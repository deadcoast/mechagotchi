# Algorithm Card: Coverage/QD Gates + the Plain-GA Baseline

## Purpose

Judge the dossier's MAP-Elites decision gate at the documented
protocol: archive coverage vs the niche space, coverage advantage over
a plain GA under identical budgets, and best-fitness tolerance —
booleans from paired-seed means, no sentiment (gap-analysis Phase E,
E4).

## Mathematical basis

- The documented gates: coverage ≥ 0.25 of the 512-niche space;
  MAP-Elites/GA coverage ratio ≥ 1.25; MAP-Elites mean best fitness ≥
  0.9 × the strongest arm's mean.
- Plain generational GA: truncation selection (top half by scalar
  fitness, deterministic tie-break), full replacement — the classical
  control isolating the archive mechanism.
- GA coverage = |{scale niches touched by ANY evaluated candidate}| /
  512 (the search-history reading — standard in QD comparisons and the
  most favorable to the GA).

## Inputs

Paired consecutive seeds (the documented ten), identical bootstraps,
budgets (20,480), the shared WFC variation operator, E1's frozen
edges, the calibrated Stage 0 fitness.

## Outputs

Per-run records both arms (coverage, QD, best fitness, bin spread; the
MAP-Elites runs carry full elite rosters for E5), and the three-gate
verdict from paired-seed means.

## Strengths

- The mechanism is isolated: everything shared except selection
  structure.
- Rule pre-registered; escalation from the three-seed adaptation to
  the documented ten seeds fixed in advance.
- Refutations return as plain booleans and get recorded.

## Weaknesses

- The shared-WFC design compresses the archive's relative advantage
  (the operator itself illuminates) — the 25% threshold predates the
  WFC adoption; see DR 0032.
- Twenty full-scale runs are machine-hours; the artifact is run-once
  evidence.

## Failure modes

- Near-threshold verdicts flapping with seed count — handled by
  running the full documented seed count (observed: converged, +22.9%
  → +22.6%).

## Integration risk

None directly (analysis lab); the disposition (DR 0032) governs the
archive module's standing.

## License status

Repo Apache-2.0 (DR 0028); stdlib only.

## Prototype result

Ten-seed verdict: coverage 0.549 (gate MET, 2.2×); best fitness
identical across arms (clause MET); GA advantage +22.6% vs ≥25%
(REFUTED, converged). E5 answers the family clause: 52 recurrent
families vs ≥5 (MET).

## Decision

**adopt** (the instrument and its verdicts; the MAP-Elites disposition
is DR 0032 — adopted with the refuted clause recorded and a named
re-opener).

## Go-No-Go gate

The gate IS this card's subject: 3 of 4 documented clauses met, one
refuted and dispositioned by DR 0032. NO-GO triggers for the
disposition are DR 0032's re-openers.

## Sources

- `labs/map_elites_archive/coverage_qd_gates.py` (+ `test_coverage_qd_gates.py`)
- `data/archives/coverage_qd_gates_stage0.json`
- `research/experiment_reports/2026-07-09-coverage-qd-gates.md`
- `research/decision_records/0032-map-elites-ga-gate-disposition.md`
