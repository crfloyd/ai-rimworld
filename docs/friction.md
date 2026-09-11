# Open tooling friction

Current open items only. The 0.9.0 live report was implemented in 0.9.1. The 0.9.1 playtest
batch except notification re-wait (item 1b) was implemented in 0.9.2; see `CHANGELOG.md`.
Item 2b remains closed.

Source of these items: a measured live playtest of 0.9.1 on `continuance`, 2026-09-11, ticks
3720001 to 3896437. The agent resumed a berserk crisis, completed a trade with a tribal bulk
goods caravan, survived a cold snap, and received a mechanoid cluster. Evidence lives in
`campaigns/continuance/observations.jsonl` and `reference/compositions/`.

---

## 1b. Every notification ends a wait, including ones that cannot change a decision

During the cold snap each frost-killed plant emitted a notification that terminated the wait.
One wait returned after **58 ticks**, one game second, for a dead rice plant. Six consecutive
waits advanced about 6,000 ticks total. After `force` removed the cap, notifications became
the new binding constraint: three of four forced waits ended on `cause: notification`, two of
them on a repeat of the same "Major break risk" alert already visible in the previous packet.

**This is the hardest remaining item and should be built last.** `wait_for_event` has no ignore
parameter, so suppression cannot be pushed upstream. The facade would have to keep waiting
internally while still returning the ignored notifications, which makes one public `rw_wait`
into a composition of several game advances. That carries real obligations:

- Bound it hard: a maximum internal iteration count and a wall-clock budget, both reported.
- Record every internal wait in the durable composition manifest, as `rw_observe` already does
  for its sub-reads, so an interrupted loop is reconcilable and never replayed.
- Stop immediately on a letter, a threat transition, a `forcePaused`, or a zero-tick advance.
  A re-wait loop must never mask a zero-tick `forcePaused`.
- Never drop a class the caller did not name. Ignored notifications are still returned in the
  packet; only wait termination is suppressed.

**Do not start with a coarse `notifications: "significant"` enum.** The taxonomy is not well
enough understood. Stage it:

1. Suppress termination on a notification identical to one already delivered in the previous
   wait packet of the same session.
2. Add an explicit caller `ignore` list of notification kinds.

**How to verify offline.** A fixture stream of repeated plant-death notifications plus one
letter must terminate once, at the letter, when the plant class is ignored, and the manifest
must list each internal wait.

Build only after a playtest of 0.9.2 shows notifications as the new ceiling. The 0.9.2 wait
changes already landed: `crisis_cap` is `info`, event context follows `data.event` or
`_notifications` only, `crisisCap` versus `wait_budget` and `force` are named, and a zero-tick
`forcePaused` wait names the pausing window.

---

## Closed, do not implement

**2b. An unknown thing id blocks a whole composition.** Leave it blocking. An unknown id means
the agent's world model is stale, which is categorically different from a size guard reporting
its own bound.

---

## Still unverified, needs a future live run

- **`trade_action cancel` after a committed deal never had to be tested.** Dismissing the
  negotiator message box with `window_action button=OK` closed the trade dialog as well, so no
  `cancel` was needed. The 0.9.0 leftover-dialog problem did not reproduce. The `deal`
  annotation's `unverified` note about cancel should stay as it is. The 0.9.2 live check also
  had no trader, so `set_trade` same-dialog batches and goods-near-the-trader were not
  exercised either.
- Mutation receipts omitting `_threatWarning`: the 0.9.2 live check never attached that block,
  so omission has no live proof. Offline fixtures already cover the shape.

---

## Confirmed on the 0.9.2 live check (`continuance`, 2026-09-11)

Ticks 3896438–3908000. Paused except supervised `rw_wait`. Not a measured playtest of colony
quality. Evidence IDs are in `VALIDATION.md`.

- Quiet `crisisCap` timeout: `crisis_cap` is `info`, no `requires_review`, no automatic event
  context; later waits with a real letter or notification still built the packet. `force` was
  not sent.
- Decision `threat` with hardcoded `limit: 20`: `matched: 54`, `returned: 20`, `truncated:
  true`, observe stayed complete.
- `rw_wait verify` with `preset: "decision"` materialized `decisions.now.core`.
- Zero-tick `forcePaused`: a bed-use `Dialog_MessageBox` was already open from changing room
  assignment; the wait named it under `pausing_window`. The wait did not create the dialog.
- Empty `order_pawn` listings inside `rw_observe` carried `empty_options`.
- Slave medical bed, same id `Bed74667`, paused: inspect showed `For slave use` with Medical
  off, then Medical on after `do_thing_action`. Restored afterward.

Nearby `category=building` + `radius` + `limit` again filled with walls (107 matches, 20
returned, Campfire182321 missed; `defName: Campfire` found it). Same failure mode as the 0.9.1
PassiveCooler miss. See the scan note below; this is not a new tooling defect.

---

## Considered, not scheduled: nearby building scans

Do not change what `list_things category=building` returns. Walls are buildings, they really
are nearer, and the receipt already reports `matched` / `returned` / `truncated`. Silently
dropping walls or doors, or inventing an "interesting buildings" order, would hide
player-visible things and would not match nearest-first.

Keep requiring `defName` (or another source filter) when the question is "is this specific
building here." Radius plus limit answers "what is immediately adjacent," which in a colony is
usually walls.

A later optional annotation, analogous to `empty_options`, could name that failure mode when
`category=building` is truncated: the nearest N of M rows are usually walls, so pass
`defName` to find one kind. Truncation metadata alone did not stop the wrong "it's not there"
conclusion twice. That annotation is a nudge, not a scan change, and is not scheduled.

---

## Confirmed working in 0.9.1, do not regress

- Recoverable coverage: a `largeOutput` section degrades and its siblings still run. Observed
  on the first live call of the session.
- `faction: neutral` pawn reads find a visiting trade caravan that world queries cannot see.
- The reordered `food_crisis` workflow: the food alert was a suspended stove bill with 186
  rice in storage, exactly as the workflow now predicts.
- `context: "brief"` waits measured 3,800 to 6,000 bytes against the recorded 16,722 median,
  with no lost decision.
- Scoped event topics: a standing threat warning no longer re-triggers the deep sweep, while a
  real "break risk" notification still escalates topics correctly.
- The `deal` annotation on an accepted trade correctly reported committed, dialog still open,
  and the right confirmation path.
- Ordinary mutation batches complete: undraft plus `set_work_priority`, and two
  `do_thing_action` deconstructs, both ran to completion.
- `rw_guard` abstains beside a degraded section.

Constraints that still apply: no new public tool, no auto-force, no silent drops, offline
fixtures built from the recorded receipts in this campaign, and the list above stays frozen.
