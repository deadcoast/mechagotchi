"""X5: actual ordered admission observations preserve complete old outputs.

Pins were measured BEFORE either runtime source changed on 2026-10-06,
HEAD d4b4337; complete outputs and source identities are retained under
.development/x5/runtime/before-*.json. These pins compare complete archives
and reports, including every elite, rather than two calls to new code.
"""
import copy
import hashlib
import importlib
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages/mecha_engine/src"))
import mecha_engine_runtime_loop as lab
from corpus_builder import build_seed_grids, build_seed_grids_16
from readability_benchmark import score_readability
from mecha_engine.generation import train_generation_model
from mecha_engine.genome import validate_grid
from mecha_engine.repair import train_repair_model
from mecha_engine.runtime import evolve
from mecha_engine.slip import is_grid_aligned

PACKAGE = importlib.import_module("mecha_engine.runtime.evolve")
CONFIG = dict(generations=2, population=2, damage_cycles=1, ticks=4,
              dropout_rate=0.2, rng_seed=20260512)
BEFORE_SOURCE_SHA256 = {
    "package_none": "06bdda781a0649ef9482869a4ed6584b57aafd2692c3faeef84ac543170aa7b1",
    "package_empty": "c6cd986df70e1fd3239069bbc94ea002a76c9f5ff2e3f4740ad00751f080e8d5",
    "package_ordered_duplicates": "7c604a89fce1cc7d3e006532084cded6c31619b0878a43bdf20814ce28287844",
    "package_size_rejected": "8fcc184bb259853d620b8729557709ef80a0fa677a118215a36b19252f885626",
    "lab_none": "1c13c0161b2557bf596f2352289469773f2d382f42fcf9507e738a0cf9dd66a9",
    "lab_empty_directory": "633813877a8acea8fc9488b577014a89a68d62228d93d8c11489335ebd4356bc",
    "lab_ordered_directory": "9e07718caffe05cd1155d16dcbbe5014e11f8201ee6dcf3d75a6c5eac5a59360",
}


def complete_digest(output, directory=None):
    if directory is not None:
        assert output[1]["workshop_grids_dir"] == str(directory)
        output = copy.deepcopy(output)
        output[1]["workshop_grids_dir"] = "<temporary-founder-directory>"
    payload = json.dumps(output, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class AdmissionObserverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seeds = build_seed_grids()
        cls.slip = json.loads((ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(encoding="utf-8"))
        cls.generation = train_generation_model(cls.seeds)
        cls.repair = train_repair_model(cls.seeds[:40], epochs=2, rng_seed=CONFIG["rng_seed"])
        aligned = [grid for grid in cls.seeds if is_grid_aligned(grid, cls.slip).ok]
        good, other = copy.deepcopy(aligned[:2])
        rejected = copy.deepcopy(good)
        rejected["palette"]["palette_id"] = "gameboy_gray"
        size = copy.deepcopy(next(grid for grid in build_seed_grids_16()
                                  if validate_grid(grid).ok and is_grid_aligned(grid, cls.slip).ok))
        invalid = copy.deepcopy(good)
        invalid["cells"][0]["x"] = 99
        cls.founders = [good, rejected, other, size, invalid]
        for grid in cls.founders:
            grid["grid_id"] = "x5_duplicate"

    def package(self, founders=None, **kwargs):
        return evolve(self.seeds, self.slip, self.generation, self.repair,
                      readability_scorer=score_readability, founder_grids=founders,
                      **CONFIG, **kwargs)

    def laboratory(self, **kwargs):
        archives = []
        summary = lab.archive_summary
        def capture(archive):
            archives.append(copy.deepcopy(archive))
            return summary(archive)
        with patch.object(lab, "archive_summary", side_effect=capture):
            report = lab.run_mecha_engine_evolution_loop(repair_epochs=2, **CONFIG, **kwargs)
        return archives[-1], report

    def write_founders(self, directory):
        for ordinal, grid in enumerate(self.founders):
            (directory / f"{ordinal:02d}.json").write_text(json.dumps(grid), encoding="utf-8")
        (directory / "ignore.bak.json").write_text("invalid JSON deliberately skipped", encoding="utf-8")

    def test_package_complete_pre_source_results_with_observer_off_none_and_on(self):
        cases = {"package_none": None, "package_empty": [],
                 "package_ordered_duplicates": self.founders,
                 "package_size_rejected": [self.founders[3]]}
        for name, founders in cases.items():
            for option in ({}, {"admission_callback": None}, {"admission_callback": lambda event: None}):
                with self.subTest(case=name, observer=list(option)):
                    self.assertEqual(BEFORE_SOURCE_SHA256[name], complete_digest(self.package(founders, **option)))

    def test_lab_complete_pre_source_directory_results_are_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            for option in ({}, {"admission_callback": None}, {"admission_callback": lambda event: None}):
                with self.subTest(case="lab_none", observer=list(option)):
                    self.assertEqual(BEFORE_SOURCE_SHA256["lab_none"], complete_digest(self.laboratory(**option)))
                with self.subTest(case="lab_empty_directory", observer=list(option)):
                    self.assertEqual(BEFORE_SOURCE_SHA256["lab_empty_directory"],
                                     complete_digest(self.laboratory(workshop_grids_dir=directory, **option), directory))
            self.write_founders(directory)
            complete_plain = self.laboratory(workshop_grids_dir=directory)
            self.assertEqual(complete_plain, self.laboratory(workshop_grids_dir=directory, admission_callback=lambda event: None))
            for option in ({}, {"admission_callback": None}, {"admission_callback": lambda event: None}):
                with self.subTest(case="lab_ordered_directory", observer=list(option)):
                    self.assertEqual(BEFORE_SOURCE_SHA256["lab_ordered_directory"],
                                     complete_digest(self.laboratory(workshop_grids_dir=directory, **option), directory))

    def test_lab_direct_founders_match_existing_package_verdicts_and_elites(self):
        events = []
        archive, report = self.package(self.founders)
        lab_archive, lab_report = self.laboratory(founder_grids=self.founders, admission_callback=events.append)
        self.assertEqual(archive, lab_archive)
        self.assertEqual(["x5_duplicate"] * 2, report["founders"]["admitted_ids"])
        self.assertEqual([True, False, True, False, False], [event["admitted"] for event in events])
        self.assertEqual(report["founders"]["rejected"], [
            {"grid_id": event["grid_id"], "errors": event["rejection_errors"]}
            for event in events if not event["admitted"]])
        self.assertIsNone(lab_report["workshop_grids_dir"])

    def test_duplicate_occurrences_and_actual_errors_match_lab_and_package(self):
        package_events, lab_events = [], []
        archive, report = self.package(self.founders, admission_callback=package_events.append)
        lab_archive, _ = self.laboratory(founder_grids=self.founders, admission_callback=lab_events.append)
        self.assertEqual(package_events, lab_events)
        self.assertEqual(archive, lab_archive)
        self.assertEqual(list(range(5)), [event["submission_index"] for event in package_events])
        self.assertEqual(["x5_duplicate"] * 5, [event["grid_id"] for event in package_events])
        self.assertEqual([True, False, True, False, False], [event["admitted"] for event in package_events])
        self.assertNotEqual(self.founders[0], self.founders[2])
        for event in package_events:
            self.assertEqual({"submission_index", "grid_id", "admitted", "rejection_errors"}, set(event))
            if event["admitted"]:
                self.assertIsNone(event["rejection_errors"])
        self.assertEqual([row["errors"] for row in report["founders"]["rejected"]],
                         [event["rejection_errors"] for event in package_events if not event["admitted"]])
        self.assertEqual(["founder grid is 16x16 but the era runs at 8x8"], package_events[3]["rejection_errors"])
        self.assertTrue(any("palette" in error for error in package_events[1]["rejection_errors"]))
        self.assertTrue(package_events[4]["rejection_errors"])

    def test_callback_mutation_cannot_change_inputs_errors_or_complete_results(self):
        before = copy.deepcopy((self.seeds, self.slip, self.generation, self.repair, self.founders))
        rng = random.getstate()
        for run in (lambda **kw: self.package(self.founders, **kw),
                    lambda **kw: self.laboratory(founder_grids=self.founders, **kw)):
            expected = run()
            retained = []
            def mutate(event):
                retained.append(copy.deepcopy(event))
                if event["rejection_errors"] is not None:
                    event["rejection_errors"].clear()
                event.clear()
            self.assertEqual(expected, run(admission_callback=mutate))
            self.assertEqual(5, len(retained))
            self.assertTrue(retained[3]["rejection_errors"])
        self.assertEqual(before, (self.seeds, self.slip, self.generation, self.repair, self.founders))
        self.assertEqual(rng, random.getstate())

    def test_observes_existing_verdict_once_before_any_candidate_generation(self):
        for module, run in ((PACKAGE, lambda **kw: self.package(self.founders, **kw)),
                            (lab, lambda **kw: self.laboratory(founder_grids=self.founders, **kw))):
            events = []
            with patch.object(module, "validate_grid", wraps=module.validate_grid) as validate, \
                 patch.object(module, "generate_candidate", wraps=module.generate_candidate) as generate:
                def observe(event):
                    self.assertEqual(event["submission_index"] + 1, validate.call_count)
                    self.assertEqual(0, generate.call_count)
                    events.append(event)
                run(admission_callback=observe)
                self.assertEqual(5, len(events))
                self.assertEqual(4, generate.call_count)

    def test_callback_exception_propagates_before_evolution_and_preserves_inputs(self):
        class StopAdmission(Exception):
            pass
        before = copy.deepcopy((self.seeds, self.slip, self.generation, self.repair, self.founders))
        for module, run in ((PACKAGE, lambda **kw: self.package(self.founders, **kw)),
                            (lab, lambda **kw: self.laboratory(founder_grids=self.founders, **kw))):
            seen = []
            def stop(event):
                seen.append(event)
                if event["submission_index"] == 1:
                    raise StopAdmission("foreground cancellation")
            with patch.object(module, "generate_candidate", wraps=module.generate_candidate) as generate:
                with self.assertRaisesRegex(StopAdmission, "foreground cancellation"):
                    run(admission_callback=stop)
                generate.assert_not_called()
            self.assertEqual([0, 1], [event["submission_index"] for event in seen])
        self.assertEqual(before, (self.seeds, self.slip, self.generation, self.repair, self.founders))

    def test_none_and_empty_inputs_stay_distinct_without_events(self):
        package_events, lab_events = [], []
        absent = self.package(None, admission_callback=package_events.append)
        empty = self.package([], admission_callback=package_events.append)
        self.assertNotIn("founders", absent[1])
        self.assertEqual({"admitted_ids": [], "rejected": []}, empty[1]["founders"])
        self.assertNotEqual(complete_digest(absent), complete_digest(empty))
        lab_absent = self.laboratory(founder_grids=None, admission_callback=lab_events.append)
        self.assertEqual(BEFORE_SOURCE_SHA256["lab_none"], complete_digest(lab_absent))
        lab_empty = self.laboratory(founder_grids=[], admission_callback=lab_events.append)
        self.assertEqual(lab_empty, self.laboratory(founder_grids=[]))
        self.assertNotIn("workshop", lab_absent[1]["summary"])
        self.assertEqual([], lab_empty[1]["summary"]["workshop"]["founder_ids"])
        self.assertEqual(0, lab_empty[1]["summary"]["workshop"]["released_count"])
        self.assertIsNone(lab_empty[1]["workshop_grids_dir"])
        self.assertEqual([], package_events)
        self.assertEqual([], lab_events)

    def test_legacy_directory_observes_its_original_size_verdict_without_reclassification(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            self.write_founders(directory)
            events = []
            output = self.laboratory(workshop_grids_dir=directory, admission_callback=events.append)
            self.assertEqual(BEFORE_SOURCE_SHA256["lab_ordered_directory"], complete_digest(output, directory))
            self.assertEqual(output, self.laboratory(workshop_grids_dir=directory))
            self.assertEqual(list(range(5)), [event["submission_index"] for event in events])
            self.assertEqual([True, False, True, True, False], [event["admitted"] for event in events])
            self.assertIsNone(events[3]["rejection_errors"])

    def test_lab_refuses_ambiguous_or_invalid_direct_input_before_training(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(lab, "train_generation_model") as train:
            for founders in ([], self.founders):
                with self.assertRaisesRegex(ValueError, "mutually exclusive"):
                    self.laboratory(founder_grids=founders, workshop_grids_dir=temp)
            for founders in ({}, (), "founders"):
                with self.assertRaisesRegex(ValueError, "founder_grids must be a list"):
                    self.laboratory(founder_grids=founders)
            train.assert_not_called()

    def test_reordered_duplicate_inputs_are_observed_in_submitted_order(self):
        founders = list(reversed(self.founders))
        left, right = [], []
        self.package(founders, admission_callback=left.append)
        self.laboratory(founder_grids=founders, admission_callback=right.append)
        self.assertEqual(left, right)
        self.assertEqual([False, False, True, False, True], [event["admitted"] for event in left])
        self.assertEqual(list(range(5)), [event["submission_index"] for event in left])


if __name__ == "__main__":
    unittest.main()
