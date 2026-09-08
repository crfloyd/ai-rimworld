# Reasoning, bounded execution and interruption

The agent owns strategy. The runner can execute a finite period of **routine** progress without calling the model after every quiet wait. Combat, unstable medicine, recruitment, travel decisions and victory commitments still need deliberate reasoning. A monitor does not decide tactics or silently change priorities.

## Start with one focused packet

Use `rw --run NAME packet --topic TOPIC` for current risks, uncertainty, pending work, deadlines, checkpoint status, unresolved decisions and relevant reference pointers. Use `observe --queries JSON --token TOKEN` to perform a bounded set of ordinary reads in one agent exchange. It prevalidates all queries and never advances time. Reads can pause/change UI; the controller must own the game.

`act --json JSON --token TOKEN` accepts an intent, ordinary tool/arguments and an optional outcome contract. It avoids a separate temporary predicate file. For example, after verifying actual IDs and map coordinates:

```json
{
  "tool": "order_pawn",
  "args": {"id": "ACTUAL_PAWN", "command": "ACTUAL_SUPPORTED_COMMAND"},
  "intent": "Reach the inspected refuge",
  "outcome": {"family": "movement", "pawn": "ACTUAL_PAWN", "mapIndex": 0, "x": 10, "z": 20}
}
```

The example command is deliberately not a guessed RimMolt order. Discover supported actions first. Movement, equipped/worn items, finished buildings and extinguished fires have reusable contracts. Rescue also requires fresh refuge hazard checks. Treatment requires a reviewed timestamp field and a newer tend time; a version lacking those fields stays unknown and needs scoped visual evidence. Combat has no universal completion shortcut. Missing fields never satisfy a contract. Every component of a compound contract must be fresh, from the right run/session/origin, and later than the accepted order.

## Qualify the live session once

Before automatic continuation, establish ownership, connect, inspect and bind the correct loaded game. Perform a small supervised `advance` and a normal `pause`. Both must actually report paused. Then use:

```sh
python3 rw --run NAME monitor-ready --token TOKEN --wait-evidence WAIT_OBS --pause-evidence PAUSE_OBS --review 'Explain the reviewed finite-wait and pause behavior, current mod settings, and remaining failure limits'
```

This records an empirical qualification for the current session and catalog. It is not a proof of all server/mod behavior. A reconnect or catalog change invalidates it. The stored RimMolt catalog shows `set_speed {"action":"pause"}` as an ordinary pause action; unpause is reserved for monitored waits. A mod setting may override a wait's pause request, so `pausedAfter` is always checked.

## Define and run a finite plan

Use [the plan template](../templates/continuation.json), fill it from current observations, then `plan --json JSON`. The command saves an immutable named plan under the selected run. It does not advance time. Run it with `continue --plan PLAN_ID --token TOKEN`.

A plan records the purpose, rationale, expected progress, reconsideration conditions, watched pawn IDs/maps, observation queries, safety predicates, milestones, allowed resource/building changes, and finite wall/game/cycle budgets. There is no implicit default colony, roster, or winning strategy.

Every cycle requires fresh status, alerts and complete roster; health and needs for each watched colonist; and fire/visible-pawn coverage on each watched map. Status bundles can provide alerts/roster without extra calls. Threat queries must be complete, unfiltered map pawn lists with explicit hostility. If this RimMolt version cannot supply that coverage, continuation stops; narrow supervised action remains available. The monitor never treats an omitted list as empty.

Routine continuation currently allows at most 20 waits, ten wall-clock minutes and six game hours per plan, with each wait bounded to 5–40 wall seconds and at most one game hour. These are finite execution safety envelopes, not context truncation limits. Known hard deadlines further shorten the next wait. The agent should choose smaller budgets when the situation warrants them. No force/crisis-cap override is used automatically.

The runner continues only expected progress. It stops for:

- New or unacknowledged risks, Critical/unknown signals, pawn damage, dialogs, identity/roster/map changes, or incomplete/stale coverage.
- Unknown/blocked/interrupted requests or unfinished treatment, rescue or combat; any explicitly critical open issue.
- Hard deadlines, due review reminders, five-day history checkpoints, false/unknown continuation predicates, or reached/unknown milestone predicates.
- Resource/building changes not explicitly covered by the plan, changed weather, zero tick progress, guardian loss, or any finite budget ending.

Actual tutorial notifications with kind=learning remain recorded as informational. Other unknown notifications stay reviewable. This avoids stopping merely to read a tutorial hint while preserving unfamiliar events.

A plan can execute only once. Review its result and create another plan; an interrupted plan is never replayed to repeat orders. The monitor itself performs reads and waits, not new tactical mutations.

## Acknowledged risks

`acknowledge --ids ... --evidence ... --review ... --expires-tick ...` records exact, current, scoped risk fingerprints for a finite period. Batches can continue through the identical reviewed risk. Changed content, another session, expiry, missing coverage, partial application and protocol uncertainty do not inherit acknowledgement. Global server warnings have global/map identity rather than the actor issuing the next order.

Automatic routine continuation still stops for Critical/unknown risks even when acknowledged. An acknowledgement is not a claim that a threat is resolved or permission for unattended combat. A soft issue reminder stays visible; a typed `deadline: {"kind":"hard","tick":...,"reason":...}` constrains supervised advance too. Do not label every economic reminder a hard medical deadline.

## Independent pause guardian and process handles

The continuation process owns a lease and all ordinary game requests. A separate process watches that lease and the worker heartbeat. Its sole gameplay action is an idempotent normal pause on expiry or worker loss. Calls remain serialized through the controller lock. It cannot make strategic decisions, start waits, retry an order, or take over the colony.

The monitor confirms pause before returning, even when the model has not responded. A wait reporting pausedAfter=false invokes the ordinary pause safeguard and still stops for review. If the server is unreachable, a request is unresolved, or another process holds the RPC lock, **a client cannot guarantee that the game is paused**. The guardian records that uncertainty; the original pending request and its handle remain. A paused response alone does not prove a prior wait terminated. Inspect the original process/server evidence before reconciliation. Never replay the uncertain order.

If the host returns an execution/session handle while `continue` is running, retain that actual handle and optionally attach it:

```sh
python3 rw --run NAME controller handle --request PLAN_ID --handle-kind exec --handle-value ACTUAL_HANDLE
```

`controller inspect`, run packets and handoffs expose it. Poll the existing handle rather than launching another loop. No cooperating process may reconnect, release ownership, or interleave gameplay calls while the monitor owns the lease. Unrelated clients and human UI input are outside this filesystem lock, so a real control handoff is still required.

Use monitor-stop --token TOKEN --basis NOTE to request an orderly stop, then poll the existing process. If both the worker and guardian were lost, first reconcile any original server request from terminal evidence, confirm an ordinary pause, and use monitor-reconcile with that fresh evidence, a review, and --worker-terminal. A live/unknown PID or unresolved request prevents lease reconciliation. No plan is replayed.

## Measure without confusing speed with quality

Each successful control call records RPC time, local persistence/processing time, total measured call time, serialized input/output sizes, and the gap since the preceding call. The gap combines reasoning, orchestration, user/idle time and local work; it does not isolate model thinking. Monitor cycles, stop reasons and pause attempts are durable events. `metrics` reports available components and explicitly marks unavailable timing.

Use `tools/benchmark.py` for an isolated synthetic persistence/output benchmark. Use a real authorized campaign later to measure event response, false interruptions, strategic mistakes and useful progress. More game ticks or fewer tokens alone do not establish better play.

## 0.3.1 live integration notes

Use lowercase pawn with verbose:true for explicit hostility. A successful fire scan with an explicit integer fireCount=0 is known-empty even when fires is omitted; unknown or positive-count responses without rows still fail coverage. A monitor stop returns stop details and a packet_path to its stored complete snapshot, rather than repeatedly emitting that snapshot. All queries after a monitor/handoff get a fresh presentation baseline on their next read. The Continuance lab established real zero-gap stop behavior, not healthy autonomous progress or failure recovery; see LAB-2026-09-08.md.
