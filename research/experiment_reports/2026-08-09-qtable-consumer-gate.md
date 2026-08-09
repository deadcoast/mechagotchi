# The Q-Table Earns Its Consumer — the Bar Is Cleared, the Saturation Lesson Refuted, and the Gain Belongs to the Good Keeper (Cycle 27 · ENGINE · Q1)

Date: 2026-08-09

## WHY

P4 measured `qtable_policy` beating the incumbent frozen reactive rule
by **44.685%** at per-tick recommendation quality — but that
recommendation enters the decision today only as one diluted additive
nudge among ~15 threads (`effects[best_action] × confidence`, scale
0.30). DR 0051 decision 3: joining the fleet *"needs a consumer asking
for it."* Q1 builds that consumer and gates the end-to-end question
D6's welfare-saturation lesson said would come back ~0.

## WHAT

**The seam** (`labs/grid_genome/micro_switchboard.py`): a new
`qtable_consumer` learning switch — explicit `True` required (the D1
rule) — under which the switchboard **follows** the kept thread's
recommendation whenever the thread itself reports full confidence (its
own committed semantics: `QTABLE_CONFIDENT_VISITS = 12`; no new
constant). The override is recorded rung-conditionally in the decision
(`qtable_consumer: {followed, recommended, base_action, agreed, …}`),
rides through deliberation, and off-mode decisions never gain a key.
The harness gains one additive condition (`qtable_consumer` = the full
extended fleet plus the switch — the only delta against `full_fleet`
is the consumer).

**The gate** (`labs/micro_threads/qtable_consumer_gate.py`, 20 pins;
rule and prediction pre-registered): **G0** instruments before verdicts
— the committed switchboard scenarios artifact must reproduce
parsed-equal on every run (byte-identity off), and at the committed
budget the committed N3 `full_fleet` numbers (welfare, per-keeper,
survival) must reproduce exactly; **G2** the consumer must fire;
**G3** the D6 rule verbatim at the documented 5% bar, consumer
condition vs incumbent `full_fleet` on the same harness, seeds and
budgets — `adopt_into_default_candidate` / `eligible_not_promoted` /
`refuse_as_consumer`. **The beg interaction is measured, never gated**
here. **Prediction, recorded first**: `eligible_not_promoted` — the D6
saturation lesson.

## FINDINGS

**The prediction was REFUTED in the strong direction — the second
refuted prediction on this seam in two cycles, and the learning
track's strongest positive result to date.**

| | incumbent `full_fleet` | `qtable_consumer` | delta |
| --- | --- | --- | --- |
| welfare | 0.187712 *(committed, reproduced)* | **0.201518** | **+7.355%** — over the 5% bar |
| mean survival | 47.944 | **50.526** | +2.58 ticks |
| beg ticks | 6,475 | 6,711 | +236 |
| keeper feeds | 4,098 | 4,341 | +243 |

**Verdict: `ADOPT_INTO_DEFAULT_CANDIDATE`** — the first D6-style 5%
welfare clearance the learning track has produced at the decision seam
(the whole fleet's own additive contribution measured +0.965%). The
consumer fired on **59.4%** of ticks, agreed with the additive choice
on 73.8% of those — so roughly **one tick in six had its decision
changed** by the Q-table.

### The mechanism, measured per keeper — the gain belongs to the good keeper

| keeper | incumbent | consumer |
| --- | --- | --- |
| attentive | 0.727579 | **0.796586** (+0.069) |
| erratic | 0.083001 | 0.083023 |
| exploratory / neglectful / punitive | — | **unchanged to the sixth decimal** |

**The consumer amplifies good keeping and cannot rescue neglect.**
Under keepers who do not respond, companions die around tick 11 — the
table never reaches its 12-visit confidence floor, the consumer never
fires, and those trajectories are byte-identical. Under the attentive
keeper the warm table's choices (and its extra, well-timed begs — the
+236 beg ticks are answered at +243 feeds) buy +0.069 welfare and
+2.58 mean survival ticks. **The begging is part of the mechanism and
is recorded, not hidden**: the pet asks at the right times and the good
keeper answers. Whether more begging is acceptable default behavior is
a design question the promotion record must own.

### What D6's saturation lesson actually was

D6 measured every fleet thread's welfare removal cost at ~0 and
concluded the decision seam sat near the welfare optimum. This gate
shows the saturation was a property of **additive dilution**, not of
the seam: the same signal that nudges for +0.965% *steers* for
+7.355% when followed at full confidence. D6's numbers stand untouched
— they measured the blended fleet, and this measures a follower.

## HONEST REMAINDERS

1. **This verdict names ELIGIBILITY, not adoption** (pre-registered):
   promoting the consumer into the default fleet is a decision record
   plus package work (the promoted switchboard, the game's fleet, the
   parity pins) — chartered by DR 0060 as the named next task, the
   N5 → O1 pattern, never smuggled here.
2. **The gain is keeper-conditional** — a default player who neglects
   their companion gets nothing from it (and loses nothing).
3. **Follow-at-full-confidence is one consumer policy.** A graded
   (confidence-weighted) follower is a different consumer with its own
   gate.
4. **One seed corpus, five documented keepers, committed budgets**
   (N3's inherited frame).

## Verification

RED:

```text
PS> python -B -m unittest discover -s labs/micro_threads -p "test_qtable_consumer_gate.py"
ImportError: cannot import name 'QTABLE_CONSUMER_SWITCH' from 'micro_switchboard'
FAILED (errors=1)
```

GREEN (both touched labs):

```text
PS> python -B -m unittest discover -s labs/micro_threads -p "test_*.py"
Ran 160 tests in 9.396s
OK
PS> python -B -m unittest discover -s labs/grid_genome -p "test_*.py"
Ran 226 tests in 10.024s
OK
```

The lab invocation that produced the artifact:

```text
PS> python -B labs/micro_threads/qtable_consumer_gate.py
instrument: scenarios reproduced True; full_fleet reproduced True
incumbent welfare 0.187712  consumer welfare 0.201518  delta 7.355%  (bar 5.0%)
consumer fired on 0.594347 of ticks (agreement 0.738395)
beg ticks 6475 -> 6711 (delta 236)  keeper feeds 4098 -> 4341

verdict: ADOPT_INTO_DEFAULT_CANDIDATE
prediction_refuted: predicted eligible_not_promoted, measured adopt_into_default_candidate
wall clock 10.131 s
wrote data/micro_threads/qtable_consumer_gate_stage0.json
```

## Sources

- `sunsetted/TODO.md` (cycle 27 Q1) · `research/decision_records/0060-qtable-consumer-seam.md` (the record this study produced)
- `research/experiment_reports/2026-08-09-harder-skill-baselines.md` (P4, the consumer argument) · `2026-07-28-candidate-learner-ablation.md` (N3) · `2026-07-08-ablation-gates.md` (D6, whose saturation lesson this refutes at the follower)
- `labs/grid_genome/micro_switchboard.py` (the seam) · `labs/micro_threads/ablation_gates.py` (the additive condition) · `labs/micro_threads/qtable_consumer_gate.py` (+ 20 pins) · `data/micro_threads/qtable_consumer_gate_stage0.json`
- `data/micro_learners/switchboard_stage0.json` (the committed scenarios the off-mode is pinned against) · `data/micro_threads/candidate_learner_ablation_stage0.json` (the committed full_fleet numbers reproduced)
- `research/decision_records/0051-micro-learner-conditions-efg.md` (decision 3 — the consumer this gate supplies)
