"""The Keeper's campaign â€” eras of the soup, in the client (F4).

DR 0021's core loop as a PRODUCT surface, mirroring the proven G2/G4
session lab (`labs/game_loop/session_runner.py`) without importing it
(boundary law, DR 0033): one era = one promoted `runtime.evolve` run;
the next era's founder pool is the previous era's elites (the
persistence spine); unlock FACTS are earned from era-report metrics
against the lab's A4-calibrated thresholds (tuning data, falsifiable
by test); an extinct bloodline's successor starts fresh from seeds
carrying ONLY the Keeper's unlocks (roguelite stakes); the campaign
persists through `mecha_engine.storage`'s ledger (DR 0022 â€”
blob-authoritative, one era per transaction).

One DOCUMENTED divergence from the lab session: the game injects the
LEARNED readability scorer (`runtime.learned_readability_score` over
the committed adopted model) as `evolve`'s readability hook â€” the lab
session injected the historical proxy. DR 0019 makes the learned
signal primary; the client never re-implements an engine number.

Weather stays synthetic until the real-CuBFF ingest gate clears
(Phase G): the snapshot builders mirror the session lab's verbatim,
and real exports drop into the same seam with no client change.
"""

from __future__ import annotations

from collections import Counter
import copy
import json
from pathlib import Path

from mecha_engine.generation import (
    GenerationModel,
    train_generation_model,
)
from mecha_game.compatibility import campaign_writer
from mecha_engine.repair import train_repair_model
from mecha_engine.runtime import evolve, learned_readability_score
from mecha_engine.storage import (
    campaign_history,
    canonical_json,
    open_ledger,
    record_campaign,
    record_era,
)

# Mirrored session-lab constants (labs/game_loop/session_runner.py â€”
# tuning data plus the DR 0021 structure, cited not imported).
ERA_SEED_STRIDE = 1_000_000
SUCCESSOR_SEED_OFFSET = 50_000_000
# "real" (G4): the G2-ingested REAL CuBFF snapshots as the pressure
# source â€” the documented upgrade, zero seam changes. "callback"
# (K4, DR 0043): the I3 compact records with the replication channel
# LIT â€” the first forecast whose harshness channels carry measured
# biology; same seam, zero engine changes.
WEATHER_NAMES = ("calm", "stable_soup", "storm", "real", "callback")
REAL_INGEST_REPORT = (
    Path("data")
    / "cubff_real_ingest"
    / "real_snapshot_ingest_stage0_report.json"
)
CALLBACK_STATES_PATH = (
    Path("data")
    / "cubff_real_ingest"
    / "callback_states"
    / "callback_states_compact.json"
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


def _founder_records(founders, released_count, report, *, population_policy='legacy_archive'):
    """Project uniquely attributable inputs into the existing unordered table.

    Duplicate IDs remain untouched in evolution and its verbatim report. The
    table cannot identify their individual inputs, so every such row is omitted.
    """
    submitted = Counter(grid.get('grid_id') for grid in founders)
    outcomes = {}
    for grid_id in report.get('founders', {}).get('admitted_ids', []):
        outcomes.setdefault(grid_id, []).append((True, None))
    for row in report.get('founders', {}).get('rejected', []):
        outcomes.setdefault(row['grid_id'], []).append((False, row['errors']))
    records = []
    for index, grid in enumerate(founders):
        # Ordered execution occurrences retain breeders; the historical SQL table
        # cannot truthfully represent their source kind. Never label them elites.
        if population_policy == 'generation_survivors_v1' and index >= released_count:
            continue
        grid_id = grid.get('grid_id')
        verdicts = outcomes.get(grid_id, [])
        if not isinstance(grid_id, str) or not grid_id or submitted[grid_id] != 1 or len(verdicts) != 1:
            continue
        admitted, errors = verdicts[0]
        records.append(dict(grid_id=grid_id, source='workshop_release' if index < released_count else 'era_elite',
            admitted=admitted, rejection_errors=copy.deepcopy(errors), grid=copy.deepcopy(grid)))
    return records


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


def load_real_weather_source(start: Path | None = None, *, source_records=None) -> list[dict]:
    """The G2-ingested REAL snapshot records, VERBATIM from the
    committed ingest report, in epoch order â€” the documented upgrade
    path (DR 0021: 'real exports drop in with no seam changes')."""
    from mecha_game.packets import data_search_origins

    from mecha_game.runtime_resources import validate_resource

    for base in data_search_origins(start):
        report_path = base / REAL_INGEST_REPORT
        if report_path.is_file():
            validate_resource(report_path)
            raw = report_path.read_bytes()
            report = json.loads(raw)
            if source_records is not None:
                from mecha_game.execution import source_record
                source_records.append(source_record(raw, role='weather', source_position=0,
                    label=REAL_INGEST_REPORT.as_posix()))
            records = report.get("ingested_snapshots") or []
            if not records:
                raise ValueError(
                    "the real-ingest gate holds no snapshots "
                    f"(status: {report.get('status')})"
                )
            return sorted(records, key=lambda r: r["epoch"])
    raise FileNotFoundError(
        "no real-ingest report in this installation"
    )



def load_callback_weather_source(start: Path | None = None, *, source_records=None) -> list[dict]:
    """The I3 callback compact records, VERBATIM in epoch order â€”
    the replication channel LIT (DR 0043; the committed evidence is
    self-verifying: tape + soup hash + all per-program scores). A
    missing or empty record file refuses with a named error, never a
    silent fallback (the G4/load_real_weather_source pattern)."""
    from mecha_game.packets import data_search_origins

    from mecha_game.runtime_resources import validate_resource

    for base in data_search_origins(start):
        states_path = base / CALLBACK_STATES_PATH
        if states_path.is_file():
            validate_resource(states_path)
            raw = states_path.read_bytes()
            payload = json.loads(raw)
            if source_records is not None:
                from mecha_game.execution import source_record
                source_records.append(source_record(raw, role='weather', source_position=0,
                    label=CALLBACK_STATES_PATH.as_posix()))
            records = payload.get("records") or []
            if not records:
                raise ValueError(
                    "the callback state file holds no records"
                )
            return sorted(records, key=lambda r: r["epoch"])
    raise FileNotFoundError(
        "no callback weather states in this installation "
        "(data/cubff_real_ingest/callback_states)"
    )



def build_weather_source(name: str, *, source_records=None) -> list[dict] | None:
    """Forecast name -> CuBFF pressure source for the promoted evolve
    (``calm`` = the byte-identical no-source default)."""
    if name == "calm":
        return None
    if name == "stable_soup":
        return [_stable_snapshot(i) for i in range(6)]
    if name == "storm":
        return [_chaotic_snapshot(i) for i in range(6)]
    if name == "real":
        return load_real_weather_source(source_records=source_records)
    if name == "callback":
        return load_callback_weather_source(source_records=source_records)
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
    bundle (the same explicit root as the hello fixtures)."""
    from mecha_game.packets import data_search_origins

    for origin in data_search_origins(start):
        found = _campaign_paths_under(origin)
        if found is not None:
            return found
    raise FileNotFoundError(
        "no campaign fixture corpus near this installation â€” "
        "pass explicit paths"
    )


def _campaign_paths_under(origin: Path) -> dict | None:
    from mecha_game.packets import DEFAULT_SLIP
    from mecha_game.runtime_resources import validate_resource

    seed_dir = origin / "data/seed_grids_16x16"
    slip = origin / DEFAULT_SLIP
    adopted = origin / "data/readability_benchmark/adopted_readability_model.json"
    if seed_dir.is_dir() and slip.is_file() and adopted.is_file():
        for path in (seed_dir, slip, adopted):
            validate_resource(path)
        return {"seed_dir": seed_dir, "slip_path": slip, "adopted_model_path": adopted}
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
    with_models: bool = True,
) -> dict:
    """Load the corpus/covenant; eager evolution models remain the default.

    ``with_models=False`` reads only the preparation inputs. Covenant review,
    import and constrained hatching do not need evolution models. The game
    prepares those later in its foreground-owned era worker.

    The legibility model is the COMMITTED adopted artifact (DR 0019 â€”
    the learned signal is primary); its absence is a hard error, never
    a silent fallback.

    ``cache_dir`` (F11): the repair model â€” the slow trainer â€” caches
    to a versioned file keyed on full ordered training contents, source
    bytes, trainer options and implementation identity. Corrupt cache bytes
    refuse without replacement. ``None`` always trains."""
    seed_paths = sorted(Path(seed_dir).glob("mg_seed16_*.json"))
    if seed_limit is not None:
        seed_paths = seed_paths[:seed_limit]
    from mecha_game.execution import source_record
    sources = []
    seed_grids = []
    for index, path in enumerate(seed_paths):
        raw = path.read_bytes()
        seed_grids.append(json.loads(raw))
        sources.append(source_record(raw, role='seed_corpus', source_position=index, label=path.name))
    if not seed_grids:
        raise FileNotFoundError(f"no 16x16 seed corpus under {seed_dir}")
    raw = Path(slip_path).read_bytes()
    slip_profile = json.loads(raw)
    sources.append(source_record(raw, role='covenant', label=Path(slip_path).name))
    raw = Path(adopted_model_path).read_bytes()
    adopted = json.loads(raw)
    sources.append(source_record(raw, role='readability_model', label=Path(adopted_model_path).name))
    legibility_model = {
        "weights": adopted["weights"],
        "reference_features": adopted["reference_features"],
    }
    inputs = {"seed_grids": seed_grids, "slip_profile": slip_profile,
              "legibility_model": legibility_model, "input_sources": sources}
    return (prepare_campaign_models(inputs, repair_epochs=repair_epochs,
            rng_seed=rng_seed, cache_dir=cache_dir) if with_models else inputs)


def prepare_campaign_models(
    inputs: dict, *, repair_epochs: int = 40, rng_seed: int = 20260707,
    cache_dir: str | Path | None = None,
) -> dict:
    """Return complete evolution inputs; failures leave the caller unchanged.

    Use the already loaded corpus and the original trainer/cache contract.
    Publishing both models together permits safe retry after a failed load.
    No campaign state, covenant, scientific parameter or saved result changes.
    """
    if "generation_model" in inputs and "repair_model" in inputs:
        return inputs
    from mecha_game.execution import ordered_json_bytes, runtime_identity, sha256
    import base64

    seed_grids = inputs["seed_grids"]
    training_grids = copy.deepcopy(seed_grids[:REPAIR_TRAINING_COUNT])
    generation_model = train_generation_model(seed_grids)
    options = dict(dropout_rates=[0.1, 0.2, 0.3, 0.4], damage_instances=1,
        epochs=repair_epochs, learning_rate=1.5, live_class_weight=3.0,
        rng_seed=rng_seed, vocabulary='legacy')
    source_ids = [dict(source_position=row.get('source_position'),
        raw_sha256=sha256(base64.b64decode(row['data_base64'], validate=True)))
        for row in inputs.get('input_sources', []) if row.get('role') == 'seed_corpus'
        and type(row.get('source_position')) is int and row['source_position'] < len(training_grids)
        and 'data_base64' in row]
    identity = runtime_identity()
    material = dict(contract='mechagotchi_repair_training_v2',
        ordered_training_sha256=sha256(ordered_json_bytes(training_grids)),
        source_identities=source_ids, trainer_options=options, runtime=identity)
    key = sha256(ordered_json_bytes(material))
    repair_model = None
    cache_path = None
    if cache_dir is not None:
        if not identity['available']:
            raise ValueError('Repair cache implementation identity unavailable; existing cache preserved.')
        cache_path = Path(cache_dir) / f"repair_model_v2_{key}.json"
        if cache_path.exists():
            try:
                envelope = json.loads(cache_path.read_bytes())
                raw_model = base64.b64decode(envelope['model_data_base64'], validate=True)
                if (envelope['format'] != 'mechagotchi_repair_cache_v2' or envelope['key'] != key
                        or envelope['key_material'] != material or sha256(raw_model) != envelope['model_sha256']):
                    raise ValueError('cache identity or model digest mismatch')
                repair_model = json.loads(raw_model)
                if not isinstance(repair_model, dict):
                    raise ValueError('cached repair model is not an object')
            except (ValueError, KeyError, TypeError, UnicodeError) as error:
                raise ValueError(f'Invalid repair cache {cache_path.name}: {error}; existing bytes preserved.') from error
    if repair_model is None:
        repair_model = train_repair_model(training_grids, **options)
        if cache_path is not None:
            raw_model = ordered_json_bytes(repair_model)
            envelope = dict(format='mechagotchi_repair_cache_v2', key=key, key_material=material,
                model_sha256=sha256(raw_model), model_data_base64=base64.b64encode(raw_model).decode('ascii'))
            raw_cache = ordered_json_bytes(envelope) + b'\n'
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation prevents an intervening writer from being lost.
            try:
                with cache_path.open('xb') as handle:
                    handle.write(raw_cache)
            except FileExistsError:
                if cache_path.read_bytes() != raw_cache:
                    raise ValueError('Conflicting repair cache appeared; both model and existing bytes preserved.') from None
    training = dict(training_contract=material['contract'], trainer_options=options,
        ordered_training_sha256=material['ordered_training_sha256'], training_grids=training_grids,
        source_identities=source_ids)
    return {**inputs, "generation_model": generation_model, "repair_model": repair_model,
            "repair_training": training}



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
        population_policy: str = 'legacy_archive',
        body_response: str = 'legacy',
    ) -> None:
        if population_policy not in ('legacy_archive', 'generation_survivors_v1'):
            raise ValueError('Unsupported campaign population policy.')
        from mecha_game.body_response import validate_body_response
        self._body_response = validate_body_response(body_response)
        self._population_policy = population_policy
        self._population_continuation = dict(founder_start_mode='bootstrap', era_index=None, ordered_breeders_sha256=None)
        self.resume_breeders: list[dict] | None = None
        self.inputs = inputs
        self.era_config = {**ERA_CONFIG, **(era_config or {})}
        # The BASE covenant and base parameters the budget computes
        # from (spends never compound against themselves â€” F7).
        self.base_profile = json.loads(
            json.dumps(inputs["slip_profile"])
        )
        self.base_covenant_source = None
        from mecha_game.execution import validate_source_records
        import base64
        for source in inputs.get('input_sources', []):
            if source.get('role') in ('covenant', 'base_covenant') and 'data_base64' in source:
                validate_source_records([source])
                if canonical_json(json.loads(base64.b64decode(source['data_base64'], validate=True))) == canonical_json(self.base_profile):
                    self.base_covenant_source = {**copy.deepcopy(source), 'role': 'base_covenant'}
                    break
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
        self.resume_founder_sources: list[dict] | None = None
        self.last_original_recording = None
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
    def body_response(self) -> str:
        return self._body_response

    @property
    def population_policy(self) -> str:
        return self._population_policy

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
        """The spendable covenant budget (F7 â€” DR 0021's table)."""
        from mecha_game.covenant import covenant_budget

        return covenant_budget(
            self.base_profile, self.base_parameters, self.unlock_state()
        )

    def species_memory(self) -> dict:
        """What the Keeper reviews: the last era's repertoire and the
        campaign's earned facts â€” report fields verbatim."""
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
        """The last era's best elite â€” the adoption handoff (the
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
        self, weather: str, *, released_grids: list[dict] | None = None,
        progress_callback=None, record_original=False, released_sources=None,
        care_selection_policy='off', care_evaluator='archive_morphology_probe_v1',
        survival_regime='sheltered', cubff_density_pressure=False,
    ) -> dict:
        """Advance the living bloodline by exactly one era (the lab's
        `advance_campaign` semantics: founders = the previous era's
        elites; unlock facts accumulate; extinction ends the chain).

        ``released_grids`` (the lab's E5 seam â€” DR 0021's Contribute):
        the Keeper's released creatures LEAD the founder pool, ahead
        of the prior era's elites (the T1/DR 0016 founders-lead rule);
        admission or verbatim rejection is the engine's own judgment
        inside ``evolve``. ``None`` keeps every prior flow identical."""
        if self.campaign["status"] != "active":
            raise ValueError(
                f"campaign {self.campaign['campaign_id']!r} is "
                f"{self.campaign['status']} â€” an ended bloodline cannot "
                "run another era (successor() starts the next)"
            )
        era_index = self.era_offset + len(self.eras)
        from mecha_game.execution import (validate_population_inputs, POPULATION_INPUT_FORMAT,
            population_arguments, population_ended, breeder_sources, validate_breeder_continuation)
        survivor = self.population_policy == 'generation_survivors_v1'
        start = ('bootstrap' if era_index == 0 else 'continue') if survivor else None
        population_inputs = dict(population_policy=self.population_policy, founder_start_mode=start,
            survival_regime=survival_regime, cubff_density_pressure=cubff_density_pressure)
        validate_population_inputs(dict(format=POPULATION_INPUT_FORMAT, **population_inputs))
        if cubff_density_pressure and not self.budget().get('cubff_density_pressure_allowed', False):
            raise ValueError('Density pressure has not been earned for this campaign.')
        previous_breeders = None
        if survivor:
            previous_breeders = (self.eras[-1]['report']['living_population']['final_breeders'] if self.eras
                                 else self.resume_breeders if era_index else [])
            if not isinstance(previous_breeders, list):
                raise ValueError('Living continuation evidence is unavailable; historical elites cannot refill it.')
            chain = [copy.deepcopy(row['grid']) for row in previous_breeders]
        elif self.eras:
            chain = [
                elite["grid"] for elite in self.eras[-1]["elites"]
            ]
        elif self.resume_founders is not None:
            # The resumed chain continues from the ledger's own pool.
            chain = self.resume_founders
        else:
            chain = []
        from mecha_game.execution import (capture_execution, decode_execution_inputs,
            finalize_execution, validate_source_records, elite_care_sources, care_arguments, body_arguments)
        releases = list(released_grids or [])
        validate_source_records(released_sources if released_sources is not None else [None] * len(releases), count=len(releases))
        founder_pool = releases + chain
        founder_grids = founder_pool if survivor else founder_pool or None
        sources = [copy.deepcopy(row) for row in self.inputs.get('input_sources', [])
                   if row.get('role') not in ('covenant', 'base_covenant')]
        base_source = copy.deepcopy(self.base_covenant_source) if self.base_covenant_source is not None else dict(
            source_kind='in_memory', source_position=None)
        sources.append({**base_source, 'role': 'base_covenant',
                        'matches_effective_covenant': canonical_json(self.base_profile) == canonical_json(self.campaign['slip_profile'])})
        for role in ('seed_corpus', 'readability_model', 'generation_model', 'repair_model'):
            if not any(row.get('role') == role for row in sources):
                sources.append(dict(role=role, source_kind='in_memory', source_position=None))
        if survivor:
            chain_sources = breeder_sources({'living_population': {'final_breeders': previous_breeders}},
                self.campaign['campaign_id'], era_index-1) if era_index else []
        elif self.eras:
            chain_sources = elite_care_sources(self.eras[-1]['report'], self.eras[-1]['elites'],
                self.campaign['campaign_id'], self.eras[-1]['era_index'])
        elif self.resume_founder_sources is not None:
            chain_sources = self.resume_founder_sources
        else:
            chain_sources = [None] * len(chain)
        founder_sources = list(released_sources or [None] * len(releases)) + list(chain_sources)
        if survivor:
            validate_breeder_continuation(founder_grids, founder_sources, previous_breeders,
                self.campaign['campaign_id'], era_index, start)
        for ordinal, source in enumerate(founder_sources):
            sources.append({**copy.deepcopy(source or dict(source_kind='in_memory', source_position=None)),
                            'role': 'founder', 'founder_ordinal': ordinal})
        contexts = [copy.deepcopy(row.get('care_context')) for row in sources if row.get('role') == 'founder']
        care_inputs = dict(founder_care_contexts=contexts, care_selection_policy=care_selection_policy,
            care_evaluator=care_evaluator) if any(context is not None for context in contexts) or care_selection_policy != 'off' else {}
        if care_selection_policy not in ('off', 'observed_care_selection_v1', 'observed_care_selection_v2') or care_evaluator not in ('pristine', 'archive_morphology_probe_v1'):
            raise ValueError('Unsupported care selection policy or evaluator.')
        weather_source = build_weather_source(weather, source_records=sources)
        if cubff_density_pressure and not weather_source:
            raise ValueError('Density pressure needs an actual weather source.')
        if weather not in ('real', 'callback'):
            sources.append(dict(role='weather', source_kind='generated' if weather_source is not None else 'none', source_position=None))
        snapshot = capture_execution(self.campaign['campaign_id'], era_index, dict(
            seed_grids=self.inputs['seed_grids'], slip_profile=self.campaign['slip_profile'],
            generation_model=self.inputs['generation_model'], repair_model=self.inputs['repair_model'],
            legibility_model=self.inputs['legibility_model'],
            readability_selection={**self.inputs['legibility_model'], 'blend': legibility_blend_for(self.unlock_state())},
            repair_training=self.inputs.get('repair_training'), founder_grids=founder_grids,
            cubff_pressure_source=weather_source, rng_seed=self.campaign['base_seed'] + era_index * ERA_SEED_STRIDE,
            effective_config=self.era_config, **care_inputs, **population_inputs,
            **({'body_response': self.body_response} if self.body_response != 'legacy' else {})), sources)
        captured = decode_execution_inputs(snapshot)
        founder_grids = captured['founder_grids']
        submitted_snapshot = copy.deepcopy(founder_grids or [])
        legibility_model = captured['legibility_model']
        admissions = []

        def scorer(grid: dict) -> float:
            return learned_readability_score(grid, legibility_model)

        recorder = None
        self.last_original_recording = None
        if record_original:
            from mecha_game.original_recording import BestEvaluationRecording
            recorder = BestEvaluationRecording(self.campaign['campaign_id'], era_index,
                self.campaign['base_seed'] + era_index * ERA_SEED_STRIDE,
                captured['slip_profile'], weather, captured['effective_config'])
        archive, report = evolve(
            captured['seed_grids'], captured['slip_profile'], captured['generation_model'], captured['repair_model'],
            readability_scorer=scorer, rng_seed=captured['rng_seed'], founder_grids=founder_grids,
            cubff_pressure_source=captured['cubff_pressure_source'], readability_selection=captured['readability_selection'],
            admission_callback=admissions.append, **captured['effective_config'], **care_arguments(snapshot),
            **population_arguments(snapshot), **body_arguments(snapshot),
            **({"progress_callback": progress_callback} if progress_callback is not None else {}),
            **({"recording_callback": recorder.capture} if recorder is not None and recorder.enabled else {}),
        )
        # The archive's elites in niche-key order â€” the same
        # deterministic ordering evolve uses for elite parents
        # (the lab's `_era_elites`, records spread VERBATIM).
        elites = [
            {"niche_key": niche, **archive["elites"][niche]}
            for niche in sorted(archive["elites"])
        ]
        went_extinct = population_ended(report, elites, self.population_policy)
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
            "founder_records": _founder_records(submitted_snapshot, len(released_grids or []), report,
                population_policy=self.population_policy),
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
        era_record['execution'] = finalize_execution(snapshot, admissions, report, elites)
        if recorder is not None:
            self.last_original_recording = recorder.finish(era_record)
        self.campaign["eras"].append(era_record)
        if survivor:
            self._population_continuation = dict(founder_start_mode='continue', era_index=era_index,
                ordered_breeders_sha256=era_record['execution']['manifest']['ordered_breeders_sha256'])
        self.campaign["unlocks"].extend(
            evaluate_unlocks(era_record, self.campaign["unlocks"])
        )
        if went_extinct:
            self.campaign["status"] = "extinct"
        return era_record

    def record_review_replay(self, era_index: int = -1) -> dict:
        """Legacy explicit post-era recorder, retained for compatibility.

        This starts a new life at the era seed. The playable E path instead
        captures the actual evaluation through recording_callback (DR0074).
        Never use this method to backfill missing original footage.
        """
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
            **({"body_response": self.body_response} if self.body_response != "legacy" else {}),
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
                "the bloodline lives â€” succession is extinction's door"
            )
        child = KeeperCampaign(
            {**self.inputs, "slip_profile": json.loads(json.dumps(self.base_profile))},
            # Roguelite: the successor carries ONLY the unlocks â€” the
            # spent covenant and caps reset to base; the fresh
            # bloodline spends again from its inherited budget.
            era_config={**self.era_config, **self.base_parameters},
            inherited_unlocks=self.unlock_state(),
            population_policy=self.population_policy, body_response=self.body_response,
            **plan,
        )
        child.base_covenant_source = copy.deepcopy(self.base_covenant_source)
        return child

    # -- replay persistence (F17 â€” DR 0022's pointer rule) -----------------

    def save_review_replay(
        self,
        replay: dict,
        keeper_dir: str | Path,
        ledger_path: str | Path,
    ) -> Path:
        """Persist complete footage once; equal retries retain historical bytes.

        A recomputed preview cannot replace an era's existing recording. Legacy
        Windows CRLF artifacts retain their bytes and normalized-text ledger hash.
        """
        import hashlib
        import os
        import tempfile

        from mecha_engine.storage import load_replay_rows, open_ledger, record_replay

        keeper_dir = Path(keeper_dir)
        era_index = (
            replay["parameters"]["rng_seed"] - self.campaign["base_seed"]
        ) // ERA_SEED_STRIDE
        directory = (keeper_dir / "replays").resolve()
        path = directory / f"{self.campaign['campaign_id']}_era{era_index}.json"
        if not path.resolve().is_relative_to(directory):
            raise ValueError("Replay recording name leaves its recordings directory.")
        payload = json.dumps(replay, indent=2) + "\n"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        conn = open_ledger(Path(ledger_path))
        try:
            # Serialize competing writers while checking both halves of the
            # artifact/pointer pair. A failed pointer write leaves complete bytes
            # that the identical retry can safely finish.
            conn.execute("BEGIN IMMEDIATE")
            rows = [row for row in load_replay_rows(conn, self.campaign["campaign_id"])
                    if row["era_index"] == era_index]
            if rows and (len(rows) != 1 or rows[0]["artifact_path"] != path.name
                         or rows[0]["artifact_sha256"] != digest):
                raise ValueError("Conflicting replay recording pointer preserved.")
            if path.exists() and path.read_text(encoding="utf-8") != payload:
                raise ValueError("Conflicting replay recording file preserved.")
            if not path.exists():
                directory.mkdir(parents=True, exist_ok=True)
                temporary = None
                try:
                    with tempfile.NamedTemporaryFile(dir=directory, prefix=".replay-",
                                                     suffix=".tmp", delete=False) as stream:
                        temporary = Path(stream.name)
                        stream.write(payload.encode("utf-8"))
                        stream.flush()
                        os.fsync(stream.fileno())
                    try:
                        os.link(temporary, path)
                    except FileExistsError:
                        if path.read_text(encoding="utf-8") != payload:
                            raise ValueError("Conflicting replay recording file preserved.")
                finally:
                    if temporary is not None:
                        temporary.unlink(missing_ok=True)
            if not rows:
                record_replay(conn, self.campaign["campaign_id"], era_index, path.name, digest)
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
                f"recorded sha256 â€” refusing a tampered recording"
            )
        return json.loads(payload)

    # -- campaign state resume (F17) ----------------------------------------

    STATE_FORMAT = "keeper_campaign_state_v1"
    POPULATION_STATE_FORMAT = "keeper_campaign_state_v2"

    @classmethod
    def validate_state_payload(cls, payload: object) -> None:
        """Validate saved facts without defaults, migration or reconstruction."""
        import math
        from mecha_engine.slip import validate_slip

        if not isinstance(payload, dict) or payload.get("state_format") not in (cls.STATE_FORMAT, cls.POPULATION_STATE_FORMAT):
            raise ValueError("Not a supported keeper campaign state.")
        from mecha_game.body_response import saved_body_response
        saved_body_response(payload)
        required = {"campaign_id": str, "keeper_label": str, "created_date": str,
                    "status": str, "base_seed": int, "era_count": int,
                    "unlocks": list, "inherited_unlocks": list, "base_profile": dict,
                    "slip_profile": dict, "era_config": dict}
        for name, expected in required.items():
            if type(payload.get(name)) is not expected:
                raise ValueError(f"Invalid campaign state field: {name}.")
        for name in ("campaign_id", "keeper_label", "created_date"):
            if not payload[name].strip():
                raise ValueError(f"Empty campaign state field: {name}.")
        if "predecessor_campaign_id" not in payload:
            raise ValueError("Missing campaign predecessor identity.")
        predecessor = payload["predecessor_campaign_id"]
        if predecessor is not None and (not isinstance(predecessor, str) or not predecessor or
                                        predecessor == payload["campaign_id"]):
            raise ValueError("Invalid campaign predecessor identity.")
        if payload["status"] not in ("active", "extinct", "retired") or payload["era_count"] < 0:
            raise ValueError("Invalid campaign status or era count.")
        if payload['state_format'] == cls.POPULATION_STATE_FORMAT:
            if payload.get('population_policy') != 'generation_survivors_v1':
                raise ValueError('Unsupported saved population policy.')
            continuation = payload.get('population_continuation')
            if not isinstance(continuation, dict) or set(continuation) != {'founder_start_mode', 'era_index', 'ordered_breeders_sha256'}:
                raise ValueError('Saved campaign is missing its explicit population continuation.')
            if payload['era_count'] == 0:
                if continuation != dict(founder_start_mode='bootstrap', era_index=None, ordered_breeders_sha256=None):
                    raise ValueError('New population campaign must explicitly bootstrap.')
            else:
                digest = continuation['ordered_breeders_sha256']
                if (continuation['founder_start_mode'] != 'continue' or type(continuation['era_index']) is not int
                        or continuation['era_index'] != payload['era_count']-1 or not isinstance(digest, str)
                        or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest)):
                    raise ValueError('Saved living continuation requires its exact prior breeder identity.')
        elif 'population_policy' in payload or 'population_continuation' in payload:
            raise ValueError('Population state requires its versioned format.')
        config = payload["era_config"]
        for name in ("generations", "population", "damage_cycles", "ticks"):
            if type(config.get(name)) is not int or config[name] < 1:
                raise ValueError(f"Invalid campaign configuration: {name}.")
        rate = config.get("dropout_rate")
        if type(rate) not in (int, float) or not math.isfinite(rate) or not 0 <= rate <= 1:
            raise ValueError("Invalid campaign dropout rate.")
        if "base_parameters" in payload:
            base = payload["base_parameters"]
            if not isinstance(base, dict) or any(type(base.get(name)) is not int or base[name] < 1
                                                for name in ("population", "generations")):
                raise ValueError("Invalid campaign base parameters.")
        for name in ("base_profile", "slip_profile"):
            try:
                verdict = validate_slip(payload[name])
            except (TypeError, KeyError, AttributeError) as error:
                raise ValueError(f"Invalid campaign covenant: {name}.") from error
            if not verdict.ok:
                raise ValueError(f"Invalid campaign covenant {name}: " + "; ".join(verdict.errors))
        if payload.get('base_covenant_source') is not None:
            from mecha_game.execution import validate_source_records
            import base64
            source = payload['base_covenant_source']
            validate_source_records([source])
            if source.get('role') != 'base_covenant' or 'data_base64' not in source:
                raise ValueError('Invalid saved base covenant source.')
            if canonical_json(json.loads(base64.b64decode(source['data_base64'], validate=True))) != canonical_json(payload['base_profile']):
                raise ValueError('Saved base covenant source disagrees with its profile.')
        for name in ("unlocks", "inherited_unlocks"):
            seen = set()
            for fact in payload[name]:
                if not isinstance(fact, dict):
                    raise ValueError(f"Invalid campaign {name} fact.")
                axis, tier = fact.get("axis"), fact.get("tier")
                if (not isinstance(axis, str) or axis not in UNLOCK_THRESHOLDS or
                    type(tier) is not int or not 1 <= tier <= len(UNLOCK_THRESHOLDS[axis]["tiers"]) or
                    type(fact.get("earned_era_index")) is not int or fact["earned_era_index"] < 0 or
                    not isinstance(fact.get("metric_path"), str) or not fact["metric_path"]):
                    raise ValueError(f"Invalid campaign {name} fact.")
                for key in ("metric_value", "threshold"):
                    value = fact.get(key)
                    if type(value) not in (int, float) or not math.isfinite(value):
                        raise ValueError(f"Invalid campaign {name} {key}.")
                if name == "unlocks" and ((axis, tier) in seen or fact["earned_era_index"] >= payload["era_count"]):
                    raise ValueError("Duplicate or misplaced campaign unlock fact.")
                seen.add((axis, tier))

    def state_payload(self) -> dict:
        """The exact active state; shared by normal saves and completed-era recovery."""
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
            "base_covenant_source": copy.deepcopy(self.base_covenant_source),
            "slip_profile": self.campaign["slip_profile"],
            "era_config": self.era_config,
            "base_parameters": self.base_parameters,
        }
        if self.body_response != 'legacy': payload['body_response'] = self.body_response
        if self.population_policy == 'generation_survivors_v1':
            payload.update(state_format=self.POPULATION_STATE_FORMAT, population_policy=self.population_policy,
                           population_continuation=copy.deepcopy(self._population_continuation))
        return payload

    @campaign_writer
    def save_state(self, path: str | Path) -> Path:
        """Atomically checkpoint the active covenant and era position."""
        from mecha_game.session import _document_bytes, _write_bytes_atomic
        path = Path(path)
        data = _document_bytes(self.state_payload())
        if path.exists():
            old = path.read_bytes()
            if old == data:
                return path
            _write_bytes_atomic(path.with_suffix('.bak.json'), old)
        _write_bytes_atomic(path, data)
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
        from mecha_game.campaign_recovery import require_no_restore, validate_ledger_state

        require_no_restore(state_path)
        try:
            payload = json.loads(Path(state_path).read_text(encoding="utf-8"))
        except (ValueError, UnicodeError) as error:
            raise ValueError("Campaign state is unreadable; existing files preserved.") from error
        cls.validate_state_payload(payload)
        history = validate_ledger_state(payload, ledger_path)
        campaign = cls(
            inputs,
            campaign_id=payload["campaign_id"],
            keeper_label=payload["keeper_label"],
            created_date=payload["created_date"],
            predecessor_campaign_id=payload["predecessor_campaign_id"],
            base_seed=payload["base_seed"],
            era_config=payload["era_config"],
            inherited_unlocks=payload["inherited_unlocks"],
            population_policy=payload.get('population_policy', 'legacy_archive'),
            body_response=payload.get('body_response', 'legacy'),
        )
        campaign.campaign["status"] = payload["status"]
        campaign.campaign["unlocks"] = payload["unlocks"]
        campaign.base_profile = payload["base_profile"]
        # Missing old source evidence stays missing; current defaults are not history.
        campaign.base_covenant_source = copy.deepcopy(payload.get('base_covenant_source'))
        # This optional field retains the established interpretation of legacy saves.
        campaign.base_parameters = payload.get("base_parameters", campaign.base_parameters)
        campaign.campaign["slip_profile"] = payload["slip_profile"]
        campaign.era_offset = payload["era_count"]
        if campaign.population_policy == 'generation_survivors_v1':
            campaign._population_continuation = copy.deepcopy(payload['population_continuation'])
            campaign.resume_breeders = copy.deepcopy(history['resume_breeders'])
        if campaign.era_offset:
            campaign.resume_founders = history["resume_founders"]
            campaign.resume_founder_sources = history['resume_founder_sources']
        return campaign

    # -- persistence (DR 0022) --------------------------------------------

    @campaign_writer
    def save(self, ledger_path: str | Path) -> Path:
        """Persist the campaign into the storage module's ledger â€”
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
                    from mecha_engine.storage import load_era_execution
                    if canonical_json(load_era_execution(conn, self.campaign['campaign_id'], era['era_index'])) != canonical_json(era.get('execution')):
                        raise ValueError('Conflicting immutable execution already occupies this era; existing evidence preserved.')
                    continue
                era_profile = self.campaign['slip_profile']
                if era.get('execution') is not None:
                    from mecha_game.execution import blob_json
                    bundle = era['execution']
                    era_profile = blob_json(bundle, bundle['manifest']['inputs']['covenant_sha256'])
                record_era(
                    conn,
                    self.campaign["campaign_id"],
                    # The ledger's era shape wants the extinction flag
                    # top-level (DR 0022 schema); the record itself
                    # stays verbatim.
                    {**era, "went_extinct": era["derived"]["went_extinct"]},
                    era_profile,
                    founders=era.get("founder_records"),
                    execution=era.get("execution"),
                    unlocks=[
                        fact
                        for fact in self.unlocks
                        if fact["earned_era_index"] == era["era_index"]
                    ],
                )
        finally:
            conn.close()
        return ledger_path
