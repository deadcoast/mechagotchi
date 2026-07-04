import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
READABILITY = ROOT / "labs" / "readability_benchmark"
LIFECYCLE = ROOT / "labs" / "lifecycle_sim"
for path in [ROOT, GRID_GENOME, READABILITY, LIFECYCLE]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from constrained_generator import build_constrained_corpus
from corpus_builder import build_seed_grids
from darwin_archive import build_map_elites_archive
from extended_descriptors import (
    build_extended_map_elites_archive,
    compare_extended_to_legacy,
    extended_descriptor_for_grid,
    score_extended_candidate,
    write_extended_archive_artifacts,
)


def load_lcd_slip() -> dict:
    return json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


class ExtendedDescriptorTests(unittest.TestCase):
    def test_extended_descriptor_adds_readability_survival_and_mutation_dimensions(self):
        grid = build_seed_grids()[0]
        slip = load_lcd_slip()

        descriptor = extended_descriptor_for_grid(
            grid, slip_profile=slip, lifecycle_ticks=24, rng_seed=20260512
        )

        self.assertGreaterEqual(len(descriptor["values"]), 6)
        names = descriptor["names"]
        self.assertIn("body_mass", names)
        self.assertIn("sensor_count", names)
        self.assertIn("symmetry", names)
        self.assertIn("readability", names)
        self.assertIn("lifecycle_survival", names)
        self.assertIn("mutation_stability", names)
        self.assertIn("behavior_neediness", names)

    def test_score_extended_candidate_uses_readability_lifecycle_and_slip(self):
        grid = build_seed_grids()[0]
        slip = load_lcd_slip()

        score = score_extended_candidate(
            grid, slip_profile=slip, lifecycle_ticks=24, rng_seed=20260512
        )

        self.assertGreaterEqual(score["fitness"], 0)
        self.assertLessEqual(score["fitness"], 1)
        self.assertIn("readability", score["components"])
        self.assertIn("survival", score["components"])
        self.assertIn("bond", score["components"])
        self.assertIn("slip_alignment", score["components"])

    def test_extended_archive_covers_more_niches_than_legacy_descriptor(self):
        candidates = build_constrained_corpus(build_seed_grids(), count=80, rng_seed=20260512)
        legacy = build_map_elites_archive(candidates)
        extended = build_extended_map_elites_archive(
            candidates,
            slip_profile=load_lcd_slip(),
            lifecycle_ticks=24,
            rng_seed=20260512,
        )

        self.assertGreater(
            extended["occupied_niches"],
            legacy["occupied_niches"],
        )
        self.assertGreater(extended["descriptor_dimensions"], 3)
        self.assertGreater(extended["qd_score"], 0)

    def test_compare_extended_to_legacy_reports_descriptor_expansion(self):
        candidates = build_constrained_corpus(build_seed_grids(), count=40, rng_seed=42)

        comparison = compare_extended_to_legacy(
            candidates,
            slip_profile=load_lcd_slip(),
            lifecycle_ticks=12,
            rng_seed=42,
        )

        self.assertEqual(3, comparison["legacy_descriptor_dimensions"])
        self.assertGreater(comparison["extended_descriptor_dimensions"], 3)
        self.assertGreaterEqual(
            comparison["extended_occupied_niches"],
            comparison["legacy_occupied_niches"],
        )

    def test_behavior_neediness_axis_varies_across_candidates_with_slip(self):
        # Regression for review finding H-03: the SLIP profile is constant per
        # archive run, so a profile-derived neediness collapsed this axis to a
        # single bin for every candidate.
        candidates = build_constrained_corpus(build_seed_grids(), count=80, rng_seed=20260512)
        slip = load_lcd_slip()

        neediness_bins = {
            extended_descriptor_for_grid(
                grid, slip_profile=slip, lifecycle_ticks=12, rng_seed=20260512 + index
            )["values"][6]
            for index, grid in enumerate(candidates)
        }

        self.assertGreater(len(neediness_bins), 1)

    def test_archive_reports_descriptor_bin_spread_for_every_axis(self):
        candidates = build_constrained_corpus(build_seed_grids(), count=40, rng_seed=42)
        archive = build_extended_map_elites_archive(
            candidates,
            slip_profile=load_lcd_slip(),
            lifecycle_ticks=12,
            rng_seed=42,
        )

        spread = archive["descriptor_bin_spread"]
        self.assertEqual(set(archive["descriptor_names"]), set(spread))
        for name, distinct_bins in spread.items():
            with self.subTest(axis=name):
                self.assertGreaterEqual(distinct_bins, 1)
        self.assertGreater(spread["behavior_neediness"], 1)

    def test_write_extended_archive_artifacts_creates_json_and_readme(self):
        candidates = build_constrained_corpus(build_seed_grids(), count=12, rng_seed=7)
        archive = build_extended_map_elites_archive(
            candidates,
            slip_profile=load_lcd_slip(),
            lifecycle_ticks=12,
            rng_seed=7,
        )
        comparison = compare_extended_to_legacy(
            candidates,
            slip_profile=load_lcd_slip(),
            lifecycle_ticks=12,
            rng_seed=7,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "map_elites_extended_stage0.json"

            write_extended_archive_artifacts(output_path, archive, comparison)

            self.assertTrue(output_path.exists())
            self.assertTrue((output_path.parent / "README.md").exists())
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(archive["archive_id"], written["archive"]["archive_id"])


if __name__ == "__main__":
    unittest.main()
