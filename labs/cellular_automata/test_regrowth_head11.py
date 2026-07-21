"""K1 (DR 0041): the 11-class regrowth head — repair learns to spell
what it preserves.

Pins the vocabulary-parameterized head at both sites (the lab
authority and the promoted ``mecha_engine.repair``), the legacy path's
byte-identity (no new model key, identical weights), the mechanism
demonstration (a wounded limb returns as a LIMB under the rich head
and as body-family under the legacy head — the DR 0039 coarsening,
now measured side by side), and the K1 study module's report shape,
gates, and determinism.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, GRID_GENOME]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from ca_nca_growth_repair import (  # noqa: E402
    CLASS_TOKENS,
    NEIGHBORHOOD_OFFSETS,
    RICH_CLASS_TOKENS,
    RICH_LIVE_TOKENS,
    grid_from_matrix,
    repair_with_wound_sites,
    train_neighborhood_repair_model,
)
from mecha_engine.repair import (  # noqa: E402
    repair_wound_sites as package_repair_wound_sites,
    train_repair_model as package_train_repair_model,
)

from regrowth_head11 import (  # noqa: E402
    ARTIFACT_ID,
    build_regrowth_head11_report,
    write_regrowth_head11_artifacts,
)


def _training_grid(grid_id: str) -> dict:
    """A small rich creature: legacy core + one limb cell at (5, 3)."""
    matrix = [["." for _ in range(8)] for _ in range(8)]
    for x, y, token in [
        (2, 1, "E"),
        (3, 1, "B"),
        (4, 1, "E"),
        (2, 2, "B"),
        (3, 2, "A"),
        (4, 2, "B"),
        (2, 3, "B"),
        (3, 3, "B"),
        (4, 3, "B"),
        (5, 3, "L"),
        (3, 4, "M"),
    ]:
        matrix[y][x] = token
    return grid_from_matrix(
        grid_id=grid_id,
        matrix=matrix,
        palette={"palette_id": "lcd_green"},
        parent_grid_id=None,
        source="regrowth_head11_test_fixture",
        mutation_events=["authored"],
        generation_delta=0,
    )


def _wounded_at_limb(grid_id: str) -> dict:
    """The same creature with the limb cell destroyed."""
    grid = _training_grid(grid_id)
    grid["cells"] = [
        cell
        for cell in grid["cells"]
        if (cell["x"], cell["y"]) != (5, 3)
    ]
    grid["organs"] = {
        organ_id: {
            **organ,
            "cells": [
                point for point in organ["cells"] if point != [5, 3]
            ],
        }
        for organ_id, organ in grid["organs"].items()
        if organ_id != "limbs"
    }
    return grid


TRAIN_KW = dict(
    dropout_rates=(0.2, 0.4, 0.6),
    damage_instances=3,
    epochs=60,
)


class RichHeadTrainingTests(unittest.TestCase):
    """The vocabulary keyword at the lab authority."""

    @classmethod
    def setUpClass(cls):
        cls.corpus = [_training_grid(f"regrow_t{i}") for i in range(3)]
        cls.legacy = train_neighborhood_repair_model(cls.corpus, **TRAIN_KW)
        cls.rich = train_neighborhood_repair_model(
            cls.corpus, vocabulary="rich", **TRAIN_KW
        )

    def test_rich_vocabulary_trains_a_twelve_class_head(self):
        self.assertEqual(RICH_CLASS_TOKENS, self.rich["class_tokens"])
        self.assertEqual(12, len(self.rich["class_tokens"]))
        self.assertEqual("rich", self.rich["vocabulary"])
        self.assertEqual(12, len(self.rich["weights"]))
        expected_features = len(NEIGHBORHOOD_OFFSETS) * len(
            RICH_LIVE_TOKENS
        ) + 64 + 1
        self.assertEqual(expected_features, self.rich["feature_count"])
        self.assertEqual(
            expected_features, len(self.rich["weights"][0])
        )

    def test_legacy_default_records_no_vocabulary_key(self):
        # DR 0041 G4 (the rider pattern): the historical model dict is
        # unchanged — no new key, the historical classes and layout.
        self.assertNotIn("vocabulary", self.legacy)
        self.assertEqual(CLASS_TOKENS, self.legacy["class_tokens"])
        self.assertEqual(
            len(NEIGHBORHOOD_OFFSETS) * 4 + 64 + 1,
            self.legacy["feature_count"],
        )
        self.assertEqual(
            "neighborhood_softmax_repair_model_stage0",
            self.legacy["model_id"],
        )

    def test_unknown_vocabulary_fails_loudly(self):
        with self.assertRaises(ValueError) as context:
            train_neighborhood_repair_model(
                self.corpus, vocabulary="chrome", **TRAIN_KW
            )
        self.assertIn("vocabulary", str(context.exception))

    def test_wounded_limb_regrows_as_limb_under_the_rich_head(self):
        # The mechanism, side by side: the legacy head coarsens the
        # limb's family to body (DR 0039's recorded partial
        # restoration); the rich head restores the exact token.
        damaged = _wounded_at_limb("regrow_wounded")
        rich_repaired = repair_with_wound_sites(
            damaged,
            self.rich,
            wound_sites=[[5, 3]],
            validity_guard=False,
        )
        legacy_repaired = repair_with_wound_sites(
            damaged,
            self.legacy,
            wound_sites=[[5, 3]],
            validity_guard=False,
        )
        rich_token = {
            (cell["x"], cell["y"]): cell["role"]
            for cell in rich_repaired["cells"]
        }[(5, 3)]
        legacy_token = {
            (cell["x"], cell["y"]): cell["role"]
            for cell in legacy_repaired["cells"]
        }[(5, 3)]
        self.assertEqual("limb", rich_token)
        self.assertEqual("body", legacy_token)


class RichHeadParityTests(unittest.TestCase):
    """DR 0041 G5: the two head sites stay byte-identical, rich included."""

    @classmethod
    def setUpClass(cls):
        cls.corpus = [_training_grid(f"parity_t{i}") for i in range(3)]

    def test_rich_trained_model_parity_every_field(self):
        lab = train_neighborhood_repair_model(
            self.corpus, vocabulary="rich", **TRAIN_KW
        )
        package = package_train_repair_model(
            self.corpus, vocabulary="rich", **TRAIN_KW
        )
        self.assertEqual(sorted(lab), sorted(package))
        for key in sorted(lab):
            with self.subTest(field=key):
                self.assertEqual(lab[key], package[key])

    def test_legacy_trained_model_parity_every_field(self):
        lab = train_neighborhood_repair_model(self.corpus, **TRAIN_KW)
        package = package_train_repair_model(self.corpus, **TRAIN_KW)
        self.assertEqual(sorted(lab), sorted(package))
        for key in sorted(lab):
            with self.subTest(field=key):
                self.assertEqual(lab[key], package[key])

    def test_rich_wound_repair_parity(self):
        lab_model = train_neighborhood_repair_model(
            self.corpus, vocabulary="rich", **TRAIN_KW
        )
        damaged = _wounded_at_limb("parity_wounded")
        lab_repaired = repair_with_wound_sites(
            damaged, lab_model, wound_sites=[[5, 3]]
        )
        package_repaired = package_repair_wound_sites(
            damaged, lab_model, wound_sites=[[5, 3]]
        )
        self.assertEqual(lab_repaired["cells"], package_repaired["cells"])
        self.assertEqual(
            lab_repaired["metadata"], package_repaired["metadata"]
        )


class RegrowthStudyTests(unittest.TestCase):
    """The K1 study report: shape, gates, determinism, artifacts."""

    @classmethod
    def setUpClass(cls):
        # Test scale: a handful of corpus grids and light training so
        # the suite stays fast; the committed artifact runs the
        # documented full configuration.
        cls.kw = dict(
            training_count=6,
            held_out_count=2,
            dropout_rates=(0.4,),
            damage_instances=1,
            epochs=8,
        )
        cls.report = build_regrowth_head11_report(**cls.kw)

    def test_report_identity_and_status(self):
        self.assertEqual(ARTIFACT_ID, self.report["artifact_id"])
        self.assertEqual("complete", self.report["status"])
        self.assertIn("purpose", self.report)
        self.assertIn("source_artifacts", self.report)

    def test_gates_carry_measured_values_and_verdicts(self):
        gates = self.report["gates"]
        for key in ("g1_exact_gain", "g2_family_held", "g3_validity_held",
                    "g4_legacy_byte_identity", "g5_parity"):
            with self.subTest(gate=key):
                self.assertIn(key, gates)
                self.assertIn("met", gates[key])
                self.assertIsInstance(gates[key]["met"], bool)
        self.assertIn(
            self.report["decision"]["verdict"],
            {"adopt_rich_head", "withhold_adoption"},
        )
        self.assertEqual(
            all(gate["met"] for gate in gates.values()),
            self.report["decision"]["verdict"] == "adopt_rich_head",
        )

    def test_metrics_report_both_arms_at_wound_sites(self):
        metrics = self.report["metrics"]
        for arm in ("legacy", "rich"):
            with self.subTest(arm=arm):
                arm_metrics = metrics[arm]
                self.assertGreaterEqual(
                    arm_metrics["wound_sites_measured"], 1
                )
                for key in (
                    "exact_restoration",
                    "family_restoration",
                    "valid_rate",
                    "guard_substitutions",
                ):
                    self.assertIn(key, arm_metrics)
                self.assertLessEqual(
                    arm_metrics["exact_restoration"],
                    arm_metrics["family_restoration"] + 1e-9,
                )

    def test_twin_runs_are_identical(self):
        self.assertEqual(
            self.report, build_regrowth_head11_report(**self.kw)
        )

    def test_artifacts_write_and_validate(self):
        with tempfile.TemporaryDirectory() as temp:
            paths = write_regrowth_head11_artifacts(Path(temp), self.report)
            written = json.loads(
                Path(paths["report"]).read_text(encoding="utf-8")
            )
            self.assertEqual(self.report, written)


if __name__ == "__main__":
    unittest.main()
