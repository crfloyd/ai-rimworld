# Public tool surface

Read this guide completely before the first live facade call in a play session and again after a tooling/version change. It contains only operational behavior a fresh player needs. Historical measurements and implementation evaluation belong in `VALIDATION.md`.

Persistent session discovery serves seven tools instead of the whole captured catalog. The proxy still knows every upstream tool, while the model loads only a compact affordance map and selected exact schemas.

| Tool | Use |
|---|---|
| `rw_capabilities` | compact overview/domain/workflow map, name search, or one exact schema |
| `rw_read` | one read-only upstream tool by name |
| `rw_act` | one mutation or an explicitly independent fail-stop batch |
| `rw_wait` | supervised time plus event context/verification in one exchange |
| `rw_observe` | named facts or a materialized decision packet |
| `rw_guard` | read→condition→one action→verification |
| `rw_retrieve` | recover stored evidence, or resolve a reference |

Upstream names are not served directly. Ordinary play must use the facade. `--expose-upstream-tools` exists only for explicitly authorized legacy compatibility/testing; do not enable it merely to avoid facade discovery or shaping.

## Reads, actions and waits

`rw_read {"tool":"list_things","args":{...}}` runs one ordinary read. Effects are classified from the actual arguments, not the name: `order_pawn` without a command is a read, `set_schedule` without an assignment is a read, and `get_status` with arguments saves configuration and is refused as a mutation. A misrouted call names the tool to use instead and dispatches nothing. Denied and unclassified tools are refused in both directions. Every call still passes through the ordinary controller: ownership, unresolved requests, stale catalog, argument validation, identity binding, evidence, safety assessment and telemetry are unchanged.

`rw_act` carries ordinary orders. `set_speed` with `action` pause remains the ordinary pause and stays available while a request is unresolved, exactly as before. An accepted order is a receipt, not arrival, treatment, delivery or completed construction.

For several unrelated, already-reviewed mutations, pass `actions` and `independent:true`. Every schema/effect is checked before the first dispatch. Execution is sequential and stops after a response that reports failure, incomplete evidence or unexpected risk; `not_run` identifies untouched steps. A successful `window_action` may continue on the same dialog when the unchanged `_dialogOpen` flag is its only review signal—the open window is required for the remaining fields. A changed/closed window, unapplied action or any other warning still stops. The durable composition remains until delivery. Do not put dependent actions in this form: use pawn `queue:true` for compatible job chains, or inspect an outcome before choosing the next action.

`rw_wait` wraps `wait_for_event` and injects `pause:always`, so a supervised pause is never optional. Choose a horizon; `maxGameTicks` is clamped to the earliest recorded deadline and reported as `wait_budget`. RimWorld may cross a requested tick bound by a few simulation ticks, so do not create tiny terminal waits for exact clock arithmetic. A wait ending before its wall budget may have reached its game-time limit. An unconfirmed pause writes the pause guard and requires review.

When a wait reports an event or risk, `context:auto` (the default) performs one post-wait status read and returns a materialized packet with core/alerts plus event-relevant food, medical, mood, threat/fire or world facets. Event pawn matching accepts IDs, full names and unambiguous name/nickname tokens. Mental-break threats include the event letter, affected health/needs/gear and nearby pawn positions/readiness around the hostile pawn; ordinary threats include current hostiles and fires include the fire list. Use `context:none` when the wait result alone is sufficient. Optional `verify` accepts the same query objects as `rw_observe`; every query is preflighted before time advances and runs after the wait in the same public exchange. The durable manifest records requested and actual verification tool/arguments plus reuse. Event context and verification never choose an action.

## Strategic affordances

`rw_capabilities {"overview":true}` returns the compact domain map. Use `domain` for one area or `workflow` for an ordered `new_game`, `medical_event`, `combat_event`, `caravan`, `food_crisis` or `trade` guide. These contain names and one-line purposes, not schemas, live availability or permission. Fetch only a selected exact contract with `{"tool":"NAME"}`. When `get_window_ui` detects a trade dialog, the facade also reads a bounded semantic `list_trade` view, leads with that state and the dedicated list/set/finalize tools, and reduces generic UI geometry to control counts; full window evidence remains locally retrievable.

This overview replaces loading the complete one-line catalog at every session start. Search remains useful for a concept outside the curated map.

## Decision observations and reuse

`rw_observe` supports `preset:"decision"` with caller-selected `include` topics: `core`, `alerts`, `food`, `medical`, `mood`, `work`, `research`, `conditions`, and `world`. Add selected pawns and only the facets required. The implementation performs ordinary evidence-preserving reads but materializes one narrow packet rather than returning every bundled status field as separate sections.

`reuse:true` may skip an upstream read only when the same tool/arguments are still current in this connection. Time advancement invalidates volatile facts; mutations conservatively invalidate every prior fact. Only explicitly stable facets such as biography, schedule reads and building assignments survive a wait. Reused sections say `reused:true` and retain their original evidence. Omit reuse when a genuinely fresh capture is required.

## Views

`view` is `compact` by default; `summary` is a navigation index; `full` returns the complete original for the new live capture. Any `rw_read` view still contacts the game. To escalate an already-captured compact result without another game call, use `rw_retrieve {"observation":"obs-…","view":"full"}`.

Compact reads are self-contained by default. General reads use `data`; pawn health/needs and status may use their named `health`, `needs`, or `status` container. Usable partial general results remain under `data`. Optional `change` metadata reports whether the same scope was unchanged and names its previous evidence. Never assume a successful read is an automatic delta.

Delta-only reads are explicit: pass both `delta:true` and `since:"obs-…"`. The base must be a complete observation from this session with the same tool and arguments; otherwise the request is rejected before contacting the game. Explicit deltas use compact view and may return empty `data` with `unchanged:true` because the caller deliberately supplied the baseline. `rw_retrieve {"observation":"obs-…","view":"full"}` recovers complete stored evidence.

Model-facing row collections are ordinary JSON arrays of objects. Internal evidence may use lossless columnar packing, but callers never need a decoder merely to iterate, index or slice a result. Speed takes precedence over small byte savings when a conventional bounded response is likely to prevent another model handover.

Usable partial or caller-bounded results also stay under `data`; `completeness`, coverage, matched/returned counts and `truncated` describe their limits. The primary container never switches to `known_subset` merely because a requested limit returned only the nearest/top rows.

## Selection and limits

`fields` selects top-level keys and `row_fields` selects columns inside row lists. Keys carrying a warning or a risk, and keys that changed, are always kept regardless of selection; everything dropped is listed in `omitted_keys`. `limit` trims whole rows and reports the true `total`.

A response that would still be very large is bounded by a serialized payload budget. It returns the evidence id, `total` and `returned` counts, `truncated`, reason, and native filters where known. Nothing is silently discarded: the complete response was already persisted, and `rw_retrieve` returns it in full.

## References

One global value repeated across different subjects — a threat warning attached to every pawn read, for instance — is delivered once and afterwards referenced as `{"same_as":"th1"}`, with `refs` naming the evidence it came from. The field itself always stays present, so an appearance is never hidden, and risk kind, severity, subject and `requires_review` stay literal in every response. A changed value is never referenced, nor is anything at critical severity.

References are valid only inside the connection that minted them. They are cleared on reconnect and on any presentation reset, so a reference never has to be interpreted across sessions. Small values remain literal when a reference would not be materially shorter. The original value always remains in evidence: `rw_retrieve {"ref":"th1"}` returns it literally, and an unknown reference is an error rather than a guess.

## Fast decision-loop guidance

- Optimize first for avoiding another model handover, then for serialized bytes. Prefer one sufficient bounded response over several tiny reads or a representation requiring custom decoding.
- Use one persistent session for repeated play. One-shot CLI calls reload code but cannot reuse connection-scoped references/cache.
- Never request the whole map when a bounded query answers the question. `list_things` accepts category, defName, faction, nearId or nearX/nearZ with radius, and limit; `get_area` accepts explicit bounds. Filtering at the source is faster than fetching and discarding.
- Use `rw_capabilities {"overview":true}` when broad strategic affordance awareness is needed, or request one domain/workflow. Fetch an exact schema only for a selected action. Prefer semantic tools such as `list_trade` over generic UI scraping.
- Keep the default compact view. If it is insufficient, retrieve the same observation in full locally instead of repeating the game read.
- Select `fields`/`row_fields` when only part of a response matters, and pass `limit` when a list is expected to be long.
- Use a bounded `rw_observe` decision preset when one decision needs several related domains. Presets preserve the caller key: one facet is `sections.KEY.data`; multiple facets are nested at `sections.KEY.FACET.data`.
- Prefer `rw_wait` over polling. Let its automatic event context supply likely follow-up facts; add preflighted `verify` reads when they will be needed regardless of how the wait ends. Read again only for facts the packet genuinely lacks.
- Batch unrelated, pre-reviewed mutations with `rw_act actions[]` and `independent:true`. A same-dialog window batch may continue only while successful actions remain on the same expected dialog and `_dialogOpen` is the sole review signal.
- For a reviewed sequence of compatible pawn jobs, send the immediate `order_pawn` normally and append later jobs with `queue:true`. This is the Shift-click queue and can remove intermediate stop/reissue cycles. Do not queue unstable combat, urgent medical work or steps whose validity depends on an earlier outcome; a queue receipt is not completion evidence.
- Repeated reads remain self-contained unless the caller explicitly supplies `delta:true` and `since`. Prefer opt-in cached reuse for stable facts over automatic empty deltas.
- Model-facing row collections are ordinary arrays. Do not write a columnar decoder. Partial/bounded facts remain usable under `data`; honor their explicit completeness, coverage and truncation metadata.
- For one-shot CLI extraction, use repeated `--select /json/pointer` options. Never pass captured JSON through shell `echo`; if capture is unavoidable, parse it once with raw `printf '%s'`.
- Keep game-operation success separate from local selection/parsing failure. A completed mutation or wait is never replayed to fix local formatting.
- Compact responses omit nothing silently. `omitted_keys`, `truncated` and `same_as` name recovery paths; use them instead of blindly reissuing the call.
- These are defaults, not call quotas. Combat, fire, bleeding, infection races, mental breaks, food collapse, caravan transitions, ambiguous receipts, partial coverage and unfamiliar mechanics justify shorter waits and deeper observation.
