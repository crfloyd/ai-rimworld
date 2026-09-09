# Current tooling handoff

0.7.0 candidate is implemented in an isolated checkout. It exposes rw_observe and rw_guard through persistent-session discovery and the shared CLI engine. One focused player still owns all game calls; historian/coordinator roles are unchanged. No production or game changes have been made by this implementation yet.

197 offline tests passed. Review regressions cover partial bundles, duplicate/nonfinite JSON, threat warnings, composition recovery handles and failed output delivery. Twelve saved paired pawn reads reproduced identical requested queries in one interface exchange instead of two; input-plus-content-text bytes were0.8%larger, wire bytes4.2%larger. These are bytes, not measured model tokens or live speed. A fresh offline discovery agent found both interfaces and produced valid requests without implementation reads; live adoption is untested.

Before integration: complete revision-bound review, obtain the running player's verified pause/clean handoff/release, then deploy and validate a read-only composition against the unchanged game. Do not mix versions mid-run. Guard tests are fake-server only; do not test arbitrary mutations on a live colony. Current rules/data and tactical discoveries remain campaign-local.

See PLAN.md, VALIDATION.md and docs/composition.md. No new monitor, natural-language planner, automatic outcome classifier or time-continuation engine was added.
