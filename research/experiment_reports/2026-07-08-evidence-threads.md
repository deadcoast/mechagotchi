# Experiment Report: The Evidence Threads — The Fleet Is 11 of 11 (Cycle 12 · ENGINE · D4)

Date: 2026-07-08

## WHY

The gap table names four evidence threads — mutation stability,
readability, SLIP compatibility, lineage survival — that stream the
engine's EXISTING measurements into the switchboard. D4's rule: wire,
never invent — every number a thread streams must already exist in a
canonical engine surface or record.

## WHAT

Four threads in `labs/micro_threads/thread_fleet.py` (RED-first; the
lab is now 67 tests) plus the wiring harness `evidence_threads.py`.
The archive interface spec's documented factoring carries over:
evidence is an INPUT bundle (`lifecycle_state["evidence"]`) computed
by the canonical surfaces; the threads convert it to D1-contract
signals with provenance-appropriate confidence:

- **`mutation_stability`** — streams
  `mecha_engine.archive._metrics.mutation_stability` (the calibrated
  cap-normalized metric). Confidence 1.0 (a deterministic
  measurement); a small additive mutate effect mirrors its meaning
  ((score − 0.5) × 0.2).
- **`readability`** — streams the F3 ADOPTED model's
  `learned_readability_score` (DR 0019: the learned signal is primary;
  the manual survey stays the fallback). Confidence = sharpness
  (|score − 0.5| × 2 — a learned opinion's distance from
  indifference); honestly effect-free (its consumers are
  generation/selection surfaces, never the action switchboard).
- **`slip_compat`** — streams the SLIP authority's `is_grid_aligned`
  verdict (the public surface). Confidence 1.0 (an authority verdict);
  effect-free.
- **`lineage_survival`** — streams the lineage record's facts (elite
  flag, generation, children counted from the parent-id chain in
  `data/lineage/lineage_stage0.json`). Confidence 1.0 (a record);
  effect-free.

Observe caches the bundle slice in thread state (signals survive the
loop dropping the key); without evidence every thread is honestly
silent (confidence 0, no effects). The package twin regenerated
mechanically; the opt-in rule keeps every frozen path byte-identical.

## FINDINGS (50 seed creatures, the LCD profile, the adopted model, the lineage graph)

- **THE WIRING PIN holds 50/50 on all four threads**: each thread's
  streamed output equals the canonical function's number
  byte-for-byte (mutation_stability 50/50, readability 50/50,
  slip_compat verdict+error-count 50/50, lineage record 50/50 of 50
  records found).
- Distributions recorded: readability mean 0.526 over the seed corpus
  (min 0.0037, max 0.913 — the adopted model discriminates), mutation
  stability mean 0.717, LCD alignment 10/50 (strict by design).
- **The documented fleet is 11 of ~11 named threads**: hunger, sleep/
  energy, boredom, attention predictors (D2), interaction timing (D2),
  the animation bandit (D3), HMM mood (D3), and the four evidence
  threads (D4) — all through the one D1 contract, all opt-in.

## Verification

```powershell
PS> python -B -m unittest discover -s labs/micro_threads -p "test_*.py"   # RED
ImportError: cannot import name 'lineage_survival_observe' from 'thread_fleet'
FAILED (errors=2)
PS> python -B -m unittest discover -s labs/micro_threads -p "test_*.py"   # GREEN
Ran 67 tests in 7.320s
OK
PS> python -B labs/micro_threads/evidence_threads.py
All four evidence threads stream their canonical numbers byte-for-byte
with honest provenance confidence.
```

Full lab sweep (19 suites) + the package suite: green.

## Sources

- `labs/micro_threads/evidence_threads.py` (+ `test_evidence_threads.py`)
- `labs/micro_threads/thread_fleet.py` (+ `test_thread_fleet.py`)
- `data/micro_threads/evidence_threads_stage0.json`
- `packages/mecha_engine/src/mecha_engine/archive/_metrics.py`
- `packages/mecha_engine/src/mecha_engine/runtime/_readability.py`
- `packages/mecha_engine/src/mecha_engine/slip/authority.py`
- `data/readability_benchmark/adopted_readability_model.json` (F3)
- `data/lineage/lineage_stage0.json`
- `research/decision_records/0019-learned-readability.md`
- `research/algorithm_cards/evidence_threads.md`
- `audits/TODO.md` (cycle 12 D4), `docs/gap-analysis.md` (Phase D)
