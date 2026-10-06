# Cycle 38 X7: care-v2 integration contract

Preregistered 2026-10-06 before integration RED in the requested phase-l-gate
checkout at owner HEAD d4b4337d0dacbdfa816d990297c03a5da2d0cdca. This appendix
implements the explicit opt-in seam from cycle-38-terminal-survival-care.md.
No default promotion or scientific qualification is implied by integration.

## Acceptance

- Preserve the v1 receipt schema, ranking, defaults and existing saved bytes;
  absent and off care remain exact incumbent behavior.
- Accept observed_care_selection_v2 as an explicit session/runtime/campaign
  policy. Carry actual parent context, founder occurrence and immutable origin
  through succession, era execution, storage, restart and reproduction.
- Validate v2 receipts without replay: exact version fields, declared ranking,
  source identity, candidate-to-episode summary, complete contiguous trajectory,
  requested-horizon/elapsed ticks, result/history/final-state agreement, terminal
  alive and death cause, zero dead tail welfare, source keeper actions and terminal
  rank. Reject tampering even when hashes or summary fields are rewritten.
- Newborn state and learned state remain cold; biological inheritance, attachment,
  and trained-Q-table inheritance are outside this designed selection mechanism.
- Exercise an actual dead parent for succession; duplicate grid IDs must not merge
  distinct life occurrences. No fixtures pretending an archive is extinct.
- Store immutable inputs with explicit policy and prove read-only reproduction;
  malformed source provenance remains rejected. Lab/package passive validation
  stays equivalent. Historical receipts remain valid without migration.

## Owned paths and execution

This lane owns care_history.py, runtime/evolve.py, campaign.py policy validation
only, storage/store.py and labs/game_loop/campaign_store.py policy dispatch only,
new care-v2 integration/storage tests and .development/x7-v2/integration evidence.
Algorithm receipts are owned by the care-v2 lane. Source is frozen by the shared
integration owner before scientific trials. Focused checks use .venv Python -B
and isolated temporary saves; final aggregate/release/preservation belongs to the
integration owner. No commits, sync, push, live-save edits or source mirrors.

## Planned RED/GREEN commands

.venv/Scripts/python.exe -B -m unittest discover -s game/tests -p test_care_v2_integration.py
.venv/Scripts/python.exe -B -m unittest discover -s labs/game_loop -p test_care_v2_storage.py
.venv/Scripts/python.exe -B -m unittest discover -s game/tests -p test_care_history.py
.venv/Scripts/python.exe -B -m unittest discover -s game/tests -p test_care_execution.py

Actual outputs will be preserved under .development/x7-v2/integration; failures
remain evidence. This contract is not a replacement for the independent 30-pair
holdout, controls and unchanged effect criterion in the terminal-survival contract.

## Sources

- docs/development/cycle-38-terminal-survival-care.md
- research/experiment_reports/2026-10-06-lived-care-and-thought.md
- game/src/mecha_game/care_history.py
- packages/mecha_engine/src/mecha_engine/runtime/evolve.py
- packages/mecha_engine/src/mecha_engine/storage/store.py
- labs/game_loop/campaign_store.py
