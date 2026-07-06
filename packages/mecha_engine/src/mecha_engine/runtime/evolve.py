"""Evolve — the elites-become-parents evolution step over the archive.

Contract sources:

- research/package_specs/mecha_engine_runtime_interface_spec.md
  ("Proposed public surface": ``evolve``; "Hard gates for the port")
- research/decision_records/0008-propose-mecha-engine-runtime-target.md
- labs/runtime_integration/mecha_engine_runtime_loop.py
  (``run_mecha_engine_evolution_loop`` — the verbatim behavior source,
  pinned by the lab-side parity test)

Verbatim lab semantics: generation 0 draws parents from the
profile-aligned subset of ``seed_grids`` round-robin; every later
generation draws parents from the archive's elites sorted by niche key
round-robin, so selection pressure is the archive's niche-fitness rule and
ancestry deepens generation over generation. A v0.2 SLIP profile carrying
``lineage_preferences.parent_selection == "fitness_weighted"`` (decision
record 0013, ladder rung T3.4) orders elite parents by ``(-fitness,
niche)`` instead — the lab's deterministic truncation bias — and the
report records the carried ``parent_selection``; default flows (every
v0.1 profile, and v0.2 profiles without the field) stay byte-identical. Per-creature seed arithmetic
is ``run_seed = rng_seed + generation_index * 100000 + index``; every
creature lives through ``live_cycle`` (damage seed ``run_seed * 10 +
cycle``), then — if every cycle stayed aligned — runs a final episode,
scores through ``mecha_engine.archive`` with the injected
``readability_scorer`` supplying the readability record (no proxy scorer
is ported; the record's manual-rating status stays visible in every score
record and is surfaced in the report's ``readability`` block), and inserts
into the archive with the lab's insert-event-to-decision mapping. The
summary and decision derivations, including the exact decision reason
strings, are the lab's own.
"""

from __future__ import annotations

from collections.abc import Callable

from mecha_engine.archive import (
    archive_summary,
    build_archive,
    descriptor_for_candidate,
    insert_candidate,
    score_candidate,
)
from mecha_engine.generation import GenerationModel, generate_candidate
from mecha_engine.genome import validate_grid
from mecha_engine.lifecycle import run_episode

from ._slip import is_grid_aligned
from .live import live_cycle

REPORT_ID = "mecha_engine_runtime_evolve"


def evolve(
    seed_grids: list[dict],
    slip_profile: dict,
    generation_model: GenerationModel,
    repair_model: dict,
    *,
    readability_scorer: Callable[[dict], dict | float],
    generations: int = 4,
    population: int = 8,
    damage_cycles: int = 3,
    ticks: int = 72,
    dropout_rate: float = 0.2,
    rng_seed: int = 20260512,
) -> tuple[dict, dict]:
    """Run multi-generation evolution through the composed engine.

    Returns ``(archive, report)``: the final ``mecha_engine.archive``
    archive (whose elites carry full audit records) and a
    JSON-serializable report mirroring the evolution-loop lab's report
    shape for ``generations``, ``summary``, and ``decision``.
    ``readability_scorer`` is a deterministic callable ``grid ->``
    readability record (or bare proxy score) — the injected "equivalent
    metrics hook"; the archive keeps its manual-rating status visible.
    Deterministic end to end; never mutates ``seed_grids``,
    ``slip_profile``, the models, or any caller-owned input.
    """
    if not isinstance(seed_grids, list) or not seed_grids:
        raise ValueError("seed_grids must be a non-empty list of grid genomes")
    if not callable(readability_scorer):
        raise ValueError(
            "readability_scorer must be a callable grid -> readability record"
        )
    if isinstance(generations, bool) or not isinstance(generations, int) or generations < 1:
        raise ValueError(f"generations must be a positive integer: {generations}")
    if isinstance(population, bool) or not isinstance(population, int) or population < 1:
        raise ValueError(f"population must be a positive integer: {population}")

    # T3.4 (decision record 0013): a v0.2 profile's lineage preference
    # steers elite parenting; v0.1 profiles never carry the field. The
    # version guard mirrors the lab loop's own reading of the profile.
    parent_selection = (
        slip_profile.get("lineage_preferences", {}).get("parent_selection")
        if isinstance(slip_profile, dict)
        and slip_profile.get("slip_version") != "0.1.0"
        else None
    )
    seed_pool = [
        seed for seed in seed_grids if is_grid_aligned(seed, slip_profile).ok
    ]
    if not seed_pool:
        raise ValueError("no seed grid satisfies the SLIP profile")

    archive = build_archive([], {})
    generation_reports: list[dict] = []
    manual_rating_statuses: set[str] = set()
    max_lineage_generation = 0

    for generation_index in range(generations):
        if generation_index == 0:
            parents = seed_pool
            parent_source = "seed_pool"
        else:
            elites = archive["elites"]
            if parent_selection == "fitness_weighted":
                # T3.4: breed from the fittest elites first (deterministic
                # truncation bias — with population <= elite count only
                # the fittest reproduce). Lab-verbatim ordering.
                ordered = sorted(
                    elites,
                    key=lambda niche: (
                        -elites[niche]["fitness"],
                        niche,
                    ),
                )
                parents = [elites[niche]["grid"] for niche in ordered]
                parent_source = "archive_elites_fitness_weighted"
            else:
                parents = [
                    elites[niche]["grid"] for niche in sorted(elites)
                ]
                parent_source = "archive_elites"
            if not parents:
                break  # measured, not asserted: an empty archive ends evolution

        creatures = []
        for index in range(population):
            parent = parents[index % len(parents)]
            run_seed = rng_seed + generation_index * 100000 + index
            stages: dict[str, bool] = {}

            candidate = generate_candidate(
                parent, generation_model, slip_profile, rng_seed=run_seed
            )
            stages["candidate_valid"] = validate_grid(candidate).ok
            max_lineage_generation = max(
                max_lineage_generation,
                candidate.get("lineage", {}).get("generation", 0),
            )

            lived = live_cycle(
                candidate,
                slip_profile,
                repair_model,
                damage_cycles=damage_cycles,
                ticks=ticks,
                dropout_rate=dropout_rate,
                rng_seed=run_seed,
            )
            cycles = lived["cycles"]
            current = lived["final_grid"]
            stages["all_cycles_valid"] = lived["all_cycles_valid"]
            stages["all_cycles_aligned"] = lived["all_cycles_aligned"]

            score_digest = None
            decision = "skipped_unaligned"
            stages["scored"] = False
            if (
                stages["all_cycles_aligned"]
                and cycles
                and cycles[-1]["episode"] is not None
            ):
                final_episode = run_episode(
                    current,
                    slip_profile,
                    policy="switchboard",
                    ticks=ticks,
                    rng_seed=run_seed,
                )
                alignment = is_grid_aligned(current, slip_profile)
                metrics = {
                    "readability": readability_scorer(current),
                    "slip_profile": slip_profile,
                    "slip_alignment": {"ok": alignment.ok},
                    "lifecycle": final_episode,
                    "rng_seed": run_seed,
                }
                archive_candidate = {"grid": current}
                score = score_candidate(archive_candidate, metrics)
                descriptor = descriptor_for_candidate(archive_candidate, metrics)
                stages["scored"] = isinstance(score.get("fitness"), float)
                manual_rating_statuses.add(
                    score["readability"]["manual_rating_status"]
                )
                score_digest = {
                    "fitness": score["fitness"],
                    "components": score["components"],
                }
                before_log = len(archive["insertion_log"])
                archive = insert_candidate(
                    archive, archive_candidate, score, descriptor
                )
                event = (
                    archive["insertion_log"][before_log]["event"]
                    if len(archive["insertion_log"]) > before_log
                    else "unlogged"
                )
                if event.startswith("inserted"):
                    decision = "inserted"
                elif event.startswith("replaced"):
                    decision = "replaced"
                elif event.startswith("blocked"):
                    decision = "blocked_invalid"
                else:
                    decision = "kept_incumbent"

            creatures.append(
                {
                    "parent_grid_id": parent["grid_id"],
                    "candidate_grid_id": candidate["grid_id"],
                    "lineage_generation": candidate.get("lineage", {}).get(
                        "generation", 0
                    ),
                    "stages": stages,
                    "cycles": cycles,
                    "score": score_digest,
                    "archive_decision": decision,
                }
            )

        summary_after = archive_summary(archive)
        generation_reports.append(
            {
                "generation": generation_index,
                "parent_source": parent_source,
                "parent_pool_size": len(parents),
                "creatures": creatures,
                "mean_fitness": round(
                    sum(
                        creature["score"]["fitness"]
                        for creature in creatures
                        if creature["score"] is not None
                    )
                    / max(
                        1,
                        sum(
                            1
                            for creature in creatures
                            if creature["score"] is not None
                        ),
                    ),
                    6,
                ),
                "archive_niches_after": summary_after["occupied_niches"],
                "archive_qd_after": summary_after["qd_score"],
            }
        )

    summary = _evolution_summary(
        generation_reports, archive, max_lineage_generation
    )
    report = {
        "lab_id": REPORT_ID,
        "rng_seed": rng_seed,
        "generations_requested": generations,
        "population": population,
        "damage_cycles": damage_cycles,
        "ticks": ticks,
        "dropout_rate": dropout_rate,
        "seed_corpus_size": len(seed_grids),
        "seed_pool_size": len(seed_pool),
        # The readability hook stays visibly uncalibrated: the statuses seen
        # across every score record produced by this run (interface spec:
        # "the record's manual-rating status stays visible in every score").
        "readability": {
            "source": "injected_scorer",
            "manual_rating_statuses": sorted(manual_rating_statuses),
            "calibration": "uncalibrated_proxy_manual_calibration_deferred",
        },
        "generations": generation_reports,
        "summary": summary,
        "decision": _evolution_decision(summary),
    }
    # Conditional exactly like the lab report: default flows carry no
    # rung key, so v0.1 reports stay byte-identical.
    if parent_selection is not None:
        report["parent_selection"] = parent_selection
    return archive, report


def _evolution_summary(
    generation_reports: list[dict], archive: dict, max_lineage_generation: int
) -> dict:
    creatures = [
        creature
        for generation in generation_reports
        for creature in generation["creatures"]
    ]
    count = len(creatures)
    cycles = [
        cycle for creature in creatures for cycle in creature["cycles"]
    ]
    archived = [
        creature for creature in creatures if creature["score"] is not None
    ]
    summary = archive_summary(archive)
    return {
        "generation_count": len(generation_reports),
        "creature_count": count,
        "total_damage_events": len(cycles),
        "candidate_valid_rate": round(
            sum(1 for c in creatures if c["stages"]["candidate_valid"]) / count,
            6,
        ),
        "slip_alignment_retention_rate": round(
            sum(1 for c in creatures if c["stages"]["all_cycles_aligned"])
            / count,
            6,
        ),
        "mean_position_restoration": round(
            sum(cycle["position_restoration"] for cycle in cycles)
            / len(cycles),
            6,
        ),
        "mean_token_restoration": round(
            sum(cycle["token_restoration"] for cycle in cycles) / len(cycles),
            6,
        ),
        "guard_substitution_total": sum(
            cycle["guard_substitutions"] for cycle in cycles
        ),
        "archived_creature_count": len(archived),
        "mean_fitness_by_generation": [
            generation["mean_fitness"] for generation in generation_reports
        ],
        "max_lineage_generation": max_lineage_generation,
        "archive": {
            "filled_niches": summary["occupied_niches"],
            "coverage": summary["coverage"],
            "qd_score": summary["qd_score"],
        },
    }


def _evolution_decision(summary: dict) -> dict:
    elites_became_parents = summary["generation_count"] >= 2
    all_green = (
        summary["candidate_valid_rate"] == 1.0
        and summary["slip_alignment_retention_rate"] == 1.0
        and summary["mean_position_restoration"] == 1.0
        and summary["archived_creature_count"] == summary["creature_count"]
        and elites_became_parents
        and summary["max_lineage_generation"] >= 2
    )
    if all_green:
        status = "evolution_loop_composed"
        reason = (
            "Archive elites reproduce: every creature in every generation "
            "validates, survives repeated damage/repair cycles with full "
            "episodes between regenerations, stays SLIP-aligned, and "
            "scores back into the archive; ancestry deepens generation "
            "over generation. Fitness and archive trajectories are "
            "reported as measurements, not gates."
        )
    else:
        status = "evolution_loop_gaps_measured"
        reason = (
            "At least one creature fell short of a module contract inside "
            "the evolution loop; the per-creature stage flags and cycle "
            "records name exactly where."
        )
    return {
        "status": status,
        # The lab records adoption "lab_only_runtime_evidence"; this IS the
        # promoted runtime surface, so the adoption label differs (the
        # lab-parity pin compares decision status and reason, which are
        # verbatim).
        "adoption": "package_runtime_surface",
        "reason": reason,
    }
