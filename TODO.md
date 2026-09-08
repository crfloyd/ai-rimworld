# Validation boundaries and future work

The enhancement plan is complete; see [PLAN.md](PLAN.md) and [VALIDATION.md](VALIDATION.md). No abandoned implementation branch or duplicate runtime remains.

Future gameplay should extend evidence where relevant: combat reaction and multi-map travel, gravship construction/victory, actual new-game/Prepare Carefully UI, and interrupted-worker recovery. These were not exercised by the five-hour recovery lab. Do not claim unattended arbitrary-threat handling or improved win rate.

Continue adding sourced mechanics as decisions demand them. Agent-selected queries, medical detail and novel fields can legitimately be large. Further speed work needs measured end-to-end loops; tiny RPC latency does not establish fast agent response. Colony work is tracked in its own STRATEGY/ISSUES/actions and immutable handoff.

## Active discovery findings — day38 lab continuation

- Native UI: Options category labels appear in get_window_ui but are absent from tabs/buttons. window_action tab=Mod options rejects (obs-0116e2aef1e1416387d4161f61906e3c). Fullscreen aligned the CUA pointer visually, but repeated clicks still did not select the category. Cause unresolved; do not claim a coordinate fix. Options closed using verified MCP OK (obs-335c148595144068aeb7a785bed4e282). Allow AI screenshots remains disabled. Future improvement should support ordinary visible category selectors, without direct settings mutation.
- Prisoner genes: list_genes uses a colonist-only resolver although prisoner Genes UI exists. Extend only to legitimately visible pawn data after checking the source and UI, not hidden information.
- Carried objects: inspected ColonistTabs.cs gear builder exposes equipment/apparel/inventory but no carryTracker. Map enumeration covers spawned things. These scopes cannot establish that an absent crafted product is destroyed. Masterwork tribalwear subsequently verified spawned in storage in obs-84d970fdad8245f38aa6d76a3db28c2a; carrying as the earlier cause is unproven.
- Absent tool-name diagnostics now direct local capability discovery; an incorrect name must not trigger unnecessary reconnect/rebind. No transport or gameplay behavior changed.
