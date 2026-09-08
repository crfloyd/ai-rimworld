# Remediation plan — optimize useful decisions and verified play

## Objective

Produce tooling that makes a fresh or returning agent better at legitimate RimWorld play: effective strategy, reliable observation, faster execution, compact working context, and retained learning. The practical objective is verified useful progress per real minute, with honest gameplay and adequate reaction quality as constraints. Raw tick rate, test count and smaller JSON are supporting measures only.

The user's instructions were sufficient to establish this goal. Current failure includes agent prioritization, repeated inspection and development/play mixing as well as interface burden. Do not assign the unexplained timing remainder entirely to the model, host, or MCP.

## Evidence and limits

The frozen a247fef experiment is documented in docs/PLAY-LOOP-EXPERIMENT.md; original evidence and independent audits are run-local. Current workflow A advanced25.69game hours with160MCP calls in20m18s active. Direct-MCP B advanced28.78hours with122calls in19m53s. Ordinary RPCs totaled about2.5seconds in each. B's gameplay response bytes were lower, but actual model context/tokens were not measured. Scenarios differed; both left economic problems unresolved and neither tested combat or compaction recovery.

0.5.0 removes mandatory bulk STATE startup, makes ordinary calls passively journaled rather than tracked goals by default, and corrects blanket critical labels for healing/new effects.180offline tests and a two-hour functional live check pass. Those changes have not earned a speed or win-rate claim. Preserve the direct-MCP baseline as a fallback and comparison, not an inferior workflow to justify replacing.

## Operating discipline, effective immediately

- Separate PLAY and DEVELOPMENT intervals. During measured play freeze production; note nonblocking defects briefly. Change tooling only for a demonstrated blocker, recording the exclusion/intervention. Limit each development increment to one hypothesis and one bounded test.
- One agent owns live control. Other agents may analyze saved evidence or write the history from captured material without issuing game/UI calls. Do not use several agents to micromanage the same colony.
- Choose a small set of concrete colony outcomes, identify the main bottleneck, and finish its dependency chain. Diagnose repeatedly interrupted production instead of reissuing the same order indefinitely. Let stable standing work priorities and queued jobs do ordinary work; verify outcomes at relevant boundaries.
- Preserve current threats, medical/food deadlines, unfinished objectives, temporary settings and their restoration conditions. A high health percentage, receipt, disappearing ID or missing resource row is not proof of recovery/completion/destruction/global absence.
- Capture checkpoint evidence while relevant; draft prose and detailed reports outside the urgent control path. Keep the story factual and interesting, without turning it into a tooling log.

## 1. Locate the real bottleneck before another framework change

Run a short, explicitly timed diagnostic of roughly10ordinary decision cycles, including a menu/order/outcome sequence and a wait. Reuse existing logs wherever possible. Separate host request dispatch/approval, HTTP execution, actual game running when measurable, post-wait collection, model review where available, and documentation/development. Do not count a chained follow-up read as model reaction.

First investigate the connection environment: both A and B used shell-mediated HTTP because no native RimMolt namespace was available. Determine whether a properly configured native MCP connection, or a persistent standard transport, removes repeated shell/approval costs here. Do not silently disable permission controls or restart unrelated work. A transport improvement should not introduce a game strategy layer.

Deliver one short trace and a ranked cost breakdown. Unknown measurements remain unknown; if model tokens or exact unpaused duration are inaccessible, label byte/timing proxies. Timebox initial diagnosis to30minutes. If it does not isolate the cause, identify the one missing measurement needed rather than expanding the instrumentation project.

## 2. Make the ordinary interface as small as direct MCP

Keep normal MCP tool names/arguments and ordinary readable facts. No new command language. Recording requests, responses, timestamps and provenance should be automatic and invisible to routine decisions. Existing ownership and uncertain-operation safeguards should run behind the interface.

Use one concise current handoff as the operational entry point, backed by immutable rules and detailed evidence. It must preserve goals/rationale, current risk, unfinished work/restorations, uncertainties and source pointers without an arbitrary limit that drops important facts. Historical details, the complete API reference and maintenance docs are retrieved only when needed. Remove conflicting current-state instructions and duplicate routes.

Keep three knowledge scopes: current working state; campaign history/lessons; shared general mechanics. Do not leak campaign surprises into new runs. Use existing files/indexes first; merge or delete redundant mechanisms after their replacements are verified. Do not create another knowledge framework.

Routine command receipts should not become permanent unfinished goals. Explicit outcome tracking remains available for real dependencies. Old accepted commands are historical records, not instructions to replay. Review the optional finite monitor for demonstrated benefit; remove or narrow it if it continues to add setup/false stops without useful continuation.

Gate: a fresh operator can begin useful play from the concise handoff without loading a historical backlog or repairing project records. Relevant evidence remains retrievable and unknowns remain visible. Measure actual startup/retrieval work, not file size alone.

## 3. Reduce decisions per unit of useful play

Before advancing, the agent chooses the intended progress, what would require reconsideration, and a defensible horizon. Group already-reviewed actions and required outcome reads into a single host exchange where safe. During an owned wait, use short offline retrieval or conditional planning; never assume predicted progress occurred or make concurrent game calls.

Support bounded continuation for reviewed routine work. Execution may carry out the chosen plan and watch observable conditions; it must not choose a strategy. Pause/return for meaningful deterioration, unfamiliar changes, missing coverage, an uncertain request, a deadline, or the planned outcome. Novel facts remain visible. Do not replace this with a finite event whitelist that can hide new DLC/mod mechanics.

Do not apply the same cadence to safe construction, a fed recovering patient and imminent melee contact. Existing known conditions must not force a fresh full review merely because they persist. Conversely, a fleeing announcement cannot certify a safe withdrawal. Validate routine continuation first; keep close combat directly supervised until its reaction behavior is demonstrated.

Gate: fewer unnecessary model/host handoffs with comparable recognition of material changes. Retain all important facts and the ability to interrupt; do not manufacture throughput by skipping needed decisions.

## 4. Fix only demonstrated MCP gaps

Use the existing full API inventory before declaring an absent capability. Candidate gaps from the trials: exact wait termination reason and elapsed running time; complete current work priorities/bill constraints and useful job/queue interruption information; resource scope/held-item ambiguity and entity transitions; targeted UI actions that enter a picker without an exposed completion path.

Confirm each against actual schemas, player-visible UI and source where appropriate. Extend or fork RimMolt only for a concrete gap the wrapper cannot solve cleanly. Expose ordinary player-visible information/actions, preserve unfamiliar fields, and do not alter balance, simulate outcomes or expose hidden AI strategy. No broad mod rewrite. Prioritize information that explains an actual stalled decision, such as repeatedly interrupted cooking, over optional conveniences.

Gate: reproduce the prior failure, show the agent can resolve it with fewer interactions, and verify equivalent ordinary game behavior. If no benefit is demonstrated, do not retain the extra mechanism by default.

## 5. Acceptance through repeated play and fresh resumes

Use fresh agents with the same settings, clear game permissions and comparable current-state handoffs. Run alternating segments where practical, separating recovery, routine production and combat. No tactical save reloads for experimental matching. Use held-out recorded situations to compare information sufficiency and decision quality under identical evidence; these supplement live play rather than replacing it.

Predeclare each comparison's objective and timing boundary. Measure verified objectives, game progress, unnecessary calls/reads, response volume, decision/host handoffs where observable, missed/delayed risks, and repeat mistakes. Record approval/UI/random-event confounds. Do not infer model tokens from wire bytes or declare one sequential pair a causal result.

Initial performance target: at least2x useful progress per active minute in comparable quiet/recovery segments relative to the direct-MCP baseline, without observed deterioration in decisions or risk recognition. This is a target, not a promised outcome. A change below that target can remain only for a clearly demonstrated reliability/continuity benefit with its cost disclosed.

Fresh-resume test: a new agent must correctly recover the current goal, urgent risks, incomplete work, temporary changes and relevant prior lesson, then make a sound next decision without a full history dump. Test that unrelated campaign discoveries stay isolated. Test meaningful combat decision cases and interrupted-request behavior separately; do not claim those capabilities from routine play.

After each experiment, keep, revise or remove the tested change. Once the loop meets the acceptance criteria, stop architecture work and pursue colony victory, collecting only failures that materially warrant another bounded improvement.

## Next execution sequence

1. Preserve the current paused run and0.5.0 baseline; no further speculative refactor.
2. Perform the connection/end-to-end timing diagnostic above.
3. Select the largest verified avoidable cost and make one small change.
4. Run a fresh-agent segment and a forced fresh-resume test with development frozen.
5. Report outcomes and cost; retain or reject the change. Repeat only for another evidenced bottleneck.

Canonical state: this plan supersedes the older phase checklist as the next-work authority. Prior plans remain in Git and experimental reports; they are not completion claims for the user's goal. Current colony details belong in the selected campaign, not this shared plan.
