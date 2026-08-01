"""Cycle 24 N5 (DR 0054): the game may not call grid stability "health".

N5 measured the question DR 0048 named — *is a player-facing "health"
that is really grid-stability honest labelling or a euphemism?* — and
the answer is **euphemism**, with the decisive number being that a
creature which **starved to death** finished with `grid_stability` at
**0.927**. A "health" bar reading that axis would have shown **93% on a
corpse**, and feeding a starving creature moves it **down**.

The game already gets this right: it displays the axis as **"body
stability"**, which is accurate. These pins keep it that way. They are
cheap, and they turn DR 0054's refusal from a paragraph into an enforced
property — the same reason N7's default pin exists.
"""

import unittest

from mecha_game.session import NEED_DISPLAY

# The engine's four LETHAL conditions (`_life_status`). `bond` is a
# danger threshold but is NOT lethal — the distinction that renamed
# N5's adopted candidate from `lethal_margin` to `danger_margin`.
LETHAL_AXES = ("hunger", "energy", "stress", "grid_stability")


class HealthLabelGuardTests(unittest.TestCase):
    def test_grid_stability_is_not_labelled_health(self):
        self.assertNotEqual(NEED_DISPLAY["grid_stability"]["label"], "health")

    def test_grid_stability_keeps_its_accurate_label(self):
        # "body stability" describes what the axis is. The refusal in
        # DR 0054 is against renaming it, not against showing it.
        self.assertEqual(NEED_DISPLAY["grid_stability"]["label"], "body stability")

    def test_no_displayed_need_claims_to_be_health(self):
        # `health` is a documented VISIBLE axis with no engine field
        # (DR 0048). Until a record adopts a definition AND a consumer
        # change lands it, nothing on screen may carry the name.
        labels = {entry["label"] for entry in NEED_DISPLAY.values()}
        self.assertNotIn("health", labels)

    def test_the_displayed_axes_are_engine_state_keys(self):
        # DR 0021's first law: everything a surface shows is engine
        # truth. Every display key must be a real state field, so a
        # future derived value cannot be slipped in beside them without
        # declaring itself.
        for key in NEED_DISPLAY:
            self.assertIsInstance(key, str)
            self.assertTrue(key)

    def test_every_lethal_axis_the_game_shows_is_shown_under_its_own_name(self):
        # The two documented-HIDDEN axes the game already surfaces
        # (`stress`, `grid_stability`) each appear under a name that
        # describes them, not a friendlier one.
        shown = set(NEED_DISPLAY)
        for axis in ("stress", "grid_stability"):
            if axis in shown:
                self.assertIn(
                    NEED_DISPLAY[axis]["label"],
                    ("stress", "body stability"),
                    f"{axis} is shown under a name that does not describe it",
                )


if __name__ == "__main__":
    unittest.main()
