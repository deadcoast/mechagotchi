# Experiment Report: Lifecycle Simulator Baseline

Date: 2026-05-12

## Objective

Continue the post-v0.1 research sequence by building the first lifecycle
simulator and measuring survival, need balance, and recovery.

## Source Basis

The v0.1 report identified lifecycle simulation as the next gate before CA/NCA
growth, CUBFF behavior signals, or archive descriptor changes. The official
Tamagotchi Connection manual is useful only as a care-loop reference: feeding,
games, sleep/light management, health meter, age, and care-dependent growth.
JaxLife is useful as an artificial-life measurement reference because it frames
survival and behavior as simulator outputs.

Sources:

- https://tamagotchi-official.com/manual/toy/connection/
- https://tamagotchi-official.com/manual/toy/connection/connection_web_manual_IS_EN.pdf
- https://arxiv.org/abs/2409.00853

## Scope

Included:

- `labs/lifecycle_sim/lifecycle_sim.py`
- `labs/lifecycle_sim/test_lifecycle_sim.py`
- deterministic state ticks for hunger, energy, stress, bond, and grid stability
- policy comparison for switchboard, idle, and random actions
- recovery event counting for dangerous hunger, energy, stress, bond, and stability
- Stage 0 artifact at `data/lifecycle/lifecycle_stage0.json`

Not included:

- player traces
- hidden disease/medicine loop
- local grid-cell stress propagation
- CA/NCA repair
- reproduction or death animation
- manual user rating protocol

## Verification

RED command:

```powershell
python -m unittest discover -s labs\lifecycle_sim -p 'test_*.py'
```

Initial result:

```txt
ModuleNotFoundError: No module named 'lifecycle_sim'
```

GREEN command:

```powershell
python -m unittest discover -s labs\lifecycle_sim -p 'test_*.py'
```

Result:

```txt
Ran 5 tests in 0.035s
OK
```

Lab command:

```powershell
python labs\lifecycle_sim\lifecycle_sim.py --output data\lifecycle\lifecycle_stage0.json --ticks 72 --rng-seed 20260512
```

## Metric Definition

`need_balance` is a full-horizon average. If a policy dies before the requested
tick horizon, every missing tick contributes `0.0`. This prevents early death
from looking artificially strong because it has fewer bad late ticks.

## Results

| Policy | Survival ticks | Alive | Need balance | Recovery events | Death cause |
| --- | ---: | --- | ---: | ---: | --- |
| switchboard | 72 | true | 0.789129 | 14 | none |
| idle | 11 | false | 0.121004 | 0 | starvation |
| random | 21 | false | 0.236001 | 2 | starvation |

Switchboard action counts:

```json
{
  "feed": 14,
  "play": 44,
  "sleep": 14,
  "idle": 0,
  "mutate": 0
}
```

## Findings

The first lifecycle simulator turns switchboard decisions into measurable
survival evidence. On the default LCD seed creature and SLIP profile, the
switchboard policy survived the full 72-tick horizon, recovered from dangerous
need states 14 times, and beat idle/random on full-horizon need balance.

The result does not prove a final companion model. It proves the project now has
a small survival benchmark that can reject policies that look plausible in static
scenarios but fail over time.

## Decision

Keep the lifecycle simulator as `prototype`.

Next research should add a held-out readability/manual rating protocol, then use
lifecycle metrics to extend MAP-Elites descriptors and evaluate grid repair
experiments.
