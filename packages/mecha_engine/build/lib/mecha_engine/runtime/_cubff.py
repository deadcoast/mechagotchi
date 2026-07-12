"""Private CuBFF feature mirror for ``mecha_engine.runtime`` (R2.5).

VERBATIM port of ``extract_cubff_features``/``features_to_traits`` and
their stdlib helpers from the lab authority
``labs/cubff_transducer/cubff_transducer.py`` (decision record 0020;
the ``_slip`` mirror discipline). When the authority changes, resync
this file verbatim — drift is caught by the lab-side parity pin
``labs/cubff_transducer/test_package_cubff_parity.py``. Only pressure
scalars derived here may cross into evolution (the semantic-compiler
rule: lineage dynamics -> mutation weights, never tape -> tokens).
"""

from __future__ import annotations

import math
from collections import Counter


def extract_cubff_features(snapshot: dict) -> dict:
    tape = _tape_values(snapshot)
    replication_scores = [
        float(value) for value in snapshot.get("replication_scores", []) if _is_number(value)
    ]
    lineage_events = snapshot.get("lineage_events", [])
    if not isinstance(lineage_events, list):
        lineage_events = []

    entropy = _normalized_entropy(tape)
    motif_counts = _motif_counts(tape)
    motif_repetition_rate = _motif_repetition_rate(motif_counts)
    instruction_diversity = len(set(tape)) / len(tape) if tape else 0
    high_replication_count = sum(1 for score in replication_scores if score >= 48)
    replication_rate = (
        high_replication_count / len(replication_scores) if replication_scores else 0
    )
    score_sum = sum(replication_scores)
    replication_dominance = max(replication_scores) / score_sum if score_sum else 0
    lineage_churn = min(1, len(lineage_events) / max(1, len(replication_scores)))
    compression_ratio = _compression_ratio(snapshot, tape)
    instability = _clamp(
        0.45 * entropy
        + 0.3 * lineage_churn
        + 0.25 * (1 - replication_dominance if replication_scores else 0.5)
    )
    semantic_pressure = _clamp(
        0.5 * replication_rate + 0.25 * motif_repetition_rate + 0.25 * lineage_churn
    )

    return {
        "snapshot_id": str(snapshot.get("snapshot_id", "cubff_snapshot")),
        "epoch": int(snapshot.get("epoch", 0)) if isinstance(snapshot.get("epoch", 0), int) else 0,
        "language": str(snapshot.get("language", "unknown")),
        "tape_length": len(tape),
        "symbol_entropy": round(entropy, 6),
        "instruction_diversity": round(instruction_diversity, 6),
        "motif_repetition_rate": round(motif_repetition_rate, 6),
        "replication_rate": round(replication_rate, 6),
        "replication_dominance": round(replication_dominance, 6),
        "lineage_churn": round(lineage_churn, 6),
        "compression_ratio": round(compression_ratio, 6),
        "instability": round(instability, 6),
        "semantic_pressure": round(semantic_pressure, 6),
        "top_motifs": [
            {"motif": motif, "count": count}
            for motif, count in sorted(
                motif_counts.items(), key=lambda item: (-item[1], item[0])
            )[:5]
        ],
    }

def features_to_traits(features: dict) -> dict:
    mutation_pressure = _clamp(
        0.45 * features["instability"]
        + 0.35 * features["semantic_pressure"]
        + 0.2 * features["instruction_diversity"]
    )
    structural_pressure = _clamp(
        0.55 * features["replication_rate"] + 0.45 * features["motif_repetition_rate"]
    )
    curiosity = _clamp(0.25 + 0.55 * features["symbol_entropy"])
    neediness = _clamp(0.2 + 0.5 * features["lineage_churn"])
    sleepiness = _clamp(0.75 - 0.45 * features["replication_rate"])

    return {
        "mutation_pressure": round(mutation_pressure, 6),
        "structural_pressure": round(structural_pressure, 6),
        "animation_instability": round(features["instability"], 6),
        "temperament": {
            "curiosity": round(curiosity, 6),
            "neediness": round(neediness, 6),
            "sleepiness": round(sleepiness, 6),
        },
    }

def _tape_values(snapshot: dict) -> list[int]:
    raw_tape = snapshot.get("tape", snapshot.get("soup", []))
    if isinstance(raw_tape, bytes):
        return list(raw_tape)
    if not isinstance(raw_tape, list):
        return []
    return [int(value) % 256 for value in raw_tape if isinstance(value, int)]


def _normalized_entropy(values: list[int]) -> float:
    if not values:
        return 0
    counts = Counter(values)
    entropy = 0.0
    for count in counts.values():
        probability = count / len(values)
        entropy -= probability * math.log2(probability)
    return entropy / 8

def _motif_counts(values: list[int]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for index in range(len(values) - 2):
        motif = f"{values[index]},{values[index + 1]},{values[index + 2]}"
        counts[motif] = counts.get(motif, 0) + 1
    return counts


def _motif_repetition_rate(motif_counts: dict[str, int]) -> float:
    if not motif_counts:
        return 0
    repeated = sum(count - 1 for count in motif_counts.values() if count > 1)
    total = sum(motif_counts.values())
    return repeated / total if total else 0

def _compression_ratio(snapshot: dict, tape: list[int]) -> float:
    brotli_size = snapshot.get("brotli_size")
    if not _is_number(brotli_size) or not tape:
        return 0
    return float(brotli_size) / len(tape)

def _is_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)

def _mean(values) -> float:
    items = list(values)
    if not items:
        return 0
    return round(sum(items) / len(items), 6)

def _clamp(value: float) -> float:
    return max(0, min(1, float(value)))
