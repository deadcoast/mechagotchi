# `cleanliness` Earns Its Mechanic — an Opt-In Seam, Every Parameter Derived, and Dirt That Hurts Only the Neglected (Cycle 26 · ENGINE→GAME · P3)

Date: 2026-08-09

## WHY

`validity-research.md` §1.17 names `cleanliness` a **VISIBLE** companion
state axis. M5 measured the gap precisely — *"there is no clean action —
and no state accumulates dirt"* — and DR 0048 recorded it as the
MECHANIC kind of gap: *"it needs a need, a decay, an action that answers
it, and its interaction with the switchboard policy and the reward
function."* Unlike `health` and `happiness`, no display work could close
it: the engine itself had nothing for a bar to read. P3 builds the
smallest honest mechanic as an **additive engine seam** and gates
whether it may ship, with the charter's own refusals first-class.

## WHAT

**The seam** (package `lifecycle/simulate.py`, opt-in via the additive
`mechanics` keyword on `initial_state`/`run_episode`; contract section
appended to the lifecycle gate spec, the O1 precedent). **Every
parameter is DERIVED from the incumbent engine, never picked**:

| parameter | value | derivation |
| --- | --- | --- |
| decay / tick | 0.0124 | the median incumbent drift magnitude at the Stage 0 default weights |
| mutate's extra mess | 0.055 | mutate's own grid-stability cost — the one action the engine already treats as body-disturbing |
| clean's restore | 0.32 | feed's own hunger relief — the incumbent table's strongest care effect |
| dirt→stress coupling | 0.01 | the engine's own need→stress coefficient (the hunger term), pointed at dirt |

The seed reads the grid's own mean cell damage (a fresh companion is as
clean as its body is undamaged). **What deliberately does not change**:
`ACTIONS` (the autonomous policies never choose `clean` — the companion
cannot clean itself, the documented interaction model); `TARGETS`,
`_need_balance`, `_snapshot`, the reward, `_life_status` (the incumbent
statistics keep their meaning; the mechanic is NON-LETHAL). `clean`
carries no incumbent-axis effects — cleaning is time spent, not
nourishment — and you cannot clean a corpse (dead states return
unchanged, pinned).

**The seam law, proven not asserted**: 17 package pins
(`test_lifecycle_cleanliness_seam.py`) hold off-mode byte-identity
against the **committed Stage 0 comparator's own numbers** (survival
72, need_balance 0.789129, the exact final state; idle's tick-11
starvation at 0.121004) and a **frozen 19-key state list** — the M3
lesson, never new-vs-new. Package suite 299 → **316**, no existing
assertion moved; lab parity suites untouched and green.

**The gate** (`labs/lifecycle_sim/cleanliness_mechanic_gate.py`, 19
pins; rule and prediction pre-registered): G1 the need decays; G2 the
clean verb clears N5's committed 0.0685 floor from a dirty live state;
G3a the consequence is measurable on the neglect stream (deterministic
engine — the noise floor is exactly zero); G3b the consequence is
bounded (survival and death cause unchanged on both streams; welfare
impact under the documented D6 5% bar) — failing G3a is the charter's
own **`blocked_on_mechanic`**, failing G3b is
**`refuse_as_lethal_cosmetic`**, and the refusals outrank the
withholdings.

## FINDINGS

**Verdict: ADOPT — prediction confirmed on every count.**

- **Instruments first**: both committed episodes reproduced off-mode
  exactly; N5's committed keeper floor 0.0685 reproduced.
- **G1**: cleanliness falls strictly every live tick of an un-cleaned
  cared-for life (1.0 → 0.628 over 30 ticks).
- **G2/G4**: one `clean` from the dirty live state responds
  **+0.3076** (0.32 restore − 0.0124 decay) — 4.5× the floor.
- **G3a**: on the neglect stream the dirt→stress coupling moves final
  stress by exactly **+0.00682** against the incumbent — measurable,
  deterministic, honest.
- **G3b**: the tick-11 starvation does not move; the autonomous
  switchboard still survives 72/72 and its need_balance moves by
  **1.6e-05** relative — four orders of magnitude under the 5% bar.
- **The fairness finding, predicted and confirmed**: an attentive
  keeper's care **absorbs the dirt pressure entirely** — the care
  stream's stress delta is exactly **0.0** (feed and sleep relief
  dwarfs the ≤0.01/tick coupling). **Dirt hurts only the neglected.**
  A keeper who tends their companion never pays for not cleaning;
  a neglected companion suffers a little more, a little sooner.

### The landing (same slice)

The client supports the mechanic end to end for **opted-in covenants**:
`CompanionSession(..., mechanics=("cleanliness",))` shows the axis in
its needs (the state's own value, verbatim — one `NEED_DISPLAY` entry,
shown only when the state carries the key), offers the keeper the
`clean` verb, and preserves the mechanic across succession and
save/resume (rung-conditional save key — a default save is
byte-identical to the pre-seam format). A **default session is
byte-identical to the pre-seam client**: no cleanliness anywhere in the
snapshot, no clean verb, the engine's verbatim refusal if one is
attempted. 10 game pins; game 228 → **239**.

**The default covenant does not enable it — deliberately, and the cost
is priced**: flipping the default changes every committed session-built
evidence artifact (a regeneration cascade) and the default play feel —
a product decision with its own future record, named in DR 0059, never
smuggled. The P1 split instrument moved with the engine (three
DR-explained differences now; regenerated: **7 on screen / 0 absent
upstream / 2 hidden surfaced**) — **no documented visible axis lacks an
engine source any longer**; §1.17 carries the P3 dated addendum.

## HONEST REMAINDERS

1. **Opt-in reach**: a player gets the axis only through a session
   constructed with the mechanic; a SLIP-carried opt-in needs a
   schema-ladder rung (DR 0012), and the default-covenant flip is its
   own record. Until one of those lands, the mechanic is engine truth
   without default players.
2. **The switchboard never cleans and never begs for cleaning** — the
   companion has no beg-display for dirt. Whether it should is a design
   question for the covenant/deliberation stack, not smuggled here.
3. **Cleanliness is outside `need_balance` and the reward** — the
   welfare statistic does not see dirt (changing what `need_balance`
   means for every committed artifact is forbidden ground, DR 0053's
   spirit). A dirt-aware welfare metric would be a new measurement.
4. **One seed creature, one covenant** (the Stage 0 comparator pair);
   magnitudes would move under other profiles.

## Verification

RED (three surfaces, watched failing before implementation):

```text
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_lifecycle_cleanliness_seam.py"
TypeError: initial_state() got an unexpected keyword argument 'mechanics'
PS> python -B -m unittest discover -s labs/lifecycle_sim -p "test_cleanliness_mechanic_gate.py"
ModuleNotFoundError: No module named 'cleanliness_mechanic_gate'
PS> uv run python -B -m unittest discover -s game/tests -p "test_cleanliness_mechanic.py"
TypeError: CompanionSession.__init__() got an unexpected keyword argument 'mechanics'
```

GREEN:

```text
PS> python -B -m unittest discover -s packages/mecha_engine/tests -p "test_*.py"
Ran 316 tests in 5.294s
OK
PS> python -B -m unittest discover -s labs/lifecycle_sim -p "test_*.py"
Ran 43 tests in 0.335s
OK
PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 239 tests in 12.864s
OK
```

The lab invocation that produced the artifact:

```text
PS> python -B labs/lifecycle_sim/cleanliness_mechanic_gate.py
instrument: committed episodes reproduced (switchboard True, idle True); keeper floor 0.0685 reproduced
G1 decays True  G2 clean response 0.3076 (floor 0.0685)  G4 answers True
G3a neglect stress delta 0.00682  G3b survival unchanged True, welfare impact 1.6e-05 (bar 0.05)
care absorbs dirt pressure: True (care stress delta 0.0)

verdict: ADOPT
prediction_confirmed
wrote data/lifecycle/cleanliness_mechanic_gate_stage0.json
```

Process note: two probe defects were caught and fixed at GREEN stage,
before the study ran — the first dirty-state probe idled the companion
to death and then tried to clean the corpse (the engine correctly
returned the dead state unchanged, which became its own pin), and the
first clean-stream had no feeding. Instrumentation fixes, recorded; no
gate, bar, or verdict text was touched after the run.

## Sources

- `sunsetted/TODO.md` (cycle 26 P3) · `research/decision_records/0059-cleanliness-mechanic-opt-in.md` (the record this study produced)
- `research/decision_records/0048-visible-companion-state-axes.md` (the MECHANIC gap), `0021-game-loop.md` (engine truth), `0053` (restate/meaning rules), `0012-slip-schema-extension-ladder.md` (the named opt-in rung)
- `packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py` (the seam) · `packages/mecha_engine/tests/test_lifecycle_cleanliness_seam.py` (17 pins)
- `research/package_specs/mecha_engine_lifecycle_contract_gate.md` (the appended seam section)
- `labs/lifecycle_sim/cleanliness_mechanic_gate.py` (+ 19 pins) · `data/lifecycle/cleanliness_mechanic_gate_stage0.json`
- `game/src/mecha_game/session.py` (the opt-in landing) · `game/tests/test_cleanliness_mechanic.py` (10 pins)
- `data/game_client/companion_axis_split_stage0.json` (regenerated: 7/0/2) · `data/lifecycle/lifecycle_stage0.json` (the committed comparator the seam is pinned against)
- `docs/project-research/validity-research.md` §1.17 (the P3 dated addendum)
