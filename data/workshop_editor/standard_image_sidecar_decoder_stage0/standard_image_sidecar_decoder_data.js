window.MECHAGOTCHI_STANDARD_IMAGE_SIDECAR_DECODER = {
  "report": {
    "artifact_id": "standard_image_sidecar_decoder_stage0",
    "status": "research_standard_image_sidecar_decoder_no_package_code",
    "profile_count": 3,
    "png_roundtrip_success_count": 3,
    "invalid_probe_count": 2,
    "invalid_probe_rejected_count": 2,
    "metrics": {
      "png_roundtrip_success_rate": 1.0,
      "mean_semantic_fidelity": 1.0,
      "mean_pixel_fidelity": 1.0,
      "invalid_probe_rejection_rate": 1.0
    },
    "closed_states": [
      "standard_image_static_rgba_png_decoder",
      "standard_image_sidecar_export",
      "standard_image_sidecar_import",
      "png_signature_crc_and_idat_validation",
      "png_sidecar_semantic_restore"
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
    "decision": "prototype_static_rgba_png_sidecar_decoder"
  },
  "png_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "asset": {
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
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ]
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "asset": {
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
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ]
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "asset": {
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
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ]
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    }
  ]
};
