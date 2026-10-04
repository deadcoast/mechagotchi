# Q2: covenant-authored mechanics

Preregistered 2026-10-04, before implementation. Queue: cycle 27 Q2.

## Contract

SLIP v0.2 gains an optional `mechanics` object with exactly one supported
optional field, `cleanliness`, whose value must be a JSON boolean. Absence,
`{}`, or `{"cleanliness": false}` means off. Unknown keys, null, strings and
numeric substitutes are invalid. SLIP v0.1 stays frozen and rejects the block.
The authored JSON Schema, package authority, both stdlib lab mirrors and
Pydantic model/generated schema must agree on the same case matrix.

Lifecycle authority order is explicit: `mechanics=None` inherits the validated
profile; any supplied tuple/list overrides it, including the empty sequence
which disables the mechanic. A keyword override never excuses an invalid
profile. `run_episode` must use the same resolution as `initial_state` before
deciding whether an explicit `clean` action stream is allowed.

The game constructor keeps its public signature. Covenant opt-in must survive
save/load and succession. The current `tuple(mechanics) if mechanics else None`
loses an explicit empty override; replace that distinction without changing
ordinary off-mode save shapes. Old profiles, state/episode reports and default
covenant remain byte-identical where the mechanic is absent. The default flip
belongs to Q3 and cannot be smuggled into Q2.

## Cohesive implementation and evidence scope

- Extend `research/slip/slip.schema.json`, the package SLIP authority,
  `labs/grid_genome/slip.py`, `labs/slip_validator/slip_validator.py`, and
  `pydantic_contract.py`; regenerate only the named generated schema.
- Add one valid opted-in fixture and one malformed fixture. Update fixture
  census expectations as an explicitly documented corpus change (4/14 ->
  5/15), preserving prior fixture bytes and historical corpus observations.
- Resolve profile mechanics in package lifecycle and preserve precedence
  through game save/resume/succession. Avoid extending the old lab lifecycle
  simulator merely to mirror code; a package-backed lab gate follows DR 0059.
- Add a dated report, algorithm card, decision record and metric artifact,
  ledger entry, contract updates, and measured queue completion only after
  acceptance. Pre-register any further scientific decision separately.

## Required evidence

1. One shared adversarial case matrix compares all five authorities, including
   version/null/boolean/unknown-key distinctions; tests begin RED.
2. A profile-only opt-in permits cleaning. Explicit empty override prevents it.
   Explicit enabled override wins over profile false. Inputs are not mutated.
3. Every existing valid profile reproduces incumbent state and episode outputs
   without the new key. Reproduce committed DR 0059 off-mode pins rather than
   generating a new expected result from the implementation being tested.
4. Game save/resume and succession retain effective mechanics and explicit
   disable; ordinary existing saves retain their prior shape.
5. Focused suites: grid_genome, slip_validator, lifecycle_sim, package, game,
   CLI. Then full sweep, artifact audit, and separate exact-SHA native CI.

## Sources

- `sunsetted/TODO.md` Q2-Q5
- `research/decision_records/0012-slip-schema-extension-ladder.md`
- `research/decision_records/0013-port-slip-v2-and-packet-v2.md`
- `research/decision_records/0027-slip-module-disposition.md`
- `research/decision_records/0059-cleanliness-mechanic-opt-in.md`
- `packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py`
- `packages/mecha_engine/src/mecha_engine/slip/authority.py`
- `game/src/mecha_game/session.py`, `game/tests/test_cleanliness_mechanic.py`
