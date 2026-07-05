# Experiment Report: SLIP-Aware Repair Guard

Date: 2026-07-05

## Objective

Close the runtime integration seam: repair's validity guard consulted only
the genome validator, so a destroyed profile-required organ could be
refilled as the wrong organ — a validator-valid creature that
`mecha_engine.lifecycle` refuses to simulate (alignment retention 0.9167
in the first composed run). Extend the guard, lab-first and mirrored into
the promoted module, to accept the active SLIP profile and hill-climb on
the combined error count (validator errors + alignment errors).

## Contract change, stated precisely

- New optional parameter on both surfaces:
  `repair_with_wound_sites(..., slip_profile=None)` (lab) and
  `repair_wound_sites(..., slip_profile=None)` (package).
- **No template enters.** The SLIP profile is the engine-native
  constraint set (palette legality, required organ roles, mass bounds)
  that applies to every creature of its kind; it carries nothing about
  the individual's silhouette or destroyed tokens.
- **Baseline continuity proven**: with the default `None`, behavior is
  bit-identical — the trained-repair benchmark artifact regenerated
  byte-identical (checked against git HEAD before any doc changed).
- Honest consequence: with a profile, the guard repairs the *constraint*
  ("an expression cell exists"), not the individual's exact tokens — the
  restored organ may occupy a different wound site than the destroyed
  one. The runtime run below shows this as a small token-restoration dip
  in exchange for a simulatable creature.
- Package-side alignment comes from a new private
  `mecha_engine/repair/_slip.py`, the same verbatim port (identical rule
  set and error strings) that `lifecycle` and `generation` each carry —
  the documented factoring while a full `mecha_engine.slip` module stays
  deferred.

## Verification

RED (lab, adversarial fixture: mg_seed_001's only expression cell at
(5,3) destroyed, model biased to refill "B"):

```powershell
python -B -m unittest test_ca_nca_growth_repair.CaNcaGrowthRepairTests.test_wound_site_guard_can_restore_slip_alignment
# TypeError: unexpected keyword argument 'slip_profile' -> FAILED (errors=1)
```

GREEN (all repair-adjacent suites after lab + package implementation):

```powershell
python -B -m unittest discover -s labs/cellular_automata -p "test_*.py"      # Ran 32 tests ... OK
python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py" # Ran 196 tests ... OK
```

New pins: the lab test above (profile-unaware repair stays valid but
unaligned; profile-aware repair is valid AND aligned, >= 1 substitution,
deterministic); the contract driver's `slip_aware_guard` probe using
`mecha_engine.lifecycle.initial_state` as the public cross-module
alignment oracle (+3 contract tests); a lab-side slip-aware parity case
(lab vs package bit-identical with the profile over all 10 held-out
grids).

Baseline continuity:

```powershell
python -B .\labs\cellular_automata\ca_nca_growth_repair.py --mode trained-repair --output-dir .\data\cellular_automata
# artifact byte-identical to HEAD (verified programmatically)
```

Runtime loop rerun (the seam's own gate; the runtime now hands the active
profile to repair):

```powershell
python -B .\labs\runtime_integration\mecha_engine_runtime_loop.py
```

```txt
"slip_alignment_retention_rate": 1.0, "archived_run_count": 12,
"guard_substitution_total": 1, "mean_token_restoration": 0.965368,
"archive": {"filled_niches": 10, "qd_score": 9.29076}
"decision": "runtime_loop_composed"
```

## Findings

1. The guard fired exactly once across the full 12-creature run — on
   precisely the creature that previously became unsimulatable — and
   restored SLIP alignment: retention 0.9167 → **1.0**, archived runs
   11 → **12**, decision honestly flips to `runtime_loop_composed`.
2. The token-restoration mean dipped 0.9729 → 0.9654: the guard placed
   the restored expression cell at a different wound site than the
   original. Constraint repair, not template repair — exactly the
   documented semantics.
3. The runtime lab's go/no-go gate ("no `runtime` package target until
   retention is 1.0") is now satisfied on the evidence side; proposing
   the target remains a decision-record-gated owner step.

## Decision

Adopt the SLIP-aware guard on both surfaces; interface spec and
traceability matrix updated in the same change. Next engine step:
multi-generation evolution over archive elites in the runtime lab; a
`runtime` package target proposal (decision record 0008 candidate) is now
evidence-ready whenever the owner wants it.

## Sources

- `labs/cellular_automata/ca_nca_growth_repair.py`
- `labs/cellular_automata/test_ca_nca_growth_repair.py`
- `labs/cellular_automata/test_package_repair_parity.py`
- `packages/mecha_engine/src/mecha_engine/repair/wound.py`
- `packages/mecha_engine/src/mecha_engine/repair/_slip.py`
- `packages/mecha_engine/tests/test_repair_contract.py`
- `packages/mecha_engine/tests/helpers/repair_contract_driver.py`
- `labs/runtime_integration/mecha_engine_runtime_loop.py`
- `data/runtime_integration/mecha_engine_runtime_loop_stage0.json`
- `research/package_specs/mecha_engine_repair_interface_spec.md`
- `research/experiment_reports/2026-07-05-mecha-engine-runtime-loop.md`
- `research/algorithm_cards/ca_nca_growth_repair.md`
- `research/algorithm_cards/mecha_engine_runtime_loop.md`
