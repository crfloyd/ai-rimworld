# Current implementation plan — decision-loop latency

User-approved scope: reduce wall-clock latency by removing avoidable think→query→think handovers without weakening strategic reasoning or exposing the full upstream schema surface. Preserve ordinary safety, evidence, uncertainty and pause behavior.

The model still sees seven tools. Existing tools gain five complementary paths: compact domain/workflow affordance discovery, materialized decision observations, automatic event context and requested post-wait verification, explicitly independent fail-stop action batches, and connection-scoped observation reuse with conservative invalidation.

Design boundaries: event context is materialized from a post-wait status read only when the wait reports an event/risk and can be disabled; caller-selected verify reads are preflighted before time advances. Action arrays require `independent=true`, preflight every step before dispatch, stop after a reported problem and retain a durable composition until delivery. Reuse is opt-in and only returns facts current under explicit time/mutation generations; waits invalidate volatile facts and mutations conservatively invalidate all prior facts. Small values are never replaced by larger references.

Validation: offline regressions cover overview/workflow discovery, event context plus same-call verification, decision materialization, stable-versus-volatile reuse, batch preflight/fail-stop behavior, delivery markers and the existing facade safety contracts. Numbers and limits are in VALIDATION.md.

Status: implementation and documentation complete pending final repository validation and an independent live adoption test. No live game endpoint or save is used while implementing this release.
