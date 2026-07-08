import json
import sys
import tempfile
import unittest
from pathlib import Path

from corpus_builder import build_seed_grids
from grid_helpers import PALETTES
from invariant_scaling import (
    FLOOR_CANDIDATES,
    RATIFIED_FLOOR_16,
    body_core_min_cells,
    build_invariant_scaling_report,
    build_pilot_grids,
    chance_connectivity_experiment,
    evaluate_floor_candidates,
    noise_largest_component_experiment,
    population_census,
    upscale_grid_2x,
    write_invariant_scaling_artifacts,
)
from validator import validate_grid

PACKAGE_SRC = Path(__file__).resolve().parents[2] / "packages" / "mecha_engine" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from mecha_engine.archive._metrics import symmetry_score as package_symmetry_score  # noqa: E402
from mecha_engine.genome import validate_grid as package_validate_grid  # noqa: E402


def _core_mass(grid: dict) -> int:
    return sum(
        1
        for organ_name, organ in grid["organs"].items()
        if organ.get("role") == "body_core" and organ.get("required") is True
        for _ in organ["cells"]
    )


class PilotExemplarTests(unittest.TestCase):
    def setUp(self):
        self.pilots = build_pilot_grids()

    def test_ten_pilots_all_valid_against_lab_and_package_validators(self):
        self.assertEqual(len(self.pilots), 10)
        for grid in self.pilots:
            lab_result = validate_grid(grid)
            package_result = package_validate_grid(grid)
            self.assertTrue(lab_result.ok, f"{grid['grid_id']}: {lab_result.errors}")
            self.assertTrue(
                package_result.ok, f"{grid['grid_id']}: {package_result.errors}"
            )

    def test_pilots_are_16x16_with_exactly_one_anchor(self):
        for grid in self.pilots:
            self.assertEqual(grid["grid_size"], [16, 16], grid["grid_id"])
            anchors = sum(
                1 for cell in grid["cells"] if cell["animation_anchor"] is True
            )
            self.assertEqual(anchors, 1, grid["grid_id"])

    def test_pilots_cover_all_five_palettes_twice(self):
        counts: dict[str, int] = {}
        for grid in self.pilots:
            counts[grid["palette"]["palette_id"]] = (
                counts.get(grid["palette"]["palette_id"], 0) + 1
            )
        self.assertEqual(counts, {palette: 2 for palette in PALETTES})

    def test_pilots_have_sensor_pairs(self):
        for grid in self.pilots:
            eye_cells = [cell for cell in grid["cells"] if cell["role"] == "eye"]
            self.assertGreaterEqual(len(eye_cells), 2, grid["grid_id"])

    def test_pilots_exercise_the_dr0015_vocabulary(self):
        roles = {cell["role"] for grid in self.pilots for cell in grid["cells"]}
        for role in [
            "body",
            "shell",
            "joint",
            "limb",
            "eye",
            "mouth",
            "antenna",
            "sensor",
            "decoration",
            "effect",
        ]:
            self.assertIn(role, roles)

    def test_pilot_core_masses_probe_the_floor_and_the_ceiling(self):
        masses = sorted(_core_mass(grid) for grid in self.pilots)
        self.assertEqual(masses[0], RATIFIED_FLOOR_16)
        self.assertGreaterEqual(masses[-1], 55)
        self.assertGreaterEqual(sum(1 for mass in masses if mass >= 40), 3)

    def test_pilot_symmetry_spans_low_mid_high(self):
        scores = [package_symmetry_score(grid) for grid in self.pilots]
        self.assertLess(min(scores), 0.4)
        self.assertGreaterEqual(sum(1 for score in scores if score >= 0.9), 6)
        self.assertTrue(any(0.5 <= score <= 0.85 for score in scores))

    def test_pilots_are_morphologically_distinct(self):
        signatures = {
            tuple(sorted((cell["x"], cell["y"], cell["role"]) for cell in grid["cells"]))
            for grid in self.pilots
        }
        self.assertEqual(len(signatures), 10)


class UpscaleControlTests(unittest.TestCase):
    def setUp(self):
        self.seeds = build_seed_grids()
        self.controls = [upscale_grid_2x(grid) for grid in self.seeds]

    def test_controls_are_valid_16x16_with_exactly_one_anchor(self):
        self.assertEqual(len(self.controls), 50)
        for control in self.controls:
            result = validate_grid(control)
            self.assertTrue(result.ok, f"{control['grid_id']}: {result.errors}")
            self.assertEqual(control["grid_size"], [16, 16])
            anchors = sum(
                1 for cell in control["cells"] if cell["animation_anchor"] is True
            )
            self.assertEqual(anchors, 1, control["grid_id"])

    def test_upscale_multiplies_core_mass_by_exactly_four(self):
        for seed, control in zip(self.seeds, self.controls):
            self.assertEqual(_core_mass(control), 4 * _core_mass(seed))

    def test_upscale_preserves_symmetry_score(self):
        for seed, control in zip(self.seeds, self.controls):
            self.assertAlmostEqual(
                package_symmetry_score(control),
                package_symmetry_score(seed),
                places=9,
                msg=seed["grid_id"],
            )

    def test_control_ids_are_schema_legal(self):
        for control in self.controls:
            self.assertLessEqual(len(control["grid_id"]), 64)
            self.assertTrue(control["grid_id"].endswith("_up16"))


class NoiseExperimentTests(unittest.TestCase):
    def test_chance_connectivity_is_deterministic(self):
        first = chance_connectivity_experiment()
        second = chance_connectivity_experiment()
        self.assertEqual(first, second)

    def test_connectivity_discrimination_strengthens_with_scale(self):
        rates = chance_connectivity_experiment()
        self.assertLess(rates["16x16"]["k18"], rates["8x8"]["k4"])
        self.assertLess(rates["16x16"]["k18"], 0.02)

    def test_largest_component_experiment_is_deterministic(self):
        first = noise_largest_component_experiment()
        second = noise_largest_component_experiment()
        self.assertEqual(first, second)


class FloorLawTests(unittest.TestCase):
    def test_law_reproduces_both_ratified_scales(self):
        self.assertEqual(body_core_min_cells(8, 8), 4)
        self.assertEqual(body_core_min_cells(16, 16), RATIFIED_FLOOR_16)

    def test_law_is_monotonic_in_area_and_floored_at_four(self):
        self.assertEqual(body_core_min_cells(8, 8), 4)
        previous = 0
        for size in [8, 12, 16, 24, 32, 64]:
            value = body_core_min_cells(size, size)
            self.assertGreaterEqual(value, max(4, previous))
            previous = value

    def test_candidate_evaluation_adopts_the_documented_floor(self):
        pilots = build_pilot_grids()
        controls = [upscale_grid_2x(grid) for grid in build_seed_grids()]
        rows = evaluate_floor_candidates(pilots, controls)
        self.assertEqual([row["floor"] for row in rows], FLOOR_CANDIDATES)
        by_floor = {row["floor"]: row for row in rows}
        self.assertEqual(by_floor[RATIFIED_FLOOR_16]["verdict"], "adopt")
        for floor in [4, 8]:
            self.assertEqual(by_floor[floor]["verdict"], "reject_fraction_band")
        self.assertEqual(by_floor[24]["verdict"], "reject_fraction_band")
        for row in rows:
            self.assertTrue(row["pilots_pass"] or row["floor"] > RATIFIED_FLOOR_16)
            self.assertTrue(row["controls_pass"])


class ReportTests(unittest.TestCase):
    def test_report_is_deterministic_and_complete(self):
        report = build_invariant_scaling_report()
        again = build_invariant_scaling_report()
        self.assertEqual(json.dumps(report, sort_keys=True), json.dumps(again, sort_keys=True))
        for key in [
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
        ]:
            self.assertIn(key, report)
        self.assertEqual(report["artifact_id"], "invariant_scaling_16x16_stage0")
        self.assertEqual(report["metrics"]["ratified"]["floor_16x16"], RATIFIED_FLOOR_16)
        self.assertTrue(report["blocked_states"])

    def test_census_reports_the_three_populations(self):
        report = build_invariant_scaling_report()
        populations = report["metrics"]["populations"]
        self.assertEqual(
            sorted(populations),
            ["pilot_16x16", "seed_8x8", "upscaled_16x16_control"],
        )
        self.assertEqual(populations["seed_8x8"]["count"], 50)
        self.assertEqual(populations["upscaled_16x16_control"]["count"], 50)
        self.assertEqual(populations["pilot_16x16"]["count"], 10)
        self.assertEqual(populations["pilot_16x16"]["core_mass"]["min"], RATIFIED_FLOOR_16)

    def test_census_paths_and_fractions_are_sane(self):
        census = population_census(build_pilot_grids())
        self.assertGreater(census["occupancy_fraction"]["max"], 0.3)
        self.assertLess(census["occupancy_fraction"]["max"], 0.5)
        self.assertEqual(census["core_8connected_fraction"], 1.0)

    def test_artifact_writer_emits_report_and_pilot_corpus(self):
        report = build_invariant_scaling_report()
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "grid_genome"
            pilot_dir = output_dir / "pilot_16x16"
            write_invariant_scaling_artifacts(output_dir, report, pilot_dir)
            stage0 = output_dir / "invariant_scaling_16x16_stage0.json"
            self.assertTrue(stage0.exists())
            round_trip = json.loads(stage0.read_text(encoding="utf-8"))
            self.assertEqual(round_trip["artifact_id"], "invariant_scaling_16x16_stage0")
            pilot_files = sorted(pilot_dir.glob("mg_pilot16_*.json"))
            self.assertEqual(len(pilot_files), 10)
            self.assertTrue((pilot_dir / "README.md").exists())
            for path in pilot_files:
                grid = json.loads(path.read_text(encoding="utf-8"))
                self.assertTrue(validate_grid(grid).ok, path.name)


if __name__ == "__main__":
    unittest.main()
