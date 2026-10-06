"""X7 immutable, factual care tapes, separate from genome and learned state.

The retained tail is a bounded observation window, never a reconstructed life.
Contextual evaluation is an explicitly named stress test, not inherited memory.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math

from mecha_engine.lifecycle import ACTIONS

CARE_FORMAT = "keeper_care_context_v1"
CARE_POLICY = "observed_care_selection_v1"
CARE_POLICY_V2 = "observed_care_selection_v2"
CARE_POLICIES = (CARE_POLICY, CARE_POLICY_V2)
CARE_EVALUATORS = ("archive_morphology_probe_v1", "pristine")
CARE_EVENT_LIMIT = 100
EVENT_FIELDS = ("tick", "session_tick", "actor", "action", "begging", "alive", "death_cause")


def care_grid_digest(grid):
    """Canonical JSON identity; matches storage and the engine care helper."""
    return hashlib.sha256(json.dumps(grid, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode("utf-8")).hexdigest()


def care_structure_digest(grid):
    from mecha_engine.runtime.care import care_structure_sha256
    return care_structure_sha256(grid)


def validate_care_configuration(policy, evaluator):
    if policy not in ("off", *CARE_POLICIES):
        raise ValueError("care selection policy must be off or " + " or ".join(CARE_POLICIES))
    if evaluator not in CARE_EVALUATORS:
        raise ValueError("unsupported care evaluator")


def capture_care_context(session):
    """Freeze a validated actual life before staging or selecting its child."""
    session._validate_chronicle()
    life = session.lineage[-1]
    context = dict(format=CARE_FORMAT, keeper_id=session.keeper_id,
        life_id=life["life_id"], grid_id=session.grid["grid_id"],
        grid_sha256=care_grid_digest(session.grid), care_summary=copy.deepcopy(life["care_summary"]),
        events=[{key: copy.deepcopy(event[key]) for key in EVENT_FIELDS} for event in life["events"]],
        events_omitted=life["events_omitted"], last_age_ticks=life["last_age_ticks"],
        last_session_tick=life["last_session_tick"], outcome=life["outcome"])
    if session.body_response != "legacy": context["body_response"] = session.body_response
    return validate_care_context(context)


def validate_care_context(context, *, keeper_id=None, life_id=None, grid_id=None, grid=None):
    """Validate exact summary/tail semantics and optional source association."""
    from mecha_engine.runtime.care import validate_care_context as validate_engine_context
    try:
        context = validate_engine_context(context)
    except (TypeError, KeyError, AttributeError) as error:
        raise ValueError("invalid care context: malformed evidence") from error
    def refuse(reason):
        raise ValueError("invalid care context: " + reason)
    def integer(value):
        return type(value) is int and value >= 0
    def text(value):
        return isinstance(value, str) and bool(value.strip())
    def digest(value):
        return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)
    keys = {"format", "keeper_id", "life_id", "grid_id", "grid_sha256", "care_summary", "events",
            "events_omitted", "last_age_ticks", "last_session_tick", "outcome"}
    from mecha_game.body_response import saved_body_response
    model = saved_body_response(context)
    if model != "legacy": keys.add("body_response")
    if not isinstance(context, dict) or set(context) != keys or context.get("format") != CARE_FORMAT:
        refuse("unsupported format or fields")
    if any(not text(context[key]) for key in ("keeper_id", "life_id", "grid_id")):
        refuse("missing source identity")
    prefix = context["keeper_id"] + ":life-"
    if (not context["life_id"].startswith(prefix) or len(context["life_id"]) == len(prefix) or
            not digest(context["grid_sha256"])):
        refuse("life or genome identity")
    for key, expected in (("keeper_id", keeper_id), ("life_id", life_id), ("grid_id", grid_id)):
        if expected is not None and context[key] != expected:
            refuse("source " + key + " disagrees")
    if grid is not None and (context["grid_id"] != grid.get("grid_id") or context["grid_sha256"] != care_grid_digest(grid)):
        refuse("source genome disagrees")
    if any(not integer(context[key]) for key in ("events_omitted", "last_age_ticks", "last_session_tick")):
        refuse("invalid observation clocks")
    if context["last_session_tick"] < context["last_age_ticks"]:
        refuse("session clock precedes age")
    outcome = context["outcome"]
    if outcome not in ("alive", "dead", "replaced_alive", "unknown"):
        refuse("invalid outcome")
    summary = context["care_summary"]
    expected_summary = {"history", "from_age_ticks", "ticks_observed", "keeper_actions", "companion_actions", "beg_requests"}
    if not isinstance(summary, dict) or set(summary) != expected_summary or summary["history"] not in ("complete", "partial", "unavailable"):
        refuse("invalid care availability")
    if any(not integer(summary[key]) for key in ("from_age_ticks", "ticks_observed", "beg_requests")):
        refuse("invalid care counters")
    ticks = summary["ticks_observed"]
    if (summary["from_age_ticks"] + ticks != context["last_age_ticks"] or
            summary["beg_requests"] > ticks or
            (summary["history"] == "complete" and summary["from_age_ticks"] != 0) or
            (summary["history"] == "unavailable" and ticks != 0)):
        refuse("invalid observation boundary")
    actions = (*ACTIONS, "clean")
    for key in ("keeper_actions", "companion_actions"):
        counts = summary[key]
        if not isinstance(counts, dict) or any(action not in actions or not integer(count) or count == 0 for action, count in counts.items()):
            refuse("invalid action totals")
    if any(action in summary["companion_actions"] for action in ("feed", "clean")):
        refuse("companion care totals claim keeper-only actions")
    if sum(sum(summary[key].values()) for key in ("keeper_actions", "companion_actions")) != ticks:
        refuse("action totals differ from observed ticks")
    events = context["events"]
    if not isinstance(events, list) or len(events) > CARE_EVENT_LIMIT or len(events) + context["events_omitted"] != ticks:
        refuse("invalid retained event window")
    tail_counts = {"keeper_actions": {}, "companion_actions": {}}
    tail_begs = 0
    for index, event in enumerate(events, 1):
        if (not isinstance(event, dict) or set(event) != set(EVENT_FIELDS) or
                type(event["tick"]) is not int or type(event["session_tick"]) is not int or
                event["tick"] != context["last_age_ticks"] - len(events) + index or
                event["session_tick"] != context["last_session_tick"] - len(events) + index or
                event["actor"] not in ("keeper", "companion") or event["action"] not in actions or
                type(event["begging"]) is not bool or type(event["alive"]) is not bool):
            refuse("invalid observed event")
        alive = not (outcome == "dead" and index == len(events))
        if event["alive"] != alive or (event["death_cause"] is not None if alive else not text(event["death_cause"])):
            refuse("event outcome disagrees")
        if event["actor"] == "companion" and event["action"] in ("feed", "clean"):
            refuse("companion cannot feed or clean itself")
        counts = tail_counts[event["actor"] + "_actions"]
        counts[event["action"]] = counts.get(event["action"], 0) + 1
        tail_begs += int(event["begging"])
    if tail_begs > summary["beg_requests"] or any(count > summary[key].get(action, 0)
            for key, counts in tail_counts.items() for action, count in counts.items()):
        refuse("event tail contradicts care totals")
    if context["events_omitted"] == 0 and (tail_begs != summary["beg_requests"] or
            any(tail_counts[key] != summary[key] for key in tail_counts)):
        refuse("complete event window contradicts care totals")
    return copy.deepcopy(context)


def validate_care_selection(selection, *, parent_record, child_grid=None, child_record=None):
    """Check a factual parent tape and complete stored trial outcome, without rerunning it."""
    def refuse(reason):
        raise ValueError("invalid care selection: " + reason)
    def digest(value):
        return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)
    if not isinstance(selection, dict) or set(selection) != {"context", "receipt"}:
        refuse("invalid evidence fields")
    context = validate_care_context(selection["context"], life_id=parent_record["life_id"],
                                    grid_id=parent_record["grid_id"])
    from mecha_game.body_response import saved_body_response
    model = saved_body_response(context)
    if model != saved_body_response(parent_record): refuse("parent body response differs from care context")
    if child_record is not None and model != saved_body_response(child_record): refuse("child body response differs from care selection")
    expected_events = [{key: event[key] for key in EVENT_FIELDS} for event in parent_record["events"]]
    if (context["events"] != expected_events or
            any(context[key] != parent_record[key] for key in
                ("care_summary", "events_omitted", "last_age_ticks", "last_session_tick", "outcome")) or
            ("grid_sha256" in parent_record and context["grid_sha256"] != parent_record["grid_sha256"])):
        refuse("context differs from the actual parent's care or body")
    receipt = selection["receipt"]
    fields = {"policy", "evaluator", "context_sha256", "observed_window", "pool_size", "selected_index",
              "selected_grid_sha256", "selected_structure_sha256", "candidates"}
    version_two = isinstance(receipt, dict) and receipt.get("policy") == CARE_POLICY_V2
    if version_two:
        fields |= {"selection_order", "source_identity"}
    if model != "legacy": fields.add("body_response")
    if saved_body_response(receipt) != model: refuse("receipt body response differs from source context")
    if not isinstance(receipt, dict) or set(receipt) != fields or not context["events"]:
        refuse("invalid receipt fields or empty source window")
    validate_care_configuration(receipt["policy"], receipt["evaluator"])
    if receipt["policy"] not in CARE_POLICIES or receipt["context_sha256"] != care_grid_digest(context):
        refuse("policy or context hash disagrees")
    if version_two and (receipt["selection_order"] != ["terminal_survival", "need_balance", "survival_ticks", "earliest_index"]
            or receipt["source_identity"] != {key: context[key] for key in ("keeper_id", "life_id", "grid_id", "grid_sha256")}):
        refuse("versioned order or source identity disagrees")
    selected = receipt["selected_index"]
    candidates = receipt["candidates"]
    if (type(receipt["pool_size"]) is not int or receipt["pool_size"] != 8 or
            type(selected) is not int or not 0 <= selected < 8 or
            not isinstance(candidates, list) or len(candidates) != 8):
        refuse("invalid candidate pool")
    events = context["events"]
    first, last = events[0], events[-1]
    window = {"first_age_tick": first["tick"], "last_age_tick": last["tick"],
              "first_session_tick": first["session_tick"], "last_session_tick": last["session_tick"],
              "ticks": len(events), "events_omitted": context["events_omitted"]}
    if receipt["observed_window"] != window or any(type(value) is not int for value in receipt["observed_window"].values()):
        refuse("observed window differs from source tape")
    candidate_fields = {"index", "rng_seed", "grid_id", "grid_sha256", "structure_sha256",
                        "need_balance", "survival_ticks", "alive", "death_cause"}
    if version_two:
        candidate_fields |= {"terminal_survival", "episode"}
    if model != "legacy": candidate_fields |= {"candidate_grid", "episode"}
    first_seed = None
    for index, row in enumerate(candidates):
        if (not isinstance(row, dict) or set(row) != candidate_fields or
                type(row["index"]) is not int or row["index"] != index or type(row["rng_seed"]) is not int or
                not isinstance(row["grid_id"], str) or not row["grid_id"].strip() or
                not digest(row["grid_sha256"]) or not digest(row["structure_sha256"]) or
                type(row["need_balance"]) not in (int, float) or not math.isfinite(row["need_balance"]) or
                not 0 <= row["need_balance"] <= 1 or type(row["survival_ticks"]) is not int or
                not 1 <= row["survival_ticks"] <= len(events) or type(row["alive"]) is not bool):
            refuse("invalid candidate row")
        if model != "legacy":
            candidate = row["candidate_grid"]
            if (not isinstance(candidate, dict) or candidate.get("grid_id") != row["grid_id"]
                    or care_grid_digest(candidate) != row["grid_sha256"]
                    or care_structure_digest(candidate) != row["structure_sha256"]):
                refuse("candidate body differs from its immutable hashes")
            from mecha_engine.lifecycle import initial_state
            from mecha_engine.archive import lifecycle_probe_grid
            evaluated = lifecycle_probe_grid(candidate) if receipt["evaluator"] == "archive_morphology_probe_v1" else candidate
            expected_workload = initial_state(evaluated, body_response=model)["body_workload"]
            episode = row["episode"]
            if (not isinstance(episode, dict) or saved_body_response(episode) != model
                    or episode.get("body_workload") != expected_workload):
                refuse("candidate episode workload differs from its actual evaluated body")
        if first_seed is None:
            first_seed = row["rng_seed"]
        if row["rng_seed"] != first_seed + index:
            refuse("candidate seeds do not follow the fixed pool")
        if row["alive"]:
            if row["survival_ticks"] != len(events) or row["death_cause"] is not None:
                refuse("surviving candidate outcome disagrees")
        elif not isinstance(row["death_cause"], str) or not row["death_cause"].strip():
            refuse("dead candidate lacks a death cause")
        if version_two or model != "legacy":
            try:
                _validate_care_v2_episode(row, receipt, context)
            except (TypeError, KeyError, AttributeError, OverflowError) as error:
                raise ValueError("invalid care selection: malformed v2 trajectory") from error
    def rank(index):
        row = candidates[index]
        legacy = (row["need_balance"], row["survival_ticks"], -index)
        return (row["terminal_survival"], *legacy) if version_two else legacy
    winner = max(range(8), key=rank)
    if (selected != winner or receipt["selected_grid_sha256"] != candidates[selected]["grid_sha256"] or
            receipt["selected_structure_sha256"] != candidates[selected]["structure_sha256"]):
        refuse("selected candidate disagrees with rank or hashes")
    if child_grid is not None and (care_grid_digest(child_grid) != receipt["selected_grid_sha256"] or
            care_structure_digest(child_grid) != receipt["selected_structure_sha256"]):
        refuse("selected child differs from its actual body")
    if child_record is not None and (child_record.get("grid_sha256") != receipt["selected_grid_sha256"] or
            child_record.get("grid_structure_sha256") != receipt["selected_structure_sha256"]):
        refuse("selected child differs from its recorded body")


def _validate_care_v2_episode(row, receipt, context):
    """Bind complete stored evidence; loading never reruns candidate simulation.

    These are schema and internal-consistency checks, not authentication of an
    externally authored history. Explicit immutable-era reproduction is the
    independent computation check.
    """
    from collections import Counter

    def refuse(reason):
        raise ValueError("invalid care selection: v2 " + reason)

    def equal(left, right):
        # JSON equality also distinguishes booleans from numeric counters.
        return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(right, sort_keys=True, allow_nan=False)

    def probability(value):
        return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1

    try:
        care_grid_digest(row)
    except (TypeError, ValueError):
        refuse("episode contains non-finite or non-JSON evidence")
    episode = row["episode"]
    version_two = receipt["policy"] == CARE_POLICY_V2
    fields = {"policy", "evaluator", "ticks_requested", "survival_ticks", "alive", "death_cause",
              "need_balance", "recovery_events", "action_counts", "keeper_actions", "beg_requests",
              "final_state", "history", "initial_state", "trajectory"}
    if version_two: fields.add("terminal_survival")
    from mecha_game.body_response import saved_body_response
    model = saved_body_response(receipt)
    if model != "legacy": fields |= {"body_response", "body_workload"}
    if saved_body_response(episode) != model: refuse("episode body response differs from receipt")
    if not isinstance(episode, dict) or set(episode) != fields:
        refuse("episode fields")
    horizon, elapsed = len(context["events"]), row["survival_ticks"]
    compared = ("need_balance", "survival_ticks", "alive", "death_cause") + (("terminal_survival",) if version_two else ())
    if (episode["policy"] != receipt["policy"] or episode["evaluator"] != receipt["evaluator"]
            or type(episode["ticks_requested"]) is not int or episode["ticks_requested"] != horizon
            or any(not equal(episode[key], row[key]) for key in compared)
            or version_two and (type(row["terminal_survival"]) is not bool
                or row["terminal_survival"] != (row["alive"] and elapsed == horizon))):
        refuse("candidate, requested horizon or terminal summary disagrees")
    history, trajectory = episode["history"], episode["trajectory"]
    start, finish = episode["initial_state"], episode["final_state"]
    if (not isinstance(history, list) or not isinstance(trajectory, list)
            or len(history) != elapsed or len(trajectory) != elapsed
            or not isinstance(start, dict) or not isinstance(finish, dict)):
        refuse("complete trajectory and states required")
    if (type(start.get("age_ticks")) is not int or start["age_ticks"] != 0
            or start.get("alive") is not True or start.get("death_cause") is not None
            or start.get("history") != [] or start.get("grid_id") != row["grid_id"]
            or start.get("recovery_events") != 0 or "thread_states" in start
            or start.get("learning_switches", {}).get("qtable_policy") is not False
            or start.get("learning_switches", {}).get("qtable_consumer") is not False):
        refuse("evaluation must start cold and alive")
    if model != "legacy":
        from mecha_engine.lifecycle import initial_state
        from mecha_engine.archive import lifecycle_probe_grid
        candidate = row["candidate_grid"]
        evaluated = lifecycle_probe_grid(candidate) if receipt["evaluator"] == "archive_morphology_probe_v1" else candidate
        expected_workload = initial_state(evaluated, body_response=model)["body_workload"]
        if not equal(episode.get("body_workload"), expected_workload) or not equal(start.get("body_workload"), expected_workload):
            refuse("workload differs from the actual evaluated candidate body")
    for state in (start, finish):
        if saved_body_response(state) != model: refuse("state body response differs from episode")
    if model != "legacy" and start.get("body_workload") != finish.get("body_workload"):
        refuse("fixed body workload changed within the episode")
    cleanliness_on = "cleanliness" in start
    if (cleanliness_on and not probability(start["cleanliness"])
            or ("cleanliness" in finish) != cleanliness_on
            or cleanliness_on and not probability(finish["cleanliness"])):
        refuse("invalid optional cleanliness state")
    actions = (*ACTIONS, "clean")
    counts = start.get("action_counts")
    if not isinstance(counts, dict) or set(counts) != set(ACTIONS) or any(type(n) is not int or n != 0 for n in counts.values()):
        refuse("evaluation action counts must start cold")
    counts = dict(counts)
    keeper_counts = Counter()
    begging_count = recovery_count = 0
    axes = ("hunger", "energy", "stress", "bond", "grid_stability")
    previous_snapshot = {key: start.get(key) for key in axes}
    if any(not probability(value) for value in previous_snapshot.values()):
        refuse("invalid initial physiology")
    trajectory_fields = {"evaluation_tick", "source_actor", "source_action", "decision_state",
                         "recommendation", "recommended_thought", "begging", "applied_action",
                         "applied_thought", "result"}
    history_fields = {"tick", "action", "balance", "recoveries", "alive", "death_cause", "state"}
    for index, (step, result, source) in enumerate(zip(trajectory, history, context["events"]), 1):
        if (not isinstance(step, dict) or set(step) != trajectory_fields
                or type(step["evaluation_tick"]) is not int or step["evaluation_tick"] != index
                or step["source_actor"] != source["actor"] or step["source_action"] != source["action"]
                or not equal(step["result"], result)):
            refuse("trajectory clock, source action or history disagrees")
        state = step["decision_state"]
        if (not isinstance(state, dict) or type(state.get("age_ticks")) is not int
                or state["age_ticks"] != index - 1 or state.get("alive") is not True
                or state.get("death_cause") is not None or state.get("grid_id") != row["grid_id"]
                or not equal({key: state.get(key) for key in axes}, previous_snapshot)
                or not equal(state.get("action_counts"), counts)
                or not equal(state.get("recovery_events"), recovery_count)):
            refuse("decision state does not continue the prior tick")
        if (("cleanliness" in state) != cleanliness_on
                or cleanliness_on and (not probability(state["cleanliness"])
                    or index == 1 and not equal(state["cleanliness"], start["cleanliness"]))):
            refuse("optional cleanliness observation disagrees")
        if saved_body_response(state) != model or (model != "legacy" and state.get("body_workload") != start.get("body_workload")):
            refuse("decision workload differs from initial body")
        if model != "legacy" and any(not equal(state.get(key), start.get(key)) for key in ("neediness", "sleepiness", "curiosity")):
            refuse("species physiology changed within the fixed-body episode")
        recommendation, action = step["recommendation"], step["applied_action"]
        if action == "clean" and not cleanliness_on:
            refuse("clean action requires the optional cleanliness state")
        if (recommendation not in ACTIONS or action not in actions or type(step["begging"]) is not bool
                or step["begging"] != (recommendation == "feed")
                or step["recommended_thought"] is not None and not isinstance(step["recommended_thought"], dict)):
            refuse("invalid recommendation or begging")
        expected_action = source["action"] if source["actor"] == "keeper" else ("idle" if step["begging"] else recommendation)
        expected_thought = None if source["actor"] == "keeper" else step["recommended_thought"]
        if action != expected_action or not equal(step["applied_thought"], expected_thought):
            refuse("applied care differs from the actual source action")
        expected_fields = history_fields | ({"deliberation"} if expected_thought is not None else set())
        if model != "legacy":
            expected_fields |= {"body_response", "play_energy_cost", "action_energy_effect"}
            effects = {"play": -start["body_workload"]["play_energy_cost"], "feed": .01, "sleep": .34, "idle": -.012, "mutate": -.045, "clean": 0.0}
            if (saved_body_response(result) != model or not equal(result.get("play_energy_cost"), expected_workload["play_energy_cost"])
                    or not equal(result.get("action_energy_effect"), effects[action])):
                refuse("tick body model or applied energy effect differs")
            sleepiness = state.get("sleepiness")
            if not probability(sleepiness): refuse("invalid species sleepiness")
            expected_energy = round(max(0.0, min(1.0, state["energy"] - (0.022 + sleepiness * 0.012) + effects[action])), 6)
            if not isinstance(result.get("state"), dict) or not equal(result["state"].get("energy"), expected_energy):
                refuse("actual energy transition differs from the body's applied workload")
        if (not isinstance(result, dict) or set(result) != expected_fields
                or type(result["tick"]) is not int or result["tick"] != index or result["action"] != action
                or not probability(result["balance"]) or not equal(result.get("deliberation"), expected_thought)
                or type(result["alive"]) is not bool or not isinstance(result["recoveries"], list)
                or len(set(result["recoveries"])) != len(result["recoveries"])
                or any(key not in axes for key in result["recoveries"])
                or not isinstance(result["state"], dict) or set(result["state"]) != set(axes)
                or any(not probability(value) for value in result["state"].values())):
            refuse("invalid tick result")
        expected_alive = index != elapsed or row["alive"]
        if result["alive"] != expected_alive or result["death_cause"] != (None if expected_alive else row["death_cause"]):
            refuse("trajectory terminal outcome disagrees or continues after death")
        counts[action] = counts.get(action, 0) + 1
        if source["actor"] == "keeper":
            keeper_counts[action] += 1
        begging_count += int(step["begging"])
        recovery_count += len(result["recoveries"])
        previous_snapshot = result["state"]
    if model != "legacy" and any(not equal(finish.get(key), start.get(key)) for key in ("neediness", "sleepiness", "curiosity")):
        refuse("final species physiology differs")
    if (any(not equal(finish.get(key), episode[key]) for key in ("alive", "death_cause", "action_counts", "recovery_events"))
            or type(finish.get("age_ticks")) is not int or finish["age_ticks"] != elapsed
            or finish.get("grid_id") != row["grid_id"] or not equal(finish.get("history"), history[-32:])
            or not equal({key: finish.get(key) for key in axes}, previous_snapshot)
            or not equal(episode["action_counts"], counts) or not equal(episode["keeper_actions"], dict(keeper_counts))
            or not equal(episode["beg_requests"], begging_count) or not equal(episode["recovery_events"], recovery_count)
            or episode["need_balance"] != round(sum(item["balance"] for item in history) / horizon, 6)):
        refuse("final state, counters or horizon welfare disagrees")

