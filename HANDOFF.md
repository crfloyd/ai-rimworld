# Current tooling handoff

0.7.0 is deployed after the prior player verified pause, closed its connection and released control. It exposes rw_observe and rw_guard through persistent-session discovery and the shared CLI engine. Existing ordinary tools and player/coordinator/historian ownership remain.

198 offline tests pass. Revision-bound review found no unresolved critical issue; the final total-read-budget correction is regression-tested. A fresh offline agent discovered both interfaces through normal guidance and expressed the two supplied tasks correctly. Live read-only checks verified tools/list discovery, a status+two-pawn-tab composition, CLI composition, unchanged game tick and clean delivery/closure. No live guarded mutation was tested.

Twelve saved compatible paired reads use one composed MCP request rather than two individual requests, with0.8%larger input-plus-content-text bytes and4.2%larger wire bytes. Ordinary reads could already be batched into one host exchange; this is not measured model-handover/token/speed improvement. Actual fresh-player adoption and decision quality remain to evaluate.

Removed duplicate CLI observation execution, inert UI preparation command, stale monitor/P8 tasks and accumulated presentation-history instructions. Current implementation scope is in PLAN.md; API examples/limits in docs/composition.md; evidence limits in VALIDATION.md. Campaign facts and pending combat remain in the selected run, not shared guidance.
