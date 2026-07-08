"""The micro-thread fleet for mecha_engine.learning (cycle 12 D1/D2).

Verbatim twin of the shared sections of
``labs/micro_threads/thread_fleet.py`` (regenerated mechanically from
the lab module; the lab-side seam tests pin lab decision == package
decision, opted-in and frozen). See the lab module for the contract
prose. THE OPT-IN RULE is load-bearing: fleet threads run only on an
explicit ``learning_switches[name] is True``, so every frozen path is
byte-identical until a profile opts in.
"""

from __future__ import annotations

HISTORY_LIMIT = 8
FEED_ANTICIPATION_FLOOR = 0.55
# estimate_hidden_mood flips to "tired" strictly below energy 0.2; the
# sleep predictor speaks when the FORECAST drops below this ceiling.
SLEEP_ANTICIPATION_CEILING = 0.30
ACTION_WINDOW = 8
ATTENTION_TRIALS_FLOOR = 20
ATTENTION_BUCKETS = 10
GAP_ALPHA = 0.3
GAP_COUNT_FLOOR = 5
# Decayed-count learners stay bounded at 1/(1-decay) = 50 trials.
COUNT_DECAY = 0.98
ERROR_EWMA_ALPHA = 0.3
DELTA_ALPHA = 0.3
VALUE_BUCKETS = 10
# Hierarchical smoothing: bucket estimates shrink toward the thread's
# own global rate with this pseudo-count strength.
SMOOTHING_STRENGTH = 2.0
# Confidence for the value forecasters is SELF-ASSESSED skill measured
# PER BUCKET: 1 - sensitivity x the bucket's own realized-error EWMA
# (spiky regimes keep honestly low confidence; drift regimes earn high).
TREND_ERROR_SENSITIVITY = 4.0


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def _trend_prediction(history: list[float]) -> tuple[float, float] | None:
    """Median-delta trend: robust to action discontinuities (feed/sleep
    spikes), so the slope tracks the lifecycle drift the spikes ride on."""
    if len(history) < 2:
        return None
    deltas = [
        round(current - previous, 6)
        for previous, current in zip(history, history[1:])
    ]
    slope = _median(deltas)
    return _clamp(history[-1] + slope), slope


def _value_bucket(value: float) -> str:
    return str(min(VALUE_BUCKETS - 1, int(_clamp(value) * VALUE_BUCKETS)))


def _conditional_prediction(
    history: list[float], means: dict, trials: dict
) -> float | None:
    """The learned conditional-delta model: at the current need level's
    bucket, the decayed mean of the engine's own observed next-tick
    deltas (which learns e.g. that high hunger attracts feeds); unseen
    buckets fall back to the median-delta trend."""
    if len(history) < 2:
        return None
    current = history[-1]
    bucket = _value_bucket(current)
    mean = means.get(bucket)
    if mean is not None and float(trials.get(bucket, 0.0)) >= 2.0:
        return _clamp(current + float(mean))
    trend = _trend_prediction(history)
    return trend[0] if trend is not None else None


def _smoothed_probability(
    trials: dict, hits: dict, key: str, fallback_rate: float
) -> float:
    observed = float(trials.get(key, 0.0))
    positive = float(hits.get(key, 0.0))
    return (positive + SMOOTHING_STRENGTH * fallback_rate) / (
        observed + SMOOTHING_STRENGTH
    )


def _updated_error_ewma(error_ewma: object, error: float) -> float:
    if error_ewma is None:
        return round(error, 6)
    return round(
        (1 - ERROR_EWMA_ALPHA) * float(error_ewma) + ERROR_EWMA_ALPHA * error, 6
    )


def _skill(error_ewma: object, sensitivity: float) -> float:
    if error_ewma is None:
        return 1.0
    return max(0.0, 1.0 - sensitivity * float(error_ewma))


def _sharpness_confidence(probability: float) -> float:
    """A calibrated binary predictor's expected Brier error IS
    p(1-p) — sharpness is the honest confidence statement, scaled so
    a coin-flip prediction is 0 and a certain one is 1."""
    return max(0.0, 1.0 - 4.0 * probability * (1.0 - probability))


def _need_forecast_observe(
    thread_state: dict, lifecycle_state: dict, field: str
) -> dict:
    history = list(thread_state.get("history", []))
    current = _clamp(lifecycle_state.get(field, 0.5))
    means = dict(thread_state.get("bucket_mean_delta") or {})
    errors = dict(thread_state.get("bucket_error_ewma") or {})
    trials = dict(thread_state.get("bucket_trials") or {})
    if history:
        previous = history[-1]
        bucket = _value_bucket(previous)
        predicted = _conditional_prediction(history, means, trials)
        if predicted is not None:
            errors[bucket] = _updated_error_ewma(
                errors.get(bucket), abs(predicted - current)
            )
        delta = round(current - previous, 6)
        mean = means.get(bucket)
        means[bucket] = round(
            delta
            if mean is None
            else (1 - DELTA_ALPHA) * float(mean) + DELTA_ALPHA * delta,
            6,
        )
        trials[bucket] = round(
            COUNT_DECAY * float(trials.get(bucket, 0.0)) + 1.0, 6
        )
    history.append(current)
    return {
        "history": history[-HISTORY_LIMIT:],
        "bucket_mean_delta": means,
        "bucket_error_ewma": errors,
        "bucket_trials": trials,
    }


def _need_forecast_signal(
    thread_state: dict, name: str, field: str
) -> tuple[dict | None, float, float]:
    """Shared forecast machinery: (cold-start thread | None, predicted, confidence)."""
    history = thread_state.get("history", [])
    predicted = _conditional_prediction(
        history,
        thread_state.get("bucket_mean_delta") or {},
        thread_state.get("bucket_trials") or {},
    )
    if predicted is None:
        cold = _thread(
            name,
            {"history_length": len(history)},
            {f"predicted_{field}": None},
            0.0,
            f"Cold start: no {field} trend observed yet.",
            {},
        )
        return cold, 0.0, 0.0
    fill = min(1.0, len(history) / HISTORY_LIMIT)
    bucket_error = (thread_state.get("bucket_error_ewma") or {}).get(
        _value_bucket(history[-1])
    )
    confidence = round(
        fill * _skill(bucket_error, TREND_ERROR_SENSITIVITY), 6
    )
    return None, predicted, confidence


def hunger_forecast_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    return _need_forecast_observe(thread_state, lifecycle_state, "hunger")


def hunger_forecast_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    cold, predicted, confidence = _need_forecast_signal(
        thread_state, "hunger_forecast", "hunger"
    )
    if cold is not None:
        return cold
    history = thread_state.get("history", [])
    anticipation = max(0.0, predicted - FEED_ANTICIPATION_FLOOR)
    effects = {}
    if anticipation > 0:
        effects["feed"] = round(anticipation * 0.5, 6)
    return _thread(
        "hunger_forecast",
        {"history_length": len(history), "last_hunger": history[-1]},
        {"predicted_hunger": round(predicted, 6)},
        confidence,
        "Hunger trend forecast; anticipatory feeding before the reactive threshold.",
        effects,
    )


def energy_forecast_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    return _need_forecast_observe(thread_state, lifecycle_state, "energy")


def energy_forecast_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    cold, predicted, confidence = _need_forecast_signal(
        thread_state, "energy_forecast", "energy"
    )
    if cold is not None:
        return cold
    history = thread_state.get("history", [])
    shortfall = max(0.0, SLEEP_ANTICIPATION_CEILING - predicted)
    effects = {}
    if shortfall > 0:
        effects["sleep"] = round(shortfall * 0.5, 6)
    return _thread(
        "energy_forecast",
        {"history_length": len(history), "last_energy": history[-1]},
        {"predicted_energy": round(predicted, 6)},
        confidence,
        "Energy trend forecast; anticipatory sleep before the reactive threshold.",
        effects,
    )


def boredom_novelty_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    """Infers the last action from the engine's own action_counts ledger
    (exactly one count increments per tick; sorted iteration keeps the
    inference deterministic even on a malformed multi-increment state),
    then learns per-action repeat propensity with decayed counts."""
    counts = lifecycle_state.get("action_counts") or {}
    seen = thread_state.get("counts") or {}
    last_action = None
    for action in sorted(counts):
        if int(counts.get(action, 0)) > int(seen.get(action, 0)):
            last_action = action
            break
    window = list(thread_state.get("recent_actions", []))
    trials = dict(thread_state.get("repeat_trials") or {})
    hits = dict(thread_state.get("repeat_hits") or {})
    global_trials = float(thread_state.get("global_trials", 0.0))
    global_hits = float(thread_state.get("global_hits", 0.0))
    if last_action is not None:
        previous = window[-1] if window else None
        if previous is not None:
            outcome = 1.0 if last_action == previous else 0.0
            trials[previous] = round(
                COUNT_DECAY * float(trials.get(previous, 0.0)) + 1.0, 6
            )
            hits[previous] = round(
                COUNT_DECAY * float(hits.get(previous, 0.0)) + outcome, 6
            )
            global_trials = round(COUNT_DECAY * global_trials + 1.0, 6)
            global_hits = round(COUNT_DECAY * global_hits + outcome, 6)
        window.append(last_action)
    return {
        "counts": {action: int(counts[action]) for action in sorted(counts)},
        "recent_actions": window[-ACTION_WINDOW:],
        "repeat_trials": trials,
        "repeat_hits": hits,
        "global_trials": global_trials,
        "global_hits": global_hits,
    }


def boredom_novelty_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    window = thread_state.get("recent_actions", [])
    if len(window) < 3:
        return _thread(
            "boredom_novelty",
            {"window_length": len(window)},
            {"boredom": None, "predicted_repeat_probability": None},
            0.0,
            "Cold start: no action stream observed yet.",
            {},
        )
    last_action = window[-1]
    global_trials = float(thread_state.get("global_trials", 0.0))
    global_rate = (
        (float(thread_state.get("global_hits", 0.0)) + 0.5)
        / (global_trials + 1.0)
    )
    predicted_repeat = _clamp(
        _smoothed_probability(
            thread_state.get("repeat_trials") or {},
            thread_state.get("repeat_hits") or {},
            last_action,
            global_rate,
        )
    )
    novelty = len(set(window)) / len(window)
    boredom = round(_clamp(1.0 - novelty), 6)
    confidence = round(
        min(1.0, len(window) / ACTION_WINDOW)
        * _sharpness_confidence(predicted_repeat),
        6,
    )
    effects = {}
    if boredom > 0:
        effects["play"] = round(boredom * 0.15, 6)
    return _thread(
        "boredom_novelty",
        {"window_length": len(window), "last_action": last_action},
        {
            "boredom": boredom,
            "predicted_repeat_probability": round(predicted_repeat, 6),
        },
        confidence,
        "Novelty decay over the companion's own action stream; boredom seeks play.",
        effects,
    )


def attention_forecast_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    """An online hazard model: P(interaction | ticks since the last one),
    learned per bucket with decayed counts from the companion's own
    recent_interactions stream."""
    interactions = lifecycle_state.get("recent_interactions") or []
    if not interactions:
        return dict(thread_state)
    outcome = 1 if _clamp(interactions[-1]) > 0 else 0
    bucket = str(min(int(thread_state.get("ticks_since", 0)), ATTENTION_BUCKETS - 1))
    trials = dict(thread_state.get("bucket_trials") or {})
    hits = dict(thread_state.get("bucket_hits") or {})
    trials[bucket] = round(COUNT_DECAY * float(trials.get(bucket, 0.0)) + 1.0, 6)
    hits[bucket] = round(COUNT_DECAY * float(hits.get(bucket, 0.0)) + outcome, 6)
    ticks_since = (
        0
        if outcome
        else min(int(thread_state.get("ticks_since", 0)) + 1, ATTENTION_BUCKETS - 1)
    )
    return {
        "bucket_trials": trials,
        "bucket_hits": hits,
        "global_trials": round(
            COUNT_DECAY * float(thread_state.get("global_trials", 0.0)) + 1.0, 6
        ),
        "global_hits": round(
            COUNT_DECAY * float(thread_state.get("global_hits", 0.0)) + outcome, 6
        ),
        "ticks_since": ticks_since,
        "observations": min(int(thread_state.get("observations", 0)) + 1, 60),
    }


def attention_forecast_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    observations = int(thread_state.get("observations", 0))
    if observations == 0:
        return _thread(
            "attention_forecast",
            {"observations": 0},
            {"predicted_interaction_probability": None},
            0.0,
            "Cold start: no attention history observed yet.",
            {},
        )
    ticks_since = int(thread_state.get("ticks_since", 0))
    bucket = str(min(ticks_since, ATTENTION_BUCKETS - 1))
    global_trials = float(thread_state.get("global_trials", 0.0))
    global_rate = (
        (float(thread_state.get("global_hits", 0.0)) + 0.5)
        / (global_trials + 1.0)
    )
    probability = _clamp(
        _smoothed_probability(
            thread_state.get("bucket_trials") or {},
            thread_state.get("bucket_hits") or {},
            bucket,
            global_rate,
        )
    )
    confidence = round(
        min(1.0, observations / ATTENTION_TRIALS_FLOOR)
        * _sharpness_confidence(probability),
        6,
    )
    effects = {}
    if probability > 0:
        effects["play"] = round(probability * 0.15, 6)
    return _thread(
        "attention_forecast",
        {"observations": observations, "ticks_since_interaction": ticks_since},
        {"predicted_interaction_probability": round(probability, 6)},
        confidence,
        "Interaction-hazard estimate predicts near-term user attention.",
        effects,
    )


def interaction_timing_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    interactions = lifecycle_state.get("recent_interactions") or []
    latest = 1 if (interactions and _clamp(interactions[-1]) > 0) else 0
    ticks_since = int(thread_state.get("ticks_since", 0))
    mean_gap = thread_state.get("mean_gap")
    gaps_seen = int(thread_state.get("gaps_seen", 0))
    if latest:
        gap = ticks_since + 1
        mean_gap = (
            float(gap)
            if mean_gap is None
            else round((1 - GAP_ALPHA) * float(mean_gap) + GAP_ALPHA * gap, 6)
        )
        gaps_seen = min(gaps_seen + 1, 50)
        ticks_since = 0
    else:
        ticks_since += 1
    updated = {"ticks_since": ticks_since, "gaps_seen": gaps_seen}
    if mean_gap is not None:
        updated["mean_gap"] = mean_gap
    return updated


def interaction_timing_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    gaps_seen = int(thread_state.get("gaps_seen", 0))
    if gaps_seen == 0:
        return _thread(
            "interaction_timing",
            {"gaps_seen": 0},
            {"predicted_ticks_to_next_interaction": None, "mean_gap_ticks": None},
            0.0,
            "Cold start: no completed interaction gap observed yet.",
            {},
        )
    mean_gap = float(thread_state.get("mean_gap", 0.0))
    ticks_since = int(thread_state.get("ticks_since", 0))
    remaining = round(max(0.0, mean_gap - ticks_since), 6)
    confidence = round(min(1.0, gaps_seen / GAP_COUNT_FLOOR), 6)
    effects = {}
    if remaining <= 1.5:
        effects["play"] = 0.1
    return _thread(
        "interaction_timing",
        {"gaps_seen": gaps_seen, "ticks_since_interaction": ticks_since},
        {
            "predicted_ticks_to_next_interaction": remaining,
            "mean_gap_ticks": round(mean_gap, 6),
        },
        confidence,
        "Online interaction-gap rhythm predicts the next interaction moment.",
        effects,
    )


# The fleet registry: (name, observe, signal), execution order fixed.
FLEET_THREADS = [
    ("hunger_forecast", hunger_forecast_observe, hunger_forecast_signal),
    ("energy_forecast", energy_forecast_observe, energy_forecast_signal),
    ("boredom_novelty", boredom_novelty_observe, boredom_novelty_signal),
    ("attention_forecast", attention_forecast_observe, attention_forecast_signal),
    ("interaction_timing", interaction_timing_observe, interaction_timing_signal),
]
FLEET_THREAD_NAMES = [name for name, _observe, _signal in FLEET_THREADS]


def observe_fleet(lifecycle_state: dict) -> dict:
    """One observe step for every OPTED-IN fleet thread.

    Returns the new ``thread_states`` mapping (the caller stores it back
    on its state); the input state is never mutated. Threads without an
    explicit ``learning_switches[name] is True`` do not run and hold no
    memory.
    """
    switches = lifecycle_state.get("learning_switches") or {}
    thread_states = dict(lifecycle_state.get("thread_states") or {})
    updated: dict = {}
    for name, observe, _signal in FLEET_THREADS:
        if switches.get(name) is True:
            updated[name] = observe(thread_states.get(name) or {}, lifecycle_state)
    return updated


def fleet_signals(lifecycle_state: dict) -> list[dict]:
    """Signals for every opted-in fleet thread (the switchboard seam)."""
    switches = lifecycle_state.get("learning_switches") or {}
    thread_states = lifecycle_state.get("thread_states") or {}
    return [
        signal(thread_states.get(name) or {}, lifecycle_state)
        for name, _observe, signal in FLEET_THREADS
        if switches.get(name) is True
    ]



def _thread(
    name: str,
    inputs: dict,
    output: object,
    confidence: float,
    explanation: str,
    effects: dict[str, float],
) -> dict:
    return {
        "name": name,
        "input": inputs,
        "output": output,
        "confidence": round(_clamp(confidence), 6),
        "explanation": explanation,
        "effects": effects,
    }


def _clamp(value: object) -> float:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        number = 0.0
    return max(0.0, min(1.0, number))


