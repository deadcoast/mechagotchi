"""Wound-site repair — the promoted site-aware surface of mecha_engine.repair.

Contract sources:

- research/package_specs/mecha_engine_repair_interface_spec.md
  ("The observability contract", "Required public surface",
  "Validity-guard semantics")
- research/decision_records/0006-create-mecha-engine-repair-target.md
  (verbatim lab semantics — fill order, guard substitutions, metadata,
  grid-id suffix — pinned by the lab-side parity test)

The validity guard consults ``mecha_engine.genome.validate_grid`` — the
target-free grid validator — plus, when the active ``slip_profile`` is
supplied, the private SLIP alignment port (an engine-native constraint
set, not a template). No template, no destroyed tokens.
"""

from __future__ import annotations

from mecha_engine.genome import validate_grid

from ._features import CLASS_TOKENS, neighborhood_features, softmax_probs
from ._grids import grid_from_matrix, matrix_from_grid
from mecha_engine.slip import is_grid_aligned


def repair_wound_sites(
    damaged_grid: dict,
    model: dict,
    *,
    wound_sites: list[list[int]] | None = None,
    validity_guard: bool = True,
    slip_profile: dict | None = None,
) -> dict:
    """Refill exactly the cells the damage event reports as destroyed.

    Observability contract: the arm receives the damage event's destroyed
    positions (``metadata.removed_cells``) but never the destroyed tokens and
    never a target template — every token is predicted by the trained
    softmax rule. Sites are filled most-confident-first so later fills see
    earlier ones as live neighborhood context; the procedure is fully
    deterministic.

    With ``validity_guard`` on, a refill that breaks a hard grid invariant is
    repaired by substituting alternative live tokens at wound sites —
    least-confident fill first, next tokens in descending model
    probability — accepting only substitutions that strictly reduce the
    validation error count. The guard consults the target-free validator
    only; it never empties a site and never sees a template.

    With ``slip_profile`` supplied (the engine-native constraint set active
    at runtime), the guard additionally counts SLIP alignment errors, so a
    destroyed profile-required organ is refilled back into an aligned
    creature (runtime integration finding, 2026-07-05). The profile
    constrains every creature of its kind and carries nothing about this
    creature's silhouette or destroyed tokens — no template enters.
    """
    weights = model["weights"]
    matrix = matrix_from_grid(damaged_grid)
    if wound_sites is None:
        wound_sites = damaged_grid["metadata"]["removed_cells"]
    site_count = len(wound_sites)
    pending = [(x, y) for x, y in wound_sites if matrix[y][x] == "."]
    fill_confidence: dict[tuple[int, int], float] = {}
    while pending:
        best_choice = None
        for x, y in pending:
            probs = softmax_probs(weights, neighborhood_features(matrix, x, y))
            live_class = max(range(1, len(CLASS_TOKENS)), key=lambda c: probs[c])
            if best_choice is None or probs[live_class] > best_choice[0]:
                best_choice = (probs[live_class], x, y, CLASS_TOKENS[live_class])
        confidence, x, y, token = best_choice
        matrix[y][x] = token
        fill_confidence[(x, y)] = confidence
        pending.remove((x, y))

    substitutions = 0
    if validity_guard:
        matrix, substitutions = _wound_fill_validity_guard(
            matrix,
            fill_confidence,
            weights,
            damaged_grid,
            slip_profile=slip_profile,
        )

    repaired = grid_from_matrix(
        grid_id=f"{damaged_grid.get('grid_id', 'grid')}_wound_repaired",
        matrix=matrix,
        palette=damaged_grid.get("palette", {}),
        parent_grid_id=damaged_grid.get("grid_id"),
        source="learned_wound_site_softmax_repair",
        mutation_events=[
            "ca_damage_observed",
            "learned_wound_site_softmax_repair",
        ],
        generation_delta=1,
    )
    repaired["metadata"]["learned_model_id"] = model.get("model_id")
    repaired["metadata"]["target_template_used"] = False
    repaired["metadata"]["wound_site_count"] = site_count
    repaired["metadata"]["validity_guard_substitutions"] = substitutions
    return repaired


def _wound_fill_validity_guard(
    matrix: list[list[str]],
    fill_confidence: dict[tuple[int, int], float],
    weights: list[list[float]],
    source_grid: dict,
    *,
    slip_profile: dict | None = None,
) -> tuple[list[list[str]], int]:
    """Substitute wound-site tokens until the grid validates, or give up.

    Greedy hill-climb on the combined error count — hard validator errors
    plus, when the active ``slip_profile`` is supplied, SLIP alignment
    errors: sites in ascending fill-confidence order (the least confident
    fill is the most likely to be wrong), alternative live tokens in
    descending model probability with class-index tie-break. Only strict
    error reductions are accepted, and each pass is bounded, so the guard
    terminates deterministically. Wound sites are never emptied, and
    non-site cells are never touched.
    """

    def probe_errors(candidate: list[list[str]]) -> list[str]:
        probe = grid_from_matrix(
            grid_id="wound_guard_probe",
            matrix=candidate,
            palette=source_grid.get("palette", {}),
            parent_grid_id=source_grid.get("grid_id"),
            source="wound_guard_probe",
            mutation_events=["wound_guard_probe"],
            generation_delta=1,
        )
        errors = list(validate_grid(probe).errors)
        if slip_profile is not None:
            errors.extend(is_grid_aligned(probe, slip_profile).errors)
        return errors

    errors = probe_errors(matrix)
    if not errors:
        return matrix, 0
    sites = sorted(
        fill_confidence, key=lambda site: (fill_confidence[site], site)
    )
    substitutions = 0
    for _ in range(len(sites)):
        improved = False
        for x, y in sites:
            current_token = matrix[y][x]
            probs = softmax_probs(
                weights, neighborhood_features(matrix, x, y)
            )
            alternatives = sorted(
                (
                    class_index
                    for class_index in range(1, len(CLASS_TOKENS))
                    if CLASS_TOKENS[class_index] != current_token
                ),
                key=lambda class_index: (-probs[class_index], class_index),
            )
            for class_index in alternatives:
                matrix[y][x] = CLASS_TOKENS[class_index]
                candidate_errors = probe_errors(matrix)
                if len(candidate_errors) < len(errors):
                    errors = candidate_errors
                    substitutions += 1
                    improved = True
                    break
                matrix[y][x] = current_token
            if not errors:
                break
        if not errors or not improved:
            break
    return matrix, substitutions
