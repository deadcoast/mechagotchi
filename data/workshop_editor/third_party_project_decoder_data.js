window.MECHAGOTCHI_THIRD_PARTY_PROJECT_DECODER = {
  "report": {
    "artifact_id": "third_party_project_decoder_stage0",
    "status": "research_third_party_project_decoder_boundary_no_package_code",
    "profile_count": 3,
    "project_decoder_success_count": 3,
    "sidecar_restore_success_count": 3,
    "invalid_probe_count": 3,
    "invalid_probe_rejected_count": 3,
    "metrics": {
      "project_decoder_success_rate": 1.0,
      "sidecar_restore_success_rate": 1.0,
      "mean_semantic_fidelity": 1.0,
      "invalid_probe_rejection_rate": 1.0,
      "native_metadata_writer_count": 0,
      "project_formats_covered": 3
    },
    "closed_states": [
      "third_party_project_decoder_boundary",
      "piskel_project_json_boundary",
      "pixelorama_pxo_zip_data_json_boundary",
      "aseprite_libresprite_header_boundary",
      "project_file_sidecar_binding_integrity",
      "project_import_rejects_missing_or_mismatched_sidecar"
    ],
    "blocked_states": [
      "full_project_format_coverage",
      "png_adam7_interlace_decoder",
      "apng_decoder",
      "full_png_conformance",
      "spritesheet_packed_rotation_trim_decoder",
      "runtime_animation_playback",
      "embedded_png_metadata_writer",
      "project_file_native_metadata_writer",
      "runtime_lifecycle_archive_selection",
      "profile_weighted_evolution"
    ],
    "decision": "prototype_third_party_project_decoder_boundary"
  },
  "project_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "format_id": "piskel_project",
      "asset": {
        "asset_id": "slip_lcd_seed_constrained_000.piskel",
        "format_id": "piskel_project",
        "media_type": "application/json",
        "uri": "generated://workshop/project/slip_lcd_seed_constrained_000.piskel",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:7d2af75a9e9b0e51b9791f3c601c6e12504a8a0a8edd2bf012363f0271ea1447",
        "semantic_policy": "sidecar_required"
      },
      "decoded_project": {
        "format_id": "piskel_project",
        "model_version": 2,
        "name": "slip_lcd_seed_constrained_000",
        "dimensions": [
          8,
          8
        ],
        "frame_count": 1,
        "layer_count": 1,
        "chunk_count": 1,
        "native_mechagotchi_semantics": false
      },
      "semantic_fidelity": 1.0,
      "project_policy": {
        "semantic_policy": "sidecar_required",
        "native_mechagotchi_semantics": false,
        "decoder_scope": "json_envelope_layer_chunk_metadata_and_png_chunk_dimensions"
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "format_id": "pixelorama_pxo",
      "asset": {
        "asset_id": "slip_gray_stable_constrained_000.pxo",
        "format_id": "pixelorama_pxo",
        "media_type": "application/octet-stream",
        "uri": "generated://workshop/project/slip_gray_stable_constrained_000.pxo",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:b8ae11e2a8e01f7008bcea0d3e72c536a9ff0556fbc7ad966eeabfc55da499a4",
        "semantic_policy": "sidecar_required"
      },
      "decoded_project": {
        "format_id": "pixelorama_pxo",
        "name": "slip_gray_stable_constrained_000",
        "is_zip": true,
        "dimensions": [
          8,
          8
        ],
        "frame_count": 1,
        "layer_count": 1,
        "cel_count": 1,
        "native_mechagotchi_semantics": false
      },
      "semantic_fidelity": 1.0,
      "project_policy": {
        "semantic_policy": "sidecar_required",
        "native_mechagotchi_semantics": false,
        "decoder_scope": "zip_container_data_json_and_frame_image_inventory"
      }
    },
    {
      "profile_id": "slip_amber_social",
      "format_id": "libresprite_project",
      "asset": {
        "asset_id": "slip_amber_social_constrained_000.aseprite",
        "format_id": "libresprite_project",
        "media_type": "application/octet-stream",
        "uri": "generated://workshop/project/slip_amber_social_constrained_000.aseprite",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:12b54979d33f8fa73797bb1aa1bdf675c06b555172ac7bb4f4677859ce0aaa15",
        "semantic_policy": "sidecar_required"
      },
      "decoded_project": {
        "format_id": "libresprite_project",
        "magic": "0xa5e0",
        "frame_magic": "0xf1fa",
        "dimensions": [
          8,
          8
        ],
        "frame_count": 1,
        "layer_count": 0,
        "chunk_count": 0,
        "color_depth_bpp": 32,
        "native_mechagotchi_semantics": false
      },
      "semantic_fidelity": 1.0,
      "project_policy": {
        "semantic_policy": "sidecar_required",
        "native_mechagotchi_semantics": false,
        "decoder_scope": "aseprite_header_and_empty_frame_header_only"
      }
    }
  ]
};
