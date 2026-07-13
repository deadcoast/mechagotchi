"""The documented transducer study over REAL CuBFF states (cycle 17 G3).

The dossier's protocol, executed over the G2 build path: 20 runs /
400 curated states; **keep the semantic transducer if PREFERENCE >
60% and INVALID < 10%** — pre-registered arithmetic, falsifiable both
ways, judged over per-state results.

- **Curation is the fixed grid, never a choice**: every checkpoint of
  every run directory (`seedNN/*.dat`), ingested through the G2 gate's
  own parser in epoch order — epoch-stratified sampling with no
  cherry-picking.
- **The arms are the existing lab's, verbatim**: per state, the direct
  tape→pixels projection vs the semantic compile
  (features → traits → constrained grid), both judged by the lab's own
  validity and readability functions. Preference per state = the
  semantic grid strictly out-reads the direct one.
- **The verdicts are whatever the real corpus supports** — a refuted
  gate is a first-class finding.
"""

import argparse
import json
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from cubff_transducer import (  # noqa: E402
    compile_semantic_grid,
    direct_tape_to_grid,
    score_readability,
)
from real_snapshot_ingest import ingest_snapshot_file  # noqa: E402

GRID_GENOME_DIR = LAB_DIR.parent / "grid_genome"
if str(GRID_GENOME_DIR) not in sys.path:
    sys.path.insert(0, str(GRID_GENOME_DIR))

from corpus_builder import build_seed_grids  # noqa: E402
from validator import validate_grid  # noqa: E402

ARTIFACT_ID = "real_transducer_study_stage0"
REPORT_DATE = "2026-07-12"
CUBFF_REPO_URL = "https://github.com/paradigms-of-intelligence/cubff"
# The documented keep gates (gap analysis, the CuBFF row): strict.
PREFERENCE_GATE = 0.60
INVALID_GATE = 0.10
SLIP_PROFILE_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"


def curate_states(
    fleet_dir: str | Path, *, source_commit: str
) -> list[dict]:
    """Every checkpoint of every ``seedNN`` run directory, ingested in
    epoch order through the G2 parser — the fixed curation grid."""
    fleet_dir = Path(fleet_dir)
    states: list[dict] = []
    for run_dir in sorted(fleet_dir.glob("seed*")):
        run_seed = int(run_dir.name.replace("seed", ""))
        for dat in sorted(run_dir.glob("*.dat")):
            outcome = ingest_snapshot_file(
                dat,
                source_repo=CUBFF_REPO_URL,
                source_commit=source_commit,
                language="bff_noheads",
                seed=run_seed,
            )
            for record in outcome["snapshots"]:
                record["run_seed"] = run_seed
                record["snapshot_id"] = (
                    f"seed{run_seed:02d}_{record['snapshot_id']}"
                )
                states.append(record)
    return states


def write_curated_states(path: str | Path, states: list[dict]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "curation": "every checkpoint of every run, epoch order",
                "state_count": len(states),
                "states": states,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def judge_gates(results: list[dict]) -> dict:
    """The documented keep gates, strict, over per-state results."""
    count = len(results)
    preferred = sum(1 for r in results if r["semantic_preferred"])
    invalid = sum(1 for r in results if not r["semantic_valid"])
    preference_rate = preferred / count if count else 0.0
    invalid_rate = invalid / count if count else 1.0
    preference_met = preference_rate > PREFERENCE_GATE
    invalid_met = invalid_rate < INVALID_GATE
    return {
        "state_count": count,
        "preferred_count": preferred,
        "preference_rate": round(preference_rate, 6),
        "preference_gate": f"> {PREFERENCE_GATE}",
        "preference_gate_met": preference_met,
        "semantic_invalid_count": invalid,
        "semantic_invalid_rate": round(invalid_rate, 6),
        "invalid_gate": f"< {INVALID_GATE}",
        "invalid_gate_met": invalid_met,
        "keep_decision": (
            "keep" if preference_met and invalid_met else "reject"
        ),
    }


def run_real_transducer_study(
    states: list[dict], *, rng_seed: int = 5150
) -> dict:
    """Both arms per state, the lab's own functions verbatim."""
    seed_grids = build_seed_grids()
    slip_profile = json.loads(
        SLIP_PROFILE_PATH.read_text(encoding="utf-8")
    )
    per_state: list[dict] = []
    for index, state in enumerate(states):
        direct = direct_tape_to_grid(
            state, grid_id=f"real_direct_{index:03d}"
        )
        semantic = compile_semantic_grid(
            state,
            seed_grids,
            slip_profile,
            grid_id=f"real_semantic_{index:03d}",
            rng_seed=rng_seed + index,
        )
        direct_valid = validate_grid(direct).ok
        semantic_valid = validate_grid(semantic).ok
        direct_read = round(score_readability(direct), 6)
        semantic_read = round(score_readability(semantic), 6)
        per_state.append(
            {
                "snapshot_id": state["snapshot_id"],
                "run_seed": state["run_seed"],
                "epoch": state["epoch"],
                "direct_valid": direct_valid,
                "semantic_valid": semantic_valid,
                "direct_readability": direct_read,
                "semantic_readability": semantic_read,
                "semantic_preferred": semantic_read > direct_read,
            }
        )
    gates = judge_gates(per_state)
    run_seeds = sorted({state["run_seed"] for state in states})
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "source_mode": "real_cubff_checkpoints",
        "state_count": len(states),
        "run_count": len(run_seeds),
        "run_seeds": run_seeds,
        "per_state": per_state,
        "gates": gates,
        "arms": {
            "direct": "A: raw tape to pixels (the lab's projection)",
            "semantic": (
                "D: CuBFF features -> traits -> constrained grid "
                "(the lab's compiler)"
            ),
        },
        "source_anchors": [
            CUBFF_REPO_URL,
            "https://arxiv.org/abs/2406.19108",
        ],
    }


def write_study_artifacts(
    output_dir: str | Path, report: dict, states: list[dict]
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_curated_states(
        output_dir / "real_states_curated.json", states
    )
    path = output_dir / f"{ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fleet-dir", type=Path, required=True)
    parser.add_argument(
        "--source-commit",
        default="f212e849027c98fcf4b242eccfb5fed435223e23",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data" / "cubff_transducer",
    )
    args = parser.parse_args()
    curated = curate_states(
        args.fleet_dir, source_commit=args.source_commit
    )
    study = run_real_transducer_study(curated)
    written = write_study_artifacts(args.output_dir, study, curated)
    print(f"wrote {written}")
    print(json.dumps(study["gates"], indent=2))
