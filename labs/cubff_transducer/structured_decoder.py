"""Cycle 20 J4: the structured-decoder direct arm.

I2 proved the transducer study's saturation belongs to the ARMS: raw
tape→pixels never forms a validator-legal body in ANY soup phase, and
the semantic arm is validator-gated by construction. This lab builds
the DIFFERENT direct arm the I2 remainder named — a decoder grounded
in the tape's OWN language, bff_noheads's ten instruction bytes
(`bff.inc.h` at the audited commit), by recorded correspondence:

    '.' copy-read  -> B body    (what replicates is mass)
    ',' copy-write -> E eye     (the program's output face)
    '[' ']' loops  -> J joint   (control flow articulates)
    '<' '>' head-0 -> L limb    (tape motion locomotes)
    '{'     head-1 -> N antenna (the second head feels forward)
    '}'     head-1 -> P sensor  (and feels back)
    '+' '-' mutate -> F effect  (byte mutation glows)
    everything else -> empty

Byte index i lands at (i % 8, i // 8) on the 8×8 canvas — the tape's
structure IS the morphology's structure. The FIRST copy-read cell
carries the animation anchor (a creature's heart is its first copy).
The validator judges freely: no connectivity fix-ups, no organ
patching, no anchor rescue — the decoder can FAIL, which is exactly
what makes the comparison falsifiable both ways. Un-saturation and
joining the refuted record are both first-class verdicts.
"""

import argparse
import json
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
GRID_GENOME = LAB_DIR.parent / "grid_genome"
READABILITY = LAB_DIR.parent / "readability_benchmark"
for _path in (LAB_DIR, GRID_GENOME, READABILITY):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from cubff_transducer import score_readability  # noqa: E402
from grid_helpers import grid_from_matrix  # noqa: E402
from validator import validate_grid  # noqa: E402

ARTIFACT_ID = "structured_decoder_stage0"
REPORT_DATE = "2026-07-20"
DECODE_SIZE = 8
INSTRUCTION_TOKENS: dict[int, str] = {
    ord("["): "J",
    ord("]"): "J",
    ord("<"): "L",
    ord(">"): "L",
    ord("{"): "N",
    ord("}"): "P",
    ord("+"): "F",
    ord("-"): "F",
    ord("."): "B",
    ord(","): "E",
}
DEFAULT_CURATED_PATH = (
    ROOT / "data" / "cubff_transducer" / "real_states_curated_i2.json"
)


def decode_tape_to_grid(
    state: dict, grid_id: str, *, palette_id: str = "lcd_green"
) -> dict:
    """Decode one real state's 64-byte tape into a grid genome."""
    tape = [int(value) % 256 for value in state.get("tape", [])][
        : DECODE_SIZE * DECODE_SIZE
    ]
    matrix = [
        ["." for _ in range(DECODE_SIZE)] for _ in range(DECODE_SIZE)
    ]
    anchor_placed = False
    for index, byte in enumerate(tape):
        token = INSTRUCTION_TOKENS.get(byte)
        if token is None:
            continue
        if token == "B" and not anchor_placed:
            token = "A"
            anchor_placed = True
        matrix[index // DECODE_SIZE][index % DECODE_SIZE] = token
    return grid_from_matrix(
        grid_id,
        matrix,
        palette_id,
        source="structured_tape_decoder",
        mutation_events=["structured_tape_decoded"],
    )


def build_decoder_study_report(
    *, curated_path: str | Path = DEFAULT_CURATED_PATH
) -> dict:
    curated = json.loads(Path(curated_path).read_text(encoding="utf-8"))
    states = curated["states"]

    per_state: list[dict] = []
    for index, state in enumerate(states):
        grid = decode_tape_to_grid(
            state, f"decoded_{index:03d}"
        )
        valid = validate_grid(grid).ok
        readability = round(score_readability(grid), 6)
        per_state.append(
            {
                "snapshot_id": state.get("snapshot_id", f"state_{index}"),
                "phase": state.get("phase", "unmeasured"),
                "decoded_cell_count": len(grid["cells"]),
                "decoder_valid": valid,
                "decoder_readability": readability,
            }
        )

    valid_count = sum(1 for e in per_state if e["decoder_valid"])
    reads = [e["decoder_readability"] for e in per_state]
    gates = {
        "validity_unsaturated": valid_count > 0,
        "readability_graded": bool(reads) and max(reads) > min(reads),
    }

    phase_metrics: dict[str, dict] = {}
    for phase in sorted({e["phase"] for e in per_state}):
        subset = [e for e in per_state if e["phase"] == phase]
        phase_reads = [e["decoder_readability"] for e in subset]
        phase_metrics[phase] = {
            "state_count": len(subset),
            "valid_count": sum(1 for e in subset if e["decoder_valid"]),
            "valid_rate": round(
                sum(1 for e in subset if e["decoder_valid"]) / len(subset), 6
            ),
            "mean_readability": round(
                sum(phase_reads) / len(phase_reads), 6
            ),
            "mean_decoded_cells": round(
                sum(e["decoded_cell_count"] for e in subset) / len(subset),
                6,
            ),
        }
    phase_names = list(phase_metrics)
    gates["phase_sensitive"] = len(phase_names) > 1 and any(
        phase_metrics[phase_names[0]][key]
        != phase_metrics[phase_names[1]][key]
        for key in ("valid_rate", "mean_readability", "mean_decoded_cells")
    )

    unsaturated = (
        gates["validity_unsaturated"] and gates["readability_graded"]
    )
    decision = {
        "verdict": "unsaturated"
        if unsaturated
        else "decoder_joins_the_refuted_record",
        "reason": (
            "the structured decoder produces validator-passing bodies "
            "with graded readability — the arms' saturation is broken "
            "and the comparison is measurable again"
            if unsaturated
            else "even a language-grounded structured decoder cannot "
            "produce validator-passing bodies from real tape — the "
            "refuted record grows by one honest entry"
        ),
    }

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 20 J4: the I2 remainder's DIFFERENT direct arm — a "
            "tape decoder grounded in bff_noheads's own instruction "
            "classes, judged freely by the validator over the "
            "committed two-phase corpus; un-saturation and refutation "
            "both first-class."
        ),
        "source_artifacts": [
            "data/cubff_transducer/real_states_curated_i2.json",
            "labs/cubff_transducer/cubff_transducer.py (score_readability)",
            "labs/grid_genome/grid_helpers.py (the rich reconstruction)",
            "research/experiment_reports/2026-07-20-transducer-study-post-takeover.md",
        ],
        "instruction_correspondence": {
            chr(byte): token for byte, token in INSTRUCTION_TOKENS.items()
        },
        "metrics": {
            "state_count": len(per_state),
            "decoder_valid_count": valid_count,
            "decoder_valid_rate": round(valid_count / len(per_state), 6)
            if per_state
            else 0.0,
            "readability_min": min(reads) if reads else 0.0,
            "readability_max": max(reads) if reads else 0.0,
            "per_phase": phase_metrics,
            "per_state": per_state,
            "gates": gates,
        },
        "closed_states": [
            "structured_decoder_designed_and_judged_freely",
        ],
        "blocked_states": [
            "pipeline_adoption_not_in_question (the KEEP decision for "
            "the semantic transducer stands; the decoder is a study "
            "instrument)",
        ],
        "decision": decision,
        "next_research_step": (
            "if unsaturated: the graded comparison re-runs the "
            "preference question with a live direct arm; if refuted: "
            "the record stands sharper"
        ),
    }


def write_decoder_study_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--curated-path", type=Path, default=DEFAULT_CURATED_PATH
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data" / "cubff_transducer",
    )
    args = parser.parse_args()
    report = build_decoder_study_report(curated_path=args.curated_path)
    written = write_decoder_study_artifacts(args.output_dir, report)
    print(f"wrote {written}")
    print(json.dumps(report["metrics"]["gates"], indent=2))
    print(json.dumps(report["metrics"]["per_phase"], indent=2))
    print(report["decision"]["verdict"])
