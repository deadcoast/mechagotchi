"""The recurrent morphological families (cycle 13 E5).

The dossier's MAP-Elites decision gate asks for "at least five recurrent
families" across runs; the gap table demands they be identified "across
independent seeded runs (lineage/descriptor clustering over the
archive's elites); family recurrence recorded, not curated."

Operationalization (descriptor clustering — the WFC parent path carries
no single-parent lineage, recorded in E3): a FAMILY is a coarse cell of
the E1 scale descriptor space — each 8-bin axis halved
(``COARSENING_FACTOR = 2``), giving 4×4×4 = 64 morphological cells over
(symmetry, visual complexity, behavior neediness). A family is
RECURRENT when it is occupied by at least one elite in EVERY independent
seeded run. Nothing is curated: the family list is the deterministic
intersection, each entry carrying per-run counts, pooled axis-value
means, and per-run exemplar grid ids so a human check (the dossier's
"reliably distinguish" reading — owner-deferred survey territory, never
a blocker) has its material.

Input: E4's committed artifact (`coverage_qd_gates_stage0.json`), whose
MAP-Elites runs each record their full elite roster (grid_id,
descriptor, axis values, morphology signature hash) per seed.
"""

import argparse
import json
import sys
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = ROOT / "labs" / "map_elites_archive"
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from niche_scale_archive import SCALE_DESCRIPTOR_NAMES  # noqa: E402


REPORT_DATE = "2026-07-09"
ARTIFACT_ID = "recurrent_families_stage0"
FAMILY_GATE = 5  # the dossier's "at least five recurrent families"
COARSENING_FACTOR = 2  # 8 fine bins -> 4 coarse cells per axis
E4_ARTIFACT = ROOT / "data" / "archives" / "coverage_qd_gates_stage0.json"


def family_key(descriptor: list[int] | tuple[int, ...]) -> tuple[int, ...]:
    """The coarse morphological cell a fine descriptor belongs to."""
    return tuple(value // COARSENING_FACTOR for value in descriptor)


def cluster_families(elite_records: list[dict]) -> dict[tuple[int, ...], dict]:
    """Deterministic family clusters over one run's elite roster."""
    clusters: dict[tuple[int, ...], dict] = {}
    for record in elite_records:
        key = family_key(record["descriptor"])
        cluster = clusters.setdefault(
            key, {"count": 0, "grid_ids": [], "records": []}
        )
        cluster["count"] += 1
        cluster["grid_ids"].append(record["grid_id"])
        cluster["records"].append(record)
    return clusters


def find_recurrent_families(runs: list[list[dict]]) -> list[dict]:
    """Families occupied in EVERY independent run — the intersection,
    recorded with per-run counts, pooled axis means, and exemplars."""
    per_run_clusters = [cluster_families(records) for records in runs]
    if not per_run_clusters:
        return []
    shared_keys = set(per_run_clusters[0])
    for clusters in per_run_clusters[1:]:
        shared_keys &= set(clusters)

    recurrent = []
    for key in sorted(shared_keys):
        members = [
            record
            for clusters in per_run_clusters
            for record in clusters[key]["records"]
        ]
        recurrent.append(
            {
                "family": list(key),
                "per_run_counts": [
                    clusters[key]["count"] for clusters in per_run_clusters
                ],
                "total_members": len(members),
                "axis_value_means": {
                    name: round(
                        mean(
                            record["axis_values"][name] for record in members
                        ),
                        6,
                    )
                    for name in SCALE_DESCRIPTOR_NAMES
                },
                "mean_fitness": round(
                    mean(record["fitness"] for record in members), 6
                ),
                "exemplars_per_run": [
                    clusters[key]["grid_ids"][0]
                    for clusters in per_run_clusters
                ],
            }
        )
    return recurrent


def build_recurrent_families_report(
    *, runs: list[dict] | None = None, artifact_path: Path = E4_ARTIFACT
) -> dict:
    """Cluster E4's per-seed elite rosters (or explicit ``runs``)."""
    if runs is None:
        e4 = json.loads(Path(artifact_path).read_text(encoding="utf-8"))
        runs = [
            {
                "rng_seed": run["rng_seed"],
                "elite_records": run["elite_records"],
            }
            for run in e4["metrics"]["map_elites_runs"]
        ]
    rosters = [run["elite_records"] for run in runs]
    recurrent = find_recurrent_families(rosters)
    per_run_family_counts = [
        len(cluster_families(roster)) for roster in rosters
    ]
    gate_met = len(recurrent) >= FAMILY_GATE

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete" if gate_met else "refuted",
        "date": REPORT_DATE,
        "purpose": (
            "Identify the documented recurrent morphological families "
            "across independent seeded runs by deterministic descriptor "
            "clustering over the archives' elites — recurrence recorded, "
            "not curated (cycle 13 E5)."
        ),
        "source_artifacts": [
            "data/archives/coverage_qd_gates_stage0.json",
            "labs/map_elites_archive/evaluation_loop_scale.py",
            "labs/map_elites_archive/niche_scale_archive.py",
            "docs/project-research/deep-research/01/deep-research.md",
        ],
        "metrics": {
            "protocol": {
                "runs_analyzed": len(runs),
                "run_seeds": [run["rng_seed"] for run in runs],
                "family_definition": (
                    "a coarse cell of the E1 scale descriptor space — each "
                    "8-bin axis halved (COARSENING_FACTOR 2), 4x4x4 = 64 "
                    "morphological cells over (symmetry, visual complexity, "
                    "behavior neediness)"
                ),
                "recurrence_rule": (
                    "occupied by at least one elite in EVERY independent "
                    "seeded run — the deterministic intersection, nothing "
                    "curated"
                ),
                "lineage_note": (
                    "descriptor clustering, not parent-chain lineage: the "
                    "WFC parent path retrains on the whole elite pool, so "
                    "children carry no single parent (recorded in E3)"
                ),
            },
            "per_run_family_counts": per_run_family_counts,
            "recurrent_families": recurrent,
            "verdict": {
                "family_gate": FAMILY_GATE,
                "recurrent_family_count": len(recurrent),
                "gate_met": gate_met,
            },
        },
        "closed_states": [
            "families_clustered_deterministically_over_elite_records",
            "recurrence_is_the_intersection_across_all_runs",
            "per_family_characterization_recorded",
        ],
        "blocked_states": [
            "human_distinguishability_not_collected (the dossier's "
            "'reliably distinguish' reading is owner-deferred survey "
            "territory — never a blocker; the per-family axis means and "
            "exemplars are its prepared material)",
        ],
        "decision": (
            f"{len(recurrent)} recurrent families across "
            f"{len(runs)} independent seeded runs against the documented "
            f">= {FAMILY_GATE} gate — "
            + ("the gate is MET." if gate_met else "the gate FAILED; recorded.")
        ),
        "next_research_step": (
            "E6: the consolidated Phase-E gate report with the honest "
            "remainder list; cycle 13 archives; cycle 14 opens Phase F."
        ),
    }


def write_recurrent_families_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="The recurrent morphological families (cycle 13 E5)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "archives"
    )
    parser.add_argument("--e4-artifact", type=Path, default=E4_ARTIFACT)
    args = parser.parse_args()

    report = build_recurrent_families_report(artifact_path=args.e4_artifact)
    write_recurrent_families_artifacts(args.output_dir, report)
    print(json.dumps(report["metrics"]["verdict"], indent=2))
    print(
        json.dumps(
            report["metrics"]["per_run_family_counts"], indent=2
        )
    )
    print(report["decision"])


if __name__ == "__main__":
    main()
