# Decision Record 0060: The Q-Table's Consumer Seam — Adopted Opt-In, the Bar Cleared, and the Default-Fleet Promotion Chartered as Its Own Record

Date: 2026-08-09

## Status

**ACCEPTED** (cycle 27 · ENGINE track · Phase Q, task Q1) — by the rule
pre-registered in `labs/micro_threads/qtable_consumer_gate.py` before
the run, with the prediction recorded first and **REFUTED in the
strong direction**.

- **The consumer seam is ADOPTED, opt-in, at the lab tier**: the
  switchboard's `qtable_consumer` learning switch (explicit `True`,
  the D1 rule) follows the kept `qtable_policy` thread's
  recommendation whenever the thread itself reports full confidence
  (its own committed `QTABLE_CONFIDENT_VISITS = 12`; no new constant).
  Byte-identical off, pinned against the committed scenarios artifact
  on every run of the gate.
- **The measured verdict: `ADOPT_INTO_DEFAULT_CANDIDATE`** — welfare
  **+7.355%** over the incumbent `full_fleet` condition at the
  committed budget, over the documented D6 5% bar: **the first
  D6-style welfare clearance the learning track has ever produced at
  the decision seam** (the whole fleet's additive contribution
  measured +0.965%).
- **The default-fleet promotion is CHARTERED as its own record, not
  taken here** — the N5 → O1 pattern. It carries package work (the
  promoted switchboard, the game's fleet, parity pins) and one design
  question this record names and refuses to smuggle: **the follower
  begs more** (+236 beg ticks, answered at +243 keeper feeds).

## Context

DR 0051 kept `qtable_policy` on skill and said promotion *"needs a
consumer asking for it."* P4 then measured the consumer argument: the
frozen reactive rule's per-tick choices carry 0.027851 empirical
regret against the Q-table's 0.015406 — a 44.685% advantage entering
the decision only as one diluted nudge among ~15 threads. D6's
standing lesson said the decision seam's welfare was near-saturated;
the pre-run prediction inherited it and expected
`eligible_not_promoted`.

## Pre-registered gates and the measured verdict

| gate | question | measured | result |
| --- | --- | --- | --- |
| G0 | instruments before verdicts (committed scenarios parsed-equal; committed `full_fleet` welfare/per-keeper/survival exact) | reproduced | pass |
| G2 | does the consumer fire? | **59.4%** of ticks (73.8% agreement — ~1 tick in 6 changed) | pass |
| G3 | the D6 rule verbatim at the 5% bar | **+7.355%** (0.187712 → 0.201518) | **adopt_into_default_candidate** |

**The mechanism, measured per keeper — the gain belongs to the good
keeper.** Attentive: 0.727579 → **0.796586** (+0.069, with +2.58 mean
survival ticks overall). Exploratory, neglectful, punitive: unchanged
to the sixth decimal — their companions die near tick 11, the table
never reaches its 12-visit floor, the consumer never fires, and those
trajectories are byte-identical. **The consumer amplifies good keeping
and cannot rescue neglect.** The extra begs are part of the mechanism
(the pet asks at the right times; the good keeper answers) and are
recorded, never gated here.

**What D6's saturation lesson actually was**: a property of additive
DILUTION, not of the seam. The same signal that nudges for +0.965%
steers for +7.355% when followed at full confidence. D6's committed
numbers stand untouched — they measured the blended fleet; this
measures a follower.

## Decisions

1. **The seam ships, opt-in, lab-tier** — `micro_switchboard.py`'s
   `QTABLE_CONSUMER_SWITCH` + the harness's additive
   `qtable_consumer` condition; off unless explicitly switched on;
   nothing deletes or weakens the incumbent rule.
2. **The eligibility verdict is recorded as measured** — and it is
   eligibility ONLY (pre-registered): this artifact adopts no default.
3. **The default-fleet promotion is the NAMED next task** with its own
   record, carrying: the package switchboard seam + parity pins, the
   game fleet wiring, regeneration of every invalidated artifact with
   deltas explained — and **the beg design question decided on the
   record** (a default companion that begs ~3.6% more is a product
   behavior change, not a free win).
4. **A graded (confidence-weighted) follower is a different consumer**
   with its own gate — named, not attempted.
5. **DR 0051's roster verdicts stand**; this record supplies the
   consumer DR 0051 said a promotion needs, and the promotion itself
   remains the next record's act.

## What this record does NOT do

1. It does not change the default fleet, the promoted switchboard, or
   any package surface.
2. It does not decide the beg design question — it prices it.
3. It does not measure a graded follower, other seed corpora, other
   keeper models, or other budgets (N3's inherited frame).

## Sources

- `research/experiment_reports/2026-08-09-qtable-consumer-gate.md` (this record's study)
- `labs/grid_genome/micro_switchboard.py` (the seam) · `labs/micro_threads/ablation_gates.py` (the condition) · `labs/micro_threads/qtable_consumer_gate.py` (+ 20 pins) · `data/micro_threads/qtable_consumer_gate_stage0.json`
- `data/micro_learners/switchboard_stage0.json` · `data/micro_threads/candidate_learner_ablation_stage0.json` (the committed instruments)
- `research/experiment_reports/2026-08-09-harder-skill-baselines.md` (P4) · `2026-07-28-candidate-learner-ablation.md` (N3) · `2026-07-08-ablation-gates.md` (D6)
- `research/decision_records/0051-micro-learner-conditions-efg.md`
- `sunsetted/TODO.md` (cycle 27 Q1)
