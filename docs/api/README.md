# API reference

The complete captured input catalog lives in [catalog.json](../../api/catalog.json); [effect classifications](../../api/effects.json) describe conservative default handling. Agent-selected dynamic actions still require inspecting current menus and run permissions. No tool grants permission to cheat or use hidden targeting.

```sh
./rw capabilities "caravan"
./rw capabilities --tool form_caravan
./rw --run continuance capabilities --tool get_pawn
```

Without a run, discovery uses the shipped snapshot. With a run, it reads that run's last captured catalog. Both are offline and explicitly dated. Reconnect under owned control to discover actual current tools. Unknown tools remain visible but require effect review before execution.

[Observed response shapes](../../api/observed-shapes.json) preserve field paths/types and source handler pointers for all 113 tools. Sixty-nine have standalone response evidence; 44 do not. None declares an output schema. Empty arrays and observed omissions cannot establish complete contracts. Runtime output preserves unfamiliar properties instead of filtering them through this historical field inventory.

[Shared model behavior](MODELS.md) explains wrappers, event limits and visibility. The full 113-tool review, source provenance, 2,224-record inventory and reproduction scripts are preserved in Git commit 15c7708. They were removed from the active tree once their useful interface information moved into api/; they are historical evidence, not runtime dependencies. The original installed-DLL hash was 3dc82a89bd53d13dc263be26d473a11605623cfe92827460864616445e03e53a.
