"""Learning contract surface for mecha_engine — the micro-switchboard learner.

Promoted eighth, per decision record 0009
(research/decision_records/0009-create-mecha-engine-learning-target.md,
accepted 2026-07-05). Public surface per
research/package_specs/mecha_engine_learning_interface_spec.md:

- ``decide(state) -> dict`` — the micro-switchboard decision: a verbatim
  port of the grid_genome research lab's ``run_switchboard`` (action,
  confidence, per-learner signal threads, explanation) over a lifecycle
  state from ``mecha_engine.lifecycle.initial_state``/``advance_tick``.
- ``ACTIONS`` — the supported action set, identical to the lab's.
- ``run_feedback_episode(grid, slip_profile, *, ticks=48,
  feedback_enabled=True, miscalibrate=True) -> dict`` — one deterministic
  episode driving ``mecha_engine.lifecycle`` publics with switchboard
  decisions; ``feedback_enabled=False`` resets action-reward histories
  every tick (the frozen comparator); ``miscalibrate=True`` applies the
  labs' deliberate reward miscalibration (the learnable-gap premise both
  recorded measurements share).

The bounded claim (load-bearing, per decision record 0009 and the
interface spec): this module's contract claim is **wellbeing, not
survival** — online reward feedback improves companion need balance
(measured +0.080069 under the stress regime, +0.03964 sheltered) at zero
survival cost (``lost_by_feedback_count = 0``). Survival is
morphology-decided under the current lifecycle bistability
(``feedback_beats_frozen_survival = false`` is recorded evidence), and no
surface, docstring, or report of this module claims survival improvement;
any future survival claim requires new evidence.

The lifecycle boundary holds: the learner lives here and drives lifecycle
only through its public surface; reward-shaping state (the feedback/frozen
switch and update count) lives in the episode loop, never inside
lifecycle. Learning is single-episode only — nothing persists at module
level or across episodes, matching the evidence bounds. The implementation
is self-contained package code (stdlib plus promoted mecha_engine modules,
no research lab imports) and performs no Stage 0 artifact writes on
import.
"""

from ._switchboard import ACTIONS, decide
from .episode import run_feedback_episode
from .threads import FLEET_THREAD_NAMES, fleet_signals, observe_fleet

# The fleet surface (cycle 14 F3b, additive export only — behavior
# unchanged): the D1 contract's ``observe_fleet``/``fleet_signals``
# already promoted in cycle 12 and consumed internally by ``decide``,
# exported for the consumer the Phase-D gate names — the GAME (beg
# timing, clip choice, mood display). The load-bearing opt-in rule is
# unchanged: without an explicit ``learning_switches[name] is True``
# both surfaces are silent and every frozen path stays byte-identical.
__all__ = [
    "ACTIONS",
    "FLEET_THREAD_NAMES",
    "decide",
    "fleet_signals",
    "observe_fleet",
    "run_feedback_episode",
]
