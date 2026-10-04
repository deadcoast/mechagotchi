# DR 0070: consume saved elite records without changing the living campaign

Date: 2026-10-04. Status: locally complete and reviewed. Full run
`20261004T185738-2f3b4168` passed 2,563 tests / 24 suites, two documented
skips and 2,282 valid JSON artifacts without source mutations. Query parity,
11 game pins, 22 application observations and 12 additional adoption checks
preserve covenant, policy and save/restart behavior. Evidence and exact commands
are in the report below. Native keyboard and published CI remain separate.

The repertoire browser explicitly deferred ledger browsing to F17, but B still
required current-run eras after restart. DR 0022 already stores complete elite
blobs and each era's covenant. DR 0021 requires the player to see species memory.

Expose load_era_elites through the existing lab-first storage surface, preserving
blob authority, niche ordering and campaign/era scope. Promote the exact proven
query to the package with source/behavior parity. No schema or engine math changes.
Read those records without hydrating KeeperCampaign.eras or altering continuation.

Historical rendering uses the recorded covenant. Explicit A adoption uses the
current covenant gate and S2 checkpoint behavior, retaining the policy choice;
refusal keeps the existing pet. Browsing pauses care and queues no care input.
B/Escape goes back, T opens the selected report, and help returns to the selection.
Empty/corrupt data stays explicit; unavailable archives cannot launch planning.

The actual T1 small-window review also found C controls behind care status.
Move the existing controls first, preserving covenant spending and care timing.

Evidence: `research/experiment_reports/2026-10-04-saved-archive.md`,
`labs/game_loop/test_saved_elite_query.py`, `game/tests/test_saved_archive.py`,
`labs/game_loop/verify_saved_archive.py`, and separate saved_archive_release
observation artifacts. Native keyboard remains blocked by missing runtime tools.
