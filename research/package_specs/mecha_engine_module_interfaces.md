# Mecha Engine Module Interface Specs

Date: 2026-05-12

## Status

Research interface specification. This document does not create
`packages/mecha_engine` and does not promote lab code.

## Boundary Rule

The future package must expose stable engine contracts, not lab scripts. Lab
modules can inform the interface, but package code must be created only after a
package-scaffold decision record and a satisfied promotion gate.

The package should use a `src` style import boundary when it is created, so
tests exercise the installed package surface instead of importing accidental
repository-root files. Package metadata should be represented through a modern
`pyproject.toml` with explicit project metadata.

## Shared Data Contracts

### Grid Genome

Canonical schema:

- `research/grid_genome/grid_genome.schema.json`
- Draft: JSON Schema 2020-12
- Schema version: `0.1.0`

Required top-level fields:

- `grid_id`
- `schema_version`
- `grid_size`
- `cells`
- `organs`
- `palette`
- `mutation`

Required validation outcomes:

- `ok: bool`
- `errors: list[str]`

### Lifecycle Episode

Required summary fields:

- `survival_ticks`
- `alive`
- `death_cause`
- `need_balance`
- `recovery_events`
- `action_counts`
- `final_state`
- `history`

### Archive Candidate

Required fields:

- `grid`
- `descriptor`
- `fitness`
- `fitness_components`
- `validation`
- `provenance`

### Provenance Result

Required fields:

- `ok`
- `checks`
- `parsed_expressions`
- `included_hashes`
- `decision_record_gate`
- `errors`

## Module Specs

### `genome`

Purpose:

- Own the semantic grid-genome contract.
- Validate grid structure, organ integrity, palette references, mutation
  bounds, connectedness, sensor presence, and animation readiness.

Inputs:

- Grid genome dictionaries loaded from JSON.
- Optional schema version selector.

Outputs:

- `ValidationResult(ok: bool, errors: list[str])`
- Normalized grid payloads after later package implementation.

Required public surface:

- `validate_grid(grid) -> ValidationResult`
- `validate_grid_file(path) -> ValidationResult`
- `grid_signature(grid) -> str`
- `render_packet_from_grid(grid, state=None) -> dict`

Hard gates:

- Must accept the 50 seed grids.
- Must reject the 200 invalid counterexamples.
- Must preserve JSON Schema 2020-12 compatibility.
- Must not mutate input payloads during validation.

Research sources:

- `labs/grid_genome/validator.py`
- `research/grid_genome/grid_invariants.md`
- `research/experiment_reports/2026-05-12-grid-validator-baseline.md`

### `generation`

Purpose:

- Produce valid child grid genomes from seed or parent grids.
- Treat raw Markov output as a proposal source and constraint stabilization as
  the default MVP path.

Inputs:

- Seed grid corpus.
- Parent grid genome.
- Optional SLIP profile.
- RNG seed.
- Generator configuration.

Outputs:

- Candidate grid genome.
- Generation trace with parent, seed, constraints, rejected attempts, and final
  validation status.

Required public surface:

- `train_generation_model(seed_grids) -> GenerationModel`
- `generate_candidate(parent_grid, model, slip_profile=None, rng_seed=None) -> dict`
- `generate_batch(seed_grids, count, slip_profile=None, rng_seed=None) -> list[dict]`
- `explain_generation(candidate) -> dict`

Hard gates:

- Candidate output must pass `genome.validate_grid`.
- SLIP-constrained generation must pass the SLIP alignment gate when a profile
  is supplied.
- Generation traces must preserve enough data for lineage and provenance.
- Raw Markov generation must not be the sole production generator.

Research sources:

- `labs/grid_genome/constrained_generator.py`
- `research/experiment_reports/2026-05-12-constrained-wfc-style-generator.md`
- `research/experiment_reports/2026-05-12-slip-constraint-baseline.md`

### `lifecycle`

Purpose:

- Simulate bounded companion state over ticks.
- Convert feed, play, sleep, idle, and mutation actions into measurable survival
  and need-balance outcomes.

Inputs:

- Valid grid genome.
- Optional SLIP profile.
- Tick horizon.
- Policy or explicit action stream.
- RNG seed.

Outputs:

- Lifecycle episode summary.
- Per-tick history.
- Reward observations for lab-only switchboard feedback.

Required public surface:

- `initial_state(grid, slip_profile=None) -> dict`
- `advance_tick(state, action) -> dict`
- `run_episode(grid, slip_profile=None, policy=None, actions=None, ticks=72, rng_seed=None) -> dict`
- `reward_for_transition(previous_state, next_state, action) -> float`

Hard gates:

- Invalid grids must fail before simulation.
- State variables must remain bounded.
- Death causes must be explicit.
- Reward observations can feed research learners, but online reward shaping
  remains lab-only until it beats the frozen baseline.

Research sources:

- `labs/lifecycle_sim/lifecycle_sim.py`
- `research/algorithm_cards/lifecycle_simulator.md`
- `research/experiment_reports/2026-05-12-lifecycle-simulator-baseline.md`
- `research/experiment_reports/2026-05-12-switchboard-lifecycle-feedback.md`

### `archive`

Purpose:

- Preserve diverse high-performing companion families rather than one scalar
  winner.
- Store elites by behavior descriptor and expose lineage/archive metrics.

Inputs:

- Valid candidate grids.
- Readability score.
- Lifecycle episode summary.
- SLIP alignment result.
- Mutation stability metrics.

Outputs:

- Archive state.
- Elite entries.
- Descriptor vector.
- Fitness components.
- Coverage, QD score, best fitness, and mean elite fitness.

Required public surface:

- `descriptor_for_candidate(candidate, metrics) -> tuple[int, ...]`
- `score_candidate(candidate, metrics) -> dict`
- `insert_candidate(archive, candidate, score, descriptor) -> dict`
- `build_archive(candidates, metrics_by_grid_id) -> dict`
- `archive_summary(archive) -> dict`

Hard gates:

- Archive insertion must require valid grids.
- Descriptor calculation must include lifecycle and readability once available.
- Scalar top-k must not replace the archive.
- Manual readability ratings must be incorporated before final descriptor
  thresholds are locked.

Research sources:

- `labs/map_elites_archive/extended_descriptors.py`
- `research/algorithm_cards/map_elites_extended_descriptors.md`
- `research/experiment_reports/2026-05-12-map-elites-extended-descriptors.md`

### `provenance`

Purpose:

- Keep source, license, attribution, hash, and decision-record checks attached
  to assets and package artifacts.
- Fail risky included assets before release or package promotion.

Inputs:

- Provenance ledger.
- Included file paths.
- SPDX license expressions.
- Decision-record references.

Outputs:

- Validation result.
- CI report.
- Attribution manifest.
- Parsed license-expression details.

Required public surface:

- `parse_spdx_expression(expression) -> dict`
- `validate_ledger(ledger, repo_root) -> dict`
- `build_ci_report(ledger, repo_root) -> dict`
- `generate_attribution_manifest(ledger) -> dict`
- `hash_included_path(path) -> dict`

Hard gates:

- SPDX operators must be case-sensitive.
- Included assets must have hashes.
- Included share-alike or copyleft assets require decision-record references.
- Provenance checks must run before package promotion.

Research sources:

- `labs/asset_pipeline/provenance_ledger.py`
- `research/algorithm_cards/provenance_ci_spdx.md`
- `research/experiment_reports/2026-05-12-provenance-ci-spdx-parser.md`

## Cross-Module MVP Flow

```txt
genome.validate_grid(seed_or_parent)
  -> generation.generate_candidate(...)
  -> genome.validate_grid(candidate)
  -> lifecycle.run_episode(candidate, ...)
  -> archive.score_candidate(candidate, metrics)
  -> archive.insert_candidate(...)
  -> provenance.build_ci_report(...)
  -> render_packet_from_grid(...)
```

## Non-Goals

- No `packages/mecha_engine` scaffold in this step.
- No package metadata file in this step.
- No trained NCA promotion.
- No production online learner.
- No workshop/editor implementation.

## External Standards

- Python Packaging User Guide, `pyproject.toml` specification:
  https://packaging.python.org/en/latest/specifications/pyproject-toml/
- Python Packaging User Guide, `src` layout discussion:
  https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- JSON Schema Draft 2020-12:
  https://json-schema.org/draft/2020-12
- SPDX License Expressions:
  https://spdx.github.io/spdx-spec/v2.2.2/SPDX-license-expressions/

