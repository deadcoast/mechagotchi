"""Cycle 20 J2: motion-role emission, measured at the source.

Phase I measured the same fact from three sides: coverage is bounded
by the generators' descriptor range (I5b), the motion vocabulary
animates but only the exemplar exercises it (I4), and the committed
exemplar corpus is the vocabulary's ONLY committed proof. This lab
measures, per generation surface, how often the generators actually
EMIT the DR 0011/0015 motion trio (limb, joint, decoration) — plus
the sway/flicker roles for context — against the committed corpora as
reference. The generator increment is gated on these numbers, never
on intuition.
"""

import argparse
import json
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
WFC_DIR = LAB_DIR.parent / "wfc_grid"
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
for _path in (LAB_DIR, WFC_DIR, PACKAGE_SRC):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from constrained_generator import build_constrained_corpus  # noqa: E402
from corpus_builder import build_seed_grids_16  # noqa: E402
from wfc_grid import build_wfc_corpus, split_corpus, train_wfc_model  # noqa: E402

from mecha_engine.generation import generate_batch  # noqa: E402

ARTIFACT_ID = "role_emission_stage0"
REPORT_DATE = "2026-07-20"
MOTION_ROLES = ["limb", "joint", "decoration"]
CONTEXT_ROLES = ["antenna", "sensor", "effect"]
EXEMPLAR_DIR = ROOT / "data" / "vocabulary_exemplars"


def _measure_source(grids: list[dict]) -> dict:
    roles: dict[str, dict] = {}
    for role in MOTION_ROLES + CONTEXT_ROLES:
        grids_with = 0
        total_cells = 0
        for grid in grids:
            count = sum(
                1 for cell in grid.get("cells", []) if cell.get("role") == role
            )
            if count:
                grids_with += 1
            total_cells += count
        roles[role] = {
            "grids_with_role": grids_with,
            "grids_with_role_rate": round(grids_with / len(grids), 6)
            if grids
            else 0.0,
            "mean_cells_per_grid": round(total_cells / len(grids), 6)
            if grids
            else 0.0,
        }
    return {"grid_count": len(grids), "roles": roles}


def _load_exemplars() -> list[dict]:
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(EXEMPLAR_DIR.glob("*.json"))
    ]


def build_role_emission_report(
    *, count: int = 1000, rng_seed: int = 77
) -> dict:
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    wfc_model = train_wfc_model(train)

    sources = {
        "constrained": _measure_source(
            build_constrained_corpus(seeds, count=count, rng_seed=rng_seed)
        ),
        "wfc": _measure_source(
            build_wfc_corpus(wfc_model, count=count, rng_seed=rng_seed)
        ),
        "promoted_generate_batch": _measure_source(
            generate_batch(seeds, count, rng_seed=rng_seed)
        ),
        "seed_corpus_16": _measure_source(seeds),
        "vocabulary_exemplars": _measure_source(_load_exemplars()),
    }

    motion_trio_emission = {
        name: round(
            sum(
                source["roles"][role]["grids_with_role_rate"]
                for role in MOTION_ROLES
            )
            / len(MOTION_ROLES),
            6,
        )
        for name, source in sources.items()
    }

    generator_names = ["constrained", "wfc", "promoted_generate_batch"]
    finding = (
        "motion-trio emission (mean grids-with-role rate): "
        + ", ".join(
            f"{name} {motion_trio_emission[name]}"
            for name in generator_names
        )
        + f" vs seed corpus {motion_trio_emission['seed_corpus_16']} "
        f"and exemplars {motion_trio_emission['vocabulary_exemplars']}"
    )

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 20 J2 (measurement half): per-surface emission "
            "rates for the DR 0011/0015 motion trio — the generator "
            "increment is gated on these numbers."
        ),
        "source_artifacts": [
            "labs/grid_genome/constrained_generator.py",
            "labs/wfc_grid/wfc_grid.py",
            "packages/mecha_engine/src/mecha_engine/generation/generate.py",
            "data/vocabulary_exemplars/",
            "research/experiment_reports/2026-07-20-per-role-motion.md",
        ],
        "parameters": {"count": count, "rng_seed": rng_seed},
        "metrics": {
            "sources": sources,
            "motion_trio_emission": motion_trio_emission,
            "finding": finding,
        },
        "closed_states": [
            "motion_role_emission_measured_per_generation_surface",
        ],
        "blocked_states": [
            "generator_increment_not_designed_here (the gated change "
            "rides its own decision record, judged on these numbers)",
        ],
        "decision": finding,
        "next_research_step": (
            "the gated generator increment (role-aware generation "
            "and/or the mutation-temperature knob) with pre-registered "
            "gates: emission up, validity held, descriptor support "
            "widened"
        ),
    }


def write_role_emission_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "grid_genome"
    )
    args = parser.parse_args()
    report = build_role_emission_report(count=args.count)
    written = write_role_emission_artifacts(args.output_dir, report)
    print(f"wrote {written}")
    print(report["metrics"]["finding"])
