"""The hatchery — species generation in the client (F8, MVP 0.2).

Generation stops being a fixtures-only path: founders are GENERATED
through the promoted constrained surfaces (`generation.generate_batch`
— profile-weighted parent filtering, validator-gated output,
deterministic under seeds; DR 0031's WFC remains the era-side
generator inside the engine) and every hatched creature is LEGIBLE:
it carries `explain_generation`'s verbatim trace, and the origin line
the client shows is built only from trace fields — the creature's
provenance is engine truth, never a caption.
"""

from __future__ import annotations

from mecha_engine.generation import explain_generation, generate_batch


def hatch_founders(
    seed_grids: list[dict],
    slip_profile: dict,
    *,
    count: int = 1,
    rng_seed: int,
) -> list[dict]:
    """Hatch ``count`` new founders under the covenant.

    Each entry is ``{"grid", "explanation"}`` — the candidate exactly
    as the engine produced it, and its generation trace verbatim."""
    candidates = generate_batch(
        seed_grids, count, slip_profile=slip_profile, rng_seed=rng_seed
    )
    return [
        {"grid": candidate, "explanation": explain_generation(candidate)}
        for candidate in candidates
    ]


def origin_summary(explanation: dict) -> str:
    """One display line, trace fields only."""
    return (
        f"{explanation['generator_strategy']} from "
        f"{explanation['parent_grid_id']} · proposals "
        f"{explanation['accepted_proposals']}/"
        f"{explanation['proposal_attempts']} · gen "
        f"{explanation['lineage_generation']}"
    )
