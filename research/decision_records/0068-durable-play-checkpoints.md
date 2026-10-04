# DR 0068: checkpoint the pet first and preserve play on save failure

Date: 2026-10-04. Status: locally complete; 2,537 tests / 24 suites passed in full run
`20261004T173915-19f22122`, alongside the actual launch checks.

Actual app failures proved the separate writes were a product defect: a failed
primary replacement left an export with two lineage records against the saved
pet's one, and a failed export aborted before saving otherwise writable progress.
The browser already consumes the companion's embedded lineage.

Keep one authority: atomically checkpoint the companion first, then synchronize
the derived lineage export. Repair stale exports on validated resume/recovery,
backing up replaced bytes. Export failure is a warning, not loss of the saved
pet. Repeated identical checkpoints leave the recovery backup intact. No schema
migration, journal, multi-file transaction or second persistence authority.

Ctrl+S saves now. Critical life transitions checkpoint. Primary failure pauses
care and retains the live in-memory state for retry. Failed interactive quit
stays open; Ctrl+S retries that quit, Ctrl+Q explicitly discards unsaved progress.
Bounded runs exit nonzero on primary failure. Existing policy/covenant choices,
S1 explicit recovery/refusals, and scientific/default-adoption boundaries stay.

Evidence: `research/experiment_reports/2026-10-04-safe-checkpoints.md` and
`data/game_client/safe_checkpoints_release_stage0.json`.
