"""The campaign ledger's storage surface — verbatim from the lab.

Behavior source: labs/game_loop/campaign_store.py (C2, decision record
0022). Every function below is the lab's, unchanged — the lab-side
parity pin (labs/game_loop/test_package_storage_parity.py) compares the
two stores row-for-row over real engine output, so drift cannot be
silent.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import math
import sqlite3
from pathlib import Path

SCHEMA_VERSION = 2
SUPPORTED_READ_SCHEMA_VERSIONS = (1, 2)
INTERIM_SCHEMA = "dr0022_v1_json_interim"

SCHEMA = """
CREATE TABLE campaigns (
  campaign_id               TEXT PRIMARY KEY,
  keeper_label              TEXT NOT NULL,
  created_date              TEXT NOT NULL,
  predecessor_campaign_id   TEXT REFERENCES campaigns(campaign_id),
  status                    TEXT NOT NULL
    CHECK (status IN ('active', 'extinct', 'retired'))
);

CREATE TABLE slip_profiles (
  profile_id    INTEGER PRIMARY KEY,
  campaign_id   TEXT NOT NULL REFERENCES campaigns(campaign_id),
  era_index     INTEGER NOT NULL,
  slip_version  TEXT NOT NULL,
  profile_json  TEXT NOT NULL,
  UNIQUE (campaign_id, era_index)
);

CREATE TABLE eras (
  campaign_id             TEXT NOT NULL REFERENCES campaigns(campaign_id),
  era_index               INTEGER NOT NULL,
  rng_seed                INTEGER NOT NULL,
  slip_profile_id         INTEGER NOT NULL REFERENCES slip_profiles(profile_id),
  weather_json            TEXT,
  report_json             TEXT NOT NULL,
  decision_status         TEXT NOT NULL,
  filled_niches           INTEGER NOT NULL,
  coverage                REAL NOT NULL,
  qd_score                REAL NOT NULL,
  max_lineage_generation  INTEGER NOT NULL,
  went_extinct            INTEGER NOT NULL,
  PRIMARY KEY (campaign_id, era_index)
);

CREATE TABLE elites (
  campaign_id  TEXT NOT NULL,
  era_index    INTEGER NOT NULL,
  niche_key    TEXT NOT NULL,
  grid_id      TEXT NOT NULL,
  fitness      REAL NOT NULL,
  elite_json   TEXT NOT NULL,
  PRIMARY KEY (campaign_id, era_index, niche_key),
  FOREIGN KEY (campaign_id, era_index) REFERENCES eras
);

CREATE TABLE founders (
  campaign_id           TEXT NOT NULL,
  era_index             INTEGER NOT NULL,
  grid_id               TEXT NOT NULL,
  source                TEXT NOT NULL
    CHECK (source IN ('workshop_release', 'era_elite')),
  admitted              INTEGER NOT NULL,
  rejection_errors_json TEXT,
  grid_json             TEXT,
  PRIMARY KEY (campaign_id, era_index, grid_id),
  FOREIGN KEY (campaign_id, era_index) REFERENCES eras
);

CREATE TABLE unlocks (
  campaign_id      TEXT NOT NULL REFERENCES campaigns(campaign_id),
  axis             TEXT NOT NULL
    CHECK (axis IN ('niche_mastery', 'bloodline_depth',
                    'quality_diversity', 'storm_record', 'legibility')),
  tier             INTEGER NOT NULL,
  earned_era_index INTEGER NOT NULL,
  metric_path      TEXT NOT NULL,
  metric_value     TEXT NOT NULL,
  threshold        TEXT NOT NULL,
  PRIMARY KEY (campaign_id, axis, tier)
);

CREATE TABLE replays (
  campaign_id     TEXT NOT NULL,
  era_index       INTEGER NOT NULL,
  artifact_path   TEXT NOT NULL,
  artifact_sha256 TEXT NOT NULL,
  PRIMARY KEY (campaign_id, era_index, artifact_path),
  FOREIGN KEY (campaign_id, era_index) REFERENCES eras
);
"""


SCHEMA_V2 = """
CREATE TABLE execution_blobs (
  sha256 TEXT PRIMARY KEY,
  media_type TEXT NOT NULL,
  payload BLOB NOT NULL
);
CREATE TABLE era_executions (
  campaign_id TEXT NOT NULL,
  era_index INTEGER NOT NULL,
  manifest_json TEXT NOT NULL,
  manifest_sha256 TEXT NOT NULL,
  PRIMARY KEY (campaign_id, era_index),
  FOREIGN KEY (campaign_id, era_index) REFERENCES eras
);
CREATE TABLE founder_occurrences (
  campaign_id TEXT NOT NULL,
  era_index INTEGER NOT NULL,
  ordinal INTEGER NOT NULL,
  occurrence_json TEXT NOT NULL,
  PRIMARY KEY (campaign_id, era_index, ordinal),
  FOREIGN KEY (campaign_id, era_index) REFERENCES eras
);
"""

EXECUTION_FORMAT = "mechagotchi_era_execution_v1"
EXECUTION_FORMAT_V2 = "mechagotchi_era_execution_v2"
POPULATION_POLICY = "generation_survivors_v1"
_REQUIRED_INPUT_DIGESTS = (
    "seed_corpus_sha256", "covenant_sha256", "generation_model_sha256",
    "repair_model_sha256", "readability_model_sha256",
    "readability_selection_sha256",
)


def _execution_error(reason: str) -> ValueError:
    return ValueError(f"invalid era execution: {reason}")


def _require_digest(value, field: str) -> str:
    if (not isinstance(value, str) or len(value) != 64
            or any(char not in "0123456789abcdef" for char in value)):
        raise _execution_error(f"{field} must be a SHA256 digest")
    return value


def _require_text(value, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise _execution_error(f"{field} must be nonempty text")


def _require_position(value, field: str, *, nullable=False) -> None:
    if nullable and value is None:
        return
    if type(value) is not int or value < 0:
        raise _execution_error(f"{field} must be a nonnegative integer")


def _json_value(value) -> None:
    """Reject values JSON would coerce or encode outside its data model."""
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise _execution_error("JSON object keys must be strings")
            _json_value(item)
    elif isinstance(value, list):
        for item in value:
            _json_value(item)
    elif value is not None and type(value) not in (str, bool, int, float):
        raise _execution_error("bundle must contain only JSON values")
    elif isinstance(value, float) and not math.isfinite(value):
        raise _execution_error("JSON numbers must be finite")


def _decode_json(data: bytes):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise _execution_error("duplicate JSON object key")
            result[key] = value
        return result

    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=pairs)
        _json_value(value)
        return value
    except (UnicodeError, ValueError, TypeError) as error:
        raise _execution_error(f"unreadable JSON bytes: {error}") from error


def _manifest_references(manifest: dict) -> set[str]:
    """The manifest is the complete index of this era's retained blobs."""
    inputs = manifest["inputs"]
    refs = {manifest["calibration_sha256"], *inputs["founder_sha256"]}
    for field in ("ordered_elites_sha256", "ordered_breeders_sha256"):
        if field in manifest:
            refs.add(manifest[field])
    refs.update(value for key, value in inputs.items()
                if key.endswith("_sha256") and key != "founder_sha256"
                and value is not None)
    refs.update(source["raw_sha256"] for source in manifest["sources"]
                if "raw_sha256" in source)
    return refs


def _validate_care_context(context: dict) -> None:
    """Passive factual-schema check; no runtime imports, replay or inferred care."""
    keys = {"format", "keeper_id", "life_id", "grid_id", "grid_sha256", "care_summary",
            "events", "events_omitted", "last_age_ticks", "last_session_tick", "outcome"}
    if isinstance(context, dict) and "body_response" in context:
        keys.add("body_response")
        if context["body_response"] != "workload-v1":
            raise _execution_error("unsupported care body response")
    if not isinstance(context, dict) or set(context) != keys or context["format"] != "keeper_care_context_v1":
        raise _execution_error("unsupported care context schema")
    for field in ("keeper_id", "life_id", "grid_id"):
        _require_text(context[field], "care." + field)
    prefix = context["keeper_id"] + ":life-"
    if not context["life_id"].startswith(prefix) or not context["life_id"][len(prefix):].strip():
        raise _execution_error("care life does not belong to Keeper")
    _require_digest(context["grid_sha256"], "care.grid_sha256")
    for field in ("events_omitted", "last_age_ticks", "last_session_tick"):
        _require_position(context[field], "care." + field)
    if context["last_session_tick"] < context["last_age_ticks"]:
        raise _execution_error("care session clock precedes life clock")
    if context["outcome"] not in ("alive", "dead", "replaced_alive", "unknown"):
        raise _execution_error("unsupported care outcome")
    summary = context["care_summary"]
    if not isinstance(summary, dict) or set(summary) != {
            "history", "from_age_ticks", "ticks_observed", "keeper_actions", "companion_actions", "beg_requests"}:
        raise _execution_error("unsupported care summary schema")
    for field in ("from_age_ticks", "ticks_observed", "beg_requests"):
        _require_position(summary[field], "care.summary." + field)
    if (summary["history"] not in ("complete", "partial", "unavailable")
            or summary["from_age_ticks"] + summary["ticks_observed"] != context["last_age_ticks"]
            or summary["beg_requests"] > summary["ticks_observed"]
            or summary["history"] == "complete" and summary["from_age_ticks"] != 0
            or summary["history"] == "unavailable" and summary["ticks_observed"] != 0):
        raise _execution_error("care summary observation boundary")
    actions = ("feed", "play", "sleep", "idle", "mutate", "clean")
    total = 0
    for actor in ("keeper", "companion"):
        counts = summary[actor + "_actions"]
        if not isinstance(counts, dict):
            raise _execution_error("care action counts must be an object")
        for action, count in counts.items():
            if action not in actions:
                raise _execution_error("unsupported care action")
            _require_position(count, "care.action_count")
            if count == 0:
                raise _execution_error("care action totals contain only observed actions")
            if actor == "companion" and action in ("feed", "clean") and count:
                raise _execution_error("companion cannot execute keeper care")
        total += sum(counts.values())
    events = context["events"]
    if (not isinstance(events, list) or len(events) > 100
            or len(events) + context["events_omitted"] != summary["ticks_observed"]
            or total != summary["ticks_observed"]):
        raise _execution_error("care retained/cumulative event count differs")
    seen = {"keeper": {}, "companion": {}}
    begs = 0
    for index, event in enumerate(events):
        if not isinstance(event, dict) or set(event) != {
                "tick", "session_tick", "actor", "action", "begging", "alive", "death_cause"}:
            raise _execution_error("unsupported care event schema")
        for field in ("tick", "session_tick"):
            _require_position(event[field], "care.event." + field)
        if (event["tick"] < 1 or event["session_tick"] < event["tick"]
                or event["tick"] != context["last_age_ticks"] - len(events) + index + 1
                or event["session_tick"] != context["last_session_tick"] - len(events) + index + 1):
            raise _execution_error("care event clocks are not a contiguous tail")
        actor, action = event["actor"], event["action"]
        if actor not in seen or action not in actions or actor == "companion" and action in ("feed", "clean"):
            raise _execution_error("unsupported care event actor/action")
        if type(event["alive"]) is not bool or type(event["begging"]) is not bool:
            raise _execution_error("care event booleans required")
        if event["alive"]:
            if event["death_cause"] is not None:
                raise _execution_error("living care event has death cause")
        else:
            _require_text(event["death_cause"], "care.event.death_cause")
            if index != len(events) - 1 or context["outcome"] != "dead":
                raise _execution_error("care event continues after death")
        seen[actor][action] = seen[actor].get(action, 0) + 1
        begs += int(event["begging"])
    if events and (not events[-1]["alive"]) != (context["outcome"] == "dead"):
        raise _execution_error("care outcome differs from final event")
    for actor, counts in seen.items():
        if any(count > summary[actor + "_actions"].get(action, 0) for action, count in counts.items()):
            raise _execution_error("care events exceed cumulative action counts")
    if begs > summary["beg_requests"] or context["events_omitted"] == 0 and begs != summary["beg_requests"]:
        raise _execution_error("care events exceed cumulative begging count")


def _care_digest(value) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _validate_care_origin(origin, context) -> None:
    if not isinstance(origin, dict) or set(origin) != {"founder_submission_index", "context_sha256"}:
        raise _execution_error("care origin needs exact founder occurrence and context digest")
    _require_position(origin["founder_submission_index"], "care origin founder ordinal")
    if origin["context_sha256"] != _care_digest(context):
        raise _execution_error("care origin differs from context")


def _validate_care_inputs(manifest: dict, documents: dict) -> None:
    refs = manifest["inputs"]
    sources, occurrences = manifest["sources"], manifest["founder_occurrences"]
    if "care_inputs_sha256" not in refs:
        if any("care_context" in row or "care_context_origin" in row for row in sources + occurrences):
            raise _execution_error("care provenance has no immutable care inputs")
        return
    payload = documents[refs["care_inputs_sha256"]]
    if (not isinstance(payload, dict) or set(payload) != {"format", "policy", "evaluator", "founder_contexts"}
            or payload["format"] != "keeper_care_inputs_v1"
            or payload["policy"] not in ("off", "observed_care_selection_v1", "observed_care_selection_v2")
            or payload["evaluator"] not in ("pristine", "archive_morphology_probe_v1")):
        raise _execution_error("unsupported immutable care inputs")
    contexts = payload["founder_contexts"]
    if not isinstance(contexts, list) or len(contexts) != len(refs["founder_sha256"]):
        raise _execution_error("ordered care contexts must match founder inputs")
    by_ordinal = {}
    for row in sources:
        if "founder_ordinal" not in row:
            if "care_context" in row or "care_context_origin" in row or row["role"] == "founder":
                raise _execution_error("care founder source needs an ordinal")
            continue
        ordinal = row["founder_ordinal"]
        if row["role"] != "founder" or ordinal in by_ordinal:
            raise _execution_error("care founder source ordinals must be unique")
        by_ordinal[ordinal] = row
    if set(by_ordinal) != set(range(len(contexts))):
        raise _execution_error("care founder sources must cover submitted occurrences")
    for ordinal, context in enumerate(contexts):
        source, occurrence = by_ordinal[ordinal], occurrences[ordinal]
        source_projection = {key: value for key, value in source.items()
                             if key not in ("role", "founder_ordinal", "raw_sha256")}
        if source["source_kind"] == "era_breeder":
            source_projection.pop("grid_sha256", None)
        occurrence_projection = {key: value for key, value in occurrence.items()
                                if key not in ("ordinal", "grid_id", "grid_sha256", "admitted", "rejection_errors")}
        if ("care_context" not in source or "care_context" not in occurrence
                or canonical_json(source_projection) != canonical_json(occurrence_projection)
                or canonical_json(source["care_context"]) != canonical_json(context)):
            raise _execution_error("care input/source/occurrence binding differs")
        if context is None:
            if "care_context_origin" in source:
                raise _execution_error("null care context has an origin")
            continue
        _validate_care_context(context)
        if source["source_kind"] == "keeper_companion":
            genome = documents[refs["founder_sha256"][ordinal]]
            if (context["keeper_id"] != source.get("keeper_id") or context["life_id"] != source.get("life_id")
                    or context["grid_id"] != genome.get("grid_id")
                    or context["grid_sha256"] != _care_digest(genome) or "care_context_origin" in source):
                raise _execution_error("direct Keeper care differs from immutable founder identity")
        elif source["source_kind"] in ("era_elite", "era_breeder"):
            for field in (("campaign_id", "niche_key") if source["source_kind"] == "era_elite" else ("campaign_id",)):
                _require_text(source.get(field), "care ancestor." + field)
            _require_position(source.get("era_index"), "care ancestor.era_index")
            _require_position(source.get("source_position"), "care ancestor.source_position")
            _validate_care_origin(source.get("care_context_origin"), context)
        else:
            raise _execution_error("care context has no supported source provenance")


def _bind_care_report(manifest: dict, decoded: dict, report: dict, elites: list) -> None:
    ref = manifest["inputs"].get("care_inputs_sha256")
    payload = _decode_json(decoded[ref]) if ref is not None else None
    care = report.get("care_selection")
    contexts = payload["founder_contexts"] if payload else []
    if not any(context is not None for context in contexts):
        if care is not None:
            raise _execution_error("care report has no supplied context")
        return
    if not isinstance(care, dict) or any(canonical_json(care.get(key)) != canonical_json(payload[key])
            for key in ("policy", "evaluator", "founder_contexts")):
        raise _execution_error("care report differs from immutable inputs")
    outputs, origins = care.get("elite_contexts"), care.get("elite_origins")
    if not isinstance(outputs, list) or not isinstance(origins, list) or len(outputs) != len(elites) or len(origins) != len(elites):
        raise _execution_error("care output contexts/origins differ from elite slots")
    for context, origin in zip(outputs, origins):
        if context is None:
            if origin is not None:
                raise _execution_error("null elite care context has an origin")
            continue
        _validate_care_context(context)
        _validate_care_origin(origin, context)
        ordinal = origin["founder_submission_index"]
        if (ordinal >= len(contexts) or not manifest["founder_occurrences"][ordinal]["admitted"]
                or canonical_json(context) != canonical_json(contexts[ordinal])):
            raise _execution_error("elite care origin differs from admitted founder occurrence")


def _bind_care_ancestors(conn: sqlite3.Connection, bundle: dict) -> None:
    try:
        _checked_population_ancestors(conn, bundle)
        _checked_care_ancestors(conn, bundle)
    except (KeyError, TypeError, AttributeError, UnicodeError, sqlite3.DatabaseError) as error:
        raise _execution_error(f"unreadable care ancestor: {error}") from error


def _checked_care_ancestors(conn: sqlite3.Connection, bundle: dict) -> None:
    """Bind continued care to the prior recorded elite slot, never grid-ID lookup."""
    manifest = bundle["manifest"]
    for source in manifest["sources"]:
        context = source.get("care_context")
        if context is None or source["source_kind"] != "era_elite":
            continue
        campaign_id, era_index = source["campaign_id"], source["era_index"]
        if campaign_id == manifest["campaign_id"] and era_index >= manifest["era_index"]:
            raise _execution_error("care ancestor is not a prior era")
        prior = conn.execute("SELECT e.report_json, x.manifest_json, x.manifest_sha256 FROM eras e JOIN era_executions x ON x.campaign_id=e.campaign_id AND x.era_index=e.era_index WHERE e.campaign_id=? AND e.era_index=?", (campaign_id, era_index)).fetchone()
        if prior is None or hashlib.sha256(prior[1].encode("utf-8")).hexdigest() != prior[2]:
            raise _execution_error("care ancestor has no verified execution manifest")
        report, prior_manifest = _decode_json(prior[0].encode("utf-8")), _decode_json(prior[1].encode("utf-8"))
        elites = load_era_elites(conn, campaign_id, era_index)
        if (_care_digest(report) != prior_manifest["report_sha256"]
                or _care_digest(elites) != prior_manifest["elites_sha256"]):
            raise _execution_error("care ancestor outputs differ from immutable execution")
        position = source["source_position"]
        care = report.get("care_selection", {})
        contexts, origins = care.get("elite_contexts"), care.get("elite_origins")
        if (not isinstance(contexts, list) or not isinstance(origins, list)
                or len(contexts) != len(elites) or len(origins) != len(elites) or position >= len(elites)):
            raise _execution_error("care ancestor has no matching ordered elite context")
        elite = elites[position]
        ref = manifest["inputs"]["founder_sha256"][source["founder_ordinal"]]
        genome = _decode_json(base64.b64decode(bundle["blobs"][ref]["data_base64"]))
        if (source["niche_key"] != elite["niche_key"] or canonical_json(genome) != canonical_json(elite["grid"])
                or canonical_json(contexts[position]) != canonical_json(context)
                or canonical_json(origins[position]) != canonical_json(source["care_context_origin"])):
            raise _execution_error("care ancestor source differs from recorded elite slot")


def _body_model(manifest, documents):
    ref = manifest["inputs"].get("body_response_inputs_sha256")
    if ref is None:
        return "legacy"
    if documents.get(ref) != {"format": "body_response_inputs_v1", "body_response": "workload-v1"}:
        raise _execution_error("unsupported immutable body response inputs")
    return "workload-v1"


def _validate_body_inputs(manifest, documents):
    model = _body_model(manifest, documents)
    ref = manifest["inputs"].get("care_inputs_sha256")
    if ref is not None:
        for context in documents[ref]["founder_contexts"]:
            if context is not None and context.get("body_response", "legacy") != model:
                raise _execution_error("founder care body response differs from immutable era model")


def _bind_body_report(manifest, decoded, report):
    """Read-only projection validation; never replay or change a recorded life."""
    try:
        _checked_body_report(manifest, decoded, report)
    except (KeyError, TypeError, AttributeError, IndexError, OverflowError) as error:
        raise _execution_error("malformed body response evidence") from error


def _checked_body_report(manifest, decoded, report):
    documents = {key: _decode_json(raw) for key, raw in decoded.items()
                 if key in (manifest["inputs"].get("body_response_inputs_sha256"),
                            manifest["inputs"]["covenant_sha256"])}
    model = _body_model(manifest, documents)
    if (report.get("body_response", "legacy") != model
            or model == "legacy" and "body_response" in report):
        raise _execution_error("body response report differs from immutable inputs")
    covenant = documents[manifest["inputs"]["covenant_sha256"]]
    breeder_ref = manifest.get("ordered_breeders_sha256")
    breeders = _decode_json(decoded[breeder_ref]) if breeder_ref is not None else []
    final_bodies = {(row["generation_index"], row["candidate_index"]): row["grid"] for row in breeders}
    population_ref = manifest["inputs"].get("population_inputs_sha256")
    regime = _decode_json(decoded[population_ref])["survival_regime"] if population_ref is not None else "sheltered"

    def evaluated_body(grid):
        if regime == "stress_probe":
            from mecha_engine.archive import lifecycle_probe_grid
            return lifecycle_probe_grid(grid)
        return grid

    def endpoint(value, grid=None):
        if value is None:
            return
        if not isinstance(value, dict) or value.get("body_response", "legacy") != model:
            raise _execution_error("episode body response differs from immutable model")
        if model == "legacy":
            if any(key in value for key in ("body_response", "body_workload", "evaluated_grid")):
                raise _execution_error("legacy episode carries active body response evidence")
            return
        if grid is None:
            grid = value.get("evaluated_grid")
        elif "evaluated_grid" in value and canonical_json(value["evaluated_grid"]) != canonical_json(grid):
            raise _execution_error("episode evaluated body differs from actual recorded body")
        try:
            # Public pure initialization validates the real body and recomputes
            # the same projection; no action, RNG, replay or storage write runs.
            from mecha_engine.lifecycle import initial_state
            expected = initial_state(grid, covenant, body_response=model)["body_workload"]
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            raise _execution_error("invalid episode body projection source") from error
        if canonical_json(value.get("body_workload")) != canonical_json(expected):
            raise _execution_error("episode body workload differs from actual evaluated body")
        for state in (value.get("initial_state"), value.get("final_state")):
            if state is not None and (state.get("grid_id") != grid["grid_id"] or state.get("body_response") != model
                    or canonical_json(state.get("body_workload")) != canonical_json(expected)):
                raise _execution_error("care state body workload differs from actual evaluated body")
        for tick in value.get("history", []):
            if (tick.get("body_response") != model
                    or tick.get("play_energy_cost") != expected["play_energy_cost"]
                    or tick.get("action") == "play" and tick.get("action_energy_effect") != -expected["play_energy_cost"]):
                raise _execution_error("care tick body response differs from actual evaluated body")
        for row in value.get("trajectory", []):
            state = row.get("decision_state", {})
            if (state.get("grid_id") != grid["grid_id"] or state.get("body_response") != model
                    or canonical_json(state.get("body_workload")) != canonical_json(expected)):
                raise _execution_error("care decision body workload differs from actual evaluated body")

    for generation in report.get("generations", []):
        for candidate_index, creature in enumerate(generation.get("creatures", [])):
            for cycle in creature.get("cycles", []):
                source = (cycle.get("frames") or {}).get("repaired_grid")
                endpoint(cycle.get("episode"), evaluated_body(source) if source is not None and model != "legacy" else None)
            source = final_bodies.get((generation.get("generation"), candidate_index)) if model != "legacy" else None
            final_grid = evaluated_body(source) if source is not None else None
            endpoint((creature.get("score") or {}).get("final_episode"), final_grid)
            endpoint((creature.get("breeding") or {}).get("final_episode"), final_grid)
            receipt = creature.get("care_selection")
            if receipt is not None:
                if receipt.get("body_response", "legacy") != model:
                    raise _execution_error("care selection body response differs from immutable model")
                if model != "legacy":
                    for candidate in receipt["candidates"]:
                        grid = candidate.get("candidate_grid")
                        from mecha_engine.runtime.care import care_structure_sha256
                        if (not isinstance(grid, dict) or _care_digest(grid) != candidate["grid_sha256"]
                                or grid.get("grid_id") != candidate["grid_id"]
                                or care_structure_sha256(grid) != candidate["structure_sha256"]):
                            raise _execution_error("care candidate body differs from immutable hash")
                        if receipt["evaluator"] == "archive_morphology_probe_v1":
                            from mecha_engine.archive import lifecycle_probe_grid
                            grid = lifecycle_probe_grid(grid)
                        if not isinstance(candidate.get("episode"), dict):
                            raise _execution_error("active care candidate requires body episode evidence")
                        endpoint(candidate["episode"], grid)


def _bind_body_continuation(conn, campaign_id, era_index, report):
    if era_index == 0:
        return
    row = conn.execute("SELECT report_json FROM eras WHERE campaign_id=? AND era_index=?",
                       (campaign_id, era_index - 1)).fetchone()
    if row is None and report.get("body_response", "legacy") != "legacy":
        raise _execution_error("active body response campaign lacks the preceding era")
    if row is not None:
        prior = _decode_json(row[0].encode("utf-8"))
        if prior.get("body_response", "legacy") != report.get("body_response", "legacy"):
            raise _execution_error("campaign body response cannot change between eras")


def _population_options(manifest: dict, documents: dict) -> dict | None:
    ref = manifest["inputs"].get("population_inputs_sha256")
    return documents[ref] if ref is not None else None


def _validate_population_inputs(manifest: dict, documents: dict) -> None:
    options = _population_options(manifest, documents)
    breeder_sources = [s for s in manifest["sources"] if s["source_kind"] == "era_breeder"]
    if manifest["format"] == EXECUTION_FORMAT:
        if options is not None or "ordered_breeders_sha256" in manifest or breeder_sources:
            raise _execution_error("population evidence requires execution v2")
        return
    fields = {"format", "population_policy", "founder_start_mode", "survival_regime", "cubff_density_pressure"}
    if (not isinstance(options, dict) or set(options) != fields
            or options["format"] != "survival_population_inputs_v1"
            or options["population_policy"] not in ("legacy_archive", POPULATION_POLICY)
            or options["survival_regime"] not in ("sheltered", "stress_probe")
            or type(options["cubff_density_pressure"]) is not bool):
        raise _execution_error("unsupported immutable population inputs")
    survivors = options["population_policy"] == POPULATION_POLICY
    if options["founder_start_mode"] not in (("bootstrap", "continue") if survivors else (None, "bootstrap")):
        raise _execution_error("unsupported population founder start mode")
    refs = manifest["inputs"]
    if options["cubff_density_pressure"] and (refs["weather_mode"] != "list" or not documents[refs["ordered_weather_sha256"]]):
        raise _execution_error("density pressure requires actual weather inputs")
    if not survivors:
        if "ordered_breeders_sha256" in manifest or breeder_sources:
            raise _execution_error("legacy population cannot claim living breeders")
        return
    ref = manifest.get("ordered_breeders_sha256")
    _require_digest(ref, "ordered_breeders_sha256")
    if ref not in documents or not isinstance(documents[ref], list):
        raise _execution_error("missing ordered breeder output list")
    for record in documents[ref]:
        fields = {"generation_index", "candidate_index", "grid_id", "grid", "grid_sha256", "fitness",
                  "learned_readability", "care_context", "care_context_origin"}
        if not isinstance(record, dict) or set(record) != fields:
            raise _execution_error("unsupported breeder record fields")
        for field in ("generation_index", "candidate_index"):
            _require_position(record[field], "breeder." + field)
        _require_text(record["grid_id"], "breeder.grid_id")
        if (not isinstance(record["grid"], dict) or record["grid"].get("grid_id") != record["grid_id"]
                or _care_digest(record["grid"]) != record["grid_sha256"]
                or type(record["fitness"]) not in (int, float) or not math.isfinite(record["fitness"])
                or record["learned_readability"] is not None and (type(record["learned_readability"]) not in (int, float)
                    or not math.isfinite(record["learned_readability"]))):
            raise _execution_error("breeder body identity or score disagrees")
        if record["care_context"] is None:
            if record["care_context_origin"] is not None:
                raise _execution_error("null breeder context has an origin")
        else:
            _validate_care_context(record["care_context"])
            _validate_care_origin(record["care_context_origin"], record["care_context"])
    ordered = [(row["generation_index"], row["candidate_index"]) for row in documents[ref]]
    if ordered != sorted(set(ordered)):
        raise _execution_error("breeder occurrences must be unique and in evaluation order")
    by_ordinal = {}
    for source in manifest["sources"]:
        if "founder_ordinal" not in source:
            if source["role"] == "founder" or source["source_kind"] == "era_breeder":
                raise _execution_error("population founder source requires ordinal")
            continue
        ordinal = source["founder_ordinal"]
        if source["role"] != "founder" or ordinal in by_ordinal:
            raise _execution_error("duplicate population founder source")
        by_ordinal[ordinal] = source
    if set(by_ordinal) != set(range(len(refs["founder_sha256"]))):
        raise _execution_error("population sources must cover every founder occurrence")
    for ordinal, source in by_ordinal.items():
        occurrence = manifest["founder_occurrences"][ordinal]
        projection = {key: value for key, value in source.items() if key not in ("role", "founder_ordinal", "raw_sha256")}
        if source["source_kind"] == "era_breeder":
            _require_text(source.get("campaign_id"), "breeder ancestor campaign")
            for key in ("era_index", "source_position", "generation_index", "candidate_index"):
                _require_position(source.get(key), "breeder ancestor." + key)
            _require_digest(source.get("grid_sha256"), "breeder ancestor grid")
            if source["grid_sha256"] != _care_digest(documents[refs["founder_sha256"][ordinal]]):
                raise _execution_error("breeder source differs from immutable founder body")
            projection.pop("grid_sha256")
        observed = {key: value for key, value in occurrence.items()
                    if key not in ("ordinal", "grid_id", "grid_sha256", "admitted", "rejection_errors")}
        if canonical_json(projection) != canonical_json(observed):
            raise _execution_error("population source differs from immutable occurrence")
    ordered_sources = [by_ordinal[i] for i in range(len(by_ordinal))]
    positions = [i for i, source in enumerate(ordered_sources) if source["source_kind"] == "era_breeder"]
    if options["founder_start_mode"] == "bootstrap":
        if manifest["era_index"] != 0:
            raise _execution_error("bootstrap requires a new campaign at era zero")
        if positions:
            raise _execution_error("bootstrap cannot claim breeder continuation")
    else:
        if refs["founder_mode"] != "list":
            raise _execution_error("continuation requires explicit founder list, including empty")
        if positions and positions != list(range(positions[0], len(ordered_sources))):
            raise _execution_error("breeder continuation must follow release prefix")


def _population_episode(episode, ticks: int) -> bool:
    """Check recorded endpoint facts only; this ledger never simulates a life."""
    keys = {"survival_ticks", "alive", "death_cause", "survival_ratio", "need_balance"}
    if isinstance(episode, dict) and episode.get("body_response") == "workload-v1":
        keys |= {"body_response", "body_workload", "evaluated_grid"}
    if not isinstance(episode, dict) or set(episode) != keys:
        raise _execution_error("missing or malformed population episode endpoint")
    elapsed = episode["survival_ticks"]
    if (type(elapsed) is not int or not 0 <= elapsed <= ticks or type(episode["alive"]) is not bool
            or type(episode["need_balance"]) not in (int, float) or not 0 <= episode["need_balance"] <= 1
            or type(episode["survival_ratio"]) not in (int, float)
            or episode["survival_ratio"] != (round(elapsed / ticks, 6) if ticks else 0.0)):
        raise _execution_error("population episode counters disagree")
    if episode["alive"]:
        if episode["death_cause"] is not None:
            raise _execution_error("living population endpoint does not complete its horizon")
    else:
        _require_text(episode["death_cause"], "population episode death cause")
    return episode["alive"] and elapsed == ticks


def _eligible_final_grid_id(creature, damage_cycles):
    """Versioned runtime identity: eligible bodies completed every repair cycle."""
    candidate = creature["candidate_grid_id"]
    _require_text(candidate, "candidate grid identity")
    return f"{candidate}_c{damage_cycles:02d}" if damage_cycles else candidate


def _bind_population_report(manifest, decoded, report, era):
    try:
        _checked_population_report(manifest, decoded, report, era)
    except (KeyError, TypeError, AttributeError, IndexError, OverflowError) as error:
        raise _execution_error(f"malformed population report: {error}") from error


def _checked_population_report(manifest, decoded, report, era):
    if manifest["format"] == EXECUTION_FORMAT_V2:
        _json_value(report)
    ref = manifest["inputs"].get("population_inputs_sha256")
    options = _decode_json(decoded[ref]) if ref is not None else None
    living = report.get("living_population")
    if options is not None:
        pressure = report.get("cubff_pressure", {})
        if not isinstance(pressure, dict) or type(pressure.get("density_pressure", False)) is not bool or pressure.get("density_pressure", False) != options["cubff_density_pressure"]:
            raise _execution_error("density pressure report differs from immutable inputs")
    if options is None or options["population_policy"] != POPULATION_POLICY:
        if living is not None:
            raise _execution_error("living population has no captured survivor policy")
        if options is not None and report.get("survival_regime", "sheltered") != options["survival_regime"]:
            raise _execution_error("survival regime differs from immutable inputs")
        return
    keys = {"format", "population_policy", "founder_start_mode", "survival_regime", "initial_parent_occurrences",
            "requested_candidate_slots", "evaluated_candidates", "unexecuted_candidate_slots", "final_breeders", "termination"}
    if (not isinstance(living, dict) or set(living) != keys or living["format"] != POPULATION_POLICY
            or any(living[key] != options[key] for key in ("population_policy", "founder_start_mode", "survival_regime"))
            or not isinstance(living["initial_parent_occurrences"], list)):
        raise _execution_error("living population differs from captured policy")
    breeders = _decode_json(decoded[manifest["ordered_breeders_sha256"]])
    if canonical_json(living["final_breeders"]) != canonical_json(breeders):
        raise _execution_error("breeder output blob differs from population report")
    config = manifest["effective_config"]
    for field in ("generations", "population", "damage_cycles", "ticks"):
        _require_position(config.get(field), "population configuration." + field)
    if config["generations"] < 1 or config["population"] < 1:
        raise _execution_error("population generation and capacity must be positive")
    if any(report.get(key) != config[field] or type(report.get(key)) is not int
            for key, field in (("generations_requested", "generations"), ("population", "population"),
                               ("damage_cycles", "damage_cycles"), ("ticks", "ticks"))):
        raise _execution_error("population report configuration differs from captured input")
    initial = living["initial_parent_occurrences"]
    admitted = [r["ordinal"] for r in manifest["founder_occurrences"] if r["admitted"]]
    submitted = []; seeds = []; seed_seen = False
    corpus = _decode_json(decoded[manifest["inputs"]["seed_corpus_sha256"]])
    for origin in initial:
        if not isinstance(origin, dict):
            raise _execution_error("invalid initial parent occurrence")
        kind = origin.get("kind")
        index_key = "submission_index" if kind == "submitted_founder" else "source_position"
        if kind not in ("submitted_founder", "seed_corpus") or set(origin) != {"kind", index_key, "grid_id", "grid_sha256"}:
            raise _execution_error("unsupported initial parent identity")
        position = origin[index_key]; _require_position(position, "initial parent ordinal")
        if kind == "submitted_founder":
            if seed_seen or position not in admitted:
                raise _execution_error("initial parent is not an admitted founder occurrence")
            submitted.append(position)
            grid = _decode_json(decoded[manifest["inputs"]["founder_sha256"][position]])
        else:
            seed_seen = True
            if options["founder_start_mode"] != "bootstrap" or position >= len(corpus):
                raise _execution_error("continuation cannot refill from seed corpus")
            seeds.append(position); grid = corpus[position]
        if origin["grid_id"] != grid.get("grid_id") or origin["grid_sha256"] != _care_digest(grid):
            raise _execution_error("initial parent body differs from immutable input")
    if submitted != admitted or seeds != sorted(set(seeds)):
        raise _execution_error("initial parent occurrences omit or duplicate admitted sources")
    if options["founder_start_mode"] == "bootstrap" and (not seeds
            or type(report.get("seed_pool_size")) is not int or len(seeds) != report["seed_pool_size"]):
        raise _execution_error("bootstrap must retain its actual nonempty admitted seed cohort")
    care_ref = manifest["inputs"].get("care_inputs_sha256")
    contexts = _decode_json(decoded[care_ref])["founder_contexts"] if care_ref is not None else []
    generations = report["generations"]
    if not isinstance(generations, list) or len(generations) > config["generations"]:
        raise _execution_error("invalid population generations")
    if bool(generations) != bool(initial):
        raise _execution_error("evaluated generations disagree with actual initial parent availability")
    evaluated = 0; last_eligible = []; deaths = structural = 0
    prior_eligible = {}
    for generation_index, generation in enumerate(generations):
        if type(generation.get("generation")) is not int or generation["generation"] != generation_index:
            raise _execution_error("population generation order differs")
        creatures = generation["creatures"]
        if not isinstance(creatures, list) or len(creatures) != config["population"]:
            raise _execution_error("population evaluation slots are incomplete")
        if not initial:
            raise _execution_error("population evaluates candidates without actual parents")
        evaluated += len(creatures); last_eligible = []; deaths = structural = 0
        for candidate_index, creature in enumerate(creatures):
            breeding = creature["breeding"]
            fields = {"occurrence", "parent_occurrence", "candidate_grid_sha256", "final_grid_sha256", "cycles_requested",
                      "cycles_attempted", "cycles_qualified", "final_episode", "eligible", "stop"}
            if (not isinstance(breeding, dict) or set(breeding) != fields
                    or canonical_json(breeding["occurrence"]) != canonical_json(dict(generation_index=generation_index,candidate_index=candidate_index))
                    or type(breeding["eligible"]) is not bool):
                raise _execution_error("invalid candidate breeding occurrence")
            parent = breeding["parent_occurrence"]
            if generation_index == 0:
                if canonical_json(parent) not in [canonical_json(item) for item in initial]:
                    raise _execution_error("candidate parent differs from admitted initial occurrence")
                ordinal = parent.get("submission_index")
                context = contexts[ordinal] if ordinal is not None and contexts else None
                expected_origin = {"founder_submission_index":ordinal,"context_sha256":_care_digest(context)} if context is not None else None
            else:
                if (not isinstance(parent, dict) or set(parent) != {"kind","generation_index","candidate_index","grid_id","grid_sha256"}
                        or parent["kind"] != "generation_breeder" or type(parent["generation_index"]) is not int
                        or parent["generation_index"] != generation_index-1 or type(parent["candidate_index"]) is not int):
                    raise _execution_error("candidate parent is not a prior-generation breeder occurrence")
                prior = prior_eligible.get(parent["candidate_index"])
                if prior is None or parent["grid_sha256"] != prior["breeding"]["final_grid_sha256"]:
                    raise _execution_error("candidate parent body differs from prior eligible occurrence")
                if parent["grid_id"] != _eligible_final_grid_id(prior, config["damage_cycles"]):
                    raise _execution_error("parent grid identity differs from prior eligible body")
                expected_origin = prior.get("care_context_origin")
            if creature.get("parent_grid_id") != parent["grid_id"]:
                raise _execution_error("displayed parent identity differs from actual occurrence")
            if canonical_json(creature.get("care_context_origin")) != canonical_json(expected_origin):
                raise _execution_error("candidate care origin differs from its actual parent occurrence")
            for key in ("candidate_grid_sha256", "final_grid_sha256"):
                _require_digest(breeding[key], "breeding." + key)
            for key in ("cycles_requested", "cycles_attempted", "cycles_qualified"):
                _require_position(breeding[key], "breeding." + key)
            cycles = creature["cycles"]
            if (not isinstance(cycles, list) or breeding["cycles_requested"] != config["damage_cycles"]
                    or breeding["cycles_attempted"] != len(cycles) or len(cycles) > config["damage_cycles"]):
                raise _execution_error("candidate cycle counts disagree")
            stages = creature["stages"]
            if not isinstance(stages, dict) or any(type(stages.get(key)) is not bool for key in ("candidate_valid","all_cycles_valid","all_cycles_aligned","scored")):
                raise _execution_error("candidate stage flags must be actual booleans")
            failure_stop = None if stages["candidate_valid"] else dict(stage="candidate",cycle_index=None,reason="invalid_candidate")
            if failure_stop is not None and cycles:
                raise _execution_error("invalid candidate cannot run damage cycles")
            qualified = 0; dead = False; interrupted = False
            for cycle_index, cycle in enumerate(cycles, 1):
                if (interrupted or type(cycle.get("cycle")) is not int or cycle["cycle"] != cycle_index
                        or type(cycle.get("valid")) is not bool or type(cycle.get("aligned")) is not bool):
                    raise _execution_error("candidate cycle sequence continues after a stop")
                if cycle["valid"] and cycle["aligned"]:
                    alive = _population_episode(cycle["episode"], config["ticks"])
                    dead = dead or not cycle["episode"]["alive"]; qualified += int(alive); interrupted = not alive
                    if not alive:
                        failure_stop = dict(stage="cycle_episode",cycle_index=cycle_index,
                            reason="lifecycle_death" if not cycle["episode"]["alive"] else "incomplete_episode")
                else:
                    if cycle.get("episode") is not None:
                        raise _execution_error("invalid repair claims an episode")
                    interrupted = True
                    failure_stop = dict(stage="repair",cycle_index=cycle_index,
                        reason="invalid_repair" if not cycle["valid"] else "unaligned_repair")
            if (stages["all_cycles_valid"] != (stages["candidate_valid"] and all(c["valid"] for c in cycles))
                    or stages["all_cycles_aligned"] != all(c["aligned"] for c in cycles)):
                raise _execution_error("aggregate cycle flags differ from actual recorded cycles")
            if breeding["cycles_qualified"] != qualified:
                raise _execution_error("qualified cycle count disagrees")
            complete = qualified == config["damage_cycles"] and len(cycles) == config["damage_cycles"]
            stages = creature["stages"]
            final = breeding["final_episode"]
            if final is not None:
                if not complete or stages.get("candidate_valid") is not True:
                    raise _execution_error("premature stop claims a final scoring episode")
                final_alive = _population_episode(final, config["ticks"]); dead = dead or not final["alive"]
                if stages["scored"] is not True:
                    raise _execution_error("final scoring endpoint has no actual score")
                if not final_alive:
                    failure_stop = dict(stage="final_episode",cycle_index=None,
                        reason="lifecycle_death" if not final["alive"] else "incomplete_episode")
            else:
                final_alive = False
                if failure_stop is None:
                    raise _execution_error("qualified cycles require an actual final scoring endpoint")
            eligible = (complete and stages.get("candidate_valid") is True and stages.get("all_cycles_valid") is True
                        and stages.get("all_cycles_aligned") is True and final_alive)
            if breeding["eligible"] != eligible:
                raise _execution_error("breeder eligibility differs from actual terminal endpoints")
            stop = breeding["stop"]
            if canonical_json(stop) != canonical_json(failure_stop):
                raise _execution_error("population stop differs from the actual failed stage")
            if eligible:
                if stop is not None:
                    raise _execution_error("eligible breeder has a stop")
                last_eligible.append((generation_index, candidate_index, creature))
            else:
                if (not isinstance(stop, dict) or set(stop) != {"stage", "cycle_index", "reason"}
                        or stop["stage"] not in ("candidate", "repair", "cycle_episode", "final_episode")):
                    raise _execution_error("ineligible candidate requires a stop reason")
                _require_position(stop["cycle_index"], "population stop cycle", nullable=True)
                _require_text(stop["reason"], "population stop reason")
                structural += int(stop["stage"] in ("candidate", "repair"))
            deaths += int(dead)
        prior_eligible = {index:creature for _,index,creature in last_eligible}
        if not last_eligible and generation_index != len(generations)-1:
            raise _execution_error("population continues after an empty cohort")
    requested = config["generations"] * config["population"]
    for key, expected in (("requested_candidate_slots", requested), ("evaluated_candidates", evaluated),
                          ("unexecuted_candidate_slots", requested-evaluated)):
        if type(living[key]) is not int or living[key] != expected:
            raise _execution_error("population opportunity count disagrees")
    if [(r["generation_index"],r["candidate_index"]) for r in breeders] != [(g,c) for g,c,_ in last_eligible]:
        raise _execution_error("final breeder membership differs from eligible final generation")
    for breeder, (_,_,creature) in zip(breeders,last_eligible):
        if (breeder["grid_id"] != _eligible_final_grid_id(creature, config["damage_cycles"])
                or breeder["grid_sha256"] != creature["breeding"]["final_grid_sha256"]
                or canonical_json(breeder["fitness"]) != canonical_json(creature["score"]["fitness"])):
            raise _execution_error("breeder body or fitness differs from evaluated occurrence")
        context, origin = breeder["care_context"], breeder["care_context_origin"]
        if canonical_json(origin) != canonical_json(creature.get("care_context_origin")):
            raise _execution_error("breeder care differs from evaluated occurrence")
        if context is not None:
            ordinal = origin["founder_submission_index"]
            if (ordinal >= len(contexts) or not manifest["founder_occurrences"][ordinal]["admitted"]
                    or canonical_json(context) != canonical_json(contexts[ordinal])):
                raise _execution_error("breeder care differs from admitted founder occurrence")
    termination = living["termination"]
    fields = {"ended", "reason", "generation_index", "lifecycle_deaths", "structural_disqualifications", "genuine_lifecycle_extinction"}
    if not isinstance(termination, dict) or set(termination) != fields:
        raise _execution_error("unsupported population termination fields")
    ended = not breeders; terminal_generation = len(generations)-1 if generations else None
    expected_reason = ("requested_horizon_complete" if breeders else "no_eligible_breeders" if generations
                       else "empty_continuation" if not manifest["inputs"]["founder_sha256"] else "all_founders_rejected")
    expected = dict(ended=ended,reason=expected_reason,generation_index=terminal_generation,lifecycle_deaths=deaths,
        structural_disqualifications=structural,genuine_lifecycle_extinction=ended and deaths>0)
    if canonical_json(termination) != canonical_json(expected) or type(era.get("went_extinct")) is not bool or era["went_extinct"] != ended:
        raise _execution_error("population termination differs from actual final cohort")
    if breeders and len(generations) != config["generations"]:
        raise _execution_error("living population stopped before requested horizon")


def _checked_population_ancestors(conn, bundle):
    manifest = bundle["manifest"]
    ref = manifest["inputs"].get("population_inputs_sha256")
    if ref is None:
        return
    options = _decode_json(base64.b64decode(bundle["blobs"][ref]["data_base64"]))
    if options["population_policy"] != POPULATION_POLICY or options["founder_start_mode"] != "continue":
        return
    era_index = manifest["era_index"]
    if era_index < 1:
        raise _execution_error("continuation requires a prior same-campaign era")
    ended = conn.execute("SELECT went_extinct FROM eras WHERE campaign_id=? AND era_index=?",(manifest["campaign_id"],era_index-1)).fetchone()
    if ended is not None and ended[0]:
        raise _execution_error("extinct predecessor cannot continue or accept releases")
    prior = load_era_breeders(conn, manifest["campaign_id"], era_index-1)
    if prior is None:
        raise _execution_error("continuation has no verified living predecessor cohort")
    sources = sorted((s for s in manifest["sources"] if "founder_ordinal" in s), key=lambda s:s["founder_ordinal"])
    breeders = [s for s in sources if s["source_kind"] == "era_breeder"]
    if len(breeders) != len(prior):
        raise _execution_error("continuation must include the complete previous breeder cohort")
    for position, (source, ancestor) in enumerate(zip(breeders,prior)):
        if (source["campaign_id"] != manifest["campaign_id"] or source["era_index"] != era_index-1
                or source["source_position"] != position
                or any(source[key] != ancestor[key] for key in ("generation_index", "candidate_index", "grid_sha256"))):
            raise _execution_error("breeder source differs from the prior ordered occurrence")
        grid_ref = manifest["inputs"]["founder_sha256"][source["founder_ordinal"]]
        grid = _decode_json(base64.b64decode(bundle["blobs"][grid_ref]["data_base64"]))
        if (canonical_json(grid) != canonical_json(ancestor["grid"])
                or canonical_json(source.get("care_context")) != canonical_json(ancestor["care_context"])
                or canonical_json(source.get("care_context_origin")) != canonical_json(ancestor["care_context_origin"])):
            raise _execution_error("breeder source body or care differs from the prior slot")


def load_era_breeders(conn: sqlite3.Connection, campaign_id: str, era_index: int) -> list[dict] | None:
    """Verified ordered living cohort, [] explicit empty, None historical absence.

    Never interprets an archive elite as living, upgrades a schema, or repairs
    missing evidence. A new-policy report without its execution refuses.
    """
    bundle = load_era_execution(conn, campaign_id, era_index)
    if bundle is None:
        row = conn.execute("SELECT report_json FROM eras WHERE campaign_id=? AND era_index=?",(campaign_id,era_index)).fetchone()
        if row is not None and "living_population" in _decode_json(row[0].encode("utf-8")):
            raise _execution_error("living population execution evidence is missing")
        return None
    ref = bundle["manifest"].get("ordered_breeders_sha256")
    return _decode_json(base64.b64decode(bundle["blobs"][ref]["data_base64"])) if ref is not None else None


def _population_founder_projection(manifest, decoded):
    ref = manifest["inputs"].get("population_inputs_sha256")
    if ref is None or _decode_json(decoded[ref])["population_policy"] != POPULATION_POLICY:
        return None
    rows = manifest["founder_occurrences"]
    counts = {}
    for row in rows:
        counts[row["grid_id"]] = counts.get(row["grid_id"], 0) + 1
    return sorted([dict(grid_id=row["grid_id"], source="workshop_release", admitted=row["admitted"],
                        rejection_errors=row["rejection_errors"], grid=_decode_json(decoded[row["grid_sha256"]]))
                   for row in rows if row["source_kind"] != "era_breeder" and counts[row["grid_id"]] == 1],
                  key=lambda row: row["grid_id"])


def _bind_population_projection(manifest, decoded, founders):
    expected = _population_founder_projection(manifest, decoded)
    if expected is not None and (not isinstance(founders, list)
            or any(not isinstance(row, dict) or not isinstance(row.get("grid_id"),str) for row in founders)
            or canonical_json(sorted(founders, key=lambda row:row["grid_id"])) != canonical_json(expected)):
        raise _execution_error("legacy founder projection differs from population release occurrences")


def _load_population_projection(conn, campaign_id, era_index):
    result = []
    for grid_id, source, admitted, errors, grid in conn.execute(
            "SELECT grid_id, source, admitted, rejection_errors_json, grid_json FROM founders "
            "WHERE campaign_id=? AND era_index=? ORDER BY grid_id",(campaign_id,era_index)):
        if admitted not in (0, 1):
            raise _execution_error("invalid projected founder admission")
        result.append(dict(grid_id=grid_id,source=source,admitted=bool(admitted),
            rejection_errors=_decode_json(errors.encode("utf-8")) if errors is not None else None,
            grid=_decode_json(grid.encode("utf-8")) if grid is not None else None))
    return result


def _validated_execution(bundle: dict) -> dict[str, bytes]:
    """Pure structural validation; execution compatibility is game-owned."""
    try:
        _json_value(bundle)
        if not isinstance(bundle, dict) or set(bundle) != {"manifest", "blobs"}:
            raise _execution_error("bundle needs manifest and blobs")
        manifest, blobs = bundle["manifest"], bundle["blobs"]
        if not isinstance(manifest, dict) or not isinstance(blobs, dict):
            raise _execution_error("manifest and blobs must be objects")
        if manifest["format"] not in (EXECUTION_FORMAT, EXECUTION_FORMAT_V2):
            raise _execution_error("unsupported manifest format")
        _require_text(manifest["campaign_id"], "campaign_id")
        _require_position(manifest["era_index"], "era_index")
        if type(manifest["rng_seed"]) is not int:
            raise _execution_error("rng_seed must be an integer")
        contract = manifest["execution_contract"]
        if not isinstance(contract, dict):
            raise _execution_error("execution_contract must be an object")
        _require_text(contract["name"], "execution_contract.name")
        if not isinstance(contract["runtime"], dict) or not isinstance(contract["policies"], dict):
            raise _execution_error("runtime and policies must be objects")
        if not isinstance(manifest["effective_config"], dict):
            raise _execution_error("effective_config must be an object")
        for field in ("report_sha256", "elites_sha256", "calibration_sha256"):
            _require_digest(manifest[field], field)
        decoded = {}
        documents = {}
        for sha, blob in blobs.items():
            _require_digest(sha, "blob key")
            if not isinstance(blob, dict) or set(blob) != {"media_type", "data_base64"}:
                raise _execution_error("blob needs media_type and data_base64")
            if blob["media_type"] not in ("application/json", "application/octet-stream"):
                raise _execution_error("unsupported blob media type")
            if not isinstance(blob["data_base64"], str):
                raise _execution_error("blob data_base64 must be text")
            data = base64.b64decode(blob["data_base64"], validate=True)
            if base64.b64encode(data).decode("ascii") != blob["data_base64"]:
                raise _execution_error("noncanonical base64")
            if hashlib.sha256(data).hexdigest() != sha:
                raise _execution_error("blob hash mismatch")
            decoded[sha] = data
            if blob["media_type"] == "application/json":
                documents[sha] = _decode_json(data)

        def reference(sha, field, *, raw=False):
            _require_digest(sha, field)
            media = ("application/json", "application/octet-stream") if raw else ("application/json",)
            if sha not in decoded or blobs[sha]["media_type"] not in media:
                raise _execution_error(f"missing or wrongly typed blob: {field}")
            return None if raw else documents[sha]

        reference(manifest["calibration_sha256"], "calibration_sha256")
        if "ordered_elites_sha256" in manifest:
            if not isinstance(reference(manifest["ordered_elites_sha256"], "ordered_elites_sha256"), list):
                raise _execution_error("ordered elite outputs must be a list")
        inputs = manifest["inputs"]
        if not isinstance(inputs, dict):
            raise _execution_error("inputs must be an object")
        for field in _REQUIRED_INPUT_DIGESTS:
            reference(inputs[field], field)
        if not isinstance(documents[inputs["seed_corpus_sha256"]], list):
            raise _execution_error("seed corpus must be an ordered list")
        if not isinstance(documents[inputs["covenant_sha256"]], dict):
            raise _execution_error("covenant must be an object")
        for field, sha in inputs.items():
            if field.endswith("_sha256") and field not in ("founder_sha256", "ordered_weather_sha256"):
                reference(sha, field)
        founders = inputs["founder_sha256"]
        if not isinstance(founders, list) or inputs["founder_mode"] not in ("none", "list"):
            raise _execution_error("invalid founder mode or ordered references")
        if inputs["founder_mode"] == "none" and founders:
            raise _execution_error("none founder mode has submitted founders")
        for sha in founders:
            if not isinstance(reference(sha, "founder_sha256"), dict):
                raise _execution_error("founder genome must be an object")
        if inputs["weather_mode"] == "none":
            if inputs["ordered_weather_sha256"] is not None:
                raise _execution_error("none weather mode has weather bytes")
        elif inputs["weather_mode"] == "list":
            if not isinstance(reference(inputs["ordered_weather_sha256"], "ordered_weather_sha256"), list):
                raise _execution_error("weather must be an ordered list")
        else:
            raise _execution_error("invalid weather mode")
        sources = manifest["sources"]
        if not isinstance(sources, list):
            raise _execution_error("sources must be an ordered list")
        for source in sources:
            if not isinstance(source, dict):
                raise _execution_error("source must be an object")
            _require_text(source["role"], "source.role")
            _require_text(source["source_kind"], "source.source_kind")
            _require_position(source["source_position"], "source.source_position", nullable=True)
            if "founder_ordinal" in source:
                _require_position(source["founder_ordinal"], "source.founder_ordinal")
                if source["founder_ordinal"] >= len(founders):
                    raise _execution_error("source founder ordinal outside submitted inputs")
            if "label" in source:
                label = source["label"]
                _require_text(label, "source.label")
                if label.startswith(("/", "\\")) or ":" in label or ".." in label.replace("\\", "/").split("/"):
                    raise _execution_error("source label must be relative")
            if "raw_sha256" in source:
                reference(source["raw_sha256"], "source.raw_sha256", raw=True)
        occurrences = manifest["founder_occurrences"]
        if not isinstance(occurrences, list) or len(occurrences) != len(founders):
            raise _execution_error("founder occurrences must match submitted inputs")
        for ordinal, occurrence in enumerate(occurrences):
            if not isinstance(occurrence, dict):
                raise _execution_error("founder occurrence must be an object")
            if type(occurrence["ordinal"]) is not int or occurrence["ordinal"] != ordinal:
                raise _execution_error("founder ordinals must be contiguous and ordered")
            if occurrence["grid_sha256"] != founders[ordinal]:
                raise _execution_error("founder occurrence does not match ordered genome")
            if canonical_json(occurrence["grid_id"]) != canonical_json(documents[founders[ordinal]].get("grid_id")):
                raise _execution_error("founder grid identity does not match genome")
            _require_text(occurrence["source_kind"], "founder.source_kind")
            _require_position(occurrence["source_position"], "founder.source_position", nullable=True)
            admitted, errors = occurrence["admitted"], occurrence["rejection_errors"]
            if type(admitted) is not bool:
                raise _execution_error("founder admission must be boolean")
            if admitted:
                if errors is not None:
                    raise _execution_error("admitted founder has rejection errors")
            elif not isinstance(errors, list) or not errors or any(not isinstance(item, str) for item in errors):
                raise _execution_error("refused founder needs verbatim errors")
            for field in ("campaign_id", "niche_key"):
                if field in occurrence:
                    _require_text(occurrence[field], f"founder.{field}")
            if "era_index" in occurrence:
                _require_position(occurrence["era_index"], "founder.era_index")
        _validate_population_inputs(manifest, documents)
        _validate_care_inputs(manifest, documents)
        _validate_body_inputs(manifest, documents)
        if _manifest_references(manifest) != set(blobs):
            raise _execution_error("bundle contains blobs outside manifest references")
        return decoded
    except (KeyError, TypeError, AttributeError, binascii.Error, UnicodeError) as error:
        raise _execution_error(f"malformed bundle: {error}") from error


def validate_execution(bundle: dict) -> None:
    """Validate hashes, references and occurrence ordering without I/O or simulation."""
    _validated_execution(bundle)


def _bind_execution(bundle: dict, decoded: dict[str, bytes], campaign_id: str,
                    era: dict, slip_profile: dict) -> None:
    manifest = bundle["manifest"]
    for key, value in (("campaign_id", campaign_id), ("era_index", era["era_index"]),
                       ("rng_seed", era["rng_seed"])):
        if canonical_json(manifest[key]) != canonical_json(value):
            raise _execution_error(f"recorded {key} differs from era")
    covenant = _decode_json(decoded[manifest["inputs"]["covenant_sha256"]])
    if canonical_json(covenant) != canonical_json(slip_profile):
        raise _execution_error("recorded covenant differs from era profile")
    if "ordered_elites_sha256" in manifest:
        ordered_elites = _decode_json(decoded[manifest["ordered_elites_sha256"]])
        if canonical_json(ordered_elites) != canonical_json(era.get("elites", [])):
            raise _execution_error("ordered elite output bytes differ from era result")
    report = era["report"]
    _bind_body_report(manifest, decoded, report)
    _bind_care_report(manifest, decoded, report, era.get("elites", []))
    _bind_population_report(manifest, decoded, report, era)
    if manifest["inputs"]["founder_mode"] == "none":
        if "founders" in report:
            raise _execution_error("none founder mode differs from report founder presence")
    else:
        occurrences = manifest["founder_occurrences"]
        admissions = {
            "admitted_ids": [item["grid_id"] for item in occurrences if item["admitted"]],
            "rejected": [{"grid_id": item["grid_id"], "errors": item["rejection_errors"]}
                         for item in occurrences if not item["admitted"]],
        }
        # Preserve both ordered streams, verbatim errors and duplicate IDs.
        # Only the observer's ordinal identifies which equal-ID body was admitted.
        if canonical_json(report.get("founders")) != canonical_json(admissions):
            raise _execution_error("founder admission occurrences differ from era report")
    for key, value in (("report_sha256", report), ("elites_sha256", era.get("elites", []))):
        if hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest() != manifest[key]:
            raise _execution_error(f"recorded {key} differs from era result")


def _record_execution(conn: sqlite3.Connection, bundle: dict, decoded: dict[str, bytes]) -> None:
    manifest = bundle["manifest"]
    for sha, data in decoded.items():
        media = bundle["blobs"][sha]["media_type"]
        prior = conn.execute("SELECT media_type, payload FROM execution_blobs WHERE sha256 = ?", (sha,)).fetchone()
        if prior is None:
            conn.execute("INSERT INTO execution_blobs (sha256, media_type, payload) VALUES (?, ?, ?)",
                         (sha, media, data))
        elif prior != (media, data):
            raise _execution_error("existing blob conflicts with immutable bytes or media type")
    text = canonical_json(manifest)
    conn.execute("INSERT INTO era_executions (campaign_id, era_index, manifest_json, manifest_sha256) VALUES (?, ?, ?, ?)",
                 (manifest["campaign_id"], manifest["era_index"], text, hashlib.sha256(text.encode("utf-8")).hexdigest()))
    for occurrence in manifest["founder_occurrences"]:
        conn.execute("INSERT INTO founder_occurrences (campaign_id, era_index, ordinal, occurrence_json) VALUES (?, ?, ?, ?)",
                     (manifest["campaign_id"], manifest["era_index"], occurrence["ordinal"], canonical_json(occurrence)))


def load_era_execution(conn: sqlite3.Connection, campaign_id: str, era_index: int) -> dict | None:
    """Read verified immutable inputs. Historical absence never triggers migration."""
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version not in SUPPORTED_READ_SCHEMA_VERSIONS:
        raise ValueError(f"unsupported campaign-ledger schema version: {version}")
    if version == 1:
        return None
    try:
        row = conn.execute("SELECT manifest_json, manifest_sha256 FROM era_executions WHERE campaign_id = ? AND era_index = ?",
                           (campaign_id, era_index)).fetchone()
        if row is None:
            era_report = conn.execute("SELECT report_json FROM eras WHERE campaign_id=? AND era_index=?",
                                      (campaign_id, era_index)).fetchone()
            if era_report is not None and "body_response" in _decode_json(era_report[0].encode("utf-8")):
                raise _execution_error("body response execution evidence is missing")
            if conn.execute("SELECT 1 FROM founder_occurrences WHERE campaign_id = ? AND era_index = ? LIMIT 1",
                            (campaign_id, era_index)).fetchone() is not None:
                raise _execution_error("orphan founder occurrence projection")
            return None
        if not isinstance(row[0], str) or hashlib.sha256(row[0].encode("utf-8")).hexdigest() != row[1]:
            raise _execution_error("manifest hash mismatch")
        manifest = _decode_json(row[0].encode("utf-8"))
        blobs = {}
        for sha in sorted(_manifest_references(manifest)):
            blob = conn.execute("SELECT media_type, payload FROM execution_blobs WHERE sha256 = ?", (sha,)).fetchone()
            if blob is None or not isinstance(blob[1], bytes):
                raise _execution_error("missing or non-binary execution blob")
            blobs[sha] = dict(media_type=blob[0], data_base64=base64.b64encode(blob[1]).decode("ascii"))
        bundle = dict(manifest=manifest, blobs=blobs)
        decoded = _validated_execution(bundle)
        rows = conn.execute("SELECT ordinal, occurrence_json FROM founder_occurrences WHERE campaign_id = ? AND era_index = ? ORDER BY ordinal",
                            (campaign_id, era_index)).fetchall()
        expected = [(item["ordinal"], canonical_json(item)) for item in manifest["founder_occurrences"]]
        if rows != expected:
            raise _execution_error("founder occurrence projection differs from manifest")
        era_row = conn.execute("SELECT e.rng_seed, e.report_json, p.profile_json, e.went_extinct FROM eras e JOIN slip_profiles p ON p.profile_id = e.slip_profile_id WHERE e.campaign_id = ? AND e.era_index = ?",
                               (campaign_id, era_index)).fetchone()
        if era_row is None:
            raise _execution_error("execution has no matching era/profile")
        era = dict(era_index=era_index, rng_seed=era_row[0], report=_decode_json(era_row[1].encode("utf-8")),
                   elites=load_era_elites(conn, campaign_id, era_index), went_extinct=bool(era_row[3]))
        _bind_execution(bundle, decoded, campaign_id, era, _decode_json(era_row[2].encode("utf-8")))
        _bind_care_ancestors(conn, bundle)
        _bind_body_continuation(conn, campaign_id, era_index, era["report"])
        if _population_founder_projection(manifest, decoded) is not None:
            _bind_population_projection(manifest, decoded, _load_population_projection(conn, campaign_id, era_index))
        return bundle
    except (KeyError, TypeError, AttributeError, UnicodeError, sqlite3.DatabaseError) as error:
        raise _execution_error(f"unreadable ledger evidence: {error}") from error


def canonical_json(value) -> str:
    """The blob-authoritative encoding (DR 0022): canonical JSON text."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def open_ledger(path: str | Path) -> sqlite3.Connection:
    """Open the ordinary writer; schema changes are forward-only and atomic."""
    conn = sqlite3.connect(str(path))
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, *SUPPORTED_READ_SCHEMA_VERSIONS):
            raise ValueError(f"unsupported campaign-ledger schema version: {version}")
        if version < SCHEMA_VERSION:
            # executescript commits pending transactions. Individual DDL statements
            # inside BEGIN keep both tables and user_version atomic on failure.
            with conn:
                conn.execute("BEGIN IMMEDIATE")
                schema = (SCHEMA if version == 0 else "") + SCHEMA_V2
                for statement in schema.split(";"):
                    if statement.strip():
                        conn.execute(statement)
                conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        return conn
    except BaseException:
        conn.close()
        raise


def record_campaign(conn: sqlite3.Connection, campaign: dict) -> None:
    """Insert or update one campaign row (status changes flow through
    here — e.g. extinction)."""
    with conn:
        conn.execute(
            "INSERT INTO campaigns (campaign_id, keeper_label, created_date,"
            " predecessor_campaign_id, status) VALUES (?, ?, ?, ?, ?)"
            " ON CONFLICT(campaign_id) DO UPDATE SET status = excluded.status",
            (
                campaign["campaign_id"],
                campaign["keeper_label"],
                campaign["created_date"],
                campaign["predecessor_campaign_id"],
                campaign["status"],
            ),
        )


def record_era(
    conn: sqlite3.Connection,
    campaign_id: str,
    era: dict,
    slip_profile: dict,
    founders: list[dict] | None = None,
    unlocks: list[dict] | None = None,
    execution: dict | None = None,
) -> None:
    """One era = one transaction (DR 0022): the profile, the era row,
    its elites, its founder admissions, unlock facts and optional execution commit
    atomically or not at all.

    ``era`` is the interim era row shape: era_index, rng_seed, weather,
    the VERBATIM report, and the derived flags; elites ride either on
    the era (session records) or are passed via the interim's elites
    rows by the ingester.
    """
    report = era["report"]
    if "body_response" in report and execution is None:
        raise _execution_error("body response requires immutable execution")
    _bind_body_continuation(conn, campaign_id, era["era_index"], report)
    if "living_population" in report and execution is None:
        raise _execution_error("living population requires immutable execution")
    decoded = None
    if execution is not None:
        decoded = _validated_execution(execution)
        _bind_execution(execution, decoded, campaign_id, era, slip_profile)
        _bind_care_ancestors(conn, execution)
        _bind_population_projection(execution["manifest"], decoded, [] if founders is None else founders)
        if era.get("elites", []) != sorted(era.get("elites", []), key=lambda item: item["niche_key"]):
            raise _execution_error("complete elites must be in niche order")
    with conn:
        cursor = conn.execute(
            "INSERT INTO slip_profiles (campaign_id, era_index,"
            " slip_version, profile_json) VALUES (?, ?, ?, ?)",
            (
                campaign_id,
                era["era_index"],
                str(slip_profile.get("slip_version", "unknown")),
                canonical_json(slip_profile),
            ),
        )
        profile_row_id = cursor.lastrowid
        conn.execute(
            "INSERT INTO eras (campaign_id, era_index, rng_seed,"
            " slip_profile_id, weather_json, report_json, decision_status,"
            " filled_niches, coverage, qd_score, max_lineage_generation,"
            " went_extinct) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                campaign_id,
                era["era_index"],
                era["rng_seed"],
                profile_row_id,
                canonical_json(era["weather"])
                if era.get("weather") is not None
                else None,
                canonical_json(report),
                report["decision"]["status"],
                report["summary"]["archive"]["filled_niches"],
                report["summary"]["archive"]["coverage"],
                report["summary"]["archive"]["qd_score"],
                report["summary"]["max_lineage_generation"],
                1 if era["went_extinct"] else 0,
            ),
        )
        for elite in era.get("elites", []):
            record = {
                key: value for key, value in elite.items() if key != "niche_key"
            }
            conn.execute(
                "INSERT INTO elites (campaign_id, era_index, niche_key,"
                " grid_id, fitness, elite_json) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    campaign_id,
                    era["era_index"],
                    elite["niche_key"],
                    record["grid_id"],
                    record["fitness"],
                    canonical_json(record),
                ),
            )
        for founder in founders or []:
            conn.execute(
                "INSERT INTO founders (campaign_id, era_index, grid_id,"
                " source, admitted, rejection_errors_json, grid_json)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    campaign_id,
                    era["era_index"],
                    founder["grid_id"],
                    founder["source"],
                    1 if founder["admitted"] else 0,
                    canonical_json(founder["rejection_errors"])
                    if founder.get("rejection_errors") is not None
                    else None,
                    canonical_json(founder["grid"])
                    if founder.get("grid") is not None
                    else None,
                ),
            )
        for fact in unlocks or []:
            conn.execute(
                "INSERT INTO unlocks (campaign_id, axis, tier,"
                " earned_era_index, metric_path, metric_value, threshold)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    campaign_id,
                    fact["axis"],
                    fact["tier"],
                    fact["earned_era_index"],
                    fact["metric_path"],
                    canonical_json(fact["metric_value"]),
                    canonical_json(fact["threshold"]),
                ),
            )

        if execution is not None:
            _record_execution(conn, execution, decoded)


def record_replay(
    conn: sqlite3.Connection,
    campaign_id: str,
    era_index: int,
    artifact_path: str,
    artifact_sha256: str,
) -> None:
    """One replays-table row (C5): the artifact stays a file; the
    ledger stores the pointer and the content hash (DR 0022)."""
    with conn:
        conn.execute(
            "INSERT INTO replays (campaign_id, era_index, artifact_path,"
            " artifact_sha256) VALUES (?, ?, ?, ?)",
            (campaign_id, era_index, artifact_path, artifact_sha256),
        )


def load_replay_rows(
    conn: sqlite3.Connection, campaign_id: str
) -> list[dict]:
    return [
        {
            "campaign_id": campaign_id,
            "era_index": row[0],
            "artifact_path": row[1],
            "artifact_sha256": row[2],
        }
        for row in conn.execute(
            "SELECT era_index, artifact_path, artifact_sha256 FROM replays"
            " WHERE campaign_id = ? ORDER BY era_index, artifact_path",
            (campaign_id,),
        )
    ]


def load_era_elites(
    conn: sqlite3.Connection, campaign_id: str, era_index: int
) -> list[dict]:
    """Complete recorded elites in niche order, with no derived recomputation.

    The blob remains authoritative for grid/fitness/descriptor values; the
    primary-key niche is the only field stored outside that blob (DR 0022).
    Missing campaigns/eras return an empty selection without creating records.
    """
    rows = conn.execute(
        "SELECT niche_key, elite_json FROM elites WHERE campaign_id = ?"
        " AND era_index = ? ORDER BY niche_key",
        (campaign_id, era_index),
    ).fetchall()
    return [{**json.loads(row[1]), "niche_key": row[0]} for row in rows]


def load_founder_pool(
    conn: sqlite3.Connection,
    campaign_id: str,
    era_index: int | None = None,
) -> list[dict]:
    """The founder pool for the NEXT era (default) or for a given era —
    the previous era's elites in niche-key order, the same deterministic
    ordering ``evolve`` uses for elite parents (DR 0022)."""
    if era_index is None:
        row = conn.execute(
            "SELECT MAX(era_index) FROM eras WHERE campaign_id = ?",
            (campaign_id,),
        ).fetchone()
        if row[0] is None:
            return []
        source_era = row[0]
    else:
        source_era = era_index - 1
        if source_era < 0:
            return []
    rows = conn.execute(
        "SELECT elite_json FROM elites WHERE campaign_id = ? AND"
        " era_index = ? ORDER BY niche_key",
        (campaign_id, source_era),
    ).fetchall()
    return [json.loads(row[0])["grid"] for row in rows]


def load_unlock_state(
    conn: sqlite3.Connection, campaign_id: str
) -> list[dict]:
    """The Keeper's unlock state: this campaign's facts plus every
    predecessor's, resolved through the pointer chain — rows are never
    copied (DR 0022's succession rule)."""
    facts: list[dict] = []
    seen: set[str] = set()
    current: str | None = campaign_id
    while current is not None and current not in seen:
        seen.add(current)
        for row in conn.execute(
            "SELECT axis, tier, earned_era_index, metric_path,"
            " metric_value, threshold FROM unlocks WHERE campaign_id = ?"
            " ORDER BY axis, tier",
            (current,),
        ):
            facts.append(
                {
                    "campaign_id": current,
                    "axis": row[0],
                    "tier": row[1],
                    "earned_era_index": row[2],
                    "metric_path": row[3],
                    "metric_value": json.loads(row[4]),
                    "threshold": json.loads(row[5]),
                }
            )
        row = conn.execute(
            "SELECT predecessor_campaign_id FROM campaigns WHERE"
            " campaign_id = ?",
            (current,),
        ).fetchone()
        current = row[0] if row else None
    return facts


def campaign_history(
    conn: sqlite3.Connection, campaign_id: str
) -> dict:
    """Replay-sufficient history: the campaign row plus every era's
    verbatim inputs and report."""
    row = conn.execute(
        "SELECT campaign_id, keeper_label, created_date,"
        " predecessor_campaign_id, status FROM campaigns WHERE"
        " campaign_id = ?",
        (campaign_id,),
    ).fetchone()
    if row is None:
        raise KeyError(f"no such campaign: {campaign_id}")
    eras = []
    for era_row in conn.execute(
        "SELECT e.era_index, e.rng_seed, e.weather_json, e.report_json,"
        " e.went_extinct, p.profile_json FROM eras e JOIN slip_profiles p"
        " ON p.profile_id = e.slip_profile_id WHERE e.campaign_id = ?"
        " ORDER BY e.era_index",
        (campaign_id,),
    ):
        eras.append(
            {
                "era_index": era_row[0],
                "rng_seed": era_row[1],
                "weather": json.loads(era_row[2])
                if era_row[2] is not None
                else None,
                "report": json.loads(era_row[3]),
                "went_extinct": bool(era_row[4]),
                "slip_profile": json.loads(era_row[5]),
            }
        )
    return {
        "campaign_id": row[0],
        "keeper_label": row[1],
        "created_date": row[2],
        "predecessor_campaign_id": row[3],
        "status": row[4],
        "eras": eras,
        "unlocks": load_unlock_state(conn, campaign_id),
    }


def ingest_session_artifacts(
    conn: sqlite3.Connection, interim: dict | str | Path
) -> dict:
    """Consume the shipped JSON interim (`dr0022_v1_json_interim`)
    losslessly. Returns row counts per table."""
    if not isinstance(interim, dict):
        interim = json.loads(Path(interim).read_text(encoding="utf-8"))
    if interim.get("schema") != INTERIM_SCHEMA:
        raise ValueError(
            f"not a {INTERIM_SCHEMA} ledger: {interim.get('schema')!r}"
        )
    for campaign in interim["campaigns"]:
        record_campaign(conn, campaign)
    unlocks_by_campaign: dict[str, list[dict]] = {}
    for fact in interim["unlocks"]:
        unlocks_by_campaign.setdefault(fact["campaign_id"], []).append(
            {key: value for key, value in fact.items() if key != "campaign_id"}
        )
    for era_row in interim["eras"]:
        campaign_id = era_row["campaign_id"]
        elites = [
            {
                "niche_key": row["niche_key"],
                **row["elite"],
            }
            for row in interim["elites"]
            if row["campaign_id"] == campaign_id
            and row["era_index"] == era_row["era_index"]
        ]
        founders = [
            {
                "grid_id": row["grid_id"],
                "source": row["source"],
                "admitted": row["admitted"],
                "rejection_errors": row["rejection_errors"],
                "grid": row.get("grid"),
            }
            for row in interim["founders"]
            if row["campaign_id"] == campaign_id
            and row["era_index"] == era_row["era_index"]
        ]
        era_unlocks = [
            fact
            for fact in unlocks_by_campaign.get(campaign_id, [])
            if fact["earned_era_index"] == era_row["era_index"]
        ]
        record_era(
            conn,
            campaign_id,
            {
                "era_index": era_row["era_index"],
                "rng_seed": era_row["rng_seed"],
                "weather": era_row["weather"],
                "report": era_row["report"],
                "went_extinct": era_row["went_extinct"],
                "elites": elites,
            },
            era_row["slip_profile"],
            founders=founders,
            unlocks=era_unlocks,
        )
    for replay_row in interim.get("replays", []):
        record_replay(
            conn,
            replay_row["campaign_id"],
            replay_row["era_index"],
            replay_row["artifact_path"],
            replay_row["artifact_sha256"],
        )
    counts = {}
    for table in (
        "campaigns",
        "slip_profiles",
        "eras",
        "elites",
        "founders",
        "unlocks",
        "replays",
    ):
        counts[table] = conn.execute(
            f"SELECT COUNT(*) FROM {table}"  # noqa: S608 — fixed table names
        ).fetchone()[0]
    return counts
