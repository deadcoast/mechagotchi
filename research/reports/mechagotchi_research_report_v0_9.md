# Mechagotchi Research Report v0.9

Date: 2026-07-04

## Executive Summary

The package-implementation wave. The user explicitly authorized starting
package work (the go/no-go every decision record required), and the
sequence defined by DR 0004 and the contract traceability matrix executed
end to end in one wave: the empty `packages/mecha_engine` scaffold, all
five initial module promotions in the fixed order (genome → generation →
lifecycle → archive → provenance), the parallel research-blocker batch, and
the capstone promotion-gate rerun that produced the repo's first three
`promotion_ready` candidates.

Every promotion followed the same discipline: a self-contained port
(stdlib only, zero `labs` imports, no artifact writes), subprocess-driven
contract tests proving the module's gate assertions, and a lab-side parity
pin — byte-identical outcomes against the authoritative lab over the full
fixture corpora wherever the surfaces coincide, documented semantic
equivalence where they extend (generation traces, archive candidate
contract).

Test base: 481 lab tests at the scaffold step → **520 lab + 163 package
tests, all green**. `package_runtime_integration_ready` is now
evidence-derived true; `profile_weighted_evolution` remains blocked on a
single human-gated reason: the 63 manual readability rows.

This report consolidates and links the underlying experiment reports; it
does not replace them.

## Consolidated Reports (8)

1. `research/experiment_reports/2026-07-04-mecha-engine-package-scaffold.md`
   — empty src-layout scaffold per DR 0004; new executable scaffold
   verification gate (9/9); every package-absence observer updated honestly.
2. `research/experiment_reports/2026-07-04-mecha-engine-genome-promotion.md`
   — 50/50 seeds, 200/200 invalid, zero mutations, byte-identical parity.
3. `research/experiment_reports/2026-07-04-mecha-engine-generation-promotion.md`
   — 100/100 valid unique candidates (baseline 42/100), 50/50 SLIP-aligned,
   parity over 150 candidates incl. mutation-temperature jitter.
4. `research/experiment_reports/2026-07-04-mecha-engine-lifecycle-promotion.md`
   — frozen-policy factoring per spec; zero-excluded-key parity across
   3 policies × 4 horizons; pinned death-tick semantics preserved.
5. `research/experiment_reports/2026-07-04-mecha-engine-archive-promotion.md`
   — calibrated seven-axis semantics verbatim; exact parity to the pinned
   artifact (83 niches, QD 72.07); descriptor thresholds carried as
   explicitly provisional pending manual readability.
6. `research/experiment_reports/2026-07-04-mecha-engine-provenance-promotion.md`
   — byte-identical re-derivation of all committed provenance artifacts;
   error-for-error validation parity across 16 fault-injected ledgers.
7. `research/experiment_reports/2026-07-04-ca-nca-trained-neighborhood-repair.md`
   — reward-shaping blocker cleared with root-cause diagnosis
   (need_balance_delta 0.0 → +0.0396); gradient-trained repair beats
   no-repair by +0.63 overlap but stands at 0.86 vs the 0.9 assisted bar
   (blocker converted static → evidence-derived).
8. `research/experiment_reports/2026-07-04-package-promotion-gate-first-ready.md`
   — first `promotion_ready`: lifecycle_simulator, map_elites_archive,
   provenance_ci; registry targets fixed to the src layout.

## Decisions

- The five initial modules are promoted and gate-recognized; further module
  work proceeds against their contract tests, not the labs.
- Deferred module targets (`learning`, `repair`, `render`, `storage`,
  `slip`) stay absent until their own gates; learning is design-ready.
- Package dependency policy remains blocked (DR 0005 scope) — `[project]`
  still declares no dependencies; all five modules are stdlib-only.

## Blocked / Open

- Manual readability calibration: 0 of 63 reviewer rows — blocks the
  evaluation module, final descriptor threshold locks, and any
  profile-weighted evolution claim. Human input only.
- Learned repair stability bar: 0.8625 vs 0.9 (measured, derived blocker).
- The mecha_workshop build track and remaining research-plan stages beyond
  the engine package.

## Publication Status

Published internally as the v0.9 package-implementation wave report.
Sources and metrics in `research/reports/research_report_v0_9_manifest.json`.

## Sources

- `research/decision_records/0004-mecha-engine-package-scaffold.md`
- `research/decision_records/0005-declare-lab-dependency-manifest.md`
- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `research/reports/mechagotchi_research_report_v0_8.md`
- the eight consolidated experiment reports listed above
