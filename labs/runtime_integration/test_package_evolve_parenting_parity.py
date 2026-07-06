"""Parity pin: lab evolution parenting vs mecha_engine.runtime.evolve (T3.4).

The frozen v0.1 pin (``test_package_runtime_parity.py``) stays untouched.
This file adds the decision-record-0013 surface: a v0.2 profile carrying
``lineage_preferences.parent_selection`` must steer package ``evolve``
parenting exactly as it steers the lab loop — ``fitness_weighted`` orders
elite parents by ``(-fitness, niche)``, ``uniform`` keeps the frozen
niche-key round-robin — and default v0.1 flows carry no rung key.

Documented equivalence scope: full ``generations``/``summary`` record
parity is pinned for v0.2 profiles whose ONLY ladder field is
``lineage_preferences``. That field is not consumed by lifecycle, so the
lab loop's v0.1 projection onto package surfaces (``slip.v01_projection``,
DR 0012 rule 4) is behaviorally transparent and the two sides are
byte-comparable. Profiles carrying ``risk_tolerances`` or
``learning_switches`` are deliberately NOT full-run-compared here: the lab
loop still projects those fields away before its package calls while
package ``evolve`` now consumes them natively (DR 0013), so their episode
streams diverge by design until the lab drops its projection (the DR's
follow-up experiment, not this pin). Their per-module parity lives in
``labs/lifecycle_sim/test_package_lifecycle_v2_parity.py`` and
``labs/grid_genome/test_package_switchboard_v2_parity.py``.

Small models (20 repair epochs) keep the pin fast; both sides train
through the same package surfaces, so the models are identical by
construction — the same setup the frozen runtime parity pin documents.

Direction note: labs may import the package for regression evidence; the
reverse (package importing labs) stays forbidden by the runtime interface
spec, and this file lives on the lab side precisely so the package tree
keeps zero lab references.
"""

import json
import sys
import unittest
from pathlib import Path


LAB_DIR = Path(__file__).resolve().parent
REPO_ROOT = LAB_DIR.parents[1]
GRID_GENOME = REPO_ROOT / "labs" / "grid_genome"
READABILITY = REPO_ROOT / "labs" / "readability_benchmark"
PACKAGE_SRC = REPO_ROOT / "packages" / "mecha_engine" / "src"
for path in [LAB_DIR, GRID_GENOME, READABILITY]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from corpus_builder import build_seed_grids  # noqa: E402
from readability_benchmark import score_readability  # noqa: E402

from mecha_engine_runtime_loop import (  # noqa: E402
    run_mecha_engine_evolution_loop,
)

from mecha_engine.generation import train_generation_model  # noqa: E402
from mecha_engine.repair import train_repair_model  # noqa: E402
from mecha_engine.runtime import evolve  # noqa: E402


PARITY_RNG_SEED = 20260512
PARITY_KW = dict(
    generations=2,
    population=4,
    damage_cycles=1,
    ticks=8,
    rng_seed=PARITY_RNG_SEED,
)
REPAIR_EPOCHS = 20
REPAIR_TRAINING_COUNT = 40  # the lab loop's fixed training split


def _v2_profile(parent_selection: str) -> dict:
    profile = json.loads(
        (REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )
    profile["slip_version"] = "0.2.0"
    profile["lineage_preferences"] = {"parent_selection": parent_selection}
    return profile


def _generation_1_parents(report: dict) -> list[str]:
    return [
        creature["parent_grid_id"]
        for creature in report["generations"][1]["creatures"]
    ]


class PackageEvolveParentingParityTests(unittest.TestCase):
    seeds: list[dict]

    @classmethod
    def setUpClass(cls):
        cls.seeds = build_seed_grids()
        cls.generation_model = train_generation_model(cls.seeds)
        cls.repair_model = train_repair_model(
            cls.seeds[:REPAIR_TRAINING_COUNT],
            epochs=REPAIR_EPOCHS,
            rng_seed=PARITY_RNG_SEED,
        )

    def _package_report(self, slip_profile: dict) -> dict:
        _, report = evolve(
            self.seeds,
            slip_profile,
            self.generation_model,
            self.repair_model,
            readability_scorer=score_readability,
            dropout_rate=0.2,
            **PARITY_KW,
        )
        return report

    def _lab_report(self, slip_profile: dict | None) -> dict:
        return run_mecha_engine_evolution_loop(
            repair_epochs=REPAIR_EPOCHS,
            slip_profile=slip_profile,
            **PARITY_KW,
        )

    def test_fitness_weighted_parenting_records_match_the_lab(self):
        lab_report = self._lab_report(_v2_profile("fitness_weighted"))
        package_report = self._package_report(_v2_profile("fitness_weighted"))
        self.assertEqual("fitness_weighted", lab_report["parent_selection"])
        self.assertEqual(
            "fitness_weighted", package_report["parent_selection"]
        )
        self.assertEqual(
            "archive_elites_fitness_weighted",
            package_report["generations"][1]["parent_source"],
        )
        self.assertEqual(
            lab_report["generations"], package_report["generations"]
        )
        self.assertEqual(lab_report["summary"], package_report["summary"])

    def test_uniform_parenting_records_match_the_lab(self):
        lab_report = self._lab_report(_v2_profile("uniform"))
        package_report = self._package_report(_v2_profile("uniform"))
        self.assertEqual("uniform", package_report["parent_selection"])
        self.assertEqual(
            "archive_elites",
            package_report["generations"][1]["parent_source"],
        )
        self.assertEqual(
            lab_report["generations"], package_report["generations"]
        )
        self.assertEqual(lab_report["summary"], package_report["summary"])

    def test_the_two_modes_pick_different_parents_on_both_sides(self):
        lab_uniform = self._lab_report(_v2_profile("uniform"))
        lab_weighted = self._lab_report(_v2_profile("fitness_weighted"))
        package_uniform = self._package_report(_v2_profile("uniform"))
        package_weighted = self._package_report(_v2_profile("fitness_weighted"))
        self.assertNotEqual(
            _generation_1_parents(lab_uniform),
            _generation_1_parents(lab_weighted),
        )
        self.assertEqual(
            _generation_1_parents(lab_uniform),
            _generation_1_parents(package_uniform),
        )
        self.assertEqual(
            _generation_1_parents(lab_weighted),
            _generation_1_parents(package_weighted),
        )

    def test_default_v01_flows_carry_no_rung_key_on_either_side(self):
        lab_report = self._lab_report(None)
        package_report = self._package_report(
            json.loads(
                (
                    REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
                ).read_text(encoding="utf-8")
            )
        )
        self.assertNotIn("parent_selection", lab_report)
        self.assertNotIn("parent_selection", package_report)
        self.assertEqual(
            "archive_elites",
            package_report["generations"][1]["parent_source"],
        )
        self.assertEqual(
            lab_report["generations"], package_report["generations"]
        )
        self.assertEqual(lab_report["summary"], package_report["summary"])


if __name__ == "__main__":
    unittest.main()
