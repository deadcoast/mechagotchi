# Responsive covenant preparation

## Purpose
Avoid training evolution-only models during covenant preparation and import.

## Mathematical basis
Unchanged generation/repair trainers and scientific calculations. Only the point
at which models are requested changes; eager/deferred outputs must match exactly.

## Inputs and outputs
Existing seed corpus, covenant, adopted readability artifact and campaign state.
Light inputs support preparation; complete inputs are published for an era after
both models prepare successfully. Existing model-cache keys and parameters remain.

## Strengths
Cold valid/invalid/stale imports avoid seconds of event starvation. E retains
the actual responsive loading, cancellation and joined-worker boundaries.

## Weaknesses and failure modes
Corpus/history file reads remain synchronous. Maximum scale is unmeasured.
Cold model cancellation waits for the existing load boundary. Model/cache failure
is visible through the existing era retry path; no partial inputs publish.
State/ledger persistence remains separate writes, not a new transaction promise.

## License
Apache-2.0 repository implementation.

## Result and decision
Measured normal/256-file import and both-policy interaction checks pass; eager
tiny/normal hashes and earned-larger reports/recordings remain equal. Adopted
locally after 2,666 tests / 24 suites, two documented skips, 2,297 valid JSON
artifacts and preservation review. No default-policy,
biological definition, engine promotion or hosted-distribution decision.

## Sources
- docs/development/cycle-34-responsive-preparation.md
- research/decision_records/0077-responsive-covenant-preparation.md
- research/experiment_reports/2026-10-05-responsive-preparation.md
- game/src/mecha_game/{app,campaign}.py
- labs/game_loop/verify_preparation_responsiveness.py
