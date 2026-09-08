# RimMolt API review — 8 September 2026

This reference supports decisions about intelligent, efficient play. It inventories the captured API rather than treating the runner's existing capabilities or outcome templates as the limits of the game. The colony was not contacted or advanced during this review.

## Read selectively

- [Full API reference](API-REFERENCE.md): every catalog tool, exact declared inputs, observed response variants, and implementation pointers.
- [Machine inventory](inventory.json): nested response field paths/types, counts, provenance, source registrations, and explicit coverage gaps. This is evidence, not a strict generated output validator.
- [Shared transport and model behavior](MODELS.md): envelopes, side effects, event limitations, and dynamic output.
- [Runner findings and recommended design](RUNNER-REVIEW.md): what can be lost today and how to avoid limiting reasoning to predefined outcomes.
- [Offline probes](evidence/runner-probes.json): reproducible demonstrations of unknown-field handling in runner 0.3.1. The invented fields are tests, not reported game hazards.
- [Provenance](evidence/provenance.json): installed assembly, catalog, runner files, decompilation tool and evidence hashes.

The saved corpus contains 2,224 evidence records after merging 30 matching RPC overlaps. Sixty-nine tools have standalone observations; 44 do not. All 113 tools have source registration/handler pointers.

Do not load the full reference in routine play. Find a tool in the index and retrieve its entry and relevant model notes. Before consequential decisions, retrieve the actual current records and applicable lessons. API availability is not evidence that an action is legal for this run, currently enabled, or strategically useful.

## What “complete” means here

The captured catalog contains 113 tools. Every declared input is retained. None declares an output schema or tool annotations. Recorded responses and the installed implementation extend the picture, but cannot establish all future values, mod integrations, reflected UI controls, or every runtime branch. Observed requiredness must never be inferred from presence frequency. Empty arrays supply no element model.

The decompiled implementation is preserved for inspection, with tool handlers mapped by the inventory. It is derived from the installed DLL, not original authored source and not a verified rebuild. Missing game assembly references produce some decompiler warnings. Source extraction and spot review are explicitly different from manually validating every handler branch in the game. The catalog capture and currently installed DLL are separately fingerprinted; a current disk assembly is not proof of the exact bytes previously loaded by the game process.

A subagent built the catalog/corpus/handler inventory. The primary agent independently reviewed shared server behavior and the runner, reproduced information-loss cases, and checked the integrated inventory. No runner behavior or game/mod/save/configuration files were changed by this review.

## Reproduce this snapshot offline

The generator is specific to the captured Continuance corpus; it does not select or control a live campaign. Run from the project root into a fresh temporary output directory:

```sh
python3 -B docs/api/generator.py --root . --source docs/api/evidence/decompiled --out /tmp/rimmolt-api-regenerated
```

Compare inventory.json and API-REFERENCE.md with the saved copies. A changed campaign corpus intentionally changes the generated result; use the recorded source hashes when comparing this historical review. The generator performs no network or game calls. Decompiled sources are evidence only: do not build or install them.

[Validation results](evidence/validation.json) confirm exact 113-tool coverage, handler pointers, byte-identical regeneration, local links and unchanged runner sources. The runtime test suite and live game were not run for this documentation-only change.

To rerun the synthetic information-handling probes without contacting the game:

```sh
python3 -B docs/api/evidence/runner-probes.py --root . --output /tmp/rimmolt-probes.json
```
