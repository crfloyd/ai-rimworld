# Memory, evidence and learning

## What is authoritative

Each named run lives in campaigns/NAME. CAMPAIGN.md/campaign.json contain the user's rules; STRATEGY.md contains current decisions, rationale, unresolved dependencies and restoration duties. Original requests/results are in raw/, normalized observations in observations.jsonl, and action/issue/event histories in their journals. Never treat another run's records as this run's state.

Latest-by-scope facts live in the rebuildable reference/facts.sqlite index. Journals are processed from stored offsets, not reread in full per observation. The small .projection.json and generated STATE.md/ISSUES.md/summary.json are views, not independent authority. An incomplete or corrupt authoritative journal fails visibly; rebuilding does not silently skip it or change a game save.

Each observation carries run/session/origin, capture time, game tick/basis when supplied, scope, coverage and original evidence reference. Fixture/external evidence cannot bind or verify live actions. A failed/partial read retains prior known data as stale. Missing keys do not mean absence. Mutations, time advancement, session changes and clock reversal invalidate freshness; stored paused evidence is not proof that no external client changed the game.

## Routine reading and presentation

Use AGENTS.md and docs/agent-flow.md for role ownership. Players read current run rules/strategy/issues and the small resume handoff, then revalidate the actual game. Full STATE/packets/history are optional targeted references. Do not dump JSONL/transcript lines; select the relevant records or retrieve an observation by ID. Original detail and screenshots remain available for reporting.

The persistent session forwards full player-visible ordinary MCP facts/media with evidence references. Composed observations group explicitly requested sections; no readiness diagnosis or game-wide completeness is implied. Sections not requested are unknown. See composition.md for read presets and guarded actions.

The single-call CLI presentation can return deltas against named previous observations. First reads after session change/reconciliation/handoff reset are complete. Nested JSON types are compared explicitly, so false differs from0. Row replacements/updates retain identity and exact missing-field meaning. Spatial packing is lossless columnar encoding only when smaller. If a baseline is not available in context, retrieve it; use --full-output or retrieve for full recorded details. A host losing output without reporting it cannot be detected automatically: reconcile uncertainty before actions, never replay on assumption.

Risk labels are advisory, not an exhaustive hazard model. Do not substitute HP for health/capacity details, a receipt for completion, aggregate resource counts for accessibility, or a short timer for a source condition's disappearance. Unknown fields are retained. The explicit exclusion of hidden hostile targeting remains; it is not permission to classify other unfamiliar data away.

## Current state and handoff

STRATEGY is one current account. Replace superseded orders while preserving their historical evidence; do not accumulate contradictory CURRENT/emergency overrides. Keep known participant roles, dependencies, pending request/actual process handle, exact temporary settings and restoration conditions. A player owns current-state edits; the historian owns reports. Capture current state before compaction or transfer without an arbitrary summary limit that forces important facts out.

handoff captures rules, strategy, evidence pointers, issues, optional tracked outcomes, local lessons, journal boundaries and controller/request state, including an unfinished composition and handle. Snapshots are immutable. resume shows the saved handoff and changed-since-snapshot flags without loading a save or starting time. The default is a small strategy/change/index view; --full-output exposes the full packet.

Follow control.md for sole ownership, actual pause, closed connection and explicit release. Rebinding after a reconnect does not automatically validate old outcomes. reconcile-actions requires reviewed same-game continuity and selected IDs; reconcile-clock requires current evidence. No operation reloads or changes a game save. Source session IDs remain intact.

## Issues and optional outcome tracking

Ordinary calls record evidence automatically and do not create an unfinished goal for every command. Use act, call --track or explicit checks only when tracking a consequential outcome is helpful. An accepted order is not arrival, treatment, delivery or construction completion. Original old accepted commands are not instructions to replay.

Issue records require rationale, next action, revisit condition and resolution criterion. Temporary overrides require restore_when. Soft revisit_tick is a review reminder. Only a typed hard deadline constrains advancement; unknown-clock/due review remains visible. Resolution/retirement requires newer appropriate evidence, never automatic aging-out. The retire command keeps originals retrievable and a new observation returns the subject to active views.

Use decide for evidence-linked major commitments; outcome compares expected and observed results. Unexpected/failed/inconclusive outcomes create run-local lesson-review candidates. incident keys distinguish real episodes from repeated observations. The CLI event decision route uses the same validation as decide; generic events remain for milestones and measurements. Manual verification supports outcomes the API cannot establish. These are optional tools, not routine paperwork.

## Learning scopes

Current working state, campaign history/lessons, and shared mechanics remain separate. Campaign surprises and tactical discoveries stay local. Shared mechanics explain general rules with source/version/DLC applicability and should respect the user's discovery preferences. See knowledge-boundary.md and ../knowledge/INDEX.md before shared edits.

mechanics retrieves sourced general reference; recall joins relevant mechanics/local lessons/unresolved intentions. Retrieval is advice/evidence, not a live fact or new permission. context additionally includes the run's pinned adopted guidance and freshness-aware fact pointers. Only explicitly shared guidance is adopted; existing runs change their baseline deliberately. A retrieved limitation is not proof that the current game cannot do something.

lesson writes stay in the selected campaign. Promotion requires a reviewed generalized draft and generalization_review; do not copy private run discoveries into defaults. Corroboration requires independent evidence, not repeated reads of the same event. Disputed/retired knowledge stays available as caution. Historical schema/behavior changes remain in Git/CHANGELOG, not extra startup instructions.

## Measurements and records

metrics reads recorded request timings and explicit phase markers; it is an analysis operation, not a routine play step. Transport/persistence time excludes model thinking and host orchestration. Account for actual sleep/idle periods before comparing wall-clock throughput. Use the pinned Python runtime; pre3.10macOS monotonic epochs are process-local. Clock IDs must identify the same boot; incompatible/negative/nonfinite intervals are rejected.

Preserve campaign files through the user's backup workflow; they are excluded from source Git by default. Do not keep active authority only in /tmp. Rebuildable indexes may be reconstructed from intact journals; corrupt authority requires reconciliation. Root HANDOFF.md is tooling status/routing only, never campaign instructions. Carry the small docs/api/README.md pointer across compaction, not the full manual.
