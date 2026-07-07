"""MAP-Elites comparator study (audit T18, RUN TWO's unrun keep-gate).

MAP-Elites was adopted without its og-specified comparison. This lab
runs it: GA truncation selection and novelty search versus the shipped
archive, at MATCHED budgets over IDENTICAL candidate streams (the same
generated creatures, in the same order, per seed — only the SELECTION
strategy differs). Stage 0 scale is recorded honestly: population 32
and hundreds of evaluations per comparator per seed; RUN TWO's
256-population / 50k-evaluation / 10-seed protocol is the scale-up.

Keep-gate (RUN TWO adapted): MAP-Elites is CONFIRMED if its niche
coverage beats GA's by >= 25% at matched budget while best fitness stays
within 10% of the strongest comparator — derived from measurements; a
CHALLENGED verdict would be a first-class result.
"""

import argparse
import json
import sys
from pathlib import Path
from statistics import mean, pstdev


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "data" / "archives"
for path in [
    ROOT / "packages" / "mecha_engine" / "src",
    ROOT / "labs" / "grid_genome",
    ROOT / "labs" / "readability_benchmark",
]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from corpus_builder import build_seed_grids  # noqa: E402
from readability_benchmark import score_readability  # noqa: E402

from mecha_engine.archive import (  # noqa: E402
    build_archive,
    descriptor_for_candidate,
    insert_candidate,
    score_candidate,
)
from mecha_engine.generation import (  # noqa: E402
    generate_candidate,
    train_generation_model,
)
from mecha_engine.lifecycle import run_episode  # noqa: E402


POPULATION = 32
NOVELTY_K = 5


def _candidate_stream(
    seeds: list[dict], slip_profile: dict, generation_model: dict,
    *, budget: int, ticks: int, rng_seed: int, generator=None,
) -> list[dict]:
    """One evaluated candidate stream, shared by every comparator.

    `generator(parent, index, run_seed) -> grid` overrides the default
    package-hybrid arm (the T17 A/B uses the constrained generator).
    """
    pool = [
        seed
        for seed in seeds
        if seed["palette"]["palette_id"]
        in slip_profile["grid"]["allowed_palettes"]
    ]
    stream = []
    for index in range(budget):
        parent = pool[index % len(pool)]
        run_seed = rng_seed + index
        if generator is not None:
            grid = generator(parent, index, run_seed)
        else:
            grid = generate_candidate(
                parent, generation_model, slip_profile, rng_seed=run_seed
            )
        episode = run_episode(
            grid, slip_profile, policy="switchboard",
            ticks=ticks, rng_seed=run_seed,
        )
        metrics = {
            "readability": score_readability(grid),
            "slip_profile": slip_profile,
            "slip_alignment": {"ok": True},
            "lifecycle": episode,
            "rng_seed": run_seed,
        }
        candidate = {"grid": grid}
        score = score_candidate(candidate, metrics)
        descriptor = descriptor_for_candidate(candidate, metrics)
        stream.append(
            {
                "candidate": candidate,
                "score": score,
                "descriptor": tuple(descriptor),
                "fitness": score["fitness"],
            }
        )
    return stream


def _survivor_metrics(survivors: list[dict]) -> dict:
    niches: dict[tuple, float] = {}
    for entry in survivors:
        key = entry["descriptor"]
        niches[key] = max(niches.get(key, 0.0), entry["fitness"])
    fits = [entry["fitness"] for entry in survivors]
    return {
        "coverage": len(niches),
        "qd_score": round(sum(niches.values()), 6),
        "best_fitness": round(max(fits), 6) if fits else 0.0,
        "mean_fitness": round(mean(fits), 6) if fits else 0.0,
        "descriptor_dispersion": round(
            pstdev([sum(entry["descriptor"]) for entry in survivors]), 6
        )
        if len(survivors) > 1
        else 0.0,
        "survivor_count": len(survivors),
    }


def _ga_truncation(stream: list[dict]) -> dict:
    population: list[dict] = []
    for entry in stream:
        population.append(entry)
        population.sort(key=lambda e: (-e["fitness"], e["descriptor"]))
        population = population[:POPULATION]
    return _survivor_metrics(population)


def _novelty_search(stream: list[dict]) -> dict:
    seen: list[tuple] = []
    archive: list[dict] = []
    for entry in stream:
        if seen:
            distances = sorted(
                sum(abs(a - b) for a, b in zip(entry["descriptor"], other))
                for other in seen
            )
            novelty = mean(distances[:NOVELTY_K])
        else:
            novelty = float("inf")
        seen.append(entry["descriptor"])
        archive.append({**entry, "novelty": novelty})
        archive.sort(
            key=lambda e: (-e["novelty"], -e["fitness"], e["descriptor"])
        )
        archive = archive[:POPULATION]
    return _survivor_metrics(archive)


def _map_elites(stream: list[dict]) -> dict:
    archive = build_archive([], {})
    for entry in stream:
        archive = insert_candidate(
            archive, entry["candidate"], entry["score"],
            list(entry["descriptor"]),
        )
    survivors = [
        {
            "descriptor": tuple(elite["descriptor"]["values"]),
            "fitness": elite["fitness"],
        }
        for elite in archive["elites"].values()
    ]
    return _survivor_metrics(survivors)


def build_archive_comparators_report(
    *, budget: int = 150, ticks: int = 24, rng_seeds: tuple = (20260512, 20260612, 20260712),
) -> dict:
    slip_profile = json.loads(
        (ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )
    seeds = build_seed_grids()
    generation_model = train_generation_model(seeds)

    runs = []
    for rng_seed in rng_seeds:
        stream = _candidate_stream(
            seeds, slip_profile, generation_model,
            budget=budget, ticks=ticks, rng_seed=rng_seed,
        )
        runs.append(
            {
                "rng_seed": rng_seed,
                "ga_truncation": _ga_truncation(stream),
                "novelty_search": _novelty_search(stream),
                "map_elites": _map_elites(stream),
            }
        )

    def _avg(comparator: str, metric: str) -> float:
        return round(mean(run[comparator][metric] for run in runs), 6)

    summary = {
        comparator: {
            metric: _avg(comparator, metric)
            for metric in (
                "coverage", "qd_score", "best_fitness", "mean_fitness",
            )
        }
        for comparator in ("ga_truncation", "novelty_search", "map_elites")
    }
    ga_coverage = summary["ga_truncation"]["coverage"]
    me_coverage = summary["map_elites"]["coverage"]
    strongest_best = max(
        summary[c]["best_fitness"] for c in summary
    )
    coverage_advantage = round(
        (me_coverage - ga_coverage) / ga_coverage, 6
    ) if ga_coverage else float("inf")
    best_gap = round(
        (strongest_best - summary["map_elites"]["best_fitness"])
        / strongest_best,
        6,
    ) if strongest_best else 0.0
    confirmed = coverage_advantage >= 0.25 and best_gap <= 0.10

    return {
        "artifact_id": "archive_comparators_stage0",
        "status": "stage0_complete",
        "date": "2026-07-06",
        "purpose": (
            "RUN TWO's unrun MAP-Elites keep-gate (audit T18): GA "
            "truncation and novelty search vs the shipped archive at "
            "matched budgets over identical candidate streams."
        ),
        "protocol": {
            "budget_per_comparator_per_seed": budget,
            "rng_seeds": list(rng_seeds),
            "population": POPULATION,
            "novelty_k": NOVELTY_K,
            "ticks": ticks,
            "scale_up": (
                "RUN TWO full protocol: population 256, 50k evaluations, "
                "10 seeds (recorded, not run at Stage 0)."
            ),
        },
        "runs": runs,
        "summary": summary,
        "gate": {
            "coverage_advantage_over_ga": coverage_advantage,
            "og_coverage_bar": 0.25,
            "best_fitness_gap_to_strongest": best_gap,
            "og_best_gap_bar": 0.10,
            "map_elites_confirmed": confirmed,
        },
        "decision": {
            "status": (
                "map_elites_confirmed" if confirmed else "map_elites_challenged"
            ),
            "reason": (
                f"Mean coverage {me_coverage} vs GA {ga_coverage} "
                f"(advantage {coverage_advantage}, bar 0.25); best-fitness "
                f"gap to strongest {best_gap} (bar 0.10). Measured over "
                f"{len(rng_seeds)} seeds x {budget} evaluations on "
                "identical streams."
            ),
        },
        "next_research_step": (
            "Scale toward the RUN TWO protocol (population, budget, "
            "seeds) and add the zoo profiles as additional streams; a "
            "challenged verdict at scale reopens the archive design."
        ),
    }


def build_generator_ab_report(
    *, budget: int = 150, ticks: int = 24,
    rng_seeds: tuple = (20260512, 20260612, 20260712),
) -> dict:
    """T17 follow-up A/B: does the constrained arm's holdout novelty
    (2.4x the hybrid's) translate into a better MAP-Elites archive?

    Identical evaluation, identical budgets, identical parent pools —
    only the GENERATOR differs. Any switch of the shipped generator
    happens by its own decision record, only if the constrained arm
    wins here.
    """
    from constrained_generator import (
        generate_constrained_grid,
        train_constraints,
    )

    slip_profile = json.loads(
        (ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )
    seeds = build_seed_grids()
    generation_model = train_generation_model(seeds)
    constrained_model = train_constraints(seeds)

    def constrained(parent, index, run_seed):
        return generate_constrained_grid(
            constrained_model,
            seeds,
            f"ab_wfc_{index:04d}",
            run_seed,
            slip=slip_profile,
        )

    runs = []
    for rng_seed in rng_seeds:
        arms = {}
        for arm_name, generator in [
            ("package_hybrid", None),
            ("constrained_wfc", constrained),
        ]:
            stream = _candidate_stream(
                seeds, slip_profile, generation_model,
                budget=budget, ticks=ticks, rng_seed=rng_seed,
                generator=generator,
            )
            arms[arm_name] = _map_elites(stream)
        runs.append({"rng_seed": rng_seed, **arms})

    summary = {
        arm: {
            metric: round(
                mean(run[arm][metric] for run in runs), 6
            )
            for metric in ("coverage", "qd_score", "best_fitness", "mean_fitness")
        }
        for arm in ("package_hybrid", "constrained_wfc")
    }
    hybrid, wfc = summary["package_hybrid"], summary["constrained_wfc"]
    wfc_wins = (
        wfc["coverage"] > hybrid["coverage"]
        and wfc["qd_score"] > hybrid["qd_score"]
        and wfc["best_fitness"] >= hybrid["best_fitness"] * 0.95
    )
    return {
        "artifact_id": "generator_evolution_ab_stage0",
        "status": "stage0_complete",
        "date": "2026-07-06",
        "purpose": (
            "T17 follow-up: constrained-vs-hybrid generator A/B through "
            "the MAP-Elites archive at matched budgets."
        ),
        "protocol": {
            "budget_per_arm_per_seed": budget,
            "rng_seeds": list(rng_seeds),
            "ticks": ticks,
        },
        "runs": runs,
        "summary": summary,
        "decision": {
            "status": (
                "constrained_arm_wins_dr_gated_switch_proposed"
                if wfc_wins
                else "shipped_hybrid_stands"
            ),
            "reason": (
                f"coverage {wfc['coverage']} vs {hybrid['coverage']}; QD "
                f"{wfc['qd_score']} vs {hybrid['qd_score']}; best fitness "
                f"{wfc['best_fitness']} vs {hybrid['best_fitness']}. A "
                "generator switch requires its own decision record."
            ),
        },
    }


def write_generator_ab_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "generator_evolution_ab_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def write_archive_comparators_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "archive_comparators_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the archive comparators.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--budget", type=int, default=150)
    parser.add_argument(
        "--mode", choices=["comparators", "generator_ab"], default="comparators"
    )
    args = parser.parse_args()
    if args.mode == "generator_ab":
        report = build_generator_ab_report(budget=args.budget)
        write_generator_ab_artifacts(args.output_dir, report)
    else:
        report = build_archive_comparators_report(budget=args.budget)
        write_archive_comparators_artifacts(args.output_dir, report)
    print(json.dumps(report["summary"], indent=2))
    if "gate" in report:
        print(json.dumps(report["gate"], indent=2))
    print(json.dumps(report["decision"], indent=2))


if __name__ == "__main__":
    main()
