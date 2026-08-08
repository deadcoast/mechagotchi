"""The `health` readout — DR 0054's adopted definition, on screen.

`validity-research.md` §1.17 names `health` a VISIBLE companion state
axis and never defines it. DR 0054 adopted **`danger_margin`** as the
**CHOSEN** definition — the minimum normalised safety margin across the
engine's own `DANGER_THRESHOLDS` — after **refusing `grid_stability`
under that name as a euphemism**: a creature that starved to death
finished with `grid_stability` at 0.927, so a bar reading that axis
would have shown **93% on a corpse**.

**Why a minimum, and not a blend.** DR 0048 rejected a composite health
score because *"any composite needs weights nobody documented"*. A
minimum has no weights at all — only the engine's published thresholds,
promoted to the public API by cycle 25 O1 so this module reads a surface
the package actually promises.

**The design question DR 0054 left for this consumer, and its answer.**
The keeper has two verbs, and one of them *lowers* the number:

    feed  ->  health +0.021   (hunger relieved)
    play  ->  health -0.075   (energy spent, appetite raised)

A keeper who clicks "play" and watches health fall will call it a bug.
The answer is **not** to smooth the number or hide the drop — both would
break DR 0021's first law. It is to **show the binding axis beside it**.

Health is a minimum, and a bare minimum throws away the one thing that
makes it legible: *which* axis is binding. `health 0.62 — tired` costs
no new number (the axis is the argmin of margins already computed), is
engine truth, and turns an unexplained fall into a sentence a player can
read: playing made them tired, and tired is what is closest to trouble.

**This formula is MIRRORED into the game, never imported from a lab** —
the boundary law. It is pinned against
`data/architecture/health_definition_gate_stage0.json`, the committed
evidence DR 0054 rests on, so drift in either direction fails the suite.
"""

from __future__ import annotations

from mecha_engine.lifecycle import DANGER_THRESHOLDS

# Rising toward the threshold is the dangerous direction for these; for
# every other axis it is falling toward it. Both readings come from the
# engine's own state semantics, not from a tuned preference.
_RISING_IS_DANGEROUS = ("hunger", "stress")

# What the player reads instead of an axis name. Each describes the
# state the axis is IN when it is the one closest to trouble — never a
# friendlier word for it (DR 0054's refusal applies to this table too).
BINDING_AXIS_WORDS = {
    "hunger": "hungry",
    "energy": "tired",
    "stress": "stressed",
    "bond": "lonely",
    "grid_stability": "unstable",
}


def _margins(state: dict, thresholds: dict | None = None) -> dict:
    thresholds = DANGER_THRESHOLDS if thresholds is None else thresholds
    margins: dict[str, float] = {}
    for axis, threshold in thresholds.items():
        value = float(state[axis])
        if axis in _RISING_IS_DANGEROUS:
            room = threshold if threshold > 0 else 1.0
            margins[axis] = (threshold - value) / room
        else:
            room = 1.0 - threshold if threshold < 1.0 else 1.0
            margins[axis] = (value - threshold) / room
    return margins


def danger_margin(state: dict, thresholds: dict | None = None) -> float:
    """How close to trouble the companion is, on its WORST axis.

    Higher is safer. Clamped to ``[0, 1]``: past a danger threshold the
    reading is 0, which is the honest floor — "in trouble" has no
    degrees below itself on this scale.
    """
    margins = _margins(state, thresholds)
    return round(max(0.0, min(1.0, min(margins.values()))), 6)


def binding_axis(state: dict, thresholds: dict | None = None) -> str:
    """The axis the minimum came from — what makes the number legible."""
    margins = _margins(state, thresholds)
    return min(margins, key=lambda axis: margins[axis])


def health_readout(state: dict, thresholds: dict | None = None) -> dict:
    """The frame's health entry: the number, and why it is that number."""
    axis = binding_axis(state, thresholds)
    return {
        "label": "health",
        "value": danger_margin(state, thresholds),
        "good_when": "high",
        "binding_axis": axis,
        "binding_word": BINDING_AXIS_WORDS.get(axis, axis),
        # DR 0054 adopted this as a CHOSEN definition, not a documented
        # one. The surface says so rather than presenting it as fact.
        "definition": "danger_margin",
        "chosen": True,
    }
