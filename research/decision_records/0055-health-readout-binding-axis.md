# Decision Record 0055: The `health` Readout Ships With Its Binding Axis — the Play-Drop Is Explained, Not Hidden

Date: 2026-07-28

## Status

**ACCEPTED.** `health` is on the player's screen, as
`danger_margin` (DR 0054's adopted CHOSEN definition) **shown with the
axis that binds it**.

DR 0054's deferred design question is answered: the drop stays, and the
readout is given what it needs to explain itself.

## Context

DR 0054 adopted `danger_margin` as the definition of the documented
VISIBLE axis `health`, refused `grid_stability` under that name as a
euphemism, shipped only a guard, and deferred one question:

> `play` **LOWERS** `danger_margin` (−0.075467, because play costs
> energy and adds hunger), so a keeper who sees "health" drop when they
> play with their pet will read it as a bug. **Whoever puts this on
> screen owns that design question.**

O1 promoted `DANGER_THRESHOLDS` to the package API, removing the
blocker. O2 lands the readout.

## The decision

**1. The drop ships, unmodified.** Smoothing the number or hiding the
fall would make the surface show something the engine does not, which
DR 0021's first law forbids. Playing with a tired companion really does
move it closer to trouble.

**2. The readout shows the BINDING AXIS beside the number.** Health is a
*minimum* across axes; a bare minimum discards the one thing that makes
it legible — *which* axis is binding. `health 0.62 (tired)` costs no new
number (the axis is the argmin of margins already computed), is engine
truth, and converts an unexplained fall into a sentence: *playing made
them tired, and tired is what is closest to trouble.*

**3. The binding word names the state, never a friendlier version of
it.** `hungry` / `tired` / `stressed` / `lonely` / `unstable`. DR 0054's
refusal was against renaming an axis into something more comfortable;
that constraint applies to this table too.

**4. The formula is MIRRORED into the game, never imported from a lab**
(the boundary law), and pinned against
`data/architecture/health_definition_gate_stage0.json` — the committed
evidence DR 0054 rests on, which is data rather than a lab import — so
drift in either direction fails the suite.

**5. Refusal was reachable and did not fire.** The gate pins that a drop
must be explained by the axis named after it; had the drop named an axis
`play` does not worsen, the readout would have misled and would not have
shipped.

## The measured case for it

**The readout predicts the death cause, by name, eight ticks early.** A
keeper rotating feed / idle / play and never sleeping:

```text
tick  health  binding      keeper does
   2  0.419   tired        play
   6  0.003   tired        feed
   7  0.000   tired        -
   ... died of energy_collapse at tick 10
```

**A keeper who acts on the word thrives on the same creature**: health
**0.487 → 0.976** over sixteen ticks, against a death at tick 10 for the
keeper who ignored it. And the play-drop itself is visible and legible
in that run — tick 8 plays at 0.813, tick 9 reads 0.715 and says
`tired`.

**The number alone would have shown a falling line. The number plus the
word says what is wrong and which button fixes it.**

## Honest limits

- **The bar bottoms out at DANGER, not at death.** Health reads `0.000`
  while the companion is still alive, because the floor is the engine's
  danger threshold rather than its death condition. Defensible — a
  warning that hits zero and still leaves time to act is a warning — but
  the word "health" implies zero means dead, and it does not. **Recorded
  rather than fixed**: a different floor is a different CHOSEN
  definition and needs its own gate.
- **`bond` is in the thresholds and is not lethal**, so a companion can
  read `lonely` at its minimum while in no danger of dying. The word is
  honest about the axis; it is not a mortality forecast.
- One seed creature, one covenant.

## Consequences

- Game suite **188 → 200**. The N5 label guard still holds:
  `grid_stability` keeps its accurate name and health is a separate
  derived readout that does not rename it.
- **Phase O's premise is half discharged**: of the three things Phase N
  adopted and left off-screen, `health` is now in front of a player. The
  `slip_admission` default remains prospective by design (DR 0053), and
  O3 is the task that moves its headline numbers.

## Sources

- `research/experiment_reports/2026-07-28-health-readout.md` (this record's study)
- `research/decision_records/0054-health-definition-danger-margin.md` (the adopted definition and the deferred question), `0021-game-loop.md` (engine truth), `0053-admission-policy-belongs-at-the-call-site.md`
- `research/experiment_reports/2026-07-28-danger-thresholds-promotion.md` (O1 — the promoted API this reads)
- `game/src/mecha_game/health.py`, `session.py`, `app.py` · `game/tests/test_health_readout.py` (12 pins), `test_health_label_guard.py`
- `data/architecture/health_definition_gate_stage0.json` (the mirror's parity anchor)
- `audits/TODO.md` (cycle 25 O2)
