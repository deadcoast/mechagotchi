"""Repair contract tests for the mecha_engine package surface.

Traceability: research/package_specs/mecha_engine_repair_interface_spec.md
("The observability contract", "Data contracts", "Required public
surface", "Validity-guard semantics", "Hard gates for a future package
port"), research/package_specs/mecha_engine_contract_traceability_matrix.md
(the "Repair" row and "Cross-Cut Negative Tests"), and
research/decision_records/0006-create-mecha-engine-repair-target.md.

Import mechanics match ``tests/test_package_imports.py`` and the other
contract suites: the probes run in one ``python -B`` subprocess whose
PYTHONPATH points at this package's own ``src`` directory (standard
src-layout semantics; an installed package satisfies the same probe),
executed by ``tests/helpers/repair_contract_driver.py`` through
``mecha_engine.repair`` and ``mecha_engine.genome``. This module never
mutates the interpreter module search path and never points the subprocess
at research lab directories. Fixtures are frozen repository corpora:
``data/seed_grids/mg_seed_*.json`` (including the adversarial
validity-guard fixture ``mg_seed_001`` with wound ``[[2, 3], [3, 3]]``).
The verbatim benchmark reproduction (weights, per-cycle repairs, and the
guarded stability bar) is pinned by the lab-side parity test; this suite
proves the package contract directly.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
SRC_DIR = PACKAGE_ROOT / "src"
DRIVER = Path(__file__).resolve().parent / "helpers" / "repair_contract_driver.py"

REQUIRED_PUBLIC_SURFACE = [
    "repair_blind",
    "repair_wound_sites",
    "train_repair_model",
]
REQUIRED_MODEL_FIELDS = [
    "model_id",
    "source_mode",
    "weights",
    "training_grid_ids",
    "example_count",
    "feature_count",
    "class_tokens",
    "rng_seed",
    "epochs",
    "learning_rate",
    "live_class_weight",
    "initial_loss",
    "final_loss",
    "target_template_used",
]
REQUIRED_RESULT_METADATA_FIELDS = [
    "learned_model_id",
    "target_template_used",
    "wound_site_count",
    "validity_guard_substitutions",
]
# Interface-spec training defaults (kept verbatim from the research lab).
REQUIRED_TRAIN_DEFAULTS = {
    "training_grids": "REQUIRED",
    "dropout_rates": "(0.1, 0.2, 0.3, 0.4)",
    "damage_instances": "1",
    "epochs": "150",
    "learning_rate": "1.5",
    "live_class_weight": "3.0",
    "rng_seed": "20260512",
}
REQUIRED_WOUND_DEFAULTS = {
    "damaged_grid": "REQUIRED",
    "model": "REQUIRED",
    "wound_sites": "None",
    "validity_guard": "True",
}


def _run_driver() -> dict:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(SRC_DIR) + (os.pathsep + existing if existing else "")
    result = subprocess.run(
        [sys.executable, "-B", str(DRIVER), "--repo-root", str(REPO_ROOT)],
        capture_output=True,
        text=True,
        env=env,
        cwd=PACKAGE_ROOT,
        timeout=600,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"repair contract driver failed ({result.returncode}): {result.stderr}"
        )
    return json.loads(result.stdout)


class MechaEngineRepairContractTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = _run_driver()

    # -- Public surface -----------------------------------------------------

    def test_public_surface_is_the_contracted_three_functions(self):
        self.assertEqual(REQUIRED_PUBLIC_SURFACE, self.report["surface"]["public_all"])

    def test_train_repair_model_keeps_the_lab_training_defaults(self):
        defaults = self.report["surface"]["signature_defaults"]["train_repair_model"]
        self.assertEqual(REQUIRED_TRAIN_DEFAULTS, defaults)

    def test_repair_wound_sites_signature_matches_interface_spec(self):
        defaults = self.report["surface"]["signature_defaults"]["repair_wound_sites"]
        self.assertEqual(REQUIRED_WOUND_DEFAULTS, defaults)

    def test_no_template_or_target_parameter_anywhere_on_the_surface(self):
        for name, parameters in self.report["surface"][
            "template_named_parameters"
        ].items():
            with self.subTest(function=name):
                self.assertEqual([], parameters)

    def test_template_kwargs_are_rejected(self):
        for key in ["template_kwarg_rejected", "pre_damage_grid_kwarg_rejected"]:
            raised = self.report["surface"][key]
            self.assertIsNotNone(raised, key)
            self.assertIn("TypeError", raised)

    def test_template_assisted_attractor_is_not_ported(self):
        # Decision record 0006: the module is structurally template-free.
        self.assertEqual([], self.report["surface"]["attractor_surface_absent"])

    def test_blind_arm_is_labelled_below_bar_benchmark_comparator(self):
        surface = self.report["surface"]
        self.assertTrue(surface["blind_doc_labels_benchmark_comparator"])
        self.assertTrue(surface["blind_doc_labels_below_bar"])

    def test_repair_surface_loads_no_lab_modules(self):
        self.assertEqual([], self.report["lab_modules_loaded"])

    # -- Training acceptance --------------------------------------------------

    def test_training_is_deterministic_for_identical_inputs(self):
        training = self.report["training"]
        self.assertTrue(training["identical_inputs_identical_weights"])
        self.assertTrue(training["identical_inputs_identical_model"])
        self.assertTrue(training["reseeded_weights_differ"])

    def test_training_never_uses_a_target_template(self):
        self.assertTrue(self.report["training"]["target_template_used_false"])

    def test_training_loss_decreases(self):
        self.assertTrue(self.report["training"]["final_loss_below_initial"])

    def test_model_reports_all_contracted_fields(self):
        training = self.report["training"]
        self.assertEqual(REQUIRED_MODEL_FIELDS, training["required_fields_present"])
        self.assertTrue(training["training_grid_ids_recorded"])
        self.assertTrue(training["example_count_positive"])
        self.assertTrue(training["model_json_roundtrip"])

    def test_empty_training_corpus_is_rejected(self):
        raised = self.report["training"]["empty_corpus_raised"]
        self.assertIsNotNone(raised)
        self.assertIn("ValueError", raised)
        self.assertIn("training_grids must not be empty", raised)

    def test_training_never_mutates_the_corpus(self):
        self.assertFalse(self.report["training"]["inputs_mutated"])

    # -- Wound-site repair acceptance ------------------------------------------

    def test_repair_fills_exactly_the_reported_sites(self):
        wound = self.report["wound_repair"]
        self.assertGreater(wound["site_count"], 0)
        self.assertTrue(wound["every_site_refilled_live"])
        self.assertTrue(wound["live_set_is_damaged_plus_sites"])
        self.assertTrue(wound["non_site_cells_unchanged"])

    def test_repaired_live_positions_equal_pre_damage_live_positions(self):
        # The interface-spec invariant that makes one-sided overlap equal
        # two-sided structural agreement identically for this surface.
        self.assertTrue(self.report["wound_repair"]["live_positions_restored"])

    def test_repair_is_deterministic(self):
        self.assertTrue(self.report["wound_repair"]["deterministic_repeat_identical"])

    def test_wound_sites_default_to_the_damage_events_removed_cells(self):
        self.assertTrue(self.report["wound_repair"]["default_sites_match_explicit_sites"])

    def test_repair_result_reports_all_contracted_metadata(self):
        wound = self.report["wound_repair"]
        self.assertEqual(
            REQUIRED_RESULT_METADATA_FIELDS, wound["metadata_fields_present"]
        )
        self.assertTrue(wound["learned_model_id_recorded"])
        self.assertTrue(wound["target_template_used_false"])
        self.assertTrue(wound["wound_site_count_matches"])
        self.assertTrue(wound["substitutions_are_int"])
        self.assertEqual("learned_wound_site_softmax_repair", wound["source_label"])
        self.assertTrue(wound["grid_id_suffix_ok"])
        self.assertTrue(wound["parent_grid_id_is_damaged_grid"])
        self.assertTrue(wound["result_json_roundtrip"])

    def test_guarded_repair_of_the_probe_wound_is_valid(self):
        self.assertTrue(self.report["wound_repair"]["repaired_valid"])

    def test_damage_event_without_removed_cells_fails_loudly(self):
        raised = self.report["wound_repair"]["missing_removed_cells_raised"]
        self.assertIsNotNone(raised)
        self.assertIn("KeyError", raised)
        self.assertIn("removed_cells", raised)

    def test_repair_never_mutates_the_damaged_grid_or_model(self):
        wound = self.report["wound_repair"]
        self.assertFalse(wound["damaged_grid_mutated"])
        self.assertFalse(wound["model_mutated"])
        self.assertFalse(self.report["fixtures_mutated"])

    # -- Validity guard ---------------------------------------------------------

    def test_guard_fixture_wounds_body_core_cells(self):
        self.assertTrue(self.report["validity_guard"]["fixture_cells_are_body_core"])

    def test_guard_off_reproduces_the_invalid_adversarial_refill(self):
        guard = self.report["validity_guard"]
        self.assertTrue(guard["guard_off_invalid"])
        self.assertTrue(guard["guard_off_substitutions_zero"])

    def test_guard_on_recovers_a_valid_grid_with_substitutions(self):
        guard = self.report["validity_guard"]
        self.assertTrue(guard["guard_on_valid"])
        self.assertGreaterEqual(guard["guard_on_substitutions"], 1)

    def test_guard_substitutes_tokens_without_changing_the_live_set(self):
        self.assertTrue(self.report["validity_guard"]["live_sets_equal_guard_on_off"])

    def test_guard_is_deterministic_on_and_off(self):
        guard = self.report["validity_guard"]
        self.assertTrue(guard["guard_off_deterministic"])
        self.assertTrue(guard["guard_on_deterministic"])

    def test_target_template_used_is_false_on_every_result(self):
        guard = self.report["validity_guard"]
        self.assertTrue(guard["naive_target_template_used_false"])
        self.assertTrue(guard["guarded_target_template_used_false"])
        self.assertTrue(self.report["wound_repair"]["target_template_used_false"])
        self.assertTrue(self.report["blind"]["target_template_used_false"])
        self.assertTrue(self.report["training"]["target_template_used_false"])

    # -- Blind benchmark comparator ----------------------------------------------

    def test_blind_comparator_is_deterministic_and_labelled(self):
        blind = self.report["blind"]
        self.assertTrue(blind["deterministic_repeat_identical"])
        self.assertTrue(blind["learned_model_id_recorded"])
        self.assertEqual("learned_neighborhood_softmax_repair", blind["source_label"])
        self.assertEqual(8, blind["repair_steps_recorded"])
        self.assertTrue(blind["grid_id_suffix_ok"])
        self.assertFalse(blind["damaged_grid_mutated"])


if __name__ == "__main__":
    unittest.main()
