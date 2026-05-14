window.MECHAGOTCHI_SPRITESHEET_MULTI_PAGE_ATLAS = {
  "report": {
    "artifact_id": "spritesheet_multi_page_atlas_stage0",
    "status": "research_spritesheet_multi_page_atlas_no_package_code",
    "profile_count": 3,
    "bundle_roundtrip_count": 3,
    "bundle_roundtrip_success_count": 3,
    "invalid_probe_count": 6,
    "invalid_probe_rejected_count": 6,
    "metrics": {
      "bundle_roundtrip_success_rate": 1.0,
      "mean_semantic_fidelity": 1.0,
      "mean_reconstructed_frame_fidelity": 1.0,
      "mean_runtime_frame_fidelity": 1.0,
      "mean_page_count": 3.0,
      "mean_frame_count": 7.0,
      "invalid_probe_rejection_rate": 1.0
    },
    "page_policy": {
      "algorithm_id": "multi_page_first_fit_shelf_scan",
      "basis": "first-fit page selection with scanline shelf placement and 0/90-degree rotation candidates",
      "max_page_width": 12,
      "max_page_height": 12,
      "padding_px": 1,
      "allow_rotation": true
    },
    "closed_states": [
      "multi_page_atlas_page_manifest",
      "multi_page_atlas_frame_page_binding",
      "multi_page_atlas_page_hash_validation",
      "multi_page_atlas_runtime_page_switch_sampling",
      "multi_page_atlas_sidecar_semantic_restore",
      "multi_page_atlas_invalid_probe_rejection"
    ],
    "blocked_states": [
      "editor-authored atlas fixtures",
      "production renderer playback",
      "live external editor rewrite validation",
      "full project-format coverage",
      "arbitrary Aseprite project schema coverage",
      "package runtime lifecycle integration",
      "manual readability calibration",
      "profile-weighted evolution"
    ],
    "decision": "prototype_spritesheet_multi_page_atlas"
  },
  "bundle_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "asset": {
        "asset_id": "slip_lcd_seed_multi_page_atlas.bundle",
        "format_id": "spritesheet_atlas_pages",
        "media_type": "application/vnd.mechagotchi.atlas-pages+json",
        "uri": "generated://workshop/spritesheet-multi-page-atlas/slip_lcd_seed.bundle",
        "width": 12,
        "height": 11,
        "frame_count": 7,
        "page_count": 3,
        "pages": [
          {
            "page_index": 0,
            "asset_id": "slip_lcd_seed_multi_page_atlas_page_0.png",
            "width": 8,
            "height": 8,
            "frame_count": 1,
            "content_hash": "sha256:0b011351d8d3c536ba1ef7811887fca161a454cbf02adcb339826b267498c326"
          },
          {
            "page_index": 1,
            "asset_id": "slip_lcd_seed_multi_page_atlas_page_1.png",
            "width": 12,
            "height": 11,
            "frame_count": 3,
            "content_hash": "sha256:e3cf1b7635e2efb302cd39a4732d5e53c255b95217a5d541fc5bfd0fedef9029"
          },
          {
            "page_index": 2,
            "asset_id": "slip_lcd_seed_multi_page_atlas_page_2.png",
            "width": 12,
            "height": 11,
            "frame_count": 3,
            "content_hash": "sha256:bad5353bb0be47991059eac5f2d05e633bc6333b53af310ff8f37af32fe2ee50"
          }
        ],
        "content_hash": "sha256:58ecd90832a9b60341f046e0bd474fb2b384ba920ae5d70fa6d86093d04f747b",
        "semantic_policy": "sidecar_required"
      },
      "page_count": 3,
      "frame_count": 7,
      "decoded_pages": [
        {
          "page_index": 0,
          "asset_id": "slip_lcd_seed_multi_page_atlas_page_0.png",
          "content_hash": "sha256:0b011351d8d3c536ba1ef7811887fca161a454cbf02adcb339826b267498c326",
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
        {
          "page_index": 1,
          "asset_id": "slip_lcd_seed_multi_page_atlas_page_1.png",
          "content_hash": "sha256:e3cf1b7635e2efb302cd39a4732d5e53c255b95217a5d541fc5bfd0fedef9029",
          "width": 12,
          "height": 11,
          "bit_depth": 8,
          "color_type": 6,
          "pixel_count": 132,
          "chunks": [
            "IHDR",
            "IDAT",
            "IEND"
          ]
        },
        {
          "page_index": 2,
          "asset_id": "slip_lcd_seed_multi_page_atlas_page_2.png",
          "content_hash": "sha256:bad5353bb0be47991059eac5f2d05e633bc6333b53af310ff8f37af32fe2ee50",
          "width": 12,
          "height": 11,
          "bit_depth": 8,
          "color_type": 6,
          "pixel_count": 132,
          "chunks": [
            "IHDR",
            "IDAT",
            "IEND"
          ]
        }
      ],
      "semantic_fidelity": 1.0,
      "reconstructed_frame_fidelity": 1.0,
      "runtime_frame_fidelity": 1.0,
      "runtime_playback": {
        "timeline": [
          {
            "time_ms": 0,
            "effective_time_ms": 0,
            "frame_index": 0,
            "page_index": 0,
            "duration_ms": 90,
            "visual_delta": "base_pose",
            "page_content_hash": "sha256:0b011351d8d3c536ba1ef7811887fca161a454cbf02adcb339826b267498c326",
            "expected_page_content_hash": "sha256:0b011351d8d3c536ba1ef7811887fca161a454cbf02adcb339826b267498c326",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:97548c7836c0223dc594e82a9d608b98a96e5247b09864e29c81be367f0db9b3",
            "expected_canonical_pixel_hash": "sha256:97548c7836c0223dc594e82a9d608b98a96e5247b09864e29c81be367f0db9b3",
            "canonical_hash_match": true
          },
          {
            "time_ms": 90,
            "effective_time_ms": 90,
            "frame_index": 1,
            "page_index": 1,
            "duration_ms": 110,
            "visual_delta": "sensor_blink_crop",
            "page_content_hash": "sha256:e3cf1b7635e2efb302cd39a4732d5e53c255b95217a5d541fc5bfd0fedef9029",
            "expected_page_content_hash": "sha256:e3cf1b7635e2efb302cd39a4732d5e53c255b95217a5d541fc5bfd0fedef9029",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:0c1eaa187c72469607ef1e34a12b0ceace404f0ffdcbc09bdcd213e4450bd8ce",
            "expected_canonical_pixel_hash": "sha256:0c1eaa187c72469607ef1e34a12b0ceace404f0ffdcbc09bdcd213e4450bd8ce",
            "canonical_hash_match": true
          },
          {
            "time_ms": 200,
            "effective_time_ms": 200,
            "frame_index": 2,
            "page_index": 1,
            "duration_ms": 130,
            "visual_delta": "left_body_sweep",
            "page_content_hash": "sha256:e3cf1b7635e2efb302cd39a4732d5e53c255b95217a5d541fc5bfd0fedef9029",
            "expected_page_content_hash": "sha256:e3cf1b7635e2efb302cd39a4732d5e53c255b95217a5d541fc5bfd0fedef9029",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:319e103118aeecceeb2971c5e8b6fbe412cd42852840728594053905c8026b2a",
            "expected_canonical_pixel_hash": "sha256:319e103118aeecceeb2971c5e8b6fbe412cd42852840728594053905c8026b2a",
            "canonical_hash_match": true
          },
          {
            "time_ms": 330,
            "effective_time_ms": 330,
            "frame_index": 3,
            "page_index": 1,
            "duration_ms": 150,
            "visual_delta": "upper_anchor_echo",
            "page_content_hash": "sha256:e3cf1b7635e2efb302cd39a4732d5e53c255b95217a5d541fc5bfd0fedef9029",
            "expected_page_content_hash": "sha256:e3cf1b7635e2efb302cd39a4732d5e53c255b95217a5d541fc5bfd0fedef9029",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:efc7c0a4f7c58ed537a22c260f9eb4e7361577cae0f093b6dade6a3d615319e8",
            "expected_canonical_pixel_hash": "sha256:efc7c0a4f7c58ed537a22c260f9eb4e7361577cae0f093b6dade6a3d615319e8",
            "canonical_hash_match": true
          },
          {
            "time_ms": 480,
            "effective_time_ms": 480,
            "frame_index": 4,
            "page_index": 2,
            "duration_ms": 170,
            "visual_delta": "lower_expression_pulse",
            "page_content_hash": "sha256:bad5353bb0be47991059eac5f2d05e633bc6333b53af310ff8f37af32fe2ee50",
            "expected_page_content_hash": "sha256:bad5353bb0be47991059eac5f2d05e633bc6333b53af310ff8f37af32fe2ee50",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:62c127f389a65ed80c75191e9f93442c694692a1f0a1ac61e32c5befa398dce0",
            "expected_canonical_pixel_hash": "sha256:62c127f389a65ed80c75191e9f93442c694692a1f0a1ac61e32c5befa398dce0",
            "canonical_hash_match": true
          },
          {
            "time_ms": 650,
            "effective_time_ms": 650,
            "frame_index": 5,
            "page_index": 2,
            "duration_ms": 190,
            "visual_delta": "right_sensor_stride",
            "page_content_hash": "sha256:bad5353bb0be47991059eac5f2d05e633bc6333b53af310ff8f37af32fe2ee50",
            "expected_page_content_hash": "sha256:bad5353bb0be47991059eac5f2d05e633bc6333b53af310ff8f37af32fe2ee50",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:40163e002303e57871e68771a90ead8423daea0e526dd8da5f77b16128fab633",
            "expected_canonical_pixel_hash": "sha256:40163e002303e57871e68771a90ead8423daea0e526dd8da5f77b16128fab633",
            "canonical_hash_match": true
          },
          {
            "time_ms": 840,
            "effective_time_ms": 840,
            "frame_index": 6,
            "page_index": 2,
            "duration_ms": 210,
            "visual_delta": "core_idle_glow",
            "page_content_hash": "sha256:bad5353bb0be47991059eac5f2d05e633bc6333b53af310ff8f37af32fe2ee50",
            "expected_page_content_hash": "sha256:bad5353bb0be47991059eac5f2d05e633bc6333b53af310ff8f37af32fe2ee50",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:49685375d87666a6320aa64b64202787b70474127d31651e80cf5e7d73036b7d",
            "expected_canonical_pixel_hash": "sha256:49685375d87666a6320aa64b64202787b70474127d31651e80cf5e7d73036b7d",
            "canonical_hash_match": true
          },
          {
            "time_ms": 1050,
            "effective_time_ms": 0,
            "frame_index": 0,
            "page_index": 0,
            "duration_ms": 90,
            "visual_delta": "base_pose",
            "page_content_hash": "sha256:0b011351d8d3c536ba1ef7811887fca161a454cbf02adcb339826b267498c326",
            "expected_page_content_hash": "sha256:0b011351d8d3c536ba1ef7811887fca161a454cbf02adcb339826b267498c326",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:97548c7836c0223dc594e82a9d608b98a96e5247b09864e29c81be367f0db9b3",
            "expected_canonical_pixel_hash": "sha256:97548c7836c0223dc594e82a9d608b98a96e5247b09864e29c81be367f0db9b3",
            "canonical_hash_match": true
          }
        ],
        "sample_count": 8,
        "loop": true,
        "total_duration_ms": 1050
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "asset": {
        "asset_id": "slip_gray_stable_multi_page_atlas.bundle",
        "format_id": "spritesheet_atlas_pages",
        "media_type": "application/vnd.mechagotchi.atlas-pages+json",
        "uri": "generated://workshop/spritesheet-multi-page-atlas/slip_gray_stable.bundle",
        "width": 12,
        "height": 11,
        "frame_count": 7,
        "page_count": 3,
        "pages": [
          {
            "page_index": 0,
            "asset_id": "slip_gray_stable_multi_page_atlas_page_0.png",
            "width": 8,
            "height": 8,
            "frame_count": 1,
            "content_hash": "sha256:204ae78a574e2913c22cd2e9bb1d0882b1b5805be69c66a73f2c7dc4ddb7f6a4"
          },
          {
            "page_index": 1,
            "asset_id": "slip_gray_stable_multi_page_atlas_page_1.png",
            "width": 12,
            "height": 11,
            "frame_count": 3,
            "content_hash": "sha256:b7b96125827ac24d7ea1179ab69af9e361fc505d7e504206572a9af5e5c83a00"
          },
          {
            "page_index": 2,
            "asset_id": "slip_gray_stable_multi_page_atlas_page_2.png",
            "width": 12,
            "height": 11,
            "frame_count": 3,
            "content_hash": "sha256:b8c01b29fa2d05c4ea5f2d9f644fce7c610689975bdef9872e9c475506458f79"
          }
        ],
        "content_hash": "sha256:3b361fcc29f2654db41549a33a51c515b4df06ac5bec4b1166422b9023567c74",
        "semantic_policy": "sidecar_required"
      },
      "page_count": 3,
      "frame_count": 7,
      "decoded_pages": [
        {
          "page_index": 0,
          "asset_id": "slip_gray_stable_multi_page_atlas_page_0.png",
          "content_hash": "sha256:204ae78a574e2913c22cd2e9bb1d0882b1b5805be69c66a73f2c7dc4ddb7f6a4",
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
        {
          "page_index": 1,
          "asset_id": "slip_gray_stable_multi_page_atlas_page_1.png",
          "content_hash": "sha256:b7b96125827ac24d7ea1179ab69af9e361fc505d7e504206572a9af5e5c83a00",
          "width": 12,
          "height": 11,
          "bit_depth": 8,
          "color_type": 6,
          "pixel_count": 132,
          "chunks": [
            "IHDR",
            "IDAT",
            "IEND"
          ]
        },
        {
          "page_index": 2,
          "asset_id": "slip_gray_stable_multi_page_atlas_page_2.png",
          "content_hash": "sha256:b8c01b29fa2d05c4ea5f2d9f644fce7c610689975bdef9872e9c475506458f79",
          "width": 12,
          "height": 11,
          "bit_depth": 8,
          "color_type": 6,
          "pixel_count": 132,
          "chunks": [
            "IHDR",
            "IDAT",
            "IEND"
          ]
        }
      ],
      "semantic_fidelity": 1.0,
      "reconstructed_frame_fidelity": 1.0,
      "runtime_frame_fidelity": 1.0,
      "runtime_playback": {
        "timeline": [
          {
            "time_ms": 0,
            "effective_time_ms": 0,
            "frame_index": 0,
            "page_index": 0,
            "duration_ms": 90,
            "visual_delta": "base_pose",
            "page_content_hash": "sha256:204ae78a574e2913c22cd2e9bb1d0882b1b5805be69c66a73f2c7dc4ddb7f6a4",
            "expected_page_content_hash": "sha256:204ae78a574e2913c22cd2e9bb1d0882b1b5805be69c66a73f2c7dc4ddb7f6a4",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:fd27f573ab85107bd9269ebec16db7a959f5a0a4b38b7f03aec741b9b3fd3e08",
            "expected_canonical_pixel_hash": "sha256:fd27f573ab85107bd9269ebec16db7a959f5a0a4b38b7f03aec741b9b3fd3e08",
            "canonical_hash_match": true
          },
          {
            "time_ms": 90,
            "effective_time_ms": 90,
            "frame_index": 1,
            "page_index": 1,
            "duration_ms": 110,
            "visual_delta": "sensor_blink_crop",
            "page_content_hash": "sha256:b7b96125827ac24d7ea1179ab69af9e361fc505d7e504206572a9af5e5c83a00",
            "expected_page_content_hash": "sha256:b7b96125827ac24d7ea1179ab69af9e361fc505d7e504206572a9af5e5c83a00",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:c015132120bc46a23bf3a848bd9ca2048878e36bf66b5c9672f3034b539e9b2c",
            "expected_canonical_pixel_hash": "sha256:c015132120bc46a23bf3a848bd9ca2048878e36bf66b5c9672f3034b539e9b2c",
            "canonical_hash_match": true
          },
          {
            "time_ms": 200,
            "effective_time_ms": 200,
            "frame_index": 2,
            "page_index": 1,
            "duration_ms": 130,
            "visual_delta": "left_body_sweep",
            "page_content_hash": "sha256:b7b96125827ac24d7ea1179ab69af9e361fc505d7e504206572a9af5e5c83a00",
            "expected_page_content_hash": "sha256:b7b96125827ac24d7ea1179ab69af9e361fc505d7e504206572a9af5e5c83a00",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:b6776b8970c8fc51ba319b1dbebd3485da0eb9b161d12548578a9039710091d5",
            "expected_canonical_pixel_hash": "sha256:b6776b8970c8fc51ba319b1dbebd3485da0eb9b161d12548578a9039710091d5",
            "canonical_hash_match": true
          },
          {
            "time_ms": 330,
            "effective_time_ms": 330,
            "frame_index": 3,
            "page_index": 1,
            "duration_ms": 150,
            "visual_delta": "upper_anchor_echo",
            "page_content_hash": "sha256:b7b96125827ac24d7ea1179ab69af9e361fc505d7e504206572a9af5e5c83a00",
            "expected_page_content_hash": "sha256:b7b96125827ac24d7ea1179ab69af9e361fc505d7e504206572a9af5e5c83a00",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:0df70f74bc6b6cf86581d410babff6945d5b90234d78fcd6206026fb9862587b",
            "expected_canonical_pixel_hash": "sha256:0df70f74bc6b6cf86581d410babff6945d5b90234d78fcd6206026fb9862587b",
            "canonical_hash_match": true
          },
          {
            "time_ms": 480,
            "effective_time_ms": 480,
            "frame_index": 4,
            "page_index": 2,
            "duration_ms": 170,
            "visual_delta": "lower_expression_pulse",
            "page_content_hash": "sha256:b8c01b29fa2d05c4ea5f2d9f644fce7c610689975bdef9872e9c475506458f79",
            "expected_page_content_hash": "sha256:b8c01b29fa2d05c4ea5f2d9f644fce7c610689975bdef9872e9c475506458f79",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:07ae2b9f301a2bc4174a6398b71eff67a0f3cd8f4ce4d5041956b17caed52219",
            "expected_canonical_pixel_hash": "sha256:07ae2b9f301a2bc4174a6398b71eff67a0f3cd8f4ce4d5041956b17caed52219",
            "canonical_hash_match": true
          },
          {
            "time_ms": 650,
            "effective_time_ms": 650,
            "frame_index": 5,
            "page_index": 2,
            "duration_ms": 190,
            "visual_delta": "right_sensor_stride",
            "page_content_hash": "sha256:b8c01b29fa2d05c4ea5f2d9f644fce7c610689975bdef9872e9c475506458f79",
            "expected_page_content_hash": "sha256:b8c01b29fa2d05c4ea5f2d9f644fce7c610689975bdef9872e9c475506458f79",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:88919e43439d2f83ebdb1f2dcf3afa812014b2b5d0abc1b3bf63c0e11f968fbf",
            "expected_canonical_pixel_hash": "sha256:88919e43439d2f83ebdb1f2dcf3afa812014b2b5d0abc1b3bf63c0e11f968fbf",
            "canonical_hash_match": true
          },
          {
            "time_ms": 840,
            "effective_time_ms": 840,
            "frame_index": 6,
            "page_index": 2,
            "duration_ms": 210,
            "visual_delta": "core_idle_glow",
            "page_content_hash": "sha256:b8c01b29fa2d05c4ea5f2d9f644fce7c610689975bdef9872e9c475506458f79",
            "expected_page_content_hash": "sha256:b8c01b29fa2d05c4ea5f2d9f644fce7c610689975bdef9872e9c475506458f79",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:e7dbfc0ee9f86120efe6ffbb516583596cec335a46fa19d726ce17c28f7b2c88",
            "expected_canonical_pixel_hash": "sha256:e7dbfc0ee9f86120efe6ffbb516583596cec335a46fa19d726ce17c28f7b2c88",
            "canonical_hash_match": true
          },
          {
            "time_ms": 1050,
            "effective_time_ms": 0,
            "frame_index": 0,
            "page_index": 0,
            "duration_ms": 90,
            "visual_delta": "base_pose",
            "page_content_hash": "sha256:204ae78a574e2913c22cd2e9bb1d0882b1b5805be69c66a73f2c7dc4ddb7f6a4",
            "expected_page_content_hash": "sha256:204ae78a574e2913c22cd2e9bb1d0882b1b5805be69c66a73f2c7dc4ddb7f6a4",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:fd27f573ab85107bd9269ebec16db7a959f5a0a4b38b7f03aec741b9b3fd3e08",
            "expected_canonical_pixel_hash": "sha256:fd27f573ab85107bd9269ebec16db7a959f5a0a4b38b7f03aec741b9b3fd3e08",
            "canonical_hash_match": true
          }
        ],
        "sample_count": 8,
        "loop": true,
        "total_duration_ms": 1050
      }
    },
    {
      "profile_id": "slip_amber_social",
      "asset": {
        "asset_id": "slip_amber_social_multi_page_atlas.bundle",
        "format_id": "spritesheet_atlas_pages",
        "media_type": "application/vnd.mechagotchi.atlas-pages+json",
        "uri": "generated://workshop/spritesheet-multi-page-atlas/slip_amber_social.bundle",
        "width": 12,
        "height": 11,
        "frame_count": 7,
        "page_count": 3,
        "pages": [
          {
            "page_index": 0,
            "asset_id": "slip_amber_social_multi_page_atlas_page_0.png",
            "width": 8,
            "height": 8,
            "frame_count": 1,
            "content_hash": "sha256:a70d506ab208c13058773c1325d08a2674045b301bd04d02ac5dc30b170ecd56"
          },
          {
            "page_index": 1,
            "asset_id": "slip_amber_social_multi_page_atlas_page_1.png",
            "width": 12,
            "height": 11,
            "frame_count": 3,
            "content_hash": "sha256:7906fef3363a40df0d2833c48c732c17333314d52fb7c6484c50e9a50de56474"
          },
          {
            "page_index": 2,
            "asset_id": "slip_amber_social_multi_page_atlas_page_2.png",
            "width": 12,
            "height": 11,
            "frame_count": 3,
            "content_hash": "sha256:98b0b97f659e4e70f7d560550e659cac6d719b4d6b1a333e51766c0188e8923f"
          }
        ],
        "content_hash": "sha256:866c8995c9d1903b6ce84712ef22bdca8485e11293a0d3e1f33c8250e7439c2b",
        "semantic_policy": "sidecar_required"
      },
      "page_count": 3,
      "frame_count": 7,
      "decoded_pages": [
        {
          "page_index": 0,
          "asset_id": "slip_amber_social_multi_page_atlas_page_0.png",
          "content_hash": "sha256:a70d506ab208c13058773c1325d08a2674045b301bd04d02ac5dc30b170ecd56",
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
        {
          "page_index": 1,
          "asset_id": "slip_amber_social_multi_page_atlas_page_1.png",
          "content_hash": "sha256:7906fef3363a40df0d2833c48c732c17333314d52fb7c6484c50e9a50de56474",
          "width": 12,
          "height": 11,
          "bit_depth": 8,
          "color_type": 6,
          "pixel_count": 132,
          "chunks": [
            "IHDR",
            "IDAT",
            "IEND"
          ]
        },
        {
          "page_index": 2,
          "asset_id": "slip_amber_social_multi_page_atlas_page_2.png",
          "content_hash": "sha256:98b0b97f659e4e70f7d560550e659cac6d719b4d6b1a333e51766c0188e8923f",
          "width": 12,
          "height": 11,
          "bit_depth": 8,
          "color_type": 6,
          "pixel_count": 132,
          "chunks": [
            "IHDR",
            "IDAT",
            "IEND"
          ]
        }
      ],
      "semantic_fidelity": 1.0,
      "reconstructed_frame_fidelity": 1.0,
      "runtime_frame_fidelity": 1.0,
      "runtime_playback": {
        "timeline": [
          {
            "time_ms": 0,
            "effective_time_ms": 0,
            "frame_index": 0,
            "page_index": 0,
            "duration_ms": 90,
            "visual_delta": "base_pose",
            "page_content_hash": "sha256:a70d506ab208c13058773c1325d08a2674045b301bd04d02ac5dc30b170ecd56",
            "expected_page_content_hash": "sha256:a70d506ab208c13058773c1325d08a2674045b301bd04d02ac5dc30b170ecd56",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:ddf7b424d0c816e9a59f63c88f3405119b6388baecae0cde5a2f11c3716d24a3",
            "expected_canonical_pixel_hash": "sha256:ddf7b424d0c816e9a59f63c88f3405119b6388baecae0cde5a2f11c3716d24a3",
            "canonical_hash_match": true
          },
          {
            "time_ms": 90,
            "effective_time_ms": 90,
            "frame_index": 1,
            "page_index": 1,
            "duration_ms": 110,
            "visual_delta": "sensor_blink_crop",
            "page_content_hash": "sha256:7906fef3363a40df0d2833c48c732c17333314d52fb7c6484c50e9a50de56474",
            "expected_page_content_hash": "sha256:7906fef3363a40df0d2833c48c732c17333314d52fb7c6484c50e9a50de56474",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:c2d583b38a539ac92d082ea428ec8f51317284efd157fa22dab3860886f28b50",
            "expected_canonical_pixel_hash": "sha256:c2d583b38a539ac92d082ea428ec8f51317284efd157fa22dab3860886f28b50",
            "canonical_hash_match": true
          },
          {
            "time_ms": 200,
            "effective_time_ms": 200,
            "frame_index": 2,
            "page_index": 1,
            "duration_ms": 130,
            "visual_delta": "left_body_sweep",
            "page_content_hash": "sha256:7906fef3363a40df0d2833c48c732c17333314d52fb7c6484c50e9a50de56474",
            "expected_page_content_hash": "sha256:7906fef3363a40df0d2833c48c732c17333314d52fb7c6484c50e9a50de56474",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:ba6938199211780119ab5a3efc5940e18e57ececa12fa3fa362a44ff4c00ab62",
            "expected_canonical_pixel_hash": "sha256:ba6938199211780119ab5a3efc5940e18e57ececa12fa3fa362a44ff4c00ab62",
            "canonical_hash_match": true
          },
          {
            "time_ms": 330,
            "effective_time_ms": 330,
            "frame_index": 3,
            "page_index": 1,
            "duration_ms": 150,
            "visual_delta": "upper_anchor_echo",
            "page_content_hash": "sha256:7906fef3363a40df0d2833c48c732c17333314d52fb7c6484c50e9a50de56474",
            "expected_page_content_hash": "sha256:7906fef3363a40df0d2833c48c732c17333314d52fb7c6484c50e9a50de56474",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:70802419be21d860d91e45a91d2ff29ddfefa3c5df156fd810f2b6d9e501bc21",
            "expected_canonical_pixel_hash": "sha256:70802419be21d860d91e45a91d2ff29ddfefa3c5df156fd810f2b6d9e501bc21",
            "canonical_hash_match": true
          },
          {
            "time_ms": 480,
            "effective_time_ms": 480,
            "frame_index": 4,
            "page_index": 2,
            "duration_ms": 170,
            "visual_delta": "lower_expression_pulse",
            "page_content_hash": "sha256:98b0b97f659e4e70f7d560550e659cac6d719b4d6b1a333e51766c0188e8923f",
            "expected_page_content_hash": "sha256:98b0b97f659e4e70f7d560550e659cac6d719b4d6b1a333e51766c0188e8923f",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:ffea7bb1d2d8da8c5d48009df2799152e7a5b8308c327cdc1a5e8cf6e1728a46",
            "expected_canonical_pixel_hash": "sha256:ffea7bb1d2d8da8c5d48009df2799152e7a5b8308c327cdc1a5e8cf6e1728a46",
            "canonical_hash_match": true
          },
          {
            "time_ms": 650,
            "effective_time_ms": 650,
            "frame_index": 5,
            "page_index": 2,
            "duration_ms": 190,
            "visual_delta": "right_sensor_stride",
            "page_content_hash": "sha256:98b0b97f659e4e70f7d560550e659cac6d719b4d6b1a333e51766c0188e8923f",
            "expected_page_content_hash": "sha256:98b0b97f659e4e70f7d560550e659cac6d719b4d6b1a333e51766c0188e8923f",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:b612da2f7bd9f457afb26799c5e797daabe8a2e964811b6dd1109c249c1d5e0c",
            "expected_canonical_pixel_hash": "sha256:b612da2f7bd9f457afb26799c5e797daabe8a2e964811b6dd1109c249c1d5e0c",
            "canonical_hash_match": true
          },
          {
            "time_ms": 840,
            "effective_time_ms": 840,
            "frame_index": 6,
            "page_index": 2,
            "duration_ms": 210,
            "visual_delta": "core_idle_glow",
            "page_content_hash": "sha256:98b0b97f659e4e70f7d560550e659cac6d719b4d6b1a333e51766c0188e8923f",
            "expected_page_content_hash": "sha256:98b0b97f659e4e70f7d560550e659cac6d719b4d6b1a333e51766c0188e8923f",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:9158bd8b35a40626d4e3c1f4957140cfe8d04a51e532bd8e95c81e4250677c5a",
            "expected_canonical_pixel_hash": "sha256:9158bd8b35a40626d4e3c1f4957140cfe8d04a51e532bd8e95c81e4250677c5a",
            "canonical_hash_match": true
          },
          {
            "time_ms": 1050,
            "effective_time_ms": 0,
            "frame_index": 0,
            "page_index": 0,
            "duration_ms": 90,
            "visual_delta": "base_pose",
            "page_content_hash": "sha256:a70d506ab208c13058773c1325d08a2674045b301bd04d02ac5dc30b170ecd56",
            "expected_page_content_hash": "sha256:a70d506ab208c13058773c1325d08a2674045b301bd04d02ac5dc30b170ecd56",
            "page_hash_match": true,
            "canonical_pixel_hash": "sha256:ddf7b424d0c816e9a59f63c88f3405119b6388baecae0cde5a2f11c3716d24a3",
            "expected_canonical_pixel_hash": "sha256:ddf7b424d0c816e9a59f63c88f3405119b6388baecae0cde5a2f11c3716d24a3",
            "canonical_hash_match": true
          }
        ],
        "sample_count": 8,
        "loop": true,
        "total_duration_ms": 1050
      }
    }
  ]
};
