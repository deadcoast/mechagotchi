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


def render_packet_v2(
    grid: dict,
    lifecycle_state: dict | None = None,
    *,
    animation: str | None = None,
    slip_profile: dict | None = None,
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
    """
    # Rung T3.5: the species' visual grammar bounds the vocabulary.
    vocabulary = list(ANIMATION_STATES)
    if slip_profile is not None:
        grammar = slip_profile.get("visual_grammar") or {}
        vocab = grammar.get("animation_vocab")
        if isinstance(vocab, list) and vocab:
            vocabulary = [s for s in ANIMATION_STATES if s in vocab]
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
    return packet
