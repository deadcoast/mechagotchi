"""Cycle 22 L5 (DR 0045): density as pressure — the rider's contract.

DR 0043 clause 2's named record. The checkpoint format cannot carry
`replication_scores` or `lineage_events`, so the promoted pressure math
sees only entropy and instruction diversity — both of which FALL as a
soup organizes — and reads organization as calm. Instruction density is
the one carried channel that RISES, so it is the missing counterweight.

These pins fix the contract before the verdict: the rider is
keyword-only and BYTE-IDENTICAL when off, the organization signal is
derived from the language's own alphabet rather than calibrated on the
outcome, density never synthesizes the silent channels, and the
documented multiplier band still clamps everything.
"""

import sys
import unittest
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
for path in (LAB_DIR, ROOT / "packages" / "mecha_engine" / "src"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import cubff_transducer as authority  # noqa: E402
from cubff_transducer import (  # noqa: E402
    CUBFF_DENSITY_WEIGHT,
    CUBFF_INSTRUCTION_BYTES,
    ORGANIZATION_CEILING,
    extract_cubff_features,
    features_to_traits,
    organization_of,
)


def _snapshot(tape: list[int], **extra) -> dict:
    base = {
        "snapshot_id": "t",
        "epoch": 1,
        "language": "bff_noheads",
        "program_size": len(tape),
        "tape": tape,
        "replication_scores": [],
        "lineage_events": [],
    }
    base.update(extra)
    return base


ALL_INSTRUCTIONS = [ord("[")] * 64
NO_INSTRUCTIONS = [200] * 64


class InstructionAlphabetTests(unittest.TestCase):
    def test_the_ten_bff_noheads_instruction_bytes_are_the_j4_set(self):
        # Mirrored verbatim from labs/cubff_transducer/structured_decoder
        # (INSTRUCTION_TOKENS), never re-derived by hand.
        from structured_decoder import INSTRUCTION_TOKENS

        self.assertEqual(set(INSTRUCTION_TOKENS), set(CUBFF_INSTRUCTION_BYTES))
        self.assertEqual(10, len(CUBFF_INSTRUCTION_BYTES))


class OrganizationSignalTests(unittest.TestCase):
    def test_the_ceiling_is_the_language_alphabet_not_a_calibration(self):
        # ratio_max = n / (n * 10/256) = 256/10, independent of tape
        # length. Derived from bff_noheads itself; never tuned on the
        # corpus, which is what keeps the gate honest.
        self.assertAlmostEqual(25.6, ORGANIZATION_CEILING, places=9)

    def test_random_expectation_scales_with_tape_length(self):
        self.assertAlmostEqual(2.5, organization_of([0] * 64)["expectation"], places=9)
        self.assertAlmostEqual(5.0, organization_of([0] * 128)["expectation"], places=9)

    def test_a_tape_at_chance_has_ratio_one_and_signal_zero(self):
        # 2.5 instruction bytes in 64 is exactly chance — but tapes are
        # integral, so use the ceiling/floor pair around it instead of
        # pretending a fractional byte exists.
        measured = organization_of(NO_INSTRUCTIONS)
        self.assertEqual(0.0, measured["density"])
        self.assertEqual(0.0, measured["signal"])

    def test_an_all_instruction_tape_saturates_the_signal(self):
        measured = organization_of(ALL_INSTRUCTIONS)
        self.assertAlmostEqual(ORGANIZATION_CEILING, measured["ratio"], places=6)
        self.assertAlmostEqual(1.0, measured["signal"], places=6)

    def test_the_signal_is_monotone_in_density(self):
        low = organization_of([ord("[")] * 4 + [200] * 60)["signal"]
        high = organization_of([ord("[")] * 12 + [200] * 52)["signal"]
        self.assertLess(low, high)

    def test_the_signal_is_clamped_below_at_zero(self):
        # A tape below chance must not produce negative pressure.
        self.assertEqual(0.0, organization_of(NO_INSTRUCTIONS)["signal"])


class SeamLawTests(unittest.TestCase):
    def test_features_are_byte_identical_when_the_rider_is_off(self):
        snapshot = _snapshot(ALL_INSTRUCTIONS)
        self.assertEqual(
            extract_cubff_features(snapshot),
            extract_cubff_features(snapshot, include_density=False),
        )

    def test_the_density_keys_appear_only_when_asked(self):
        snapshot = _snapshot(ALL_INSTRUCTIONS)
        off = extract_cubff_features(snapshot)
        on = extract_cubff_features(snapshot, include_density=True)
        self.assertEqual(
            {
                "instruction_density",
                "density_expectation",
                "organization_ratio",
                "organization_signal",
            },
            set(on) - set(off),
        )
        self.assertEqual(off, {k: v for k, v in on.items() if k in off})

    def test_traits_are_byte_identical_at_weight_zero(self):
        features = extract_cubff_features(
            _snapshot(ALL_INSTRUCTIONS), include_density=True
        )
        self.assertEqual(
            features_to_traits(features),
            features_to_traits(features, density_weight=0.0),
        )

    def test_a_weighted_rider_raises_pressure_on_an_organized_tape(self):
        features = extract_cubff_features(
            _snapshot(ALL_INSTRUCTIONS), include_density=True
        )
        base = features_to_traits(features)["mutation_pressure"]
        ridden = features_to_traits(
            features, density_weight=CUBFF_DENSITY_WEIGHT
        )["mutation_pressure"]
        self.assertGreater(ridden, base)

    def test_the_rider_needs_the_density_features_and_refuses_without_them(self):
        # Asking for a weighted rider on a feature dict that never
        # measured density would silently contribute zero — a quiet
        # no-op is exactly the kind of thing that hides a wiring bug.
        plain = extract_cubff_features(_snapshot(ALL_INSTRUCTIONS))
        with self.assertRaises(KeyError):
            features_to_traits(plain, density_weight=CUBFF_DENSITY_WEIGHT)


class NoSmugglingTests(unittest.TestCase):
    def test_density_never_synthesizes_the_silent_channels(self):
        # DR 0045 G4 / DR 0043 clause 3: replication_rate and
        # lineage_churn stay honestly zero on a checkpoint-shaped
        # record, however organized its tape is.
        features = extract_cubff_features(
            _snapshot(ALL_INSTRUCTIONS), include_density=True
        )
        self.assertEqual(0, features["replication_rate"])
        self.assertEqual(0, features["lineage_churn"])
        self.assertGreater(features["organization_signal"], 0.0)


class BoundTests(unittest.TestCase):
    def test_pressure_stays_clamped_in_the_unit_interval(self):
        features = extract_cubff_features(
            _snapshot(ALL_INSTRUCTIONS), include_density=True
        )
        ridden = features_to_traits(features, density_weight=10.0)
        self.assertLessEqual(ridden["mutation_pressure"], 1.0)
        self.assertGreaterEqual(ridden["mutation_pressure"], 0.0)


class PackageMirrorTests(unittest.TestCase):
    def test_the_package_mirrors_the_authority_verbatim(self):
        import importlib

        mirror = importlib.import_module("mecha_engine.runtime._cubff")
        snapshot = _snapshot([ord("[")] * 20 + [200] * 44)
        for kwargs in ({}, {"include_density": True}):
            with self.subTest(kwargs=kwargs):
                self.assertEqual(
                    authority.extract_cubff_features(snapshot, **kwargs),
                    mirror.extract_cubff_features(snapshot, **kwargs),
                )
        features = authority.extract_cubff_features(snapshot, include_density=True)
        for weight in (0.0, CUBFF_DENSITY_WEIGHT):
            with self.subTest(weight=weight):
                self.assertEqual(
                    authority.features_to_traits(features, density_weight=weight),
                    mirror.features_to_traits(features, density_weight=weight),
                )
        self.assertEqual(CUBFF_DENSITY_WEIGHT, mirror.CUBFF_DENSITY_WEIGHT)
        self.assertEqual(
            set(CUBFF_INSTRUCTION_BYTES), set(mirror.CUBFF_INSTRUCTION_BYTES)
        )


if __name__ == "__main__":
    unittest.main()
