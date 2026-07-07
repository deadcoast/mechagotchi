"""Session runner — one full Keeper session over the promoted engine (G2).

Executable research prototype for decision record 0021 build gate G2:
one campaign of eras runs end to end over the PROMOTED surfaces only
(`mecha_engine.runtime.evolve` plus the package model trainers) —

- **era-chaining** (the DR 0016/0021 persistence spine): every era after
  the first submits the previous era's archive elites, in niche-key
  order, as `founder_grids`, so the bloodline is re-admitted through the
  engine's own gates each era (admission or verbatim rejection, both
  recorded);
- **weather selection** (DR 0018/0020): each era names a forecast —
  ``calm`` (no pressure source, the byte-identical default),
  ``stable_soup`` or ``storm`` (synthetic CuBFF snapshot sets with the
  measured low/high mutation-pressure signatures) — and the engine's own
  `cubff_pressure` block is the weather record, snapshot provenance
  included;
- **unlock evaluation** (DR 0021's progression table): unlock FACTS are
  computed from era-record metrics against threshold DATA
  (`UNLOCK_THRESHOLDS` — tuning, not architecture), each fact citing the
  metric path and value that earned it, falsifiable by construction;
- **extinction and succession**: an era that ends early (the engine's
  measured empty-archive break) or archives no elites marks the campaign
  extinct, and the Keeper's successor bloodline carries ONLY the unlock
  facts (resolved through the predecessor pointer, never copied — DR
  0022's succession rule).

Persistence is the DR 0021/0022 JSON interim: `build_campaign_ledger`
emits the DR 0022 schema-v1 vocabulary (campaigns / eras / elites /
founders / unlocks / replays) with every engine artifact stored verbatim,
so the future `storage` module's `ingest_session_artifacts` migration is
lossless by design.

Measured boundary recorded during G2 development (probe, 2026-07-07): at
extreme synthesizer dropout (>= 0.9 with 4+ cycles) `live_cycle` can
produce a repaired grid that is SLIP-ALIGNED yet LIFECYCLE-INVALID
("required body core is disconnected"), which raises inside the episode
run — alignment does not imply lifecycle validity at extreme damage.
Session configurations stay below that regime (weather multiplies base
dropout by at most 1.6); the boundary is ledgered as a blocked state, not
silently avoided.

Deterministic end to end: seeds, dates, and ids are fixed or injected —
no wall clock, no os randomness.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
READABILITY = ROOT / "labs" / "readability_benchmark"
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
for path in [GRID_GENOME, READABILITY, PACKAGE_SRC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from corpus_builder import build_seed_grids  # noqa: E402
from learned_readability import (  # noqa: E402
    build_learned_readability_report,
    learned_readability_score,
)
from readability_benchmark import score_readability  # noqa: E402

from mecha_engine.generation import train_generation_model  # noqa: E402
from mecha_engine.repair import train_repair_model  # noqa: E402
from mecha_engine.runtime import evolve  # noqa: E402

ARTIFACT_ID = "game_loop_session_runner_stage0"
REPORT_DATE = "2026-07-07"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "game_loop"
SLIP_PROFILE_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
REPAIR_TRAINING_COUNT = 40  # the runtime lab's fixed training split

# Era seed spacing must exceed evolve's per-creature arithmetic
# (generation_index * 100000 + index) for every session configuration.
ERA_SEED_STRIDE = 1_000_000
# A successor bloodline is a genuinely fresh start: its era seeds live in
# a disjoint band from every predecessor era.
SUCCESSOR_SEED_OFFSET = 50_000_000

WEATHER_NAMES = ("calm", "stable_soup", "storm")

# DR 0021: "threshold VALUES are tuning, not architecture: they live in
# the session lab as data, proven falsifiable by tests." Tier values are
# calibrated to Stage-0 measured magnitudes (R2's evolution artifact:
# filled_niches 13, qd_score 12.03, max_lineage_generation 2 at
# 4 generations x 6 population; storm multipliers cluster near 1.17x).
UNLOCK_THRESHOLDS: dict[str, dict] = {
    "niche_mastery": {
        "metric_path": "report.summary.archive.filled_niches",
        "tiers": [4, 8, 13],
    },
    "bloodline_depth": {
        "metric_path": "report.summary.max_lineage_generation",
        "tiers": [2, 3, 4],
    },
    "quality_diversity": {
        "metric_path": "report.summary.archive.qd_score",
        "tiers": [3.0, 6.0, 12.0],
    },
    "storm_record": {
        "metric_path": "derived.max_dropout_multiplier_survived",
        "tiers": [1.1, 1.4],
    },
    "legibility": {
        "metric_path": "derived.elite_mean_learned_readability",
        "tiers": [0.25, 0.35],
    },
}


def _stable_snapshot(index: int) -> dict:
    """A calmly replicating soup: low instability, low mutation pressure."""
    tape = [7, 7, 7, 8, 7, 7, 7, 8] * 8
    return {
        "snapshot_id": f"weather_stable_{index:03d}",
        "epoch": 100 + index,
        "language": "bff_noheads",
        "program_size": 64,
        "tape": tape,
        "replication_scores": [64, 64, 64, 48, 64, 64, 48, 64],
        "brotli_size": 12,
        "lineage_events": [{"parent": 0, "child": 0}],
    }


def _chaotic_snapshot(index: int) -> dict:
    """A turbulent soup: high churn, high mutation pressure."""
    tape = [(index * 13 + position * 31) % 64 for position in range(64)]
    return {
        "snapshot_id": f"weather_storm_{index:03d}",
        "epoch": 100 + index,
        "language": "bff_noheads",
        "program_size": 64,
        "tape": tape,
        "replication_scores": [0, 4, 8, 0, 4, 8, 0, 4],
        "brotli_size": 57,
        "lineage_events": [
            {"parent": p % 8, "child": (p + 1) % 8} for p in range(8)
        ],
    }


def build_weather_source(name: str) -> list[dict] | None:
    """Forecast name -> CuBFF pressure source for the promoted evolve.

    ``calm`` returns ``None`` — the byte-identical no-source default.
    Synthetic snapshots stand in until the real-export ingest gate clears
    (`awaiting_real_cubff_snapshots`); real snapshots drop into the same
    seam with no session-runner change (DR 0021's weather design).
    """
    if name == "calm":
        return None
    if name == "stable_soup":
        return [_stable_snapshot(i) for i in range(6)]
    if name == "storm":
        return [_chaotic_snapshot(i) for i in range(6)]
    raise ValueError(f"unknown weather forecast: {name}")


def train_session_models(
    seed_grids: list[dict], *, repair_epochs: int, rng_seed: int
) -> tuple[dict, dict]:
    """The promoted trainers, composed once per session (they are
    deterministic in their inputs, so sharing them across eras is
    behavior-identical to retraining)."""
    generation_model = train_generation_model(seed_grids)
    repair_model = train_repair_model(
        seed_grids[:REPAIR_TRAINING_COUNT],
        epochs=repair_epochs,
        rng_seed=rng_seed,
    )
    return generation_model, repair_model


def train_legibility_model(rng_seed: int = 20260706) -> dict:
    """The R3 learned readability model (DR 0019) — the PRIMARY
    legibility signal; the manual rating system remains the fallback."""
    model = build_learned_readability_report(rng_seed=rng_seed)["model"]
    return {
        "weights": model["weights"],
        "reference_features": model["reference_features"],
    }


def _resolve_metric(era_record: dict, path: str):
    """Resolve an unlock fact's dotted metric path inside its era record."""
    value = era_record
    for key in path.split("."):
        if not isinstance(value, dict) or key not in value:
            raise KeyError(
                f"metric path {path!r} does not resolve in era record"
            )
        value = value[key]
    return value


def evaluate_unlocks(
    era_record: dict, already_unlocked: list[dict]
) -> list[dict]:
    """Compute the unlock FACTS an era earns (DR 0021's table).

    Pure over its inputs: a threshold met in the era record must unlock;
    unmet must not; an (axis, tier) already earned is never re-earned.
    Facts cite the metric path, the value, and the threshold verbatim
    (DR 0022's unlocks table shape).
    """
    earned = {(fact["axis"], fact["tier"]) for fact in already_unlocked}
    facts: list[dict] = []
    for axis, spec in UNLOCK_THRESHOLDS.items():
        try:
            value = _resolve_metric(era_record, spec["metric_path"])
        except KeyError:
            continue  # e.g. no storm record in a calm era
        if value is None:
            continue
        for tier_index, threshold in enumerate(spec["tiers"], start=1):
            if (axis, tier_index) in earned:
                continue
            if value >= threshold:
                facts.append(
                    {
                        "axis": axis,
                        "tier": tier_index,
                        "earned_era_index": era_record["era_index"],
                        "metric_path": spec["metric_path"],
                        "metric_value": value,
                        "threshold": threshold,
                    }
                )
    return facts


def _era_elites(archive: dict) -> list[dict]:
    """The archive's elites in niche-key order — the same deterministic
    ordering evolve itself uses for elite parents (DR 0022's
    `load_founder_pool` contract, JSON interim)."""
    return [
        {"niche_key": niche, **archive["elites"][niche]}
        for niche in sorted(archive["elites"])
    ]


def _total_removed_cells(report: dict) -> int:
    return sum(
        cycle["removed_cell_count"]
        for generation in report["generations"]
        for creature in generation["creatures"]
        for cycle in creature["cycles"]
    )


def run_era(
    *,
    era_index: int,
    weather: str,
    seed_grids: list[dict],
    slip_profile: dict,
    generation_model: dict,
    repair_model: dict,
    legibility_model: dict,
    founder_grids: list[dict] | None,
    rng_seed: int,
    generations: int,
    population: int,
    damage_cycles: int,
    ticks: int,
    dropout_rate: float,
) -> dict:
    """One era = one promoted `runtime.evolve` run (DR 0021's core loop).

    The returned era record stores the engine's report VERBATIM (the
    blob-authoritative rule, DR 0022) plus the derived session metrics —
    each pinned to engine truth: extinction is the report's own early
    end, the storm record is the engine's recorded multipliers, and
    legibility is the R3 learned model scored over the era's actual
    elites."""
    archive, report = evolve(
        seed_grids,
        slip_profile,
        generation_model,
        repair_model,
        readability_scorer=score_readability,
        generations=generations,
        population=population,
        damage_cycles=damage_cycles,
        ticks=ticks,
        dropout_rate=dropout_rate,
        rng_seed=rng_seed,
        founder_grids=founder_grids,
        cubff_pressure_source=build_weather_source(weather),
    )
    elites = _era_elites(archive)
    went_extinct = (
        len(report["generations"]) < report["generations_requested"]
        or not elites
    )
    multipliers = [
        entry["dropout_multiplier"]
        for entry in report.get("cubff_pressure", {}).get("by_generation", [])
    ]
    max_multiplier_survived = (
        max(multipliers) if multipliers and not went_extinct else None
    )
    legibility = (
        round(
            sum(
                learned_readability_score(elite["grid"], legibility_model)
                for elite in elites
            )
            / len(elites),
            6,
        )
        if elites
        else None
    )
    return {
        "era_index": era_index,
        "rng_seed": rng_seed,
        "weather": {
            "forecast": weather,
            "snapshot_ids": [
                entry["snapshot_id"]
                for entry in report.get("cubff_pressure", {}).get(
                    "by_generation", []
                )
            ],
        },
        "founders_submitted": (
            [grid["grid_id"] for grid in founder_grids]
            if founder_grids is not None
            else []
        ),
        "report": report,
        "elites": elites,
        "derived": {
            "went_extinct": went_extinct,
            "generations_ran": len(report["generations"]),
            "total_removed_cells": _total_removed_cells(report),
            "max_dropout_multiplier_survived": max_multiplier_survived,
            "elite_mean_learned_readability": legibility,
        },
    }


def run_campaign(
    *,
    campaign_id: str,
    keeper_label: str = "keeper_stage0",
    created_date: str = REPORT_DATE,
    predecessor_campaign_id: str | None = None,
    weather_schedule: tuple[str, ...] = ("calm", "stable_soup", "storm"),
    base_seed: int = 20260707,
    seed_grids: list[dict] | None = None,
    slip_profile: dict | None = None,
    generation_model: dict | None = None,
    repair_model: dict | None = None,
    legibility_model: dict | None = None,
    generations: int = 3,
    population: int = 4,
    damage_cycles: int = 2,
    ticks: int = 16,
    dropout_rate: float = 0.2,
    repair_epochs: int = 20,
) -> dict:
    """One campaign: a chain of eras where each era's founder pool is the
    previous era's elites (DR 0021's persistence spine). Extinction ends
    the chain and marks the campaign extinct; unlock facts accumulate
    per era."""
    if seed_grids is None:
        seed_grids = build_seed_grids()
    if slip_profile is None:
        slip_profile = json.loads(
            SLIP_PROFILE_PATH.read_text(encoding="utf-8")
        )
    if generation_model is None or repair_model is None:
        generation_model, repair_model = train_session_models(
            seed_grids, repair_epochs=repair_epochs, rng_seed=base_seed
        )
    if legibility_model is None:
        legibility_model = train_legibility_model()

    campaign = {
        "campaign_id": campaign_id,
        "keeper_label": keeper_label,
        "created_date": created_date,
        "predecessor_campaign_id": predecessor_campaign_id,
        "status": "active",
        "slip_profile": slip_profile,
        "base_seed": base_seed,
        "eras": [],
        "unlocks": [],
    }
    for weather in weather_schedule:
        if campaign["status"] != "active":
            break
        advance_campaign(
            campaign,
            weather,
            seed_grids=seed_grids,
            generation_model=generation_model,
            repair_model=repair_model,
            legibility_model=legibility_model,
            generations=generations,
            population=population,
            damage_cycles=damage_cycles,
            ticks=ticks,
            dropout_rate=dropout_rate,
        )
    return campaign


def advance_campaign(
    campaign: dict,
    weather: str,
    *,
    seed_grids: list[dict],
    generation_model: dict,
    repair_model: dict,
    legibility_model: dict,
    generations: int,
    population: int,
    damage_cycles: int,
    ticks: int,
    dropout_rate: float,
) -> dict:
    """Advance a living campaign by exactly one era (G4's play surface).

    Mutates ``campaign`` in place: appends the era record, accumulates
    the unlock facts it earns, and marks the campaign extinct when the
    engine ends the bloodline. The next era's founder pool is always the
    previous era's elites — the DR 0021 spine — so incremental play and
    ``run_campaign``'s batch play are the same code path."""
    if campaign["status"] != "active":
        raise ValueError(
            f"campaign {campaign['campaign_id']!r} is {campaign['status']} — "
            "an ended bloodline cannot run another era (plan_succession "
            "starts the successor)"
        )
    era_index = len(campaign["eras"])
    founder_grids = (
        [elite["grid"] for elite in campaign["eras"][-1]["elites"]]
        if campaign["eras"]
        else None
    )
    era_record = run_era(
        era_index=era_index,
        weather=weather,
        seed_grids=seed_grids,
        slip_profile=campaign["slip_profile"],
        generation_model=generation_model,
        repair_model=repair_model,
        legibility_model=legibility_model,
        founder_grids=founder_grids,
        rng_seed=campaign["base_seed"] + era_index * ERA_SEED_STRIDE,
        generations=generations,
        population=population,
        damage_cycles=damage_cycles,
        ticks=ticks,
        dropout_rate=dropout_rate,
    )
    campaign["eras"].append(era_record)
    campaign["unlocks"].extend(
        evaluate_unlocks(era_record, campaign["unlocks"])
    )
    if era_record["derived"]["went_extinct"]:
        campaign["status"] = "extinct"
    return era_record


def resolve_unlock_state(campaigns: list[dict], campaign_id: str) -> list[dict]:
    """The Keeper's unlock state: this campaign's facts plus every
    predecessor's, resolved through the pointer chain — rows are never
    copied, so each fact keeps citing the era report that earned it
    (DR 0022's succession rule)."""
    by_id = {campaign["campaign_id"]: campaign for campaign in campaigns}
    facts: list[dict] = []
    seen: set[str] = set()
    current: str | None = campaign_id
    while current is not None and current not in seen:
        seen.add(current)
        campaign = by_id[current]
        facts.extend(campaign["unlocks"])
        current = campaign["predecessor_campaign_id"]
    return facts


def plan_succession(campaign: dict) -> dict | None:
    """Roguelite stakes (DR 0021): an extinct campaign's successor starts
    a fresh bloodline from seeds, carrying ONLY the Keeper's unlocks
    (via the predecessor pointer). Returns the successor's campaign
    parameters, or None while the bloodline lives."""
    if campaign["status"] != "extinct":
        return None
    return {
        "campaign_id": f"{campaign['campaign_id']}_successor",
        "keeper_label": campaign["keeper_label"],
        "created_date": campaign["created_date"],
        "predecessor_campaign_id": campaign["campaign_id"],
        "base_seed": campaign["base_seed"] + SUCCESSOR_SEED_OFFSET,
    }


def run_keeper_session(
    *,
    campaign_id: str = "campaign_stage0",
    max_successions: int = 1,
    **campaign_kw,
) -> dict:
    """One full Keeper session: run the campaign; if the bloodline goes
    extinct, run the successor bloodline (carrying only unlocks)."""
    campaigns = [run_campaign(campaign_id=campaign_id, **campaign_kw)]
    for _ in range(max_successions):
        succession = plan_succession(campaigns[-1])
        if succession is None:
            break
        campaigns.append(
            run_campaign(
                **succession,
                **{
                    key: value
                    for key, value in campaign_kw.items()
                    if key not in ("base_seed", "keeper_label", "created_date")
                },
            )
        )
    active = campaigns[-1]["campaign_id"]
    return {
        "campaigns": campaigns,
        "active_campaign_id": active,
        "unlock_state": resolve_unlock_state(campaigns, active),
    }


def build_campaign_ledger(session: dict) -> dict:
    """The DR 0022 schema-v1 vocabulary as the JSON interim: one row set
    per table, engine artifacts verbatim, derived columns alongside their
    authoritative blobs (the future `ingest_session_artifacts` migration
    consumes exactly this shape)."""
    campaigns = []
    eras = []
    elites = []
    founders = []
    unlocks = []
    for campaign in session["campaigns"]:
        campaigns.append(
            {
                "campaign_id": campaign["campaign_id"],
                "keeper_label": campaign["keeper_label"],
                "created_date": campaign["created_date"],
                "predecessor_campaign_id": campaign[
                    "predecessor_campaign_id"
                ],
                "status": campaign["status"],
            }
        )
        for era in campaign["eras"]:
            report = era["report"]
            eras.append(
                {
                    "campaign_id": campaign["campaign_id"],
                    "era_index": era["era_index"],
                    "rng_seed": era["rng_seed"],
                    "slip_profile": campaign["slip_profile"],
                    "weather": era["weather"],
                    "report": report,
                    # Derived query columns (DR 0022): each pinned equal
                    # to its blob field by the contract tests.
                    "decision_status": report["decision"]["status"],
                    "filled_niches": report["summary"]["archive"][
                        "filled_niches"
                    ],
                    "coverage": report["summary"]["archive"]["coverage"],
                    "qd_score": report["summary"]["archive"]["qd_score"],
                    "max_lineage_generation": report["summary"][
                        "max_lineage_generation"
                    ],
                    "went_extinct": era["derived"]["went_extinct"],
                }
            )
            for elite in era["elites"]:
                elites.append(
                    {
                        "campaign_id": campaign["campaign_id"],
                        "era_index": era["era_index"],
                        "niche_key": elite["niche_key"],
                        "grid_id": elite["grid_id"],
                        "fitness": elite["fitness"],
                        "elite": {
                            key: value
                            for key, value in elite.items()
                            if key != "niche_key"
                        },
                    }
                )
            founder_block = report.get("founders")
            if founder_block is not None:
                for grid_id in founder_block["admitted_ids"]:
                    founders.append(
                        {
                            "campaign_id": campaign["campaign_id"],
                            "era_index": era["era_index"],
                            "grid_id": grid_id,
                            "source": "era_elite",
                            "admitted": True,
                            "rejection_errors": None,
                        }
                    )
                for rejection in founder_block["rejected"]:
                    founders.append(
                        {
                            "campaign_id": campaign["campaign_id"],
                            "era_index": era["era_index"],
                            "grid_id": rejection["grid_id"],
                            "source": "era_elite",
                            "admitted": False,
                            "rejection_errors": rejection["errors"],
                        }
                    )
        for fact in campaign["unlocks"]:
            unlocks.append(
                {"campaign_id": campaign["campaign_id"], **fact}
            )
    return {
        "ledger_id": "game_loop_campaign_ledger",
        "schema": "dr0022_v1_json_interim",
        "campaigns": campaigns,
        "eras": eras,
        "elites": elites,
        "founders": founders,
        "unlocks": unlocks,
        "replays": [],  # R5's table; the recorder is its own task
    }


def _era_digest(era: dict) -> dict:
    report = era["report"]
    return {
        "era_index": era["era_index"],
        "forecast": era["weather"]["forecast"],
        "snapshot_ids": era["weather"]["snapshot_ids"],
        "generations_ran": era["derived"]["generations_ran"],
        "went_extinct": era["derived"]["went_extinct"],
        "total_removed_cells": era["derived"]["total_removed_cells"],
        "max_dropout_multiplier_survived": era["derived"][
            "max_dropout_multiplier_survived"
        ],
        "elite_mean_learned_readability": era["derived"][
            "elite_mean_learned_readability"
        ],
        "founders_submitted": len(era["founders_submitted"]),
        "founders_admitted": len(
            report.get("founders", {}).get("admitted_ids", [])
        ),
        "founders_rejected": len(
            report.get("founders", {}).get("rejected", [])
        ),
        "parent_source_generation_0": report["generations"][0][
            "parent_source"
        ],
        "filled_niches": report["summary"]["archive"]["filled_niches"],
        "qd_score": report["summary"]["archive"]["qd_score"],
        "max_lineage_generation": report["summary"][
            "max_lineage_generation"
        ],
        "decision_status": report["decision"]["status"],
    }


def build_session_report(session: dict) -> dict:
    """The lab's stage-0 report over one full Keeper session."""
    primary = session["campaigns"][0]
    era_digests = [
        _era_digest(era)
        for campaign in session["campaigns"]
        for era in campaign["eras"]
    ]
    chained = [
        digest
        for digest in era_digests
        if digest["parent_source_generation_0"] == "founders_plus_seed_pool"
    ]
    removed_by_forecast: dict[str, int] = {}
    for digest in era_digests:
        removed_by_forecast[digest["forecast"]] = (
            removed_by_forecast.get(digest["forecast"], 0)
            + digest["total_removed_cells"]
        )
    closed_states = [
        "session_loop_runs_over_promoted_surfaces_only",
        "era_chaining_admits_prior_elites_through_engine_gates",
        "weather_selection_reaches_the_engine_with_snapshot_provenance",
        "unlock_facts_cite_resolvable_metric_paths",
        "succession_carries_only_unlock_facts_via_predecessor_pointer",
        "ledger_matches_dr0022_schema_v1_vocabulary",
    ]
    blocked_states = [
        # Real CuBFF weather still waits on the ingest gate (DR 0020).
        "awaiting_real_cubff_snapshots",
        # Extinction did not occur live at Stage-0 scale: the repair
        # guard held SLIP alignment up to 0.95 probe dropout, and beyond
        # ~0.9 with 4+ cycles lies the measured aligned-but-invalid
        # boundary (live_cycle episode raises "required body core is
        # disconnected"). Extinction detection and succession are proven
        # falsifiable on fixture era records instead.
        "extinction_not_observed_at_stage0_scale",
        "aligned_but_lifecycle_invalid_boundary_at_extreme_dropout",
        # DR 0022: the SQLite ledger waits on the storage module's own
        # lab and promotion; this lab persists the JSON interim.
        "sqlite_ledger_pending_storage_module_promotion",
    ]
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0_complete",
        "date": REPORT_DATE,
        "purpose": (
            "Run one full Keeper session (DR 0021, gate G2) over the "
            "promoted engine surfaces: era-chaining via founder_grids, "
            "weather selection via cubff_pressure_source, unlock facts "
            "from era-record metrics, extinction detection with "
            "succession, and the DR 0022 JSON-interim campaign ledger."
        ),
        "source_artifacts": [
            "research/decision_records/0021-game-loop.md",
            "research/decision_records/0022-storage-module.md",
            "packages/mecha_engine/src/mecha_engine/runtime/evolve.py",
            "data/slips/valid/slip_lcd_seed.json",
        ],
        "session_parameters": {
            "campaign_id": primary["campaign_id"],
            "base_seed": primary["base_seed"],
            "weather_schedule": [
                era["weather"]["forecast"] for era in primary["eras"]
            ],
        },
        "metrics": {
            "campaign_count": len(session["campaigns"]),
            "era_count": len(era_digests),
            "eras": era_digests,
            "chained_era_count": len(chained),
            "founder_admission_all_or_nothing": all(
                digest["founders_rejected"] == 0 for digest in chained
            ),
            "total_removed_cells_by_forecast": removed_by_forecast,
            "unlock_facts": session["unlock_state"],
            "unlock_fact_count": len(session["unlock_state"]),
            "final_status_by_campaign": {
                campaign["campaign_id"]: campaign["status"]
                for campaign in session["campaigns"]
            },
        },
        "unlock_thresholds": UNLOCK_THRESHOLDS,
        "closed_states": closed_states,
        "blocked_states": blocked_states,
        "decision": {
            "status": "session_loop_composed",
            "adoption": "lab_only_game_loop_evidence",
            "reason": (
                "One full Keeper session runs deterministically over the "
                "promoted engine: every post-founder era re-admits the "
                "previous era's elites through the engine's own gates, "
                "the chosen forecast measurably scales that era's damage "
                "with snapshot provenance recorded by the engine itself, "
                "and every unlock fact cites a metric path that resolves "
                "in its era record. Extinction and succession are "
                "contract-detected and fixture-proven; live extinction "
                "and real CuBFF weather remain honestly blocked."
            ),
        },
        "next_research_step": (
            "G4 (the Keeper's surface: session UI + mechas session "
            "commands) and R5 (the replay recorder this loop's Review "
            "step consumes); the storage lab (campaign_store, DR 0022) "
            "replaces the JSON interim when its gates pass."
        ),
    }


def write_session_artifacts(
    output_dir: str | Path, report: dict, session: dict
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "session_runner_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "campaign_ledger.json").write_text(
        json.dumps(build_campaign_ledger(session), indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "README.md").write_text(
        "# Game loop artifacts (Stage 0)\n\n"
        "G2 (decision record 0021): one full Keeper session over the\n"
        "promoted engine surfaces. `session_runner_stage0.json` is the\n"
        "session lab report; `campaign_ledger.json` is the DR 0022\n"
        "schema-v1 JSON-interim campaign ledger (campaigns/eras/elites/\n"
        "founders/unlocks/replays with engine reports stored verbatim),\n"
        "the future `storage` module's lossless migration source.\n\n"
        "R5 (decision record 0023): `replay_recorder_stage0.json` is the\n"
        "replay recorder lab report; `replay_sample.json` is one recorded\n"
        "life in the `mechagotchi_replay_v1` format — birth/wound/repair\n"
        "frames plus every episode tick, all engine truth verbatim — the\n"
        "workshop preview scrubber's artifact.\n\n"
        "Regenerate:\n\n"
        "- `python -B labs/game_loop/session_runner.py`\n"
        "- `python -B labs/game_loop/replay_recorder.py`\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------- G4:
# the Keeper's persistent session (DR 0021 gate G4). The state file is
# the JSON interim (DR 0022); every save also refreshes the derived
# schema-v1 campaign ledger. Backup-before-overwrite like the workshop.

SESSION_FORMAT = "keeper_session_v1"
# Play state lives in its own subdirectory so a live session never
# overwrites the committed stage-0 evidence artifacts one level up.
KEEPER_DIR = DEFAULT_OUTPUT_DIR / "keeper"
SESSION_STATE_PATH = KEEPER_DIR / "keeper_session.json"
LEDGER_PATH = KEEPER_DIR / "campaign_ledger.json"
DEFAULT_ENGINE_PARAMETERS = {
    "generations": 3,
    "population": 4,
    "damage_cycles": 2,
    "ticks": 16,
    "dropout_rate": 0.2,
    "repair_epochs": 40,
}


def _campaign_shell(
    *,
    campaign_id: str,
    keeper_label: str,
    created_date: str,
    predecessor_campaign_id: str | None,
    base_seed: int,
    slip_profile: dict,
) -> dict:
    return {
        "campaign_id": campaign_id,
        "keeper_label": keeper_label,
        "created_date": created_date,
        "predecessor_campaign_id": predecessor_campaign_id,
        "status": "active",
        "slip_profile": slip_profile,
        "base_seed": base_seed,
        "eras": [],
        "unlocks": [],
    }


def new_keeper_state(
    *,
    campaign_id: str = "keeper_campaign_001",
    keeper_label: str = "keeper",
    created_date: str = REPORT_DATE,
    base_seed: int = 20260707,
    slip_profile: dict | None = None,
    engine_parameters: dict | None = None,
) -> dict:
    """A fresh Keeper session: one active campaign, zero eras. The
    covenant and engine parameters are fixed at creation so every later
    era is reproducible from the state file alone."""
    if slip_profile is None:
        slip_profile = json.loads(
            SLIP_PROFILE_PATH.read_text(encoding="utf-8")
        )
    return {
        "session_format": SESSION_FORMAT,
        "active_campaign_id": campaign_id,
        "engine_parameters": dict(
            DEFAULT_ENGINE_PARAMETERS, **(engine_parameters or {})
        ),
        "campaigns": [
            _campaign_shell(
                campaign_id=campaign_id,
                keeper_label=keeper_label,
                created_date=created_date,
                predecessor_campaign_id=None,
                base_seed=base_seed,
                slip_profile=slip_profile,
            )
        ],
    }


def advance_keeper_state(
    state: dict,
    weather: str,
    *,
    seed_grids: list[dict] | None = None,
    generation_model: dict | None = None,
    repair_model: dict | None = None,
    legibility_model: dict | None = None,
) -> dict:
    """Run one era of the active campaign and return the turn summary.

    On extinction the successor bloodline is created immediately
    (carrying only the Keeper's unlocks, via the predecessor pointer —
    DR 0022) and becomes the active campaign; the NEXT advance runs the
    successor's first era from seeds."""
    if state.get("session_format") != SESSION_FORMAT:
        raise ValueError("not a keeper_session_v1 state")
    params = state["engine_parameters"]
    by_id = {c["campaign_id"]: c for c in state["campaigns"]}
    campaign = by_id[state["active_campaign_id"]]
    if seed_grids is None:
        seed_grids = build_seed_grids()
    if generation_model is None or repair_model is None:
        generation_model, repair_model = train_session_models(
            seed_grids,
            repair_epochs=params["repair_epochs"],
            rng_seed=campaign["base_seed"],
        )
    if legibility_model is None:
        legibility_model = train_legibility_model()

    unlocks_before = len(campaign["unlocks"])
    era_record = advance_campaign(
        campaign,
        weather,
        seed_grids=seed_grids,
        generation_model=generation_model,
        repair_model=repair_model,
        legibility_model=legibility_model,
        generations=params["generations"],
        population=params["population"],
        damage_cycles=params["damage_cycles"],
        ticks=params["ticks"],
        dropout_rate=params["dropout_rate"],
    )
    succession = (
        apply_succession(state, campaign)
        if campaign["status"] == "extinct"
        else None
    )
    return {
        "campaign_id": campaign["campaign_id"],
        "status": campaign["status"],
        "era": _era_digest(era_record),
        "unlocks_earned": campaign["unlocks"][unlocks_before:],
        "unlock_state_count": len(
            resolve_unlock_state(
                state["campaigns"], state["active_campaign_id"]
            )
        ),
        "active_campaign_id": state["active_campaign_id"],
        "succession": succession,
    }


def apply_succession(state: dict, campaign: dict) -> dict:
    """An extinct campaign's successor becomes the active bloodline:
    fresh from seeds, carrying ONLY the Keeper's unlocks through the
    predecessor pointer (DR 0022 — never copied)."""
    plan = plan_succession(campaign)
    if plan is None:
        raise ValueError(
            f"campaign {campaign['campaign_id']!r} is not extinct — "
            "succession is for ended bloodlines"
        )
    successor = _campaign_shell(
        campaign_id=plan["campaign_id"],
        keeper_label=plan["keeper_label"],
        created_date=plan["created_date"],
        predecessor_campaign_id=plan["predecessor_campaign_id"],
        base_seed=plan["base_seed"],
        slip_profile=campaign["slip_profile"],
    )
    state["campaigns"].append(successor)
    state["active_campaign_id"] = successor["campaign_id"]
    return {
        "successor_campaign_id": successor["campaign_id"],
        "carried_unlock_count": len(
            resolve_unlock_state(
                state["campaigns"], successor["campaign_id"]
            )
        ),
    }


def keeper_state_summary(state: dict) -> dict:
    """The Keeper page's read model — digests only, blobs stay on disk."""
    campaigns = []
    for campaign in state["campaigns"]:
        campaigns.append(
            {
                "campaign_id": campaign["campaign_id"],
                "keeper_label": campaign["keeper_label"],
                "status": campaign["status"],
                "predecessor_campaign_id": campaign[
                    "predecessor_campaign_id"
                ],
                "base_seed": campaign["base_seed"],
                "profile_id": campaign["slip_profile"].get("profile_id"),
                "era_count": len(campaign["eras"]),
                "eras": [_era_digest(era) for era in campaign["eras"]],
                "unlocks": campaign["unlocks"],
            }
        )
    return {
        "session_format": state["session_format"],
        "active_campaign_id": state["active_campaign_id"],
        "engine_parameters": state["engine_parameters"],
        "campaigns": campaigns,
        "unlock_state": resolve_unlock_state(
            state["campaigns"], state["active_campaign_id"]
        ),
        "weather_names": list(WEATHER_NAMES),
        "unlock_thresholds": UNLOCK_THRESHOLDS,
    }


def load_keeper_state(path: str | Path = SESSION_STATE_PATH) -> dict | None:
    path = Path(path)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_keeper_state(
    state: dict,
    path: str | Path = SESSION_STATE_PATH,
    ledger_path: str | Path | None = None,
) -> None:
    """Backup-before-overwrite (the workshop's save discipline); every
    save refreshes the derived DR 0022 schema-v1 ledger, which lives
    next to the state file by default."""
    path = Path(path)
    if ledger_path is None:
        ledger_path = path.parent / "campaign_ledger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.with_suffix(".bak.json").write_text(
            path.read_text(encoding="utf-8"), encoding="utf-8"
        )
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    if ledger_path is not None:
        Path(ledger_path).write_text(
            json.dumps(
                build_campaign_ledger({"campaigns": state["campaigns"]}),
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "The Keeper session lab: --mode demo writes the G2 stage-0 "
            "artifacts; new/advance/status drive the persistent session "
            "(G4). Machine-readable JSON on stdout."
        )
    )
    parser.add_argument(
        "--mode",
        choices=("demo", "new", "advance", "status"),
        default="demo",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR
    )
    parser.add_argument("--state-path", type=Path, default=SESSION_STATE_PATH)
    parser.add_argument("--base-seed", type=int, default=20260707)
    parser.add_argument("--repair-epochs", type=int, default=40)
    parser.add_argument("--campaign-id", default="keeper_campaign_001")
    parser.add_argument(
        "--weather", choices=WEATHER_NAMES, default="calm"
    )
    args = parser.parse_args()

    if args.mode == "demo":
        session = run_keeper_session(
            base_seed=args.base_seed, repair_epochs=args.repair_epochs
        )
        report = build_session_report(session)
        write_session_artifacts(args.output_dir, report, session)
        print(
            json.dumps(
                {
                    "artifact_id": report["artifact_id"],
                    "decision": report["decision"]["status"],
                    "era_count": report["metrics"]["era_count"],
                    "unlock_fact_count": report["metrics"][
                        "unlock_fact_count"
                    ],
                    "output_dir": str(args.output_dir),
                },
                indent=2,
            )
        )
        return

    if args.mode == "new":
        if Path(args.state_path).exists():
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": "a keeper session already exists — "
                        "advance it, or move the state file aside to "
                        "start over",
                    }
                )
            )
            raise SystemExit(1)
        state = new_keeper_state(
            campaign_id=args.campaign_id,
            base_seed=args.base_seed,
            engine_parameters={"repair_epochs": args.repair_epochs},
        )
        save_keeper_state(state, args.state_path)
        print(json.dumps({"ok": True, **keeper_state_summary(state)}))
        return

    state = load_keeper_state(args.state_path)
    if args.mode == "status":
        if state is None:
            print(json.dumps({"ok": False, "error": "no keeper session yet"}))
            raise SystemExit(1)
        print(json.dumps({"ok": True, **keeper_state_summary(state)}))
        return

    # advance
    if state is None:
        state = new_keeper_state(
            campaign_id=args.campaign_id,
            base_seed=args.base_seed,
            engine_parameters={"repair_epochs": args.repair_epochs},
        )
    turn = advance_keeper_state(state, args.weather)
    save_keeper_state(state, args.state_path)
    print(json.dumps({"ok": True, **turn}))


if __name__ == "__main__":
    main()
