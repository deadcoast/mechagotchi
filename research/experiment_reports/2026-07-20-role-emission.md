# Experiment Report: Motion-Role Emission — the Vocabulary-Blind Generator Found (Cycle 20 · SHARED · J2, measurement half)

Date: 2026-07-20

## WHY

Phase I measured the generative range from three sides (I5b's
descriptor-range bound, I4's exemplar-only motion roles, I2's
structureless tapes). J2's charter gates any generator increment on
MEASURED emission rates: how often do the generation surfaces
actually emit the DR 0011/0015 motion trio (limb, joint,
decoration)?

## WHAT

`labs/grid_genome/role_emission.py` (RED first, 5 pins) measures
1,000 grids per generation surface against the committed corpora:

| Surface | Motion-trio emission (mean grids-with-role rate) |
| --- | --- |
| constrained (lab) | **0.0** |
| **promoted `generate_batch`** | **0.0** |
| WFC (adopted, DR 0031) | 0.800667 |
| seed corpus 16×16 (reference) | 0.48 |
| vocabulary exemplars (reference) | 1.0 |

**The finding, with its mechanism:** the constrained path — including
the PROMOTED `generate_batch`, the exact surface the game's evolution
loop breeds offspring through — emits the motion trio at **exactly
zero**, while its own training corpus carries it at 0.48. The cause
is structural, found by survey: the constrained generator projects
every grid through the 5-token matrix alphabet
(`TOKENS = [".", "B", "A", "E", "M"]` →
`_matrix_from_grid`/`_grid_from_matrix`), which predates DR 0011's
vocabulary ratification — limb, joint, decoration (and the
shell/antenna/effect distinctions) are ERASED in projection and can
never be reconstructed. The evolution path is vocabulary-blind by
construction. WFC, which works over grid patterns directly, carries
the trio at 0.80 — but WFC feeds corpus mixes, not the evolve loop's
offspring.

This explains all three Phase-I observations at once: the
I5b descriptor-range ceiling, the exemplar's isolation, and why
creatures with legs are effectively absent from evolved populations —
the game's players cannot breed what the breeding surface cannot
spell.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/grid_genome -p "test_role_emission.py"
ImportError: cannot import name 'MOTION_ROLES' from 'role_emission'
FAILED (errors=1)                           # RED: the lab absent
# after implementation:
Ran 5 tests ... OK
PS> python -B labs/grid_genome/role_emission.py
# motion-trio emission: constrained 0.0, wfc 0.800667,
#   promoted_generate_batch 0.0 vs seed corpus 0.48 and exemplars 1.0
```

## HONEST REMAINDER

1. **The increment is designed and gated separately** (the J2 second
   half, its own decision record): a vocabulary-complete generation
   alphabet is a deep change to the promoted generation model — the
   token projection, the adjacency statistics, the reconstruction,
   and the package mirror all move together under parity pins, judged
   by pre-registered gates (emission up, validity held, descriptor
   support widened).
2. **WFC's 0.80 is not a free ride** — WFC feeds corpus mixes and
   founder pools, not the evolve loop's per-generation offspring; a
   WFC-arm in evolution would be its own gated change.
3. **Emission ≠ expression**: a generator that emits limbs must still
   pass the validator's organ semantics; the measured gates for the
   increment include validity held at 1.0.

## Sources

- `audits/TODO.md` (cycle 20 J2)
- `labs/grid_genome/role_emission.py` (+ `test_role_emission.py`)
- `data/grid_genome/role_emission_stage0.json`
- `labs/grid_genome/constrained_generator.py` (the 5-token alphabet), `labs/grid_genome/markov_grid.py` (`_matrix_from_grid`)
- `research/experiment_reports/2026-07-20-per-role-motion.md` (I4), `2026-07-20-occupancy-saturation.md` (I5b)
- `research/decision_records/0011-run-one-run-two-reconciliation.md`, `0015-dormant-vocabulary-coverage.md`, `0031-wfc-generation-adoption.md`
