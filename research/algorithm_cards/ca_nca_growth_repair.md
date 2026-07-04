# Algorithm Card: CA/NCA Growth and Repair

## Purpose

Test whether cellular-automata style local update rules can support
Mechagotchi grid growth, damage repair, and lifecycle viability without making
the creature unreadable.

## Mathematical Basis

Cellular automata update each cell from local neighbor state. Growing Neural
Cellular Automata extend this idea with learned local update rules that can grow
patterns from a seed, persist, and regenerate after damage.

This Stage 0 lab is not a trained neural CA. It is a deterministic discrete
local-attractor baseline that uses a target grid as a genotype-like template.

## Inputs

- Valid seed grid genomes
- A deterministic damage mask
- Local 8-neighborhood token state
- Lifecycle and readability metrics

## Outputs

- Damaged grids
- Seed-grown grids
- Repaired grids
- Growth overlap, repair overlap, validity, readability delta, SLIP alignment,
  and lifecycle survival metrics

## Strengths

- Directly tests growth and repair after the lifecycle gate
- Keeps the update rule inspectable
- Produces valid grid-genome outputs
- Gives a baseline before any heavier differentiable NCA implementation

## Weaknesses

- Not trained and not neural
- Uses a target template, so it is closer to local morphogenetic repair than
  open-ended emergence
- Damage pattern is deterministic
- SLIP alignment is low when measured against the LCD-only profile across mixed
  seed palettes

## Failure Modes

- Overstating this as a trained NCA
- Perfect template reconstruction masking weak autonomy
- Validity improving while animation or user-perceived repair remains weak
- Repair rules producing unreadable growth under harder damage patterns

## Integration Risk

Medium. The discrete repair/growth rule is safe as a lab module, but a real NCA
would add ML infrastructure and training complexity.

## License Status

Internal Mechagotchi research code. Source basis is primary literature and
article references only; no external code is vendored.

Sources:

- [a](https://distill.pub/2020/growing-ca/)
- [b](https://distill.pub/selforg/2021/textures/)
- [c](https://arxiv.org/abs/2102.02579)

## Prototype Result

Implemented on 2026-05-12.

Artifacts:

- `labs/cellular_automata/ca_nca_growth_repair.py`
- `labs/cellular_automata/test_ca_nca_growth_repair.py`
- `data/cellular_automata/ca_nca_growth_repair_stage0.json`
- `data/cellular_automata/ca_nca_persistence_damage_stage0.json`
- `data/cellular_automata/ca_nca_repeated_stochastic_damage_stage0.json`
- `data/cellular_automata/ca_nca_learned_repair_comparison_stage0.json`
- `data/cellular_automata/ca_nca_trained_repair_stage0.json`
- `data/cellular_automata/ca_nca_repair_context_ablation_stage0.json`
- `labs/cellular_automata/ca_nca_repair_context_ablation.py`
- `labs/cellular_automata/test_ca_nca_repair_context_ablation.py`
- `data/cellular_automata/samples/`
- `data/cellular_automata/stress_samples/`
- `data/cellular_automata/repeated_stress_samples/`
- `data/cellular_automata/learned_repair_samples/`
- `data/cellular_automata/trained_repair_samples/`
- `research/experiment_reports/2026-05-12-ca-nca-growth-repair.md`
- `research/experiment_reports/2026-05-12-ca-nca-persistence-damage-benchmark.md`
- `research/experiment_reports/2026-05-12-ca-nca-repeated-stochastic-damage.md`
- `research/experiment_reports/2026-05-12-ca-nca-learned-repair-comparison.md`
- `research/experiment_reports/2026-07-04-ca-nca-trained-neighborhood-repair.md`
- `research/experiment_reports/2026-07-04-ca-nca-repair-context-ablation.md`
- `research/experiment_reports/2026-07-04-ca-nca-wound-site-repair.md`

Measured result:

- Growth validity rate: 1.0
- Repair validity rate: 1.0
- Mean damaged overlap: 0.321388
- Mean growth overlap: 1.0
- Mean repair overlap: 1.0
- Mean readability delta after repair: 0.430918
- Mean lifecycle survival after repair: 1.0

Stress follow-up:

- Damage patterns: center_cut, left_sensor, lower_body
- Stress samples: 24
- Stress repair validity rate: 1.0
- Persistence validity rate: 1.0
- Mean damaged overlap across stress masks: 0.519015
- Mean repair overlap across stress masks: 1.0
- Mean persistence overlap after 12 idle ticks: 1.0
- Hardest deterministic mask: center_cut

Repeated stochastic damage follow-up:

- Samples: 8
- Cycles: 5
- Total damage events: 40
- Final validity rate: 1.0
- Mean final overlap: 1.0
- Mean final readability: 0.862129
- Mean final lifecycle survival: 1.0
- Mean removed cells per event: 2.675
- Mean repair gain per event: 0.205373

Learned repair comparison follow-up:

- Samples: 8
- Cycles: 5
- Total damage events: 40
- Assisted final validity rate: 1.0
- Learned final validity rate: 1.0
- Mean assisted final overlap: 1.0
- Mean learned final overlap: 0.778563
- Mean learned-vs-assisted final overlap delta: -0.221437
- Mean learned repair gain per event: 0.148998
- Learned final lifecycle survival: 1.0
- Target template used by learned repair: false

Gradient-trained repair follow-up (2026-07-04, held-out grids, 5 cycles at
dropout 0.2):

- Trained (blind) arm: final overlap 0.862546, structural agreement 0.631871,
  validity 1.0 — `meets_assisted_stability_bar = false` (the blocker's
  measured basis)
- Site-aware (wound-signal) arm — same trained model, additionally observing
  the damage event's destroyed positions, never the destroyed tokens, never a
  template: final overlap 0.930769, structural agreement 0.930769, validity
  0.9 — `site_aware_meets_assisted_stability_bar = true`. The single validity
  failure is `mg_seed_046` ("required body core is disconnected" after a
  wrong-token refill).
- Restricting refill to reported damage sites removes overgrowth by
  construction; the residual error is pure token prediction.

Context-conditioning ablation (2026-07-04, negative result, identical
protocol):

- Retrieval-context features: final overlap 0.802656 (worse than plain
  0.862546); self-play retraining: 0.809249; plus confidence pruning:
  0.801557; plain+self-play+prune: 0.838278 — every config degrades the
  plain trained rule.
- Exemplar-retrieval ceiling: the best training exemplar reaches only mean
  structural agreement 0.785 against held-out targets, bounding the entire
  retrieved-template repair family below the 0.9 bar on this corpus.

## Decision

Prototype as a discrete local-attractor growth, repair, and persistence lab
plus a gradient-trained wound-site repair rule. Do not adopt a trained NCA
dependency yet. Repeated stochastic damage is now part of the benchmark
contract. Blind (no-observability) learned repair remains below the assisted
stability bar, and retrieval-context conditioning is rejected as a measured
negative result. The wound-site arm meets the assisted stability bar without
any target template, so template assistance is no longer required for repair
stability when damage events report destroyed positions — an engine-native
signal. The repair candidate's `lab_only_target_template_assisted` blocker
now derives from `site_aware_meets_assisted_stability_bar`; the blind arm's
verdict stays recorded separately.
