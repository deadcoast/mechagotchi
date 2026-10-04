# DR 0066: promote the measured learner as an explicit playable option

Date: 2026-10-04. Status: implemented; default adoption remains gated by R3.

Port the lab's bounded Q-table observe/signal and full-confidence follower into
promoted learning, preserving all constants, rounding, ties and explicit-True
switches. The complete Q1 instrument reproduces; the new package parity record
is `data/micro_threads/package_qtable_parity_stage0.json`.

The game selects `incumbent` or experimental `qtable` per new session. Persist
trained state on resume; refuse conflicting choices before writes; retain the
policy across succession, hatch and elite adoption while starting each new
life's table cold. Feeding stays keeper-mediated. Old saves remain incumbent.

Inspection found the current game uses lifecycle's frozen evaluator. Its five
kept threads observe/display but do not affect that evaluator. Add an explicit
evaluator argument after the engine reflexes, used only by the experimental
session. Do not silently replace the incumbent or quote lab welfare as a game
gain. Fix the public learner's missing CTM helpers, revealed by cold/warm
parity vectors, using the existing lab math.

Evidence: `research/experiment_reports/2026-10-04-playable-learning.md`.
Next: actual-game paired adoption gate; refusal retains this useful opt-in.
