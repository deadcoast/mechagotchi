"""Cycle 24 N1: do 600 creatures determine the octile edges?

E1 derives the whole scale geometry — the edges every coverage and QD
number in the ledger is counted against — from a **600-candidate**
derivation population. M2 (DR 0046) measured, as a control for something
else entirely, that re-deriving that same recipe at a different seed
**re-addresses 20% of a population**, and the probe recipe **31%**. The
split M2 was sent to decide turned out not to be the disease; this is:

> **The octile edges may not be determined by a 600-creature
> derivation at all.**

That is a defect *underneath every coverage number in the ledger*, and
it is a question about E1's derivation *protocol*, not about which
population feeds it. This module measures the protocol.

**It changes no geometry.** It measures whether the process that
produces them is sound, and both answers are real findings.

THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN
===============================================

**The statistic** is the **re-addressing rate** R(N): the fraction of
one common, fixed evaluation population that receives a **different
descriptor address** under two independent derivations of size N. This
is exactly M2's control statistic, now as a function of derivation size,
and it is deliberately the unit DR 0046 established — *a niche is a
whole address*, and edge distance is not the unit any ledger number is
expressed in.

Measured over **disjoint seed pairs**, so each rung carries a measured
spread rather than a single draw.

**Gate 1 — the mechanism. Is the instability curable by spending
derivation budget?** Quantile estimates converge at N^-1/2, so if the
re-addressing is ordinary sampling error, R(N) falls with a log-log
slope of **-0.5**. The comparison is against the **MEASURED** spread of
the per-track slopes, never a constant:

* ``sampling_limited`` — the theory slope lies inside the measured band.
  The protocol is sound and 600 is simply too small; a bigger derivation
  fixes it, and N2 can freeze at a size this study names.
* ``structurally_indeterminate`` — the curve is materially **flatter**
  than theory. More budget does **not** fix it: the edges are not
  determined by any affordable population, which is what K3's
  measure-thinness and L3's 0.046-wide band predict.
* ``faster_than_sampling`` — steeper than theory. Unexpected, and
  first-class rather than quietly folded into "consistent".

**Gate 2 — the practical question. Is 600 enough for what the edges are
USED for?** Individual addresses are not what the ledger quotes;
occupied-niche counts are. So the second gate is measured in that unit,
against a floor that is **measured, never assumed**: hold the edges
fixed and resample the **evaluation** population, and the occupied count
moves by an amount that has nothing to do with derivation size. That is
the instrument's own noise. ``determined_at`` is the smallest ladder
size whose derivation-induced movement falls at or below it, and
``not_determined_within_reach`` is a first-class verdict.

**These two gates can disagree, and that is the point.** Addresses can
be wildly unstable while the aggregate they feed is not. Reporting only
one of them would be the kind of sentence Phase M kept catching.

**The instrument validates itself against a committed number.** At
N = 600 on M2's own seed pair this ladder must reproduce DR 0046's
incumbent control of **0.2 exactly**. If it does not, the ladder is
measuring something M2 did not, and no rung on it is interpretable.
"""

import argparse
import json
import sys
import time
from math import log
from pathlib import Path
from statistics import mean, stdev

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from niche_scale_archive import (  # noqa: E402
    DEFAULT_RNG_SEED,
    EVALUATION_STREAM_OFFSET,
    SCALE_BINS_PER_AXIS,
    SCALE_DESCRIPTOR_NAMES,
    TOTAL_SCALE_NICHES,
    build_population,
    derive_scale_bin_edges,
    scale_axis_values,
    scale_descriptor_for_values,
    _load_default_slip,
)
from corpus_builder import build_seed_grids_16  # noqa: E402
from wfc_grid import split_corpus, train_wfc_model  # noqa: E402
from wfc_population_throughput import load_frozen_scale_edges  # noqa: E402

ARTIFACT_ID = "derivation_size_stability_stage0"
REPORT_DATE = "2026-07-27"

# E1's own derivation size — the number this study is named after.
E1_DERIVATION_COUNT = 600

# The ladder brackets E1 on both sides and spans 64x, which is the lever
# arm a log-log slope needs. The smallest rung still exceeds the 8 values
# derive_scale_bin_edges requires for 8 octiles.
DERIVATION_SIZE_LADDER = (75, 150, 300, 600, 1200, 2400, 4800)

# Eight replicate seeds -> four DISJOINT pairs, so each rung's rate
# carries a measured spread instead of a single draw.
REPLICATE_SEED_COUNT = 8

# Both recipes L3 found the repo running, because N2 (freezing the
# probe's edges) needs to know what size to freeze AT.
RECIPES = ("incumbent", "probe")

# Sampling theory for quantile estimates: the standard error of an
# empirical quantile falls as N^-1/2, and for a locally-smooth density
# the re-addressed fraction is proportional to the edge displacement.
SAMPLING_THEORY_SLOPE = -0.5

# The repo's control factor (L3, M1, M2), applied here to a MEASURED
# spread of per-track slopes rather than to a threshold.
SLOPE_CONTROL_FACTOR = 2.0

# Evaluation replicates live far from the derivation stream so the floor
# is not measured on a population a derivation already saw.
EVALUATION_POPULATION_STRIDE = 100 * EVALUATION_STREAM_OFFSET

# DR 0046's committed controls, quoted here so the reproduction check is
# against the record rather than against a fresh opinion of it.
DR0046_COMMITTED_CONTROLS = {"incumbent": 0.2, "probe": 0.310333}

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 24 N1), two gates, every verdict "
    "first-class. The statistic is the RE-ADDRESSING RATE R(N): the "
    "fraction of one common evaluation population that receives a "
    "different descriptor address under two independent derivations of "
    "size N — DR 0046's unit, because a niche is a whole address and "
    "edge distance is not the unit any ledger number is counted in. "
    "GATE 1 (mechanism): fit log R against log N; sampling theory for "
    f"quantile estimates predicts a slope of {SAMPLING_THEORY_SLOPE}. "
    "Judge it against the MEASURED spread of the per-track slopes at "
    f"{SLOPE_CONTROL_FACTOR}x, never against a constant — "
    "'sampling_limited' if theory lies inside the measured band (the "
    "protocol is sound and 600 is merely small), "
    "'structurally_indeterminate' if the curve is materially flatter "
    "(no affordable population determines the edges), "
    "'faster_than_sampling' if steeper. GATE 2 (practical): the "
    "derivation-induced movement in OCCUPIED-NICHE COUNT, against a "
    "MEASURED floor — the movement that same count shows when the "
    "edges are held fixed and the evaluation population is resampled. "
    "'determined_at' is the smallest ladder size reaching that floor; "
    "'not_determined_within_reach' is first-class. The two gates may "
    "disagree, and reporting only one of them would hide the finding."
)

GEOMETRY_UNCHANGED_NOTE = (
    "This study moves no geometry and retracts no number. Every "
    "committed coverage, QD and reachability figure stays true under "
    "the edges it was measured with, and DR 0046's comparability rule "
    "still governs how they may be quoted. What is measured here is "
    "whether the PROTOCOL that produces those edges determines them — "
    "a question about what the edges mean, not about whether the "
    "numbers counted against them were counted correctly."
)


def derivation_replicate_seeds(
    count: int = REPLICATE_SEED_COUNT, rng_seed: int = DEFAULT_RNG_SEED
) -> list[int]:
    """Replicate seeds on the repo's existing disjoint-stream stride.

    Deliberately begins at ``DEFAULT_RNG_SEED``, so the FIRST pair is
    exactly M2's pair and the ladder reproduces DR 0046 by construction
    rather than by a separate special case.
    """
    if count < 2 or count % 2 != 0:
        raise ValueError(
            f"replicate seeds must be an even count of at least 2: {count!r}"
        )
    return [rng_seed + index * EVALUATION_STREAM_OFFSET for index in range(count)]


def disjoint_pairs(seeds: list[int]) -> list[tuple[int, int]]:
    """Non-overlapping seed pairs — independence over pair count.

    All C(n,2) pairs would give more comparisons that share draws; these
    share none, so their spread is a measurement rather than an artefact
    of reuse.
    """
    if len(seeds) < 2 or len(seeds) % 2 != 0:
        raise ValueError(
            "disjoint pairing needs an even number of at least two seeds: "
            f"{len(seeds)}"
        )
    return [(seeds[i], seeds[i + 1]) for i in range(0, len(seeds), 2)]


def readdressing_rate(
    first: list[tuple[int, ...]], second: list[tuple[int, ...]]
) -> float:
    """Fraction of a population that changes ADDRESS between two geometries.

    DR 0046's statistic verbatim: a descriptor is a whole address, so one
    axis off by one octile is a different niche, not a partial match.
    """
    if len(first) != len(second):
        raise ValueError(
            "the same population must be addressed under both derivations: "
            f"{len(first)} vs {len(second)}"
        )
    if not first:
        raise ValueError("an empty population has no addresses to compare")
    differing = sum(1 for a, b in zip(first, second) if a != b)
    return round(differing / len(first), 6)


def per_axis_readdressing(
    first: list[tuple[int, ...]], second: list[tuple[int, ...]]
) -> dict:
    """Where the movement lives — the headline rate says only that it does."""
    if len(first) != len(second):
        raise ValueError(
            "the same population must be addressed under both derivations: "
            f"{len(first)} vs {len(second)}"
        )
    if not first:
        raise ValueError("an empty population has no addresses to compare")
    return {
        name: round(
            sum(1 for a, b in zip(first, second) if a[index] != b[index])
            / len(first),
            6,
        )
        for index, name in enumerate(SCALE_DESCRIPTOR_NAMES)
    }


def log_log_slope(sizes: list[int], rates: list[float]) -> float:
    """Least-squares slope of log(rate) against log(size).

    A zero rate is REFUSED rather than clamped: it is a real outcome
    (a geometry that stopped moving entirely) and must be reported as
    that, not smuggled into a fit as an epsilon.
    """
    if len(sizes) != len(rates):
        raise ValueError(
            f"sizes and rates must pair up: {len(sizes)} vs {len(rates)}"
        )
    if len(sizes) < 2:
        raise ValueError(
            f"a slope needs at least two ladder rungs, got {len(sizes)}"
        )
    if any(size <= 0 for size in sizes):
        raise ValueError(f"derivation sizes must be positive: {sizes!r}")
    if any(rate <= 0 for rate in rates):
        raise ValueError(
            "a non-positive re-addressing rate cannot be fitted on a log "
            f"scale — report it, never clamp it: {rates!r}"
        )
    xs = [log(size) for size in sizes]
    ys = [log(rate) for rate in rates]
    x_mean, y_mean = mean(xs), mean(ys)
    denominator = sum((x - x_mean) ** 2 for x in xs)
    if denominator == 0:
        raise ValueError("every ladder rung is the same size; no slope exists")
    numerator = sum(
        (x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)
    )
    return numerator / denominator


def judge_derivation_protocol(*, slope: float, slope_spread: float) -> dict:
    """GATE 1, applied. Every verdict is first-class."""
    if slope_spread < 0:
        raise ValueError(f"a measured spread cannot be negative: {slope_spread!r}")
    half_width = SLOPE_CONTROL_FACTOR * slope_spread
    low, high = slope - half_width, slope + half_width
    if low <= SAMPLING_THEORY_SLOPE <= high:
        verdict = "sampling_limited"
    elif high < SAMPLING_THEORY_SLOPE:
        verdict = "faster_than_sampling"
    else:
        verdict = "structurally_indeterminate"
    return {
        "verdict": verdict,
        "slope": round(slope, 6),
        "slope_spread": round(slope_spread, 6),
        "consistent_band": [low, high],
        "theory_slope": SAMPLING_THEORY_SLOPE,
        "factor": SLOPE_CONTROL_FACTOR,
        "reading": {
            "sampling_limited": (
                "the re-addressing is ordinary sampling error: the "
                "protocol is sound and 600 is merely too small, so a "
                "larger derivation buys a determinate geometry"
            ),
            "structurally_indeterminate": (
                "the curve is materially flatter than sampling theory: "
                "more derivation budget does NOT buy determinacy, and "
                "the octile edges are not determined by any affordable "
                "population"
            ),
            "faster_than_sampling": (
                "the curve falls faster than sampling theory predicts — "
                "unexpected, and recorded as its own outcome rather "
                "than folded into agreement"
            ),
        }[verdict],
    }


def judge_determined_size(*, movement_by_size: dict, floor: float) -> dict:
    """GATE 2, applied against a MEASURED floor."""
    if not movement_by_size:
        raise ValueError("no ladder rungs to judge")
    if floor <= 0:
        raise ValueError(
            "the evaluation-resampling floor must be positive — a zero "
            "floor would make every movement infinitely significant; "
            "measure it, never assume it"
        )
    reaching = sorted(
        size for size, movement in movement_by_size.items() if movement <= floor
    )
    determined_at = reaching[0] if reaching else None
    e1_movement = movement_by_size.get(E1_DERIVATION_COUNT)
    return {
        "verdict": (
            "determined"
            if determined_at is not None
            else "not_determined_within_reach"
        ),
        "determined_at": determined_at,
        "floor": round(floor, 6),
        "e1_derivation_count": E1_DERIVATION_COUNT,
        "e1_movement": (
            None if e1_movement is None else round(e1_movement, 6)
        ),
        "e1_size_determined": (
            e1_movement is not None and e1_movement <= floor
        ),
        "largest_size_measured": max(movement_by_size),
    }


def measure_derivation_unit(
    *, sample_count: int = 200, rng_seed: int = DEFAULT_RNG_SEED
) -> dict:
    """Wall-clock pilot (DR 0028: FIRST, and derived rather than picked).

    One unit = generate one candidate + measure its three axis values.
    Machine-dependent; lives only in the artifact's ``measured`` section
    and is never asserted by a test.
    """
    slip_profile = _load_default_slip()
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    wfc_model = train_wfc_model(train)

    build_start = time.perf_counter()
    population, _ = build_population(sample_count, rng_seed, train, wfc_model)
    build_ms = (time.perf_counter() - build_start) * 1000

    axis_start = time.perf_counter()
    for grid in population:
        scale_axis_values(grid, slip_profile=slip_profile)
    axis_ms = (time.perf_counter() - axis_start) * 1000

    mean_ms = round((build_ms + axis_ms) / sample_count, 4)
    ladder_grid_total = (
        sum(DERIVATION_SIZE_LADDER) * REPLICATE_SEED_COUNT * len(RECIPES)
    )
    return {
        "context": (
            "stage-0 dev machine; excludes one-time seed/model setup; "
            "one unit is mixed constrained+WFC generation of one "
            "candidate plus its three scale-axis measurements (no "
            "lifecycle scoring — a derivation population is never scored)"
        ),
        "derivation_unit": {
            "sample_count": sample_count,
            "build_ms_total": round(build_ms, 2),
            "axis_ms_total": round(axis_ms, 2),
            "mean_ms_per_grid": mean_ms,
        },
        "projections": {
            "ladder_grid_total": ladder_grid_total,
            "full_ladder_s": round(mean_ms * ladder_grid_total / 1000, 2),
        },
    }


def _axis_values_for(population: list[dict], slip_profile: dict) -> list[dict]:
    return [
        scale_axis_values(grid, slip_profile=slip_profile) for grid in population
    ]


def _edges_from_values(values: list[dict]) -> dict:
    return {
        name: derive_scale_bin_edges([value[name] for value in values])
        for name in SCALE_DESCRIPTOR_NAMES
    }


def _address_values(values: list[dict], edges: dict) -> list[tuple[int, ...]]:
    return [scale_descriptor_for_values(value, edges) for value in values]


def _edge_band_widths(edges: dict) -> dict:
    """How tightly the seven interior edges are packed, per axis.

    M2 localised the split to ``visual_complexity``, whose edges sit in a
    band about 0.046 wide — thin enough that a movement far inside
    sampling noise re-addresses a quarter of the population.
    """
    return {
        name: round(max(edges[name]) - min(edges[name]), 6)
        for name in SCALE_DESCRIPTOR_NAMES
    }


def _distinct_fraction(population: list[dict]) -> float:
    """Is the generator still producing new creatures at this size?

    A derivation population that has saturated is not a larger sample of
    the distribution — it is the same sample counted twice, and a ladder
    that ignored this would read saturation as convergence.
    """
    signatures = {
        tuple(
            sorted(
                (cell["x"], cell["y"], cell["role"])
                for cell in grid.get("cells", [])
            )
        )
        for grid in population
    }
    return round(len(signatures) / len(population), 6)


def _spread(values: list[float]) -> float:
    return round(stdev(values), 6) if len(values) > 1 else 0.0


def build_derivation_size_stability_report(
    *,
    size_ladder: tuple[int, ...] = DERIVATION_SIZE_LADDER,
    replicate_seed_count: int = REPLICATE_SEED_COUNT,
    evaluation_count: int = 3000,
    evaluation_replicate_count: int = 6,
    recipes: tuple[str, ...] = RECIPES,
    rng_seed: int = DEFAULT_RNG_SEED,
) -> dict:
    started = time.perf_counter()
    slip_profile = _load_default_slip()
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    wfc_model = train_wfc_model(train)

    # The two recipes L3 named, each defined by the corpus it draws from.
    sources = {"incumbent": train, "probe": seeds}

    # --- the evaluation populations -----------------------------------
    # Replicate 0 is M2's own evaluation population, so the reproduction
    # check compares like with like. The rest measure the floor.
    evaluation_values: list[list[dict]] = []
    for index in range(evaluation_replicate_count):
        population, _ = build_population(
            evaluation_count,
            rng_seed + EVALUATION_STREAM_OFFSET + index * EVALUATION_POPULATION_STRIDE,
            seeds,
            wfc_model,
        )
        evaluation_values.append(_axis_values_for(population, slip_profile))
    common_values = evaluation_values[0]

    # --- GATE 2's floor: fixed edges, resampled evaluation population --
    frozen_edges = load_frozen_scale_edges()
    frozen_ceilings = [
        len(set(_address_values(values, frozen_edges)))
        for values in evaluation_values
    ]
    floor_pairs = [
        abs(frozen_ceilings[i] - frozen_ceilings[i + 1])
        for i in range(0, len(frozen_ceilings) - 1, 2)
    ]
    evaluation_floor = round(mean(floor_pairs), 6) if floor_pairs else 0.0

    # --- the ladder ----------------------------------------------------
    replicate_seeds = derivation_replicate_seeds(replicate_seed_count, rng_seed)
    pairs = disjoint_pairs(replicate_seeds)

    ladder: dict[str, dict] = {recipe: {} for recipe in recipes}
    for recipe in recipes:
        corpus = sources[recipe]
        for size in size_ladder:
            edges_by_seed: dict[int, dict] = {}
            first_distinct = None
            for seed in replicate_seeds:
                population, _ = build_population(size, seed, corpus, wfc_model)
                if first_distinct is None:
                    first_distinct = _distinct_fraction(population)
                edges_by_seed[seed] = _edges_from_values(
                    _axis_values_for(population, slip_profile)
                )

            addressed = {
                seed: _address_values(common_values, edges)
                for seed, edges in edges_by_seed.items()
            }
            ceilings = {
                seed: len(set(addresses)) for seed, addresses in addressed.items()
            }

            rates, movements, per_axis_by_pair = [], [], []
            for left, right in pairs:
                rates.append(readdressing_rate(addressed[left], addressed[right]))
                movements.append(abs(ceilings[left] - ceilings[right]))
                per_axis_by_pair.append(
                    per_axis_readdressing(addressed[left], addressed[right])
                )

            band_widths = [
                _edge_band_widths(edges) for edges in edges_by_seed.values()
            ]
            ladder[recipe][str(size)] = {
                "derivation_count": size,
                "readdressing_by_pair": rates,
                "readdressing_mean": round(mean(rates), 6),
                "readdressing_spread": _spread(rates),
                "per_axis_readdressing_mean": {
                    name: round(
                        mean(entry[name] for entry in per_axis_by_pair), 6
                    )
                    for name in SCALE_DESCRIPTOR_NAMES
                },
                "support_ceiling_by_seed": [
                    ceilings[seed] for seed in replicate_seeds
                ],
                "ceiling_movement_by_pair": movements,
                "ceiling_movement_mean": round(mean(movements), 6),
                "edge_band_width_mean": {
                    name: round(mean(width[name] for width in band_widths), 6)
                    for name in SCALE_DESCRIPTOR_NAMES
                },
                "first_replicate_distinct_fraction": first_distinct,
                "first_replicate_edges": edges_by_seed[replicate_seeds[0]],
            }

    # --- GATE 1: a slope per independent track, then their spread ------
    slope_fits: dict[str, dict] = {}
    for recipe in recipes:
        track_slopes, unfittable = [], []
        for index in range(len(pairs)):
            rungs = [
                (size, ladder[recipe][str(size)]["readdressing_by_pair"][index])
                for size in size_ladder
            ]
            usable = [(size, rate) for size, rate in rungs if rate > 0]
            if len(usable) < 2:
                unfittable.append(index)
                continue
            track_slopes.append(
                log_log_slope([size for size, _ in usable], [rate for _, rate in usable])
            )
        slope_fits[recipe] = {
            "track_slopes": [round(value, 6) for value in track_slopes],
            "slope_mean": round(mean(track_slopes), 6) if track_slopes else None,
            "slope_spread": _spread(track_slopes),
            "unfittable_tracks": unfittable,
        }

    # --- the two gates, applied ----------------------------------------
    decision_by_recipe: dict[str, dict] = {}
    for recipe in recipes:
        fit = slope_fits[recipe]
        if fit["slope_mean"] is None:
            mechanism = {
                "verdict": "not_measurable",
                "reason": (
                    "no track had two or more rungs with a positive "
                    "re-addressing rate, so no slope exists to judge"
                ),
            }
        else:
            mechanism = judge_derivation_protocol(
                slope=fit["slope_mean"], slope_spread=fit["slope_spread"]
            )
        movement_by_size = {
            size: ladder[recipe][str(size)]["ceiling_movement_mean"]
            for size in size_ladder
        }
        if evaluation_floor <= 0:
            practical = {
                "verdict": "floor_not_measurable",
                "reason": (
                    "the evaluation-resampling floor measured 0 at this "
                    "evaluation size: the instrument cannot resolve a "
                    "floor here, and no substitute is invented for it"
                ),
                "floor": evaluation_floor,
                "determined_at": None,
                "e1_size_determined": False,
            }
        else:
            practical = judge_determined_size(
                movement_by_size=movement_by_size, floor=evaluation_floor
            )
        decision_by_recipe[recipe] = {
            "mechanism": mechanism,
            "practical": practical,
        }

    # --- the instrument's own validation against DR 0046 ---------------
    reproduction = {}
    for recipe in recipes:
        rung = ladder[recipe].get(str(E1_DERIVATION_COUNT))
        committed = DR0046_COMMITTED_CONTROLS[recipe]
        measured = None
        if (
            rung is not None
            and evaluation_count == 3000
            and replicate_seeds[0] == DEFAULT_RNG_SEED
        ):
            measured = rung["readdressing_by_pair"][0]
        applicable = measured is not None
        reproduction[recipe] = {
            "committed": committed,
            "measured": measured,
            "reproduced": applicable and measured == committed,
            "applicable": applicable,
        }

    wall_clock_s = round(time.perf_counter() - started, 3)

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 24 N1: measure whether E1's 600-creature derivation "
            "DETERMINES the octile edges, by running the re-addressing "
            "rate as a function of derivation size against two "
            "pre-registered gates — a mechanism gate against sampling "
            "theory's own convergence rate, and a practical gate "
            "against the MEASURED movement the occupied-niche count "
            "shows when only the evaluation population is resampled."
        ),
        "source_artifacts": [
            "data/archives/geometry_decision_stage0.json",
            "data/archives/geometry_consistency_stage0.json",
            "data/archives/niche_scale_archive_stage0.json",
            "data/archives/occupancy_saturation_stage0.json",
            "data/archives/reachability_probe_stage0.json",
        ],
        "parameters": {
            "size_ladder": list(size_ladder),
            "replicate_seed_count": replicate_seed_count,
            "replicate_seeds": replicate_seeds,
            "disjoint_pairs": [list(pair) for pair in pairs],
            "evaluation_count": evaluation_count,
            "evaluation_replicate_count": evaluation_replicate_count,
            "recipes": list(recipes),
            "bins_per_axis": SCALE_BINS_PER_AXIS,
            "total_niches": TOTAL_SCALE_NICHES,
            "recipe_definitions": {
                "incumbent": (
                    "build_population(N, seed, TRAIN, wfc_model) — E1's "
                    "own protocol, whose output is frozen and committed "
                    "and carries every coverage/QD number in the ledger"
                ),
                "probe": (
                    "build_population(N, seed, ALL 50 SEEDS, wfc_model) "
                    "— re-derived live by reachability_probe and "
                    "occupancy_saturation; measured here because N2 must "
                    "choose a size to freeze it AT"
                ),
            },
        },
        "metrics": {
            "ladder": ladder,
            "slope_fits": slope_fits,
            "evaluation_resampling_floor": {
                "floor": evaluation_floor,
                "frozen_edge_ceilings": frozen_ceilings,
                "pairwise_movements": floor_pairs,
                "unit": "occupied niches (of %d)" % TOTAL_SCALE_NICHES,
                "method": (
                    "the committed frozen incumbent edges held fixed "
                    "while the evaluation population is resampled at the "
                    "same size — the movement that has nothing to do "
                    "with derivation size"
                ),
            },
            "dr0046_reproduction": reproduction,
            "wall_clock_s": wall_clock_s,
        },
        "closed_states": [
            "edge stability is measured as a FUNCTION of derivation "
            "size, in DR 0046's address unit, rather than at one size",
            "the mechanism gate compares against sampling theory's own "
            "convergence rate, judged by the MEASURED spread of "
            "independent per-track slopes",
            "the practical gate is measured in the unit the ledger "
            "quotes (occupied niches) against a MEASURED floor",
            "the instrument reproduces DR 0046's committed control at "
            "E1's own derivation size, so every rung is interpretable",
            "generator saturation is measured per rung, so a population "
            "that stopped producing new creatures cannot be read as a "
            "geometry that stopped moving",
            GEOMETRY_UNCHANGED_NOTE,
        ],
        "blocked_states": [
            "this study moves no geometry and freezes nothing: acting "
            "on it is N2's charter (freezing the probe's edges) and any "
            "change to E1's derivation size would be its own record",
            "the evaluation population shares an rng seed with the "
            "second derivation replicate, inherited from M2's "
            "construction so DR 0046 reproduces exactly. The draws "
            "differ in size and source corpus and so are not identical, "
            "but they are not formally independent either — recorded "
            "rather than silently re-seeded, because re-seeding would "
            "have cost the reproduction check",
            "the re-addressing statistic counts an address change of "
            "any size (DR 0046's own remainder, inherited): a creature "
            "moving one octile counts the same as one moving three on "
            "all three axes",
            "one common evaluation population carries every rung's "
            "re-addressing rate, so the ladder measures derivation "
            "instability against a fixed ruler and says nothing about "
            "how the rate would move on a different evaluation draw",
        ],
        "decision": {
            "by_recipe": decision_by_recipe,
            "rule": PRE_REGISTERED_RULE,
            "geometry_unchanged": GEOMETRY_UNCHANGED_NOTE,
        },
        "next_research_step": (
            "N2: freeze the probe's edges to a committed artifact with "
            "recorded provenance, at a derivation size this study "
            "names — and re-express 508/512 and the support ceiling "
            "against the frozen set."
        ),
    }


def write_derivation_size_stability_artifacts(
    output_dir: str | Path, report: dict
) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{ARTIFACT_ID}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser(description="Cycle 24 N1: derivation-size stability.")
    parser.add_argument("--output-dir", default=str(ROOT / "data" / "archives"))
    parser.add_argument("--evaluation-count", type=int, default=3000)
    parser.add_argument("--evaluation-replicate-count", type=int, default=6)
    parser.add_argument("--pilot-count", type=int, default=200)
    parser.add_argument("--skip-timing", action="store_true")
    args = parser.parse_args()

    # DR 0028 discipline: the wall-clock pilot runs FIRST.
    if not args.skip_timing:
        measured = measure_derivation_unit(sample_count=args.pilot_count)
        print(json.dumps(measured, indent=2))

    report = build_derivation_size_stability_report(
        evaluation_count=args.evaluation_count,
        evaluation_replicate_count=args.evaluation_replicate_count,
    )
    metrics = report["metrics"]
    floor = metrics["evaluation_resampling_floor"]["floor"]
    print(f"\nevaluation-resampling floor: {floor} niches")
    for recipe, decision in report["decision"]["by_recipe"].items():
        mechanism, practical = decision["mechanism"], decision["practical"]
        print(f"\n[{recipe}]")
        rungs = metrics["ladder"][recipe]
        for size in sorted(int(key) for key in rungs):
            rung = rungs[str(size)]
            print(
                f"  N={size:<5} re-address {rung['readdressing_mean']:.6f} "
                f"(+/-{rung['readdressing_spread']:.6f})  "
                f"ceiling move {rung['ceiling_movement_mean']:.3f}  "
                f"vc band {rung['edge_band_width_mean']['visual_complexity']:.6f}  "
                f"distinct {rung['first_replicate_distinct_fraction']:.4f}"
            )
        print(
            f"  GATE 1 slope {mechanism.get('slope')} "
            f"(spread {mechanism.get('slope_spread')}) -> "
            f"{mechanism['verdict'].upper()}"
        )
        print(
            f"  GATE 2 determined_at {practical['determined_at']} "
            f"(floor {practical['floor']}) -> {practical['verdict'].upper()}"
        )
        reproduction = metrics["dr0046_reproduction"][recipe]
        print(
            f"  DR 0046 control: committed {reproduction['committed']}, "
            f"measured {reproduction['measured']} -> "
            f"{'REPRODUCED' if reproduction['reproduced'] else 'NOT REPRODUCED'}"
        )
    for path in write_derivation_size_stability_artifacts(args.output_dir, report):
        print(f"\nwrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
