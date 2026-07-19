# Experiment Report: The Behavior Editor — Deliberation Depth Gains Its Authoring Face (Cycle 18 · WORKSHOP · H4)

Date: 2026-07-19

## WHY

The gap table's Workshop row names the behavior editor; the TODO's H4
scope is "SLIP behavior/survival weights, mutation caps, and
deliberation depth authored visually, validated live by the engine's
authority (verbatim refusals in the page) — the covenant's authoring
face." The survey found the honest gap precisely: the slip creator has
authored behavior/survival weights and mutation caps with live
authority verdicts since its first slice — but **deliberation**
(`max_ticks` 2..8, `confidence_threshold` 0..1; DR 0017's
CTM-inspired confidence-gated thinking, the field the game's Covenant
step spends bloodline tiers into) had **no authoring control
anywhere**. H4 is that face.

## WHAT

**The slip creator gains the deliberation panel**: a max-ticks slider
whose position 1 is the off-sentinel (below the authority's real floor
of 2 — the risk-tolerance pattern), a confidence-gate slider defaulting
to the engine's own 0.72 (`DELIBERATION_CONFIDENCE_DEFAULT`, the
`_policy.py` default), and the honest hint naming the floor/ceiling
and the covenant linkage. Setting it writes `slip_version 0.2.0` (the
ladder rule); `buildProfile`, load-restore, and New-reset all carry
the field; every change flows through the existing live
`/api/slip/validate` loop, so the authority's refusals — e.g.
`deliberation max_ticks must be an integer in 2..8` — reach the page
verbatim, as pinned.

**No server change was needed** — `validate_slip` (the promoted
`mecha_engine.slip` authority) has judged deliberation since DR 0027,
and `_slip_validate`/`_slip_save` pass profiles through verbatim. The
new tests pin that truth end to end: a deliberating profile validates,
saves, and round-trips exactly; the floor refusal is verbatim; the
0.2.0 version gate holds.

**The covenant's authoring face, stated honestly**: a covenant IS an
authority-validated SLIP (`campaign["slip_profile"]`); the workshop
authors species contracts, and an exported covenant file
(`covenant_io`) placed in the project's slips is loadable, editable,
and re-judged here — deliberation included. The earned-budget
governance (`apply_covenant_change`, `covenant_budget`) stays the
GAME's concern: budgets are campaign state, and the workshop does not
pretend to know a campaign's unlock facts.

## Verification

```powershell
PS> python -B -m unittest test_workshop_server.DeliberationAuthoringTests   # (from workshop/tests)
Ran 4 tests ... FAILED (failures=1)   # RED: the page serves no deliberation controls
# after the panel:
Ran 4 tests ... OK
PS> node --check <extracted slip creator script>
JS SYNTAX OK                           # 435 lines
```

## HONEST REMAINDER

1. **`visual_grammar` and `species_class`** remain un-authored ladder
   fields — real, named, and small; they queue behind the documented
   H5/H6 gates rather than smuggling in here.
2. **Budget-aware covenant editing in the workshop** (showing a
   campaign's earned caps beside the sliders) would need the workshop
   to read campaign state — a cross-surface decision for a DR, not a
   drift.
3. **The panel is server-verified, not click-tested** — H5's gate, as
   with H2/H3.

## Sources

- `audits/TODO.md` (cycle 18 H4), the gap table's Workshop row
- `workshop/slip_creator/slip_creator.html` (the deliberation panel) + `workshop/tests/test_workshop_server.py` (DeliberationAuthoringTests)
- `research/slip/slip.schema.json` (the deliberation fragment), `packages/mecha_engine/src/mecha_engine/slip/authority.py` (`_validate_deliberation`)
- `packages/mecha_engine/src/mecha_engine/lifecycle/_policy.py` (the 0.72 default + tick loop), `game/src/mecha_game/covenant.py` (the spend into this field)
- `research/decision_records/0017-recalibration-engine-game-duality.md`, `research/algorithm_cards/ctm_inspired_ticks.md`
