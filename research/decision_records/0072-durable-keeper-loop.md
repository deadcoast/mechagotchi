# DR 0072: preserve Keeper decisions through era completion

Date: 2026-10-04. Status: locally complete; full run
`20261004T202052-aaa63dd1` passed 2,590 tests / 24 suites, two documented
skips and 2,286 valid JSON artifacts without source mutations. Contract: `docs/development/cycle-30-durable-era-plan.md`.
Sources: DR 0021's connected session, DR 0022 persistence, F7 budget invariants,
F9 contributions and F17 campaign resume. No engine mechanic is added.

Actual T3 save/restart lost a staged cared-for genome and storm selection.
Successful covenant changes also reached disk only with a later era. Persist
explicit weather/contribution choices atomically; stage exact grids in order,
deduplicate exact repeats, refuse conflicting identities and malformed genomes
through the existing authority, and let Backspace unstage copies. Era admission
still judges compatibility; it is never inferred from staging or forced by a
changed covenant. Persist accepted covenant changes immediately. Store known
base_parameters so newly written states preserve F7's non-compounding budget;
old states without them retain their existing load interpretation.

E computes from a copy using unchanged engine calls. Before committing, save the
actual completed era and exact campaign state in a checksummed journal. Finish
ledger, state and staged-input consumption idempotently. Retry/restart completes
that output without another evolve call. Guard conflicting external state/history
and corrupt preparation; do not silently replace them. No service or scheduler.

Use the existing care/report/covenant casing for preparation and show exact
admitted founder IDs beside existing engine refusals. Preserve read-only history,
archive/adoption, post-era replay labels, companion checkpoints and policy choice.
Keep report outcomes/niches/QD on page one and hide disabled preparation prompts
during completion recovery. No extra panel or speculative feature list.

Evidence: `research/experiment_reports/2026-10-04-keeper-loop.md`,
`game/tests/test_era_plan.py`, `labs/game_loop/verify_keeper_loop.py`,
`data/game_client/keeper_loop_review_stage0.json`, and separate
`keeper_loop_release_stage0.json` / `keeper_loop_release_stage1.json`.
Fourteen targeted checks and 25 native/source observations pass. Exact full
closure, native keyboard limits and publication boundaries remain in the report.
