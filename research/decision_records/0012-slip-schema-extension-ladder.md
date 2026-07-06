# Decision Record 0012: The SLIP Schema Extension Ladder

Date: 2026-07-05

## Status

**Accepted** (audit task T3; owner: "Next action: T3, the SLIP schema
extension ladder --go", 2026-07-05). Defines HOW the SLIP schema grows
from v0.1.0 toward the og scope ratified for pursuit by DR 0011, and
executes the first rung (T3.1 `forbidden_traits`).

## The rules of the ladder

1. **Dual-version authority.** `slip_version` becomes an enum:
   `"0.1.0"` (the frozen baseline — exactly the original key set) and
   `"0.2.0"` (baseline + the ladder's optional fields). Every existing
   fixture and every profile the promoted modules consume stays 0.1.0
   and validates byte-identically; ladder fields are legal ONLY under
   0.2.0 (a 0.1.0 profile carrying one is rejected with a version
   error). Breaking changes, if ever needed, take a new decision record
   and a major version.
2. **Enforced-or-consumed, never decorative.** A field enters the schema
   only together with its enforcement (validator/alignment) or its
   consumer (lifecycle, switchboard, learning, archive), plus fixtures
   exercising both directions. This is the standing SLIP discipline,
   now written down.
3. **All four validation surfaces move together**: the Stage 0 authority
   (`labs/grid_genome/slip.py`), the dependency-free duplicate
   (`labs/slip_validator/slip_validator.py`), the pydantic mirror
   (`labs/slip_validator/pydantic_contract.py`) with its regenerated
   schema, and the hand-authored `research/slip/slip.schema.json`. The
   cross-validator agreement tests are the gate.
4. **The package boundary is explicit.** Promoted modules
   (`mecha_engine.generation`, `.lifecycle`, and their `_slip` mirrors)
   pin `slip_version == "0.1.0"` and exact keys — **v0.2 profiles are
   deliberately rejected by package simulations** until a dedicated
   promoted-module port DR (parity implications documented there).
   Until that port, v0.2 fields live in the authoring/alignment world:
   the workshop (which validates through the lab authority), the wire's
   founder admission, and lab-side experiments that use the lab
   authority. This mirrors the repo's promotion discipline: lab-proven
   first, package by decision record.
5. **Rung order** (from the audit; each rung its own change with triads):
   T3.1 `forbidden_traits` (this record) → T3.2 `risk_tolerances`
   (lifecycle/switchboard consumers) → T3.3 `learning_switches`
   (`mecha_engine.learning` consumers) → T3.4 `lineage_preferences`
   (archive/evolve parenting) → T3.5 `species_class` + `materials` +
   `visual_grammar` (with T4/T15) → T3.6 the og gates (20-archetype
   expressiveness test, fuzz pack with false-pass ≤ 1%, profile zoo
   15 → 100).

## Rung T3.1: `forbidden_traits`

Shape (optional, v0.2-only):

```json
"forbidden_traits": {
  "roles": ["shell", "antenna"],
  "materials": ["light"]
}
```

- Value vocabularies mirror the grid genome schema's cell `role` and
  `material` enums (minus `empty`/`void`, which cannot be forbidden);
  a pin test cross-checks the mirrors against
  `research/grid_genome/grid_genome.schema.json` so drift is impossible.
- Contradiction guard: forbidding the cell role a required organ role
  implies (`sensor→eye`, `expression→mouth`, `body_core→body`) is a
  validation error — a profile may not require what it forbids.
- Enforcement: `is_grid_aligned` rejects any grid containing a
  forbidden role or material, with the offending values named. The
  workshop's live chips, the slip-creator's fit counts, and the T1
  wire's founder admission all enforce it immediately (they run on the
  lab authority).

## Consequences

- The ladder has law: versioning, discipline, surfaces, boundary, order.
- The workshop slip creator gains forbidden-trait controls and writes
  `slip_version` automatically (0.1.0 when no ladder field is used —
  maximum compatibility — else 0.2.0).
- A future "port SLIP v0.2 into mecha_engine" DR is the sanctioned path
  for package-side consumption (queued under T3's completion).

## Sources

- `audits/TODO.md` (T3), `audits/audit-devspec.md` (§2.5, addendum A0)
- `research/decision_records/0011-run-one-run-two-reconciliation.md`
- `labs/grid_genome/slip.py`, `labs/slip_validator/slip_validator.py`, `labs/slip_validator/pydantic_contract.py`
- `research/slip/slip.schema.json`, `research/grid_genome/grid_genome.schema.json`
- `packages/mecha_engine/src/mecha_engine/generation/generate.py`, `packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py` (the package boundary)
