# Illustrated history

The historian owns the complete reporting workflow under [agent-flow](agent-flow.md); only the player captures live scenes. Keep two outputs: an operational report and the colony's narrative book. Both derive from real evidence. Neither raw tool logs nor plans are completed game events. Reporting proceeds from saved evidence while the player continues; no game calls from the historian.

## Capture

The player captures important transient scenes when safe, even between checkpoints, and hands the original paths, evidence IDs and actual ticks to the historian. Prefer the ordinary MCP screenshot tool when enabled: explicit map bounds frame the subject, include_ui=false leaves the real camera alone, and include_ui=true moves it. Preserve the original returned PNG. Enablement must follow the user's authorization; a disabled tool is not a captured image. Before taking a shot, use normal game controls to frame the relevant people, structures, landscape or battlefield. Never expose a pawn or prolong a crisis for a photograph.

On macOS, shot windows dynamically lists current RimWorld windows using the system window inventory. With a current window ID:

```sh
python3 rw --campaign NAME shot capture --window CURRENT_ID --tick GAME_TICK --subject 'Subject' --caption 'What is actually visible' --framing 'Explain the framing' --evidence OBS_OR_EVENT_ID --map-index ACTUAL_MAP_INDEX
```

Alternatively import an original PNG with shot add --file PATH and the same metadata. The bytes are copied unchanged and hashed. The PNG header is checked; visual truth and readability still require inspection with the host's image tool.

After actually viewing the image, run shot review --id SHOT_ID --note 'Describe what is legible and how it supports the chapter'. Changed bytes invalidate that review. Capture methods depend on host screen permissions; do not claim capture success without a returned file and visual inspection.

## Checkpoint

checkpoint without a file reports the next checkpoint based on observed/derived game time. The default is every five in-game days. A crisis can delay writing; record the real capture and publication context. Do not backdate a later image as an earlier event.

Write a chapter file and a checkpoint JSON using templates/checkpoint.json. Use the returned relative screenshot paths in the chapter for portability. Renderers that require absolute paths can receive absolute links in chat; preserve portable links in the book when practical.

The checkpoint command checks cited IDs, available game time, reviewed screenshot hashes, image links, and required report fields. It commits the report and book with a stable checkpoint marker so retrying after a local write interruption does not duplicate the chapter. If screenshots were missed, explicitly supply missed_screenshots instead of creating documentary replacements.

## Voice

Write connected prose about people, places, pressure, choices, reversals and consequences. Explain enough that someone who never watched can follow the colony. Include mistakes candidly. Separate uncertainty from fact, and anticipated outcomes from achievements. Do not invent dialogue, feelings, relationships, causal explanations or imagery.

Technical troubleshooting, scheduling, tool checks and next-chapter promises belong in working notes. The operational report separately includes accomplishments, losses/current risks, next five-day goals and the one-year aim. Simple phrase warnings help review; they do not establish narrative quality. The author must read the chapter before publishing it.

## Run association and image integrity

Use shot add/capture with --evidence OBS_OR_EVENT_ID (one or more) and --map-index when known. Original captures record run/session, source capture time when available, association evidence, dimensions and a byte hash. Import time is not presented as an independently known original capture time. Actual visual review must confirm both legibility/framing and that the image illustrates this run's claimed event.

Every inline image in a chapter must be a declared, reviewed, unchanged original inside this run; external paths and undeclared images are rejected. Use inline Markdown image links, not reference-style or HTML images, so all documentary images are validated. Legacy captures lacking run association require explicit reimport of the unchanged original with evidence. These metadata checks support provenance; they do not replace looking at the actual image or establish that a model's caption is true.
