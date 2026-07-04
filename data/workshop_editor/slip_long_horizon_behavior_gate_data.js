window.MECHAGOTCHI_SLIP_LONG_HORIZON_BEHAVIOR_GATE = {
  "artifact_id": "slip_long_horizon_behavior_gate_stage0",
  "status": "research_slip_long_horizon_behavior_gate_no_package_code",
  "date": "2026-05-13",
  "metrics": {
    "long_horizon_success_rate": 1.0,
    "invalid_probe_rejection_rate": 1.0,
    "mean_switchboard_survival_ratio": 1.0,
    "mean_idle_survival_ratio": 0.114583,
    "mean_switchboard_need_balance": 0.782108,
    "mean_idle_need_balance": 0.090432,
    "mean_need_balance_delta_vs_idle": 0.691676,
    "mean_held_out_switchboard_survival_ratio": 1.0,
    "mean_held_out_idle_survival_ratio": 0.114583,
    "long_horizon_behavior_tests_specified": true,
    "manual_readability_calibration_ready": false
  },
  "profile_results": [
    {
      "profile_id": "slip_lcd_seed",
      "gate_started": true,
      "validation_ok": true,
      "selected_offspring_grid_id": "slip_lcd_seed_constrained_007_offspring_core_growth",
      "selected_switchboard_survival_ratio": 1.0,
      "selected_idle_survival_ratio": 0.114583,
      "held_out_candidate_count": 6,
      "held_out_switchboard_full_survival_count": 6,
      "held_out_idle_death_count": 6,
      "manual_readability_status": "not_collected"
    },
    {
      "profile_id": "slip_gray_stable",
      "gate_started": true,
      "validation_ok": true,
      "selected_offspring_grid_id": "slip_gray_stable_constrained_004_offspring_stability_tune",
      "selected_switchboard_survival_ratio": 1.0,
      "selected_idle_survival_ratio": 0.125,
      "held_out_candidate_count": 6,
      "held_out_switchboard_full_survival_count": 6,
      "held_out_idle_death_count": 6,
      "manual_readability_status": "not_collected"
    },
    {
      "profile_id": "slip_amber_social",
      "gate_started": true,
      "validation_ok": true,
      "selected_offspring_grid_id": "slip_amber_social_constrained_004_offspring_stability_tune",
      "selected_switchboard_survival_ratio": 1.0,
      "selected_idle_survival_ratio": 0.104167,
      "held_out_candidate_count": 6,
      "held_out_switchboard_full_survival_count": 6,
      "held_out_idle_death_count": 6,
      "manual_readability_status": "not_collected"
    }
  ],
  "closed_states": [
    "held_out_long_horizon_behavior_tests",
    "offspring_long_horizon_survival_probe",
    "invalid_profile_rejected_before_long_horizon"
  ],
  "blocked_states": [
    "runtime_jsonschema_validation",
    "profile_weighted_evolution",
    "package_runtime_lifecycle_integration",
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
  "decision": "prototype_slip_long_horizon_behavior_gate",
  "next_research_step": "Collect manual readability ratings and calibrate proxy readability thresholds before claiming profile-weighted evolution."
};
