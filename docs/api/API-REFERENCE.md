# RimMolt captured API reference

Restored readable source-review snapshot from Git `15c7708`. Use the selected campaign’s captured catalog to check current availability; this document is reference evidence, not live game state or gameplay authorization. Current machine-readable interfaces: [input catalog](../../api/catalog.json), [observed shapes](../../api/observed-shapes.json), and [effect handling](../../api/effects.json). Retrieve individual sections through the index rather than loading all113 tools during routine play.

This inventory covers every tool in the captured catalog. Declared input schemas are complete copies; response models describe recorded evidence, not exhaustive contracts. No tool declares `outputSchema`. Dynamic menus, mods, DLC, state, compact/verbose modes, errors, and future versions can introduce unobserved output variants.

The original machine-readable companion `docs/api/inventory.json` (retained in Git `15c7708`) contains full declarations, all observed nested field paths and JSON types, per-field presence counts, query selectors, root-key variants, and source file/line pointers. Array elements use `/*`; object property names use JSON Pointer escaping. Field counts count records containing a path, not array elements. A type count counts records with that type at the path; heterogeneous arrays can contribute multiple types.

Corpus overlap is deduplicated only when an actual JSON-RPC response id and a matching tool/arguments/full-payload SHA256 exist. Conflicting content sharing an RPC id remains separate. Explicit MCP isError and JSON-RPC errors are counted even when the decoded payload is plain text. Historical records without response ids are distinct evidence records, not necessarily unique game actions. Bundled child results remain nested under their actual calling tool; they do not count as standalone observations of the child tool. Empty arrays reveal no element schema. Missing fields are not false or empty unless the tool contract explicitly says so.

Do not load this whole reference during routine play. Use the index to retrieve the relevant tool section or machine-readable entry. Full raw records remain the authority for interpreting returned values.

Archived source paths below are provenance identifiers from the original review, not current checkout links. Source-review metadata and reproduction records remain in Git `15c7708`; decompiled source is not a runtime dependency.

## Coverage

- Catalog tools: 113.
- Tools with standalone observed responses: 69.
- Tools without standalone observed responses: 44.
- Evidence records after identified RPC overlap removal: 2224 (30 duplicate RPC references merged).

## Index

- [get_status](#get_status)
- [list_colonists](#list_colonists)
- [get_pawn](#get_pawn)
- [get_resources](#get_resources)
- [get_resource_readout](#get_resource_readout)
- [get_research](#get_research)
- [learning_helper](#learning_helper)
- [get_map](#get_map)
- [get_alerts](#get_alerts)
- [read_letter](#read_letter)
- [get_world](#get_world)
- [list_things](#list_things)
- [get_area](#get_area)
- [list_unmanaged_items](#list_unmanaged_items)
- [list_fires](#list_fires)
- [get_conditions](#get_conditions)
- [get_room](#get_room)
- [inspect_thing](#inspect_thing)
- [get_info_card](#get_info_card)
- [list_main_buttons](#list_main_buttons)
- [list_architect](#list_architect)
- [do_thing_action](#do_thing_action)
- [designate](#designate)
- [build](#build)
- [set_work_priority](#set_work_priority)
- [wait_for_event](#wait_for_event)
- [set_speed](#set_speed)
- [order_pawn](#order_pawn)
- [draft](#draft)
- [set_research](#set_research)
- [assign_building](#assign_building)
- [list_wildlife](#list_wildlife)
- [list_animals](#list_animals)
- [manage_animal](#manage_animal)
- [list_power_grids](#list_power_grids)
- [room_graph](#room_graph)
- [set_ideo_role](#set_ideo_role)
- [manage_gear](#manage_gear)
- [rename_pawn](#rename_pawn)
- [list_genes](#list_genes)
- [create_xenogerm](#create_xenogerm)
- [implant_xenogerm](#implant_xenogerm)
- [list_mechs](#list_mechs)
- [set_mech_control](#set_mech_control)
- [get_anomaly](#get_anomaly)
- [entity_codex](#entity_codex)
- [list_study_targets](#list_study_targets)
- [set_study](#set_study)
- [get_royalty](#get_royalty)
- [list_titles](#list_titles)
- [manage_permits](#manage_permits)
- [use_permit](#use_permit)
- [list_policies](#list_policies)
- [set_schedule](#set_schedule)
- [set_outfit](#set_outfit)
- [set_drug_policy](#set_drug_policy)
- [manage_apparel_policy](#manage_apparel_policy)
- [manage_food_policy](#manage_food_policy)
- [manage_drug_policy](#manage_drug_policy)
- [set_food_policy](#set_food_policy)
- [set_hostility_response](#set_hostility_response)
- [set_allowed_area](#set_allowed_area)
- [manage_area](#manage_area)
- [list_zones](#list_zones)
- [select_zone](#select_zone)
- [rename_zone](#rename_zone)
- [delete_zone](#delete_zone)
- [set_growing_zone](#set_growing_zone)
- [set_stockpile_priority](#set_stockpile_priority)
- [set_stockpile_filter](#set_stockpile_filter)
- [get_quest](#get_quest)
- [quest_action](#quest_action)
- [list_recipes](#list_recipes)
- [list_bills](#list_bills)
- [add_bill](#add_bill)
- [set_bill](#set_bill)
- [delete_bill](#delete_bill)
- [list_windows](#list_windows)
- [get_window_ui](#get_window_ui)
- [window_action](#window_action)
- [get_inspect_pane](#get_inspect_pane)
- [set_medical_care](#set_medical_care)
- [list_surgeries](#list_surgeries)
- [add_surgery](#add_surgery)
- [list_trade](#list_trade)
- [set_trade](#set_trade)
- [trade_action](#trade_action)
- [manage_prisoner](#manage_prisoner)
- [list_world_objects](#list_world_objects)
- [get_world_tile](#get_world_tile)
- [caravan_action](#caravan_action)
- [world_target](#world_target)
- [find_world_tiles](#find_world_tiles)
- [form_caravan](#form_caravan)
- [world_object_action](#world_object_action)
- [game_setup_status](#game_setup_status)
- [main_menu](#main_menu)
- [save_game](#save_game)
- [load_game](#load_game)
- [return_to_title](#return_to_title)
- [select_scenario](#select_scenario)
- [select_storyteller](#select_storyteller)
- [create_world](#create_world)
- [select_starting_site](#select_starting_site)
- [choose_ideoligion](#choose_ideoligion)
- [edit_ideoligion](#edit_ideoligion)
- [edit_starting_pawn](#edit_starting_pawn)
- [start_game](#start_game)
- [reform_ideoligion](#reform_ideoligion)
- [get_live_chat](#get_live_chat)
- [screenshot](#screenshot)
- [say](#say)
- [help](#help)

## get_status

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RimMoltTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RimMoltTools.cs`) registration line 37 → `Collect = GetStatus` (method line 334). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Overall game status: whether a colony is loaded, current tick, game speed, colony/storyteller name, and every loaded map ('maps': index, name, kind — home settlement vs camp vs quest site — colonist count, and which one the camera is on; use it to pick mapIndex args). Call this first on connecting to check loaded=true before anything else; once a colony is loaded (e.g. right after game start), follow up with get_map for the whole-map orientation (coarse ASCII terrain + forbidden items) before diving into specific tools. Since this is typically called every turn, it also bundles other read-only tools' full output under 'bundled' (default bundle: list_colonists, get_alerts) so routine polling needs one call instead of several — the current bundle list is always reported as 'statusBundle'. Configure the bundle with 'bundle_add'/'bundle_remove' (add/remove tool names) or 'bundle_set' (replace the whole list); only read-only list_*/get_* tools may be bundled, and get_status can't bundle itself. The bundle is saved per save game (survives reload).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "bundle_add": {
      "type": "string",
      "description": "Tool name(s) to add to the get_status bundle: comma-separated, or a JSON array. Must be existing read-only list_*/get_* tools (see help)."
    },
    "bundle_remove": {
      "type": "string",
      "description": "Tool name(s) to remove from the bundle: comma-separated, or a JSON array."
    },
    "bundle_set": {
      "type": "string",
      "description": "Replace the entire bundle with this list: comma-separated, or a JSON array. Pass an empty string to clear it."
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **59**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `loaded`, `programState`. Example: `campaigns/continuance/reference/legacy/history.jsonl:39`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `bundled`, `colonistCount`, `colonyName`, `daysPassed`, `difficulty`, `loaded`, `mapCount`, `maps`, `paused`, `statusBundle`, `statusBundleHint`, `storyteller`, `ticksGame`, `timeSpeed`, `yearsPassed`. Example: `campaigns/continuance/reference/legacy/history.jsonl:75`.
- 56 × `object` with keys: `_paused`, `bundled`, `colonistCount`, `colonyName`, `daysPassed`, `difficulty`, `loaded`, `mapCount`, `maps`, `paused`, `statusBundle`, `statusBundleHint`, `storyteller`, `ticksGame`, `timeSpeed`, `yearsPassed`. Example: `campaigns/continuance/reference/legacy/history.jsonl:159`.
- 1 × `object` with keys: `_paused`, `bundleConfigNotes`, `bundled`, `colonistCount`, `colonyName`, `daysPassed`, `difficulty`, `loaded`, `mapCount`, `maps`, `paused`, `statusBundle`, `statusBundleHint`, `storyteller`, `ticksGame`, `timeSpeed`, `yearsPassed`. Example: `campaigns/continuance/reference/legacy/history.jsonl:224`.

Observed selector combinations: `{}` (59).

All **136** nested observed paths, type counts and provenance are in `inventory.json` → `tools.get_status.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## list_colonists

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RimMoltTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RimMoltTools.cs`) registration line 52 → `Collect = ListColonists` (method line 521). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

List the player's colonists across all maps AND world caravans/travelling transporters, with a summary of health, mood, current job and top skills. 'mentalState' (when present) means the pawn is having a MENTAL BREAK (berserk, daze, tantrum…) and will not take orders until it ends. 'incapableOf' (when present) lists what a pawn can NEVER do (e.g. Violent = cannot fight, Skilled = no art/crafting…) — check it before assigning work or combat; get_pawn tab=bio gives the exact disabled work types. 'inCaravan' (when present) means the pawn is on the world map, not a colony map — it carries the caravan's name instead of the usual map-specific fields (job/mapIndex). 'hint' (when present) flags a pawn worth a closer look — low HP/bleeding or mood near a mental break — with the exact get_pawn call (id + tab) to inspect.

### Declared input schema

```json
{
  "type": "object",
  "properties": {}
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **12**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 12 × `object` with keys: `_paused`, `colonists`, `count`, `loaded`. Example: `campaigns/continuance/reference/legacy/history.jsonl:369`.

Observed selector combinations: `{}` (12).

All **21** nested observed paths, type counts and provenance are in `inventory.json` → `tools.list_colonists.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## get_pawn

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RimMoltTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RimMoltTools.cs`) registration line 58 → `Collect = GetColonist` (method line 687). Registered aliases: `get_colonist`. This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Detailed information about one PAWN — a colonist, or (by id/name) any other pawn: raiders, visitors, traders, prisoners, slaves, animals, mechs. Works for pawns AWAY FROM EVERY MAP too — anyone travelling with a caravan or riding a transport pod/shuttle (the same tabs a human opens off the caravan on the world map); such a result carries onMap=false + inCaravan and its x/z/mapIndex are meaningless. A human can click any of them and read the same tabs, so you can too; a non-colonist result carries isColonist=false plus faction/factionRelation/hostile/role so you can't mistake a raider for one of yours. Use this to size up an incoming raid (tab=gear for their weapons/armour, tab=health for injuries and capacities, tab=bio for skills/traits) or to read a prisoner or a visitor. Without 'tab': a minimal summary only (health, mood, downed/dead, equipped weapon, job, position, mapIndex) — request a tab for skills/traits/needs/health/social/etc. With 'tab': the full contents of that inspect tab, same as the human sees — health (capacities+hediffs), needs (with mood thought breakdown), gear (equipment/apparel/inventory/mass/temperature), bio (backstory/traits/skills/title/ideoligion), social (relations+opinions), log (what happened to them recently, e.g. tab=log to see combat and social events), records, training. Identify by 'id' or 'name'. With tab=needs/health (or 'all') pass detail=true to also include the mouseover tooltip text a human sees on hover: each need's meaning + thresholds, each capacity's 'affected by' breakdown, each hediff's full description (cause, tend quality, immunity progression). Default (detail omitted) stays compact.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Pawn ThingID (preferred — from list_colonists, or list_things category=pawn for non-colonists)"
    },
    "name": {
      "type": "string",
      "description": "Pawn name or label (case-insensitive substring match); colonists are matched first"
    },
    "tab": {
      "type": "string",
      "enum": [
        "health",
        "needs",
        "gear",
        "bio",
        "social",
        "log",
        "records",
        "training",
        "all"
      ],
      "description": "Inspect tab: health/needs/gear/bio/social/log/records/training (or 'all'). Omit for a summary."
    },
    "detail": {
      "type": "boolean",
      "description": "With tab=needs/health/all: also include mouseover tooltip text (need meaning + thresholds, capacity 'affected by' breakdown, hediff description). Default false (compact)."
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **378**. Explicit error-marker records: **6**.

Root-key variants (counts are evidence records):

- 15 × `object` with keys: `_paused`, `apparel`, `comfyTempMax`, `comfyTempMin`, `equipment`, `id`, `inventory`, `loaded`, `massCapacity`, `massCarried`, `name`, `tab`. Example: `campaigns/continuance/reference/legacy/history.jsonl:172`.
- 2 × `object` with keys: `_paused`, `faction`, `factionRelation`, `id`, `isColonist`, `kind`, `loaded`, `name`, `needs`, `role`, `tab`. Example: `campaigns/continuance/reference/legacy/history.jsonl:221`.
- 50 × `object` with keys: `_paused`, `id`, `loaded`, `mood`, `name`, `needs`, `tab`, `thoughts`. Example: `campaigns/continuance/reference/legacy/history.jsonl:259`.
- 6 × `object` with keys: `_paused`, `apparel`, `comfyTempMax`, `comfyTempMin`, `equipment`, `faction`, `factionRelation`, `hostile`, `id`, `inventory`, `isColonist`, `kind`, `loaded`, `massCapacity`, `massCarried`, `name`, `role`, `tab`. Example: `campaigns/continuance/reference/legacy/history.jsonl:370`.
- 1 × `object` with keys: `_paused`, `adulthood`, `ageBiological`, `ageChronological`, `childhood`, `faction`, `factionRelation`, `gender`, `hostile`, `id`, `ideoligion`, `isColonist`, `kind`, `loaded`, `name`, `role`, `skills`, `tab`, `traits`. Example: `campaigns/continuance/reference/legacy/history.jsonl:371`.
- 6 × `object` with keys: `_paused`, `_threatWarning`, `bleedRatePerDay`, `capacities`, `dead`, `downed`, `faction`, `factionRelation`, `hediffs`, `hostile`, `id`, `isColonist`, `kind`, `loaded`, `name`, `overallHealthPercent`, `painPercent`, `role`, `state`, `tab`. Example: `campaigns/continuance/reference/legacy/history.jsonl:384`.
- 9 × `object` with keys: `_paused`, `bleedRatePerDay`, `capacities`, `dead`, `downed`, `faction`, `factionRelation`, `hediffs`, `hostile`, `id`, `isColonist`, `kind`, `loaded`, `name`, `overallHealthPercent`, `painPercent`, `role`, `state`, `tab`. Example: `campaigns/continuance/reference/legacy/history.jsonl:387`.
- 5 × `object` with keys: `_paused`, `capacities`, `dead`, `downed`, `faction`, `factionRelation`, `hediffs`, `hostile`, `id`, `isColonist`, `kind`, `loaded`, `name`, `overallHealthPercent`, `painPercent`, `role`, `state`, `tab`. Example: `campaigns/continuance/reference/legacy/history.jsonl:398`.
- 5 × `object` with keys: `_paused`, `error`. Example: `campaigns/continuance/reference/legacy/history.jsonl:437`.
- 1 × `object` with keys: `_paused`, `adulthood`, `ageBiological`, `ageChronological`, `childhood`, `downed`, `faction`, `factionRelation`, `gender`, `id`, `ideoligion`, `isColonist`, `kind`, `loaded`, `name`, `role`, `skills`, `tab`, `traits`. Example: `campaigns/continuance/reference/legacy/history.jsonl:469`.
- 14 × `object` with keys: `_paused`, `capacities`, `dead`, `downed`, `faction`, `factionRelation`, `hediffs`, `id`, `isColonist`, `kind`, `loaded`, `name`, `overallHealthPercent`, `painPercent`, `role`, `state`, `tab`. Example: `campaigns/continuance/reference/legacy/history.jsonl:470`.
- 1 × `object` with keys: `_paused`, `adulthood`, `ageBiological`, `ageChronological`, `childhood`, `downed`, `faction`, `factionRelation`, `gender`, `hostile`, `id`, `ideoligion`, `isColonist`, `kind`, `loaded`, `name`, `role`, `skills`, `tab`, `traits`. Example: `campaigns/continuance/reference/legacy/history.jsonl:491`.
- 2 × `object` with keys: `_paused`, `dead`, `downed`, `faction`, `factionRelation`, `health`, `hint`, `hostile`, `hostilityResponse`, `id`, `isColonist`, `job`, `kind`, `mapIndex`, `mentalState`, `mood`, `name`, `role`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:709`.
- 18 × `object` with keys: `_paused`, `dead`, `downed`, `health`, `hint`, `hostilityResponse`, `id`, `incapableOf`, `job`, `mapIndex`, `mood`, `name`, `royalTitle`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:717`.
- 30 × `object` with keys: `_paused`, `dead`, `downed`, `health`, `hint`, `hostilityResponse`, `id`, `job`, `mapIndex`, `mood`, `name`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:718`.
- 7 × `object` with keys: `_paused`, `_threatWarning`, `dead`, `downed`, `faction`, `factionRelation`, `health`, `hint`, `hostile`, `hostilityResponse`, `id`, `isColonist`, `job`, `kind`, `mapIndex`, `mentalState`, `mood`, `name`, `role`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:720`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `bio`, `faction`, `factionRelation`, `gear`, `health`, `hostile`, `id`, `isColonist`, `kind`, `loaded`, `log`, `name`, `needs`, `records`, `role`, `social`, `training`. Example: `campaigns/continuance/reference/legacy/history.jsonl:769`.
- 4 × `object` with keys: `_paused`, `dead`, `downed`, `faction`, `factionRelation`, `health`, `hint`, `hostile`, `hostilityResponse`, `id`, `isColonist`, `job`, `kind`, `mapIndex`, `mood`, `name`, `role`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:778`.
- 27 × `object` with keys: `_paused`, `_threatWarning`, `dead`, `downed`, `health`, `hint`, `hostilityResponse`, `id`, `incapableOf`, `job`, `mapIndex`, `mood`, `name`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:794`.
- 4 × `object` with keys: `_paused`, `_threatWarning`, `dead`, `downed`, `faction`, `factionRelation`, `health`, `hint`, `hostile`, `hostilityResponse`, `id`, `isColonist`, `job`, `kind`, `mapIndex`, `mood`, `name`, `role`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:795`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `capacities`, `dead`, `downed`, `faction`, `factionRelation`, `hediffs`, `id`, `isColonist`, `kind`, `loaded`, `name`, `overallHealthPercent`, `painPercent`, `role`, `state`, `tab`. Example: `campaigns/continuance/reference/legacy/history.jsonl:808`.
- 8 × `object` with keys: `_paused`, `dead`, `downed`, `health`, `hint`, `hostilityResponse`, `id`, `incapableOf`, `job`, `mapIndex`, `mood`, `name`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:877`.
- 61 × `object` with keys: `_paused`, `capacities`, `dead`, `downed`, `hediffs`, `id`, `loaded`, `name`, `overallHealthPercent`, `painPercent`, `state`, `tab`. Example: `campaigns/continuance/reference/legacy/history.jsonl:960`.
- 3 × `object` with keys: `_paused`, `adulthood`, `ageBiological`, `ageChronological`, `childhood`, `gender`, `id`, `ideoligion`, `loaded`, `name`, `skills`, `tab`, `traits`. Example: `campaigns/continuance/reference/legacy/history.jsonl:990`.
- 1 × `object` with keys: `_paused`, `bio`, `gear`, `health`, `id`, `loaded`, `log`, `name`, `needs`, `records`, `social`, `training`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1050`.
- 26 × `object` with keys: `_paused`, `_threatWarning`, `dead`, `downed`, `health`, `hint`, `hostilityResponse`, `id`, `job`, `mapIndex`, `mood`, `name`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1108`.
- 15 × `object` with keys: `_paused`, `_threatWarning`, `dead`, `downed`, `health`, `hint`, `hostilityResponse`, `id`, `incapableOf`, `job`, `mapIndex`, `mood`, `name`, `royalTitle`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1120`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `dead`, `downed`, `health`, `hint`, `hostilityResponse`, `id`, `job`, `mapIndex`, `mentalState`, `mood`, `name`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1158`.
- 21 × `object` with keys: `_paused`, `bleedRatePerDay`, `capacities`, `dead`, `downed`, `hediffs`, `id`, `loaded`, `name`, `overallHealthPercent`, `painPercent`, `state`, `tab`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1165`.
- 1 × `object` with keys: `_paused`, `adulthood`, `ageBiological`, `ageChronological`, `childhood`, `gender`, `id`, `ideoligion`, `incapableOf`, `incapableOfTags`, `incapableWorkTypes`, `loaded`, `name`, `skills`, `tab`, `traits`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1167`.
- 2 × `object` with keys: `_paused`, `ageBiological`, `ageChronological`, `childhood`, `gender`, `id`, `ideoligion`, `loaded`, `name`, `skills`, `tab`, `traits`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1187`.
- 3 × `object` with keys: `_paused`, `dead`, `downed`, `health`, `hint`, `hostilityResponse`, `id`, `job`, `mapIndex`, `mentalState`, `mood`, `name`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1203`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `apparel`, `comfyTempMax`, `comfyTempMin`, `equipment`, `id`, `inventory`, `loaded`, `massCapacity`, `massCarried`, `name`, `tab`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1362`.
- 6 × `object` with keys: `_paused`, `_threatWarning`, `dead`, `downed`, `faction`, `factionRelation`, `health`, `hint`, `hostile`, `hostilityResponse`, `id`, `incapableOf`, `isColonist`, `job`, `kind`, `mapIndex`, `mood`, `name`, `role`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1512`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `ageBiological`, `ageChronological`, `childhood`, `downed`, `faction`, `factionRelation`, `gender`, `hostile`, `id`, `ideoligion`, `isColonist`, `kind`, `loaded`, `name`, `role`, `skills`, `tab`, `traits`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1566`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `adulthood`, `ageBiological`, `ageChronological`, `childhood`, `downed`, `faction`, `factionRelation`, `gender`, `hostile`, `id`, `ideoligion`, `isColonist`, `kind`, `loaded`, `name`, `role`, `skills`, `tab`, `traits`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1567`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `error`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1584`.
- 2 × `object` with keys: `_paused`, `_threatWarning`, `id`, `loaded`, `mood`, `name`, `needs`, `tab`, `thoughts`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1599`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `capacities`, `dead`, `downed`, `faction`, `factionRelation`, `hediffs`, `hostile`, `id`, `isColonist`, `kind`, `loaded`, `name`, `overallHealthPercent`, `painPercent`, `role`, `state`, `tab`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1603`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `apparel`, `comfyTempMax`, `comfyTempMin`, `equipment`, `id`, `inventory`, `loaded`, `massCapacity`, `massCarried`, `name`, `tab`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1605`.
- 1 × `object` with keys: `_paused`, `carriedBy`, `dead`, `downed`, `faction`, `factionRelation`, `health`, `hint`, `hostile`, `hostilityResponse`, `id`, `isColonist`, `job`, `kind`, `mapIndex`, `mood`, `name`, `role`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1616`.
- 4 × `object` with keys: `_paused`, `dead`, `downed`, `faction`, `factionRelation`, `health`, `hint`, `hostilityResponse`, `id`, `isColonist`, `job`, `kind`, `mapIndex`, `mood`, `name`, `role`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1641`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `entries`, `id`, `loaded`, `name`, `tab`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1828`.
- 1 × `object` with keys: `_paused`, `carriedBy`, `dead`, `downed`, `health`, `hint`, `hostilityResponse`, `id`, `incapableOf`, `job`, `mapIndex`, `mood`, `name`, `royalTitle`, `weapon`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1840`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `adulthood`, `ageBiological`, `ageChronological`, `childhood`, `downed`, `faction`, `factionRelation`, `gender`, `hostile`, `id`, `ideoligion`, `incapableOf`, `incapableOfTags`, `incapableWorkTypes`, `isColonist`, `kind`, `loaded`, `name`, `role`, `skills`, `tab`, `traits`. Example: `campaigns/continuance/reference/legacy/history.jsonl:2051`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `apparel`, `comfyTempMax`, `comfyTempMin`, `equipment`, `faction`, `factionRelation`, `hostile`, `id`, `inventory`, `isColonist`, `kind`, `loaded`, `massCapacity`, `massCarried`, `name`, `role`, `tab`. Example: `campaigns/continuance/reference/legacy/history.jsonl:2090`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `faction`, `factionRelation`, `hostile`, `id`, `isColonist`, `kind`, `loaded`, `mood`, `name`, `needs`, `role`, `tab`, `thoughts`. Example: `campaigns/continuance/reference/legacy/history.jsonl:2091`.
- 3 × `object` with keys: `_paused`, `downed`, `faction`, `factionRelation`, `id`, `isColonist`, `kind`, `loaded`, `mood`, `name`, `needs`, `role`, `tab`, `thoughts`. Example: `campaigns/continuance/raw/obs-6bc9ae45690f424db9b7865500b4e31d.json`.

Observed selector combinations: `{"tab": "gear"}` (24), `{"tab": "needs"}` (58), `{"tab": "bio"}` (12), `{"tab": "health"}` (99), `{}` (160), `{"tab": "all"}` (3), `{"detail": true, "tab": "health"}` (21), `{"tab": "log"}` (1).

All **226** nested observed paths, type counts and provenance are in `inventory.json` → `tools.get_pawn.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## get_resources

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RimMoltTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RimMoltTools.cs`) registration line 80 → `Collect = GetResources` (method line 856). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Stockpiled resource counts and total colony wealth, aggregated across maps.

### Declared input schema

```json
{
  "type": "object",
  "properties": {}
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **2**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 2 × `object` with keys: `_paused`, `loaded`, `resourceKinds`, `resources`, `wealthTotal`. Example: `campaigns/continuance/reference/legacy/history.jsonl:175`.

Observed selector combinations: `{}` (2).

All **10** nested observed paths, type counts and provenance are in `inventory.json` → `tools.get_resources.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## get_resource_readout

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RimMoltTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RimMoltTools.cs`) registration line 85 → `Collect = GetResourceReadout` (method line 898). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

The stored-item readout shown in the corner of the screen: every counted resource the colony has in storage, with its count, grouped by category exactly as the on-screen readout groups them. Mirrors the human UI's resource list. Aggregated across maps.

### Declared input schema

```json
{
  "type": "object",
  "properties": {}
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **1**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `_paused`, `categories`, `loaded`, `resourceKinds`, `totalItems`. Example: `campaigns/continuance/reference/legacy/history.jsonl:2058`.

Observed selector combinations: `{}` (1).

All **13** nested observed paths, type counts and provenance are in `inventory.json` → `tools.get_resource_readout.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## get_research

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RimMoltTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RimMoltTools.cs`) registration line 90 → `Collect = GetResearch` (method line 1048). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Research information. Without args: the current project(s), progress, counts, and the research tabs that exist (base game + DLC/mod tabs each add their own tab of projects). With list='unfinished': every unfinished project with cost, whether it can start now, and which prerequisites are still missing (optionally narrowed with tab='<tab defName>'). With project='<defName|label>': that project's full detail — prerequisite tree (unfinished branches expanded), tech level, techprints, required research bench/facilities — i.e. the exact reasons it can or cannot start. Anomaly-tab projects are researched with knowledge points gained by STUDYING entities (list_study_targets), not at a research bench; they run in parallel with the normal project — one active project per knowledge category (Basic/Advanced). The summary's 'anomaly' block shows each category's active project. Undiscovered entity research stays hidden until the entity is encountered.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "list": {
      "type": "string",
      "enum": [
        "unfinished"
      ],
      "description": "Set to 'unfinished' to list all unfinished research projects"
    },
    "tab": {
      "type": "string",
      "description": "With list='unfinished': only projects of this research tab (ResearchTabDef defName from the summary's 'tabs', e.g. Main)"
    },
    "project": {
      "type": "string",
      "description": "ResearchProjectDef defName or label for a detailed report with prerequisite tree"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **21**. Explicit error-marker records: **1**.

Root-key variants (counts are evidence records):

- 12 × `object` with keys: `_paused`, `availableCount`, `completedCount`, `current`, `loaded`, `tabs`, `totalCount`. Example: `campaigns/continuance/reference/legacy/history.jsonl:188`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `availableCount`, `completedCount`, `current`, `loaded`, `tabs`, `totalCount`. Example: `campaigns/continuance/reference/legacy/history.jsonl:283`.
- 4 × `object` with keys: `_paused`, `canStartNow`, `cost`, `defName`, `description`, `finished`, `label`, `loaded`, `prerequisites`, `requirements`, `techLevel`. Example: `campaigns/continuance/reference/legacy/history.jsonl:292`.
- 2 × `object` with keys: `_dialogOpen`, `_paused`, `canStartNow`, `cost`, `defName`, `description`, `finished`, `label`, `loaded`, `prerequisites`, `requirements`, `techLevel`. Example: `campaigns/continuance/reference/legacy/history.jsonl:361`.
- 1 × `object` with keys: `_paused`, `error`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:606`.
- 1 × `object` with keys: `_paused`, `count`, `hint`, `loaded`, `mode`, `projects`. Example: `campaigns/continuance/reference/legacy/history.jsonl:680`.

Observed selector combinations: `{}` (21).

All **58** nested observed paths, type counts and provenance are in `inventory.json` → `tools.get_research.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## learning_helper

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RimMoltTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RimMoltTools.cs`) registration line 109 → `Collect = LearningHelper` (method line 976). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

The in-game Learning Helper (concept tutorials). Without 'title': lists every learning-helper topic title (the same concepts RimWorld surfaces to teach mechanics). With 'title': the full explanatory text of that topic (matched by title, case-insensitive substring, or defName). You don't need to poll this proactively: when vanilla itself decides to teach a concept (the same moment it would pop up the on-screen tutorial panel), its title + full text arrive unprompted in this and every other tool result's '_notifications' (kind='learning'), each concept at most once — gated by the 'Forward Learning Helper lessons to the AI' mod setting (default on).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Topic title/defName to read (omit to list all titles)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## get_map

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RimMoltTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RimMoltTools.cs`) registration line 119 → `Collect = GetMap` (method line 1412). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

CALL THIS FIRST when a colony begins (or when you resume one): summary of one map — the one on camera by default, or pass mapIndex for another (get_status's 'maps' list gives each loaded map's index/name/kind, e.g. home settlement vs camp vs quest site) — (size, biome, danger rating, wealth, colonist/animal/hostile counts) PLUS a game-start orientation — 'terrainOverview', a coarse whole-map ASCII grid (auto-scaled, with legend) showing terrain/rock/water/trees/structures/geysers at a glance (no zones — this is the structures-only terrain layer), and 'forbiddenItems', a count of forbidden items with a pointer to list_unmanaged_items for the position-level list. For a closer look use get_area render='ascii' — fine-grained (1 char/cell) over a specific rectangle when planning construction or defense, or coarse (pass 'scale') for other whole-map passes with a different layer: 'zones' for zone+building placement, 'buildings' for furniture placement, 'affordance' for construction support, or pollution/fertility.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default: the map on camera). get_status's 'maps' list maps indices to names."
    },
    "confirm": {
      "type": "boolean",
      "description": "Fetch the full output even when it exceeds the large-output guard (~25k chars)."
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **1**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `_dialogOpen`, `_paused`, `biome`, `colonists`, `colonyAnimals`, `dangerRating`, `forbiddenItems`, `hostilesSpawned`, `index`, `loaded`, `name`, `sizeX`, `sizeZ`, `terrainOverview`, `wealthTotal`. Example: `campaigns/continuance/reference/legacy/history.jsonl:76`.

Observed selector combinations: `{}` (1).

All **39** nested observed paths, type counts and provenance are in `inventory.json` → `tools.get_map.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## get_alerts

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RimMoltTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RimMoltTools.cs`) registration line 134 → `Collect = GetAlerts` (method line 1462). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Current threats and warnings: danger rating per map, the active letters stack (each with an id for read_letter), the active alert readout (right-side warnings like low food, idle colonist, needs treatment) with priority and explanation, and 'recentMessages' — the last few top-left toast messages that have since faded off-screen (newest first).

### Declared input schema

```json
{
  "type": "object",
  "properties": {}
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **6**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `loaded`, `message`. Example: `campaigns/continuance/reference/legacy/history.jsonl:65`.
- 5 × `object` with keys: `_paused`, `activeAlerts`, `activeLetters`, `dangerByMap`, `hint`, `loaded`, `recentMessages`. Example: `campaigns/continuance/reference/legacy/history.jsonl:503`.

Observed selector combinations: `{}` (6).

All **32** nested observed paths, type counts and provenance are in `inventory.json` → `tools.get_alerts.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## read_letter

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RimMoltTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RimMoltTools.cs`) registration line 139 → `Collect = ReadLetter` (method line 1596). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Read the full text of an in-game letter (the body shown when you click a letter). Give 'id' (a letter id from get_alerts or a notification's id). Without 'id', lists the active letters with their ids and labels. Dismissed letters may still be found in the archive. Pass open=true to also click the letter open in-game: its dialog (with any choice buttons) appears and can then be read/answered via list_windows/get_window_ui/window_action. Pass dismiss=true to also remove the letter from the on-screen stack (the human right-click) once it is handled — this call returns the full text first, so nothing is lost, and future get_alerts results stay small. Only a read letter can be dismissed (dismiss requires 'id' and always reads).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "description": "Letter id (from get_alerts/notifications)"
    },
    "open": {
      "type": "boolean",
      "description": "Also open the letter's dialog in-game (like clicking it), enabling window_action on its choices"
    },
    "dismiss": {
      "type": "boolean",
      "description": "After reading, remove the letter from the on-screen stack (like right-clicking it). Use once the letter is handled, to keep get_alerts small."
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **66**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 10 × `object` with keys: `_paused`, `arrivalTick`, `dismissed`, `id`, `label`, `ok`, `text`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:305`.
- 4 × `object` with keys: `_paused`, `arrivalTick`, `dismissed`, `id`, `label`, `ok`, `relatedFaction`, `text`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:327`.
- 3 × `object` with keys: `_paused`, `arrivalTick`, `dismissed`, `hint`, `id`, `label`, `ok`, `questId`, `questName`, `questState`, `text`, `title`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:353`.
- 7 × `object` with keys: `_paused`, `arrivalTick`, `id`, `label`, `ok`, `relatedFaction`, `text`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:367`.
- 1 × `object` with keys: `_paused`, `arrivalTick`, `dismissNote`, `dismissed`, `id`, `label`, `ok`, `relatedFaction`, `text`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:439`.
- 4 × `object` with keys: `_paused`, `arrivalTick`, `hint`, `id`, `label`, `ok`, `questId`, `questName`, `questState`, `text`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:466`.
- 4 × `object` with keys: `_dialogOpen`, `_paused`, `arrivalTick`, `hint`, `id`, `label`, `ok`, `opened`, `questId`, `questName`, `questState`, `text`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:493`.
- 4 × `object` with keys: `_paused`, `arrivalTick`, `dismissed`, `hint`, `id`, `label`, `ok`, `questId`, `questName`, `questState`, `text`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:550`.
- 5 × `object` with keys: `_paused`, `_threatWarning`, `arrivalTick`, `id`, `label`, `ok`, `text`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:667`.
- 11 × `object` with keys: `_paused`, `arrivalTick`, `id`, `label`, `ok`, `text`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:708`.
- 7 × `object` with keys: `_paused`, `arrivalTick`, `hint`, `id`, `label`, `ok`, `questId`, `questName`, `questState`, `text`, `title`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:970`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `arrivalTick`, `hint`, `id`, `label`, `ok`, `opened`, `openedNote`, `questId`, `questName`, `questState`, `text`, `title`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1008`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `arrivalTick`, `hint`, `id`, `label`, `ok`, `opened`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1418`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `arrivalTick`, `hint`, `id`, `label`, `ok`, `questId`, `questName`, `questState`, `text`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1485`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `_threatWarning`, `arrivalTick`, `hint`, `id`, `label`, `ok`, `opened`, `text`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1518`.
- 1 × `object` with keys: `_paused`, `arrivalTick`, `hint`, `id`, `label`, `ok`, `questId`, `questName`, `questState`, `relatedFaction`, `text`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1888`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `arrivalTick`, `hint`, `id`, `label`, `ok`, `opened`, `text`, `type`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1944`.

Observed selector combinations: `{}` (66).

All **36** nested observed paths, type counts and provenance are in `inventory.json` → `tools.read_letter.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## get_world

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RimMoltTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RimMoltTools.cs`) registration line 154 → `Collect = GetWorld` (method line 1881). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

World-level info: visible factions with relations/goodwill, and active quests with their state. If the output would be very large, a short notice is returned instead — re-call with confirm=true.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "confirm": {
      "type": "boolean",
      "description": "Fetch the full output even when it exceeds the large-output guard (~25k chars)."
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **1**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `_paused`, `activeQuests`, `factions`, `loaded`. Example: `campaigns/continuance/reference/legacy/history.jsonl:205`.

Observed selector combinations: `{}` (1).

All **10** nested observed paths, type counts and provenance are in `inventory.json` → `tools.get_world.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## list_things

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/EntityTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/EntityTools.cs`) registration line 47 → `Collect = ListThings` (method line 332). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

List spawned things on a map, filtered by category and faction. Use this to get all pawns, all hostiles, all colonists, all buildings/items, etc. Provide an anchor ('nearId' = a thing/pawn, or 'nearX'+'nearZ') to sort results nearest-first and include 'distance'; optionally limit by 'radius'. TOKENS: results are compact (default/empty fields omitted: absent faction = none, absent hostile = not hostile, absent forbidden = allowed). Use 'summary' for just per-def counts (smallest payload), 'verbose' for the full fixed-shape record, and 'limit' to cap rows. When category=item, the result also carries a 'storage' block (free storage slots per zone/shelf); if all storage is full it includes a 'warning' recommending more shelves or a bigger stockpile. In summary mode, item results also carry a 'forbiddenSplit' block (allowedCount/forbiddenCount plus per-def groups for each) so you can see at a glance which item stacks are forbidden vs allowed across the whole map — see also list_unmanaged_items for a position-level list of exactly what to haul/allow. Blueprints (planned, not started) and frames (under construction) are never reported as if they were the finished building: 'construction' says which, 'label' states the status in words, and frames also carry 'percentComplete' (work progress) and 'materialsPercent' (how much of the required stuff has been delivered — a frame can sit at 100% materials but 0% work if construction stalled). Live hostile pawns also carry 'targeting' (e.g. 'attacking colonist Alice', 'targeting door') — what their current job is aimed at; this is AI-internal info a human player can't see directly, gated by the 'Reveal hostile targeting' mod setting (default on) and omitted when off.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "category": {
      "type": "string",
      "enum": [
        "all",
        "pawn",
        "building",
        "item",
        "plant",
        "filth",
        "blueprint",
        "frame",
        "construction"
      ],
      "description": "Thing category filter"
    },
    "faction": {
      "type": "string",
      "enum": [
        "any",
        "player",
        "hostile",
        "neutral",
        "wild"
      ],
      "description": "Faction relation filter"
    },
    "defName": {
      "type": "string",
      "description": "Exact ThingDef defName filter (optional)"
    },
    "summary": {
      "type": "boolean",
      "description": "Return only per-def counts ({def,label,count}) instead of individual things"
    },
    "verbose": {
      "type": "boolean",
      "description": "Include all fields per thing instead of the compact form"
    },
    "nearId": {
      "type": "string",
      "description": "Anchor ThingID: sort results by distance from this thing/pawn"
    },
    "nearX": {
      "type": "integer",
      "description": "Anchor cell X (used with nearZ if no nearId)"
    },
    "nearZ": {
      "type": "integer",
      "description": "Anchor cell Z (used with nearX if no nearId)"
    },
    "radius": {
      "type": "integer",
      "description": "Only include things within this distance of the anchor (optional)"
    },
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default: current map)"
    },
    "limit": {
      "type": "integer",
      "description": "Max results to return (default 300)"
    },
    "confirm": {
      "type": "boolean",
      "description": "Fetch the full output even when it exceeds the large-output guard (~25k chars)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **132**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 5 × `object` with keys: `_dialogOpen`, `_paused`, `loaded`, `mapIndex`, `matched`, `returned`, `sortedByDistance`, `things`, `truncated`. Example: `campaigns/continuance/reference/legacy/history.jsonl:79`.
- 98 × `object` with keys: `_paused`, `loaded`, `mapIndex`, `matched`, `returned`, `sortedByDistance`, `things`, `truncated`. Example: `campaigns/continuance/reference/legacy/history.jsonl:82`.
- 14 × `object` with keys: `_paused`, `loaded`, `mapIndex`, `matched`, `returned`, `sortedByDistance`, `storage`, `things`, `truncated`. Example: `campaigns/continuance/reference/legacy/history.jsonl:83`.
- 5 × `object` with keys: `_paused`, `groups`, `loaded`, `mapIndex`, `matched`, `mode`. Example: `campaigns/continuance/reference/legacy/history.jsonl:174`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `groups`, `loaded`, `mapIndex`, `matched`, `mode`. Example: `campaigns/continuance/reference/legacy/history.jsonl:284`.
- 2 × `object` with keys: `_paused`, `forbiddenSplit`, `groups`, `loaded`, `mapIndex`, `matched`, `mode`, `storage`. Example: `campaigns/continuance/reference/legacy/history.jsonl:837`.
- 7 × `object` with keys: `_paused`, `_threatWarning`, `loaded`, `mapIndex`, `matched`, `returned`, `sortedByDistance`, `things`, `truncated`. Example: `campaigns/continuance/reference/legacy/history.jsonl:928`.

Observed selector combinations: `{"category": "pawn"}` (35), `{"category": "item"}` (14), `{"category": "construction", "summary": true}` (2), `{"category": "building"}` (6), `{"category": "plant", "summary": true}` (2), `{"category": "plant"}` (5), `{"category": "construction"}` (6), `{}` (53), `{"verbose": true}` (1), `{"category": "item", "summary": true}` (2), `{"category": "building", "summary": true}` (1), `{"category": "pawn", "summary": true}` (1), `{"category": "pawn", "verbose": true}` (4).

All **81** nested observed paths, type counts and provenance are in `inventory.json` → `tools.list_things.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## get_area

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/EntityTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/EntityTools.cs`) registration line 68 → `Collect = GetArea` (method line 567). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

THE recommended way to understand spatial layout, terrain and base structure — prefer this over reading thing lists when you need to picture the map. Inspect a rectangular area: every thing inside it with its location, plus a per-terrain cell-count summary. Omit minX/minZ/maxX/maxZ entirely to cover the whole current map. Non-ASCII area is capped at 2500 cells. TOKENS: things are compact (default/empty fields omitted). Use 'summary' for just per-def thing counts + terrain (smallest payload), or 'verbose' for full per-thing records. SPATIAL LAYOUT: pass render='ascii' for a character-grid map (with a legend) instead of thing lists — by far the most token-efficient way to see where walls/doors/plants/water/geysers actually are. Two grain levels: fine (default, 1 char = 1 cell) for planning construction or defense over a specific rectangle; coarse (pass 'scale', e.g. 4-10, so 1 char summarizes a scale×scale block by its most common/highest-priority content) for a whole-map overview at colony start — omit bounds + set a scale (or just call get_map, which embeds this automatically). If bounds are omitted/too large for fine-grained ascii, a scale is auto-picked so the grid fits in roughly 55 characters per side. 'layer' picks: terrain (default — structures only: walls/rock/doors/trees/water/geysers/ground, no zones); zones (zone AND building placement — each zone gets its own letter, uppercase for stockpiles, lowercase for growing/other, legend gives label+type+priority/crop); buildings (furniture/building placement — every distinct built ThingDef in view gets its own letter, legend gives def label + count; walls/doors stay fixed chars and aren't lettered); things (show ONLY things matching the 'thing' arg — pass 'thing' and this layer is picked automatically); affordance (what the ground supports building — heavy/medium/light/bridge-only/none, per terrain's construction affordances); pollution; fertility; deepResources (drillable ore lumps found by ground-penetrating scanners — one letter per resource, legend gives cell count + total drill yield; empty until a scanner completes a scan); roof (unroofed/constructed/thin rock/overhead mountain — solar+growing need unroofed, overhead mountain blocks mortars and carries infestation risk); light (brightness bands — darkness stops plant growth and penalizes work); areas (ONE Area's cells — home area by default, or pass 'area' to pick an allowed/no-roof/snow-clear area by name; legend lists every area).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "minX": {
      "type": "integer",
      "description": "Rectangle min X (west); omit all four bounds together for the whole map"
    },
    "minZ": {
      "type": "integer",
      "description": "Rectangle min Z (south)"
    },
    "maxX": {
      "type": "integer",
      "description": "Rectangle max X (east)"
    },
    "maxZ": {
      "type": "integer",
      "description": "Rectangle max Z (north)"
    },
    "summary": {
      "type": "boolean",
      "description": "Return only per-def counts + terrain summary instead of individual things"
    },
    "verbose": {
      "type": "boolean",
      "description": "Include all fields per thing instead of the compact form"
    },
    "render": {
      "type": "string",
      "enum": [
        "ascii"
      ],
      "description": "Set to 'ascii' for a character-grid map of the area instead of thing lists"
    },
    "layer": {
      "type": "string",
      "enum": [
        "terrain",
        "zones",
        "buildings",
        "things",
        "affordance",
        "pollution",
        "fertility",
        "deepResources",
        "roof",
        "light",
        "areas"
      ],
      "description": "ASCII grid layer (with render=ascii; default terrain — structures only, no zones). 'zones' = zone+building placement (lettered). 'buildings' = furniture/building placement (lettered per def). 'things' = only cells matching the 'thing' arg (required for this layer). 'affordance' = construction support per cell (heavy/medium/light/bridge/none). 'deepResources' = drillable ore found by ground-penetrating scanners (lettered per resource). 'roof' = roof state per cell (overhead mountain/rock/constructed/none). 'light' = brightness bands. 'areas' = one Area's cells (default home area; pick with 'area')."
    },
    "area": {
      "type": "string",
      "description": "With layer='areas': which Area to render — label match, exact first then substring, case-insensitive (e.g. 'Home', an allowed area's name, 'Build roof', 'Snow clear'). Omit for the home area; the legend always lists every area on the map."
    },
    "thing": {
      "type": "string",
      "description": "With render=ascii: show only things matching this ThingDef defName (exact, case-insensitive) or label substring (case-insensitive) — matches items, buildings, plants and pawns. Passing this auto-selects layer='things' even if 'layer' is omitted or set to something else."
    },
    "scale": {
      "type": "integer",
      "description": "With render=ascii: cells per character per side (e.g. 4 = each char summarizes a 4x4 block, picked by highest-priority/most-common content). Omit for exact 1-char-per-cell; for large areas a scale is auto-picked if you omit this."
    },
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default: current map)"
    },
    "confirm": {
      "type": "boolean",
      "description": "Fetch the full output even when it exceeds the large-output guard (~25k chars)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **30**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 10 × `object` with keys: `_paused`, `bounds`, `grid`, `layer`, `legend`, `loaded`, `mapIndex`, `orientation`, `scale`. Example: `campaigns/continuance/reference/legacy/history.jsonl:87`.
- 7 × `object` with keys: `_paused`, `bounds`, `cells`, `loaded`, `mapIndex`, `terrainSummary`, `thingCount`, `things`. Example: `campaigns/continuance/reference/legacy/history.jsonl:99`.
- 4 × `object` with keys: `_paused`, `bounds`, `cells`, `forbiddenSplit`, `loaded`, `mapIndex`, `mode`, `terrainSummary`, `thingCount`, `thingGroups`. Example: `campaigns/continuance/reference/legacy/history.jsonl:268`.
- 2 × `object` with keys: `_paused`, `area`, `availableAreas`, `bounds`, `grid`, `layer`, `legend`, `loaded`, `mapIndex`, `orientation`, `scale`. Example: `campaigns/continuance/reference/legacy/history.jsonl:702`.
- 2 × `object` with keys: `_paused`, `_threatWarning`, `bounds`, `grid`, `layer`, `legend`, `loaded`, `mapIndex`, `orientation`, `scale`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1590`.
- 2 × `object` with keys: `_paused`, `chars`, `items`, `largeOutput`, `message`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1990`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `bounds`, `cells`, `loaded`, `mapIndex`, `terrainSummary`, `thingCount`, `things`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1999`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `bounds`, `grid`, `layer`, `legend`, `loaded`, `mapIndex`, `orientation`, `scale`. Example: `campaigns/continuance/reference/legacy/history.jsonl:2072`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `bounds`, `cells`, `loaded`, `mapIndex`, `terrainSummary`, `thingCount`, `things`. Example: `campaigns/continuance/reference/legacy/history.jsonl:2089`.

Observed selector combinations: `{}` (26), `{"summary": true}` (4).

All **128** nested observed paths, type counts and provenance are in `inventory.json` → `tools.get_area.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## list_unmanaged_items

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/EntityTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/EntityTools.cs`) registration line 90 → `Collect = ListUnmanagedItems` (method line 3045). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Items that need attention: every FORBIDDEN item on the map (marked forbidden=true — a human/AI-designated 'do not touch'; inspect_thing + do_thing_action toggles its Allow/Forbid gizmo) PLUS every haulable item lying loose on the ground — not inside any stockpile zone or storage building (rows without 'forbidden' are the loose ones). This is what to check right after colony start, after a raid/trade, or after unpacking a caravan, to decide what to haul or unforbid; each row has def/label/position/count so you can act on it directly (designate a haul, order_pawn, or set up/expand a stockpile so it gets hauled automatically).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default: current map)"
    },
    "limit": {
      "type": "integer",
      "description": "Max rows to return (default 300)"
    },
    "confirm": {
      "type": "boolean",
      "description": "Fetch the full output even when it exceeds the large-output guard (~25k chars)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **1**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `_dialogOpen`, `_paused`, `chars`, `items`, `largeOutput`, `message`. Example: `campaigns/continuance/reference/legacy/history.jsonl:78`.

Observed selector combinations: `{}` (1).

All **7** nested observed paths, type counts and provenance are in `inventory.json` → `tools.list_unmanaged_items.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## list_fires

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/EntityTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/EntityTools.cs`) registration line 102 → `Collect = ListFires` (method line 1607). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Where is it burning: every fire on a map — total count and size, how many burn inside the home area, the burning area's bounding box, and the biggest fires with their cell and what they are attached to (a pawn or building on fire). fireCount=0 means nothing is burning. Use during/after a 'fire' message to decide where to send firefighters. NOTE: pawns auto-extinguish fires ONLY inside the home area; fires outside it burn unattended until they spread or burn out. If fires keep breaking out outside the home area, extinguish them manually (draft colonists and order them onto the fire) or expand the home area to cover the spot.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default: current map)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **11**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 2 × `object` with keys: `_paused`, `_threatWarning`, `bounds`, `fireCount`, `fires`, `firesInHomeArea`, `mapIndex`, `ok`, `totalFireSize`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1704`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `bounds`, `fireCount`, `fires`, `firesInHomeArea`, `mapIndex`, `note`, `ok`, `totalFireSize`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1790`.
- 1 × `object` with keys: `_paused`, `bounds`, `fireCount`, `fires`, `firesInHomeArea`, `mapIndex`, `note`, `ok`, `totalFireSize`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1845`.
- 1 × `object` with keys: `_paused`, `bounds`, `fireCount`, `fires`, `firesInHomeArea`, `mapIndex`, `ok`, `totalFireSize`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1874`.
- 5 × `object` with keys: `_paused`, `fireCount`, `mapIndex`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1883`.
- 1 × `object` with keys: `_notifications`, `_paused`, `bounds`, `fireCount`, `fires`, `firesInHomeArea`, `mapIndex`, `ok`, `totalFireSize`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1921`.

Observed selector combinations: `{}` (11).

All **44** nested observed paths, type counts and provenance are in `inventory.json` → `tools.list_fires.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## get_conditions

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/EntityTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/EntityTools.cs`) registration line 108 → `Collect = GetConditions` (method line 1737). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Current map conditions — what the player reads in the bottom-right HUD: in-game date/hour/season, current weather (with rain/snow/wind rates), outdoor + seasonal-average temperature, natural sky light 0..1 (night, eclipse and fallout dim it — solar panels track it), whether outdoor crops can grow RIGHT NOW (growingSeasonNow), and every active game condition affecting the map (eclipse, solar flare, toxic fallout, cold snap, psychic drone…) with hours remaining. Check before planning outdoor work, sowing, caravans or solar power, and when something feels off (a listed condition often explains it).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default: current map)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **1**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `_paused`, `conditions`, `conditionsNote`, `date`, `dayOfSeason`, `growingSeasonNow`, `hour`, `loaded`, `mapIndex`, `season`, `seasonLabel`, `skyGlow`, `temperature`, `weather`, `year`. Example: `campaigns/continuance/reference/legacy/history.jsonl:181`.

Observed selector combinations: `{}` (1).

All **23** nested observed paths, type counts and provenance are in `inventory.json` → `tools.get_conditions.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## get_room

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/EntityTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/EntityTools.cs`) registration line 114 → `Collect = GetRoom` (method line 1885). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Evaluate the room containing a cell ('x'+'z') or a thing ('id'): role (bedroom/dining room/…), temperature, owners, and every room stat the human sees (impressiveness, wealth, space, beauty, cleanliness, …) with score and quality stage — PLUS 'floor' (per-terrain cell counts with each terrain's Beauty stat) and 'detractors': the negative-beauty things, filth, AND bare/rough flooring (detractors.negativeBeautyFloor) inside that are dragging the scores down, so you know exactly what to clean/remove/re-floor to improve the room.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "x": {
      "type": "integer",
      "description": "Cell X inside the room (with z)"
    },
    "z": {
      "type": "integer",
      "description": "Cell Z inside the room (with x)"
    },
    "id": {
      "type": "string",
      "description": "A thing inside the room (alternative to x+z), e.g. a bed's ThingID"
    },
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default: current map)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **7**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 6 × `object` with keys: `_paused`, `cellCount`, `detractors`, `floor`, `loaded`, `mapIndex`, `outdoors`, `properRoom`, `role`, `stats`, `temperature`. Example: `campaigns/continuance/reference/legacy/history.jsonl:179`.
- 1 × `object` with keys: `_paused`, `cellCount`, `detractors`, `floor`, `loaded`, `mapIndex`, `outdoors`, `owners`, `properRoom`, `role`, `stats`, `temperature`. Example: `campaigns/continuance/reference/legacy/history.jsonl:306`.

Observed selector combinations: `{}` (7).

All **36** nested observed paths, type counts and provenance are in `inventory.json` → `tools.get_room.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## inspect_thing

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/EntityTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/EntityTools.cs`) registration line 126 → `Collect = InspectThing` (method line 2135). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Select a thing (pawn, item, building) the way a player click does, and return its info plus everything the bottom-right UI would show: 'actions' (info-card button, gizmos like Draft, and reverse designators like Cut/Extract tree, Mine, Deconstruct) and 'tabs' (e.g. for a pawn: Health, Gear, Bio, Social, Needs, Log, Restrict). Toggle gizmos (draft, forbid/allow, …) carry 'toggle':true, 'active' (the CURRENT on/off state) and a 'toggleHint' — executing one FLIPS it, so check 'active' first; the thing's own state is also stated directly ('drafted' on pawns, 'allowed' on forbiddable things). Also selects the thing in the live game UI (best-effort). Buildings carry 'effectZones' — the ranges/cells a human sees as selection overlays: watch cells (TV/horseshoe pin), gravship thruster exhaust clearance (with current blockage), IED blast radius, turret range and mortar dead zone, deep drill reach, facility link range, grav engine substructure radius, interaction cell, and placement rules; its 'drawnOverlays' is a raw capture of every ring/zone/connection-line overlay the game draws for this building's selection and placement ghost, so modded buildings' ranges show up too. Identify by 'id' (ThingID), or by 'x'+'z' cell coordinates. Fogged things cannot be inspected.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Thing ThingID (preferred, from list_things/get_area)"
    },
    "x": {
      "type": "integer",
      "description": "Cell X (used with z when no id given)"
    },
    "z": {
      "type": "integer",
      "description": "Cell Z (used with x when no id given)"
    },
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default: current map)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **53**. Explicit error-marker records: **2**.

Root-key variants (counts are evidence records):

- 11 × `object` with keys: `_paused`, `actions`, `category`, `def`, `faction`, `growth`, `growthFraction`, `harvestable`, `hitPoints`, `hostile`, `id`, `inspectString`, `label`, `loaded`, `maxHitPoints`, `rotation`, `rotationInt`, `tabs`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:230`.
- 10 × `object` with keys: `_paused`, `actions`, `category`, `def`, `effectZones`, `faction`, `hitPoints`, `hostile`, `id`, `inspectString`, `label`, `loaded`, `maxHitPoints`, `quality`, `rotation`, `rotationInt`, `tabs`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:298`.
- 5 × `object` with keys: `_paused`, `actions`, `category`, `def`, `effectZones`, `faction`, `hitPoints`, `hostile`, `id`, `inspectString`, `interactionCell`, `label`, `loaded`, `maxHitPoints`, `rotation`, `rotationInt`, `tabs`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:459`.
- 3 × `object` with keys: `_paused`, `actions`, `category`, `dead`, `def`, `downed`, `drafted`, `faction`, `hostile`, `id`, `inspectString`, `kind`, `label`, `loaded`, `rotation`, `rotationInt`, `tabs`, `tabsHint`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:460`.
- 1 × `object` with keys: `_paused`, `actions`, `category`, `def`, `effectZones`, `faction`, `hitPoints`, `hostile`, `id`, `inspectString`, `interactionCell`, `label`, `loaded`, `maxHitPoints`, `tabs`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:574`.
- 1 × `object` with keys: `_paused`, `actions`, `category`, `dead`, `def`, `downed`, `faction`, `hostile`, `id`, `inspectString`, `kind`, `label`, `loaded`, `rotation`, `rotationInt`, `tabs`, `tabsHint`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:587`.
- 1 × `object` with keys: `_paused`, `actions`, `allowed`, `builds`, `category`, `construction`, `costList`, `def`, `faction`, `hostile`, `id`, `inspectString`, `label`, `loaded`, `rotation`, `rotationInt`, `tabs`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:751`.
- 4 × `object` with keys: `_paused`, `actions`, `category`, `def`, `effectZones`, `faction`, `hostile`, `id`, `inspectString`, `label`, `loaded`, `rotation`, `rotationInt`, `tabs`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:824`.
- 2 × `object` with keys: `_paused`, `error`. Example: `campaigns/continuance/reference/legacy/history.jsonl:991`.
- 5 × `object` with keys: `_paused`, `actions`, `category`, `def`, `effectZones`, `faction`, `hitPoints`, `hostile`, `id`, `inspectString`, `label`, `loaded`, `maxHitPoints`, `tabs`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1227`.
- 2 × `object` with keys: `_paused`, `actions`, `allowed`, `category`, `def`, `faction`, `hitPoints`, `hostile`, `id`, `inspectString`, `label`, `loaded`, `maxHitPoints`, `tabs`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1307`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `actions`, `category`, `def`, `effectZones`, `faction`, `hitPoints`, `hostile`, `id`, `inspectString`, `label`, `loaded`, `maxHitPoints`, `tabs`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1361`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `actions`, `category`, `def`, `faction`, `hostile`, `id`, `inspectString`, `label`, `loaded`, `rotation`, `rotationInt`, `tabs`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1595`.
- 2 × `object` with keys: `_paused`, `_threatWarning`, `actions`, `category`, `def`, `effectZones`, `faction`, `hostile`, `id`, `inspectString`, `label`, `loaded`, `rotation`, `rotationInt`, `tabs`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1607`.
- 1 × `object` with keys: `_paused`, `actions`, `carriedBy`, `category`, `dead`, `def`, `downed`, `faction`, `hostile`, `id`, `inspectString`, `kind`, `label`, `loaded`, `rotation`, `rotationInt`, `tabs`, `tabsHint`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1617`.
- 1 × `object` with keys: `_paused`, `actions`, `allowed`, `builds`, `category`, `construction`, `costList`, `def`, `faction`, `hostile`, `id`, `inspectString`, `label`, `loaded`, `tabs`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1974`.
- 1 × `object` with keys: `_paused`, `actions`, `category`, `def`, `faction`, `growth`, `growthFraction`, `harvestable`, `hitPoints`, `hostile`, `id`, `inspectString`, `label`, `loaded`, `maxHitPoints`, `tabs`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:2037`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `actions`, `allowed`, `category`, `def`, `door`, `faction`, `hitPoints`, `hostile`, `id`, `label`, `loaded`, `maxHitPoints`, `tabs`, `uiSelected`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:2094`.

Observed selector combinations: `{}` (53).

All **131** nested observed paths, type counts and provenance are in `inventory.json` → `tools.inspect_thing.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## get_info_card

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/EntityTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/EntityTools.cs`) registration line 138 → `Collect = GetInfoCard` (method line 154). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

The detailed info-card content shown by the 'i' button: description plus the full stat list (grouped by category, each stat's label and value). Identify a spawned thing by 'id' or 'x'+'z', or query a def directly with 'def' (+ optional 'stuff' material).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Thing ThingID"
    },
    "x": {
      "type": "integer",
      "description": "Cell X (with z)"
    },
    "z": {
      "type": "integer",
      "description": "Cell Z (with x)"
    },
    "def": {
      "type": "string",
      "description": "ThingDef defName to inspect as a def (instead of a spawned thing)"
    },
    "stuff": {
      "type": "string",
      "description": "Material ThingDef defName (with def, for stuffed items)"
    },
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default: current map)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **4**. Explicit error-marker records: **1**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `_paused`, `error`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1324`.
- 3 × `object` with keys: `_paused`, `def`, `description`, `label`, `loaded`, `stats`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1382`.

Observed selector combinations: `{}` (4).

All **14** nested observed paths, type counts and provenance are in `inventory.json` → `tools.get_info_card.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## list_main_buttons

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ActionTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ActionTools.cs`) registration line 67 → `Collect = ListMainButtons` (method line 822). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

List the bottom main-button row (Architect, Work, Restrict, Assign, Schedule, Wildlife, Research, Quests, World, History, Menu, …) with defName and label.

### Declared input schema

```json
{
  "type": "object",
  "properties": {}
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## list_architect

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ActionTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ActionTools.cs`) registration line 72 → `Collect = ListArchitect` (method line 857). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

List Architect content. With no args: the categories (Orders, Structure, Production, …). With 'category' (defName): the designators/buildables in it, each with a stable 'type' (designator class) and, for buildables, 'buildDef' (use it with the build tool). Buildables also carry 'placement' when they have placement rules or effect ranges a human would see as overlays: interactionCell (the cell pawns stand on to use it), watchArea (TV/horseshoe pin usage cells), exhaustClearance (gravship thruster), explosion (IED blast radius), turret range/minRange (mortar dead zone), effectRadius (deep drill/sun lamp), facility link range, substructureRadius (grav engine), and placeRules (constraints like 'must not be under a roof'). Check it BEFORE placing anything that needs clear surrounding space.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "category": {
      "type": "string",
      "description": "DesignationCategoryDef defName to expand (optional)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **8**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 8 × `object` with keys: `_paused`, `category`, `designators`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:84`.

Observed selector combinations: `{"category": "Orders"}` (1), `{"category": "Zone"}` (1), `{"category": "Furniture"}` (1), `{"category": "Joy"}` (1), `{"category": "Misc"}` (1), `{"category": "Production"}` (1), `{"category": "Security"}` (1), `{"category": "Odyssey"}` (1).

All **69** nested observed paths, type counts and provenance are in `inventory.json` → `tools.list_architect.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## do_thing_action

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ActionTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ActionTools.cs`) registration line 78 → `Collect = DoThingAction` (method line 981). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Execute one of the actions returned by inspect_thing on a thing — a gizmo (e.g. Draft) or a reverse designator (e.g. Cut/Extract tree). Identify the thing by 'id' and the action by 'label' (case-insensitive) or 'index' (matching inspect_thing's actions order). TOGGLES: a toggle gizmo (draft, forbid/allow, …) FLIPS its state — check the action's 'active' field from inspect_thing first if you want a specific end state; the result reports 'nowActive' (the state AFTER the click) so the outcome is never ambiguous. A dropdown gizmo (e.g. 'set plant to grow', a mortar's shell choice) opens a menu: its options come back in this result ('openedFloatMenu' + 'options'; the menu is pinned so the human's mouse cannot dismiss it) — pick one with window_action option=<label or index>. For bed/throne owners use assign_building instead. PLACEMENT gizmos — Install (a minified/uninstalled item) and Reinstall (a placed minifiable building) — need a destination: pass 'targetX'+'targetZ' (+ optional 'rot' 0-3) and the install/reinstall blueprint is placed there, exactly like a human clicking the destination cell; invalid spots return the game's own rejection reason.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Thing ThingID"
    },
    "label": {
      "type": "string",
      "description": "Action label to run (case-insensitive)"
    },
    "index": {
      "type": "integer",
      "description": "Action index from inspect_thing.actions (alternative to label)"
    },
    "targetId": {
      "type": "string",
      "description": "Optional: direct a designator/targeted action at another thing"
    },
    "targetX": {
      "type": "integer",
      "description": "Optional: direct the action at a cell X (with targetZ) — required for Install/Reinstall"
    },
    "targetZ": {
      "type": "integer",
      "description": "Optional: direct the action at a cell Z (with targetX)"
    },
    "rot": {
      "type": "integer",
      "description": "Optional rotation 0-3 (N/E/S/W) for placement designators like Install/Reinstall (default: the def's default; non-rotatable defs are forced North)"
    }
  },
  "required": [
    "id"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **21**. Explicit error-marker records: **2**.

Root-key variants (counts are evidence records):

- 6 × `object` with keys: `_paused`, `blueprint`, `blueprintId`, `executed`, `kind`, `label`, `ok`, `redirected`. Example: `campaigns/continuance/reference/legacy/history.jsonl:300`.
- 5 × `object` with keys: `_paused`, `executed`, `hint`, `kind`, `label`, `ok`, `openedFloatMenu`, `options`. Example: `campaigns/continuance/reference/legacy/history.jsonl:392`.
- 2 × `object` with keys: `_paused`, `error`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:463`.
- 2 × `object` with keys: `_dialogOpen`, `_paused`, `executed`, `kind`, `label`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:588`.
- 2 × `object` with keys: `_paused`, `executed`, `kind`, `label`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:878`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `executed`, `hint`, `kind`, `label`, `ok`, `openedFloatMenu`, `options`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1608`.
- 3 × `object` with keys: `_paused`, `executed`, `kind`, `label`, `nowActive`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1636`.

Observed selector combinations: `{}` (21).

All **35** nested observed paths, type counts and provenance are in `inventory.json` → `tools.do_thing_action.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## designate

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ActionTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ActionTools.cs`) registration line 93 → `Collect = Designate` (method line 1419). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Apply a designator (orders): cut/mine/hunt/harvest/deconstruct/etc., and zones (stockpile/growing). Identify the designator by 'designator' (its class name from list_architect, e.g. 'Designator_Mine', or its label). Target one thing ('id'), one cell ('x'+'z'), or a drag rectangle ('minX/minZ/maxX/maxZ') with 'fill'='filled' (every cell) or 'outline' (perimeter only). IMPORTANT: rectangles can partially fail — always check 'rejected'; failures come back as 'warning', 'reasons' (most-frequent first) and 'failedCells' [{x,z,reason}]. For editing AREAS (制限エリア: home/roof/snow-clear/pollution-clear/allowed areas) prefer 'manage_area' instead — it addresses areas by label, shows the paint on-screen, and adds create/clear/invert/rename/delete.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "designator": {
      "type": "string",
      "description": "Designator class name (e.g. Designator_Mine) or label"
    },
    "id": {
      "type": "string",
      "description": "Target thing ThingID"
    },
    "x": {
      "type": "integer",
      "description": "Target cell X"
    },
    "z": {
      "type": "integer",
      "description": "Target cell Z"
    },
    "minX": {
      "type": "integer",
      "description": "Rectangle min X"
    },
    "minZ": {
      "type": "integer",
      "description": "Rectangle min Z"
    },
    "maxX": {
      "type": "integer",
      "description": "Rectangle max X"
    },
    "maxZ": {
      "type": "integer",
      "description": "Rectangle max Z"
    },
    "fill": {
      "type": "string",
      "enum": [
        "filled",
        "outline"
      ],
      "description": "Rectangle fill mode (default filled)"
    },
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default current)"
    }
  },
  "required": [
    "designator"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **112**. Explicit error-marker records: **3**.

Root-key variants (counts are evidence records):

- 33 × `object` with keys: `_paused`, `applied`, `cells`, `designator`, `failedCells`, `ok`, `reasons`, `rejected`, `target`, `warning`. Example: `campaigns/continuance/reference/legacy/history.jsonl:88`.
- 66 × `object` with keys: `_paused`, `applied`, `designator`, `ok`, `target`. Example: `campaigns/continuance/reference/legacy/history.jsonl:92`.
- 1 × `object` with keys: `_notifications`, `_paused`, `applied`, `cells`, `designator`, `ok`, `rejected`, `target`. Example: `campaigns/continuance/reference/legacy/history.jsonl:97`.
- 10 × `object` with keys: `_paused`, `applied`, `cells`, `designator`, `ok`, `rejected`, `target`. Example: `campaigns/continuance/reference/legacy/history.jsonl:107`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `applied`, `cells`, `designator`, `failedCells`, `ok`, `reasons`, `rejected`, `target`, `warning`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1063`.
- 1 × `object` with keys: `_paused`, `error`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:2022`.

Observed selector combinations: `{}` (112).

All **33** nested observed paths, type counts and provenance are in `inventory.json` → `tools.designate.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## build

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ActionTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ActionTools.cs`) registration line 111 → `Collect = Build` (method line 1704). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Place a building or floor (Architect → Build). Give 'def' — a ThingDef (Wall, Bed, …) or a TerrainDef floor (WoodPlankFloor, PavedTile, Concrete, …) — and a target: a single cell ('x'+'z'), or a drag rectangle ('minX/minZ/maxX/maxZ') with 'fill'='filled' (every cell, e.g. floors) or 'outline' (perimeter only, e.g. room walls). Optional 'rot' (0-3) and 'stuff' (material defName; a sensible default is chosen if omitted). Normally places blueprints; in god mode (or zero work-to-build) it spawns the finished building directly, skipping research requirements and consuming no materials. Multi-cell defs extend from the given cell as their Position; the result reports 'size' [w,h] and the occupied 'footprint'. Single-cell results also report 'placement' — the concrete cells/radii the building needs or affects at that spot (interaction cell, watch cells, thruster exhaust clearance incl. whether it is currently blocked, blast radius, …); keep those cells clear. Its 'drawnOverlays' is a raw capture of every overlay the game would draw for this ghost (radius rings, cell zones, connection lines) — it covers modded buildings too. Use list_architect to read a def's 'size' and 'placement' before placing. IMPORTANT: rectangle placement can partially fail — always check 'rejected'; failures come back as 'warning', 'reasons' (most-frequent first) and 'failedCells' [{x,z,reason}].

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "def": {
      "type": "string",
      "description": "Buildable def: a ThingDef (Wall, Bed) or a floor TerrainDef (WoodPlankFloor, PavedTile)"
    },
    "x": {
      "type": "integer",
      "description": "Cell X (single-cell placement)"
    },
    "z": {
      "type": "integer",
      "description": "Cell Z (single-cell placement)"
    },
    "minX": {
      "type": "integer",
      "description": "Rectangle min X (drag placement)"
    },
    "minZ": {
      "type": "integer",
      "description": "Rectangle min Z"
    },
    "maxX": {
      "type": "integer",
      "description": "Rectangle max X"
    },
    "maxZ": {
      "type": "integer",
      "description": "Rectangle max Z"
    },
    "fill": {
      "type": "string",
      "enum": [
        "filled",
        "outline"
      ],
      "description": "Rectangle fill mode (default filled)"
    },
    "rot": {
      "type": "integer",
      "description": "Rotation 0-3 (N/E/S/W; default: the def's default facing). Non-rotatable defs ignore this and use their fixed rotation"
    },
    "stuff": {
      "type": "string",
      "description": "Material ThingDef defName (optional; must be a stuff the def accepts — an invalid choice is rejected with the allowed list)"
    },
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default current)"
    }
  },
  "required": [
    "def"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **90**. Explicit error-marker records: **12**.

Root-key variants (counts are evidence records):

- 2 × `object` with keys: `_paused`, `cells`, `def`, `directPlacements`, `failedCells`, `fill`, `ok`, `placed`, `reasons`, `rejected`, `rot`, `size`, `stuff`, `target`, `warning`. Example: `campaigns/continuance/reference/legacy/history.jsonl:91`.
- 19 × `object` with keys: `_paused`, `blueprintId`, `def`, `direct`, `footprint`, `ok`, `placed`, `rot`, `size`, `stuff`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:93`.
- 32 × `object` with keys: `_paused`, `blueprintId`, `def`, `direct`, `footprint`, `ok`, `placed`, `placement`, `rot`, `size`, `stuff`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:94`.
- 3 × `object` with keys: `_paused`, `def`, `direct`, `footprint`, `ok`, `placed`, `rot`, `size`, `stuff`, `thingId`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:168`.
- 8 × `object` with keys: `_paused`, `def`, `direct`, `footprint`, `ok`, `placed`, `placement`, `reason`, `rot`, `size`, `stuff`, `warning`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:185`.
- 16 × `object` with keys: `_paused`, `cells`, `def`, `directPlacements`, `fill`, `ok`, `placed`, `reasons`, `rejected`, `rot`, `size`, `stuff`, `target`. Example: `campaigns/continuance/reference/legacy/history.jsonl:193`.
- 1 × `object` with keys: `_paused`, `def`, `direct`, `footprint`, `note`, `ok`, `placed`, `placement`, `rot`, `size`, `stuff`, `thingId`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:602`.
- 4 × `object` with keys: `_paused`, `def`, `direct`, `footprint`, `ok`, `placed`, `reason`, `rot`, `size`, `stuff`, `warning`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1037`.
- 1 × `object` with keys: `_paused`, `def`, `direct`, `footprint`, `ok`, `placed`, `placement`, `rot`, `size`, `stuff`, `thingId`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1208`.
- 1 × `object` with keys: `_paused`, `blueprintId`, `def`, `direct`, `footprint`, `note`, `ok`, `placed`, `rot`, `size`, `stuff`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1388`.
- 2 × `object` with keys: `_paused`, `_threatWarning`, `blueprintId`, `def`, `direct`, `footprint`, `ok`, `placed`, `rot`, `size`, `stuff`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1591`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `def`, `direct`, `footprint`, `ok`, `placed`, `rot`, `size`, `stuff`, `thingId`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1593`.

Observed selector combinations: `{}` (90).

All **101** nested observed paths, type counts and provenance are in `inventory.json` → `tools.build.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## set_work_priority

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ActionTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ActionTools.cs`) registration line 130 → `Collect = SetWorkPriority` (method line 2161). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Set a colonist's work priority (Work tab). 'workType' is a WorkTypeDef defName (e.g. Doctor, Cooking, Mining); 'priority' 0 disables, 1 (highest) to 4 (lowest). Identify the colonist by 'id' or 'name'. Setting a priority above 1 automatically turns on manual (numeric) priorities for the whole colony; the result's 'manualPrioritiesEnabled' reports the current mode.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Colonist ThingID"
    },
    "name": {
      "type": "string",
      "description": "Colonist name (case-insensitive)"
    },
    "workType": {
      "type": "string",
      "description": "WorkTypeDef defName"
    },
    "priority": {
      "type": "integer",
      "description": "0=disabled, 1=highest .. 4=lowest"
    }
  },
  "required": [
    "workType",
    "priority"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **102**. Explicit error-marker records: **3**.

Root-key variants (counts are evidence records):

- 93 × `object` with keys: `_paused`, `manualPrioritiesEnabled`, `ok`, `pawn`, `priority`, `workType`. Example: `campaigns/continuance/reference/legacy/history.jsonl:111`.
- 3 × `object` with keys: `_paused`, `error`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:114`.
- 6 × `object` with keys: `_paused`, `_threatWarning`, `manualPrioritiesEnabled`, `ok`, `pawn`, `priority`, `workType`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1793`.

Observed selector combinations: `{}` (102).

All **25** nested observed paths, type counts and provenance are in `inventory.json` → `tools.set_work_priority.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## wait_for_event

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ActionTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ActionTools.cs`) registration line 142 → `Background = WaitForEvent` (method line 719). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Advance time until something notable happens, then return the cause. Triggers: a new letter or a notable on-screen message (e.g. fire, a colonist needing rescue), a hostile-count transition — cause 'threatAppeared' when hostiles show up on a map that had none, 'threatsCleared' when the last hostile is downed/dead/gone (a battle was won) — a forced pause (dialog/cutscene), the on-screen 'Pause & return to AI' button, or a timeout. A plain user pause does NOT end the wait, and the human may freely change the speed while waiting. On an event the game is paused; on a plain timeout it is NOT paused. The wait speed is configured in the mod settings. Starting a wait closes any UI the AI opened (main tabs, inspect tabs, dropdowns). Returns { event, cause, ticksWaited, time } where time is the current in-game date/hour/season; weatherChanged {from,to} appears when the map weather changed during the wait. The triggering letters/messages arrive in the result's _notifications, and _delta summarizes what changed while waiting (newItems/removedItems resource counts; newBuildings/removedBuildings for constructions finished and walls/furniture/rock destroyed, deconstructed or mined; pawnDamage with hp before/after and new injuries; keys absent when nothing changed). Blocks until one of these occurs. CRISIS CAP: if a crisis already exists when the wait begins — hostiles on a map, fire burning in the home area (pawns auto-firefight only there; fires outside the home area must be extinguished manually — see list_fires), or a colonist with a life-threatening condition — the in-game time budget is capped at 1 hour (2500 ticks) regardless of maxGameTicks/Seconds/Hours/Days, so you can't accidentally fast-forward past it; the result's 'crisisCap' reports why. Pass force=true to bypass the cap and wait the full requested time anyway. 'pause' controls what happens to game speed when the wait ends (default 'auto'); a mod setting can disable end-of-wait pausing entirely (overriding 'pause') — the result's 'pausedAfter' always reports what actually happened.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "maxSeconds": {
      "type": "integer",
      "description": "Real-time timeout in seconds (default 60, range 5-600). The default timeout is real-time."
    },
    "maxGameTicks": {
      "type": "number",
      "description": "Optional in-game tick timeout (0 = no tick limit). 2500 ticks = 1 in-game hour, 60000 = 1 day."
    },
    "maxGameSeconds": {
      "type": "number",
      "description": "Optional in-game-clock second timeout (3600 in-game seconds = 1 in-game hour = 2500 ticks; converted to ticks and combined with maxGameTicks). Note in-game seconds are short — ~0.7 ticks each — so a few seconds is only a handful of ticks."
    },
    "maxGameHours": {
      "type": "number",
      "description": "Optional in-game hour timeout (converted to ticks; combined with maxGameTicks). Fractions work: 0.1 = 250 ticks."
    },
    "maxGameDays": {
      "type": "number",
      "description": "Optional in-game day timeout (converted to ticks; combined with maxGameTicks). Fractions work: 0.5 = half a day."
    },
    "force": {
      "type": "boolean",
      "description": "Bypass the crisis time cap (default false). Without it, waits started while hostiles are on the map, fire is in the home area, or a colonist has a life-threatening condition are capped at 1 in-game hour."
    },
    "pause": {
      "type": "string",
      "enum": [
        "auto",
        "always",
        "never"
      ],
      "description": "Pause behavior when the wait ends: 'auto' (default — pause on an event, resume at the unpause speed on a plain timeout), 'always' (pause on every stop cause), or 'never' (never pause; always resume at the unpause speed)."
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **309**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 30 × `object` with keys: `_paused`, `cause`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`. Example: `campaigns/continuance/reference/legacy/history.jsonl:81`.
- 21 × `object` with keys: `_notifications`, `_paused`, `cause`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`. Example: `campaigns/continuance/reference/legacy/history.jsonl:85`.
- 84 × `object` with keys: `_delta`, `_notifications`, `_paused`, `cause`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`. Example: `campaigns/continuance/reference/legacy/history.jsonl:158`.
- 51 × `object` with keys: `_delta`, `_paused`, `cause`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`. Example: `campaigns/continuance/reference/legacy/history.jsonl:170`.
- 12 × `object` with keys: `_delta`, `_dialogOpen`, `_paused`, `cause`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`. Example: `campaigns/continuance/reference/legacy/history.jsonl:219`.
- 4 × `object` with keys: `_delta`, `_dialogOpen`, `_notifications`, `_paused`, `cause`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`. Example: `campaigns/continuance/reference/legacy/history.jsonl:343`.
- 33 × `object` with keys: `_paused`, `_threatWarning`, `cause`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`. Example: `campaigns/continuance/reference/legacy/history.jsonl:381`.
- 2 × `object` with keys: `_dialogOpen`, `_paused`, `cause`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`. Example: `campaigns/continuance/reference/legacy/history.jsonl:420`.
- 9 × `object` with keys: `_delta`, `_notifications`, `_paused`, `cause`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`, `weatherChanged`. Example: `campaigns/continuance/reference/legacy/history.jsonl:451`.
- 12 × `object` with keys: `_delta`, `_notifications`, `_paused`, `_threatWarning`, `cause`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`. Example: `campaigns/continuance/reference/legacy/history.jsonl:666`.
- 34 × `object` with keys: `_delta`, `_paused`, `_threatWarning`, `cause`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`. Example: `campaigns/continuance/reference/legacy/history.jsonl:673`.
- 2 × `object` with keys: `_delta`, `_dialogOpen`, `_notifications`, `_paused`, `cause`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`, `weatherChanged`. Example: `campaigns/continuance/reference/legacy/history.jsonl:759`.
- 8 × `object` with keys: `_notifications`, `_paused`, `_threatWarning`, `cause`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`. Example: `campaigns/continuance/reference/legacy/history.jsonl:786`.
- 1 × `object` with keys: `_delta`, `_paused`, `_threatWarning`, `cause`, `crisisCap`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1454`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `cause`, `event`, `hostileCount`, `ok`, `pausedAfter`, `ticksWaited`, `time`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1565`.
- 1 × `object` with keys: `_delta`, `_paused`, `_threatWarning`, `cause`, `event`, `hostileCount`, `ok`, `pausedAfter`, `ticksWaited`, `time`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1583`.
- 2 × `object` with keys: `_delta`, `_notifications`, `_paused`, `cause`, `crisisCap`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1626`.
- 1 × `object` with keys: `_delta`, `_paused`, `_threatWarning`, `cause`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`, `weatherChanged`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1826`.
- 1 × `object` with keys: `_delta`, `_paused`, `cause`, `event`, `ok`, `pausedAfter`, `ticksWaited`, `time`, `weatherChanged`. Example: `campaigns/continuance/reference/legacy/history.jsonl:2066`.

Observed selector combinations: `{}` (309).

All **74** nested observed paths, type counts and provenance are in `inventory.json` → `tools.wait_for_event.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## set_speed

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ActionTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ActionTools.cs`) registration line 157 → `Collect = SetSpeed` (method line 780). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Pause or unpause the game. action='pause' stops time (issue orders safely); action='unpause' resumes at the speed configured in the mod settings (default: the last speed the human selected, falling back to Normal). Faster speeds are not exposed here — advancing time is wait_for_event's job (its speed is a mod setting). Returns the resulting speed and paused state.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": [
        "pause",
        "unpause"
      ],
      "description": "pause or unpause"
    }
  },
  "required": [
    "action"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **7**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 7 × `object` with keys: `_paused`, `action`, `ok`, `paused`, `speed`. Example: `campaigns/continuance/raw/obs-1de40584328f496591626f3e71f5f490.json`.

Observed selector combinations: `{"action": "pause"}` (7).

All **6** nested observed paths, type counts and provenance are in `inventory.json` → `tools.set_speed.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## order_pawn

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ActionTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ActionTools.cs`) registration line 163 → `Collect = OrderPawn` (method line 464). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Issue a right-click order to a pawn at a target — the float-menu options (go here, haul, attack, arrest, rescue, prioritize work, tend, etc.). Pawn by 'id'; target by 'targetId' or 'x'+'z'. Without 'command'/'index' it lists the available options; with one it executes it. By default the order replaces the pawn's current job immediately; pass queue=true (the human Shift-click) to append it after the current job and any previously queued orders instead — call repeatedly with queue=true to chain several orders. When the pawn is drafted and the target is hostile, the option list also includes 'Auto attack (AI): <target>' — pick it like any other order to start the non-vanilla combat AI (seeks cover, fires, repositions, or closes to melee) fixed on that one target for sustained combat, instead of re-issuing a one-shot attack order every tick; disabled when the pawn is unarmed/incapable of violence or the autoCombat mod setting is off.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Pawn ThingID (a player-controlled colonist)"
    },
    "targetId": {
      "type": "string",
      "description": "Target thing ThingID (or use x+z)"
    },
    "x": {
      "type": "integer",
      "description": "Target cell X"
    },
    "z": {
      "type": "integer",
      "description": "Target cell Z"
    },
    "command": {
      "type": "string",
      "description": "Option label to execute (case-insensitive)"
    },
    "index": {
      "type": "integer",
      "description": "Option index to execute (alternative to command)"
    },
    "queue": {
      "type": "boolean",
      "description": "Queue after the current job instead of replacing it (Shift-click equivalent)"
    }
  },
  "required": [
    "id"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **326**. Explicit error-marker records: **7**.

Root-key variants (counts are evidence records):

- 84 × `object` with keys: `_paused`, `mode`, `ok`, `options`, `pawn`, `target`. Example: `campaigns/continuance/reference/legacy/history.jsonl:161`.
- 84 × `object` with keys: `_paused`, `executed`, `label`, `ok`, `pawn`. Example: `campaigns/continuance/reference/legacy/history.jsonl:164`.
- 13 × `object` with keys: `_paused`, `executed`, `jobQueueLength`, `label`, `ok`, `pawn`, `queued`. Example: `campaigns/continuance/reference/legacy/history.jsonl:165`.
- 24 × `object` with keys: `_paused`, `_threatWarning`, `mode`, `ok`, `options`, `pawn`, `target`. Example: `campaigns/continuance/reference/legacy/history.jsonl:385`.
- 3 × `object` with keys: `_paused`, `error`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:628`.
- 112 × `object` with keys: `_paused`, `_threatWarning`, `executed`, `label`, `ok`, `pawn`. Example: `campaigns/continuance/reference/legacy/history.jsonl:670`.
- 2 × `object` with keys: `_paused`, `_threatWarning`, `error`, `label`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:796`.
- 2 × `object` with keys: `_dialogOpen`, `_paused`, `mode`, `ok`, `options`, `pawn`, `target`. Example: `campaigns/continuance/reference/legacy/history.jsonl:809`.
- 1 × `object` with keys: `_paused`, `available`, `error`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:872`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `available`, `error`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1724`.

Observed selector combinations: `{}` (326).

All **38** nested observed paths, type counts and provenance are in `inventory.json` → `tools.order_pawn.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## draft

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ActionTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ActionTools.cs`) registration line 178 → `Collect = DraftPawns` (method line 283). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Draft or undraft colonists in bulk — the human 'box-select everyone, press R' equivalent. action='draft' arms them for combat, action='undraft' releases them back to work. Default target: every spawned free colonist on every map; pass 'ids' (comma-separated ThingIDs) to target a subset (colony mechs work too). Pawns that cannot change state (downed, deathresting, mental break, uncontrollable mech, off-map) are skipped with the game's own reason while the rest still proceed — check 'skipped' in the result. Single-pawn draft stays available as the Draft toggle via inspect_thing + do_thing_action.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": [
        "draft",
        "undraft"
      ],
      "description": "draft = arm for combat, undraft = back to normal work"
    },
    "ids": {
      "type": "string",
      "description": "Optional comma-separated pawn ThingIDs to target instead of all colonists"
    }
  },
  "required": [
    "action"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **58**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 10 × `object` with keys: `_paused`, `action`, `alreadyInState`, `drafted`, `skipped`. Example: `campaigns/continuance/reference/legacy/history.jsonl:374`.
- 22 × `object` with keys: `_paused`, `action`, `alreadyInState`, `skipped`, `undrafted`. Example: `campaigns/continuance/reference/legacy/history.jsonl:390`.
- 6 × `object` with keys: `_notifications`, `_paused`, `action`, `alreadyInState`, `drafted`, `skipped`. Example: `campaigns/continuance/reference/legacy/history.jsonl:548`.
- 11 × `object` with keys: `_paused`, `_threatWarning`, `action`, `alreadyInState`, `drafted`, `skipped`. Example: `campaigns/continuance/reference/legacy/history.jsonl:668`.
- 3 × `object` with keys: `_notifications`, `_paused`, `_threatWarning`, `action`, `alreadyInState`, `drafted`, `skipped`. Example: `campaigns/continuance/reference/legacy/history.jsonl:929`.
- 1 × `object` with keys: `_notifications`, `_paused`, `action`, `alreadyInState`, `skipped`, `undrafted`. Example: `campaigns/continuance/reference/legacy/history.jsonl:952`.
- 5 × `object` with keys: `_paused`, `_threatWarning`, `action`, `alreadyInState`, `skipped`, `undrafted`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1149`.

Observed selector combinations: `{"action": "draft"}` (30), `{"action": "undraft"}` (28).

All **33** nested observed paths, type counts and provenance are in `inventory.json` → `tools.draft.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## set_research

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ActionTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ActionTools.cs`) registration line 188 → `Collect = SetResearch` (method line 196). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Set the colony's current research project (Research tab). 'project' is a ResearchProjectDef defName or label. Without 'project' it lists the projects that can be started now. Rejects projects that are finished or locked (missing prerequisites/tech level/techprints/buildings). Anomaly-tab (knowledge) projects are also set here: they occupy their own slot per knowledge category (Basic/Advanced), running in parallel with the bench project, and advance only when entities are studied (list_study_targets).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "project": {
      "type": "string",
      "description": "ResearchProjectDef defName or label (omit to list available)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **19**. Explicit error-marker records: **2**.

Root-key variants (counts are evidence records):

- 16 × `object` with keys: `_paused`, `cost`, `current`, `label`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:186`.
- 2 × `object` with keys: `_paused`, `error`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:286`.
- 1 × `object` with keys: `_paused`, `available`, `mode`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1275`.

Observed selector combinations: `{}` (19).

All **14** nested observed paths, type counts and provenance are in `inventory.json` → `tools.set_research.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## assign_building

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/AssignTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/AssignTools.cs`) registration line 15 → `Collect = AssignBuilding` (method line 28). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Assign or unassign a pawn to an assignable building — bed owners (incl. prisoner beds), thrones, graves, etc. (the 'Set owner' button, without the dialog). action='list' (default) shows current assignees and every candidate with whether/why they can be assigned; action='assign'/'unassign' with 'pawn' (id or name) changes the assignment. Assigning a bed moves the pawn's ownership (their previous bed is released automatically).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Building ThingID (a bed/throne/grave/… from list_things or get_area)"
    },
    "action": {
      "type": "string",
      "enum": [
        "list",
        "assign",
        "unassign"
      ],
      "description": "What to do (default list)"
    },
    "pawn": {
      "type": "string",
      "description": "Pawn ThingID or name (for assign/unassign)"
    }
  },
  "required": [
    "id"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **9**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 4 × `object` with keys: `_paused`, `assigned`, `building`, `candidates`, `forPrisoners`, `id`, `loaded`, `medical`, `slots`. Example: `campaigns/continuance/reference/legacy/history.jsonl:289`.
- 5 × `object` with keys: `_paused`, `action`, `assigned`, `building`, `candidates`, `forPrisoners`, `id`, `loaded`, `medical`, `ok`, `pawn`, `slots`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1002`.

Observed selector combinations: `{"action": "list"}` (4), `{"action": "assign"}` (5).

All **21** nested observed paths, type counts and provenance are in `inventory.json` → `tools.assign_building.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## list_wildlife

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/AnimalTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/AnimalTools.cs`) registration line 16 → `Collect = ListWildlife` (method line 48). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

The Wildlife tab: every wild animal on a map — id/kind/position/gender, whether it is marked for hunting or taming, 'revengeOnHarmPercent' (the human tab's manhunter-on-damage column: the chance the animal and its herd turn manhunter when hunted/hurt — check it BEFORE hunting), MANHUNTERS (mentalState present = dangerous), predators, plus per-kind info (count, predator, wildness%, trainability, tameable). Issue the actual orders with designate: designator=Designator_Hunt (or Designator_Tame) id=<animal id>.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default: current map)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **3**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 3 × `object` with keys: `_paused`, `animals`, `count`, `hint`, `kinds`, `loaded`, `mapIndex`. Example: `campaigns/continuance/reference/legacy/history.jsonl:617`.

Observed selector combinations: `{}` (3).

All **23** nested observed paths, type counts and provenance are in `inventory.json` → `tools.list_wildlife.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## list_animals

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/AnimalTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/AnimalTools.cs`) registration line 22 → `Collect = ListAnimals` (method line 188). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

The Animals tab: every animal of the colony across maps — id, name, kind, gender, age, bonded pawns, master, followDrafted/followFieldwork, allowed area, medical care, and each trainable skill's wanted/learned state. Change these with manage_animal.

### Declared input schema

```json
{
  "type": "object",
  "properties": {}
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **2**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 2 × `object` with keys: `_paused`, `animals`, `count`, `hint`, `loaded`. Example: `campaigns/continuance/reference/legacy/history.jsonl:173`.

Observed selector combinations: `{}` (2).

All **21** nested observed paths, type counts and provenance are in `inventory.json` → `tools.list_animals.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## manage_animal

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/AnimalTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/AnimalTools.cs`) registration line 29 → `Collect = ManageAnimal` (method line 305). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Configure a colony animal (Animals-tab settings). Identify by 'id' or 'name'. Any combination of: 'master' (a colonist id/name, or 'none'; requires obedience training), 'followDrafted'/'followFieldwork' (booleans; need a master), 'area' (an allowed-area name, or 'unrestricted'), 'train' (a trainable skill: Tameness/Obedience/Release/Rescue/Haul) with 'wanted' (default true) to set the training target.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Animal ThingID (from list_animals)"
    },
    "name": {
      "type": "string",
      "description": "Animal name (case-insensitive substring; alternative to id)"
    },
    "master": {
      "type": "string",
      "description": "New master: colonist id/name, or 'none' to clear"
    },
    "followDrafted": {
      "type": "boolean",
      "description": "Follow its master while drafted"
    },
    "followFieldwork": {
      "type": "boolean",
      "description": "Follow its master while doing field work"
    },
    "area": {
      "type": "string",
      "description": "Allowed area name, or 'unrestricted'"
    },
    "train": {
      "type": "string",
      "description": "TrainableDef defName or label (e.g. Obedience, Release, Haul, Rescue)"
    },
    "wanted": {
      "type": "boolean",
      "description": "With 'train': whether the skill should be trained (default true)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## list_power_grids

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/PowerTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/PowerTools.cs`) registration line 15 → `Collect = ListPowerGrids` (method line 23). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Verify everything is wired to a power grid, and find unpowered or unconnected devices. Lists every power net on the map: net gain in Watts ('gainWatts', production minus consumption of currently-on components), stored energy vs total battery capacity (in watt-days, the unit vanilla's own battery tooltip uses), and its components grouped by ThingDef — producers (rated Watts per unit, how many are currently producing), consumers (Watts each, how many are powered on / powered off / switched off), batteries (stored/max), and a transmitter (conduit) count. Each group carries one sample position so you can find it on the map. The headline feature is 'unconnected': every spawned building with a power component (generator, battery, or power-consuming building) that is NOT wired into any power net at all — a plugged-in-looking but actually disconnected building, most often from a broken conduit run. A top-level 'problems' array calls out unconnected buildings, nets whose consumption exceeds production with empty batteries, and switched-on consumers not currently receiving power, all in plain sentences.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default: current map)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **4**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 4 × `object` with keys: `_paused`, `loaded`, `mapIndex`, `netCount`, `nets`, `problems`, `unconnected`, `unconnectedCount`. Example: `campaigns/continuance/reference/legacy/history.jsonl:642`.

Observed selector combinations: `{}` (4).

All **45** nested observed paths, type counts and provenance are in `inventory.json` → `tools.list_power_grids.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## room_graph

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RoomTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RoomTools.cs`) registration line 17 → `Collect = GetRoomGraph` (method line 31). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Verify base room connectivity — sealed rooms, missing exits, rooms you forgot to connect — plus room quality stats. Builds a graph of the map's rooms: every proper room is a node (role, cell count, a representative cell to locate it, temperature, and — unless stats=false — the full room-stat readout: impressiveness, wealth, space, beauty, cleanliness, etc.); every room that is 'outdoors' (psychologically or literally) is merged into a single virtual 'outdoors' node; doors are the edges. Use this to find: rooms that are completely sealed (no door at all), rooms that connect to other rooms but never reach the outside (missing exterior door/hallway), and whether the base has any exit to the outdoors at all. Each node carries 'reachableFromOutside' (graph BFS over the door edges) AND a ground-truth 'canReachMapEdge' (vanilla's own Reachability.CanReachMapEdge, which also catches door-less gaps the door graph can't see) — when the two disagree that itself is informative and both are reported. Top-level 'problems' lists issues in plain sentences.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default: current map)"
    },
    "stats": {
      "type": "boolean",
      "description": "Include per-room quality stats (impressiveness/wealth/space/beauty/cleanliness/...). Default true."
    },
    "confirm": {
      "type": "boolean",
      "description": "Fetch the full output even when it exceeds the large-output guard (~25k chars)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **3**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 3 × `object` with keys: `_paused`, `edgeCount`, `edges`, `loaded`, `mapIndex`, `nodeCount`, `nodes`, `problems`, `sealedRoomCount`, `sealedRooms`. Example: `campaigns/continuance/reference/legacy/history.jsonl:641`.

Observed selector combinations: `{}` (3).

All **38** nested observed paths, type counts and provenance are in `inventory.json` → `tools.room_graph.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## set_ideo_role

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/IdeoRoleTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/IdeoRoleTools.cs`) registration line 15 → `Collect = SetIdeoRole` (method line 27). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Assign or remove ideoligion roles (Ideology DLC; the Social-tab role dropdown). Without args: list every role of the colony's ideoligions with current holders and each colonist's eligibility. With 'pawn' + 'role': assign that role (single-holder roles replace the previous holder — reported in the result). With 'pawn' + role='none': remove the pawn's current role.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "pawn": {
      "type": "string",
      "description": "Colonist ThingID or name"
    },
    "role": {
      "type": "string",
      "description": "Role name (e.g. 'moral guide', 'leader'; case-insensitive substring), or 'none' to unassign"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **6**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `_paused`, `hint`, `ideoligions`, `loaded`. Example: `campaigns/continuance/reference/legacy/history.jsonl:456`.
- 4 × `object` with keys: `_paused`, `apparelRequirements`, `assignedRole`, `ideoligion`, `ok`, `pawn`. Example: `campaigns/continuance/reference/legacy/history.jsonl:457`.
- 1 × `object` with keys: `_paused`, `ok`, `pawn`, `removedRole`. Example: `campaigns/continuance/reference/legacy/history.jsonl:650`.

Observed selector combinations: `{}` (6).

All **20** nested observed paths, type counts and provenance are in `inventory.json` → `tools.set_ideo_role.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## manage_gear

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GearTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GearTools.cs`) registration line 16 → `Collect = ManageGear` (method line 30). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Manage a colonist's gear/loadout (Gear tab). Read current gear with get_pawn (gear tab); this WRITES. Pawn by 'id'/'name'; target item by 'item' (a ThingID from the gear readout, or a defName). op: 'equip' = order the pawn to equip a weapon (from its inventory or the ground — a real walk-over job); 'wear' = order the pawn to put on apparel; 'drop' = drop the item (equipped weapon / worn apparel / inventory item) onto the ground; 'force' / 'unforce' = keep a worn apparel on regardless of the outfit policy (or stop keeping it). Returns the resolved item, where it was found, and what was ordered.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Colonist ThingID"
    },
    "name": {
      "type": "string",
      "description": "Colonist name (case-insensitive)"
    },
    "op": {
      "type": "string",
      "enum": [
        "equip",
        "wear",
        "drop",
        "force",
        "unforce"
      ],
      "description": "Operation"
    },
    "item": {
      "type": "string",
      "description": "Target item: a ThingID from the get_pawn gear readout, or a defName"
    }
  },
  "required": [
    "op",
    "item"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **6**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 6 × `object` with keys: `_paused`, `from`, `item`, `itemId`, `ok`, `op`, `ordered`, `pawn`. Example: `campaigns/continuance/reference/legacy/history.jsonl:155`.

Observed selector combinations: `{}` (6).

All **9** nested observed paths, type counts and provenance are in `inventory.json` → `tools.manage_gear.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## rename_pawn

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RenameTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RenameTools.cs`) registration line 13 → `Collect = RenamePawn` (method line 28). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Rename an existing colonist (requires the 'Let the AI rename colonists' mod setting). Colonist by 'id'/'name'; give at least one of 'first'/'nick'/'last' (nick is the short name shown in-game). Unspecified parts are kept. Animals with a name can also be renamed by 'id'.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Colonist (or named animal) ThingID"
    },
    "name": {
      "type": "string",
      "description": "Colonist current name (case-insensitive)"
    },
    "first": {
      "type": "string",
      "description": "First name"
    },
    "nick": {
      "type": "string",
      "description": "Nickname — the short name shown in-game"
    },
    "last": {
      "type": "string",
      "description": "Last name"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## list_genes

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GeneTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GeneTools.cs`) registration line 49 → `Collect = ListGenes` (method line 96). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Biotech genes overview. Without args: every colonist's xenotype + gene summary (metabolism/complexity totals), plus the colony's genepack LIBRARY (genepacks stored in gene banks, each with its genes, complexity/metabolism/archites and whether it is powered/deteriorating), any finished xenogerms lying on the map, and the gene assemblers (with max complexity from connected gene processors). With 'pawn': that colonist's full gene list — endogenes (inherited) and xenogenes (implanted) separately, each gene's biostats, plus xenotype name and any work types the genes disable. Use create_xenogerm to assemble a new xenogerm from library genepacks.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "pawn": {
      "type": "string",
      "description": "Colonist ThingID or name for a full per-pawn gene list (omit for the colony overview)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## create_xenogerm

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GeneTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GeneTools.cs`) registration line 55 → `Background = CreateXenogerm` (method line 387). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Assemble a xenogerm from stored genepacks at a gene assembler — the core 'edit a gene set' action. Drives the REAL vanilla 'Assemble genes' dialog visibly on screen (dialog opens, each chosen genepack is added one at a time with the biostats table updating, then Start combining is pressed). Requires Biotech, a built gene assembler with genepacks in connected gene banks. Without 'genepacks': lists the assembler(s) and every available library genepack (id, genes, complexity) so you can choose — the informed-choice gate. With 'genepacks' (comma-separated genepack ids/labels, or a JSON array): selects those, names the xenotype ('name', optional — auto-generated from the genes if omitted) and starts the recombination. Rejects selections over the assembler's max complexity, missing gene prerequisites, or archite genes without the Archogenetics research, reporting exactly why (vanilla's own gate). The finished xenogerm appears on the assembler's cell after the colony works on it; implant it with implant_xenogerm.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "assembler": {
      "type": "string",
      "description": "Gene assembler building ThingID (optional; defaults to the only/first assembler on the map)"
    },
    "genepacks": {
      "type": "string",
      "description": "Genepacks to combine: comma-separated ThingIDs or labels, or a JSON array. Omit to list available genepacks + assemblers."
    },
    "name": {
      "type": "string",
      "description": "Xenotype name for the result (optional; auto-generated from the genes if omitted)"
    },
    "mapIndex": {
      "type": "integer",
      "description": "Map index (optional; defaults to the current map)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## implant_xenogerm

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GeneTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GeneTools.cs`) registration line 67 → `Collect = ImplantXenogerm` (method line 614). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Order the implantation of a finished xenogerm into a colonist (prisoner/slave allowed) — vanilla's ImplantXenogerm operation. This OVERWRITES the target's existing xenogenes and puts them in a xenogermination coma for days, so it is treated as a consequential action: the first call REVIEWS it (reports the xenogerm's genes, the target's metabolism after implanting, and which current xenogenes would be lost) and requires confirm=true to actually queue the surgery bill. A colonist must then carry the xenogerm to the target and perform the operation (needs a medical bed + medicine). Give 'xenogerm' (a Xenogerm ThingID from list_genes) and 'pawn'.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "xenogerm": {
      "type": "string",
      "description": "Xenogerm ThingID (from list_genes 'xenogerms')"
    },
    "pawn": {
      "type": "string",
      "description": "Target colonist/prisoner/slave ThingID or name"
    },
    "confirm": {
      "type": "boolean",
      "description": "Set true to actually queue the implantation surgery bill (first call without it only reviews the effect)."
    }
  },
  "required": [
    "xenogerm",
    "pawn"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## list_mechs

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/MechTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/MechTools.cs`) registration line 17 → `Collect = ListMechs` (method line 55). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Biotech mechanitors + mechanoids overview. Lists each mechanitor colonist with bandwidth (used/total, and how much is spent on gestation vs. active mechs), their control groups (index, work mode, target, recharge thresholds, and the mechs in each), and any in-progress mech gestation bills. Also lists colony mechs that need an overseer but have none (feral risk) and any mechs pending control. Use set_mech_control to assign/reconfigure mechs. Work modes are: Work, Recharge, SelfShutdown (dormant self-charge), Escort.

### Declared input schema

```json
{
  "type": "object",
  "properties": {}
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## set_mech_control

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/MechTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/MechTools.cs`) registration line 22 → `Collect = SetMechControl` (method line 205). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Manage a mechanitor's mechanoids — the mech/mechanitor gizmo actions. Requires Biotech. Actions (arg 'action'):
• control — order a mechanitor to take control of a colony mech (walks over and links it, like the right-click 'Control mech'). Needs 'mech' + 'mechanitor'; rejects if out of bandwidth or the mech is already controlled/uncontrollable.
• disconnect — release a mech from its overseer ('mech').
• group — move a controlled mech into control group N ('mech' + 'group', 1-based).
• workmode — set a control group's work mode ('mechanitor' + 'group' + 'workMode' = Work/Recharge/SelfShutdown/Escort).
• recharge — set a control group's auto-recharge battery thresholds ('mechanitor' + 'group' + 'rechargeMin'/'rechargeMax', 0..1). Mechs recharge below min and stop at max.
Without 'action': lists the same overview as list_mechs so you can pick ids.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": [
        "control",
        "disconnect",
        "group",
        "workmode",
        "recharge"
      ],
      "description": "What to do"
    },
    "mech": {
      "type": "string",
      "description": "Mechanoid ThingID or name (for control/disconnect/group)"
    },
    "mechanitor": {
      "type": "string",
      "description": "Mechanitor colonist ThingID or name (for control/workmode/recharge)"
    },
    "group": {
      "type": "integer",
      "description": "Control group index (1-based) for group/workmode/recharge"
    },
    "workMode": {
      "type": "string",
      "enum": [
        "Work",
        "Recharge",
        "SelfShutdown",
        "Escort"
      ],
      "description": "Work mode (for action=workmode)"
    },
    "rechargeMin": {
      "type": "number",
      "description": "Recharge-below battery fraction 0..1 (for action=recharge)"
    },
    "rechargeMax": {
      "type": "number",
      "description": "Charge-up-to battery fraction 0..1 (for action=recharge)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## get_anomaly

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/AnomalyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/AnomalyTools.cs`) registration line 17 → `Collect = GetAnomaly` (method line 66). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Anomaly DLC overview: the void monolith (level, whether it can be advanced/activated and what is missing), the anomaly playstyle, entity codex discovery counts, and the anomaly research state per knowledge category (Basic/Advanced — each has its own active project slot, advanced by studying entities rather than at a research bench). Check this when a monolith/entity letter arrives, or before deciding what to study or contain.

### Declared input schema

```json
{
  "type": "object",
  "properties": {}
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## entity_codex

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/AnomalyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/AnomalyTools.cs`) registration line 22 → `Collect = EntityCodexTool` (method line 209). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

The entity codex (the bestiary of anomalous entities the colony has encountered). Without args: every codex category with discovered/total counts and the discovered entries. With entry='<defName|label>': that DISCOVERED entry's full detail — description, the concrete things it covers, and the research projects its discovery unlocked (with finished state). Undiscovered entries are not shown and cannot be queried (the player cannot see them either).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "entry": {
      "type": "string",
      "description": "EntityCodexEntryDef defName or label of a discovered entry for full detail"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## list_study_targets

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/AnomalyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/AnomalyTools.cs`) registration line 28 → `Collect = ListStudyTargets` (method line 309). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Everything that can currently be studied for anomaly knowledge (or quest study progress): captured entities on holding platforms (with containment strength and escape risk), studiable prisoners (e.g. ghouls), and studiable things (shards, obelisks, the monolith…). Each row shows the knowledge category and amount a study session yields, whether study is enabled/ready (with the reason and cooldown when not), and study-notes progress. With id='<ThingID>': that target's detail including its full Study-notes tab content (every unlocked note's title and text). Studying advances the active anomaly research project of the matching knowledge category (set_research); toggle studying with set_study.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "ThingID of one study target for full detail incl. study notes"
    },
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default: all maps)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## set_study

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/AnomalyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/AnomalyTools.cs`) registration line 38 → `Collect = SetStudy` (method line 583). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Enable or disable studying of one study target (the Study toggle on the entity / the checkbox in its Study-notes tab). 'id' is the target's ThingID from list_study_targets (a holding platform's ThingID also works — it resolves to the held entity). Colonists with the Dark study work type will only study targets that are enabled and off cooldown.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Study target ThingID (from list_study_targets)"
    },
    "enabled": {
      "type": "boolean",
      "description": "true = studying on, false = studying off"
    }
  },
  "required": [
    "id",
    "enabled"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## get_royalty

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RoyaltyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RoyaltyTools.cs`) registration line 44 → `Collect = GetRoyalty` (method line 311). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Royalty DLC overview: which colonists hold royal titles, their favor (honor) toward each title-granting faction, permit points and held permits. With pawn='<id|name>': that colonist's full royal status — title per faction, favor and next-title cost, permit points, held permits with cooldowns, UNMET throneroom/bedroom requirements (the exact strings vanilla's alerts show), required apparel (and whether it is currently satisfied), food requirement, work types the title forbids, granted abilities (e.g. Speech), heir, and the assigned throne. Use list_titles for what each rank requires/grants, manage_permits to spend permit points, use_permit to call in aid.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "pawn": {
      "type": "string",
      "description": "Colonist ThingID or name for full royal detail (omit for the colony overview)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **3**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 3 × `object` with keys: `_paused`, `colonists`, `count`, `hint`, `loaded`, `titleFactions`. Example: `campaigns/continuance/reference/legacy/history.jsonl:583`.

Observed selector combinations: `{}` (3).

All **22** nested observed paths, type counts and provenance are in `inventory.json` → `tools.get_royalty.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## list_titles

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RoyaltyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RoyaltyTools.cs`) registration line 50 → `Collect = ListTitles` (method line 792). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

The royal title track of a title-granting faction (default: the only such faction, normally the Empire), lowest to highest seniority: each title's favor cost (and cumulative total from nothing), permit points awarded, permits granted by the title itself (e.g. trade rights), and its CONDITIONS — required apparel and minimum quality, bedroom and throneroom requirements, food requirement, and work types it disables — plus rewards, abilities, inheritance, and who currently holds it. With title='<defName|label>': one title's full detail (description, per-gender apparel lists, satisfying meals…). Titles are advanced by earning favor (quests, bestowing ceremonies); favor is spent automatically when a title is claimed.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "faction": {
      "type": "string",
      "description": "Faction name or defName (only needed when several factions grant titles)"
    },
    "title": {
      "type": "string",
      "description": "RoyalTitleDef defName or label for one title's full detail"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## manage_permits

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RoyaltyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RoyaltyTools.cs`) registration line 60 → `Background = ManagePermits` (method line 1066). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

The royal permits screen (opens the real Permits tab on the pawn's info card so the player can watch). Without 'action': lists the pawn's permit points, favor, held permits and the whole acquirable permit tree — each entry says its point cost, required title, prerequisite permit and whether it can be taken RIGHT NOW (the informed-choice gate; no defaults are chosen for you). action='add' + permit='<defName>': spends a permit point to take that permit (vanilla's Accept button, shown on screen). action='returnAll': returns ALL of the pawn's permits from the faction to re-spend the points — this COSTS FAVOR and is confirmed on a re-call with confirm=true only. Permits obtained here are used with use_permit.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "pawn": {
      "type": "string",
      "description": "Colonist ThingID or name (omit to list which colonists have permit points)"
    },
    "faction": {
      "type": "string",
      "description": "Faction name or defName (only needed when several factions grant titles)"
    },
    "action": {
      "type": "string",
      "enum": [
        "add",
        "returnAll"
      ],
      "description": "What to do: 'add' takes a permit, 'returnAll' refunds all permits for favor. Omit to view."
    },
    "permit": {
      "type": "string",
      "description": "With action='add': the RoyalTitlePermitDef defName or label to take"
    },
    "confirm": {
      "type": "boolean",
      "description": "With action='returnAll': set true on the re-call to actually pay the favor and return the permits"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## use_permit

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/RoyaltyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/RoyaltyTools.cs`) registration line 73 → `Background = UsePermit` (method line 1395). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Use (consume) a royal permit a pawn holds — call military aid, a transport shuttle, a resource drop, a laborer team, or an orbital strike onto a map cell. Drives the REAL vanilla flow visibly: the pawn's royal-aid option opens vanilla's targeter on screen, the camera moves to the target, then the target is confirmed; vanilla's own validation (range from the pawn, fog/roof/landing footprint, weather range cap) decides. Without 'permit': lists every permit the pawn can use right now, with its cooldown state and cost (a use is FREE off cooldown; ON cooldown it costs the listed favor instead — that is vanilla's early-reuse rule). With permit but no x/z: that permit's targeting info so you can pick a cell. With x + z: executes. Colonists in a CARAVAN use their world-map permits (shuttle/resource drop) via the caravan's gizmos instead (world_object_action); trade permits are passive and are not 'used'.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "pawn": {
      "type": "string",
      "description": "Colonist ThingID or name holding the permit"
    },
    "permit": {
      "type": "string",
      "description": "RoyalTitlePermitDef defName or label (omit to list the pawn's usable permits)"
    },
    "faction": {
      "type": "string",
      "description": "Faction name or defName the permit is from (only needed when ambiguous)"
    },
    "x": {
      "type": "integer",
      "description": "Target cell X on the pawn's map"
    },
    "z": {
      "type": "integer",
      "description": "Target cell Z on the pawn's map"
    }
  },
  "required": [
    "pawn"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## list_policies

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/PolicyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/PolicyTools.cs`) registration line 17 → `Collect = ListPolicies` (method line 152). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

List assignable policies for the colony: apparel policies (outfits), food policies, allowed areas (current map), and schedule time-assignments. Use these names with the set_* tools.

### Declared input schema

```json
{
  "type": "object",
  "properties": {}
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **1**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `_paused`, `areas`, `drugPolicies`, `foodPolicies`, `ok`, `outfits`, `timeAssignments`. Example: `campaigns/continuance/reference/legacy/history.jsonl:212`.

Observed selector combinations: `{}` (1).

All **22** nested observed paths, type counts and provenance are in `inventory.json` → `tools.list_policies.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## set_schedule

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/PolicyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/PolicyTools.cs`) registration line 22 → `Collect = SetSchedule` (method line 248). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Read or set a colonist's schedule (timetable). With NO 'assignment': READ mode — returns the current 24-hour assignment grid (hour 0-23 -> TimeAssignmentDef, e.g. Work/Sleep/Joy/Anything/Meditate) for the colonist named by 'id'/'name', or for EVERY colonist if neither is given. To EDIT: 'assignment' is a TimeAssignmentDef defName (Anything, Work, Sleep, Joy, Meditate). Apply to a single 'hour' (0-23), an 'hourStart'..'hourEnd' range, or the whole day if no hours given. Colonist by 'id' or 'name'.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Colonist ThingID"
    },
    "name": {
      "type": "string",
      "description": "Colonist name (case-insensitive)"
    },
    "assignment": {
      "type": "string",
      "description": "TimeAssignmentDef defName (Anything/Work/Sleep/Joy/Meditate). Omit to read the current schedule instead of editing."
    },
    "hour": {
      "type": "integer",
      "description": "Single hour 0-23"
    },
    "hourStart": {
      "type": "integer",
      "description": "Range start hour 0-23 (with hourEnd)"
    },
    "hourEnd": {
      "type": "integer",
      "description": "Range end hour 0-23 inclusive (with hourStart)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **17**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 17 × `object` with keys: `_paused`, `assignment`, `hoursSet`, `ok`, `pawn`, `schedule`. Example: `campaigns/continuance/reference/legacy/history.jsonl:147`.

Observed selector combinations: `{}` (17).

All **8** nested observed paths, type counts and provenance are in `inventory.json` → `tools.set_schedule.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## set_outfit

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/PolicyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/PolicyTools.cs`) registration line 36 → `Collect = SetOutfit` (method line 343). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Set a colonist's apparel policy (outfit) by 'policy' (label or id). Colonist by 'id' or 'name'.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Colonist ThingID"
    },
    "name": {
      "type": "string",
      "description": "Colonist name (case-insensitive)"
    },
    "policy": {
      "type": "string",
      "description": "Apparel policy label or numeric id"
    }
  },
  "required": [
    "policy"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## set_drug_policy

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/PolicyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/PolicyTools.cs`) registration line 47 → `Collect = SetDrugPolicy` (method line 399). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Set a colonist's drug policy (Assign tab) by 'policy' (label or id). Colonist by 'id' or 'name'.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Colonist ThingID"
    },
    "name": {
      "type": "string",
      "description": "Colonist name (case-insensitive)"
    },
    "policy": {
      "type": "string",
      "description": "Drug policy label or numeric id"
    }
  },
  "required": [
    "policy"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **4**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 4 × `object` with keys: `_paused`, `drugPolicy`, `ok`, `pawn`. Example: `campaigns/continuance/reference/legacy/history.jsonl:213`.

Observed selector combinations: `{}` (4).

All **5** nested observed paths, type counts and provenance are in `inventory.json` → `tools.set_drug_policy.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## manage_apparel_policy

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/PolicyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/PolicyTools.cs`) registration line 58 → `Collect = ManageApparelPolicy` (method line 427). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Manage an apparel policy (the 'Manage apparel' dialog behind the Assign tab). Without an op, returns the policy's allowed-apparel filter summary. Ops: 'create' (with 'name') makes a new policy; 'rename' (+ 'name'); 'delete'. Edit the allowed apparel with 'allow'/'disallow' (comma-separated apparel ThingDef defNames or ThingCategory names), 'allowAll'/'disallowAll', and hp/quality ranges. Identify the policy by 'policy' (label or id); not needed for 'create'.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "policy": {
      "type": "string",
      "description": "Apparel policy label or numeric id (omit for create)"
    },
    "create": {
      "type": "boolean",
      "description": "Create a new policy (use 'name' for its label)"
    },
    "rename": {
      "type": "boolean",
      "description": "Rename the policy to 'name'"
    },
    "delete": {
      "type": "boolean",
      "description": "Delete the policy"
    },
    "name": {
      "type": "string",
      "description": "New policy label (for create/rename)"
    },
    "allow": {
      "type": "string",
      "description": "Comma-separated apparel ThingDef defNames or ThingCategory names to allow"
    },
    "disallow": {
      "type": "string",
      "description": "Comma-separated apparel ThingDef defNames or ThingCategory names to disallow"
    },
    "allowAll": {
      "type": "boolean",
      "description": "Allow all apparel (applied before allow/disallow)"
    },
    "disallowAll": {
      "type": "boolean",
      "description": "Disallow all apparel (applied before allow/disallow)"
    },
    "hpMin": {
      "type": "integer",
      "description": "Minimum hit-point percent 0-100"
    },
    "hpMax": {
      "type": "integer",
      "description": "Maximum hit-point percent 0-100"
    },
    "qualityMin": {
      "type": "string",
      "description": "Minimum quality (Awful..Legendary)"
    },
    "qualityMax": {
      "type": "string",
      "description": "Maximum quality (Awful..Legendary)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## manage_food_policy

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/PolicyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/PolicyTools.cs`) registration line 79 → `Collect = ManageFoodPolicy` (method line 586). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Edit the CONTENTS of a food policy (the 'Manage food restrictions' dialog behind the Assign tab) — which foods colonists on this policy are allowed to eat. Without an op, returns the policy's allowed-food filter summary. Ops: 'create' (with 'name') makes a new policy; 'rename' (+ 'name'); 'delete'. Edit the allowed food with 'allow'/'disallow' (comma-separated food ThingDef defNames, ThingCategory names, or special-filter names like AllowRotten/AllowFresh from the summary's specialFilters), and 'allowAll'/'disallowAll'. Identify the policy by 'policy' (label or id); not needed for 'create'.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "policy": {
      "type": "string",
      "description": "Food policy label or numeric id (omit for create)"
    },
    "create": {
      "type": "boolean",
      "description": "Create a new policy (use 'name' for its label)"
    },
    "rename": {
      "type": "boolean",
      "description": "Rename the policy to 'name'"
    },
    "delete": {
      "type": "boolean",
      "description": "Delete the policy"
    },
    "name": {
      "type": "string",
      "description": "New policy label (for create/rename)"
    },
    "allow": {
      "type": "string",
      "description": "Comma-separated food ThingDef defNames, ThingCategory names, or special-filter names to allow"
    },
    "disallow": {
      "type": "string",
      "description": "Comma-separated food ThingDef defNames, ThingCategory names, or special-filter names to disallow"
    },
    "allowAll": {
      "type": "boolean",
      "description": "Allow all foods (applied before allow/disallow)"
    },
    "disallowAll": {
      "type": "boolean",
      "description": "Disallow all foods (applied before allow/disallow)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## manage_drug_policy

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/PolicyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/PolicyTools.cs`) registration line 96 → `Collect = ManageDrugPolicy` (method line 697). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Edit the CONTENTS of a drug policy (the 'Manage drug policies' dialog behind the Assign tab) — the per-drug schedule columns. Without an op, returns every drug row (allowedForJoy, allowScheduled, daysFrequency, onlyIfMoodBelow%, onlyIfJoyBelow%, takeToInventory, allowedForAddiction). Ops: 'create' (with 'name') makes a new policy; 'rename' (+ 'name'); 'delete'. To edit a drug row, pass 'drug' (a drug ThingDef defName or label) with any of the fields to change; omitted fields are left as-is. Identify the policy by 'policy' (label or id); not needed for 'create'.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "policy": {
      "type": "string",
      "description": "Drug policy label or numeric id (omit for create)"
    },
    "create": {
      "type": "boolean",
      "description": "Create a new policy (use 'name' for its label)"
    },
    "rename": {
      "type": "boolean",
      "description": "Rename the policy to 'name'"
    },
    "delete": {
      "type": "boolean",
      "description": "Delete the policy"
    },
    "name": {
      "type": "string",
      "description": "New policy label (for create/rename)"
    },
    "drug": {
      "type": "string",
      "description": "Drug ThingDef defName or label to edit a single scheduled-consumption row"
    },
    "allowScheduled": {
      "type": "boolean",
      "description": "Take this drug on a schedule (the 'scheduled' checkbox)"
    },
    "daysFrequency": {
      "type": "number",
      "description": "Scheduled dose frequency in doses per day (e.g. 1 = once/day, 0.5 = every 2 days)"
    },
    "onlyIfMoodBelow": {
      "type": "number",
      "description": "Only take when mood is below this percent 0-100 (100 = no mood restriction)"
    },
    "onlyIfJoyBelow": {
      "type": "number",
      "description": "Only take when recreation is below this percent 0-100 (100 = no recreation restriction)"
    },
    "takeToInventory": {
      "type": "integer",
      "description": "Number of doses colonists carry for emergencies (0 = none)"
    },
    "allowedForJoy": {
      "type": "boolean",
      "description": "Allow taking this drug for recreation/joy"
    },
    "allowedForAddiction": {
      "type": "boolean",
      "description": "Allow taking this drug to satisfy an existing addiction"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## set_food_policy

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/PolicyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/PolicyTools.cs`) registration line 117 → `Collect = SetFoodPolicy` (method line 371). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Set a colonist's food policy by 'policy' (label or id). Colonist by 'id' or 'name'.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Colonist ThingID"
    },
    "name": {
      "type": "string",
      "description": "Colonist name (case-insensitive)"
    },
    "policy": {
      "type": "string",
      "description": "Food policy label or numeric id"
    }
  },
  "required": [
    "policy"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## set_hostility_response

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/PolicyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/PolicyTools.cs`) registration line 128 → `Collect = SetHostilityResponse` (method line 866). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Read or set a colonist's hostility response (the Attack/Flee/Ignore icon on a selected pawn and in the Assign tab): what they do when an enemy comes close while they are NOT drafted. Without 'response': READ mode — the current mode for the colonist ('id'/'name'), or for every colonist if neither is given. 'response' = Attack, Flee or Ignore to change it (pawns incapable of violence cannot be set to Attack).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Colonist ThingID"
    },
    "name": {
      "type": "string",
      "description": "Colonist name (case-insensitive)"
    },
    "response": {
      "type": "string",
      "enum": [
        "Attack",
        "Flee",
        "Ignore"
      ],
      "description": "Hostility response mode (omit to read)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## set_allowed_area

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/PolicyTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/PolicyTools.cs`) registration line 139 → `Collect = SetAllowedArea` (method line 927). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Set a colonist's allowed area by 'area' (label), or 'unrestricted'/'none' to clear it. Colonist by 'id' or 'name'.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Colonist ThingID"
    },
    "name": {
      "type": "string",
      "description": "Colonist name (case-insensitive)"
    },
    "area": {
      "type": "string",
      "description": "Area label, or 'unrestricted'/'none' to clear"
    }
  },
  "required": [
    "area"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **34**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 34 × `object` with keys: `_paused`, `area`, `ok`, `pawn`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1443`.

Observed selector combinations: `{}` (34).

All **5** nested observed paths, type counts and provenance are in `inventory.json` → `tools.set_allowed_area.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## manage_area

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/AreaTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/AreaTools.cs`) registration line 33 → `Background = ManageArea` (method line 55). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Create and edit map Areas — the per-cell overlays behind allowed-area restriction. (To ASSIGN an existing area to a colonist use set_allowed_area; to VIEW an area's cells use get_area layer='areas'.) 'op': 'list' = all areas on the current map (label, kind, cells, mutable); 'create' = new allowed area (max 10) with optional 'label'; if cell/rect args are given it is also painted; 'paint' = add cells to area, 'erase' = remove cells (target one cell 'x'+'z' or a rectangle 'minX/minZ/maxX/maxZ', 'fill'='filled'|'edges'); 'clear' = empty the area, 'invert' = flip every cell; 'rename' = set 'newLabel' (allowed areas only); 'delete' = remove the area (allowed areas only; LOSSY — unassigns everyone; review first, then re-call with confirm=true). Edit ops target an existing area by 'area' (label). Painting is shown on screen band-by-band with the camera on the region.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "op": {
      "type": "string",
      "enum": [
        "list",
        "create",
        "paint",
        "erase",
        "clear",
        "invert",
        "rename",
        "delete"
      ],
      "description": "Operation"
    },
    "area": {
      "type": "string",
      "description": "Target area label (for paint/erase/clear/invert/rename/delete; case-insensitive, matches built-in areas too)"
    },
    "label": {
      "type": "string",
      "description": "New area's label (op='create'; optional — auto-named if omitted)"
    },
    "newLabel": {
      "type": "string",
      "description": "New label (op='rename')"
    },
    "x": {
      "type": "integer",
      "description": "Cell X (single-cell paint/erase)"
    },
    "z": {
      "type": "integer",
      "description": "Cell Z (single-cell paint/erase)"
    },
    "minX": {
      "type": "integer",
      "description": "Rectangle min X (paint/erase)"
    },
    "minZ": {
      "type": "integer",
      "description": "Rectangle min Z (paint/erase)"
    },
    "maxX": {
      "type": "integer",
      "description": "Rectangle max X (paint/erase)"
    },
    "maxZ": {
      "type": "integer",
      "description": "Rectangle max Z (paint/erase)"
    },
    "fill": {
      "type": "string",
      "description": "'filled' (default, every cell) or 'edges' (perimeter only) for a rectangle"
    },
    "confirm": {
      "type": "boolean",
      "description": "Set true to actually delete (op='delete') after reviewing the impact"
    }
  },
  "required": [
    "op"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **13**. Explicit error-marker records: **1**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `_paused`, `error`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:250`.
- 11 × `object` with keys: `_paused`, `area`, `areaCellsAfter`, `cellsAffected`, `ok`, `op`, `rejected`. Example: `campaigns/continuance/reference/legacy/history.jsonl:251`.
- 1 × `object` with keys: `_paused`, `area`, `cells`, `hint`, `ok`, `op`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1440`.

Observed selector combinations: `{}` (13).

All **11** nested observed paths, type counts and provenance are in `inventory.json` → `tools.manage_area.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## list_zones

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ZoneTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ZoneTools.cs`) registration line 14 → `Collect = ListZones` (method line 219). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

List all zones (stockpile and growing) with their id, kind, label, cell count, position, and settings (growing: plant + allowSow; stockpile: priority, stored count, and how full it is — occupiedCells / fullPercent). Growing zones with a blight outbreak report blightedPlants + a blightNotice explaining how to order cutting them. Use the id with the other zone tools.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "mapIndex": {
      "type": "integer",
      "description": "Map index (default: all maps)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **9**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 9 × `object` with keys: `_paused`, `ok`, `zones`. Example: `campaigns/continuance/reference/legacy/history.jsonl:101`.

Observed selector combinations: `{}` (9).

All **19** nested observed paths, type counts and provenance are in `inventory.json` → `tools.list_zones.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## select_zone

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ZoneTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ZoneTools.cs`) registration line 20 → `Collect = SelectZone` (method line 250). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Select a zone by 'id' in the live game UI (so its settings panel is shown to the human). This is how you 'select a zone', since zones are not clickable things.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "description": "Zone id (from list_zones)"
    }
  },
  "required": [
    "id"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## rename_zone

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ZoneTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ZoneTools.cs`) registration line 26 → `Collect = RenameZone` (method line 282). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Rename a zone by 'id' to 'name'.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "description": "Zone id"
    },
    "name": {
      "type": "string",
      "description": "New label"
    }
  },
  "required": [
    "id",
    "name"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **5**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 5 × `object` with keys: `_paused`, `allowSow`, `cells`, `id`, `kind`, `label`, `mapIndex`, `plant`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:278`.

Observed selector combinations: `{}` (5).

All **11** nested observed paths, type counts and provenance are in `inventory.json` → `tools.rename_zone.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## delete_zone

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ZoneTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ZoneTools.cs`) registration line 36 → `Collect = DeleteZone` (method line 307). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Delete a zone by 'id' (removes the whole zone).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "description": "Zone id"
    }
  },
  "required": [
    "id"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## set_growing_zone

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ZoneTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ZoneTools.cs`) registration line 42 → `Collect = SetGrowingZone` (method line 340). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Configure a growing zone by 'id': set the plant to grow ('plant' = plant ThingDef defName, e.g. Plant_Rice, Plant_Potato, Plant_Cotton) and/or toggle sowing ('allowSow').

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "description": "Zone id (must be a growing zone)"
    },
    "plant": {
      "type": "string",
      "description": "Plant ThingDef defName to grow"
    },
    "allowSow": {
      "type": "boolean",
      "description": "Whether colonists sow here"
    }
  },
  "required": [
    "id"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **9**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 9 × `object` with keys: `_paused`, `allowSow`, `cells`, `id`, `kind`, `label`, `mapIndex`, `plant`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:109`.

Observed selector combinations: `{}` (9).

All **11** nested observed paths, type counts and provenance are in `inventory.json` → `tools.set_growing_zone.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## set_stockpile_priority

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ZoneTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ZoneTools.cs`) registration line 53 → `Collect = SetStockpilePriority` (method line 380). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Set a stockpile zone's storage 'priority' by 'id' (Unstored/Low/Normal/Preferred/Important/Critical).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "description": "Zone id (must be a stockpile)"
    },
    "priority": {
      "type": "string",
      "enum": [
        "Low",
        "Normal",
        "Preferred",
        "Important",
        "Critical"
      ],
      "description": "Storage priority"
    }
  },
  "required": [
    "id",
    "priority"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **1**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `_paused`, `allowedDefCount`, `cells`, `fullPercent`, `id`, `kind`, `label`, `mapIndex`, `occupiedCells`, `priority`, `storedThings`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1238`.

Observed selector combinations: `{}` (1).

All **14** nested observed paths, type counts and provenance are in `inventory.json` → `tools.set_stockpile_priority.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## set_stockpile_filter

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ZoneTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ZoneTools.cs`) registration line 63 → `Collect = SetStockpileFilter` (method line 411). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Read or edit which items a stockpile zone accepts (its storage filter) by 'id'. With ONLY 'id': returns the CURRENT settings — allowed defs, hp/quality ranges, and every special filter (allow fresh, allow rotten, allow smeltable, biocodable/bladelink weapons, corpses, …) with its state and toggle token. To edit: 'allow' / 'disallow' are comma-separated ThingDef defNames (e.g. Silver,Steel), ThingCategoryDef names (e.g. Foods, Weapons, Medicine) or SpecialThingFilterDef defNames (e.g. AllowFresh, AllowRotten). 'allowAll' accepts everything storable; 'disallowAll' clears the filter. Quality/hp ranges via hpMin/hpMax (0-100) and qualityMin/qualityMax (Awful/Poor/Normal/Good/Excellent/Masterwork/Legendary).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "description": "Zone id (must be a stockpile)"
    },
    "allow": {
      "type": "string",
      "description": "Comma-separated ThingDef / ThingCategory / SpecialThingFilter names to allow"
    },
    "disallow": {
      "type": "string",
      "description": "Comma-separated ThingDef / ThingCategory / SpecialThingFilter names to disallow"
    },
    "allowAll": {
      "type": "boolean",
      "description": "Allow everything storable (applied before allow/disallow)"
    },
    "disallowAll": {
      "type": "boolean",
      "description": "Disallow everything (applied before allow/disallow)"
    },
    "hpMin": {
      "type": "integer",
      "description": "Minimum hit-point percent 0-100"
    },
    "hpMax": {
      "type": "integer",
      "description": "Maximum hit-point percent 0-100"
    },
    "qualityMin": {
      "type": "string",
      "description": "Minimum quality (Awful..Legendary)"
    },
    "qualityMax": {
      "type": "string",
      "description": "Maximum quality (Awful..Legendary)"
    }
  },
  "required": [
    "id"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **5**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 5 × `object` with keys: `_paused`, `allowedDefCount`, `applied`, `cells`, `filter`, `fullPercent`, `id`, `kind`, `label`, `mapIndex`, `occupiedCells`, `priority`, `storedThings`, `x`, `z`. Example: `campaigns/continuance/reference/legacy/history.jsonl:110`.

Observed selector combinations: `{}` (5).

All **26** nested observed paths, type counts and provenance are in `inventory.json` → `tools.set_stockpile_filter.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## get_quest

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/QuestTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/QuestTools.cs`) registration line 15 → `Collect = GetQuest` (method line 71). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Read quests. With 'id': full detail (name, description, state, reward points, expiry, accepter, and relatedLetterIds — the letter ids that announced it). Without 'id': lists all quests with id/name/state (NotYetAccepted offers, Ongoing, and ended). NOTE: a quest id is NOT a letter id — they are separate id spaces. A letter about a quest carries the questId to use here; use read_letter for the letter's own id.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "description": "Quest id (from the quest list, get_world, or a letter's questId — NOT a letter id)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **19**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 5 × `object` with keys: `_paused`, `ok`, `quests`. Example: `campaigns/continuance/reference/legacy/history.jsonl:208`.
- 6 × `object` with keys: `_paused`, `description`, `everAccepted`, `id`, `name`, `ok`, `points`, `relatedLetterIds`, `requiresAccepter`, `state`. Example: `campaigns/continuance/reference/legacy/history.jsonl:356`.
- 5 × `object` with keys: `_paused`, `challengeRating`, `description`, `everAccepted`, `id`, `name`, `ok`, `points`, `relatedLetterIds`, `requiresAccepter`, `state`, `ticksUntilExpiry`. Example: `campaigns/continuance/reference/legacy/history.jsonl:527`.
- 2 × `object` with keys: `_paused`, `challengeRating`, `description`, `everAccepted`, `id`, `name`, `ok`, `points`, `relatedLetterIds`, `requiresAccepter`, `state`, `tags`. Example: `campaigns/continuance/reference/legacy/history.jsonl:972`.
- 1 × `object` with keys: `_paused`, `challengeRating`, `description`, `everAccepted`, `id`, `name`, `ok`, `points`, `relatedLetterIds`, `requiresAccepter`, `state`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1958`.

Observed selector combinations: `{}` (19).

All **22** nested observed paths, type counts and provenance are in `inventory.json` → `tools.get_quest.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## quest_action

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/QuestTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/QuestTools.cs`) registration line 21 → `Collect = QuestAction` (method line 172). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Act on a quest by 'id': 'accept' an offered quest (optionally 'by' = colonist id/name for the accepter), 'dismiss' an offer you don't want, or 'abandon' an ongoing quest (fails it).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "description": "Quest id"
    },
    "action": {
      "type": "string",
      "enum": [
        "accept",
        "dismiss",
        "abandon"
      ],
      "description": "What to do"
    },
    "by": {
      "type": "string",
      "description": "Colonist id or name to accept the quest (optional; defaults to a free colonist)"
    }
  },
  "required": [
    "id",
    "action"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **4**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `_notifications`, `_paused`, `accepter`, `id`, `ok`, `state`. Example: `campaigns/continuance/reference/legacy/history.jsonl:545`.
- 3 × `object` with keys: `_paused`, `accepter`, `id`, `ok`, `state`. Example: `campaigns/continuance/reference/legacy/history.jsonl:584`.

Observed selector combinations: `{"action": "accept"}` (4).

All **14** nested observed paths, type counts and provenance are in `inventory.json` → `tools.quest_action.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## list_recipes

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/BillTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/BillTools.cs`) registration line 15 → `Collect = ListRecipes` (method line 161). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

List the recipes a work table can make right now (for add_bill). 'id' = the work table ThingID.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Work table ThingID"
    }
  },
  "required": [
    "id"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **9**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 9 × `object` with keys: `_paused`, `ok`, `recipes`, `thing`. Example: `campaigns/continuance/reference/legacy/history.jsonl:229`.

Observed selector combinations: `{}` (9).

All **8** nested observed paths, type counts and provenance are in `inventory.json` → `tools.list_recipes.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## list_bills

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/BillTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/BillTools.cs`) registration line 21 → `Collect = ListBills` (method line 189). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

List the production bills on a work table ('id' = ThingID): index, recipe, repeat mode/count, suspended state.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Work table ThingID"
    }
  },
  "required": [
    "id"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **2**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 2 × `object` with keys: `_paused`, `bills`, `ok`, `thing`. Example: `campaigns/continuance/reference/legacy/history.jsonl:631`.

Observed selector combinations: `{}` (2).

All **16** nested observed paths, type counts and provenance are in `inventory.json` → `tools.list_bills.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## add_bill

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/BillTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/BillTools.cs`) registration line 27 → `Collect = AddBill` (method line 217). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Add a production bill to a work table. 'id' = ThingID, 'recipe' = RecipeDef defName/label (from list_recipes). Optional 'repeatMode' (forever/repeatCount/targetCount), 'count' (repeat count for repeatCount, default 1), 'targetCount' (for targetCount mode).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Work table ThingID"
    },
    "recipe": {
      "type": "string",
      "description": "RecipeDef defName or label"
    },
    "repeatMode": {
      "type": "string",
      "enum": [
        "forever",
        "repeatCount",
        "targetCount"
      ],
      "description": "Repeat mode"
    },
    "count": {
      "type": "integer",
      "description": "Repeat count (repeatCount mode)"
    },
    "targetCount": {
      "type": "integer",
      "description": "Target stock count (targetCount mode)"
    }
  },
  "required": [
    "id",
    "recipe"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **14**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 13 × `object` with keys: `_paused`, `added`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:192`.
- 1 × `object` with keys: `_paused`, `_threatWarning`, `added`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1613`.

Observed selector combinations: `{}` (14).

All **31** nested observed paths, type counts and provenance are in `inventory.json` → `tools.add_bill.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## set_bill

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/BillTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/BillTools.cs`) registration line 40 → `Collect = SetBill` (method line 253). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Read or edit a bill on a work table by 'index' (from list_bills). With ONLY id+index: returns the bill's full detail including its INGREDIENT FILTER — allowed defs, hp/quality ranges, and every special filter (allow fresh/rotten, allow smeltable, biocodable/bladelink (persona) weapons, corpse kinds, …) with its state and toggle token. Edits: 'repeatMode', 'count', 'targetCount', 'suspended'; ingredient filter via 'allow'/'disallow' (comma-separated ThingDef / ThingCategory / SpecialThingFilter names, e.g. allow=AllowRotten), 'allowAll' (reset to the recipe's full ingredient set), 'disallowAll', hpMin/hpMax (0-100), qualityMin/qualityMax; and 'ingredientSearchRadius' (cells; 999 = unlimited).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Work table ThingID"
    },
    "index": {
      "type": "integer",
      "description": "Bill index (from list_bills)"
    },
    "repeatMode": {
      "type": "string",
      "enum": [
        "forever",
        "repeatCount",
        "targetCount"
      ],
      "description": "Repeat mode"
    },
    "count": {
      "type": "integer",
      "description": "Repeat count (repeatCount mode)"
    },
    "targetCount": {
      "type": "integer",
      "description": "Target stock count (targetCount mode)"
    },
    "suspended": {
      "type": "boolean",
      "description": "Suspend/unsuspend the bill"
    },
    "allow": {
      "type": "string",
      "description": "Ingredient filter: comma-separated ThingDef / ThingCategory / SpecialThingFilter names to allow"
    },
    "disallow": {
      "type": "string",
      "description": "Ingredient filter: names to disallow"
    },
    "allowAll": {
      "type": "boolean",
      "description": "Reset the ingredient filter to everything the recipe accepts"
    },
    "disallowAll": {
      "type": "boolean",
      "description": "Clear the ingredient filter"
    },
    "hpMin": {
      "type": "integer",
      "description": "Ingredient minimum hit-point percent 0-100"
    },
    "hpMax": {
      "type": "integer",
      "description": "Ingredient maximum hit-point percent 0-100"
    },
    "qualityMin": {
      "type": "string",
      "description": "Ingredient minimum quality (Awful..Legendary)"
    },
    "qualityMax": {
      "type": "string",
      "description": "Ingredient maximum quality (Awful..Legendary)"
    },
    "ingredientSearchRadius": {
      "type": "integer",
      "description": "Max distance colonists fetch ingredients from (999 = unlimited)"
    }
  },
  "required": [
    "id",
    "index"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **8**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 5 × `object` with keys: `_paused`, `bill`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:262`.
- 3 × `object` with keys: `_paused`, `applied`, `bill`, `ingredientFilter`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:925`.

Observed selector combinations: `{}` (8).

All **26** nested observed paths, type counts and provenance are in `inventory.json` → `tools.set_bill.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## delete_bill

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/BillTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/BillTools.cs`) registration line 63 → `Collect = DeleteBill` (method line 392). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Delete a bill on a work table by 'index' (from list_bills).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Work table ThingID"
    },
    "index": {
      "type": "integer",
      "description": "Bill index"
    }
  },
  "required": [
    "id",
    "index"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## list_windows

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/WindowTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/WindowTools.cs`) registration line 47 → `Collect = ListWindows` (method line 459). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

List open pop-up windows/dialogs and their content: choice dialogs (title/text/options), message boxes (title/text/buttons), float menus / dropdowns (the option list a dropdown gizmo or right-click order opens — title/options), open main tabs (Assign/Work/… — kind 'mainTab', readable with get_window_ui), and other windows by type. Use window_action to respond. Results carry _dialogOpen when a pausing popup is waiting.

### Declared input schema

```json
{
  "type": "object",
  "properties": {}
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **12**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 8 × `object` with keys: `ok`, `windows`. Example: `campaigns/continuance/reference/legacy/history.jsonl:28`.
- 3 × `object` with keys: `_dialogOpen`, `_paused`, `ok`, `windows`. Example: `campaigns/continuance/reference/legacy/history.jsonl:77`.
- 1 × `object` with keys: `_paused`, `ok`, `windows`. Example: `campaigns/continuance/reference/legacy/history.jsonl:220`.

Observed selector combinations: `{}` (12).

All **17** nested observed paths, type counts and provenance are in `inventory.json` → `tools.list_windows.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## get_window_ui

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/WindowTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/WindowTools.cs`) registration line 53 → `Collect = GetWindowUi` (method line 127). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Get the actual on-screen contents of a modal pop-up window or an open main tab (Assign/Work/Schedule/… — kind 'mainTab' in list_windows): buttons (incl. image buttons), labels/text, text fields, tabs, checkboxes, and radio buttons drawn this frame, with positions. Per-row controls (a plain checkbox, '<'/'>' arrows, or an amount box on an item/pawn row) carry a 'row' field = that row's own label (the item/pawn NAME, e.g. 'Steel'/'Anshe'), so ambiguous controls and which amount box belongs to which row become addressable. Buttons whose label starts 'DEV:' are flagged 'dev' (developer shortcuts with surprising effects). Works for arbitrary dialogs (naming, caravan/transporter/trade rows, custom events). Target with 'index' (from list_windows); defaults to the top-most pausing dialog. Use window_action to operate them.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "index": {
      "type": "integer",
      "description": "Window index from list_windows (default: top-most pausing dialog)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **34**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 5 × `object` with keys: `buttons`, `captured`, `checkboxes`, `hint`, `labels`, `ok`, `radios`, `tabs`, `textFields`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:29`.
- 23 × `object` with keys: `_dialogOpen`, `_paused`, `buttons`, `captured`, `checkboxes`, `hint`, `labels`, `ok`, `radios`, `tabs`, `textFields`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:322`.
- 6 × `object` with keys: `_paused`, `buttons`, `captured`, `checkboxes`, `hint`, `labels`, `ok`, `radios`, `tabs`, `textFields`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:393`.

Observed selector combinations: `{}` (34).

All **58** nested observed paths, type counts and provenance are in `inventory.json` → `tools.get_window_ui.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## window_action

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/WindowTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/WindowTools.cs`) registration line 59 → `Background = WindowAction` (method line 491). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Respond to a pop-up window (from list_windows/get_window_ui). Pick one: 'option' (index or label) for a choice dialog OR a float menu / dropdown; 'button' (A/B/C or label) for a message box; 'clickButton' (label, matches text buttons AND image-button tooltips/names) to press any on-screen button generically; 'tab' (label) to switch tabs; 'setChecked' (checkbox label) with optional 'checked' (default: toggle) to flip a checkbox; 'text' (+ 'field' index, default 0) to type into a text box; or 'close'. Add 'row' (an item/pawn row's leading label) to scope clickButton/setChecked to one row so ambiguous '<'/'>' arrows and plain checkboxes become addressable. Target with 'index' (default: top-most pausing dialog). clickButton/tab/setChecked/text take effect on the next game frame; this tool then VERIFIES the change actually landed and returns 'applied' (false with a 'warning' if the control was not really pressed/flipped — e.g. off-screen, disabled, or already at min/max). For an exact amount on a transferable row, prefer text=<n> field=<that row's textField index> (the '<'/'>' buttons only step by 1 or jump to min/max). Avoid buttons flagged 'dev' by get_window_ui.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "index": {
      "type": "integer",
      "description": "Window index from list_windows (default: top-most pausing dialog)"
    },
    "option": {
      "type": "string",
      "description": "Choice-dialog option: label (case-insensitive) or numeric index"
    },
    "button": {
      "type": "string",
      "description": "Message-box button: 'A'/'B'/'C' or the button label"
    },
    "clickButton": {
      "type": "string",
      "description": "Generic: press the on-screen button (text button, image-button tooltip/name, or radio) whose label contains this text"
    },
    "tab": {
      "type": "string",
      "description": "Select the tab whose label contains this text"
    },
    "setChecked": {
      "type": "string",
      "description": "Flip the checkbox whose label contains this text (use 'row' for an unlabeled per-row checkbox)"
    },
    "checked": {
      "type": "boolean",
      "description": "Desired checkbox state for setChecked (omit to toggle the current state)"
    },
    "row": {
      "type": "string",
      "description": "Scope clickButton/setChecked to the row whose leading label contains this text"
    },
    "text": {
      "type": "string",
      "description": "Type this into a text box (naming/rename/etc.)"
    },
    "field": {
      "type": "integer",
      "description": "Which text box to type into (0-based draw order; default 0)"
    },
    "accept": {
      "type": "boolean",
      "description": "After setting text via a known rename dialog, confirm it (default true)"
    },
    "close": {
      "type": "boolean",
      "description": "Just close the window"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **48**. Explicit error-marker records: **2**.

Root-key variants (counts are evidence records):

- 4 × `object` with keys: `applied`, `button`, `did`, `ok`, `row`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:30`.
- 2 × `object` with keys: `applied`, `did`, `ok`, `tab`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:34`.
- 2 × `object` with keys: `applied`, `button`, `did`, `ok`, `warning`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:36`.
- 1 × `object` with keys: `did`, `ok`, `option`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:80`.
- 15 × `object` with keys: `_paused`, `did`, `ok`, `option`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:285`.
- 2 × `object` with keys: `_dialogOpen`, `_paused`, `did`, `ok`, `text`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:323`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `did`, `field`, `note`, `ok`, `text`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:324`.
- 1 × `object` with keys: `_notifications`, `_paused`, `amountAfter`, `amountBefore`, `applied`, `button`, `did`, `ok`, `row`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:325`.
- 11 × `object` with keys: `_paused`, `applied`, `button`, `did`, `ok`, `row`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:345`.
- 4 × `object` with keys: `_notifications`, `_paused`, `applied`, `button`, `did`, `ok`, `row`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:495`.
- 2 × `object` with keys: `_paused`, `did`, `ok`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:881`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `applied`, `button`, `did`, `ok`, `row`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1420`.
- 2 × `object` with keys: `_paused`, `_threatWarning`, `did`, `ok`, `option`, `window`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1519`.

Observed selector combinations: `{}` (46), `{"tab": "Equipment"}` (1), `{"tab": "Characters"}` (1).

All **42** nested observed paths, type counts and provenance are in `inventory.json` → `tools.window_action.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## get_inspect_pane

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/InspectPaneTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/InspectPaneTools.cs`) registration line 15 → `Collect = GetInspectPane` (method line 27). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

The bottom-left inspect pane, as the human sees it: the selected thing (or pass 'id' to select one), its inspect text, its action buttons (gizmos — run them with do_thing_action) and its tabs, each tagged with the tool that reads/operates it (get_pawn tabs, list_bills, set_stockpile_filter, assign_building, get_room…). Pass 'tab' (e.g. 'bills', 'storage', 'assign', or a pawn tab like 'health') to also get that tab's structured contents inline.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Thing to select first (default: whatever is currently selected)"
    },
    "tab": {
      "type": "string",
      "description": "Tab whose contents to include: bills/storage/assign or health/needs/gear/bio/social/log/records/training"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## set_medical_care

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/HealthTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/HealthTools.cs`) registration line 16 → `Collect = SetMedicalCare` (method line 73). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Set a pawn's medical care (Health tab): 'care' = NoCare/NoMeds/HerbalOrWorse/NormalOrWorse/Best, and/or 'selfTend' (whether the pawn tends itself). Pawn by 'id' or 'name'.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Pawn ThingID"
    },
    "name": {
      "type": "string",
      "description": "Pawn name (case-insensitive)"
    },
    "care": {
      "type": "string",
      "enum": [
        "NoCare",
        "NoMeds",
        "HerbalOrWorse",
        "NormalOrWorse",
        "Best"
      ],
      "description": "Medicine quality"
    },
    "selfTend": {
      "type": "boolean",
      "description": "Whether the pawn tends its own wounds"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **5**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 4 × `object` with keys: `_paused`, `medCare`, `ok`, `pawn`, `selfTend`. Example: `campaigns/continuance/reference/legacy/history.jsonl:150`.
- 1 × `object` with keys: `_notifications`, `_paused`, `medCare`, `ok`, `pawn`, `selfTend`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1849`.

Observed selector combinations: `{}` (5).

All **12** nested observed paths, type counts and provenance are in `inventory.json` → `tools.set_medical_care.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## list_surgeries

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/HealthTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/HealthTools.cs`) registration line 28 → `Collect = ListSurgeries` (method line 114). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

List the surgeries/operations available now on a pawn (Health tab → Operations): recipe defName/label and, for part-targeted ones, the body parts you can pick. Pawn by 'id' or 'name'.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Pawn ThingID"
    },
    "name": {
      "type": "string",
      "description": "Pawn name"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## add_surgery

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/HealthTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/HealthTools.cs`) registration line 38 → `Collect = AddSurgery` (method line 171). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Queue a surgery/operation on a pawn. 'recipe' = a surgery RecipeDef defName/label from list_surgeries; 'part' = body part label or index (required when the operation targets a body part and there is more than one option). Remove queued surgeries with delete_bill on the pawn id.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Pawn ThingID"
    },
    "name": {
      "type": "string",
      "description": "Pawn name"
    },
    "recipe": {
      "type": "string",
      "description": "Surgery RecipeDef defName or label"
    },
    "part": {
      "type": "string",
      "description": "Body part label or index (from list_surgeries)"
    }
  },
  "required": [
    "recipe"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## list_trade

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/TradeTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/TradeTools.cs`) registration line 26 → `Collect = ListTrade` (method line 176). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

List the current trade deal (requires an open trade — start one with order_pawn 'Trade with…'). Returns the trader, negotiator, gift mode, the colony's silver balance, and each tradeable with its label/def, colonyCount, traderCount, buyPrice (to buy from trader), sellPrice (to sell), the current signed 'transfer' (positive=buying, negative=selling) and 'action'. Filter by 'filter' (name substring); 'limit' caps rows (default 200).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "filter": {
      "type": "string",
      "description": "Only tradeables whose label contains this text (case-insensitive)"
    },
    "limit": {
      "type": "integer",
      "description": "Max tradeables to return (default 200)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **4**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 3 × `object` with keys: `_dialogOpen`, `_paused`, `active`, `giftMode`, `negotiator`, `ok`, `returned`, `silver`, `tradeableCount`, `tradeables`, `trader`. Example: `campaigns/continuance/reference/legacy/history.jsonl:339`.
- 1 × `object` with keys: `_paused`, `active`, `giftMode`, `negotiator`, `ok`, `returned`, `silver`, `tradeableCount`, `tradeables`, `trader`. Example: `campaigns/continuance/reference/legacy/history.jsonl:419`.

Observed selector combinations: `{}` (4).

All **25** nested observed paths, type counts and provenance are in `inventory.json` → `tools.list_trade.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## set_trade

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/TradeTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/TradeTools.cs`) registration line 36 → `Collect = SetTrade` (method line 239). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Set how much of one tradeable to move in the active trade. Identify it by 'index' (from list_trade), 'def' (ThingDef defName), or 'label'. Then either give a signed 'transfer' (positive=buy from trader, negative=sell to colony) OR 'action'='buy'/'sell' with a positive 'count'. The amount is clamped to what's available. Returns the resulting transfer, price and cost.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "index": {
      "type": "integer",
      "description": "Tradeable index from list_trade"
    },
    "def": {
      "type": "string",
      "description": "ThingDef defName (alternative to index)"
    },
    "label": {
      "type": "string",
      "description": "Tradeable label (case-insensitive; alternative to index)"
    },
    "transfer": {
      "type": "integer",
      "description": "Signed target count: positive=buy, negative=sell (absolute set)"
    },
    "action": {
      "type": "string",
      "enum": [
        "buy",
        "sell"
      ],
      "description": "With 'count': whether to buy or sell"
    },
    "count": {
      "type": "integer",
      "description": "Positive amount to buy/sell (used with 'action')"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **3**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 3 × `object` with keys: `_dialogOpen`, `_paused`, `action`, `buyPrice`, `colonyCount`, `def`, `index`, `label`, `ok`, `requested`, `sellPrice`, `silverAfterDeal`, `traderCount`, `transfer`. Example: `campaigns/continuance/reference/legacy/history.jsonl:340`.

Observed selector combinations: `{}` (3).

All **15** nested observed paths, type counts and provenance are in `inventory.json` → `tools.set_trade.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## trade_action

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/TradeTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/TradeTools.cs`) registration line 50 → `Collect = TradeAct` (method line 308). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Finalize the active trade: 'accept' executes the deal (and closes the dialog), 'reset' clears all pending amounts, 'cancel' closes the trade without trading. Returns whether anything traded.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": [
        "accept",
        "reset",
        "cancel"
      ],
      "description": "Trade action"
    }
  },
  "required": [
    "action"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **3**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 2 × `object` with keys: `_paused`, `did`, `note`, `ok`, `traded`. Example: `campaigns/continuance/reference/legacy/history.jsonl:342`.
- 1 × `object` with keys: `_paused`, `did`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:899`.

Observed selector combinations: `{"action": "accept"}` (2), `{"action": "cancel"}` (1).

All **6** nested observed paths, type counts and provenance are in `inventory.json` → `tools.trade_action.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## manage_prisoner

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/PrisonerTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/PrisonerTools.cs`) registration line 15 → `Collect = ManagePrisoner` (method line 47). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Read or set the treatment of a captured pawn (the Prisoner/Slave inspect tab). Without 'mode': reports status (Prisoner/Slave), current interaction mode, resistance, will, recruitable, and the available modes to choose from. With 'mode' (defName or label): for a PRISONER sets the exclusive interaction mode (e.g. NoInteraction=leave alone, AttemptRecruit=recruit, ReduceResistance, Convert=change ideoligion, Enslave, Release, Execution) — or toggles a non-exclusive mode (Bloodfeed/HemogenFarm/Study) with 'enabled'. For a SLAVE sets the slave interaction mode (e.g. NoInteraction, Suppress, Emancipate, Execute, Imprison). Identify the pawn by 'id' or 'name'.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "description": "Prisoner/slave pawn ThingID (from list_things/inspect_thing)"
    },
    "name": {
      "type": "string",
      "description": "Prisoner/slave name (case-insensitive substring)"
    },
    "mode": {
      "type": "string",
      "description": "Interaction mode defName or label to set (omit to just read state)"
    },
    "enabled": {
      "type": "boolean",
      "description": "For a non-exclusive prisoner mode: enable (true, default) or disable (false)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **12**. Explicit error-marker records: **2**.

Root-key variants (counts are evidence records):

- 2 × `object` with keys: `_paused`, `error`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:399`.
- 5 × `object` with keys: `_paused`, `label`, `mode`, `name`, `ok`, `status`. Example: `campaigns/continuance/reference/legacy/history.jsonl:405`.
- 5 × `object` with keys: `_paused`, `availableModes`, `id`, `interactionMode`, `name`, `ok`, `recruitable`, `resistance`, `status`, `will`. Example: `campaigns/continuance/reference/legacy/history.jsonl:517`.

Observed selector combinations: `{}` (12).

All **19** nested observed paths, type counts and provenance are in `inventory.json` → `tools.manage_prisoner.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## list_world_objects

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/WorldTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/WorldTools.cs`) registration line 108 → `Collect = ListWorldObjects` (method line 297). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

List objects on the world map: faction settlements (faction/relation/goodwill, whether you can trade), your caravans (tile, pawns, food days, mass, moving/destination), sites, AND every other world object — so it includes launch/gravship destinations. Each has an 'id' (use with world_object_action / caravan_action / world_target targetId=) and a 'tile'. With the Odyssey DLC, each row also reports its planet 'layer' and 'layerId', and 'space':true for non-surface (orbital) objects — use kind='space' to list only those; that id/tile+layerId is how you send pods/shuttle/gravship to a space destination via world_target. Sorted nearest-first from 'fromTile' (defaults to your colony tile), with 'distanceTiles' (straight-line). The nearest ~5 surface objects also carry 'travelDays' — estimated caravan travel time over the ACTUAL route (terrain costs, roads) at standard caravan speed — or 'caravanUnreachable':true when no land route exists; use travelDays, not distanceTiles, to judge how far a trip really is.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "kind": {
      "type": "string",
      "enum": [
        "all",
        "settlements",
        "caravans",
        "sites",
        "space"
      ],
      "description": "Filter by object kind ('space' = non-surface/orbital, Odyssey only)"
    },
    "faction": {
      "type": "string",
      "description": "Only objects of this faction (name substring, optional)"
    },
    "fromTile": {
      "type": "integer",
      "description": "Reference tile for distance sorting (default: your colony tile)"
    },
    "confirm": {
      "type": "boolean",
      "description": "Fetch the full output even when it exceeds the large-output guard (~25k chars)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **1**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `_dialogOpen`, `_paused`, `count`, `fromTile`, `objects`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1375`.

Observed selector combinations: `{"kind": "sites"}` (1).

All **19** nested observed paths, type counts and provenance are in `inventory.json` → `tools.list_world_objects.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## get_world_tile

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/WorldTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/WorldTools.cs`) registration line 121 → `Collect = GetWorldTile` (method line 821). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Inspect a world tile and its surroundings, and FOCUS the game on it: selects the tile and jumps the world camera there so the human watching sees what you are inspecting. Returns biome, hilliness, temperature, rainfall, elevation, swampiness, pollution, coastal, named region, any world objects on it, its immediate neighbouring tiles, and a 'surroundings' summary (nearby biomes/hilliness within a few tiles, whether rivers/roads/coast touch the area, and nearby settlements with faction/hostility/distance/compass direction). Give 'tile' (a tile id from list_world_objects or a neighbour); defaults to your current colony's tile. Also reports 'distanceTiles' (straight-line) and 'travelDays' from 'fromTile' (default: your colony) — estimated caravan travel time over the ACTUAL route (terrain, roads) at standard speed — or 'caravanUnreachable':true when no land route exists.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "tile": {
      "type": "integer",
      "description": "World tile id (default: current colony tile)"
    },
    "fromTile": {
      "type": "integer",
      "description": "Reference tile for distance/travelDays (default: your colony tile)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## caravan_action

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/WorldTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/WorldTools.cs`) registration line 131 → `Collect = CaravanAction` (method line 1024). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Observe or control one of YOUR caravans (identify by 'id' from list_world_objects, or 'name'). Without any action: selects it on the world map and reports its status, its 'members' (every travelling pawn with health/mood/food/rest, injuries, downed/bleeding, and their food/drug/medical settings), its 'cargo' (grouped carried items — this is where the caravan's food and medicine are), available gizmos AND 'arrivalActions' — the right-click float-menu options on the world map for the world object(s) at its tile (Enter map, Trade, Attack, Visit, Offer gifts, …), each with a label and disabled reason. 'option' (label) or 'optionIndex' executes one of those arrival/right-click actions (this is how a caravan enters a map, trades, attacks a settlement, etc. on arrival). 'targetId' picks a specific world object to act on; 'targetTile' lists options for a different tile (default: the caravan's own tile). 'gizmo' (label or index) executes a caravan world gizmo (Settle, Split, Pause, Merge, form-camp, …). 'gotoTile' sends it travelling to a tile. 'tradeWith' (a settlement id or tile) sends it to that settlement to trade — on arrival the trade dialog opens, then use list_trade/set_trade/trade_action.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "description": "Caravan id (WorldObject id from list_world_objects)"
    },
    "name": {
      "type": "string",
      "description": "Caravan name (case-insensitive substring)"
    },
    "gizmo": {
      "type": "string",
      "description": "Caravan gizmo label to execute (case-insensitive)"
    },
    "index": {
      "type": "integer",
      "description": "Caravan gizmo index (alternative to gizmo label)"
    },
    "option": {
      "type": "string",
      "description": "Arrival/right-click float-menu option label to execute (Enter/Trade/Attack/Visit/…)"
    },
    "optionIndex": {
      "type": "integer",
      "description": "Arrival/right-click float-menu option index (alternative to option label)"
    },
    "targetId": {
      "type": "integer",
      "description": "World object id to act on for arrival actions (default: object at the caravan's tile)"
    },
    "targetTile": {
      "type": "integer",
      "description": "Tile whose world objects' arrival actions to list/execute (default: caravan's tile)"
    },
    "gotoTile": {
      "type": "integer",
      "description": "Send the caravan travelling to this world tile"
    },
    "tradeWith": {
      "type": "integer",
      "description": "Send the caravan to this settlement (id or tile) to trade"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## world_target

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/WorldTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/WorldTools.cs`) registration line 149 → `Background = WorldTarget` (method line 1898). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Complete a DESTINATION selection opened by launching transport pods / a shuttle / an Odyssey gravship (do_thing_action label='Launch'), including the follow-up in-map landing spot. Handles all three targeters: the world-tile crosshair (pods/shuttle), the gravship tile picker, and the in-map landing cell. Without args: reports which selection is active (worldTileTargeting / gravshipTargeting / mapCellTargeting) and any open pulldown. To confirm a WORLD TILE give 'tile' (from list_world_objects/find_world_tiles/get_world_tile) or 'targetId' (a world object id — carries the correct planet layer, so this is how you reach SPACE/orbital objects); add 'layer' to target a bare non-surface (space) tile. Some tiles offer several choices (settlement: give gift/trade/attack/drop at edge; a tile with a map: 'Land in specific spot'): a pulldown opens and its 'options' come back — pick one with 'option'. If the destination has an EXISTING MAP you then choose the exact landing cell: the result flags 'openedMapCellTarget' — call again with 'x'+'z' (a cell on that map). Out of range / low fuel / impassable → 'rejected'. 'cancel'=true aborts. The camera frames the target before confirming (watchable). A landed GRAVSHIP (Odyssey) also asks where on the destination map to set down — when discovery shows 'gravshipLanding':true, give x+z (+ optional 'rot' 0-3) for the ship's landing cell/rotation; the ship footprint must fit on the map (landing clears whatever is there).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "tile": {
      "type": "integer",
      "description": "Destination world tile id to confirm (pods/shuttle or gravship)"
    },
    "targetId": {
      "type": "integer",
      "description": "Destination world object id (settlement/site/space object) — carries the correct planet layer"
    },
    "layer": {
      "type": "integer",
      "description": "Planet layer id for a bare 'tile' on a non-surface layer (e.g. space/orbit); omit for the surface"
    },
    "x": {
      "type": "integer",
      "description": "In-map landing cell X (with z): pod-arrival landing spot, or the gravship's landing cell"
    },
    "z": {
      "type": "integer",
      "description": "In-map landing cell Z (with x)"
    },
    "rot": {
      "type": "integer",
      "description": "Gravship landing rotation 0-3 (N/E/S/W); omit to keep the marker's current rotation"
    },
    "option": {
      "type": "string",
      "description": "Pick an option from the pulldown that opened: its label (case-insensitive) or numeric index"
    },
    "cancel": {
      "type": "boolean",
      "description": "Cancel the active target selection (right-click / Esc equivalent)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## find_world_tiles

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/WorldTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/WorldTools.cs`) registration line 165 → `Collect = FindWorldTiles` (method line 2745). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Scan the world map and return the tiles matching a filter — for scouting settle spots or routes. The matches are HIGHLIGHTED with marker rings on the planet for ~15 seconds and the world camera jumps to the nearest/best match, so the human watching sees the candidates (markers only draw while the world map is on screen). Filters (all optional, combined with AND): 'biome' (name/defName substring), 'hilliness' (exact Flat/SmallHills/LargeHills/Mountainous/Impassable) or 'maxHilliness', temperature range ('tempMin'/'tempMax', °C), 'rainfallMin'/'rainfallMax' (mm), 'elevationMin'/'elevationMax' (m), 'coastal', 'road', 'river' (booleans). Restrict the search to 'maxDistance' tiles from 'fromTile' (default: your colony tile). Results are sorted nearest-first with 'distanceTiles'; 'limit' caps rows (default 100, max 500). Reports 'totalMatched' even when truncated.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "biome": {
      "type": "string",
      "description": "Biome name or defName (case-insensitive substring)"
    },
    "hilliness": {
      "type": "string",
      "enum": [
        "Flat",
        "SmallHills",
        "LargeHills",
        "Mountainous",
        "Impassable"
      ],
      "description": "Exact hilliness"
    },
    "maxHilliness": {
      "type": "string",
      "enum": [
        "Flat",
        "SmallHills",
        "LargeHills",
        "Mountainous",
        "Impassable"
      ],
      "description": "Max hilliness (inclusive)"
    },
    "tempMin": {
      "type": "integer",
      "description": "Min average temperature °C"
    },
    "tempMax": {
      "type": "integer",
      "description": "Max average temperature °C"
    },
    "rainfallMin": {
      "type": "integer",
      "description": "Min rainfall mm"
    },
    "rainfallMax": {
      "type": "integer",
      "description": "Max rainfall mm"
    },
    "elevationMin": {
      "type": "integer",
      "description": "Min elevation m"
    },
    "elevationMax": {
      "type": "integer",
      "description": "Max elevation m"
    },
    "coastal": {
      "type": "boolean",
      "description": "Require coastal (true) or inland (false)"
    },
    "road": {
      "type": "boolean",
      "description": "Require a road (true) or no road (false)"
    },
    "river": {
      "type": "boolean",
      "description": "Require a river (true) or no river (false)"
    },
    "maxDistance": {
      "type": "integer",
      "description": "Only tiles within this many tiles of fromTile"
    },
    "fromTile": {
      "type": "integer",
      "description": "Reference tile for distance filter/sort (default: colony tile)"
    },
    "limit": {
      "type": "integer",
      "description": "Max tiles to return (default 100, max 500)"
    },
    "confirm": {
      "type": "boolean",
      "description": "Fetch the full output even when it exceeds the large-output guard (~25k chars)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## form_caravan

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/WorldTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/WorldTools.cs`) registration line 190 → `Background = FormCaravan` (method line 2935). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Form a caravan by DRIVING the REAL in-game Form Caravan dialog on screen, at a human-watchable pace: the dialog opens, the Pawns tab is shown and each chosen colonist/animal is ticked into the caravan one at a time, then the Items tab is shown and each requested item's count is dialed up, then the Send button is pressed. Vanilla's own validation runs (overweight, no valid exit, unreachable items, low-food warning) and its messages/warnings show on screen. On a successful Send the chosen pawns gather the items at a packing spot, carry them, walk to the map edge and leave to the world map over in-game time (NOT instant); advance time (wait_for_event) and the formed caravan appears in list_world_objects. 
mode='start' (default): 'pawns' = colonists/animals to send (comma-separated ids or names, or a JSON array); required. 'items' = optional cargo, comma-separated 'defName:count' pairs (e.g. 'Silver:500,MealSimple:30') — only items the dialog offers (reachable in the home area/storage) load. 'destinationTile' (optional) is where the formed caravan heads; the exit edge is chosen along that route (omitted: a nearby exit tile is used). 
mode='status': report any in-progress caravan formations on the map (which stage they're at, pawns, items still to load). 
mode='cancel': stop an in-progress formation (unloads everything) — use this if a formation is stuck, since it otherwise blocks the pawns.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "mode": {
      "type": "string",
      "enum": [
        "start",
        "status",
        "cancel"
      ],
      "description": "start (begin forming, default), status (report in-progress formations), cancel (abort a formation)"
    },
    "pawns": {
      "type": "string",
      "description": "Colonists/animals to send: comma-separated ThingIDs or names (or a JSON array)"
    },
    "items": {
      "type": "string",
      "description": "Optional cargo: comma-separated defName:count pairs (e.g. Silver:500,MealSimple:30)"
    },
    "destinationTile": {
      "type": "integer",
      "description": "Optional destination world tile; the exit edge is chosen along the route to it"
    },
    "mapIndex": {
      "type": "integer",
      "description": "Source map index (default: current map)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## world_object_action

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/WorldTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/WorldTools.cs`) registration line 203 → `Collect = WorldObjectAction` (method line 1467). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Observe or operate a WORLD OBJECT's gizmos — the buttons shown when it is selected on the world map: your settlements/camps, NPC settlements, sites, and any modded world object. Identify it by 'id' (from list_world_objects) or 'name'. Without 'gizmo'/'index': selects it on the world map (camera jumps, so the human sees it) and returns its status and gizmo list, each with any disabled reason. 'gizmo' (label, case-insensitive) or 'index' executes one — e.g. 'Show sellable items' on an NPC settlement (a dialog opens: read it with get_window_ui). ABANDONING one of your colonies (the 'Abandon' gizmo) is DESTRUCTIVE and two-phase: choosing it first only returns a REVIEW of exactly what would be lost (pawns left behind are banished, everything on the map is lost); re-call with confirm=true to actually abandon — this frees a slot toward the max-colonies limit. For your caravans prefer caravan_action (adds travel/trade/arrival actions on top of gizmos).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "description": "World object id (from list_world_objects)"
    },
    "name": {
      "type": "string",
      "description": "World object name (case-insensitive substring; your own objects match first)"
    },
    "gizmo": {
      "type": "string",
      "description": "Gizmo label to execute (case-insensitive)"
    },
    "index": {
      "type": "integer",
      "description": "Gizmo index (alternative to gizmo label)"
    },
    "confirm": {
      "type": "boolean",
      "description": "Only for the destructive Abandon gizmo: true = actually abandon (after a review call)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## game_setup_status

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GameSetupTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GameSetupTools.cs`) registration line 123 → `Collect = Status` (method line 327). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Report where you are in the new-game flow and what to do next. Returns 'programState' (Entry=main menu/setup, Playing=colony running), the current 'stage' (main_menu, scenario, storyteller, planet, starting_site, ideoligion, configure_ideo, pawns, loading, in_game), the choices available at that stage, and a 'hint'. Poll this after any setup step, especially after create_world / start_game which generate asynchronously.

### Declared input schema

```json
{
  "type": "object",
  "properties": {}
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **2**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `hint`, `ok`, `pawns`, `programState`, `stage`. Example: `campaigns/continuance/reference/legacy/history.jsonl:52`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `hint`, `ok`, `programState`, `stage`. Example: `campaigns/continuance/reference/legacy/history.jsonl:74`.

Observed selector combinations: `{}` (2).

All **25** nested observed paths, type counts and provenance are in `inventory.json` → `tools.game_setup_status.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## main_menu

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GameSetupTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GameSetupTools.cs`) registration line 129 → `Collect = MainMenu` (method line 465). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Main-menu actions (only valid at ProgramState.Entry). action='new_colony' begins a new game (opens the scenario page — follow with select_scenario). action='list_saves' lists saved games. action='load_save' with 'name' loads that save (asynchronous; poll game_setup_status until Playing).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": [
        "new_colony",
        "list_saves",
        "load_save"
      ],
      "description": "What to do"
    },
    "name": {
      "type": "string",
      "description": "Save file name (for load_save; without extension)"
    }
  },
  "required": [
    "action"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## save_game

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GameSetupTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GameSetupTools.cs`) registration line 139 → `Collect = SaveGame` (method line 533). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Save the current game to a save file. 'name' picks the file name (default: the file this session last saved to or loaded from — i.e. overwrite the current save — else the colony name). If a save with that name already exists on disk, this is REFUSED with a warning (the file's timestamp and instructions) instead of overwriting it — pass overwrite=true to confirm overwriting, or a different 'name' to save as a new file. In commitment (permadeath) mode the game's fixed permadeath save file is always used and 'name'/'overwrite' are ignored — it is always overwritten there, exactly as in vanilla.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Save file name, no extension (default: overwrite the last-used save, else the colony name)"
    },
    "overwrite": {
      "type": "boolean",
      "description": "Confirm overwriting an existing save file with this name (required when one already exists; ignored in permadeath mode)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **8**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 8 × `object` with keys: `_paused`, `ok`, `permadeath`, `saved`. Example: `campaigns/continuance/reference/legacy/history.jsonl:351`.

Observed selector combinations: `{}` (8).

All **5** nested observed paths, type counts and provenance are in `inventory.json` → `tools.save_game.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## load_game

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GameSetupTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GameSetupTools.cs`) registration line 149 → `Collect = LoadGame` (method line 611). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Load a saved game (works in-game and at the main menu). Without 'name': lists the available saves with timestamps, newest first. With 'name': starts loading it (asynchronous — poll get_status/game_setup_status until the colony is loaded). REFUSED while playing in commitment (permadeath) mode, matching vanilla. If in-game time has passed since the last save, a warning is returned instead of loading — call save_game first, or re-call with confirm=true to deliberately discard that progress.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Save file name to load (omit to list all saves with timestamps)"
    },
    "confirm": {
      "type": "boolean",
      "description": "Proceed even though unsaved progress since the last save will be lost"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## return_to_title

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GameSetupTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GameSetupTools.cs`) registration line 159 → `Collect = ReturnToTitle` (method line 662). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Quit the current game to the main menu (title screen). If in-game time has passed since the last save it warns first — pass save=true to save-and-quit (recommended), or confirm=true to discard the unsaved progress. In commitment (permadeath) mode it always saves to the fixed permadeath file before quitting ('Save and quit to main menu' is vanilla's only option there). Asynchronous — poll game_setup_status until stage=main_menu.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "save": {
      "type": "boolean",
      "description": "Save first (save_game with its default name), then quit to title"
    },
    "confirm": {
      "type": "boolean",
      "description": "Quit WITHOUT saving, discarding progress since the last save"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## select_scenario

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GameSetupTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GameSetupTools.cs`) registration line 169 → `Background = SelectScenario` (method line 814). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

On the scenario page, pick a scenario by 'name' and advance to the storyteller page. There is NO default — you must name a scenario explicitly. A review gate applies: the FIRST call at this page (if you have not yet listed the scenarios via game_setup_status) does NOT advance — it returns the full scenario list with summaries and asks you to call again with an explicit choice, so you read the actual options before committing. The chosen scenario is then visibly highlighted on the page for a moment before advancing (so the human watching sees the selection).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "Scenario name (case-insensitive; e.g. 'Crashlanded', 'The Rich Explorer', 'Lost Tribe')"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## select_storyteller

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GameSetupTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GameSetupTools.cs`) registration line 175 → `Background = SelectStoryteller` (method line 890). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

On the storyteller page, choose the AI storyteller + difficulty + reload mode and advance to planet creation. There are NO defaults — 'storyteller', 'difficulty' and 'reloadAnytime' must ALL be given explicitly (resolve storyteller/difficulty by defName or label). A review gate applies: the FIRST call at this page (if you have not yet listed the options via game_setup_status) does NOT advance — it returns the full storyteller and difficulty lists with descriptions and asks you to call again with explicit choices. The choices are then applied ONE AT A TIME on screen (storyteller → difficulty → reload mode), each visible for a moment, before the page advances.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "storyteller": {
      "type": "string",
      "description": "Storyteller defName or label (e.g. 'Cassandra', 'Phoebe', 'Randy') — required"
    },
    "difficulty": {
      "type": "string",
      "description": "Difficulty defName or label (e.g. 'Rough' = Strive to Survive) — required"
    },
    "reloadAnytime": {
      "type": "boolean",
      "description": "true = reload-anytime; false = commitment/permadeath mode — required"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## create_world

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GameSetupTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GameSetupTools.cs`) registration line 186 → `Background = CreateWorld` (method line 1018). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

On the planet page, set world-generation parameters and START generating the planet (asynchronous — poll game_setup_status until stage=starting_site). All fields optional; sensible defaults are pre-filled. coverage is one of 0.3/0.5/1.0. rainfall/temperature/population accept 'Low'/'Normal'/'High'. pollution is 0..1 (Biotech).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "seed": {
      "type": "string",
      "description": "World seed string (default = random)"
    },
    "coverage": {
      "type": "number",
      "description": "Planet coverage 0.3, 0.5 or 1.0"
    },
    "rainfall": {
      "type": "string",
      "enum": [
        "Low",
        "Normal",
        "High"
      ],
      "description": "Overall rainfall"
    },
    "temperature": {
      "type": "string",
      "enum": [
        "Low",
        "Normal",
        "High"
      ],
      "description": "Overall temperature"
    },
    "population": {
      "type": "string",
      "enum": [
        "Low",
        "Normal",
        "High"
      ],
      "description": "Overall population (faction density)"
    },
    "pollution": {
      "type": "number",
      "description": "Pollution 0..1 (Biotech only)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## select_starting_site

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GameSetupTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GameSetupTools.cs`) registration line 200 → `Background = SelectStartingSite` (method line 1096). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Choose the colony's starting tile — a TWO-PHASE, review-then-confirm flow so you (and the human watching) actually look at the site first. Phase 1: call with 'tile' (a world tile id from find_world_tiles/get_world_tile) or omit it for a random valid candidate. This does NOT settle: it selects the tile, jumps the world camera to frame it, and returns a full dossier — 'tileInfo' (biome, temperature, rainfall, POLLUTION, swampiness, hilliness, coastal), 'surroundings' (nearby biomes, hilliness, rivers/roads/coast and neighbouring settlements with faction/hostility/direction) and, when other factions' bases are close, 'proximityGoodwill' (the recurring per-quadrum goodwill penalty). Phase 2: re-call with confirm=true to actually settle the reviewed tile and advance (pass the same 'tile', or omit it to settle the candidate from phase 1). The tile is validated for settlement before advancing.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "tile": {
      "type": "integer",
      "description": "World tile id (omit for a random valid candidate; on confirm, omit to settle the phase-1 candidate)"
    },
    "confirm": {
      "type": "boolean",
      "description": "true = settle the reviewed tile and advance; false/omitted = review only (phase 1)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## choose_ideoligion

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GameSetupTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GameSetupTools.cs`) registration line 210 → `Collect = ChooseIdeoligion` (method line 1343). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

On the ideoligion page (Ideology DLC only), pick how the colony's ideoligion is made. mode='fluid' (RECOMMENDED: a Custom ideoligion that evolves during play) or 'fixed' both open a full editor — a complete ideoligion is generated and you then customize it with edit_ideoligion (structure/memes/precepts/name) before finalizing. mode='classic' (simple non-ideoligion mode) and mode='preset' (with 'preset'=an IdeoPreset defName/label, optional 'structure' meme) commit immediately and go straight to character creation.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "mode": {
      "type": "string",
      "enum": [
        "fluid",
        "fixed",
        "classic",
        "preset"
      ],
      "description": "Ideoligion mode"
    },
    "preset": {
      "type": "string",
      "description": "IdeoPreset defName or label (for mode=preset)"
    },
    "structure": {
      "type": "string",
      "description": "Structure meme defName/label (optional starting structure)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## edit_ideoligion

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GameSetupTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GameSetupTools.cs`) registration line 221 → `Collect = EditIdeoligion` (method line 1698). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Customize the in-progress Custom ideoligion (after choose_ideoligion mode='fluid'/'fixed') as a GUIDED, ORDERED flow so a human spectator can follow one stage at a time. Steps in order: structure → memes → precepts → roles → rituals → buildings → relics → weapons → animals → apparel → xenotypes (Biotech only, else auto-skipped) → styles → identity, then finalize. A mutation that belongs to a LATER step than the current one is REJECTED — edit the current step, or call action='next_step' (which marks the current step done, advances, and returns the new step's options so you see the choices before acting). Editing memes/structure re-randomizes precepts and rolls the flow back to 'precepts'; 'randomize' restarts the whole flow. action='status' (default) shows the 'flow'/'currentStep'/'hint' plus name/structure/memes/precepts and rituals/roles/buildings/relics/veneratedAnimals/preferredApparel/weaponPreference (each instance has an 'id'). 'options' (kind=structures/memes/issues/precepts/rituals/roles/buildings/relics/animals/apparel/weapons/xenotypes/rewards/styles/symbols/style_categories) lists choices — kind=precepts without 'issue' is a compact all-issues list. Mutations: 'set_structure' (meme), 'add_meme'/'remove_meme'/'set_memes', 'set_precept' (basic: swaps the issue's precept; special: adds — rituals take 'pattern', buildings/relics/animals/apparel take 'thing', weapons take 'noble'+'despised', xenotypes take 'xenotype'), 'remove_precept', 'rename_precept' (name, +femaleName for the leader role), 'edit_ritual' (anytime / quadrum+day / reward), 'set_style' (building visual style), 'set_thing' (switch a precept's ThingDef in place, e.g. the ritual seat), 'set_style_category' (add/remove culture style categories, max 3), 'set_name' (name/adjective/memberName), 'set_symbols' (icon/color), 'set_description' (text or random=true), 'randomize'. Meme count follows the game's rules ('memeRange' in status): a FLUID ideoligion starts with exactly 1 normal meme (use set_memes to swap it); a FIXED one allows 1-4. action='finalize' commits the ideoligion and advances to character creation (only once the flow reaches 'identity').

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": [
        "status",
        "options",
        "next_step",
        "set_structure",
        "add_meme",
        "remove_meme",
        "set_memes",
        "set_precept",
        "remove_precept",
        "rename_precept",
        "edit_ritual",
        "set_style",
        "set_thing",
        "set_style_category",
        "set_name",
        "set_symbols",
        "set_description",
        "randomize",
        "finalize"
      ],
      "description": "What to do"
    },
    "kind": {
      "type": "string",
      "enum": [
        "structures",
        "memes",
        "issues",
        "precepts",
        "rituals",
        "roles",
        "buildings",
        "relics",
        "animals",
        "apparel",
        "weapons",
        "xenotypes",
        "rewards",
        "styles",
        "symbols",
        "style_categories"
      ],
      "description": "For action=options: which list"
    },
    "issue": {
      "type": "string",
      "description": "IssueDef defName/label (for options kind=precepts; omit for all issues)"
    },
    "meme": {
      "type": "string",
      "description": "MemeDef defName/label (for set_structure/add_meme/remove_meme)"
    },
    "memes": {
      "type": "string",
      "description": "Normal meme defNames/labels (csv or JSON array, for set_memes)"
    },
    "precept": {
      "type": "string",
      "description": "PreceptDef defName/label to add (set_precept), or an existing precept's instance id/name (remove_precept/rename_precept/edit_ritual/set_style/set_thing, options kind=rewards/styles)"
    },
    "pattern": {
      "type": "string",
      "description": "RitualPatternDef defName (set_precept on a ritual; see options kind=rituals)"
    },
    "thing": {
      "type": "string",
      "description": "ThingDef defName/label (set_precept on a building/relic/venerated-animal/apparel precept; set_thing to replace a ritual seat's thing in place — see options kind=buildings)"
    },
    "noble": {
      "type": "string",
      "description": "WeaponClassDef for the noble side (set_precept on the weapon precept)"
    },
    "despised": {
      "type": "string",
      "description": "WeaponClassDef for the despised side (set_precept on the weapon precept)"
    },
    "xenotype": {
      "type": "string",
      "description": "XenotypeDef defName/label (set_precept on a xenotype precept; Biotech)"
    },
    "name": {
      "type": "string",
      "description": "New name (for set_name / rename_precept; precept names max 32 chars, symbols max 40)"
    },
    "adjective": {
      "type": "string",
      "description": "New adjective for the ideoligion (set_name; max 40 chars)"
    },
    "memberName": {
      "type": "string",
      "description": "New name for the ideoligion's members (set_name; max 40 chars)"
    },
    "icon": {
      "type": "string",
      "description": "IdeoIconDef defName (set_symbols; see options kind=symbols)"
    },
    "color": {
      "type": "string",
      "description": "ColorDef defName, ColorType.Ideo only (set_symbols; see options kind=symbols)"
    },
    "description": {
      "type": "string",
      "description": "New description text (set_description; omit and pass random=true to auto-generate)"
    },
    "random": {
      "type": "boolean",
      "description": "set_description: true = generate a fresh random description"
    },
    "add": {
      "type": "string",
      "description": "StyleCategoryDef defName to add (set_style_category; see options kind=style_categories)"
    },
    "remove": {
      "type": "string",
      "description": "StyleCategoryDef defName to remove (set_style_category)"
    },
    "femaleName": {
      "type": "string",
      "description": "Female leader title (rename_precept on the leader role only)"
    },
    "anytime": {
      "type": "boolean",
      "description": "edit_ritual: true = startable anytime, false = date/trigger-bound"
    },
    "quadrum": {
      "type": "string",
      "enum": [
        "Aprimay",
        "Jugust",
        "Septober",
        "Decembary"
      ],
      "description": "edit_ritual: quadrum of the fixed date"
    },
    "day": {
      "type": "integer",
      "description": "edit_ritual: day of the quadrum (1-15, with 'quadrum')"
    },
    "reward": {
      "type": "string",
      "description": "edit_ritual: RitualAttachableOutcomeEffectDef defName, or 'none' to clear (see options kind=rewards precept=<ritual>)"
    },
    "style": {
      "type": "string",
      "description": "set_style: style category defName (see options kind=styles precept=<building>)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **27**. Explicit error-marker records: **2**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `hint`, `items`, `kind`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1`.
- 8 × `object` with keys: `action`, `ideo`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:2`.
- 2 × `object` with keys: `error`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:3`.
- 1 × `object` with keys: `action`, `completedStep`, `currentStep`, `flow`, `hint`, `ideo`, `ok`, `options`, `skipped`. Example: `campaigns/continuance/reference/legacy/history.jsonl:12`.
- 1 × `object` with keys: `action`, `ideo`, `ok`, `removed`. Example: `campaigns/continuance/reference/legacy/history.jsonl:13`.
- 1 × `object` with keys: `action`, `anytime`, `ideo`, `ok`, `ritual`. Example: `campaigns/continuance/reference/legacy/history.jsonl:14`.
- 1 × `object` with keys: `hint`, `items`, `kind`, `ok`, `ritual`. Example: `campaigns/continuance/reference/legacy/history.jsonl:15`.
- 1 × `object` with keys: `action`, `ideo`, `ok`, `reward`, `ritual`. Example: `campaigns/continuance/reference/legacy/history.jsonl:16`.
- 1 × `object` with keys: `action`, `added`, `ideo`, `ok`, `pattern`. Example: `campaigns/continuance/reference/legacy/history.jsonl:17`.
- 8 × `object` with keys: `action`, `completedStep`, `currentStep`, `flow`, `hint`, `ideo`, `ok`, `options`. Example: `campaigns/continuance/reference/legacy/history.jsonl:18`.
- 1 × `object` with keys: `action`, `adjective`, `currentStep`, `flow`, `hint`, `ideo`, `memberName`, `name`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:26`.
- 1 × `object` with keys: `hint`, `ok`, `stage`. Example: `campaigns/continuance/reference/legacy/history.jsonl:27`.

Observed selector combinations: `{"action": "options", "kind": "precepts"}` (1), `{"action": "set_precept"}` (11), `{"action": "next_step"}` (9), `{"action": "remove_precept"}` (1), `{"action": "edit_ritual"}` (2), `{"action": "options", "kind": "rewards"}` (1), `{"action": "set_name"}` (1), `{"action": "finalize"}` (1).

All **135** nested observed paths, type counts and provenance are in `inventory.json` → `tools.edit_ideoligion.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## edit_starting_pawn

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GameSetupTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GameSetupTools.cs`) registration line 255 → `Background = EditStartingPawn` (method line 2884). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Review/adjust the starting colonists — works BOTH on the new-game character-creation page AND on the post-colony-wipe "create new colonists" window (opened from the GameOver letter via read_letter open=true once every colonist is lost; drive that letter's create choice with window_action first). action='list' (default) shows all pawns with index, name, skills+passions, traits, incapabilities, health and xenotype ('context' tells you whether you're in 'setup' or the post-wipe 'wanderers' dialog). action='reroll' regenerates the pawn at 'index' once. action='reroll_until' keeps rerolling the pawn at 'index' until it matches ALL given conditions (traits/avoidTraits/passions/minSkills/capableOf/healthy/gender/minAge/maxAge), up to 'attempts' rerolls (the human's reroll-limit setting is both the default and a hard ceiling — asking for more is clamped down to it). The rerolls are PACED and VISIBLE on screen: each candidate appears in turn (fast, ~5/sec), and a small overlay window shows the conditions being searched for with a live green ✓ / red ✗ per condition for the current candidate. It stops at the first match; on giving up it reports per-condition match rates so you can see which requirement is too demanding. action='rename' sets the pawn's name (any subset of first/nick/last). action='reorder' moves the pawn at 'index' to position 'to' (also swaps which are starting vs left-behind). action='xenotype' (Biotech): WITHOUT 'xenotype' it LISTS every choosable xenotype (base-game defs AND saved custom ones) with its genes, description and inheritability — review these before choosing; WITH 'xenotype' it sets that xenotype on the pawn at 'index' and regenerates ('any' = random non-archite). action='create_xenotype' (Biotech) builds a NEW custom xenotype by driving the REAL vanilla Xenotype editor visibly on screen (dialog opens, each gene is added one at a time with the biostats updating, then Save & Apply) and applies it to the pawn at 'index'; without 'genes' it lists every selectable gene (grouped by category, with complexity/metabolism biostats) — the informed-choice gate. In the post-wipe 'wanderers' dialog ONLY: action='add' generates one more candidate colonist (max 6), action='remove' drops the pawn at 'index' (min 1), and action='confirm' finalizes — the chosen colonists arrive on the map. On the setup page use start_game instead of confirm.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": [
        "list",
        "reroll",
        "reroll_until",
        "rename",
        "reorder",
        "xenotype",
        "create_xenotype",
        "add",
        "remove",
        "confirm"
      ],
      "description": "What to do"
    },
    "index": {
      "type": "integer",
      "description": "Pawn index in the list (from action=list)"
    },
    "to": {
      "type": "integer",
      "description": "Target index (for action=reorder)"
    },
    "xenotype": {
      "type": "string",
      "description": "Xenotype defName/label or a custom xenotype's name, or 'any' (action=xenotype; OMIT to list all xenotypes with their genes first)"
    },
    "genes": {
      "type": "string",
      "description": "create_xenotype: genes for the new xenotype — comma-separated GeneDef defNames/labels, or a JSON array. Omit to list all selectable genes."
    },
    "name": {
      "type": "string",
      "description": "create_xenotype: name for the new xenotype (optional; auto-generated from the genes if omitted)"
    },
    "inheritable": {
      "type": "boolean",
      "description": "create_xenotype: make the genes germline/inheritable instead of xenogenes (default false)"
    },
    "ignoreRestrictions": {
      "type": "boolean",
      "description": "create_xenotype: allow archite genes / out-of-range metabolism / conflicting genes, like the editor's 'Ignore restrictions' checkbox (default false)"
    },
    "first": {
      "type": "string",
      "description": "First name (for action=rename)"
    },
    "nick": {
      "type": "string",
      "description": "Nickname — the short name shown in-game (for action=rename)"
    },
    "last": {
      "type": "string",
      "description": "Last name (for action=rename)"
    },
    "traits": {
      "type": "string",
      "description": "reroll_until: traits the pawn MUST have (csv of trait names/defNames, e.g. 'tough,industrious')"
    },
    "avoidTraits": {
      "type": "string",
      "description": "reroll_until: traits the pawn must NOT have (csv, e.g. 'pyromaniac,slothful')"
    },
    "passions": {
      "type": "string",
      "description": "reroll_until: skills that need a passion (csv; 'shooting' = any passion, 'medicine:major' = burning passion)"
    },
    "minSkills": {
      "type": "string",
      "description": "reroll_until: minimum skill levels (csv of skill:level, e.g. 'shooting:6,cooking:4')"
    },
    "capableOf": {
      "type": "string",
      "description": "reroll_until: work the pawn must NOT be incapable of (csv of work tags or WorkTypeDefs, e.g. 'Violent,Firefighting,Doctor')"
    },
    "healthy": {
      "type": "boolean",
      "description": "reroll_until: true = no diseases, chronic conditions or missing body parts"
    },
    "gender": {
      "type": "string",
      "description": "reroll_until: required gender (Male/Female)"
    },
    "minAge": {
      "type": "integer",
      "description": "reroll_until: minimum biological age"
    },
    "maxAge": {
      "type": "integer",
      "description": "reroll_until: maximum biological age"
    },
    "attempts": {
      "type": "integer",
      "description": "reroll_until: max rerolls before giving up. Defaults to (and is capped at) the human's 'Starting-colonist reroll limit' mod setting, currently 500."
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **14**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `context`, `ok`, `pawns`. Example: `campaigns/continuance/reference/legacy/history.jsonl:45`.
- 4 × `object` with keys: `action`, `attemptsUsed`, `conditionStats`, `matched`, `message`, `ok`, `pawns`, `rerolls`. Example: `campaigns/continuance/reference/legacy/history.jsonl:48`.
- 9 × `object` with keys: `action`, `ok`, `pawns`. Example: `campaigns/continuance/reference/legacy/history.jsonl:49`.

Observed selector combinations: `{"action": "list"}` (1), `{"action": "reroll_until"}` (4), `{"action": "reorder"}` (1), `{"action": "rename"}` (8).

All **28** nested observed paths, type counts and provenance are in `inventory.json` → `tools.edit_starting_pawn.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## start_game

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GameSetupTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GameSetupTools.cs`) registration line 284 → `Collect = StartGame` (method line 3923). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Finalize character creation and START the game: generates the map and drops the colonists (asynchronous — poll game_setup_status until programState=Playing). Only valid on the character-creation page.

### Declared input schema

```json
{
  "type": "object",
  "properties": {}
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **2**. Explicit error-marker records: **1**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `error`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:61`.
- 1 × `object` with keys: `message`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:73`.

Observed selector combinations: `{}` (2).

All **4** nested observed paths, type counts and provenance are in `inventory.json` → `tools.start_game.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## reform_ideoligion

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/GameSetupTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/GameSetupTools.cs`) registration line 290 → `Collect = ReformIdeoligion` (method line 2082). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Reform a FLUID ideoligion in a running colony (Ideology DLC). Reforming is gated by development points (earned from rituals/conversions) — action='status' shows points and whether you can reform now. 'begin' opens the REAL vanilla reform dialog on screen (with the ideoligions tab behind it) so the human spectator sees every edit live; give 'ideo' by name/id or omit for the player's primary. Edits are GUIDED one stage at a time (same flow as edit_ideoligion): each result carries 'currentStep'+'hint'+'flow'; do that step's edits then action='next_step' to advance, and 'finalize' (allowed only after the last step) to commit the reform (this consumes it). The game allows ONE stage-1 change per reform: a structure swap (set_structure) OR one normal-meme change (add_meme/remove_meme/set_memes — at most one meme added and one removed, count staying within ±1 of current, cap 4) OR a style-category change. Free stage-2 edits: 'set_precept'/'remove_precept' (incl. rituals/roles/buildings/relics/venerated animals/preferred apparel/weapon+xenotype preference — same args as edit_ideoligion: pattern/thing/noble+despised/xenotype), 'rename_precept', 'edit_ritual' (anytime/date/reward), 'set_style', 'set_thing' (switch a precept's ThingDef in place, e.g. the ritual seat), 'set_style_category' (add/remove culture style categories, max 3), 'set_name' (name/adjective/memberName), 'set_symbols' (icon/color) and 'set_description' (text or random=true). 'options' lists choices (same kinds as edit_ideoligion, incl. symbols/style_categories; instance ids are in the status 'working' snapshot). 'randomize' rerolls culture/precepts/appearance (not memes; restarts the flow). 'reset' reverts the working copy; 'cancel' discards it and closes the dialog. Closing the dialog in-game (or clicking its Done/Cancel) ends the session.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": [
        "status",
        "begin",
        "options",
        "next_step",
        "set_structure",
        "add_meme",
        "remove_meme",
        "set_memes",
        "set_precept",
        "remove_precept",
        "rename_precept",
        "edit_ritual",
        "set_style",
        "set_thing",
        "set_style_category",
        "set_name",
        "set_symbols",
        "set_description",
        "reset",
        "randomize",
        "finalize",
        "cancel"
      ],
      "description": "What to do"
    },
    "ideo": {
      "type": "string",
      "description": "Target ideoligion name or id (for status/begin; default = player's primary ideoligion)"
    },
    "kind": {
      "type": "string",
      "enum": [
        "structures",
        "memes",
        "issues",
        "precepts",
        "rituals",
        "roles",
        "buildings",
        "relics",
        "animals",
        "apparel",
        "weapons",
        "xenotypes",
        "rewards",
        "styles",
        "symbols",
        "style_categories"
      ],
      "description": "For action=options: which list"
    },
    "issue": {
      "type": "string",
      "description": "IssueDef defName/label (for options kind=precepts; omit for all issues)"
    },
    "meme": {
      "type": "string",
      "description": "MemeDef defName/label (for set_structure/add_meme/remove_meme)"
    },
    "memes": {
      "type": "string",
      "description": "Normal meme defNames/labels (csv or JSON array, for set_memes)"
    },
    "precept": {
      "type": "string",
      "description": "PreceptDef defName/label to add (set_precept), or an existing precept's instance id/name (remove_precept/rename_precept/edit_ritual/set_style/set_thing, options kind=rewards/styles)"
    },
    "pattern": {
      "type": "string",
      "description": "RitualPatternDef defName (set_precept on a ritual; see options kind=rituals)"
    },
    "thing": {
      "type": "string",
      "description": "ThingDef defName/label (set_precept on a building/relic/venerated-animal/apparel precept; set_thing to replace a ritual seat's thing in place — see options kind=buildings)"
    },
    "noble": {
      "type": "string",
      "description": "WeaponClassDef for the noble side (set_precept on the weapon precept)"
    },
    "despised": {
      "type": "string",
      "description": "WeaponClassDef for the despised side (set_precept on the weapon precept)"
    },
    "xenotype": {
      "type": "string",
      "description": "XenotypeDef defName/label (set_precept on a xenotype precept; Biotech)"
    },
    "name": {
      "type": "string",
      "description": "New name (for set_name / rename_precept; precept names max 32 chars, symbols max 40)"
    },
    "adjective": {
      "type": "string",
      "description": "New adjective for the ideoligion (set_name; max 40 chars)"
    },
    "memberName": {
      "type": "string",
      "description": "New name for the ideoligion's members (set_name; max 40 chars)"
    },
    "icon": {
      "type": "string",
      "description": "IdeoIconDef defName (set_symbols; see options kind=symbols)"
    },
    "color": {
      "type": "string",
      "description": "ColorDef defName, ColorType.Ideo only (set_symbols; see options kind=symbols)"
    },
    "description": {
      "type": "string",
      "description": "New description text (set_description; omit and pass random=true to auto-generate)"
    },
    "random": {
      "type": "boolean",
      "description": "set_description: true = generate a fresh random description"
    },
    "add": {
      "type": "string",
      "description": "StyleCategoryDef defName to add (set_style_category; see options kind=style_categories)"
    },
    "remove": {
      "type": "string",
      "description": "StyleCategoryDef defName to remove (set_style_category)"
    },
    "femaleName": {
      "type": "string",
      "description": "Female leader title (rename_precept on the leader role only)"
    },
    "anytime": {
      "type": "boolean",
      "description": "edit_ritual: true = startable anytime, false = date/trigger-bound"
    },
    "quadrum": {
      "type": "string",
      "enum": [
        "Aprimay",
        "Jugust",
        "Septober",
        "Decembary"
      ],
      "description": "edit_ritual: quadrum of the fixed date"
    },
    "day": {
      "type": "integer",
      "description": "edit_ritual: day of the quadrum (1-15, with 'quadrum')"
    },
    "reward": {
      "type": "string",
      "description": "edit_ritual: RitualAttachableOutcomeEffectDef defName, or 'none' to clear"
    },
    "style": {
      "type": "string",
      "description": "set_style: style category defName (see options kind=styles precept=<building>)"
    }
  },
  "required": [
    "action"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## get_live_chat

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/YoutubeTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/YoutubeTools.cs`) registration line 13 → `Collect = GetLiveChat` (method line 25). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Read recent YouTube live-chat comments the stream is receiving (the experimental YouTube Live integration; configure it on the mod's 'YouTube Live' settings screen). Returns connection status plus a list of recent messages with text and, unless hidden, an author (real display name or a stable anonymous id; broadcaster/moderator may be tagged), and Super Chat amount when applicable. Pass 'afterSeq' with the last 'latestSeq' you saw to fetch only newer messages (paging); 'limit' caps how many are returned (default 25). These same messages are also pushed to you automatically in '_notifications' (kind='chat') unless push is turned off.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "limit": {
      "type": "integer",
      "description": "Max messages to return, newest kept (default 25, max 200)."
    },
    "afterSeq": {
      "type": "integer",
      "description": "Only return messages with a sequence number greater than this (use the previous latestSeq to page)."
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **0**. Explicit error-marker records: **0**.

No standalone response captured. Its response model remains unobserved.

## screenshot

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/ScreenshotTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/ScreenshotTools.cs`) registration line 19 → `Background = TakeScreenshot` (method line 36). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Capture a screenshot of the game window (or a specific region of it) to a PNG file and return the file's ABSOLUTE PATH (the image is not returned inline — open/read that file with your image-capable reader only when you actually need to see the screen; images are context-heavy). Useful when on-screen layout matters: warning icons drawn over gizmos/portraits, visual glitches, or any UI detail the JSON tools do not convey. Requires the 'Allow AI screenshots' mod setting (default off).
Region (optional, pick at most one): give x/z/w/h together for a MAP-CELL rectangle (a min corner + size, in map cells on the current map — validated/clamped to map bounds), or give screen_rect for a SCREEN-PIXEL rectangle. Omit both to capture the whole screen.
include_ui (default true) controls whether the RimWorld UI (gizmos, tabs, dialogs, overlays) is included. include_ui=false always uses an offscreen render and NEVER moves or otherwise disturbs the player's camera; with an x/z/w/h cell rect it can capture ANY part of the map, including regions far outside the current camera view. include_ui=true with an x/z/w/h cell rect instead moves the REAL camera to fit that rect (so the UI drawn relative to world objects lines up correctly) and leaves it there afterward (noted in the result).

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "x": {
      "type": "integer",
      "description": "Map-cell rect: min X (column). Give together with z/w/h to capture a specific region of the current map instead of the whole screen. Mutually exclusive with screen_rect."
    },
    "z": {
      "type": "integer",
      "description": "Map-cell rect: min Z (row). Give together with x/w/h."
    },
    "w": {
      "type": "integer",
      "description": "Map-cell rect: width, in cells. Give together with x/z/h."
    },
    "h": {
      "type": "integer",
      "description": "Map-cell rect: height, in cells. Give together with x/z/w."
    },
    "screen_rect": {
      "type": "string",
      "description": "Crop rectangle on the screen as \"x,y,w,h\", TOP-LEFT origin, in UI points — the same coordinate space list_windows/get_window_ui report widget rects in (equal to raw device pixels only when the UI Scale setting is 1x). Mutually exclusive with x/z/w/h."
    },
    "include_ui": {
      "type": "boolean",
      "description": "Whether to include the RimWorld UI (gizmos, tabs, dialogs, overlays drawn in OnGUI). Default true. See the tool description for how this interacts with a region."
    },
    "pixels_per_cell": {
      "type": "integer",
      "description": "Pixels per map cell, only for the no-UI x/z/w/h render (default 24). Auto-reduced (noted in the result) so neither output dimension exceeds 4096px."
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **1**. Explicit error-marker records: **1**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `_paused`, `error`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:1416`.

Observed selector combinations: `{}` (1).

All **4** nested observed paths, type counts and provenance are in `inventory.json` → `tools.screenshot.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## say

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/SayTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/SayTools.cs`) registration line 12 → `Collect = Say` (method line 20). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Say something to the human watching the game: the text appears in an on-screen panel in RimWorld itself. The spectator cannot read your client's window, so this is the only place your own words reach them — use it to explain what you are about to do and why, report how something turned out, and react to events. Plain conversational text, a few sentences at most (longer messages are trimmed); no markdown, no tool names. Requires the 'AI messages (say)' mod setting to be on — when it is off this tool refuses and nothing is shown.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "text": {
      "type": "string",
      "description": "What to show the human watching, in their language when you know it. Up to 2000 characters."
    }
  },
  "required": [
    "text"
  ]
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **2**. Explicit error-marker records: **0**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `chars`, `ok`, `shown`. Example: `campaigns/continuance/reference/legacy/history.jsonl:38`.
- 1 × `object` with keys: `_paused`, `chars`, `note`, `ok`, `shown`. Example: `campaigns/continuance/reference/legacy/history.jsonl:255`.

Observed selector combinations: `{}` (2).

All **6** nested observed paths, type counts and provenance are in `inventory.json` → `tools.say.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.

## help

Source mapping (automatically extracted from decompiled DLL): RimMolt.Tools/HelpTools.cs (archived source path: `evidence/decompiled/RimMolt.Tools/HelpTools.cs`) registration line 13 → `Collect = Help` (method line 25). This maps dispatch, not every runtime response branch. Source-derived literal key assignments and helper call names are navigation leads in the inventory, not complete schemas; dynamic dictionaries, anonymous objects, reflection, and UI callbacks remain branch-dependent.

Discover RimMolt's tools. No args: every tool grouped by category with a one-line summary (cheapest overview — start here when unsure which tool does something). With 'category': that category's tools with their full descriptions. With 'tool': one tool's full description and input schema.

### Declared input schema

```json
{
  "type": "object",
  "properties": {
    "category": {
      "type": "string",
      "description": "Category name from the overview (e.g. orders, map, colonists)"
    },
    "tool": {
      "type": "string",
      "description": "Tool name for full detail (description + input schema)"
    }
  }
}
```

Output schema: **not declared**.

### Observed response evidence

Standalone evidence records: **18**. Explicit error-marker records: **1**.

Root-key variants (counts are evidence records):

- 1 × `object` with keys: `categories`, `combatTip`, `hint`, `ok`, `tip`, `toolCount`. Example: `campaigns/continuance/reference/legacy/history.jsonl:47`.
- 4 × `object` with keys: `category`, `description`, `inputSchema`, `name`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:50`.
- 11 × `object` with keys: `_paused`, `category`, `description`, `inputSchema`, `name`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:264`.
- 1 × `object` with keys: `_paused`, `error`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:317`.
- 1 × `object` with keys: `_dialogOpen`, `_paused`, `category`, `description`, `inputSchema`, `name`, `ok`. Example: `campaigns/continuance/reference/legacy/history.jsonl:598`.

Observed selector combinations: `{}` (18).

All **215** nested observed paths, type counts and provenance are in `inventory.json` → `tools.help.observed.field_paths`. This is observed evidence; field presence does not establish formal requiredness.
