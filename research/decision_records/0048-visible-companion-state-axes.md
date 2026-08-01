# Decision Record 0048: The Documented Visible Companion State — Three Gaps, Not Five, and Each Dispositioned Separately

Date: 2026-07-27

## Status

**ACCEPTED.** The survey's correction stands, and each remaining axis is
dispositioned. **No engine field is added and no number is invented.**

## Context

`validity-research.md` §1.17 names eight **VISIBLE** companion state
axes — *hunger, happiness, energy, cleanliness, mood, age, health, bond*
— and eight **HIDDEN** ones, including `stress` and `grid stability`.

The Phase-K gate's survey, re-verified at the Phase-L gate and carried
into `audits/TODO.md`, `ONBOARDING.md` and `CHANGELOG.md`, recorded:

> Five of the eight documented VISIBLE companion state axes have no
> engine field — `happiness`, `cleanliness`, `mood`, `age` and `health`
> — the largest documented player-facing gap in the repo.

M5's charter was to **survey each axis honestly before building
anything**. Measured against the live engine
(`labs/architecture/companion_state_survey.py`), the claim is
**overstated**.

## The correction

| axis | disposition | evidence |
| --- | --- | --- |
| hunger | `lifecycle_field` | 0.374 |
| happiness | **absent** | — |
| energy | `lifecycle_field` | 0.68 |
| cleanliness | **absent** | — |
| **mood** | **`derived_engine_value`** | **`curious`** |
| **age** | **`lifecycle_field`** | **`age_ticks`** |
| health | **absent** | — |
| bond | `lifecycle_field` | 0.6075 |

- **`age` is a lifecycle field.** `initial_state` sets `age_ticks: 0`,
  `advance_tick` increments it every tick, `run_episode` reports it as
  `survival_ticks`, and the lineage browser records `died_age_ticks`.
  **The game already displays it** (`game/src/mecha_game/app.py:316`,
  `session.py:149`).
- **`mood` is a derived engine value.** `select_animation_state` returns
  `(animation, mood)` — `tired` / `hungry` / `stressed` / `curious` —
  and has since Phase C. **The game already displays it**
  (`app.py:316`, `session.py:156`).

**The earlier survey counted lifecycle *homeostasis fields*, which is a
narrower question than "has an engine field".** Two axes that are engine
truth, and are already on the player's screen, were recorded as gaps.

**The real gap is three axes, not five** — and it is not the largest
player-facing gap in the repo on this evidence, because two of the five
were never gaps.

## Decision, per remaining axis

**1. `happiness` — OUT OF SCOPE pending a documented definition.**

There is no engine source: no field, no derivation, and no formula
anywhere in the documentation, which names the axis and never defines
it. `bond` is a *separate* documented axis and is not a synonym. Any
happiness number the engine produced today would be invented, which
DR 0021's first law forbids. **Not built.** It becomes available the day
a definition is documented, or the day a record proposes one and gates
it as CHOSEN (the L4 precedent).

**2. `cleanliness` — OUT OF SCOPE; it needs a MECHANIC, not a field.**

This is the important distinction and the reason it is not a quick win.
The lifecycle's action set is `(feed, play, sleep, idle, mutate)` —
**there is no clean action** — and no state accumulates dirt. Adding
cleanliness is not exposing something the engine knows; it is adding a
need, a decay, an action that answers it, and its interaction with the
switchboard policy and the reward function. That is a **design decision
with its own record**, and pretending it is a display gap would
understate it by an order of magnitude. **Not built.**

**3. `health` — DEFINABLE, but the definition would be CHOSEN, so it is
WITHHELD pending its own gate.**

Unlike the other two, health *is* derivable from engine truth:
`grid_stability` and per-cell `damage` both exist and both move under
the lifecycle. But:

- **both are documented HIDDEN axes** by §1.17's own split, so surfacing
  either *as* health would promote a hidden axis to a visible one — a
  documentation change, not an engine one; and
- **any composite needs weights nobody documented.** A health bar
  blending stability and damage on invented coefficients is precisely
  the class of number DR 0021 forbids.

So health is **withheld, not refused**: the honest path is a record that
declares its definition **CHOSEN** (exactly as L4 did for
`animation_density`), states which hidden axes it reads, and gates it —
including on whether a player-facing "health" that is really
grid-stability is *honest labelling* or a euphemism. **Not built here.**

> **Dated note, 2026-07-28 — RESOLVED by cycle 24 N5 (DR 0054), and the
> euphemism question is answered: it IS a euphemism.** The gate was
> built as named. **`grid_stability` under the name "health" is
> REFUSED**, on the decisive measurement that a creature which
> **starved to death** finished with `grid_stability` at **0.927** — a
> bar reading that axis shows **93% on a corpse** — and that feeding a
> starving companion moves it **−0.001**, i.e. *down*. An inverted
> signal, not a weak one. **`health` is instead ADOPTED as
> `danger_margin`**, the minimum normalised safety margin across the
> engine's own `DANGER_THRESHOLDS`, which answers this record's own
> objection: a composite would need undocumented weights, and **a
> minimum has no weights at all**. Also found, by reading the client
> rather than the document: **the game never committed the euphemism** —
> it already displays the axis as *"body stability"* — and it already
> shows `stress` too, so **§1.17's visible/hidden split is stale against
> the shipped game**. Nothing is on screen yet: `danger_margin` reads a
> constant not in the package's `__all__`, and promoting it is a package
> change with its own gate. See
> `research/experiment_reports/2026-07-28-health-definition-gate.md`.

## Consequences

- **The Phase-K/L claim is corrected by a dated note beside the
  original**, never rewritten: `age` and `mood` are engine truth and
  were already on screen.
- **Nothing was built, and that is the finding.** The charter said
  "survey each honestly before building"; the survey's result is that
  two axes needed no work and the remaining three each need a *different
  kind* of work — a definition, a mechanic, and a gated CHOSEN
  definition respectively. Building a "visible state" panel over them
  would have invented two numbers and mislabelled a third.
- **No proxy is substituted anywhere**, and no absent axis carries a
  value in the artifact (pinned).
- The documented **hidden** axes are untouched: `stress` and
  `grid_stability` stay hidden, which is what stops "health" being
  solved by renaming.

## Sources

- `research/experiment_reports/2026-07-27-companion-state-survey.md` (this record's study)
- `labs/architecture/companion_state_survey.py` (+ `test_companion_state_survey.py`, 13 pins) · `data/architecture/companion_state_survey_stage0.json`
- `docs/project-research/validity-research.md` §1.17 (the eight visible and eight hidden axes)
- `packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py` (`initial_state`, `advance_tick`, `age_ticks`) · `genome/animation.py` (`select_animation_state`) · `lifecycle/_policy.py` (`ACTIONS` — no clean action)
- `game/src/mecha_game/app.py`, `session.py`, `lineage.py` (age and mood already displayed)
- `research/experiment_reports/2026-07-26-phase-l-gate.md` (remainder 7 — the claim this corrects, now carrying a dated note; the Phase-K gate originated the survey but does not state the count, so it carries no note)
- `research/decision_records/0021-game-loop.md` (the engine-truth first law), `0026-render-packet-disposition.md`, `0041-eleven-class-regrowth-head.md` (withholding precedent), `0044-covenant-budget-workshop-face.md`
- `audits/TODO.md` (cycle 23 M5)
