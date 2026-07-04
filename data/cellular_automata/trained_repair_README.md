# CA/NCA Trained Repair Stage 0

Held-out benchmark for a gradient-trained per-cell softmax repair rule against no-repair, the role-prior baseline, and the target-template assisted attractor.

- Training grids: 40
- Held-out targets: 10
- Cycles: 5 at dropout 0.2

| Arm | Final overlap | Structural agreement | Validity | Repair gain/event |
| --- | ---: | ---: | ---: | ---: |
| no_repair | 0.231776 | 0.231776 | 0.1 | 0.0 |
| role_prior | 0.900458 | 0.532016 | 1.0 | 0.168864 |
| trained | 0.862546 | 0.631871 | 1.0 | 0.152124 |
| assisted | 1.0 | 1.0 | 1.0 | 0.209487 |

- Trained vs no-repair overlap delta: 0.63077
- Trained vs role-prior overlap delta: -0.037912
- Trained vs assisted overlap delta: -0.137454
- Decision: prototype_learned_repair_gap_narrowed

The trained arm learns from (damaged neighborhood -> target token) pairs by deterministic gradient descent and never sees a target template during repair. Structural agreement is reported because plain overlap does not penalise spurious fills.
