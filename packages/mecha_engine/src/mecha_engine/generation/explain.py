"""Generation explanations for lineage, archive scoring, and provenance.

Contract source: research/package_specs/mecha_engine_generation_contract_gate.md
("Explanation Acceptance"): ``explain_generation(candidate)`` returns a
JSON-serializable dictionary with at least ``grid_id``, ``parent_grid_id``,
``generator_strategy``, ``rng_seed``, ``mutation_events``, ``validation``,
``slip_alignment``, ``accepted_proposals``, and ``rejected_proposals`` —
sufficient for lineage, archive scoring, debugging, and provenance without
access to any research lab module.
"""

from __future__ import annotations

from copy import deepcopy

from .generate import TRACE_METADATA_KEY


def explain_generation(candidate: dict) -> dict:
    """Return the JSON-serializable generation trace for a candidate.

    The candidate must carry the generation trace produced by
    ``generate_candidate`` / ``generate_batch``; a grid without one is
    rejected with ``ValueError`` instead of returning a partial
    explanation. The candidate is never mutated.
    """
    if not isinstance(candidate, dict):
        raise ValueError("candidate must be a grid genome dictionary")
    metadata = candidate.get("metadata")
    trace = metadata.get(TRACE_METADATA_KEY) if isinstance(metadata, dict) else None
    if not isinstance(trace, dict):
        raise ValueError(
            "candidate carries no mecha_engine generation trace; only "
            "candidates produced by mecha_engine.generation can be explained"
        )

    lineage = candidate.get("lineage", {})
    mutation_events = (
        list(lineage.get("mutation_events", [])) if isinstance(lineage, dict) else []
    )
    return {
        "grid_id": candidate.get("grid_id"),
        "parent_grid_id": trace.get("parent_grid_id"),
        "generator_strategy": trace.get("generator_strategy"),
        "proposal_source": trace.get("proposal_source"),
        "rng_seed": trace.get("rng_seed"),
        "lineage_generation": lineage.get("generation") if isinstance(lineage, dict) else None,
        "ancestor_ids": (
            list(lineage.get("ancestor_ids", [])) if isinstance(lineage, dict) else []
        ),
        "mutation_events": mutation_events,
        "validation": deepcopy(trace.get("validation")),
        "slip_alignment": deepcopy(trace.get("slip_alignment")),
        "proposal_attempts": trace.get("proposal_attempts"),
        "accepted_proposals": trace.get("accepted_proposals"),
        "rejected_proposals": trace.get("rejected_proposals"),
        "model": deepcopy(trace.get("model")),
    }
