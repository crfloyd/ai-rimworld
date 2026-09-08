# Project handoff — 0.3.1 repairs and live lab

Read AGENTS.md first. This project supports intelligent, efficient RimWorld play; fewer tokens or more ticks alone are not success.

Version 0.3.1 repairs all five findings in docs/AUDIT-2026-09-08.md and several additional real API/context defects. See docs/LAB-2026-09-08.md for measurements, exact scope and limitations; VALIDATION.md is the current evidence summary. Prior source is preserved in releases/pre-lab-0.3.0-20260908.tar.gz. No game files or saves were changed.

124 offline tests pass. Actual monitor coverage now has zero gaps; a real independent guardian confirmed pause and the monitor made zero waits under medical risks. Healthy multi-cycle autonomy and live worker/server failure remain unverified. Real-response replay: 21.4 KB new output, 64.8 KB old runner, 34.4 KB base MCP for 30 calls. The 5,000-distinct-query benchmark stays near 4 ms per ingestion; all evidence remains indexed.

Latest-by-scope facts use reference/facts.sqlite with atomic replay checkpoints. The small .projection.json is diagnostic. Originals remain in append-only journals and raw/. Action indexes rebuild independently. Medical cards, lossless list patches and lean CLI presentation reduce repeated output; retrieve is always full, and --full-output exposes full fingerprints/provenance. Monitor handback uses a packet path. Monitor/handoff resets prevent unseen delta baselines.

For this conversation, the authorized existing colony is campaigns/continuance; this is not a default for unrelated new games. Do not reinitialize or reload it. Existing user authorization covers autonomous play and support improvements. A new setup interview is unnecessary for this resume.

Continuance is paused at tick 2287413, eight colonists alive. All acute Tatyana injuries and all Swan injuries are tended; both remain recovering. Ward undrafted and sleeping. No pending actions or requests; controller ownership released after a fresh ordinary pause. Latest immutable run handoff is campaigns/continuance/handoffs/handoff-dc841c54a827454abf9ce2e465811ec3.json. Resume must inspect current controller state and live identity before advancing.

Open colony work: healing and nutrition; prisoner bed/clothing/cell/mood; low food, battery research 83%, fuel and defenses; legitimate replacement for the stolen grav engine, then gravcore/flight progression. Crawford is still downed with abasia and malnutrition; do not infer absence from map danger None. No recruitment in the lab. Next report/book checkpoint day40/tick2400000. No victory achieved.

Run-local lessons, decision/outcome evidence and lab captures are durable under campaigns/continuance/. Original operational history is reference/legacy/; measurements and scripts are reference/lab/. The illustrated History.md was preserved. The medical lesson gained actual outcome evidence and remains provisional; shared advice was not silently changed.

Future experiments: whole agent-to-game timing, meaningful false interruptions during routine recovery/sleep, pending-construction workloads and varied active-risk histories, then real worker-loss behavior under safe conditions. Preserve uncertainty and strategy rationale while measuring each change. Do not treat the runner as a reason to postpone intelligent supervised play.

## API review continuation

Full catalog/corpus/source review is in docs/api/README.md. All 113 tools have declared inputs and source handler mappings; 69 have standalone response evidence, 44 do not, and none declares outputSchema. Read docs/api/RUNNER-REVIEW.md before expanding unattended automation: compact entity views can hide unknown fields, model coverage is not reliably visible, valid list_things summary mode is misclassified partial, and 64 tools lack built-in effect classification. Explicit outcome checks already extend beyond the six convenience contracts. New findings are documented, not fixed.

Source event limits matter: damage deltas track only on-map free colonists, excluding Swan; notifications have global cursors, filters and retention limits. Preserve explicit patient checks and broader reconciliation. This review made no game calls or runner changes. The preceding colony handoff remains the latest saved evidence, not a fresh live observation. Documentation additions supersede only these pointers; the 0.3.1 installation manifest remains historical.
