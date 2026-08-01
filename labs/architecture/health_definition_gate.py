"""Cycle 24 N5: `health` — the CHOSEN definition, gated. (GAME track.)

`validity-research.md` §1.17 names `health` a **VISIBLE** companion
state axis. M5 measured that the engine has no `health` field, and
DR 0048 **withheld** it rather than refusing it, naming the gate it
needed:

> *"a record that declares its definition **CHOSEN** (exactly as L4 did
> for `animation_density`), states which hidden axes it reads, and gates
> it — including on whether a player-facing 'health' that is really
> grid-stability is **honest labelling or a euphemism**."*

This module is that gate, and the euphemism question is a **real gate
with a measured answer**, not a paragraph of judgement.

TWO CANDIDATES, because DR 0048's named one may not be the best one
=================================================================

* **A — `grid_stability`.** DR 0048's candidate: surface the documented
  HIDDEN axis directly under the visible name. It is engine truth, it
  moves under the lifecycle, and it is one of the engine's four lethal
  conditions (`grid_collapse` at <= 0.05).
* **B — `danger_margin`.** *How close am I to trouble, on my worst
  axis.* The minimum normalised safety margin across the engine's
  `DANGER_THRESHOLDS`. DR 0048 rejected a composite because *"any
  composite needs weights nobody documented"* — **a minimum has no
  weights at all.** Its only constants are the engine's own published
  thresholds, so it invents nothing.

  **This candidate was renamed mid-study, and the reason is the study's
  own subject.** It was drafted as `lethal_margin`, which overclaims:
  `DANGER_THRESHOLDS` carries **five** axes and one of them, `bond`, is
  **not** a lethal condition — only `hunger`, `energy`, `stress` and
  `grid_stability` appear in `_life_status`. A gate whose entire purpose
  is asking whether a label is honest cannot ship a definition whose own
  name overstates what it measures. Renamed to `danger_margin`, which is
  what it is.

**Both definitions are CHOSEN and both say so.** Neither is documented;
§1.17 names the axis and never defines it. That is stated first, as L4
did, rather than discovered afterwards.

THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN
===============================================

* **G1 — the definition is DECLARED CHOSEN.** It must name the
  documented-HIDDEN axes it reads. Structural: a definition that will
  not say what it reads cannot be audited.
* **G2 — the KEEPER can move it.** A bar labelled for the player is
  judged against **what the player can do**, which in this game is
  `feed` and `play` — not what the companion does to itself. The bar is
  **MEASURED, never a constant**: the smallest response any *existing
  visible* axis (`hunger`, `energy`, `bond`) shows to those same
  actions. A candidate flatter than the incumbent visible axes is not
  behaving like a visible axis.
* **G3 — it is coupled to survival.** Deaths and survivors must
  separate on it. A "health" bar that reads the same for a creature
  about to die and one that is fine is not measuring health.
* **G4 — THE LABEL TEST, and the one DR 0048 actually asked for.** Put
  the creature in distress, have the keeper relieve it, and see whether
  the bar rises. **A bar that does not move when the keeper relieves the
  distress is a euphemism, whatever it is called** — and failing this
  gate is `refuse_as_euphemism`, a different and harsher verdict than
  the `withhold` a structural failure earns.

**Refusal is first-class and reachable for every candidate** (pinned).
DR 0048 said as much; a gate that could only adopt would have made that
a lie.

**A PREDICTION IS RECORDED BEFORE THE RUN** (DR 0045's precedent), so it
can be wrong on the record — see ``PRE_RUN_PREDICTION``.

This module builds no UI. It decides whether a definition may carry the
name; putting a bar on the player's screen is the consumer's change and
needs this record to exist first.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"

ARTIFACT_ID = "health_definition_gate_stage0"
REPORT_DATE = "2026-07-28"

# What the PLAYER can do. The euphemism question turns on this: a
# player-facing bar is judged against the player's own verbs. Measured
# from the game's keeper model (`labs/micro_threads/ablation_gates.py`
# `keeper_respond`, whose five documented keepers answer a beg with
# `feed` or `play`), not assumed.
KEEPER_ACTIONS = ("feed", "play")

# The companion's own verbs, recorded so the artifact shows what was
# deliberately NOT counted as keeper care.
COMPANION_ACTIONS = ("sleep", "idle", "mutate")

# The engine's existing VISIBLE axes, which set G2's measured floor.
INCUMBENT_VISIBLE_AXES = ("hunger", "energy", "bond")

CANDIDATES: dict[str, dict] = {
    "grid_stability": {
        "label": "DR 0048's named candidate: the hidden axis, surfaced",
        "hidden_axes_read": ["grid_stability"],
        "chosen": True,
        "rationale": (
            "engine truth, moves under the lifecycle, and one of the "
            "four lethal conditions (grid_collapse at <= 0.05)"
        ),
    },
    "danger_margin": {
        "label": "how close am I to trouble, on my worst axis",
        "hidden_axes_read": ["stress", "grid_stability"],
        "chosen": True,
        "rationale": (
            "the MINIMUM normalised safety margin across the engine's "
            "own DANGER_THRESHOLDS. DR 0048 rejected a composite "
            "because 'any composite needs weights nobody documented' — "
            "a minimum has no weights at all, only the engine's "
            "published thresholds"
        ),
        "renamed_from": "lethal_margin",
        "rename_reason": (
            "DANGER_THRESHOLDS carries five axes and one of them, "
            "`bond`, is NOT a lethal condition — only hunger, energy, "
            "stress and grid_stability appear in _life_status. A gate "
            "asking whether a label is honest may not ship a definition "
            "whose own name overstates what it measures"
        ),
    },
}

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 24 N5), refusal first-class and reachable "
    "for every candidate. Both definitions are declared CHOSEN up front "
    "(the L4 precedent): validity-research.md names `health` and never "
    "defines it. G1 — the definition must DECLARE which documented "
    "HIDDEN axes it reads; a definition that will not say what it reads "
    "cannot be audited. G2 — the KEEPER must be able to move it, judged "
    "against what the PLAYER can do (feed, play) rather than what the "
    "companion does to itself, with the bar MEASURED as the smallest "
    "response any existing VISIBLE axis shows to those same actions, "
    "never a constant. G3 — it must be coupled to survival: deaths and "
    "survivors must separate on it. G4 — THE LABEL TEST, the question "
    "DR 0048 actually asked: put the creature in distress, have the "
    "keeper relieve it, and measure whether the bar rises. A bar that "
    "does not move when the keeper relieves the distress is a "
    "EUPHEMISM whatever it is called, and earns "
    "'refuse_as_euphemism' — a harsher verdict than the 'withhold' a "
    "structural failure earns, because the two are different "
    "accusations and must not be conflated. This module builds no UI: "
    "it decides whether a definition may carry the name."
)

PRE_RUN_PREDICTION = (
    "Written before the run (DR 0045's precedent, so it can be wrong on "
    "the record): `grid_stability` is expected to FAIL G2 and G4 and be "
    "refused as a euphemism, because the engine's ACTION_EFFECTS move it "
    "by exactly 0.0 under both `feed` and `play` — the only two verbs a "
    "keeper has — while it falls 0.055 under `mutate`, an action a "
    "player would read as growth rather than harm. `danger_margin` is "
    "expected to pass, because hunger and energy are lethal axes that "
    "feed and sleep move. If the measurement disagrees, the measurement "
    "wins."
)

PROBE_TIMEOUT_S = 240

_PROBE = r"""
import json, sys
from mecha_engine.lifecycle import ACTIONS, advance_tick, initial_state
# DANGER_THRESHOLDS is a PUBLIC name in a PUBLIC module but is not
# re-exported by the package's __all__, so it is imported from the
# submodule rather than reached for through a private path. Recorded in
# the artifact's blocked states: a definition that depends on it is
# depending on a surface the package has not promised.
from mecha_engine.lifecycle.simulate import DANGER_THRESHOLDS

grid = json.loads(open(sys.argv[1], encoding="utf-8").read())
ticks = int(sys.argv[2])
lifecycles = int(sys.argv[3])
AXES = ["hunger", "energy", "stress", "bond", "grid_stability"]


def snap(state):
    return {axis: round(float(state[axis]), 6) for axis in AXES}


base = initial_state(grid, None)
out = {
    "danger_thresholds": dict(DANGER_THRESHOLDS),
    "actions": list(ACTIONS),
    "initial": snap(base),
}

# 1) One tick of each action from the SAME state: what does each verb do?
per_action = {}
for action in ACTIONS:
    after = advance_tick(base, action)
    per_action[action] = {
        axis: round(after[axis] - base[axis], 6) for axis in AXES
    }
out["per_action_delta"] = per_action

# 2) Distress, then relief. Drive the creature into hunger distress by
#    idling, then have the KEEPER feed it, and record what moved.
distress = base
for _ in range(ticks):
    if distress["hunger"] >= DANGER_THRESHOLDS["hunger"]:
        break
    distress = advance_tick(distress, "idle")
relieved = advance_tick(distress, "feed")
out["distress"] = {
    "reached_hunger_danger": bool(
        distress["hunger"] >= DANGER_THRESHOLDS["hunger"]
    ),
    "before": snap(distress),
    "after_keeper_feed": snap(relieved),
    "delta": {
        axis: round(relieved[axis] - distress[axis], 6) for axis in AXES
    },
}

# 3) Real lifecycles: a NEGLECT arm (idle only) and a CARE arm (the
#    keeper feeding and playing), so deaths and survivors both occur.
runs = []
for index in range(lifecycles):
    for arm, cycle in (("neglect", ["idle"]), ("care", ["feed", "play", "sleep"])):
        state = initial_state(grid, None)
        step = 0
        while state["alive"] and step < ticks:
            state = advance_tick(state, cycle[step % len(cycle)])
            step += 1
        runs.append(
            {
                "arm": arm,
                "index": index,
                "alive": bool(state["alive"]),
                "death_cause": state["death_cause"],
                "ticks": step,
                "final": snap(state),
            }
        )
out["lifecycles"] = runs
print(json.dumps(out))
"""


def _probe_env() -> dict:
    """Inherit the environment and EXTEND ``PYTHONPATH``, never replace it.

    The repo's probe pattern (M5's, and the scaffold gate's before it):
    replacing the environment drops ``PATH`` and any virtualenv vars, so
    the probe fails for reasons unrelated to the engine it measures.
    """
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(PACKAGE_SRC) + (
        os.pathsep + existing if existing else ""
    )
    return env


def probe_engine(*, ticks: int, lifecycles: int) -> dict:
    """Measure the live engine through the package boundary."""
    seed = ROOT / "data" / "seed_grids_16x16" / "mg_seed16_001_beetle.json"
    try:
        result = subprocess.run(
            [sys.executable, "-B", "-c", _PROBE, str(seed), str(ticks), str(lifecycles)],
            capture_output=True,
            text=True,
            env=_probe_env(),
            cwd=str(ROOT),
            timeout=PROBE_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(
            f"the engine probe did not return within {PROBE_TIMEOUT_S}s; "
            "this gate refuses to judge a definition it could not measure"
        ) from error
    if result.returncode != 0:
        raise RuntimeError(
            "the engine probe failed; this gate refuses to judge a "
            f"definition it could not measure:\n{result.stderr}"
        )
    return json.loads(result.stdout)


def danger_margin(snapshot: dict, thresholds: dict) -> float:
    """Candidate B: the worst normalised safety margin. No weights.

    Higher is safer. Each axis contributes its distance to the engine's
    own danger threshold, normalised by the room available on that side,
    and the MINIMUM decides — a creature one step from starvation is not
    healthy because its grid is intact.
    """
    margins = []
    for axis, threshold in thresholds.items():
        value = float(snapshot[axis])
        if axis in ("hunger", "stress"):
            # Rising is dangerous.
            room = threshold if threshold > 0 else 1.0
            margins.append((threshold - value) / room)
        else:
            # Falling is dangerous (energy, grid_stability).
            room = 1.0 - threshold if threshold < 1.0 else 1.0
            margins.append((value - threshold) / room)
    return round(max(0.0, min(1.0, min(margins))), 6)


def candidate_value(name: str, snapshot: dict, thresholds: dict) -> float:
    if name == "grid_stability":
        return round(float(snapshot["grid_stability"]), 6)
    if name == "danger_margin":
        return danger_margin(snapshot, thresholds)
    raise ValueError(f"unknown health candidate: {name}")


def judge_candidate(
    *,
    candidate: str,
    hidden_axes_read: list,
    keeper_action_response: dict,
    incumbent_response_floor: float,
    distress_relief: float,
    separates_deaths_from_survivors: bool,
) -> dict:
    """Apply the four pre-registered gates. Every verdict first-class."""
    if incumbent_response_floor < 0:
        raise ValueError(
            "the incumbent response floor is a measured magnitude and "
            f"cannot be negative: {incumbent_response_floor!r}"
        )
    declared = bool(hidden_axes_read)
    best_keeper_response = max(
        (abs(value) for value in keeper_action_response.values()), default=0.0
    )
    keeper_responsive = best_keeper_response >= incumbent_response_floor
    honest_label = distress_relief > 0.0

    failed = []
    if not declared:
        failed.append("G1_definition_declared")
    if not keeper_responsive:
        failed.append("G2_keeper_responsive")
    if not separates_deaths_from_survivors:
        failed.append("G3_survival_coupled")
    if not honest_label:
        failed.append("G4_honest_label")

    if not failed:
        verdict = "adopt"
    elif "G4_honest_label" in failed:
        # The harsher verdict, and a different accusation: the engine
        # has a number, and the name would misdescribe it.
        verdict = "refuse_as_euphemism"
    else:
        verdict = "withhold"

    return {
        "candidate": candidate,
        "verdict": verdict,
        "failed_gates": failed,
        "chosen_definition": True,
        "hidden_axes_read": list(hidden_axes_read),
        "keeper_action_response": dict(keeper_action_response),
        "best_keeper_response": round(best_keeper_response, 6),
        "incumbent_response_floor": round(incumbent_response_floor, 6),
        "distress_relief": round(distress_relief, 6),
        "separates_deaths_from_survivors": separates_deaths_from_survivors,
    }


def build_health_definition_report(*, ticks: int = 200, lifecycles: int = 3) -> dict:
    engine = probe_engine(ticks=ticks, lifecycles=lifecycles)
    thresholds = engine["danger_thresholds"]
    per_action = engine["per_action_delta"]

    # G2's floor, MEASURED: the smallest response any existing VISIBLE
    # axis shows to the keeper's own verbs.
    incumbent_responses = {
        axis: max(abs(per_action[action][axis]) for action in KEEPER_ACTIONS)
        for axis in INCUMBENT_VISIBLE_AXES
    }
    incumbent_floor = min(incumbent_responses.values())

    distress = engine["distress"]
    survivors = [run for run in engine["lifecycles"] if run["alive"]]
    deaths = [run for run in engine["lifecycles"] if not run["alive"]]

    judged: dict[str, dict] = {}
    per_candidate_measures: dict[str, dict] = {}
    for name in CANDIDATES:
        keeper_response = {}
        for action in KEEPER_ACTIONS:
            before = engine["initial"]
            after = {
                axis: before[axis] + per_action[action][axis] for axis in before
            }
            keeper_response[action] = round(
                candidate_value(name, after, thresholds)
                - candidate_value(name, before, thresholds),
                6,
            )
        relief = round(
            candidate_value(name, distress["after_keeper_feed"], thresholds)
            - candidate_value(name, distress["before"], thresholds),
            6,
        )
        survivor_values = [
            candidate_value(name, run["final"], thresholds) for run in survivors
        ]
        death_values = [
            candidate_value(name, run["final"], thresholds) for run in deaths
        ]
        separates = bool(
            survivor_values
            and death_values
            and min(survivor_values) > max(death_values)
        )
        per_candidate_measures[name] = {
            "keeper_response": keeper_response,
            "distress_relief": relief,
            "survivor_values": survivor_values,
            "death_values": death_values,
            "separates_deaths_from_survivors": separates,
        }
        judged[name] = judge_candidate(
            candidate=name,
            hidden_axes_read=CANDIDATES[name]["hidden_axes_read"],
            keeper_action_response=keeper_response,
            incumbent_response_floor=incumbent_floor,
            distress_relief=relief,
            separates_deaths_from_survivors=separates,
        )

    adopted = [name for name, entry in judged.items() if entry["verdict"] == "adopt"]

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 24 N5: gate a CHOSEN definition of the documented "
            "VISIBLE axis `health`, which DR 0048 withheld — including "
            "on the question it named: whether a player-facing 'health' "
            "that is really grid-stability is honest labelling or a "
            "euphemism. Two candidates, four gates, refusal first-class."
        ),
        "source_artifacts": [
            "data/architecture/companion_state_survey_stage0.json",
            "data/seed_grids_16x16/mg_seed16_001_beetle.json",
        ],
        "parameters": {
            "ticks": ticks,
            "lifecycles": lifecycles,
            "keeper_actions": list(KEEPER_ACTIONS),
            "companion_actions": list(COMPANION_ACTIONS),
            "incumbent_visible_axes": list(INCUMBENT_VISIBLE_AXES),
            "candidates": {
                name: {
                    key: value
                    for key, value in spec.items()
                    if key != "hidden_axes_read"
                }
                | {"hidden_axes_read": list(spec["hidden_axes_read"])}
                for name, spec in CANDIDATES.items()
            },
            "seed_grid": "data/seed_grids_16x16/mg_seed16_001_beetle.json",
        },
        "metrics": {
            "engine": engine,
            "incumbent_keeper_responses": incumbent_responses,
            "incumbent_response_floor": round(incumbent_floor, 6),
            "candidates": per_candidate_measures,
        },
        "closed_states": [
            "both definitions are declared CHOSEN up front (the L4 "
            "precedent), because validity-research.md names `health` "
            "and never defines it",
            "the euphemism question DR 0048 named is a REAL GATE with a "
            "measured answer, not a paragraph of judgement",
            "G2's bar is MEASURED as the smallest response an existing "
            "VISIBLE axis shows to the keeper's own verbs, never a "
            "constant",
            "the keeper's verbs are measured from the game's keeper "
            "model rather than assumed, because a player-facing bar is "
            "judged against what the PLAYER can do",
            "refusal is reachable for every candidate (pinned), as "
            "DR 0048 required",
            "a prediction was recorded BEFORE the run so it could be "
            "wrong on the record (DR 0045's precedent)",
        ],
        "blocked_states": [
            "this module builds no UI: it decides whether a definition "
            "may carry the name, and putting a bar on the player's "
            "screen is the consumer's change",
            "surfacing ANY of these promotes a documented HIDDEN axis "
            "to a VISIBLE one — a documentation change to "
            "validity-research.md §1.17, not an engine one, and it is "
            "not made here",
            "one seed creature and one SLIP-free lifecycle: the "
            "measurements are of the engine's action model, which is "
            "profile-independent, but a profile with different "
            "behaviour weights would move the magnitudes",
            "`happiness` and `cleanliness` stay OUT OF SCOPE (DR 0048): "
            "one needs a definition, the other a mechanic",
            "`danger_margin` reads DANGER_THRESHOLDS, which is a PUBLIC "
            "name in a PUBLIC module but is NOT in the package's "
            "__all__ — so a definition built on it depends on a surface "
            "the package has not promised. Adopting it would mean "
            "promoting that constant to the public API, which is a "
            "package change with its own spec update and gate",
        ],
        "decision": {
            "candidates": judged,
            "adopted": adopted,
            "rule": PRE_REGISTERED_RULE,
            "pre_run_prediction": PRE_RUN_PREDICTION,
        },
        "next_research_step": (
            "N6: the Phase-N gate — then archive cycle 24 and plan "
            "cycle 25 from the documentation."
        ),
    }


def write_health_definition_artifacts(
    output_dir: str | Path, report: dict
) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{ARTIFACT_ID}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser(description="Cycle 24 N5: the health definition gate.")
    parser.add_argument("--output-dir", default=str(ROOT / "data" / "architecture"))
    parser.add_argument("--ticks", type=int, default=200)
    parser.add_argument("--lifecycles", type=int, default=3)
    args = parser.parse_args()

    report = build_health_definition_report(
        ticks=args.ticks, lifecycles=args.lifecycles
    )
    metrics = report["metrics"]
    print(f"keeper verbs: {list(KEEPER_ACTIONS)}")
    print(
        "incumbent visible-axis responses to those verbs: "
        f"{metrics['incumbent_keeper_responses']} "
        f"-> measured floor {metrics['incumbent_response_floor']}"
    )
    print()
    for name, entry in report["decision"]["candidates"].items():
        measures = metrics["candidates"][name]
        print(f"  {name}")
        print(
            f"    keeper response {measures['keeper_response']}  "
            f"distress relief {measures['distress_relief']}"
        )
        print(
            f"    survivors {measures['survivor_values']}  "
            f"deaths {measures['death_values']}  "
            f"separates {measures['separates_deaths_from_survivors']}"
        )
        print(
            f"    -> {entry['verdict'].upper()}"
            + (f"  (failed {','.join(entry['failed_gates'])})" if entry["failed_gates"] else "")
        )
    print(f"\nadopted: {report['decision']['adopted'] or 'NONE'}")
    for path in write_health_definition_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
