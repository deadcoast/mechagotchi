# Experiment Report: The Keepers + The Scale Harness — And an Honest Zero (Cycle 12 · ENGINE · D5)

Date: 2026-07-08

## WHY

The dossier's micro-learner ablation names five synthetic user models
(attentive, neglectful, erratic, punitive, exploratory) and 500
lifecycles per condition; the gap table demands the 100k-tick ×
500-lifecycle benchmark measuring welfare with and without threads —
wall-clock measured FIRST (the Phase A/B precedent, DR 0028: this was
the likeliest genuine NumPy trigger yet).

## WHAT

`labs/micro_threads/synthetic_keepers.py` (RED-first; the lab is now
76 tests): the five documented keepers as deterministic-under-seed
interaction policies over the companion surface (per tick a keeper may
inject a feed/play interaction; the switchboard drives all autonomous
behavior — attentive answers real needs, neglectful barely appears,
erratic acts on whim, punitive acts at the WRONG times, exploratory
probes in alternating bursts), and the two-arm benchmark: the frozen
switchboard vs the fully opted-in 11-thread fleet, paired seeds,
5 keepers × 100 lifecycles × 200 ticks per arm = the documented
100k ticks per arm. Welfare is the engine's own per-tick need
`balance` — no new statistics.

## FINDINGS

- **Wall-clock FIRST: stdlib holds.** Pilot 800 ticks in 0.129 s →
  projection 32.3 s for the full 2-arm benchmark; measured 17.9 s.
  The DR 0028 NumPy trigger is NOT met. The measured hotspot was
  `advance_tick`'s deepcopy of the growing history list (O(ticks²) per
  episode, 0.42 → 0.07 ms/tick once addressed); the bench loop reads
  each tick's balance and trims its own episode history — the engine
  is untouched.
- **The honest zero: welfare deltas are ~0%** (attentive −0.012%,
  neglectful −0.111%, erratic −0.027%, punitive −0.002%, exploratory
  −0.007%). The cause is measured, not guessed: the sheltered
  environment is welfare-SATURATED — every keeper's balance sits in
  [0.781, 0.791] with 100% survival, because the switchboard feeds its
  own companion autonomously. The frozen baseline has no headroom to
  beat, so no thread effect can show welfare value here.
- **The modeling insight this forces**: in the game's actual
  interaction model, feeding is a USER action — the companion begs,
  the keeper feeds. D6 must run the documented ablation gates in a
  keeper-dependent mode with real welfare headroom (autonomous feed
  removed or rationed), or record the ≥15% gate as failed in the
  sheltered mode. Recorded in `blocked_states`; nothing is fudged to
  manufacture a delta.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/micro_threads -p "test_synthetic_keepers.py"   # RED
ImportError (module synthetic_keepers does not exist)
PS> python -B -m unittest discover -s labs/micro_threads -p "test_*.py"   # GREEN
Ran 76 tests in 7.924s
OK
PS> python -B labs/micro_threads/synthetic_keepers.py
projected_full_benchmark_seconds: 32.3 / measured: 17.9 / stdlib_holds: true
attentive frozen 0.790672 fleet 0.790578 delta% -0.011889
...
The harness stands at the documented scale and the two-arm welfare
measurement is recorded honestly; the ablation verdicts belong to D6.
```

## Sources

- `labs/micro_threads/synthetic_keepers.py` (+ `test_synthetic_keepers.py`)
- `data/micro_threads/synthetic_keepers_stage0.json`
- `labs/micro_threads/thread_fleet.py`, `evidence_threads.py`
- `labs/lifecycle_sim/lifecycle_sim.py` (the balance metric)
- `docs/project-research/deep-research/01/deep-research.md` (the five models, the 500-lifecycle protocol)
- `research/decision_records/0028-license-and-dependency-policy.md` (measure first)
- `research/algorithm_cards/synthetic_keepers.md`
- `audits/TODO.md` (cycle 12 D5), `docs/gap-analysis.md` (Phase D)
