"""Deterministic included-asset hashing for the mecha_engine package surface.

Contract sources:

- research/package_specs/mecha_engine_provenance_contract_gate.md
  ("Hash Acceptance")
- research/package_specs/mecha_engine_module_interfaces.md ("provenance")

Verbatim semantic port of the Stage 0 research hashing (the asset_pipeline
lab): ``sha256`` over file bytes, and a ``sha256-tree`` directory digest
that folds in each child file's path *relative to the hashed directory*
(POSIX separators) alongside its content digest, in deterministic sorted
case-sensitive relative POSIX-string order (DR 0061). Because only paths relative to the hashed root enter
the digest, the result is independent of where the repository lives on
disk; callers anchor ledger ``included_path`` strings on an explicit
``repo_root`` (the ledger records repo-relative POSIX path strings, per
the repo-root path-anchoring convention). DR 0061 preserves the original
Windows baseline and identifies the corrected current ledger separately.
No network access and no environment-dependent
metadata (names and bytes only — never timestamps, permissions, or
absolute paths) enter any digest.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def hash_included_path(path: str | Path) -> dict:
    """Return deterministic hash metadata for an included file or directory.

    Files return ``{"hash_algorithm": "sha256", "hash": <64 hex>}``;
    directories return ``{"hash_algorithm": "sha256-tree", "hash": <64 hex>}``.
    Absent paths raise ``FileNotFoundError``.
    """
    path = Path(path)
    if path.is_file():
        return {
            "hash_algorithm": "sha256",
            "hash": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    if path.is_dir():
        digest = hashlib.sha256()
        for child in sorted(
            (item for item in path.rglob("*") if item.is_file()),
            key=lambda item: item.relative_to(path).as_posix(),
        ):
            digest.update(child.relative_to(path).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(hashlib.sha256(child.read_bytes()).hexdigest().encode("ascii"))
            digest.update(b"\0")
        return {"hash_algorithm": "sha256-tree", "hash": digest.hexdigest()}
    raise FileNotFoundError(path)
