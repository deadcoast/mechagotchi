# Mecha Engine Formal Invariant Dependency Gate

Date: 2026-05-12

Status: `research_formal_invariant_dependency_gate_no_package_code`

Target package root: `packages/mecha_engine`

Package root exists at authoring: no

## Purpose

This gate defines the load-bearing invariants and dependency ordering that the
future `mecha_engine` package must preserve across `genome`, `generation`,
`lifecycle`, `archive`, and `provenance`.

This is a research handoff artifact. It does not create package code, package
tests, or a package root. It exists to prevent the future package migration from
turning lab successes into convenient examples without preserving the evidence
chain.

## Source Position

The governing research plan defines the grid as:

```txt
G = (C, A, N, O, M, P)
```

Where:

- `C` is the cell set;
- `A` is the per-cell attribute map;
- `N` is neighborhood topology;
- `O` is organ and semantic region membership;
- `M` is mutation permission and weight state;
- `P` is palette and render constraint state.

This gate treats `G` as the root admissibility object. A downstream module may
not treat a grid as valid unless the future package genome API accepts it.

## External Anchors

The gate uses external sources only for boundary discipline:

- JSON Schema Draft 2020-12 is the formal schema dialect for the grid genome
  schema. The official draft page identifies the 2020-12 specification and
  meta-schema.
- The Python `jsonschema` project exposes a `Draft202012Validator` for repeated
  validation, schema checking, and collecting validation errors.
- MAP-Elites is the research basis for the archive module because it stores
  high-performing solutions over user-chosen behavioral or phenotypic
  dimensions instead of reducing evolution to one scalar winner.
- Wave Function Collapse is used as a constraint-propagation reference for
  local grid coherence, not as a claim that the package has adopted a complete
  WFC implementation.
- SPDX license expressions and the SPDX License List define the provenance
  syntax and identifier normalization that the package provenance gate must
  preserve.

These sources do not override the repository fixtures or local gates. They
justify terminology and failure semantics only.

## Formal Model

```txt
G = grid genome payload
V(G) = genome validation result
P = SLIP profile or null profile
C = generated candidate with grid, lineage, and trace metadata
E = lifecycle episode result
D = archive descriptor
F = fitness vector or scalar comparator value
A = archive state
R = provenance report
```

The minimum admissibility chain is:

```txt
V(G).ok
  -> generation may use G as a parent
  -> generation returns C
  -> V(C.grid).ok
  -> lifecycle may simulate C.grid
  -> lifecycle returns finite bounded E
  -> archive may derive D and F from C and E
  -> archive may update A
  -> provenance R must be ok before package promotion
  -> genome may produce render packet from accepted G or C.grid
```

No module may silently repair, clip, or downgrade an invalid object into a valid
downstream state without recording that transition as rejected or blocked.

## Dependency Graph

```txt
scaffold
  -> genome
      -> generation
      -> lifecycle
          -> archive
  -> provenance

generation -> genome
generation -> SLIP profile contract when profile constraints are used
lifecycle -> genome
lifecycle -> SLIP profile contract when profile-weighted needs are used
archive -> genome
archive -> generation trace
archive -> lifecycle metrics
archive -> readability evidence when human-calibrated descriptors are claimed
provenance -> asset ledger, hashes, SPDX syntax, decision records
provenance -> package promotion
```

`provenance` is cross-cutting. It must not become a runtime dependency for
normal genome validation or lifecycle simulation, but promotion may not pass
without it.

## Invariant Families

### 1. Structural Grid Invariants

The genome module owns these invariants:

- grid schema is Draft 2020-12 compatible;
- cells remain within declared bounds;
- occupied coordinates are unique;
- semantic roles are known;
- mutation weights remain bounded;
- body mass is within the accepted range;
- occupied body remains connected when the profile requires one body;
- sensor and animation-anchor requirements are enforced;
- organ memberships reference existing occupied cells;
- palette and render packet constraints remain satisfiable.

Repository evidence:

- 50 hand-authored seed grids are accepted by the current validator.
- 200 invalid counterexamples are rejected by the current validator.

### 2. Validation Monotonicity

Once a payload fails `V(G)`, downstream modules must treat it as inadmissible:

- generation must reject invalid parents;
- lifecycle must refuse simulation for invalid grids;
- archive must refuse insertion for invalid candidates;
- render-packet production must not claim renderability for invalid grids.

An invalid object may be used only inside a negative test or repair experiment,
and the output must remain marked as rejected until a fresh package genome
validation passes.

### 3. Bounded Continuous Values

The package must preserve explicit numeric bounds:

- mutation weights are in the interval defined by the genome schema;
- lifecycle state values such as need balance, stress, energy, and mood
  components remain finite;
- lifecycle scores and archive fitness components remain bounded and
  JSON-serializable;
- generator SLIP alignment and profile weights are finite and bounded;
- archive descriptors are deterministic bins, not unbounded floats.

If a lab prototype uses clipping to recover from numeric drift, the package
must expose that recovery as a recorded correction or rejected state. Silent
clipping is not accepted as evidence.

### 4. Determinism and Reproducibility

For the same declared seed, parent grid, profile, and fixture corpus, package
outputs that are documented as deterministic must reproduce:

- candidate grid;
- validation result;
- lifecycle episode summary;
- archive descriptor key;
- provenance report summary.

For intentionally stochastic functions, the package output must preserve the
seed or random-source metadata required to reproduce the run.

### 5. Input Immutability

Package APIs must not mutate caller-provided dictionaries, lists, grids,
profiles, candidates, episode results, or archive states unless the function is
documented as an in-place mutation API. The first package surface should avoid
in-place mutation entirely.

### 6. Trace Preservation

Generated candidates and archive insertions must preserve:

- parent ID or null seed origin;
- generator name;
- generator version or gate status;
- random seed when used;
- SLIP profile ID when used;
- validation status;
- rejected proposal count when generation filters candidates;
- lifecycle episode configuration;
- archive descriptor key and fitness components;
- provenance decision references when assets or licenses are involved.

### 7. Archive Correctness

The archive module may not reduce the research result to scalar top-k behavior:

- descriptor keys must be deterministic;
- elite replacement must happen only when a candidate beats the current elite
  for the same descriptor key under the documented comparator;
- archive coverage and QD score must remain reportable;
- scalar top-k output is a comparator/debug view, not the archive contract;
- human-calibrated readability descriptors remain blocked until human ratings
  exist.

### 8. Calibration Gates

The following states are blocked, not partially complete:

- final human-readability thresholds without `data/readability/manual_ratings.csv`;
- final archive descriptor thresholds that claim human calibration without
  reviewer data;
- real CuBFF adoption without real upstream or local snapshot artifacts;
- online reward-shaping promotion until it beats the frozen baseline under
  dynamic stress;
- release license metadata until the package exists and license decision
  records are explicit.

### 9. Boundary Invariants

The future package must satisfy these boundary rules:

- package runtime code does not import from `labs`;
- package tests do not import from `labs`;
- package tests do not mutate `sys.path` to reach lab modules;
- package imports do not write Stage 0 artifacts;
- package outputs remain JSON-serializable where the contract says they are
  report artifacts;
- package-promotion checks are rerun after package tests exist.

## Failure Propagation Rules

| Failure | Required propagation |
| --- | --- |
| Invalid grid | Reject parent, candidate, lifecycle simulation, archive insertion, and render packet until fresh validation passes. |
| Invalid SLIP profile | Reject profile-constrained generation and profile-weighted lifecycle use. Do not fall back to an implicit friendly profile unless the fallback is explicit in the result. |
| Generator returns invalid candidate | Keep candidate in rejection trace only; do not score it as a lifecycle or archive candidate. |
| Lifecycle emits non-finite state | Reject episode; archive may not derive descriptor or fitness from it. |
| Archive descriptor uses missing human ratings | Block human-calibrated descriptor claim; use only non-human descriptors. |
| Provenance report fails | Block package promotion even if package tests pass. |
| Package root absent | Do not run package tests or claim package readiness. Continue research-only gates. |

## Required Future Package Test Order

The future package implementation should execute tests in this order:

1. Scaffold import-surface tests.
2. Genome schema and semantic validation tests.
3. Generation tests that call the package genome validator.
4. Lifecycle tests that reject invalid grids through the package genome
   validator before simulation.
5. Archive tests that validate candidates through the package genome validator
   before insertion.
6. Provenance tests and package-promotion rerun.
7. Human-readability and release-compliance gates only after their blocked
   fixtures exist.

## Evidence Required Before Package Promotion

- all 50 seed grids accepted through package imports;
- all 200 invalid counterexamples rejected through package imports;
- constrained WFC-style generator package path reproduces the 100/100 valid
  candidate gate or supersedes it with stricter evidence;
- SLIP-constrained generation preserves the 50/50 valid and aligned fixture
  status or supersedes it with stricter evidence;
- lifecycle comparator produces finite bounded episode summaries for the frozen
  scenarios;
- archive reproduces descriptor coverage, elite replacement, and QD-score
  evidence through package imports;
- provenance CI parses SPDX expressions and preserves included/reference-only
  distinction;
- package contains no lab imports, no package-test `sys.path` mutation, and no
  import-time artifact writes.

## Negative Checks

The formal dependency gate fails if:

- a downstream module accepts an invalid grid because a lab fixture happened to
  look visually plausible;
- a generator reports only successful candidates and drops rejected proposals
  without trace metadata;
- lifecycle clips non-finite or out-of-range values without reporting the
  correction;
- archive replacement becomes scalar top-k selection;
- package docs claim full WFC, CTM, CuBFF, NCA, or online-learning adoption
  beyond the tested contract;
- provenance accepts lowercase SPDX operators as equivalent to `AND`, `OR`, and
  `WITH`;
- package code or tests import from `labs`;
- the package is marked promotion-ready before the promotion gate is rerun.

## Future Verification Commands

These commands are valid now for this research artifact:

```powershell
python -m json.tool .\data\architecture\mecha_engine_formal_invariant_dependency_gate_stage0.json
Test-Path .\packages
rg -n "mecha_engine_formal_invariant_dependency_gate|research_formal_invariant_dependency_gate_no_package_code" .\research .\data
git diff --check
```

These commands become valid only after package implementation explicitly starts:

```powershell
python -B -m unittest discover -s .\packages\mecha_engine\tests -p "test_*.py"
rg -n "from labs|import labs|labs/|labs\\|sys\.path" .\packages\mecha_engine
python -B .\labs\package_promotion\package_promotion_gate.py --root . --output-dir .\data\package_promotion
```

## Decision

Adopt this formal invariant/dependency gate as the next package-handoff layer.
It converts the research plan and module gates into a single cross-module
admissibility rule:

```txt
No future package module may consume, promote, archive, render, or release a
state that has not passed the upstream invariant gate required by its input.
```

Next research step:

```txt
Use this gate when converting package contract obligations into concrete
package tests after the user explicitly starts package implementation.
```

## References

- `docs/01-brainstorming.md`
- `docs/02-research_plan.md`
- `research/grid_genome/grid_invariants.md`
- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `research/package_specs/mecha_engine_test_fixture_manifest.md`
- `data/architecture/mecha_engine_contract_traceability_matrix_stage0.json`
- `data/architecture/mecha_engine_test_fixture_manifest_stage0.json`
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12
- Python jsonschema validation docs: https://python-jsonschema.readthedocs.io/en/latest/validate/
- MAP-Elites paper: https://arxiv.org/abs/1504.04909
- Wave Function Collapse reference implementation: https://github.com/mxgmn/WaveFunctionCollapse
- SPDX license expressions: https://spdx.github.io/spdx-spec/v2.2.2/SPDX-license-expressions/
- SPDX License List: https://spdx.org/licenses/
