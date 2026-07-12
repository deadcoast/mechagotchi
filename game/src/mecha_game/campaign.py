"""The Keeper's campaign — eras of the soup, in the client (F4).

DR 0021's core loop as a PRODUCT surface, mirroring the proven G2/G4
session lab (`labs/game_loop/session_runner.py`) without importing it
(boundary law, DR 0033): one era = one promoted `runtime.evolve` run;
the next era's founder pool is the previous era's elites (the
persistence spine); unlock FACTS are earned from era-report metrics
against the lab's A4-calibrated thresholds (tuning data, falsifiable
by test); an extinct bloodline's successor starts fresh from seeds
carrying ONLY the Keeper's unlocks (roguelite stakes); the campaign
persists through `mecha_engine.storage`'s ledger (DR 0022 —
blob-authoritative, one era per transaction).

One DOCUMENTED divergence from the lab session: the game injects the
LEARNED readability scorer (`runtime.learned_readability_score` over
the committed adopted model) as `evolve`'s readability hook — the lab
session injected the historical proxy. DR 0019 makes the learned
signal primary; the client never re-implements an engine number.

Weather stays synthetic until the real-CuBFF ingest gate clears
(Phase G): the snapshot builders mirror the session lab's verbatim,
and real exports drop into the same seam with no client change.
"""

from __future__ import annotations

import json
from pathlib import Path

from mecha_engine.generation import (
    GenerationModel,
    train_generation_model,
)
from mecha_engine.repair import train_repair_model
from mecha_engine.runtime import evolve, learned_readability_score
from mecha_engine.storage import (
    campaign_history,
    open_ledger,
    record_campaign,
    record_era,
)

# Mirrored session-lab constants (labs/game_loop/session_runner.py —
# tuning data plus the DR 0021 structure, cited not imported).
ERA_SEED_STRIDE = 1_000_000
SUCCESSOR_SEED_OFFSET = 50_000_000
WEATHER_NAMES = ("calm", "stable_soup", "storm")
LEGIBILITY_BLEND = 0.7
LEGIBILITY_BLEND_STEP = 0.05
LEGIBILITY_BLEND_CAP = 0.9
REPAIR_TRAINING_COUNT = 40
# The cycle 09 A4 session configuration at the ratified 16x16 corpus.
ERA_CONFIG = {
    "generations": 6,
    "population": 16,
    "damage_cycles": 2,
    "ticks": 16,
    "dropout_rate": 0.2,
}
UNLOCK_THRESHOLDS: dict[str, dict] = {
    "niche_mastery": {
        "metric_path": "report.summary.archive.filled_niches",
        "tiers": [16, 26, 36],
    },
    "bloodline_depth": {
        "metric_path": "report.summary.max_lineage_generation",
        "tiers": [2, 3, 4],
    },
    "quality_diversity": {
        "metric_path": "report.summary.archive.qd_score",
        "tiers": [9.0, 18.0, 33.0],
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
    """A calmly replicating soup (the session lab's synthetic weather)."""
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
    """Forecast name -> CuBFF pressure source for the promoted evolve
    (``calm`` = the byte-identical no-source default)."""
    if name == "calm":
        return None
    if name == "stable_soup":
        return [_stable_snapshot(i) for i in range(6)]
    if name == "storm":
        return [_chaotic_snapshot(i) for i in range(6)]
    raise ValueError(f"unknown weather forecast: {name}")


def _resolve_metric(era_record: dict, path: str):
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
    """The unlock FACTS an era earns (DR 0021's table; the lab's exact
    rule): a threshold met must unlock, unmet must not, an (axis, tier)
    already earned is never re-earned; facts cite metric path, value,
    and threshold verbatim (DR 0022's unlocks shape)."""
    earned = {(fact["axis"], fact["tier"]) for fact in already_unlocked}
    facts: list[dict] = []
    for axis, spec in UNLOCK_THRESHOLDS.items():
        try:
            value = _resolve_metric(era_record, spec["metric_path"])
        except KeyError:
            continue
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


def _max_tier(unlock_state: list[dict], axis: str) -> int:
    return max(
        (fact["tier"] for fact in unlock_state if fact["axis"] == axis),
        default=0,
    )


def legibility_blend_for(unlock_state: list[dict]) -> float:
    """The earned parenting blend (DR 0021's legibility axis)."""
    return round(
        min(
            LEGIBILITY_BLEND_CAP,
            LEGIBILITY_BLEND
            + LEGIBILITY_BLEND_STEP * _max_tier(unlock_state, "legibility"),
        ),
        6,
    )


# The suite-speed configuration (tests); the session scale is the
# A4-calibrated default above.
TINY_ERA_CONFIG = {
    "generations": 2,
    "population": 6,
    "damage_cycles": 1,
    "ticks": 8,
    "dropout_rate": 0.2,
}


def default_campaign_paths(start: Path | None = None) -> dict:
    """Resolve the campaign inputs from a repo checkout or a frozen
    bundle (the same walk-up rule as the hello fixtures)."""
    from mecha_game.packets import data_search_origins

    for origin in data_search_origins(start):
        found = _campaign_paths_under(origin)
        if found is not None:
            return found
    raise FileNotFoundError(
        "no campaign fixture corpus near this installation — "
        "pass explicit paths"
    )


def _campaign_paths_under(origin: Path) -> dict | None:
    for base in (origin, *origin.parents):
        seed_dir = base / "data" / "seed_grids_16x16"
        slip = base / "data" / "slips" / "valid" / "slip_lcd_seed.json"
        adopted = (
            base
            / "data"
            / "readability_benchmark"
            / "adopted_readability_model.json"
        )
        if seed_dir.is_dir() and slip.is_file() and adopted.is_file():
            return {
                "seed_dir": seed_dir,
                "slip_path": slip,
                "adopted_model_path": adopted,
            }
    return None


def load_campaign_inputs(
    seed_dir: str | Path,
    slip_path: str | Path,
    adopted_model_path: str | Path,
    *,
    repair_epochs: int = 40,
    rng_seed: int = 20260707,
    seed_limit: int | None = None,
) -> dict:
    """Load the corpus, the covenant, and train the promoted models.

    The legibility model is the COMMITTED adopted artifact (DR 0019 —
    the learned signal is primary); its absence is a hard error, never
    a silent fallback."""
    seed_paths = sorted(Path(seed_dir).glob("mg_seed16_*.json"))
    if seed_limit is not None:
        seed_paths = seed_paths[:seed_limit]
    seed_grids = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in seed_paths
    ]
    if not seed_grids:
        raise FileNotFoundError(f"no 16x16 seed corpus under {seed_dir}")
    slip_profile = json.loads(
        Path(slip_path).read_text(encoding="utf-8")
    )
    adopted = json.loads(
        Path(adopted_model_path).read_text(encoding="utf-8")
    )
    legibility_model = {
        "weights": adopted["weights"],
        "reference_features": adopted["reference_features"],
    }
    generation_model = train_generation_model(seed_grids)
    repair_model = train_repair_model(
        seed_grids[:REPAIR_TRAINING_COUNT],
        epochs=repair_epochs,
        rng_seed=rng_seed,
    )
    return {
        "seed_grids": seed_grids,
        "slip_profile": slip_profile,
        "generation_model": generation_model,
        "repair_model": repair_model,
        "legibility_model": legibility_model,
    }


class KeeperCampaign:
    """One bloodline: a chain of eras, its unlock facts, its ledger."""

    def __init__(
        self,
        inputs: dict,
        *,
        campaign_id: str = "keeper_campaign",
        keeper_label: str = "keeper",
        created_date: str = "2026-07-12",
        base_seed: int = 20260707,
        predecessor_campaign_id: str | None = None,
        era_config: dict | None = None,
        inherited_unlocks: list[dict] | None = None,
    ) -> None:
        self.inputs = inputs
        self.era_config = {**ERA_CONFIG, **(era_config or {})}
        # The BASE covenant and base parameters the budget computes
        # from (spends never compound against themselves — F7).
        self.base_profile = json.loads(
            json.dumps(inputs["slip_profile"])
        )
        self.base_parameters = {
            "population": self.era_config["population"],
            "generations": self.era_config["generations"],
        }
        # Roguelite inheritance (DR 0022's succession rule, resolved
        # in memory): the predecessor chain's facts, never copied into
        # this campaign's OWN unlocks.
        self.inherited_unlocks = list(inherited_unlocks or [])
        self.campaign = {
            "campaign_id": campaign_id,
            "keeper_label": keeper_label,
            "created_date": created_date,
            "predecessor_campaign_id": predecessor_campaign_id,
            "status": "active",
            "slip_profile": inputs["slip_profile"],
            "base_seed": base_seed,
            "eras": [],
            "unlocks": [],
        }

    # -- read model ------------------------------------------------------

    @property
    def status(self) -> str:
        return self.campaign["status"]

    @property
    def eras(self) -> list[dict]:
        return self.campaign["eras"]

    @property
    def unlocks(self) -> list[dict]:
        return self.campaign["unlocks"]

    def unlock_state(self) -> list[dict]:
        """The Keeper's full unlock state: inherited facts plus this
        campaign's own (the in-memory mirror of the ledger's
        pointer-chain resolution)."""
        return self.inherited_unlocks + self.campaign["unlocks"]

    def budget(self) -> dict:
        """The spendable covenant budget (F7 — DR 0021's table)."""
        from mecha_game.covenant import covenant_budget

        return covenant_budget(
            self.base_profile, self.base_parameters, self.unlock_state()
        )

    def species_memory(self) -> dict:
        """What the Keeper reviews: the last era's repertoire and the
        campaign's earned facts — report fields verbatim."""
        if not self.eras:
            return {
                "eras_run": 0,
                "status": self.status,
                "unlocks": list(self.unlocks),
            }
        era = self.eras[-1]
        summary = era["report"]["summary"]
        return {
            "eras_run": len(self.eras),
            "status": self.status,
            "last_era": {
                "era_index": era["era_index"],
                "weather": era["weather"]["forecast"],
                "filled_niches": summary["archive"]["filled_niches"],
                "qd_score": summary["archive"]["qd_score"],
                "max_lineage_generation": summary[
                    "max_lineage_generation"
                ],
                "went_extinct": era["derived"]["went_extinct"],
                "elite_count": len(era["elites"]),
                "elite_mean_learned_readability": era["derived"][
                    "elite_mean_learned_readability"
                ],
            },
            "unlocks": list(self.unlocks),
        }

    def best_elite_grid(self) -> dict | None:
        """The last era's best elite — the adoption handoff (the
        companion loop adopts it through the engine's own gate)."""
        if not self.eras or not self.eras[-1]["elites"]:
            return None
        best = max(
            self.eras[-1]["elites"],
            key=lambda elite: (elite["fitness"], elite["niche_key"]),
        )
        return json.loads(json.dumps(best["grid"]))

    # -- the loop --------------------------------------------------------

    def advance_era(self, weather: str) -> dict:
        """Advance the living bloodline by exactly one era (the lab's
        `advance_campaign` semantics: founders = the previous era's
        elites; unlock facts accumulate; extinction ends the chain)."""
        if self.campaign["status"] != "active":
            raise ValueError(
                f"campaign {self.campaign['campaign_id']!r} is "
                f"{self.campaign['status']} — an ended bloodline cannot "
                "run another era (successor() starts the next)"
            )
        era_index = len(self.eras)
        founder_grids = (
            [elite["grid"] for elite in self.eras[-1]["elites"]]
            if self.eras
            else None
        )
        legibility_model = self.inputs["legibility_model"]

        def scorer(grid: dict) -> float:
            return learned_readability_score(grid, legibility_model)

        archive, report = evolve(
            self.inputs["seed_grids"],
            self.campaign["slip_profile"],
            self.inputs["generation_model"],
            self.inputs["repair_model"],
            readability_scorer=scorer,
            rng_seed=self.campaign["base_seed"]
            + era_index * ERA_SEED_STRIDE,
            founder_grids=founder_grids,
            cubff_pressure_source=build_weather_source(weather),
            readability_selection={
                **legibility_model,
                "blend": legibility_blend_for(self.unlock_state()),
            },
            **self.era_config,
        )
        # The archive's elites in niche-key order — the same
        # deterministic ordering evolve uses for elite parents
        # (the lab's `_era_elites`, records spread VERBATIM).
        elites = [
            {"niche_key": niche, **archive["elites"][niche]}
            for niche in sorted(archive["elites"])
        ]
        went_extinct = (
            len(report["generations"]) < report["generations_requested"]
            or not elites
        )
        multipliers = [
            entry["dropout_multiplier"]
            for entry in report.get("cubff_pressure", {}).get(
                "by_generation", []
            )
        ]
        legibility = (
            round(
                sum(
                    learned_readability_score(
                        elite["grid"], legibility_model
                    )
                    for elite in elites
                )
                / len(elites),
                6,
            )
            if elites
            else None
        )
        era_record = {
            "era_index": era_index,
            "rng_seed": self.campaign["base_seed"]
            + era_index * ERA_SEED_STRIDE,
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
                "max_dropout_multiplier_survived": (
                    max(multipliers)
                    if multipliers and not went_extinct
                    else None
                ),
                "elite_mean_learned_readability": legibility,
            },
        }
        self.campaign["eras"].append(era_record)
        self.campaign["unlocks"].extend(
            evaluate_unlocks(era_record, self.campaign["unlocks"])
        )
        if went_extinct:
            self.campaign["status"] = "extinct"
        return era_record

    def plan_succession(self) -> dict | None:
        """Roguelite stakes: the successor's parameters once the
        bloodline is extinct; None while it lives."""
        if self.campaign["status"] != "extinct":
            return None
        return {
            "campaign_id": f"{self.campaign['campaign_id']}_successor",
            "keeper_label": self.campaign["keeper_label"],
            "created_date": self.campaign["created_date"],
            "predecessor_campaign_id": self.campaign["campaign_id"],
            "base_seed": self.campaign["base_seed"]
            + SUCCESSOR_SEED_OFFSET,
        }

    def successor(self) -> "KeeperCampaign":
        plan = self.plan_succession()
        if plan is None:
            raise ValueError(
                "the bloodline lives — succession is extinction's door"
            )
        return KeeperCampaign(
            self.inputs,
            # Roguelite: the successor carries ONLY the unlocks — the
            # spent covenant and caps reset to base; the fresh
            # bloodline spends again from its inherited budget.
            era_config={**self.era_config, **self.base_parameters},
            inherited_unlocks=self.unlock_state(),
            **plan,
        )

    # -- persistence (DR 0022) --------------------------------------------

    def save(self, ledger_path: str | Path) -> Path:
        """Persist the campaign into the storage module's ledger —
        blob-authoritative, one era per transaction; re-saving updates
        the status row and appends only unseen eras."""
        ledger_path = Path(ledger_path)
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        conn = open_ledger(ledger_path)
        try:
            record_campaign(conn, self.campaign)
            try:
                recorded = len(
                    campaign_history(
                        conn, self.campaign["campaign_id"]
                    )["eras"]
                )
            except (KeyError, ValueError):
                recorded = 0
            for era in self.eras[recorded:]:
                record_era(
                    conn,
                    self.campaign["campaign_id"],
                    # The ledger's era shape wants the extinction flag
                    # top-level (DR 0022 schema); the record itself
                    # stays verbatim.
                    {**era, "went_extinct": era["derived"]["went_extinct"]},
                    self.campaign["slip_profile"],
                    founders=None,
                    unlocks=[
                        fact
                        for fact in self.unlocks
                        if fact["earned_era_index"] == era["era_index"]
                    ],
                )
        finally:
            conn.close()
        return ledger_path
