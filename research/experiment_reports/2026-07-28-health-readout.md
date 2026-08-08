# Experiment Report: `health` Reaches the Player's Screen — and the Fix for the Play-Drop Was Not to Hide It (Cycle 25 · GAME · O2)

Date: 2026-07-28

## WHY

DR 0054 adopted **`danger_margin`** as the CHOSEN definition of the
documented VISIBLE axis `health`, shipped only a guard, and deferred one
question to whoever put the bar on screen:

> `play` **LOWERS** `danger_margin` (−0.075467, because play costs
> energy and adds hunger), so a keeper who sees "health" drop when they
> play with their pet will read it as a bug. **Whoever puts this on
> screen owns that design question**, and it is not answered here.

O1 removed the API blocker. O2 lands the readout and answers the
question.

## WHAT

**The keeper has two verbs and one of them lowers the number:**

| keeper does | hunger | energy | → health |
| --- | --- | --- | --- |
| **feed** | −0.280 | −0.018 | **+0.021** |
| **play** | +0.075 | −0.098 | **−0.075** |

Three ways to handle that, and two are forbidden by DR 0021's first law:
**smoothing** the number or **hiding** the drop would both make the
surface show something the engine does not.

**The answer is to show the BINDING AXIS beside the number.** Health is
a *minimum* across axes, and a bare minimum throws away the one thing
that makes it legible: *which* axis is binding. `health 0.62 (tired)`
costs no new number — the axis is the argmin of margins already
computed — is engine truth, and turns an unexplained fall into a
sentence: *playing made them tired, and tired is what is closest to
trouble.*

**Pre-registered, with refusal first-class**: if the drop were **not**
explained by the axis named after it, the player would still see an
unexplained fall and the readout would mislead — so that is a pin, not
an assumption:

```python
if after < before:
    self.assertIn(binding_axis(after_state), ("energy", "hunger"))
```

## FINDINGS

### The readout predicts the death cause, by name, eight ticks early

A keeper rotating feed / idle / play — never sleeping — in the live
client:

```text
tick  health  binding      keeper does
   1  0.509   lonely       -
   2  0.419   tired        play
   3  0.288   tired        feed
   4  0.264   tired        -
   5  0.133   tired        play
   6  0.003   tired        feed
   7  0.000   tired        -
   ...
ValueError: the companion died of energy_collapse at tick 10
```

**The bar said `tired` from tick 2 and the companion died of
`energy_collapse` at tick 10.** A bare number would have shown a falling
line; the binding word named the cause, and named the verb that would
have fixed it, eight ticks before it happened.

### A keeper who reads the word thrives — same creature, same engine

```text
tick  health  binding      keeper does
   0  0.487   lonely       play
   1  0.410   hungry       feed
   2  0.419   tired        sleep
   3  0.593   lonely       play
   ...
  14  0.976   tired        sleep
  15  0.914   hungry       feed
```

Acting on whatever the word says takes health **0.487 → 0.976** and
keeps the companion alive and rising, against a death at tick 10 for the
keeper who ignored it. **The readout is actionable, which is the whole
case for it.**

### The play-drop, visible and legible in the live client

Tick 8 → 9 in that same run: the keeper plays at 0.813, health falls to
0.715, and the word reads **`tired`**. That is the exact
DR 0054 scenario — and the drop explains itself on screen rather than
reading as a bug. The gate that could have refused this did not fire,
because the axis named after the drop is one play actually worsens.

## HONEST REMAINDERS

1. **The bar bottoms out at DANGER, not at death.** Health reads `0.000`
   for several ticks while the companion is still alive (ticks 7–10
   above), because the floor is the engine's danger threshold, not its
   death condition. This is defensible — a warning bar that hits zero
   and still leaves you time to act is a *warning*, which is the point —
   but the word "health" implies zero means dead, and it does not.
   **Recorded, not fixed**; changing it would mean choosing a different
   floor, which is a new CHOSEN definition and needs its own gate.
2. **The formula is MIRRORED into the game, not imported from the lab**
   (the boundary law). It is pinned against
   `data/architecture/health_definition_gate_stage0.json` — the
   committed evidence DR 0054 rests on — so drift in either direction
   fails the suite. That artifact is data, not a lab import.
3. **`bond` is in the thresholds and is not lethal.** A companion can
   read `lonely` at its minimum while in no danger of dying. The word is
   honest about the axis; it is not a mortality forecast.
4. **One seed creature, one covenant.** The binding-word behaviour is a
   property of the engine's action model, which is profile-independent,
   but a profile with different behaviour weights would change which
   axis binds most often.
5. **The N5 guard still holds**: `grid_stability` keeps its own accurate
   name ("body stability"), and health is a separate derived readout
   that does not rename it — pinned.

## Verification

RED — the pins, written before the module existed:

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_health_readout.py"
ModuleNotFoundError: No module named 'mecha_game.health'

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```

GREEN, and the whole game suite with the readout wired into the frame
and the footer:

```powershell
PS> uv run python -B -m unittest discover -s game/tests -p "test_health_readout.py"
----------------------------------------------------------------------
Ran 12 tests in 0.006s

OK

PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
----------------------------------------------------------------------
Ran 200 tests in 17.165s

OK
```

Game suite **188 → 200**. The two live-client runs above are the
verification that it renders, not only that it passes.

## Sources

- `audits/TODO.md` (cycle 25 O2) · `research/decision_records/0055-health-readout-binding-axis.md` (the record this study produced)
- `research/decision_records/0054-health-definition-danger-margin.md` (the adopted definition and the deferred design question), `0021-game-loop.md` (the engine-truth first law)
- `research/experiment_reports/2026-07-28-danger-thresholds-promotion.md` (O1 — the API this reads), `2026-07-28-health-definition-gate.md` (N5)
- `game/src/mecha_game/health.py` (the mirrored formula + the binding axis) · `session.py` (the frame entry) · `app.py` (the footer)
- `game/tests/test_health_readout.py` (12 pins), `test_health_label_guard.py` (N5's guard, still holding)
- `data/architecture/health_definition_gate_stage0.json` (the committed evidence the mirror is pinned against)
- `packages/mecha_engine/src/mecha_engine/lifecycle/__init__.py` (`DANGER_THRESHOLDS`, promoted by O1)
