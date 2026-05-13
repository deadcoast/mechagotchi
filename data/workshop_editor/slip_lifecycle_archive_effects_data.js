window.MECHAGOTCHI_SLIP_LIFECYCLE_ARCHIVE_EFFECTS = {
  "report": {
    "artifact_id": "slip_lifecycle_archive_effects_stage0",
    "status": "research_slip_lifecycle_archive_effects_no_package_code",
    "profile_count": 3,
    "preview_request_success_count": 3,
    "lifecycle_effect_count": 3,
    "archive_effect_count": 3,
    "invalid_probe_count": 2,
    "invalid_probe_rejected_count": 2,
    "metrics": {
      "preview_request_success_rate": 1.0,
      "lifecycle_effect_success_rate": 1.0,
      "archive_effect_success_rate": 1.0,
      "invalid_probe_rejection_rate": 1.0,
      "distinct_preview_fingerprints": 3,
      "distinct_lifecycle_fingerprints": 3,
      "distinct_archive_fingerprints": 3,
      "profile_weight_effects_measured": true,
      "preview_to_lifecycle_archive_effects_measured": true,
      "mean_lifecycle_need_balance": 0.793865,
      "mean_lifecycle_survival_ratio": 1.0,
      "mean_archive_qd_score": 7.671145
    },
    "parameters": {
      "candidate_limit": 12,
      "lifecycle_ticks": 24,
      "archive_lifecycle_ticks": 12,
      "rng_seed": 20260512
    },
    "closed_states": [
      "profile_preview_signal_measurement",
      "slip_preview_lifecycle_effect_probe",
      "slip_preview_archive_effect_probe",
      "invalid_profile_rejected_before_lifecycle_archive"
    ],
    "blocked_states": [
      "runtime_jsonschema_validation",
      "declared_dependency_manifest",
      "profile_weighted_evolution",
      "engine_lifecycle_behavior_integration",
      "archive_selection_policy_integration",
      "png_adam7_interlace_decoder",
      "apng_decoder",
      "full_png_conformance",
      "spritesheet_variant_layout_coverage",
      "full_project_format_coverage",
      "embedded_png_metadata_writer",
      "project_file_native_metadata_writer",
      "profile_authoring_usability_pilot",
      "community_profile_packs"
    ],
    "decision": "prototype_slip_lifecycle_archive_effect_probe"
  },
  "profile_results": [
    {
      "probe_id": "slip_lcd_seed_effect_probe",
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
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
      "effects_started": true,
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
      },
      "preview_signals": {
        "social_pull": 0.385,
        "exploration_pull": 0.4625,
        "rest_pull": 0.49,
        "mutation_pressure": 0.4225,
        "mutation_caution": 0.5625
      },
      "lifecycle_effect": {
        "profile_id": "slip_lcd_seed",
        "grid_id": "slip_lcd_seed_constrained_000",
        "policy": "switchboard",
        "ticks_requested": 24,
        "survival_ticks": 24,
        "survival_ratio": 1.0,
        "alive": true,
        "death_cause": null,
        "need_balance": 0.802552,
        "recovery_events": 4,
        "action_counts": {
          "feed": 4,
          "play": 16,
          "sleep": 4,
          "idle": 0,
          "mutate": 0
        },
        "action_ratios": {
          "feed": 0.166667,
          "play": 0.666667,
          "sleep": 0.166667,
          "idle": 0.0,
          "mutate": 0.0
        },
        "final_state": {
          "hunger": 0.6888,
          "energy": 0.288,
          "stress": 0.0,
          "bond": 1.0,
          "grid_stability": 0.976
        }
      },
      "archive_effect": {
        "profile_id": "slip_lcd_seed",
        "archive_id": "map_elites_extended_stage0",
        "descriptor_names": [
          "body_mass",
          "sensor_count",
          "symmetry",
          "readability",
          "lifecycle_survival",
          "mutation_stability",
          "behavior_neediness"
        ],
        "descriptor_dimensions": 7,
        "candidate_count": 12,
        "lifecycle_ticks": 12,
        "occupied_niches": 7,
        "coverage": 9e-05,
        "best_fitness": 0.973629,
        "mean_elite_fitness": 0.960404,
        "qd_score": 6.722827,
        "elite_count": 7,
        "score_component_means": {
          "bond": 0.993,
          "mutation_stability": 0.9775,
          "readability": 0.847891,
          "slip_alignment": 1.0,
          "survival": 1.0,
          "validity": 1.0
        },
        "descriptor_metric_means": {
          "behavior_neediness": 0.4,
          "body_mass": 9.857143,
          "lifecycle_survival": 1.0,
          "mutation_stability": 0.9775,
          "readability": 0.847891,
          "sensor_count": 2.142857,
          "symmetry": 0.521787
        },
        "representative_elites": [
          {
            "grid_id": "slip_lcd_seed_constrained_009",
            "fitness": 0.964767,
            "descriptor": {
              "names": [
                "body_mass",
                "sensor_count",
                "symmetry",
                "readability",
                "lifecycle_survival",
                "mutation_stability",
                "behavior_neediness"
              ],
              "values": [
                1,
                1,
                1,
                4,
                4,
                4,
                1
              ],
              "key": "1,1,1,4,4,4,1",
              "metrics": {
                "body_mass": 9,
                "sensor_count": 2,
                "symmetry": 0.333333,
                "readability": 0.866069,
                "lifecycle_survival": 1.0,
                "mutation_stability": 0.9775,
                "behavior_neediness": 0.4
              }
            },
            "score_components": {
              "survival": 1.0,
              "readability": 0.866069,
              "validity": 1.0,
              "bond": 0.993,
              "mutation_stability": 0.9775,
              "slip_alignment": 1.0
            }
          },
          {
            "grid_id": "slip_lcd_seed_constrained_011",
            "fitness": 0.967783,
            "descriptor": {
              "names": [
                "body_mass",
                "sensor_count",
                "symmetry",
                "readability",
                "lifecycle_survival",
                "mutation_stability",
                "behavior_neediness"
              ],
              "values": [
                1,
                1,
                2,
                4,
                4,
                4,
                1
              ],
              "key": "1,1,2,4,4,4,1",
              "metrics": {
                "body_mass": 8,
                "sensor_count": 2,
                "symmetry": 0.545455,
                "readability": 0.878639,
                "lifecycle_survival": 1.0,
                "mutation_stability": 0.9775,
                "behavior_neediness": 0.4
              }
            },
            "score_components": {
              "survival": 1.0,
              "readability": 0.878639,
              "validity": 1.0,
              "bond": 0.993,
              "mutation_stability": 0.9775,
              "slip_alignment": 1.0
            }
          },
          {
            "grid_id": "slip_lcd_seed_constrained_008",
            "fitness": 0.944192,
            "descriptor": {
              "names": [
                "body_mass",
                "sensor_count",
                "symmetry",
                "readability",
                "lifecycle_survival",
                "mutation_stability",
                "behavior_neediness"
              ],
              "values": [
                1,
                2,
                1,
                3,
                4,
                4,
                1
              ],
              "key": "1,2,1,3,4,4,1",
              "metrics": {
                "body_mass": 8,
                "sensor_count": 3,
                "symmetry": 0.5,
                "readability": 0.780343,
                "lifecycle_survival": 1.0,
                "mutation_stability": 0.9775,
                "behavior_neediness": 0.4
              }
            },
            "score_components": {
              "survival": 1.0,
              "readability": 0.780343,
              "validity": 1.0,
              "bond": 0.993,
              "mutation_stability": 0.9775,
              "slip_alignment": 1.0
            }
          }
        ]
      },
      "preview_to_lifecycle_links": {
        "social_pull_to_play": {
          "preview_signal": 0.385,
          "lifecycle_action": "play",
          "action_count": 16,
          "action_ratio": 0.666667,
          "final_bond": 1.0
        },
        "rest_pull_to_sleep": {
          "preview_signal": 0.49,
          "lifecycle_action": "sleep",
          "action_count": 4,
          "action_ratio": 0.166667,
          "final_energy": 0.288
        },
        "mutation_pressure_to_archive": {
          "preview_signal": 0.4225,
          "cell_mutation_budget": 2,
          "organ_shift_budget": 1,
          "archive_mutation_stability_mean": 0.9775
        },
        "mutation_caution_to_archive": {
          "preview_signal": 0.5625,
          "caps_respected": true,
          "archive_best_fitness": 0.973629,
          "archive_qd_score": 6.722827
        }
      },
      "preview_effect_fingerprint": [
        0.385,
        0.4625,
        0.49,
        0.4225,
        0.5625
      ],
      "lifecycle_effect_fingerprint": [
        1.0,
        0.802552,
        0.166667,
        0.166667,
        0.666667,
        0.166667,
        0.0,
        0.0,
        1.0,
        0.288
      ],
      "archive_effect_fingerprint": [
        7.0,
        9e-05,
        0.973629,
        0.960404,
        6.722827,
        1.0,
        0.4,
        0.9775,
        1.0
      ],
      "measured_effect_fingerprint": {
        "lifecycle_survival_ratio": 1.0,
        "lifecycle_need_balance": 0.802552,
        "lifecycle_recovery_rate": 0.166667,
        "lifecycle_play_ratio": 0.666667,
        "lifecycle_sleep_ratio": 0.166667,
        "archive_occupied_niches": 7,
        "archive_best_fitness": 0.973629,
        "archive_qd_score": 6.722827
      }
    },
    {
      "probe_id": "slip_gray_stable_effect_probe",
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
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
      "effects_started": true,
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
      },
      "preview_signals": {
        "social_pull": 0.2775,
        "exploration_pull": 0.2625,
        "rest_pull": 0.6675,
        "mutation_pressure": 0.2275,
        "mutation_caution": 0.74
      },
      "lifecycle_effect": {
        "profile_id": "slip_gray_stable",
        "grid_id": "slip_gray_stable_constrained_000",
        "policy": "switchboard",
        "ticks_requested": 24,
        "survival_ticks": 24,
        "survival_ratio": 1.0,
        "alive": true,
        "death_cause": null,
        "need_balance": 0.785464,
        "recovery_events": 8,
        "action_counts": {
          "feed": 4,
          "play": 16,
          "sleep": 4,
          "idle": 0,
          "mutate": 0
        },
        "action_ratios": {
          "feed": 0.166667,
          "play": 0.666667,
          "sleep": 0.166667,
          "idle": 0.0,
          "mutate": 0.0
        },
        "final_state": {
          "hunger": 0.6336,
          "energy": 0.2268,
          "stress": 0.0,
          "bond": 1.0,
          "grid_stability": 0.988
        }
      },
      "archive_effect": {
        "profile_id": "slip_gray_stable",
        "archive_id": "map_elites_extended_stage0",
        "descriptor_names": [
          "body_mass",
          "sensor_count",
          "symmetry",
          "readability",
          "lifecycle_survival",
          "mutation_stability",
          "behavior_neediness"
        ],
        "descriptor_dimensions": 7,
        "candidate_count": 12,
        "lifecycle_ticks": 12,
        "occupied_niches": 8,
        "coverage": 0.000102,
        "best_fitness": 0.973786,
        "mean_elite_fitness": 0.955711,
        "qd_score": 7.645688,
        "elite_count": 8,
        "score_component_means": {
          "bond": 1.0,
          "mutation_stability": 0.9775,
          "readability": 0.824837,
          "slip_alignment": 1.0,
          "survival": 1.0,
          "validity": 1.0
        },
        "descriptor_metric_means": {
          "behavior_neediness": 0.3,
          "body_mass": 9.875,
          "lifecycle_survival": 1.0,
          "mutation_stability": 0.9775,
          "readability": 0.824837,
          "sensor_count": 2.0,
          "symmetry": 0.475525
        },
        "representative_elites": [
          {
            "grid_id": "slip_gray_stable_constrained_008",
            "fitness": 0.970124,
            "descriptor": {
              "names": [
                "body_mass",
                "sensor_count",
                "symmetry",
                "readability",
                "lifecycle_survival",
                "mutation_stability",
                "behavior_neediness"
              ],
              "values": [
                1,
                1,
                1,
                4,
                4,
                4,
                1
              ],
              "key": "1,1,1,4,4,4,1",
              "metrics": {
                "body_mass": 9,
                "sensor_count": 2,
                "symmetry": 0.5,
                "readability": 0.884891,
                "lifecycle_survival": 1.0,
                "mutation_stability": 0.9775,
                "behavior_neediness": 0.3
              }
            },
            "score_components": {
              "survival": 1.0,
              "readability": 0.884891,
              "validity": 1.0,
              "bond": 1.0,
              "mutation_stability": 0.9775,
              "slip_alignment": 1.0
            }
          },
          {
            "grid_id": "slip_gray_stable_constrained_011",
            "fitness": 0.929396,
            "descriptor": {
              "names": [
                "body_mass",
                "sensor_count",
                "symmetry",
                "readability",
                "lifecycle_survival",
                "mutation_stability",
                "behavior_neediness"
              ],
              "values": [
                1,
                2,
                1,
                3,
                4,
                4,
                1
              ],
              "key": "1,2,1,3,4,4,1",
              "metrics": {
                "body_mass": 8,
                "sensor_count": 3,
                "symmetry": 0.333333,
                "readability": 0.71519,
                "lifecycle_survival": 1.0,
                "mutation_stability": 0.9775,
                "behavior_neediness": 0.3
              }
            },
            "score_components": {
              "survival": 1.0,
              "readability": 0.71519,
              "validity": 1.0,
              "bond": 1.0,
              "mutation_stability": 0.9775,
              "slip_alignment": 1.0
            }
          },
          {
            "grid_id": "slip_gray_stable_constrained_009",
            "fitness": 0.973786,
            "descriptor": {
              "names": [
                "body_mass",
                "sensor_count",
                "symmetry",
                "readability",
                "lifecycle_survival",
                "mutation_stability",
                "behavior_neediness"
              ],
              "values": [
                2,
                0,
                1,
                4,
                4,
                4,
                1
              ],
              "key": "2,0,1,4,4,4,1",
              "metrics": {
                "body_mass": 10,
                "sensor_count": 1,
                "symmetry": 0.5,
                "readability": 0.900149,
                "lifecycle_survival": 1.0,
                "mutation_stability": 0.9775,
                "behavior_neediness": 0.3
              }
            },
            "score_components": {
              "survival": 1.0,
              "readability": 0.900149,
              "validity": 1.0,
              "bond": 1.0,
              "mutation_stability": 0.9775,
              "slip_alignment": 1.0
            }
          }
        ]
      },
      "preview_to_lifecycle_links": {
        "social_pull_to_play": {
          "preview_signal": 0.2775,
          "lifecycle_action": "play",
          "action_count": 16,
          "action_ratio": 0.666667,
          "final_bond": 1.0
        },
        "rest_pull_to_sleep": {
          "preview_signal": 0.6675,
          "lifecycle_action": "sleep",
          "action_count": 4,
          "action_ratio": 0.166667,
          "final_energy": 0.2268
        },
        "mutation_pressure_to_archive": {
          "preview_signal": 0.2275,
          "cell_mutation_budget": 2,
          "organ_shift_budget": 1,
          "archive_mutation_stability_mean": 0.9775
        },
        "mutation_caution_to_archive": {
          "preview_signal": 0.74,
          "caps_respected": true,
          "archive_best_fitness": 0.973786,
          "archive_qd_score": 7.645688
        }
      },
      "preview_effect_fingerprint": [
        0.2775,
        0.2625,
        0.6675,
        0.2275,
        0.74
      ],
      "lifecycle_effect_fingerprint": [
        1.0,
        0.785464,
        0.333333,
        0.166667,
        0.666667,
        0.166667,
        0.0,
        0.0,
        1.0,
        0.2268
      ],
      "archive_effect_fingerprint": [
        8.0,
        0.000102,
        0.973786,
        0.955711,
        7.645688,
        1.0,
        0.3,
        0.9775,
        1.0
      ],
      "measured_effect_fingerprint": {
        "lifecycle_survival_ratio": 1.0,
        "lifecycle_need_balance": 0.785464,
        "lifecycle_recovery_rate": 0.333333,
        "lifecycle_play_ratio": 0.666667,
        "lifecycle_sleep_ratio": 0.166667,
        "archive_occupied_niches": 8,
        "archive_best_fitness": 0.973786,
        "archive_qd_score": 7.645688
      }
    },
    {
      "probe_id": "slip_amber_social_effect_probe",
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
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
      "effects_started": true,
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
      },
      "preview_signals": {
        "social_pull": 0.54,
        "exploration_pull": 0.535,
        "rest_pull": 0.3625,
        "mutation_pressure": 0.4775,
        "mutation_caution": 0.4775
      },
      "lifecycle_effect": {
        "profile_id": "slip_amber_social",
        "grid_id": "slip_amber_social_constrained_000",
        "policy": "switchboard",
        "ticks_requested": 24,
        "survival_ticks": 24,
        "survival_ratio": 1.0,
        "alive": true,
        "death_cause": null,
        "need_balance": 0.793579,
        "recovery_events": 4,
        "action_counts": {
          "feed": 5,
          "play": 15,
          "sleep": 4,
          "idle": 0,
          "mutate": 0
        },
        "action_ratios": {
          "feed": 0.208333,
          "play": 0.625,
          "sleep": 0.166667,
          "idle": 0.0,
          "mutate": 0.0
        },
        "final_state": {
          "hunger": 0.4442,
          "energy": 0.4292,
          "stress": 0.0,
          "bond": 1.0,
          "grid_stability": 0.97
        }
      },
      "archive_effect": {
        "profile_id": "slip_amber_social",
        "archive_id": "map_elites_extended_stage0",
        "descriptor_names": [
          "body_mass",
          "sensor_count",
          "symmetry",
          "readability",
          "lifecycle_survival",
          "mutation_stability",
          "behavior_neediness"
        ],
        "descriptor_dimensions": 7,
        "candidate_count": 12,
        "lifecycle_ticks": 12,
        "occupied_niches": 9,
        "coverage": 0.000115,
        "best_fitness": 0.976533,
        "mean_elite_fitness": 0.960547,
        "qd_score": 8.644921,
        "elite_count": 9,
        "score_component_means": {
          "bond": 1.0,
          "mutation_stability": 0.9775,
          "readability": 0.844986,
          "slip_alignment": 1.0,
          "survival": 1.0,
          "validity": 1.0
        },
        "descriptor_metric_means": {
          "behavior_neediness": 0.6,
          "body_mass": 9.888889,
          "lifecycle_survival": 1.0,
          "mutation_stability": 0.9775,
          "readability": 0.844986,
          "sensor_count": 1.777778,
          "symmetry": 0.463573
        },
        "representative_elites": [
          {
            "grid_id": "slip_amber_social_constrained_005",
            "fitness": 0.973542,
            "descriptor": {
              "names": [
                "body_mass",
                "sensor_count",
                "symmetry",
                "readability",
                "lifecycle_survival",
                "mutation_stability",
                "behavior_neediness"
              ],
              "values": [
                1,
                0,
                2,
                4,
                4,
                4,
                2
              ],
              "key": "1,0,2,4,4,4,2",
              "metrics": {
                "body_mass": 8,
                "sensor_count": 1,
                "symmetry": 0.6,
                "readability": 0.899135,
                "lifecycle_survival": 1.0,
                "mutation_stability": 0.9775,
                "behavior_neediness": 0.6
              }
            },
            "score_components": {
              "survival": 1.0,
              "readability": 0.899135,
              "validity": 1.0,
              "bond": 1.0,
              "mutation_stability": 0.9775,
              "slip_alignment": 1.0
            }
          },
          {
            "grid_id": "slip_amber_social_constrained_003",
            "fitness": 0.949312,
            "descriptor": {
              "names": [
                "body_mass",
                "sensor_count",
                "symmetry",
                "readability",
                "lifecycle_survival",
                "mutation_stability",
                "behavior_neediness"
              ],
              "values": [
                1,
                1,
                1,
                3,
                4,
                4,
                2
              ],
              "key": "1,1,1,3,4,4,2",
              "metrics": {
                "body_mass": 9,
                "sensor_count": 2,
                "symmetry": 0.5,
                "readability": 0.798174,
                "lifecycle_survival": 1.0,
                "mutation_stability": 0.9775,
                "behavior_neediness": 0.6
              }
            },
            "score_components": {
              "survival": 1.0,
              "readability": 0.798174,
              "validity": 1.0,
              "bond": 1.0,
              "mutation_stability": 0.9775,
              "slip_alignment": 1.0
            }
          },
          {
            "grid_id": "slip_amber_social_constrained_007",
            "fitness": 0.942308,
            "descriptor": {
              "names": [
                "body_mass",
                "sensor_count",
                "symmetry",
                "readability",
                "lifecycle_survival",
                "mutation_stability",
                "behavior_neediness"
              ],
              "values": [
                2,
                0,
                1,
                3,
                4,
                4,
                2
              ],
              "key": "2,0,1,3,4,4,2",
              "metrics": {
                "body_mass": 10,
                "sensor_count": 1,
                "symmetry": 0.5,
                "readability": 0.768992,
                "lifecycle_survival": 1.0,
                "mutation_stability": 0.9775,
                "behavior_neediness": 0.6
              }
            },
            "score_components": {
              "survival": 1.0,
              "readability": 0.768992,
              "validity": 1.0,
              "bond": 1.0,
              "mutation_stability": 0.9775,
              "slip_alignment": 1.0
            }
          }
        ]
      },
      "preview_to_lifecycle_links": {
        "social_pull_to_play": {
          "preview_signal": 0.54,
          "lifecycle_action": "play",
          "action_count": 15,
          "action_ratio": 0.625,
          "final_bond": 1.0
        },
        "rest_pull_to_sleep": {
          "preview_signal": 0.3625,
          "lifecycle_action": "sleep",
          "action_count": 4,
          "action_ratio": 0.166667,
          "final_energy": 0.4292
        },
        "mutation_pressure_to_archive": {
          "preview_signal": 0.4775,
          "cell_mutation_budget": 3,
          "organ_shift_budget": 1,
          "archive_mutation_stability_mean": 0.9775
        },
        "mutation_caution_to_archive": {
          "preview_signal": 0.4775,
          "caps_respected": true,
          "archive_best_fitness": 0.976533,
          "archive_qd_score": 8.644921
        }
      },
      "preview_effect_fingerprint": [
        0.54,
        0.535,
        0.3625,
        0.4775,
        0.4775
      ],
      "lifecycle_effect_fingerprint": [
        1.0,
        0.793579,
        0.166667,
        0.208333,
        0.625,
        0.166667,
        0.0,
        0.0,
        1.0,
        0.4292
      ],
      "archive_effect_fingerprint": [
        9.0,
        0.000115,
        0.976533,
        0.960547,
        8.644921,
        1.0,
        0.6,
        0.9775,
        1.0
      ],
      "measured_effect_fingerprint": {
        "lifecycle_survival_ratio": 1.0,
        "lifecycle_need_balance": 0.793579,
        "lifecycle_recovery_rate": 0.166667,
        "lifecycle_play_ratio": 0.625,
        "lifecycle_sleep_ratio": 0.166667,
        "archive_occupied_niches": 9,
        "archive_best_fitness": 0.976533,
        "archive_qd_score": 8.644921
      }
    }
  ],
  "invalid_probe_results": [
    {
      "probe_id": "unsupported_version_rejected_before_effects",
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "profile_path": "data/slips/valid/slip_lcd_seed.json",
      "grid_path": "data/slips/multi_profile_generation_stage0/slip_lcd_seed/slip_lcd_seed_constrained_000.json",
      "validation": {
        "ok": false,
        "profile_id": "slip_lcd_seed",
        "grid_id": "slip_lcd_seed_constrained_000",
        "profile_validation": {
          "ok": false,
          "migration": {
            "ok": false,
            "source_version": "0.2.0",
            "target_version": null,
            "action": "reject_before_validation",
            "errors": [
              {
                "family": "schema_version_unsupported",
                "message": "unsupported SLIP version: 0.2.0"
              }
            ]
          },
          "dependency_free": {
            "source_path": null,
            "ok": false,
            "errors": [
              {
                "family": "schema_enum",
                "path": "slip_version",
                "message": "slip_version must equal '0.1.0'"
              }
            ],
            "error_families": [
              "schema_enum"
            ]
          },
          "pydantic": {
            "source_path": "authoring_draft",
            "ok": false,
            "errors": [
              {
                "family": "schema_enum",
                "path": "slip_version",
                "type": "literal_error",
                "message": "Input should be '0.1.0'"
              }
            ],
            "error_families": [
              "schema_enum"
            ]
          },
          "errors": [
            {
              "source": "migration",
              "family": "schema_version_unsupported",
              "path": "slip_version",
              "message": "unsupported SLIP version: 0.2.0"
            },
            {
              "source": "dependency_free",
              "family": "schema_enum",
              "path": "slip_version",
              "message": "slip_version must equal '0.1.0'"
            },
            {
              "source": "pydantic",
              "family": "schema_enum",
              "path": "slip_version",
              "message": "Input should be '0.1.0'"
            }
          ],
          "error_families": [
            "schema_enum",
            "schema_version_unsupported"
          ]
        },
        "grid_validation": {
          "ok": true,
          "errors": []
        },
        "alignment": {
          "ok": false,
          "errors": []
        },
        "preview_surfaces": [],
        "errors": [
          {
            "source": "migration",
            "family": "schema_version_unsupported",
            "path": "slip_version",
            "message": "unsupported SLIP version: 0.2.0"
          },
          {
            "source": "dependency_free",
            "family": "schema_enum",
            "path": "slip_version",
            "message": "slip_version must equal '0.1.0'"
          },
          {
            "source": "pydantic",
            "family": "schema_enum",
            "path": "slip_version",
            "message": "Input should be '0.1.0'"
          }
        ],
        "error_families": [
          "schema_enum",
          "schema_version_unsupported"
        ]
      },
      "effects_started": false
    },
    {
      "probe_id": "mismatched_profile_grid_rejected_before_effects",
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_lcd_seed_constrained_000",
      "profile_path": "data/slips/valid/slip_gray_stable.json",
      "grid_path": "data/slips/multi_profile_generation_stage0/slip_lcd_seed/slip_lcd_seed_constrained_000.json",
      "validation": {
        "ok": false,
        "profile_id": "slip_gray_stable",
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
          "ok": false,
          "errors": [
            "palette lcd_green not allowed by SLIP"
          ]
        },
        "preview_surfaces": [],
        "errors": [
          {
            "source": "slip_alignment",
            "family": "slip_alignment",
            "path": "$",
            "message": "palette lcd_green not allowed by SLIP"
          }
        ],
        "error_families": [
          "slip_alignment"
        ]
      },
      "effects_started": false
    }
  ]
};
