# Experiment Report: The Documented Visible Companion State — Two of the Five "Gaps" Were Already on Screen (Cycle 23 · GAME · M5)

Date: 2026-07-27

## WHY

`validity-research.md` §1.17 names eight **VISIBLE** companion state
axes — *hunger, happiness, energy, cleanliness, mood, age, health, bond*
— and eight **HIDDEN** ones, including `stress` and `grid stability`.

The Phase-K gate's survey, re-verified at the Phase-L gate and carried
into `audits/TODO.md`, `ONBOARDING.md`, `CLAUDE.md` and `CHANGELOG.md`,
recorded that **five of the eight visible axes have no engine field** —
`happiness`, `cleanliness`, `mood`, `age`, `health` — and called it *the
largest documented player-facing gap in the repo*. It became cycle 23's
one deliberate GAME-track slice.

M5's charter was explicit: **survey each axis honestly *before* building
anything**, decide per axis by DR, and **never invent a number for a
player** (DR 0021's first law).

## WHAT

An instrument that **measures, rather than asserts**. Every disposition
is obtained by building a real lifecycle state from a committed seed
creature and calling the real engine functions through the package
boundary. A survey that read a document and reported what the document
said would reproduce exactly the error it exists to correct.

Dispositions fixed in advance, with **`absent` first-class** — a survey
that cannot report a gap is not a survey:

- `lifecycle_field` — the engine carries it as state;
- `derived_engine_value` — the engine computes it from state it carries;
- `absent` — no engine source; **no value reported, none invented**.

## FINDINGS

### The claim is overstated: three gaps, not five

```text
documented visible axes, measured against the live engine:
  hunger       lifecycle_field        0.374
  happiness    absent                 —
  energy       lifecycle_field        0.68
  cleanliness  absent                 —
  mood         derived_engine_value   curious
  age          lifecycle_field        0
  health       absent                 —
  bond         lifecycle_field        0.6075

prior claim: 5 absent (happiness, cleanliness, mood, age, health)
measured   : 3 absent (happiness, cleanliness, health)
```

- **`age` is a lifecycle field.** `initial_state` sets `age_ticks: 0`,
  `advance_tick` increments it every tick (measured: +1), `run_episode`
  reports it as `survival_ticks`, and the lineage browser records
  `died_age_ticks`. **The game already displays it** —
  `game/src/mecha_game/app.py:316`, `session.py:149`.
- **`mood` is a derived engine value.** `select_animation_state` returns
  `(animation, mood)` — `tired` / `hungry` / `stressed` / `curious` —
  and has since Phase C. **The game already displays it** —
  `app.py:316`, `session.py:156`.

**The earlier survey counted lifecycle *homeostasis fields*, which is a
narrower question than "has an engine field".** Two axes that are engine
truth, and are already on the player's screen, were recorded as missing.

This is the third overstated claim this cycle has caught — after M1's
understated L4 remainder and M4's stale 52-vs-54 family count — and like
both of those it was found by **reading the engine instead of the
prose**.

### The three real gaps are three *different kinds* of gap

That distinction is the substantive result, and it is why "build a
visible-state panel" would have been the wrong move:

1. **`happiness` — no definition exists.** No field, no derivation, and
   no formula anywhere: the documentation names the axis and never
   defines it. `bond` is a *separate* documented axis, not a synonym.
   Any happiness number today is invented.
2. **`cleanliness` — no MECHANIC exists.** The action set is
   `(feed, play, sleep, idle, mutate)` — **there is no clean action** —
   and no state accumulates dirt. This is not a display gap: it needs a
   need, a decay, an action that answers it, and its interaction with
   the switchboard policy and the reward function. Treating it as a
   missing field would understate it by an order of magnitude.
3. **`health` — definable, but only as a CHOSEN definition.**
   `grid_stability` and per-cell `damage` both exist and both move under
   the lifecycle. But **both are documented HIDDEN axes** by §1.17's own
   split, so surfacing either *as* health promotes a hidden axis to a
   visible one — a documentation change, not an engine one — and any
   composite needs weights nobody documented.

### The decision (DR 0048): nothing is built, and that is the finding

`happiness` and `cleanliness` are **out of scope** — one pending a
documented definition, one pending a mechanic with its own record.
`health` is **withheld pending its own gate**, on the L4 precedent: a
record that declares its definition CHOSEN, states which hidden axes it
reads, and gates it — *including* on whether a player-facing "health"
that is really grid-stability is honest labelling or a euphemism.

The charter said survey before building. The survey's answer is that two
axes needed no work at all, and the remaining three each need a
different kind of work. **Building the panel would have invented two
numbers and mislabelled a third.**

## HONEST REMAINDERS

1. **`health` is withheld, not refused.** It is the one axis with a real
   engine source, and it is the obvious next record.
2. **The game-side display of `age` and `mood` is cited by file
   reference, not measured by this lab.** Importing the game from a lab
   would cross the boundary law, so those two lines are verified by
   reading rather than by test. A game-side pin asserting the snapshot
   carries both would close that, and belongs to the game suite.
3. **The survey measures one seed creature's initial state.** It
   establishes that the fields and derivations *exist*; it is not a
   claim about their ranges or their behaviour over a life.
4. **The documented HIDDEN axes were not surveyed.** The Phase-L gate
   noted they need a per-axis survey of their own — some exist under
   other names on other surfaces — and that is still true and still
   untasked.

## Verification

```powershell
PS> python -B -m unittest test_companion_state_survey   # (from labs/architecture)
ModuleNotFoundError: No module named 'companion_state_survey'      # RED
...
PS> python -B -m unittest test_companion_state_survey
Ran 13 tests in 0.166s

OK

PS> python -B labs/architecture/companion_state_survey.py
documented visible axes, measured against the live engine:
  hunger       lifecycle_field        0.374
  happiness    absent                 —
  energy       lifecycle_field        0.68
  cleanliness  absent                 —
  mood         derived_engine_value   curious
  age          lifecycle_field        0
  health       absent                 —
  bond         lifecycle_field        0.6075

prior claim: 5 absent (happiness, cleanliness, mood, age, health)
measured   : 3 absent (happiness, cleanliness, health)
wrote data/architecture/companion_state_survey_stage0.json
```

## Sources

- `audits/TODO.md` (cycle 23 M5) · `research/decision_records/0048-visible-companion-state-axes.md` (the record this study produced)
- `docs/project-research/validity-research.md` §1.17 (the eight visible and eight hidden axes)
- `labs/architecture/companion_state_survey.py` (+ `test_companion_state_survey.py`, 13 pins) · `data/architecture/companion_state_survey_stage0.json`
- `packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py` (`initial_state`, `advance_tick`, `age_ticks`, `survival_ticks`) · `genome/animation.py` (`select_animation_state`) · `lifecycle/_policy.py` (`ACTIONS` — no clean action)
- `game/src/mecha_game/app.py`, `session.py`, `lineage.py` (age and mood already displayed)
- `research/experiment_reports/2026-07-26-phase-l-gate.md` (remainder 7 — the claim this corrects, now carrying a dated note). The Phase-K gate is where the survey originated but its report does not state the count, so it carries no note; the propagated copies live in `audits/TODO.md`, `ONBOARDING.md`, `CLAUDE.md` and `CHANGELOG.md`, which are live state documents and are updated directly
- `research/decision_records/0021-game-loop.md` (the engine-truth first law), `0041-eleven-class-regrowth-head.md` (the withholding precedent)
