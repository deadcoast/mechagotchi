# Experiment Report: `health` — a Definition Adopted, a Euphemism Refused, and the Game Was Already Right (Cycle 24 · GAME · N5)

Date: 2026-07-28

## WHY

`validity-research.md` §1.17 names `health` a **VISIBLE** companion
state axis. M5 measured that the engine has no `health` field, and
DR 0048 **withheld** it rather than refusing it, naming the gate it
needed:

> *"a record that declares its definition **CHOSEN**, states which
> hidden axes it reads, and gates it — including on whether a
> player-facing 'health' that is really grid-stability is **honest
> labelling or a euphemism**."*

N5 is that gate, and the euphemism question is answered with a
measurement rather than a judgement.

## WHAT

**Two candidates**, because DR 0048's named one need not be the best one:

- **A — `grid_stability`**: surface the documented HIDDEN axis under the
  visible name. Engine truth, moves under the lifecycle, and one of the
  four lethal conditions (`grid_collapse` at ≤ 0.05).
- **B — `danger_margin`**: the **minimum** normalised safety margin
  across the engine's own `DANGER_THRESHOLDS`. DR 0048 rejected a
  composite because *"any composite needs weights nobody documented"* —
  **a minimum has no weights at all.**

**Both are declared CHOSEN up front** (the L4 precedent): §1.17 names
the axis and never defines it.

**Four gates, pre-registered.** G1 the definition declares which hidden
axes it reads. G2 the **keeper** can move it — judged against what the
*player* can do (`feed`, `play`), against a **measured** bar: the
smallest response any existing VISIBLE axis shows to those same verbs.
G3 deaths and survivors separate on it. **G4 — the label test**: put the
creature in distress, have the keeper relieve it, and measure whether
the bar rises. Failing G4 earns `refuse_as_euphemism`, deliberately a
harsher and *different* verdict from the `withhold` a structural failure
earns.

**A prediction was recorded before the run** (DR 0045's precedent):
`grid_stability` would fail G2 and G4; `danger_margin` would pass.

## FINDINGS

Measured floor (G2's bar): **0.0685** — `bond`'s response to the
keeper's verbs, the smallest among hunger 0.2799, energy 0.098, bond
0.0685.

| candidate | keeper response (feed / play) | distress relief | survivors vs deaths | verdict |
| --- | --- | --- | --- | --- |
| `grid_stability` | **−0.001 / −0.001** | **−0.001** | 0.998 vs 0.927 | **REFUSE_AS_EUPHEMISM** (G2, G4) |
| `danger_margin` | +0.021333 / −0.075467 | **+0.176** | 0.845333 vs **0.0** | **ADOPT** |

**The prediction is confirmed.**

### The number that settles it

> The neglected creature **starved to death** — `hunger` 1.0,
> `death_cause: starvation`, at tick 11 — and finished with
> **`grid_stability` at 0.927**.

A "health" bar reading that axis would have shown **93% on a corpse**.
And feeding a starving creature moves it **−0.001**: the bar ticks
*down* while the keeper is saving the creature's life. That is not a
weak signal, it is an inverted one, and it is why the verdict is
`refuse_as_euphemism` rather than merely `withhold`.

`grid_stability` did pass G3 — survivors 0.998 against deaths 0.927 —
but that separation is an artefact, not a signal: **both readings are
high**, and the deaths were starvations that the axis never noticed.
Passing a survival gate on a 0.07 gap while reading 93% at the moment of
death is exactly the kind of number that would look defensible in a
table and mislead a player on screen.

`danger_margin` by contrast reads **0.0** on the dead creature and
**0.845** on the survivor, and rises **+0.176** when the keeper feeds a
starving companion.

### The game already got this right — and §1.17 is out of date with it

Checking the shipped client rather than the document:
`game/src/mecha_game/session.py` **already displays `grid_stability`**,
labelled **"body stability"**. The game never committed the euphemism;
it surfaced the axis under a name that describes it.

It also already displays `stress`. **Both are documented HIDDEN axes**
by §1.17's split — so the shipped game surfaces two "hidden" axes under
accurate names, and §1.17's visible/hidden split no longer describes the
client. That is a documentation gap this study found by reading the
engine instead of the document, and it is recorded rather than fixed
here: amending §1.17 is a documentation change with its own decision.

**This reframes what N5 could usefully ship.** The refusal is not a
warning about something the game does — it is a guard on something the
game currently does *right* and could lose. So what ships is the guard:
five pins in `game/tests/test_health_label_guard.py` asserting that
`grid_stability` keeps its accurate label and that **nothing on the
player's screen carries the name "health"** until a record adopts a
definition and a consumer change lands it.

### A self-correction, for the reason this study exists

Candidate B was drafted as **`lethal_margin`** and renamed mid-study to
**`danger_margin`**. `DANGER_THRESHOLDS` carries **five** axes and one
of them — `bond` — is **not** a lethal condition; only `hunger`,
`energy`, `stress` and `grid_stability` appear in `_life_status`.

A gate whose entire subject is whether a label overstates what it
measures cannot ship a definition whose own name overstates what it
measures. Recorded here rather than quietly fixed.

## HONEST REMAINDERS

1. **The adopted definition is NOT on the player's screen, and the
   blocker is concrete.** `danger_margin` reads
   `DANGER_THRESHOLDS`, which is a **public name in a public module but
   is not in `mecha_engine`'s `__all__`**. A game that depended on it
   would be depending on a surface the package has not promised.
   Promoting that constant to the public API is a **package change with
   its own spec update and gate** — named, not smuggled. That is the
   next step, and it is small.
2. **`play` LOWERS `danger_margin`** (−0.075467), because play costs
   energy and adds hunger. That is honest — playing with a tired
   companion really does reduce its safety margin — but a keeper who
   sees a "health" bar drop when they play with their pet will read it
   as a bug. **Whoever puts this on screen owns that design question**,
   and it is not answered here.
3. **Two distinct trajectories, not six.** The run reports three
   lifecycles per arm, but the arms are deterministic policies over one
   seed grid, so all three are identical repeats. G3 rests on **one**
   neglect run and **one** care run. The separation is stark
   (0.845 vs 0.0), but its *n* is 2, and reporting it as 6 would be
   dressing up a repeat as evidence.
4. **One seed creature, no SLIP profile.** The action model measured is
   profile-independent, but a profile with different behaviour weights
   would move the magnitudes.
5. **`happiness` and `cleanliness` stay OUT OF SCOPE** (DR 0048): one
   needs a definition, the other a mechanic.
6. **§1.17's visible/hidden split is stale** against the shipped game
   (see above) — recorded, not amended.

## Verification

RED — the pins, written before the module existed:

```powershell
PS> python -B -m unittest test_health_definition_gate   # (from labs/architecture)
    from health_definition_gate import (  # noqa: E402
    ...<9 lines>...
    )
ModuleNotFoundError: No module named 'health_definition_gate'


----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

GREEN, and the game suite carrying the new guard:

```powershell
PS> python -B -m unittest test_health_definition_gate
----------------------------------------------------------------------
Ran 25 tests in 0.090s

OK

PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
----------------------------------------------------------------------
Ran 188 tests in 12.887s

OK
```

The lab invocation that produced the artifact:

```powershell
PS> python -B labs/architecture/health_definition_gate.py
keeper verbs: ['feed', 'play']
incumbent visible-axis responses to those verbs: {'hunger': 0.2799, 'energy': 0.098, 'bond': 0.0685} -> measured floor 0.0685

  grid_stability
    keeper response {'feed': -0.001, 'play': -0.001}  distress relief -0.001
    survivors [0.998, 0.998, 0.998]  deaths [0.927, 0.927, 0.927]  separates True
    -> REFUSE_AS_EUPHEMISM  (failed G2_keeper_responsive,G4_honest_label)
  danger_margin
    keeper response {'feed': 0.021333, 'play': -0.075467}  distress relief 0.176
    survivors [0.845333, 0.845333, 0.845333]  deaths [0.0, 0.0, 0.0]  separates True
    -> ADOPT

adopted: ['danger_margin']
wrote data/architecture/health_definition_gate_stage0.json
```

## Sources

- `audits/TODO.md` (cycle 24 N5) · `research/decision_records/0054-health-definition-danger-margin.md` (the record this study produced)
- `research/decision_records/0048-visible-companion-state-axes.md` (the withholding this resolves and the gate it named), `0021-game-loop.md` (the engine-truth first law), `0041-eleven-class-regrowth-head.md` and `0045-density-as-pressure.md` (the withholding and pre-run-prediction precedents)
- `research/experiment_reports/2026-07-27-companion-state-survey.md` (M5)
- `labs/architecture/health_definition_gate.py` (+ `test_health_definition_gate.py`, 25 pins) · `data/architecture/health_definition_gate_stage0.json`
- `game/tests/test_health_label_guard.py` (5 pins — the refusal made an enforced property) · `game/src/mecha_game/session.py` (`NEED_DISPLAY`, where the game already labels the axis honestly)
- `packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py` (`DANGER_THRESHOLDS`, `_life_status`, `ACTION_EFFECTS`)
- `docs/project-research/validity-research.md` §1.17 (the visible/hidden split, now measurably stale against the shipped game)
