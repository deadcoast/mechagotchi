window.MECHAGOTCHI_PNG_APNG_CHUNK_ORDER_CONFORMANCE = {
  "report": {
    "artifact_id": "png_apng_chunk_order_conformance_stage0",
    "status": "research_png_apng_chunk_order_conformance_no_package_code",
    "profile_count": 3,
    "conformance_case_ids": [
      "static_rgba_single_idat",
      "rgba_split_idat",
      "indexed_plte_trns",
      "apng_static_first_frame"
    ],
    "conformance_case_count": 12,
    "conformance_case_success_count": 12,
    "invalid_probe_count": 7,
    "invalid_probe_rejected_count": 7,
    "metrics": {
      "conformance_case_success_rate": 1.0,
      "invalid_probe_rejection_rate": 1.0,
      "profile_coverage": 3,
      "valid_case_family_count": 4
    },
    "closed_states": [
      "png_critical_chunk_order_matrix",
      "png_palette_transparency_order_matrix",
      "png_consecutive_idat_matrix",
      "apng_control_chunk_order_matrix",
      "apng_sequence_number_matrix"
    ],
    "blocked_states": [
      "full_apng_png_conformance",
      "live_external_editor_rewrite_validation",
      "production_import_export_carrier_selection_final_decision",
      "manual_readability_calibration",
      "package_runtime_lifecycle_integration"
    ],
    "decision": "prototype_png_apng_chunk_order_conformance_subset"
  },
  "conformance_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "static_rgba_single_idat",
      "description": "Static truecolor-alpha PNG with IHDR, one IDAT, and IEND.",
      "png_file_name": "slip_lcd_seed_static_rgba_single_idat.png",
      "png_hash": "sha256:7ec438e0f21f3731d1746da4fdc96dc51a16299e4e1855f8a3d149a10f797877",
      "validation": {
        "ok": true,
        "case_id": "static_rgba_single_idat",
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "chunk_count": 3,
        "idat_count": 1,
        "color_type": 6,
        "bit_depth": 8,
        "interlace_method": 0,
        "apng_sequence_numbers": [],
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "rgba_split_idat",
      "description": "Static truecolor-alpha PNG with consecutive split IDAT chunks.",
      "png_file_name": "slip_lcd_seed_rgba_split_idat.png",
      "png_hash": "sha256:9bf48c9639ead10159105d5aa69ffc00ebebc35c58abb48fb4eef1d018184b8b",
      "validation": {
        "ok": true,
        "case_id": "rgba_split_idat",
        "chunks": [
          "IHDR",
          "IDAT",
          "IDAT",
          "IEND"
        ],
        "chunk_count": 4,
        "idat_count": 2,
        "color_type": 6,
        "bit_depth": 8,
        "interlace_method": 0,
        "apng_sequence_numbers": [],
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "indexed_plte_trns",
      "description": "Indexed-color PNG with PLTE before tRNS before IDAT.",
      "png_file_name": "slip_lcd_seed_indexed_plte_trns.png",
      "png_hash": "sha256:dbb6a628ba5f89366c7336b3c58ca5b5f472aac571ae076d176b141d64970b80",
      "validation": {
        "ok": true,
        "case_id": "indexed_plte_trns",
        "chunks": [
          "IHDR",
          "PLTE",
          "tRNS",
          "IDAT",
          "IEND"
        ],
        "chunk_count": 5,
        "idat_count": 1,
        "color_type": 3,
        "bit_depth": 8,
        "interlace_method": 0,
        "apng_sequence_numbers": [],
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "apng_static_first_frame",
      "description": "APNG with acTL before IDAT, fcTL sequence 0 on the static first frame, and fdAT for the second frame.",
      "png_file_name": "slip_lcd_seed_apng_static_first_frame.png",
      "png_hash": "sha256:94675d786bfe50bdecf444ae2b2fc28b3b194d37eceaa9cada8270b43d75744d",
      "validation": {
        "ok": true,
        "case_id": "apng_static_first_frame",
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "IEND"
        ],
        "chunk_count": 7,
        "idat_count": 1,
        "color_type": 6,
        "bit_depth": 8,
        "interlace_method": 0,
        "apng_sequence_numbers": [
          0,
          1,
          2
        ],
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "static_rgba_single_idat",
      "description": "Static truecolor-alpha PNG with IHDR, one IDAT, and IEND.",
      "png_file_name": "slip_gray_stable_static_rgba_single_idat.png",
      "png_hash": "sha256:423852196fa1519d513342d2dc4ffdaa03d258fa3d22a58fe036227e386dee6c",
      "validation": {
        "ok": true,
        "case_id": "static_rgba_single_idat",
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "chunk_count": 3,
        "idat_count": 1,
        "color_type": 6,
        "bit_depth": 8,
        "interlace_method": 0,
        "apng_sequence_numbers": [],
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "rgba_split_idat",
      "description": "Static truecolor-alpha PNG with consecutive split IDAT chunks.",
      "png_file_name": "slip_gray_stable_rgba_split_idat.png",
      "png_hash": "sha256:08e130e313c7096af26cbac7e7fb2ea22e0376a74785eb5ad9721e220c8823fc",
      "validation": {
        "ok": true,
        "case_id": "rgba_split_idat",
        "chunks": [
          "IHDR",
          "IDAT",
          "IDAT",
          "IEND"
        ],
        "chunk_count": 4,
        "idat_count": 2,
        "color_type": 6,
        "bit_depth": 8,
        "interlace_method": 0,
        "apng_sequence_numbers": [],
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "indexed_plte_trns",
      "description": "Indexed-color PNG with PLTE before tRNS before IDAT.",
      "png_file_name": "slip_gray_stable_indexed_plte_trns.png",
      "png_hash": "sha256:1fa2edee14569d13e535d1da418d2888d5da075bef8d4739e830c7f93eb70b67",
      "validation": {
        "ok": true,
        "case_id": "indexed_plte_trns",
        "chunks": [
          "IHDR",
          "PLTE",
          "tRNS",
          "IDAT",
          "IEND"
        ],
        "chunk_count": 5,
        "idat_count": 1,
        "color_type": 3,
        "bit_depth": 8,
        "interlace_method": 0,
        "apng_sequence_numbers": [],
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "apng_static_first_frame",
      "description": "APNG with acTL before IDAT, fcTL sequence 0 on the static first frame, and fdAT for the second frame.",
      "png_file_name": "slip_gray_stable_apng_static_first_frame.png",
      "png_hash": "sha256:90d9571e27f879673e5739290eecdb5f9fa1afff0a072eb8e6d073d3d7ea7d82",
      "validation": {
        "ok": true,
        "case_id": "apng_static_first_frame",
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "IEND"
        ],
        "chunk_count": 7,
        "idat_count": 1,
        "color_type": 6,
        "bit_depth": 8,
        "interlace_method": 0,
        "apng_sequence_numbers": [
          0,
          1,
          2
        ],
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "static_rgba_single_idat",
      "description": "Static truecolor-alpha PNG with IHDR, one IDAT, and IEND.",
      "png_file_name": "slip_amber_social_static_rgba_single_idat.png",
      "png_hash": "sha256:caa3b67b904d9bdadd1ebe8821e196ec297ffbd4acc1086567f98c61502db8c1",
      "validation": {
        "ok": true,
        "case_id": "static_rgba_single_idat",
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "chunk_count": 3,
        "idat_count": 1,
        "color_type": 6,
        "bit_depth": 8,
        "interlace_method": 0,
        "apng_sequence_numbers": [],
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "rgba_split_idat",
      "description": "Static truecolor-alpha PNG with consecutive split IDAT chunks.",
      "png_file_name": "slip_amber_social_rgba_split_idat.png",
      "png_hash": "sha256:0cace885f604c830c7408705098406615107b5ff5d76a937b482437dfbfcca70",
      "validation": {
        "ok": true,
        "case_id": "rgba_split_idat",
        "chunks": [
          "IHDR",
          "IDAT",
          "IDAT",
          "IEND"
        ],
        "chunk_count": 4,
        "idat_count": 2,
        "color_type": 6,
        "bit_depth": 8,
        "interlace_method": 0,
        "apng_sequence_numbers": [],
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "indexed_plte_trns",
      "description": "Indexed-color PNG with PLTE before tRNS before IDAT.",
      "png_file_name": "slip_amber_social_indexed_plte_trns.png",
      "png_hash": "sha256:69d7d378811f569049a08ad9656c0515d2046dc97a4afd20148ec128a95ad509",
      "validation": {
        "ok": true,
        "case_id": "indexed_plte_trns",
        "chunks": [
          "IHDR",
          "PLTE",
          "tRNS",
          "IDAT",
          "IEND"
        ],
        "chunk_count": 5,
        "idat_count": 1,
        "color_type": 3,
        "bit_depth": 8,
        "interlace_method": 0,
        "apng_sequence_numbers": [],
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "apng_static_first_frame",
      "description": "APNG with acTL before IDAT, fcTL sequence 0 on the static first frame, and fdAT for the second frame.",
      "png_file_name": "slip_amber_social_apng_static_first_frame.png",
      "png_hash": "sha256:6d1a5e11e6f868cca5e06b29524f7ecaf177c90498189d4e6404d9c6107bf17b",
      "validation": {
        "ok": true,
        "case_id": "apng_static_first_frame",
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "IEND"
        ],
        "chunk_count": 7,
        "idat_count": 1,
        "color_type": 6,
        "bit_depth": 8,
        "interlace_method": 0,
        "apng_sequence_numbers": [
          0,
          1,
          2
        ],
        "errors": [],
        "error_families": []
      }
    }
  ],
  "invalid_probe_results": [
    {
      "probe_id": "duplicate_ihdr",
      "expected_family": "png_ihdr_duplicate",
      "rejected": true,
      "validation": {
        "ok": false,
        "case_id": "invalid",
        "chunks": [
          "IHDR",
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "errors": [
          {
            "path": "png.chunk_order",
            "family": "png_ihdr_duplicate",
            "message": "PNG must contain exactly one IHDR chunk"
          }
        ],
        "error_families": [
          "png_ihdr_duplicate"
        ]
      }
    },
    {
      "probe_id": "chunk_after_iend",
      "expected_family": "png_iend_not_last",
      "rejected": true,
      "validation": {
        "ok": false,
        "case_id": "invalid",
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND",
          "tEXt"
        ],
        "errors": [
          {
            "path": "png.chunk_order",
            "family": "png_iend_not_last",
            "message": "IEND must be the final chunk"
          }
        ],
        "error_families": [
          "png_iend_not_last"
        ]
      }
    },
    {
      "probe_id": "plte_after_idat",
      "expected_family": "png_plte_after_idat",
      "rejected": true,
      "validation": {
        "ok": false,
        "case_id": "invalid",
        "chunks": [
          "IHDR",
          "tRNS",
          "IDAT",
          "PLTE",
          "IEND"
        ],
        "errors": [
          {
            "path": "png.chunk_order",
            "family": "png_plte_after_idat",
            "message": "PLTE must appear before the first IDAT"
          }
        ],
        "error_families": [
          "png_plte_after_idat"
        ]
      }
    },
    {
      "probe_id": "trns_before_plte",
      "expected_family": "png_trns_before_plte",
      "rejected": true,
      "validation": {
        "ok": false,
        "case_id": "invalid",
        "chunks": [
          "IHDR",
          "tRNS",
          "PLTE",
          "IDAT",
          "IEND"
        ],
        "errors": [
          {
            "path": "png.chunk_order",
            "family": "png_trns_before_plte",
            "message": "tRNS must appear after PLTE when PLTE is present"
          }
        ],
        "error_families": [
          "png_trns_before_plte"
        ]
      }
    },
    {
      "probe_id": "idat_not_consecutive",
      "expected_family": "png_idat_not_consecutive",
      "rejected": true,
      "validation": {
        "ok": false,
        "case_id": "invalid",
        "chunks": [
          "IHDR",
          "IDAT",
          "tEXt",
          "IDAT",
          "IEND"
        ],
        "errors": [
          {
            "path": "png.chunk_order",
            "family": "png_idat_not_consecutive",
            "message": "multiple IDAT chunks must be consecutive"
          }
        ],
        "error_families": [
          "png_idat_not_consecutive"
        ]
      }
    },
    {
      "probe_id": "actl_after_idat",
      "expected_family": "apng_actl_after_idat",
      "rejected": true,
      "validation": {
        "ok": false,
        "case_id": "invalid",
        "chunks": [
          "IHDR",
          "fcTL",
          "IDAT",
          "acTL",
          "fcTL",
          "fdAT",
          "IEND"
        ],
        "errors": [
          {
            "path": "png.chunk_order",
            "family": "apng_actl_after_idat",
            "message": "acTL must appear before the first IDAT"
          }
        ],
        "error_families": [
          "apng_actl_after_idat"
        ]
      }
    },
    {
      "probe_id": "fctl_sequence_gap",
      "expected_family": "apng_sequence_number_gap",
      "rejected": true,
      "validation": {
        "ok": false,
        "case_id": "invalid",
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "IEND"
        ],
        "errors": [
          {
            "path": "png.chunk_order",
            "family": "apng_sequence_number_gap",
            "message": "APNG sequence numbers must ascend without gaps or duplicates"
          }
        ],
        "error_families": [
          "apng_sequence_number_gap"
        ]
      }
    }
  ]
};
