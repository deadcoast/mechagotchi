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
    judge_degeneracy,
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


def _phased_result(
    phase: str,
    *,
    direct_valid: bool = False,
    direct_readability: float = 0.0,
    semantic_readability: float = 1.0,
) -> dict:
    return {
        "snapshot_id": "s",
        "run_seed": 0,
        "phase": phase,
        "semantic_valid": True,
        "direct_valid": direct_valid,
        "semantic_readability": semantic_readability,
        "direct_readability": direct_readability,
        "semantic_preferred": semantic_readability > direct_readability,
    }


class DegeneracyTests(unittest.TestCase):
    """Cycle 19 I2: G3's saturation is the pre-registered expectation

    to BREAK over post-takeover states — and the judgment must be
    falsifiable both ways (a corpus that stays degenerate is a
    first-class finding, not an error).
    """

    def test_post_takeover_direct_validity_breaks_the_degeneracy(self):
        results = [
            _phased_result("early_phase"),
            _phased_result("post_takeover", direct_valid=True),
            _phased_result("post_takeover"),
        ]
        verdict = judge_degeneracy(results)
        self.assertEqual(2, verdict["post_takeover_state_count"])
        self.assertEqual(1, verdict["direct_valid_count"])
        self.assertTrue(verdict["direct_left_zero_valid"])
        self.assertTrue(verdict["degeneracy_broken"])

    def test_post_takeover_readability_variance_breaks_the_degeneracy(self):
        results = [
            _phased_result("post_takeover", direct_readability=0.0),
            _phased_result("post_takeover", direct_readability=0.25),
        ]
        verdict = judge_degeneracy(results)
        self.assertFalse(verdict["direct_left_zero_valid"])
        self.assertTrue(verdict["direct_readability_left_flat"])
        self.assertTrue(verdict["degeneracy_broken"])
        self.assertEqual(0.0, verdict["direct_readability_min"])
        self.assertEqual(0.25, verdict["direct_readability_max"])

    def test_a_still_degenerate_post_takeover_corpus_is_reported_honestly(self):
        results = [
            _phased_result("post_takeover"),
            _phased_result("post_takeover"),
        ]
        verdict = judge_degeneracy(results)
        self.assertFalse(verdict["direct_left_zero_valid"])
        self.assertFalse(verdict["direct_readability_left_flat"])
        self.assertFalse(verdict["degeneracy_broken"])

    def test_no_post_takeover_states_cannot_claim_a_break(self):
        verdict = judge_degeneracy([_phased_result("early_phase")])
        self.assertEqual(0, verdict["post_takeover_state_count"])
        self.assertFalse(verdict["degeneracy_broken"])
        self.assertIn("no post-takeover states", verdict["reason"])

    def test_semantic_variance_is_recorded_but_never_the_break_criterion(self):
        results = [
            _phased_result("post_takeover", semantic_readability=1.0),
            _phased_result("post_takeover", semantic_readability=0.75),
        ]
        verdict = judge_degeneracy(results)
        self.assertTrue(verdict["semantic_readability_left_flat"])
        self.assertFalse(verdict["degeneracy_broken"])


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

    def test_per_state_carries_phase_and_the_report_judges_degeneracy(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "seed00"
            run_dir.mkdir()
            dats = sorted(G2_CORPUS.glob("*.dat"))[:2]
            for dat in dats:
                (run_dir / dat.name).write_bytes(dat.read_bytes())
            # The run's own metrics: first save early, second post.
            (run_dir / "metrics.csv").write_text(
                "epoch,brotli_size,soup_size,higher_entropy\n"
                "1,524284,8192,-0.000301\n"
                "2049,100000,8192,5.0\n",
                encoding="utf-8",
            )
            states = curate_states(
                Path(tmp), source_commit=SOURCE_COMMIT
            )
            report = run_real_transducer_study(states, rng_seed=5150)
        self.assertEqual(
            ["early_phase", "post_takeover"],
            [entry["phase"] for entry in report["per_state"]],
        )
        self.assertEqual(
            {"early_phase": 1, "post_takeover": 1, "unmeasured": 0},
            report["phase_summary"],
        )
        self.assertIn("degeneracy_broken", report["degeneracy"])
        self.assertEqual(
            1, report["degeneracy"]["post_takeover_state_count"]
        )

    def test_artifact_identity_can_diverge_so_g3_stays_frozen(self):
        report = run_real_transducer_study(
            [], artifact_id="real_transducer_study_i2_stage0",
            date="2026-07-20",
        )
        self.assertEqual(
            "real_transducer_study_i2_stage0", report["artifact_id"]
        )
        self.assertEqual("2026-07-20", report["date"])
        default = run_real_transducer_study([])
        self.assertEqual(
            "real_transducer_study_stage0", default["artifact_id"]
        )
        self.assertEqual("2026-07-12", default["date"])


if __name__ == "__main__":
    unittest.main()
