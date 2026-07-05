"""Runtime integration lab: the promoted engine running as one organism.

Composes all six promoted `mecha_engine` modules through the cross-module
MVP flow (research/package_specs/mecha_engine_module_interfaces.md),
extended with the repair module's damage-event contract:

    genome.validate_grid(parent)
      -> generation.generate_candidate(...)
      -> genome.validate_grid / grid_signature / render_packet_from_grid
      -> lifecycle.run_episode (pre-damage)
      -> damage event (reference source: the cellular_automata lab's
         seeded stochastic damage, which reports `removed_cells` per the
         repair interface spec's observability contract)
      -> repair.repair_wound_sites (validity guard on, no template)
      -> lifecycle.run_episode (post-repair)
      -> archive.score_candidate / descriptor_for_candidate /
         insert_candidate -> archive_summary
      -> provenance.validate_ledger / build_ci_report over the real
         repository ledger

This is evidence for a future `runtime` package surface — which remains
decision-record-gated and is NOT created here. Labs may import the
package (the established parity direction); the package never imports
labs. Readability enters the archive as the uncalibrated proxy with its
manual-rating status visible (calibration is deferred by owner decision).
"""

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
GRID_GENOME = ROOT / "labs" / "grid_genome"
READABILITY = ROOT / "labs" / "readability_benchmark"
CELLULAR = ROOT / "labs" / "cellular_automata"
for path in [PACKAGE_SRC, GRID_GENOME, READABILITY, CELLULAR]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from ca_nca_growth_repair import apply_stochastic_damage  # noqa: E402
from corpus_builder import build_seed_grids  # noqa: E402
from readability_benchmark import score_readability  # noqa: E402
from slip import is_grid_aligned  # noqa: E402

from mecha_engine.archive import (  # noqa: E402
    archive_summary,
    build_archive,
    descriptor_for_candidate,
    insert_candidate,
    score_candidate,
)
from mecha_engine.generation import (  # noqa: E402
    generate_candidate,
    train_generation_model,
)
from mecha_engine.genome import (  # noqa: E402
    grid_signature,
    render_packet_from_grid,
    validate_grid,
)
from mecha_engine.lifecycle import run_episode  # noqa: E402
from mecha_engine.provenance import (  # noqa: E402
    build_ci_report,
    validate_ledger,
)
from mecha_engine.repair import (  # noqa: E402
    repair_wound_sites,
    train_repair_model,
)


ARTIFACT_ID = "mecha_engine_runtime_loop_stage0"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "runtime_integration"
SLIP_PROFILE_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
LEDGER_PATH = ROOT / "data" / "asset_provenance" / "ledger.json"
REPAIR_TRAINING_COUNT = 40  # the trained-repair benchmark's split


def _live_tokens(grid: dict) -> dict[tuple[int, int], str]:
    return {
        (cell["x"], cell["y"]): f"{cell['role']}/{cell.get('organ')}"
        for cell in grid["cells"]
    }


def _restoration(pre_damage: dict, repaired: dict) -> dict:
    """Runtime restoration fidelity: the loop holds the pre-damage truth.

    `position_restoration` is 1.0 exactly when the repaired live-cell set
    equals the pre-damage set (the wound-site structural guarantee);
    `token_restoration` is the fraction of those positions whose
    role/organ matches — the learned part of repair.
    """
    before = _live_tokens(pre_damage)
    after = _live_tokens(repaired)
    union = set(before) | set(after)
    position_matches = sum(
        1 for key in union if key in before and key in after
    )
    token_matches = sum(
        1 for key in union if before.get(key) == after.get(key)
    )
    return {
        "position_restoration": round(position_matches / len(union), 6),
        "token_restoration": round(token_matches / len(union), 6),
    }


def _episode_digest(episode: dict, ticks: int) -> dict:
    return {
        "survival_ticks": episode["survival_ticks"],
        "alive": episode["alive"],
        "death_cause": episode["death_cause"],
        "survival_ratio": round(episode["survival_ticks"] / ticks, 6)
        if ticks
        else 0.0,
        "need_balance": episode["need_balance"],
    }


def run_mecha_engine_runtime_loop(
    *,
    count: int = 12,
    ticks: int = 72,
    dropout_rate: float = 0.2,
    repair_epochs: int = 150,
    rng_seed: int = 20260512,
) -> dict:
    """Run `count` creatures through the full engine loop, deterministically."""
    slip_profile = json.loads(SLIP_PROFILE_PATH.read_text(encoding="utf-8"))
    seeds = build_seed_grids()
    generation_model = train_generation_model(seeds)
    repair_model = train_repair_model(
        seeds[:REPAIR_TRAINING_COUNT],
        epochs=repair_epochs,
        rng_seed=rng_seed,
    )

    # Second integration behavior surfaced by composing the modules: the
    # generation contract REJECTS parents that cannot satisfy the SLIP
    # profile (e.g. a disallowed palette), so a runtime selects parents
    # per profile. The corpus mixes three palettes; the run pool is the
    # profile-aligned subset.
    parent_pool = [
        seed for seed in seeds if is_grid_aligned(seed, slip_profile).ok
    ]
    if not parent_pool:
        raise ValueError("no seed grid satisfies the SLIP profile")

    archive = build_archive([], {})
    runs = []
    for index in range(count):
        parent = parent_pool[index % len(parent_pool)]
        run_seed = rng_seed + index
        stages: dict[str, bool] = {}

        stages["parent_valid"] = validate_grid(parent).ok

        candidate = generate_candidate(
            parent, generation_model, slip_profile, rng_seed=run_seed
        )
        candidate_validation = validate_grid(candidate)
        stages["candidate_valid"] = candidate_validation.ok
        signature = grid_signature(candidate)
        packet = render_packet_from_grid(candidate)
        json.dumps(packet)  # the packet contract: JSON-serializable
        stages["render_packet_serializable"] = True

        episode_pre = run_episode(
            candidate,
            slip_profile,
            policy="switchboard",
            ticks=ticks,
            rng_seed=run_seed,
        )
        stages["episode_pre_completed"] = episode_pre["survival_ticks"] >= 0

        damaged = apply_stochastic_damage(
            candidate,
            dropout_rate=dropout_rate,
            rng_seed=rng_seed + index * 1000 + 1,
            event_index=1,
        )
        damage_event = {
            "removed_cell_count": damaged["metadata"]["removed_cell_count"],
            "removed_cells": damaged["metadata"]["removed_cells"],
        }

        # SLIP-aware guard (the seam fix, 2026-07-05): the runtime hands
        # the active profile to repair, so a destroyed profile-required
        # organ is refilled back into an aligned, simulatable creature.
        repaired = repair_wound_sites(
            damaged, repair_model, slip_profile=slip_profile
        )
        repaired_validation = validate_grid(repaired)
        stages["repaired_valid"] = repaired_validation.ok
        restoration = _restoration(candidate, repaired)
        restoration["validity_guard_substitutions"] = repaired["metadata"][
            "validity_guard_substitutions"
        ]

        # Cross-module contract gap, found by this lab's first composed
        # run: repair guarantees genome-validator validity, but lifecycle
        # REJECTS grids that lost SLIP alignment (e.g. the only expression
        # cell destroyed and refilled as another organ). Alignment
        # retention is therefore a first-class measured stage; unaligned
        # repairs skip the post episode and the archive, honestly.
        alignment = is_grid_aligned(repaired, slip_profile)
        stages["slip_aligned_post_repair"] = alignment.ok

        episode_post_digest = None
        score_digest = None
        descriptor_list = None
        decision = "skipped_unaligned"
        stages["episode_post_completed"] = False
        stages["scored"] = False
        if alignment.ok:
            episode_post = run_episode(
                repaired,
                slip_profile,
                policy="switchboard",
                ticks=ticks,
                rng_seed=run_seed,
            )
            stages["episode_post_completed"] = episode_post["survival_ticks"] >= 0
            episode_post_digest = _episode_digest(episode_post, ticks)

            metrics = {
                "readability": score_readability(repaired),
                "slip_profile": slip_profile,
                "slip_alignment": {"ok": True},
                "lifecycle": episode_post,
                "rng_seed": run_seed,
            }
            archive_candidate = {"grid": repaired}
            score = score_candidate(archive_candidate, metrics)
            descriptor = descriptor_for_candidate(archive_candidate, metrics)
            stages["scored"] = isinstance(score.get("fitness"), float)
            score_digest = {
                "fitness": score["fitness"],
                "components": score["components"],
                "readability": {
                    "proxy_readability_score": score["readability"][
                        "proxy_readability_score"
                    ],
                    "manual_rating_status": score["readability"][
                        "manual_rating_status"
                    ],
                },
            }
            descriptor_list = list(descriptor)

            before_log = len(archive["insertion_log"])
            archive = insert_candidate(
                archive, archive_candidate, score, descriptor
            )
            event = (
                archive["insertion_log"][before_log]["event"]
                if len(archive["insertion_log"]) > before_log
                else "unlogged"
            )
            if event.startswith("inserted"):
                decision = "inserted"
            elif event.startswith("replaced"):
                decision = "replaced"
            elif event.startswith("blocked"):
                decision = "blocked_invalid"
            else:
                decision = "kept_incumbent"

        runs.append(
            {
                "parent_grid_id": parent["grid_id"],
                "candidate_grid_id": candidate["grid_id"],
                "candidate_signature": signature,
                "stages": stages,
                "episode_pre": _episode_digest(episode_pre, ticks),
                "damage": damage_event,
                "repair": restoration,
                "episode_post": episode_post_digest,
                "score": score_digest,
                "descriptor": descriptor_list,
                "archive_decision": decision,
            }
        )

    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    ledger_result = validate_ledger(ledger, ROOT)
    ci_report = build_ci_report(ledger, ROOT)

    summary = _loop_summary(runs, archive, ticks)
    report = {
        "lab_id": ARTIFACT_ID,
        "date": "2026-07-05",
        "rng_seed": rng_seed,
        "count": count,
        "parent_pool_size": len(parent_pool),
        "seed_corpus_size": len(seeds),
        "ticks": ticks,
        "dropout_rate": dropout_rate,
        "repair_epochs": repair_epochs,
        "repair_training_count": REPAIR_TRAINING_COUNT,
        "purpose": (
            "Compose all six promoted mecha_engine modules through the "
            "cross-module MVP flow plus the repair damage-event contract, "
            "as executable evidence for a future runtime surface."
        ),
        "source_artifacts": [
            "research/package_specs/mecha_engine_module_interfaces.md",
            "research/package_specs/mecha_engine_repair_interface_spec.md",
            "research/package_specs/mecha_engine_contract_traceability_matrix.md",
            "data/slips/valid/slip_lcd_seed.json",
            "data/asset_provenance/ledger.json",
        ],
        "runs": runs,
        "summary": summary,
        "provenance": {
            "ledger_ok": ledger_result["ok"],
            "ledger_asset_count": ledger_result["summary"]["asset_count"],
            "ci_ok": bool(ci_report.get("ok")),
        },
        "closed_states": [
            "six_module_loop_composed_generation_to_provenance",
            "repair_damage_event_contract_exercised_in_full_loop",
        ],
        "blocked_states": [
            "runtime_package_target_absent_decision_record_gated",
            "readability_proxy_uncalibrated_manual_calibration_deferred",
        ],
        "decision": _loop_decision(summary, ledger_result, ci_report),
        "next_research_step": (
            "Extend the loop to multi-generation evolution (offspring of "
            "archive elites) and repeated damage/repair cycles before any "
            "runtime package design is proposed (decision record required)."
        ),
    }
    return report


def _loop_summary(runs: list[dict], archive: dict, ticks: int) -> dict:
    count = len(runs)
    summary = archive_summary(archive)
    archived = [run for run in runs if run["score"] is not None]
    return {
        "run_count": count,
        "candidate_valid_rate": round(
            sum(1 for run in runs if run["stages"]["candidate_valid"]) / count, 6
        ),
        "repaired_valid_rate": round(
            sum(1 for run in runs if run["stages"]["repaired_valid"]) / count, 6
        ),
        "slip_alignment_retention_rate": round(
            sum(
                1 for run in runs if run["stages"]["slip_aligned_post_repair"]
            )
            / count,
            6,
        ),
        "mean_removed_cells": round(
            sum(run["damage"]["removed_cell_count"] for run in runs) / count, 6
        ),
        "mean_position_restoration": round(
            sum(run["repair"]["position_restoration"] for run in runs) / count, 6
        ),
        "mean_token_restoration": round(
            sum(run["repair"]["token_restoration"] for run in runs) / count, 6
        ),
        "guard_substitution_total": sum(
            run["repair"]["validity_guard_substitutions"] for run in runs
        ),
        "mean_survival_ratio_pre": round(
            sum(run["episode_pre"]["survival_ratio"] for run in runs) / count, 6
        ),
        "mean_survival_ratio_post": round(
            sum(
                run["episode_post"]["survival_ratio"]
                for run in archived
            )
            / len(archived),
            6,
        )
        if archived
        else 0.0,
        "mean_fitness": round(
            sum(run["score"]["fitness"] for run in archived) / len(archived), 6
        )
        if archived
        else 0.0,
        "archived_run_count": len(archived),
        "archive": {
            "filled_niches": summary["occupied_niches"],
            "coverage": summary["coverage"],
            "qd_score": summary["qd_score"],
            "insertions": sum(
                1 for run in runs if run["archive_decision"] == "inserted"
            ),
        },
    }


def _loop_decision(summary: dict, ledger_result: dict, ci_report: dict) -> dict:
    all_stages_green = (
        summary["candidate_valid_rate"] == 1.0
        and summary["repaired_valid_rate"] == 1.0
        and summary["slip_alignment_retention_rate"] == 1.0
        and summary["mean_position_restoration"] == 1.0
        and summary["archive"]["filled_niches"] >= 1
        and ledger_result["ok"]
        and bool(ci_report.get("ok"))
    )
    if all_stages_green:
        status = "runtime_loop_composed"
        reason = (
            "All six promoted modules compose into one deterministic loop: "
            "every generated creature validates, survives an episode, takes "
            "a reported damage event, is repaired to its exact live-cell "
            "silhouette without a template, survives post-repair, scores "
            "into the archive, and the provenance gate passes over the real "
            "ledger. Evidence exists for a runtime surface design; creating "
            "that target stays decision-record-gated."
        )
    else:
        status = "runtime_loop_gaps_measured"
        reason = (
            "At least one stage fell short of its module contract inside "
            "the composed loop; the per-run stage flags record exactly "
            "where. The gap list, not this consolidated flag, is the "
            "actionable surface."
        )
    return {
        "status": status,
        "adoption": "lab_only_runtime_evidence",
        "reason": reason,
    }


def write_runtime_loop_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(_readme_text(report), encoding="utf-8")


def _readme_text(report: dict) -> str:
    summary = report["summary"]
    return (
        "# Mecha Engine Runtime Loop Stage 0\n\n"
        "All six promoted `mecha_engine` modules composed through the "
        "cross-module MVP flow plus the repair damage-event contract.\n\n"
        "Key results:\n\n"
        f"- Runs: {summary['run_count']} creatures, {report['ticks']} ticks/episode\n"
        f"- Candidate validity: {summary['candidate_valid_rate']}\n"
        f"- Repaired validity: {summary['repaired_valid_rate']}\n"
        f"- SLIP alignment retention after repair: "
        f"{summary['slip_alignment_retention_rate']} "
        f"({summary['archived_run_count']}/{summary['run_count']} runs archived)\n"
        f"- Position restoration: {summary['mean_position_restoration']} "
        f"(token restoration {summary['mean_token_restoration']})\n"
        f"- Survival ratio pre/post repair: {summary['mean_survival_ratio_pre']} "
        f"/ {summary['mean_survival_ratio_post']}\n"
        f"- Archive: {summary['archive']['filled_niches']} niches, "
        f"QD {summary['archive']['qd_score']}\n"
        f"- Provenance: ledger_ok={report['provenance']['ledger_ok']}, "
        f"ci_ok={report['provenance']['ci_ok']}\n"
        f"- Decision: {report['decision']['status']}\n\n"
        "Readability enters the archive as the uncalibrated proxy with its "
        "manual-rating status visible (calibration deferred by owner "
        "decision). The runtime package target remains "
        "decision-record-gated.\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the mecha_engine runtime integration loop."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--ticks", type=int, default=72)
    parser.add_argument("--dropout-rate", type=float, default=0.2)
    parser.add_argument("--rng-seed", type=int, default=20260512)
    args = parser.parse_args()
    report = run_mecha_engine_runtime_loop(
        count=args.count,
        ticks=args.ticks,
        dropout_rate=args.dropout_rate,
        rng_seed=args.rng_seed,
    )
    write_runtime_loop_artifacts(args.output_dir, report)
    print(json.dumps(report["summary"], indent=2))
    print(json.dumps(report["decision"], indent=2))


if __name__ == "__main__":
    main()
