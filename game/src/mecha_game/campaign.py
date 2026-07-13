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
# "real" (G4): the G2-ingested REAL CuBFF snapshots as the pressure
# source — the documented upgrade, zero seam changes.
WEATHER_NAMES = ("calm", "stable_soup", "storm", "real")
REAL_INGEST_REPORT = (
    Path("data")
    / "cubff_real_ingest"
    / "real_snapshot_ingest_stage0_report.json"
)
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


def load_real_weather_source(start: Path | None = None) -> list[dict]:
    """The G2-ingested REAL snapshot records, VERBATIM from the
    committed ingest report, in epoch order — the documented upgrade
    path (DR 0021: 'real exports drop in with no seam changes')."""
    from mecha_game.packets import data_search_origins

    for origin in data_search_origins(start):
        for base in (origin, *origin.parents):
            report_path = base / REAL_INGEST_REPORT
            if report_path.is_file():
                report = json.loads(
                    report_path.read_text(encoding="utf-8")
                )
                records = report.get("ingested_snapshots") or []
                if not records:
                    raise ValueError(
                        "the real-ingest gate holds no snapshots "
                        f"(status: {report.get('status')})"
                    )
                return sorted(records, key=lambda r: r["epoch"])
    raise FileNotFoundError(
        "no real-ingest report near this installation"
    )


def build_weather_source(name: str) -> list[dict] | None:
    """Forecast name -> CuBFF pressure source for the promoted evolve
    (``calm`` = the byte-identical no-source default)."""
    if name == "calm":
        return None
    if name == "stable_soup":
        return [_stable_snapshot(i) for i in range(6)]
    if name == "storm":
        return [_chaotic_snapshot(i) for i in range(6)]
    if name == "real":
        return load_real_weather_source()
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
    cache_dir: str | Path | None = None,
) -> dict:
    """Load the corpus, the covenant, and train the promoted models.

    The legibility model is the COMMITTED adopted artifact (DR 0019 —
    the learned signal is primary); its absence is a hard error, never
    a silent fallback.

    ``cache_dir`` (F11): the repair model — the slow trainer — caches
    to a file keyed on the corpus's grid ids + epochs + seed; a cached
    load is byte-equal to fresh training (the trainer is deterministic
    in its inputs), PINNED by test. ``None`` always trains."""
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
    repair_model = None
    cache_path = None
    if cache_dir is not None:
        import hashlib

        key_material = json.dumps(
            {
                "grid_ids": [
                    grid["grid_id"]
                    for grid in seed_grids[:REPAIR_TRAINING_COUNT]
                ],
                "epochs": repair_epochs,
                "rng_seed": rng_seed,
            },
            sort_keys=True,
        )
        key = hashlib.sha256(key_material.encode("utf-8")).hexdigest()[
            :16
        ]
        cache_path = Path(cache_dir) / f"repair_model_{key}.json"
        if cache_path.is_file():
            repair_model = json.loads(
                cache_path.read_text(encoding="utf-8")
            )
    if repair_model is None:
        repair_model = train_repair_model(
            seed_grids[:REPAIR_TRAINING_COUNT],
            epochs=repair_epochs,
            rng_seed=rng_seed,
        )
        if cache_path is not None:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(
                json.dumps(repair_model) + "\n", encoding="utf-8"
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
        # Resume support (F17): eras recorded in the LEDGER before
        # this process; era indices/seeds continue from the offset,
        # and the resumed first era's founders come from the ledger.
        self.era_offset = 0
        self.resume_founders: list[dict] | None = None
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

    def advance_era(
        self, weather: str, *, released_grids: list[dict] | None = None
    ) -> dict:
        """Advance the living bloodline by exactly one era (the lab's
        `advance_campaign` semantics: founders = the previous era's
        elites; unlock facts accumulate; extinction ends the chain).

        ``released_grids`` (the lab's E5 seam — DR 0021's Contribute):
        the Keeper's released creatures LEAD the founder pool, ahead
        of the prior era's elites (the T1/DR 0016 founders-lead rule);
        admission or verbatim rejection is the engine's own judgment
        inside ``evolve``. ``None`` keeps every prior flow identical."""
        if self.campaign["status"] != "active":
            raise ValueError(
                f"campaign {self.campaign['campaign_id']!r} is "
                f"{self.campaign['status']} — an ended bloodline cannot "
                "run another era (successor() starts the next)"
            )
        era_index = self.era_offset + len(self.eras)
        if self.eras:
            chain = [
                elite["grid"] for elite in self.eras[-1]["elites"]
            ]
        elif self.resume_founders is not None:
            # The resumed chain continues from the ledger's own pool.
            chain = self.resume_founders
        else:
            chain = []
        founder_pool = list(released_grids or []) + chain
        founder_grids = founder_pool or None
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

    def record_review_replay(self, era_index: int = -1) -> dict:
        """The Review step's window (F10): the era's best elite lives
        one RECORDED life at the era's own seed and parameters —
        honest label per the lab: a real recorded life of a real era
        creature, replayed post-era (the in-era lives ran without
        frame recording; threading record_frames through evolve
        remains the engine's named future seam)."""
        from mecha_game.replay import build_replay

        if not self.eras:
            raise ValueError("no era to review yet")
        era = self.eras[era_index]
        if not era["elites"]:
            raise ValueError(
                f"era {era['era_index']} ended with no elites to replay"
            )
        best = max(
            era["elites"],
            key=lambda elite: (elite["fitness"], elite["niche_key"]),
        )
        replay = build_replay(
            best["grid"],
            self.campaign["slip_profile"],
            self.inputs["repair_model"],
            damage_cycles=self.era_config["damage_cycles"],
            ticks=self.era_config["ticks"],
            dropout_rate=self.era_config["dropout_rate"],
            rng_seed=era["rng_seed"],
        )
        replay["honest_label"] = (
            "a real recorded life of a real era creature, replayed "
            f"post-era at era {era['era_index']}'s own seed"
        )
        return replay

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

    # -- replay persistence (F17 — DR 0022's pointer rule) -----------------

    def save_review_replay(
        self,
        replay: dict,
        keeper_dir: str | Path,
        ledger_path: str | Path,
    ) -> Path:
        """Persist a review: the artifact stays a FILE, the ledger
        stores the pointer + sha256 (skipping a duplicate pointer)."""
        import hashlib

        from mecha_engine.storage import (
            load_replay_rows,
            open_ledger,
            record_replay,
        )

        keeper_dir = Path(keeper_dir)
        # The era index is derivable from the replay's own seed.
        era_index = (
            replay["parameters"]["rng_seed"] - self.campaign["base_seed"]
        ) // ERA_SEED_STRIDE
        path = (
            keeper_dir
            / "replays"
            / f"{self.campaign['campaign_id']}_era{era_index}.json"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(replay, indent=2) + "\n"
        path.write_text(payload, encoding="utf-8")
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        relative = path.name
        conn = open_ledger(Path(ledger_path))
        try:
            rows = load_replay_rows(
                conn, self.campaign["campaign_id"]
            )
            already = any(
                row["era_index"] == era_index
                and row["artifact_path"] == relative
                for row in rows
            )
            if not already:
                record_replay(
                    conn,
                    self.campaign["campaign_id"],
                    era_index,
                    relative,
                    digest,
                )
        finally:
            conn.close()
        return path

    def load_review_replay(
        self,
        keeper_dir: str | Path,
        ledger_path: str | Path,
        era_index: int,
    ) -> dict | None:
        """A persisted review, hash-verified against the ledger's
        recorded sha256 (a tampered artifact is refused, named)."""
        import hashlib

        from mecha_engine.storage import load_replay_rows, open_ledger

        conn = open_ledger(Path(ledger_path))
        try:
            rows = [
                row
                for row in load_replay_rows(
                    conn, self.campaign["campaign_id"]
                )
                if row["era_index"] == era_index
            ]
        finally:
            conn.close()
        if not rows:
            return None
        row = rows[0]
        path = Path(keeper_dir) / "replays" / row["artifact_path"]
        payload = path.read_text(encoding="utf-8")
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        if digest != row["artifact_sha256"]:
            raise ValueError(
                f"replay artifact {row['artifact_path']} fails its "
                f"recorded sha256 — refusing a tampered recording"
            )
        return json.loads(payload)

    # -- campaign state resume (F17) ----------------------------------------

    STATE_FORMAT = "keeper_campaign_state_v1"

    def save_state(self, path: str | Path) -> Path:
        """The ACTIVE campaign state (the spent covenant included) as
        play state — the ledger keeps the evidence; this file keeps
        the Keeper's place."""
        payload = {
            "state_format": self.STATE_FORMAT,
            "campaign_id": self.campaign["campaign_id"],
            "keeper_label": self.campaign["keeper_label"],
            "created_date": self.campaign["created_date"],
            "predecessor_campaign_id": self.campaign[
                "predecessor_campaign_id"
            ],
            "status": self.campaign["status"],
            "base_seed": self.campaign["base_seed"],
            "era_count": self.era_offset + len(self.eras),
            "unlocks": self.campaign["unlocks"],
            "inherited_unlocks": self.inherited_unlocks,
            "base_profile": self.base_profile,
            "slip_profile": self.campaign["slip_profile"],
            "era_config": self.era_config,
        }
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.with_suffix(".bak.json").write_text(
                path.read_text(encoding="utf-8"), encoding="utf-8"
            )
        path.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
        return path

    @classmethod
    def load_state(
        cls,
        inputs: dict,
        state_path: str | Path,
        ledger_path: str | Path,
    ) -> "KeeperCampaign":
        """Resume a campaign exactly where it stopped: the spent
        covenant and earned facts from the state file, the era chain's
        founders from the LEDGER's own pool (pinned: a resumed
        continuation matches the unbroken run byte for byte)."""
        from mecha_engine.storage import load_founder_pool, open_ledger

        payload = json.loads(
            Path(state_path).read_text(encoding="utf-8")
        )
        if payload.get("state_format") != cls.STATE_FORMAT:
            raise ValueError(
                "not a keeper campaign state: "
                f"{payload.get('state_format')!r}"
            )
        campaign = cls(
            inputs,
            campaign_id=payload["campaign_id"],
            keeper_label=payload["keeper_label"],
            created_date=payload["created_date"],
            predecessor_campaign_id=payload[
                "predecessor_campaign_id"
            ],
            base_seed=payload["base_seed"],
            era_config=payload["era_config"],
            inherited_unlocks=payload["inherited_unlocks"],
        )
        campaign.campaign["status"] = payload["status"]
        campaign.campaign["unlocks"] = payload["unlocks"]
        campaign.base_profile = payload["base_profile"]
        campaign.campaign["slip_profile"] = payload["slip_profile"]
        campaign.era_offset = payload["era_count"]
        if campaign.era_offset:
            conn = open_ledger(Path(ledger_path))
            try:
                campaign.resume_founders = load_founder_pool(
                    conn, payload["campaign_id"]
                )
            finally:
                conn.close()
        return campaign

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
                recorded = {
                    era["era_index"]
                    for era in campaign_history(
                        conn, self.campaign["campaign_id"]
                    )["eras"]
                }
            except (KeyError, ValueError):
                recorded = set()
            for era in self.eras:
                if era["era_index"] in recorded:
                    continue
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
