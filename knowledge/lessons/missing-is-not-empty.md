# Missing observations must remain unknown

Status: provisional; reviewed 2026-09-08T02:25:26.861584+00:00.
Topics: memory, control

## Applicability

{
  "required_dlc": [],
  "game_version": "Observed in RimWorld 1.6; revalidate behavior for the current game.",
  "mods": "RimMolt and ordinary gameplay; details can vary by version and other enabled mods."
}

## Observed

A large-output guard was reduced to an empty list by a default value.

## Explanation

The caller discarded the distinction between incomplete output and an empty area.

## Recommendation

Check completeness before filtering or counting; narrow or summarize a guarded read.

## Exceptions

A present empty list in a complete response can be valid evidence of absence within that exact scope.

## Verify

Replay the offline large-area fixture and confirm partial status with missing things, not zero objects.

## Evidence

[
  {
    "source": "knowledge/evidence/observed-failures.md",
    "kind": "reviewed observation",
    "scope": "Observation 1; a single deidentified campaign"
  }
]

## Review

Reviewed source account; retain provisional status and avoid universal tactical claims.
