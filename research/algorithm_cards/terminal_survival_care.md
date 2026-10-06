# Terminal-survival care selection

## Name

observed_care_selection_v2; explicit experimental/default-off correction to v1.

## Purpose

Prevent an evaluation candidate dead at the horizon from beating an available
live candidate merely because elapsed survival ticks tie. Separately measure
whether actual parental care histories select different structural descendants.

## Mathematical basis

For each of eight deterministic legacy candidates, replay the parent's exact
observed Keeper action window under a cold incumbent product evaluator. Let
A be alive after the complete requested window, B the unchanged mean need balance
with zero dead tail, T elapsed survival ticks and i the original pool index.
V2 selects lexicographic max (A, B, T, -i). V1 remains max (B, T, -i).
Death on the last tick has A=false even when T equals the requested horizon.

## Inputs

Exact parent genome, generation model, species covenant, observed care context,
base seed, explicit policy and evaluator. Pool seeds are base+[0..7]. Pristine
is the null evaluator; archive_morphology_probe_v1 evaluates existing morphology
load on copies. Keeper/life/genome identity binds evidence but cannot affect rank.

## Outputs

Unmodified pristine selected candidate and a versioned receipt containing source
identity, context digest, explicit rank order, complete eight-candidate cold
trajectories and terminal outcomes. No trained state or physiology is inherited.

## Strengths

Deterministic; disabled/absent/empty parity; exact retained v1 regression;
terminal-survival semantics distinguish alive from last-tick death; complete
stored provenance/trajectories validate through the real product loader.

## Weaknesses

Care affects welfare and survival but did not alter any fresh holdout ranking.
All 240 neglected candidate evaluations in each evaluator died from starvation,
so alive-first cannot differentiate those candidate pools. A scalar morphology
load does not establish individual personality or beneficial developmental change.

## Failure modes

Treating the known regression as qualification; lowering prior welfare/tick
nonregression bars; conflating elapsed ticks with terminal survival; source/input
drift; metadata-dependent selection; trained Q-table or damage inheritance;
resurrecting refused trials; asserting biology or attachment from designed rules.

## Integration risk

V2 receipts are larger because trajectories are retained. Existing saves remain
v1/off unless explicitly configured; v1 receipt semantics are unchanged. Context
continues to follow actual founder occurrences and immutable inputs. The native
consumer, persistence, restart and final aggregate checks are separate integration
evidence, not implied by a unit test or one known regression.

## License status

Original repository implementation under the project's Apache-2.0 terms.

## Prototype result

One source-frozen bounded study: 30 new founder/seed pairs, two evaluators,
64.428071 seconds; all control, runtime and terminal semantics gates pass.
Both evaluators produce 0/30 structural care-dependent descendant changes.
The retained pair 22 correction changes the neglected probe selection from dead
index 4 to live index 0, but is not part of those holdouts. V1 is byte-exact.

## Decision

REFUSE contextual product promotion. Keep the v2 correction explicitly available
with default off. X7 meaningful care-driven descendants remain open.

## Go-No-Go gate

Unchanged complete-cohort structural-effect, welfare/ticks nonregression and
control requirements, augmented by terminal nonregression and live-option
preference. All applicable criteria must pass; a known example is insufficient.
A future mechanism needs new preregistration and independent held-out evidence.

## Sources

- docs/development/cycle-38-terminal-survival-care.md
- research/experiment_reports/2026-10-06-terminal-survival-care.md
- research/decision_records/0087-terminal-survival-care-selection.md
- labs/runtime_integration/observed_care_selection.py
- labs/runtime_integration/observed_care_v2_gate.py
- packages/mecha_engine/src/mecha_engine/runtime/_observed_care.py
- data/game_client/care_v2_terminal_survival_stage0.json
- data/game_client/observed_care_selection_stage0.json
