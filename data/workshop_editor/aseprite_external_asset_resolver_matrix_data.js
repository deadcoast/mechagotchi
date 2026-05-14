window.MECHAGOTCHI_ASEPRITE_EXTERNAL_ASSET_RESOLVER_MATRIX = {
  "report": {
    "artifact_id": "aseprite_external_asset_resolver_matrix_stage0",
    "status": "research_aseprite_external_asset_resolver_matrix_no_package_code",
    "profile_count": 3,
    "resolver_policy_count": 4,
    "resolver_roundtrip_count": 36,
    "resolver_roundtrip_success_count": 36,
    "invalid_probe_count": 5,
    "invalid_probe_rejected_count": 5,
    "metrics": {
      "resolver_roundtrip_success_rate": 1.0,
      "mean_semantic_fidelity": 1.0,
      "external_asset_resolution_rate": 1.0,
      "invalid_probe_rejection_rate": 1.0,
      "live_external_editor_verified": false
    },
    "closed_states": [
      "aseprite_direct_manifest_asset_resolver_subset",
      "aseprite_relative_file_asset_resolver_subset",
      "aseprite_content_addressed_asset_resolver_subset",
      "aseprite_multi_root_asset_resolver_subset",
      "aseprite_external_asset_resolver_invalid_probe_rejection"
    ],
    "blocked_states": [
      "live_external_editor_rewrite_validation",
      "editor_authored_aseprite_document_variants",
      "arbitrary_aseprite_project_schema_coverage",
      "full_project_format_coverage",
      "package_runtime_lifecycle_integration",
      "manual_readability_calibration",
      "profile_weighted_evolution"
    ],
    "decision": "prototype_aseprite_external_asset_resolver_matrix_subset"
  },
  "resolver_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "indexed_8",
      "resolver_policy_id": "direct_manifest",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_lcd_seed_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0d29de6bc1854261fbd86db276303b681c5a167227fd6eb222dbed40e58aa83a",
          "resolver_path": "slip_lcd_seed_palette.gpl"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_lcd_seed_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:38724e0b75276fcf6ec4186163a3bca362d5430d90418ab42ff4907f17924c31",
          "resolver_path": "slip_lcd_seed_tileset.json"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "indexed_8",
      "resolver_policy_id": "relative_file_map",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_lcd_seed_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0d29de6bc1854261fbd86db276303b681c5a167227fd6eb222dbed40e58aa83a",
          "resolver_path": "profile_asset_root/slip_lcd_seed/assets/slip_lcd_seed_palette.gpl"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_lcd_seed_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:38724e0b75276fcf6ec4186163a3bca362d5430d90418ab42ff4907f17924c31",
          "resolver_path": "profile_asset_root/slip_lcd_seed/assets/slip_lcd_seed_tileset.json"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_asset_root/slip_lcd_seed/assets/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "indexed_8",
      "resolver_policy_id": "content_addressed_pool",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_lcd_seed_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0d29de6bc1854261fbd86db276303b681c5a167227fd6eb222dbed40e58aa83a",
          "resolver_path": "content_addressed/0d29de6bc1854261.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_lcd_seed_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:38724e0b75276fcf6ec4186163a3bca362d5430d90418ab42ff4907f17924c31",
          "resolver_path": "content_addressed/38724e0b75276fcf.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "content_addressed/829cb7ef4b3754da.asset"
        }
      ]
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "indexed_8",
      "resolver_policy_id": "multi_root_priority",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_lcd_seed_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0d29de6bc1854261fbd86db276303b681c5a167227fd6eb222dbed40e58aa83a",
          "resolver_path": "profile_root/slip_lcd_seed/multi_root/external_palette/slip_lcd_seed_palette.gpl"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_lcd_seed_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:38724e0b75276fcf6ec4186163a3bca362d5430d90418ab42ff4907f17924c31",
          "resolver_path": "profile_root/slip_lcd_seed/multi_root/external_tileset/slip_lcd_seed_tileset.json"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_root/slip_lcd_seed/multi_root/extension_properties/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "grayscale_alpha_16",
      "resolver_policy_id": "direct_manifest",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_lcd_seed_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0d29de6bc1854261fbd86db276303b681c5a167227fd6eb222dbed40e58aa83a",
          "resolver_path": "slip_lcd_seed_palette.gpl"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_lcd_seed_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:38724e0b75276fcf6ec4186163a3bca362d5430d90418ab42ff4907f17924c31",
          "resolver_path": "slip_lcd_seed_tileset.json"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "grayscale_alpha_16",
      "resolver_policy_id": "relative_file_map",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_lcd_seed_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0d29de6bc1854261fbd86db276303b681c5a167227fd6eb222dbed40e58aa83a",
          "resolver_path": "profile_asset_root/slip_lcd_seed/assets/slip_lcd_seed_palette.gpl"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_lcd_seed_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:38724e0b75276fcf6ec4186163a3bca362d5430d90418ab42ff4907f17924c31",
          "resolver_path": "profile_asset_root/slip_lcd_seed/assets/slip_lcd_seed_tileset.json"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_asset_root/slip_lcd_seed/assets/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "grayscale_alpha_16",
      "resolver_policy_id": "content_addressed_pool",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_lcd_seed_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0d29de6bc1854261fbd86db276303b681c5a167227fd6eb222dbed40e58aa83a",
          "resolver_path": "content_addressed/0d29de6bc1854261.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_lcd_seed_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:38724e0b75276fcf6ec4186163a3bca362d5430d90418ab42ff4907f17924c31",
          "resolver_path": "content_addressed/38724e0b75276fcf.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "content_addressed/829cb7ef4b3754da.asset"
        }
      ]
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "grayscale_alpha_16",
      "resolver_policy_id": "multi_root_priority",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_lcd_seed_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0d29de6bc1854261fbd86db276303b681c5a167227fd6eb222dbed40e58aa83a",
          "resolver_path": "profile_root/slip_lcd_seed/multi_root/external_palette/slip_lcd_seed_palette.gpl"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_lcd_seed_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:38724e0b75276fcf6ec4186163a3bca362d5430d90418ab42ff4907f17924c31",
          "resolver_path": "profile_root/slip_lcd_seed/multi_root/external_tileset/slip_lcd_seed_tileset.json"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_root/slip_lcd_seed/multi_root/extension_properties/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "rgba_32",
      "resolver_policy_id": "direct_manifest",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_lcd_seed_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0d29de6bc1854261fbd86db276303b681c5a167227fd6eb222dbed40e58aa83a",
          "resolver_path": "slip_lcd_seed_palette.gpl"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_lcd_seed_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:38724e0b75276fcf6ec4186163a3bca362d5430d90418ab42ff4907f17924c31",
          "resolver_path": "slip_lcd_seed_tileset.json"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "rgba_32",
      "resolver_policy_id": "relative_file_map",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_lcd_seed_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0d29de6bc1854261fbd86db276303b681c5a167227fd6eb222dbed40e58aa83a",
          "resolver_path": "profile_asset_root/slip_lcd_seed/assets/slip_lcd_seed_palette.gpl"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_lcd_seed_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:38724e0b75276fcf6ec4186163a3bca362d5430d90418ab42ff4907f17924c31",
          "resolver_path": "profile_asset_root/slip_lcd_seed/assets/slip_lcd_seed_tileset.json"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_asset_root/slip_lcd_seed/assets/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "rgba_32",
      "resolver_policy_id": "content_addressed_pool",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_lcd_seed_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0d29de6bc1854261fbd86db276303b681c5a167227fd6eb222dbed40e58aa83a",
          "resolver_path": "content_addressed/0d29de6bc1854261.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_lcd_seed_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:38724e0b75276fcf6ec4186163a3bca362d5430d90418ab42ff4907f17924c31",
          "resolver_path": "content_addressed/38724e0b75276fcf.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "content_addressed/829cb7ef4b3754da.asset"
        }
      ]
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "rgba_32",
      "resolver_policy_id": "multi_root_priority",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_lcd_seed_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0d29de6bc1854261fbd86db276303b681c5a167227fd6eb222dbed40e58aa83a",
          "resolver_path": "profile_root/slip_lcd_seed/multi_root/external_palette/slip_lcd_seed_palette.gpl"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_lcd_seed_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:38724e0b75276fcf6ec4186163a3bca362d5430d90418ab42ff4907f17924c31",
          "resolver_path": "profile_root/slip_lcd_seed/multi_root/external_tileset/slip_lcd_seed_tileset.json"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_root/slip_lcd_seed/multi_root/extension_properties/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "indexed_8",
      "resolver_policy_id": "direct_manifest",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_gray_stable_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:436ed114afff418c0cb411bbed35305fb54fe0adcaa19f4187d1f53716e9d382",
          "resolver_path": "slip_gray_stable_palette.gpl"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_gray_stable_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:0c6cecf3e17657e8548dddc0bd4cbc913c03b90155376500c99daa9624e75f70",
          "resolver_path": "slip_gray_stable_tileset.json"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "indexed_8",
      "resolver_policy_id": "relative_file_map",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_gray_stable_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:436ed114afff418c0cb411bbed35305fb54fe0adcaa19f4187d1f53716e9d382",
          "resolver_path": "profile_asset_root/slip_gray_stable/assets/slip_gray_stable_palette.gpl"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_gray_stable_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:0c6cecf3e17657e8548dddc0bd4cbc913c03b90155376500c99daa9624e75f70",
          "resolver_path": "profile_asset_root/slip_gray_stable/assets/slip_gray_stable_tileset.json"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_asset_root/slip_gray_stable/assets/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "indexed_8",
      "resolver_policy_id": "content_addressed_pool",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_gray_stable_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:436ed114afff418c0cb411bbed35305fb54fe0adcaa19f4187d1f53716e9d382",
          "resolver_path": "content_addressed/436ed114afff418c.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_gray_stable_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:0c6cecf3e17657e8548dddc0bd4cbc913c03b90155376500c99daa9624e75f70",
          "resolver_path": "content_addressed/0c6cecf3e17657e8.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "content_addressed/829cb7ef4b3754da.asset"
        }
      ]
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "indexed_8",
      "resolver_policy_id": "multi_root_priority",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_gray_stable_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:436ed114afff418c0cb411bbed35305fb54fe0adcaa19f4187d1f53716e9d382",
          "resolver_path": "profile_root/slip_gray_stable/multi_root/external_palette/slip_gray_stable_palette.gpl"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_gray_stable_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:0c6cecf3e17657e8548dddc0bd4cbc913c03b90155376500c99daa9624e75f70",
          "resolver_path": "profile_root/slip_gray_stable/multi_root/external_tileset/slip_gray_stable_tileset.json"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_root/slip_gray_stable/multi_root/extension_properties/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "grayscale_alpha_16",
      "resolver_policy_id": "direct_manifest",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_gray_stable_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:436ed114afff418c0cb411bbed35305fb54fe0adcaa19f4187d1f53716e9d382",
          "resolver_path": "slip_gray_stable_palette.gpl"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_gray_stable_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:0c6cecf3e17657e8548dddc0bd4cbc913c03b90155376500c99daa9624e75f70",
          "resolver_path": "slip_gray_stable_tileset.json"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "grayscale_alpha_16",
      "resolver_policy_id": "relative_file_map",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_gray_stable_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:436ed114afff418c0cb411bbed35305fb54fe0adcaa19f4187d1f53716e9d382",
          "resolver_path": "profile_asset_root/slip_gray_stable/assets/slip_gray_stable_palette.gpl"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_gray_stable_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:0c6cecf3e17657e8548dddc0bd4cbc913c03b90155376500c99daa9624e75f70",
          "resolver_path": "profile_asset_root/slip_gray_stable/assets/slip_gray_stable_tileset.json"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_asset_root/slip_gray_stable/assets/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "grayscale_alpha_16",
      "resolver_policy_id": "content_addressed_pool",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_gray_stable_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:436ed114afff418c0cb411bbed35305fb54fe0adcaa19f4187d1f53716e9d382",
          "resolver_path": "content_addressed/436ed114afff418c.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_gray_stable_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:0c6cecf3e17657e8548dddc0bd4cbc913c03b90155376500c99daa9624e75f70",
          "resolver_path": "content_addressed/0c6cecf3e17657e8.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "content_addressed/829cb7ef4b3754da.asset"
        }
      ]
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "grayscale_alpha_16",
      "resolver_policy_id": "multi_root_priority",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_gray_stable_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:436ed114afff418c0cb411bbed35305fb54fe0adcaa19f4187d1f53716e9d382",
          "resolver_path": "profile_root/slip_gray_stable/multi_root/external_palette/slip_gray_stable_palette.gpl"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_gray_stable_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:0c6cecf3e17657e8548dddc0bd4cbc913c03b90155376500c99daa9624e75f70",
          "resolver_path": "profile_root/slip_gray_stable/multi_root/external_tileset/slip_gray_stable_tileset.json"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_root/slip_gray_stable/multi_root/extension_properties/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "rgba_32",
      "resolver_policy_id": "direct_manifest",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_gray_stable_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:436ed114afff418c0cb411bbed35305fb54fe0adcaa19f4187d1f53716e9d382",
          "resolver_path": "slip_gray_stable_palette.gpl"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_gray_stable_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:0c6cecf3e17657e8548dddc0bd4cbc913c03b90155376500c99daa9624e75f70",
          "resolver_path": "slip_gray_stable_tileset.json"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "rgba_32",
      "resolver_policy_id": "relative_file_map",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_gray_stable_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:436ed114afff418c0cb411bbed35305fb54fe0adcaa19f4187d1f53716e9d382",
          "resolver_path": "profile_asset_root/slip_gray_stable/assets/slip_gray_stable_palette.gpl"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_gray_stable_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:0c6cecf3e17657e8548dddc0bd4cbc913c03b90155376500c99daa9624e75f70",
          "resolver_path": "profile_asset_root/slip_gray_stable/assets/slip_gray_stable_tileset.json"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_asset_root/slip_gray_stable/assets/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "rgba_32",
      "resolver_policy_id": "content_addressed_pool",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_gray_stable_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:436ed114afff418c0cb411bbed35305fb54fe0adcaa19f4187d1f53716e9d382",
          "resolver_path": "content_addressed/436ed114afff418c.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_gray_stable_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:0c6cecf3e17657e8548dddc0bd4cbc913c03b90155376500c99daa9624e75f70",
          "resolver_path": "content_addressed/0c6cecf3e17657e8.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "content_addressed/829cb7ef4b3754da.asset"
        }
      ]
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "rgba_32",
      "resolver_policy_id": "multi_root_priority",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_gray_stable_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:436ed114afff418c0cb411bbed35305fb54fe0adcaa19f4187d1f53716e9d382",
          "resolver_path": "profile_root/slip_gray_stable/multi_root/external_palette/slip_gray_stable_palette.gpl"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_gray_stable_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:0c6cecf3e17657e8548dddc0bd4cbc913c03b90155376500c99daa9624e75f70",
          "resolver_path": "profile_root/slip_gray_stable/multi_root/external_tileset/slip_gray_stable_tileset.json"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_root/slip_gray_stable/multi_root/extension_properties/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "indexed_8",
      "resolver_policy_id": "direct_manifest",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_amber_social_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0472cf687417661c0fade24daeb619ac971c183a10dfdd9df541fa22737a306e",
          "resolver_path": "slip_amber_social_palette.gpl"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_amber_social_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:a158ef6363a16c937485754480ee59d0e795a9f4acdaf54045a50fa7b4e00741",
          "resolver_path": "slip_amber_social_tileset.json"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "indexed_8",
      "resolver_policy_id": "relative_file_map",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_amber_social_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0472cf687417661c0fade24daeb619ac971c183a10dfdd9df541fa22737a306e",
          "resolver_path": "profile_asset_root/slip_amber_social/assets/slip_amber_social_palette.gpl"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_amber_social_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:a158ef6363a16c937485754480ee59d0e795a9f4acdaf54045a50fa7b4e00741",
          "resolver_path": "profile_asset_root/slip_amber_social/assets/slip_amber_social_tileset.json"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_asset_root/slip_amber_social/assets/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "indexed_8",
      "resolver_policy_id": "content_addressed_pool",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_amber_social_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0472cf687417661c0fade24daeb619ac971c183a10dfdd9df541fa22737a306e",
          "resolver_path": "content_addressed/0472cf687417661c.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_amber_social_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:a158ef6363a16c937485754480ee59d0e795a9f4acdaf54045a50fa7b4e00741",
          "resolver_path": "content_addressed/a158ef6363a16c93.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "content_addressed/829cb7ef4b3754da.asset"
        }
      ]
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "indexed_8",
      "resolver_policy_id": "multi_root_priority",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_amber_social_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0472cf687417661c0fade24daeb619ac971c183a10dfdd9df541fa22737a306e",
          "resolver_path": "profile_root/slip_amber_social/multi_root/external_palette/slip_amber_social_palette.gpl"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_amber_social_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:a158ef6363a16c937485754480ee59d0e795a9f4acdaf54045a50fa7b4e00741",
          "resolver_path": "profile_root/slip_amber_social/multi_root/external_tileset/slip_amber_social_tileset.json"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_root/slip_amber_social/multi_root/extension_properties/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "grayscale_alpha_16",
      "resolver_policy_id": "direct_manifest",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_amber_social_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0472cf687417661c0fade24daeb619ac971c183a10dfdd9df541fa22737a306e",
          "resolver_path": "slip_amber_social_palette.gpl"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_amber_social_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:a158ef6363a16c937485754480ee59d0e795a9f4acdaf54045a50fa7b4e00741",
          "resolver_path": "slip_amber_social_tileset.json"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "grayscale_alpha_16",
      "resolver_policy_id": "relative_file_map",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_amber_social_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0472cf687417661c0fade24daeb619ac971c183a10dfdd9df541fa22737a306e",
          "resolver_path": "profile_asset_root/slip_amber_social/assets/slip_amber_social_palette.gpl"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_amber_social_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:a158ef6363a16c937485754480ee59d0e795a9f4acdaf54045a50fa7b4e00741",
          "resolver_path": "profile_asset_root/slip_amber_social/assets/slip_amber_social_tileset.json"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_asset_root/slip_amber_social/assets/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "grayscale_alpha_16",
      "resolver_policy_id": "content_addressed_pool",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_amber_social_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0472cf687417661c0fade24daeb619ac971c183a10dfdd9df541fa22737a306e",
          "resolver_path": "content_addressed/0472cf687417661c.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_amber_social_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:a158ef6363a16c937485754480ee59d0e795a9f4acdaf54045a50fa7b4e00741",
          "resolver_path": "content_addressed/a158ef6363a16c93.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "content_addressed/829cb7ef4b3754da.asset"
        }
      ]
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "grayscale_alpha_16",
      "resolver_policy_id": "multi_root_priority",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_amber_social_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0472cf687417661c0fade24daeb619ac971c183a10dfdd9df541fa22737a306e",
          "resolver_path": "profile_root/slip_amber_social/multi_root/external_palette/slip_amber_social_palette.gpl"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_amber_social_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:a158ef6363a16c937485754480ee59d0e795a9f4acdaf54045a50fa7b4e00741",
          "resolver_path": "profile_root/slip_amber_social/multi_root/external_tileset/slip_amber_social_tileset.json"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_root/slip_amber_social/multi_root/extension_properties/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "rgba_32",
      "resolver_policy_id": "direct_manifest",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_amber_social_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0472cf687417661c0fade24daeb619ac971c183a10dfdd9df541fa22737a306e",
          "resolver_path": "slip_amber_social_palette.gpl"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_amber_social_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:a158ef6363a16c937485754480ee59d0e795a9f4acdaf54045a50fa7b4e00741",
          "resolver_path": "slip_amber_social_tileset.json"
        },
        {
          "resolver_policy_id": "direct_manifest",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "rgba_32",
      "resolver_policy_id": "relative_file_map",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_amber_social_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0472cf687417661c0fade24daeb619ac971c183a10dfdd9df541fa22737a306e",
          "resolver_path": "profile_asset_root/slip_amber_social/assets/slip_amber_social_palette.gpl"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_amber_social_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:a158ef6363a16c937485754480ee59d0e795a9f4acdaf54045a50fa7b4e00741",
          "resolver_path": "profile_asset_root/slip_amber_social/assets/slip_amber_social_tileset.json"
        },
        {
          "resolver_policy_id": "relative_file_map",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_asset_root/slip_amber_social/assets/mechagotchi_variant_resolver.json"
        }
      ]
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "rgba_32",
      "resolver_policy_id": "content_addressed_pool",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_amber_social_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0472cf687417661c0fade24daeb619ac971c183a10dfdd9df541fa22737a306e",
          "resolver_path": "content_addressed/0472cf687417661c.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_amber_social_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:a158ef6363a16c937485754480ee59d0e795a9f4acdaf54045a50fa7b4e00741",
          "resolver_path": "content_addressed/a158ef6363a16c93.asset"
        },
        {
          "resolver_policy_id": "content_addressed_pool",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "content_addressed/829cb7ef4b3754da.asset"
        }
      ]
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "rgba_32",
      "resolver_policy_id": "multi_root_priority",
      "semantic_fidelity": 1.0,
      "resolved_external_assets": [
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1001,
          "type": 0,
          "type_name": "external_palette",
          "name": "slip_amber_social_palette.gpl",
          "media_type": "text/plain",
          "content_hash": "sha256:0472cf687417661c0fade24daeb619ac971c183a10dfdd9df541fa22737a306e",
          "resolver_path": "profile_root/slip_amber_social/multi_root/external_palette/slip_amber_social_palette.gpl"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1002,
          "type": 1,
          "type_name": "external_tileset",
          "name": "slip_amber_social_tileset.json",
          "media_type": "application/json",
          "content_hash": "sha256:a158ef6363a16c937485754480ee59d0e795a9f4acdaf54045a50fa7b4e00741",
          "resolver_path": "profile_root/slip_amber_social/multi_root/external_tileset/slip_amber_social_tileset.json"
        },
        {
          "resolver_policy_id": "multi_root_priority",
          "entry_id": 1003,
          "type": 2,
          "type_name": "extension_properties",
          "name": "mechagotchi_variant_resolver.json",
          "media_type": "application/json",
          "content_hash": "sha256:829cb7ef4b3754da15ee1be6e61f8619b24cc788ca773cf052d93202d9d2d6e8",
          "resolver_path": "profile_root/slip_amber_social/multi_root/extension_properties/mechagotchi_variant_resolver.json"
        }
      ]
    }
  ]
};
