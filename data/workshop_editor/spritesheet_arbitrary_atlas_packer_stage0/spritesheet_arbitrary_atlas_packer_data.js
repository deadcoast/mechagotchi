window.MECHAGOTCHI_SPRITESHEET_ARBITRARY_ATLAS_PACKER = {
  "report": {
    "artifact_id": "spritesheet_arbitrary_atlas_packer_stage0",
    "status": "research_spritesheet_arbitrary_atlas_packer_no_package_code",
    "profile_count": 3,
    "packing_policy_count": 2,
    "atlas_roundtrip_count": 6,
    "atlas_roundtrip_success_count": 6,
    "invalid_probe_count": 6,
    "invalid_probe_rejected_count": 6,
    "metrics": {
      "atlas_roundtrip_success_rate": 1.0,
      "mean_semantic_fidelity": 1.0,
      "mean_reconstructed_frame_fidelity": 1.0,
      "mean_runtime_frame_fidelity": 1.0,
      "mean_occupancy_rate": 0.682598,
      "invalid_probe_rejection_rate": 1.0,
      "default_runtime_sample_count": 6
    },
    "policy_comparison": {
      "policies": [
        {
          "algorithm_id": "maxrects_best_short_side_fit",
          "mean_occupancy_rate": 0.698529,
          "mean_sheet_area": 272.0,
          "mean_wasted_area": 82.0
        },
        {
          "algorithm_id": "shelf_height_desc",
          "mean_occupancy_rate": 0.666667,
          "mean_sheet_area": 285.0,
          "mean_wasted_area": 95.0
        }
      ],
      "best_occupancy_policy": "maxrects_best_short_side_fit",
      "selection_basis": "highest mean occupancy, then smallest mean sheet area"
    },
    "closed_states": [
      "arbitrary_atlas_packing_geometry",
      "maxrects_best_short_side_fit_policy",
      "shelf_height_desc_baseline_policy",
      "atlas_rotation_trim_reconstruction",
      "atlas_frame_overlap_and_bounds_rejection",
      "atlas_runtime_sidecar_playback_sampling",
      "atlas_sidecar_semantic_restore"
    ],
    "blocked_states": [
      "production renderer playback",
      "live external editor rewrite validation",
      "full project-format coverage",
      "arbitrary Aseprite project schema coverage",
      "package runtime lifecycle integration",
      "manual readability calibration",
      "profile-weighted evolution",
      "community profile packs"
    ],
    "decision": "prototype_spritesheet_arbitrary_atlas_packer"
  },
  "atlas_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "policy_id": "shelf_height_desc",
      "asset": {
        "asset_id": "slip_lcd_seed_shelf_arbitrary_atlas.png",
        "format_id": "spritesheet_png",
        "media_type": "image/png",
        "uri": "generated://workshop/spritesheet-arbitrary-atlas/slip_lcd_seed_shelf_arbitrary_atlas.png",
        "width": 19,
        "height": 15,
        "frame_count": 5,
        "content_hash": "sha256:eff2c9339f7512e2140da8803745cd97366ca92a5ce53d8b9d0c094ba7c16713",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 19,
        "height": 15,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 285,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ]
      },
      "frame_count": 5,
      "packing_policy": {
        "algorithm_id": "shelf_height_desc",
        "basis": "height-descending shelf baseline",
        "max_width": 20,
        "padding_px": 1,
        "allow_rotation": true,
        "used_rect_area": 190,
        "sheet_area": 285,
        "wasted_area": 95,
        "occupancy_rate": 0.666667,
        "placement_order": [
          0,
          2,
          1,
          4,
          3
        ]
      },
      "semantic_fidelity": 1.0,
      "reconstructed_frame_fidelity": 1.0,
      "runtime_frame_fidelity": 1.0,
      "runtime_playback": {
        "timeline": [
          {
            "time_ms": 0,
            "effective_time_ms": 0,
            "frame_index": 0,
            "duration_ms": 100,
            "visual_delta": "base_pose",
            "canonical_pixel_hash": "sha256:97548c7836c0223dc594e82a9d608b98a96e5247b09864e29c81be367f0db9b3",
            "expected_canonical_pixel_hash": "sha256:97548c7836c0223dc594e82a9d608b98a96e5247b09864e29c81be367f0db9b3",
            "canonical_hash_match": true
          },
          {
            "time_ms": 100,
            "effective_time_ms": 100,
            "frame_index": 1,
            "duration_ms": 120,
            "visual_delta": "sensor_blink_crop",
            "canonical_pixel_hash": "sha256:0c1eaa187c72469607ef1e34a12b0ceace404f0ffdcbc09bdcd213e4450bd8ce",
            "expected_canonical_pixel_hash": "sha256:0c1eaa187c72469607ef1e34a12b0ceace404f0ffdcbc09bdcd213e4450bd8ce",
            "canonical_hash_match": true
          },
          {
            "time_ms": 220,
            "effective_time_ms": 220,
            "frame_index": 2,
            "duration_ms": 140,
            "visual_delta": "left_body_sweep",
            "canonical_pixel_hash": "sha256:319e103118aeecceeb2971c5e8b6fbe412cd42852840728594053905c8026b2a",
            "expected_canonical_pixel_hash": "sha256:319e103118aeecceeb2971c5e8b6fbe412cd42852840728594053905c8026b2a",
            "canonical_hash_match": true
          },
          {
            "time_ms": 360,
            "effective_time_ms": 360,
            "frame_index": 3,
            "duration_ms": 160,
            "visual_delta": "upper_anchor_echo",
            "canonical_pixel_hash": "sha256:efc7c0a4f7c58ed537a22c260f9eb4e7361577cae0f093b6dade6a3d615319e8",
            "expected_canonical_pixel_hash": "sha256:efc7c0a4f7c58ed537a22c260f9eb4e7361577cae0f093b6dade6a3d615319e8",
            "canonical_hash_match": true
          },
          {
            "time_ms": 520,
            "effective_time_ms": 520,
            "frame_index": 4,
            "duration_ms": 180,
            "visual_delta": "lower_expression_pulse",
            "canonical_pixel_hash": "sha256:62c127f389a65ed80c75191e9f93442c694692a1f0a1ac61e32c5befa398dce0",
            "expected_canonical_pixel_hash": "sha256:62c127f389a65ed80c75191e9f93442c694692a1f0a1ac61e32c5befa398dce0",
            "canonical_hash_match": true
          },
          {
            "time_ms": 700,
            "effective_time_ms": 0,
            "frame_index": 0,
            "duration_ms": 100,
            "visual_delta": "base_pose",
            "canonical_pixel_hash": "sha256:97548c7836c0223dc594e82a9d608b98a96e5247b09864e29c81be367f0db9b3",
            "expected_canonical_pixel_hash": "sha256:97548c7836c0223dc594e82a9d608b98a96e5247b09864e29c81be367f0db9b3",
            "canonical_hash_match": true
          }
        ],
        "sample_count": 6,
        "loop": true,
        "total_duration_ms": 700
      }
    },
    {
      "profile_id": "slip_lcd_seed",
      "policy_id": "maxrects_best_short_side_fit",
      "asset": {
        "asset_id": "slip_lcd_seed_maxrects_arbitrary_atlas.png",
        "format_id": "spritesheet_png",
        "media_type": "image/png",
        "uri": "generated://workshop/spritesheet-arbitrary-atlas/slip_lcd_seed_maxrects_arbitrary_atlas.png",
        "width": 16,
        "height": 17,
        "frame_count": 5,
        "content_hash": "sha256:9e41461c470b5b521b716adc0f03921dde2615daa4cf8fe3f1874abdea565152",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 16,
        "height": 17,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 272,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ]
      },
      "frame_count": 5,
      "packing_policy": {
        "algorithm_id": "maxrects_best_short_side_fit",
        "basis": "MaxRects-style best-short-side-fit rectangle placement",
        "max_width": 16,
        "padding_px": 1,
        "allow_rotation": true,
        "used_rect_area": 190,
        "sheet_area": 272,
        "wasted_area": 82,
        "occupancy_rate": 0.698529,
        "placement_order": [
          0,
          4,
          2,
          1,
          3
        ]
      },
      "semantic_fidelity": 1.0,
      "reconstructed_frame_fidelity": 1.0,
      "runtime_frame_fidelity": 1.0,
      "runtime_playback": {
        "timeline": [
          {
            "time_ms": 0,
            "effective_time_ms": 0,
            "frame_index": 0,
            "duration_ms": 100,
            "visual_delta": "base_pose",
            "canonical_pixel_hash": "sha256:97548c7836c0223dc594e82a9d608b98a96e5247b09864e29c81be367f0db9b3",
            "expected_canonical_pixel_hash": "sha256:97548c7836c0223dc594e82a9d608b98a96e5247b09864e29c81be367f0db9b3",
            "canonical_hash_match": true
          },
          {
            "time_ms": 100,
            "effective_time_ms": 100,
            "frame_index": 1,
            "duration_ms": 120,
            "visual_delta": "sensor_blink_crop",
            "canonical_pixel_hash": "sha256:0c1eaa187c72469607ef1e34a12b0ceace404f0ffdcbc09bdcd213e4450bd8ce",
            "expected_canonical_pixel_hash": "sha256:0c1eaa187c72469607ef1e34a12b0ceace404f0ffdcbc09bdcd213e4450bd8ce",
            "canonical_hash_match": true
          },
          {
            "time_ms": 220,
            "effective_time_ms": 220,
            "frame_index": 2,
            "duration_ms": 140,
            "visual_delta": "left_body_sweep",
            "canonical_pixel_hash": "sha256:319e103118aeecceeb2971c5e8b6fbe412cd42852840728594053905c8026b2a",
            "expected_canonical_pixel_hash": "sha256:319e103118aeecceeb2971c5e8b6fbe412cd42852840728594053905c8026b2a",
            "canonical_hash_match": true
          },
          {
            "time_ms": 360,
            "effective_time_ms": 360,
            "frame_index": 3,
            "duration_ms": 160,
            "visual_delta": "upper_anchor_echo",
            "canonical_pixel_hash": "sha256:efc7c0a4f7c58ed537a22c260f9eb4e7361577cae0f093b6dade6a3d615319e8",
            "expected_canonical_pixel_hash": "sha256:efc7c0a4f7c58ed537a22c260f9eb4e7361577cae0f093b6dade6a3d615319e8",
            "canonical_hash_match": true
          },
          {
            "time_ms": 520,
            "effective_time_ms": 520,
            "frame_index": 4,
            "duration_ms": 180,
            "visual_delta": "lower_expression_pulse",
            "canonical_pixel_hash": "sha256:62c127f389a65ed80c75191e9f93442c694692a1f0a1ac61e32c5befa398dce0",
            "expected_canonical_pixel_hash": "sha256:62c127f389a65ed80c75191e9f93442c694692a1f0a1ac61e32c5befa398dce0",
            "canonical_hash_match": true
          },
          {
            "time_ms": 700,
            "effective_time_ms": 0,
            "frame_index": 0,
            "duration_ms": 100,
            "visual_delta": "base_pose",
            "canonical_pixel_hash": "sha256:97548c7836c0223dc594e82a9d608b98a96e5247b09864e29c81be367f0db9b3",
            "expected_canonical_pixel_hash": "sha256:97548c7836c0223dc594e82a9d608b98a96e5247b09864e29c81be367f0db9b3",
            "canonical_hash_match": true
          }
        ],
        "sample_count": 6,
        "loop": true,
        "total_duration_ms": 700
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "policy_id": "shelf_height_desc",
      "asset": {
        "asset_id": "slip_gray_stable_shelf_arbitrary_atlas.png",
        "format_id": "spritesheet_png",
        "media_type": "image/png",
        "uri": "generated://workshop/spritesheet-arbitrary-atlas/slip_gray_stable_shelf_arbitrary_atlas.png",
        "width": 19,
        "height": 15,
        "frame_count": 5,
        "content_hash": "sha256:dc43af1762d5c41e9dff2a4a459bfede9b7a81a9aa57ec2a4dd6d33586996486",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 19,
        "height": 15,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 285,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ]
      },
      "frame_count": 5,
      "packing_policy": {
        "algorithm_id": "shelf_height_desc",
        "basis": "height-descending shelf baseline",
        "max_width": 20,
        "padding_px": 1,
        "allow_rotation": true,
        "used_rect_area": 190,
        "sheet_area": 285,
        "wasted_area": 95,
        "occupancy_rate": 0.666667,
        "placement_order": [
          0,
          2,
          1,
          4,
          3
        ]
      },
      "semantic_fidelity": 1.0,
      "reconstructed_frame_fidelity": 1.0,
      "runtime_frame_fidelity": 1.0,
      "runtime_playback": {
        "timeline": [
          {
            "time_ms": 0,
            "effective_time_ms": 0,
            "frame_index": 0,
            "duration_ms": 100,
            "visual_delta": "base_pose",
            "canonical_pixel_hash": "sha256:fd27f573ab85107bd9269ebec16db7a959f5a0a4b38b7f03aec741b9b3fd3e08",
            "expected_canonical_pixel_hash": "sha256:fd27f573ab85107bd9269ebec16db7a959f5a0a4b38b7f03aec741b9b3fd3e08",
            "canonical_hash_match": true
          },
          {
            "time_ms": 100,
            "effective_time_ms": 100,
            "frame_index": 1,
            "duration_ms": 120,
            "visual_delta": "sensor_blink_crop",
            "canonical_pixel_hash": "sha256:c015132120bc46a23bf3a848bd9ca2048878e36bf66b5c9672f3034b539e9b2c",
            "expected_canonical_pixel_hash": "sha256:c015132120bc46a23bf3a848bd9ca2048878e36bf66b5c9672f3034b539e9b2c",
            "canonical_hash_match": true
          },
          {
            "time_ms": 220,
            "effective_time_ms": 220,
            "frame_index": 2,
            "duration_ms": 140,
            "visual_delta": "left_body_sweep",
            "canonical_pixel_hash": "sha256:b6776b8970c8fc51ba319b1dbebd3485da0eb9b161d12548578a9039710091d5",
            "expected_canonical_pixel_hash": "sha256:b6776b8970c8fc51ba319b1dbebd3485da0eb9b161d12548578a9039710091d5",
            "canonical_hash_match": true
          },
          {
            "time_ms": 360,
            "effective_time_ms": 360,
            "frame_index": 3,
            "duration_ms": 160,
            "visual_delta": "upper_anchor_echo",
            "canonical_pixel_hash": "sha256:0df70f74bc6b6cf86581d410babff6945d5b90234d78fcd6206026fb9862587b",
            "expected_canonical_pixel_hash": "sha256:0df70f74bc6b6cf86581d410babff6945d5b90234d78fcd6206026fb9862587b",
            "canonical_hash_match": true
          },
          {
            "time_ms": 520,
            "effective_time_ms": 520,
            "frame_index": 4,
            "duration_ms": 180,
            "visual_delta": "lower_expression_pulse",
            "canonical_pixel_hash": "sha256:07ae2b9f301a2bc4174a6398b71eff67a0f3cd8f4ce4d5041956b17caed52219",
            "expected_canonical_pixel_hash": "sha256:07ae2b9f301a2bc4174a6398b71eff67a0f3cd8f4ce4d5041956b17caed52219",
            "canonical_hash_match": true
          },
          {
            "time_ms": 700,
            "effective_time_ms": 0,
            "frame_index": 0,
            "duration_ms": 100,
            "visual_delta": "base_pose",
            "canonical_pixel_hash": "sha256:fd27f573ab85107bd9269ebec16db7a959f5a0a4b38b7f03aec741b9b3fd3e08",
            "expected_canonical_pixel_hash": "sha256:fd27f573ab85107bd9269ebec16db7a959f5a0a4b38b7f03aec741b9b3fd3e08",
            "canonical_hash_match": true
          }
        ],
        "sample_count": 6,
        "loop": true,
        "total_duration_ms": 700
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "policy_id": "maxrects_best_short_side_fit",
      "asset": {
        "asset_id": "slip_gray_stable_maxrects_arbitrary_atlas.png",
        "format_id": "spritesheet_png",
        "media_type": "image/png",
        "uri": "generated://workshop/spritesheet-arbitrary-atlas/slip_gray_stable_maxrects_arbitrary_atlas.png",
        "width": 16,
        "height": 17,
        "frame_count": 5,
        "content_hash": "sha256:d55f5fe5bbe9eb505747cac2336217efd5e3b819f06e537adcc368da95de7611",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 16,
        "height": 17,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 272,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ]
      },
      "frame_count": 5,
      "packing_policy": {
        "algorithm_id": "maxrects_best_short_side_fit",
        "basis": "MaxRects-style best-short-side-fit rectangle placement",
        "max_width": 16,
        "padding_px": 1,
        "allow_rotation": true,
        "used_rect_area": 190,
        "sheet_area": 272,
        "wasted_area": 82,
        "occupancy_rate": 0.698529,
        "placement_order": [
          0,
          4,
          2,
          1,
          3
        ]
      },
      "semantic_fidelity": 1.0,
      "reconstructed_frame_fidelity": 1.0,
      "runtime_frame_fidelity": 1.0,
      "runtime_playback": {
        "timeline": [
          {
            "time_ms": 0,
            "effective_time_ms": 0,
            "frame_index": 0,
            "duration_ms": 100,
            "visual_delta": "base_pose",
            "canonical_pixel_hash": "sha256:fd27f573ab85107bd9269ebec16db7a959f5a0a4b38b7f03aec741b9b3fd3e08",
            "expected_canonical_pixel_hash": "sha256:fd27f573ab85107bd9269ebec16db7a959f5a0a4b38b7f03aec741b9b3fd3e08",
            "canonical_hash_match": true
          },
          {
            "time_ms": 100,
            "effective_time_ms": 100,
            "frame_index": 1,
            "duration_ms": 120,
            "visual_delta": "sensor_blink_crop",
            "canonical_pixel_hash": "sha256:c015132120bc46a23bf3a848bd9ca2048878e36bf66b5c9672f3034b539e9b2c",
            "expected_canonical_pixel_hash": "sha256:c015132120bc46a23bf3a848bd9ca2048878e36bf66b5c9672f3034b539e9b2c",
            "canonical_hash_match": true
          },
          {
            "time_ms": 220,
            "effective_time_ms": 220,
            "frame_index": 2,
            "duration_ms": 140,
            "visual_delta": "left_body_sweep",
            "canonical_pixel_hash": "sha256:b6776b8970c8fc51ba319b1dbebd3485da0eb9b161d12548578a9039710091d5",
            "expected_canonical_pixel_hash": "sha256:b6776b8970c8fc51ba319b1dbebd3485da0eb9b161d12548578a9039710091d5",
            "canonical_hash_match": true
          },
          {
            "time_ms": 360,
            "effective_time_ms": 360,
            "frame_index": 3,
            "duration_ms": 160,
            "visual_delta": "upper_anchor_echo",
            "canonical_pixel_hash": "sha256:0df70f74bc6b6cf86581d410babff6945d5b90234d78fcd6206026fb9862587b",
            "expected_canonical_pixel_hash": "sha256:0df70f74bc6b6cf86581d410babff6945d5b90234d78fcd6206026fb9862587b",
            "canonical_hash_match": true
          },
          {
            "time_ms": 520,
            "effective_time_ms": 520,
            "frame_index": 4,
            "duration_ms": 180,
            "visual_delta": "lower_expression_pulse",
            "canonical_pixel_hash": "sha256:07ae2b9f301a2bc4174a6398b71eff67a0f3cd8f4ce4d5041956b17caed52219",
            "expected_canonical_pixel_hash": "sha256:07ae2b9f301a2bc4174a6398b71eff67a0f3cd8f4ce4d5041956b17caed52219",
            "canonical_hash_match": true
          },
          {
            "time_ms": 700,
            "effective_time_ms": 0,
            "frame_index": 0,
            "duration_ms": 100,
            "visual_delta": "base_pose",
            "canonical_pixel_hash": "sha256:fd27f573ab85107bd9269ebec16db7a959f5a0a4b38b7f03aec741b9b3fd3e08",
            "expected_canonical_pixel_hash": "sha256:fd27f573ab85107bd9269ebec16db7a959f5a0a4b38b7f03aec741b9b3fd3e08",
            "canonical_hash_match": true
          }
        ],
        "sample_count": 6,
        "loop": true,
        "total_duration_ms": 700
      }
    },
    {
      "profile_id": "slip_amber_social",
      "policy_id": "shelf_height_desc",
      "asset": {
        "asset_id": "slip_amber_social_shelf_arbitrary_atlas.png",
        "format_id": "spritesheet_png",
        "media_type": "image/png",
        "uri": "generated://workshop/spritesheet-arbitrary-atlas/slip_amber_social_shelf_arbitrary_atlas.png",
        "width": 19,
        "height": 15,
        "frame_count": 5,
        "content_hash": "sha256:7aa9bac7949a682ff6f8698de1eb52d4fac6e3c0880437d8efe8506fcfb08c1f",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 19,
        "height": 15,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 285,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ]
      },
      "frame_count": 5,
      "packing_policy": {
        "algorithm_id": "shelf_height_desc",
        "basis": "height-descending shelf baseline",
        "max_width": 20,
        "padding_px": 1,
        "allow_rotation": true,
        "used_rect_area": 190,
        "sheet_area": 285,
        "wasted_area": 95,
        "occupancy_rate": 0.666667,
        "placement_order": [
          0,
          2,
          1,
          4,
          3
        ]
      },
      "semantic_fidelity": 1.0,
      "reconstructed_frame_fidelity": 1.0,
      "runtime_frame_fidelity": 1.0,
      "runtime_playback": {
        "timeline": [
          {
            "time_ms": 0,
            "effective_time_ms": 0,
            "frame_index": 0,
            "duration_ms": 100,
            "visual_delta": "base_pose",
            "canonical_pixel_hash": "sha256:ddf7b424d0c816e9a59f63c88f3405119b6388baecae0cde5a2f11c3716d24a3",
            "expected_canonical_pixel_hash": "sha256:ddf7b424d0c816e9a59f63c88f3405119b6388baecae0cde5a2f11c3716d24a3",
            "canonical_hash_match": true
          },
          {
            "time_ms": 100,
            "effective_time_ms": 100,
            "frame_index": 1,
            "duration_ms": 120,
            "visual_delta": "sensor_blink_crop",
            "canonical_pixel_hash": "sha256:c2d583b38a539ac92d082ea428ec8f51317284efd157fa22dab3860886f28b50",
            "expected_canonical_pixel_hash": "sha256:c2d583b38a539ac92d082ea428ec8f51317284efd157fa22dab3860886f28b50",
            "canonical_hash_match": true
          },
          {
            "time_ms": 220,
            "effective_time_ms": 220,
            "frame_index": 2,
            "duration_ms": 140,
            "visual_delta": "left_body_sweep",
            "canonical_pixel_hash": "sha256:ba6938199211780119ab5a3efc5940e18e57ececa12fa3fa362a44ff4c00ab62",
            "expected_canonical_pixel_hash": "sha256:ba6938199211780119ab5a3efc5940e18e57ececa12fa3fa362a44ff4c00ab62",
            "canonical_hash_match": true
          },
          {
            "time_ms": 360,
            "effective_time_ms": 360,
            "frame_index": 3,
            "duration_ms": 160,
            "visual_delta": "upper_anchor_echo",
            "canonical_pixel_hash": "sha256:70802419be21d860d91e45a91d2ff29ddfefa3c5df156fd810f2b6d9e501bc21",
            "expected_canonical_pixel_hash": "sha256:70802419be21d860d91e45a91d2ff29ddfefa3c5df156fd810f2b6d9e501bc21",
            "canonical_hash_match": true
          },
          {
            "time_ms": 520,
            "effective_time_ms": 520,
            "frame_index": 4,
            "duration_ms": 180,
            "visual_delta": "lower_expression_pulse",
            "canonical_pixel_hash": "sha256:ffea7bb1d2d8da8c5d48009df2799152e7a5b8308c327cdc1a5e8cf6e1728a46",
            "expected_canonical_pixel_hash": "sha256:ffea7bb1d2d8da8c5d48009df2799152e7a5b8308c327cdc1a5e8cf6e1728a46",
            "canonical_hash_match": true
          },
          {
            "time_ms": 700,
            "effective_time_ms": 0,
            "frame_index": 0,
            "duration_ms": 100,
            "visual_delta": "base_pose",
            "canonical_pixel_hash": "sha256:ddf7b424d0c816e9a59f63c88f3405119b6388baecae0cde5a2f11c3716d24a3",
            "expected_canonical_pixel_hash": "sha256:ddf7b424d0c816e9a59f63c88f3405119b6388baecae0cde5a2f11c3716d24a3",
            "canonical_hash_match": true
          }
        ],
        "sample_count": 6,
        "loop": true,
        "total_duration_ms": 700
      }
    },
    {
      "profile_id": "slip_amber_social",
      "policy_id": "maxrects_best_short_side_fit",
      "asset": {
        "asset_id": "slip_amber_social_maxrects_arbitrary_atlas.png",
        "format_id": "spritesheet_png",
        "media_type": "image/png",
        "uri": "generated://workshop/spritesheet-arbitrary-atlas/slip_amber_social_maxrects_arbitrary_atlas.png",
        "width": 16,
        "height": 17,
        "frame_count": 5,
        "content_hash": "sha256:3c969410d556446a684c145cb6cc277db3b0fb795abea41a2833b97d13d2a253",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 16,
        "height": 17,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 272,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ]
      },
      "frame_count": 5,
      "packing_policy": {
        "algorithm_id": "maxrects_best_short_side_fit",
        "basis": "MaxRects-style best-short-side-fit rectangle placement",
        "max_width": 16,
        "padding_px": 1,
        "allow_rotation": true,
        "used_rect_area": 190,
        "sheet_area": 272,
        "wasted_area": 82,
        "occupancy_rate": 0.698529,
        "placement_order": [
          0,
          4,
          2,
          1,
          3
        ]
      },
      "semantic_fidelity": 1.0,
      "reconstructed_frame_fidelity": 1.0,
      "runtime_frame_fidelity": 1.0,
      "runtime_playback": {
        "timeline": [
          {
            "time_ms": 0,
            "effective_time_ms": 0,
            "frame_index": 0,
            "duration_ms": 100,
            "visual_delta": "base_pose",
            "canonical_pixel_hash": "sha256:ddf7b424d0c816e9a59f63c88f3405119b6388baecae0cde5a2f11c3716d24a3",
            "expected_canonical_pixel_hash": "sha256:ddf7b424d0c816e9a59f63c88f3405119b6388baecae0cde5a2f11c3716d24a3",
            "canonical_hash_match": true
          },
          {
            "time_ms": 100,
            "effective_time_ms": 100,
            "frame_index": 1,
            "duration_ms": 120,
            "visual_delta": "sensor_blink_crop",
            "canonical_pixel_hash": "sha256:c2d583b38a539ac92d082ea428ec8f51317284efd157fa22dab3860886f28b50",
            "expected_canonical_pixel_hash": "sha256:c2d583b38a539ac92d082ea428ec8f51317284efd157fa22dab3860886f28b50",
            "canonical_hash_match": true
          },
          {
            "time_ms": 220,
            "effective_time_ms": 220,
            "frame_index": 2,
            "duration_ms": 140,
            "visual_delta": "left_body_sweep",
            "canonical_pixel_hash": "sha256:ba6938199211780119ab5a3efc5940e18e57ececa12fa3fa362a44ff4c00ab62",
            "expected_canonical_pixel_hash": "sha256:ba6938199211780119ab5a3efc5940e18e57ececa12fa3fa362a44ff4c00ab62",
            "canonical_hash_match": true
          },
          {
            "time_ms": 360,
            "effective_time_ms": 360,
            "frame_index": 3,
            "duration_ms": 160,
            "visual_delta": "upper_anchor_echo",
            "canonical_pixel_hash": "sha256:70802419be21d860d91e45a91d2ff29ddfefa3c5df156fd810f2b6d9e501bc21",
            "expected_canonical_pixel_hash": "sha256:70802419be21d860d91e45a91d2ff29ddfefa3c5df156fd810f2b6d9e501bc21",
            "canonical_hash_match": true
          },
          {
            "time_ms": 520,
            "effective_time_ms": 520,
            "frame_index": 4,
            "duration_ms": 180,
            "visual_delta": "lower_expression_pulse",
            "canonical_pixel_hash": "sha256:ffea7bb1d2d8da8c5d48009df2799152e7a5b8308c327cdc1a5e8cf6e1728a46",
            "expected_canonical_pixel_hash": "sha256:ffea7bb1d2d8da8c5d48009df2799152e7a5b8308c327cdc1a5e8cf6e1728a46",
            "canonical_hash_match": true
          },
          {
            "time_ms": 700,
            "effective_time_ms": 0,
            "frame_index": 0,
            "duration_ms": 100,
            "visual_delta": "base_pose",
            "canonical_pixel_hash": "sha256:ddf7b424d0c816e9a59f63c88f3405119b6388baecae0cde5a2f11c3716d24a3",
            "expected_canonical_pixel_hash": "sha256:ddf7b424d0c816e9a59f63c88f3405119b6388baecae0cde5a2f11c3716d24a3",
            "canonical_hash_match": true
          }
        ],
        "sample_count": 6,
        "loop": true,
        "total_duration_ms": 700
      }
    }
  ]
};
