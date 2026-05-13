# Experiment Report: CTM-Inspired Internal Ticks

Date: 2026-05-12

## Objective

Continue the advanced-lab research plan by testing whether the useful CTM idea
of reasoning over internal time can improve Mechagotchi's existing
micro-switchboard without adopting CTM as a dependency.

## Source Basis

Continuous Thought Machines introduce an internal temporal axis, neuron-level
temporal processing, and synchronization as a representation. For Mechagotchi,
the research question is smaller: can uncertain companion decisions spend extra
internal ticks before selecting an action?

Sources:

- https://pub.sakana.ai/ctm/
- https://github.com/SakanaAI/continuous-thought-machines
- https://arxiv.org/abs/2505.05522

## Scope

Included:

- confidence-gated internal ticks
- comparison against the single-pass micro-switchboard
- action accuracy, confidence gain, tick count, and trace metrics
- scenario artifact at `data/ctm_ticks/ctm_inspired_ticks_stage0.json`

Not included:

- CTM architecture implementation
- CTM training or checkpoints
- neuron-level synchronization model
- user-facing latency or animation tests
- persistent online learning

## Method

Each scenario first runs the existing single-pass switchboard. If confidence is
below 0.72, the wrapper spends up to four internal ticks accumulating
state-pressure evidence from hunger, energy, bond, stress, grid stability, and
recent interaction history.

This is deliberately labeled
`ctm_inspired_lightweight_internal_ticks`. It is a measured switchboard
mechanism, not CTM adoption.

## Verification

RED command:

```powershell
python -B .\labs\ctm_ticks\test_ctm_inspired_ticks.py
```

Initial result:

```txt
ModuleNotFoundError: No module named 'ctm_inspired_ticks'
```

GREEN command:

```powershell
python -B .\labs\ctm_ticks\test_ctm_inspired_ticks.py
```

Result:

```txt
Ran 4 tests in 0.011s
OK
```

Lab command:

```powershell
python -B .\labs\ctm_ticks\ctm_inspired_ticks.py --output-dir .\data\ctm_ticks --max-ticks 4 --confidence-threshold 0.72
```

Result summary:

```json
{
  "scenario_count": 4,
  "baseline_accuracy": 1.0,
  "deliberative_accuracy": 1.0,
  "mean_baseline_confidence": 0.805435,
  "mean_deliberative_confidence": 0.824067,
  "mean_confidence_gain": 0.018632,
  "mean_tick_count": 1.75,
  "extra_tick_case_count": 1,
  "decision_change_count": 0
}
```

## Findings

The tick wrapper improved mean decision confidence without changing any correct
scenario action. Only one scenario needed extra ticks, which is the desired
shape: confident cases should remain single-pass.

The result is not strong enough to justify a CTM model dependency. It is enough
to keep confidence-gated internal ticks as a prototype switchboard mechanism.

## Decision

Prototype the lightweight internal-tick wrapper. Keep CTM itself as conceptual
source material only.
