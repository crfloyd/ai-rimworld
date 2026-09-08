# An accepted order needs an observed outcome

Status: provisional; reviewed 2026-09-08T02:25:26.860510+00:00.
Topics: control, combat, medicine

## Applicability

{
  "required_dlc": [],
  "game_version": "Observed in RimWorld 1.6; revalidate behavior for the current game.",
  "mods": "RimMolt and ordinary gameplay; details can vary by version and other enabled mods."
}

## Observed

Order acceptance was followed by an interrupted or ineffective job.

## Explanation

An inference: asynchronous jobs can be displaced or fail after initial acceptance.

## Recommendation

Track consequential orders and verify the intended state change before relying on it.

## Exceptions

Some immediate configuration tools return the changed state directly; avoid unnecessary extra polls.

## Verify

Use new job/position/health/equipment evidence or an explicit completion predicate.

## Evidence

[
  {
    "source": "knowledge/evidence/observed-failures.md",
    "kind": "reviewed observation",
    "scope": "Observation 2; a single deidentified campaign"
  }
]

## Review

Reviewed source account; retain provisional status and avoid universal tactical claims.
