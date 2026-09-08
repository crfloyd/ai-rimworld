# Approved setup profiles

A profile contains reusable preferences the player explicitly asks to save or use. The repository ships no selected default profile and no inherited run configuration.

The agent can save an approved profile here as JSON with its settings, approval basis and date. It must contain no live session token, pawn ID, map coordinates, game binding, or copied campaign history. Save references identifying a particular colony belong to that campaign instead.

When the player names a profile, read it and resolve its preferences against the current request. Explicit new instructions override profile values. Record the profile path and version/date plus any overrides in the new run's intake. Create a complete independent campaign specification; do not pass a profile of an undocumented shape directly to new.

A run keeps the selected settings as its own snapshot. Updating a shared profile never changes an existing run. Do not silently use a profile called default, the most recent run's settings, or a previously approved unrelated setup. Discuss a reusable default only when the player wants that behavior.
