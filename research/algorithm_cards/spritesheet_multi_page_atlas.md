# Algorithm Card: Spritesheet Multi-Page Atlas

## Purpose

Extend the arbitrary atlas proof from a single page to a generated multi-page
atlas bundle with per-page PNG carriers, a page manifest, frame-to-page
bindings, and sidecar-driven runtime page-switch sampling.

## Mathematical Basis

The lab models a page atlas as deterministic rectangle packing over a sequence
of bounded pages:

```txt
region_i = trim(canonical_frame_i)
page_j, placement_i = first_fit(region_i, pages, rotation_order, padding)
valid_bundle = every(page_hash_j matches manifest_j)
             and every(frame_i.page_index exists)
             and no_overlap(placements on page_j)
canonical_frame_i = paste(unrotate(crop(page_j, placement_i)), source_size, trim_i)
```

The first-fit scan respects page order, rotation candidate order, y scan order,
and x scan order. Tall non-square regions try 90-degree rotation first when the
policy allows rotation.

## Inputs

- Current valid SLIP profiles.
- First generated grid for each current valid profile.
- Seven deterministic 8x8 canonical source frames per grid.
- Sidecar metadata with page manifests, page hashes, frame page indices,
  packed rectangles, trim/source rectangles, rotation flags, frame durations,
  and canonical frame hashes.

## Outputs

- Three atlas page PNGs per profile in the Stage 0 corpus.
- One sidecar file per profile with page and frame bindings.
- Aggregate bundle metadata with page count and content hash.
- Runtime playback samples crossing more than one atlas page.
- Invalid-probe rejection report.

## Strengths

- Closes generated multi-page atlas fixtures without package code.
- Verifies page count, page hash, missing-page, unknown-page, bounds, frame
  hash, and playback-order rejection.
- Reconstructs canonical frames exactly from page-local rectangles and sidecar
  trim/rotation metadata.
- Preserves SLIP/grid semantics through sidecar restore rather than treating
  atlas page pixels as semantic truth.

## Weaknesses

- Uses generated lab pages, not editor-authored atlas exports.
- Covers one first-fit page policy and 0/90-degree rotations only.
- Runtime playback is deterministic metadata sampling, not production renderer
  draw-call evidence.
- Does not prove live external editor rewrite preservation.

## Failure Modes

- Missing atlas pages must be rejected.
- Page content-hash mismatches must be rejected.
- Frame references to unknown pages must be rejected.
- Rectangles outside their page bounds must be rejected.
- Packed frame hash mismatches must be rejected.
- Duplicate or non-integer playback order values must be rejected.

## Integration Risk

Medium.

## License Status

No external code selected. libGDX TexturePacker documentation is a workflow
anchor only; PNG remains the page image carrier.

## Prototype Result

Stage 0 generated multi-page atlas proof completed on 2026-05-14.

```txt
profile_count: 3
bundle_roundtrip_success_count: 3
invalid_probe_rejected_count: 6
bundle_roundtrip_success_rate: 1.0
mean_semantic_fidelity: 1.0
mean_reconstructed_frame_fidelity: 1.0
mean_runtime_frame_fidelity: 1.0
mean_page_count: 3.0
mean_frame_count: 7.0
```

## Decision

Keep as active prototype. This closes Stage 0 generated multi-page atlas page
manifest and frame-page binding evidence for the current profile corpus, but it
does not close editor-authored atlas fixtures, production renderer playback,
live external editor rewrite validation, full project-format coverage, package
runtime integration, manual readability calibration, or profile-weighted
evolution.

## Go/No-Go Gate

Promote only after production runtime draw calls and real editor-exported
multi-page atlas fixtures can consume or reject the same page manifest,
per-page hashes, and frame-to-page bindings without losing Mechagotchi sidecar
semantics.
