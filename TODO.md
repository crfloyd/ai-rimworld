# Current follow-ups

The active implementation scope is in PLAN.md; tested claims are in VALIDATION.md.

## Approved live-friction fix batch

- [x] Make compact reads self-contained by default; require explicit `delta:true` plus same-scope `since` for delta-only output.
- [x] Keep conventional model-facing row arrays and stable caller keys/nested preset facets.
- [x] Keep usable partial/bounded facts under `data` with explicit completeness/coverage instead of switching to `known_subset`.
- [x] Surface and enrich semantic trade state through `list_trade`/`set_trade`/`trade_action` rather than generic window geometry.
- [x] Allow successful same-dialog `window_action` batches to continue when the unchanged expected `_dialogOpen` flag is their only review signal.
- [x] Strengthen mental-break/threat wait packets with letter text, robust pawn-name matching, affected health/needs/gear and nearby responder state.
- [x] Record every post-wait verification observation in the durable composition and expose requested versus actual tool/arguments for mismatch diagnosis.
- [x] Add shell-safe JSON guidance: never round-trip captured JSON through `echo`; parse once with `printf '%s'`/raw stdin.
- [x] Add a built-in CLI response selector so common paths do not require ad hoc `python3 -c` pipelines.
- [x] Distinguish per-operation game success from later local parsing/presentation failure; never imply a completed mutation/wait should be replayed.
- [x] Update replay measurement, contracts and validation claims for speed-first self-contained responses, then run the full offline suite once.

## Fresh-agent onboarding cleanup

- [x] Return controller-aware resume command templates with correct global option placement.
- [x] Keep default resume pointer-based; load archived rules/strategy/packet only with `--full-output`.
- [x] Add a valid decision-preset example and clarify that upstream pawn summary omits `tab`.
- [x] Suggest close capability names after an invalid exact lookup.
- [x] Add a general threat decision facet and resume-crisis affordance workflow.
- [x] Clarify cached session metadata versus a running stdio process and when reconnect is actually needed.
- [x] Keep STRATEGY current-only; preserve prior strategy and history in immutable handoffs/journals instead of onboarding context.

## Current-memory cleanup

- [x] Define informal, multi-horizon STRATEGY update triggers without requiring per-order writes or a parser schema.
- [x] Render ISSUES.md as concise current action cards while preserving full issue journals and exact-ID retrieval.
- [x] Bound STATE.md to evidence pointers, current risk/incomplete records, a small pawn sample and recent tracked outcomes.
- [x] Keep historical provenance in journals/handoffs rather than current startup documents.
- [ ] Replace multi-megabyte immutable handoff copies of every fact/knowledge body with integrity-checked indexes and selective retrieval; measure handoff wall time before changing the safety contract.

- Independently measure whether event packets, decision observations, action batches and cache reuse reduce model handovers and wall time in live resumed play.
- Test compact overview/workflow discovery with a fresh-context new-game planner before trusting it for a live setup.
- Measure rw_capabilities lookup volume after overview/workflow adoption; exact schemas remain deferred and heavy lookup can still erode the surface saving.
- rw_observe and rw_guard are59% of the served surface; shorten those declarations before adding further public tools.
- Keep existing current-state notes reconciled; archive superseded emergencies instead of prepending competing CURRENT blocks.
- Add backend information only for a demonstrated gap in player-visible facts. Do not infer recipe eligibility, work priorities, reservation ownership or route safety from unrelated summaries.
- Measure delivery/formatting improvements separately from model/backend latency. Historical baseline results (predating the persistent transport and composition API) remain in run-local records only; the standalone experiment doc was removed as superseded.
