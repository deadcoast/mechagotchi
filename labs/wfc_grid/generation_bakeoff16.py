"""The REAL documented generation bake-off at 16x16 (cycle 10 B2).

The dossier's stage-two protocol: compare generator arms on validity,
connectedness, organ-presence F1, symmetry, silhouette entropy, palette
violations, generation time, descriptor novelty, and readability — with
thresholds >=85-95% validity and <=250 ms per candidate at 16x16. The
historical bake-off ran WITHOUT the documented WFC field; this one has
all five arms:

- **random**   — the random-mutation baseline (the historical floor)
- **markov**   — raw Markov local transitions (proposal source only)
- **constrained** — the promoted validator-gated stabilizer (4-token)
- **wfc**      — B1's constraint layer over the FULL rich alphabet
- **hybrid**   — the documented pipeline reading: the WFC arm's
  proposal distribution IS the Markov-style local statistic, so hybrid
  = WFC collapse -> the promoted mutation-temperature stage (finding
  L-12's jitter) -> validator gate with bounded retries

Protocol adaptations, recorded: the 72/24/24 split over 120 seeds is
30/10/10 over the real 50-creature corpus (stratified per palette);
human pairwise preference is not collected (owner-deferred survey — the
readability proxy is labeled 8x8-calibrated); organ-presence F1 is
operationalized against the train corpus's modal organ-role set (roles
present in at least half the training creatures); silhouette entropy is
the Shannon entropy (bits) of the batch's silhouette-signature
distribution; descriptor novelty is unique baseline archive descriptors
per candidate. Generation time is measured wall-clock in a separate
``measured`` section flagged machine-dependent — tests assert its
presence and the gate verdict, never its values.

The adoption rule is PRE-REGISTERED (before the run): among arms
meeting the dossier validity bar (>=0.85), rich-alphabet emission is
REQUIRED (the Phase-A remainder this phase exists to close), then rank
by descriptor novelty, then silhouette entropy, then mean readability
proxy. If the documented hybrid does not win, the refutation is a
first-class finding.
"""

import argparse
import json
import math
import sys
import time
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
for sub in ["labs/grid_genome", "labs/readability_benchmark", "labs/wfc_grid"]:
    path = str(ROOT / sub)
    if path not in sys.path:
        sys.path.insert(0, path)
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from constrained_generator import (  # noqa: E402
    _apply_mutation_temperature,
    build_constrained_corpus,
)
from corpus_builder import build_seed_grids_16  # noqa: E402
from markov_grid import build_markov_corpus  # noqa: E402
from random_mutation import build_generated_corpus  # noqa: E402
from readability_benchmark import score_readability  # noqa: E402
from validator import validate_grid  # noqa: E402
from wfc_grid import (  # noqa: E402
    build_wfc_corpus,
    generate_wfc_grid,
    split_corpus,
    train_wfc_model,
)

from mecha_engine.archive import descriptor_for_candidate  # noqa: E402
from mecha_engine.archive._metrics import symmetry_score  # noqa: E402


REPORT_DATE = "2026-07-08"
ARTIFACT_ID = "generation_bakeoff16_stage0"
BATCH_COUNT = 100
RNG_SEED = 1030
VALIDITY_BAR = 0.85
TIME_BAR_MS = 250.0
HYBRID_MAX_ATTEMPTS = 4

BASIC_ROLES = {"body", "eye", "mouth"}


def build_hybrid_corpus(model: dict, *, count: int, rng_seed: int) -> list[dict]:
    """The documented pipeline: constraint collapse -> mutation -> gate."""
    candidates: list[dict] = []
    for index in range(count):
        grid_id = f"mg_hybrid_{index:03d}"
        accepted: dict | None = None
        for attempt in range(HYBRID_MAX_ATTEMPTS):
            candidate = generate_wfc_grid(
                model,
                grid_id=grid_id,
                rng_seed=int(f"{rng_seed}{attempt}"),
            )
            _apply_mutation_temperature(candidate, grid_id, rng_seed, None)
            candidate["metadata"]["source"] = "hybrid_wfc_mutation_gate_lab"
            candidate["lineage"]["mutation_events"] = [
                "wfc_wave_collapsed",
                "mutation_temperature_applied",
                "validator_gated",
            ]
            if validate_grid(candidate).ok:
                accepted = candidate
                break
            accepted = candidate  # honest: the last attempt counts
        candidates.append(accepted)
    return candidates


def measure_arm(
    grids: list[dict], train_grids: list[dict], modal_roles: set[str]
) -> dict:
    total = len(grids)
    validity = sum(1 for grid in grids if validate_grid(grid).ok) / total
    connected = sum(1 for grid in grids if _core_connected(grid)) / total
    f1_values = [
        _organ_role_f1(grid, modal_roles) for grid in grids
    ]
    symmetry_values = [symmetry_score(grid) for grid in grids]
    signatures = [_signature(grid) for grid in grids]
    train_signatures = {_signature(grid) for grid in train_grids}
    descriptors = {
        descriptor_for_candidate({"grid": grid}, {}, mode="baseline")
        for grid in grids
    }
    palette_violations = [
        _palette_violation_fraction(grid) for grid in grids
    ]
    readability_values = [
        score_readability(grid)["proxy_readability_score"] for grid in grids
    ]
    roles = {cell["role"] for grid in grids for cell in grid["cells"]}
    return {
        "candidate_count": total,
        "validity_rate": round(validity, 6),
        "connectedness_rate": round(connected, 6),
        "organ_presence_f1_mean": round(sum(f1_values) / total, 6),
        "symmetry_mean": round(sum(symmetry_values) / total, 6),
        "silhouette_entropy_bits": round(_entropy_bits(signatures), 6),
        "unique_silhouettes": len(set(signatures)),
        "palette_violation_rate": round(
            sum(palette_violations) / total, 6
        ),
        "descriptor_novelty": round(len(descriptors) / total, 6),
        "readability_proxy_mean": round(
            sum(readability_values) / total, 6
        ),
        "readability_proxy_status": "8x8_calibrated_proxy",
        "rich_roles_emitted": sorted(roles - BASIC_ROLES),
        "rich_alphabet": bool(roles - BASIC_ROLES),
        "training_copy_rate": round(
            sum(1 for sig in signatures if sig in train_signatures) / total,
            6,
        ),
        "meets_validity_bar": validity >= VALIDITY_BAR,
    }


def build_bakeoff_report() -> dict:
    seeds = build_seed_grids_16()
    train, dev, holdout = split_corpus(seeds)
    modal_roles = _modal_roles(train)
    wfc_model = train_wfc_model(train)

    batches = {
        "random": build_generated_corpus(train, per_seed=4, rng_seed=RNG_SEED)[
            :BATCH_COUNT
        ],
        "markov": build_markov_corpus(train, count=BATCH_COUNT, rng_seed=RNG_SEED),
        "constrained": build_constrained_corpus(
            train, count=BATCH_COUNT, rng_seed=RNG_SEED
        ),
        "wfc": build_wfc_corpus(wfc_model, count=BATCH_COUNT, rng_seed=RNG_SEED),
        "hybrid": build_hybrid_corpus(
            wfc_model, count=BATCH_COUNT, rng_seed=RNG_SEED
        ),
    }
    arms = {
        name: measure_arm(batch, train, modal_roles)
        for name, batch in sorted(batches.items())
    }

    # Pre-registered adoption ranking (see module docstring).
    eligible = [
        name
        for name, arm in sorted(arms.items())
        if arm["meets_validity_bar"] and arm["rich_alphabet"]
    ]
    winner = (
        max(
            eligible,
            key=lambda name: (
                arms[name]["descriptor_novelty"],
                arms[name]["silhouette_entropy_bits"],
                arms[name]["readability_proxy_mean"],
                name,
            ),
        )
        if eligible
        else None
    )
    hybrid_won = winner == "hybrid"

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete" if winner else "refuted",
        "date": REPORT_DATE,
        "purpose": (
            "Run the REAL documented generation bake-off at 16x16 — all five "
            "arms (random/markov/constrained/wfc/hybrid) on the dossier "
            "metrics with the adoption rule pre-registered: validity bar "
            ">=0.85, rich-alphabet emission required, then descriptor "
            "novelty, silhouette entropy, readability proxy."
        ),
        "source_artifacts": [
            "labs/wfc_grid/wfc_grid.py",
            "labs/grid_genome/markov_grid.py",
            "labs/grid_genome/random_mutation.py",
            "labs/grid_genome/constrained_generator.py",
            "data/seed_grids_16x16",
            "data/wfc_grid/wfc_grid_stage0.json",
            "docs/project-research/deep-research/01/deep-research.md",
        ],
        "metrics": {
            "protocol": {
                "split": {
                    "train": len(train),
                    "dev": len(dev),
                    "holdout": len(holdout),
                },
                "batch_count": BATCH_COUNT,
                "rng_seed": RNG_SEED,
                "validity_bar": VALIDITY_BAR,
                "time_bar_ms": TIME_BAR_MS,
                "modal_organ_roles": sorted(modal_roles),
                "human_pairwise_preference": "not_collected (owner-deferred survey)",
            },
            "arms": arms,
            "verdict": {
                "eligible": eligible,
                "winner": winner,
                "hybrid_won": hybrid_won,
                "hybrid_refuted": winner is not None and not hybrid_won,
            },
        },
        "closed_states": [
            "documented_bakeoff_ran_with_all_five_arms",
            "adoption_rule_pre_registered",
        ],
        "blocked_states": [
            "generation_time_gate_judged_on_the_measured_section (machine-dependent; produced by --measure-time, recorded in the report)",
            "engine_adoption_pending (B3: the winner, by decision record)",
            "human_pairwise_preference_not_collected (owner-deferred; never a blocker)",
        ],
        "decision": (
            f"Winner by the pre-registered rule: {winner}."
            if winner
            else "No arm met the bar — the protocol is refuted, not fudged."
        ),
        "next_research_step": (
            "B3: adopt the winner into mecha_engine.generation by decision "
            "record (additive seam, byte-identical off, RED-first)."
        ),
    }


def measure_generation_time() -> dict:
    """Machine-dependent wall-clock per arm (the <=250 ms dossier gate).

    Kept OUT of the deterministic report body; written into the artifact
    under ``measured`` with the machine context named.
    """
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    wfc_model = train_wfc_model(train)
    timings: dict[str, dict] = {}

    def timed(name, thunk, count):
        start = time.perf_counter()
        thunk()
        elapsed_ms = (time.perf_counter() - start) * 1000 / count
        timings[name] = {
            "mean_ms_per_candidate": round(elapsed_ms, 2),
            "meets_time_bar": elapsed_ms <= TIME_BAR_MS,
        }

    timed(
        "random",
        lambda: build_generated_corpus(train, per_seed=4, rng_seed=RNG_SEED),
        120,
    )
    timed(
        "markov",
        lambda: build_markov_corpus(train, count=BATCH_COUNT, rng_seed=RNG_SEED),
        BATCH_COUNT,
    )
    timed(
        "constrained",
        lambda: build_constrained_corpus(train, count=BATCH_COUNT, rng_seed=RNG_SEED),
        BATCH_COUNT,
    )
    timed(
        "wfc",
        lambda: build_wfc_corpus(wfc_model, count=BATCH_COUNT, rng_seed=RNG_SEED),
        BATCH_COUNT,
    )
    timed(
        "hybrid",
        lambda: build_hybrid_corpus(wfc_model, count=BATCH_COUNT, rng_seed=RNG_SEED),
        BATCH_COUNT,
    )
    return {
        "context": "stage-0 dev machine; excludes one-time model training",
        "arms": timings,
    }


def write_bakeoff_artifacts(
    output_dir: Path, report: dict, measured: dict | None = None
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = dict(report)
    if measured is not None:
        payload["measured"] = measured
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )


def _modal_roles(train_grids: list[dict]) -> set[str]:
    counts: dict[str, int] = {}
    for grid in train_grids:
        for role in {
            organ.get("role") for organ in grid["organs"].values()
        }:
            counts[role] = counts.get(role, 0) + 1
    return {
        role
        for role, count in counts.items()
        if count >= len(train_grids) / 2
    }


def _organ_role_f1(grid: dict, modal_roles: set[str]) -> float:
    present = {
        organ.get("role")
        for organ in grid.get("organs", {}).values()
        if isinstance(organ, dict)
    }
    if not present or not modal_roles:
        return 0.0
    true_positive = len(present & modal_roles)
    if true_positive == 0:
        return 0.0
    precision = true_positive / len(present)
    recall = true_positive / len(modal_roles)
    return 2 * precision * recall / (precision + recall)


def _core_connected(grid: dict) -> bool:
    points = {
        (x, y)
        for organ in grid.get("organs", {}).values()
        if isinstance(organ, dict)
        and organ.get("role") == "body_core"
        and organ.get("required") is True
        for x, y in organ.get("cells", [])
    }
    if not points:
        return False
    start = next(iter(points))
    seen = {start}
    queue = [start]
    while queue:
        x, y = queue.pop()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                neighbor = (x + dx, y + dy)
                if neighbor in points and neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
    return seen == points


def _palette_violation_fraction(grid: dict) -> float:
    colors = set(grid.get("palette", {}).get("colors", []))
    cells = grid.get("cells", [])
    if not cells or not colors:
        return 0.0
    violations = sum(
        1 for cell in cells if cell.get("visual") not in colors
    )
    return violations / len(cells)


def _entropy_bits(signatures: list[str]) -> float:
    counts: dict[str, int] = {}
    for signature in signatures:
        counts[signature] = counts.get(signature, 0) + 1
    total = len(signatures)
    return -sum(
        (count / total) * math.log2(count / total)
        for count in counts.values()
    )


def _signature(grid: dict) -> str:
    return "|".join(
        f"{cell['x']},{cell['y']}:{cell['role']}"
        for cell in sorted(
            grid["cells"], key=lambda cell: (cell["y"], cell["x"], cell["role"])
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="The documented 16x16 generation bake-off (cycle 10 B2)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "wfc_grid"
    )
    parser.add_argument("--skip-timing", action="store_true")
    args = parser.parse_args()
    report = build_bakeoff_report()
    measured = None if args.skip_timing else measure_generation_time()
    write_bakeoff_artifacts(args.output_dir, report, measured)
    print(json.dumps(report["metrics"]["arms"], indent=2))
    print(json.dumps(report["metrics"]["verdict"], indent=2))
    if measured is not None:
        print(json.dumps(measured, indent=2))


if __name__ == "__main__":
    main()
