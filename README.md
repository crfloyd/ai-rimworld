# AI RimWorld

A small Python support system for agents playing RimWorld: explicit game control, trustworthy observations, compact campaign memory, action verification, reusable lessons, and an illustrated history.

Requires Python 3.10+ on macOS or Linux. No third-party Python packages are required. Automatic screenshot window discovery/capture currently supports macOS; agents can import original game/OS PNGs on other systems. The game, RimMolt, and computer-control tools are provided by the host environment.

## Open this folder and name the run

Open this persistent base folder as the project for play sessions. The root AGENTS.md routes the agent to the [startup guide](docs/startup.md); a separately installed skill is not needed. Each run has its own directory under campaigns/. Shared tools, templates and reviewed knowledge remain at the base.

You can say:

> I want to start a new run.

The agent extracts preferences already supplied, then asks a few relevant questions about challenge, DLC/theme and goals, and rules such as reloads and autonomy. A detailed prompt fills those answers directly. “You choose” delegates ordinary settings. Once meaningful gaps are resolved, the agent records the agreed setup and proceeds without another blanket confirmation.

> Start a new run called Ember Coast with [my setup and rules].

> Resume Ember Coast.

Resume reads that run's rules, current memory, strategy and unfinished work before verifying the real game. It does not repeat the new-run interview. If new versus resume, or the intended existing run, is ambiguous, the agent asks about that ambiguity. It never silently selects the most recent colony.

## Local run commands

```sh
python3 rw runs
python3 rw new ember-coast --spec /absolute/path/agreed-campaign.json
python3 rw resume ember-coast
python3 rw --run ember-coast brief
python3 rw --run ember-coast context control
```

The agent prepares the specification from [templates/campaign.json](templates/campaign.json), recording the player's answers, delegation and sources. The player does not need to author JSON. See [approved profiles](profiles/README.md) for explicitly reusable preferences.

new creates campaigns/ember-coast/ with a new identity, rules, STATE.md, STRATEGY.md, ISSUES.md, action/event/observation records, History.md, raw evidence, reports and screenshots. It refuses an existing directory and explicitly recorded unanswered questions. It neither launches RimWorld nor starts/loads a save. init remains available as a lower-level record bootstrap. --run and --campaign are equivalent selectors; runs and list are equivalent listings.

runs reads compact metadata without loading every run's logs. resume is also read-only: it returns the latest immutable handoff packet, changes since that snapshot, the named directory and required reading paths. If there is no snapshot, that gap stays explicit. Neither creates a global active-run setting nor touches the game. Unknown time, unavailable summaries and damaged records remain visible. Current-state summaries are cached evidence, not proof that a game is paused or safe.

Game menus, Prepare Carefully and scenario selection still use the actual available MCP/UI capabilities after control is established. If setup fails, use an already authorized fallback or resolve the concrete conflict. Do not silently change the run's rules.

## Connect only at a game-control handoff

Read [docs/control.md](docs/control.md). These commands affect the live connection, and game inspection may pause the game. Do not run them while another task is playing.

```sh
python3 rw --campaign ember-coast controller claim --owner main-agent --control-available --basis 'Describe the actual verified handoff'
python3 rw --campaign ember-coast connect --token OWNER_TOKEN
python3 rw --campaign ember-coast call get_status --token OWNER_TOKEN
```

Use the returned live observation ID and actual identifying fields to bind the authorized game:

```sh
python3 rw --campaign ember-coast bind --token OWNER_TOKEN --observation OBS_ID --expected '{"loaded":true,"colonyName":"ACTUAL_NAME"}' --basis 'Describe how this game was identified beyond its name'
```

For an authorized fresh run at the main menu, bind `{"loaded":false}`. Classify unfamiliar setup tools after reading their live schemas, and use `--setup` for setup mutations. Re-inspect and rebind after the colony loads. If setup fails, use only a user-authorized fallback.

The token and session files are local coordination records, not credentials to bypass permission systems. Tokens, campaign records, and captures are excluded from git by default. Back up campaigns separately if desired; the game manages its own saves.

## Routine play

Start with `packet --topic TOPIC`. Use `observe --queries JSON` for a bounded group of live reads and `act --json JSON` for a reviewed order with an outcome contract. Once actual pause/wait behavior is qualified, a finite `plan` and `continue` loop can handle expected routine progress without a model round trip after every quiet wait. See [the complete loop contract](docs/runner-loop.md) before enabling it. Combat and unstable medicine remain supervised.


```sh
python3 rw --campaign ember-coast call get_pawn --args '{"id":"ACTUAL_PAWN_ID","tab":"health","detail":true}' --token OWNER_TOKEN
python3 rw --campaign ember-coast context medicine --entity ACTUAL_PAWN_ID
python3 rw --campaign ember-coast retrieve --observation OBS_ID
python3 rw --campaign ember-coast advance --token OWNER_TOKEN --hours 1 --risk medical --intent 'Continue recovery' --review 'Record current bleeding, tend status, threats and next deadline'
python3 rw --campaign ember-coast brief
```

Read `rw --help` and each command's `--help` for arguments. Offline commands such as brief/context/retrieve/issue/lesson/metrics never query the game. Important mutations should use `--family treatment|extinguishing|rescue|movement|equipment|construction|combat`. See the [action workflow](docs/control.md#actions-and-verification) for explicit verification predicates and manual evidence review. Low-impact general mutations retain request evidence without filling the long-lived action list.

`batch --file` serializes a bounded JSON list of tool calls and stops on incomplete results, changed identity, or new events. Dependencies can name already-completed action IDs. Do not use a batch to assume that a just-accepted order has finished. Waits use supervised `advance` or qualified finite `continue`. Critical alerts and every bundle child are inspected; exact acknowledged risks do not automatically stop an otherwise valid batch.

## Learn and report

`--run NAME lesson` always writes under that run's `knowledge/`. Shared guidance is a pinned adoption, not another run's changing memory. Shared promotion requires a separate generalized draft and explicit review. `decide`, `outcome`, `incident` and `lesson-review` link experience to learning; see [memory](docs/memory.md).

Before ending or compacting a play session, save `handoff --reason ... --next ... --uncertainties ...`. It preserves immutable rules, strategy, evidence references, pending work, lessons and control uncertainty. It never loads a save or proves live freshness.


```sh
python3 rw --campaign ember-coast issue --file /absolute/path/issue.json
python3 rw --run ember-coast lesson --file /absolute/path/lesson.json --review 'Explain the evidence and scope'
python3 rw --campaign ember-coast checkpoint
python3 rw shot windows
```

See [memory.md](docs/memory.md) for retrieval and learning, [history.md](docs/history.md) for screenshots and publication, and [templates](templates) for complete examples. Chapters are authored by the agent from evidence; no generated prose is treated as an observed game event.

## Validate without a game

```sh
python3 -B tools/check.py
python3 -B tools/demo.py --output /tmp/rimworld-support-demo
```

The demo is an explicitly synthetic campaign in a new output directory. It demonstrates fresh startup, interrupted orders, uncertainty, issues, selective retrieval, and reports without contacting a server. Do not point it at an existing campaign.

The implementation and validation status is in [VALIDATION.md](VALIDATION.md). The original [PLAN.md](PLAN.md) is historical; [TODO.md](TODO.md) records the approved audit fixes and remaining field checks. [docs/AUDIT.md](docs/AUDIT.md) preserves the failures that motivated them.

The complete captured [RimMolt API review](docs/api/README.md) covers all 113 tools, input declarations, observed response shapes and source handlers. Use its index selectively; it also records unresolved runner information-loss findings.
