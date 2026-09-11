# Current follow-ups

The active implementation scope is in PLAN.md; tested claims are in VALIDATION.md.

- Independently measure whether event packets, decision observations, action batches and cache reuse reduce model handovers and wall time in live resumed play.
- Test compact overview/workflow discovery with a fresh-context new-game planner before trusting it for a live setup.
- Measure rw_capabilities lookup volume after overview/workflow adoption; exact schemas remain deferred and heavy lookup can still erode the surface saving.
- rw_observe and rw_guard are59% of the served surface; shorten those declarations before adding further public tools.
- Keep existing current-state notes reconciled; archive superseded emergencies instead of prepending competing CURRENT blocks.
- Add backend information only for a demonstrated gap in player-visible facts. Do not infer recipe eligibility, work priorities, reservation ownership or route safety from unrelated summaries.
- Measure delivery/formatting improvements separately from model/backend latency. Historical baseline results (predating the persistent transport and composition API) remain in run-local records only; the standalone experiment doc was removed as superseded.
