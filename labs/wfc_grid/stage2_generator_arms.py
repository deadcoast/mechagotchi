"""Stage 2's undispositioned generator arms (cycle 25 O4).

`deep-research.md` names two generator-adjacent methods that have never
been dispositioned — no card, no prototype, no reject/watch verdict.
This lab judges both, **each in its documented role** (the correction O4
recorded against its own charter):

* **CPPN** — the dossier files it under *Indirect encoding*: *"Keep as
  a late exploratory generator"*, *"optional late-stage"*, integration
  risk High, named risk *"hard integration with semantic pixels"*. A
  generator bake-off IS its documented role, so it is judged on the B2
  bake-off's own terms against the adopted constrained layer's
  committed row (DR 0042).
* **Shape grammar** — filed under *Constraint systems* with WFC and
  SAT/SMT; that family's stance is *"Use as validator or post-generator
  stabilizer"*, named risk *"over-constraining novelty"*. It is
  explicitly NOT a primary generator — and its documented role is
  ALREADY SHIPPED as `wfc_grid._finish` (DR 0031's adopted arm). The
  real open question is sharper: does a shape-grammar stabilizer BEAT
  the incumbent `_finish`? Judged head-to-head on the same protocol.

THE PRE-REGISTERED RULE (see ``PRE_REGISTERED_RULE``) was written before
the run, with the prediction (``PRE_RUN_PREDICTION``) recorded first.
Nothing is re-scored after the fact; rejecting both is first-class
(DR 0031 already refuted the hybrid arm the same way).

**The instrument is the committed one.** ``measure_arm`` is imported
from the B2 bake-off, and before any verdict is trusted at the
documented protocol (batch 100, seed 1030) the harness must reproduce
the committed ``wfc`` row of ``generation_bakeoff16_stage0.json``
EXACTLY — a mismatch raises rather than writing a half-trusted
artifact (cycle 24's convergent lesson: check the instrument against a
committed number first). The distinct-rate floor 0.68 is likewise the
committed refused ``random`` arm's own unique-silhouette rate, and the
module re-derives it from the committed artifact at run time so drift
fails loudly. Noise floors for the stabilizer comparison are MEASURED
(the incumbent pipeline run at a second seed, cycle 22 L3's pattern),
never picked.
"""

import argparse
import json
import math
import random
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
for _sub in ("labs/wfc_grid", "labs/grid_genome", "labs/readability_benchmark"):
    _path = str(ROOT / _sub)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from generation_bakeoff16 import (  # noqa: E402
    BATCH_COUNT,
    RNG_SEED,
    VALIDITY_BAR,
    _modal_roles,
    measure_arm,
)
from corpus_builder import build_seed_grids_16  # noqa: E402
from grid_helpers import PALETTES, grid_from_matrix  # noqa: E402
from validator import body_core_min_cells  # noqa: E402
from wfc_grid import (  # noqa: E402
    MAX_RESTARTS,
    _collapse,
    _largest_component,
    generate_wfc_grid,
    rich_matrix_from_grid,
    split_corpus,
    train_wfc_model,
)


REPORT_DATE = "2026-08-08"
ARTIFACT_ID = "stage2_generator_arms_stage0"
NOISE_SEED = 2061
COMMITTED_BAKEOFF = "data/wfc_grid/generation_bakeoff16_stage0.json"

ARMS = ("cppn", "shape_grammar")

# The dossier's verbatim stances — the roles each arm is judged at.
DOCUMENTED_ROLES = {
    "cppn": {
        "role": "generator",
        "family": "Indirect encoding (CPPN, HyperNEAT-style regularity)",
        "dossier_stance": "Keep as a late exploratory generator",
        "dossier_notes": (
            "optional body-plan regularity and symmetry; priority "
            "low-to-medium; main risk: hard integration with semantic "
            "pixels; method matrix: regularity-heavy indirect encoding, "
            "optional late-stage, integration risk High"
        ),
    },
    "shape_grammar": {
        "role": "post_generator_stabilizer",
        "family": "Constraint systems (WFC, SAT/SMT, ASP, shape grammars)",
        "dossier_stance": "Use as validator or post-generator stabilizer",
        "dossier_notes": (
            "hard validity, organ placement, symmetry, reachability of "
            "body plans; main risk: over-constraining novelty; the "
            "incumbent at this job is wfc_grid._finish (DR 0031, the "
            "adopted WFC arm's own finishing pass)"
        ),
    },
}

# The committed refused `random` arm's unique-silhouette rate (68/100 in
# data/wfc_grid/generation_bakeoff16_stage0.json) — the measured floor
# below which a batch's distinctness matches an arm the bake-off already
# refused. build_stage2_arms_report re-derives it from the committed
# artifact and refuses to run if this constant has drifted.
REFUSED_DISTINCT_FLOOR = 0.68

PRE_REGISTERED_RULE = (
    "PRE-REGISTERED before the run; each arm is judged in its DOCUMENTED "
    "ROLE, not the charter's original bake-off-both framing. "
    "CPPN (generator): reject if validity < the dossier bar "
    f"{VALIDITY_BAR} (the B2 bake-off's own bar) — validity is the first "
    "gate and nothing offsets it; reject if distinct rate <= "
    f"{REFUSED_DISTINCT_FLOOR} (the committed refused random arm's "
    "measured floor); prototype if it matches the adopted constrained "
    "layer's committed row (DR 0042) on BOTH validity and readability; "
    "watch otherwise. Adopt is deliberately unreachable at stage 0 — the "
    "charter's own verbs are reject/watch/prototype, and adoption is a "
    "decision-record act at documented scale, not a prototype verdict. "
    "Shape grammar (post-generator stabilizer, judged at the incumbent "
    "wfc_grid._finish's own job): reject if it does not raise validity "
    "over the raw collapse beyond the measured noise; reject if distinct "
    f"retention falls below {REFUSED_DISTINCT_FLOOR} (over-constraining "
    "novelty, the dossier's named risk); prototype only if it beats the "
    "incumbent _finish on validity beyond the two-seed noise floor "
    "without worse distinct retention; watch on a tie within noise; "
    "reject if it loses to the incumbent beyond noise — the DR 0031 "
    "hybrid-refutation logic: a challenger that adds nothing over the "
    "shipped incumbent is refused. Instrument gate: at the committed "
    "protocol (batch 100, seed 1030) the harness must reproduce the "
    "committed wfc row of generation_bakeoff16_stage0.json exactly; a "
    "mismatch raises instead of writing an artifact."
)

PRE_RUN_PREDICTION = (
    "Recorded before the run: cppn is predicted to REJECT on raw "
    "validity — an indirect encoding painting activation blobs meets the "
    "semantic-pixel validator's connected-core floor head on, which is "
    "the dossier's own named risk ('hard integration with semantic "
    "pixels'). Shape grammar is predicted to raise validity over the raw "
    "collapse but at best TIE the incumbent _finish at its committed "
    "validity 1.0, landing WATCH. Whatever the numbers say is what ships."
)

_PREDICTED_VERDICTS = {"cppn": "reject", "shape_grammar": "watch"}


# --------------------------------------------------------------------------
# The CPPN arm — a compositional pattern-producing network over cell
# coordinates. Inputs per cell: normalized x, normalized y, radial
# distance r, and |x| (the bilateral-symmetry channel CPPNs are known
# for). One output channel per generator token; the cell takes the
# argmax. Two declared design choices, both part of the generator: the
# empty channel gains a radial bias (creatures live in the canvas
# middle — the same prior the WFC lab learns from its corpus), and the
# center cell is a germ cell (every creature has a body seed). The
# anchor is anointed at the strongest body activation, mirroring the
# promoted generator's one-anchor semantics.
# --------------------------------------------------------------------------

_HIDDEN_NODES = 6
_WEIGHT_SPAN = 2.0
_EMPTY_RADIAL_GAIN = 1.5
_OUTPUT_TOKENS = (".", "B", "S", "J", "L", "E", "M", "N", "P", "D", "F")


def _gauss(z: float) -> float:
    return math.exp(-z * z)


def _sigmoid(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, z))))


_FUNCTION_TABLE = (math.sin, math.cos, _gauss, _sigmoid, abs)


def _cppn_network(rng: random.Random) -> tuple[list[dict], dict[str, dict]]:
    hidden = [
        {
            "function": rng.randrange(len(_FUNCTION_TABLE)),
            "weights": [
                rng.uniform(-_WEIGHT_SPAN, _WEIGHT_SPAN) for _ in range(4)
            ],
            "bias": rng.uniform(-1.0, 1.0),
        }
        for _ in range(_HIDDEN_NODES)
    ]
    outputs = {
        token: {
            "weights": [
                rng.uniform(-_WEIGHT_SPAN, _WEIGHT_SPAN)
                for _ in range(_HIDDEN_NODES)
            ],
            "bias": rng.uniform(-1.0, 1.0),
        }
        for token in _OUTPUT_TOKENS
    }
    return hidden, outputs


def _cppn_scores(
    hidden: list[dict],
    outputs: dict[str, dict],
    xn: float,
    yn: float,
    r: float,
    s: float,
) -> dict[str, float]:
    activations = []
    for node in hidden:
        w = node["weights"]
        z = w[0] * xn + w[1] * yn + w[2] * r + w[3] * s + node["bias"]
        activations.append(_FUNCTION_TABLE[node["function"]](z))
    scores: dict[str, float] = {}
    for token, out in outputs.items():
        z = sum(
            weight * value for weight, value in zip(out["weights"], activations)
        ) + out["bias"]
        z = math.tanh(z)
        if token == ".":
            # Centered radial bias: empty is penalized in the canvas
            # middle and favored at the rim (creatures live in the
            # middle — the same prior the WFC lab learns from its corpus).
            z += _EMPTY_RADIAL_GAIN * (r - 0.5)
        scores[token] = z
    return scores


def cppn_grid(*, rng_seed: int, size: int = 16, grid_id: str | None = None) -> dict:
    """Compose one creature; deterministic per (rng_seed, size)."""
    rng = random.Random(rng_seed)
    hidden, outputs = _cppn_network(rng)
    half = (size - 1) / 2.0
    matrix: list[list[str]] = []
    body_score: dict[tuple[int, int], float] = {}
    for y in range(size):
        row: list[str] = []
        for x in range(size):
            xn = (x - half) / half
            yn = (y - half) / half
            scores = _cppn_scores(
                hidden, outputs, xn, yn, math.hypot(xn, yn), abs(xn)
            )
            token = max(sorted(scores), key=lambda name: scores[name])
            row.append(token)
            if token == "B":
                body_score[(x, y)] = scores["B"]
        matrix.append(row)

    center = size // 2
    if matrix[center][center] == ".":
        # The germ rule: every creature has a body seed.
        matrix[center][center] = "B"
        body_score[(center, center)] = float("-inf")
    elif matrix[center][center] != "B" and not body_score:
        matrix[center][center] = "B"
        body_score[(center, center)] = float("-inf")

    anchor_x, anchor_y = min(
        body_score, key=lambda point: (-body_score[point], point[1], point[0])
    )
    matrix[anchor_y][anchor_x] = "A"

    palette_id = rng.choice(sorted(PALETTES))
    return grid_from_matrix(
        grid_id or f"mg_cppn_{rng_seed:03d}",
        ["".join(row) for row in matrix],
        palette_id,
        source="cppn_generator_lab",
        rng_seed=rng_seed,
        mutation_events=["cppn_composed"],
    )


def build_cppn_corpus(*, count: int, rng_seed: int, size: int) -> list[dict]:
    return [
        cppn_grid(
            rng_seed=rng_seed + index, size=size, grid_id=f"mg_cppn_{index:03d}"
        )
        for index in range(count)
    ]


# --------------------------------------------------------------------------
# The shape-grammar arm — named constraint productions applied to a grid,
# each recorded in the trace (the dossier's stance includes "validator",
# and an unexplainable validator is worthless). Deterministic: no RNG,
# smallest-(y, x) tie-breaks throughout. The input grid is never mutated.
# --------------------------------------------------------------------------


def shape_grammar_stabilize(grid: dict) -> tuple[dict, list[dict]]:
    width, height = grid["grid_size"]
    matrix = [row[:] for row in rich_matrix_from_grid(deepcopy(grid))]
    trace: list[dict] = []

    def core_cells() -> set[tuple[int, int]]:
        return {
            (x, y)
            for y, row in enumerate(matrix)
            for x, token in enumerate(row)
            if token in ("B", "A")
        }

    def neighbors(point: tuple[int, int]) -> list[tuple[int, int]]:
        x, y = point
        return [
            (x + dx, y + dy)
            for dy in (-1, 0, 1)
            for dx in (-1, 0, 1)
            if (dx, dy) != (0, 0)
            and 0 <= x + dx < width
            and 0 <= y + dy < height
        ]

    core = core_cells()
    if not core:
        germ = (width // 2, height // 2)
        matrix[germ[1]][germ[0]] = "B"
        core = {germ}
        trace.append({"rule": "seed_germ_cell", "cell": [germ[0], germ[1]]})

    anchors = sum(row.count("A") for row in matrix)
    if anchors:
        for y, row in enumerate(matrix):
            for x, token in enumerate(row):
                if token == "A":
                    matrix[y][x] = "B"
        trace.append({"rule": "anchors_read_as_body", "cells": anchors})

    largest = _largest_component(core)
    strays = core - largest
    if strays:
        for x, y in strays:
            matrix[y][x] = "."
        core = set(largest)
        trace.append({"rule": "largest_core_survives", "removed": len(strays)})

    floor = body_core_min_cells(width, height)
    grown = 0
    while len(core) < floor:
        frontier = sorted(
            {
                point
                for cell in core
                for point in neighbors(cell)
                if matrix[point[1]][point[0]] == "."
            },
            key=lambda point: (point[1], point[0]),
        )
        if not frontier:
            break
        x, y = frontier[0]
        matrix[y][x] = "B"
        core.add((x, y))
        grown += 1
    if grown:
        trace.append(
            {"rule": "grow_core_to_floor", "grown": grown, "floor": floor}
        )

    if not any("E" in row for row in ("".join(row) for row in matrix)):
        empty_adjacent = sorted(
            {
                point
                for cell in core
                for point in neighbors(cell)
                if matrix[point[1]][point[0]] == "."
            },
            key=lambda point: (point[1], point[0]),
        )
        placed = None
        if empty_adjacent:
            placed = empty_adjacent[0]
        else:
            empties = sorted(
                (
                    (x, y)
                    for y, row in enumerate(matrix)
                    for x, token in enumerate(row)
                    if token == "."
                ),
                key=lambda point: (point[1], point[0]),
            )
            if empties:
                placed = empties[0]
        if placed is not None:
            matrix[placed[1]][placed[0]] = "E"
            trace.append(
                {"rule": "require_sensor_cell", "cell": [placed[0], placed[1]]}
            )

    anchor_x, anchor_y = min(core, key=lambda point: (point[1], point[0]))
    matrix[anchor_y][anchor_x] = "A"
    trace.append({"rule": "anoint_anchor", "cell": [anchor_x, anchor_y]})

    palette_id = grid.get("palette", {}).get("palette_id")
    if palette_id not in PALETTES:
        palette_id = sorted(PALETTES)[0]
    stabilized = grid_from_matrix(
        grid["grid_id"],
        ["".join(row) for row in matrix],
        palette_id,
        source="shape_grammar_stabilizer_lab",
        mutation_events=[entry["rule"] for entry in trace],
    )
    return stabilized, trace


# --------------------------------------------------------------------------
# The pre-registered judges. Judged on values as passed (callers pass the
# ROUNDED rates the artifact reports, so a verdict always agrees with the
# number it publishes — the float-boundary trap).
# --------------------------------------------------------------------------


def _require_rate(value: float, name: str) -> None:
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise ValueError(f"{name} must be a number, got {value!r}")
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{name} outside 0..1: {value}")


def judge_generator_arm(
    *,
    arm: str,
    validity_rate: float,
    baseline_validity_rate: float,
    readability: float,
    baseline_readability: float,
    distinct_rate: float,
) -> dict:
    """CPPN's gate — the documented generator thresholds (see module doc)."""
    for name, value in (
        ("validity_rate", validity_rate),
        ("baseline_validity_rate", baseline_validity_rate),
        ("readability", readability),
        ("baseline_readability", baseline_readability),
        ("distinct_rate", distinct_rate),
    ):
        _require_rate(value, name)

    if validity_rate < VALIDITY_BAR:
        verdict, reason = "reject", (
            f"validity {validity_rate} is below the dossier bar "
            f"{VALIDITY_BAR} the adopted layer was judged by; validity is "
            "the first gate and nothing offsets it"
        )
    elif distinct_rate <= REFUSED_DISTINCT_FLOOR:
        verdict, reason = "reject", (
            f"distinct rate {distinct_rate} is at or below the committed "
            f"refused random arm's floor {REFUSED_DISTINCT_FLOOR} — the "
            "batch's novelty matches an arm the bake-off already refused"
        )
    elif (
        validity_rate >= baseline_validity_rate
        and readability >= baseline_readability
    ):
        verdict, reason = "prototype", (
            "matches the adopted layer's committed row on both validity "
            f"({validity_rate} vs {baseline_validity_rate}) and "
            f"readability ({readability} vs {baseline_readability}) at "
            "prototype scale — a deeper prototype is earned"
        )
    else:
        verdict, reason = "watch", (
            "clears the dossier's own bars but does not match the adopted "
            f"layer (validity {validity_rate} vs {baseline_validity_rate}, "
            f"readability {readability} vs {baseline_readability})"
        )
    return {
        "arm": arm,
        "role": "generator",
        "verdict": verdict,
        "reason": reason,
        "inputs": {
            "validity_rate": validity_rate,
            "baseline_validity_rate": baseline_validity_rate,
            "readability": readability,
            "baseline_readability": baseline_readability,
            "distinct_rate": distinct_rate,
        },
    }


def judge_stabilizer_arm(
    *,
    arm: str,
    validity_before: float,
    validity_after: float,
    distinct_before: float,
    distinct_after: float,
    incumbent_validity_after: float | None = None,
    incumbent_distinct_after: float | None = None,
    noise_validity: float = 0.0,
    noise_distinct: float = 0.0,
) -> dict:
    """Shape grammar's gate — its OWN documented job (see module doc)."""
    for name, value in (
        ("validity_before", validity_before),
        ("validity_after", validity_after),
        ("distinct_before", distinct_before),
        ("distinct_after", distinct_after),
    ):
        _require_rate(value, name)
    for name, value in (
        ("incumbent_validity_after", incumbent_validity_after),
        ("incumbent_distinct_after", incumbent_distinct_after),
    ):
        if value is not None:
            _require_rate(value, name)
    if noise_validity < 0.0 or noise_distinct < 0.0:
        raise ValueError("noise floors must be non-negative")

    retention = (
        distinct_after / distinct_before if distinct_before > 0.0 else 1.0
    )
    if validity_after <= validity_before + noise_validity:
        verdict, reason = "reject", (
            f"does not raise validity ({validity_before} -> "
            f"{validity_after}, noise {noise_validity}) — raising validity "
            "is a stabilizer's one documented job"
        )
    elif retention < REFUSED_DISTINCT_FLOOR:
        verdict, reason = "reject", (
            f"collapses novelty: distinct retention {round(retention, 6)} "
            f"is below the committed floor {REFUSED_DISTINCT_FLOOR} — "
            "over-constraining novelty is the dossier's named risk for "
            "constraint systems"
        )
    elif incumbent_validity_after is None:
        verdict, reason = "watch", (
            "raises validity at its documented job; no incumbent "
            "comparison provided at this call"
        )
    elif (
        validity_after > incumbent_validity_after + noise_validity
        and distinct_after >= (incumbent_distinct_after or 0.0) - noise_distinct
    ):
        verdict, reason = "prototype", (
            f"beats the incumbent _finish on validity "
            f"({validity_after} vs {incumbent_validity_after}, noise "
            f"{noise_validity}) without worse distinct retention"
        )
    elif validity_after >= incumbent_validity_after - noise_validity:
        verdict, reason = "watch", (
            f"ties the incumbent _finish within the measured noise floor "
            f"({validity_after} vs {incumbent_validity_after}, noise "
            f"{noise_validity}); a tie is not a reason to replace a "
            "shipped incumbent"
        )
    else:
        verdict, reason = "reject", (
            f"loses to the incumbent _finish beyond noise "
            f"({validity_after} vs {incumbent_validity_after}, noise "
            f"{noise_validity}) — the DR 0031 hybrid-refutation logic: a "
            "challenger that adds nothing over the shipped incumbent is "
            "refused"
        )
    return {
        "arm": arm,
        "role": "post_generator_stabilizer",
        "verdict": verdict,
        "reason": reason,
        "inputs": {
            "validity_before": validity_before,
            "validity_after": validity_after,
            "distinct_before": distinct_before,
            "distinct_after": distinct_after,
            "distinct_retention": round(retention, 6),
            "incumbent_validity_after": incumbent_validity_after,
            "incumbent_distinct_after": incumbent_distinct_after,
            "noise_validity": noise_validity,
            "noise_distinct": noise_distinct,
        },
    }


# --------------------------------------------------------------------------
# The harness.
# --------------------------------------------------------------------------


def _raw_collapse_corpus(
    model: dict, *, count: int, rng_seed: int
) -> tuple[list[dict], int]:
    """Collapse-only candidates: the incumbent's own RNG discipline, no
    stabilizer of any kind (restarts fire on wave contradiction only)."""
    grids: list[dict] = []
    failures = 0
    for index in range(count):
        grid_id = f"mg_raw_{index:03d}"
        rng = random.Random(f"{rng_seed}:{grid_id}")
        matrix = None
        for _ in range(MAX_RESTARTS):
            matrix = _collapse(model, rng)
            if matrix is not None:
                break
        if matrix is None:
            failures += 1
            continue
        palette_id = rng.choice(sorted(PALETTES))
        grids.append(
            grid_from_matrix(
                grid_id,
                ["".join(row) for row in matrix],
                palette_id,
                source="stage2_raw_collapse",
                mutation_events=["wfc_wave_collapsed_unstabilized"],
            )
        )
    return grids, failures


def _incumbent_corpus(
    model: dict, *, count: int, rng_seed: int
) -> tuple[list[dict], int]:
    """The shipped pipeline verbatim: generate_wfc_grid, restarts and all.
    Same grid ids and seed discipline as build_wfc_corpus, so at the
    committed protocol this reproduces the committed wfc row exactly."""
    grids: list[dict] = []
    failures = 0
    for index in range(count):
        try:
            grids.append(
                generate_wfc_grid(
                    model, grid_id=f"mg_wfc_{index:03d}", rng_seed=rng_seed
                )
            )
        except ValueError:
            failures += 1
    return grids, failures


def _distinct_rate(measures: dict) -> float:
    return round(
        measures["unique_silhouettes"] / measures["candidate_count"], 6
    )


def build_stage2_arms_report(
    *,
    count: int = BATCH_COUNT,
    size: int = 16,
    rng_seed: int = RNG_SEED,
    noise_seed: int = NOISE_SEED,
) -> dict:
    if size != 16:
        raise ValueError(
            "the stabilizer bake-off runs over the 16x16 seed corpus "
            f"(DR 0029); got size {size}"
        )

    committed = json.loads(
        (ROOT / COMMITTED_BAKEOFF).read_text(encoding="utf-8")
    )
    committed_arms = committed["metrics"]["arms"]
    baseline_row = committed_arms["constrained"]
    committed_wfc = committed_arms["wfc"]
    random_row = committed_arms["random"]

    committed_floor = round(
        random_row["unique_silhouettes"] / random_row["candidate_count"], 6
    )
    if abs(committed_floor - REFUSED_DISTINCT_FLOOR) > 1e-9:
        raise ValueError(
            "REFUSED_DISTINCT_FLOOR has drifted from the committed refused "
            f"random arm ({committed_floor} committed vs "
            f"{REFUSED_DISTINCT_FLOOR} in this module)"
        )

    train, _dev, _holdout = split_corpus(build_seed_grids_16())
    modal_roles = _modal_roles(train)
    model = train_wfc_model(train)

    # --- CPPN, judged as a generator on the bake-off's own terms -------
    cppn_corpus = build_cppn_corpus(count=count, rng_seed=rng_seed, size=size)
    cppn_measures = measure_arm(cppn_corpus, train, modal_roles)
    judged_cppn = judge_generator_arm(
        arm="cppn",
        validity_rate=cppn_measures["validity_rate"],
        baseline_validity_rate=baseline_row["validity_rate"],
        readability=cppn_measures["readability_proxy_mean"],
        baseline_readability=baseline_row["readability_proxy_mean"],
        distinct_rate=_distinct_rate(cppn_measures),
    )

    # --- shape grammar, judged as a stabilizer against _finish ---------
    raw_grids, raw_failures = _raw_collapse_corpus(
        model, count=count, rng_seed=rng_seed
    )
    if not raw_grids:
        raise ValueError("every raw collapse contradicted; nothing to judge")
    grammar_grids = [shape_grammar_stabilize(grid)[0] for grid in raw_grids]
    incumbent_grids, incumbent_failures = _incumbent_corpus(
        model, count=count, rng_seed=rng_seed
    )
    incumbent_second, second_failures = _incumbent_corpus(
        model, count=count, rng_seed=noise_seed
    )

    raw_measures = measure_arm(raw_grids, train, modal_roles)
    grammar_measures = measure_arm(grammar_grids, train, modal_roles)
    incumbent_measures = measure_arm(incumbent_grids, train, modal_roles)
    second_measures = measure_arm(incumbent_second, train, modal_roles)

    noise_validity = round(
        abs(
            incumbent_measures["validity_rate"]
            - second_measures["validity_rate"]
        ),
        6,
    )
    noise_distinct = round(
        abs(_distinct_rate(incumbent_measures) - _distinct_rate(second_measures)),
        6,
    )

    judged_grammar = judge_stabilizer_arm(
        arm="shape_grammar",
        validity_before=raw_measures["validity_rate"],
        validity_after=grammar_measures["validity_rate"],
        distinct_before=_distinct_rate(raw_measures),
        distinct_after=_distinct_rate(grammar_measures),
        incumbent_validity_after=incumbent_measures["validity_rate"],
        incumbent_distinct_after=_distinct_rate(incumbent_measures),
        noise_validity=noise_validity,
        noise_distinct=noise_distinct,
    )

    # --- the instrument gate ------------------------------------------
    instrument_applicable = count == BATCH_COUNT and rng_seed == RNG_SEED
    instrument_keys = (
        "validity_rate",
        "readability_proxy_mean",
        "descriptor_novelty",
        "silhouette_entropy_bits",
        "unique_silhouettes",
    )
    instrument_check: dict = {
        "applicable": instrument_applicable,
        "committed_artifact": COMMITTED_BAKEOFF,
        "committed_row": "wfc",
        "distinct_floor_reproduced": committed_floor,
    }
    if instrument_applicable:
        comparisons = {
            key: {
                "committed": committed_wfc[key],
                "measured": incumbent_measures[key],
                "match": committed_wfc[key] == incumbent_measures[key],
            }
            for key in instrument_keys
        }
        instrument_check["comparisons"] = comparisons
        if not all(entry["match"] for entry in comparisons.values()):
            raise ValueError(
                "instrument check failed: the harness did not reproduce the "
                f"committed wfc row at the committed protocol: {comparisons}"
            )
        instrument_check["reproduced_committed_row"] = True
    else:
        instrument_check["reproduced_committed_row"] = (
            "not_applicable (count/seed differ from the committed protocol)"
        )

    verdicts = {
        "cppn": judged_cppn["verdict"],
        "shape_grammar": judged_grammar["verdict"],
    }
    prediction_outcome = (
        "prediction_confirmed"
        if verdicts == _PREDICTED_VERDICTS
        else (
            f"prediction_refuted: predicted {_PREDICTED_VERDICTS}, "
            f"measured {verdicts}"
        )
    )

    closed_states = [
        "cppn_dispositioned_in_documented_role_generator",
        "shape_grammar_dispositioned_in_documented_role_stabilizer",
        "charter_framing_correction_recorded (a bake-off-both framing would "
        "have tested shape grammar at a job the dossier never gave it)",
    ]
    if instrument_applicable:
        closed_states.append(
            "instrument_reproduced_committed_wfc_row (batch "
            f"{BATCH_COUNT}, seed {RNG_SEED})"
        )

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete",
        "date": REPORT_DATE,
        "purpose": (
            "Disposition Stage 2's two undispositioned generator arms — "
            "CPPN and shape grammar — each in its DOCUMENTED role (the O4 "
            "charter correction): CPPN as a generator on the B2 bake-off's "
            "own terms against the adopted constrained layer's committed "
            "row (DR 0042), shape grammar as a post-generator stabilizer "
            "head-to-head against the incumbent wfc_grid._finish "
            "(DR 0031). The rule and the prediction were pre-registered; "
            "rejecting both is first-class."
        ),
        "source_artifacts": [
            "labs/wfc_grid/wfc_grid.py",
            "labs/wfc_grid/generation_bakeoff16.py",
            "labs/grid_genome/grid_helpers.py",
            "labs/grid_genome/validator.py",
            "data/wfc_grid/generation_bakeoff16_stage0.json",
            "data/seed_grids_16x16",
            "docs/project-research/deep-research/01/deep-research.md",
            "research/decision_records/0031-wfc-generation-adoption.md",
            "research/decision_records/0042-generation-layer-loop-revisit.md",
        ],
        "parameters": {
            "count": count,
            "size": size,
            "rng_seed": rng_seed,
            "noise_seed": noise_seed,
            "committed_batch_count": BATCH_COUNT,
            "committed_rng_seed": RNG_SEED,
            "raw_collapse_failures": raw_failures,
            "incumbent_pipeline_failures": incumbent_failures,
            "incumbent_second_seed_failures": second_failures,
        },
        "metrics": {
            "instrument_check": instrument_check,
            "cppn": {
                "measures": cppn_measures,
                "baseline_committed_row": {
                    key: baseline_row[key] for key in instrument_keys
                },
                "judged": judged_cppn,
            },
            "shape_grammar": {
                "raw_collapse": raw_measures,
                "grammar_stabilized": grammar_measures,
                "incumbent_finish": incumbent_measures,
                "incumbent_finish_second_seed": second_measures,
                "noise": {
                    "validity": noise_validity,
                    "distinct": noise_distinct,
                    "derivation": (
                        "the incumbent pipeline run twice, seeds "
                        f"{rng_seed} and {noise_seed}, |delta| per metric "
                        "(cycle 22 L3's pattern)"
                    ),
                },
                "judged": judged_grammar,
            },
        },
        "closed_states": closed_states,
        "blocked_states": [
            "cppn_under_evolutionary_mutation_not_measured (the indirect "
            "encoding's documented selling point is regularity under "
            "mutation; a generator-only bake-off cannot see it — the "
            "re-opener if CPPN ever returns)",
            "shape_grammar_as_standalone_validator_not_separately_judged "
            "(the dossier stance's other half; the engine's validate_grid "
            "already holds that job)",
            "human_pairwise_preference_not_collected (owner-deferred; "
            "never a blocker)",
            "24x24_not_measured (DR 0014's re-opener would apply to any "
            "adopted generator; nothing is adopted here)",
        ],
        "decision": {
            "rule": PRE_REGISTERED_RULE,
            "prediction": PRE_RUN_PREDICTION,
            "arms": {"cppn": judged_cppn, "shape_grammar": judged_grammar},
            "prediction_outcome": prediction_outcome,
        },
        "next_research_step": (
            "Register both dispositions in the ledger (algorithm cards + "
            "decision record); the named blocked_states are the only "
            "documented paths back."
        ),
    }


def write_stage2_arms_artifacts(
    output_dir: str | Path, report: dict
) -> list[Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{ARTIFACT_ID}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage 2's undispositioned generator arms (cycle 25 O4)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "wfc_grid"
    )
    parser.add_argument("--count", type=int, default=BATCH_COUNT)
    parser.add_argument("--size", type=int, default=16)
    args = parser.parse_args()
    report = build_stage2_arms_report(count=args.count, size=args.size)
    written = write_stage2_arms_artifacts(args.output_dir, report)
    print(json.dumps(report["metrics"]["instrument_check"], indent=2))
    print(json.dumps(report["decision"]["arms"], indent=2))
    print(json.dumps(report["decision"]["prediction_outcome"], indent=2))
    print(f"wrote {written[0].relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
