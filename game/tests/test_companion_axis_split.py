"""Pins for cycle 26 P1: the §1.17 axis split, measured as shipped.

`validity-research.md` §1.17 names eight VISIBLE and eight HIDDEN
companion state axes and defines none of them. The split is measurably
stale against the shipped client — M5/DR 0048 corrected the gap count
(five → three), N5/DR 0054 found the client already surfaces two
documented-HIDDEN axes under accurate names, and O2/DR 0055 put
`health` on screen under a CHOSEN definition. P1 builds the instrument
that measures the split AS SHIPPED — each documented axis → its engine
source and its on-screen surface, or its recorded absence — so the
dated correction beside §1.17 quotes a measurement, and so M5's honest
remainder 2 (the game-side display of age and mood was cited by file
reference, never measured) is CLOSED by a pin in the game's own suite.

The engine-source half must reproduce the committed M5 survey
(`data/architecture/companion_state_survey_stage0.json`) on seven of
eight visible axes, with `health` differing in exactly the DR 0054
direction — any other mismatch is instrument drift and the builder
refuses to produce an artifact (Phase N's law, O4's hard-gate shape).
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _src in (
    ROOT / "game",
    ROOT / "game" / "src",
    ROOT / "packages" / "mecha_engine" / "src",
):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from evidence import (  # noqa: E402
    AXIS_SPLIT_ARTIFACT_ID,
    AXIS_SPLIT_PREDICTION,
    AXIS_SPLIT_RULE,
    SECTION_117_HIDDEN,
    SECTION_117_VISIBLE,
    _new_session,
    build_companion_axis_split_report,
    write_companion_axis_split_artifacts,
)


class SnapshotPinTests(unittest.TestCase):
    """The direct game-side pins M5's remainder 2 asked for."""

    def test_snapshot_carries_age_and_mood(self):
        snapshot = _new_session().snapshot()
        self.assertIn("age_ticks", snapshot)
        self.assertIsInstance(snapshot["age_ticks"], int)
        self.assertIn("mood", snapshot)
        self.assertIsInstance(snapshot["mood"], str)

    def test_snapshot_surfaces_the_two_hidden_axes_under_their_labels(self):
        needs = _new_session().snapshot()["needs"]
        self.assertEqual(needs["stress"]["label"], "stress")
        self.assertEqual(needs["grid_stability"]["label"], "body stability")

    def test_snapshot_never_carries_an_invented_axis(self):
        # `happiness` is no longer invented: DR 0058 adopted a CHOSEN
        # definition and the readout landed in the same P2 slice, so the
        # pin's job narrows to the one axis that still has no source —
        # and to asserting that what IS shown says it is chosen.
        snapshot = _new_session().snapshot()
        flat = json.dumps(snapshot).lower()
        self.assertNotIn("cleanliness", flat)
        self.assertTrue(snapshot["happiness"]["chosen"])


class ReportShapeTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_companion_axis_split_report()

    def test_report_carries_every_required_artifact_key(self):
        for key in (
            "artifact_id",
            "status",
            "date",
            "purpose",
            "source_artifacts",
            "parameters",
            "metrics",
            "closed_states",
            "blocked_states",
            "decision",
            "next_research_step",
        ):
            self.assertIn(key, self.report)
        self.assertEqual(self.report["artifact_id"], AXIS_SPLIT_ARTIFACT_ID)

    def test_all_sixteen_documented_axes_are_measured(self):
        axes = self.report["metrics"]["axes"]
        self.assertEqual(
            sorted(axes),
            sorted(SECTION_117_VISIBLE + SECTION_117_HIDDEN),
        )
        for name in SECTION_117_VISIBLE:
            self.assertEqual(axes[name]["documented_split"], "visible")
        for name in SECTION_117_HIDDEN:
            self.assertEqual(axes[name]["documented_split"], "hidden")

    def test_the_shipped_visible_surface_is_measured(self):
        axes = self.report["metrics"]["axes"]
        shown = (
            "hunger", "energy", "bond", "age", "mood", "health", "happiness",
        )
        for name in shown:
            self.assertTrue(axes[name]["on_screen"]["shown"], name)
        self.assertFalse(axes["cleanliness"]["on_screen"]["shown"])

    def test_no_axis_without_an_engine_source_is_shown(self):
        # DR 0021's first law, measured rather than asserted.
        for name, axis in self.report["metrics"]["axes"].items():
            if axis["engine_source"]["disposition"] == "absent":
                self.assertFalse(axis["on_screen"]["shown"], name)

    def test_the_two_surfaced_hidden_axes_carry_their_shipped_labels(self):
        axes = self.report["metrics"]["axes"]
        self.assertTrue(axes["stress"]["on_screen"]["shown"])
        self.assertEqual(axes["stress"]["on_screen"]["label"], "stress")
        self.assertTrue(axes["grid stability"]["on_screen"]["shown"])
        self.assertEqual(
            axes["grid stability"]["on_screen"]["label"], "body stability"
        )

    def test_the_other_six_hidden_axes_are_not_surfaced(self):
        axes = self.report["metrics"]["axes"]
        for name in SECTION_117_HIDDEN:
            if name in ("stress", "grid stability"):
                continue
            self.assertFalse(axes[name]["on_screen"]["shown"], name)

    def test_health_is_shown_as_a_chosen_definition_with_its_binding_axis(self):
        health = self.report["metrics"]["axes"]["health"]
        self.assertEqual(
            health["engine_source"]["disposition"], "chosen_definition_dr0054"
        )
        self.assertTrue(health["on_screen"]["shown"])
        self.assertTrue(health["on_screen"]["binding_word"])
        self.assertTrue(health["on_screen"]["labelled_chosen"])

    def test_absences_carry_their_measured_causes(self):
        axes = self.report["metrics"]["axes"]
        self.assertIn(
            "no clean action",
            axes["cleanliness"]["engine_source"]["measured_cause"],
        )
        self.assertIn(
            "no lifecycle field",
            axes["happiness"]["engine_source"]["measured_cause"],
        )


class InstrumentCheckTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_companion_axis_split_report()

    def test_the_committed_survey_is_reproduced_on_six_of_eight(self):
        # Two axes now legitimately differ from the committed M5 survey,
        # each explained by the decision record that moved it — health
        # (DR 0054, cycle 24) and happiness (DR 0058, this cycle). Any
        # OTHER difference is instrument drift and the builder raises.
        check = self.report["metrics"]["instrument_check"]
        self.assertTrue(check["reproduced_committed_dispositions"])
        self.assertEqual(check["matching_axes"], 6)
        differences = check["expected_differences"]
        self.assertEqual(sorted(differences), ["happiness", "health"])
        self.assertEqual(
            differences["health"]["measured"], "chosen_definition_dr0054"
        )
        self.assertEqual(
            differences["happiness"]["measured"], "chosen_definition_dr0058"
        )
        for entry in differences.values():
            self.assertEqual(entry["committed"], "absent")

    def test_happiness_is_shown_as_a_chosen_definition(self):
        happiness = self.report["metrics"]["axes"]["happiness"]
        self.assertEqual(
            happiness["engine_source"]["disposition"],
            "chosen_definition_dr0058",
        )
        self.assertTrue(happiness["on_screen"]["shown"])
        self.assertTrue(happiness["on_screen"]["labelled_chosen"])

    def test_the_rule_and_prediction_are_pre_registered(self):
        self.assertIn("pre-registered", AXIS_SPLIT_RULE.lower())
        self.assertIn("instrument", AXIS_SPLIT_RULE.lower())
        self.assertTrue(AXIS_SPLIT_PREDICTION)
        self.assertEqual(self.report["decision"]["rule"], AXIS_SPLIT_RULE)

    def test_the_correction_is_warranted_and_names_its_three_clauses(self):
        decision = self.report["decision"]
        self.assertTrue(decision["correction_warranted"])
        clauses = decision["correction_clauses"]
        self.assertEqual(len(clauses), 3)
        flat = " ".join(clauses).lower()
        self.assertIn("happiness", flat)
        self.assertIn("cleanliness", flat)
        self.assertIn("body stability", flat)
        self.assertIn("health", flat)


class ArtifactTests(unittest.TestCase):
    report: dict

    @classmethod
    def setUpClass(cls):
        cls.report = build_companion_axis_split_report()

    def test_source_artifact_paths_are_repo_relative(self):
        for path in self.report["source_artifacts"]:
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("\\", path)

    def test_artifact_round_trips_as_json(self):
        with tempfile.TemporaryDirectory() as directory:
            written = write_companion_axis_split_artifacts(
                directory, self.report
            )
            reloaded = json.loads(written.read_text(encoding="utf-8"))
        self.assertEqual(reloaded["artifact_id"], AXIS_SPLIT_ARTIFACT_ID)
        self.assertEqual(reloaded["decision"]["rule"], AXIS_SPLIT_RULE)


if __name__ == "__main__":
    unittest.main()
