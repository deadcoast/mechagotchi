"""F14 gates — the lineage browser: the Keeper's whole story.

Every line is a lineage RECORD field verbatim (the grid schema's own
lineage blocks — generation, ancestor_ids, mutation_events — plus the
session's born/died/cause facts). The additive `origin` field names
how each life began (founder / hatched / era_elite / succession) and
rides the save file; old saves without it stay loadable.
"""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _src in (ROOT / "game" / "src", ROOT / "packages" / "mecha_engine" / "src"):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from mecha_game.lineage import LineageBrowser  # noqa: E402
from mecha_game.session import (  # noqa: E402
    CompanionSession,
    load_session_inputs,
)

SEED_PATH = ROOT / "data" / "seed_grids_16x16" / "mg_seed16_001_beetle.json"
SLIP_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"


def _session(**kwargs) -> CompanionSession:
    grid, slip_profile, model = load_session_inputs(SEED_PATH, SLIP_PATH)
    return CompanionSession(grid, slip_profile, model=model, **kwargs)


def _run_to_death(session: CompanionSession, limit: int = 400) -> None:
    for _ in range(limit):
        if not session.alive:
            return
        session.advance()
    raise AssertionError("companion did not die within the limit")


class OriginTests(unittest.TestCase):
    def test_lives_carry_their_origin(self):
        session = _session(origin="hatched")
        self.assertEqual("hatched", session.lineage[0]["origin"])
        _run_to_death(session)
        session.succeed()
        self.assertEqual("succession", session.lineage[1]["origin"])

    def test_the_default_origin_is_founder(self):
        session = _session()
        self.assertEqual("founder", session.lineage[0]["origin"])

    def test_origin_rides_the_save_file_and_old_saves_load(self):
        session = _session(origin="era_elite")
        with tempfile.TemporaryDirectory() as tmp:
            path = session.save(Path(tmp) / "companion.json")
            resumed = CompanionSession.load(path)
            self.assertEqual(
                "era_elite", resumed.lineage[0]["origin"]
            )
            # An old save without origins stays loadable.
            import json

            payload = json.loads(path.read_text(encoding="utf-8"))
            for record in payload["lineage"]:
                record.pop("origin", None)
            path.write_text(json.dumps(payload), encoding="utf-8")
            legacy = CompanionSession.load(path)
            self.assertNotIn("origin", legacy.lineage[0])


class LineageBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = _session(name="story")
        _run_to_death(cls.session)
        cls.session.succeed()
        _run_to_death(cls.session)
        cls.session.succeed()
        cls.browser = LineageBrowser(cls.session.lineage)

    def test_the_story_opens_on_the_living_life(self):
        self.assertEqual(3, self.browser.count)
        self.assertEqual(self.browser.count - 1, self.browser.index)

    def test_paging_clamps(self):
        browser = LineageBrowser(self.session.lineage)
        browser.step()
        self.assertEqual(browser.count - 1, browser.index)
        for _ in range(browser.count + 3):
            browser.back()
        self.assertEqual(0, browser.index)

    def test_captions_are_record_fields_verbatim(self):
        browser = LineageBrowser(self.session.lineage)
        browser.back()  # the middle life: died, has a parent
        record = browser.current()
        caption = browser.caption()
        self.assertIn(record["grid_id"], caption)
        self.assertIn(record["origin"], caption)
        self.assertIn(str(record["died_age_ticks"]), caption)
        self.assertIn(record["death_cause"], caption)
        detail = browser.detail_lines()
        joined = "\n".join(detail)
        self.assertIn(str(record["parent_grid_id"]), joined)
        lineage_block = record["lineage"] or {}
        self.assertIn(
            str(lineage_block.get("generation", 0)), joined
        )

    def test_the_living_life_shows_no_death(self):
        browser = LineageBrowser(self.session.lineage)
        self.assertIn("alive", browser.caption())

    def test_an_empty_story_refuses(self):
        with self.assertRaises(ValueError):
            LineageBrowser([])


if __name__ == "__main__":
    unittest.main()
