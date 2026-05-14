window.MECHAGOTCHI_PNG_DEEP_COLOR_SIDECAR_DECODER = {
  "report": {
    "artifact_id": "png_deep_color_sidecar_decoder_stage0",
    "status": "research_png_deep_color_sidecar_decoder_no_package_code",
    "profile_count": 3,
    "variant_count_per_profile": 11,
    "variant_roundtrip_count": 33,
    "variant_roundtrip_success_count": 33,
    "invalid_probe_count": 6,
    "invalid_probe_rejected_count": 6,
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
      "quantized_visual_variant_count": 27
    },
    "closed_states": [
      "png_grayscale_low_bit_depth_decoder",
      "png_indexed_low_bit_depth_decoder",
      "png_16bit_sample_decoder",
      "png_color_type_4_grayscale_alpha_decoder",
      "png_deep_color_sidecar_export",
      "png_deep_color_sidecar_import",
      "png_deep_color_sidecar_semantic_restore",
      "png_deep_color_invalid_probe_rejection"
    ],
    "blocked_states": [
      "apng_decoder",
      "full_png_conformance",
      "adam7_deep_color_cross_product_decoder",
      "live_external_editor_rewrite_validation",
      "private_chunk_editor_preservation_matrix",
      "final_png_production_carrier_selection",
      "package_runtime_integration",
      "manual_readability_calibration",
      "profile_weighted_evolution"
    ],
    "decision": "prototype_png_deep_color_sidecar_decoder"
  },
  "variant_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "grayscale_1bit",
      "asset": {
        "asset_id": "slip_lcd_seed_grayscale_1bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_lcd_seed_grayscale_1bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:8febbbcebd3ef0e70c3f0ab8abf08c75d70c620e765468024ed28c51717a0672",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 1,
        "color_type": 0,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 1,
        "filter_bpp": 1,
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
      "variant_id": "grayscale_2bit",
      "asset": {
        "asset_id": "slip_lcd_seed_grayscale_2bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_lcd_seed_grayscale_2bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:07bbe1ffe2ca8fc533030ca623bab98c51dd62daac0091a81a31067bc8a31787",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 2,
        "color_type": 0,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 2,
        "filter_bpp": 1,
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
      "variant_id": "grayscale_4bit",
      "asset": {
        "asset_id": "slip_lcd_seed_grayscale_4bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_lcd_seed_grayscale_4bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:c67879d0c0760f733628ca73235c32fab1d16f2d42ca4cf90c73bda24e1b97cc",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 4,
        "color_type": 0,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 4,
        "filter_bpp": 1,
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
      "variant_id": "grayscale_16bit",
      "asset": {
        "asset_id": "slip_lcd_seed_grayscale_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_lcd_seed_grayscale_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:f6230d84f4758a64d070d90bee5598e2c2492b69d934a618893bf82d53246dc2",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 0,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 16,
        "filter_bpp": 2,
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
      "variant_id": "indexed_1bit",
      "asset": {
        "asset_id": "slip_lcd_seed_indexed_1bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_lcd_seed_indexed_1bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:0dd92bcd271edece1100b138ee340c98f7d2add05cf6e2a05c28d803dcdd3866",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 1,
        "color_type": 3,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 1,
        "filter_bpp": 1,
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
      "variant_id": "indexed_2bit",
      "asset": {
        "asset_id": "slip_lcd_seed_indexed_2bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_lcd_seed_indexed_2bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:ad1bbaaa9f87d9df467c7d0c2fb97ed5c5ecffe67251c5112663377719f89313",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 2,
        "color_type": 3,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 2,
        "filter_bpp": 1,
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
      "variant_id": "indexed_4bit",
      "asset": {
        "asset_id": "slip_lcd_seed_indexed_4bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_lcd_seed_indexed_4bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:74263a36f67df1394cdf60f9acff7e7961a709b80d2fc0ca4507602c19cd895f",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 4,
        "color_type": 3,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 4,
        "filter_bpp": 1,
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
      "variant_id": "truecolor_16bit",
      "asset": {
        "asset_id": "slip_lcd_seed_truecolor_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_lcd_seed_truecolor_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:217e7e5108ed8b6132fa2a8aa94a2483ac606fd64c3bbf8e31c1b9f1dfd215d8",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 2,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 48,
        "filter_bpp": 6,
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
      "variant_id": "grayscale_alpha_8bit",
      "asset": {
        "asset_id": "slip_lcd_seed_grayscale_alpha_8bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_lcd_seed_grayscale_alpha_8bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:4932b651b4f270a15dbb22aee74811ccebd876ad331a8bc6d1c20c7c76569b44",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 4,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 16,
        "filter_bpp": 2,
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
      "variant_id": "grayscale_alpha_16bit",
      "asset": {
        "asset_id": "slip_lcd_seed_grayscale_alpha_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_lcd_seed_grayscale_alpha_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:d21e61419074913748e9690563f807411c895f82cef45ced142fb74608db31db",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 4,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 32,
        "filter_bpp": 4,
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
      "variant_id": "rgba_16bit",
      "asset": {
        "asset_id": "slip_lcd_seed_rgba_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_lcd_seed_rgba_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:bd696142d9dc4f50b13ba77e0ba654422afa2cb9892e9f62728be6f8fc9d4c18",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 6,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 64,
        "filter_bpp": 8,
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
      "variant_id": "grayscale_1bit",
      "asset": {
        "asset_id": "slip_gray_stable_grayscale_1bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_gray_stable_grayscale_1bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:a114ed30a91b2354f465c0d2fdf7a1062629a6c4e695834492fe3a2dc95e8591",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 1,
        "color_type": 0,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 1,
        "filter_bpp": 1,
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
      "variant_id": "grayscale_2bit",
      "asset": {
        "asset_id": "slip_gray_stable_grayscale_2bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_gray_stable_grayscale_2bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:96d350a9c728884e78e2367bbae961474cdcb33d70a544f16e4b32f6f0f1d3cb",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 2,
        "color_type": 0,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 2,
        "filter_bpp": 1,
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
      "variant_id": "grayscale_4bit",
      "asset": {
        "asset_id": "slip_gray_stable_grayscale_4bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_gray_stable_grayscale_4bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:76949e29a09bbc8d38b0f6c3e2d79b755df0dbe45af272139e4be3c1e21f42bb",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 4,
        "color_type": 0,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 4,
        "filter_bpp": 1,
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
      "variant_id": "grayscale_16bit",
      "asset": {
        "asset_id": "slip_gray_stable_grayscale_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_gray_stable_grayscale_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:f72c12d56982a8027daf56435a7d4e8edc90b50b5c016380d9b1b9271a2192ab",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 0,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 16,
        "filter_bpp": 2,
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
      "variant_id": "indexed_1bit",
      "asset": {
        "asset_id": "slip_gray_stable_indexed_1bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_gray_stable_indexed_1bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:2552bb2fa8c34397595e9e8513305b87afe82b40cfc79a91ac7fc0e8da000b8b",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 1,
        "color_type": 3,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 1,
        "filter_bpp": 1,
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
      "variant_id": "indexed_2bit",
      "asset": {
        "asset_id": "slip_gray_stable_indexed_2bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_gray_stable_indexed_2bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:ab8162979031bba396b9ca10b3efb713432165deead8ec729eea87b47f9298a8",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 2,
        "color_type": 3,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 2,
        "filter_bpp": 1,
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
      "variant_id": "indexed_4bit",
      "asset": {
        "asset_id": "slip_gray_stable_indexed_4bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_gray_stable_indexed_4bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:5c0e1ec190168655c9b7f00ef0c9aea605f5d0061aed90975115a285c4877fc6",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 4,
        "color_type": 3,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 4,
        "filter_bpp": 1,
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
      "variant_id": "truecolor_16bit",
      "asset": {
        "asset_id": "slip_gray_stable_truecolor_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_gray_stable_truecolor_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:394412eb18bf44478c6e766e94b144b085c156da7dd68015ff3317858677a032",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 2,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 48,
        "filter_bpp": 6,
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
      "variant_id": "grayscale_alpha_8bit",
      "asset": {
        "asset_id": "slip_gray_stable_grayscale_alpha_8bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_gray_stable_grayscale_alpha_8bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:956c0a946e9eef8ca9dcbbf629b7c5073ee890a59e20d56ab3c43a7dc799a8c4",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 4,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 16,
        "filter_bpp": 2,
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
      "variant_id": "grayscale_alpha_16bit",
      "asset": {
        "asset_id": "slip_gray_stable_grayscale_alpha_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_gray_stable_grayscale_alpha_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:3f1f8c3129368ebc664d5a9533ca4f55f5bd9139f383674a0274a733e48598ab",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 4,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 32,
        "filter_bpp": 4,
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
      "variant_id": "rgba_16bit",
      "asset": {
        "asset_id": "slip_gray_stable_rgba_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_gray_stable_rgba_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:98b449713ef8ace51a5f8b96576011c9e4a7b93040f8d6df011ce49e134a14dc",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 6,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 64,
        "filter_bpp": 8,
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
      "variant_id": "grayscale_1bit",
      "asset": {
        "asset_id": "slip_amber_social_grayscale_1bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_amber_social_grayscale_1bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:2720e0443c393c6dc95cd15cea140401af4453492bd78c69c4f6cd981a8e39b8",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 1,
        "color_type": 0,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 1,
        "filter_bpp": 1,
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
      "variant_id": "grayscale_2bit",
      "asset": {
        "asset_id": "slip_amber_social_grayscale_2bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_amber_social_grayscale_2bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:60657d54887704d1f8ef2740f91084868938f3f7b39b3ec03d7af80d0c0687bd",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 2,
        "color_type": 0,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 2,
        "filter_bpp": 1,
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
      "variant_id": "grayscale_4bit",
      "asset": {
        "asset_id": "slip_amber_social_grayscale_4bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_amber_social_grayscale_4bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:9142cb65e5246dc9a3662bf35d45393ea66ed7ecab4d3617e35ffc69642ee707",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 4,
        "color_type": 0,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 4,
        "filter_bpp": 1,
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
      "variant_id": "grayscale_16bit",
      "asset": {
        "asset_id": "slip_amber_social_grayscale_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_amber_social_grayscale_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:e8656688e4636e1ea1ce043186166fdbef898a8f44e776f6c4f3d801ae0a9b10",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 0,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 16,
        "filter_bpp": 2,
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
      "variant_id": "indexed_1bit",
      "asset": {
        "asset_id": "slip_amber_social_indexed_1bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_amber_social_indexed_1bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:ba5bdb3308b5d31040b3c834b4f5c4b828a3ac9da60d3598e73c7dfb246d3a07",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 1,
        "color_type": 3,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 1,
        "filter_bpp": 1,
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
      "variant_id": "indexed_2bit",
      "asset": {
        "asset_id": "slip_amber_social_indexed_2bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_amber_social_indexed_2bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:745cc565a64d86e0ef6a661d429c2840d68ae3fbf3905be96bcfc1869dd5c566",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 2,
        "color_type": 3,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 2,
        "filter_bpp": 1,
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
      "variant_id": "indexed_4bit",
      "asset": {
        "asset_id": "slip_amber_social_indexed_4bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_amber_social_indexed_4bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:39cfc1b66c06cc383dc09f0e1c8f658185912c1ff4bfbe351f38ef9369cff4ba",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 4,
        "color_type": 3,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 4,
        "filter_bpp": 1,
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
      "variant_id": "truecolor_16bit",
      "asset": {
        "asset_id": "slip_amber_social_truecolor_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_amber_social_truecolor_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:3c09b0df34607e7fe5513ed7c48e7601a52e8028c96793c8d47ffce51a1d3776",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 2,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 48,
        "filter_bpp": 6,
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
      "variant_id": "grayscale_alpha_8bit",
      "asset": {
        "asset_id": "slip_amber_social_grayscale_alpha_8bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_amber_social_grayscale_alpha_8bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:5421d628f7c679fd2f2b478d860406bc24053ea541332c5062cf0d8fe2ab36c6",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 4,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 16,
        "filter_bpp": 2,
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
      "variant_id": "grayscale_alpha_16bit",
      "asset": {
        "asset_id": "slip_amber_social_grayscale_alpha_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_amber_social_grayscale_alpha_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:ad8dbc99e74af5f1fe1312cacc5f9df62c1aff97df9cd4af2f4e0fb648220179",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 4,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 32,
        "filter_bpp": 4,
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
      "variant_id": "rgba_16bit",
      "asset": {
        "asset_id": "slip_amber_social_rgba_16bit.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-deep-color/slip_amber_social_rgba_16bit.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:3878100eef77590a380a5c376e6d02bad0bea91fabb0736d3262f3229ec20483",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 16,
        "color_type": 6,
        "interlace_method": 0,
        "pixel_count": 64,
        "scanline_byte_length": 64,
        "filter_bpp": 8,
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
