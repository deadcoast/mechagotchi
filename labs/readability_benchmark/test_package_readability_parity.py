"""Lab-side parity pin: ``runtime/_readability.py`` mirrors the lab
authority verbatim (C1, decision record 0025 — the ``_cubff``/``_slip``
mirror discipline).

Labs may import the package; that is how a port is pinned to lab
semantics. If the authorities change (``learned_readability.py`` for
the scorer/features, ``readability_benchmark.py`` for the structural
helpers), the package mirror must be resynced verbatim — this suite is
the drift guard, exercised over the whole seed corpus, generated
candidates, and degradation edge cases."""

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for path in [
    Path(__file__).resolve().parent,
    ROOT / "labs" / "grid_genome",
    ROOT / "packages" / "mecha_engine" / "src",
]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from corpus_builder import build_seed_grids  # noqa: E402
from learned_readability import (  # noqa: E402
    build_degradation_pairs,
    extract_readability_features,
    learned_readability_score,
    train_pairwise_ranker,
)

package_mirror = importlib.import_module("mecha_engine.runtime._readability")


class ReadabilityMirrorParityTests(unittest.TestCase):
    seeds: list[dict]

    @classmethod
    def setUpClass(cls):
        cls.seeds = build_seed_grids()
        pairs = build_degradation_pairs(
            cls.seeds[:12], rng_seed=20260707, pairs_per_family=6
        )
        cls.model = train_pairwise_ranker(pairs, rng_seed=20260707, epochs=40)
        # The anchored form the consumers carry (weights + reference).
        features = [
            extract_readability_features(seed) for seed in cls.seeds[:12]
        ]
        cls.anchored = {
            "weights": cls.model["weights"],
            "reference_features": {
                name: sum(f[name] for f in features) / len(features)
                for name in cls.model["weights"]
            },
        }

    def test_feature_extraction_identical_across_the_corpus(self):
        for seed in self.seeds:
            self.assertEqual(
                extract_readability_features(seed),
                package_mirror.extract_readability_features(seed),
                seed["grid_id"],
            )

    def test_scores_identical_across_the_corpus(self):
        for seed in self.seeds:
            self.assertEqual(
                learned_readability_score(seed, self.anchored),
                package_mirror.learned_readability_score(
                    seed, self.anchored
                ),
                seed["grid_id"],
            )

    def test_edge_cases_identical(self):
        edges = [
            {},  # everything missing
            {"grid_size": [0, 0], "cells": [], "palette": {}},
            {
                "grid_size": [8, 8],
                "cells": [
                    {"x": 0, "y": 0, "role": "body", "organ": "core"}
                ],  # no visuals, no anchors
                "palette": {"colors": [], "background_index": 0},
                "organs": {},
            },
        ]
        model = {"weights": dict.fromkeys(self.model["weights"], 1.0)}
        for grid in edges:
            self.assertEqual(
                extract_readability_features(grid),
                package_mirror.extract_readability_features(grid),
            )
            self.assertEqual(
                learned_readability_score(grid, model),
                package_mirror.learned_readability_score(grid, model),
            )


if __name__ == "__main__":
    unittest.main()
