# Experiment Report: SLIP Mass Bounds Scale by Reference Canvas — A3 Closes (Cycle 09 · ENGINE)

Date: 2026-07-08

## WHY

Every SLIP profile's `body_mass_min/max` is an absolute cell count
denominated at the 8×8 canvas, so every 16×16 corpus creature (core
18–85) violated every shipped profile — blocking SLIP-aligned
generation and workshop exports at the ratified default scale, and
(ahead in A4) profile-filtered evolution. DR 0014 put "size-relative
mass bounds in SLIP" on the ladder; DR 0030 is the design decision.

## WHAT

**DR 0030**: mass bounds are denominated at the 8×8 reference canvas
and scale by area — `effective_bound = authored_bound · w · h // 64` —
implemented identically in the two (and only two) alignment surfaces:
the lab authority (`labs/grid_genome/slip.py`) and the promoted
`mecha_engine.slip`. No schema change, no fixture change; the error
message reports the EFFECTIVE bounds actually applied; malformed
`grid_size` falls back to the authored bounds. At 8×8 the scaling is an
exact identity (`bound·64//64 = bound`), so every historical verdict
and error string is byte-identical — the F2 pair pin's 2,080 alignment
cases pass unmodified.

RED first: ten failures (every lcd_green 16×16 corpus creature rejected
by the zoo profile) before the change; the parity pin gained a 16×16
sweep with a non-vacuity assertion (at least one profile×creature pair
must actually align, so the test can never silently pass on an
all-rejecting scaler).

## FINDINGS

- The zoo's 4..24 becomes 16..96 at 16×16: all ten lcd_green corpus
  creatures align with `slip_lcd_seed`; a deliberately tightened
  profile (4..5 → 16..20) rejects the 54-core beetle with the honest
  effective-bounds message ("body mass 54 outside SLIP bounds 16..20").
- The validator's ratified floor (18) stays the stricter hard gate
  beneath the SLIP preference layer (a scaled minimum of 16 admits
  nothing the validator would pass at fewer than 18 cells).
- The A2 workshop limitation closes for aligned creatures: PNG/APNG
  export of a 16×16 creature bound to a palette-matching profile now
  passes the alignment gate.
- The dossier's `grid_size_min/max` generator priors are NOT this
  change (they gate generation, not alignment) — named in DR 0030 as a
  future DR 0012-ladder extension for Phase B's generator.

**With this increment, A3 is complete**: validator floor (DR 0029 law,
both validators, 500-file parity), generation size-parametric (16×16
gates in lab + contract), repair retrained and re-gated at scale
(bit-for-bit 8×8, 40/40 valid held-out repairs, the NumPy trigger
measured and not fired), lifecycle re-measured through the renormalized
stress probe (real 16×16 episodes in the stress_probe_scaling lab;
`initial_state` verified to derive only from dimensionless stress/
damage means), and SLIP bounds size-relative (this report). Every
standing gate reruns green at 16×16 and no 8×8 pin moved.

## Verification

RED:

```powershell
PS> python -B -m unittest discover -s labs/grid_genome -p "test_slip_constraints.py"
Ran 11 tests ... FAILED (failures=10)
```

GREEN (constraint + parity suites, then the SLIP consumers):

```powershell
PS> python -B -m unittest discover -s labs/grid_genome -p "test_slip*.py"
Ran 59 tests in 0.278s
OK
PS> python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
Ran 209 tests in 5.421s
OK
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 291 tests in 5.637s
OK
PS> # slip_validator 24 OK · runtime_integration 65 OK · game_loop 81 OK ·
PS> # workshop 58 OK · lifecycle_sim OK · map_elites_archive OK · cellular_automata OK
```

## Sources

- `research/decision_records/0030-slip-size-relative-mass-bounds.md`
- `labs/grid_genome/slip.py`, `packages/mecha_engine/src/mecha_engine/slip/authority.py`
- `labs/grid_genome/test_slip_constraints.py`, `labs/grid_genome/test_package_slip_parity.py`
- `research/decision_records/0011` (verdict 1), `0012`, `0014`, `0029`
- `research/experiment_reports/2026-07-08-16x16-validator-generation.md`, `2026-07-08-stress-probe-scaling.md`, `2026-07-08-repair-at-16x16.md` (the A3 companions)
- `data/slips/valid/`, `data/seed_grids_16x16/`
- `audits/TODO.md` (cycle 09 A3), `docs/gap-analysis.md` (Phase A)
