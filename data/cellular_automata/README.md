# CA/NCA Growth, Repair, and Persistence Stage 0

Discrete NCA-inspired local-attractor lab for grid growth, damage repair,
post-repair idle persistence, and less-assisted repair comparison.

Key results:

- Growth/repair samples: 8
- Persistence stress samples: 24
- Repeated stochastic stress events: 40
- Learned repair comparison events: 40
- Growth validity rate: 1.0
- Repair validity rate: 1.0
- Persistence validity rate: 1.0
- Repeated stress final validity rate: 1.0
- Learned repair final validity rate: 1.0
- Mean damaged overlap: 0.321388
- Mean repair overlap: 1.0
- Mean stress damaged overlap: 0.519015
- Mean stress persistence overlap: 1.0
- Mean repeated stress final overlap: 1.0
- Mean learned repair final overlap: 0.778563
- Learned-vs-assisted final overlap delta: -0.221437
- Hardest deterministic stress mask: center_cut
- Decision: watch_learned_repair

This is not a trained neural cellular automaton. It is a measured local-rule
baseline for deciding whether growth and repair deserve a heavier NCA
implementation later. The learned role-prior comparison is less assisted than
the target-template baseline, but it does not beat the assisted repair contract.

Files:

- `ca_nca_growth_repair_stage0.json`
- `ca_nca_persistence_damage_stage0.json`
- `ca_nca_repeated_stochastic_damage_stage0.json`
- `ca_nca_learned_repair_comparison_stage0.json`
- `samples/`
- `stress_samples/`
- `repeated_stress_samples/`
- `learned_repair_samples/`
