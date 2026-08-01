# Decision Record 0054: `health` Is `danger_margin` — and `grid_stability` Under That Name Is REFUSED as a Euphemism

Date: 2026-07-28

## Status

**ACCEPTED.** DR 0048's withholding of `health` is resolved by the gate
it named.

- **`danger_margin` — ADOPTED** as the CHOSEN definition of `health`.
- **`grid_stability` under the name "health" — REFUSED as a euphemism**,
  on the measurement, not on taste.
- **Nothing is put on the player's screen yet**, and the blocker is
  named and small.

## Context

`validity-research.md` §1.17 names `health` a VISIBLE axis. M5 found no
engine field for it. DR 0048 withheld rather than refused, and specified
the gate: declare the definition **CHOSEN**, state which HIDDEN axes it
reads, and decide *"whether a player-facing 'health' that is really
grid-stability is honest labelling or a euphemism."*

## Pre-registered gates

Four, with refusal reachable for every candidate (pinned), and a
prediction recorded before the run (DR 0045's precedent).

- **G1** — the definition declares which documented-HIDDEN axes it reads.
- **G2** — the **keeper** can move it, judged against what the *player*
  can do (`feed`, `play`), against a **MEASURED** bar: the smallest
  response any existing VISIBLE axis shows to those same verbs.
- **G3** — deaths and survivors separate on it.
- **G4 — the label test.** Put the creature in distress, have the keeper
  relieve it, measure whether the bar rises. Failing G4 earns
  `refuse_as_euphemism` — deliberately a **different and harsher**
  verdict than the `withhold` a structural failure earns, because they
  are different accusations.

## Measured verdict

Measured floor: **0.0685**.

| candidate | keeper response (feed / play) | distress relief | survivors vs deaths | verdict |
| --- | --- | --- | --- | --- |
| `grid_stability` | −0.001 / −0.001 | **−0.001** | 0.998 vs 0.927 | **refuse_as_euphemism** |
| `danger_margin` | +0.021333 / −0.075467 | **+0.176** | 0.845333 vs **0.0** | **adopt** |

### The number the refusal rests on

> The neglected creature **starved to death** (`hunger` 1.0,
> `death_cause: starvation`, tick 11) and finished with
> **`grid_stability` at 0.927**.

A "health" bar reading that axis shows **93% on a corpse**, and ticks
**down** while the keeper feeds a starving companion. The signal is not
weak, it is **inverted** — which is why this is a refusal rather than a
withholding.

`grid_stability` technically passed G3, and that pass is instructive
rather than exculpatory: a 0.07 gap between 0.998 and 0.927 looks like
separation in a table while reading 93% at the moment of death. The
gate's other three questions are what caught it.

## Decision

**1. `health` is defined as `danger_margin`** — the minimum normalised
safety margin across the engine's own `DANGER_THRESHOLDS`. The
definition is **CHOSEN** and says so: §1.17 names the axis and never
defines it. It reads the documented-HIDDEN axes `stress` and
`grid_stability` (plus the visible `hunger`, `energy`, `bond`), and it
**introduces no weight that is not already an engine threshold** — a
minimum has no weights at all, which is precisely the objection DR 0048
raised against a composite.

**2. `grid_stability` may not be shown as "health".** It stays visible
under its own accurate name. The refusal is against *renaming*, not
against *showing*.

**3. The refusal is an enforced property, not a paragraph.** Five pins
in `game/tests/test_health_label_guard.py` assert that
`grid_stability` keeps its accurate label and that **nothing on the
player's screen carries the name "health"** until a consumer change
lands one.

**4. The definition is NOT on screen, and the blocker is concrete.**
`danger_margin` reads `DANGER_THRESHOLDS`, a **public name in a public
module that is not in `mecha_engine`'s `__all__`**. A game depending on
it would depend on a surface the package has not promised. **Promoting
that constant to the public API is a package change with its own spec
update and gate** — the next step, and a small one.

## Reported beside the verdict, deliberately outside it

**The game already got this right.** `session.py` displays
`grid_stability` as **"body stability"** — it never committed the
euphemism. It also already displays `stress`. **Both are documented
HIDDEN axes**, so the shipped client surfaces two "hidden" axes under
accurate names and **§1.17's visible/hidden split no longer describes
it**. Found by reading the client rather than the document; recorded,
not amended, because amending §1.17 is its own documentation decision.

**`play` lowers `danger_margin`** (−0.075467), because play costs energy
and adds hunger. Honest, and a real design question — a keeper who sees
"health" drop when they play with their pet will read it as a bug.
**Whoever puts this on screen owns that**, and this record does not
answer it.

## Process note

Candidate B was drafted as `lethal_margin` and **renamed mid-study to
`danger_margin`**: `DANGER_THRESHOLDS` carries five axes and one of them
(`bond`) is not a lethal condition. A gate whose subject is whether a
label overstates what it measures may not ship a definition whose own
name overstates what it measures.

## Honest limits

- **Two distinct trajectories, not six** — the arms are deterministic
  over one seed grid, so the three lifecycles per arm are identical
  repeats. G3's *n* is 2.
- One seed creature, no SLIP profile.
- `happiness` and `cleanliness` remain OUT OF SCOPE (DR 0048).

## Sources

- `research/experiment_reports/2026-07-28-health-definition-gate.md` (this record's study)
- `research/decision_records/0048-visible-companion-state-axes.md` (the withholding this resolves), `0021-game-loop.md`, `0041-eleven-class-regrowth-head.md`, `0045-density-as-pressure.md`
- `labs/architecture/health_definition_gate.py` (+ `test_health_definition_gate.py`, 25 pins) · `data/architecture/health_definition_gate_stage0.json`
- `game/tests/test_health_label_guard.py` (5 pins) · `game/src/mecha_game/session.py`
- `packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py`
- `docs/project-research/validity-research.md` §1.17
- `audits/TODO.md` (cycle 24 N5)
