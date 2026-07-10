"""WFC generation throughput at population scale (cycle 13 E2).

The gap table's evolution row demands populations ~256 per generation;
the dossier's generation gate demands <=250 ms per candidate at 16x16.
This lab runs the ENGINE's own promoted generation surfaces
(``mecha_engine.generation``) at that scale, with parents drawn from
archive elites PER THE PROMOTED EVOLVE SEMANTICS — the default branch of
``runtime.evolve``: ``parents = [elites[niche]["grid"] for niche in
sorted(elites)]``, candidates seeded ``rng_seed + generation * 100000 +
index``, the constrained arm round-robining ``parents[index %
len(parents)]``.

Two arms from the SAME parents each generation, because the standing
remainder (cycle 10, DR 0031) left evolve's inner loop on the
constrained path pending its own evidence:

- **wfc** — the adopted generation layer as the parent path: the WFC
  model is retrained on the current elite pool each generation (the WFC
  reading of "parents from archive elites"), then collapsed
  per-candidate. Wave contradictions are recorded as failures, never
  hidden.
- **constrained** — the promoted inner-loop path verbatim:
  ``generate_candidate(parent, model, ...)`` with the evolve seed
  scheme (the generation model trained once from the seed corpus,
  exactly as evolve receives it).

The archive between generations is refreshed by the WFC arm (the path
under test); descriptors bin with E1's FROZEN empirically derived octile
edges (`data/archives/niche_scale_archive_stage0.json`), and fitness is
the calibrated Stage 0 scoring — the same surfaces E1 proved at
hundreds of niches.

SLIP alignment is deliberately NOT enforced in this harness (generation
is measured without profile constraints; E3's full loop owns the
alignment gates) — recorded in the protocol and blocked states.

Wall-clock stays out of the deterministic report body: the ``measured``
section times both arms per candidate against the documented 250 ms
bar, counting the WFC arm's per-generation model retraining honestly
(it is part of that path's cost) while the constrained arm's one-time
seed-corpus training is excluded (evolve trains it once, outside the
loop).
"""

import argparse
import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
for sub in [
    "labs/wfc_grid",
    "labs/grid_genome",
    "labs/readability_benchmark",
    "labs/lifecycle_sim",
    "labs/map_elites_archive",
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
from validator import validate_grid  # noqa: E402
from wfc_grid import _signature, split_corpus  # noqa: E402
from wfc_grid import train_wfc_model as lab_train_wfc_model  # noqa: E402

from mecha_engine.generation import (  # noqa: E402
    generate_candidate,
    generate_wfc_grid,
    train_generation_model,
    train_wfc_model,
)


REPORT_DATE = "2026-07-09"
ARTIFACT_ID = "wfc_population_throughput_stage0"
DEFAULT_RNG_SEED = 20260709
DEFAULT_LIFECYCLE_TICKS = 24
TIME_BAR_MS = 250.0
# The evolve per-candidate seed scheme, verbatim.
GENERATION_SEED_STRIDE = 100_000

_E1_ARTIFACT = ROOT / "data" / "archives" / "niche_scale_archive_stage0.json"


def load_frozen_scale_edges() -> dict[str, list[float]]:
    """E1's empirically derived octile edges — the standing calibration."""
    artifact = json.loads(_E1_ARTIFACT.read_text(encoding="utf-8"))
    return artifact["metrics"]["edge_derivation"]["edges"]


def parents_from_archive(archive: dict, grids_by_id: dict) -> list[dict]:
    """runtime.evolve's default parent branch: elites in sorted(niche) order."""
    return [
        grids_by_id[archive["elites"][niche]["grid_id"]]
        for niche in sorted(archive["elites"])
    ]


def wfc_population(
    parents: list[dict],
    *,
    population: int,
    generation_index: int,
    rng_seed: int,
) -> tuple[list[dict], list[dict]]:
    """The WFC parent path: retrain on the elite pool, collapse per child.

    Returns ``(candidates, failures)`` — a wave contradiction after the
    generator's bounded restarts is a recorded failure, never a crash.
    """
    model = train_wfc_model(parents)
    candidates: list[dict] = []
    failures: list[dict] = []
    for index in range(population):
        grid_id = f"mg_e2w_g{generation_index}_{index:03d}"
        run_seed = rng_seed + generation_index * GENERATION_SEED_STRIDE + index
        try:
            candidates.append(
                generate_wfc_grid(model, grid_id=grid_id, rng_seed=run_seed)
            )
        except ValueError as error:
            failures.append({"grid_id": grid_id, "error": str(error)})
    return candidates, failures


def constrained_population(
    parents: list[dict],
    generation_model,
    *,
    population: int,
    generation_index: int,
    rng_seed: int,
    slip_profile: dict | None = None,
) -> tuple[list[dict], list[dict]]:
    """The promoted evolve inner loop, verbatim: round-robin + seed scheme."""
    candidates: list[dict] = []
    failures: list[dict] = []
    for index in range(population):
        parent = parents[index % len(parents)]
        run_seed = rng_seed + generation_index * GENERATION_SEED_STRIDE + index
        try:
            candidates.append(
                generate_candidate(
                    parent, generation_model, slip_profile, rng_seed=run_seed
                )
            )
        except ValueError as error:
            failures.append(
                {"parent_grid_id": parent.get("grid_id"), "error": str(error)}
            )
    return candidates, failures


def arm_metrics(
    candidates: list[dict], parents: list[dict], edges: dict[str, list[float]]
) -> dict:
    """Validity, uniqueness, parent-novelty, and descriptor spread."""
    produced = len(candidates)
    if not produced:
        return {
            "produced": 0,
            "validity_rate": 0.0,
            "unique_signature_rate": 0.0,
            "parent_copy_rate": 0.0,
            "unique_scale_descriptors": 0,
        }
    signatures = [_signature(candidate) for candidate in candidates]
    parent_signatures = {_signature(parent) for parent in parents}
    descriptors = {
        scale_descriptor_for_values(scale_axis_values(candidate), edges)
        for candidate in candidates
    }
    return {
        "produced": produced,
        "validity_rate": round(
            sum(1 for candidate in candidates if validate_grid(candidate).ok)
            / produced,
            6,
        ),
        "unique_signature_rate": round(len(set(signatures)) / produced, 6),
        "parent_copy_rate": round(
            sum(1 for signature in signatures if signature in parent_signatures)
            / produced,
            6,
        ),
        "unique_scale_descriptors": len(descriptors),
    }


def build_population_throughput_report(
    *,
    initial_count: int = 400,
    population: int = 256,
    generations: int = 3,
    rng_seed: int = DEFAULT_RNG_SEED,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
) -> dict:
    edges = load_frozen_scale_edges()
    slip_profile = _load_default_slip()
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    generation_model = train_generation_model(seeds)

    # The initial archive: E1's proven surfaces over a mixed population.
    initial_population, initial_composition = build_population(
        initial_count, rng_seed, train, lab_train_wfc_model(train)
    )
    grids_by_id = {grid["grid_id"]: grid for grid in initial_population}
    archive = new_scale_archive()
    for index, grid in enumerate(initial_population):
        score = score_extended_candidate(
            grid,
            slip_profile=slip_profile,
            lifecycle_ticks=lifecycle_ticks,
            rng_seed=rng_seed + index,
        )
        descriptor = scale_descriptor_for_values(
            scale_axis_values(grid, slip_profile=slip_profile), edges
        )
        insert_scale_candidate(archive, grid, score, descriptor)
    initial_summary = scale_archive_summary(archive)

    generation_entries: list[dict] = []
    for generation_index in range(1, generations + 1):
        parents = parents_from_archive(archive, grids_by_id)
        wfc_candidates, wfc_failures = wfc_population(
            parents,
            population=population,
            generation_index=generation_index,
            rng_seed=rng_seed,
        )
        constrained_candidates, constrained_failures = constrained_population(
            parents,
            generation_model,
            population=population,
            generation_index=generation_index,
            rng_seed=rng_seed,
        )
        entry = {
            "generation": generation_index,
            "population": population,
            "parent_count": len(parents),
            "arms": {
                "wfc": {
                    **arm_metrics(wfc_candidates, parents, edges),
                    "collapse_failures": len(wfc_failures),
                },
                "constrained": {
                    **arm_metrics(constrained_candidates, parents, edges),
                    "generation_failures": len(constrained_failures),
                },
            },
        }
        generation_entries.append(entry)

        # The WFC parent path refreshes the archive (the path under test);
        # the constrained arm is the measured comparator, never inserted.
        for index, candidate in enumerate(wfc_candidates):
            score = score_extended_candidate(
                candidate,
                slip_profile=slip_profile,
                lifecycle_ticks=lifecycle_ticks,
                rng_seed=rng_seed
                + generation_index * GENERATION_SEED_STRIDE
                + index,
            )
            descriptor = scale_descriptor_for_values(
                scale_axis_values(candidate, slip_profile=slip_profile), edges
            )
            insert_scale_candidate(archive, candidate, score, descriptor)
            grids_by_id[candidate["grid_id"]] = candidate

    final_summary = scale_archive_summary(archive)
    aggregate = {
        arm: {
            "validity_rate_mean": round(
                sum(entry["arms"][arm]["validity_rate"] for entry in generation_entries)
                / len(generation_entries),
                6,
            ),
            "unique_signature_rate_mean": round(
                sum(
                    entry["arms"][arm]["unique_signature_rate"]
                    for entry in generation_entries
                )
                / len(generation_entries),
                6,
            ),
            "unique_scale_descriptors_total": sum(
                entry["arms"][arm]["unique_scale_descriptors"]
                for entry in generation_entries
            ),
        }
        for arm in ("wfc", "constrained")
    }

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "Measure the engine's promoted generation surfaces at the "
            "documented population scale (hundreds per generation), parents "
            "drawn from archive elites per the promoted evolve semantics — "
            "the WFC parent path vs the constrained inner-loop path from "
            "the SAME parents (cycle 13 E2; the DR 0031 standing remainder's "
            "evidence)."
        ),
        "source_artifacts": [
            "packages/mecha_engine/src/mecha_engine/generation",
            "packages/mecha_engine/src/mecha_engine/runtime/evolve.py",
            "labs/map_elites_archive/niche_scale_archive.py",
            "data/archives/niche_scale_archive_stage0.json",
            "data/seed_grids_16x16",
            "docs/project-research/deep-research/01/deep-research.md",
        ],
        "metrics": {
            "protocol": {
                "initial_count": initial_count,
                "population": population,
                "generations": generations,
                "rng_seed": rng_seed,
                "lifecycle_ticks": lifecycle_ticks,
                "archive_refresh_arm": "wfc",
                "parent_semantics": (
                    "runtime.evolve default branch: elites' grids in "
                    "sorted(niche) order; constrained arm round-robins "
                    "parents[index % len(parents)]; per-candidate seed "
                    "rng_seed + generation * 100000 + index"
                ),
                "slip_alignment": (
                    "not enforced in this harness — generation measured "
                    "without profile constraints; E3's full loop owns the "
                    "alignment gates"
                ),
                "initial_composition": initial_composition,
                "frozen_edges_source": (
                    "data/archives/niche_scale_archive_stage0.json"
                ),
            },
            "initial_archive": initial_summary,
            "generations": generation_entries,
            "aggregate": aggregate,
            "final_archive": final_summary,
        },
        "closed_states": [
            "promoted_surfaces_measured_at_population_scale",
            "parents_drawn_from_archive_elites_per_evolve_semantics",
            "both_arms_measured_from_shared_parents",
            "wfc_collapse_failures_recorded_never_hidden",
        ],
        "blocked_states": [
            "throughput_gate_judged_on_the_measured_section "
            "(machine-dependent; produced alongside the artifact)",
            "slip_alignment_not_enforced_in_this_harness "
            "(E3's full loop owns the alignment gates)",
            "evolve_inner_loop_adoption_pending "
            "(the constrained-vs-WFC parent-path evidence recorded here "
            "feeds E3/a decision record; the promoted evolve is untouched)",
        ],
        "decision": (
            "Measured at population "
            f"{population} x {generations} generations from "
            f"{initial_summary['occupied_niches']}-elite parents: WFC "
            f"validity {aggregate['wfc']['validity_rate_mean']}, unique-"
            f"signature rate {aggregate['wfc']['unique_signature_rate_mean']} "
            f"vs constrained validity "
            f"{aggregate['constrained']['validity_rate_mean']}, unique-"
            f"signature rate "
            f"{aggregate['constrained']['unique_signature_rate_mean']}; the "
            f"archive grew from {initial_summary['occupied_niches']} to "
            f"{final_summary['occupied_niches']} occupied niches under the "
            "WFC parent path."
        ),
        "next_research_step": (
            "E3: the full evolve loop at 20k+ stress-probed lifecycle "
            "evaluations, wall-clock first (DR 0028), determinism pinned "
            "under seeds."
        ),
    }


def measure_population_throughput(
    *, population: int = 256, rng_seed: int = DEFAULT_RNG_SEED
) -> dict:
    """Machine-dependent per-candidate wall-clock vs the 250 ms bar.

    The WFC arm's per-generation model retraining is COUNTED (it is part
    of that parent path's per-generation cost); the constrained arm's
    one-time seed-corpus training is excluded (evolve trains it once,
    outside the loop).
    """
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    generation_model = train_generation_model(seeds)

    wfc_start = time.perf_counter()
    wfc_model = train_wfc_model(train)
    train_ms = (time.perf_counter() - wfc_start) * 1000
    produced = 0
    for index in range(population):
        try:
            generate_wfc_grid(
                wfc_model,
                grid_id=f"mg_e2t_w_{index:03d}",
                rng_seed=rng_seed + index,
            )
            produced += 1
        except ValueError:
            pass
    wfc_ms = (time.perf_counter() - wfc_start) * 1000

    constrained_start = time.perf_counter()
    for index in range(population):
        generate_candidate(
            train[index % len(train)],
            generation_model,
            None,
            rng_seed=rng_seed + index,
        )
    constrained_ms = (time.perf_counter() - constrained_start) * 1000

    wfc_mean = round(wfc_ms / population, 4)
    constrained_mean = round(constrained_ms / population, 4)
    return {
        "context": (
            "stage-0 dev machine; parents = the 16x16 train split; the WFC "
            "mean includes that generation's model retraining (the parent "
            "path's real per-generation cost); the constrained mean "
            "excludes the one-time seed-corpus model training"
        ),
        "population": population,
        "arms": {
            "wfc": {
                "mean_ms_per_candidate": wfc_mean,
                "model_train_ms": round(train_ms, 2),
                "produced": produced,
                "meets_time_bar": wfc_mean <= TIME_BAR_MS,
            },
            "constrained": {
                "mean_ms_per_candidate": constrained_mean,
                "meets_time_bar": constrained_mean <= TIME_BAR_MS,
            },
        },
        "time_bar_ms": TIME_BAR_MS,
    }


def write_population_throughput_artifacts(
    output_dir: Path, report: dict, measured: dict | None = None
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = dict(report)
    if measured is not None:
        payload["measured"] = measured
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def _load_default_slip() -> dict:
    return json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="WFC generation throughput at population scale (cycle 13 E2)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "wfc_grid"
    )
    parser.add_argument("--initial-count", type=int, default=400)
    parser.add_argument("--population", type=int, default=256)
    parser.add_argument("--generations", type=int, default=3)
    parser.add_argument("--rng-seed", type=int, default=DEFAULT_RNG_SEED)
    parser.add_argument("--skip-timing", action="store_true")
    args = parser.parse_args()

    # DR 0028 discipline: wall-clock measured FIRST.
    measured = (
        None
        if args.skip_timing
        else measure_population_throughput(
            population=args.population, rng_seed=args.rng_seed
        )
    )
    if measured is not None:
        print(json.dumps(measured, indent=2))

    report = build_population_throughput_report(
        initial_count=args.initial_count,
        population=args.population,
        generations=args.generations,
        rng_seed=args.rng_seed,
    )
    write_population_throughput_artifacts(args.output_dir, report, measured)
    print(json.dumps(report["metrics"]["aggregate"], indent=2))
    print(json.dumps(report["metrics"]["final_archive"], indent=2))
    print(report["decision"])


if __name__ == "__main__":
    main()
