# Composed observations and guarded actions

These are local tools served by `session` and `capabilities` as part of the small public surface described in [facade](facade.md). They use the same owned ordinary calls, evidence journal and uncertainty guards as individual tools. They do not install a game mod or infer strategy.

## Ask for related facts once

Use `rw_observe` through the persistent MCP session, or `./rw --run NAME observe --json JSON --token TOKEN` (`--file FILE` also works). CLI and MCP share one implementation. The universal `call rw_observe --args JSON` / `call rw_guard --args JSON` forms route to that same engine; do not use tracking/setup flags with these local tools.

```json
{"queries":[
  {"key":"worker","preset":"pawn","id":"Human123","include":["summary","needs","health"]},
  {"key":"stove","preset":"production","id":"FueledStove456","worker_id":"Human123","include":["station","bills","work_options"]}
]}
```

Use real current IDs. `key` is the caller's label, not name resolution, and every preset preserves it. A single facet returns one section at that key (`sections.bywa.data`); multiple facets nest by name (`sections.tat.summary.data`, `sections.tat.gear.data`, `sections.tat.health.data`). Explicit queries remain flat at their exact keys. Each leaf section has full `data` from the first JSON text block. The response gives a composition evidence ID and sequential capture interval; its manifest retains each expanded section's individual observation ID, time and coverage. Use `provenance:true` (CLI `--full-output`) to include those per-section details inline. Incomplete coverage and skipped queries are always visible. Other content/media, text annotations and unfamiliar result properties remain present. Raw originals and the expanded recipe are retained in the campaign. Malformed/ambiguous JSON is explicitly unusable rather than actionable; original evidence is retained.

| Preset | Default | Optional include sections |
|---|---|---|
| pawn, with id | summary | summary, needs, health, gear, bio, schedule |
| production, with id | station, bills | station, bills, recipes, resources, worker, work_options |
| decision | core, alerts | core, alerts, food, medical, mood, threat, work, research, conditions, world; optional selected pawn facets |

Decision example:

```json
{"reuse":true,"queries":[{"key":"recovery","preset":"decision",
  "include":["core","alerts","food","medical","mood","threat"],
  "pawns":[{"id":"Human123","include":["health","needs"]}],"mood_below":35}]}
```

The result places the materialized packet under `decisions.recovery` and retains its evidence IDs. With `threat`, the nearby pawn read is anchored on the first selected pawn when supplied; include that pawn's summary/health/needs/gear when a current crisis needs them. Expanded raw sections are not duplicated in the default response. `reuse:true` is conservative and connection-scoped: waits invalidate volatile facts and mutations invalidate all prior facts; reused sections are labeled. Use a normal explicit query when an exact full response is the decision input.

`detail:true` adds the game's hover details only to requested pawn needs/health. Production worker/work_options require worker_id. Resources are the game's aggregate resource result, not proof of reachable/unreserved ingredients. There is no invented work-priority getter. Recipes use actual list_recipes; recipe presence does not guarantee the chosen worker can perform it. Schedule uses the documented read form of set_schedule without assignment.

For another capability, include an explicit ordinary read:

```json
{"queries":[
  {"key":"local_layout","tool":"get_area","args":{"minX":120,"maxX":130,"minZ":110,"maxZ":120,"render":"ascii","layer":"buildings"}},
  {"key":"weather","tool":"get_conditions","args":{}}
]}
```

Presets select information; they are not an outcome whitelist. Unknown preset sections/invalid arguments fail preflight before any game call. Explicit reads still use the current captured tool contract and reviewed effect classification. At most32 expanded reads per request. Choose a narrow query; do not request every section by default.

Captures are sequential, not atomic. No game-time advancement is requested, but normal reads can change UI selection and external clients can change state. Coverage/identity/pause problems stop remaining reads, which are listed under not_run. Partial bundled observations are also reported. Omitted sections remain unqueried, not healthy/empty. Direct tools remain available.

`rw_wait verify` accepts these same query objects and preflights their expanded reads before time advances. Pawn `summary` omits upstream `tab` in every path. If optional post-wait read-only enrichment fails locally after a durable paused wait, the facade returns the completed wait with `event_context_error`, `requires_review` and `no_replay`; it does not turn the wait itself into an unknown operation.

## Preselect one conditional action

Use `rw_guard`, or `./rw --run NAME guard --json JSON --token TOKEN`, only when the agent has already chosen the rule and its action (plus an optional otherwise action). It is not a readiness or safety verdict. If interpretation is still needed, use rw_observe and reason before acting.

Example: the agent has already decided a particular bed should return to ordinary use after patient recovery. Toggle only if its Medical setting is still on; then inspect the actual result.

```json
{"queries":[{"key":"bed","tool":"inspect_thing","args":{"id":"Bed123"}}],
 "when":[{"source":"bed","path":"/actions","match":{"label":"Medical","disabled":false},"field":"/active","op":"eq","value":true}],
 "then":{"tool":"do_thing_action","args":{"id":"Bed123","label":"Medical"}},
 "verify":[{"key":"bed_after","tool":"inspect_thing","args":{"id":"Bed123"}}]}
```

Predicates use RFC6901 JSON Pointers into section data. `match` optionally selects exactly one array row by exact fields; `field` then addresses that row. Supported comparisons: eq/ne/lt/lte/gt/gte. All predicates must be true for then. Known false chooses an explicitly supplied otherwise command, or does nothing. Missing values, type mismatches, duplicate matches, partial/bundled-incomplete data, unconfirmed pause and reported interruptions cause no action in either branch. False and numeric0 are distinct. No fuzzy action selection or name guessing.

Branches are literal ordinary tool/args objects. They are preflight-validated before reads, use existing game permission/effect checks, and execute at most one mutation. No waits, speed changes, setup, loops, dynamic targets, nested compositions or automatic retries. New warnings/events, including threat warnings and extra unparsed content, require review. Current low health/mood is a fact, not automatically a veto; the agent must choose sufficient conditions for its intended action. Unknown fields are retained, not interpreted by a policy engine.

The returned action is a receipt, not proof of completion. Optional verify queries read immediate consequences without advancing time. Treatment, hauling and other jobs may require later game time and ordinary outcome checks. For a known right-click command, ordinary order_pawn can already execute the offered label directly; do not add a menu round trip merely for ceremony. Use a guard when an explicit condition/unique enabled option needs checking first.

## Interrupted composition

A durable composition.json covers the interval between subcalls and output delivery. Its campaign-local manifest records the recipe, child evidence and any action receipt without copying full response bodies. The existing pending.json still covers the current server request. Other calls/release are blocked while a composition is unfinished; ordinary emergency pause preserves both records.

A successful stdout flush clears the composition marker internally; there is no user acknowledgement workflow. On process/output failure, use controller inspect and the original manifest/handle. Reconcile only after ALL original subrequests and the originating process are terminal and their outcomes reviewed. Never resend the whole guard to discover whether its action happened. A host silently dropping output after a successful flush remains a delivery limitation, not replay permission.
