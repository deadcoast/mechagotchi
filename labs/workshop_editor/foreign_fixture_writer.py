"""Independent, spec-derived PNG/APNG fixture writer for foreign-file conformance.

This module is deliberately NOT built on any existing workshop lab encoder.
Every byte it emits is derived directly from the W3C PNG specification,
Third Edition (https://www.w3.org/TR/png-3/), including the APNG chapter:

- its own chunk serializer (length + type + data + CRC-32),
- its own scanline filter implementations for filter types 0..4,
- its own Adam7 pass extraction,
- its own acTL/fcTL/fdAT serialization and sequence numbering,
- its own APNG playback reference model (blend source/over and
  dispose none/background/previous) computed with exact rational
  arithmetic.

The writer produces spec-valid files exercising features the lab encoders
never emit (multi-IDAT streams, filters 1..4, interleaved ancillary chunks,
independent Adam7 output, APNG dispose/blend variants, sub-canvas frame
regions, and fdAT payloads split across chunks) so decoder tests stop being
self-referential.

Output is fully deterministic: fixed pixel patterns, no timestamps, no
randomness. ``main`` regenerates ``data/foreign_fixtures``.
"""

import argparse
import hashlib
import json
import struct
import zlib
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SPEC_URL = "https://www.w3.org/TR/png-3/"
CORPUS_ID = "foreign_fixture_corpus_v1"
DEFAULT_OUTPUT_DIR = ROOT / "data/foreign_fixtures"

# Adam7 pass grid from the PNG specification: (x_start, y_start, x_step, y_step).
ADAM7_PASSES = (
    (0, 0, 8, 8),
    (4, 0, 8, 8),
    (0, 4, 4, 8),
    (2, 0, 4, 4),
    (0, 2, 2, 4),
    (1, 0, 2, 2),
    (0, 1, 1, 2),
)

TRANSPARENT_BLACK = (0, 0, 0, 0)

GAMA_CHUNK = ("gAMA", struct.pack(">I", 45455))
PHYS_CHUNK = ("pHYs", struct.pack(">IIB", 2835, 2835, 1))
TEXT_SOFTWARE_CHUNK = ("tEXt", b"Software\x00mechagotchi foreign fixture writer")
TEXT_COMMENT_CHUNK = ("tEXt", b"Comment\x00spec-derived license-clean corpus")


# ---------------------------------------------------------------------------
# Low-level PNG serialization (independent of every lab encoder)
# ---------------------------------------------------------------------------


def write_chunk(chunk_type: str, payload: bytes) -> bytes:
    tag = chunk_type.encode("ascii")
    crc = zlib.crc32(payload, zlib.crc32(tag)) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)


def _paeth_predictor(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    distance_left = abs(estimate - left)
    distance_up = abs(estimate - up)
    distance_upper_left = abs(estimate - upper_left)
    if distance_left <= distance_up and distance_left <= distance_upper_left:
        return left
    if distance_up <= distance_upper_left:
        return up
    return upper_left


def _filter_scanline(row: bytes, previous: bytes | None, filter_type: int, bpp: int) -> bytes:
    if filter_type == 0:
        return row
    filtered = bytearray()
    for index, value in enumerate(row):
        left = row[index - bpp] if index >= bpp else 0
        up = previous[index] if previous is not None else 0
        upper_left = previous[index - bpp] if previous is not None and index >= bpp else 0
        if filter_type == 1:
            prediction = left
        elif filter_type == 2:
            prediction = up
        elif filter_type == 3:
            prediction = (left + up) // 2
        elif filter_type == 4:
            prediction = _paeth_predictor(left, up, upper_left)
        else:
            raise ValueError("PNG filter type must be in 0..4")
        filtered.append((value - prediction) & 0xFF)
    return bytes(filtered)


def _serialize_rows(rows: list[bytes], row_filters: list[int], bpp: int = 4) -> bytes:
    """Serialize unfiltered rows into a filtered raw datastream.

    ``row_filters`` is cycled across rows; the previous row used by filters
    2..4 is the reconstructed (original) previous row per the specification.
    """
    raw = bytearray()
    previous = None
    for index, row in enumerate(rows):
        filter_type = row_filters[index % len(row_filters)]
        raw.append(filter_type)
        raw.extend(_filter_scanline(row, previous, filter_type, bpp))
        previous = row
    return bytes(raw)


def _pixel_rows(width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> list[bytes]:
    if len(pixels) != width * height:
        raise ValueError("pixel count does not match dimensions")
    rows = []
    for y in range(height):
        row = bytearray()
        for pixel in pixels[y * width : (y + 1) * width]:
            if len(pixel) != 4 or any(channel < 0 or channel > 255 for channel in pixel):
                raise ValueError("RGBA channels must be in [0, 255]")
            row.extend(pixel)
        rows.append(bytes(row))
    return rows


def _sequential_raw(
    width: int,
    height: int,
    pixels: list[tuple[int, int, int, int]],
    row_filters: list[int],
) -> bytes:
    return _serialize_rows(_pixel_rows(width, height, pixels), row_filters)


def _adam7_raw(
    width: int,
    height: int,
    pixels: list[tuple[int, int, int, int]],
    row_filters: list[int],
) -> bytes:
    """Serialize an Adam7-interlaced datastream (independent pass extraction).

    Each reduced image is filtered independently: the previous-row state
    resets at the start of every pass. The ``row_filters`` cycle advances
    across all emitted reduced scanlines.
    """
    raw = bytearray()
    filter_cursor = 0
    for x_start, y_start, x_step, y_step in ADAM7_PASSES:
        pass_columns = list(range(x_start, width, x_step))
        pass_rows = list(range(y_start, height, y_step))
        if not pass_columns or not pass_rows:
            continue
        previous = None
        for y in pass_rows:
            row = bytearray()
            for x in pass_columns:
                row.extend(pixels[y * width + x])
            row_bytes = bytes(row)
            filter_type = row_filters[filter_cursor % len(row_filters)]
            filter_cursor += 1
            raw.append(filter_type)
            raw.extend(_filter_scanline(row_bytes, previous, filter_type, 4))
            previous = row_bytes
    return bytes(raw)


def _split_segments(payload: bytes, segment_lengths: list[int] | None) -> list[bytes]:
    """Split a compressed datastream at arbitrary byte boundaries.

    ``segment_lengths`` lists the byte length of every segment except the
    last, which receives the remainder. ``None`` means a single segment.
    Zero-length segments are legal per the specification.
    """
    if not segment_lengths:
        return [payload]
    segments = []
    offset = 0
    for length in segment_lengths:
        if length < 0 or offset + length > len(payload):
            raise ValueError("segment lengths exceed the compressed payload")
        segments.append(payload[offset : offset + length])
        offset += length
    segments.append(payload[offset:])
    return segments


def _even_segment_lengths(total: int, chunk_count: int) -> list[int]:
    if chunk_count < 1:
        raise ValueError("chunk count must be positive")
    base = total // chunk_count
    return [base] * (chunk_count - 1)


def _ihdr_payload(
    width: int,
    height: int,
    interlace: int,
    bit_depth: int = 8,
    color_type: int = 6,
) -> bytes:
    return struct.pack(">IIBBBBB", width, height, bit_depth, color_type, 0, 0, interlace)


def build_static_png(
    width: int,
    height: int,
    pixels: list[tuple[int, int, int, int]],
    *,
    row_filters: list[int] | None = None,
    interlace: int = 0,
    idat_segment_lengths: list[int] | None = None,
    idat_chunk_count: int | None = None,
    pre_idat_chunks: tuple[tuple[str, bytes], ...] = (),
    post_idat_chunks: tuple[tuple[str, bytes], ...] = (),
) -> bytes:
    filters = row_filters or [0]
    if interlace == 0:
        raw = _sequential_raw(width, height, pixels, filters)
    elif interlace == 1:
        raw = _adam7_raw(width, height, pixels, filters)
    else:
        raise ValueError("interlace method must be 0 or 1")
    compressed = zlib.compress(raw)
    if idat_chunk_count is not None and idat_segment_lengths is None:
        idat_segment_lengths = _even_segment_lengths(len(compressed), idat_chunk_count)
    segments = _split_segments(compressed, idat_segment_lengths)

    parts = [PNG_SIGNATURE, write_chunk("IHDR", _ihdr_payload(width, height, interlace))]
    for chunk_type, payload in pre_idat_chunks:
        parts.append(write_chunk(chunk_type, payload))
    for segment in segments:
        parts.append(write_chunk("IDAT", segment))
    for chunk_type, payload in post_idat_chunks:
        parts.append(write_chunk(chunk_type, payload))
    parts.append(write_chunk("IEND", b""))
    return b"".join(parts)


# ---------------------------------------------------------------------------
# Grayscale and deep-color (16-bit) serialization
#
# Encoded pixels are represented as one ``bytes`` object per pixel so the
# same filter and Adam7 pass-extraction code covers every sample size. Per
# the specification, filter method 0 operates on bytes with the pixel byte
# stride ``bpp``: 1 for 8-bit grayscale, 2 for 16-bit grayscale, and 8 for
# 16-bit RGBA. 16-bit samples are serialized big-endian (network order).
# ---------------------------------------------------------------------------


def _gray8_pixel_bytes(samples: list[int]) -> list[bytes]:
    encoded = []
    for sample in samples:
        if sample < 0 or sample > 255:
            raise ValueError("8-bit grayscale samples must be in [0, 255]")
        encoded.append(bytes([sample]))
    return encoded


def _gray16_pixel_bytes(samples: list[int]) -> list[bytes]:
    encoded = []
    for sample in samples:
        if sample < 0 or sample > 65535:
            raise ValueError("16-bit grayscale samples must be in [0, 65535]")
        encoded.append(struct.pack(">H", sample))
    return encoded


def _rgba16_pixel_bytes(pixels: list[tuple[int, int, int, int]]) -> list[bytes]:
    encoded = []
    for pixel in pixels:
        if len(pixel) != 4 or any(channel < 0 or channel > 65535 for channel in pixel):
            raise ValueError("16-bit RGBA channels must be in [0, 65535]")
        encoded.append(struct.pack(">HHHH", *pixel))
    return encoded


def _sequential_raw_from_pixel_bytes(
    width: int,
    height: int,
    pixel_bytes: list[bytes],
    row_filters: list[int],
    bpp: int,
) -> bytes:
    rows = [
        b"".join(pixel_bytes[y * width : (y + 1) * width]) for y in range(height)
    ]
    return _serialize_rows(rows, row_filters, bpp)


def _adam7_raw_from_pixel_bytes(
    width: int,
    height: int,
    pixel_bytes: list[bytes],
    row_filters: list[int],
    bpp: int,
) -> bytes:
    """Adam7 datastream for arbitrary sample sizes (independent extraction).

    Same pass semantics as ``_adam7_raw``: each reduced image is filtered
    independently and the filter cycle advances across all emitted reduced
    scanlines; empty passes emit nothing.
    """
    raw = bytearray()
    filter_cursor = 0
    for x_start, y_start, x_step, y_step in ADAM7_PASSES:
        pass_columns = list(range(x_start, width, x_step))
        pass_rows = list(range(y_start, height, y_step))
        if not pass_columns or not pass_rows:
            continue
        previous = None
        for y in pass_rows:
            row_bytes = b"".join(pixel_bytes[y * width + x] for x in pass_columns)
            filter_type = row_filters[filter_cursor % len(row_filters)]
            filter_cursor += 1
            raw.append(filter_type)
            raw.extend(_filter_scanline(row_bytes, previous, filter_type, bpp))
            previous = row_bytes
    return bytes(raw)


def build_static_deep_png(
    width: int,
    height: int,
    pixel_bytes: list[bytes],
    *,
    bit_depth: int,
    color_type: int,
    row_filters: list[int] | None = None,
    interlace: int = 0,
    idat_segment_lengths: list[int] | None = None,
    idat_chunk_count: int | None = None,
    pre_idat_chunks: tuple[tuple[str, bytes], ...] = (),
    post_idat_chunks: tuple[tuple[str, bytes], ...] = (),
) -> bytes:
    if len(pixel_bytes) != width * height:
        raise ValueError("pixel count does not match dimensions")
    bpp = len(pixel_bytes[0])
    if any(len(encoded) != bpp for encoded in pixel_bytes):
        raise ValueError("encoded pixels must share one byte stride")
    filters = row_filters or [0]
    if interlace == 0:
        raw = _sequential_raw_from_pixel_bytes(width, height, pixel_bytes, filters, bpp)
    elif interlace == 1:
        raw = _adam7_raw_from_pixel_bytes(width, height, pixel_bytes, filters, bpp)
    else:
        raise ValueError("interlace method must be 0 or 1")
    compressed = zlib.compress(raw)
    if idat_chunk_count is not None and idat_segment_lengths is None:
        idat_segment_lengths = _even_segment_lengths(len(compressed), idat_chunk_count)
    segments = _split_segments(compressed, idat_segment_lengths)

    parts = [
        PNG_SIGNATURE,
        write_chunk("IHDR", _ihdr_payload(width, height, interlace, bit_depth, color_type)),
    ]
    for chunk_type, payload in pre_idat_chunks:
        parts.append(write_chunk(chunk_type, payload))
    for segment in segments:
        parts.append(write_chunk("IDAT", segment))
    for chunk_type, payload in post_idat_chunks:
        parts.append(write_chunk(chunk_type, payload))
    parts.append(write_chunk("IEND", b""))
    return b"".join(parts)


# ---------------------------------------------------------------------------
# APNG serialization
# ---------------------------------------------------------------------------


def make_frame(
    pixels: list[tuple[int, int, int, int]],
    *,
    width: int,
    height: int,
    x_offset: int = 0,
    y_offset: int = 0,
    delay_num: int = 1,
    delay_den: int = 10,
    dispose_op: int = 0,
    blend_op: int = 0,
    row_filters: list[int] | None = None,
    data_chunk_count: int = 1,
) -> dict:
    return {
        "pixels": pixels,
        "width": width,
        "height": height,
        "x_offset": x_offset,
        "y_offset": y_offset,
        "delay_num": delay_num,
        "delay_den": delay_den,
        "dispose_op": dispose_op,
        "blend_op": blend_op,
        "row_filters": row_filters or [0],
        "data_chunk_count": data_chunk_count,
    }


def _fctl_payload(sequence_number: int, frame: dict) -> bytes:
    return struct.pack(
        ">IIIIIHHBB",
        sequence_number,
        frame["width"],
        frame["height"],
        frame["x_offset"],
        frame["y_offset"],
        frame["delay_num"],
        frame["delay_den"],
        frame["dispose_op"],
        frame["blend_op"],
    )


def build_apng(
    canvas_width: int,
    canvas_height: int,
    frames: list[dict],
    *,
    default_image: dict | None = None,
    num_plays: int = 0,
    chunks_after_actl: tuple[tuple[str, bytes], ...] = (),
) -> bytes:
    """Serialize an APNG from the specification.

    ``frames`` are the animation frames in playback order. When
    ``default_image`` is ``None`` the first animation frame doubles as the
    default image and is carried in IDAT chunks (its fcTL precedes IDAT).
    When ``default_image`` is provided, it is carried by IDAT chunks that
    are NOT covered by any fcTL, so the default image is not part of the
    animation and every animation frame travels in fdAT chunks.
    """
    if not frames:
        raise ValueError("APNG requires at least one animation frame")
    if default_image is None:
        first = frames[0]
        if (
            first["width"] != canvas_width
            or first["height"] != canvas_height
            or first["x_offset"]
            or first["y_offset"]
        ):
            raise ValueError("the default image frame must cover the full canvas")
    elif default_image["width"] != canvas_width or default_image["height"] != canvas_height:
        raise ValueError("the default image must cover the full canvas")

    parts = [
        PNG_SIGNATURE,
        write_chunk("IHDR", _ihdr_payload(canvas_width, canvas_height, 0)),
        write_chunk("acTL", struct.pack(">II", len(frames), num_plays)),
    ]
    for chunk_type, payload in chunks_after_actl:
        parts.append(write_chunk(chunk_type, payload))

    sequence_number = 0
    if default_image is not None:
        raw = _sequential_raw(
            canvas_width,
            canvas_height,
            default_image["pixels"],
            default_image["row_filters"],
        )
        compressed = zlib.compress(raw)
        segments = _split_segments(
            compressed,
            _even_segment_lengths(len(compressed), default_image["data_chunk_count"]),
        )
        for segment in segments:
            parts.append(write_chunk("IDAT", segment))

    for index, frame in enumerate(frames):
        parts.append(write_chunk("fcTL", _fctl_payload(sequence_number, frame)))
        sequence_number += 1
        raw = _sequential_raw(frame["width"], frame["height"], frame["pixels"], frame["row_filters"])
        compressed = zlib.compress(raw)
        segments = _split_segments(
            compressed,
            _even_segment_lengths(len(compressed), frame["data_chunk_count"]),
        )
        if index == 0 and default_image is None:
            for segment in segments:
                parts.append(write_chunk("IDAT", segment))
        else:
            for segment in segments:
                parts.append(write_chunk("fdAT", struct.pack(">I", sequence_number) + segment))
                sequence_number += 1

    parts.append(write_chunk("IEND", b""))
    return b"".join(parts)


# ---------------------------------------------------------------------------
# Reference APNG playback (spec semantics, exact arithmetic)
# ---------------------------------------------------------------------------


def _composite_over(
    source: tuple[int, int, int, int],
    destination: tuple[int, int, int, int],
) -> tuple[int, int, int, int]:
    source_alpha = Fraction(source[3], 255)
    destination_alpha = Fraction(destination[3], 255)
    out_alpha = source_alpha + destination_alpha * (1 - source_alpha)
    if out_alpha == 0:
        return TRANSPARENT_BLACK
    channels = []
    for index in range(3):
        value = (
            source[index] * source_alpha
            + destination[index] * destination_alpha * (1 - source_alpha)
        ) / out_alpha
        if value.denominator != 1:
            raise ValueError(
                "foreign fixture blend-over patterns must composite to exact integers"
            )
        channels.append(int(value))
    alpha = out_alpha * 255
    if alpha.denominator != 1:
        raise ValueError("foreign fixture blend-over patterns must composite to exact integers")
    channels.append(int(alpha))
    return tuple(channels)


def simulate_apng_playback(canvas_width: int, canvas_height: int, frames: list[dict]) -> dict:
    """Reference playback per the APNG chapter of the PNG specification.

    The output buffer starts fully transparent black. Each frame is
    composited into its region with blend_op source (0) or over (1); the
    buffer after rendering is the displayed frame. Disposal then prepares
    the buffer for the next frame: none (0) keeps it, background (1) clears
    the frame region, previous (2) reverts the frame region (treated as
    background on the first frame).
    """
    output = [TRANSPARENT_BLACK] * (canvas_width * canvas_height)
    display_pixels = []
    after_dispose_pixels = []
    for index, frame in enumerate(frames):
        before = list(output)
        for y in range(frame["height"]):
            for x in range(frame["width"]):
                source = frame["pixels"][y * frame["width"] + x]
                target = (frame["y_offset"] + y) * canvas_width + frame["x_offset"] + x
                if frame["blend_op"] == 0:
                    output[target] = source
                else:
                    output[target] = _composite_over(source, output[target])
        display_pixels.append(list(output))
        if frame["dispose_op"] == 1 or (frame["dispose_op"] == 2 and index == 0):
            for y in range(frame["height"]):
                for x in range(frame["width"]):
                    target = (frame["y_offset"] + y) * canvas_width + frame["x_offset"] + x
                    output[target] = TRANSPARENT_BLACK
        elif frame["dispose_op"] == 2:
            output = before
        after_dispose_pixels.append(list(output))
    return {
        "display_pixels": display_pixels,
        "after_dispose_pixels": after_dispose_pixels,
        "final_output_pixels": after_dispose_pixels[-1],
    }


# ---------------------------------------------------------------------------
# Deterministic pixel patterns
# ---------------------------------------------------------------------------


def pattern_pixels(width: int, height: int, variant: int = 0) -> list[tuple[int, int, int, int]]:
    pixels = []
    for y in range(height):
        for x in range(width):
            pixels.append(
                (
                    (x * 31 + y * 7 + variant * 11) % 256,
                    (x * 13 + y * 41 + variant * 29) % 256,
                    (x * 3 + y * 59 + variant * 47) % 256,
                    200 if (x + y + variant) % 4 == 0 else 255,
                )
            )
    return pixels


def opaque_pattern_pixels(width: int, height: int, variant: int = 0) -> list[tuple[int, int, int, int]]:
    return [(red, green, blue, 255) for red, green, blue, _alpha in pattern_pixels(width, height, variant)]


def quantized_pixels(
    width: int,
    height: int,
    variant: int,
    alpha: int,
) -> list[tuple[int, int, int, int]]:
    """Channels are multiples of 5 so alpha-over compositing with alpha 51
    (exactly 1/5 coverage) or 255 stays on exact integers."""
    pixels = []
    for y in range(height):
        for x in range(width):
            pixels.append(
                (
                    5 * ((x * 7 + y * 2 + variant * 3) % 52),
                    5 * ((x * 3 + y * 11 + variant * 5) % 52),
                    5 * ((x * 5 + y * 4 + variant * 7) % 52),
                    alpha,
                )
            )
    return pixels


def gray8_pattern_samples(width: int, height: int, variant: int = 0) -> list[int]:
    return [
        (x * 23 + y * 47 + variant * 13) % 256
        for y in range(height)
        for x in range(width)
    ]


def gray16_pattern_samples(width: int, height: int, variant: int = 0) -> list[int]:
    """16-bit grayscale samples whose high and low bytes both vary, so
    byte-oriented filtering is exercised across the full sample width."""
    return [
        (x * 4813 + y * 12289 + variant * 769) % 65536
        for y in range(height)
        for x in range(width)
    ]


def rgba16_pattern_pixels(
    width: int, height: int, variant: int = 0
) -> list[tuple[int, int, int, int]]:
    pixels = []
    for y in range(height):
        for x in range(width):
            pixels.append(
                (
                    (x * 4099 + y * 259 + variant * 6151) % 65536,
                    (x * 307 + y * 9973 + variant * 211) % 65536,
                    (x * 7919 + y * 1031 + variant * 97) % 65536,
                    (x * 257 + y * 8191 + variant * 127) % 65536,
                )
            )
    return pixels


def scale_16bit_sample_to_byte(value: int) -> int:
    """Sample-depth rescaling from the specification:
    ``round(value * 255 / 65535)``. Because 65535 is odd, an exact .5 tie is
    impossible, so round-half-up integer arithmetic equals true rounding."""
    if value < 0 or value > 65535:
        raise ValueError("16-bit sample must be in [0, 65535]")
    return (value * 255 + 32767) // 65535


def gray_reference_pixels(samples: list[int], bit_depth: int) -> list[tuple[int, int, int, int]]:
    if bit_depth == 8:
        return [(sample, sample, sample, 255) for sample in samples]
    if bit_depth == 16:
        return [
            (byte, byte, byte, 255)
            for byte in (scale_16bit_sample_to_byte(sample) for sample in samples)
        ]
    raise ValueError("grayscale reference pixels require bit depth 8 or 16")


def rgba16_reference_pixels(
    pixels: list[tuple[int, int, int, int]],
) -> list[tuple[int, int, int, int]]:
    return [
        tuple(scale_16bit_sample_to_byte(channel) for channel in pixel)
        for pixel in pixels
    ]


def hash_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def hash_pixels(pixels: list[tuple[int, int, int, int]]) -> str:
    return hash_bytes(b"".join(bytes(pixel) for pixel in pixels))


# ---------------------------------------------------------------------------
# Fixture corpus
# ---------------------------------------------------------------------------


def _decode(extra: dict | None = None) -> dict:
    expectation = {"outcome": "decode"}
    if extra:
        expectation.update(extra)
    return expectation


def _reject(family: str) -> dict:
    return {"outcome": "typed_reject", "family": family}


def _static_fixture(
    fixture_id: str,
    *,
    width: int,
    height: int,
    variant: int,
    features: list[str],
    row_filters: list[int] | None = None,
    interlace: int = 0,
    idat_chunk_count: int | None = None,
    idat_segment_lengths: list[int] | None = None,
    pre_idat_chunks: tuple[tuple[str, bytes], ...] = (),
    post_idat_chunks: tuple[tuple[str, bytes], ...] = (),
    expected: dict,
) -> dict:
    pixels = pattern_pixels(width, height, variant)
    png_bytes = build_static_png(
        width,
        height,
        pixels,
        row_filters=row_filters,
        interlace=interlace,
        idat_chunk_count=idat_chunk_count,
        idat_segment_lengths=idat_segment_lengths,
        pre_idat_chunks=pre_idat_chunks,
        post_idat_chunks=post_idat_chunks,
    )
    return {
        "fixture_id": fixture_id,
        "file_name": f"{fixture_id}.png",
        "png_bytes": png_bytes,
        "kind": "static",
        "features": features,
        "width": width,
        "height": height,
        "color_type": 6,
        "bit_depth": 8,
        "frame_count": 1,
        "reference": {
            "pixels": pixels,
            "pixel_hash": hash_pixels(pixels),
        },
        "expected": expected,
    }


def _deep_static_fixture(
    fixture_id: str,
    *,
    width: int,
    height: int,
    color_type: int,
    bit_depth: int,
    variant: int,
    features: list[str],
    row_filters: list[int] | None = None,
    interlace: int = 0,
    idat_chunk_count: int | None = None,
    expected: dict,
) -> dict:
    """Grayscale or 16-bit fixture. The RGBA8 reference records the spec
    sample-depth rescaling of the source samples; ``source_sample_hash``
    pins the raw big-endian sample bytes the file actually carries."""
    if color_type == 0 and bit_depth == 8:
        samples = gray8_pattern_samples(width, height, variant)
        pixel_bytes = _gray8_pixel_bytes(samples)
        reference_pixels = gray_reference_pixels(samples, 8)
    elif color_type == 0 and bit_depth == 16:
        samples = gray16_pattern_samples(width, height, variant)
        pixel_bytes = _gray16_pixel_bytes(samples)
        reference_pixels = gray_reference_pixels(samples, 16)
    elif color_type == 6 and bit_depth == 16:
        pixels16 = rgba16_pattern_pixels(width, height, variant)
        pixel_bytes = _rgba16_pixel_bytes(pixels16)
        reference_pixels = rgba16_reference_pixels(pixels16)
    else:
        raise ValueError(
            "deep static fixtures cover color type 0 (bit depth 8/16) and "
            "color type 6 (bit depth 16) only"
        )
    png_bytes = build_static_deep_png(
        width,
        height,
        pixel_bytes,
        bit_depth=bit_depth,
        color_type=color_type,
        row_filters=row_filters,
        interlace=interlace,
        idat_chunk_count=idat_chunk_count,
    )
    return {
        "fixture_id": fixture_id,
        "file_name": f"{fixture_id}.png",
        "png_bytes": png_bytes,
        "kind": "static",
        "features": features,
        "width": width,
        "height": height,
        "color_type": color_type,
        "bit_depth": bit_depth,
        "frame_count": 1,
        "reference": {
            "pixels": reference_pixels,
            "pixel_hash": hash_pixels(reference_pixels),
            "source_sample_hash": hash_bytes(b"".join(pixel_bytes)),
        },
        "expected": expected,
    }


def _apng_fixture(
    fixture_id: str,
    *,
    canvas_width: int,
    canvas_height: int,
    frames: list[dict],
    default_image: dict | None = None,
    chunks_after_actl: tuple[tuple[str, bytes], ...] = (),
    features: list[str],
    expected: dict,
) -> dict:
    png_bytes = build_apng(
        canvas_width,
        canvas_height,
        frames,
        default_image=default_image,
        chunks_after_actl=chunks_after_actl,
    )
    playback = simulate_apng_playback(canvas_width, canvas_height, frames)
    default_pixels = (default_image or frames[0])["pixels"]
    return {
        "fixture_id": fixture_id,
        "file_name": f"{fixture_id}.png",
        "png_bytes": png_bytes,
        "kind": "apng",
        "features": features,
        "width": canvas_width,
        "height": canvas_height,
        "color_type": 6,
        "bit_depth": 8,
        "frame_count": len(frames),
        "reference": {
            "default_image_pixels": default_pixels,
            "default_image_pixel_hash": hash_pixels(default_pixels),
            "frames": [
                {
                    "pixels": frame["pixels"],
                    "pixel_hash": hash_pixels(frame["pixels"]),
                    "width": frame["width"],
                    "height": frame["height"],
                    "x_offset": frame["x_offset"],
                    "y_offset": frame["y_offset"],
                    "dispose_op": frame["dispose_op"],
                    "blend_op": frame["blend_op"],
                }
                for frame in frames
            ],
            "display_pixels": playback["display_pixels"],
            "display_hashes": [hash_pixels(pixels) for pixels in playback["display_pixels"]],
            "after_dispose_hashes": [
                hash_pixels(pixels) for pixels in playback["after_dispose_pixels"]
            ],
            "final_output_hash": hash_pixels(playback["final_output_pixels"]),
        },
        "expected": expected,
    }


def build_all_fixtures() -> list[dict]:
    fixtures = []

    fixtures.append(
        _static_fixture(
            "static_multi_idat_even",
            width=8,
            height=8,
            variant=1,
            features=["rgba8", "filter_0", "multi_idat_even_split"],
            idat_chunk_count=4,
            expected={
                "standard_decode_png_rgba": _decode(),
                "adam7_decode_png_adam7_rgba": _reject("png_adam7_interlace_required"),
                "apng_decode_apng_frames": _reject("apng_control_missing"),
                "image_data_chunking": _decode({"idat_chunk_count": 4}),
                "chunk_order_validator": _decode(),
                "textual_metadata_import": _reject("png_textual_metadata_chunk_missing"),
            },
        )
    )

    fixtures.append(
        _static_fixture(
            "static_multi_idat_ragged",
            width=6,
            height=5,
            variant=2,
            features=[
                "rgba8",
                "filter_0",
                "multi_idat_ragged_split",
                "zero_length_idat_chunk",
            ],
            idat_segment_lengths=[0, 1, 2],
            expected={
                "standard_decode_png_rgba": _decode(),
                "image_data_chunking": _decode({"idat_chunk_count": 4}),
                "chunk_order_validator": _decode(),
            },
        )
    )

    for filter_type, name in ((1, "sub"), (2, "up"), (3, "average"), (4, "paeth")):
        fixtures.append(
            _static_fixture(
                f"static_filter_{name}",
                width=6,
                height=6,
                variant=2 + filter_type,
                features=["rgba8", f"filter_{filter_type}_all_rows"],
                row_filters=[filter_type],
                expected={
                    "standard_decode_png_rgba": _reject("png_filter_unsupported"),
                    "image_data_chunking": _decode({"idat_chunk_count": 1}),
                    "chunk_order_validator": _decode(),
                },
            )
        )

    fixtures.append(
        _static_fixture(
            "static_filter_mixed",
            width=8,
            height=8,
            variant=7,
            features=["rgba8", "filters_mixed_per_row_0_to_4"],
            row_filters=[0, 1, 2, 3, 4, 3, 2, 1],
            expected={
                "standard_decode_png_rgba": _reject("png_filter_unsupported"),
                "image_data_chunking": _decode({"idat_chunk_count": 1}),
                "chunk_order_validator": _decode(),
            },
        )
    )

    fixtures.append(
        _static_fixture(
            "static_ancillary_interleaved",
            width=8,
            height=8,
            variant=8,
            features=[
                "rgba8",
                "filter_0",
                "gama_before_idat",
                "phys_before_idat",
                "text_before_idat",
                "text_after_idat",
            ],
            pre_idat_chunks=(GAMA_CHUNK, PHYS_CHUNK, TEXT_SOFTWARE_CHUNK),
            post_idat_chunks=(TEXT_COMMENT_CHUNK,),
            expected={
                "standard_decode_png_rgba": _decode(),
                "image_data_chunking": _decode({"idat_chunk_count": 1}),
                "chunk_order_validator": _decode(),
                "textual_metadata_import": _reject("png_textual_metadata_chunk_missing"),
            },
        )
    )

    fixtures.append(
        _static_fixture(
            "adam7_basic",
            width=10,
            height=9,
            variant=9,
            features=["rgba8", "adam7_interlace", "filter_0", "non_power_of_two_dimensions"],
            interlace=1,
            expected={
                "standard_decode_png_rgba": _reject("png_method_unsupported"),
                "adam7_decode_png_adam7_rgba": _decode(),
                "image_data_chunking": _reject("png_interlace_unsupported"),
                "chunk_order_validator": _decode(),
            },
        )
    )

    fixtures.append(
        _static_fixture(
            "adam7_mixed_filters_multi_idat",
            width=8,
            height=8,
            variant=10,
            features=["rgba8", "adam7_interlace", "filters_mixed_per_reduced_row", "multi_idat"],
            interlace=1,
            row_filters=[4, 3, 2, 1, 0],
            idat_chunk_count=3,
            expected={
                "standard_decode_png_rgba": _reject("png_method_unsupported"),
                "adam7_decode_png_adam7_rgba": _decode(),
                "chunk_order_validator": _decode({"idat_chunk_count": 3}),
            },
        )
    )

    fixtures.append(
        _deep_static_fixture(
            "gray8_multi_idat_mixed_filters",
            width=7,
            height=6,
            color_type=0,
            bit_depth=8,
            variant=40,
            features=[
                "gray8",
                "color_type_0",
                "filters_mixed_per_row_0_to_4",
                "multi_idat_even_split",
                "filter_bpp_1",
            ],
            row_filters=[0, 1, 2, 3, 4, 2],
            idat_chunk_count=2,
            expected={
                "standard_decode_png_rgba": _reject("png_color_type_unsupported"),
                "adam7_decode_png_adam7_rgba": _reject("png_color_type_unsupported"),
                "apng_decode_apng_frames": _reject("apng_color_model_unsupported"),
                "apng_filtered_frame_data": _reject("apng_color_model_unsupported"),
                "apng_partial_frame_playback": _reject("apng_color_model_unsupported"),
                "image_data_chunking": _decode({"idat_chunk_count": 2}),
                "chunk_order_validator": _decode(),
                "textual_metadata_import": _reject("png_color_type_unsupported"),
                "deep_color_decode": _decode(),
                "adam7_deep_color_decode": _reject("png_adam7_deep_color_interlace_required"),
            },
        )
    )

    fixtures.append(
        _deep_static_fixture(
            "gray16_multi_idat_mixed_filters",
            width=6,
            height=5,
            color_type=0,
            bit_depth=16,
            variant=41,
            features=[
                "gray16",
                "color_type_0",
                "bit_depth_16",
                "filters_mixed_per_row_0_to_4",
                "multi_idat_even_split",
                "filter_bpp_2",
            ],
            row_filters=[4, 2, 1, 3, 0],
            idat_chunk_count=3,
            expected={
                "standard_decode_png_rgba": _reject("png_bit_depth_unsupported"),
                "adam7_decode_png_adam7_rgba": _reject("png_bit_depth_unsupported"),
                "apng_decode_apng_frames": _reject("apng_color_model_unsupported"),
                "apng_filtered_frame_data": _reject("apng_color_model_unsupported"),
                "apng_partial_frame_playback": _reject("apng_color_model_unsupported"),
                "image_data_chunking": _decode({"idat_chunk_count": 3}),
                "chunk_order_validator": _decode(),
                "textual_metadata_import": _reject("png_bit_depth_unsupported"),
                "deep_color_decode": _decode(),
                "adam7_deep_color_decode": _reject("png_adam7_deep_color_interlace_required"),
            },
        )
    )

    fixtures.append(
        _deep_static_fixture(
            "rgba16_basic",
            width=5,
            height=4,
            color_type=6,
            bit_depth=16,
            variant=42,
            features=["rgba16", "bit_depth_16", "filter_0", "single_idat"],
            row_filters=[0],
            expected={
                "standard_decode_png_rgba": _reject("png_bit_depth_unsupported"),
                "adam7_decode_png_adam7_rgba": _reject("png_bit_depth_unsupported"),
                "apng_decode_apng_frames": _reject("apng_color_model_unsupported"),
                "apng_filtered_frame_data": _reject("apng_color_model_unsupported"),
                "apng_partial_frame_playback": _reject("apng_color_model_unsupported"),
                "image_data_chunking": _decode({"idat_chunk_count": 1}),
                "chunk_order_validator": _decode(),
                "textual_metadata_import": _reject("png_bit_depth_unsupported"),
                "deep_color_decode": _decode(),
                "adam7_deep_color_decode": _reject("png_adam7_deep_color_interlace_required"),
            },
        )
    )

    fixtures.append(
        _deep_static_fixture(
            "rgba16_paeth_sub_multi_idat",
            width=8,
            height=6,
            color_type=6,
            bit_depth=16,
            variant=43,
            features=[
                "rgba16",
                "bit_depth_16",
                "filters_sub_paeth_up_average",
                "multi_idat_even_split",
                "filter_bpp_8",
            ],
            row_filters=[1, 4, 2, 3, 4, 1],
            idat_chunk_count=3,
            expected={
                "standard_decode_png_rgba": _reject("png_bit_depth_unsupported"),
                "adam7_decode_png_adam7_rgba": _reject("png_bit_depth_unsupported"),
                "apng_decode_apng_frames": _reject("apng_color_model_unsupported"),
                "apng_filtered_frame_data": _reject("apng_color_model_unsupported"),
                "apng_partial_frame_playback": _reject("apng_color_model_unsupported"),
                "image_data_chunking": _decode({"idat_chunk_count": 3}),
                "chunk_order_validator": _decode(),
                "textual_metadata_import": _reject("png_bit_depth_unsupported"),
                "deep_color_decode": _decode(),
                "adam7_deep_color_decode": _reject("png_adam7_deep_color_interlace_required"),
            },
        )
    )

    fixtures.append(
        _deep_static_fixture(
            "rgba16_adam7_mixed_filters_multi_idat",
            width=6,
            height=7,
            color_type=6,
            bit_depth=16,
            variant=44,
            features=[
                "rgba16",
                "bit_depth_16",
                "adam7_interlace",
                "filters_mixed_per_reduced_row",
                "multi_idat",
                "non_power_of_two_dimensions",
                "filter_bpp_8",
            ],
            row_filters=[4, 3, 1, 0, 2],
            interlace=1,
            idat_chunk_count=2,
            expected={
                "standard_decode_png_rgba": _reject("png_bit_depth_unsupported"),
                "adam7_decode_png_adam7_rgba": _reject("png_bit_depth_unsupported"),
                "apng_decode_apng_frames": _reject("apng_color_model_unsupported"),
                "apng_filtered_frame_data": _reject("apng_color_model_unsupported"),
                "apng_partial_frame_playback": _reject("apng_color_model_unsupported"),
                "image_data_chunking": _reject("png_interlace_unsupported"),
                "chunk_order_validator": _decode(),
                "textual_metadata_import": _reject("png_bit_depth_unsupported"),
                "deep_color_decode": _reject("png_interlace_unsupported"),
                "adam7_deep_color_decode": _decode({"idat_chunk_count": 2}),
            },
        )
    )

    canvas_width = 8
    canvas_height = 8

    base = opaque_pattern_pixels(canvas_width, canvas_height, 20)
    pulse = opaque_pattern_pixels(canvas_width, canvas_height, 21)
    fixtures.append(
        _apng_fixture(
            "apng_basic_split_fdat",
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            frames=[
                make_frame(
                    base,
                    width=canvas_width,
                    height=canvas_height,
                    delay_num=1,
                    delay_den=5,
                    data_chunk_count=2,
                ),
                make_frame(
                    pulse,
                    width=canvas_width,
                    height=canvas_height,
                    delay_num=1,
                    delay_den=5,
                    data_chunk_count=3,
                ),
            ],
            chunks_after_actl=(TEXT_SOFTWARE_CHUNK,),
            features=[
                "apng",
                "two_full_canvas_frames",
                "default_image_in_animation",
                "idat_split",
                "fdat_split_across_chunks",
                "text_between_actl_and_fctl",
            ],
            expected={
                "standard_decode_png_rgba": _decode(),
                "apng_decode_apng_frames": _decode(),
                "apng_filtered_frame_data": _decode(),
                "apng_partial_frame_playback": _decode(),
                "image_data_chunking": _decode({"idat_chunk_count": 2, "fdat_chunk_count": 3}),
                "chunk_order_validator": _decode(),
            },
        )
    )

    default_only = opaque_pattern_pixels(canvas_width, canvas_height, 22)
    animated_a = opaque_pattern_pixels(canvas_width, canvas_height, 23)
    patch_b = opaque_pattern_pixels(4, 3, 24)
    fixtures.append(
        _apng_fixture(
            "apng_default_image_not_animated",
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            default_image=make_frame(
                default_only,
                width=canvas_width,
                height=canvas_height,
            ),
            frames=[
                make_frame(animated_a, width=canvas_width, height=canvas_height),
                make_frame(
                    patch_b,
                    width=4,
                    height=3,
                    x_offset=2,
                    y_offset=4,
                    data_chunk_count=2,
                ),
            ],
            features=[
                "apng",
                "default_image_not_in_animation",
                "all_frames_in_fdat",
                "sub_canvas_frame_region",
                "fdat_split_across_chunks",
            ],
            expected={
                "standard_decode_png_rgba": _decode(),
                "apng_decode_apng_frames": _reject("apng_default_frame_control_missing"),
                "apng_filtered_frame_data": _reject("apng_default_frame_unsupported"),
                "apng_partial_frame_playback": _reject("apng_default_frame_unsupported"),
                "image_data_chunking": _reject("apng_default_frame_unsupported"),
                "chunk_order_validator": _decode(),
            },
        )
    )

    dispose_base = opaque_pattern_pixels(canvas_width, canvas_height, 25)
    dispose_patch = opaque_pattern_pixels(4, 3, 26)
    fixtures.append(
        _apng_fixture(
            "apng_dispose_background",
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            frames=[
                make_frame(
                    dispose_base,
                    width=canvas_width,
                    height=canvas_height,
                    dispose_op=1,
                ),
                make_frame(
                    dispose_patch,
                    width=4,
                    height=3,
                    x_offset=2,
                    y_offset=2,
                ),
            ],
            features=["apng", "dispose_op_background", "sub_canvas_frame_region"],
            expected={
                "standard_decode_png_rgba": _decode(),
                "apng_decode_apng_frames": _reject("apng_frame_control_unsupported"),
                "apng_filtered_frame_data": _reject("apng_dispose_op_unsupported"),
                "apng_partial_frame_playback": _decode(),
                "image_data_chunking": _reject("apng_dispose_op_unsupported"),
                "chunk_order_validator": _decode(),
            },
        )
    )

    previous_base = opaque_pattern_pixels(canvas_width, canvas_height, 27)
    previous_patch = opaque_pattern_pixels(3, 3, 28)
    final_patch = opaque_pattern_pixels(2, 4, 29)
    fixtures.append(
        _apng_fixture(
            "apng_dispose_previous",
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            frames=[
                make_frame(previous_base, width=canvas_width, height=canvas_height),
                make_frame(
                    previous_patch,
                    width=3,
                    height=3,
                    x_offset=4,
                    y_offset=1,
                    dispose_op=2,
                ),
                make_frame(
                    final_patch,
                    width=2,
                    height=4,
                    x_offset=1,
                    y_offset=3,
                ),
            ],
            features=["apng", "three_frames", "dispose_op_previous", "sub_canvas_frame_regions"],
            expected={
                "standard_decode_png_rgba": _decode(),
                "apng_decode_apng_frames": _reject("apng_frame_count_unsupported"),
                "apng_filtered_frame_data": _reject("apng_dispose_op_unsupported"),
                "apng_partial_frame_playback": _decode(),
                "image_data_chunking": _reject("apng_dispose_op_unsupported"),
                "chunk_order_validator": _decode(),
            },
        )
    )

    over_base = quantized_pixels(canvas_width, canvas_height, 1, 255)
    over_veil = quantized_pixels(canvas_width, canvas_height, 2, 51)
    fixtures.append(
        _apng_fixture(
            "apng_blend_over",
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            frames=[
                make_frame(over_base, width=canvas_width, height=canvas_height),
                make_frame(
                    over_veil,
                    width=canvas_width,
                    height=canvas_height,
                    blend_op=1,
                ),
            ],
            features=["apng", "blend_op_over", "semi_transparent_frame"],
            expected={
                "standard_decode_png_rgba": _decode(),
                "apng_decode_apng_frames": _reject("apng_frame_control_unsupported"),
                "apng_filtered_frame_data": _reject("apng_blend_op_unsupported"),
                "apng_partial_frame_playback": _decode(),
                "image_data_chunking": _reject("apng_blend_op_unsupported"),
                "chunk_order_validator": _decode(),
            },
        )
    )

    region_base = opaque_pattern_pixels(canvas_width, canvas_height, 30)
    region_patch = opaque_pattern_pixels(4, 3, 31)
    fixtures.append(
        _apng_fixture(
            "apng_subcanvas_regions",
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            frames=[
                make_frame(region_base, width=canvas_width, height=canvas_height),
                make_frame(
                    region_patch,
                    width=4,
                    height=3,
                    x_offset=3,
                    y_offset=2,
                    data_chunk_count=2,
                ),
            ],
            features=["apng", "sub_canvas_frame_region", "fdat_split_across_chunks"],
            expected={
                "standard_decode_png_rgba": _decode(),
                "apng_decode_apng_frames": _reject("apng_frame_control_unsupported"),
                "apng_filtered_frame_data": _decode(),
                "apng_partial_frame_playback": _decode(),
                "image_data_chunking": _decode({"idat_chunk_count": 1, "fdat_chunk_count": 2}),
                "chunk_order_validator": _decode(),
            },
        )
    )

    filtered_base = opaque_pattern_pixels(canvas_width, canvas_height, 32)
    filtered_pulse = opaque_pattern_pixels(canvas_width, canvas_height, 33)
    fixtures.append(
        _apng_fixture(
            "apng_filtered_frames_split_fdat",
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            frames=[
                make_frame(
                    filtered_base,
                    width=canvas_width,
                    height=canvas_height,
                    row_filters=[1, 2, 3, 4],
                ),
                make_frame(
                    filtered_pulse,
                    width=canvas_width,
                    height=canvas_height,
                    row_filters=[4, 3, 2, 1],
                    data_chunk_count=2,
                ),
            ],
            features=[
                "apng",
                "filters_1_to_4_in_frame_data",
                "fdat_split_across_chunks",
            ],
            expected={
                "standard_decode_png_rgba": _reject("png_filter_unsupported"),
                "apng_decode_apng_frames": _reject("apng_filter_unsupported"),
                "apng_filtered_frame_data": _decode(),
                "apng_partial_frame_playback": _reject("apng_filter_unsupported"),
                "image_data_chunking": _decode({"idat_chunk_count": 1, "fdat_chunk_count": 2}),
                "chunk_order_validator": _decode(),
            },
        )
    )

    return fixtures


# ---------------------------------------------------------------------------
# Manifest and corpus output
# ---------------------------------------------------------------------------


def _manifest_reference(fixture: dict) -> dict:
    reference = fixture["reference"]
    if fixture["kind"] == "static":
        manifest_reference = {"pixel_hash": reference["pixel_hash"]}
        if "source_sample_hash" in reference:
            manifest_reference["source_sample_hash"] = reference["source_sample_hash"]
        return manifest_reference
    return {
        "default_image_pixel_hash": reference["default_image_pixel_hash"],
        "frame_pixel_hashes": [frame["pixel_hash"] for frame in reference["frames"]],
        "display_hashes": reference["display_hashes"],
        "after_dispose_hashes": reference["after_dispose_hashes"],
        "final_output_hash": reference["final_output_hash"],
    }


def build_manifest(fixtures: list[dict]) -> dict:
    return {
        "corpus_id": CORPUS_ID,
        "generator": "labs/workshop_editor/foreign_fixture_writer.py",
        "spec_source": SPEC_URL,
        "deterministic": True,
        "license": (
            "Generated in-repo from the public W3C PNG specification; contains no "
            "third-party image data."
        ),
        "pixel_hash_model": (
            "sha256 over concatenated RGBA bytes, row-major; 16-bit fixtures "
            "record the RGBA8 reference after the specification's sample-depth "
            "rescaling (round(sample * 255 / 65535)) plus a source_sample_hash "
            "over the raw big-endian sample bytes carried by the file"
        ),
        "fixture_count": len(fixtures),
        "known_deficiencies": [],
        "coverage_notes": {
            "closed": (
                "Grayscale (color type 0, bit depths 8 and 16) and deep-color "
                "RGBA (color type 6, bit depth 16) foreign fixtures are covered, "
                "including 16-bit multi-IDAT streams with non-zero filters "
                "(filter bpp 2 for gray16, 8 for rgba16) and one 16-bit RGBA "
                "Adam7 fixture; png_deep_color_sidecar_decoder and "
                "png_adam7_deep_color_cross_product decode them pixel-exact "
                "against the writer's independent references."
            ),
            "out_of_scope": [
                "indexed color type 3 (claimed by png_deep_color_sidecar_decoder "
                "at bit depths 1/2/4 but not yet covered by foreign fixtures)",
                "truecolor color type 2 and grayscale-alpha color type 4 "
                "(claimed by png_deep_color_sidecar_decoder but not yet covered "
                "by foreign fixtures)",
                "low-bit grayscale (bit depths 1/2/4)",
                "grayscale or 16-bit APNG frame data (no APNG decoder in the "
                "conformance sweep claims frame data beyond 8-bit RGBA)",
            ],
        },
        "fixtures": [
            {
                "fixture_id": fixture["fixture_id"],
                "file_name": fixture["file_name"],
                "kind": fixture["kind"],
                "byte_count": len(fixture["png_bytes"]),
                "sha256": hash_bytes(fixture["png_bytes"]),
                "features": fixture["features"],
                "width": fixture["width"],
                "height": fixture["height"],
                "color_type": fixture["color_type"],
                "bit_depth": fixture["bit_depth"],
                "frame_count": fixture["frame_count"],
                "reference": _manifest_reference(fixture),
                "expected": fixture["expected"],
            }
            for fixture in fixtures
        ],
    }


def _readme_text(manifest: dict) -> str:
    lines = [
        "# Foreign Fixture Corpus",
        "",
        "Spec-derived PNG/APNG conformance fixtures for the workshop_editor",
        "decoders. Every file is generated in-repo by",
        "`labs/workshop_editor/foreign_fixture_writer.py`, an independent",
        "encoder written directly from the W3C PNG specification, Third",
        f"Edition ({SPEC_URL}), including the APNG chapter. The corpus is",
        "license-clean: it contains no third-party image data, only",
        "deterministic synthetic pixel patterns.",
        "",
        "The writer deliberately shares no code with the lab encoders so",
        "encoder bugs cannot cancel decoder bugs. Features covered:",
        "multi-IDAT streams split at arbitrary byte boundaries (including a",
        "zero-length IDAT chunk), scanline filters 0-4 (uniform and mixed",
        "per row), interleaved ancillary chunks (gAMA, pHYs, tEXt) at legal",
        "positions, Adam7 interlace from an independent pass extraction,",
        "APNG dispose ops none/background/previous, blend op over,",
        "sub-canvas frame regions, a default image excluded from the",
        "animation, and fdAT payloads split across chunks with consecutive",
        "sequence numbers.",
        "",
        "Grayscale and deep-color coverage: 8-bit grayscale (color type 0),",
        "16-bit grayscale, and 16-bit RGBA fixtures, including 16-bit",
        "multi-IDAT streams with non-zero filters (byte-oriented filtering",
        "with bpp 2 for gray16 and bpp 8 for rgba16) and one 16-bit RGBA",
        "Adam7 fixture for the Adam7/deep-color cross-product decoder.",
        "16-bit references record the specification's sample-depth",
        "rescaling to RGBA8 (round(sample * 255 / 65535)) plus a hash of",
        "the raw big-endian samples. Still out of scope (see the manifest",
        "coverage_notes): indexed color type 3, truecolor color type 2,",
        "grayscale-alpha color type 4, low-bit grayscale (1/2/4), and",
        "grayscale/16-bit APNG frame data (no APNG decoder in the sweep",
        "claims frame data beyond 8-bit RGBA).",
        "",
        "`manifest.json` describes every fixture: features, dimensions,",
        "frame count, reference pixel hashes computed by the writer's own",
        "reference model, and the expected outcome (decode or typed",
        "rejection family) per workshop decoder.",
        "",
        "Regenerate with:",
        "",
        "```",
        "python labs/workshop_editor/foreign_fixture_writer.py",
        "```",
        "",
        f"- Fixtures: {manifest['fixture_count']}",
        f"- Corpus id: {manifest['corpus_id']}",
    ]
    return "\n".join(lines) + "\n"


def write_foreign_fixture_corpus(output_dir: Path) -> dict:
    fixtures = build_all_fixtures()
    manifest = build_manifest(fixtures)
    output_dir.mkdir(parents=True, exist_ok=True)
    for fixture in fixtures:
        (output_dir / fixture["file_name"]).write_bytes(fixture["png_bytes"])
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(_readme_text(manifest), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write the spec-derived foreign PNG/APNG fixture corpus.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    manifest = write_foreign_fixture_corpus(args.output_dir)
    print(
        json.dumps(
            {
                "corpus_id": manifest["corpus_id"],
                "output_dir": str(args.output_dir).replace("\\", "/"),
                "fixture_count": manifest["fixture_count"],
                "fixtures": [fixture["file_name"] for fixture in manifest["fixtures"]],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
