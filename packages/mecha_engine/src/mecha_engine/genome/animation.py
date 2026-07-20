"""Animation-state projections and the render packet v2 for mecha_engine.

Contract sources:

- research/decision_records/0013-port-slip-v2-and-packet-v2.md ("Genome
  additive publics": ``ANIMATION_STATES``, ``project_animation_state``,
  ``render_packet_v2`` — verbatim ports of the T4/T16 lab semantics;
  ``render_packet_from_grid`` stays exactly v1)
- research/experiment_reports/2026-07-05-render-packet-v2.md (T16)
- labs/grid_genome/animation_states.py (the verbatim behavior source,
  pinned by ``labs/grid_genome/test_package_animation_parity.py``)

The design decision the lab proved (audit T4): an animation state is a
DETERMINISTIC, VISUAL-ONLY PROJECTION of the base grid — never a
hand-authored extra frame. The grid stays the single source of truth,
every projection preserves cell positions/roles/organs and validator
validity, and ``idle`` is the identity.

Projection semantics (all derived from palette + role, nothing new
authored):

- idle  — identity.
- blink — eye cells take the background color (eyes closed).
- sleep — eye AND mouth cells take the background color (face at rest).
- beg   — mouth cells take the accent color (the palette's last color).
- ill   — body cells on odd (x+y) parity take the accent color (a
  deterministic shiver/glitch pattern); sensory cells unchanged.

``render_packet_v2`` wraps ``render_packet_from_grid`` (packet structure
and validation stay the v1 engine contract) and adds ``animation``,
``mood``, and ``animation_vocabulary`` — the T16 og contract.
"""

from __future__ import annotations

from copy import deepcopy

from .render import render_packet_from_grid

ANIMATION_STATES = ["idle", "blink", "sleep", "beg", "ill"]

# ---------------------------------------------------------------------
# The clip model (cycle 11 C4): animation CLIPS as bounded frame
# sequences over the state projections — a verbatim port of
# labs/animation_system/clip_model.py, pinned by
# labs/animation_system/test_package_clip_parity.py. A clip frame is a
# deterministic, VISUAL-ONLY projection (state track -> all-or-nothing
# whole-body motion -> per-role motion); the genome is never mutated.
# ---------------------------------------------------------------------

CLIP_STATES: dict[str, list[str]] = {
    "idle": ["idle", "idle", "idle", "idle"],
    "blink": ["idle", "blink", "idle"],
    "sleep": ["sleep", "sleep", "sleep", "sleep"],
    "beg": ["beg", "beg", "beg", "beg"],
    "ill": ["ill", "ill", "ill", "ill"],
}

CLIP_BODY_MOTION: dict[str, list[tuple[int, int]]] = {
    "idle": [(0, 0), (0, 0), (0, 0), (0, 0)],
    "blink": [(0, 0), (0, 0), (0, 0)],
    "sleep": [(0, 0), (0, 1), (0, 1), (0, 0)],
    "beg": [(0, 0), (0, -1), (0, -1), (0, 0)],
    "ill": [(0, 0), (-1, 0), (0, 0), (1, 0)],
}

SWAY_ROLES = {"antenna", "sensor"}
CLIP_SWAY: dict[str, list[int]] = {
    "idle": [0, 1, 0, -1],
    "blink": [0, 0, 0],
    "sleep": [0, 0, 0, 0],
    "beg": [0, 1, -1, 0],
    "ill": [0, -1, 1, -1],
}

FLICKER_ROLES = {"effect"}

# Cycle 19 I4 (DR 0037): the DR 0015 WATCH seam's named increment —
# limb/joint/decoration motion, recorded per clip. Amplitudes are the
# LCD unit step (1px at every canvas). Limbs step VERTICALLY and
# joints flex HORIZONTALLY with the column-parity sign rule (even
# column +offset, odd column −offset — the gait / counter-flex read);
# decoration bobs vertically in unison (ornaments shimmer together).
# Every per-cell offset keeps the collision/bounds skip.
LIMB_STEP_ROLES = {"limb"}
JOINT_FLEX_ROLES = {"joint"}
DECOR_BOB_ROLES = {"decoration"}
CLIP_LIMB_STEP: dict[str, list[int]] = {
    "idle": [0, 0, 0, 0],
    "blink": [0, 0, 0],
    "sleep": [0, 0, 0, 0],
    "beg": [0, -1, -1, 0],
    "ill": [0, 1, -1, 1],
}
CLIP_JOINT_FLEX: dict[str, list[int]] = {
    "idle": [0, 0, 0, 0],
    "blink": [0, 0, 0],
    "sleep": [0, 0, 0, 0],
    "beg": [0, 1, -1, 0],
    "ill": [0, -1, 1, -1],
}
CLIP_DECOR_BOB: dict[str, list[int]] = {
    "idle": [0, 1, 0, -1],
    "blink": [0, 0, 0],
    "sleep": [0, 0, 0, 0],
    "beg": [0, -1, -1, 0],
    "ill": [0, 1, -1, 1],
}


def _apply_role_offsets(
    cells: list[dict],
    *,
    roles: set[str],
    offset: int,
    axis: str,
    parity_sign: bool,
    width: int,
    height: int,
) -> None:
    """One per-role pass with the standard collision/bounds skip."""
    if not offset:
        return
    occupied = {(cell["x"], cell["y"]) for cell in cells}
    for cell in cells:
        if cell["role"] not in roles:
            continue
        applied = offset if not parity_sign or cell["x"] % 2 == 0 else -offset
        if axis == "x":
            target = (cell["x"] + applied, cell["y"])
        else:
            target = (cell["x"], cell["y"] + applied)
        if not (0 <= target[0] < width and 0 <= target[1] < height):
            continue
        if target in occupied:
            continue
        occupied.discard((cell["x"], cell["y"]))
        occupied.add(target)
        cell["x"], cell["y"] = target


def clip_names() -> list[str]:
    return sorted(CLIP_STATES)


def clip_frame_count(clip: str) -> int:
    if clip not in CLIP_STATES:
        raise ValueError(f"unknown clip: {clip}")
    return len(CLIP_STATES[clip])


def clip_frame(grid: dict, clip: str, frame_index: int) -> dict:
    """One deterministic frame packet; the grid is never mutated."""
    frame_count = clip_frame_count(clip)
    if not isinstance(frame_index, int) or not 0 <= frame_index < frame_count:
        raise ValueError(
            f"frame_index {frame_index} outside clip {clip} (0..{frame_count - 1})"
        )
    width, height = grid["grid_size"]
    projected = project_animation_state(grid, CLIP_STATES[clip][frame_index])
    cells = deepcopy(projected["cells"])

    dx, dy = CLIP_BODY_MOTION[clip][frame_index]
    if (dx, dy) != (0, 0) and all(
        0 <= cell["x"] + dx < width and 0 <= cell["y"] + dy < height
        for cell in cells
    ):
        for cell in cells:
            cell["x"] += dx
            cell["y"] += dy

    sway = CLIP_SWAY[clip][frame_index]
    if sway:
        occupied = {(cell["x"], cell["y"]) for cell in cells}
        for cell in cells:
            if cell["role"] not in SWAY_ROLES:
                continue
            target = (cell["x"] + sway, cell["y"])
            if not 0 <= target[0] < width or target in occupied:
                continue
            occupied.discard((cell["x"], cell["y"]))
            occupied.add(target)
            cell["x"] = target[0]

    _apply_role_offsets(
        cells,
        roles=LIMB_STEP_ROLES,
        offset=CLIP_LIMB_STEP[clip][frame_index],
        axis="y",
        parity_sign=True,
        width=width,
        height=height,
    )
    _apply_role_offsets(
        cells,
        roles=JOINT_FLEX_ROLES,
        offset=CLIP_JOINT_FLEX[clip][frame_index],
        axis="x",
        parity_sign=True,
        width=width,
        height=height,
    )
    _apply_role_offsets(
        cells,
        roles=DECOR_BOB_ROLES,
        offset=CLIP_DECOR_BOB[clip][frame_index],
        axis="y",
        parity_sign=False,
        width=width,
        height=height,
    )

    if frame_index % 2 == 1:
        cells = [cell for cell in cells if cell["role"] not in FLICKER_ROLES]

    return {
        "grid_id": grid["grid_id"],
        "clip": clip,
        "frame_index": frame_index,
        "frame_count": frame_count,
        "grid_size": deepcopy(grid["grid_size"]),
        "palette": deepcopy(grid["palette"]),
        "cells": cells,
        "anchors": [
            [cell["x"], cell["y"]]
            for cell in cells
            if cell.get("animation_anchor") is True
        ],
    }


def project_animation_state(grid: dict, state: str) -> dict:
    """Project the base grid into one animation state (visual-only)."""
    if state not in ANIMATION_STATES:
        raise ValueError(f"unknown animation state: {state}")
    if state == "idle":
        return grid
    projected = deepcopy(grid)
    colors = projected["palette"]["colors"]
    background = colors[projected["palette"]["background_index"]]
    accent = colors[-1]
    for cell in projected["cells"]:
        role = cell.get("role")
        if state == "blink" and role == "eye":
            cell["visual"] = background
        elif state == "sleep" and role in ("eye", "mouth"):
            cell["visual"] = background
        elif state == "beg" and role == "mouth":
            cell["visual"] = accent
        elif (
            state == "ill"
            and role == "body"
            and (cell["x"] + cell["y"]) % 2 == 1
        ):
            cell["visual"] = accent
    return projected


def select_animation_state(lifecycle_state: dict) -> tuple[str, str]:
    """(animation, mood) from lifecycle state — T16 packet selection.

    Thresholds mirror the lab micro-switchboard's
    ``estimate_hidden_mood`` (labs/grid_genome/micro_switchboard.py:
    energy 0.2 / hunger 0.65 / stress 0.65) so mood and animation always
    agree; blink is a deterministic periodic tic (every fifth tick) in
    the curious band.
    """
    energy = lifecycle_state.get("energy", 0.5)
    hunger = lifecycle_state.get("hunger", 0.5)
    stress = lifecycle_state.get("stress", 0.0)
    if energy < 0.2:
        return "sleep", "tired"
    if hunger > 0.65:
        return "beg", "hungry"
    if stress > 0.65:
        return "ill", "stressed"
    if lifecycle_state.get("age_ticks", 0) % 5 == 0 and lifecycle_state.get(
        "age_ticks", 0
    ) > 0:
        return "blink", "curious"
    return "idle", "curious"


def packet_effects(
    lifecycle_state: dict | None, selected: str
) -> tuple[list[str], dict, dict]:
    """The retro effects declaration + ui_hints (cycle 11 C5).

    Renderer-neutral (DR 0026: consumers rasterize, the engine never
    does): the documented list shape rides ``effects``, deterministic
    parameters ride ``effect_parameters``, and everything derives from
    engine state. The LCD identity (scanline + lcd_ghosting) is always
    on; glitch rides the ill display with its amplitude tied to the
    engine's own stress number; crt_bloom rides the beg display.
    ``ui_hints`` mirror the T16 selection thresholds (hunger 0.65 /
    energy 0.2 / stress 0.65) so icons and animation always agree.
    """
    stress = (lifecycle_state or {}).get("stress", 0.0)
    hunger = (lifecycle_state or {}).get("hunger", 0.0)
    energy = (lifecycle_state or {}).get("energy", 1.0)
    effects = ["scanline", "lcd_ghosting"]
    parameters: dict[str, dict] = {
        "scanline": {"period": 2, "opacity": 0.12},
        "lcd_ghosting": {"alpha": 0.35},
    }
    if selected == "beg":
        effects.append("crt_bloom")
        parameters["crt_bloom"] = {"radius": 1, "intensity": 0.3}
    if selected == "ill":
        effects.append("glitch")
        parameters["glitch"] = {
            "amplitude": round(max(0.25, min(1.0, stress)), 6)
        }
    ui_hints = {
        "show_hunger_icon": hunger > 0.65,
        "show_sleep_icon": energy < 0.2,
        "show_attention_ping": stress > 0.65 or hunger > 0.65,
    }
    return effects, parameters, ui_hints


def render_packet_v2(
    grid: dict,
    lifecycle_state: dict | None = None,
    *,
    animation: str | None = None,
    slip_profile: dict | None = None,
    clip: str | None = None,
    frame_index: int | None = None,
) -> dict:
    """Render packet v2 (audit T16): the og contract as a package surface.

    animation + mood ride the packet; cells carry the SELECTED state's
    projected visuals (T4 semantics). Explicit ``animation`` overrides the
    lifecycle selection (previewer use). ``render_packet_from_grid`` stays
    exactly v1; this builder wraps it, so packet structure and validation
    stay the engine's — invalid grids raise through the v1 gate.

    ``slip_profile`` (cycle 05 E1 — the T3.5 visual-grammar gate promoted
    verbatim from ``labs/grid_genome/animation_states.build_render_packet_v2``,
    pinned by ``labs/grid_genome/test_package_animation_parity.py``): the
    species' ``visual_grammar.animation_vocab`` bounds the vocabulary, and
    a selected state outside it falls back to a DISPLAYED ``idle`` while
    ``mood`` stays honest (a hunger-driven ``beg`` on a species with no
    beg shows idle + mood hungry). ``None`` is byte-identical to the
    pre-E1 package contract (full vocabulary, no fallback).

    ``clip``/``frame_index`` (cycle 11 C4 — the documented animation
    contract, a DR 0013 additive rung): when a clip is requested, the
    packet's ``animation`` field becomes the dossier's BLOCK
    (``{"clip", "frame_index", "frame_count", "anchors"}``) and the
    packet's ``cells`` are the clip FRAME's cells (state projection plus
    motion). Validation stays on the projected grid (positions
    preserved); the moved frame is presentation applied after the v1
    gate. Clip names are the state names, so the same vocabulary gate
    bounds them (an out-of-vocab clip displays the ``idle`` clip; mood
    stays honest). ``frame_index`` defaults to 0. ``clip=None`` is
    byte-identical to the pre-C4 contract.
    """
    # Rung T3.5: the species' visual grammar bounds the vocabulary.
    vocabulary = list(ANIMATION_STATES)
    if slip_profile is not None:
        grammar = slip_profile.get("visual_grammar") or {}
        vocab = grammar.get("animation_vocab")
        if isinstance(vocab, list) and vocab:
            vocabulary = [s for s in ANIMATION_STATES if s in vocab]

    if clip is not None:
        # Rung C4: the documented clip contract.
        if clip not in CLIP_STATES:
            raise ValueError(f"unknown clip: {clip}")
        selected_clip = clip if clip in vocabulary else "idle"
        index = 0 if frame_index is None else frame_index
        frame = clip_frame(grid, selected_clip, index)
        mood = None
        if lifecycle_state is not None:
            _, mood = select_animation_state(lifecycle_state)
        projected = project_animation_state(
            grid, CLIP_STATES[selected_clip][index]
        )
        packet = render_packet_from_grid(projected, lifecycle_state)
        packet["cells"] = deepcopy(frame["cells"])
        packet["animation"] = {
            "clip": selected_clip,
            "frame_index": index,
            "frame_count": frame["frame_count"],
            "anchors": frame["anchors"],
        }
        packet["mood"] = mood
        packet["animation_vocabulary"] = vocabulary
        effects, parameters, ui_hints = packet_effects(
            lifecycle_state, selected_clip
        )
        packet["effects"] = effects
        packet["effect_parameters"] = parameters
        packet["ui_hints"] = ui_hints
        return packet

    if animation is not None:
        if animation not in ANIMATION_STATES:
            raise ValueError(f"unknown animation state: {animation}")
        selected, mood = animation, None
        if lifecycle_state is not None:
            _, mood = select_animation_state(lifecycle_state)
    elif lifecycle_state is not None:
        selected, mood = select_animation_state(lifecycle_state)
    else:
        selected, mood = "idle", None
    if selected not in vocabulary:
        # Mood stays honest; the DISPLAYED state falls back to idle.
        selected = "idle"
    projected = project_animation_state(grid, selected)
    packet = render_packet_from_grid(projected, lifecycle_state)
    packet["animation"] = selected
    packet["mood"] = mood
    packet["animation_vocabulary"] = vocabulary
    effects, parameters, ui_hints = packet_effects(lifecycle_state, selected)
    packet["effects"] = effects
    packet["effect_parameters"] = parameters
    packet["ui_hints"] = ui_hints
    return packet
