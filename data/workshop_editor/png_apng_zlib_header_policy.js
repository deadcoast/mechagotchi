window.MECHAGOTCHI_PNG_APNG_ZLIB_HEADER_POLICY = {
  "report": {
    "artifact_id": "png_apng_zlib_header_policy_stage0",
    "status": "research_png_apng_zlib_header_policy_no_package_code",
    "date": "2026-05-14",
    "profile_count": 3,
    "case_ids": [
      "png_zlib_window_512",
      "png_zlib_window_4096",
      "png_zlib_window_32768",
      "apng_fdat_zlib_window_512",
      "apng_fdat_zlib_window_4096",
      "apng_fdat_zlib_window_32768"
    ],
    "case_count": 18,
    "case_success_count": 18,
    "invalid_probe_count": 6,
    "invalid_probe_rejected_count": 6,
    "metrics": {
      "case_success_ratio": 1.0,
      "invalid_probe_rejection_ratio": 1.0,
      "profile_coverage": 3,
      "case_family_count": 6,
      "png_case_count": 9,
      "apng_case_count": 9,
      "zlib_cinfo_values_covered": [
        1,
        4,
        7
      ],
      "zlib_window_sizes_covered": [
        512,
        4096,
        32768
      ],
      "ihdr_compression_method_0_count": 18,
      "zlib_cm8_case_count": 18,
      "fdict_false_case_count": 18,
      "cmf_flg_check_passed_case_count": 18,
      "split_fdat_case_count": 9,
      "live_external_editor_verified": false
    },
    "closed_states": [
      "png_zlib_window_header_reconstruction",
      "apng_fdat_zlib_window_header_reconstruction",
      "png_apng_fdict_rejection",
      "png_apng_zlib_cmf_flg_error_rejection",
      "png_apng_zlib_header_policy_invalid_probe_rejection"
    ],
    "blocked_states": [
      "full_apng_png_conformance",
      "live_external_editor_rewrite_validation",
      "production_import_export_carrier_selection_final_decision",
      "manual_readability_calibration",
      "package_runtime_lifecycle_integration"
    ],
    "decision": "prototype_png_apng_zlib_header_policy_subset"
  },
  "case_summaries": [
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "png_zlib_window_512",
      "carrier_family": "png",
      "window_policy_id": "window_512",
      "window_size_bytes": 512,
      "png_file_name": "slip_lcd_seed_png_zlib_window_512.png",
      "png_hash": "sha256:0f959dff38050e5df8f4e4343241f82dad85dec1bde7a37c1783242752b6efd6",
      "decoded": {
        "ok": true,
        "carrier_family": "png",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
        "raw_image_data_hash": "sha256:67278881e3b35c10069a091535e7fba3cd769d6002e64d92ce89a46bc74a219b",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:0537128c250607bbfe5f7dba7eafb8d8d6c25f0258a400b0d48e223239abdfa3",
        "compressed_data_length": 95,
        "zlib_header": {
          "cmf": 24,
          "flg": 149,
          "compression_method": 8,
          "compression_info": 1,
          "window_size_bytes": 512,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          95
        ],
        "fdat_frame_data_lengths": [],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 0,
        "data_chunk_count": 1,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "width": 8,
        "height": 8,
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "png_zlib_window_4096",
      "carrier_family": "png",
      "window_policy_id": "window_4096",
      "window_size_bytes": 4096,
      "png_file_name": "slip_lcd_seed_png_zlib_window_4096.png",
      "png_hash": "sha256:eef484bc6326464b6bd4afde01130a12c30c660bd01a8b293db607582541f51c",
      "decoded": {
        "ok": true,
        "carrier_family": "png",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
        "raw_image_data_hash": "sha256:67278881e3b35c10069a091535e7fba3cd769d6002e64d92ce89a46bc74a219b",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:475a4db54c815516ccc66c327b30e519b81c10a275d1ec2e6dd390e58bdcd08c",
        "compressed_data_length": 95,
        "zlib_header": {
          "cmf": 72,
          "flg": 137,
          "compression_method": 8,
          "compression_info": 4,
          "window_size_bytes": 4096,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          95
        ],
        "fdat_frame_data_lengths": [],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 0,
        "data_chunk_count": 1,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "width": 8,
        "height": 8,
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "png_zlib_window_32768",
      "carrier_family": "png",
      "window_policy_id": "window_32768",
      "window_size_bytes": 32768,
      "png_file_name": "slip_lcd_seed_png_zlib_window_32768.png",
      "png_hash": "sha256:9b1473e14ec6e9713721a93bb5156b7a7df19619ca208a7a8a562f8d8ff68283",
      "decoded": {
        "ok": true,
        "carrier_family": "png",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
        "raw_image_data_hash": "sha256:67278881e3b35c10069a091535e7fba3cd769d6002e64d92ce89a46bc74a219b",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:ebf09b6ec0e2da75204544b29bbd082ae32de5baeb9a1484a30ed03b3ca31458",
        "compressed_data_length": 95,
        "zlib_header": {
          "cmf": 120,
          "flg": 156,
          "compression_method": 8,
          "compression_info": 7,
          "window_size_bytes": 32768,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          95
        ],
        "fdat_frame_data_lengths": [],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 0,
        "data_chunk_count": 1,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "width": 8,
        "height": 8,
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "apng_fdat_zlib_window_512",
      "carrier_family": "apng",
      "window_policy_id": "window_512",
      "window_size_bytes": 512,
      "png_file_name": "slip_lcd_seed_apng_fdat_zlib_window_512.png",
      "png_hash": "sha256:6cd030ceb3160a8e26db43bbb3cd0825bac67deb054544f3558113d199385dac",
      "decoded": {
        "ok": true,
        "carrier_family": "apng",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
        "raw_image_data_hash": "sha256:67278881e3b35c10069a091535e7fba3cd769d6002e64d92ce89a46bc74a219b",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:0537128c250607bbfe5f7dba7eafb8d8d6c25f0258a400b0d48e223239abdfa3",
        "compressed_data_length": 95,
        "zlib_header": {
          "cmf": 24,
          "flg": 149,
          "compression_method": 8,
          "compression_info": 1,
          "window_size_bytes": 512,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          95
        ],
        "fdat_frame_data_lengths": [
          47,
          48
        ],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 2,
        "data_chunk_count": 3,
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT",
          "IEND"
        ],
        "frame_count": 2,
        "display_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417"
        ],
        "final_output_hash": "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "apng_fdat_zlib_window_4096",
      "carrier_family": "apng",
      "window_policy_id": "window_4096",
      "window_size_bytes": 4096,
      "png_file_name": "slip_lcd_seed_apng_fdat_zlib_window_4096.png",
      "png_hash": "sha256:0b2d21da6b4eefa31a83638198f5b465a7efed66f420af46042d42ad36fc6278",
      "decoded": {
        "ok": true,
        "carrier_family": "apng",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
        "raw_image_data_hash": "sha256:67278881e3b35c10069a091535e7fba3cd769d6002e64d92ce89a46bc74a219b",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:475a4db54c815516ccc66c327b30e519b81c10a275d1ec2e6dd390e58bdcd08c",
        "compressed_data_length": 95,
        "zlib_header": {
          "cmf": 72,
          "flg": 137,
          "compression_method": 8,
          "compression_info": 4,
          "window_size_bytes": 4096,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          95
        ],
        "fdat_frame_data_lengths": [
          47,
          48
        ],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 2,
        "data_chunk_count": 3,
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT",
          "IEND"
        ],
        "frame_count": 2,
        "display_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417"
        ],
        "final_output_hash": "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_lcd_seed",
      "grid_id": "slip_lcd_seed_constrained_000",
      "case_id": "apng_fdat_zlib_window_32768",
      "carrier_family": "apng",
      "window_policy_id": "window_32768",
      "window_size_bytes": 32768,
      "png_file_name": "slip_lcd_seed_apng_fdat_zlib_window_32768.png",
      "png_hash": "sha256:f2e5f4cb3dc45283ec88c27038b4b36ed767e015c7df1e9bbc8c34c992177aec",
      "decoded": {
        "ok": true,
        "carrier_family": "apng",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
        "raw_image_data_hash": "sha256:67278881e3b35c10069a091535e7fba3cd769d6002e64d92ce89a46bc74a219b",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:ebf09b6ec0e2da75204544b29bbd082ae32de5baeb9a1484a30ed03b3ca31458",
        "compressed_data_length": 95,
        "zlib_header": {
          "cmf": 120,
          "flg": 156,
          "compression_method": 8,
          "compression_info": 7,
          "window_size_bytes": 32768,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          95
        ],
        "fdat_frame_data_lengths": [
          47,
          48
        ],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 2,
        "data_chunk_count": 3,
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT",
          "IEND"
        ],
        "frame_count": 2,
        "display_hashes": [
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
          "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417"
        ],
        "final_output_hash": "sha256:9c181bb6b445ce498b054d0c98ac2cb9cfb1bf93390f11462cc67dc386942417",
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "png_zlib_window_512",
      "carrier_family": "png",
      "window_policy_id": "window_512",
      "window_size_bytes": 512,
      "png_file_name": "slip_gray_stable_png_zlib_window_512.png",
      "png_hash": "sha256:28b109a04c430093a96ba61417933a16871da49a52a4b71d56423dd8ff98b44f",
      "decoded": {
        "ok": true,
        "carrier_family": "png",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
        "raw_image_data_hash": "sha256:50f9e746e7524124ca177ccf04b7f820e3d42de1e520ef2764ad254b12787d60",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:98cd778873f003547849873e0a43e258e8267770873256259cf2a0e87c16d1b3",
        "compressed_data_length": 102,
        "zlib_header": {
          "cmf": 24,
          "flg": 149,
          "compression_method": 8,
          "compression_info": 1,
          "window_size_bytes": 512,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          102
        ],
        "fdat_frame_data_lengths": [],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 0,
        "data_chunk_count": 1,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "width": 8,
        "height": 8,
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "png_zlib_window_4096",
      "carrier_family": "png",
      "window_policy_id": "window_4096",
      "window_size_bytes": 4096,
      "png_file_name": "slip_gray_stable_png_zlib_window_4096.png",
      "png_hash": "sha256:00008dbbd8db2a692fa034356e2ce683bb4eb4b7ba8d71f0bc1e9856835fe00f",
      "decoded": {
        "ok": true,
        "carrier_family": "png",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
        "raw_image_data_hash": "sha256:50f9e746e7524124ca177ccf04b7f820e3d42de1e520ef2764ad254b12787d60",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:56ff87b167ed8b947cd6391fe51127324803953783195f6c2a7b12f9bb90758a",
        "compressed_data_length": 102,
        "zlib_header": {
          "cmf": 72,
          "flg": 137,
          "compression_method": 8,
          "compression_info": 4,
          "window_size_bytes": 4096,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          102
        ],
        "fdat_frame_data_lengths": [],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 0,
        "data_chunk_count": 1,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "width": 8,
        "height": 8,
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "png_zlib_window_32768",
      "carrier_family": "png",
      "window_policy_id": "window_32768",
      "window_size_bytes": 32768,
      "png_file_name": "slip_gray_stable_png_zlib_window_32768.png",
      "png_hash": "sha256:cc58a133976a17479e059237421d31ad1553f05665f794e941ef5d61a6babfe5",
      "decoded": {
        "ok": true,
        "carrier_family": "png",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
        "raw_image_data_hash": "sha256:50f9e746e7524124ca177ccf04b7f820e3d42de1e520ef2764ad254b12787d60",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:cdfd6b370c981af35715767b086e9bdf3d09eac0bfb0cf4a86a55393a082a4da",
        "compressed_data_length": 102,
        "zlib_header": {
          "cmf": 120,
          "flg": 156,
          "compression_method": 8,
          "compression_info": 7,
          "window_size_bytes": 32768,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          102
        ],
        "fdat_frame_data_lengths": [],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 0,
        "data_chunk_count": 1,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "width": 8,
        "height": 8,
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "apng_fdat_zlib_window_512",
      "carrier_family": "apng",
      "window_policy_id": "window_512",
      "window_size_bytes": 512,
      "png_file_name": "slip_gray_stable_apng_fdat_zlib_window_512.png",
      "png_hash": "sha256:f05e54c683ee8f94f9da7a6684cfbeca18f25747a512e379ba9222d8c3cbf530",
      "decoded": {
        "ok": true,
        "carrier_family": "apng",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
        "raw_image_data_hash": "sha256:50f9e746e7524124ca177ccf04b7f820e3d42de1e520ef2764ad254b12787d60",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:98cd778873f003547849873e0a43e258e8267770873256259cf2a0e87c16d1b3",
        "compressed_data_length": 102,
        "zlib_header": {
          "cmf": 24,
          "flg": 149,
          "compression_method": 8,
          "compression_info": 1,
          "window_size_bytes": 512,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          102
        ],
        "fdat_frame_data_lengths": [
          51,
          51
        ],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 2,
        "data_chunk_count": 3,
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT",
          "IEND"
        ],
        "frame_count": 2,
        "display_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0"
        ],
        "final_output_hash": "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "apng_fdat_zlib_window_4096",
      "carrier_family": "apng",
      "window_policy_id": "window_4096",
      "window_size_bytes": 4096,
      "png_file_name": "slip_gray_stable_apng_fdat_zlib_window_4096.png",
      "png_hash": "sha256:7692ebbba4e03bb413a7388cd872f0b967a532e4d94164ebab10dd5931ffd7ce",
      "decoded": {
        "ok": true,
        "carrier_family": "apng",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
        "raw_image_data_hash": "sha256:50f9e746e7524124ca177ccf04b7f820e3d42de1e520ef2764ad254b12787d60",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:56ff87b167ed8b947cd6391fe51127324803953783195f6c2a7b12f9bb90758a",
        "compressed_data_length": 102,
        "zlib_header": {
          "cmf": 72,
          "flg": 137,
          "compression_method": 8,
          "compression_info": 4,
          "window_size_bytes": 4096,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          102
        ],
        "fdat_frame_data_lengths": [
          51,
          51
        ],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 2,
        "data_chunk_count": 3,
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT",
          "IEND"
        ],
        "frame_count": 2,
        "display_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0"
        ],
        "final_output_hash": "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_gray_stable",
      "grid_id": "slip_gray_stable_constrained_000",
      "case_id": "apng_fdat_zlib_window_32768",
      "carrier_family": "apng",
      "window_policy_id": "window_32768",
      "window_size_bytes": 32768,
      "png_file_name": "slip_gray_stable_apng_fdat_zlib_window_32768.png",
      "png_hash": "sha256:3561bd966cbff6b7cae589128154effbd9ce9e2c7c5ef02042b43a89f68f0da8",
      "decoded": {
        "ok": true,
        "carrier_family": "apng",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
        "raw_image_data_hash": "sha256:50f9e746e7524124ca177ccf04b7f820e3d42de1e520ef2764ad254b12787d60",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:cdfd6b370c981af35715767b086e9bdf3d09eac0bfb0cf4a86a55393a082a4da",
        "compressed_data_length": 102,
        "zlib_header": {
          "cmf": 120,
          "flg": 156,
          "compression_method": 8,
          "compression_info": 7,
          "window_size_bytes": 32768,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          102
        ],
        "fdat_frame_data_lengths": [
          51,
          51
        ],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 2,
        "data_chunk_count": 3,
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT",
          "IEND"
        ],
        "frame_count": 2,
        "display_hashes": [
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
          "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0"
        ],
        "final_output_hash": "sha256:d9bdc5be78d2111ce862360599da0401a62bebd28d1a72fea607a7fe153442f0",
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "png_zlib_window_512",
      "carrier_family": "png",
      "window_policy_id": "window_512",
      "window_size_bytes": 512,
      "png_file_name": "slip_amber_social_png_zlib_window_512.png",
      "png_hash": "sha256:f93fdf5f2994aaeceb51d32b3176d2bbbe2cbe22bb7aee2dab9273136c346b7e",
      "decoded": {
        "ok": true,
        "carrier_family": "png",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
        "raw_image_data_hash": "sha256:034c35b8178764c7a5eb66352643a39aa520ac1205d942dc52b9eba965f017ce",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:92ec96bf5f4b341380e6c2ba6a498ae3428fd41b461e3f890a4fc152201c2d74",
        "compressed_data_length": 93,
        "zlib_header": {
          "cmf": 24,
          "flg": 149,
          "compression_method": 8,
          "compression_info": 1,
          "window_size_bytes": 512,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          93
        ],
        "fdat_frame_data_lengths": [],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 0,
        "data_chunk_count": 1,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "width": 8,
        "height": 8,
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "png_zlib_window_4096",
      "carrier_family": "png",
      "window_policy_id": "window_4096",
      "window_size_bytes": 4096,
      "png_file_name": "slip_amber_social_png_zlib_window_4096.png",
      "png_hash": "sha256:c3ad0b71b0426b2bf38ffe2fc2251686ffc8c2ed0eda8787712d34d5500220cc",
      "decoded": {
        "ok": true,
        "carrier_family": "png",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
        "raw_image_data_hash": "sha256:034c35b8178764c7a5eb66352643a39aa520ac1205d942dc52b9eba965f017ce",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:dbeebcf1ebde4a0ed654368fbf097d995f4c0f320df75917e61b0038d51887a8",
        "compressed_data_length": 93,
        "zlib_header": {
          "cmf": 72,
          "flg": 137,
          "compression_method": 8,
          "compression_info": 4,
          "window_size_bytes": 4096,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          93
        ],
        "fdat_frame_data_lengths": [],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 0,
        "data_chunk_count": 1,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "width": 8,
        "height": 8,
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "png_zlib_window_32768",
      "carrier_family": "png",
      "window_policy_id": "window_32768",
      "window_size_bytes": 32768,
      "png_file_name": "slip_amber_social_png_zlib_window_32768.png",
      "png_hash": "sha256:29c56a16bf4330304963dbe4e57e8b46f61cc99e970f39f2c3aab99d63fb8a18",
      "decoded": {
        "ok": true,
        "carrier_family": "png",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
        "raw_image_data_hash": "sha256:034c35b8178764c7a5eb66352643a39aa520ac1205d942dc52b9eba965f017ce",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:328bf991929f7ed9a65dd0d0df0ba457346c3dc3c15c467030d3e1e0cb4d1421",
        "compressed_data_length": 93,
        "zlib_header": {
          "cmf": 120,
          "flg": 156,
          "compression_method": 8,
          "compression_info": 7,
          "window_size_bytes": 32768,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          93
        ],
        "fdat_frame_data_lengths": [],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 0,
        "data_chunk_count": 1,
        "chunks": [
          "IHDR",
          "IDAT",
          "IEND"
        ],
        "width": 8,
        "height": 8,
        "filter_types_seen": [
          0,
          1,
          2,
          3,
          4
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "apng_fdat_zlib_window_512",
      "carrier_family": "apng",
      "window_policy_id": "window_512",
      "window_size_bytes": 512,
      "png_file_name": "slip_amber_social_apng_fdat_zlib_window_512.png",
      "png_hash": "sha256:8866560f5f55bf27c6f1bab86385b5830db2c24eb5664b04e6c623d270b91a2d",
      "decoded": {
        "ok": true,
        "carrier_family": "apng",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
        "raw_image_data_hash": "sha256:034c35b8178764c7a5eb66352643a39aa520ac1205d942dc52b9eba965f017ce",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:92ec96bf5f4b341380e6c2ba6a498ae3428fd41b461e3f890a4fc152201c2d74",
        "compressed_data_length": 93,
        "zlib_header": {
          "cmf": 24,
          "flg": 149,
          "compression_method": 8,
          "compression_info": 1,
          "window_size_bytes": 512,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          93
        ],
        "fdat_frame_data_lengths": [
          46,
          47
        ],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 2,
        "data_chunk_count": 3,
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT",
          "IEND"
        ],
        "frame_count": 2,
        "display_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb"
        ],
        "final_output_hash": "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "apng_fdat_zlib_window_4096",
      "carrier_family": "apng",
      "window_policy_id": "window_4096",
      "window_size_bytes": 4096,
      "png_file_name": "slip_amber_social_apng_fdat_zlib_window_4096.png",
      "png_hash": "sha256:091f533b9433d4d7f7659f11d2c2f2a3cd61b9909185a56e6de03d4c11d0d327",
      "decoded": {
        "ok": true,
        "carrier_family": "apng",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
        "raw_image_data_hash": "sha256:034c35b8178764c7a5eb66352643a39aa520ac1205d942dc52b9eba965f017ce",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:dbeebcf1ebde4a0ed654368fbf097d995f4c0f320df75917e61b0038d51887a8",
        "compressed_data_length": 93,
        "zlib_header": {
          "cmf": 72,
          "flg": 137,
          "compression_method": 8,
          "compression_info": 4,
          "window_size_bytes": 4096,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          93
        ],
        "fdat_frame_data_lengths": [
          46,
          47
        ],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 2,
        "data_chunk_count": 3,
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT",
          "IEND"
        ],
        "frame_count": 2,
        "display_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb"
        ],
        "final_output_hash": "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ]
      },
      "success": true
    },
    {
      "profile_id": "slip_amber_social",
      "grid_id": "slip_amber_social_constrained_000",
      "case_id": "apng_fdat_zlib_window_32768",
      "carrier_family": "apng",
      "window_policy_id": "window_32768",
      "window_size_bytes": 32768,
      "png_file_name": "slip_amber_social_apng_fdat_zlib_window_32768.png",
      "png_hash": "sha256:6df969b6a1c62a6a478950f0ef69df9fe541532a8b473f890af0aa7ecbd99454",
      "decoded": {
        "ok": true,
        "carrier_family": "apng",
        "ihdr_compression_method": 0,
        "pixel_hash": "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
        "raw_image_data_hash": "sha256:034c35b8178764c7a5eb66352643a39aa520ac1205d942dc52b9eba965f017ce",
        "raw_image_data_length": 264,
        "compressed_data_hash": "sha256:328bf991929f7ed9a65dd0d0df0ba457346c3dc3c15c467030d3e1e0cb4d1421",
        "compressed_data_length": 93,
        "zlib_header": {
          "cmf": 120,
          "flg": 156,
          "compression_method": 8,
          "compression_info": 7,
          "window_size_bytes": 32768,
          "fdict": false,
          "flevel": 2,
          "cmf_flg_check_passed": true
        },
        "idat_data_lengths": [
          93
        ],
        "fdat_frame_data_lengths": [
          46,
          47
        ],
        "idat_chunk_count": 1,
        "fdat_chunk_count": 2,
        "data_chunk_count": 3,
        "chunks": [
          "IHDR",
          "acTL",
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT",
          "IEND"
        ],
        "frame_count": 2,
        "display_hashes": [
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
          "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb"
        ],
        "final_output_hash": "sha256:f8c5546c0f6c7f8bf95b224ab92c07cb6697ac67f460e2510a53373cbc3384bb",
        "animation_chunk_order": [
          "fcTL",
          "IDAT",
          "fcTL",
          "fdAT",
          "fdAT"
        ]
      },
      "success": true
    }
  ],
  "invalid_probe_results": [
    {
      "probe_id": "png_fdict",
      "expected_family": "png_image_data_decompression_failed",
      "ok": false,
      "error_families": [
        "png_image_data_decompression_failed"
      ],
      "error_family": "png_image_data_decompression_failed",
      "rejected": true
    },
    {
      "probe_id": "png_cmf_flg_check",
      "expected_family": "png_image_data_decompression_failed",
      "ok": false,
      "error_families": [
        "png_image_data_decompression_failed"
      ],
      "error_family": "png_image_data_decompression_failed",
      "rejected": true
    },
    {
      "probe_id": "png_reserved_cm",
      "expected_family": "png_image_data_decompression_failed",
      "ok": false,
      "error_families": [
        "png_image_data_decompression_failed"
      ],
      "error_family": "png_image_data_decompression_failed",
      "rejected": true
    },
    {
      "probe_id": "apng_fdict",
      "expected_family": "apng_frame_decompression_failed",
      "ok": false,
      "error_families": [
        "apng_frame_decompression_failed"
      ],
      "error_family": "apng_frame_decompression_failed",
      "rejected": true
    },
    {
      "probe_id": "apng_cmf_flg_check",
      "expected_family": "apng_frame_decompression_failed",
      "ok": false,
      "error_families": [
        "apng_frame_decompression_failed"
      ],
      "error_family": "apng_frame_decompression_failed",
      "rejected": true
    },
    {
      "probe_id": "apng_cinfo_too_large",
      "expected_family": "apng_frame_decompression_failed",
      "ok": false,
      "error_families": [
        "apng_frame_decompression_failed"
      ],
      "error_family": "apng_frame_decompression_failed",
      "rejected": true
    }
  ]
};
