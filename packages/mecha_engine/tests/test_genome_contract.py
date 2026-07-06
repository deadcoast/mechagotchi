"""Genome contract tests for the mecha_engine package surface.

Traceability: research/package_specs/mecha_engine_genome_contract_gate.md
("Validation Acceptance", "Schema Acceptance", "Signature Acceptance",
"Render Packet Acceptance", "Negative Checks"),
research/package_specs/mecha_engine_contract_traceability_matrix.md
("Genome Test Obligations"), and
research/package_specs/mecha_engine_property_negative_test_strategy.md
(P1, P2, genome metamorphic checks).

Import mechanics match ``tests/test_package_imports.py``: the probes run in
one ``python -B`` subprocess whose PYTHONPATH points at this package's own
``src`` directory (standard src-layout semantics; an installed package
satisfies the same probe), executed by
``tests/helpers/genome_contract_driver.py`` through ``mecha_engine.genome``.
This module never mutates the interpreter module search path and never
points the subprocess at research lab directories. Fixtures are the frozen
repository corpora fixed by the test fixture manifest:
``data/seed_grids/*.json`` (50) and ``data/invalid_grids/*.json`` (200).
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
DRIVER = Path(__file__).resolve().parent / "helpers" / "genome_contract_driver.py"

SEED_CORPUS_EXPECTED = 50
INVALID_CORPUS_EXPECTED = 200
REQUIRED_TOP_LEVEL_FIELDS = [
    "grid_id",
    "schema_version",
    "grid_size",
    "cells",
    "organs",
    "palette",
    "mutation",
]
REQUIRED_PACKET_FIELDS = {"grid_id", "grid_size", "palette", "cells", "state"}
# The og five-state vocabulary, order load-bearing (decision record 0013).
REQUIRED_ANIMATION_STATES = ["idle", "blink", "sleep", "beg", "ill"]
REQUIRED_SINGLE_FAULTS = {
    "coordinate_out_of_bounds",
    "duplicate_occupied_coordinate",
    "unknown_semantic_role",
    "unknown_material",
    "mutation_weight_below_minimum",
    "mutation_weight_above_maximum",
    "cell_mutation_weight_above_maximum",
    "missing_animation_anchor",
    "missing_required_sensor_or_expression",
    "organ_references_absent_cell",
    "body_mass_below_minimum",
    "disconnected_required_body_core",
    "palette_color_not_hex",
    "palette_id_invalid",
    "grid_size_outside_schema_range",
    "schema_version_mismatch",
    "grid_id_pattern_violation",
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
        timeout=300,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"genome contract driver failed ({result.returncode}): {result.stderr}"
        )
    return json.loads(result.stdout)


class MechaEngineGenomeContractTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = _run_driver()

    def test_accepts_all_seed_grids(self):
        corpus = self.report["corpus"]
        self.assertEqual(SEED_CORPUS_EXPECTED, corpus["seed_total"])
        self.assertEqual([], corpus["rejected_seed_files"])
        self.assertEqual(SEED_CORPUS_EXPECTED, corpus["seed_accepted"])

    def test_rejects_all_invalid_grids(self):
        corpus = self.report["corpus"]
        self.assertEqual(INVALID_CORPUS_EXPECTED, corpus["invalid_total"])
        self.assertEqual([], corpus["accepted_invalid_files"])
        self.assertEqual(INVALID_CORPUS_EXPECTED, corpus["invalid_rejected"])

    def test_validation_does_not_mutate_inputs(self):
        self.assertEqual([], self.report["corpus"]["mutated_input_files"])

    def test_validate_grid_file_matches_validate_grid(self):
        self.assertEqual([], self.report["corpus"]["file_api_mismatch_files"])

    def test_repeat_validation_is_stable(self):
        # Metamorphic check: validating the same payload twice yields the
        # same result and error family.
        self.assertEqual([], self.report["corpus"]["revalidation_mismatch_files"])

    def test_invalid_corpus_errors_are_structured(self):
        self.assertEqual([], self.report["corpus"]["empty_error_invalid_files"])

    def test_ordinary_invalid_payloads_return_errors_without_throwing(self):
        outcomes = self.report["ordinary_invalid_payloads"]
        self.assertGreaterEqual(len(outcomes), 3)
        for outcome in outcomes:
            self.assertIsNone(outcome["raised"], outcome)
            self.assertFalse(outcome["ok"], outcome)
            self.assertGreater(outcome["error_count"], 0, outcome)
            self.assertFalse(outcome["mutated"], outcome)

    def test_schema_2020_12_contract_is_preserved(self):
        schema = self.report["schema"]
        self.assertEqual(
            "https://json-schema.org/draft/2020-12/schema", schema["schema_draft"]
        )
        self.assertEqual(REQUIRED_TOP_LEVEL_FIELDS, schema["schema_required"])
        self.assertEqual(REQUIRED_TOP_LEVEL_FIELDS, schema["package_required"])
        self.assertEqual("0.1.0", schema["schema_version_const"])

    def test_schema_and_semantic_gates_stay_aligned(self):
        # Removing any schema-required top-level field must also fail the
        # package's semantic validation.
        removals = self.report["schema"]["required_field_removal_fails"]
        self.assertEqual(set(REQUIRED_TOP_LEVEL_FIELDS), set(removals))
        for field, failed in removals.items():
            self.assertTrue(failed, f"schema field removal not rejected: {field}")

    def test_single_fault_variants_are_rejected_for_expected_reason(self):
        outcomes = {outcome["fault"]: outcome for outcome in self.report["single_faults"]}
        self.assertEqual(REQUIRED_SINGLE_FAULTS, set(outcomes))
        for fault, outcome in outcomes.items():
            self.assertTrue(outcome["rejected"], outcome)
            self.assertTrue(outcome["expected_error_present"], outcome)
            self.assertFalse(outcome["mutated"], outcome)

    def test_signature_is_deterministic(self):
        signature = self.report["signature"]
        self.assertTrue(signature["deterministic"])
        self.assertTrue(signature["json_roundtrip_stable"])
        self.assertFalse(signature["input_mutated"])
        self.assertEqual(
            [], self.report["corpus"]["seed_signature_nondeterministic_files"]
        )

    def test_signature_changes_on_semantic_surfaces(self):
        for surface, changed in self.report["signature"]["changes_on"].items():
            self.assertTrue(changed, f"signature did not change on: {surface}")

    def test_signature_ignores_non_semantic_metadata(self):
        for surface, same in self.report["signature"]["ignores"].items():
            self.assertTrue(same, f"signature changed on non-semantic surface: {surface}")

    def test_render_packet_shape_and_serializability(self):
        packet = self.report["render_packet"]
        self.assertTrue(REQUIRED_PACKET_FIELDS.issubset(set(packet["keys"])))
        self.assertTrue(packet["grid_id_matches"])
        self.assertTrue(packet["cell_count_matches"])
        self.assertTrue(packet["stateless_state_is_null"])
        self.assertTrue(packet["state_passthrough"])
        self.assertTrue(packet["json_serializable"])
        self.assertTrue(packet["json_roundtrip_equal"])

    def test_render_packet_does_not_alias_or_mutate_inputs(self):
        packet = self.report["render_packet"]
        self.assertTrue(packet["grid_not_mutated"])
        self.assertTrue(packet["state_not_mutated"])

    def test_render_packet_rejects_invalid_grids(self):
        packet = self.report["render_packet"]
        self.assertTrue(packet["invalid_grid_rejected"])
        self.assertIn("valid grid", packet["invalid_grid_error"])
        corpus = self.report["corpus"]
        self.assertEqual(SEED_CORPUS_EXPECTED, corpus["seed_render_packets_built"])
        self.assertEqual([], corpus["seed_render_packet_failures"])

    def test_genome_surface_loads_no_lab_modules(self):
        self.assertEqual([], self.report["lab_modules_loaded"])

    # -- Render packet v2 (decision record 0013) ------------------------------

    def test_render_packet_v2_idle_is_base_and_carries_the_vocabulary(self):
        packet = self.report["render_packet_v2"]
        self.assertEqual(REQUIRED_ANIMATION_STATES, packet["vocabulary"])
        self.assertEqual("idle", packet["idle_animation"])
        self.assertTrue(packet["idle_mood_is_none"])
        self.assertTrue(packet["idle_cells_equal_v1"])
        self.assertTrue(packet["idle_state_is_null"])
        self.assertTrue(
            set(REQUIRED_PACKET_FIELDS | {"animation", "mood", "animation_vocabulary"}).issubset(
                set(packet["idle_keys"])
            )
        )

    def test_render_packet_from_grid_stays_exactly_v1(self):
        self.assertTrue(self.report["render_packet_v2"]["v1_packet_has_no_v2_keys"])

    def test_render_packet_v2_projections_are_visual_only_and_valid(self):
        packet = self.report["render_packet_v2"]
        self.assertTrue(packet["projections_visual_only"])
        self.assertTrue(packet["projections_valid"])

    def test_render_packet_v2_selection_mirrors_the_mood_thresholds(self):
        for case in self.report["render_packet_v2"]["selection"]:
            with self.subTest(expected=case["expected"]):
                self.assertEqual(case["expected"], case["actual"])
                self.assertTrue(case["state_passthrough"])

    def test_render_packet_v2_projected_visuals_ride_the_cells(self):
        packet = self.report["render_packet_v2"]
        # sleep: eye AND mouth cells take the background color.
        self.assertEqual([packet["background"]], packet["sleep_face_visuals"])

    def test_render_packet_v2_explicit_animation_override_wins(self):
        packet = self.report["render_packet_v2"]
        self.assertEqual("beg", packet["override_animation"])
        # The override keeps the lifecycle-selected mood visible.
        self.assertEqual("tired", packet["override_mood"])
        self.assertEqual([packet["accent"]], packet["override_mouth_visuals"])

    def test_render_packet_v2_rejects_unknown_states_and_invalid_grids(self):
        packet = self.report["render_packet_v2"]
        self.assertIsNotNone(packet["unknown_state_error"])
        self.assertIn("unknown animation state", packet["unknown_state_error"])
        self.assertIsNotNone(packet["invalid_grid_error"])
        self.assertIn("valid grid", packet["invalid_grid_error"])

    def test_render_packet_v2_is_deterministic_serializable_and_pure(self):
        packet = self.report["render_packet_v2"]
        self.assertTrue(packet["deterministic_repeat_identical"])
        self.assertTrue(packet["json_serializable"])
        self.assertTrue(packet["json_roundtrip_equal"])
        self.assertTrue(packet["grid_not_mutated"])


if __name__ == "__main__":
    unittest.main()
