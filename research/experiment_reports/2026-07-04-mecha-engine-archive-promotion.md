# mecha_engine Archive Module Promotion

Date: 2026-07-04

Status: `package_archive_module_promoted_contract_evidence`

## Purpose

Execute the fourth module promotion into `packages/mecha_engine`, per the
traceability matrix order (genome → generation → lifecycle → **archive** →
provenance), against
`research/package_specs/mecha_engine_module_interfaces.md` and
`research/package_specs/mecha_engine_archive_contract_gate.md`.

## What changed

`packages/mecha_engine/src/mecha_engine/archive/` implements the full
contracted surface, self-contained (stdlib plus the already-promoted
`mecha_engine.genome` and `mecha_engine.lifecycle` modules, no `labs`
imports, no artifact writes, typed):

- `descriptors.py` — `descriptor_for_candidate`: deterministic integer
  descriptor tuples in two modes (keyword-only selector, default
  `extended`): the baseline 3D option (body mass, sensor count, symmetry)
  and the calibrated extended 7D Stage 0 descriptor (adds readability,
  lifecycle survival, mutation stability, behavior neediness). The
  provisional Stage 0 bin edges are ported verbatim and explicitly marked
  unlocked (`final_descriptor_thresholds_locked: false`) pending manual
  readability ratings.
- `scoring.py` — `score_candidate`: verbatim port of the calibrated Stage 0
  extended fitness (survival 0.28, readability 0.24, validity 0.18, bond
  0.12, mutation stability 0.10, SLIP alignment 0.08; aggregate computed
  from unrounded components, then clamped and rounded exactly as the lab
  does). Returns fitness, components, validation, readability (proxy,
  manual-rating status visible), lifecycle, slip_alignment, provenance,
  and per-axis descriptor metrics; invalid candidates are scored as
  failures for reports.
- `store.py` — `insert_candidate` / `build_archive` / `archive_summary`:
  MAP-Elites niche mechanics with the pinned elite rule (empty niche
  accepts the first valid candidate; replacement only on strictly higher
  fitness; equal fitness keeps the incumbent — deterministic tie
  handling), immutably returned archives (a losing candidate leaves the
  previous archive intact by construction), an audit `insertion_log` for
  every decision, blocked/skipped candidate accounting, and summaries
  reporting descriptor metadata, occupied niches with theoretical-coverage
  context (`descriptor_bin_spread` per axis), best/mean-elite fitness, QD
  score, and the readability calibration status. Candidate grids are
  re-validated through `mecha_engine.genome.validate_grid` at insertion:
  invalid candidates never become elites.
- `_metrics.py` — documented metric factoring (the interface spec scopes
  readability, the lifecycle episode summary, the SLIP alignment result,
  and mutation caps as archive *inputs* via the per-candidate `metrics`
  bundle, so no proxy-readability scorer is ported; missing metric inputs
  are rejected with explicit `missing metric input: ...` errors). The
  calibrated grid-derived Stage 0 arithmetic is preserved verbatim:
  morphology axes, cap-normalized mutation stability
  (`1 - mean(rate/cap)` against SLIP `*_max` caps or the default generator
  vector), the grid-derived behavior-neediness term with the SLIP prior as
  a shift only, and the morphology-derived lifecycle stress probe
  (`clamp(body_mass/16 + (1 - symmetry)·0.65 - sensor_count·0.08)`)
  simulated through `mecha_engine.lifecycle` switchboard episodes when the
  bundle carries no precomputed lifecycle summary (both the reduced and
  full episode-summary shapes are accepted and resolve identically).

Package tests (`test_archive_contract.py`, 40 tests, same subprocess
mechanics as genome/generation/lifecycle) prove the contract gate:
deterministic 7D/3D integer descriptor tuples with metadata (names,
cardinalities, 78125/125 total niches), the provisional readability bin
edges, the stress-probe survival axis pinned against a direct
`mecha_engine.lifecycle` oracle, the pinned fitness weights and bounded
components, empty-niche insertion, strictly-higher-fitness replacement
with incumbent-keeping ties and audited decisions, blocked/skipped
accounting, summary-metric definitions, explicit missing-metric
rejection, no input mutation, determinism, JSON-serializability, the
scalar-top-k separation probe (a weaker unique-niche candidate stays an
elite that ranked top-k selection would drop; no ranked/top-k surface
exists), and the full 200-grid invalid-corpus sweep (all scored as
failures, zero become elites). Lab-side parity
(`labs/map_elites_archive/test_package_archive_parity.py`, 9 tests) pins
the package against the calibrated research archive: identical per-candidate
descriptors and scores, identical elites per niche (grid_id, fitness,
descriptor values, per-axis metrics, components), identical summary
metrics, and baseline-mode niche-geometry parity with the legacy 3-axis
archive.

Documented spec resolutions: `build_archive` input candidates are mappings
with `grid` (plus optional `provenance`); the six-field archive-candidate
data contract (grid, descriptor, fitness, fitness_components, validation,
provenance) is satisfied by the stored elite entries the archive builds
from candidate + score + descriptor. The extended rows of the contract
gate's Stage 0 table were intentionally updated by the descriptor-axis
calibration report (occupied 29 → 83, best fitness 0.979592 → 0.972366,
QD 27.773545 → 72.069987); parity pins the current
`data/archives/map_elites_extended_stage0.json` values through the
package. The baseline scalar-top-k comparator (top-20 by the legacy
scalar fitness reaching 7 of the package archive's 24 baseline niches)
runs test-side with the lab's legacy `score_grid`, since the legacy
fitness function is not part of the promoted surface — the spec's fitness
acceptance lists only the extended components. The package additionally
blocks invalid candidates from elite status (the lab lets fitness carry
validity alone); the Stage 0 corpus is fully valid, so parity is
unaffected and blocked/skipped counts are asserted zero.

## Result

- Calibrated Stage 0 extended archive reproduced exactly through the
  package surface: 83 occupied niches, coverage 0.001062, best fitness
  0.972366, mean elite fitness 0.868313, QD score 72.069987, bin spread
  {body_mass 3, sensor_count 4, symmetry 4, readability 3,
  lifecycle_survival 2, mutation_stability 5, behavior_neediness 2} on the
  160-candidate corpus (seed 20260512, 24 lifecycle ticks).
- Baseline 3D occupancy parity with the legacy archive: 24 occupied
  niches, coverage 0.192 on the 200-candidate corpus (seed 818); scalar
  top-20 reaches only 7 niches — comparator-only, reproduced test-side.
- Invalid candidates cannot become elites: 200/200 invalid grids scored as
  failures and blocked at insertion; every elite passes
  `mecha_engine.genome.validate_grid`.
- Missing metric inputs (readability, SLIP alignment with a profile) are
  rejected explicitly; `build_archive` counts them as skipped without
  aborting the run.
- Manual readability stays an explicit open calibration gate: proxy-only
  status in every archive and summary, thresholds unlocked, no
  human-calibration claim anywhere in the surface.
- Boundary scan over `packages/mecha_engine`: zero matches.

```powershell
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
# Ran 123 tests - OK  (was 83; +40 archive contract)
```

Scaffold verification gate: `promoted_modules` now
`["genome", "generation", "lifecycle", "archive"]`, 9/9 checks pass,
artifact regenerated. Full 12-lab sweep: 511 lab tests (was 502; +9
archive parity) + 123 package tests, all green. The package-promotion gate
rerun (`data/package_promotion`) is deferred to the orchestrated
promotion-gate step and not rerun here.

## Decision

`mecha_engine.archive` is promoted with contract evidence. Scalar top-k
remains a comparator only, final descriptor thresholds remain unlocked,
and manual readability ratings remain required before threshold lock per
the contract gate. Next module in the traceability order: `provenance`.

## Verification

```powershell
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
python -B labs/map_elites_archive/test_package_archive_parity.py
python -B -m unittest discover -s labs/map_elites_archive -p "test_*.py"
python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
python -B -m unittest discover -s labs/lifecycle_sim -p "test_*.py"
python -B labs/architecture/mecha_engine_scaffold_verification_gate.py
python -m json.tool data/architecture/mecha_engine_scaffold_verification_gate_stage0.json
```

## Sources

- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/package_specs/mecha_engine_archive_contract_gate.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `research/package_specs/mecha_engine_property_negative_test_strategy.md`
- `data/architecture/mecha_engine_archive_contract_gate_stage0.json`
- `data/archives/map_elites_extended_stage0.json`
- `data/archives/map_elites_stage0.json`
- `labs/map_elites_archive/extended_descriptors.py`
- `labs/grid_genome/darwin_archive.py`
- `labs/readability_benchmark/readability_benchmark.py`
- `packages/mecha_engine/src/mecha_engine/archive/`
- `packages/mecha_engine/tests/test_archive_contract.py`
- `labs/map_elites_archive/test_package_archive_parity.py`
- `research/experiment_reports/2026-07-04-descriptor-axis-calibration.md`
- `research/experiment_reports/2026-07-04-mecha-engine-lifecycle-promotion.md`
