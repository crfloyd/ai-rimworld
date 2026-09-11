# Current follow-ups

Completed work is recorded in `CHANGELOG.md` and `VALIDATION.md`; this file holds only what is
still open. Active implementation scope is in `PLAN.md`.

## Open tooling friction

Current open items, with evidence and recommended fixes, live in [friction.md](docs/friction.md).
They came from the measured 0.9.1 live playtest on `continuance`, 2026-09-11. Ranked by
measured cost:

- [ ] Reclassify `crisis_cap` to `info`, not `review`: `assess` blocks on anything above
      `info`, so `review` still sets `requires_review`. Land it together with decoupling event
      context from `requires_review` (`event = data.event or data._notifications`); either
      change alone is ineffective, because `_threatWarning`, `delta:pawnDamage` and
      `wait_event` also set the flag. Measured: event context runs on 47 of 52 playtest waits
      now and 35 after, removing 12 extra `get_status` reads. Verified safe: all 142 event-ish
      waits in campaign history carry `data.event` or `_notifications`. Also name `crisisCap`
      versus `wait_budget` and `force` in the `rw_wait` contract and `facade.md`. Do not infer
      a second cap field; upstream already sends one.
- [ ] On a wait that returns `ticksWaited: 0` with `forcePaused`, name the blocking window and
      the `window_action` that clears it.
- [ ] Do not classify upstream `truncated` as degraded when `data.returned == args.limit`.
      This is not our `caller_limit` marker; test the upstream shape.
- [ ] Run receipt annotations in the composition capture path, not only `rw_read`/`rw_act`.
- [ ] Materialize decision presets inside `rw_wait verify` rather than returning the raw
      status bundle. Do not reject them; `verify` exists to avoid the extra handover.
- [ ] Extend the same-dialog batch exception to `set_trade`. Live-verified; see friction.md.
- [ ] Correct the `trade` workflow: confirm goods with `list_things` anchored on the trader,
      not map-wide `list_unmanaged_items`.
- [ ] Drop `_threatWarning` from mutation receipts. Do not persist the reference table across
      one-shot CLI processes.
- [ ] Suppress wait termination on repeated notifications, then add an explicit caller
      `ignore` list. Build only after the cap work lands, as a bounded composition that
      records every internal wait and never masks a zero-tick `forcePaused`.
- [ ] Documentation only: empty hostile scan after a ThreatBig letter (4a), `get_pawn` summary
      is the read that carries `weapon` (4b), scan by `defName` not radius+limit (4c), say why
      `order_pawn` returned `options: []` (4d).

Closed, do not implement:

- [x] An unknown thing id stays blocking. A stale world model is not a size guard.

Still unverified, needs a future live run:

- [ ] Whether `trade_action cancel` after a committed deal can reverse it. Never had to be
      tested, because dismissing the message box also closed the trade dialog.
- [ ] Reproduce the slave medical bed toggle with `inspect_thing` before and after, same id,
      paused.

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
instead of 54.
