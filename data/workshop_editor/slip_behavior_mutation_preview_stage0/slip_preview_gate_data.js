window.MECHAGOTCHI_SLIP_PREVIEW_GATES = {
  "report": {
    "artifact_id": "slip_behavior_mutation_preview_stage0",
    "status": "research_slip_behavior_mutation_preview_no_package_code",
    "profile_count": 3,
    "behavior_preview_count": 3,
    "mutation_preview_count": 3,
    "invalid_probe_count": 2,
    "invalid_probe_rejected_count": 2,
    "metrics": {
      "preview_gate_success_rate": 1.0,
      "profile_weight_effects_observed": true,
      "mutation_caps_respected": true,
      "invalid_probe_rejection_rate": 1.0,
      "palette_shift_blocked_by_single_palette_profiles": 3
    },
    "closed_states": [
      "behavior_preview_gate",
      "mutation_preview_gate",
      "profile_weights_drive_preview_outputs",
      "mutation_caps_bound_preview_outputs",
      "invalid_profile_rejected_before_preview"
    ],
    "blocked_states": [
      "runtime_jsonschema_validation",
      "declared_dependency_manifest",
      "profile_weighted_evolution",
      "package_runtime_lifecycle_integration",
      "png_adam7_interlace_decoder",
      "apng_decoder",
      "full_png_conformance",
      "spritesheet_packed_rotation_trim_decoder",
      "runtime_animation_playback",
      "full_project_format_coverage",
      "embedded_native_metadata_writer",
      "profile_authoring_usability_pilot",
      "community_profile_packs"
    ],
    "decision": "prototype_behavior_mutation_preview_gate"
  },
  "profile_results": [
    {
      "profile_id": "slip_lcd_seed",
      "profile_path": "data/slips/valid/slip_lcd_seed.json",
      "grid_path": "data/slips/multi_profile_generation_stage0/slip_lcd_seed/slip_lcd_seed_constrained_000.json",
      "validation": {
        "ok": true,
        "profile_id": "slip_lcd_seed",
        "grid_id": "slip_lcd_seed_constrained_000",
        "profile_validation": {
          "ok": true,
          "migration": {
            "ok": true,
            "source_version": "0.1.0",
            "target_version": "0.1.0",
            "action": "accept_current_no_migration",
            "errors": []
          },
          "dependency_free": {
            "source_path": null,
            "ok": true,
            "errors": [],
            "error_families": []
          },
          "pydantic": {
            "source_path": "authoring_draft",
            "ok": true,
            "profile_id": "slip_lcd_seed",
            "errors": [],
            "error_families": []
          },
          "errors": [],
          "error_families": []
        },
        "grid_validation": {
          "ok": true,
          "errors": []
        },
        "alignment": {
          "ok": true,
          "errors": []
        },
        "preview_surfaces": [
          "behavior_preview",
          "mutation_preview"
        ],
        "errors": [],
        "error_families": []
      },
      "behavior_preview": {
        "profile_id": "slip_lcd_seed",
        "preview_model": "deterministic_profile_weight_proxy",
        "scenario_count": 3,
        "signals": {
          "social_pull": 0.385,
          "exploration_pull": 0.4625,
          "rest_pull": 0.49,
          "mutation_pressure": 0.4225,
          "mutation_caution": 0.5625
        },
        "scenarios": [
          {
            "scenario_id": "attention_gap",
            "selected_action": "play",
            "action_scores": {
              "idle": 0.25695,
              "mutate": 0.17745,
              "play": 0.3682,
              "sleep": 0.2842
            },
            "confidence": 0.3682,
            "explanation": "Neediness and bond raise the user-facing play prompt."
          },
          {
            "scenario_id": "low_energy_tick",
            "selected_action": "sleep",
            "action_scores": {
              "idle": 0.1666,
              "mutate": 0.07605,
              "play": 0.0693,
              "sleep": 0.46385
            },
            "confidence": 0.46385,
            "explanation": "Sleepiness and stability raise the rest response."
          },
          {
            "scenario_id": "safe_novelty_window",
            "selected_action": "play",
            "action_scores": {
              "idle": 0.135,
              "mutate": 0.13815,
              "play": 0.22655,
              "sleep": 0.1078
            },
            "confidence": 0.22655,
            "explanation": "Curiosity and novelty raise mutation interest while stability tempers it."
          }
        ],
        "effect_fingerprint": [
          0.385,
          0.4625,
          0.49,
          0.4225,
          0.5625
        ],
        "limitations": [
          "Preview only: no lifecycle state is mutated.",
          "Preview only: no reinforcement-learning policy is trained or adopted."
        ]
      },
      "mutation_preview": {
        "profile_id": "slip_lcd_seed",
        "grid_id": "slip_lcd_seed_constrained_000",
        "preview_model": "deterministic_cap_projection_no_mutation_applied",
        "body_mass": 10,
        "mutable_cell_count": 13,
        "organ_cell_count": 3,
        "budgets": {
          "cell_mutation_budget": 2,
          "cell_mutation_budget_cap": 2,
          "organ_shift_budget": 1,
          "organ_shift_budget_cap": 1,
          "symmetry_break_budget": 1,
          "symmetry_break_budget_cap": 1
        },
        "caps": {
          "cell_mutation_rate_max": 0.15,
          "organ_shift_rate_max": 0.05,
          "palette_shift_rate_max": 0.05,
          "symmetry_break_rate_max": 0.05
        },
        "cell_mutation_candidates": [
          {
            "coordinate": [
              2,
              2
            ],
            "organ": "core",
            "role": "body",
            "mutation_weight": 0.1
          },
          {
            "coordinate": [
              3,
              2
            ],
            "organ": "core",
            "role": "body",
            "mutation_weight": 0.1
          }
        ],
        "organ_shift_candidates": [
          {
            "coordinate": [
              3,
              4
            ],
            "organ": "expression",
            "role": "mouth",
            "mutation_weight": 0.1
          }
        ],
        "palette_shift": {
          "allowed": false,
          "current_palette": "lcd_green",
          "allowed_palettes": [
            "lcd_green"
          ],
          "reason": "single_allowed_palette_blocks_preview_shift"
        },
        "caps_respected": true,
        "limitations": [
          "Preview only: no grid cells are changed.",
          "Preview only: does not prove offspring validity or archive impact."
        ]
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "profile_path": "data/slips/valid/slip_gray_stable.json",
      "grid_path": "data/slips/multi_profile_generation_stage0/slip_gray_stable/slip_gray_stable_constrained_000.json",
      "validation": {
        "ok": true,
        "profile_id": "slip_gray_stable",
        "grid_id": "slip_gray_stable_constrained_000",
        "profile_validation": {
          "ok": true,
          "migration": {
            "ok": true,
            "source_version": "0.1.0",
            "target_version": "0.1.0",
            "action": "accept_current_no_migration",
            "errors": []
          },
          "dependency_free": {
            "source_path": null,
            "ok": true,
            "errors": [],
            "error_families": []
          },
          "pydantic": {
            "source_path": "authoring_draft",
            "ok": true,
            "profile_id": "slip_gray_stable",
            "errors": [],
            "error_families": []
          },
          "errors": [],
          "error_families": []
        },
        "grid_validation": {
          "ok": true,
          "errors": []
        },
        "alignment": {
          "ok": true,
          "errors": []
        },
        "preview_surfaces": [
          "behavior_preview",
          "mutation_preview"
        ],
        "errors": [],
        "error_families": []
      },
      "behavior_preview": {
        "profile_id": "slip_gray_stable",
        "preview_model": "deterministic_profile_weight_proxy",
        "scenario_count": 3,
        "signals": {
          "social_pull": 0.2775,
          "exploration_pull": 0.2625,
          "rest_pull": 0.6675,
          "mutation_pressure": 0.2275,
          "mutation_caution": 0.74
        },
        "scenarios": [
          {
            "scenario_id": "attention_gap",
            "selected_action": "sleep",
            "action_scores": {
              "idle": 0.34215,
              "mutate": 0.09555,
              "play": 0.24555,
              "sleep": 0.38715
            },
            "confidence": 0.38715,
            "explanation": "Neediness and bond raise the user-facing play prompt."
          },
          {
            "scenario_id": "low_energy_tick",
            "selected_action": "sleep",
            "action_scores": {
              "idle": 0.22695,
              "mutate": 0.04095,
              "play": 0.04995,
              "sleep": 0.62715
            },
            "confidence": 0.62715,
            "explanation": "Sleepiness and stability raise the rest response."
          },
          {
            "scenario_id": "safe_novelty_window",
            "selected_action": "idle",
            "action_scores": {
              "idle": 0.1776,
              "mutate": 0.00445,
              "play": 0.1392,
              "sleep": 0.14685
            },
            "confidence": 0.1776,
            "explanation": "Curiosity and novelty raise mutation interest while stability tempers it."
          }
        ],
        "effect_fingerprint": [
          0.2775,
          0.2625,
          0.6675,
          0.2275,
          0.74
        ],
        "limitations": [
          "Preview only: no lifecycle state is mutated.",
          "Preview only: no reinforcement-learning policy is trained or adopted."
        ]
      },
      "mutation_preview": {
        "profile_id": "slip_gray_stable",
        "grid_id": "slip_gray_stable_constrained_000",
        "preview_model": "deterministic_cap_projection_no_mutation_applied",
        "body_mass": 11,
        "mutable_cell_count": 15,
        "organ_cell_count": 4,
        "budgets": {
          "cell_mutation_budget": 2,
          "cell_mutation_budget_cap": 2,
          "organ_shift_budget": 1,
          "organ_shift_budget_cap": 1,
          "symmetry_break_budget": 1,
          "symmetry_break_budget_cap": 1
        },
        "caps": {
          "cell_mutation_rate_max": 0.1,
          "organ_shift_rate_max": 0.05,
          "palette_shift_rate_max": 0.05,
          "symmetry_break_rate_max": 0.05
        },
        "cell_mutation_candidates": [
          {
            "coordinate": [
              3,
              2
            ],
            "organ": "core",
            "role": "body",
            "mutation_weight": 0.1
          },
          {
            "coordinate": [
              4,
              2
            ],
            "organ": "core",
            "role": "body",
            "mutation_weight": 0.1
          }
        ],
        "organ_shift_candidates": [
          {
            "coordinate": [
              4,
              4
            ],
            "organ": "expression",
            "role": "mouth",
            "mutation_weight": 0.1
          }
        ],
        "palette_shift": {
          "allowed": false,
          "current_palette": "gameboy_gray",
          "allowed_palettes": [
            "gameboy_gray"
          ],
          "reason": "single_allowed_palette_blocks_preview_shift"
        },
        "caps_respected": true,
        "limitations": [
          "Preview only: no grid cells are changed.",
          "Preview only: does not prove offspring validity or archive impact."
        ]
      }
    },
    {
      "profile_id": "slip_amber_social",
      "profile_path": "data/slips/valid/slip_amber_social.json",
      "grid_path": "data/slips/multi_profile_generation_stage0/slip_amber_social/slip_amber_social_constrained_000.json",
      "validation": {
        "ok": true,
        "profile_id": "slip_amber_social",
        "grid_id": "slip_amber_social_constrained_000",
        "profile_validation": {
          "ok": true,
          "migration": {
            "ok": true,
            "source_version": "0.1.0",
            "target_version": "0.1.0",
            "action": "accept_current_no_migration",
            "errors": []
          },
          "dependency_free": {
            "source_path": null,
            "ok": true,
            "errors": [],
            "error_families": []
          },
          "pydantic": {
            "source_path": "authoring_draft",
            "ok": true,
            "profile_id": "slip_amber_social",
            "errors": [],
            "error_families": []
          },
          "errors": [],
          "error_families": []
        },
        "grid_validation": {
          "ok": true,
          "errors": []
        },
        "alignment": {
          "ok": true,
          "errors": []
        },
        "preview_surfaces": [
          "behavior_preview",
          "mutation_preview"
        ],
        "errors": [],
        "error_families": []
      },
      "behavior_preview": {
        "profile_id": "slip_amber_social",
        "preview_model": "deterministic_profile_weight_proxy",
        "scenario_count": 3,
        "signals": {
          "social_pull": 0.54,
          "exploration_pull": 0.535,
          "rest_pull": 0.3625,
          "mutation_pressure": 0.4775,
          "mutation_caution": 0.4775
        },
        "scenarios": [
          {
            "scenario_id": "attention_gap",
            "selected_action": "play",
            "action_scores": {
              "idle": 0.2085,
              "mutate": 0.20055,
              "play": 0.4846,
              "sleep": 0.21025
            },
            "confidence": 0.4846,
            "explanation": "Neediness and bond raise the user-facing play prompt."
          },
          {
            "scenario_id": "low_energy_tick",
            "selected_action": "sleep",
            "action_scores": {
              "idle": 0.12325,
              "mutate": 0.08595,
              "play": 0.0972,
              "sleep": 0.3542
            },
            "confidence": 0.3542,
            "explanation": "Sleepiness and stability raise the rest response."
          },
          {
            "scenario_id": "safe_novelty_window",
            "selected_action": "play",
            "action_scores": {
              "idle": 0.1146,
              "mutate": 0.18145,
              "play": 0.2791,
              "sleep": 0.07975
            },
            "confidence": 0.2791,
            "explanation": "Curiosity and novelty raise mutation interest while stability tempers it."
          }
        ],
        "effect_fingerprint": [
          0.54,
          0.535,
          0.3625,
          0.4775,
          0.4775
        ],
        "limitations": [
          "Preview only: no lifecycle state is mutated.",
          "Preview only: no reinforcement-learning policy is trained or adopted."
        ]
      },
      "mutation_preview": {
        "profile_id": "slip_amber_social",
        "grid_id": "slip_amber_social_constrained_000",
        "preview_model": "deterministic_cap_projection_no_mutation_applied",
        "body_mass": 10,
        "mutable_cell_count": 14,
        "organ_cell_count": 4,
        "budgets": {
          "cell_mutation_budget": 3,
          "cell_mutation_budget_cap": 3,
          "organ_shift_budget": 1,
          "organ_shift_budget_cap": 1,
          "symmetry_break_budget": 1,
          "symmetry_break_budget_cap": 1
        },
        "caps": {
          "cell_mutation_rate_max": 0.15,
          "organ_shift_rate_max": 0.05,
          "palette_shift_rate_max": 0.05,
          "symmetry_break_rate_max": 0.05
        },
        "cell_mutation_candidates": [
          {
            "coordinate": [
              2,
              2
            ],
            "organ": "core",
            "role": "body",
            "mutation_weight": 0.1
          },
          {
            "coordinate": [
              3,
              2
            ],
            "organ": "core",
            "role": "body",
            "mutation_weight": 0.1
          },
          {
            "coordinate": [
              4,
              2
            ],
            "organ": "core",
            "role": "body",
            "mutation_weight": 0.1
          }
        ],
        "organ_shift_candidates": [
          {
            "coordinate": [
              3,
              4
            ],
            "organ": "expression",
            "role": "mouth",
            "mutation_weight": 0.1
          }
        ],
        "palette_shift": {
          "allowed": false,
          "current_palette": "amber_terminal",
          "allowed_palettes": [
            "amber_terminal"
          ],
          "reason": "single_allowed_palette_blocks_preview_shift"
        },
        "caps_respected": true,
        "limitations": [
          "Preview only: no grid cells are changed.",
          "Preview only: does not prove offspring validity or archive impact."
        ]
      }
    }
  ]
};
