"""Internal candidate-metric resolution for the archive module.

Contract sources:

- research/package_specs/mecha_engine_archive_contract_gate.md
  ("Candidate Acceptance", "Descriptor Acceptance", "Fitness Acceptance")
- research/package_specs/mecha_engine_module_interfaces.md ("archive")

Documented factoring: the interface spec scopes readability, the lifecycle
episode summary, the SLIP alignment result, and mutation-stability context
as *inputs* to the archive module (the ``metrics`` bundle), not as archive
implementations, so no proxy-readability scorer is ported here — the proxy
readability score arrives in ``metrics["readability"]`` and stays explicitly
marked as uncalibrated. The grid-derived Stage 0 descriptor arithmetic,
which the calibrated research archive owns, is preserved verbatim in this
module: morphology axes (body mass, sensor count, mirror symmetry),
cap-normalized mutation stability, the grid-derived behavior-neediness
term, and the morphology-derived lifecycle stress probe. Survival metrics
are computed through ``mecha_engine.lifecycle`` episodes when the metrics
bundle does not carry a precomputed lifecycle summary, exactly as the brief
"episodes for survival descriptors" dependency prescribes.

Missing metric inputs are rejected with explicit ``ValueError`` messages
(``missing metric input: ...``) so callers can surface blocked/skipped
candidates instead of silently defaulting descriptor axes.
"""

from __future__ import annotations

from copy import deepcopy
from statistics import mean

from mecha_engine.genome import validate_grid
from mecha_engine.lifecycle import run_episode

# Stage 0 lifecycle probe defaults (the calibrated research archive run:
# data/archives/map_elites_extended_stage0.json parameters).
DEFAULT_LIFECYCLE_TICKS = 24
DEFAULT_RNG_SEED = 20260512

# Default per-rate mutation ceilings (the fixed vector the Stage 0 grid
# generator emits when no SLIP profile is supplied). Used as cap context for
# cap-normalized mutation stability when the metrics bundle carries no
# profile.
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

_ZERO_LIFECYCLE: dict = {
    "survival_ratio": 0.0,
    "need_balance": 0.0,
    "recovery_events": 0,
    "final_state": {"bond": 0.0},
}


def require_candidate(candidate: object) -> dict:
    """Return the candidate's grid after structural checks."""
    if not isinstance(candidate, dict) or not isinstance(candidate.get("grid"), dict):
        raise ValueError("archive candidate must be a mapping with a 'grid' object")
    return candidate["grid"]


def require_metrics(metrics: object) -> dict:
    if not isinstance(metrics, dict):
        raise ValueError("archive metrics must be a mapping")
    return metrics


def _cells(grid: dict) -> list[dict]:
    """Structurally parseable cell list (invalid grids stay scorable).

    Grids that fail ``validate_grid`` may still be scored as failures for
    reports, so morphology helpers tolerate malformed payloads instead of
    raising unexpected exception types. Valid grids (the only ones that can
    become elites) always satisfy the strict schema, so this changes
    nothing for them.
    """
    cells = grid.get("cells")
    if not isinstance(cells, list):
        return []
    return [cell for cell in cells if isinstance(cell, dict)]


def body_mass(grid: dict) -> int:
    return sum(1 for cell in _cells(grid) if cell.get("organ") == "core")


def sensor_count(grid: dict) -> int:
    organs = grid.get("organs")
    sensors = organs.get("sensors") if isinstance(organs, dict) else None
    cells = sensors.get("cells") if isinstance(sensors, dict) else None
    return len(cells) if isinstance(cells, list) else 0


def symmetry_score(grid: dict) -> float:
    grid_size = grid.get("grid_size", [0, 0])
    width = (
        grid_size[0]
        if isinstance(grid_size, list)
        and grid_size
        and isinstance(grid_size[0], int)
        and not isinstance(grid_size[0], bool)
        else 0
    )
    occupied = set()
    for cell in _cells(grid):
        x, y = cell.get("x"), cell.get("y")
        if isinstance(x, int) and isinstance(y, int):
            occupied.add((x, y, cell.get("role")))
    if not occupied:
        return 0.0
    mirrored = 0
    for x, y, role in occupied:
        if (width - 1 - x, y, role) in occupied:
            mirrored += 1
    return mirrored / len(occupied)


def mutation_stability(grid: dict, slip_profile: dict | None) -> float:
    """Cap-normalized mutation stability (calibrated Stage 0 metric).

    ``stability = 1 - mean(rate_i / cap_i)`` with each ratio clamped into
    ``[0, 1]``; a raw-mean form cannot leave the top descriptor bin under
    SLIP caps, so the share of the permitted mutation budget is measured
    instead. Caps come from the run's SLIP profile ``*_max`` limits, or the
    default generator rate vector when no profile is supplied.
    """
    mutation = grid.get("mutation")
    if not isinstance(mutation, dict):
        mutation = {}
    caps = DEFAULT_MUTATION_RATE_CAPS
    if slip_profile is not None:
        profile_mutation = slip_profile.get("mutation")
        if not isinstance(profile_mutation, dict):
            profile_mutation = {}
        caps = {
            rate_key: clamp(profile_mutation.get(cap_key, 0.0))
            for rate_key, cap_key in SLIP_MUTATION_CAP_KEYS.items()
        }
    ratios = []
    for rate_key, cap in caps.items():
        rate = clamp(mutation.get(rate_key, 1.0))
        if cap <= 0:
            # A zero cap permits no mutation: any positive rate exhausts it.
            ratios.append(1.0 if rate > 0 else 0.0)
        else:
            ratios.append(min(1.0, rate / cap))
    return clamp(1.0 - mean(ratios))


def behavior_neediness(grid: dict, slip_profile: dict | None) -> float:
    """Grid-derived neediness with the SLIP prior as a shift only.

    Descriptor axes must vary per candidate: a SLIP profile is constant for
    an archive run, so the grid-derived term carries the per-candidate
    signal and the profile neediness only shifts it (Stage 0 calibration).
    """
    grid_term = 0.35 + sensor_count(grid) * 0.08 - body_mass(grid) * 0.01
    if slip_profile is not None:
        behavior = slip_profile.get("behavior")
        if not isinstance(behavior, dict):
            behavior = {}
        if "neediness" in behavior:
            return clamp(grid_term + (clamp(behavior["neediness"]) - 0.5) * 0.2)
    return clamp(grid_term)


def lifecycle_probe_grid(grid: dict) -> dict:
    """Return a grid copy carrying the morphology-derived stress load.

    Calibrated Stage 0 probe: generated candidates ship with pristine cells
    and the SLIP profile is constant per archive run, so without a
    per-candidate load every valid candidate shares one lifecycle
    trajectory and the survival axis collapses into a single bin. The
    archive therefore probes each candidate under a deterministic
    structural load derived from its own morphology:

        load = clamp(body_mass / 16 + (1 - symmetry) * 0.65
                     - sensor_count * 0.08)

    The load is written to every cell's ``stress`` field on a deep copy;
    lifecycle initial state translates mean cell stress into the starting
    stress/grid_stability, and whether the frozen switchboard policy can
    stabilize that starting point decides survival. Lifecycle drift,
    action, and death arithmetic stay untouched.
    """
    probe = deepcopy(grid)
    load = clamp(
        body_mass(grid) / 16
        + (1 - symmetry_score(grid)) * 0.65
        - sensor_count(grid) * 0.08
    )
    for cell in probe.get("cells", []):
        cell["stress"] = round(load, 6)
    return probe


def resolve_lifecycle(grid: dict, metrics: dict, grid_is_valid: bool) -> dict:
    """Resolve the lifecycle metric bundle for one candidate.

    Invalid grids always resolve to the zero lifecycle record (they never
    reach simulation, matching the Stage 0 archive semantics). Otherwise a
    precomputed summary from ``metrics["lifecycle"]`` is used when present
    (either the reduced archive shape or a full ``run_episode`` summary);
    without one, the survival descriptor is computed through
    ``mecha_engine.lifecycle`` on the stress-probed grid with the bundle's
    ``slip_profile``, ``lifecycle_ticks``, and ``rng_seed``.
    """
    if not grid_is_valid:
        return deepcopy(_ZERO_LIFECYCLE)

    supplied = metrics.get("lifecycle")
    if supplied is not None:
        return _reduce_lifecycle_summary(supplied)

    ticks = metrics.get("lifecycle_ticks", DEFAULT_LIFECYCLE_TICKS)
    if isinstance(ticks, bool) or not isinstance(ticks, int) or ticks < 0:
        raise ValueError(f"metrics lifecycle_ticks must be a non-negative integer: {ticks}")
    rng_seed = metrics.get("rng_seed", DEFAULT_RNG_SEED)
    try:
        episode = run_episode(
            lifecycle_probe_grid(grid),
            metrics.get("slip_profile"),
            policy="switchboard",
            ticks=ticks,
            rng_seed=rng_seed,
        )
    except ValueError:
        return deepcopy(_ZERO_LIFECYCLE)
    return {
        "survival_ratio": round(episode["survival_ticks"] / ticks, 6) if ticks else 0.0,
        "need_balance": episode["need_balance"],
        "recovery_events": episode["recovery_events"],
        "final_state": episode["final_state"],
    }


def _reduce_lifecycle_summary(summary: object) -> dict:
    if not isinstance(summary, dict):
        raise ValueError("metrics lifecycle summary must be a mapping")
    if "survival_ratio" in summary:
        reduced = summary
    elif "survival_ticks" in summary and "ticks_requested" in summary:
        ticks = summary["ticks_requested"]
        reduced = {
            "survival_ratio": round(summary["survival_ticks"] / ticks, 6) if ticks else 0.0,
            "need_balance": summary.get("need_balance", 0.0),
            "recovery_events": summary.get("recovery_events", 0),
            "final_state": summary.get("final_state", {"bond": 0.0}),
        }
    else:
        raise ValueError(
            "metrics lifecycle summary must carry survival_ratio or a full "
            "episode summary (survival_ticks and ticks_requested)"
        )
    final_state = reduced.get("final_state")
    if not isinstance(final_state, dict):
        raise ValueError("metrics lifecycle final_state must be a mapping")
    return {
        "survival_ratio": clamp(reduced.get("survival_ratio", 0.0)),
        "need_balance": clamp(reduced.get("need_balance", 0.0)),
        "recovery_events": int(reduced.get("recovery_events", 0)),
        "final_state": deepcopy(final_state),
    }


def resolve_readability(metrics: dict) -> tuple[dict, float]:
    """Return the readability record and proxy score from the bundle.

    Readability is an archive *input* (no proxy scorer is ported into the
    package); a missing readability entry is rejected explicitly. The
    record keeps its manual-rating status visible so proxy readability is
    never presented as human-calibrated readability.
    """
    if "readability" not in metrics:
        raise ValueError("missing metric input: readability")
    supplied = metrics["readability"]
    if isinstance(supplied, dict):
        if "proxy_readability_score" not in supplied:
            raise ValueError(
                "missing metric input: readability proxy_readability_score"
            )
        record = deepcopy(supplied)
        record.setdefault("manual_rating_status", "not_collected")
        record.setdefault("human_readability_rating", None)
        value = record["proxy_readability_score"]
    elif isinstance(supplied, int | float) and not isinstance(supplied, bool):
        value = supplied
        record = {
            "proxy_readability_score": clamp(value),
            "manual_rating_status": "not_collected",
            "human_readability_rating": None,
        }
    else:
        raise ValueError("metrics readability must be a number or a mapping")
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError("metrics readability proxy_readability_score must be a number")
    return record, clamp(value)


def resolve_slip_alignment(metrics: dict) -> tuple[bool, bool]:
    """Return ``(alignment_ok, profile_supplied)`` from the bundle.

    The SLIP alignment result is an archive input per the interface spec.
    Without a profile the candidate counts as aligned (Stage 0 semantics);
    with a profile the bundle must carry the alignment result explicitly.
    """
    profile_supplied = metrics.get("slip_profile") is not None
    if "slip_alignment" not in metrics:
        if profile_supplied:
            raise ValueError("missing metric input: slip_alignment")
        return True, False
    supplied = metrics["slip_alignment"]
    if isinstance(supplied, bool):
        return supplied, profile_supplied
    if isinstance(supplied, dict) and isinstance(supplied.get("ok"), bool):
        return supplied["ok"], profile_supplied
    raise ValueError("metrics slip_alignment must be a bool or a mapping with 'ok'")


def resolve_candidate_metrics(candidate: dict, metrics: dict) -> dict:
    """Resolve every descriptor/fitness ingredient for one candidate.

    Deterministic pure resolution: neither the candidate nor the metrics
    bundle is mutated, and identical inputs always resolve identically.
    """
    grid = require_candidate(candidate)
    metrics = require_metrics(metrics)
    validation = validate_grid(grid)
    slip_profile = metrics.get("slip_profile")
    if slip_profile is not None and not isinstance(slip_profile, dict):
        raise ValueError("metrics slip_profile must be a mapping or None")
    readability_record, readability_value = resolve_readability(metrics)
    alignment_ok, profile_supplied = resolve_slip_alignment(metrics)
    lifecycle = resolve_lifecycle(grid, metrics, validation.ok)
    return {
        "validation": {"ok": validation.ok, "errors": list(validation.errors)},
        "body_mass": body_mass(grid),
        "sensor_count": sensor_count(grid),
        "symmetry": symmetry_score(grid),
        "readability_record": readability_record,
        "readability_value": readability_value,
        "lifecycle": lifecycle,
        "mutation_stability": mutation_stability(grid, slip_profile),
        "behavior_neediness": behavior_neediness(grid, slip_profile),
        "slip_alignment_ok": alignment_ok,
        "slip_profile_supplied": profile_supplied,
    }


def clamp(value: object) -> float:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        number = 0.0
    return max(0.0, min(1.0, number))
