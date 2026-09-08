# Reviewed interface and continuity observations

These are provisional API/agent workflow observations, not tactical foreknowledge for a fresh colony. Original development provenance remains in Git; campaign encounter details belong in that campaign.

1. A large-output response omitted the normal things field. Defaulting that missing field to an empty list produced a false empty-map conclusion; a separate summary confirmed objects remained.
2. executed=true acknowledged an order without proving its eventual outcome. Later job/state reads were necessary.
3. Encounter-specific tactical learning is retained in the originating run, outside shared defaults.
4. An old state file lagged newer evidence. Source timing, unfinished work and retrieval pointers must survive handoff.
5. A recorded recurring problem remained unresolved despite being mentioned repeatedly. Tracking must include the next action and a resolution criterion.
6. A stock count alone did not establish production status; inputs, work and consumption required observation.

These observations support workflow precautions, not optimal game strategies. Tests validate the interface contract, not game outcomes.
