# mecha_engine Learning Module Promotion

Date: 2026-07-05

Status: `package_learning_module_promoted_contract_evidence`

## Purpose

Execute the eighth module promotion: the feedback micro-switchboard as
`mecha_engine.learning`, authorized by decision record 0009 (owner:
"propose 0009 --go" — proposal and go together), against
`research/package_specs/mecha_engine_learning_interface_spec.md` and the
Learning row of the traceability matrix. The promotion claim is bounded
by the stress learning benchmark's evidence: **wellbeing, not survival.**

## What changed

`packages/mecha_engine/src/mecha_engine/learning/` (ported by sub-agent
under a spec-first brief; orchestrator-verified): `decide` + `ACTIONS`
(verbatim `micro_switchboard.run_switchboard` port — thread math,
rounding, tie-breaks, decision dict identical) and `run_feedback_episode`
(the feedback lab's tick loop without the lab-only scenario machinery;
frozen arm resets reward histories per tick; miscalibration helper
verbatim; drives ONLY `mecha_engine.lifecycle` publics, preserving the
lifecycle contract that reward shaping never enters lifecycle state).
The bounded claim is in the module docstring; no survival claim appears
anywhere.

Contract evidence:

- `tests/test_learning_contract.py` + `helpers/learning_contract_driver.py`
  (18 subprocess tests, frozen fixtures): surface/signature pins, decide
  determinism and no-mutation, both-arm episode determinism,
  `reward_update_count` 48 vs 0, and the sheltered wellbeing pin computed
  in-driver — feedback 0.790524, frozen 0.750884, **delta exactly
  0.03964**, matching the original artifact; survival equality asserted
  explicitly as not-a-survival-claim.
- `labs/grid_genome/test_package_learning_parity.py` (5 tests): decide ==
  lab switchboard at every state of full replayed 48-tick trajectories
  (both arms); episode parity on all 13 shared fields including
  byte-for-byte history; the +0.03964 artifact delta; stress pins — 3
  stress-probed generated candidates, package episode == the benchmark's
  `_policy_episode` both arms.
- `tests/test_package_imports.py`: `learning` moved to
  `LATER_PROMOTED_MODULES` (DR 0009 cited); `render`/`storage`/`slip`
  stay deferred.

Gate rederivations (test-first, staged RED before the target existed):

- Promotion gate: new `learning_switchboard` candidate derives from the
  stress benchmark's own keys (`feedback_beats_frozen_need_balance ==
  true`, `lost_by_feedback_count == 0`). Finding recorded during the
  flip: the pre-existing `switchboard_feedback` candidate (the sheltered
  reward-shaping gate, cleared pre-v0.9) also targets `learning` and
  flipped `promotion_ready` when the directory appeared — the module
  deliberately has TWO evidence candidates, sheltered and stress.
  Artifact: `promotion_ready_count` 5 → 7 of 8 candidates,
  `package_design_ready_count` → 0.
- Scaffold gate: `learning` joins the DR-cited `LATER_PROMOTED_MODULES`
  (deferred list now `render`/`storage`/`slip`); 9/9 checks, 8 promoted
  modules, 235 package tests.

## Verification

```powershell
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"  # Ran 235 tests ... OK
python -B -m unittest discover -s labs/grid_genome -p "test_*.py"             # Ran 78 tests ... OK (5 parity)
python -B -m unittest discover -s labs/runtime_integration -p "test_*.py"     # Ran 24 tests ... OK
python -B -m unittest discover -s labs/architecture -p "test_*.py"            # Ran 14 tests ... OK
python -B -m unittest discover -s labs/package_promotion -p "test_*.py"       # Ran 6 tests ... OK
python -B labs/package_promotion/package_promotion_gate.py                    # promotion_ready_count: 7
python -B labs/architecture/mecha_engine_scaffold_verification_gate.py        # 9/9, promoted_module_count: 8
```

Boundary scan over `*.py`: zero matches. mypy unavailable in this
environment (module fully annotated).

## Decision

`learning` is the eighth promoted module, with the engine's measured
behavior story now layered and honest: **morphology decides survival
(evolution's domain); policy decides wellbeing (learning's domain).**
Remaining deferred modules: `render`, `storage`, `slip` — each requiring
its own decision record. A future survival-relevant learner requires new
evidence through the stress learning benchmark harness.

## Sources

- `research/decision_records/0009-create-mecha-engine-learning-target.md`
- `research/package_specs/mecha_engine_learning_interface_spec.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `packages/mecha_engine/src/mecha_engine/learning/`
- `packages/mecha_engine/tests/test_learning_contract.py`
- `packages/mecha_engine/tests/helpers/learning_contract_driver.py`
- `packages/mecha_engine/tests/test_package_imports.py`
- `labs/grid_genome/test_package_learning_parity.py`
- `research/experiment_reports/2026-07-05-stress-learning-benchmark.md`
- `data/runtime_integration/stress_learning_benchmark_stage0.json`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- `data/architecture/mecha_engine_scaffold_verification_gate_stage0.json`
