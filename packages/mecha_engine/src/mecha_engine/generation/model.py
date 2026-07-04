"""Generation-model training for the mecha_engine package surface.

Contract sources:

- research/package_specs/mecha_engine_generation_contract_gate.md
  ("Model Acceptance")
- research/package_specs/mecha_engine_module_interfaces.md ("generation")

Self-contained semantic port of the Stage 0 research constrained generator's
training step (grid_genome lab): the model preserves local right/down
adjacency pair counts and token frequencies over the fixed 8x8 token
alphabet, which is exactly the local-pattern evidence the constrained
stabilizer needs. Raw Markov-style local statistics are a proposal source
only; the production path is the validator-gated constrained stabilizer in
``generate.py`` (negative check: raw Markov output must never be the sole
production generator).

Training never mutates seed-grid dictionaries and records model metadata
sufficient to identify the training corpus and generator strategy.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from mecha_engine.genome import validate_grid

GRID_WIDTH = 8
GRID_HEIGHT = 8
TOKENS: tuple[str, ...] = (".", "B", "A", "E", "M")

# Production strategy label: constrained WFC-style stabilization gated by
# mecha_engine.genome.validate_grid, never raw Markov sampling.
GENERATOR_STRATEGY = "constrained_wfc_style_stabilizer"
PROPOSAL_SOURCE = "markov_local_adjacency_proposals"


@dataclass(frozen=True)
class GenerationModel:
    """Trained local-pattern evidence for constrained candidate generation.

    ``adjacency`` maps direction ("right"/"down") to per-token successor
    counts; ``token_counts`` holds global token frequencies. ``metadata``
    identifies the training corpus and the generator strategy. The model is
    treated as read-only by every generation path.
    """

    width: int
    height: int
    adjacency: dict[str, dict[str, dict[str, int]]]
    token_counts: dict[str, int]
    total_pairs: int
    metadata: dict


def matrix_from_grid(grid: dict) -> list[list[str]]:
    """Project a grid genome onto the token matrix used for training."""
    width, height = grid["grid_size"]
    matrix = [["." for _ in range(width)] for _ in range(height)]
    for cell in grid["cells"]:
        if cell["role"] == "body":
            matrix[cell["y"]][cell["x"]] = "A" if cell["animation_anchor"] else "B"
        elif cell["role"] == "eye":
            matrix[cell["y"]][cell["x"]] = "E"
        elif cell["role"] == "mouth":
            matrix[cell["y"]][cell["x"]] = "M"
    return matrix


def train_generation_model(seed_grids: list[dict]) -> GenerationModel:
    """Train a constrained generation model from valid seed grids.

    Raises ``ValueError`` for an empty corpus or for corpora containing
    grids that fail ``mecha_engine.genome.validate_grid``. Seed grids are
    read, never mutated.
    """
    if not isinstance(seed_grids, list) or not seed_grids:
        raise ValueError("seed corpus must be a non-empty list of grid genomes")

    invalid: list[str] = []
    for index, grid in enumerate(seed_grids):
        result = validate_grid(grid) if isinstance(grid, dict) else None
        if result is None or not result.ok:
            label = (
                grid.get("grid_id", f"seed_index_{index}")
                if isinstance(grid, dict)
                else f"seed_index_{index}"
            )
            errors = "; ".join(result.errors) if result is not None else "not an object"
            invalid.append(f"{label}: {errors}")
    if invalid:
        raise ValueError("seed corpus contains invalid grids: " + " | ".join(invalid))

    adjacency: dict[str, dict[str, dict[str, int]]] = {"right": {}, "down": {}}
    token_counts: dict[str, int] = {token: 0 for token in TOKENS}
    total_pairs = 0
    for grid in seed_grids:
        matrix = matrix_from_grid(grid)
        for y, row in enumerate(matrix):
            for x, token in enumerate(row):
                token_counts[token] = token_counts.get(token, 0) + 1
                if x + 1 < len(row):
                    _add_pair(adjacency["right"], token, row[x + 1])
                    total_pairs += 1
                if y + 1 < len(matrix):
                    _add_pair(adjacency["down"], token, matrix[y + 1][x])
                    total_pairs += 1

    seed_grid_ids = [grid["grid_id"] for grid in seed_grids]
    metadata = {
        "strategy": GENERATOR_STRATEGY,
        "proposal_source": PROPOSAL_SOURCE,
        "seed_count": len(seed_grids),
        "seed_grid_ids": seed_grid_ids,
        "seed_corpus_sha256": _corpus_digest(seed_grid_ids),
    }
    return GenerationModel(
        width=GRID_WIDTH,
        height=GRID_HEIGHT,
        adjacency=adjacency,
        token_counts=token_counts,
        total_pairs=total_pairs,
        metadata=metadata,
    )


def _add_pair(adjacency: dict[str, dict[str, int]], left: str, right: str) -> None:
    counts = adjacency.setdefault(left, {})
    counts[right] = counts.get(right, 0) + 1


def _corpus_digest(seed_grid_ids: list[str]) -> str:
    payload = "\n".join(seed_grid_ids)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
