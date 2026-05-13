# Experiment Report: Stage 0 and Stage 1 Kickoff

Date: 2026-05-12

## Objective

Begin the research phase defined by `docs/02-research_plan.md` by establishing
the active research structure, ontology, source map, first grid contract, and
algorithm cards.

## Work Performed

1. Reviewed `docs/01-brainstorming.md`.
2. Reviewed `docs/02-research_plan.md`.
3. Inventoried the existing shelved deep research report and source list.
4. Checked project state with Git; existing modified file:
   `docs/01-notes/01-prompts.md`.
5. Queried Serena project memory; no project memory existed.
6. Queried durable memory; no Mechagotchi hits existed.
7. Ran targeted web source review.
8. Queried Context7 for Pydantic schema/validation documentation.
9. Created initial `/research` evidence artifacts.

## Outputs Created

- `research/README.md`
- `research/questions.md`
- `research/glossary.md`
- `research/literature_map.md`
- `research/grid_genome/grid_genome.schema.json`
- `research/grid_genome/grid_invariants.md`
- `research/algorithm_cards/*.md`
- `research/source_notes/2026-05-12-primary-source-review.md`
- `research/decision_records/0001-research-ontology-and-first-sequence.md`
- `research/asset_provenance/ledger.schema.md`

## Findings

The existing project docs already converge on the right research stance:
Mechagotchi should be a semantic grid-genome companion engine, not a virtual-pet
clone or a procedural sprite toy.

The first measurable dependency is the grid genome and validator. Without that,
Markov, WFC, MAP-Elites, CUBFF, CTM, NCA, and workshop authoring cannot be
compared fairly.

## Open Work

1. Create 50 hand-authored seed grids. Done in `data/seed_grids/`.
2. Create 200 invalid counterexample grids. Done in `data/invalid_grids/`.
3. Implement the first validator lab. Done in `labs/grid_genome/validator.py`.
4. Emit a first validation report. Done in
   `research/experiment_reports/2026-05-12-grid-validator-baseline.md`.
5. Build the random mutation baseline. Done in
   `research/experiment_reports/2026-05-12-random-mutation-baseline.md`.
6. Build Markov and WFC generator labs. Raw Markov prototype is done in
   `research/experiment_reports/2026-05-12-markov-local-generator.md`;
   constrained WFC-style stabilization is done in
   `research/experiment_reports/2026-05-12-constrained-wfc-style-generator.md`.
7. Add SLIP constraints. First profile-constrained generation baseline is done
   in `research/experiment_reports/2026-05-12-slip-constraint-baseline.md`.
8. Build first MAP-Elites archive. First CPU archive baseline is done in
   `research/experiment_reports/2026-05-12-map-elites-archive-baseline.md`.
9. Add lineage tracking. First lineage graph baseline is done in
   `research/experiment_reports/2026-05-12-lineage-tracking-baseline.md`.
10. Build micro-learning switchboard. First interpretable switchboard baseline
    is done in
    `research/experiment_reports/2026-05-12-micro-switchboard-baseline.md`.
11. Run CUBFF semantic transducer lab. First synthetic CUBFF-style transducer
    baseline is done in
    `research/experiment_reports/2026-05-12-cubff-semantic-transducer-baseline.md`.
12. Build minimal workshop editor. First semantic workshop editor baseline is
    done in
    `research/experiment_reports/2026-05-12-workshop-editor-baseline.md`.
13. Add asset provenance ledger. First executable ledger and attribution
    manifest baseline is done in
    `research/experiment_reports/2026-05-12-asset-provenance-ledger-baseline.md`.
14. Publish research report v0.1. First consolidated research report is done in
    `research/reports/mechagotchi_research_report_v0_1.md`.

## Decision

The first research sequence has enough evidence to treat the semantic
grid-genome stack as the baseline architecture. Next research should move into
lifecycle simulation, held-out readability evaluation, archive descriptor
refinement, workshop round trips, real CuBFF snapshot ingestion, and provenance
CI.

## Post-v0.1 Continuation

1. Add lifecycle simulator. First baseline is done in
   `research/experiment_reports/2026-05-12-lifecycle-simulator-baseline.md`.
2. Add held-out readability benchmark and manual rating protocol. First
   baseline is done in
   `research/experiment_reports/2026-05-12-readability-benchmark-baseline.md`.
3. Extend MAP-Elites descriptors beyond body mass, sensors, and symmetry. First
   extended descriptor archive is done in
   `research/experiment_reports/2026-05-12-map-elites-extended-descriptors.md`.
4. Add workshop import/export round trips. First native semantic round-trip
   baseline is done in
   `research/experiment_reports/2026-05-12-workshop-roundtrip-baseline.md`.
5. Ingest real CuBFF snapshots before revisiting CUBFF adoption. The ingest
   contract and upstream snapshot audit are done in
   `research/experiment_reports/2026-05-12-cubff-real-snapshot-ingest.md`, but
   the adoption gate remains blocked because no real CuBFF snapshot artifacts
   were available in the official repo or local drop zone.
6. Add provenance CI checks and SPDX expression parsing. First CI report and
   parser baseline is done in
   `research/experiment_reports/2026-05-12-provenance-ci-spdx-parser.md`.
7. Start CA/NCA growth and repair after lifecycle metrics exist. First
   discrete local-attractor baseline is done in
   `research/experiment_reports/2026-05-12-ca-nca-growth-repair.md`.
8. Stress CA/NCA repair with multiple deterministic damage masks and idle
   persistence. First follow-up benchmark is done in
   `research/experiment_reports/2026-05-12-ca-nca-persistence-damage-benchmark.md`.
9. Prototype CTM-inspired internal ticks as a confidence-gated switchboard
   wrapper. First benchmark is done in
   `research/experiment_reports/2026-05-12-ctm-inspired-internal-ticks.md`.
10. Publish the post-v0.1 consolidated research report. Done in
    `research/reports/mechagotchi_research_report_v0_2.md`.
11. Connect switchboard action rewards back to lifecycle outcomes. First
    feedback-loop benchmark is done in
    `research/experiment_reports/2026-05-12-switchboard-lifecycle-feedback.md`.
12. Create the manual readability rating intake and aggregation gate. First
    template/intake report is done in
    `research/experiment_reports/2026-05-12-manual-readability-rating-intake.md`.
13. Add repeated stochastic damage to the CA/NCA benchmark. First repeated
    dropout stress report is done in
    `research/experiment_reports/2026-05-12-ca-nca-repeated-stochastic-damage.md`.
14. Define package promotion criteria for `packages/mecha_engine`. First gate
    and decision record are done in
    `research/experiment_reports/2026-05-12-mecha-engine-package-promotion-gate.md`
    and
    `research/decision_records/0002-mecha-engine-package-promotion-gate.md`.
15. Produce the MVP architecture decision record from the v0.1 and v0.2
    reports. Done in
    `research/experiment_reports/2026-05-12-mvp-architecture-decision.md`
    and `research/decision_records/0003-mvp-architecture.md`.
16. Publish the post-v0.2 wrap-up report. Done in
    `research/reports/mechagotchi_research_report_v0_3.md`.
17. Create package module interface specs for `genome`, `generation`,
    `lifecycle`, `archive`, and `provenance`. Done in
    `research/package_specs/mecha_engine_module_interfaces.md`.
18. Recheck manual readability ratings. Still blocked because no filled
    reviewer CSV exists; recorded in
    `research/experiment_reports/2026-05-12-manual-readability-rating-recheck.md`.
19. Stress switchboard feedback under changing needs and user-interaction
    patterns. Dynamic stress benchmark is done in
    `research/experiment_reports/2026-05-12-switchboard-feedback-dynamic-stress.md`.
20. Compare a less-assisted learned repair rule against the assisted CA/NCA
    repair baseline. First role-prior comparison is done in
    `research/experiment_reports/2026-05-12-ca-nca-learned-repair-comparison.md`.
21. Produce a package-scaffold decision record before creating
    `packages/mecha_engine`. Scaffold design is accepted and package creation
    is deferred in
    `research/decision_records/0004-mecha-engine-package-scaffold.md`.
22. Publish the post-v0.3 wrap-up report. Done in
    `research/reports/mechagotchi_research_report_v0_4.md`.
23. Define the scaffold verification and package import-surface acceptance
    gate before creating `packages/mecha_engine`. Done in
    `research/package_specs/mecha_engine_scaffold_verification_gate.md`.
24. Prepare the manual readability reviewer packet and collection gate. Packet
    is ready, but human ratings remain absent until
    `data/readability/manual_ratings.csv` is filled; recorded in
    `research/experiment_reports/2026-05-12-manual-readability-reviewer-packet.md`.
25. Define the `mecha_engine.genome` package contract and validator acceptance
    gate before moving grid-genome code out of `labs/`. Done in
    `research/package_specs/mecha_engine_genome_contract_gate.md` and
    `research/experiment_reports/2026-05-12-mecha-engine-genome-contract-gate.md`.
26. Define the `mecha_engine.generation` package contract and constrained
    generator acceptance gate before moving generator code out of `labs/`. Done
    in `research/package_specs/mecha_engine_generation_contract_gate.md` and
    `research/experiment_reports/2026-05-12-mecha-engine-generation-contract-gate.md`.
27. Define the `mecha_engine.lifecycle` package contract and bounded simulator
    acceptance gate before moving lifecycle code out of `labs/`. Done in
    `research/package_specs/mecha_engine_lifecycle_contract_gate.md` and
    `research/experiment_reports/2026-05-12-mecha-engine-lifecycle-contract-gate.md`.
28. Define the `mecha_engine.archive` package contract and MAP-Elites
    acceptance gate before moving archive code out of `labs/`. Done in
    `research/package_specs/mecha_engine_archive_contract_gate.md` and
    `research/experiment_reports/2026-05-12-mecha-engine-archive-contract-gate.md`.
29. Define the `mecha_engine.provenance` package contract and provenance CI
    acceptance gate before moving asset-pipeline code out of `labs/`. Done in
    `research/package_specs/mecha_engine_provenance_contract_gate.md` and
    `research/experiment_reports/2026-05-12-mecha-engine-provenance-contract-gate.md`.
30. Publish the post-v0.4 package-contract handoff report after scaffold,
    genome, generation, lifecycle, archive, and provenance gates are defined.
    Done in `research/reports/mechagotchi_research_report_v0_5.md` and
    `research/reports/research_report_v0_5_manifest.json`.
31. Translate the scaffold and module contract gates into future package test
    obligations before implementation starts. Done in
    `research/package_specs/mecha_engine_contract_traceability_matrix.md` and
    `research/experiment_reports/2026-05-12-mecha-engine-contract-traceability-matrix.md`.
32. Inventory the concrete repository fixtures that future package tests must
    use. Done in `research/package_specs/mecha_engine_test_fixture_manifest.md`
    and
    `research/experiment_reports/2026-05-12-mecha-engine-test-fixture-manifest.md`.
33. Define the formal cross-module invariant, dependency, and failure
    propagation gate before package implementation starts. Done in
    `research/package_specs/mecha_engine_formal_invariant_dependency_gate.md`
    and
    `research/experiment_reports/2026-05-12-mecha-engine-formal-invariant-dependency-gate.md`.
34. Define the property-style, metamorphic, and single-fault negative test
    strategy for future package gates before package implementation starts.
    Done in
    `research/package_specs/mecha_engine_property_negative_test_strategy.md`
    and
    `research/experiment_reports/2026-05-12-mecha-engine-property-negative-test-strategy.md`.
35. Define the Stage 0 SLIP profile compatibility test matrix required by the
    research plan. Done in `research/slip/profile_compatibility_tests.md` and
    `research/experiment_reports/2026-05-12-slip-profile-compatibility-matrix.md`.
36. Run the multi-profile SLIP generation compatibility benchmark called out by
    the matrix. Done in
    `research/experiment_reports/2026-05-12-slip-multi-profile-generation-benchmark.md`
    and
    `data/slips/multi_profile_generation_stage0/slip_multi_profile_generation_stage0.json`.
37. Extend native workshop round trips across the generated multi-profile SLIP
    corpora. Done in
    `research/experiment_reports/2026-05-12-workshop-multi-profile-roundtrip.md`
    and
    `data/workshop_editor/multi_profile_roundtrip_stage0/workshop_multi_profile_roundtrip_stage0.json`.
38. Author the versioned Stage 0 SLIP schema and expanded failure-case corpus.
    Done in
    `research/experiment_reports/2026-05-12-slip-schema-failure-corpus.md`,
    `research/slip/slip.schema.json`, `research/slip/slip_examples/`,
    `research/slip/slip_failure_cases.md`, and
    `data/slips/slip_schema_validation_stage0.json`.
39. Add the Stage 0 Pydantic model contract gate for SLIP profiles. Done in
    `research/experiment_reports/2026-05-12-slip-pydantic-contract-gate.md`,
    `research/slip/pydantic_contract.md`,
    `research/slip/slip_pydantic_model.schema.json`, and
    `data/slips/slip_pydantic_contract_stage0.json`.
40. Define the Stage 0 SLIP schema migration and runtime dependency gate. Done
    in
    `research/experiment_reports/2026-05-12-slip-schema-migration-dependency-gate.md`,
    `research/slip/schema_migration_dependency_gate.md`, and
    `data/slips/slip_schema_migration_dependency_gate_stage0.json`.
41. Build the minimal Stage 0 SLIP profile-authoring panel against the current
    schema, Pydantic contract, and migration policy. Done in
    `research/experiment_reports/2026-05-12-slip-authoring-panel.md`,
    `labs/workshop_editor/slip_authoring_panel.py`, and
    `data/workshop_editor/slip_authoring_panel_stage0.json`.
42. Add the deterministic Stage 0 SLIP behavior and mutation preview gate.
    Done in
    `research/experiment_reports/2026-05-12-slip-behavior-mutation-preview-gate.md`,
    `labs/workshop_editor/slip_preview_gates.py`, and
    `data/workshop_editor/slip_behavior_mutation_preview_stage0.json`.
43. Define the Stage 0 external metadata sidecar strategy for non-native image
    and project imports. Done in
    `research/experiment_reports/2026-05-12-external-metadata-sidecar-strategy.md`,
    `labs/workshop_editor/external_metadata_sidecar.py`, and
    `data/workshop_editor/external_metadata_sidecar_stage0.json`.
44. Build the Stage 0 standard-image sidecar decoder for static RGBA PNG
    import/export. Done in
    `research/experiment_reports/2026-05-12-standard-image-sidecar-decoder.md`,
    `labs/workshop_editor/standard_image_sidecar_decoder.py`, and
    `data/workshop_editor/standard_image_sidecar_decoder_stage0.json`.
45. Build the Stage 0 spritesheet sidecar decoder for fixed horizontal
    spritesheet PNG import/export. Done in
    `research/experiment_reports/2026-05-12-spritesheet-sidecar-decoder.md`,
    `labs/workshop_editor/spritesheet_sidecar_decoder.py`, and
    `data/workshop_editor/spritesheet_sidecar_decoder_stage0.json`.
46. Connect deterministic SLIP preview signals to measured lifecycle and
    extended archive effects without claiming runtime profile-weighted
    evolution. Done in
    `research/experiment_reports/2026-05-12-slip-lifecycle-archive-effects.md`,
    `labs/workshop_editor/slip_lifecycle_archive_effects.py`, and
    `data/workshop_editor/slip_lifecycle_archive_effects_stage0.json`.
47. Build the Stage 0 third-party project decoder boundary for sidecar-bound
    Piskel JSON, Pixelorama `.pxo`, and Aseprite/LibreSprite header imports.
    Done in
    `research/experiment_reports/2026-05-13-third-party-project-decoder-boundary.md`,
    `labs/workshop_editor/third_party_project_decoder.py`, and
    `data/workshop_editor/third_party_project_decoder_stage0.json`.
48. Build the Stage 0 PNG variant sidecar decoder for 8-bit non-interlaced PNG
    color/filter variants. Done in
    `research/experiment_reports/2026-05-13-png-variant-sidecar-decoder.md`,
    `labs/workshop_editor/png_variant_sidecar_decoder.py`, and
    `data/workshop_editor/png_variant_sidecar_decoder_stage0.json`.
49. Build the Stage 0 spritesheet layout variant sidecar decoder for vertical,
    matrix, padded/guttered, and sparse-atlas spritesheet import/export. Done
    in
    `research/experiment_reports/2026-05-13-spritesheet-layout-variant-decoder.md`,
    `labs/workshop_editor/spritesheet_layout_variant_decoder.py`, and
    `data/workshop_editor/spritesheet_layout_variant_decoder_stage0.json`.
50. Specify and test the Stage 0 SLIP runtime lifecycle/archive selection
    policy without claiming profile-weighted evolution. Done in
    `research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`,
    `research/algorithm_cards/slip_runtime_selection_policy.md`,
    `labs/workshop_editor/slip_runtime_selection_policy.py`, and
    `data/workshop_editor/slip_runtime_selection_policy_stage0.json`.
51. Specify and test bounded Stage 0 offspring mutation selection and lineage
    replacement decisions without claiming persistent profile-weighted
    evolution. Done in
    `research/experiment_reports/2026-05-13-slip-offspring-lineage-gate.md`,
    `research/algorithm_cards/slip_offspring_lineage_gate.md`,
    `labs/workshop_editor/slip_offspring_lineage_gate.py`, and
    `data/workshop_editor/slip_offspring_lineage_gate_stage0.json`.
52. Run held-out Stage 0 long-horizon behavior tests for selected offspring
    and generated candidates without claiming manual readability calibration or
    profile-weighted evolution. Done in
    `research/experiment_reports/2026-05-13-slip-long-horizon-behavior-gate.md`,
    `research/algorithm_cards/slip_long_horizon_behavior_gate.md`,
    `labs/workshop_editor/slip_long_horizon_behavior_gate.py`, and
    `data/workshop_editor/slip_long_horizon_behavior_gate_stage0.json`.
53. Prepare the current SLIP long-horizon corpus for manual readability
    calibration without fabricating reviewer rows or claiming
    profile-weighted evolution. Done in
    `research/experiment_reports/2026-05-13-slip-readability-calibration-gate.md`,
    `research/algorithm_cards/slip_readability_calibration_gate.md`,
    `labs/readability_benchmark/slip_readability_calibration_gate.py`, and
    `data/readability/slip_readability_calibration_gate_stage0.json`.
54. Run a lab-only persistent SLIP multigeneration lineage runner without
    claiming package runtime integration or profile-weighted evolution. Done in
    `research/experiment_reports/2026-05-13-slip-multigeneration-lineage-runner.md`,
    `research/algorithm_cards/slip_multigeneration_lineage_runner.md`,
    `labs/workshop_editor/slip_multigeneration_lineage_runner.py`, and
    `data/workshop_editor/slip_multigeneration_lineage_runner_stage0.json`.
