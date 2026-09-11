# Current follow-ups

The active implementation scope is in PLAN.md; tested claims are in VALIDATION.md.

- Measure fresh-player discovery, model handovers, total context and decision quality on ordinary resumed play.
- Measure rw_capabilities lookup volume in real play; the facade defers schema cost rather than removing it, and heavy lookup would erode the surface saving. If it is heavy, consider inlining the highest-traffic signatures into rw_read's description.
- rw_observe and rw_guard are59% of the served surface; shorten those declarations before adding further public tools.
- Keep existing current-state notes reconciled; archive superseded emergencies instead of prepending competing CURRENT blocks.
- Add backend information only for a demonstrated gap in player-visible facts. Do not infer recipe eligibility, work priorities, reservation ownership or route safety from unrelated summaries.
- Measure delivery/formatting improvements separately from model/backend latency. Historical baseline results (predating the persistent transport and composition API) remain in run-local records only; the standalone experiment doc was removed as superseded.
