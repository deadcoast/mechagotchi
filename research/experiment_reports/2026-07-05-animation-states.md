# Experiment Report: Animation-State Vocabulary (T4, first slice)

Date: 2026-07-05

## Objective
Audit T4: define the og animation-state semantics on the grid genome and
emit `animstate_300`. Design thesis proven: states are deterministic
visual-only projections of the genome — no second art source.

## Verification
RED: module absent (8 tests). GREEN:

```txt
labs/grid_genome  Ran 116 tests  OK
python -B labs/grid_genome/animation_states.py
  "sequence_count": 300, "projection_valid_rate": 1.0
  "status": "adopt_projection_semantics"
```

## Findings
1. All 300 projections (60 creatures x 5 states) preserve
   positions/roles/organs and validator validity; idle is the identity;
   blink/sleep/beg/ill derive entirely from palette + role + parity.
2. Honest corpus note: the bake-off's raw markov outputs include
   invalid grids by design (the arm's measured validity rate) — the
   animation corpus filters to validator-valid generated grids; the
   first run's 0.833 valid rate exposed this and the filter fixed it.
3. og dataset `animstate_300` delivered (T11 item).

## Remaining T4 scope (tracked)
Render-packet animation selection (T16), the workshop five-state
previewer, and the SLIP `animation_vocab` field (T3.5) — all recorded as
blocked_states in the artifact.

## Sources
- `labs/grid_genome/animation_states.py`, `labs/grid_genome/test_animation_states.py`
- `data/grid_genome/animation_states_stage0.json`, `data/grid_genome/animstate_300.json`
- `research/algorithm_cards/animation_states.md`
- `audits/TODO.md` (T4, T11, T16)
