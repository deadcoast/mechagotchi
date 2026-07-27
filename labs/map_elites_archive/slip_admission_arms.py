"""Cycle 23 M3: the unbreedable bootstrap elites, and what fixing them costs.

L1 measured the mechanism exactly and deliberately did **not** fix it:
all 4,435 generation refusals are the SLIP rejecting the **parent**;
100% of those parents are **bootstrap** creatures (the corpus generators
build them without ever being handed the profile); they win niches on
fitness, hold them because only a fitter same-niche candidate displaces
them, and are round-robined as parents forever — a flat 38-per-generation
tax that never improves. M1 then sized the population exactly:
**48 of 460 elites (10.4%) are bootstrap creatures.**

L1 refused to patch it because **the fix trades against coverage**, and
the three candidate changes are not equivalent:

* ``bootstrap`` — admit only SLIP-legal creatures into the bootstrap
  population. The least surgical: it changes what the archive is seeded
  from, so niches only a rejected creature could have reached are never
  filled at all.
* ``insertion`` — admit only SLIP-legal creatures into the **archive**.
  A niche whose only occupant is SLIP-illegal goes **EMPTY**. This is
  where the coverage trade bites hardest and most directly.
* ``parents`` — keep the archive exactly as it is, but breed only legal
  elites. Costs no niche by construction; costs parent diversity
  instead, which may cost coverage indirectly.

"Fixing" the refusals could therefore lower the **0.8984** coverage
DR 0042 just adopted. So the arms are measured, never blended, and
**refusal is first-class**.

THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN.

* **G1 — the cause is eliminated**: ``refusals == 0``. This bar is
  **structural, not tuned**: L1 proved 100% of refusals are SLIP-illegal
  parents, so an arm that removes the cause must reach **exactly zero**.
  A "90% reduction" bar would be a number nobody derived. An arm that
  reduces refusals without eliminating them is *partial*, and is
  reported with its measured number rather than rounded up to success.
* **G2 — coverage is preserved**: the arm's coverage cost must not
  exceed the **MEASURED** coverage control — the loop's own seed-to-seed
  coverage variation, measured here by running the incumbent at two
  seeds. **Never a constant.** A coverage *gain* is never penalised.
* **Adopt** only an arm passing BOTH. If several pass, the tie-break is
  **least-invasive-first** (``INVASIVENESS_ORDER``), fixed before the
  run so it cannot be chosen to suit the result: ``parents`` changes
  only who breeds, ``insertion`` changes what the archive holds,
  ``bootstrap`` changes what it starts from.

**Nothing is adopted by this module.** It measures the arms and applies
the rule; changing the loop's default is a decision record's job, and
the incumbent stays runnable and byte-identical either way.
"""

import argparse
import json
import sys
import time
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
for _sub in ("labs/map_elites_archive", "labs/grid_genome"):
    _path = str(ROOT / _sub)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from evaluation_loop_scale import (  # noqa: E402
    DEFAULT_LIFECYCLE_TICKS,
    DEFAULT_RNG_SEED,
    PRE_REGISTERED_BOUND_S as LOOP_BOUND_S,
    _load_default_slip,
    run_evaluation_loop,
)
from niche_scale_archive import EVALUATION_STREAM_OFFSET  # noqa: E402

from slip import is_grid_aligned  # noqa: E402

ARTIFACT_ID = "slip_admission_arms_stage0"
REPORT_DATE = "2026-07-27"

ARMS = ("bootstrap", "insertion", "parents")

# Fixed BEFORE the run: least invasive first. `parents` changes only who
# breeds; `insertion` changes what the archive holds; `bootstrap`
# changes what it starts from.
INVASIVENESS_ORDER = ("parents", "insertion", "bootstrap")

# This study runs the loop five times: the incumbent at two seeds (the
# measured coverage control) plus one run per arm. The bound is DERIVED
# from the loop's own registered bound rather than picked (DR 0028).
PRE_REGISTERED_BOUND_S = 5 * LOOP_BOUND_S

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 23 M3), refusal first-class: an arm is "
    "ADOPTABLE only if it passes BOTH gates. G1 — the cause is "
    "eliminated: refusals == exactly zero, a STRUCTURAL bar because L1 "
    "proved 100% of refusals are SLIP-illegal parents, so removing the "
    "cause must reach zero (a percentage-reduction bar would be a "
    "number nobody derived). G2 — coverage is preserved: the arm's "
    "coverage cost must not exceed the MEASURED coverage control, the "
    "loop's own seed-to-seed variation measured by running the "
    "incumbent at two seeds, never a constant; a coverage GAIN is never "
    "penalised. Among passing arms the winner is the least invasive "
    f"({' < '.join(INVASIVENESS_ORDER)}), fixed before the run. This "
    "module adopts nothing: changing the loop's default is a decision "
    "record's job."
)


def slip_legal(grid: dict, slip_profile: dict | None) -> bool:
    """The generation arm's OWN predicate — imported, never re-implemented.

    ``_acceptable`` treats a missing profile as "no constraint"; the
    arms must agree, or an unprofiled run would silently change meaning.
    """
    if slip_profile is None:
        return True
    return is_grid_aligned(grid, slip_profile).ok


def arm_is_adoptable(
    *, refusals: int, coverage_cost: float, coverage_control: float
) -> dict:
    """Apply the pre-registered rule. Both outcomes are first-class."""
    if coverage_control <= 0.0:
        raise ValueError(
            "the coverage control must be positive — a zero control "
            "would make every coverage cost fatal; measure it, never "
            "assume it"
        )
    cause_eliminated = refusals == 0
    coverage_preserved = coverage_cost <= coverage_control
    failed: list[str] = []
    if not cause_eliminated:
        failed.append("G1_cause_eliminated")
    if not coverage_preserved:
        failed.append("G2_coverage_preserved")
    return {
        "adoptable": not failed,
        "failed_gates": failed,
        "refusals": refusals,
        "cause_eliminated": cause_eliminated,
        "coverage_cost": round(coverage_cost, 6),
        "coverage_control": round(coverage_control, 6),
        "coverage_preserved": coverage_preserved,
        "rule": PRE_REGISTERED_RULE,
    }


def _run(
    *,
    slip_admission: str,
    population: int,
    target_evaluations: int,
    rng_seed: int,
    lifecycle_ticks: int,
) -> dict:
    result = run_evaluation_loop(
        population=population,
        target_evaluations=target_evaluations,
        rng_seed=rng_seed,
        lifecycle_ticks=lifecycle_ticks,
        generation="constrained",
        slip_admission=slip_admission,
        collect_refusals=True,
        collect_elite_grids=True,
    )
    summary = result["archive_summary"]
    collection = result["elite_grid_collection"]
    origins = {"bootstrap": 0, "loop_offspring": 0}
    for record in collection["elites"]:
        origins[record["origin"]] += 1
    slip_profile = _load_default_slip()
    illegal_elites = sum(
        1
        for record in collection["elites"]
        if not slip_legal(record["grid"], slip_profile)
    )
    measured = {
        "slip_admission": slip_admission,
        "occupied_niches": summary["occupied_niches"],
        "coverage": summary["coverage"],
        "qd_score": summary["qd_score"],
        "best_fitness": summary["best_fitness"],
        "evaluations_total": result["evaluations_total"],
        "generations_run": len(result["trajectory"]),
        "refusals": len(result["refusal_collection"]["records"]),
        "generation_attempts_total": result["refusal_collection"][
            "generation_attempts_total"
        ],
        "bootstrap_admitted": result["bootstrap_admitted"],
        "elite_origin_counts": origins,
        "slip_illegal_elites": illegal_elites,
    }
    if "parent_fallback_generations" in result:
        measured["parent_fallback_generations"] = result[
            "parent_fallback_generations"
        ]
    return measured


def build_slip_admission_report(
    *,
    population: int = 256,
    target_evaluations: int = 20_480,
    rng_seed: int = DEFAULT_RNG_SEED,
    control_rng_seed: int = DEFAULT_RNG_SEED + EVALUATION_STREAM_OFFSET,
    lifecycle_ticks: int = DEFAULT_LIFECYCLE_TICKS,
) -> dict:
    started = time.perf_counter()
    common = dict(
        population=population,
        target_evaluations=target_evaluations,
        lifecycle_ticks=lifecycle_ticks,
    )

    # The incumbent at two seeds: the baseline every arm is measured
    # against, and the MEASURED coverage control.
    baseline = _run(slip_admission="none", rng_seed=rng_seed, **common)
    baseline_control = _run(
        slip_admission="none", rng_seed=control_rng_seed, **common
    )
    coverage_control = round(
        abs(baseline["coverage"] - baseline_control["coverage"]), 6
    )

    arms: dict[str, dict] = {}
    for name in ARMS:
        measured = _run(slip_admission=name, rng_seed=rng_seed, **common)
        coverage_cost = round(baseline["coverage"] - measured["coverage"], 6)
        judged = arm_is_adoptable(
            refusals=measured["refusals"],
            coverage_cost=coverage_cost,
            coverage_control=coverage_control,
        )
        arms[name] = {
            **measured,
            "coverage_cost": coverage_cost,
            "niches_lost": baseline["occupied_niches"]
            - measured["occupied_niches"],
            "refusals_removed": baseline["refusals"] - measured["refusals"],
            "adoptable": judged["adoptable"],
            "failed_gates": judged["failed_gates"],
            "cause_eliminated": judged["cause_eliminated"],
            "coverage_preserved": judged["coverage_preserved"],
        }

    adoptable = [name for name in ARMS if arms[name]["adoptable"]]
    adopted = next(
        (name for name in INVASIVENESS_ORDER if name in adoptable), None
    )
    wall_clock_s = round(time.perf_counter() - started, 3)

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 23 M3: measure what each of the three candidate fixes "
            "for the unbreedable bootstrap elites COSTS in coverage, "
            "against a measured control, with refusal first-class — "
            "L1's named fix, deliberately not taken there because it "
            "trades against the coverage DR 0042 adopted."
        ),
        "source_artifacts": [
            "data/archives/generation_refusal_causes_stage0.json",
            "data/archives/elite_population_measures_stage0.json",
            "data/archives/lineage_dominance_stage0.json",
            "data/archives/generation_arm_evolution_stage0.json",
            "data/archives/evaluation_loop_scale_stage0.json",
        ],
        "parameters": {
            "population": population,
            "target_evaluations": target_evaluations,
            "rng_seed": rng_seed,
            "control_rng_seed": control_rng_seed,
            "lifecycle_ticks": lifecycle_ticks,
            "generation": "constrained (the DR 0042 adopted default)",
            "selection": "novelty_first (the DR 0040 adopted default)",
            "arms": list(ARMS),
            "invasiveness_order": list(INVASIVENESS_ORDER),
            "slip_profile": "data/slips/valid/slip_lcd_seed.json",
        },
        "metrics": {
            "baseline": baseline,
            "baseline_control": baseline_control,
            "coverage_control": coverage_control,
            "arms": arms,
            "wall_clock_s": wall_clock_s,
            "pre_registered_bound_s": PRE_REGISTERED_BOUND_S,
            "within_bound": wall_clock_s <= PRE_REGISTERED_BOUND_S,
        },
        "closed_states": [
            "the three candidate fixes are separated and measured "
            "independently — never blended into one 'fix'",
            "the coverage bar is the loop's own MEASURED seed-to-seed "
            "variation, not a constant",
            "G1 is structural (exactly zero refusals), derived from L1's "
            "measured mechanism rather than picked as a percentage",
            "the SLIP predicate is the generation arm's own, imported "
            "and never re-implemented, so no arm can admit a creature "
            "the generator would refuse",
            "every arm's coverage cost is reported, including refused "
            "arms — a refused arm's cost is the evidence for refusing it",
        ],
        "blocked_states": [
            "this module ADOPTS NOTHING: it measures the arms and "
            "applies the rule. Changing the loop's default is a "
            "decision record's job, and the incumbent stays runnable "
            "and byte-identical when the arm is off",
            "one seed per arm against a two-seed control; a "
            "distributional claim about any arm's cost needs E4's "
            "ten-seed protocol",
            "the arms are measured under ONE SLIP profile "
            "(slip_lcd_seed). A profile with a wider palette would "
            "reject fewer bootstrap creatures and could change every "
            "cost here — the numbers are this covenant's, not the "
            "mechanism's in general",
            "coverage and QD are incumbent-geometry numbers (DR 0046's "
            "comparability rule): they may not be read against "
            "reachability or support counts, which live in the probe "
            "geometry",
        ],
        "decision": {
            "adopted_arm": adopted,
            "adoptable_arms": adoptable,
            "coverage_control": coverage_control,
            "per_arm": {
                name: {
                    "adoptable": arms[name]["adoptable"],
                    "failed_gates": arms[name]["failed_gates"],
                    "refusals": arms[name]["refusals"],
                    "coverage_cost": arms[name]["coverage_cost"],
                    "niches_lost": arms[name]["niches_lost"],
                }
                for name in ARMS
            },
            "rule": PRE_REGISTERED_RULE,
        },
        "next_research_step": (
            "M4: ancestry versus morphology — do Phase E's 52 recurrent "
            "families share ancestors, or converge from different "
            "founder lines? (Evolution Q3.)"
        ),
    }


def write_slip_admission_artifacts(
    output_dir: str | Path, report: dict
) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{ARTIFACT_ID}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(ROOT / "data" / "archives"))
    parser.add_argument("--population", type=int, default=256)
    parser.add_argument("--target-evaluations", type=int, default=20_480)
    parser.add_argument("--rng-seed", type=int, default=DEFAULT_RNG_SEED)
    args = parser.parse_args()

    report = build_slip_admission_report(
        population=args.population,
        target_evaluations=args.target_evaluations,
        rng_seed=args.rng_seed,
    )
    metrics, decision = report["metrics"], report["decision"]
    base = metrics["baseline"]
    print(
        f"baseline: coverage {base['coverage']} ({base['occupied_niches']} "
        f"niches), {base['refusals']} refusals, "
        f"{base['slip_illegal_elites']} SLIP-illegal elites"
    )
    print(f"measured coverage control: {metrics['coverage_control']}")
    for name in ARMS:
        arm = metrics["arms"][name]
        print(
            f"  {name:10} coverage {arm['coverage']:.6f} "
            f"(cost {arm['coverage_cost']:+.6f}, {arm['niches_lost']:+d} niches) "
            f"refusals {arm['refusals']:5d} -> "
            f"{'ADOPTABLE' if arm['adoptable'] else 'refused ' + str(arm['failed_gates'])}"
        )
    print(
        f"ADOPTED ARM: {decision['adopted_arm'] or 'NONE — every arm refused'}"
    )
    for path in write_slip_admission_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
