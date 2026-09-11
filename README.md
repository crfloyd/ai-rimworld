# AI RimWorld

An information and control layer for agents playing RimWorld through ordinary RimMolt actions. The agent reasons about strategy. The layer discovers capabilities, gathers evidence, preserves uncertainty and history, retrieves sourced knowledge, and verifies explicitly defined outcomes.

Uses the repository pyenv pin in `.python-version` (Python 3.11.13), with standard-library SQLite FTS5 and an accessible RimMolt endpoint for live play. Run commands from this repository with `pyenv exec python` or `./rw`; shell commands must not silently use macOS system Python. Python 3.10+ is required for comparable monotonic clocks across processes. No external knowledge service or Python packages are required. Read [AGENTS.md](AGENTS.md), then [startup](docs/startup.md) for fresh play or an existing run.

Autonomous play uses the [live-play flow](docs/agent-flow.md): the current agent normally owns user interaction and sole game control directly, uses sparse event-driven observations while conditions are stable, and adapts to closer attention when events or uncertainty require it. Offline reporting or advice may be delegated when independently useful, but delegation is not the default play path and never competes for game control.

## Start, resume and inspect

```sh
./rw runs
./rw new NAME --spec /path/to/campaign.json
./rw resume NAME
./rw --run NAME packet --topic medicine
./rw capabilities "construction"
./rw capabilities --tool build
./rw mechanics "gravship foundation"
./rw mechanics --id gravship-foundation
./rw --run NAME recall "tending prisoner" --entity PAWN_ID
```

These commands do not query or start the game. A new campaign requires its own agreed specification; no default campaign or inherited pawn IDs. Resume returns saved evidence, not proof of live state. [Templates](templates/README.md) describe input records.

## Live work

Follow the [control contract](docs/control.md) to claim handed-off ownership, connect, inspect and bind the actual game. A session serves the small [public surface](docs/facade.md) — `rw_read`, `rw_act`, `rw_wait`, `rw_capabilities`, `rw_retrieve` and the two composed tools — over the113-tool captured catalog, which stays reachable by name. Then use ordinary `call TOOL --args JSON` requests, or the shared `rw_observe`/CLI `observe` interface for named related facts. `rw_guard`/CLI `guard` supports an explicit read/condition/one-action rule; see [composition](docs/composition.md). Use `act` when a tracked strategic outcome helps. Use `spatial --observation ID --rect MINX MAXX MINZ MAXZ` to inspect full recorded properties in a chosen area. Placement validity and line of sight still require current game information; the layer does not invent them.

Ordinary calls journal requests/evidence without creating unfinished goals or requiring intent text. Opt into tracking with `call --track --intent ...`, a check, or `act`. Any family label can be used; `outcome.checks` or `check` supplies arbitrary scoped predicates. Accepted never means completed. Keep actual unfinished work and temporary changes in current notes; all uncertain requests still block replay. Read `./rw COMMAND --help` for exact arguments.


## Evidence and knowledge

Spatial/reference rows use lossless columnar encoding only when smaller; `columns` name fields, `rows` preserve order and `absent` distinguishes missing cells from null. Sparse changes name the previous observation. `retrieve --observation ID` returns full normalized evidence; raw transport evidence remains run-local. Known hostile AI targeting is explicitly excluded from decision views under honest-play rules.

[Shared mechanics](knowledge/mechanics/README.md) are sourced JSON/prose records with version/DLC/mod cautions and revision history; a rebuildable SQLite FTS index supports targeted search. Campaign lessons remain local unless explicitly reviewed and promoted. [Memory](docs/memory.md) and [history](docs/history.md) explain continuity and the five-day illustrated book.

Campaigns, controller files, caches, credentials and generated archives are excluded from Git. Preserve campaign files through the user's backup workflow; never manipulate game saves. Git is the source-history authority. Historical audits and generated manuals are available at baseline commit 15c7708, while [the API index](docs/api/README.md) contains the active interface reference.

## Development and validation

[PLAN.md](PLAN.md) is the implementation plan, [TODO.md](TODO.md) the open work and [VALIDATION.md](VALIDATION.md) the tested claims and limits.

```sh
pyenv exec python -B tools/check.py
pyenv exec python -B tools/demo.py --output /tmp/rimworld-demo-UNIQUE
```

Both are offline. Live validation requires actual owned game control and an explicit final pause/handoff. Passing fixtures cannot establish game victory or intelligent play.

For repeated live calls, use `./rw --run NAME session --token TOKEN`: standard MCP JSON-RPC over one persistent process. See [control](docs/control.md). Full ordinary facts and evidence references are returned, without a planning framework.
