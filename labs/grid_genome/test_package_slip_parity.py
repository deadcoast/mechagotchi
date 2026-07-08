"""Parity pin: lab SLIP authority vs the promoted ``mecha_engine.slip``.

DR 0027 (F2): the four private ``_slip`` mirrors collapsed into the
public tenth module after gate-1 reconciliation measured ZERO behavioral
divergences across five implementations (118 profiles x corruption
cases; 104 valid profiles x 20 seeds). This file is that reconciliation
made PERMANENT for the surviving pair: the Stage 0 lab authority
(``labs/grid_genome/slip.py``) and ``mecha_engine.slip`` must agree
EXACTLY — verdicts and error strings — over the whole frozen profile
corpus (valid + failure_cases + the SLIP zoo), systematic corruptions of
every profile, and grid alignment across the seed corpus. If the
authority changes, the package module must be resynced verbatim; this
suite is the drift guard.

Direction note: labs may import the package for regression evidence; the
reverse (package importing labs) stays forbidden, and this file lives on
the lab side precisely so the package tree keeps zero lab references.
"""

import json
import sys
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

import slip as lab_slip  # noqa: E402
from corpus_builder import build_seed_grids  # noqa: E402

from mecha_engine import slip as package_slip  # noqa: E402


def _profiles() -> list[tuple[str, dict]]:
    paths = []
    for sub in ("valid", "failure_cases", "zoo"):
        paths.extend(sorted((REPO_ROOT / "data" / "slips" / sub).glob("*.json")))
    return [
        (path.name, json.loads(path.read_text(encoding="utf-8")))
        for path in paths
    ]


def _corruptions(profile: dict):
    yield "bad_version", dict(profile, slip_version="9.9.9")
    stripped = json.loads(json.dumps(profile))
    stripped.pop("grid", None)
    yield "no_grid", stripped
    bad_species = json.loads(json.dumps(profile))
    bad_species["species_class"] = "Bad Case"
    yield "bad_species", bad_species
    bad_delib = json.loads(json.dumps(profile))
    bad_delib.setdefault("deliberation", {})["max_ticks"] = 99
    yield "bad_deliberation", bad_delib


class SlipAuthorityParityTests(unittest.TestCase):
    profiles: list[tuple[str, dict]]

    @classmethod
    def setUpClass(cls):
        cls.profiles = _profiles()
        cls.seeds = build_seed_grids()

    def test_the_corpus_is_substantial(self):
        self.assertGreaterEqual(len(self.profiles), 100)

    def test_validate_slip_agrees_exactly_over_corpus_and_corruptions(self):
        for name, profile in self.profiles:
            cases = [("as_is", profile)] + list(_corruptions(profile))
            for case_name, case in cases:
                with self.subTest(profile=name, case=case_name):
                    lab = lab_slip.validate_slip(case)
                    pkg = package_slip.validate_slip(case)
                    self.assertEqual(lab.ok, pkg.ok)
                    self.assertEqual(lab.errors, pkg.errors)

    def test_is_grid_aligned_agrees_exactly_over_seeds_and_profiles(self):
        valid_profiles = [
            (name, profile)
            for name, profile in self.profiles
            if lab_slip.validate_slip(profile).ok
        ]
        self.assertGreaterEqual(len(valid_profiles), 50)
        for name, profile in valid_profiles:
            for seed in self.seeds[:20]:
                with self.subTest(profile=name, seed=seed["grid_id"]):
                    lab = lab_slip.is_grid_aligned(seed, profile)
                    pkg = package_slip.is_grid_aligned(seed, profile)
                    self.assertEqual(lab.ok, pkg.ok)
                    self.assertEqual(lab.errors, pkg.errors)


if __name__ == "__main__":
    unittest.main()
