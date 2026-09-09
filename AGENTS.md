# AI RimWorld

Help the agent play the user's authorized run intelligently, with little operating overhead. The agent owns strategy; this project supplies evidence, ordinary MCP access and optional recall. Continue to the actual user objective. A stable colony, tooling commit or green tests is not victory.

Use `./rw` or the repository's pinned `pyenv exec python`; do not change global Python. Keep each run under `campaigns/NAME`. No developer/debug actions, hidden tactical information, balance changes or game/save manipulation. Follow the user's actual recovery rules; ordinary failure is not permission to reload.

## Roles and routing

For a request to play or continue a run, use the [coordinated flow](docs/agent-flow.md): the main agent coordinates the user conversation and delegates live play to one focused player, with a historian handling requested reports. This is explicit authorization to use subagents for those roles where supported. Keep the same responsive player running; do not replace it for each user question or checkpoint. Observers and strategists are optional, bounded advisers. Repository maintenance alone does not start a player.

An agent already assigned player, historian or adviser executes that role directly; it must not recursively create another player. Only the player may issue game/MCP/UI calls. The coordinator relays user steering and reads saved progress. If delegation is unavailable or the user requests single-agent play, use the same boundaries sequentially and defer report assembly until a safe pause.

The coordinator reads docs/agent-flow.md once and dispatches a concise task with the run, objective, current files and control handoff, using a fresh context rather than inheriting the whole conversation. The player owns current STRATEGY/ISSUES; the historian owns History/reports/screenshot registration; the coordinator owns shared tooling guidance and Git integration. No overlapping writers. Historical detail stays retrievable in campaign files.

## Enter a run — player

For a new game, use [startup](docs/startup.md), honoring the user's supplied choices and delegation. For a resume, read that run's CAMPAIGN.md, current STRATEGY.md and open ISSUES.md, plus the small `rw resume NAME` handoff/change flags. STATE, full packets, all history and maintenance plans are on-demand references. Missing knowledge remains unknown; retrieve it before decisions that need it.

Establish sole control and no pending request through [control](docs/control.md). Revalidate the actual game and identity. Reuse a valid session; unfamiliar names call for the small [API index](docs/api/README.md) and exact contracts, not a reconnect or guesses. The complete API remains discoverable. Read only the relevant reference section; parse JSONL records selectively instead of dumping raw transcript lines.

## Ordinary play

Use a focused observation, make the strategic decision, group reviewed ordinary commands where safe, then one finite event-driven wait and the outcome reads needed next. `call TOOL --args JSON` uses ordinary MCP arguments. Requests and original evidence are journaled automatically; routine calls do not require an intention or create unfinished goals by default.

Use `act` or `call --track --intent ...` with checks when a tracked strategic outcome is useful. Do not manually close a record for every routine command. Preserve consequential unfinished work, dependencies and temporary changes in current notes/issues; capture original settings before changing them. An accepted order is not treatment, arrival, delivery or completed construction. Verify the actual result.

Use ordinary `wait_for_event` with `pause=always` for supervised time. Choose a horizon appropriate to the situation, inspect the real event and pausedAfter result, and retain/poll the actual process handle. Never replay an uncertain operation or assume a timeout cancelled it. Ownership, uncertainty and pause checks apply even to untracked calls. During a wait, short offline retrieval/conditional planning is useful; concurrent game calls are not.

Preserve unfamiliar fields, coverage limits, current threats and unresolved risks. Partial, stale, absent and known-empty are different. Classification is advisory evidence, not a substitute for reading the actual condition. A wait ending before its wall budget may have reached its game-time limit.

Use the persistent `session` transport in [control](docs/control.md) for repeated play calls. It uses ordinary MCP messages and forwards full facts; it does not choose strategy. Do not recreate the removed monitor, qualification or acknowledgement workflow. Backlog nonblocking tooling findings and separate development from measured play.

## Continuity and learning

Keep a concise current strategy with urgent risks, unfinished jobs, restoration duties, rationale and exact evidence pointers. Preserve known participant roles, role-specific needs and critical-worker dependencies; a roster or HP summary is not complete coverage. Record unknowns rather than assuming them away. Replace superseded orders; retain their history on disk. Before compaction or handoff, preserve current context and any pending handle, then verify pause before releasing control. Carry the API index pointer and only relevant interface uncertainties, not the full manual.

Use `mechanics`, `recall` and [knowledge](knowledge/INDEX.md) when the decision would benefit. Campaign surprises and tactical lessons stay local; shared mechanics explain general rules. Read [memory](docs/memory.md) for memory changes and [knowledge boundary](docs/knowledge-boundary.md) before shared edits. A retrieved lesson is evidence/advice, not a live fact or permission.

At requested checkpoints, the player captures original, well-framed screenshots and sends evidence pointers, outcomes and future aims to the historian, then resumes authorized play. The historian follows [history](docs/history.md) to write and validate the complete narrative/report. Reporting does not block urgent play; late or missed captures are explicitly dated. Never invent progress or documentary images.

## Tool maintenance

Only when doing development, read PLAN.md, HANDOFF.md and VALIDATION.md. Keep production frozen during measured trials. Measure actual handover latency, useful outcomes and context growth; context size or reasoning effort alone is not an established cause of slow responses. Prefer removing demonstrated friction; each added mechanism must justify its cost in play or continuity. Tests verify behaviors, not expertise, speed or win rate. Scope checks to the change and report what the evidence actually supports.
