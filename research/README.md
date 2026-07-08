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

- `research/decision_records/0018-cubff-live-lineage-pressure.md`
- `research/experiment_reports/2026-07-06-cubff-live-lineage-pressure.md`
- `labs/runtime_integration/test_cubff_pressure.py`
- `data/runtime_integration/mecha_engine_evolution_cubff_pressure_stage0.json` (R2: CuBFF Pipeline C LIVE in the evolution loop — chaotic soup 1.17x damage/111 cells vs stable 0.90x/88 at the same seed; the Google experiment's dynamics are now the engine's bloodstream, not a lab exhibit; semantic-compiler rule held, absent source byte-identical)

- `research/decision_records/0019-learned-readability.md`
- `research/experiment_reports/2026-07-06-learned-readability.md`
- `research/algorithm_cards/learned_readability.md`
- `labs/readability_benchmark/learned_readability.py` / `data/readability_benchmark/learned_readability_stage0.json` (R3: TRUE ML primary readability path — physics-supervised pairwise ranker, heldout 1.0, leave-one-family-out 1.0 on all four degradation families, auditable learned weights)
- `data/runtime_integration/mecha_engine_evolution_readability_selection_stage0.json` (R3 live consumer: the LEARNED model steers evolution's parent selection — A/B at the same seed, post-founder mean candidate readability 0.361 vs 0.270 control, gen-3 0.498 vs 0.199; manual rating system unchanged as the fallback/calibration check)

- `research/decision_records/0020-cubff-pressure-runtime-promotion.md`
- `research/experiment_reports/2026-07-07-cubff-pressure-runtime-promotion.md`
- `packages/mecha_engine/src/mecha_engine/runtime/_cubff.py` / `packages/mecha_engine/tests/test_runtime_cubff_contract.py` / `labs/cubff_transducer/test_package_cubff_parity.py` (R2.5: CuBFF lineage pressure promoted into `runtime.evolve` — verbatim mirror + contract + drift guard; promoted-surface directional effect 1.17x vs 0.90x; real-snapshot clause honestly blocked on `awaiting_real_cubff_snapshots`)

- `research/decision_records/0021-game-loop.md` (R4: the game loop — "Eras of the Soup": Keeper fantasy, era-chaining via `founder_grids` as the persistence spine, CuBFF weather, engine-truth progression currencies, extinction stakes from measured archive behavior; unblocks the `storage` module DR (G1) and defines build gates G1–G4)

- `research/decision_records/0022-storage-module.md` (G1: the `storage` module target authorized — SQLite campaign ledger via stdlib `sqlite3` per DR 0011's ratified pointer; blob-authoritative schema v1 for campaigns/eras/elites/founders/unlocks/replays, succession without copying, deterministic-replay and unlock-falsifiability gates; lab-first in `labs/game_loop/campaign_store.py` before any promotion, G2's JSON interim guaranteed a lossless migration)

- `research/experiment_reports/2026-07-07-game-loop-session-runner.md`
- `research/algorithm_cards/game_loop_session_runner.md`
- `labs/game_loop/session_runner.py` (+ `test_session_runner.py`)
- `data/game_loop/session_runner_stage0.json` + `data/game_loop/campaign_ledger.json` (G2: one full Keeper session over promoted surfaces — era-chaining admits 10/10 and 9/9 prior elites through the engine's own gates, stable soup measurably shields (58 vs calm 65 removed cells) while the storm's 1.17x earns the storm record, 6 unlock facts each citing a resolvable metric path, succession fixture-proven, DR 0022 JSON-interim ledger. FOUND+FIXED the aligned-but-invalid promotion drift: the lab's T1 validity gate on episodes had never reached `runtime.live_cycle`/`evolve` — RED-first sync, spec amended, all frozen pins byte-identical)
- `labs/runtime_integration/test_invalid_repair_semantics.py` + the `invalid_repair_boundary` contract probe (the drift fix's lab-package boundary parity pin and package-side contract pin)

- `research/decision_records/0023-replay-recording.md`
- `research/experiment_reports/2026-07-07-replay-recorder.md`
- `research/algorithm_cards/replay_recorder.md`
- `labs/game_loop/replay_recorder.py` (+ `test_replay_recorder.py`)
- `data/game_loop/replay_recorder_stage0.json` + `data/game_loop/replay_sample.json` (R5: the player's window — `live_cycle(record_frames=True)` engine seam (byte-identical off, contract-probed), the `mechagotchi_replay_v1` recorder (birth/wound/repair/tick frames, all engine truth verbatim, invalid repairs carry validator errors never fake bodies), and the preview scrubber over `POST /api/preview/replay`; sample life 151 frames/144 ticks, deterministic end to end)

- `research/experiment_reports/2026-07-07-keeper-session-surface.md`
- `workshop/session/session.html` + the `/api/session/*` endpoints
- `tools/mechas_cli/src/mechas_cli/workflows/session.py` (G4: the Keeper's surface — persistent `keeper_session_v1` state with incremental play PINNED equal to batch play, succession seating the successor bloodline automatically, the Keeper page on the workshop server pattern, and `mechas session --open/--era/--status/--new` per the DR 0007 charter; play state gitignored under `data/game_loop/keeper/` so a live game never overwrites evidence)

- `research/experiment_reports/2026-07-07-dataset-program.md`
- `research/algorithm_cards/dataset_program.md`
- `labs/datasets/dataset_program.py` (+ `test_dataset_program.py`)
- `data/datasets/` (R6: the og dataset table completed — `mechaseed_200` (50 seeds + 150 validity-curated, signature-deduped engine variants, each reproducible from its recorded config), `mutationbench_5000` (5,000 signature-verifiable offspring cases — full grids of truth without stored grids), `replay_100k_ticks` (100,004 verbatim lifecycle ticks, byte-deterministic gzip) — all under the shipped `slip_corpus_r6` profile, sha256-manifested; PNG companions honestly deferred, no consumer yet)

- `research/decision_records/0024-grid-schema-animation-species-resolution.md` (R7: og grid-level animation/species fields resolved by superseding decision — animation is T4's projections + packet-v2 selection + covenant vocabulary (the og itself put animation on the packet; `animation_anchor` already shipped); species is covenant identity (T3.5), the grid-level copy rejected as decorative duplication with mixed-species soups as the designated re-opener; DR 0011 verdict #5 fully resolved)

- `research/decision_records/0025-readability-selection-runtime-promotion.md`
- `research/experiment_reports/2026-07-07-readability-selection-promotion.md`
- `packages/mecha_engine/src/mecha_engine/runtime/_readability.py`
- `labs/readability_benchmark/test_package_readability_parity.py` + `labs/runtime_integration/test_readability_selection_parity.py` (C1: R3's live consumer promoted into `runtime.evolve` — verbatim scorer mirror + drift guard, record-for-record lab parity, the R3 A/B directional claim holding on the PROMOTED surface, defaults byte-identical; the session steers every era at blend 0.7 and the legibility currency is EARNABLE live (tiers 1+2, elite mean 0.401 vs 0.244) — which immediately measured legibility drifting DOWN across chained eras (0.401 → 0.014; bodies fragment, symmetry falls), a real dynamic queued for C4/C6)

- `research/experiment_reports/2026-07-07-campaign-store.md`
- `research/algorithm_cards/campaign_store.md`
- `labs/game_loop/campaign_store.py` (+ `test_campaign_store.py`)
- `data/game_loop/campaign_store_stage0.json` + `data/game_loop/campaign_store.sqlite` (C2: DR 0022's SQLite campaign ledger, lab-proven — all eight gates green as tests over a REAL chained campaign incl. byte-identical blob round-trips, derived-column pins, atomic eras, deterministic replay of stored eras, pointer-chain succession with zero copied rows, and the lossless `dr0022_v1_json_interim` migration; `founders.grid_json` divergence documented (nullable — single-source rule); promotion-gate candidate registered, verdict `ready_for_package_design`)

- `research/experiment_reports/2026-07-07-storage-module-promotion.md`
- `packages/mecha_engine/src/mecha_engine/storage/` + `packages/mecha_engine/tests/test_storage_contract.py`
- `labs/game_loop/test_package_storage_parity.py` (C3: `mecha_engine.storage` promoted — the NINTH module; verbatim byte-level port with dual parity pins (source byte-identity + row-for-row behavior over the real interim), contract suite with observed atomic rollback, the Keeper session/server deriving `campaign_ledger.sqlite` through the exercised migration on every save; promotion gate verdict PROMOTION_READY, deferred set now `render` + `slip`)

- `research/experiment_reports/2026-07-07-per-era-replay.md`
- `data/game_loop/replays/` (C5: the Review step closes — every era records its best elite's life via the DR 0023 recorder at the era's own seed; ledger `replays` rows are pure functions of state (path convention + sha256 over canonical JSON, file hash == row hash pinned); both stores ingest the rows; `GET /api/session/replay` + the Keeper page's per-era in-page scrubber over RECORDED frames)

- `research/experiment_reports/2026-07-07-repair-validity-boundary.md`
- `research/algorithm_cards/repair_validity_boundary.md`
- `labs/repair_boundary/repair_validity_boundary.py` (+ `test_repair_validity_boundary.py`)
- `data/repair_boundary/repair_validity_boundary_stage0.json` (C6: the repair-validity boundary MEASURED on the production `evolve` surface — hypothesis "extreme-damage-only" REFUTED: a damage-scaled mortality gradient present throughout (0.025 at 0.2×1 → 0.10 at 0.9×4, ~0.0125 in the session band), the ONLY failing invariant the disconnected required body core (cause-diagnosed, not assumed); VERDICT: the skip is retained as correct biology, the connected-core repair contract REJECTED as manufacturing survival the physics didn't grant. Two harness false starts recorded as the finding's spine — grid_id overflow, and reconstruction-blindness from shared `validate_grid`)

- `research/experiment_reports/2026-07-07-covenant-step.md` (C4: unlocks SPEND — `covenant_budget` maps the DR 0021 progression table to spendable budget as a pure function of earned facts (deliberation on the authority's real floor of 2; caps double per QD tier; the earned blend flows through `advance_campaign` keeping batch == incremental pinned); `apply_covenant_change` enforces budget + authority with named violations; the Keeper page's covenant panel + `POST /api/session/covenant`; deferred axes named in the budget payload; regenerated session runs eras 1–2 at the EARNED blend 0.8)

- `research/experiment_reports/2026-07-07-mortal-wound-signal.md` (D2: C6's shattered-core mortality gradient surfaced as a Keeper-visible event at every surface — `_mortal_wounds` reads the report's existing per-creature `archive_decision` (no new engine number), rides the era digest + session `mortal_wound_toll`, and shows as "the toll" in `mechas session` and on the Keeper page; honest at zero (demo toll 0, the ~1.25% in-band rate), test-proven to fire non-zero under heavy damage and always pinned to a recomputation of engine truth; stale `sqlite_ledger_pending_storage_module_promotion` blocked-state removed post-C3)

- `research/decision_records/0026-render-module-disposition.md` (D3: the `render` module dispositioned by the DR 0024 method — the renderer-neutral packet contract (`render_packet_from_grid` + `render_packet_v2`) already SHIPS in `mecha_engine.genome`; a `mecha_engine.render` DRAWING module is REJECTED-until-consumer (the only pixel code is non-portable browser JS, no Python rasterizer consumer exists), with a named re-opener (a non-workshop Python consumer needs to rasterize — server-side PNG export, headless renderer, or a `mechas` image command). Identified: a `genome` follow-up (the `slip_profile` animation-vocab gate into `render_packet_v2`) and a workshop-track cleanup (the three duplicated canvas draw loops into a shared asset). `render` + `slip` remain the deferred targets)

- `research/experiment_reports/2026-07-07-campaign-scale-soak.md`
- `labs/game_loop/session_soak.py` (+ `test_session_soak.py`)
- `data/game_loop/session_soak_stage0.json` (D5: the C2/C3/C5 persistence spine load-verified over a 12-era chain through the promoted storage module — determinism at scale, ledger blob round-trips, deterministic replay of EVERY stored era, replay-file hashes matching rows, founder-chain continuity, unlock-chain monotonicity; `soak_spine_holds_at_campaign_scale`. Two harness-faithfulness bugs found and fixed (the C4 earned blend must be replayed not defaulted; `founder_grids=None` ≠ `[]` — the DR 0016 distinction is intentional); live extinction honestly unreachable at Stage-0 scale, so succession stays fixture-proven)

- `research/experiment_reports/2026-07-07-render-packet-v2-slip-gate-promotion.md`
- `packages/mecha_engine/src/mecha_engine/genome/animation.py` + `labs/grid_genome/test_package_animation_parity.py` (E1: the T3.5 SLIP `visual_grammar.animation_vocab` gate promoted verbatim into `genome.render_packet_v2` — the species' vocabulary bounds the packet and unsupported states fall back to a DISPLAYED idle with honest mood; `slip_profile=None` byte-identical, parity carve-out closed, contract probe added; the workshop `/api/preview/render` switched to the promoted surface (nocturne renders vocab `[idle,sleep]` end-to-end) — the last shipped-surface dependency on a lab for packet building, closed)

- `research/experiment_reports/2026-07-07-shared-workshop-draw-asset.md`
- `workshop/shared/draw.js` (E2: DR 0026's recorded cleanup — one shared `MechaDraw` packet drawer (damage stroke as an option pinning each page's historical pixels) + wound overlay + scrubber body-resolution; preview + session import it, inline duplicates deleted, endpoint tests pin asset/imports/no-duplicates; scope correction recorded — the grid editor's `draw()` is a distinct MATRIX-authoring surface, not a duplicate, and stays local by test)

- `research/experiment_reports/2026-07-07-dataset-consumers.md`
- `labs/datasets/dataset_consumers.py` (+ `test_dataset_consumers.py`)
- `data/datasets/dataset_consumers_stage0.json` (E3: the R6 fuel burns — TWO findings. (1) R3's synthetic-trained model generalizes to REAL mutations: 0.9406 pairwise accuracy on 2,880 physics-labeled real pairs (0.983 degraded / 0.849 improved; 57.6% coverage, unlabeled reported not hidden; all 5,000 signatures re-verified). (2) A survivorship-bias catch: the naive per-lived-tick mean ranked switchboard LAST; the engine-faithful full-horizon statistic flips it — switchboard 0.789 at survival 1.00 vs idle 0.121 at survival 0.00 (all idle creatures starve by tick ~11); the padding math pinned by a hand-computed crafted-corpus test)

- `research/decision_records/0027-slip-module-disposition.md` (E4: the last deferred target dispositioned — and unlike render, `slip` EARNS it: four package-internal `_slip.py` mirrors (~80 KB quadruplicated, held in sync only by the DR 0013 parity pins) plus the workshop server's docstring-promised switch. `mecha_engine.slip` authorized as the tenth target under the DR 0022 authorize-then-gate pattern; port gates fixed (mirror reconciliation over zoo+fuzz first, contract + parity, byte-identical module behavior after the collapse, workshop switch, promotion_ready before merge); the pydantic cross-check stays lab-side — independence is its value. The og deferred-target list is now empty)

- `research/experiment_reports/2026-07-07-five-notices-audit.md` (E5: DR 0021's five player-notices audited end to end — weather SHIPPED+VISIBLE with provenance display closed here; "creatures think" MECHANISM SHIPPED but the deliberation record is discarded before episode history (trace invisible — seeded with its exact engineering path); legibility SHIPPED+VISIBLE with the direction corrected by measurement; "blood persists" GAP CLOSED — the Contribute step wired into the Keeper session (releases lead the founder pool through the engine's gates, server + CLI + tests); "absence hurts" SHIPPED with the honest reading. Four of five fully live)

- `research/experiment_reports/2026-07-07-seen-thought.md`
- `labs/lifecycle_sim/test_deliberation_history.py` (F1: the seen thought — `choose_action_detailed` + a rung-conditional `deliberation` key on history entries, verbatim across the lab authority and the package with identical-history pins; reflexes/idle/random/frozen flows byte-identical; contract driver probe; both scrubbers render "thought N ticks" and a thinking-covenant replay carries bounded thoughts end to end. DR 0021's notice 2 fully live — five of five)

- `research/experiment_reports/2026-07-07-slip-module-promotion.md`
- `packages/mecha_engine/src/mecha_engine/slip/` + `packages/mecha_engine/tests/test_slip_contract.py`
- `labs/slip_validator/slip_authority_reconciliation.py` + `data/slips/slip_authority_reconciliation_stage0.json` (F2: `mecha_engine.slip` promoted — the TENTH module. Gate-1 reconciliation measured ZERO divergences five-way pre-collapse; the four private `_slip.py` mirrors deleted (~60 KB of quadruplication gone) with every module suite passing unmodified through the public import; the parity pin rewritten as the permanent pair pin (exact verdict-and-error-string equality, 590 validate + 2,080 alignment cases); the workshop server's long-promised switch fulfilled; promotion gate NINE of ten ready. Every og module target is now realized — ten promoted, `render` dispositioned with a named re-opener)

- `research/experiment_reports/2026-07-07-real-mutation-finetune.md`
- `labs/readability_benchmark/real_mutation_finetune.py`
- `data/readability_benchmark/real_mutation_finetune_stage0.json` + `data/readability_benchmark/adopted_readability_model.json` (F3: the ranker augmented with mutationbench's physics-labeled REAL pairs — ALL GATES GREEN and ADOPTED: real heldout (cross-parent) 0.98018 → 1.0, zero synthetic regression, live physics A/B not worse; the adopted weights frozen as a committed auditable artifact and the session's legibility trainer switched to load it. E3's fuel became a better model)

- `research/reports/mechagotchi_research_report_v1_0.md` + `research/reports/research_report_v1_0_manifest.json` (V1: the realization-wave consolidation — cycles 02–06 in one document: ten of ten og module targets, "Eras of the Soup" live with five of five notices, the dataset→consumer→adopted-model chain, the mortality-gradient verdict, test base 747 → 1,210; 46 experiment reports + 20 decision records referenced, all 79 manifest paths verified; the underlying lab reports untouched per the convention)

- `research/experiment_reports/2026-07-07-living-companion.md`
- `labs/game_loop/companion.py` + `test_companion.py` (W1: the living companion — the tamagotchi heart on the engine's tick. Adopt through `initial_state`'s gate, tend with `ACTIONS` (one `advance_tick` per button), idle moments played by the frozen switchboard with the deliberation record visible LIVE, frames via packet v2 over the live state, honest refusal-not-noop death. Lifecycle surface widened to six exports (gate doc § Interactive surface); `/companion` + `mechas session --companion`; 12 lab gates + endpoint flow)

- `research/experiment_reports/2026-07-08-16x16-invariant-scaling.md`
- `research/algorithm_cards/invariant_scaling_16x16.md`
- `labs/grid_genome/invariant_scaling.py` (+ `test_invariant_scaling.py`)
- `data/grid_genome/invariant_scaling_16x16_stage0.json` + `data/grid_genome/pilot_16x16/`
- `research/decision_records/0029-16x16-default-grid-scale.md` (cycle 09 A1 · ENGINE · Phase A: the invariants re-derived EMPIRICALLY at the documented primary scale — 16×16 ratified as the proven default (DR 0014's required size-adoption record); body-core floor 18 via the size law `max(4, 18·w·h//256)` reproducing both ratified scales (8×8 stays 4, pins untouched); candidates {4,8,24} refuted by the canvas-share band, 18 preferred over 16 because it exceeds the p95=17 accidental noise blob; 8-neighbor topology reaffirmed as load-bearing (26% of seed cores diagonal-dependent); chance-pass rejection 0.625% → 0/4,000 at scale; ten pilot exemplars across the DR 0015 vocabulary (core 18–60, symmetry 0.128–1.0, occupancy ≤0.4375, lab+package clean) seed A2's corpus; engine adoption deliberately deferred to A3 RED-first — blocked states honest in the artifact)

- `research/experiment_reports/2026-07-08-16x16-seed-corpus.md`
- `labs/grid_genome/corpus_builder.py` (`BLUEPRINTS_16`) + `labs/grid_genome/grid_helpers.py` (`grid_from_rich_matrix`)
- `data/seed_grids_16x16/` (50) + `data/invalid_grids_16x16/` (200)
- `workshop/grid_editor/grid_editor.html` + `workshop/server/workshop_server.py` (cycle 09 A2 · ENGINE · Phase A: the documented corpus deliverable at the primary scale — 50 hand-authored 16×16 creatures (pilots 001–010 + forty new across all five palettes; core span 18–85, profile-view asymmetrics alongside bilaterals, limbless alongside limbed; every seed sensor-paired, single-anchored, over the ratified 18 floor, validator-clean), 200 counterexamples all rejected, and the workshop's size-parametric canvas (8×8/16×16 buttons, matrix gate on exactly the ratified sizes, symmetry mirrored on the grid's own width); the rich-token alphabet collapsed to one source in grid_helpers (L-04 discipline). Honest blocked states: SLIP mass bounds, the engine's 4-cell floor constant, and the mass/16 stress probe stay 8×8-denominated until A3/A4 — named in the report, mirrored not hidden)

- `research/experiment_reports/2026-07-08-16x16-validator-generation.md`
- `labs/grid_genome/validator.py` + `packages/mecha_engine/src/mecha_engine/genome/validation.py`
- `packages/mecha_engine/src/mecha_engine/generation/model.py` + `labs/grid_genome/constrained_generator.py` (cycle 09 A3 first slice · ENGINE · Phase A: the DR 0029 floor law `max(4, 18·w·h//256)` enforced in BOTH validators RED-first (8×8 outcome and error string byte-identical; the lab evidence function delegates to the enforced law so they cannot drift); the 16×16 corpora joined the genome parity pin (500 files, error-string equality at both scales); generation made size-parametric (model dimensions derive from the corpus, mixed sizes fail loudly, 8×8 models byte-identical) with 16×16 gates in the lab and the package contract (25/25 valid candidates over the floor). Honest remainders recorded: the 4-token generation alphabet (Phase B's WFC charter), and the stress-probe denominator deliberately NOT renormalized by fiat — the measured 16×16 core fractions refute the naive `mass/(area/4)` family, so the denominator gets its own lab measurement in the next A3 increment with repair retraining, lifecycle re-derivation, and size-relative SLIP bounds)

- `research/experiment_reports/2026-07-08-stress-probe-scaling.md`
- `research/algorithm_cards/stress_probe_scaling.md`
- `labs/map_elites_archive/stress_probe_scaling.py` (+ `test_stress_probe_scaling.py`)
- `data/archives/stress_probe_scaling_stage0.json` (cycle 09 A3 · ENGINE · Phase A: the /16 stress-probe denominator re-derived from evidence as DR 0014 required — the exact engine statistic (probe → real run_episode → the archive's own bins) measured over both proven corpora under three laws that all reproduce /16 at 8×8. The shipped constant measured as a TOTAL 16×16 collapse (98% saturation, one bin, every creature dead at tick 12); the first-slice prediction that DR 0014's `mass/(w·h/4)` family would fail is REFUTED and recorded (18% saturation, axis alive, all gates pass); `area_over_4` adopted by the pre-registered rule into `lifecycle_probe_grid` AND its four verbatim mirrors (runtime lab probe, archive contract oracle, extended-descriptors lab, workshop morphology panel) — 8×8 byte-identical by the identity gate, every consumer suite green unmodified; `four_x_floor` (D=72) the named runner-up if a difficulty pass judges the saturation harsh)

- `research/experiment_reports/2026-07-08-repair-at-16x16.md`
- `labs/cellular_automata/ca_nca_growth_repair.py` + `labs/cellular_automata/test_repair_scale16.py`
- `packages/mecha_engine/src/mecha_engine/repair/` (cycle 09 A3 · ENGINE · Phase A: the repair feature layout made size-parametric in matched lab/package pairs — position one-hot derives from the grid (161 features at 8×8 exactly as before, 353 at 16×16), training derives its scale from the corpus with loud mixed-size rejection, and a scale guard rejects model/grid mismatches; wound-site semantics untouched and 8×8 weights bit-for-bit (full parity suite unmodified). The 16×16 re-gate: guarded wound repair validator-clean 40/40 held-out, exact-token restoration 539/603 (0.894), sites beyond the old quadrant refilled. The TODO's named NumPy trigger did NOT fire — full-corpus 16×16 training measured 21.0s stdlib vs 5.5s at 8×8, a train-once cost that justifies no dependency at this phase; recorded as a negative result with Phase E the named re-check)

- `research/experiment_reports/2026-07-08-slip-size-relative-bounds.md`
- `research/decision_records/0030-slip-size-relative-mass-bounds.md`
- `labs/grid_genome/slip.py` + `packages/mecha_engine/src/mecha_engine/slip/authority.py` (cycle 09 A3 · ENGINE · Phase A — **A3 closes**: SLIP mass bounds ratified as 8×8-reference-denominated, scaling by area (`bound·w·h//64`) in the two alignment surfaces identically — an exact identity at 8×8 so the F2 pair pin's 2,080 cases pass unmodified; the zoo's 4..24 reads 16..96 at 16×16 and the corpus aligns (RED: ten lcd creatures rejected before; parity gained a non-vacuous 16×16 sweep); the error message reports the EFFECTIVE bounds; no schema or fixture change; the A2 workshop export limitation closes for aligned creatures; the dossier's grid_size priors named as a future Phase-B ladder item. A3 complete across its five surfaces: validator floor, size-parametric generation, retrained/re-gated repair, lifecycle via the renormalized probe, and size-relative SLIP — every standing gate green at 16×16, no 8×8 pin moved)

- `labs/map_elites_archive/test_descriptor_scale16.py`
- `packages/mecha_engine/src/mecha_engine/archive/descriptors.py` + `store.py`
- `labs/grid_genome/darwin_archive.py` + `labs/map_elites_archive/extended_descriptors.py` (cycle 09 A4 first increment · ENGINE · Phase A: the body-mass descriptor bin edges re-derived for the 16×16 trait ranges by the DR 0029/0030 reference-canvas pattern — `edge·w·h//64`, identity at 8×8 ([6,9,12,16] unchanged, every historical descriptor byte-identical), [24,36,48,64] at 16×16 where the corpus previously collapsed into the top bin; the axis now spreads ≥4 of 5 bins over the corpus (RED: 52 failures before). Applied at all three binning sites in agreement — package descriptors/store, darwin baseline lab, extended-descriptors lab; sensor/symmetry/readability/survival/stability/neediness edges unchanged (dimensionless or discrete, measured to spread already). Consolidated A4 experiment report lands with the A4 gate)

- `research/experiment_reports/2026-07-08-evolution-at-16x16.md`
- `labs/game_loop/session_runner.py` + `packages/mecha_engine/src/mecha_engine/runtime/evolve.py` + `workshop/server/workshop_server.py`
- `data/game_loop/` (regenerated demo + replays) (cycle 09 A4 · ENGINE · Phase A — **A4 closes**: evolution and the game surfaces at 16×16 defaults. Wall-clock measured on the session's exact path (toy 3×4: 0.1s → adopted 6×16: 1.2s/era, 39 niches, qd 36.4 → gen10×32: 4.9s, 70 niches) — the raised default is instant-feeling and the covenant's earned doublings stay playable; unlock tiers re-tuned to the measured 3-era magnitudes (niche [16,26,36], qd [9,18,33]; bloodline/storm/legibility regimes measured unchanged), demo re-earns 8 facts over 3 eras. Eras are size-coherent: evolve rejects wrong-scale founders through the gate with the honest reason (the crash it replaces was measured in the workshop suite); campaign_scale/session_scale read a bloodline's scale from its own bodies so pre-A4 8×8 saves keep their machinery while fresh campaigns start at 16×16; the workshop serves per-scale models with the 16×16 corpus leading its listings and the companion adopting at either scale. Finding: wall-clock is not the binding constraint — evaluations are, which is Phase E's problem to have)

- `research/experiment_reports/2026-07-08-phase-a-gate.md` (cycle 09 A5 · ENGINE · **Phase A GATE — GREEN**: the consolidated gate over A1–A4 — the invariant table, corpus stats, every surface's 16×16 gate result, the measured wall-clock curve, and the honest 8×8-remainder list (the 4-token generation alphabet → Phase B's WFC charter; readability calibration 8×8-derived and displayed as uncalibrated; animation corpora → Phase C; the datasets program → its Phase D/E consumers; the editor's default canvas; the ARGUS exemplar). Phase A checked off in `docs/gap-analysis.md`; cycle 09 archives to `audits/complete/09/`; cycle 10 opens Phase B from the gap analysis)

- `research/experiment_reports/2026-07-08-wfc-grid-lab.md`
- `research/algorithm_cards/wfc_grid.md`
- `labs/wfc_grid/wfc_grid.py` (+ `test_wfc_grid.py`)
- `data/wfc_grid/wfc_grid_stage0.json` (cycle 10 B1 · ENGINE · Phase B: the documented WFC/constraint generator exists at last, over the FULL DR 0015 alphabet — position-channel overlapping WFC, minimum-entropy collapse with arc-consistent propagation, deterministic bounded restarts, and the dossier's own recommended stabilizer usage. First-class negative result recorded: pure local collapse measured 2% valid (49/50 disconnected cores — position priors mix body plans and local adjacency cannot see global connectivity); with largest-core retention + cardinality restarts + the promoted anchor semantics: validity 1.0, 50 unique silhouettes, all six rich roles, copy rate 0.0, cores 31–60. The 72/24/24 dossier protocol adapted to 30/10/10 stratified per palette, recorded. The arm is honest-local — no validator-gated resampling; the B2 bake-off judges it against random/Markov/constrained/hybrid)

- `research/experiment_reports/2026-07-08-generation-bakeoff-16x16.md`
- `labs/wfc_grid/generation_bakeoff16.py` (+ `test_generation_bakeoff16.py`)
- `data/wfc_grid/generation_bakeoff16_stage0.json` (cycle 10 B2 · ENGINE · Phase B: the REAL documented bake-off, all five arms at 16×16, adoption rule pre-registered before the run. Verdict: **WFC wins; the documented hybrid is REFUTED** — its added mutation+gate stages buy nothing on the measured axes (the jitter varies only the mutation vector, the gate never fires, and the Markov stage is already inside the collapse's proposal distribution; the promoted evolve applies its own jitter regardless, so the simpler arm loses nothing). Constrained clears validity with the best readability/novelty but is barred by the rich-alphabet requirement; markov measures 2% valid at 16×16 (raw proposals are never a production path); random is 46% valid and 53% training copies — the honest floor. All arms pass the ≤250 ms gate with ~40× headroom (wfc 6.3 ms measured). Human pairwise preference recorded not-collected (owner-deferred). markov_grid gained the size-derivation fix, 8×8 pins intact)

- `research/decision_records/0031-wfc-generation-adoption.md`
- `packages/mecha_engine/src/mecha_engine/generation/wfc.py`
- `labs/wfc_grid/test_package_wfc_parity.py` (cycle 10 B3 · ENGINE · Phase B: the bake-off winner ADOPTED — `mecha_engine.generation` gains the WFC surface (`train_wfc_model` / `generate_wfc_grid` / `build_wfc_corpus`) as an additive seam, a verbatim semantic port pinned lab-side over trained models and full corpora (identical dicts, RNG streams, error strings); every existing generation surface byte-identical, the contract's public-surface pin widened deliberately. The hybrid refutation is recorded with its named re-opener (an extended-descriptor bake-off where the jitter/gate stages could show value); the constrained stabilizer remains the 4-token parent-based path and evolve's inner loop stays on it — moving it is a future decision with its own evidence. Stdlib holds at 6.3 ms/candidate measured)

- `research/experiment_reports/2026-07-08-phase-b-gate.md`
- `data/generated_grids/wfc_16x16/` (50 candidates) (cycle 10 B4 · ENGINE · **Phase B GATE — GREEN**: the generation layer is no longer missing — the WFC lab (B1, with pure collapse's 2% self-refutation recorded), the real five-arm bake-off (B2, WFC wins at validity 1.0 / 6.3 ms, the documented hybrid REFUTED under the pre-registered rule), the engine adoption (B3, DR 0031, additive seam parity-pinned), and the regenerated 16×16 generated corpus. Honest remainders named: evolve's inner loop stays constrained pending its own evidence; the hybrid re-opener is an extended-descriptor bake-off; WFC candidates carry no parent lineage yet; readability remains the 8×8-calibrated proxy. Phase B checked off in `docs/gap-analysis.md`; cycle 10 archives to `audits/complete/10/`; cycle 11 opens Phase C — the animation system)

- `research/experiment_reports/2026-07-08-clip-model.md`
- `research/algorithm_cards/clip_model.md`
- `labs/animation_system/clip_model.py` (+ `test_clip_model.py`)
- `data/animation_system/clip_model_stage0.json` (cycle 11 C1 · ENGINE · Phase C: the animation system's first layer — CLIPS as bounded frame sequences over the promoted state projections, extending the proven visual-only-projection thesis into time. Frame = state track → all-or-nothing whole-body motion → per-role motion (antenna/sensor sway, effect flicker — the DR 0015 WATCH seam recorded per role; limb/joint/decoration named as the next increment, not improvised). Hard rules pinned: frames are valid render surfaces (in-bounds/palette-clean/no invented cells/no overlaps), the genome is never mutated, idle frame 0 is the identity, every clip moves; size-parametric (16×16 + 8×8). 950/950 corpus frames pass every gate; the intra-clip delta table (idle 0.032 → ill 0.768) is C2's transition baseline)

- `research/experiment_reports/2026-07-08-transition-graph.md`
- `labs/animation_system/transition_graph.py` (+ `test_transition_graph.py`)
- `data/animation_system/transition_graph_stage0.json` (cycle 11 C2 · ENGINE · Phase C: the clip transition graph — hub-and-spoke through idle with self-loops (a clip that cannot loop cannot play) — measured against the dossier's ≥80% bar under a PRE-REGISTERED metric (a cut may not be jerkier than the jerkiest step already inside either clip; near-static clips fall back to the corpus intra-max, never a free pass). **Validity 0.9877 over 650 measured transitions** — eleven of thirteen edges perfect; the only imperfect edges are idle↔ill at 0.92 (illness onset is the jerkiest cut — sensible biology, recorded per edge with the client-side softening option named). Boundary deltas p50 0.029 / p95 0.841)

- `research/experiment_reports/2026-07-08-animstate-950.md`
- `labs/animation_system/animstate_dataset.py` (+ `test_animstate_dataset.py`)
- `data/animation_system/animstate_950.json` (+ stage0 + README) (cycle 11 C3 · ENGINE · Phase C: the documented animstate dataset regenerated at clip-frame resolution over the 16×16 corpus — 950 labeled (grid, palette, clip, state, frame) samples, full creature×clip×frame coverage, in-bounds and palette-clean 1.0, deterministic; named by its real size with a `supersedes` block citing the documented `animstate_300` and its minimum (the og 8×8 dataset kept as history). The named consumer is Phase D's animation-preference learner)

- `research/experiment_reports/2026-07-08-packet-clip-contract.md`
- `packages/mecha_engine/src/mecha_engine/genome/animation.py`
- `labs/animation_system/test_package_clip_parity.py`
- `workshop/server/workshop_server.py` (`/api/preview/clip`) (cycle 11 C4 · ENGINE · Phase C: the render packet carries the documented animation contract — the clip model promoted verbatim into `mecha_engine.genome` (frame-for-frame parity pins), `render_packet_v2` gains `clip`/`frame_index` as a DR 0013 additive rung whose `animation` field becomes the dossier's block (clip/frame_index/frame_count/anchors) with the frame's cells as the packet's cells; validation stays on the projected grid, the moved frame is presentation after the v1 gate; SLIP `animation_vocab` bounds clips exactly as states with honest-mood idle fallback; `clip=None` byte-identical — proven by the pre-existing animation parity suite passing unmodified. The workshop scrubs a real clip end-to-end through the promoted rung)

- `research/experiment_reports/2026-07-08-effects-contract.md`
- `packages/mecha_engine/src/mecha_engine/genome/animation.py` + `labs/grid_genome/animation_states.py` (the twins)
- `workshop/shared/draw.js` (`applyEffects`) (cycle 11 C5 · ENGINE · Phase C: the retro effects pipeline contract-side — `effects` in the documented list shape + `effect_parameters` with deterministic engine-derived values (glitch amplitude IS the engine's stress number, riding the ill display; crt_bloom rides beg; scanline+lcd_ghosting are the standing LCD identity) + `ui_hints` mirroring the T16 thresholds, on every v2 packet in verbatim lab/package twins (the parity suite failed loudly at 134 when momentarily one-sided — the discipline working). Consumer proof: the shared drawer rasterizes the declared effects (scanline, glitch row-shear, bloom halo; lcd_ghosting honestly skipped as a temporal live-player concern for Phase F). Workshop 60 green)

- `research/experiment_reports/2026-07-08-phase-c-gate.md` (cycle 11 C6 · ENGINE · **Phase C GATE — GREEN**: the animation system exists — clips over the promoted projections (C1), transitions measured at 0.9877 against the 0.80 bar under a pre-registered metric (C2), `animstate_950` superseding the documented dataset (C3), the packet carrying the dossier's animation block as a byte-identical-off rung (C4), and the effects/ui_hints contract with the drawer consumer proof (C5). Honest remainders named: limb/joint/decoration per-role motion; lcd_ghosting's temporal rasterization; live clip DRIVING through the graph (Phase F's consumption); the bandit consumer (Phase D); clip-frame exports. Phase C checked off in `docs/gap-analysis.md`; cycle 11 archives to `audits/complete/11/`; cycle 12 opens Phase D — the intelligence threads, the core ML thesis)

- `research/experiment_reports/2026-07-08-micro-thread-fleet-contract.md`
- `research/algorithm_cards/micro_thread_fleet_contract.md`
- `labs/micro_threads/thread_fleet.py` (+ `test_thread_fleet.py`)
- `data/micro_threads/micro_thread_fleet_contract_stage0.json` (cycle 12 D1 · ENGINE · Phase D: the ONE contract the documented ~11-thread micro-learner fleet grows through — a fleet thread is `(name, observe, signal)`: observe is the pure/deterministic/bounded online learning step living in the episode loop (decide stays a pure read, DR 0009), signal emits the historical `{name, input, output, confidence, explanation, effects}` shape additively combined as effects×confidence. The switchboard (lab + package twin `learning/threads.py`, parity-pinned) gains one additive seam line under THE OPT-IN RULE: fleet threads run ONLY on explicit `learning_switches[name] is True`, so the frozen baseline — the phase's ablation control — is byte-identical everywhere: 48/48 frozen replay decisions identical lab-and-package with zero fleet appearances; all 19 lab suites + 291 package tests green. The `hunger_forecast` pipe cleaner (8-sample trend forecaster) proves the pipe end-to-end: first anticipatory signal at tick 2 vs the reactive 0.65 threshold at tick 4, utilities moved 26/48 ticks, honest cold start (confidence 0, no effects). Honest remainder: 0 decision flips at LCD scale — effect calibration on replayed histories is D2's assignment, recorded)

Stage 0 and Stage 1 established:

- Stage 0: define the research ontology and evaluation vocabulary.
- Stage 1: turn the source list into a structured literature map.

No algorithm should graduate into `packages/` until it has an algorithm card,
an experiment report, a metric report, and a decision record.
