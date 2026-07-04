import argparse
import csv
import json
import sys
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
WORKSHOP_DIR = ROOT / "labs" / "workshop_editor"
for path in [LAB_DIR, WORKSHOP_DIR]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from manual_rating_intake import (  # noqa: E402
    TEMPLATE_FIELDS,
    build_rating_template,
    load_rating_rows,
    run_manual_rating_intake_lab,
)
from readability_benchmark import manual_rating_protocol, score_readability  # noqa: E402
from slip_long_horizon_behavior_gate import (  # noqa: E402
    DEFAULT_GENERATED_ROOT,
    REPORT_PATH as DEFAULT_LONG_HORIZON_PATH,
    _selected_offspring_grid,
)
from slip_offspring_lineage_gate import _read_parent_grid  # noqa: E402
from slip_preview_gates import build_mutation_preview  # noqa: E402


ARTIFACT_ID = "slip_readability_calibration_gate_stage0"
DEFAULT_OUTPUT_DIR = Path("data/readability")
DEFAULT_RATINGS_PATH = DEFAULT_OUTPUT_DIR / "slip_readability_calibration_ratings.csv"
DEFAULT_INTER_REVIEWER_DELTA_MAX = 1.0
DEFAULT_MIN_PROXY_HUMAN_SPEARMAN = 0.25


def build_slip_long_horizon_readability_benchmark(
    long_horizon_path: Path = DEFAULT_LONG_HORIZON_PATH,
    *,
    generated_root: Path = DEFAULT_GENERATED_ROOT,
) -> dict:
    long_horizon = _read_json(long_horizon_path)
    parameters = long_horizon["parameters"]
    rng_seed = parameters["rng_seed"]
    samples = []

    for profile_index, result in enumerate(long_horizon.get("profile_results", [])):
        if not result.get("gate_started"):
            continue
        profile = _read_json(Path(result["profile_path"]))
        profile_id = result["profile_id"]
        corpus_profile_id = result.get("candidate_profile_id", profile_id)
        parent_grid_id = result["offspring_lineage"]["runtime_parent_grid_id"]
        parent_grid = _read_parent_grid(generated_root, corpus_profile_id, parent_grid_id)
        mutation_preview = build_mutation_preview(profile, parent_grid)
        selected_grid = _selected_offspring_grid(
            profile,
            parent_grid,
            mutation_preview,
            result["selected_offspring_grid_id"],
            rng_seed=rng_seed + profile_index,
        )
        samples.append(
            _sample_entry(
                "selected_offspring",
                selected_grid,
                profile_id=profile_id,
                source_path=None,
                provenance={
                    "long_horizon_probe_id": result["probe_id"],
                    "runtime_parent_grid_id": parent_grid_id,
                    "selection_source": "slip_long_horizon_behavior_gate_stage0",
                },
            )
        )

        for record in result.get("held_out_candidates", []):
            if not record.get("validation", {}).get("ok"):
                continue
            source_path = Path(record["path"])
            grid = _read_json(source_path)
            samples.append(
                _sample_entry(
                    "held_out_long_horizon",
                    grid,
                    profile_id=profile_id,
                    source_path=source_path,
                    provenance={
                        "long_horizon_probe_id": result["probe_id"],
                        "switchboard_survival_ratio": record["switchboard"][
                            "survival_ratio"
                        ],
                        "idle_survival_ratio": record["idle"]["survival_ratio"],
                    },
                )
            )

    return {
        "lab_id": ARTIFACT_ID,
        "date": "2026-05-13",
        "source_artifacts": [
            _portable(long_horizon_path),
            "labs/readability_benchmark/slip_readability_calibration_gate.py",
            "labs/workshop_editor/slip_long_horizon_behavior_gate.py",
            "labs/readability_benchmark/readability_benchmark.py",
            "labs/readability_benchmark/manual_rating_intake.py",
            "data/readability/manual_rating_protocol.md",
        ],
        "long_horizon_artifact_id": long_horizon["artifact_id"],
        "manual_rating_protocol": manual_rating_protocol(),
        "samples": samples,
        "summary": _benchmark_summary(samples),
    }


def run_slip_readability_calibration_gate_lab(
    *,
    long_horizon_path: Path = DEFAULT_LONG_HORIZON_PATH,
    generated_root: Path = DEFAULT_GENERATED_ROOT,
    ratings_path: Path | None = None,
    rating_rows: list[dict] | None = None,
    inter_reviewer_delta_max: float = DEFAULT_INTER_REVIEWER_DELTA_MAX,
    min_proxy_human_spearman: float = DEFAULT_MIN_PROXY_HUMAN_SPEARMAN,
) -> dict:
    benchmark = build_slip_long_horizon_readability_benchmark(
        long_horizon_path,
        generated_root=generated_root,
    )
    if rating_rows is None:
        rating_rows = load_rating_rows(ratings_path or DEFAULT_RATINGS_PATH)

    manual_intake = run_manual_rating_intake_lab(
        benchmark=benchmark,
        rating_rows=rating_rows,
        rng_seed=20260513,
    )
    template = build_rating_template(benchmark)
    minimum_reviewers = benchmark["manual_rating_protocol"]["minimum_reviewers"]
    expected_rows = benchmark["summary"]["sample_count"] * minimum_reviewers
    readiness = _calibration_readiness(
        manual_intake,
        sample_count=benchmark["summary"]["sample_count"],
        expected_rows=expected_rows,
        minimum_reviewers=minimum_reviewers,
        inter_reviewer_delta_max=inter_reviewer_delta_max,
        min_proxy_human_spearman=min_proxy_human_spearman,
    )
    closed_states = [
        "slip_long_horizon_readability_packet",
        "manual_rating_template_for_slip_long_horizon_corpus",
        "proxy_readability_snapshot_for_slip_long_horizon_corpus",
    ]
    blocked_states = [
        "profile_weighted_evolution",
        "package_runtime_lifecycle_integration",
        "final_descriptor_threshold_lock",
    ]
    if readiness["ready"]:
        closed_states.extend(
            [
                "manual_readability_calibration",
                "proxy_human_readability_correlation_check",
                "inter_reviewer_reliability_check",
            ]
        )
    else:
        blocked_states.extend(
            [
                "manual_readability_calibration",
                "proxy_human_readability_correlation_check",
                "inter_reviewer_reliability_check",
            ]
        )

    return {
        "artifact_id": ARTIFACT_ID,
        "status": (
            "manual_readability_calibration_ready"
            if readiness["ready"]
            else "slip_readability_packet_ready_human_ratings_required"
        ),
        "date": "2026-05-13",
        "purpose": (
            "Bind the current SLIP long-horizon corpus to the manual readability "
            "protocol, produce the reviewer template, and only unlock calibration "
            "after real reviewer rows satisfy completeness, reliability, and "
            "proxy-correlation checks."
        ),
        "source_artifacts": benchmark["source_artifacts"],
        "external_anchors": [
            {
                "source": "Comparing PCG metrics with Human Evaluation in Minecraft Settlement Generation",
                "url": "https://arxiv.org/abs/2107.02457",
                "used_for": (
                    "Proxy readability metrics are treated as hypotheses that must "
                    "be compared against human ratings before threshold claims."
                ),
            },
            {
                "source": "A comprehensive guide to study the agreement and reliability of multi-observer ordinal data",
                "url": "https://link.springer.com/article/10.1186/s12874-024-02431-y",
                "used_for": (
                    "Stage 0 records reviewer count and agreement checks separately "
                    "from proxy-human correlation."
                ),
            },
        ],
        "benchmark": benchmark,
        "manual_intake": manual_intake,
        "template": template,
        "ratings_collected": manual_intake["ratings_collected"],
        "manual_readability_calibration_ready": readiness["ready"],
        "expected_completed_rating_rows": expected_rows,
        "calibration_thresholds": {
            "minimum_reviewers": minimum_reviewers,
            "expected_completed_rating_rows": expected_rows,
            "inter_reviewer_mean_absolute_delta_max": inter_reviewer_delta_max,
            "min_proxy_human_spearman": min_proxy_human_spearman,
        },
        "metrics": {
            "sample_count": benchmark["summary"]["sample_count"],
            # _benchmark_summary only creates by_source entries for sources that
            # produced samples, so an empty source group must report count 0
            # instead of raising KeyError.
            "selected_offspring_sample_count": benchmark["summary"]["by_source"]
            .get("selected_offspring", {})
            .get("count", 0),
            "held_out_long_horizon_sample_count": benchmark["summary"]["by_source"]
            .get("held_out_long_horizon", {})
            .get("count", 0),
            "mean_proxy_readability_score": benchmark["summary"][
                "mean_proxy_readability_score"
            ],
            "rating_row_count": manual_intake["summary"]["rating_row_count"],
            "valid_rating_row_count": manual_intake["summary"][
                "valid_rating_row_count"
            ],
            "rated_sample_count": manual_intake["summary"]["rated_sample_count"],
            "reviewer_count": manual_intake["summary"]["reviewer_count"],
            "row_error_count": readiness["row_error_count"],
            "inter_reviewer_mean_absolute_delta": manual_intake["summary"].get(
                "inter_reviewer_mean_absolute_delta"
            ),
            "proxy_human_spearman": manual_intake["summary"].get(
                "proxy_human_spearman"
            ),
            "manual_readability_calibration_ready": readiness["ready"],
        },
        "readiness": readiness,
        "closed_states": closed_states,
        "blocked_states": blocked_states,
        "decision": (
            "prototype_manual_readability_calibration_ready"
            if readiness["ready"]
            else "prototype_slip_readability_packet_only"
        ),
        "next_research_step": (
            f"Collect {expected_rows} reviewer rows in "
            f"{_portable(DEFAULT_RATINGS_PATH)} and rerun this gate before "
            "changing proxy readability thresholds or claiming profile-weighted evolution."
        ),
        "limitations": [
            "No human ratings are fabricated by this lab.",
            "A complete template alone does not calibrate the proxy metric.",
            "Spearman correlation remains descriptive at Stage 0 and must not be treated as a causal readability model.",
            "Profile-weighted evolution still also requires package/runtime integration.",
        ],
    }


def write_slip_readability_calibration_gate_artifacts(
    output_dir: Path,
    report: dict,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / f"{ARTIFACT_ID}.json", report)
    _write_template_csv(
        output_dir / "slip_readability_calibration_template.csv",
        report["template"],
    )
    (output_dir / "slip_readability_calibration_reviewer_packet.md").write_text(
        _reviewer_packet_text(report),
        encoding="utf-8",
    )
    (output_dir / "slip_readability_calibration_README.md").write_text(
        _readme_text(report),
        encoding="utf-8",
    )


def _sample_entry(
    source: str,
    grid: dict,
    *,
    profile_id: str,
    source_path: Path | None,
    provenance: dict,
) -> dict:
    readability = score_readability(grid)
    grid_id = grid.get("grid_id", "unknown_grid")
    return {
        "sample_id": f"{source}:{grid_id}",
        "grid_id": grid_id,
        "source": source,
        "profile_id": profile_id,
        "path": _portable(source_path) if source_path is not None else None,
        "grid_size": grid.get("grid_size", []),
        "cell_count": len(grid.get("cells", [])),
        "readability": readability,
        "manual_rating": None,
        "manual_rating_status": "not_collected",
        "provenance": provenance,
    }


def _benchmark_summary(samples: list[dict]) -> dict:
    scores = [sample["readability"]["proxy_readability_score"] for sample in samples]
    by_source = {}
    for source in sorted({sample["source"] for sample in samples}):
        source_samples = [sample for sample in samples if sample["source"] == source]
        source_scores = [
            sample["readability"]["proxy_readability_score"]
            for sample in source_samples
        ]
        by_source[source] = {
            "count": len(source_samples),
            "valid_count": sum(
                1 for sample in source_samples if sample["readability"]["valid"]
            ),
            "mean_proxy_readability_score": _round(mean(source_scores))
            if source_scores
            else None,
            "min_proxy_readability_score": _round(min(source_scores))
            if source_scores
            else None,
            "max_proxy_readability_score": _round(max(source_scores))
            if source_scores
            else None,
        }
    return {
        "sample_count": len(samples),
        "valid_sample_count": sum(
            1 for sample in samples if sample["readability"]["valid"]
        ),
        "by_source": by_source,
        "mean_proxy_readability_score": _round(mean(scores)) if scores else None,
        "min_proxy_readability_score": _round(min(scores)) if scores else None,
        "max_proxy_readability_score": _round(max(scores)) if scores else None,
    }


def _calibration_readiness(
    manual_intake: dict,
    *,
    sample_count: int,
    expected_rows: int,
    minimum_reviewers: int,
    inter_reviewer_delta_max: float,
    min_proxy_human_spearman: float,
) -> dict:
    summary = manual_intake["summary"]
    row_error_count = summary.get("row_error_count", len(manual_intake["row_errors"]))
    inter_reviewer_delta = summary.get("inter_reviewer_mean_absolute_delta")
    proxy_human_spearman = summary.get("proxy_human_spearman")
    complete = (
        summary["reviewer_count"] >= minimum_reviewers
        and summary["rated_sample_count"] == sample_count
        and summary["valid_rating_row_count"] >= expected_rows
        and row_error_count == 0
    )
    reliability_ok = (
        inter_reviewer_delta is not None
        and inter_reviewer_delta <= inter_reviewer_delta_max
    )
    correlation_ok = (
        proxy_human_spearman is not None
        and proxy_human_spearman >= min_proxy_human_spearman
    )
    ready = complete and reliability_ok and correlation_ok
    reasons = []
    if not manual_intake["ratings_collected"]:
        reasons.append("human_ratings_absent")
    if summary["reviewer_count"] < minimum_reviewers:
        reasons.append("minimum_reviewer_count_not_met")
    if summary["rated_sample_count"] != sample_count:
        reasons.append("not_all_samples_rated")
    if summary["valid_rating_row_count"] < expected_rows:
        reasons.append("expected_completed_rating_rows_not_met")
    if row_error_count:
        reasons.append("rating_row_errors_present")
    if not reliability_ok:
        reasons.append("inter_reviewer_reliability_not_established")
    if not correlation_ok:
        reasons.append("proxy_human_correlation_not_established")

    return {
        "ready": ready,
        "complete_rating_matrix": complete,
        "inter_reviewer_reliability_ok": reliability_ok,
        "proxy_human_correlation_ok": correlation_ok,
        "row_error_count": row_error_count,
        "blocking_reasons": reasons,
    }


def _write_template_csv(path: Path, template: dict) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TEMPLATE_FIELDS)
        writer.writeheader()
        writer.writerows(template["rows"])


def _reviewer_packet_text(report: dict) -> str:
    protocol = report["benchmark"]["manual_rating_protocol"]
    summary = report["benchmark"]["summary"]
    return (
        "# SLIP Readability Calibration Reviewer Packet\n\n"
        "Rate every row in `slip_readability_calibration_template.csv` before "
        "looking at proxy readability values. Use independent reviewer IDs and "
        "one row per sample per reviewer.\n\n"
        "Protocol:\n\n"
        f"- Protocol ID: `{protocol['protocol_id']}`\n"
        f"- Rating scale: {protocol['rating_scale']}\n"
        f"- Minimum reviewers: {protocol['minimum_reviewers']}\n"
        f"- Sample count: {summary['sample_count']}\n"
        f"- Expected completed rows: {report['expected_completed_rating_rows']}\n"
        "- Aggregation: median per question, then mean across questions\n\n"
        "Questions:\n\n"
        + "".join(
            f"- `{field}`: {question}\n"
            for field, question in protocol["questions"].items()
        )
        + "\nCalibration remains blocked until the filled CSV has all expected "
        "reviewer rows, no row errors, acceptable inter-reviewer agreement, and "
        "a positive proxy-human rank correlation.\n"
    )


def _readme_text(report: dict) -> str:
    metrics = report["metrics"]
    return (
        "# SLIP Readability Calibration Gate Stage 0\n\n"
        "Readability calibration packet for the current SLIP long-horizon corpus.\n\n"
        "Key results:\n\n"
        f"- Samples: {metrics['sample_count']}\n"
        f"- Selected offspring samples: {metrics['selected_offspring_sample_count']}\n"
        f"- Held-out long-horizon samples: {metrics['held_out_long_horizon_sample_count']}\n"
        f"- Expected completed rating rows: {report['expected_completed_rating_rows']}\n"
        f"- Ratings collected: {report['ratings_collected']}\n"
        f"- Manual readability calibration ready: {report['manual_readability_calibration_ready']}\n"
        f"- Decision: {report['decision']}\n\n"
        "No human ratings are fabricated. Fill "
        "`slip_readability_calibration_ratings.csv` from the template and rerun "
        "the gate before changing proxy readability thresholds.\n"
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _portable(path: Path | None) -> str | None:
    if path is None:
        return None
    return path.as_posix()


def _round(value: float | int) -> float:
    return round(float(value), 6)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the SLIP long-horizon readability calibration packet."
    )
    parser.add_argument("--long-horizon", type=Path, default=DEFAULT_LONG_HORIZON_PATH)
    parser.add_argument("--generated-root", type=Path, default=DEFAULT_GENERATED_ROOT)
    parser.add_argument("--ratings", type=Path, default=DEFAULT_RATINGS_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    report = run_slip_readability_calibration_gate_lab(
        long_horizon_path=args.long_horizon,
        generated_root=args.generated_root,
        ratings_path=args.ratings,
    )
    write_slip_readability_calibration_gate_artifacts(args.output_dir, report)
    print(json.dumps(report["metrics"], indent=2))


if __name__ == "__main__":
    main()
