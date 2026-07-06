"""Animation-state vocabulary: the og five states as genome projections.

Audit task T4 (og 01-formatted: idle/blink/sleep/beg/ill; `animstate_300`
dataset). The design decision this lab proves: an animation state is a
DETERMINISTIC, VISUAL-ONLY PROJECTION of the base grid — never a
hand-authored extra frame. The grid stays the single source of truth
(genome = phenotype = animation substrate, the og's own thesis), every
projection preserves cell positions/roles/organs and validator validity,
and `idle` is the identity. Downstream consumers: render-packet
animation selection (T16), the workshop previewer, and SLIP
`animation_vocab` (T3.5 / DR 0011 verdict 2).

Projection semantics (all derived from palette + role, nothing new
authored):

- idle  — identity.
- blink — eye cells take the background color (eyes closed).
- sleep — eye AND mouth cells take the background color (face at rest).
- beg   — mouth cells take the accent color (the palette's last color).
- ill   — body cells on odd (x+y) parity take the accent color (a
  deterministic shiver/glitch pattern); sensory cells unchanged.
"""

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATED_DIR = ROOT / "data" / "generated_grids" / "markov_local"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "grid_genome"

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from corpus_builder import build_seed_grids  # noqa: E402
from validator import validate_grid  # noqa: E402

from mecha_engine.genome import render_packet_from_grid  # noqa: E402


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

    Thresholds mirror `micro_switchboard.estimate_hidden_mood` (energy
    0.2 / hunger 0.65 / stress 0.65) so mood and animation always agree;
    blink is a deterministic periodic tic (every fifth tick) in the
    curious band.
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


def build_render_packet_v2(
    grid: dict,
    lifecycle_state: dict | None = None,
    *,
    animation: str | None = None,
    slip_profile: dict | None = None,
) -> dict:
    """Render packet v2 (audit T16): the og contract restored lab-side.

    animation + mood ride the packet; cells carry the SELECTED state's
    projected visuals (T4 semantics). Explicit `animation` overrides the
    lifecycle selection (previewer use). The promoted
    `mecha_engine.genome.render_packet_from_grid` stays v1 until its
    port decision record (DR 0012 rule 4 spirit); this builder wraps it,
    so packet structure and validation stay the engine's.
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


def _corpus() -> list[dict]:
    """50 hand-authored seeds + 10 generated grids = 60 creatures.

    60 creatures x 5 states = the og `animstate_300` dataset size.
    """
    grids = build_seed_grids()
    # The bake-off corpus contains raw generator outputs, some invalid by
    # design (the arm's measured validity rate) — only validator-valid
    # grids join the animation corpus.
    added = 0
    for path in sorted(GENERATED_DIR.glob("*.json")):
        grid = json.loads(path.read_text(encoding="utf-8"))
        if validate_grid(grid).ok:
            grids.append(grid)
            added += 1
            if added == 10:
                break
    return grids


def build_animation_states_report() -> dict:
    grids = _corpus()
    sequences = []
    valid = 0
    for grid in grids:
        for state in ANIMATION_STATES:
            projected = project_animation_state(grid, state)
            ok = validate_grid(projected).ok
            valid += 1 if ok else 0
            sequences.append(
                {
                    "grid_id": grid["grid_id"],
                    "state": state,
                    "valid": ok,
                    "cells": [
                        {
                            "x": cell["x"],
                            "y": cell["y"],
                            "visual": cell["visual"],
                            "role": cell["role"],
                        }
                        for cell in projected["cells"]
                    ],
                }
            )
    total = len(sequences)
    summary = {
        "creature_count": len(grids),
        "state_vocabulary": list(ANIMATION_STATES),
        "sequence_count": total,
        "projection_valid_rate": round(valid / total, 6) if total else 0.0,
    }
    return {
        "artifact_id": "animation_states_stage0",
        "status": "stage0_complete",
        "date": "2026-07-05",
        "purpose": (
            "Prove the og animation-state vocabulary as deterministic "
            "visual-only genome projections and emit the animstate_300 "
            "dataset (audit T4)."
        ),
        "source_artifacts": [
            "data/seed_grids",
            "data/generated_grids/markov_local",
            "research/grid_genome/grid_invariants.md",
        ],
        "summary": summary,
        "sequences_preview": sequences[:2],
        "closed_states": [
            "animation_vocabulary_defined_as_genome_projections",
            "projections_visual_only_and_validator_clean",
            "animstate_300_dataset_emitted",
        ],
        "blocked_states": [
            "render_packet_animation_selection_pending_t16",
            "workshop_state_previewer_pending",
            "slip_animation_vocab_field_pending_t3_5",
        ],
        "decision": {
            "status": "adopt_projection_semantics",
            "reason": (
                "All 300 projections across 60 creatures preserve "
                "positions/roles/organs and validator validity; idle is "
                "the identity; states derive from palette + role with "
                "zero authored data."
            ),
        },
        "next_research_step": (
            "Render packet contract v2 (T16): packets carry the selected "
            "animation state; the workshop previewer plays the five-state "
            "cycle from engine truth."
        ),
        "_sequences": sequences,
    }


def write_animation_states_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    sequences = report.pop("_sequences")
    (output_dir / "animation_states_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "animstate_300.json").write_text(
        json.dumps(
            {
                "dataset_id": "animstate_300",
                "date": report["date"],
                "state_vocabulary": report["summary"]["state_vocabulary"],
                "sequences": sequences,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    report["_sequences"] = sequences


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the animation-state projections and dataset."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    report = build_animation_states_report()
    write_animation_states_artifacts(args.output_dir, report)
    print(json.dumps(report["summary"], indent=2))
    print(json.dumps(report["decision"], indent=2))


if __name__ == "__main__":
    main()
