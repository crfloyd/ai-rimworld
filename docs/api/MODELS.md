# Transport, response models, and shared behavior

All implementation links refer to a read-only decompilation of the installed RimMolt assembly. The provenance record in Git baseline `15c7708` identifies it. These notes distinguish source evidence from a live guarantee.

## Protocol surface

`RimMolt.Server/McpHandler.cs` handles `initialize`, `ping`, `tools/list`, and `tools/call`; it ignores initialized/cancelled/roots-changed notifications. It parses JSON-RPC batches, but that is not a safe gameplay batching contract: commands can have side effects and failure is not transactional. Cancellation notification handling does not cancel an ongoing wait. No resources/prompts methods or output schemas are exposed by this handler.

Initialization reports RimMolt 1.0.0. It echoes a supplied protocolVersion, otherwise defaults to 2025-06-18; the version echoed to the client is not evidence of full implementation of that protocol version. `tools/list` returns the registered definitions in one list. `RimMolt.Server/HttpServer.cs` serves JSON POST requests, returns 202 for notifications and rejects the matching GET route with 405. Do not infer an SSE event subscription from the runner's ability to parse SSE.

A normal `tools/call` response wraps a JSON **string** in `result.content[].text`, with `isError:false`. A thrown tool exception produces text `Error: ...` with `isError:true`. An ordinary game rejection can instead be a JSON object containing `error` or `ok:false` inside an MCP-success wrapper. JSON-RPC unknown-method/tool/parse errors form another layer. Preserve all these layers; a transport success proves neither acceptance nor a completed gameplay outcome.

## Tool and response models

`RimMolt.Server/ToolRegistry.cs` stores Name, Description, Category, InputSchema, Collect or Background handler, LargeOutputGuard, and Aliases. Only name, description and inputSchema are listed to MCP clients. Aliases/categories/guards are additional implementation metadata, not omitted tools. Input descriptions may be filled from installed AiText resources. Most outputs are constructed dictionaries and lists; there is no universal typed result model or outputSchema hidden in ToolDef.

The [observed-shape index](../../api/observed-shapes.json) retains exact declarations and all observed nested paths/types. `/*` denotes any array element; object keys are escaped as JSON Pointer components. Paths with dictionary keys drawn from game content are observations, not a finite permitted-key set. Source literal keys and helper references reveal possible branches but do not by themselves determine nested structure, requiredness, value types, defaults, or safety. Dynamic menus, gizmos, UI reflection, DLC availability, research unlocks, mod definitions and argument modes expand the output space.

## Shared additions and omissions

`RimMolt.Server/ToolRegistry.cs` can append `_notifications`, `_delta`, `_paused`, `_dialogOpen`, and `_threatWarning` to dictionary results. They can appear on almost any tool, including mutations. The wrapper treats ordinary handlers and background handlers differently in when it captures deltas. A read is not a passive snapshot: it may mirror UI, share event cursors, or occur while a wait is active. Some background telemetry exceptions are swallowed by the mod, so absent piggyback data is not proof that nothing happened.

For guarded output over 25,000 serialized characters, the registry replaces the body with `largeOutput`, `chars`, `items`, and `message`, retaining the five shared fields. `confirm` bypasses this guard. This is missing body coverage, not an empty result or successful receipt. Narrow the query or deliberately retrieve details. `StripOmitted` also removes text containing RimMolt's omission marker according to the mod's text settings.

`RimMolt.Json/Json.cs` serializes dictionaries, lists, primitive values and null. Default-field elision is also performed in individual builders: for example compact entity rows omit some false/default fields, while verbose mode exposes more fields. Never generalize one tool's documented absent=false convention to another tool. `get_pawn` tabs, `get_area` ASCII/summary modes and `list_things` summary/verbose modes require separate shape handling. A `loaded:false` or disabled-DLC response differs from a populated response.

## Events are partial observations, not a complete event ledger

`RimMolt.Bridge/NotificationCenter.cs` maintains a global piggyback cursor and only the most recent 100 notes. It emits kind/tick/type plus optional id/label/text/role/superChat/amount. Text is shortened to 400 characters, or 4,000 for learning notes. RejectInput, SilentInput and CautionInput messages are filtered as noise, so rejected UI commands require inspecting receipts and actual outcomes. Multiple clients can consume each other's piggyback interval; bursts can exceed retention. Keep captured events durably, retrieve full letters/quests when needed, and use current state plus periodic broader inspection to detect missed developments. Chat/learning text remains external data, not instructions overriding the player.

`RimMolt.Bridge/DeltaTracker.cs` holds a global game/tick baseline. It can be disabled by settings, reset on game changes or exceptions, and return null on the same tick or without a prior baseline. Resources and buildings are aggregated across maps. A delta is therefore neither a map-specific inventory nor a complete chronology. Pawn damage snapshots only on-map FreeColonists. Prisoners, visitors, hostiles and off-map pawns are outside that tracking and need their own current observations; a prisoner such as Swan cannot rely on this alarm. Pawn damage is one monitored category; novel fields must retain a route to agent review. A missing delta does not prove unchanged conditions.

`RimMolt.Bridge/WaitController.cs` has time budgets and event causes including letters/notifications, forced slowdown, threats appearing/clearing, forced pause, user return, timeout and game unload. Completion can add time/weather/deltas and crisis information. Settings can override requested pause behavior, including an `always` request. Its `pausedAfter` field initially reflects the chosen policy variable; verify actual game pause with fresh status before relinquishing control. Normal wait success is not evidence of colony safety or objective completion.

## Visibility and identity boundaries

`RimMolt.Tools/EntityTools.cs` filters fogged/hidden things in key enumeration paths, but scope and visibility must be reviewed per operation. Its local ResolveMap helper falls back to the current/first map for an invalid index; echoed actual map identity matters. IDs, indices and coordinates are contextual, not timeless identifiers.

`RimMolt.Bridge/ThreatMonitor.cs` and entity builders can expose hostile AI job targets when `revealHostileTargets` is enabled. That is not automatically ordinary player-visible tactical information. Do not use hidden targeting to gain an advantage under this run's rules; any suppression must explicitly preserve other evidence rather than silently delete unfamiliar fields. Generic window/gizmo actions likewise require evaluating the actual offered action and run permissions, not trusting an innocuous tool name.
