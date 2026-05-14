window.MECHAGOTCHI_PNG_PRIVATE_CHUNK_PRESERVATION_MATRIX = {
  "report": {
    "artifact_id": "png_private_chunk_preservation_matrix_stage0",
    "status": "research_png_private_chunk_preservation_matrix_no_package_code",
    "profile_count": 3,
    "scenario_count": 6,
    "matrix_result_count": 18,
    "expected_outcome_match_count": 18,
    "recoverable_import_count": 6,
    "missing_metadata_count": 6,
    "stale_private_chunk_rejection_count": 6,
    "strict_ancillary_rejection_count": 3,
    "metrics": {
      "expected_outcome_match_rate": 1.0,
      "recoverable_import_rate": 0.333333,
      "metadata_loss_rate": 0.333333,
      "stale_private_chunk_rejection_rate": 0.333333,
      "strict_ancillary_rejection_rate": 0.166667,
      "recoverable_semantic_fidelity_mean": 1.0,
      "recoverable_pixel_fidelity_mean": 1.0,
      "live_external_editor_verified": false
    },
    "closed_states": [
      "png_private_chunk_editor_preservation_matrix_simulated",
      "png_private_chunk_exact_preservation_gate",
      "png_private_chunk_stale_unsafe_copy_rejection_gate",
      "png_private_chunk_metadata_loss_detection_gate",
      "png_private_chunk_mechagotchi_rebind_gate"
    ],
    "blocked_states": [
      "live_external_editor_rewrite_validation",
      "final_png_production_carrier_selection",
      "APNG/full PNG conformance",
      "package_runtime_lifecycle_integration",
      "manual_readability_calibration",
      "profile_weighted_evolution"
    ],
    "decision": "prototype_png_private_chunk_preservation_matrix"
  },
  "scenario_policies": [
    {
      "scenario_id": "preserve_exact_bytes",
      "editor_model": "identity_open_save_preserves_all_bytes",
      "critical_image_data_changed": false,
      "private_chunk_preserved": true,
      "mechagotchi_metadata_aware": false,
      "spec_copy_class": "no_editor_change",
      "expected_outcome": "private_chunk_preserved_valid"
    },
    {
      "scenario_id": "strip_private_without_visual_change",
      "editor_model": "metadata_stripping_open_save_without_visual_change",
      "critical_image_data_changed": false,
      "private_chunk_preserved": false,
      "mechagotchi_metadata_aware": false,
      "spec_copy_class": "unknown_private_chunk_dropped",
      "expected_outcome": "private_chunk_missing_after_editor_save"
    },
    {
      "scenario_id": "preserve_private_after_ancillary_append",
      "editor_model": "ancillary_metadata_append_preserves_unknown_private_chunk",
      "critical_image_data_changed": false,
      "private_chunk_preserved": true,
      "mechagotchi_metadata_aware": false,
      "spec_copy_class": "safe_to_copy_allowed_by_png_but_strict_hash_bound",
      "expected_outcome": "strict_hash_rejects_ancillary_change"
    },
    {
      "scenario_id": "strip_private_after_lossless_reencode",
      "editor_model": "lossless_reencode_drops_unknown_private_chunk",
      "critical_image_data_changed": true,
      "private_chunk_preserved": false,
      "mechagotchi_metadata_aware": false,
      "spec_copy_class": "unsafe_to_copy_dropped_after_critical_change",
      "expected_outcome": "private_chunk_missing_after_editor_save"
    },
    {
      "scenario_id": "preserve_private_after_lossless_reencode",
      "editor_model": "lossless_reencode_incorrectly_copies_unknown_unsafe_private_chunk",
      "critical_image_data_changed": true,
      "private_chunk_preserved": true,
      "mechagotchi_metadata_aware": false,
      "spec_copy_class": "unsafe_to_copy_stale_copy",
      "expected_outcome": "stale_private_chunk_rejected"
    },
    {
      "scenario_id": "mechagotchi_rebind_after_lossless_reencode",
      "editor_model": "metadata_aware_lossless_reencode_rebinds_private_chunk",
      "critical_image_data_changed": true,
      "private_chunk_preserved": true,
      "mechagotchi_metadata_aware": true,
      "spec_copy_class": "recognized_application_rewrites_binding",
      "expected_outcome": "private_chunk_rebound_valid"
    }
  ],
  "matrix_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "scenario_id": "preserve_exact_bytes",
      "expected_outcome": "private_chunk_preserved_valid",
      "actual_outcome": "private_chunk_preserved_valid",
      "expected_outcome_matched": true,
      "byte_changed": false,
      "chunk_sequence": [
        "IHDR",
        "mgOT",
        "IDAT",
        "IEND"
      ],
      "import_result": {
        "ok": true,
        "private_chunk_policy": {
          "ok": true,
          "chunk_type": "mgOT",
          "magic": "mechagotchi.private_chunk.v1",
          "private_chunk_policy": "ancillary_private_unsafe_to_copy_with_magic_prefix",
          "ancillary": true,
          "private": true,
          "reserved_bit_valid": true,
          "safe_to_copy": false,
          "private_chunk_count": 1,
          "live_external_editor_verified": false
        },
        "decoded_png": {
          "width": 8,
          "height": 8,
          "bit_depth": 8,
          "color_type": 6,
          "pixel_count": 64,
          "chunks": [
            "IHDR",
            "mgOT",
            "IDAT",
            "IEND"
          ]
        },
        "canonical_decoded_png": {
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
        "pixel_fidelity": 1.0,
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_lcd_seed",
      "scenario_id": "strip_private_without_visual_change",
      "expected_outcome": "private_chunk_missing_after_editor_save",
      "actual_outcome": "private_chunk_missing_after_editor_save",
      "expected_outcome_matched": true,
      "byte_changed": true,
      "chunk_sequence": [
        "IHDR",
        "IDAT",
        "IEND"
      ],
      "import_result": {
        "ok": false,
        "private_chunk_policy": null,
        "decoded_png": null,
        "canonical_decoded_png": null,
        "semantic_fidelity": 0.0,
        "pixel_fidelity": 0.0,
        "errors": [
          {
            "path": "png.private_chunk",
            "family": "png_private_chunk_missing",
            "message": "PNG does not contain a Mechagotchi private metadata chunk"
          }
        ],
        "error_families": [
          "png_private_chunk_missing"
        ]
      }
    },
    {
      "profile_id": "slip_lcd_seed",
      "scenario_id": "preserve_private_after_ancillary_append",
      "expected_outcome": "strict_hash_rejects_ancillary_change",
      "actual_outcome": "strict_hash_rejects_ancillary_change",
      "expected_outcome_matched": true,
      "byte_changed": true,
      "chunk_sequence": [
        "IHDR",
        "mgOT",
        "IDAT",
        "vpAg",
        "IEND"
      ],
      "import_result": {
        "ok": false,
        "private_chunk_policy": null,
        "decoded_png": null,
        "canonical_decoded_png": null,
        "semantic_fidelity": 0.0,
        "pixel_fidelity": 0.0,
        "errors": [
          {
            "path": "png.private_chunk",
            "family": "png_private_chunk_canonical_hash_mismatch",
            "message": "PNG private chunk canonical PNG hash does not match PNG without private metadata chunks"
          }
        ],
        "error_families": [
          "png_private_chunk_canonical_hash_mismatch"
        ]
      }
    },
    {
      "profile_id": "slip_lcd_seed",
      "scenario_id": "strip_private_after_lossless_reencode",
      "expected_outcome": "private_chunk_missing_after_editor_save",
      "actual_outcome": "private_chunk_missing_after_editor_save",
      "expected_outcome_matched": true,
      "byte_changed": true,
      "chunk_sequence": [
        "IHDR",
        "IDAT",
        "IEND"
      ],
      "import_result": {
        "ok": false,
        "private_chunk_policy": null,
        "decoded_png": null,
        "canonical_decoded_png": null,
        "semantic_fidelity": 0.0,
        "pixel_fidelity": 0.0,
        "errors": [
          {
            "path": "png.private_chunk",
            "family": "png_private_chunk_missing",
            "message": "PNG does not contain a Mechagotchi private metadata chunk"
          }
        ],
        "error_families": [
          "png_private_chunk_missing"
        ]
      }
    },
    {
      "profile_id": "slip_lcd_seed",
      "scenario_id": "preserve_private_after_lossless_reencode",
      "expected_outcome": "stale_private_chunk_rejected",
      "actual_outcome": "stale_private_chunk_rejected",
      "expected_outcome_matched": true,
      "byte_changed": true,
      "chunk_sequence": [
        "IHDR",
        "mgOT",
        "IDAT",
        "IEND"
      ],
      "import_result": {
        "ok": false,
        "private_chunk_policy": null,
        "decoded_png": null,
        "canonical_decoded_png": null,
        "semantic_fidelity": 0.0,
        "pixel_fidelity": 0.0,
        "errors": [
          {
            "path": "png.private_chunk",
            "family": "png_private_chunk_canonical_hash_mismatch",
            "message": "PNG private chunk canonical PNG hash does not match PNG without private metadata chunks"
          }
        ],
        "error_families": [
          "png_private_chunk_canonical_hash_mismatch"
        ]
      }
    },
    {
      "profile_id": "slip_lcd_seed",
      "scenario_id": "mechagotchi_rebind_after_lossless_reencode",
      "expected_outcome": "private_chunk_rebound_valid",
      "actual_outcome": "private_chunk_rebound_valid",
      "expected_outcome_matched": true,
      "byte_changed": true,
      "chunk_sequence": [
        "IHDR",
        "mgOT",
        "IDAT",
        "IEND"
      ],
      "import_result": {
        "ok": true,
        "private_chunk_policy": {
          "ok": true,
          "chunk_type": "mgOT",
          "magic": "mechagotchi.private_chunk.v1",
          "private_chunk_policy": "ancillary_private_unsafe_to_copy_with_magic_prefix",
          "ancillary": true,
          "private": true,
          "reserved_bit_valid": true,
          "safe_to_copy": false,
          "private_chunk_count": 1,
          "live_external_editor_verified": false
        },
        "decoded_png": {
          "width": 8,
          "height": 8,
          "bit_depth": 8,
          "color_type": 6,
          "pixel_count": 64,
          "chunks": [
            "IHDR",
            "mgOT",
            "IDAT",
            "IEND"
          ]
        },
        "canonical_decoded_png": {
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
        "pixel_fidelity": 1.0,
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "scenario_id": "preserve_exact_bytes",
      "expected_outcome": "private_chunk_preserved_valid",
      "actual_outcome": "private_chunk_preserved_valid",
      "expected_outcome_matched": true,
      "byte_changed": false,
      "chunk_sequence": [
        "IHDR",
        "mgOT",
        "IDAT",
        "IEND"
      ],
      "import_result": {
        "ok": true,
        "private_chunk_policy": {
          "ok": true,
          "chunk_type": "mgOT",
          "magic": "mechagotchi.private_chunk.v1",
          "private_chunk_policy": "ancillary_private_unsafe_to_copy_with_magic_prefix",
          "ancillary": true,
          "private": true,
          "reserved_bit_valid": true,
          "safe_to_copy": false,
          "private_chunk_count": 1,
          "live_external_editor_verified": false
        },
        "decoded_png": {
          "width": 8,
          "height": 8,
          "bit_depth": 8,
          "color_type": 6,
          "pixel_count": 64,
          "chunks": [
            "IHDR",
            "mgOT",
            "IDAT",
            "IEND"
          ]
        },
        "canonical_decoded_png": {
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
        "pixel_fidelity": 1.0,
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "scenario_id": "strip_private_without_visual_change",
      "expected_outcome": "private_chunk_missing_after_editor_save",
      "actual_outcome": "private_chunk_missing_after_editor_save",
      "expected_outcome_matched": true,
      "byte_changed": true,
      "chunk_sequence": [
        "IHDR",
        "IDAT",
        "IEND"
      ],
      "import_result": {
        "ok": false,
        "private_chunk_policy": null,
        "decoded_png": null,
        "canonical_decoded_png": null,
        "semantic_fidelity": 0.0,
        "pixel_fidelity": 0.0,
        "errors": [
          {
            "path": "png.private_chunk",
            "family": "png_private_chunk_missing",
            "message": "PNG does not contain a Mechagotchi private metadata chunk"
          }
        ],
        "error_families": [
          "png_private_chunk_missing"
        ]
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "scenario_id": "preserve_private_after_ancillary_append",
      "expected_outcome": "strict_hash_rejects_ancillary_change",
      "actual_outcome": "strict_hash_rejects_ancillary_change",
      "expected_outcome_matched": true,
      "byte_changed": true,
      "chunk_sequence": [
        "IHDR",
        "mgOT",
        "IDAT",
        "vpAg",
        "IEND"
      ],
      "import_result": {
        "ok": false,
        "private_chunk_policy": null,
        "decoded_png": null,
        "canonical_decoded_png": null,
        "semantic_fidelity": 0.0,
        "pixel_fidelity": 0.0,
        "errors": [
          {
            "path": "png.private_chunk",
            "family": "png_private_chunk_canonical_hash_mismatch",
            "message": "PNG private chunk canonical PNG hash does not match PNG without private metadata chunks"
          }
        ],
        "error_families": [
          "png_private_chunk_canonical_hash_mismatch"
        ]
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "scenario_id": "strip_private_after_lossless_reencode",
      "expected_outcome": "private_chunk_missing_after_editor_save",
      "actual_outcome": "private_chunk_missing_after_editor_save",
      "expected_outcome_matched": true,
      "byte_changed": true,
      "chunk_sequence": [
        "IHDR",
        "IDAT",
        "IEND"
      ],
      "import_result": {
        "ok": false,
        "private_chunk_policy": null,
        "decoded_png": null,
        "canonical_decoded_png": null,
        "semantic_fidelity": 0.0,
        "pixel_fidelity": 0.0,
        "errors": [
          {
            "path": "png.private_chunk",
            "family": "png_private_chunk_missing",
            "message": "PNG does not contain a Mechagotchi private metadata chunk"
          }
        ],
        "error_families": [
          "png_private_chunk_missing"
        ]
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "scenario_id": "preserve_private_after_lossless_reencode",
      "expected_outcome": "stale_private_chunk_rejected",
      "actual_outcome": "stale_private_chunk_rejected",
      "expected_outcome_matched": true,
      "byte_changed": true,
      "chunk_sequence": [
        "IHDR",
        "mgOT",
        "IDAT",
        "IEND"
      ],
      "import_result": {
        "ok": false,
        "private_chunk_policy": null,
        "decoded_png": null,
        "canonical_decoded_png": null,
        "semantic_fidelity": 0.0,
        "pixel_fidelity": 0.0,
        "errors": [
          {
            "path": "png.private_chunk",
            "family": "png_private_chunk_canonical_hash_mismatch",
            "message": "PNG private chunk canonical PNG hash does not match PNG without private metadata chunks"
          }
        ],
        "error_families": [
          "png_private_chunk_canonical_hash_mismatch"
        ]
      }
    },
    {
      "profile_id": "slip_gray_stable",
      "scenario_id": "mechagotchi_rebind_after_lossless_reencode",
      "expected_outcome": "private_chunk_rebound_valid",
      "actual_outcome": "private_chunk_rebound_valid",
      "expected_outcome_matched": true,
      "byte_changed": true,
      "chunk_sequence": [
        "IHDR",
        "mgOT",
        "IDAT",
        "IEND"
      ],
      "import_result": {
        "ok": true,
        "private_chunk_policy": {
          "ok": true,
          "chunk_type": "mgOT",
          "magic": "mechagotchi.private_chunk.v1",
          "private_chunk_policy": "ancillary_private_unsafe_to_copy_with_magic_prefix",
          "ancillary": true,
          "private": true,
          "reserved_bit_valid": true,
          "safe_to_copy": false,
          "private_chunk_count": 1,
          "live_external_editor_verified": false
        },
        "decoded_png": {
          "width": 8,
          "height": 8,
          "bit_depth": 8,
          "color_type": 6,
          "pixel_count": 64,
          "chunks": [
            "IHDR",
            "mgOT",
            "IDAT",
            "IEND"
          ]
        },
        "canonical_decoded_png": {
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
        "pixel_fidelity": 1.0,
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_amber_social",
      "scenario_id": "preserve_exact_bytes",
      "expected_outcome": "private_chunk_preserved_valid",
      "actual_outcome": "private_chunk_preserved_valid",
      "expected_outcome_matched": true,
      "byte_changed": false,
      "chunk_sequence": [
        "IHDR",
        "mgOT",
        "IDAT",
        "IEND"
      ],
      "import_result": {
        "ok": true,
        "private_chunk_policy": {
          "ok": true,
          "chunk_type": "mgOT",
          "magic": "mechagotchi.private_chunk.v1",
          "private_chunk_policy": "ancillary_private_unsafe_to_copy_with_magic_prefix",
          "ancillary": true,
          "private": true,
          "reserved_bit_valid": true,
          "safe_to_copy": false,
          "private_chunk_count": 1,
          "live_external_editor_verified": false
        },
        "decoded_png": {
          "width": 8,
          "height": 8,
          "bit_depth": 8,
          "color_type": 6,
          "pixel_count": 64,
          "chunks": [
            "IHDR",
            "mgOT",
            "IDAT",
            "IEND"
          ]
        },
        "canonical_decoded_png": {
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
        "pixel_fidelity": 1.0,
        "errors": [],
        "error_families": []
      }
    },
    {
      "profile_id": "slip_amber_social",
      "scenario_id": "strip_private_without_visual_change",
      "expected_outcome": "private_chunk_missing_after_editor_save",
      "actual_outcome": "private_chunk_missing_after_editor_save",
      "expected_outcome_matched": true,
      "byte_changed": true,
      "chunk_sequence": [
        "IHDR",
        "IDAT",
        "IEND"
      ],
      "import_result": {
        "ok": false,
        "private_chunk_policy": null,
        "decoded_png": null,
        "canonical_decoded_png": null,
        "semantic_fidelity": 0.0,
        "pixel_fidelity": 0.0,
        "errors": [
          {
            "path": "png.private_chunk",
            "family": "png_private_chunk_missing",
            "message": "PNG does not contain a Mechagotchi private metadata chunk"
          }
        ],
        "error_families": [
          "png_private_chunk_missing"
        ]
      }
    },
    {
      "profile_id": "slip_amber_social",
      "scenario_id": "preserve_private_after_ancillary_append",
      "expected_outcome": "strict_hash_rejects_ancillary_change",
      "actual_outcome": "strict_hash_rejects_ancillary_change",
      "expected_outcome_matched": true,
      "byte_changed": true,
      "chunk_sequence": [
        "IHDR",
        "mgOT",
        "IDAT",
        "vpAg",
        "IEND"
      ],
      "import_result": {
        "ok": false,
        "private_chunk_policy": null,
        "decoded_png": null,
        "canonical_decoded_png": null,
        "semantic_fidelity": 0.0,
        "pixel_fidelity": 0.0,
        "errors": [
          {
            "path": "png.private_chunk",
            "family": "png_private_chunk_canonical_hash_mismatch",
            "message": "PNG private chunk canonical PNG hash does not match PNG without private metadata chunks"
          }
        ],
        "error_families": [
          "png_private_chunk_canonical_hash_mismatch"
        ]
      }
    },
    {
      "profile_id": "slip_amber_social",
      "scenario_id": "strip_private_after_lossless_reencode",
      "expected_outcome": "private_chunk_missing_after_editor_save",
      "actual_outcome": "private_chunk_missing_after_editor_save",
      "expected_outcome_matched": true,
      "byte_changed": true,
      "chunk_sequence": [
        "IHDR",
        "IDAT",
        "IEND"
      ],
      "import_result": {
        "ok": false,
        "private_chunk_policy": null,
        "decoded_png": null,
        "canonical_decoded_png": null,
        "semantic_fidelity": 0.0,
        "pixel_fidelity": 0.0,
        "errors": [
          {
            "path": "png.private_chunk",
            "family": "png_private_chunk_missing",
            "message": "PNG does not contain a Mechagotchi private metadata chunk"
          }
        ],
        "error_families": [
          "png_private_chunk_missing"
        ]
      }
    },
    {
      "profile_id": "slip_amber_social",
      "scenario_id": "preserve_private_after_lossless_reencode",
      "expected_outcome": "stale_private_chunk_rejected",
      "actual_outcome": "stale_private_chunk_rejected",
      "expected_outcome_matched": true,
      "byte_changed": true,
      "chunk_sequence": [
        "IHDR",
        "mgOT",
        "IDAT",
        "IEND"
      ],
      "import_result": {
        "ok": false,
        "private_chunk_policy": null,
        "decoded_png": null,
        "canonical_decoded_png": null,
        "semantic_fidelity": 0.0,
        "pixel_fidelity": 0.0,
        "errors": [
          {
            "path": "png.private_chunk",
            "family": "png_private_chunk_canonical_hash_mismatch",
            "message": "PNG private chunk canonical PNG hash does not match PNG without private metadata chunks"
          }
        ],
        "error_families": [
          "png_private_chunk_canonical_hash_mismatch"
        ]
      }
    },
    {
      "profile_id": "slip_amber_social",
      "scenario_id": "mechagotchi_rebind_after_lossless_reencode",
      "expected_outcome": "private_chunk_rebound_valid",
      "actual_outcome": "private_chunk_rebound_valid",
      "expected_outcome_matched": true,
      "byte_changed": true,
      "chunk_sequence": [
        "IHDR",
        "mgOT",
        "IDAT",
        "IEND"
      ],
      "import_result": {
        "ok": true,
        "private_chunk_policy": {
          "ok": true,
          "chunk_type": "mgOT",
          "magic": "mechagotchi.private_chunk.v1",
          "private_chunk_policy": "ancillary_private_unsafe_to_copy_with_magic_prefix",
          "ancillary": true,
          "private": true,
          "reserved_bit_valid": true,
          "safe_to_copy": false,
          "private_chunk_count": 1,
          "live_external_editor_verified": false
        },
        "decoded_png": {
          "width": 8,
          "height": 8,
          "bit_depth": 8,
          "color_type": 6,
          "pixel_count": 64,
          "chunks": [
            "IHDR",
            "mgOT",
            "IDAT",
            "IEND"
          ]
        },
        "canonical_decoded_png": {
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
        "pixel_fidelity": 1.0,
        "errors": [],
        "error_families": []
      }
    }
  ]
};
