# Decision Record 0059: `cleanliness` Earns Its Mechanic — an Opt-In Lifecycle Seam, Every Parameter Derived, Adopted and Landed for Opted-In Covenants

Date: 2026-08-09

## Status

**ACCEPTED** (cycle 26 · ENGINE gate → GAME landing · Phase P, task
P3) — by the five-gate rule pre-registered in
`labs/lifecycle_sim/cleanliness_mechanic_gate.py` before the run, with
the prediction recorded first and confirmed.

- **The cleanliness mechanic is ADOPTED** as the engine's first OPT-IN
  lifecycle mechanic: a need that decays, a keeper `clean` verb that
  answers it, and a bounded dirt→stress consequence — the exact
  MECHANIC gap DR 0048 measured for the documented VISIBLE axis.
- **The seam is byte-identical when off, proven** against the
  committed Stage 0 comparator's own episode numbers and a frozen
  state-key list (never new-vs-new). `__all__` does not widen.
- **The landing ships for opted-in covenants in the same slice**; the
  **default covenant does not enable it**, and that flip is a named
  future record with its cost priced, never a side effect.

## Context

`health` needed a chosen definition (DR 0054); `happiness` needed a
chosen definition (DR 0058); `cleanliness` needed something neither
did — **engine behavior that does not exist**: *"a need, a decay, an
action that answers it, and its interaction with the switchboard
policy and the reward function"* (DR 0048, quoting M5's measurement).
DR 0021's first law forbids displaying an invented number, so no
display work could close this gap. The Stage 0 lifecycle's own cited
care-loop reference (the Tamagotchi Connection manual, in the committed
artifact's `source_refs`) names cleaning as a canonical care category.

## The mechanic, every parameter derived

| parameter | value | derivation |
| --- | --- | --- |
| seed | 1 − mean cell damage | the grid field `grid_stability` already reads |
| decay / tick | **0.0124** | the median incumbent drift magnitude at Stage 0 defaults |
| mutate's mess | **0.055** | mutate's own grid-stability cost |
| clean's restore | **0.32** | feed's own hunger relief — the strongest care effect |
| dirt→stress | **0.01** | the engine's own need→stress coefficient, pointed at dirt |

**What deliberately does not change**: `ACTIONS` (the autonomous
policies never choose `clean` — the companion cannot clean itself, the
same documented interaction model that keeps feeding keeper-mediated);
`TARGETS` / `_need_balance` / `_snapshot` / the reward / `_life_status`
(the incumbent statistics keep their meaning; the mechanic is
**non-lethal**, and a danger threshold for dirt would be a separate
gated decision). `clean` carries no incumbent-axis effects — cleaning
is time spent, not nourishment — and dead states return unchanged,
`clean` included.

## Pre-registered gates and the measured verdict

| gate | question | measured | result |
| --- | --- | --- | --- |
| G1 | does the need decay? | strictly, every live tick | pass |
| G2 | can the keeper move it ≥ the committed 0.0685 floor? | **+0.3076** | pass |
| G3a | is the consequence measurable (noise floor exactly 0)? | neglect stress **+0.00682** | pass |
| G3b | is it bounded (no new death; welfare < the D6 5% bar)? | deaths unchanged; **1.6e-05** | pass |
| G4 | does clean answer? | cleanliness rises | pass |

Failing G3a was pre-registered as **`blocked_on_mechanic`** (the
charter's own refusal — a need nobody can measure is not a need);
failing G3b as **`refuse_as_lethal_cosmetic`** (a cosmetic axis that
kills the pet has outgrown "smallest"), outranking the withholdings.
The instrument reproduced the committed switchboard and idle episodes
and N5's committed keeper floor **before judging**.

**The fairness finding, predicted and confirmed**: an attentive
keeper's care **absorbs the dirt pressure entirely** (care-stream
stress delta exactly 0.0). **Dirt hurts only the neglected** — the
mechanic punishes neglect a little more, a little sooner, and costs an
attentive keeper nothing but the cleaning tick itself.

## Decisions

1. **The mechanic is adopted** at the seam tier: package lifecycle,
   opt-in keyword, contract section appended
   (`mecha_engine_lifecycle_contract_gate.md`), 17 package pins.
2. **The client lands it for opted-in covenants** in the same slice:
   the needs readout (state value verbatim), the `clean` verb, and
   persistence across succession and save/resume. A default session is
   byte-identical to the pre-seam client, pinned.
3. **The default covenant stays off, and the flip is a NAMED future
   record** with two priced costs: the session-built evidence
   artifacts regenerate, and the default play feel changes. Neither
   happens as a side effect.
4. **A SLIP-carried opt-in is the schema ladder's next rung**
   (DR 0012), named, not smuggled — until then the `mechanics` keyword
   is the only author.
5. **`cleanliness` stays outside `need_balance`, the reward, and
   `DANGER_THRESHOLDS`** — the incumbent statistics keep their meaning
   (DR 0053's spirit), and each extension would be its own gate.

## What this record does NOT do

1. It does not enable the mechanic for any default player (decision 3).
2. It does not give the companion a dirt beg-display or an autonomous
   grooming behavior — the switchboard is untouched; whether the
   companion should ask to be cleaned is a covenant/deliberation design
   question.
3. It does not make dirt visible to the welfare statistic or lethal at
   any threshold.
4. It does not extend the SLIP schema (decision 4).

## Sources

- `research/experiment_reports/2026-08-09-cleanliness-mechanic-gate.md` (this record's study)
- `labs/lifecycle_sim/cleanliness_mechanic_gate.py` (+ 19 pins) · `data/lifecycle/cleanliness_mechanic_gate_stage0.json`
- `packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py` · `packages/mecha_engine/tests/test_lifecycle_cleanliness_seam.py` (17 pins) · `research/package_specs/mecha_engine_lifecycle_contract_gate.md`
- `game/src/mecha_game/session.py` · `game/tests/test_cleanliness_mechanic.py` (10 pins)
- `data/lifecycle/lifecycle_stage0.json` (the committed comparator, including the Tamagotchi care-loop source_ref) · `data/architecture/health_definition_gate_stage0.json` (the committed keeper floor)
- `research/decision_records/0048-visible-companion-state-axes.md`, `0021-game-loop.md`, `0053-admission-policy-belongs-at-the-call-site.md`, `0012-slip-schema-extension-ladder.md`
- `docs/project-research/validity-research.md` §1.17 (the P3 dated addendum)
- `sunsetted/TODO.md` (cycle 26 P3)
