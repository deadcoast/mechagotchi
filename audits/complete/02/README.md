# Fable 5 Review

> Everything Below is claimed by Fable 5

All four reviews plus test ground truth are in. Here's the full picture.

---
(a) State of the Source Code — Review

Test ground truth (run 2026-07-04, Python 3.14.3 from repo root)

┌────────────────────────────────────────────┬────────┬───────────────────┐
│                    Lab                     │ Tests  │      Result       │
├────────────────────────────────────────────┼────────┼───────────────────┤
│ workshop_editor                            │ 249    │ OK                │
├────────────────────────────────────────────┼────────┼───────────────────┤
│ grid_genome                                │ 42     │ OK                │
├────────────────────────────────────────────┼────────┼───────────────────┤
│ readability_benchmark                      │ 15     │ OK                │
├────────────────────────────────────────────┼────────┼───────────────────┤
│ slip_validator                             │ 15     │ FAILED (2)        │
├────────────────────────────────────────────┼────────┼───────────────────┤
│ cellular_automata                          │ 14     │ OK                │
├────────────────────────────────────────────┼────────┼───────────────────┤
│ asset_pipeline                             │ 11     │ OK                │
├────────────────────────────────────────────┼────────┼───────────────────┤
│ cubff_transducer                           │ 8      │ OK                │
├────────────────────────────────────────────┼────────┼───────────────────┤
│ lifecycle_sim                              │ 5      │ OK                │
├────────────────────────────────────────────┼────────┼───────────────────┤
│ map_elites_archive                         │ 5      │ OK                │
├────────────────────────────────────────────┼────────┼───────────────────┤
│ architecture, ctm_ticks, package_promotion │ 4 each │ OK                │
├────────────────────────────────────────────┼────────┼───────────────────┤
│ Total                                      │ 376    │ 374 pass / 2 fail │
└────────────────────────────────────────────┴────────┴───────────────────┘

The 2 failures are not pydantic drift (correcting my earlier session claim — all 12 failure-corpus cases are correctly rejected under pydantic 2.12.5). Both are assertFalse(report["jsonschema_available"]) at labs/slip_validator/test_pydantic_contract.py:49 and labs/slip_validator/test_schema_migration_gate.py:24 — the tests baked "jsonschema is not installed" into the dependency-gate as an environment snapshot; jsonschema 4.26.0 now sits in user site-packages (AppData\Roaming\Python\Python314), visible to every interpreter, so the suite fails everywhere. Uncommitted edits to the two data/slips/*_stage0.json gate artifacts already flipped jsonschema_available: true — the artifacts moved, the tests didn't.

Verdict by area

Documentation/traceability system — excellent, one structural debt. 251/252 ledger paths, 89/89 manifest artifact refs, and 149/150 ## Sources refs resolve; zero orphan lab modules or data artifacts; schemas verified in sync with emitters (schema_version 0.1.0 both sides; pydantic-generated SLIP schema matches the model). The debt: the consolidated-report layer stopped at v0_5 (published 2026-05-12) while 43 experiment reports have landed since — the entire PNG/APNG/Aseprite/spritesheet wave has no v0_6 rollup, and two complete deep-color triads never made it into the README ledger at all.

grid_genome — solid core, but the two SLIP validators have drifted. labs/grid_genome/slip.py (which gates seed selection in constrained_generator) accepts profiles the authoritative labs/slip_validator/slip_validator.py and slip.schema.json reject: extra/missing behavior/survival_weights keys, bool body-mass bounds, duplicate palettes, unpatterned profile_id. Separately, validator.py enforces less than grid_genome.schema.json promises (no role/material enums, no grid_size 8–64 range, no palette validation) while also enforcing more (body-core ≥ 4 cells — a magic number absent from the schema and untested).

workshop_editor — disciplined design, systemic copy-paste decay. The sidecar/hash-binding architecture is sound and the reports' blocked_states/closed_states honestly match what the code proves. But the same binary-format helpers are reimplemented per module with exactly the divergences where robustness breaks:_read_png_chunks exists in ~5 variants (one accepts trailing bytes after IEND and crashes untyped on non-ASCII chunk types — and the APNG sidecar decoder imports that one); six aseprite decoders dropped the try/except around json.loads that their siblings kept, so malformed-but-prefixed user-data chunks crash importers with untyped errors; no zlib.decompress anywhere is size-capped despite the expected output size being known up front. Test coverage is broad (249) but almost entirely self-referential round-trips against the modules' own encoders — real-world format conformance is effectively unverified.

Small labs — mostly healthy, two metric-validity problems. The MAP-Elites extended archive's headline claim ("3 → 7 descriptors") is inflated: behavior_neediness is constant whenever a SLIP is supplied (always bin 1 for the default run) and mutation_stability is constant on the shipped corpus, while coverage divides by the full 5⁷ denominator — coverage is understated ~5× and only ~5–6 axes actually vary. The runtime-boundary gate's negative-probe count includes two hardcoded constants that can never fail. On the positive side: readability weights, QD-score, Spearman math, and division-by-zero guards were explicitly checked and are correct; package_promotion_gate genuinely reads artifacts (not self-satisfying).

Infrastructure — the deferred-dependency policy is now leaking. No pyproject.toml/requirements.txt anywhere (deliberate — schema_migration_gate.py:36 says "defer_python_jsonschema_until_dependency_manifest_exists"), but the environment has moved underneath it: .venv (3.13, empty) vs system 3.14 (pydantic, jsonschema in user site-packages leaking into every interpreter). The failing gate tests are the first casualty of that deferral. Everything is cwd-dependent (relative data/ paths in modules and tests), which works but is fragile.

---
(b) TODO — Flagged Issues

IDs are stable for reference. Sev: H=correctness/validity broken now, M=real defect on a reachable path, L=debt/hardening.

ID: H-01
Sev: H
Area: slip_validator
Location: test_pydantic_contract.py:49, test_schema_migration_gate.py:24
Issue: Tests assert jsonschema_available == False; jsonschema 4.26.0 in user site → 2 failures in every env. Uncommitted data/slips/**stage0.json already flipped to true
Fix direction: Assert report shape (key present, bool), not env snapshot; record env state in artifact only. Reconcile the 2 uncommitted stage0 JSONs + compatibility-matrix blocked-state
  wording in same commit
────────────────────────────────────────
ID: H-02
Sev: H
Area: grid_genome
Location: slip.py:47-53
Issue: validate_slip never checks required/extra keys in behavior/survival_weights — accepts profiles slip_validator.py + slip.schema.json reject (e.g. slip_survival_extra_key.json);
  gates seed selection via constrained_generator.*filter_seed_pool
Fix direction: Enforce exact key sets from schema; add failure-corpus cross-check test asserting both validators agree on all data/slips/failure_cases/
────────────────────────────────────────
ID: H-03
Sev: H
Area: map_elites
Location: extended_descriptors.py:326-333, 150, 347-351
Issue: behavior_neediness descriptor constant when SLIP supplied (always bin 1) → "7 descriptors" claim inflated; coverage divides by 5⁷ though ≤5⁶ niches reachable → coverage understated
  ~5×
Fix direction: Derive neediness from grid+slip interaction or drop axis; fix denominator; regenerate data/archives/map_elites_extended_stage0.json + update report/card claims
────────────────────────────────────────
ID: H-04
Sev: H
Area: workshop_editor
Location: aseprite*{tags_layers:161, tilemap_tileset:224, palette_slice:203, linked_cel:217, nested_timeline:177, external_properties:197, document_variant_resolution:262}
Issue: Unguarded json.loads after prefix check — malformed user-data chunk crashes import** with untyped JSONDecodeError (siblings third_party_project_decoder.py:243,
  aseprite_user_data_chunk_writer.py:770 kept the guard)
Fix direction: Wrap in typed AsepriteUserDataError; add malformed-JSON negative probe to each module's _invalid_probe_results
────────────────────────────────────────
ID: H-05
Sev: H
Area: workshop_editor
Location: png_embedded_sidecar_writer.py:388,398 vs standard_image_sidecar_decoder.py:380, png_adam7_interlace_decoder.py:589, png_deep_color_sidecar_decoder.py:767
Issue:_read_png_chunks ×5 divergent variants: different dict keys, CRC conventions, trailing-byte policy; embedded-writer variant silently accepts post-IEND bytes + raw
  UnicodeDecodeError on non-ASCII chunk type — and png_apng_sidecar_decoder.py imports that one
Fix direction: Factor one shared typed, trailing-byte-strict chunk reader; migrate all decoders
────────────────────────────────────────
ID: H-06
Sev: H
Area: research docs
Location: research/reports/ (newest: v0_5, 2026-05-12)
Issue: 43 experiment reports postdate v0_5 manifest (13× 05-13, 30× 05-14): entire PNG/APNG/Aseprite/spritesheet wave unconsolidated
Fix direction: Cut research_report_v0_6.md + manifest covering the 43 reports
────────────────────────────────────────
ID: M-01
Sev: M
Area: workshop_editor
Location: standard_image_sidecar_decoder.py:114, png_adam7_interlace_decoder.py:84, png_deep_color_sidecar_decoder.py:198, png_apng_sidecar_decoder.py:562,
  aseprite_user_data_chunk_writer.py:740, aseprite_tilemap_tileset_semantics.py:866+, png_textual_metadata_policy.py:556,634
Issue: Every zlib.decompress unbounded — size check runs after full inflate (decompression-bomb surface); expected size known up front in each case
Fix direction: Pass max_length via zlib.decompressobj, raise typed error on overflow
────────────────────────────────────────
ID: M-02
Sev: M
Area: workshop_editor
Location: third_party_project_decoder.py:331,344; project_native_metadata_writer.py:653; project_editor_rewrite_preservation.py:406
Issue: .pxo zip members read with no decompressed-size cap; dangling cel path from attacker-controlled data.json → raw KeyError (handler catches only BadZipFile)
Fix direction: Check ZipInfo.file_size cap; catch KeyError → ProjectDecodeError
────────────────────────────────────────
ID: M-03
Sev: M
Area: workshop_editor
Location: slip_preview_gates.py:426-431 (CLI at :529)
Issue: *profile_weight_effects_observed hard-indexes the 3 default profile ids — any custom --profile run crashes with raw KeyError
Fix direction: Iterate over actual by_profile keys
────────────────────────────────────────
ID: M-04
Sev: M
Area: workshop_editor
Location: png_apng_sidecar_decoder.py:247-250
Issue: except Exception reports all errors as apng_decode_failed — programming bugs masquerade as malformed-input rejections and count toward probe successes
Fix direction: Catch typed errors only, matching sibling importers
────────────────────────────────────────
ID: M-05
Sev: M
Area: grid_genome
Location: slip.py:34, 24-30, 39-45
Issue: vs authoritative validator: bool accepted as int for body-mass bounds; profile_id pattern ^[a-z0-9*]+$ unenforced; uniqueItems unenforced for allowed_palettes/required_organ_roles
Fix direction: Port the four checks from slip_validator.py; long-term: single shared validator (see L-04)
────────────────────────────────────────
ID: M-06
Sev: M
Area: grid_genome
Location: slip.py:104-107
Issue: is_grid_aligned compares value > limit on unvalidated grid data — non-numeric mutation value raises TypeError; bool silently compares
Fix direction: Validate grid mutation block before comparison; return alignment error
────────────────────────────────────────
ID: M-07
Sev: M
Area: grid_genome
Location: validator.py:129-139 + gaps
Issue: Schema invariants unenforced: grid_size 8–64 range, cell.role enum (12), cell.material enum (7), entire palette block, schema_version const, grid_id pattern — 4×4 grid with unknown
  roles passes
Fix direction: Add checks or document deliberate scope split in grid_invariants.md
────────────────────────────────────────
ID: M-08
Sev: M
Area: grid_genome
Location: validator.py:104-105
Issue: Body-core ≥ 4 cells is a magic number absent from grid_genome.schema.json and never tested
Fix direction: Add to schema or invariants doc; add sub-minimum negative test
────────────────────────────────────────
ID: M-09
Sev: M
Area: architecture
Location: mecha_engine_runtime_boundary_gate.py:364-381; test :55-57
Issue: 2 of 5 "negative probes" (package_runtime_imports_labs, package_test_mutates_sys_path_to_lab) are hardcoded accepted=False constants — probe count + closed-state
  lab_import_negative_probe_rejected trivially true; test can never fail
Fix direction: Implement real repo inspection (grep for lab imports under future packages/) or relabel as not_yet_probed
────────────────────────────────────────
ID: M-10
Sev: M
Area: readability
Location: slip_readability_calibration_gate.py:224-229 (vs_benchmark_summary:315-348)
Issue: `Unconditional by_source["selected_offspring"]["count"]` — empty source group → KeyError crash instead of zero-count report
Fix direction: .get(key, {}).get("count", 0)
────────────────────────────────────────
ID: M-11
Sev: M
Area: cubff
Location: real_snapshot_ingest.py:41-53, 54-72
Issue: One malformed record/line rejects entire snapshot file (.json comprehension aborts; .jsonl json.loads unguarded) — valid records lost
Fix direction: Per-record try/except; report rejected_records alongside accepted
────────────────────────────────────────
ID: M-12
Sev: M
Area: ctm_ticks
Location: ctm_inspired_ticks.py:75-78, 169-181, 305-310
Issue: confidence_gain subtracts across two different confidence formulas (switchboard vs _clamp(0.5+margin)); "prototype" decision keyed on mean_confidence_gain > 0 may be formula
  artifact
Fix direction: Recompute baseline confidence with same formula, or decide on a scale-free metric; re-derive decision
────────────────────────────────────────
ID: M-13
Sev: M
Area: research docs
Location: research/README.md ledger end
Issue: Two complete 05-14 triads invisible to ledger and all manifests: png_adam7_deep_color_cross_product, png_deep_color_sidecar_decoder (reports+cards+labs+stage0 all exist)
Fix direction: Add ledger entries; include in v0_6 manifest (H-06)
────────────────────────────────────────
ID: M-14
Sev: M
Area: research docs
Location: research/decision_records/0001-...md Sources
Issue: Broken path docs/01-notes/01-shelved/03-reports/03-deep_research_report.md → actual docs/01-shelved/... (only broken Sources ref in repo, 149/150)
Fix direction: Fix path
────────────────────────────────────────
ID: M-15
Sev: M
Area: infra
Location: no pyproject.toml/requirements*.txt; .venv (3.13, empty) vs system 3.14 + user-site leakage
Issue: Deliberate dependency deferral (schema_migration_gate.py:36) now leaking: user site-packages flip gate outcomes (caused H-01); python resolves to system 3.14, venv unused
Fix direction: Decision point: author the dependency manifest the gate is waiting for, or isolate gates with -I/-s (ignore user site) and pin the intended interpreter in docs
────────────────────────────────────────
ID: L-01
Sev: L
Area: grid_genome tests
Location: test_slip_constraints.py; validator.py:105
Issue: is_grid_aligned rejection branches (palette/body-mass/role/mutation-cap) never asserted False; body-core-below-minimum never exercised
Fix direction: Add negative tests per branch
────────────────────────────────────────
ID: L-02
Sev: L
Area: grid_genome
Location: validator.py:161-181
Issue: Connectivity BFS is 8-directional while body cores are authored 4-connected — diagonal-only cores pass a looser invariant than geometry implies
Fix direction: Decide + document in grid_invariants.md; align BFS
────────────────────────────────────────
ID: L-03
Sev: L
Area: grid_genome
Location: switchboard_feedback.py:36,99
Issue: rng_seed param drives nothing (episode fully deterministic) yet echoed into report — misleading reproducibility field
Fix direction: Remove param or wire it
────────────────────────────────────────
ID: L-04
Sev: L
Area: grid_genome
Location:_cell/_grid_from_matrix ×3 (corpus_builder:194, markov_grid:102,194, constrained_generator:186,283); run_baseline ×3;_signature ×2
Issue: Triplicated helpers, drift risk; also SLIP validation logic exists in 3 places (slip.py / slip_validator.py / pydantic_contract.py)
Fix direction: Factor shared helpers module within lab
────────────────────────────────────────
ID: L-05
Sev: L
Area: grid_genome
Location: slip.py:3
Issue: Palette validation imports PALETTES from corpus_builder instead of schema enum — contract coupled to generator
Fix direction: Source palette ids from slip.schema.json
────────────────────────────────────────
ID: L-06
Sev: L
Area: workshop_editor tests
Location: e.g. test_standard_image_sidecar_decoder.py:50-58, test_png_apng_sidecar_decoder.py:51-118
Issue: All 249 tests are self-referential round-trips (decode own encoder's output; negatives mutate own output) — no foreign PNG/APNG/.aseprite fixtures; multi-IDAT join, real
  dispose/blend, mixed filters never exercised
Fix direction: Add small foreign-fixture corpus under data/ + conformance tests
────────────────────────────────────────
ID: L-07
Sev: L
Area: workshop_editor
Location: slip_preview_gates.py:173, 187-188
Issue: symmetry_break_budget set equal to its own cap → caps_respected trivially true, field implies computed value that isn't
Fix direction: Compute real candidate count or drop field
────────────────────────────────────────
ID: L-08
Sev: L
Area: repo-wide
Location: e.g. external_metadata_sidecar.py:22-23, standard_image_sidecar_decoder.py:481, test_slip_readability_calibration_gate.py:21
Issue: Modules anchor imports on ROOT = parents[2] but leave data paths cwd-relative; tests only pass from repo root
Fix direction: Anchor default paths on ROOT; note requirement in CLAUDE.md (done)
────────────────────────────────────────
ID: L-09
Sev: L
Area: cubff
Location: cubff_transducer.py:379-395
Issue: reason text claims "semantic compilation beats direct projection" even when status="reject_direct_mapping" — narrative contradicts gate
Fix direction: Branch reason on status
────────────────────────────────────────
ID: L-10
Sev: L
Area: package_promotion
Location: package_promotion_gate.py:103,162,184
Issue: research_blockers hardcoded in registry (e.g. human_ratings_absent) — would force hold_research_only even if artifact showed ratings collected
Fix direction: Derive blockers from metric artifacts
────────────────────────────────────────
ID: L-11
Sev: L
Area: lifecycle_sim
Location: lifecycle_sim.py:163, 205-215
Issue: survival_ticks counts the death tick (+1 vs "ticks fully survived"); feeds survival_ratio in map_elites + CA labs
Fix direction: Define semantics; adjust or document
────────────────────────────────────────
ID: L-12
Sev: L
Area: map_elites
Location: extended_descriptors.py:314-323
Issue: mutation_stability constant on shipped corpus (all 50 seeds share identical mutation rates) — second low-information axis
Fix direction: Note in report; vary mutation block in generated candidates
────────────────────────────────────────
ID: L-13
Sev: L
Area: cubff
Location: cubff_transducer.py:210-219 vs 485-494
Issue: Semantic grids compiled + readability-scored twice (main + run_transducer_lab)
Fix direction: Pass through
────────────────────────────────────────
ID: L-14
Sev: L
Area: research docs
Location: research/README.md; research/algorithm_cards/{cubff_transducer,lineage_tracking,markov_grid}.md
Issue: 11 v0_1-era reports absent from README flat list (manifest-covered, so traceable); 3 cards referenced nowhere; 23 modules ledgered under non-matching slugs
Fix direction: Backfill ledger entries; normalize slugs opportunistically

Suggested attack order: H-01 + M-15 together (unblocks the suite and settles the dependency question), then H-02/M-05/M-06 as one SLIP-validator-alignment change, H-04 + H-05 + M-01 as one workshop_editor hardening pass, H-03 as a metrics-integrity fix with artifact regeneration, and H-06 + M-13 + M-14 as one documentation-ledger commit. Per repo convention, each of these needs its triad docs updated in the same change.
────────────────────────────────────────
Final state: all 12 lab suites green — 386 tests (was 374/376 passing at review time), all HIGH findings closed, all stage0 artifacts regenerated and JSON-validated, every batch documented as a dated experiment report ledgered in research/README.md per the triad convention.

Still open (tracked in the review doc with live annotations):
- M-02–M-04, M-07–M-12 — medium items not in the attack order (pxo zip caps, hardcoded profile ids, broad except, validator/schema scope split, self-satisfying boundary probes, calibration-gate KeyError, snapshot ingest, CTM confidence scales)
- L-02–L-15 — including the new L-15 found during Batch 3 (three more _read_png_chunks copies in the APNG frame-data labs)
- M-15 remainder — the dependency-manifest decision itself, deliberately left to you: creating one flips dependency_manifest_present and triggers the migration gate's own revisit policy

The v0.6 report already notes remediation continues in v0.7, so the doc trail is set up for whenever you want to work through the remaining M/L items.
────────────────────────────────────────
