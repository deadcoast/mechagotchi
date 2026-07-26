"""Cycle 22 L1: the refusal-cause histogram over the adopted loop.

K2 recorded that the constrained arm logs ~22% generation failures and
left the CAUSE unmeasured — the failure records already carry their
error strings, but only ``len(failures)`` survives into the loop's
trajectory. These pins fix the instrument's contract: the loop gains an
additive refusal-collection seam (byte-identical when off, proven), the
classifier splits a refusal into its family and its individual reasons
without silently merging or dropping any, and the report's totals
self-verify against the loop's own independent counter.

The instrument NEVER changes generation behaviour: whatever it finds,
any generator fix it motivates is its own record with its own gates.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from evaluation_loop_scale import run_evaluation_loop  # noqa: E402

from generation_refusal_causes import (  # noqa: E402
    ARTIFACT_ID,
    UNCLASSIFIED_FAMILY,
    build_refusal_cause_report,
    classify_refusal,
    write_refusal_cause_artifacts,
)

TINY = dict(population=16, target_evaluations=64, rng_seed=31)

# Verbatim shapes from the promoted generator's raise sites
# (packages/mecha_engine/src/mecha_engine/generation/generate.py) —
# mirrored as TEXT for classification, never imported across the
# boundary. The parent-SLIP samples are measured strings from a real
# constrained_population run, not invented.
PARENT_SLIP = (
    "parent grid cannot satisfy SLIP constraints: "
    "palette crt_blue not allowed by SLIP"
)
PARENT_SLIP_TWO_REASONS = (
    "parent grid cannot satisfy SLIP constraints: "
    "palette gameboy_gray not allowed by SLIP; "
    "required organ role missing for SLIP: expression"
)
PARENT_VALIDATION = (
    "parent grid failed package genome validation before proposal "
    "generation: live cells must form one 8-connected region"
)
INVALID_CANDIDATE = (
    "constrained generation produced an invalid candidate mg_c_0007 "
    "(parent mg_seed16_001_beetle, rng_seed 20260709): "
    "live cells must form one 8-connected region"
)
MISALIGNED_CANDIDATE = (
    "constrained generation produced a SLIP-misaligned candidate "
    "mg_c_0007: palette crt_blue not allowed by SLIP"
)
SLIP_INVALID = "SLIP profile is invalid: profile_id must be a non-empty string"


class RefusalClassifierTests(unittest.TestCase):
    def test_every_documented_raise_site_gets_its_own_family(self):
        # Each raise site in the promoted generator is a DIFFERENT
        # diagnosis: a refused parent is a selection problem, an
        # invalid candidate is a generator problem. Collapsing them
        # would hide exactly what the instrument exists to find.
        families = {
            PARENT_SLIP: "parent_slip_misaligned",
            PARENT_VALIDATION: "parent_invalid",
            INVALID_CANDIDATE: "candidate_invalid",
            MISALIGNED_CANDIDATE: "candidate_slip_misaligned",
            SLIP_INVALID: "slip_profile_invalid",
        }
        for message, expected in families.items():
            with self.subTest(family=expected):
                self.assertEqual(expected, classify_refusal(message)["family"])

    def test_a_refusal_carrying_several_reasons_splits_into_all_of_them(self):
        # A single ValueError joins the authority's errors with "; ".
        # Counting the message once would undercount the reasons.
        classified = classify_refusal(PARENT_SLIP_TWO_REASONS)
        self.assertEqual(
            [
                "palette gameboy_gray not allowed by SLIP",
                "required organ role missing for SLIP: expression",
            ],
            classified["reasons"],
        )

    def test_reason_classes_drop_the_value_but_keep_the_colon_bearing_shape(self):
        # "required organ role missing for SLIP: expression" carries a
        # colon INSIDE the reason — the family split must take only the
        # first colon, and the reason class must survive it.
        classified = classify_refusal(PARENT_SLIP_TWO_REASONS)
        self.assertEqual(
            [
                "palette not allowed by SLIP",
                "required organ role missing for SLIP",
            ],
            classified["reason_classes"],
        )

    def test_the_same_reason_class_groups_across_different_values(self):
        first = classify_refusal(PARENT_SLIP)["reason_classes"]
        second = classify_refusal(
            "parent grid cannot satisfy SLIP constraints: "
            "palette pocket_plum not allowed by SLIP"
        )["reason_classes"]
        self.assertEqual(first, second)
        self.assertEqual(["palette not allowed by SLIP"], first)

    def test_an_unrecognized_refusal_is_named_never_silently_dropped(self):
        # The honesty rule: an unknown shape must be visible as
        # unknown, keeping its verbatim text, so a future generator
        # change cannot quietly vanish from the histogram.
        classified = classify_refusal("something nobody predicted happened")
        self.assertEqual(UNCLASSIFIED_FAMILY, classified["family"])
        self.assertEqual(
            ["something nobody predicted happened"], classified["reasons"]
        )
        self.assertEqual(
            ["something nobody predicted happened"], classified["reason_classes"]
        )

    def test_an_unnormalized_reason_keeps_its_verbatim_text_as_its_class(self):
        # A KNOWN family carrying an UNKNOWN reason must not be merged
        # into a neighbouring class — it keeps its own text and is
        # reported as unnormalized by the report.
        classified = classify_refusal(
            "parent grid cannot satisfy SLIP constraints: a brand new refusal"
        )
        self.assertEqual("parent_slip_misaligned", classified["family"])
        self.assertEqual(["a brand new refusal"], classified["reason_classes"])


class LoopRefusalSeamTests(unittest.TestCase):
    def test_the_seam_is_byte_identical_when_off(self):
        # The seam law: additive, byte-identical when off, PROVEN.
        implicit = run_evaluation_loop(**TINY)
        explicit = run_evaluation_loop(collect_refusals=False, **TINY)
        self.assertEqual(implicit, explicit)
        self.assertNotIn("refusal_collection", implicit)

    def test_collecting_refusals_changes_nothing_but_adds_one_key(self):
        # Turning the instrument ON must not perturb the run it
        # observes: every other key stays equal to the off run, and the
        # seam adds exactly one key.
        off = run_evaluation_loop(**TINY)
        on = run_evaluation_loop(collect_refusals=True, **TINY)
        self.assertEqual({"refusal_collection"}, set(on) - set(off))
        self.assertEqual(
            off, {k: v for k, v in on.items() if k != "refusal_collection"}
        )

    def test_the_records_total_equals_the_loops_own_independent_counter(self):
        # The self-verification pin: the trajectory's collapse_failures
        # is counted by a different line of code than the records are
        # collected by. They must agree.
        result = run_evaluation_loop(collect_refusals=True, **TINY)
        counted = sum(
            entry["collapse_failures"] for entry in result["trajectory"]
        )
        self.assertEqual(counted, len(result["refusal_collection"]["records"]))

    def test_attempts_are_counted_by_the_loop_that_makes_them(self):
        # The refusal RATE needs a denominator the instrument cannot
        # reconstruct from outside without duplicating the loop's own
        # pool arithmetic — so the loop reports it.
        result = run_evaluation_loop(collect_refusals=True, **TINY)
        collection = result["refusal_collection"]
        self.assertGreaterEqual(
            collection["generation_attempts_total"], len(collection["records"])
        )

    def test_every_record_names_its_generation_and_its_error(self):
        result = run_evaluation_loop(collect_refusals=True, **TINY)
        for record in result["refusal_collection"]["records"]:
            self.assertIn("generation_index", record)
            self.assertIn("error", record)
            self.assertIn("parent_grid_id", record)

    def test_the_collection_is_deterministic_under_the_seed(self):
        # The loop's determinism law extends to what it observes: an
        # instrument whose readings drift between identical runs cannot
        # diagnose anything.
        first = run_evaluation_loop(collect_refusals=True, **TINY)
        second = run_evaluation_loop(collect_refusals=True, **TINY)
        self.assertEqual(
            first["refusal_collection"], second["refusal_collection"]
        )

    def test_the_seam_is_self_consistent_on_the_wfc_arm_too(self):
        # The seam belongs to the LOOP, not to one arm. WFC's refusal
        # count is an observation this pin deliberately does NOT fix
        # (H-01) — only the invariant is asserted.
        result = run_evaluation_loop(
            generation="wfc", collect_refusals=True, **TINY
        )
        counted = sum(
            entry["collapse_failures"] for entry in result["trajectory"]
        )
        self.assertEqual(counted, len(result["refusal_collection"]["records"]))


class RefusalCauseReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_refusal_cause_report(**TINY)

    def test_the_report_carries_the_stage0_contract(self):
        for key in (
            "artifact_id",
            "status",
            "date",
            "purpose",
            "source_artifacts",
            "metrics",
            "closed_states",
            "blocked_states",
            "decision",
            "next_research_step",
        ):
            with self.subTest(key=key):
                self.assertIn(key, self.report)
        self.assertEqual(ARTIFACT_ID, self.report["artifact_id"])

    def test_the_decision_records_that_this_is_an_instrument(self):
        # Pre-registered: L1 observes, it never changes generation.
        # A future fix is its own record with its own gates.
        self.assertEqual("instrument", self.report["decision"]["kind"])

    def test_the_histogram_totals_reconcile_with_the_record_count(self):
        metrics = self.report["metrics"]
        self.assertEqual(
            metrics["refusals_total"],
            sum(metrics["family_histogram"].values()),
        )

    def test_the_reason_histogram_counts_reasons_not_messages(self):
        # A refusal carrying two reasons contributes to two classes,
        # so the reason total is >= the refusal total — never less.
        metrics = self.report["metrics"]
        self.assertGreaterEqual(
            sum(metrics["reason_class_histogram"].values()),
            metrics["refusals_total"],
        )

    def test_unclassified_and_unnormalized_are_reported_not_hidden(self):
        metrics = self.report["metrics"]
        self.assertIn("unclassified_messages", metrics)
        self.assertIn("unnormalized_reasons", metrics)

    def test_the_failure_rate_is_measured_against_attempts_not_guessed(self):
        metrics = self.report["metrics"]
        self.assertIn("generation_attempts_total", metrics)
        self.assertIn("refusal_rate", metrics)

    def test_the_refused_parents_origin_is_measured_by_membership(self):
        # Origin separates "it came from the bootstrap, which the corpus
        # generators build without the SLIP in hand" from "the loop's
        # own generate_candidate produced it" — and the latter would be
        # a contradiction, since that path refuses to EMIT a
        # SLIP-misaligned candidate. It is measured by membership in the
        # bootstrap population, never inferred from lineage depth: a
        # bootstrap creature is itself generated from a seed, so its
        # depth is already 1 and depth would mislabel it.
        origin = self.report["metrics"]["refused_parent_origin"]
        self.assertEqual(
            self.report["metrics"]["refusals_total"], sum(origin.values())
        )
        self.assertTrue(set(origin) <= {"bootstrap", "loop_offspring"})

    def test_lineage_depth_is_reported_separately_from_origin(self):
        # They answer different questions; conflating them is the
        # mislabeling this pin exists to prevent.
        metrics = self.report["metrics"]
        self.assertIn("refused_parent_lineage_depth", metrics)
        self.assertEqual(
            metrics["refusals_total"],
            sum(metrics["refused_parent_lineage_depth"].values()),
        )

    def test_the_artifact_writes_and_reloads(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = write_refusal_cause_artifacts(Path(tmp), self.report)
            self.assertTrue(written)
            for path in written:
                reloaded = json.loads(Path(path).read_text(encoding="utf-8"))
                self.assertEqual(ARTIFACT_ID, reloaded["artifact_id"])


if __name__ == "__main__":
    unittest.main()
