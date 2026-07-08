"""Invariant scaling: the 16x16 re-derivation (cycle 09, ENGINE track, A1).

The gap analysis names the foundational gap: every invariant, corpus, and
gate was proven at 8x8 (~13-cell bodies) while the documents name 16x16 as
the primary target (validity-research 1.34; deep-research bake-off scale;
dossier example invariants block: min_body_mass 18, sensor pair, one
connected component). DR 0014 committed 8x8 for its phase and required
that any size adoption take its own decision record backed by measurement.
This lab is that measurement.

Method — measure, don't assume:

1. Census the proven 8x8 seed corpus (the evidence base) as dimensionless
   statistics: core mass, occupancy fraction, symmetry, organ presence,
   4- vs 8-connectivity of the required core.
2. Build a 2x-upscaled control population from the 50 seeds (DR 0014's
   probe method) — the "upscaled blob" anti-goal, used only as the
   area-scaling anchor (core mass x4 exactly, symmetry preserved).
3. Hand-author ten 16x16 PILOT exemplars across the five palettes with
   real morphology from the DR 0015 vocabulary (shell, joint, limb,
   antenna, sensor, decoration, effect), including deliberate probes:
   a lean creature at the documented floor, a heavy near-ceiling tank,
   a low-symmetry serpent, a mid-symmetry golem, and one creature whose
   core is 8-connected but NOT 4-connected (the diagonal tolerance is
   load-bearing). A2 grows this into the >=50 corpus; the pilots are the
   measurement subjects that make A1 empirical rather than assumed.
4. Noise experiments (seeded, deterministic): chance-pass probability of
   the mass+connectivity invariant for scattered cells at both scales
   (the validator's actual semantic), and largest-component
   characterization of density-matched scatter.
5. Evaluate candidate 16x16 core floors {4, 8, 16, 18, 24} against
   empirical gates; adopt the documented dossier floor (18) only if no
   gate refutes it.

The ratified law: body_core_min_cells(w, h) = max(4, 18*w*h // 256) —
anchored at the documented 16x16 floor and backward-consistent with the
ratified 8x8 floor (18*64 // 256 = 4). Engine/validator adoption is task
A3 (RED-first, size-parametric, 8x8 pins unbroken); this lab is the
evidence and the numbers.
"""

import argparse
import json
import random
import statistics
from collections import deque
from copy import deepcopy
from pathlib import Path

from corpus_builder import build_seed_grids
from grid_helpers import RICH_ORGAN_ROLES, RICH_TOKENS, grid_from_rich_matrix
from validator import body_core_min_cells as _validator_floor_law
from validator import validate_grid


ROOT = Path(__file__).resolve().parents[2]

REPORT_DATE = "2026-07-08"

# The documented 16x16 floor (deep-research dossier invariants block),
# adopted by measurement below and ratified in DR 0029.
RATIFIED_FLOOR_16 = 18
RATIFIED_FLOOR_8 = 4
FLOOR_CANDIDATES = [4, 8, 16, 18, 24]
# Fraction-preservation tolerance: a candidate floor's share of the canvas
# must stay within +/-25% of the ratified 8x8 share (4/64).
FRACTION_BAND = (0.75, 1.25)
CHANCE_TRIALS = 4000
NOISE_TRIALS = 1000
CHANCE_K_VALUES = [4, 8, 16, 18]

# The rich authoring alphabet lives in grid_helpers (RICH_TOKENS /
# RICH_ORGAN_ROLES) — shared with corpus_builder's 16x16 corpus so the
# vocabulary has one source (finding L-04). Aliased here for the pilots.
PILOT_TOKENS = RICH_TOKENS
PILOT_ORGAN_ROLES = RICH_ORGAN_ROLES

PILOT_BLUEPRINTS = [
    # Domed beetle: shell carapace, six jointed legs, sensor pods on
    # antennae. High symmetry, heavy occupancy.
    ("mg_pilot16_beetle", "lcd_green", [
        "................",
        "....P......P....",
        ".....N....N.....",
        "....SSSSSSSS....",
        "...SSBBBBBBSS...",
        "..SSBBEBBEBBSS..",
        "..SBBBBBBBBBBS..",
        "..SBBBABBBBBBS..",
        "..SBBBBMMBBBBS..",
        "..SSBBBBBBBBSS..",
        "...SSBBBBBBSS...",
        "....SSSSSSSS....",
        "...J..J..J..J...",
        "...L..L..L..L...",
        "...L..L..L..L...",
        "................",
    ]),
    # Lean wisp: 20-cell core just above the documented floor, effect
    # aura, trim tail lights. The lean-but-authored probe.
    ("mg_pilot16_wisp", "lcd_green", [
        "................",
        "................",
        "......F..F......",
        ".......EE.......",
        ".....BBBBBB.....",
        "....BBBABBBB....",
        ".....BBBBBB.....",
        ".......MM.......",
        "......D..D......",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    # Wide crab: antenna eye-stalks, jointed leg fan.
    ("mg_pilot16_crab", "gameboy_gray", [
        "................",
        "....N......N....",
        "....N......N....",
        "....EBBBBBBE....",
        "..BBBBBBBBBBBB..",
        "..BBBBBABBBBBB..",
        "...BBBBMMBBBB...",
        "....BBBBBBBB....",
        "...J.J....J.J...",
        "..L...L..L...L..",
        ".LL..........LL.",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    # Moth: limb wings spanning the full width, feathered antennae.
    ("mg_pilot16_moth", "gameboy_gray", [
        "................",
        "....N......N....",
        ".....N....N.....",
        ".....EBBBBE.....",
        "......BMMB......",
        ".LLL.BBBBBB.LLL.",
        "LLLLLBBABBBLLLLL",
        ".LLL.BBBBBB.LLL.",
        "..LL..BBBB..LL..",
        ".......BB.......",
        "......D..D......",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    # Serpent: S-coiled body, side-facing mouth, rattle trim. The
    # deliberate LOW-symmetry probe (no 8x8 seed is this asymmetric).
    ("mg_pilot16_serpent", "amber_terminal", [
        "................",
        "..EE............",
        ".BBBB...........",
        ".BABBM..........",
        ".BBB............",
        "..BBB...........",
        "...BBB..........",
        "....BBBB........",
        "......BBBB......",
        "........BBBB....",
        "..........BBB...",
        "...........BBB..",
        "..........BBB...",
        ".......BBBB.....",
        ".....DD.........",
        "................",
    ]),
    # Turtle: 60-cell core in a full shell ring, head through a shell
    # gap. The heavy near-ceiling probe (43.8% occupancy) — and its neck
    # cells connect to the torso only diagonally, so the core is
    # 8-connected but NOT 4-connected (invariant 6's topology matters).
    ("mg_pilot16_turtle", "amber_terminal", [
        "................",
        "......EBBE......",
        "......BMMB......",
        "....SSSBBSSS....",
        "...SSBBBBBBSS...",
        "..SSBBBBBBBBSS..",
        "..SBBBDBBDBBBS..",
        "..SBBBBABBBBBS..",
        "..SBBBDBBDBBBS..",
        "..SSBBBBBBBBSS..",
        "...SSBBBBBBSS...",
        "....SSSSSSSS....",
        "..LL........LL..",
        ".LL..........LL.",
        "................",
        "................",
    ]),
    # Strider: 18-cell core exactly at the documented floor on stilt
    # legs. The floor probe: the leanest deliberately-readable creature.
    ("mg_pilot16_strider", "crt_blue", [
        "................",
        "......EBBE......",
        ".....BBBBBB.....",
        ".....BBABBB.....",
        ".....BBMMBB.....",
        "....J.J..J.J....",
        "....J.J..J.J....",
        "...L..L..L..L...",
        "...L..L..L..L...",
        "..L...L..L...L..",
        "..L...L..L...L..",
        ".L....L..L....L.",
        ".L....L..L....L.",
        "................",
        "................",
        "................",
    ]),
    # Jelly: dome with embedded eyes, dangling light-trim tendrils,
    # effect sparks.
    ("mg_pilot16_jelly", "crt_blue", [
        "................",
        "......F..F......",
        ".....BBBBBB.....",
        "....BBBBBBBB....",
        "...BBEBBBBEBB...",
        "...BBBBABBBBB...",
        "...BBBBMMBBBB...",
        "....D.D..D.D....",
        "....D.D..D.D....",
        ".....D.DD.D.....",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ]),
    # Owl: 2x2 eye blocks (multi-cell organs are what 16x16 affords),
    # ear tufts, jointed talons.
    ("mg_pilot16_owl", "pocket_plum", [
        "................",
        "...N........N...",
        "....N......N....",
        "....BBBBBBBB....",
        "...BEEBBBBEEB...",
        "...BEEBBBBEEB...",
        "...BBBBMMBBBB...",
        "....BBBMMBBB....",
        "....BBBABBBB....",
        ".....BBBBBB.....",
        ".....JBBBBJ.....",
        "....LL....LL....",
        "....L......L....",
        "................",
        "................",
        "................",
    ]),
    # Golem: blocky torso with an asymmetric left pauldron (shell +
    # decoration). The mid-symmetry probe (~0.65, the dossier's
    # symmetry_bias band).
    ("mg_pilot16_golem", "pocket_plum", [
        "................",
        "......EBBE......",
        "..DD..BMMB......",
        "..SS.BBBBBB.....",
        ".SSSBBBBBBBB....",
        ".SSBBBBABBBB....",
        "..SBBBBBBBBB....",
        "...BBBBBBBBB....",
        "...BBB..BBB.....",
        "...BBB..BBB.....",
        "...LLL..LLL.....",
        "...LLL..LLL.....",
        "................",
        "................",
        "................",
        "................",
    ]),
]


def body_core_min_cells(width: int, height: int) -> int:
    """The ratified size-parametric core-mass floor (DR 0029).

    Anchored at the documented 16x16 floor (18) and backward-consistent
    with the ratified 8x8 floor: 18*64 // 256 = 4. Since the A3 port the
    ENFORCED law lives in validator.body_core_min_cells; this delegates
    so the lab evidence and the enforcement can never drift.
    """
    return _validator_floor_law(width, height)


def build_pilot_grids() -> list[dict]:
    return [
        _grid_from_pilot_blueprint(grid_id, palette_id, rows)
        for grid_id, palette_id, rows in PILOT_BLUEPRINTS
    ]


def upscale_grid_2x(grid: dict) -> dict:
    """DR 0014's probe method: cells -> 2x2 blocks, single anchor kept.

    The control population: valid by construction, core mass exactly 4x,
    symmetry preserved — and exactly the "upscaled blob" A2 must not be.
    """
    control = deepcopy(grid)
    width, height = grid["grid_size"]
    control["grid_id"] = f"{grid['grid_id']}_up16"
    control["parent_grid_id"] = grid["grid_id"]
    control["grid_size"] = [2 * width, 2 * height]
    cells: list[dict] = []
    for cell in grid["cells"]:
        for dy in (0, 1):
            for dx in (0, 1):
                copy = deepcopy(cell)
                copy["x"] = 2 * cell["x"] + dx
                copy["y"] = 2 * cell["y"] + dy
                copy["animation_anchor"] = (
                    cell.get("animation_anchor") is True and dx == 0 and dy == 0
                )
                cells.append(copy)
    control["cells"] = cells
    control["organs"] = {
        name: {
            **organ,
            "cells": [
                [2 * x + dx, 2 * y + dy]
                for x, y in organ["cells"]
                for dy in (0, 1)
                for dx in (0, 1)
            ],
        }
        for name, organ in grid["organs"].items()
    }
    control.setdefault("metadata", {})["source"] = "invariant_scaling_upscale_control"
    lineage = control.setdefault(
        "lineage", {"generation": 0, "ancestor_ids": [], "mutation_events": []}
    )
    lineage["mutation_events"] = list(lineage.get("mutation_events", [])) + [
        "upscaled_2x_control"
    ]
    return control


def population_census(grids: list[dict]) -> dict:
    core_masses = [_core_mass(grid) for grid in grids]
    occupied = [len(grid["cells"]) for grid in grids]
    fractions = [
        len(grid["cells"]) / (grid["grid_size"][0] * grid["grid_size"][1])
        for grid in grids
    ]
    eye_counts = [
        sum(1 for cell in grid["cells"] if cell.get("role") == "eye") for grid in grids
    ]
    anchor_counts = [
        sum(1 for cell in grid["cells"] if cell.get("animation_anchor") is True)
        for grid in grids
    ]
    symmetries = [_symmetry_score(grid) for grid in grids]
    four_connected = [
        _is_connected(_required_core_points(grid), diagonal=False) for grid in grids
    ]
    eight_connected = [
        _is_connected(_required_core_points(grid), diagonal=True) for grid in grids
    ]
    organ_roles = sorted({role for role, _ in PILOT_ORGAN_ROLES.values()})
    role_presence = {
        role: round(
            sum(
                1
                for grid in grids
                if any(organ.get("role") == role for organ in grid["organs"].values())
            )
            / len(grids),
            6,
        )
        for role in organ_roles
    }
    return {
        "count": len(grids),
        "core_mass": _stat_triplet(core_masses),
        "occupied_cells": _stat_triplet(occupied),
        "occupancy_fraction": _stat_triplet(fractions),
        "eye_cells": _stat_triplet(eye_counts),
        "anchor_cells": _stat_triplet(anchor_counts),
        "symmetry": _stat_triplet(symmetries),
        "symmetry_bins_covered": _symmetry_bins(symmetries),
        "core_4connected_fraction": round(
            sum(four_connected) / len(four_connected), 6
        ),
        "core_8connected_fraction": round(
            sum(eight_connected) / len(eight_connected), 6
        ),
        "organ_role_presence": role_presence,
    }


def chance_connectivity_experiment(
    trials: int = CHANCE_TRIALS, k_values: list[int] | None = None
) -> dict:
    """P(k uniformly scattered cells form one 8-connected component).

    The validator's actual chance-pass semantic for a genome whose whole
    core is random scatter. Measures how the mass+connectivity invariant's
    rejection power scales with the canvas.
    """
    results: dict[str, dict[str, float]] = {}
    for size in (8, 16):
        row: dict[str, float] = {}
        for k in k_values or CHANCE_K_VALUES:
            rng = random.Random(f"invariant_scaling_chance:{size}:{k}")
            connected = 0
            for _ in range(trials):
                points = _scatter(rng, size, k)
                if _is_connected(points, diagonal=True):
                    connected += 1
            row[f"k{k}"] = round(connected / trials, 6)
        results[f"{size}x{size}"] = row
    return results


def noise_largest_component_experiment(trials: int = NOISE_TRIALS) -> dict:
    """Largest 8-connected component of density-matched random scatter.

    Density is the measured median occupancy of the proven 8x8 seed
    corpus, applied to both canvases. Characterization only (an adversary
    labeling the largest noise cluster as a core organ), not a gate: the
    validator never sees undeclared organs.
    """
    seeds = build_seed_grids()
    median_occupied = statistics.median(len(grid["cells"]) for grid in seeds)
    density = median_occupied / 64
    results: dict[str, dict] = {}
    for size in (8, 16):
        k = round(density * size * size)
        rng = random.Random(f"invariant_scaling_noise:{size}:{k}")
        largest: list[int] = []
        for _ in range(trials):
            points = _scatter(rng, size, k)
            largest.append(_largest_component(points))
        largest.sort()
        results[f"{size}x{size}"] = {
            "scattered_cells": k,
            "p50": largest[(len(largest) - 1) // 2],
            "p95": largest[int(0.95 * (len(largest) - 1))],
            "max": largest[-1],
        }
    results["density"] = round(density, 6)
    return results


def evaluate_floor_candidates(
    pilots: list[dict], controls: list[dict]
) -> list[dict]:
    pilot_masses = [_core_mass(grid) for grid in pilots]
    control_masses = [_core_mass(grid) for grid in controls]
    chance = chance_connectivity_experiment(
        trials=CHANCE_TRIALS, k_values=FLOOR_CANDIDATES
    )
    baseline_fraction = RATIFIED_FLOOR_8 / 64
    rows: list[dict] = []
    for floor in FLOOR_CANDIDATES:
        fraction = floor / 256
        fraction_ratio = fraction / baseline_fraction
        fraction_gate = FRACTION_BAND[0] <= fraction_ratio <= FRACTION_BAND[1]
        pilots_pass = all(mass >= floor for mass in pilot_masses)
        controls_pass = all(mass >= floor for mass in control_masses)
        chance_pass_rate = chance["16x16"][f"k{floor}"]
        chance_gate = chance_pass_rate <= 0.02
        if not fraction_gate:
            verdict = "reject_fraction_band"
        elif not (pilots_pass and controls_pass and chance_gate):
            verdict = "reject_empirical_gate"
        elif floor == RATIFIED_FLOOR_16:
            verdict = "adopt"
        else:
            verdict = "viable_alternate"
        rows.append(
            {
                "floor": floor,
                "fraction_of_area": round(fraction, 6),
                "fraction_ratio_vs_8x8": round(fraction_ratio, 6),
                "fraction_gate": fraction_gate,
                "pilots_pass": pilots_pass,
                "controls_pass": controls_pass,
                "chance_pass_rate_16x16": chance_pass_rate,
                "chance_gate": chance_gate,
                "verdict": verdict,
            }
        )
    return rows


def build_invariant_scaling_report() -> dict:
    seeds = build_seed_grids()
    pilots = build_pilot_grids()
    controls = [upscale_grid_2x(grid) for grid in seeds]
    floor_rows = evaluate_floor_candidates(pilots, controls)
    adopted = [row for row in floor_rows if row["verdict"] == "adopt"]
    law_table = {
        f"{size}x{size}": body_core_min_cells(size, size)
        for size in (8, 12, 16, 24, 32, 64)
    }
    pilot_census = population_census(pilots)
    return {
        "artifact_id": "invariant_scaling_16x16_stage0",
        "status": "complete" if len(adopted) == 1 else "refuted",
        "date": REPORT_DATE,
        "purpose": (
            "Re-derive the grid-genome hard/soft invariants at 16x16 "
            "empirically (cycle 09 A1): census the proven 8x8 corpus as "
            "dimensionless statistics, anchor area scaling with 2x-upscaled "
            "controls, author ten 16x16 pilot exemplars across the DR 0015 "
            "vocabulary, measure chance-pass rejection power, and evaluate "
            "candidate core-mass floors against the documented dossier value."
        ),
        "source_artifacts": [
            "labs/grid_genome/corpus_builder.py",
            "labs/grid_genome/validator.py",
            "data/seed_grids",
            "research/grid_genome/grid_invariants.md",
            "research/decision_records/0014-grid-size-commitment.md",
            "research/decision_records/0015-dormant-vocabulary-coverage.md",
            "docs/project-research/deep-research/01/deep-research.md",
        ],
        "metrics": {
            "populations": {
                "seed_8x8": population_census(seeds),
                "upscaled_16x16_control": population_census(controls),
                "pilot_16x16": pilot_census,
            },
            "chance_connectivity": chance_connectivity_experiment(),
            "noise_largest_component": noise_largest_component_experiment(),
            "floor_candidates": floor_rows,
            "ratified": {
                "floor_16x16": RATIFIED_FLOOR_16,
                "floor_8x8": RATIFIED_FLOOR_8,
                "floor_law": "max(4, 18 * width * height // 256)",
                "floor_law_table": law_table,
                "connectivity_topology": "8-neighbor (unchanged; one pilot's core is 8- but not 4-connected)",
                "sensor_pair_16x16": "soft expectation; hard corpus gate in A2; validator status revisited in A3",
                "symmetry_band_16x16": pilot_census["symmetry"],
                "occupancy_ceiling_16x16_soft": pilot_census["occupancy_fraction"]["max"],
            },
        },
        "closed_states": [
            "pilot_16x16_exemplars_validated_lab_and_package",
            "floor_16x16_ratified_at_documented_18",
            "floor_law_backward_consistent_with_8x8",
            "connectivity_topology_reaffirmed_8_neighbor",
            "chance_pass_rejection_strengthens_with_scale",
            "upscale_area_law_confirmed_4x",
        ],
        "blocked_states": [
            "engine_validator_floor_still_8x8_constant (A3: RED-first size-parametric port; 8x8 pins unbroken)",
            "slip_fixture_mass_bounds_still_8x8_denominated (A3: size-relative bounds per DR 0014's ladder)",
            "generation_model_cannot_emit_16x16 (A3: per-size training on the A2 corpus)",
            "archive_stress_probe_uses_8x8_constant_mass_div_16 (A3/A4: renormalize from evidence)",
            "readability_16x16_uncalibrated (learned-model retrain in A3; human survey remains the deferred fallback, never a blocker)",
        ],
        "decision": (
            "16x16 is ratified as the proven default target scale (DR 0029). "
            "Body-core floor 18 at 16x16 via the size law "
            "max(4, 18*w*h//256); 8x8 stays ratified at 4 and remains valid "
            "input. 8-neighbor connectivity reaffirmed. Engine adoption is "
            "cycle-09 A3, size-parametric, never size-replacing."
        ),
        "next_research_step": (
            "A2: extend the corpus to >=50 hand-authored-quality 16x16 "
            "creatures across the DR 0015 vocabulary (the pilots seed it), "
            "plus the invalid corpus and the workshop 16x16 canvas."
        ),
    }


def write_invariant_scaling_artifacts(
    output_dir: Path, report: dict, pilot_dir: Path
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    pilot_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "invariant_scaling_16x16_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    for grid in build_pilot_grids():
        (pilot_dir / f"{grid['grid_id']}.json").write_text(
            json.dumps(grid, indent=2) + "\n", encoding="utf-8"
        )
    (pilot_dir / "README.md").write_text(
        "# 16x16 Pilot Exemplars\n\n"
        "Ten hand-authored 16x16 creatures (cycle 09 A1, DR 0029): the\n"
        "measurement subjects for the invariant re-derivation at the\n"
        "documented primary scale. Real morphology from the DR 0015\n"
        "vocabulary — shell, joint, limb, antenna, sensor, decoration,\n"
        "effect — across all five palettes, with deliberate probes: a\n"
        "lean 18-cell-core strider at the documented floor, a 60-cell\n"
        "turtle near the occupancy ceiling (whose neck makes the core\n"
        "8- but not 4-connected), a low-symmetry serpent, and a\n"
        "mid-symmetry golem. NOT upscaled 8x8 blobs. The A2 seed corpus\n"
        "grows from these.\n\n"
        "Produced by `labs/grid_genome/invariant_scaling.py`; evidence in\n"
        "`data/grid_genome/invariant_scaling_16x16_stage0.json`.\n",
        encoding="utf-8",
    )


def _grid_from_pilot_blueprint(grid_id: str, palette_id: str, rows: list[str]) -> dict:
    return grid_from_rich_matrix(
        grid_id,
        rows,
        palette_id,
        size=16,
        source="invariant_scaling_pilot16",
        mutation_events=["pilot16_hand_authored"],
    )


def _core_mass(grid: dict) -> int:
    return len(_required_core_points(grid))


def _required_core_points(grid: dict) -> set[tuple[int, int]]:
    points: set[tuple[int, int]] = set()
    for organ in grid["organs"].values():
        if organ.get("role") == "body_core" and organ.get("required") is True:
            points.update((x, y) for x, y in organ["cells"])
    return points


def _symmetry_score(grid: dict) -> float:
    # Mirrored verbatim from mecha_engine.archive._metrics.symmetry_score
    # (drift pinned by test_invariant_scaling against the package function).
    width = grid["grid_size"][0]
    occupied = {(cell["x"], cell["y"], cell["role"]) for cell in grid["cells"]}
    if not occupied:
        return 0.0
    mirrored = sum(
        1 for x, y, role in occupied if (width - 1 - x, y, role) in occupied
    )
    return mirrored / len(occupied)


def _symmetry_bins(scores: list[float]) -> int:
    return len({min(int(score * 5), 4) for score in scores})


def _stat_triplet(values: list) -> dict:
    return {
        "min": round(min(values), 6),
        "p50": round(statistics.median(values), 6),
        "max": round(max(values), 6),
    }


def _scatter(rng: random.Random, size: int, k: int) -> set[tuple[int, int]]:
    return {(index % size, index // size) for index in rng.sample(range(size * size), k)}


def _neighbors(x: int, y: int, diagonal: bool):
    if diagonal:
        return (
            (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
            (x - 1, y), (x + 1, y),
            (x - 1, y + 1), (x, y + 1), (x + 1, y + 1),
        )
    return ((x, y - 1), (x - 1, y), (x + 1, y), (x, y + 1))


def _is_connected(points: set[tuple[int, int]], *, diagonal: bool) -> bool:
    if not points:
        return False
    start = next(iter(points))
    seen = {start}
    queue: deque[tuple[int, int]] = deque([start])
    while queue:
        x, y = queue.popleft()
        for neighbor in _neighbors(x, y, diagonal):
            if neighbor in points and neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen == points


def _largest_component(points: set[tuple[int, int]]) -> int:
    remaining = set(points)
    largest = 0
    while remaining:
        start = remaining.pop()
        seen = {start}
        queue: deque[tuple[int, int]] = deque([start])
        while queue:
            x, y = queue.popleft()
            for neighbor in _neighbors(x, y, diagonal=True):
                if neighbor in remaining:
                    remaining.discard(neighbor)
                    seen.add(neighbor)
                    queue.append(neighbor)
        largest = max(largest, len(seen))
    return largest


def main() -> None:
    parser = argparse.ArgumentParser(description="16x16 invariant scaling lab (A1).")
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "grid_genome"
    )
    parser.add_argument(
        "--pilot-dir", type=Path, default=ROOT / "data" / "grid_genome" / "pilot_16x16"
    )
    args = parser.parse_args()
    for grid in build_pilot_grids():
        result = validate_grid(grid)
        if not result.ok:
            raise SystemExit(f"{grid['grid_id']} failed validation: {result.errors}")
    report = build_invariant_scaling_report()
    write_invariant_scaling_artifacts(args.output_dir, report, args.pilot_dir)
    print(
        json.dumps(
            {
                "artifact_id": report["artifact_id"],
                "status": report["status"],
                "ratified": report["metrics"]["ratified"],
                "floor_candidates": report["metrics"]["floor_candidates"],
                "pilot_core_mass": report["metrics"]["populations"]["pilot_16x16"][
                    "core_mass"
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
