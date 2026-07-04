"""Generation contract tests for the mecha_engine package surface.

Traceability: research/package_specs/mecha_engine_generation_contract_gate.md
("Model Acceptance", "Candidate Acceptance", "Batch Acceptance",
"SLIP Acceptance", "Explanation Acceptance", "Negative Checks"),
research/package_specs/mecha_engine_contract_traceability_matrix.md
("Generation Test Obligations"), and
research/package_specs/mecha_engine_property_negative_test_strategy.md
(P3, invalid-parent propagation, deterministic batches).

Import mechanics match ``tests/test_package_imports.py`` and
``tests/test_genome_contract.py``: the probes run in one ``python -B``
subprocess whose PYTHONPATH points at this package's own ``src`` directory
(standard src-layout semantics; an installed package satisfies the same
probe), executed by ``tests/helpers/generation_contract_driver.py`` through
``mecha_engine.generation`` and ``mecha_engine.genome``. This module never
mutates the interpreter module search path and never points the subprocess
at research lab directories. Fixtures are the frozen repository corpora
fixed by the test fixture manifest: ``data/seed_grids/*.json`` (50),
``data/invalid_grids/*.json`` (200), and
``data/slips/valid/slip_lcd_seed.json``.
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
DRIVER = Path(__file__).resolve().parent / "helpers" / "generation_contract_driver.py"

SEED_CORPUS_EXPECTED = 50
RANDOM_MUTATION_BASELINE_VALID_PER_100 = 42
CONSTRAINED_GATE_VALID_PER_100 = 100
SLIP_GATE_VALID_AND_ALIGNED_PER_50 = 50
REQUIRED_EXPLANATION_FIELDS = [
    "grid_id",
    "parent_grid_id",
    "generator_strategy",
    "rng_seed",
    "mutation_events",
    "validation",
    "slip_alignment",
    "accepted_proposals",
    "rejected_proposals",
]
REQUIRED_PUBLIC_SURFACE = [
    "GenerationModel",
    "explain_generation",
    "generate_batch",
    "generate_candidate",
    "train_generation_model",
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
            f"generation contract driver failed ({result.returncode}): {result.stderr}"
        )
    return json.loads(result.stdout)


class MechaEngineGenerationContractTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = _run_driver()

    # -- Model acceptance -------------------------------------------------

    def test_model_trains_on_full_seed_corpus(self):
        self.assertEqual(SEED_CORPUS_EXPECTED, self.report["seed_corpus_size"])
        model = self.report["model"]
        self.assertTrue(model["is_generation_model"])
        self.assertEqual(SEED_CORPUS_EXPECTED, model["seed_count_recorded"])
        self.assertTrue(model["total_pairs_positive"])
        self.assertEqual(["down", "right"], model["adjacency_directions"])

    def test_model_metadata_identifies_corpus_and_strategy(self):
        model = self.report["model"]
        self.assertEqual("constrained_wfc_style_stabilizer", model["strategy"])
        self.assertEqual("markov_local_adjacency_proposals", model["proposal_source"])
        self.assertTrue(model["seed_grid_ids_match_corpus"])
        self.assertTrue(model["corpus_digest_present"])

    def test_model_training_is_deterministic(self):
        self.assertTrue(self.report["model"]["training_deterministic"])

    def test_model_rejects_empty_seed_corpus(self):
        raised = self.report["model"]["empty_corpus_raised"]
        self.assertIsNotNone(raised)
        self.assertNotIn("UNEXPECTED", raised)
        self.assertIn("non-empty", raised)

    def test_model_rejects_invalid_seed_corpus(self):
        raised = self.report["model"]["invalid_corpus_raised"]
        self.assertIsNotNone(raised)
        self.assertNotIn("UNEXPECTED", raised)
        self.assertIn("invalid grids", raised)

    def test_model_training_does_not_mutate_seed_grids(self):
        self.assertFalse(self.report["model"]["seeds_mutated"])

    # -- Candidate acceptance ---------------------------------------------

    def test_candidate_passes_package_genome_validation(self):
        candidate = self.report["candidate"]
        self.assertTrue(
            candidate["candidate_valid_through_genome"],
            candidate["candidate_validation_errors"],
        )
        self.assertTrue(candidate["schema_version_preserved"])
        self.assertTrue(candidate["json_roundtrip_equal"])

    def test_candidate_rejects_invalid_parent_before_proposals(self):
        raised = self.report["candidate"]["invalid_parent_raised"]
        self.assertIsNotNone(raised)
        self.assertNotIn("UNEXPECTED", raised)
        self.assertIn("before proposal", raised)
        non_model = self.report["candidate"]["non_model_raised"]
        self.assertIsNotNone(non_model)
        self.assertNotIn("UNEXPECTED", non_model)

    def test_candidate_preserves_lineage_and_parent(self):
        candidate = self.report["candidate"]
        self.assertTrue(candidate["parent_grid_id_preserved"])
        self.assertTrue(candidate["generation_incremented"])
        self.assertTrue(candidate["ancestor_ids_extend_parent_chain"])
        self.assertTrue(candidate["mutation_events_present"])

    def test_candidate_lineage_chains_across_generations(self):
        candidate = self.report["candidate"]
        self.assertTrue(candidate["chained_generation_incremented"])
        self.assertTrue(candidate["chained_ancestors_extend_chain"])

    def test_candidate_is_deterministic_for_same_inputs(self):
        candidate = self.report["candidate"]
        self.assertTrue(candidate["deterministic_repeat_identical"])
        self.assertTrue(candidate["deterministic_repeat_signature_equal"])

    def test_candidate_differs_for_different_rng_seed(self):
        self.assertTrue(self.report["candidate"]["reseeded_differs"])

    def test_candidate_id_is_stable_and_schema_compatible(self):
        candidate = self.report["candidate"]
        self.assertTrue(candidate["grid_id_pattern_ok"])
        self.assertTrue(candidate["grid_id_stable_across_repeats"])

    def test_candidate_generation_does_not_mutate_inputs(self):
        candidate = self.report["candidate"]
        self.assertFalse(candidate["parent_mutated"])
        self.assertFalse(candidate["model_mutated"])
        self.assertFalse(self.report["seed_corpus_mutated"])

    # -- Batch acceptance ---------------------------------------------------

    def test_batch_returns_exact_count_with_unique_ids(self):
        batch = self.report["batch"]
        self.assertEqual(batch["count_requested"], batch["count_returned"])
        self.assertEqual(batch["count_returned"], batch["unique_candidate_ids"])
        self.assertTrue(batch["zero_count_returns_empty"])
        self.assertIsNotNone(batch["negative_count_raised"])

    def test_batch_is_deterministic_per_rng_seed(self):
        batch = self.report["batch"]
        self.assertTrue(batch["deterministic_batches_identical"])
        self.assertTrue(batch["reseeded_batch_differs"])

    def test_batch_reproduces_constrained_100_of_100_validity_gate(self):
        batch = self.report["batch"]
        self.assertEqual(CONSTRAINED_GATE_VALID_PER_100, batch["valid_count"])
        self.assertEqual(CONSTRAINED_GATE_VALID_PER_100, batch["unique_signatures"])
        self.assertGreater(
            batch["valid_count"], RANDOM_MUTATION_BASELINE_VALID_PER_100
        )
        self.assertTrue(batch["beats_random_mutation_baseline"])

    def test_batch_candidates_carry_lineage_and_trace(self):
        batch = self.report["batch"]
        self.assertEqual(batch["count_returned"], batch["traces_present"])
        self.assertEqual(batch["count_returned"], batch["lineage_complete"])

    # -- SLIP acceptance ----------------------------------------------------

    def test_slip_batch_reproduces_50_of_50_valid_and_aligned_gate(self):
        slip_batch = self.report["slip_batch"]
        self.assertEqual(slip_batch["count_requested"], slip_batch["count_returned"])
        self.assertEqual(
            SLIP_GATE_VALID_AND_ALIGNED_PER_50, slip_batch["valid_count"]
        )
        self.assertEqual(
            SLIP_GATE_VALID_AND_ALIGNED_PER_50, slip_batch["aligned_count"]
        )
        self.assertEqual(
            SLIP_GATE_VALID_AND_ALIGNED_PER_50, slip_batch["trace_aligned_count"]
        )
        self.assertEqual(
            slip_batch["count_returned"], slip_batch["unique_candidate_ids"]
        )

    def test_slip_candidate_is_aligned_with_evidence(self):
        slip_candidate = self.report["slip_candidate"]
        self.assertTrue(slip_candidate["candidate_valid_through_genome"])
        self.assertTrue(slip_candidate["structurally_aligned"])
        self.assertTrue(slip_candidate["trace_alignment_checked"])
        self.assertTrue(slip_candidate["trace_alignment_ok"])
        self.assertEqual("slip_lcd_seed", slip_candidate["trace_alignment_profile_id"])

    def test_invalid_slip_profile_is_rejected_before_generation(self):
        candidate_raised = self.report["slip_candidate"]["invalid_profile_raised"]
        self.assertIsNotNone(candidate_raised)
        self.assertNotIn("UNEXPECTED", candidate_raised)
        self.assertIn("curiosity", candidate_raised)
        batch_raised = self.report["slip_batch"]["invalid_profile_raised"]
        self.assertIsNotNone(batch_raised)
        self.assertNotIn("UNEXPECTED", batch_raised)

    def test_unsatisfiable_slip_profile_fails_clearly(self):
        batch_raised = self.report["slip_batch"]["unsatisfiable_profile_raised"]
        self.assertIsNotNone(batch_raised)
        self.assertNotIn("UNEXPECTED", batch_raised)
        self.assertIn("no seed grids satisfy SLIP constraints", batch_raised)
        parent_raised = self.report["slip_candidate"]["misaligned_parent_raised"]
        self.assertIsNotNone(parent_raised)
        self.assertNotIn("UNEXPECTED", parent_raised)
        self.assertIn("SLIP", parent_raised)

    def test_slip_profile_is_not_mutated(self):
        self.assertFalse(self.report["slip_candidate"]["profile_mutated"])
        self.assertFalse(self.report["slip_batch"]["profile_mutated"])

    # -- Explanation acceptance ----------------------------------------------

    def test_explanation_contains_required_fields(self):
        explanation = self.report["explanation"]
        self.assertEqual(
            REQUIRED_EXPLANATION_FIELDS, explanation["required_fields_present"]
        )
        self.assertTrue(explanation["json_serializable"])

    def test_explanation_matches_candidate_evidence(self):
        explanation = self.report["explanation"]
        self.assertTrue(explanation["grid_id_matches"])
        self.assertTrue(explanation["parent_matches"])
        self.assertTrue(explanation["rng_seed_matches"])
        self.assertTrue(explanation["mutation_events_match_lineage"])
        self.assertTrue(explanation["validation_ok"])
        self.assertTrue(explanation["proposals_accounted"])
        self.assertTrue(explanation["unconstrained_alignment_unchecked"])
        self.assertTrue(explanation["slip_alignment_checked"])
        self.assertTrue(explanation["slip_alignment_ok"])
        self.assertEqual("slip_lcd_seed", explanation["slip_alignment_profile_id"])

    def test_explanation_never_mutates_and_rejects_untraced_candidates(self):
        explanation = self.report["explanation"]
        self.assertFalse(explanation["candidate_mutated_by_explain"])
        raised = explanation["untraced_candidate_raised"]
        self.assertIsNotNone(raised)
        self.assertNotIn("UNEXPECTED", raised)
        self.assertIn("generation trace", raised)

    # -- Negative checks -------------------------------------------------------

    def test_raw_markov_is_not_the_sole_production_generator(self):
        exposure = self.report["markov_exposure"]
        self.assertEqual(REQUIRED_PUBLIC_SURFACE, exposure["public_all"])
        self.assertEqual([], exposure["markov_named_public_surface"])
        self.assertTrue(exposure["model_strategy_is_constrained"])
        self.assertTrue(exposure["proposal_source_is_markov_proposals_only"])
        self.assertTrue(exposure["all_batch_candidates_validator_gated"])

    def test_generation_surface_loads_no_lab_modules(self):
        self.assertEqual([], self.report["lab_modules_loaded"])


if __name__ == "__main__":
    unittest.main()
