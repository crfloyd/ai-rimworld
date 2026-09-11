# Public tool surface

Persistent session discovery serves seven tools instead of the whole captured catalog. The proxy still knows every upstream tool; the model is not required to carry all of them. The upstream declarations cost142,785bytes in `tools/list`; the0.9.0served surface costs13,455bytes (**10.6× smaller**), including the new decision-loop schemas.

| Tool | Use |
|---|---|
| `rw_capabilities` | compact overview/domain/workflow map, name search, or one exact schema |
| `rw_read` | one read-only upstream tool by name |
| `rw_act` | one mutation or an explicitly independent fail-stop batch |
| `rw_wait` | supervised time plus event context/verification in one exchange |
| `rw_observe` | named facts or a materialized decision packet |
| `rw_guard` | read→condition→one action→verification |
| `rw_retrieve` | recover stored evidence, or resolve a reference |

Upstream names are not served directly. Start `session --expose-upstream-tools`, or set `expose_upstream_tools` in the run's campaign record, to also advertise and accept the captured catalog; saved orchestration that sends raw tool names needs that flag. The CLI `call` still accepts any name and is unaffected.

## Reads, actions and waits

`rw_read {"tool":"list_things","args":{...}}` runs one ordinary read. Effects are classified from the actual arguments, not the name: `order_pawn` without a command is a read, `set_schedule` without an assignment is a read, and `get_status` with arguments saves configuration and is refused as a mutation. A misrouted call names the tool to use instead and dispatches nothing. Denied and unclassified tools are refused in both directions. Every call still passes through the ordinary controller: ownership, unresolved requests, stale catalog, argument validation, identity binding, evidence, safety assessment and telemetry are unchanged.

`rw_act` carries ordinary orders. `set_speed` with `action` pause remains the ordinary pause and stays available while a request is unresolved, exactly as before. An accepted order is a receipt, not arrival, treatment, delivery or completed construction.

For several unrelated, already-reviewed mutations, pass `actions` and `independent:true`. Every schema/effect is checked before the first dispatch. Execution is sequential and stops after a response that reports failure, incomplete evidence or risk; `not_run` identifies untouched steps. The durable composition remains until the response is delivered. Do not put dependent actions in this form: use pawn `queue:true` for compatible job chains, or inspect an outcome before choosing the next action.

`rw_wait` wraps `wait_for_event` and injects `pause:always`, so a supervised pause is never optional. Choose a horizon; `maxGameTicks` is still clamped to the earliest recorded deadline and reported as `wait_budget`. A wait ending before its wall budget may have reached its game-time limit. An unconfirmed pause still writes the pause guard and requires review.

When a wait reports an event or risk, `context:auto` (the default) performs one post-wait status read and returns a materialized packet with core/alerts plus event-relevant food, medical, mood, threat/fire or world facets. Named medical/mood events include bounded affected-pawn health/needs; threats include current hostiles and fires include the fire list. Use `context:none` when the wait result alone is sufficient. Optional `verify` accepts the same query objects as `rw_observe`; every query is preflighted before time advances and runs after the wait in the same public exchange. Event context and verification never choose an action.

## Strategic affordances

`rw_capabilities {"overview":true}` returns the compact domain map. Use `domain` for one area or `workflow` for an ordered `new_game`, `medical_event`, `combat_event`, `caravan` or `food_crisis` guide. These contain names and one-line purposes, not schemas, live availability or permission. Fetch only a selected exact contract with `{"tool":"NAME"}`.

This overview replaces loading the complete one-line catalog at every session start. Search remains useful for a concept outside the curated map.

## Decision observations and reuse

`rw_observe` supports `preset:"decision"` with caller-selected `include` topics: `core`, `alerts`, `food`, `medical`, `mood`, `work`, `research`, `conditions`, and `world`. Add selected pawns and only the facets required. The implementation performs ordinary evidence-preserving reads but materializes one narrow packet rather than returning every bundled status field as separate sections.

`reuse:true` may skip an upstream read only when the same tool/arguments are still current in this connection. Time advancement invalidates volatile facts; mutations conservatively invalidate every prior fact. Only explicitly stable facets such as biography, schedule reads and building assignments survive a wait. Reused sections say `reused:true` and retain their original evidence. Omit reuse when a genuinely fresh capture is required.

## Views

`view` is `compact` by default; `summary` is the navigation index; `full` replays the complete stored original. `full` and `summary` read local evidence and never call the game again, so starting compact costs nothing to escalate.

Compact carries the evidence id, the game facts, risk cards and, on a repeated read of the same scope, only what changed. `rw_retrieve {"observation":"obs-…","view":"full"}` recovers everything.

## Selection and limits

`fields` selects top-level keys and `row_fields` selects columns inside row lists. Keys carrying a warning or a risk, and keys that changed, are always kept regardless of selection; everything dropped is listed in `omitted_keys`. `limit` trims whole rows and reports the true `total`.

A response that would still be very large is bounded by a serialized payload budget of32,768bytes. It returns the evidence id, `total` and `returned` counts, `truncated`, `reason` `model_payload_budget`, and the native filters available for that tool. Nothing is silently discarded: the complete response was already persisted, and `rw_retrieve` returns it in full. In2,513recorded calls this backstop never fired; it exists for an unfiltered read, not for ordinary play.

## References

One global value repeated across different subjects — a threat warning attached to every pawn read, for instance — is delivered once and afterwards referenced as `{"same_as":"th1"}`, with `refs` naming the evidence it came from. The field itself always stays present, so an appearance is never hidden, and risk kind, severity, subject and `requires_review` stay literal in every response. A changed value is never referenced, nor is anything at critical severity.

References are valid only inside the connection that minted them. They are cleared on reconnect and on any presentation reset, so a reference never has to be interpreted across sessions. Small values remain literal when a reference would not be materially shorter. The original value always remains in evidence: `rw_retrieve {"ref":"th1"}` returns it literally, and an unknown reference is an error rather than a guess.

## Token-Efficient Agent Guidance

- Never request the whole map when a bounded query answers the question. `list_things` accepts category, defName, faction, nearId or nearX/nearZ with radius, and limit; `get_area` accepts explicit bounds. Filtering at the source is faster than fetching and discarding.
- Pull `rw_capabilities {"overview":true}` once when strategic affordance awareness is needed, or request one domain/workflow. Fetch an exact schema only for a selected action. Do not load the full catalog by default.
- Keep the default compact view. Escalate to `full` only when compact is genuinely insufficient — it is a local replay, not another game call.
- Select `fields`/`row_fields` when only part of a response matters, and pass `limit` when a list is expected to be long.
- Prefer `rw_wait` over repeated reads to see whether something finished. One finite event-driven wait replaces a polling loop.
- For a reviewed sequence of compatible pawn jobs, send the immediate `order_pawn` normally and append later jobs with `queue:true`. This is the Shift-click queue and can remove intermediate stop/reissue cycles. Do not queue unstable combat, urgent medical work or steps whose validity depends on an earlier outcome; a queue receipt is not completion evidence.
- Repeated reads of one scope return only what changed; re-reading a stable scope is cheap, and re-reading everything to be sure is not.
- Compact responses omit nothing silently. `omitted_keys`, `truncated` and `same_as` each name their recovery path; act on the report rather than re-issuing the call.
