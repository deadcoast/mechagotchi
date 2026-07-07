"""D5: the campaign-scale spine holds under load — determinism, ledger
integrity, deterministic replay of every stored era, replay-hash
matching, and founder/unlock chain continuity, over a multi-era chain
persisted through the promoted storage module. A shorter chain keeps the
test fast; the shipped artifact uses the full 12-era schedule."""

import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

import session_soak as soak  # noqa: E402
from session_soak import (  # noqa: E402
    build_soak_report,
    run_soak_campaign,
    verify_soak,
)
from session_runner import (  # noqa: E402
    build_seed_grids,
    train_legibility_model,
    train_session_models,
)

SHORT_SCHEDULE = ("calm", "stable_soup", "storm", "calm", "storm")


class SessionSoakTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seeds = build_seed_grids()
        cls.generation_model, cls.repair_model = train_session_models(
            cls.seeds, repair_epochs=20, rng_seed=soak.SOAK_BASE_SEED
        )
        cls.legibility_model = train_legibility_model()
        cls.models = dict(
            seed_grids=cls.seeds,
            generation_model=cls.generation_model,
            repair_model=cls.repair_model,
            legibility_model=cls.legibility_model,
        )
        cls.campaign = run_soak_campaign(
            schedule=SHORT_SCHEDULE, **cls.models
        )

    def _verify(self, tmp: str) -> dict:
        return verify_soak(
            self.campaign, ledger_dir=Path(tmp), **self.models
        )

    def test_the_campaign_is_deterministic_at_scale(self):
        again = run_soak_campaign(schedule=SHORT_SCHEDULE, **self.models)
        self.assertEqual(self.campaign, again)

    def test_the_spine_is_all_green_over_the_full_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            checks = self._verify(tmp)
        self.assertEqual(len(SHORT_SCHEDULE), checks["era_count"])
        self.assertTrue(checks["ledger_round_trips_byte_identical"])
        self.assertTrue(
            checks["every_stored_era_replays_deterministically"]
        )
        self.assertTrue(checks["founder_chain_continuous"])
        self.assertTrue(checks["replay_hashes_match_rows"])
        self.assertTrue(checks["unlock_chain_monotonic"])

    def test_ingest_counts_scale_with_the_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            checks = self._verify(tmp)
        counts = checks["ingest_counts"]
        self.assertEqual(len(SHORT_SCHEDULE), counts["eras"])
        self.assertEqual(len(SHORT_SCHEDULE), counts["slip_profiles"])
        self.assertEqual(len(SHORT_SCHEDULE), counts["replays"])
        self.assertEqual(checks["replay_files_written"], counts["replays"])

    def test_unlock_counts_never_shrink(self):
        with tempfile.TemporaryDirectory() as tmp:
            checks = self._verify(tmp)
        series = checks["unlock_counts_by_era"]
        for earlier, later in zip(series, series[1:]):
            self.assertGreaterEqual(later, earlier)

    def test_report_decision_reflects_the_green_spine(self):
        with tempfile.TemporaryDirectory() as tmp:
            checks = self._verify(tmp)
            report = build_soak_report(self.campaign, checks)
        self.assertEqual(
            "soak_spine_holds_at_campaign_scale",
            report["decision"]["status"],
        )
        self.assertTrue(report["metrics"]["spine_all_green"])
        self.assertIn(
            "live_extinction_not_reachable_at_stage0_scale",
            report["blocked_states"],
        )
        import json

        json.dumps(report)


if __name__ == "__main__":
    unittest.main()
