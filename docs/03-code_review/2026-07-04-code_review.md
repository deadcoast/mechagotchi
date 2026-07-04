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
| H-01 | H | slip_validator | `test_pydantic_contract.py:49`, `test_schema_migration_gate.py:24` | Tests assert `jsonschema_available == False`; jsonschema 4.26.0 in user site → 2 failures in every env | Assert report *shape*, not env snapshot; reconcile `data/slips/*_stage0.json` + compatibility-matrix wording in same commit |
| H-02 | H | grid_genome | `slip.py:47-53` | `validate_slip` never checks required/extra keys in `behavior`/`survival_weights` — accepts profiles `slip_validator.py` + schema reject; gates seed selection via `constrained_generator._filter_seed_pool` | Enforce exact key sets; add cross-validator agreement test over `data/slips/failure_cases/` |
| H-03 | H | map_elites | `extended_descriptors.py:326-333, 150, 347-351` | `behavior_neediness` constant when SLIP supplied (always bin 1) → "7 descriptors" inflated; coverage divides by 5^7 though ≤5^6 reachable → understated ~5× | Fix descriptor or drop axis; fix denominator; regenerate `map_elites_extended_stage0.json` + update claims |
| H-04 | H | workshop_editor | `aseprite_{tags_layers:161, tilemap_tileset:224, palette_slice:203, linked_cel:217, nested_timeline:177, external_properties:197, document_variant_resolution:262}` | Unguarded `json.loads` after prefix check — malformed user-data chunk crashes `import_*` with untyped `JSONDecodeError` | Wrap in typed `AsepriteUserDataError`; add malformed-JSON negative probes |
| H-05 | H | workshop_editor | `png_embedded_sidecar_writer.py:388,398` vs `standard_image_sidecar_decoder.py:380`, `png_adam7_interlace_decoder.py:589`, `png_deep_color_sidecar_decoder.py:767` | `_read_png_chunks` ×5 divergent variants; embedded-writer variant accepts post-IEND bytes + raw `UnicodeDecodeError`; APNG sidecar decoder imports that one | Factor one shared typed, trailing-byte-strict chunk reader; migrate all decoders |
| H-06 | H | research docs | `research/reports/` (newest: v0_5, 2026-05-12) | 43 experiment reports postdate the v0_5 manifest — PNG/APNG/Aseprite/spritesheet wave unconsolidated | Cut `research_report_v0_6.md` + manifest |
| M-01 | M | workshop_editor | `standard_image_sidecar_decoder.py:114`, `png_adam7_interlace_decoder.py:84`, `png_deep_color_sidecar_decoder.py:198`, `png_apng_sidecar_decoder.py:562`, `aseprite_user_data_chunk_writer.py:740`, `aseprite_tilemap_tileset_semantics.py:866+`, `png_textual_metadata_policy.py:556,634` | Every `zlib.decompress` unbounded — size check after full inflate (decompression-bomb surface) | `max_length` via `zlib.decompressobj`, typed error on overflow |
| M-02 | M | workshop_editor | `third_party_project_decoder.py:331,344`; `project_native_metadata_writer.py:653`; `project_editor_rewrite_preservation.py:406` | `.pxo` zip members read without decompressed-size cap; dangling cel path → raw `KeyError` (handler catches only `BadZipFile`) | Check `ZipInfo.file_size` cap; `KeyError` → `ProjectDecodeError` |
| M-03 | M | workshop_editor | `slip_preview_gates.py:426-431` (CLI `:529`) | `_profile_weight_effects_observed` hard-indexes 3 default profile ids — custom `--profile` crashes with `KeyError` | Iterate actual `by_profile` keys |
| M-04 | M | workshop_editor | `png_apng_sidecar_decoder.py:247-250` | `except Exception` reports all errors as `apng_decode_failed` — bugs masquerade as malformed-input rejections | Catch typed errors only |
| M-05 | M | grid_genome | `slip.py:34, 24-30, 39-45` | Bool accepted as int for body-mass bounds; `profile_id` pattern unenforced; `uniqueItems` unenforced for palettes/roles | Port checks from `slip_validator.py` |
| M-06 | M | grid_genome | `slip.py:104-107` | `is_grid_aligned` compares `value > limit` on unvalidated grid data — non-numeric raises `TypeError`; bool silently compares | Validate grid mutation block first |
| M-07 | M | grid_genome | `validator.py:129-139` + gaps | Schema invariants unenforced: grid_size 8–64 range, `cell.role`/`cell.material` enums, palette block, `schema_version` const, `grid_id` pattern | Add checks or document scope split in `grid_invariants.md` |
| M-08 | M | grid_genome | `validator.py:104-105` | Body-core ≥ 4 cells is a magic number absent from schema and untested | Record in schema/invariants doc; add negative test |
| M-09 | M | architecture | `mecha_engine_runtime_boundary_gate.py:364-381`; test `:55-57` | 2 of 5 "negative probes" are hardcoded `accepted=False` constants — probe count + closed-state trivially true | Implement real inspection or relabel `not_yet_probed` |
| M-10 | M | readability | `slip_readability_calibration_gate.py:224-229` | Unconditional `by_source[...]["count"]` — empty source group → `KeyError` crash | `.get(key, {}).get("count", 0)` |
| M-11 | M | cubff | `real_snapshot_ingest.py:41-53, 54-72` | One malformed record/line rejects entire snapshot file; valid records lost | Per-record try/except; report `rejected_records` |
| M-12 | M | ctm_ticks | `ctm_inspired_ticks.py:75-78, 169-181, 305-310` | `confidence_gain` subtracts across two different confidence formulas; decision keyed on it may be formula artifact | Recompute baseline with same formula |
| M-13 | M | research docs | `research/README.md` ledger end | Two complete 05-14 triads invisible to ledger and manifests: `png_adam7_deep_color_cross_product`, `png_deep_color_sidecar_decoder` | Add ledger entries; include in v0_6 |
| M-14 | M | research docs | `research/decision_records/0001-...md` Sources | Broken path `docs/01-notes/01-shelved/...` → actual `docs/01-shelved/...` | Fix path |
| M-15 | M | infra | no `pyproject.toml`/`requirements*.txt`; `.venv` unused | Dependency deferral leaking: user site-packages flip gate outcomes (caused H-01); `python` = system 3.14 | Author dependency manifest, or make gates env-robust and pin intended interpreter in docs |
| L-01 | L | grid_genome tests | `test_slip_constraints.py`; `validator.py:105` | `is_grid_aligned` rejection branches never asserted False; body-core minimum never exercised | Add negative tests |
| L-02 | L | grid_genome | `validator.py:161-181` | Connectivity BFS 8-directional while cores authored 4-connected — diagonal-only cores pass | Decide + document in `grid_invariants.md` |
| L-03 | L | grid_genome | `switchboard_feedback.py:36,99` | `rng_seed` drives nothing yet echoed into report — misleading reproducibility field | Remove or wire |
| L-04 | L | grid_genome | `_cell`/`_grid_from_matrix` ×3, `run_baseline` ×3, `_signature` ×2; SLIP validation ×3 places | Duplicated helpers, drift risk (H-02/M-05 are the realized cost) | Factor shared helpers |
| L-05 | L | grid_genome | `slip.py:3` | Palette validation imports `PALETTES` from `corpus_builder` instead of schema enum | Source from `slip.schema.json` |
| L-06 | L | workshop_editor tests | e.g. `test_standard_image_sidecar_decoder.py:50-58` | All tests self-referential round-trips; no foreign PNG/APNG/.aseprite fixtures; multi-IDAT, real dispose/blend, mixed filters never exercised | Foreign-fixture corpus + conformance tests |
| L-07 | L | workshop_editor | `slip_preview_gates.py:173, 187-188` | `symmetry_break_budget` set equal to its own cap → `caps_respected` trivially true | Compute real count or drop field |
| L-08 | L | repo-wide | e.g. `external_metadata_sidecar.py:22-23`, `test_slip_readability_calibration_gate.py:21` | Imports anchored on `ROOT` but data paths cwd-relative; tests pass only from repo root | Anchor default paths on `ROOT` |
| L-09 | L | cubff | `cubff_transducer.py:379-395` | `reason` text claims success even when `status="reject_direct_mapping"` | Branch reason on status |
| L-10 | L | package_promotion | `package_promotion_gate.py:103,162,184` | `research_blockers` hardcoded in registry — would override artifact evidence | Derive from metric artifacts |
| L-11 | L | lifecycle_sim | `lifecycle_sim.py:163, 205-215` | `survival_ticks` counts the death tick (+1); feeds `survival_ratio` downstream | Define semantics; adjust or document |
| L-12 | L | map_elites | `extended_descriptors.py:314-323` | `mutation_stability` constant on shipped corpus (all 50 seeds share identical mutation rates) | Note in report; vary in generated candidates |
| L-13 | L | cubff | `cubff_transducer.py:210-219` vs `485-494` | Semantic grids compiled + scored twice | Pass through |
| L-14 | L | research docs | `research/README.md`; 3 cards; 23 modules | 11 v0_1-era reports absent from README flat list (manifest-covered); 3 cards referenced nowhere; 23 modules ledgered under non-matching slugs | Backfill opportunistically |

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
