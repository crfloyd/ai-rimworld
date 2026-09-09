# Current remediation plan

## Objective

Make legitimate RimWorld play more effective per real minute while retaining relevant facts, learned dependencies and continuity. The agent makes strategy; the interface supplies evidence and ordinary game actions. Victory remains the campaign goal. Faster ticks, source deletion or passing tests alone are insufficient.

## Verified position

The redundant monitor/qualification workflow is removed. Persistent ordinary MCP and automatic evidence journaling remain, with sole ownership, no uncertain replay, finite paused waits and hard deadlines. C/D and five-day E completed; detailed evidence is in docs/PLAY-LOOP-EXPERIMENT.md and campaign-local experiment records. Production stayed frozen during measured play.

E showed a fresh same-model/high player progressing about2.60times faster in ticks per minute than the parent while completing useful work. Conditions differ. Parent stalls occurred outside fast ordinary MCP calls; neither context size nor effort alone establishes the cause. Fresh context nevertheless grew beyond240k, so context efficiency is not solved. Three observer advisories did not establish additional outcome benefit. The user adopted one focused player with reporting/discussion outside its loop. AGENTS.md and docs/agent-flow.md define that default and full historian ownership; observers/strategists remain optional and bounded.

## Next bounded change

1. Integrate a thin reply collector/presentation example for the actual host. It must collect the existing response with short internal polls, preserve partial lines, media, errors and real handles, stop at the matching request and never continue gameplay or replay. Empty terminal polls in observed samples used their full effective window; do not assume long polls return early.
2. Remove outer serialization overhead while preserving exact original content. Prefer focused spatial/entity queries; do not add a strategic outcome whitelist or hide unfamiliar fields. Keep detailed evidence retrievable.
3. Test recorded complete/partial/error/large/media replies and interrupted delivery, then a short frozen live comparison. Measure response-ready-to-delivery latency, model handovers, actual context growth and useful outcomes. Do not infer token savings from character counts alone.

No broad mod rewrite, native-connection restart or new memory framework is justified now. Consult the complete API index before declaring gaps. Known critical participant roles/dependencies must survive handoffs; missing crew knowledge stays unknown until inspected, rather than forcing repeated full-roster dumps.

## Operating and acceptance rules

Only one player controls the endpoint; other agents consume saved evidence and send sparse actionable advice with freshness/conditions. The player never waits for a committee during immediate danger. User steering reaches the player explicitly. Preserve unfinished work, restoration duties, rationale and source pointers in one current campaign strategy; history stays on disk.

Separate development from measured play. Verify accepted orders by outcomes and check coverage before important decisions. Record losses and failed hypotheses honestly. Test fresh resume, uncertainty recovery and meaningful combat independently; do not claim expertise or win-rate improvement from routine construction. Stop expanding architecture when a narrow fix suffices, and continue toward the user's campaign objective.
