# Connected import inboxes

## Name

Paused Keeper covenant and pack inbox selection (W1, DR0076).

## Purpose

Connect named file carriers to existing validation and durable next-era preparation.

## Mathematical basis

No new scientific calculation. SHA256 binds import to the bytes previewed; lexical
filename order defines selection. Engine validators retain all authority.

## Inputs

Direct JSON files in the selected save home's covenants/ and packs/ directories;
existing companion/campaign state and the shipped seed corpus.

## Outputs

Read-only previews, explicit import verdicts, accepted staged files and existing
campaign persistence. Browsing never loads models or evolves a creature.

## Strengths

Both inboxes share controls and a paused state. Full names/reasons wrap and page.
Changed previews refuse; equal existing pack JSON is recognized without rewriting;
different existing bytes are preserved. Successful imports cannot repeat on held Enter.

## Weaknesses

This is an inbox selector, not an arbitrary filesystem chooser. Pack staging is
per item, not a transaction across all files. Maximum input scale is unmeasured.

## Failure modes

Malformed/undecodable/stale data, authority/corpus refusal, write failure and
conflicts are explicit. Accepted pack items survive another item's failure;
retry reports already-staged items. Current companion policy stays unchanged.

## Integration risk

The existing synchronous covenant application may load campaign models. Existing
campaign ledger and state remain separate writes; state failure is visible and
retryable. No engine promotion, historical recalculation or default-policy change.

## License status

Apache-2.0, repository-authored implementation.

## Prototype result

See the measured report and import_inboxes_release artifacts. Runtime evidence
is separate from native keyboard or human-usability evidence.

## Decision

Adopt subject to the preregistered local gate; no hosted-distribution decision.

## Go-No-Go gate

The complete W1 acceptance contract, source/native observations, preservation
and full sweep. Failed controls cannot be weakened to claim completion.

## Sources

- docs/development/cycle-33-import-inboxes.md
- research/decision_records/0076-connected-import-inboxes.md
- research/experiment_reports/2026-10-05-import-inboxes.md
- game/src/mecha_game/{inbox,covenant_io,packs,app}.py
- game/tests/test_import_inboxes.py
- labs/game_loop/verify_import_inboxes.py
