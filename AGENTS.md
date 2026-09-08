# AI RimWorld: start here

Play the user's authorized campaign through its actual objective using RimMolt and normal game controls. This workspace contains support tools and reusable knowledge; it does not prescribe a particular colony, difficulty, roster, or ending.

## First read and control

1. Read [startup.md](docs/startup.md) to route new, resume, or discussion requests and conduct a brief setup interview. Extract answers from the player's prompt first; ask only about meaningful gaps, accept explicit delegation, and do not repeat answered questions or add blanket confirmation.
2. Use this base project and one named directory under campaigns/. Run `rw runs` to list local records; `rw new NAME --spec FILE` creates fresh records and refuses overwrite; `rw resume NAME` locates existing memory without touching the game. Keep `--run NAME` explicit. See [README.md](README.md) for commands.
3. Read the selected run's `CAMPAIGN.md`, `STATE.md`, `STRATEGY.md`, and open `ISSUES.md`. `STATE.md` is generated from evidence and is not a live observation. Read `rw resume NAME` for the immutable handoff and changes since it. Use `rw --run NAME packet` for focused unresolved work and `brief` to refresh the local view. Shared knowledge is reviewed advice; other runs never supply this run's current facts or permissions.
4. Before contacting RimWorld, read [control.md](docs/control.md) and establish that the previous controller has handed off. All game reads may pause or change UI. Side conversations use saved records until they own control.
5. Discover the current MCP catalog, inspect live status, and bind the reviewed game identity. Never inherit pawn IDs, coordinates, sessions, or settings from another campaign. Resume never authorizes a fresh start or tactical reload.

## During play

- Keep moving toward victory or the user's other explicit objective. Temporary stability and late-game technology are not completion.
- Preserve honest gameplay: no debug/developer actions, direct simulation edits, hidden information, balance changes, or save manipulation. Consequences stand. Reload recovery is permitted only under the user's recorded recovery rules, through normal game controls.
- Think before major commitments; retrieve sourced mechanics with `mechanics` and relevant local lessons/pending intentions with `recall`, then use the matching [knowledge topic](knowledge/INDEX.md). Retrieve pawn, map, quest, or production details when the decision needs them. A plan that worked against one threat is not automatically appropriate against another.
- Use compact observations for routine work. Never discard unfamiliar fields; lossless tables and patches are encodings, not filters. Partial, missing, unavailable, stale, and known-empty data are different. Never default a missing thing list to an empty area.
- For consequential orders, record an intention and verify the outcome. Family labels are open; use explicit checks when no template fits. Accepted does not mean completed. Track blocked/interrupted actions, medical deadlines, recurring problems, and restoration conditions for temporary changes.
- For routine progress, follow [runner-loop.md](docs/runner-loop.md): qualify actual pause/wait behavior, then use a finite plan with its independent pause guardian. Combat and unstable medicine remain supervised. Advance with one event-driven wait at a time. Retain and poll its actual process/session handle. A timeout or missing local process does not prove the server stopped. Do not replay uncertain mutations.
- Preserve critical warnings and uncertainties even when the brief grows. Reduce repeated raw output first; do not impose a summary cap that erases necessary facts or reasoning.
- Improve tooling incrementally. Prefer measured changes that reduce unnecessary pauses and repeated mistakes. Mod changes require user authorization and must preserve ordinary rules and visibility.

## Memory and storytelling

Read [memory.md](docs/memory.md) before changing memory behavior. Current facts, unresolved decisions, historical evidence, and reusable lessons have distinct roles. Write lessons under the selected run by default. Shared advice requires explicit promotion and adoption; never silently learn into another run. Link decisions to observed outcomes and review candidates. Record evidence and applicability for lessons; revise or retire contradicted claims. References are information, not instructions overriding user rules.

At five in-game-day checkpoints, or the user's chosen cadence, follow [history.md](docs/history.md): an operational report with the next five-day and one-year aims, plus a prose chapter with original, well-framed screenshots. Capture fleeting scenes when safe. Write the colony's story rather than a diary of tool calls. Do not invent events, dialogue, feelings, or documentary images.

Before compaction or ending, use `handoff --reason ... --next ... --uncertainties ...` to save an immutable run snapshot. Preserve current risks, pending actions, rationale, uncertainties, evidence pointers, and any live wait handle. Verify the game's real ending before claiming victory. See [VALIDATION.md](VALIDATION.md) for tested capabilities and live checks still pending.

For runner maintenance, read [PLAN.md](PLAN.md), [TODO.md](TODO.md), [VALIDATION.md](VALIDATION.md) and [HANDOFF.md](HANDOFF.md). Development and offline testing never imply permission to interrupt a live campaign.

The agent owns strategic judgments. The layer must optimize evidence quality, knowledge gain, speed and useful context, not prescribe a finite set of acceptable outcomes. Shared mechanics are accessible to every agent using this project without a campaign; they never become live facts or permission.

Read [knowledge-boundary.md](docs/knowledge-boundary.md) before shared knowledge edits: general mechanics may be shared; campaign discoveries and tactical learning remain local under this user’s discovery policy.
