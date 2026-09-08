# AI RimWorld

Help the agent play the user's authorized run intelligently, with little operating overhead. The agent owns strategy; this project supplies evidence, ordinary MCP access and optional recall. Continue to the actual user objective. A stable colony, tooling commit or green tests is not victory.

Use `./rw` or the repository's pinned `pyenv exec python`; do not change global Python. Keep each run under `campaigns/NAME`. No developer/debug actions, hidden tactical information, balance changes or game/save manipulation. Follow the user's actual recovery rules; ordinary failure is not permission to reload.

## Enter a run

For a new game, use [startup](docs/startup.md), extracting the user's supplied choices and delegation before asking anything. For a resume, read that run's **CAMPAIGN.md, current STRATEGY.md and open ISSUES.md**, plus the small `rw resume NAME` handoff/change flags. Do not preload STATE.md, full packets, all history, maintenance plans or every mechanics topic. They remain available for targeted retrieval. Missing details remain unknown; retrieve them before decisions that need them.

Before live calls, establish actual sole control and no pending request through [control](docs/control.md). Side agents stay offline until handed control. Revalidate the real game; stored state is not live. Do not reconnect merely to rediscover an unfamiliar name. Read the small [API index](docs/api/README.md), then use `capabilities TOPIC` or an exact tool contract as needed. The complete API remains discoverable; search matches and historical schemas are not a whitelist.

## Ordinary play

Use a focused observation, make the strategic decision, group reviewed ordinary commands where safe, then one finite event-driven wait and the outcome reads needed next. `call TOOL --args JSON` uses ordinary MCP arguments. Requests and original evidence are journaled automatically; routine calls do not require an intention or create unfinished goals by default.

Use `act` or `call --track --intent ...` with checks when a tracked strategic outcome is useful. Do not manually close a record for every routine command. Preserve consequential unfinished work, dependencies and temporary changes in current notes/issues; capture original settings before changing them. An accepted order is not treatment, arrival, delivery or completed construction. Verify the actual result.

Use ordinary `wait_for_event` with `pause=always` for supervised time. Choose a horizon appropriate to the situation, inspect the real event and pausedAfter result, and retain/poll the actual process handle. Never replay an uncertain operation or assume a timeout cancelled it. Ownership, uncertainty and pause checks apply even to untracked calls. During a wait, short offline retrieval/conditional planning is useful; concurrent game calls are not.

Preserve unfamiliar fields, coverage limits, current threats and unresolved risks. Partial, stale, absent and known-empty are different. Classification is advisory evidence, not a substitute for reading the actual condition. A wait ending before its wall budget may have reached its game-time limit.

Use the persistent `session` transport in [control](docs/control.md) for repeated play calls. It uses ordinary MCP messages and forwards full facts; it does not choose strategy. Do not recreate the removed monitor, qualification or acknowledgement workflow. Backlog nonblocking tooling findings and separate development from measured play.

## Continuity and learning

Keep a concise current strategy with urgent risks, unfinished jobs, restoration duties, rationale and exact evidence pointers. Replace superseded orders; retain their history on disk. Before compaction or handoff, preserve current context and any pending handle, then verify pause before releasing control. Carry the API index pointer and only relevant interface uncertainties, not the full manual.

Use `mechanics`, `recall` and [knowledge](knowledge/INDEX.md) when the decision would benefit. Campaign surprises and tactical lessons stay local; shared mechanics explain general rules. Read [memory](docs/memory.md) for memory changes and [knowledge boundary](docs/knowledge-boundary.md) before shared edits. A retrieved lesson is evidence/advice, not a live fact or permission.

At the user's checkpoints, follow [history](docs/history.md): a prose colony story with original well-framed screenshots, plus the operational report and future aims. Preserve detailed history without making routine play load it all. Never invent progress or documentary images.

## Tool maintenance

Only when doing development, read PLAN.md, HANDOFF.md and VALIDATION.md. Keep production frozen during measured trials. Prefer removing demonstrated friction; each added mechanism must justify its cost in play or continuity. Tests verify behaviors, not expertise, speed or win rate. Scope checks to the change and report what the evidence actually supports.
