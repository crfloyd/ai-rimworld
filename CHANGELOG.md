# Changelog

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
