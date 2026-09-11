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
- [x] Keep default resume pointer-based; load the compact checkpoint body only with `--full-output`.
- [x] Add a valid decision-preset example and clarify that upstream pawn summary omits `tab`.
- [x] Suggest close capability names after an invalid exact lookup.
- [x] Add a general threat decision facet and resume-crisis affordance workflow.
- [x] Clarify cached session metadata versus a running stdio process and when reconnect is actually needed.
- [x] Keep STRATEGY current-only; preserve evidence/history in indexed journals instead of onboarding context.

## Live friction batch two (docs/friction.md)

- [x] Continue a composition past a recoverable upstream size guard; keep every real safety stop.
- [x] Return structured narrowing advice naming both exits, filters and `confirm:true`.
- [x] Default the decision preset's world read to `kind=caravans` and add a `visitors` topic over neutral map pawns.
- [x] State in the food facet that suspended bills and loose piles are outside it.
- [x] Recognize an `order_pawn` refusal whose only option is the already-running form of the same job.
- [x] Name the trade rows upstream counted but withheld, and what an accepted deal receipt does and does not prove.
- [x] Scope event topics to the event narrative; add `context:"brief"`.
- [x] Cover every permitted catalog tool in a domain; serve a small domain index by default.
- [x] Rewrite the trade and food workflows around what live play actually missed; add `build_structure`.
- [x] Serve overview/domain/workflow from the `capabilities` CLI subcommand.
- [x] Replace argparse usage dumps with one JSON object naming the right sibling flags.
- [x] Suggest real JSON Pointers when a `--select` path is absent.
- [ ] Confirm in the next live run whether a `set_trade` batch can safely continue on an unchanged trade dialog. The trade workflow currently says not to batch them.
- [ ] Confirm in the next live run whether `trade_action cancel` after a committed deal can reverse it. No tooling text currently claims either way.
- [ ] Reproduce the slave medical bed toggle with an `inspect_thing` before and after on the same id, paused.
- [ ] Re-measure wait, discovery and composition bytes in the next live run against the recorded baseline: 304 facade calls, 926,845 bytes, wait event context 387,143 of them.

## Current-memory cleanup

- [x] Define informal, multi-horizon STRATEGY update triggers without requiring per-order writes or a parser schema.
- [x] Render ISSUES.md as concise current action cards while preserving full issue journals and exact-ID retrieval.
- [x] Bound STATE.md to evidence pointers, current risk/incomplete records, a small pawn sample and recent tracked outcomes.
- [x] Keep historical provenance in journals/handoffs rather than current startup documents.
- [x] Replace multi-megabyte immutable handoff copies with one integrity-checked compact current checkpoint and selective journal/evidence retrieval.
- [x] Add authorized action-ledger compaction that retains only selected current tracking without asserting retired gameplay outcomes.

## Resume friction found live

- [x] Route automatic wait-context pawn summary through the shared preset mapping so upstream `tab` is omitted.
- [x] Deliver a durable completed wait when optional post-wait enrichment fails locally; mark partial/no-replay instead of unknown.
- [x] Default resume guidance to one-shot CLI and reserve persistent sessions for hosts with reliable interactive stdin.
- [x] Surface a concrete controller reconciliation template for unknown compositions.

- Independently measure whether event packets, decision observations, action batches and cache reuse reduce model handovers and wall time in live resumed play.
- Test compact overview/workflow discovery with a fresh-context new-game planner before trusting it for a live setup.
- Measure rw_capabilities lookup volume after overview/workflow adoption; exact schemas remain deferred and heavy lookup can still erode the surface saving.
- rw_observe and rw_guard are59% of the served surface; shorten those declarations before adding further public tools.
- Keep existing current-state notes reconciled; archive superseded emergencies instead of prepending competing CURRENT blocks.
- Add backend information only for a demonstrated gap in player-visible facts. Do not infer recipe eligibility, work priorities, reservation ownership or route safety from unrelated summaries.
- Measure delivery/formatting improvements separately from model/backend latency. Historical baseline results (predating the persistent transport and composition API) remain in run-local records only; the standalone experiment doc was removed as superseded.
