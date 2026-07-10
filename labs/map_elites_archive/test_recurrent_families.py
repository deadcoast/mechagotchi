import json
import sys
import tempfile
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from recurrent_families import (  # noqa: E402
    COARSENING_FACTOR,
    FAMILY_GATE,
    build_recurrent_families_report,
    cluster_families,
    family_key,
    find_recurrent_families,
    write_recurrent_families_artifacts,
)


def record(grid_id, descriptor, symmetry=0.5, complexity=0.8, neediness=0.1):
    return {
        "grid_id": grid_id,
        "niche": ",".join(str(v) for v in descriptor),
        "fitness": 0.7,
        "descriptor": list(descriptor),
        "axis_values": {
            "symmetry": symmetry,
            "visual_complexity": complexity,
            "behavior_neediness": neediness,
        },
        "signature_hash": f"hash_{grid_id}",
    }


class FamilyKeyTests(unittest.TestCase):
    def test_coarsening_halves_each_axis(self):
        self.assertEqual(2, COARSENING_FACTOR)
        self.assertEqual((0, 1, 3), family_key([1, 2, 7]))
        self.assertEqual((0, 0, 0), family_key([0, 1, 0]))

    def test_neighbouring_fine_niches_share_a_family(self):
        self.assertEqual(family_key([4, 4, 4]), family_key([5, 5, 5]))
        self.assertNotEqual(family_key([4, 4, 4]), family_key([6, 4, 4]))


class ClusterTests(unittest.TestCase):
    def test_clusters_carry_counts_and_exemplars(self):
        records = [
            record("a", [0, 0, 0]),
            record("b", [1, 1, 1]),  # same family as a (coarse 0,0,0)
            record("c", [7, 7, 7]),
        ]
        families = cluster_families(records)
        self.assertEqual(2, len(families))
        self.assertEqual(2, families[(0, 0, 0)]["count"])
        self.assertEqual(["a", "b"], families[(0, 0, 0)]["grid_ids"])
        self.assertEqual(1, families[(3, 3, 3)]["count"])


class RecurrenceTests(unittest.TestCase):
    def test_a_family_in_every_run_is_recurrent(self):
        runs = [
            [record("a1", [0, 0, 0]), record("a2", [7, 7, 7])],
            [record("b1", [1, 1, 0]), record("b2", [6, 6, 6])],
            [record("c1", [0, 1, 1]), record("c2", [7, 6, 7])],
        ]
        recurrent = find_recurrent_families(runs)
        keys = [entry["family"] for entry in recurrent]
        self.assertIn([0, 0, 0], keys)
        self.assertIn([3, 3, 3], keys)

    def test_a_family_missing_in_one_run_is_not_recurrent(self):
        runs = [
            [record("a1", [0, 0, 0])],
            [record("b1", [0, 0, 0])],
            [record("c1", [7, 7, 7])],  # family (0,0,0) absent here
        ]
        recurrent = find_recurrent_families(runs)
        self.assertEqual([], recurrent)

    def test_recurrent_entries_record_per_run_counts_and_means(self):
        runs = [
            [record("a1", [0, 0, 0], symmetry=0.2)],
            [record("b1", [1, 1, 1], symmetry=0.4)],
            [record("c1", [0, 0, 1], symmetry=0.6)],
        ]
        (entry,) = find_recurrent_families(runs)
        self.assertEqual([1, 1, 1], entry["per_run_counts"])
        self.assertEqual(3, entry["total_members"])
        self.assertEqual(
            round((0.2 + 0.4 + 0.6) / 3, 6),
            entry["axis_value_means"]["symmetry"],
        )
        self.assertEqual(["a1", "b1", "c1"], entry["exemplars_per_run"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Synthetic runs: six families, all recurrent across three runs.
        descriptors = [
            [0, 0, 0],
            [2, 2, 2],
            [4, 4, 4],
            [6, 6, 6],
            [0, 6, 0],
            [6, 0, 6],
        ]
        cls.runs = [
            {
                "rng_seed": 100 + run_index,
                "elite_records": [
                    record(f"r{run_index}_{i}", descriptor)
                    for i, descriptor in enumerate(descriptors)
                ],
            }
            for run_index in range(3)
        ]
        cls.report = build_recurrent_families_report(runs=cls.runs)

    def test_report_shape_follows_the_lab_idiom(self):
        for field in (
            "artifact_id",
            "status",
            "date",
            "purpose",
            "source_artifacts",
            "metrics",
            "closed_states",
            "blocked_states",
            "decision",
            "next_research_step",
        ):
            self.assertIn(field, self.report)
        self.assertEqual(
            "recurrent_families_stage0", self.report["artifact_id"]
        )

    def test_gate_verdict_is_recorded(self):
        metrics = self.report["metrics"]
        self.assertEqual(FAMILY_GATE, metrics["verdict"]["family_gate"])
        self.assertEqual(6, metrics["verdict"]["recurrent_family_count"])
        self.assertTrue(metrics["verdict"]["gate_met"])
        self.assertEqual("complete", self.report["status"])

    def test_failed_gate_reads_refuted(self):
        report = build_recurrent_families_report(
            runs=[
                {"rng_seed": 1, "elite_records": [record("a", [0, 0, 0])]},
                {"rng_seed": 2, "elite_records": [record("b", [7, 7, 7])]},
            ]
        )
        self.assertEqual("refuted", report["status"])
        self.assertFalse(report["metrics"]["verdict"]["gate_met"])

    def test_artifact_writer_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_recurrent_families_artifacts(output_dir, self.report)
            payload = json.loads(
                (output_dir / "recurrent_families_stage0.json").read_text(
                    encoding="utf-8"
                )
            )
        self.assertEqual(self.report["artifact_id"], payload["artifact_id"])


class Stage0ArtifactConsistencyTests(unittest.TestCase):
    """Pins the committed full-scale artifact over E4's seeded runs."""

    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(
            (
                REPO_ROOT / "data" / "archives" / "recurrent_families_stage0.json"
            ).read_text(encoding="utf-8")
        )

    def test_families_recur_across_at_least_three_independent_runs(self):
        metrics = self.artifact["metrics"]
        self.assertGreaterEqual(metrics["protocol"]["runs_analyzed"], 3)
        self.assertGreaterEqual(
            metrics["verdict"]["recurrent_family_count"], FAMILY_GATE
        )
        self.assertTrue(metrics["verdict"]["gate_met"])

    def test_every_recurrent_family_is_present_in_every_run(self):
        runs = self.artifact["metrics"]["protocol"]["runs_analyzed"]
        for family in self.artifact["metrics"]["recurrent_families"]:
            with self.subTest(family=family["family"]):
                self.assertEqual(runs, len(family["per_run_counts"]))
                self.assertTrue(
                    all(count > 0 for count in family["per_run_counts"])
                )


if __name__ == "__main__":
    unittest.main()
