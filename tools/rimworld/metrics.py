"""Measurements with unknown components reported as unknown."""

from . import __version__
from collections import Counter
import statistics
import math
from .core import journal
from .control import effect


def metrics(campaign):
    observations, _ = journal(campaign.path / "observations.jsonl")
    roots = [o for o in observations if not o.get("parent_id")]
    waits = [o for o in roots if o["tool"] == "wait_for_event"]
    requests = [o["seconds"] for o in roots if isinstance(o.get("seconds"), (int, float))]
    reads = [o for o in roots if effect(o["tool"], o["args"]).startswith("inspection")]
    signatures = Counter((o["tool"], str(sorted(o["args"].items()))) for o in reads)
    action_status = Counter(a["status"] for a in campaign._actions().values())
    events, _ = journal(campaign.path / "events.jsonl")
    marks = [e for e in events if e.get("kind") == "measurement"]
    intervals, unmatched, invalid = [], [], []
    pairs = {}
    for mark in marks:
        key = (mark.get("loop"), mark.get("phase"))
        if mark.get("edge") == "start":
            if key in pairs:
                unmatched.append(pairs[key])
            pairs[key] = mark
        elif mark.get("edge") == "end":
            start = pairs.pop(key, None)
            if start and isinstance(mark.get("monotonic"), (int, float)) and isinstance(start.get("monotonic"), (int, float)):
                duration = mark["monotonic"] - start["monotonic"]
                qualified = start.get('clock_kind') in ('clock_gettime(CLOCK_MONOTONIC)', 'time.monotonic:system')
                if (not qualified or mark.get('clock_kind') != start.get('clock_kind') or
                        not mark.get('clock_id') or mark.get("clock_id") != start.get("clock_id") or
                        not math.isfinite(duration) or duration < 0):
                    invalid.append({'loop': key[0], 'phase': key[1], 'start': start['id'], 'end': mark['id'],
                                    'reason': 'Unqualified/incompatible clock or invalid elapsed time; not a latency measurement'})
                else:
                    intervals.append({"loop": key[0], "phase": key[1],
                                      "seconds": mark["monotonic"] - start["monotonic"],
                                      "conditions": start.get("conditions"),
                                      "basis": "explicit local markers, not inferred model/runtime telemetry"})
            else:
                unmatched.append(mark)
    unmatched += list(pairs.values())
    telemetry, _ = journal(campaign.path / "telemetry.jsonl")
    def distribution(key):
        values = [row[key] for row in telemetry if type(row.get(key)) in (int, float)]
        return {"samples": len(values), "sum": sum(values) if values else None,
                "median": statistics.median(values) if values else None,
                "max": max(values) if values else None}
    reviews = campaign.issue_reviews()
    return {"tooling_version": __version__, "campaign": campaign.meta["id"],
            "automatic_telemetry": {key: distribution(key) for key in
                ("rpc_seconds", "persistence_seconds", "total_seconds", "context_bytes", "raw_bytes", "since_previous_call_seconds")},
            "telemetry_origins": dict(Counter(row.get("driver", "unknown") for row in telemetry)),
            "loop_timing_limits": "since_previous_call includes agent, orchestration, user/idle and local work; it is not isolated model reasoning time. Server event-to-pause timing is unavailable unless supplied by the server.",
            "monitor_stops": dict(Counter(e["summary"] for e in events if e.get("kind") == "monitor_stop")),
            "monitor_cycles": sum(e.get("kind") == "monitor_cycle" for e in events),
            "pause_guards": [{"id": e["id"], "result": e["summary"]} for e in events if e.get("kind") == "pause_guard"],
            "observations": len(roots), "origin_counts": dict(Counter(o["origin"] for o in roots)),
            "request_seconds": {"sum": sum(requests) if requests else None,
                                "median": statistics.median(requests) if requests else None},
            "wait_ticks": sum(o["data"].get("ticksWaited", 0) for o in waits),
            "wait_causes": dict(Counter(o["data"].get("cause", "unknown") for o in waits)),
            "incomplete_observations": sum(o["completeness"] != "known" for o in roots),
            "repeated_inspection_signatures": [{"tool": k[0], "args": k[1], "count": v}
                                              for k, v in signatures.items() if v > 1],
            "action_status": dict(action_status), "marked_intervals": intervals,
            "unmatched_markers": len(unmatched), "invalid_intervals": invalid,
            "overdue_review_issues": [i["id"] for i in reviews if i["revisit_due"] is True],
            "recorded_recurring_issues": [i["id"] for i in reviews if i["recurring"]],
            "recorded_missed_deadlines": [e["id"] for e in events if e.get("kind") == "missed_deadline"],
            "recorded_strategic_errors": [e["id"] for e in events if e.get("kind") == "strategy_error"],
            "recorded_milestones": [{"id": e["id"], "summary": e["summary"]}
                                    for e in events if e.get("kind") == "milestone"],
            "unmeasured_unless_explicitly_marked": ["model reasoning", "approval/orchestration overhead",
                                                  "game paused wall time", "event-to-action latency"],
            "interpretation": "Repeated reads may be necessary. Conditions and difficulty confound comparisons; no win-rate claim."}
