window.MECHAGOTCHI_PNG_ADAM7_DEEP_COLOR_CROSS_PRODUCT = {
  "report": {
    "artifact_id": "png_adam7_deep_color_cross_product_stage0",
    "status": "research_png_adam7_deep_color_cross_product_no_package_code",
    "profile_count": 3,
    "variant_count_per_profile": 11,
    "variant_roundtrip_count": 33,
    "variant_roundtrip_success_count": 33,
    "invalid_probe_count": 7,
    "invalid_probe_rejected_count": 7,
    "metrics": {
      "variant_roundtrip_success_rate": 1.0,
      "mean_semantic_fidelity": 1.0,
      "mean_pixel_fidelity": 1.0,
      "invalid_probe_rejection_rate": 1.0,
      "supported_color_types": [
        0,
        2,
        3,
        4,
        6
      ],
      "supported_bit_depths": [
        1,
        2,
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
      "mean_non_empty_pass_count": 7.0,
      "quantized_visual_variant_count": 27
    },
    "closed_states": [
      "png_adam7_deep_color_cross_product_decoder",
      "png_adam7_deep_color_low_bit_decoder",
      "png_adam7_deep_color_16bit_decoder",
      "png_adam7_deep_color_grayscale_alpha_decoder",
      "png_adam7_deep_color_pass_manifest",
      "png_adam7_deep_color_sidecar_semantic_restore",
      "png_adam7_deep_color_invalid_probe_rejection"
    ],
    "blocked_states": [
      "apng_decoder",
      "full_png_conformance",
      "live_external_editor_rewrite_validation",
      "private_chunk_editor_preservation_matrix",
      "final_png_production_carrier_selection",
      "package_runtime_integration",
      "manual_readability_calibration",
      "profile_weighted_evolution"
    ],
    "decision": "prototype_png_adam7_deep_color_cross_product"
  },
  "variant_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "adam7_grayscale_1bit",
      "asset": {
        "asset_id": "slip_lcd_seed_adam7_grayscale_1bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_lcd_seed_adam7_grayscale_1bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:ed57c553c52ae60bfc2fe9cffc3d463833302d9236455de68e36c02ff0b336a1",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 1,
        "color_type": 0,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "adam7_grayscale_2bit",
      "asset": {
        "asset_id": "slip_lcd_seed_adam7_grayscale_2bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_lcd_seed_adam7_grayscale_2bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:ddf9165640ee19484f515af6cdbc976b9b960d74c88cebb87ae1eff83771e363",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 2,
        "color_type": 0,
        "interlace_method": 1,
        "pixel_count": 64,
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
            "scanline_byte_length": 2,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "adam7_grayscale_4bit",
      "asset": {
        "asset_id": "slip_lcd_seed_adam7_grayscale_4bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_lcd_seed_adam7_grayscale_4bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:cb2e4213b2bcb7964b851a51947213dc2fdb84e79ea36bc1b8ee5c9929ae3a40",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 4,
        "color_type": 0,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "adam7_grayscale_16bit",
      "asset": {
        "asset_id": "slip_lcd_seed_adam7_grayscale_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_lcd_seed_adam7_grayscale_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:731aad49ffa052b3065e585ade5bb5cb10b0a6af66d6fa015d8904dd21418273",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 0,
        "interlace_method": 1,
        "pixel_count": 64,
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
            "scanline_byte_length": 2,
            "filter_bpp": 2,
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
            "scanline_byte_length": 2,
            "filter_bpp": 2,
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
            "scanline_byte_length": 4,
            "filter_bpp": 2,
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
            "scanline_byte_length": 4,
            "filter_bpp": 2,
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
            "scanline_byte_length": 8,
            "filter_bpp": 2,
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
            "scanline_byte_length": 8,
            "filter_bpp": 2,
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
            "scanline_byte_length": 16,
            "filter_bpp": 2,
            "filter_types_seen": [
              1,
              2,
              3,
              4
            ]
          }
        ],
        "non_empty_pass_count": 7,
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "adam7_indexed_1bit",
      "asset": {
        "asset_id": "slip_lcd_seed_adam7_indexed_1bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_lcd_seed_adam7_indexed_1bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:1cd3990c14f297d1b7888c1c40d5027b9cecbbf089ad04ba10fd797d5409e739",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 1,
        "color_type": 3,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "PLTE",
          "IDAT",
          "IEND"
        ],
        "has_plte": true,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "adam7_indexed_2bit",
      "asset": {
        "asset_id": "slip_lcd_seed_adam7_indexed_2bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_lcd_seed_adam7_indexed_2bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:f795e7c8730b4bf81ba96bd00d2e7598ea3ba3de46bf96cb97d3c7e025b41663",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 2,
        "color_type": 3,
        "interlace_method": 1,
        "pixel_count": 64,
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
            "scanline_byte_length": 2,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "PLTE",
          "IDAT",
          "IEND"
        ],
        "has_plte": true,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "adam7_indexed_4bit",
      "asset": {
        "asset_id": "slip_lcd_seed_adam7_indexed_4bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_lcd_seed_adam7_indexed_4bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:fb99003b01f7856eaaf3850e2ba48b3d3cf6e23605a3e8d1e1e7dda00e0eb406",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 4,
        "color_type": 3,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "PLTE",
          "IDAT",
          "IEND"
        ],
        "has_plte": true,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "adam7_truecolor_16bit",
      "asset": {
        "asset_id": "slip_lcd_seed_adam7_truecolor_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_lcd_seed_adam7_truecolor_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:d1e8226920ac66ddd4cc0dd3bcc279cee123db3b8e537a5dd89ea0de2bbe61af",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 2,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 0,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "adam7_grayscale_alpha_8bit",
      "asset": {
        "asset_id": "slip_lcd_seed_adam7_grayscale_alpha_8bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_lcd_seed_adam7_grayscale_alpha_8bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:0a9daa941024a6c8d3461336dd9da2691720ab6fcbee96be1bf1a12b3cf84d90",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 4,
        "interlace_method": 1,
        "pixel_count": 64,
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
            "scanline_byte_length": 2,
            "filter_bpp": 2,
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
            "scanline_byte_length": 2,
            "filter_bpp": 2,
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
            "scanline_byte_length": 4,
            "filter_bpp": 2,
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
            "scanline_byte_length": 4,
            "filter_bpp": 2,
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
            "scanline_byte_length": 8,
            "filter_bpp": 2,
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
            "scanline_byte_length": 8,
            "filter_bpp": 2,
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
            "scanline_byte_length": 16,
            "filter_bpp": 2,
            "filter_types_seen": [
              1,
              2,
              3,
              4
            ]
          }
        ],
        "non_empty_pass_count": 7,
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "adam7_grayscale_alpha_16bit",
      "asset": {
        "asset_id": "slip_lcd_seed_adam7_grayscale_alpha_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_lcd_seed_adam7_grayscale_alpha_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:cbaf0abd3620b3617852de754983a9a442bf19f089db1fb8283f4ea9efe8fb86",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 4,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "adam7_rgba_16bit",
      "asset": {
        "asset_id": "slip_lcd_seed_adam7_rgba_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_lcd_seed_adam7_rgba_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:18ca0f004e51373b4ac340cdb00af4a6a197d8dc02ae3bc07efe44d92afc6771",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 6,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 0,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "adam7_grayscale_1bit",
      "asset": {
        "asset_id": "slip_gray_stable_adam7_grayscale_1bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_gray_stable_adam7_grayscale_1bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:ff5d21e12a01b50d8f53215a4ef2e595c8cafdcb0da644079ad2c836619e24c1",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 1,
        "color_type": 0,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "adam7_grayscale_2bit",
      "asset": {
        "asset_id": "slip_gray_stable_adam7_grayscale_2bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_gray_stable_adam7_grayscale_2bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:9b7a5fccc65b1b45866fe277ba016ef5746f10d018505e0492358dcbd7cd1757",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 2,
        "color_type": 0,
        "interlace_method": 1,
        "pixel_count": 64,
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
            "scanline_byte_length": 2,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "adam7_grayscale_4bit",
      "asset": {
        "asset_id": "slip_gray_stable_adam7_grayscale_4bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_gray_stable_adam7_grayscale_4bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:29293e0df22488ae8fb83288af876963cf2e29a3d6b2344b0b486d79ee26e704",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 4,
        "color_type": 0,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "adam7_grayscale_16bit",
      "asset": {
        "asset_id": "slip_gray_stable_adam7_grayscale_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_gray_stable_adam7_grayscale_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:0d9511edc0a220c776ebac8afee9eb2b3adab94050cd922684338c1a63b7ea41",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 0,
        "interlace_method": 1,
        "pixel_count": 64,
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
            "scanline_byte_length": 2,
            "filter_bpp": 2,
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
            "scanline_byte_length": 2,
            "filter_bpp": 2,
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
            "scanline_byte_length": 4,
            "filter_bpp": 2,
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
            "scanline_byte_length": 4,
            "filter_bpp": 2,
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
            "scanline_byte_length": 8,
            "filter_bpp": 2,
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
            "scanline_byte_length": 8,
            "filter_bpp": 2,
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
            "scanline_byte_length": 16,
            "filter_bpp": 2,
            "filter_types_seen": [
              1,
              2,
              3,
              4
            ]
          }
        ],
        "non_empty_pass_count": 7,
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "adam7_indexed_1bit",
      "asset": {
        "asset_id": "slip_gray_stable_adam7_indexed_1bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_gray_stable_adam7_indexed_1bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:c9bafb0bb41e21638041b474781470054e497b0afe34189c6647fbe00354084f",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 1,
        "color_type": 3,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "PLTE",
          "IDAT",
          "IEND"
        ],
        "has_plte": true,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "adam7_indexed_2bit",
      "asset": {
        "asset_id": "slip_gray_stable_adam7_indexed_2bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_gray_stable_adam7_indexed_2bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:09d406652a94f47ad5f6d869a0e40292a74bd8b746c24b76ac5d36f7bff0d819",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 2,
        "color_type": 3,
        "interlace_method": 1,
        "pixel_count": 64,
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
            "scanline_byte_length": 2,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "PLTE",
          "IDAT",
          "IEND"
        ],
        "has_plte": true,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "adam7_indexed_4bit",
      "asset": {
        "asset_id": "slip_gray_stable_adam7_indexed_4bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_gray_stable_adam7_indexed_4bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:b22d57bc83c57a0b44261be595e8e228e8715035b8724ea6383220937d194f64",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 4,
        "color_type": 3,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "PLTE",
          "IDAT",
          "IEND"
        ],
        "has_plte": true,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "adam7_truecolor_16bit",
      "asset": {
        "asset_id": "slip_gray_stable_adam7_truecolor_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_gray_stable_adam7_truecolor_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:3d36b3a9781a5223c4368b76e08aead0f8941c8529ce3b5cc2c7d6be0ed787a4",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 2,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 0,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "adam7_grayscale_alpha_8bit",
      "asset": {
        "asset_id": "slip_gray_stable_adam7_grayscale_alpha_8bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_gray_stable_adam7_grayscale_alpha_8bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:b2419e4e353ac72e77abfc75d9bdf943c80c59257f241ca10e63cc6f1c9bbda8",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 4,
        "interlace_method": 1,
        "pixel_count": 64,
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
            "scanline_byte_length": 2,
            "filter_bpp": 2,
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
            "scanline_byte_length": 2,
            "filter_bpp": 2,
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
            "scanline_byte_length": 4,
            "filter_bpp": 2,
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
            "scanline_byte_length": 4,
            "filter_bpp": 2,
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
            "scanline_byte_length": 8,
            "filter_bpp": 2,
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
            "scanline_byte_length": 8,
            "filter_bpp": 2,
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
            "scanline_byte_length": 16,
            "filter_bpp": 2,
            "filter_types_seen": [
              1,
              2,
              3,
              4
            ]
          }
        ],
        "non_empty_pass_count": 7,
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "adam7_grayscale_alpha_16bit",
      "asset": {
        "asset_id": "slip_gray_stable_adam7_grayscale_alpha_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_gray_stable_adam7_grayscale_alpha_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:d32e8c687df7fa03498215a452080db071cd8271ebb406b4228fa395fee3e123",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 4,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "adam7_rgba_16bit",
      "asset": {
        "asset_id": "slip_gray_stable_adam7_rgba_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_gray_stable_adam7_rgba_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:d263422c9b15c483e6e7d3e335a01950d6503afe0c43f4151e75a0ae4ed55ffe",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 6,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 0,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "adam7_grayscale_1bit",
      "asset": {
        "asset_id": "slip_amber_social_adam7_grayscale_1bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_amber_social_adam7_grayscale_1bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:fa9ccf24ae2c96d7ffc24ee42fe3c3fc137e7f87ed232d96c096fad92f5fb30a",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 1,
        "color_type": 0,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "adam7_grayscale_2bit",
      "asset": {
        "asset_id": "slip_amber_social_adam7_grayscale_2bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_amber_social_adam7_grayscale_2bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:c2862e0464c6eb88ca2fc18d4a0a73d3b0c0d20a9eabc80c03db507ead91dc65",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 2,
        "color_type": 0,
        "interlace_method": 1,
        "pixel_count": 64,
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
            "scanline_byte_length": 2,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "adam7_grayscale_4bit",
      "asset": {
        "asset_id": "slip_amber_social_adam7_grayscale_4bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_amber_social_adam7_grayscale_4bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:7b8bdb11323edbb8a38df13d078d9d3efd9962d01f63278381a34ec82923b4c6",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 4,
        "color_type": 0,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "adam7_grayscale_16bit",
      "asset": {
        "asset_id": "slip_amber_social_adam7_grayscale_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_amber_social_adam7_grayscale_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:9b888e830bb3493b0b90e0b5998ee1e617b74dd256cc4e405b46f645767dcd9d",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 0,
        "interlace_method": 1,
        "pixel_count": 64,
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
            "scanline_byte_length": 2,
            "filter_bpp": 2,
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
            "scanline_byte_length": 2,
            "filter_bpp": 2,
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
            "scanline_byte_length": 4,
            "filter_bpp": 2,
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
            "scanline_byte_length": 4,
            "filter_bpp": 2,
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
            "scanline_byte_length": 8,
            "filter_bpp": 2,
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
            "scanline_byte_length": 8,
            "filter_bpp": 2,
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
            "scanline_byte_length": 16,
            "filter_bpp": 2,
            "filter_types_seen": [
              1,
              2,
              3,
              4
            ]
          }
        ],
        "non_empty_pass_count": 7,
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "adam7_indexed_1bit",
      "asset": {
        "asset_id": "slip_amber_social_adam7_indexed_1bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_amber_social_adam7_indexed_1bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:3504cda7d5ad5d0bf6849b0bdea266a07fab1274cadf9b6a382ff355b801337d",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 1,
        "color_type": 3,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "PLTE",
          "IDAT",
          "IEND"
        ],
        "has_plte": true,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "adam7_indexed_2bit",
      "asset": {
        "asset_id": "slip_amber_social_adam7_indexed_2bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_amber_social_adam7_indexed_2bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:c06c7c8a55d7b7df63e5abfba9254c51495d12245a24e08788c80c7c4d856a8d",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 2,
        "color_type": 3,
        "interlace_method": 1,
        "pixel_count": 64,
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
            "scanline_byte_length": 2,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "PLTE",
          "IDAT",
          "IEND"
        ],
        "has_plte": true,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "adam7_indexed_4bit",
      "asset": {
        "asset_id": "slip_amber_social_adam7_indexed_4bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_amber_social_adam7_indexed_4bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:7bb934161ba01fd628459ff7abee13dd5ea5f7694408695d3e9e11e4dd7cd26d",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 4,
        "color_type": 3,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "PLTE",
          "IDAT",
          "IEND"
        ],
        "has_plte": true,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "adam7_truecolor_16bit",
      "asset": {
        "asset_id": "slip_amber_social_adam7_truecolor_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_amber_social_adam7_truecolor_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:d265b74924bc28e8288ccd252e5d880ef089ecfa702bf8c09763874df3a28d7f",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 2,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 0,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "adam7_grayscale_alpha_8bit",
      "asset": {
        "asset_id": "slip_amber_social_adam7_grayscale_alpha_8bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_amber_social_adam7_grayscale_alpha_8bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:bf75cd850224bfd5668c7d61e0994ce93b1e93bf7c5616650e02e8eaf8ace229",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 4,
        "interlace_method": 1,
        "pixel_count": 64,
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
            "scanline_byte_length": 2,
            "filter_bpp": 2,
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
            "scanline_byte_length": 2,
            "filter_bpp": 2,
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
            "scanline_byte_length": 4,
            "filter_bpp": 2,
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
            "scanline_byte_length": 4,
            "filter_bpp": 2,
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
            "scanline_byte_length": 8,
            "filter_bpp": 2,
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
            "scanline_byte_length": 8,
            "filter_bpp": 2,
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
            "scanline_byte_length": 16,
            "filter_bpp": 2,
            "filter_types_seen": [
              1,
              2,
              3,
              4
            ]
          }
        ],
        "non_empty_pass_count": 7,
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "adam7_grayscale_alpha_16bit",
      "asset": {
        "asset_id": "slip_amber_social_adam7_grayscale_alpha_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_amber_social_adam7_grayscale_alpha_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:c878c5eafaae80c71d2e8f4180db26124e3838b8a168c98db3a87899fe5f6884",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 4,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 64,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "adam7_rgba_16bit",
      "asset": {
        "asset_id": "slip_amber_social_adam7_rgba_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-adam7-deep-color/slip_amber_social_adam7_rgba_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:cbd04e51adf4412dbf3f11b266924ee67cacf2db7d38c871498820c2edae8261",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 6,
        "interlace_method": 1,
        "pixel_count": 64,
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
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "source_visual_delta_count": 0,
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    }
  ]
};
