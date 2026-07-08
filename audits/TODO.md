# Development TODO — Cycle 07: consolidation — the v1.0 milestone

Source: the repo's own conventions now that the build tracks have
converged. Cycle 06 is archived complete at `audits/complete/06/`
(F1 the seen thought — five notices of five live; F2 the slip module —
every og module target realized; F3 the real-mutation fine-tune —
adopted on a full-gate win). The last consolidated report is v0.9;
cycles 02–06 shipped the entire ENGINE+GAME duality since. Governing
rule unchanged: deep integrations over breadth (DR 0017); a task is
complete when developed to its description, then marked; development
proceeds continuously; planning triggers ONLY on exhaustion confirmed
COMPLETE. (Decision records remain the design documentation for tasks
that need them; they do not pause the queue.)

- [ ] **V1 · Research report v1.0 + manifest — the ENGINE+GAME
  milestone.** The consolidated-report convention
  (`research/reports/research_report_v1_0.md` +
  `research_report_v1_0_manifest.json` with `source_plan`,
  `referenced_artifacts`, `headline_metrics`): consolidate cycles
  02–06 — the ten promoted modules, the complete game loop (all five
  DR 0021 notices live; Contribute/Covenant/Run/Collect/Review),
  the storage spine, the replay window, the mortal-wound gradient, the
  dataset program and its consumers, the adopted real-hardened
  readability model, and the honest blocked/closed ledger (real-CuBFF
  optional by owner decision; render's re-opener; the manual-ratings
  gate). Consolidation must NOT replace the underlying lab reports.
- [ ] **V2 · Refresh `docs/agent-standards.md`.** Its own charter is to
  orient a fresh session with a state snapshot — six cycles stale.
  Rewrite the snapshot to the current truth (ten modules, the Keeper
  session surfaces, the adopted model, the standing owner decisions),
  keeping its honesty norms and re-verification instructions intact.
- [ ] **V3 · Untrack the `__pycache__` hazard.** The pre-existing
  hazard CLAUDE.md documents: bytecode directories are TRACKED in git
  (the ignore rule stops new ones but does not untrack). `git rm
  --cached` every tracked `__pycache__` path, verify the sweep stays
  green and `git status` stays clean under the `-B` discipline, and
  update the hazard's documentation to say it is CLOSED.

## Standing note

The identity constraint and DR 0017 govern: the engine is the
application, the game is its showcase. The rating system is the
fallback; `.depreciated/` is the owner's archive (ignore unless
linked). Owner-decision items are NOT tasks: the `[project]`
dependencies policy stays deliberately blocked; the repo-wide license
grant stays the owner's pending decision; real-CuBFF ingest stays the
optional drop-in seam (cycle 04). `render` stays dispositioned with
its named re-opener (DR 0026).

## Sources

- `audits/complete/06/TODO.md` (cycle 06, complete)
- `research/decision_records/0017-recalibration-engine-game-duality.md`
- `research/reports/` (the consolidated-report convention, v0.9 the last)
- `docs/agent-standards.md` (V2's charter)
- CLAUDE.md (V3's documented hazard)
