"""Cycle 23 M5: the documented visible companion state, surveyed honestly.

`validity-research.md` §1.17 names eight VISIBLE state axes — *hunger,
happiness, energy, cleanliness, mood, age, health, bond* — and eight
HIDDEN ones. The Phase-K survey, re-verified at the Phase-L gate,
recorded that **five of the eight visible axes have no engine field**
and called it the largest player-facing gap in the repo.

M5 was chartered to survey each axis honestly **before** building
anything. These pins fix what "honestly" means here:

* presence is **MEASURED against the live engine**, never asserted from
  a document — the survey builds a real lifecycle state and calls the
  real derivation functions;
* an axis backed by a **derived engine value** counts as present. The
  earlier survey looked only at lifecycle homeostasis fields, which is a
  narrower question than "has an engine field";
* the verdict vocabulary is fixed in advance and **`absent` is
  first-class** — the survey must be able to report a gap where one
  exists, or it is not a survey.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from companion_state_survey import (  # noqa: E402
    ARTIFACT_ID,
    DOCUMENTED_HIDDEN_AXES,
    DOCUMENTED_VISIBLE_AXES,
    DISPOSITIONS,
    build_companion_state_report,
    survey_axis,
    write_companion_state_artifacts,
)


class DocumentedAxisTests(unittest.TestCase):
    def test_the_eight_visible_axes_are_the_documented_ones_verbatim(self):
        # Quoted from validity-research.md §1.17 in document order. If
        # this list drifts, the survey is measuring something the
        # documentation did not ask for.
        self.assertEqual(
            (
                "hunger",
                "happiness",
                "energy",
                "cleanliness",
                "mood",
                "age",
                "health",
                "bond",
            ),
            DOCUMENTED_VISIBLE_AXES,
        )

    def test_stress_and_grid_stability_are_documented_HIDDEN_not_visible(self):
        # They exist in the engine, but promoting a hidden axis to a
        # visible one would be a documentation change, not a survey
        # finding. Keeping the two lists apart is what stops that.
        self.assertIn("stress", DOCUMENTED_HIDDEN_AXES)
        self.assertIn("grid stability", DOCUMENTED_HIDDEN_AXES)
        for axis in DOCUMENTED_HIDDEN_AXES:
            self.assertNotIn(axis, DOCUMENTED_VISIBLE_AXES)


class SurveyVerdictTests(unittest.TestCase):
    def test_absent_is_a_first_class_disposition(self):
        # A survey that cannot report a gap is not a survey.
        self.assertIn("absent", DISPOSITIONS)
        self.assertIn("lifecycle_field", DISPOSITIONS)
        self.assertIn("derived_engine_value", DISPOSITIONS)

    def test_a_lifecycle_field_axis_is_measured_present(self):
        result = survey_axis("hunger")
        self.assertEqual("lifecycle_field", result["disposition"])
        self.assertIsNotNone(result["measured_value"])

    def test_age_is_present_as_a_lifecycle_field_measured_not_assumed(self):
        # The correction this survey exists to make: `age_ticks` is set
        # at construction and incremented every tick. Measured against
        # the live engine, not read off a document.
        result = survey_axis("age")
        self.assertEqual("lifecycle_field", result["disposition"])
        self.assertEqual("age_ticks", result["engine_field"])

    def test_mood_is_present_as_a_DERIVED_engine_value(self):
        # `select_animation_state` returns (animation, mood) and has
        # since Phase C. It is not a homeostasis field, which is why a
        # field-only survey missed it — but it is engine truth.
        result = survey_axis("mood")
        self.assertEqual("derived_engine_value", result["disposition"])
        self.assertIn(result["measured_value"], ("tired", "hungry", "stressed", "curious"))

    def test_a_genuinely_absent_axis_is_reported_absent_with_no_value(self):
        # And no number is invented for it (DR 0021's first law).
        for axis in ("happiness", "cleanliness"):
            with self.subTest(axis=axis):
                result = survey_axis(axis)
                self.assertEqual("absent", result["disposition"])
                self.assertIsNone(result["measured_value"])

    def test_an_unknown_axis_is_refused_rather_than_reported_absent(self):
        # "Absent" is a measurement about a documented axis; a typo must
        # not silently become a finding.
        with self.assertRaises(ValueError):
            survey_axis("sparkliness")


class CompanionStateReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_companion_state_report()

    def test_the_report_carries_the_stage0_contract(self):
        for key in (
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
            with self.subTest(key=key):
                self.assertIn(key, self.report)
        self.assertEqual(ARTIFACT_ID, self.report["artifact_id"])

    def test_every_documented_visible_axis_is_surveyed(self):
        surveyed = self.report["metrics"]["visible_axes"]
        self.assertEqual(set(DOCUMENTED_VISIBLE_AXES), set(surveyed))

    def test_the_prior_survey_claim_is_re_measured_and_recorded(self):
        # The claim under test: "five of the eight visible axes have no
        # engine field". The survey records what it actually measures
        # rather than repeating it.
        correction = self.report["metrics"]["prior_claim"]
        self.assertEqual(5, correction["previously_reported_absent"])
        self.assertEqual(
            correction["measured_absent"],
            len(
                [
                    a
                    for a, r in self.report["metrics"]["visible_axes"].items()
                    if r["disposition"] == "absent"
                ]
            ),
        )

    def test_no_absent_axis_carries_an_invented_value(self):
        # DR 0021's first law, pinned: an absent axis gets no number.
        for axis, result in self.report["metrics"]["visible_axes"].items():
            if result["disposition"] == "absent":
                with self.subTest(axis=axis):
                    self.assertIsNone(result["measured_value"])

    def test_the_artifact_writes_and_reloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = write_companion_state_artifacts(Path(tmp), self.report)
            self.assertTrue(written)
            for path in written:
                reloaded = json.loads(Path(path).read_text(encoding="utf-8"))
                self.assertEqual(ARTIFACT_ID, reloaded["artifact_id"])


if __name__ == "__main__":
    unittest.main()
