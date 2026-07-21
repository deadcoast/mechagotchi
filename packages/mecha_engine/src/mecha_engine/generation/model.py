"""Generation-model training for the mecha_engine package surface.

Contract sources:

- research/package_specs/mecha_engine_generation_contract_gate.md
  ("Model Acceptance")
- research/package_specs/mecha_engine_module_interfaces.md ("generation")

Self-contained semantic port of the Stage 0 research constrained generator's
training step (grid_genome lab): the model preserves local right/down
adjacency pair counts and token frequencies over the corpus's own grid size
(size-parametric since cycle 09 A3, DR 0029; the token alphabet is
unchanged), which is exactly the local-pattern evidence the constrained
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

# The ratified Stage 0 scale; models now derive their own dimensions from
# the training corpus (DR 0029), these remain as the historical defaults.
GRID_WIDTH = 8
GRID_HEIGHT = 8

# DR 0038: the vocabulary-complete generation alphabet — a VERBATIM
# mirror of the research lab's RICH_TOKENS / RICH_ORGAN_ROLES
# (labs/grid_genome/grid_helpers.py; the same tables the seed corpus
# was authored with). When the lab authority changes, resync verbatim —
# drift is caught by labs/grid_genome/test_package_generation_parity.py.
# token -> (role, material, organ_id, palette_index); "A" is the
# anchor-flagged body cell.
RICH_TOKENS: dict[str, tuple[str, str, str, int]] = {
    "B": ("body", "hard", "core", 1),
    "A": ("body", "hard", "core", 1),
    "S": ("shell", "hard", "carapace", 1),
    "J": ("joint", "joint", "joints", 1),
    "L": ("limb", "hard", "limbs", 1),
    "E": ("eye", "glass", "sensors", 2),
    "M": ("mouth", "soft", "expression", 2),
    "N": ("antenna", "signal", "antennae", 2),
    "P": ("sensor", "signal", "antennae", 2),
    "D": ("decoration", "light", "trim", 2),
    "F": ("effect", "signal", "aura", 2),
}
RICH_ORGAN_ROLES: dict[str, tuple[str, bool]] = {
    "core": ("body_core", True),
    "carapace": ("body_core", False),
    "sensors": ("sensor", True),
    "antennae": ("sensor", False),
    "expression": ("expression", False),
    "joints": ("locomotion", False),
    "limbs": ("locomotion", False),
    "trim": ("ornament", False),
    "aura": ("effect", False),
}
ROLE_TOKENS: dict[str, str] = {
    role: token
    for token, (role, _material, _organ, _index) in RICH_TOKENS.items()
    if token != "A"
}
ORGAN_ORDER: tuple[str, ...] = (
    "core",
    "carapace",
    "sensors",
    "antennae",
    "expression",
    "joints",
    "limbs",
    "trim",
    "aura",
)
TOKENS: tuple[str, ...] = (".", *RICH_TOKENS)

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
    """Project a grid genome onto the token matrix used for training.

    DR 0038: every ratified role projects to its RICH token (the
    standalone anchor role normalizes to "A", the seed corpus's
    anchor-flagged-body convention); legacy-role grids project
    identically to the historical 5-token behavior.
    """
    width, height = grid["grid_size"]
    matrix = [["." for _ in range(width)] for _ in range(height)]
    for cell in grid["cells"]:
        if cell["role"] == "body":
            matrix[cell["y"]][cell["x"]] = "A" if cell["animation_anchor"] else "B"
        elif cell["role"] == "anchor":
            matrix[cell["y"]][cell["x"]] = "A"
        else:
            token = ROLE_TOKENS.get(cell["role"])
            if token is not None:
                matrix[cell["y"]][cell["x"]] = token
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

    # DR 0029 / cycle 09 A3: the model derives its dimensions from the
    # corpus (size-parametric, not size-replacing — an 8x8 corpus trains
    # the identical historical model). Mixed sizes would silently train
    # wrong-position statistics, so they fail loudly instead.
    sizes = {tuple(grid["grid_size"]) for grid in seed_grids}
    if len(sizes) != 1:
        raise ValueError(
            "seed corpus must share a single grid size, found: "
            + ", ".join(f"{w}x{h}" for w, h in sorted(sizes))
        )
    ((width, height),) = sizes

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
        width=width,
        height=height,
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
