"""Cycle 24 N2: freeze the probe's edges.

DR 0046's strongest named follow-on. The repo runs two scale geometries
(DR 0046 froze the split and refused to converge it), and they are
protected very differently:

* the **incumbent** is derived once and **committed** — every consumer
  reads it through ``load_frozen_scale_edges()``;
* the **probe** is **re-derived live on every run** by three separate
  call sites, each carrying its own copy of the recipe.

**THE CHARTER'S PREMISE IS PARTLY WRONG, AND THE REAL DEFECT IS
SHARPER.** The queue recorded that each probe number "is contingent on
a draw **no artifact records**". Read against the engine rather than the
sentence, that is not what is committed:

* ``reachability_probe_stage0.json`` **DOES** record its edges, at
  ``metrics.edges``;
* ``occupancy_saturation_stage0.json`` does **not** — its support
  ceiling of 460 is counted under edges it never writes down;
* ``reachability_escalation_stage0.json`` does **not** either — and K3's
  blocking-axis bounds are expressed as *"the required octile interval
  from the frozen edges"*, against edges that artifact does not carry.

So the defect is not that the probe geometry is unrecorded. It is that
**one artifact records it and two others silently depend on the same
draw**, with nothing pinning any of them together. A re-derivation at a
different seed or count would move all three and only one would show it.

**THIS MODULE MAKES THE DRAW AN OBJECT.** It commits the probe edges
with their regeneration provenance, gives the consumers one loader to
share, and pins the frozen set against a live re-derivation so drift
**fails the suite** instead of quietly re-addressing 31% of creatures
(DR 0049's measured figure for this recipe).

THE RULE IS PRE-REGISTERED HERE, BEFORE ANY RUN. Every verdict is
first-class.

**GATE 1 — PROVENANCE.** The edges frozen here must equal the edges
``reachability_probe_stage0.json`` already records, because that is the
draw the committed 508/512 was counted under. Freezing a *different*
draw would silently redefine every probe-side number in the ledger.
**Structural, with NO TOLERANCE** — the two are supposed to be the same
object, and a tolerance would let a real redefinition pass as rounding.

**GATE 2 — DETERMINISM.** Two independent derivations at the documented
parameters must be identical. DR 0046 asserted the probe is
"deterministic in practice (a fixed default seed)"; this is the first
time that claim is *tested* rather than assumed. The cross-run version
of the same claim is pinned in the suite, which is what makes future
drift fail.

**GATE 3 — CONSUMER INVARIANCE.** The probe-side headline numbers
re-expressed against the frozen set must not move. The bar is
**MEASURED, never assumed** (DR 0049's construction): hold the frozen
edges fixed, resample only the counted population, and the count moves
by an amount that has nothing to do with the freeze. The **tightest** of
the measured floors is taken, because a movement should have to sit
inside the *strictest* noise estimate before it is called noise. This
gate is not a formality — it recomputes the committed numbers from
scratch, and M2 already found one cross-geometry headline (K2's 460)
that did not survive being recounted.

**GATE 4 — SEPARATION.** The frozen probe set must NOT equal the frozen
incumbent set. DR 0046 refused convergence on the measurement; a freeze
that quietly adopted the incumbent edges would undo that record without
saying so.

**This module moves no geometry and re-runs no descent.** The 508/512
count is composed of a binning result (495 reached by generators) and
two engine move-set descents (+8, +5). Only the binning is re-expressed
here; the descent results are unchanged **because the edges are
identical**, which is Gate 1 — not because they were re-run. Had the
edges moved, re-running them would have been mandatory, and that
consequence is recorded rather than hidden.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from statistics import mean

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from niche_scale_archive import (  # noqa: E402
    DEFAULT_RNG_SEED,
    EVALUATION_STREAM_OFFSET,
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

ARTIFACT_ID = "probe_edge_freeze_stage0"
REPORT_DATE = "2026-07-28"

# The documented probe draw — the parameters all three probe-side
# consumers already use, so the freeze captures the draw the committed
# numbers were counted under rather than inventing a new one.
PROBE_DERIVATION_COUNT = 600
PROBE_RNG_SEED = DEFAULT_RNG_SEED

# The committed population sizes the probe-side headlines are counted
# over. Re-expression is only comparable at these sizes.
COMMITTED_EVALUATION_COUNT = 3000
COMMITTED_POOL_COUNT = 9000

_FROZEN_ARTIFACT = ROOT / "data" / "archives" / f"{ARTIFACT_ID}.json"
_PROBE_ARTIFACT = ROOT / "data" / "archives" / "reachability_probe_stage0.json"
_OCCUPANCY_ARTIFACT = ROOT / "data" / "archives" / "occupancy_saturation_stage0.json"

# Where consumers read the frozen set. Stable and documented, because a
# pointer that moves is a second unrecorded draw.
FROZEN_EDGES_POINTER = "metrics.frozen_edges.edges"

REGENERATE_COMMAND = "python -B labs/map_elites_archive/probe_edge_freeze.py"

PROBE_RECIPE = (
    "build_population(N, seed, ALL 50 SEED GRIDS, wfc_model) then "
    "interior octiles of the measured axis distributions — the recipe "
    "reachability_probe and occupancy_saturation each carried their own "
    "copy of before this freeze"
)

PRE_REGISTERED_RULE = (
    "pre-registered (cycle 24 N2), four gates, every verdict "
    "first-class. GATE 1 PROVENANCE: the frozen edges must equal the "
    "edges reachability_probe_stage0.json already records, because that "
    "is the draw the committed 508/512 was counted under — STRUCTURAL, "
    "with NO TOLERANCE, since the two are supposed to be the same "
    "object and a tolerance would let a redefinition pass as rounding. "
    "GATE 2 DETERMINISM: two independent derivations at the documented "
    "parameters must be identical, testing DR 0046's asserted "
    "'deterministic in practice' rather than assuming it. GATE 3 "
    "CONSUMER INVARIANCE: the probe-side headline numbers re-expressed "
    "against the frozen set must not move, judged against a MEASURED "
    "floor — the movement the same count shows when the frozen edges "
    "are held fixed and only the counted population is resampled — "
    "with the TIGHTEST measured floor taken, so a movement must sit "
    "inside the strictest noise estimate before it is called noise. "
    "GATE 4 SEPARATION: the frozen probe set must NOT equal the frozen "
    "incumbent set, because DR 0046 refused convergence and a freeze "
    "that adopted the incumbent edges would undo that record silently."
)

GEOMETRY_UNCHANGED_NOTE = (
    "This freeze moves no geometry and retracts no number. It makes an "
    "existing draw an addressable object with recorded provenance and a "
    "parity pin, so that a future re-derivation FAILS THE SUITE instead "
    "of silently re-addressing creatures. DR 0046's comparability rule "
    "is untouched: probe-geometry numbers and incumbent-geometry "
    "numbers still may not be read against each other."
)

DESCENT_NOT_RERUN_NOTE = (
    "508/512 is a COMPOSED number: 495 bins reached by the generators "
    "(a binning result, re-expressed here) plus 8 from the probe's "
    "engine move-set descent and 5 from K3's escalation (search "
    "results, NOT re-run here). The descent counts are unchanged "
    "because the edges are identical — that is Gate 1 — and not "
    "because they were recomputed. Had the edges moved, re-running "
    "both descents would have been mandatory."
)


def derive_probe_edges(
    *,
    derivation_count: int = PROBE_DERIVATION_COUNT,
    rng_seed: int = PROBE_RNG_SEED,
) -> dict[str, list[float]]:
    """The probe recipe, in ONE place instead of three copies."""
    slip_profile = _load_default_slip()
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    wfc_model = train_wfc_model(train)
    derivation, _ = build_population(derivation_count, rng_seed, seeds, wfc_model)
    return {
        name: derive_scale_bin_edges(
            [
                scale_axis_values(grid, slip_profile=slip_profile)[name]
                for grid in derivation
            ]
        )
        for name in SCALE_DESCRIPTOR_NAMES
    }


def load_frozen_probe_edges() -> dict[str, list[float]]:
    """The probe geometry's standing calibration — the E1 pattern.

    Mirrors ``load_frozen_scale_edges()`` exactly, so the two geometries
    are protected the same way rather than one being privileged.
    """
    if not _FROZEN_ARTIFACT.exists():
        raise FileNotFoundError(
            "the frozen probe edges are not committed yet; regenerate "
            f"with `{REGENERATE_COMMAND}` (cycle 24 N2)"
        )
    artifact = json.loads(_FROZEN_ARTIFACT.read_text(encoding="utf-8"))
    return artifact["metrics"]["frozen_edges"]["edges"]


def load_recorded_probe_edges() -> dict[str, list[float]]:
    """The draw the committed reachability numbers were counted under."""
    artifact = json.loads(_PROBE_ARTIFACT.read_text(encoding="utf-8"))
    return artifact["metrics"]["edges"]


def load_committed_probe_headlines() -> dict[str, int]:
    """READ from the artifacts, never quoted from prose.

    The 52-vs-54 recurrent-family count went stale precisely because
    prose was quoted while the artifact had moved.
    """
    probe = json.loads(_PROBE_ARTIFACT.read_text(encoding="utf-8"))
    occupancy = json.loads(_OCCUPANCY_ARTIFACT.read_text(encoding="utf-8"))
    return {
        "reached_by_generators": int(probe["metrics"]["reached_by_generators"]),
        "support_ceiling": int(
            occupancy["metrics"]["support_ceiling"]["distinct_descriptors"]
        ),
    }


def probe_edges_for(
    *,
    derivation_count: int = PROBE_DERIVATION_COUNT,
    rng_seed: int = PROBE_RNG_SEED,
) -> tuple[dict[str, list[float]], str]:
    """Frozen at the documented draw; live when the caller wants another.

    A caller passing a different count or seed is asking for a different
    geometry — handing back the frozen set would make the parameter a
    lie. The source is returned so every consumer artifact can record
    which one it used, which is the defect this task exists to fix.
    """
    if derivation_count == PROBE_DERIVATION_COUNT and rng_seed == PROBE_RNG_SEED:
        return load_frozen_probe_edges(), "frozen"
    return (
        derive_probe_edges(derivation_count=derivation_count, rng_seed=rng_seed),
        "live",
    )


def judge_provenance(*, frozen: dict, recorded: dict) -> dict:
    """GATE 1 — structural, no tolerance."""
    differing = sorted(
        name
        for name in set(frozen) | set(recorded)
        if frozen.get(name) != recorded.get(name)
    )
    return {
        "verdict": "provenance_matched" if not differing else "provenance_broken",
        "differing_axes": differing,
        "basis": (
            "exact equality with no tolerance — the frozen set and the "
            "draw reachability_probe_stage0.json records are supposed to "
            "be the same object, so any difference is a redefinition of "
            "every committed probe-side number, not a rounding artifact"
        ),
    }


def judge_reproduction(*, frozen: dict, live: dict) -> dict:
    """GATE 2 — determinism of the derivation at fixed parameters."""
    differing = sorted(
        name
        for name in set(frozen) | set(live)
        if frozen.get(name) != live.get(name)
    )
    return {
        "verdict": "reproducible" if not differing else "not_reproducible",
        "differing_axes": differing,
        "basis": (
            "DR 0046 asserted the probe is 'deterministic in practice "
            "(a fixed default seed)'. This measures that claim instead "
            "of inheriting it; the cross-run form is pinned in the suite"
        ),
    }


def judge_separation(*, probe: dict, incumbent: dict) -> dict:
    """GATE 4 — the two geometries must stay two geometries."""
    deltas = []
    for name in set(probe) & set(incumbent):
        for left, right in zip(probe[name], incumbent[name]):
            deltas.append(abs(left - right))
    max_abs_delta = max(deltas) if deltas else 0.0
    identical = probe == incumbent
    return {
        "verdict": "converged" if identical else "separated",
        "max_abs_delta": max_abs_delta,
        "basis": (
            "DR 0046 refused convergence ON THE MEASUREMENT; a freeze "
            "that adopted the incumbent edges would undo that record "
            "without saying so"
        ),
    }


def judge_consumer_invariance(*, movements: dict, floor: float) -> dict:
    """GATE 3 — re-expression against a MEASURED floor."""
    if not movements:
        raise ValueError("no consumer numbers to judge")
    if floor <= 0:
        raise ValueError(
            "the resampling floor must be positive — a zero floor would "
            "make every movement infinitely significant; measure it, "
            "never assume it"
        )
    worst = max(abs(value) for value in movements.values())
    if worst == 0:
        verdict = "invariant"
    elif worst <= floor:
        verdict = "within_measured_floor"
    else:
        verdict = "material"
    return {
        "verdict": verdict,
        "movements": dict(movements),
        "worst_movement": worst,
        "floor": round(floor, 6),
        "basis": (
            "the movement the same count shows when the frozen edges "
            "are held fixed and only the counted population is "
            "resampled, with the TIGHTEST measured floor taken"
        ),
    }


def _distinct_descriptors(values: list[dict], edges: dict) -> int:
    return len({scale_descriptor_for_values(value, edges) for value in values})


def _axis_values(population: list[dict], slip_profile: dict) -> list[dict]:
    return [
        scale_axis_values(grid, slip_profile=slip_profile) for grid in population
    ]


def _resampling_floor(
    *,
    count: int,
    replicates: int,
    edges: dict,
    slip_profile: dict,
    seeds: list[dict],
    wfc_model: dict,
    rng_seed: int,
    stride: int,
) -> dict:
    """Hold the edges fixed; resample the population; measure the move."""
    counts = []
    for index in range(replicates):
        population, _ = build_population(
            count, rng_seed + index * stride, seeds, wfc_model
        )
        counts.append(
            _distinct_descriptors(_axis_values(population, slip_profile), edges)
        )
    movements = [
        abs(counts[i] - counts[i + 1]) for i in range(0, len(counts) - 1, 2)
    ]
    return {
        "population_count": count,
        "replicates": replicates,
        "distinct_counts": counts,
        "pairwise_movements": movements,
        "floor": round(mean(movements), 6) if movements else 0.0,
    }


def build_probe_edge_freeze_report(
    *,
    evaluation_count: int = COMMITTED_EVALUATION_COUNT,
    pool_count: int = COMMITTED_POOL_COUNT,
    evaluation_replicate_count: int = 6,
    pool_replicate_count: int = 4,
    rng_seed: int = PROBE_RNG_SEED,
) -> dict:
    started = time.perf_counter()
    slip_profile = _load_default_slip()
    seeds = build_seed_grids_16()
    train, _, _ = split_corpus(seeds)
    wfc_model = train_wfc_model(train)

    # --- the draw being frozen, derived at the documented parameters --
    frozen_edges = derive_probe_edges(
        derivation_count=PROBE_DERIVATION_COUNT, rng_seed=PROBE_RNG_SEED
    )

    # --- GATE 1: is this the draw the committed numbers used? ---------
    recorded_edges = load_recorded_probe_edges()
    provenance = judge_provenance(frozen=frozen_edges, recorded=recorded_edges)

    # --- GATE 2: is the derivation deterministic at fixed parameters? -
    second_derivation = derive_probe_edges(
        derivation_count=PROBE_DERIVATION_COUNT, rng_seed=PROBE_RNG_SEED
    )
    reproduction = judge_reproduction(frozen=frozen_edges, live=second_derivation)

    # --- GATE 4: the two geometries stay two geometries ---------------
    incumbent_edges = load_frozen_scale_edges()
    separation = judge_separation(probe=frozen_edges, incumbent=incumbent_edges)

    # --- GATE 3: re-express the headlines against the frozen set ------
    committed = load_committed_probe_headlines()

    evaluation_population, _ = build_population(
        evaluation_count, rng_seed + EVALUATION_STREAM_OFFSET, seeds, wfc_model
    )
    support_ceiling = _distinct_descriptors(
        _axis_values(evaluation_population, slip_profile), frozen_edges
    )
    pool_population, _ = build_population(
        pool_count, rng_seed + EVALUATION_STREAM_OFFSET, seeds, wfc_model
    )
    reached_by_generators = _distinct_descriptors(
        _axis_values(pool_population, slip_profile), frozen_edges
    )

    re_expressed = {
        "support_ceiling": {
            "committed": committed["support_ceiling"],
            "re_expressed": support_ceiling,
            "comparable": evaluation_count == COMMITTED_EVALUATION_COUNT,
        },
        "reached_by_generators": {
            "committed": committed["reached_by_generators"],
            "re_expressed": reached_by_generators,
            "comparable": pool_count == COMMITTED_POOL_COUNT,
        },
    }
    for entry in re_expressed.values():
        entry["delta"] = (
            entry["re_expressed"] - entry["committed"] if entry["comparable"] else None
        )

    evaluation_floor = _resampling_floor(
        count=evaluation_count,
        replicates=evaluation_replicate_count,
        edges=frozen_edges,
        slip_profile=slip_profile,
        seeds=seeds,
        wfc_model=wfc_model,
        rng_seed=rng_seed + EVALUATION_STREAM_OFFSET,
        stride=100 * EVALUATION_STREAM_OFFSET,
    )
    pool_floor = _resampling_floor(
        count=pool_count,
        replicates=pool_replicate_count,
        edges=frozen_edges,
        slip_profile=slip_profile,
        seeds=seeds,
        wfc_model=wfc_model,
        rng_seed=rng_seed + EVALUATION_STREAM_OFFSET,
        stride=100 * EVALUATION_STREAM_OFFSET,
    )
    measured_floors = [
        floor["floor"] for floor in (evaluation_floor, pool_floor) if floor["floor"] > 0
    ]
    tightest_floor = min(measured_floors) if measured_floors else 0.0

    movements = {
        name: entry["delta"]
        for name, entry in re_expressed.items()
        if entry["comparable"]
    }
    if not movements:
        invariance = {
            "verdict": "not_comparable",
            "reason": (
                "the re-expression population sizes differ from the "
                "committed ones, so the counts are not comparable and "
                "no substitute is invented for them"
            ),
            "movements": {},
            "floor": tightest_floor,
        }
    elif tightest_floor <= 0:
        invariance = {
            "verdict": "floor_not_measurable",
            "reason": (
                "every resampling floor measured 0 at these population "
                "sizes: the instrument cannot resolve a floor here, and "
                "no substitute is invented for it"
            ),
            "movements": movements,
            "floor": tightest_floor,
        }
    else:
        invariance = judge_consumer_invariance(
            movements=movements, floor=tightest_floor
        )

    gates = {
        "g1_provenance": provenance,
        "g2_determinism": reproduction,
        "g3_consumer_invariance": invariance,
        "g4_separation": separation,
    }
    passed = (
        provenance["verdict"] == "provenance_matched"
        and reproduction["verdict"] == "reproducible"
        and separation["verdict"] == "separated"
        and invariance["verdict"] in ("invariant", "within_measured_floor")
    )

    wall_clock_s = round(time.perf_counter() - started, 3)

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 24 N2: freeze the probe geometry to a committed "
            "artifact with recorded provenance — the way E1's incumbent "
            "edges already are — so the three probe-side consumers stop "
            "re-deriving it live from three private copies of the "
            "recipe, and so a future re-derivation FAILS THE SUITE "
            "instead of silently re-addressing creatures."
        ),
        "source_artifacts": [
            "data/archives/reachability_probe_stage0.json",
            "data/archives/occupancy_saturation_stage0.json",
            "data/archives/reachability_escalation_stage0.json",
            "data/archives/niche_scale_archive_stage0.json",
            "data/archives/geometry_decision_stage0.json",
            "data/archives/derivation_size_stability_stage0.json",
        ],
        "parameters": {
            "evaluation_count": evaluation_count,
            "pool_count": pool_count,
            "evaluation_replicate_count": evaluation_replicate_count,
            "pool_replicate_count": pool_replicate_count,
            "rng_seed": rng_seed,
            "committed_evaluation_count": COMMITTED_EVALUATION_COUNT,
            "committed_pool_count": COMMITTED_POOL_COUNT,
        },
        "metrics": {
            "frozen_edges": {
                "edges": frozen_edges,
                "provenance": {
                    "recipe": PROBE_RECIPE,
                    "derivation_count": PROBE_DERIVATION_COUNT,
                    "rng_seed": PROBE_RNG_SEED,
                    "corpus": (
                        "all 50 seed grids from build_seed_grids_16() — "
                        "NOT the 30-grid train split the incumbent uses; "
                        "the corpus is the whole difference between the "
                        "two geometries"
                    ),
                    "regenerate": REGENERATE_COMMAND,
                    "pointer": FROZEN_EDGES_POINTER,
                    "frozen_on": REPORT_DATE,
                    "sizing_rationale": (
                        "frozen at E1's own 600 on DR 0049's measured "
                        "guidance: a larger derivation buys ADDRESS "
                        "stability but not AGGREGATE stability (the "
                        "probe's occupied-count movement never reaches "
                        "the measured floor anywhere on a 64x ladder), "
                        "while 600 keeps the two geometries "
                        "size-comparable — worth more than a marginal "
                        "rung — and is the draw every committed "
                        "probe-side number was counted under"
                    ),
                },
            },
            "recorded_edges_witness": {
                "source": "data/archives/reachability_probe_stage0.json",
                "pointer": "metrics.edges",
                "edges": recorded_edges,
            },
            "incumbent_edges": incumbent_edges,
            "re_expressed_headlines": re_expressed,
            "evaluation_resampling_floor": evaluation_floor,
            "pool_resampling_floor": pool_floor,
            "tightest_floor": tightest_floor,
            "total_niches": TOTAL_SCALE_NICHES,
            "wall_clock_s": wall_clock_s,
        },
        "closed_states": [
            "the probe geometry is a committed object with recorded "
            "regeneration provenance, protected the same way E1's "
            "incumbent edges are rather than one geometry being "
            "privileged over the other",
            "the recipe lives in ONE place (derive_probe_edges) instead "
            "of three private copies at three call sites",
            "a live re-derivation is pinned against the frozen set, so "
            "drift FAILS THE SUITE instead of silently re-addressing "
            "creatures",
            "DR 0046's asserted determinism is MEASURED rather than "
            "inherited",
            "the committed headline numbers are READ from their "
            "artifacts and recounted, never quoted from prose",
            GEOMETRY_UNCHANGED_NOTE,
            DESCENT_NOT_RERUN_NOTE,
        ],
        "blocked_states": [
            "the two engine move-set descents (+8 probe, +5 escalation) "
            "are NOT re-run here — see the descent note; they are "
            "unchanged because the edges are identical, which is Gate 1",
            "occupancy_saturation and reachability_escalation still do "
            "not record the edges their numbers are counted under in "
            "their OWN artifacts; this task gives them a shared frozen "
            "source and a pin, and regenerating those artifacts to "
            "carry it is a re-run of each, named rather than silently "
            "skipped",
            "the resampling floors are measured at these two population "
            "sizes only, and the tightest is taken; a floor measured "
            "over many more pairs would resolve a smaller movement",
            "DR 0046's comparability rule is untouched: probe-geometry "
            "numbers still may not be read against incumbent-geometry "
            "numbers",
        ],
        "decision": {
            "gates": gates,
            "freeze": "accepted" if passed else "refused",
            "rule": PRE_REGISTERED_RULE,
            "geometry_unchanged": GEOMETRY_UNCHANGED_NOTE,
        },
        "next_research_step": (
            "N3: the micro-learner ablation conditions E/F/G — "
            "documented and unmet since cycle 12, and deliberately this "
            "cycle's non-archive ENGINE slice."
        ),
    }


def write_probe_edge_freeze_artifacts(
    output_dir: str | Path, report: dict
) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{ARTIFACT_ID}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser(description="Cycle 24 N2: freeze the probe's edges.")
    parser.add_argument("--output-dir", default=str(ROOT / "data" / "archives"))
    parser.add_argument("--evaluation-count", type=int, default=COMMITTED_EVALUATION_COUNT)
    parser.add_argument("--pool-count", type=int, default=COMMITTED_POOL_COUNT)
    args = parser.parse_args()

    report = build_probe_edge_freeze_report(
        evaluation_count=args.evaluation_count, pool_count=args.pool_count
    )
    metrics, decision = report["metrics"], report["decision"]
    gates = decision["gates"]
    print(f"G1 provenance   -> {gates['g1_provenance']['verdict'].upper()}")
    print(f"G2 determinism  -> {gates['g2_determinism']['verdict'].upper()}")
    print(
        f"G4 separation   -> {gates['g4_separation']['verdict'].upper()} "
        f"(max |delta| {gates['g4_separation']['max_abs_delta']:.6f})"
    )
    for name, entry in metrics["re_expressed_headlines"].items():
        print(
            f"  {name}: committed {entry['committed']} -> re-expressed "
            f"{entry['re_expressed']} (delta {entry['delta']})"
        )
    print(
        f"  floors: evaluation {metrics['evaluation_resampling_floor']['floor']}, "
        f"pool {metrics['pool_resampling_floor']['floor']}, "
        f"tightest {metrics['tightest_floor']}"
    )
    print(f"G3 invariance   -> {gates['g3_consumer_invariance']['verdict'].upper()}")
    print(f"\nFREEZE {decision['freeze'].upper()}")
    for path in write_probe_edge_freeze_artifacts(args.output_dir, report):
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
