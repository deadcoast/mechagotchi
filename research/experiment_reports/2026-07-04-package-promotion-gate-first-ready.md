# Package Promotion Gate: First Promotion-Ready Candidates

Date: 2026-07-04

Status: `package_promotion_gate_promotion_candidates_available`

## Purpose

Rerun `labs/package_promotion/package_promotion_gate.py` over the complete
five-module promotion evidence (genome, generation, lifecycle, archive,
provenance — commits `db19236`..`a2ac151`), completing the traceability
matrix's final step ("rerun promotion gate"). Also fix the registry's
flat target paths (`packages/mecha_engine/<module>`), which predated the
src layout and were flagged for revisit at the first contract landing.

## Result

Registry targets now point at `packages/mecha_engine/src/mecha_engine/*`.
Gate outcome — the first promotion-ready candidates in the repo's history:

| Candidate | Status | Blockers |
|---|---|---|
| lifecycle_simulator | **promotion_ready** | — |
| map_elites_archive | **promotion_ready** | — |
| provenance_ci | **promotion_ready** | — |
| switchboard_feedback | ready_for_package_design | target (learning deferred) |
| readability_gate | blocked | target + `human_ratings_absent` (63 rows) |
| ca_nca_repair | hold_research_only | target + stability bar (0.86 vs 0.9) |

Decision: `promotion_candidates_available` /
`review_before_copying_lab_code` — apt, since the "copying" already
happened under contract tests and byte-identical parity pins.

The runtime boundary gate, regenerated, derives
`package_runtime_integration_ready: true` from the promotion evidence (the
Batch 17 hardening required exactly this evidence before flipping), while
`profile_weighted_evolution_ready` stays false on the single remaining
human-gated reason: `manual_readability_calibration_absent`. Three test
pins asserting the pre-promotion "empty scaffold" state were updated to
the evidence-derived current state.

## Decision

The five initial modules are promoted and gate-recognized. Remaining path
to further promotion: the 63 manual readability rows (evaluation module +
final descriptor threshold locks + any profile-weighted evolution claim),
the learned-repair stability bar, and a future decision on the deferred
learning module target.

## Verification

```powershell
python -B labs/package_promotion/package_promotion_gate.py
python -B labs/architecture/mecha_engine_runtime_boundary_gate.py
python -B -m unittest discover -s labs/package_promotion -p "test_*.py"
python -B -m unittest discover -s labs/architecture -p "test_*.py"
```

## Sources

- `research/package_specs/mecha_engine_contract_traceability_matrix.md`
- `labs/package_promotion/package_promotion_gate.py`
- `labs/architecture/mecha_engine_runtime_boundary_gate.py`
- `data/package_promotion/mecha_engine_package_promotion_gate_stage0.json`
- `data/architecture/mecha_engine_runtime_boundary_gate_stage0.json`
- `research/experiment_reports/2026-07-04-mecha-engine-genome-promotion.md`
- `research/experiment_reports/2026-07-04-mecha-engine-generation-promotion.md`
- `research/experiment_reports/2026-07-04-mecha-engine-lifecycle-promotion.md`
- `research/experiment_reports/2026-07-04-mecha-engine-archive-promotion.md`
- `research/experiment_reports/2026-07-04-mecha-engine-provenance-promotion.md`
