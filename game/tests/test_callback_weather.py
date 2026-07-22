"""K4 gates (DR 0043) — the callback forecast, decided by its consumer.

The committed I3 compact records (the LIT replication channel) drop
into the engine's `cubff_pressure_source` seam UNMODIFIED as forecast
key 5; a callback era runs with the engine's own provenance; the
multipliers recompute live into the I3 harshness artifact's committed
values (self-verifying, never pasted); the J4 instruction-density
warm-up rides as a brotli-free evidence instrument over BOTH record
families; absence refuses with a named error.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _src in (ROOT / "game" / "src", ROOT / "packages" / "mecha_engine" / "src"):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))
if str(ROOT / "game") not in sys.path:
    sys.path.insert(0, str(ROOT / "game"))

from mecha_game.campaign import (  # noqa: E402
    TINY_ERA_CONFIG,
    WEATHER_NAMES,
    KeeperCampaign,
    build_weather_source,
    load_callback_weather_source,
    load_campaign_inputs,
)

import evidence  # noqa: E402

SEED_DIR = ROOT / "data" / "seed_grids_16x16"
SLIP_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
ADOPTED = (
    ROOT / "data" / "readability_benchmark" / "adopted_readability_model.json"
)
CALLBACK_STATES = (
    ROOT
    / "data"
    / "cubff_real_ingest"
    / "callback_states"
    / "callback_states_compact.json"
)
HARSHNESS_ARTIFACT = (
    ROOT / "data" / "game_client" / "real_weather_harshness_stage0.json"
)


class CallbackWeatherSourceTests(unittest.TestCase):
    def test_callback_is_the_fifth_named_forecast(self):
        self.assertIn("callback", WEATHER_NAMES)
        self.assertEqual("callback", WEATHER_NAMES[4])

    def test_the_source_is_the_committed_records_verbatim(self):
        payload = json.loads(CALLBACK_STATES.read_text(encoding="utf-8"))
        source = load_callback_weather_source()
        by_epoch = sorted(payload["records"], key=lambda r: r["epoch"])
        self.assertEqual(by_epoch, source)  # verbatim, epoch order
        for record in source:
            self.assertEqual(
                "real_cubff_python_state", record["source_type"]
            )
            # DR 0043 clause 3: honest lineage silence, not fabrication.
            self.assertEqual([], record["lineage_events"])
        self.assertEqual(source, build_weather_source("callback"))

    def test_absence_and_emptiness_refuse_with_named_errors(self):
        # data_search_origins ALWAYS includes the checkout (start is an
        # additional origin by design), so absence is simulated by
        # narrowing the origins for the call's duration.
        import mecha_game.packets as packets

        original = packets.data_search_origins
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            packets.data_search_origins = lambda start=None: [base]
            try:
                with self.assertRaises(FileNotFoundError) as context:
                    load_callback_weather_source()
                self.assertIn("callback", str(context.exception))
                states = base / CALLBACK_STATES.relative_to(ROOT)
                states.parent.mkdir(parents=True, exist_ok=True)
                states.write_text(
                    json.dumps({"records": []}), encoding="utf-8"
                )
                with self.assertRaises(ValueError) as context:
                    load_callback_weather_source()
                self.assertIn("no records", str(context.exception))
            finally:
                packets.data_search_origins = original


class CallbackWeatherEraTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(
            SEED_DIR, SLIP_PATH, ADOPTED, repair_epochs=6, seed_limit=12
        )
        cls.campaign = KeeperCampaign(
            cls.inputs, era_config=TINY_ERA_CONFIG, campaign_id="cw"
        )
        cls.era = cls.campaign.advance_era("callback")

    def test_a_callback_weather_era_runs(self):
        self.assertEqual("callback", self.era["weather"]["forecast"])
        self.assertEqual(
            len(self.era["report"]["generations"]),
            self.era["derived"]["generations_ran"],
        )

    def test_provenance_is_the_engines_own_per_generation_report(self):
        callback_ids = {
            record["snapshot_id"]
            for record in load_callback_weather_source()
        }
        reported = self.era["weather"]["snapshot_ids"]
        self.assertTrue(reported)
        for snapshot_id in reported:
            self.assertIn(snapshot_id, callback_ids)
        by_generation = self.era["report"]["cubff_pressure"][
            "by_generation"
        ]
        self.assertEqual(
            [entry["snapshot_id"] for entry in by_generation],
            reported,
        )

    def test_multipliers_recompute_into_the_committed_i3_values(self):
        # Self-verifying, never pasted: the era's engine math over the
        # committed records must land exactly on the I3 harshness
        # artifact's callback per-state multipliers.
        committed = {
            entry["snapshot_id"]: entry["dropout_multiplier"]
            for entry in json.loads(
                HARSHNESS_ARTIFACT.read_text(encoding="utf-8")
            )["metrics"]["callback_path"]["per_state"]
        }
        for entry in self.era["report"]["cubff_pressure"][
            "by_generation"
        ]:
            with self.subTest(snapshot=entry["snapshot_id"]):
                self.assertEqual(
                    committed[entry["snapshot_id"]],
                    entry["dropout_multiplier"],
                )

    def test_callback_weather_is_deterministic(self):
        twin = KeeperCampaign(
            self.inputs, era_config=TINY_ERA_CONFIG, campaign_id="cw"
        )
        era = twin.advance_era("callback")
        self.assertEqual(
            json.dumps(self.era, sort_keys=True),
            json.dumps(era, sort_keys=True),
        )


class ForecastDensityInstrumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = evidence.build_forecast_density_report()

    def test_report_is_complete_and_brotli_free(self):
        self.assertEqual("complete", self.report["status"])
        self.assertEqual(
            "forecast_density_stage0", self.report["artifact_id"]
        )
        self.assertIn("brotli-free", self.report["metrics"]["method"])
        self.assertNotIn("brotli", sys.modules.get("evidence").__dict__)

    def test_the_expectation_is_recomputed_not_pasted(self):
        metrics = self.report["metrics"]
        self.assertEqual(
            round(64 * 10 / 256, 6), metrics["random_expectation"]
        )
        self.assertEqual(10, metrics["instruction_byte_count"])

    def test_both_record_families_are_measured(self):
        sources = self.report["metrics"]["sources"]
        self.assertEqual({"real", "callback"}, set(sources))
        for name, entries in sources.items():
            with self.subTest(source=name):
                self.assertTrue(entries["per_record"])
                for record in entries["per_record"]:
                    self.assertGreaterEqual(
                        record["instruction_density"], 0
                    )
                    self.assertLessEqual(
                        record["instruction_density"], 64
                    )

    def test_the_warm_up_is_visible_without_brotli(self):
        # J4's finding on the game's own committed forecasts: early
        # soup already runs above the random expectation.
        metrics = self.report["metrics"]
        early = [
            record["instruction_density"]
            for entries in metrics["sources"].values()
            for record in entries["per_record"]
            if record["phase"] == "early_phase"
        ]
        self.assertTrue(early)
        self.assertGreater(
            sum(early) / len(early), metrics["random_expectation"]
        )


if __name__ == "__main__":
    unittest.main()
