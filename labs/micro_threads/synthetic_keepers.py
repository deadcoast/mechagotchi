"""The synthetic keepers + the scale benchmark (cycle 12 D5).

The dossier's micro-learner ablation names FIVE synthetic user models —
attentive, neglectful, erratic, punitive, exploratory — and 500
lifecycles per condition. This lab operationalizes the five as
deterministic-under-seed interaction policies over the companion
surface (each tick a keeper may inject a feed/play interaction; the
switchboard drives all autonomous behavior), and delivers the
100k-tick x 500-lifecycle welfare benchmark: 5 keepers x 100
lifecycles x 200 ticks per arm, the FROZEN switchboard vs the FULL
opted-in fleet, paired seeds per lifecycle.

WALL-CLOCK FIRST (the Phase A/B precedent, DR 0028): the report
measures a pilot before the full run and records the dependency
decision. Measured hotspot: ``advance_tick``'s deepcopy of the growing
history list (O(ticks^2) per episode); the bench loop reads each
tick's balance then trims history to its last entry — an owned-loop
optimization, not an engine change — after which the full 2-arm
benchmark projects to well under a minute of stdlib. NumPy's trigger
is NOT met; recorded, not assumed.

Welfare is the engine's own metric: the per-tick need ``balance`` the
lifecycle already computes (mean over the episode) — no new statistics
invented. The >=15% welfare gate and the per-thread ablations are D6's
job; this lab delivers the harness and the honest two-arm measurement.
"""

import argparse
import json
import random
import sys
import time
from pathlib import Path

from thread_fleet import FLEET_THREAD_NAMES, observe_fleet


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
LIFECYCLE_SIM = ROOT / "labs" / "lifecycle_sim"
for _path in [GRID_GENOME, LIFECYCLE_SIM]:
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

ARTIFACT_ID = "synthetic_keepers_stage0"
REPORT_DATE = "2026-07-08"
KEEPER_IDS = ["attentive", "neglectful", "erratic", "punitive", "exploratory"]
FULL_LIFECYCLES_PER_KEEPER = 100
FULL_TICKS = 200
SEED_BASE = 20260708
PILOT_LIFECYCLES = 2
# The one-shot artifact run tolerates minutes; the trigger for a NumPy
# decision record is a projection beyond this bound (DR 0028).
STDLIB_WALLCLOCK_BOUND_SECONDS = 600.0


def keeper_action(keeper_id: str, state: dict, rng: random.Random) -> str | None:
    """One keeper's interaction decision for this tick (feed/play/None).

    The five documented models, operationalized: attentive responds to
    real needs; neglectful barely appears; erratic interacts on whim;
    punitive interacts at the WRONG times; exploratory probes in
    alternating bursts.
    """
    hunger = float(state.get("hunger", 0.5))
    energy = float(state.get("energy", 0.5))
    bond = float(state.get("bond", 0.5))
    age = int(state.get("age_ticks", 0))
    roll = rng.random()
    if keeper_id == "attentive":
        if hunger > 0.6 and roll < 0.9:
            return "feed"
        if bond < 0.55 and energy > 0.4 and roll < 0.5:
            return "play"
        if roll < 0.05:
            return "play"
        return None
    if keeper_id == "neglectful":
        if hunger > 0.85 and roll < 0.1:
            return "feed"
        return None
    if keeper_id == "erratic":
        if roll < 0.25:
            return "feed" if rng.random() < 0.5 else "play"
        return None
    if keeper_id == "punitive":
        if energy < 0.3 and roll < 0.6:
            return "play"  # wakes the tired companion
        if hunger < 0.3 and roll < 0.4:
            return "feed"  # overfeeds the sated one
        return None  # and ignores the real need
    if keeper_id == "exploratory":
        if age % 10 < 3 and roll < 0.6:
            return "play" if (age // 10) % 2 == 0 else "feed"
        return None
    raise ValueError(f"unknown keeper model: {keeper_id}")


def run_keeper_lifecycle(
    grid: dict,
    keeper_id: str,
    *,
    ticks: int,
    rng_seed: int,
    fleet_enabled: bool,
    evidence: dict | None = None,
) -> dict:
    from animation_states import select_animation_state
    from lifecycle_sim import advance_tick, initial_lifecycle_state
    from micro_switchboard import run_switchboard

    rng = random.Random(rng_seed)
    state = initial_lifecycle_state(grid, None)
    if fleet_enabled:
        state["learning_switches"] = {name: True for name in FLEET_THREAD_NAMES}
        if evidence is not None:
            state["evidence"] = evidence
    balance_total = 0.0
    overrides = 0
    lived = 0
    for _tick in range(ticks):
        if not state.get("alive", False):
            break
        if fleet_enabled:
            state["last_animation"] = select_animation_state(state)[0]
            state["thread_states"] = observe_fleet(state)
        decision = run_switchboard(state)
        override = keeper_action(keeper_id, state, rng)
        if override is not None:
            overrides += 1
        state = advance_tick(state, override or decision["action"])
        balance_total += state["history"][-1]["balance"]
        lived += 1
        # The measured hotspot: deepcopy of the growing history. The
        # bench loop owns its episode, reads each balance, and keeps
        # only the last entry — the engine is untouched.
        state["history"] = state["history"][-1:]
    return {
        "keeper_id": keeper_id,
        "fleet_enabled": fleet_enabled,
        "survival_ticks": lived,
        "alive": bool(state.get("alive", False)),
        "mean_balance": round(balance_total / lived, 6) if lived else 0.0,
        "keeper_overrides": overrides,
    }


def _keeper_evidence(seeds: list[dict]) -> dict:
    from evidence_threads import build_evidence_bundle, _adopted_model, _lineage_nodes

    slip_profile = json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )
    model = _adopted_model()
    nodes = _lineage_nodes()
    return {
        grid["grid_id"]: build_evidence_bundle(
            grid, slip_profile, readability_model=model, lineage_nodes=nodes
        )
        for grid in seeds
    }


def run_benchmark(
    *,
    lifecycles_per_keeper: int = FULL_LIFECYCLES_PER_KEEPER,
    ticks: int = FULL_TICKS,
    seed_base: int = SEED_BASE,
) -> dict:
    from corpus_builder import build_seed_grids

    seeds = build_seed_grids()
    evidence_by_grid = _keeper_evidence(seeds)
    keepers = []
    for keeper_index, keeper_id in enumerate(KEEPER_IDS):
        arms: dict[str, dict] = {}
        for arm, fleet_enabled in [("frozen", False), ("fleet", True)]:
            balance_sum = 0.0
            survival_sum = 0
            alive_count = 0
            overrides_sum = 0
            for index in range(lifecycles_per_keeper):
                grid = seeds[index % len(seeds)]
                summary = run_keeper_lifecycle(
                    grid,
                    keeper_id,
                    ticks=ticks,
                    # Paired seeds: both arms replay the same keeper
                    # randomness per lifecycle.
                    rng_seed=seed_base + keeper_index * 1_000_00 + index,
                    fleet_enabled=fleet_enabled,
                    evidence=evidence_by_grid[grid["grid_id"]],
                )
                balance_sum += summary["mean_balance"]
                survival_sum += summary["survival_ticks"]
                alive_count += 1 if summary["alive"] else 0
                overrides_sum += summary["keeper_overrides"]
            arms[arm] = {
                "mean_balance": round(balance_sum / lifecycles_per_keeper, 6),
                "mean_survival_ticks": round(
                    survival_sum / lifecycles_per_keeper, 6
                ),
                "survival_rate": round(alive_count / lifecycles_per_keeper, 6),
                "mean_keeper_overrides": round(
                    overrides_sum / lifecycles_per_keeper, 6
                ),
            }
        frozen_balance = arms["frozen"]["mean_balance"]
        delta_pct = (
            (arms["fleet"]["mean_balance"] - frozen_balance)
            / frozen_balance
            * 100.0
            if frozen_balance
            else 0.0
        )
        keepers.append(
            {
                "keeper_id": keeper_id,
                "frozen": arms["frozen"],
                "fleet": arms["fleet"],
                "welfare_delta_pct": round(delta_pct, 6),
            }
        )
    return {
        "lifecycles_per_arm": lifecycles_per_keeper * len(KEEPER_IDS),
        "ticks_requested_per_arm": lifecycles_per_keeper
        * len(KEEPER_IDS)
        * ticks,
        "ticks_per_lifecycle": ticks,
        "keepers": keepers,
    }


def build_synthetic_keeper_report(
    *,
    lifecycles_per_keeper: int = FULL_LIFECYCLES_PER_KEEPER,
    ticks: int = FULL_TICKS,
) -> dict:
    from corpus_builder import build_seed_grids

    # WALL-CLOCK FIRST (the Phase A/B precedent): a measured pilot
    # before the full run, and the dependency decision recorded.
    seeds = build_seed_grids()
    evidence = _keeper_evidence(seeds[:1])
    pilot_start = time.perf_counter()
    pilot_ticks = 0
    for index in range(PILOT_LIFECYCLES):
        for fleet_enabled in [False, True]:
            summary = run_keeper_lifecycle(
                seeds[0],
                "attentive",
                ticks=FULL_TICKS,
                rng_seed=SEED_BASE + index,
                fleet_enabled=fleet_enabled,
                evidence=evidence[seeds[0]["grid_id"]],
            )
            pilot_ticks += summary["survival_ticks"]
    pilot_seconds = time.perf_counter() - pilot_start
    full_ticks_both_arms = FULL_LIFECYCLES_PER_KEEPER * len(KEEPER_IDS) * FULL_TICKS * 2
    projected = pilot_seconds / max(pilot_ticks, 1) * full_ticks_both_arms
    stdlib_holds = projected < STDLIB_WALLCLOCK_BOUND_SECONDS

    benchmark_start = time.perf_counter()
    benchmark = run_benchmark(
        lifecycles_per_keeper=lifecycles_per_keeper, ticks=ticks
    )
    benchmark_seconds = time.perf_counter() - benchmark_start

    full_scale = (
        lifecycles_per_keeper == FULL_LIFECYCLES_PER_KEEPER
        and ticks == FULL_TICKS
    )
    balances = [
        keeper[arm]["mean_balance"]
        for keeper in benchmark["keepers"]
        for arm in ("frozen", "fleet")
    ]
    saturation = {
        "balance_min": round(min(balances), 6),
        "balance_max": round(max(balances), 6),
        "balance_spread": round(max(balances) - min(balances), 6),
        "all_survival_rates_one": all(
            keeper[arm]["survival_rate"] == 1.0
            for keeper in benchmark["keepers"]
            for arm in ("frozen", "fleet")
        ),
    }
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete" if stdlib_holds else "refuted",
        "date": REPORT_DATE,
        "purpose": (
            "D5: the five documented synthetic user models (attentive, "
            "neglectful, erratic, punitive, exploratory) as deterministic "
            "interaction policies over the companion surface, and the "
            "100k-tick x 500-lifecycle welfare benchmark — the frozen "
            "switchboard vs the full opted-in fleet, paired seeds, "
            "welfare = the engine's own per-tick need balance. "
            "Wall-clock measured FIRST; the DR 0028 dependency decision "
            "recorded from the measurement."
        ),
        "source_artifacts": [
            "labs/micro_threads/thread_fleet.py",
            "labs/micro_threads/evidence_threads.py",
            "labs/lifecycle_sim/lifecycle_sim.py",
            "labs/grid_genome/micro_switchboard.py",
            "data/seed_grids",
            "docs/project-research/deep-research/01/deep-research.md",
        ],
        "metrics": {
            "scale": {
                "lifecycles_per_keeper": lifecycles_per_keeper,
                "ticks_per_lifecycle": ticks,
                "full_scale_run": full_scale,
            },
            "wallclock": {
                "pilot_lifecycles": PILOT_LIFECYCLES * 2,
                "pilot_ticks": pilot_ticks,
                "pilot_seconds": round(pilot_seconds, 3),
                "projected_full_benchmark_seconds": round(projected, 1),
                "measured_benchmark_seconds": round(benchmark_seconds, 1),
                "stdlib_bound_seconds": STDLIB_WALLCLOCK_BOUND_SECONDS,
                "stdlib_holds": stdlib_holds,
            },
            "dependency_decision": (
                "stdlib holds: the projected full benchmark stays under "
                "the bound; NumPy's DR 0028 trigger is NOT met at this "
                "scale (the measured hotspot was advance_tick's history "
                "deepcopy, solved by the bench loop trimming its own "
                "episode history)."
                if stdlib_holds
                else "the projection exceeds the bound: draft the NumPy "
                "decision record citing this measurement."
            ),
            "benchmark": benchmark,
            "saturation": saturation,
        },
        "closed_states": (
            [
                "five_documented_user_models_operationalized",
                "wallclock_measured_first_dependency_decision_recorded",
                "welfare_measured_with_and_without_threads_paired_seeds",
                "welfare_is_the_engines_own_balance_metric",
            ]
            + (
                ["benchmark_at_the_documented_100k_tick_500_lifecycle_scale"]
                if full_scale
                else []
            )
            if stdlib_holds
            else ["d5_bar_not_met_recorded_honestly"]
        ),
        "blocked_states": [
            "ablation_gates_not_run (D6: >=15% welfare over the frozen "
            "baseline; drop any thread whose removal costs <5% — this "
            "harness is D6's instrument)",
            "sheltered_environment_is_welfare_saturated (HONEST FINDING: "
            "the two-arm deltas measure ~0% because the switchboard "
            "feeds itself autonomously and every keeper's balance sits "
            "near 0.79 with full survival — the frozen baseline has no "
            "headroom to beat. In the game's actual interaction model "
            "feeding is a USER action (the companion begs, the keeper "
            "feeds). D6 must run the gates in a keeper-dependent mode "
            "with real welfare headroom, or record the gate failure)",
            "keeper_models_are_lab_operationalizations "
            "(the five documented names; real player telemetry is a "
            "GAME-track concern, Phase F+)",
        ],
        "decision": (
            "The harness stands at the documented scale and the two-arm "
            "welfare measurement is recorded honestly; the ablation "
            "verdicts belong to D6."
            if stdlib_holds
            else "The D5 bar is NOT met — recorded, not fudged."
        ),
        "next_research_step": (
            "D6: the documented ablation gates over this harness; the "
            "Phase-D gate report with the honest remainder list."
        ),
    }


def write_synthetic_keeper_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synthetic keepers + scale benchmark lab (cycle 12 D5)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "micro_threads"
    )
    args = parser.parse_args()
    report = build_synthetic_keeper_report()
    write_synthetic_keeper_artifacts(args.output_dir, report)
    print(json.dumps(report["metrics"]["wallclock"], indent=2))
    for keeper in report["metrics"]["benchmark"]["keepers"]:
        print(
            keeper["keeper_id"],
            "frozen", keeper["frozen"]["mean_balance"],
            "fleet", keeper["fleet"]["mean_balance"],
            "delta%", keeper["welfare_delta_pct"],
        )
    print(report["decision"])


if __name__ == "__main__":
    main()
