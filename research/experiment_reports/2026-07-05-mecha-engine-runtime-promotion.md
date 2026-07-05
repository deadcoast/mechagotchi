# mecha_engine Runtime Module Promotion

Date: 2026-07-05

Status: `package_runtime_module_promoted_contract_evidence`

## Purpose

Execute the seventh module promotion into `packages/mecha_engine`: the
composed-engine runtime surface, authorized by decision record 0008
(proposed and accepted by the owner the same day), against
`research/package_specs/mecha_engine_runtime_interface_spec.md` and the
Runtime row of the contract traceability matrix.

## What changed

`packages/mecha_engine/src/mecha_engine/runtime/` (ported by sub-agent
under a spec-first brief; verified by the orchestrator) implements the
contracted surface — stdlib-only, typed, no `labs` imports, no `sys.path`,
public cross-module imports only:

- `live.py` — `live_cycle`: one creature's repeated damage/repair/episode
  life, verbatim lab cycle semantics (seed arithmetic, per-cycle grid-id
  reassignment, SLIP-aware `repair_wound_sites`, unaligned break,
  restoration/episode digests). Optional injected `damage_events` (one
  cycle per event; empty `removed_cells` is a legal no-op; reported sites
  recomputed live-before/empty-after so an already-empty request can
  never grow the creature; malformed events raise).
- `evolve.py` — `evolve(seed_grids, slip_profile, generation_model,
  repair_model, *, readability_scorer, ...) -> (archive, report)`:
  verbatim lab evolution algorithm — generation-0 parents from the
  profile-aligned seed pool, later generations from archive elites sorted
  by niche key, identical metrics bundles, insert-event mapping, summary
  and decision derivations with the exact reason strings.
- `_slip.py`, `_grids.py`, `_damage.py` — private ports per the
  documented per-module factoring (the third `_grids` copy was required
  because `_damage` depends on it and cross-module private imports are
  boundary-illegal; documented in its header).

Contract evidence:

- `tests/test_runtime_contract.py` + `helpers/runtime_contract_driver.py`
  (21 subprocess tests over frozen `data/` fixtures): evolve and
  live_cycle determinism, no input mutation, generation-1
  `parent_source == "archive_elites"`, injected-events path incl. the
  zero-site no-op, readability manual-rating status visible on every
  score (`report["readability"]["manual_rating_statuses"] ==
  ["not_collected"]`), JSON serializability, signature pins.
- `labs/runtime_integration/test_package_runtime_parity.py` (6 tests):
  lab evolution loop vs package `evolve` with the lab's proxy readability
  injected — generations lists equal, summary equal, decision
  status+reason equal; `live_cycle` pinned against all three generation-0
  lab creatures' cycle records. Documented exclusions: the report
  envelope (lab_id, dates, ledger-only keys) and
  `decision.adoption` (`"package_runtime_surface"` vs the lab's
  `"lab_only_runtime_evidence"`, which would be false in a package).
- `tests/test_package_imports.py`: `runtime` joined
  `LATER_PROMOTED_MODULES`.

Gate rederivations (test-first, staged RED before the target existed):

- Promotion gate: new `runtime_loop` candidate whose thresholds derive
  from the evolution artifact's summary (validity, alignment retention,
  position restoration all >= 1.0). Artifact: `promotion_ready_count`
  4 → 5 of 7 candidates.
- Scaffold verification gate: `runtime` joined the DR-cited
  `LATER_PROMOTED_MODULES`; 9/9 checks, 7 promoted modules, 217
  import-suite tests.

## Verification

```powershell
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"   # Ran 217 tests ... OK
python -B -m unittest discover -s labs/runtime_integration -p "test_*.py"      # Ran 15 tests ... OK (6 parity)
python -B -m unittest discover -s labs/architecture -p "test_*.py"             # Ran 14 tests ... OK
python -B -m unittest discover -s labs/package_promotion -p "test_*.py"        # Ran 6 tests ... OK
python -B labs/package_promotion/package_promotion_gate.py                     # promotion_ready_count: 5
python -B labs/architecture/mecha_engine_scaffold_verification_gate.py         # 9/9, promoted_module_count: 7
```

Boundary scan over `*.py`: zero matches (one pre-existing self-referential
prose line in the package README mentions the forbidden string by name;
the executable gate scans code and passes).

## Deviations and notes

- No semantic deviations from the lab algorithm (parity pins prove it);
  envelope/adoption differences are enumerated above and in the parity
  docstring.
- The spec's manual-rating-status visibility is satisfied at the report
  level (aggregated statuses) because per-creature score digests stay
  lab-verbatim `{fitness, components}` for parity — the documented
  resolution of a mild spec tension.
- mypy unavailable in this environment; module fully annotated.
- Known non-goal carried forward: lineage-counter accumulation through
  repair (parity-reviewed follow-up; ancestry truth is the parent-id
  chain).

## Decision

`runtime` is the seventh promoted module — the engine now has one
supported entry point (`live_cycle` + `evolve`) encoding the five
integration lessons the runtime lab discovered executable-first. The lab
remains the research harness. Remaining deferred modules (`learning`,
`render`, `storage`, `slip`) each still require their own decision
records.

## Sources

- `research/decision_records/0008-propose-mecha-engine-runtime-target.md`
- `research/package_specs/mecha_engine_runtime_interface_spec.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `packages/mecha_engine/src/mecha_engine/runtime/`
- `packages/mecha_engine/tests/test_runtime_contract.py`
- `packages/mecha_engine/tests/helpers/runtime_contract_driver.py`
- `packages/mecha_engine/tests/test_package_imports.py`
- `labs/runtime_integration/test_package_runtime_parity.py`
- `labs/package_promotion/package_promotion_gate.py`
- `labs/architecture/mecha_engine_scaffold_verification_gate.py`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- `data/architecture/mecha_engine_scaffold_verification_gate_stage0.json`
- `research/experiment_reports/2026-07-05-mecha-engine-evolution-loop.md`
