# Experiment Report: CTM Deliberation in the Live Switchboard (R1)

Date: 2026-07-06

## Objective

DR 0017's R1 (carried T8): wire `labs/ctm_ticks`' confidence-gated
deliberation into the LIVE decision path — the og "thinking over ticks"
— and measure the og questions: does internal deliberation improve
decisions, and does the creature visibly think?

## Design

- New SLIP ladder field `deliberation {max_ticks: 2..8,
  confidence_threshold: 0..1}` (0.2.0-only, all four lab surfaces +
  the four package `_slip` mirrors + regenerated pydantic schema).
- Consumer: `run_switchboard` deliberates when the lifecycle-stashed
  keys are present — the CTM lab's EXACT semantics (state pressure,
  0.55/tick gain, margin-confidence), pinned by a live-vs-lab parity
  test; decisions gain a `deliberation` trace (tick_count etc.). Both
  package switchboard mirrors (learning/_switchboard,
  lifecycle/_policy) synced. Absent keys = bit-for-bit frozen path.

## Verification

RED -> GREEN: grid_genome slip suites, ctm_ticks 5, slip_validator 24,
lifecycle 19, package 266 — all green; live path == CTM lab verbatim on
a torn state (multi-tick), confident states act immediately (1 tick).

## Measurement (8 aligned creatures x 48-tick sheltered episodes)

```txt
deliberation events: 64 across 8 episodes (~8 per episode when torn)
mean internal ticks when run: 1.25
need_balance: thinker 0.791142 vs baseline 0.791142 (delta 0.0%)
```

## Verdict (og decision rule applied honestly)

**Adopt as an opt-in species expressiveness trait; WATCH for utility.**
The creature now genuinely deliberates — observable internal ticks with
a trace the game can render as "thinking…" (the felt-aliveness half,
delivered). But in sheltered episodes deliberation converged to the
same actions with higher confidence: NO measured wellbeing gain (delta
0.0, honestly recorded — not destabilizing either). Per the og rule
("CTM should not become a core dependency until smaller systems fail"),
it stays opt-in per species; the stress regime and future game contexts
are the designated re-measurement grounds.

## Sources

- `research/decision_records/0017-recalibration-engine-game-duality.md` (R1)
- `labs/ctm_ticks/ctm_inspired_ticks.py`, `labs/grid_genome/micro_switchboard.py`, `labs/grid_genome/test_slip_deliberation.py`
- `labs/lifecycle_sim/lifecycle_sim.py`, `packages/mecha_engine/src/mecha_engine/{learning/_switchboard,lifecycle/_policy}.py`
- `research/slip/slip.schema.json`, `data/slips/valid/slip_v2_no_shell.json`
