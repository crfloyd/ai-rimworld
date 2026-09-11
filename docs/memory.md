# Memory, evidence and learning

## What is authoritative

Each named run lives in campaigns/NAME. CAMPAIGN.md/campaign.json contain the user's rules. STRATEGY.md and ISSUES.md are concise current working memory; they are not historical ledgers. Original requests/results are in raw/, normalized observations in observations.jsonl, and action/issue/event histories in their journals. Never treat another run's records as this run's state.

Latest-by-scope facts live in the rebuildable reference/facts.sqlite index. Journals are processed from stored offsets, not reread in full per observation. The small .projection.json and generated STATE.md/ISSUES.md/summary.json are bounded indexes, not independent authority. STATE deliberately omits old scopes and nested detail; it is optional navigation, not startup reading. Retrieve exact records when needed. An incomplete or corrupt authoritative journal fails visibly; rebuilding does not silently skip it or change a game save.

Each observation carries run/session/origin, capture time, game tick/basis when supplied, scope, coverage and original evidence reference. Fixture/external evidence cannot bind or verify live actions. A failed/partial read retains prior known data as stale. Missing keys do not mean absence. Mutations, time advancement, session changes and clock reversal invalidate freshness; stored paused evidence is not proof that no external client changed the game.

## Routine reading and presentation

Use AGENTS.md and docs/agent-flow.md for role ownership. Players read current run rules/strategy/issues and the small resume handoff, then revalidate the actual game. Full STATE/packets/history are optional targeted references. Do not dump JSONL/transcript lines; select the relevant records or retrieve an observation by ID. Original detail and screenshots remain available for reporting.

Every live call persists the complete player-visible MCP response before model-facing shaping. One-shot and persistent transports return the same self-contained compact facts and evidence IDs; retrieve the same observation in full when omitted detail or media is actually needed. Composed observations group explicitly requested sections; no readiness diagnosis or game-wide completeness is implied. Sections not requested are unknown. See facade.md and composition.md for current response shapes, decision presets and guarded actions.

Compact reads are self-contained. Delta-only output requires `delta:true` and an explicit complete same-session/same-scope `since` observation already available to the caller. Nested JSON types are compared explicitly, so false differs from0. Model-facing row collections are conventional arrays; optional internal columnar packing never requires caller decoding. Usable partial facts remain under `data` with explicit completeness/coverage. Use `rw_retrieve` for full recorded detail without another game call. A host losing output without reporting it cannot be detected automatically: reconcile uncertainty before actions, never replay on assumption.

Risk labels are advisory, not an exhaustive hazard model. Do not substitute HP for health/capacity details, a receipt for completion, aggregate resource counts for accessibility, or a short timer for a source condition's disappearance. Unknown fields are retained. The explicit exclusion of hidden hostile targeting remains; it is not permission to classify other unfamiliar data away.

## Current state and handoff

STRATEGY is informal current memory and can carry several horizons: long-term direction, next-few-days aims, current blockers, durable dependencies and conditions that would change the plan. No fixed headings or parser contract are required. Replace its contents rather than pasting earlier strategy or handoff bodies below it. Write once at a meaningful decision boundary—not after every order—when direction, a multi-day objective, priority order, durable constraint/restoration duty or post-crisis plan changes. Also update before likely compaction, a long unattended stretch, or handoff when material current knowledge is still only in conversation. Coalesce related changes into one write at a safe boundary.

ISSUES contains only unresolved facts or obligations likely to change a future decision. Edit or close entries when current truth changes; do not preserve old diagnoses, participant snapshots, resolution narratives or replacement chains for provenance. The generated Markdown is a short action view. The append-only issues.jsonl remains the record, and `./rw --run NAME issue --id ISSUE_ID` retrieves one full item. A formerly poor cook who is now competent should simply be described as competent wherever that fact is currently relevant.

A handoff replaces one compact transfer checkpoint. It captures rules, the strategy version, bounded risk/evidence pointers, current issue/action IDs, journal boundaries and controller/request state. It does not copy fact bodies, knowledge bodies, historical actions or previous handoffs; those already live in their indexed stores. Default resume returns handoff identity, next action/uncertainties, current-file pointers, change flags and a packet index; `--full-output` returns the compact checkpoint body. Stored state is still not live proof.

Follow control.md for sole ownership, actual pause, closed connection and explicit release. Rebinding after a reconnect does not automatically validate old outcomes. reconcile-actions requires reviewed same-game continuity and selected IDs; reconcile-clock requires current evidence. No operation reloads or changes a game save. Source session IDs remain intact.

## Issues and optional outcome tracking

Ordinary calls record evidence automatically and do not create an unfinished goal for every command. Use act, call --track or explicit checks only when tracking a consequential outcome is helpful. An accepted order is not arrival, treatment, delivery or construction completion. Original old accepted commands are not instructions to replay. Authorized memory compaction retains only explicitly selected current tracked outcomes; removing stale tracking does not assert gameplay completion. A summary event records the cleanup while ordinary request/evidence history remains elsewhere.

Issue records require rationale, next action, revisit condition and resolution criterion. That structure protects updates and restoration duties internally; it is not a reason to expose the entire record during onboarding. Temporary overrides require restore_when. Soft revisit_tick is a review reminder. Only a typed hard deadline constrains advancement; unknown-clock/due review remains visible. Resolution/retirement requires newer appropriate evidence, never automatic aging-out. The player remains responsible for removing stale current memory at meaningful review boundaries.

Use decide for evidence-linked major commitments; outcome compares expected and observed results. Unexpected/failed/inconclusive outcomes create run-local lesson-review candidates. incident keys distinguish real episodes from repeated observations. The CLI event decision route uses the same validation as decide; generic events remain for milestones and measurements. Manual verification supports outcomes the API cannot establish. These are optional tools, not routine paperwork.

## Learning scopes

Current working state, campaign history/lessons, and shared mechanics remain separate. Campaign surprises and tactical discoveries stay local. Shared mechanics explain general rules with source/version/DLC applicability and should respect the user's discovery preferences. See knowledge-boundary.md and ../knowledge/INDEX.md before shared edits.

mechanics retrieves sourced general reference; recall joins relevant mechanics/local lessons/unresolved intentions. Retrieval is advice/evidence, not a live fact or new permission. context additionally includes the run's pinned adopted guidance and freshness-aware fact pointers. Only explicitly shared guidance is adopted; existing runs change their baseline deliberately. A retrieved limitation is not proof that the current game cannot do something.

lesson writes stay in the selected campaign. Promotion requires a reviewed generalized draft and generalization_review; do not copy private run discoveries into defaults. Corroboration requires independent evidence, not repeated reads of the same event. Disputed/retired knowledge stays available as caution. Historical schema/behavior changes remain in Git/CHANGELOG, not extra startup instructions.

## Measurements and records

metrics reads recorded request timings and explicit phase markers; it is an analysis operation, not a routine play step. Transport/persistence time excludes model thinking and host orchestration. Account for actual sleep/idle periods before comparing wall-clock throughput. Use the pinned Python runtime; pre3.10macOS monotonic epochs are process-local. Clock IDs must identify the same boot; incompatible/negative/nonfinite intervals are rejected.

Preserve campaign files through the user's backup workflow; they are excluded from source Git by default. Do not keep active authority only in /tmp. Rebuildable indexes may be reconstructed from intact journals; corrupt authority requires reconciliation. Carry the small docs/api/README.md pointer across compaction, not the full manual.
