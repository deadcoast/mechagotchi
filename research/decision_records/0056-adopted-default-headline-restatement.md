# Decision Record 0056: The Adopted Default's Headline Numbers — DR 0042 Restated, Not Retracted

Date: 2026-07-28

## Status

**ACCEPTED.** The loop's headline numbers under the adopted
`slip_admission="insertion"` default are recorded, the documented E4
gates are re-judged and **hold**, and **DR 0042's numbers are not
retracted** — they remain what the loop achieves under the incumbent.

## Context

DR 0053 flipped the default prospectively and named the only two studies
whose migration was a real question. O3 restated both, without
overwriting either committed artifact, because DR 0053's rule 2 makes
this **a new measurement answering a new question** rather than a
regeneration.

## The restated headline

At DR 0042's own seed, population and budget:

| | incumbent (`none`) | adopted (`insertion`) | delta |
| --- | --- | --- | --- |
| coverage | 0.898438 | **0.880859** | −0.017579 |
| **QD** | 404.618236 | **411.738214** | **+7.119978** |
| occupied niches | 460 | 451 | −9 |
| refusals | 4,435 | **0** | −4,435 |
| SLIP-illegal elites | 35 | **0** | −35 |

**Coverage does not fall for nothing — it buys quality.** L1 refused to
patch the refusal tax because *"the fix trades against coverage"*. It
does, and this prices the other side: **nine niches and 0.0176 coverage
buy +7.12 QD, the removal of 4,435 wasted evaluations per run, and an
archive legal under the covenant that bred it.**

## The documented E4 gates: `NO_REGRESSION`

Re-judged **verbatim** (`judge_gates` imported, never re-implemented)
over the documented ten paired seeds, against the **same GA control**:

| gate | incumbent | adopted | |
| --- | --- | --- | --- |
| `coverage_gate_met` | True | **True** | held |
| `ga_advantage_gate_met` | False | False | already failing — **not** a regression |

Mean best fitness moves **−0.000565**. No documented gate that passed
now fails.

## Decision

**1. The adopted default's headline numbers are: coverage 0.880859, QD
411.738214, 451 niches, 0 refusals, 0 illegal elites** (DR 0042's seed
and budget). These are what to quote for *"the loop under the adopted
default"*.

**2. DR 0042's 0.8984 is NOT retracted.** It is what the loop achieves
under the incumbent arm and stays true of that configuration. Both
numbers are correct; they answer different questions, and a dated note
now sits beside DR 0042 saying which is which.

**3. Neither committed artifact is overwritten.**
`evaluation_loop_scale_stage0.json` and `coverage_qd_gates_stage0.json`
remain the measurements they were — DR 0053 rule 2.

**4. DR 0032's GA-advantage clause is refuted again, and slightly
deeper**, with `coverage_advantage_over_ga` falling a further 0.029664.
**This is explicitly not attributed to the adoption**: the gate was
already failing under the incumbent, and the comparison is written so a
pre-existing failure cannot be reported as a regression. DR 0032's
re-openers stay untriggered.

**5. Quoting rule.** Any statement of the form *"the loop achieves X"*
must now say **which arm** it means. DR 0046's comparability rule
already forbids reading numbers across geometries; this adds the same
discipline across admission arms.

## What this record does NOT do

1. **It does not migrate the other six callers.** Four of them measure
   the defect and must never migrate (DR 0053 rule 2).
2. **It does not re-run the GA control.** `run_ga_baseline` takes no
   `slip_admission` and is structurally unaffected, so the control was
   read — sound, but it means the GA side carries the incumbent run's
   own seed noise unchanged.
3. **It does not widen the evidence beyond one SLIP profile**
   (`slip_lcd_seed`), DR 0047's inherited limit.
4. **It does not touch the geometry.** Every number here is an
   incumbent-geometry number (DR 0046).

## Sources

- `research/experiment_reports/2026-07-28-adopted-default-restatement.md` (this record's study)
- `research/decision_records/0053-admission-policy-belongs-at-the-call-site.md` (rules 2 and 3), `0052-slip-admission-default-insertion.md`, `0042-generation-layer-loop-revisit.md` (restated, not retracted), `0032-map-elites-ga-gate-disposition.md`, `0047-slip-admission-arms.md`, `0046-two-geometry-split.md`
- `labs/map_elites_archive/adopted_default_restatement.py` (+ `test_adopted_default_restatement.py`, 17 pins) · `data/archives/adopted_default_restatement_stage0.json`
- `data/archives/coverage_qd_gates_stage0.json`, `evaluation_loop_scale_stage0.json`, `slip_admission_default_stage0.json` (read, never overwritten)
- `audits/TODO.md` (cycle 25 O3)
