# AI RimWorld

Help the agent play the user's authorized run intelligently, with little operating overhead. The agent owns strategy; this project supplies evidence, ordinary MCP access and optional recall. Continue to the actual user objective. A stable colony, tooling commit or green tests is not victory.

Use `./rw` or the repository's pinned `pyenv exec python`; do not change global Python. Keep each run under `campaigns/NAME`. No developer/debug actions, hidden tactical information, balance changes or game/save manipulation. Follow the user's actual recovery rules; ordinary failure is not permission to reload.

## Roles and routing

For a request to play or continue a run, use the [live-play flow](docs/agent-flow.md). The current agent normally owns the conversation, live play, continuity and later reporting itself. Do not delegate the player role merely to isolate gameplay: measured live runs showed substantial relay and decision-cycle overhead without an established quality benefit. Repository maintenance alone does not start live play.

Delegation remains available when the agent judges that a concrete, bounded offline task can proceed independently and its benefit outweighs coordination cost—for example, a requested historical report from already-saved evidence or a difficult mechanics question that does not delay an urgent decision. Delegated agents never issue game/MCP/UI calls while the current player owns control, never overlap writers, and do not become a second gameplay authority. If a user explicitly requests a separate player, preserve the same sole-control and handoff boundaries.

The live player owns current STRATEGY/ISSUES and all immediate decisions. Reporting and tooling work normally wait for a verified pause and released or deliberately retained safe control state. Historical detail stays retrievable in campaign files rather than being repeatedly loaded into the play context.

## Enter a run — player

For a new game, use [startup](docs/startup.md), honoring the user's supplied choices and delegation. For a resume, read that run's CAMPAIGN.md, current STRATEGY.md and open ISSUES.md, plus the small `rw resume NAME` handoff/change flags. STATE, full packets, all history and maintenance plans are on-demand references. Missing knowledge remains unknown; retrieve it before decisions that need it.

Establish sole control and no pending request through [control](docs/control.md). Revalidate the actual game and identity. Reuse a valid session; unfamiliar names call for the small [API index](docs/api/README.md) and exact contracts, not a reconnect or guesses. The complete API remains discoverable. Read only the relevant reference section; parse JSONL records selectively instead of dumping raw transcript lines.

## Ordinary play

Session discovery serves a small surface: `rw_read`, `rw_act`, `rw_wait`, `rw_capabilities`, `rw_retrieve`, `rw_observe` and `rw_guard`. The full upstream catalog stays reachable by name through `rw_read`/`rw_act`. On entering a run, use the compact capability overview/domain/workflow map to see the real strategic affordances, then fetch only exact contracts genuinely needed; do not load the full one-line catalog by default. Filter at the source, keep the default compact view, and escalate with `rw_retrieve` only when compact is genuinely insufficient. See [facade](docs/facade.md) for views, selection, limits and references.

For related facts, use the local `rw_observe` tool (CLI `observe`) with named queries or selected pawn/production sections. It combines ordinary reads into one response without diagnosing readiness. Use `rw_guard` only for an already-chosen bounded read/condition/one-action rule; unknown/ambiguous data must not become an else action. See [composition](docs/composition.md) for exact examples and limitations. Individual tools remain available through the facade.

Bias toward a sparse loop: use the handoff and one focused current observation, make the strategic decision, group reviewed independent commands or safe pawn queues, then choose the longest finite event-driven wait that current evidence makes prudent. Let `rw_wait` return its default event-specific context and include preflighted `verify` reads when their results will be needed regardless of how the wait ends. After the wait, inspect only the affected facts still missing for the next decision. Use a materialized `rw_observe` decision preset for a bounded cross-domain question, and opt into cached reuse only when its conservative freshness rules fit. Do not re-read stable pawn tabs, status bundles or receipts merely for reassurance. `call TOOL --args JSON` uses ordinary MCP arguments. Requests and original evidence are journaled automatically; routine calls do not require an intention or create unfinished goals by default.

Optimize first for avoiding another model handover, then for serialized bytes. When a bounded response has a high chance of supplying the facts normally needed for the decision, prefer that sufficient conventional JSON over a smaller representation that requires decoding or predictable follow-up reads. `rw_read` is self-contained by default; request `delta:true` only with an explicit `since` observation already available in the current reasoning context. Payload budgets and explicit caller filters still bound genuinely large results; never omit risk, coverage or uncertainty to save context. When a specialized semantic tool exists—such as `list_trade` for a trade dialog—prefer it over scraping generic window controls.

When one pawn has several already-reviewed, compatible jobs, use `order_pawn` with `queue=true` to append Shift-click-style orders and let the pawn work through them before the next decision boundary. Send the immediate order normally when it should replace the current job, then append later jobs with `queue=true`; each receipt reports whether it queued and the queue length. Queueing reduces stop-and-reissue cycles, but it does not prove any job completed. Do not pre-queue combat, urgent treatment, unstable targets or dependency-sensitive steps whose later validity depends on an earlier outcome; inspect between those when strategy or safety requires it.

This is general guidance, not a call quota or a hard rule. Shorten waits and increase observation depth whenever events or uncertainty warrant it: active combat, fire, bleeding, infection/immunity races, mental breaks, food collapse, caravan transitions, expiring choices, temporary settings, ambiguous receipts, partial coverage or unfamiliar mechanics can all require close attention. Once those conditions are controlled and verified, widen the horizon again. Strategy and safety decide the cadence; neither UI responsiveness nor a desire to minimize calls overrides them.

Use `act` or `call --track --intent ...` with checks when a tracked strategic outcome is useful. Do not manually close a record for every routine command. Preserve consequential unfinished work, dependencies and temporary changes in current notes/issues; capture original settings before changing them. An accepted order is not treatment, arrival, delivery or completed construction. Verify the actual result.

Use `rw_wait` for supervised time; it injects `pause=always`. Choose a horizon appropriate to the situation, inspect the real event and pausedAfter result, and retain/poll the actual process handle. Never replay an uncertain operation or assume a timeout cancelled it. Ownership, uncertainty and pause checks apply even to untracked calls. During a wait, short offline retrieval/conditional planning is useful; concurrent game calls are not.

Preserve unfamiliar fields, coverage limits, current threats and unresolved risks. Partial, stale, absent and known-empty are different. Classification is advisory evidence, not a substitute for reading the actual condition. A wait ending before its wall budget may have reached its game-time limit.

Use the persistent `session` transport in [control](docs/control.md) for repeated play calls. It uses ordinary MCP messages and forwards full facts; it does not choose strategy. Do not recreate the removed monitor, qualification or acknowledgement workflow. Backlog nonblocking tooling findings and separate development from measured play.

For one-shot CLI output, use built-in `--select` JSON Pointers instead of `python3 -c` pipelines. If capture is unavoidable, parse once with raw `printf '%s'`; never pass JSON through shell `echo`, which can turn escaped control sequences into invalid JSON. Keep game-operation success separate from later local selection, formatting or presentation failure, and never replay a completed mutation/wait to repair a local parser.

## Continuity and learning

Keep a concise current strategy with urgent risks, unfinished jobs, restoration duties, rationale and exact evidence pointers. Preserve known participant roles, role-specific needs and critical-worker dependencies; a roster or HP summary is not complete coverage. Record unknowns rather than assuming them away. Replace superseded orders; retain their history on disk. Before compaction or handoff, preserve current context and any pending handle, then verify pause before releasing control. Carry the API index pointer and only relevant interface uncertainties, not the full manual.

Use `mechanics`, `recall` and [knowledge](knowledge/INDEX.md) when the decision would benefit. Campaign surprises and tactical lessons stay local; shared mechanics explain general rules. Read [memory](docs/memory.md) for memory changes and [knowledge boundary](docs/knowledge-boundary.md) before shared edits. A retrieved lesson is evidence/advice, not a live fact or permission.

At requested checkpoints, capture original, well-framed screenshots when safe and preserve evidence pointers, outcomes and future aims. Normally write and validate the complete narrative/report after a safe pause by following [history](docs/history.md). A separately delegated historian is optional for a requested independent report from saved evidence; it never makes live game calls or delays urgent play. Late or missed captures are explicitly dated. Never invent progress or documentary images.

## Tool maintenance

Only when doing development, read PLAN.md and VALIDATION.md. Keep production frozen during measured trials. Measure actual handover latency, useful outcomes and context growth; context size or reasoning effort alone is not an established cause of slow responses. Prefer removing demonstrated friction; each added mechanism must justify its cost in play or continuity. Tests verify behaviors, not expertise, speed or win rate. Scope checks to the change and report what the evidence actually supports.
