"""MAP-Elites archive state, insertion, and summary for mecha_engine.

Contract sources:

- research/package_specs/mecha_engine_archive_contract_gate.md
  ("Mathematical Contract", "Candidate Acceptance", "Insertion Acceptance",
  "Summary Acceptance", "Negative Checks")
- research/package_specs/mecha_engine_module_interfaces.md ("archive")

The archive is a quality-diversity repertoire, never a scalar leaderboard:
elites are keyed by discretized descriptor niche, a niche accepts its first
valid candidate, an occupied niche is replaced only by strictly higher
fitness (deterministic tie handling: on equal fitness the incumbent elite
is kept), and losing candidates leave the previous archive intact. Scalar
top-k selection stays a comparator outside this module — no ranked-top-k
surface exists here. Candidate grids must pass
``mecha_engine.genome.validate_grid`` before insertion; invalid candidates
may be scored for reports but are blocked from elite status and recorded
in the audit log. All public functions return new dictionaries and never
mutate caller-owned inputs.
"""

from __future__ import annotations

from copy import deepcopy

from mecha_engine.genome import validate_grid

from . import _metrics, descriptors, scoring

_REQUIRED_ARCHIVE_KEYS = frozenset(
    {
        "archive_kind",
        "descriptor_mode",
        "descriptor_names",
        "descriptor_cardinalities",
        "elites",
        "observed_bins",
        "candidate_count",
        "blocked_invalid_count",
        "skipped_missing_metrics_count",
        "insertion_log",
    }
)


def build_archive(
    candidates: list[dict],
    metrics_by_grid_id: dict,
    *,
    mode: str = descriptors.EXTENDED_MODE,
) -> dict:
    """Build a MAP-Elites archive from candidates and precomputed metrics.

    Every candidate flows through the same niche mechanics as
    ``insert_candidate`` — scalar top-k never replaces the archive.
    Candidates whose grid id has no metrics bundle, or whose bundle is
    missing required metric inputs, are counted and logged as skipped;
    invalid grids are scored but blocked from elite status. Deterministic:
    identical candidates and metrics always build an identical archive.
    """
    if not isinstance(candidates, list):
        raise ValueError("candidates must be a list of candidate mappings")
    if not isinstance(metrics_by_grid_id, dict):
        raise ValueError("metrics_by_grid_id must be a mapping keyed by grid_id")

    archive = _new_archive(mode)
    for candidate in candidates:
        grid = _metrics.require_candidate(candidate)
        grid_id = grid.get("grid_id", "unknown_grid")
        metrics = metrics_by_grid_id.get(grid_id)
        if metrics is None:
            _record_skip(archive, grid_id, "no metrics bundle for grid_id")
            continue
        try:
            resolved = _metrics.resolve_candidate_metrics(candidate, metrics)
        except ValueError as error:
            _record_skip(archive, grid_id, str(error))
            continue
        descriptor = descriptors.descriptor_from_axis_values(
            descriptors.descriptor_axis_values(resolved),
            mode,
            grid_area=descriptors.grid_area_of(grid),
        )
        score = scoring.score_from_resolved(candidate, resolved)
        archive = insert_candidate(archive, candidate, score, descriptor)
    return archive


def insert_candidate(
    archive: dict, candidate: dict, score: dict, descriptor: tuple[int, ...]
) -> dict:
    """Insert or replace an elite deterministically by niche and fitness.

    Returns a new archive dictionary; the input archive is preserved
    unchanged (a losing candidate therefore leaves the previous archive
    intact by construction). Elite rule: empty niche accepts the first
    valid candidate; an occupied niche is replaced only by strictly higher
    fitness; equal fitness keeps the incumbent (deterministic tie
    handling). Candidate grids are re-validated through
    ``mecha_engine.genome.validate_grid`` — invalid candidates never become
    elites and are recorded as blocked. Every decision is appended to the
    audit ``insertion_log``.
    """
    _check_archive(archive)
    grid = _metrics.require_candidate(candidate)
    mode = archive["descriptor_mode"]
    checked_descriptor = descriptors.check_descriptor(descriptor, mode)
    checked_score = scoring.check_score(score)

    next_archive = deepcopy(archive)
    next_archive["candidate_count"] += 1
    niche = descriptors.descriptor_key(checked_descriptor)
    grid_id = grid.get("grid_id", "unknown_grid")
    fitness = checked_score["fitness"]
    for name, value in zip(archive["descriptor_names"], checked_descriptor):
        observed = set(next_archive["observed_bins"][name])
        observed.add(value)
        next_archive["observed_bins"][name] = sorted(observed)

    validation = validate_grid(grid)
    if not validation.ok or not checked_score["validation"]["ok"]:
        _log(
            next_archive,
            event="blocked_invalid_candidate",
            niche=niche,
            grid_id=grid_id,
            fitness=fitness,
            reason="candidate grid failed mecha_engine.genome.validate_grid; "
            "invalid candidates may be scored for reports but never become elites",
        )
        next_archive["blocked_invalid_count"] += 1
        return next_archive

    incumbent = next_archive["elites"].get(niche)
    if incumbent is None:
        next_archive["elites"][niche] = _elite_entry(
            grid, candidate, checked_score, checked_descriptor, archive
        )
        _log(
            next_archive,
            event="inserted_empty_niche",
            niche=niche,
            grid_id=grid_id,
            fitness=fitness,
            reason="niche was empty",
        )
    elif fitness > incumbent["fitness"]:
        next_archive["elites"][niche] = _elite_entry(
            grid, candidate, checked_score, checked_descriptor, archive
        )
        _log(
            next_archive,
            event="replaced_elite",
            niche=niche,
            grid_id=grid_id,
            fitness=fitness,
            reason="strictly higher fitness than incumbent",
            incumbent_grid_id=incumbent["grid_id"],
            incumbent_fitness=incumbent["fitness"],
        )
    else:
        _log(
            next_archive,
            event=(
                "kept_incumbent_tie"
                if fitness == incumbent["fitness"]
                else "kept_incumbent_higher_fitness"
            ),
            niche=niche,
            grid_id=grid_id,
            fitness=fitness,
            reason=(
                "equal fitness keeps the incumbent (deterministic tie handling)"
                if fitness == incumbent["fitness"]
                else "incumbent fitness is higher"
            ),
            incumbent_grid_id=incumbent["grid_id"],
            incumbent_fitness=incumbent["fitness"],
        )
    return next_archive


def archive_summary(archive: dict) -> dict:
    """Return the JSON-serializable summary of an archive's state.

    Reports descriptor metadata, occupied niches with theoretical-coverage
    context (total possible niches, coverage, per-axis observed bin
    spread), fitness metrics (best, mean elite, QD score), candidate and
    blocked/skipped counts, and the readability calibration status
    (proxy-only; final descriptor thresholds stay unlocked until manual
    ratings exist).
    """
    _check_archive(archive)
    elites = archive["elites"]
    mode = archive["descriptor_mode"]
    total_niches = descriptors.total_possible_niches(mode)
    qd_score = sum(elite["fitness"] for elite in elites.values())
    return {
        "archive_kind": archive["archive_kind"],
        "descriptor_mode": mode,
        "descriptor_names": list(archive["descriptor_names"]),
        "descriptor_dimensions": len(archive["descriptor_names"]),
        "descriptor_cardinalities": list(archive["descriptor_cardinalities"]),
        "total_possible_niches": total_niches,
        "occupied_niches": len(elites),
        "coverage": round(len(elites) / total_niches, 6),
        # Distinct bins observed per axis across all presented candidates:
        # observed-niche context so theoretical coverage is never read
        # across descriptor dimensionalities without it.
        "descriptor_bin_spread": {
            name: len(archive["observed_bins"][name])
            for name in archive["descriptor_names"]
        },
        "best_fitness": max((elite["fitness"] for elite in elites.values()), default=0),
        "mean_elite_fitness": round(qd_score / len(elites), 6) if elites else 0,
        "qd_score": round(qd_score, 6),
        "candidate_count": archive["candidate_count"],
        "blocked_invalid_count": archive["blocked_invalid_count"],
        "skipped_missing_metrics_count": archive["skipped_missing_metrics_count"],
        "readability_calibration_status": archive["readability_calibration_status"],
        "final_descriptor_thresholds_locked": archive[
            "final_descriptor_thresholds_locked"
        ],
    }


def _new_archive(mode: str) -> dict:
    names = descriptors.descriptor_names(mode)
    return {
        "archive_kind": "map_elites",
        "descriptor_mode": mode,
        "descriptor_names": names,
        "descriptor_cardinalities": descriptors.descriptor_cardinalities(mode),
        "descriptor_dimensions": len(names),
        "total_possible_niches": descriptors.total_possible_niches(mode),
        "readability_calibration_status": descriptors.READABILITY_CALIBRATION_STATUS,
        "final_descriptor_thresholds_locked": (
            descriptors.FINAL_DESCRIPTOR_THRESHOLDS_LOCKED
        ),
        "elites": {},
        "observed_bins": {name: [] for name in names},
        "candidate_count": 0,
        "blocked_invalid_count": 0,
        "skipped_missing_metrics_count": 0,
        "insertion_log": [],
    }


def _elite_entry(
    grid: dict,
    candidate: dict,
    score: dict,
    descriptor: tuple[int, ...],
    archive: dict,
) -> dict:
    """Archive-candidate record satisfying the shared data contract.

    Carries the six required candidate fields (grid, descriptor, fitness,
    fitness_components, validation, provenance) so an elite can be audited
    without the original pipeline objects.
    """
    return {
        "grid_id": grid.get("grid_id", "unknown_grid"),
        "grid": deepcopy(grid),
        "descriptor": {
            "names": list(archive["descriptor_names"]),
            "values": list(descriptor),
            "key": descriptors.descriptor_key(descriptor),
            "metrics": deepcopy(score.get("descriptor_metrics", {})),
        },
        "fitness": score["fitness"],
        "fitness_components": deepcopy(score.get("components", {})),
        "validation": deepcopy(score["validation"]),
        "provenance": deepcopy(
            score.get("provenance", {"provided": False, "record": None})
        ),
    }


def _record_skip(archive: dict, grid_id: str, reason: str) -> None:
    archive["candidate_count"] += 1
    archive["skipped_missing_metrics_count"] += 1
    _log(
        archive,
        event="skipped_missing_metrics",
        niche=None,
        grid_id=grid_id,
        fitness=None,
        reason=reason,
    )


def _log(archive: dict, **event_fields: object) -> None:
    archive["insertion_log"].append(event_fields)


def _check_archive(archive: object) -> None:
    if not isinstance(archive, dict) or not _REQUIRED_ARCHIVE_KEYS.issubset(archive):
        raise ValueError(
            "archive must be a mapping created by build_archive or "
            "insert_candidate (missing required archive keys)"
        )
