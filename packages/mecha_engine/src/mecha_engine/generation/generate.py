"""Validator-gated constrained candidate generation for mecha_engine.

Contract sources:

- research/package_specs/mecha_engine_generation_contract_gate.md
  ("Candidate Acceptance", "Batch Acceptance", "SLIP Acceptance",
  "Negative Checks")
- research/package_specs/mecha_engine_module_interfaces.md ("generation")

Self-contained semantic port of the Stage 0 research constrained generator
(grid_genome lab), including the 2026-07-04 mutation-temperature jitter
(review finding L-12). Raw Markov-style local adjacency statistics only
*propose* single-cell resamples; every proposal must pass
``mecha_engine.genome.validate_grid`` (plus SLIP alignment when a profile is
supplied) before it is kept, so raw Markov output is never the production
path. Determinism: all randomness flows from streams seeded with the
caller-supplied RNG seed and the candidate grid id, so the same parent,
model, SLIP profile, and seed always reproduce the same candidate.

Parity note: ``generate_batch`` keeps the Stage 0 corpus candidate naming
(``mg_constrained_NNN``) and the research generator's exact RNG consumption
order, so package batches remain byte-comparable with the research
generator's output for the same seed corpus and RNG seed (candidate
``metadata`` additionally carries the package generation trace).

Inputs are never mutated: not the parent grid, not the seed corpus, not the
model, and not the SLIP profile.
"""

from __future__ import annotations

import hashlib
import random
from copy import deepcopy

from mecha_engine.genome import validate_grid

from mecha_engine.slip import is_grid_aligned, validate_slip
from .model import (
    GENERATOR_STRATEGY,
    ORGAN_ORDER,
    PROPOSAL_SOURCE,
    RICH_ORGAN_ROLES,
    RICH_TOKENS,
    GenerationModel,
    matrix_from_grid,
    train_generation_model,
)

# Stage 0 palette table (research corpus builder); palette ids mirror the
# SLIP palette enum in research/slip/slip.schema.json.
PALETTES: dict[str, list[str]] = {
    "lcd_green": ["#07140d", "#5dbb63", "#d8ffd6"],
    "gameboy_gray": ["#111814", "#7e8f76", "#d7dfc7"],
    "amber_terminal": ["#1c1005", "#d98428", "#ffe0a3"],
    "crt_blue": ["#06131f", "#3e8fbf", "#d6f3ff"],
    "pocket_plum": ["#160e1f", "#7e5aa6", "#f2dcff"],
}

# Per-rate ceilings for the deterministic mutation-rate jitter (review
# finding L-12). Without a SLIP profile the ceilings are the fixed default
# vector emitted by grid construction; with a profile they are the profile's
# *_max caps, so jittered grids always stay SLIP-aligned.
DEFAULT_MUTATION_RATE_CAPS: dict[str, float] = {
    "cell_mutation_rate": 0.05,
    "organ_shift_rate": 0.02,
    "palette_shift_rate": 0.01,
    "symmetry_break_rate": 0.01,
}

SLIP_MUTATION_CAP_KEYS: dict[str, str] = {
    "cell_mutation_rate": "cell_mutation_rate_max",
    "organ_shift_rate": "organ_shift_rate_max",
    "palette_shift_rate": "palette_shift_rate_max",
    "symmetry_break_rate": "symmetry_break_rate_max",
}

PROPOSAL_ATTEMPTS = 12
DEFAULT_RNG_SEED = 0
METADATA_SOURCE = "mecha_engine.generation"
TRACE_METADATA_KEY = "generation_trace"
BATCH_GRID_ID_TEMPLATE = "mg_constrained_{index:03d}"

# DR 0038's rider: the structural resample-temperature knob. OFF by
# default (None = the historical 12-attempt loop, byte-identical); when
# set it must sit in (0, 2] and scales the proposal-attempt count to
# round(12 * (1 + temperature)). Mirrors the research generator.
MAX_RESAMPLE_TEMPERATURE = 2.0


def _proposal_attempts(resample_temperature: float | None) -> int:
    if resample_temperature is None:
        return PROPOSAL_ATTEMPTS
    if (
        isinstance(resample_temperature, bool)
        or not isinstance(resample_temperature, int | float)
        or not 0 < resample_temperature <= MAX_RESAMPLE_TEMPERATURE
    ):
        raise ValueError(
            "resample_temperature must be a number in (0, "
            f"{MAX_RESAMPLE_TEMPERATURE}]: {resample_temperature!r}"
        )
    return round(PROPOSAL_ATTEMPTS * (1 + resample_temperature))


def generate_candidate(
    parent_grid: dict,
    model: GenerationModel,
    slip_profile: dict | None = None,
    rng_seed: int | None = None,
    *,
    resample_temperature: float | None = None,
) -> dict:
    """Generate one valid child candidate from an explicit parent grid.

    The parent must pass ``mecha_engine.genome.validate_grid`` (rejected
    before any proposal generation otherwise); a supplied SLIP profile is
    validated first and the parent must be able to satisfy it. ``rng_seed``
    ``None`` uses the documented fixed default seed ``0`` so output stays
    deterministic. The returned candidate passes package genome validation,
    preserves lineage (parent id, generation number, ancestor ids, mutation
    events), and carries the generation trace used by
    ``explain_generation``.
    """
    if not isinstance(model, GenerationModel):
        raise ValueError("model must be a GenerationModel from train_generation_model")
    parent_result = validate_grid(parent_grid) if isinstance(parent_grid, dict) else None
    if parent_result is None or not parent_result.ok:
        errors = parent_result.errors if parent_result is not None else ["not an object"]
        raise ValueError(
            "parent grid failed package genome validation before proposal "
            "generation: " + "; ".join(errors)
        )
    model.validate_for(parent_grid["grid_size"])
    if slip_profile is not None:
        profile_result = validate_slip(slip_profile)
        if not profile_result.ok:
            raise ValueError("SLIP profile is invalid: " + "; ".join(profile_result.errors))
        parent_alignment = is_grid_aligned(parent_grid, slip_profile)
        if not parent_alignment.ok:
            raise ValueError(
                "parent grid cannot satisfy SLIP constraints: "
                + "; ".join(parent_alignment.errors)
            )

    attempts = _proposal_attempts(resample_temperature)
    seed = DEFAULT_RNG_SEED if rng_seed is None else rng_seed
    grid_id = _candidate_grid_id(parent_grid["grid_id"], seed)
    rng = random.Random(f"{seed}:{grid_id}")
    return _stabilize(
        parent_grid,
        model,
        grid_id=grid_id,
        rng=rng,
        rng_seed=seed,
        slip=slip_profile,
        base_mutation_events=["parent_grid_supplied", "validator_gated_resample"],
        proposal_attempts=attempts,
    )


def generate_batch(
    seed_grids: list[dict],
    count: int,
    slip_profile: dict | None = None,
    rng_seed: int | None = None,
    *,
    resample_temperature: float | None = None,
) -> list[dict]:
    """Generate exactly ``count`` valid, traceable candidates from seeds.

    Trains the constrained model from ``seed_grids`` (rejecting empty or
    invalid corpora), filters the parent pool by SLIP alignment when a
    profile is supplied (failing clearly when no seed can satisfy it), and
    produces deterministic batches with unique candidate ids for the same
    inputs and RNG seed. Every returned candidate passes
    ``mecha_engine.genome.validate_grid``.
    """
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ValueError(f"count must be a non-negative integer: {count}")
    attempts = _proposal_attempts(resample_temperature)
    model = train_generation_model(seed_grids)
    if slip_profile is not None:
        profile_result = validate_slip(slip_profile)
        if not profile_result.ok:
            raise ValueError("SLIP profile is invalid: " + "; ".join(profile_result.errors))

    parent_pool = _filter_seed_pool(seed_grids, slip_profile)
    seed = DEFAULT_RNG_SEED if rng_seed is None else rng_seed

    candidates: list[dict] = []
    for index in range(count):
        grid_id = BATCH_GRID_ID_TEMPLATE.format(index=index)
        rng = random.Random(f"{seed}:{grid_id}")
        parent = rng.choice(parent_pool)
        candidates.append(
            _stabilize(
                parent,
                model,
                grid_id=grid_id,
                rng=rng,
                rng_seed=seed,
                slip=slip_profile,
                base_mutation_events=["seed_parent_selected", "validator_gated_resample"],
                proposal_attempts=attempts,
            )
        )
    return candidates


def _filter_seed_pool(seed_grids: list[dict], slip: dict | None) -> list[dict]:
    if slip is None:
        return list(seed_grids)
    aligned = [grid for grid in seed_grids if is_grid_aligned(grid, slip).ok]
    if not aligned:
        raise ValueError("no seed grids satisfy SLIP constraints")
    return aligned


def _stabilize(
    parent_grid: dict,
    model: GenerationModel,
    *,
    grid_id: str,
    rng: random.Random,
    rng_seed: int,
    slip: dict | None,
    base_mutation_events: list[str],
    proposal_attempts: int = PROPOSAL_ATTEMPTS,
) -> dict:
    """Run the validator-gated constrained stabilization pipeline.

    Ports the research generator's exact proposal loop and RNG consumption
    order: twelve local resample proposals, each rebuilt as a full grid and
    kept only when it passes package genome validation (and SLIP alignment
    when constrained), then anchor variation and the deterministic
    mutation-temperature jitter.
    """
    parent_grid_id = parent_grid["grid_id"]
    parent_lineage = parent_grid.get("lineage", {})
    parent_generation = (
        parent_lineage.get("generation", 0) if isinstance(parent_lineage, dict) else 0
    )
    parent_ancestors = (
        list(parent_lineage.get("ancestor_ids", []))
        if isinstance(parent_lineage, dict)
        else []
    )

    matrix = matrix_from_grid(parent_grid)
    accepted_proposals = 0
    rejected_proposals = 0
    for _ in range(proposal_attempts):
        proposal = deepcopy(matrix)
        _attempt_local_resample(proposal, model, rng)
        candidate = _grid_from_matrix(
            grid_id,
            proposal,
            _choose_palette(rng, slip),
            rng_seed,
            mutation_events=base_mutation_events,
            parent_grid_id=parent_grid_id,
            parent_generation=parent_generation,
            parent_ancestors=parent_ancestors,
        )
        if _acceptable(candidate, slip):
            matrix = proposal
            accepted_proposals += 1
        else:
            rejected_proposals += 1

    safe_variant = _grid_from_matrix(
        grid_id,
        matrix,
        _choose_palette(rng, slip),
        rng_seed,
        mutation_events=base_mutation_events,
        parent_grid_id=parent_grid_id,
        parent_generation=parent_generation,
        parent_ancestors=parent_ancestors,
    )
    variant = _ensure_semantic_variation(safe_variant, rng)
    _apply_mutation_temperature(variant, grid_id, rng_seed, slip)

    validation = validate_grid(variant)
    if not validation.ok:
        # Never expected on the constrained path; fail loudly with trace
        # data instead of silently dropping the candidate.
        raise ValueError(
            f"constrained generation produced an invalid candidate {grid_id} "
            f"(parent {parent_grid_id}, rng_seed {rng_seed}): "
            + "; ".join(validation.errors)
        )

    if slip is not None:
        alignment = is_grid_aligned(variant, slip)
        slip_alignment = {
            "checked": True,
            "profile_id": slip.get("profile_id"),
            "ok": alignment.ok,
            "errors": list(alignment.errors),
        }
        if not alignment.ok:
            raise ValueError(
                f"constrained generation produced a SLIP-misaligned candidate "
                f"{grid_id}: " + "; ".join(alignment.errors)
            )
    else:
        slip_alignment = {"checked": False, "profile_id": None, "ok": None, "errors": []}

    variant["metadata"][TRACE_METADATA_KEY] = {
        "generator_strategy": GENERATOR_STRATEGY,
        "proposal_source": PROPOSAL_SOURCE,
        "rng_seed": rng_seed,
        "parent_grid_id": parent_grid_id,
        "proposal_attempts": proposal_attempts,
        "accepted_proposals": accepted_proposals,
        "rejected_proposals": rejected_proposals,
        "validation": {"ok": validation.ok, "errors": list(validation.errors)},
        "slip_alignment": slip_alignment,
        "model": {
            "strategy": model.metadata.get("strategy"),
            "seed_count": model.metadata.get("seed_count"),
            "seed_corpus_sha256": model.metadata.get("seed_corpus_sha256"),
        },
    }
    return variant


def _candidate_grid_id(parent_grid_id: str, rng_seed: int) -> str:
    digest = hashlib.sha256(f"{parent_grid_id}:{rng_seed}".encode("utf-8")).hexdigest()
    return f"gen_{digest[:16]}"


def _attempt_local_resample(
    matrix: list[list[str]], model: GenerationModel, rng: random.Random
) -> None:
    x = rng.randrange(model.width)
    y = rng.randrange(model.height)
    candidates = _candidate_tokens(matrix, model, x, y)
    if not candidates:
        return
    matrix[y][x] = _weighted_sample(candidates, rng)


def _candidate_tokens(
    matrix: list[list[str]], model: GenerationModel, x: int, y: int
) -> dict[str, int]:
    candidates = dict(model.token_counts)
    for token in list(candidates):
        if not _allowed_at(matrix, model, x, y, token):
            del candidates[token]
    return candidates


def _allowed_at(
    matrix: list[list[str]], model: GenerationModel, x: int, y: int, token: str
) -> bool:
    adjacency = model.adjacency
    width = model.width
    height = model.height
    if x > 0 and token not in adjacency["right"].get(matrix[y][x - 1], {}):
        return False
    if x + 1 < width and matrix[y][x + 1] not in adjacency["right"].get(token, {}):
        return False
    if y > 0 and token not in adjacency["down"].get(matrix[y - 1][x], {}):
        return False
    if y + 1 < height and matrix[y + 1][x] not in adjacency["down"].get(token, {}):
        return False
    return True


def _weighted_sample(counts: dict[str, int], rng: random.Random) -> str:
    total = sum(counts.values())
    pick = rng.randint(1, total)
    cursor = 0
    for token, count in sorted(counts.items()):
        cursor += count
        if pick <= cursor:
            return token
    raise RuntimeError("unreachable sample state")


def _choose_palette(rng: random.Random, slip: dict | None) -> str:
    if slip is None:
        return rng.choice(sorted(PALETTES))
    return rng.choice(sorted(slip["grid"]["allowed_palettes"]))


def _acceptable(grid: dict, slip: dict | None) -> bool:
    if not validate_grid(grid).ok:
        return False
    return slip is None or is_grid_aligned(grid, slip).ok


def _cell(
    x: int,
    y: int,
    *,
    visual: str,
    role: str,
    material: str,
    organ: str,
    animation_anchor: bool = False,
) -> dict:
    return {
        "x": x,
        "y": y,
        "visual": visual,
        "role": role,
        "material": material,
        "mutation_weight": 0.1,
        "animation_anchor": animation_anchor,
        "organ": organ,
        "stress": 0,
        "damage": 0,
        "locked": False,
    }


def _grid_from_matrix(
    grid_id: str,
    matrix: list[list[str]],
    palette_id: str,
    rng_seed: int,
    *,
    mutation_events: list[str],
    parent_grid_id: str,
    parent_generation: int,
    parent_ancestors: list[str],
) -> dict:
    """Build a schema-compatible grid genome from a token matrix.

    Lineage preserves the parent chain: generation is the parent's
    generation plus one and ancestor ids extend the parent's ancestor list
    (for Stage 0 seed parents this reduces to the research generator's
    generation 1 / single-ancestor lineage).
    """
    palette = PALETTES[palette_id]
    cells: list[dict] = []
    organ_cells: dict[str, list[list[int]]] = {}

    # DR 0038: the full RICH_TOKENS alphabet reconstructs — every token
    # synthesizes its ratified role/material/organ pairing (mirrors the
    # research grid_from_matrix; legacy-only matrices reconstruct
    # byte-identically to the historical shape).
    for y, row in enumerate(matrix):
        for x, token in enumerate(row):
            if token == "." or token not in RICH_TOKENS:
                continue
            role, material, organ, palette_index = RICH_TOKENS[token]
            cells.append(
                _cell(
                    x,
                    y,
                    visual=palette[palette_index],
                    role=role,
                    material=material,
                    organ=organ,
                    animation_anchor=token == "A",
                )
            )
            organ_cells.setdefault(organ, []).append([x, y])

    organs: dict[str, dict] = {
        "core": {
            "role": "body_core",
            "cells": organ_cells.get("core", []),
            "required": True,
        },
        "sensors": {
            "role": "sensor",
            "cells": organ_cells.get("sensors", []),
            "required": True,
        },
    }
    for organ_id in ORGAN_ORDER:
        if organ_id in organs or organ_id not in organ_cells:
            continue
        organ_role, organ_required = RICH_ORGAN_ROLES[organ_id]
        organs[organ_id] = {
            "role": organ_role,
            "cells": organ_cells[organ_id],
            "required": organ_required,
        }

    return {
        "grid_id": grid_id,
        "schema_version": "0.1.0",
        "parent_grid_id": parent_grid_id,
        "grid_size": [len(matrix[0]), len(matrix)],
        "cells": cells,
        "organs": organs,
        "palette": {
            "palette_id": palette_id,
            "colors": palette,
            "background_index": 0,
        },
        "mutation": {
            "cell_mutation_rate": 0.05,
            "organ_shift_rate": 0.02,
            "palette_shift_rate": 0.01,
            "symmetry_break_rate": 0.01,
        },
        "lineage": {
            "generation": parent_generation + 1,
            "ancestor_ids": [*parent_ancestors, parent_grid_id],
            "mutation_events": list(mutation_events),
        },
        "metadata": {"source": METADATA_SOURCE, "rng_seed": rng_seed},
    }


def _ensure_semantic_variation(grid: dict, rng: random.Random) -> dict:
    variant = deepcopy(grid)
    core_cells = [cell for cell in variant["cells"] if cell.get("organ") == "core"]
    if core_cells:
        for cell in core_cells:
            cell["animation_anchor"] = False
        rng.choice(core_cells)["animation_anchor"] = True
        if "anchor_repositioned" not in variant["lineage"]["mutation_events"]:
            variant["lineage"]["mutation_events"].append("anchor_repositioned")
    return variant if validate_grid(variant).ok else grid


def _apply_mutation_temperature(
    grid: dict, grid_id: str, rng_seed: int, slip: dict | None
) -> None:
    """Deterministically vary the candidate's mutation vector (finding L-12).

    Each candidate draws a "mutation temperature" in [0.05, 1.0) from its
    own dedicated RNG stream (separate from the structural stream, so cell
    layouts match the pre-jitter generator byte for byte) and scales every
    rate ceiling by it: ``rate = round(cap * temperature, 6)``. The stream
    is seeded with ``f"{rng_seed}:{grid_id}:mutation"`` so the same seed
    always reproduces the same vector, and rates stay in (0, cap], keeping
    both genome validation (rates in [0, 1]) and SLIP alignment (rates at or
    below the profile's *_max caps) satisfied.
    """
    rng = random.Random(f"{rng_seed}:{grid_id}:mutation")
    temperature = 0.05 + 0.95 * rng.random()
    caps = DEFAULT_MUTATION_RATE_CAPS
    if slip is not None:
        caps = {
            rate_key: float(slip["mutation"][cap_key])
            for rate_key, cap_key in SLIP_MUTATION_CAP_KEYS.items()
        }
    grid["mutation"] = {
        rate_key: round(cap * temperature, 6) for rate_key, cap in caps.items()
    }
