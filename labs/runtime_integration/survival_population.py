"""X8 laboratory living breeder population algorithm.

The archive is historical evidence; generation_survivors_v1 parents are the
immediately prior generation's qualified candidate occurrences. The retained
legacy branch remains the default. Independent lifecycle episodes are designed
qualification trials, not continuous aging or biological reproduction.
"""
from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy

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

from mecha_engine.runtime._cubff import extract_cubff_features, features_to_traits
from mecha_engine.runtime._readability import learned_readability_score
from mecha_engine.slip import is_grid_aligned
from survival_live import (live_cycle, _episode_digest, endpoint_qualified,
                           endpoint_reason, evaluation_grid)
from mecha_engine.runtime.care import (CARE_POLICIES, CARE_EVALUATORS, care_context_sha256,
                   care_grid_sha256, select_care_successor, validate_care_context)

REPORT_ID = "mecha_engine_runtime_evolve"


# R2.5 (decision record 0020): CuBFF Pipeline C promoted from the lab
# loop verbatim â€” lineage dynamics -> mutation weights. mutation_pressure
# in [0,1] scales per-generation damage severity by 1 + GAIN*(pressure-0.5),
# clamped so the ecosystem never trivially collapses. Only scalars cross
# the boundary (never tape tokens â€” the semantic-compiler rule).
CUBFF_PRESSURE_GAIN = 1.1
CUBFF_MULTIPLIER_BAND = (0.5, 1.6)


def _cubff_generation_pressure(
    snapshot: dict, *, density_pressure: bool = False
) -> tuple[float, float]:
    """(mutation_pressure, dropout_multiplier) for one generation.

    ``density_pressure`` is DR 0045's rider: OFF by default and
    byte-identical there (pinned). On, instruction density enters as
    its own named channel â€” the one signal the CHECKPOINT format
    carries that RISES as a soup organizes, and therefore the
    counterweight to entropy terms that fall. It never synthesizes the
    structurally-absent replication or lineage channels.
    """
    from mecha_engine.runtime._cubff import CUBFF_DENSITY_WEIGHT

    features = extract_cubff_features(snapshot, include_density=density_pressure)
    pressure = features_to_traits(
        features,
        density_weight=CUBFF_DENSITY_WEIGHT if density_pressure else 0.0,
    )["mutation_pressure"]
    raw = 1.0 + CUBFF_PRESSURE_GAIN * (pressure - 0.5)
    low, high = CUBFF_MULTIPLIER_BAND
    return round(pressure, 6), round(max(low, min(high, raw)), 6)


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
    founder_grids: list[dict] | None = None,
    cubff_pressure_source: list[dict] | None = None,
    readability_selection: dict | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
    recording_callback: Callable[[dict], None] | None = None,
    admission_callback: Callable[[dict], None] | None = None,
    founder_care_contexts: list[dict | None] | None = None,
    care_selection_policy: str = "off",
    care_evaluator: str = "archive_morphology_probe_v1",
    population_policy: str = "legacy_archive",
    founder_start_mode: str | None = None,
    survival_regime: str = "sheltered",
    cubff_density_pressure: bool = False,
    evaluation_callback: Callable[[dict], None] | None = None,
    body_response: str = "legacy",
) -> tuple[dict, dict]:
    """Run multi-generation evolution through the composed engine.

    Returns ``(archive, report)``: the final ``mecha_engine.archive``
    archive (whose elites carry full audit records) and a
    JSON-serializable report mirroring the evolution-loop lab's report
    shape for ``generations``, ``summary``, and ``decision``.
    ``readability_scorer`` is a deterministic callable ``grid ->``
    readability record (or bare proxy score) â€” the injected "equivalent
    metrics hook"; the archive keeps its manual-rating status visible.
    ``progress_callback(completed, budget)`` is optional observation: zero
    before evaluation, then one call after each fully recorded candidate.
    Exceptions propagate for caller-owned cancellation; early extinction may
    finish below the requested budget. No output field or seed changes.
    ``recording_callback`` receives isolated original live-cycle records when
    an inserted/replaced candidate becomes the overall best (fitness, niche).
    It never re-simulates; frame data stays outside the scientific result.
    ``admission_callback`` observes every actual founder verdict in submission
    order, including duplicate IDs. Its isolated dictionary carries
    ``submission_index``, ``grid_id``, ``admitted`` and ``rejection_errors``
    (None on admission). Exceptions propagate for foreground cancellation;
    no scientific output fields, admission rules or RNG draws change.
    Deterministic end to end; never mutates ``seed_grids``,
    ``slip_profile``, the models, or any caller-owned input.

    ``founder_grids`` (decision record 0016, the T1 wire's contract):
    released creatures admitted through the engine's own gates
    (``validate_grid`` + SLIP alignment; rejections recorded verbatim);
    admitted founders LEAD the generation-0 parent pool. ``None`` is
    byte-identical to the pre-0016 contract.

    ``cubff_pressure_source`` (decision record 0020, promoting the R2
    seam): an ordered list of CuBFF snapshots, one consumed per
    generation (cycled if fewer). Each generation's
    ``extract_cubff_features -> mutation_pressure`` scales that
    generation's damage severity â€” real computational-life dynamics
    shaping the ecosystem (Pipeline C). Only pressure scalars cross the
    boundary; CuBFF never sets cell tokens. ``None`` is byte-identical.

    ``readability_selection`` (decision record 0025, promoting the R3
    live consumer): ``{"weights": ..., "reference_features": ...,
    "blend": 0.5}`` â€” the LEARNED readability model (DR 0019) steers
    elite parenting: parents ranked by ``blend * learned_readability +
    (1 - blend) * min-max-normalized fitness`` (lab-verbatim ordering;
    takes precedence over ``lineage_preferences`` exactly as in the
    lab). The report gains a rung-conditional ``readability_selection``
    block with per-generation mean learned readability over candidates.
    The manual rating system remains the fallback; ``None`` is
    byte-identical.
    """
    if body_response not in ("legacy", "workload-v1"):
        raise ValueError("unsupported body response")
    if population_policy not in ("legacy_archive", "generation_survivors_v1"):
        raise ValueError("unsupported population policy")
    survivors = population_policy == "generation_survivors_v1"
    if founder_start_mode not in (None, "bootstrap", "continue"):
        raise ValueError("unsupported founder start mode")
    if survivors and founder_start_mode is None:
        raise ValueError("generation_survivors_v1 requires an explicit founder start mode")
    if not survivors and founder_start_mode == "continue":
        raise ValueError("legacy archive cannot honor explicit continuation")
    if survivors and founder_start_mode == "continue" and not isinstance(founder_grids, list):
        raise ValueError("continuation requires an explicit founder list, including []")
    if survival_regime not in ("sheltered", "stress_probe"):
        raise ValueError("unsupported survival regime")
    if type(cubff_density_pressure) is not bool:
        raise ValueError("cubff_density_pressure must be boolean")
    if cubff_density_pressure and cubff_pressure_source is None:
        raise ValueError("density pressure requires a weather source")
    if survivors and (type(damage_cycles) is not int or damage_cycles < 0):
        raise ValueError("damage_cycles must be a non-negative integer")
    if survivors and (type(ticks) is not int or ticks < 0):
        raise ValueError("ticks must be a non-negative integer")
    stress = survival_regime == "stress_probe"
    final_breeders = []
    initial_parent_occurrences = []
    admitted_occurrences = []
    termination = None
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
    if cubff_pressure_source is not None and (
        not isinstance(cubff_pressure_source, list) or not cubff_pressure_source
    ):
        raise ValueError(
            "cubff_pressure_source must be a non-empty list of CuBFF snapshots"
        )
    if readability_selection is not None and (
        not isinstance(readability_selection, dict)
        or not isinstance(readability_selection.get("weights"), dict)
    ):
        raise ValueError(
            "readability_selection must be a mapping carrying the learned "
            "model's 'weights' (DR 0019)"
        )

    if care_selection_policy not in ("off", *CARE_POLICIES):
        raise ValueError("care selection policy must be off or " + " or ".join(CARE_POLICIES))
    if care_evaluator not in CARE_EVALUATORS:
        raise ValueError("unsupported care evaluator: " + str(care_evaluator))
    care_contexts = None
    if founder_care_contexts is not None:
        if (not isinstance(founder_care_contexts, list)
                or (founder_grids is None and founder_care_contexts != [])
                or len(founder_care_contexts) != len(founder_grids or [])):
            raise ValueError("founder care contexts must match ordered founder occurrences")
        care_contexts = [validate_care_context(value) if value is not None else None
                         for value in founder_care_contexts]
    if any(value is not None and value.get("body_response", "legacy") != body_response
           for value in care_contexts or []):
        raise ValueError("founder care body response differs from era model")
    care_active = care_contexts is not None and any(value is not None for value in care_contexts)
    admitted_care: list[dict | None] = []
    archive_care: dict[str, dict | None] = {}

    # T3.4 (decision record 0013): a v0.2 profile's lineage preference
    # steers elite parenting; v0.1 profiles never carry the field. The
    # version guard mirrors the lab loop's own reading of the profile.
    parent_selection = (
        slip_profile.get("lineage_preferences", {}).get("parent_selection")
        if isinstance(slip_profile, dict)
        and slip_profile.get("slip_version") != "0.1.0"
        else None
    )
    admitted_founders: list[dict] = []
    rejected_founders: list[dict] = []
    era_grid_size = seed_grids[0].get("grid_size") if seed_grids else None
    if founder_grids is not None:
        if not isinstance(founder_grids, list):
            raise ValueError("founder_grids must be a list of grid genomes")
        for submission_index, founder in enumerate(founder_grids):
            errors: list[str] = []
            validation = validate_grid(founder)
            errors.extend(validation.errors)
            alignment = is_grid_aligned(founder, slip_profile)
            errors.extend(alignment.errors)
            # A4 (DR 0029): eras are size-coherent â€” a founder whose
            # canvas differs from the era's seed corpus is rejected
            # through the gate (recorded verbatim), never bred against a
            # mismatched generation model. 8x8-only flows are untouched
            # (founders always matched their seeds before multi-scale).
            founder_grid_size = founder.get("grid_size")
            if not errors and founder_grid_size != era_grid_size:
                founder_label = (
                    f"{founder_grid_size[0]}x{founder_grid_size[1]}"
                    if isinstance(founder_grid_size, list)
                    and len(founder_grid_size) == 2
                    else str(founder_grid_size)
                )
                era_label = (
                    f"{era_grid_size[0]}x{era_grid_size[1]}"
                    if isinstance(era_grid_size, list)
                    and len(era_grid_size) == 2
                    else str(era_grid_size)
                )
                errors.append(
                    f"founder grid is {founder_label} but the era runs at "
                    f"{era_label}"
                )
            if errors:
                rejected_founders.append(
                    {"grid_id": founder.get("grid_id"), "errors": errors}
                )
            else:
                admitted_founders.append(founder)
                admitted_occurrences.append(_source_ref("submitted_founder", founder,
                                                          submission_index=submission_index))
                context = care_contexts[submission_index] if care_contexts is not None else None
                admitted_care.append({"context": context, "founder_submission_index": submission_index}
                                     if context is not None else None)
            if admission_callback is not None:
                admission_callback(deepcopy({
                    "submission_index": submission_index,
                    "grid_id": founder.get("grid_id"),
                    "admitted": not errors,
                    "rejection_errors": errors if errors else None,
                }))

    def seed_admitted(seed):
        return (is_grid_aligned(seed, slip_profile).ok
                and (not survivors or (validate_grid(seed).ok and seed.get("grid_size") == era_grid_size)))
    seed_pool = [seed for seed in seed_grids if seed_admitted(seed)]
    if not seed_pool and not (survivors and founder_start_mode == "continue"):
        raise ValueError("no seed grid satisfies the SLIP profile")

    seed_occurrences = [_source_ref("seed_corpus", seed, source_position=i)
                        for i, seed in enumerate(seed_grids)
                        if seed_admitted(seed)]
    archive = build_archive([], {})
    generation_reports: list[dict] = []
    manual_rating_statuses: set[str] = set()
    max_lineage_generation = 0

    cubff = cubff_pressure_source is not None
    cubff_by_generation: list[dict] = []

    # C1 (decision record 0025): R3's live consumer promoted verbatim â€”
    # the LEARNED model steers parenting; manual rating stays the fallback.
    readability = readability_selection is not None
    readability_blend = (
        float(readability_selection.get("blend", 0.5)) if readability else 0.0
    )
    readability_model = (
        {
            "weights": dict(readability_selection["weights"]),
            "reference_features": dict(
                readability_selection.get("reference_features", {})
            ),
        }
        if readability
        else None
    )
    readability_means: list[float] = []

    # DR 0073: the lab-proven observer changes neither RNG nor report fields.
    if progress_callback is not None:
        progress_callback(0, generations * population)
    generation_indices = range(generations)
    if survivors and founder_start_mode == "continue" and not admitted_founders:
        termination = _termination([], None, "all_founders_rejected" if founder_grids else "empty_continuation")
        generation_indices = ()
    for generation_index in generation_indices:
        generation_dropout = dropout_rate
        if cubff:
            snapshot = cubff_pressure_source[
                generation_index % len(cubff_pressure_source)
            ]
            pressure, multiplier = _cubff_generation_pressure(snapshot, density_pressure=cubff_density_pressure)
            generation_dropout = round(dropout_rate * multiplier, 6)
            cubff_by_generation.append(
                {
                    "snapshot_id": str(snapshot.get("snapshot_id", "cubff")),
                    "mutation_pressure": pressure,
                    "dropout_multiplier": multiplier,
                }
            )
        if survivors:
            if generation_index == 0:
                if founder_start_mode == "continue":
                    parents = admitted_founders
                    parent_care = admitted_care
                    parent_occurrences = admitted_occurrences
                    parent_source = "continuing_founders"
                else:
                    parents = admitted_founders + seed_pool
                    parent_care = admitted_care + [None] * len(seed_pool)
                    parent_occurrences = admitted_occurrences + seed_occurrences
                    parent_source = "founders_plus_seed_pool" if admitted_founders else "seed_pool"
                initial_parent_occurrences = deepcopy(parent_occurrences)
                if not parents:
                    termination = _termination([], None, "all_founders_rejected" if founder_grids else "empty_continuation")
                    break
            else:
                ordered_breeders = _ordered_breeders(final_breeders, parent_selection,
                                                    readability_model, readability_blend)
                parents = [b["grid"] for b in ordered_breeders]
                parent_care = [{"context": b["care_context"],
                                "founder_submission_index": b["care_context_origin"]["founder_submission_index"]}
                               if b["care_context"] is not None else None for b in ordered_breeders]
                parent_occurrences = [_source_ref("generation_breeder", b["grid"],
                    generation_index=b["generation_index"],candidate_index=b["candidate_index"])
                    for b in ordered_breeders]
                parent_source = ("generation_breeders_readability_blend" if readability
                                 else "generation_breeders_fitness_weighted" if parent_selection == "fitness_weighted"
                                 else "generation_breeders")
        elif generation_index == 0:
            if admitted_founders:
                # Founders lead so the round-robin always exercises the
                # wire deterministically (decision record 0016).
                parents = admitted_founders + seed_pool
                parent_care = admitted_care + [None] * len(seed_pool)
                parent_source = "founders_plus_seed_pool"
            else:
                parents = seed_pool
                parent_care = [None] * len(seed_pool)
                parent_source = "seed_pool"
        else:
            elites = archive["elites"]
            if readability and elites:
                # R3 (decision record 0019): the LEARNED model steers
                # parenting. Fitness is min-max normalized across the
                # current elites so the blend weighs comparable scales.
                fitnesses = [elites[niche]["fitness"] for niche in elites]
                low, high = min(fitnesses), max(fitnesses)
                span = (high - low) or 1.0

                def _blended(niche: str) -> float:
                    fitness_norm = (elites[niche]["fitness"] - low) / span
                    learned = learned_readability_score(
                        elites[niche]["grid"], readability_model
                    )
                    return (
                        readability_blend * learned
                        + (1.0 - readability_blend) * fitness_norm
                    )

                ordered = sorted(
                    elites, key=lambda niche: (-_blended(niche), niche)
                )
                parents = [elites[niche]["grid"] for niche in ordered]
                parent_source = "archive_elites_readability_blend"
            elif parent_selection == "fitness_weighted":
                # T3.4: breed from the fittest elites first (deterministic
                # truncation bias â€” with population <= elite count only
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
                ordered = sorted(elites)
                parents = [elites[niche]["grid"] for niche in ordered]
                parent_source = "archive_elites"
            parent_care = [archive_care.get(niche) for niche in ordered]
            if not parents:
                break  # measured, not asserted: an empty archive ends evolution

        creatures = []
        generation_breeders = []
        generation_readability: list[float] = []
        for index in range(population):
            parent = parents[index % len(parents)]
            care_origin = parent_care[index % len(parents)]
            care_receipt = None
            run_seed = rng_seed + generation_index * 100000 + index
            stages: dict[str, bool] = {}

            if care_origin is not None and care_selection_policy != "off":
                candidate, care_receipt = select_care_successor(
                    parent, generation_model, slip_profile, rng_seed=run_seed,
                    context=care_origin["context"], policy=care_selection_policy,
                    evaluator=care_evaluator,
                    **({"body_response": body_response} if body_response != "legacy" else {}),
                )
            else:
                candidate = generate_candidate(
                    parent, generation_model, slip_profile, rng_seed=run_seed
                )
            if readability:
                generation_readability.append(
                    learned_readability_score(candidate, readability_model)
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
                dropout_rate=generation_dropout,
                rng_seed=run_seed,
                population_policy=population_policy, survival_regime=survival_regime,
                **({"body_response": body_response} if body_response != "legacy" else {}),
                **({"record_frames": True} if recording_callback is not None or evaluation_callback is not None else {}),
            )
            cycles = ([{k: v for k, v in cycle.items() if k != "frames"}
                       for cycle in lived["cycles"]] if recording_callback is not None or evaluation_callback is not None else lived["cycles"])
            current = lived["final_grid"]
            stages["all_cycles_valid"] = lived["all_cycles_valid"]
            stages["all_cycles_aligned"] = lived["all_cycles_aligned"]

            score_digest = None
            final_episode = None
            final_episode_grid, final_load = evaluation_grid(current, survival_regime)
            # Verbatim lab semantics (T1, commit d382805; promotion-drift
            # fix 2026-07-07): an aligned-but-invalid creature is
            # "skipped_invalid", and scoring requires every cycle valid
            # AND aligned with a final-cycle episode.
            decision = (
                "skipped_invalid"
                if stages["all_cycles_aligned"]
                and not stages["all_cycles_valid"]
                else "skipped_unaligned"
            )
            stages["scored"] = False
            if (
                stages["all_cycles_valid"]
                and stages["all_cycles_aligned"]
                and ((not survivors and cycles and cycles[-1]["episode"] is not None)
                     or (survivors and lived["stop"] is None
                         and lived["cycles_qualified"] == damage_cycles))
            ):
                final_episode = run_episode(
                    final_episode_grid,
                    slip_profile,
                    policy="switchboard",
                    ticks=ticks,
                    rng_seed=run_seed,
                    **({"body_response": body_response} if body_response != "legacy" else {}),
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
                if stress:
                    score_digest["final_episode"] = _episode_digest(final_episode, ticks, evaluated_grid=final_episode_grid)
                before_log = len(archive["insertion_log"])
                archive = insert_candidate(
                    archive, archive_candidate, score, descriptor
                )
                event = (
                    archive["insertion_log"][before_log]["event"]
                    if len(archive["insertion_log"]) > before_log
                    else "unlogged"
                )
                if event.startswith(("inserted", "replaced")):
                    niche = archive["insertion_log"][before_log]["niche"]
                    archive_care[niche] = deepcopy(care_origin)
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
                    **({"care_context_origin": {
                        "founder_submission_index": care_origin["founder_submission_index"],
                        "context_sha256": care_context_sha256(care_origin["context"]),
                    }} if care_origin is not None else {}),
                    **({"care_selection": care_receipt} if care_receipt is not None else {}),
                }
            )

            if stress:
                creatures[-1]["stress_load"] = final_load
            if survivors:
                stop = deepcopy(lived["stop"])
                if stop is None and not endpoint_qualified(final_episode, ticks):
                    stop = {"stage": "final_episode", "cycle_index": None,
                            "reason": endpoint_reason(final_episode)}
                eligible = stop is None and score_digest is not None
                if score_digest is None and stop is not None:
                    creatures[-1]["archive_decision"] = (
                        "skipped_dead" if stop["reason"] == "lifecycle_death"
                        else "skipped_invalid" if stop["reason"] in ("invalid_candidate", "invalid_repair")
                        else "skipped_unaligned" if stop["reason"] == "unaligned_repair" else "skipped_incomplete")
                creatures[-1]["breeding"] = {
                    "occurrence": {"generation_index": generation_index, "candidate_index": index},
                    "parent_occurrence": deepcopy(parent_occurrences[index % len(parents)]),
                    "candidate_grid_sha256": care_grid_sha256(candidate),
                    "final_grid_sha256": care_grid_sha256(current),
                    "cycles_requested": damage_cycles, "cycles_attempted": len(cycles),
                    "cycles_qualified": lived["cycles_qualified"],
                    "final_episode": _episode_digest(final_episode, ticks, evaluated_grid=final_episode_grid) if final_episode is not None else None,
                    "eligible": eligible, "stop": stop,
                }
                if eligible:
                    generation_breeders.append({
                        "generation_index": generation_index, "candidate_index": index,
                        "grid_id": current["grid_id"], "grid": deepcopy(current),
                        "grid_sha256": care_grid_sha256(current), "fitness": score_digest["fitness"],
                        "learned_readability": learned_readability_score(current, readability_model) if readability else None,
                        "care_context": deepcopy(care_origin["context"]) if care_origin is not None else None,
                        "care_context_origin": deepcopy(creatures[-1].get("care_context_origin")),
                    })
            if evaluation_callback is not None:
                evaluation_callback(deepcopy({
                    "generation_index": generation_index, "candidate_index": index,
                    "run_seed": run_seed, "parent_grid": parent, "candidate_grid": candidate,
                    "final_grid": current, "effective_dropout_rate": generation_dropout,
                    "generation_weather": cubff_by_generation[-1] if cubff else None,
                    "cycles": [{**cycle, "damage_seed": run_seed * 10 + cycle["cycle"]} for cycle in lived["cycles"]], "final_episode": final_episode,
                    "creature": creatures[-1],
                }))

            # DR0074: lab-proven original evaluation observation, no RNG or selection change.
            if recording_callback is not None and decision in ("inserted", "replaced"):
                best_niche = max(archive["elites"], key=lambda n: (archive["elites"][n]["fitness"], n))
                if archive["elites"][best_niche]["grid"] == current:
                    recording_callback(deepcopy({
                        "era_seed": rng_seed, "run_seed": run_seed,
                        "generation_index": generation_index, "candidate_index": index,
                        "effective_dropout_rate": generation_dropout,
                        "generation_weather": cubff_by_generation[-1] if cubff else None,
                        "damage_cycles": damage_cycles, "ticks": ticks,
                        "niche_key": best_niche, "fitness": archive["elites"][best_niche]["fitness"],
                        "candidate_grid": candidate, "lived": lived,
                    }))
            if progress_callback is not None:
                progress_callback(generation_index * population + index + 1, generations * population)

        summary_after = archive_summary(archive)
        if readability:
            readability_means.append(
                round(
                    sum(generation_readability) / len(generation_readability),
                    6,
                )
                if generation_readability
                else 0.0
            )
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

        if survivors:
            final_breeders = generation_breeders
            termination = _termination(creatures, generation_index,
                "requested_horizon_complete" if final_breeders else "no_eligible_breeders")
            if not final_breeders:
                break

    summary = _evolution_summary(
        generation_reports, archive, max_lineage_generation, allow_empty=survivors
    )
    if stress:
        summary["survival_regime"] = "stress_probe"
        summary["mean_stress_load_by_generation"] = [
            round(sum(c["stress_load"] for c in g["creatures"]) / len(g["creatures"]), 6)
            for g in generation_reports]
        final_episodes = [[c["score"]["final_episode"] for c in g["creatures"] if c["score"] is not None]
                          for g in generation_reports]
        summary["mean_survival_ratio_by_generation"] = [
            round(sum(e["survival_ratio"] for e in episodes) / len(episodes), 6) if episodes else 0.0
            for episodes in final_episodes]
        summary["death_count"] = sum(not e["alive"] for episodes in final_episodes for e in episodes)
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
        **(
            {
                "founders": {
                    "admitted_ids": [
                        grid["grid_id"] for grid in admitted_founders
                    ],
                    "rejected": rejected_founders,
                }
            }
            if founder_grids is not None
            else {}
        ),
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
    if stress:
        report["survival_regime"] = "stress_probe"
    if survivors:
        report["living_population"] = {
            "format": "generation_survivors_v1", "population_policy": population_policy,
            "founder_start_mode": founder_start_mode, "survival_regime": survival_regime,
            "initial_parent_occurrences": initial_parent_occurrences,
            "requested_candidate_slots": generations * population,
            "evaluated_candidates": summary["creature_count"],
            "unexecuted_candidate_slots": generations * population - summary["creature_count"],
            "final_breeders": final_breeders, "termination": termination,
        }
        report["decision"] = {
            "status": "living_population_completed" if not termination["ended"] else "living_population_ended",
            "adoption": "experimental_population_api",
            "reason": "Endpoint-qualified candidate occurrences replace the prior generation; historical archives remain separate.",
        }
    if parent_selection is not None:
        report["parent_selection"] = parent_selection
    if cubff:
        report["cubff_pressure"] = {
            "semantic_rule": "lineage_dynamics_to_mutation_weights_pipeline_c",
            "pressure_gain": CUBFF_PRESSURE_GAIN,
            "multiplier_band": list(CUBFF_MULTIPLIER_BAND),
            "source_snapshot_count": len(cubff_pressure_source),
            "by_generation": cubff_by_generation,
            **({"density_pressure": True} if cubff_density_pressure else {}),
        }
    if readability:
        report["readability_selection"] = {
            "readability_authority": (
                "learned_model_primary_manual_rating_fallback"
            ),
            "blend": readability_blend,
            "weights": dict(readability_model["weights"]),
            "reference_features": dict(
                readability_model["reference_features"]
            ),
            "mean_learned_readability_by_generation": readability_means,
        }
    if care_active:
        elite_order = sorted(archive["elites"])
        report["care_selection"] = {
            "policy": care_selection_policy, "evaluator": care_evaluator,
            "founder_contexts": deepcopy(care_contexts),
            "elite_contexts": [deepcopy(archive_care[niche]["context"])
                               if archive_care.get(niche) is not None else None
                               for niche in elite_order],
            "elite_origins": [{"founder_submission_index": archive_care[niche]["founder_submission_index"],
                               "context_sha256": care_context_sha256(archive_care[niche]["context"])}
                              if archive_care.get(niche) is not None else None for niche in elite_order],
        }
    if body_response != "legacy":
        report["body_response"] = body_response
    return archive, report


def _evolution_summary(
    generation_reports: list[dict], archive: dict, max_lineage_generation: int, *, allow_empty: bool = False
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
        ) if count or not allow_empty else None,
        "slip_alignment_retention_rate": round(
            sum(1 for c in creatures if c["stages"]["all_cycles_aligned"])
            / count,
            6,
        ) if count or not allow_empty else None,
        "mean_position_restoration": round(
            sum(cycle["position_restoration"] for cycle in cycles)
            / len(cycles),
            6,
        ) if cycles or not allow_empty else None,
        "mean_token_restoration": round(
            sum(cycle["token_restoration"] for cycle in cycles) / len(cycles),
            6,
        ) if cycles or not allow_empty else None,
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
        "adoption": "package_runtime_surface",
        "reason": reason,
    }
    if stress:
        loads = summary["mean_stress_load_by_generation"]
        survival = summary["mean_survival_ratio_by_generation"]
        decision["observations"] = {
            "mean_load_last_vs_first": round(loads[-1] - loads[0], 6) if loads else None,
            "mean_survival_last_vs_first": round(
                survival[-1] - survival[0], 6
            ) if survival else None,
            "deaths_observed": summary["death_count"] > 0,
        }
    return decision



def _source_ref(kind: str, grid: dict, **position: int) -> dict:
    return {"kind": kind, **position, "grid_id": grid["grid_id"], "grid_sha256": care_grid_sha256(grid)}


def _ordered_breeders(breeders: list[dict], parent_selection: str | None,
                      readability_model: dict | None, blend: float) -> list[dict]:
    if readability_model is not None and breeders:
        low = min(b["fitness"] for b in breeders)
        span = (max(b["fitness"] for b in breeders) - low) or 1.0
        key = lambda b: (-(blend * b["learned_readability"] + (1 - blend) * (b["fitness"] - low) / span),
                         b["generation_index"], b["candidate_index"])
    elif parent_selection == "fitness_weighted":
        key = lambda b: (-b["fitness"], b["generation_index"], b["candidate_index"])
    else:
        key = lambda b: (b["generation_index"], b["candidate_index"])
    return sorted(breeders, key=key)


def _termination(creatures: list[dict], generation_index: int | None, reason: str) -> dict:
    stopped = [c["breeding"]["stop"] for c in creatures if not c["breeding"]["eligible"]]
    deaths = sum(s is not None and s["reason"] == "lifecycle_death" for s in stopped)
    structural = sum(s is not None and s["reason"] in ("invalid_candidate", "invalid_repair", "unaligned_repair")
                     for s in stopped)
    ended = reason != "requested_horizon_complete"
    return {"ended": ended, "reason": reason, "generation_index": generation_index,
            "lifecycle_deaths": deaths, "structural_disqualifications": structural,
            "genuine_lifecycle_extinction": ended and deaths > 0}
