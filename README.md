# AI RimWorld

An information and control layer for agents playing RimWorld through ordinary RimMolt actions. The agent reasons about strategy. The layer discovers capabilities, gathers evidence, preserves uncertainty and history, retrieves sourced knowledge, and verifies explicitly defined outcomes.

Requires Python 3 with standard-library SQLite FTS5 and an accessible RimMolt endpoint for live play. No external knowledge service or Python packages are required. Read [AGENTS.md](AGENTS.md), then [startup](docs/startup.md) for fresh play or an existing run.

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

Follow the [control contract](docs/control.md) to claim handed-off ownership, connect, inspect and bind the actual game. Then use `observe` for explicit read packets and `act` for intended gameplay changes. Use `spatial --observation ID --rect MINX MAXX MINZ MAXZ` to inspect full recorded properties in a chosen area. Placement validity and line of sight still require current game information; the layer does not invent them.

Mutations create intention records by default. Any family label can be used; `outcome.checks` or `check` supplies arbitrary scoped predicates. Accepted never means completed. An explicit `track:false` in act is available for low-impact changes; the request remains journaled. Read `./rw COMMAND --help` for exact arguments.

[Finite observation plans](docs/runner-loop.md) execute agent-selected reads and bounded waits with an independent pause guardian. Essential coverage refreshes every cycle; supplementary queries may specify `every_cycles`. Additional `watch_patients` require their own health/needs coverage. New or unreviewed response structure returns control. Combat and unstable medicine remain supervised.

## Evidence and knowledge

Spatial/reference rows use lossless columnar encoding only when smaller; `columns` name fields, `rows` preserve order and `absent` distinguishes missing cells from null. Sparse changes name the previous observation. `retrieve --observation ID` returns full normalized evidence; raw transport evidence remains run-local. Known hostile AI targeting is explicitly excluded from decision views under honest-play rules.

[Shared mechanics](knowledge/mechanics/README.md) are sourced JSON/prose records with version/DLC/mod cautions and revision history; a rebuildable SQLite FTS index supports targeted search. Campaign lessons remain local unless explicitly reviewed and promoted. [Memory](docs/memory.md) and [history](docs/history.md) explain continuity and the five-day illustrated book.

Campaigns, controller files, caches, credentials and generated archives are excluded from Git. Preserve campaign files through the user's backup workflow; never manipulate game saves. Git is the source-history authority. Historical audits and generated manuals are available at baseline commit 15c7708, while [the API index](docs/api/README.md) contains the active interface reference.

## Development and validation

[PLAN.md](PLAN.md) is the implementation plan, [HANDOFF.md](HANDOFF.md) the current continuation state, [TODO.md](TODO.md) the open work and [VALIDATION.md](VALIDATION.md) the tested claims and limits.

```sh
python3 -B tools/check.py
python3 -B tools/demo.py --output /tmp/rimworld-demo-UNIQUE
```

Both are offline. Live validation requires actual owned game control and an explicit final pause/handoff. Passing fixtures cannot establish game victory or intelligent play.
