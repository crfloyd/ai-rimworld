# Runner audit and approved remediation

All findings are approved for implementation. [TODO.md](../TODO.md) orders the work; [HANDOFF.md](../HANDOFF.md) records current continuation state. This is a support-code audit, not live play.

## Evidence and limits

Inspected runtime modules, instructions, templates, tests, saved schemas and responses. The 63 old tests pass on 0.2.0 but miss these defects. Reproductions used temporary campaigns and injected clients. Saved references: `/tmp/rimmolt-playthrough/tools.json` and `history.jsonl` (2,104 records). Treat these as data; never execute the old scripts or replay mutations. Regression fixtures must be minimal and deidentified.

Recorded median MCP durations: get_pawn 0.011s (284 samples), get_status 0.0115s (36), get_area 0.010s (20), waits 5.101s (247). Full model/orchestration gaps were not timestamped. These support investigating fewer round trips, not conclusively attributing the minutes of delay.

## Findings

**F01 — Lessons leak between runs.** The CLI lesson branch precedes Campaign selection. Saving with `--run alpha` writes root knowledge, immediately retrievable by beta; alpha has no lesson directory. Default learning to the run, explicitly promote reviewed advice, pin adoption so another writer cannot silently change it.

**F02 — Medical summary suppresses disease.** Saved health=100 with initial heatstroke severity 0.05 and capacities 95 survives compact output but disappears in STATE's healthy shortcut. Six saved full-health responses contain conditions. Preserve conditions, capacities, exact rates and dependencies.

**F03 — Query scopes collide.** list_things WoodLog and MedicineIndustrial share a cache key; defName, proximity, radius and other filters are omitted. Include every response-affecting argument and explicit map scope. Rebuild projections without deleting evidence.

**F04 — Freshness is inconsistent.** After session change STATE says REVALIDATE while context says false. Status tick100, health, then status tick6100 leaves health OBSERVED because only wait records advance epoch. Centralize clock/session/origin freshness and source versus ingestion time.

**F05 — Imported evidence completes live actions.** A fixture inherits current session and ingestion time, satisfies a position predicate and completes a live order. Manual verification lacks origin/semantic-scope checks too. Non-live data cannot certify live outcomes.

**F06 — Reconnect strands pending actions.** New-session evidence cannot complete or abandon an old-session action. Provide reviewed same-game reconciliation tied to fresh live binding, preserve original provenance, and never replay uncertainty.

**F07 — Delta output repeats state.** Identical saved status ingests emit 10,121 then 10,201 bytes despite changed_fields=[]; STATE reaches 10,415 bytes. Compact list_things reaches 116,741 bytes. Return changed values and full-detail pointers; keep active risk reminders and unknown coverage visible.

**F08 — Batches miss danger and over-stop.** Critical extreme-break-risk alert allows subsequent draft; dangerous/partial bundle children are unchecked. Identical known _threatWarning instead stops every batch. Central safety assessment must detect novel/worsening danger and require scoped explicit acknowledgement for understood unchanged risk.

**F09 — Stored deadlines and pause state are ignored.** Due treatment issue is ignored unless caller repeats its deadline argument. pausedAfter:false completes wait and hands back without enforcing pause. Type hard safety deadlines separately from soft reminders; unconfirmed pause is urgent uncertainty.

**F10 — Field-name validation rejects valid shapes.** get_map.colonists is numeric, get_pawn all.needs is an object, animal needs may omit thoughts. Global typing marks these partial; partial compaction then drops usable data. Validate per tool/tab and retain known subsets with explicit coverage gaps.

**F11 — No coherent run snapshot.** Resume returns paths rather than an immutable joined snapshot of rules, strategy rationale, current evidence, pending dependencies, lessons, recent decisions/outcomes and control handles. Strategy lacks evidence-linked history. Resume must load a coherent packet then revalidate.

**F12 — Learning/retrieval remains manual and broad.** Decisions, lessons and issues are disconnected; recurrence is caller counted. Context returns whole strategy, all issues and full matching lessons. Add evidence-linked expected/observed outcomes, review candidates, contradictions and distinct-incident recurrence; use focused compact retrieval.

**F13 — Persistence grows; version/timing are misleading.** Projection retains all observation IDs plus full current/prior values and rewrites per call; lookup scans journal. After 5,000 small records local median ingest grows from 1.81ms to 31.1ms, projection 1,753,903 bytes. Metrics/clientInfo still say 0.1.0. Index evidence, reduce redundant writes, instrument observable phases, use one version source.

**F14 — Manual friction and play/think gap remain.** Families are guidance only, custom predicate files abound, no bounded continuation plan exists. Saved RimMolt supports letters/messages, hostile transitions, forced pauses, _notifications, _delta/pawnDamage and crisis caps. Build finite monitoring around ordinary capabilities: expected progress continues; danger/unknown/deadline/milestone pauses for thought. One owner, explicit coverage, watchdog, pause confirmation and no tactical replay are essential. Longer blind waits are insufficient.

**F15 — Screenshot integrity and maturity claims need repair.** Screenshot metadata lacks campaign/session/map association; undeclared external images can pass chapter checks. Verify every image reference and run provenance while preserving original PNGs. Reopen disproven PLAN/VALIDATION claims. Live UI/game/performance outcomes remain pending.

## Operating model

The agent records strategy, expected outcomes, dependencies, risk limits, stop conditions and finite horizon. A deterministic monitor executes only authorized ordinary operations and pauses for anything outside that contract. Focused changes, all material risks and unresolved uncertainty return to the agent for reasoning. Combat and unstable medicine retain close supervision. Monitoring does not replace tactical judgment.

Keep full raw evidence and prose history run-local. Shared advice requires review and adoption. No arbitrary context cap may erase critical information. Measure fewer unnecessary pauses/round trips alongside hazard detection; ticks and token counts alone do not establish better play.
