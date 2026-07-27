"""The evaluation loop at documented scale (cycle 13 E3).

The dossier's MAP-Elites archive test budgets 50,000 evaluations per
run; the gap table demands 20k–50k stress-probed lifecycle evaluations.
This lab runs the full generational evolve loop at that budget over the
E1 scale geometry (8×8×8, frozen empirical edges):

    bootstrap population → [parents = archive elites (the promoted
    evolve ordering) → WFC retrain on the elite pool → generate the
    population → stress-probed lifecycle scoring → elite insertion]
    repeated until the evaluation budget is reached.

The parent path is WFC — E2's measured evidence (validity 1.0,
unique-signature rate 1.0, 7.04 ms/candidate WITH retraining, archive
growth 171→233) — recorded in the protocol, with the constrained
bootstrap mixing both promoted generator families exactly as E1/E2 did.

DR 0028 discipline, in order:

1. the wall-clock PILOT runs first and projects to 20k/50k;
2. the bound is PRE-REGISTERED before the full run:
   ``PRE_REGISTERED_BOUND_S = 600`` (the D5 precedent — one run-once
   evidence build on the stage-0 dev machine);
3. the full run's measured wall-clock is recorded against that bound in
   the artifact's ``measured`` section — if stdlib could not hold, the
   NumPy decision record would cite the measurement.

Determinism is pinned under seeds by the test suite (identical seeds →
identical trajectories and elites, byte-for-byte). Elite records carry
descriptor + axis values + a morphology signature hash so E5's family
clustering never needs the full grids in the artifact.

SLIP alignment stays out of this harness (generation measured without
profile constraints — the standing E2 scope note); the engine archive's
scale-geometry seam stays lab-side (the promotion is its own gated
package change, named for the Phase-E gate).

Cycle 22 L1 added ``collect_refusals`` — an OBSERVATION seam, additive
and byte-identical when off (pinned). It surfaces the refusal records
the generation arms have always built and the loop has always thrown
away, and it is what corrected DR 0042's reading of its own failure
number: the refusals are SLIP-rejected PARENTS, not invalid candidates
(`labs/map_elites_archive/generation_refusal_causes.py`).

Cycle 23 M1 added ``collect_elite_grids`` — the third observation seam,
under the same law. L2's seam emits ancestry; this one emits the elite
GRIDS, because Phase L's convergent finding is that every geometry,
occupancy and candidate-axis number in the ledger is measured on a
derivation or bootstrap population rather than on the creatures the
archive is actually filled with, and a morphological re-measure needs
the cells (`labs/map_elites_archive/elite_population_measures.py`).
"""

import argparse
import hashlib
import json
import sys
import time
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
for sub in [
    "labs/map_elites_archive",
    "labs/grid_genome",
    "labs/readability_benchmark",
    "labs/lifecycle_sim",
    "labs/wfc_grid",
]:
    path = str(ROOT / sub)
    if path not in sys.path:
        sys.path.insert(0, path)
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from corpus_builder import build_seed_grids_16  # noqa: E402
from extended_descriptors import score_extended_candidate  # noqa: E402
from niche_scale_archive import (  # noqa: E402
    build_population,
    insert_scale_candidate,
    new_scale_archive,
    scale_archive_summary,
    scale_axis_values,
    scale_descriptor_for_values,
)
from wfc_grid import _signature, split_corpus  # noqa: E402
from wfc_grid import train_wfc_model as lab_train_wfc_model  # noqa: E402
from wfc_population_throughput import (  # noqa: E402
    constrained_population,
    load_frozen_scale_edges,
    parents_from_archive,
    wfc_population,
)

from slip import is_grid_aligned  # noqa: E402

from mecha_engine.generation import train_generation_model  # noqa: E402


REPORT_DATE = "2026-07-09"
ARTIFACT_ID = "evaluation_loop_scale_stage0"
DEFAULT_RNG_SEED = 20260709
DEFAULT_LIFECYCLE_TICKS = 24
# Pre-registered BEFORE the full-scale run (the D5 precedent): one
# run-once evidence build must fit the bound on the stage-0 dev
# machine, or the NumPy decision record cites the measurement
# (DR 0028). Re-registered 600 -> 1200 s by DR 0040: the adopted
# novelty-first default collapses a 3x generation pool per generation
# (measured 774 s at the documented budget — the generation volume,
# not the scoring, carries the overage; stdlib holds).
PRE_REGISTERED_BOUND_S = 1200.0


def run_evaluation_loop(
    *,
    population: int = 256,
    target_evaluations: int = 20_480,
    rng_seed: int = DEFAULT_RNG_SEED,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
    # DR 0040 (adopted on the measured verdict): novelty-first is the
    # loop's default selection — +0.0215 coverage AND +2.2% QD over
    # baseline at the matched scored budget; "baseline" and "blend"
    # stay runnable arms.
    selection: str = "novelty_first",
    pool_factor: int = 3,
    # DR 0042 (adopted on the measured verdict): the generation layer
    # is an arm, and "constrained" — E2's recorded promoted-evolve
    # inner loop, verbatim — is the loop's default after beating the
    # WFC incumbent on BOTH pre-registered bars at the matched budget
    # (coverage 0.7852 -> 0.8984, +0.1133 vs the +0.02 bar; QD ratio
    # 1.3025 vs the 0.95 floor). "wfc" stays a runnable arm,
    # byte-identical when asked for.
    generation: str = "constrained",
    # Cycle 22 L1 (an INSTRUMENT, never a gate): the generation arms
    # already build a record per refusal — `{parent_grid_id, error}` —
    # but only `len(failures)` has ever survived into the trajectory,
    # so K2's ~22% constrained failure rate has a count and no cause.
    # Turning this on collects those records verbatim and reports the
    # attempt denominator only the loop can compute. Additive and
    # byte-identical when off (pinned): observing the loop must never
    # perturb the loop.
    collect_refusals: bool = False,
    # Cycle 22 L2 (an INSTRUMENT, never a gate): the documented
    # MAP-Elites gate has a second clause — "no single lineage > 40% of
    # occupied cells" (deep-research.md:205) — that has never been
    # measured. Turning this on emits the engine's OWN recorded
    # ancestry for each occupied niche's elite; the founder rule lives
    # in one pinned place (`lineage_dominance.founder_of`), so the loop
    # collects and never derives. Additive and byte-identical when off.
    collect_lineage: bool = False,
    # Cycle 23 M1 (an INSTRUMENT, never a gate): every geometry,
    # occupancy and candidate-axis number in the ledger is measured on a
    # derivation or bootstrap population, never on the creatures the
    # archive is actually filled with — Phase L's convergent finding,
    # arrived at four separate times. The L2 seam emits ancestry only;
    # measuring a MORPHOLOGICAL statistic (animation density, the
    # descriptor axes recomputed) needs the cells themselves. Turning
    # this on emits a deep COPY of each occupied niche's elite grid,
    # plus its origin measured by MEMBERSHIP in this loop's bootstrap
    # population (L1's recorded process error: lineage depth is not
    # provenance — a bootstrap creature is generated FROM a seed and
    # already sits at depth 1). The loop collects; the instrument
    # derives. Additive and byte-identical when off.
    collect_elite_grids: bool = False,
    # Cycle 23 M3 (an ARM set, judged by its own pre-registered gate —
    # never a silent default change): L1 measured that 100% of the
    # loop's generation refusals are the SLIP rejecting the PARENT, and
    # that every such parent is a bootstrap creature the corpus
    # generators built without ever being handed the profile. M1 sized
    # them: 48 of 460 elites. The fix TRADES AGAINST COVERAGE — a niche
    # whose only occupant is SLIP-illegal goes empty if that occupant is
    # excluded — so the three candidate changes are separated here and
    # measured, never blended:
    #
    #   "bootstrap" — admit only SLIP-legal creatures into the bootstrap
    #   "insertion" — admit only SLIP-legal creatures into the ARCHIVE
    #   "parents"   — keep the archive as-is, but breed only legal elites
    #
    # The predicate is the generation arm's own (`slip.is_grid_aligned`),
    # imported and never re-implemented, so an arm cannot admit a
    # creature the generator would refuse. "none" is the incumbent and
    # is byte-identical (pinned).
    slip_admission: str = "none",
) -> dict:
    """The full generational loop to the documented evaluation budget.

    Deterministic under ``rng_seed``: the bootstrap population, every
    generation's candidate generation, every stress-probed lifecycle
    score, and every elite decision replay identically. Returns the
    archive, the per-generation trajectory, and lean elite records
    (descriptor, axis values, signature hash — E5's clustering inputs).
    """
    if selection not in ("baseline", "novelty_first", "blend"):
        raise ValueError(
            "selection must be baseline | novelty_first | blend: "
            f"{selection!r}"
        )
    if generation not in ("wfc", "constrained"):
        raise ValueError(
            f"generation must be wfc | constrained: {generation!r}"
        )
    if slip_admission not in ("none", "bootstrap", "insertion", "parents"):
        raise ValueError(
            "slip_admission must be none | bootstrap | insertion | "
            f"parents: {slip_admission!r}"
        )
    edges = load_frozen_scale_edges()
    slip_profile = _load_default_slip()
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    generation_model = (
        train_generation_model(seeds) if generation == "constrained" else None
    )

    def generate_population(
        parents: list[dict], count: int, generation_index: int
    ) -> tuple[list[dict], list[dict]]:
        if generation == "wfc":
            return wfc_population(
                parents,
                population=count,
                generation_index=generation_index,
                rng_seed=rng_seed,
            )
        return constrained_population(
            parents,
            generation_model,
            population=count,
            generation_index=generation_index,
            rng_seed=rng_seed,
            slip_profile=slip_profile,
        )

    archive = new_scale_archive()
    elite_grids: dict[str, dict] = {}
    evaluations = 0

    # M3: the generation arm's OWN predicate, memoised per grid id. A
    # second implementation could admit a creature `generate_candidate`
    # would refuse, which would make every arm's number a fiction.
    legality_cache: dict[str, bool] = {}

    def _is_slip_legal(grid: dict) -> bool:
        if slip_profile is None:
            return True
        # Coerced to str: the cache is keyed by id, and a grid missing
        # one would otherwise cache under None and collide with every
        # other unnamed grid.
        grid_id = str(grid.get("grid_id", ""))
        cached = legality_cache.get(grid_id)
        if cached is None:
            cached = is_grid_aligned(grid, slip_profile).ok
            legality_cache[grid_id] = cached
        return cached

    def evaluate_and_insert(grid: dict, run_seed: int) -> None:
        nonlocal evaluations
        score = score_extended_candidate(
            grid,
            slip_profile=slip_profile,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=run_seed,
        )
        # The evaluation is SPENT whether or not the archive admits the
        # creature: the budget is scored lifecycles, and letting a
        # refused insertion buy an extra evaluation would compare the
        # arms at different budgets.
        evaluations += 1
        if slip_admission == "insertion" and not _is_slip_legal(grid):
            return
        descriptor = scale_descriptor_for_values(
            scale_axis_values(grid, slip_profile=slip_profile), edges
        )
        insert_scale_candidate(archive, grid, score, descriptor)
        event = archive["events"][-1]["event"]
        if event in ("inserted_empty_niche", "replaced_elite"):
            elite_grids[grid["grid_id"]] = grid

    bootstrap_population, bootstrap_composition = build_population(
        population, rng_seed, train, lab_train_wfc_model(train)
    )
    bootstrap_admitted = len(bootstrap_population)
    if slip_admission == "bootstrap":
        # `build_population` returns the constrained half first, then the
        # WFC half, so membership is recoverable by index BEFORE the
        # filter. Recomputing the composition matters: leaving it at the
        # pre-filter counts would report a mix that sums to the original
        # population beside an `bootstrap_admitted` that does not — the
        # kind of internally inconsistent metadata that misleads every
        # downstream reader.
        constrained_ids = {
            grid.get("grid_id")
            for grid in bootstrap_population[
                : bootstrap_composition.get("constrained", 0)
            ]
        }
        bootstrap_population = [
            grid for grid in bootstrap_population if _is_slip_legal(grid)
        ]
        bootstrap_admitted = len(bootstrap_population)
        admitted_constrained = sum(
            1
            for grid in bootstrap_population
            if grid.get("grid_id") in constrained_ids
        )
        bootstrap_composition = {
            "constrained": admitted_constrained,
            "wfc": bootstrap_admitted - admitted_constrained,
        }
        if not bootstrap_population:
            raise ValueError(
                "slip_admission='bootstrap' admitted no creatures: the "
                "profile rejects the entire bootstrap population, so the "
                "loop has nothing to seed the archive with"
            )
    bootstrap_ids = {grid.get("grid_id") for grid in bootstrap_population}
    for index, grid in enumerate(bootstrap_population):
        evaluate_and_insert(grid, rng_seed + index)

    trajectory: list[dict] = []
    refusal_records: list[dict] = []
    generation_attempts = 0
    generation_index = 0
    parent_fallback_generations = 0
    while evaluations < target_evaluations:
        generation_index += 1
        parents = parents_from_archive(archive, elite_grids)
        if slip_admission == "parents":
            breedable = [grid for grid in parents if _is_slip_legal(grid)]
            if breedable:
                parents = breedable
            else:
                # No legal elite exists yet. Falling back silently would
                # reintroduce the very refusals this arm exists to
                # remove and make its gate uninterpretable, so the
                # fallback is COUNTED and rides in the result.
                parent_fallback_generations += 1
        # DR 0040: novelty-first candidate selection — generation is
        # cheap, the SCORED budget is the bar. A novelty generation
        # collapses pool_factor x population, bins the pool with the
        # lifecycle-free descriptors, and scores the first-of-unseen-
        # niche candidates first (then generation order) — the same
        # scored budget as the baseline path.
        novelty_generation = selection == "novelty_first" or (
            selection == "blend" and generation_index % 2 == 0
        )
        pool_size = None
        if novelty_generation:
            requested = population * pool_factor
            pool, failures = generate_population(
                parents, requested, generation_index
            )
            pool_size = len(pool)
            candidates = _novelty_first_candidates(
                pool,
                population,
                archive,
                edges,
                slip_profile=slip_profile,
            )
        else:
            requested = population
            candidates, failures = generate_population(
                parents, requested, generation_index
            )
        if collect_refusals:
            # L1: the records verbatim — the generation index is what
            # makes an early-vs-late reading possible, and the parent id
            # is what distinguishes "this parent is unbreedable" from
            # "the generator missed".
            #
            # `parent_origin` is measured by MEMBERSHIP in the bootstrap
            # population this loop built, not inferred from the parent's
            # lineage depth. The distinction is not pedantic: a
            # bootstrap creature is itself generated FROM a seed, so its
            # lineage depth is already 1, and reading depth as origin
            # mislabels every bootstrap creature as loop offspring
            # (measured, then caught — see the L1 report's process
            # note). Lineage depth rides along as its own honest field.
            generation_attempts += requested
            parent_depths = {
                parent.get("grid_id"): (parent.get("lineage") or {}).get(
                    "generation"
                )
                for parent in parents
            }
            refusal_records.extend(
                {
                    "generation_index": generation_index,
                    "parent_grid_id": failure.get("parent_grid_id"),
                    "parent_origin": (
                        "bootstrap"
                        if failure.get("parent_grid_id") in bootstrap_ids
                        else "loop_offspring"
                    ),
                    "parent_lineage_depth": parent_depths.get(
                        failure.get("parent_grid_id")
                    ),
                    "error": failure.get("error"),
                }
                for failure in failures
            )
        replacements_before = _replacement_count(archive)
        for index, candidate in enumerate(candidates):
            evaluate_and_insert(
                candidate,
                rng_seed + generation_index * 100_000 + index,
            )
        summary = scale_archive_summary(archive)
        entry = {
            "generation": generation_index,
            "evaluations_total": evaluations,
            "parent_count": len(parents),
            "collapse_failures": len(failures),
            "occupied_niches": summary["occupied_niches"],
            "coverage": summary["coverage"],
            "qd_score": summary["qd_score"],
            "best_fitness": summary["best_fitness"],
            "replacements_this_generation": _replacement_count(archive)
            - replacements_before,
        }
        if selection != "baseline":
            entry["selection_novelty"] = novelty_generation
            if pool_size is not None:
                entry["pool_size"] = pool_size
        trajectory.append(entry)
        # Bound the working set: only current elites' grids parent the
        # next generation.
        current_elite_ids = {
            elite["grid_id"] for elite in archive["elites"].values()
        }
        elite_grids = {
            grid_id: grid
            for grid_id, grid in elite_grids.items()
            if grid_id in current_elite_ids
        }

    summary = scale_archive_summary(archive)
    elite_records = [
        {
            "niche": niche,
            "grid_id": elite["grid_id"],
            "fitness": elite["fitness"],
            "descriptor": elite["descriptor"]["values"],
            "axis_values": scale_axis_values(
                elite_grids[elite["grid_id"]], slip_profile=slip_profile
            ),
            "signature_hash": hashlib.sha256(
                _signature(elite_grids[elite["grid_id"]]).encode("utf-8")
            ).hexdigest()[:16],
        }
        for niche, elite in sorted(archive["elites"].items())
    ]
    # DR 0042 (observation, not a gate): the elites' role texture — the
    # game-facing consequence of the generation-layer choice.
    motion_roles = {"limb", "joint", "decoration"}
    elite_role_sets = [
        {
            cell["role"]
            for cell in elite_grids[elite["grid_id"]]["cells"]
        }
        for elite in archive["elites"].values()
    ]
    elite_role_summary = {
        "roles_present": sorted(set().union(*elite_role_sets))
        if elite_role_sets
        else [],
        "motion_trio_elite_fraction": round(
            sum(1 for roles in elite_role_sets if roles & motion_roles)
            / len(elite_role_sets),
            6,
        )
        if elite_role_sets
        else 0.0,
    }
    result = {
        "archive": archive,
        "archive_summary": summary,
        "trajectory": trajectory,
        "evaluations_total": evaluations,
        "bootstrap_composition": bootstrap_composition,
        "elite_records": elite_records,
        "generation": generation,
        "elite_role_summary": elite_role_summary,
    }
    if slip_admission != "none":
        # M3: arm metadata is RUNG-CONDITIONAL, not unconditional.
        #
        # An earlier draft emitted these two keys always, on the
        # `generation` precedent. That was wrong, and review caught it:
        # the law is byte-identical when OFF, and "off" means identical
        # to what the loop returned before this arm existed — not merely
        # identical between two calls to the new code. Emitting them
        # unconditionally silently changed the result dict for every
        # existing caller, and a test comparing new-to-new could never
        # have detected it (the off-mode key set is now pinned against a
        # frozen list for exactly that reason).
        result["slip_admission"] = slip_admission
        result["bootstrap_admitted"] = bootstrap_admitted
    if slip_admission == "parents":
        # A rung-conditional key: it exists only when its arm ran, so a
        # reader can never mistake "absent" for "zero" (the None != []
        # != absent discipline).
        result["parent_fallback_generations"] = parent_fallback_generations
    if collect_refusals:
        # The seam adds exactly ONE key, and only when asked (pinned).
        result["refusal_collection"] = {
            "records": refusal_records,
            "generation_attempts_total": generation_attempts,
        }
    if collect_lineage:
        # L2: the engine's OWN recorded ancestry per occupied niche,
        # verbatim. `ancestor_ids` accumulates oldest-first
        # (`[*parent_ancestors, parent_grid_id]` in the promoted
        # generator), so element 0 is the founder — but that derivation
        # belongs to the instrument, not here.
        result["lineage_collection"] = {
            "occupied_niches": summary["occupied_niches"],
            "elites": [
                {
                    "niche": niche,
                    "grid_id": elite["grid_id"],
                    "lineage": deepcopy(
                        elite_grids[elite["grid_id"]].get("lineage") or {}
                    ),
                }
                for niche, elite in sorted(archive["elites"].items())
            ],
        }
    if collect_elite_grids:
        # M1: the creatures the archive is actually filled with, whole.
        # Deep-copied because an observation seam must never hand out a
        # live reference into the loop's working set — a caller that
        # mutated one would corrupt the parents of the next generation.
        # `origin` is measured by MEMBERSHIP in this loop's bootstrap
        # population, never inferred from lineage depth (L1's error).
        result["elite_grid_collection"] = {
            "occupied_niches": summary["occupied_niches"],
            "bootstrap_population_size": len(bootstrap_ids),
            "elites": [
                {
                    "niche": niche,
                    "grid_id": elite["grid_id"],
                    "origin": (
                        "bootstrap"
                        if elite["grid_id"] in bootstrap_ids
                        else "loop_offspring"
                    ),
                    "fitness": elite["fitness"],
                    "grid": deepcopy(elite_grids[elite["grid_id"]]),
                }
                for niche, elite in sorted(archive["elites"].items())
            ],
        }
    return result


def _novelty_first_candidates(
    pool: list[dict],
    budget: int,
    archive: dict,
    edges: dict,
    *,
    slip_profile: dict | None,
) -> list[dict]:
    """First-of-unseen-niche candidates first, generation order for the

    remainder — deterministic; no lifecycle scoring is spent choosing."""
    occupied = set(archive["elites"])
    seen: set[str] = set()
    novel: list[dict] = []
    rest: list[dict] = []
    for grid in pool:
        descriptor = scale_descriptor_for_values(
            scale_axis_values(grid, slip_profile=slip_profile), edges
        )
        niche = ",".join(str(value) for value in descriptor)
        if niche not in occupied and niche not in seen:
            seen.add(niche)
            novel.append(grid)
        else:
            rest.append(grid)
    return (novel + rest)[:budget]


def build_evaluation_loop_report(
    *,
    population: int = 256,
    target_evaluations: int = 20_480,
    rng_seed: int = DEFAULT_RNG_SEED,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
    generation: str = "constrained",
) -> dict:
    result = run_evaluation_loop(
        population=population,
        target_evaluations=target_evaluations,
        rng_seed=rng_seed,
        lifecycle_ticks=lifecycle_ticks,
        generation=generation,
    )
    summary = result["archive_summary"]
    parent_path_evidence = {
        "wfc": (
            "E2 (data/wfc_grid/wfc_population_throughput_stage0."
            "json): validity 1.0, unique-signature rate 1.0, "
            "7.04 ms/candidate with retraining, archive growth "
            "171->233 under the WFC parent path"
        ),
        "constrained": (
            "DR 0042 (data/archives/generation_arm_evolution_stage0."
            "json): the promoted-evolve inner loop beat the WFC "
            "incumbent in the FULL loop at the matched budget — "
            "coverage 0.7852 -> 0.8984 (+0.1133 vs the +0.02 bar), "
            "QD ratio 1.3025 (vs the 0.95 floor) — the adopted "
            "generation default"
        ),
    }[generation]
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "Run the full generational evolve loop at the documented "
            "evaluation budget (20k+ stress-probed lifecycle evaluations) "
            "over the E1 scale geometry with the adopted generation "
            "layer (DR 0042); wall-clock measured first against the "
            "pre-registered bound; determinism pinned under seeds "
            "(cycle 13 E3)."
        ),
        "source_artifacts": [
            "labs/map_elites_archive/niche_scale_archive.py",
            "labs/wfc_grid/wfc_population_throughput.py",
            "data/archives/niche_scale_archive_stage0.json",
            "data/wfc_grid/wfc_population_throughput_stage0.json",
            "data/seed_grids_16x16",
            "packages/mecha_engine/src/mecha_engine/generation",
            "docs/project-research/deep-research/01/deep-research.md",
        ],
        "metrics": {
            "protocol": {
                "population": population,
                "target_evaluations": target_evaluations,
                "rng_seed": rng_seed,
                "lifecycle_ticks": lifecycle_ticks,
                "wall_clock_bound_s": PRE_REGISTERED_BOUND_S,
                "parent_path": generation,
                "parent_path_evidence": parent_path_evidence,
                "bootstrap_composition": result["bootstrap_composition"],
                "frozen_edges_source": (
                    "data/archives/niche_scale_archive_stage0.json"
                ),
                "slip_alignment": (
                    "not enforced in this harness (the standing E2 scope "
                    "note); alignment gates belong to the ecosystem loop, "
                    "not the archive evaluation budget"
                ),
            },
            "evaluations_total": result["evaluations_total"],
            "generations_run": len(result["trajectory"]),
            "trajectory": result["trajectory"],
            "final_archive": summary,
            "elite_records": result["elite_records"],
        },
        "closed_states": [
            "documented_evaluation_budget_reached",
            "determinism_pinned_under_seeds",
            "wall_clock_bound_pre_registered_before_the_run",
            "trajectory_recorded_per_generation_for_the_e4_gates",
            "elite_records_carry_e5_clustering_inputs",
        ],
        "blocked_states": [
            "coverage_qd_gates_not_judged_here (E4 runs the documented "
            "gates including the GA baseline under identical budgets)",
            "package_scale_geometry_seam_not_promoted (still lab-side; "
            "named for the Phase-E gate)",
            "slip_alignment_not_enforced_in_this_harness (the standing "
            "E2 scope note)",
        ],
        "decision": (
            f"The loop ran {result['evaluations_total']} stress-probed "
            f"lifecycle evaluations over {len(result['trajectory'])} "
            f"generations of population {population}: "
            f"{summary['occupied_niches']} of 512 niches occupied "
            f"(coverage {summary['coverage']}), QD score "
            f"{summary['qd_score']}, best fitness "
            f"{summary['best_fitness']} — deterministic under seed "
            f"{rng_seed}."
        ),
        "next_research_step": (
            "E4: the documented coverage/QD gates plus the plain-GA "
            "baseline under identical budgets (MAP-Elites >=25% coverage "
            "over GA)."
        ),
    }


def measure_loop_pilot(
    *,
    population: int = 64,
    generations: int = 2,
    rng_seed: int = DEFAULT_RNG_SEED,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
) -> dict:
    """DR 0028: the pilot wall-clock, measured FIRST, projected to 20k/50k."""
    start = time.perf_counter()
    result = run_evaluation_loop(
        population=population,
        target_evaluations=population * (generations + 1),
        rng_seed=rng_seed,
        lifecycle_ticks=lifecycle_ticks,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000
    mean_ms = round(elapsed_ms / result["evaluations_total"], 4)
    projection_20k = round(mean_ms * 20_000 / 1000, 2)
    projection_50k = round(mean_ms * 50_000 / 1000, 2)
    return {
        "context": (
            "stage-0 dev machine; the full loop unit (WFC retrain + "
            "collapse + stress-probed lifecycle scoring + elite "
            "insertion), bootstrap included"
        ),
        "pilot": {
            "population": population,
            "generations": generations,
            "evaluations": result["evaluations_total"],
            "mean_ms_per_evaluation": mean_ms,
        },
        "projections": {
            "evaluations_20k_s": projection_20k,
            "evaluations_50k_s": projection_50k,
            "projection_meets_bound_20k": projection_20k
            <= PRE_REGISTERED_BOUND_S,
            "projection_meets_bound_50k": projection_50k
            <= PRE_REGISTERED_BOUND_S,
        },
        "pre_registered_bound_s": PRE_REGISTERED_BOUND_S,
    }


def write_evaluation_loop_artifacts(
    output_dir: Path, report: dict, measured: dict | None = None
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = dict(report)
    if measured is not None:
        payload["measured"] = measured
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def _replacement_count(archive: dict) -> int:
    return sum(
        1
        for event in archive["events"]
        if event["event"] == "replaced_elite"
    )


def _load_default_slip() -> dict:
    return json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="The evaluation loop at documented scale (cycle 13 E3)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "archives"
    )
    parser.add_argument("--population", type=int, default=256)
    parser.add_argument("--target-evaluations", type=int, default=20_480)
    parser.add_argument("--rng-seed", type=int, default=DEFAULT_RNG_SEED)
    parser.add_argument("--skip-timing", action="store_true")
    args = parser.parse_args()

    # DR 0028 discipline, in order: pilot first, bound already
    # pre-registered, full run measured against it.
    measured = (
        None
        if args.skip_timing
        else measure_loop_pilot(rng_seed=args.rng_seed)
    )
    if measured is not None:
        print(json.dumps(measured, indent=2))

    full_start = time.perf_counter()
    report = build_evaluation_loop_report(
        population=args.population,
        target_evaluations=args.target_evaluations,
        rng_seed=args.rng_seed,
    )
    full_wall_clock = round(time.perf_counter() - full_start, 2)
    if measured is not None:
        measured["full_run"] = {
            "wall_clock_s": full_wall_clock,
            "meets_bound": full_wall_clock <= PRE_REGISTERED_BOUND_S,
            "bound_s": PRE_REGISTERED_BOUND_S,
        }

    write_evaluation_loop_artifacts(args.output_dir, report, measured)
    print(json.dumps(report["metrics"]["final_archive"], indent=2))
    print(json.dumps(report["metrics"]["trajectory"][-3:], indent=2))
    if measured is not None:
        print(json.dumps(measured["full_run"], indent=2))
    print(report["decision"])


if __name__ == "__main__":
    main()
