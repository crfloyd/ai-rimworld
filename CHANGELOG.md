# Changelog

## 0.9.1

- An upstream large-output guard or truncation flag no longer cancels the rest of a composition. The affected section is marked `degraded` with structured `retry` advice naming both exits, narrowing filters and `confirm:true`, while every sibling query still runs. Unconfirmed pause, identity mismatch, unparseable JSON, upstream errors and missing or malformed fields keep their original hard stop.
- The decision preset reads `list_world_objects` with `kind` defaulting to `caravans` and gains a `visitors` topic over neutral map pawns, which is where a visiting trade caravan actually is. Automatic wait context uses the same narrow world read and adds map visitors. The `food` facet now states that suspended bills and loose piles are outside it.
- Receipts carry facade interpretation alongside unedited upstream fields: an `order_pawn` refusal whose only offered option is the already-running form of the same job reports `already_satisfied` and no longer aborts an independent batch; `list_trade` names rows upstream counted but withheld; an accepted `trade_action` states whether the deal committed, whether a dialog is still open, and how to confirm goods that landed on the ground.
- Event context is chosen from the event narrative rather than from a substring match over the whole serialized body, so a standing threat warning no longer re-triggers a full pawn and responder sweep on every later wait. `rw_wait` gains `context:"brief"` for the status packet without that sweep.
- Capability domains now cover all 112 permitted catalog tools, up from 54. The default overview is a domain index of about 2,000 bytes rather than a 12,000-byte tool map; `domain`, `workflow` and `overview` with `full:true` drill in. Workflows carry operational notes, trade begins at finding the trader and ends at confirming delivered goods, food_crisis reaches bills before concluding there are no ingredients, and a new `build_structure` workflow explains interaction-spot placement refusals.
- The `capabilities` CLI subcommand serves `--overview`, `--full`, `--domain` and `--workflow`, matching the MCP tool. Argument mistakes return one JSON object naming the sibling command's flags instead of a usage dump, and a failed `--select` suggests real JSON Pointers from the response it received.

## 0.9.0

- Fixed automatic wait event context generating invalid `get_pawn tab=summary`; all pawn facets now share one expansion. Optional post-wait enrichment errors preserve the completed paused wait as partial/no-replay. Resume defaults to one-shot CLI unless the host supports interactive stdin, and unknown compositions expose a concrete reconciliation template.
- Handoffs are now one replaceable compact transfer checkpoint rather than an immutable snapshot chain. They retain bounded current pointers and journal offsets without copying fact/knowledge bodies. Authorized memory compaction removes legacy copies and retains only selected current action tracking without claiming retired gameplay outcomes completed.
- Current memory is now explicitly present-tense rather than chain-of-custody: informal STRATEGY supports several planning horizons and event-driven coalesced updates, ISSUES renders short action cards with full ID retrieval, and optional STATE is a bounded evidence index instead of a nested historical dump.
- Fresh resume now returns controller-aware command templates and pointer-based checkpoint metadata by default; the compact checkpoint body requires `--full-output`. Strategy guidance forbids appending old handoff bodies because indexed journals already preserve evidence history.
- Decision observations add a general threat facet and `resume_crisis` workflow; capability misses suggest close tool names, upstream pawn summary is documented as an omitted tab, and controller docs distinguish cached session metadata from a live process.
- Every live player must read the audited operational `docs/facade.md` before its first facade call and after tooling changes; historical benchmark material was removed from that guide.
- Onboarding, memory, control, history and knowledge guidance now agree on self-contained facade reads, local full retrieval, compatibility-only raw calls, conventional model-facing rows and model-handover-first efficiency. Offline spatial selections also return ordinary row arrays.
- Compact reads are self-contained by default with separate change metadata. Delta-only output now requires `delta:true` plus an explicit same-scope `since` observation, preventing empty automatic responses when callers need current state.
- Capability discovery adds a semantic trade domain/workflow, and trade-window reads lead with `list_trade`/`set_trade`/`trade_action` guidance instead of encouraging generic button scraping.
- One-shot `call`/`observe`/`guard` commands add repeatable JSON-Pointer `--select`; local selection failures report completed-operation evidence and no-replay guidance. Shell guidance forbids `echo` round-trips that corrupt escaped JSON and requires one-pass parsing.
- Caller-bounded partial results keep usable facts under `data`; successful same-dialog window batches tolerate only their expected persistent dialog flag; mental-break packets include the letter, affected pawn facets and nearby responders; verification manifests record requested and actual calls.
- Model-facing row collections are conventional arrays of objects; lossless columnar packing is internal only, avoiding decoder failures and recovery calls during live decisions.
- Presets always preserve the caller's exact key: one facet returns its section there, while multiple facets nest by name instead of inventing dotted top-level keys.
- `rw_capabilities` adds compact domain overviews and staged workflow maps so the model can see strategic affordances without loading113 schemas.
- `rw_observe` adds a materialized decision preset for selected core, alerts, food, medical, mood, work, research, conditions, world and pawn facets; opt-in reuse skips only connection-cached reads still valid under conservative wait/mutation invalidation.
- `rw_wait` defaults to a compact post-event decision packet and accepts preflighted verification queries in the same exchange, reducing wait→read handovers. `context:none` preserves the prior response path.
- `rw_act` accepts pre-reviewed action arrays only with `independent:true`, preflights the complete batch, executes sequentially, stops on a reported problem and retains durable delivery evidence. Pawn `queue:true` remains the preferred dependent job-chain mechanism.
- Reference substitution now skips small values when the reference plus metadata would be larger.

## 0.8.0

- Live play now defaults to the current agent directly rather than a coordinator-delegated player. Guidance biases toward focused observations and the longest prudent event-driven wait while explicitly requiring closer attention whenever threats, medical deadlines, mood/food crises, caravan transitions, ambiguity or unfamiliar mechanics warrant it; delegation remains optional for bounded offline work.
- Sparse-play guidance and the public action description now surface `order_pawn queue=true` for safe Shift-click-style job chains, with explicit exclusions for unstable tactical, medical and outcome-dependent sequences.
- Session discovery serves seven local tools instead of the whole captured catalog: rw_capabilities, rw_read, rw_act, rw_wait, rw_retrieve, rw_observe and rw_guard. Advertised tool declarations fall from142,785to9,613bytes.
- The113upstream tools remain reachable by name through rw_read/rw_act, with rw_capabilities returning ranked names for a query and one exact schema per selected tool.
- Read and mutation are separated by the actual arguments, not the tool name; a misrouted call names the tool to use and dispatches nothing. Ordinary controller guards, evidence, safety assessment and telemetry are unchanged.
- rw_wait injects pause always over wait_for_event; existing budget clamping and pause-guard repair are untouched.
- Compact responses by default, with summary and full views replayed from stored evidence without another game call. fields/row_fields selection and limit report every omission; keys carrying warnings, risks or changes are never dropped.
- A32,768-byte model payload budget bounds an unfiltered read, reporting evidence id, total, returned, truncated, reason and the native filters for that tool. Nothing is silently discarded.
- One global value repeated across subjects is delivered once and then referenced; references are connection-scoped, cleared on reconnect or presentation reset, and always resolvable from evidence.
- Upstream names are no longer served directly; session --expose-upstream-tools restores the previous surface and dispatch for saved orchestration.
- Telemetry records a driver per call, so facade and legacy paths separate in metrics. Composed subcalls are tagged as `facade_observe`/`facade_guard`, and a public-call journal measures all seven local tools—including offline capability/retrieval calls—with exact model-facing text-response bytes. compare_views gains --facade and per-tool totals.

## 0.7.0

- Shared composed reads exposed as rw_observe and CLI observe, with selected pawn/production presets and explicit queries.
- Agent-authored rw_guard performs bounded fresh reads, typed conditions, at most one literal action, and optional immediate verification reads. Unknown/partial/ambiguous input abstains.
- Durable composition manifests cover subcall/delivery gaps and participate in inspection, handoff, pause and reconciliation.
- Full valid game data, media and unfamiliar properties retained; duplicate/nonfinite JSON cannot trigger a guard.
- Removed duplicate CLI-only observe execution, inert ui preparation command, stale monitor/P8 tasks and accumulated presentation instructions. Historical records remain supported.

## 0.3.1

- Correct lowercase/verbose pawn coverage against the captured real RimMolt catalog.
- Indexed latest-scope storage with atomic replay checkpoints; no full projection rewrite per varied query.
- Compact medical risk cards, lean CLI observation presentation, and no duplicate controller risk bodies.
- Typed review deadlines and missing action-index recovery repaired.
- Recognize actual bleedRatePerDay and status-carried damage deltas.
- Independent audit regressions and offline response-comparison tool; live lab evidence is recorded separately.

## 0.3.0

- Compartmentalized run learning and pinned shared adoptions; explicit reviewed promotion.
- Correct query scopes, tool/tab shapes, full-health medical detail, source/session/clock/dispatch freshness and live action evidence.
- True deltas, indexed observations, incremental active-work views, focused packets and immutable run handoffs.
- Decision/outcome/incident/candidate learning flow; explicit same-game action and clock reconciliation.
- Reusable outcome contracts, grouped observations, Critical/bundle-aware danger checks and typed hard deadlines.
- Finite routine continuation with an independent pause-only guardian, pause repair, stop requests, terminal lease reconciliation and preserved request handles.
- Versioned automatic telemetry, scenario regressions, scalable-history benchmark, and stricter screenshot/run/link integrity.
- No live game or mod changes; live integration and end-to-end improvement remain to be measured.

## 0.2.0

Named-run startup and intake: root instructions route to a topology and player-question guide; supplied answers and explicit delegation take precedence over additional questions. Campaign templates retain answer sources and distinguish player decisions from technical checks. Approved-profile guidance adds no automatic preset.

Added offline runs/list, new and resume commands, --run as an explicit --campaign alias, and small generated run summaries. Initialization refuses duplicate or symlinked compartments; new refuses recorded unanswered questions. Resume never loads a game or changes global selection. Twelve additional tests pass; live deployment checks remain pending.

## 0.1.0

Initial reusable support system: thin MCP client, guarded control, explicit observation uncertainty, campaign projections, selective retrieval, consequential-action tracking, persistent issues, reviewed knowledge, original screenshot and checkpoint workflow, and offline validation/demo tools.

Live game integration is not claimed by this release. See VALIDATION.md for exact evidence and pending deployment checks.
