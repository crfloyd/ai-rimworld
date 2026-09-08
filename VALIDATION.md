# Validation —0.6.0 candidate

173 offline tests pass. Independent review reproduced and then verified fixes for array-root visibility, interrupted delivery and preserved protocol notifications. Offline tests cover ownership/identity, original evidence and unknown-field retention, no uncertain replay, hard deadlines/paused waits, raw/media forwarding, persistent MCP protocol, and lost-output/EOF failures. The isolated cleanup removes the unproductive finite monitor and its qualification/acknowledgement tests, not the request/pause safeguards. Run tools/check.py for current results.

The [fresh-agent experiment](docs/PLAY-LOOP-EXPERIMENT.md) remains the measured baseline. It did not prove combat, compaction recovery or improved win rate. Persistent-transport timing and a new frozen play/resume trial are required before performance claims.

Historical lab reports and obsolete validation snapshots are removed from the working tree. Git retains them; original run evidence stays in the selected campaign. No game/mod/save changes are part of this cleanup.
