window.MECHAGOTCHI_APNG_SIDECAR_DECODER = {
  "report": {
    "artifact_id": "apng_sidecar_decoder_stage0",
    "status": "research_apng_sidecar_decoder_no_package_code",
    "profile_count": 3,
    "apng_roundtrip_count": 3,
    "apng_roundtrip_success_count": 3,
    "invalid_probe_count": 5,
    "invalid_probe_rejected_count": 5,
    "metrics": {
      "apng_roundtrip_success_rate": 1.0,
      "mean_semantic_fidelity": 1.0,
      "mean_frame_pixel_fidelity": 1.0,
      "invalid_probe_rejection_rate": 1.0
    },
    "closed_states": [
      "apng_full_canvas_source_frame_decoder",
      "apng_actl_fctl_fdat_sequence_validation",
      "apng_sidecar_semantic_restore",
      "apng_frame_hash_validation",
      "apng_invalid_probe_rejection"
    ],
    "blocked_states": [
      "full_apng_png_conformance",
      "partial_frame_blend_over_disposal_variants",
      "APNG_textual_private_metadata_carrier_cross_product",
      "live_external_editor_rewrite_validation",
      "final_png_production_carrier_selection",
      "package_runtime_lifecycle_integration",
      "manual_readability_calibration",
      "profile_weighted_evolution"
    ],
    "decision": "prototype_bounded_apng_sidecar_decoder"
  },
  "apng_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "asset": {
        "asset_id": "slip_lcd_seed_constrained_000.apng.png",
        "format_id": "png",
        "media_type": "image/apng",
        "uri": "generated://workshop/apng-sidecar-decoder/slip_lcd_seed_constrained_000.png",
        "width": 8,
        "height": 8,
        "frame_count": 2,
        "content_hash": "sha256:94675d786bfe50bdecf444ae2b2fc28b3b194d37eceaa9cada8270b43d75744d",
        "semantic_policy": "sidecar_required"
      },
      "decoded_apng": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "IEND"
        ],
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT"
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "full_canvas": true,
            "pixel_hash": "sha256:36a30b12003b9e74aecefeb992a602fa13cd1ec01c93e0a80fc9d513ef36468b"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": true,
            "pixel_hash": "sha256:77e711be9f751a723c41dba097dfe1d1ee88e42c58208a8b429fc8b595305363"
          }
        ]
      },
      "semantic_fidelity": 1.0,
      "frame_pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "asset": {
        "asset_id": "slip_gray_stable_constrained_000.apng.png",
        "format_id": "png",
        "media_type": "image/apng",
        "uri": "generated://workshop/apng-sidecar-decoder/slip_gray_stable_constrained_000.png",
        "width": 8,
        "height": 8,
        "frame_count": 2,
        "content_hash": "sha256:90d9571e27f879673e5739290eecdb5f9fa1afff0a072eb8e6d073d3d7ea7d82",
        "semantic_policy": "sidecar_required"
      },
      "decoded_apng": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "IEND"
        ],
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT"
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "full_canvas": true,
            "pixel_hash": "sha256:b81f1f6c48601015838b407cceb766abc47c576a2be1d6b25eaa48ba323fc50a"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": true,
            "pixel_hash": "sha256:266a4f78b717c1836f6c3666a4c65f8877c93ba3b9242d43a9b18ed4beacc3c4"
          }
        ]
      },
      "semantic_fidelity": 1.0,
      "frame_pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "asset": {
        "asset_id": "slip_amber_social_constrained_000.apng.png",
        "format_id": "png",
        "media_type": "image/apng",
        "uri": "generated://workshop/apng-sidecar-decoder/slip_amber_social_constrained_000.png",
        "width": 8,
        "height": 8,
        "frame_count": 2,
        "content_hash": "sha256:6d1a5e11e6f868cca5e06b29524f7ecaf177c90498189d4e6404d9c6107bf17b",
        "semantic_policy": "sidecar_required"
      },
      "decoded_apng": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "IEND"
        ],
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT"
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "full_canvas": true,
            "pixel_hash": "sha256:ca56f937335979c6b3d75627efb1eda1b610da60027fe1bca505275d261be99e"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": true,
            "pixel_hash": "sha256:c56573e75e8ddf7f154eaf27676e2d6ecef49751a87ff46d5eec3cc226269608"
          }
        ]
      },
      "semantic_fidelity": 1.0,
      "frame_pixel_fidelity": 1.0
    }
  ]
};
