# DR 0067: validate saved models and recover companions explicitly

Date: 2026-10-04. Status: implemented; full local closing gate recorded in report.

Reject structurally invalid generation models and incompatible parent dimensions
in the engine before use. Validate required saved-session structure on resume
without resetting, retraining or changing valid saved state. Preserve the
existing per-life learning choice; show it in both live and dead casing states.

Add explicit `--recover-backup` through source, CLI and native app. Validate the
exact backup bytes and policy before any write; archive any primary bytes under
a content-derived filename without overwrite, then atomically replace the
primary. Recognize backup-only native homes, and refuse automatic replacement
of a missing primary when a backup remains. Refuse new-life/covenant conflicts.

Normal saves atomically replace each file, retaining the prior primary as the
backup. This is per-file durability, not a transaction across companion and
lineage exports. Recovery uses the backup's age/state; it does not merge newer
progress. Prior science, generator math and the Q-table adoption refusal stay.

Evidence: `research/experiment_reports/2026-10-04-safe-resume.md` and
`data/game_client/safe_resume_release_stage0.json` (48 actual process launches,
48 passing continuity/refusal checks; rendered casing inspected).
