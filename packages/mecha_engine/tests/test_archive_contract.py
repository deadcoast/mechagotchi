"""Archive contract tests for the mecha_engine package surface.

Traceability: research/package_specs/mecha_engine_archive_contract_gate.md
("Mathematical Contract", "Candidate Acceptance", "Descriptor Acceptance",
"Fitness Acceptance", "Insertion Acceptance", "Summary Acceptance",
"Negative Checks"),
research/package_specs/mecha_engine_contract_traceability_matrix.md
("Archive Test Obligations"), and
research/package_specs/mecha_engine_property_negative_test_strategy.md (P5
archive niche correctness, P2/P7 invalid-candidate rejection, the archive
metamorphic checks, and the scalar-top-k separation rule).

Import mechanics match ``tests/test_package_imports.py``,
``tests/test_genome_contract.py``, ``tests/test_generation_contract.py``,
and ``tests/test_lifecycle_contract.py``: the probes run in one
``python -B`` subprocess whose PYTHONPATH points at this package's own
``src`` directory (standard src-layout semantics; an installed package
satisfies the same probe), executed by
``tests/helpers/archive_contract_driver.py`` through
``mecha_engine.archive``, ``mecha_engine.genome``, and
``mecha_engine.lifecycle``. This module never mutates the interpreter
module search path and never points the subprocess at research lab
directories. Fixtures are the frozen repository corpora fixed by the test
fixture manifest: ``data/seed_grids/*.json``, ``data/invalid_grids/*.json``
(all 200), and ``data/slips/valid/slip_lcd_seed.json``. The pinned Stage 0
extended-archive metrics run lab-side, in the map_elites_archive research
lab's package parity test, because they require the research corpus
generator and proxy readability scorer.
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
DRIVER = Path(__file__).resolve().parent / "helpers" / "archive_contract_driver.py"

REQUIRED_PUBLIC_SURFACE = [
    "archive_summary",
    "build_archive",
    "descriptor_for_candidate",
    "insert_candidate",
    "lifecycle_probe_grid",
    "score_candidate",
]
EXTENDED_DESCRIPTOR_NAMES = [
    "body_mass",
    "sensor_count",
    "symmetry",
    "readability",
    "lifecycle_survival",
    "mutation_stability",
    "behavior_neediness",
]
REQUIRED_FITNESS_COMPONENTS = [
    "bond",
    "mutation_stability",
    "readability",
    "slip_alignment",
    "survival",
    "validity",
]
REQUIRED_SCORE_FIELDS = [
    "fitness",
    "components",
    "validation",
    "readability",
    "lifecycle",
    "slip_alignment",
    "provenance",
]
REQUIRED_ELITE_FIELDS = [
    "descriptor",
    "fitness",
    "fitness_components",
    "grid",
    "grid_id",
    "provenance",
    "validation",
]
REQUIRED_SUMMARY_FIELDS = [
    "archive_kind",
    "best_fitness",
    "blocked_invalid_count",
    "candidate_count",
    "coverage",
    "descriptor_bin_spread",
    "descriptor_cardinalities",
    "descriptor_dimensions",
    "descriptor_mode",
    "descriptor_names",
    "final_descriptor_thresholds_locked",
    "mean_elite_fitness",
    "occupied_niches",
    "qd_score",
    "readability_calibration_status",
    "skipped_missing_metrics_count",
    "total_possible_niches",
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
        timeout=300,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"archive contract driver failed ({result.returncode}): {result.stderr}"
        )
    return json.loads(result.stdout)


class MechaEngineArchiveContractTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = _run_driver()

    # -- Public surface -----------------------------------------------------

    def test_public_surface_is_the_contracted_five_functions(self):
        self.assertEqual(REQUIRED_PUBLIC_SURFACE, self.report["surface"]["public_all"])

    def test_no_scalar_top_k_named_public_surface(self):
        # Scalar top-k selection is a comparator, not an archive
        # replacement: the package exposes no ranked/top-k surface at all.
        self.assertEqual([], self.report["surface"]["scalar_named_public_surface"])

    def test_descriptor_mode_selector_defaults_to_extended(self):
        surface = self.report["surface"]
        self.assertEqual("extended", surface["descriptor_mode_default"])
        self.assertEqual("KEYWORD_ONLY", surface["descriptor_mode_keyword_only"])
        self.assertEqual("extended", surface["build_archive_mode_default"])

    def test_archive_surface_loads_no_lab_modules(self):
        self.assertEqual([], self.report["lab_modules_loaded"])

    # -- Descriptor acceptance ------------------------------------------------

    def test_extended_descriptor_is_a_deterministic_7d_integer_tuple(self):
        descriptors = self.report["descriptors"]
        self.assertTrue(descriptors["extended_is_tuple"])
        self.assertEqual(7, descriptors["extended_length"])
        self.assertTrue(descriptors["extended_all_int"])
        self.assertTrue(descriptors["extended_deterministic"])

    def test_baseline_3d_descriptor_option_is_preserved(self):
        descriptors = self.report["descriptors"]
        self.assertEqual(3, descriptors["baseline_length"])
        self.assertTrue(descriptors["baseline_matches_extended_prefix"])
        self.assertTrue(descriptors["baseline_needs_no_metric_values"])

    def test_readability_axis_bins_on_the_provisional_stage0_thresholds(self):
        descriptors = self.report["descriptors"]
        self.assertEqual(
            descriptors["expected_readability_bins"], descriptors["readability_bins"]
        )

    def test_lifecycle_survival_axis_runs_the_contracted_stress_probe(self):
        # The survival descriptor must come from a mecha_engine.lifecycle
        # episode over the calibrated morphology-derived stress probe.
        descriptors = self.report["descriptors"]
        self.assertEqual(
            descriptors["expected_survival_bin"], descriptors["survival_bin"]
        )

    def test_precomputed_lifecycle_summaries_resolve_identically(self):
        descriptors = self.report["descriptors"]
        self.assertTrue(descriptors["full_summary_matches_internal"])
        self.assertTrue(descriptors["reduced_summary_matches_internal"])

    def test_missing_metric_inputs_are_rejected_explicitly(self):
        descriptors = self.report["descriptors"]
        for key, needle in [
            ("missing_readability_raised", "missing metric input: readability"),
            ("missing_slip_alignment_raised", "missing metric input: slip_alignment"),
            ("non_mapping_candidate_raised", "candidate"),
            ("candidate_without_grid_raised", "grid"),
            ("non_mapping_metrics_raised", "metrics"),
            ("unsupported_mode_raised", "unsupported descriptor mode"),
        ]:
            raised = descriptors[key]
            self.assertIsNotNone(raised, key)
            self.assertNotIn("UNEXPECTED", raised)
            self.assertIn(needle, raised)

    def test_descriptor_functions_never_mutate_inputs(self):
        descriptors = self.report["descriptors"]
        self.assertFalse(descriptors["candidate_mutated"])
        self.assertFalse(descriptors["metrics_mutated"])
        self.assertFalse(self.report["fixtures_mutated"])

    def test_descriptor_metadata_exposes_names_and_cardinalities(self):
        metadata = self.report["metadata"]
        self.assertEqual(EXTENDED_DESCRIPTOR_NAMES, metadata["extended"]["names"])
        self.assertEqual([5] * 7, metadata["extended"]["cardinalities"])
        self.assertEqual(7, metadata["extended"]["dimensions"])
        self.assertEqual(78125, metadata["extended"]["total_possible_niches"])
        self.assertEqual(EXTENDED_DESCRIPTOR_NAMES[:3], metadata["baseline"]["names"])
        self.assertEqual([5] * 3, metadata["baseline"]["cardinalities"])
        self.assertEqual(125, metadata["baseline"]["total_possible_niches"])

    def test_readability_calibration_stays_an_explicit_open_gate(self):
        # Proxy readability is never presented as human-calibrated and
        # final descriptor thresholds stay unlocked until manual ratings
        # exist (blocked-state assertion from the test strategy).
        metadata = self.report["metadata"]
        self.assertIn("proxy", metadata["readability_calibration_status"])
        self.assertIn("not_collected", metadata["readability_calibration_status"])
        self.assertFalse(metadata["final_descriptor_thresholds_locked"])
        scoring = self.report["scoring"]
        self.assertEqual("not_collected", scoring["proxy_marking_default"])
        self.assertEqual("not_collected", scoring["proxy_marking_preserved"])
        self.assertTrue(scoring["human_rating_absent"])

    # -- Fitness acceptance -----------------------------------------------------

    def test_score_reports_all_contracted_fields(self):
        scoring = self.report["scoring"]
        self.assertEqual(REQUIRED_SCORE_FIELDS, scoring["required_fields_present"])
        self.assertEqual(REQUIRED_FITNESS_COMPONENTS, scoring["component_names"])
        self.assertTrue(scoring["json_roundtrip"])

    def test_components_and_fitness_stay_inside_the_unit_interval(self):
        scoring = self.report["scoring"]
        self.assertTrue(scoring["components_bounded"])
        self.assertTrue(scoring["fitness_bounded"])
        self.assertTrue(scoring["invalid_scored_as_failure"]["fitness_bounded"])

    def test_fitness_is_the_pinned_stage0_weighted_component_sum(self):
        scoring = self.report["scoring"]
        self.assertTrue(scoring["fitness_matches_weighted_components"])
        # readability carries the pinned 0.24 weight: a 0.25 readability
        # difference moves fitness by exactly 0.06.
        self.assertEqual(0.06, scoring["readability_weight_delta"])

    def test_score_is_deterministic_and_pure(self):
        scoring = self.report["scoring"]
        self.assertTrue(scoring["deterministic"])
        self.assertFalse(scoring["candidate_mutated"])
        self.assertFalse(scoring["metrics_mutated"])

    def test_bond_component_comes_from_the_lifecycle_final_state(self):
        self.assertTrue(self.report["scoring"]["bond_component_from_lifecycle_final_state"])

    def test_slip_alignment_component_reflects_the_alignment_result(self):
        scoring = self.report["scoring"]
        self.assertTrue(scoring["aligned_slip_component_one"])
        self.assertTrue(scoring["misaligned_slip_component_zero"])

    def test_provenance_is_carried_and_missing_provenance_is_marked(self):
        scoring = self.report["scoring"]
        self.assertTrue(scoring["provenance_provided"]["provided"])
        self.assertEqual(
            {"source": "driver", "parent": None},
            scoring["provenance_provided"]["record"],
        )
        self.assertEqual(
            {"provided": False, "record": None}, scoring["provenance_missing_marked"]
        )

    def test_invalid_candidates_are_scored_as_failures_for_reports(self):
        failure = self.report["scoring"]["invalid_scored_as_failure"]
        self.assertEqual(0.0, failure["validity_component"])
        self.assertEqual(0.0, failure["survival_component"])
        self.assertEqual(0.0, failure["bond_component"])
        self.assertFalse(failure["validation_ok"])
        self.assertTrue(failure["validation_errors_nonempty"])
        self.assertTrue(failure["fitness_below_valid"])

    # -- Insertion acceptance ------------------------------------------------

    def test_empty_niche_accepts_the_first_valid_candidate(self):
        insertion = self.report["insertion"]
        self.assertTrue(insertion["inserted_into_empty_niche"])
        self.assertEqual("mg_seed_001", insertion["elite_grid_id"])

    def test_niche_key_is_derived_from_the_descriptor(self):
        insertion = self.report["insertion"]
        self.assertTrue(insertion["elite_descriptor_key_matches"])
        self.assertEqual(
            insertion["expected_descriptor_values"],
            insertion["elite_descriptor_values"],
        )

    def test_elite_entries_satisfy_the_archive_candidate_contract(self):
        # grid, descriptor, fitness, fitness_components, validation, and
        # provenance (plus grid_id) per the shared data contract.
        self.assertEqual(REQUIRED_ELITE_FIELDS, self.report["insertion"]["elite_fields"])

    def test_replacement_requires_strictly_higher_fitness(self):
        insertion = self.report["insertion"]
        self.assertTrue(insertion["same_niche_fixture"])
        self.assertTrue(insertion["fitness_ordering_fixture"])
        self.assertTrue(insertion["higher_fitness_replaced"])
        self.assertTrue(insertion["weaker_keeps_incumbent"])
        self.assertEqual("kept_incumbent_higher_fitness", insertion["weaker_event"])

    def test_equal_fitness_keeps_the_incumbent_deterministically(self):
        insertion = self.report["insertion"]
        self.assertTrue(insertion["tie_keeps_incumbent"])
        self.assertEqual("kept_incumbent_tie", insertion["tie_event"])

    def test_losing_candidates_preserve_the_previous_archive(self):
        insertion = self.report["insertion"]
        self.assertTrue(insertion["previous_archive_preserved_after_loss"])
        self.assertTrue(insertion["empty_archive_preserved"])
        self.assertTrue(insertion["returns_new_object"])
        self.assertTrue(insertion["input_archive_not_mutated_by_insert"])

    def test_insertions_are_audited_in_the_insertion_log(self):
        insertion = self.report["insertion"]
        self.assertEqual(
            ["inserted_empty_niche", "replaced_elite", "kept_incumbent_higher_fitness"],
            insertion["log_events"],
        )
        self.assertTrue(insertion["log_entries_complete"])
        self.assertTrue(insertion["replace_event_audits_incumbent"])
        self.assertTrue(insertion["candidate_count_accounting"])

    def test_distinct_morphology_occupies_a_distinct_niche(self):
        self.assertTrue(self.report["insertion"]["distinct_morphology_opens_second_niche"])

    def test_malformed_descriptors_scores_and_archives_are_rejected(self):
        insertion = self.report["insertion"]
        for key in [
            "bad_descriptor_raised",
            "non_int_descriptor_raised",
            "out_of_range_descriptor_raised",
            "bad_fitness_raised",
            "missing_validation_raised",
            "bad_archive_raised",
        ]:
            raised = insertion[key]
            self.assertIsNotNone(raised, key)
            self.assertNotIn("UNEXPECTED", raised)

    # -- Build and summary acceptance --------------------------------------------

    def test_build_archive_is_deterministic_and_pure(self):
        build = self.report["build"]
        self.assertTrue(build["deterministic_rebuild_identical"])
        self.assertFalse(build["candidates_mutated"])
        self.assertFalse(build["metrics_mutated"])
        self.assertTrue(build["json_roundtrip"])

    def test_build_archive_matches_the_per_candidate_public_functions(self):
        build = self.report["build"]
        self.assertEqual(build["expected_occupied_niches"], build["occupied_niches"])
        self.assertTrue(build["elite_keys_match_descriptors"])
        self.assertTrue(build["elite_fitness_match"])
        self.assertTrue(build["elite_entries_complete"])

    def test_build_archive_counts_blocked_and_skipped_candidates(self):
        build = self.report["build"]
        self.assertEqual(build["presented_candidates"], build["candidate_count"])
        self.assertEqual(1, build["blocked_invalid_count"])
        self.assertEqual(2, build["skipped_missing_metrics_count"])

    def test_summary_reports_every_contracted_field(self):
        self.assertEqual(REQUIRED_SUMMARY_FIELDS, self.report["build"]["summary_fields"])

    def test_summary_metrics_match_their_definitions(self):
        build = self.report["build"]
        self.assertTrue(build["coverage_matches"])
        self.assertTrue(build["qd_score_matches"])
        self.assertTrue(build["mean_elite_fitness_matches"])
        self.assertTrue(build["best_fitness_matches"])

    def test_summary_distinguishes_observed_bins_from_theoretical_coverage(self):
        self.assertTrue(self.report["build"]["bin_spread_matches"])

    def test_empty_archive_summary_reports_zero_state(self):
        empty = self.report["metadata"]["empty_summary"]
        self.assertEqual(0, empty["occupied_niches"])
        self.assertEqual(0.0, empty["coverage"])
        self.assertEqual(0, empty["best_fitness"])
        self.assertEqual(0, empty["mean_elite_fitness"])
        self.assertEqual(0, empty["qd_score"])

    def test_archive_kind_is_map_elites(self):
        self.assertEqual("map_elites", self.report["metadata"]["archive_kind"])

    # -- Negative checks ---------------------------------------------------------

    def test_scalar_top_k_remains_a_comparator_not_the_archive(self):
        separation = self.report["scalar_separation"]
        self.assertTrue(separation["weak_is_last_ranked"])
        self.assertTrue(separation["strong_pair_shares_one_niche"])
        self.assertTrue(separation["weak_niche_distinct"])
        self.assertTrue(separation["weak_candidate_kept_as_elite"])
        self.assertTrue(separation["archive_beats_scalar_niche_count"])
        self.assertEqual(2, separation["occupied_niches"])

    def test_no_invalid_corpus_grid_can_become_an_elite(self):
        corpus = self.report["invalid_corpus"]
        self.assertEqual(200, corpus["invalid_grid_count"])
        self.assertEqual([], corpus["unexpected_errors"])
        self.assertEqual(
            corpus["invalid_grid_count"],
            corpus["scored_as_failures"] + corpus["structurally_rejected"],
        )
        self.assertEqual(0, corpus["elites_after_sweep"])
        self.assertEqual(corpus["scored_as_failures"], corpus["blocked_invalid_count"])


if __name__ == "__main__":
    unittest.main()
