# Experiment Report: Micro-Learning Switchboard Baseline

Date: 2026-05-12

## Objective

Continue the research plan into Stage 5 by building the first
`mecha_switchboard` prototype and proving that small interpretable learners can
produce explainable action decisions.

## Source Basis

The research plan calls for many narrow learners rather than one broad pet
brain. Contextual bandits are relevant because they select actions from context
and feedback. Hidden Markov Models are relevant as a conceptual reference for
latent mood/state inference, although this first lab uses a rule-based
HMM-like estimator rather than a full HMM.

Sources:

- https://arxiv.org/abs/1003.0146
- https://www.cs.cmu.edu/~durand/03-711/Readings/Rabiner89.pdf

## Scope

Included:

- `labs/grid_genome/micro_switchboard.py`
- recent interaction EWMA
- rule-based hidden mood estimator
- reward-average action preference bandit
- mutation risk scorer
- additive action utility switchboard
- scenario artifact at `data/micro_learners/switchboard_stage0.json`

Not included:

- learned HMM
- LinUCB implementation
- persistent online learning
- lifecycle/survival feedback loop
- user study
- anti-annoyance reward design

## Required Thread Contract

Each micro-learner returns:

- input
- output
- confidence
- explanation
- effects on action utilities

## Verification

Command:

```powershell
python -m unittest discover -s labs\grid_genome -p 'test_*.py'
```

Result:

```txt
Ran 34 tests in 0.374s
OK
```

Scenario command:

```powershell
python labs\grid_genome\micro_switchboard.py --output data\micro_learners\switchboard_stage0.json
```

## Scenario Results

```json
{
  "scenario_count": 3,
  "action_counts": {
    "feed": 1,
    "sleep": 1,
    "play": 1
  }
}
```

Observed decisions:

| Scenario | Selected action | Confidence |
| --- | --- | ---: |
| hungry_recent_attention | feed | 0.829113 |
| low_energy | sleep | 0.816769 |
| stable_curious | play | 0.776111 |

## Findings

The first switchboard can combine narrow signals and produce an explainable
action. The low-energy scenario correctly selects sleep, the hungry scenario
selects feed, and the stable/curious scenario selects play.

This is still a static scenario proof. It does not yet prove learning over
time, survival improvement, or non-annoyance. The next switchboard step should
connect selected actions to lifecycle rewards and update the action-preference
thread from observed outcomes.

## Decision

Keep the micro-switchboard direction. Do not introduce a broad ML model. The
next research step should add a small lifecycle simulator so the switchboard can
be evaluated against survival, need balance, and recovery metrics.

