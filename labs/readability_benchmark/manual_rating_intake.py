import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, median


ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from readability_benchmark import build_heldout_readability_benchmark  # noqa: E402


RATING_FIELDS = [
    "silhouette",
    "organ_clarity",
    "palette_contrast",
    "animation_readiness",
    "companion_appeal",
]

TEMPLATE_FIELDS = [
    "sample_id",
    "grid_id",
    "source",
    "reviewer_id",
    *RATING_FIELDS,
    "notes",
]

SOURCE_REFS = [
    {
        "name": "Comparing PCG metrics with Human Evaluation in Minecraft Settlement Generation",
        "url": "https://arxiv.org/abs/2107.02457",
        "use": "Reference for comparing procedural-content metrics against human evaluation.",
    },
    {
        "name": "Measuring inter-rater reliability for nominal data",
        "url": "https://bmcmedresmethodol.biomedcentral.com/articles/10.1186/s12874-016-0200-9",
        "use": "Reference for treating reviewer agreement as a required reliability concern.",
    },
]


def build_rating_template(benchmark: dict) -> dict:
    rows = []
    for sample in benchmark.get("samples", []):
        rows.append(
            {
                "sample_id": sample["sample_id"],
                "grid_id": sample["grid_id"],
                "source": sample["source"],
                "reviewer_id": "",
                "silhouette": "",
                "organ_clarity": "",
                "palette_contrast": "",
                "animation_readiness": "",
                "companion_appeal": "",
                "notes": "",
            }
        )
    return {
        "protocol_id": benchmark["manual_rating_protocol"]["protocol_id"],
        "template_row_count": len(rows),
        "fields": TEMPLATE_FIELDS,
        "rows": rows,
    }


def load_rating_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def run_manual_rating_intake_lab(
    *,
    benchmark: dict | None = None,
    rating_rows: list[dict] | None = None,
    rng_seed: int = 20260512,
) -> dict:
    benchmark = benchmark or build_heldout_readability_benchmark(rng_seed=rng_seed)
    rating_rows = rating_rows or []
    template = build_rating_template(benchmark)
    sample_index = {sample["sample_id"]: sample for sample in benchmark["samples"]}
    parsed_rows, row_errors = _parse_rating_rows(rating_rows, sample_index)

    if not parsed_rows:
        summary = {
            "status": "awaiting_human_ratings",
            "template_row_count": template["template_row_count"],
            "rating_row_count": 0,
            "valid_rating_row_count": 0,
            "rated_sample_count": 0,
            "reviewer_count": 0,
            "mean_human_rating": None,
            "proxy_human_spearman": None,
            "inter_reviewer_mean_absolute_delta": None,
        }
        per_sample = []
    else:
        per_sample = _aggregate_per_sample(parsed_rows, sample_index)
        summary = _summary(template, parsed_rows, per_sample, row_errors)

    return {
        "lab_id": "manual_readability_rating_intake_stage0",
        "date": "2026-05-12",
        "rng_seed": rng_seed,
        "protocol_id": template["protocol_id"],
        "ratings_collected": bool(parsed_rows),
        "summary": summary,
        "template": template,
        "per_sample": per_sample,
        "row_errors": row_errors,
        "source_refs": SOURCE_REFS,
        "decision": _decision(summary),
        "limitations": [
            "No human ratings are bundled unless a reviewer CSV is supplied.",
            "Spearman correlation is unstable for very small or tied rating sets.",
            "Reviewer reliability is approximated with mean absolute deltas in Stage 0.",
            "Formal inter-rater reliability should be added after real rating volume exists.",
        ],
    }


def write_manual_rating_intake_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "manual_readability_rating_intake_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_template_csv(output_dir / "manual_rating_template.csv", report["template"])
    (output_dir / "manual_rating_intake_README.md").write_text(
        _readme_text(report),
        encoding="utf-8",
    )


def _parse_rating_rows(
    rows: list[dict], sample_index: dict[str, dict]
) -> tuple[list[dict], list[dict]]:
    parsed = []
    errors = []
    for row_number, row in enumerate(rows, start=2):
        sample_id = row.get("sample_id", "")
        reviewer_id = row.get("reviewer_id", "")
        if sample_id not in sample_index:
            errors.append(
                {
                    "row_number": row_number,
                    "sample_id": sample_id,
                    "error": "unknown_sample_id",
                }
            )
            continue
        if not reviewer_id:
            errors.append(
                {
                    "row_number": row_number,
                    "sample_id": sample_id,
                    "error": "missing_reviewer_id",
                }
            )
            continue
        ratings = {}
        for field in RATING_FIELDS:
            value = _parse_rating(row.get(field))
            if value is None:
                errors.append(
                    {
                        "row_number": row_number,
                        "sample_id": sample_id,
                        "field": field,
                        "error": "rating_must_be_integer_1_to_5",
                    }
                )
                ratings = None
                break
            ratings[field] = value
        if ratings is None:
            continue
        parsed.append(
            {
                "row_number": row_number,
                "sample_id": sample_id,
                "reviewer_id": reviewer_id,
                "ratings": ratings,
                "notes": row.get("notes", ""),
                "human_rating": round(mean(ratings.values()), 6),
            }
        )
    return parsed, errors


def _aggregate_per_sample(
    rows: list[dict], sample_index: dict[str, dict]
) -> list[dict]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["sample_id"]].append(row)
    per_sample = []
    for sample_id in sorted(grouped):
        sample_rows = grouped[sample_id]
        question_medians = {
            field: median(row["ratings"][field] for row in sample_rows)
            for field in RATING_FIELDS
        }
        human_rating = round(mean(question_medians.values()), 6)
        sample = sample_index[sample_id]
        per_sample.append(
            {
                "sample_id": sample_id,
                "grid_id": sample["grid_id"],
                "source": sample["source"],
                "reviewer_count": len({row["reviewer_id"] for row in sample_rows}),
                "rating_row_count": len(sample_rows),
                "question_medians": question_medians,
                "human_rating": human_rating,
                "proxy_readability_score": sample["readability"][
                    "proxy_readability_score"
                ],
                "proxy_human_delta": round(
                    sample["readability"]["proxy_readability_score"]
                    - (human_rating / 5),
                    6,
                ),
            }
        )
    return per_sample


def _summary(
    template: dict,
    parsed_rows: list[dict],
    per_sample: list[dict],
    row_errors: list[dict],
) -> dict:
    reviewers = sorted({row["reviewer_id"] for row in parsed_rows})
    human_values = [sample["human_rating"] for sample in per_sample]
    proxy_values = [sample["proxy_readability_score"] for sample in per_sample]
    return {
        "status": "ratings_collected",
        "template_row_count": template["template_row_count"],
        "rating_row_count": len(parsed_rows) + len(row_errors),
        "valid_rating_row_count": len(parsed_rows),
        "rated_sample_count": len(per_sample),
        "reviewer_count": len(reviewers),
        "mean_human_rating": round(mean(human_values), 6) if human_values else None,
        "mean_proxy_readability_for_rated_samples": round(mean(proxy_values), 6)
        if proxy_values
        else None,
        "proxy_human_spearman": _spearman(proxy_values, human_values),
        "inter_reviewer_mean_absolute_delta": _inter_reviewer_delta(parsed_rows),
        "row_error_count": len(row_errors),
    }


def _spearman(left: list[float], right: list[float]) -> float | None:
    if len(left) < 2 or len(left) != len(right):
        return None
    return _pearson(_rank(left), _rank(right))


def _rank(values: list[float]) -> list[float]:
    sorted_pairs = sorted((value, index) for index, value in enumerate(values))
    ranks = [0.0] * len(values)
    position = 0
    while position < len(sorted_pairs):
        end = position
        while end + 1 < len(sorted_pairs) and sorted_pairs[end + 1][0] == sorted_pairs[position][0]:
            end += 1
        average_rank = (position + end + 2) / 2
        for _, index in sorted_pairs[position : end + 1]:
            ranks[index] = average_rank
        position = end + 1
    return ranks


def _pearson(left: list[float], right: list[float]) -> float | None:
    left_mean = mean(left)
    right_mean = mean(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_denominator = sum((a - left_mean) ** 2 for a in left) ** 0.5
    right_denominator = sum((b - right_mean) ** 2 for b in right) ** 0.5
    denominator = left_denominator * right_denominator
    if denominator == 0:
        return None
    return round(numerator / denominator, 6)


def _inter_reviewer_delta(rows: list[dict]) -> float | None:
    by_sample = defaultdict(list)
    for row in rows:
        by_sample[row["sample_id"]].append(row["human_rating"])
    deltas = []
    for ratings in by_sample.values():
        if len(ratings) < 2:
            continue
        for index, left in enumerate(ratings):
            for right in ratings[index + 1 :]:
                deltas.append(abs(left - right))
    return round(mean(deltas), 6) if deltas else None


def _parse_rating(value: object) -> int | None:
    try:
        rating = int(str(value).strip())
    except (TypeError, ValueError):
        return None
    if 1 <= rating <= 5:
        return rating
    return None


def _decision(summary: dict) -> dict:
    if summary["status"] == "awaiting_human_ratings":
        return {
            "status": "blocked_human_ratings_absent",
            "adoption": "do_not_calibrate_proxy",
            "reason": (
                "The intake protocol and CSV template exist, but no reviewer "
                "ratings were supplied. Proxy calibration remains blocked."
            ),
        }
    reliable = (
        summary["reviewer_count"] >= 3
        and summary["rated_sample_count"] >= 3
        and summary["row_error_count"] == 0
    )
    return {
        "status": "prototype_rating_intake" if reliable else "watch",
        "adoption": "lab_only_manual_rating_gate",
        "reason": (
            "Manual ratings were ingested and can be compared to proxy scores, "
            "but more rating volume is needed before changing proxy weights."
        ),
    }


def _write_template_csv(path: Path, template: dict) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TEMPLATE_FIELDS)
        writer.writeheader()
        writer.writerows(template["rows"])


def _readme_text(report: dict) -> str:
    summary = report["summary"]
    return (
        "# Manual Readability Rating Intake Stage 0\n\n"
        "CSV intake and aggregation gate for real human readability ratings.\n\n"
        "Key results:\n\n"
        f"- Status: {summary['status']}\n"
        f"- Template rows: {summary['template_row_count']}\n"
        f"- Rating rows: {summary['rating_row_count']}\n"
        f"- Rated samples: {summary['rated_sample_count']}\n"
        f"- Reviewers: {summary['reviewer_count']}\n"
        f"- Decision: {report['decision']['status']}\n\n"
        "No human ratings are fabricated. Fill `manual_rating_template.csv` "
        "with reviewer rows and rerun the intake command to produce calibrated "
        "rating summaries.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/readability")
    parser.add_argument("--ratings", type=Path, default=ROOT / "data/readability/manual_ratings.csv")
    parser.add_argument("--count-per-source", type=int, default=10)
    parser.add_argument("--rng-seed", type=int, default=20260512)
    args = parser.parse_args()
    benchmark = build_heldout_readability_benchmark(
        count_per_source=args.count_per_source,
        rng_seed=args.rng_seed,
    )
    rows = load_rating_rows(args.ratings)
    report = run_manual_rating_intake_lab(
        benchmark=benchmark,
        rating_rows=rows,
        rng_seed=args.rng_seed,
    )
    write_manual_rating_intake_artifacts(args.output_dir, report)
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
