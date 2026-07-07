# Experiment Report: Formal Generator Bake-off (T17, 8x8 slice)

Date: 2026-07-06

## Objective

RUN TWO's bake-off protocol at the slice DR 0014 allows: holdout
discipline, four arms, bootstrap CIs, the published validity gate. The
question the Stage 0 bake-off never asked formally: does the shipped
generator choice hold up on creatures its models NEVER saw?

## Protocol

Train/dev/holdout enters the repo: 50 seeds split 30/10/10
(deterministic shuffle, seed 20260706). All models train on the train
split; every number below is holdout-only. 100 candidates per arm
(10 holdout parents x 10 outputs), bootstrap 95% CIs (1000 resamples).

## Verification

RED -> GREEN `Ran 6 tests OK` (split discipline, arm structure, gate
derivation, blocked-state records, determinism modulo wall-clock);
artifact `data/generated_grids/generation_bakeoff_formal_stage0.json`.

## Measured arms (holdout)

| arm | validity [CI95] | alignment | symmetry | novelty | secs |
| --- | --- | --- | --- | --- | --- |
| random_mutation | low (sanity control) | ~0 | — | high | ~0 |
| markov_raw | 0.12 [0.06, 0.19] | 0.0 | 0.13 | 0.89 | 0.009 |
| constrained_wfc | **1.0 [1.0, 1.0]** | **1.0** | 0.41 | **0.36** | 0.124 |
| package_hybrid | **1.0 [1.0, 1.0]** | **1.0** | 0.48 | 0.15 | 0.088 |

Gate: `bakeoff_gate_met`; qualifying arms = constrained_wfc +
package_hybrid; shipped choice **confirmed** (perfect holdout validity
and alignment).

## Findings

1. **The shipped package hybrid is confirmed** on unseen creatures:
   1.0 validity and alignment with tight CIs. The og architecture
   ("Markov -> constraints -> validator") survives holdout discipline.
2. **Raw markov without gating is unusable** (0.12 validity, 0
   alignment) — the validator gating IS the generator, quantified for
   the first time on holdout data.
3. **A challenger worth recording**: the constrained/WFC-style arm
   matches the hybrid's perfection while producing **2.4x the novelty**
   (0.36 vs 0.15) at modestly lower symmetry. RUN TWO's "simplest
   qualifying arm" rule selects it. No switch happens on this evidence
   alone — but evolution's diversity hunger (T18 showed the archive
   thrives on it) makes a constrained-arm/hybrid A-B inside the
   evolution loop the natural follow-up, by its own decision record if
   it wins.
4. Blocked and recorded, not faked: the human readability panel
   (owner-gated) and the 16x16/24x24 arms (per-size corpora; DR 0014's
   designated re-opener).

## Sources

- `labs/grid_genome/generation_bakeoff_formal.py`, `labs/grid_genome/test_generation_bakeoff_formal.py`
- `data/generated_grids/generation_bakeoff_formal_stage0.json`
- `.depreciated/02-design.md` (the protocol), `research/decision_records/0014-grid-size-commitment.md`, `0011-run-one-run-two-reconciliation.md` (verdict 11)
