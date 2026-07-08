"""The clip model: animation CLIPS over the promoted state projections
(cycle 11 C1, gap-analysis Phase C).

What exists is five single-frame STATE projections (idle/blink/sleep/
beg/ill — deterministic visual-only recolorings, promoted in
``mecha_engine.genome.animation``). What the documents specify is an
animation SYSTEM: clips with frames, anchors, and transitions, carried
by the render packet as ``{"clip", "frame_index", "anchors"}``. This lab
extends the SAME proven thesis one axis further — a clip frame is a
DETERMINISTIC, VISUAL-ONLY PROJECTION of the base grid, never a
hand-authored extra frame and never a genome mutation:

    frame(clip, i) = per-role motion( whole-body motion(
                        state projection(grid, CLIP_STATES[clip][i]) ) )

- **State track** (per clip, per frame): which promoted projection the
  frame wears — blink is [idle, blink, idle]; sleep sleeps throughout.
- **Whole-body motion**: an (dx, dy) translation per frame — the
  LCD-style bob/hop/shiver. ALL-OR-NOTHING: if any cell would leave the
  canvas, the translation is skipped for that frame (a creature at the
  edge breathes in place; deterministic per creature, no deformation).
- **Per-role motion** (the DR 0015 WATCH seam, recorded per role, never
  improvised): antenna/sensor cells sway horizontally; effect cells
  flicker (hidden on odd frames). A per-cell offset is skipped when its
  target is out of bounds or occupied (no overlaps, no deformation).

Frames mirror the render packet's cell shape (full cell dicts with
transformed x/y and the projection's visuals) plus the ``anchors`` list
the dossier's packet example carries. The packet integration itself is
C4 (an additive DR 0013 rung); this lab proves the model.
"""

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
for path in [GRID_GENOME, PACKAGE_SRC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from mecha_engine.genome import project_animation_state  # noqa: E402


REPORT_DATE = "2026-07-08"
ARTIFACT_ID = "clip_model_stage0"

# Per-frame state track: which promoted projection each frame wears.
CLIP_STATES: dict[str, list[str]] = {
    "idle": ["idle", "idle", "idle", "idle"],
    "blink": ["idle", "blink", "idle"],
    "sleep": ["sleep", "sleep", "sleep", "sleep"],
    "beg": ["beg", "beg", "beg", "beg"],
    "ill": ["ill", "ill", "ill", "ill"],
}

# Whole-body translation per frame (dx, dy); all-or-nothing per frame.
CLIP_BODY_MOTION: dict[str, list[tuple[int, int]]] = {
    "idle": [(0, 0), (0, 0), (0, 0), (0, 0)],
    "blink": [(0, 0), (0, 0), (0, 0)],
    "sleep": [(0, 0), (0, 1), (0, 1), (0, 0)],
    "beg": [(0, 0), (0, -1), (0, -1), (0, 0)],
    "ill": [(0, 0), (-1, 0), (0, 0), (1, 0)],
}

# Per-role horizontal sway per frame (the DR 0015 WATCH seam: antennae
# and sensor pods move; per-cell, skipped on collision/out-of-bounds).
SWAY_ROLES = {"antenna", "sensor"}
CLIP_SWAY: dict[str, list[int]] = {
    "idle": [0, 1, 0, -1],
    "blink": [0, 0, 0],
    "sleep": [0, 0, 0, 0],
    "beg": [0, 1, -1, 0],
    "ill": [0, -1, 1, -1],
}

# Effect cells flicker: hidden on odd frames (aura breathes).
FLICKER_ROLES = {"effect"}


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


def clip_frames(grid: dict, clip: str) -> list[dict]:
    return [
        clip_frame(grid, clip, index)
        for index in range(clip_frame_count(clip))
    ]


def build_clip_model_report() -> dict:
    from corpus_builder import build_seed_grids_16

    corpus = build_seed_grids_16()
    frames_rendered = 0
    in_bounds = 0
    palette_clean = 0
    untouched = 0
    deltas: list[float] = []
    per_clip_deltas: dict[str, list[float]] = {clip: [] for clip in clip_names()}
    for grid in corpus:
        pristine = json.loads(json.dumps(grid))
        legal_colors = set(grid["palette"]["colors"])
        width, height = grid["grid_size"]
        for clip in clip_names():
            frames = clip_frames(grid, clip)
            for previous, current in zip(frames, frames[1:]):
                delta = _frame_delta(previous, current)
                deltas.append(delta)
                per_clip_deltas[clip].append(delta)
            for frame in frames:
                frames_rendered += 1
                if all(
                    0 <= cell["x"] < width and 0 <= cell["y"] < height
                    for cell in frame["cells"]
                ):
                    in_bounds += 1
                if all(
                    cell["visual"] in legal_colors for cell in frame["cells"]
                ):
                    palette_clean += 1
        if json.loads(json.dumps(grid)) == pristine:
            untouched += 1

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "Prove the clip model (cycle 11 C1): animation CLIPS as bounded "
            "frame sequences over the promoted state projections — state "
            "track + all-or-nothing whole-body motion + per-role motion "
            "(the DR 0015 WATCH seam) — every frame a deterministic "
            "visual-only projection, the genome never touched, measured "
            "over the full 16x16 corpus."
        ),
        "source_artifacts": [
            "packages/mecha_engine/src/mecha_engine/genome/animation.py",
            "labs/grid_genome/animation_states.py",
            "data/seed_grids_16x16",
            "research/decision_records/0015-dormant-vocabulary-coverage.md",
            "research/decision_records/0024-grid-schema-animation-species-resolution.md",
        ],
        "metrics": {
            "corpus_size": len(corpus),
            "clips": {
                clip: clip_frame_count(clip) for clip in clip_names()
            },
            "frames_rendered": frames_rendered,
            "frames_in_bounds_rate": round(in_bounds / frames_rendered, 6),
            "frames_palette_clean_rate": round(
                palette_clean / frames_rendered, 6
            ),
            "genome_untouched_rate": round(untouched / len(corpus), 6),
            "intra_clip_delta": {
                "mean_fraction": round(sum(deltas) / len(deltas), 6),
                "max_fraction": round(max(deltas), 6),
                "per_clip_mean": {
                    clip: round(sum(values) / len(values), 6)
                    for clip, values in sorted(per_clip_deltas.items())
                },
            },
        },
        "closed_states": [
            "clip_model_exists_over_the_promoted_projections",
            "frames_are_visual_only_and_deterministic",
            "per_role_motion_recorded_for_antenna_sensor_effect",
        ],
        "blocked_states": [
            "transition_graph_not_built (C2: the >=80% dossier bar)",
            "animstate_300_not_regenerated_as_clip_frames (C3)",
            "packet_clip_contract_not_wired (C4: the DR 0013 additive rung)",
            "per_role_motion_for_limb_joint_decoration_unrecorded (a named future increment of the DR 0015 seam, not improvised here)",
        ],
        "decision": (
            "The clip model holds over the full corpus: every frame in "
            "bounds, palette-clean, genome untouched, and every clip "
            "actually moves. The intra-clip delta table is C2's baseline."
        ),
        "next_research_step": (
            "C2: the transition graph and the measured >=80% transition "
            "validity bar."
        ),
    }


def write_clip_model_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def _frame_delta(previous: dict, current: dict) -> float:
    """Fraction of render positions that differ between two frames."""
    before = {
        (cell["x"], cell["y"]): cell["visual"] for cell in previous["cells"]
    }
    after = {
        (cell["x"], cell["y"]): cell["visual"] for cell in current["cells"]
    }
    positions = set(before) | set(after)
    if not positions:
        return 0.0
    changed = sum(
        1
        for position in positions
        if before.get(position) != after.get(position)
    )
    return changed / len(positions)


def main() -> None:
    parser = argparse.ArgumentParser(description="Clip model lab (cycle 11 C1).")
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "animation_system"
    )
    args = parser.parse_args()
    report = build_clip_model_report()
    write_clip_model_artifacts(args.output_dir, report)
    print(json.dumps(report["metrics"], indent=2))


if __name__ == "__main__":
    main()
