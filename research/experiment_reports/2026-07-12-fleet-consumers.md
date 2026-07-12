# Experiment Report: The Kept Fleet Cashes Out — the Game's Consumers (Cycle 14 · GAME · F3, second half)

Date: 2026-07-12

## WHY

The Phase-D gate's load-bearing remainder: the fleet's welfare
increment at the decision seam is ~0 because the frozen rules already
sit near the autonomous optimum — "the fleet's proven value
(prediction skill, personalization, interpretability) cashes out at
the GAME's consumers: beg timing, ui_hints, clip choice, mood
display." F3's second half wires those consumers.

**A correction first (recorded, not smoothed over):** the F3a report
claimed the kept threads needed PROMOTION into the package. Wrong —
cycle 12's D-phase had already ported the full fleet verbatim into
`mecha_engine.learning.threads` and wired it through `decide`'s
additive seam; what was missing was only the PUBLIC EXPORT (the
surface was not in `__all__`/the interface spec) and the consumers.
The F3a report and the regenerated bridge artifact carry the
correction.

## WHAT

**The additive export** (`mecha_engine.learning`): `observe_fleet`,
`fleet_signals`, `FLEET_THREAD_NAMES` join the public surface — zero
behavior change; the load-bearing opt-in rule (explicit
`learning_switches[name] is True`, else silent) is unchanged and now
pinned by `tests/test_learning_fleet_surface.py` (subprocess-probe
convention). The interface spec gained its "fleet surface" section
and the contract pin was updated WITH it, in the same change.

**The session opts in exactly the D6-kept five** (`KEPT_THREADS` in
`session.py`, citing the ablation artifact): hunger_forecast,
energy_forecast, interaction_timing, animation_bandit,
hidden_mood_hmm — dropped threads stay out of default profiles, per
D6, and successors keep the opt-in with FRESH per-companion memory
(the D1 threads are per-companion learners; caught RED-first — the
first succession dropped the switches). Each tick runs the D6 lab's
exact wiring order: `last_animation` = what the window actually
showed (the clip driver's emitted clip — the bandit's reward
attribution input), then `observe_fleet`, then the switchboard
decides with the kept signals riding its additive seam.

**The consumers, engine numbers verbatim:**

- **Beg timing** — the footer shows the hunger forecast and says
  "begs soon" exactly when the thread's OWN anticipatory feed effect
  fires (never a client threshold).
- **Clip choice** — when the engine selects plain idle and the kept
  bandit has a confident learned recommendation, `desired_clip()`
  returns the recommendation (packet-side, honestly effect-free —
  D3's design), and the graph driver walks to it.
- **Mood display** — the HMM's felt mood (MAP readout) with its
  entropy-honest confidence, alongside the reactive packet mood.
- The snapshot's `threads` block streams all five signals
  (output/confidence/explanation/effects) — the D1 shape, verbatim.

**Measured** (`data/game_client/fleet_consumers_stage0.json`, status
complete; an 80-tick attentive scripted life): exactly the kept five
stream; the threads WARM on the companion's own life —
hunger_forecast confidence 0.983, energy_forecast 0.869,
hidden_mood_hmm 0.763, interaction_timing 1.0 — and the bandit is
HONESTLY COLD (0.0: its recommendation must be earned from real
interaction feedback; nothing fabricated). Twin runs byte-equal.
**Decision divergence fleet-on vs fleet-off over the script: 0** —
consistent with D6's recorded ~0 welfare increment at the decision
seam; the fleet's game value is the display/timing/choice layer,
exactly as the gate said.

## Verification

RED → GREEN:

```powershell
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_learning_fleet_surface.py"
Ran 0 tests ... FAILED (errors=1)   # ImportError: FLEET_THREAD_NAMES not public
# after the export + spec + pin:
Ran 3 tests ... OK
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 294 tests ... OK
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 64 tests in 2.652s
OK
PS> uv run python -B game/evidence.py    # all four artifacts, statuses complete
PS> uv run python -B game/run_game.py --ticks 6 --keeper-dir <tmp>   # exit 0
```

## HONEST REMAINDER

1. **The bandit's recommendation must be earned in real play** — the
   scripted harness leaves it cold (confidence 0); the consumer path
   is pinned by a warmed-state test instead.
2. **The fleet changes no autonomous decision on the script** (0
   divergence) — expected per D6 and recorded; if a future consumer
   wants decision-seam influence it argues from new evidence.
3. **F4 remainders unchanged**: eras/saves (the archive
   scale-geometry seam may promote there), per-role motion (engine).

## Sources

- `audits/TODO.md` (cycle 14 F3), `research/experiment_reports/2026-07-08-phase-d-gate.md` (the named consumer remainder)
- `data/micro_threads/ablation_gates_stage0.json` (the kept/dropped verdicts)
- `research/package_specs/mecha_engine_learning_interface_spec.md` (the fleet-surface section, added with the pin)
- `packages/mecha_engine/src/mecha_engine/learning/__init__.py`, `packages/mecha_engine/tests/test_learning_fleet_surface.py`
- `game/src/mecha_game/{session,app}.py` (+ tests), `data/game_client/fleet_consumers_stage0.json`
- `research/experiment_reports/2026-07-12-render-bridge-client.md` (F3a, corrected)
