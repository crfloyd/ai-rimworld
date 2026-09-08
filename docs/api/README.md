# API reference

[Full readable 113-tool reference](API-REFERENCE.md) — use its index for one tool at a time.

The complete captured input catalog lives in [catalog.json](../../api/catalog.json); [effect classifications](../../api/effects.json) describe conservative default handling. Agent-selected dynamic actions still require inspecting current menus and run permissions. No tool grants permission to cheat or use hidden targeting.

```sh
./rw capabilities "caravan"
./rw capabilities --tool form_caravan
./rw --run NAME capabilities --tool get_pawn
```

Without a run, discovery uses the shipped snapshot. With a run, it reads that run's last captured catalog. Both are offline and explicitly dated. Reconnect under owned control to discover actual current tools. Unknown tools remain visible but require effect review before execution.

[Observed response shapes](../../api/observed-shapes.json) preserve field paths/types and source handler pointers for all 113 tools. Sixty-nine have standalone response evidence; 44 do not. None declares an output schema. Empty arrays and observed omissions cannot establish complete contracts. Runtime output preserves unfamiliar properties instead of filtering them through this historical field inventory.

[Shared model behavior](MODELS.md) explains wrappers, event limits and visibility. The full readable113-tool review is restored above. Source provenance, the2,224-record inventory and reproduction scripts remain in Git15c7708; current machine-readable interface information lives in api/. The captured review is reference evidence, not a runtime dependency. The original installed-DLL hash was 3dc82a89bd53d13dc263be26d473a11605623cfe92827460864616445e03e53a.

## Retrieval across starts and compactions

Read this index once when entering a new run or recovering working context. Search by the intended action before guessing tool names or switching to computer use. Inspect the exact tool contract before unfamiliar commands. If a topic search misses, try broader terms or list `./rw capabilities` without a query; search matches are not a whitelist of available actions.

Use the readable manual's `## TOOL_NAME` section for source-reviewed behavior, and the corresponding entry in `api/observed-shapes.json` when response interpretation requires more detail. Retrieve only that section or entry. The current captured input contract governs available arguments; historical response shapes do not bound future fields. Inspect live dynamic menus for current options. A missing cached capability is uncertain until the installed catalog can be refreshed under owned control, not proof that the game cannot perform the action.

In a compaction handoff keep this pointer (`docs/api/README.md`), relevant tool names, unresolved API questions, and evidence references for pending outcomes. Keep the full catalog, schemas and historical examples on disk. API routing belongs in shared project guidance; current IDs, UI state, permissions and encounter discoveries belong only in the selected campaign. This routing does not add API payloads to routine observations or force a reconnect at every compaction.
