window.MECHAGOTCHI_APNG_PARTIAL_FRAME_PLAYBACK = {
  "report": {
    "artifact_id": "apng_partial_frame_playback_stage0",
    "status": "research_apng_partial_frame_playback_no_package_code",
    "profile_count": 3,
    "playback_scenario_ids": [
      "source_patch_dispose_none",
      "over_patch_dispose_none",
      "background_disposal",
      "previous_disposal"
    ],
    "playback_case_count": 12,
    "playback_case_success_count": 12,
    "invalid_probe_count": 5,
    "invalid_probe_rejected_count": 5,
    "metrics": {
      "playback_case_success_rate": 1.0,
      "invalid_probe_rejection_rate": 1.0,
      "profile_coverage": 3,
      "scenario_family_count": 4
    },
    "closed_states": [
      "apng_partial_frame_offset_playback",
      "apng_blend_source_over_playback",
      "apng_dispose_background_previous_playback",
      "apng_partial_frame_invalid_control_rejection"
    ],
    "blocked_states": [
      "full_apng_png_conformance",
      "live_external_editor_rewrite_validation",
      "production_import_export_carrier_selection_final_decision",
      "manual_readability_calibration",
      "package_runtime_lifecycle_integration"
    ],
    "decision": "prototype_apng_partial_frame_playback_subset"
  },
  "playback_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "scenario_id": "source_patch_dispose_none",
      "png_file_name": "slip_lcd_seed_source_patch_dispose_none.png",
      "png_hash": "sha256:5012f2bbf70e975ecd01098e6368b88d166d1fdeec632d102867918242ed93ff",
      "decoded": {
        "ok": true,
        "canvas_width": 8,
        "canvas_height": 8,
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
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
            "full_canvas": true,
            "pixel_hash": "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417"
          },
          {
            "frame_index": 1,
            "width": 3,
            "height": 3,
            "x_offset": 1,
            "y_offset": 1,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:900ed1fe8ee51b9fbf3be4e07683b8403bb4992125db40768e87bbbc38dd55fe"
          }
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:03191affee60b0f6f89905968b4688c28d38c9ffe30537429a6429088db339f8"
        ],
        "after_dispose_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:03191affee60b0f6f89905968b4688c28d38c9ffe30537429a6429088db339f8"
        ],
        "final_output_hash": "sha256:03191affee60b0f6f89905968b4688c28d38c9ffe30537429a6429088db339f8"
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "scenario_id": "over_patch_dispose_none",
      "png_file_name": "slip_lcd_seed_over_patch_dispose_none.png",
      "png_hash": "sha256:9e9ec93209111f7b3dfff0858927f7123cf8704c3c7f92eaa6d64ef999181dd9",
      "decoded": {
        "ok": true,
        "canvas_width": 8,
        "canvas_height": 8,
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
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
            "full_canvas": true,
            "pixel_hash": "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417"
          },
          {
            "frame_index": 1,
            "width": 3,
            "height": 3,
            "x_offset": 1,
            "y_offset": 1,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 1,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:5333b55009427937c46549626c13ca196ee496a04d8984c16ee3a83874423bf7"
          }
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:683db15e7150e5bee0a65de0afc708f69413447c8d12e7e906fcc24659a4e0ea"
        ],
        "after_dispose_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:683db15e7150e5bee0a65de0afc708f69413447c8d12e7e906fcc24659a4e0ea"
        ],
        "final_output_hash": "sha256:683db15e7150e5bee0a65de0afc708f69413447c8d12e7e906fcc24659a4e0ea"
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "scenario_id": "background_disposal",
      "png_file_name": "slip_lcd_seed_background_disposal.png",
      "png_hash": "sha256:8fb2bf2fd79d42a7a5ca425d90f4cbac873965fbe866c6314a1a538264185873",
      "decoded": {
        "ok": true,
        "canvas_width": 8,
        "canvas_height": 8,
        "animation_control": {
          "num_frames": 3,
          "num_plays": 0
        },
        "frame_count": 3,
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
            "full_canvas": true,
            "pixel_hash": "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417"
          },
          {
            "frame_index": 1,
            "width": 3,
            "height": 3,
            "x_offset": 1,
            "y_offset": 1,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 1,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:900ed1fe8ee51b9fbf3be4e07683b8403bb4992125db40768e87bbbc38dd55fe"
          },
          {
            "frame_index": 2,
            "width": 3,
            "height": 3,
            "x_offset": 3,
            "y_offset": 3,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:9d2f44972cfe335f812e5e93f76560d148defb99512c951162d9a7860e4df74f"
          }
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fcTL",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:03191affee60b0f6f89905968b4688c28d38c9ffe30537429a6429088db339f8",
          "sha256:726fa02c7ae49c19c32b32303c0159b2b518d8f647a1c5509e08db9cde674180"
        ],
        "after_dispose_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:e653c93d90123690742060fcbafac219369ccc85ab823584e067d116b982f531",
          "sha256:726fa02c7ae49c19c32b32303c0159b2b518d8f647a1c5509e08db9cde674180"
        ],
        "final_output_hash": "sha256:726fa02c7ae49c19c32b32303c0159b2b518d8f647a1c5509e08db9cde674180"
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "scenario_id": "previous_disposal",
      "png_file_name": "slip_lcd_seed_previous_disposal.png",
      "png_hash": "sha256:e2cdc9e50ba1ae9fe9e514f9017fd7e89a357ccea4685a7451698112749f249f",
      "decoded": {
        "ok": true,
        "canvas_width": 8,
        "canvas_height": 8,
        "animation_control": {
          "num_frames": 3,
          "num_plays": 0
        },
        "frame_count": 3,
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
            "full_canvas": true,
            "pixel_hash": "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417"
          },
          {
            "frame_index": 1,
            "width": 3,
            "height": 3,
            "x_offset": 1,
            "y_offset": 1,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 2,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:900ed1fe8ee51b9fbf3be4e07683b8403bb4992125db40768e87bbbc38dd55fe"
          },
          {
            "frame_index": 2,
            "width": 3,
            "height": 3,
            "x_offset": 3,
            "y_offset": 3,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:9d2f44972cfe335f812e5e93f76560d148defb99512c951162d9a7860e4df74f"
          }
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fcTL",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:03191affee60b0f6f89905968b4688c28d38c9ffe30537429a6429088db339f8",
          "sha256:0558d2adcfb22a20e4ad7f8f82e651fab086618c1507894f0b352076a65202c9"
        ],
        "after_dispose_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:0558d2adcfb22a20e4ad7f8f82e651fab086618c1507894f0b352076a65202c9"
        ],
        "final_output_hash": "sha256:0558d2adcfb22a20e4ad7f8f82e651fab086618c1507894f0b352076a65202c9"
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "scenario_id": "source_patch_dispose_none",
      "png_file_name": "slip_gray_stable_source_patch_dispose_none.png",
      "png_hash": "sha256:67f683da2f0e9217a53fa7f6fdda70cb512b8f66a376839cdca23e0ee3b0f011",
      "decoded": {
        "ok": true,
        "canvas_width": 8,
        "canvas_height": 8,
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
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
            "full_canvas": true,
            "pixel_hash": "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0"
          },
          {
            "frame_index": 1,
            "width": 3,
            "height": 3,
            "x_offset": 1,
            "y_offset": 1,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:b29da384e8289fae45e5ef63c3ae02f18f3901fade3314630ed4354113742b6f"
          }
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:15d55006a08575d491905a43e1bc1635ebf8ad33d3b03a43e59a14d747ba4a37"
        ],
        "after_dispose_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:15d55006a08575d491905a43e1bc1635ebf8ad33d3b03a43e59a14d747ba4a37"
        ],
        "final_output_hash": "sha256:15d55006a08575d491905a43e1bc1635ebf8ad33d3b03a43e59a14d747ba4a37"
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "scenario_id": "over_patch_dispose_none",
      "png_file_name": "slip_gray_stable_over_patch_dispose_none.png",
      "png_hash": "sha256:1697d5f5d2e49278226b519652831beb1a749be959085011b9f1a8635a484cae",
      "decoded": {
        "ok": true,
        "canvas_width": 8,
        "canvas_height": 8,
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
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
            "full_canvas": true,
            "pixel_hash": "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0"
          },
          {
            "frame_index": 1,
            "width": 3,
            "height": 3,
            "x_offset": 1,
            "y_offset": 1,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 1,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:14e1bf3c30c1a9c033a6932b65d5dbf9f3a00dcd2cb474ed6f8c9e123f94882c"
          }
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:83f37947bc4ed40e1b9d7e4be195bc41f6c579d1fba910fae8e1409adac1445b"
        ],
        "after_dispose_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:83f37947bc4ed40e1b9d7e4be195bc41f6c579d1fba910fae8e1409adac1445b"
        ],
        "final_output_hash": "sha256:83f37947bc4ed40e1b9d7e4be195bc41f6c579d1fba910fae8e1409adac1445b"
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "scenario_id": "background_disposal",
      "png_file_name": "slip_gray_stable_background_disposal.png",
      "png_hash": "sha256:ab9c591477e23e9b898768f7d5278c5081fe5591024e076c893c8acadbaa6be6",
      "decoded": {
        "ok": true,
        "canvas_width": 8,
        "canvas_height": 8,
        "animation_control": {
          "num_frames": 3,
          "num_plays": 0
        },
        "frame_count": 3,
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
            "full_canvas": true,
            "pixel_hash": "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0"
          },
          {
            "frame_index": 1,
            "width": 3,
            "height": 3,
            "x_offset": 1,
            "y_offset": 1,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 1,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:b29da384e8289fae45e5ef63c3ae02f18f3901fade3314630ed4354113742b6f"
          },
          {
            "frame_index": 2,
            "width": 3,
            "height": 3,
            "x_offset": 3,
            "y_offset": 3,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:8442326d581ee2e1eee00ee46748458f72242ad94cc9d4b48b762da64c4298cb"
          }
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fcTL",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:15d55006a08575d491905a43e1bc1635ebf8ad33d3b03a43e59a14d747ba4a37",
          "sha256:ef3e354dda52e14d75a1be5653e1e1b68d23673bf5e2ad75fafe328172d3342b"
        ],
        "after_dispose_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:c175d981f569daf0d26451df150e37a753307d7199b48b0aa2ff4db44fc417d0",
          "sha256:ef3e354dda52e14d75a1be5653e1e1b68d23673bf5e2ad75fafe328172d3342b"
        ],
        "final_output_hash": "sha256:ef3e354dda52e14d75a1be5653e1e1b68d23673bf5e2ad75fafe328172d3342b"
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "scenario_id": "previous_disposal",
      "png_file_name": "slip_gray_stable_previous_disposal.png",
      "png_hash": "sha256:5e386fc8e9317bd9a2cb45fdf3ba9bda5d55ea3ab5938176f4c9665089c60f9b",
      "decoded": {
        "ok": true,
        "canvas_width": 8,
        "canvas_height": 8,
        "animation_control": {
          "num_frames": 3,
          "num_plays": 0
        },
        "frame_count": 3,
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
            "full_canvas": true,
            "pixel_hash": "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0"
          },
          {
            "frame_index": 1,
            "width": 3,
            "height": 3,
            "x_offset": 1,
            "y_offset": 1,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 2,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:b29da384e8289fae45e5ef63c3ae02f18f3901fade3314630ed4354113742b6f"
          },
          {
            "frame_index": 2,
            "width": 3,
            "height": 3,
            "x_offset": 3,
            "y_offset": 3,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:8442326d581ee2e1eee00ee46748458f72242ad94cc9d4b48b762da64c4298cb"
          }
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fcTL",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:15d55006a08575d491905a43e1bc1635ebf8ad33d3b03a43e59a14d747ba4a37",
          "sha256:da2ed440c85b4a0b77b8796e0ed82ca6e8ead40a472e7b6a68548b566307de3f"
        ],
        "after_dispose_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:da2ed440c85b4a0b77b8796e0ed82ca6e8ead40a472e7b6a68548b566307de3f"
        ],
        "final_output_hash": "sha256:da2ed440c85b4a0b77b8796e0ed82ca6e8ead40a472e7b6a68548b566307de3f"
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "scenario_id": "source_patch_dispose_none",
      "png_file_name": "slip_amber_social_source_patch_dispose_none.png",
      "png_hash": "sha256:2585cb7c0ca95dda0888a1fcdbda485218d6a8319e2bc38ee211f1b433c0c5d9",
      "decoded": {
        "ok": true,
        "canvas_width": 8,
        "canvas_height": 8,
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
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
            "full_canvas": true,
            "pixel_hash": "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb"
          },
          {
            "frame_index": 1,
            "width": 3,
            "height": 3,
            "x_offset": 1,
            "y_offset": 1,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:c88166788ac6f15bc99f9c135c4dbb1893db2480b436f303aa015c5b8a096e86"
          }
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:78946983cc0edde78f545b4113dc9f593e49fdfb1c7716dbe6f52fd56069c113"
        ],
        "after_dispose_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:78946983cc0edde78f545b4113dc9f593e49fdfb1c7716dbe6f52fd56069c113"
        ],
        "final_output_hash": "sha256:78946983cc0edde78f545b4113dc9f593e49fdfb1c7716dbe6f52fd56069c113"
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "scenario_id": "over_patch_dispose_none",
      "png_file_name": "slip_amber_social_over_patch_dispose_none.png",
      "png_hash": "sha256:2798ffce5af3717fcc9c413f0d9d1f3ab4a88d2e9d879a39d424eabd317ae4d9",
      "decoded": {
        "ok": true,
        "canvas_width": 8,
        "canvas_height": 8,
        "animation_control": {
          "num_frames": 2,
          "num_plays": 0
        },
        "frame_count": 2,
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
            "full_canvas": true,
            "pixel_hash": "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb"
          },
          {
            "frame_index": 1,
            "width": 3,
            "height": 3,
            "x_offset": 1,
            "y_offset": 1,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 1,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:e3ff8c5f007adc771fefadcfbd69dded22f140a3ee914de3c45b28fb6a184f65"
          }
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:af9a3d0fb5da475a867c3b03746ab4651301d6eabbbfe35ec57d61233be6abce"
        ],
        "after_dispose_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:af9a3d0fb5da475a867c3b03746ab4651301d6eabbbfe35ec57d61233be6abce"
        ],
        "final_output_hash": "sha256:af9a3d0fb5da475a867c3b03746ab4651301d6eabbbfe35ec57d61233be6abce"
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "scenario_id": "background_disposal",
      "png_file_name": "slip_amber_social_background_disposal.png",
      "png_hash": "sha256:30a954abaf70856b5347d12a42192db4d0f722fa3a738911d0e416f638da1aa9",
      "decoded": {
        "ok": true,
        "canvas_width": 8,
        "canvas_height": 8,
        "animation_control": {
          "num_frames": 3,
          "num_plays": 0
        },
        "frame_count": 3,
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
            "full_canvas": true,
            "pixel_hash": "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb"
          },
          {
            "frame_index": 1,
            "width": 3,
            "height": 3,
            "x_offset": 1,
            "y_offset": 1,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 1,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:c88166788ac6f15bc99f9c135c4dbb1893db2480b436f303aa015c5b8a096e86"
          },
          {
            "frame_index": 2,
            "width": 3,
            "height": 3,
            "x_offset": 3,
            "y_offset": 3,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:c9210e53becb67842df95cddc7244b821860fb2a4534b18eca8d0d1c03bb0cd9"
          }
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fcTL",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:78946983cc0edde78f545b4113dc9f593e49fdfb1c7716dbe6f52fd56069c113",
          "sha256:a4cb087fbc7a43519392b43de4debbb0a395d43086bd0314b26d428db3dd299e"
        ],
        "after_dispose_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:d114cb305968bf5ae18c494b5c0c445dcd1752ddd4cc57b350b7d54a472d2ef2",
          "sha256:a4cb087fbc7a43519392b43de4debbb0a395d43086bd0314b26d428db3dd299e"
        ],
        "final_output_hash": "sha256:a4cb087fbc7a43519392b43de4debbb0a395d43086bd0314b26d428db3dd299e"
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "scenario_id": "previous_disposal",
      "png_file_name": "slip_amber_social_previous_disposal.png",
      "png_hash": "sha256:6fa9383da35a1cb46ae85cf81fb28446d42c3b7f5199089e2a94ba5c80c3632a",
      "decoded": {
        "ok": true,
        "canvas_width": 8,
        "canvas_height": 8,
        "animation_control": {
          "num_frames": 3,
          "num_plays": 0
        },
        "frame_count": 3,
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
            "full_canvas": true,
            "pixel_hash": "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb"
          },
          {
            "frame_index": 1,
            "width": 3,
            "height": 3,
            "x_offset": 1,
            "y_offset": 1,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 2,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:c88166788ac6f15bc99f9c135c4dbb1893db2480b436f303aa015c5b8a096e86"
          },
          {
            "frame_index": 2,
            "width": 3,
            "height": 3,
            "x_offset": 3,
            "y_offset": 3,
            "delay_num": 1,
            "delay_den": 10,
            "delay_ms": 100,
            "dispose_op": 0,
            "blend_op": 0,
            "data_source": "fdAT",
            "full_canvas": false,
            "pixel_hash": "sha256:c9210e53becb67842df95cddc7244b821860fb2a4534b18eca8d0d1c03bb0cd9"
          }
        ],
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fcTL",
          "fdAT"
        ],
        "display_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:78946983cc0edde78f545b4113dc9f593e49fdfb1c7716dbe6f52fd56069c113",
          "sha256:9d4ca9165b2837b6dd9e9e200a0c5d24bad040f97f8c22a0c5c095f96593185e"
        ],
        "after_dispose_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:9d4ca9165b2837b6dd9e9e200a0c5d24bad040f97f8c22a0c5c095f96593185e"
        ],
        "final_output_hash": "sha256:9d4ca9165b2837b6dd9e9e200a0c5d24bad040f97f8c22a0c5c095f96593185e"
      },
      "success": true
    }
  ],
  "invalid_probe_results": [
    {
      "probe_id": "out_of_bounds",
      "expected_family": "apng_frame_bounds_invalid",
      "rejected": true,
      "decoded": {
        "ok": false,
        "errors": [
          {
            "path": "apng.partial_frame",
            "family": "apng_frame_bounds_invalid",
            "message": "APNG frame bounds exceed the canvas"
          }
        ],
        "error_families": [
          "apng_frame_bounds_invalid"
        ]
      }
    },
    {
      "probe_id": "invalid_dispose",
      "expected_family": "apng_dispose_op_invalid",
      "rejected": true,
      "decoded": {
        "ok": false,
        "errors": [
          {
            "path": "apng.partial_frame",
            "family": "apng_dispose_op_invalid",
            "message": "APNG dispose_op must be 0, 1, or 2"
          }
        ],
        "error_families": [
          "apng_dispose_op_invalid"
        ]
      }
    },
    {
      "probe_id": "invalid_blend",
      "expected_family": "apng_blend_op_invalid",
      "rejected": true,
      "decoded": {
        "ok": false,
        "errors": [
          {
            "path": "apng.partial_frame",
            "family": "apng_blend_op_invalid",
            "message": "APNG blend_op must be 0 or 1"
          }
        ],
        "error_families": [
          "apng_blend_op_invalid"
        ]
      }
    },
    {
      "probe_id": "missing_default_idat",
      "expected_family": "apng_idat_missing",
      "rejected": true,
      "decoded": {
        "ok": false,
        "errors": [
          {
            "path": "apng.partial_frame",
            "family": "apng_idat_missing",
            "message": "APNG default IDAT chunk must be present"
          }
        ],
        "error_families": [
          "apng_idat_missing"
        ]
      }
    },
    {
      "probe_id": "missing_frame_data",
      "expected_family": "apng_frame_data_missing",
      "rejected": true,
      "decoded": {
        "ok": false,
        "errors": [
          {
            "path": "apng.partial_frame",
            "family": "apng_frame_data_missing",
            "message": "APNG frame has no image data"
          }
        ],
        "error_families": [
          "apng_frame_data_missing"
        ]
      }
    }
  ]
};
