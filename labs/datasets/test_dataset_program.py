"""R6 gates: every corpus is deterministic, engine-derived, and honest —
validity-curated bodies, signature-verifiable mutation cases, verbatim
lifecycle ticks. Tests run at scaled-down targets; the shipped datasets
use the module defaults."""

import gzip
import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from dataset_program import (  # noqa: E402
    build_corpus_profile,
    build_mechaseed_200,
    build_mutationbench_5000,
    build_replay_100k_ticks,
    build_seed_grids,
    write_dataset_artifacts,
)
from slip import is_grid_aligned, validate_slip  # noqa: E402

from mecha_engine.generation import (  # noqa: E402
    generate_candidate,
    train_generation_model,
)
from mecha_engine.genome import grid_signature, validate_grid  # noqa: E402


class DatasetProgramTests(unittest.TestCase):
    seeds: list[dict]

    @classmethod
    def setUpClass(cls):
        cls.seeds = build_seed_grids()
        cls.generation_model = train_generation_model(cls.seeds)
        cls.slip_profile = build_corpus_profile(cls.seeds)
        cls.mechaseed = build_mechaseed_200(
            cls.seeds, cls.generation_model, cls.slip_profile, target=60
        )
        cls.bench = build_mutationbench_5000(
            cls.seeds, cls.generation_model, cls.slip_profile, target=100
        )
        cls.replay_rows, cls.replay_coverage = build_replay_100k_ticks(
            cls.seeds,
            cls.slip_profile,
            tick_target=500,
            ticks_per_episode=12,
        )

    # -- the corpus profile -----------------------------------------------

    def test_corpus_profile_is_authority_valid_and_admits_every_seed(self):
        self.assertTrue(validate_slip(self.slip_profile).ok)
        for seed in self.seeds:
            self.assertTrue(is_grid_aligned(seed, self.slip_profile).ok)

    # -- mechaseed_200 --------------------------------------------------

    def test_mechaseed_meets_its_target_and_keeps_the_50(self):
        self.assertEqual(60, self.mechaseed["entry_count"])
        originals = [
            entry
            for entry in self.mechaseed["entries"]
            if entry["origin"] == "mechaseed_50"
        ]
        self.assertEqual(len(self.seeds), len(originals))

    def test_mechaseed_every_entry_is_valid_and_signature_unique(self):
        signatures = set()
        for entry in self.mechaseed["entries"]:
            self.assertTrue(validate_grid(entry["grid"]).ok)
            self.assertEqual(
                grid_signature(entry["grid"]), entry["grid_signature"]
            )
            self.assertNotIn(entry["grid_signature"], signatures)
            signatures.add(entry["grid_signature"])

    def test_mechaseed_variants_are_reproducible_from_their_record(self):
        variant = next(
            entry
            for entry in self.mechaseed["entries"]
            if entry["origin"] == "generated_variant"
        )
        parent = next(
            seed
            for seed in self.seeds
            if seed["grid_id"] == variant["parent_grid_id"]
        )
        regenerated = generate_candidate(
            parent,
            self.generation_model,
            self.slip_profile,
            rng_seed=variant["variant_rng_seed"],
        )
        self.assertEqual(regenerated, variant["grid"])

    def test_mechaseed_is_deterministic(self):
        again = build_mechaseed_200(
            self.seeds, self.generation_model, self.slip_profile, target=60
        )
        self.assertEqual(self.mechaseed, again)

    # -- mutationbench_5000 ----------------------------------------------

    def test_mutationbench_rows_are_signature_verifiable(self):
        self.assertEqual(100, len(self.bench))
        by_id = {seed["grid_id"]: seed for seed in self.seeds}
        for row in self.bench[:5]:
            candidate = generate_candidate(
                by_id[row["parent_grid_id"]],
                self.generation_model,
                self.slip_profile,
                rng_seed=row["rng_seed"],
            )
            self.assertEqual(
                grid_signature(candidate), row["candidate_signature"]
            )
            self.assertEqual(validate_grid(candidate).ok, row["valid"])

    def test_mutationbench_rows_carry_the_measurements(self):
        for row in self.bench:
            for field in (
                "case_id",
                "parent_grid_id",
                "rng_seed",
                "valid",
                "aligned",
                "lineage_generation",
                "cells_added",
                "cells_removed",
                "cells_retoken",
                "mass_delta",
                "mutation_events",
            ):
                self.assertIn(field, row)
        self.assertEqual(
            len({row["case_id"] for row in self.bench}), len(self.bench)
        )

    def test_mutationbench_is_deterministic(self):
        again = build_mutationbench_5000(
            self.seeds, self.generation_model, self.slip_profile, target=100
        )
        self.assertEqual(self.bench, again)

    # -- replay_100k_ticks -------------------------------------------------

    def test_replay_meets_the_tick_target_with_verbatim_entries(self):
        self.assertGreaterEqual(len(self.replay_rows), 500)
        self.assertEqual(
            self.replay_coverage["tick_count"], len(self.replay_rows)
        )
        for row in self.replay_rows[:50]:
            for field in (
                "episode_id",
                "grid_id",
                "policy",
                "rng_seed",
                "tick",
                "action",
                "balance",
                "alive",
                "state",
            ):
                self.assertIn(field, row)
            self.assertGreaterEqual(row["balance"], 0.0)
            self.assertLessEqual(row["balance"], 1.0)

    def test_replay_ticks_are_contiguous_per_episode(self):
        by_episode: dict[str, list[int]] = {}
        for row in self.replay_rows:
            by_episode.setdefault(row["episode_id"], []).append(row["tick"])
        for ticks in by_episode.values():
            self.assertEqual(list(range(1, len(ticks) + 1)), ticks)

    def test_replay_is_deterministic(self):
        rows, coverage = build_replay_100k_ticks(
            self.seeds,
            self.slip_profile,
            tick_target=500,
            ticks_per_episode=12,
        )
        self.assertEqual(self.replay_rows, rows)
        self.assertEqual(self.replay_coverage, coverage)

    # -- artifacts ------------------------------------------------------------

    def test_artifacts_write_with_readmes_checksums_and_gzip_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = write_dataset_artifacts(
                tmp,
                self.mechaseed,
                self.bench,
                self.replay_rows,
                self.replay_coverage,
            )
            for name in (
                "mechaseed_200",
                "mutationbench_5000",
                "replay_100k_ticks",
                "replay_sample",
            ):
                self.assertIn(name, manifest)
                self.assertTrue(manifest[name]["sha256"])
                # Repo-relative POSIX path strings (the L-08 rule) —
                # write into the repo? No: paths recorded relative to
                # ROOT only when inside it; temp writes fall back to
                # the file name check below.
            for sub in (
                "mechaseed_200/README.md",
                "mutationbench_5000/README.md",
                "replay_100k_ticks/README.md",
            ):
                self.assertTrue((Path(tmp) / sub).exists())
            packed = Path(tmp) / "replay_100k_ticks" / "replay_100k_ticks.jsonl.gz"
            with gzip.open(packed, "rt", encoding="utf-8") as handle:
                rows = [json.loads(line) for line in handle]
            self.assertEqual(self.replay_rows, rows)


if __name__ == "__main__":
    unittest.main()
