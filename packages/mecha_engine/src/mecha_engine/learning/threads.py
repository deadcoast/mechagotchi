"""The micro-thread fleet for mecha_engine.learning (cycle 12 D1).

Verbatim twin of ``labs/micro_threads/thread_fleet.py``, pinned by the
lab-side parity test. See the lab module for the contract prose. THE
OPT-IN RULE is load-bearing: fleet threads run only on an explicit
``learning_switches[name] is True``, so every frozen path is
byte-identical until a profile opts in.
"""

from __future__ import annotations

HISTORY_LIMIT = 8
FEED_ANTICIPATION_FLOOR = 0.55


def hunger_forecast_observe(thread_state: dict, lifecycle_state: dict) -> dict:
    history = list(thread_state.get("history", []))
    history.append(_clamp(lifecycle_state.get("hunger", 0.5)))
    return {"history": history[-HISTORY_LIMIT:]}


def hunger_forecast_signal(thread_state: dict, lifecycle_state: dict) -> dict:
    history = thread_state.get("history", [])
    if len(history) < 2:
        return _thread(
            "hunger_forecast",
            {"history_length": len(history)},
            {"predicted_hunger": None},
            0.0,
            "Cold start: no hunger trend observed yet.",
            {},
        )
    deltas = [
        round(current - previous, 6)
        for previous, current in zip(history, history[1:])
    ]
    slope = sum(deltas) / len(deltas)
    predicted = _clamp(history[-1] + slope)
    rising = sum(1 for delta in deltas if delta > 0)
    falling = sum(1 for delta in deltas if delta < 0)
    consistency = (
        max(rising, falling) / len(deltas) if any(deltas) else 0.0
    )
    confidence = round(
        min(1.0, len(history) / HISTORY_LIMIT) * (0.4 + 0.6 * consistency), 6
    )
    anticipation = max(0.0, predicted - FEED_ANTICIPATION_FLOOR)
    effects = {}
    if anticipation > 0:
        effects["feed"] = round(anticipation * 0.5, 6)
    return _thread(
        "hunger_forecast",
        {"history_length": len(history), "last_hunger": history[-1]},
        {
            "predicted_hunger": round(predicted, 6),
            "slope": round(slope, 6),
        },
        confidence,
        "Hunger trend forecast; anticipatory feeding before the reactive threshold.",
        effects,
    )


FLEET_THREADS = [
    ("hunger_forecast", hunger_forecast_observe, hunger_forecast_signal),
]
FLEET_THREAD_NAMES = [name for name, _observe, _signal in FLEET_THREADS]


def observe_fleet(lifecycle_state: dict) -> dict:
    """One observe step for every OPTED-IN fleet thread.

    Returns the new ``thread_states`` mapping (the caller stores it back
    on its state); the input state is never mutated.
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
