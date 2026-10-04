# DR 0071: reopen indexed post-era recordings without reconstructing history

Date: 2026-10-04. Status: locally complete and reviewed. Full
`20261004T192757-866fdf0f` passed 2,576 tests / 24 suites, two documented
skips and 2,283 JSON artifacts, with no source mutations.
Contract: `docs/development/cycle-30-saved-replays.md`. Sources: DR 0021 Review,
DR 0022 pointer/hash persistence and DR 0023 recorded engine frames.

Replace the client V current-run guard with a read-only saved replay consumer.
Use the existing public query, normalized-text SHA convention, exact selected
era seed and validated consumed frame fields. Never fabricate a missing body,
reconstruct an unrecorded historical life or overwrite an invalid artifact.
The existing current-run producer is unchanged and may record only when the
era's recorded covenant/parameters still match. Preserve its post-era label.

Pause care and ignore care/planning keys during playback; expose bounded
scrubbing, play/pause, help that freezes playback, and returns to the selected
report or entry care. Preserve S2 checkpoint/retry. Fit recorded body dimensions
inside the existing panel, without altering packets or engine semantics.

Evidence: `research/experiment_reports/2026-10-04-saved-replays.md`,
`game/tests/test_saved_replays.py`, `labs/game_loop/verify_saved_replays.py`,
`data/game_client/saved_replays_release_stage0.json`. Thirteen targeted tests
and 17 actual application observations pass. The current focused/full runner gates passed; native keyboard and published
CI remain separate. Final closure is recorded in `.development/t3-closed.json`.
