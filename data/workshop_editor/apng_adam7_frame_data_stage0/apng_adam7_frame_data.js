window.MECHAGOTCHI_APNG_ADAM7_FRAME_DATA = {
  "report": {
    "artifact_id": "apng_adam7_frame_data_stage0",
    "status": "research_apng_adam7_frame_data_no_package_code",
    "profile_count": 3,
    "case_ids": [
      "rgba8_adam7_fdat",
      "grayscale1_adam7_fdat",
      "indexed4_adam7_trns_fdat",
      "truecolor16_adam7_fdat",
      "grayscale_alpha16_adam7_over_fdat",
      "truecolor_alpha16_adam7_over_fdat"
    ],
    "case_count": 18,
    "case_success_count": 18,
    "invalid_probe_count": 5,
    "invalid_probe_rejected_count": 5,
    "metrics": {
      "case_success_ratio": 1.0,
      "invalid_probe_rejection_ratio": 1.0,
      "profile_coverage": 3,
      "case_family_count": 6,
      "supported_color_types": [
        0,
        2,
        3,
        4,
        6
      ],
      "supported_bit_depths": [
        1,
        4,
        8,
        16
      ],
      "supported_filter_types": [
        0,
        1,
        2,
        3,
        4
      ],
      "supported_interlace_methods": [
        1
      ],
      "adam7_pass_count": 7,
      "split_fdat_frame_count": 18,
      "over_blend_case_count": 6,
      "live_external_editor_verified": false
    },
    "closed_states": [
      "apng_adam7_frame_reconstruction",
      "apng_adam7_pass_manifest_reconstruction",
      "apng_adam7_deep_sample_reconstruction",
      "apng_adam7_split_fdat_reconstruction",
      "apng_adam7_invalid_probe_rejection"
    ],
    "blocked_states": [
      "full_apng_png_conformance",
      "live_external_editor_rewrite_validation",
      "production_import_export_carrier_selection_final_decision",
      "manual_readability_calibration",
      "package_runtime_lifecycle_integration"
    ],
    "decision": "prototype_apng_adam7_frame_data_subset"
  },
  "case_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "rgba8_adam7_fdat",
      "color_type": 6,
      "bit_depth": 8,
      "blend_op": 0,
      "interlace_method": 1,
      "png_file_name": "slip_lcd_seed_rgba8_adam7_fdat.png",
      "png_hash": "sha256:6675bb4a41ca2c25d739a0133a4b4aba637c50ed8a77000b8046ff52e76d6b9a",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 8,
          "color_type": 6,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "interlace_method": 1,
        "bytes_per_pixel": 4,
        "scanline_byte_length": 32,
        "filter_bpp": 4,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": false,
          "entry_count": 0
        },
        "transparency": {
          "present": false,
          "entry_count": 0
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 32,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:a05934dcbed44d28e1cbf938ef18305421c1d62fedad6540e5c006a80ed7f79b"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 32,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:f95383cecc60457f520065899c2cf9db6048371dec65e57bcee67cc097a052c7"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:a05934dcbed44d28e1cbf938ef18305421c1d62fedad6540e5c006a80ed7f79b",
          "sha256:f95383cecc60457f520065899c2cf9db6048371dec65e57bcee67cc097a052c7"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:a05934dcbed44d28e1cbf938ef18305421c1d62fedad6540e5c006a80ed7f79b",
          "sha256:f95383cecc60457f520065899c2cf9db6048371dec65e57bcee67cc097a052c7"
        ],
        "after_dispose_hashes": [
          "sha256:a05934dcbed44d28e1cbf938ef18305421c1d62fedad6540e5c006a80ed7f79b",
          "sha256:f95383cecc60457f520065899c2cf9db6048371dec65e57bcee67cc097a052c7"
        ],
        "final_canvas_hash": "sha256:f95383cecc60457f520065899c2cf9db6048371dec65e57bcee67cc097a052c7",
        "final_output_hash": "sha256:f95383cecc60457f520065899c2cf9db6048371dec65e57bcee67cc097a052c7"
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "grayscale1_adam7_fdat",
      "color_type": 0,
      "bit_depth": 1,
      "blend_op": 0,
      "interlace_method": 1,
      "png_file_name": "slip_lcd_seed_grayscale1_adam7_fdat.png",
      "png_hash": "sha256:716aa0d0cb49d530856d73705964ae4f2ffe93c98f908395c96dc08a28483c68",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 1,
          "color_type": 0,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 1,
        "color_type": 0,
        "interlace_method": 1,
        "bytes_per_pixel": 1,
        "scanline_byte_length": 1,
        "filter_bpp": 1,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": false,
          "entry_count": 0
        },
        "transparency": {
          "present": false,
          "entry_count": 0
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:a181f8ad524efbdabfaf736729e6183573f716c939ada4c4ba453bfafaae498b"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:2e8e39ea6552d9e815d880f04548c99525e7d6c567282bb161e738d1471d60d4"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:a181f8ad524efbdabfaf736729e6183573f716c939ada4c4ba453bfafaae498b",
          "sha256:2e8e39ea6552d9e815d880f04548c99525e7d6c567282bb161e738d1471d60d4"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:a181f8ad524efbdabfaf736729e6183573f716c939ada4c4ba453bfafaae498b",
          "sha256:2e8e39ea6552d9e815d880f04548c99525e7d6c567282bb161e738d1471d60d4"
        ],
        "after_dispose_hashes": [
          "sha256:a181f8ad524efbdabfaf736729e6183573f716c939ada4c4ba453bfafaae498b",
          "sha256:2e8e39ea6552d9e815d880f04548c99525e7d6c567282bb161e738d1471d60d4"
        ],
        "final_canvas_hash": "sha256:2e8e39ea6552d9e815d880f04548c99525e7d6c567282bb161e738d1471d60d4",
        "final_output_hash": "sha256:2e8e39ea6552d9e815d880f04548c99525e7d6c567282bb161e738d1471d60d4"
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "indexed4_adam7_trns_fdat",
      "color_type": 3,
      "bit_depth": 4,
      "blend_op": 0,
      "interlace_method": 1,
      "png_file_name": "slip_lcd_seed_indexed4_adam7_trns_fdat.png",
      "png_hash": "sha256:1df76b6c407ac71ca07e5eb992b067c4025fdee0be6f7e33b78842d74ebb93c9",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 4,
          "color_type": 3,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 4,
        "color_type": 3,
        "interlace_method": 1,
        "bytes_per_pixel": 1,
        "scanline_byte_length": 4,
        "filter_bpp": 1,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": true,
          "entry_count": 16
        },
        "transparency": {
          "present": true,
          "entry_count": 16
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 2,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 2,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 4,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 6,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:22592babf8e16ecbf682cd916eae27effa210d6463ea1d8f5ef299242be16744"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 2,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 2,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 4,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 6,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:d5571bc60e8becc571493903550b4994322bfc4e323f13618c01927b16b55cf0"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:22592babf8e16ecbf682cd916eae27effa210d6463ea1d8f5ef299242be16744",
          "sha256:d5571bc60e8becc571493903550b4994322bfc4e323f13618c01927b16b55cf0"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:22592babf8e16ecbf682cd916eae27effa210d6463ea1d8f5ef299242be16744",
          "sha256:d5571bc60e8becc571493903550b4994322bfc4e323f13618c01927b16b55cf0"
        ],
        "after_dispose_hashes": [
          "sha256:22592babf8e16ecbf682cd916eae27effa210d6463ea1d8f5ef299242be16744",
          "sha256:d5571bc60e8becc571493903550b4994322bfc4e323f13618c01927b16b55cf0"
        ],
        "final_canvas_hash": "sha256:d5571bc60e8becc571493903550b4994322bfc4e323f13618c01927b16b55cf0",
        "final_output_hash": "sha256:d5571bc60e8becc571493903550b4994322bfc4e323f13618c01927b16b55cf0"
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "truecolor16_adam7_fdat",
      "color_type": 2,
      "bit_depth": 16,
      "blend_op": 0,
      "interlace_method": 1,
      "png_file_name": "slip_lcd_seed_truecolor16_adam7_fdat.png",
      "png_hash": "sha256:301bb0ccb8e1841300ff7abf8c263152dd8d26370958771e9e8ca0c181bdc388",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 2,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 2,
        "interlace_method": 1,
        "bytes_per_pixel": 6,
        "scanline_byte_length": 48,
        "filter_bpp": 6,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": false,
          "entry_count": 0
        },
        "transparency": {
          "present": false,
          "entry_count": 0
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 6,
                "filter_bpp": 6,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 6,
                "filter_bpp": 6,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 12,
                "filter_bpp": 6,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 12,
                "filter_bpp": 6,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 24,
                "filter_bpp": 6,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 24,
                "filter_bpp": 6,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 48,
                "filter_bpp": 6,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 6,
                "filter_bpp": 6,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 6,
                "filter_bpp": 6,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 12,
                "filter_bpp": 6,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 12,
                "filter_bpp": 6,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 24,
                "filter_bpp": 6,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 24,
                "filter_bpp": 6,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 48,
                "filter_bpp": 6,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:f33ddeecd3843a99d459f8e3d17619cadbc82535b71491bee229b83db17262e8"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:f33ddeecd3843a99d459f8e3d17619cadbc82535b71491bee229b83db17262e8"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:f33ddeecd3843a99d459f8e3d17619cadbc82535b71491bee229b83db17262e8"
        ],
        "after_dispose_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:f33ddeecd3843a99d459f8e3d17619cadbc82535b71491bee229b83db17262e8"
        ],
        "final_canvas_hash": "sha256:f33ddeecd3843a99d459f8e3d17619cadbc82535b71491bee229b83db17262e8",
        "final_output_hash": "sha256:f33ddeecd3843a99d459f8e3d17619cadbc82535b71491bee229b83db17262e8"
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "grayscale_alpha16_adam7_over_fdat",
      "color_type": 4,
      "bit_depth": 16,
      "blend_op": 1,
      "interlace_method": 1,
      "png_file_name": "slip_lcd_seed_grayscale_alpha16_adam7_over_fdat.png",
      "png_hash": "sha256:26f19504e2d9621c2037908978f2776e70ba205e4c58916c3f44c33cd5f5caac",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 4,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 4,
        "interlace_method": 1,
        "bytes_per_pixel": 4,
        "scanline_byte_length": 32,
        "filter_bpp": 4,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": false,
          "entry_count": 0
        },
        "transparency": {
          "present": false,
          "entry_count": 0
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 32,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:8d7fa0dfddf7968a1f05beecdb5599670c6c4cc693b9ab5f158d98e7059ae282"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 1,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 32,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:66b433a504f1da1ca8503dd38e3704f71df080e0d7a454f2cea95800cdd70feb"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:8d7fa0dfddf7968a1f05beecdb5599670c6c4cc693b9ab5f158d98e7059ae282",
          "sha256:66b433a504f1da1ca8503dd38e3704f71df080e0d7a454f2cea95800cdd70feb"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:8d7fa0dfddf7968a1f05beecdb5599670c6c4cc693b9ab5f158d98e7059ae282",
          "sha256:96d39e12b9e48c273162acf867afe1eecbfb9c68e9aad3af1af9a5ad55ba1a40"
        ],
        "after_dispose_hashes": [
          "sha256:8d7fa0dfddf7968a1f05beecdb5599670c6c4cc693b9ab5f158d98e7059ae282",
          "sha256:96d39e12b9e48c273162acf867afe1eecbfb9c68e9aad3af1af9a5ad55ba1a40"
        ],
        "final_canvas_hash": "sha256:96d39e12b9e48c273162acf867afe1eecbfb9c68e9aad3af1af9a5ad55ba1a40",
        "final_output_hash": "sha256:96d39e12b9e48c273162acf867afe1eecbfb9c68e9aad3af1af9a5ad55ba1a40"
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "truecolor_alpha16_adam7_over_fdat",
      "color_type": 6,
      "bit_depth": 16,
      "blend_op": 1,
      "interlace_method": 1,
      "png_file_name": "slip_lcd_seed_truecolor_alpha16_adam7_over_fdat.png",
      "png_hash": "sha256:68f5943d6a26a4f5f8f765926a9534dff2b76b57d00b54e852e08b3ec8cae2e2",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 6,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 6,
        "interlace_method": 1,
        "bytes_per_pixel": 8,
        "scanline_byte_length": 64,
        "filter_bpp": 8,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": false,
          "entry_count": 0
        },
        "transparency": {
          "present": false,
          "entry_count": 0
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 8,
                "filter_bpp": 8,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 8,
                "filter_bpp": 8,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 16,
                "filter_bpp": 8,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 16,
                "filter_bpp": 8,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 32,
                "filter_bpp": 8,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 32,
                "filter_bpp": 8,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 64,
                "filter_bpp": 8,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:a05934dcbed44d28e1cbf938ef18305421c1d62fedad6540e5c006a80ed7f79b"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 1,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 8,
                "filter_bpp": 8,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 8,
                "filter_bpp": 8,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 16,
                "filter_bpp": 8,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 16,
                "filter_bpp": 8,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 32,
                "filter_bpp": 8,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 32,
                "filter_bpp": 8,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 64,
                "filter_bpp": 8,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:f95383cecc60457f520065899c2cf9db6048371dec65e57bcee67cc097a052c7"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:a05934dcbed44d28e1cbf938ef18305421c1d62fedad6540e5c006a80ed7f79b",
          "sha256:f95383cecc60457f520065899c2cf9db6048371dec65e57bcee67cc097a052c7"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:a05934dcbed44d28e1cbf938ef18305421c1d62fedad6540e5c006a80ed7f79b",
          "sha256:2b4bda29fd8798cea02ad6de9240ad577c2db08ba729cbcd29fed6b473699c0e"
        ],
        "after_dispose_hashes": [
          "sha256:a05934dcbed44d28e1cbf938ef18305421c1d62fedad6540e5c006a80ed7f79b",
          "sha256:2b4bda29fd8798cea02ad6de9240ad577c2db08ba729cbcd29fed6b473699c0e"
        ],
        "final_canvas_hash": "sha256:2b4bda29fd8798cea02ad6de9240ad577c2db08ba729cbcd29fed6b473699c0e",
        "final_output_hash": "sha256:2b4bda29fd8798cea02ad6de9240ad577c2db08ba729cbcd29fed6b473699c0e"
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "rgba8_adam7_fdat",
      "color_type": 6,
      "bit_depth": 8,
      "blend_op": 0,
      "interlace_method": 1,
      "png_file_name": "slip_gray_stable_rgba8_adam7_fdat.png",
      "png_hash": "sha256:a08ddf4f5cf2e63e7a9ccff98239712befd27a0a4734b55b8693c3e6485460fc",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 8,
          "color_type": 6,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "interlace_method": 1,
        "bytes_per_pixel": 4,
        "scanline_byte_length": 32,
        "filter_bpp": 4,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": false,
          "entry_count": 0
        },
        "transparency": {
          "present": false,
          "entry_count": 0
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 32,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:379714cf07de62aed1cd54f21855ac6a3761f38b03a3324928918184225ecf68"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 32,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:ade18fc0349c9ae34a63015d3fdf458de2cfc6fc7344c7613ee00fd1f9f72cf7"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:379714cf07de62aed1cd54f21855ac6a3761f38b03a3324928918184225ecf68",
          "sha256:ade18fc0349c9ae34a63015d3fdf458de2cfc6fc7344c7613ee00fd1f9f72cf7"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:379714cf07de62aed1cd54f21855ac6a3761f38b03a3324928918184225ecf68",
          "sha256:ade18fc0349c9ae34a63015d3fdf458de2cfc6fc7344c7613ee00fd1f9f72cf7"
        ],
        "after_dispose_hashes": [
          "sha256:379714cf07de62aed1cd54f21855ac6a3761f38b03a3324928918184225ecf68",
          "sha256:ade18fc0349c9ae34a63015d3fdf458de2cfc6fc7344c7613ee00fd1f9f72cf7"
        ],
        "final_canvas_hash": "sha256:ade18fc0349c9ae34a63015d3fdf458de2cfc6fc7344c7613ee00fd1f9f72cf7",
        "final_output_hash": "sha256:ade18fc0349c9ae34a63015d3fdf458de2cfc6fc7344c7613ee00fd1f9f72cf7"
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "grayscale1_adam7_fdat",
      "color_type": 0,
      "bit_depth": 1,
      "blend_op": 0,
      "interlace_method": 1,
      "png_file_name": "slip_gray_stable_grayscale1_adam7_fdat.png",
      "png_hash": "sha256:7e1f224e3461e34b5ae81018f1ea49ea6e8f177189daace94da0e598c6885728",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 1,
          "color_type": 0,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 1,
        "color_type": 0,
        "interlace_method": 1,
        "bytes_per_pixel": 1,
        "scanline_byte_length": 1,
        "filter_bpp": 1,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": false,
          "entry_count": 0
        },
        "transparency": {
          "present": false,
          "entry_count": 0
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:640882b56ffa6a01ab835affd7334cecf4241ffddf44f3ca401621c56fc999f3"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:3381d61da875e55ede4597ca365709923701ee6c802267818cdb5383c282839d"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:640882b56ffa6a01ab835affd7334cecf4241ffddf44f3ca401621c56fc999f3",
          "sha256:3381d61da875e55ede4597ca365709923701ee6c802267818cdb5383c282839d"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:640882b56ffa6a01ab835affd7334cecf4241ffddf44f3ca401621c56fc999f3",
          "sha256:3381d61da875e55ede4597ca365709923701ee6c802267818cdb5383c282839d"
        ],
        "after_dispose_hashes": [
          "sha256:640882b56ffa6a01ab835affd7334cecf4241ffddf44f3ca401621c56fc999f3",
          "sha256:3381d61da875e55ede4597ca365709923701ee6c802267818cdb5383c282839d"
        ],
        "final_canvas_hash": "sha256:3381d61da875e55ede4597ca365709923701ee6c802267818cdb5383c282839d",
        "final_output_hash": "sha256:3381d61da875e55ede4597ca365709923701ee6c802267818cdb5383c282839d"
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "indexed4_adam7_trns_fdat",
      "color_type": 3,
      "bit_depth": 4,
      "blend_op": 0,
      "interlace_method": 1,
      "png_file_name": "slip_gray_stable_indexed4_adam7_trns_fdat.png",
      "png_hash": "sha256:8c17697368efc5c04d895d1706f81363198e6a19456fe6c2cbc803c89644860e",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 4,
          "color_type": 3,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 4,
        "color_type": 3,
        "interlace_method": 1,
        "bytes_per_pixel": 1,
        "scanline_byte_length": 4,
        "filter_bpp": 1,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": true,
          "entry_count": 16
        },
        "transparency": {
          "present": true,
          "entry_count": 16
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 2,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 2,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 4,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 6,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:d06cb1f160bf6f501faa1dc60b00718d50e39c33004f3c226d4b1daec39c653e"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 2,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 2,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 4,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 6,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:e3a3ef95c236f4bef30acab10b552491fa1b5c9aa6195e36f6b350dacc5ee90d"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:d06cb1f160bf6f501faa1dc60b00718d50e39c33004f3c226d4b1daec39c653e",
          "sha256:e3a3ef95c236f4bef30acab10b552491fa1b5c9aa6195e36f6b350dacc5ee90d"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:d06cb1f160bf6f501faa1dc60b00718d50e39c33004f3c226d4b1daec39c653e",
          "sha256:e3a3ef95c236f4bef30acab10b552491fa1b5c9aa6195e36f6b350dacc5ee90d"
        ],
        "after_dispose_hashes": [
          "sha256:d06cb1f160bf6f501faa1dc60b00718d50e39c33004f3c226d4b1daec39c653e",
          "sha256:e3a3ef95c236f4bef30acab10b552491fa1b5c9aa6195e36f6b350dacc5ee90d"
        ],
        "final_canvas_hash": "sha256:e3a3ef95c236f4bef30acab10b552491fa1b5c9aa6195e36f6b350dacc5ee90d",
        "final_output_hash": "sha256:e3a3ef95c236f4bef30acab10b552491fa1b5c9aa6195e36f6b350dacc5ee90d"
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "truecolor16_adam7_fdat",
      "color_type": 2,
      "bit_depth": 16,
      "blend_op": 0,
      "interlace_method": 1,
      "png_file_name": "slip_gray_stable_truecolor16_adam7_fdat.png",
      "png_hash": "sha256:d1975d30a96333dd07979e36bd83bd659944023d284fb89846028616b2ef52c0",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 2,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 2,
        "interlace_method": 1,
        "bytes_per_pixel": 6,
        "scanline_byte_length": 48,
        "filter_bpp": 6,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": false,
          "entry_count": 0
        },
        "transparency": {
          "present": false,
          "entry_count": 0
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 6,
                "filter_bpp": 6,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 6,
                "filter_bpp": 6,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 12,
                "filter_bpp": 6,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 12,
                "filter_bpp": 6,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 24,
                "filter_bpp": 6,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 24,
                "filter_bpp": 6,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 48,
                "filter_bpp": 6,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 6,
                "filter_bpp": 6,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 6,
                "filter_bpp": 6,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 12,
                "filter_bpp": 6,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 12,
                "filter_bpp": 6,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 24,
                "filter_bpp": 6,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 24,
                "filter_bpp": 6,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 48,
                "filter_bpp": 6,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:0b0afb8f56825d2102446068b211aa96611928dfbe2e6790ecc97fb48b248021"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:0b0afb8f56825d2102446068b211aa96611928dfbe2e6790ecc97fb48b248021"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:0b0afb8f56825d2102446068b211aa96611928dfbe2e6790ecc97fb48b248021"
        ],
        "after_dispose_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:0b0afb8f56825d2102446068b211aa96611928dfbe2e6790ecc97fb48b248021"
        ],
        "final_canvas_hash": "sha256:0b0afb8f56825d2102446068b211aa96611928dfbe2e6790ecc97fb48b248021",
        "final_output_hash": "sha256:0b0afb8f56825d2102446068b211aa96611928dfbe2e6790ecc97fb48b248021"
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "grayscale_alpha16_adam7_over_fdat",
      "color_type": 4,
      "bit_depth": 16,
      "blend_op": 1,
      "interlace_method": 1,
      "png_file_name": "slip_gray_stable_grayscale_alpha16_adam7_over_fdat.png",
      "png_hash": "sha256:7ec5f69f24b189c2aaae57c9a0456baeb65469ca024c5c38b7dcd98af240545b",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 4,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 4,
        "interlace_method": 1,
        "bytes_per_pixel": 4,
        "scanline_byte_length": 32,
        "filter_bpp": 4,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": false,
          "entry_count": 0
        },
        "transparency": {
          "present": false,
          "entry_count": 0
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 32,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:eb764661995399f3ff2e1088700d5f6054866fab56027598b066593697b3576f"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 1,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 32,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:65ee8addbe10d63eeeb112d8e85c606ce6e0f63fc2c71afc5ac7fec7f93b71a0"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:eb764661995399f3ff2e1088700d5f6054866fab56027598b066593697b3576f",
          "sha256:65ee8addbe10d63eeeb112d8e85c606ce6e0f63fc2c71afc5ac7fec7f93b71a0"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:eb764661995399f3ff2e1088700d5f6054866fab56027598b066593697b3576f",
          "sha256:62c81663a6a61a82fe1754eb13e5f912b68cce832ddbd89e5c7ee2a5560d300a"
        ],
        "after_dispose_hashes": [
          "sha256:eb764661995399f3ff2e1088700d5f6054866fab56027598b066593697b3576f",
          "sha256:62c81663a6a61a82fe1754eb13e5f912b68cce832ddbd89e5c7ee2a5560d300a"
        ],
        "final_canvas_hash": "sha256:62c81663a6a61a82fe1754eb13e5f912b68cce832ddbd89e5c7ee2a5560d300a",
        "final_output_hash": "sha256:62c81663a6a61a82fe1754eb13e5f912b68cce832ddbd89e5c7ee2a5560d300a"
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "truecolor_alpha16_adam7_over_fdat",
      "color_type": 6,
      "bit_depth": 16,
      "blend_op": 1,
      "interlace_method": 1,
      "png_file_name": "slip_gray_stable_truecolor_alpha16_adam7_over_fdat.png",
      "png_hash": "sha256:e7c4796d065fa95844fc0ef7b5bd986ad6d8feb03e3f5cd710a9347ac241c8e4",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 6,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 6,
        "interlace_method": 1,
        "bytes_per_pixel": 8,
        "scanline_byte_length": 64,
        "filter_bpp": 8,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": false,
          "entry_count": 0
        },
        "transparency": {
          "present": false,
          "entry_count": 0
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 8,
                "filter_bpp": 8,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 8,
                "filter_bpp": 8,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 16,
                "filter_bpp": 8,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 16,
                "filter_bpp": 8,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 32,
                "filter_bpp": 8,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 32,
                "filter_bpp": 8,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 64,
                "filter_bpp": 8,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:379714cf07de62aed1cd54f21855ac6a3761f38b03a3324928918184225ecf68"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 1,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 8,
                "filter_bpp": 8,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 8,
                "filter_bpp": 8,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 16,
                "filter_bpp": 8,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 16,
                "filter_bpp": 8,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 32,
                "filter_bpp": 8,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 32,
                "filter_bpp": 8,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 64,
                "filter_bpp": 8,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:ade18fc0349c9ae34a63015d3fdf458de2cfc6fc7344c7613ee00fd1f9f72cf7"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:379714cf07de62aed1cd54f21855ac6a3761f38b03a3324928918184225ecf68",
          "sha256:ade18fc0349c9ae34a63015d3fdf458de2cfc6fc7344c7613ee00fd1f9f72cf7"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:379714cf07de62aed1cd54f21855ac6a3761f38b03a3324928918184225ecf68",
          "sha256:b1fb0817577d9c1cd4896c5cb6d2caf1e60a59b7d87b551ebb744621fe8ea811"
        ],
        "after_dispose_hashes": [
          "sha256:379714cf07de62aed1cd54f21855ac6a3761f38b03a3324928918184225ecf68",
          "sha256:b1fb0817577d9c1cd4896c5cb6d2caf1e60a59b7d87b551ebb744621fe8ea811"
        ],
        "final_canvas_hash": "sha256:b1fb0817577d9c1cd4896c5cb6d2caf1e60a59b7d87b551ebb744621fe8ea811",
        "final_output_hash": "sha256:b1fb0817577d9c1cd4896c5cb6d2caf1e60a59b7d87b551ebb744621fe8ea811"
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "rgba8_adam7_fdat",
      "color_type": 6,
      "bit_depth": 8,
      "blend_op": 0,
      "interlace_method": 1,
      "png_file_name": "slip_amber_social_rgba8_adam7_fdat.png",
      "png_hash": "sha256:25762d642c3b8de7e155d0aca97e8c971699e797a028917218fa8dbfec662ce6",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 8,
          "color_type": 6,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "interlace_method": 1,
        "bytes_per_pixel": 4,
        "scanline_byte_length": 32,
        "filter_bpp": 4,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": false,
          "entry_count": 0
        },
        "transparency": {
          "present": false,
          "entry_count": 0
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 32,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:a50eb115b304e7c79e820bdf2d0839f104a9e4c3166758dd87a7747c2598a1aa"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 32,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:a97d1f4377dd6b9cf40fa26ec429632a04877501f9e4a52fdb2a027c8e1e64c6"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:a50eb115b304e7c79e820bdf2d0839f104a9e4c3166758dd87a7747c2598a1aa",
          "sha256:a97d1f4377dd6b9cf40fa26ec429632a04877501f9e4a52fdb2a027c8e1e64c6"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:a50eb115b304e7c79e820bdf2d0839f104a9e4c3166758dd87a7747c2598a1aa",
          "sha256:a97d1f4377dd6b9cf40fa26ec429632a04877501f9e4a52fdb2a027c8e1e64c6"
        ],
        "after_dispose_hashes": [
          "sha256:a50eb115b304e7c79e820bdf2d0839f104a9e4c3166758dd87a7747c2598a1aa",
          "sha256:a97d1f4377dd6b9cf40fa26ec429632a04877501f9e4a52fdb2a027c8e1e64c6"
        ],
        "final_canvas_hash": "sha256:a97d1f4377dd6b9cf40fa26ec429632a04877501f9e4a52fdb2a027c8e1e64c6",
        "final_output_hash": "sha256:a97d1f4377dd6b9cf40fa26ec429632a04877501f9e4a52fdb2a027c8e1e64c6"
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "grayscale1_adam7_fdat",
      "color_type": 0,
      "bit_depth": 1,
      "blend_op": 0,
      "interlace_method": 1,
      "png_file_name": "slip_amber_social_grayscale1_adam7_fdat.png",
      "png_hash": "sha256:e63915b256882a12662056202df156f3a180398940fc85e4e54bfa95f45f2185",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 1,
          "color_type": 0,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 1,
        "color_type": 0,
        "interlace_method": 1,
        "bytes_per_pixel": 1,
        "scanline_byte_length": 1,
        "filter_bpp": 1,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": false,
          "entry_count": 0
        },
        "transparency": {
          "present": false,
          "entry_count": 0
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:ff30b79b6c1a05043b92ecbc6b2ae71567b6dd457ff1b4e6a12cecab32a3eb46"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:aba7c9de6cfca3d3b8e16ef7e8d0c19dc16d98e0c26369267126d35ad4233ac4"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:ff30b79b6c1a05043b92ecbc6b2ae71567b6dd457ff1b4e6a12cecab32a3eb46",
          "sha256:aba7c9de6cfca3d3b8e16ef7e8d0c19dc16d98e0c26369267126d35ad4233ac4"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:ff30b79b6c1a05043b92ecbc6b2ae71567b6dd457ff1b4e6a12cecab32a3eb46",
          "sha256:aba7c9de6cfca3d3b8e16ef7e8d0c19dc16d98e0c26369267126d35ad4233ac4"
        ],
        "after_dispose_hashes": [
          "sha256:ff30b79b6c1a05043b92ecbc6b2ae71567b6dd457ff1b4e6a12cecab32a3eb46",
          "sha256:aba7c9de6cfca3d3b8e16ef7e8d0c19dc16d98e0c26369267126d35ad4233ac4"
        ],
        "final_canvas_hash": "sha256:aba7c9de6cfca3d3b8e16ef7e8d0c19dc16d98e0c26369267126d35ad4233ac4",
        "final_output_hash": "sha256:aba7c9de6cfca3d3b8e16ef7e8d0c19dc16d98e0c26369267126d35ad4233ac4"
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "indexed4_adam7_trns_fdat",
      "color_type": 3,
      "bit_depth": 4,
      "blend_op": 0,
      "interlace_method": 1,
      "png_file_name": "slip_amber_social_indexed4_adam7_trns_fdat.png",
      "png_hash": "sha256:e9bfaf780ca0fcd742252f5b4ccff9b1feb06c7d966b010e8f2073023823d867",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 4,
          "color_type": 3,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 4,
        "color_type": 3,
        "interlace_method": 1,
        "bytes_per_pixel": 1,
        "scanline_byte_length": 4,
        "filter_bpp": 1,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": true,
          "entry_count": 16
        },
        "transparency": {
          "present": true,
          "entry_count": 16
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 2,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 2,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 4,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 6,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:05abc4b97632c187bb33b9b5d5f3d864e6ded5c60cbbb2f95a7e3e5069aac740"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 1,
                "filter_bpp": 1,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 2,
                "filter_bpp": 1,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 2,
                "filter_bpp": 1,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 4,
                "filter_bpp": 1,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 6,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:7931ee6076f8429df88969300b1c1e744a903b1e0e202c9b7c590f21e11d6113"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:05abc4b97632c187bb33b9b5d5f3d864e6ded5c60cbbb2f95a7e3e5069aac740",
          "sha256:7931ee6076f8429df88969300b1c1e744a903b1e0e202c9b7c590f21e11d6113"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:05abc4b97632c187bb33b9b5d5f3d864e6ded5c60cbbb2f95a7e3e5069aac740",
          "sha256:7931ee6076f8429df88969300b1c1e744a903b1e0e202c9b7c590f21e11d6113"
        ],
        "after_dispose_hashes": [
          "sha256:05abc4b97632c187bb33b9b5d5f3d864e6ded5c60cbbb2f95a7e3e5069aac740",
          "sha256:7931ee6076f8429df88969300b1c1e744a903b1e0e202c9b7c590f21e11d6113"
        ],
        "final_canvas_hash": "sha256:7931ee6076f8429df88969300b1c1e744a903b1e0e202c9b7c590f21e11d6113",
        "final_output_hash": "sha256:7931ee6076f8429df88969300b1c1e744a903b1e0e202c9b7c590f21e11d6113"
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "truecolor16_adam7_fdat",
      "color_type": 2,
      "bit_depth": 16,
      "blend_op": 0,
      "interlace_method": 1,
      "png_file_name": "slip_amber_social_truecolor16_adam7_fdat.png",
      "png_hash": "sha256:cc3eb3f8c11499b0a5784671469e8415b7f2317a317529646bf8e7b3f4df3925",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 2,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 2,
        "interlace_method": 1,
        "bytes_per_pixel": 6,
        "scanline_byte_length": 48,
        "filter_bpp": 6,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": false,
          "entry_count": 0
        },
        "transparency": {
          "present": false,
          "entry_count": 0
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 6,
                "filter_bpp": 6,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 6,
                "filter_bpp": 6,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 12,
                "filter_bpp": 6,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 12,
                "filter_bpp": 6,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 24,
                "filter_bpp": 6,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 24,
                "filter_bpp": 6,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 48,
                "filter_bpp": 6,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 6,
                "filter_bpp": 6,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 6,
                "filter_bpp": 6,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 12,
                "filter_bpp": 6,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 12,
                "filter_bpp": 6,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 24,
                "filter_bpp": 6,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 24,
                "filter_bpp": 6,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 48,
                "filter_bpp": 6,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:48418c4b3721c5432c97709f6228e4ad0d1389433a6249d5e5f427dde9ca781b"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:48418c4b3721c5432c97709f6228e4ad0d1389433a6249d5e5f427dde9ca781b"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:48418c4b3721c5432c97709f6228e4ad0d1389433a6249d5e5f427dde9ca781b"
        ],
        "after_dispose_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:48418c4b3721c5432c97709f6228e4ad0d1389433a6249d5e5f427dde9ca781b"
        ],
        "final_canvas_hash": "sha256:48418c4b3721c5432c97709f6228e4ad0d1389433a6249d5e5f427dde9ca781b",
        "final_output_hash": "sha256:48418c4b3721c5432c97709f6228e4ad0d1389433a6249d5e5f427dde9ca781b"
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "grayscale_alpha16_adam7_over_fdat",
      "color_type": 4,
      "bit_depth": 16,
      "blend_op": 1,
      "interlace_method": 1,
      "png_file_name": "slip_amber_social_grayscale_alpha16_adam7_over_fdat.png",
      "png_hash": "sha256:55837662926ab143abc61c06d72ea56b87e067c55276ad8b65b76aa7f20da6d9",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 4,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 4,
        "interlace_method": 1,
        "bytes_per_pixel": 4,
        "scanline_byte_length": 32,
        "filter_bpp": 4,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": false,
          "entry_count": 0
        },
        "transparency": {
          "present": false,
          "entry_count": 0
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 32,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:b52078c12ad2034345e53e4510d26fa18b9dc704ad1f4bc2d4eff33682be9db6"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 1,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 4,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 8,
                "filter_bpp": 4,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 16,
                "filter_bpp": 4,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 32,
                "filter_bpp": 4,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:87e074454fbd03d0401b5c972a779e4adcb06a4ee9e3e429dfc8bcfe724a91a5"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:b52078c12ad2034345e53e4510d26fa18b9dc704ad1f4bc2d4eff33682be9db6",
          "sha256:87e074454fbd03d0401b5c972a779e4adcb06a4ee9e3e429dfc8bcfe724a91a5"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:b52078c12ad2034345e53e4510d26fa18b9dc704ad1f4bc2d4eff33682be9db6",
          "sha256:7c99b98506ab45b0b07171c27df21d632e58fe7ec06d6dd50a5941174264ab7e"
        ],
        "after_dispose_hashes": [
          "sha256:b52078c12ad2034345e53e4510d26fa18b9dc704ad1f4bc2d4eff33682be9db6",
          "sha256:7c99b98506ab45b0b07171c27df21d632e58fe7ec06d6dd50a5941174264ab7e"
        ],
        "final_canvas_hash": "sha256:7c99b98506ab45b0b07171c27df21d632e58fe7ec06d6dd50a5941174264ab7e",
        "final_output_hash": "sha256:7c99b98506ab45b0b07171c27df21d632e58fe7ec06d6dd50a5941174264ab7e"
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "truecolor_alpha16_adam7_over_fdat",
      "color_type": 6,
      "bit_depth": 16,
      "blend_op": 1,
      "interlace_method": 1,
      "png_file_name": "slip_amber_social_truecolor_alpha16_adam7_over_fdat.png",
      "png_hash": "sha256:6981372faff9bdd23077026c6539a048a49259b2ad37d002b4b5076598cf6d8f",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 6,
          "compression": 0,
          "filter_method": 0,
          "interlace": 1
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 6,
        "interlace_method": 1,
        "bytes_per_pixel": 8,
        "scanline_byte_length": 64,
        "filter_bpp": 8,
        "pass_order": [
          1,
          2,
          3,
          4,
          5,
          6,
          7
        ],
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "palette": {
          "present": false,
          "entry_count": 0
        },
        "transparency": {
          "present": false,
          "entry_count": 0
        },
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
        "sequence_numbers": [
          0,
          1,
          2,
          3
        ],
        "frames": [
          {
            "frame_index": 0,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 5,
            "delay_ms": 200,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "IDAT",
            "fdat_chunk_count": 0,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 8,
                "filter_bpp": 8,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 8,
                "filter_bpp": 8,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 16,
                "filter_bpp": 8,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 16,
                "filter_bpp": 8,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 32,
                "filter_bpp": 8,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 32,
                "filter_bpp": 8,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 64,
                "filter_bpp": 8,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:a50eb115b304e7c79e820bdf2d0839f104a9e4c3166758dd87a7747c2598a1aa"
          },
          {
            "frame_index": 1,
            "width": 8,
            "height": 8,
            "x_offset": 0,
            "y_offset": 0,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 1,
            "data_source": "fdAT",
            "fdat_chunk_count": 2,
            "filter_types_seen": [
              0,
              1,
              2,
              3,
              4
            ],
            "pass_order": [
              1,
              2,
              3,
              4,
              5,
              6,
              7
            ],
            "pass_summaries": [
              {
                "pass_index": 1,
                "x_start": 0,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 8,
                "filter_bpp": 8,
                "filter_types_seen": [
                  0
                ]
              },
              {
                "pass_index": 2,
                "x_start": 4,
                "y_start": 0,
                "x_step": 8,
                "y_step": 8,
                "width": 1,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 1,
                "scanline_byte_length": 8,
                "filter_bpp": 8,
                "filter_types_seen": [
                  1
                ]
              },
              {
                "pass_index": 3,
                "x_start": 0,
                "y_start": 4,
                "x_step": 4,
                "y_step": 8,
                "width": 2,
                "height": 1,
                "scanline_count": 1,
                "pixel_count": 2,
                "scanline_byte_length": 16,
                "filter_bpp": 8,
                "filter_types_seen": [
                  2
                ]
              },
              {
                "pass_index": 4,
                "x_start": 2,
                "y_start": 0,
                "x_step": 4,
                "y_step": 4,
                "width": 2,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 4,
                "scanline_byte_length": 16,
                "filter_bpp": 8,
                "filter_types_seen": [
                  3,
                  4
                ]
              },
              {
                "pass_index": 5,
                "x_start": 0,
                "y_start": 2,
                "x_step": 2,
                "y_step": 4,
                "width": 4,
                "height": 2,
                "scanline_count": 2,
                "pixel_count": 8,
                "scanline_byte_length": 32,
                "filter_bpp": 8,
                "filter_types_seen": [
                  0,
                  1
                ]
              },
              {
                "pass_index": 6,
                "x_start": 1,
                "y_start": 0,
                "x_step": 2,
                "y_step": 2,
                "width": 4,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 16,
                "scanline_byte_length": 32,
                "filter_bpp": 8,
                "filter_types_seen": [
                  2,
                  3,
                  4,
                  0
                ]
              },
              {
                "pass_index": 7,
                "x_start": 0,
                "y_start": 1,
                "x_step": 1,
                "y_step": 2,
                "width": 8,
                "height": 4,
                "scanline_count": 4,
                "pixel_count": 32,
                "scanline_byte_length": 64,
                "filter_bpp": 8,
                "filter_types_seen": [
                  1,
                  2,
                  3,
                  4
                ]
              }
            ],
            "non_empty_pass_count": 7,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:a97d1f4377dd6b9cf40fa26ec429632a04877501f9e4a52fdb2a027c8e1e64c6"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:a50eb115b304e7c79e820bdf2d0839f104a9e4c3166758dd87a7747c2598a1aa",
          "sha256:a97d1f4377dd6b9cf40fa26ec429632a04877501f9e4a52fdb2a027c8e1e64c6"
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:a50eb115b304e7c79e820bdf2d0839f104a9e4c3166758dd87a7747c2598a1aa",
          "sha256:cab82dc7e9e2a4694b207892a9be96a593a9b34955a42231f960931ee939d039"
        ],
        "after_dispose_hashes": [
          "sha256:a50eb115b304e7c79e820bdf2d0839f104a9e4c3166758dd87a7747c2598a1aa",
          "sha256:cab82dc7e9e2a4694b207892a9be96a593a9b34955a42231f960931ee939d039"
        ],
        "final_canvas_hash": "sha256:cab82dc7e9e2a4694b207892a9be96a593a9b34955a42231f960931ee939d039",
        "final_output_hash": "sha256:cab82dc7e9e2a4694b207892a9be96a593a9b34955a42231f960931ee939d039"
      },
      "success": true
    }
  ],
  "invalid_probe_results": [
    {
      "probe_id": "non_adam7_interlace",
      "expected_family": "apng_adam7_interlace_required",
      "rejected": true,
      "decoded": {
        "ok": false,
        "errors": [
          {
            "path": "apng.adam7_frame_data",
            "family": "apng_adam7_interlace_required",
            "message": "Stage 0 APNG Adam7 frame-data matrix requires interlace method 1"
          }
        ],
        "error_families": [
          "apng_adam7_interlace_required"
        ],
        "error_family": "apng_adam7_interlace_required"
      }
    },
    {
      "probe_id": "invalid_bit_depth_color_type",
      "expected_family": "png_bit_depth_color_type_invalid",
      "rejected": true,
      "decoded": {
        "ok": false,
        "errors": [
          {
            "path": "apng.adam7_frame_data",
            "family": "png_bit_depth_color_type_invalid",
            "message": "PNG bit depth is not allowed for this APNG Adam7 lab color type"
          }
        ],
        "error_families": [
          "png_bit_depth_color_type_invalid"
        ],
        "error_family": "png_bit_depth_color_type_invalid"
      }
    },
    {
      "probe_id": "truncated_adam7_scanline",
      "expected_family": "apng_adam7_scanline_length_mismatch",
      "rejected": true,
      "decoded": {
        "ok": false,
        "errors": [
          {
            "path": "apng.adam7_frame_data",
            "family": "apng_adam7_scanline_length_mismatch",
            "message": "Adam7 reduced-image scanline data ended early"
          }
        ],
        "error_families": [
          "apng_adam7_scanline_length_mismatch"
        ],
        "error_family": "apng_adam7_scanline_length_mismatch"
      }
    },
    {
      "probe_id": "invalid_filter_type",
      "expected_family": "png_filter_type_unsupported",
      "rejected": true,
      "decoded": {
        "ok": false,
        "errors": [
          {
            "path": "apng.adam7_frame_data",
            "family": "png_filter_type_unsupported",
            "message": "PNG filter type must be in 0..4 for filter method 0"
          }
        ],
        "error_families": [
          "png_filter_type_unsupported"
        ],
        "error_family": "png_filter_type_unsupported"
      }
    },
    {
      "probe_id": "fdat_sequence_gap",
      "expected_family": "apng_sequence_number_invalid",
      "rejected": true,
      "decoded": {
        "ok": false,
        "errors": [
          {
            "path": "apng.adam7_frame_data",
            "family": "apng_sequence_number_invalid",
            "message": "APNG sequence numbers must be consecutive"
          }
        ],
        "error_families": [
          "apng_sequence_number_invalid"
        ],
        "error_family": "apng_sequence_number_invalid"
      }
    }
  ]
};
