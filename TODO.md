# Current follow-ups

Completed work is recorded in `CHANGELOG.md` and `VALIDATION.md`; this file holds only what is
still open. Active implementation scope is in `PLAN.md`.

## Open tooling friction

Current open items, with evidence and recommended fixes, live in [friction.md](docs/friction.md).
Items 5a-5g came out of the 2026-09-12 siege post-mortem on `continuance` and were revised
after an independent review corrected the first draft. All seven are now implemented and
covered by `tests/test_siege_postmortem.py`; `friction.md` records where each fix deviates from
the recommendation as filed. Two pieces stay open and are upstream or unresolved: the alert
list still names no siege and attributes no fire cause, and a telemetry query for a key the
file lacks still returns zero rows rather than raising.
They came from the measured 0.9.1 live playtest on `continuance`, 2026-09-11. The 0.9.2 batch
landed 1a, 1c, 2a, 3a–3c, `set_trade` same-dialog batches, trade confirmation near the trader,
and documentation 4a–4d.

Still open:

- [ ] Suppress wait termination on repeated notifications, then add an explicit caller
      `ignore` list. Build only after a playtest shows notifications as the new ceiling, as a
      bounded composition that records every internal wait and never masks a zero-tick
      `forcePaused`.

Closed, do not implement:

- [x] An unknown thing id stays blocking. A stale world model is not a size guard.

Still unverified, needs a future live run:

- [ ] Whether `trade_action cancel` after a committed deal can reverse it. Never had to be
      tested, because dismissing the message box also closed the trade dialog. No trader was
      present on the 0.9.2 live check, so `set_trade` batches and goods-near-the-trader were
      also not exercised.
- [ ] Mutation receipts omitting `_threatWarning`: that block was not attached on the 0.9.2
      live check.

Closed from the 0.9.2 live check:

- [x] Slave medical bed toggle with `inspect_thing` before and after, same id `Bed74667`,
      paused. Medical turned on while the bed stayed `For slave use`, then restored.

Nearby `category=building` + radius + limit filling with walls is the same 0.9.1 PassiveCooler
failure mode, reproduced on Campfire. Keep requiring `defName` for a specific building; do
not change the scan. An optional truncated-building annotation is considered, not scheduled.

## Standing measurement notes

- Measure delivery and formatting improvements separately from model and backend latency.
- Tests verify behaviors, not expertise, speed or win rate. Scope checks to the change and
  report what the evidence actually supports.
- `rw_observe` and `rw_guard` are a large share of the served surface; shorten those
  declarations before adding further public tools.
- Add backend information only for a demonstrated gap in player-visible facts. Do not infer
  recipe eligibility, work priorities, reservation ownership or route safety from unrelated
  summaries.

## Baseline for the next measured run

From `campaigns/continuance/telemetry.jsonl`, the 0.9.0 session: 304 facade calls and 926,845
model-facing bytes, of which `rw_wait` was 416,195 and its automatic event context 387,143
across 36 waits. Neither the 32,768-byte payload backstop, the 32-query composition cap nor the
16-action batch cap fired once.

From the 0.9.1 playtest: `context:"brief"` waits measured 3,800 to 6,000 bytes; the capability
overview index is 2,009 bytes against 12,008 for the 0.9.0 tool map, covering 112 tools
instead of 54. Event context ran on 47 of 52 waits; the 0.9.2 event-context rule would have
run on 35 of those (12 extra `get_status` reads removed). That remaining 35 is why item 1b
is the next wait-loop lever.
