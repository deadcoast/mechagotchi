# The Harder Baselines N3 Named — the Q-Table Beats the Incumbent Rule Itself, and F's Drop Holds Like-for-Like (Cycle 26 · ENGINE · P4)

Date: 2026-08-09

## WHY

DR 0051 kept condition E (`qtable_policy`) on skill **+55.459% against
uniform random** and, in its own "What this record does NOT do" list,
named both of this slice's questions: the uniform baseline is *"a weak
opponent"* (the comparison against the incumbent frozen reactive rule
was not run), and F's stump baseline *"gets a full-sample oracle while
the tree is scored on its online recommendation — an asymmetry that
runs against the tree."* P4 runs both, as a **new artifact** (DR 0053:
a measurement is reproduced or superseded, never improved) — the
committed N3 artifact is untouched, and both findings become dated
notes beside DR 0051.

## WHAT

`labs/micro_threads/harder_skill_baselines.py` (+ 17 pins; rule and
prediction pre-registered). The collector is a **superset of N3's** —
the same harness (`run_dependent_lifecycle`), the same seeds, the same
record order — with two extra fields: the **frozen reactive rule's own
choice** per record (the switchboard run on the same pre-tick state
with the fleet's inputs stripped exactly as the harness's `frozen`
condition never carries them), and the record's lifecycle identity.
**The instrument gate**: at the committed budget the collector must
reproduce **all** of N3's committed statistics exactly — both regrets,
both returns, the Brier pair, the record count — or it raises. The
statistics themselves are imported from N3's module
(`_policy_regret`, `_group_means`, `_pct_reduction`, `_brier`), never
re-implemented.

- **E vs the incumbent rule**: the rule's empirical regret over the
  same bucket means, judged at the documented D6 5% bar
  (`beats_incumbent_rule` / `indistinguishable_from_rule` /
  `loses_to_incumbent_rule`).
- **F vs a like-for-like ONLINE stump**: per-lifecycle running
  (side, action) means, predict-then-update, cold until the side has
  seen two distinct actions (the tree's own cold-start footing), valued
  under the same full-sample means as the committed framing
  (`drop_holds_like_for_like` / `drop_overturned_like_for_like`).
- **No roster change in any branch, pre-registered.**

**Prediction, recorded first**: E's advantage expected to collapse into
the ±5% band (`indistinguishable_from_rule`); F's drop expected to hold.

## FINDINGS

**The prediction was REFUTED on E, and the refutation is the headline.**

| question | committed | measured harder | verdict |
| --- | --- | --- | --- |
| E: Q-table regret vs opponent | 0.015406 vs uniform 0.03459 (+55.459%) | vs the **frozen rule 0.027851** → **+44.685%** | **BEATS_INCUMBENT_RULE** |
| F: tree return vs stump | 0.799976 vs oracle 0.814443 (−1.776%) | vs the **online stump 0.805975** → **−0.744%** | **DROP_HOLDS_LIKE_FOR_LIKE** |

**1. The incumbent rule turned out to be barely harder than uniform
random.** The frozen reactive rule's per-tick choices carry empirical
regret 0.027851 against the bucket optima — 81% of uniform random's
0.03459. D6's finding that the frozen rules sit near the welfare
optimum is about *survival outcomes*; per-tick action selection is a
different question, and on it the rules leave real regret on the table.
The Q-table's +55.459% did not collapse: it beats **the incumbent
itself, on the incumbent's own replayed states, by 44.685%** — nine
times the documented bar.

**2. F's asymmetry was real and accounted for roughly 58% of the
committed gap — and the drop still holds.** On equal online footing the
stump's return falls from the oracle's 0.814443 to 0.805975, narrowing
the tree's deficit from −1.776% to **−0.744%** — the sign never flips,
and +5% is nowhere in sight. DR 0051's own caution (*"the −1.776%
margin should not be read as precise"*) now has the like-for-like
number beside it.

**3. Nothing moves.** The roster is unchanged in both branches
(pre-registered); DR 0051's keep and drops stand — E's keep now rests
on a much stronger footing than the record could claim, and that
strengthening is recorded as a dated note beside DR 0051, not a
re-score. Promoting `qtable_policy` into the fleet remains a separate
record needing a consumer — now with a measurably better case waiting
for it.

## HONEST REMAINDERS

1. **Regret here is regret against an empirical optimum**, computed
   from the harness's own executed behaviour — not a counterfactual
   simulator (N3's inherited framing). The bucket means are made
   largely of the rule-plus-keeper behaviour distribution.
2. **One extended-fleet condition**: the harder baselines are measured
   where the candidates actually ran, not under the frozen condition's
   own trajectories.
3. **The online stump is one operationalization** (per-lifecycle
   running means, predict-then-update, two-action cold start) —
   pre-registered before the run, but a different online footing is a
   different measurement.

## Verification

RED:

```text
PS> python -B -m unittest discover -s labs/micro_threads -p "test_harder_skill_baselines.py"
ModuleNotFoundError: No module named 'harder_skill_baselines'
FAILED (errors=1)
```

GREEN:

```text
PS> python -B -m unittest discover -s labs/micro_threads -p "test_harder_skill_baselines.py"
Ran 17 tests in 0.123s
OK
PS> python -B -m unittest discover -s labs/micro_threads -p "test_*.py"
Ran 140 tests in 7.039s
OK
```

The lab invocation that produced the artifact:

```text
PS> python -B labs/micro_threads/harder_skill_baselines.py
instrument: committed statistics reproduced = True
E  committed q-vs-uniform 55.459%  rule_regret 0.027851  q_vs_rule 44.685%
F  committed tree-vs-oracle -1.776%  online stump 0.805975 (21093 scored)  tree_vs_online -0.744%

E: BEATS_INCUMBENT_RULE   F: DROP_HOLDS_LIKE_FOR_LIKE   roster changed: False
prediction_refuted: predicted {'e_verdict': 'indistinguishable_from_rule', 'f_verdict': 'drop_holds_like_for_like'}, measured {'e_verdict': 'beats_incumbent_rule', 'f_verdict': 'drop_holds_like_for_like'}
wall clock 5.895 s
wrote data/micro_threads/harder_skill_baselines_stage0.json
```

## Sources

- `sunsetted/TODO.md` (cycle 26 P4)
- `research/decision_records/0051-micro-learner-conditions-efg.md` (now carrying two dated notes from this study)
- `labs/micro_threads/harder_skill_baselines.py` (+ `test_harder_skill_baselines.py`, 17 pins) · `data/micro_threads/harder_skill_baselines_stage0.json`
- `labs/micro_threads/candidate_learner_ablation.py` (the committed instrument, imported never re-implemented) · `data/micro_threads/candidate_learner_ablation_stage0.json` (the committed numbers reproduced)
- `labs/micro_threads/ablation_gates.py` (`run_dependent_lifecycle`, `KEEP_THRESHOLD_PCT`, the `frozen` condition semantics)
- `research/experiment_reports/2026-07-28-candidate-learner-ablation.md` (N3)
