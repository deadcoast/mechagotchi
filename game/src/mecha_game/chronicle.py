"""Keeper facts, separate from engine ancestry and per-life learning.

Cycle 38 preregistration: unique actual-life identities; exact observed care
counters with a bounded event tail; no inferred legacy care, genetic parentage
or death. Explicit X7 contextual selection consumes a validated frozen copy;
ordinary lifecycle and disabled generation remain independent of these facts.
"""
from __future__ import annotations

import hashlib
import json
import uuid

CHRONICLE_FORMAT = "keeper_chronicle_v1"


def clone(value):
    return json.loads(json.dumps(value, allow_nan=False))


def new_chronicle(*, legacy_payload: dict | None = None) -> dict:
    if legacy_payload is None:
        identity = uuid.uuid4().hex
    else:
        # Stable for the exact legacy read snapshot; no claim that absent old
        # identity can distinguish historical copies in different save homes.
        identity = "legacy-" + hashlib.sha256(
            json.dumps(legacy_payload, sort_keys=True, allow_nan=False).encode()).hexdigest()[:32]
    return {
        "chronicle_format": CHRONICLE_FORMAT,
        "keeper_id": "keeper-" + identity,
        "identity_origin": "new_keeper" if legacy_payload is None else "legacy_snapshot",
        "prior_history": "none" if legacy_payload is None else "unavailable",
        "campaign_id": None,
        "campaign_links": [],
    }


def new_life_identity(keeper_id: str) -> str:
    # A recovered snapshot may branch while newer lives survive in a recovery
    # archive. Ordinal identities would alias those distinct actual lives.
    return f"{keeper_id}:life-{uuid.uuid4().hex}"


def observe_life(record: dict, *, life_id: str, age_ticks: int,
                 session_tick: int, history: str = "complete") -> None:
    """Begin observation at a known boundary, never infer previous actions."""
    record.update(life_id=life_id, last_age_ticks=age_ticks,
                  last_session_tick=session_tick,
                  outcome="dead" if "death_cause" in record else "alive",
                  care_summary={"history": history, "from_age_ticks": age_ticks,
                                "ticks_observed": 0, "keeper_actions": {},
                                "companion_actions": {}, "beg_requests": 0},
                  events=[], events_omitted=0)


def record_tick(record: dict, entry: dict, *, event_limit: int) -> None:
    summary = record["care_summary"]
    summary["ticks_observed"] += 1
    actions = summary[entry["actor"] + "_actions"]
    action = entry["action"]
    actions[action] = actions.get(action, 0) + 1
    summary["beg_requests"] += int(entry["begging"])
    record["last_age_ticks"] = entry["tick"]
    record["last_session_tick"] = entry["session_tick"]
    record["events"].append(clone(entry))
    if len(record["events"]) > event_limit:
        record["events"] = record["events"][-event_limit:]
        record["events_omitted"] += 1
    if not entry["alive"]:
        record["outcome"] = "dead"
        record["ended_age_ticks"] = entry["tick"]
        record["ended_session_tick"] = entry["session_tick"]


def import_legacy(payload: dict) -> tuple[dict, list[dict]]:
    """Keep known historical fields; annotate only the observation boundary."""
    metadata = new_chronicle(legacy_payload=payload)
    records = clone(payload["lineage"])
    if not records or any(not isinstance(row, dict) for row in records):
        raise ValueError("invalid companion chronicle: no valid lineage records")
    for index, record in enumerate(records):
        current = index == len(records) - 1
        age = payload["state"]["age_ticks"] if current else record.get("died_age_ticks", 0)
        tick = payload["session_tick"] if current else record.get("died_session_tick", record.get("born_session_tick", 0))
        observe_life(record, life_id=f"{metadata['keeper_id']}:life-{index + 1}",
                     age_ticks=age, session_tick=tick,
                     history="partial" if current else "unavailable")
        if current:
            record["outcome"] = "alive" if payload["state"]["alive"] else "dead"
            if not payload["state"]["alive"]:
                record["death_cause"] = payload["state"].get("death_cause")
                record["died_age_ticks"] = age
                record["died_session_tick"] = tick
        elif "death_cause" not in record:
            record["outcome"] = "unknown"
        # Legacy rows did not store life-to-life relationships. Their engine
        # parent_grid_id is retained, but is not promoted to a cared parent ID.
        if record["outcome"] == "dead":
            record["ended_age_ticks"] = age
            record["ended_session_tick"] = tick
    return metadata, records


def validate_chronicle(metadata: dict, records: list[dict], *, grid_id: str,
                       state: dict, session_tick: int, succession_index: int,
                       event_limit: int, actions: tuple[str, ...]) -> None:
    """Reject inconsistent supported-format facts before save or resume."""
    def refuse(reason):
        raise ValueError("invalid companion chronicle: " + reason)

    def integer(value):
        return type(value) is int and value >= 0

    def identity(value):
        return isinstance(value, str) and bool(value.strip())

    if not isinstance(metadata, dict) or metadata.get("chronicle_format") != CHRONICLE_FORMAT:
        refuse("unsupported metadata")
    if (not identity(metadata.get("keeper_id")) or
            metadata.get("identity_origin") not in ("new_keeper", "legacy_snapshot") or
            metadata.get("prior_history") not in ("none", "unavailable")):
        refuse("Keeper identity or history")
    if "prior_history_reason" in metadata and not identity(metadata["prior_history_reason"]):
        refuse("prior history reason")
    if type(succession_index) is not int or not 1 <= succession_index <= len(records):
        refuse("succession index")
    if not records or any(not isinstance(row, dict) for row in records):
        refuse("lineage records")
    ids = [row.get("life_id") for row in records]
    if any(not identity(value) for value in ids) or len(set(ids)) != len(ids):
        refuse("duplicate or missing life identity")
    prefix = metadata["keeper_id"] + ":life-"
    if any(not value.startswith(prefix) or len(value) == len(prefix) for value in ids):
        refuse("life identities belong to a different Keeper")
    previous_tick = 0
    for index, row in enumerate(records):
        if not identity(row.get("grid_id")):
            refuse("life grid identity")
        for key in ("name", "origin", "prior_history_unavailable"):
            if key in row and not identity(row[key]):
                refuse("life display field")
        if row.get("learning_policy", "incumbent") not in ("incumbent", "qtable"):
            refuse("life learning policy")
        ancestry = row.get("lineage")
        if ancestry is not None:
            if not isinstance(ancestry, dict):
                refuse("recorded genetic ancestry")
            if any(ancestry.get(key) is not None and not isinstance(ancestry[key], list)
                   for key in ("ancestor_ids", "mutation_events")):
                refuse("recorded ancestor or mutation list")
        for key in ("born_session_tick", "last_age_ticks", "last_session_tick", "events_omitted"):
            if not integer(row.get(key)):
                refuse("life clock or event count")
        if not previous_tick <= row["born_session_tick"] <= row["last_session_tick"] <= session_tick:
            refuse("life ordering")
        previous_tick = row["last_session_tick"]
        outcome = row.get("outcome")
        if outcome not in ("alive", "dead", "replaced_alive", "unknown"):
            refuse("life outcome")
        if index != len(records) - 1 and outcome == "alive":
            refuse("earlier life is still active")
        if outcome == "dead":
            if (not identity(row.get("death_cause")) or
                    row.get("died_age_ticks") != row["last_age_ticks"] or
                    row.get("died_session_tick") != row["last_session_tick"]):
                refuse("death facts")
        elif any(key in row for key in ("death_cause", "died_age_ticks", "died_session_tick")):
            refuse("death recorded for a non-dead life")
        if outcome in ("dead", "replaced_alive"):
            if (row.get("ended_age_ticks") != row["last_age_ticks"] or
                    row.get("ended_session_tick") != row["last_session_tick"]):
                refuse("life ending")
        if "previous_life_id" in row and (index == 0 or row["previous_life_id"] != ids[index - 1]):
            refuse("previous life relationship")
        if "parent_life_id" in row:
            if (index == 0 or row["parent_life_id"] != ids[index - 1] or
                    row.get("origin") != "succession" or records[index - 1]["outcome"] != "dead" or
                    row.get("parent_grid_id") != records[index - 1]["grid_id"]):
                refuse("genetic life relationship")
        if "source" in row:
            source = row["source"]
            if (not isinstance(source, dict) or
                    (source.get("campaign_id") is not None and not identity(source["campaign_id"])) or
                    ("era_index" in source and not integer(source["era_index"]))):
                refuse("adoption source")
        summary = row.get("care_summary")
        if not isinstance(summary, dict) or summary.get("history") not in ("complete", "partial", "unavailable"):
            refuse("care availability")
        for key in ("from_age_ticks", "ticks_observed", "beg_requests"):
            if not integer(summary.get(key)):
                refuse("care counter")
        if (summary["from_age_ticks"] + summary["ticks_observed"] != row["last_age_ticks"] or
                summary["beg_requests"] > summary["ticks_observed"] or
                (summary["history"] == "complete" and summary["from_age_ticks"] != 0) or
                (summary["history"] == "unavailable" and summary["ticks_observed"] != 0)):
            refuse("care observation boundary")
        total = 0
        for key in ("keeper_actions", "companion_actions"):
            counts = summary.get(key)
            if (not isinstance(counts, dict) or
                    any(action not in actions or not integer(count) or count == 0
                        for action, count in counts.items())):
                refuse("care action counts")
            total += sum(counts.values())
        if total != summary["ticks_observed"]:
            refuse("care total")
        events = row.get("events")
        if (not isinstance(events, list) or len(events) > event_limit or
                len(events) + row["events_omitted"] != summary["ticks_observed"]):
            refuse("bounded events")
        start_age = summary["from_age_ticks"] + row["events_omitted"]
        tail_counts = {"keeper_actions": {}, "companion_actions": {}}
        tail_begs = 0
        for offset, event in enumerate(events, 1):
            if (not isinstance(event, dict) or event.get("tick") != start_age + offset or
                    not integer(event.get("session_tick")) or
                    event["session_tick"] != row["last_session_tick"] - len(events) + offset or
                    event.get("actor") not in ("keeper", "companion") or
                    event.get("action") not in actions or type(event.get("begging")) is not bool or
                    type(event.get("alive")) is not bool):
                refuse("observed event")
            alive = not (outcome == "dead" and offset == len(events))
            if (event["alive"] != alive or
                    event.get("death_cause") != (None if alive else row["death_cause"])):
                refuse("event outcome differs from life")
            if "life_id" in event and event["life_id"] != row["life_id"]:
                refuse("observed event belongs to a different life")
            counts = tail_counts[event["actor"] + "_actions"]
            counts[event["action"]] = counts.get(event["action"], 0) + 1
            tail_begs += int(event["begging"])
        if (tail_begs > summary["beg_requests"] or
                (row["events_omitted"] == 0 and tail_begs != summary["beg_requests"]) or
                any(count > summary[key].get(action, 0)
                    for key, counts in tail_counts.items() for action, count in counts.items())):
            refuse("event tail contradicts care totals")
    current = records[-1]
    if (current["grid_id"] != grid_id or state.get("grid_id") != grid_id or
            current["last_age_ticks"] != state["age_ticks"] or
            current["last_session_tick"] != session_tick or
            current["outcome"] != ("alive" if state["alive"] else "dead") or
            (not state["alive"] and current.get("death_cause") != state.get("death_cause"))):
        refuse("active life differs from saved companion")
    campaign_id = metadata.get("campaign_id")
    links = metadata.get("campaign_links")
    if (campaign_id is not None and not identity(campaign_id)) or not isinstance(links, list):
        refuse("campaign association")
    previous_campaign = None
    previous_tick = 0
    for link in links:
        if (not isinstance(link, dict) or not identity(link.get("campaign_id")) or
                link.get("life_id") not in ids or not integer(link.get("session_tick")) or
                not previous_tick <= link["session_tick"] <= session_tick or
                link.get("predecessor_campaign_id") != previous_campaign or
                ("campaign_predecessor_id" in link and not identity(link["campaign_predecessor_id"]))):
            refuse("campaign relationship")
        previous_campaign = link["campaign_id"]
        previous_tick = link["session_tick"]
    if campaign_id != previous_campaign:
        refuse("active campaign relationship")
