"""Parity pin: lab evolution loop vs promoted mecha_engine.runtime.

Runs the Stage 0 lab surface (``run_mecha_engine_evolution_loop``, the
authoritative research behavior behind
``data/runtime_integration/mecha_engine_evolution_loop_stage0.json``) and
the promoted package surface (``mecha_engine.runtime.evolve`` through the
package src layout) over the same seed corpus, SLIP profile, seeds, and
cycle parameters, and asserts the evolution records equal.

Documented equivalence scope: ``evolve`` reproduces the lab loop's
algorithm verbatim — the same per-creature seed arithmetic (``run_seed =
rng_seed + generation_index * 100000 + index``; damage seed ``run_seed *
10 + cycle``), the same per-cycle grid-id reassignment
(``{candidate_id}_c{cycle:02d}``), the same parent selection (generation 0
from the profile-aligned seed pool round-robin; later generations from
archive elites sorted by niche key round-robin), the same metrics-bundle
construction, archive insert/event-to-decision mapping, and the same
summary/decision derivations including the exact decision reason strings —
so the ``generations`` lists (every per-creature record: parent/candidate
ids, lineage generation, stage flags, full cycle digests, score digests,
archive decisions), the ``summary``, and the decision ``status`` and
``reason`` are compared for full equality. The models are trained through
the package functions on both sides (the lab loop itself imports
``mecha_engine.generation`` / ``mecha_engine.repair``, the established
parity-identical surfaces), and the lab's proxy ``score_readability`` is
injected as the package's ``readability_scorer`` (the interface spec's
"equivalent metrics hook"; no proxy scorer is ported into the package).

Comparison exclusions, decided here: report envelope keys outside
``generations``/``summary``/``decision`` are research-ledger surfaces and
differ by design — the lab report carries ``lab_id``
``mecha_engine_evolution_loop_stage0``, ``date``, ``purpose``,
``source_artifacts``, ``closed_states``, ``blocked_states``,
``repair_epochs``, and ``next_research_step``; the package report carries
``lab_id`` ``mecha_engine_runtime_evolve``, the parameter echo, and the
readability-visibility block. Within ``decision``, ``adoption`` also
differs by design (lab: ``lab_only_runtime_evidence``; package:
``package_runtime_surface``) — status and reason are the pinned content.

The live-cycle pin reproduces the lab's per-creature cycle records
directly through ``live_cycle`` for every generation-0 creature:
``rng_seed`` is the creature's ``run_seed`` (the documented factoring
constraint), so the factored function is bit-identical to the lab's
inline damage/repair/episode loop.

Direction note: labs may import the package for regression evidence; the
reverse (package importing labs) stays forbidden by the runtime interface
spec and decision record 0008, and this file lives on the lab side
precisely so the package tree keeps zero lab references.
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
from slip import is_grid_aligned  # noqa: E402

from mecha_engine_runtime_loop import (  # noqa: E402
    run_mecha_engine_evolution_loop,
)

from mecha_engine.generation import (  # noqa: E402
    generate_candidate,
    train_generation_model,
)
from mecha_engine.repair import train_repair_model  # noqa: E402
from mecha_engine.runtime import evolve, live_cycle  # noqa: E402


# Small but complete evolution: two generations (so archive elites
# genuinely become parents), the same configuration the lab's own
# evolution-loop test suite exercises.
PARITY_RNG_SEED = 20260512
PARITY_GENERATIONS = 2
PARITY_POPULATION = 3
PARITY_DAMAGE_CYCLES = 2
PARITY_TICKS = 24
PARITY_DROPOUT_RATE = 0.2
REPAIR_EPOCHS = 150
REPAIR_TRAINING_COUNT = 40  # the lab loop's benchmark training split


class PackageRuntimeParityTests(unittest.TestCase):
    seeds: list[dict]
    slip_profile: dict
    lab_report: dict
    package_archive: dict
    package_report: dict

    @classmethod
    def setUpClass(cls):
        cls.slip_profile = json.loads(
            (
                REPO_ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
            ).read_text(encoding="utf-8")
        )
        cls.seeds = build_seed_grids()
        # Both sides train through the package model surfaces (the lab loop
        # imports them itself), so the models are identical by construction.
        cls.generation_model = train_generation_model(cls.seeds)
        cls.repair_model = train_repair_model(
            cls.seeds[:REPAIR_TRAINING_COUNT],
            epochs=REPAIR_EPOCHS,
            rng_seed=PARITY_RNG_SEED,
        )
        cls.lab_report = run_mecha_engine_evolution_loop(
            generations=PARITY_GENERATIONS,
            population=PARITY_POPULATION,
            damage_cycles=PARITY_DAMAGE_CYCLES,
            ticks=PARITY_TICKS,
            dropout_rate=PARITY_DROPOUT_RATE,
            repair_epochs=REPAIR_EPOCHS,
            rng_seed=PARITY_RNG_SEED,
        )
        cls.package_archive, cls.package_report = evolve(
            cls.seeds,
            cls.slip_profile,
            cls.generation_model,
            cls.repair_model,
            readability_scorer=score_readability,
            generations=PARITY_GENERATIONS,
            population=PARITY_POPULATION,
            damage_cycles=PARITY_DAMAGE_CYCLES,
            ticks=PARITY_TICKS,
            dropout_rate=PARITY_DROPOUT_RATE,
            rng_seed=PARITY_RNG_SEED,
        )

    def test_generation_records_parity_every_creature(self):
        lab_generations = self.lab_report["generations"]
        package_generations = self.package_report["generations"]
        self.assertEqual(len(lab_generations), len(package_generations))
        for lab_generation, package_generation in zip(
            lab_generations, package_generations
        ):
            with self.subTest(generation=lab_generation["generation"]):
                for lab_creature, package_creature in zip(
                    lab_generation["creatures"],
                    package_generation["creatures"],
                ):
                    with self.subTest(
                        candidate=lab_creature["candidate_grid_id"]
                    ):
                        self.assertEqual(lab_creature, package_creature)
                self.assertEqual(lab_generation, package_generation)
        self.assertEqual(lab_generations, package_generations)

    def test_summary_parity(self):
        self.assertEqual(
            self.lab_report["summary"], self.package_report["summary"]
        )

    def test_decision_status_and_reason_parity(self):
        lab_decision = self.lab_report["decision"]
        package_decision = self.package_report["decision"]
        self.assertEqual(lab_decision["status"], package_decision["status"])
        self.assertEqual(lab_decision["reason"], package_decision["reason"])
        # The parity run itself must be the composed-green trajectory the
        # promotion evidence pins.
        self.assertEqual("evolution_loop_composed", package_decision["status"])

    def test_package_report_identifies_the_runtime_surface(self):
        self.assertEqual(
            "mecha_engine_runtime_evolve", self.package_report["lab_id"]
        )
        self.assertEqual(
            "mecha_engine_evolution_loop_stage0", self.lab_report["lab_id"]
        )

    def test_archive_matches_the_summary_it_reported(self):
        summary = self.package_report["summary"]
        self.assertEqual(
            summary["archive"]["filled_niches"],
            len(self.package_archive["elites"]),
        )

    def test_live_cycle_matches_lab_per_creature_cycle_records(self):
        # The factoring constraint: live_cycle takes the caller's run_seed
        # as rng_seed, so the factored per-creature loop reproduces every
        # generation-0 creature of the lab report bit-for-bit.
        seed_pool = [
            seed
            for seed in self.seeds
            if is_grid_aligned(seed, self.slip_profile).ok
        ]
        lab_creatures = self.lab_report["generations"][0]["creatures"]
        self.assertEqual(PARITY_POPULATION, len(lab_creatures))
        for index, lab_creature in enumerate(lab_creatures):
            with self.subTest(creature_index=index):
                parent = seed_pool[index % len(seed_pool)]
                run_seed = PARITY_RNG_SEED + 0 * 100000 + index
                candidate = generate_candidate(
                    parent,
                    self.generation_model,
                    self.slip_profile,
                    rng_seed=run_seed,
                )
                self.assertEqual(
                    lab_creature["candidate_grid_id"], candidate["grid_id"]
                )
                lived = live_cycle(
                    candidate,
                    self.slip_profile,
                    self.repair_model,
                    damage_cycles=PARITY_DAMAGE_CYCLES,
                    ticks=PARITY_TICKS,
                    dropout_rate=PARITY_DROPOUT_RATE,
                    rng_seed=run_seed,
                )
                self.assertEqual(lab_creature["cycles"], lived["cycles"])
                self.assertEqual(
                    lab_creature["stages"]["all_cycles_valid"],
                    lived["all_cycles_valid"],
                )
                self.assertEqual(
                    lab_creature["stages"]["all_cycles_aligned"],
                    lived["all_cycles_aligned"],
                )
                self.assertEqual(
                    f"{candidate['grid_id']}_c{PARITY_DAMAGE_CYCLES:02d}",
                    lived["final_grid"]["grid_id"],
                )


if __name__ == "__main__":
    unittest.main()
