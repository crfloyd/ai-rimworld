# Validation boundaries and future work

The enhancement plan is complete; see [PLAN.md](PLAN.md) and [VALIDATION.md](VALIDATION.md). No abandoned implementation branch or duplicate runtime remains.

Future gameplay should extend evidence where relevant: combat reaction and multi-map travel, gravship construction/victory, actual new-game/Prepare Carefully UI, and interrupted-worker recovery. These were not exercised by the five-hour recovery lab. Do not claim unattended arbitrary-threat handling or improved win rate.

Continue adding sourced mechanics as decisions demand them. Agent-selected queries, medical detail and novel fields can legitimately be large. Further speed work needs measured end-to-end loops; tiny RPC latency does not establish fast agent response. Colony work is tracked in its own STRATEGY/ISSUES/actions and immutable handoff.

## Active discovery findings

- Options category selectors appear only as labels in get_window_ui, absent from actionable tabs/buttons. Normal UI click delivery remains unqualified on the test host. Add generic visible-control support only after reproducing the mechanism; do not directly change settings as a workaround.
- list_genes uses a colonist-only resolver although a prisoner Genes UI can exist. Any expansion must preserve ordinary player visibility.
- Gear inspection exposes equipment/apparel/inventory but not held carry-tracker objects; map enumeration covers spawned objects. Their absence cannot establish destruction. Capture scope explicitly and consider a visible held-object observation.
- Unknown tool-name guidance now directs local discovery, not unnecessary reconnect.
- Named UI High/Medium/Low alerts require explicit review; Critical and unknown remain blockers. No strategy label whitelist. Finite-monitor live qualification remains pending.
- Independent review confirmed session-baseline reuse and nested bool/number equality defects. Fixes and154 regression tests pass. Root handoff now routes campaign-local play state without containing it.
- Next performance work: measure full loops and event-to-response, separating intentional game time from RPC/persistence, host orchestration and agent review. Smaller output alone is not a speed result.

Active P8 in PLAN.md supersedes the earlier statement that the enhancement work is complete. Verified concerns: approximately191KB generated startup state,70 open general actions without automatic checks, no demonstrated successful finite-monitor cycle in this campaign, and slow supervised combat. Prioritize startup navigation and action lifecycle, then measured composed play loops. The exact risk-reference presentation fix is committed, but has not solved end-to-end speed.

A/B trials and independent audits are complete (docs/PLAY-LOOP-EXPERIMENT.md).0.5.0 removes mandatory bulk-state preload and default per-call goal bookkeeping, and corrects HP-increase critical labels. The ordinary path passed a bounded live functional check; next prioritize useful gameplay/continuity measurement rather than more infrastructure. Do not claim exact context-token savings or model reaction latency from wire bytes/chained-read timing. Host review and native MCP deployment remain separate unisolated factors.
