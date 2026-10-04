# Local development cycle

## Name
REVIEW -> REPAIR -> ENHANCE -> POLISH with resumable verification.

## Purpose
Carry an existing Mechagotchi queue item through one cohesive local slice while
retaining actual evidence and explicitly distinguishing remote acceptance.

## Mathematical basis
A verification result is current only if its source SHA-256 fingerprint equals
the current inventory and no subsequent failed check revokes it. Local
completion is `phase == polish AND current_full_pass AND no_running_check`.
Full pass requires the entire suite set, successful nonempty test discovery,
dependency availability, valid artifacts, unchanged source bytes and a clean
whitespace check. Remote acceptance is not derivable from this predicate.

## Inputs
Repository Git inventory; preregistered slice/spec; exact suite names; a
provisioned interpreter; agent findings and checkpoint notes.

## Outputs
Atomic local state, immutable per-run logs/summary/results, phase transitions,
completed-cycle history, and a concrete next-action checkpoint.

## Strengths
Preserves side-effect evidence, rejects stale/incomplete success, anchors work
to the actual folder, and reuses the established test instrument.

## Weaknesses
One active operator; manual scientific judgment remains necessary. Markdown
reports need review even when they do not invalidate executable verification.

## Failure modes
Wrong repository, malformed/missing specification, failed or empty discovery,
missing dependencies, source mutation, stale evidence, interrupted subprocess,
and prematurely replacing unfinished state are explicit failures.

## Integration risk
Adds one supporting CLI command and one additive local sweep selector; engine
and game behavior remain unchanged. State is ignored and carries no credentials.

## License status
Repository Apache-2.0 policy; no new dependencies or external assets.

## Prototype result
Real subprocess and temporary-Git regression pins cover failure retention,
resumption, source mutation, stale success, complete-suite enforcement, timeout
cleanup, CLI argument validation and the unmet remote gate. Actual measured
results are in the linked experiment report and metric artifact.

## Decision
Adopt as the local operating instrument (DR 0062).

## Go-No-Go gate
All regression controls plus the full sweep must pass. No native remote pass
may be inferred. Q2 remains an explicitly preregistered next slice.

## Sources
- `research/decision_records/0062-local-development-cycle.md`
- `research/experiment_reports/2026-10-04-local-development-cycle.md`
- `data/development/local_development_cycle_stage0.json`
- `tools/mechas_cli/tests/test_development.py`
- `docs/development/local-cycle.md`
