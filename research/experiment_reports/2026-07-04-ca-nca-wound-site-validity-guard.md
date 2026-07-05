# Experiment Report: Wound-Site Repair Validity Guard

Date: 2026-07-04

## Objective

Close next step (a) of the wound-site repair report: the arm met the
assisted stability bar at 0.930769 overlap/agreement but with validity at
exactly 0.9 — one held-out grid (`mg_seed_046`) ended invalid because a
wrong-token refill disconnected the required body core. Since the
site-aware arm's residual error surface is pure token prediction, a
connectivity-aware token choice should close it without touching the
observability contract.

## Design

`repair_with_wound_sites` gains a `validity_guard` (default on): after the
most-confident-first fill, if the repaired grid fails the grid validator, a
bounded greedy hill-climb substitutes alternative live tokens at wound
sites — least-confident fill first (the most likely to be wrong),
alternative tokens in descending model probability with class-index
tie-break — accepting only substitutions that strictly reduce the
validation error count. The guard:

- consults only the target-free validator (`validate_grid`); no template,
  no destroyed tokens;
- never empties a wound site and never touches non-site cells, so the
  live-position invariant (overlap = agreement) is preserved;
- terminates deterministically (passes bounded by site count, strict
  improvement required);
- records its work in `metadata.validity_guard_substitutions`.

## Verification

RED (guard keyword does not exist; adversarial fixture from a probe —
refilling `mg_seed_001` wound (2,3)+(3,3) as expression cells disconnects
the required body core, exactly the `mg_seed_046` failure mode):

```powershell
python -B -m unittest test_ca_nca_growth_repair.CaNcaGrowthRepairTests.test_wound_site_validity_guard_recovers_from_invalid_refill
```

```txt
TypeError: repair_with_wound_sites() got an unexpected keyword argument 'validity_guard'
Ran 1 test in 0.002s
FAILED (errors=1)
```

GREEN (full lab suite after implementation):

```powershell
python -B -m unittest discover -s labs/cellular_automata -p "test_ca_nca_growth_repair.py"
```

```txt
Ran 22 tests in 2.324s
OK
```

Lab command (regenerates the artifact):

```powershell
python -B .\labs\cellular_automata\ca_nca_growth_repair.py --mode trained-repair --output-dir .\data\cellular_automata
```

Site-aware arm, held-out grids, 5 cycles at dropout 0.2:

| Metric | Before guard | After guard |
| --- | ---: | ---: |
| mean final overlap | 0.930769 | **0.938462** |
| mean final structural agreement | 0.930769 | **0.938462** |
| final validity rate | 0.9 | **1.0** |
| mean final lifecycle survival | 0.9 | **1.0** |

All other arms (no_repair, role_prior, trained, assisted) are byte-identical
to the previous artifact — the guard only activates on wound-site refills
that break an invariant.

## Findings

1. The guard fired exactly where diagnosed: `mg_seed_046`, cycle 2, where
   the unguarded refill produced "required body core is disconnected". Per-
   cycle metrics show cycles 2–5 move from `repair_overlap 0.923077,
   valid false` to `repair_overlap 1.0, valid true`.
2. The validator signal alone recovered the *correct* token: the guard has
   no access to the target, but the core-connectivity constraint identified
   the right substitution, so overlap rose along with validity. This is not
   guaranteed in general — the guard guarantees invariant repair, not token
   correctness — and the report and card state both numbers (guarded
   0.938462/1.0; unguarded 0.930769/0.9) so neither is overwritten.
3. The wound-site arm now meets the assisted stability bar with margin on
   all three criteria, still with no template and no destroyed-token
   memory. `site_aware_meets_assisted_stability_bar` stays `true`;
   `meets_assisted_stability_bar` (blind arm) stays `false`; the promotion
   gate output is unchanged.

## Decision

Adopt the validity guard as part of the wound-site repair surface; carry
its semantics (validator-only signal, sites never emptied, strict error
reduction, bounded and deterministic) into the repair interface spec
(`research/package_specs/mecha_engine_repair_interface_spec.md`). Full
sweep after the change: 691 tests across 12 labs + the package suite, all
green.

## Sources

- `labs/cellular_automata/ca_nca_growth_repair.py`
- `labs/cellular_automata/test_ca_nca_growth_repair.py`
- `data/cellular_automata/ca_nca_trained_repair_stage0.json`
- `data/cellular_automata/trained_repair_samples/`
- `research/experiment_reports/2026-07-04-ca-nca-wound-site-repair.md`
- `research/algorithm_cards/ca_nca_growth_repair.md`
- `research/package_specs/mecha_engine_repair_interface_spec.md`
