window.MECHAGOTCHI_SLIP_AUTHORING_PANEL = {
  "report": {
    "artifact_id": "slip_authoring_panel_stage0",
    "status": "research_slip_authoring_panel_no_package_code",
    "profile_count": 3,
    "valid_draft_count": 3,
    "invalid_probe_count": 3,
    "invalid_probe_rejected_count": 3,
    "metrics": {
      "profile_authoring_success_rate": 1.0,
      "invalid_probe_rejection_rate": 1.0,
      "dependency_free_valid_draft_acceptance": 3,
      "pydantic_valid_draft_acceptance": 3,
      "migration_valid_draft_acceptance": 3
    },
    "closed_states": [
      "minimal_profile_authoring_panel",
      "current_profile_draft_validation",
      "schema_migration_gate_consumed_by_authoring",
      "pydantic_contract_consumed_by_authoring"
    ],
    "blocked_states": [
      "runtime_jsonschema_validation",
      "declared_dependency_manifest",
      "behavior_preview",
      "mutation_preview_ui",
      "profile_weighted_evolution",
      "external_image_project_metadata_sidecar_strategy",
      "profile_authoring_usability_pilot"
    ],
    "decision": "prototype_minimal_slip_authoring_panel"
  },
  "authoring_states": [
    {
      "panel_id": "slip_authoring_panel_stage0",
      "status": "research_slip_authoring_panel_no_package_code",
      "profile": {
        "slip_version": "0.1.0",
        "profile_id": "slip_lcd_seed",
        "name": "LCD Seed Companion",
        "grid": {
          "allowed_palettes": [
            "lcd_green"
          ],
          "body_mass_min": 4,
          "body_mass_max": 24,
          "required_organ_roles": [
            "sensor",
            "expression"
          ]
        },
        "mutation": {
          "cell_mutation_rate_max": 0.15,
          "organ_shift_rate_max": 0.05,
          "palette_shift_rate_max": 0.05,
          "symmetry_break_rate_max": 0.05
        },
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
      "surfaces": [
        "profile_metadata_form",
        "grid_constraint_controls",
        "mutation_cap_sliders",
        "behavior_weight_sliders",
        "survival_weight_sliders",
        "schema_validation_panel",
        "migration_gate_panel",
        "json_profile_export_panel"
      ],
      "schema_constraints": {
        "slip_version": "0.1.0",
        "profile_id_pattern": "^[a-z0-9_]+$",
        "profile_id_min_length": 1,
        "name_min_length": 1,
        "palette_values": [
          "amber_terminal",
          "crt_blue",
          "gameboy_gray",
          "lcd_green",
          "pocket_plum"
        ],
        "organ_roles": [
          "body_core",
          "expression",
          "sensor"
        ],
        "body_mass_minimum": 1,
        "unit_interval": {
          "minimum": 0,
          "maximum": 1
        },
        "mutation_required": [
          "cell_mutation_rate_max",
          "organ_shift_rate_max",
          "palette_shift_rate_max",
          "symmetry_break_rate_max"
        ],
        "behavior_required": [
          "curiosity",
          "neediness",
          "sleepiness"
        ],
        "survival_required": [
          "bond",
          "novelty",
          "stability"
        ],
        "additional_properties": "forbid"
      },
      "migration_gate": {
        "supported_versions": [
          "0.1.0"
        ],
        "current_version_action": "accept_current_no_migration",
        "missing_version_action": "reject_before_validation",
        "typed_version_action": "reject_before_validation",
        "unknown_version_action": "reject_before_validation"
      },
      "dependency_contracts": {
        "dependency_manifest_present": false,
        "pydantic_available": true,
        "pydantic_version": "2.12.5",
        "jsonschema_available": false,
        "jsonschema_version": null,
        "runtime_jsonschema_policy": "defer_python_jsonschema_until_dependency_manifest_exists"
      },
      "validation": {
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
      "profile_path": "data/slips/valid/slip_lcd_seed.json"
    },
    {
      "panel_id": "slip_authoring_panel_stage0",
      "status": "research_slip_authoring_panel_no_package_code",
      "profile": {
        "slip_version": "0.1.0",
        "profile_id": "slip_gray_stable",
        "name": "Gray Stable Companion",
        "grid": {
          "allowed_palettes": [
            "gameboy_gray"
          ],
          "body_mass_min": 5,
          "body_mass_max": 24,
          "required_organ_roles": [
            "sensor",
            "expression"
          ]
        },
        "mutation": {
          "cell_mutation_rate_max": 0.1,
          "organ_shift_rate_max": 0.05,
          "palette_shift_rate_max": 0.05,
          "symmetry_break_rate_max": 0.05
        },
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
      "surfaces": [
        "profile_metadata_form",
        "grid_constraint_controls",
        "mutation_cap_sliders",
        "behavior_weight_sliders",
        "survival_weight_sliders",
        "schema_validation_panel",
        "migration_gate_panel",
        "json_profile_export_panel"
      ],
      "schema_constraints": {
        "slip_version": "0.1.0",
        "profile_id_pattern": "^[a-z0-9_]+$",
        "profile_id_min_length": 1,
        "name_min_length": 1,
        "palette_values": [
          "amber_terminal",
          "crt_blue",
          "gameboy_gray",
          "lcd_green",
          "pocket_plum"
        ],
        "organ_roles": [
          "body_core",
          "expression",
          "sensor"
        ],
        "body_mass_minimum": 1,
        "unit_interval": {
          "minimum": 0,
          "maximum": 1
        },
        "mutation_required": [
          "cell_mutation_rate_max",
          "organ_shift_rate_max",
          "palette_shift_rate_max",
          "symmetry_break_rate_max"
        ],
        "behavior_required": [
          "curiosity",
          "neediness",
          "sleepiness"
        ],
        "survival_required": [
          "bond",
          "novelty",
          "stability"
        ],
        "additional_properties": "forbid"
      },
      "migration_gate": {
        "supported_versions": [
          "0.1.0"
        ],
        "current_version_action": "accept_current_no_migration",
        "missing_version_action": "reject_before_validation",
        "typed_version_action": "reject_before_validation",
        "unknown_version_action": "reject_before_validation"
      },
      "dependency_contracts": {
        "dependency_manifest_present": false,
        "pydantic_available": true,
        "pydantic_version": "2.12.5",
        "jsonschema_available": false,
        "jsonschema_version": null,
        "runtime_jsonschema_policy": "defer_python_jsonschema_until_dependency_manifest_exists"
      },
      "validation": {
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
      "profile_path": "data/slips/valid/slip_gray_stable.json"
    },
    {
      "panel_id": "slip_authoring_panel_stage0",
      "status": "research_slip_authoring_panel_no_package_code",
      "profile": {
        "slip_version": "0.1.0",
        "profile_id": "slip_amber_social",
        "name": "Amber Social Companion",
        "grid": {
          "allowed_palettes": [
            "amber_terminal"
          ],
          "body_mass_min": 6,
          "body_mass_max": 24,
          "required_organ_roles": [
            "sensor",
            "expression"
          ]
        },
        "mutation": {
          "cell_mutation_rate_max": 0.15,
          "organ_shift_rate_max": 0.05,
          "palette_shift_rate_max": 0.05,
          "symmetry_break_rate_max": 0.05
        },
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
      "surfaces": [
        "profile_metadata_form",
        "grid_constraint_controls",
        "mutation_cap_sliders",
        "behavior_weight_sliders",
        "survival_weight_sliders",
        "schema_validation_panel",
        "migration_gate_panel",
        "json_profile_export_panel"
      ],
      "schema_constraints": {
        "slip_version": "0.1.0",
        "profile_id_pattern": "^[a-z0-9_]+$",
        "profile_id_min_length": 1,
        "name_min_length": 1,
        "palette_values": [
          "amber_terminal",
          "crt_blue",
          "gameboy_gray",
          "lcd_green",
          "pocket_plum"
        ],
        "organ_roles": [
          "body_core",
          "expression",
          "sensor"
        ],
        "body_mass_minimum": 1,
        "unit_interval": {
          "minimum": 0,
          "maximum": 1
        },
        "mutation_required": [
          "cell_mutation_rate_max",
          "organ_shift_rate_max",
          "palette_shift_rate_max",
          "symmetry_break_rate_max"
        ],
        "behavior_required": [
          "curiosity",
          "neediness",
          "sleepiness"
        ],
        "survival_required": [
          "bond",
          "novelty",
          "stability"
        ],
        "additional_properties": "forbid"
      },
      "migration_gate": {
        "supported_versions": [
          "0.1.0"
        ],
        "current_version_action": "accept_current_no_migration",
        "missing_version_action": "reject_before_validation",
        "typed_version_action": "reject_before_validation",
        "unknown_version_action": "reject_before_validation"
      },
      "dependency_contracts": {
        "dependency_manifest_present": false,
        "pydantic_available": true,
        "pydantic_version": "2.12.5",
        "jsonschema_available": false,
        "jsonschema_version": null,
        "runtime_jsonschema_policy": "defer_python_jsonschema_until_dependency_manifest_exists"
      },
      "validation": {
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
      "profile_path": "data/slips/valid/slip_amber_social.json"
    }
  ]
};
