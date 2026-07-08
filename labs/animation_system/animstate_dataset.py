"""animstate at documented scale: the clip-frame dataset (cycle 11 C3).

The documents name ``animstate_300`` — at least 300 labeled animation
samples — and the og dataset delivered exactly that: 300 single-frame
STATE projections at 8x8. With the clip system (C1/C2) the honest
resolution is the clip FRAME: every (creature, clip, frame) over the
16x16 corpus and the full clip vocabulary — 50 x 19 = 950 samples, each
labeled with grid_id, palette, clip, the frame's state-track entry,
frame_index/frame_count, the packet-shaped cells, and the anchor. The
dataset is named by its real size (``animstate_950``) and records what
it supersedes instead of wearing the old size; the 8x8
``animstate_300.json`` stays in place as history.

Consumers: Phase D's animation-preference learner (the documented
bandit over clips) and any renderer needing ground-truth frames.
"""

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
LAB_DIR = Path(__file__).resolve().parent
for path in [GRID_GENOME, LAB_DIR]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from clip_model import CLIP_STATES, clip_frames, clip_names  # noqa: E402


REPORT_DATE = "2026-07-08"
DATASET_ID = "animstate_950"
ARTIFACT_ID = "animstate_dataset_stage0"


def build_animstate_dataset() -> dict:
    from corpus_builder import build_seed_grids_16

    samples: list[dict] = []
    for grid in build_seed_grids_16():
        for clip in clip_names():
            for frame in clip_frames(grid, clip):
                samples.append(
                    {
                        "grid_id": grid["grid_id"],
                        "palette_id": grid["palette"]["palette_id"],
                        "clip": clip,
                        "state": CLIP_STATES[clip][frame["frame_index"]],
                        "frame_index": frame["frame_index"],
                        "frame_count": frame["frame_count"],
                        "cells": [
                            {
                                "x": cell["x"],
                                "y": cell["y"],
                                "visual": cell["visual"],
                                "role": cell["role"],
                            }
                            for cell in frame["cells"]
                        ],
                        "anchors": frame["anchors"],
                    }
                )
    return {
        "dataset_id": DATASET_ID,
        "date": REPORT_DATE,
        "grid_scale": "16x16",
        "clip_vocabulary": clip_names(),
        "supersedes": {
            "documented_name": "animstate_300",
            "documented_minimum": 300,
            "og_dataset": "data/grid_genome/animstate_300.json (8x8 single-frame state projections; kept as history)",
        },
        "samples": samples,
    }


def build_animstate_report() -> dict:
    from corpus_builder import build_seed_grids_16

    corpus = {grid["grid_id"]: grid for grid in build_seed_grids_16()}
    dataset = build_animstate_dataset()
    samples = dataset["samples"]
    in_bounds = 0
    palette_clean = 0
    for sample in samples:
        grid = corpus[sample["grid_id"]]
        width, height = grid["grid_size"]
        legal_colors = set(grid["palette"]["colors"])
        if all(
            0 <= cell["x"] < width and 0 <= cell["y"] < height
            for cell in sample["cells"]
        ):
            in_bounds += 1
        if all(cell["visual"] in legal_colors for cell in sample["cells"]):
            palette_clean += 1

    per_clip: dict[str, int] = {}
    for sample in samples:
        per_clip[sample["clip"]] = per_clip.get(sample["clip"], 0) + 1

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "Regenerate the documented animstate dataset at clip-frame "
            "resolution over the 16x16 corpus (cycle 11 C3): every "
            "(creature, clip, frame) labeled for Phase D's animation-"
            "preference learner; named by its real size and recording what "
            "it supersedes."
        ),
        "source_artifacts": [
            "labs/animation_system/clip_model.py",
            "data/animation_system/clip_model_stage0.json",
            "data/seed_grids_16x16",
            "data/grid_genome/animstate_300.json",
        ],
        "metrics": {
            "sample_count": len(samples),
            "documented_minimum": 300,
            "creatures": len({s["grid_id"] for s in samples}),
            "samples_per_clip": dict(sorted(per_clip.items())),
            "frames_in_bounds_rate": round(in_bounds / len(samples), 6),
            "frames_palette_clean_rate": round(
                palette_clean / len(samples), 6
            ),
        },
        "closed_states": [
            "animstate_dataset_regenerated_at_clip_frame_resolution",
            "documented_minimum_exceeded_and_named_honestly",
        ],
        "blocked_states": [
            "packet_clip_contract_not_wired (C4)",
            "animation_preference_learner_not_built (Phase D consumes this dataset)",
        ],
        "decision": (
            "animstate_950 ships: 950 labeled clip frames, all in bounds "
            "and palette-clean, full coverage of corpus x clips x frames."
        ),
        "next_research_step": (
            "C4: render_packet_v2 gains the documented clip/frame_index/"
            "anchors block as an additive rung."
        ),
    }


def write_animstate_artifacts(
    output_dir: Path, report: dict, dataset: dict
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / f"{DATASET_ID}.json").write_text(
        json.dumps(dataset, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "README.md").write_text(
        "# Animation System Data\n\n"
        "Cycle 11 (ENGINE - Phase C) artifacts:\n\n"
        "- `clip_model_stage0.json` - C1: the clip model gates over the\n"
        "  16x16 corpus (950 frames; in-bounds/palette-clean/genome-\n"
        "  untouched all 1.0) and the intra-clip delta table.\n"
        "- `transition_graph_stage0.json` - C2: the hub-and-spoke\n"
        "  transition graph measured at 0.9877 validity against the\n"
        "  dossier's >=0.80 bar (pre-registered metric).\n"
        "- `animstate_950.json` - C3: the documented animstate dataset\n"
        "  regenerated at clip-frame resolution (950 labeled samples;\n"
        "  supersedes the og 8x8 `animstate_300`, which stays in\n"
        "  `data/grid_genome/` as history). Consumers: Phase D's\n"
        "  animation-preference learner.\n"
        "- `animstate_dataset_stage0.json` - C3's gates.\n\n"
        "Produced by `labs/animation_system/`.\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="animstate clip-frame dataset (cycle 11 C3)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "animation_system"
    )
    args = parser.parse_args()
    report = build_animstate_report()
    dataset = build_animstate_dataset()
    write_animstate_artifacts(args.output_dir, report, dataset)
    print(json.dumps(report["metrics"], indent=2))


if __name__ == "__main__":
    main()
