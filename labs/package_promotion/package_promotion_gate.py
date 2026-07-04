import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


SOURCE_REFS = [
    {
        "name": "Python Packaging User Guide - Writing your pyproject.toml",
        "url": "https://packaging.python.org/en/latest/guides/writing-pyproject-toml/",
        "use": "Reference for modern Python package metadata and build-system expectations.",
    },
    {
        "name": "Python Packaging User Guide - src layout vs flat layout",
        "url": "https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/",
        "use": "Reference for package boundary and import-layout decisions.",
    },
]


def build_promotion_criteria() -> list[dict]:
    return [
        {
            "criterion_id": "research_artifacts_complete",
            "description": "Algorithm card, experiment report, and metric artifact exist.",
            "required_for": "package_design",
        },
        {
            "criterion_id": "metric_thresholds_met",
            "description": "Candidate metrics satisfy component-specific thresholds.",
            "required_for": "package_design",
        },
        {
            "criterion_id": "package_boundary_defined",
            "description": "Target package path and ownership boundary are named.",
            "required_for": "package_design",
        },
        {
            "criterion_id": "verification_surface_defined",
            "description": "A focused verification command exists for the candidate.",
            "required_for": "package_design",
        },
        {
            "criterion_id": "provenance_gate_clean",
            "description": "External source, license, and attribution blockers are absent.",
            "required_for": "promotion",
        },
        {
            "criterion_id": "package_root_exists",
            "description": "`packages/mecha_engine` exists before lab code is moved.",
            "required_for": "promotion",
        },
        {
            "criterion_id": "no_research_blockers",
            "description": "Human-rating, real-ingest, or lab-only blockers are resolved.",
            "required_for": "promotion",
        },
    ]


def build_candidate_registry() -> list[dict]:
    return [
        {
            "component_id": "lifecycle_simulator",
            "target_package": "packages/mecha_engine/src/mecha_engine/lifecycle",
            "algorithm_card": "research/algorithm_cards/lifecycle_simulator.md",
            "experiment_report": "research/experiment_reports/2026-05-12-lifecycle-simulator-baseline.md",
            "metric_artifact": "data/lifecycle/lifecycle_stage0.json",
            "thresholds": [
                {
                    "metric_path": ["policies", "switchboard", "alive"],
                    "operator": "==",
                    "value": True,
                },
                {
                    "metric_path": ["summary", "switchboard_beats_idle_on_need_balance"],
                    "operator": "==",
                    "value": True,
                },
            ],
            "verification": "python -B labs/lifecycle_sim/test_lifecycle_sim.py",
            "research_notes": "Lifecycle is a first-class v0.2 gate.",
        },
        {
            "component_id": "switchboard_feedback",
            "target_package": "packages/mecha_engine/src/mecha_engine/learning",
            "algorithm_card": "research/algorithm_cards/micro_learning_switchboard.md",
            "experiment_report": "research/experiment_reports/2026-05-12-switchboard-lifecycle-feedback.md",
            "metric_artifact": "data/micro_learners/switchboard_lifecycle_feedback_stage0.json",
            "thresholds": [
                {
                    "metric_path": ["summary", "feedback_reward_update_count"],
                    "operator": ">=",
                    "value": 1,
                },
                {
                    "metric_path": ["summary", "survival_delta"],
                    "operator": ">=",
                    "value": 0,
                },
            ],
            "verification": "python -B labs/grid_genome/test_switchboard_feedback.py",
            "research_notes": "Feedback loop is wired but did not beat frozen baseline yet.",
            "research_blockers": [
                {
                    "blocker_id": "reward_shaping_not_superior_to_frozen_baseline",
                    "cleared_when": {
                        "metric_path": ["summary", "need_balance_delta"],
                        "operator": ">",
                        "value": 0,
                    },
                }
            ],
        },
        {
            "component_id": "map_elites_archive",
            "target_package": "packages/mecha_engine/src/mecha_engine/archive",
            "algorithm_card": "research/algorithm_cards/map_elites_extended_descriptors.md",
            "experiment_report": "research/experiment_reports/2026-05-12-map-elites-extended-descriptors.md",
            "metric_artifact": "data/archives/map_elites_extended_stage0.json",
            "thresholds": [
                {
                    "metric_path": ["archive", "occupied_niches"],
                    "operator": ">=",
                    "value": 20,
                },
                {
                    "metric_path": ["archive", "best_fitness"],
                    "operator": ">=",
                    "value": 0.9,
                },
            ],
            "verification": "python -B labs/map_elites_archive/test_extended_descriptors.py",
            "research_notes": "Descriptor space is richer but sparse.",
        },
        {
            "component_id": "provenance_ci",
            "target_package": "packages/mecha_engine/src/mecha_engine/provenance",
            "algorithm_card": "research/algorithm_cards/provenance_ci_spdx.md",
            "experiment_report": "research/experiment_reports/2026-05-12-provenance-ci-spdx-parser.md",
            "metric_artifact": "data/asset_provenance/provenance_ci_report.json",
            "thresholds": [
                {
                    "metric_path": ["ok"],
                    "operator": "==",
                    "value": True,
                },
                {
                    "metric_path": ["checks", "spdx_expressions_ok"],
                    "operator": "==",
                    "value": True,
                },
            ],
            "verification": "python -B labs/asset_pipeline/test_provenance_ledger.py",
            "research_notes": "Research-artifact provenance gate is adoptable.",
        },
        {
            "component_id": "readability_gate",
            "target_package": "packages/mecha_engine/src/mecha_engine/evaluation",
            "algorithm_card": "research/algorithm_cards/readability_benchmark.md",
            "experiment_report": "research/experiment_reports/2026-05-12-manual-readability-rating-intake.md",
            "metric_artifact": "data/readability/manual_readability_rating_intake_stage0.json",
            "thresholds": [
                {
                    "metric_path": ["ratings_collected"],
                    "operator": "==",
                    "value": True,
                }
            ],
            "verification": "python -B labs/readability_benchmark/test_manual_rating_intake.py",
            "research_notes": "Proxy calibration is blocked until real human ratings exist.",
            "research_blockers": [
                {
                    "blocker_id": "human_ratings_absent",
                    "cleared_when": {
                        "metric_path": ["ratings_collected"],
                        "operator": "==",
                        "value": True,
                    },
                }
            ],
        },
        {
            "component_id": "ca_nca_repair",
            "target_package": "packages/mecha_engine/src/mecha_engine/repair",
            "algorithm_card": "research/algorithm_cards/ca_nca_growth_repair.md",
            "experiment_report": "research/experiment_reports/2026-05-12-ca-nca-repeated-stochastic-damage.md",
            "metric_artifact": "data/cellular_automata/ca_nca_repeated_stochastic_damage_stage0.json",
            "thresholds": [
                {
                    "metric_path": ["summary", "final_validity_rate"],
                    "operator": ">=",
                    "value": 0.9,
                },
                {
                    "metric_path": ["summary", "mean_final_overlap"],
                    "operator": ">=",
                    "value": 0.9,
                },
            ],
            "verification": "python -B labs/cellular_automata/test_ca_nca_growth_repair.py",
            "research_notes": (
                "Assisted target-template baseline; a gradient-trained "
                "neighborhood repair model now exists and beats no-repair "
                "substantially, but has not reached the assisted stability "
                "bar (0.9)."
            ),
            "research_blockers": [
                # Derived since 2026-07-04: the trained-repair lab records a
                # machine-checkable stability-bar verdict in its own artifact.
                {
                    "blocker_id": "lab_only_target_template_assisted",
                    "cleared_when": {
                        "artifact": (
                            "data/cellular_automata/ca_nca_trained_repair_stage0.json"
                        ),
                        "metric_path": [
                            "decision",
                            "thresholds",
                            "meets_assisted_stability_bar",
                        ],
                        "operator": "==",
                        "value": True,
                    },
                }
            ],
        },
    ]


def evaluate_candidate(
    root: Path,
    candidate: dict,
    *,
    package_root_exists: bool,
) -> dict:
    evidence_paths = {
        "algorithm_card": candidate["algorithm_card"],
        "experiment_report": candidate["experiment_report"],
        "metric_artifact": candidate["metric_artifact"],
    }
    missing_evidence = [
        label for label, path in evidence_paths.items() if not (root / path).exists()
    ]
    metrics = _load_json(root / candidate["metric_artifact"])
    threshold_results = [
        _evaluate_threshold(metrics, threshold)
        for threshold in candidate.get("thresholds", [])
    ]
    thresholds_met = all(result["ok"] for result in threshold_results)
    research_evidence_complete = not missing_evidence and thresholds_met

    blocker_details = _evaluate_research_blockers(
        candidate.get("research_blockers", []),
        metrics,
        root,
    )
    active_research_blockers = [
        detail["blocker_id"] for detail in blocker_details if detail["active"]
    ]

    promotion_blockers = []
    if not package_root_exists:
        promotion_blockers.append("package_root_absent")
    if not (root / candidate["target_package"]).exists():
        promotion_blockers.append("target_package_absent")
    promotion_blockers.extend(active_research_blockers)

    if not research_evidence_complete:
        gate_status = "blocked_missing_or_failed_research_evidence"
    elif active_research_blockers:
        gate_status = "hold_research_only"
    elif package_root_exists and (root / candidate["target_package"]).exists():
        gate_status = "promotion_ready"
    else:
        gate_status = "ready_for_package_design"

    return {
        "component_id": candidate["component_id"],
        "target_package": candidate["target_package"],
        "gate_status": gate_status,
        "research_evidence_complete": research_evidence_complete,
        "missing_evidence": missing_evidence,
        "thresholds_met": thresholds_met,
        "threshold_results": threshold_results,
        "verification": candidate["verification"],
        "promotion_blockers": promotion_blockers,
        "research_blocker_details": blocker_details,
        "research_notes": candidate.get("research_notes", ""),
    }


def _evaluate_research_blockers(
    blockers: list,
    metrics: dict | None,
    root: Path,
) -> list[dict]:
    """Derive blocker activity from the metric artifact where possible.

    A blocker with a `cleared_when` check is derived: it stays active until
    the referenced artifact field satisfies the check. The check reads the
    candidate's metric artifact by default; a check carrying an `artifact`
    path reads that artifact instead (for evidence recorded outside the
    candidate's primary metric report). A blocker without a check (or
    declared as a bare string) has no corresponding artifact evidence and is
    reported with `"static": true` so static and derived blockers stay
    distinguishable.
    """
    details = []
    for blocker in blockers:
        if isinstance(blocker, str):
            blocker = {"blocker_id": blocker}
        cleared_when = blocker.get("cleared_when")
        if cleared_when is None:
            details.append(
                {
                    "blocker_id": blocker["blocker_id"],
                    "static": True,
                    "active": True,
                    "evidence": None,
                }
            )
            continue
        evidence_source = metrics
        artifact_override = cleared_when.get("artifact")
        if artifact_override is not None:
            evidence_source = _load_json(root / artifact_override)
        evidence = _evaluate_threshold(evidence_source, cleared_when)
        if artifact_override is not None:
            evidence["artifact"] = artifact_override
        details.append(
            {
                "blocker_id": blocker["blocker_id"],
                "static": False,
                # If the artifact is missing or the field is absent, the
                # check cannot pass and the blocker conservatively stays on.
                "active": not evidence["ok"],
                "evidence": evidence,
            }
        )
    return details


def run_package_promotion_gate(root: Path) -> dict:
    package_root_exists = (root / "packages" / "mecha_engine").exists()
    criteria = build_promotion_criteria()
    candidates = [
        evaluate_candidate(
            root,
            candidate,
            package_root_exists=package_root_exists,
        )
        for candidate in build_candidate_registry()
    ]
    summary = {
        "package_root_exists": package_root_exists,
        "criteria_count": len(criteria),
        "candidate_count": len(candidates),
        "research_ready_count": sum(
            1
            for candidate in candidates
            if candidate["gate_status"]
            in {"ready_for_package_design", "promotion_ready", "hold_research_only"}
        ),
        "package_design_ready_count": sum(
            1
            for candidate in candidates
            if candidate["gate_status"] == "ready_for_package_design"
        ),
        "promotion_ready_count": sum(
            1 for candidate in candidates if candidate["gate_status"] == "promotion_ready"
        ),
        "blocked_count": sum(
            1
            for candidate in candidates
            if candidate["gate_status"] == "blocked_missing_or_failed_research_evidence"
        ),
        "hold_research_only_count": sum(
            1 for candidate in candidates if candidate["gate_status"] == "hold_research_only"
        ),
    }
    return {
        "lab_id": "mecha_engine_package_promotion_gate_stage0",
        "date": "2026-05-12",
        "source_mode": "research_to_package_promotion_gate",
        "summary": summary,
        "criteria": criteria,
        "candidates": candidates,
        "decision": _decision(summary),
        "source_refs": SOURCE_REFS,
        "limitations": [
            "This defines the gate; it does not create packages/mecha_engine.",
            "Promotion remains blocked while target package boundaries and their package-level tests are absent, even though the empty scaffold root exists.",
            "Some lab candidates are intentionally held because their research status is lab-only or blocked.",
        ],
    }


def write_package_promotion_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "mecha_engine_package_promotion_gate_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "mecha_engine_package_promotion_criteria.md").write_text(
        _criteria_markdown(report),
        encoding="utf-8",
    )


def _evaluate_threshold(metrics: dict | None, threshold: dict) -> dict:
    actual = _metric_value(metrics, threshold["metric_path"]) if metrics else None
    expected = threshold["value"]
    operator = threshold["operator"]
    ok = False
    if actual is not None:
        if operator == "==":
            ok = actual == expected
        elif operator == ">=":
            ok = actual >= expected
        elif operator == "<=":
            ok = actual <= expected
        elif operator == ">":
            ok = actual > expected
        elif operator == "<":
            ok = actual < expected
    return {
        "metric_path": threshold["metric_path"],
        "operator": operator,
        "expected": expected,
        "actual": actual,
        "ok": ok,
    }


def _metric_value(metrics: dict, path: list[str]) -> object:
    current = metrics
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _decision(summary: dict) -> dict:
    if not summary["package_root_exists"]:
        return {
            "status": "criteria_defined_no_package_promotion",
            "adoption": "define_gate_only",
            "reason": (
                "Research evidence can identify package-design candidates, but "
                "`packages/mecha_engine` does not exist, so no lab code should "
                "be promoted yet."
            ),
        }
    if summary["promotion_ready_count"] > 0:
        return {
            "status": "promotion_candidates_available",
            "adoption": "review_before_copying_lab_code",
            "reason": "At least one candidate has evidence and a package boundary.",
        }
    return {
        "status": "criteria_defined_no_ready_candidates",
        "adoption": "hold",
        "reason": "The package root exists but no component clears the promotion gate.",
    }


def _criteria_markdown(report: dict) -> str:
    lines = [
        "# Mecha Engine Package Promotion Criteria",
        "",
        "This gate defines when lab code may be considered for `packages/mecha_engine`.",
        "It does not promote code by itself.",
        "",
        "## Criteria",
        "",
    ]
    for criterion in report["criteria"]:
        lines.append(
            f"- `{criterion['criterion_id']}` ({criterion['required_for']}): {criterion['description']}"
        )
    lines.extend(["", "## Candidate Status", ""])
    for candidate in report["candidates"]:
        lines.append(
            f"- `{candidate['component_id']}` -> `{candidate['gate_status']}` "
            f"for `{candidate['target_package']}`"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"Status: `{report['decision']['status']}`",
            "",
            report["decision"]["reason"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/package_promotion")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = run_package_promotion_gate(args.root.resolve())
    write_package_promotion_artifacts(args.output_dir, report)
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
