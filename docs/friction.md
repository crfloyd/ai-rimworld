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

# Siege post-mortem findings, 2026-09-12

Source: measured live play on `continuance`, ticks 4636041 to 4707956. A Psyck Crew siege
arrived at tick 4665000, built two steel mortars at (15,92) and (15,96), and shelled Haven.
Fires burned through the sealed compound, interior air reached 147 C, and six of nine
colonists died of burns and heatstroke. Evidence is in
`campaigns/continuance/observations.jsonl`.

**Revised 2026-09-12 after an independent review.** The first version of these items blamed
the threat summaries for failing to report the siege. That was wrong, and checking it produced
better items. The wait response carried the mortar construction and `_threatWarning` did fire.
The defects below are the ones that survive verification. Items 5a and 5c as originally filed
were withdrawn; their numbers are reused here for the corrected findings.

**Implemented 2026-09-12.** All seven are fixed with offline regressions in
`tests/test_siege_postmortem.py`, which fail without the fix. Two deviate from the
recommendation as written and say so below: 5a cannot gate on faction, and 5b is served by the
event packet rather than by an alert. 5c uses `room_graph`, not a per-room threshold sweep.

## 5a. Hostile construction is excluded from risk classification

**Fixed, with one deviation.** Building deltas are classified again, but not by faction: the
delta rows carry only `count`, `def` and `label`, with no faction field anywhere, so the
recommended gate cannot be implemented from this payload. Def class is the discriminator
instead. Artillery classes in `newBuildings` raise `critical`, in `removedBuildings` `review`,
and ordinary construction raises nothing, which keeps the offline check's second half (a
player wall does none of those) while failing its first half by a different route. The second
half of the defect is fixed as recommended: artillery in a delta now counts as an event, so a
plain `cause: timeout` wait that reports one builds a packet and adds the `threat` topic.

`safety.py` classifies `_delta` keys and skips four of them:

```python
if key not in ('newItems', 'removedItems', 'newBuildings', 'removedBuildings'):
```

At 13:21:15 a wait returned `_delta.newBuildings` containing
`{"count": 2, "def": "Turret_Mortar", "label": "mortar"}` alongside 26 barricades. A besieging
faction finishing two mortars is exactly a review-worthy event, and the exclusion meant it
produced no risk card, no `requires_review`, and nothing that would stop a batch.

The exclusion is defensible for `newItems`: a colonist hauling rice should not raise a risk.
It is not defensible for buildings belonging to a hostile faction.

The defect has a second half. That same wait ended on `cause: timeout` with no notifications,
and the documented rule is that the post-wait event packet is built only when a wait reports
`data.event` or `_notifications`. Telemetry confirms it: that row is `event_context: false` at
656 bytes, against 3,200 to 9,988 bytes on neighbouring rows. So a besieging faction completing
two mortars produced neither a risk card nor an event packet.

**Recommended fix, both halves.** Classify `newBuildings` and `removedBuildings` when the
building's faction is hostile, at `review` severity, or at `critical` for artillery and turret
classes. Leave player-faction construction unclassified. Separately, count a hostile-faction
building appearing in a delta as an event for context purposes, so the wait that reports it
also returns a packet.

**How to verify offline.** A fixture delta with a hostile `Turret_Mortar` in `newBuildings`
must produce a risk card, set `requires_review`, and build an event packet even when the wait
ended on a plain timeout; the same delta with a player-faction wall must do none of those.

## 5b. No alert names an artillery siege

**Fixed in the packet, not in the alert list.** The alert list is upstream and this repo cannot
add to it. The threat facet instead carries an `artillery` term: hostile indirect-fire
buildings with count, faction and position, present whenever the threat topic is active and
keyed on existence rather than distance. It reports its own truncation, so an empty term under
a truncated scan is not read as an absence. Shell-attributed fire causes remain upstream.

During active shelling the alert list held Low food, Low medicine, Tattered apparel, Extreme
break risk, Fire!, Medical treatment needed, Heatstroke, Colonist left unburied, an unfilled
ideoligion role, Colonist needs rescue and Need doctor. Nothing named the siege, the mortars,
or incoming shells. "Fire!" carried no cause, so repeated shell-started fires presented as a
single ordinary fire that firefighters were losing.

This is lower priority than 5a because the information was available in the wait delta. It
still matters for an agent that resumes mid-siege and reads alerts rather than deltas.

**Recommended fix.** Surface a standing alert while a hostile artillery building exists on the
map. Where a fire's cause is a shell impact, say so on the fire alert.

## 5c. Interior temperature is not in any default read

**Fixed for fire events, via `room_graph` rather than an alerts-facet sweep.** A fire packet
now carries `fires.enclosure`: the hottest non-outdoors room, with cell, role, cell count,
whether it can reach the map edge, and a `lethal` flag at 50 C, plus a note that a downed pawn
cannot be rescued into an unsafe temperature. One bounded call covers the whole base, which is
why this is not a per-room threshold sweep. The node key is undocumented upstream, so the
reader accepts `rooms` or `nodes` and reports unknown rather than safe when neither fits.

Six colonists died of heatstroke in a 147 C room. `get_status` and its bundle carry no
temperature field at all, and `get_conditions` reports outdoor temperature, which stayed
between 11 and 25 C for the whole event. The variable that killed the colony was reachable
only through `get_room` at a guessed coordinate, and was in fact read once, after everyone was
already down.

**Recommended fix.** Add a maximum enclosed-room temperature term to the alerts facet, naming
the room, whenever any player-owned room exceeds a habitability threshold.

**How to verify offline.** A fixture map with one enclosed room above 50 C must produce that
term while outdoor temperature stays temperate.

## 5d. `force` suppresses `crisisCap` and leaves no trace

**Fixed, both halves.** The first forced wait of a session must pass `force_reason`, which is
journalled as an `advance_review` event. Every forced wait returns `forced.basis`, the threat
signature it was justified against, and says that an absent `crisisCap` means force suppressed
it. When the signature changes by hostile kind, artillery class or distance band, the next
forced wait is refused once and names the change; passing force again re-affirms.

Two related defects.

`safety.py` adds a `crisis_cap` info signal from `d.get('crisisCap')`, but passing `force`
suppresses the `crisisCap` field, so the signal cannot fire on precisely the calls that
overrode a cap. Across the whole run, every observation carrying `crisisCap` has `force=None`.

Separately, nothing records why force was used. `force_reason` is null across every entry in
`events.jsonl`, and no `advance_review` event exists after 2026-09-08, so a session can pass
force indefinitely with no artifact stating the basis. The earlier version of this item claimed
a "documented basis" existed. It did not; it existed only in the operator's prose.

**Recommended fix.** Have a forced wait echo the cap it overrode and what triggered it, so
`crisis_cap` still fires at `review` severity rather than `info`. Require and journal a short
`force_reason` on the first forced wait of a session, and re-prompt when the threat signature
changes: a new hostile faction, a new hostile building class, or a hostile crossing a distance
band.

## 5e. Pointer selection drops risk-bearing keys without notice

**Fixed.** `select_output` compares each risk's `value_ref` against the selected pointers and,
when a non-info risk is dropped, returns `selected` plus `retained_risks` naming what went.
Selecting the risk itself, or selecting from a response with no risks, is unchanged.

The facade's compact `project` force-keeps keys carrying a warning, a risk, or a change, and
lists everything dropped in `omitted_keys`. The CLI's `select_output` does neither: it is
applied to display output only and has no force-keep and no omission report. Two selection
mechanisms in the same tool should not have opposite safety properties.

This one is mitigated by the fact that selection is display-only and the full observation is
journaled, which is how this review was possible at all. It is still the mechanism that hid
the death letters from the operator in real time.

**Recommended fix.** Give `select_output` the same force-keep and omission notice as `project`.

## 5f. ISSUES.md is generated, but the run rules treat it as editable

**Fixed on both sides.** `ISSUES.md` and `STATE.md` now open with a line saying they are
generated and overwritten, and `ISSUES.md` names the command that closes an issue. `AGENTS.md`
and `docs/memory.md` no longer describe either as hand-maintained.

`memory.py` renders `ISSUES.md` from the issue store and writes it with `atomic_text`, so any
hand edit is silently overwritten on the next rebuild. `AGENTS.md` and `docs/memory.md`
describe `ISSUES.md` as current working memory to be updated and pruned by the player, which
reads as an invitation to edit the file.

Observed consequence: a player "closed" the Recruit Kolyoya issue by deleting it from the
Markdown and reported it closed in a published history chapter. The issue was never closed in
the store. Two later rewrites recording six deaths were also discarded, which is why the file
still carries live next-actions for three dead colonists.

**Recommended fix.** Either make `ISSUES.md` clearly generated, with a header saying so and
naming the command that closes an issue, or stop regenerating it and let the store follow the
file. Do not leave a generated file described as hand-maintained.

## 5g. Two telemetry files with different schemas and different coverage

**Partly fixed.** Both files are current and serve different transports, so neither is stale
and retiring one would lose data. Every row in each now carries `stream`, `public_tool_calls`
or `game_calls`, so a query can assert which file it read. That converts the silent empty
result into a checkable one; it does not make a missing key raise, which stays open.

`campaigns/NAME/` holds both `telemetry.jsonl` and `facade-telemetry.jsonl`. They are not the
same data. `telemetry.jsonl` has 7,332 rows on `continuance`, carries `event_context`,
`omitted`, `model_bytes`, `verification_sections` and `facade_tool`, and covers current play.
`facade-telemetry.jsonl` has 86 rows, stops at 2026-09-11, and uses `public_tool` and
`response_bytes` instead.

Two reviewers of this incident each read one file, reached opposite conclusions about whether
event context was suppressed, and spent a round resolving it. The names give no hint which is
current, and the key that identifies the tool differs between them, so a query written for one
silently returns nothing on the other rather than erroring.

The naming is only half the trap. The other half is that a query for a key the file does not
have returns zero rows rather than raising, so an empty result reads as a confident negative.
Both reviewers reasoned from one and were sure of the answer.

**Recommended fix.** Retire or rename the stale file, or have both carry a `schema` field and a
header row naming their successor. At minimum, document which one is authoritative.

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
