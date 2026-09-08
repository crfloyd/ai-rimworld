"""Normalize uncertainty before any summarization or filtering."""

import copy
import json
import math
import datetime as dt
from .core import Error, digest, identifier, now


MISSING = object()
FLAGS = ("error", "message", "warning", "warnings", "largeOutput", "truncated",
         "rejected", "failedCells", "_threatWarning", "_dialogOpen", "_notifications",
         "crisisCap", "pausedAfter", "_paused", "_normalizationWarnings", "_mcpAdditionalText", "_protocolNotifications")


def decode(payload):
    """Accept a direct result, JSON-RPC, or MCP content; keep ambiguity explicit."""
    if not isinstance(payload, dict):
        return {"error": "Expected an object response", "original": payload}, "unavailable"
    transport_notifications = payload.get("_transportNotifications")
    if "jsonrpc" in payload:
        if "error" in payload:
            return {"error": payload["error"]}, "unavailable"
        if "result" not in payload:
            return {"error": "JSON-RPC response has no result"}, "unavailable"
        payload = payload["result"]
    if not isinstance(payload, dict):
        return {"error": "Result is not an object", "original": payload}, "unavailable"
    if "content" in payload or "structuredContent" in payload:
        blocks = payload.get("content", [])
        structured = payload.get("structuredContent")
        texts, other = [], []
        if not isinstance(blocks, list):
            return {"error": "MCP content is not a list"}, "unavailable"
        for block in blocks:
            if isinstance(block, dict) and block.get("type") == "text":
                texts.append(block.get("text", ""))
            else:
                other.append(block)
        if isinstance(structured, dict):
            result = copy.deepcopy(structured)
        else:
            parsed = []
            for text in texts:
                try:
                    parsed.append(json.loads(text))
                except (ValueError, TypeError):
                    pass
            if len(parsed) != 1 or not isinstance(parsed[0], dict):
                return {"error": "No unambiguous structured tool result",
                        "text": texts, "otherContent": other}, "unavailable"
            result = parsed[0]
        additional = []
        for text in texts:
            try:
                json.loads(text)
            except (ValueError, TypeError):
                additional.append(text)
        if additional:
            result["_mcpAdditionalText"] = additional
        if texts:
            result["_mcpText"] = texts
        if other:
            result["_otherContent"] = other
        if payload.get("isError"):
            result["_mcpError"] = True
        payload = result
    if transport_notifications:
        payload["_protocolNotifications"] = transport_notifications
    return copy.deepcopy(payload), None


def expected_fields(tool, args, data):
    if tool == "get_area":
        return ["grid"] if args.get("render") == "ascii" else (
            ["thingGroups", "terrainSummary"] if args.get("summary") else ["things", "terrainSummary"])
    if tool == "get_status":
        return ["loaded"] + (["ticksGame", "maps"] if data.get("loaded") is True else [])
    if tool == "get_alerts":
        return ["activeAlerts"]
    if tool == "get_resources":
        return ["resources"]
    if tool == "list_colonists":
        return ["colonists"]
    if tool == "list_things": return ["groups"] if args.get("summary") else ["things"]
    if tool == "list_fires": return ["fires"]
    if tool == "list_wildlife":
        return ["animals"]
    if tool == "get_pawn":
        return {"health": ["hediffs", "overallHealthPercent"], "gear": ["equipment", "apparel"],
                "needs": ["needs"]}.get(args.get("tab"), ["id"])
    if tool == "wait_for_event":
        return ["cause", "ticksWaited", "pausedAfter"]
    return []


def normalize(tool, args, payload, campaign_id, session_id, origin="live",
              tick=None, map_index=None, seconds=None, request_id=None, source_captured_at=None):
    if tick is not None and (type(tick) not in (int, float) or not math.isfinite(tick) or tick < 0):
        raise Error("Caller tick must be a finite nonnegative number.")
    data, forced = decode(payload)
    empty_basis = None
    if tool == "list_fires" and data.get("ok") is True and type(data.get("fireCount")) is int and data["fireCount"] == 0 and "fires" not in data:
        data["fires"] = []
        empty_basis = "Explicit successful fireCount=0; raw response preserved."
    missing = [key for key in expected_fields(tool, args, data) if key not in data]
    # Field names have different meanings on different tabs/tools (map.colonists is a count).
    types = {
        "get_area": {"things": list, "thingGroups": list, "terrainSummary": dict, "grid": list},
        "get_status": {"loaded": bool, "paused": bool, "maps": list, "bundled": dict},
        "get_alerts": {"activeAlerts": list}, "get_resources": {"resources": list},
        "list_colonists": {"colonists": list}, "list_wildlife": {"animals": list},
        "list_things": {"things": list, "groups": list}, "list_fires": {"fires": list},
        "wait_for_event": {"cause": str, "ticksWaited": (int, float), "pausedAfter": bool},
    }.get(tool, {})
    if tool == "get_pawn":
        types = {"health": {"hediffs": list, "overallHealthPercent": (int, float), "downed": bool, "dead": bool}, "needs": {"needs": list, "thoughts": list},
                 "gear": {"equipment": list, "apparel": list}}.get(args.get("tab"), {})
    malformed = [k for k, expected in types.items() if k in data and
                 (not isinstance(data[k], expected) or (expected == (int, float) and
                  (isinstance(data[k], bool) or not math.isfinite(data[k]))))]
    state = forced or "known"
    if data.get("ok") is False or data.get("_mcpError") or data.get("error"):
        state = "unavailable"
    elif data.get("largeOutput") or data.get("truncated"):
        state = "partial"
    elif data.get("rejected", 0) or missing or malformed:
        state = "partial"
    observed_tick = data.get("ticksGame", data.get("ticks"))
    if observed_tick is not None and (type(observed_tick) not in (int, float) or
                                      not math.isfinite(observed_tick) or observed_tick < 0):
        malformed.append("game tick")
        observed_tick = None
        state = "partial"
    tick_basis = "response" if observed_tick is not None else None
    if observed_tick is None and tick is not None:
        observed_tick, tick_basis = tick, "caller-supplied"
    explicit_map = data.get("mapIndex", args.get("mapIndex", map_index))
    # Omitted current-map indices remain unknown. They are never assumed to be 0.
    scope = copy.deepcopy(args)  # Include every filter, including future schema additions.
    if explicit_map is not None:
        scope["mapIndex"] = explicit_map
    if tool == "wait_for_event" and type(data.get("ticksWaited")) in (int, float) and data["ticksWaited"] < 0:
        malformed.append("ticksWaited"); state = "partial"
    if malformed:
        message = "Malformed fields require inspection: " + ", ".join(malformed)
        data.setdefault("warning", message)
        data["_normalizationWarnings"] = [message]
    captured = now()
    return {"normalizer_version": 4, "id": identifier("obs-"), "campaign_id": campaign_id, "session_id": session_id,
            "origin": origin, "tool": tool, "args": copy.deepcopy(args), "scope": scope,
            "key": tool + ":" + digest(scope)[:20], "captured_at": captured,
            "source_captured_at": source_captured_at or (captured if origin in ("live", "fixture") else None),
            "tick": observed_tick, "tick_basis": tick_basis, "map_index": explicit_map,
            "completeness": state, "missing": missing, "malformed": malformed,
            "coverage": {"model": "reviewed fields; semantics require agent judgment" if types else "unmodeled",
                         "kind": "aggregate" if args.get("summary") else "requested scope",
                         "known_empty_basis": empty_basis, "expected": expected_fields(tool, args, data),
                         "present": [k for k in data if not k.startswith("_")],
                         "missing": missing, "malformed": malformed,
                         "schema": "reviewed tool/tab fields" if types else "unmodeled; inspect before automation"}, "data": data, "seconds": seconds,
            "request_id": request_id, "warnings": {k: data[k] for k in FLAGS if k in data}}


def bundle_children(observation):
    data = observation["data"]
    children = []
    bundle = data.get("bundled", {})
    if not isinstance(bundle, dict):
        return []
    for name, result in bundle.items():
        child = normalize(name, {}, result, observation["campaign_id"], observation["session_id"],
                          observation["origin"], request_id=observation["request_id"])
        child["parent_id"] = observation["id"]
        child["captured_at"] = observation["captured_at"]
        child["source_captured_at"] = observation.get("source_captured_at")
        if child["tick"] is None:
            child["tick"] = observation["tick"]
            child["tick_basis"] = "parent-bundle; individual timing not supplied"
        children.append(child)
    return children


def pack_rows(rows):
    """Lossless columnar encoding; explicit absent cells distinguish null/missing.

    Choose it only when smaller than literal rows. No fields or rows are dropped.
    """
    if not rows or not all(isinstance(r, dict) for r in rows): return rows
    columns = sorted({k for r in rows for k in r})
    result = {"encoding": "columns-v1", "columns": columns,
              "rows": [[r.get(k) for k in columns] for r in rows]}
    absent = {str(i): [j for j,k in enumerate(columns) if k not in r]
              for i,r in enumerate(rows) if any(k not in r for k in columns)}
    if absent: result["absent"] = absent
    return result if len(json.dumps(result)) < len(json.dumps(rows)) else rows


def unpack_rows(value):
    if isinstance(value, list): return value
    if not isinstance(value, dict) or value.get("encoding") != "columns-v1":
        raise Error("Not a columns-v1 table.")
    return [{k: row[j] for j,k in enumerate(value["columns"])
             if j not in value.get("absent", {}).get(str(i), [])}
            for i,row in enumerate(value["rows"])]


def compact(observation, *, full=False):
    """Compact typed views; full evidence is always available. Risk extraction precedes reduction."""
    from collections import Counter
    from .safety import signals
    d = observation["data"]
    result = {k: observation[k] for k in ("id", "tool", "scope", "tick", "tick_basis",
                                         "captured_at", "completeness", "missing", "origin")}
    result["model"] = observation.get("coverage", {}).get("model", "unmodeled")
    result["query_kind"] = observation.get("coverage", {}).get("kind", "unknown")
    result["warnings"] = observation["warnings"]
    result["evidence"] = observation.get("raw", observation["id"])
    result["risks"] = signals(observation)
    data = {k: v for k, v in d.items() if k not in ("_mcpText", "bundled")}
    if observation["completeness"] != "known":
        result["message"] = d.get("message", d.get("error", "Partial or unavailable observation"))
        result["known_subset"] = {k: v for k, v in data.items() if k not in observation.get("malformed", [])}
        result["known_subset"] = {k: pack_rows(v) if isinstance(v,list) else v
                                  for k,v in result["known_subset"].items()}
        result["coverage"] = observation.get("coverage")
        return result
    tool = observation["tool"]
    if full:
        result["data"] = data
    elif tool == "get_pawn" and observation["args"].get("tab") == "health":
        result["health"] = data
    elif tool == "get_pawn" and observation["args"].get("tab") == "needs":
        result["needs"] = data
    elif tool == "get_status":
        result["status"] = {k: v for k, v in data.items() if k not in ("statusBundleHint",)}
        result["bundle_tools"] = list(d.get("bundled", {}))
    elif tool in ("get_area", "list_things") and isinstance(d.get("things"), list):
        things = d["things"]
        result["counts"] = dict(Counter(t.get("def", t.get("defName", "?")) for t in things if isinstance(t, dict)))
        result["data"] = {k: pack_rows(v) if isinstance(v, list) else v for k,v in data.items()}
    elif tool in ("list_architect", "list_recipes", "get_research"):
        result["data"] = {k: pack_rows(v) if isinstance(v, list) else v for k,v in data.items()}
    else:
        result["data"] = data
    return result


def changed(previous, current):
    """Actual changed values. Missing keys are not inferred to mean empty/deleted."""
    if previous is None:
        return {"first_observation": True}
    old, new = previous["data"], current["data"]
    keys = [k for k in new if k not in ("_mcpText", "bundled") and (k not in old or new[k] != old[k])]
    return {"changed_fields": keys, "not_returned_now": [k for k in old if k not in new and k != "_mcpText"],
            "previous_evidence": previous["id"]}


def delta_view(previous, current):
    change = changed(previous, current)
    if previous is None or current["completeness"] != "known" or previous["completeness"] != "known":
        result = compact(current)
    else:
        reduced = copy.deepcopy(current)
        reduced["data"] = {k: current["data"][k] for k in change["changed_fields"]}
        result = compact(reduced)
        # Keep all active signals, even if their source values are unchanged.
        from .safety import signals
        result["risks"] = signals(current)
        result["unchanged"] = not change["changed_fields"] and not change["not_returned_now"]
        result["view"] = "delta; omitted unchanged fields remain in previous evidence"
    result["delta"] = change
    # Lossless positional patches against a named prior observation, not guessed
    # entity identity. Full evidence remains retrievable; changed values survive.
    if previous is not None and current["completeness"] == previous["completeness"] == "known":
        patches = {}
        for key in change.get("changed_fields", []):
            old, new = previous["data"].get(key), current["data"].get(key)
            if isinstance(old, list) and isinstance(new, list) and len(old) == len(new) and old:
                patch = {"length": len(new), "replace": {str(i): v for i, v in enumerate(new) if v != old[i]}}
                if len(json.dumps(patch)) < len(json.dumps(new)):
                    for body in ("data", "health", "needs", "status"):
                        if key in result.get(body, {}):
                            del result[body][key]
                            patches[key] = patch
                            break
        if patches:
            result["list_changes"] = {"base": previous["id"], "fields": patches,
                "basis": "Replace these zero-based indices in the previous observation; indices are not persistent entity IDs."}
    return result


def path_value(data, path):
    current = data
    for part in path.split(".") if path else []:
        if isinstance(current, dict):
            current = current.get(part, MISSING)
        elif isinstance(current, list) and part.isdecimal() and int(part) < len(current):
            current = current[int(part)]
        else:
            return MISSING
        if current is MISSING:
            return MISSING
    return current


def matches(observation, check):
    """Return true, false, or unknown. Predicates require fresh, complete observations."""
    if observation["completeness"] != "known":
        return None
    if observation["tool"] != check["tool"]:
        return None
    for key, value in check.get("args", {}).items():
        if observation["args"].get(key, MISSING) != value:
            return None
    predicates = check.get("all", [])
    if not predicates:
        raise Error("A verification requires at least one explicit predicate.")
    answers = []
    for predicate in predicates:
        value = path_value(observation["data"], predicate["path"])
        if value is MISSING:
            answers.append(None)
            continue
        expected = predicate.get("value")
        op = predicate["op"]
        if op in ("any_item", "no_item"):
            if not isinstance(value, list): answers.append(None); continue
            values = [matches(dict(observation, data=item), dict(check, all=predicate.get("all", [])))
                      if isinstance(item, dict) else None for item in value]
            answer = True if True in values else (None if None in values else False)
            answers.append((not answer) if op == "no_item" and answer is not None else answer)
        elif op == "eq":
            answers.append(type(value) is type(expected) and value == expected)
        elif op == "contains":
            answers.append(expected in value if isinstance(value, (list, str, dict)) else None)
        elif op == "exists":
            answers.append(value is not None)
        elif op in ("gt", "gte", "lt", "lte"):
            if type(value) not in (int, float) or type(expected) not in (int, float):
                answers.append(None)
            else:
                answers.append({"gt": value > expected, "gte": value >= expected,
                                "lt": value < expected, "lte": value <= expected}[op])
        else:
            raise Error(f"Unsupported verification operator: {op}")
    return False if False in answers else (None if None in answers else True)


def freshness(observation, state, meta, *, live=True, max_age_seconds=120):
    """One policy for context, evidence and safety. A recorded read never proves live freshness."""
    reasons = []
    if observation.get("completeness") != "known": reasons.append("incomplete")
    if live and observation.get("origin") != "live": reasons.append("non-live origin")
    if observation.get("session_id") != (meta.get("session_id") or "unbound"): reasons.append("session changed")
    source_time = observation.get("source_captured_at")
    if not source_time:
        reasons.append("source capture time unknown")
    elif live:
        try:
            captured = dt.datetime.fromisoformat(source_time.replace("Z", "+00:00"))
            if captured.tzinfo is None: raise ValueError("timezone missing")
            age = (dt.datetime.now(dt.timezone.utc) - captured).total_seconds()
            if age > max_age_seconds or age < -5: reasons.append("wall-clock freshness expired or clock skewed")
        except (TypeError, ValueError, AttributeError):
            reasons.append("source capture time invalid")
    if source_time and source_time < meta.get("mutable_facts_invalidated_at", ""):
        reasons.append("gameplay request dispatched after observation; its effects need revalidation")
    if observation.get("epoch", -1) < state.get("epoch", 0): reasons.append("game advanced since observation")
    if state.get("clock_warning"): reasons.append("game clock requires reconciliation")
    return {"revalidate": bool(reasons), "reasons": reasons}


def pause_confirmed(observation):
    d = observation["data"]
    if observation["completeness"] != "known": return False
    if "paused" in d: return d["paused"] is True and d.get("_paused") is not False
    return d.get("_paused") is True
