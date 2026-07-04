# Mechagotchi Research Report v0.7

Date: 2026-07-04

## Executive Summary

The post-v0.6 research continuation consolidates the seven remediation
reports dated 2026-07-04 that postdate the v0.6 manifest. Together with the
three remediation reports already consolidated in v0.6, they complete the
code-review remediation wave driven by
`docs/03-code_review/2026-07-04-code_review.md`.

The review baseline was 376 tests with 374 passing (2 environment-coupled
failures). After this wave the full sweep is 455 tests across 12 labs, all
green. Every H-severity and M-severity finding in the review is resolved,
with one deliberate exception: the dependency-manifest decision itself (the
M-15 remainder) stays an explicit open decision for the maintainer. Of the
L-severity findings, only L-12 (descriptor-axis degeneracy on the shipped
corpus, now visible via the `descriptor_bin_spread` diagnostic) remains open
as a calibration item, and the foreign-fixture corpus records one honest
coverage gap: no grayscale/deep-color foreign fixtures yet.

The wave contains two findings of independent interest beyond the fixes
themselves. First, the foreign-fixture conformance corpus caught a
wrong-pixels bug (dispose/blend ops accepted but silently ignored) that
self-referential round-trip tests could never have found. Second, the
gate-integrity pass recorded an honest negative result: the M-12 confidence
scale mismatch flagged by the review was latent, not active — the measured
gain was unchanged to six decimal places after the fix.

The key conclusion remains conservative. This wave hardens the labs; it does
not advance the research frontier. There is still no `packages/mecha_engine`
code, no package runtime lifecycle integration, no manual readability
calibration, no live external editor validation, and no profile-weighted
evolution claim.

This report consolidates and links the underlying experiment reports; it does
not replace them.

## Research Scope

This report consolidates the post-v0.6 remediation sequence:

1. Harden the `labs/workshop_editor/` decoder family: typed errors for
   malformed metadata JSON, one shared strict PNG chunk reader, bounded zlib
   inflation, zip-member caps, and exception narrowing at import boundaries
   (findings H-04, H-05, M-01, M-02, M-03, M-04, L-07, L-15).
2. Align `labs/grid_genome/validator.py` with the full
   `grid_genome.schema.json` surface and document the lab invariants layered
   on top of it (M-07, M-08, L-01 remainder, L-02, L-03, L-05), including the
   offspring `grid_id` regression the stricter validator exposed in-flight.
3. Restore gate integrity across six small labs: evidence-driven negative
   probes, per-record ingest isolation, like-for-like confidence baselines,
   and evidence-aware promotion blockers (M-09, M-10, M-11, M-12, L-09,
   L-10, L-11, L-13).
4. Break the self-referential-fixture limitation with an independent
   spec-derived foreign-fixture corpus and conformance sweep (L-06).
5. Retire structural debt: single-source the duplicated grid_genome helpers
   with byte-equivalence proof (L-04), anchor all lab paths on the repo root
   (L-08), and backfill the research ledger (L-14, recorded in the
   code-review TODO table and `research/README.md`; no dedicated experiment
   report).

## Primary Artifacts

| Area | Artifact |
| --- | --- |
| Shared PNG chunk reader / bounded inflate | `labs/workshop_editor/png_chunk_reader.py` |
| Schema-aligned grid validator | `labs/grid_genome/validator.py` |
| Runtime boundary gate (evidence probes) | `data/architecture/mecha_engine_runtime_boundary_gate_stage0.json` |
| Snapshot ingest (per-record isolation) | `data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json` |
| Promotion gate (evidence-aware blockers) | `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json` |
| Independent foreign-fixture writer | `labs/workshop_editor/foreign_fixture_writer.py` |
| Foreign-fixture corpus manifest | `data/foreign_fixtures/manifest.json` |
| Single-source grid_genome helpers | `labs/grid_genome/grid_helpers.py` |
| Schema-bounded offspring lineage | `data/workshop_editor/slip_offspring_lineage_gate_stage0.json` |

## Cluster Results

### 1. Decoder and Boundary Hardening (2 reports)

| Fix | Findings | Evidence Anchor |
| --- | --- | ---: |
| Typed aseprite metadata errors | H-04 | 7 decoders wrap malformed User Data JSON into typed `AsepriteUserDataError`; tamper probes added per module |
| Shared strict PNG chunk reader | H-05, L-15 | `png_chunk_reader.read_png_chunks` replaces all 8 private `_read_png_chunks` copies; trailing-bytes and non-ASCII chunk-type defects fixed |
| Bounded zlib inflation | M-01 | `bounded_decompress` at 19 decode-path sites; text chunks capped at 1 MiB; lab-internal self-compressed helpers deliberately exempt |
| `.pxo` zip-member caps | M-02 | typed `pxo_member_missing` / `*_member_too_large` (8 MiB cap) in all three project modules |
| Profile-set metric fix | M-03 | `_profile_weight_effects_observed` computes over the actual profile set; default-run values byte-identical |
| Exception narrowing | M-04 | APNG import boundary traps only its typed error families; programming bugs no longer masquerade as rejections |
| Symmetry budget honesty | L-07 | `symmetry_break_budget` is `null` (no candidate enumeration exists to count) |

Reports:
`research/experiment_reports/2026-07-04-workshop-editor-decoder-hardening.md`,
`research/experiment_reports/2026-07-04-workshop-editor-boundary-hardening.md`.

workshop_editor tests went 249 → 259 → 267 across the two passes. The
decoder-hardening report's stated limitation — tests exercise tampered
self-output, not foreign files (L-06) — is addressed by cluster 4 below.

### 2. Grid Validator Schema Alignment (1 report)

| Fix | Findings | Evidence Anchor |
| --- | --- | ---: |
| Full schema surface enforced | M-07 | `validate_grid` now enforces schema_version const, grid_id pattern, grid_size 8..64, cell role/material enums, organ role enum, and the palette block |
| Body-core constant documented | M-08 | `BODY_CORE_MIN_CELLS = 4` named and stated in hard invariant 5 as a lab invariant layered on the schema |
| Negative-test remainder | L-01 | body-core, unknown-enum, undersized-grid, and pattern-violation negative tests added |
| Connectivity closed as designed | L-02 | 8-neighbor choice already documented in hard invariant 6; no change |
| Determinism honesty | L-03 | `episode_deterministic: true` reported beside the interface-parity-only `rng_seed` |
| Generator coupling removed | L-05 | `slip.py` carries the authoritative literal palette set, pinned by the cross-validator agreement test |

Report:
`research/experiment_reports/2026-07-04-grid-validator-schema-alignment.md`.

Corpus behavior was unchanged under the stricter validator (50/50 seed grids
valid, 200/200 invalid grids rejected); grid_genome tests went 48 → 53. The
alignment also exposed a real regression in-flight: the newly enforced 64-char
`grid_id` pattern broke compounding offspring ids in
`slip_offspring_lineage_gate.py` at generation 2+, erroring all four
multigeneration-runner tests. The fix (deterministic truncated-prefix +
sha256-suffix compression, ancestry preserved in `lineage.ancestor_ids`,
pinned by a five-generation schema-conformance test) landed in the
boundary-hardening batch. The episode is a useful caution: the
schema-alignment report's "all consuming lab suites green" claim missed the
workshop_editor suite that was in flight.

### 3. Small Labs Gate Integrity (1 report)

| Fix | Findings | Evidence Anchor |
| --- | --- | ---: |
| Evidence-driven boundary probes | M-09 | lab-import probes now derive from real `packages/**` inspection with evidence dicts; a synthetic-violation test proves they can fail |
| Empty-source guard | M-10 | calibration gate no longer crashes on zero-sample source groups |
| Per-record ingest isolation | M-11 | malformed snapshot records land in `rejected_records` with error families; valid records survive |
| Like-for-like confidence baseline | M-12 | baseline recomputed with the deliberative formula; measured effect none (`mean_confidence_gain` 0.018632 unchanged, decision `prototype` unchanged) — the flagged mismatch was latent, and the fix removes the coupling so future divergence cannot silently skew the gain |
| Status-branched decision reason | L-09 | `reject_direct_mapping` no longer carries a success narrative |
| Evidence-aware promotion blockers | L-10 | blockers with artifact evidence carry `cleared_when` checks; evidence-less blockers marked `static: true`; current outcomes identical |
| `survival_ticks` semantics pinned | L-11 | documented and death-tick-tested; arithmetic deliberately unchanged |
| Single grid compilation | L-13 | output byte-identical |

Report:
`research/experiment_reports/2026-07-04-small-labs-gate-integrity.md`.

Test counts: architecture 4→6, readability_benchmark 15→16, cubff_transducer
8→13, package_promotion 4→5, lifecycle_sim 5→6, ctm_ticks 4→4. The M-12
negative result is deliberately recorded: gate claims now derive from
inspected evidence rather than constants, and the honest finding is that the
review's "two scales" concern was not numerically active in current code.

### 4. Foreign-Fixture Conformance Corpus (1 report)

| Proof | Evidence Anchor |
| --- | ---: |
| Independent spec-derived writer | `foreign_fixture_writer.py` shares no code with the lab encoders: own chunk writer/CRC, filters 0-4, Adam7 extraction, acTL/fcTL/fdAT serialization, exact-arithmetic playback reference model |
| 17-fixture committed corpus | multi-IDAT (even/ragged/zero-length), per-row filters 0-4, interleaved ancillary chunks, independent Adam7, split fdAT, non-animated default images, dispose background/previous, blend over, sub-canvas regions |
| 29 conformance tests | every fixture x decoder outcome is a pixel-exact decode or a documented typed rejection; no raw exceptions |
| Wrong-pixels bug found and fixed | `png_apng_filtered_frame_data.py` accepted dispose 1/2 and blend 1 while silently ignoring them — now typed `apng_dispose_op_unsupported` / `apng_blend_op_unsupported` rejections matching the module's documented scope |
| Determinism | double-generation byte-compare pinned by test; committed corpus byte-matches regeneration |

Report:
`research/experiment_reports/2026-07-04-foreign-fixture-conformance.md`.

This closes L-06 for the features the corpus covers and closes the
self-referential-fixture limitation recorded by the decoder-hardening report.
The manifest's `known_deficiencies` list is empty — no wrong-pixel behavior
remains — and is the designated honest place for any future wrong-pixel
finding. The remaining honest gap: no grayscale/deep-color foreign fixtures
(the decoders under test claim 8-bit RGBA scope). workshop_editor tests went
267 → 296.

### 5. Structural Debt Retirement (2 reports + ledger backfill)

| Fix | Findings | Evidence Anchor |
| --- | --- | ---: |
| grid_genome helper dedup | L-04 | `grid_helpers.py` single-sources cell construction, matrix-to-grid conversion (real divergences parameterized, strict-token behavior pinned), baseline reporting (key-order exact), signatures, and weighted sampling; 9 pinning tests; corpora verified byte-equivalent against a pristine-HEAD worktree run |
| Repo-root path anchoring | L-08 | 143 lab files anchored on `ROOT = Path(__file__).resolve().parents[2]`; artifact path strings recorded repo-relative; full sweep verified from two cwds; artifacts byte-stable |
| Research ledger backfill | L-14 | 11 baseline triads backfilled; 3 orphan cards referenced (recorded in the code-review TODO table; no dedicated experiment report) |

Reports:
`research/experiment_reports/2026-07-04-grid-genome-helper-dedup.md`,
`research/experiment_reports/2026-07-04-repo-root-path-anchoring.md`.

The dedup report's rationale is the review's own causal chain: drift between
copies of shared logic is the failure class that produced H-02. Deliberate
divergences stay local with a naming comment (`_add_body_cell`'s intentional
weight difference); the constrained-corpus regeneration was a catch-up to
HEAD code discovered during verification, not an effect of the refactor.
grid_genome tests went 53 → 62; the full 455-test sweep is green from the
repo root and from a foreign cwd. Pre-existing residuals recorded by the
anchoring report: three hand-extended `data/*/README.md` files diverge from
their generators, and tracked `__pycache__/*.pyc` files dirty non-`-B` runs.

## Decisions

### Adopt

- `png_chunk_reader` as the single chunk-read/inflate path for workshop labs:
  new decoders must not copy a private `_read_png_chunks` or call unbounded
  `zlib.decompress` on external data.
- Uniformly typed import boundaries: missing/oversized zip members, malformed
  metadata JSON, malformed chunk streams, and oversized zlib payloads all
  reject with family-tagged errors; no import path catches blind `Exception`.
- `validate_grid` as the executable form of hard invariant 1 for the surfaces
  the schema can express, plus the two documented lab invariants; schema enum
  or range changes must be mirrored in the validator constants.
- Evidence-driven gate claims: negative probes derive from inspected repo
  state with evidence dicts, ingest reports partial typed results, and
  promotion blockers clear against the metric artifacts the gate reads.
- Foreign fixtures as the conformance mechanism: new decoder claims add
  fixtures to `data/foreign_fixtures/` rather than relying on encoder
  round-trips; `known_deficiencies` is the honest place for unfixable
  wrong-pixel findings.
- `grid_helpers.py` as the single source for grid_genome helpers; incidental
  divergences go through parameters, deliberate ones stay local with a
  comment naming the difference.
- The ROOT-anchoring two-liner for all new lab code, with artifact path
  strings recorded repo-relative (recorded in CLAUDE.md).

### Watch

- The dependency-manifest decision (M-15 remainder): deliberately open;
  authoring a manifest flips `dependency_manifest_present` and triggers the
  migration-gate revisit.
- Degenerate `lifecycle_survival` and `mutation_stability` descriptor axes
  (L-12): now visible via `descriptor_bin_spread` (spread 1); the calibration
  fix (harder lifecycle probe or mutation-varying generation) is still open.
- Foreign-fixture coverage gap: no grayscale/deep-color fixtures yet.
- `third_party_project_decoder` zip-timestamp nondeterminism (wall-clock
  timestamps vs the siblings' stable-timestamp pattern) — noted as future
  alignment work.
- Pre-existing residuals: three hand-extended `data/*/README.md` files
  diverge from their generators; tracked `__pycache__/*.pyc` files dirty
  non-`-B` test runs.

### Blocked

- Profile-weighted evolution, manual readability calibration (still 0 of 63
  reviewer rows), package runtime lifecycle integration, and package
  promotion — unchanged from v0.6.
- Live external editor rewrite validation and editor-authored fixtures; the
  foreign-fixture corpus is independent of the lab encoders but still
  lab-generated, not editor-produced.
- Full APNG/PNG conformance and the final PNG production carrier selection.
- Arbitrary Aseprite project schema coverage, full project-format coverage,
  and community profile packs.

## Implementation Boundary

This report does not authorize implementation by itself. The first allowed
implementation step remains the empty `packages/mecha_engine` `src`-layout
scaffold defined by the v0.4/v0.5 reports and the scaffold verification gate,
and it may be taken only when the user explicitly starts package work. The
hardened runtime boundary gate now proves its lab-import probes against real
repo state; it still defines contracts only and does not create the scaffold.

## Next Research Sequence

1. Make the dependency manifest decision (M-15 remainder) explicit, then
   rerun the schema-migration and pydantic contract gates.
2. Extend the foreign-fixture corpus to grayscale and deep-color features, or
   record the scope boundary explicitly in the decoders under test.
3. Address the L-12 descriptor degeneracy with a harder lifecycle probe or
   mutation-varying candidate generation.
4. Collect 63 real SLIP readability reviewer rows and rerun the calibration
   gate before changing proxy thresholds or claiming profile-weighted
   evolution.
5. Collect live external editor open-save fixtures (Piskel, Pixelorama,
   Aseprite/LibreSprite) before removing editor-preservation blockers, and
   decide the production metadata carrier only after they exist.
6. Keep package scaffold creation blocked until explicitly authorized.

## Publication Status

This is an internal research publication. It consolidates the post-v0.6
remediation evidence and records that the repository is still research-only:
the 2026-07-04 code-review remediation is complete except the deliberately
open dependency-manifest decision, the full sweep is 455 tests green, and all
package, calibration, live-editor, and evolution claims remain blocked.

## External References

- W3C PNG specification, Third Edition: https://www.w3.org/TR/png-3/
- RFC 1950, ZLIB Compressed Data Format: https://www.rfc-editor.org/rfc/rfc1950
- RFC 1951, DEFLATE Compressed Data Format: https://www.rfc-editor.org/rfc/rfc1951
- Aseprite file-format specification:
  https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md
- Illuminating search spaces by mapping elites: https://arxiv.org/abs/1504.04909
