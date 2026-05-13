# Experiment Report: SLIP Multigeneration Lineage Runner

Date: 2026-05-13

Status: `research_slip_multigeneration_lineage_runner_no_package_code`

## Question

Can Mechagotchi persist a real multigeneration SLIP lineage in the lab, with
archive update decisions and lineage graph continuity, without claiming package
runtime integration or profile-weighted evolution?

## Plan Alignment

This continues the research plan's evolution, quality-diversity, lifecycle, and
lineage tracks. The previous offspring gate proved one bounded child decision;
the long-horizon gate proved behavior survival; the readability gate prepared
the human-review packet. This experiment addresses the remaining
repo-verifiable blocker: persistent multigeneration lineage. No `packages/`
code was created.

## External Source Refresh

Sources used:

- Illuminating search spaces by mapping elites:
  https://arxiv.org/abs/1504.04909
- Avida Digital Evolution Platform: https://avida.devosoft.org/

MAP-Elites supports preserving diverse high-performing elites in behavior
space rather than reducing evolution to one scalar winner. Avida supports
treating generation-by-generation lineage and measurement outputs as explicit
digital-evolution experiment artifacts.

## Method

Added `labs/workshop_editor/slip_multigeneration_lineage_runner.py` with:

- `run_profile_multigeneration_lineage_probe`
- `run_slip_multigeneration_lineage_runner_lab`
- `write_slip_multigeneration_lineage_runner_artifacts`

Added `labs/workshop_editor/test_slip_multigeneration_lineage_runner.py` first
and watched it fail on the missing module before implementing the runner.

For each current valid profile, the lab:

1. selects an initial runtime parent from the profile-specific archive;
2. produces three bounded offspring candidates per generation;
3. scores children with the existing offspring gate metrics;
4. records archive actions separately from the candidate-lineage frontier;
5. continues qualified selected children for three generations;
6. builds a lineage graph over the initial parent and all generated offspring;
7. rejects unsupported-version and mismatched-corpus probes before the runner
   starts.

## Results

Machine-readable artifacts:

- `data/workshop_editor/slip_multigeneration_lineage_runner_stage0.json`
- `data/workshop_editor/slip_multigeneration_lineage_runner_stage0/slip_multigeneration_lineage_runner_stage0.json`
- `data/workshop_editor/slip_multigeneration_lineage_runner_stage0/*_multigeneration_lineage_runner.json`
- `data/workshop_editor/slip_multigeneration_lineage_runner_data.js`
- `research/algorithm_cards/slip_multigeneration_lineage_runner.md`

Summary:

| Metric | Result |
| --- | ---: |
| Current valid profiles covered | 3 |
| Multigeneration successes | 3 |
| Generation records | 9 |
| Selected offspring | 9 |
| Continued child count | 9 |
| Add archive niche count | 2 |
| Hold parent count | 7 |
| Replace parent count | 0 |
| Invalid probes rejected | 2 |
| Max generation reached | 4 |
| Mean selected offspring score | 0.925309 |
| Mean selected runtime survival ratio | 1.0 |
| Mean dominant lineage share | 0.333333 |

Closed states:

- `persistent_multigeneration_lineage_runner`
- `multigeneration_lineage_graph_continuity`
- `invalid_profile_rejected_before_multigeneration_lineage`

Blocked states:

- `profile_weighted_evolution`
- `package_runtime_lifecycle_integration`
- `manual_readability_calibration`
- `final_descriptor_threshold_lock`

## Interpretation

The lab now persists qualified selected children across three generations for
all current SLIP profiles. The lineage graph has no orphaned children, reaches
generation 4, and records every generated branch. Archive action remains
separate from the candidate frontier: the runner can continue a qualified child
as a lineage stress test even when the archive action holds the parent.

This still is not profile-weighted evolution in the product/runtime sense.
There is no package runtime state, no installed package boundary, and no human
readability calibration.

## Verification

RED command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_slip_multigeneration_lineage_runner.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'slip_multigeneration_lineage_runner'
```

GREEN command:

```powershell
python -B -m unittest .\labs\workshop_editor\test_slip_multigeneration_lineage_runner.py
```

Result:

```txt
Ran 4 tests in 0.369s
OK
```

Artifact command:

```powershell
python -B .\labs\workshop_editor\slip_multigeneration_lineage_runner.py
```

Result:

```txt
persistent_multigeneration_lineage_runner_specified: true
total_generation_records: 9
continued_child_count: 9
max_generation_reached: 4
mean_selected_offspring_score: 0.925309
```

## Decision

Adopt `slip_multigeneration_lineage_runner_stage0` as the Stage 0 proof that
the lab can persist SLIP lineages across multiple generations.

Next research should integrate package/runtime lifecycle boundaries and collect
manual readability ratings before claiming profile-weighted evolution.
