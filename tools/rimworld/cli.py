"""Command-line entry point. Offline commands never contact RimWorld."""

import argparse
import json
import os
from pathlib import Path
import time

from . import __version__
from .core import Error, identifier, now, read_json, require_fields
from .control import Control, effect
from .history import add_shot, capture, checkpoint, review_shot, windows
from .knowledge import adopt_shared, context, promote, retrieve, run_knowledge, save_lesson
from .mcp import validate
from .memory import Campaign, init_campaign
from .metrics import metrics
from .runs import list_runs, resume_run


def obj(text):
    try:
        value = json.loads(text)
    except ValueError as exc:
        raise Error("Argument must be valid JSON.") from exc
    if not isinstance(value, dict):
        raise Error("Arguments must be a JSON object.")
    return value


def parser():
    p = argparse.ArgumentParser(description="RimWorld evidence, control, memory and history support.")
    p.add_argument("--full-output", action="store_true", help="Return full structured provenance/risk fingerprints; retrieve is always full.")
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument("--campaign", "--run", dest="campaign", help="Explicit named run in campaigns/.")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command", required=True)
    q = sub.add_parser("mechanics", help="Shared sourced knowledge; no run required, no game contact.")
    q.add_argument("query", nargs="?", default=""); q.add_argument("--id"); q.add_argument("--limit", type=int, default=8)
    q.add_argument("--file", type=Path, help="Save a reviewed sourced mechanics record, never campaign state.")
    q = sub.add_parser("capabilities", help="Offline API discovery; run optional, no game contact.")
    q.add_argument("query", nargs="?", default=""); q.add_argument("--tool")
    q = sub.add_parser("spatial", help="Select full recorded entity properties by ID or rectangle.")
    q.add_argument("--observation", required=True); q.add_argument("--rect", nargs=4, type=int)
    q.add_argument("--ids", nargs="+")
    q = sub.add_parser("init", help="Create local campaign records; never starts a game.")
    q.add_argument("name"); q.add_argument("--spec", type=Path, required=True)
    q = sub.add_parser("new", help="Create a named run from the agreed specification; no game action.")
    q.add_argument("name"); q.add_argument("--spec", type=Path, required=True)
    sub.add_parser("runs", aliases=["list"], help="List named runs from compact local records only.")
    q = sub.add_parser("resume", help="Locate a named run and its required reads; no save load or time change.")
    q.add_argument("name")
    q = sub.add_parser("packet", help="Read a focused local decision packet with all urgent work retained.")
    q.add_argument("--topic"); q.add_argument("--entity")
    q = sub.add_parser("handoff", help="Save an immutable run snapshot; no live game call.")
    q.add_argument("--reason", required=True); q.add_argument("--next", required=True); q.add_argument("--uncertainties", required=True)
    for name in ("decide", "outcome", "incident"):
        q = sub.add_parser(name)
        q.add_argument("--json", required=True, help="Structured record; no temporary file required.")
    q = sub.add_parser("lesson-review")
    q.add_argument("id"); q.add_argument("--status", required=True); q.add_argument("--review", required=True); q.add_argument("--lesson")
    sub.add_parser("rebuild", help="Rebuild derived observation views/indexes without rewriting original journals.")
    sub.add_parser("brief", help="Regenerate a local current-fact brief; no live read.")
    q = sub.add_parser("ingest", help="Ingest a recorded response without executing it.")
    q.add_argument("tool"); q.add_argument("--args", default="{}")
    q.add_argument("--response", type=Path, required=True)
    q.add_argument("--origin", choices=("recorded", "fixture", "external"), default="recorded")
    q.add_argument("--tick", type=float); q.add_argument("--seconds", type=float)
    q.add_argument("--source-captured-at")
    q = sub.add_parser("retrieve", help="Read full saved evidence selectively.")
    q.add_argument("--tool"); q.add_argument("--entity"); q.add_argument("--observation")
    q = sub.add_parser("retire", help="Remove resolved detail from working context while preserving evidence.")
    q.add_argument("--observation", required=True); q.add_argument("--evidence", required=True)
    q.add_argument("--reason", required=True)
    q = sub.add_parser("recall", help="Find relevant mechanics, local lessons and unresolved intentions.")
    q.add_argument("query"); q.add_argument("--entity"); q.add_argument("--limit", type=int, default=8)
    q = sub.add_parser("context", help="Retrieve situation-specific lessons and evidence pointers.")
    q.add_argument("topic"); q.add_argument("--entity")
    q = sub.add_parser("issue")
    q.add_argument("--file", type=Path); q.add_argument("--id")
    q = sub.add_parser("event", help="Record a decision, verification, observation or milestone.")
    q.add_argument("--file", type=Path, required=True)
    q = sub.add_parser("lesson")
    q.add_argument("--file", type=Path); q.add_argument("--review"); q.add_argument("--topic")
    q.add_argument("--shared", action="store_true"); q.add_argument("--full", action="store_true")
    q.add_argument("--promote"); q.add_argument("--adopt", action="store_true")
    q = sub.add_parser("action", help="Review a tracked gameplay outcome using evidence.")
    q.add_argument("--id"); q.add_argument("--status"); q.add_argument("--evidence"); q.add_argument("--reason")
    q = sub.add_parser("reconcile-clock", help="Record a reviewed clock change from current bound status; never loads a save.")
    q.add_argument("--evidence", required=True); q.add_argument("--review", required=True)
    q = sub.add_parser("reconcile-actions", help="Reconcile selected pending outcomes after a verified same-game reconnect; never replay.")
    q.add_argument("ids", nargs="+"); q.add_argument("--evidence", required=True); q.add_argument("--review", required=True)
    sub.add_parser("metrics")
    q = sub.add_parser("measure", help="Explicit timing marker; unavailable timing is never inferred.")
    q.add_argument("--loop", required=True); q.add_argument("--phase", required=True)
    q.add_argument("--edge", choices=("start", "end"), required=True)
    q.add_argument("--clock-id", required=True, help="Stable ID for this host boot/clock period.")
    q.add_argument("--conditions", required=True)
    q = sub.add_parser("controller")
    q.add_argument("op", choices=("claim", "inspect", "release", "reconcile", "handle"))
    q.add_argument("--endpoint"); q.add_argument("--owner"); q.add_argument("--token")
    q.add_argument("--control-available", action="store_true"); q.add_argument("--basis")
    q.add_argument("--evidence"); q.add_argument("--server-terminal", action="store_true")
    q.add_argument("--request"); q.add_argument("--handle-kind"); q.add_argument("--handle-value")
    q = sub.add_parser("pause", help="Confirm ordinary pause; emergency mode preserves unresolved requests.")
    q.add_argument("--token", required=True); q.add_argument("--emergency", action="store_true")
    q = sub.add_parser("connect", help="Negotiate MCP and cache the catalog under exclusive control.")
    q.add_argument("--endpoint"); q.add_argument("--token", required=True)
    q = sub.add_parser("bind", help="Bind a reviewed live status to the authorized campaign.")
    q.add_argument("--observation", required=True); q.add_argument("--expected", required=True)
    q.add_argument("--basis", required=True); q.add_argument("--token", required=True)
    q = sub.add_parser("catalog", help="Inspect or classify the saved tool catalog.")
    q.add_argument("--tool"); q.add_argument("--effect"); q.add_argument("--basis"); q.add_argument("--token")
    q = sub.add_parser("observe", help="Read a finite set of ordinary queries in one agent exchange.")
    q.add_argument("--queries", required=True); q.add_argument("--token", required=True)
    q = sub.add_parser("act", help="Issue one ordinary order with an inline intent and outcome contract.")
    q.add_argument("--json", required=True); q.add_argument("--token", required=True)
    q = sub.add_parser("call", help="Execute one ordinary MCP tool under an existing controller.")
    q.add_argument("tool"); q.add_argument("--args", default="{}"); q.add_argument("--token", required=True)
    q.add_argument("--intent"); q.add_argument("--family", default="general")
    q.add_argument("--track", action="store_true", help="Track a strategic outcome; requires --intent. Requests are always journaled.")
    q.add_argument("--check", type=Path); q.add_argument("--setup", action="store_true")
    q = sub.add_parser("batch", help="Bounded serialized operations; stops at failures or new events.")
    q.add_argument("--file", type=Path, required=True); q.add_argument("--token", required=True)
    q = sub.add_parser("session", help="Persistent standard MCP JSON-RPC over stdin/stdout; reuse owned control.")
    q.add_argument("--token", required=True); q.add_argument("--setup", action="store_true")
    q = sub.add_parser("shot")
    q.add_argument("op", choices=("windows", "add", "capture", "review"))
    q.add_argument("--file", type=Path); q.add_argument("--window", type=int)
    q.add_argument("--tick", type=float); q.add_argument("--subject"); q.add_argument("--caption")
    q.add_argument("--framing"); q.add_argument("--id"); q.add_argument("--note")
    q.add_argument("--evidence", nargs="+"); q.add_argument("--map-index", type=int)
    q = sub.add_parser("checkpoint")
    q.add_argument("--file", type=Path, help="Omit to inspect which checkpoint is due.")
    q = sub.add_parser("ui", help="Prepare a tracked normal-UI action for computer-control tools.")
    q.add_argument("--intent", required=True); q.add_argument("--family", required=True)
    q.add_argument("--target", required=True); q.add_argument("--token", required=True)
    return p


def run(args):
    if args.command == "mechanics":
        from .mechanics import search,save
        if args.file:return save(args.root,read_json(args.file))
        env=Campaign(args.root,args.campaign).meta.get('setup',{}) if args.campaign else None
        return search(args.root,args.query,args.id,args.limit,env)
    if args.command == "capabilities":
        from .capabilities import discover
        return discover(args.root,args.query,args.tool,Campaign(args.root,args.campaign) if args.campaign else None)
    if args.command in ("runs", "list"):
        return list_runs(args.root)
    if args.command in ("init", "new", "resume"):
        if args.campaign and args.campaign != args.name:
            raise Error("Conflicting run names; selection must be explicit and consistent.")
        if args.command == "resume":
            return resume_run(args.root, args.name, full=args.full_output)
        spec = read_json(args.spec)
        if args.command == "new":
            if not isinstance(spec, dict) or spec.get("mode") != "fresh":
                raise Error("new requires mode=fresh; use resume for an existing run.")
            intake = spec.get("intake")
            if isinstance(intake, dict) and intake.get("unresolved_questions"):
                raise Error("Resolve the recorded player questions before creating a new run.")
        return init_campaign(args.root, args.name, spec)
    if args.command == "lesson" and args.shared:
        if args.campaign: raise Error("Use --promote to share a run lesson; do not combine --run and --shared.")
        return (save_lesson(args.root, read_json(args.file), args.review, shared=True) if args.file else
                retrieve(args.root, args.topic, full=args.full))
    if args.command == "shot" and args.op == "windows":
        return windows()
    if not args.campaign:
        raise Error("--campaign is required; the current game must never be guessed from a default.")
    campaign = Campaign(args.root, args.campaign)
    command = args.command
    if command in ("packet", "handoff", "decide", "outcome", "incident", "lesson-review"):
        from . import continuity
        if command == "packet": return continuity.packet(campaign, args.topic, args.entity)
        if command == "handoff": return continuity.handoff(campaign, args.reason, args.next, args.uncertainties)
        if command == "lesson-review": return continuity.review_candidate(campaign, args.id, args.status, args.review, args.lesson)
        return getattr(continuity, command)(campaign, obj(args.json))
    if command == "lesson":
        if args.adopt: return adopt_shared(campaign, args.review)
        if args.promote:
            if not args.file: raise Error("Promotion needs a generalized draft --file.")
            return promote(campaign, args.promote, read_json(args.file), args.review)
        if args.file: return save_lesson(args.root, read_json(args.file), args.review, campaign=campaign)
        if not args.topic: raise Error("Use --topic or --file; learning belongs to this selected run.")
        return run_knowledge(campaign, args.topic, full=args.full)
    if command == "reconcile-clock": return campaign.reconcile_clock(args.evidence, args.review)
    if command == "reconcile-actions":
        return campaign.reconcile_actions(args.ids, args.evidence, args.review)
    if command == "rebuild": return campaign.rebuild()
    if command == "brief":
        return campaign.refresh()
    if command == "ingest":
        return campaign.ingest(args.tool, obj(args.args), read_json(args.response), origin=args.origin,
                               tick=args.tick, seconds=args.seconds, source_captured_at=args.source_captured_at)
    if command == "spatial":
        from .capabilities import spatial
        return spatial(campaign.observation(args.observation),args.rect,args.ids)
    if command == "retrieve":
        return campaign.observation(args.observation) if args.observation else campaign.retrieve(args.tool, args.entity)
    if command == "retire":
        return campaign.retire(args.observation, args.evidence, args.reason)
    if command == "recall":
        from .knowledge import recall
        return recall(campaign,args.query,args.entity,args.limit)
    if command == "context":
        return context(campaign, args.topic, args.entity)
    if command == "issue":
        return campaign.issue(read_json(args.file), args.id) if args.file else campaign.issue_reviews()
    if command == "event":
        value = read_json(args.file)
        if value.get("kind") == "decision":
            require_fields(value, ("rationale", "expected_result", "risks", "alternatives", "reconsider_when"))
        return campaign.event(value)
    if command == "action":
        return campaign.action_update(args.id, args.status, args.evidence, args.reason) if args.id else list(campaign._actions().values())
    if command == "metrics":
        return metrics(campaign)
    if command == "measure":
        return campaign.event({"kind": "measurement", "summary": f"{args.phase} {args.edge}",
                               "loop": args.loop, "phase": args.phase, "edge": args.edge,
                               "monotonic": time.monotonic(), "clock_id": args.clock_id, "clock_kind": "time.monotonic:system",
                               "conditions": args.conditions, "version": __version__})
    if command == "shot":
        if args.op == "review":
            return review_shot(campaign, args.id, args.note)
        if args.op == "add":
            if args.file is None:
                raise Error("shot add requires --file.")
            return add_shot(campaign, args.file, args.tick, args.subject, args.caption, args.framing, evidence=args.evidence, map_index=args.map_index)
        if args.window is None:
            raise Error("shot capture requires a window from a fresh shot windows result.")
        return capture(campaign, args.window, args.tick, args.subject, args.caption, args.framing, evidence=args.evidence, map_index=args.map_index)
    if command == "checkpoint":
        return checkpoint(campaign, read_json(args.file)) if args.file else campaign.checkpoints()
    control = Control(campaign, getattr(args, "endpoint", None))
    if command == "controller":
        if args.op == "inspect":
            return control.inspect()
        if args.op == "claim":
            return control.claim(args.owner, args.control_available, args.basis)
        if args.op == "release":
            return control.release(args.token, args.basis)
        if args.op == "reconcile":
            return control.reconcile(args.token, args.evidence, args.basis, args.server_terminal)
        if args.op == "handle":
            control.attach_handle(args.request, args.handle_kind, args.handle_value)
            return {"handle_recorded": True}
    if command == "pause": return control.ensure_paused(args.token, emergency=args.emergency)
    if command == "connect":
        return control.connect(args.token)
    if command == "bind":
        return control.bind(args.observation, obj(args.expected), args.basis, args.token)
    if command == "catalog":
        catalog = read_json(campaign.path / "raw" / "catalog.json")
        if args.effect:
            if not args.tool:
                raise Error("Classification requires --tool.")
            return control.classify(args.token, args.tool, args.effect, args.basis)
        if args.tool:
            if args.tool not in catalog["tools"]:
                raise Error("Tool not present in the catalog.")
            return catalog["tools"][args.tool]
        return {"captured_at": catalog["captured_at"], "schema_digest": catalog["schema_digest"],
                "tools": [{"name": name, "effect": effect(name, {})} for name in catalog["tools"]]}
    if command == "session":
        from .session import serve
        return serve(control, args.token, setup=args.setup)
    if command == "act":
        spec = obj(args.json); require_fields(spec, ("tool", "intent"))
        from .outcomes import contract
        check = contract(spec["outcome"]) if spec.get("outcome") else spec.get("check")
        family = spec.get("outcome", {}).get("family", spec.get("family", "general"))
        if spec["tool"] in ("wait_for_event", "set_speed"):
            raise Error("Use call wait_for_event with pause=always, or pause.")
        for dependency in spec.get("requires_completed", []):
            if campaign._actions().get(dependency, {}).get("status") != "completed":
                raise Error("Required action is not verified complete: " + dependency)
        return control.call(args.token, spec["tool"], spec.get("args", {}), spec["intent"], family, check, track=spec.get("track",True))
    if command == "observe":
        queries = json.loads(args.queries)
        if not isinstance(queries, list) or not 1 <= len(queries) <= 32:
            raise Error("Use 1–32 explicit read queries; this is a bounded read packet.")
        catalog = read_json(campaign.path / "raw/catalog.json")
        for q in queries:
            require_fields(q, ("tool",))
            if not effect(q["tool"], q.get("args", {})).startswith("inspection"):
                raise Error("Observe only accepts classified ordinary reads.")
            if q["tool"] not in catalog["tools"]: raise Error("Unknown read tool.")
            validate(catalog["tools"][q["tool"]]["inputSchema"], q.get("args", {}))
        result = []
        for q in queries:
            value = control.call(args.token, q["tool"], q.get("args", {})); result.append(value)
            if value.get("identity_mismatch") or value["completeness"] == "unavailable": break
        return {"observations": result, "game_advanced": False,
                "note": "All warnings preserved. This read packet does not authorize continuing through danger."}
    if command == "call":
        return control.call(args.token, args.tool, obj(args.args), args.intent, args.family,
                            read_json(args.check) if args.check else None, args.setup, track=args.track)
    if command == "batch":
        steps = read_json(args.file)
        if not isinstance(steps, list) or not steps:
            raise Error("A batch is a nonempty JSON list.")
        catalog = read_json(campaign.path / "raw" / "catalog.json")
        for step in steps:
            require_fields(step, ("tool",))
            if step["tool"] == "wait_for_event":
                raise Error("Waits are standalone calls, not precommitted batch steps.")
            if step["tool"] not in catalog["tools"]:
                raise Error("Unknown batch tool.")
            validate(catalog["tools"][step["tool"]]["inputSchema"], step.get("args", {}))
            kind = effect(step["tool"], step.get("args", {}))
            if kind == "unclassified":
                rules_path = control.path / "classifications.json"
                rule = read_json(rules_path).get(step["tool"]) if rules_path.exists() else None
                from .core import digest
                if rule and rule["schema_digest"] == digest(catalog["tools"][step["tool"]]):
                    kind = rule["effect"]
            if kind in ("denied", "unclassified"):
                raise Error("Batch contains a prohibited or unclassified tool.")
            if kind == "mutation" and (step.get("track", False) or step.get("check") is not None) and not step.get("intent"):
                raise Error("Tracked batch outcomes need an intent.")
            from .core import slug
            slug(step.get("family", "general"))
            for dependency in step.get("requires_completed", []):
                record = campaign._actions().get(dependency)
                if not record or record["status"] != "completed":
                    raise Error("Batch dependency is not verified completed: " + dependency)
        results = []
        for step in steps:
            result = control.call(args.token, step["tool"], step.get("args", {}),
                                  step.get("intent"), step.get("family", "general"),
                                  step.get("check"), step.get("setup", False), track=step.get("track",False))
            results.append(result)
            from .safety import assess
            observations = [campaign.observation(result["id"])] + [campaign.observation(c["id"]) for c in result.get("bundle", [])]
            safety = assess(campaign, observations)
            if safety["stop"] or result.get("identity_mismatch"):
                return {"stopped": True, "reason": "Risk/coverage/identity needs review", "safety": safety, "results": results}
        return {"stopped": False, "results": results}
    if command == "ui":
        control._owner(args.token)
        control._no_pending()
        if not campaign.meta.get("binding"):
            raise Error("Bind the reviewed game identity before UI control.")
        action = campaign.action("normal_ui", {"target": args.target}, args.intent, args.family)
        return {"action": action, "steps": [
            "Read the current game screen through the computer-control tool.",
            "Select the actor and open the real action/targeter. For abilities, do not pass an unsupported targetId.",
            "Read the changed screen, confirm the targeter and current target position, then click the visible target.",
            "Inspect actual gameplay outcome after appropriate advancement; record fresh evidence before marking complete."],
            "warning": "This command prepares a tracked action; it does not click, cast, or claim success."}
    raise Error("Unhandled command.")


def main(argv=None):
    try:
        args = parser().parse_args(argv)
        result = run(args)
        if args.command == "session": return 0
        from .presentation import present
        print(result if isinstance(result, str) else json.dumps(result if args.full_output or args.command == "retrieve" else present(result), ensure_ascii=False, separators=(",", ":")))
        return 0
    except (Error, OSError, ValueError, KeyError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
