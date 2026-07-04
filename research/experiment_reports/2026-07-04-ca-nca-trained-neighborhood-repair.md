# Experiment Report: CA/NCA Gradient-Trained Neighborhood Repair

Date: 2026-07-04

## Objective

Address the `lab_only_target_template_assisted` research blocker by training
an actual learned repair rule — fitted by gradient descent from
(damaged neighborhood -> target token) pairs — and benchmarking it on
held-out grids against no-repair, the earlier role-prior learned baseline,
and the target-template assisted attractor.

## Source Basis

Growing Neural Cellular Automata frames regeneration as a learned local-rule
problem; the soft-robot NCA work benchmarks regeneration as a learned local
policy rather than target-template reconstruction. This lab keeps that framing
but restricts the learner to what the stdlib-only Stage 0 environment allows:
a per-cell multiclass softmax over one-hot neighborhood and position features,
trained with deterministic full-batch gradient descent.

Sources:

- https://distill.pub/2020/growing-ca/
- https://distill.pub/selforg/2021/textures/
- https://arxiv.org/abs/2102.02579

## Scope

Included:

- per-cell softmax repair rule (161 features: 24-cell 5x5 neighborhood
  one-hot over 4 live tokens, 64-position one-hot, bias; 5 output classes)
- deterministic full-batch gradient descent (150 epochs, learning rate 1.5,
  live-class weight 3.0, zero-initialised weights, convex loss, exactly
  reproducible)
- training pairs from seeded stochastic dropout (rates 0.1/0.2/0.3/0.4) on a
  40-grid training split; 8,639 examples
- held-out evaluation on the remaining 10 seed grids the model never saw
- five seeded stochastic damage/repair cycles per held-out grid
- four arms under identical damage seeds: no-repair, role-prior (retrained on
  the same 40-grid split), trained, assisted target-template attractor
- a new two-sided `structural_agreement` metric, because `matrix_overlap`
  is one-sided and never penalises spurious fills

Not included:

- differentiable NCA with hidden state channels
- damage-curriculum or self-play training
- novel-species generalisation (all 50 grids are the same hand-authored
  species corpus)
- human repair ratings

## Verification

Test command:

```powershell
python -B .\labs\cellular_automata\test_ca_nca_growth_repair.py
```

Result:

```txt
Ran 19 tests in 2.035s
OK
```

Lab command (runs in about 6 seconds):

```powershell
python -B .\labs\cellular_automata\ca_nca_growth_repair.py --mode trained-repair --output-dir .\data\cellular_automata
```

Result summary (held-out grids `mg_seed_041`..`mg_seed_050`, 5 cycles at
dropout 0.2):

| Arm | Final overlap | Structural agreement | Validity | Lifecycle survival | Readability |
| --- | ---: | ---: | ---: | ---: | ---: |
| no_repair | 0.231776 | 0.231776 | 0.1 | 0.1 | 0.442509 |
| role_prior | 0.900458 | 0.532016 | 1.0 | 1.0 | 0.786010 |
| trained | 0.862546 | 0.631871 | 1.0 | 1.0 | 0.833454 |
| assisted | 1.0 | 1.0 | 1.0 | 1.0 | 0.867316 |

Key deltas:

- trained vs no-repair final overlap: **+0.63077** (agreement +0.400095)
- trained vs role-prior: overlap -0.037912, structural agreement **+0.099855**
- trained vs assisted final overlap: -0.137454
- mean first-cycle (single-shot) repair overlap for trained: 0.939011

## Findings

1. The trained rule genuinely learns: training loss falls from 1.609 (uniform)
   to 0.251, and on grids it never saw it recovers single-shot damage to
   0.939 overlap and holds 0.8625 overlap with 100% validity and lifecycle
   survival across five compounding damage cycles, versus 0.2318 overlap and
   10% validity with no repair.
2. Metric honesty matters: the retrained role-prior baseline posts a higher
   one-sided overlap (0.9005) than the trained rule by force-filling the most
   common corpus positions — overgrowth that `matrix_overlap` cannot see. On
   the two-sided structural agreement the trained rule is the best learned
   arm (0.6319 vs 0.5320) and it also wins on readability. Both learned arms
   remain far below the assisted attractor's 1.0 agreement.
3. The assisted target-template attractor is still the upper bound. The
   trained rule does not meet the assisted stability bar
   (overlap/validity/agreement >= 0.9 held jointly), mainly because a linear
   softmax learns one species-level shape prior and cannot distinguish which
   corpus variant it is repairing.

## Decision

Status: `prototype_learned_repair_gap_narrowed`.

The repair lab now contains a real gradient-trained repair rule with a
machine-checkable evidence surface
(`data/cellular_automata/ca_nca_trained_repair_stage0.json`:
`decision.thresholds.beats_no_repair_substantially = true`,
`best_learned_on_structural_agreement = true`,
`meets_assisted_stability_bar = false`). The
`lab_only_target_template_assisted` blocker no longer needs to be static
with null evidence: it can be derived from
`meets_assisted_stability_bar`, which honestly remains `false` today, so the
blocker stands — but for a measured reason, with a defined bar to clear.
The next step toward clearing it is a learner with per-grid context (for
example conditioning on the surviving cells' global layout or hidden state
channels), not more template assistance.
