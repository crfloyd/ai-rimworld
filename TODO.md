# Audit remediation — active implementation

The user approved every finding in [the audit](docs/AUDIT.md). This is the current checklist; earlier PLAN.md checkmarks describe the original release, not proof these defects are resolved. Work on the runner only. Do not contact the live game during this side conversation.

## Ordered phases and acceptance

- [x] **A — Protect campaign memory and evidence.** Default lessons to the selected run; explicitly review shared promotion; pin adopted shared advice. Validate campaign paths. Reject non-live evidence for live orders. Reconcile actions across a verified same-game reconnect without replay. Test two-run isolation and fabricated completion. (F01, F05, F06)
- [x] **B — Correct observation identity, coverage and freshness.** Full semantic query scope; per-tool/tab schemas; source versus ingestion time; one freshness policy. Preserve conditions at 100% health, exact medical values, partial known subsets, warnings and bundle uncertainties. Test saved-response shapes, clock/session changes and filter collisions. (F02–F05, F10)
- [x] **C — Make context selective and incremental.** True deltas, compact decision cards and risk summaries with raw pointers, focused lessons/issues. Preserve urgent risks and dependencies. Indexed evidence retrieval and measured cache/journal growth. (F07, F12, F13)
- [x] **D — Coherent resume and learning loops.** Immutable run handoffs join rules, strategy/rationale, evidence versions, unresolved work/dependencies, lessons, decisions/outcomes and controller uncertainty. Link incident→decision→outcome→lesson; track recurrence from distinct incidents. Resume never implies freshness or success. (F06, F11, F12)
- [x] **E — Danger handling and action ergonomics.** Inspect bundle children and Critical alerts; distinguish novel/worsening danger from explicitly acknowledged unchanged risk. Derive hard deadlines separately from soft reminders. Reusable outcome contracts; unknown on insufficient evidence. Fail closed on missing coverage. (F08–F10, F14)
- [x] **F — Bounded monitored continuation.** One controller, durable finite plan, expected routine progress only. Stop on danger/unknown/verification failure/milestone/review/watchdog expiry. Confirm pause before handback, including pausedAfter:false; never replay uncertain mutations. Use reviewed ordinary capabilities. Offline watchdog and continuation tests. (F08, F09, F14)
- [x] **G — Measurement and integration.** Single version source; automatic observable phase timings and output sizes; truthful unavailable model timing; scenario danger tests and large-history measurement. Strengthen screenshot/run association. Update commands/templates/startup/claims/handoff. Preserve prior tooling, never game saves. (F13–F15)

For each phase: add regressions, implement, run appropriate offline checks, record evidence, install after source-hash preflight, update HANDOFF.md. Do not infer live readiness or improved win rate from fixtures.

## Field validation — pending separate authorized control handoff

- [ ] Actual RimMolt pause/event behavior, process loss and mod overrides.
- [ ] New run/resume, live identity, critical outcomes, DLC/map changes, native screenshots, real five-day prose chapter.
- [ ] Comparable end-to-end play/think/pause/reaction timing and decision quality. Historical logs lack full agent-gap timestamps.

## Evidence

Release 0.3.0: 111 offline tests pass, including regressions for all reproduced audit failures and finite-monitor/guardian scenarios. The synthetic walkthrough and 5,000-observation benchmark complete. See VALIDATION.md for the exact scope, source digest and pending field checks. Runtime changes remain support-only; no game, save, mod, existing campaign or controller was accessed during this implementation.

Audit baseline: 0.2.0, 63 passing old offline tests, defects reproduced in AUDIT.md. No game calls or game/save/mod changes. Implemented in the runner after staged verification and source-hash preflight; prior 0.2.0 support code is preserved in releases/.

## Independent audit follow-up — 8 September

A01–A05 in docs/AUDIT-2026-09-08.md have implementation/regression fixes in 0.3.1. The original audit is preserved. Live catalog comparison additionally exposed bleedRatePerDay, status damage deltas and excessive presentation overhead; those paths now have fixes. Live colony testing and before/after measurements are underway; do not equate offline passes with successful monitored play.

### 0.3.1 live-lab result

- [x] A01–A05 repaired and independently regressed.
- [x] Real catalog, zero-fire shape, draft receipt, bleeding and status-damage integration fixes.
- [x] Lean output, full retrieval, lossless list patches and unseen-baseline reset.
- [x] Actual medical outcome verification, run-local lesson update, real guardian stop and zero-gap coverage.
- [x] Durable lab evidence and immutable Continuance handoff.
- [ ] Healthy multi-cycle, live worker/server loss, combat reaction and whole agent-loop comparisons. See docs/LAB-2026-09-08.md; these remain unproven.

## Full API review — 8 September (new findings; not implemented)

See [API review](docs/api/README.md) and [runner findings](docs/api/RUNNER-REVIEW.md). The inventory covers 113 tools; source mappings are complete, runtime response coverage is explicitly partial. Prior repaired findings remain repaired, but these new gaps are unresolved.

- [ ] Preserve novel top-level and per-entity fields in compact views; distinguish model coverage from readable JSON.
- [ ] Correct list_things summary shape coverage without confusing aggregates with spatial safety evidence.
- [ ] Review currently unclassified strategic capabilities by actual effects and run permissions.
- [ ] Extend consequential intent/outcome and goal-aware change routing beyond convenience templates.
- [ ] Test open-ended novelty, strategic opportunities, prisoner/off-map coverage and source event gaps alongside timing/output metrics.

Documentation review only: no game calls and no runner behavior changes.
