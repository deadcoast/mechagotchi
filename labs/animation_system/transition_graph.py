"""The clip transition graph and the dossier's >=80% validity bar
(cycle 11 C2, gap-analysis Phase C).

The graph is hub-and-spoke: ``idle`` is the resting hub, every state
clip enters from and returns to it, and every clip may loop on itself
(the loop boundary — last frame back to first — is judged by the same
metric as any transition; a clip that cannot loop cleanly cannot play).

The validity metric is PRE-REGISTERED (fixed here before the run): a
transition a→b is valid for a creature when its boundary delta — the
fraction of render positions changing between the LAST frame of ``a``
and the FIRST frame of ``b`` (the same ``_frame_delta`` C1 measured
inside clips) — is no larger than the jerkiest step already inside
either clip for that creature:

    boundary_delta(a_last, b_first) <= max(intra_max(a), intra_max(b))

i.e. the cut may not be jerkier than the animation itself. Creatures
whose clip has fewer than two distinct frames fall back to the corpus-
wide intra-max for that clip pair (never a free pass). The dossier's
bar: >=80% of (creature x edge) transitions valid.
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

from clip_model import _frame_delta, clip_frames, clip_names  # noqa: E402


REPORT_DATE = "2026-07-08"
ARTIFACT_ID = "transition_graph_stage0"
VALIDITY_BAR = 0.8

# Hub-and-spoke plus self-loops: idle is the resting state every clip
# enters from and returns to; blink is idle's micro-interruption.
TRANSITIONS: tuple[tuple[str, str], ...] = (
    ("idle", "idle"),
    ("idle", "blink"),
    ("blink", "idle"),
    ("blink", "blink"),
    ("idle", "sleep"),
    ("sleep", "idle"),
    ("sleep", "sleep"),
    ("idle", "beg"),
    ("beg", "idle"),
    ("beg", "beg"),
    ("idle", "ill"),
    ("ill", "idle"),
    ("ill", "ill"),
)


def boundary_delta(grid: dict, source: str, target: str) -> float:
    """The cut's render delta: last frame of source -> first of target."""
    source_frames = clip_frames(grid, source)
    target_frames = clip_frames(grid, target)
    return _frame_delta(source_frames[-1], target_frames[0])


def _intra_max(grid: dict, clip: str) -> float:
    frames = clip_frames(grid, clip)
    deltas = [
        _frame_delta(previous, current)
        for previous, current in zip(frames, frames[1:])
    ]
    return max(deltas) if deltas else 0.0


def transition_is_valid(
    grid: dict,
    source: str,
    target: str,
    *,
    fallback_bound: float | None = None,
) -> bool:
    bound = max(_intra_max(grid, source), _intra_max(grid, target))
    if bound == 0.0:
        if fallback_bound is None:
            return boundary_delta(grid, source, target) == 0.0
        bound = fallback_bound
    return boundary_delta(grid, source, target) <= bound


def build_transition_report() -> dict:
    from corpus_builder import build_seed_grids_16

    corpus = build_seed_grids_16()

    # Corpus-wide intra-max per clip pair: the fallback bound for
    # creatures whose own clip barely moves (never a free pass).
    corpus_intra_max: dict[str, float] = {}
    for clip in clip_names():
        corpus_intra_max[clip] = max(
            _intra_max(grid, clip) for grid in corpus
        )

    measured = 0
    valid = 0
    per_edge: dict[str, list[bool]] = {
        f"{source}->{target}": [] for source, target in TRANSITIONS
    }
    boundary_deltas: list[float] = []
    for grid in corpus:
        for source, target in TRANSITIONS:
            fallback = max(
                corpus_intra_max[source], corpus_intra_max[target]
            )
            ok = transition_is_valid(
                grid, source, target, fallback_bound=fallback
            )
            measured += 1
            valid += int(ok)
            per_edge[f"{source}->{target}"].append(ok)
            boundary_deltas.append(boundary_delta(grid, source, target))

    validity_rate = valid / measured
    boundary_deltas.sort()
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete" if validity_rate >= VALIDITY_BAR else "refuted",
        "date": REPORT_DATE,
        "purpose": (
            "Measure the clip transition graph against the dossier's >=80% "
            "transition-validity bar under the pre-registered metric: a "
            "cut may not be jerkier than the jerkiest step already inside "
            "either clip (per creature, with the corpus-wide intra-max as "
            "the fallback bound for near-static clips)."
        ),
        "source_artifacts": [
            "labs/animation_system/clip_model.py",
            "data/animation_system/clip_model_stage0.json",
            "data/seed_grids_16x16",
            "docs/project-research/deep-research/01/deep-research.md",
        ],
        "metrics": {
            "corpus_size": len(corpus),
            "edge_count": len(TRANSITIONS),
            "transitions_measured": measured,
            "transitions_valid": valid,
            "transition_validity_rate": round(validity_rate, 6),
            "validity_bar": VALIDITY_BAR,
            "per_edge_validity": {
                edge: round(sum(results) / len(results), 6)
                for edge, results in sorted(per_edge.items())
            },
            "boundary_delta": {
                "p50": round(
                    boundary_deltas[(len(boundary_deltas) - 1) // 2], 6
                ),
                "p95": round(
                    boundary_deltas[int(0.95 * (len(boundary_deltas) - 1))],
                    6,
                ),
                "max": round(boundary_deltas[-1], 6),
            },
            "corpus_intra_max_per_clip": {
                clip: round(value, 6)
                for clip, value in sorted(corpus_intra_max.items())
            },
        },
        "closed_states": (
            [
                "transition_graph_defined_hub_and_spoke_with_loops",
                "validity_metric_pre_registered",
                "dossier_bar_met",
            ]
            if validity_rate >= VALIDITY_BAR
            else ["dossier_bar_not_met_recorded_honestly"]
        ),
        "blocked_states": [
            "animstate_300_not_regenerated_as_clip_frames (C3)",
            "packet_clip_contract_not_wired (C4)",
            "state_machine_not_driven_by_live_companion_state (the game's client selects clips through this graph; Phase F consumes it)",
        ],
        "decision": (
            f"Transition validity {round(validity_rate, 4)} against the "
            f">= {VALIDITY_BAR} bar: "
            + (
                "the graph holds."
                if validity_rate >= VALIDITY_BAR
                else "the bar is NOT met — recorded, not fudged."
            )
        ),
        "next_research_step": (
            "C3: the animstate_300 dataset over (grid, state, clip, frame)."
        ),
    }


def write_transition_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clip transition graph lab (cycle 11 C2)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "animation_system"
    )
    args = parser.parse_args()
    report = build_transition_report()
    write_transition_artifacts(args.output_dir, report)
    print(json.dumps(report["metrics"], indent=2))
    print(report["decision"])


if __name__ == "__main__":
    main()
