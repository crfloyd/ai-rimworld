# Control contract

## Supported transport and scope

The default endpoint is `http://localhost:8787/mcp`; it can be supplied at claim/connect time. The standard-library client implements MCP initialization, initialized notification, paginated tool discovery, request IDs, JSON responses, and POST SSE responses. It preserves session IDs and negotiated protocol versions. It makes no automatic retry of gameplay requests and does not offer a background event stream or automatic SSE resumption.

Protocol references: [MCP transports](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports) and [lifecycle](https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle). Disconnecting a request does not imply cancellation. An expired session requires a reviewed reconnect and identity rebind; it never authorizes replaying the last action.

Input validation supports the documented JSON Schema subset in `tools/rimworld/mcp.py`. Unsupported constraints fail explicitly; use a fuller standards-compliant client if a future server requires them. Current tool names are discovered, not assumed. Cached classifications are tied to the captured tool schema/description digest.

## Ownership and interruption

Only one cooperating controller may own an endpoint within this workspace. Loopback URL aliases share a coordination key. A kernel file lock serializes operations; persistent owner and pending-operation files survive process interruption. These records do not stop an unrelated client or another copy of this workspace from controlling the same game. An actual handoff is required.

`controller inspect` is local and reports ownership, pending request, local PID liveness, and an attached orchestration handle. During a yielded command, attach its real handle with:

```sh
python3 rw --campaign NAME controller handle --request REQUEST_ID --handle-kind exec --handle-value ACTUAL_SESSION_ID
```

Poll that actual handle through the host tool. Never infer server termination from elapsed time, a stale file, or local process exit. If a request ends uncertainly, further calls are blocked. Preserve the pending record and determine whether the server operation ended through the original handle, available server diagnostics, or normal UI. Only then use `controller reconcile --token TOKEN --server-terminal --evidence SOURCE --basis REASON`. Reconciliation records the operator's evidence; it does not verify a gameplay outcome or replay anything.

When a tool response is known but local persistence fails, the request is also uncertain. Do not rerun it. A release requires a recorded verified handoff/pause state and no pending operation. It does not itself pause or close the game.

## Identity

A newly connected session is unbound. Its first allowed game call is get_status. Bind a complete live observation to expected fields and record how the authorized game was identified. Colony names alone may be reused; include additional available fields and review the real game. Bindings are evidence attestations, not a server-issued unique save ID.

Reconnect invalidates the previous binding. A later status mismatch clears the binding and stops dependent batches. Missing or changed session identity must be reconciled before using old IDs.

## Actions and verification

Request records cover every MCP call. Mutations are tracked by default with a free-form intention family and remain requested/accepted/started/blocked/interrupted/unknown until verified completed or consciously abandoned with evidence. The families provide review guidance, not a claim that the server exposes action lifecycle events.

Example order shape (use real IDs and an option read from the current menu):

```sh
python3 rw --campaign NAME call order_pawn --args '{"id":"PAWN_ID","targetId":"PATIENT_ID","command":"EXACT_MENU_LABEL"}' --family treatment --intent 'Control the patient bleeding' --check /absolute/path/reviewed-treatment-check.json --token TOKEN
```

A complete accepted response is not proof of treatment. Supply a check grounded in actual response fields; if this version lacks the required timing/detail, use a scoped visual verification event instead. Read health again at an appropriate interval, then:

```sh
python3 rw --campaign NAME action --id ACTION_ID --status completed --evidence FRESH_OBS_ID --reason 'Explain the condition-specific treatment change'
```

Fresh observations can also satisfy explicit predicates supplied via `--check FILE`; see `templates/verification-movement.json`. Predicates require a matching tool/argument scope, complete observation, same session, and a capture after acceptance. Missing fields return unknown. Include map identity and every necessary condition. A weak predicate remains a weak proof: the agent must choose predicates that establish its actual objective.

For treatment, old bandages or a rounded immunity value are insufficient. For rescue, reaching any bed does not establish a safe route or successful treatment. For construction, a blueprint does not establish a completed structure. Keep multiple objectives as separate checks/issues where necessary.

Manual computer-control outcomes use a verification event with an original source, current session ID, and explanatory summary. The agent must actually inspect the evidence; the system cannot infer semantic correctness from a sentence claiming success.

## Time advancement

`advance` records a risk review and requests one wait with `pause=always` and an agent-selected `--max-seconds` budget of 5–600 seconds (default 40). Transport inactivity timeout accommodates this wait plus 15 seconds; it is not a cancellation guarantee. Retain and poll the actual host handle, and keep communicating while a longer wait runs. Maximum requested intervals are 0.2 game hours for combat, 1 for medical monitoring, 2 for travel, and 18 for routine work. These are observation budgets, not difficulty modifiers. Choose shorter intervals when the situation demands it.

An optional deadline tick shortens the interval. Exact ticks use reported data; between explicit tick reports, the memory can derive elapsed ticks from a monitored wait and labels that basis. Revalidate after external control or any unobserved advancement. A due deadline must be handled before advancing.

`--force-reason` permits a reviewed crisis-cap override for routine/medical monitoring only. It is never an automatic response to a repeated warning. An ordinary response preserves the actual pausedAfter value; inspect it rather than assuming the game stopped.

## Unsupported UI targeting

Use `ui --family ... --intent ... --target ... --token TOKEN` to create a tracked normal-UI intent. Then use the host's computer-control tool:

1. Read the current screen and select the actor.
2. Activate the actual gizmo/ability. Do not pass a separate target argument if the MCP action rejects it.
3. Read the targeting state and current visible target position; click through normal controls.
4. Confirm the resulting action and its effect from fresh observations or a sourced verification event.

The bridge intentionally does not guess pixels or expose a direct simulation cast. No image/coordinate template is reused across window sizes. Live ability targeting and macOS capture permissions remain deployment checks; the offline tests cannot establish them.

## Tooling rollback

Commit the preceding tooling revision before changing live control. Restore tooling files only if needed, then reconcile the existing game state. Never restore game saves as a tooling rollback. This release does not modify RimWorld or RimMolt files.

## Audit-hardened execution

See [runner-loop.md](runner-loop.md) for observe/act, finite routine continuation, qualification, danger acknowledgement, watchdog behavior and timing. The normal set_speed pause action is the only emergency uncertainty exception: it is idempotent, never replays a tactical order and never clears an unresolved request by itself. A missing/failed pause capability remains urgent and blocks more gameplay calls.

Both automatic and manual action completion check origin, subject/semantic scope, freshness and all outcome predicates. A visual verification event must name its action_id, current session_id, live origin, original source and observed_outcome. Accepted orders remain unresolved until that evidence exists. Same-game session reconciliation is explicit; a new MCP session alone never certifies continuity or success.

Only typed hard issue deadlines cap supervised advance. Batches inspect Critical alerts and every bundle child, including coverage failures. Exact reviewed acknowledgements expire and do not cover changed risks. A finite monitor owns its lease; another cooperating process cannot reconnect or interleave calls. Process exit, timeout, a local lock, or an old screenshot never proves the game is paused.

All 113 captured capabilities have conservative default effects in api/effects.json. Discovery uses the selected catalog and never authorizes an operation. `act` may explicitly set track:false for low-impact work, retaining the request journal. New families use general verification guidance or supplied checks; no strategic family whitelist is imposed.

A manual verification may cite an original MCP observation that the agent actually inspected, or original UI evidence. Record the action, current session/origin, exact source and observed outcome. If an automatic predicate was wrong, explain that correction; never claim the predicate passed. This is an explicit agent attestation, not automatic semantic validation or permission to fabricate evidence.
