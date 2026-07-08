# Experiment Report: `mecha_engine.slip` Promoted (F2) — The Tenth Module, Four Mirrors Collapsed

Date: 2026-07-07

## WHY

DR 0027 authorized the target with fixed gates: four private `_slip.py`
mirrors (~80 KB quadruplicated inside the package, held in sync only by
parity pins) plus the workshop server whose docstring had promised for
cycles to "switch to a promoted `mecha_engine.slip` surface when one
exists." F2 is the port, gates in order.

## Gate 1 — mirror reconciliation: ZERO divergences

Before touching anything, the five-way sweep (lab authority +
generation/lifecycle/repair/runtime mirrors) over 118 profiles × 5
cases (as-is + 4 systematic corruptions) and 104 valid profiles × 20
seeds: **zero validate divergences, zero alignment divergences** — the
hash differences were docstrings, the behavior was one. Recorded in
`data/slips/slip_authority_reconciliation_stage0.json`
(`labs/slip_validator/slip_authority_reconciliation.py` keeps the
surviving lab-vs-package pair sweep alive: 590 validate + 2,080
alignment cases, still zero).

## WHAT

- **The module** — `mecha_engine.slip` (`authority.py` + `__init__.py`,
  exporting `validate_slip`, `is_grid_aligned`, `SlipResult`): the
  fullest mirror's body verbatim, now the single in-package authority.
- **The collapse** — the five import sites (`generation.generate`,
  `lifecycle.simulate`, `repair.wound`, `runtime.evolve`,
  `runtime.live`) switched to the public import; the four `_slip.py`
  files DELETED. Every module suite passed unmodified through the new
  import — the regression harness DR 0027 demanded.
- **The pins** — `labs/grid_genome/test_package_slip_parity.py`
  rewritten from the four-way mirror pin into the permanent pair pin
  (exact verdict-and-error-string equality over the whole corpus +
  corruptions + seed alignment); `tests/test_slip_contract.py` +
  driver (valid fixtures all pass, failure cases all rejected, the
  ladder rungs version-gated and bounded, alignment errors named,
  determinism, purity, boundary scan).
- **The promise fulfilled** — the workshop server now imports
  `mecha_engine.slip`; its docstring's standing note is updated to say
  so. The lab authority remains the Stage 0 research source, pinned.
- **The bookkeeping** — `slip` joined `LATER_PROMOTED_MODULES`
  (deferred set now `render` alone, dispositioned by DR 0026); the
  promotion gate gained the `slip_authority` candidate and its pinned
  count advanced to NINE promotion-ready.

## Verification

```powershell
PS> python -B labs/slip_validator/slip_authority_reconciliation.py
{ "decision": "slip_authorities_identical",
  "validate_cases": 590, "validate_divergences": 0,
  "alignment_cases": 2080, "alignment_divergences": 0 }

PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 290 tests ... OK   # incl. the 8-test slip contract suite

PS> python -B -m unittest discover -s labs/grid_genome -p "test_package_slip_parity.py"
Ran 3 tests ... OK     # the permanent pair pin
```

## Decision

Adopt — F2 developed to its description: `mecha_engine` has its tenth
module, ~60 KB of quadruplication is gone, the workshop's promise is
fulfilled, and every og module target is now realized (nine → ten
promoted; `render` dispositioned with a named re-opener).

## Sources

- `research/decision_records/0027-slip-module-disposition.md` (the gates)
- `research/algorithm_cards/slip_schema_validator.md` (the validator's card)
- `packages/mecha_engine/src/mecha_engine/slip/`
- `packages/mecha_engine/tests/test_slip_contract.py` (+ driver)
- `labs/grid_genome/test_package_slip_parity.py` (the permanent pair pin)
- `labs/slip_validator/slip_authority_reconciliation.py`
- `data/slips/slip_authority_reconciliation_stage0.json`
- `workshop/server/workshop_server.py` (the fulfilled switch)
- `labs/package_promotion/package_promotion_gate.py` (the `slip_authority` candidate)
