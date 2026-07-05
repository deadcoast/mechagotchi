# CA/NCA Trained Repair Stage 0

Held-out benchmark for a gradient-trained per-cell softmax repair rule against no-repair, the role-prior baseline, a wound-site variant of the same model (damage-event positions observed, tokens still predicted), and the target-template assisted attractor.

- Training grids: 40
- Held-out targets: 10
- Cycles: 5 at dropout 0.2

| Arm | Final overlap | Structural agreement | Validity | Repair gain/event |
| --- | ---: | ---: | ---: | ---: |
| no_repair | 0.231776 | 0.231776 | 0.1 | 0.0 |
| role_prior | 0.900458 | 0.532016 | 1.0 | 0.168864 |
| trained | 0.862546 | 0.631871 | 1.0 | 0.152124 |
| site_aware | 0.938462 | 0.938462 | 1.0 | 0.191245 |
| assisted | 1.0 | 1.0 | 1.0 | 0.209487 |

- Trained vs no-repair overlap delta: 0.63077
- Trained vs role-prior overlap delta: -0.037912
- Trained vs assisted overlap delta: -0.137454
- Site-aware vs trained agreement delta: 0.306591
- Site-aware vs assisted overlap delta: -0.061538
- Decision: wound_signal_repair_meets_bar

The trained arm learns from (damaged neighborhood -> target token) pairs by deterministic gradient descent and never sees a target template during repair. The site_aware arm reuses that model but refills exactly the positions the damage event reports as destroyed (tokens still predicted, never remembered), which removes overgrowth by construction. Structural agreement is reported because plain overlap does not penalise spurious fills.
