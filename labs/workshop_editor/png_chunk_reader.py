"""Shared strict PNG chunk reader and bounded zlib inflation for workshop labs.

Every workshop lab that needs raw PNG chunk access reads through this module
and wraps ``PNGChunkError`` into its own typed error family at the call
boundary, so each lab keeps its existing public error surface.
"""

import binascii
import struct
import zlib


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class PNGChunkError(Exception):
    def __init__(self, family: str, message: str):
        super().__init__(message)
        self.family = family
        self.message = message


def read_png_chunks(png_bytes: bytes) -> list[dict]:
    """Read (type, payload) chunks strictly: signature, CRC, ASCII chunk
    types, and no trailing bytes after IEND."""
    if not png_bytes.startswith(PNG_SIGNATURE):
        raise PNGChunkError("png_signature_invalid", "PNG signature is invalid")
    chunks = []
    offset = len(PNG_SIGNATURE)
    while offset < len(png_bytes):
        if offset + 12 > len(png_bytes):
            raise PNGChunkError("png_chunk_truncated", "PNG chunk header is truncated")
        length = struct.unpack(">I", png_bytes[offset : offset + 4])[0]
        chunk_type = png_bytes[offset + 4 : offset + 8]
        data_start = offset + 8
        data_end = data_start + length
        crc_end = data_end + 4
        if crc_end > len(png_bytes):
            raise PNGChunkError("png_chunk_truncated", "PNG chunk payload is truncated")
        payload = png_bytes[data_start:data_end]
        expected_crc = struct.unpack(">I", png_bytes[data_end:crc_end])[0]
        actual_crc = binascii.crc32(payload, binascii.crc32(chunk_type)) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise PNGChunkError("png_crc_mismatch", f"CRC mismatch in {chunk_type!r}")
        try:
            chunk_name = chunk_type.decode("ascii")
        except UnicodeDecodeError as exc:
            raise PNGChunkError("png_chunk_type_invalid", "chunk type must be ASCII") from exc
        chunks.append({"type": chunk_name, "payload": payload})
        offset = crc_end
        if chunk_type == b"IEND":
            break
    if offset != len(png_bytes):
        raise PNGChunkError("png_trailing_bytes", "PNG has trailing bytes after IEND")
    return chunks


def bounded_decompress(data: bytes, max_length: int) -> bytes:
    """Inflate ``data`` refusing to produce more than ``max_length`` bytes.

    Callers keep their existing exact-length post-checks; this only guards
    against decompression bombs and preserves ``zlib.decompress`` strictness
    for truncated streams.
    """
    if max_length <= 0:
        # zlib treats max_length=0 as "no limit", which would silently disarm
        # the bomb guard for a zero or negative declared size.
        raise PNGChunkError(
            "zlib_output_overflow", "declared decompressed size must be positive"
        )
    decompressor = zlib.decompressobj()
    try:
        payload = decompressor.decompress(data, max_length)
    except zlib.error as error:
        raise PNGChunkError("zlib_stream_invalid", f"zlib stream invalid: {error}") from None
    if decompressor.unconsumed_tail:
        raise PNGChunkError("zlib_output_overflow", "decompressed payload exceeds declared size")
    if not decompressor.eof:
        raise PNGChunkError("zlib_stream_invalid", "zlib stream is incomplete or truncated")
    return payload
