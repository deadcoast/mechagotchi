# Experiment Report: `DANGER_THRESHOLDS` Promoted to the Package's Public API — Narrowly, and On Purpose (Cycle 25 · ENGINE · O1)

Date: 2026-07-28

## WHY

DR 0054 adopted **`danger_margin`** — the minimum normalised safety
margin across the engine's danger thresholds — as the **CHOSEN**
definition of the documented VISIBLE axis `health`, after **refusing
`grid_stability` under that name as a euphemism**.

It then recorded its own blocker, in its own blocked states:

> `danger_margin` reads `DANGER_THRESHOLDS`, which is a **public name in
> a public module but is NOT in the package's `__all__`** — so a
> definition built on it depends on a surface the package has not
> promised. Adopting it would mean promoting that constant to the public
> API, which is a package change with its own spec update and gate.

O1 is that package change. It is the smallest task in the cycle-25
queue, and it is the one that unblocks the health readout.

## WHAT

**The promotion follows the W1 precedent exactly** — the last time this
module's contracted surface widened (four names to six, for the living
companion), it was done by documenting the widening in the lifecycle
contract gate, adding the names to `__all__`, and letting the **exact
`__all__` equality probe** fail until the spec and the code agreed. The
same three steps here take the surface from **six names to seven**.

**RED-first, and the RED is the contract itself.** The surface probe
asserts `__all__` equality against a frozen list in
`test_lifecycle_contract.py`. Adding the name to that list *before*
exporting it is what produces the failing run — the pin is doing its job
by rejecting an undocumented widening.

**The promotion is deliberately narrow, and the narrowness is pinned.**
O1's charter said *"do not widen the promotion beyond the constant — if
the margin formula itself belongs in the engine, that is a separate
decision, and this task must say which it did."* It did **not** promote
the formula, and a package test now asserts that neither `danger_margin`
nor `health` appears on the lifecycle surface, so the distinction cannot
erode silently.

## FINDINGS

### The contract now pins the constant BY VALUE, not by presence

A promoted constant whose numbers can drift is not a contract. Three new
package pins:

| pin | what it prevents |
| --- | --- |
| `danger_thresholds` probed by value through the package boundary | the numbers changing under a consumer that computes a health bar from them |
| every **lethal** axis has a threshold | a threshold set missing one, which would let a bar read healthy on a dying companion — **the exact failure DR 0054 refused `grid_stability` for** |
| neither `danger_margin` nor `health` on the surface | the promotion quietly widening into the formula |

The contracted values:

```text
hunger 0.75 · energy 0.25 · stress 0.65 · bond 0.25 · grid_stability 0.35
```

### The "danger, not lethal" distinction is now a package-level pin

`bond` carries a threshold and is **not** a death condition — only
`hunger`, `energy`, `stress` and `grid_stability` appear in
`_life_status`. DR 0054 renamed its own adopted candidate from
`lethal_margin` to `danger_margin` over precisely this, and the promoted
surface may not overclaim either. A pin asserts `bond` is in the
thresholds and absent from the lethal set, so the two can never be
conflated in a consumer's head or in a future doc edit.

### The loop N5 opened is closed

`labs/architecture/health_definition_gate.py` now imports
`DANGER_THRESHOLDS` from `mecha_engine.lifecycle` like every other
contracted name, instead of reaching into `mecha_engine.lifecycle.simulate`.
**The artifact regenerates with identical verdicts** — `grid_stability`
still `refuse_as_euphemism`, `danger_margin` still `adopt` — which is
the check that the promotion moved a surface and not a behaviour.

### No behaviour changed, and nothing else moved

The name binds the exact object `simulate` already used internally.
Every threshold value, every death condition and every episode number is
untouched; the package suite went **295 → 299** with the four new pins
and no existing assertion moved.

## Why this has no decision record

DR 0054 already made the decision this executes, and it named this task
as its blocker. The **W1 precedent** governs the mechanics: a widening
of this module's contracted surface is documented in
`mecha_engine_lifecycle_contract_gate.md` and pinned by the surface
probe, not given a record of its own. Writing DR 0055 here would record
the *execution* of a decision rather than a decision, which is the kind
of paperwork that makes a ledger harder to read rather than easier.

**What would need a record**: promoting the margin *formula* into the
engine. That is deliberately not done, and the pin above is what keeps
the question open rather than answered by drift.

## HONEST REMAINDERS

1. **The health readout still is not on screen.** O1 removed the
   blocker; **O2** is the task that lands it — and O2 must answer the
   design question DR 0054 refused to answer for the consumer: `play`
   *lowers* `danger_margin` (−0.075467, because play costs energy), so a
   keeper will read the drop as a bug.
2. **The margin formula is not in the engine**, by choice. Every
   consumer that wants `danger_margin` computes it from the promoted
   constant. If a second consumer appears, that duplication is the
   argument for promoting the formula — and it would need its own gate.
3. **`DANGER_THRESHOLDS` is not the lethal set.** It is documented and
   pinned as danger boundaries; `_life_status`'s four death conditions
   remain package-internal and were not promoted.

## Verification

RED — the frozen surface pin rejecting an undocumented widening:

```powershell
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_lifecycle_contract.py"
AssertionError: Lists differ: ['ACTIONS', 'DANGER_THRESHOLDS', 'advance_tick', 'choo[72 chars]ode'] != ['ACTIONS', 'advance_tick', 'choose_action_detailed', [51 chars]ode']

First differing element 1:
'DANGER_THRESHOLDS'
'advance_tick'

  ['ACTIONS',
-  'DANGER_THRESHOLDS',
   'advance_tick',
   'choose_action_detailed',
   'initial_state',
   'reward_for_transition',
   'run_episode']

----------------------------------------------------------------------
Ran 42 tests in 0.318s

FAILED (failures=1, errors=3)
```

GREEN — the whole package suite:

```powershell
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
----------------------------------------------------------------------
Ran 299 tests in 9.341s

OK
```

The N5 gate re-run through the public API, verdicts unchanged:

```powershell
PS> python -B labs/architecture/health_definition_gate.py
    -> ADOPT

adopted: ['danger_margin']
wrote data/architecture/health_definition_gate_stage0.json

PS> python -B -m unittest test_health_definition_gate
----------------------------------------------------------------------
Ran 25 tests in 0.111s

OK
```

## Sources

- `audits/TODO.md` (cycle 25 O1)
- `research/decision_records/0054-health-definition-danger-margin.md` (the record whose blocker this removes)
- `research/package_specs/mecha_engine_lifecycle_contract_gate.md` (the widening, documented — §"Danger thresholds (O1)"; the W1 section is the precedent followed)
- `research/package_specs/mecha_engine_contract_traceability_matrix.md` (Lifecycle Test Obligations, extended)
- `packages/mecha_engine/src/mecha_engine/lifecycle/__init__.py` (the export) · `simulate.py` (`DANGER_THRESHOLDS`, `_life_status`)
- `packages/mecha_engine/tests/test_lifecycle_contract.py` (+ `helpers/lifecycle_contract_driver.py`) — 4 new pins, package suite 295 → 299
- `labs/architecture/health_definition_gate.py` (now importing from the public API) · `data/architecture/health_definition_gate_stage0.json`
- `research/experiment_reports/2026-07-28-health-definition-gate.md` (N5)
