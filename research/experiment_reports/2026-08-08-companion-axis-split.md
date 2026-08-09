# The §1.17 Axis Split, Measured As Shipped — Six of Eight Visible On Screen, Two Hidden Axes Surfaced Honestly (Cycle 26 · SHARED · P1)

Date: 2026-08-08

## WHY

`validity-research.md` §1.17 names eight VISIBLE and eight HIDDEN
companion state axes and defines none of them. Three successive
findings left it **measurably stale against the shipped client**, each
recorded elsewhere but never measured *as a split*: M5/DR 0048
corrected the gap count (three real gaps, not five); N5/DR 0054 found
the client already surfaces two documented-HIDDEN axes under accurate
names; O2/DR 0055 moved `health` from "no source" to on-screen under a
chosen definition. And M5 left an honest remainder P1 exists to close:
*the game-side display of age and mood was cited by file reference, not
measured* — a lab cannot import the game (boundary law), but **the game
suite can measure itself**.

P1's charter: build the smallest evidence artifact that measures the
split as shipped — each §1.17 axis → its engine source and its
on-screen surface, or its recorded absence — then place a **dated
correction note beside §1.17**, never rewriting the founding text.

## WHAT

`build_companion_axis_split_report()` in `game/evidence.py` (the
game-side evidence pattern), + 16 pins in
`game/tests/test_companion_axis_split.py`. The rule and prediction were
pre-registered in the module before the run:

- **The measurement is a live client session**, not a reading of any
  document: a real `CompanionSession` from the committed seed and
  covenant, advanced one autonomous tick; the on-screen half read from
  `snapshot()` — the read model every frame draws from; the
  engine-source half from the live lifecycle state through the package
  boundary. **On-screen is operationalized** as: presented by the
  snapshot as a *named readout* (a needs entry, the age/mood readouts,
  or the health readout) — data that merely rides the snapshot for
  other consumers (log, thread signals, ui_hints) is not a readout.
- **The instrument gate** (Phase N's law, O4's hard-gate shape): the
  eight visible-axis engine dispositions must reproduce the committed
  M5 survey (`companion_state_survey_stage0.json`) on **exactly seven
  of eight**, with `health` differing only as
  `absent → chosen_definition_dr0054` — the decision DR 0054 took
  *after* that survey. Any other mismatch raises instead of writing an
  artifact. Measured absences are additionally asserted live before any
  disposition is recorded (`happiness`/`cleanliness`/`health` not in
  the state; no `clean` action) — if a future engine grows one of
  those, the harness refuses to produce a stale correction.

## FINDINGS

**1. The split as shipped: 6 / 2 / 2.** Six of the eight documented
VISIBLE axes are on the shipped client's read model (hunger, energy,
bond, age, mood, health); the two that are not — **happiness** and
**cleanliness** — are absent **upstream of display** (a missing
DEFINITION and a missing MECHANIC, DR 0048), not display gaps. Two
documented HIDDEN axes are surfaced under accurate names: `stress` as
"stress" and `grid stability` as "body stability". The other six hidden
axes are not surfaced anywhere on the read model.

**2. No axis without an engine source is shown — measured, not
asserted.** A pin walks every axis: `engine_source == absent` implies
`on_screen.shown == False`. DR 0021's first law holds on the shipped
surface.

**3. `health` reads as what it is.** On-screen with its binding word,
and `labelled_chosen: true` — the surface itself says the definition is
chosen (DR 0054), not documented.

**4. M5's remainder 2 is CLOSED.** The game's own suite now pins that
`snapshot()` carries `age_ticks` and `mood` (and that the two surfaced
hidden axes carry their shipped labels, and that no invented axis name
appears anywhere in the snapshot). The file-reference citation is now a
measurement.

**5. The instrument reproduced the committed survey 7/8**, with
`health`'s difference explained by DR 0054/0055 — a decision, not
drift. **The prediction (recorded first) was confirmed** on all three
counts: visible-shown set, hidden-surfaced set, and the 7/8 match.

**6. The dated correction is placed.** §1.17 now carries a
2026-08-08 note quoting this artifact — three clauses (the upstream
gaps; the chosen health definition; the two honestly-surfaced hidden
axes) — with the founding text untouched above it.

## HONEST REMAINDERS

1. **The six unsurfaced hidden axes' engine sources remain
   unsurveyed** — M5's remainder 4 stands, carried in the artifact's
   blocked states, and this artifact measures only the shipped surface.
2. **On-screen is measured at the read model** (`snapshot()`), not at
   the pixel level; rendering from the snapshot is exercised by the
   client's own suites.
3. **One session, one tick.** The split (which axes appear) is
   structural and does not vary over a life; values do, and no claim
   here is about values.

## Verification

RED (the builder does not exist):

```text
PS> uv run python -B -m unittest discover -s game/tests -p "test_companion_axis_split.py"
ImportError: Failed to import test module: test_companion_axis_split
ImportError: cannot import name 'AXIS_SPLIT_ARTIFACT_ID' from 'evidence'
FAILED (errors=1)
```

GREEN (the 16 pins, then the whole game suite):

```text
PS> uv run python -B -m unittest discover -s game/tests -p "test_companion_axis_split.py"
Ran 16 tests in 0.024s
OK

PS> uv run python -B -m unittest discover -s game/tests -p "test_*.py"
Ran 216 tests in 14.836s
OK
```

Artifact (the documented invocation and its output):

```text
PS> uv run python -B -c "... build_companion_axis_split_report / write ..."
{
 "visible_on_screen": 6,
 "visible_absent_upstream": 2,
 "hidden_surfaced": 2
}
{
 "axis": "health",
 "committed": "absent",
 "measured": "chosen_definition_dr0054",
 "explained_by": "DR 0054 (the definition CHOSEN after the committed survey) and DR 0055/O2 (the readout shipped) — a decision, not instrument drift"
}
"prediction_confirmed"
wrote data/game_client/companion_axis_split_stage0.json
```

## Sources

- `game/evidence.py` (`build_companion_axis_split_report`) + `game/tests/test_companion_axis_split.py` (16 pins)
- `data/game_client/companion_axis_split_stage0.json` (the artifact)
- `docs/project-research/validity-research.md` §1.17 (now carrying the dated correction note)
- `data/architecture/companion_state_survey_stage0.json` (the committed M5 survey the instrument reproduces)
- `research/experiment_reports/2026-07-27-companion-state-survey.md` (M5 — remainders 2 and 4)
- `research/decision_records/0048-visible-companion-state-axes.md`, `0054-health-definition-danger-margin.md`, `0055-health-readout-binding-axis.md`, `0021-game-loop.md`
- `game/src/mecha_game/session.py` (`snapshot`, `NEED_DISPLAY`) · `game/src/mecha_game/health.py`
- `sunsetted/TODO.md` (cycle 26 P1)
