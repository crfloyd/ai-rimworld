# Validation —0.4.0

145 offline tests pass, covering lossless unknown-field handling, partial/summary variants, null/missing distinctions, all113 capabilities, spatial selection, mechanics search/rebuild/applicability, free-form intentions, patient coverage, structure lineage and persistence. Synthetic new-run/resume workflow passes. Fresh-clone evidence is recorded in [VALIDATION-0.4.0.json](docs/VALIDATION-0.4.0.json).

The [0.4.0 live lab](docs/LAB-0.4.0.md) advanced five supervised game hours with real orders and outcome reads. All five waits returned pausedAfter=true. The game ended paused at2299925, ownership released, and an immutable campaign handoff saved. No game files/mods, saves, difficulty or balance were altered; no reload or debug action occurred.

Same30-call replay:29,059 candidate bytes versus34,426 raw MCP bytes. The old21,410-byte view omitted pawn details and is not equivalent. Live60-call telemetry:115,225 candidate bytes versus160,410 raw bytes. These are bytes, not model tokens; some lab outputs were agent-selected views. Neither comparison establishes improved decision quality, win rate or end-to-end speed. Median live RPC8.13ms and persistence8.24ms exclude permission review, reasoning and host delays.

Actual new-game UI, combat/raid reaction, gravship launch/victory, multi-cycle unattended play and worker-death recovery were not tested in this lab. The earlier [0.3.1 lab](docs/LAB-2026-09-08.md) remains separate historical evidence. Output-shape observations are not exhaustive formal schemas. Six sourced mechanics records need expansion and contextual judgment.

## Independent-review corrections

154 offline tests pass after reproducing and fixing cross-session unseen baselines and nested numeric/boolean equality. New tests cover first bundled observations, reconnect, post-ingest delivery failure without replay, type-changing nested row patches and row identity, and presentation-version transitions. Shared root handoff now contains tooling routing only; campaign orders and discoveries were preserved in their originating campaign and immutable handoff. This is scoped regression evidence, not proof that every possible response shape is lossless.

A subsequent discovery sample of50 live calls contained46 non-wait RPCs totaling0.393seconds and50 persistence phases totaling0.660seconds. Four waits spent40.315seconds intentionally advancing the game. Most wall time was outside RPC/persistence. Inter-call time mixes reasoning, tooling edits, UI attempts, host orchestration and idle time, so this does not isolate the cause or establish faster routine play. Detailed request-linked measurements remain with the test campaign. Next: measure a routine-only interval and observed-event response before further compression changes.
