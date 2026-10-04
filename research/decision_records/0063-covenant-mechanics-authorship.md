# Decision Record 0063: Covenant-authored cleanliness

Date: 2026-10-04. Cycle 27 Q2. Status: ACCEPTED for opt-in authorship.

## Context

DR 0059 adopted the mechanic behind a constructor keyword and explicitly
deferred covenant authorship. The Q2 contract was committed at `2cb9bd1`
before implementation. The existing game session also collapsed an explicit
empty override into inheritance, and its clean action/readout had no keyboard
or footer binding in the playable window. The client correction was added to
the preregistration before its two failing event/readout tests.

## Decision

1. SLIP `0.2.0` may carry `"mechanics": {"cleanliness": true}`. Absence,
   an empty object, and false keep the mechanic off. Unknown keys, null and
   non-boolean values fail validation. Frozen `0.1.0` rejects the block.
2. The validated profile supplies the default. An explicit engine/session
   `mechanics` sequence takes precedence, including an empty tuple/list to
   disable. Overrides do not excuse invalid profiles. This preserves the
   caller's existing authority while making the covenant a usable author.
3. Save/load and succession preserve inheritance and explicit disable.
   Inherited opt-in is carried by the saved profile. An explicit empty override
   of an enabled profile is saved as `[]`; ordinary incumbent saves keep their
   existing shape. No save-version migration is needed.
4. Opted-in players see the engine's cleanliness value and use **G** to clean
   on the next lifecycle tick. Existing off-mode controls/footer remain intact.
5. All thirteen preregistered contract checks must pass to `adopt_authorship`;
   any false or missing check yields `withhold`. This is a contract gate, not
   a new welfare threshold. DR 0059's metrics and decision must reproduce.

## Evidence and limits

The shared matrix contains 32 adversarial cases and 192 verdicts: authored
schema, committed generated schema, Pydantic, package, grid lab, standalone
lab. The generated schema is separately pinned to current generation.
Four preimplementation profiles reproduce initial states, twelve seeded
episodes, game snapshots and save payloads under the recorded canonical JSON
encoding. The baseline includes the actual default game covenant/grid.
DR 0059 reproduces, including the committed keeper floor `0.0685`.
Both inheritance and explicit disable survive resumed play and succession.

This adds one valid and one malformed fixture (4/14 becomes 5/15). Prior
fixture bytes and historical observations are preserved; only the generated
schema is regenerated. Pydantic roundtrip assertions now execute for every
fixture, correcting an existing indentation weakness.

The default covenant remains unchanged. Q3 owns the priced default-covenant
ADOPT/REFUSE study. Autonomous grooming, reward/need-balance/death definitions,
and Q-table default promotion are unchanged. Headless client evidence is not
a human usability study. Native remote CI remains unverified while publication
is blocked; local acceptance makes no cloud claim.

## Sources

- `docs/development/q2-mechanics-rung.md`, `sunsetted/TODO.md`
- `research/decision_records/0012-slip-schema-extension-ladder.md`, `0059-cleanliness-mechanic-opt-in.md`
- `research/experiment_reports/2026-10-04-slip-mechanics-authorship.md`
- `research/algorithm_cards/slip_mechanics_authorship.md`
- `labs/lifecycle_sim/slip_mechanics_gate.py`, `labs/slip_validator/mechanics_contract.py`
- `data/lifecycle/slip_mechanics_authorship_stage0.json`, `slip_mechanics_incumbent_baseline.json`
- `data/slips/mechanics_cases_stage0.json`
