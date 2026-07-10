import json
import sys
import tempfile
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
READABILITY = REPO_ROOT / "labs" / "readability_benchmark"
LIFECYCLE = REPO_ROOT / "labs" / "lifecycle_sim"
WFC = REPO_ROOT / "labs" / "wfc_grid"
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, GRID_GENOME, READABILITY, LIFECYCLE, WFC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from constrained_generator import build_constrained_corpus  # noqa: E402
from corpus_builder import build_seed_grids_16  # noqa: E402
from extended_descriptors import (  # noqa: E402
    _behavior_neediness,
    _symmetry_score,
    score_extended_candidate,
)
from learned_readability import extract_readability_features  # noqa: E402
from niche_scale_archive import (  # noqa: E402
    DOCUMENTED_REPERTOIRE_FIGURES,
    SCALE_BINS_PER_AXIS,
    SCALE_DESCRIPTOR_NAMES,
    TOTAL_SCALE_NICHES,
    build_niche_scale_report,
    build_scale_archive,
    derive_scale_bin_edges,
    insert_scale_candidate,
    measure_evaluation_unit,
    new_scale_archive,
    scale_archive_summary,
    scale_axis_values,
    scale_descriptor_for_values,
    write_niche_scale_artifacts,
)

from mecha_engine.archive import archive_summary, build_archive  # noqa: E402

from test_package_archive_parity import package_metrics_for  # noqa: E402


RNG_SEED = 20260709


def load_lcd_slip() -> dict:
    return json.loads(
        (REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )


def small_corpus(count: int = 24, rng_seed: int = RNG_SEED) -> list[dict]:
    return build_constrained_corpus(
        build_seed_grids_16(), count=count, rng_seed=rng_seed
    )


class ScaleGeometryTests(unittest.TestCase):
    def test_geometry_is_the_documented_first_pass_8x8x8(self):
        # deep-research.md "MAP-Elites archive test": three descriptor axes
        # in the first pass — symmetry, visual complexity, neediness — with
        # 8x8x8 niches.
        self.assertEqual(
            ["symmetry", "visual_complexity", "behavior_neediness"],
            SCALE_DESCRIPTOR_NAMES,
        )
        self.assertEqual(8, SCALE_BINS_PER_AXIS)
        self.assertEqual(512, TOTAL_SCALE_NICHES)

    def test_documented_figure_discrepancy_is_recorded_not_reconciled(self):
        # The dossier states both "8x8x8 niches" (= 512) and a "576-cell
        # repertoire"; the discrepancy is carried verbatim, never averaged.
        self.assertEqual(512, DOCUMENTED_REPERTOIRE_FIGURES["niches_8x8x8"])
        self.assertEqual(
            576, DOCUMENTED_REPERTOIRE_FIGURES["table_repertoire_cells"]
        )


class EdgeDerivationTests(unittest.TestCase):
    def test_octile_edges_linear_interpolation_exact_case(self):
        # n=17 values 1..17: h = (n-1)*i/8 = 2i lands on ranks exactly, so
        # edge_i = value at rank 2i = 2i + 1.
        values = [float(v) for v in range(1, 18)]
        edges = derive_scale_bin_edges(values)
        self.assertEqual([3.0, 5.0, 7.0, 9.0, 11.0, 13.0, 15.0], edges)

    def test_edges_are_order_invariant_and_monotone(self):
        values = [0.9, 0.1, 0.4, 0.7, 0.2, 0.65, 0.3, 0.85, 0.5, 0.15]
        edges = derive_scale_bin_edges(values)
        self.assertEqual(edges, derive_scale_bin_edges(list(reversed(values))))
        self.assertEqual(SCALE_BINS_PER_AXIS - 1, len(edges))
        self.assertEqual(edges, sorted(edges))

    def test_degenerate_distribution_yields_duplicate_edges(self):
        edges = derive_scale_bin_edges([0.5] * 40)
        self.assertEqual([0.5] * 7, edges)

    def test_empty_or_tiny_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            derive_scale_bin_edges([])
        with self.assertRaises(ValueError):
            derive_scale_bin_edges([1.0, 2.0])


class ScaleAxisValueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.slip = load_lcd_slip()
        cls.grids = build_seed_grids_16()[:6]

    def test_axis_values_come_from_the_canonical_surfaces(self):
        # No new statistics: symmetry and neediness are the calibrated
        # descriptor formulas; visual complexity is the readability feature
        # extractor's silhouette entropy (the dossier's named metric).
        for grid in self.grids:
            with self.subTest(grid_id=grid["grid_id"]):
                values = scale_axis_values(grid, slip_profile=self.slip)
                self.assertEqual(
                    round(_symmetry_score(grid), 6), values["symmetry"]
                )
                self.assertEqual(
                    extract_readability_features(grid)["silhouette_entropy"],
                    values["visual_complexity"],
                )
                self.assertEqual(
                    round(_behavior_neediness(grid, self.slip), 6),
                    values["behavior_neediness"],
                )

    def test_descriptor_bins_against_explicit_edges(self):
        edges = {
            "symmetry": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
            "visual_complexity": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
            "behavior_neediness": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
        }
        values = {
            "symmetry": 0.05,
            "visual_complexity": 0.3,  # boundary: value == edge -> lower bin
            "behavior_neediness": 0.95,
        }
        self.assertEqual(
            (0, 2, 7), scale_descriptor_for_values(values, edges)
        )


class ScaleArchiveMechanicsTests(unittest.TestCase):
    """The package's elite rule, verbatim, at the scale geometry."""

    @classmethod
    def setUpClass(cls):
        cls.grids = build_seed_grids_16()
        cls.invalid_grid = json.loads(
            next(
                (REPO_ROOT / "data" / "invalid_grids_16x16").glob("*.json")
            ).read_text(encoding="utf-8")
        )

    @staticmethod
    def _score(fitness: float) -> dict:
        return {"fitness": fitness}

    def test_empty_niche_accepts_first_valid_candidate(self):
        archive = new_scale_archive()
        archive = insert_scale_candidate(
            archive, self.grids[0], self._score(0.5), (1, 2, 3)
        )
        self.assertEqual(1, len(archive["elites"]))
        self.assertEqual(
            self.grids[0]["grid_id"], archive["elites"]["1,2,3"]["grid_id"]
        )
        self.assertEqual("inserted_empty_niche", archive["events"][-1]["event"])

    def test_strictly_higher_fitness_replaces_the_incumbent(self):
        archive = new_scale_archive()
        archive = insert_scale_candidate(
            archive, self.grids[0], self._score(0.5), (1, 2, 3)
        )
        archive = insert_scale_candidate(
            archive, self.grids[1], self._score(0.6), (1, 2, 3)
        )
        self.assertEqual(
            self.grids[1]["grid_id"], archive["elites"]["1,2,3"]["grid_id"]
        )
        self.assertEqual("replaced_elite", archive["events"][-1]["event"])

    def test_equal_fitness_keeps_the_incumbent(self):
        archive = new_scale_archive()
        archive = insert_scale_candidate(
            archive, self.grids[0], self._score(0.5), (1, 2, 3)
        )
        archive = insert_scale_candidate(
            archive, self.grids[1], self._score(0.5), (1, 2, 3)
        )
        self.assertEqual(
            self.grids[0]["grid_id"], archive["elites"]["1,2,3"]["grid_id"]
        )
        self.assertEqual("kept_incumbent_tie", archive["events"][-1]["event"])

    def test_lower_fitness_keeps_the_incumbent(self):
        archive = new_scale_archive()
        archive = insert_scale_candidate(
            archive, self.grids[0], self._score(0.5), (1, 2, 3)
        )
        archive = insert_scale_candidate(
            archive, self.grids[1], self._score(0.4), (1, 2, 3)
        )
        self.assertEqual(
            self.grids[0]["grid_id"], archive["elites"]["1,2,3"]["grid_id"]
        )
        self.assertEqual(
            "kept_incumbent_higher_fitness", archive["events"][-1]["event"]
        )

    def test_invalid_candidates_are_blocked_never_elites(self):
        archive = new_scale_archive()
        archive = insert_scale_candidate(
            archive, self.invalid_grid, self._score(0.9), (1, 2, 3)
        )
        self.assertEqual(0, len(archive["elites"]))
        self.assertEqual(1, archive["blocked_invalid_count"])
        self.assertEqual(
            "blocked_invalid_candidate", archive["events"][-1]["event"]
        )

    def test_descriptor_outside_geometry_is_rejected(self):
        archive = new_scale_archive()
        with self.assertRaises(ValueError):
            insert_scale_candidate(
                archive, self.grids[0], self._score(0.5), (8, 0, 0)
            )
        with self.assertRaises(ValueError):
            insert_scale_candidate(
                archive, self.grids[0], self._score(0.5), (0, 0)
            )

    def test_summary_arithmetic_is_consistent(self):
        archive = new_scale_archive()
        archive = insert_scale_candidate(
            archive, self.grids[0], self._score(0.5), (0, 0, 0)
        )
        archive = insert_scale_candidate(
            archive, self.grids[1], self._score(0.7), (7, 7, 7)
        )
        summary = scale_archive_summary(archive)
        self.assertEqual(512, summary["total_possible_niches"])
        self.assertEqual(2, summary["occupied_niches"])
        self.assertEqual(round(2 / 512, 6), summary["coverage"])
        self.assertEqual(0.7, summary["best_fitness"])
        self.assertEqual(round(1.2, 6), summary["qd_score"])
        self.assertEqual(round(0.6, 6), summary["mean_elite_fitness"])
        self.assertEqual(
            {"symmetry": 2, "visual_complexity": 2, "behavior_neediness": 2},
            summary["descriptor_bin_spread"],
        )


class PackageMechanicsParityTests(unittest.TestCase):
    """The scale mechanics ARE the package's mechanics — pinned.

    The lab archive, configured with the package's extended geometry and fed
    the package-identical corpus, must reproduce mecha_engine.archive's
    elites and summary exactly. The scale run then differs only in
    descriptor geometry, never in the elite rule.
    """

    @classmethod
    def setUpClass(cls):
        cls.slip = load_lcd_slip()
        # 8x8 Stage 0 corpus keeps this pin fast and reuses the proven
        # parity harness from test_package_archive_parity.
        from corpus_builder import build_seed_grids

        cls.candidates = build_constrained_corpus(
            build_seed_grids(), count=48, rng_seed=RNG_SEED, slip=cls.slip
        )
        cls.metrics = package_metrics_for(
            cls.candidates, cls.slip, rng_seed=RNG_SEED
        )
        cls.package_archive = build_archive(
            [{"grid": grid} for grid in cls.candidates], cls.metrics
        )
        cls.package_summary = archive_summary(cls.package_archive)
        cls.lab_archive = build_scale_archive(
            cls.candidates,
            slip_profile=cls.slip,
            rng_seed=RNG_SEED,
            geometry="extended_parity",
        )

    def test_elite_niches_and_winners_match_the_package(self):
        package_elites = self.package_archive["elites"]
        lab_elites = self.lab_archive["elites"]
        self.assertEqual(sorted(package_elites), sorted(lab_elites))
        for key, package_elite in package_elites.items():
            with self.subTest(niche=key):
                self.assertEqual(
                    package_elite["grid_id"], lab_elites[key]["grid_id"]
                )
                self.assertEqual(
                    package_elite["fitness"], lab_elites[key]["fitness"]
                )

    def test_summary_metrics_match_the_package(self):
        summary = scale_archive_summary(self.lab_archive)
        for field in (
            "occupied_niches",
            "coverage",
            "best_fitness",
            "mean_elite_fitness",
            "qd_score",
            "total_possible_niches",
            "candidate_count",
            "blocked_invalid_count",
            "descriptor_bin_spread",
        ):
            with self.subTest(field=field):
                self.assertEqual(self.package_summary[field], summary[field])


class NicheScaleReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_niche_scale_report(
            derivation_count=16,
            evaluation_count=24,
            rng_seed=RNG_SEED,
        )

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
        self.assertEqual("niche_scale_archive_stage0", self.report["artifact_id"])

    def test_edges_are_derived_not_hand_set(self):
        derivation = self.report["metrics"]["edge_derivation"]
        self.assertEqual(
            sorted(SCALE_DESCRIPTOR_NAMES), sorted(derivation["edges"])
        )
        for name in SCALE_DESCRIPTOR_NAMES:
            with self.subTest(axis=name):
                edges = derivation["edges"][name]
                self.assertEqual(SCALE_BINS_PER_AXIS - 1, len(edges))
                self.assertEqual(edges, sorted(edges))
                self.assertIn(
                    name, derivation["diagnostics"]
                )  # distinct-edge honesty per axis

    def test_populations_are_disjoint_and_recorded(self):
        populations = self.report["metrics"]["populations"]
        self.assertEqual(16, populations["derivation"]["candidate_count"])
        self.assertEqual(24, populations["evaluation"]["candidate_count"])
        self.assertNotEqual(
            populations["derivation"]["rng_seed"],
            populations["evaluation"]["rng_seed"],
        )
        for split in ("derivation", "evaluation"):
            self.assertIn("composition", populations[split])

    def test_archive_summary_and_coverage_arithmetic(self):
        summary = self.report["metrics"]["archive"]
        self.assertEqual(512, summary["total_possible_niches"])
        self.assertEqual(
            round(summary["occupied_niches"] / 512, 6), summary["coverage"]
        )
        self.assertLessEqual(
            summary["occupied_niches"], summary["candidate_count"]
        )

    def test_report_body_carries_no_wall_clock(self):
        self.assertNotIn("measured", self.report)
        self.assertNotIn("measured", self.report["metrics"])

    def test_artifact_writer_emits_report_and_measured_section(self):
        measured = measure_evaluation_unit(sample_count=4, rng_seed=RNG_SEED)
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            write_niche_scale_artifacts(output_dir, self.report, measured)
            payload = json.loads(
                (output_dir / "niche_scale_archive_stage0.json").read_text(
                    encoding="utf-8"
                )
            )
        self.assertEqual(self.report["artifact_id"], payload["artifact_id"])
        self.assertIn("measured", payload)
        self.assertIn("context", payload["measured"])


class EvaluationUnitWallClockTests(unittest.TestCase):
    def test_measurement_shape_projections_and_bound_fields(self):
        measured = measure_evaluation_unit(sample_count=4, rng_seed=RNG_SEED)
        self.assertIn("context", measured)
        unit = measured["evaluation_unit"]
        self.assertEqual(4, unit["sample_count"])
        self.assertGreater(unit["mean_ms_per_evaluation"], 0)
        projections = measured["projections"]
        self.assertIn("evaluations_20k_s", projections)
        self.assertIn("evaluations_50k_s", projections)
        # Projections are linear in the measured unit — machine-dependent
        # values are never pinned, only the arithmetic.
        self.assertEqual(
            round(unit["mean_ms_per_evaluation"] * 20_000 / 1000, 2),
            projections["evaluations_20k_s"],
        )
        self.assertEqual(
            round(unit["mean_ms_per_evaluation"] * 50_000 / 1000, 2),
            projections["evaluations_50k_s"],
        )


class Stage0ArtifactConsistencyTests(unittest.TestCase):
    """Pins the committed full-scale evidence artifact.

    The E1 claim — archive mechanics proven at HUNDREDS of occupied
    niches — is earned by the full-scale artifact, not asserted in prose.
    """

    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(
            (
                REPO_ROOT / "data" / "archives" / "niche_scale_archive_stage0.json"
            ).read_text(encoding="utf-8")
        )

    def test_full_scale_archive_occupies_hundreds_of_niches(self):
        summary = self.artifact["metrics"]["archive"]
        self.assertGreaterEqual(summary["occupied_niches"], 200)
        self.assertEqual(512, summary["total_possible_niches"])
        self.assertEqual(
            round(summary["occupied_niches"] / 512, 6), summary["coverage"]
        )

    def test_artifact_records_edges_and_measured_section(self):
        self.assertEqual(
            sorted(SCALE_DESCRIPTOR_NAMES),
            sorted(self.artifact["metrics"]["edge_derivation"]["edges"]),
        )
        self.assertIn("measured", self.artifact)
        self.assertIn("projections", self.artifact["measured"])


if __name__ == "__main__":
    unittest.main()
