# Experiment Report: The Micro-Learner Ablation Conditions E/F/G — Built at Last, and Two of Three Dropped by the Documented Rule (Cycle 24 · ENGINE · N3)

Date: 2026-07-28

## WHY

The dossier's micro-learner ablation names eight conditions
(`deep-research.md:714–724`). Phase D built the eleven-thread fleet and
ran A/B/remove-one over it, keeping five and dropping six — but **none
of the eleven is a Q-table, a tiny decision tree, or a Bayesian
counter**. So

```text
E. full minus Q-table;
F. full minus tiny tree;
G. full minus Bayesian counter;
```

have been *documented and unmet since cycle 12*. This is the oldest
open protocol item in the learning track, and it is deliberately this
cycle's **non-archive ENGINE slice**: cycles 22 and 23 were both
archive-heavy, and the anti-periscope rule applies to the developer too.

## WHAT

**Three learners built, each the dossier's own mechanism with the
dossier's own named weakness respected rather than engineered around**
(`deep-research.md:647–649`):

| condition | learner | dossier's weakness | how it is respected |
| --- | --- | --- | --- |
| **E** | `qtable_policy` | *"state explosion, needs repeated visits"* | scoped tightly to 3×3 hunger/energy buckets; silent until a bucket has ≥ 3 visits |
| **F** | `tiny_tree_router` | *"brittle if overfit"* | depth 2, at most four leaves, thresholds adapt as running means rather than being fitted |
| **G** | `bayes_keeper_counter` | *"limited expressivity"* | one Beta-Bernoulli question only — how often is a tick social? |

All three credit the **executed** action, not their own recommendation:
the keeper can override the companion's choice, and a learner that
credited its own suggestion would be learning a policy the world never
ran.

**The rule is D6's rule, verbatim — not a new one invented for the
candidates.** The dossier: *"Keep a learner only if its removal causes
at least a 5% decline in one target metric without improving another
more important metric."* Operationally as D6 applied it: a learner keeps
its place on **EITHER** its welfare removal cost **OR** its own
documented skill metric, at the same 5% bar. `ablation_gates` is
**IMPORTED, never re-implemented** — the candidates are judged by the
same code that judged the incumbent eleven.

Each skill baseline follows an existing D6 precedent rather than a new
statistic: regret reduction vs a uniform random policy (the
`animation_bandit` precedent), return improvement vs a **depth-1 stump**
(the tree's own simpler self), and next-interaction Brier reduction vs
the **running rate** (the `attention_forecast` precedent, the harsher of
the available baselines).

**Written into the module before the run**, so it could be refuted:

> D6 measured every welfare removal cost at ~0 — the frozen reactive
> rules already sit near the autonomous-behavior welfare optimum, and
> *"the remaining welfare belongs to the keeper"*. So all five kept
> threads were kept on **skill**, not welfare. The candidates are
> expected to show near-zero welfare cost too, with their fate resting
> on skill.

## FINDINGS

### The verdicts: 1 kept, 2 dropped

| | learner | decision | welfare removal cost | skill metric |
| --- | --- | --- | --- | --- |
| **E** | `qtable_policy` | **KEEP** | 0.795% | **+55.459%** regret reduction |
| **F** | `tiny_tree_router` | **DROP** | 0.615% | **−1.776%** vs depth-1 stump |
| **G** | `bayes_keeper_counter` | **DROP** | 1.194% | **+2.756%** Brier reduction |

The pre-run expectation held: **every candidate's welfare cost is under
1.2%**, far below the 5% bar, so all three were decided on skill —
exactly as the incumbent five were.

**Both drops carry a measured mechanism, and both confirm the dossier's
own weakness column:**

- **F — the second split is decoration.** The depth-2 tree returns
  **0.799976** against the depth-1 stump's **0.814443**. Splitting on
  energy *after* hunger makes the router **worse than not splitting at
  all**. The dossier predicted "brittle if overfit"; measured here, the
  extra depth does not overfit so much as dilute — the leaf populations
  are thin enough that the second split adds variance without adding
  signal.
- **G — a Beta-Bernoulli is barely distinguishable from a running
  mean.** Brier **0.190317** against the running rate's **0.195712** —
  a real improvement, in the right direction, and **under half the
  bar**. The dossier predicted "limited expressivity"; the measurement
  puts a number on it: on this one question, the uncertainty a Beta
  posterior carries buys **2.756%**, and nothing in the switchboard
  consumes the uncertainty itself.

**E is kept on the same footing as the incumbent five** — a large skill
number and a negligible welfare contribution. Its regret is **0.015406**
against a uniform random policy's **0.03459** over 23,972 scored ticks.

### The incumbent eleven, re-judged rather than assumed

The charter named this explicitly: *"a drop that changes the kept-five
roster would be a real result about the fleet."* Adding three threads
moves the `full_fleet` baseline every removal cost is measured against,
so all eleven were recomputed:

| thread | welfare removal cost (extended fleet) |
| --- | --- |
| hunger_forecast | 0.359% |
| hidden_mood_hmm | 0.289% |
| boredom_novelty / attention_forecast | 0.225% |
| interaction_timing | 0.128% |
| energy_forecast | 0.018% |
| animation_bandit, mutation_stability, readability, slip_compat, lineage_survival | 0.000% |

**Every one is below the 5% bar, as in D6.** The kept-five roster is
therefore **unchanged** — and the reason is worth stating precisely
rather than waving at: the roster rests on skill metrics that are read
from the D2/D3 artifacts and are **properties of each thread's own
prediction task, not of fleet composition**, so adding threads cannot
move them. What adding threads *could* have moved is the welfare side,
and it did not move it across the bar for any thread.

### One number did move, and it is small but real

| gate | D6 (11 threads) | N3 (14 threads) |
| --- | --- | --- |
| full vs rules_only | 292.649% | **296.653%** |
| fleet vs frozen | **−0.054%** | **+0.965%** |

D6 recorded the fleet as very slightly *worse* than the frozen reactive
rules; with the three candidates opted in it is very slightly *better*.
The sign flipped. This is about **1%** — far below any gate, and
reported because it is a measured effect of the candidates on the
decision seam, not because it licenses a claim. D6's conclusion stands
unchanged: the frozen rules sit near the autonomous-behavior welfare
optimum and the remaining welfare belongs to the keeper.

### Byte-identity proven, not asserted

The extension rides the existing opt-in seam: `FLEET_THREADS` is
untouched, and a thread without an explicit
`learning_switches[name] is True` never runs and holds no memory.
The claim is **proven by regenerating the committed D6 artifact at full
scale and hashing it**:

```text
committed    sha256: 75640475cc9c9fc4cab5f4c4955121e8a2a118672169e5c64acdc5bf17e66f44
regenerated  sha256: 75640475cc9c9fc4cab5f4c4955121e8a2a118672169e5c64acdc5bf17e66f44
BYTE-IDENTICAL: True
```

Every field identical, including all 14 condition welfares and all 11
thread verdicts. The off-mode roster is additionally pinned against a
**frozen literal list** of the Phase-D eleven — not against a second
call to the new code, which is the trap M3 shipped and external review
caught.

## PROCESS DEVIATION, RECORDED NOT BURIED

**The first run scored condition G at −154.796%, and that number was my
instrument's error, not the learner's.**

`bayes_keeper_counter` observes `recent_interactions`, which
`lifecycle_sim` fills with `1 if action in {"feed", "play"}` — *whether
the executed action was social*. The first observer scored its
prediction against `override is not None` — *whether the keeper
intervened*. Those are different events: an autonomous `play` is social
without the keeper, and the learner was being marked wrong on a question
it was never asked.

Corrected to score the event the thread can actually observe, and
**re-run**: G moves **−154.796% → +2.756%**, and **E and F are
bit-for-bit unchanged** (55.459%, −1.776%), which is the check that the
fix touched only the mismatched metric.

This is a defect repair, not a re-score: the rule, the bar and the
baselines are exactly as pre-registered, and the correction makes the
measurement *valid*, not *nicer* — G is dropped either way. The thread's
own explanation string was also corrected, having called the quantity
"keeper responsiveness" when it measures the social-tick rate
(keeper-dominated in the beg-mediated harness, but not purely keeper).

## HONEST REMAINDERS

1. **Nothing is promoted.** A kept candidate is a learner that passed
   the ablation gate, not a fleet member. `FLEET_THREADS` is unchanged,
   and promoting `qtable_policy` would need its own decision record with
   a consumer asking for it.
2. **E's baseline is weak by construction.** Uniform random is the
   `animation_bandit` precedent's shape, so it is the documented
   comparison — but the harder question, *does the Q-table beat the
   incumbent reactive rule*, is not what the precedent asks and is **not
   run here**. The 55% is "better than choosing at random in the same
   bucket", which is a lower bar than it sounds.
3. **F's baseline is given an oracle.** The depth-1 stump is scored on a
   full-sample argmax while the tree is scored on its **online**
   recommendation. That asymmetry runs *against* the tree, so −1.776%
   is a conservative reading; a like-for-like online stump would narrow
   the gap and might close it. The verdict is a drop either way at the
   5% bar, but the margin should not be read as precise.
4. **The welfare seam is saturated and this study inherits that.** D6
   measured it; N3 reproduces it. A near-zero candidate welfare cost
   bounds the *decision seam*, not the learner's value.
5. **Five documented keepers, one harness.** The skill metrics are
   properties of this keeper distribution; a different one would move
   them.
6. **The dossier's condition H** (full minus HMM) is not in scope here —
   `hidden_mood_hmm` exists and was judged in D6.

## Verification

RED — the pins, written before the module existed:

```powershell
PS> python -B -m unittest test_candidate_learner_ablation   # (from labs/micro_threads)
  File "labs\micro_threads\test_candidate_learner_ablation.py", line 31, in <module>
    from thread_fleet import (  # noqa: E402
    ...<12 lines>...
    )
ImportError: cannot import name 'CANDIDATE_THREAD_NAMES' from 'thread_fleet' (labs\micro_threads\thread_fleet.py)


----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

GREEN, and the whole micro_threads lab with it (the D6 suite must pass
unchanged — it is the incumbent contract):

```powershell
PS> python -B -m unittest test_candidate_learner_ablation
----------------------------------------------------------------------
Ran 38 tests in 0.731s

OK

PS> python -B -m unittest discover -s labs/micro_threads -p "test_*.py"
----------------------------------------------------------------------
Ran 123 tests in 8.855s

OK
```

(The lab total is **85 → 123**, measured rather than quoted. An earlier
draft of this report recorded 121 from a run taken before the last two
byte-identity pins were added — the same class of stale-count error N1
caught in the Phase-M gate's "319", and caught here the same way, by
re-measuring instead of carrying the number forward.)

The byte-identity proof (the committed D6 artifact regenerated at full
scale into a scratch directory and hashed):

```powershell
PS> python -B labs/micro_threads/ablation_gates.py --output-dir <scratch>
PS> python -B <diff script>
committed sha256: 75640475cc9c9fc4cab5f4c4955121e8a2a118672169e5c64acdc5bf17e66f44
regenerated sha256: 75640475cc9c9fc4cab5f4c4955121e8a2a118672169e5c64acdc5bf17e66f44
BYTE-IDENTICAL: True

Every field identical, including all 14 condition welfares
and all 11 thread verdicts.
```

The lab invocation that produced the artifact (the DR 0028 pilot ran
first and projected 555.35 s for the full run; the measured 107.155 s
came in well under, because neglectful and punitive keepers kill their
companions long before the 200-tick ceiling — the projection assumed
full-length lifecycles and is conservative by design):

```powershell
PS> python -B labs/micro_threads/candidate_learner_ablation.py
full vs rules_only 296.653% (>=15%: True); fleet vs frozen 0.965%

CANDIDATES (the dossier's E/F/G):
  E  qtable_policy          KEEP  welfare    0.795%  skill    55.459%  (action_regret_reduction_vs_uniform_random_policy)
  F  tiny_tree_router       DROP  welfare    0.615%  skill    -1.776%  (route_return_improvement_vs_depth1_stump)
  G  bayes_keeper_counter   DROP  welfare    1.194%  skill     2.756%  (next_interaction_brier_reduction_vs_running_rate)

INCUMBENT ELEVEN, re-judged on the new baseline:
  hunger_forecast        welfare    0.359%  meets_bar False
  energy_forecast        welfare    0.018%  meets_bar False
  boredom_novelty        welfare    0.225%  meets_bar False
  attention_forecast     welfare    0.225%  meets_bar False
  interaction_timing     welfare    0.128%  meets_bar False
  animation_bandit       welfare      0.0%  meets_bar False
  hidden_mood_hmm        welfare    0.289%  meets_bar False
  mutation_stability     welfare      0.0%  meets_bar False
  readability            welfare      0.0%  meets_bar False
  slip_compat            welfare      0.0%  meets_bar False
  lineage_survival       welfare      0.0%  meets_bar False

kept 1 / dropped 2 of 3
wrote data/micro_threads/candidate_learner_ablation_stage0.json
```

Wall clock 107.155 s; 23,972 ticks scored for the skill metrics.

The closing sweep:

```powershell
PS> python -B tools/ci/run_sweep.py
lab:animation_system             OK  OK  [10.7s]
lab:architecture                 OK  OK  [19.2s]
lab:asset_pipeline               OK  OK  [0.5s]
lab:cellular_automata            OK  OK  [39.7s]
lab:ctm_ticks                    OK  OK  [0.1s]
lab:cubff_transducer             OK  OK  [0.8s]
lab:datasets                     OK  OK  [3.3s]
lab:game_loop                    OK  OK  [7.9s]
lab:grid_genome                  OK  OK  [9.6s]
lab:lifecycle_sim                OK  OK  [0.5s]
lab:map_elites_archive           OK  OK  [164.9s]
lab:micro_threads                OK  OK  [8.8s]
lab:package_promotion            OK  OK  [0.2s]
lab:readability_benchmark        OK  OK  [3.2s]
lab:repair_boundary              OK  OK  [3.4s]
lab:runtime_integration          OK  OK  [83.5s]
lab:slip_validator               OK  OK  [0.7s]
lab:wfc_grid                     OK  OK  [6.0s]
lab:workshop_editor              OK  OK  [6.2s]
package                          OK  OK  [7.1s]
cli                              OK  OK (skipped=15)  [3.7s]
game                             OK  OK (skipped=5)  [12.5s]
workshop                         OK  <sys>:0: ResourceWarning: unclosed <socket.socket fd=596, family=2, type=1, proto=0, laddr=('127.0.0.1', 8808)>  [176.4s]
data artifacts                   OK  2243 JSON artifacts valid  [8.8s]

SWEEP GREEN
```

The **package** and **game** suites pass unchanged, which matters here:
`mecha_engine.learning` carries its own mirrored copy of the fleet, and
this slice touched only the lab side.

## Sources

- `audits/TODO.md` (cycle 24 N3) · `research/decision_records/0051-micro-learner-conditions-efg.md` (the record this study produced)
- `docs/project-research/deep-research/01/deep-research.md` (the micro-learner ablation: conditions at `:714–724`, the learner matrix at `:647–649`)
- `research/experiment_reports/2026-07-08-phase-d-gate.md` (Phase D — the fleet and the D6 gates this reuses)
- `labs/micro_threads/candidate_learner_ablation.py` (+ `test_candidate_learner_ablation.py`, 38 pins) · `data/micro_threads/candidate_learner_ablation_stage0.json`
- `labs/micro_threads/thread_fleet.py` (the three candidate learners; `FLEET_THREADS` untouched), `ablation_gates.py` (the D6 harness, imported and given additive `fleet_names`/`observer` parameters)
- `data/micro_threads/ablation_gates_stage0.json` (the committed D6 artifact, regenerated byte-identical), `need_predictors_stage0.json`, `animation_bandit_hmm_mood_stage0.json`, `evidence_threads_stage0.json`
- `research/algorithm_cards/micro_learning_switchboard.md`
