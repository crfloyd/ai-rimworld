# Current implementation plan — composed observations

User-approved scope: one discoverable composed-read interface, two small selection presets (pawn/production), preserved ordinary tools/evidence, and bounded explicit conditional action for recurring sequences. Remove superseded entry points and stale instructions. No strategic diagnosis engine or automatic time continuation.

Implementation is isolated from the live checkout until the active player finishes its current request, verifies pause, saves a reconciled handoff and releases control. One integration owner; no game calls during development.

Implemented candidate: rw_observe/CLI observe share expansion, preflight and result mapping. rw_guard reads explicit conditions, dispatches at most one literal branch and optionally reads immediate verification. Unknown/ambiguous/partial/unpaused/interrupted input abstains. Durable composition marker covers subcall and delivery gaps; original request guards remain. Local discovery includes both tools. Original facts, extra fields and media remain available.

Cleanup: remove duplicate CLI-only observation execution, inert ui preparation command, stale monitor/P8 TODOs and accumulated presentation-change instructions. Keep distinct supported batch/outcome/knowledge/continuity features and original campaign records. Git preserves old source history.

Validation: focused fake-server tests for expansion, schema/effect preflight, full data/media, malformed JSON, nested partial coverage, branches, pause/identity/interruption, process/output failure and recovery. Run the existing suite. Replay representative saved reads to measure combined query/response size and model handovers without live calls. Independent code review before integration.

Adoption: after deployment, a fresh player receives ordinary resume instructions and discovers the advertised tools without a private walkthrough. Compare useful outcomes, total context and decision handovers; do not infer intelligence from fewer RPCs or ticks alone. Higher-level views must earn their place; partial results never certify safety. Current state stays one reconciled campaign strategy, with history on disk.
