# Decision Record 0051: The Micro-Learner Conditions E/F/G — One Kept, Two Dropped, and Nothing Promoted

Date: 2026-07-28

## Status

**ACCEPTED** — by D6's rule applied verbatim, pre-registered in
`labs/micro_threads/candidate_learner_ablation.py` before the run.

- **E `qtable_policy` — KEPT** by the rule (skill +55.459%).
- **F `tiny_tree_router` — DROPPED** (skill −1.776%, welfare 0.615%).
- **G `bayes_keeper_counter` — DROPPED** (skill +2.756%, welfare 1.194%).

**No learner is promoted into the fleet.** A kept candidate has passed
the ablation gate; joining `FLEET_THREADS` is a separate decision that
needs a consumer asking for it.

## Context

The dossier's micro-learner ablation names eight conditions. Phase D
built the eleven-thread fleet and ran A/B/remove-one, keeping five and
dropping six — but **none of the eleven is a Q-table, a tiny decision
tree, or a Bayesian counter**, so conditions **E**, **F** and **G** have
been documented and unmet since **cycle 12**. This is the oldest open
item in the learning track.

Phase D's own result frames the question: D6 measured **every** welfare
removal cost at ~0, because the frozen reactive rules already sit near
the autonomous-behavior welfare optimum and *"the remaining welfare
belongs to the keeper"*. All five kept threads were therefore kept on
their **skill** metric, not on welfare.

## Pre-registered gates

**D6's rule, verbatim — not a new rule invented for the candidates.**
The dossier: *"Keep a learner only if its removal causes at least a 5%
decline in one target metric without improving another more important
metric."* Operationally as D6 applied it: a learner keeps its place on
**EITHER** its welfare removal cost **OR** its own documented skill
metric, at the same 5% bar. `ablation_gates` is **imported, never
re-implemented**.

Each skill baseline follows an existing D6 precedent:

| condition | skill metric | precedent |
| --- | --- | --- |
| E | action-regret reduction vs a uniform random policy | `animation_bandit` |
| F | return improvement vs a **depth-1 stump** | the tree's own simpler self |
| G | next-interaction Brier reduction vs the **running rate** | `attention_forecast` |

**Dropping all three was declared first-class**, and the incumbent
eleven were to be **re-judged** on the new `full_fleet` baseline rather
than assumed unchanged.

**Written down before the run**: the candidates were expected to show
near-zero welfare cost, with their fate resting on skill. The
measurement was free to refute it; it did not.

## Measured verdict

| | learner | decision | welfare | skill |
| --- | --- | --- | --- | --- |
| **E** | `qtable_policy` | **KEEP** | 0.795% | **+55.459%** |
| **F** | `tiny_tree_router` | **DROP** | 0.615% | **−1.776%** |
| **G** | `bayes_keeper_counter` | **DROP** | 1.194% | **+2.756%** |

**Both drops confirm the dossier's own weakness column, with a number
attached:**

- **F — "brittle if overfit".** The depth-2 tree returns **0.799976**
  against the depth-1 stump's **0.814443**: splitting on energy after
  hunger makes the router **worse than not splitting at all**. Measured
  here the failure is dilution rather than overfitting — the leaves are
  thin enough that the second split adds variance without signal.
- **G — "limited expressivity".** Brier **0.190317** against the running
  rate's **0.195712**: a real improvement, in the right direction, and
  **under half the bar**. The uncertainty a Beta posterior carries buys
  2.756% on this question, and nothing in the switchboard consumes the
  uncertainty itself.

**E** is kept on exactly the footing the incumbent five were: a large
skill number (regret 0.015406 vs 0.03459 over 23,972 scored ticks) and a
negligible welfare contribution.

### The kept-five roster is unchanged, and the reason is stated precisely

All eleven incumbents were recomputed against the extended baseline;
every welfare removal cost lands between **0.000% and 0.359%**, all
below the bar, as in D6. The roster is unchanged because the skill
metrics it rests on are read from the D2/D3 artifacts and are
**properties of each thread's own prediction task, not of fleet
composition** — adding threads cannot move them. What adding threads
*could* have moved is the welfare side, and it did not move it across
the bar for anyone.

### One measured change, small and real

`fleet_vs_frozen` moves **−0.054% (D6) → +0.965% (N3)**: the sign flips,
the fleet becoming very slightly *better* than the frozen reactive rules
rather than very slightly worse. It is ~1%, far below any gate, and is
recorded because it is a measured effect of the candidates on the
decision seam — not because it licenses a claim. D6's conclusion stands.

## Decision

**1. Condition E is answered: the Q-table earns its keep by the rule**,
on skill, exactly as the incumbent five do.

**2. Conditions F and G are answered: dropped**, each with a measured
mechanism rather than a shrug, and each confirming the weakness the
dossier predicted for it.

**3. Nothing is promoted.** `FLEET_THREADS` is unchanged. The candidates
ride the same opt-in seam and are off unless explicitly switched on.
Promoting `qtable_policy` into the fleet is a separate record and needs
a consumer that wants it.

**4. Byte-identity is PROVEN, not asserted.** The committed D6 artifact
regenerates at full scale with an identical SHA-256
(`75640475cc9c9fc4cab5f4c4955121e8a2a118672169e5c64acdc5bf17e66f44`) —
all 14 condition welfares and all 11 thread verdicts unchanged. The
off-mode roster is additionally pinned against a **frozen literal list**
rather than a second call to the new code.

**5. The dossier's protocol item is closed** after twelve cycles, with
its conditions answered in the document's own vocabulary (E/F/G carried
as `condition_letter` in the artifact).

## Process deviation, recorded

The first run scored **G at −154.796%** — an artifact of the instrument,
not the learner. `bayes_keeper_counter` observes `recent_interactions`
(`1 if action in {feed, play}` — *whether the executed action was
social*), while the first observer scored it against `override is not
None` (*whether the keeper intervened*). Different events; the learner
was marked wrong on a question it was never asked.

Corrected to the thread's own observable and **re-run**: G moves
**−154.796% → +2.756%**, with **E and F bit-for-bit unchanged** — the
check that the fix touched only the mismatched metric. This is a defect
repair, not a re-score: the rule, the bar and the baselines are exactly
as pre-registered, and **G is dropped either way**.

## What this record does NOT do

1. **It does not promote any learner into the fleet** (see Decision 3).
2. **It does not test E against the incumbent reactive rule.** The
   uniform-random baseline is the `animation_bandit` precedent's shape
   and therefore the documented comparison, but it is a weak opponent:
   *"better than choosing at random in the same bucket"* is a lower bar
   than 55% sounds. The harder comparison is not run here.
   > **Dated note, 2026-08-09 (cycle 26 P4).** Now run, as a new
   > artifact (`data/micro_threads/harder_skill_baselines_stage0.json`)
   > whose collector reproduced this record's committed statistics
   > exactly first. **The Q-table BEATS the incumbent frozen reactive
   > rule by 44.685%** (rule regret 0.027851 vs the Q-table's 0.015406,
   > over the same replayed states, at the same 5% bar) — the harder
   > opponent turned out to be barely harder than uniform (0.0346): the
   > frozen rules are welfare-optimal at the survival level, and their
   > per-tick choices still carry real empirical regret. The P4
   > prediction expected the advantage to collapse and was **refuted**.
   > This record's keep stands unchanged; the roster is unchanged
   > (pre-registered in P4's rule); promotion remains a separate record
   > needing a consumer.
3. **It does not give F a like-for-like baseline.** The depth-1 stump is
   scored on a full-sample argmax while the tree is scored on its
   **online** recommendation — an asymmetry that runs *against* the
   tree. The drop holds at the 5% bar either way, but the −1.776% margin
   should not be read as precise.
   > **Dated note, 2026-08-09 (cycle 26 P4).** Now measured in the same
   > new artifact: against a like-for-like ONLINE stump (per-lifecycle
   > running means, the tree's own cold-start footing) the tree still
   > loses — **−0.744%** — so the asymmetry accounted for roughly 58%
   > of the committed −1.776% gap and the **drop holds like-for-like**,
   > exactly as this record expected its margin not to be read as
   > precise.
4. **It does not revisit the saturated welfare seam.** D6 measured it;
   this reproduces it. A near-zero candidate welfare cost bounds the
   decision seam, not the learner's value.
5. **It does not address condition H** (full minus HMM) —
   `hidden_mood_hmm` exists and was judged in D6.

## Sources

- `research/experiment_reports/2026-07-28-candidate-learner-ablation.md` (this record's study)
- `docs/project-research/deep-research/01/deep-research.md` (conditions at `:714–724`; the learner matrix and its weakness column at `:647–649`)
- `labs/micro_threads/candidate_learner_ablation.py` (+ `test_candidate_learner_ablation.py`, 38 pins) · `data/micro_threads/candidate_learner_ablation_stage0.json`
- `labs/micro_threads/thread_fleet.py` (the three candidates; `FLEET_THREADS` untouched), `ablation_gates.py` (the D6 harness, imported with additive `fleet_names`/`observer` parameters)
- `research/experiment_reports/2026-07-08-phase-d-gate.md` · `data/micro_threads/ablation_gates_stage0.json` (regenerated byte-identical)
- `research/algorithm_cards/micro_learning_switchboard.md`
- `research/decision_records/0028-dependency-and-license-policy.md` (the wall-clock-first discipline)
- `audits/TODO.md` (cycle 24 N3)
