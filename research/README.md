# Mechagotchi Research

This folder is the active research workspace defined by
`docs/02-research_plan.md`.

The research standard is:

1. Read or inspect the source.
2. Extract usable theory.
3. Build the smallest lab prototype.
4. Measure output against a baseline.
5. Record failures.
6. Decide: reject, watch, prototype, or adopt.

The first research sequence is published as:

- `research/reports/mechagotchi_research_report_v0_1.md`
- `research/reports/research_report_v0_1_manifest.json`

Post-v0.1 continuation has started:

- `research/experiment_reports/2026-05-12-lifecycle-simulator-baseline.md`
- `research/algorithm_cards/lifecycle_simulator.md`
- `data/lifecycle/lifecycle_stage0.json`
- `research/experiment_reports/2026-05-12-readability-benchmark-baseline.md`
- `research/algorithm_cards/readability_benchmark.md`
- `data/readability/readability_stage0.json`
- `data/readability/manual_rating_protocol.md`
- `research/experiment_reports/2026-05-12-map-elites-extended-descriptors.md`
- `research/algorithm_cards/map_elites_extended_descriptors.md`
- `data/archives/map_elites_extended_stage0.json`
- `research/experiment_reports/2026-05-12-workshop-roundtrip-baseline.md`
- `research/algorithm_cards/workshop_roundtrip_io.md`
- `data/workshop_editor/workshop_roundtrip_stage0_report.json`

Stage 0 and Stage 1 established:

- Stage 0: define the research ontology and evaluation vocabulary.
- Stage 1: turn the source list into a structured literature map.

No algorithm should graduate into `packages/` until it has an algorithm card,
an experiment report, a metric report, and a decision record.
