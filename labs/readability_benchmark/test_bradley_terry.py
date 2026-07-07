import csv
import tempfile
import unittest
from pathlib import Path

from bradley_terry import bradley_terry_strengths, load_pairwise_csv


class BradleyTerryTests(unittest.TestCase):
    """T20 tooling validation on SYNTHETIC pairings (never human data)."""

    def test_dominant_item_earns_the_highest_strength(self):
        wins = {("a", "b"): 9, ("b", "a"): 1, ("a", "c"): 8, ("c", "a"): 2, ("b", "c"): 6, ("c", "b"): 4}
        strengths = bradley_terry_strengths(wins)
        self.assertGreater(strengths["a"], strengths["b"])
        self.assertGreater(strengths["b"], strengths["c"])
        self.assertAlmostEqual(1.0, sum(strengths.values()), places=5)

    def test_symmetric_wins_give_equal_strengths(self):
        wins = {("x", "y"): 5, ("y", "x"): 5}
        strengths = bradley_terry_strengths(wins)
        self.assertAlmostEqual(strengths["x"], strengths["y"], places=6)

    def test_deterministic_and_empty_safe(self):
        wins = {("a", "b"): 3, ("b", "c"): 3, ("c", "a"): 3}
        self.assertEqual(
            bradley_terry_strengths(wins), bradley_terry_strengths(wins)
        )
        self.assertEqual({}, bradley_terry_strengths({}))

    def test_csv_intake(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "pairs.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["winner", "loser", "count"])
                writer.writerow(["a", "b", "3"])
                writer.writerow(["a", "b", "2"])
                writer.writerow(["b", "a", "1"])
            wins = load_pairwise_csv(path)
            self.assertEqual({("a", "b"): 5, ("b", "a"): 1}, wins)


if __name__ == "__main__":
    unittest.main()
