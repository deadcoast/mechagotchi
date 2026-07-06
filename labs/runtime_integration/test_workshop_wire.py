import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAB_DIR = Path(__file__).resolve().parent
CA_DIR = ROOT / "labs" / "cellular_automata"
for path in [LAB_DIR, CA_DIR]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ca_nca_growth_repair import grid_from_matrix  # noqa: E402

from mecha_engine_runtime_loop import (  # noqa: E402
    run_mecha_engine_evolution_loop,
)


ALIGNED_MATRIX = [
    [".", "E", ".", ".", "E", ".", ".", "."],
    [".", ".", "B", "B", ".", ".", ".", "."],
    [".", "B", "A", "B", "B", ".", ".", "."],
    [".", ".", "B", "B", ".", "M", ".", "."],
    [".", ".", ".", "B", "B", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
    [".", ".", ".", ".", ".", ".", ".", "."],
]


def _workshop_grid(grid_id: str, palette_id: str, colors: list[str]) -> dict:
    return grid_from_matrix(
        grid_id=grid_id,
        matrix=ALIGNED_MATRIX,
        palette={
            "palette_id": palette_id,
            "colors": colors,
            "background_index": 0,
        },
        parent_grid_id=None,
        source="workshop_grid_editor",
        mutation_events=["workshop_grid_editor_draft"],
        generation_delta=0,
    )


class WorkshopWireEvolutionTests(unittest.TestCase):
    """T1: released workshop creatures become simulation founders."""

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        released = Path(cls.temp.name)
        # One creature the LCD profile accepts, one it must reject
        # (palette not allowed) — the rejection is a measured outcome.
        aligned = _workshop_grid(
            "workshop_hero", "lcd_green", ["#07140d", "#5dbb63", "#d8ffd6"]
        )
        rejected = _workshop_grid(
            "workshop_gray",
            "gameboy_gray",
            ["#1a1a1a", "#7a7a7a", "#dedede"],
        )
        (released / "workshop_hero.json").write_text(
            json.dumps(aligned), encoding="utf-8"
        )
        (released / "workshop_gray.json").write_text(
            json.dumps(rejected), encoding="utf-8"
        )
        cls.report = run_mecha_engine_evolution_loop(
            generations=3,
            population=6,
            damage_cycles=2,
            ticks=24,
            repair_epochs=40,
            rng_seed=20260512,
            workshop_grids_dir=released,
        )

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_workshop_founders_are_admitted_through_the_engine_gates(self):
        workshop = self.report["summary"]["workshop"]
        self.assertEqual(2, workshop["released_count"])
        self.assertEqual(["workshop_hero"], workshop["founder_ids"])
        self.assertEqual(1, len(workshop["rejected"]))
        rejected = workshop["rejected"][0]
        self.assertEqual("workshop_gray", rejected["grid_id"])
        # The engine's own alignment errors, verbatim.
        self.assertTrue(
            any("palette" in error for error in rejected["errors"])
        )

    def test_every_creature_carries_a_founder_source(self):
        sources = set()
        for generation in self.report["generations"]:
            for creature in generation["creatures"]:
                self.assertIn(
                    creature["founder_source"], ("workshop", "corpus")
                )
                sources.add(creature["founder_source"])
        # Founders lead the generation-0 pool, so the wire is exercised.
        self.assertIn("workshop", sources)
        self.assertIn("corpus", sources)

    def test_workshop_ancestry_is_traceable_through_generations(self):
        # T1.2: a later-generation workshop-lineage creature must carry
        # the founder's grid_id in its ancestor chain.
        traced = [
            creature
            for generation in self.report["generations"][1:]
            for creature in generation["creatures"]
            if creature["founder_source"] == "workshop"
        ]
        summary = self.report["summary"]["workshop"]
        self.assertEqual(
            len(traced) > 0, summary["lineage_survived_beyond_founding"]
        )
        for creature in traced:
            self.assertIn("workshop_hero", creature["ancestor_ids"])

    def test_summary_measures_the_workshop_lineage_honestly(self):
        workshop = self.report["summary"]["workshop"]
        for key in (
            "creature_count_by_generation",
            "archive_elite_count",
            "mean_fitness",
            "corpus_mean_fitness",
            "lineage_survived_beyond_founding",
        ):
            self.assertIn(key, workshop)
        by_gen = workshop["creature_count_by_generation"]
        self.assertEqual(3, len(by_gen))
        self.assertGreaterEqual(by_gen[0], 1)

    def test_artifact_identity_is_wire_specific(self):
        self.assertEqual(
            "mecha_engine_evolution_workshop_wire_stage0",
            self.report["lab_id"],
        )

    def test_without_workshop_dir_no_wire_keys_leak(self):
        report = run_mecha_engine_evolution_loop(
            generations=1,
            population=2,
            damage_cycles=1,
            ticks=8,
            repair_epochs=20,
            rng_seed=20260512,
        )
        self.assertNotIn("workshop", report["summary"])
        self.assertEqual(
            "mecha_engine_evolution_loop_stage0", report["lab_id"]
        )
        for creature in report["generations"][0]["creatures"]:
            self.assertNotIn("founder_source", creature)
            self.assertNotIn("ancestor_ids", creature)


if __name__ == "__main__":
    unittest.main()
