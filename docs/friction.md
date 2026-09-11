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

### 1a. The crisis cap is invisible, and its trigger is a bad proxy

`wait_for_event` caps a wait at 2500 ticks, one in-game hour, whenever hostiles are on the
map, fire is in the home area, or a colonist has a life-threatening condition. `force:true`
bypasses it. This is upstream behavior, documented in the tool's own schema, not ours.

Two problems.

**The response never says the cap applied.** A request for 20000 ticks returns
`ticksWaited: 2505, cause: "timeout"` with `wait_budget: null`. That reads as "nothing
happened", not "your horizon was cut to an eighth". The agent has no signal to act on.

**"Hostiles on the map" stays true for days.** A dormant mechanoid cluster sits on the map for
its whole countdown. During this playtest the cluster's fuse was 4.3 in-game days, danger
rating was `None`, nobody was downed, and there was no fire, yet every wait was still capped.
The cap was pinned on by three sleeping machines 55 cells away.

Measured directly, same colony, same conditions, requesting 20000 ticks each time:

| Path | Calls | Ticks advanced | Ticks per call |
|---|---|---|---|
| Default | ~20 | 48,816 | ~2,500 |
| `force: true` | 4 | 48,816 | 12,204 |

One forced call reached the full 20,004 ticks with `cause: timeout`, eight times the cap.

**The cap is not what makes a wait safe.** `wait_for_event` already returns on a new letter, a
notable message, a hostile-count transition, or a forced pause. `force` removes only the time
cap; every one of those triggers still fires. So during a genuine firefight the wait ends on
the event anyway, and during four quiet days the cap does nothing but bill round trips.

**Recommended fix.** Do not auto-force, and do not remove the cap. Make it visible and let the
agent choose:
- When `ticksWaited` is materially below the requested tick budget and `cause` is `timeout`,
  add a field naming the likely crisis cap, the condition that triggered it (hostiles present,
  fire, life-threatening condition), and `force:true` as the deliberate override.
- Surface the same condition proactively in the wait result so the agent can decide before
  burning several capped calls.
- Keep `force` opt-in with the existing "according to actual risk, never automatically" rule,
  which held up well in play: it was correctly withheld while two colonists were dying of
  hypothermia and correctly used once danger was `None`.

**How to verify offline.** A fixture where the requested `maxGameTicks` greatly exceeds
`ticksWaited` with `cause: timeout` must produce the cap explanation; a wait that ends on a
real event must not.

### 1b. Every notification ends a wait, including ones that cannot change a decision

During the cold snap each frost-killed plant emitted a notification that terminated the wait.
One wait returned after **58 ticks**, one game second, for a dead rice plant. Six consecutive
waits advanced about 6,000 ticks total. After `force` removed the cap, notifications became
the new binding constraint: three of four forced waits ended on `cause: notification`, two of
them on a repeat of the same "Major break risk" alert already visible in the previous packet.

There is no way to say which notification classes are decision-relevant.

**Recommended fix.** Give `rw_wait` a caller-selected notification filter, for example
`ignore: ["plantDied", "healed"]` or a coarser `notifications: "all" | "significant"`, and
have the facade suppress wait termination for the ignored classes while still returning them
in the packet. Never silently drop a class the caller did not name. A repeat of a message
already delivered in the previous wait packet is the clearest candidate for suppression.

**How to verify offline.** A fixture stream of repeated plant-death notifications with one
letter must terminate once, at the letter, when the plant class is ignored.

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
upstream returns 20 and sets `truncated: true`, the normalizer maps that to `partial`, and
0.9.1 then marks the section `degraded`. Honoring a requested limit is not degradation. The
same happened to a deliberate `list_unmanaged_items limit: 60` against 1123 matches.

This also means that before 0.9.1 any decision packet including `threat` on a busy map
silently stopped mid-packet. That is very likely one of the four recorded observe stops in the
0.9.0 baseline.

**Recommended fix.** In `coverage_problem`, treat `truncated` as neither blocking nor degraded
when `returned` equals the caller's requested `limit`. Keep the truncation metadata visible.
Only an upstream-initiated bound should degrade.

**How to verify offline.** A fixture with `limit: 20`, `matched: 33`, `returned: 20` must be
`known`, not degraded; a `largeOutput` fixture must still degrade.

### 2b. An unknown thing id blocks a whole composition

`inspect_thing` on `Campfire169350`, a campfire that no longer existed, returned an upstream
error, which is correctly blocking, and the two pawn reads after it were `not_run`. An
unknown-id error is arguably also a complete, self-describing answer that says nothing about
sibling queries.

**Recommendation.** Judgement call, deliberately left open. If it is made recoverable, it must
be scoped narrowly to "target not found" and must not swallow other upstream errors. A guard
must continue to abstain beside it, as it already does for degraded sections.

---

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

**Recommended fix.** Materialize decision presets in `run_reads` as well, or reject the preset
in `verify` with a message naming the supported forms. Silently returning the bigger thing is
the worst of the three options.

### 3c. `_threatWarning` is repeated on every one-shot receipt

Each receipt carries the full nine-colonist threat block, roughly 500 bytes, including on pure
mutation receipts. The `same_as` dedupe that exists to solve this is connection-scoped, and
one-shot CLI, the documented default transport, opens a new connection per call, so the dedupe
never fires. `--select` works around it but every unselected call pays.

**Recommended fix.** Either persist the reference table across one-shot calls for a run, or
drop `_threatWarning` from receipts by default and keep it in reads, since a mutation receipt
is not where a standing threat should be discovered.

---

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
for every pawn; only per-pawn `get_pawn` carries it. Finding a safe melee pawn cost two extra
reads during an active mental break.

**Recommended fix.** Add `weapon` to pawn rows if upstream exposes it; otherwise say in the
trade and combat workflow notes that the roster view cannot answer "who is armed".

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
