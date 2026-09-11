# Open tooling friction

Current open items only. Everything the 0.9.0 live report raised was implemented in 0.9.1 and
removed from this file; see `CHANGELOG.md` and the completed
`docs/plans/2026-09-11-decision-loop-friction.md`. The superseded report and the raw playtest
log remain in git history.

Source of these items: a measured live playtest of 0.9.1 on `continuance`, 2026-09-11, ticks
3720001 to 3896437. The agent resumed a berserk crisis, completed a trade with a tribal bulk
goods caravan, survived a cold snap, and received a mechanoid cluster. Evidence lives in
`campaigns/continuance/observations.jsonl` and `reference/compositions/`.

Ranked by measured cost to the decision loop.

---

## 1. Time advancement is the dominant cost

Three separate mechanisms each cut a wait short. Together they are why play degenerates into
short bursts separated by model turns. This is the single highest-value area to fix.

### 1a. The crisis cap is reported, classified as a safety stop, and never documented

**Correction, 2026-09-11.** An earlier draft of this item claimed the response never says the
cap applied, and recommended inferring it by comparing `ticksWaited` to the request. That was
wrong. Upstream already returns a `crisisCap` object and it is fully self-explanatory:

```json
{"cappedAtTicks": 2500, "reasons": ["hostiles"],
 "note": "Wait was capped at 1 in-game hour because of an active crisis. Address it, or pass force:true to wait longer."}
```

It is documented in the `wait_for_event` catalog description, listed in `observations.FLAGS`,
classified in `safety.py`, and present in 35 receipts in this campaign, including 32 from the
playtest itself. The playtest agent missed it by printing only selected fields from each wait
and never dumping the whole body. Do not add a second inferred field; promote the existing one.

The real defects are three, and they compound.

**It is classified `critical`.** `safety.signals` adds `crisis_cap` at `critical`;
`safety.assess` treats any severity above `info` as a blocker, which sets `stop`, which sets
`requires_review`. A routine capped timeout therefore presents as a safety stop.

**That also forces an event packet on every quiet capped wait.** `wait_sequence` computes
`event = data.event or data._notifications or body.requires_review`. Because `crisisCap` sets
`requires_review`, a wait that advanced 2500 ticks with nothing happening still runs a
post-wait `get_status` and builds a decision packet. Measured in the playtest: **47 of 52
waits ran an event-context read**, most of them on quiet capped timeouts. Demoting the
severity is not cosmetic; it removes an entire extra game read per quiet wait.

**Nothing the agent is told to read mentions it.** `facade.md` is required reading before the
first live call and never names `crisisCap` or `force`; it points at `wait_budget`, which is
only our own deadline clamp and is `null` in this situation. The `rw_wait` description says to
inspect `pausedAfter` and `ticksWaited`, not the cap.

**Why it matters even when reported.** The cap's trigger is "hostiles on the map", which stays
true for a dormant mechanoid cluster's entire countdown. During the playtest the fuse was 4.3
in-game days, danger rating was `None`, nobody was downed and there was no fire, yet every
wait was cut to an hour by three sleeping machines 55 cells away. Measured on the same colony,
requesting 20,000 ticks each time:

| Path | Calls | Ticks advanced |
|---|---|---|
| Default | ~20 | 48,816 |
| `force: true` | 4 | 48,816 |

One forced call reached the full 20,004 ticks.

**The cap is not what makes a wait safe.** `wait_for_event` already returns on a new letter, a
notable message, a hostile-count transition, or a forced pause. `force` removes only the time
limit; every one of those triggers still fires. In a real firefight the wait ends on the event
regardless; across four quiet days the cap only bills round trips.

**Recommended fix.** Two changes, and the first is useless without the second.

1. **Reclassify `crisis_cap` to `info`.** Not `review`. `assess` marks anything above `info`
   as a blocker (`severity != 'info'`), so `review` still sets `stop`, still sets
   `requires_review`, and still trips event context. Keep the `crisisCap` object literal and
   visible in the wait body; it must never be referenced away or dropped.
2. **Drive event context from what the game reported, not from our review flags.** Change
   `wait_sequence` from `event = data.event or data._notifications or requires_review` to
   `event = data.event or data._notifications`. `requires_review` is the wrong proxy for "an
   event happened", and `crisis_cap` is far from the only thing that sets it. On the playtest
   receipts the other blockers riding along on quiet capped timeouts were `_threatWarning`
   (`review`), `delta:pawnDamage` (`review` or `critical`, and it fires on *healing* too
   because the upstream field mixes both), and `wait_event` (`review` for any non-timeout
   cause). Demoting `crisis_cap` alone leaves every one of those in place.
3. **Name `crisisCap` and `force` in the `rw_wait` description and the `facade.md` wait
   section**, making explicit that `crisisCap` is upstream's crisis cap and `wait_budget` is
   our own deadline clamp, and that they are different things.

Keep `force` opt-in with the existing "according to actual risk, never automatically" rule. It
held up in play: withheld while two colonists were dying of hypothermia, used once danger was
`None`. The bad trigger proxy itself is upstream and is not ours to fix; surfacing why is the
local lever.

**Measured effect, and its limit.** Replaying all 52 playtest wait receipts through both
rules: event context currently runs on **47**, and would run on **35**. So the combined fix
removes **12 extra `get_status` reads**, not most of them. The remaining 35 are waits where
the game genuinely set `event` or `_notifications`. That is a real but bounded win, and it is
the reason item 1b is where the rest of the volume lives.

**Safety check on change 2.** Across the whole campaign history there are 142 waits whose
`cause` is `letter`, `notification`, `forcePaused`, `threatAppeared`, `threatsCleared` or
`pauseButton`. **Every one of them carries `data.event` or `data._notifications`.** Zero would
lose their packet under the proposed rule. A wait with an unconfirmed pause also keeps its
existing separate protection: `context_safe` already gates on `pause_guard`, and
`requires_review` still appears on the body either way.

**How to verify offline.**
- A fixture wait carrying `crisisCap` with `cause: timeout` must not set `requires_review`,
  must not run an event-context read, and must still show the `crisisCap` object verbatim.
- A fixture wait carrying `crisisCap` **and** `_threatWarning` **and** a `delta.pawnDamage`
  healing entry, with `cause: timeout`, must also run no event-context read. This is the case
  that demoting `crisis_cap` alone does not fix.
- A fixture wait with `cause: threatAppeared` and `data.event` set must still build its packet.

### 1b. Every notification ends a wait, including ones that cannot change a decision

During the cold snap each frost-killed plant emitted a notification that terminated the wait.
One wait returned after **58 ticks**, one game second, for a dead rice plant. Six consecutive
waits advanced about 6,000 ticks total. After `force` removed the cap, notifications became
the new binding constraint: three of four forced waits ended on `cause: notification`, two of
them on a repeat of the same "Major break risk" alert already visible in the previous packet.

**This is the hardest item here and should be built last.** `wait_for_event` has no ignore
parameter, so suppression cannot be pushed upstream. The facade would have to keep waiting
internally while still returning the ignored notifications, which makes one public `rw_wait`
into a composition of several game advances. That carries real obligations:

- Bound it hard: a maximum internal iteration count and a wall-clock budget, both reported.
- Record every internal wait in the durable composition manifest, as `rw_observe` already does
  for its sub-reads, so an interrupted loop is reconcilable and never replayed.
- Stop immediately on a letter, a threat transition, a `forcePaused`, or a zero-tick advance.
  A re-wait loop must never mask item 1c.
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

### 1c. A modal dialog freezes time and the wait does not say so

Three consecutive waits returned `ok` with `cause: forcePaused`, `ticksWaited: 0`, and an
unchanged game tick of 3770419. Nothing named the blocker. It was a
`Dialog_NodeTree` "Research finished: Deep drilling" with `forcePause: true`, found only by
calling `list_windows` by hand. Three model round trips bought zero game time.

**Recommended fix.** When a wait returns `ticksWaited: 0` with `forcePaused`, read
`list_windows`, name the pausing window and its buttons, and give the exact `window_action`
call that clears it. This is cheap: one extra read only on the zero-progress path.

**How to verify offline.** A fixture returning `ticksWaited: 0, cause: forcePaused` plus a
`list_windows` fixture with a force-pausing dialog must return the window and a concrete
dismissal call.

---

## 2. Coverage classification

### 2a. `truncated` from the caller's own limit is misreported as degraded

The decision preset's `threat` topic hardcodes `limit: 20`. On a map with 33 matching pawns
upstream returns `matched: 33, returned: 20, truncated: true`, the normalizer maps that to
`partial`, and 0.9.1 then marks the section `degraded`. Honoring a requested limit is not
degradation. The same happened to a deliberate `list_unmanaged_items limit: 60` against 1123
matches.

**Precise condition for the implementer.** This is upstream `truncated`, not our own `cap()`.
Evidence `obs-5f31a7f9ac3a410b98632269b7209077` has `args.limit == 20` and
`data.returned == 20` with no `reason` field at all. Our `caller_limit` marker is set only by
`facade.cap()` on the projection path and was never involved. So the test is
`data.truncated and data.returned == args.limit`, not `reason == "caller_limit"`.

Also note this means that before 0.9.1 any decision packet including `threat` on a busy map
silently stopped mid-packet, which is very likely one of the four recorded observe stops in
the 0.9.0 baseline.

**Recommended fix.** In `coverage_problem`, treat that shape as `known` with its truncation
metadata intact. Keep `largeOutput` degraded.

**How to verify offline.** A fixture with `limit: 20`, `matched: 33`, `returned: 20` must be
`known`; a `largeOutput` fixture must still degrade; a fixture where `returned < limit` but
`truncated` is set must still degrade, because that bound came from somewhere else.

### 2b. An unknown thing id blocks a whole composition — closed, leave as is

`inspect_thing` on `Campfire169350`, a campfire that no longer existed, returned an upstream
error and the two pawn reads after it were `not_run`.

**Decision: leave it blocking.** An unknown id means the agent's world model is stale, which
is categorically different from a size guard reporting its own bound. Two skipped pawn reads
are cheap next to a guard acting beside a target that is not there. If this is ever revisited,
scope it narrowly to "target not found", never to upstream errors generally, and keep the
guard abstention.

## 3. Response shaping is inconsistent between tools

### 3a. Receipt annotations never reach composition sections

`rows_withheld`, `already_satisfied`, `retry` and `deal` are added in `facade.self_contained`,
which only `rw_read` and `rw_act` use. The identical `list_trade` read inside an `rw_observe`
section showed `returned 57 / tradeableCount 58` with no explanation, while the same read
through `rw_read` explained it.

**Recommended fix.** Run `facade.annotate` in the composition capture path too.

### 3b. Decision presets are not materialized inside `rw_wait verify`

A `preset: "decision"` verify query passes validation, expands to `st.status`, and returns the
entire raw `get_status` bundle, because `materialize_decisions` runs only in
`Composer.execute`. Same input, two different and oppositely sized outputs depending on which
tool ran it.

**Recommended fix: materialize, do not reject.** `verify` exists precisely to avoid a post-wait
handover, and a decision packet is the most useful thing to ask for there. Call
`materialize_decisions` in `run_reads` on the same query specs. Silently returning the fatter
object is the bug; rejecting the preset would remove the reason `verify` exists.

### 3c. `_threatWarning` is repeated on every one-shot receipt

Each receipt carries the full nine-colonist threat block, roughly 500 bytes, including on pure
mutation receipts. The `same_as` dedupe that exists to solve this is connection-scoped, and
one-shot CLI, the documented default transport, opens a new connection per call, so it never
fires.

**Recommended fix: drop `_threatWarning` from mutation receipts.** Do not persist the
reference table across one-shot CLI processes; a stale `same_as` pointing at a table from a
dead process is worse than 500 repeated bytes, and references are deliberately
connection-scoped for that reason. A standing threat belongs on reads and waits, which is
where an agent should be discovering it. Keep it on `rw_read` and `rw_wait` output unchanged.

## 4. Discovery and filter gaps

### 4a. An empty filtered result cannot be distinguished from "not yet"

Immediately after the `Mechanoid cluster` letter, `list_things category=pawn faction=hostile`
matched 0 and `category=building faction=hostile` matched 0, because the cluster was still
landing. Two thousand ticks later the same reads returned 3 mechs and 10 structures. The
0.9.0 report recorded the mirror image of this with `list_world_objects kind=caravans`
returning empty while the trader stood on the map.

**Recommendation.** Where a threat letter is active and a hostile scan is empty, say so: an
empty hostile list within a short window of a `ThreatBig` letter deserves a one-line note that
arrival may still be in progress. Do not fabricate a count.

### 4b. `list_things` pawn rows carry no weapon

The friendly-fire rule depends on knowing who is armed, but roster rows return `weapon: None`
for every pawn. Finding a safe melee pawn cost two extra reads during an active mental break.

**Recommended fix: a workflow note, not a new field.** RimMolt does not send `weapon` on
`list_things` rows, and we must not promise a field upstream does not provide. `get_pawn`
summary does carry it, confirmed in evidence (Remy, "Bolt-action rifle (normal)"). Say in the
`combat_event` and `resume_crisis` workflow notes that the roster view cannot answer "who is
armed" and that `get_pawn` summary is the read that can.

### 4c. A silent limit hit looks like absence

`list_things category=building nearId=... radius=12 limit=60` returned 60 rows and zero
passive coolers; `defName: 'PassiveCooler'` returned both instantly with `matched: 2`. The
truncation was reported, but an agent scanning labels for a substring just concludes the thing
is not there.

**Recommended fix.** Workflow and tool-description guidance: when scanning for a specific
building or item, filter by `defName` rather than by radius and limit.

### 4d. `order_pawn` returns bare `options: []` with no reason

A berserk colonist exposes no float-menu options, so the listing returned `[]`. That is
indistinguishable from a failed lookup. A one-line cause, such as the target being in a mental
state, asleep, or unreachable, would have saved a guess during a crisis.

---

## 5. Verified answers from live play

These were open questions. They are now settled and need no further investigation.

- **`set_trade` cannot batch today, and the exception is safe to extend.** An
  `independent: true` batch of three sells stopped after action 0 with
  `reason: "Action response requires review"`. The receipt that caused the stop was
  `ok: true`, `transfer: -35`, `silverAfterDeal: 242`, and its only review signal was
  `_dialogOpen: true`, structurally identical to the `window_action` receipts the same-dialog
  exception already allows through. **Fix:** extend `expected_same_dialog` to `set_trade`
  while `list_trade` reports the same active trader and negotiator, and make `trade_action`
  accept an explicit batch terminator that always stops.
- **The missing `list_trade` index is benign.** Index 2 is absent because silver is reported
  separately in the `silver` field. `returned 57 / tradeableCount 58` is the honest signal and
  `rows_withheld` explains it correctly. No change needed.
- **`trade_action cancel` after a committed deal never had to be tested.** Dismissing the
  negotiator message box with `window_action button=OK` closed the trade dialog as well, so no
  `cancel` was needed. The 0.9.0 leftover-dialog problem did not reproduce. The `deal`
  annotation's `unverified` note about cancel should stay as it is.
- **Berserk colonists cannot be arrested.** No float-menu options are offered at all. The
  working resolution is to draft a pawn carrying no lethal ranged weapon and order
  "Melee attack X". The menu also offers "Fire at X", disabled only for range, which confirms
  the recorded friendly-fire hazard is real and range-gated.
- **Passive coolers have no off switch.** `inspect_thing` offers only Deconstruct. This closed
  a campaign issue that had been open since the previous session.

## 6. Confirmed working in 0.9.1, do not regress

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

## 7. Correction to a 0.9.1 change

The `trade` workflow tells the player to confirm bought goods with `list_unmanaged_items`.
That is wrong on a mature map: it matched 1123 items with no positional filter, dominated by
map-wide corpses and old steel. The correct confirmation is
`list_things category=item nearId=<trader> radius=12`, which returned 8 rows and showed the
exact bought stacks. Change the workflow note.

---

## 8. Recommended sequencing

Reviewed and agreed with a second pass on 2026-09-11.

1. **Wait loop.** Reclassify `crisis_cap` to `info` (not `review`), decouple event context
   from `requires_review`, name `crisisCap` versus `wait_budget` and `force` in the `rw_wait`
   contract and `facade.md`, and auto-name the pausing window on a zero-tick `forcePaused`.
   Items 1a and 1c. The two parts of 1a must land together; either alone is ineffective.
2. **Correctness already measured.** Caller-limit is not degraded (2a); annotate inside
   compositions (3a); materialize decision presets in `verify` (3b); drop `_threatWarning`
   from mutation receipts (3c); extend the same-dialog exception to `set_trade` (section 5,
   live-verified); correct the trade confirmation note (section 7).
3. **Notification suppression.** Item 1b, only after 1a and 1c land and a playtest shows
   notifications as the new ceiling. Build it as a bounded, manifest-recorded composition.
4. **Documentation only.** Items 4a, 4b, 4c, 4d.
5. **Closed, do not implement.** Item 2b.

Constraints that still apply: no new public tool, no auto-force, no silent drops, offline
fixtures built from the recorded receipts in this campaign, and the section 6 list stays
frozen.

## 9. Process lesson from the playtest

The `crisisCap` field was present in every capped receipt and the playtest agent still
reported it as missing, because every wait was inspected through a hand-written selector that
printed `cause`, `ticksWaited` and `wait_budget` and nothing else. Selective printing is the
right habit for context, but a finding of the form "the response never tells me X" must be
checked against a full body dump before it is written down.
