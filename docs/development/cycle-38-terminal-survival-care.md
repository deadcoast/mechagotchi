# Cycle 38 X7 v2: terminal-survival care selection

Preregistered 2026-10-06 before v2 RED or scientific execution in the requested
phase-l-gate checkout, owner HEAD d4b4337d0dacbdfa816d990297c03a5da2d0cdca.
Preserve v1 code semantics, receipts, criteria and complete REFUSE artifacts;
commits, sync and push remain the owner's. This is a designed computational
selection mechanism, not evidence of biological inheritance or personality.

## Versioned correction

Add explicit observed_care_selection_v2. Keep observed_care_selection_v1 and off
byte-identical. Same legacy pool of eight pristine generated candidates at
base+[0..7], same cold incumbent care replay, same requested-horizon welfare
(including zero dead tail), same actually observed action windows, same two
named evaluators. V2 ranks lexicographically by alive at the end of the requested
horizon, welfare, elapsed survival ticks, then earliest original index. A death
on the last tick is dead even when its elapsed survival ticks equal the horizon.
No dead candidate may beat a live candidate. All-dead pools still use the
registered welfare/ticks/index order. Newborn cells and learning stay cold;
evaluation damage, learned state and source-life physiology never transfer.

V2 receipts record the explicit order, complete candidate tick trajectories,
terminal states, source Keeper/life/grid digest and context digest. IDs, summary
counters and source labels bind provenance but never influence selection. The
species covenant remains distinct from any individual variation; the archive
morphology probe is a standardized stress test, not a personality trait.

## Regression and fresh qualification

Regression: retain the exact original pair22 founder2/seed20260702 contexts from
.development/x7/care/manifest.json. Reproduce the original v1 receipt exactly
against data/game_client/observed_care_selection_stage0.json. V2 must select a
live neglected candidate from that pool, without treating this known example as
new holdout evidence. Preserve full trajectories for both paired v2 histories.

Fresh cohort: founders10 through19 (zero-based) of the frozen 50-founder product
manifest .development/x7/learning/manifest.json; seeds20261007,20261017,20261027.
The seed ranges are disjoint from the prior study and each other. Evaluate all
30 paired founder/seed cases under pristine and archive_morphology_probe_v1.
Use the same actual 12-tick observed feeding-every-third versus neglect histories
with the common actual observed prefix if either ends early; no fabricated,
padded, repeated, or extrapolated events. Freeze both complete source histories,
used prefixes, immutable ordered founder identity and admitted genomes first.

Per evaluator ADOPT requires the complete 30-pair holdout cohort, at least one
structural selected-descendant difference across paired care histories, and all
prior controls: welfare and elapsed survival never worse than index0, pristine
child, repeated determinism and exact lab/package parity, identical candidate
bytes across care histories, metadata-only negative control, missing/empty/off
exact incumbent behavior, input immutability and source stability. Add explicit
terminal-alive nonregression versus index0, selection of a live candidate whenever
any live option exists, and exact trajectory-to-terminal consistency. Do not
relax welfare nonregression to accommodate a survival/welfare tradeoff. Keep
founder occurrence, immutable input provenance, persistence/reproduction and
native product checks separate integration gates. The correction alone is not
meaningful care qualification. Zero structural effect or any unmet criterion
REFUSES adoption; default remains off without every applicable gate.

## Bounds, durable receipts and stopping

Foreground only: setup<=30s, each regression/holdout pair<=30s, cumulative study
<=300s including setup and resumed work. Each attempt writes a started receipt
before its subprocess, a completed hashed receipt after success and cumulative
consumption checkpoints. Source hashes cover the actual transitive mechanism and
instrument sources; source edits are paused during execution. Failed/incomplete
trials and source drift are preserved and never retried automatically. Hard
instrument/invariant failures stop execution. If an evaluator irreversibly fails
a qualification invariant, that evaluator is refused immediately; the other
predeclared evaluator may finish within the original bound. No seed hunting or
second candidate configuration. Explicit resume is permitted only at a completed
pair boundary with unchanged inputs/sources, no started unfinished trial, and
remaining cumulative budget; interruption during a trial refuses automatic
resume. Every verdict remains separate from implementation test success.

## Sources

- docs/development/cycle-38-lived-care-and-thought.md
- research/experiment_reports/2026-10-06-lived-care-and-thought.md
- data/game_client/observed_care_selection_stage0.json
- .development/x7/care/manifest.json
- .development/x7/learning/manifest.json
- labs/runtime_integration/observed_care_selection.py
- labs/runtime_integration/observed_care_v2_gate.py
- packages/mecha_engine/src/mecha_engine/runtime/_observed_care.py

## Instrument clarification before scientific execution

The retained pair22 live-selection regression applies specifically to
archive_morphology_probe_v1; pristine remains the separate null control. RED's
actual regression assertion was already scoped to that probe. Measure two package
calls as repeatability, separately from the laboratory mirror comparison. Measure
empty, absent and disabled parity independently. Require exact selected newborn
bytes from the generated pool, no postdeath trajectory ticks, complete trajectory
balance recomputation, and distinct receipt source identity. Bind the frozen
contract, all input/model/covenant/admission payloads and transitive game
health/happiness sources. Qualification nonregressions are evaluator-local;
source/input/parity/receipt/instrument failures stop the entire bounded study.
The study freezes the care contract; outcomes go into a separate report.
