# `happiness` — a Definition Adopted, a Duplicate Refused, the Engine's Own Statistic Withheld — and the Readout Lands the Same Day (Cycle 26 · ENGINE→GAME · P2)

Date: 2026-08-08

## WHY

`validity-research.md` §1.17 names `happiness` a **VISIBLE** companion
state axis and never defines it. M5 measured that the engine has no
source — *"no field, no derivation, and no documented formula"* — and
DR 0048 put the axis out of scope **pending a documented definition**.
P2 is that gate, running the proven N5 → O2 pattern **end to end in one
slice**, because O2's lesson binds: adopted-but-not-landed is exactly
the debt that quietly becomes permanent.

## WHAT

`labs/architecture/happiness_definition_gate.py` (+ 24 pins), the rule
and the prediction pre-registered before the run. **Three candidates,
all declared CHOSEN, all reading only what the engine already
records** (DR 0021's first law — nothing invented):

- **`bond_rename`** — the naive candidate every player would assume:
  `bond`, surfaced under the name "happiness". Already on screen under
  its own accurate name.
- **`need_balance`** — the engine's OWN per-tick contentment statistic
  (`1 − mean(|axis − target|)`), computed and recorded by
  `advance_tick` in every history entry since Stage 0.
- **`social_warmth`** — the mean of the engine's `recent_interactions`
  window: the last-5-tick trace of keeper care (feed/play), carried in
  state and consumed by the switchboard since Stage 0.

(`curiosity` was deliberately not a candidate: a SLIP-derived constant
the lifecycle never moves would fail G2 by construction — a strawman.)

**Five gates**: N5's four verbatim in shape — G1 declared sources;
G2 keeper-responsive against the measured floor, **with the recomputed
floor required to reproduce N5's committed 0.0685 exactly** (instrument
gate — a mismatch raises); G3 care-coupled (a cherished and a
neglected life must separate); G4 the label test (keeper-relieved
distress must raise the bar, else `refuse_as_euphemism`) — plus the
gate this axis needed that `health` did not: **G5 distinct-from-shown**.
A per-tick identity with a readout already on the player's screen under
another name earns **`refuse_as_duplicate`**, which outranks the
euphemism verdict — the sharper accusation: nothing about the number is
wrong, only the second name. The `need_balance` mirror was additionally
pinned tick-for-tick against the engine's own recorded balances
(**633 ticks, max |Δ| = 0.0**).

**Selection among eligibles, pre-registered**: the lowest final reading
on the neglected corpse — N5's own refusal logic (what the bar shows at
death measures the label's honesty) made into the selection statistic.

## FINDINGS

| candidate | keeper response (feed / play) | relief | neglect corpse | care final | verdict |
| --- | --- | --- | --- | --- | --- |
| `bond_rename` | +0.016 / +0.0685 | +0.016 | 0.4315 | 1.0 | **REFUSE_AS_DUPLICATE** (G5: ≡ the shown `bond`) |
| `need_balance` | **−0.046932 / −0.027172** | +0.05929 | **0.646661** | 0.79862 | **WITHHOLD** (G2, under the 0.0685 floor) |
| `social_warmth` | +0.083333 / +0.083333 | +0.2 | **0.0** | 0.8 | **ADOPT** |

**The prediction (recorded first) was confirmed**, including its
deliberately named uncertainty: `need_balance`'s keeper responses fell
*under* the floor and *negative* — feeding an un-hungry creature moves
the mean distance away from targets — and its corpse reading (0.65)
landed where the prediction's "~0.7, a mean hides the killer axis"
warned. It fails structurally, not as a euphemism (its relief is
honest); the withholding records both liabilities.

**`bond_rename` passed every behavioural gate and was refused on
exactly one ground**: its per-tick series is the shown `bond` readout's,
tick for tick. One engine number may not wear two visible names.

**`social_warmth` adopted with the strongest honesty property any
candidate showed**: the neglected corpse reads **0.0** — an ignored
companion's window empties — while a cherished life reads 0.8, both
keeper verbs move it +0.083333 (over the floor), and relieving a
starving companion raises it +0.2.

**The design property the keeper will actually see, measured in the lab
and re-measured live in the client**: `play` RAISES happiness
(+0.083333) while it LOWERS the health readout (−0.075467). The two
bars answer different questions — *am I being tended* vs *how close is
trouble* — and both tell the truth. This is the differentiation that
makes happiness informative beside health, recorded as an observation
(never a gate).

### The landing (same slice, the O2 pattern)

`game/src/mecha_game/happiness.py` mirrors the formula (never imports
it — boundary law), pinned against the committed artifact's
`game_mirror_parity_values`; `session.snapshot()` carries the readout
with its legibility surface in engine truth — `tended_ticks` /
`window_ticks` (*"happiness 0.2 — 1 of last 5 ticks tended"*), and
`chosen: true` on the surface (DR 0055's pattern). 11 game pins,
including the live client reproducing the play-differentiation.

**The P1 instrument moved with the surface, deliberately.** The
axis-split builder now expects exactly **two** DR-explained differences
from the committed M5 survey (health → DR 0054, happiness → DR 0058) and
still raises on any other; the regenerated artifact reads
**7 visible on screen / 1 absent upstream / 2 hidden surfaced**, and
§1.17 carries a dated addendum under P1's note. The precedent is O2
updating N5's label guard when the adoption landed.

## HONEST REMAINDERS

1. **The definition is CHOSEN, and one-input.** Happiness here is
   *recent keeper warmth* and nothing else: a fed, rested, healthy
   companion left alone five ticks reads 0.0. That is defensible
   tamagotchi semantics (an ignored pet is not a happy pet) and the
   surface says exactly what it measures — but a different documented
   definition would be a different gate.
2. **A tended-while-dying companion reads happy.** The window measures
   care received, not outcomes; a keeper hand-feeding a creature that
   is dying anyway sees high happiness beside a collapsing health bar.
   The two-readout design makes that legible rather than hidden.
3. **The window is 5 ticks** — the engine's own bound, inherited, not
   tuned here. A different horizon is a different definition.
4. **One seed creature, no SLIP profile** (N5's inherited limit).
5. **`cleanliness` stays the one absent axis** — it needs a MECHANIC,
   and that is P3's charter, not this record's.

## Verification

RED (both surfaces, watched failing before implementation):

```text
PS> python -B -m unittest discover -s labs/architecture -p "test_happiness_definition_gate.py"
ModuleNotFoundError: No module named 'happiness_definition_gate'
FAILED (errors=1)

PS> uv run python -B -m unittest discover -s game/tests -p "test_happiness_readout.py"
ModuleNotFoundError: No module named 'mecha_game.happiness'
FAILED (errors=1)
```

GREEN:

```text
PS> python -B -m unittest discover -s labs/architecture -p "test_happiness_definition_gate.py"
Ran 24 tests in 0.295s
OK
PS> python -B -m unittest discover -s labs/architecture -p "test_*.py"
Ran 76 tests in 15.704s
OK
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 228 tests in 15.724s
OK
```

The lab invocation that produced the artifact:

```text
PS> python -B labs/architecture/happiness_definition_gate.py
instrument: committed floor 0.0685 reproduced; balance mirror parity {'ticks_compared': 633, 'max_abs_difference': 0.0}

  bond_rename
    keeper response {'feed': 0.016, 'play': 0.0685}  distress relief 0.016
    neglect finals [0.4315, 0.4315, 0.4315]  care finals [1.0, 1.0, 1.0]  coupled True  duplicate_of bond
    -> REFUSE_AS_DUPLICATE  (failed G5_distinct_from_shown)
  need_balance
    keeper response {'feed': -0.046932, 'play': -0.027172}  distress relief 0.05929
    neglect finals [0.646661, 0.646661, 0.646661]  care finals [0.79862, 0.79862, 0.79862]  coupled True  duplicate_of None
    -> WITHHOLD  (failed G2_keeper_responsive)
  social_warmth
    keeper response {'feed': 0.083333, 'play': 0.083333}  distress relief 0.2
    neglect finals [0.0, 0.0, 0.0]  care finals [0.8, 0.8, 0.8]  coupled True  duplicate_of None
    play raises it while health falls: True
    -> ADOPT

adopted: ['social_warmth']
prediction_confirmed
wrote data/architecture/happiness_definition_gate_stage0.json
```

The regenerated P1 instrument under the new surface:

```text
{"visible_on_screen": 7, "visible_absent_upstream": 1, "hidden_surfaced": 2}
"prediction_confirmed"
wrote data/game_client/companion_axis_split_stage0.json
```

## Sources

- `sunsetted/TODO.md` (cycle 26 P2) · `research/decision_records/0058-happiness-definition-social-warmth.md` (the record this study produced)
- `research/decision_records/0048-visible-companion-state-axes.md` (the out-of-scope this resolves), `0054`/`0055` (the N5 → O2 pattern), `0021-game-loop.md` (the first law)
- `labs/architecture/happiness_definition_gate.py` (+ `test_happiness_definition_gate.py`, 24 pins) · `data/architecture/happiness_definition_gate_stage0.json`
- `game/src/mecha_game/happiness.py` (the mirror) · `game/src/mecha_game/session.py` (the snapshot entry) · `game/tests/test_happiness_readout.py` (11 pins) · `game/tests/test_companion_axis_split.py` (updated to the new surface)
- `data/game_client/companion_axis_split_stage0.json` (regenerated: 7/1/2)
- `packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py` (`recent_interactions`, `_need_balance`, `ACTION_EFFECTS`)
- `docs/project-research/validity-research.md` §1.17 (now carrying the P2 dated addendum)
