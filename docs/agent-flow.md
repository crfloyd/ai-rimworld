# Live play flow

Use one current agent for the user conversation, live game control, continuity and immediate strategy. This is the default because measured facade trials completed comparable one-day windows with far fewer decision cycles and less wall time when the acting agent received results directly. That evidence supports a bias, not a universal claim about model quality or every game situation.

## Ownership and phases

Only one agent or process may issue game/MCP/UI calls. It owns current `STRATEGY.md` and `ISSUES.md`, the persistent session and every immediate decision until it verifies pause, closes or safely preserves the session, saves a handoff and releases control. Stored handoff evidence is not live proof; revalidate ownership, identity and pause on entry.

The same agent normally proceeds through these phases sequentially:

1. Read the run rules, current strategy/issues and small resume handoff.
2. Claim sole control, reuse or establish one session, inspect and bind the actual game.
3. Play with the adaptive loop below.
4. At a stop or checkpoint, verify pause and pending-operation state before continuity or report work.
5. Replace the compact current transfer checkpoint, close the session and release control when play is ending.

Do not mix implementation work into measured or active play. Do not let reporting, screenshots or advisory work delay an urgent game decision.

## Adaptive sparse loop

Start from the handoff instead of rebuilding the whole colony model. Obtain one focused live observation sufficient to validate current risks. Make the decision, group already-reviewed independent commands or pawn job queues where safe, then use one finite `rw_wait` with the longest horizon justified by current evidence. Use its event context and preflighted post-wait verification to avoid a second model handover when those facts are predictably needed. Inspect only the affected facts still missing for the next choice.

Treat stable information as stable until time advancement, a relevant mutation, an event or an explicit coverage limitation can invalidate it. Exact mutation receipts do not automatically require a broad verification sweep; verify consequential outcomes at the scope and time where they can actually have changed. Prefer a small explicit `rw_observe` over a broad preset when only a few related facts matter.

Use pawn job queues when a reviewed sequence can safely run without another decision between steps. An immediate `order_pawn` replaces the current job; subsequent calls with `queue=true` append Shift-click-style jobs after it and after any existing queue. This is useful for known hauling, cleaning, repair, construction or movement sequences and can remove repeated wait/order handovers. The queue receipt is not completion evidence. Do not pre-commit tactical combat, urgent medicine, changing targets or any later order whose correctness depends on the outcome of an earlier one.

This is not a fixed cadence. The player decides how much attention the situation needs. Use shorter waits, narrower deadlines and deeper reads for combat, fire, bleeding, infection/immunity races, acute mood or food problems, caravan formation/arrival, expiring dialogs or quests, restoration duties, ambiguous receipts, partial data and unfamiliar mechanics. It is reasonable to take several sequential reads before a high-consequence decision when no single response supplies enough evidence. When danger and uncertainty subside, return to longer waits and fewer observations.

Do not create extra calls merely to make the UI appear active, issue routine status commentary, or prove again that an unchanged fact remains unchanged. Conversely, never suppress a necessary read or rush a decision merely to improve call counts or wall-time metrics.

Use the conversation for transient tactics and STRATEGY/ISSUES for facts that must survive compaction. At meaningful decision boundaries, coalesce any material current-memory changes into one ordinary Markdown replacement. Preserve multiple planning horizons, but do not write routine commands or progress reports and do not append historical state. If the current plan remains accurate, make no file write.

## User steering

Because the current agent is the player, apply user steering directly at the next safe boundary. A stop request takes priority: resolve the actual pending operation or wait handle, verify pause, preserve continuity and release control. Status questions should be answered from the latest reliable evidence without manufacturing another game read unless the requested fact is genuinely unknown or stale.

## Optional delegation

Delegate only a concrete, bounded task that can proceed without live game authority and whose expected value exceeds the context and relay overhead. Examples include a requested historical report from completed evidence, a difficult mechanics lookup, or independent analysis of a recorded decision. Advisers and historians remain offline while a player owns the endpoint unless their work uses only saved evidence and cannot interfere with current writers.

Never delegate a separate player merely because play is long-running or because a coordinator wants to remain chat-responsive. If the user explicitly requests a separate player, transfer only after verified pause, terminal pending requests, updated strategy/issues, a saved handoff, connection closure and release. The incoming player revalidates identity and outcomes; no timeout-based takeover.

## Reporting

The current agent normally captures important scenes when safe and assembles requested reports after a verified pause. A historian may be delegated from saved evidence when the user requests independent reporting or the report can proceed without blocking play. The historian makes no game/UI calls, does not rewrite current strategy/issues, checks every claim and image date, and follows [history](history.md). Missing captures remain explicitly missing; never invent documentary images.
