# Experiment Report: CA/NCA Wound-Site Learned Repair

Date: 2026-07-04

## Objective

Continue the `lab_only_target_template_assisted` blocker work from the
trained-neighborhood-repair report: the blind gradient-trained rule measured
0.862546 final overlap and 0.631871 structural agreement against the
0.9/0.9/0.9 assisted stability bar. Decompose where that gap comes from and
test whether an observability assumption the engine natively satisfies —
damage events reporting which cells they destroyed — closes it without any
target template.

## Diagnosis

Decomposing the blind trained arm's final grids against their held-out
targets (union of live positions, pooled over the 10 targets):

- spurious fills (live in candidate, empty in target): 49 cells, 27.2% of
  the union — the dominant loss
- wrong tokens (both live, different token): 7 cells, 3.9%
- missing cells (live in target, empty in candidate): 11 cells, 6.1%

Even a zero-overgrowth version of the blind rule would only reach ~0.86
agreement, so the bar requires eliminating spurious fills *and* filling more
accurately. The companion context-conditioning ablation
(`2026-07-04-ca-nca-repair-context-ablation.md`) shows corpus-retrieval
conditioning cannot do this — it degrades the rule, and the exemplar ceiling
(0.785 mean agreement) bounds the whole retrieved-template family below the
bar.

## The wound-site arm

`apply_stochastic_damage` now records the positions it destroys
(`metadata.removed_cells`: live before, empty after — the anchor reseed only
promotes a surviving body cell, so the list is exact). The new
`repair_with_wound_sites` refills exactly those reported positions,
most-confident-first, with tokens predicted by the *same* trained softmax
model the blind arm uses. Observability contract: the arm sees destroyed
positions, never destroyed tokens, never a template. Restricting refill to
reported sites removes overgrowth by construction — the live position set
provably stays equal to the target's across cycles — so all residual error
is token prediction, and one-sided overlap equals two-sided structural
agreement identically.

An arm that also remembered the destroyed *tokens* would trivialise the
benchmark (undo, not repair); that is why the token side stays learned and
the verdict is recorded under its own threshold key
(`site_aware_meets_assisted_stability_bar`) instead of redefining the blind
arm's `meets_assisted_stability_bar`, which honestly remains `false`.

## Verification

RED (new assertions before implementation):

```powershell
python -B -m unittest discover -s labs/cellular_automata -p "test_ca_nca_growth_repair.py"
```

```txt
ERROR: test_apply_stochastic_damage_records_removed_cell_positions (...)
ERROR: test_repair_with_wound_sites_fills_exactly_the_damage_sites (...)
FAIL: test_run_trained_repair_benchmark_compares_all_arms_on_heldout_grids (...)
AssertionError: Items in the first set but not the second:
'site_aware'
FAIL: test_write_trained_repair_artifacts_creates_report_and_samples (...)
AssertionError: 10 != 8
Ran 21 tests in 2.112s
FAILED (failures=2, errors=2)
```

GREEN (same command after implementation):

```txt
Ran 21 tests in 2.134s
OK
```

Lab command (regenerates the artifact; ~6 s):

```powershell
python -B .\labs\cellular_automata\ca_nca_growth_repair.py --mode trained-repair --output-dir .\data\cellular_automata
```

Result (held-out grids `mg_seed_041`..`mg_seed_050`, 5 cycles at dropout
0.2; all previously published arms byte-identical — baseline continuity):

| Arm | Final overlap | Structural agreement | Validity | Lifecycle survival |
| --- | ---: | ---: | ---: | ---: |
| no_repair | 0.231776 | 0.231776 | 0.1 | 0.1 |
| role_prior | 0.900458 | 0.532016 | 1.0 | 1.0 |
| trained (blind) | 0.862546 | 0.631871 | 1.0 | 1.0 |
| **site_aware** | **0.930769** | **0.930769** | **0.9** | 0.9 |
| assisted | 1.0 | 1.0 | 1.0 | 1.0 |

Gate rerun:

```powershell
python -B -m unittest discover -s labs/package_promotion -p "test_*.py"   # Ran 6 tests ... OK
python -B .\labs\package_promotion\package_promotion_gate.py
```

```txt
"package_design_ready_count": 2,
"hold_research_only_count": 0
```

## Findings

1. The wound-site arm meets all three assisted stability bars
   (overlap 0.930769 >= 0.9, agreement 0.930769 >= 0.9, validity 0.9 >= 0.9)
   on held-out grids, with no target template. Its first-cycle repair
   overlap is 0.962088 vs the blind arm's 0.939011, and it beats the blind
   arm by +0.298898 structural agreement.
2. The result is thin on validity: exactly 9 of 10 finals validate. The
   failure is `mg_seed_046` — "required body core is disconnected" — where a
   wrong-token refill split the core organ. Token prediction, not placement,
   is now the entire residual error surface (site-aware overlap and
   agreement are equal by construction).
3. The artifact's decision gains a new tier: with the blind bar unmet but
   the site-aware bar met, `decision.status =
   "wound_signal_repair_meets_bar"` and
   `decision.thresholds.site_aware_meets_assisted_stability_bar = true`,
   while `meets_assisted_stability_bar` stays `false`.
4. The promotion gate's `lab_only_target_template_assisted` blocker now
   derives from the site-aware key: the blocker's factual basis was "only
   template-assisted repair reaches stability", and the wound-site arm
   refutes exactly that under an engine-native observability (damage events
   know what they destroyed). The `ca_nca_repair` candidate moves from
   `hold_research_only` to `ready_for_package_design`; it remains
   unpromotable (`target_package_absent`) until a repair package target is
   deliberately created, which stays a decision-record-gated scope step.

## Decision

Status: `wound_signal_repair_meets_bar`.

Adopt the wound-site arm as the lab's learned-repair candidate surface.
Keep the blind arm and its unmet bar in the benchmark permanently — it is
the honest record of what template-free, observability-free repair achieves.
Next steps, in value order: (a) the validity failure mode is a
connectivity-aware token choice away from closing (predict-then-check
against the target-free validator, as the ablation's prune pass already
does); (b) any repair-module package design must carry the observability
contract (damage events report destroyed positions) into the interface spec
before promotion is considered.

## Sources

- `labs/cellular_automata/ca_nca_growth_repair.py`
- `labs/cellular_automata/test_ca_nca_growth_repair.py`
- `data/cellular_automata/ca_nca_trained_repair_stage0.json`
- `data/cellular_automata/trained_repair_samples/`
- `labs/package_promotion/package_promotion_gate.py`
- `labs/package_promotion/test_package_promotion_gate.py`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- `research/experiment_reports/2026-07-04-ca-nca-trained-neighborhood-repair.md`
- `research/experiment_reports/2026-07-04-ca-nca-repair-context-ablation.md`
- `research/algorithm_cards/ca_nca_growth_repair.md`
