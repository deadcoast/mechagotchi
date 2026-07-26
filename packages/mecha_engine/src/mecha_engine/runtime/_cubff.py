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

# DR 0045 (cycle 22 L5): the ten bff_noheads instruction bytes,
# MIRRORED VERBATIM from labs/cubff_transducer/structured_decoder.py's
# INSTRUCTION_TOKENS (the J4 authority) — cited, never imported across
# the package boundary, because this mirror cannot import labs.
CUBFF_INSTRUCTION_BYTES = frozenset(
    ord(character) for character in "[]<>{}+-.,"
)

# The theoretical maximum organization ratio. A tape whose every byte is
# an instruction has density n, hence ratio n / (n * 10/256) = 256/10 —
# INDEPENDENT of tape length. Derived from the language's own alphabet,
# never calibrated on the corpus, which is what keeps DR 0045's gate
# honest.
ORGANIZATION_CEILING = 256 / len(CUBFF_INSTRUCTION_BYTES)

# Pre-registered (DR 0045): density may contribute at most 0.5 to a
# pressure in [0,1] — enough to matter, never enough to dominate the
# three incumbent terms.
CUBFF_DENSITY_WEIGHT = 0.5


def organization_of(tape: list[int]) -> dict:
    """Instruction density as a measured departure from randomness.

    A uniformly random tape of length n carries ``n * 10/256``
    instruction bytes, so ``ratio`` is 1.0 at chance and rises as the
    soup organizes. ``signal`` maps that onto [0,1] against the
    language's theoretical ceiling.

    This is the one channel the CHECKPOINT format carries that rises
    with organization: entropy and instruction diversity both fall,
    and replication_rate / lineage_churn are structurally absent
    (DR 0043 clause 3), which is why the promoted math reads a
    replicator-dominated soup as calm.
    """
    length = len(tape)
    if not length:
        return {"density": 0.0, "expectation": 0.0, "ratio": 0.0, "signal": 0.0}
    density = float(sum(1 for byte in tape if byte in CUBFF_INSTRUCTION_BYTES))
    expectation = length * len(CUBFF_INSTRUCTION_BYTES) / 256
    ratio = density / expectation if expectation else 0.0
    signal = (ratio - 1.0) / (ORGANIZATION_CEILING - 1.0)
    return {
        "density": round(density, 6),
        "expectation": round(expectation, 6),
        "ratio": round(ratio, 6),
        "signal": round(_clamp(signal), 6),
    }


def extract_cubff_features(snapshot: dict, *, include_density: bool = False) -> dict:
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

    features = {
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
    if include_density:
        # DR 0045: an ADDITIVE observation. Off, the dict above is
        # byte-identical to the incumbent's (pinned).
        organization = organization_of(tape)
        features["instruction_density"] = organization["density"]
        features["density_expectation"] = organization["expectation"]
        features["organization_ratio"] = organization["ratio"]
        features["organization_signal"] = organization["signal"]
    return features

def features_to_traits(features: dict, *, density_weight: float = 0.0) -> dict:
    """Traits from features; ``density_weight`` is DR 0045's rider.

    At weight 0.0 this is the incumbent formula exactly (pinned). A
    non-zero weight REQUIRES the density features — a silent zero
    contribution would hide a wiring bug, so the KeyError is deliberate.
    """
    mutation_pressure = _clamp(
        0.45 * features["instability"]
        + 0.35 * features["semantic_pressure"]
        + 0.2 * features["instruction_diversity"]
    )
    if density_weight:
        mutation_pressure = _clamp(
            mutation_pressure + density_weight * features["organization_signal"]
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
