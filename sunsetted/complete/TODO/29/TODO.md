# Development TODO - Cycle 29: safe companion resume

Cycle 28 is locally complete and reviewed from its actual source, native
observations and final full run 20261004T162036-b03ceece. The archive is
`sunsetted/complete/TODO/28/TODO.md`; the Q-table default refusal remains intact.

- [x] **S1 - Safe resume, backup recovery and policy status.** Validate loaded
  generation models and compatibility before play; refuse malformed saves
  without writes; restore a validated backup only on explicit request while
  retaining the prior primary; show the effective policy clearly. Preserve
  exact good-save continuation, existing policy choices and scientific files.

Contract: `docs/development/cycle-29-safe-resume.md`. Use the existing workflow,
this repository and its .venv. No Git mutations by the development agent.

S1 closed locally with full run `20261004T170013-413498d4`: 2,528 tests in
24 suites, two documented zlib skips, 2,275 valid JSON artifacts, no source
mutations. Actual source/CLI/native recovery passed 48 launches / 48 checks.
Report: `research/experiment_reports/2026-10-04-safe-resume.md`; native app:
`game/dist/s1-safe-resume/Mechagotchi/Mechagotchi.exe` (retain `_internal`).

- [x] **S2 - Durable play checkpoints and save-failure recovery.** Implemented
  with focused run `20261004T173506-cd1787fd`: 655 tests / 2,276 JSON files,
  no mutations. Actual source/CLI/native observations: 48 passing process checks
  and four interactive retry/discard flows. Contract:
  `docs/development/cycle-29-safe-checkpoints.md`; report:
  `research/experiment_reports/2026-10-04-safe-checkpoints.md`.
  **Closed:** full run `20261004T173915-19f22122`, 2,537 tests / 24 suites,
  two documented zlib skips, 2,276 valid JSON artifacts, no source mutations.

No verification is running and no next slice has started. Preserve current
focused/native evidence; do not repeat unchanged S1 verification. S2's verified
bundle is `game/dist/s2-safe-checkpoints/Mechagotchi/Mechagotchi.exe` with adjacent
`_internal`. Q-table default adoption remains refused; remote published-SHA CI,
signing and human usability remain separate. No Git mutations by the agent.
