"""Cycle 20 J4 gates — the structured-decoder direct arm.

I2 proved the study's saturation is a property of the ARMS: raw
tape→pixels never forms a validator-legal body in any phase. The
structured decoder is the DIFFERENT direct arm the remainder named —
grounded in the tape's OWN language: each of bff_noheads's ten
instruction bytes maps to a morphological token by recorded
correspondence (copy-read → body, copy-write → eye, loops → joints,
head-0 motion → limbs, head-1 motion → feelers, byte mutation →
effects; every other byte is empty), position-preserving on the 8×8
canvas, the anchor on the FIRST copy-read cell. The validator judges
freely — the decoder can fail, so the comparison is falsifiable both
ways, and un-saturation or refutation are both first-class.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
GRID_GENOME = LAB_DIR.parent / "grid_genome"
for _path in (LAB_DIR, GRID_GENOME):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

from structured_decoder import (  # noqa: E402
    INSTRUCTION_TOKENS,
    build_decoder_study_report,
    decode_tape_to_grid,
    write_decoder_study_artifacts,
)
from validator import validate_grid  # noqa: E402


def _tape(instructions: dict[int, str]) -> list[int]:
    tape = [0] * 64
    for index, char in instructions.items():
        tape[index] = ord(char)
    return tape


def _state(tape: list[int], *, snapshot_id: str = "s", phase: str = "early_phase") -> dict:
    return {
        "snapshot_id": snapshot_id,
        "epoch": 1,
        "tape": tape,
        "phase": phase,
        "run_seed": 0,
    }


class InstructionTableTests(unittest.TestCase):
    def test_the_correspondence_is_the_recorded_ten_instructions(self):
        expected = {
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
        self.assertEqual(expected, INSTRUCTION_TOKENS)


class DecoderTests(unittest.TestCase):
    def test_positions_preserve_the_tape_and_roles_follow_the_table(self):
        tape = _tape({0: ".", 1: ".", 9: "[", 10: "]", 17: "<", 26: ",", 35: "+"})
        grid = decode_tape_to_grid(_state(tape), "decode_pin")
        by_position = {
            (cell["x"], cell["y"]): (cell["role"], cell["animation_anchor"])
            for cell in grid["cells"]
        }
        # Byte index i lands at (i % 8, i // 8); the FIRST copy-read
        # carries the anchor.
        self.assertEqual(("body", True), by_position[(0, 0)])
        self.assertEqual(("body", False), by_position[(1, 0)])
        self.assertEqual(("joint", False), by_position[(1, 1)])
        self.assertEqual(("joint", False), by_position[(2, 1)])
        self.assertEqual(("limb", False), by_position[(1, 2)])
        self.assertEqual(("eye", False), by_position[(2, 3)])
        self.assertEqual(("effect", False), by_position[(3, 4)])
        self.assertEqual(7, len(grid["cells"]))

    def test_a_tape_without_copy_reads_has_no_anchor_and_fails_freely(self):
        tape = _tape({i: "[" for i in range(16)})
        grid = decode_tape_to_grid(_state(tape), "anchorless")
        self.assertFalse(
            any(cell["animation_anchor"] for cell in grid["cells"])
        )
        result = validate_grid(grid)
        self.assertFalse(result.ok)  # the decoder can fail — by design

    def test_decoding_is_deterministic_and_never_mutates_the_state(self):
        tape = _tape({0: ".", 1: "[", 2: "]"})
        state = _state(tape)
        pristine = json.loads(json.dumps(state))
        first = decode_tape_to_grid(state, "twin")
        second = decode_tape_to_grid(state, "twin")
        self.assertEqual(
            json.dumps(first, sort_keys=True),
            json.dumps(second, sort_keys=True),
        )
        self.assertEqual(pristine, state)


class DecoderStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # A tiny synthetic curated corpus: one dense-replicator-style
        # state (structured), one no-op state (empty), both phases.
        dense = _tape(
            {
                **{i: "." for i in range(18, 30)},
                **{i: "." for i in range(34, 38)},
                8: "[",
                15: "]",
                40: "<",
                41: ">",
                43: ",",
                50: "+",
            }
        )
        sparse = _tape({})
        cls.curated = {
            "states": [
                _state(dense, snapshot_id="post_dense", phase="post_takeover"),
                _state(sparse, snapshot_id="early_empty", phase="early_phase"),
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "curated.json"
            path.write_text(json.dumps(cls.curated), encoding="utf-8")
            cls.report = build_decoder_study_report(curated_path=path)

    def test_every_state_is_judged_with_its_phase(self):
        per_state = self.report["metrics"]["per_state"]
        self.assertEqual(2, len(per_state))
        for entry in per_state:
            self.assertIn("decoder_valid", entry)
            self.assertIn("decoder_readability", entry)
            self.assertIn(entry["phase"], {"early_phase", "post_takeover"})

    def test_the_unsaturation_gates_are_the_numbers(self):
        metrics = self.report["metrics"]
        per_state = metrics["per_state"]
        valid_count = sum(1 for e in per_state if e["decoder_valid"])
        reads = [e["decoder_readability"] for e in per_state]
        self.assertEqual(
            metrics["gates"]["validity_unsaturated"], valid_count > 0
        )
        self.assertEqual(
            metrics["gates"]["readability_graded"],
            max(reads) > min(reads),
        )
        expected_verdict = (
            "unsaturated"
            if metrics["gates"]["validity_unsaturated"]
            and metrics["gates"]["readability_graded"]
            else "decoder_joins_the_refuted_record"
        )
        self.assertEqual(expected_verdict, self.report["decision"]["verdict"])

    def test_artifacts_are_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_decoder_study_artifacts(Path(tmp), self.report)
            payload = json.loads(
                (
                    Path(tmp) / "structured_decoder_stage0.json"
                ).read_text(encoding="utf-8")
            )
        self.assertEqual(
            "structured_decoder_stage0", payload["artifact_id"]
        )
        self.assertIn("verdict", payload["decision"])


if __name__ == "__main__":
    unittest.main()
