# Coordinated play

Use one focused player for live control, a coordinator for user interaction/project work, and a historian for requested reports. Use observers or strategists only for a concrete bounded question or demonstrated review need. More agents are not an automatic improvement: the five-day test showed faster focused play but no established added outcome benefit from three observer advisories.

## Ownership

| Role | Owns | Reads/receives | Boundary |
|---|---|---|---|
| Coordinator | User scope, role dispatch, shared tooling docs, Git integration | Current handoff, sparse player progress, specialist results | No live game calls while a player owns control; no campaign-state edits during that player's turn |
| Player | Every game/MCP/UI call; current STRATEGY and issue updates | Run rules/current state; exact API contracts and relevant lessons on demand | Makes immediate tactical judgments; does not wait for advisory approval |
| Historian | History.md, reports, checkpoint publication, screenshot registration/review | Completed period evidence, original images, prior chapter for continuity | No game/UI calls; no current strategy/issue rewrites; never invent missing events/images |
| Adviser | Bounded analysis and concise recommendations | Already-recorded evidence and relevant reference material | No game calls, authority edits or routine all-clear messages |

Automatic request/evidence journaling continues normally. Use existing CLI operations and locks for records; do not manually rewrite journals or derived views. Assign one writer to each authority. The coordinator may repair state after explicit player release; never silently supersede an active player's plan.

## Dispatch and user steering

Use a fresh-context subagent when supported, without a model/effort override unless explicitly requested. Supply only the selected run/path, user objective and stopping conditions, authoritative current file pointers, original gameplay permissions/rules, control release state, and relevant uncertainties. The player reads AGENTS.md and its required run/control/API entry points; it does not need this entire coordination guide or maintenance history.

For a new game, the coordinator routes the user's supplied setup choices through startup.md without inventing a current-state handoff or loading another run. A new campaign must not inherit another campaign's discoveries. For an existing game, do not read a stored handoff as proof that its control or mutable facts are still current.

Retain the current responsive player across checkpoints and questions. The coordinator answers status questions from saved progress without stopping play and promptly forwards actual user steering as USER DIRECTION, distinct from adviser suggestions. A user stop/pause request takes priority: contact the player immediately, confirm actual pause and resolve any pending operation through control.md. Never leave a live owner running after the coordinator ends an explicitly stopped task. When coordinating ongoing play, retain/wait on the player task rather than ending the turn while claiming continued background work.

Replace a player only for a real need such as measured response stalls, continuity failure or a completed bounded segment. Transfer only after verified pause, terminal pending requests, updated STRATEGY/ISSUES, saved handoff, connection closure and explicit release. Preserve the actual process/request handles if a problem prevents release. The incoming player revalidates identity and outcomes; no timeout-based takeover.

### Minimal player task

> You are the sole next player for RUN in REPOSITORY. Continue USER OBJECTIVE until USER STOP CONDITION. Follow the user's rules and normal gameplay only. Read AGENTS.md, this run's CAMPAIGN/STRATEGY/ISSUES and small resume handoff, then docs/control.md and docs/api/README.md. CONTROL RELEASE EVIDENCE is the prior operator's handoff, not live proof. Claim/revalidate before acting. Use one persistent connection and discover local composed reads (`rw_observe`) when related facts are needed together; individual tools remain available. Guarded actions require an already-chosen sufficient rule. Use reviewed commands and finite event-driven waits. You own current strategy/issues and immediate decisions. Do not perform tooling development or assemble reports during play. At requested checkpoints capture original images and send the historian evidence/outcomes/next aims. Preserve unknowns, role/dependency knowledge and restoration duties. On completion or transfer verify pause, close, save current state/handoff, release and report exact endpoint evidence. Do not stop merely because the colony is stable.

## Reporting without blocking play

Reuse a historian at the requested in-game checkpoints; do not have it poll continuously for work. The player sends a small checkpoint message: period/actual tick, significant events and losses, verified accomplishments, unresolved risks, next-period/year aims when requested, and exact evidence/image paths with capture ticks. If a crisis prevents a capture, preserve the facts and date a later image honestly.

The historian retrieves missing detail from saved records, registers and visually reviews originals, writes interesting factual prose and the separate operational report, and publishes with the existing checkpoint command. It checks claims, image dates and evidence itself and reports the finished paths plus unresolved factual questions. The coordinator reviews material uncertainty or errors; it does not routinely take over drafting or formatting. The player continues independently unless the historian identifies an urgent overlooked game risk.

### Minimal historian task

> You are the historian for RUN/PERIOD in REPOSITORY. No RimMolt calls or live game UI actions, and no current strategy/issue edits. Local image viewing and existing record operations are allowed. Read docs/history.md and the player's checkpoint message; retrieve only relevant saved evidence and the prior chapter. Own the complete narrative, operational report, original screenshot registration/visual review and checkpoint publication. Preserve actual dates, losses and uncertainty; do not write a tool log or invent dialogue/images/outcomes. Ask the player only for consequential missing facts or a safe future capture, without blocking routine play. Return finished file paths and any remaining limitations.

## Advisers and measurement

An adviser receives a bounded question and current evidence pointers. It may identify an overlooked dependency, compare a prospective construction/expedition plan, or retrieve a precise mechanic/API contract. It sends advice only when actionable: finding, evidence/capture tick, recommendation, applicability and missing information. It cannot see unqueried facts. The player decides whether the advice still fits; no acknowledgement ritual is required.

Track useful decisions/outcomes, output-to-next-call latency, response-ready-to-delivery delay where available, context growth/truncations and extra reads caused by advice. Separate gameplay, reporting and development intervals. Do not attribute speed to context, effort or multiple agents merely because a later segment is faster. Keep shared mechanics generic; current facts, tactical discoveries and user permissions stay in their campaign.
