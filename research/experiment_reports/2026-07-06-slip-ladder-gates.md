# Experiment Report: SLIP Ladder Gates (T3.6) — the ladder closes

Date: 2026-07-06

## Objective

The og gates for the completed schema ladder: 20-archetype
expressiveness, invalid-profile fuzz (false pass <= 1%), profile zoo
15 -> 100.

## Design

- Twenty archetypes spanning the og axes (palettes, mass classes,
  materials grammar, animation vocabularies, risk temperaments,
  parenting modes, learning configurations, taxonomy). Two are
  DELIBERATELY aspirational (pack_socialite needs sociability;
  glitch_showman needs the render effects block) so the gate measures
  its real question: are any gaps UNPLANNED?
- Fuzz pack: 161 deterministic corruptions (version/shape/type/range/
  enum/version-gate/contradiction/section-type across both bases and
  all palettes), validated through the authority AND the duplicate.
- Zoo: 5 deterministic variants per representable archetype + palette-
  rotated fillers = exactly 100, in `data/slips/zoo/` (its own corpus;
  the frozen `valid/` fixtures stay count-pinned).

## Verification

RED -> GREEN `Ran 6 tests OK` (both interpreters); artifact + zoo:

```txt
expressiveness: 18/20 representable; unplanned_gap_count 0
fuzz: 161 cases, false_pass_rate 0.0 (og bar 0.01), 0 disagreements
zoo: 100 profiles, 100 valid, 100 unique
decision: ladder_gates_met
```

## Findings

1. **The ladder passes its own og gates.** Every capability gap the
   archetype set exposed was already queued by DR 0011 (sociability;
   render effects) — the schema grew exactly where it planned to.
2. Zero false passes across 161 systematic corruptions, with the
   authority and duplicate validator in perfect outcome agreement — the
   four-surface discipline holds under adversarial input.
3. The zoo gives every future compatibility/bake-off/fuzz study a
   hundred-profile corpus (og `slip_zoo_100` delivered — T11 item).

## Sources

- `labs/slip_validator/slip_zoo_gates.py`, `labs/slip_validator/test_slip_zoo_gates.py`
- `data/slips/slip_zoo_gates_stage0.json`, `data/slips/zoo/`
- `research/decision_records/0011-run-one-run-two-reconciliation.md`, `0012-slip-schema-extension-ladder.md`
