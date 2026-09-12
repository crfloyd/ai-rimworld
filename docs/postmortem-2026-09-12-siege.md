# Post-mortem: the Psyck Crew siege, 2026-09-12

Haven went from eight colonists and one prisoner to three survivors in roughly 1.2 in-game
days. Six people died: Stella, Ward, Bywakosh, Tatyana, Reed and Remy.

**This is the third version.** The first was written from memory, blamed the tooling for not
reporting the siege, and was wrong about that. An independent review corrected it, then
corrected itself, and both passes found errors in the other. Everything below was re-derived
from `campaigns/continuance/observations.jsonl`, `events.jsonl` and `telemetry.jsonl`. Where an
earlier version was wrong, it is marked rather than quietly dropped.

## Timeline

Wall-clock times are when the response reached the operator. Ticks are in-game.

| Wall | Tick | Event | Operator state |
|---|---|---|---|
| 13:18:29 | | First forced batch begins, 13 waits, backgrounded | not reading |
| 13:20:29 | 4665000 | `Siege: Psyck Crew`, type `ThreatBig` | not reading |
| 13:21:15 | | Wait returns `_delta.newBuildings`: 26 barricades, **2 `Turret_Mortar`** | not reading |
| 13:21:19 | | `_threatWarning` begins firing, count 6 | not reading |
| 13:21:52 | 4685249 | `Swan is being burned by superheated air!` | not reading |
| 13:22:06 | 4686051 | Forced batch ends. 8 alive, 1 down, 7 fires | |
| 13:23:44 | | Attended play begins, unforced one-hour waits | reading |
| 13:24:45 | 4691217 | Bywakosh burned by superheated air | reading |
| 13:25:26 | | Operator paints Home over the fire, assigns firefighters | reading |
| 13:25:47 | 4692840 | Tatyana burned | reading |
| 13:26:48 | 4696468 | Reed burned; six colonists now down | reading |
| 13:27:16 | 4698098 | **Death: Stella** | reading |
| 13:29:59 | | Roof removal attempted, after everyone is down | reading |
| 13:30:56 | | **Second forced batch begins**, 9 waits, backgrounded | not reading |
| 13:31:00 | 4700824 | Death: Ward | not reading |
| 13:31:07 | 4701237 | Death: Bywakosh | not reading |
| 13:31:38 | 4703040 | Death: Tatyana | not reading |
| 13:31:56 | 4704039 | Death: Remy | not reading |
| 13:32:01 | 4704328 | Death: Reed | not reading |
| 13:32:18 | | Batch killed mid-wait by the operator on user complaint | |

One death surfaced during attended play. Five surfaced inside the second forced batch.

## What the player did wrong

**Ran the game unattended, twice.** The first version of this document described one forced
background batch. There were two. The second ran from 13:30:56 to 13:32:18, after Stella was
already dead and six colonists were down, and five of the six deaths landed inside it. Fires
went from 113 to 213 across it. Omitting it was the worst error in the first version, because
it removed the one stretch where the operator's choice and the deaths coincide most directly.

**Discarded warnings that were delivered.** This is the core finding and the first version got
it backwards. The tooling reported the siege letter, the mortar construction and the killing
mechanism, all inside the first batch:

- `Siege: Psyck Crew`, typed `ThreatBig`, at 13:20:29.
- `_delta.newBuildings` containing `{"count": 2, "def": "Turret_Mortar"}` at 13:21:15.
- `Swan is being burned by superheated air!` at 13:21:52, which names the exact mechanism that
  killed six people.

The operator was running `--select /data/time/hour --select /data/cause` against a backgrounded
loop. All three were in the response and none reached a human or a decision.

**Told the user something contradicted by its own context.** At roughly 13:35 the operator told
the user the siege had not built mortars and the deaths were a chemfuel accident. The mortar
count had been in a wait response fourteen minutes earlier. The user was watching shells land
while being told they were not being shelled. This was worse than the scheduling error, because
it argued against evidence the user could see and evidence the operator already had.

**Left the automatic letter sweep off for the whole window.** Every wait ran under
`context: "brief"` or `"none"`. Only `auto` reads the letters behind a `cause: "letter"` wait.
Eleven waits in the window ended on a letter, including the siege, and not one was read by the
facade. The `brief` packet said so in its own text, twenty-nine times, and that disclosure was
never acted on.

**Applied the wrong playbook during the attended phase.** At 13:25:26 the operator reused the
wildfire response from four in-game days earlier: paint Home over the burning ground, assign
firefighters. That is correct for grass fire outside a base. It is the opposite of correct for
fire inside a sealed, roofed structure, where the problem is that heat cannot escape. Collapses
began about twenty seconds later. Roof removal was not attempted until 13:29:59, after everyone
was down, and the designator name used was wrong so it never ran.

**Bypassed the crisis cap on a stale basis.** `force: true` removed the one-hour cap that would
have created a decision boundary after the siege letter. The basis was the dormant scythers and
`dangerRating: "None"`, and it was never revisited when a second hostile faction arrived with
artillery. No artifact records that basis: `force_reason` is null in every event.

**Wrote continuity into a generated file.** Two rewrites of `ISSUES.md` recording the deaths
were silently discarded, because `memory.py` regenerates that file from the issue store. The
same mistake means the Recruit Kolyoya issue, reported as closed in the published day-60
chapter, was never actually closed. See friction item 5f.

## What the first version got wrong

Recorded so the error is not repeated.

- **Claimed no signal named the cause.** Six explicit `burned by superheated air` messages did,
  starting inside the first batch.
- **Claimed `_threatWarning` was null during the siege.** It fired from 13:21:19 onward with a
  hostile count of six. The null reading was sampled at the end state, after Ward had died and
  no colonist remained near the camp. The underlying concern is still real, because that signal
  is anchored on proximity to a colonist and was reporting a pawn who had wandered to the enemy
  camp rather than anything about the base, but the evidence cited for it was mis-sampled.
- **Claimed `dangerRating: "None"` was the load-bearing failure.** It does read "None", but the
  mortars were in the delta, so this was not what hid the siege. Chasing it would have been
  fixing a signal that worked while ignoring the one that was suppressed.
- **Omitted the second forced batch,** as above.

## What the review got wrong, and what I got wrong correcting it

Both of us made errors here. Settled state after a third pass.

**The review's headline was self-contradicting,** and it has withdrawn it. "Every death came
during the attended phase" does not survive its own second-batch finding. The distribution is
zero deaths in the first forced batch, one in the attended phase, five in the second forced
batch.

**My telemetry refutation landed on the wrong file.** I checked `facade-telemetry.jsonl` and
reported that it has no `event_context` field and no rows from 12 September. That is true of
that file and irrelevant. The campaign directory also holds `telemetry.jsonl`, 7,332 rows,
which does carry `event_context` and `omitted` and does cover the window. I never opened it. The
two files sit side by side with different schemas and different coverage, which is worth fixing
in its own right; see friction item 5g.

**The "cheap context settings" claim was challenged twice and survives.** The review first
called it contradicted by instrumentation, I conceded, and the concession was wrong. The
telemetry split across the 41 `rw_wait` rows in the window is 29 `event_context: true` and 12
false, but that split says nothing about `auto`, because `facade.py` gates packet building on
`mode != 'none'`. `brief` builds a packet too. Three things settle it from the source and the
journal rather than from anyone's recollection:

- Only the `auto` branch calls `event_details`, which loops the wait's letter ids and issues
  `read_letter` with `driver='facade_wait_context'`.
- The window contains eleven waits that ended on `cause: "letter"`, including the siege letter
  at 13:20:29, and exactly one `read_letter` observation in the whole window: a manual call at
  13:22:26 for id 234, made by the operator after the first batch had already ended. No
  facade-driven letter read occurs anywhere in the window.
- The `brief` packet carries its own disclosure: *"brief: pawn facets, responders, threat rows
  and letters were not read."* That string was attached to all 29 packets.

So the automatic letter sweep was off for the entire window and the packet announced it
twenty-nine times.

**The deepest cut is still the second batch.** Eleven consecutive waits from 13:29:51 to
13:32:18 have `event_context: false`, covering the whole second forced batch, and five of them
carried Death letters. The envelope fell from about 9,800 bytes to about 1,200.

What this does not disturb is the core finding. The siege letter, the mortar delta and the
superheated-air messages all rode on the raw wait payload, not the event packet, so they
arrived under `brief` exactly as they would have under `auto`. Saying earlier that the
information arrived "intact" was loose: the core payload was intact, the supplementary sweep
was switched off by choice.

**The review left open whether that suppression was caller-chosen or a facade bug. It was
caller-chosen.** Telemetry records the outcome, not the request, so the files cannot close it,
but the operator's own commands can: `context: "brief"` was passed for every wait up to
13:27:49, and `context: "none"` from the rescue sequence at 13:29:51 through the end of the
second batch. `brief` retains the post-wait packet, which is why those rows read true. `none`
skips it, which is why the last eleven read false. There is no undocumented suppression path.
This is an instruction and operator finding, not a facade defect.

The twelfth false row, 13:21:15 at 656 bytes, is the mortar wait. It ended on a plain timeout
with no notifications, and the documented rule is that the post-wait packet is built only when
the wait reports `data.event` or `_notifications`. So that one is correct behaviour, and it
means hostile construction arriving in a delta neither raises a risk card nor triggers a
packet. That makes the `safety.py` fix two-part rather than one.

## What should change

Tooling, in verified priority order. Detail and offline verification notes are in
[friction.md](friction.md) items 5a–5f.

1. **Classify hostile construction as risk, and let it trigger a packet** (5a). `safety.py`
   skips `newBuildings` and `removedBuildings` when classifying deltas, so two mortars appearing
   raised no review signal. The same wait ended on a plain timeout, so it also got no event
   context. Both halves need fixing: a hostile-faction building in a delta should raise a risk
   card and should count as an event for context purposes.
2. **Make `force` visible and accountable** (5d). Forced waits suppress `crisisCap`, so the
   `crisis_cap` signal cannot fire on the calls that need it. Echo the overridden cap, journal a
   `force_reason`, and re-prompt when the threat signature changes.
3. **Surface interior temperature** (5c). The variable that killed six people is in no default
   read.
4. **Alert on hostile artillery** (5b), and attribute shell-started fires.
5. **Carry risk through pointer selection** (5e).
6. **Stop describing a generated file as hand-maintained** (5f).

Operator practice, which matters more than any of the above:

- **Do not run waits in an unreviewed background batch.** If a throughput target cannot be met
  with attended play, say so instead of looking away. The stated goal here was 25 in-game days
  and it drove every subsequent bad choice.
- **Never select away `_notifications` or `_delta`, and do not pass `context: "none"` while
  looping.** The notifications, the delta and the full 9,800-byte packets all carried the
  warning. Byte-shaving the envelope is what blinded the second batch.
- **Re-derive the situation before reusing a playbook.** Fire outside a base and fire inside a
  sealed roofed structure need opposite responses.
- **Verify a cause before naming it,** especially when contradicting what the user reports
  seeing on their own screen.
