"""Runtime contract tests for the mecha_engine package surface.

Traceability: research/package_specs/mecha_engine_runtime_interface_spec.md
("Proposed public surface", "Hard gates for the port", "Non-goals"),
research/package_specs/mecha_engine_contract_traceability_matrix.md
(the "Runtime" row and "Cross-Cut Negative Tests"), and
research/decision_records/0008-propose-mecha-engine-runtime-target.md.

Import mechanics match ``tests/test_package_imports.py`` and the other
contract suites: the probes run in one ``python -B`` subprocess whose
PYTHONPATH points at this package's own ``src`` directory (standard
src-layout semantics; an installed package satisfies the same probe),
executed by ``tests/helpers/runtime_contract_driver.py`` through
``mecha_engine.runtime`` and its promoted dependencies. This module never
mutates the interpreter module search path and never points the subprocess
at research lab directories. Fixtures are frozen repository corpora:
``data/seed_grids/mg_seed_001..050.json`` and
``data/slips/valid/slip_lcd_seed.json``; the readability scorer is an
injected constant. The verbatim evolution-loop reproduction (summary,
per-creature records, and decision, with the lab's proxy readability
injected) is pinned by the lab-side parity test
(``labs/runtime_integration/test_package_runtime_parity.py``); this suite
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
DRIVER = Path(__file__).resolve().parent / "helpers" / "runtime_contract_driver.py"

REQUIRED_PUBLIC_SURFACE = ["evolve", "live_cycle"]
# Interface-spec signatures (runtime interface spec, "Proposed public
# surface"; rng_seed is the caller's per-creature run seed).
REQUIRED_LIVE_CYCLE_DEFAULTS = {
    "grid": "REQUIRED",
    "slip_profile": "REQUIRED",
    "repair_model": "REQUIRED",
    "damage_cycles": "3",
    "ticks": "72",
    "dropout_rate": "0.2",
    "rng_seed": "20260512",
    "damage_events": "None",
}
REQUIRED_EVOLVE_DEFAULTS = {
    "seed_grids": "REQUIRED",
    "slip_profile": "REQUIRED",
    "generation_model": "REQUIRED",
    "repair_model": "REQUIRED",
    "readability_scorer": "REQUIRED",
    "generations": "4",
    "population": "8",
    "damage_cycles": "3",
    "ticks": "72",
    "dropout_rate": "0.2",
    "rng_seed": "20260512",
}
REQUIRED_CYCLE_FIELDS = [
    "aligned",
    "cycle",
    "episode",
    "guard_substitutions",
    "position_restoration",
    "removed_cell_count",
    "token_restoration",
    "valid",
]
REQUIRED_FINAL_STATE_FIELDS = [
    "aligned",
    "cycles_completed",
    "grid_id",
    "live_cell_count",
    "valid",
]


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
            f"runtime contract driver failed ({result.returncode}): {result.stderr}"
        )
    return json.loads(result.stdout)


class MechaEngineRuntimeContractTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = _run_driver()

    # -- Public surface -----------------------------------------------------

    def test_public_surface_is_the_contracted_two_functions(self):
        self.assertEqual(
            REQUIRED_PUBLIC_SURFACE, self.report["surface"]["public_all"]
        )

    def test_live_cycle_signature_matches_interface_spec(self):
        defaults = self.report["surface"]["signature_defaults"]["live_cycle"]
        self.assertEqual(REQUIRED_LIVE_CYCLE_DEFAULTS, defaults)

    def test_evolve_signature_matches_interface_spec(self):
        defaults = self.report["surface"]["signature_defaults"]["evolve"]
        self.assertEqual(REQUIRED_EVOLVE_DEFAULTS, defaults)

    def test_tuning_parameters_are_keyword_only(self):
        keyword_only = self.report["surface"]["keyword_only_parameters"]
        self.assertEqual(
            ["damage_cycles", "ticks", "dropout_rate", "rng_seed", "damage_events"],
            keyword_only["live_cycle"],
        )
        self.assertEqual(
            [
                "readability_scorer",
                "generations",
                "population",
                "damage_cycles",
                "ticks",
                "dropout_rate",
                "rng_seed",
            ],
            keyword_only["evolve"],
        )

    def test_runtime_surface_loads_no_lab_modules(self):
        self.assertEqual([], self.report["lab_modules_loaded"])

    # -- Evolve acceptance ----------------------------------------------------

    def test_evolve_is_deterministic_end_to_end(self):
        probe = self.report["evolve"]
        self.assertTrue(probe["deterministic_reports_equal"])
        self.assertTrue(probe["deterministic_archives_equal"])

    def test_evolve_report_and_archive_are_json_serializable(self):
        probe = self.report["evolve"]
        self.assertTrue(probe["report_json_roundtrip"])
        self.assertTrue(probe["archive_json_roundtrip"])

    def test_archive_elites_become_parents_in_generation_1(self):
        probe = self.report["evolve"]
        self.assertEqual(2, probe["generation_count"])
        self.assertEqual("seed_pool", probe["generation_0_parent_source"])
        self.assertEqual("archive_elites", probe["generation_1_parent_source"])

    def test_readability_manual_rating_status_stays_visible(self):
        # Interface spec: no proxy scorer is ported; the record's
        # manual-rating status stays visible in every score.
        probe = self.report["evolve"]
        self.assertEqual(
            ["not_collected"], probe["readability_manual_rating_statuses"]
        )
        self.assertGreater(probe["archived_creature_count"], 0)

    def test_every_creature_completes_and_scores(self):
        probe = self.report["evolve"]
        self.assertEqual(probe["creature_count"], probe["archived_creature_count"])
        self.assertTrue(probe["every_creature_scored"])
        self.assertGreaterEqual(probe["elite_count"], 1)
        self.assertEqual("evolution_loop_composed", probe["decision_status"])

    def test_evolve_rejects_missing_scorer_and_empty_seed_corpus(self):
        probe = self.report["evolve"]
        raised = probe["readability_scorer_required_keyword"]
        self.assertIsNotNone(raised)
        self.assertIn("TypeError", raised)
        raised = probe["empty_seed_grids_raised"]
        self.assertIsNotNone(raised)
        self.assertIn("ValueError", raised)
        self.assertIn("seed_grids", raised)

    def test_evolve_never_mutates_caller_inputs(self):
        self.assertFalse(self.report["fixtures_mutated"])
        self.assertFalse(self.report["generation_model_mutated"])

    # -- Live cycle acceptance --------------------------------------------------

    def test_live_cycle_is_deterministic(self):
        probe = self.report["live_cycle"]
        self.assertTrue(probe["deterministic_repeat_identical"])
        self.assertTrue(probe["result_json_roundtrip"])

    def test_live_cycle_runs_the_requested_synthesizer_cycles(self):
        probe = self.report["live_cycle"]
        self.assertEqual("internal_synthesizer", probe["damage_source"])
        self.assertEqual(2, probe["cycle_count"])
        self.assertEqual(2, probe["cycles_requested"])
        self.assertTrue(probe["every_cycle_reports_removed_cells"])

    def test_live_cycle_reports_contracted_cycle_and_final_state_digests(self):
        probe = self.report["live_cycle"]
        self.assertEqual(REQUIRED_CYCLE_FIELDS, probe["cycle_fields"])
        self.assertEqual(REQUIRED_FINAL_STATE_FIELDS, probe["final_state_fields"])
        self.assertTrue(probe["final_state_valid"])
        self.assertTrue(probe["final_state_aligned"])

    def test_live_cycle_reassigns_the_grid_id_per_cycle(self):
        # The 64-char grid_id cap trap: ids are reassigned, never suffixed
        # cumulatively.
        self.assertTrue(self.report["live_cycle"]["final_grid_id_reassigned"])

    def test_aligned_cycles_carry_full_episodes(self):
        self.assertTrue(self.report["live_cycle"]["aligned_cycles_have_episodes"])

    # -- Injected damage events ---------------------------------------------------

    def test_injected_events_replace_the_synthesizer(self):
        probe = self.report["injected_events"]
        self.assertEqual("injected_events", probe["damage_source"])
        self.assertTrue(probe["events_define_cycle_count"])
        self.assertTrue(probe["deterministic_repeat_identical"])

    def test_injected_wound_is_repaired_to_the_full_silhouette(self):
        probe = self.report["injected_events"]
        self.assertGreater(probe["wound_cycle_removed_cell_count"], 0)
        self.assertEqual(1.0, probe["wound_cycle_position_restoration"])

    def test_empty_removed_cells_event_is_a_no_op_repair(self):
        # Measured lab behavior: a zero-cell damage event is legal and the
        # repair is a no-op.
        probe = self.report["injected_events"]
        self.assertEqual(0, probe["empty_event_removed_cell_count"])
        self.assertEqual(1.0, probe["empty_event_position_restoration"])
        self.assertEqual(1.0, probe["empty_event_token_restoration"])
        self.assertEqual(0, probe["empty_event_guard_substitutions"])
        self.assertTrue(probe["noop_tokens_unchanged"])

    def test_injected_events_are_never_mutated_and_bad_events_fail_loudly(self):
        probe = self.report["injected_events"]
        self.assertFalse(probe["events_mutated"])
        raised = probe["missing_removed_cells_raised"]
        self.assertIsNotNone(raised)
        self.assertIn("ValueError", raised)
        self.assertIn("removed_cells", raised)
        raised = probe["out_of_range_position_raised"]
        self.assertIsNotNone(raised)
        self.assertIn("ValueError", raised)


if __name__ == "__main__":
    unittest.main()
