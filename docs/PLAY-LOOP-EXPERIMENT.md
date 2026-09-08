# Fresh-agent play-loop experiment — 2026-09-08

Two fresh agents used the same inherited model/settings in sequential live intervals. A used the project workflow at revision a247fef; B used direct RimMolt MCP without the project wrapper, memory, ledger, monitor or compressed presentation. Production was frozen for both. Each targeted two game days or20active minutes; neither reached the two-day target. Consequences stood, with no save reloads, debug or game/mod/config edits.

| Measure | A: project workflow | B: direct MCP |
|---|---:|---:|
| Measured active interval |20m18s|19m53s|
| Game hours advanced |25.69|28.78|
| Gameplay MCP calls |160|122|
| Wait calls |19|16|
| Time inside wait RPCs |195.46s|247.62s|
| Other RPC time |2.60s|2.46s|
| Raw gameplay response bytes |311,977|201,088|
| Explicit MCP errors |2|5|

A's interval excludes82reported seconds for checkpoint storytelling/capture. Its final confirmation ran slightly beyond the nominal cap without more game ticks. B's two host-review rejections remain included. B also fetched137,567startup MCP bytes; A used cached discovery whose offline fetched volume was not measured. These byte figures are not actual model context or tokens. Additional local/UI/host failures occurred and are not included in the MCP-error row.

B advanced12% more ticks, used24% fewer gameplay calls, and fetched36% fewer gameplay response bytes. Time-normalized throughput was about14% higher. These are descriptive results, not an isolated effect of removing tooling: B inherited a concise curated handoff and a later recovery state, while random conditions, food shortages and medical complications differed. Both still spent most wall time outside game RPCs; that includes useful reasoning as well as avoidable work.

Independent evidence audits confirmed survival/recovery in A and procurement, construction and bed-restoration outcomes in B. Both ended with food and mood risks unresolved. B's new medical complication remained substantially impairing despite a high health percentage. No new hostile encounter tested combat quality. The results do not establish better win rate or prove the project unnecessary.

The project has not demonstrated a benefit sufficient to justify mandatory bulk-state/history loading or per-command goal bookkeeping. Preserve durable original evidence, run isolation, targeted recall, actual outcome checks, temporary-change continuity, finite waits, real pause confirmation and no uncertain replay. B retained several of these behaviors manually; it did not test compaction or interrupted-worker recovery.

## Resulting simplification

Normal startup reads rules, current strategy and open issues; full STATE/packets/history stay available on demand. Ordinary calls/batches journal requests automatically without requiring intent text or creating unfinished goals by default. Explicit tracked outcomes/checks remain available. The upstream pawnDamage field can contain healing/drug effects; annotations now distinguish an observed HP decline, new conditions needing review, and unfamiliar shapes requiring attention. No response fields are removed by this classification.

180offline tests pass under the0.5.0 default-contract change, including ordinary CLI execution, explicit/check-implied tracking, untracked uncertainty blocking replay and health-change fidelity. These tests do not prove faster play with the new defaults; a subsequent live check and fresh-agent crossover remain separate evidence.

## Traceability and remaining work

Detailed original records, participant reports, independent audits and comparison.json remain run-local under the selected campaign's reference/experiments/. Trial B's passive HTTP records are archived in its trial-b-direct/ directory. They were not replayed or silently passed off as project-generated live observations. This shared report contains tooling conclusions only; campaign-specific discoveries remain with that run.

The early-stop popup investigation found that wall and game-time limits both return cause=timeout. Recent no-event stops reached the selected one-game-hour limit before the40second wall budget. RPC duration is not exact visible unpaused time. Event-to-next-call timings of a few milliseconds were chained reads, not measured model comprehension or reaction.

Next: use the simpler ordinary path and compare matched situations/crossovers before further mechanisms. Native MCP deployment/host-review overhead, actual context consumption, long-run continuity and combat remain unisolated. Do not interpret green tests, smaller output, or this one pair as expert-play validation.
