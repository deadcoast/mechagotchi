"""Live cycle — one creature's life under fire, the runtime's inner loop.

Contract sources:

- research/package_specs/mecha_engine_runtime_interface_spec.md
  ("Proposed public surface": ``live_cycle``; "Hard gates for the port")
- research/decision_records/0008-propose-mecha-engine-runtime-target.md
- labs/runtime_integration/mecha_engine_runtime_loop.py
  (``run_mecha_engine_evolution_loop``'s per-creature cycle loop — the
  verbatim behavior source, pinned by the lab-side parity test)

Verbatim lab semantics, factored so ``evolve`` calls this function for
every creature: per cycle a damage event (the private seeded synthesizer,
seed ``rng_seed * 10 + cycle`` — ``rng_seed`` IS the lab's per-creature
``run_seed``, supplied by the caller so ``evolve`` reproduces the lab
exactly), SLIP-aware wound-site repair through
``mecha_engine.repair.repair_wound_sites``, per-cycle grid-id reassignment
(``{grid_id}_c{cycle:02d}`` — suffix accumulation would overflow the
schema's 64-char grid_id cap, a known trap), restoration fidelity against
the pre-damage truth held by the loop, validity and SLIP-alignment checks,
and a full lifecycle episode for aligned states. An unaligned repair ends
the cycle loop honestly; the creature's last accepted state stays the one
before the failed cycle. Zero-cell damage events are no-op repairs
(measured lab behavior). Deterministic; inputs are never mutated.
"""

from __future__ import annotations

from copy import deepcopy

from mecha_engine.genome import validate_grid
from mecha_engine.lifecycle import run_episode
from mecha_engine.repair import repair_wound_sites

from ._damage import apply_damage_event, apply_stochastic_damage
from ._slip import is_grid_aligned


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
) -> dict:
    """Run one creature through repeated damage/repair/episode cycles.

    ``rng_seed`` is the creature's run seed (the lab's ``run_seed``): the
    internal synthesizer damages cycle ``c`` with seed
    ``rng_seed * 10 + c`` and every episode runs with ``rng_seed`` itself,
    exactly as the evolution-loop lab does. When ``damage_events`` is
    supplied (a future gameplay source), the events replace the internal
    synthesizer — one cycle per event, in order, so the events list
    defines the cycle count and ``damage_cycles``/``dropout_rate`` govern
    only the synthesizer path — without changing cycle semantics; an event
    with empty ``removed_cells`` is a zero-site no-op repair.

    Returns a JSON-serializable dict with per-cycle digests (``cycles``:
    removed cells, restoration fidelity, guard substitutions, validity,
    alignment, episode digest), the ``all_cycles_valid`` /
    ``all_cycles_aligned`` flags, the creature's last accepted grid
    (``final_grid``), and a ``final_state`` digest. Deterministic; never
    mutates ``grid``, ``slip_profile``, ``repair_model``, or
    ``damage_events``.
    """
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
    for cycle in range(1, cycle_count + 1):
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
        episode = (
            run_episode(
                repaired,
                slip_profile,
                policy="switchboard",
                ticks=ticks,
                rng_seed=rng_seed,
            )
            if aligned
            else None
        )
        cycles.append(
            {
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
                "episode": _episode_digest(episode, ticks)
                if episode is not None
                else None,
            }
        )
        if not aligned:
            break
        current = repaired

    final_grid = deepcopy(current)
    return {
        "grid_id": base_grid_id,
        "rng_seed": rng_seed,
        "damage_source": damage_source,
        "cycles_requested": cycle_count,
        "cycles": cycles,
        "all_cycles_valid": all_valid,
        "all_cycles_aligned": all_aligned,
        "final_grid": final_grid,
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
    role/organ matches — the learned part of repair.
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


def _episode_digest(episode: dict, ticks: int) -> dict:
    return {
        "survival_ticks": episode["survival_ticks"],
        "alive": episode["alive"],
        "death_cause": episode["death_cause"],
        "survival_ratio": round(episode["survival_ticks"] / ticks, 6)
        if ticks
        else 0.0,
        "need_balance": episode["need_balance"],
    }
