# Development TODO — Cycle 28: ENGINE → GAME / Phase R

**PLANNED, NOT STARTED.** Prepared from the Phase-Q gate and DR 0060's named
promotion debt. Q5 must be reviewed before this cycle starts. The completed
cycle 27 charter is archived at `sunsetted/complete/TODO/27/TODO.md`.

The complete contract is `docs/development/cycle-28-learning-consumer.md`.
The product gap is concrete: the package lacks Q-table observe/signal and its
full-confidence follower; the game still uses five incumbent threads. Lab
eligibility (+7.355%) is not a measured current-game gain. Do not enable an
invalid SLIP key or silently adopt the extended lab roster.

- [ ] **R1 · Package producer + consumer parity, defaults off (ENGINE).**
  Port the bounded existing Q-table and follower together. Pin complete
  lab/public decisions, thread state, off/cold/warm/floor/tie/deliberation cases,
  original instruments and no input mutation. Keep schema/defaults unchanged.
- [ ] **R2 · Explicit playable opt-in and honest saves (GAME).**
  Wire only the required thread/consumer beside the five kept threads. Deliver
  app and launcher choice, save/resume/succession/fleet-off/refusal checks;
  old saves stay incumbent and only the keeper feeds.
- [ ] **R3 · Actual-game default ADOPT/REFUSE (ENGINE + GAME).**
  Preregister paired incumbent/additive/follower arms at inherited budgets,
  compare the actual v0.2 product, retain the 5% bar and price begging explicitly.
  Preserve historical controls. Refusal ships the opt-in, not a forced default.
- [ ] **R4 · Chosen behavior and real release continuity (GAME).**
  Apply any adoption only to new lives, retain opt-out and historical saves,
  document exact artifact impact, and verify readable controls and native bundle.
- [ ] **R5 · Consolidated gate and following plan (SHARED).**
  Full sweep, artifact/hash audit, measured triad continuity, cycle archive.
  No next cycle begins from a stale status or unreviewed result.

## Retained boundaries

No hidden-axis displays or invented definitions; no graded follower, autonomous
cleaning, reward/threshold retuning, archive default change, human-preference
claim or unrequested hosting. Human studies remain prepared-not-blocking.
Follow pombi's authorized local development direction. The user's 2026-10-04
instruction assigns verified commits/pushes to the development agent; preserve
external work and never rewrite history. No new source copies or environment.

## Sources

- `research/experiment_reports/2026-10-04-phase-q-gate.md`
- `research/decision_records/0060-qtable-consumer-seam.md`, `0063-covenant-mechanics-authorship.md`, `0064-default-covenant-cleanliness.md`, `0065-hidden-axis-sources-and-readable-controls.md`
- `docs/development/cycle-28-learning-consumer.md`
- `packages/mecha_engine/src/mecha_engine/learning/_switchboard.py`, `threads.py`; `game/src/mecha_game/session.py`
