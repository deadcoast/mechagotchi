window.MECHAGOTCHI_PNG_TEXTUAL_METADATA_POLICY = {
  "report": {
    "artifact_id": "png_textual_metadata_policy_stage0",
    "status": "research_png_textual_metadata_policy_no_package_code",
    "profile_count": 3,
    "textual_metadata_roundtrip_count": 12,
    "textual_metadata_roundtrip_success_count": 12,
    "invalid_probe_count": 7,
    "invalid_probe_rejected_count": 7,
    "metrics": {
      "textual_metadata_roundtrip_success_rate": 1.0,
      "mean_semantic_fidelity": 1.0,
      "mean_pixel_fidelity": 1.0,
      "invalid_probe_rejection_rate": 1.0
    },
    "closed_states": [
      "png_textual_metadata_text_ascii_policy",
      "png_textual_metadata_ztxt_compressed_policy",
      "png_textual_metadata_itxt_utf8_policy",
      "png_textual_metadata_hash_validation",
      "png_textual_metadata_invalid_probe_rejection"
    ],
    "blocked_states": [
      "live_external_editor_rewrite_validation",
      "Adam7/APNG/full PNG conformance",
      "arbitrary Aseprite project schema coverage",
      "full project-format coverage",
      "package_runtime_lifecycle_integration",
      "manual readability calibration",
      "profile_weighted_evolution",
      "community profile packs"
    ],
    "decision": "prototype_png_textual_metadata_policy"
  },
  "variant_policies": [
    {
      "variant_id": "text_ascii",
      "chunk_type": "tEXt",
      "compressed": false,
      "encoding_policy": "ascii_json_in_latin1_text_chunk"
    },
    {
      "variant_id": "ztxt_ascii",
      "chunk_type": "zTXt",
      "compressed": true,
      "encoding_policy": "ascii_json_in_latin1_ztxt_chunk"
    },
    {
      "variant_id": "itxt_utf8",
      "chunk_type": "iTXt",
      "compressed": false,
      "encoding_policy": "utf8_json_in_itxt_chunk"
    },
    {
      "variant_id": "itxt_utf8_compressed",
      "chunk_type": "iTXt",
      "compressed": true,
      "encoding_policy": "utf8_json_in_itxt_chunk"
    }
  ],
  "textual_metadata_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "text_ascii",
      "chunk_type": "tEXt",
      "encoding_policy": "ascii_json_in_latin1_text_chunk",
      "compressed": false,
      "png_file_name": "slip_lcd_seed_text_ascii.png",
      "metadata": {
        "metadata_model": "png_textual_metadata_policy_v1",
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "text_ascii",
        "chunk_type": "tEXt",
        "encoding_policy": "ascii_json_in_latin1_text_chunk",
        "compressed": false,
        "canonical_png_hash": "sha256:7ec438e0f21f3731d1746da4fdc96dc51a16299e4e1855f8a3d149a10f797877",
        "sidecar_hash": "sha256:b71539696df90d53def583112f446d9afd5b72ba50232faf1fb582dd1d5191f9",
        "ascii_probe": "cafe ascii metadata",
        "unicode_probe": "caf\u00e9 \u0394 metadata",
        "hash_note": "canonical_png_hash excludes Mechagotchi textual metadata chunks"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "tEXt",
          "IDAT",
          "IEND"
        ]
      },
      "metadata_policy": {
        "ok": true,
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "text_ascii",
        "chunk_type": "tEXt",
        "encoding_policy": "ascii_json_in_latin1_text_chunk",
        "compressed": false,
        "metadata_model": "png_textual_metadata_policy_v1",
        "textual_chunk_count": 1,
        "unicode_metadata_supported": false,
        "live_external_editor_verified": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "ztxt_ascii",
      "chunk_type": "zTXt",
      "encoding_policy": "ascii_json_in_latin1_ztxt_chunk",
      "compressed": true,
      "png_file_name": "slip_lcd_seed_ztxt_ascii.png",
      "metadata": {
        "metadata_model": "png_textual_metadata_policy_v1",
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "ztxt_ascii",
        "chunk_type": "zTXt",
        "encoding_policy": "ascii_json_in_latin1_ztxt_chunk",
        "compressed": true,
        "canonical_png_hash": "sha256:7ec438e0f21f3731d1746da4fdc96dc51a16299e4e1855f8a3d149a10f797877",
        "sidecar_hash": "sha256:b71539696df90d53def583112f446d9afd5b72ba50232faf1fb582dd1d5191f9",
        "ascii_probe": "cafe ascii metadata",
        "unicode_probe": "caf\u00e9 \u0394 metadata",
        "hash_note": "canonical_png_hash excludes Mechagotchi textual metadata chunks"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "zTXt",
          "IDAT",
          "IEND"
        ]
      },
      "metadata_policy": {
        "ok": true,
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "ztxt_ascii",
        "chunk_type": "zTXt",
        "encoding_policy": "ascii_json_in_latin1_ztxt_chunk",
        "compressed": true,
        "metadata_model": "png_textual_metadata_policy_v1",
        "textual_chunk_count": 1,
        "unicode_metadata_supported": false,
        "live_external_editor_verified": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "itxt_utf8",
      "chunk_type": "iTXt",
      "encoding_policy": "utf8_json_in_itxt_chunk",
      "compressed": false,
      "png_file_name": "slip_lcd_seed_itxt_utf8.png",
      "metadata": {
        "metadata_model": "png_textual_metadata_policy_v1",
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "itxt_utf8",
        "chunk_type": "iTXt",
        "encoding_policy": "utf8_json_in_itxt_chunk",
        "compressed": false,
        "canonical_png_hash": "sha256:7ec438e0f21f3731d1746da4fdc96dc51a16299e4e1855f8a3d149a10f797877",
        "sidecar_hash": "sha256:b71539696df90d53def583112f446d9afd5b72ba50232faf1fb582dd1d5191f9",
        "ascii_probe": "cafe ascii metadata",
        "unicode_probe": "caf\u00e9 \u0394 metadata",
        "hash_note": "canonical_png_hash excludes Mechagotchi textual metadata chunks"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "iTXt",
          "IDAT",
          "IEND"
        ]
      },
      "metadata_policy": {
        "ok": true,
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "itxt_utf8",
        "chunk_type": "iTXt",
        "encoding_policy": "utf8_json_in_itxt_chunk",
        "compressed": false,
        "metadata_model": "png_textual_metadata_policy_v1",
        "textual_chunk_count": 1,
        "unicode_metadata_supported": true,
        "live_external_editor_verified": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_lcd_seed",
      "variant_id": "itxt_utf8_compressed",
      "chunk_type": "iTXt",
      "encoding_policy": "utf8_json_in_itxt_chunk",
      "compressed": true,
      "png_file_name": "slip_lcd_seed_itxt_utf8_compressed.png",
      "metadata": {
        "metadata_model": "png_textual_metadata_policy_v1",
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "itxt_utf8_compressed",
        "chunk_type": "iTXt",
        "encoding_policy": "utf8_json_in_itxt_chunk",
        "compressed": true,
        "canonical_png_hash": "sha256:7ec438e0f21f3731d1746da4fdc96dc51a16299e4e1855f8a3d149a10f797877",
        "sidecar_hash": "sha256:b71539696df90d53def583112f446d9afd5b72ba50232faf1fb582dd1d5191f9",
        "ascii_probe": "cafe ascii metadata",
        "unicode_probe": "caf\u00e9 \u0394 metadata",
        "hash_note": "canonical_png_hash excludes Mechagotchi textual metadata chunks"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "iTXt",
          "IDAT",
          "IEND"
        ]
      },
      "metadata_policy": {
        "ok": true,
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "itxt_utf8_compressed",
        "chunk_type": "iTXt",
        "encoding_policy": "utf8_json_in_itxt_chunk",
        "compressed": true,
        "metadata_model": "png_textual_metadata_policy_v1",
        "textual_chunk_count": 1,
        "unicode_metadata_supported": true,
        "live_external_editor_verified": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "text_ascii",
      "chunk_type": "tEXt",
      "encoding_policy": "ascii_json_in_latin1_text_chunk",
      "compressed": false,
      "png_file_name": "slip_gray_stable_text_ascii.png",
      "metadata": {
        "metadata_model": "png_textual_metadata_policy_v1",
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "text_ascii",
        "chunk_type": "tEXt",
        "encoding_policy": "ascii_json_in_latin1_text_chunk",
        "compressed": false,
        "canonical_png_hash": "sha256:423852196fa1519d513342d2dc4ffdaa03d258fa3d22a58fe036227e386dee6c",
        "sidecar_hash": "sha256:b31590e11aadfaa9fb86adfe2955dd5fb342241ec95cbf9afc1385212202624f",
        "ascii_probe": "cafe ascii metadata",
        "unicode_probe": "caf\u00e9 \u0394 metadata",
        "hash_note": "canonical_png_hash excludes Mechagotchi textual metadata chunks"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "tEXt",
          "IDAT",
          "IEND"
        ]
      },
      "metadata_policy": {
        "ok": true,
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "text_ascii",
        "chunk_type": "tEXt",
        "encoding_policy": "ascii_json_in_latin1_text_chunk",
        "compressed": false,
        "metadata_model": "png_textual_metadata_policy_v1",
        "textual_chunk_count": 1,
        "unicode_metadata_supported": false,
        "live_external_editor_verified": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "ztxt_ascii",
      "chunk_type": "zTXt",
      "encoding_policy": "ascii_json_in_latin1_ztxt_chunk",
      "compressed": true,
      "png_file_name": "slip_gray_stable_ztxt_ascii.png",
      "metadata": {
        "metadata_model": "png_textual_metadata_policy_v1",
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "ztxt_ascii",
        "chunk_type": "zTXt",
        "encoding_policy": "ascii_json_in_latin1_ztxt_chunk",
        "compressed": true,
        "canonical_png_hash": "sha256:423852196fa1519d513342d2dc4ffdaa03d258fa3d22a58fe036227e386dee6c",
        "sidecar_hash": "sha256:b31590e11aadfaa9fb86adfe2955dd5fb342241ec95cbf9afc1385212202624f",
        "ascii_probe": "cafe ascii metadata",
        "unicode_probe": "caf\u00e9 \u0394 metadata",
        "hash_note": "canonical_png_hash excludes Mechagotchi textual metadata chunks"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "zTXt",
          "IDAT",
          "IEND"
        ]
      },
      "metadata_policy": {
        "ok": true,
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "ztxt_ascii",
        "chunk_type": "zTXt",
        "encoding_policy": "ascii_json_in_latin1_ztxt_chunk",
        "compressed": true,
        "metadata_model": "png_textual_metadata_policy_v1",
        "textual_chunk_count": 1,
        "unicode_metadata_supported": false,
        "live_external_editor_verified": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "itxt_utf8",
      "chunk_type": "iTXt",
      "encoding_policy": "utf8_json_in_itxt_chunk",
      "compressed": false,
      "png_file_name": "slip_gray_stable_itxt_utf8.png",
      "metadata": {
        "metadata_model": "png_textual_metadata_policy_v1",
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "itxt_utf8",
        "chunk_type": "iTXt",
        "encoding_policy": "utf8_json_in_itxt_chunk",
        "compressed": false,
        "canonical_png_hash": "sha256:423852196fa1519d513342d2dc4ffdaa03d258fa3d22a58fe036227e386dee6c",
        "sidecar_hash": "sha256:b31590e11aadfaa9fb86adfe2955dd5fb342241ec95cbf9afc1385212202624f",
        "ascii_probe": "cafe ascii metadata",
        "unicode_probe": "caf\u00e9 \u0394 metadata",
        "hash_note": "canonical_png_hash excludes Mechagotchi textual metadata chunks"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "iTXt",
          "IDAT",
          "IEND"
        ]
      },
      "metadata_policy": {
        "ok": true,
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "itxt_utf8",
        "chunk_type": "iTXt",
        "encoding_policy": "utf8_json_in_itxt_chunk",
        "compressed": false,
        "metadata_model": "png_textual_metadata_policy_v1",
        "textual_chunk_count": 1,
        "unicode_metadata_supported": true,
        "live_external_editor_verified": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "variant_id": "itxt_utf8_compressed",
      "chunk_type": "iTXt",
      "encoding_policy": "utf8_json_in_itxt_chunk",
      "compressed": true,
      "png_file_name": "slip_gray_stable_itxt_utf8_compressed.png",
      "metadata": {
        "metadata_model": "png_textual_metadata_policy_v1",
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "itxt_utf8_compressed",
        "chunk_type": "iTXt",
        "encoding_policy": "utf8_json_in_itxt_chunk",
        "compressed": true,
        "canonical_png_hash": "sha256:423852196fa1519d513342d2dc4ffdaa03d258fa3d22a58fe036227e386dee6c",
        "sidecar_hash": "sha256:b31590e11aadfaa9fb86adfe2955dd5fb342241ec95cbf9afc1385212202624f",
        "ascii_probe": "cafe ascii metadata",
        "unicode_probe": "caf\u00e9 \u0394 metadata",
        "hash_note": "canonical_png_hash excludes Mechagotchi textual metadata chunks"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "iTXt",
          "IDAT",
          "IEND"
        ]
      },
      "metadata_policy": {
        "ok": true,
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "itxt_utf8_compressed",
        "chunk_type": "iTXt",
        "encoding_policy": "utf8_json_in_itxt_chunk",
        "compressed": true,
        "metadata_model": "png_textual_metadata_policy_v1",
        "textual_chunk_count": 1,
        "unicode_metadata_supported": true,
        "live_external_editor_verified": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "text_ascii",
      "chunk_type": "tEXt",
      "encoding_policy": "ascii_json_in_latin1_text_chunk",
      "compressed": false,
      "png_file_name": "slip_amber_social_text_ascii.png",
      "metadata": {
        "metadata_model": "png_textual_metadata_policy_v1",
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "text_ascii",
        "chunk_type": "tEXt",
        "encoding_policy": "ascii_json_in_latin1_text_chunk",
        "compressed": false,
        "canonical_png_hash": "sha256:caa3b67b904d9bdadd1ebe8821e196ec297ffbd4acc1086567f98c61502db8c1",
        "sidecar_hash": "sha256:6a6b008d4a171f766522fe49a36de203e7fe32b7f51d7ef2c03e04ac4afe8af3",
        "ascii_probe": "cafe ascii metadata",
        "unicode_probe": "caf\u00e9 \u0394 metadata",
        "hash_note": "canonical_png_hash excludes Mechagotchi textual metadata chunks"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "tEXt",
          "IDAT",
          "IEND"
        ]
      },
      "metadata_policy": {
        "ok": true,
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "text_ascii",
        "chunk_type": "tEXt",
        "encoding_policy": "ascii_json_in_latin1_text_chunk",
        "compressed": false,
        "metadata_model": "png_textual_metadata_policy_v1",
        "textual_chunk_count": 1,
        "unicode_metadata_supported": false,
        "live_external_editor_verified": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "ztxt_ascii",
      "chunk_type": "zTXt",
      "encoding_policy": "ascii_json_in_latin1_ztxt_chunk",
      "compressed": true,
      "png_file_name": "slip_amber_social_ztxt_ascii.png",
      "metadata": {
        "metadata_model": "png_textual_metadata_policy_v1",
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "ztxt_ascii",
        "chunk_type": "zTXt",
        "encoding_policy": "ascii_json_in_latin1_ztxt_chunk",
        "compressed": true,
        "canonical_png_hash": "sha256:caa3b67b904d9bdadd1ebe8821e196ec297ffbd4acc1086567f98c61502db8c1",
        "sidecar_hash": "sha256:6a6b008d4a171f766522fe49a36de203e7fe32b7f51d7ef2c03e04ac4afe8af3",
        "ascii_probe": "cafe ascii metadata",
        "unicode_probe": "caf\u00e9 \u0394 metadata",
        "hash_note": "canonical_png_hash excludes Mechagotchi textual metadata chunks"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "zTXt",
          "IDAT",
          "IEND"
        ]
      },
      "metadata_policy": {
        "ok": true,
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "ztxt_ascii",
        "chunk_type": "zTXt",
        "encoding_policy": "ascii_json_in_latin1_ztxt_chunk",
        "compressed": true,
        "metadata_model": "png_textual_metadata_policy_v1",
        "textual_chunk_count": 1,
        "unicode_metadata_supported": false,
        "live_external_editor_verified": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "itxt_utf8",
      "chunk_type": "iTXt",
      "encoding_policy": "utf8_json_in_itxt_chunk",
      "compressed": false,
      "png_file_name": "slip_amber_social_itxt_utf8.png",
      "metadata": {
        "metadata_model": "png_textual_metadata_policy_v1",
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "itxt_utf8",
        "chunk_type": "iTXt",
        "encoding_policy": "utf8_json_in_itxt_chunk",
        "compressed": false,
        "canonical_png_hash": "sha256:caa3b67b904d9bdadd1ebe8821e196ec297ffbd4acc1086567f98c61502db8c1",
        "sidecar_hash": "sha256:6a6b008d4a171f766522fe49a36de203e7fe32b7f51d7ef2c03e04ac4afe8af3",
        "ascii_probe": "cafe ascii metadata",
        "unicode_probe": "caf\u00e9 \u0394 metadata",
        "hash_note": "canonical_png_hash excludes Mechagotchi textual metadata chunks"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "iTXt",
          "IDAT",
          "IEND"
        ]
      },
      "metadata_policy": {
        "ok": true,
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "itxt_utf8",
        "chunk_type": "iTXt",
        "encoding_policy": "utf8_json_in_itxt_chunk",
        "compressed": false,
        "metadata_model": "png_textual_metadata_policy_v1",
        "textual_chunk_count": 1,
        "unicode_metadata_supported": true,
        "live_external_editor_verified": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "variant_id": "itxt_utf8_compressed",
      "chunk_type": "iTXt",
      "encoding_policy": "utf8_json_in_itxt_chunk",
      "compressed": true,
      "png_file_name": "slip_amber_social_itxt_utf8_compressed.png",
      "metadata": {
        "metadata_model": "png_textual_metadata_policy_v1",
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "itxt_utf8_compressed",
        "chunk_type": "iTXt",
        "encoding_policy": "utf8_json_in_itxt_chunk",
        "compressed": true,
        "canonical_png_hash": "sha256:caa3b67b904d9bdadd1ebe8821e196ec297ffbd4acc1086567f98c61502db8c1",
        "sidecar_hash": "sha256:6a6b008d4a171f766522fe49a36de203e7fe32b7f51d7ef2c03e04ac4afe8af3",
        "ascii_probe": "cafe ascii metadata",
        "unicode_probe": "caf\u00e9 \u0394 metadata",
        "hash_note": "canonical_png_hash excludes Mechagotchi textual metadata chunks"
      },
      "decoded_png": {
        "width": 8,
        "height": 8,
        "bit_depth": 8,
        "color_type": 6,
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "iTXt",
          "IDAT",
          "IEND"
        ]
      },
      "metadata_policy": {
        "ok": true,
        "keyword": "mechagotchi.sidecar.v1",
        "variant_id": "itxt_utf8_compressed",
        "chunk_type": "iTXt",
        "encoding_policy": "utf8_json_in_itxt_chunk",
        "compressed": true,
        "metadata_model": "png_textual_metadata_policy_v1",
        "textual_chunk_count": 1,
        "unicode_metadata_supported": true,
        "live_external_editor_verified": false
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    }
  ]
};
