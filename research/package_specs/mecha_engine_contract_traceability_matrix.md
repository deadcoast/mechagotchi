# Mecha Engine Contract Traceability Matrix

Date: 2026-05-12

## Status

Research traceability matrix. This document does not create or modify
`packages/mecha_engine` and does not move lab code.

## Purpose

Translate the scaffold gate and five module contract gates into concrete future
package test obligations. This is the bridge between research acceptance gates
and implementation-stage tests, so package work can start from evidence instead
of recollection.

## Scope

Included package surfaces:

- scaffold and import boundary
- `mecha_engine.genome`
- `mecha_engine.generation`
- `mecha_engine.lifecycle`
- `mecha_engine.archive`
- `mecha_engine.provenance`

Excluded from this matrix:

- package creation
- package implementation
- migration of lab modules
- online reward-shaping promotion
- ~~CA/NCA repair promotion~~ — no longer excluded: the wound-site arm
  cleared the stability blocker (2026-07-04), decision record 0006
  authorized the target (2026-07-05), and the repair row below is now an
  enforced contract like the initial five
- readability calibration without human ratings
- release license metadata
- full REUSE/legal-review/SBOM compliance

## Package Test Order

The future implementation should preserve this order:

1. Scaffold import-surface tests.
2. Genome validation tests.
3. Generation tests that call the package genome API.
4. Lifecycle tests that reject invalid grids before simulation.
5. Archive tests that validate candidates through package genome APIs.
6. Provenance tests that run without importing lab modules.
7. Package-promotion gate rerun after package tests exist.

This order is load-bearing. Generation, lifecycle, and archive tests depend on
the package genome contract being real enough to validate candidates.

## Traceability Matrix

| Surface | Source Gate | Future Package Test | Required Assertions |
| --- | --- | --- | --- |
| Scaffold | `mecha_engine_scaffold_verification_gate.md` | `tests/test_package_imports.py` | Import `mecha_engine`, `genome`, `generation`, `lifecycle`, `archive`, and `provenance`; verify package metadata boundary; verify no implementation migration in scaffold step |
| Genome | `mecha_engine_genome_contract_gate.md` | `tests/test_genome_contract.py` | Accept 50 seed grids; reject 200 invalid counterexamples; do not mutate inputs; deterministic signatures; renderer packet is JSON-serializable |
| Generation | `mecha_engine_generation_contract_gate.md` | `tests/test_generation_contract.py` | Train only on valid seeds; reject invalid parents; produce valid candidates; produce deterministic batches; reproduce constrained `100/100` and SLIP-aligned `50/50` gates |
| Lifecycle | `mecha_engine_lifecycle_contract_gate.md` | `tests/test_lifecycle_contract.py` | Reject invalid grids; clamp state variables; preserve deterministic episodes; reproduce switchboard/idle/random comparator; keep reward shaping out of package state |
| Archive | `mecha_engine_archive_contract_gate.md` | `tests/test_archive_contract.py` | Validate candidate grids; compute deterministic descriptors; insert/replace only by niche fitness; keep scalar top-k comparator-only; report coverage, QD score, and calibration status |
| Provenance | `mecha_engine_provenance_contract_gate.md` | `tests/test_provenance_contract.py` | Parse supported SPDX expressions; reject unknown IDs and lowercase operators under Stage 0 policy; verify file/tree hashes; enforce decision-record gate; generate attribution manifest |
| Repair (promoted 2026-07-05, decision record 0006) | `mecha_engine_repair_interface_spec.md` | `tests/test_repair_contract.py` | Honor the observability contract (damage events report `removed_cells`, never destroyed tokens, never a template); fill exactly the reported sites; assert overlap == structural agreement for the site-aware surface; reproduce the lab benchmark via a lab-parity pin (guarded 0.938462/0.938462/1.0; guard-off 0.930769/0.930769/0.9; blind arm recorded below bar); deterministic including validity-guard substitutions; `target_template_used == false` on every result; SLIP-aware guard: with the active profile a valid-but-unaligned refill becomes lifecycle-acceptable, without it behavior is bit-identical (driver `slip_aware_guard` probe + slip-aware parity case) |

| Runtime (promoted 2026-07-05, decision record 0008 accepted) | `mecha_engine_runtime_interface_spec.md` | `tests/test_runtime_contract.py` | Lab-parity pin reproducing both runtime-lab artifact summaries (single loop 12/12 retention 1.0; evolution 32/32, 96 damage events, retention 1.0, 15 niches, QD 13.92); SLIP-aware repair throughout; readability injected and visibly uncalibrated; deterministic, no input mutation, no labs imports; validity gate on episodes (promotion-drift fix 2026-07-07): aligned-but-invalid repairs carry no episode, record `skipped_invalid`, never score — `invalid_repair_boundary` driver probe + lab-side boundary parity (`labs/runtime_integration/test_invalid_repair_semantics.py`) |

| Learning (promoted 2026-07-05, decision record 0009) | `mecha_engine_learning_interface_spec.md` | `tests/test_learning_contract.py` | Bounded claim only (need-balance +0.080069 stress / +0.03964 sheltered at zero survival cost; NO survival claim); decide parity with the lab switchboard over episode trajectories; feedback/frozen episode parity incl. the need-balance delta pins; lifecycle driven through its public surface only; deterministic, no input mutation, no labs imports |

| Storage (promoted 2026-07-07, decision record 0022, cycle 03 C3) | `research/decision_records/0022-storage-module.md` (the schema and the eight gates ARE the contract) | `tests/test_storage_contract.py` | Schema v1 (`user_version`, foreign keys); blob-authoritative byte-identical round-trips; derived columns pinned to their blobs; founder pool in niche-key order; unlock state via the predecessor pointer (never copied); replay-sufficient history; atomic one-transaction eras (rollback observed); bad versions and foreign schemas refused; no labs imports, no `sys.path`; lab-side pins: source-verbatim + row-for-row behavior parity over the real interim (`labs/game_loop/test_package_storage_parity.py`), the eight-gate suite over real engine output (`labs/game_loop/test_campaign_store.py`) |

| Slip (promoted 2026-07-07, decision record 0027, cycle 06 F2) | `research/decision_records/0027-slip-module-disposition.md` (the port gates) | `tests/test_slip_contract.py` | Every valid fixture passes; every failure case rejected; the SLIP zoo judged; ladder rungs version-gated and bounded; alignment accepts/rejects with named errors; deterministic, pure, no labs imports, no `sys.path`; gate-1 reconciliation measured ZERO divergences five-way pre-collapse; lab-side pin: exact verdict-and-error-string parity with the Stage 0 authority over the whole corpus + corruptions + seed alignment (`labs/grid_genome/test_package_slip_parity.py`); the workshop server's promised switch fulfilled |

## Cross-Cut Negative Tests

Every package test slice must enforce:

- package tests import `mecha_engine`, not `labs`;
- package tests do not mutate `sys.path` to reach `labs`;
- package runtime code does not import `labs`;
- package runtime code performs no Stage 0 artifact writes on import;
- package APIs return JSON-serializable dictionaries or typed results where
  the contract requires them;
- package APIs do not mutate caller-owned input dictionaries unless a later
  contract explicitly allows mutation;
- package promotion gate is rerun after package tests exist.

Required scan after package implementation begins:

```powershell
rg -n "from labs|import labs|labs/|labs\\|sys\\.path" .\packages\mecha_engine
```

Expected result: no matches.

## Scaffold Test Obligations

Future `tests/test_package_imports.py` must verify:

- `packages/mecha_engine/pyproject.toml` exists;
- `packages/mecha_engine/README.md` exists;
- `packages/mecha_engine/src/mecha_engine/__init__.py` exists;
- `packages/mecha_engine/src/mecha_engine/py.typed` exists;
- each initial module package imports;
- `project.name` is `mecha-engine`;
- distribution metadata does not declare release license fields until the
  package/repository license decision is explicit;
- the first scaffold contains no copied lab implementation.

## Genome Test Obligations

Future `tests/test_genome_contract.py` must verify:

- `validate_grid` accepts all 50 seed grids from `data/seed_grids`;
- `validate_grid` rejects all 200 invalid grids from `data/invalid_grids`;
- `validate_grid_file` uses the same semantic rules as `validate_grid`;
- ordinary invalid payloads return structured errors instead of throwing;
- validation does not mutate input payloads;
- `grid_signature` is deterministic;
- `grid_signature` changes for semantic grid changes;
- `grid_signature` ignores non-semantic review metadata;
- `render_packet_from_grid` returns JSON-serializable renderer-neutral data.

## Generation Test Obligations

Future `tests/test_generation_contract.py` must verify:

- `train_generation_model` rejects empty or invalid seed corpora;
- `generate_candidate` rejects invalid parents before proposal generation;
- every returned candidate passes `mecha_engine.genome.validate_grid`;
- generation preserves parent ID, generation number, ancestor IDs, and trace;
- deterministic RNG seeds reproduce candidates and batches;
- `generate_batch` returns exactly the requested count;
- batch candidates have unique candidate IDs;
- constrained generation reproduces the `100/100` validity gate;
- SLIP-constrained generation reproduces the `50/50` valid and aligned gate;
- raw Markov output is not exposed as the production generator.

## Lifecycle Test Obligations

Future `tests/test_lifecycle_contract.py` must verify:

- invalid grids fail before simulation;
- supplied SLIP profiles are validated before state creation;
- `initial_state` does not mutate the grid or profile;
- `advance_tick` only accepts the supported first action set;
- continuous state values stay inside `[0, 1]`;
- death causes are explicit;
- early death cannot inflate need-balance by shortening the scoring horizon;
- deterministic episodes reproduce for the same inputs and RNG seed;
- switchboard/idle/random comparator metrics are reproduced or revised through
  a new decision record;
- reward values stay inside `[0, 1]`;
- online learner memory remains outside `mecha_engine.lifecycle`;
- **the public surface is exactly the contracted set** (exact `__all__`
  equality), now **seven** names after O1 promoted `DANGER_THRESHOLDS`;
- **`DANGER_THRESHOLDS` is pinned BY VALUE**, not merely by presence — a
  promoted constant whose numbers can drift is not a contract — and
  **covers every lethal axis**, because a threshold set missing one
  would let a health bar read healthy on a dying companion (the failure
  DR 0054 refused `grid_stability` for);
- **the promotion did not widen beyond the constant**: neither
  `danger_margin` nor `health` appears on the lifecycle surface, so
  whether the margin formula belongs in the engine stays a separate
  decision with its own gate.
- **the cleanliness mechanic seam (P3, DR 0059) is byte-identical when
  off**: `mechanics=None` reproduces the committed Stage 0 comparator
  episodes verbatim and the off-mode state key set matches a frozen
  literal list; the seam's derived constants (decay 0.0124, mutate mess
  0.055, clean restore 0.32, dirt-to-stress 0.01) are pinned BY VALUE;
  `clean` without the mechanic raises the incumbent error verbatim; the
  mechanic is non-lethal and the autonomous action vocabulary is
  untouched (`tests/test_lifecycle_cleanliness_seam.py`).

## Archive Test Obligations

Future `tests/test_archive_contract.py` must verify:

- invalid candidate grids cannot become elites;
- baseline and extended descriptors return deterministic integer tuples;
- descriptor metadata exposes names and cardinalities;
- `score_candidate` returns bounded components and aggregate fitness;
- `insert_candidate` inserts into empty niches;
- `insert_candidate` replaces only when the new candidate has higher fitness;
- deterministic tie handling is explicit;
- scalar top-k remains a comparator, not an archive replacement;
- archive summaries report total possible niches, occupied niches, coverage,
  best fitness, mean elite fitness, QD score, blocked counts, and readability
  calibration status;
- final descriptor thresholds remain unlocked until human readability ratings
  exist.

## Provenance Test Obligations

Future `tests/test_provenance_contract.py` must verify:

- `parse_spdx_expression` accepts the project-supported SPDX subset;
- unknown SPDX license IDs are rejected;
- unknown exception IDs are rejected;
- lowercase operators remain rejected under the Stage 0 policy;
- file hashes use `sha256`;
- directory hashes use deterministic `sha256-tree`;
- missing included hashes fail;
- stale included hashes fail;
- included share-alike or copyleft assets require `decision_record`;
- reference-only assets are excluded from shipped assets;
- attribution-required assets appear in the attribution manifest;
- `build_ci_report` returns the four required checks:
  `ledger_validation_ok`, `spdx_expressions_ok`, `included_hashes_ok`, and
  `decision_record_gate_ok`.

## Future Verification Command Set

After package implementation begins, the full first-pass verification set is:

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "import mecha_engine, mecha_engine.genome, mecha_engine.generation, mecha_engine.lifecycle, mecha_engine.archive, mecha_engine.provenance"
rg -n "from labs|import labs|labs/|labs\\|sys\\.path" .\packages\mecha_engine
python -B .\labs\grid_genome\test_validator.py
python -B .\labs\grid_genome\test_constrained_generator.py
python -B .\labs\lifecycle_sim\test_lifecycle_sim.py
python -B -m unittest discover -s .\labs\map_elites_archive -p "test_*.py"
python -B -m unittest discover -s .\labs\asset_pipeline -p "test_*.py"
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
git diff --check
```

The lab commands are regression references. Package tests must still prove the
installed `mecha_engine` surface directly.

## Sources

- `research/package_specs/mecha_engine_scaffold_verification_gate.md`
- `research/package_specs/mecha_engine_genome_contract_gate.md`
- `research/package_specs/mecha_engine_generation_contract_gate.md`
- `research/package_specs/mecha_engine_lifecycle_contract_gate.md`
- `research/package_specs/mecha_engine_archive_contract_gate.md`
- `research/package_specs/mecha_engine_provenance_contract_gate.md`
- `research/reports/mechagotchi_research_report_v0_5.md`
- `data/architecture/mecha_engine_scaffold_verification_gate_stage0.json`
- `data/architecture/mecha_engine_genome_contract_gate_stage0.json`
- `data/architecture/mecha_engine_generation_contract_gate_stage0.json`
- `data/architecture/mecha_engine_lifecycle_contract_gate_stage0.json`
- `data/architecture/mecha_engine_archive_contract_gate_stage0.json`
- `data/architecture/mecha_engine_provenance_contract_gate_stage0.json`
