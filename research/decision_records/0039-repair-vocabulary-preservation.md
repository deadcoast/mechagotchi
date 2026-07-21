# Decision Record 0039: Repair Preserves What It Cannot Yet Spell

Date: 2026-07-20

## Status

**Accepted and implemented** (cycle 20 · Phase J, with DR 0038's
implementation — the two landed together because the second blindness
was only observable once the first was cured).

## Context

DR 0038's implementation passed all five of its pre-registered gates
on the generation surface — and then the game's era loop went
EXTINCT: generation 0, zero elites. The diagnosis traced a SECOND
vocabulary-blind surface: the repair stack (the promoted
`mecha_engine.repair`, its runtime `_grids` twin, and the research CA
lab authority) still projected through the 5-token alphabet, and its
`_token_for_cell` coerced every unrecognized cell to BODY. Every
damage/repair cycle therefore rebuilt a rich creature as a legacy
body-blob: limbs became core mass, slip mass caps blew, token
restoration collapsed to ~0.53, nothing was admitted — the era died.
The game could breed rich creatures but could not keep them alive
through a single wound.

## Decision

Three changes, mirrored VERBATIM at all three sites
(`labs/cellular_automata/ca_nca_growth_repair.py` — the authority —
`mecha_engine/repair/{_grids,_features,train}.py`, and
`mecha_engine/runtime/_grids.py`):

1. **Vocabulary-preserving projection and reconstruction**: the full
   RICH_TOKENS alphabet round-trips — surviving cells keep their
   ratified role/material/organ pairings verbatim; the standalone
   anchor role normalizes to "A"; truly-unknown cells keep the
   defensive legacy fallback.
2. **Perception coarsening, recorded**: the learned regrowth head
   stays 5-class (the 11-class NCA retrain is a NAMED future record),
   and it PERCEIVES rich tokens by palette family — body-family
   (S/J/L) as B, sensory/light-family (N/P/D/F) as E — for feature
   encoding and training labels alike. Wounded rich cells regrow as
   legacy classes (restoration honestly partial); untouched rich
   cells are never rewritten.
3. **The guard's island drain**: refilled body cells at former
   limb/decoration positions form required-core ISLANDS that strict
   single-flip hill-climbing can never fix (each drain holds the
   error count until the last island falls). The stall path gains a
   structural, template-free pass: components of the matrix's own
   core cells; every core WOUND SITE outside the largest component
   flips to its best non-core live class, per-flip non-increasing
   acceptance. Runs ONLY on stall — every historically-passing guard
   outcome is untouched.

## Measured consequences

- **The era lives, with the whole vocabulary**: the diagnostic
  campaign that went extinct now runs its generations with 12 elites
  whose cells span antenna, body, decoration, effect, eye, joint,
  limb, mouth, sensor, shell — the game breeds creatures it could
  never spell before.
- **The repair boundary receded**: the boundary study re-measures
  session-band failures at **0.0** (was: a measured skip gradient
  with core disconnection the only cause); only mortal wounds at the
  harshest regime fail (8.75%), cause now ANCHOR LOSS — the
  disconnected-core failure mode is gone. The replay recorder's
  truncated-life fixture rides the measured residual boundary.
- **The generation bake-off verdict flipped**: with the constrained
  path now clearing the rich-alphabet eligibility bar it once failed,
  it WINS the 16×16 bake-off by the same pre-registered rule (WFC
  6.92 ms/candidate, constrained winner on the quality rule). WFC's
  adoption (DR 0031) STANDS until its own record revisits it — the
  pin records the measured verdict, never the adoption.
- 8×8 legacy corpora stay byte-identical everywhere (the additivity
  law shared with DR 0038).

## HONEST REMAINDER

1. **The 11-class regrowth head** — repair can preserve but not
   REGROW the rich vocabulary; a wounded limb returns as body/eye.
   The retrain (features, classes, weights, contract) is its own
   record when the ecology demands regrown limbs.
2. **Mortal wounds remain mortal** — the harshest-regime anchor-loss
   gradient is the game's honest death boundary, recorded not tuned.
3. **DR 0031 revisit** — the flipped bake-off verdict is named
   evidence for a future generation-layer record, not an adoption
   change here.

## Sources

- `research/decision_records/0038-vocabulary-complete-generation-alphabet.md` (the charter this completes)
- `labs/cellular_automata/ca_nca_growth_repair.py` (+ `test_repair_vocabulary_preservation.py`, `test_repair_scale16.py`)
- `packages/mecha_engine/src/mecha_engine/repair/`, `packages/mecha_engine/src/mecha_engine/runtime/_grids.py`
- `labs/repair_boundary/repair_validity_boundary.py` (+ the regenerated boundary artifact)
- `labs/wfc_grid/generation_bakeoff16.py` (+ the regenerated bake-off artifact)
- `game/tests/test_replay.py` (the truncated-life fixture on the measured boundary)
