window.MECHAGOTCHI_SLIP_RUNTIME_SELECTION_POLICY = {
  "report": {
    "artifact_id": "slip_runtime_selection_policy_stage0",
    "status": "research_slip_runtime_selection_policy_no_package_code",
    "profile_count": 3,
    "selection_success_count": 3,
    "selected_elite_count": 3,
    "invalid_probe_count": 2,
    "invalid_probe_rejected_count": 2,
    "metrics": {
      "selection_success_rate": 1.0,
      "invalid_probe_rejection_rate": 1.0,
      "distinct_selected_grid_ids": 3,
      "distinct_selected_archive_niches": 3,
      "mean_selected_selection_score": 0.955828,
      "mean_selected_need_balance": 0.793865,
      "mean_selected_survival_ratio": 1.0,
      "runtime_lifecycle_archive_selection_specified": true
    },
    "parameters": {
      "candidate_limit": 12,
      "lifecycle_ticks": 24,
      "rng_seed": 20260513
    },
    "closed_states": [
      "runtime_lifecycle_archive_selection_policy",
      "profile_weighted_archive_elite_selection_trace",
      "invalid_profile_rejected_before_runtime_selection"
    ],
    "blocked_states": [
      "runtime_jsonschema_validation",
      "declared_dependency_manifest",
      "profile_weighted_evolution",
      "package_runtime_lifecycle_integration",
      "held_out_long_horizon_behavior_tests",
      "manual_readability_calibration",
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
    "decision": "prototype_slip_runtime_selection_policy"
  },
  "profile_results": [
    {
      "probe_id": "slip_lcd_seed_runtime_selection_policy",
      "profile_id": "slip_lcd_seed",
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
      "selection_started": true,
      "policy": {
        "policy_id": "profile_weighted_archive_elite_v0",
        "runtime_lifecycle_policy": "switchboard",
        "archive_policy": "extended_map_elites_elite_pool",
        "selection_rule": "weighted average over runtime survival, need balance, bond, mutation stability, niche rarity, readability, and SLIP alignment"
      },
      "archive_summary": {
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
        "occupied_niches": 7,
        "coverage": 9e-05,
        "best_fitness": 0.974469,
        "mean_elite_fitness": 0.961244,
        "qd_score": 6.728707,
        "elite_grid_ids": [
          "slip_lcd_seed_constrained_000",
          "slip_lcd_seed_constrained_002",
          "slip_lcd_seed_constrained_004",
          "slip_lcd_seed_constrained_007",
          "slip_lcd_seed_constrained_008",
          "slip_lcd_seed_constrained_009",
          "slip_lcd_seed_constrained_011"
        ]
      },
      "selected": {
        "grid_id": "slip_lcd_seed_constrained_011",
        "archive_niche": "1,1,2,4,4,4,1",
        "archive_fitness": 0.968623,
        "selection_score": 0.955499,
        "components": {
          "survival_ratio": 1.0,
          "need_balance": 0.802552,
          "bond": 1.0,
          "mutation_stability": 0.9775,
          "archive_niche_rarity": 1.0,
          "readability": 0.878639,
          "slip_alignment": 1.0
        },
        "component_weights": {
          "survival_ratio": 0.675,
          "need_balance": 0.425,
          "bond": 0.375,
          "mutation_stability": 0.45,
          "archive_niche_rarity": 0.41,
          "readability": 0.36,
          "slip_alignment": 0.4
        },
        "runtime_episode": {
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
          "final_state": {
            "hunger": 0.6888,
            "energy": 0.288,
            "stress": 0.0,
            "bond": 1.0,
            "grid_stability": 0.976
          }
        },
        "descriptor_metrics": {
          "body_mass": 8,
          "sensor_count": 2,
          "symmetry": 0.545455,
          "readability": 0.878639,
          "lifecycle_survival": 1.0,
          "mutation_stability": 0.9775,
          "behavior_neediness": 0.4
        },
        "score_components": {
          "survival": 1.0,
          "readability": 0.878639,
          "validity": 1.0,
          "bond": 1.0,
          "mutation_stability": 0.9775,
          "slip_alignment": 1.0
        }
      },
      "selection_trace": {
        "profile_id": "slip_lcd_seed",
        "profile_weights": {
          "behavior": {
            "curiosity": 0.6,
            "neediness": 0.4,
            "sleepiness": 0.5
          },
          "survival_weights": {
            "stability": 0.5,
            "novelty": 0.25,
            "bond": 0.25
          }
        },
        "profile_weighted_score": 0.955499,
        "selected_grid_id": "slip_lcd_seed_constrained_011",
        "selected_archive_niche": "1,1,2,4,4,4,1",
        "selected_components": {
          "survival_ratio": 1.0,
          "need_balance": 0.802552,
          "bond": 1.0,
          "mutation_stability": 0.9775,
          "archive_niche_rarity": 1.0,
          "readability": 0.878639,
          "slip_alignment": 1.0
        },
        "selected_component_weights": {
          "survival_ratio": 0.675,
          "need_balance": 0.425,
          "bond": 0.375,
          "mutation_stability": 0.45,
          "archive_niche_rarity": 0.41,
          "readability": 0.36,
          "slip_alignment": 0.4
        },
        "ranked_elite_count": 7,
        "top_ranked_elites": [
          {
            "rank": 1,
            "grid_id": "slip_lcd_seed_constrained_011",
            "archive_niche": "1,1,2,4,4,4,1",
            "selection_score": 0.955499,
            "archive_fitness": 0.968623
          },
          {
            "rank": 2,
            "grid_id": "slip_lcd_seed_constrained_007",
            "archive_niche": "2,2,2,3,4,4,1",
            "selection_score": 0.948422,
            "archive_fitness": 0.95402
          },
          {
            "rank": 3,
            "grid_id": "slip_lcd_seed_constrained_002",
            "archive_niche": "3,1,2,3,4,4,1",
            "selection_score": 0.944953,
            "archive_fitness": 0.946864
          },
          {
            "rank": 4,
            "grid_id": "slip_lcd_seed_constrained_008",
            "archive_niche": "1,2,1,3,4,4,1",
            "selection_score": 0.944066,
            "archive_fitness": 0.945032
          },
          {
            "rank": 5,
            "grid_id": "slip_lcd_seed_constrained_000",
            "archive_niche": "2,1,2,4,4,4,1",
            "selection_score": 0.892096,
            "archive_fitness": 0.974469
          }
        ]
      }
    },
    {
      "probe_id": "slip_gray_stable_runtime_selection_policy",
      "profile_id": "slip_gray_stable",
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
      "selection_started": true,
      "policy": {
        "policy_id": "profile_weighted_archive_elite_v0",
        "runtime_lifecycle_policy": "switchboard",
        "archive_policy": "extended_map_elites_elite_pool",
        "selection_rule": "weighted average over runtime survival, need balance, bond, mutation stability, niche rarity, readability, and SLIP alignment"
      },
      "archive_summary": {
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
        "occupied_niches": 8,
        "coverage": 0.000102,
        "best_fitness": 0.973786,
        "mean_elite_fitness": 0.955711,
        "qd_score": 7.645688,
        "elite_grid_ids": [
          "slip_gray_stable_constrained_000",
          "slip_gray_stable_constrained_004",
          "slip_gray_stable_constrained_005",
          "slip_gray_stable_constrained_006",
          "slip_gray_stable_constrained_007",
          "slip_gray_stable_constrained_008",
          "slip_gray_stable_constrained_009",
          "slip_gray_stable_constrained_011"
        ]
      },
      "selected": {
        "grid_id": "slip_gray_stable_constrained_008",
        "archive_niche": "1,1,1,4,4,4,1",
        "archive_fitness": 0.970124,
        "selection_score": 0.955179,
        "components": {
          "survival_ratio": 1.0,
          "need_balance": 0.785464,
          "bond": 1.0,
          "mutation_stability": 0.9775,
          "archive_niche_rarity": 1.0,
          "readability": 0.884891,
          "slip_alignment": 1.0
        },
        "component_weights": {
          "survival_ratio": 0.805,
          "need_balance": 0.4375,
          "bond": 0.34,
          "mutation_stability": 0.55,
          "archive_niche_rarity": 0.265,
          "readability": 0.2725,
          "slip_alignment": 0.4
        },
        "runtime_episode": {
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
          "final_state": {
            "hunger": 0.6336,
            "energy": 0.2268,
            "stress": 0.0,
            "bond": 1.0,
            "grid_stability": 0.988
          }
        },
        "descriptor_metrics": {
          "body_mass": 9,
          "sensor_count": 2,
          "symmetry": 0.5,
          "readability": 0.884891,
          "lifecycle_survival": 1.0,
          "mutation_stability": 0.9775,
          "behavior_neediness": 0.3
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
      "selection_trace": {
        "profile_id": "slip_gray_stable",
        "profile_weights": {
          "behavior": {
            "curiosity": 0.35,
            "neediness": 0.3,
            "sleepiness": 0.65
          },
          "survival_weights": {
            "stability": 0.7,
            "novelty": 0.1,
            "bond": 0.2
          }
        },
        "profile_weighted_score": 0.955179,
        "selected_grid_id": "slip_gray_stable_constrained_008",
        "selected_archive_niche": "1,1,1,4,4,4,1",
        "selected_components": {
          "survival_ratio": 1.0,
          "need_balance": 0.785464,
          "bond": 1.0,
          "mutation_stability": 0.9775,
          "archive_niche_rarity": 1.0,
          "readability": 0.884891,
          "slip_alignment": 1.0
        },
        "selected_component_weights": {
          "survival_ratio": 0.805,
          "need_balance": 0.4375,
          "bond": 0.34,
          "mutation_stability": 0.55,
          "archive_niche_rarity": 0.265,
          "readability": 0.2725,
          "slip_alignment": 0.4
        },
        "ranked_elite_count": 8,
        "top_ranked_elites": [
          {
            "rank": 1,
            "grid_id": "slip_gray_stable_constrained_008",
            "archive_niche": "1,1,1,4,4,4,1",
            "selection_score": 0.955179,
            "archive_fitness": 0.970124
          },
          {
            "rank": 2,
            "grid_id": "slip_gray_stable_constrained_000",
            "archive_niche": "2,2,1,3,4,4,1",
            "selection_score": 0.946843,
            "archive_fitness": 0.947587
          },
          {
            "rank": 3,
            "grid_id": "slip_gray_stable_constrained_005",
            "archive_niche": "2,3,1,3,4,4,1",
            "selection_score": 0.943656,
            "archive_fitness": 0.938969
          },
          {
            "rank": 4,
            "grid_id": "slip_gray_stable_constrained_011",
            "archive_niche": "1,2,1,3,4,4,1",
            "selection_score": 0.940116,
            "archive_fitness": 0.929396
          },
          {
            "rank": 5,
            "grid_id": "slip_gray_stable_constrained_009",
            "archive_niche": "2,0,1,4,4,4,1",
            "selection_score": 0.913373,
            "archive_fitness": 0.973786
          }
        ]
      }
    },
    {
      "probe_id": "slip_amber_social_runtime_selection_policy",
      "profile_id": "slip_amber_social",
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
      "selection_started": true,
      "policy": {
        "policy_id": "profile_weighted_archive_elite_v0",
        "runtime_lifecycle_policy": "switchboard",
        "archive_policy": "extended_map_elites_elite_pool",
        "selection_rule": "weighted average over runtime survival, need balance, bond, mutation stability, niche rarity, readability, and SLIP alignment"
      },
      "archive_summary": {
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
        "occupied_niches": 9,
        "coverage": 0.000115,
        "best_fitness": 0.976533,
        "mean_elite_fitness": 0.960547,
        "qd_score": 8.644921,
        "elite_grid_ids": [
          "slip_amber_social_constrained_000",
          "slip_amber_social_constrained_003",
          "slip_amber_social_constrained_004",
          "slip_amber_social_constrained_005",
          "slip_amber_social_constrained_006",
          "slip_amber_social_constrained_007",
          "slip_amber_social_constrained_008",
          "slip_amber_social_constrained_009",
          "slip_amber_social_constrained_011"
        ]
      },
      "selected": {
        "grid_id": "slip_amber_social_constrained_004",
        "archive_niche": "2,0,2,4,4,4,2",
        "archive_fitness": 0.976533,
        "selection_score": 0.956805,
        "components": {
          "survival_ratio": 1.0,
          "need_balance": 0.793579,
          "bond": 1.0,
          "mutation_stability": 0.9775,
          "archive_niche_rarity": 1.0,
          "readability": 0.911596,
          "slip_alignment": 1.0
        },
        "component_weights": {
          "survival_ratio": 0.61,
          "need_balance": 0.4375,
          "bond": 0.445,
          "mutation_stability": 0.4,
          "archive_niche_rarity": 0.42,
          "readability": 0.395,
          "slip_alignment": 0.4
        },
        "runtime_episode": {
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
          "final_state": {
            "hunger": 0.4442,
            "energy": 0.4292,
            "stress": 0.0,
            "bond": 1.0,
            "grid_stability": 0.97
          }
        },
        "descriptor_metrics": {
          "body_mass": 10,
          "sensor_count": 1,
          "symmetry": 0.666667,
          "readability": 0.911596,
          "lifecycle_survival": 1.0,
          "mutation_stability": 0.9775,
          "behavior_neediness": 0.6
        },
        "score_components": {
          "survival": 1.0,
          "readability": 0.911596,
          "validity": 1.0,
          "bond": 1.0,
          "mutation_stability": 0.9775,
          "slip_alignment": 1.0
        }
      },
      "selection_trace": {
        "profile_id": "slip_amber_social",
        "profile_weights": {
          "behavior": {
            "curiosity": 0.7,
            "neediness": 0.6,
            "sleepiness": 0.35
          },
          "survival_weights": {
            "stability": 0.4,
            "novelty": 0.25,
            "bond": 0.35
          }
        },
        "profile_weighted_score": 0.956805,
        "selected_grid_id": "slip_amber_social_constrained_004",
        "selected_archive_niche": "2,0,2,4,4,4,2",
        "selected_components": {
          "survival_ratio": 1.0,
          "need_balance": 0.793579,
          "bond": 1.0,
          "mutation_stability": 0.9775,
          "archive_niche_rarity": 1.0,
          "readability": 0.911596,
          "slip_alignment": 1.0
        },
        "selected_component_weights": {
          "survival_ratio": 0.61,
          "need_balance": 0.4375,
          "bond": 0.445,
          "mutation_stability": 0.4,
          "archive_niche_rarity": 0.42,
          "readability": 0.395,
          "slip_alignment": 0.4
        },
        "ranked_elite_count": 9,
        "top_ranked_elites": [
          {
            "rank": 1,
            "grid_id": "slip_amber_social_constrained_004",
            "archive_niche": "2,0,2,4,4,4,2",
            "selection_score": 0.956805,
            "archive_fitness": 0.976533
          },
          {
            "rank": 2,
            "grid_id": "slip_amber_social_constrained_009",
            "archive_niche": "2,1,2,4,4,4,2",
            "selection_score": 0.955901,
            "archive_fitness": 0.974826
          },
          {
            "rank": 3,
            "grid_id": "slip_amber_social_constrained_005",
            "archive_niche": "1,0,2,4,4,4,2",
            "selection_score": 0.955221,
            "archive_fitness": 0.973542
          },
          {
            "rank": 4,
            "grid_id": "slip_amber_social_constrained_003",
            "archive_niche": "1,1,1,3,4,4,2",
            "selection_score": 0.942388,
            "archive_fitness": 0.949312
          },
          {
            "rank": 5,
            "grid_id": "slip_amber_social_constrained_011",
            "archive_niche": "2,1,0,3,4,4,2",
            "selection_score": 0.940248,
            "archive_fitness": 0.945272
          }
        ]
      }
    }
  ],
  "invalid_probe_results": [
    {
      "probe_id": "unsupported_version_rejected_before_runtime_selection",
      "profile_id": "slip_lcd_seed",
      "profile_path": "data/slips/valid/slip_lcd_seed.json",
      "candidate_profile_id": "slip_lcd_seed",
      "candidate_limit": 12,
      "lifecycle_ticks": 24,
      "selection_started": false,
      "grid_id": "slip_lcd_seed_constrained_000",
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
      }
    },
    {
      "probe_id": "mismatched_candidate_corpus_rejected_before_runtime_selection",
      "profile_id": "slip_gray_stable",
      "profile_path": "data/slips/valid/slip_gray_stable.json",
      "candidate_profile_id": "slip_lcd_seed",
      "candidate_limit": 12,
      "lifecycle_ticks": 24,
      "selection_started": false,
      "grid_id": "slip_lcd_seed_constrained_000",
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
      }
    }
  ]
};
