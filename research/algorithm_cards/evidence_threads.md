# Algorithm Card: Evidence Threads

## Purpose

The four documented evidence threads (gap-analysis Phase D, D4) —
mutation stability, readability, SLIP compatibility, lineage
survival — streaming the engine's EXISTING measurements through the
D1 fleet contract with provenance-appropriate confidence. Completes
the documented ~11-thread fleet.

## Mathematical Basis

- No new statistics: each thread streams a canonical surface's number
  verbatim — `archive._metrics.mutation_stability` (cap-normalized),
  `runtime._readability.learned_readability_score` under the F3
  adopted model, `slip.is_grid_aligned`'s verdict, and the lineage
  record's (elite, generation, children-from-parent-chain).
- Evidence is an INPUT bundle (`lifecycle_state["evidence"]`) computed
  by the canonical surfaces — the archive interface spec's documented
  input factoring applied to learning.
- Confidence by provenance: 1.0 for deterministic measurements and
  authority verdicts; sharpness (|score − 0.5| × 2) for the learned
  readability opinion.
- Effects: mutation_stability adds (score − 0.5) × 0.2 to mutate;
  the other three are honestly effect-free (their consumers are
  generation/selection/packet surfaces, not action arbitration).

## Inputs

- `lifecycle_state["evidence"]` per creature (the loop provides it;
  the D4 harness builds it via the canonical functions)

## Outputs

- D1-contract signals carrying the canonical numbers;
  `data/micro_threads/evidence_threads_stage0.json`

## Strengths

- THE WIRING PIN: 50/50 byte-equality with the canonical surfaces on
  every thread over the seed corpus
- Readability rides as the DR 0019 primary signal (survey = fallback)
- Cold start honest everywhere; frozen paths byte-identical (opt-in)

## Weaknesses

- The live loop does not yet build the evidence bundle — D5's harness
  provides it; runtime wiring lands with its consumer
- Three of four threads are effect-free: D6's ablation judges them on
  their documented metrics (selection quality, interpretability), not
  action welfare alone

## Failure Modes

- A stale bundle streams stale evidence — the cache is per-companion
  state, refreshed whenever the loop re-provides the key
- A missing lineage record keeps that thread silent (measured: 50/50
  seeds have records in the current graph)

## Integration Risk

Minimal: pure pass-through threads behind the opt-in rule; the package
twin is mechanically regenerated and parity-pinned.

## License Status

Original stdlib-only code, Apache-2.0.

## Prototype Result

67 lab tests green; harness report `status: complete` — all wiring
pins hold; readability mean 0.526 (min 0.0037 / max 0.913) over the
seeds; mutation stability mean 0.717; LCD alignment 10/50.

## Decision

**Adopt into the fleet — the fleet is 11 of ~11.** Go gate for D5:
the five documented synthetic user models and the 100k-tick ×
500-lifecycle welfare benchmark (wall-clock measured FIRST, DR 0028).

## Sources

- `labs/micro_threads/evidence_threads.py` (+ `test_evidence_threads.py`)
- `labs/micro_threads/thread_fleet.py` (+ `test_thread_fleet.py`)
- `data/micro_threads/evidence_threads_stage0.json`
- `research/experiment_reports/2026-07-08-evidence-threads.md`
- `research/decision_records/0019-learned-readability.md`
- `audits/TODO.md` (cycle 12 D4), `docs/gap-analysis.md` (Phase D)
