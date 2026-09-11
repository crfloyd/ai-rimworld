> **Status (2026-09-11).** Every tooling item below is addressed in
> `docs/plans/2026-09-11-decision-loop-friction.md` and landed in version 0.9.1.
> Two questions are deliberately left open for the next live run, because saved
> receipts cannot settle them: whether a `set_trade` batch can safely continue on
> an unchanged trade dialog, and whether `trade_action cancel` after a committed
> deal can reverse it. The trade workflow currently says not to batch `set_trade`,
> and no tooling text claims anything about what `cancel` does to a committed deal.
> The slave medical bed question also remains open and needs an inspect before and
> after on a live bed.

The biggest slowdowns were **tooling contracts and evidence shape**, not “what should Haven do next.” Strategy was usually clear; getting a reliable next action through the facade often was not.

**Where the tooling cost time**

- **CLI vs session.** Early play used JSON-RPC-style calling. The real default is one-shot `./rw --run continuance call|observe|wait`. `observe` wants `--json`, not `--args`. `retrieve` does not take `--token`. Those mismatches produced failed turns before any game decision.
- **`--select` and “do not replay.”** Compact pawn reads live under `/data`, not `/needs`. A missing pointer looks like a failed operation even when the game call already succeeded. Recover with `retrieve --observation obs-…`, not another `get_pawn`.
- **Serial lock.** Two `./rw` calls at once hit `operation.lock`. Parallel “independent” reads are not actually independent on this host.
- **Review flags abort batches.** `_dialogOpen` and `_threatWarning` with `requires_review` stop `independent:true` `rw_act` chains. Trade then became many sequential `set_trade` calls. Same-dialog work is allowed in principle and painful in practice.
- **`rw_observe` decision + `world`.** The preset stopped mid-packet because world output is large and wants `confirm` or a `kind` filter. Pawns never ran. I had to rebuild the picture with extra reads.
- **World vs map for traders.** `list_world_objects` `kind=caravans` was empty while Eragalor was already on the map as pawns. The letter said they were approaching; the world list said nothing. The fix was `list_things` with `faction: any` near home, not another world query.
- **Stockpile vs map piles.** After a successful trade, `get_resources` still looked like the old colony (silver 144, no alpaca meat). The meat was on the ground at ~140,97. That looked like a cancelled deal until a `defName` item list.
- **Trade dialog leftover.** `trade_action accept` applied the deal but left the dialog plus a “Remy cannot talk properly” OK box. `cancel` afterward was scary because it might have undone the trade. It did not, but the receipts do not say that clearly.
- **Exact order labels.** Forge was already on the campfire; the next `order_pawn` failed with “No order matched” and `available: ["Already working…"]`. That is success, reported as error.
- **Schema vs live flags.** Compact `get_pawn` `seen_structure` still listed `_threatWarning` from older captures. Full retrieve of *this* obs had no hostiles. Extra caution for a ghost field.

**Where the game was confusing (as an API player)**

- **Campfire placement.** Many cells “blocked” because the *interaction* cell overlapped another building’s interaction spot (research benches, shelves), not because the fire tile was occupied. `rot: 2` at 129,119 worked after several failed ghosts. The `placement.interactionCell` field is the right hint; I burned tries before trusting it.
- **Cooking was suspended.** Low-food alerts did not say the stove’s simple-meal bill was `suspended: true`. Food looked like a production/haul problem until `list_bills`.
- **Reed cannot trade.** Social-incapable pawn: the only option was “Will never do Social.” Needed a different negotiator (Remy), then worse prices from a talking impairment that showed up *after* accept.
- **Slave medical bed.** Toggling “For slaves” on `Bed43450` did not change what inspect reported. I still do not treat that as proven.
- **Draft + friendly fire.** Drafting Remy with a rifle next to Tatyana during berserk kiting is how she took the gunshots. The float menu gives “Go here” when drafted; it does not warn that watch-for-targets will shoot a colonist.
- **Compaction stop.** Play also stopped because the conversation was summarized, not because the colony was safe. Current `ISSUES.md` can lag `STRATEGY.md` when a write is interrupted.

**What was fine**

- Combat/berserk *intent* (get them inside, tend, undraft) was obvious once pawn jobs and letters were in view.
- `list_trade` by index, unsuspend bill, and `rw_wait` with `verify` were usable once the contracts were loaded.
- Event waits ending on frost-kill toasts were correct; they just are not “Reed woke up.”

If you tighten one thing for the next measured run, I would put **trader-on-map discovery** and **post-trade stock vs ground piles** in the trade workflow, and treat **suspended bills** as part of the food-crisis path—not more catalog text.

---

## How to use this note

Live-play notes from Continuance (Haven), ~8–9 Jugust 5501 / wall 2026-09-10–11. They are player-experienced friction, not a measured VALIDATION.md result and not permission to change balance or saves.

Campaign-local surprises (berserk kite, `Bed43450`, Remy’s talking impairment, named pawns) stay in `campaigns/continuance/` unless someone deliberately generalizes them under [knowledge-boundary](knowledge-boundary.md). Tooling holes below are candidates for facade/CLI/workflow/tests.

Reproduce from saved evidence before inventing a new live trial: `./rw --run continuance retrieve --observation OBS_ID`, journals under `campaigns/continuance/`, and `./rw --run continuance issue --id ISSUE_ID`. Do not replay completed waits or trades to “fix” a selector.

| Kind | Where to look |
|---|---|
| CLI flag mismatches | `./rw observe --help`, `./rw call --help`, `./rw retrieve --help`; `tools/rimworld/cli.py` (`local_selection`, `--select`) |
| Facade / composition stop | [facade.md](facade.md), [composition.md](composition.md), `tools/rimworld/composition.py` (`queried_complete`, stop reason `Identity, pause, JSON or coverage requires review`), `tools/rimworld/observations.py` (`largeOutput` → partial) |
| Workflow text the player actually loads | `tools/rimworld/capabilities.py` `WORKFLOWS` / `DOMAINS`; `rw_capabilities {"workflow":"trade"|"food_crisis"}` |
| One-process lock | `tools/rimworld/control.py` `operation.lock`; also `session.py`, `composition.py` |
| Independent act stop | `docs/facade.md` same-dialog exception; `tests/test_facade.py` independent-batch tests |
| Continuance facts | `campaigns/continuance/STRATEGY.md`, `ISSUES.md` (may lag), `obs-*` below |

Suggested work order if plugging holes: (1) CLI/help and `--select` recovery already exist—document them where the player looks first (`docs/facade.md` fast-loop + `observe` help); (2) change `trade` / `food_crisis` workflow strings so the next player does not skip `list_things` / `list_bills`; (3) only then change composition/act-batch behavior, with a test that the old Continuance receipts still classify the same way.

## Tooling — investigate / plug (items above unchanged)

**CLI vs session.** `call` uses `--args`; `observe`/`guard` use `--json`/`--file`. `retrieve` is local and has no `--token`. AGENTS.md says one-shot CLI and “never invent a pipe”; a host with MCP may still tempt `session`. Plug: one cheat-sheet in facade “Fast decision-loop” listing the three flag sets; optional CLI error that names the sibling command (`observe: error: use --json`). Investigate: grep the play transcript for `jsonrpc`, `session`, `observe: error`.

**`--select` and do not replay.** `tools/rimworld/cli.py` returns `phase: local_selection`, `operation_completed: true`, `replay: Do not replay…`, plus `evidence`. Compact `get_pawn` without `tab` is summary under `data`; needs/health are only after `tab=needs|health` (or observe pawn include). Pointers must target the presented compact JSON, not the upstream mental model. Example failed select: `obs-42b650eee3e8451dbae266d3bc01c625` (summary-only Tatyana). Plug: `--select` error could list 2–3 example pointers from `available_top_level` / compact pawn keys (`/data/mood`, `/needs/thoughts` only when that container exists). Test: select `/needs` on a summary `get_pawn` must exit 2 and must not imply `ok:false` of the game op.

**Serial lock.** All ordinary controller entry points take `operation.lock`. The player’s “independent reads in one message” are two OS processes. Plug: docs one-liner “never parallel `./rw`”; or a clearer lock error that says “serialize one-shot CLI; batch inside `rw_observe` / `rw_act actions` instead.” Do not “fix” by allowing two game clients. Investigate a lock failure: the error names `.runtime/…/operation.lock`.

**Review flags abort batches.** Facade already continues same-dialog `window_action` when the *only* review flag is unchanged `_dialogOpen`. `set_trade` receipts also carry `_dialogOpen` + `requires_review`, so a trade `actions[]` stop is expected today. Continuance then used many sequential `set_trade` (e.g. cloth sell `obs-e1fd9494ebb44e20859d5f8a55f76003` through meat buy). Plug options, pick one and test: (a) extend the same-dialog exception to `set_trade`/`list_trade` while `active:true` and trader/negotiator unchanged; (b) document “do not batch `set_trade`”; (c) a single `set_trade` multi-row API (larger change). `_threatWarning` on unrelated pawn reads is a different stop—do not fold it into the trade exception.

**`rw_observe` decision + `world`.** Continuance packet `compose-cb9ebe68b6864c5b8572ec66d9e887c0` stopped `after: now.world` with `not_run` including threat and all pawn facets. `list_world_objects` without `kind` returns `largeOutput` / confirm. `observations.py` treats `largeOutput` as partial coverage; composition then refuses the rest. Plug: decision `world` should expand to `list_world_objects` with `kind` (default `caravans` or `settlements,caravans,sites`) or skip world on largeOutput and still run later queries; or document “never include `world` without `kind`.” Test: observe decision `include:["core","world"]` on a fixture with `largeOutput` world must either complete pawns or name `not_run` without looking like a full decision packet.

**World vs map for traders.** `WORKFLOWS['trade']` is `list_trade → set_trade → list_trade → trade_action` and assumes a dialog. Incoming bulk goods are map pawns (`kind: Town_Trader`, faction name on the pawn), often **not** `list_world_objects kind=caravans` (Continuance: count 0 while Chaz `Human169082` was at ~140,94). Letter text “approaching” ≠ world caravan row. Plug: insert `order_pawn` “Trade with…” and `list_things category=pawn faction=any nearId|nearX/Z` (and maybe `get_alerts` recentMessages) at the front of the trade workflow; domain `trade` currently omits `order_pawn`/`list_things`. Campaign evidence: pawn list `obs-14a8d0d557734faca54475ec27b034a9`.

**Stockpile vs map piles.** `get_resources` is aggregated stockpile-style counts, not “every item the colony just bought.” Post-accept, alpaca meat was `Meat_Alpaca169340/169341` at 140,97 / 139,97 (`obs-7a3beb8cba8841039c122f3af4373467`) while `get_resources` still showed silver 144 and no meat. Plug: trade workflow after `accept`: `list_things category=item` for purchased defs (or `near` the trader) **before** treating `get_resources` as the deal outcome; optional note on `get_resources` description. Do not teach “cancel undoes accept” from this incident—verify with `list_things` first.

**Trade dialog leftover.** `trade_action accept` `obs-e1b8cff9918641fb9a27df9eb4cf4938`: `traded:true` but `_dialogOpen:true`. Then `Dialog_MessageBox` “negotiator cannot talk properly” (`obs-6e53313e936040e38fdd01e5e4caed75`); `window_action button=OK`; leftover `list_trade` still `active` with colony silver 9; `trade_action cancel` closed it without reversing counts already moved. Plug: receipt should say whether the *deal committed*, whether a *blocking message box* is open, and whether `cancel` now means “close empty dialog” vs “abort uncommitted transfer.” Investigate upstream `trade_action` vs vanilla confirmation; add a facade note: dismiss message boxes with `window_action` before `cancel`. Talking impairment is a game fact (Remy’s health/talking); prices were already used.

**Exact order labels.** Receipt `obs-8d48610091ba4fb0afa02e1e44889fad`: `ok:false`, `error: No order matched 'Prioritize working on campfire (blueprint).'`, `available: ["Already working on campfire (blueprint)"]`. Player had just listed `Prioritize working on…` then the pawn started the job. Plug: treat “Already working on X” as a non-failure / `ok:true` alias when the requested command is the prioritize form of the same job; or return `executed:true, already:true`. Test from this obs shape, not live Forge.

**Schema vs live flags.** Observation `seen_structure` unions historical field paths for that tool; it is not “this capture contained `_threatWarning`.” Compact `data` / `view:full` for `obs-42b650eee3e8451dbae266d3bc01c625` had no hostiles. Plug: docs one sentence on `seen_structure`; never infer current threat from it. DangerRating `None` plus absent `_threatWarning` in `data` is the live fact.

## Game-as-API — investigate / plug

**Campfire placement.** Failed `build` receipts include `placement.interactionCell` and `reason` like “Interaction spot is blocked by wooden simple research bench” even when the fire cell is empty (`PlaceWorker_PreventInteractionSpotOverlap`). Rotation changes the offset (`rot:2` → `[0,1]` at 129,119 succeeded, blueprint `Blueprint_Campfire169343` → `Campfire169350`). Plug: building workflow / `build` description: read `interactionCell` before the next cell guess; try `rot` 0–3; `list_architect` if size unknown. Failed Continuance ghosts: 125,121 / 133,121 / 127,122. This is general placement, not a Continuance-only lesson.

**Cooking was suspended.** `list_bills` on `FueledStove43668` (`obs-691d99164ef247b1940f0bab5b7f35a8`): Cook simple meal `suspended:true`, psychite tea also suspended. `food_crisis` workflow already lists `list_bills` but after `get_resources`/`list_things`; alerts never mention bills. Plug: workflow purpose string for `list_bills`: “including suspended”; food domain already has it—make the one-line purpose louder. Player skip is the bug to design for, not missing tools.

**Reed cannot trade.** `order_pawn` list on a Social-incapable pawn: only `Will never do Social` (`obs-969a3614c06d46808b09b715915a709c`). Remy had Trade + Dismiss (`obs-e9a9f46a20bb4056aa67a046f23020c2`). `list_colonists` / pawn summary `incapableOf` is the pre-filter. Plug: trade workflow: pick a negotiator with Social; if options lack “Trade with”, try another pawn—do not wait. Impairment letter after accept is separate (`talking` capacity).

**Slave medical bed.** Continuance `Bed43450` “For colonist use”; float “For slaves” did not change inspectString. Re-check with `inspect_thing` / `do_thing_action` before and after, same `id`, paused. Unproven either way—keep as campaign unknown in ISSUES, not a global mechanics card until reproduced with inspect diffs.

**Draft + friendly fire.** Game rule: drafted colonist with a ranged weapon and hostile-adjacent targeting can shoot a berserk colonist. Facade `order_pawn` drafted “Go here” does not mention that. Campaign lesson for Continuance; optional combat_event workflow caution: do not draft armed friendlies onto a melee kite without expecting fire. Not a tooling defect.

**Compaction stop.** Conversation summarization dropped the player mid-loop; user saw a stop. `ISSUES.md` can stay stale if a write is interrupted (`STRATEGY.md` was updated later than ISSUES in this session). Plug for agents: coalesce STRATEGY/ISSUES before a long wait; compaction is not a safe pause. Tooling cannot fix host context limits; handoff checkpoint still can.

## Suggested workflow deltas (text only until edited in code)

`trade` (capabilities): find map trader (`list_things` pawns / letter) → `order_pawn` Trade with → wait until `list_trade active` → set/buy/sell → `accept` → dismiss message boxes → confirm with `list_things` for bought defs, not only `get_resources` → close idle dialog.

`food_crisis`: after resources/alerts, **always** `list_bills` on the stove (suspended + ingredient filter) before assuming no food exists.

## Open questions for a fixer

- Should decision-preset `world` ever mean unfiltered `list_world_objects`?
- Is `_dialogOpen` on `set_trade` the same class as on `window_action` (safe to continue) or a different risk?
- Does vanilla drop traded items at the trader’s feet, and should `get_resources` document that delay/haul gap?
- Is “Already working on …” an upstream float-menu label or our matcher?

---

## Follow-up reads: missing payload vs missed flag

Whether a second call was needed because the first result was incomplete, or because the first call omitted an argument / used the wrong tool. Do **not** “fix” these by adding `world` to default decision packets.

### Not a missing-field bug (wrong args or wrong tool)

- **`get_pawn` without `tab`.** Summary is documented. Needs/hediffs require `tab=needs|health` or observe pawn `include`. Selecting `/needs` on summary is a local pointer miss (`obs-42b650eee3e8451dbae266d3bc01c625`).
- **`list_trade filter=meal`.** Trader sold meat/eggs, not meals. Unfiltered `list_trade` already had alpaca meat and eggs.
- **`list_world_objects kind=caravans`.** Visiting bulk goods are map pawns, not world caravans. Empty `objects:[]` was a true empty for that kind.
- **Indoor heat via `get_conditions`.** That tool is outdoor HUD temp. Room temp is `get_room` (`id` or `x`+`z`). I used Tatyana’s Chilly thought as a proxy instead of `get_room` on the barracks.
- **Campfire fuel via `list_things verbose`.** Compact/verbose building rows still lacked fuel. `inspect_thing` is the inspect pane (fuel gizmos). I did not call it.
- **Loose traded stacks via `get_resources`.** That tool is *stockpiled* counts. Loose haulables are `list_unmanaged_items` (catalog already says after trade/raid). Not in `food` / `food_crisis` / `trade` workflows, so I never discovered it in play.
- **Reed’s Social incapability.** `list_colonists` already carries `incapableOf`. Trying `order_pawn` on Reed first was extra, not missing data.
- **Remy’s talking impairment.** Not on pawn summary; `tab=health` capacities would have shown it before trade. I did not read Remy before negotiating.
- **`--select` dropping `event_context`.** The wait had more than I kept. Do not replay the wait to recover; retrieve the wait observation without select.
- **`order_pawn` list then execute.** Menu round-trip; composition.md already says skip when the label is known.

### Real holes (first successful call still lacked a decision fact)

1. **`rw_observe` abort after `world`.** Decision include `world` hit `largeOutput` / confirm. Composition stopped (`after: now.world`) and **did not run later queries in the same request** (threat, selected pawn facets). Core/alerts/food/medical/mood/conditions from `get_status` still materialized. Fix: do not cancel sibling queries when one section is large; or map decision `world` to `kind=caravans` (etc.) so it never trips the guard. Not: default-include world.

2. **No “traders/visitors on this map” on colony reads.** After the Eragalor letter was dismissed, `get_alerts` had no active letter, `list_world_objects kind=caravans` was empty, and `get_status` / colonist bundle do not list NPC visitors. The fact lived only on `list_things category=pawn faction=any`. Worth a small dedicated read (e.g. visitors/traders on current map) or a `get_alerts`/`get_status` field — not a full world dump.

3. **`get_resources` / `list_trade.colonyCount` vs owned-but-unhauled.** After `accept`, silver/cloth in the trade UI had moved, but `get_resources` still looked pre-trade and `list_trade` showed alpaca `colonyCount: 0` while stacks sat at the trader’s feet. A human sees the piles. Fix options: `list_unmanaged_items` on the trade workflow after accept; or `colonyCount` meaning “owned including loose”; or `get_resources` pointing at unmanaged. Do not make `get_resources` a full map item list.

4. **Decision `food` is stockpile + the Low food alert only.** `composition.py` `decision_status` filters `get_resources` for meal/meat/rice/… and food-labeled alerts. It does not read `list_bills` (suspended stove) or unmanaged piles. That matches why food looked like “no ingredients” until a later `list_bills`. Adding bills (and maybe unmanaged) to the **food topic** is a bounded fix; it is not including world.

5. **`list_trade` row skip.** Compact list returned 64 of 65 and jumped over `index: 2` with no omitted-row note. I did not know whether silver/marble was missing. `returned`/`tradeableCount` exist; the missing index should be named or included.

6. **`trade_action accept` vs leftover UI.** `traded:true` plus still-open dialog and a talking-impairment `Dialog_MessageBox`. `list_trade` stayed `active`. No field for “deal committed, dismiss remaining UI.” Forced `get_window_ui` then OK then `cancel`.

7. **`get_window_ui` immediately after `order_pawn` Trade.** Inspect pane, job text “Trading with Chaz”, `list_trade` not active yet. No structured `pendingTrade` / `dialogOpen:false, walking:true`. Waiting was correct; a one-line reason would have avoided guessing whether Trade failed.

8. **`list_things faction`.** Enum is `any|player|hostile|neutral|wild`, not a faction name like Eragalor. Filtering Eragalor is impossible; `faction=any` near home was the workaround. A name/def filter (or `kind=Town_Trader`) would remove the wide pawn dump.

9. **Low food alert vs suspended bills.** Vanilla alert text does not mention bills. That is why `list_bills` felt like a surprise. Prefer putting bills in the food decision topic / food_crisis purpose string over stuffing the alert.

### Borderline (nice, not required)

- **Bed “For slaves”** inspectString unchanged — needs inspect-before/after, not a bigger default pawn read.
- **Wait `cause: notification` (corn/devilstrand died)** does not mean Reed woke or meals cooked. Event context is working; verify queries must ask for bills/jobs if that is the decision. Not a missing world map.