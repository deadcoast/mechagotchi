# Cycle 38 X7 v2: terminal survival corrected; care effect still refused

The versioned correction is implemented and tested, but **meaningful care-driven
descendant change remains unqualified**. Both complete fresh holdout evaluators
REFUSE promotion: 0/30 paired structural differences, with every other
preregistered criterion passing. Care selection remains off by default.

The exact repository was C:/Users/ryanf/github/_shelved/mechagotchi, branch
phase-l-gate, owner HEAD d4b4337d0dacbdfa816d990297c03a5da2d0cdca. No checkout,
environment, commit, sync or push was created. This report covers the care lane;
parent integration owns final native/build/full-sweep/preservation evidence.

## Corrected behavior and retained v1 evidence

V1 ranks welfare before elapsed survival ticks. Lifecycle increments elapsed
age before recording death, so a candidate dying on tick 10 and one alive after
tick 10 both report 10. Independent review reproduced all four retained pair 22
v1 receipts exactly. In its archive morphology probe, v1 chooses index 4,
gen_0b131675d2822091, welfare .691788, dead from starvation after tick 10, while
index 0 gen_721a54398bf9924c is alive after tick 10 at welfare .645193.

Explicit observed_care_selection_v2 ranks terminal survival first, then the
unchanged welfare, elapsed ticks and earliest index. It chooses live index 0 in
that regression. The known regression's fed/neglect structures differ under the
probe, but that discovered example is **not holdout qualification**. V1 policy,
receipts and original refusal artifacts remain unchanged and runnable. Off,
absent and empty contexts retain the exact original one-candidate generation.

V2 retains all eight candidates' full evaluation trajectories, initial/final
states, actual source-action mapping, recommendations, applied actions/thoughts,
terminal outcome and immutable Keeper/life/genome/context identity. Newborns
remain the pristine generated candidates; no evaluation damage, late-life state,
trained Q-table or rewards are inherited. Species covenant behavior priors are
separate from morphology. The probe is a designed stress evaluation, not a
biological or individual-personality claim.

## Fresh source-bound qualification

The preregistered holdout uses original product founders 10Ã¢â‚¬â€œ19 (zero-based),
seeds 20261007/20261017/20261027, eight legacy candidates per pool, and both
pristine and archive_morphology_probe_v1. Those seed ranges do not overlap each
other or the v1 ranges. Exact original product-manifest canonical digest
05d3512573e8066536181c731ce20839748980732f2e46cb0b957c464d495737
and the retained product evidence bind all founders, generation models, covenant
and ordered admissions. No alternate founders, replacement trials or seed search
were used.

Each observed feeding-every-third source life reached 12 ticks alive; each
neglected source life died at 10. Paired candidate evaluation uses only their
common observed 10-tick prefix, with the original 12/10 histories retained and no
padding. The known pair 22 regression was measured separately first.

| Evaluator | Complete holdout pairs | Structural differences | Candidate alive: fed / neglect | Decision |
| --- | ---: | ---: | ---: | --- |
| Pristine | 30 | 0 | 240/240 / 0/240 | REFUSE |
| Archive morphology probe v1 | 30 | 0 | 240/240 / 0/240 | REFUSE |

All neglected holdout candidates died from starvation; no fresh pool contained
a live neglected alternative for the correction to select. Pools contain 6Ã¢â‚¬â€œ8
structurally distinct bodies. The probe selected a nonzero index in 21/30 pairs,
but complete candidate rankings stayed identical across care histories in all 30
pairs for both evaluators. Feeding altered matched candidate welfare by .027176
in pristine and .041128Ã¢â‚¬â€œ.062290 in the probe. Thus care reaches evaluation and
changes welfare/survival, but still does not change held-out descendant rankings.

All original no-worse welfare and elapsed-survival criteria remain intact.
Added terminal nonregression and live-option preference also pass. Every pair
passes separate package repetition, exact laboratory mirror, metadata-only
negative control, same pool bytes, off/absent/empty parity, founder identity,
input immutability, exact pristine child, cold state, strict full trajectory
validation and the actual product's receipt loader. No acceptance bar was lowered.

The complete study measured 64.428071 seconds, including 0.523522 seconds setup;
maximum holdout pair 2.602590 seconds; regression 2.303483 seconds. The final
checkpoint including metric publication is 65.028740 seconds. Limits were 30
seconds setup/pair and 300 seconds cumulative. All 61 frozen source identities
were unchanged at evaluation. Every trial has a started receipt, raw payload,
final hashed receipt and checkpoint. Safe explicit resume validates completed
boundaries, hashes, original inputs, elapsed debit and derived evaluator state;
uncompleted, failed, drifted or resurrected evaluator work cannot auto-resume.
There was one scientific attempt, complete, with no operational failure.

## Verification and independent review

Exact commands use repository .venv/Scripts/python.exe 3.13.9 and -B, with
PYTHONPATH=packages/mecha_engine/src;game/src;labs/runtime_integration for lab tests.

```powershell
& .venv/Scripts/python.exe -B -m unittest discover -s labs/runtime_integration -p test_observed_care_v2.py -v
# RED: 5 tests, 5 errors (v2 public API/policy absent); .development/x7-v2/care/red.log
& .venv/Scripts/python.exe -B -m unittest discover -s labs/runtime_integration -p test_observed_care_v2_gate.py -v
# Instrument RED: 8 tests, 1 failure (boolean pair index accepted); gate-red.log
& .venv/Scripts/python.exe -B -m unittest discover -s labs/runtime_integration -p 'test_observed_care*.py' -v
# Final prefreeze GREEN: 37 tests, OK; green-reviewed.log
& .venv/Scripts/python.exe -B -m unittest discover -s packages/mecha_engine/tests -p test_care_contract.py -v
# GREEN: 4 tests, OK; package-02.log
& .venv/Scripts/python.exe -B labs/runtime_integration/observed_care_v2_gate.py --run .development/x7-v2/care/study --product-manifest .development/x7/learning/manifest.json --artifact data/game_client/care_v2_terminal_survival_stage0.json
# Complete 30 pairs; both evaluators REFUSE only structural_descendant_effect; study.log
```

An intermediate package test initially read full context from a deliberately
minimal origin record and raised KeyError; the test was corrected to resolve its
existing founder ordinal against the immutable input contexts. Runtime evidence
and thresholds were unchanged. package-01.log preserves that test-authoring error.

Pre-run independent review repaired the instrument's transitive source closure,
actual setup elapsed enforcement, evaluator-local regression refusals, exact
original cohort/admission binding, resume evaluator reconstruction and cumulative
time debit. Trajectory checks share the actual product loader's strict schema,
source mapping, continuity and terminal semantics. These repairs preceded the
single source-frozen scientific run. Independent review then validated 1,569
evidence checks, all 992 candidate trajectories / 9,920 ticks, 31 raw/final/start
receipt bindings and identical full rankings in all 30 pairs per evaluator.
Its audit is .development/x7-v2/independent-review.json. Final aggregate tests and native journeys
are reported by the integration owner; this lane does not claim them prematurely.

## Artifact serialization and remaining goal

The full new metric retains the complete manifest, known regression and all 30
paired receipts/trajectories. Its initial pretty JSON was 103,369,129 bytes. After
completion, only whitespace serialization was compacted; parsed equality was
verified; the compact metric is 28,581,819 bytes. The original bytes remain at
.development/x7-v2/care/study/metric-pretty-original.json. Neither the frozen
manifest nor any per-trial receipt was rewritten. Exact hashes and sizes are in
.development/x7-v2/care/serialization.json. This was an evidence packaging
transform, not another experiment, corrected outcome or dropped trajectory.

Meaningful care remains OPEN. A future justified mechanism needs a new
preregistration and independent qualification; neither this correction nor the
known regression closes that goal. No additional simulations, automatic retries,
default adoption or biological/attachment/personality claim is authorized by
these findings. Existing v1 negative findings retain their original criteria.

## Sources

- docs/development/cycle-38-terminal-survival-care.md
- research/experiment_reports/2026-10-06-lived-care-and-thought.md
- research/algorithm_cards/terminal_survival_care.md
- research/decision_records/0087-terminal-survival-care-selection.md
- labs/runtime_integration/observed_care_selection.py
- labs/runtime_integration/observed_care_v2_gate.py
- labs/runtime_integration/test_observed_care_v2.py
- labs/runtime_integration/test_observed_care_v2_gate.py
- packages/mecha_engine/src/mecha_engine/runtime/_observed_care.py
- packages/mecha_engine/src/mecha_engine/runtime/care.py
- packages/mecha_engine/tests/test_care_contract.py
- packages/mecha_engine/tests/helpers/care_contract_driver.py
- data/game_client/observed_care_inputs_stage0.json
- data/game_client/observed_care_selection_stage0.json
- data/game_client/care_v2_terminal_survival_stage0.json
- .development/x7-v2/care/study/manifest.json
- .development/x7-v2/care/analysis.json
- .development/x7-v2/care/serialization.json

- .development/x7-v2/independent-review.json
