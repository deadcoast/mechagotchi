"""F3 gates — live clip DRIVING through the documented graph.

The C2 transition graph is hub-and-spoke (idle the resting hub, every
state clip entering from and returning to it, self-loops everywhere),
and its PRE-REGISTERED validity metric judges exactly one kind of cut:
the LAST frame of the source to the FIRST frame of the target. The
driver therefore cuts ONLY at loop boundaries and routes illegal
direct edges through the idle hub — every emitted step is either an
intra-clip advance, a self-loop boundary, or a measured graph edge.
Pure and deterministic (the named Phase-C remainder #3, consumed).
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _src in (ROOT / "game" / "src", ROOT / "packages" / "mecha_engine" / "src"):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from mecha_game.clips import TRANSITIONS, ClipDriver  # noqa: E402

FRAME_COUNTS = {"idle": 4, "blink": 4, "sleep": 4, "beg": 4, "ill": 4}


def _drive(driver, targets):
    return [driver.step(target) for target in targets]


class GraphTests(unittest.TestCase):
    def test_the_documented_edges_are_mirrored(self):
        self.assertIn(("idle", "beg"), TRANSITIONS)
        self.assertIn(("beg", "idle"), TRANSITIONS)
        self.assertIn(("beg", "beg"), TRANSITIONS)
        self.assertNotIn(("beg", "sleep"), TRANSITIONS)
        self.assertNotIn(("sleep", "ill"), TRANSITIONS)


class ClipDriverTests(unittest.TestCase):
    def _driver(self):
        return ClipDriver(FRAME_COUNTS, initial_clip="idle")

    def test_same_target_advances_and_loops(self):
        driver = self._driver()
        steps = _drive(driver, ["idle"] * 6)
        self.assertEqual(
            [
                ("idle", 0),
                ("idle", 1),
                ("idle", 2),
                ("idle", 3),
                ("idle", 0),  # the self-loop boundary
                ("idle", 1),
            ],
            steps,
        )

    def test_legal_transition_cuts_only_at_the_loop_boundary(self):
        driver = self._driver()
        _drive(driver, ["idle"])  # frame 0
        steps = _drive(driver, ["beg"] * 5)
        # idle finishes its cycle (frames 1..3), THEN cuts to beg 0.
        self.assertEqual(
            [
                ("idle", 1),
                ("idle", 2),
                ("idle", 3),
                ("beg", 0),
                ("beg", 1),
            ],
            steps,
        )

    def test_illegal_edge_routes_through_the_idle_hub(self):
        driver = self._driver()
        _drive(driver, ["beg"] * 5)  # into beg (via idle completion)
        current, _ = driver.step("beg")
        self.assertEqual("beg", current)
        # beg -> sleep is not an edge: finish beg, pass through a full
        # idle cycle, then enter sleep.
        steps = _drive(driver, ["sleep"] * 12)
        clips = [clip for clip, _ in steps]
        self.assertIn("idle", clips)
        self.assertIn("sleep", clips)
        first_sleep = clips.index("sleep")
        self.assertTrue(all(c in ("beg", "idle") for c in clips[:first_sleep]))

    def test_every_emitted_cut_is_a_graph_edge_at_the_boundary(self):
        driver = self._driver()
        script = (
            ["idle"] * 3
            + ["beg"] * 9
            + ["sleep"] * 14
            + ["ill"] * 14
            + ["idle"] * 6
            + ["blink"] * 7
        )
        steps = _drive(driver, script)
        for (clip_a, frame_a), (clip_b, frame_b) in zip(steps, steps[1:]):
            if clip_a == clip_b and frame_b == frame_a + 1:
                continue  # intra-clip advance
            # Anything else is a cut: it must leave from the LAST frame,
            # land on the FIRST frame, and ride a documented edge.
            self.assertEqual(FRAME_COUNTS[clip_a] - 1, frame_a)
            self.assertEqual(0, frame_b)
            self.assertIn((clip_a, clip_b), TRANSITIONS)

    def test_deterministic(self):
        script = ["idle", "beg", "beg", "sleep", "sleep", "idle"] * 4
        first = _drive(self._driver(), script)
        second = _drive(self._driver(), script)
        self.assertEqual(first, second)

    def test_unknown_clip_refused(self):
        driver = self._driver()
        with self.assertRaises(ValueError):
            driver.step("moonwalk")


if __name__ == "__main__":
    unittest.main()
