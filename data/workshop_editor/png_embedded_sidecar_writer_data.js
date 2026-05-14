window.MECHAGOTCHI_PNG_EMBEDDED_SIDECAR_WRITER = {
  "report": {
    "artifact_id": "png_embedded_sidecar_writer_stage0",
    "status": "research_png_embedded_sidecar_writer_no_package_code",
    "profile_count": 3,
    "embedded_roundtrip_count": 3,
    "embedded_roundtrip_success_count": 3,
    "invalid_probe_count": 3,
    "invalid_probe_rejected_count": 3,
    "metrics": {
      "embedded_roundtrip_success_rate": 1.0,
      "mean_semantic_fidelity": 1.0,
      "mean_pixel_fidelity": 1.0,
      "invalid_probe_rejection_rate": 1.0
    },
    "closed_states": [
      "embedded_png_metadata_writer_text_chunk",
      "embedded_png_metadata_reader_text_chunk",
      "embedded_png_sidecar_semantic_restore",
      "embedded_png_sidecar_hash_validation"
    ],
    "blocked_states": [
      "Adam7/APNG/full PNG conformance",
      "project-file native metadata writer",
      "full project-format coverage",
      "arbitrary atlas packing",
      "tags/layers",
      "production renderer playback",
      "package runtime lifecycle integration",
      "manual readability calibration",
      "profile-weighted evolution",
      "community profile packs"
    ],
    "decision": "prototype_png_embedded_sidecar_writer"
  },
  "embedded_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "embedded_asset": {
        "asset_id": "slip_lcd_seed_constrained_000.embedded-sidecar.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-embedded-sidecar/slip_lcd_seed_constrained_000.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:38f11f840f43d1431482ff98ee514f6a5a1c54752bacd2002d4c7dc9842ec02a",
        "semantic_policy": "embedded_sidecar_required"
      },
      "canonical_asset": {
        "asset_id": "slip_lcd_seed_constrained_000.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/standard-image/slip_lcd_seed_constrained_000.png",
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
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "tEXt",
          "IDAT",
          "IEND"
        ]
      },
      "embedded_metadata": {
        "ok": true,
        "keyword": "mechagotchi.sidecar.v1",
        "metadata": {
          "metadata_model": "png_text_sidecar_v1",
          "keyword": "mechagotchi.sidecar.v1",
          "canonical_png_hash": "sha256:7ec438e0f21f3731d1746da4fdc96dc51a16299e4e1855f8a3d149a10f797877",
          "sidecar_hash": "sha256:1b4cc9655091636e8c0cb12cb58ea94bd94bfc5808b6d0dea97e9b804d61bc8d",
          "hash_note": "canonical_png_hash excludes this metadata chunk to avoid self-referential hashing"
        },
        "embedded_chunk_count": 1
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_gray_stable",
      "embedded_asset": {
        "asset_id": "slip_gray_stable_constrained_000.embedded-sidecar.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-embedded-sidecar/slip_gray_stable_constrained_000.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:51991f6ee704d4ae57a88d1f82bbabc500c1ed854722b36f673b8ddbe555ce29",
        "semantic_policy": "embedded_sidecar_required"
      },
      "canonical_asset": {
        "asset_id": "slip_gray_stable_constrained_000.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/standard-image/slip_gray_stable_constrained_000.png",
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
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "tEXt",
          "IDAT",
          "IEND"
        ]
      },
      "embedded_metadata": {
        "ok": true,
        "keyword": "mechagotchi.sidecar.v1",
        "metadata": {
          "metadata_model": "png_text_sidecar_v1",
          "keyword": "mechagotchi.sidecar.v1",
          "canonical_png_hash": "sha256:423852196fa1519d513342d2dc4ffdaa03d258fa3d22a58fe036227e386dee6c",
          "sidecar_hash": "sha256:65c8fae7d9d5f80520d80d404a869929f1aaa8c9871ff618822e165cfe6241c0",
          "hash_note": "canonical_png_hash excludes this metadata chunk to avoid self-referential hashing"
        },
        "embedded_chunk_count": 1
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    },
    {
      "profile_id": "slip_amber_social",
      "embedded_asset": {
        "asset_id": "slip_amber_social_constrained_000.embedded-sidecar.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/png-embedded-sidecar/slip_amber_social_constrained_000.png",
        "width": 8,
        "height": 8,
        "frame_count": 1,
        "content_hash": "sha256:e3395fb2d636b779ccc2e142cff1736e0336043214ec4e56f45038e5052b3f1d",
        "semantic_policy": "embedded_sidecar_required"
      },
      "canonical_asset": {
        "asset_id": "slip_amber_social_constrained_000.png",
        "format_id": "png",
        "media_type": "image/png",
        "uri": "generated://workshop/standard-image/slip_amber_social_constrained_000.png",
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
        "pixel_count": 64,
        "chunks": [
          "IHDR",
          "tEXt",
          "IDAT",
          "IEND"
        ]
      },
      "embedded_metadata": {
        "ok": true,
        "keyword": "mechagotchi.sidecar.v1",
        "metadata": {
          "metadata_model": "png_text_sidecar_v1",
          "keyword": "mechagotchi.sidecar.v1",
          "canonical_png_hash": "sha256:caa3b67b904d9bdadd1ebe8821e196ec297ffbd4acc1086567f98c61502db8c1",
          "sidecar_hash": "sha256:25c4fddeb6e9ea7898ddcbac935323eccf829efda9a1e1d9f0f5f3d30d3ddafc",
          "hash_note": "canonical_png_hash excludes this metadata chunk to avoid self-referential hashing"
        },
        "embedded_chunk_count": 1
      },
      "semantic_fidelity": 1.0,
      "pixel_fidelity": 1.0
    }
  ]
};
