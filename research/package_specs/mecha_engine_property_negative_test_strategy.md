# Mecha Engine Property and Negative Test Strategy

Date: 2026-05-12

Status: `research_property_negative_test_strategy_no_package_code`

Target package root: `packages/mecha_engine`

Package root exists at authoring: no

## Purpose

This strategy defines how the future `mecha_engine` package tests should prove
the formal invariant/dependency gate without relying on convenient hand-picked
examples. It translates the fixture manifest and formal invariant families into
property-style tests, single-fault negative tests, metamorphic checks, and
cross-module rejection paths.

This is a research artifact only. It does not create package code, package
tests, package dependencies, or a package root.

## Source Position

The current package handoff has four layers:

1. module interfaces define package surfaces;
2. contract gates define per-module acceptance;
3. fixture manifest defines concrete data evidence;
4. formal invariant gate defines cross-module admissibility.

This file adds the missing test-design layer:

```txt
fixtures + invariants -> future test generators + future oracles
```

The package tests must still import `mecha_engine`, not `labs`. Lab artifacts
remain regression references only.

## External Testing Anchors

The strategy uses external testing sources for method discipline:

- Python `unittest` is the default runner boundary already used by the package
  traceability matrix. The official docs describe test discovery, assertion
  methods, and exception assertions.
- Hypothesis is a candidate property-based test dependency because its official
  docs describe generated inputs, edge cases, and property checks. It is not a
  required dependency until a future package dependency decision explicitly adds
  it.
- Python `jsonschema` validation docs anchor schema-test behavior: schema
  validation, `Draft202012Validator`, `is_valid`, `iter_errors`, and
  `validate` error behavior.

The required test strategy must be implementable with deterministic fixture
derivation and `unittest` alone. Hypothesis may later broaden input coverage,
but no package gate may depend on an undeclared test dependency.

## Test Taxonomy

| Test type | Role | Required before promotion |
| --- | --- | --- |
| Fixture regression | Replays the frozen repository corpora and metrics. | yes |
| Single-fault negative | Derives one invalid mutation at a time from valid fixtures. | yes |
| Property-style invariant | Checks general rules across generated or fixture-derived inputs. | yes |
| Metamorphic | Applies transformations where expected validity or signature behavior is known. | yes |
| Cross-module rejection | Proves invalid upstream state cannot flow downstream. | yes |
| Boundary/import | Proves package runtime and tests do not import `labs` or mutate `sys.path`. | yes |
| Promotion rerun | Re-executes package promotion after package tests exist. | yes |
| Human-calibration | Proves manual readability ratings drive thresholds. | blocked |

## Runner and Dependency Policy

The first package test suite must be runnable with:

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
```

`pytest`, Hypothesis, mutation-testing tools, fuzzers, and coverage tools are
optional future enhancements. They require explicit package/dev-dependency
decisions before they can become required gates.

If Hypothesis is adopted later, it should target properties that have compact
oracles:

- generated valid grids always pass package genome validation;
- single-fault corruptions fail for the intended reason family;
- repeated validation does not mutate input;
- deterministic seeds reproduce candidate identity and trace;
- bounded lifecycle state remains finite;
- archive insertion is monotonic per descriptor niche;
- SPDX operator case remains strict.

## Property Families and Oracles

### P1. Schema and Structural Grid Admissibility

Input generator:

- every seed grid in `data/seed_grids/*.json`;
- fixture-derived single-fault variants from each seed grid.

Single-fault variants:

- coordinate outside declared bounds;
- duplicate occupied coordinate;
- unknown semantic role;
- mutation weight below minimum;
- mutation weight above maximum;
- body mass below minimum;
- body mass above maximum;
- disconnected occupied body;
- missing sensor cell;
- missing animation anchor;
- organ reference to an absent cell;
- palette reference not declared in palette contract.

Oracle:

- unmodified seed grid passes;
- single-fault variant fails;
- failure result contains structured error information;
- validation does not mutate input.

### P2. Invalid Corpus Rejection

Input generator:

- every invalid grid in `data/invalid_grids/*.json`;
- a deterministic sample of two independent fault combinations derived from
  seed grids after single-fault testing is already passing.

Oracle:

- every invalid input fails;
- invalid input does not become a generation parent;
- invalid input does not become a lifecycle subject;
- invalid input does not become an archive elite;
- invalid input does not produce a renderability claim.

### P3. Generation Validity and Trace

Input generator:

- valid seed parent grids;
- valid SLIP profiles;
- invalid SLIP profiles;
- deterministic RNG seeds.

Oracle:

- invalid parent is rejected before proposal generation;
- invalid SLIP profile is rejected before constrained generation;
- returned candidate grid passes package genome validation;
- candidate trace preserves parent ID, generator ID, seed, profile ID when
  used, rejected proposal count, and validation status;
- same inputs and seed reproduce candidate identity and grid signature;
- generated batch size equals request;
- generated batch candidate IDs are unique within the batch.

### P4. Lifecycle Boundedness and Rejection

Input generator:

- valid seed grid;
- invalid grid;
- valid SLIP profile;
- supported first action set;
- deterministic episode seed.

Oracle:

- invalid grid fails before state creation;
- invalid profile fails before profile-weighted state creation;
- `initial_state` does not mutate grid or profile;
- every continuous state value stays in `[0, 1]`;
- every reward value stays in `[0, 1]`;
- death cause is explicit;
- same inputs and seed reproduce the episode summary;
- switchboard, idle, and random comparator scenarios reproduce or are replaced
  by a decision-recorded successor.

### P5. Archive Niche Correctness

Input generator:

- package-valid candidates from lineage fixtures;
- deterministic lifecycle metric fixtures;
- descriptor functions for baseline and extended archive modes.

Oracle:

- invalid candidate grids cannot become elites;
- descriptor key is a deterministic integer tuple;
- metadata exposes descriptor names and cardinalities;
- empty niche accepts first valid candidate;
- occupied niche replaces only when the candidate has higher documented
  fitness for that same niche;
- tie behavior is deterministic and documented;
- scalar top-k never replaces MAP-Elites archive behavior;
- summary reports coverage, occupied niches, best fitness, mean elite fitness,
  QD score, blocked counts, and readability calibration status.

### P6. Provenance and License Strictness

Input generator:

- ledger entries from `data/asset_provenance/ledger.json`;
- valid SPDX expressions from current fixtures;
- single-token SPDX mutations;
- included asset paths and altered hashes.

Oracle:

- supported expressions parse;
- unknown license IDs fail;
- unknown exception IDs fail;
- lowercase `and`, `or`, and `with` fail under Stage 0 policy;
- included asset hashes use `sha256`;
- directory hashes are deterministic `sha256-tree`;
- missing included hashes fail;
- stale included hashes fail;
- included share-alike or copyleft assets require a decision record;
- reference-only assets remain excluded from shipped asset lists.

### P7. Cross-Module Failure Propagation

Input generator:

- invalid grids from P1 and P2;
- invalid profiles;
- lifecycle outputs with non-finite or out-of-range values;
- provenance reports with failed checks.

Oracle:

- generation rejects invalid parents;
- lifecycle rejects invalid grids and profiles;
- archive rejects invalid candidates and invalid lifecycle metrics;
- render packet creation rejects invalid grids;
- package promotion rejects provenance failure;
- blocked states remain blocked, not partially accepted.

### P8. Boundary and Import Hygiene

Input generator:

- future package source tree;
- future package tests;
- import statements;
- package import side effects.

Oracle:

- package runtime imports do not reference `labs`;
- package tests do not reference `labs`;
- package tests do not mutate `sys.path`;
- importing package modules writes no Stage 0 artifacts;
- package outputs remain JSON-serializable where report contracts require JSON.

## Metamorphic Checks

The future test suite must include these metamorphic checks after the package
genome API exists:

| Transformation | Expected result |
| --- | --- |
| Reorder non-semantic metadata fields | same semantic signature |
| Change semantic role of an occupied cell | different semantic signature |
| Deep-copy input before validation | copied and original payloads remain equal after validation |
| Validate same payload twice | same result and same error family |
| Use same generator seed and parent | same candidate identity and grid signature |
| Use different generator seed with same parent | candidate identity or trace seed differs |
| Insert weaker candidate into occupied archive niche | existing elite remains |
| Insert stronger candidate into occupied archive niche | elite changes to stronger candidate |
| Lowercase SPDX operator | expression rejected under Stage 0 policy |

## Required Future Test Allocation

| Future file | Required strategy coverage |
| --- | --- |
| `tests/test_package_imports.py` | import hygiene, metadata boundary, no import-time writes |
| `tests/test_genome_contract.py` | P1, P2, genome metamorphic checks |
| `tests/test_generation_contract.py` | P3, invalid-parent propagation, deterministic batches |
| `tests/test_lifecycle_contract.py` | P4, invalid-grid rejection, bounded state |
| `tests/test_archive_contract.py` | P5, scalar top-k separation |
| `tests/test_provenance_contract.py` | P6, SPDX mutation tests, hash tests |
| `tests/test_cross_module_invariants.py` | P7, package-wide blocked-state propagation |
| `tests/helpers/fixtures.py` | fixture loading without importing `labs` |
| `tests/helpers/mutators.py` | deterministic single-fault fixture derivation |

Helper files are allowed only after package implementation starts. They must
not import from `labs`.

## Required Blocked-State Assertions

Future package tests must assert that these are blocked:

- human-calibrated readability thresholds before manual ratings exist;
- archive descriptors claiming human calibration before manual ratings exist;
- real CuBFF adoption without real snapshot artifacts;
- online reward-shaping promotion before it beats the frozen baseline under
  dynamic stress;
- release license metadata before package and repository license decision
  records exist.

## Required Research-Time Checks

This research artifact is verified with:

```powershell
python -m json.tool .\data\architecture\mecha_engine_property_negative_test_strategy_stage0.json
Test-Path .\packages
rg -n "mecha_engine_property_negative_test_strategy|research_property_negative_test_strategy_no_package_code" .\research .\data
git diff --check
```

## Future Package Verification Command Set

After package implementation explicitly starts, the first complete package-test
gate is:

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
python -c "import mecha_engine, mecha_engine.genome, mecha_engine.generation, mecha_engine.lifecycle, mecha_engine.archive, mecha_engine.provenance"
rg -n "from labs|import labs|labs/|labs\\|sys\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
git diff --check
```

Lab commands may be used as regression references, but package promotion cannot
be proven by lab tests alone.

## Decision

Adopt this property and negative test strategy as the next package handoff
artifact. It makes the future test suite responsible for proving invariants,
not for demonstrating a few convenient successful examples.

Next research step:

```txt
Use this strategy to produce the first implementation checklist only after the
user explicitly starts `packages/mecha_engine` package work.
```

## References

- `docs/01-brainstorming.md`
- `docs/02-research_plan.md`
- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `research/package_specs/mecha_engine_test_fixture_manifest.md`
- `research/package_specs/mecha_engine_formal_invariant_dependency_gate.md`
- `data/architecture/mecha_engine_contract_traceability_matrix_stage0.json`
- `data/architecture/mecha_engine_test_fixture_manifest_stage0.json`
- `data/architecture/mecha_engine_formal_invariant_dependency_gate_stage0.json`
- Python unittest docs: https://docs.python.org/3.11/library/unittest.html
- Hypothesis docs: https://hypothesis.readthedocs.io/en/latest/
- Python jsonschema validation docs: https://python-jsonschema.readthedocs.io/en/v4.22.0/validate/
