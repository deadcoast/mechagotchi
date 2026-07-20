"""Cycle 20 J2 gates — motion-role emission, measured at the source.

I4 animated limb/joint/decoration and I5b bounded coverage by the
generators' descriptor range; the exemplar is the only committed grid
exercising all three roles. Before any generator increment, the
emission rates are MEASURED per generation surface (the lab
constrained corpus, the adopted WFC corpus, and the PROMOTED
``generate_batch``) against the committed corpora as reference — the
numbers first, the increment gated on them.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from role_emission import (  # noqa: E402
    MOTION_ROLES,
    build_role_emission_report,
    write_role_emission_artifacts,
)


class RoleEmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_role_emission_report(count=12, rng_seed=19)

    def test_every_surface_is_measured_with_the_same_count(self):
        sources = self.report["metrics"]["sources"]
        for name in ("constrained", "wfc", "promoted_generate_batch"):
            with self.subTest(source=name):
                self.assertEqual(12, sources[name]["grid_count"])

    def test_the_reference_corpora_are_measured_too(self):
        sources = self.report["metrics"]["sources"]
        self.assertIn("seed_corpus_16", sources)
        self.assertIn("vocabulary_exemplars", sources)
        # The exemplar corpus is the vocabulary's proof: every motion
        # role present.
        exemplar = sources["vocabulary_exemplars"]
        for role in MOTION_ROLES:
            with self.subTest(role=role):
                self.assertGreater(
                    exemplar["roles"][role]["grids_with_role_rate"], 0
                )

    def test_rates_are_the_measured_arithmetic(self):
        for name, source in self.report["metrics"]["sources"].items():
            for role, stats in source["roles"].items():
                with self.subTest(source=name, role=role):
                    self.assertAlmostEqual(
                        stats["grids_with_role_rate"],
                        round(
                            stats["grids_with_role"]
                            / source["grid_count"],
                            6,
                        ),
                        places=9,
                    )

    def test_the_motion_trio_summary_matches_the_sources(self):
        summary = self.report["metrics"]["motion_trio_emission"]
        sources = self.report["metrics"]["sources"]
        for name in ("constrained", "wfc", "promoted_generate_batch"):
            with self.subTest(source=name):
                expected = round(
                    sum(
                        sources[name]["roles"][role][
                            "grids_with_role_rate"
                        ]
                        for role in MOTION_ROLES
                    )
                    / len(MOTION_ROLES),
                    6,
                )
                self.assertEqual(expected, summary[name])

    def test_the_report_is_deterministic_and_writes(self):
        twin = build_role_emission_report(count=12, rng_seed=19)
        self.assertEqual(
            json.dumps(self.report, sort_keys=True),
            json.dumps(twin, sort_keys=True),
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_role_emission_artifacts(Path(tmp), self.report)
            payload = json.loads(
                (Path(tmp) / "role_emission_stage0.json").read_text(
                    encoding="utf-8"
                )
            )
        self.assertEqual("role_emission_stage0", payload["artifact_id"])


if __name__ == "__main__":
    unittest.main()
