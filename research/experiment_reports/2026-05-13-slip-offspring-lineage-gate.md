# Experiment Report: SLIP Offspring Lineage Gate

Date: 2026-05-13

Status: `research_slip_offspring_lineage_gate_no_package_code`

## Question

Can Mechagotchi specify bounded offspring mutation selection and lineage
replacement decisions after runtime lifecycle/archive parent selection, without
claiming persistent profile-weighted evolution?

## Plan Alignment

This continues the research plan's evolution, quality-diversity, lifecycle, and
`SLIP` tracks. The runtime selection policy chose existing archive elites; this
experiment adds a child-selection and lineage-decision gate. No `packages/` code
was created.

## External Source Refresh

Sources used:

- MAP-Elites paper: https://arxiv.org/abs/1504.04909
- Essentials of Metaheuristics: https://people.cs.gmu.edu/~sean/book/metaheuristics/
- Evolutionary computation survivor-selection reference: https://www.evolutionarycomputation.org/part-one/fitness-selection-and-population-management/

MAP-Elites supports treating replacement as a niche-aware operation rather than
global scalar top-k. The evolutionary-computation references are used for the
operator separation: parent selection, variation, and survivor/replacement
policy are distinct gates.

## Method

Added `labs/workshop_editor/slip_offspring_lineage_gate.py` with:

- `run_profile_offspring_lineage_probe`
- `run_slip_offspring_lineage_gate_lab`
- `write_slip_offspring_lineage_gate_artifacts`

Added `labs/workshop_editor/test_slip_offspring_lineage_gate.py` first and
watched it fail on the missing module before implementing the gate.

For each current valid profile, the lab:

1. selects a runtime/archive parent using `slip_runtime_selection_policy`;
2. loads the selected parent grid from the generated profile corpus;
3. builds bounded child candidates from the SLIP mutation preview caps;
4. validates every child against grid validation and SLIP alignment;
5. scores children by survival, need balance, bond, archive fitness, parent
   continuity, qualified novelty, mutation-cap compliance, validity, and SLIP
   alignment;
6. emits one lineage action: `replace_parent`, `add_archive_niche`, or
   `hold_parent`.

Invalid probes cover unsupported `SLIP` version and mismatched profile/candidate
corpus. Both must stop before the offspring gate starts.

## Results

Machine-readable artifacts:

- `data/workshop_editor/slip_offspring_lineage_gate_stage0.json`
- `data/workshop_editor/slip_offspring_lineage_gate_stage0/slip_offspring_lineage_gate_stage0.json`
- `data/workshop_editor/slip_offspring_lineage_gate_stage0/*_offspring_lineage_gate.json`
- `data/workshop_editor/slip_offspring_lineage_gate_data.js`
- `research/algorithm_cards/slip_offspring_lineage_gate.md`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Offspring gate successes | 3 |
| Lineage decisions | 3 |
| Invalid probes rejected | 2 |
| Mean selected offspring score | 0.928194 |
| Mean selected offspring need balance | 0.793865 |
| Mean selected offspring survival ratio | 1.0 |
| Distinct selected offspring ids | 3 |
| Distinct selected offspring niches | 3 |
| Replace parent decisions | 0 |
| Add archive niche decisions | 1 |
| Hold parent decisions | 2 |

Selected offspring:

| Profile | Parent | Selected offspring | Archive niche | Action |
| --- | --- | --- | --- | --- |
| `slip_lcd_seed` | `slip_lcd_seed_constrained_011` | `slip_lcd_seed_constrained_011_offspring_stability_tune` | `1,1,2,4,4,4,1` | `hold_parent` |
| `slip_gray_stable` | `slip_gray_stable_constrained_008` | `slip_gray_stable_constrained_008_offspring_core_growth` | `2,1,1,4,4,4,1` | `add_archive_niche` |
| `slip_amber_social` | `slip_amber_social_constrained_004` | `slip_amber_social_constrained_004_offspring_stability_tune` | `2,0,2,4,4,4,2` | `hold_parent` |

Closed states:

- `offspring_mutation_selection`
- `lineage_replacement_policy`
- `invalid_profile_rejected_before_offspring_lineage`
- `runtime_parent_to_offspring_selection_trace`

Blocked states:

- `profile_weighted_evolution`
- `package_runtime_lifecycle_integration`
- `manual_readability_calibration`

## Interpretation

The offspring mutation and lineage replacement gap is now specified and tested
at Stage 0. The lab produces real child grid records, validates cap compliance,
and separates parent replacement from archive niche addition.

This is still not profile-weighted evolution. The follow-on
`slip_long_horizon_behavior_gate_stage0` now covers held-out long-horizon
behavior tests, and `slip_multigeneration_lineage_runner_stage0` now covers
lab-only multigeneration lineage. There is still no package runtime
integration and no manual readability calibration.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_slip_offspring_lineage_gate.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'slip_offspring_lineage_gate'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_slip_offspring_lineage_gate.py
```

Result:

```txt
Ran 4 tests in 0.255s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\slip_offspring_lineage_gate.py
```

## Decision

Adopt `slip_offspring_lineage_gate_stage0` as the Stage 0 proof for lab-only
offspring mutation selection and lineage replacement policy.

Next research should collect manual readability ratings and calibrate proxy
readability thresholds before claiming profile-weighted evolution.
