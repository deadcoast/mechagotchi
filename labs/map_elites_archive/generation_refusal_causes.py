"""Cycle 22 L1: the refusal-cause histogram over the adopted loop.

K2 (DR 0042) adopted the constrained generation arm at its consumer and
recorded an honest number it could not explain: the arm logged 4,435
generation failures — reported there as "~22% of attempts — the
promoted path refuses invalid candidates loudly" — while WFC logged 0.
The cause was never looked at, and not because it was hard: the arm's
failure records have always carried their error strings
(``{parent_grid_id, error}``), but only ``len(failures)`` survived into
the loop's trajectory. So the rate had a count and no diagnosis.

**What this module measured** (the artifact is the authority; these are
its numbers): the count is exact, and BOTH claims attached to it were
wrong. The real denominator is 61,440 generation attempts — the loop
requests ``population × pool_factor`` per generation under the adopted
novelty-first default, three times the scored budget the ~22% figure
divided by — so the rate is **7.2%**. And the promoted path refused
**zero** invalid candidates: 100% of the refusals are the SLIP
rejecting the PARENT before a candidate exists, and 100% of those
parents came from the bootstrap population, exactly as ``_acceptable``
(which requires SLIP alignment to emit) guarantees they must.

This module is the diagnosis, and it is **pre-registered as an
INSTRUMENT, never a change**: it runs the adopted loop with the
additive refusal-collection seam on (byte-identical when off, pinned),
classifies every refusal by the promoted generator's own raise site,
and reports the histogram. Whatever it finds, any generator or
selection fix it motivates is its own record with its own gates —
nothing here touches generation behaviour.

Why the classification matters more than the count: the promoted
generator raises from five distinct sites, and they are five different
diagnoses. A refused PARENT (``parent grid cannot satisfy SLIP
constraints``) means the loop offered a breeding partner the profile
forbids — a SELECTION fact, and the attempt dies before a candidate is
ever proposed. An invalid CANDIDATE (``constrained generation produced
an invalid candidate``) means the generator itself missed — a
GENERATOR fact. Pooling them into "~22% failures" hides which of the
two is actually spending the budget.

Honesty rules this module keeps:

* an unrecognized message is classified ``unclassified`` and reported
  verbatim — a future generator change cannot quietly vanish from the
  histogram;
* a recognized family carrying an unrecognized reason keeps that
  reason's verbatim text as its own class and is listed under
  ``unnormalized_reasons`` — reasons are never merged into a
  neighbouring class to make the table look tidy;
* the refusal total is checked against the loop's own independently
  counted ``collapse_failures``, and (at the K2 parameters) against the
  committed K2 artifact's total — the instrument reproduces the
  recorded number or it is wrong.
"""

import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

LAB_DIR = Path(__file__).resolve().parent
ROOT = LAB_DIR.parents[1]
if str(LAB_DIR) not in sys.path:
    sys.path.insert(0, str(LAB_DIR))

from evaluation_loop_scale import (  # noqa: E402
    DEFAULT_LIFECYCLE_TICKS,
    DEFAULT_RNG_SEED,
    PRE_REGISTERED_BOUND_S,
    run_evaluation_loop,
)

ARTIFACT_ID = "generation_refusal_causes_stage0"
REPORT_DATE = "2026-07-26"
UNCLASSIFIED_FAMILY = "unclassified"

# The K2 run this instrument diagnoses, and its committed total.
K2_ARTIFACT = ROOT / "data" / "archives" / "generation_arm_evolution_stage0.json"
K2_PARAMETERS = {
    "population": 256,
    "target_evaluations": 20_480,
    "rng_seed": DEFAULT_RNG_SEED,
    "lifecycle_ticks": DEFAULT_LIFECYCLE_TICKS,
}

# The promoted generator's raise sites, MIRRORED AS TEXT and never
# imported across the package boundary (the house rule). Each entry is
# (family, message prefix, the separator that ends the prefix's
# preamble) — the candidate families interpolate a grid id and seed
# between the prefix and the reasons, so their separator differs.
# Source: packages/mecha_engine/src/mecha_engine/generation/generate.py
REFUSAL_FAMILIES: tuple[tuple[str, str, str], ...] = (
    (
        "parent_slip_misaligned",
        "parent grid cannot satisfy SLIP constraints",
        ": ",
    ),
    (
        "parent_invalid",
        "parent grid failed package genome validation before proposal "
        "generation",
        ": ",
    ),
    ("slip_profile_invalid", "SLIP profile is invalid", ": "),
    (
        "candidate_invalid",
        "constrained generation produced an invalid candidate",
        "): ",
    ),
    (
        "candidate_slip_misaligned",
        "constrained generation produced a SLIP-misaligned candidate",
        ": ",
    ),
)

# Reason-class normalization: a declared table, applied in order. Each
# entry strips the VARIABLE VALUE (a palette name, an organ role) so
# the same refusal groups across values, while the class text stays the
# authority's own words. Anything unmatched keeps its verbatim text as
# its class AND is reported under `unnormalized_reasons` — this table
# grows only from what a run actually produced, never from guesses.
REASON_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"^palette \S+ not allowed by SLIP$", "palette not allowed by SLIP"),
    (
        r"^required organ role missing for SLIP: .+$",
        "required organ role missing for SLIP",
    ),
    (
        r"^material not allowed by SLIP visual grammar: .+$",
        "material not allowed by SLIP visual grammar",
    ),
    (
        r"^body mass \d+ (?:below|above) SLIP (?:minimum|maximum) \d+$",
        "body mass outside SLIP bounds",
    ),
)

# Caps are NAMED, never silent (the house rule on truncation).
MAX_REPORTED_EXAMPLES = 25


def classify_refusal(message: str) -> dict:
    """Split one refusal into its family and its individual reasons.

    Returns ``{"family", "reasons", "reason_classes"}``. An unknown
    message shape is ``unclassified`` and keeps its text — never
    dropped, never guessed at.
    """
    text = (message or "").strip()
    for family, prefix, separator in REFUSAL_FAMILIES:
        if not text.startswith(prefix):
            continue
        cut = text.find(separator, len(prefix))
        if cut == -1:
            # The family is recognizable but the reasons are missing —
            # report the whole message rather than invent an empty one.
            reasons = [text]
        else:
            tail = text[cut + len(separator) :]
            reasons = [part for part in tail.split("; ") if part]
        return {
            "family": family,
            "reasons": reasons,
            "reason_classes": [_reason_class(reason) for reason in reasons],
        }
    return {
        "family": UNCLASSIFIED_FAMILY,
        "reasons": [text],
        "reason_classes": [text],
    }


def _reason_class(reason: str) -> str:
    for pattern, label in REASON_PATTERNS:
        if re.match(pattern, reason):
            return label
    return reason


def _is_normalized(reason: str) -> bool:
    return any(re.match(pattern, reason) for pattern, _ in REASON_PATTERNS)


def _k2_committed_total() -> int | None:
    if not K2_ARTIFACT.exists():
        return None
    payload = json.loads(K2_ARTIFACT.read_text(encoding="utf-8"))
    arm = payload.get("metrics", {}).get("arms", {}).get("constrained", {})
    total = arm.get("collapse_failures_total")
    return total if isinstance(total, int) else None


def build_refusal_cause_report(
    *,
    population: int = K2_PARAMETERS["population"],
    target_evaluations: int = K2_PARAMETERS["target_evaluations"],
    rng_seed: int = K2_PARAMETERS["rng_seed"],
    lifecycle_ticks: int = K2_PARAMETERS["lifecycle_ticks"],
) -> dict:
    started = time.perf_counter()
    result = run_evaluation_loop(
        population=population,
        target_evaluations=target_evaluations,
        rng_seed=rng_seed,
        lifecycle_ticks=lifecycle_ticks,
        generation="constrained",
        collect_refusals=True,
        # Pinned to the incumbent (cycle 24 N7), and this one is the
        # clearest case in the repo: THIS STUDY IS THE MEASUREMENT OF
        # THE DEFECT. Its subject is the 4,435-refusal tax. DR 0052
        # moved the loop's default to "insertion", under which that tax
        # is zero — so running this study on the new default would not
        # update the finding, it would ERASE the evidence the finding
        # is made of.
        slip_admission="none",
    )
    wall_clock_s = round(time.perf_counter() - started, 3)

    collection = result["refusal_collection"]
    records = collection["records"]
    attempts = collection["generation_attempts_total"]

    family_counts: Counter[str] = Counter()
    reason_class_counts: Counter[str] = Counter()
    family_reason_counts: dict[str, Counter[str]] = {}
    refusals_by_generation: Counter[int] = Counter()
    refused_parents: Counter[str] = Counter()
    refused_parent_origins: Counter[str] = Counter()
    refused_parent_depths: Counter[str] = Counter()
    unclassified: list[str] = []
    unnormalized: Counter[str] = Counter()
    reason_examples: dict[str, str] = {}

    for record in records:
        classified = classify_refusal(record["error"])
        family = classified["family"]
        family_counts[family] += 1
        refusals_by_generation[record["generation_index"]] += 1
        refused_parents[str(record.get("parent_grid_id"))] += 1
        refused_parent_origins[str(record.get("parent_origin"))] += 1
        depth = record.get("parent_lineage_depth")
        refused_parent_depths[str(depth)] += 1
        if family == UNCLASSIFIED_FAMILY:
            unclassified.append(record["error"])
        bucket = family_reason_counts.setdefault(family, Counter())
        for reason, reason_class in zip(
            classified["reasons"], classified["reason_classes"]
        ):
            reason_class_counts[reason_class] += 1
            bucket[reason_class] += 1
            reason_examples.setdefault(reason_class, reason)
            if family != UNCLASSIFIED_FAMILY and not _is_normalized(reason):
                unnormalized[reason] += 1

    refusals_total = len(records)
    committed_total = _k2_committed_total()
    parameters_match_k2 = {
        "population": population,
        "target_evaluations": target_evaluations,
        "rng_seed": rng_seed,
        "lifecycle_ticks": lifecycle_ticks,
    } == K2_PARAMETERS

    # The self-verification pin, stated honestly: the K2 comparison is
    # only meaningful at K2's own parameters. At any other scale the
    # field says so rather than reporting a meaningless mismatch.
    if not parameters_match_k2:
        k2_check: dict = {
            "applicable": False,
            "reason": (
                "the committed K2 total is the 20,480-evaluation run's; "
                "this report ran different parameters"
            ),
            "committed_total": committed_total,
            "measured_total": refusals_total,
        }
    else:
        k2_check = {
            "applicable": True,
            "committed_total": committed_total,
            "measured_total": refusals_total,
            "match": committed_total == refusals_total,
        }

    parent_share = (
        max(refused_parents.values()) / refusals_total if refusals_total else 0.0
    )

    metrics = {
        "generation_attempts_total": attempts,
        "refusals_total": refusals_total,
        "refusal_rate": round(refusals_total / attempts, 6) if attempts else 0.0,
        "family_histogram": dict(family_counts.most_common()),
        "family_share": {
            family: round(count / refusals_total, 6)
            for family, count in family_counts.most_common()
        }
        if refusals_total
        else {},
        "reason_class_histogram": dict(reason_class_counts.most_common()),
        "reason_classes_by_family": {
            family: dict(counts.most_common())
            for family, counts in sorted(family_reason_counts.items())
        },
        "reason_examples": {
            label: reason_examples[label]
            for label, _ in reason_class_counts.most_common(
                MAX_REPORTED_EXAMPLES
            )
        },
        "refusals_by_generation": [
            {"generation": index, "refusals": refusals_by_generation[index]}
            for index in sorted(refusals_by_generation)
        ],
        "distinct_refused_parents": len(refused_parents),
        "largest_single_parent_share": round(parent_share, 6),
        # The mechanism, measured by MEMBERSHIP rather than inferred
        # from lineage depth: `bootstrap` means the parent entered the
        # archive from the bootstrap population (built by the corpus
        # generators, which are not handed the SLIP), `loop_offspring`
        # means the loop's own `generate_candidate` produced it — and
        # that path refuses to EMIT a SLIP-misaligned candidate, so a
        # refused loop offspring would be a contradiction worth
        # chasing. Lineage depth is reported separately because it
        # answers a different question and must not be read as origin.
        "refused_parent_origin": dict(refused_parent_origins.most_common()),
        "refused_parent_lineage_depth": dict(
            refused_parent_depths.most_common()
        ),
        "most_refused_parents": dict(
            refused_parents.most_common(MAX_REPORTED_EXAMPLES)
        ),
        "unclassified_messages": unclassified[:MAX_REPORTED_EXAMPLES],
        "unclassified_total": len(unclassified),
        "unnormalized_reasons": dict(
            unnormalized.most_common(MAX_REPORTED_EXAMPLES)
        ),
        "unnormalized_total": sum(unnormalized.values()),
        "reported_example_cap": MAX_REPORTED_EXAMPLES,
        "k2_self_verification": k2_check,
        "loop_counter_agreement": sum(
            entry["collapse_failures"] for entry in result["trajectory"]
        )
        == refusals_total,
        "wall_clock_s": wall_clock_s,
        "pre_registered_bound_s": PRE_REGISTERED_BOUND_S,
        "within_bound": wall_clock_s <= PRE_REGISTERED_BOUND_S,
    }

    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0",
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 22 L1: diagnose the constrained generation arm's "
            "refusals by the promoted generator's own raise sites — K2 "
            "recorded the ~22% rate and left the cause unmeasured."
        ),
        "source_artifacts": [
            "data/archives/generation_arm_evolution_stage0.json",
            "data/archives/evaluation_loop_scale_stage0.json",
        ],
        "parameters": {
            "population": population,
            "target_evaluations": target_evaluations,
            "rng_seed": rng_seed,
            "lifecycle_ticks": lifecycle_ticks,
            "generation": "constrained",
            "selection": "novelty_first (the DR 0040 adopted default)",
        },
        "metrics": metrics,
        "closed_states": [
            "the constrained arm's refusals are classified by raise site, "
            "not pooled into one rate",
            "reason classes group across variable values while keeping the "
            "authority's own words",
            "the refusal total is cross-checked against the loop's own "
            "independent collapse-failure counter",
        ],
        "blocked_states": [
            "this instrument does not change generation behaviour: any fix "
            "it motivates is its own record with its own pre-registered "
            "gates",
            "reasons are split on '; ' — an individual authority error "
            "containing that separator would be over-split (unobserved, "
            "recorded as a known limitation)",
            "the WFC arm is not measured here: it logs zero refusals, so "
            "the histogram would be empty by construction",
        ],
        "decision": {
            "kind": "instrument",
            "rule": (
                "pre-registered (cycle 22 L1): this module OBSERVES. It "
                "reports whatever the histogram says, including a result "
                "that contradicts K2's reading of its own number. No "
                "generation change rides on this artifact."
            ),
        },
        "next_research_step": (
            "L2: the documented lineage-dominance clause "
            "(deep-research.md:205), never judged."
        ),
    }


def write_refusal_cause_artifacts(output_dir: str | Path, report: dict) -> list[Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return [path]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", default=str(ROOT / "data" / "archives")
    )
    parser.add_argument("--population", type=int, default=K2_PARAMETERS["population"])
    parser.add_argument(
        "--target-evaluations",
        type=int,
        default=K2_PARAMETERS["target_evaluations"],
    )
    parser.add_argument("--rng-seed", type=int, default=K2_PARAMETERS["rng_seed"])
    args = parser.parse_args()

    report = build_refusal_cause_report(
        population=args.population,
        target_evaluations=args.target_evaluations,
        rng_seed=args.rng_seed,
    )
    written = write_refusal_cause_artifacts(args.output_dir, report)
    metrics = report["metrics"]
    print(
        f"refusals {metrics['refusals_total']} / attempts "
        f"{metrics['generation_attempts_total']} "
        f"(rate {metrics['refusal_rate']})"
    )
    for family, count in metrics["family_histogram"].items():
        share = metrics["family_share"].get(family, 0.0)
        print(f"  {family:28} {count:6}  {share:.4f}")
    print(f"k2 self-verification: {metrics['k2_self_verification']}")
    for path in written:
        print(f"wrote {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
