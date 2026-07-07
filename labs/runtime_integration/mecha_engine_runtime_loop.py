"""Runtime integration lab: the promoted engine running as one organism.

Composes all six promoted `mecha_engine` modules through the cross-module
MVP flow (research/package_specs/mecha_engine_module_interfaces.md),
extended with the repair module's damage-event contract:

    genome.validate_grid(parent)
      -> generation.generate_candidate(...)
      -> genome.validate_grid / grid_signature / render_packet_from_grid
      -> lifecycle.run_episode (pre-damage)
      -> damage event (reference source: the cellular_automata lab's
         seeded stochastic damage, which reports `removed_cells` per the
         repair interface spec's observability contract)
      -> repair.repair_wound_sites (validity guard on, no template)
      -> lifecycle.run_episode (post-repair)
      -> archive.score_candidate / descriptor_for_candidate /
         insert_candidate -> archive_summary
      -> provenance.validate_ledger / build_ci_report over the real
         repository ledger

This is evidence for a future `runtime` package surface — which remains
decision-record-gated and is NOT created here. Labs may import the
package (the established parity direction); the package never imports
labs. Readability enters the archive as the uncalibrated proxy with its
manual-rating status visible (calibration is deferred by owner decision).
"""

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
GRID_GENOME = ROOT / "labs" / "grid_genome"
READABILITY = ROOT / "labs" / "readability_benchmark"
CELLULAR = ROOT / "labs" / "cellular_automata"
for path in [PACKAGE_SRC, GRID_GENOME, READABILITY, CELLULAR]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ca_nca_growth_repair import apply_stochastic_damage  # noqa: E402
from corpus_builder import build_seed_grids  # noqa: E402
from readability_benchmark import score_readability  # noqa: E402
from slip import is_grid_aligned  # noqa: E402

from mecha_engine.archive import (  # noqa: E402
    archive_summary,
    build_archive,
    descriptor_for_candidate,
    insert_candidate,
    score_candidate,
)
from mecha_engine.generation import (  # noqa: E402
    generate_candidate,
    train_generation_model,
)
from mecha_engine.genome import (  # noqa: E402
    grid_signature,
    render_packet_from_grid,
    validate_grid,
)
from mecha_engine.lifecycle import run_episode  # noqa: E402
from mecha_engine.provenance import (  # noqa: E402
    build_ci_report,
    validate_ledger,
)
from mecha_engine.repair import (  # noqa: E402
    repair_wound_sites,
    train_repair_model,
)


ARTIFACT_ID = "mecha_engine_runtime_loop_stage0"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "runtime_integration"
SLIP_PROFILE_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
LEDGER_PATH = ROOT / "data" / "asset_provenance" / "ledger.json"
REPAIR_TRAINING_COUNT = 40  # the trained-repair benchmark's split


def _probe_clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _probe_body_mass(grid: dict) -> int:
    return sum(1 for cell in grid.get("cells", []) if cell.get("organ") == "core")


def _probe_sensor_count(grid: dict) -> int:
    sensors = grid.get("organs", {}).get("sensors", {})
    cells = sensors.get("cells") if isinstance(sensors, dict) else None
    return len(cells) if isinstance(cells, list) else 0


def _probe_symmetry(grid: dict) -> float:
    width = grid.get("grid_size", [0, 0])[0]
    occupied = {
        (cell["x"], cell["y"], cell.get("role"))
        for cell in grid.get("cells", [])
    }
    if not occupied:
        return 0.0
    mirrored = sum(
        1 for x, y, role in occupied if (width - 1 - x, y, role) in occupied
    )
    return mirrored / len(occupied)


def _stress_probe(grid: dict) -> tuple[dict, float]:
    """The archive's contracted morphology stress probe, mirrored verbatim.

    Source of truth: ``mecha_engine.archive._metrics.lifecycle_probe_grid``
    (load = clamp(body_mass/16 + (1 - symmetry) * 0.65 - sensors * 0.08),
    written to every cell's ``stress`` field on a copy). The hard survival
    regime runs episodes on this probed copy, so whether the switchboard
    can stabilize the morphology-derived load decides survival — the
    gradient selection and (later) learning need.
    """
    load = _probe_clamp(
        _probe_body_mass(grid) / 16
        + (1 - _probe_symmetry(grid)) * 0.65
        - _probe_sensor_count(grid) * 0.08
    )
    probe = json.loads(json.dumps(grid))
    for cell in probe.get("cells", []):
        cell["stress"] = round(load, 6)
    return probe, round(load, 6)


def _live_tokens(grid: dict) -> dict[tuple[int, int], str]:
    return {
        (cell["x"], cell["y"]): f"{cell['role']}/{cell.get('organ')}"
        for cell in grid["cells"]
    }


def _restoration(pre_damage: dict, repaired: dict) -> dict:
    """Runtime restoration fidelity: the loop holds the pre-damage truth.

    `position_restoration` is 1.0 exactly when the repaired live-cell set
    equals the pre-damage set (the wound-site structural guarantee);
    `token_restoration` is the fraction of those positions whose
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


def run_mecha_engine_runtime_loop(
    *,
    count: int = 12,
    ticks: int = 72,
    dropout_rate: float = 0.2,
    repair_epochs: int = 150,
    rng_seed: int = 20260512,
) -> dict:
    """Run `count` creatures through the full engine loop, deterministically."""
    slip_profile = json.loads(SLIP_PROFILE_PATH.read_text(encoding="utf-8"))
    seeds = build_seed_grids()
    generation_model = train_generation_model(seeds)
    repair_model = train_repair_model(
        seeds[:REPAIR_TRAINING_COUNT],
        epochs=repair_epochs,
        rng_seed=rng_seed,
    )

    # Second integration behavior surfaced by composing the modules: the
    # generation contract REJECTS parents that cannot satisfy the SLIP
    # profile (e.g. a disallowed palette), so a runtime selects parents
    # per profile. The corpus mixes three palettes; the run pool is the
    # profile-aligned subset.
    parent_pool = [
        seed for seed in seeds if is_grid_aligned(seed, slip_profile).ok
    ]
    if not parent_pool:
        raise ValueError("no seed grid satisfies the SLIP profile")

    archive = build_archive([], {})
    runs = []
    for index in range(count):
        parent = parent_pool[index % len(parent_pool)]
        run_seed = rng_seed + index
        stages: dict[str, bool] = {}

        stages["parent_valid"] = validate_grid(parent).ok

        candidate = generate_candidate(
            parent, generation_model, slip_profile, rng_seed=run_seed
        )
        candidate_validation = validate_grid(candidate)
        stages["candidate_valid"] = candidate_validation.ok
        signature = grid_signature(candidate)
        packet = render_packet_from_grid(candidate)
        json.dumps(packet)  # the packet contract: JSON-serializable
        stages["render_packet_serializable"] = True

        episode_pre = run_episode(
            candidate,
            slip_profile,
            policy="switchboard",
            ticks=ticks,
            rng_seed=run_seed,
        )
        stages["episode_pre_completed"] = episode_pre["survival_ticks"] >= 0

        damaged = apply_stochastic_damage(
            candidate,
            dropout_rate=dropout_rate,
            rng_seed=rng_seed + index * 1000 + 1,
            event_index=1,
        )
        damage_event = {
            "removed_cell_count": damaged["metadata"]["removed_cell_count"],
            "removed_cells": damaged["metadata"]["removed_cells"],
        }

        # SLIP-aware guard (the seam fix, 2026-07-05): the runtime hands
        # the active profile to repair, so a destroyed profile-required
        # organ is refilled back into an aligned, simulatable creature.
        repaired = repair_wound_sites(
            damaged, repair_model, slip_profile=slip_profile
        )
        repaired_validation = validate_grid(repaired)
        stages["repaired_valid"] = repaired_validation.ok
        restoration = _restoration(candidate, repaired)
        restoration["validity_guard_substitutions"] = repaired["metadata"][
            "validity_guard_substitutions"
        ]

        # Cross-module contract gap, found by this lab's first composed
        # run: repair guarantees genome-validator validity, but lifecycle
        # REJECTS grids that lost SLIP alignment (e.g. the only expression
        # cell destroyed and refilled as another organ). Alignment
        # retention is therefore a first-class measured stage; unaligned
        # repairs skip the post episode and the archive, honestly.
        alignment = is_grid_aligned(repaired, slip_profile)
        stages["slip_aligned_post_repair"] = alignment.ok

        episode_post_digest = None
        score_digest = None
        descriptor_list = None
        decision = "skipped_unaligned"
        stages["episode_post_completed"] = False
        stages["scored"] = False
        if alignment.ok:
            episode_post = run_episode(
                repaired,
                slip_profile,
                policy="switchboard",
                ticks=ticks,
                rng_seed=run_seed,
            )
            stages["episode_post_completed"] = episode_post["survival_ticks"] >= 0
            episode_post_digest = _episode_digest(episode_post, ticks)

            metrics = {
                "readability": score_readability(repaired),
                "slip_profile": slip_profile,
                "slip_alignment": {"ok": True},
                "lifecycle": episode_post,
                "rng_seed": run_seed,
            }
            archive_candidate = {"grid": repaired}
            score = score_candidate(archive_candidate, metrics)
            descriptor = descriptor_for_candidate(archive_candidate, metrics)
            stages["scored"] = isinstance(score.get("fitness"), float)
            score_digest = {
                "fitness": score["fitness"],
                "components": score["components"],
                "readability": {
                    "proxy_readability_score": score["readability"][
                        "proxy_readability_score"
                    ],
                    "manual_rating_status": score["readability"][
                        "manual_rating_status"
                    ],
                },
            }
            descriptor_list = list(descriptor)

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

        runs.append(
            {
                "parent_grid_id": parent["grid_id"],
                "candidate_grid_id": candidate["grid_id"],
                "candidate_signature": signature,
                "stages": stages,
                "episode_pre": _episode_digest(episode_pre, ticks),
                "damage": damage_event,
                "repair": restoration,
                "episode_post": episode_post_digest,
                "score": score_digest,
                "descriptor": descriptor_list,
                "archive_decision": decision,
            }
        )

    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    ledger_result = validate_ledger(ledger, ROOT)
    ci_report = build_ci_report(ledger, ROOT)

    summary = _loop_summary(runs, archive, ticks)
    report = {
        "lab_id": ARTIFACT_ID,
        "date": "2026-07-05",
        "rng_seed": rng_seed,
        "count": count,
        "parent_pool_size": len(parent_pool),
        "seed_corpus_size": len(seeds),
        "ticks": ticks,
        "dropout_rate": dropout_rate,
        "repair_epochs": repair_epochs,
        "repair_training_count": REPAIR_TRAINING_COUNT,
        "purpose": (
            "Compose all six promoted mecha_engine modules through the "
            "cross-module MVP flow plus the repair damage-event contract, "
            "as executable evidence for a future runtime surface."
        ),
        "source_artifacts": [
            "research/package_specs/mecha_engine_module_interfaces.md",
            "research/package_specs/mecha_engine_repair_interface_spec.md",
            "research/package_specs/mecha_engine_contract_traceability_matrix.md",
            "data/slips/valid/slip_lcd_seed.json",
            "data/asset_provenance/ledger.json",
        ],
        "runs": runs,
        "summary": summary,
        "provenance": {
            "ledger_ok": ledger_result["ok"],
            "ledger_asset_count": ledger_result["summary"]["asset_count"],
            "ci_ok": bool(ci_report.get("ok")),
        },
        "closed_states": [
            "six_module_loop_composed_generation_to_provenance",
            "repair_damage_event_contract_exercised_in_full_loop",
        ],
        "blocked_states": [
            "runtime_package_target_absent_decision_record_gated",
            "readability_proxy_uncalibrated_manual_calibration_deferred",
        ],
        "decision": _loop_decision(summary, ledger_result, ci_report),
        "next_research_step": (
            "Extend the loop to multi-generation evolution (offspring of "
            "archive elites) and repeated damage/repair cycles before any "
            "runtime package design is proposed (decision record required)."
        ),
    }
    return report


def _loop_summary(runs: list[dict], archive: dict, ticks: int) -> dict:
    count = len(runs)
    summary = archive_summary(archive)
    archived = [run for run in runs if run["score"] is not None]
    return {
        "run_count": count,
        "candidate_valid_rate": round(
            sum(1 for run in runs if run["stages"]["candidate_valid"]) / count, 6
        ),
        "repaired_valid_rate": round(
            sum(1 for run in runs if run["stages"]["repaired_valid"]) / count, 6
        ),
        "slip_alignment_retention_rate": round(
            sum(
                1 for run in runs if run["stages"]["slip_aligned_post_repair"]
            )
            / count,
            6,
        ),
        "mean_removed_cells": round(
            sum(run["damage"]["removed_cell_count"] for run in runs) / count, 6
        ),
        "mean_position_restoration": round(
            sum(run["repair"]["position_restoration"] for run in runs) / count, 6
        ),
        "mean_token_restoration": round(
            sum(run["repair"]["token_restoration"] for run in runs) / count, 6
        ),
        "guard_substitution_total": sum(
            run["repair"]["validity_guard_substitutions"] for run in runs
        ),
        "mean_survival_ratio_pre": round(
            sum(run["episode_pre"]["survival_ratio"] for run in runs) / count, 6
        ),
        "mean_survival_ratio_post": round(
            sum(
                run["episode_post"]["survival_ratio"]
                for run in archived
            )
            / len(archived),
            6,
        )
        if archived
        else 0.0,
        "mean_fitness": round(
            sum(run["score"]["fitness"] for run in archived) / len(archived), 6
        )
        if archived
        else 0.0,
        "archived_run_count": len(archived),
        "archive": {
            "filled_niches": summary["occupied_niches"],
            "coverage": summary["coverage"],
            "qd_score": summary["qd_score"],
            "insertions": sum(
                1 for run in runs if run["archive_decision"] == "inserted"
            ),
        },
    }


def _loop_decision(summary: dict, ledger_result: dict, ci_report: dict) -> dict:
    all_stages_green = (
        summary["candidate_valid_rate"] == 1.0
        and summary["repaired_valid_rate"] == 1.0
        and summary["slip_alignment_retention_rate"] == 1.0
        and summary["mean_position_restoration"] == 1.0
        and summary["archive"]["filled_niches"] >= 1
        and ledger_result["ok"]
        and bool(ci_report.get("ok"))
    )
    if all_stages_green:
        status = "runtime_loop_composed"
        reason = (
            "All six promoted modules compose into one deterministic loop: "
            "every generated creature validates, survives an episode, takes "
            "a reported damage event, is repaired to its exact live-cell "
            "silhouette without a template, survives post-repair, scores "
            "into the archive, and the provenance gate passes over the real "
            "ledger. Evidence exists for a runtime surface design; creating "
            "that target stays decision-record-gated."
        )
    else:
        status = "runtime_loop_gaps_measured"
        reason = (
            "At least one stage fell short of its module contract inside "
            "the composed loop; the per-run stage flags record exactly "
            "where. The gap list, not this consolidated flag, is the "
            "actionable surface."
        )
    return {
        "status": status,
        "adoption": "lab_only_runtime_evidence",
        "reason": reason,
    }


def run_mecha_engine_evolution_loop(
    *,
    generations: int = 4,
    population: int = 8,
    damage_cycles: int = 3,
    ticks: int = 72,
    dropout_rate: float = 0.2,
    repair_epochs: int = 150,
    rng_seed: int = 20260512,
    survival_regime: str = "sheltered",
    workshop_grids_dir: str | Path | None = None,
    slip_profile: dict | None = None,
) -> dict:
    """Multi-generation evolution through the composed engine.

    Generation 0 draws parents from the profile-aligned seed pool; every
    later generation draws parents from the archive's elites (sorted by
    niche key for determinism), so selection pressure is the archive's
    niche-fitness rule and ancestry deepens generation over generation.
    Each creature lives through `damage_cycles` repeated damage events,
    each repaired by the SLIP-aware wound-site guard and followed by a
    full lifecycle episode — the creature must keep earning its survival
    after every regeneration.

    `survival_regime`: "sheltered" (default, byte-identical to the
    original loop — the package parity pins depend on it) runs episodes
    on the pristine creature; "stress_probe" runs every episode on the
    archive's contracted morphology stress probe, making survival
    morphology-dependent so selection has a gradient. Stress-only report
    keys are added exclusively under the stress regime.

    `slip_profile` (T3.4): an explicit profile — a v0.2 profile's
    `lineage_preferences.parent_selection` steers elite parenting
    (fitness_weighted breeds from the fittest elites first; uniform is
    the frozen niche-key round-robin). Since DR 0013 the package
    consumes v0.2 natively, so the FULL profile flows through every
    surface (risk tolerances and learning switches reach package
    episodes). Default None loads the standard fixture — byte-identical
    to the frozen loop.

    `workshop_grids_dir` (T1, the workshop->engine asset wire — owner
    DESIGN-CORRECTION 2026-07-05): a directory of RELEASED workshop
    creatures. Each is admitted through the engine's own gates
    (validate_grid + SLIP alignment); admitted founders LEAD the
    generation-0 parent pool so the wire is always exercised, and their
    grid_ids remain traceable through every descendant's
    `lineage.ancestor_ids` chain (renames per damage cycle touch only
    `grid_id`, never the ancestor list). All wire keys are conditional:
    the default `None` path stays byte-identical — the package parity
    pins depend on it.
    """
    if survival_regime not in ("sheltered", "stress_probe"):
        raise ValueError(f"unknown survival_regime: {survival_regime}")
    stress = survival_regime == "stress_probe"

    def episode_grid(grid: dict) -> tuple[dict, float | None]:
        if not stress:
            return grid, None
        return _stress_probe(grid)

    if slip_profile is None:
        slip_profile = json.loads(
            SLIP_PROFILE_PATH.read_text(encoding="utf-8")
        )
    parent_selection = (
        slip_profile.get("lineage_preferences", {}).get("parent_selection")
        if slip_profile.get("slip_version") != "0.1.0"
        else None
    )
    # DR 0013 ported SLIP v0.2 into the package: full profiles flow
    # natively (the v01_projection adapter is retired from this loop —
    # it remains in the authority for consumers that need it).
    package_profile = slip_profile
    seeds = build_seed_grids()
    generation_model = train_generation_model(seeds)
    repair_model = train_repair_model(
        seeds[:REPAIR_TRAINING_COUNT],
        epochs=repair_epochs,
        rng_seed=rng_seed,
    )
    seed_pool = [
        seed for seed in seeds if is_grid_aligned(seed, slip_profile).ok
    ]
    if not seed_pool:
        raise ValueError("no seed grid satisfies the SLIP profile")

    workshop = workshop_grids_dir is not None
    workshop_founders: list[dict] = []
    workshop_rejected: list[dict] = []
    founder_ids: set[str] = set()
    released_count = 0
    if workshop:
        released_dir = Path(workshop_grids_dir)
        for file in sorted(released_dir.glob("*.json")):
            if file.name.endswith(".bak.json"):
                continue
            released_count += 1
            grid = json.loads(file.read_text(encoding="utf-8"))
            errors: list[str] = []
            validation = validate_grid(grid)
            errors.extend(validation.errors)
            alignment = is_grid_aligned(grid, slip_profile)
            errors.extend(alignment.errors)
            if errors:
                workshop_rejected.append(
                    {"grid_id": grid.get("grid_id"), "errors": errors}
                )
            else:
                workshop_founders.append(grid)
                founder_ids.add(grid["grid_id"])

    archive = build_archive([], {})
    generation_reports = []
    max_lineage_generation = 0

    for generation_index in range(generations):
        if generation_index == 0:
            if workshop and workshop_founders:
                # Founders lead the pool so the round-robin always
                # exercises the wire deterministically.
                parents = workshop_founders + seed_pool
                parent_source = "workshop_founders_plus_seed_pool"
            else:
                parents = seed_pool
                parent_source = "seed_pool"
        else:
            elites = archive["elites"]
            if parent_selection == "fitness_weighted":
                # T3.4: breed from the fittest elites first (deterministic
                # truncation bias — with population <= elite count only
                # the fittest reproduce).
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
                parent, generation_model, package_profile, rng_seed=run_seed
            )
            stages["candidate_valid"] = validate_grid(candidate).ok
            max_lineage_generation = max(
                max_lineage_generation,
                candidate.get("lineage", {}).get("generation", 0),
            )

            current = candidate
            cycles = []
            all_valid = True
            all_aligned = True
            for cycle in range(1, damage_cycles + 1):
                damage_seed = run_seed * 10 + cycle
                damaged = apply_stochastic_damage(
                    current,
                    dropout_rate=dropout_rate,
                    rng_seed=damage_seed,
                    event_index=cycle,
                )
                removed = damaged["metadata"]["removed_cell_count"]
                repaired = repair_wound_sites(
                    damaged, repair_model, slip_profile=package_profile
                )
                # Reassign the id every cycle: suffix accumulation would
                # overflow the schema's 64-char grid_id cap (known trap).
                repaired["grid_id"] = f"{candidate['grid_id']}_c{cycle:02d}"
                restoration = _restoration(current, repaired)
                valid = validate_grid(repaired).ok
                aligned = is_grid_aligned(repaired, slip_profile).ok
                all_valid = all_valid and valid
                all_aligned = all_aligned and aligned
                episode = None
                if valid and aligned:
                    cycle_episode_grid, _ = episode_grid(repaired)
                    episode = run_episode(
                        cycle_episode_grid,
                        package_profile,
                        policy="switchboard",
                        ticks=ticks,
                        rng_seed=run_seed,
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

            stages["all_cycles_valid"] = all_valid
            stages["all_cycles_aligned"] = all_aligned

            score_digest = None
            # Overwritten by the archive outcome when scoring runs.
            decision = (
                "skipped_invalid"
                if all_aligned and not all_valid
                else "skipped_unaligned"
            )
            stages["scored"] = False
            final_load = None
            if (
                all_valid
                and all_aligned
                and cycles
                and cycles[-1]["episode"] is not None
            ):
                final_episode_grid, final_load = episode_grid(current)
                final_episode = run_episode(
                    final_episode_grid,
                    package_profile,
                    policy="switchboard",
                    ticks=ticks,
                    rng_seed=run_seed,
                )
                alignment = is_grid_aligned(current, slip_profile)
                metrics = {
                    "readability": score_readability(current),
                    "slip_profile": package_profile,
                    "slip_alignment": {"ok": alignment.ok},
                    "lifecycle": final_episode,
                    "rng_seed": run_seed,
                }
                archive_candidate = {"grid": current}
                score = score_candidate(archive_candidate, metrics)
                descriptor = descriptor_for_candidate(archive_candidate, metrics)
                stages["scored"] = isinstance(score.get("fitness"), float)
                score_digest = {
                    "fitness": score["fitness"],
                    "components": score["components"],
                }
                if stress:
                    score_digest["final_episode"] = _episode_digest(
                        final_episode, ticks
                    )
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

            ancestor_ids = list(
                candidate.get("lineage", {}).get("ancestor_ids", [])
            )
            creature_record = {
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
            if stress:
                if final_load is None:
                    _, final_load = _stress_probe(current)
                creature_record["stress_load"] = final_load
            if workshop:
                descended = parent["grid_id"] in founder_ids or any(
                    founder in ancestor_ids for founder in founder_ids
                )
                creature_record["founder_source"] = (
                    "workshop" if descended else "corpus"
                )
                creature_record["ancestor_ids"] = ancestor_ids
            creatures.append(creature_record)

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
    if stress:
        summary["survival_regime"] = "stress_probe"
        summary["mean_stress_load_by_generation"] = [
            round(
                sum(c["stress_load"] for c in generation["creatures"])
                / len(generation["creatures"]),
                6,
            )
            for generation in generation_reports
        ]
        final_episodes_by_generation = [
            [
                c["score"]["final_episode"]
                for c in generation["creatures"]
                if c["score"] is not None
            ]
            for generation in generation_reports
        ]
        summary["mean_survival_ratio_by_generation"] = [
            round(
                sum(e["survival_ratio"] for e in episodes) / len(episodes), 6
            )
            if episodes
            else 0.0
            for episodes in final_episodes_by_generation
        ]
        summary["death_count"] = sum(
            1
            for episodes in final_episodes_by_generation
            for e in episodes
            if not e["alive"]
        )
    if workshop:
        def _is_workshop(creature: dict) -> bool:
            return creature.get("founder_source") == "workshop"

        def _mean_fitness(records: list[dict]) -> float | None:
            scored = [
                r["score"]["fitness"] for r in records if r["score"] is not None
            ]
            return round(sum(scored) / len(scored), 6) if scored else None

        all_creatures = [
            creature
            for generation in generation_reports
            for creature in generation["creatures"]
        ]
        workshop_creatures = [c for c in all_creatures if _is_workshop(c)]
        corpus_creatures = [c for c in all_creatures if not _is_workshop(c)]
        elite_ids_with_workshop_ancestry = sum(
            1
            for niche in sorted(archive["elites"])
            if any(
                founder
                in archive["elites"][niche]["grid"]
                .get("lineage", {})
                .get("ancestor_ids", [])
                for founder in founder_ids
            )
        )
        summary["workshop"] = {
            "released_count": released_count,
            "founder_ids": sorted(founder_ids),
            "rejected": workshop_rejected,
            "creature_count_by_generation": [
                sum(1 for c in generation["creatures"] if _is_workshop(c))
                for generation in generation_reports
            ],
            "archive_elite_count": elite_ids_with_workshop_ancestry,
            "mean_fitness": _mean_fitness(workshop_creatures),
            "corpus_mean_fitness": _mean_fitness(corpus_creatures),
            "lineage_survived_beyond_founding": any(
                _is_workshop(c)
                for generation in generation_reports[1:]
                for c in generation["creatures"]
            ),
        }
    if workshop:
        report_lab_id = "mecha_engine_evolution_workshop_wire_stage0"
    elif stress:
        report_lab_id = "mecha_engine_evolution_hard_regime_stage0"
    else:
        report_lab_id = "mecha_engine_evolution_loop_stage0"
    result = {
        "lab_id": report_lab_id,
        "date": "2026-07-05",
        "rng_seed": rng_seed,
        "generations_requested": generations,
        "population": population,
        "damage_cycles": damage_cycles,
        "ticks": ticks,
        "dropout_rate": dropout_rate,
        "repair_epochs": repair_epochs,
        "purpose": (
            "Multi-generation evolution through the composed engine: "
            "archive elites become parents, and every creature survives "
            "repeated damage/repair cycles with full lifecycle episodes "
            "between regenerations."
        ),
        "source_artifacts": [
            "data/runtime_integration/mecha_engine_runtime_loop_stage0.json",
            "research/package_specs/mecha_engine_module_interfaces.md",
            "research/package_specs/mecha_engine_repair_interface_spec.md",
        ],
        "generations": generation_reports,
        "summary": summary,
        "closed_states": [
            "archive_elites_become_parents_across_generations",
            "repeated_damage_repair_cycles_with_episodes_between",
        ],
        "blocked_states": [
            "runtime_package_target_absent_decision_record_gated",
            "readability_proxy_uncalibrated_manual_calibration_deferred",
        ],
        "decision": _evolution_decision(summary),
        "next_research_step": (
            "Design the mecha_engine.runtime surface from this loop's "
            "evidence (decision record 0008) and study longer-horizon "
            "evolution: more generations, mutation-profile variation, and "
            "fitness trajectories under the calibrated readability score "
            "once human ratings exist."
        ),
    }
    if parent_selection is not None:
        result["parent_selection"] = parent_selection
    if (
        slip_profile.get("slip_version") != "0.1.0"
        and "species_class" in slip_profile
    ):
        result["species_class"] = slip_profile["species_class"]
    if workshop:
        result["workshop_grids_dir"] = (
            Path(workshop_grids_dir).resolve().relative_to(ROOT).as_posix()
            if Path(workshop_grids_dir).resolve().is_relative_to(ROOT)
            else str(workshop_grids_dir)
        )
        result["purpose"] = (
            "T1, the workshop->engine asset wire: released workshop "
            "creatures join the evolution founder pool through the "
            "engine's own gates, and their lineages are traced through "
            "every generation — the og promise that user-authored assets "
            "influence evolution, measured."
        )
        result["next_research_step"] = (
            "With workshop lineages measurably competing in the "
            "ecosystem, propose the runtime.evolve seed-source contract "
            "extension by decision record (T1.5, owner-gated) and grow "
            "the released corpus."
        )
    if stress:
        result["survival_regime"] = "stress_probe"
        result["next_research_step"] = (
            "With survival now morphology-dependent, study whether "
            "selection climbs (mean stress load / survival by generation) "
            "over longer horizons, then give the learning module this "
            "regime as its evaluation environment (decision record 0009 "
            "candidate)."
        )
    return result


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
    stress = summary.get("survival_regime") == "stress_probe"
    if all_green:
        status = (
            "evolution_under_stress_composed"
            if stress
            else "evolution_loop_composed"
        )
        reason = (
            "Archive elites reproduce: every creature in every generation "
            "validates, survives repeated damage/repair cycles with full "
            "episodes between regenerations, stays SLIP-aligned, and "
            "scores back into the archive; ancestry deepens generation "
            "over generation. Fitness and archive trajectories are "
            "reported as measurements, not gates."
        )
        if stress:
            reason += (
                " Under the stress regime, episode death is a legitimate "
                "measured outcome (see death_count and the per-generation "
                "load/survival trajectories), never a contract failure."
            )
    else:
        status = (
            "evolution_under_stress_gaps_measured"
            if stress
            else "evolution_loop_gaps_measured"
        )
        reason = (
            "At least one creature fell short of a module contract inside "
            "the evolution loop; the per-creature stage flags and cycle "
            "records name exactly where."
        )
    decision = {
        "status": status,
        "adoption": "lab_only_runtime_evidence",
        "reason": reason,
    }
    if stress:
        loads = summary["mean_stress_load_by_generation"]
        survival = summary["mean_survival_ratio_by_generation"]
        decision["observations"] = {
            "mean_load_last_vs_first": round(loads[-1] - loads[0], 6),
            "mean_survival_last_vs_first": round(
                survival[-1] - survival[0], 6
            ),
            "deaths_observed": summary["death_count"] > 0,
        }
    return decision


def write_evolution_loop_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    stress = report.get("survival_regime") == "stress_probe"
    (output_dir / f"{report['lab_id']}.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    summary = report["summary"]
    wire = "workshop" in report["summary"]
    if wire:
        readme_name = "evolution_workshop_wire_README.md"
    elif stress:
        readme_name = "evolution_hard_regime_README.md"
    else:
        readme_name = "evolution_loop_README.md"
    regime_lines = ""
    if wire:
        workshop_summary = report["summary"]["workshop"]
        regime_lines += (
            f"- Workshop wire: {len(workshop_summary['founder_ids'])} founder(s) "
            f"admitted of {workshop_summary['released_count']} released "
            f"({len(workshop_summary['rejected'])} rejected by the engine's gates)\n"
            f"- Workshop-lineage creatures by generation: "
            f"{workshop_summary['creature_count_by_generation']}\n"
            f"- Workshop-ancestry elites in the archive: "
            f"{workshop_summary['archive_elite_count']}\n"
            f"- Mean fitness workshop vs corpus lineages: "
            f"{workshop_summary['mean_fitness']} vs "
            f"{workshop_summary['corpus_mean_fitness']}\n"
        )
    if stress:
        regime_lines = (
            f"- Survival regime: stress_probe (episodes on the contracted "
            f"morphology stress probe)\n"
            f"- Mean stress load by generation: "
            f"{summary['mean_stress_load_by_generation']}\n"
            f"- Mean survival by generation: "
            f"{summary['mean_survival_ratio_by_generation']}\n"
            f"- Deaths: {summary['death_count']}\n"
        )
    (output_dir / readme_name).write_text(
        "# Mecha Engine Evolution Loop Stage 0\n\n"
        "Multi-generation evolution through the composed engine: archive "
        "elites become parents; every creature survives repeated "
        "damage/repair cycles with episodes between regenerations.\n\n"
        "Key results:\n\n"
        f"- Generations: {summary['generation_count']} × "
        f"{report['population']} creatures × {report['damage_cycles']} "
        f"damage cycles ({summary['total_damage_events']} damage events)\n"
        f"- Candidate validity: {summary['candidate_valid_rate']}\n"
        f"- SLIP alignment retention: {summary['slip_alignment_retention_rate']}\n"
        f"- Position restoration: {summary['mean_position_restoration']} "
        f"(token {summary['mean_token_restoration']})\n"
        f"- Mean fitness by generation: {summary['mean_fitness_by_generation']}\n"
        f"- Max lineage generation: {summary['max_lineage_generation']}\n"
        f"- Archive: {summary['archive']['filled_niches']} niches, "
        f"QD {summary['archive']['qd_score']}\n"
        + regime_lines
        + f"- Decision: {report['decision']['status']}\n",
        encoding="utf-8",
    )


def write_runtime_loop_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")


def _readme_text(report: dict) -> str:
    summary = report["summary"]
    return (
        "# Mecha Engine Runtime Loop Stage 0\n\n"
        "All six promoted `mecha_engine` modules composed through the "
        "cross-module MVP flow plus the repair damage-event contract.\n\n"
        "Key results:\n\n"
        f"- Runs: {summary['run_count']} creatures, {report['ticks']} ticks/episode\n"
        f"- Candidate validity: {summary['candidate_valid_rate']}\n"
        f"- Repaired validity: {summary['repaired_valid_rate']}\n"
        f"- SLIP alignment retention after repair: "
        f"{summary['slip_alignment_retention_rate']} "
        f"({summary['archived_run_count']}/{summary['run_count']} runs archived)\n"
        f"- Position restoration: {summary['mean_position_restoration']} "
        f"(token restoration {summary['mean_token_restoration']})\n"
        f"- Survival ratio pre/post repair: {summary['mean_survival_ratio_pre']} "
        f"/ {summary['mean_survival_ratio_post']}\n"
        f"- Archive: {summary['archive']['filled_niches']} niches, "
        f"QD {summary['archive']['qd_score']}\n"
        f"- Provenance: ledger_ok={report['provenance']['ledger_ok']}, "
        f"ci_ok={report['provenance']['ci_ok']}\n"
        f"- Decision: {report['decision']['status']}\n\n"
        "Readability enters the archive as the uncalibrated proxy with its "
        "manual-rating status visible (calibration deferred by owner "
        "decision). The runtime package target remains "
        "decision-record-gated.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the mecha_engine runtime integration loops."
    )
    parser.add_argument(
        "--mode", choices=["single", "evolution"], default="single"
    )
    parser.add_argument(
        "--regime", choices=["sheltered", "stress_probe"], default="sheltered"
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--generations", type=int, default=4)
    parser.add_argument("--population", type=int, default=8)
    parser.add_argument("--damage-cycles", type=int, default=3)
    parser.add_argument("--ticks", type=int, default=72)
    parser.add_argument("--dropout-rate", type=float, default=0.2)
    parser.add_argument("--rng-seed", type=int, default=20260512)
    parser.add_argument(
        "--workshop-dir",
        type=Path,
        default=None,
        help="Directory of RELEASED workshop creatures to admit as "
        "evolution founders (T1 wire); e.g. data/workshop/released.",
    )
    args = parser.parse_args()
    if args.mode == "evolution":
        report = run_mecha_engine_evolution_loop(
            generations=args.generations,
            population=args.population,
            damage_cycles=args.damage_cycles,
            ticks=args.ticks,
            dropout_rate=args.dropout_rate,
            rng_seed=args.rng_seed,
            survival_regime=args.regime,
            workshop_grids_dir=args.workshop_dir,
        )
        write_evolution_loop_artifacts(args.output_dir, report)
    else:
        report = run_mecha_engine_runtime_loop(
            count=args.count,
            ticks=args.ticks,
            dropout_rate=args.dropout_rate,
            rng_seed=args.rng_seed,
        )
        write_runtime_loop_artifacts(args.output_dir, report)
    print(json.dumps(report["summary"], indent=2))
    print(json.dumps(report["decision"], indent=2))


if __name__ == "__main__":
    main()
