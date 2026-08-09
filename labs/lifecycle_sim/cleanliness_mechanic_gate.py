"""Cycle 26 P3: the cleanliness mechanic, gated. (ENGINE gate → GAME landing.)

`validity-research.md` §1.17 names `cleanliness` a **VISIBLE** companion
state axis; M5 measured the gap precisely — *"there is no clean action
— and no state accumulates dirt"* — and DR 0048 recorded it as needing
a MECHANIC with its own record: *"a need, a decay, an action that
answers it, and its interaction with the switchboard policy and the
reward function."*

The seam now exists in the package lifecycle (cycle 26 P3), OPT-IN via
``initial_state(..., mechanics=("cleanliness",))`` and **byte-identical
when off** — pinned in the package suite against the committed Stage 0
comparator's own numbers. Every parameter is DERIVED from the incumbent
engine (the median drift magnitude; mutate's own grid cost; feed's own
hunger relief; the engine's own need→stress coefficient). This gate
decides whether the seam may SHIP, judging it through the package
boundary the way N5 judged the health definitions.

THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN
===============================================

* **G1 — the need decays.** With the mechanic on and nobody cleaning,
  `cleanliness` falls strictly every live tick. A need that does not
  need is not a need → ``withhold``.
* **G2 — the KEEPER can move it.** The `clean` verb's response from a
  dirty live state must clear the same measured floor every visible
  axis cleared (N5's committed 0.0685, reproduced by this instrument
  before judging) → ``withhold``.
* **G3a — the consequence is measurable.** On the neglect stream the
  dirt→stress coupling must move final stress by MORE THAN ZERO against
  the incumbent (the engine is deterministic; the noise floor is
  exactly zero). Failing this is the charter's own refusal —
  ``blocked_on_mechanic``: the smallest honest mechanic is
  indistinguishable from the incumbent engine at the documented
  budgets, and a need nobody can measure is not a need.
* **G3b — the consequence is BOUNDED.** A cosmetic axis may not kill
  the companion (survival and death cause unchanged on the neglect
  stream AND under the autonomous switchboard at the documented
  horizon) and may not move the documented welfare statistic beyond
  the D6 ablation bar (|Δ need_balance| / incumbent < 5% under the
  switchboard). Failing either is ``refuse_as_lethal_cosmetic`` — the
  refusals outrank the withholdings.
* **G4 — the answer answers.** One `clean` on a dirty live companion
  raises `cleanliness` → ``withhold``.

**A PREDICTION IS RECORDED BEFORE THE RUN** (``PRE_RUN_PREDICTION``).
This module builds no UI; if the mechanic is adopted, landing the
opt-in readout is the same P3 slice's game-side change.
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

ARTIFACT_ID = "cleanliness_mechanic_gate_stage0"
REPORT_DATE = "2026-08-09"
COMMITTED_LIFECYCLE = "data/lifecycle/lifecycle_stage0.json"
COMMITTED_HEALTH_GATE = "data/architecture/health_definition_gate_stage0.json"

# The documented D6 ablation bar — the repo's welfare significance bar
# ("at least a 5% decline in one target metric"), applied here as the
# ceiling a cosmetic mechanic may not move the welfare statistic past.
D6_WELFARE_BAR = 0.05

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 26 P3), every verdict first-class. The seam "
    "is judged through the package boundary at the documented Stage 0 "
    "budget (72 ticks, the committed comparator grid and covenant), "
    "with the instrument required to reproduce the committed "
    "switchboard and idle episodes and N5's committed keeper-response "
    "floor before anything is judged. G1 the need decays (else "
    "withhold); G2 the clean verb clears the committed 0.0685 floor "
    "from a dirty live state (else withhold); G3a the dirt->stress "
    "consequence moves final stress on the neglect stream by more than "
    "zero against the incumbent - the engine is deterministic, so the "
    "noise floor is exactly zero - else BLOCKED_ON_MECHANIC, the "
    "charter's own refusal; G3b the consequence is bounded - survival "
    "and death cause unchanged on the neglect stream and under the "
    "autonomous switchboard, and |delta need_balance|/incumbent under "
    "the documented D6 welfare bar (5%) - else "
    "REFUSE_AS_LETHAL_COSMETIC, and the refusals outrank the "
    "withholdings; G4 one clean on a dirty live companion raises "
    "cleanliness (else withhold). This module builds no UI."
)

PRE_RUN_PREDICTION = (
    "Written before the run: ADOPT. The neglect stream is expected to "
    "show the measurable consequence (dirt pressure raises final "
    "stress above the incumbent's committed 0.55004 by a small exact "
    "amount) without moving the starvation death at tick 11; the "
    "attentive keeper's care is expected to ABSORB the dirt pressure "
    "almost entirely (stress relief from feed and sleep dwarfs the "
    "<=0.01-per-tick coupling), recorded as the fairness finding "
    "either way; the switchboard's welfare impact is expected well "
    "under the 5% bar; and the clean verb's +0.32 restore clears the "
    "0.0685 floor by construction - the gate proves the "
    "implementation, not the intent. If the measurement disagrees, "
    "the measurement wins."
)

PROBE_TIMEOUT_S = 240

_PROBE = r"""
import json, sys
from mecha_engine.lifecycle import ACTIONS, advance_tick, initial_state, run_episode

grid = json.loads(open(sys.argv[1], encoding="utf-8").read())
slip = json.loads(open(sys.argv[2], encoding="utf-8").read())
MECH = ("cleanliness",)
out = {}


def episode_summary(episode):
    summary = {
        "survival_ticks": episode["survival_ticks"],
        "alive": episode["alive"],
        "death_cause": episode["death_cause"],
        "need_balance": episode["need_balance"],
        "final_state": episode["final_state"],
    }
    if "final_cleanliness" in episode:
        summary["final_cleanliness"] = episode["final_cleanliness"]
    return summary


# Instrument: the committed episodes, reproduced off-mode.
out["off_switchboard"] = episode_summary(
    run_episode(grid, slip, policy="switchboard")
)
out["off_idle"] = episode_summary(run_episode(grid, slip, policy="idle"))

# Instrument: the N5 keeper floor, recomputed from per-action deltas.
base = initial_state(grid, None)
AXES = ["hunger", "energy", "stress", "bond", "grid_stability"]
per_action = {}
for action in ACTIONS:
    after = advance_tick(base, action)
    per_action[action] = {
        axis: round(after[axis] - base[axis], 6) for axis in AXES
    }
out["per_action_delta"] = per_action

# G1: the need decays under care without cleaning.
on = initial_state(grid, slip, mechanics=MECH)
care = ["feed", "play", "sleep"]
series = []
state = on
for step in range(30):
    state = advance_tick(state, care[step % 3])
    series.append(state["cleanliness"])
out["care_cleanliness_series"] = series
out["care_alive"] = state["alive"]

# G2/G4: one clean from the dirty live state.
cleaned = advance_tick(state, "clean")
out["dirty_value"] = state["cleanliness"]
out["cleaned_value"] = cleaned["cleanliness"]

# G3a/G3b: the neglect stream, on vs off (explicit stream, paired).
neglect_off = run_episode(grid, slip, actions=["idle"] * 72, ticks=72)
neglect_on = run_episode(
    grid, slip, actions=["idle"] * 72, ticks=72, mechanics=MECH
)
out["neglect_off"] = episode_summary(neglect_off)
out["neglect_on"] = episode_summary(neglect_on)

# G3b: the autonomous switchboard, on vs off.
switch_on = run_episode(grid, slip, policy="switchboard", mechanics=MECH)
out["switchboard_on"] = episode_summary(switch_on)

# The absorption finding: the same explicit care stream, on vs off.
care_stream = care * 24
care_off = run_episode(grid, slip, actions=care_stream, ticks=72)
care_on = run_episode(
    grid, slip, actions=care_stream, ticks=72, mechanics=MECH
)
out["care_off"] = episode_summary(care_off)
out["care_on"] = episode_summary(care_on)
print(json.dumps(out))
"""


def _probe_env() -> dict:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(PACKAGE_SRC) + (
        os.pathsep + existing if existing else ""
    )
    return env


def probe_engine() -> dict:
    grid = ROOT / "data" / "seed_grids" / "mg_seed_001.json"
    slip = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
    try:
        result = subprocess.run(
            [sys.executable, "-B", "-c", _PROBE, str(grid), str(slip)],
            capture_output=True,
            text=True,
            env=_probe_env(),
            cwd=str(ROOT),
            timeout=PROBE_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(
            f"the engine probe did not return within {PROBE_TIMEOUT_S}s; "
            "this gate refuses to judge a mechanic it could not measure"
        ) from error
    if result.returncode != 0:
        raise RuntimeError(
            "the engine probe failed; this gate refuses to judge a "
            f"mechanic it could not measure:\n{result.stderr}"
        )
    return json.loads(result.stdout)


def judge_mechanic(
    *,
    need_decays: bool,
    keeper_response: float,
    incumbent_response_floor: float,
    clean_answers: bool,
    consequence_measurable: bool,
    survival_unchanged: bool,
    welfare_impact: float,
) -> dict:
    """Apply the pre-registered gates. Every verdict first-class."""
    if incumbent_response_floor < 0:
        raise ValueError(
            "the incumbent response floor is a measured magnitude and "
            f"cannot be negative: {incumbent_response_floor!r}"
        )
    failed = []
    if not need_decays:
        failed.append("G1_need_decays")
    if abs(keeper_response) < incumbent_response_floor:
        failed.append("G2_keeper_responsive")
    if not consequence_measurable:
        failed.append("G3a_consequence_measurable")
    if not survival_unchanged:
        failed.append("G3b_survival_unchanged")
    if welfare_impact >= D6_WELFARE_BAR:
        failed.append("G3b_welfare_bounded")
    if not clean_answers:
        failed.append("G4_clean_answers")

    if "G3b_survival_unchanged" in failed or "G3b_welfare_bounded" in failed:
        verdict = "refuse_as_lethal_cosmetic"
    elif "G3a_consequence_measurable" in failed:
        verdict = "blocked_on_mechanic"
    elif failed:
        verdict = "withhold"
    else:
        verdict = "adopt"

    return {
        "verdict": verdict,
        "failed_gates": failed,
        "need_decays": need_decays,
        "keeper_response": round(keeper_response, 6),
        "incumbent_response_floor": round(incumbent_response_floor, 6),
        "clean_answers": clean_answers,
        "consequence_measurable": consequence_measurable,
        "survival_unchanged": survival_unchanged,
        "welfare_impact": round(welfare_impact, 6),
        "welfare_bar": D6_WELFARE_BAR,
    }


def build_cleanliness_mechanic_report() -> dict:
    engine = probe_engine()
    committed = json.loads(
        (ROOT / COMMITTED_LIFECYCLE).read_text(encoding="utf-8")
    )
    committed_switch = committed["policies"]["switchboard"]
    committed_idle = committed["policies"]["idle"]
    health_gate = json.loads(
        (ROOT / COMMITTED_HEALTH_GATE).read_text(encoding="utf-8")
    )
    committed_floor = health_gate["metrics"]["incumbent_response_floor"]

    # Instrument gate 1: the committed episodes reproduced off-mode.
    switchboard_reproduced = (
        engine["off_switchboard"]["survival_ticks"]
        == committed_switch["survival_ticks"]
        and engine["off_switchboard"]["need_balance"]
        == committed_switch["need_balance"]
        and engine["off_switchboard"]["final_state"]
        == committed_switch["final_state"]
    )
    idle_reproduced = (
        engine["off_idle"]["survival_ticks"] == committed_idle["survival_ticks"]
        and engine["off_idle"]["death_cause"] == committed_idle["death_cause"]
        and engine["off_idle"]["need_balance"] == committed_idle["need_balance"]
    )
    if not (switchboard_reproduced and idle_reproduced):
        raise ValueError(
            "instrument drift: the off-mode engine did not reproduce the "
            "committed Stage 0 episodes; this gate refuses to judge a "
            "seam whose off mode has moved"
        )

    # Instrument gate 2: N5's keeper floor, recomputed.
    incumbent_responses = {
        axis: max(
            abs(engine["per_action_delta"][action][axis])
            for action in ("feed", "play")
        )
        for axis in ("hunger", "energy", "bond")
    }
    recomputed_floor = min(incumbent_responses.values())
    if round(recomputed_floor, 6) != committed_floor:
        raise ValueError(
            "instrument drift: the recomputed keeper floor "
            f"{round(recomputed_floor, 6)} does not reproduce N5's "
            f"committed {committed_floor}"
        )

    # G1: strict decay every live tick of the un-cleaned care stream.
    series = engine["care_cleanliness_series"]
    need_decays = bool(engine["care_alive"]) and all(
        later < earlier for earlier, later in zip(series, series[1:])
    ) and series[0] < 1.0

    # G2/G4.
    keeper_response = round(
        engine["cleaned_value"] - engine["dirty_value"], 6
    )
    clean_answers = engine["cleaned_value"] > engine["dirty_value"]

    # G3a: the deterministic consequence on the neglect stream.
    stress_delta = round(
        engine["neglect_on"]["final_state"]["stress"]
        - engine["neglect_off"]["final_state"]["stress"],
        6,
    )
    consequence_measurable = stress_delta > 0.0

    # G3b: bounded.
    survival_unchanged = (
        engine["neglect_on"]["survival_ticks"]
        == engine["neglect_off"]["survival_ticks"]
        and engine["neglect_on"]["death_cause"]
        == engine["neglect_off"]["death_cause"]
        and engine["switchboard_on"]["survival_ticks"]
        == committed_switch["survival_ticks"]
        and engine["switchboard_on"]["death_cause"]
        == committed_switch["death_cause"]
    )
    welfare_impact = round(
        abs(
            engine["switchboard_on"]["need_balance"]
            - committed_switch["need_balance"]
        )
        / committed_switch["need_balance"],
        6,
    )

    judged = judge_mechanic(
        need_decays=need_decays,
        keeper_response=keeper_response,
        incumbent_response_floor=recomputed_floor,
        clean_answers=clean_answers,
        consequence_measurable=consequence_measurable,
        survival_unchanged=survival_unchanged,
        welfare_impact=welfare_impact,
    )

    care_stress_delta = round(
        engine["care_on"]["final_state"]["stress"]
        - engine["care_off"]["final_state"]["stress"],
        6,
    )
    findings = {
        "neglect_stress_delta": stress_delta,
        "care_stress_delta": care_stress_delta,
        "care_absorbs_dirt_pressure": care_stress_delta == 0.0,
        "switchboard_need_balance_on": engine["switchboard_on"]["need_balance"],
        "switchboard_need_balance_committed": committed_switch["need_balance"],
        "neglect_final_cleanliness": engine["neglect_on"].get(
            "final_cleanliness"
        ),
        "care_final_cleanliness_uncleaned": series[-1] if series else None,
    }

    prediction_outcome = (
        "prediction_confirmed"
        if judged["verdict"] == "adopt"
        else f"prediction_refuted: predicted adopt, measured {judged['verdict']}"
    )

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 26 P3: gate the opt-in cleanliness mechanic seam — "
            "the MECHANIC gap DR 0048 measured (no field, no decay, no "
            "answering action) — through the package boundary at the "
            "documented Stage 0 budget, with every verdict the charter "
            "names first-class: withhold, blocked_on_mechanic, "
            "refuse_as_lethal_cosmetic, adopt."
        ),
        "source_artifacts": [
            COMMITTED_LIFECYCLE,
            COMMITTED_HEALTH_GATE,
            "data/seed_grids/mg_seed_001.json",
            "data/slips/valid/slip_lcd_seed.json",
            "packages/mecha_engine/src/mecha_engine/lifecycle/simulate.py",
            "packages/mecha_engine/tests/test_lifecycle_cleanliness_seam.py",
            "research/decision_records/0048-visible-companion-state-axes.md",
        ],
        "parameters": {
            "ticks": 72,
            "seed_grid": "data/seed_grids/mg_seed_001.json",
            "slip_profile": "data/slips/valid/slip_lcd_seed.json",
            "derived_constants": {
                "decay": 0.0124,
                "mutate_mess": 0.055,
                "clean_restore": 0.32,
                "stress_coefficient": 0.01,
            },
            "welfare_bar": D6_WELFARE_BAR,
        },
        "metrics": {
            "instrument_check": {
                "switchboard_reproduced": switchboard_reproduced,
                "idle_reproduced": idle_reproduced,
                "committed_need_balance": committed_switch["need_balance"],
                "committed_keeper_floor": committed_floor,
                "recomputed_keeper_floor": round(recomputed_floor, 6),
            },
            "gates": judged,
            "findings": findings,
            "engine": engine,
        },
        "closed_states": [
            "the seam is byte-identical when off, pinned in the package "
            "suite against the committed Stage 0 comparator's own "
            "numbers (the M3 lesson: frozen literals, never new-vs-new)",
            "every mechanic parameter is DERIVED from the incumbent "
            "engine, never picked",
            "the instrument reproduced the committed episodes and N5's "
            "committed keeper floor before judging",
            "the autonomous policies never choose clean — the companion "
            "cannot clean itself, the documented interaction model",
            "a prediction was recorded BEFORE the run",
        ],
        "blocked_states": [
            "the mechanic is OPT-IN and the default covenant does not "
            "enable it: flipping the default is a product decision with "
            "its own record and a priced evidence-regeneration cascade, "
            "deliberately not taken here",
            "a SLIP-carried opt-in needs a schema-ladder rung (DR 0012); "
            "until then the mechanics keyword is the only author",
            "cleanliness stays OUT of TARGETS/_need_balance/reward and "
            "out of DANGER_THRESHOLDS: the incumbent statistics keep "
            "their meaning, and a danger threshold for dirt would be a "
            "separate gated decision",
            "one seed creature and one covenant (the Stage 0 comparator "
            "pair); magnitudes would move under other profiles",
        ],
        "decision": {
            "verdict": judged["verdict"],
            "gates": judged,
            "rule": PRE_REGISTERED_RULE,
            "pre_run_prediction": PRE_RUN_PREDICTION,
            "prediction_outcome": prediction_outcome,
        },
        "next_research_step": (
            "If adopted: land the opt-in readout and the clean verb in "
            "the game (same slice), record DR 0059, and name the "
            "default-covenant decision as its own future record."
        ),
    }


def write_cleanliness_mechanic_artifacts(
    output_dir: str | Path, report: dict
) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{ARTIFACT_ID}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cycle 26 P3: the cleanliness mechanic gate."
    )
    parser.add_argument("--output-dir", default=str(ROOT / "data" / "lifecycle"))
    args = parser.parse_args()

    report = build_cleanliness_mechanic_report()
    metrics = report["metrics"]
    check = metrics["instrument_check"]
    print(
        f"instrument: committed episodes reproduced "
        f"(switchboard {check['switchboard_reproduced']}, idle "
        f"{check['idle_reproduced']}); keeper floor "
        f"{check['committed_keeper_floor']} reproduced"
    )
    gates = metrics["gates"]
    print(
        f"G1 decays {gates['need_decays']}  "
        f"G2 clean response {gates['keeper_response']} "
        f"(floor {gates['incumbent_response_floor']})  "
        f"G4 answers {gates['clean_answers']}"
    )
    print(
        f"G3a neglect stress delta {metrics['findings']['neglect_stress_delta']}  "
        f"G3b survival unchanged {gates['survival_unchanged']}, "
        f"welfare impact {gates['welfare_impact']} (bar {gates['welfare_bar']})"
    )
    print(
        f"care absorbs dirt pressure: "
        f"{metrics['findings']['care_absorbs_dirt_pressure']} "
        f"(care stress delta {metrics['findings']['care_stress_delta']})"
    )
    print(f"\nverdict: {gates['verdict'].upper()}")
    print(report["decision"]["prediction_outcome"])
    for path in write_cleanliness_mechanic_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
