# Validation — version 0.3.1

The independent audit repairs and live lab are documented in [LAB-2026-09-08.md](docs/LAB-2026-09-08.md). The original [audit](docs/AUDIT-2026-09-08.md) is preserved. Earlier 0.3.0 claims and source remain in the [pre-lab tooling archive](releases/pre-lab-0.3.0-20260908.tar.gz).

## Verified

- `python3 -B tools/check.py`: 124 offline tests plus syntax, JSON and local Markdown-link checks.
- A01–A05 reproductions now pass: real pawn schema/coverage, varied-scope persistence, medical delta size, review deadline scheduling and missing action-index reconstruction.
- 5,000 distinct queries: first/final ingestion medians 4.22/3.55 ms. The 20.9 MB derived index retains all scopes; the 409-byte export is not the whole stored state.
- Replay of 30 real responses: old runner 64,812 bytes, lean runner 21,410 bytes, base MCP 34,426 bytes. This is the named sequence, not a promise that every read shrinks.
- Actual paused Continuance session: ordinary short waits returned with pause confirmed; real separate guardian started and stopped; final monitor coverage had zero gaps and made zero waits because medical/needs risks remained.
- Real action tracking kept treatment unfinished after acceptance, then completed it only when every acute injury satisfied the explicit check. Relevant original-run lessons were retrieved and an observed outcome added to a run-local lesson.
- Full evidence retrieval remains full. Monitor/handoff resets prevent deltas from depending on unseen internal reads.

The lab additionally fixed explicit-zero fire responses, actual bleedRatePerDay, status-carried damage deltas, draft receipts without ok:true, duplicate control assessments, lossless list patches and oversized monitor handbacks.

## Limits

Byte counts are not exact model tokens. Live timing excludes model reasoning, host orchestration and approvals. First reads carry small evidence-reference overhead; full retrieval intentionally preserves detail. Simple repeated-status processing can cost about a millisecond more locally even though varied-query growth is improved.

Not verified live: worker/OS/server failure recovery, competing controllers, a healthy multi-cycle routine interval, a new raid/combat trial, new-colony startup, DLC/map transition, or a five-day illustrated chapter. No victory or win-rate improvement is established. The monitor remains conservative around downed pawns and low needs; future tuning needs medical/job trajectories and real false-interruption measurements, not blindly relaxed thresholds.

No debug/developer commands, game-state file edits, reloads, balance changes or mod edits were used. The existing game is preserved and paused at the lab handoff. The original colony objective remains unfinished.
