"""Conformance tests feeding foreign, spec-derived PNG/APNG fixtures to the
workshop decoders.

The fixtures come from ``foreign_fixture_writer``, an independent encoder
written directly from the W3C PNG specification that shares no code with
the lab encoders. For every fixture x decoder pair the outcome must be
either a correct decode (pixel-verified against the writer's own reference
model) or a typed rejection carrying an error family; a raw struct/zlib/
index/decode error escaping any decoder is a genuine decoder bug.
"""

import json
import tempfile
import unittest
import zlib
from pathlib import Path

from foreign_fixture_writer import (
    build_all_fixtures,
    build_manifest,
    hash_bytes,
    write_foreign_fixture_corpus,
)
from png_adam7_deep_color_cross_product import (
    PNGAdam7DeepColorDecodeError,
    decode_png_adam7_deep_color,
)
from png_adam7_interlace_decoder import PNGAdam7DecodeError, decode_png_adam7_rgba
from png_apng_chunk_order_conformance import validate_png_apng_chunk_order
from png_apng_filtered_frame_data import decode_apng_filtered_frame_data
from png_apng_image_data_chunking import decode_png_apng_image_data_chunking
from png_apng_partial_frame_playback import decode_apng_partial_frame_playback
from png_apng_sidecar_decoder import decode_apng_frames
from png_deep_color_sidecar_decoder import (
    PNGDeepColorDecodeError,
    decode_png_deep_color,
)
from png_textual_metadata_policy import import_png_textual_metadata
from standard_image_sidecar_decoder import PNGDecodeError, decode_png_rgba


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "data" / "foreign_fixtures"

FIXTURES = build_all_fixtures()
FIXTURES_BY_ID = {fixture["fixture_id"]: fixture for fixture in FIXTURES}
MANIFEST = build_manifest(FIXTURES)

DECODERS = {
    "standard_decode_png_rgba": decode_png_rgba,
    "adam7_decode_png_adam7_rgba": decode_png_adam7_rgba,
    "apng_decode_apng_frames": decode_apng_frames,
    "apng_filtered_frame_data": decode_apng_filtered_frame_data,
    "apng_partial_frame_playback": decode_apng_partial_frame_playback,
    "image_data_chunking": decode_png_apng_image_data_chunking,
    "chunk_order_validator": validate_png_apng_chunk_order,
    "textual_metadata_import": import_png_textual_metadata,
    "deep_color_decode": decode_png_deep_color,
    "adam7_deep_color_decode": decode_png_adam7_deep_color,
}

STATIC_FILTER_FIXTURE_IDS = [
    "static_filter_sub",
    "static_filter_up",
    "static_filter_average",
    "static_filter_paeth",
    "static_filter_mixed",
]

DEEP_STATIC_FIXTURE_IDS = [
    "gray8_multi_idat_mixed_filters",
    "gray16_multi_idat_mixed_filters",
    "rgba16_basic",
    "rgba16_paeth_sub_multi_idat",
]

GRAY_DEEP_FIXTURE_IDS = DEEP_STATIC_FIXTURE_IDS + [
    "rgba16_adam7_mixed_filters_multi_idat",
]

APNG_FIXTURE_IDS = [
    "apng_basic_split_fdat",
    "apng_default_image_not_animated",
    "apng_dispose_background",
    "apng_dispose_previous",
    "apng_blend_over",
    "apng_subcanvas_regions",
    "apng_filtered_frames_split_fdat",
]


def _run_decoder(decoder_id: str, png_bytes: bytes) -> dict:
    """Normalize decoder outcomes into decode / typed_reject."""
    decoder = DECODERS[decoder_id]
    try:
        result = decoder(png_bytes)
    except ValueError as exc:
        family = getattr(exc, "family", None)
        if family is None:
            raise
        return {"outcome": "typed_reject", "families": [family], "result": None}
    if not isinstance(result, dict):
        raise AssertionError(f"{decoder_id} returned a non-dict result: {result!r}")
    if result.get("ok") is False:
        return {
            "outcome": "typed_reject",
            "families": list(result.get("error_families", [])),
            "result": result,
        }
    return {"outcome": "decode", "families": [], "result": result}


class TestForeignFixtureWriterDeterminism(unittest.TestCase):
    def test_build_all_fixtures_is_deterministic(self):
        first = build_all_fixtures()
        second = build_all_fixtures()
        self.assertEqual(
            [fixture["fixture_id"] for fixture in first],
            [fixture["fixture_id"] for fixture in second],
        )
        for one, two in zip(first, second):
            self.assertEqual(one["png_bytes"], two["png_bytes"], one["fixture_id"])
        self.assertEqual(build_manifest(first), build_manifest(second))

    def test_writer_main_writes_identical_bytes_across_runs(self):
        with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
            write_foreign_fixture_corpus(Path(first_dir))
            write_foreign_fixture_corpus(Path(second_dir))
            first_files = sorted(path.name for path in Path(first_dir).iterdir())
            second_files = sorted(path.name for path in Path(second_dir).iterdir())
            self.assertEqual(first_files, second_files)
            self.assertGreater(len(first_files), len(FIXTURES))
            for name in first_files:
                self.assertEqual(
                    (Path(first_dir) / name).read_bytes(),
                    (Path(second_dir) / name).read_bytes(),
                    name,
                )


# DR 0034: deflate output is zlib-BUILD-specific. The committed corpus
# was generated under a zlib-ng CPython build, so the byte-identity
# pins below run only under a matching build — an environment
# OBSERVATION (H-01), never a pinned assumption. Every content-level
# gate (recorded-hash integrity, all decode expectations over freshly
# built fixtures) runs unconditionally under every build.
FIXTURE_ZLIB_BUILD = "zlib-ng"
ZLIB_BUILD_MATCHES = FIXTURE_ZLIB_BUILD in zlib.ZLIB_RUNTIME_VERSION
_ZLIB_SKIP_REASON = (
    "byte-identity pins require the fixture-generating zlib build "
    f"({FIXTURE_ZLIB_BUILD}; this interpreter: "
    f"{zlib.ZLIB_RUNTIME_VERSION}) — DR 0034; the content gates "
    "still run"
)


class TestCommittedForeignCorpus(unittest.TestCase):
    @unittest.skipUnless(ZLIB_BUILD_MATCHES, _ZLIB_SKIP_REASON)
    def test_committed_fixture_files_match_writer_output(self):
        for fixture in FIXTURES:
            with self.subTest(fixture=fixture["fixture_id"]):
                committed = (FIXTURE_DIR / fixture["file_name"]).read_bytes()
                self.assertEqual(committed, fixture["png_bytes"])

    @unittest.skipUnless(ZLIB_BUILD_MATCHES, _ZLIB_SKIP_REASON)
    def test_committed_manifest_is_valid_json_and_matches_writer(self):
        committed = json.loads(
            (FIXTURE_DIR / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(committed, json.loads(json.dumps(MANIFEST)))
        self.assertEqual(committed["fixture_count"], len(committed["fixtures"]))

    def test_manifest_hashes_match_committed_files(self):
        committed = json.loads(
            (FIXTURE_DIR / "manifest.json").read_text(encoding="utf-8")
        )
        for entry in committed["fixtures"]:
            with self.subTest(fixture=entry["fixture_id"]):
                payload = (FIXTURE_DIR / entry["file_name"]).read_bytes()
                self.assertEqual(entry["sha256"], hash_bytes(payload))
                self.assertEqual(entry["byte_count"], len(payload))


class TestManifestExpectedOutcomes(unittest.TestCase):
    def test_every_manifest_expectation_holds(self):
        for fixture in FIXTURES:
            for decoder_id, expected in fixture["expected"].items():
                with self.subTest(fixture=fixture["fixture_id"], decoder=decoder_id):
                    observed = _run_decoder(decoder_id, fixture["png_bytes"])
                    self.assertEqual(expected["outcome"], observed["outcome"])
                    if expected["outcome"] == "typed_reject":
                        self.assertIn(expected["family"], observed["families"])


class TestStandardDecoderForeignConformance(unittest.TestCase):
    def test_multi_idat_fixtures_decode_reference_pixels(self):
        for fixture_id in ["static_multi_idat_even", "static_multi_idat_ragged"]:
            with self.subTest(fixture=fixture_id):
                fixture = FIXTURES_BY_ID[fixture_id]
                decoded = decode_png_rgba(fixture["png_bytes"])
                self.assertEqual(decoded["width"], fixture["width"])
                self.assertEqual(decoded["height"], fixture["height"])
                self.assertGreater(decoded["chunks"].count("IDAT"), 1)
                self.assertEqual(decoded["pixels"], fixture["reference"]["pixels"])

    def test_ancillary_interleaved_fixture_decodes_reference_pixels(self):
        fixture = FIXTURES_BY_ID["static_ancillary_interleaved"]
        decoded = decode_png_rgba(fixture["png_bytes"])
        self.assertEqual(decoded["pixels"], fixture["reference"]["pixels"])
        for chunk_type in ["gAMA", "pHYs", "tEXt"]:
            self.assertIn(chunk_type, decoded["chunks"])

    def test_scanline_filters_1_to_4_raise_typed_rejection(self):
        for fixture_id in STATIC_FILTER_FIXTURE_IDS:
            with self.subTest(fixture=fixture_id):
                fixture = FIXTURES_BY_ID[fixture_id]
                with self.assertRaises(PNGDecodeError) as context:
                    decode_png_rgba(fixture["png_bytes"])
                self.assertEqual(context.exception.family, "png_filter_unsupported")

    def test_adam7_fixtures_raise_typed_rejection(self):
        for fixture_id in ["adam7_basic", "adam7_mixed_filters_multi_idat"]:
            with self.subTest(fixture=fixture_id):
                with self.assertRaises(PNGDecodeError) as context:
                    decode_png_rgba(FIXTURES_BY_ID[fixture_id]["png_bytes"])
                self.assertEqual(context.exception.family, "png_method_unsupported")

    def test_apng_default_images_decode_as_static_png(self):
        for fixture_id in APNG_FIXTURE_IDS:
            fixture = FIXTURES_BY_ID[fixture_id]
            expected = fixture["expected"]["standard_decode_png_rgba"]
            if expected["outcome"] != "decode":
                continue
            with self.subTest(fixture=fixture_id):
                decoded = decode_png_rgba(fixture["png_bytes"])
                self.assertEqual(
                    decoded["pixels"],
                    fixture["reference"]["default_image_pixels"],
                )


class TestAdam7DecoderForeignConformance(unittest.TestCase):
    def test_adam7_basic_decodes_reference_pixels(self):
        fixture = FIXTURES_BY_ID["adam7_basic"]
        decoded = decode_png_adam7_rgba(fixture["png_bytes"])
        self.assertEqual(decoded["width"], fixture["width"])
        self.assertEqual(decoded["height"], fixture["height"])
        self.assertEqual(decoded["interlace_method"], 1)
        self.assertEqual(decoded["pixels"], fixture["reference"]["pixels"])
        self.assertEqual(decoded["non_empty_pass_count"], 7)
        self.assertEqual(decoded["filter_types_seen"], [0])

    def test_adam7_mixed_filters_multi_idat_decodes_reference_pixels(self):
        fixture = FIXTURES_BY_ID["adam7_mixed_filters_multi_idat"]
        decoded = decode_png_adam7_rgba(fixture["png_bytes"])
        self.assertEqual(decoded["pixels"], fixture["reference"]["pixels"])
        self.assertEqual(decoded["chunks"].count("IDAT"), 3)
        self.assertEqual(sorted(decoded["filter_types_seen"]), [0, 1, 2, 3, 4])

    def test_non_interlaced_foreign_fixture_raises_typed_rejection(self):
        with self.assertRaises(PNGAdam7DecodeError) as context:
            decode_png_adam7_rgba(FIXTURES_BY_ID["static_multi_idat_even"]["png_bytes"])
        self.assertEqual(context.exception.family, "png_adam7_interlace_required")


class TestDeepColorDecoderForeignConformance(unittest.TestCase):
    def test_gray_and_16bit_fixtures_decode_reference_pixels(self):
        for fixture_id in DEEP_STATIC_FIXTURE_IDS:
            with self.subTest(fixture=fixture_id):
                fixture = FIXTURES_BY_ID[fixture_id]
                decoded = decode_png_deep_color(fixture["png_bytes"])
                self.assertEqual(decoded["width"], fixture["width"])
                self.assertEqual(decoded["height"], fixture["height"])
                self.assertEqual(decoded["color_type"], fixture["color_type"])
                self.assertEqual(decoded["bit_depth"], fixture["bit_depth"])
                self.assertEqual(decoded["interlace_method"], 0)
                self.assertEqual(decoded["pixels"], fixture["reference"]["pixels"])

    def test_gray8_multi_idat_uses_single_byte_filter_stride(self):
        decoded = decode_png_deep_color(
            FIXTURES_BY_ID["gray8_multi_idat_mixed_filters"]["png_bytes"]
        )
        self.assertEqual(decoded["filter_bpp"], 1)
        self.assertEqual(decoded["chunks"].count("IDAT"), 2)
        self.assertEqual(sorted(decoded["filter_types_seen"]), [0, 1, 2, 3, 4])

    def test_16bit_multi_idat_nonzero_filters_use_16bit_strides(self):
        gray16 = decode_png_deep_color(
            FIXTURES_BY_ID["gray16_multi_idat_mixed_filters"]["png_bytes"]
        )
        self.assertEqual(gray16["filter_bpp"], 2)
        self.assertEqual(gray16["chunks"].count("IDAT"), 3)
        self.assertEqual(sorted(gray16["filter_types_seen"]), [0, 1, 2, 3, 4])

        rgba16 = decode_png_deep_color(
            FIXTURES_BY_ID["rgba16_paeth_sub_multi_idat"]["png_bytes"]
        )
        self.assertEqual(rgba16["filter_bpp"], 8)
        self.assertEqual(rgba16["chunks"].count("IDAT"), 3)
        self.assertEqual(sorted(rgba16["filter_types_seen"]), [1, 2, 3, 4])

    def test_rgba8_foreign_fixtures_also_decode_pixel_exact(self):
        fixture_ids = [
            "static_multi_idat_even",
            "static_multi_idat_ragged",
            "static_ancillary_interleaved",
        ] + STATIC_FILTER_FIXTURE_IDS
        for fixture_id in fixture_ids:
            with self.subTest(fixture=fixture_id):
                fixture = FIXTURES_BY_ID[fixture_id]
                decoded = decode_png_deep_color(fixture["png_bytes"])
                self.assertEqual(decoded["pixels"], fixture["reference"]["pixels"])

    def test_adam7_16bit_fixture_is_typed_interlace_rejection(self):
        with self.assertRaises(PNGDeepColorDecodeError) as context:
            decode_png_deep_color(
                FIXTURES_BY_ID["rgba16_adam7_mixed_filters_multi_idat"]["png_bytes"]
            )
        self.assertEqual(context.exception.family, "png_interlace_unsupported")


class TestAdam7DeepColorForeignConformance(unittest.TestCase):
    def test_rgba16_adam7_fixture_decodes_reference_pixels(self):
        fixture = FIXTURES_BY_ID["rgba16_adam7_mixed_filters_multi_idat"]
        decoded = decode_png_adam7_deep_color(fixture["png_bytes"])
        self.assertEqual(decoded["width"], fixture["width"])
        self.assertEqual(decoded["height"], fixture["height"])
        self.assertEqual(decoded["color_type"], 6)
        self.assertEqual(decoded["bit_depth"], 16)
        self.assertEqual(decoded["chunks"].count("IDAT"), 2)
        self.assertEqual(sorted(decoded["filter_types_seen"]), [0, 1, 2, 3, 4])
        self.assertEqual(decoded["pixels"], fixture["reference"]["pixels"])

    def test_non_interlaced_gray_deep_fixtures_require_adam7(self):
        for fixture_id in DEEP_STATIC_FIXTURE_IDS:
            with self.subTest(fixture=fixture_id):
                with self.assertRaises(PNGAdam7DeepColorDecodeError) as context:
                    decode_png_adam7_deep_color(FIXTURES_BY_ID[fixture_id]["png_bytes"])
                self.assertEqual(
                    context.exception.family,
                    "png_adam7_deep_color_interlace_required",
                )


class TestGrayDeepRejectionForeignConformance(unittest.TestCase):
    RGBA8_ONLY_EXPECTED_FAMILIES = {
        "gray8_multi_idat_mixed_filters": "png_color_type_unsupported",
        "gray16_multi_idat_mixed_filters": "png_bit_depth_unsupported",
        "rgba16_basic": "png_bit_depth_unsupported",
        "rgba16_paeth_sub_multi_idat": "png_bit_depth_unsupported",
        "rgba16_adam7_mixed_filters_multi_idat": "png_bit_depth_unsupported",
    }

    def test_standard_decoder_rejects_with_documented_families(self):
        for fixture_id, family in self.RGBA8_ONLY_EXPECTED_FAMILIES.items():
            with self.subTest(fixture=fixture_id):
                with self.assertRaises(PNGDecodeError) as context:
                    decode_png_rgba(FIXTURES_BY_ID[fixture_id]["png_bytes"])
                self.assertEqual(context.exception.family, family)

    def test_adam7_rgba8_decoder_rejects_with_documented_families(self):
        for fixture_id, family in self.RGBA8_ONLY_EXPECTED_FAMILIES.items():
            with self.subTest(fixture=fixture_id):
                with self.assertRaises(PNGAdam7DecodeError) as context:
                    decode_png_adam7_rgba(FIXTURES_BY_ID[fixture_id]["png_bytes"])
                self.assertEqual(context.exception.family, family)

    def test_apng_family_rejects_with_color_model_family(self):
        apng_decoder_ids = [
            "apng_decode_apng_frames",
            "apng_filtered_frame_data",
            "apng_partial_frame_playback",
        ]
        for fixture_id in GRAY_DEEP_FIXTURE_IDS:
            for decoder_id in apng_decoder_ids:
                with self.subTest(fixture=fixture_id, decoder=decoder_id):
                    observed = _run_decoder(
                        decoder_id, FIXTURES_BY_ID[fixture_id]["png_bytes"]
                    )
                    self.assertEqual(observed["outcome"], "typed_reject")
                    self.assertEqual(
                        observed["families"], ["apng_color_model_unsupported"]
                    )

    def test_textual_metadata_import_rejects_with_documented_families(self):
        for fixture_id, family in self.RGBA8_ONLY_EXPECTED_FAMILIES.items():
            with self.subTest(fixture=fixture_id):
                imported = import_png_textual_metadata(
                    FIXTURES_BY_ID[fixture_id]["png_bytes"]
                )
                self.assertFalse(imported["ok"])
                self.assertEqual(imported["error_families"], [family])


class TestApngSidecarDecoderForeignConformance(unittest.TestCase):
    def test_basic_split_fdat_decodes_frames_and_sequence_numbers(self):
        fixture = FIXTURES_BY_ID["apng_basic_split_fdat"]
        decoded = decode_apng_frames(fixture["png_bytes"])
        reference = fixture["reference"]
        self.assertEqual(decoded["frame_count"], 2)
        self.assertEqual(decoded["sequence_numbers"], [0, 1, 2, 3, 4])
        self.assertEqual(
            decoded["animation_chunk_order"],
            ["fcTL", "IDAT", "IDAT", "fcTL", "fdAT", "fdAT", "fdAT"],
        )
        for index, frame in enumerate(decoded["frames"]):
            self.assertEqual(frame["pixels"], reference["frames"][index]["pixels"])

    def test_out_of_scope_apng_features_raise_documented_families(self):
        expectations = {
            "apng_default_image_not_animated": "apng_default_frame_control_missing",
            "apng_dispose_background": "apng_frame_control_unsupported",
            "apng_dispose_previous": "apng_frame_control_unsupported",
            "apng_blend_over": "apng_frame_control_unsupported",
            "apng_subcanvas_regions": "apng_frame_control_unsupported",
            "apng_filtered_frames_split_fdat": "apng_filter_unsupported",
        }
        for fixture_id, family in expectations.items():
            with self.subTest(fixture=fixture_id):
                with self.assertRaises(ValueError) as context:
                    decode_apng_frames(FIXTURES_BY_ID[fixture_id]["png_bytes"])
                self.assertEqual(getattr(context.exception, "family", None), family)


class TestApngFilteredFrameDataForeignConformance(unittest.TestCase):
    def test_supported_fixtures_reproduce_reference_playback_hashes(self):
        for fixture_id in [
            "apng_basic_split_fdat",
            "apng_subcanvas_regions",
            "apng_filtered_frames_split_fdat",
        ]:
            with self.subTest(fixture=fixture_id):
                fixture = FIXTURES_BY_ID[fixture_id]
                decoded = decode_apng_filtered_frame_data(fixture["png_bytes"])
                self.assertTrue(decoded["ok"], decoded.get("error_families"))
                reference = fixture["reference"]
                self.assertEqual(decoded["display_hashes"], reference["display_hashes"])
                self.assertEqual(
                    decoded["final_output_hash"], reference["final_output_hash"]
                )

    def test_filtered_frames_report_foreign_filter_types(self):
        fixture = FIXTURES_BY_ID["apng_filtered_frames_split_fdat"]
        decoded = decode_apng_filtered_frame_data(fixture["png_bytes"])
        self.assertTrue(decoded["ok"])
        seen = sorted(
            {
                filter_type
                for frame in decoded["frames"]
                for filter_type in frame["filter_types_seen"]
            }
        )
        self.assertEqual(seen, [1, 2, 3, 4])

    def test_dispose_and_blend_variants_are_typed_rejections_not_wrong_pixels(self):
        # Regression coverage for the decoder fix: _simulate_source_playback
        # implements source playback only, so dispose background/previous and
        # blend over must be rejected with typed families rather than played
        # back with spec-incorrect hashes.
        expectations = {
            "apng_dispose_background": "apng_dispose_op_unsupported",
            "apng_dispose_previous": "apng_dispose_op_unsupported",
            "apng_blend_over": "apng_blend_op_unsupported",
        }
        for fixture_id, family in expectations.items():
            with self.subTest(fixture=fixture_id):
                decoded = decode_apng_filtered_frame_data(
                    FIXTURES_BY_ID[fixture_id]["png_bytes"]
                )
                self.assertFalse(decoded["ok"])
                self.assertEqual(decoded["error_families"], [family])


class TestApngPartialPlaybackForeignConformance(unittest.TestCase):
    def test_playback_fixtures_reproduce_reference_hashes(self):
        for fixture_id in [
            "apng_basic_split_fdat",
            "apng_dispose_background",
            "apng_dispose_previous",
            "apng_blend_over",
            "apng_subcanvas_regions",
        ]:
            with self.subTest(fixture=fixture_id):
                fixture = FIXTURES_BY_ID[fixture_id]
                decoded = decode_apng_partial_frame_playback(fixture["png_bytes"])
                self.assertTrue(decoded["ok"], decoded.get("error_families"))
                reference = fixture["reference"]
                self.assertEqual(decoded["frame_count"], fixture["frame_count"])
                self.assertEqual(decoded["display_hashes"], reference["display_hashes"])
                self.assertEqual(
                    decoded["after_dispose_hashes"], reference["after_dispose_hashes"]
                )
                self.assertEqual(
                    decoded["final_output_hash"], reference["final_output_hash"]
                )

    def test_default_image_not_animated_is_typed_rejection(self):
        decoded = decode_apng_partial_frame_playback(
            FIXTURES_BY_ID["apng_default_image_not_animated"]["png_bytes"]
        )
        self.assertFalse(decoded["ok"])
        self.assertEqual(decoded["error_families"], ["apng_default_frame_unsupported"])

    def test_filtered_frames_fixture_is_typed_rejection(self):
        decoded = decode_apng_partial_frame_playback(
            FIXTURES_BY_ID["apng_filtered_frames_split_fdat"]["png_bytes"]
        )
        self.assertFalse(decoded["ok"])
        self.assertEqual(decoded["error_families"], ["apng_filter_unsupported"])


class TestImageDataChunkingForeignConformance(unittest.TestCase):
    def test_static_fixtures_decode_reference_hash_and_chunk_counts(self):
        for fixture in FIXTURES:
            expected = fixture["expected"].get("image_data_chunking")
            if fixture["kind"] != "static" or not expected or expected["outcome"] != "decode":
                continue
            with self.subTest(fixture=fixture["fixture_id"]):
                decoded = decode_png_apng_image_data_chunking(fixture["png_bytes"])
                self.assertTrue(decoded["ok"], decoded.get("error_families"))
                self.assertEqual(decoded["pixel_hash"], fixture["reference"]["pixel_hash"])
                self.assertEqual(decoded["idat_chunk_count"], expected["idat_chunk_count"])

    def test_apng_fixtures_decode_reference_final_hash(self):
        for fixture in FIXTURES:
            expected = fixture["expected"].get("image_data_chunking")
            if fixture["kind"] != "apng" or not expected or expected["outcome"] != "decode":
                continue
            with self.subTest(fixture=fixture["fixture_id"]):
                decoded = decode_png_apng_image_data_chunking(fixture["png_bytes"])
                self.assertTrue(decoded["ok"], decoded.get("error_families"))
                self.assertEqual(
                    decoded["final_output_hash"],
                    fixture["reference"]["final_output_hash"],
                )
                self.assertEqual(decoded["idat_chunk_count"], expected["idat_chunk_count"])
                self.assertEqual(decoded["fdat_chunk_count"], expected["fdat_chunk_count"])

    def test_out_of_scope_fixtures_reject_with_typed_families(self):
        expectations = {
            "adam7_basic": "png_interlace_unsupported",
            "apng_default_image_not_animated": "apng_default_frame_unsupported",
            "apng_dispose_background": "apng_dispose_op_unsupported",
            "apng_dispose_previous": "apng_dispose_op_unsupported",
            "apng_blend_over": "apng_blend_op_unsupported",
        }
        for fixture_id, family in expectations.items():
            with self.subTest(fixture=fixture_id):
                decoded = decode_png_apng_image_data_chunking(
                    FIXTURES_BY_ID[fixture_id]["png_bytes"]
                )
                self.assertFalse(decoded["ok"])
                self.assertIn(family, decoded["error_families"])


class TestChunkOrderForeignConformance(unittest.TestCase):
    def test_every_foreign_fixture_is_spec_valid_chunk_order(self):
        for fixture in FIXTURES:
            with self.subTest(fixture=fixture["fixture_id"]):
                validation = validate_png_apng_chunk_order(fixture["png_bytes"])
                self.assertTrue(validation["ok"], validation["errors"])
                self.assertEqual(validation["errors"], [])

    def test_apng_fixture_sequence_numbers_are_consecutive(self):
        for fixture_id in APNG_FIXTURE_IDS:
            with self.subTest(fixture=fixture_id):
                validation = validate_png_apng_chunk_order(
                    FIXTURES_BY_ID[fixture_id]["png_bytes"]
                )
                self.assertTrue(validation["ok"], validation["errors"])
                numbers = validation["apng_sequence_numbers"]
                self.assertEqual(numbers, list(range(len(numbers))))


class TestTextualMetadataForeignConformance(unittest.TestCase):
    def test_foreign_text_chunks_are_typed_metadata_missing(self):
        for fixture_id in ["static_multi_idat_even", "static_ancillary_interleaved"]:
            with self.subTest(fixture=fixture_id):
                imported = import_png_textual_metadata(
                    FIXTURES_BY_ID[fixture_id]["png_bytes"]
                )
                self.assertFalse(imported["ok"])
                self.assertEqual(
                    imported["error_families"], ["png_textual_metadata_chunk_missing"]
                )


class TestForeignFixtureSweep(unittest.TestCase):
    def test_no_raw_exception_escapes_any_decoder(self):
        for fixture in FIXTURES:
            for decoder_id, decoder in DECODERS.items():
                with self.subTest(fixture=fixture["fixture_id"], decoder=decoder_id):
                    try:
                        result = decoder(fixture["png_bytes"])
                    except Exception as exc:
                        self.assertIsInstance(
                            exc,
                            ValueError,
                            f"raw {type(exc).__name__} escaped {decoder_id}: {exc!r}",
                        )
                        family = getattr(exc, "family", None)
                        self.assertIsInstance(
                            family,
                            str,
                            f"{decoder_id} raised ValueError without a family: {exc!r}",
                        )
                        self.assertTrue(family)
                    else:
                        self.assertIsInstance(result, dict)
                        if result.get("ok") is False:
                            families = result.get("error_families")
                            self.assertTrue(
                                families,
                                f"{decoder_id} rejected without error families",
                            )


if __name__ == "__main__":
    unittest.main()
