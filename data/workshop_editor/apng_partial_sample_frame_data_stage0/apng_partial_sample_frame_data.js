window.MECHAGOTCHI_APNG_PARTIAL_SAMPLE_FRAME_DATA = {
  "report": {
    "artifact_id": "apng_partial_sample_frame_data_stage0",
    "status": "research_apng_partial_sample_frame_data_no_package_code",
    "profile_count": 3,
    "case_family_ids": [
      "grayscale1_source_patch",
      "indexed4_trns_source_patch",
      "truecolor16_source_patch",
      "grayscale_alpha16_over_patch",
      "truecolor_alpha16_over_patch"
    ],
    "case_ids": [
      "slip_lcd_seed_grayscale1_source_patch",
      "slip_lcd_seed_indexed4_trns_source_patch",
      "slip_lcd_seed_truecolor16_source_patch",
      "slip_lcd_seed_grayscale_alpha16_over_patch",
      "slip_lcd_seed_truecolor_alpha16_over_patch",
      "slip_gray_stable_grayscale1_source_patch",
      "slip_gray_stable_indexed4_trns_source_patch",
      "slip_gray_stable_truecolor16_source_patch",
      "slip_gray_stable_grayscale_alpha16_over_patch",
      "slip_gray_stable_truecolor_alpha16_over_patch",
      "slip_amber_social_grayscale1_source_patch",
      "slip_amber_social_indexed4_trns_source_patch",
      "slip_amber_social_truecolor16_source_patch",
      "slip_amber_social_grayscale_alpha16_over_patch",
      "slip_amber_social_truecolor_alpha16_over_patch"
    ],
    "case_count": 15,
    "case_success_count": 15,
    "invalid_probe_count": 5,
    "invalid_probe_rejected_count": 5,
    "metrics": {
      "case_success_ratio": 1.0,
      "invalid_probe_rejection_ratio": 1.0,
      "profile_coverage": 3,
      "case_family_count": 5,
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
        16
      ],
      "supported_filter_types": [
        0,
        1,
        2,
        3,
        4
      ],
      "partial_frame_case_count": 15,
      "over_blend_case_count": 6,
      "split_fdat_frame_count": 15
    },
    "closed_states": [
      "apng_partial_sample_offset_reconstruction",
      "apng_partial_low_bit_region_reconstruction",
      "apng_partial_16bit_region_reconstruction",
      "apng_partial_alpha_over_sample_reconstruction",
      "apng_partial_sample_invalid_probe_rejection"
    ],
    "blocked_states": [
      "full_apng_png_conformance",
      "live_external_editor_rewrite_validation",
      "production_import_export_carrier_selection_final_decision",
      "manual_readability_calibration",
      "package_runtime_lifecycle_integration"
    ],
    "decision": "prototype_apng_partial_sample_frame_data_subset"
  },
  "case_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "slip_lcd_seed_grayscale1_source_patch",
      "case_family_id": "grayscale1_source_patch",
      "color_type": 0,
      "bit_depth": 1,
      "blend_op": 0,
      "png_file_name": "slip_lcd_seed_grayscale1_source_patch.png",
      "png_hash": "sha256:96631e456aa8d706be04530902b0520527a2ddcf6606d537214c016b87fdc8dd",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 1,
          "color_type": 0,
          "compression": 0,
          "filter_method": 0,
          "interlace": 0
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 1,
        "color_type": 0,
        "bytes_per_pixel": 1,
        "scanline_byte_length": 1,
        "filter_bpp": 1,
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
            "scanline_byte_length": 1,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:a181f8ad524efbdabfaf736729e6183573f716c939ada4c4ba453bfafaae498b"
          },
          {
            "frame_index": 1,
            "width": 4,
            "height": 5,
            "x_offset": 2,
            "y_offset": 1,
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
            "scanline_byte_length": 1,
            "pixel_count": 20,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": false,
            "pixel_hash": "sha256:5f8d033b19c30e5bea59de2ca02740a677fcddf42b91414bd6cda1548a5ae808"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:a181f8ad524efbdabfaf736729e6183573f716c939ada4c4ba453bfafaae498b",
          "sha256:5f8d033b19c30e5bea59de2ca02740a677fcddf42b91414bd6cda1548a5ae808"
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
          "sha256:eacc222584f2a683adf99b73f0f33ee62ffe90122269e8e4da03f5f8d03f3532"
        ],
        "after_dispose_hashes": [
          "sha256:a181f8ad524efbdabfaf736729e6183573f716c939ada4c4ba453bfafaae498b",
          "sha256:eacc222584f2a683adf99b73f0f33ee62ffe90122269e8e4da03f5f8d03f3532"
        ],
        "final_canvas_hash": "sha256:eacc222584f2a683adf99b73f0f33ee62ffe90122269e8e4da03f5f8d03f3532",
        "final_output_hash": "sha256:eacc222584f2a683adf99b73f0f33ee62ffe90122269e8e4da03f5f8d03f3532"
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "slip_lcd_seed_indexed4_trns_source_patch",
      "case_family_id": "indexed4_trns_source_patch",
      "color_type": 3,
      "bit_depth": 4,
      "blend_op": 0,
      "png_file_name": "slip_lcd_seed_indexed4_trns_source_patch.png",
      "png_hash": "sha256:884749531549a2be70e2830ebee3ce0fa72e09f786b262aa64101671e12c7ef4",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 4,
          "color_type": 3,
          "compression": 0,
          "filter_method": 0,
          "interlace": 0
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 4,
        "color_type": 3,
        "bytes_per_pixel": 1,
        "scanline_byte_length": 4,
        "filter_bpp": 1,
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
            "scanline_byte_length": 4,
            "pixel_count": 64,
            "transparent_pixel_count": 6,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:22592babf8e16ecbf682cd916eae27effa210d6463ea1d8f5ef299242be16744"
          },
          {
            "frame_index": 1,
            "width": 4,
            "height": 5,
            "x_offset": 2,
            "y_offset": 1,
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
            "scanline_byte_length": 2,
            "pixel_count": 20,
            "transparent_pixel_count": 2,
            "partial_alpha_pixel_count": 0,
            "full_canvas": false,
            "pixel_hash": "sha256:a4ef3ca4a34f60f4227f1602e09b42df5514762bfc3631c846efcbea290964b5"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:22592babf8e16ecbf682cd916eae27effa210d6463ea1d8f5ef299242be16744",
          "sha256:a4ef3ca4a34f60f4227f1602e09b42df5514762bfc3631c846efcbea290964b5"
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
          "sha256:bddb9491fe71264a90e330521daffb0e67b38149f0f9e066d8260c616c6fe9ab"
        ],
        "after_dispose_hashes": [
          "sha256:22592babf8e16ecbf682cd916eae27effa210d6463ea1d8f5ef299242be16744",
          "sha256:bddb9491fe71264a90e330521daffb0e67b38149f0f9e066d8260c616c6fe9ab"
        ],
        "final_canvas_hash": "sha256:bddb9491fe71264a90e330521daffb0e67b38149f0f9e066d8260c616c6fe9ab",
        "final_output_hash": "sha256:bddb9491fe71264a90e330521daffb0e67b38149f0f9e066d8260c616c6fe9ab"
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "slip_lcd_seed_truecolor16_source_patch",
      "case_family_id": "truecolor16_source_patch",
      "color_type": 2,
      "bit_depth": 16,
      "blend_op": 0,
      "png_file_name": "slip_lcd_seed_truecolor16_source_patch.png",
      "png_hash": "sha256:8b748bf2a4321b662284b8c8397f78a40e13c14f3edf971e0015617f3d9f73a3",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 2,
          "compression": 0,
          "filter_method": 0,
          "interlace": 0
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 2,
        "bytes_per_pixel": 6,
        "scanline_byte_length": 48,
        "filter_bpp": 6,
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
            "scanline_byte_length": 48,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417"
          },
          {
            "frame_index": 1,
            "width": 4,
            "height": 5,
            "x_offset": 2,
            "y_offset": 1,
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
            "scanline_byte_length": 24,
            "pixel_count": 20,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": false,
            "pixel_hash": "sha256:472413df27dab7f200270dd76e546f9e0276efafd5602a133da3ee813ec520fc"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:472413df27dab7f200270dd76e546f9e0276efafd5602a133da3ee813ec520fc"
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
          "sha256:8ed7018a07287a610a7e6eb6719b2c465dd7d010563905ad13e835fdb68bc901"
        ],
        "after_dispose_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:8ed7018a07287a610a7e6eb6719b2c465dd7d010563905ad13e835fdb68bc901"
        ],
        "final_canvas_hash": "sha256:8ed7018a07287a610a7e6eb6719b2c465dd7d010563905ad13e835fdb68bc901",
        "final_output_hash": "sha256:8ed7018a07287a610a7e6eb6719b2c465dd7d010563905ad13e835fdb68bc901"
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "slip_lcd_seed_grayscale_alpha16_over_patch",
      "case_family_id": "grayscale_alpha16_over_patch",
      "color_type": 4,
      "bit_depth": 16,
      "blend_op": 1,
      "png_file_name": "slip_lcd_seed_grayscale_alpha16_over_patch.png",
      "png_hash": "sha256:d0ae715b4290614d32d92b00f901b9334658f2c70a68b5af7a33d6d0b62e76b2",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 4,
          "compression": 0,
          "filter_method": 0,
          "interlace": 0
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 4,
        "bytes_per_pixel": 4,
        "scanline_byte_length": 32,
        "filter_bpp": 4,
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
            "scanline_byte_length": 32,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:8d7fa0dfddf7968a1f05beecdb5599670c6c4cc693b9ab5f158d98e7059ae282"
          },
          {
            "frame_index": 1,
            "width": 4,
            "height": 5,
            "x_offset": 2,
            "y_offset": 1,
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
            "scanline_byte_length": 16,
            "pixel_count": 20,
            "transparent_pixel_count": 2,
            "partial_alpha_pixel_count": 18,
            "full_canvas": false,
            "pixel_hash": "sha256:a3508287e0fe8c45a29d50eb961e421513fe9c4d2c4a03ebbdf754590336a00b"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:8d7fa0dfddf7968a1f05beecdb5599670c6c4cc693b9ab5f158d98e7059ae282",
          "sha256:a3508287e0fe8c45a29d50eb961e421513fe9c4d2c4a03ebbdf754590336a00b"
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
          "sha256:b783719e0e2d8958c7fa300fa31654cef1da143c0999a87864acbc0de0d5a3ab"
        ],
        "after_dispose_hashes": [
          "sha256:8d7fa0dfddf7968a1f05beecdb5599670c6c4cc693b9ab5f158d98e7059ae282",
          "sha256:b783719e0e2d8958c7fa300fa31654cef1da143c0999a87864acbc0de0d5a3ab"
        ],
        "final_canvas_hash": "sha256:b783719e0e2d8958c7fa300fa31654cef1da143c0999a87864acbc0de0d5a3ab",
        "final_output_hash": "sha256:b783719e0e2d8958c7fa300fa31654cef1da143c0999a87864acbc0de0d5a3ab"
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "slip_lcd_seed_truecolor_alpha16_over_patch",
      "case_family_id": "truecolor_alpha16_over_patch",
      "color_type": 6,
      "bit_depth": 16,
      "blend_op": 1,
      "png_file_name": "slip_lcd_seed_truecolor_alpha16_over_patch.png",
      "png_hash": "sha256:cea5d07c459b891b5086c977663f88110cd0c976f232e221e8ce1ac52cf7b1d3",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 6,
          "compression": 0,
          "filter_method": 0,
          "interlace": 0
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 6,
        "bytes_per_pixel": 8,
        "scanline_byte_length": 64,
        "filter_bpp": 8,
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
            "scanline_byte_length": 64,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:a05934dcbed44d28e1cbf938ef18305421c1d62fedad6540e5c006a80ed7f79b"
          },
          {
            "frame_index": 1,
            "width": 4,
            "height": 5,
            "x_offset": 2,
            "y_offset": 1,
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
            "scanline_byte_length": 32,
            "pixel_count": 20,
            "transparent_pixel_count": 2,
            "partial_alpha_pixel_count": 18,
            "full_canvas": false,
            "pixel_hash": "sha256:340feadf1458ab861b4335e56e7a051ef53f3b5e714aadcf7e7748e1aa38c83c"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:a05934dcbed44d28e1cbf938ef18305421c1d62fedad6540e5c006a80ed7f79b",
          "sha256:340feadf1458ab861b4335e56e7a051ef53f3b5e714aadcf7e7748e1aa38c83c"
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
          "sha256:8899e314024d8e302d60b252c4a2caa9ddb107d8251f17aac08e75971ea12014"
        ],
        "after_dispose_hashes": [
          "sha256:a05934dcbed44d28e1cbf938ef18305421c1d62fedad6540e5c006a80ed7f79b",
          "sha256:8899e314024d8e302d60b252c4a2caa9ddb107d8251f17aac08e75971ea12014"
        ],
        "final_canvas_hash": "sha256:8899e314024d8e302d60b252c4a2caa9ddb107d8251f17aac08e75971ea12014",
        "final_output_hash": "sha256:8899e314024d8e302d60b252c4a2caa9ddb107d8251f17aac08e75971ea12014"
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "slip_gray_stable_grayscale1_source_patch",
      "case_family_id": "grayscale1_source_patch",
      "color_type": 0,
      "bit_depth": 1,
      "blend_op": 0,
      "png_file_name": "slip_gray_stable_grayscale1_source_patch.png",
      "png_hash": "sha256:d0f311b934962d091c57784bf9ffc1786e051a7d7172932845cb489419b13b3c",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 1,
          "color_type": 0,
          "compression": 0,
          "filter_method": 0,
          "interlace": 0
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 1,
        "color_type": 0,
        "bytes_per_pixel": 1,
        "scanline_byte_length": 1,
        "filter_bpp": 1,
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
            "scanline_byte_length": 1,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:640882b56ffa6a01ab835affd7334cecf4241ffddf44f3ca401621c56fc999f3"
          },
          {
            "frame_index": 1,
            "width": 4,
            "height": 5,
            "x_offset": 2,
            "y_offset": 1,
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
            "scanline_byte_length": 1,
            "pixel_count": 20,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": false,
            "pixel_hash": "sha256:6c73f1a6e779d2fc2ec3a95e0c5a579118a5fbcc6a1c95e1462f921f0cac0e5e"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:640882b56ffa6a01ab835affd7334cecf4241ffddf44f3ca401621c56fc999f3",
          "sha256:6c73f1a6e779d2fc2ec3a95e0c5a579118a5fbcc6a1c95e1462f921f0cac0e5e"
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
          "sha256:193f6829f1b15265fd877fb45efce5919c50b5368ff9135f822a4ccb7e75168e"
        ],
        "after_dispose_hashes": [
          "sha256:640882b56ffa6a01ab835affd7334cecf4241ffddf44f3ca401621c56fc999f3",
          "sha256:193f6829f1b15265fd877fb45efce5919c50b5368ff9135f822a4ccb7e75168e"
        ],
        "final_canvas_hash": "sha256:193f6829f1b15265fd877fb45efce5919c50b5368ff9135f822a4ccb7e75168e",
        "final_output_hash": "sha256:193f6829f1b15265fd877fb45efce5919c50b5368ff9135f822a4ccb7e75168e"
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "slip_gray_stable_indexed4_trns_source_patch",
      "case_family_id": "indexed4_trns_source_patch",
      "color_type": 3,
      "bit_depth": 4,
      "blend_op": 0,
      "png_file_name": "slip_gray_stable_indexed4_trns_source_patch.png",
      "png_hash": "sha256:5afc670b9ed15aba58195d734df1f6a323e18f48ca08af162cefd636219bcb7c",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 4,
          "color_type": 3,
          "compression": 0,
          "filter_method": 0,
          "interlace": 0
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 4,
        "color_type": 3,
        "bytes_per_pixel": 1,
        "scanline_byte_length": 4,
        "filter_bpp": 1,
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
            "scanline_byte_length": 4,
            "pixel_count": 64,
            "transparent_pixel_count": 6,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:d06cb1f160bf6f501faa1dc60b00718d50e39c33004f3c226d4b1daec39c653e"
          },
          {
            "frame_index": 1,
            "width": 4,
            "height": 5,
            "x_offset": 2,
            "y_offset": 1,
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
            "scanline_byte_length": 2,
            "pixel_count": 20,
            "transparent_pixel_count": 2,
            "partial_alpha_pixel_count": 0,
            "full_canvas": false,
            "pixel_hash": "sha256:5ab62e08a73222aa523d735c38fe2fce7d883acab25a65fb29e1ea1b06ad8497"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:d06cb1f160bf6f501faa1dc60b00718d50e39c33004f3c226d4b1daec39c653e",
          "sha256:5ab62e08a73222aa523d735c38fe2fce7d883acab25a65fb29e1ea1b06ad8497"
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
          "sha256:bc040952531fdffad036a49b5163c9fb773704275957d3137d98345744ec7dce"
        ],
        "after_dispose_hashes": [
          "sha256:d06cb1f160bf6f501faa1dc60b00718d50e39c33004f3c226d4b1daec39c653e",
          "sha256:bc040952531fdffad036a49b5163c9fb773704275957d3137d98345744ec7dce"
        ],
        "final_canvas_hash": "sha256:bc040952531fdffad036a49b5163c9fb773704275957d3137d98345744ec7dce",
        "final_output_hash": "sha256:bc040952531fdffad036a49b5163c9fb773704275957d3137d98345744ec7dce"
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "slip_gray_stable_truecolor16_source_patch",
      "case_family_id": "truecolor16_source_patch",
      "color_type": 2,
      "bit_depth": 16,
      "blend_op": 0,
      "png_file_name": "slip_gray_stable_truecolor16_source_patch.png",
      "png_hash": "sha256:6faf396ccc3a1ad5e8456a87e9d3fd37ff30fdd9b2a07a66549e3bf46a1543a4",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 2,
          "compression": 0,
          "filter_method": 0,
          "interlace": 0
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 2,
        "bytes_per_pixel": 6,
        "scanline_byte_length": 48,
        "filter_bpp": 6,
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
            "scanline_byte_length": 48,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0"
          },
          {
            "frame_index": 1,
            "width": 4,
            "height": 5,
            "x_offset": 2,
            "y_offset": 1,
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
            "scanline_byte_length": 24,
            "pixel_count": 20,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": false,
            "pixel_hash": "sha256:f2874b19c4f96a42d4640b00a04546d9f0bf36c630ef95af1bfb5f386be800d9"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:f2874b19c4f96a42d4640b00a04546d9f0bf36c630ef95af1bfb5f386be800d9"
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
          "sha256:6e587e61c8a9c76767c502b13be6ff5bae9f30e1b3b9d828f33c1676d3aca118"
        ],
        "after_dispose_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:6e587e61c8a9c76767c502b13be6ff5bae9f30e1b3b9d828f33c1676d3aca118"
        ],
        "final_canvas_hash": "sha256:6e587e61c8a9c76767c502b13be6ff5bae9f30e1b3b9d828f33c1676d3aca118",
        "final_output_hash": "sha256:6e587e61c8a9c76767c502b13be6ff5bae9f30e1b3b9d828f33c1676d3aca118"
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "slip_gray_stable_grayscale_alpha16_over_patch",
      "case_family_id": "grayscale_alpha16_over_patch",
      "color_type": 4,
      "bit_depth": 16,
      "blend_op": 1,
      "png_file_name": "slip_gray_stable_grayscale_alpha16_over_patch.png",
      "png_hash": "sha256:c25e24d299233730c809298fde57bf80a55025418982c4243acaeef130c1c7a0",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 4,
          "compression": 0,
          "filter_method": 0,
          "interlace": 0
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 4,
        "bytes_per_pixel": 4,
        "scanline_byte_length": 32,
        "filter_bpp": 4,
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
            "scanline_byte_length": 32,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:eb764661995399f3ff2e1088700d5f6054866fab56027598b066593697b3576f"
          },
          {
            "frame_index": 1,
            "width": 4,
            "height": 5,
            "x_offset": 2,
            "y_offset": 1,
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
            "scanline_byte_length": 16,
            "pixel_count": 20,
            "transparent_pixel_count": 2,
            "partial_alpha_pixel_count": 18,
            "full_canvas": false,
            "pixel_hash": "sha256:b760d502579f03a6250835ac6be2c535d1408846c5195956290219e2ab8d56bd"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:eb764661995399f3ff2e1088700d5f6054866fab56027598b066593697b3576f",
          "sha256:b760d502579f03a6250835ac6be2c535d1408846c5195956290219e2ab8d56bd"
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
          "sha256:46e35f435bc82bc62f2335ffcabb854b16df9cd5304b13535d98a6cf8c0a85bd"
        ],
        "after_dispose_hashes": [
          "sha256:eb764661995399f3ff2e1088700d5f6054866fab56027598b066593697b3576f",
          "sha256:46e35f435bc82bc62f2335ffcabb854b16df9cd5304b13535d98a6cf8c0a85bd"
        ],
        "final_canvas_hash": "sha256:46e35f435bc82bc62f2335ffcabb854b16df9cd5304b13535d98a6cf8c0a85bd",
        "final_output_hash": "sha256:46e35f435bc82bc62f2335ffcabb854b16df9cd5304b13535d98a6cf8c0a85bd"
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "slip_gray_stable_truecolor_alpha16_over_patch",
      "case_family_id": "truecolor_alpha16_over_patch",
      "color_type": 6,
      "bit_depth": 16,
      "blend_op": 1,
      "png_file_name": "slip_gray_stable_truecolor_alpha16_over_patch.png",
      "png_hash": "sha256:bb8489b63675a8095232741c2874148951451888d2a3de1a59ebfb4be99eea86",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 6,
          "compression": 0,
          "filter_method": 0,
          "interlace": 0
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 6,
        "bytes_per_pixel": 8,
        "scanline_byte_length": 64,
        "filter_bpp": 8,
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
            "scanline_byte_length": 64,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:379714cf07de62aed1cd54f21855ac6a3761f38b03a3324928918184225ecf68"
          },
          {
            "frame_index": 1,
            "width": 4,
            "height": 5,
            "x_offset": 2,
            "y_offset": 1,
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
            "scanline_byte_length": 32,
            "pixel_count": 20,
            "transparent_pixel_count": 2,
            "partial_alpha_pixel_count": 18,
            "full_canvas": false,
            "pixel_hash": "sha256:30bfbf993988c80af796ffe0a178ec6e0b7541cd6165b8240e5e594b0d8966c7"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:379714cf07de62aed1cd54f21855ac6a3761f38b03a3324928918184225ecf68",
          "sha256:30bfbf993988c80af796ffe0a178ec6e0b7541cd6165b8240e5e594b0d8966c7"
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
          "sha256:2e2c4b26fb6b3ae1ab098a31e2487b9a306d7bc3fc9717f7d174867501bd5387"
        ],
        "after_dispose_hashes": [
          "sha256:379714cf07de62aed1cd54f21855ac6a3761f38b03a3324928918184225ecf68",
          "sha256:2e2c4b26fb6b3ae1ab098a31e2487b9a306d7bc3fc9717f7d174867501bd5387"
        ],
        "final_canvas_hash": "sha256:2e2c4b26fb6b3ae1ab098a31e2487b9a306d7bc3fc9717f7d174867501bd5387",
        "final_output_hash": "sha256:2e2c4b26fb6b3ae1ab098a31e2487b9a306d7bc3fc9717f7d174867501bd5387"
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "slip_amber_social_grayscale1_source_patch",
      "case_family_id": "grayscale1_source_patch",
      "color_type": 0,
      "bit_depth": 1,
      "blend_op": 0,
      "png_file_name": "slip_amber_social_grayscale1_source_patch.png",
      "png_hash": "sha256:b2b4b1c1efd1f728cdcde76fc11f099e9550c8290cd58c096cd086c9a8e19e5e",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 1,
          "color_type": 0,
          "compression": 0,
          "filter_method": 0,
          "interlace": 0
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 1,
        "color_type": 0,
        "bytes_per_pixel": 1,
        "scanline_byte_length": 1,
        "filter_bpp": 1,
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
            "scanline_byte_length": 1,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:ff30b79b6c1a05043b92ecbc6b2ae71567b6dd457ff1b4e6a12cecab32a3eb46"
          },
          {
            "frame_index": 1,
            "width": 4,
            "height": 5,
            "x_offset": 2,
            "y_offset": 1,
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
            "scanline_byte_length": 1,
            "pixel_count": 20,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": false,
            "pixel_hash": "sha256:e63e2a8238a5740d3a2866286f30271e2d90f6e97f99a6a942ec955b465807a2"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:ff30b79b6c1a05043b92ecbc6b2ae71567b6dd457ff1b4e6a12cecab32a3eb46",
          "sha256:e63e2a8238a5740d3a2866286f30271e2d90f6e97f99a6a942ec955b465807a2"
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
          "sha256:38a03fa37a8859675e40ea424ccae5bfbf72e7be8eb5553b1f1f6b4eda557f51"
        ],
        "after_dispose_hashes": [
          "sha256:ff30b79b6c1a05043b92ecbc6b2ae71567b6dd457ff1b4e6a12cecab32a3eb46",
          "sha256:38a03fa37a8859675e40ea424ccae5bfbf72e7be8eb5553b1f1f6b4eda557f51"
        ],
        "final_canvas_hash": "sha256:38a03fa37a8859675e40ea424ccae5bfbf72e7be8eb5553b1f1f6b4eda557f51",
        "final_output_hash": "sha256:38a03fa37a8859675e40ea424ccae5bfbf72e7be8eb5553b1f1f6b4eda557f51"
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "slip_amber_social_indexed4_trns_source_patch",
      "case_family_id": "indexed4_trns_source_patch",
      "color_type": 3,
      "bit_depth": 4,
      "blend_op": 0,
      "png_file_name": "slip_amber_social_indexed4_trns_source_patch.png",
      "png_hash": "sha256:2a605ace2e394df5c2caf6c7266c88d2c274583584704fe893e211d0eb20272b",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 4,
          "color_type": 3,
          "compression": 0,
          "filter_method": 0,
          "interlace": 0
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 4,
        "color_type": 3,
        "bytes_per_pixel": 1,
        "scanline_byte_length": 4,
        "filter_bpp": 1,
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
            "scanline_byte_length": 4,
            "pixel_count": 64,
            "transparent_pixel_count": 6,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:05abc4b97632c187bb33b9b5d5f3d864e6ded5c60cbbb2f95a7e3e5069aac740"
          },
          {
            "frame_index": 1,
            "width": 4,
            "height": 5,
            "x_offset": 2,
            "y_offset": 1,
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
            "scanline_byte_length": 2,
            "pixel_count": 20,
            "transparent_pixel_count": 2,
            "partial_alpha_pixel_count": 0,
            "full_canvas": false,
            "pixel_hash": "sha256:769467940a16c6f7a20f1f2df9427cfe739ad3ad7c6c4004441598cb4f94f3f4"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:05abc4b97632c187bb33b9b5d5f3d864e6ded5c60cbbb2f95a7e3e5069aac740",
          "sha256:769467940a16c6f7a20f1f2df9427cfe739ad3ad7c6c4004441598cb4f94f3f4"
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
          "sha256:4c221fb1c74cd76f1bf372d2ee7db1e5ff89b168ab3123a7cc890a7d189674c3"
        ],
        "after_dispose_hashes": [
          "sha256:05abc4b97632c187bb33b9b5d5f3d864e6ded5c60cbbb2f95a7e3e5069aac740",
          "sha256:4c221fb1c74cd76f1bf372d2ee7db1e5ff89b168ab3123a7cc890a7d189674c3"
        ],
        "final_canvas_hash": "sha256:4c221fb1c74cd76f1bf372d2ee7db1e5ff89b168ab3123a7cc890a7d189674c3",
        "final_output_hash": "sha256:4c221fb1c74cd76f1bf372d2ee7db1e5ff89b168ab3123a7cc890a7d189674c3"
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "slip_amber_social_truecolor16_source_patch",
      "case_family_id": "truecolor16_source_patch",
      "color_type": 2,
      "bit_depth": 16,
      "blend_op": 0,
      "png_file_name": "slip_amber_social_truecolor16_source_patch.png",
      "png_hash": "sha256:adf72bd62168525224efdd0648b81f7e5318beb822db52c0b86b2405612cdbb2",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 2,
          "compression": 0,
          "filter_method": 0,
          "interlace": 0
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 2,
        "bytes_per_pixel": 6,
        "scanline_byte_length": 48,
        "filter_bpp": 6,
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
            "scanline_byte_length": 48,
            "pixel_count": 64,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": true,
            "pixel_hash": "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb"
          },
          {
            "frame_index": 1,
            "width": 4,
            "height": 5,
            "x_offset": 2,
            "y_offset": 1,
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
            "scanline_byte_length": 24,
            "pixel_count": 20,
            "transparent_pixel_count": 0,
            "partial_alpha_pixel_count": 0,
            "full_canvas": false,
            "pixel_hash": "sha256:e36e519d1aaf15840314509c53b38a689d30bbbb605dfb2573486085f5c33795"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:e36e519d1aaf15840314509c53b38a689d30bbbb605dfb2573486085f5c33795"
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
          "sha256:2193042f1ae71d23404241ebe24f3748c5f28e0df92d42a52d112352480b87f2"
        ],
        "after_dispose_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:2193042f1ae71d23404241ebe24f3748c5f28e0df92d42a52d112352480b87f2"
        ],
        "final_canvas_hash": "sha256:2193042f1ae71d23404241ebe24f3748c5f28e0df92d42a52d112352480b87f2",
        "final_output_hash": "sha256:2193042f1ae71d23404241ebe24f3748c5f28e0df92d42a52d112352480b87f2"
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "slip_amber_social_grayscale_alpha16_over_patch",
      "case_family_id": "grayscale_alpha16_over_patch",
      "color_type": 4,
      "bit_depth": 16,
      "blend_op": 1,
      "png_file_name": "slip_amber_social_grayscale_alpha16_over_patch.png",
      "png_hash": "sha256:b84e779b23cdc53a685205aefe55483cff57c59fbea6308aaca4217ebbb9ed13",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 4,
          "compression": 0,
          "filter_method": 0,
          "interlace": 0
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 4,
        "bytes_per_pixel": 4,
        "scanline_byte_length": 32,
        "filter_bpp": 4,
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
            "scanline_byte_length": 32,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:b52078c12ad2034345e53e4510d26fa18b9dc704ad1f4bc2d4eff33682be9db6"
          },
          {
            "frame_index": 1,
            "width": 4,
            "height": 5,
            "x_offset": 2,
            "y_offset": 1,
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
            "scanline_byte_length": 16,
            "pixel_count": 20,
            "transparent_pixel_count": 2,
            "partial_alpha_pixel_count": 18,
            "full_canvas": false,
            "pixel_hash": "sha256:fd8173a16e65067a544f3b36820cf214bbb5aed88203fae457c75a8bb48b4384"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:b52078c12ad2034345e53e4510d26fa18b9dc704ad1f4bc2d4eff33682be9db6",
          "sha256:fd8173a16e65067a544f3b36820cf214bbb5aed88203fae457c75a8bb48b4384"
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
          "sha256:eef4dca9a5a47c2fd197a93429b8ea8cdf3ea850ca9f6c003e212d6f718ae6aa"
        ],
        "after_dispose_hashes": [
          "sha256:b52078c12ad2034345e53e4510d26fa18b9dc704ad1f4bc2d4eff33682be9db6",
          "sha256:eef4dca9a5a47c2fd197a93429b8ea8cdf3ea850ca9f6c003e212d6f718ae6aa"
        ],
        "final_canvas_hash": "sha256:eef4dca9a5a47c2fd197a93429b8ea8cdf3ea850ca9f6c003e212d6f718ae6aa",
        "final_output_hash": "sha256:eef4dca9a5a47c2fd197a93429b8ea8cdf3ea850ca9f6c003e212d6f718ae6aa"
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "slip_amber_social_truecolor_alpha16_over_patch",
      "case_family_id": "truecolor_alpha16_over_patch",
      "color_type": 6,
      "bit_depth": 16,
      "blend_op": 1,
      "png_file_name": "slip_amber_social_truecolor_alpha16_over_patch.png",
      "png_hash": "sha256:4b920a5980d9bd6f7989e298f28914a4166611b608ee9960b7f09a64b3acb452",
      "decoded": {
        "ok": true,
        "ihdr": {
          "width": 8,
          "height": 8,
          "bit_depth": 16,
          "color_type": 6,
          "compression": 0,
          "filter_method": 0,
          "interlace": 0
        },
        "canvas_width": 8,
        "canvas_height": 8,
        "bit_depth": 16,
        "color_type": 6,
        "bytes_per_pixel": 8,
        "scanline_byte_length": 64,
        "filter_bpp": 8,
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
            "scanline_byte_length": 64,
            "pixel_count": 64,
            "transparent_pixel_count": 5,
            "partial_alpha_pixel_count": 9,
            "full_canvas": true,
            "pixel_hash": "sha256:a50eb115b304e7c79e820bdf2d0839f104a9e4c3166758dd87a7747c2598a1aa"
          },
          {
            "frame_index": 1,
            "width": 4,
            "height": 5,
            "x_offset": 2,
            "y_offset": 1,
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
            "scanline_byte_length": 32,
            "pixel_count": 20,
            "transparent_pixel_count": 2,
            "partial_alpha_pixel_count": 18,
            "full_canvas": false,
            "pixel_hash": "sha256:0780cb94662763b1b318741532174cb44673afc6c412ec1e6f3559b4e8426a8d"
          }
        ],
        "frame_pixel_hashes": [
          "sha256:a50eb115b304e7c79e820bdf2d0839f104a9e4c3166758dd87a7747c2598a1aa",
          "sha256:0780cb94662763b1b318741532174cb44673afc6c412ec1e6f3559b4e8426a8d"
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
          "sha256:aeb5281f70730a8ba0ba4238cd60f612fba1c7b716503372744930a44d875af4"
        ],
        "after_dispose_hashes": [
          "sha256:a50eb115b304e7c79e820bdf2d0839f104a9e4c3166758dd87a7747c2598a1aa",
          "sha256:aeb5281f70730a8ba0ba4238cd60f612fba1c7b716503372744930a44d875af4"
        ],
        "final_canvas_hash": "sha256:aeb5281f70730a8ba0ba4238cd60f612fba1c7b716503372744930a44d875af4",
        "final_output_hash": "sha256:aeb5281f70730a8ba0ba4238cd60f612fba1c7b716503372744930a44d875af4"
      },
      "success": true
    }
  ],
  "invalid_probe_results": [
    {
      "probe_id": "out_of_bounds_partial_frame",
      "expected_family": "apng_frame_bounds_invalid",
      "rejected": true,
      "decoded": {
        "ok": false,
        "errors": [
          {
            "path": "apng.partial_sample_frame_data",
            "family": "apng_frame_bounds_invalid",
            "message": "APNG frame bounds exceed the canvas"
          }
        ],
        "error_families": [
          "apng_frame_bounds_invalid"
        ],
        "error_family": "apng_frame_bounds_invalid"
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
            "path": "apng.partial_sample_frame_data",
            "family": "png_bit_depth_color_type_invalid",
            "message": "PNG bit depth is not allowed for this APNG partial-sample lab color type"
          }
        ],
        "error_families": [
          "png_bit_depth_color_type_invalid"
        ],
        "error_family": "png_bit_depth_color_type_invalid"
      }
    },
    {
      "probe_id": "truncated_partial_scanline",
      "expected_family": "apng_scanline_length_mismatch",
      "rejected": true,
      "decoded": {
        "ok": false,
        "errors": [
          {
            "path": "apng.partial_sample_frame_data",
            "family": "apng_scanline_length_mismatch",
            "message": "APNG scanline length does not match frame dimensions"
          }
        ],
        "error_families": [
          "apng_scanline_length_mismatch"
        ],
        "error_family": "apng_scanline_length_mismatch"
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
            "path": "apng.partial_sample_frame_data",
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
            "path": "apng.partial_sample_frame_data",
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
