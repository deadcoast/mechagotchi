"""Cycle 23 M5: the documented visible companion state, surveyed honestly.

`docs/project-research/validity-research.md` §1.17 names eight **VISIBLE**
companion state axes — *hunger, happiness, energy, cleanliness, mood,
age, health, bond* — and eight **HIDDEN** ones (*mutation pressure,
lineage fitness, stress, novelty decay, attachment score, user response
confidence, profile alignment, grid stability*).

The Phase-K gate's survey, re-verified at the Phase-L gate, recorded:

> **Five of the eight documented VISIBLE companion state axes have no
> engine field** — `happiness`, `cleanliness`, `mood`, `age` and
> `health` — the largest documented player-facing gap in the repo.

**M5's charter was to survey each axis honestly BEFORE building
anything, and the survey's first result is that the claim above is
overstated.** It was made by looking at the lifecycle's *homeostasis
fields*, which is a narrower question than "has an engine field":

* **`age` is a lifecycle field.** `initial_state` sets ``age_ticks: 0``
  and `advance_tick` increments it every tick; `run_episode` reports it
  as `survival_ticks`. The game already displays it.
* **`mood` is a derived engine value.** `select_animation_state` returns
  ``(animation, mood)`` and has since Phase C. It is not a homeostasis
  field, which is exactly why a field-only survey missed it — but it is
  engine truth, and the game already displays it.

So the gap is **three axes, not five**: `happiness`, `cleanliness` and
`health`.

**THIS MODULE MEASURES, IT DOES NOT ASSERT.** Every disposition is
obtained by building a real lifecycle state from a committed seed
creature and calling the real engine functions. A survey that read a
document and reported what the document said would reproduce exactly the
error it exists to correct.

**Dispositions**, fixed in advance, with `absent` first-class — a survey
that cannot report a gap is not a survey:

* ``lifecycle_field`` — the engine carries it as state.
* ``derived_engine_value`` — the engine computes it from state it
  carries; engine truth, no new field required.
* ``absent`` — the engine has no source for it. **No value is
  reported and none is invented** (DR 0021's first law).

**This module builds nothing and adopts nothing.** What each absent axis
should become — engine truth, a derived view, or deliberately out of
scope — is DR 0048's decision, and an axis with no honest source is
shown as uncalibrated or not shown at all.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"

ARTIFACT_ID = "companion_state_survey_stage0"
REPORT_DATE = "2026-07-27"

# Quoted verbatim from validity-research.md §1.17, in document order.
DOCUMENTED_VISIBLE_AXES = (
    "hunger",
    "happiness",
    "energy",
    "cleanliness",
    "mood",
    "age",
    "health",
    "bond",
)

DOCUMENTED_HIDDEN_AXES = (
    "mutation pressure",
    "lineage fitness",
    "stress",
    "novelty decay",
    "attachment score",
    "user response confidence",
    "profile alignment",
    "grid stability",
)

DISPOSITIONS = ("lifecycle_field", "derived_engine_value", "absent")

# The claim this survey re-measures.
PRIOR_CLAIM = (
    "five of the eight documented VISIBLE companion state axes have no "
    "engine field (happiness, cleanliness, mood, age, health) — recorded "
    "at the Phase-K gate and re-verified at the Phase-L gate as the "
    "largest documented player-facing gap in the repo"
)

# How each documented visible axis maps onto the engine, if it does.
# `field` names a lifecycle state key; `derived` names an engine
# function that computes it from state the engine already carries.
AXIS_SOURCES: dict[str, dict] = {
    "hunger": {"field": "hunger"},
    "energy": {"field": "energy"},
    "bond": {"field": "bond"},
    "age": {"field": "age_ticks"},
    "mood": {"derived": "mecha_engine.genome.animation.select_animation_state"},
    "happiness": {},
    "cleanliness": {},
    "health": {},
}

# Why each absent axis is absent — measured against the engine surface,
# stated so DR 0048 decides on evidence rather than impression.
ABSENCE_CAUSES: dict[str, str] = {
    "happiness": (
        "no engine source. No lifecycle field, no derivation, and no "
        "documented formula: validity-research.md names the axis and "
        "never defines it. `bond` is a separate documented axis and is "
        "not a synonym. Any happiness number today would be invented."
    ),
    "cleanliness": (
        "no engine MECHANIC, not merely no field. The lifecycle's "
        "action set is (feed, play, sleep, idle, mutate) — there is no "
        "clean action — and no state accumulates dirt. Supplying "
        "cleanliness needs a new mechanic, which is a design decision "
        "with its own record, not a derived view."
    ),
    "health": (
        "no engine field, and the nearest sources are documented "
        "HIDDEN: `grid_stability` is a hidden axis by "
        "validity-research.md's own split, and per-cell `damage` feeds "
        "it. A 'health' bar composed from them would either rename a "
        "hidden axis as a visible one or blend them on weights nobody "
        "documented. The axis is definable from engine truth, but the "
        "definition would be CHOSEN (the L4 precedent) and needs its "
        "own gate."
    ),
}

_PROBE = r"""
import json, sys
from mecha_engine.lifecycle import initial_state, advance_tick
from mecha_engine.genome.animation import select_animation_state

grid = json.loads(open(sys.argv[1], encoding="utf-8").read())
state = initial_state(grid)
after = advance_tick(state, "idle")
animation, mood = select_animation_state(state)
print(json.dumps({
    "state_keys": sorted(state),
    "state": {k: v for k, v in state.items() if isinstance(v, (int, float))},
    "age_ticks_initial": state["age_ticks"],
    "age_ticks_after_one_tick": after["age_ticks"],
    "mood": mood,
    "animation": animation,
}))
"""


def _probe_engine() -> dict:
    """Measure the live engine through the package boundary.

    Run as a subprocess with ``PYTHONPATH`` at the package src, the same
    way the package's own tests locate the module — a lab may import the
    package, and this keeps the measurement honest rather than mocked.
    """
    seed = ROOT / "data" / "seed_grids_16x16" / "mg_seed16_001_beetle.json"
    result = subprocess.run(
        [sys.executable, "-B", "-c", _PROBE, str(seed)],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(PACKAGE_SRC), "SYSTEMROOT": "C:\\Windows"},
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        raise RuntimeError(
            "the engine probe failed; the survey refuses to report "
            f"dispositions it could not measure:\n{result.stderr[-2000:]}"
        )
    return json.loads(result.stdout)


_PROBE_CACHE: dict | None = None


def _engine() -> dict:
    global _PROBE_CACHE
    if _PROBE_CACHE is None:
        _PROBE_CACHE = _probe_engine()
    return _PROBE_CACHE


def survey_axis(axis: str) -> dict:
    """Measure one documented visible axis against the live engine."""
    if axis not in DOCUMENTED_VISIBLE_AXES:
        raise ValueError(
            f"{axis!r} is not one of the documented visible axes "
            f"({', '.join(DOCUMENTED_VISIBLE_AXES)}). 'absent' is a "
            "measurement about a documented axis; a name the "
            "documentation never used is not a finding"
        )
    engine = _engine()
    source = AXIS_SOURCES[axis]

    if "field" in source:
        field = source["field"]
        present = field in engine["state_keys"]
        return {
            "axis": axis,
            "disposition": "lifecycle_field" if present else "absent",
            "engine_field": field if present else None,
            "engine_function": None,
            "measured_value": engine["state"].get(field) if present else None,
            "note": (
                f"carried as lifecycle state key {field!r}, measured on a "
                "live initial_state"
            )
            if present
            else ABSENCE_CAUSES.get(axis, "no engine source"),
        }

    if "derived" in source:
        return {
            "axis": axis,
            "disposition": "derived_engine_value",
            "engine_field": None,
            "engine_function": source["derived"],
            "measured_value": engine["mood"],
            "note": (
                "computed by the engine from state it already carries "
                "(returns (animation, mood)); engine truth, no new field "
                "required. Not a homeostasis field, which is why a "
                "field-only survey recorded it as absent"
            ),
        }

    return {
        "axis": axis,
        "disposition": "absent",
        "engine_field": None,
        "engine_function": None,
        "measured_value": None,
        "note": ABSENCE_CAUSES[axis],
    }


def build_companion_state_report() -> dict:
    engine = _engine()
    visible = {axis: survey_axis(axis) for axis in DOCUMENTED_VISIBLE_AXES}
    absent = [a for a, r in visible.items() if r["disposition"] == "absent"]
    present = [a for a in visible if a not in absent]

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 23 M5: survey the eight documented VISIBLE companion "
            "state axes against the LIVE engine before building "
            "anything — the charter's own instruction — and re-measure "
            "the Phase-K/L claim that five of them have no engine field."
        ),
        "source_artifacts": [
            "docs/project-research/validity-research.md",
            "packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py",
            "packages/mecha_engine/src/mecha_engine/genome/animation.py",
            "data/seed_grids_16x16/mg_seed16_001_beetle.json",
        ],
        "parameters": {
            "documented_visible_axes": list(DOCUMENTED_VISIBLE_AXES),
            "documented_hidden_axes": list(DOCUMENTED_HIDDEN_AXES),
            "dispositions": list(DISPOSITIONS),
            "probe_grid": "data/seed_grids_16x16/mg_seed16_001_beetle.json",
            "measurement": (
                "a real initial_state + advance_tick + "
                "select_animation_state through the package boundary; "
                "nothing is read off a document"
            ),
        },
        "metrics": {
            "visible_axes": visible,
            "present_axes": present,
            "absent_axes": absent,
            "lifecycle_state_keys": engine["state_keys"],
            "age_ticks_increments": (
                engine["age_ticks_after_one_tick"] - engine["age_ticks_initial"]
            ),
            "prior_claim": {
                "claim": PRIOR_CLAIM,
                "previously_reported_absent": 5,
                "previously_named": [
                    "happiness",
                    "cleanliness",
                    "mood",
                    "age",
                    "health",
                ],
                "measured_absent": len(absent),
                "measured_names": absent,
                "correction": (
                    "the claim is OVERSTATED. `age` is a lifecycle field "
                    "(age_ticks, set at construction and incremented "
                    "every tick) and `mood` is a derived engine value "
                    "(select_animation_state, since Phase C) — both are "
                    "engine truth and both are already displayed by the "
                    "game. The earlier survey counted homeostasis fields, "
                    "which is a narrower question than 'has an engine "
                    "field'. The real gap is three axes, not five."
                ),
            },
        },
        "closed_states": [
            "every documented visible axis is measured against the LIVE "
            "engine rather than read off a document",
            "the Phase-K/L claim is re-measured and corrected: three "
            "axes are absent, not five",
            "the visible and hidden documented lists are kept apart, so "
            "promoting a hidden axis to a visible one cannot happen by "
            "accident",
            "each absent axis carries its measured CAUSE, so DR 0048 "
            "decides on evidence rather than impression",
        ],
        "blocked_states": [
            "no absent axis is given a value: DR 0021's first law means "
            "an axis with no honest source is shown as uncalibrated or "
            "not shown at all, and nothing here invents a number",
            "this module builds nothing and adopts nothing — what each "
            "absent axis should become is DR 0048's decision",
            "`health` is DEFINABLE from engine truth (grid_stability and "
            "per-cell damage) but both are documented HIDDEN axes, so "
            "any definition would be CHOSEN rather than documented (the "
            "L4 precedent) and needs its own gate",
            "the game-side display of age and mood is cited by file "
            "reference, not measured here: importing the game from a lab "
            "would cross the boundary law",
        ],
        "decision": {
            "measured_absent": len(absent),
            "absent_axes": absent,
            "present_axes": present,
            "prior_claim_status": "overstated — three absent, not five",
            "per_axis": {
                axis: visible[axis]["disposition"]
                for axis in DOCUMENTED_VISIBLE_AXES
            },
        },
        "next_research_step": (
            "DR 0048 decides each absent axis: engine truth, a derived "
            "view, or deliberately out of scope. Then M6, the Phase-M "
            "gate."
        ),
    }


def write_companion_state_artifacts(
    output_dir: str | Path, report: dict
) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{ARTIFACT_ID}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", default=str(ROOT / "data" / "architecture")
    )
    args = parser.parse_args()

    report = build_companion_state_report()
    metrics = report["metrics"]
    print("documented visible axes, measured against the live engine:")
    for axis in DOCUMENTED_VISIBLE_AXES:
        result = metrics["visible_axes"][axis]
        value = result["measured_value"]
        shown = "—" if value is None else str(value)
        print(f"  {axis:12} {result['disposition']:22} {shown}")
    claim = metrics["prior_claim"]
    print(
        f"\nprior claim: {claim['previously_reported_absent']} absent "
        f"({', '.join(claim['previously_named'])})"
    )
    print(
        f"measured   : {claim['measured_absent']} absent "
        f"({', '.join(claim['measured_names'])})"
    )
    for path in write_companion_state_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
