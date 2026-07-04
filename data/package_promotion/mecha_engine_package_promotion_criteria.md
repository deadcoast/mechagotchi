# Mecha Engine Package Promotion Criteria

This gate defines when lab code may be considered for `packages/mecha_engine`.
It does not promote code by itself.

## Criteria

- `research_artifacts_complete` (package_design): Algorithm card, experiment report, and metric artifact exist.
- `metric_thresholds_met` (package_design): Candidate metrics satisfy component-specific thresholds.
- `package_boundary_defined` (package_design): Target package path and ownership boundary are named.
- `verification_surface_defined` (package_design): A focused verification command exists for the candidate.
- `provenance_gate_clean` (promotion): External source, license, and attribution blockers are absent.
- `package_root_exists` (promotion): `packages/mecha_engine` exists before lab code is moved.
- `no_research_blockers` (promotion): Human-rating, real-ingest, or lab-only blockers are resolved.

## Candidate Status

- `lifecycle_simulator` -> `promotion_ready` for `packages/mecha_engine/src/mecha_engine/lifecycle`
- `switchboard_feedback` -> `ready_for_package_design` for `packages/mecha_engine/src/mecha_engine/learning`
- `map_elites_archive` -> `promotion_ready` for `packages/mecha_engine/src/mecha_engine/archive`
- `provenance_ci` -> `promotion_ready` for `packages/mecha_engine/src/mecha_engine/provenance`
- `readability_gate` -> `blocked_missing_or_failed_research_evidence` for `packages/mecha_engine/src/mecha_engine/evaluation`
- `ca_nca_repair` -> `ready_for_package_design` for `packages/mecha_engine/src/mecha_engine/repair`

## Decision

Status: `promotion_candidates_available`

At least one candidate has evidence and a package boundary.
