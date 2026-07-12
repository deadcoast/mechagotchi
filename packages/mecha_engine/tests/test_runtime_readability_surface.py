"""The learned-readability scoring surface (cycle 14 F4 — the game's
era loop is the consumer).

DR 0019 made the LEARNED model the primary legibility signal; DR 0025
ported the scorer verbatim into ``runtime._readability`` for the
promoted readability-selection path. The game's Keeper/era loop needs
the SAME scorer for `evolve`'s injected ``readability_scorer`` hook
(a client must never re-implement an engine number — DR 0021's first
law). This pins the additive export: `learned_readability_score` on
the runtime public surface, deterministic, bounded to [0, 1], scored
against the committed ADOPTED model artifact.

Import mechanics match ``tests/test_package_imports.py``: probes run
in a ``python -B -c`` subprocess whose PYTHONPATH points at this
package's own ``src``; this module never mutates the interpreter
module search path and never points the subprocess at lab code.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parents[1]
SRC_DIR = PACKAGE_ROOT / "src"

PROBE = f"""
import json
from pathlib import Path
from mecha_engine.runtime import learned_readability_score

grid = json.loads(Path(r"{REPO_ROOT}" ).joinpath(
    "data", "seed_grids_16x16", "mg_seed16_001_beetle.json"
).read_text(encoding="utf-8"))
adopted = json.loads(Path(r"{REPO_ROOT}").joinpath(
    "data", "readability_benchmark", "adopted_readability_model.json"
).read_text(encoding="utf-8"))
model = {{
    "weights": adopted["weights"],
    "reference_features": adopted["reference_features"],
}}
first = learned_readability_score(grid, model)
second = learned_readability_score(grid, model)
print(json.dumps({{"first": first, "second": second}}))
"""


def _probe() -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC_DIR)
    result = subprocess.run(
        [sys.executable, "-B", "-c", PROBE],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(PACKAGE_ROOT),
        timeout=120,
    )
    if result.returncode != 0:
        raise AssertionError(
            "readability surface probe failed: " + result.stderr
        )
    return json.loads(result.stdout)


class RuntimeReadabilitySurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = _probe()

    def test_score_is_bounded_and_deterministic(self):
        first = self.report["first"]
        self.assertIsInstance(first, float)
        self.assertGreaterEqual(first, 0.0)
        self.assertLessEqual(first, 1.0)
        self.assertEqual(first, self.report["second"])


if __name__ == "__main__":
    unittest.main()
