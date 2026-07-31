"""The micro-thread fleet contract (cycle 12 D1, gap-analysis Phase D).

The documents specify ~11 micro-learner threads streaming confidence
into the switchboard; ~2 exist. This lab is the CONTRACT the fleet
grows through, plus the first documented need predictor as the
end-to-end pipe cleaner.

A fleet thread is (name, observe, signal):

- ``observe(thread_state, lifecycle_state) -> new thread_state`` — the
  online learning step. Pure (returns a NEW dict), deterministic,
  JSON-serializable, BOUNDED memory. Called by the episode/companion
  loop per tick, never by the switchboard (the promoted rule: decide is
  a pure read; learning mechanics live in the loop).
- ``signal(thread_state, lifecycle_state) -> thread dict`` — the same
  ``{name, input, output, confidence, explanation, effects}`` shape the
  historical switchboard threads emit, additively combined as
  ``effects x confidence``.

Thread memory lives in ``lifecycle_state["thread_states"][name]``.

THE OPT-IN RULE (load-bearing): historical switchboard threads run on
``learning_switches`` absent-or-True; fleet threads run ONLY on an
explicit ``learning_switches[name] is True``. No existing flow sets
fleet names, so every frozen path — the parity-pinned baseline, every
episode, every session — is byte-identical until a profile opts in.

The pipe cleaner, ``hunger_forecast`` (the documented hunger
predictor): an online trend forecaster over the companion's own hunger
history. It anticipates — its feed utility rises BEFORE the reactive
mood thread's 0.65 threshold trips — and it is honest at cold start
(confidence 0, no effects, no invented signal).
"""

import argparse
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
LIFECYCLE_SIM = ROOT / "labs" / "lifecycle_sim"
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
for _path in [GRID_GENOME, LIFECYCLE_SIM, PACKAGE_SRC]:
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))


ARTIFACT_ID = "micro_thread_fleet_contract_stage0"
REPORT_DATE = "2026-07-08"
REPLAY_TICKS = 48
# estimate_hidden_mood's frozen rule: mood flips to "hungry" strictly
# above this. The pipe cleaner must speak BEFORE it.
REACTIVE_HUNGRY_THRESHOLD = 0.65

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
# The documented clip vocabulary — identical to
# labs/grid_genome/animation_states.ANIMATION_STATES (the package twin
# cannot import labs; the D3 lab harness pins the two lists equal).
CLIP_VOCABULARY = ["idle", "blink", "sleep", "beg", "ill"]
BANDIT_PULLS_FLOOR = 20.0
# Greedy-leaning UCB for the documented short-lifecycle horizon (the
# classic 2.0 explores past the companion's lifetime); counts are plain
# increments capped for bounded state.
BANDIT_EXPLORATION = 0.3
BANDIT_TRIALS_CAP = 500.0
# The T16 mood vocabulary in fixed order (select_animation_state /
# estimate_hidden_mood ground truth: energy 0.2 / hunger 0.65 /
# stress 0.65, lexicographic priority tired > hungry > stressed).
HMM_MOODS = ["curious", "hungry", "stressed", "tired"]
HMM_STICKINESS = 0.85
HMM_EVIDENCE_SLOPE = 40.0
HMM_EVIDENCE_FLOOR = 0.02
HMM_OBSERVATION_FLOOR = 5
# Dwell hysteresis on the MAP readout: the reported mood switches only
# when the challenger's belief beats the incumbent's by this margin
# (the full distribution is always reported unsmoothed).
HMM_MAP_MARGIN = 0.15
# The frozen reactive mood->effects table (estimate_hidden_mood),
# expectation-weighted by the filtered posterior.
HMM_MOOD_EFFECTS = {
    "tired": {"sleep": 0.55, "play": -0.25, "mutate": -0.2},
    "hungry": {"feed": 0.5, "play": -0.1},
    "stressed": {"idle": 0.35, "mutate": -0.35},
    "curious": {"play": 0.25, "idle": 0.05},
}


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def _mood_evidence(lifecycle_state: dict) -> dict[str, float]:
    """Soft per-mood likelihoods grounded in the frozen T16 thresholds,
    with the reactive rule's lexicographic priority encoded by masking
    each mood's evidence with its higher-priority complements."""
    hunger = _clamp(lifecycle_state.get("hunger", 0.5))
    energy = _clamp(lifecycle_state.get("energy", 0.5))
    stress = _clamp(lifecycle_state.get("stress", 0.0))
    tired = _sigmoid((0.2 - energy) * HMM_EVIDENCE_SLOPE)
    hungry = _sigmoid((hunger - 0.65) * HMM_EVIDENCE_SLOPE) * (1.0 - tired)
    stressed = (
        _sigmoid((stress - 0.65) * HMM_EVIDENCE_SLOPE)
        * (1.0 - tired)
        * (1.0 - _sigmoid((hunger - 0.65) * HMM_EVIDENCE_SLOPE))
    )
    curious = (1.0 - tired) * (1.0 - hungry) * (1.0 - stressed)
    return {
        "curious": max(HMM_EVIDENCE_FLOOR, curious),
        "hungry": max(HMM_EVIDENCE_FLOOR, hungry),
        "stressed": max(HMM_EVIDENCE_FLOOR, stressed),
        "tired": max(HMM_EVIDENCE_FLOOR, tired),
    }


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


def _threshold_mood(lifecycle_state: dict) -> str:
    """The frozen T16/estimate_hidden_mood rule, verbatim thresholds
    (energy 0.2 / hunger 0.65 / stress 0.65, lexicographic priority)."""
    if _clamp(lifecycle_state.get("energy", 0.5)) < 0.2:
        return "tired"
    if _clamp(lifecycle_state.get("hunger", 0.5)) > 0.65:
        return "hungry"
    if _clamp(lifecycle_state.get("stress", 0.0)) > 0.65:
        return "stressed"
    return "curious"


def animation_bandit_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    """Contextual UCB over clips: reward = the next-tick interaction bit,
    attributed to the (mood, clip) PENDING from the previous show."""
    trials = dict(thread_state.get("trials") or {})
    wins = dict(thread_state.get("wins") or {})
    pending = thread_state.get("pending")
    interactions = lifecycle_state.get("recent_interactions") or []
    if pending is not None and interactions:
        reward = 1.0 if _clamp(interactions[-1]) > 0 else 0.0
        key = str(pending)
        if float(trials.get(key, 0.0)) < BANDIT_TRIALS_CAP:
            trials[key] = round(float(trials.get(key, 0.0)) + 1.0, 6)
            wins[key] = round(float(wins.get(key, 0.0)) + reward, 6)
    shown = lifecycle_state.get("last_animation")
    updated = {"trials": trials, "wins": wins}
    if isinstance(shown, str) and shown in CLIP_VOCABULARY:
        updated["pending"] = f"{_threshold_mood(lifecycle_state)}|{shown}"
    return updated


def animation_bandit_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    mood = _threshold_mood(lifecycle_state)
    trials = thread_state.get("trials") or {}
    wins = thread_state.get("wins") or {}
    vocabulary = lifecycle_state.get("animation_vocabulary")
    if not isinstance(vocabulary, list) or not vocabulary:
        vocabulary = list(CLIP_VOCABULARY)
    arms = [clip for clip in CLIP_VOCABULARY if clip in vocabulary]
    context_trials = {clip: float(trials.get(f"{mood}|{clip}", 0.0)) for clip in arms}
    total = sum(context_trials.values())
    means = {}
    recommended = None
    for clip in arms:
        if context_trials[clip] < 1.0:
            # Unplayed arms first, in vocabulary order — deterministic.
            if recommended is None:
                recommended = clip
            means[clip] = None
            continue
        means[clip] = round(
            float(wins.get(f"{mood}|{clip}", 0.0)) / context_trials[clip], 6
        )
    if recommended is None:
        # Every arm played: UCB1 with the decayed counts.
        recommended = max(
            arms,
            key=lambda clip: (
                means[clip]
                + math.sqrt(
                    BANDIT_EXPLORATION
                    * math.log(max(total, 2.0))
                    / context_trials[clip]
                ),
                -arms.index(clip),
            ),
        )
    played_means = sorted(
        (value for value in means.values() if value is not None), reverse=True
    )
    gap = (
        played_means[0] - played_means[1] if len(played_means) >= 2 else 0.0
    )
    confidence = round(min(1.0, total / BANDIT_PULLS_FLOOR) * _clamp(gap), 6)
    return _thread(
        "animation_bandit",
        {"context_mood": mood, "context_pulls": round(total, 6)},
        {
            "recommended_clip": recommended,
            "context_mood": mood,
            "clip_means": means,
        },
        confidence,
        "Contextual UCB personalizes clip choice per mood from interaction feedback.",
        # Clip preference is consumed by the render/packet side, never
        # the action switchboard — an honestly effect-free thread.
        {},
    )


def hidden_mood_hmm_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    """Forward-filter step over the T16 mood vocabulary."""
    belief = thread_state.get("belief") or {
        mood: 1.0 / len(HMM_MOODS) for mood in HMM_MOODS
    }
    evidence = _mood_evidence(lifecycle_state)
    posterior = {}
    for mood in HMM_MOODS:
        prior = sum(
            float(belief.get(source, 0.0))
            * (
                HMM_STICKINESS
                if source == mood
                else (1.0 - HMM_STICKINESS) / (len(HMM_MOODS) - 1)
            )
            for source in HMM_MOODS
        )
        posterior[mood] = prior * evidence[mood]
    normalizer = sum(posterior.values()) or 1.0
    filtered = {
        mood: round(posterior[mood] / normalizer, 6) for mood in HMM_MOODS
    }
    challenger = max(HMM_MOODS, key=lambda mood: (filtered[mood], mood))
    incumbent = thread_state.get("map_mood")
    if incumbent is None or filtered[challenger] > (
        filtered.get(incumbent, 0.0) + HMM_MAP_MARGIN
    ):
        incumbent = challenger
    return {
        "belief": filtered,
        "map_mood": incumbent,
        "observations": min(int(thread_state.get("observations", 0)) + 1, 60),
    }


def hidden_mood_hmm_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    observations = int(thread_state.get("observations", 0))
    if observations == 0:
        return _thread(
            "hidden_mood_hmm",
            {"observations": 0},
            {"map_mood": None, "mood_distribution": None},
            0.0,
            "Cold start: no mood evidence filtered yet.",
            {},
        )
    belief = thread_state.get("belief") or {}
    map_mood = thread_state.get("map_mood") or max(
        HMM_MOODS, key=lambda mood: (belief.get(mood, 0.0), mood)
    )
    entropy = 0.0
    for mood in HMM_MOODS:
        probability = float(belief.get(mood, 0.0))
        if probability > 0:
            entropy -= probability * math.log(probability)
    certainty = max(0.0, 1.0 - entropy / math.log(len(HMM_MOODS)))
    confidence = round(
        min(1.0, observations / HMM_OBSERVATION_FLOOR) * certainty, 6
    )
    effects: dict[str, float] = {}
    for mood in HMM_MOODS:
        probability = float(belief.get(mood, 0.0))
        for action, weight in HMM_MOOD_EFFECTS[mood].items():
            effects[action] = effects.get(action, 0.0) + probability * weight
    effects = {
        action: round(value, 6)
        for action, value in sorted(effects.items())
        if round(value, 6) != 0.0
    }
    return _thread(
        "hidden_mood_hmm",
        {"observations": observations},
        {
            "map_mood": map_mood,
            "mood_distribution": {
                mood: round(float(belief.get(mood, 0.0)), 6)
                for mood in HMM_MOODS
            },
        },
        confidence,
        "Forward-filtered latent mood over the T16 vocabulary; entropy-honest.",
        effects,
    )


# -- The D4 evidence threads ---------------------------------------------
#
# Each streams an EXISTING engine number through the D1 contract — no
# new statistics invented. The loop provides the per-creature evidence
# bundle on ``lifecycle_state["evidence"]`` (computed by the canonical
# package surfaces: archive metrics, the F3 adopted readability model,
# the SLIP authority, the lineage records — the archive interface
# spec's documented input factoring). Observe caches the bundle slice
# in thread state; without evidence the thread is honestly silent.


def _evidence_observe(
    thread_state: dict, lifecycle_state: dict, keys: list[str]
) -> dict:
    bundle = lifecycle_state.get("evidence")
    if not isinstance(bundle, dict):
        return dict(thread_state)
    cached = dict(thread_state.get("evidence") or {})
    for key in keys:
        if key in bundle:
            cached[key] = bundle[key]
    return {"evidence": cached}


def mutation_stability_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    return _evidence_observe(thread_state, lifecycle_state, ["mutation_stability"])


def mutation_stability_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    evidence = thread_state.get("evidence") or {}
    score = evidence.get("mutation_stability")
    if score is None:
        return _thread(
            "mutation_stability",
            {"evidence_present": False},
            {"mutation_stability": None},
            0.0,
            "Cold start: no mutation-stability evidence provided.",
            {},
        )
    score = _clamp(score)
    # A deterministic measured metric: full confidence in provenance.
    effects = {"mutate": round((score - 0.5) * 0.2, 6)}
    if effects["mutate"] == 0.0:
        effects = {}
    return _thread(
        "mutation_stability",
        {"evidence_present": True},
        {"mutation_stability": round(score, 6)},
        1.0,
        "The archive's cap-normalized mutation-stability metric, streamed.",
        effects,
    )


def readability_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    return _evidence_observe(thread_state, lifecycle_state, ["readability_score"])


def readability_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    evidence = thread_state.get("evidence") or {}
    score = evidence.get("readability_score")
    if score is None:
        return _thread(
            "readability",
            {"evidence_present": False},
            {"readability_score": None},
            0.0,
            "Cold start: no readability evidence provided.",
            {},
        )
    score = _clamp(score)
    # A learned model's opinion: sharpness confidence (distance from
    # indifference), the primary signal per DR 0019 — survey fallback.
    confidence = round(abs(score - 0.5) * 2.0, 6)
    return _thread(
        "readability",
        {"evidence_present": True},
        {"readability_score": round(score, 6)},
        confidence,
        "The F3 adopted readability model's score, streamed (DR 0019 primary).",
        # Consumed by generation/selection surfaces, never the action
        # switchboard — an honestly effect-free thread.
        {},
    )


def slip_compat_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    return _evidence_observe(
        thread_state, lifecycle_state, ["slip_aligned", "slip_error_count"]
    )


def slip_compat_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    evidence = thread_state.get("evidence") or {}
    aligned = evidence.get("slip_aligned")
    if aligned is None:
        return _thread(
            "slip_compat",
            {"evidence_present": False},
            {"slip_aligned": None},
            0.0,
            "Cold start: no SLIP-alignment evidence provided.",
            {},
        )
    return _thread(
        "slip_compat",
        {"evidence_present": True},
        {
            "slip_aligned": bool(aligned),
            "slip_error_count": int(evidence.get("slip_error_count", 0)),
        },
        1.0,
        "The SLIP authority's alignment verdict, streamed.",
        {},
    )


def lineage_survival_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    return _evidence_observe(thread_state, lifecycle_state, ["lineage"])


def lineage_survival_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    evidence = thread_state.get("evidence") or {}
    record = evidence.get("lineage")
    if not isinstance(record, dict):
        return _thread(
            "lineage_survival",
            {"evidence_present": False},
            {"elite": None, "generation": None, "children": None},
            0.0,
            "Cold start: no lineage record provided.",
            {},
        )
    return _thread(
        "lineage_survival",
        {"evidence_present": True},
        {
            "elite": bool(record.get("elite", False)),
            "generation": int(record.get("generation", 0)),
            "children": int(record.get("children", 0)),
        },
        1.0,
        "The lineage record's survival facts (elite, generation, children), streamed.",
        {},
    )


# The fleet registry: (name, observe, signal), execution order fixed.
# ---------------------------------------------------------------------
# Cycle 24 N3: the dossier's ablation conditions E / F / G.
#
# The micro-learner ablation names eight conditions; Phase D built the
# eleven-thread fleet and instantiated NONE of E (Q-table), F (tiny
# decision tree) or G (Bayesian counter), so those conditions have been
# documented-and-unmet since cycle 12. These three learners exist to be
# ABLATED — they are candidates, not fleet, and they are additive and
# byte-identical when off (they require an explicit ``True`` switch, and
# ``FLEET_THREADS`` below is untouched, so every committed Phase-D
# number stands).
#
# Each is the dossier's own mechanism, with the dossier's own named
# weakness respected rather than engineered around:
#   E  Q-table              "state explosion, needs repeated visits"
#                           -> scoped tightly to 3x3 buckets, silent
#                              until a state has been visited enough
#   F  Tiny decision tree   "brittle if overfit"
#                           -> depth 2, at most four leaves, thresholds
#                              adapt as running means rather than being
#                              fitted to a sample
#   G  Bayesian counter     "limited expressivity"
#                           -> one Beta-Bernoulli question only: how
#                              responsive is this keeper?
# ---------------------------------------------------------------------

QTABLE_TERCILES = (0.34, 0.67)
QTABLE_MIN_VISITS = 3
QTABLE_CONFIDENT_VISITS = 12
QTABLE_EFFECT_SCALE = 0.30
TREE_MIN_SAMPLES = 3
TREE_CONFIDENT_SAMPLES = 10
TREE_SPLIT_ALPHA = 0.15
TREE_EFFECT_SCALE = 0.25
BAYES_CONFIDENT_OBSERVATIONS = 12
BAYES_EFFECT_SCALE = 0.35
_CREDITABLE_ACTIONS = ("feed", "play", "sleep", "idle", "mutate")


def _tercile(value: object) -> int:
    number = _clamp(value)
    if number < QTABLE_TERCILES[0]:
        return 0
    if number < QTABLE_TERCILES[1]:
        return 1
    return 2


def _qtable_bucket(lifecycle_state: dict) -> str:
    """The tightly scoped discrete state: 3 hunger x 3 energy = 9."""
    return (
        f"{_tercile(lifecycle_state.get('hunger'))}"
        f"{_tercile(lifecycle_state.get('energy'))}"
    )


def _last_executed(lifecycle_state: dict) -> tuple[str, float] | None:
    """The action the tick ACTUALLY ran, and the balance it returned.

    The keeper can override the companion's choice, so a learner that
    credited its own recommendation would be learning a policy the
    world never executed.
    """
    history = lifecycle_state.get("history") or []
    if not history:
        return None
    entry = history[-1]
    action = entry.get("action")
    if action not in _CREDITABLE_ACTIONS:
        return None
    try:
        return action, float(entry.get("balance", 0.0))
    except (TypeError, ValueError):
        return None


def _running_update(store: dict, key: str, value: float) -> None:
    record = store.get(key) or {"mean": 0.0, "n": 0}
    count = int(record["n"]) + 1
    mean = float(record["mean"]) + (value - float(record["mean"])) / count
    store[key] = {"mean": round(mean, 6), "n": count}


def qtable_policy_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    """E — tabular value estimate over (bucket, EXECUTED action)."""
    table = {key: dict(value) for key, value in (thread_state.get("q") or {}).items()}
    pending = thread_state.get("pending_bucket")
    executed = _last_executed(lifecycle_state)
    if pending is not None and executed is not None:
        action, reward = executed
        _running_update(table, f"{pending}|{action}", reward)
    return {"q": table, "pending_bucket": _qtable_bucket(lifecycle_state)}


def qtable_policy_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    bucket = _qtable_bucket(lifecycle_state)
    table = thread_state.get("q") or {}
    seen = {
        key.split("|", 1)[1]: value
        for key, value in table.items()
        if key.startswith(f"{bucket}|") and int(value.get("n", 0)) >= QTABLE_MIN_VISITS
    }
    if not seen:
        return _thread(
            "qtable_policy",
            {"bucket": bucket, "visited_actions": 0},
            {"best_action": None, "cold_start": True},
            0.0,
            "Q-table cold: this bucket has not been visited enough to act.",
            {},
        )
    best_action = max(seen, key=lambda action: float(seen[action]["mean"]))
    best_value = float(seen[best_action]["mean"])
    visits = sum(int(value["n"]) for value in seen.values())
    confidence = min(1.0, visits / QTABLE_CONFIDENT_VISITS)
    effects = {}
    if best_value > 0:
        effects[best_action] = round(best_value * QTABLE_EFFECT_SCALE, 6)
    return _thread(
        "qtable_policy",
        {"bucket": bucket, "visited_actions": len(seen)},
        {
            "best_action": best_action,
            "best_value": round(best_value, 6),
            "cold_start": False,
        },
        confidence,
        f"Q-table over 3x3 hunger/energy buckets; bucket {bucket} favours {best_action}.",
        effects,
    )


def _tree_leaf(thread_state: dict, lifecycle_state: dict) -> tuple[str, float, float]:
    hunger_split = float(thread_state.get("hunger_split", 0.5))
    energy_split = float(thread_state.get("energy_split", 0.5))
    hunger = _clamp(lifecycle_state.get("hunger"))
    energy = _clamp(lifecycle_state.get("energy"))
    leaf = ("h" if hunger >= hunger_split else "l") + (
        "h" if energy >= energy_split else "l"
    )
    return leaf, hunger_split, energy_split


def tiny_tree_router_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    """F — depth-2 router; thresholds adapt, they are never fitted."""
    leaf_returns = {
        key: {action: dict(record) for action, record in value.items()}
        for key, value in (thread_state.get("leaf_returns") or {}).items()
    }
    pending = thread_state.get("pending_leaf")
    executed = _last_executed(lifecycle_state)
    if pending is not None and executed is not None:
        action, reward = executed
        bucket = leaf_returns.setdefault(pending, {})
        _running_update(bucket, action, reward)
    hunger_split = float(thread_state.get("hunger_split", 0.5))
    energy_split = float(thread_state.get("energy_split", 0.5))
    hunger_split += TREE_SPLIT_ALPHA * (_clamp(lifecycle_state.get("hunger")) - hunger_split)
    energy_split += TREE_SPLIT_ALPHA * (_clamp(lifecycle_state.get("energy")) - energy_split)
    updated = {
        "leaf_returns": leaf_returns,
        "hunger_split": round(hunger_split, 6),
        "energy_split": round(energy_split, 6),
    }
    leaf, _, _ = _tree_leaf(updated, lifecycle_state)
    updated["pending_leaf"] = leaf
    return updated


def tiny_tree_router_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    leaf, hunger_split, energy_split = _tree_leaf(thread_state, lifecycle_state)
    route = (
        f"hunger{'>=' if leaf[0] == 'h' else '<'}{hunger_split:.2f} & "
        f"energy{'>=' if leaf[1] == 'h' else '<'}{energy_split:.2f}"
    )
    bucket = (thread_state.get("leaf_returns") or {}).get(leaf) or {}
    usable = {
        action: record
        for action, record in bucket.items()
        if int(record.get("n", 0)) >= TREE_MIN_SAMPLES
    }
    if not usable:
        return _thread(
            "tiny_tree_router",
            {"leaf": leaf, "samples": 0},
            {"route": route, "best_action": None, "cold_start": True},
            0.0,
            "Tiny tree cold: this leaf has too few samples to route.",
            {},
        )
    best_action = max(usable, key=lambda action: float(usable[action]["mean"]))
    best_value = float(usable[best_action]["mean"])
    samples = sum(int(record["n"]) for record in usable.values())
    effects = {}
    if best_value > 0:
        effects[best_action] = round(best_value * TREE_EFFECT_SCALE, 6)
    return _thread(
        "tiny_tree_router",
        {"leaf": leaf, "samples": samples},
        {
            "route": route,
            "best_action": best_action,
            "best_value": round(best_value, 6),
            "cold_start": False,
        },
        min(1.0, samples / TREE_CONFIDENT_SAMPLES),
        f"Depth-2 router: {route} -> {best_action}.",
        effects,
    )


def bayes_keeper_counter_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    """G — Beta-Bernoulli tracker on one question: is the keeper there?"""
    alpha = float(thread_state.get("alpha", 1.0))
    beta = float(thread_state.get("beta", 1.0))
    observations = int(thread_state.get("observations", 0))
    interactions = lifecycle_state.get("recent_interactions") or []
    if interactions:
        if _clamp(interactions[-1]) > 0:
            alpha += 1.0
        else:
            beta += 1.0
        observations += 1
    return {
        "alpha": round(alpha, 6),
        "beta": round(beta, 6),
        "observations": observations,
    }


def bayes_keeper_counter_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    alpha = float(thread_state.get("alpha", 1.0))
    beta = float(thread_state.get("beta", 1.0))
    observations = int(thread_state.get("observations", 0))
    total = alpha + beta
    responsiveness = alpha / total
    uncertainty = (alpha * beta / (total * total * (total + 1.0))) ** 0.5
    if observations == 0:
        return _thread(
            "bayes_keeper_counter",
            {"observations": 0},
            {
                "responsiveness": round(responsiveness, 6),
                "uncertainty": round(uncertainty, 6),
                "cold_start": True,
            },
            0.0,
            "Beta-Bernoulli cold: no keeper evidence observed yet.",
            {},
        )
    hunger = _clamp(lifecycle_state.get("hunger"))
    # The domain point: begging only pays if someone answers. A
    # companion that has learned its keeper is absent should stop
    # spending ticks on a display nobody sees.
    pull = (responsiveness - 0.5) * 2.0
    effects = {"feed": round(pull * hunger * BAYES_EFFECT_SCALE, 6)}
    if pull < 0:
        effects["sleep"] = round(-pull * (1.0 - hunger) * BAYES_EFFECT_SCALE, 6)
    return _thread(
        "bayes_keeper_counter",
        {"observations": observations},
        {
            "responsiveness": round(responsiveness, 6),
            "uncertainty": round(uncertainty, 6),
            "cold_start": False,
        },
        min(1.0, observations / BAYES_CONFIDENT_OBSERVATIONS),
        (
            # Named for what it MEASURES: the rate of social ticks
            # (`recent_interactions`, i.e. executed feed/play). In the
            # beg-mediated dependent harness that is dominated by the
            # keeper answering a beg, but it is not purely the keeper —
            # an autonomous play counts too.
            f"Social-tick rate {responsiveness:.2f} "
            f"(+/-{uncertainty:.2f}) over {observations} observations."
        ),
        effects,
    )


FLEET_THREADS = [
    ("hunger_forecast", hunger_forecast_observe, hunger_forecast_signal),
    ("energy_forecast", energy_forecast_observe, energy_forecast_signal),
    ("boredom_novelty", boredom_novelty_observe, boredom_novelty_signal),
    ("attention_forecast", attention_forecast_observe, attention_forecast_signal),
    ("interaction_timing", interaction_timing_observe, interaction_timing_signal),
    ("animation_bandit", animation_bandit_observe, animation_bandit_signal),
    ("hidden_mood_hmm", hidden_mood_hmm_observe, hidden_mood_hmm_signal),
    ("mutation_stability", mutation_stability_observe, mutation_stability_signal),
    ("readability", readability_observe, readability_signal),
    ("slip_compat", slip_compat_observe, slip_compat_signal),
    ("lineage_survival", lineage_survival_observe, lineage_survival_signal),
]
FLEET_THREAD_NAMES = [name for name, _observe, _signal in FLEET_THREADS]

# Cycle 24 N3: the dossier's E/F/G learners are CANDIDATES, not fleet.
# ``FLEET_THREADS`` above stays the committed Phase-D eleven so every
# Phase-D number keeps its meaning; the candidates ride the same seam
# and are reachable only by an explicit opt-in, which is what makes the
# extension byte-identical when off.
CANDIDATE_THREADS = [
    ("qtable_policy", qtable_policy_observe, qtable_policy_signal),
    ("tiny_tree_router", tiny_tree_router_observe, tiny_tree_router_signal),
    (
        "bayes_keeper_counter",
        bayes_keeper_counter_observe,
        bayes_keeper_counter_signal,
    ),
]
CANDIDATE_THREAD_NAMES = [name for name, _observe, _signal in CANDIDATE_THREADS]
EXTENDED_FLEET_THREADS = FLEET_THREADS + CANDIDATE_THREADS


def observe_fleet(lifecycle_state: dict) -> dict:
    """One observe step for every OPTED-IN thread.

    Returns the new ``thread_states`` mapping (the caller stores it back
    on its state); the input state is never mutated. Threads without an
    explicit ``learning_switches[name] is True`` do not run and hold no
    memory — which is why iterating the EXTENDED list (cycle 24 N3)
    leaves every existing caller byte-identical: a profile that never
    names a candidate can never run one.
    """
    switches = lifecycle_state.get("learning_switches") or {}
    thread_states = dict(lifecycle_state.get("thread_states") or {})
    updated: dict = {}
    for name, observe, _signal in EXTENDED_FLEET_THREADS:
        if switches.get(name) is True:
            updated[name] = observe(thread_states.get(name) or {}, lifecycle_state)
    return updated


def fleet_signals(lifecycle_state: dict) -> list[dict]:
    """Signals for every opted-in thread (the switchboard seam)."""
    switches = lifecycle_state.get("learning_switches") or {}
    thread_states = lifecycle_state.get("thread_states") or {}
    return [
        signal(thread_states.get(name) or {}, lifecycle_state)
        for name, _observe, signal in EXTENDED_FLEET_THREADS
        if switches.get(name) is True
    ]


def _replay(ticks: int, opt_in: bool) -> dict:
    """One deterministic lifecycle replay on the LCD seed subject.

    ``opt_in=False`` is the frozen arm: every visited state is decided by
    BOTH the lab switchboard and the promoted package, counted identical.
    ``opt_in=True`` is the fleet arm: the loop observes per tick (the
    contract's division of labor), and each visited state is also decided
    with the opt-in stripped, so the seam's utility movement is measured
    on the very states the fleet trajectory visits.
    """
    from corpus_builder import build_seed_grids
    from lifecycle_sim import advance_tick, initial_lifecycle_state
    from micro_switchboard import run_switchboard

    from mecha_engine.learning import decide

    slip_profile = json.loads(
        (ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json").read_text(
            encoding="utf-8"
        )
    )
    state = initial_lifecycle_state(build_seed_grids()[0], slip_profile)
    if opt_in:
        switches = dict(state.get("learning_switches") or {})
        switches["hunger_forecast"] = True
        state["learning_switches"] = switches

    arm = {
        "ticks": ticks,
        "lab_package_decisions_identical": 0,
        "fleet_thread_appearances": 0,
        "anticipatory_signal_ticks": 0,
        "first_anticipatory_signal_tick": None,
        "first_reactive_hungry_tick": None,
        "cold_start_silent_ticks": 0,
        "utility_moved_ticks": 0,
        "decision_flips": 0,
        "max_confidence": 0.0,
        "feed_count": 0,
        "mean_hunger": 0.0,
    }
    hunger_total = 0.0
    for tick in range(ticks):
        if opt_in:
            state["thread_states"] = observe_fleet(state)
        decision = run_switchboard(state)
        if decision == decide(state):
            arm["lab_package_decisions_identical"] += 1
        hunger = _clamp(state.get("hunger", 0.5))
        hunger_total += hunger
        if (
            hunger > REACTIVE_HUNGRY_THRESHOLD
            and arm["first_reactive_hungry_tick"] is None
        ):
            arm["first_reactive_hungry_tick"] = tick
        fleet_entries = [
            thread
            for thread in decision["threads"]
            if thread["name"] in FLEET_THREAD_NAMES
        ]
        arm["fleet_thread_appearances"] += len(fleet_entries)
        for entry in fleet_entries:
            arm["max_confidence"] = max(arm["max_confidence"], entry["confidence"])
            if entry["confidence"] == 0.0 and not entry["effects"]:
                arm["cold_start_silent_ticks"] += 1
            if entry["effects"] and hunger <= REACTIVE_HUNGRY_THRESHOLD:
                arm["anticipatory_signal_ticks"] += 1
                if arm["first_anticipatory_signal_tick"] is None:
                    arm["first_anticipatory_signal_tick"] = tick
        if opt_in:
            stripped = dict(state)
            stripped.pop("thread_states", None)
            stripped_switches = dict(stripped.get("learning_switches") or {})
            stripped_switches.pop("hunger_forecast", None)
            stripped["learning_switches"] = stripped_switches
            frozen_decision = run_switchboard(stripped)
            if frozen_decision["utilities"] != decision["utilities"]:
                arm["utility_moved_ticks"] += 1
            if frozen_decision["action"] != decision["action"]:
                arm["decision_flips"] += 1
        if decision["action"] == "feed":
            arm["feed_count"] += 1
        state = advance_tick(state, decision["action"])
    arm["mean_hunger"] = round(hunger_total / ticks, 6)
    return arm


def build_thread_fleet_report() -> dict:
    frozen = _replay(REPLAY_TICKS, opt_in=False)
    fleet = _replay(REPLAY_TICKS, opt_in=True)
    frozen_arm = {
        key: frozen[key]
        for key in [
            "ticks",
            "lab_package_decisions_identical",
            "fleet_thread_appearances",
            "feed_count",
            "mean_hunger",
        ]
    }
    fleet_arm = {key: fleet[key] for key in fleet if key != "decision_flips"}
    fleet_arm["decision_flips"] = fleet["decision_flips"]

    frozen_holds = (
        frozen["lab_package_decisions_identical"] == frozen["ticks"]
        and frozen["fleet_thread_appearances"] == 0
    )
    anticipates = fleet["anticipatory_signal_ticks"] > 0 and (
        fleet["first_reactive_hungry_tick"] is None
        or fleet["first_anticipatory_signal_tick"]
        < fleet["first_reactive_hungry_tick"]
    )
    complete = frozen_holds and anticipates
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "complete" if complete else "refuted",
        "date": REPORT_DATE,
        "purpose": (
            "The D1 micro-thread fleet contract (observe -> signal -> "
            "confidence in [0,1], pure, deterministic, JSON-serializable, "
            "bounded memory) plus the switchboard's ADDITIVE confidence "
            "seam, proven on a two-arm deterministic lifecycle replay: "
            "the frozen arm must be byte-identical lab-and-package with "
            "zero fleet appearances; the opted-in arm must move utilities "
            "through the seam and speak before the reactive hungry "
            "threshold (0.65) trips."
        ),
        "source_artifacts": [
            "labs/grid_genome/micro_switchboard.py",
            "packages/mecha_engine/src/mecha_engine/learning/_switchboard.py",
            "packages/mecha_engine/src/mecha_engine/learning/threads.py",
            "labs/lifecycle_sim/lifecycle_sim.py",
            "data/slips/valid/slip_lcd_seed.json",
            "data/seed_grids/mg_seed_001.json",
            "docs/gap-analysis.md",
            "docs/project-research/deep-research/01/deep-research.md",
        ],
        "metrics": {
            "replay_ticks": REPLAY_TICKS,
            "fleet_size": len(FLEET_THREADS),
            "documented_fleet_target": 11,
            "reactive_hungry_threshold": REACTIVE_HUNGRY_THRESHOLD,
            "feed_anticipation_floor": FEED_ANTICIPATION_FLOOR,
            "frozen_replay": frozen_arm,
            "fleet_replay": fleet_arm,
        },
        "closed_states": (
            [
                "thread_contract_defined_observe_signal_confidence",
                "opt_in_rule_keeps_frozen_paths_byte_identical",
                "switchboard_seam_additive_lab_and_package",
                "package_twin_parity_pinned_by_lab_tests",
                "hunger_forecast_speaks_before_the_reactive_threshold",
                "cold_start_is_honest_zero_confidence_no_effects",
            ]
            if complete
            else ["d1_bar_not_met_recorded_honestly"]
        ),
        "blocked_states": [
            "need_predictors_not_trained_on_replayed_histories (D2)",
            "confidence_calibration_unmeasured (D2)",
            "animation_bandit_and_hmm_mood_not_built (D3)",
            "evidence_threads_not_wired (D4)",
            "synthetic_keepers_and_scale_harness_absent (D5)",
            "ablation_gates_not_run (D6)",
        ]
        + (
            []
            if fleet["decision_flips"] > 0
            else [
                "anticipatory_signal_moves_utilities_but_never_flips_the_lcd_decision "
                "(effect magnitudes are D2's calibration work; recorded, not fudged)"
            ]
        ),
        "decision": (
            "The contract and the seam hold: "
            f"{frozen_arm['lab_package_decisions_identical']}/{REPLAY_TICKS} "
            "frozen decisions byte-identical lab-and-package with zero fleet "
            "appearances; the opted-in pipe cleaner moved utilities on "
            f"{fleet_arm['utility_moved_ticks']} ticks and first spoke at "
            f"tick {fleet_arm['first_anticipatory_signal_tick']} "
            f"(reactive threshold trips at "
            f"{fleet_arm['first_reactive_hungry_tick']})."
            if complete
            else "The D1 bar is NOT met — recorded, not fudged."
        ),
        "next_research_step": (
            "D2: the need predictors (sleep/energy, boredom/novelty, "
            "attention, interaction timing) trained against replayed "
            "lifecycle traces, each streaming calibrated confidence."
        ),
    }


def write_thread_fleet_artifacts(output_dir: Path, report: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / f"{ARTIFACT_ID}.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Micro-thread fleet contract lab (cycle 12 D1)."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "data" / "micro_threads"
    )
    args = parser.parse_args()
    report = build_thread_fleet_report()
    write_thread_fleet_artifacts(args.output_dir, report)
    print(json.dumps(report["metrics"], indent=2))
    print(report["decision"])


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


if __name__ == "__main__":
    main()
