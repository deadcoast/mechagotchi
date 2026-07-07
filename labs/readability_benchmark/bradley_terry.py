"""Bradley-Terry pairwise-preference scoring (audit T20, tooling only).

RUN TWO prefers blind pairwise forced choice over rubric scoring for
human judgments. This lab is the ANALYSIS half: given pairwise win
counts, the classic minorization-maximization (MM) algorithm estimates
each item's strength (Hunter 2004), normalized to sum 1. Stdlib only,
deterministic.

STANDING RULE: the tests validate the TOOLING on synthetic pairings,
clearly marked as such — no synthetic result is ever recorded as human
evidence. Real studies follow research/human_studies_protocol.md.
"""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def bradley_terry_strengths(
    wins: dict[tuple[str, str], int],
    *,
    iterations: int = 200,
    tolerance: float = 1e-10,
) -> dict[str, float]:
    """MM estimates from ``wins[(winner, loser)] = count``."""
    items = sorted({name for pair in wins for name in pair})
    if not items:
        return {}
    strengths = {item: 1.0 for item in items}
    win_totals = defaultdict(float)
    pair_counts = defaultdict(float)
    for (winner, loser), count in wins.items():
        win_totals[winner] += count
        key = tuple(sorted((winner, loser)))
        pair_counts[key] += count
    for _ in range(iterations):
        updated = {}
        for item in items:
            denominator = 0.0
            for other in items:
                if other == item:
                    continue
                games = pair_counts.get(tuple(sorted((item, other))), 0.0)
                if games:
                    denominator += games / (
                        strengths[item] + strengths[other]
                    )
            updated[item] = (
                win_totals[item] / denominator if denominator else 0.0
            )
        total = sum(updated.values()) or 1.0
        updated = {item: value / total for item, value in updated.items()}
        delta = max(
            abs(updated[item] - strengths[item]) for item in items
        )
        strengths = updated
        if delta < tolerance:
            break
    return {item: round(value, 6) for item, value in strengths.items()}


def load_pairwise_csv(path: Path) -> dict[tuple[str, str], int]:
    """CSV columns: winner,loser[,count] — the study intake format."""
    wins: dict[tuple[str, str], int] = defaultdict(int)
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            count = int(row.get("count", 1) or 1)
            wins[(row["winner"], row["loser"])] += count
    return dict(wins)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bradley-Terry strengths from a pairwise CSV."
    )
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()
    strengths = bradley_terry_strengths(load_pairwise_csv(args.csv_path))
    print(json.dumps(strengths, indent=2))


if __name__ == "__main__":
    main()
