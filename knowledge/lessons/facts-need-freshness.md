# Timestamped facts must survive a context handoff

Status: provisional; reviewed 2026-09-08T02:25:26.864247+00:00.
Topics: memory

## Applicability

{
  "required_dlc": [],
  "game_version": "Observed in RimWorld 1.6; revalidate behavior for the current game.",
  "mods": "RimMolt and ordinary gameplay; details can vary by version and other enabled mods."
}

## Observed

The state note lagged behind newer action and medical records.

## Explanation

Independent manual copies of changing facts diverged.

## Recommendation

Generate current fact views from evidence, preserve rationale separately, and revalidate on resume.

## Exceptions

Stable historical details need less frequent refresh than active combat or treatment state.

## Verify

Resume from an empty context and check gear, health, game time and unfinished actions against the newest evidence.

## Evidence

[
  {
    "source": "knowledge/evidence/observed-failures.md",
    "kind": "reviewed observation",
    "scope": "Observation 4; a single deidentified campaign"
  }
]

## Review

Reviewed source account; retain provisional status and avoid universal tactical claims.
