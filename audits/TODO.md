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

- [x] **V1 · Research report v1.0 + manifest — the ENGINE+GAME
  milestone.** (2026-07-07:
  `research/reports/mechagotchi_research_report_v1_0.md` — "the
  realization wave" — + `research_report_v1_0_manifest.json`
  consolidating 46 experiment reports and 20 decision records
  (0008–0027) across the 2026-07-05→07 window, every one of the 79
  referenced paths verified to exist; headline metrics incl. ten of
  ten og module targets, five of five notices, test base 747 → 1,210
  all green, the adopted model's gates, the mortality gradient, and
  the soak; owner decisions and named re-openers ledgered as
  deliberately-open, not queued. The reports index updated; the
  underlying lab reports untouched, per the convention.)
- [ ] **V2 · Refresh `docs/agent-standards.md`.** Its own charter is to
  orient a fresh session with a state snapshot — six cycles stale.
  Rewrite the snapshot to the current truth (ten modules, the Keeper
  session surfaces, the adopted model, the standing owner decisions),
  keeping its honesty norms and re-verification instructions intact.
- [x] **V3 · Untrack the `__pycache__` hazard.** (2026-07-07: all 144
  tracked bytecode files `git rm --cached`-ed (files stay on disk,
  covered by the ignore rule — verified); CLAUDE.md and `.gitignore`
  hazard notes updated to CLOSED; zero tracked `__pycache__` paths
  remain; smoke green. The `-B` discipline stays as tree hygiene.)

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
