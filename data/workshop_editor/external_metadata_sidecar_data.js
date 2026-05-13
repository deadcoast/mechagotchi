window.MECHAGOTCHI_EXTERNAL_METADATA_SIDECAR = {
  "report": {
    "artifact_id": "external_metadata_sidecar_stage0",
    "status": "research_external_metadata_sidecar_strategy_no_package_code",
    "profile_count": 3,
    "sidecar_roundtrip_success_count": 3,
    "invalid_probe_count": 2,
    "invalid_probe_rejected_count": 2,
    "metrics": {
      "sidecar_roundtrip_success_rate": 1.0,
      "mean_semantic_fidelity": 1.0,
      "invalid_probe_rejection_rate": 1.0,
      "adapter_formats_requiring_sidecar": 5
    },
    "closed_states": [
      "external_metadata_sidecar_strategy",
      "sidecar_asset_binding_integrity",
      "sidecar_restores_semantic_grid",
      "sidecar_preserves_slip_alignment",
      "format_adapter_policy_matrix"
    ],
    "blocked_states": [
      "png_adam7_interlace_decoder",
      "apng_decoder",
      "full_png_conformance",
      "spritesheet_variant_layout_coverage",
      "full_project_format_coverage",
      "embedded_png_metadata_writer",
      "project_file_native_metadata_writer",
      "profile_weighted_evolution"
    ],
    "decision": "prototype_external_metadata_sidecar_strategy"
  },
  "adapter_matrix": [
    {
      "format_id": "png",
      "media_type": "image/png",
      "semantic_policy": "sidecar_required",
      "native_semantic_capacity": "pixels_only_no_mechagotchi_organs",
      "code_reuse_policy": "standard_format_safe_to_decode_later",
      "anchor": "W3C PNG specification"
    },
    {
      "format_id": "spritesheet_png",
      "media_type": "image/png",
      "semantic_policy": "sidecar_required",
      "native_semantic_capacity": "frames_and_pixels_only_no_semantic_cells",
      "code_reuse_policy": "standard_format_safe_to_decode_later",
      "anchor": "W3C PNG specification"
    },
    {
      "format_id": "piskel_project",
      "media_type": "application/json",
      "semantic_policy": "sidecar_required",
      "native_semantic_capacity": "sprite_project_data_not_mechagotchi_schema",
      "code_reuse_policy": "study_reference_possible_apache_2_review_before_embedding",
      "anchor": "Piskel GitHub"
    },
    {
      "format_id": "pixelorama_pxo",
      "media_type": "application/octet-stream",
      "semantic_policy": "sidecar_required",
      "native_semantic_capacity": "editor_project_metadata_not_mechagotchi_schema",
      "code_reuse_policy": "study_and_interop_possible_mit_review_before_embedding",
      "anchor": "Pixelorama documentation"
    },
    {
      "format_id": "libresprite_project",
      "media_type": "application/octet-stream",
      "semantic_policy": "sidecar_required",
      "native_semantic_capacity": "animation_project_data_not_mechagotchi_schema",
      "code_reuse_policy": "study_only_do_not_embed",
      "anchor": "LibreSprite GitHub"
    }
  ],
  "sidecar_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "asset": {
        "asset_id": "slip_lcd_seed_constrained_000.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "external://workshop/slip_lcd_seed_constrained_000.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:92fb6d747bbec766ad4290c25b2da277e5ff01322dc4150a921d94fb88388eb2",
        "semantic_policy": "sidecar_required"
      },
      "semantic_fidelity": 1.0,
      "validation": {
        "ok": true,
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "asset": {
        "asset_id": "slip_gray_stable_constrained_000.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "external://workshop/slip_gray_stable_constrained_000.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:06f5e70ca3bae06b23d6cb378d9a2c256b1c882d893b4029f3c6567cf407f498",
        "semantic_policy": "sidecar_required"
      },
      "semantic_fidelity": 1.0,
      "validation": {
        "ok": true,
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_amber_social",
      "asset": {
        "asset_id": "slip_amber_social_constrained_000.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "external://workshop/slip_amber_social_constrained_000.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:120a241ad964ff8a6868f9b75a86bd14dad3f59a3a44352541b3c8526fff8123",
        "semantic_policy": "sidecar_required"
      },
      "semantic_fidelity": 1.0,
      "validation": {
        "ok": true,
        "errors": [],
        "error_families": []
      }
    }
  ]
};
