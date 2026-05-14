# Algorithm Card: Aseprite External Asset Resolver Matrix

## Purpose

Broaden Aseprite/LibreSprite External Files Chunk evidence from a direct
generated asset list to a bounded resolver matrix.

## Mathematical Basis

The resolver treats Aseprite external file entries as a hash-bound manifest:

```txt
manifest_entry = (entry_id, type, name, media_type, content_hash)
resolved_asset_hash = sha256(payload_text)
resolver_ok = manifest_entry.content_hash == resolved_asset_hash
```

Semantic restore is delegated to the existing document-variant importer only
after the resolver proves that every required asset is present, unambiguous,
path-safe, and hash-matched.

## Inputs

- Valid SLIP profile
- Generated profile-aligned grid
- Aseprite document-variant project bytes
- External asset manifest from the project metadata
- Resolver input using one bounded policy:
  - direct manifest
  - relative file map
  - content-addressed pool
  - multi-root priority

## Outputs

- Resolved external asset list
- Restored semantic grid
- Resolver policy summary
- Invalid-probe rejection report

## External Anchor

The Aseprite file-format specification anchors External Files Chunk `0x2008`.

Source: <https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md>

## Strengths

- Separates resolver trust from Aseprite document parsing.
- Covers all current profiles, all three current document variants, and four
  resolver policies.
- Rejects missing assets, tampered payloads, ambiguous candidates, path
  traversal, and unsupported resolver policy IDs.
- Preserves the existing document-variant semantic restore path.

## Weaknesses

- Resolver inputs are generated Stage 0 fixtures, not editor-authored project
  files.
- Does not execute Aseprite or LibreSprite.
- Does not prove arbitrary Aseprite project schemas.
- Does not prove live open-save behavior.

## Failure Modes

- Missing resolver source must reject import.
- Payload hash mismatch must reject import before document-variant restore.
- Duplicate candidate paths for the same manifest entry must reject import.
- Relative paths containing `..` or absolute roots must reject import.
- Unknown resolver policy IDs must reject import.

## Integration Risk

Medium.

## License Status

No external editor code selected. The Aseprite specification is used as a
format reference only.

## Prototype Result

Stage 0 resolver matrix completed on 2026-05-14.

```txt
profile_count: 3
resolver_policy_count: 4
resolver_roundtrip_success_count: 36
invalid_probe_rejected_count: 5
resolver_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
external_asset_resolution_rate: 1.0
invalid_probe_rejection_rate: 1.0
```

## Decision

Keep as a bounded resolver prototype. This closes only generated direct,
relative-path, content-addressed, and multi-root resolver behavior for the
current document-variant corpus. Live editor validation, editor-authored
Aseprite variants, arbitrary project schemas, full project-format coverage,
package runtime integration, manual readability calibration, and
profile-weighted evolution remain blocked.
