# Tooling handoff and routing

This root owns reusable tooling status only. It does not select a campaign, grant game control, carry pawn identities/orders, or supersede any campaign strategy. For an authorized run use `rw runs`, `rw resume NAME`, and its rules, state, STRATEGY.md, issues and immutable handoff. Follow docs/control.md before game contact. Store run-specific operational handoffs and discoveries only under that campaign.

Current work: independently reproduced review findings in session baseline reuse and nested scalar type comparison. 154 tests pass for fixes: full first response after session change; reset presentation after uncertain delivery; recursive type-aware equality for full deltas and positional patches. Root operational notes moved into their originating campaign with original evidence preserved.

Committed baseline5f57573 includes reviewed High-vs-Critical alert handling (148 tests). Earlier20232f2 introduced row field patches; its byte reduction was not proof of faster decisions. See VALIDATION.md and TODO.md for tested boundaries. The scoped regressions pass; do not claim universal losslessness or faster gameplay.

Next: commit the review fixes, then prioritize end-to-end measurements of review-to-unpause and event-to-response under stated conditions over further compression. Separate RPC/persistence time, intentional game advancement, host execution overhead and inter-call time; unknown components remain unknown. Existing telemetry includes raw/context bytes and call gaps, but cannot isolate model reasoning or server event-arrival latency. Retain all unfamiliar fields and pending outcomes.
