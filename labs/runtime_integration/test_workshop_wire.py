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


class EvolveFounderContractTests(unittest.TestCase):
    """DR 0016 (T1.5): the wire semantics in the promoted evolve."""

    @classmethod
    def setUpClass(cls):
        import json as _json

        sys.path.insert(0, str(ROOT / "packages" / "mecha_engine" / "src"))
        sys.path.insert(0, str(ROOT / "labs" / "readability_benchmark"))
        from corpus_builder import build_seed_grids
        from readability_benchmark import score_readability
        from mecha_engine.generation import train_generation_model
        from mecha_engine.repair import train_repair_model
        from mecha_engine.runtime import evolve

        cls.evolve = staticmethod(evolve)
        cls.scorer = staticmethod(score_readability)
        cls.seeds = build_seed_grids()
        cls.slip = _json.loads(
            (ROOT / "data/slips/valid/slip_lcd_seed.json").read_text(
                encoding="utf-8"
            )
        )
        cls.generation_model = train_generation_model(cls.seeds)
        cls.repair_model = train_repair_model(
            cls.seeds[:6], epochs=20, rng_seed=20260512
        )
        cls.founders = [
            _workshop_grid(
                "founder_hero", "lcd_green",
                ["#07140d", "#5dbb63", "#d8ffd6"],
            ),
            _workshop_grid(
                "founder_gray", "gameboy_gray",
                ["#1a1a1a", "#7a7a7a", "#dedede"],
            ),
        ]

    def _run(self, **kwargs):
        return self.evolve(
            self.seeds,
            self.slip,
            self.generation_model,
            self.repair_model,
            readability_scorer=self.scorer,
            generations=1,
            population=3,
            damage_cycles=1,
            ticks=8,
            rng_seed=20260512,
            **kwargs,
        )

    def test_founders_admitted_through_the_engine_gates_and_lead(self):
        archive, report = self._run(founder_grids=self.founders)
        founders = report["founders"]
        self.assertEqual(["founder_hero"], founders["admitted_ids"])
        self.assertEqual(1, len(founders["rejected"]))
        self.assertTrue(
            any("palette" in e for e in founders["rejected"][0]["errors"])
        )
        generation = report["generations"][0]
        self.assertEqual("founders_plus_seed_pool", generation["parent_source"])
        self.assertEqual(
            "founder_hero", generation["creatures"][0]["parent_grid_id"]
        )

    def test_default_contract_is_untouched(self):
        archive, report = self._run()
        self.assertNotIn("founders", report)
        self.assertEqual(
            "seed_pool", report["generations"][0]["parent_source"]
        )
