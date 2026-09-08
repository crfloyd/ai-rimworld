"""Campaign records and incremental, rebuildable views."""

from contextlib import closing
import json
import math
import sqlite3
from pathlib import Path

from .core import (Error, append_json, atomic_json, atomic_text, canonical, contained,
                   identifier, journal, journal_entries, lock, now, read_json, require_fields, slug)
from .facts import Facts, initialize, entries
from .observations import bundle_children, changed, compact, evidence_index, delta_view, freshness, matches, normalize


OPEN = {"requested", "accepted", "started", "unknown", "blocked", "interrupted"}
ACTION_STATES = OPEN | {"completed", "abandoned"}
FAMILIES = {
    "treatment": "Verify the intended condition received fresh treatment; old bandages are insufficient.",
    "extinguishing": "Verify the intended pawn or cells are no longer burning, and inspect new fires.",
    "rescue": "Verify the patient reached a safe bed or designated refuge; check bleeding and route hazards.",
    "movement": "Verify pawn/map/cell and whether the route exposed the pawn to a new threat.",
    "equipment": "Verify the item is equipped or worn, rather than merely in inventory or reserved.",
    "construction": "Verify the completed building/foundation and relevant roof, access, and dependencies.",
    "combat": "Verify position, engagement, line of sight and target condition; an accepted shot is insufficient.",
    "general": "Verify the intended gameplay outcome using current evidence.",
}


def init_campaign(root, name, spec):
    slug(name)
    require_fields(spec, ("objective", "mode", "rules", "setup"))
    if spec["mode"] not in ("fresh", "resume"):
        raise Error("Campaign mode must be fresh or resume.")
    if not isinstance(spec["setup"], dict) or not isinstance(spec["rules"], (dict, list, str)):
        raise Error("setup must be an object; rules must record the user's explicit rules.")
    for key in ("ticks_per_day", "report_interval_days"):
        v = spec.get(key, 60000 if key == "ticks_per_day" else 5)
        if type(v) is not int or v <= 0:
            raise Error(f"{key} must be a positive integer.")
    base = Path(root) / "campaigns"
    path = base / name
    if base.is_symlink() or path.is_symlink():
        raise Error("Campaign directories must not be symlinks.")
    if path.exists():
        raise Error(f"Campaign already exists: {path}; resume it or choose a new identity.")
    path.mkdir(parents=True)
    meta = dict(spec, id=identifier("campaign-"), name=name, created_at=now(),
                schema_version=1, ticks_per_day=spec.get("ticks_per_day", 60000),
                report_interval_days=spec.get("report_interval_days", 5),
                session_id=None, binding=None)
    atomic_json(path / "campaign.json", meta)
    atomic_text(path / "CAMPAIGN.md", "# Campaign rules\n\n" +
                "Authoritative structured configuration: [campaign.json](campaign.json).\n\n" +
                "This bootstrap created local records only. No game has been started or loaded.\n\n" +
                json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
    for folder in ("raw", "reference", "reports", "screenshots"):
        (path / folder).mkdir()
    for name_, fallback in (
        ("STRATEGY.md", "# Strategy\n\nNo strategic commitment recorded yet.\n"),
        ("History.md", "# Colony history\n\nThe campaign has not yet been chronicled.\n"),
    ):
        template = Path(root) / "templates" / name_
        atomic_text(path / name_, template.read_text() if template.exists() else fallback)
    for name_ in ("observations.jsonl", "actions.jsonl", "events.jsonl", "issues.jsonl"):
        atomic_text(path / name_, "")
    campaign = Campaign(root, name)
    from .knowledge import adopt_shared
    if spec.get("learning", {}).get("shared_baseline", "reviewed") != "none":
        adopt_shared(campaign, "Initial snapshot of explicitly shared reviewed runner guidance", initial=True)
    campaign.refresh()
    return meta


class Campaign:
    def __init__(self, root, name):
        self.root = Path(root).resolve()
        self.path = self.root / "campaigns" / slug(name)
        if (self.root / "campaigns").is_symlink() or self.path.is_symlink():
            raise Error("Campaign directories must not be symlinks.")
        if (self.path / "campaign.json").is_symlink():
            raise Error("Campaign metadata must not be a symlink.")
        self.meta = read_json(self.path / "campaign.json")
        if self.meta.get("name") != name or not self.meta.get("id"):
            raise Error("Campaign metadata does not match directory identity.")

    def _repair(self, obs):
        if obs.get("normalizer_version") != 4:
            obs["presentation_legacy"] = True
            repaired = normalize(obs["tool"], obs["args"], obs["data"], obs["campaign_id"],
                                 obs["session_id"], obs["origin"], tick=obs.get("tick"))
            for key in ("scope", "key", "completeness", "missing", "malformed", "coverage", "data", "warnings", "normalizer_version"):
                obs[key] = repaired[key]
            obs.setdefault("source_captured_at", obs["captured_at"] if obs["origin"] == "live" else None)
        if not obs["key"].startswith(obs["origin"] + ":"):
            obs["key"] = obs["origin"] + ":" + obs["key"]
        return obs

    def _load(self, rebuild=False):
        index = self.path / "reference" / "facts.sqlite"
        index.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(index)) as db, db:
            initialize(db)
            row = db.execute('SELECT state FROM metadata WHERE id=1').fetchone()
            state = json.loads(row[0]) if row and not rebuild else {}
            reset = state.get("schema_version") != 6
            if reset:
                db.execute('DELETE FROM facts')
                state = {"schema_version": 6, "offset": 0, "epoch": 0, "latest_tick": None,
                         "tick_basis": "unknown", "last_observation": None,
                         "last_metadata": {}, "count": 0}
            offset_before = state["offset"]
            self._fold_observations(db, state)
            if reset or rebuild or state["offset"] != offset_before: db.execute('INSERT OR REPLACE INTO metadata VALUES (1, ?)', (canonical(state),))
        state["facts"] = Facts(index)
        review = self.meta.get("clock_reconciliation", {})
        if review.get("session_id") == self.meta.get("session_id") and review.get("at", "") >= state.get("clock_warning_at", "z"):
            state.pop("clock_warning", None)
            state["clock_review"] = review
        return state

    def _fold_observations(self, db, state):
        for obs, start, end in journal_entries(self.path / "observations.jsonl", state["offset"]):
            if obs["campaign_id"] != self.meta["id"]: raise Error("Observation campaign identity mismatch.")
            obs = self._repair(obs)
            clock_source = obs["origin"] == "live" or self.meta.get("session_id") is None
            if clock_source and obs["tool"] == "wait_for_event" and obs["data"].get("ticksWaited", 0) > 0:
                state["epoch"] += 1
                if obs.get("tick") is None and state["latest_tick"] is not None:
                    state["latest_tick"] += obs["data"]["ticksWaited"]
                    state["tick_basis"] = "derived from prior tick + monitored wait; revalidate after external control"
            if clock_source and type(obs.get("tick")) in (int, float):
                old = state["latest_tick"]
                if old is not None and obs["tick"] != old: state["epoch"] += 1
                if old is not None and obs["tick"] < old:
                    state["clock_warning"] = "Observed game time moved backwards. Reconcile session identity."
                    state["clock_warning_at"] = obs["captured_at"]
                state["latest_tick"] = obs["tick"]
                state["tick_basis"] = obs.get("tick_basis", "unknown")
            obs["epoch"] = state["epoch"]
            atomic_json(self.path / "reference" / "observation-index" / (obs["id"] + ".json"),
                        {"offset": start, "end": end, "epoch": obs["epoch"], "campaign_id": self.meta["id"]})
            row = db.execute('SELECT entry FROM facts WHERE key=?', (obs["key"],)).fetchone()
            prior = json.loads(row[0]) if row else {}
            # No duplicated full current value. Retain the previous complete record only on a failed read.
            entry = {"latest": obs, "last_known": None}
            if obs["completeness"] != "known":
                entry["last_known"] = (prior.get("latest") if prior.get("latest", {}).get("completeness") == "known"
                                       else prior.get("last_known"))
            from .safety import signals
            db.execute('INSERT OR REPLACE INTO facts VALUES (?, ?, ?, ?)',
                       (obs["key"], obs["tool"], bool(signals(obs)), canonical(entry)))
            state["last_observation"] = obs["id"]
            state["last_metadata"] = {k: obs[k] for k in ("captured_at", "origin", "session_id", "tick")}
            state["count"] += 1
            state["offset"] = end

    def _save_projection(self, state):
        # Small diagnostic checkpoint. Indexed facts commit with their replay offset
        # in one SQLite transaction; this export is not a second authority.
        value = {k: v for k, v in state.items() if k != "facts"}
        value["facts_index"] = "reference/facts.sqlite"
        value["scope_count"] = len(state["facts"])
        atomic_json(self.path / ".projection.json", value)

    def _actions(self, open_only=False, rebuild=False):
        if not open_only:
            records, _ = journal(self.path / "actions.jsonl")
            return {r["id"]: r for r in records}
        with lock(self.path / ".memory.lock"):
            path = self.path / "reference" / ".active-actions.json"
            cache = read_json(path) if path.exists() and not rebuild else {"offset": 0, "open": {}}
            changed = False
            for r, start, end in journal_entries(self.path / "actions.jsonl", cache["offset"]):
                if r["status"] in OPEN: cache["open"][r["id"]] = r
                else: cache["open"].pop(r["id"], None)
                atomic_json(self.path / "reference" / "action-index" / (r["id"] + ".json"), r)
                cache["offset"] = end; changed = True
            if changed or rebuild or not path.exists(): atomic_json(path, cache)
            return cache["open"]

    def action_record(self, action_id):
        slug(action_id)
        self._actions(open_only=True)
        path = self.path / "reference" / "action-index" / (action_id + ".json")
        if not path.exists(): self._actions(open_only=True, rebuild=True)
        return read_json(path) if path.exists() else None

    def _issues(self):
        with lock(self.path / ".memory.lock"):
            path = self.path / "reference" / ".issues.json"
            cache = read_json(path) if path.exists() else {"offset": 0, "issues": {}}
            changed = False
            for r, start, end in journal_entries(self.path / "issues.jsonl", cache["offset"]):
                cache["issues"][r["id"]] = r; cache["offset"] = end; changed = True
            if changed or not path.exists(): atomic_json(path, cache)
            return cache["issues"]

    def event_view(self):
        with lock(self.path / ".memory.lock"):
            path = self.path / "reference" / ".events.json"
            cache = read_json(path) if path.exists() else {"offset": 0, "retired": [], "checkpoints": [], "acknowledgements": {}}
            changed = False
            for e, start, end in journal_entries(self.path / "events.jsonl", cache["offset"]):
                kind = e.get("kind")
                if kind == "retire_fact" and e["observation"] not in cache["retired"]: cache["retired"].append(e["observation"])
                if kind == "checkpoint" and e["day"] not in cache["checkpoints"]: cache["checkpoints"].append(e["day"])
                if kind == "risk_acknowledgement":
                    for risk in e["risk_ids"]: cache["acknowledgements"][risk] = e
                cache["offset"] = end; changed = True
            if changed or not path.exists(): atomic_json(path, cache)
            return cache

    def issue_reviews(self, state=None):
        state = state or self.state()
        reviews = []
        for issue in self._issues().values():
            if issue["status"] != "open":
                continue
            ticks = [issue["revisit_tick"]] if issue.get("revisit_tick") is not None else []
            if issue.get("deadline", {}).get("kind") == "review": ticks.append(issue["deadline"]["tick"])
            tick = min(ticks, default=None)
            due = None if tick is None or state["latest_tick"] is None else state["latest_tick"] >= tick
            reviews.append(dict(issue, revisit_due=due, review_clock_unknown=tick is not None and state["latest_tick"] is None,
                                recurring=issue.get("occurrences", 1) >= issue.get("review_after_occurrences", 2)))
        return reviews

    def _retired(self):
        return set(self.event_view()["retired"])

    def retire(self, observation_id, evidence, reason):
        previous = self.observation(observation_id)
        current = self.observation(evidence)
        if current["completeness"] != "known" or current["captured_at"] <= previous["captured_at"] or current["origin"] != previous["origin"] or current["session_id"] != previous["session_id"]:
            raise Error("Retirement needs newer complete evidence from the same origin/session.")
        if current["tool"] != previous["tool"] or current["scope"] != previous["scope"]:
            raise Error("Retirement needs matching semantic scope; an unrelated status cannot erase a known risk.")
        if not reason:
            raise Error("Explain why this observation no longer needs working context.")
        event = self.event({"kind": "retire_fact", "summary": reason,
                            "observation": observation_id, "evidence": evidence})
        self.refresh()
        return event

    def state(self):
        with lock(self.path / ".memory.lock"):
            return self._load()

    def ingest(self, tool, args, payload, origin="recorded", tick=None,
               seconds=None, request_id=None, session_id=None, source_captured_at=None):
        if origin not in ("live", "recorded", "fixture", "external"):
            raise Error("Unknown observation origin.")
        session = session_id or self.meta.get("session_id") or "unbound"
        main = normalize(tool, args, payload, self.meta["id"], session, origin,
                         tick=tick, seconds=seconds, request_id=request_id, source_captured_at=source_captured_at)
        children = bundle_children(main)
        for obs in (main, *children):
            obs["key"] = obs["origin"] + ":" + obs["key"]
        with lock(self.path / ".memory.lock"):
            state = self._load()
            before = {obs["key"]: state["facts"].get(obs["key"], {}).get("latest") for obs in (main, *children)}
            # A monitor/handoff may have inspected facts without showing them to
            # the agent. Do not emit deltas against that unseen baseline.
            reset_at = self.meta.get("presentation_reset_at")
            if reset_at:
                before = {key: (None if obs and obs["captured_at"] <= reset_at else obs)
                          for key, obs in before.items()}
            raw = "raw/" + main["id"] + ".json"
            atomic_json(self.path / raw, {"tool": tool, "args": args, "payload": payload,
                                         "metadata": main})
            for obs in (main, *children):
                obs["raw"] = raw
                append_json(self.path / "observations.jsonl", obs)
            state = self._load()
            self._verify_actions(state, (main, *children))
            self._write_views(state)
        before = {key: None if old and old.get("presentation_legacy") else old for key,old in before.items()}
        result = delta_view(before[main["key"]], main)
        if children:
            result["bundle"] = [delta_view(before[child["key"]], child) for child in children]
        return result

    def _observation(self, obs_id):
        if not isinstance(obs_id, str) or not obs_id.startswith("obs-"): raise Error("Invalid observation ID.")
        slug(obs_id)
        index_path = self.path / "reference" / "observation-index" / (obs_id + ".json")
        if not index_path.exists():
            self._load()  # Incrementally rebuild a legacy/missing derived index; never rewrite authority.
        if not index_path.exists(): raise Error("Unknown observation or missing derived index: " + obs_id + "; use rebuild to reconstruct indexes from the original journal.")
        index = read_json(index_path)
        with (self.path / "observations.jsonl").open("rb") as stream:
            stream.seek(index["offset"])
            raw = stream.read(index["end"] - index["offset"])
        try: obs = json.loads(raw)
        except ValueError as exc: raise Error("Observation index points to corrupt evidence.") from exc
        if obs.get("id") != obs_id or obs.get("campaign_id") != self.meta["id"]:
            raise Error("Observation index identity mismatch; reconcile the derived index.")
        obs = self._repair(obs)
        obs["epoch"] = index["epoch"]
        return obs

    def observation(self, obs_id):
        with lock(self.path / ".memory.lock"):
            return self._observation(obs_id)

    def has_observation(self, obs_id):
        try: self.observation(obs_id); return True
        except Error: return False

    def event(self, value):
        require_fields(value, ("kind", "summary"))
        event = dict(value, id=identifier("event-"), captured_at=now(),
                     campaign_id=self.meta["id"])
        with lock(self.path / ".memory.lock"):
            append_json(self.path / "events.jsonl", event)
        return event

    def issue(self, value, issue_id=None):
        with lock(self.path / ".memory.lock"):
            issues = self._issues()
            if issue_id and issue_id not in issues:
                raise Error("Unknown issue.")
            issue = dict(issues.get(issue_id, {}), **value)
            require_fields(issue, ("title", "rationale", "next_action", "revisit", "resolution"))
            status = issue.get("status", "open")
            if status not in ("open", "resolved", "accepted", "superseded"):
                raise Error("Unknown issue status.")
            if status != "open":
                require_fields(issue, ("evidence", "review"))
            if issue.get("deadline"):
                deadline = issue["deadline"]
                require_fields(deadline, ("kind", "tick", "reason"))
                if deadline["kind"] not in ("hard", "review") or type(deadline["tick"]) not in (int, float) or not math.isfinite(deadline["tick"]) or deadline["tick"] < 0:
                    raise Error("Deadline needs kind=hard/review, a finite nonnegative tick, and rationale.")
            if issue.get("temporary_override") and not issue.get("restore_when"):
                raise Error("Temporary overrides need a restore_when condition.")
            for field in ("occurrences", "review_after_occurrences"):
                if field in issue and (type(issue[field]) is not int or issue[field] < 1):
                    raise Error(f"{field} must be a positive integer.")
            if issue.get("revisit_tick") is not None and (
                type(issue["revisit_tick"]) not in (int, float) or not math.isfinite(issue["revisit_tick"]) or issue["revisit_tick"] < 0):
                raise Error("revisit_tick must be a nonnegative number or null.")
            if issue.get("incident_ids"):
                events = {e["id"]: e for e in journal(self.path / "events.jsonl")[0]}
                if any(events.get(i, {}).get("kind") != "incident" for i in issue["incident_ids"]):
                    raise Error("Recurrence must cite incident events from this run.")
                issue["incident_ids"] = list(dict.fromkeys(issue["incident_ids"]))
                issue["occurrences"] = len({(events[i].get("key"), events[i].get("episode")) for i in issue["incident_ids"]})
                issue["recurrence_basis"] = "distinct evidence-linked incident episodes"
            elif issue.get("occurrences", 1) > 1:
                issue["recurrence_basis"] = "legacy/manual count; investigate and link incident evidence"
            issue.update(id=issue_id or identifier("issue-"), status=status, updated_at=now())
            append_json(self.path / "issues.jsonl", issue)
            self._write_views(self._load())
            return issue

    def action(self, tool, args, intent, family="general", check=None, origin="live"):
        if origin not in ("live", "fixture"):
            raise Error("Actions must be live or explicitly synthetic fixture actions.")
        slug(family)  # Free-form label; templates are conveniences, not strategic limits.
        if not intent:
            raise Error("Record the intended outcome.")
        if check:
            from .outcomes import validate_check
            validate_check(check)
        record = {"id": identifier("action-"), "tool": tool, "args": args, "intent": intent,
                  "family": family, "verification_guidance": FAMILIES.get(family, FAMILIES["general"]),
                  "check": check, "status": "requested", "requested_at": now(),
                  "session_id": self.meta.get("session_id") or "unbound", "origin": origin,
                  "binding_expected": (self.meta.get("binding") or {}).get("expected"),
                  "reconciled_sessions": []}
        with lock(self.path / ".memory.lock"):
            append_json(self.path / "actions.jsonl", record)
            self._write_views(self._load())
        return record

    def action_update(self, action_id, status, evidence=None, reason=None, internal=False):
        if status not in ACTION_STATES:
            raise Error("Unknown action state.")
        with lock(self.path / ".memory.lock"):
            actions = self._actions(open_only=True)
            if action_id not in actions:
                raise Error("Unknown action.")
            record = actions[action_id]
            if record["status"] in ("completed", "abandoned"):
                raise Error("Closed action is immutable; record a new action or issue.")
            if status in ("completed", "started") or (not internal and status != "requested"):
                if not evidence or not reason:
                    raise Error("State changes need evidence and a reason.")
                self._check_evidence(evidence, record, outcome=status == "completed")
            record = dict(record, status=status, updated_at=now(), evidence=evidence, reason=reason)
            if status == "accepted":
                record["accepted_at"] = record["updated_at"]
            append_json(self.path / "actions.jsonl", record)
            self._write_views(self._load())
            return record

    def _check_evidence(self, evidence, action, outcome=False):
        state = self._load()
        if evidence.startswith("obs-"):
            obs = self._observation(evidence)
            self._eligible_evidence(obs, action, state)
            if outcome:
                if action["tool"] == "wait_for_event" and obs["tool"] == "wait_for_event" and obs["args"] == action["args"]:
                    return
                from .outcomes import satisfied
                supported = satisfied(self, action, state) if action.get("check") else None
                if not supported or evidence not in supported:
                    raise Error("Completion needs matching outcome predicates or an explicit scoped visual verification event.")
            else:
                actor = action.get("args", {}).get("id")
                if actor and actor not in (obs["args"].get("id"), obs["data"].get("id")):
                    raise Error("Outcome evidence does not identify the action's pawn/target.")
            return
        events, _ = journal(self.path / "events.jsonl")
        event = next((e for e in events if e["id"] == evidence), None)
        if not event or event.get("kind") != "verification":
            raise Error("Use an observation ID or an explicit visual verification event.")
        require_fields(event, ("source", "action_id", "observed_outcome", "origin", "session_id"))
        if event["action_id"] != action["id"] or event["origin"] != action.get("origin", "live"):
            raise Error("Verification event must identify this action and its origin.")
        if event["captured_at"] < action["requested_at"] or event["session_id"] != self.meta.get("session_id"):
            raise Error("Verification event must be current and later than the action.")
        if event["session_id"] not in [action["session_id"], *action.get("reconciled_sessions", [])]:
            raise Error("Reconcile the action's session before verifying it.")

    def _eligible_evidence(self, obs, action, state):
        if obs.get("origin") != action.get("origin", "live"):
            raise Error("Non-live/imported evidence cannot verify a live action.")
        threshold = action["requested_at"] if action["tool"] == "wait_for_event" else action.get("accepted_at", action["requested_at"])
        if not obs.get("source_captured_at") or obs["source_captured_at"] < threshold:
            raise Error("Evidence source time is unknown or predates the action.")
        if obs["session_id"] not in [action["session_id"], *action.get("reconciled_sessions", [])]:
            raise Error("Evidence belongs to a different session; reconcile it first.")
        if freshness(obs, state, self.meta, live=action.get("origin", "live") == "live")["revalidate"]:
            raise Error("Outcome evidence is incomplete or stale.")

    def reconcile_clock(self, evidence, review):
        if not review or (self.meta.get("binding") or {}).get("evidence") != evidence:
            raise Error("Review a fresh bound live status and explain legitimate game/session continuity; this never authorizes a reload.")
        obs = self.observation(evidence)
        state = self.state()
        reasons = freshness(obs, state, self.meta)["reasons"]
        if any(reason != "game clock requires reconciliation" for reason in reasons):
            raise Error("Clock reconciliation evidence must otherwise be fresh, complete and live.")
        record = {"at": now(), "evidence": evidence, "review": review, "session_id": self.meta["session_id"], "tick": obs["tick"]}
        with lock(self.path / ".memory.lock"):
            self.meta["clock_reconciliation"] = record
            atomic_json(self.path / "campaign.json", self.meta)
            self.event({"kind": "clock_reconciliation", "summary": review, "evidence": evidence, "tick": obs["tick"]})
            self._write_views(self._load())
        return record

    def reconcile_actions(self, action_ids, evidence, review):
        if not action_ids or not review:
            raise Error("Select outstanding actions and explain verified same-game continuity.")
        binding = self.meta.get("binding") or {}
        if binding.get("evidence") != evidence:
            raise Error("Use the fresh live status used for the current identity binding.")
        obs = self.observation(evidence)
        if freshness(obs, self.state(), self.meta)["revalidate"]:
            raise Error("Same-game reconciliation requires fresh live evidence.")
        with lock(self.path / ".memory.lock"):
            actions = self._actions(open_only=True)
            selected = [actions[i] for i in action_ids if i in actions]
            if len(selected) != len(action_ids): raise Error("Unknown action in reconciliation.")
            for action in selected:
                if action["status"] not in OPEN or not action.get("binding_expected") or action["binding_expected"] != binding["expected"]:
                    raise Error("An open action must have the same explicitly reviewed game binding.")
            result = []
            for action in selected:
                sessions = list(dict.fromkeys([*action.get("reconciled_sessions", []), self.meta["session_id"]]))
                updated = dict(action, reconciled_sessions=sessions, reconciliation={
                    "evidence": evidence, "review": review, "at": now()}, updated_at=now())
                append_json(self.path / "actions.jsonl", updated)
                result.append(updated)
            self._write_views(self._load())
        return {"actions": result, "replayed": False, "outcome": "Still unverified; inspect current gameplay outcomes."}

    def _verify_actions(self, state, observations):
        from .outcomes import satisfied
        for action in self._actions(open_only=True).values():
            if action["status"] not in ("accepted", "started") or not action.get("check"): continue
            supported = satisfied(self, action, state)
            if supported:
                updated = dict(action, status="completed", updated_at=now(), evidence=supported[0],
                               evidence_set=supported, reason="Fresh evidence satisfies every outcome requirement.")
                append_json(self.path / "actions.jsonl", updated)

    def rebuild(self):
        with lock(self.path / ".memory.lock"):
            state = self._load(rebuild=True)
            self._actions(open_only=True, rebuild=True)
            self._write_views(state)
        return {"rebuilt": True, "observations": state["count"], "original_journals_changed": False}

    def refresh(self):
        with lock(self.path / ".memory.lock"):
            state = self._load()
            self._write_views(state)
            return (self.path / "STATE.md").read_text()

    def _write_views(self, state):
        self._save_projection(state)
        open_issues = self.issue_reviews(state)
        atomic_text(self.path / "ISSUES.md", "# Unresolved issues\n\n" +
                    "\n\n".join(json.dumps(i, ensure_ascii=False, indent=2) for i in open_issues) +
                    ("\nNo open issues recorded. This is not evidence of absence of problems.\n"
                     if not open_issues else "\n"))
        actions = list(self._actions(open_only=True).values())
        last = state.get("last_metadata", {})
        atomic_json(self.path / "summary.json", {
            "schema_version": 1, "campaign_id": self.meta["id"], "generated_at": now(),
            "latest_tick": state["latest_tick"], "tick_basis": state.get("tick_basis", "unknown"),
            "last_observation_at": last.get("captured_at"), "observation_origin": last.get("origin"),
            "open_issues": len(open_issues), "pending_actions": len(actions),
        })
        lines = ["# Current evidence", "", f"Campaign: {self.meta['name']} ({self.meta['id']}).",
                 f"Generated: {now()}. Tick: {state['latest_tick']} ({state.get('tick_basis', 'unknown')}).",
                 f"Session: {self.meta.get('session_id') or 'unbound; live identity not verified'}.",
                 "Recorded observations are not a live connection. Revalidate before game control.", ""]
        if state.get("clock_warning"):
            lines += ["CLOCK WARNING: " + state["clock_warning"], ""]
        retired = self._retired()
        for entry in entries(state, tools=("get_status", "get_alerts", "get_resources", "list_colonists", "get_research", "get_conditions", "wait_for_event", "list_fires", "get_pawn"), risks=True):
            obs = entry["latest"]
            if obs["id"] in retired:
                continue
            # A failed read still carries the previous known fact, explicitly stale.
            if obs["completeness"] != "known":
                lines += [canonical(evidence_index(obs))]
                if entry.get("last_known"):
                    old = entry["last_known"]
                    lines += ["Last known, requiring revalidation: " +
                              canonical({"observation": old["id"], "captured_at": old["captured_at"],
                                         "tick": old["tick"], "detail": old["raw"], "retrieve_required": True})]
                continue
            if obs["tool"] not in ("get_status", "get_alerts", "get_resources", "list_colonists",
                                   "get_research", "get_conditions", "wait_for_event", "list_fires",
                                   "get_pawn"):
                continue
            if obs["tool"] == "get_pawn" and obs["args"].get("tab") not in ("health", "needs", None):
                continue
            stale = freshness(obs, state, self.meta)["revalidate"]
            label = "REVALIDATE" if stale else "OBSERVED"
            c = evidence_index(obs)
            lines += [label + " " + canonical(c), ""]
        if not state["facts"]:
            lines += ["No observations yet. Game identity, threats and all colony facts are unknown.", ""]
        lines += ["## Unfinished actions", ""]
        lines += [canonical(a) for a in actions] or ["None recorded; verify existing in-game orders."]
        lines += ["", "## Open issues and temporary overrides", ""]
        lines += [canonical(i) for i in open_issues] or ["None recorded."]
        lines += ["", "## Strategy and deeper evidence", "",
                  "Read STRATEGY.md for decisions and rationale; ISSUES.md for unresolved problems.",
                  "Use context/retrieve for relevant reference details. Full evidence is in raw/.",
                  "Checkpoint status: " + canonical(self.checkpoints(state)), ""]
        atomic_text(self.path / "STATE.md", "\n".join(lines))

    def checkpoints(self, state=None):
        state = state or self.state()
        checkpoints = sorted(self.event_view()["checkpoints"])
        interval = self.meta["report_interval_days"]
        next_day = interval
        while next_day in checkpoints:
            next_day += interval
        tick = state["latest_tick"]
        day = tick / self.meta["ticks_per_day"] if tick is not None else None
        return {"next_day": next_day, "observed_or_derived_day": day,
                "due": None if day is None else day >= next_day,
                "time_basis": state.get("tick_basis", "unknown")}

    def retrieve(self, tool=None, entity=None):
        result = []
        for entry in entries(self.state(), tools=(tool,) if tool else None):
            obs = entry["latest"]
            if tool and obs["tool"] != tool:
                continue
            if entity and entity not in (obs["args"].get("id"), obs["args"].get("name")):
                continue
            result.append(obs)
        return result
