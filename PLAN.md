# Current implementation plan — decision-loop latency

User-approved scope: reduce wall-clock latency by removing avoidable think→query→think handovers without weakening strategic reasoning or exposing the full upstream schema surface. Preserve ordinary safety, evidence, uncertainty and pause behavior.

The model still sees seven tools. Existing tools gain five complementary paths: compact domain/workflow affordance discovery, materialized decision observations, automatic event context and requested post-wait verification, explicitly independent fail-stop action batches, and connection-scoped observation reuse with conservative invalidation.

Design boundaries: compact reads are self-contained; delta-only output requires an explicit same-scope baseline. Event context is materialized from a post-wait status read only when the wait reports an event/risk and can be disabled; caller-selected verify reads are preflighted before time advances and fully recorded. Mental-break threats include their letter, affected pawn facets and nearby responders. Action arrays require `independent=true`, preflight every step, stop after a reported problem and retain a durable composition until delivery; successful same-dialog window actions may continue past the expected dialog-open flag only. Reuse is opt-in and only returns facts current under explicit time/mutation generations. Model-facing arrays and partial data use conventional stable shapes. Semantic trade state supersedes generic dialog geometry. CLI selectors eliminate shell parsing loops and label local selection failures without implying a game failure.

Validation: offline regressions cover overview/workflow discovery, event context plus same-call verification, decision materialization, stable-versus-volatile reuse, batch preflight/fail-stop behavior, delivery markers and the existing facade safety contracts. Numbers and limits are in VALIDATION.md.

Current-memory follow-up: STRATEGY remains informal and multi-horizon, updated in one coalesced write only at meaningful boundaries. Generated ISSUES and STATE views are bounded indexes; full history remains selectively retrievable from journals and immutable evidence instead of being copied into onboarding context.

Status: implementation, documentation and248-test offline validation complete. The next independent live run can evaluate whether the smaller current memory improves onboarding and compaction recovery. No game/MCP/UI calls or save changes were used during implementation.
