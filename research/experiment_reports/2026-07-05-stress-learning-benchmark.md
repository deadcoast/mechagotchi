# Experiment Report: Stress Learning Benchmark

Date: 2026-07-05

## Objective

Give decision record 0009 its evidence: measure the learning candidate —
the feedback-enabled micro-switchboard — against the frozen switchboard
where survival actually varies (the stress regime), instead of the
sheltered environment where the prior measurement's survival delta was
structurally forced to zero.

## Design

24 generated morphologies (profile-aligned parents, package generation),
each evaluated on the archive's contracted stress probe for 72-tick
episodes, twice: feedback on and feedback off. The arms share everything —
the original feedback lab's deliberate reward miscalibration (the
learnable-gap premise, imported from `switchboard_feedback` with
justification), the same switchboard, the same `advance_tick` — differing
ONLY in whether observed rewards update the per-action histories.
Deterministic end to end (pinned by test).

## Verification

RED (module did not exist):

```powershell
python -B -m unittest discover -s labs/runtime_integration -p "test_stress_learning*.py"
# ModuleNotFoundError -> FAILED (errors=1)
```

GREEN:

```txt
Ran 4 tests in 0.070s
OK
```

Lab command:

```powershell
python -B .\labs\runtime_integration\stress_learning_benchmark.py
```

```txt
"count": 24, "mean_stress_load": 0.809626,
"feedback_survival_rate": 1.0, "frozen_survival_rate": 1.0,
"mean_survival_ratio_delta": 0.0, "mean_need_balance_delta": 0.080069,
"saved_by_feedback_count": 0, "lost_by_feedback_count": 0
"decision": "learning_matches_frozen_under_stress",
"thresholds": {"feedback_beats_frozen_survival": false,
               "feedback_beats_frozen_need_balance": true}
```

## Findings

1. **The experiment falsified the survival framing itself** — which is
   what a falsifiable bar is for. Survival under the stress regime is
   decided by the morphology's structural load (the lifecycle's
   documented bistability): both arms survive identically, zero
   morphologies saved or lost by feedback.
   `feedback_beats_frozen_survival = false`, recorded as first-class
   evidence.
2. **The learning benefit is wellbeing, and it doubles under stress**:
   mean need-balance delta +0.080069 (vs +0.03964 in the sheltered
   measurement) at zero survival risk. Under load, choosing actions from
   updated reward estimates matters more for how well the creature lives,
   not whether it lives.
3. Consequence for the engine's behavior story, now measured rather than
   assumed: **morphology decides survival (evolution's domain); policy
   decides wellbeing (learning's domain).** Decision record 0009 bounds
   the learning module's promotion claim accordingly — need-balance
   improvement only, no survival claim permitted without new evidence.
4. Sampling note, stated honestly: this batch's loads (mean 0.81, max
   below the ~0.95 collapse boundary) produced no deaths in either arm;
   the evolution run's deaths came from boundary-adjacent morphologies.
   The policy-independence conclusion rests on the bistability mechanism
   (collapse is determined by starting load before any action matters),
   not merely on this sample's zero-death outcome.

## Decision

Status: `learning_matches_frozen_under_stress` (survival) with
`feedback_beats_frozen_need_balance = true` — the promotion gate's
learning candidate derives from exactly these keys plus
`lost_by_feedback_count == 0`. DR 0009 proceeds with the bounded
wellbeing claim. Follow-up candidates for a future survival-relevant
learner (own evidence, own decision record): action policies that reduce
accumulated stress near the collapse boundary, if the lifecycle ever
gains such actions.

## Sources

- `labs/runtime_integration/stress_learning_benchmark.py`
- `labs/runtime_integration/test_stress_learning_benchmark.py`
- `data/runtime_integration/stress_learning_benchmark_stage0.json`
- `labs/grid_genome/switchboard_feedback.py`
- `labs/grid_genome/micro_switchboard.py`
- `data/micro_learners/switchboard_lifecycle_feedback_stage0.json`
- `research/algorithm_cards/micro_learning_switchboard.md`
- `research/decision_records/0009-create-mecha-engine-learning-target.md`
- `research/package_specs/mecha_engine_learning_interface_spec.md`
