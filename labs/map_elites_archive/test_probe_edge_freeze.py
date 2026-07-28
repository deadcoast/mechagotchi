"""Pins for cycle 24 N2: freeze the probe's edges.

Written BEFORE the module (the RED run is pasted into the experiment
report). The pins assert the pre-registered RULE, the arithmetic, and
the three properties that make a freeze real rather than decorative:

1. the frozen set is the SAME DRAW the committed probe numbers were
   counted under (provenance),
2. a live re-derivation at the documented parameters still reproduces
   it (the parity pin — this is what makes drift FAIL the suite), and
3. it has not accidentally converged onto the incumbent geometry, which
   DR 0046 explicitly refused.

Measured values are never asserted; they are the study's output.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from probe_edge_freeze import (  # noqa: E402
    ARTIFACT_ID,
    FROZEN_EDGES_POINTER,
    PRE_REGISTERED_RULE,
    PROBE_DERIVATION_COUNT,
    PROBE_RNG_SEED,
    build_probe_edge_freeze_report,
    derive_probe_edges,
    judge_consumer_invariance,
    judge_provenance,
    judge_reproduction,
    judge_separation,
    load_committed_probe_headlines,
    load_frozen_probe_edges,
    load_recorded_probe_edges,
    probe_edges_for,
    write_probe_edge_freeze_artifacts,
)
from niche_scale_archive import (  # noqa: E402
    DEFAULT_RNG_SEED,
    SCALE_BINS_PER_AXIS,
    SCALE_DESCRIPTOR_NAMES,
)
from wfc_population_throughput import load_frozen_scale_edges  # noqa: E402


class ProvenanceConstantTests(unittest.TestCase):
    def test_frozen_parameters_are_the_committed_probe_parameters(self):
        # The freeze must capture the draw the committed numbers used —
        # freezing a DIFFERENT draw would silently redefine every
        # probe-side number in the ledger.
        self.assertEqual(PROBE_DERIVATION_COUNT, 600)
        self.assertEqual(PROBE_RNG_SEED, DEFAULT_RNG_SEED)

    def test_frozen_edges_pointer_is_a_stable_documented_path(self):
        self.assertEqual(FROZEN_EDGES_POINTER, "metrics.frozen_edges.edges")

    def test_rule_names_its_pre_registration_and_the_measured_bar(self):
        rule = PRE_REGISTERED_RULE.lower()
        self.assertIn("pre-registered", rule)
        self.assertIn("measured", rule)
        self.assertIn("provenance", rule)


class EdgeShapeTests(unittest.TestCase):
    def test_derived_edges_cover_every_axis_with_seven_interior_octiles(self):
        edges = derive_probe_edges(derivation_count=64, rng_seed=DEFAULT_RNG_SEED)
        self.assertEqual(sorted(edges), sorted(SCALE_DESCRIPTOR_NAMES))
        for name in SCALE_DESCRIPTOR_NAMES:
            self.assertEqual(len(edges[name]), SCALE_BINS_PER_AXIS - 1)
            self.assertEqual(edges[name], sorted(edges[name]))


class FrozenArtifactTests(unittest.TestCase):
    """The freeze itself — these are the pins that make drift fail."""

    def test_frozen_set_matches_the_draw_the_committed_probe_recorded(self):
        # reachability_probe_stage0.json records the edges its 508/512
        # was counted under. The frozen set MUST be that same object.
        self.assertEqual(load_frozen_probe_edges(), load_recorded_probe_edges())

    def test_live_rederivation_reproduces_the_frozen_set_exactly(self):
        # DR 0046 claimed the probe is "deterministic in practice under a
        # fixed default seed". This pin is what tests that claim on every
        # future run — if the derivation drifts, the suite fails.
        self.assertEqual(
            derive_probe_edges(
                derivation_count=PROBE_DERIVATION_COUNT, rng_seed=PROBE_RNG_SEED
            ),
            load_frozen_probe_edges(),
        )

    def test_frozen_probe_set_has_not_converged_onto_the_incumbent(self):
        # DR 0046 refused convergence. A freeze that quietly adopted the
        # incumbent edges would undo that record without saying so.
        self.assertNotEqual(load_frozen_probe_edges(), load_frozen_scale_edges())

    def test_frozen_and_incumbent_differ_on_visual_complexity(self):
        # M2 localised the split to this axis; the separation must be
        # visible where it was measured.
        self.assertNotEqual(
            load_frozen_probe_edges()["visual_complexity"],
            load_frozen_scale_edges()["visual_complexity"],
        )


class EdgeSourceSelectionTests(unittest.TestCase):
    """Frozen by default, live when the caller asks for another draw."""

    def test_documented_parameters_resolve_to_the_frozen_set(self):
        edges, source = probe_edges_for(
            derivation_count=PROBE_DERIVATION_COUNT, rng_seed=PROBE_RNG_SEED
        )
        self.assertEqual(source, "frozen")
        self.assertEqual(edges, load_frozen_probe_edges())

    def test_a_different_count_derives_live_and_says_so(self):
        # A caller asking for a different derivation wants a different
        # geometry; silently handing back frozen edges would make the
        # parameter a lie.
        edges, source = probe_edges_for(
            derivation_count=64, rng_seed=PROBE_RNG_SEED
        )
        self.assertEqual(source, "live")
        self.assertNotEqual(edges, load_frozen_probe_edges())

    def test_a_different_seed_derives_live_and_says_so(self):
        _, source = probe_edges_for(
            derivation_count=PROBE_DERIVATION_COUNT, rng_seed=PROBE_RNG_SEED + 1
        )
        self.assertEqual(source, "live")


class CommittedHeadlineTests(unittest.TestCase):
    def test_headlines_are_READ_from_the_artifacts_never_quoted(self):
        # The 52-vs-54 family count went stale because prose was quoted
        # instead of the artifact being read. These numbers come from the
        # committed artifacts every run.
        headlines = load_committed_probe_headlines()
        self.assertEqual(
            sorted(headlines), ["reached_by_generators", "support_ceiling"]
        )
        for value in headlines.values():
            self.assertIsInstance(value, int)
            self.assertGreater(value, 0)


class ProvenanceVerdictTests(unittest.TestCase):
    def test_identical_edges_are_provenance_matched(self):
        edges = {"symmetry": [0.1], "visual_complexity": [0.2]}
        judged = judge_provenance(frozen=edges, recorded=dict(edges))
        self.assertEqual(judged["verdict"], "provenance_matched")

    def test_any_difference_breaks_provenance(self):
        judged = judge_provenance(
            frozen={"symmetry": [0.1]}, recorded={"symmetry": [0.100001]}
        )
        self.assertEqual(judged["verdict"], "provenance_broken")

    def test_provenance_is_structural_with_no_tolerance(self):
        # The two are supposed to be the same object; a tolerance would
        # let a real redefinition pass as rounding.
        self.assertIn("no tolerance", judge_provenance(
            frozen={"a": [1.0]}, recorded={"a": [1.0]}
        )["basis"].lower())


class ReproductionVerdictTests(unittest.TestCase):
    def test_exact_reproduction_passes(self):
        edges = {"symmetry": [0.1, 0.2]}
        self.assertEqual(
            judge_reproduction(frozen=edges, live=dict(edges))["verdict"],
            "reproducible",
        )

    def test_drift_fails_and_reports_the_axis(self):
        judged = judge_reproduction(
            frozen={"symmetry": [0.1], "visual_complexity": [0.2]},
            live={"symmetry": [0.1], "visual_complexity": [0.3]},
        )
        self.assertEqual(judged["verdict"], "not_reproducible")
        self.assertEqual(judged["differing_axes"], ["visual_complexity"])


class SeparationVerdictTests(unittest.TestCase):
    def test_different_geometries_are_separated(self):
        judged = judge_separation(
            probe={"visual_complexity": [0.85]},
            incumbent={"visual_complexity": [0.86]},
        )
        self.assertEqual(judged["verdict"], "separated")
        self.assertAlmostEqual(judged["max_abs_delta"], 0.01, places=9)

    def test_identical_geometries_report_convergence(self):
        edges = {"visual_complexity": [0.85]}
        judged = judge_separation(probe=edges, incumbent=dict(edges))
        self.assertEqual(judged["verdict"], "converged")
        self.assertEqual(judged["max_abs_delta"], 0.0)


class ConsumerInvarianceTests(unittest.TestCase):
    """GATE 3 — measured floor, never assumed."""

    def test_zero_movement_is_invariant(self):
        judged = judge_consumer_invariance(
            movements={"support_ceiling": 0, "reached_by_generators": 0},
            floor=3.0,
        )
        self.assertEqual(judged["verdict"], "invariant")

    def test_small_movement_lands_within_the_measured_floor(self):
        judged = judge_consumer_invariance(
            movements={"support_ceiling": 2}, floor=3.0
        )
        self.assertEqual(judged["verdict"], "within_measured_floor")

    def test_movement_above_the_floor_is_material(self):
        judged = judge_consumer_invariance(
            movements={"support_ceiling": 9}, floor=3.0
        )
        self.assertEqual(judged["verdict"], "material")

    def test_the_worst_consumer_decides_the_verdict(self):
        judged = judge_consumer_invariance(
            movements={"support_ceiling": 0, "reached_by_generators": 9},
            floor=3.0,
        )
        self.assertEqual(judged["verdict"], "material")

    def test_non_positive_floor_is_refused(self):
        # M2's precedent, inherited: a zero floor makes every movement
        # infinitely significant. Measure it, never assume it.
        with self.assertRaises(ValueError):
            judge_consumer_invariance(movements={"support_ceiling": 1}, floor=0.0)

    def test_empty_movements_are_refused(self):
        with self.assertRaises(ValueError):
            judge_consumer_invariance(movements={}, floor=1.0)


class ArtifactTests(unittest.TestCase):
    def test_report_carries_every_required_artifact_key(self):
        report = build_probe_edge_freeze_report(
            evaluation_count=12,
            pool_count=12,
            evaluation_replicate_count=2,
            pool_replicate_count=2,
        )
        for key in (
            "artifact_id",
            "status",
            "date",
            "purpose",
            "source_artifacts",
            "parameters",
            "metrics",
            "closed_states",
            "blocked_states",
            "decision",
            "next_research_step",
        ):
            self.assertIn(key, report)
        self.assertEqual(report["artifact_id"], ARTIFACT_ID)

    def test_report_carries_the_frozen_edges_at_the_documented_pointer(self):
        report = build_probe_edge_freeze_report(
            evaluation_count=12,
            pool_count=12,
            evaluation_replicate_count=2,
            pool_replicate_count=2,
        )
        node = report
        for part in FROZEN_EDGES_POINTER.split("."):
            self.assertIn(part, node)
            node = node[part]
        self.assertEqual(sorted(node), sorted(SCALE_DESCRIPTOR_NAMES))

    def test_frozen_edges_carry_their_regeneration_provenance(self):
        report = build_probe_edge_freeze_report(
            evaluation_count=12,
            pool_count=12,
            evaluation_replicate_count=2,
            pool_replicate_count=2,
        )
        provenance = report["metrics"]["frozen_edges"]["provenance"]
        for key in ("recipe", "derivation_count", "rng_seed", "corpus", "regenerate"):
            self.assertIn(key, provenance)
        self.assertEqual(provenance["derivation_count"], PROBE_DERIVATION_COUNT)
        self.assertEqual(provenance["rng_seed"], PROBE_RNG_SEED)

    def test_source_artifact_paths_are_repo_relative(self):
        report = build_probe_edge_freeze_report(
            evaluation_count=12,
            pool_count=12,
            evaluation_replicate_count=2,
            pool_replicate_count=2,
        )
        for path in report["source_artifacts"]:
            self.assertFalse(Path(path).is_absolute())
            self.assertNotIn("\\", path)

    def test_artifact_round_trips_as_json(self):
        report = build_probe_edge_freeze_report(
            evaluation_count=12,
            pool_count=12,
            evaluation_replicate_count=2,
            pool_replicate_count=2,
        )
        with tempfile.TemporaryDirectory() as directory:
            written = write_probe_edge_freeze_artifacts(directory, report)
            self.assertEqual(len(written), 1)
            reloaded = json.loads(written[0].read_text(encoding="utf-8"))
        self.assertEqual(reloaded["artifact_id"], ARTIFACT_ID)
        self.assertEqual(reloaded["decision"]["rule"], PRE_REGISTERED_RULE)


if __name__ == "__main__":
    unittest.main()
