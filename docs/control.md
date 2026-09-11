# Control and ordinary MCP calls

Only one cooperating agent owns the game endpoint. Read the selected run's rules/current handoff; establish that the previous operator handed off. `controller inspect` is local. Claim with `controller claim --owner NAME --control-available --basis REASON`; retain its token. Connect/discover once, read actual get_status and bind the reviewed identity. Reuse a valid existing session; unfamiliar tool names call for offline capability discovery, not reconnecting.

Ownership prevents cooperating clients from interleaving. It cannot stop unrelated software or a human changing the game. All game reads may pause/change UI. Other agents remain offline while a player owns control. Never infer the authorized save from a colony name alone, and never reinterpret resume as permission to start/load another game.

## Persistent connection

After ownership and binding, run:

```sh
./rw --run NAME session --token TOKEN
```

This accepts ordinary newline-delimited MCP JSON-RPC on stdin/stdout. It keeps the process open, avoiding repeated host shell launches. A native MCP client can use the same stdio interface; in the desktop executor, retain the process session ID and use its stdin tool. Send one request per line and await its matching reply. Do not send precommitted mutations after a wait before reviewing the returned event.

```json
{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"rw_read","arguments":{"tool":"get_status","args":{}}}}
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"rw_wait","arguments":{"maxSeconds":60,"maxGameHours":4}}}
```

`tools/list` serves the small local surface described in [facade](facade.md) with the captured catalog's capture date; the113upstream tools stay reachable by name through `rw_read`/`rw_act` and discoverable through `rw_capabilities`. Refresh via connect/rebind if the server announces a change. Start `session --expose-upstream-tools` to also advertise and accept raw upstream names.

Facade responses are self-contained and compact by default: current game facts, evidence ID, risk cards, optional change metadata and any coverage/control limitation. `rw_read view:full` makes a new live capture; `rw_retrieve` replays an existing observation locally. Under compatibility-only `--expose-upstream-tools`, a raw upstream call keeps its previous shape with a short metadata block. The existing hidden-AI-targeting exclusion remains on both paths. No strategy or automatic continuation runs inside the connection.

`call TOOL --args JSON --token TOKEN` remains available for single calls. Raw requests/results and normalized evidence are automatic. Routine calls need no intention/goal bookkeeping. `act`, explicit `--track` or checks remain for deliberate strategic outcome tracking. These require a meaningful intention and actual outcome proof; a receipt cannot prove arrival, treatment, delivery or construction.

For initial-game UI only, `session --setup` or `call --setup` permits authorized setup actions under a reviewed main-menu binding. After the world loads, inspect and bind the new game identity before ordinary play. This never authorizes debug actions or tactical reloads.

## Host reply collection

For a persistent desktop terminal, an empty stdin poll may consume its entire effective wait window even when output is buffered. Observed requested1second polls took5seconds;10second polls took10seconds. A long empty poll is not a promise of early event delivery.

Collect one outstanding response inside a bounded executor operation using short internal polls, rather than returning every empty poll to the model. Keep host collection bounds separate from the agent's chosen game-time horizon. Collection ends at a parsed complete response with the exact request ID, or a bounded deadline/error. It must never send another game action or replay the request.

For one-shot CLI calls, prefer repeated `--select /json/pointer` options over piping the response through ad hoc Python. Selection happens once after the operation completes; multiple pointers return one object. A missing selector reports `phase:"local_selection"`, `operation_completed:true`, evidence IDs and an explicit no-replay warning, then acknowledges any durable compound delivery normally. Correct the selector, not the completed game call.

If shell capture is unavoidable, parse it once. Never use `echo "$R"` to feed captured JSON: zsh may interpret escaped newlines or tabs and corrupt otherwise valid JSON. Use `printf '%s' "$R"` or `print -r -- "$R"`, and derive every needed value in one parser invocation. A local parser failure after a complete response is not a failed mutation or wait and never authorizes replay.

Carry the real session/request IDs and a partial-line buffer across collection calls. Preserve complete notifications, unrelated replies, media, errors and unknown properties. Check truncation/exit metadata; malformed or clipped output is uncertainty, not an empty result. A substring match for an ID is insufficient: the remainder of the JSON record may not have arrived. If the host cell itself yields, retain and resume that cell instead of starting another collector. On a deadline retain the handle/buffer and continue collecting the same request; follow the normal reconciliation rules for delivery loss.

When presenting executor output, avoid stringifying the entire result around an already serialized stdout string. Emit the original output and a compact handle/exit/truncation envelope, without semantic filtering. Keep large original data retrievable and narrow subsequent queries. The trial's ad-hoc collector was experimental; a reusable implementation still requires focused complete/partial/error/media/truncation tests. This guidance does not certify an untested collector or alter the MCP protocol.

## Composed requests

`rw_observe` and `rw_guard` are advertised by the persistent session alongside upstream tools; see [composition](composition.md). CLI observe/guard use the same engine. Compound requests retain a durable composition marker between subcalls and until output flush. Inspect/reconcile both that marker and any underlying pending request before release or further actions. No manual acknowledgement or automatic continuation is introduced.

## Time and uncertainty

Use the normal wait_for_event arguments. There are no client combat/medical category caps. The agent chooses a finite horizon based on actual risk. maxSeconds must be an integer5–600; pause must be always. Game-time bounds must be finite/nonnegative. Existing typed hard issue deadlines still shorten the tick budget and are reported; a due deadline blocks advancement. The server's crisis cap/force option remains visible and must be used according to actual risk, never automatically.

A wall timeout and a game-time limit can both produce the server's `cause: timeout`; inspect ticksWaited and pausedAfter. HTTP timeout covers the wait plus15seconds but is not cancellation. Only one wait may be active. Retain/poll its actual host handle; use short offline reasoning while it runs, with no concurrent game calls.

The pending-operation file is written before dispatch. Timeout, lost response, process exit, malformed delivery or local persistence failure cannot authorize replay. New calls remain blocked until the original operation is proven terminal and reconciled. `controller handle` can record the real process handle; `controller reconcile` requires original evidence and an explicit server-terminal attestation. A dead PID alone is not proof.

`pause --emergency` is the sole uncertainty exception: ordinary idempotent pause, without clearing the original pending request. Failed/missing pause remains urgent. A session attempts pause on EOF; that is a fallback, not the primary handoff proof. Before closing the connection, request and inspect normal pause/status. A killed process may not run cleanup; the server wait remains finite and its outcome must still be reconciled.

Close a terminal session with EOF (Ctrl-D at an empty input line); a normal MCP client closes stdin. Ownership remains until a confirmed handoff and `controller release --basis ...`. No automatic timeout takeover.

## Outcome and continuity

Inspect current outcome facts when they matter. Keep important unfinished objectives, dependencies, original temporary settings and restoration conditions in the current handoff/issues. Use [memory](memory.md) for optional evidence-linked checks and learning. Untracked commands retain exactly the same identity, ownership, request and pause safeguards.

For unsupported normal UI actions, inspect the actual screen/menu under sole ownership. An action that opens a targeter is not the completed action. Do not guess pixels or use direct simulation calls. Never change saves or balance as a tooling workaround.

The old finite-plan monitor, qualification/acknowledgement workflow and advance command are removed. Their source/evidence history is in Git; live execution history remains in the selected campaign. Use ordinary MCP waits rather than recreating those mechanisms.
