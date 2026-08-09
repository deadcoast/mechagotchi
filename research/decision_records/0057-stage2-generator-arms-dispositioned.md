# Decision Record 0057: Stage 2's Generator Arms Dispositioned — CPPN Rejected, Shape Grammar Watches, Nothing Adopted

Date: 2026-08-08

## Status

**ACCEPTED** (cycle 25 · SHARED track · Phase O, task O4) — by the rule
pre-registered in `labs/wfc_grid/stage2_generator_arms.py` before the
run, with the prediction recorded first and confirmed.

- **CPPN — REJECTED** as a generator (validity 0.12 vs the 0.85 dossier
  bar; the mechanism is the mass floor, not incoherence).
- **Shape grammar — WATCH** as a post-generator stabilizer (raises raw
  validity 0.01 → 1.00 with retention 1.0, then **ties** the incumbent
  `_finish` at 1.00/1.0 under a measured noise floor of 0.0).
- **Nothing is adopted; nothing incumbent moves.** `wfc_grid._finish`
  stays exactly as shipped (DR 0031); the loop's generation default
  stays the constrained layer (DR 0042).

## Context

The dossier names both methods and neither had ever been dispositioned
— the last undispositioned entries of Stage 2's generator program, the
same class of debt DR 0051 closed for the micro-learner conditions
after twelve cycles. O4's charter said *"judge them against the adopted
generation layer on its own bake-off terms"* — and the design phase
**corrected that framing before writing measurement code**, because the
dossier gives the two methods different jobs:

| method | dossier family | documented stance | judged as |
| --- | --- | --- | --- |
| CPPN | Indirect encoding | *"Keep as a late exploratory generator"* | a generator, on B2's own terms |
| shape grammar | Constraint systems | *"Use as validator or post-generator stabilizer"* | a stabilizer, vs the incumbent `_finish` |

Shape grammar's documented role is **already shipped** inside the
adopted WFC arm, so its honest question was never "can it generate" but
"does it beat the incumbent stabilizer".

## Pre-registered gates

Written in the module docstring before the run (`PRE_REGISTERED_RULE`),
with `PRE_RUN_PREDICTION` recorded first. Bars derive from committed
evidence, not choice: the 0.85 validity bar is the B2 bake-off's own
(`VALIDITY_BAR` imported, never redefined); the 0.68 distinct floor is
the committed refused `random` arm's measured rate, re-derived from the
committed artifact at run time; the stabilizer noise floors are the
incumbent pipeline run at two seeds (measured: 0.0/0.0). **Adopt was
pre-registered as unreachable at stage 0** — the charter's own verbs
are reject/watch/prototype, and adoption is a decision-record act at
documented scale, not a prototype verdict. **The instrument gate**: the
harness had to reproduce the committed `wfc` row exactly (all five
compared keys) before any new number was trusted — it did.

## Measured verdict

| | role | gated result | verdict |
| --- | --- | --- | --- |
| CPPN | generator | validity **0.12** (bar 0.85); distinct 1.0; readability 0.446945 vs baseline 0.79663 | **reject** |
| shape grammar | stabilizer | **0.01 → 1.00** validity, retention 1.0; vs incumbent **1.00/1.0**, noise 0.0 | **watch** |

**CPPN's mechanism, measured with the validator's own error strings**:
of 88 invalid bodies, 79 fail *only* the DR 0029 mass floor (connected
cores under 18 cells) and 9 disconnect. What the method is documented to
be good at showed up too — symmetry 0.475226, above the WFC family's
0.3973/0.395171 — and by the pre-registered rule none of it offsets
validity.

**Shape grammar is not refuted as a method** — the dossier's named risk
(over-constraining novelty) did not fire, and it repairs in one
deterministic, traced pass where the incumbent spends restarts. It is
**watched, not adopted**, because a tie is not a reason to replace a
shipped incumbent — DR 0031's hybrid-refutation logic, pointed the
other way.

## Decisions

1. **CPPN is rejected as a generator.** The recorded re-openers, and
   they are re-openers, not tasks: regularity **under mutation** (the
   documented selling point a generator-only bake-off cannot see), and
   an answer to the measured mass-floor mechanism.
2. **Shape grammar is watched.** The incumbent `_finish` stays; the
   ungated observations that could someday re-open the comparison are
   recorded in the artifact (a +0.016238 readability edge; the
   repair-vs-restart architecture, which only matters at a protocol
   where the incumbent's restart budget actually exhausts).
3. **The Stage 2 generator program's disposition debt is CLOSED.** Every
   generator-adjacent method the dossier names now carries a verdict:
   Markov/random (the honest floors, B2), WFC (adopted, DR 0031),
   constrained (adopted at the loop, DR 0042), hybrid (refuted,
   DR 0031), CPPN (rejected, here), shape grammar (watch, here). The
   unbuilt method *tracks* (MRF-lite, Lenia, reaction–diffusion, NCA
   layers) are different rows of the dossier's matrix with their own
   stances, and stay on the standing list.
4. Stdlib holds; nothing enters the package (DR 0028 unexercised).

## What this record does NOT do

1. It does not touch `wfc_grid._finish`, the WFC surface, or the loop's
   constrained default — no incumbent moved, no seam was added.
2. It does not judge shape grammar as a *standalone validator* (the
   stance's other half); the engine's `validate_grid` already holds
   that job.
3. It does not measure CPPN under evolutionary mutation — named as the
   re-opener, deliberately unmeasured here.
4. It does not run the human readability panel (owner-deferred, never a
   blocker); the readability numbers above are the labeled 8×8
   calibrated proxy.

## Sources

- `research/experiment_reports/2026-08-08-stage2-generator-arms.md` (this record's study)
- `labs/wfc_grid/stage2_generator_arms.py` (+ `test_stage2_generator_arms.py`, 25 pins) · `data/wfc_grid/stage2_generator_arms_stage0.json`
- `research/algorithm_cards/cppn_generator.md`, `research/algorithm_cards/shape_grammar_stabilizer.md`
- `data/wfc_grid/generation_bakeoff16_stage0.json` (the committed baseline rows and the refused-arm floor)
- `docs/project-research/deep-research/01/deep-research.md` (the method matrix; the constraint-systems and indirect-encoding rows)
- `research/decision_records/0031-wfc-generation-adoption.md`, `0042-generation-layer-loop-revisit.md`, `0051-micro-learner-conditions-efg.md` (the disposition-debt precedent)
- `sunsetted/TODO.md` (cycle 25 O4 and its two recorded charter corrections)
