# Experiment Report: CUBFF Semantic Transducer Baseline

Date: 2026-05-12

## Objective

Continue the research plan by testing whether CUBFF-style artificial-life
signals should become direct pixels or hidden semantic signals for the
Mechagotchi grid genome.

## Source Basis

The Computational Life paper studies self-replicating programs emerging from
simple computational substrates without an explicit fitness landscape. The
public CuBFF repository provides the CUDA-capable implementation used for many
of those experiments and exposes Python simulation state fields such as epoch,
soup, brotli size, and replication scores.

Sources:

- https://arxiv.org/abs/2406.19108
- https://github.com/paradigms-of-intelligence/cubff

## Scope

Included:

- `labs/cubff_transducer/cubff_transducer.py`
- synthetic CUBFF-style snapshots at `data/cubff_transducer/synthetic_snapshots.json`
- direct tape-to-pixels baseline
- statistical feature extraction into trait vectors
- behavioral trait extraction into temperament and mutation pressure
- hybrid semantic compiler using the existing constrained grid generator,
  validator, and SLIP alignment
- machine-readable report at
  `data/cubff_transducer/cubff_transducer_stage0_report.json`

Not included:

- real CUDA CuBFF execution
- ingestion of saved CuBFF binary state files
- survival simulation
- human readability study
- archive-level novelty comparison

## Verification

RED command:

```powershell
python -m unittest discover -s labs\cubff_transducer -p 'test_*.py'
```

Initial result:

```txt
ModuleNotFoundError: No module named 'cubff_transducer'
```

GREEN command:

```powershell
python -m unittest discover -s labs\cubff_transducer -p 'test_*.py'
```

Result:

```txt
Ran 4 tests in 0.008s
OK
```

Lab command:

```powershell
python labs\cubff_transducer\cubff_transducer.py --output-dir data\cubff_transducer --count 12 --rng-seed 5150 --slip data\slips\valid\slip_lcd_seed.json
```

## Results

| Pipeline | Valid | SLIP aligned | Mean readability |
| --- | ---: | ---: | ---: |
| A: raw tape to pixels | 0/12 | 0/12 | 0.0 |
| D: hybrid semantic compiler | 12/12 | 12/12 | 1.0 |

Statistical transducer summary:

```json
{
  "mean_replication_rate": 0.270833,
  "mean_semantic_pressure": 0.227403
}
```

Behavioral transducer summary:

```json
{
  "mean_mutation_pressure": 0.389992,
  "mean_animation_instability": 0.487235
}
```

Direct visual baseline failure modes:

```json
{
  "body mass below minimum: required body core has fewer than 4 cells": 12,
  "missing animation anchor": 12,
  "missing required sensor or expression organ": 12
}
```

## Findings

The raw visual pipeline repeats the known failure mode: byte-level CUBFF output
does not become a semantic Mechagotchi body by direct projection.

The hybrid semantic compiler proves the interface shape is useful. Tape
statistics can become mutation pressure, animation instability, and temperament
modifiers while the established grid generator, validator, and SLIP profile keep
the final body readable and valid.

This is not evidence that CuBFF should be adopted as a core dependency. The lab
uses synthetic CUBFF-style snapshots rather than a real CuBFF simulation run.
The only defensible conclusion is that the transducer contract is worth testing
against real CuBFF output.

## Decision

Keep CUBFF as `watch_synthetic_only`.

Do not map CUBFF tapes directly to pixels. Use CUBFF only as a hidden
artificial-life signal source unless a later real-snapshot lab proves improved
readability plus either novelty, survival, or lineage value over the existing
baseline.
