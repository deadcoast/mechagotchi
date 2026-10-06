"""X8 lab: independent episodes with explicit terminal survival eligibility.

This extends the retained legacy live-cycle algorithm without changing its
default branch. Damage, repair acceptance, mortality and RNG arithmetic remain
unchanged. See docs/development/cycle-38-surviving-populations.md.
"""
from __future__ import annotations

from copy import deepcopy

from mecha_engine.genome import validate_grid
from mecha_engine.lifecycle import run_episode
from mecha_engine.repair import repair_wound_sites

from mecha_engine.runtime._damage import apply_damage_event, apply_stochastic_damage
from mecha_engine.slip import is_grid_aligned


def live_cycle(
    grid: dict,
    slip_profile: dict,
    repair_model: dict,
    *,
    damage_cycles: int = 3,
    ticks: int = 72,
    dropout_rate: float = 0.2,
    rng_seed: int = 20260512,
    damage_events: list[dict] | None = None,
    record_frames: bool = False,
    population_policy: str = "legacy_archive",
    survival_regime: str = "sheltered",
    body_response: str = "legacy",
) -> dict:
    """Run one creature through repeated damage/repair/episode cycles.

    ``rng_seed`` is the creature's run seed (the lab's ``run_seed``): the
    internal synthesizer damages cycle ``c`` with seed
    ``rng_seed * 10 + c`` and every episode runs with ``rng_seed`` itself,
    exactly as the evolution-loop lab does. When ``damage_events`` is
    supplied (a future gameplay source), the events replace the internal
    synthesizer â€” one cycle per event, in order, so the events list
    defines the cycle count and ``damage_cycles``/``dropout_rate`` govern
    only the synthesizer path â€” without changing cycle semantics; an event
    with empty ``removed_cells`` is a zero-site no-op repair.

    Returns a JSON-serializable dict with per-cycle digests (``cycles``:
    removed cells, restoration fidelity, guard substitutions, validity,
    alignment, episode digest), the ``all_cycles_valid`` /
    ``all_cycles_aligned`` flags, the creature's last accepted grid
    (``final_grid``), and a ``final_state`` digest. Deterministic; never
    mutates ``grid``, ``slip_profile``, ``repair_model``, or
    ``damage_events``.

    ``record_frames`` (R5, decision record 0023 â€” the replay recorder's
    engine seam): when true, each cycle dict additionally carries a
    ``frames`` block with the wound's ``removed_cells`` (verbatim from
    the damage event's observability contract), the ``repaired_grid``,
    and the full per-tick ``episode_history`` (``None`` when the cycle
    ran no episode) â€” the per-tick truth a replay artifact records.
    Default ``False`` is byte-identical to the pre-0023 contract.
    """
    if body_response not in ("legacy", "workload-v1"):
        raise ValueError("unsupported body response")
    if population_policy not in ("legacy_archive", "generation_survivors_v1"):
        raise ValueError("unsupported population policy")
    if survival_regime not in ("sheltered", "stress_probe"):
        raise ValueError("unsupported survival regime")
    survivors = population_policy == "generation_survivors_v1"
    stop = None
    qualified = 0
    if not isinstance(grid, dict) or not isinstance(grid.get("grid_id"), str):
        raise ValueError("grid must be a grid-genome mapping with a grid_id")
    if isinstance(damage_cycles, bool) or not isinstance(damage_cycles, int) or damage_cycles < 0:
        raise ValueError(f"damage_cycles must be a non-negative integer: {damage_cycles}")
    if damage_events is not None:
        if not isinstance(damage_events, list):
            raise ValueError("damage_events must be a list of damage-event mappings")
        cycle_count = len(damage_events)
        damage_source = "injected_events"
    else:
        cycle_count = damage_cycles
        damage_source = "internal_synthesizer"

    base_grid_id = grid["grid_id"]
    current = grid
    cycles: list[dict] = []
    all_valid = True
    all_aligned = True
    candidate_valid = validate_grid(grid).ok
    if survivors and not candidate_valid:
        stop = {"stage": "candidate", "cycle_index": None, "reason": "invalid_candidate"}
        all_valid = False
    for cycle in range(1, cycle_count + 1) if stop is None else ():
        if damage_events is not None:
            damaged = apply_damage_event(
                current, damage_events[cycle - 1], event_index=cycle
            )
        else:
            damage_seed = rng_seed * 10 + cycle
            damaged = apply_stochastic_damage(
                current,
                dropout_rate=dropout_rate,
                rng_seed=damage_seed,
                event_index=cycle,
            )
        removed = damaged["metadata"]["removed_cell_count"]
        repaired = repair_wound_sites(
            damaged, repair_model, slip_profile=slip_profile
        )
        # Reassign the id every cycle: suffix accumulation would
        # overflow the schema's 64-char grid_id cap (known trap).
        repaired["grid_id"] = f"{base_grid_id}_c{cycle:02d}"
        restoration = _restoration(current, repaired)
        valid = validate_grid(repaired).ok
        aligned = is_grid_aligned(repaired, slip_profile).ok
        all_valid = all_valid and valid
        all_aligned = all_aligned and aligned
        # Verbatim lab semantics (T1, commit d382805): an episode runs
        # only for a repair that is BOTH valid and aligned â€” an
        # aligned-but-invalid repair (e.g. a disconnected body core
        # under heavy damage) carries no episode instead of crashing
        # lifecycle simulation. Promotion-drift fix, 2026-07-07: the
        # first port pre-dated the lab's validity gate.
        episode_grid, _ = evaluation_grid(repaired, survival_regime)
        episode = (
            run_episode(
                episode_grid,
                slip_profile,
                policy="switchboard",
                ticks=ticks,
                rng_seed=rng_seed,
                **({"body_response": body_response} if body_response != "legacy" else {}),
            )
            if valid and aligned
            else None
        )
        cycle_entry = {
            "cycle": cycle,
            "removed_cell_count": removed,
            "position_restoration": restoration[
                "position_restoration"
            ],
            "token_restoration": restoration["token_restoration"],
            "guard_substitutions": repaired["metadata"][
                "validity_guard_substitutions"
            ],
            "valid": valid,
            "aligned": aligned,
            "episode": _episode_digest(episode, ticks, evaluated_grid=episode_grid)
            if episode is not None
            else None,
        }
        if record_frames:
            # R5 (decision record 0023): the replay seam â€” engine truth
            # only (the wound's observability record, the repaired body,
            # the episode's own per-tick history).
            cycle_entry["frames"] = {
                "removed_cells": deepcopy(
                    damaged["metadata"]["removed_cells"]
                ),
                "repaired_grid": deepcopy(repaired),
                "episode_history": deepcopy(episode["history"])
                if episode is not None
                else None,
            }
        cycles.append(cycle_entry)
        if survivors:
            if not valid or not aligned:
                stop = {"stage": "repair", "cycle_index": cycle,
                        "reason": "invalid_repair" if not valid else "unaligned_repair"}
                break
            current = repaired
            if not endpoint_qualified(cycle_entry["episode"], ticks):
                stop = {"stage": "cycle_episode", "cycle_index": cycle,
                        "reason": endpoint_reason(cycle_entry["episode"])}
                break
            qualified += 1
        else:
            if not aligned:
                break
            current = repaired

    final_grid = deepcopy(current)
    return {
        "grid_id": base_grid_id,
        **({"body_response": body_response} if body_response != "legacy" else {}),
        "rng_seed": rng_seed,
        "damage_source": damage_source,
        "cycles_requested": cycle_count,
        "cycles": cycles,
        "all_cycles_valid": all_valid,
        "all_cycles_aligned": all_aligned,
        "final_grid": final_grid,
        **({"stop": stop, "cycles_qualified": qualified} if survivors else {}),
        "final_state": {
            "grid_id": final_grid["grid_id"],
            "cycles_completed": len(cycles),
            "live_cell_count": len(final_grid.get("cells", [])),
            "valid": validate_grid(final_grid).ok,
            "aligned": is_grid_aligned(final_grid, slip_profile).ok,
        },
    }


def _live_tokens(grid: dict) -> dict[tuple[int, int], str]:
    return {
        (cell["x"], cell["y"]): f"{cell['role']}/{cell.get('organ')}"
        for cell in grid["cells"]
    }


def _restoration(pre_damage: dict, repaired: dict) -> dict:
    """Runtime restoration fidelity: the loop holds the pre-damage truth.

    ``position_restoration`` is 1.0 exactly when the repaired live-cell set
    equals the pre-damage set (the wound-site structural guarantee);
    ``token_restoration`` is the fraction of those positions whose
    role/organ matches â€” the learned part of repair.
    """
    before = _live_tokens(pre_damage)
    after = _live_tokens(repaired)
    union = set(before) | set(after)
    position_matches = sum(
        1 for key in union if key in before and key in after
    )
    token_matches = sum(
        1 for key in union if before.get(key) == after.get(key)
    )
    return {
        "position_restoration": round(position_matches / len(union), 6),
        "token_restoration": round(token_matches / len(union), 6),
    }


def _episode_digest(episode: dict, ticks: int, *, evaluated_grid: dict | None = None) -> dict:
    return {
        **({"body_response": episode["body_response"], "body_workload": deepcopy(episode["body_workload"]),
            "evaluated_grid": deepcopy(evaluated_grid)}
           if "body_response" in episode else {}),
        "survival_ticks": episode["survival_ticks"],
        "alive": episode["alive"],
        "death_cause": episode["death_cause"],
        "survival_ratio": round(episode["survival_ticks"] / ticks, 6)
        if ticks
        else 0.0,
        "need_balance": episode["need_balance"],
    }


def endpoint_qualified(episode: dict | None, ticks: int) -> bool:
    """A death on the last requested tick is not terminal survival."""
    return (isinstance(episode, dict) and episode.get("alive") is True
            and episode.get("death_cause") is None
            and episode.get("survival_ticks") == ticks)


def endpoint_reason(episode: dict | None) -> str:
    return ("lifecycle_death" if isinstance(episode, dict)
            and episode.get("alive") is False and episode.get("death_cause") is not None
            else "incomplete_episode")


def evaluation_grid(grid: dict, survival_regime: str) -> tuple[dict, float | None]:
    if survival_regime == "sheltered":
        return grid, None
    from mecha_engine.archive._metrics import lifecycle_probe_grid
    probe = lifecycle_probe_grid(grid)
    return probe, probe["cells"][0]["stress"] if probe.get("cells") else 0.0
