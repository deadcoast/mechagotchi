window.MECHAGOTCHI_SLIP_OFFSPRING_LINEAGE_GATE = {
  "artifact_id": "slip_offspring_lineage_gate_stage0",
  "status": "research_slip_offspring_lineage_gate_no_package_code",
  "date": "2026-05-13",
  "metrics": {
    "offspring_gate_success_rate": 1.0,
    "invalid_probe_rejection_rate": 1.0,
    "mean_selected_offspring_score": 0.941742,
    "mean_selected_offspring_need_balance": 0.793865,
    "mean_selected_offspring_survival_ratio": 1.0,
    "distinct_selected_offspring_ids": 3,
    "distinct_selected_offspring_niches": 3,
    "replace_parent_count": 0,
    "add_archive_niche_count": 2,
    "hold_parent_count": 1,
    "offspring_mutation_selection_specified": true,
    "lineage_replacement_policy_specified": true
  },
  "profile_results": [
    {
      "profile_id": "slip_lcd_seed",
      "gate_started": true,
      "validation_ok": true,
      "parent_grid_id": "slip_lcd_seed_constrained_007",
      "selected_offspring_id": "slip_lcd_seed_constrained_007_offspring_core_growth",
      "selected_offspring_score": 0.952005,
      "selected_archive_niche": "2,2,1,3,4,3,2",
      "lineage_action": "add_archive_niche",
      "lineage_reason": "child opens a qualified archive niche without displacing parent"
    },
    {
      "profile_id": "slip_gray_stable",
      "gate_started": true,
      "validation_ok": true,
      "parent_grid_id": "slip_gray_stable_constrained_004",
      "selected_offspring_id": "slip_gray_stable_constrained_004_offspring_stability_tune",
      "selected_offspring_score": 0.920873,
      "selected_archive_niche": "2,1,1,3,4,4,1",
      "lineage_action": "hold_parent",
      "lineage_reason": "parent remains elite until child beats replacement threshold"
    },
    {
      "profile_id": "slip_amber_social",
      "gate_started": true,
      "validation_ok": true,
      "parent_grid_id": "slip_amber_social_constrained_004",
      "selected_offspring_id": "slip_amber_social_constrained_004_offspring_stability_tune",
      "selected_offspring_score": 0.952347,
      "selected_archive_niche": "2,0,2,4,4,3,1",
      "lineage_action": "add_archive_niche",
      "lineage_reason": "child opens a qualified archive niche without displacing parent"
    }
  ],
  "closed_states": [
    "offspring_mutation_selection",
    "lineage_replacement_policy",
    "invalid_profile_rejected_before_offspring_lineage",
    "runtime_parent_to_offspring_selection_trace"
  ],
  "blocked_states": [
    "runtime_jsonschema_validation",
    "profile_weighted_evolution",
    "package_runtime_lifecycle_integration",
    "held_out_long_horizon_behavior_tests",
    "manual_readability_calibration",
    "persistent_multigeneration_lineage_runner",
    "png_adam7_interlace_decoder",
    "apng_decoder",
    "full_png_conformance",
    "spritesheet_packed_rotation_trim_decoder",
    "runtime_animation_playback",
    "full_project_format_coverage",
    "embedded_png_metadata_writer",
    "project_file_native_metadata_writer",
    "profile_authoring_usability_pilot",
    "community_profile_packs"
  ],
  "decision": "prototype_slip_offspring_lineage_gate",
  "next_research_step": "Run held-out long-horizon behavior tests and manual readability calibration before claiming profile-weighted evolution."
};
