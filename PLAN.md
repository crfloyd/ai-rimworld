# Current implementation plan — token-efficient facade

User-approved scope: a small stable public MCP surface over the captured RimMolt catalog, compact model-facing responses with explicit selection and limits, a configurable payload budget, connection-scoped references for repeated global values, and unchanged full-fidelity evidence. No snapshot or query-engine concept in this change set.

The model sees seven tools; the proxy still knows all113. Upstream names are reachable by name through rw_read/rw_act and discoverable through rw_capabilities, but are not advertised and not served directly unless `session --expose-upstream-tools` is set. Control.call remains the sole game path and the authority on permission, ownership, pause, evidence and telemetry; the facade only narrows and shapes.

Delivered: facade module and dispatch, argument-dependent read/act/wait gates with the emergency pause route preserved, compact/summary/full views replayed from evidence, fields/row_fields projection with forced retention of warning/risk/changed keys, caller limit and a32,768-byte payload budget with explicit truncation reporting, value-keyed references with reset invalidation, the exposure flag, CLI routing, per-call driver telemetry, and a --facade mode in compare_views.

Validation: 227 offline tests, byte-budget assertion on the served surface, and a2,513-call offline replay from stored evidence. Public-call telemetry now covers all seven facade tools and attributes composed subcalls separately. Numbers and their limits are in VALIDATION.md.

Status: implementation, tests, benchmarks and documentation complete. A first live adoption test stopped safely after7,608ticks on a corrected argument-dependent classification defect; the next validation is a fresh one-day continuation from the paused state.
