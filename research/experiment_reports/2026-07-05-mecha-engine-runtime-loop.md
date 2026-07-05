# Experiment Report: Mecha Engine Runtime Integration Loop

Date: 2026-07-05

## Objective

Run the promoted engine as one organism for the first time: compose all
six `mecha_engine` modules through the spec's cross-module MVP flow,
extended with the repair module's damage-event contract — validate →
generate → episode → damage event → wound-site repair → post-repair
episode → archive scoring/insertion → provenance over the real ledger —
as a deterministic research lab producing the evidence a future `runtime`
surface would need. Recommended next engine step of report v0.10; no
package target is created (decision-record-gated).

## Verification

RED (test file for a module that does not exist):

```powershell
python -B -m unittest discover -s labs/runtime_integration -p "test_*.py"
```

```txt
Ran 1 test in 0.000s
FAILED (errors=1)
```

GREEN (after implementation and the two integration fixes below):

```txt
Ran 4 tests in 9.180s
OK
```

Lab command (12 creatures, 72-tick episodes, dropout 0.2, ~40 s):

```powershell
python -B .\labs\runtime_integration\mecha_engine_runtime_loop.py
```

```txt
"candidate_valid_rate": 1.0, "repaired_valid_rate": 1.0,
"slip_alignment_retention_rate": 0.916667,
"mean_position_restoration": 1.0, "mean_token_restoration": 0.972944,
"mean_survival_ratio_pre": 1.0, "mean_survival_ratio_post": 1.0,
"archived_run_count": 11, "archive": {"filled_niches": 9, "qd_score": 8.353004}
"decision": "runtime_loop_gaps_measured"
```

## Findings

1. **The engine composes.** 11 of 12 creatures complete the entire loop:
   every generated candidate validates (12/12), survives its episode,
   takes a reported damage event (mean 2.42 cells destroyed), is repaired
   to its exact live-cell silhouette with no template (position
   restoration 1.0; token restoration 0.9729; zero guard substitutions
   needed), survives its post-repair episode at full ratio, scores into
   the MAP-Elites archive (9 niches, QD 8.35), and the provenance gate
   passes over the real ledger. The loop is deterministic end to end
   (pinned by test).
2. **Integration finding 1 — the SLIP-alignment seam (the measured
   gap).** The repair module guarantees *genome-validator* validity, but
   the lifecycle module *rejects* grids that lost SLIP alignment. Damage
   can destroy a profile-required organ's only cell (here: the expression
   cell of `gen_badac15b4e8a9760`), and the learned refill predicted a
   different organ — valid grid, unaligned profile, un-simulatable
   creature. The loop measures this as `slip_alignment_retention_rate`
   (0.9167) and honestly skips the post-episode/archive stages for the
   unaligned run. Root cause and direction: the validity guard consults
   only the target-free validator; the SLIP profile is an engine-native
   constraint (not a template), so extending the repair surface to accept
   the active profile in its guard is contract-compatible — a future
   batch, since it touches the promoted module and its interface spec.
3. **Integration finding 2 — profile-scoped parent selection.** The
   generation contract rejects parents that cannot satisfy the SLIP
   profile (disallowed palette). A runtime therefore selects parents from
   the profile-aligned subset of the corpus; the lab records
   `parent_pool_size` (18 of 50 seeds for the LCD profile).
4. Honesty surfaces hold under composition: readability enters the
   archive as the uncalibrated proxy with `manual_rating_status:
   "not_collected"` visible on every score (calibration deferred by owner
   decision), and the archive's calibration status remains blocked.

## Decision

Status: `runtime_loop_gaps_measured` — deliberately not "composed": the
loop's green bar requires 1.0 alignment retention, and 0.9167 is the
honest number. The gap is a single, well-understood seam with a
contract-compatible fix direction. Next research steps, in order:
(a) SLIP-aware repair guard (promoted-module change: spec + DR-level
review + parity implications documented); (b) extend the loop to
multi-generation evolution (offspring of archive elites) and repeated
damage/repair cycles. A `runtime` package target proposal comes only
after (a) turns the retention rate green.

## Sources

- `labs/runtime_integration/mecha_engine_runtime_loop.py`
- `labs/runtime_integration/test_mecha_engine_runtime_loop.py`
- `data/runtime_integration/mecha_engine_runtime_loop_stage0.json`
- `research/algorithm_cards/mecha_engine_runtime_loop.md`
- `research/package_specs/mecha_engine_module_interfaces.md`
- `research/package_specs/mecha_engine_repair_interface_spec.md`
- `data/asset_provenance/ledger.json`
- `research/reports/mechagotchi_research_report_v0_10.md`

## Addendum (same day): the seam is closed

The SLIP-aware repair guard batch
(`research/experiment_reports/2026-07-05-slip-aware-repair-guard.md`)
shipped, and the runtime now hands the active profile to
`repair_wound_sites`. Full-size rerun: alignment retention 0.9167 →
**1.0**, all 12 runs archived (10 niches, QD 9.29), exactly one guard
substitution — on precisely the creature that previously became
unsimulatable. Decision: `runtime_loop_gaps_measured` →
**`runtime_loop_composed`**. Honest nuance retained in the artifact:
token restoration dipped 0.9729 → 0.9654 because the guard restores the
profile constraint, not the individual's exact token placement. The
go/no-go gate for a `runtime` package target proposal is now satisfied on
the evidence side; creating the target remains owner-gated (decision
record required).
