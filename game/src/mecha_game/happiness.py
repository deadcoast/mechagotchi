"""The `happiness` readout — DR 0058's adopted definition, on screen.

`validity-research.md` §1.17 names `happiness` a VISIBLE companion
state axis and never defines it; M5 measured no engine source and
DR 0048 put the axis out of scope pending a definition. DR 0058 chose
one through a five-gate study (`labs/architecture/
happiness_definition_gate.py`): **`social_warmth`** — the mean of the
engine's own ``recent_interactions`` window, the last-5-tick trace of
keeper care (``1`` when the executed action was ``feed`` or ``play``)
that the lifecycle has carried and the switchboard has consumed since
Stage 0. Happiness as *being tended lately*.

Why this one, in the study's own numbers: both keeper verbs move it
(+0.083333, over the measured 0.0685 floor), relieving a starving
companion raises it (+0.2), a cherished life and a neglected life
separate on it (0.8 vs 0.0) — and **the neglected corpse reads 0.0**,
the strongest honesty property any candidate showed (`bond_rename` was
refused as a duplicate of the shown bond readout; `need_balance` was
withheld under the responsiveness floor, reading 0.65 on the corpse).

**The design property the keeper will actually see**: `play` RAISES
happiness while it LOWERS the health readout — measured in the lab and
pinned live here. The two bars answer different questions (am I being
tended vs how close is trouble), and both tell the truth (DR 0021's
first law).

**The legibility surface is the window itself.** The number can fall
for exactly one reason — the keeper stopped tending — so the readout
carries `tended_ticks` / `window_ticks` (engine truth, no new number,
no invented word) and labels the definition CHOSEN, exactly as the
health readout does (DR 0055's pattern).

**This formula is MIRRORED from the lab, never imported** (boundary
law), and pinned against the committed gate artifact's
`game_mirror_parity_values`, so drift in either direction fails the
suite.
"""

from __future__ import annotations

from statistics import mean


def social_warmth(window: list) -> float:
    """The adopted definition: the mean of the recent-interaction window.

    Mirrored verbatim from the lab gate; ``[]`` reads 0.0 — a companion
    with no recorded care has no warmth to report, and inventing one
    would break DR 0021's first law.
    """
    if not window:
        return 0.0
    return round(mean(float(value) for value in window), 6)


def happiness_readout(state: dict) -> dict:
    """The frame's happiness entry: the number, and why it is that number."""
    window = list(state.get("recent_interactions", []))
    return {
        "label": "happiness",
        "value": social_warmth(window),
        "good_when": "high",
        # DR 0058 adopted this as a CHOSEN definition, not a documented
        # one. The surface says so rather than presenting it as fact
        # (the DR 0055 pattern).
        "definition": "social_warmth",
        "chosen": True,
        # The legibility surface: the window's own counts. `happiness
        # 0.2 (1 of last 5 ticks tended)` turns a fall into a sentence.
        "tended_ticks": sum(1 for value in window if value),
        "window_ticks": len(window),
    }
