import argparse
import json
from pathlib import Path

from constrained_generator import generate_constrained_grid, train_constraints
from corpus_builder import build_seed_grids
from grid_helpers import grid_signature as _signature
from slip import is_grid_aligned, validate_slip
from validator import validate_grid


ROOT = Path(__file__).resolve().parents[2]


def run_profile_compatibility_suite(
    profile_paths: list[Path],
    *,
    count_per_profile: int = 50,
    rng_seed: int = 214,
) -> dict:
    seed_grids = build_seed_grids()
    model = train_constraints(seed_grids)
    profile_results = []

    for profile_path in profile_paths:
        profile = _load_profile(profile_path)
        slip_result = validate_slip(profile)
        if not slip_result.ok:
            raise ValueError(f"{profile_path}: {'; '.join(slip_result.errors)}")
        profile_results.append(
            _run_profile_benchmark(
                model,
                seed_grids,
                profile,
                source_path=profile_path,
                count=count_per_profile,
                rng_seed=rng_seed,
            )
        )

    return {
        "artifact_id": "slip_multi_profile_generation_stage0",
        "status": "research_slip_multi_profile_generation_no_package_code",
        "rng_seed": rng_seed,
        "count_per_profile": count_per_profile,
        "profile_results": profile_results,
        "totals": _totals(profile_results),
        "blocked_states": [
            "behavior_preview",
            "mutation_preview",
            "profile_weighted_evolution",
            "community_profile_pack_import",
            "full_slip_json_schema",
        ],
    }


def write_profile_compatibility_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "slip_multi_profile_generation_stage0.json", _without_grids(report))
    for result in report["profile_results"]:
        corpus_dir = output_dir / result["profile_id"]
        corpus_dir.mkdir(parents=True, exist_ok=True)
        for grid in result["generated_grids"]:
            _write_json(corpus_dir / f"{grid['grid_id']}.json", grid)


def _run_profile_benchmark(
    model: dict,
    seed_grids: list[dict],
    profile: dict,
    *,
    source_path: Path,
    count: int,
    rng_seed: int,
) -> dict:
    generated = []
    valid_count = 0
    aligned_count = 0
    validation_errors: dict[str, int] = {}
    alignment_errors: dict[str, int] = {}

    profile_id = profile["profile_id"]
    for index in range(count):
        grid = generate_constrained_grid(
            model,
            seed_grids,
            grid_id=f"{profile_id}_constrained_{index:03d}",
            rng_seed=rng_seed,
            slip=profile,
        )
        validation = validate_grid(grid)
        alignment = is_grid_aligned(grid, profile)
        if validation.ok:
            valid_count += 1
        else:
            _count_errors(validation_errors, validation.errors)
        if alignment.ok:
            aligned_count += 1
        else:
            _count_errors(alignment_errors, alignment.errors)
        generated.append(grid)

    candidate_count = len(generated)
    return {
        "profile_id": profile_id,
        "source_path": _portable(source_path),
        "allowed_palettes": profile["grid"]["allowed_palettes"],
        "body_mass_min": profile["grid"]["body_mass_min"],
        "body_mass_max": profile["grid"]["body_mass_max"],
        "required_organ_roles": profile["grid"]["required_organ_roles"],
        "candidate_count": candidate_count,
        "valid_count": valid_count,
        "invalid_count": candidate_count - valid_count,
        "aligned_count": aligned_count,
        "misaligned_count": candidate_count - aligned_count,
        "validity_rate": valid_count / candidate_count if candidate_count else 0,
        "alignment_rate": aligned_count / candidate_count if candidate_count else 0,
        "unique_signatures": len({_signature(grid) for grid in generated}),
        "validation_errors": dict(sorted(validation_errors.items())),
        "alignment_errors": dict(sorted(alignment_errors.items())),
        "generated_grids": generated,
    }


def _totals(profile_results: list[dict]) -> dict:
    candidate_count = sum(result["candidate_count"] for result in profile_results)
    valid_count = sum(result["valid_count"] for result in profile_results)
    aligned_count = sum(result["aligned_count"] for result in profile_results)
    return {
        "profile_count": len(profile_results),
        "candidate_count": candidate_count,
        "valid_count": valid_count,
        "invalid_count": candidate_count - valid_count,
        "aligned_count": aligned_count,
        "misaligned_count": candidate_count - aligned_count,
        "validity_rate": valid_count / candidate_count if candidate_count else 0,
        "alignment_rate": aligned_count / candidate_count if candidate_count else 0,
    }


def _without_grids(report: dict) -> dict:
    compact = dict(report)
    compact["profile_results"] = [
        {key: value for key, value in result.items() if key != "generated_grids"}
        for result in report["profile_results"]
    ]
    return compact


def _load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _portable(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _count_errors(target: dict[str, int], errors: list[str]) -> None:
    for error in errors:
        target[error] = target.get(error, 0) + 1


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        type=Path,
        action="append",
        required=True,
        help="Path to a valid SLIP profile. Repeat for multiple profiles.",
    )
    parser.add_argument("--count-per-profile", type=int, default=50)
    parser.add_argument("--rng-seed", type=int, default=214)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data/slips/multi_profile_generation_stage0",
    )
    args = parser.parse_args()

    report = run_profile_compatibility_suite(
        args.profile,
        count_per_profile=args.count_per_profile,
        rng_seed=args.rng_seed,
    )
    write_profile_compatibility_artifacts(args.output_dir, report)
    print(json.dumps(_without_grids(report), indent=2))


if __name__ == "__main__":
    main()
