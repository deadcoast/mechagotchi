"""Cycle 19 I3 gates — real weather harshness, measured per phase.

The I1 corpus carries BOTH phases, labeled by the runs' own metrics.
The harshness question is pre-registered and falsifiable both ways:
does any post-takeover snapshot's dropout multiplier — computed by the
ENGINE'S OWN promoted seam math, untouched — breach the synthetic
storm's 1.17x precedent (DR 0018's measured figure)? Whatever the
engine says is the answer; nothing is tuned to feel dramatic.
"""

import sys
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
    STORM_PRECEDENT_MULTIPLIER,
    build_real_weather_harshness_report,
)
from mecha_engine.runtime.evolve import (  # noqa: E402
    _cubff_generation_pressure,
)
from mecha_game.campaign import load_real_weather_source  # noqa: E402


class HarshnessMeasurementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_real_weather_harshness_report()

    def test_every_committed_snapshot_is_measured_with_its_phase(self):
        source = load_real_weather_source()
        per_snapshot = self.report["metrics"]["per_snapshot"]
        self.assertEqual(len(source), len(per_snapshot))
        for entry in per_snapshot:
            self.assertIn(
                entry["phase"], {"early_phase", "post_takeover"}
            )

    def test_multipliers_are_the_engines_own_seam_math(self):
        source = {
            record["snapshot_id"]: record
            for record in load_real_weather_source()
        }
        for entry in self.report["metrics"]["per_snapshot"]:
            pressure, multiplier = _cubff_generation_pressure(
                source[entry["snapshot_id"]]
            )
            self.assertEqual(multiplier, entry["dropout_multiplier"])
            self.assertEqual(pressure, entry["mutation_pressure"])

    def test_the_precedent_question_is_judged_on_the_numbers(self):
        self.assertEqual(1.17, STORM_PRECEDENT_MULTIPLIER)
        metrics = self.report["metrics"]
        post = [
            entry["dropout_multiplier"]
            for entry in metrics["per_snapshot"]
            if entry["phase"] == "post_takeover"
        ]
        self.assertTrue(post)  # the I1 corpus really carries the phase
        self.assertEqual(
            max(post), metrics["by_phase"]["post_takeover"]["max_multiplier"]
        )
        self.assertEqual(
            metrics["post_takeover_breaches_storm_precedent"],
            max(post) > STORM_PRECEDENT_MULTIPLIER,
        )

    def test_the_channel_states_stay_named_never_smuggled(self):
        # The replication channel is LIT by the callback path (a
        # closed state); lineage_churn stays silent on every real
        # path (a blocked state) — both named, neither smuggled.
        closed = " ".join(self.report["closed_states"])
        blocked = " ".join(self.report["blocked_states"])
        self.assertIn("replication", closed)
        self.assertIn("callback", closed)
        self.assertIn("lineage", blocked)

    def test_the_report_is_deterministic(self):
        import json

        twin = build_real_weather_harshness_report()
        self.assertEqual(
            json.dumps(self.report, sort_keys=True),
            json.dumps(twin, sort_keys=True),
        )


class CallbackPathTests(unittest.TestCase):
    """The named increment made real: callback states with the

    replication channel LIT, from committed compact records — every
    engine number recomputed live from the committed evidence.
    """

    @classmethod
    def setUpClass(cls):
        cls.report = build_real_weather_harshness_report()
        cls.callback = cls.report["metrics"]["callback_path"]

    def test_the_committed_states_cover_both_phases(self):
        phases = [entry["phase"] for entry in self.callback["per_state"]]
        self.assertIn("early_phase", phases)
        self.assertIn("post_takeover", phases)

    def test_replication_channel_is_lit_post_takeover_only(self):
        for entry in self.callback["per_state"]:
            if entry["phase"] == "post_takeover":
                self.assertGreater(entry["high_replication_count"], 0)
            else:
                self.assertEqual(0, entry["high_replication_count"])

    def test_multipliers_recompute_from_the_committed_records(self):
        import json as _json

        payload = _json.loads(
            (
                ROOT
                / "data"
                / "cubff_real_ingest"
                / "callback_states"
                / "callback_states_compact.json"
            ).read_text(encoding="utf-8")
        )
        by_id = {r["snapshot_id"]: r for r in payload["records"]}
        for entry in self.callback["per_state"]:
            pressure, multiplier = _cubff_generation_pressure(
                by_id[entry["snapshot_id"]]
            )
            self.assertEqual(pressure, entry["mutation_pressure"])
            self.assertEqual(multiplier, entry["dropout_multiplier"])

    def test_the_breach_verdict_is_the_numbers(self):
        post = [
            entry["dropout_multiplier"]
            for entry in self.callback["per_state"]
            if entry["phase"] == "post_takeover"
        ]
        self.assertEqual(
            self.callback["post_takeover_breaches_storm_precedent"],
            max(post) > STORM_PRECEDENT_MULTIPLIER,
        )

    def test_lineage_churn_stays_a_named_silent_channel(self):
        blocked = " ".join(self.report["blocked_states"])
        self.assertIn("lineage", blocked)


if __name__ == "__main__":
    unittest.main()
