"""G3 gates — the documented transducer study over REAL states.

The dossier's protocol: 20 runs / 400 curated states; keep the
semantic transducer if PREFERENCE > 60% and INVALID < 10%. The gates
are pre-registered arithmetic (falsifiable both ways, pinned here);
curation is the fixed epoch grid — every checkpoint of every run, no
cherry-picking; the per-state arms are the existing lab's own
functions verbatim. The committed G2 corpus (real checkpoints) backs
the curation-shape tests, so nothing here is synthetic.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from real_transducer_study import (  # noqa: E402
    curate_states,
    judge_gates,
    run_real_transducer_study,
)

G2_CORPUS = (
    ROOT / "data" / "cubff_real_ingest" / "source_snapshots" / "run_seed0_num8192"
)
SOURCE_COMMIT = "f212e849027c98fcf4b242eccfb5fed435223e23"


def _result(preferred: bool, semantic_valid: bool) -> dict:
    return {
        "snapshot_id": "s",
        "run_seed": 0,
        "semantic_valid": semantic_valid,
        "direct_valid": True,
        "semantic_readability": 1.0 if preferred else 0.0,
        "direct_readability": 0.5,
        "semantic_preferred": preferred,
    }


class GateTests(unittest.TestCase):
    def test_the_documented_gates_are_falsifiable_both_ways(self):
        # 13/20 preferred (65%) and 1/20 invalid (5%): both gates MET.
        results = [_result(True, True)] * 13 + [
            _result(False, True)
        ] * 6 + [_result(False, False)]
        verdict = judge_gates(results)
        self.assertTrue(verdict["preference_gate_met"])
        self.assertTrue(verdict["invalid_gate_met"])
        self.assertEqual(0.65, verdict["preference_rate"])
        self.assertEqual(0.05, verdict["semantic_invalid_rate"])
        self.assertEqual("keep", verdict["keep_decision"])
        # 12/20 preferred (60%) is NOT strictly greater than 60%.
        boundary = [_result(True, True)] * 12 + [
            _result(False, True)
        ] * 8
        self.assertFalse(judge_gates(boundary)["preference_gate_met"])
        # 2/20 invalid (10%) is NOT strictly under 10%.
        invalid = [_result(True, True)] * 18 + [
            _result(True, False)
        ] * 2
        self.assertFalse(judge_gates(invalid)["invalid_gate_met"])
        self.assertEqual("reject", judge_gates(invalid)["keep_decision"])


class CurationTests(unittest.TestCase):
    def test_curation_is_the_fixed_grid_over_real_checkpoints(self):
        # The committed G2 corpus is one run directory's worth of REAL
        # checkpoints; curation ingests every .dat in epoch order.
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "seed00"
            run_dir.mkdir()
            for dat in sorted(G2_CORPUS.glob("*.dat")):
                (run_dir / dat.name).write_bytes(dat.read_bytes())
            states = curate_states(
                Path(tmp), source_commit=SOURCE_COMMIT
            )
        self.assertEqual(9, len(states))
        epochs = [state["epoch"] for state in states]
        self.assertEqual(sorted(epochs), epochs)
        for state in states:
            self.assertEqual(0, state["run_seed"])
            self.assertEqual(64, len(state["tape"]))
            self.assertEqual(
                "real_cubff_checkpoint", state["source_type"]
            )


class StudyTests(unittest.TestCase):
    def test_the_study_runs_both_arms_deterministically(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "seed00"
            run_dir.mkdir()
            for dat in sorted(G2_CORPUS.glob("*.dat"))[:4]:
                (run_dir / dat.name).write_bytes(dat.read_bytes())
            states = curate_states(
                Path(tmp), source_commit=SOURCE_COMMIT
            )
        first = run_real_transducer_study(states, rng_seed=5150)
        second = run_real_transducer_study(states, rng_seed=5150)
        self.assertEqual(
            json.dumps(first, sort_keys=True),
            json.dumps(second, sort_keys=True),
        )
        self.assertEqual(4, first["state_count"])
        self.assertEqual(4, len(first["per_state"]))
        for entry in first["per_state"]:
            self.assertIn("semantic_preferred", entry)
            self.assertIn("semantic_valid", entry)
        self.assertIn("keep_decision", first["gates"])
        self.assertEqual(
            "real_cubff_checkpoints", first["source_mode"]
        )


if __name__ == "__main__":
    unittest.main()
