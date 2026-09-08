"""One serialized controller, durable uncertain-operation records, explicit handoff."""

import os
import math
import time
from pathlib import Path

from .core import (Error, alive, append_json, atomic_json, digest, identifier, lock,
                   now, read_json, require_fields, canonical)
from .mcp import Client, Uncertain, endpoint_key, validate
from .observations import decode, path_value, MISSING, freshness, pause_confirmed, same_value
from .safety import assess, deadlines


DENY = {"load_game", "delete_save", "debug", "dev_mode", "set_difficulty",
        "spawn_item", "spawn_pawn", "trigger_incident", "edit_pawn"}


def effect(tool, args):
    if tool in DENY or tool.lower().startswith(("debug_", "dev_", "spawn_")):
        return "denied"
    if tool == "get_status" and args:
        return "mutation"  # Bundle configuration is saved gameplay/tool configuration.
    if tool == "set_speed":
        return "mutation" if args == {"action": "pause"} else "denied"
    if tool == "wait_for_event":
        return "advance"
    if tool == "order_pawn" and not any(k in args for k in ("command", "index")):
        return "inspection-ui"
    if tool == "set_schedule" and "assignment" not in args:
        return "inspection-ui"
    if tool == "manage_area" and args.get("op") == "list": return "inspection-ui"
    from .capabilities import default_effects
    return default_effects().get(tool, "unclassified")


def receipt_status(tool, args, data, completeness):
    """Accept only recognized receipts; acceptance never proves task completion."""
    if data.get("ok") is False or data.get("error"): return "blocked"
    if completeness != "known": return "unknown"
    if data.get("ok") is True: return "accepted"
    if tool == "draft" and data.get("action") == args.get("action"):
        field = "drafted" if args.get("action") == "draft" else "undrafted"
        if all(isinstance(data.get(k), list) for k in (field, "alreadyInState", "skipped")):
            if data["skipped"]: return "blocked"
            if data[field] or data["alreadyInState"]: return "accepted"
    # These normal zone setters return a zone record, not an `ok` envelope.
    # Recognize the receipt; this does not prove a broader hauling objective.
    if 'id' in args and same_value(data.get('id'), args['id']):
        if tool == 'rename_zone' and isinstance(args.get('name'),str) and data.get('label') == args['name']:
            return 'accepted'
        if tool == 'set_stockpile_priority' and data.get('kind') == 'stockpile' and data.get('priority') == args.get('priority') and isinstance(args.get('priority'),str):
            return 'accepted'
        if tool == 'set_stockpile_filter' and data.get('kind') == 'stockpile' and isinstance(data.get('filter'),dict):
            applied = data.get('applied')
            if isinstance(applied,list) and all(isinstance(v,str) for v in applied):
                if any(v.startswith('unknown:') for v in applied): return 'blocked'
                expected = sum(args.get(k) is True for k in ('allowAll','disallowAll'))
                expected += sum(len([v for v in args.get(k,'').split(',') if v.strip()]) for k in ('allow','disallow'))
                expected += int(any(k in args for k in ('hpMin','hpMax')))
                expected += int(any(k in args for k in ('qualityMin','qualityMax')))
                recognized = all(v in ('allowAll','disallowAll','hpRange','qualityRange') or
                                 (v.startswith(('+','-')) and len(v)>1) for v in applied)
                if expected and len(applied) == expected and recognized: return 'accepted'
    return "unknown"


class Control:
    def __init__(self, campaign, endpoint=None, client_factory=Client):
        self.campaign = campaign
        self.endpoint = endpoint or campaign.meta.get("endpoint", "http://localhost:8787/mcp")
        self.key = digest(endpoint_key(self.endpoint))
        self.path = campaign.root / ".runtime" / self.key
        self.path.mkdir(parents=True, exist_ok=True)
        self.client_factory = client_factory

    def claim(self, owner, available, basis):
        if not available or not owner or not basis:
            raise Error("Claim requires --control-available, an owner, and a handoff basis.")
        with lock(self.path / "operation.lock"):
            if (self.path / "owner.json").exists():
                raise Error("An owner already exists. Inspect and complete its handoff; no timeout takeover.")
            if (self.path / "pending.json").exists():
                raise Error("An unresolved operation remains. Reconcile it before claiming.")
            record = {"owner": owner, "campaign_id": self.campaign.meta["id"],
                      "token": identifier("owner-"), "claimed_at": now(), "basis": basis,
                      "endpoint": self.endpoint,
                      "limitation": "Excludes cooperating clients only; external RimMolt clients must be handed off."}
            atomic_json(self.path / "owner.json", record)
            return record

    def inspect(self):
        result = {"endpoint": self.endpoint}
        for filename in ("owner", "pending", "session", "pause-uncertain", "monitor"):
            p = self.path / (filename + ".json")
            if p.exists():
                result[filename] = read_json(p)
        if "pending" in result:
            result["pending"]["local_process_alive"] = alive(result["pending"].get("pid"))
            handle = self.path / (result["pending"]["request_id"] + ".handle.json")
            if handle.exists():
                result["pending"]["orchestrator_handle"] = read_json(handle)
            result["pending"]["warning"] = "Local process exit does not prove the server operation ended."
        if "monitor" in result:
            handle = self.path / (result["monitor"]["id"] + ".handle.json")
            if handle.exists(): result["monitor"]["orchestrator_handle"] = read_json(handle)
        return result

    def _owner(self, token):
        record = read_json(self.path / "owner.json")
        if record["token"] != token or record["campaign_id"] != self.campaign.meta["id"]:
            raise Error("Controller token/campaign mismatch.")
        return record

    def release(self, token, basis):
        with lock(self.path / "operation.lock"):
            self._owner(token)
            self._no_pending()
            if (self.path / "pending.json").exists():
                raise Error("Reconcile the pending operation before releasing control.")
            if not basis:
                raise Error("Record the verified game pause/hand-off state.")
            append_json(self.path / "history.jsonl", {"kind": "release", "at": now(), "basis": basis})
            (self.path / "owner.json").unlink()
            return {"released": True, "game_changed": False}

    def attach_handle(self, request_id, kind, value):
        monitor_path = self.path / "monitor.json"
        if monitor_path.exists() and read_json(monitor_path).get("id") == request_id:
            atomic_json(self.path / (request_id + ".handle.json"),
                        {"kind": kind, "value": value, "captured_at": now(), "scope": "finite monitor process"})
            return
        pending = read_json(self.path / "pending.json")
        if pending["request_id"] != request_id:
            raise Error("Handle does not match the pending request.")
        atomic_json(self.path / (request_id + ".handle.json"),
                    {"kind": kind, "value": value, "captured_at": now()})

    def reconcile(self, token, evidence, reason, server_terminal):
        with lock(self.path / "operation.lock"):
            self._owner(token)
            pending = read_json(self.path / "pending.json")
            if not evidence or not reason or not server_terminal:
                raise Error("Require evidence, reason, and explicit confirmation that the server operation ended.")
            if alive(pending.get("pid")) is True and pending.get("pid") != os.getpid():
                raise Error("Originating process is still live; poll its handle before reconciliation.")
            append_json(self.path / "history.jsonl", {"kind": "reconciled", "pending": pending,
                        "evidence": evidence, "reason": reason, "at": now(),
                        "basis": "operator-reviewed terminal server/process evidence"})
            # A terminated worker may have persisted a response without delivering it.
            self.campaign.meta['presentation_reset_at'] = now()
            atomic_json(self.campaign.path / 'campaign.json', self.campaign.meta)
            (self.path / "pending.json").unlink()
            return {"reconciled": True, "replayed": False,
                    "action_status": "Reconcile the gameplay outcome separately; this does not mark it successful."}

    def connect(self, token):
        with lock(self.path / "operation.lock"):
            self._owner(token)
            self._no_pending()
            client = self.client_factory(self.endpoint)
            initialized = client.initialize()
            tools = client.catalog()
            atomic_json(self.path / "session.json", client.session)
            catalog = {"captured_at": now(), "server": initialized, "tools": tools,
                       "schema_digest": digest(tools), "endpoint": self.endpoint}
            atomic_json(self.campaign.path / "raw" / "catalog.json", catalog)
            stale = self.path / "catalog-stale.json"
            if stale.exists():
                stale.unlink()
            # A reconnect invalidates the prior identity attestation.
            self.campaign.meta.update(session_id=identifier("session-"), binding=None,
                                      presentation_reset_at=now(),
                                      endpoint=self.endpoint, catalog_digest=catalog["schema_digest"])
            atomic_json(self.campaign.path / "campaign.json", self.campaign.meta)
            return {"connected": True, "tools": len(tools), "catalog": "raw/catalog.json",
                    "session_id": self.campaign.meta["session_id"],
                    "next": "Observe get_status, review the running game, then bind its identity."}

    def _no_pending(self):
        monitor_path = self.path / "monitor.json"
        if monitor_path.exists():
            monitor = read_json(monitor_path)
            if monitor.get("status") == "running" and monitor.get("pid") != os.getpid():
                raise Error("A finite monitor owns control; inspect its recorded process/handle. Do not interleave another controller.")
        if (self.path / "pending.json").exists():
            raise Error("An operation is pending or uncertain. Inspect/poll/reconcile; do not replay it.")

    def bind(self, observation_id, expected, basis, token):
        with lock(self.path / "operation.lock"):
            return self._bind(observation_id, expected, basis, token)

    def _bind(self, observation_id, expected, basis, token):
        self._owner(token)
        self._no_pending()
        require_fields(expected, ("loaded",))
        obs = self.campaign.observation(observation_id)
        if obs["tool"] != "get_status" or obs["origin"] != "live" or obs["completeness"] != "known":
            raise Error("Bind only from a complete live get_status observation.")
        if obs["session_id"] != self.campaign.meta["session_id"]:
            raise Error("Identity observation is from another session.")
        if any(reason != "game clock requires reconciliation" for reason in freshness(obs, self.campaign.state(), self.campaign.meta)["reasons"]):
            raise Error("Identity must be bound from the current complete live status, not an older observation.")
        for path, value in expected.items():
            if path_value(obs["data"], path) != value:
                raise Error("Running game does not match the supplied identity.")
        if expected["loaded"] is True and not any(k != "loaded" for k in expected):
            raise Error("Loaded colonies require identifying fields as well as loaded=true.")
        if not basis:
            raise Error("Record how you verified this is the authorized game, beyond potentially reused names.")
        self.campaign.meta["binding"] = {"expected": expected, "evidence": observation_id,
                                         "basis": basis, "at": now()}
        atomic_json(self.campaign.path / "campaign.json", self.campaign.meta)
        return self.campaign.meta["binding"]

    def classify(self, token, tool, classification, basis):
        if classification not in ("inspection-pausing", "inspection-ui", "mutation", "advance"):
            raise Error("Invalid classification.")
        with lock(self.path / "operation.lock"):
            self._owner(token)
            self._no_pending()
            catalog = read_json(self.campaign.path / "raw" / "catalog.json")
            if (self.path / "catalog-stale.json").exists():
                raise Error("Server announced a changed catalog. Reconnect and rebind before further calls.")
            if tool not in catalog["tools"] or effect(tool, {}) == "denied":
                raise Error("Unknown or prohibited tool.")
            if not basis:
                raise Error("Record the reviewed schema/description and legitimate gameplay purpose.")
            p = self.path / "classifications.json"
            rules = read_json(p) if p.exists() else {}
            rules[tool] = {"effect": classification, "basis": basis,
                           "schema_digest": digest(catalog["tools"][tool]), "at": now()}
            atomic_json(p, rules)
            return rules[tool]

    def call(self, token, tool, args, intent=None, family="general", check=None, setup=False, track=True):
        with lock(self.path / "operation.lock"):
            self._owner(token)
            self._no_pending()
            lease_path = self.path / "monitor.json"
            if lease_path.exists():
                lease = read_json(lease_path)
                if lease.get("status") == "running" and lease.get("pid") != os.getpid():
                    raise Error("A finite monitor owns gameplay calls; inspect its handle instead of interleaving.")
                if lease.get("status") == "running" and time.time() >= lease.get("expires_at", 0) and tool != "set_speed":
                    raise Error("Monitor lease expired; pause and return for review.")
            if (self.path / "pause-uncertain.json").exists() and tool != "set_speed":
                raise Error("Pause is unconfirmed; use the pause safeguard before further gameplay calls.")
            if (self.path / "catalog-stale.json").exists():
                raise Error("Server announced a changed catalog. Reconnect and rebind before further calls.")
            catalog = read_json(self.campaign.path / "raw" / "catalog.json")
            if tool not in catalog["tools"]:
                raise Error(f"Tool {tool!r} is absent from the captured catalog. Use local capabilities search or capabilities --tool NAME to check the exact name and schema first; this error alone does not establish a stale connection.")
            validate(catalog["tools"][tool]["inputSchema"], args)
            kind = effect(tool, args)
            custom = self.path / "classifications.json"
            if kind == "unclassified" and custom.exists():
                rule = read_json(custom).get(tool)
                if rule and rule["schema_digest"] == digest(catalog["tools"][tool]):
                    kind = rule["effect"]
            if kind in ("denied", "unclassified"):
                raise Error(f"Tool is {kind}; inspect its live contract and use legitimate controls.")
            binding = self.campaign.meta.get("binding")
            if not binding and tool != "get_status":
                raise Error("Inspect and bind the live game identity before controlling it.")
            if binding and binding["expected"].get("loaded") is False and kind in ("mutation", "advance") and not setup:
                raise Error("Main-menu binding requires an explicit setup action; rebind after the colony loads.")
            if type(track) is not bool: raise Error("track must be boolean.")
            mutation = kind in ("mutation", "advance")
            if mutation and not intent:
                raise Error("Gameplay changes need an intended outcome.")
            if mutation and tool != "set_speed":
                # Dispatch itself can invalidate facts, even if the server response is later lost.
                self.campaign.meta["mutable_facts_invalidated_at"] = now()
                atomic_json(self.campaign.path / "campaign.json", self.campaign.meta)
            # Durable request records cover every call; long-lived action records are for important outcomes.
            tracked = mutation and (track or check is not None or kind == "advance")
            action = self.campaign.action(tool, args, intent, family, check) if tracked else None
            request_id = identifier("rpc-")
            pending = {"request_id": request_id, "pid": os.getpid(), "tool": tool,
                       "args": args, "kind": kind, "action_id": action["id"] if action else None,
                       "started_at": now(), "status": "inflight",
                       "session_id": self.campaign.meta["session_id"], "track_intention": track}
            atomic_json(self.path / "pending.json", pending)
            client = self.client_factory(self.endpoint, read_json(self.path / "session.json"))
            started = time.monotonic()
            last_timing_path = self.campaign.path / "reference" / ".last-control-timing.json"
            previous_timing = read_json(last_timing_path) if last_timing_path.exists() else {}
            wall_started = time.time()
            try:
                payload = client.rpc("tools/call", {"name": tool, "arguments": args}, request_id)
                if getattr(client, "notifications", None):
                    payload["_transportNotifications"] = client.notifications
                    if any(n.get("method") == "notifications/tools/list_changed" for n in client.notifications):
                        atomic_json(self.path / "catalog-stale.json",
                                    {"at": now(), "request_id": request_id})
                elapsed = time.monotonic() - started
                persistence_started = time.monotonic()
                result = self.campaign.ingest(tool, args, payload, origin="live",
                                             seconds=elapsed, request_id=request_id)
                data, _ = decode(payload)
                observations = [self.campaign.observation(result["id"])] + [self.campaign.observation(c["id"]) for c in result.get("bundle", [])]
                assessment = assess(self.campaign, observations, permit_acknowledged=True)
                result["safety"] = {"stop": assessment["stop"],
                    "blocker_ids": list(dict.fromkeys(r["id"] for r in assessment["blockers"])),
                    "acknowledged_ids": list(dict.fromkeys(r["id"] for r in assessment["risks"] if r["acknowledged"]))}
                # Risk details already appear once in each observation's view.
                # Assessment remains full internally; do not serialize it twice more.
                if tool == "get_status" and binding:
                    mismatch = [p for p, v in binding["expected"].items() if path_value(data, p) != v]
                    if mismatch:
                        self.campaign.meta["binding"] = None
                        atomic_json(self.campaign.path / "campaign.json", self.campaign.meta)
                        result["identity_mismatch"] = mismatch
                if action:
                    status = receipt_status(tool, args, data, result["completeness"])
                    self.campaign.action_update(action["id"], status, result["id"],
                                                "Tool response; gameplay outcome still requires verification.",
                                                internal=True)
                    result["action_id"] = action["id"]
                    # A wait's completed response proves that wait ended, not that colony risks disappeared.
                    if tool == "wait_for_event" and result["completeness"] == "known":
                        self.campaign.action_update(action["id"], "completed", result["id"],
                                                    "Matching wait response returned; pausedAfter retained.")
                atomic_json(self.path / "session.json", client.session)
                append_json(self.path / "history.jsonl", dict(pending, status="returned", seconds=elapsed))
                persistence_seconds = time.monotonic() - persistence_started
                from . import __version__
                from .presentation import present
                gap = wall_started - previous_timing["ended_at"] if previous_timing.get("ended_at") else None
                lease = read_json(self.path / "monitor.json") if (self.path / "monitor.json").exists() else {}
                append_json(self.campaign.path / "telemetry.jsonl", {"at": now(), "version": __version__,
                    "request_id": request_id, "tool": tool, "rpc_seconds": elapsed,
                    "persistence_seconds": persistence_seconds, "total_seconds": time.monotonic()-started,
                    "raw_bytes": len(canonical(payload).encode()), "context_bytes": len(canonical(present(result)).encode()),
                    "internal_view_bytes": len(canonical(result).encode()),
                    "context_bytes_basis": "Candidate presentation, not proof of host delivery or model consumption",
                    "since_previous_call_seconds": gap if gap is not None and gap >= 0 else None,
                    "driver": "monitor" if lease.get("status") == "running" and lease.get("pid") == os.getpid() else "agent_operation"})
                atomic_json(last_timing_path, {"ended_at": time.time(), "request_id": request_id})
                (self.path / "pending.json").unlink()
                if tool == "wait_for_event" and data.get("pausedAfter") is not True:
                    atomic_json(self.path / "pause-uncertain.json", {"request": request_id, "at": now(),
                                "evidence": result["id"], "reason": "Wait ended without a confirmed pause."})
                    result["pause_guard"] = self.ensure_paused(token)
                    result["safety"]["stop"] = True  # A repaired pause still requires review of the unexpected interval.
                return result
            except BaseException as exc:
                # Even local persistence failure after a server response makes this request unsafe to replay.
                # The observation may have been persisted without reaching the agent.
                self.campaign.meta['presentation_reset_at'] = now()
                atomic_json(self.campaign.path / 'campaign.json', self.campaign.meta)
                pending.update(status="unknown", error=str(exc), elapsed_seconds=time.monotonic() - started)
                atomic_json(self.path / "pending.json", pending)
                if action and (self.campaign.action_record(action["id"]) or {}).get("status") not in ("completed", "abandoned"):
                    self.campaign.action_update(action["id"], "unknown", reason=str(exc), internal=True)
                raise

    def advance(self, token, hours, risk, intent, deadline_tick=None, force_reason=None, review=None, max_seconds=40):
        if type(max_seconds) is not int or not 5 <= max_seconds <= 600:
            raise Error("Choose an integer wait budget from 5 to 600 seconds.")
        limits = {"combat": 0.2, "medical": 1, "travel": 2, "routine": 18}
        if type(hours) not in (int, float) or not math.isfinite(hours) or risk not in limits or hours <= 0 or hours > limits[risk]:
            raise Error(f"Choose positive hours within the {risk!r} observation limit: {limits.get(risk)}.")
        if deadline_tick is not None and (type(deadline_tick) not in (int, float) or not math.isfinite(deadline_tick) or deadline_tick < 0):
            raise Error("Deadline must be a finite nonnegative game tick.")
        if not review:
            raise Error("Record the current risk assessment and outstanding deadlines.")
        state = self.campaign.state()
        limits_found = deadlines(self.campaign, deadline_tick)
        deadline_tick = limits_found["earliest"]
        if limits_found["due"]:
            raise Error("A hard safety deadline is due; inspect and act before advancing.")
        if deadline_tick is not None:
            if state["latest_tick"] is None:
                raise Error("Cannot bound a deadline without a reported game tick.")
            available = (deadline_tick - state["latest_tick"]) / (self.campaign.meta["ticks_per_day"] / 24)
            hours = min(hours, available)
            if hours <= 0:
                raise Error("Deadline is due; inspect and act before advancing.")
        args = {"maxSeconds": max_seconds, "maxGameHours": hours, "pause": "always"}
        if force_reason:
            if risk in ("combat", "travel"):
                raise Error("Crisis-cap override is unavailable for combat/travel advancement.")
            args["force"] = True
        self.campaign.event({"kind": "advance_review", "summary": review, "risk": risk,
                             "force_reason": force_reason, "deadline_tick": deadline_tick, "max_seconds": max_seconds})
        return self.call(token, "wait_for_event", args, intent=intent)


    def ensure_paused(self, token, *, emergency=False):
        """The sole uncertainty exception is idempotent ordinary pause, never replaying an order.

        Preserve the original pending request: a paused game does not prove its wait terminated.
        """
        with lock(self.path / "operation.lock"):
            self._owner(token)
            catalog = read_json(self.campaign.path / "raw" / "catalog.json")
            tool = catalog["tools"].get("set_speed")
            if not tool:
                return {"confirmed": False, "urgent": "No reviewed ordinary pause capability in this catalog. Use normal UI under owned control.", "game_state": "unknown"}
            validate(tool["inputSchema"], {"action": "pause"})
            pending_path = self.path / "pending.json"
            if pending_path.exists() and not emergency:
                return {"confirmed": False, "urgent": "An unresolved server operation remains; inspect its handle, or use the emergency idempotent pause safeguard."}
            request = identifier("pause-")
            guard_path = self.path / "pause-uncertain.json"
            atomic_json(guard_path, {"request": request, "at": now(), "status": "attempting",
                                    "preserved_pending": pending_path.exists(), "pid": os.getpid()})
            client = self.client_factory(self.endpoint, read_json(self.path / "session.json"))
            try:
                payload = client.rpc("tools/call", {"name": "set_speed", "arguments": {"action": "pause"}}, request)
                result = self.campaign.ingest("set_speed", {"action": "pause"}, payload, origin="live", request_id=request)
                obs = self.campaign.observation(result["id"])
                data = obs["data"]
                confirmed = pause_confirmed(obs)
                self.campaign.event({"kind": "pause_guard", "summary": "Ordinary pause confirmed" if confirmed else "Pause remains unconfirmed",
                                     "evidence": result["id"], "emergency": emergency, "pending_preserved": pending_path.exists()})
                if confirmed and not pending_path.exists(): guard_path.unlink()
                else: atomic_json(guard_path, {"request": request, "at": now(), "confirmed_at_response": confirmed,
                                             "pending_preserved": pending_path.exists(), "evidence": result["id"]})
                return {"confirmed": confirmed, "evidence": result["id"], "pending_preserved": pending_path.exists(),
                        "safe_to_advance": confirmed and not pending_path.exists()}
            except Exception as exc:
                atomic_json(guard_path, {"request": request, "at": now(), "error": str(exc), "status": "unknown"})
                return {"confirmed": False, "urgent": str(exc), "pending_preserved": pending_path.exists()}

    def stop_monitor(self, token, basis):
        self._owner(token)
        if not basis: raise Error('Record why continuation should stop.')
        lease = read_json(self.path / 'monitor.json')
        if lease.get('status') != 'running': return {'already_stopped': True, 'monitor': lease}
        atomic_json(self.path / (lease['id'] + '.stop.json'), {'at': now(), 'basis': basis, 'id': lease['id']})
        return {'stop_requested': True, 'plan': lease['id'], 'pid': lease['pid'],
                'next': 'Poll the actual existing handle. Stop request does not itself prove pause or server termination.'}

    def reconcile_monitor(self, token, evidence, basis, worker_terminal):
        with lock(self.path / 'operation.lock'):
            self._owner(token)
            lease = read_json(self.path / 'monitor.json')
            if not basis or not worker_terminal: raise Error('Review the original process/handle and explicitly confirm worker termination.')
            if alive(lease.get('pid')) is not False: raise Error('Worker PID is still live or unknown; poll the real handle before reconciliation.')
            if (self.path / 'pending.json').exists(): raise Error('Reconcile the original server request separately; a dead worker is not a terminated wait.')
            obs = self.campaign.observation(evidence)
            if obs['tool'] != 'set_speed' or obs['args'] != {'action': 'pause'} or not pause_confirmed(obs) or freshness(obs, self.campaign.state(), self.campaign.meta)['revalidate']:
                raise Error('Require a fresh complete live ordinary-pause observation for this session.')
            record = dict(lease, status='reconciled', reconciled_at=now(), evidence=evidence, basis=basis)
            atomic_json(self.path / 'monitor.json', record)
            append_json(self.path / 'history.jsonl', {'kind': 'monitor_reconciliation', 'at': now(), 'record': record})
            return {'reconciled': True, 'replayed': False, 'next': 'Review current outcomes and create a new finite plan if appropriate.'}
