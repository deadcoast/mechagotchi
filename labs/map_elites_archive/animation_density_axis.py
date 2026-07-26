"""Cycle 22 L4: animation_density judged as a CANDIDATE descriptor axis.

`research.md:616-629` lists ten intended niche axes and the dossier's
own worked archive entry (`deep-research.md:526-532`) shows a FOUR-axis
descriptor:

    "descriptor": {
      "symmetry": 0.78, "visual_complexity": 0.41,
      "neediness": 0.29, "animation_density": 0.63
    }

The engine carries three (baseline) / six (extended) and no animation
axis. Since Phase C/H built the clip model, one is now derivable from
engine truth — which is why the Phase-K gate named it.

**THE DEFINITION IS CHOSEN, NOT DOCUMENTED — and that is stated first.**
`animation_density` appears in the documentation exactly once, as a
value in a JSON example, with no formula, no range and no threshold
anywhere. So this module does not "implement the documented axis"; it
proposes one, grounded in the engine's own clip tables, and asks
whether it earns a place. Presenting a chosen definition as a
documented one would be the same class of error L1 caught in K2.

**The definition** (potential animation):

    animation_density(grid) = |cells whose role the clip model animates|
                              / |live cells|

The animating role set is READ FROM `clip_model` at import — sway,
flicker, limb-step, joint-flex and decoration-bob roles — never copied,
so a change to the engine's clip tables moves this axis with it.

Its limitation is named, not hidden: this measures the animation the
engine WOULD apply. Per-cell offsets are skipped on collision or bounds
(`_apply_role_offsets`), so a creature can carry animating roles that
never actually move. `realised_idle_density` is reported alongside as
an OBSERVATION — measured over the idle clip, which is the one clip
with zero whole-body translation, so displacement needs no correction.

THE GATES ARE PRE-REGISTERED HERE, BEFORE ANY RUN, with refusal
first-class:

* **A1 spread** — the axis must support 8 distinct octile edges on the
  derivation population, the same `supports_full_bins` test every
  incumbent axis passes. A degenerate axis wastes a dimension.
* **A2 independence** — `|Pearson r|` against every incumbent axis must
  stay below ``INDEPENDENCE_BAR``. An axis that restates symmetry adds
  a dimension without adding information.
* **A3 discrimination** — among population pairs sharing the SAME
  three-axis bin, at least ``DISCRIMINATION_BAR`` must land in
  different animation octiles. This is the axis's whole purpose: to
  separate creatures the incumbent geometry cannot tell apart.
* **A4 coverage cost** — REPORTED, never gated: a fourth axis takes the
  space from 8³ = 512 cells to 8⁴ = 4096, so the same population is
  spread eight times thinner. Adoption must weigh this, and the number
  is put in the artifact rather than left for the reader to derive.

**AND THE DOCUMENTED SELECTION CRITERION IS BLOCKED, NOT SUBSTITUTED.**
`deep-research.md:204` requires a descriptor set "selected with
inter-rater interpretability >= 0.7" — an inter-rater measure, which
needs the owner-deferred human panel. No machine proxy is offered in
its place. The best verdict this study can reach is therefore
``adoptable_pending_blocked_clause``: the machine-side gates can pass,
and the documented criterion still cannot be met without humans.

**Which geometry would it join?** L3 found the repo runs two. This axis
is judged against the INCUMBENT geometry — the frozen train-derived
edges that `evaluation_loop_scale` and `coverage_qd_gates` consume —
because that is where coverage and QD are reported.
"""

import argparse
import json
import sys
import time
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
for sub in ("labs/map_elites_archive", "labs/animation_system"):
    path = str(ROOT / sub)
    if path not in sys.path:
        sys.path.insert(0, path)

from niche_scale_archive import (  # noqa: E402
    DEFAULT_RNG_SEED,
    SCALE_BINS_PER_AXIS,
    SCALE_DESCRIPTOR_NAMES,
    build_population,
    derive_scale_bin_edges,
    edge_diagnostics,
    scale_axis_values,
    scale_descriptor_for_values,
    _load_default_slip,
)
from corpus_builder import build_seed_grids_16  # noqa: E402
from wfc_grid import split_corpus, train_wfc_model  # noqa: E402
from wfc_population_throughput import load_frozen_scale_edges  # noqa: E402

from clip_model import (  # noqa: E402
    DECOR_BOB_ROLES,
    FLICKER_ROLES,
    JOINT_FLEX_ROLES,
    LIMB_STEP_ROLES,
    SWAY_ROLES,
    clip_frames,
)

ARTIFACT_ID = "animation_density_axis_stage0"
REPORT_DATE = "2026-07-26"

# Read from the engine's clip tables, never copied (pinned).
ANIMATING_ROLES = frozenset(
    set(SWAY_ROLES)
    | set(FLICKER_ROLES)
    | set(LIMB_STEP_ROLES)
    | set(JOINT_FLEX_ROLES)
    | set(DECOR_BOB_ROLES)
)

# Pre-registered bars (see the module docstring).
INDEPENDENCE_BAR = 0.5
DISCRIMINATION_BAR = 0.2

# L3: the repo runs two geometries. This candidate is judged against
# the one coverage and QD are reported in.
TARGET_GEOMETRY = "incumbent (frozen train-derived edges)"

DEFINITION_PROVENANCE = (
    "CHOSEN by this lab, not documented. `animation_density` appears in "
    "the documentation exactly once — as a value in the worked archive "
    "entry at deep-research.md:530 — with no formula, range or "
    "threshold anywhere. This module proposes a definition grounded in "
    "the engine's own clip tables and asks whether it earns a place; it "
    "does not claim to implement a documented one."
)

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 22 L4), refusal first-class: A1 the axis "
    "must support 8 distinct octile edges; A2 |Pearson r| against every "
    f"incumbent axis < {INDEPENDENCE_BAR}; A3 at least "
    f"{DISCRIMINATION_BAR} of same-3-axis-bin pairs must land in "
    "different animation octiles. A4 (coverage cost) is REPORTED, never "
    "gated. Even with A1-A3 all passing the verdict is at best "
    "'adoptable_pending_blocked_clause', because the documented "
    "selection criterion (inter-rater interpretability >= 0.7, "
    "deep-research.md:204) needs the owner-deferred human panel and NO "
    "proxy is substituted for it."
)


def animation_density(grid: dict) -> float:
    """The fraction of live cells the engine's clip model animates."""
    cells = grid.get("cells") or []
    if not cells:
        raise ValueError(
            "animation_density needs at least one live cell: "
            f"{grid.get('grid_id')!r} has none"
        )
    animating = sum(1 for cell in cells if cell.get("role") in ANIMATING_ROLES)
    return round(animating / len(cells), 6)


def realised_idle_density(grid: dict) -> float:
    """Cells that actually vacate their home position during `idle`.

    An OBSERVATION, never the axis. Measured over `idle` because it is
    the one clip whose whole-body translation is zero at every frame,
    so displacement needs no correction; collision and bounds skips are
    therefore visible as the gap against the potential measure.
    """
    cells = grid.get("cells") or []
    if not cells:
        raise ValueError("realised_idle_density needs at least one live cell")
    home = {(cell["x"], cell["y"]) for cell in cells}
    vacated: set[tuple[int, int]] = set()
    for frame in clip_frames(grid, "idle"):
        occupied = {(cell["x"], cell["y"]) for cell in frame["cells"]}
        vacated |= home - occupied
    return round(len(vacated) / len(cells), 6)


def pearson(xs: list[float], ys: list[float]) -> float | None:
    """Stdlib Pearson r, or None when either series has no variance.

    Returning 0.0 for a constant series would launder a degenerate axis
    into an independent-looking one, so the undefined case says so.
    """
    n = len(xs)
    if n != len(ys) or n < 2:
        raise ValueError("pearson needs two equal series of length >= 2")
    mean_x, mean_y = sum(xs) / n, sum(ys) / n
    dx = [x - mean_x for x in xs]
    dy = [y - mean_y for y in ys]
    var_x = sum(d * d for d in dx)
    var_y = sum(d * d for d in dy)
    if var_x <= 0.0 or var_y <= 0.0:
        return None
    return sum(a * b for a, b in zip(dx, dy)) / ((var_x**0.5) * (var_y**0.5))


def judge_axis(
    *, supports_full_bins: bool, max_abs_correlation: float, discrimination: float
) -> dict:
    """Apply the pre-registered rule. Refusal is first-class."""
    failed: list[str] = []
    if not supports_full_bins:
        failed.append("spread")
    if max_abs_correlation >= INDEPENDENCE_BAR:
        failed.append("independence")
    if discrimination < DISCRIMINATION_BAR:
        failed.append("discrimination")
    return {
        "verdict": "refuse" if failed else "adoptable_pending_blocked_clause",
        "failed_gates": failed,
        "interpretability_clause_blocked": True,
        "blocked_clause": (
            "deep-research.md:204 — 'descriptor set selected with "
            "inter-rater interpretability >= 0.7'. An inter-rater "
            "measure needs the owner-deferred human panel; no proxy is "
            "substituted."
        ),
        "rule": PRE_REGISTERED_RULE,
    }


def _bin_of(value: float, edges: list[float]) -> int:
    index = 0
    while index < len(edges) and value >= edges[index]:
        index += 1
    return index


def build_animation_density_report(
    *, population_count: int = 600, rng_seed: int = DEFAULT_RNG_SEED
) -> dict:
    started = time.perf_counter()
    slip_profile = _load_default_slip()
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    wfc_model = train_wfc_model(train)
    population, composition = build_population(
        population_count, rng_seed, train, wfc_model
    )

    density = [animation_density(grid) for grid in population]
    realised = [realised_idle_density(grid) for grid in population]
    incumbent = {
        name: [
            scale_axis_values(grid, slip_profile=slip_profile)[name]
            for grid in population
        ]
        for name in SCALE_DESCRIPTOR_NAMES
    }

    # A1 — spread, by the same test the incumbent axes pass.
    density_edges = derive_scale_bin_edges(density)
    diagnostics = edge_diagnostics(density, density_edges)

    # A2 — independence against every incumbent axis.
    correlations = {
        name: pearson(density, incumbent[name]) for name in SCALE_DESCRIPTOR_NAMES
    }
    measured = [abs(r) for r in correlations.values() if r is not None]
    max_abs_correlation = max(measured) if measured else 0.0

    # A3 — discrimination: among population members sharing the SAME
    # three-axis bin under the INCUMBENT geometry, how often does the
    # animation octile differ? Measured over every same-bin pair.
    frozen = load_frozen_scale_edges()
    groups: dict[tuple[int, ...], list[int]] = {}
    for index, grid in enumerate(population):
        values = {name: incumbent[name][index] for name in SCALE_DESCRIPTOR_NAMES}
        groups.setdefault(scale_descriptor_for_values(values, frozen), []).append(
            index
        )
    density_octile = [_bin_of(value, density_edges) for value in density]
    same_bin_pairs = 0
    split_pairs = 0
    for members in groups.values():
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                same_bin_pairs += 1
                if density_octile[members[i]] != density_octile[members[j]]:
                    split_pairs += 1
    discrimination = (
        round(split_pairs / same_bin_pairs, 6) if same_bin_pairs else 0.0
    )

    # A4 — the coverage cost, reported not gated.
    occupied_3 = len(groups)
    occupied_4 = len(
        {
            (*bin3, density_octile[index])
            for bin3, members in groups.items()
            for index in members
        }
    )
    cells_3 = SCALE_BINS_PER_AXIS ** len(SCALE_DESCRIPTOR_NAMES)
    cells_4 = cells_3 * SCALE_BINS_PER_AXIS

    judged = judge_axis(
        supports_full_bins=diagnostics["supports_full_bins"],
        max_abs_correlation=max_abs_correlation,
        discrimination=discrimination,
    )
    wall_clock_s = round(time.perf_counter() - started, 3)

    realised_gap = round(
        sum(d - r for d, r in zip(density, realised)) / len(density), 6
    )

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 22 L4: propose and judge animation_density as a "
            "candidate fourth descriptor axis — the documented "
            "four-axis descriptor's missing member and Evolution Q2's "
            "open half."
        ),
        "source_artifacts": [
            "data/archives/niche_scale_archive_stage0.json",
            "data/archives/geometry_consistency_stage0.json",
            "data/animation_system/clip_model_stage0.json",
        ],
        "parameters": {
            "population_count": population_count,
            "rng_seed": rng_seed,
            "composition": composition,
            "animating_roles": sorted(ANIMATING_ROLES),
        },
        "metrics": {
            "definition_provenance": DEFINITION_PROVENANCE,
            "target_geometry": TARGET_GEOMETRY,
            "edges": density_edges,
            "edge_diagnostics": diagnostics,
            "correlation_with_incumbent": {
                name: (None if r is None else round(r, 6))
                for name, r in correlations.items()
            },
            "max_abs_correlation": round(max_abs_correlation, 6),
            "discrimination": discrimination,
            "same_bin_pairs": same_bin_pairs,
            "split_pairs": split_pairs,
            "coverage_cost": {
                "cells_3_axis": cells_3,
                "cells_4_axis": cells_4,
                "occupied_3_axis": occupied_3,
                "occupied_4_axis": occupied_4,
                "coverage_3_axis": round(occupied_3 / cells_3, 6),
                "coverage_4_axis": round(occupied_4 / cells_4, 6),
            },
            "realised_idle_density_mean": round(
                sum(realised) / len(realised), 6
            ),
            "potential_minus_realised_mean": realised_gap,
            "wall_clock_s": wall_clock_s,
        },
        "closed_states": [
            "the axis is derived from the engine's own clip tables, read "
            "at import rather than copied",
            "the definition is declared CHOSEN, since the documentation "
            "names the axis without ever defining it",
            "the coverage cost of a fourth axis is reported in the "
            "artifact, not left for the reader to derive",
        ],
        "blocked_states": [
            "the documented selection criterion — inter-rater "
            "interpretability >= 0.7 (deep-research.md:204) — needs the "
            "owner-deferred human panel. It is BLOCKED, and no machine "
            "proxy is substituted for it; adoption cannot be claimed",
            "the axis measures POTENTIAL animation: per-cell offsets are "
            "skipped on collision or bounds, so a carried animating role "
            "may never move. realised_idle_density bounds that gap as an "
            "observation over the one clip with no body translation",
            "judged on the derivation population, not on the loop's "
            "elites; a candidate axis measured on what the archive is "
            "FILLED with is its own slice (L3's open question)",
        ],
        "decision": judged,
        "next_research_step": (
            "L5: density-as-pressure, decided by its consumer (DR 0043 "
            "clause 2)."
        ),
    }


def write_animation_density_artifacts(
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
    parser.add_argument("--population-count", type=int, default=600)
    args = parser.parse_args()

    report = build_animation_density_report(
        population_count=args.population_count
    )
    metrics, decision = report["metrics"], report["decision"]
    print(f"verdict: {decision['verdict'].upper()}")
    if decision["failed_gates"]:
        print(f"  failed gates: {decision['failed_gates']}")
    print(f"  A1 supports_full_bins : {metrics['edge_diagnostics']['supports_full_bins']}")
    print(f"  A2 correlations       : {metrics['correlation_with_incumbent']}")
    print(f"  A3 discrimination     : {metrics['discrimination']} "
          f"({metrics['split_pairs']}/{metrics['same_bin_pairs']} same-bin pairs)")
    cost = metrics["coverage_cost"]
    print(f"  A4 coverage cost      : {cost['occupied_3_axis']}/{cost['cells_3_axis']} "
          f"({cost['coverage_3_axis']}) -> {cost['occupied_4_axis']}/{cost['cells_4_axis']} "
          f"({cost['coverage_4_axis']})")
    print(f"  realised idle density : {metrics['realised_idle_density_mean']} "
          f"(potential - realised = {metrics['potential_minus_realised_mean']})")
    for path in write_animation_density_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
