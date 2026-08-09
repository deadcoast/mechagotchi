"""Cycle 26 P2: `happiness` — a CHOSEN definition, gated. (ENGINE gate → GAME landing.)

`validity-research.md` §1.17 names `happiness` a **VISIBLE** companion
state axis and never defines it. M5 measured that the engine has no
source for it — *"no field, no derivation, and no documented formula"*
— and DR 0048 put it out of scope **pending a documented definition**.
This module is that gate, running the proven N5 → O2 pattern: every
candidate is declared CHOSEN up front, the rule and the prediction are
pre-registered before the run, and refusal is first-class and reachable
for every candidate.

THREE CANDIDATES, all read from what the engine already records
===============================================================

* **A — `bond_rename`.** The naive candidate every player would assume:
  `bond`, surfaced under the name "happiness". It is engine truth and
  it moves under the keeper's verbs — and it is **already on the
  player's screen under its own accurate name**. M5's own note: *"bond
  is a separate documented axis, not a synonym."*
* **B — `need_balance`.** The engine's OWN per-tick contentment
  statistic — ``1 − mean(|axis − target|)`` over the five homeostasis
  axes — computed and recorded by ``advance_tick`` in **every history
  entry since Stage 0** (``entry["balance"]``; ``run_episode`` reports
  its mean as ``need_balance``). Not an invented composite: the engine
  already writes this exact number every tick of every life.
* **C — `social_warmth`.** The mean of the engine's
  ``recent_interactions`` window — the last-5-tick trace of keeper
  care (``1`` when the executed action was ``feed`` or ``play``),
  carried in state and consumed by the switchboard since Stage 0.
  Happiness as *being tended lately*.

``curiosity`` is deliberately NOT a candidate: it is a SLIP-derived
constant the lifecycle never moves, so it would fail G2 by
construction — a strawman, not a candidate.

THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN
===============================================

G1–G4 are N5's gates verbatim in shape; G5 is the gate this axis needs
that `health` did not:

* **G1 — declared.** The definition names the engine fields it reads.
* **G2 — the KEEPER can move it**, judged against the player's own
  verbs (`feed`, `play`), with the bar MEASURED as the smallest
  response any existing visible axis shows to those verbs — and the
  recomputed floor must REPRODUCE the committed N5 floor exactly
  (instrument check; a mismatch raises).
* **G3 — care-coupled.** A cherished life and a neglected life must
  separate on it. A happiness bar that reads the same for both is not
  measuring happiness.
* **G4 — THE LABEL TEST.** Put the creature in distress, have the
  keeper relieve it, and measure whether the bar rises. A "happiness"
  that does not move when a starving companion is finally fed is a
  euphemism → ``refuse_as_euphemism``.
* **G5 — DISTINCT FROM WHAT IS SHOWN.** If the candidate's per-tick
  series over the probe lives is IDENTICAL to a readout already on the
  player's screen under another name (the five needs entries, or the
  health readout's `danger_margin`), it is one engine number wearing
  two visible names — the honest-labelling law violated in the
  opposite direction from a euphemism → ``refuse_as_duplicate``,
  which OUTRANKS the euphemism verdict because it is the sharper
  accusation: nothing about the number is wrong, only the second name.

**Selection among eligible candidates is pre-registered**: the LOWEST
final reading on the neglected corpse wins — N5's own refusal logic
(what the bar shows at death measures the label's honesty) made into
the selection statistic — with ties broken toward the definition that
reads fewer engine fields, then by name. At most one candidate is
adopted; the others that pass every gate are recorded
``eligible_not_selected``, which is neither a withholding nor a
refusal.

**A PREDICTION IS RECORDED BEFORE THE RUN** — see
``PRE_RUN_PREDICTION``. This module builds no UI; if a definition is
adopted, landing the readout is the same P2 slice's game-side change
(the O2 lesson: adopted-but-not-landed is the debt that quietly
becomes permanent).
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from statistics import mean

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from health_definition_gate import danger_margin  # noqa: E402

ARTIFACT_ID = "happiness_definition_gate_stage0"
REPORT_DATE = "2026-08-08"
COMMITTED_HEALTH_GATE = "data/architecture/health_definition_gate_stage0.json"

KEEPER_ACTIONS = ("feed", "play")
INCUMBENT_VISIBLE_AXES = ("hunger", "energy", "bond")

# The readouts the shipped client already shows (P1's measured split):
# the five needs entries plus the health readout. G5 compares per-tick
# series against every one of these.
SHOWN_READOUTS = ("hunger", "energy", "stress", "bond", "grid_stability", "danger_margin")

# Mirrors the engine's Stage 0 homeostasis targets (simulate.TARGETS).
# MIRRORED, never imported piecemeal into formulas: the balance mirror
# below is pinned tick-for-tick against the engine's own recorded
# entry["balance"] over every probe tick, so drift fails the run.
_TARGETS = {
    "hunger": 0.34,
    "energy": 0.68,
    "stress": 0.18,
    "bond": 0.72,
    "grid_stability": 0.92,
}

CANDIDATES: dict[str, dict] = {
    "bond_rename": {
        "label": "the naive candidate: bond, surfaced under the name happiness",
        "reads": ["bond"],
        "chosen": True,
        "rationale": (
            "engine truth that moves under the keeper's verbs — and it "
            "is already on the player's screen under its own accurate "
            "name; M5: 'bond is a separate documented axis, not a "
            "synonym'"
        ),
    },
    "need_balance": {
        "label": "the engine's own per-tick contentment statistic",
        "reads": ["hunger", "energy", "stress", "bond", "grid_stability"],
        "chosen": True,
        "rationale": (
            "1 - mean(|axis - target|) over the five homeostasis axes, "
            "computed and recorded by advance_tick in every history "
            "entry since Stage 0 — the engine already writes this "
            "number every tick; nothing is invented"
        ),
    },
    "social_warmth": {
        "label": "being tended lately: the recent-interaction window",
        "reads": ["recent_interactions"],
        "chosen": True,
        "rationale": (
            "the mean of the engine's last-5-tick keeper-care trace "
            "(1 when the executed action was feed or play), carried in "
            "state and consumed by the switchboard since Stage 0"
        ),
    },
}

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 26 P2), refusal first-class and reachable "
    "for every candidate; every definition is declared CHOSEN up front "
    "because validity-research.md names `happiness` and never defines "
    "it. G1 — the definition names the engine fields it reads. G2 — "
    "the KEEPER can move it, judged against the player's verbs (feed, "
    "play), the bar MEASURED as the smallest response any existing "
    "visible axis shows to those verbs, and the recomputed floor must "
    "reproduce the committed N5 floor exactly (instrument check — a "
    "mismatch raises instead of judging). G3 — care-coupled: a "
    "cherished life and a neglected life must separate on it. G4 — the "
    "label test: distress relieved by the keeper must RAISE the bar, "
    "else refuse_as_euphemism. G5 — distinct from what is shown: a "
    "per-tick identity with a readout already on the player's screen "
    "under another name earns refuse_as_duplicate, which OUTRANKS the "
    "euphemism verdict (the sharper accusation: nothing about the "
    "number is wrong, only the second name). Selection among eligible "
    "candidates: the LOWEST final reading on the neglected corpse wins "
    "(N5's refusal logic made into the selection statistic), ties to "
    "the definition reading fewer engine fields, then by name. At most "
    "one adoption; eligible non-winners are recorded "
    "eligible_not_selected. This module builds no UI."
)

PRE_RUN_PREDICTION = (
    "Written before the run, so it can be wrong on the record: "
    "bond_rename is expected to pass G1–G4 and be REFUSED on G5 as a "
    "duplicate — its series is the shown bond readout's by "
    "construction, and one number may not wear two visible names. "
    "social_warmth is expected to be ELIGIBLE and SELECTED: a "
    "neglected companion's window empties, so the corpse reads 0.0 — "
    "the strongest honesty property available — while feed and play "
    "move it well over the floor. need_balance is the deliberate "
    "uncertainty, named in advance on two counts: its G2 response from "
    "a near-target start may fall under the floor (feeding an "
    "un-hungry creature moves the mean distance little), and if it is "
    "eligible its neglect-death reading is expected HIGH (~0.7 — a "
    "mean hides the killer axis, the exact property that made health a "
    "minimum), which the selection statistic penalizes. If adopted, "
    "social_warmth is additionally expected to RISE under play while "
    "the health readout falls — the property that makes happiness "
    "informative beside health, recorded as an observation, not a "
    "gate. If the measurement disagrees, the measurement wins."
)

PROBE_TIMEOUT_S = 240

_PROBE = r"""
import json, sys
from mecha_engine.lifecycle import (
    ACTIONS, DANGER_THRESHOLDS, advance_tick, initial_state,
)

grid = json.loads(open(sys.argv[1], encoding="utf-8").read())
ticks = int(sys.argv[2])
lifecycles = int(sys.argv[3])
AXES = ["hunger", "energy", "stress", "bond", "grid_stability"]


def snap(state):
    return {axis: round(float(state[axis]), 6) for axis in AXES}


def tick_record(state):
    entry = state["history"][-1]
    return {
        "snap": snap(state),
        "window": list(state.get("recent_interactions", [])),
        "balance": entry["balance"],
    }


base = initial_state(grid, None)
out = {
    "danger_thresholds": dict(DANGER_THRESHOLDS),
    "actions": list(ACTIONS),
    "initial": {
        "snap": snap(base),
        "window": list(base.get("recent_interactions", [])),
    },
}

# 1) One tick of each action from the SAME state.
per_action = {}
for action in ACTIONS:
    after = advance_tick(base, action)
    per_action[action] = tick_record(after)
    per_action[action]["delta"] = {
        axis: round(after[axis] - base[axis], 6) for axis in AXES
    }
out["per_action"] = per_action

# 2) Distress, then relief: idle into hunger danger, then the keeper feeds.
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
    "before": tick_record(distress),
    "after_keeper_feed": tick_record(relieved),
}

# 3) Real lifecycles with PER-TICK series: a NEGLECT arm (idle only) and
#    a CARE arm (feed / play / sleep).
runs = []
for index in range(lifecycles):
    for arm, cycle in (("neglect", ["idle"]), ("care", ["feed", "play", "sleep"])):
        state = initial_state(grid, None)
        series = []
        step = 0
        while state["alive"] and step < ticks:
            state = advance_tick(state, cycle[step % len(cycle)])
            series.append(tick_record(state))
            step += 1
        runs.append(
            {
                "arm": arm,
                "index": index,
                "alive": bool(state["alive"]),
                "death_cause": state["death_cause"],
                "ticks": step,
                "series": series,
            }
        )
out["lifecycles"] = runs
print(json.dumps(out))
"""


def _probe_env() -> dict:
    """Inherit the environment and EXTEND PYTHONPATH, never replace it."""
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(PACKAGE_SRC) + (
        os.pathsep + existing if existing else ""
    )
    return env


def probe_engine(*, ticks: int, lifecycles: int) -> dict:
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


# -- the candidate value functions ------------------------------------------


def social_warmth(window: list) -> float:
    """Candidate C: the mean of the recent-interaction window."""
    if not window:
        return 0.0
    return round(mean(float(value) for value in window), 6)


def need_balance_mirror(snapshot: dict) -> float:
    """Candidate B's statistic, MIRRORED from simulate._need_balance and
    pinned tick-for-tick against the engine's own recorded balances."""
    distances = [
        abs(float(snapshot[axis]) - target)
        for axis, target in _TARGETS.items()
    ]
    return round(max(0.0, min(1.0, 1 - mean(distances))), 6)


def candidate_value(name: str, record: dict, thresholds: dict) -> float:
    """One candidate's reading of one per-tick probe record."""
    if name == "bond_rename":
        return round(float(record["snap"]["bond"]), 6)
    if name == "need_balance":
        # The engine's own recorded number when the record carries one;
        # the pinned mirror for pre-tick states.
        if "balance" in record:
            return round(float(record["balance"]), 6)
        return need_balance_mirror(record["snap"])
    if name == "social_warmth":
        return social_warmth(record["window"])
    raise ValueError(f"unknown happiness candidate: {name}")


def _shown_readout_value(name: str, record: dict, thresholds: dict) -> float:
    if name == "danger_margin":
        return danger_margin(record["snap"], thresholds)
    return round(float(record["snap"][name]), 6)


# -- the pre-registered judge -----------------------------------------------


def judge_candidate(
    *,
    candidate: str,
    reads: list,
    keeper_action_response: dict,
    incumbent_response_floor: float,
    distress_relief: float,
    care_coupled: bool,
    duplicate_of: str | None,
) -> dict:
    """Apply the five pre-registered gates. Every verdict first-class."""
    if incumbent_response_floor < 0:
        raise ValueError(
            "the incumbent response floor is a measured magnitude and "
            f"cannot be negative: {incumbent_response_floor!r}"
        )
    best_keeper_response = max(
        (abs(value) for value in keeper_action_response.values()), default=0.0
    )
    failed = []
    if not reads:
        failed.append("G1_definition_declared")
    if best_keeper_response < incumbent_response_floor:
        failed.append("G2_keeper_responsive")
    if not care_coupled:
        failed.append("G3_care_coupled")
    if distress_relief <= 0.0:
        failed.append("G4_honest_label")
    if duplicate_of is not None:
        failed.append("G5_distinct_from_shown")

    if "G5_distinct_from_shown" in failed:
        verdict = "refuse_as_duplicate"
    elif "G4_honest_label" in failed:
        verdict = "refuse_as_euphemism"
    elif failed:
        verdict = "withhold"
    else:
        verdict = "eligible"

    return {
        "candidate": candidate,
        "verdict": verdict,
        "failed_gates": failed,
        "chosen_definition": True,
        "reads": list(reads),
        "keeper_action_response": dict(keeper_action_response),
        "best_keeper_response": round(best_keeper_response, 6),
        "incumbent_response_floor": round(incumbent_response_floor, 6),
        "distress_relief": round(distress_relief, 6),
        "care_coupled": care_coupled,
        "duplicate_of": duplicate_of,
    }


# -- the report --------------------------------------------------------------


def build_happiness_definition_report(
    *, ticks: int = 200, lifecycles: int = 3
) -> dict:
    engine = probe_engine(ticks=ticks, lifecycles=lifecycles)
    thresholds = engine["danger_thresholds"]
    per_action = engine["per_action"]
    initial = engine["initial"]

    # G2's floor, measured — and checked against the committed N5 floor
    # before anything is judged (Phase N's law, O4's hard-gate shape).
    incumbent_responses = {
        axis: max(
            abs(per_action[action]["delta"][axis]) for action in KEEPER_ACTIONS
        )
        for axis in INCUMBENT_VISIBLE_AXES
    }
    incumbent_floor = min(incumbent_responses.values())
    committed = json.loads(
        (ROOT / COMMITTED_HEALTH_GATE).read_text(encoding="utf-8")
    )
    committed_floor = committed["metrics"]["incumbent_response_floor"]
    if round(incumbent_floor, 6) != committed_floor:
        raise ValueError(
            "instrument drift: the recomputed keeper-response floor "
            f"{round(incumbent_floor, 6)} does not reproduce the "
            f"committed N5 floor {committed_floor}; this gate refuses "
            "to judge with an unverified instrument"
        )

    # The balance mirror, pinned tick-for-tick against the engine's own
    # recorded per-tick balances over every probe series tick.
    mirror_differences = [
        abs(need_balance_mirror(record["snap"]) - float(record["balance"]))
        for run in engine["lifecycles"]
        for record in run["series"]
    ]
    balance_parity = {
        "ticks_compared": len(mirror_differences),
        "max_abs_difference": round(max(mirror_differences), 6)
        if mirror_differences
        else None,
    }
    if balance_parity["max_abs_difference"] != 0.0:
        raise ValueError(
            "the need_balance mirror drifted from the engine's own "
            f"recorded balances: {balance_parity}"
        )

    neglect_runs = [r for r in engine["lifecycles"] if r["arm"] == "neglect"]
    care_runs = [r for r in engine["lifecycles"] if r["arm"] == "care"]

    judged: dict[str, dict] = {}
    measures: dict[str, dict] = {}
    for name, spec in CANDIDATES.items():
        base_record = {"snap": initial["snap"], "window": initial["window"]}
        keeper_response = {
            action: round(
                candidate_value(name, per_action[action], thresholds)
                - candidate_value(name, base_record, thresholds),
                6,
            )
            for action in KEEPER_ACTIONS
        }
        relief = round(
            candidate_value(
                name, engine["distress"]["after_keeper_feed"], thresholds
            )
            - candidate_value(name, engine["distress"]["before"], thresholds),
            6,
        )
        neglect_finals = [
            candidate_value(name, run["series"][-1], thresholds)
            for run in neglect_runs
        ]
        care_finals = [
            candidate_value(name, run["series"][-1], thresholds)
            for run in care_runs
        ]
        care_coupled = bool(
            care_finals
            and neglect_finals
            and min(care_finals) > max(neglect_finals)
        )

        # G5: per-tick identity against every readout the client shows.
        candidate_series = [
            candidate_value(name, record, thresholds)
            for run in engine["lifecycles"]
            for record in run["series"]
        ]
        duplicate_of = None
        for shown in SHOWN_READOUTS:
            shown_series = [
                _shown_readout_value(shown, record, thresholds)
                for run in engine["lifecycles"]
                for record in run["series"]
            ]
            if candidate_series == shown_series:
                duplicate_of = shown
                break

        # The differentiation observation (recorded, never a gate).
        health_play_response = round(
            danger_margin(per_action["play"]["snap"], thresholds)
            - danger_margin(initial["snap"], thresholds),
            6,
        )
        measures[name] = {
            "keeper_response": keeper_response,
            "distress_relief": relief,
            "neglect_final_readings": neglect_finals,
            "care_final_readings": care_finals,
            "care_coupled": care_coupled,
            "duplicate_of": duplicate_of,
            "informative_beside_health": {
                "candidate_play_response": keeper_response["play"],
                "health_play_response": health_play_response,
                "play_raises_it_while_health_falls": bool(
                    keeper_response["play"] > 0 and health_play_response < 0
                ),
            },
        }
        judged[name] = judge_candidate(
            candidate=name,
            reads=list(spec["reads"]),
            keeper_action_response=keeper_response,
            incumbent_response_floor=incumbent_floor,
            distress_relief=relief,
            care_coupled=care_coupled,
            duplicate_of=duplicate_of,
        )

    # The pre-registered selection among eligible candidates.
    eligible = sorted(
        name for name, entry in judged.items() if entry["verdict"] == "eligible"
    )
    selection_readings = {
        name: max(measures[name]["neglect_final_readings"]) for name in eligible
    }
    winner = (
        min(
            eligible,
            key=lambda name: (
                selection_readings[name],
                len(CANDIDATES[name]["reads"]),
                name,
            ),
        )
        if eligible
        else None
    )

    decision_candidates = {}
    for name, entry in judged.items():
        final = dict(entry)
        if entry["verdict"] == "eligible":
            final["verdict"] = (
                "adopt" if name == winner else "eligible_not_selected"
            )
        final["neglect_final_reading"] = (
            max(measures[name]["neglect_final_readings"])
            if measures[name]["neglect_final_readings"]
            else None
        )
        final["care_final_reading"] = (
            min(measures[name]["care_final_readings"])
            if measures[name]["care_final_readings"]
            else None
        )
        decision_candidates[name] = final

    adopted = [winner] if winner else []
    predicted = {"adopted": ["social_warmth"], "duplicate": "bond_rename"}
    outcome_measured = {
        "adopted": adopted,
        "duplicate": next(
            (
                name
                for name, entry in decision_candidates.items()
                if entry["verdict"] == "refuse_as_duplicate"
            ),
            None,
        ),
    }
    prediction_outcome = (
        "prediction_confirmed"
        if outcome_measured == predicted
        else (
            f"prediction_refuted: predicted {predicted}, measured "
            f"{outcome_measured}"
        )
    )

    # Parity values for the game-side mirror (the O2 pattern: the game
    # mirrors the adopted formula and pins it against THIS artifact).
    mirror_parity_values = [
        {"window": window, "value": social_warmth(window)}
        for window in (
            [1, 0, 1],
            [1, 0, 1, 1],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1],
            [1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1],
            [],
        )
    ]

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 26 P2: gate a CHOSEN definition of the documented "
            "VISIBLE axis `happiness`, which DR 0048 put out of scope "
            "pending a definition. Three candidates read from what the "
            "engine already records; five pre-registered gates "
            "(N5's four, plus G5 distinct-from-shown); selection among "
            "eligibles by the lowest reading on the neglected corpse; "
            "refusal first-class."
        ),
        "source_artifacts": [
            "data/architecture/companion_state_survey_stage0.json",
            "data/architecture/health_definition_gate_stage0.json",
            "data/game_client/companion_axis_split_stage0.json",
            "data/seed_grids_16x16/mg_seed16_001_beetle.json",
            "packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py",
            "research/decision_records/0048-visible-companion-state-axes.md",
            "research/decision_records/0054-health-definition-danger-margin.md",
        ],
        "parameters": {
            "ticks": ticks,
            "lifecycles": lifecycles,
            "keeper_actions": list(KEEPER_ACTIONS),
            "incumbent_visible_axes": list(INCUMBENT_VISIBLE_AXES),
            "shown_readouts_compared": list(SHOWN_READOUTS),
            "candidates": {
                name: dict(spec) for name, spec in CANDIDATES.items()
            },
            "seed_grid": "data/seed_grids_16x16/mg_seed16_001_beetle.json",
        },
        "metrics": {
            "instrument_check": {
                "committed_artifact": COMMITTED_HEALTH_GATE,
                "committed_floor": committed_floor,
                "recomputed_floor": round(incumbent_floor, 6),
                "floor_matches_committed": True,
            },
            "balance_mirror_parity": balance_parity,
            "incumbent_keeper_responses": incumbent_responses,
            "candidates": measures,
            "game_mirror_parity_values": mirror_parity_values,
        },
        "closed_states": [
            "every definition is declared CHOSEN up front, because "
            "validity-research.md names `happiness` and never defines it",
            "every candidate reads only what the engine already records "
            "— nothing is invented (DR 0021's first law)",
            "the duplicate question is a REAL GATE with a per-tick "
            "identity answer, not a judgement call",
            "the G2 floor reproduced the committed N5 floor exactly "
            "before anything was judged",
            "the need_balance mirror is pinned tick-for-tick against "
            "the engine's own recorded balances",
            "a prediction was recorded BEFORE the run",
        ],
        "blocked_states": [
            "this module builds no UI: landing the adopted readout is "
            "the same P2 slice's game-side change, pinned against this "
            "artifact's game_mirror_parity_values",
            "one seed creature and one SLIP-free lifecycle: the action "
            "model is profile-independent but magnitudes would move "
            "under other profiles (N5's inherited limit)",
            "the adopted definition, if any, is CHOSEN — §1.17 still "
            "does not define the axis, and the surface must say chosen "
            "(the DR 0055 pattern)",
            "`cleanliness` stays OUT OF SCOPE (DR 0048): it needs a "
            "MECHANIC, and that is P3's charter",
        ],
        "decision": {
            "candidates": decision_candidates,
            "adopted": adopted,
            "selection_readings": selection_readings,
            "rule": PRE_REGISTERED_RULE,
            "pre_run_prediction": PRE_RUN_PREDICTION,
            "prediction_outcome": prediction_outcome,
        },
        "next_research_step": (
            "Land the adopted readout in the game (same slice) with the "
            "mirror pinned against this artifact; record the decision "
            "as DR 0058; then P3, the cleanliness mechanic gate."
        ),
    }


def write_happiness_definition_artifacts(
    output_dir: str | Path, report: dict
) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{ARTIFACT_ID}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cycle 26 P2: the happiness definition gate."
    )
    parser.add_argument("--output-dir", default=str(ROOT / "data" / "architecture"))
    parser.add_argument("--ticks", type=int, default=200)
    parser.add_argument("--lifecycles", type=int, default=3)
    args = parser.parse_args()

    report = build_happiness_definition_report(
        ticks=args.ticks, lifecycles=args.lifecycles
    )
    metrics = report["metrics"]
    print(
        "instrument: committed floor "
        f"{metrics['instrument_check']['committed_floor']} reproduced; "
        "balance mirror parity "
        f"{metrics['balance_mirror_parity']}"
    )
    print()
    for name, entry in report["decision"]["candidates"].items():
        candidate = metrics["candidates"][name]
        print(f"  {name}")
        print(
            f"    keeper response {candidate['keeper_response']}  "
            f"distress relief {candidate['distress_relief']}"
        )
        print(
            f"    neglect finals {candidate['neglect_final_readings']}  "
            f"care finals {candidate['care_final_readings']}  "
            f"coupled {candidate['care_coupled']}  "
            f"duplicate_of {candidate['duplicate_of']}"
        )
        print(
            f"    play raises it while health falls: "
            f"{candidate['informative_beside_health']['play_raises_it_while_health_falls']}"
        )
        print(
            f"    -> {entry['verdict'].upper()}"
            + (
                f"  (failed {','.join(entry['failed_gates'])})"
                if entry["failed_gates"]
                else ""
            )
        )
    print(f"\nadopted: {report['decision']['adopted'] or 'NONE'}")
    print(report["decision"]["prediction_outcome"])
    for path in write_happiness_definition_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
