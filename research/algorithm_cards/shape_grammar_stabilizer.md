# Algorithm Card: Shape-Grammar Stabilizer

## Purpose

Disposition the dossier's shape-grammar entry at its documented role.
It is filed under *Constraint systems* (with WFC and SAT/SMT), whose
stance is *"Use as validator or post-generator stabilizer"* — explicitly
NOT a primary generator, which is why O4 corrected its own charter's
bake-off-both framing. The documented role is **already shipped** as
`wfc_grid._finish` (DR 0031's adopted arm), so the honest question is
the sharper one: does a shape-grammar stabilizer **beat the incumbent
`_finish`**? (cycle 25 O4)

## Mathematical Basis

- **Named constraint productions over the token matrix**, applied in a
  fixed order, deterministic and RNG-free (smallest-(y, x) tie-breaks
  throughout): seed germ cell (empty grids get a body seed); anchors
  read as body; largest 8-connected core survives (the incumbent's own
  rule, shared as a production); grow core to the DR 0029 floor
  (frontier growth over empty neighbors); require a sensor cell; anoint
  exactly one anchor.
- **Every applied production is named in a trace** — the dossier stance
  includes "validator", and an unexplainable validator is worthless.
- **Repair, not restart**: where the incumbent `_finish` treats global
  cardinality constraints as restart conditions (bounded retries), the
  grammar rewrites the candidate in one deterministic pass. The input
  grid is never mutated.

## Inputs

- Any grid payload (projected to the rich token matrix); measured on the
  incumbent's own raw-collapse stream at the committed B2 protocol

## Outputs

- A stabilized grid plus the production trace;
  `data/wfc_grid/stage2_generator_arms_stage0.json`

## Strengths

- Does the documented job emphatically: raw collapse validity
  **0.01 → 1.00** with **distinct retention 1.0** (the dossier's named
  risk, over-constraining novelty, did not fire)
- Deterministic, explainable (trace), single-pass — no restart budget
- Recorded beside the verdict (not gated): readability 0.701285 vs the
  incumbent's 0.685047

## Weaknesses

- **Ties the incumbent `_finish` at 1.00/1.0 with a measured two-seed
  noise floor of 0.0** — it adds nothing at the pre-registered criteria
- Descriptor novelty 0.21 vs the incumbent's 0.25 (recorded, not gated)

## Failure Modes

- A repair pass can manufacture validity for arbitrarily degenerate
  input (germ + growth builds a floor-mass core from an empty grid) —
  useful as a stabilizer, dangerous if ever mistaken for evidence that
  the upstream generator is healthy

## Integration Risk

Low as a lab instrument; nil as shipped — the incumbent stays, and
adoption never deletes the incumbent anyway.

## License Status

Original stdlib-only code, Apache-2.0.

## Prototype Result

At the committed protocol (batch 100, seed 1030), head-to-head on the
same raw-collapse stream: grammar 1.00 validity / 1.0 retention;
incumbent pipeline 1.00 / 1.0; noise 0.0 (measured, seeds 1030/2061).
A tie. Prediction (recorded first) confirmed.

## Decision

**WATCH** (DR 0057). A tie is not a reason to replace a shipped
incumbent — the DR 0031 hybrid-refutation logic, pointed the other way:
the method is not refuted, it just adds nothing at the gated criteria.
The recorded observations that could re-open it are named in the
artifact: the readability edge (+0.016238, ungated here) and the
repair-vs-restart architecture, which would only matter at a protocol
where the incumbent's restart budget actually exhausts.

## Sources

- `labs/wfc_grid/stage2_generator_arms.py` (+ `test_stage2_generator_arms.py`)
- `data/wfc_grid/stage2_generator_arms_stage0.json`
- `research/experiment_reports/2026-08-08-stage2-generator-arms.md`
- `research/decision_records/0057-stage2-generator-arms-dispositioned.md`
- `labs/wfc_grid/wfc_grid.py` (`_finish` — the incumbent this method was judged against)
- `docs/project-research/deep-research/01/deep-research.md` (the constraint-systems row)
- `research/algorithm_cards/wfc_grid.md` (the incumbent's card)
