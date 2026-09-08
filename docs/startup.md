# Starting and resuming a named run

Read this at the start of a play session, when choosing a different run, or when recovering an unfinished setup. Routine play uses the selected run's memory and the topic playbooks instead. This guide is the startup workflow; no separately installed skill is required.

## Workspace topology

Open the persistent ai-rimworld base directory as the project. A named run is a campaign directory. Keep the existing campaigns/ name; do not introduce a second runs/ tree or copy the runner into each campaign.

| Location relative to the base | Purpose and write scope |
| --- | --- |
| AGENTS.md, docs/, tools/, tests/, templates/ | Shared instructions and runner. New-run initialization does not overwrite them. |
| knowledge/ | Explicitly reviewed shared advice. New runs pin an adoption; run lessons are never written here by default. |
| profiles/ | Explicitly approved reusable setup preferences. No profile is selected automatically. |
| campaigns/NAME/ | This run's rules, facts, strategy, issues, events, actions, story and screenshots. |
| campaigns/NAME/reference/intake/ | The original player brief and relevant setup answers, if saved separately. |
| .runtime/intakes/UNIQUE_NAME/ | Optional persistent drafts while questions are unanswered; never another run's memory. |
| .runtime/ | Local control coordination. Run selection does not grant game ownership. |

All gameplay records belong to the selected campaign. A new name creates a new identity; it does not inherit pawn IDs, geometry, a previous victory route, or a live binding. Existing run directories cannot be initialized again. Do not manually delete one to reuse its name. There is no global active-run pointer that another session can silently change.

RimWorld manages actual game saves. Record the observed save label and identifying evidence in this run's reference files when available; the folder name is not proof of which save is loaded. Multiple record directories still share one game endpoint unless separately configured. Only its current owner controls it.

## Route the player's request before doing setup

- **Start a new run:** extract the provided preferences, resolve meaningful gaps below, choose or obtain a unique name, then create new local records. No separate confirmation is needed for an already explicit new-run request.
- **Resume a named run:** use its existing records. Read the rules, current strategy and open issues; full STATE/history are optional retrieval indexes, not mandatory preload; do not repeat its setup interview, initialize it again, or copy its facts into a new campaign. A recorded mode=fresh describes its original creation, not an instruction to start over on every session.
- **Continue without a name:** use an unambiguous run already selected in this conversation. Otherwise list the local runs and ask which one; recency alone is not authority to control a game.
- **Unclear new versus resume:** ask this one routing question first. Do not interview for a new game while the player may mean an existing colony.
- **Read a history or discuss strategy:** use saved records. Do not acquire game control just to answer.

If the named run is missing or damaged, surface that specific problem. Never turn a failed resume into a fresh start. If a new name already exists, preserve it and choose a distinct name when naming was delegated; otherwise resolve the name collision with the player.

## Ask for intent, then let the agent plan

First extract answers from the current prompt and applicable earlier answers in this conversation. A detailed prompt is a completed part of the interview. Do not make the player repeat it in a form. Later corrections supersede earlier preferences; record a change that affects an existing run's rules.

An explicitly selected approved profile can fill gaps. Explicit current instructions override it. Other runs and an unselected profile cannot supply permissions or defaults. See [profiles](../profiles/README.md).

For a vague request such as “I want to start a new run,” ask a small first round, usually two or three questions covering the most consequential choices. The following are question examples, not a mandatory script to recite unchanged:

1. “What kind of start and challenge would you enjoy—any scenario, storyteller or difficulty in mind, or should I choose some of those?”
2. “Any expansion, colony theme or play style to focus on? Should I pursue a particular ending, choose a legitimate victory route, or work toward another goal?”
3. “What rules should govern saves and recovery, starting-pawn customization, and how independently I play? Any other restrictions you want?”

Adapt the wording to what is missing. If difficulty is already specified, remove it from the question. If only reload rules are missing, ask only about them. Offer a few understandable choices when useful, allow a free-text answer, and accept “you choose” for ordinary setup and strategy choices. Avoid presenting every possible RimWorld setting as a questionnaire.

A broad first answer may still need one focused follow-up. Do not treat silence as an answer or as permission for a consequential choice. Continue harmless local preparation while an answer is pending, but defer dependent game setup.

## What needs to be settled

| Topic | What to extract or clarify |
| --- | --- |
| Objective and ending | Legitimate credits, a specific ending, a custom milestone, roleplay, or an open-ended colony. Distinguish a preference from a mandatory win condition. For an open-ended run, establish how the player wants control handed back. |
| Challenge and start | Scenario, storyteller, difficulty and save mode, or clear delegation to choose them. Do not silently inherit the last run's harshness or change difficulty modifiers. |
| DLC and theme | What should feature prominently, what is optional, and what is prohibited. “Focus on Odyssey” does not itself mean disable other DLC or mandate its ending. |
| Consequences | Reload/save-scumming rules, whether terminal-failure recovery is allowed, and any conditions. Commitment Mode and a recovery exception are separate choices. No tactical reloads or developer/debug actions by default; never silently grant a disaster-recovery exception. |
| Starting advantage | Random pawns, normal rerolls, balanced Prepare Carefully, or other expressly permitted customization; point limits and resource/equipment constraints when applicable. |
| Autonomy and boundaries | Whether the agent chooses strategy and recruitment independently, or the player wants involvement at named milestones. Resolve roleplay constraints, prohibited tactics and any real-time stopping limit the player raises. |
| Reporting | Five in-game-day reports and an illustrated prose history are the workspace default. Briefly disclose this; do not block startup on screenshot counts or writing style unless the player has a preference. |
| Name and world details | Use a provided name and seed/biome/map restrictions. Otherwise choose a sensible unique name and reasonable world details within the delegated scope. Cosmetic details do not require a separate interview. |

Do not ask for tactical decisions such as a starting build order merely to complete intake. Those belong to the playing agent when strategy is delegated. More questions are appropriate when the answer materially changes what counts as success or what actions are allowed.

If the player says “choose everything and do not ask questions,” choose and record ordinary settings under that delegation, disclose the resulting setup briefly, and proceed within the workspace's honest-play defaults. This does not authorize overwriting another run, modifying game balance, or inventing permissions for a blocked external action.

## Preserve answers without confusing requests and observations

Use [campaign.json](../templates/campaign.json) as the final specification. It starts with unresolved gameplay preferences rather than one experiment's settings. Fill objective, rules and setup from the player's answers or explicit delegation. Keep sources in intake.field_sources: a short note identifying a prompt, an answer, a chosen profile, delegation, or a disclosed workspace default. No full conversation needs to be loaded during every play loop.

Store the relevant original brief and answers in this run's reference/intake/ when they warrant more detail. An unfinished interview can use its own .runtime/intakes/ draft until initialization. Copy the accepted draft into the new run after it is created; never overwrite the shared template to record one player's answers.

intake.unresolved_questions records pending player decisions. intake.technical_checks_pending records facts the agent must inspect, such as available DLC, mod support, the starting menu and a correct live game identity. These are different: a desired DLC focus is a player preference, while what is installed is an observation. Empty inventory arrays in an unverified environment are not evidence that no DLC/mods exist.

The agent must review the specification semantically. The new command rejects explicitly recorded unanswered questions, but it does not understand arbitrary prose or guarantee that omitted preferences have been answered. Do not clear an unanswered question simply to pass a check.

Once meaningful gaps are resolved, give a short statement of the agreed setup and proceed. Do not add a blanket “confirm all of this” gate. Record an authorized setup fallback before needing it when the player has supplied one. If a required feature proves unavailable and no compatible fallback is authorized, ask about that concrete conflict, preserving all other answers.

## Local commands and the transition to play

From the base directory:

```sh
pyenv exec python rw runs
pyenv exec python rw new ember-coast --spec /absolute/path/agreed-campaign.json
pyenv exec python rw resume ember-coast
pyenv exec python rw --run ember-coast brief
```

runs (also list) reads small local metadata and summary files, not every colony's history. It shows last recorded time, evidence origin and outstanding counts when available. Missing or damaged records remain visible as unknown or errors. The listing is not live game state, and it never infers victory from a large day count.

new creates records only and requires a fresh specification. init remains the lower-level bootstrap for documented imports and fixtures. resume returns the selected directory, evidence summary and required reading paths; it writes nothing and does not load a save or unpause. --run and --campaign select the same directory. Keep that name explicit on subsequent commands.

On fresh starts and resumed/compacted context, read the small [API index](api/README.md) and retrieve individual capabilities on demand. Do not preload the complete manual. Before game interaction, follow [control.md](control.md): establish a real handoff, inspect the installed capabilities and game, and bind the authorized identity. Preserve any other current colony through normal controls before a permitted switch. Never contact a running player's game merely to discover settings for an intake interview.

For a resumed run, read its immutable handoff and changed-since-snapshot markers. Retrieve the captured strategy/lesson versions when needed, then verify pending orders and urgent risks before adding work. For a fresh run, perform and verify setup through ordinary UI/MCP actions, record what was actually applied, and then enter the play loop. Permission for a preferred theme is not permission to install, enable/disable, or edit mods unexpectedly. Ask about a material unavailable feature only when current authorization cannot resolve it.

After setup, obey the recorded autonomy: make gameplay decisions, maintain memory and checkpoints, and ask again only for a new user-dependent constraint, contradiction, or genuine blocker. Do not repeatedly renegotiate the same settings or ask for strategic approval during an autonomous run.

## Examples of correct routing

- “New run: Crashlanded, Randy, Losing is Fun, Commitment; standard resources, exactly three balanced customized pawns, all installed DLC allowed, choose the ending, no reloads, play autonomously.” Extract those answers and proceed. Choose the name/world details within scope; do not ask difficulty, ending, or recovery again.
- “Start a new run, maybe something with Odyssey.” Ask about challenge, whether the Odyssey interest is a preference or a required goal when necessary, and consequences/autonomy. Do not infer a mandatory ending or a mod change.
- “Resume Ember Coast.” Locate ember-coast and read its memory. Revalidate game identity and current risks; do not ask a fresh setup questionnaire.
- “Use my standard profile, but make this run peaceful.” Apply the explicitly chosen profile and the override. Resolve only a material conflict, such as a combat-only mandatory objective that the changed rules cannot support.
- “Start new and choose everything.” Record delegated choices and honest-play defaults, then continue without a preference interview. Do not reuse an old campaign directory.

## Memory after initialization

New records, learned lessons, candidates, incidents, decisions, outcomes, observations, screenshots and history belong under campaigns/NAME/. Run-local learning lives in knowledge/lessons/; the initially adopted shared baseline is copied under knowledge/adoptions/. Shared changes do not update an existing run until explicitly reviewed and adopted. Set learning.shared_baseline to none in the specification to begin without shared guidance.

Use ordinary focused live calls for routine play and packet/context only when deeper retrieval is needed; keep full evidence in raw/ and the journals. Save an immutable handoff before compaction or stopping. Resume returns its next action, rationale and uncertainty, plus markers for later local changes. A resumed live connection must rebind identity; reconcile previous-session action outcomes explicitly. Never replay orders or reinterpret a stored handoff as proof of current safety. The finite continuation workflow is in [runner-loop.md](runner-loop.md); qualify it against the actual session before use.
