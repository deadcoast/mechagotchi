window.MECHAGOTCHI_PNG_VARIANT_SIDECAR_DECODER = {
  "report": {
    "artifact_id": "png_variant_sidecar_decoder_stage0",
    "status": "research_png_variant_sidecar_decoder_no_package_code",
    "profile_count": 3,
    "variant_count_per_profile": 5,
    "variant_roundtrip_count": 15,
    "variant_roundtrip_success_count": 15,
    "invalid_probe_count": 3,
    "invalid_probe_rejected_count": 3,
    "metrics": {
      "variant_roundtrip_success_rate": 1.0,
      "mean_semantic_fidelity": 1.0,
      "mean_pixel_fidelity": 1.0,
      "invalid_probe_rejection_rate": 1.0,
      "supported_color_types": [
        0,
        2,
        3,
        6
      ],
      "supported_filter_types": [
        0,
        1,
        2,
        3,
        4
      ]
    },
    "closed_states": [
      "png_color_type_0_2_3_6_8bit_decoder",
      "png_filter_types_0_to_4_decoder",
      "png_plte_indexed_color_decoder",
      "png_variant_sidecar_export",
      "png_variant_sidecar_import",
      "png_variant_sidecar_semantic_restore"
    ],
    "blocked_states": [
      "png_adam7_interlace_decoder",
      "apng_decoder",
      "png_color_type_4_grayscale_alpha_decoder",
      "png_bit_depth_1_2_4_16_decoder",
      "full_png_conformance",
      "spritesheet_variant_layout_coverage",
      "full_project_format_coverage",
      "embedded_png_metadata_writer",
      "project_file_native_metadata_writer",
      "profile_weighted_evolution"
    ],
    "decision": "prototype_png_variant_sidecar_decoder"
  },
  "variant_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "rgba_filter_none",
      "asset": {
        "asset_id": "slip_lcd_seed_rgba_filter_none.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-variant/slip_lcd_seed_rgba_filter_none.png",
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
        "interlace_method": 0,
        "pixel_count": 64,
        "filter_types_seen": [
          0
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "rgba_filter_cycle",
      "asset": {
        "asset_id": "slip_lcd_seed_rgba_filter_cycle.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-variant/slip_lcd_seed_rgba_filter_cycle.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:9b1473e14ec6e9713721a93bb5156b7a7df19619ca208a7a8a562f8d8ff68283",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "interlace_method": 0,
        "pixel_count": 64,
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
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "rgb_truecolor_sub",
      "asset": {
        "asset_id": "slip_lcd_seed_rgb_truecolor_sub.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-variant/slip_lcd_seed_rgb_truecolor_sub.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:eba197adc2da2bb857e11b44240c5b9e569173205645c22fa8eff65d3dda6c5f",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 2,
        "interlace_method": 0,
        "pixel_count": 64,
        "filter_types_seen": [
          1
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "grayscale_up",
      "asset": {
        "asset_id": "slip_lcd_seed_grayscale_up.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-variant/slip_lcd_seed_grayscale_up.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:a591ef8db8ca4ca55de7354d4fd156560a1ff00a3713de56752fec7eff7b8846",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 0,
        "interlace_method": 0,
        "pixel_count": 64,
        "filter_types_seen": [
          2
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "indexed_palette_average_paeth",
      "asset": {
        "asset_id": "slip_lcd_seed_indexed_palette_average_paeth.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-variant/slip_lcd_seed_indexed_palette_average_paeth.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:1962d9d156f3d7dccba39ebb90a8f84afb21672f397cf0a16a73c1b9b6a58420",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 3,
        "interlace_method": 0,
        "pixel_count": 64,
        "filter_types_seen": [
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
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "rgba_filter_none",
      "asset": {
        "asset_id": "slip_gray_stable_rgba_filter_none.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-variant/slip_gray_stable_rgba_filter_none.png",
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
        "interlace_method": 0,
        "pixel_count": 64,
        "filter_types_seen": [
          0
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "rgba_filter_cycle",
      "asset": {
        "asset_id": "slip_gray_stable_rgba_filter_cycle.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-variant/slip_gray_stable_rgba_filter_cycle.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:cc58a133976a17479e059237421d31ad1553f05665f794e941ef5d61a6babfe5",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "interlace_method": 0,
        "pixel_count": 64,
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
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "rgb_truecolor_sub",
      "asset": {
        "asset_id": "slip_gray_stable_rgb_truecolor_sub.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-variant/slip_gray_stable_rgb_truecolor_sub.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:6d6f1abc2c78c30a4f053811e1a02d150ef9315559814a0f26da9913faf3ee6e",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 2,
        "interlace_method": 0,
        "pixel_count": 64,
        "filter_types_seen": [
          1
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "grayscale_up",
      "asset": {
        "asset_id": "slip_gray_stable_grayscale_up.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-variant/slip_gray_stable_grayscale_up.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:5c7e15074aaf22a19f6f1c33eb9fe7cc3763f28118cad9444236aacef8afe186",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 0,
        "interlace_method": 0,
        "pixel_count": 64,
        "filter_types_seen": [
          2
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "indexed_palette_average_paeth",
      "asset": {
        "asset_id": "slip_gray_stable_indexed_palette_average_paeth.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-variant/slip_gray_stable_indexed_palette_average_paeth.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:f95ab9838ca6f85bdc19ce1faccb95e66b95b98ed4e3d571578927b91a92e88e",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 3,
        "interlace_method": 0,
        "pixel_count": 64,
        "filter_types_seen": [
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
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "rgba_filter_none",
      "asset": {
        "asset_id": "slip_amber_social_rgba_filter_none.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-variant/slip_amber_social_rgba_filter_none.png",
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
        "interlace_method": 0,
        "pixel_count": 64,
        "filter_types_seen": [
          0
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "rgba_filter_cycle",
      "asset": {
        "asset_id": "slip_amber_social_rgba_filter_cycle.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-variant/slip_amber_social_rgba_filter_cycle.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:29c56a16bf4330304963dbe4e57e8b46f61cc99e970f39f2c3aab99d63fb8a18",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "interlace_method": 0,
        "pixel_count": 64,
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
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "rgb_truecolor_sub",
      "asset": {
        "asset_id": "slip_amber_social_rgb_truecolor_sub.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-variant/slip_amber_social_rgb_truecolor_sub.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:d7d51920e2f6b6bbca08461482f8082f2cf4118ae3d69f2c8df5438b0a710860",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 2,
        "interlace_method": 0,
        "pixel_count": 64,
        "filter_types_seen": [
          1
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "grayscale_up",
      "asset": {
        "asset_id": "slip_amber_social_grayscale_up.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-variant/slip_amber_social_grayscale_up.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:fd214e18cb9ba2bc3c8b7fb0b08356ec458630330ea25d0cb12babd943faa49b",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 0,
        "interlace_method": 0,
        "pixel_count": 64,
        "filter_types_seen": [
          2
        ],
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "has_plte": false,
        "has_trns": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "indexed_palette_average_paeth",
      "asset": {
        "asset_id": "slip_amber_social_indexed_palette_average_paeth.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-variant/slip_amber_social_indexed_palette_average_paeth.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:0fcf9776fb46eb363eea5d75e3121823bd0cb39fb0a5680280a168dbccac12ff",
        "semantic_policy": "sidecar_required"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 3,
        "interlace_method": 0,
        "pixel_count": 64,
        "filter_types_seen": [
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
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    }
  ]
};
