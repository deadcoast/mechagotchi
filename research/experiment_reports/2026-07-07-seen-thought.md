# Experiment Report: The Seen Thought (F1) — Deliberation Reaches the Replay

Date: 2026-07-07

## WHY

E5's audit found DR 0021's notice 2 half-alive: creatures genuinely
THINK (R1's confidence-gated deliberation changes decisions; C4's
covenant spends into `deliberation.max_ticks`) but could never be SEEN
thinking — `choose_action` returned only the action string, discarding
the switchboard decision's `deliberation` record before episode
history. No replay or page could render a thinking pause. The engine
grows the number first; F1 grows it.

## WHAT — RED-first, verbatim across both authorities

- **The plumbing** — `choose_action_detailed(policy, state, rng) ->
  (action, record | None)`: idle/random and the reflex quick-paths
  return `None` (reflexes don't think); switchboard ticks return the
  decision's own R1 record. `choose_action` delegates and stays
  byte-identical. `advance_tick(state, action, deliberation=None)`
  appends the record to the history entry as a RUNG-CONDITIONAL key.
  Implemented identically in the lab authority
  (`labs/lifecycle_sim/lifecycle_sim.py`) and the package
  (`lifecycle/_policy.py` + `simulate.py`).
- **The pins** — `labs/lifecycle_sim/test_deliberation_history.py`
  (RED first: "no thought reached history"): thoughts ride history on
  BOTH authorities with identical histories; counts bounded by the
  covenant's `max_ticks`; no-deliberation flows, idle/random policies,
  and reflex ticks carry no key anywhere. The lifecycle contract driver
  gained the `deliberation_history` probe (bounded counts, frozen-flow
  byte-identity, idle-never-thinks, determinism).
- **The window** — replay tick frames carry the record automatically
  (they are history entries verbatim), and both scrubbers now render it
  ("· thought 3 ticks"). End-to-end pin: a replay recorded under a
  thinking covenant carries bounded thoughts in its tick frames while
  the v0.1 replay stays thought-free.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/lifecycle_sim -p "test_deliberation_history.py"
Ran 5 tests in 0.022s
OK    # was RED: "lab: no thought reached history"

PS> foreach: labs/lifecycle_sim (24) OK · labs/grid_genome (173) OK ·
    labs/runtime_integration (65) OK · labs/game_loop (68→69 w/ the
    thinking-replay pin) OK · packages (281→282) OK · workshop OK
```

Every frozen pin passes unmodified — the rung-conditional key means
v0.1 and reflex histories are byte-identical, exactly as the R1/DR 0013
ladder discipline requires.

## The notice closes

DR 0021 notice 2 is now fully live end to end: earn bloodline tiers →
spend them into `deliberation.max_ticks` (C4) → the species' creatures
deliberate when torn (R1) → the thought rides the episode history (F1)
→ the era replay records it (C5/DR 0023) → the Keeper scrubs to a tick
and reads "thought 3 ticks". Every link is engine truth; the E5 audit's
"four of five" becomes five of five.

## Sources

- `research/experiment_reports/2026-07-07-five-notices-audit.md` (the seed)
- `research/experiment_reports/2026-07-06-ctm-deliberation-live.md` (R1)
- `labs/lifecycle_sim/lifecycle_sim.py`, `labs/lifecycle_sim/test_deliberation_history.py`
- `packages/mecha_engine/src/mecha_engine/lifecycle/_policy.py` + `simulate.py`
- `packages/mecha_engine/tests/test_lifecycle_contract.py` (+ driver)
- `labs/game_loop/test_replay_recorder.py` (the thinking-replay pin)
- `workshop/preview/preview.html`, `workshop/session/session.html`
- `research/package_specs/mecha_engine_lifecycle_contract_gate.md`
