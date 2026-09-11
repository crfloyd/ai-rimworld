# Current follow-ups

Completed work is recorded in `CHANGELOG.md` and `VALIDATION.md`; this file holds only what is
still open. Active implementation scope is in `PLAN.md`.

## Open tooling friction

Current open items, with evidence and recommended fixes, live in [friction.md](docs/friction.md).
They came from the measured 0.9.1 live playtest on `continuance`, 2026-09-11. Ranked by
measured cost:

- [ ] Report the upstream crisis time cap when it fires, name the triggering condition, and
      name `force`. Do not auto-force. Measured: 4 forced calls covered the same 48,816 ticks
      that would take about 20 capped calls.
- [ ] Let a caller ignore notification classes that cannot change a decision. One wait
      advanced 58 ticks for a dead rice plant.
- [ ] On a wait that returns `ticksWaited: 0` with `forcePaused`, name the blocking window and
      the `window_action` that clears it.
- [ ] Do not classify `truncated` as degraded when `returned` equals the caller's own `limit`.
- [ ] Run receipt annotations in the composition capture path, not only `rw_read`/`rw_act`.
- [ ] Materialize decision presets inside `rw_wait verify`, or reject them there explicitly.
- [ ] Extend the same-dialog batch exception to `set_trade`. Verified live; see friction.md.
- [ ] Correct the `trade` workflow: confirm goods with `list_things` anchored on the trader,
      not `list_unmanaged_items`.
- [ ] Stop repeating `_threatWarning` on every one-shot receipt, or persist the reference
      table across one-shot calls.
- [ ] Add `weapon` to `list_things` pawn rows, or say in the workflows that it is unavailable.
- [ ] Say why `order_pawn` returned `options: []`.
- [ ] Decide whether an unknown-thing-id error should join the recoverable class. Open
      judgement call, scoped narrowly if taken.

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
