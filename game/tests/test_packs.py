"""F16 gates — community packs at the FORMAT rung.

One importable file (`mechagotchi_pack_v1`): SLIPs + creatures +
provenance. The BUILDER refuses invalid content with the engine's
verbatim errors (an invalid pack cannot be published); IMPORT judges
every item through the same gates and stages ONLY accepted items
into the existing inboxes (covenants → `keeper/covenants/`,
creatures → `keeper/released/` where the era admission gates judge
them again at run time) — per-item verdicts, nothing smoothed.
Distribution infrastructure stays Phase G.
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

from mecha_game.packs import (  # noqa: E402
    PACK_FORMAT,
    build_pack,
    import_pack,
    load_pack,
    write_pack,
)

SEED_DIR = ROOT / "data" / "seed_grids_16x16"
SLIP_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
GRAY_SLIP = ROOT / "data" / "slips" / "valid" / "slip_gray_stable.json"
BAD_SLIP = (
    ROOT / "data" / "slips" / "failure_cases" / "slip_bad_version.json"
)

PROVENANCE = {
    "author": "test_keeper",
    "source": "game/tests/test_packs.py",
    "created_date": "2026-07-12",
}


def _slip(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _creature() -> dict:
    return json.loads(
        (SEED_DIR / "mg_seed16_002_wisp.json").read_text(
            encoding="utf-8"
        )
    )


class BuildTests(unittest.TestCase):
    def test_a_pack_carries_its_content_verbatim(self):
        pack = build_pack(
            pack_id="test_pack",
            title="Test Pack",
            provenance=PROVENANCE,
            slips=[_slip(SLIP_PATH)],
            creatures=[_creature()],
        )
        self.assertEqual(PACK_FORMAT, pack["pack_format"])
        self.assertEqual([_slip(SLIP_PATH)], pack["slips"])
        self.assertEqual([_creature()], pack["creatures"])
        self.assertEqual(PROVENANCE, pack["provenance"])

    def test_the_builder_refuses_an_invalid_slip_verbatim(self):
        with self.assertRaises(ValueError) as caught:
            build_pack(
                pack_id="bad",
                title="Bad",
                provenance=PROVENANCE,
                slips=[_slip(BAD_SLIP)],
                creatures=[],
            )
        self.assertIn("slip_version", str(caught.exception))

    def test_the_builder_refuses_an_invalid_creature_verbatim(self):
        broken = _creature()
        broken["cells"] = broken["cells"][:2]  # disconnect the body
        with self.assertRaises(ValueError):
            build_pack(
                pack_id="bad",
                title="Bad",
                provenance=PROVENANCE,
                slips=[],
                creatures=[broken],
            )

    def test_write_load_round_trips(self):
        pack = build_pack(
            pack_id="rt",
            title="Round Trip",
            provenance=PROVENANCE,
            slips=[_slip(GRAY_SLIP)],
            creatures=[_creature()],
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = write_pack(pack, Path(tmp) / "pack.json")
            self.assertEqual(pack, load_pack(path))


class ImportTests(unittest.TestCase):
    def test_import_stages_accepted_items_with_verdicts(self):
        pack = build_pack(
            pack_id="starter",
            title="Starter",
            provenance=PROVENANCE,
            slips=[_slip(SLIP_PATH), _slip(GRAY_SLIP)],
            creatures=[_creature()],
        )
        with tempfile.TemporaryDirectory() as tmp:
            keeper = Path(tmp)
            path = write_pack(pack, keeper / "pack.json")
            report = import_pack(keeper, path)
            staged_covenants = sorted(
                p.name for p in (keeper / "covenants").glob("*.json")
            )
            staged_creatures = sorted(
                p.name for p in (keeper / "released").glob("*.json")
            )
        self.assertEqual("starter", report["pack_id"])
        self.assertEqual(2, len(report["slips"]))
        self.assertTrue(
            all(entry["ok"] for entry in report["slips"])
        )
        self.assertEqual(1, len(report["creatures"]))
        self.assertTrue(report["creatures"][0]["ok"])
        self.assertEqual(2, len(staged_covenants))
        self.assertEqual(1, len(staged_creatures))

    def test_a_tampered_pack_item_is_refused_and_not_staged(self):
        pack = build_pack(
            pack_id="tampered",
            title="Tampered",
            provenance=PROVENANCE,
            slips=[_slip(SLIP_PATH)],
            creatures=[],
        )
        pack["slips"][0]["slip_version"] = "9.9.9"  # post-build tamper
        with tempfile.TemporaryDirectory() as tmp:
            keeper = Path(tmp)
            path = Path(tmp) / "pack.json"
            path.write_text(json.dumps(pack), encoding="utf-8")
            report = import_pack(keeper, path)
            staged = list((keeper / "covenants").glob("*.json"))
        self.assertFalse(report["slips"][0]["ok"])
        self.assertTrue(report["slips"][0]["violations"])
        self.assertEqual([], staged)

    def test_a_non_pack_file_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "not_a_pack.json"
            path.write_text(json.dumps({"hello": 1}), encoding="utf-8")
            report = import_pack(Path(tmp), path)
        self.assertFalse(report["ok"])
        self.assertTrue(report["violations"])


if __name__ == "__main__":
    unittest.main()
