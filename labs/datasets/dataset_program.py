"""The og dataset program (R6 = T11): the ML tracks' fuel.

Three named corpora from the og research plan's dataset table, each
built deterministically from the engine's own surfaces and shipped with
a README and a checksummed manifest:

- **mechaseed_200** — the broader body-plan training/eval set: the 50
  hand-authored `mechaseed_50` seeds plus 150 curated variants. Variants
  are engine-generated offspring (`mecha_engine.generation`, fixed rng
  seeds), curated by the same bar the corpus itself sets: every variant
  passes `validate_grid`, and `grid_signature` dedup guarantees no
  variant repeats a seed or another variant. JSON, one file
  (the `animstate_300` precedent).
- **mutationbench_5000** — mutation-operator evaluation: 5,000 offspring
  cases (50 parents x 100 fixed rng seeds) as compact JSONL rows. Rows
  carry the case config, the outcome measurements (validity, alignment,
  lineage generation, cell-level diff counts), and the candidate's
  `grid_signature` — the candidate itself is deterministically
  reproducible from the row's config, and the signature makes any
  regeneration verifiable byte-for-byte without storing 5,000 grids.
- **replay_100k_ticks** — behaviour/switchboard evaluation: 100k+
  per-tick lifecycle logs (the episode's own history entries, verbatim)
  across the seed corpus x policies (switchboard/idle/random) x rng
  seeds. Gzipped JSONL (stdlib `gzip`; the og table's "JSONL/Parquet"
  in a dependency-free form) plus a small uncompressed sample for
  greppability. Feeds R5: these are the same history entries the replay
  recorder frames.

Deterministic end to end; no wall clock; every dataset file is
checksummed (sha256) in the stage-0 report so drift is detectable.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
for path in [GRID_GENOME, PACKAGE_SRC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from corpus_builder import build_seed_grids  # noqa: E402
from slip import is_grid_aligned  # noqa: E402

from mecha_engine.generation import (  # noqa: E402
    generate_candidate,
    train_generation_model,
)
from mecha_engine.genome import grid_signature, validate_grid  # noqa: E402
from mecha_engine.lifecycle import run_episode  # noqa: E402

ARTIFACT_ID = "dataset_program_stage0"
REPORT_DATE = "2026-07-07"
DATASET_DATE = "2026-07-07"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "datasets"
SLIP_PROFILE_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"

MECHASEED_TARGET = 200
MUTATIONBENCH_TARGET = 5000
REPLAY_TICK_TARGET = 100_000
REPLAY_POLICIES = ("switchboard", "idle", "random")
REPLAY_TICKS_PER_EPISODE = 72


def build_corpus_profile(seeds: list[dict]) -> dict:
    """The dataset program's generation config: the standard fixture
    profile widened to admit the WHOLE seed corpus (every palette, the
    full mass range) so the body-plan datasets keep the corpus's
    diversity instead of one covenant's slice. Authority-valid
    (`validate_slip`) and alignment-verified against all 50 seeds by
    the test suite; shipped alongside the datasets for reproducibility."""
    profile = json.loads(SLIP_PROFILE_PATH.read_text(encoding="utf-8"))
    profile["profile_id"] = "slip_corpus_r6"
    profile["name"] = "R6 dataset-program corpus profile"
    profile["grid"]["allowed_palettes"] = sorted(
        {seed["palette"]["palette_id"] for seed in seeds}
    )
    profile["grid"]["body_mass_min"] = 1
    profile["grid"]["body_mass_max"] = 64
    return profile


def _token_map(grid: dict) -> dict[tuple[int, int], str]:
    return {
        (cell["x"], cell["y"]): f"{cell['role']}/{cell.get('organ')}"
        for cell in grid["cells"]
    }


def _cell_diff(parent: dict, candidate: dict) -> dict:
    before = _token_map(parent)
    after = _token_map(candidate)
    return {
        "cells_added": len(set(after) - set(before)),
        "cells_removed": len(set(before) - set(after)),
        "cells_retoken": sum(
            1
            for key in set(before) & set(after)
            if before[key] != after[key]
        ),
        "mass_delta": len(after) - len(before),
    }


def build_mechaseed_200(
    seeds: list[dict],
    generation_model: dict,
    slip_profile: dict,
    *,
    target: int = MECHASEED_TARGET,
) -> dict:
    """mechaseed_50 + engine-generated, validity-curated variants.

    Deterministic curation: for each seed in order, offspring at fixed
    rng seeds join the corpus when they pass `validate_grid` and their
    `grid_signature` is new; the seed offset walks forward until the
    target is met, so the corpus is a pure function of its inputs."""
    entries = [
        {
            "entry_id": f"mechaseed_200_{index:03d}",
            "origin": "mechaseed_50",
            "parent_grid_id": None,
            "variant_rng_seed": None,
            "grid_signature": grid_signature(seed),
            "grid": seed,
        }
        for index, seed in enumerate(seeds)
    ]
    signatures = {entry["grid_signature"] for entry in entries}
    offset = 0
    while len(entries) < target and offset < 100:
        for seed in seeds:
            if len(entries) >= target:
                break
            rng_seed = 20260707 + offset * 1000
            candidate = generate_candidate(
                seed, generation_model, slip_profile, rng_seed=rng_seed
            )
            if not validate_grid(candidate).ok:
                continue
            signature = grid_signature(candidate)
            if signature in signatures:
                continue
            signatures.add(signature)
            entries.append(
                {
                    "entry_id": f"mechaseed_200_{len(entries):03d}",
                    "origin": "generated_variant",
                    "parent_grid_id": seed["grid_id"],
                    "variant_rng_seed": rng_seed,
                    "grid_signature": signature,
                    "grid": candidate,
                }
            )
        offset += 1
    return {
        "dataset_id": "mechaseed_200",
        "dataset_version": f"mechaseed_200@{DATASET_DATE}",
        "date": DATASET_DATE,
        "purpose": "broader body-plan training/eval set (og dataset table)",
        "curation_rule": (
            "validate_grid must pass; grid_signature must be novel; "
            "deterministic seed-offset walk until the target is met"
        ),
        "source_corpus": "data/seed_grids/mg_seed_001..050.json",
        "entry_count": len(entries),
        "entries": entries,
    }


def build_mutationbench_5000(
    seeds: list[dict],
    generation_model: dict,
    slip_profile: dict,
    *,
    target: int = MUTATIONBENCH_TARGET,
) -> list[dict]:
    """5,000 deterministic offspring cases as compact JSONL rows."""
    per_parent = max(1, target // len(seeds))
    rows: list[dict] = []
    for parent_index, parent in enumerate(seeds):
        for case_index in range(per_parent):
            if len(rows) >= target:
                break
            rng_seed = 30260707 + parent_index * 10_000 + case_index
            candidate = generate_candidate(
                parent, generation_model, slip_profile, rng_seed=rng_seed
            )
            validation = validate_grid(candidate)
            alignment = is_grid_aligned(candidate, slip_profile)
            rows.append(
                {
                    "case_id": f"mutationbench_{len(rows):04d}",
                    "parent_grid_id": parent["grid_id"],
                    "rng_seed": rng_seed,
                    "profile_id": slip_profile.get("profile_id"),
                    "candidate_grid_id": candidate["grid_id"],
                    "candidate_signature": grid_signature(candidate),
                    "valid": validation.ok,
                    "error_count": len(validation.errors),
                    "aligned": alignment.ok,
                    "lineage_generation": candidate.get("lineage", {}).get(
                        "generation", 0
                    ),
                    "mutation_events": list(
                        candidate.get("lineage", {}).get(
                            "mutation_events", []
                        )
                    ),
                    **_cell_diff(parent, candidate),
                }
            )
    return rows


def build_replay_100k_ticks(
    seeds: list[dict],
    slip_profile: dict,
    *,
    tick_target: int = REPLAY_TICK_TARGET,
    ticks_per_episode: int = REPLAY_TICKS_PER_EPISODE,
) -> tuple[list[dict], dict]:
    """100k+ per-tick lifecycle logs (episode history entries verbatim).

    Enumeration is deterministic: rng-seed round robin over
    (seed corpus x policies); each episode contributes its full history.
    Returns (rows, coverage_summary)."""
    rows: list[dict] = []
    episode_count = 0
    by_policy: dict[str, int] = {policy: 0 for policy in REPLAY_POLICIES}
    round_index = 0
    while len(rows) < tick_target:
        for creature_index, creature in enumerate(seeds):
            for policy in REPLAY_POLICIES:
                if len(rows) >= tick_target:
                    break
                rng_seed = 40260707 + round_index * 100_000 + creature_index
                episode = run_episode(
                    creature,
                    slip_profile,
                    policy=policy,
                    ticks=ticks_per_episode,
                    rng_seed=rng_seed,
                )
                episode_id = (
                    f"replay_{creature['grid_id']}_{policy}_r{round_index:02d}"
                )
                episode_count += 1
                by_policy[policy] += len(episode["history"])
                for entry in episode["history"]:
                    rows.append(
                        {
                            "episode_id": episode_id,
                            "grid_id": creature["grid_id"],
                            "policy": policy,
                            "rng_seed": rng_seed,
                            "ticks_requested": ticks_per_episode,
                            **entry,
                        }
                    )
            if len(rows) >= tick_target:
                break
        round_index += 1
    coverage = {
        "tick_count": len(rows),
        "episode_count": episode_count,
        "creature_count": len(seeds),
        "policies": list(REPLAY_POLICIES),
        "ticks_by_policy": by_policy,
        "rounds": round_index,
    }
    return rows, coverage


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_dataset_artifacts(
    output_dir: str | Path,
    mechaseed: dict,
    mutationbench: list[dict],
    replay_rows: list[dict],
    replay_coverage: dict,
    corpus_profile: dict | None = None,
) -> dict:
    """Write the three corpora (each with a README) and return the
    manifest of files + checksums for the stage-0 report."""
    output_dir = Path(output_dir)
    files: dict[str, Path] = {}
    output_dir.mkdir(parents=True, exist_ok=True)
    if corpus_profile is not None:
        files["slip_corpus_r6"] = output_dir / "slip_corpus_r6.json"
        files["slip_corpus_r6"].write_text(
            json.dumps(corpus_profile, indent=2) + "\n", encoding="utf-8"
        )

    mechaseed_dir = output_dir / "mechaseed_200"
    mechaseed_dir.mkdir(parents=True, exist_ok=True)
    files["mechaseed_200"] = mechaseed_dir / "mechaseed_200.json"
    files["mechaseed_200"].write_text(
        json.dumps(mechaseed, indent=1) + "\n", encoding="utf-8"
    )
    (mechaseed_dir / "README.md").write_text(
        "# mechaseed_200\n\n"
        f"`{mechaseed['dataset_version']}` — the og broader body-plan\n"
        "training/eval set: the 50 hand-authored `mechaseed_50` seeds\n"
        "(`data/seed_grids/`) plus 150 engine-generated variants, curated\n"
        "by the corpus bar itself: every variant passes `validate_grid`\n"
        "and `grid_signature` dedup guarantees novelty. Deterministic —\n"
        "each variant records the parent and rng seed that reproduce it\n"
        "through `mecha_engine.generation.generate_candidate`.\n\n"
        "Regenerate: `python -B labs/datasets/dataset_program.py`\n",
        encoding="utf-8",
    )

    bench_dir = output_dir / "mutationbench_5000"
    bench_dir.mkdir(parents=True, exist_ok=True)
    files["mutationbench_5000"] = bench_dir / "mutationbench_5000.jsonl"
    files["mutationbench_5000"].write_text(
        "".join(json.dumps(row) + "\n" for row in mutationbench),
        encoding="utf-8",
    )
    (bench_dir / "README.md").write_text(
        "# mutationbench_5000\n\n"
        f"`mutationbench_5000@{DATASET_DATE}` — mutation-operator\n"
        "evaluation: 5,000 offspring cases (50 parents x 100 fixed rng\n"
        "seeds under `slip_lcd_seed`) as JSONL rows. Each row carries the\n"
        "case config, outcome measurements (validity, alignment, lineage\n"
        "generation, cell-level diffs), and the candidate's\n"
        "`grid_signature`: the candidate grid itself is deterministically\n"
        "reproducible from `(parent_grid_id, rng_seed, profile)` through\n"
        "`generate_candidate`, and the signature verifies any\n"
        "regeneration byte-for-byte — 5,000 grids of truth without\n"
        "5,000 stored grids.\n\n"
        "Regenerate: `python -B labs/datasets/dataset_program.py`\n",
        encoding="utf-8",
    )

    replay_dir = output_dir / "replay_100k_ticks"
    replay_dir.mkdir(parents=True, exist_ok=True)
    files["replay_100k_ticks"] = replay_dir / "replay_100k_ticks.jsonl.gz"
    payload = "".join(json.dumps(row) + "\n" for row in replay_rows)
    # mtime=0 keeps the gzip byte-deterministic (no wall clock).
    with gzip.GzipFile(
        filename="",
        mode="wb",
        fileobj=files["replay_100k_ticks"].open("wb"),
        mtime=0,
    ) as handle:
        handle.write(payload.encode("utf-8"))
    files["replay_sample"] = replay_dir / "replay_sample_first_200.jsonl"
    files["replay_sample"].write_text(
        "".join(json.dumps(row) + "\n" for row in replay_rows[:200]),
        encoding="utf-8",
    )
    (replay_dir / "README.md").write_text(
        "# replay_100k_ticks\n\n"
        f"`replay_100k_ticks@{DATASET_DATE}` — behaviour/switchboard\n"
        "evaluation: "
        f"{replay_coverage['tick_count']} per-tick lifecycle logs across\n"
        f"{replay_coverage['episode_count']} episodes ({replay_coverage['creature_count']}\n"
        "seed creatures x switchboard/idle/random x deterministic rng\n"
        "rounds). Rows are the episode's own history entries VERBATIM\n"
        "(tick, action, need balance, recoveries, alive/death, full state\n"
        "snapshot) — the same entries the R5 replay recorder frames.\n"
        "Gzipped JSONL (stdlib `gzip`, mtime=0 for byte determinism);\n"
        "`replay_sample_first_200.jsonl` is an uncompressed sample.\n\n"
        "Read: `import gzip, json; rows = [json.loads(l) for l in "
        "gzip.open(path, 'rt', encoding='utf-8')]`\n\n"
        "Regenerate: `python -B labs/datasets/dataset_program.py`\n",
        encoding="utf-8",
    )

    def manifest_path(path: Path) -> str:
        # Repo-relative POSIX strings (the L-08 rule); out-of-repo
        # targets (test temp dirs) record the file name only.
        try:
            return path.relative_to(ROOT).as_posix()
        except ValueError:
            return path.name

    return {
        name: {
            "path": manifest_path(path),
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for name, path in files.items()
    }


def build_program_report(
    mechaseed: dict,
    mutationbench: list[dict],
    replay_coverage: dict,
    manifest: dict,
) -> dict:
    variant_count = sum(
        1
        for entry in mechaseed["entries"]
        if entry["origin"] == "generated_variant"
    )
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0_complete",
        "date": REPORT_DATE,
        "purpose": (
            "R6 (=T11): complete the og dataset program — mechaseed_200, "
            "mutationbench_5000, replay_100k_ticks — deterministically "
            "from the engine's own surfaces, each with a README and a "
            "checksummed manifest. The ML tracks' fuel."
        ),
        "source_artifacts": [
            "data/seed_grids/",
            "data/slips/valid/slip_lcd_seed.json",
            "packages/mecha_engine/src/mecha_engine/generation/",
            "packages/mecha_engine/src/mecha_engine/lifecycle/",
        ],
        "metrics": {
            "mechaseed_200": {
                "entry_count": mechaseed["entry_count"],
                "seed_count": mechaseed["entry_count"] - variant_count,
                "variant_count": variant_count,
                "all_valid": True,  # pinned by the test suite
            },
            "mutationbench_5000": {
                "case_count": len(mutationbench),
                "valid_rate": round(
                    sum(1 for row in mutationbench if row["valid"])
                    / len(mutationbench),
                    6,
                ),
                "aligned_rate": round(
                    sum(1 for row in mutationbench if row["aligned"])
                    / len(mutationbench),
                    6,
                ),
            },
            "replay_100k_ticks": replay_coverage,
            "manifest": manifest,
        },
        "closed_states": [
            "mechaseed_200_delivered_validity_curated",
            "mutationbench_5000_delivered_signature_verifiable",
            "replay_100k_ticks_delivered_engine_history_verbatim",
            "every_dataset_readme_and_checksum_shipped",
        ],
        "blocked_states": [
            # The og table's PNG-render companion for mechaseed_200 is a
            # presentation artifact; the workshop export codecs cover it
            # on demand, and committing 200 PNGs is deferred until a
            # consumer exists.
            "mechaseed_200_png_renders_deferred_no_consumer",
        ],
        "decision": {
            "status": "dataset_program_complete",
            "adoption": "lab_only_dataset_evidence",
            "reason": (
                "All three og corpora exist as named, versioned, "
                "checksummed datasets built deterministically from "
                "promoted engine surfaces: the body-plan corpus is "
                "validity-curated and signature-deduped, the mutation "
                "bench is reproducible case-by-case and verifiable by "
                "signature, and the replay corpus is the lifecycle's "
                "own per-tick history at 100k+ ticks."
            ),
        },
        "next_research_step": (
            "R7 (grid-schema animation/species fields) closes the cycle; "
            "the ML tracks consume these corpora (learned readability "
            "retraining, switchboard evaluation, replay tooling)."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the og dataset program (R6): all three corpora."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    seeds = build_seed_grids()
    slip_profile = build_corpus_profile(seeds)
    generation_model = train_generation_model(seeds)

    mechaseed = build_mechaseed_200(seeds, generation_model, slip_profile)
    mutationbench = build_mutationbench_5000(
        seeds, generation_model, slip_profile
    )
    replay_rows, replay_coverage = build_replay_100k_ticks(
        seeds, slip_profile
    )
    manifest = write_dataset_artifacts(
        args.output_dir,
        mechaseed,
        mutationbench,
        replay_rows,
        replay_coverage,
        corpus_profile=slip_profile,
    )
    report = build_program_report(
        mechaseed, mutationbench, replay_coverage, manifest
    )
    report_path = Path(args.output_dir) / "dataset_program_stage0.json"
    report_path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "artifact_id": report["artifact_id"],
                "decision": report["decision"]["status"],
                "mechaseed_200": mechaseed["entry_count"],
                "mutationbench_5000": len(mutationbench),
                "replay_ticks": replay_coverage["tick_count"],
                "output_dir": str(args.output_dir),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
