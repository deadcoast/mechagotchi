# Decision Record 0058: `happiness` Is `social_warmth` — a Duplicate Refused, the Engine's Own Statistic Withheld, and the Readout Landed the Same Day

Date: 2026-08-08

## Status

**ACCEPTED** (cycle 26 · ENGINE gate → GAME landing · Phase P, task
P2) — by the five-gate rule pre-registered in
`labs/architecture/happiness_definition_gate.py` before the run, with
the prediction recorded first and confirmed.

- **`social_warmth` — ADOPTED** as the CHOSEN definition of the
  documented VISIBLE axis `happiness`: the mean of the engine's own
  `recent_interactions` window (feed/play, last 5 ticks).
- **`bond_rename` — REFUSED AS A DUPLICATE** (G5): its per-tick series
  is the shown `bond` readout's, tick for tick. One engine number may
  not wear two visible names.
- **`need_balance` — WITHHELD** (G2): the engine's own per-tick
  contentment statistic responds to the keeper's verbs *under* the
  measured 0.0685 floor — and negatively from a near-target start —
  with its corpse reading (0.646661) recorded as the second liability.
- **The readout is ON THE PLAYER'S SCREEN in the same slice** (the O2
  lesson): mirrored per the boundary law, parity-pinned against this
  study's committed artifact, `chosen: true` on the surface, and its
  legibility carried in engine truth (`tended_ticks` / `window_ticks`).

## Context

§1.17 names `happiness` and never defines it; M5 measured no engine
source; DR 0048 put the axis out of scope *pending a documented
definition*. The N5 → O2 pattern (choose by gate, refuse euphemisms,
land with the adoption) is proven twice; P2 runs it end to end for the
first of DR 0048's two remaining gaps. Every candidate reads only what
the engine already records — the lifecycle has carried
`recent_interactions` and written `entry["balance"]` since Stage 0 —
so nothing shown is invented (DR 0021's first law).

## Pre-registered gates

N5's four, verbatim in shape, plus the one this axis needed:

| gate | question | failure verdict |
| --- | --- | --- |
| G1 | does the definition name what it reads? | withhold |
| G2 | can the KEEPER move it, ≥ the measured floor? | withhold |
| G3 | do a cherished and a neglected life separate on it? | withhold |
| G4 | does keeper-relieved distress RAISE it? | **refuse_as_euphemism** |
| **G5** | is it distinct, per-tick, from every readout already shown? | **refuse_as_duplicate** |

G5 outranks G4 — the sharper accusation: nothing about the number is
wrong, only the second name. **Instrument gates**: the recomputed G2
floor had to reproduce N5's committed **0.0685** exactly, and the
`need_balance` mirror was pinned tick-for-tick against the engine's own
recorded balances (633 ticks, max |Δ| 0.0); either failing raises
instead of judging. **Selection among eligibles, pre-registered**: the
lowest reading on the neglected corpse (N5's refusal logic made into
the selection statistic), ties toward fewer engine fields read.

## Measured verdict

| candidate | feed / play | relief | corpse | care | verdict |
| --- | --- | --- | --- | --- | --- |
| `bond_rename` | +0.016 / +0.0685 | +0.016 | 0.4315 | 1.0 | refuse_as_duplicate |
| `need_balance` | −0.046932 / −0.027172 | +0.05929 | 0.646661 | 0.79862 | withhold |
| `social_warmth` | +0.083333 / +0.083333 | +0.2 | **0.0** | 0.8 | **adopt** |

The adopted definition carries the strongest honesty property any
candidate showed — **the neglected corpse reads 0.0** — and the design
property the keeper will actually see, measured in the lab and
re-measured live in the client: **`play` raises happiness while it
lowers the health readout** (+0.083333 vs −0.075467). The two bars
answer different questions and both tell the truth.

## Decisions

1. **`happiness` is `social_warmth`**, a CHOSEN definition (§1.17
   still does not define the axis, and the surface says `chosen`).
2. **The readout ships with the adoption** — `mecha_game/happiness.py`
   (mirrored, parity-pinned), a `snapshot()` entry, 11 pins including
   the live play-differentiation.
3. **The P1 instrument moves with the surface, deliberately**: the
   axis-split builder now expects exactly two DR-explained differences
   from the committed M5 survey (health/DR 0054, happiness/this
   record), still raising on any other; the regenerated artifact reads
   **7 visible on screen / 1 absent upstream / 2 hidden surfaced**;
   §1.17 carries a dated addendum. (The precedent: O2 updating N5's
   label guard when the adoption landed.)
4. **The refusal and the withholding are first-class findings.**
   `bond_rename`'s refusal makes the no-duplicate rule enforceable
   precedent; `need_balance`'s withholding records both measured
   liabilities (under-floor, wrong-direction keeper response; a mean
   that reads 0.65 on a corpse — the property that made health a
   minimum).

## What this record does NOT do

1. **It does not define happiness as welfare or outcomes.** The
   definition is *recent keeper warmth*, one input; a tended-but-dying
   companion reads happy beside a collapsing health bar, and the
   two-readout design makes that legible rather than hidden. A
   different documented definition is a different gate.
2. **It does not touch the engine.** No new field, no new seam; the
   window, its bound (5 ticks — the engine's own, not tuned here), and
   every input are the incumbent lifecycle's, unchanged.
3. **It does not resolve `cleanliness`** — a MECHANIC gap (DR 0048),
   P3's charter.
4. **It does not run the human panel** (owner-deferred, never a
   blocker); "happiness" here is a labelled chosen definition, not a
   measured human affect.

## Sources

- `research/experiment_reports/2026-08-08-happiness-definition-gate.md` (this record's study)
- `labs/architecture/happiness_definition_gate.py` (+ 24 pins) · `data/architecture/happiness_definition_gate_stage0.json`
- `game/src/mecha_game/happiness.py` · `game/src/mecha_game/session.py` · `game/tests/test_happiness_readout.py` (11 pins) · `game/tests/test_companion_axis_split.py`
- `data/game_client/companion_axis_split_stage0.json` (regenerated under the new surface: 7/1/2)
- `research/decision_records/0048-visible-companion-state-axes.md`, `0054-health-definition-danger-margin.md`, `0055-health-readout-binding-axis.md`, `0021-game-loop.md`
- `docs/project-research/validity-research.md` §1.17 (the axis; the P2 dated addendum)
- `sunsetted/TODO.md` (cycle 26 P2)
