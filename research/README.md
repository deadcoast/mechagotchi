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

Stage 0 baseline triads from that sequence (backfilled into this ledger on
2026-07-04; traceability previously held only via the v0_1/v0_2 manifests):

- `research/experiment_reports/2026-05-12-grid-validator-baseline.md`
- `data/seed_grids/` and `data/invalid_grids/` (validator fixture corpora)
- `research/experiment_reports/2026-05-12-random-mutation-baseline.md`
- `research/algorithm_cards/random_mutation_baseline.md`
- `research/experiment_reports/2026-05-12-markov-local-generator.md`
- `research/algorithm_cards/markov_grid.md`
- `research/experiment_reports/2026-05-12-constrained-wfc-style-generator.md`
- `research/experiment_reports/2026-05-12-map-elites-archive-baseline.md`
- `research/algorithm_cards/map_elites.md`
- `data/archives/map_elites_stage0.json`
- `research/experiment_reports/2026-05-12-lineage-tracking-baseline.md`
- `research/algorithm_cards/lineage_tracking.md`
- `research/experiment_reports/2026-05-12-micro-switchboard-baseline.md`
- `research/algorithm_cards/micro_learning_switchboard.md`
- `research/experiment_reports/2026-05-12-slip-constraint-baseline.md`
- `research/experiment_reports/2026-05-12-asset-provenance-ledger-baseline.md`
- `research/algorithm_cards/provenance_ci_spdx.md`
- `data/asset_provenance/ledger.json`
- `research/experiment_reports/2026-05-12-cubff-semantic-transducer-baseline.md`
- `research/algorithm_cards/cubff_transducer.md`
- `research/experiment_reports/2026-05-12-workshop-editor-baseline.md`
- `research/algorithm_cards/workshop_roundtrip_io.md`

Note: several early lab modules are ledgered under report slugs that differ
from the module filename (e.g. `labs/grid_genome/validator.py` under
`grid-validator-baseline`, `labs/grid_genome/slip.py` under
`slip-constraint-baseline`). New triads should keep report, card, lab, and
artifact stems aligned.

The post-v0.1 continuation is published as:

- `research/reports/mechagotchi_research_report_v0_2.md`
- `research/reports/research_report_v0_2_manifest.json`

The post-v0.2 wrap-up is published as:

- `research/reports/mechagotchi_research_report_v0_3.md`
- `research/reports/research_report_v0_3_manifest.json`

The post-v0.3 wrap-up is published as:

- `research/reports/mechagotchi_research_report_v0_4.md`
- `research/reports/research_report_v0_4_manifest.json`

The package-contract handoff is published as:

- `research/reports/mechagotchi_research_report_v0_5.md`
- `research/reports/research_report_v0_5_manifest.json`
- `research/experiment_reports/2026-05-12-mecha-engine-contract-traceability-matrix.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `data/architecture/mecha_engine_contract_traceability_matrix_stage0.json`
- `research/experiment_reports/2026-05-12-mecha-engine-test-fixture-manifest.md`
- `research/package_specs/mecha_engine_test_fixture_manifest.md`
- `data/architecture/mecha_engine_test_fixture_manifest_stage0.json`
- `research/experiment_reports/2026-05-12-mecha-engine-formal-invariant-dependency-gate.md`
- `research/package_specs/mecha_engine_formal_invariant_dependency_gate.md`
- `data/architecture/mecha_engine_formal_invariant_dependency_gate_stage0.json`
- `research/experiment_reports/2026-05-13-mecha-engine-runtime-boundary-gate.md`
- `research/package_specs/mecha_engine_runtime_boundary_gate.md`
- `data/architecture/mecha_engine_runtime_boundary_gate_stage0.json`
- `research/experiment_reports/2026-05-12-mecha-engine-property-negative-test-strategy.md`
- `research/package_specs/mecha_engine_property_negative_test_strategy.md`
- `data/architecture/mecha_engine_property_negative_test_strategy_stage0.json`
- `research/experiment_reports/2026-05-12-slip-profile-compatibility-matrix.md`
- `research/slip/profile_compatibility_tests.md`
- `data/slips/slip_profile_compatibility_matrix_stage0.json`
- `research/experiment_reports/2026-05-12-slip-multi-profile-generation-benchmark.md`
- `data/slips/multi_profile_generation_stage0/slip_multi_profile_generation_stage0.json`
- `research/experiment_reports/2026-05-12-workshop-multi-profile-roundtrip.md`
- `data/workshop_editor/multi_profile_roundtrip_stage0/workshop_multi_profile_roundtrip_stage0.json`
- `research/experiment_reports/2026-05-12-slip-schema-failure-corpus.md`
- `research/slip/slip.schema.json`
- `research/slip/slip_examples/`
- `research/slip/slip_failure_cases.md`
- `data/slips/slip_schema_validation_stage0.json`
- `research/experiment_reports/2026-05-12-slip-pydantic-contract-gate.md`
- `research/slip/pydantic_contract.md`
- `research/slip/slip_pydantic_model.schema.json`
- `data/slips/slip_pydantic_contract_stage0.json`
- `research/experiment_reports/2026-05-12-slip-schema-migration-dependency-gate.md`
- `research/slip/schema_migration_dependency_gate.md`
- `data/slips/slip_schema_migration_dependency_gate_stage0.json`
- `research/experiment_reports/2026-05-12-slip-authoring-panel.md`
- `data/workshop_editor/slip_authoring_panel_stage0.json`
- `research/experiment_reports/2026-05-12-slip-behavior-mutation-preview-gate.md`
- `data/workshop_editor/slip_behavior_mutation_preview_stage0.json`
- `research/experiment_reports/2026-05-12-slip-lifecycle-archive-effects.md`
- `data/workshop_editor/slip_lifecycle_archive_effects_stage0.json`
- `research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`
- `research/algorithm_cards/slip_runtime_selection_policy.md`
- `data/workshop_editor/slip_runtime_selection_policy_stage0.json`
- `research/experiment_reports/2026-05-13-slip-offspring-lineage-gate.md`
- `research/algorithm_cards/slip_offspring_lineage_gate.md`
- `data/workshop_editor/slip_offspring_lineage_gate_stage0.json`
- `research/experiment_reports/2026-05-13-slip-long-horizon-behavior-gate.md`
- `research/algorithm_cards/slip_long_horizon_behavior_gate.md`
- `data/workshop_editor/slip_long_horizon_behavior_gate_stage0.json`
- `research/experiment_reports/2026-05-13-slip-readability-calibration-gate.md`
- `research/algorithm_cards/slip_readability_calibration_gate.md`
- `data/readability/slip_readability_calibration_gate_stage0.json`
- `research/experiment_reports/2026-05-13-slip-multigeneration-lineage-runner.md`
- `research/algorithm_cards/slip_multigeneration_lineage_runner.md`
- `data/workshop_editor/slip_multigeneration_lineage_runner_stage0.json`
- `research/experiment_reports/2026-05-12-external-metadata-sidecar-strategy.md`
- `data/workshop_editor/external_metadata_sidecar_stage0.json`
- `research/experiment_reports/2026-05-12-standard-image-sidecar-decoder.md`
- `data/workshop_editor/standard_image_sidecar_decoder_stage0.json`
- `research/experiment_reports/2026-05-13-png-variant-sidecar-decoder.md`
- `data/workshop_editor/png_variant_sidecar_decoder_stage0.json`
- `research/experiment_reports/2026-05-14-png-adam7-interlace-decoder.md`
- `research/algorithm_cards/png_adam7_interlace_decoder.md`
- `data/workshop_editor/png_adam7_interlace_decoder_stage0.json`
- `research/experiment_reports/2026-05-13-png-embedded-sidecar-writer.md`
- `research/algorithm_cards/png_embedded_sidecar_writer.md`
- `data/workshop_editor/png_embedded_sidecar_writer_stage0.json`
- `research/experiment_reports/2026-05-14-png-textual-metadata-policy.md`
- `research/algorithm_cards/png_textual_metadata_policy.md`
- `data/workshop_editor/png_textual_metadata_policy_stage0.json`
- `research/experiment_reports/2026-05-14-png-private-chunk-policy.md`
- `research/algorithm_cards/png_private_chunk_policy.md`
- `data/workshop_editor/png_private_chunk_policy_stage0.json`
- `research/experiment_reports/2026-05-14-png-private-chunk-preservation-matrix.md`
- `research/algorithm_cards/png_private_chunk_preservation_matrix.md`
- `data/workshop_editor/png_private_chunk_preservation_matrix_stage0.json`
- `research/experiment_reports/2026-05-14-apng-sidecar-decoder.md`
- `research/algorithm_cards/png_apng_sidecar_decoder.md`
- `data/workshop_editor/apng_sidecar_decoder_stage0.json`
- `research/experiment_reports/2026-05-14-apng-metadata-carrier-cross-product.md`
- `research/algorithm_cards/png_apng_metadata_carrier_cross_product.md`
- `data/workshop_editor/apng_metadata_carrier_cross_product_stage0.json`
- `research/experiment_reports/2026-05-12-spritesheet-sidecar-decoder.md`
- `data/workshop_editor/spritesheet_sidecar_decoder_stage0.json`
- `research/experiment_reports/2026-05-13-spritesheet-layout-variant-decoder.md`
- `data/workshop_editor/spritesheet_layout_variant_decoder_stage0.json`
- `research/experiment_reports/2026-05-13-spritesheet-packed-runtime-decoder.md`
- `research/algorithm_cards/spritesheet_packed_runtime_decoder.md`
- `data/workshop_editor/spritesheet_packed_runtime_decoder_stage0.json`
- `research/experiment_reports/2026-05-14-spritesheet-arbitrary-atlas-packer.md`
- `research/algorithm_cards/spritesheet_arbitrary_atlas_packer.md`
- `data/workshop_editor/spritesheet_arbitrary_atlas_packer_stage0.json`
- `research/experiment_reports/2026-05-14-spritesheet-multi-page-atlas.md`
- `research/algorithm_cards/spritesheet_multi_page_atlas.md`
- `data/workshop_editor/spritesheet_multi_page_atlas_stage0.json`
- `research/experiment_reports/2026-05-13-third-party-project-decoder-boundary.md`
- `data/workshop_editor/third_party_project_decoder_stage0.json`
- `research/experiment_reports/2026-05-13-project-native-metadata-writer.md`
- `research/algorithm_cards/project_native_metadata_writer.md`
- `data/workshop_editor/project_native_metadata_writer_stage0.json`
- `research/experiment_reports/2026-05-13-project-editor-rewrite-preservation.md`
- `research/algorithm_cards/project_editor_rewrite_preservation.md`
- `data/workshop_editor/project_editor_rewrite_preservation_stage0.json`
- `research/experiment_reports/2026-05-14-aseprite-user-data-chunk-writer.md`
- `research/algorithm_cards/aseprite_user_data_chunk_writer.md`
- `data/workshop_editor/aseprite_user_data_chunk_writer_stage0.json`
- `research/experiment_reports/2026-05-14-aseprite-tags-layers-semantics.md`
- `research/algorithm_cards/aseprite_tags_layers_semantics.md`
- `data/workshop_editor/aseprite_tags_layers_semantics_stage0.json`
- `research/experiment_reports/2026-05-14-aseprite-palette-slice-semantics.md`
- `research/algorithm_cards/aseprite_palette_slice_semantics.md`
- `data/workshop_editor/aseprite_palette_slice_semantics_stage0.json`
- `research/experiment_reports/2026-05-14-aseprite-linked-cel-semantics.md`
- `research/algorithm_cards/aseprite_linked_cel_semantics.md`
- `data/workshop_editor/aseprite_linked_cel_semantics_stage0.json`
- `research/experiment_reports/2026-05-14-aseprite-tilemap-tileset-semantics.md`
- `research/algorithm_cards/aseprite_tilemap_tileset_semantics.md`
- `data/workshop_editor/aseprite_tilemap_tileset_semantics_stage0.json`
- `research/experiment_reports/2026-05-14-aseprite-nested-timeline-semantics.md`
- `research/algorithm_cards/aseprite_nested_timeline_semantics.md`
- `data/workshop_editor/aseprite_nested_timeline_semantics_stage0.json`
- `research/experiment_reports/2026-05-14-aseprite-external-properties-semantics.md`
- `research/algorithm_cards/aseprite_external_properties_semantics.md`
- `data/workshop_editor/aseprite_external_properties_semantics_stage0.json`
- `research/experiment_reports/2026-05-14-aseprite-document-variant-resolution.md`
- `research/algorithm_cards/aseprite_document_variant_resolution.md`
- `data/workshop_editor/aseprite_document_variant_resolution_stage0.json`
- `research/experiment_reports/2026-05-14-aseprite-external-asset-resolver-matrix.md`
- `research/algorithm_cards/aseprite_external_asset_resolver_matrix.md`
- `data/workshop_editor/aseprite_external_asset_resolver_matrix_stage0.json`
- `research/experiment_reports/2026-05-14-png-apng-chunk-order-conformance.md`
- `research/algorithm_cards/png_apng_chunk_order_conformance.md`
- `data/workshop_editor/png_apng_chunk_order_conformance_stage0.json`
- `research/experiment_reports/2026-05-14-apng-partial-frame-playback.md`
- `research/algorithm_cards/png_apng_partial_frame_playback.md`
- `data/workshop_editor/apng_partial_frame_playback_stage0.json`
- `research/experiment_reports/2026-05-14-apng-filtered-frame-data.md`
- `research/algorithm_cards/png_apng_filtered_frame_data.md`
- `data/workshop_editor/apng_filtered_frame_data_stage0.json`
- `research/experiment_reports/2026-05-14-apng-color-type-frame-data.md`
- `research/algorithm_cards/png_apng_color_type_frame_data.md`
- `data/workshop_editor/apng_color_type_frame_data_stage0.json`
- `research/experiment_reports/2026-05-14-apng-bit-depth-frame-data.md`
- `research/algorithm_cards/png_apng_bit_depth_frame_data.md`
- `data/workshop_editor/apng_bit_depth_frame_data_stage0.json`
- `research/experiment_reports/2026-05-14-apng-partial-sample-frame-data.md`
- `research/algorithm_cards/png_apng_partial_sample_frame_data.md`
- `data/workshop_editor/apng_partial_sample_frame_data_stage0.json`
- `research/experiment_reports/2026-05-14-apng-adam7-frame-data.md`
- `research/algorithm_cards/png_apng_adam7_frame_data.md`
- `data/workshop_editor/apng_adam7_frame_data_stage0.json`
- `research/experiment_reports/2026-05-14-apng-partial-adam7-frame-data.md`
- `research/algorithm_cards/png_apng_partial_adam7_frame_data.md`
- `data/workshop_editor/apng_partial_adam7_frame_data_stage0.json`
- `research/experiment_reports/2026-05-14-png-apng-image-data-chunking.md`
- `research/algorithm_cards/png_apng_image_data_chunking.md`
- `data/workshop_editor/png_apng_image_data_chunking_stage0.json`
- `research/experiment_reports/2026-05-14-png-apng-zlib-compression-matrix.md`
- `research/algorithm_cards/png_apng_zlib_compression_matrix.md`
- `data/workshop_editor/png_apng_zlib_compression_stage0.json`
- `research/experiment_reports/2026-05-14-png-apng-zlib-header-policy.md`
- `research/algorithm_cards/png_apng_zlib_header_policy.md`
- `data/workshop_editor/png_apng_zlib_header_policy_stage0.json`

Post-v0.1 continuation has started:

- `research/experiment_reports/2026-05-12-lifecycle-simulator-baseline.md`
- `research/algorithm_cards/lifecycle_simulator.md`
- `data/lifecycle/lifecycle_stage0.json`
- `research/experiment_reports/2026-05-12-readability-benchmark-baseline.md`
- `research/algorithm_cards/readability_benchmark.md`
- `data/readability/readability_stage0.json`
- `data/readability/manual_rating_protocol.md`
- `research/experiment_reports/2026-05-12-manual-readability-rating-intake.md`
- `data/readability/manual_readability_rating_intake_stage0.json`
- `data/readability/manual_rating_template.csv`
- `research/experiment_reports/2026-05-12-manual-readability-rating-recheck.md`
- `data/readability/manual_rating_recheck_stage0.json`
- `research/experiment_reports/2026-05-12-manual-readability-reviewer-packet.md`
- `data/readability/manual_rating_reviewer_packet.md`
- `data/readability/manual_rating_collection_gate_stage0.json`
- `research/experiment_reports/2026-05-13-slip-readability-calibration-gate.md`
- `research/algorithm_cards/slip_readability_calibration_gate.md`
- `data/readability/slip_readability_calibration_gate_stage0.json`
- `data/readability/slip_readability_calibration_template.csv`
- `research/experiment_reports/2026-05-13-slip-multigeneration-lineage-runner.md`
- `research/algorithm_cards/slip_multigeneration_lineage_runner.md`
- `data/workshop_editor/slip_multigeneration_lineage_runner_stage0.json`
- `research/experiment_reports/2026-05-13-mecha-engine-runtime-boundary-gate.md`
- `research/package_specs/mecha_engine_runtime_boundary_gate.md`
- `data/architecture/mecha_engine_runtime_boundary_gate_stage0.json`
- `research/experiment_reports/2026-05-12-map-elites-extended-descriptors.md`
- `research/algorithm_cards/map_elites_extended_descriptors.md`
- `data/archives/map_elites_extended_stage0.json`
- `research/experiment_reports/2026-05-12-workshop-roundtrip-baseline.md`
- `research/algorithm_cards/workshop_roundtrip_io.md`
- `data/workshop_editor/workshop_roundtrip_stage0_report.json`
- `research/experiment_reports/2026-05-12-cubff-real-snapshot-ingest.md`
- `research/algorithm_cards/cubff_real_snapshot_ingest.md`
- `data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json`
- `research/experiment_reports/2026-05-12-provenance-ci-spdx-parser.md`
- `research/algorithm_cards/provenance_ci_spdx.md`
- `data/asset_provenance/provenance_ci_report.json`
- `research/experiment_reports/2026-05-12-ca-nca-growth-repair.md`
- `research/algorithm_cards/ca_nca_growth_repair.md`
- `data/cellular_automata/ca_nca_growth_repair_stage0.json`
- `research/experiment_reports/2026-05-12-ca-nca-persistence-damage-benchmark.md`
- `data/cellular_automata/ca_nca_persistence_damage_stage0.json`
- `research/experiment_reports/2026-05-12-ca-nca-repeated-stochastic-damage.md`
- `data/cellular_automata/ca_nca_repeated_stochastic_damage_stage0.json`
- `research/experiment_reports/2026-05-12-ca-nca-learned-repair-comparison.md`
- `data/cellular_automata/ca_nca_learned_repair_comparison_stage0.json`
- `research/experiment_reports/2026-05-12-ctm-inspired-internal-ticks.md`
- `research/algorithm_cards/ctm_inspired_ticks.md`
- `data/ctm_ticks/ctm_inspired_ticks_stage0.json`
- `research/experiment_reports/2026-05-12-switchboard-lifecycle-feedback.md`
- `research/algorithm_cards/micro_learning_switchboard.md`
- `data/micro_learners/switchboard_lifecycle_feedback_stage0.json`
- `research/experiment_reports/2026-05-12-switchboard-feedback-dynamic-stress.md`
- `data/micro_learners/switchboard_feedback_dynamic_stress_stage0.json`
- `research/experiment_reports/2026-05-12-mecha-engine-package-promotion-gate.md`
- `research/decision_records/0002-mecha-engine-package-promotion-gate.md`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- `data/package_promotion/mecha_engine_package_promotion_criteria.md`
- `research/experiment_reports/2026-05-12-mvp-architecture-decision.md`
- `research/decision_records/0003-mvp-architecture.md`
- `data/architecture/mvp_architecture_decision_stage0.json`
- `research/experiment_reports/2026-05-12-mecha-engine-module-interface-specs.md`
- `research/package_specs/README.md`
- `research/package_specs/mecha_engine_module_interfaces.md`
- `data/architecture/mecha_engine_module_interface_specs_stage0.json`
- `research/experiment_reports/2026-05-12-mecha-engine-package-scaffold-decision.md`
- `research/decision_records/0004-mecha-engine-package-scaffold.md`
- `data/architecture/mecha_engine_package_scaffold_decision_stage0.json`
- `research/reports/mechagotchi_research_report_v0_4.md`
- `research/reports/research_report_v0_4_manifest.json`
- `research/experiment_reports/2026-05-12-mecha-engine-scaffold-verification-gate.md`
- `research/package_specs/mecha_engine_scaffold_verification_gate.md`
- `data/architecture/mecha_engine_scaffold_verification_gate_stage0.json`
- `research/experiment_reports/2026-05-12-mecha-engine-genome-contract-gate.md`
- `research/package_specs/mecha_engine_genome_contract_gate.md`
- `data/architecture/mecha_engine_genome_contract_gate_stage0.json`
- `research/experiment_reports/2026-05-12-mecha-engine-generation-contract-gate.md`
- `research/package_specs/mecha_engine_generation_contract_gate.md`
- `data/architecture/mecha_engine_generation_contract_gate_stage0.json`
- `research/experiment_reports/2026-05-12-mecha-engine-lifecycle-contract-gate.md`
- `research/package_specs/mecha_engine_lifecycle_contract_gate.md`
- `data/architecture/mecha_engine_lifecycle_contract_gate_stage0.json`
- `research/experiment_reports/2026-05-12-mecha-engine-archive-contract-gate.md`
- `research/package_specs/mecha_engine_archive_contract_gate.md`
- `data/architecture/mecha_engine_archive_contract_gate_stage0.json`
- `research/experiment_reports/2026-05-12-mecha-engine-provenance-contract-gate.md`
- `research/package_specs/mecha_engine_provenance_contract_gate.md`
- `data/architecture/mecha_engine_provenance_contract_gate_stage0.json`
- `research/reports/mechagotchi_research_report_v0_5.md`
- `research/reports/research_report_v0_5_manifest.json`
- `research/experiment_reports/2026-05-12-mecha-engine-formal-invariant-dependency-gate.md`
- `research/package_specs/mecha_engine_formal_invariant_dependency_gate.md`
- `data/architecture/mecha_engine_formal_invariant_dependency_gate_stage0.json`
- `research/experiment_reports/2026-05-12-mecha-engine-property-negative-test-strategy.md`
- `research/package_specs/mecha_engine_property_negative_test_strategy.md`
- `data/architecture/mecha_engine_property_negative_test_strategy_stage0.json`
- `research/experiment_reports/2026-05-12-slip-profile-compatibility-matrix.md`
- `research/slip/profile_compatibility_tests.md`
- `data/slips/slip_profile_compatibility_matrix_stage0.json`
- `research/experiment_reports/2026-05-12-slip-multi-profile-generation-benchmark.md`
- `data/slips/multi_profile_generation_stage0/slip_multi_profile_generation_stage0.json`
- `research/experiment_reports/2026-05-12-workshop-multi-profile-roundtrip.md`
- `data/workshop_editor/multi_profile_roundtrip_stage0/workshop_multi_profile_roundtrip_stage0.json`
- `research/experiment_reports/2026-05-12-slip-schema-failure-corpus.md`
- `research/slip/slip.schema.json`
- `research/slip/slip_examples/`
- `research/slip/slip_failure_cases.md`
- `data/slips/slip_schema_validation_stage0.json`
- `research/experiment_reports/2026-05-12-slip-pydantic-contract-gate.md`
- `research/slip/pydantic_contract.md`
- `research/slip/slip_pydantic_model.schema.json`
- `data/slips/slip_pydantic_contract_stage0.json`
- `research/experiment_reports/2026-05-12-slip-schema-migration-dependency-gate.md`
- `research/slip/schema_migration_dependency_gate.md`
- `data/slips/slip_schema_migration_dependency_gate_stage0.json`
- `research/experiment_reports/2026-05-12-slip-authoring-panel.md`
- `data/workshop_editor/slip_authoring_panel_stage0.json`
- `research/experiment_reports/2026-05-12-slip-behavior-mutation-preview-gate.md`
- `data/workshop_editor/slip_behavior_mutation_preview_stage0.json`
- `research/experiment_reports/2026-05-12-slip-lifecycle-archive-effects.md`
- `data/workshop_editor/slip_lifecycle_archive_effects_stage0.json`
- `research/experiment_reports/2026-05-13-slip-runtime-selection-policy.md`
- `research/algorithm_cards/slip_runtime_selection_policy.md`
- `data/workshop_editor/slip_runtime_selection_policy_stage0.json`
- `research/experiment_reports/2026-05-13-slip-offspring-lineage-gate.md`
- `research/algorithm_cards/slip_offspring_lineage_gate.md`
- `data/workshop_editor/slip_offspring_lineage_gate_stage0.json`
- `research/experiment_reports/2026-05-13-slip-long-horizon-behavior-gate.md`
- `research/algorithm_cards/slip_long_horizon_behavior_gate.md`
- `data/workshop_editor/slip_long_horizon_behavior_gate_stage0.json`
- `research/experiment_reports/2026-05-13-slip-readability-calibration-gate.md`
- `research/algorithm_cards/slip_readability_calibration_gate.md`
- `data/readability/slip_readability_calibration_gate_stage0.json`
- `research/experiment_reports/2026-05-13-slip-multigeneration-lineage-runner.md`
- `research/algorithm_cards/slip_multigeneration_lineage_runner.md`
- `data/workshop_editor/slip_multigeneration_lineage_runner_stage0.json`
- `research/experiment_reports/2026-05-13-mecha-engine-runtime-boundary-gate.md`
- `research/package_specs/mecha_engine_runtime_boundary_gate.md`
- `data/architecture/mecha_engine_runtime_boundary_gate_stage0.json`
- `research/experiment_reports/2026-05-12-external-metadata-sidecar-strategy.md`
- `data/workshop_editor/external_metadata_sidecar_stage0.json`
- `research/experiment_reports/2026-05-12-standard-image-sidecar-decoder.md`
- `data/workshop_editor/standard_image_sidecar_decoder_stage0.json`
- `research/experiment_reports/2026-05-13-png-variant-sidecar-decoder.md`
- `data/workshop_editor/png_variant_sidecar_decoder_stage0.json`
- `research/experiment_reports/2026-05-14-png-adam7-interlace-decoder.md`
- `research/algorithm_cards/png_adam7_interlace_decoder.md`
- `data/workshop_editor/png_adam7_interlace_decoder_stage0.json`
- `research/experiment_reports/2026-05-13-png-embedded-sidecar-writer.md`
- `research/algorithm_cards/png_embedded_sidecar_writer.md`
- `data/workshop_editor/png_embedded_sidecar_writer_stage0.json`
- `research/experiment_reports/2026-05-14-png-textual-metadata-policy.md`
- `research/algorithm_cards/png_textual_metadata_policy.md`
- `data/workshop_editor/png_textual_metadata_policy_stage0.json`
- `research/experiment_reports/2026-05-14-png-private-chunk-policy.md`
- `research/algorithm_cards/png_private_chunk_policy.md`
- `data/workshop_editor/png_private_chunk_policy_stage0.json`
- `research/experiment_reports/2026-05-14-png-private-chunk-preservation-matrix.md`
- `research/algorithm_cards/png_private_chunk_preservation_matrix.md`
- `data/workshop_editor/png_private_chunk_preservation_matrix_stage0.json`
- `research/experiment_reports/2026-05-14-apng-sidecar-decoder.md`
- `research/algorithm_cards/png_apng_sidecar_decoder.md`
- `data/workshop_editor/apng_sidecar_decoder_stage0.json`
- `research/experiment_reports/2026-05-12-spritesheet-sidecar-decoder.md`
- `data/workshop_editor/spritesheet_sidecar_decoder_stage0.json`
- `research/experiment_reports/2026-05-13-spritesheet-layout-variant-decoder.md`
- `data/workshop_editor/spritesheet_layout_variant_decoder_stage0.json`
- `research/experiment_reports/2026-05-13-spritesheet-packed-runtime-decoder.md`
- `research/algorithm_cards/spritesheet_packed_runtime_decoder.md`
- `data/workshop_editor/spritesheet_packed_runtime_decoder_stage0.json`
- `research/experiment_reports/2026-05-14-spritesheet-arbitrary-atlas-packer.md`
- `research/algorithm_cards/spritesheet_arbitrary_atlas_packer.md`
- `data/workshop_editor/spritesheet_arbitrary_atlas_packer_stage0.json`
- `research/experiment_reports/2026-05-14-spritesheet-multi-page-atlas.md`
- `research/algorithm_cards/spritesheet_multi_page_atlas.md`
- `data/workshop_editor/spritesheet_multi_page_atlas_stage0.json`
- `research/experiment_reports/2026-05-13-third-party-project-decoder-boundary.md`
- `data/workshop_editor/third_party_project_decoder_stage0.json`
- `research/experiment_reports/2026-05-13-project-native-metadata-writer.md`
- `research/algorithm_cards/project_native_metadata_writer.md`
- `data/workshop_editor/project_native_metadata_writer_stage0.json`
- `research/experiment_reports/2026-05-13-project-editor-rewrite-preservation.md`
- `research/algorithm_cards/project_editor_rewrite_preservation.md`
- `data/workshop_editor/project_editor_rewrite_preservation_stage0.json`
- `research/experiment_reports/2026-05-14-aseprite-user-data-chunk-writer.md`
- `research/algorithm_cards/aseprite_user_data_chunk_writer.md`
- `data/workshop_editor/aseprite_user_data_chunk_writer_stage0.json`
- `research/experiment_reports/2026-05-14-aseprite-tags-layers-semantics.md`
- `research/algorithm_cards/aseprite_tags_layers_semantics.md`
- `data/workshop_editor/aseprite_tags_layers_semantics_stage0.json`
- `research/experiment_reports/2026-05-14-png-deep-color-sidecar-decoder.md`
- `research/algorithm_cards/png_deep_color_sidecar_decoder.md`
- `data/workshop_editor/png_deep_color_sidecar_decoder_stage0.json`
- `research/experiment_reports/2026-05-14-png-adam7-deep-color-cross-product.md`
- `research/algorithm_cards/png_adam7_deep_color_cross_product.md`
- `data/workshop_editor/png_adam7_deep_color_cross_product_stage0.json`
- `research/experiment_reports/2026-07-04-slip-dependency-gate-env-decoupling.md`
- `data/slips/slip_pydantic_contract_stage0.json`
- `data/slips/slip_schema_migration_dependency_gate_stage0.json`
- `research/experiment_reports/2026-07-04-slip-lab-validator-alignment.md`
- `research/experiment_reports/2026-07-04-map-elites-neediness-descriptor-fix.md`
- `research/algorithm_cards/map_elites_extended_descriptors.md`
- `data/archives/map_elites_extended_stage0.json`
- `research/experiment_reports/2026-07-04-workshop-editor-decoder-hardening.md`
- `labs/workshop_editor/png_chunk_reader.py`
- `research/experiment_reports/2026-07-04-grid-validator-schema-alignment.md`
- `data/micro_learners/switchboard_lifecycle_feedback_stage0.json`
- `research/experiment_reports/2026-07-04-workshop-editor-boundary-hardening.md`
- `research/experiment_reports/2026-07-04-small-labs-gate-integrity.md`
- `research/experiment_reports/2026-07-04-grid-genome-helper-dedup.md`
- `labs/grid_genome/grid_helpers.py`
- `research/experiment_reports/2026-07-04-foreign-fixture-conformance.md`
- `labs/workshop_editor/foreign_fixture_writer.py`
- `data/foreign_fixtures/manifest.json`
- `research/experiment_reports/2026-07-04-repo-root-path-anchoring.md`
- `research/experiment_reports/2026-07-04-lab-dependency-manifest-and-jsonschema-parity.md`
- `research/decision_records/0005-declare-lab-dependency-manifest.md`
- `labs/slip_validator/jsonschema_runtime_parity.py`
- `data/slips/slip_jsonschema_runtime_parity_stage0.json`
- `pyproject.toml`
- `research/experiment_reports/2026-07-04-deep-color-foreign-fixtures.md`
- `research/experiment_reports/2026-07-04-descriptor-axis-calibration.md`
- `research/reports/mechagotchi_research_report_v0_8.md`
- `research/reports/research_report_v0_8_manifest.json`
- `research/experiment_reports/2026-07-04-mecha-engine-package-scaffold.md`
- `labs/architecture/mecha_engine_scaffold_verification_gate.py`
- `data/architecture/mecha_engine_scaffold_verification_gate_stage0.json`
- `packages/mecha_engine/` (empty package scaffold per decision record 0004; no lab code promoted)

- `research/experiment_reports/2026-07-04-mecha-engine-genome-promotion.md`
- `packages/mecha_engine/src/mecha_engine/genome/`
- `packages/mecha_engine/tests/test_genome_contract.py`

- `research/experiment_reports/2026-07-04-ca-nca-trained-neighborhood-repair.md`
- `data/cellular_automata/ca_nca_trained_repair_stage0.json`
- `data/micro_learners/switchboard_lifecycle_feedback_stage0.json`

- `research/experiment_reports/2026-07-04-mecha-engine-generation-promotion.md`
- `packages/mecha_engine/src/mecha_engine/generation/`
- `packages/mecha_engine/tests/test_generation_contract.py`

- `research/experiment_reports/2026-07-04-mecha-engine-lifecycle-promotion.md`
- `packages/mecha_engine/src/mecha_engine/lifecycle/`
- `packages/mecha_engine/tests/test_lifecycle_contract.py`

- `research/experiment_reports/2026-07-04-mecha-engine-archive-promotion.md`
- `packages/mecha_engine/src/mecha_engine/archive/`
- `packages/mecha_engine/tests/test_archive_contract.py`

- `research/experiment_reports/2026-07-04-mecha-engine-provenance-promotion.md`
- `packages/mecha_engine/src/mecha_engine/provenance/`
- `packages/mecha_engine/tests/test_provenance_contract.py`

- `research/experiment_reports/2026-07-04-package-promotion-gate-first-ready.md`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`

- `research/reports/mechagotchi_research_report_v0_9.md`
- `research/reports/research_report_v0_9_manifest.json`

- `research/experiment_reports/2026-07-04-ca-nca-repair-context-ablation.md`
- `research/algorithm_cards/ca_nca_growth_repair.md`
- `labs/cellular_automata/ca_nca_repair_context_ablation.py`
- `data/cellular_automata/ca_nca_repair_context_ablation_stage0.json` (negative result: retrieval-context conditioning rejected; exemplar ceiling 0.785 bounds the retrieved-template family)

- `research/experiment_reports/2026-07-04-ca-nca-wound-site-repair.md`
- `research/algorithm_cards/ca_nca_growth_repair.md`
- `labs/cellular_automata/ca_nca_growth_repair.py`
- `data/cellular_automata/ca_nca_trained_repair_stage0.json` (wound-site arm meets the assisted stability bar without a template; blind-arm verdict unchanged; `ca_nca_repair` gate candidate now `ready_for_package_design`)

- `research/experiment_reports/2026-07-04-ca-nca-wound-site-validity-guard.md`
- `research/algorithm_cards/ca_nca_growth_repair.md`
- `labs/cellular_automata/ca_nca_growth_repair.py`
- `data/cellular_automata/ca_nca_trained_repair_stage0.json` (validator-guarded token choice closes the mg_seed_046 failure; site-aware arm now 0.938462 overlap = agreement, validity 1.0)

- `research/package_specs/mecha_engine_repair_interface_spec.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md` (repair row added, design-only; target creation stays decision-record-gated)

- `research/decision_records/0006-create-mecha-engine-repair-target.md`
- `research/experiment_reports/2026-07-05-mecha-engine-repair-promotion.md`
- `packages/mecha_engine/src/mecha_engine/repair/`
- `packages/mecha_engine/tests/test_repair_contract.py`
- `labs/cellular_automata/test_package_repair_parity.py` (bit-for-bit lab parity; repair is the sixth promoted module; promotion gate `promotion_ready_count` 4, scaffold gate 9/9 with 6 promoted modules)

- `research/experiment_reports/2026-07-05-slip-readability-rating-tool.md`
- `labs/readability_benchmark/rating_tool_builder.py`
- `data/readability/slip_readability_calibration_rating_tool.html`
- `data/readability/slip_readability_rating_tool_stage0.json` (visual reviewer tool for the manual calibration; protocol now human-executable — calibration itself honestly still blocked at 0 of 63 rows)

- `research/decision_records/0007-mechas-companion-cli.md`
- `docs/cli/mechas-cli.md`
- `docs/cli/mechas-cli-design.md`
- `tools/mechas_cli/` (the `mechas` companion CLI, Typer + Rich; first standardized workflow `mechas rate --creatures [--autoexport]` runs the whole rating loop — serve, collect, save with backup, gate)

- `research/reports/mechagotchi_research_report_v0_10.md`
- `research/reports/research_report_v0_10_manifest.json`

- `research/experiment_reports/2026-07-05-mecha-engine-runtime-loop.md`
- `research/algorithm_cards/mecha_engine_runtime_loop.md`
- `labs/runtime_integration/mecha_engine_runtime_loop.py`
- `data/runtime_integration/mecha_engine_runtime_loop_stage0.json` (first full-loop composition of all six promoted modules: 11/12 creatures complete the pipeline; measured seam — SLIP-alignment retention 0.9167 after repair; next: SLIP-aware repair guard)

- `research/experiment_reports/2026-07-05-slip-aware-repair-guard.md`
- `research/package_specs/mecha_engine_repair_interface_spec.md`
- `labs/cellular_automata/ca_nca_growth_repair.py`
- `packages/mecha_engine/src/mecha_engine/repair/` (SLIP-aware validity guard on both surfaces, default-None bit-identical, contract + parity pinned; runtime loop reruns to retention 1.0 and `runtime_loop_composed` — a `runtime` target proposal is now evidence-ready, owner-gated)

- `research/experiment_reports/2026-07-05-mecha-engine-evolution-loop.md`
- `research/algorithm_cards/mecha_engine_runtime_loop.md`
- `labs/runtime_integration/mecha_engine_runtime_loop.py`
- `data/runtime_integration/mecha_engine_evolution_loop_stage0.json` (multi-generation evolution composed: 32/32 creatures over 4 generations and 96 damage events, retention 1.0, archive elites reproduce, 15 niches / QD 13.92)

- `research/decision_records/0008-propose-mecha-engine-runtime-target.md` (PROPOSED, awaiting owner acceptance)
- `research/package_specs/mecha_engine_runtime_interface_spec.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md` (proposed runtime row)

- `research/experiment_reports/2026-07-05-mecha-engine-runtime-promotion.md`
- `packages/mecha_engine/src/mecha_engine/runtime/`
- `packages/mecha_engine/tests/test_runtime_contract.py`
- `labs/runtime_integration/test_package_runtime_parity.py` (runtime is the seventh promoted module under DR 0008; promotion gate 5/7 promotion-ready; scaffold gate 9/9 with 7 modules and 217 package tests)

- `research/experiment_reports/2026-07-05-stress-regime-evolution.md`
- `research/algorithm_cards/mecha_engine_runtime_loop.md`
- `labs/runtime_integration/mecha_engine_runtime_loop.py`
- `data/runtime_integration/mecha_engine_evolution_hard_regime_stage0.json` (survival saturation broken via the contracted stress probe: 10/48 deaths, archive 25 niches / QD 21.27, mean load falls 0.855 -> 0.761; the learning module's evaluation environment now exists)

- `research/experiment_reports/2026-07-05-stress-learning-benchmark.md`
- `research/algorithm_cards/micro_learning_switchboard.md`
- `labs/runtime_integration/stress_learning_benchmark.py`
- `data/runtime_integration/stress_learning_benchmark_stage0.json` (the learning candidate's falsifiable bar: survival is policy-independent under stress — morphology decides; need-balance +0.080069 at zero survival cost)

- `research/decision_records/0009-create-mecha-engine-learning-target.md`
- `research/experiment_reports/2026-07-05-mecha-engine-learning-promotion.md`
- `research/package_specs/mecha_engine_learning_interface_spec.md`
- `packages/mecha_engine/src/mecha_engine/learning/`
- `labs/grid_genome/test_package_learning_parity.py` (learning is the eighth promoted module, bounded wellbeing claim; promotion gate 7/8 promotion-ready — learning carries two evidence candidates, sheltered and stress; scaffold gate 9/9 with 8 modules and 235 package tests)

- `research/decision_records/0010-start-mecha-workshop-build-track.md`
- `docs/workshop/mecha-workshop-design.md` (binding charter)
- `docs/workshop/mecha-workshop.md` (living reference: research-to-surface map, build slices) — the workshop build track opens charter-first; implementation slice 1 awaits owner approval of the build order

- `workshop/grid_editor/grid_editor.html`
- `workshop/server/workshop_server.py`
- `workshop/tests/test_workshop_server.py`
- `docs/workshop/mecha-workshop.md` (workshop slice 1 shipped: grid editor with live engine validation, strict saves, structural-load teaching; served by `mechas workshop --editor`)

- `workshop/slip_creator/slip_creator.html`
- `workshop/server/workshop_server.py`
- `workshop/tests/test_workshop_server.py`
- `docs/workshop/mecha-workshop.md` (workshop slice 2 shipped: SLIP profile creator with live Stage 0 authority validation, optional lab authoring review, seed-corpus fit counts, and authored profiles joining the grid editor's alignment chips; served by `mechas workshop --slip`)

- `workshop/preview/preview.html`
- `workshop/server/workshop_server.py`
- `workshop/tests/test_workshop_server.py`
- `docs/workshop/mecha-workshop.md` (workshop slice 3 shipped: preview panels drawing render packets verbatim, running runtime.live_cycle for real, and breeding offspring via the generation module; engine alignment errors ARE the preview on mismatch; served by `mechas workshop --preview`)

- `workshop/grid_editor/grid_editor.html`
- `workshop/server/workshop_server.py`
- `workshop/tests/test_workshop_server.py`
- `docs/workshop/mecha-workshop.md` (workshop slice 4a shipped: PNG import/export over the proven embedded-sidecar codec — self-contained pixels+semantics files, engine-strict export, integrity-checked import with failure families verbatim — plus the lab's animated APNG export; Aseprite/spritesheet honestly queued as 4b)

- `workshop/grid_editor/grid_editor.html`
- `workshop/server/workshop_server.py`
- `workshop/tests/test_workshop_server.py`
- `docs/workshop/mecha-workshop.md` (workshop slice 4b completes slice 4: Aseprite import/export via the user-data-chunk writer lab — self-contained projects — and spritesheet import/export as the external-sidecar pair, codec binding checks verbatim; slice 4 fully shipped)

- `audits/audit-devspec.md`
- `audits/TODO.md`
- `.depreciated/og-design.md`, `.depreciated/og-formatted.md`, `.depreciated/og-research.md` (owner DESIGN-CORRECTION 2026-07-05: og-spec audit — no foundational error, workshop subordination intact; one structural correction (T1: workshop creatures must enter the ecosystem simulations) plus og-scope restorations ledgered as tasks)

- `audits/audit-devspec.md` (RUN TWO addendum)
- `audits/TODO.md` (tasks T14-T21)
- `.depreciated/02-design.md`, `.depreciated/02-research.md` (second-pass audit: the 02 files are byte-identical; the RUN ONE/RUN TWO SLIP fork was resolved silently in RUN ONE's favor; grid schema adopted RUN TWO's vocabulary but it lies dormant; RUN TWO's statistical protocols — holdout bake-off, MAP-Elites comparators, learner ablation, pairwise studies — were downscaled or skipped without records; all now tasked)

- `research/experiment_reports/2026-07-05-workshop-engine-wire.md`
- `research/algorithm_cards/mecha_engine_runtime_loop.md`
- `labs/runtime_integration/test_workshop_wire.py`
- `data/runtime_integration/mecha_engine_evolution_workshop_wire_stage0.json`
- `data/workshop/released/` (T1, the workshop->engine asset wire: released creatures become evolution founders through the engine's gates, lineage-traced; first result — both founding lineages extinct at generation 0 vs the corpus, fitness 0.762 vs 0.868; latent episode-gate gap hardened to valid+aligned)

- `research/decision_records/0011-run-one-run-two-reconciliation.md` (audit T14: the RUN ONE/RUN TWO fork closed — RUN ONE's SLIP shape ratified; every RUN TWO delta adopted/watched-with-task/rejected with reasons; value-byte and Jupyter rejected, statistical protocols adopted as the T17-T20 program)

- `research/decision_records/0012-slip-schema-extension-ladder.md`
- `research/experiment_reports/2026-07-05-slip-ladder-forbidden-traits.md`
- `labs/grid_genome/test_slip_forbidden_traits.py`
- `data/slips/valid/slip_v2_no_shell.json` (T3.1: the SLIP ladder's first rung — dual-version authority, forbidden_traits enforced across all four validation surfaces + the workshop creator; package v0.1 boundary intact)

- `research/micro_learners/thread_census.md` (audit T5: 11 og predictors mapped — 3 implemented, 3 partial, 3 missing, 2 covered by stronger mechanisms; consumer designs for ladder rungs T3.2/T3.3)
- `research/experiment_reports/2026-07-05-slip-ladder-risk-tolerances.md`
- `labs/grid_genome/test_slip_risk_tolerances.py` (T3.2: mutation risk tolerance consumed by the switchboard through lifecycle state — monotone effect pinned, frozen baseline bit-for-bit)

- `research/experiment_reports/2026-07-05-slip-ladder-learning-switches.md`
- `labs/grid_genome/test_slip_learning_switches.py` (T3.3: og learning toggles gate switchboard threads through lifecycle state; all-off = the rules-only baseline, giving T19 its ablation harness; frozen flows bit-for-bit)

- `research/experiment_reports/2026-07-05-slip-ladder-lineage-preferences.md`
- `labs/runtime_integration/test_lineage_preferences.py` (T3.4: profile-authored parent selection — fitness_weighted vs uniform pinned different; plus the v01_projection package-boundary adapter that lets v0.2 profiles drive full engine experiments)

- `research/experiment_reports/2026-07-05-animation-states.md`
- `research/algorithm_cards/animation_states.md`
- `labs/grid_genome/animation_states.py`
- `data/grid_genome/animation_states_stage0.json` (T4 first slice: the og five animation states as deterministic visual-only genome projections — 300/300 valid; animstate_300 dataset delivered)

- `research/experiment_reports/2026-07-05-render-packet-v2.md`
- `labs/grid_genome/animation_states.py` (T16 lab-side: packets carry animation + mood selected from lifecycle state over the T4 projections; the workshop previewer plays the five-state cycle from engine truth; promoted-module port stays DR-gated)

- `research/decision_records/0013-port-slip-v2-and-packet-v2.md`
- `research/experiment_reports/2026-07-05-slip-v2-packet-v2-port.md` (owner-authorized port: SLIP v0.2 + packet v2 live in the package — 266 contract tests, zero existing pins touched, v0.2 profiles drive simulations natively)

- `research/decision_records/0014-grid-size-commitment.md` (audit T6: 8x8 committed for the current phase on probe evidence — validator is size-generic but every calibrated constant/corpus/gate is 8x8-denominated; T17's multi-size bake-off is the designated re-opener)

- `research/experiment_reports/2026-07-05-switchboard-ablation.md`
- `labs/grid_genome/switchboard_ablation.py`
- `data/micro_learners/switchboard_ablation_stage0.json` (T19 Stage 0: full switchboard beats rules-only by ~336% need balance — measured; keep-gate keeps only hidden_mood_estimator at this scale, others queued for the scaled rerun)

- `research/decision_records/0015-dormant-vocabulary-coverage.md`
- `labs/grid_genome/vocabulary_exemplars.py`
- `data/vocabulary_exemplars/` (T15: cover-not-trim — the vocab_argus exemplar exercises every dormant cell role, material, and organ role; coverage pinned by test so the vocabulary can never silently go dormant again)

- `research/experiment_reports/2026-07-05-slip-ladder-species-grammar.md`
- `labs/grid_genome/test_slip_visual_grammar.py` (T3.5, the ladder's final field rung: species_class consumed by evolution identity; visual_grammar's allowed_materials alignment-enforced and animation_vocab packet-consumed with honest mood on fallback; all four package mirrors synced — DR 0013's parity pins caught the lag as designed)

- `research/experiment_reports/2026-07-06-slip-ladder-gates.md`
- `labs/slip_validator/slip_zoo_gates.py`
- `data/slips/zoo/` + `data/slips/slip_zoo_gates_stage0.json` (T3.6, ladder_gates_met: 18/20 archetypes with zero UNPLANNED gaps; fuzz false-pass 0.0 over 161 cases, validators in perfect agreement; slip_zoo_100 delivered — THE SLIP LADDER IS COMPLETE)

- `workshop/grid_editor/grid_editor.html` + `workshop/server/workshop_server.py` (T9 trait editor: per-cell role/material/mutation-weight overrides across the DR 0015 vocabulary, organ remap server-side, engine-judged; 5 endpoint tests)

- `research/experiment_reports/2026-07-06-archive-comparators.md`
- `labs/map_elites_archive/archive_comparators.py`
- `data/archives/archive_comparators_stage0.json` (T18, map_elites_confirmed: at matched budgets on identical streams the archive preserves 3.9x GA's niches and 2.5x novelty search's with ZERO best-fitness sacrifice — the og adoption claim is now measured fact)

- `research/experiment_reports/2026-07-06-generation-bakeoff-formal.md`
- `labs/grid_genome/generation_bakeoff_formal.py`
- `data/generated_grids/generation_bakeoff_formal_stage0.json` (T17, bakeoff_gate_met: holdout discipline enters the repo; shipped hybrid CONFIRMED at 1.0/1.0 on unseen creatures; raw markov unusable at 0.12 — validator gating IS the generator; the constrained arm matches perfection with 2.4x novelty, recorded as the A/B follow-up)

- `LICENSES/` (T21: the REUSE convention — LicenseRef texts for included assets + the reference-only marker; provenance CI gains reuse_licenses_ok in BOTH the lab and the promoted mirror, contract extended; the repo-wide license grant remains the owner's pending decision, honestly recorded)

- `research/experiment_reports/2026-07-06-switchboard-ablation-scaled.md`
- `data/micro_learners/switchboard_ablation_scaled_stage0.json` (T19 scaled rerun: 240 episodes across all 8 aligned creatures — Stage 0 verdicts REPLICATE; mood estimator removal costs 77-85% at scale; others stay dead_weight, still queued on the 500-lifecycle arbiter)

- `research/experiment_reports/2026-07-06-v01-projection-retirement.md`
- `labs/runtime_integration/test_v01_projection_retirement.py` (DR 0013 follow-up closed: the loop consumes v0.2 natively — all-off switches measurably change package episodes, proven RED-first both directions; the adapter stays in the authority, documented)

- `research/experiment_reports/2026-07-06-generator-evolution-ab.md`
- `data/archives/generator_evolution_ab_stage0.json` (T17 follow-up A/B: dead heat — 76 niches both arms, shipped_hybrid_stands; raw generator novelty does not equal archive coverage, the descriptor grid bounds diversity)

- `research/decision_records/0016-evolve-founder-grids.md` (T1.5: the T1 wire's founder semantics enter the promoted runtime.evolve contract — gate-admitted founders lead generation 0; defaults byte-identical, contract pins extended)

- `workshop/inspector/inspector.html` + `/api/inspect` + `/api/lineage` (workshop slice 5: genome inspector + lineage browser over engine-judged records and the committed wire evidence; 4 endpoint tests)

- `research/human_studies_protocol.md`
- `workshop/server/workshop_server.py` (/api/metrics) + `labs/readability_benchmark/bradley_terry.py` (T10 + T20 pipelines: og workshop metrics instrumented per-session with provenance-marked records; blind-pairwise protocol + stdlib Bradley-Terry MM scorer tooling-validated on synthetic data — human DATA remains human, per the standing rule)

- `research/experiment_reports/2026-07-06-ctm-deliberation-live.md`
- `labs/grid_genome/test_slip_deliberation.py` (R1: CTM deliberation LIVE — the creature visibly thinks, 64 events/8 episodes with a renderable trace; wellbeing delta 0.0 sheltered, honestly recorded; adopt-as-expressiveness/watch-for-utility)

Stage 0 and Stage 1 established:

- Stage 0: define the research ontology and evaluation vocabulary.
- Stage 1: turn the source list into a structured literature map.

No algorithm should graduate into `packages/` until it has an algorithm card,
an experiment report, a metric report, and a decision record.
