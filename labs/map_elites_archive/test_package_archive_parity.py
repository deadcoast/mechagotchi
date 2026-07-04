"""Parity pin: lab MAP-Elites archive vs promoted mecha_engine.archive.

Runs the Stage 0 lab archive (flat imports, the authoritative calibrated
research behavior: seven descriptor axes, cap-normalized mutation
stability, the morphology-derived lifecycle stress probe, the pinned
fitness weights, and the strictly-higher-fitness elite rule) and the
promoted package archive (mecha_engine.archive through the package src
layout) over the same candidate corpus, SLIP profile, and RNG seeds, and
asserts identical descriptors, elites, and summary metrics — including the
pinned Stage 0 artifact numbers from
data/archives/map_elites_extended_stage0.json.

Documented equivalence scope: the package factors readability, SLIP
alignment, and lifecycle context as per-candidate metrics *inputs*
(interface spec, "archive" inputs), so this test feeds the lab proxy
readability scorer output and the lab SLIP alignment result into
``metrics_by_grid_id`` while the package computes morphology, mutation
stability, behavior neediness, and stress-probe lifecycle survival
internally (through ``mecha_engine.lifecycle``) with the same per-candidate
``rng_seed + index`` the lab uses. Package elite entries are a documented
superset of the lab entries (they add the grid payload, validation, and
provenance to satisfy the archive-candidate data contract), so grid_id,
fitness, descriptor values, per-axis descriptor metrics, and fitness
components are compared field-by-field. The package additionally blocks
invalid candidates from elite status; the Stage 0 corpus is fully valid,
so blocked/skipped counts are asserted to be zero. The extended
best-fitness/QD numbers pinned here are the calibrated Stage 0 values
(research/experiment_reports/2026-07-04-descriptor-axis-calibration.md
intentionally updated the archive contract gate's original table).

Direction note: labs may import the package for regression evidence; the
reverse (package importing labs) stays forbidden by the archive contract
gate, and this file lives on the lab side precisely so the package tree
keeps zero lab references.
"""

import json
import sys
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
READABILITY = REPO_ROOT / "labs" / "readability_benchmark"
LIFECYCLE = REPO_ROOT / "labs" / "lifecycle_sim"
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, GRID_GENOME, READABILITY, LIFECYCLE]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from constrained_generator import build_constrained_corpus  # noqa: E402
from corpus_builder import build_seed_grids  # noqa: E402
from darwin_archive import (  # noqa: E402
    build_map_elites_archive,
    descriptor_for_grid,
    score_grid,
)
from extended_descriptors import (  # noqa: E402
    DESCRIPTOR_NAMES,
    build_extended_map_elites_archive,
    extended_descriptor_for_grid,
    score_extended_candidate,
)
from readability_benchmark import score_readability  # noqa: E402
from slip import is_grid_aligned  # noqa: E402

from mecha_engine.archive import (  # noqa: E402
    archive_summary,
    build_archive,
    descriptor_for_candidate,
    score_candidate,
)


STAGE0_RNG_SEED = 20260512
STAGE0_CANDIDATE_COUNT = 160
STAGE0_LIFECYCLE_TICKS = 24
# Pinned calibrated Stage 0 extended archive metrics
# (data/archives/map_elites_extended_stage0.json).
STAGE0_EXTENDED = {
    "occupied_niches": 83,
    "coverage": 0.001062,
    "best_fitness": 0.972366,
    "mean_elite_fitness": 0.868313,
    "qd_score": 72.069987,
    "total_possible_niches": 78125,
    "descriptor_dimensions": 7,
    "descriptor_bin_spread": {
        "body_mass": 3,
        "sensor_count": 4,
        "symmetry": 4,
        "readability": 3,
        "lifecycle_survival": 2,
        "mutation_stability": 5,
        "behavior_neediness": 2,
    },
}
# Pinned Stage 0 legacy baseline metrics
# (data/archives/map_elites_stage0.json: 200 candidates, rng_seed 818).
STAGE0_BASELINE = {
    "occupied_niches": 24,
    "coverage": 0.192,
    "scalar_top_k": 20,
    "scalar_top_occupied_niches": 7,
}


def load_lcd_slip() -> dict:
    return json.loads(
        (REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


def package_metrics_for(
    candidates: list[dict],
    slip: dict | None,
    *,
    rng_seed: int = STAGE0_RNG_SEED,
    lifecycle_ticks: int = STAGE0_LIFECYCLE_TICKS,
) -> dict:
    """Metrics bundles matching the lab archive's per-candidate context."""
    metrics_by_grid_id = {}
    for index, grid in enumerate(candidates):
        metrics: dict = {
            "readability": score_readability(grid),
            "lifecycle_ticks": lifecycle_ticks,
            "rng_seed": rng_seed + index,
        }
        if slip is not None:
            metrics["slip_profile"] = slip
            metrics["slip_alignment"] = {"ok": is_grid_aligned(grid, slip).ok}
        metrics_by_grid_id[grid["grid_id"]] = metrics
    return metrics_by_grid_id


class PackageArchiveParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slip = load_lcd_slip()
        seeds = build_seed_grids()
        cls.candidates = build_constrained_corpus(
            seeds,
            count=STAGE0_CANDIDATE_COUNT,
            rng_seed=STAGE0_RNG_SEED,
            slip=cls.slip,
        )
        cls.lab_archive = build_extended_map_elites_archive(
            cls.candidates,
            slip_profile=cls.slip,
            lifecycle_ticks=STAGE0_LIFECYCLE_TICKS,
            rng_seed=STAGE0_RNG_SEED,
        )
        cls.metrics_by_grid_id = package_metrics_for(cls.candidates, cls.slip)
        cls.package_archive = build_archive(
            [{"grid": grid} for grid in cls.candidates], cls.metrics_by_grid_id
        )
        cls.package_summary = archive_summary(cls.package_archive)

    def test_corpus_grid_ids_are_unique(self):
        self.assertEqual(STAGE0_CANDIDATE_COUNT, len(self.metrics_by_grid_id))

    def test_extended_descriptor_parity_per_candidate(self):
        for index, grid in enumerate(self.candidates[:20]):
            with self.subTest(grid_id=grid["grid_id"]):
                lab_descriptor = extended_descriptor_for_grid(
                    grid,
                    slip_profile=self.slip,
                    lifecycle_ticks=STAGE0_LIFECYCLE_TICKS,
                    rng_seed=STAGE0_RNG_SEED + index,
                )
                package_descriptor = descriptor_for_candidate(
                    {"grid": grid}, self.metrics_by_grid_id[grid["grid_id"]]
                )
                self.assertEqual(tuple(lab_descriptor["values"]), package_descriptor)

    def test_extended_score_parity_per_candidate(self):
        for index, grid in enumerate(self.candidates[:20]):
            with self.subTest(grid_id=grid["grid_id"]):
                lab_score = score_extended_candidate(
                    grid,
                    slip_profile=self.slip,
                    lifecycle_ticks=STAGE0_LIFECYCLE_TICKS,
                    rng_seed=STAGE0_RNG_SEED + index,
                )
                lab_descriptor = extended_descriptor_for_grid(
                    grid,
                    slip_profile=self.slip,
                    lifecycle_ticks=STAGE0_LIFECYCLE_TICKS,
                    rng_seed=STAGE0_RNG_SEED + index,
                )
                package_score = score_candidate(
                    {"grid": grid}, self.metrics_by_grid_id[grid["grid_id"]]
                )
                self.assertEqual(lab_score["fitness"], package_score["fitness"])
                self.assertEqual(lab_score["components"], package_score["components"])
                self.assertEqual(
                    lab_descriptor["metrics"], package_score["descriptor_metrics"]
                )
                self.assertEqual(
                    lab_score["lifecycle"]["survival_ratio"],
                    package_score["lifecycle"]["survival_ratio"],
                )

    def test_extended_archive_elites_parity(self):
        lab_elites = self.lab_archive["elites"]
        package_elites = self.package_archive["elites"]
        self.assertEqual(sorted(lab_elites), sorted(package_elites))
        for key, lab_elite in lab_elites.items():
            package_elite = package_elites[key]
            with self.subTest(niche=key):
                self.assertEqual(lab_elite["grid_id"], package_elite["grid_id"])
                self.assertEqual(lab_elite["fitness"], package_elite["fitness"])
                self.assertEqual(
                    list(lab_elite["descriptor"]["values"]),
                    package_elite["descriptor"]["values"],
                )
                self.assertEqual(
                    lab_elite["descriptor"]["metrics"],
                    package_elite["descriptor"]["metrics"],
                )
                self.assertEqual(
                    lab_elite["score_components"],
                    package_elite["fitness_components"],
                )
                # Documented package superset: elites carry the archive
                # candidate contract fields the lab entries omit.
                self.assertTrue(package_elite["validation"]["ok"])
                self.assertIn("grid", package_elite)
                self.assertIn("provenance", package_elite)

    def test_extended_summary_parity_with_lab_archive(self):
        summary = self.package_summary
        lab = self.lab_archive
        self.assertEqual(lab["descriptor_names"], summary["descriptor_names"])
        self.assertEqual(DESCRIPTOR_NAMES, summary["descriptor_names"])
        self.assertEqual(
            lab["descriptor_cardinalities"], summary["descriptor_cardinalities"]
        )
        self.assertEqual(
            lab["descriptor_dimensions"], summary["descriptor_dimensions"]
        )
        self.assertEqual(
            lab["total_possible_niches"], summary["total_possible_niches"]
        )
        self.assertEqual(lab["occupied_niches"], summary["occupied_niches"])
        self.assertEqual(lab["coverage"], summary["coverage"])
        self.assertEqual(lab["best_fitness"], summary["best_fitness"])
        self.assertEqual(lab["mean_elite_fitness"], summary["mean_elite_fitness"])
        self.assertEqual(lab["qd_score"], summary["qd_score"])
        self.assertEqual(
            lab["descriptor_bin_spread"], summary["descriptor_bin_spread"]
        )

    def test_extended_summary_reproduces_pinned_stage0_artifact(self):
        summary = self.package_summary
        for field, expected in STAGE0_EXTENDED.items():
            with self.subTest(field=field):
                self.assertEqual(expected, summary[field])
        artifact = json.loads(
            (REPO_ROOT / "data" / "archives" / "map_elites_extended_stage0.json")
            .read_text(encoding="utf-8")
        )["archive"]
        for field in STAGE0_EXTENDED:
            with self.subTest(field=field, source="stage0_artifact"):
                self.assertEqual(artifact[field], summary[field])

    def test_stage0_corpus_has_no_blocked_or_skipped_candidates(self):
        summary = self.package_summary
        self.assertEqual(STAGE0_CANDIDATE_COUNT, summary["candidate_count"])
        self.assertEqual(0, summary["blocked_invalid_count"])
        self.assertEqual(0, summary["skipped_missing_metrics_count"])

    def test_readability_calibration_gate_stays_visible_and_unlocked(self):
        summary = self.package_summary
        self.assertIn("proxy", summary["readability_calibration_status"])
        self.assertIn("not_collected", summary["readability_calibration_status"])
        self.assertFalse(summary["final_descriptor_thresholds_locked"])

    def test_baseline_descriptor_and_occupancy_parity_with_legacy_archive(self):
        candidates = build_constrained_corpus(
            build_seed_grids(), count=200, rng_seed=818
        )
        legacy = build_map_elites_archive(candidates)
        metrics_by_grid_id = package_metrics_for(candidates, None)
        package_archive = build_archive(
            [{"grid": grid} for grid in candidates],
            metrics_by_grid_id,
            mode="baseline",
        )
        summary = archive_summary(package_archive)

        for grid in candidates[:20]:
            with self.subTest(grid_id=grid["grid_id"]):
                self.assertEqual(
                    descriptor_for_grid(grid),
                    descriptor_for_candidate(
                        {"grid": grid},
                        metrics_by_grid_id[grid["grid_id"]],
                        mode="baseline",
                    ),
                )

        self.assertEqual(3, summary["descriptor_dimensions"])
        self.assertEqual(125, summary["total_possible_niches"])
        self.assertEqual(legacy["occupied_niches"], summary["occupied_niches"])
        self.assertEqual(STAGE0_BASELINE["occupied_niches"], summary["occupied_niches"])
        self.assertEqual(STAGE0_BASELINE["coverage"], summary["coverage"])
        # Documented semantic equivalence: niche geometry (and therefore
        # occupancy/coverage) is identical, but per-niche winners follow the
        # package's extended Stage 0 fitness, not the legacy scalar
        # score_grid, so elite identities are not compared here.
        self.assertEqual(sorted(legacy["elites"]), sorted(package_archive["elites"]))

        # Scalar top-k stays a comparator (test-side, legacy Stage 0
        # scoring): the top 20 by scalar fitness reach only 7 baseline
        # niches while the package archive holds 24.
        scalar_top = sorted(
            candidates, key=lambda grid: score_grid(grid), reverse=True
        )[: STAGE0_BASELINE["scalar_top_k"]]
        scalar_niches = {
            descriptor_for_candidate(
                {"grid": grid}, metrics_by_grid_id[grid["grid_id"]], mode="baseline"
            )
            for grid in scalar_top
        }
        self.assertEqual(
            STAGE0_BASELINE["scalar_top_occupied_niches"], len(scalar_niches)
        )
        self.assertGreater(summary["occupied_niches"], len(scalar_niches))


if __name__ == "__main__":
    unittest.main()
