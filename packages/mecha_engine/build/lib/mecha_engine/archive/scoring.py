"""Bounded candidate fitness scoring for the mecha_engine archive.

Contract sources:

- research/package_specs/mecha_engine_archive_contract_gate.md
  ("Fitness Acceptance")
- research/package_specs/mecha_engine_module_interfaces.md ("archive")

Verbatim semantic port of the calibrated Stage 0 extended fitness: the six
weighted components (survival, readability, validity, bond, mutation
stability, SLIP alignment) with the pinned Stage 0 weights, every component
and the aggregate clamped into ``[0, 1]``, aggregated from the *unrounded*
component values and rounded to six places exactly as the research archive
does. Invalid candidates are scored as failures for reports (validity and
lifecycle collapse to zero); keeping them out of the archive is the
insertion layer's job.
"""

from __future__ import annotations

from copy import deepcopy

from . import _metrics, descriptors

# Pinned Stage 0 extended fitness weights (calibrated research archive).
FITNESS_WEIGHTS: dict[str, float] = {
    "survival": 0.28,
    "readability": 0.24,
    "validity": 0.18,
    "bond": 0.12,
    "mutation_stability": 0.1,
    "slip_alignment": 0.08,
}


def score_candidate(candidate: dict, metrics: dict) -> dict:
    """Return the bounded, JSON-serializable fitness record for a candidate.

    The result carries ``fitness``, ``components``, ``validation``,
    ``readability`` (proxy, with its manual-rating status visible),
    ``lifecycle``, ``slip_alignment``, ``provenance``, and the per-axis
    ``descriptor_metrics`` evidence. Inputs are never mutated.
    """
    resolved = _metrics.resolve_candidate_metrics(candidate, metrics)
    return score_from_resolved(candidate, resolved)


def score_from_resolved(candidate: dict, resolved: dict) -> dict:
    """Build the score record from an already-resolved metric bundle."""
    lifecycle = resolved["lifecycle"]
    components = {
        "survival": _metrics.clamp(lifecycle["survival_ratio"]),
        "readability": resolved["readability_value"],
        "validity": 1.0 if resolved["validation"]["ok"] else 0.0,
        "bond": _metrics.clamp(lifecycle["final_state"].get("bond", 0.0)),
        "mutation_stability": resolved["mutation_stability"],
        "slip_alignment": 1.0 if resolved["slip_alignment_ok"] else 0.0,
    }
    fitness = sum(components[name] * FITNESS_WEIGHTS[name] for name in FITNESS_WEIGHTS)
    provenance = candidate.get("provenance")
    return {
        "fitness": round(_metrics.clamp(fitness), 6),
        "components": {key: round(value, 6) for key, value in components.items()},
        "validation": deepcopy(resolved["validation"]),
        "readability": deepcopy(resolved["readability_record"]),
        "lifecycle": deepcopy(lifecycle),
        "slip_alignment": {
            "ok": resolved["slip_alignment_ok"],
            "score": components["slip_alignment"],
            "profile_supplied": resolved["slip_profile_supplied"],
        },
        "provenance": (
            {"provided": True, "record": deepcopy(provenance)}
            if provenance is not None
            else {"provided": False, "record": None}
        ),
        "descriptor_metrics": descriptors.descriptor_metrics(resolved),
    }


def check_score(score: object) -> dict:
    """Validate a caller-supplied score record before insertion."""
    if not isinstance(score, dict):
        raise ValueError("score must be a mapping from score_candidate")
    fitness = score.get("fitness")
    if isinstance(fitness, bool) or not isinstance(fitness, int | float):
        raise ValueError(f"score fitness must be a number: {fitness!r}")
    if not 0.0 <= float(fitness) <= 1.0:
        raise ValueError(f"score fitness outside 0..1: {fitness!r}")
    validation = score.get("validation")
    if not isinstance(validation, dict) or not isinstance(validation.get("ok"), bool):
        raise ValueError("score must carry a validation result with 'ok'")
    if not isinstance(score.get("components"), dict):
        raise ValueError("score must carry a components mapping")
    return score
