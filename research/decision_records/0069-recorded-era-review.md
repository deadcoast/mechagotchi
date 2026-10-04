# DR 0069: expose recorded eras without changing campaign continuation

Date: 2026-10-04. Status: locally complete. Full run
`20261004T181855-269f5dbc` passed 2,548 tests / 24 suites, two documented skips,
2,279 JSON artifacts and no source mutations; native/source observations and
expanded navigation checks passed. Native keyboard runtime remains unavailable.

DR 0021's Review/Collect loop lacked a persistent player surface for stored
outcomes and unlock reasons. A resumed campaign deliberately has no current-run
eras in memory: its offset and founder pool govern the next era. Hydrating that
list for display would risk changing seeds and evolution inputs.

Read the public DR 0022 campaign history through a read-only SQLite connection
instead. T opens the latest recorded report and pauses companion care; browse
eras and wrapped pages without creating files, training or advancing the soup.
Show stored metrics at their recorded precision, exact earned values/thresholds,
weather provenance and founder verdicts. Filter inherited unlocks by campaign
identity as well as era index. Missing/corrupt data must be explicit.

C returns to the current covenant; interactive E opens the newly completed era.
Keep bounded launch behavior, S2 save retry/discard, incumbent policy and all
scientific gates. Historical replay/archive rendering remains separate scope.

Evidence: `research/experiment_reports/2026-10-04-era-review.md`,
`game/tests/test_era_review.py`, `labs/game_loop/verify_era_review.py`, and the
separate `data/game_client/era_review_release_stage*.json` observations.
