"""F15 gates — SLIP import/export: the covenant is shareable.

Export writes the ACTIVE covenant VERBATIM (spends included — it is
already an authority-validated SLIP, shareable as-is, the zoo's
convention). Import goes through two engine gates: the authority's
validation (refusals verbatim) and corpus compatibility (`evolve`'s
own no-seed-satisfies rule, checked with the engine's alignment);
a refused import applies NOTHING. An accepted import becomes the
campaign's NEW BASE covenant — a fresh species contract whose budget
recomputes from the earned facts.
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

from mecha_game.campaign import (  # noqa: E402
    TINY_ERA_CONFIG,
    KeeperCampaign,
    load_campaign_inputs,
)
from mecha_game.covenant import apply_covenant_change  # noqa: E402
from mecha_game.covenant_io import (  # noqa: E402
    export_covenant,
    import_covenant,
)

SEED_DIR = ROOT / "data" / "seed_grids_16x16"
SLIP_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
GRAY_SLIP = ROOT / "data" / "slips" / "valid" / "slip_gray_stable.json"
BAD_SLIP = (
    ROOT / "data" / "slips" / "failure_cases" / "slip_bad_version.json"
)
ADOPTED = (
    ROOT / "data" / "readability_benchmark" / "adopted_readability_model.json"
)


class CovenantIoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = load_campaign_inputs(
            SEED_DIR, SLIP_PATH, ADOPTED, repair_epochs=6, seed_limit=12
        )

    def _campaign(self) -> KeeperCampaign:
        return KeeperCampaign(
            self.inputs, era_config=TINY_ERA_CONFIG, campaign_id="io"
        )

    def test_export_is_the_active_covenant_verbatim(self):
        campaign = self._campaign()
        campaign.campaign["unlocks"].append(
            {
                "axis": "bloodline_depth",
                "tier": 1,
                "earned_era_index": 0,
                "metric_path": "test",
                "metric_value": 2,
                "threshold": 2,
            }
        )
        result = apply_covenant_change(
            campaign, deliberation_max_ticks=2
        )
        self.assertTrue(result["ok"])
        with tempfile.TemporaryDirectory() as tmp:
            path = export_covenant(campaign, Path(tmp) / "my_slip.json")
            exported = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(campaign.campaign["slip_profile"], exported)
        self.assertEqual(2, exported["deliberation"]["max_ticks"])

    def test_import_becomes_the_new_base_and_governs_eras(self):
        campaign = self._campaign()
        result = import_covenant(campaign, GRAY_SLIP)
        self.assertTrue(result["ok"], result.get("violations"))
        imported = json.loads(GRAY_SLIP.read_text(encoding="utf-8"))
        self.assertEqual(imported, campaign.campaign["slip_profile"])
        self.assertEqual(imported, campaign.base_profile)
        era = campaign.advance_era("calm")
        self.assertTrue(era["elites"])

    def test_an_invalid_import_is_refused_verbatim(self):
        campaign = self._campaign()
        before = json.loads(
            json.dumps(campaign.campaign["slip_profile"])
        )
        result = import_covenant(campaign, BAD_SLIP)
        self.assertFalse(result["ok"])
        self.assertTrue(result["violations"])
        self.assertTrue(
            any(
                "authority rejects" in violation
                for violation in result["violations"]
            )
        )
        self.assertEqual(before, campaign.campaign["slip_profile"])

    def test_a_corpus_incompatible_import_is_refused_named(self):
        campaign = self._campaign()
        incompatible = json.loads(
            SLIP_PATH.read_text(encoding="utf-8")
        )
        # Valid to the authority, satisfiable by NO corpus seed: an
        # impossible body-mass floor.
        incompatible["grid"]["body_mass_min"] = 200
        incompatible["grid"]["body_mass_max"] = 256
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "impossible.json"
            path.write_text(
                json.dumps(incompatible), encoding="utf-8"
            )
            result = import_covenant(campaign, path)
        self.assertFalse(result["ok"])
        self.assertTrue(
            any(
                "no seed grid satisfies" in violation
                for violation in result["violations"]
            )
        )

    def test_round_trip_is_identity(self):
        campaign = self._campaign()
        with tempfile.TemporaryDirectory() as tmp:
            path = export_covenant(campaign, Path(tmp) / "slip.json")
            result = import_covenant(campaign, path)
        self.assertTrue(result["ok"])
        self.assertEqual(
            self.inputs["slip_profile"],
            campaign.campaign["slip_profile"],
        )


if __name__ == "__main__":
    unittest.main()
