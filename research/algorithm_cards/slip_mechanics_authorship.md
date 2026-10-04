# Covenant mechanics authorship

## Name

SLIP v0.2 mechanics inheritance with explicit caller precedence (DR 0063).

## Purpose

Let a validated covenant enable the adopted cleanliness mechanic throughout
the engine and playable client, preserving incumbent behavior and overrides.

## Mathematical basis

For valid profile P and optional keyword K, the effective set is K when K is
not None; otherwise it is {cleanliness} exactly when P.mechanics.cleanliness
is true, and the empty set otherwise. Boolean validation is strict, so 1 and
0 cannot masquerade as true and false. Acceptance is the conjunction of all
thirteen required contract checks; a missing check is a failed check.
DR 0059 supplies the mechanic's unchanged dynamics and measurement thresholds.

## Inputs

Validated grid/profile, optional explicit sequence, seeded action/policy
streams; frozen incumbent hashes and the committed DR 0059 instrument.

## Outputs

Effective lifecycle state; persisted caller intent; conditional clean action
and value; a 32-case/192-verdict matrix and adopt_authorship/withhold decision.

## Strengths

Strict agreement across five authorities and the generated schema. Empty
override remains distinguishable from inheritance. Off behavior is compared
with preimplementation outputs, not newly generated expectations. A changed
committed instrument, a failed check or an omitted check withholds adoption.

## Weaknesses

Finite JSON cases and four incumbent profiles do not exhaust every possible
profile. Canonical JSON identity does not assert cross-platform newline-byte
identity. The headless event loop proves routing, not human legibility.

## Failure modes

Boolean coercion, null/default conflation, version leakage, stale generated
schema, dropped empty overrides, action validation before mechanic resolution,
and a session-only control that never reaches the player.

## Integration risk

Profile validation now precedes action/policy validation in run_episode so
clean permission uses the resolved state; simultaneous invalid inputs can
report profile/grid errors first. An old client cannot consume a newly authored
mechanics profile. Defaults and historical fixture bodies remain unchanged.

## License status

Repository-authored code under the existing package/repository policies.
No new runtime dependency; Pydantic/jsonschema remain declared lab dependencies.

## Prototype result

All required checks pass, including unchanged DR 0059 metrics and four
incumbent state/episode/game/save observations. Fixture census is 5 valid,
15 malformed. Inheritance and explicit disable persist through succession.

## Decision

Adopt opt-in authorship. Default adoption remains Q3's separate decision.

## Go-No-Go gate

All required checks must be true; full local sweep and preservation audit
must pass before local completion. Native Windows/Ubuntu CI on the published
SHA is a separate unmet publication gate.

## Sources

- `research/decision_records/0063-covenant-mechanics-authorship.md`
- `research/experiment_reports/2026-10-04-slip-mechanics-authorship.md`
- `labs/lifecycle_sim/slip_mechanics_gate.py`, `labs/lifecycle_sim/test_slip_mechanics_gate.py`
- `data/lifecycle/slip_mechanics_authorship_stage0.json`
- `data/lifecycle/slip_mechanics_incumbent_baseline.json`
- `docs/development/q2-mechanics-rung.md`
