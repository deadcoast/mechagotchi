# mecha_engine Repair Module Promotion

Date: 2026-07-05

Status: `package_repair_module_promoted_contract_evidence`

## Purpose

Execute the first post-initial module promotion into
`packages/mecha_engine`: the wound-site learned repair surface, authorized
by decision record 0006 (which supersedes decision record 0004's deferral
of `repair`), against
`research/package_specs/mecha_engine_repair_interface_spec.md` and the
repair row of the contract traceability matrix. The user explicitly
authorized this scope step.

## What changed

`packages/mecha_engine/src/mecha_engine/repair/` implements the contracted
surface (stdlib-only, typed, no `labs` imports, no `sys.path` text,
validation through `mecha_engine.genome` only):

- `train.py` — `train_repair_model`: verbatim port of the lab's
  deterministic full-batch softmax training, all defaults kept (dropout
  rates 0.1/0.2/0.3/0.4, 150 epochs, learning rate 1.5, live-class weight
  3.0, rng seed 20260512), including the private training-time stochastic
  damage synthesizer (`_damage.py`) with identical RNG semantics and
  `removed_cells` reporting.
- `wound.py` — `repair_wound_sites`: wound sites default to the damage
  event's `metadata.removed_cells`; most-confident-first fill; the
  validity guard verbatim (validator-only signal, ascending-confidence
  site order, descending-probability alternatives with class-index
  tie-break, strict error-count reduction, bounded passes,
  `validity_guard_substitutions` metadata). Missing `removed_cells` raises
  `KeyError`, as in the lab.
- `blind.py` — `repair_blind`: the below-bar blind arm, exposed as an
  explicitly labelled benchmark comparator.
- `_features.py` / `_grids.py` — feature layout, softmax, matrix/grid
  conversion with the palette fallback table embedded privately (source:
  `labs/grid_genome/corpus_builder.py`; `mecha_engine.generation` keeps
  its equivalent private, so re-embedding matches the lifecycle-module
  precedent).
- The template-assisted attractor is NOT ported (decision record 0006):
  the module is structurally template-free.

Contract evidence:

- `packages/mecha_engine/tests/test_repair_contract.py` +
  `tests/helpers/repair_contract_driver.py` (29 tests through the package
  `src` surface in a subprocess): deterministic training, fills exactly
  the reported sites, guard-off reproduces the invalid adversarial refill
  while guard-on validates with unchanged live set, `target_template_used`
  false on every result, frozen `data/seed_grids` fixtures only.
- `labs/cellular_automata/test_package_repair_parity.py` (lab-side parity
  pin): bit-for-bit model-dict equality on the 40-grid training split;
  guard-on AND guard-off repair equality plus blind-arm equality over all
  10 held-out grids at the benchmark cycle-1 seeds; and the `mg_seed_046`
  five-cycle site-aware trajectory ending valid at final overlap 1.0.
- `packages/mecha_engine/tests/test_package_imports.py`: `repair` moved
  from the deferred list to the promoted import surface
  (`LATER_PROMOTED_MODULES`), with a new requirement that later-promoted
  modules carry contract tests.

Gate rederivations (test-first):

- `labs/package_promotion/test_package_promotion_gate.py`: the repair
  candidate must report `promotion_ready` (RED while the target was
  absent, GREEN after). Gate artifact regenerated:
  `promotion_ready_count` 3 → 4, `package_design_ready_count` → 1.
- `labs/architecture/mecha_engine_scaffold_verification_gate.py`: `repair`
  moved from `DEFERRED_MODULES` to a decision-record-cited
  `LATER_PROMOTED_MODULES`; required paths/import targets now include it;
  `promoted_modules` derives from contract-test existence over all package
  modules. Gate artifact regenerated: 9/9 checks, 6 promoted modules.

## Verification

```powershell
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
```

```txt
Ran 193 tests in 3.495s
OK
```

```powershell
python -B -m unittest discover -s labs/cellular_automata -p "test_*.py"   # Ran 30 tests ... OK (4 new parity tests)
python -B -m unittest discover -s labs/package_promotion -p "test_*.py"  # Ran 6 tests ... OK
python -B -m unittest discover -s labs/architecture -p "test_*.py"       # Ran 14 tests ... OK
python -B labs/package_promotion/package_promotion_gate.py               # promotion_ready_count: 4
python -B labs/architecture/mecha_engine_scaffold_verification_gate.py   # checks_passed: 9/9, promoted_module_count: 6
```

Boundary scan: `grep -rn "sys.path|import labs|from labs" packages/mecha_engine/`
→ zero matches.

## Deviations and notes

- No semantic deviations; the parity pins prove verbatim behavior.
  Cosmetic only: private helpers drop leading underscores inside private
  modules; `TOKENS` is a frozenset.
- mypy is not installed in this environment, so the ad-hoc type check did
  not run; the module is fully annotated.
- The engine-facing consequence from decision record 0006 stands: any
  future damage surface must report destroyed positions or repair
  degrades to the blind arm's measured below-bar quality.

## Decision

`repair` is the sixth promoted module. Remaining deferred modules
(`learning`, `render`, `storage`, `slip`) still require their own decision
records. Next research-side step: none for repair — the surface is
promoted with its blocker honestly derived; open work returns to the
human-input items (manual readability calibration) and the deferred-module
scope decisions.

## Sources

- `research/decision_records/0006-create-mecha-engine-repair-target.md`
- `research/package_specs/mecha_engine_repair_interface_spec.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `packages/mecha_engine/src/mecha_engine/repair/`
- `packages/mecha_engine/tests/test_repair_contract.py`
- `packages/mecha_engine/tests/helpers/repair_contract_driver.py`
- `packages/mecha_engine/tests/test_package_imports.py`
- `labs/cellular_automata/test_package_repair_parity.py`
- `labs/package_promotion/package_promotion_gate.py`
- `labs/architecture/mecha_engine_scaffold_verification_gate.py`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- `data/architecture/mecha_engine_scaffold_verification_gate_stage0.json`
- `research/experiment_reports/2026-07-04-ca-nca-wound-site-repair.md`
- `research/experiment_reports/2026-07-04-ca-nca-wound-site-validity-guard.md`
