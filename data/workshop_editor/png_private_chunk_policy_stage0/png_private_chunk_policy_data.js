window.MECHAGOTCHI_PNG_PRIVATE_CHUNK_POLICY = {
  "report": {
    "artifact_id": "png_private_chunk_policy_stage0",
    "status": "research_png_private_chunk_policy_no_package_code",
    "profile_count": 3,
    "private_chunk_roundtrip_count": 3,
    "private_chunk_roundtrip_success_count": 3,
    "invalid_probe_count": 7,
    "invalid_probe_rejected_count": 7,
    "metrics": {
      "private_chunk_roundtrip_success_rate": 1.0,
      "mean_semantic_fidelity": 1.0,
      "mean_pixel_fidelity": 1.0,
      "invalid_probe_rejection_rate": 1.0
    },
    "closed_states": [
      "png_private_chunk_type_bits_policy",
      "png_private_chunk_magic_prefix_policy",
      "png_private_chunk_hash_validation",
      "png_private_chunk_invalid_probe_rejection",
      "png_metadata_carrier_selection_inputs"
    ],
    "blocked_states": [
      "production_import_export_carrier_selection_final_decision",
      "live_external_editor_rewrite_validation",
      "Adam7/APNG/full PNG conformance",
      "private_chunk_editor_preservation_matrix",
      "package_runtime_lifecycle_integration",
      "manual readability calibration",
      "profile_weighted_evolution"
    ],
    "decision": "prototype_png_private_chunk_policy"
  },
  "chunk_type": "mgOT",
  "chunk_type_properties": {
    "ancillary": true,
    "private": true,
    "reserved_bit_valid": true,
    "safe_to_copy": false
  },
  "carrier_selection_inputs": {
    "external_sidecar": {
      "current_status": "proven_stage0_strategy",
      "strength": "highest compatibility with editors that strip unknown PNG metadata",
      "risk": "metadata can be separated from the visual asset"
    },
    "textual_png_chunks": {
      "current_status": "proven_stage0_text_ztxt_itxt_policy",
      "strength": "standard textual metadata carriers with UTF-8 path through iTXt",
      "risk": "editor preservation still unmeasured"
    },
    "private_png_chunk": {
      "current_status": "proven_stage0_private_chunk_policy",
      "strength": "application-native binary metadata carrier with explicit magic prefix",
      "risk": "spec guidance says text-specific metadata should not be stored only in private chunks; editor preservation still unmeasured"
    },
    "provisional_recommendation": "textual_or_external_sidecar_preferred_until_editor_fixtures",
    "final_decision_blocked_by": [
      "live_external_editor_rewrite_validation",
      "production_import_export_carrier_selection_final_decision"
    ]
  },
  "private_chunk_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "png_file_name": "slip_lcd_seed_private_chunk.png",
      "private_chunk_asset": {
        "asset_id": "slip_lcd_seed_constrained_000.private-chunk.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-private-chunk-policy/slip_lcd_seed_constrained_000.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:d573c5c1f68e361e884091aac9a5896a459aafe0ee629fc7ffb9d007d089387d",
        "semantic_policy": "embedded_sidecar_required"
      },
      "canonical_asset": {
        "asset_id": "slip_lcd_seed_constrained_000.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/standard-image/slip_lcd_seed_constrained_000.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:7ec438e0f21f3731d1746da4fdc96dc51a16299e4e1855f8a3d149a10f797877",
        "semantic_policy": "sidecar_required"
      },
      "metadata": {
        "metadata_model": "png_private_chunk_policy_v1",
        "chunk_type": "mgOT",
        "chunk_type_properties": {
          "ancillary": true,
          "private": true,
          "reserved_bit_valid": true,
          "safe_to_copy": false
        },
        "magic": "mechagotchi.private_chunk.v1",
        "private_chunk_policy": "ancillary_private_unsafe_to_copy_with_magic_prefix",
        "canonical_png_hash": "sha256:7ec438e0f21f3731d1746da4fdc96dc51a16299e4e1855f8a3d149a10f797877",
        "sidecar_hash": "sha256:9079ee293beef6d4b82d26e6663c2fdf2de853a960d3fcfb808214e7e9ddfa66",
        "hash_note": "canonical_png_hash excludes Mechagotchi private metadata chunks",
        "copy_note": "unsafe-to-copy private chunk because metadata is bound to image bytes"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "mgOT",
          "IDAT",
          "IEND"
        ]
      },
      "private_chunk_policy": {
        "ok": true,
        "chunk_type": "mgOT",
        "magic": "mechagotchi.private_chunk.v1",
        "private_chunk_policy": "ancillary_private_unsafe_to_copy_with_magic_prefix",
        "ancillary": true,
        "private": true,
        "reserved_bit_valid": true,
        "safe_to_copy": false,
        "private_chunk_count": 1,
        "live_external_editor_verified": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "png_file_name": "slip_gray_stable_private_chunk.png",
      "private_chunk_asset": {
        "asset_id": "slip_gray_stable_constrained_000.private-chunk.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-private-chunk-policy/slip_gray_stable_constrained_000.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:25f58fccd99d2053d429e8fbce89fdeeec1c617d1b92a6265ef778c0755d3d2b",
        "semantic_policy": "embedded_sidecar_required"
      },
      "canonical_asset": {
        "asset_id": "slip_gray_stable_constrained_000.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/standard-image/slip_gray_stable_constrained_000.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:423852196fa1519d513342d2dc4ffdaa03d258fa3d22a58fe036227e386dee6c",
        "semantic_policy": "sidecar_required"
      },
      "metadata": {
        "metadata_model": "png_private_chunk_policy_v1",
        "chunk_type": "mgOT",
        "chunk_type_properties": {
          "ancillary": true,
          "private": true,
          "reserved_bit_valid": true,
          "safe_to_copy": false
        },
        "magic": "mechagotchi.private_chunk.v1",
        "private_chunk_policy": "ancillary_private_unsafe_to_copy_with_magic_prefix",
        "canonical_png_hash": "sha256:423852196fa1519d513342d2dc4ffdaa03d258fa3d22a58fe036227e386dee6c",
        "sidecar_hash": "sha256:9cb64634d672138af773e22f29d2c8926e2d12e72bb73cb33347995b610075d4",
        "hash_note": "canonical_png_hash excludes Mechagotchi private metadata chunks",
        "copy_note": "unsafe-to-copy private chunk because metadata is bound to image bytes"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "mgOT",
          "IDAT",
          "IEND"
        ]
      },
      "private_chunk_policy": {
        "ok": true,
        "chunk_type": "mgOT",
        "magic": "mechagotchi.private_chunk.v1",
        "private_chunk_policy": "ancillary_private_unsafe_to_copy_with_magic_prefix",
        "ancillary": true,
        "private": true,
        "reserved_bit_valid": true,
        "safe_to_copy": false,
        "private_chunk_count": 1,
        "live_external_editor_verified": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "png_file_name": "slip_amber_social_private_chunk.png",
      "private_chunk_asset": {
        "asset_id": "slip_amber_social_constrained_000.private-chunk.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-private-chunk-policy/slip_amber_social_constrained_000.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:f02af5e766569c8623e06f7a9facbcc410715b44d1404860eeebdbdce6c7408c",
        "semantic_policy": "embedded_sidecar_required"
      },
      "canonical_asset": {
        "asset_id": "slip_amber_social_constrained_000.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/standard-image/slip_amber_social_constrained_000.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:caa3b67b904d9bdadd1ebe8821e196ec297ffbd4acc1086567f98c61502db8c1",
        "semantic_policy": "sidecar_required"
      },
      "metadata": {
        "metadata_model": "png_private_chunk_policy_v1",
        "chunk_type": "mgOT",
        "chunk_type_properties": {
          "ancillary": true,
          "private": true,
          "reserved_bit_valid": true,
          "safe_to_copy": false
        },
        "magic": "mechagotchi.private_chunk.v1",
        "private_chunk_policy": "ancillary_private_unsafe_to_copy_with_magic_prefix",
        "canonical_png_hash": "sha256:caa3b67b904d9bdadd1ebe8821e196ec297ffbd4acc1086567f98c61502db8c1",
        "sidecar_hash": "sha256:c4e613d37e756cc11c1b4df42a9dc7369f650f7d713aa8680c4b6ad3cc6332fc",
        "hash_note": "canonical_png_hash excludes Mechagotchi private metadata chunks",
        "copy_note": "unsafe-to-copy private chunk because metadata is bound to image bytes"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "mgOT",
          "IDAT",
          "IEND"
        ]
      },
      "private_chunk_policy": {
        "ok": true,
        "chunk_type": "mgOT",
        "magic": "mechagotchi.private_chunk.v1",
        "private_chunk_policy": "ancillary_private_unsafe_to_copy_with_magic_prefix",
        "ancillary": true,
        "private": true,
        "reserved_bit_valid": true,
        "safe_to_copy": false,
        "private_chunk_count": 1,
        "live_external_editor_verified": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    }
  ]
};
