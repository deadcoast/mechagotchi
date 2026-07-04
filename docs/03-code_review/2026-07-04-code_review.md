# Code Review — 2026-07-04

Full-source review of `labs/`, `research/`, `data/`, and the documentation traceability system. Findings carry stable IDs (`H-*`/`M-*`/`L-*`) for reference in commits and follow-up documents. Severity: **H** = correctness/validity broken now, **M** = real defect on a reachable path, **L** = debt/hardening.

Baseline: commit `66800f0`, Python 3.14.3 (system, user site-packages visible), run from repo root.

## Test ground truth

| Lab | Tests | Result |
|---|---|---|
| workshop_editor | 249 | OK |
| grid_genome | 42 | OK |
| readability_benchmark | 15 | OK |
| slip_validator | 15 | **FAILED (2)** |
| cellular_automata | 14 | OK |
| asset_pipeline | 11 | OK |
| cubff_transducer | 8 | OK |
| lifecycle_sim | 5 | OK |
| map_elites_archive | 5 | OK |
| architecture / ctm_ticks / package_promotion | 4 each | OK |
| **Total** | **376** | **374 pass / 2 fail** |

The 2 failures are environment-coupled assertions, not pydantic drift: `labs/slip_validator/test_pydantic_contract.py:49` and `labs/slip_validator/test_schema_migration_gate.py:24` assert `jsonschema_available == False`, but `jsonschema 4.26.0` is installed in user site-packages and visible to every interpreter. All 12 SLIP failure-corpus cases are correctly rejected under pydantic 2.12.5.

## Verdict by area

**Documentation/traceability — excellent, one structural debt.** 251/252 ledger paths, 89/89 manifest artifact refs, 149/150 `## Sources` refs resolve; zero orphan lab modules or data artifacts; schemas verified in sync with emitters. Debt: the consolidated-report layer stopped at v0_5 (2026-05-12) while 43 experiment reports have landed since (H-06).

**grid_genome — solid core, drifted SLIP validators.** `labs/grid_genome/slip.py` (gates seed selection) accepts profiles the authoritative `labs/slip_validator/slip_validator.py` and `research/slip/slip.schema.json` reject (H-02, M-05, M-06). `labs/grid_genome/validator.py` enforces less than `grid_genome.schema.json` promises and more (body-core ≥ 4) than the schema records (M-07, M-08).

**workshop_editor — disciplined design, systemic copy-paste decay.** Sidecar/hash-binding architecture sound; report `blocked_states`/`closed_states` honestly match the code. But shared binary-format helpers are reimplemented per module with divergences exactly where robustness breaks: 5 `_read_png_chunks` variants (H-05), 6 aseprite decoders with unguarded `json.loads` (H-04), no size-capped `zlib.decompress` anywhere (M-01). 249 tests are almost entirely self-referential round-trips (L-06).

**Small labs — mostly healthy, two metric-validity problems.** MAP-Elites extended archive's "3 → 7 descriptors" claim is inflated: `behavior_neediness` is constant when a SLIP is supplied and coverage divides by the full 5^7 denominator (H-03); `mutation_stability` is also constant on the shipped corpus (L-12). The runtime-boundary gate counts two hardcoded constants among its "negative probes" (M-09). Verified-correct: readability weights, QD-score, Spearman math, division-by-zero guards, and `package_promotion_gate` artifact evaluation.

**Infrastructure — the deferred-dependency policy is leaking.** No dependency manifest by design (`schema_migration_gate.py:36`), but user site-packages now flip gate outcomes (M-15 caused H-01). `.venv` (3.13, empty) is unused; `python` resolves to system 3.14.

## TODO — flagged issues

| ID | Sev | Area | Location | Issue | Fix direction |
|----|-----|------|----------|-------|---------------|
| H-01 | H | slip_validator | `test_pydantic_contract.py:49`, `test_schema_migration_gate.py:24` | **RESOLVED (Batch 1)** — tests now assert the dependency policy and record availability as an observation; `_module_version` moved to `importlib.metadata`; research/slip docs re-anchored to manifest absence. See `research/experiment_reports/2026-07-04-slip-dependency-gate-env-decoupling.md` | Assert report *shape*, not env snapshot; reconcile `data/slips/*_stage0.json` + compatibility-matrix wording in same commit |
| H-02 | H | grid_genome | `slip.py:47-53` | **RESOLVED (Batch 2)** — exact key-set enforcement for all sections; cross-validator agreement test pinned over the full corpus. See `research/experiment_reports/2026-07-04-slip-lab-validator-alignment.md` | Enforce exact key sets; add cross-validator agreement test over `data/slips/failure_cases/` |
| H-03 | H | map_elites | `extended_descriptors.py:326-333, 150, 347-351` | **RESOLVED (Batch 4)** — axis is grid-derived with SLIP prior as shift; per-axis `descriptor_bin_spread` added to the artifact; regenerated (niches 29→33, qd 27.77→31.62). See `research/experiment_reports/2026-07-04-map-elites-neediness-descriptor-fix.md` | Fix descriptor or drop axis; fix denominator; regenerate `map_elites_extended_stage0.json` + update claims |
| H-04 | H | workshop_editor | `aseprite_{tags_layers:161, tilemap_tileset:224, palette_slice:203, linked_cel:217, nested_timeline:177, external_properties:197, document_variant_resolution:262}` | **RESOLVED (Batch 3)** — all seven sites wrap into typed `AsepriteUserDataError` with the module's `*_json_invalid` family; tamper probes + unit tests added; artifacts regenerated. See `research/experiment_reports/2026-07-04-workshop-editor-decoder-hardening.md` | Wrap in typed `AsepriteUserDataError`; add malformed-JSON negative probes |
| H-05 | H | workshop_editor | `png_embedded_sidecar_writer.py:388,398` vs `standard_image_sidecar_decoder.py:380`, `png_adam7_interlace_decoder.py:589`, `png_deep_color_sidecar_decoder.py:767` | **RESOLVED (Batch 3)** — shared `png_chunk_reader.read_png_chunks` (strict: signature/CRC/truncation/ASCII-type/trailing-bytes); all five variants migrated as thin wrappers preserving local error families; negative tests added. Follow-up: L-15 | Factor one shared typed, trailing-byte-strict chunk reader; migrate all decoders |
| H-06 | H | research docs | `research/reports/` (newest: v0_5, 2026-05-12) | **RESOLVED (Batch 5)** — `mechagotchi_research_report_v0_6.md` + manifest published, consolidating 46 post-v0_5 reports (96/96 referenced artifacts verified); registered in reports README | Cut `research_report_v0_6.md` + manifest |
| M-01 | M | workshop_editor | `standard_image_sidecar_decoder.py:114`, `png_adam7_interlace_decoder.py:84`, `png_deep_color_sidecar_decoder.py:198`, `png_apng_sidecar_decoder.py:562`, `aseprite_user_data_chunk_writer.py:740`, `aseprite_tilemap_tileset_semantics.py:866+`, `png_textual_metadata_policy.py:556,634` | **RESOLVED (Batch 3)** — `png_chunk_reader.bounded_decompress` (expected-size cap, typed overflow/truncation errors, positive-size guard) at 19 decode-path sites incl. 9 found beyond the listed set; text chunks capped at 1 MiB; lab-internal self-compressed helpers deliberately exempt | `max_length` via `zlib.decompressobj`, typed error on overflow |
| M-02 | M | workshop_editor | `third_party_project_decoder.py:331,344`; `project_native_metadata_writer.py:653`; `project_editor_rewrite_preservation.py:406` | **RESOLVED (Batch 6)** — `_read_pxo_member` with typed `pxo_member_missing` / `*_member_too_large` (8 MiB cap) in all three modules; negative tests added. See `research/experiment_reports/2026-07-04-workshop-editor-boundary-hardening.md` | Check `ZipInfo.file_size` cap; `KeyError` → `ProjectDecodeError` |
| M-03 | M | workshop_editor | `slip_preview_gates.py:426-431` (CLI `:529`) | **RESOLVED (Batch 6)** — metric computes over actual profile set; `insufficient_profiles` for <2 profiles; default-run values byte-identical | Iterate actual `by_profile` keys |
| M-04 | M | workshop_editor | `png_apng_sidecar_decoder.py:247-250` | **RESOLVED (Batch 6)** — boundary catches only `(APNGDecodeError, PNGEmbeddedSidecarError, PNGChunkError)`; all probes reject with identical families | Catch typed errors only |
| M-05 | M | grid_genome | `slip.py:34, 24-30, 39-45` | **RESOLVED (Batch 2)** — bool rejection, `profile_id` pattern, and duplicate-item checks ported from `slip_validator.py` | Port checks from `slip_validator.py` |
| M-06 | M | grid_genome | `slip.py:104-107` | **RESOLVED (Batch 2)** — `is_grid_aligned` now type-checks grid mutation values and reports typed errors instead of crashing | Validate grid mutation block first |
| M-07 | M | grid_genome | `validator.py:129-139` + gaps | **RESOLVED (Batch 7)** — validator now enforces schema_version, grid_id pattern, grid_size 8–64, cell role/material enums, organ role enum, and the palette block; corpora unchanged (50/50 valid, 200/200 rejected). See `research/experiment_reports/2026-07-04-grid-validator-schema-alignment.md` | Add checks or document scope split in `grid_invariants.md` |
| M-08 | M | grid_genome | `validator.py:104-105` | **RESOLVED (Batch 7)** — named `BODY_CORE_MIN_CELLS = 4`, threshold stated in hard invariant 5, negative test added | Record in schema/invariants doc; add negative test |
| M-09 | M | architecture | `mecha_engine_runtime_boundary_gate.py:364-381`; test `:55-57` | **RESOLVED (Batch 8)** — probes derive from real `packages/**` inspection with evidence dicts; synthetic-violation test proves they can fail. See `research/experiment_reports/2026-07-04-small-labs-gate-integrity.md` | Implement real inspection or relabel `not_yet_probed` |
| M-10 | M | readability | `slip_readability_calibration_gate.py:224-229` | **RESOLVED (Batch 8)** — `.get(..., 0)` with empty-source unit test | `.get(key, {}).get("count", 0)` |
| M-11 | M | cubff | `real_snapshot_ingest.py:41-53, 54-72` | **RESOLVED (Batch 8)** — per-record isolation with `rejected_records` (index/line + family); file-level rejection only for container errors or zero valid records | Per-record try/except; report `rejected_records` |
| M-12 | M | ctm_ticks | `ctm_inspired_ticks.py:75-78, 169-181, 305-310` | **RESOLVED (Batch 8)** — baseline recomputed with the same formula; measured effect none (gain 0.018632 unchanged, decision `prototype` unchanged) — mismatch was latent, coupling removed | Recompute baseline with same formula |
| M-13 | M | research docs | `research/README.md` ledger end | **RESOLVED (Batch 5)** — both deep-color triads added to the ledger and included in the v0_6 manifest | Add ledger entries; include in v0_6 |
| M-14 | M | research docs | `research/decision_records/0001-...md` Sources | **RESOLVED (Batch 5)** — path fixed to `docs/01-shelved/03-reports/03-deep_research_report.md` | Fix path |
| M-15 | M | infra | no `pyproject.toml`/`requirements*.txt`; `.venv` unused | **PARTIALLY RESOLVED (Batch 1)** — gates made env-robust; interpreter reality documented in CLAUDE.md. Open remainder: the dependency-manifest decision itself (deliberately left to the maintainer — a manifest flips `dependency_manifest_present` and triggers the migration gate's revisit) | Author dependency manifest, or make gates env-robust and pin intended interpreter in docs |
| L-01 | L | grid_genome tests | `test_slip_constraints.py`; `validator.py:105` | **RESOLVED (Batches 2+7)** — all four `is_grid_aligned` rejection branches tested (Batch 2); body-core-below-minimum negative test added (Batch 7) | Add negative tests |
| L-02 | L | grid_genome | `validator.py:161-181` | **CLOSED, NO CHANGE (Batch 7)** — 8-neighbor connectivity was already documented as deliberate in `grid_invariants.md` hard invariant 6; consistent by design | Decide + document in `grid_invariants.md` |
| L-03 | L | grid_genome | `switchboard_feedback.py:36,99` | **RESOLVED (Batch 7)** — report records `episode_deterministic: true`; `rng_seed` documented as interface-parity-only | Remove or wire |
| L-04 | L | grid_genome | `_cell`/`_grid_from_matrix` ×3, `run_baseline` ×3, `_signature` ×2; SLIP validation ×3 places | **RESOLVED (Batch 10)** — `grid_helpers.py` single-sources `_cell`, grid-from-matrix (divergences parameterized; strict-token behavior pinned), `run_baseline` (key-order exact), `grid_signature`, `weighted_sample`; 9 pinning tests; corpora byte-identical. See `research/experiment_reports/2026-07-04-grid-genome-helper-dedup.md` | Factor shared helpers |
| L-05 | L | grid_genome | `slip.py:3` | **RESOLVED (Batch 7)** — `slip.py` carries the same literal palette set as the authoritative validator (pinned by the Batch 2 agreement test); generator coupling removed | Source from `slip.schema.json` |
| L-06 | L | workshop_editor tests | e.g. `test_standard_image_sidecar_decoder.py:50-58` | **RESOLVED (Batch 9)** — independent spec-derived fixture writer + 17-fixture corpus (`data/foreign_fixtures/`) + 29 conformance tests; found and fixed a wrong-pixels bug (dispose/blend accepted but ignored, `png_apng_filtered_frame_data.py:392`). Open remainder: grayscale/deep-color foreign fixtures. See `research/experiment_reports/2026-07-04-foreign-fixture-conformance.md` | Foreign-fixture corpus + conformance tests |
| L-07 | L | workshop_editor | `slip_preview_gates.py:173, 187-188` | **RESOLVED (Batch 6)** — field is now `null` with rationale (no symmetry-break candidate enumeration exists to count); cap conjunct retained | Compute real count or drop field |
| L-08 | L | repo-wide | e.g. `external_metadata_sidecar.py:22-23`, `test_slip_readability_calibration_gate.py:21` | **RESOLVED (Batch 12)** — 143 lab files anchored on `ROOT`; artifact path strings recorded repo-relative; suites verified from two cwds; artifacts byte-stable. See `research/experiment_reports/2026-07-04-repo-root-path-anchoring.md` | Anchor default paths on `ROOT` |
| L-09 | L | cubff | `cubff_transducer.py:379-395` | **RESOLVED (Batch 8)** — reason branches on status | Branch reason on status |
| L-10 | L | package_promotion | `package_promotion_gate.py:103,162,184` | **RESOLVED (Batch 8)** — blockers evidence-aware via `cleared_when` checks; evidence-less blockers marked `static: true`; current outcomes identical | Derive from metric artifacts |
| L-11 | L | lifecycle_sim | `lifecycle_sim.py:163, 205-215` | **RESOLVED (Batch 8)** — semantics documented and pinned by a death-tick test; arithmetic deliberately unchanged (downstream artifacts depend on it) | Define semantics; adjust or document |
| L-12 | L | map_elites | `extended_descriptors.py:314-323` | `mutation_stability` constant on shipped corpus (all 50 seeds share identical mutation rates). **Now visible**: Batch 4's `descriptor_bin_spread` reports it (spread 1, along with `lifecycle_survival`); calibration fix still open | Note in report; vary in generated candidates |
| L-13 | L | cubff | `cubff_transducer.py:210-219` vs `485-494` | **RESOLVED (Batch 8)** — compiled once via precompiled-grids parameter; output byte-identical | Pass through |
| L-14 | L | research docs | `research/README.md`; 3 cards; 23 modules | **RESOLVED (Batch 11)** — 11 baseline triads backfilled into the ledger with cards and data artifacts; the 3 orphan cards (`cubff_transducer`, `lineage_tracking`, `markov_grid`) now referenced; slug-drift note added for future triads | Backfill opportunistically |
| L-15 | L | workshop_editor | `png_apng_color_type_frame_data.py:724`, `png_apng_filtered_frame_data.py:675`, `png_apng_partial_frame_playback.py:628` | **RESOLVED (Batch 6)** — all three migrated to `png_chunk_reader.read_png_chunks` with strict behavior; trailing-bytes negative tests added | Migrate to `png_chunk_reader.read_png_chunks` |

## Attack order

1. **Batch 1** — H-01 + M-15 (unblocks the suite, settles the dependency question)
2. **Batch 2** — H-02 + M-05 + M-06 (one SLIP-validator-alignment change)
3. **Batch 3** — H-04 + H-05 + M-01 (one workshop_editor hardening pass)
4. **Batch 4** — H-03 (metrics-integrity fix + artifact regeneration)
5. **Batch 5** — H-06 + M-13 + M-14 (one documentation-ledger commit)

Remaining M/L items are tracked here and may be batched opportunistically. Per repo convention, each batch updates its triad documents in the same change. This file is living: update finding rows with `RESOLVED (<commit>)` annotations as batches land.

## Sources

- `labs/` (all twelve lab directories, read in full or representative depth)
- `research/README.md`
- `research/slip/slip.schema.json`
- `research/grid_genome/grid_genome.schema.json`
- `research/reports/research_report_v0_5_manifest.json`
- `data/slips/slip_pydantic_contract_stage0.json`
- `data/slips/slip_schema_migration_dependency_gate_stage0.json`
- `docs/02-research_plan.md`
