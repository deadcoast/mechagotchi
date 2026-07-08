"""The living companion (W1) — the tamagotchi heart, on the engine's tick.

Every prior surface showed the ecosystem from above (eras, archives,
replays). This module is the companion experience the og fantasy names:
ONE creature, alive on screen, that the player tends — and every beat of
it is the engine's own machinery:

- **Adopt** — `mecha_engine.lifecycle.initial_state(grid, profile)`:
  the engine itself validates the body and the covenant and refuses a
  misaligned adoption with its own errors.
- **Tend** — the player's buttons ARE the engine's action vocabulary
  (`lifecycle.ACTIONS`: feed/play/sleep/idle/mutate), each one an
  `advance_tick` — the same transition every episode in every era runs.
- **Live** — between the player's actions the creature acts for itself:
  `choose_action_detailed("switchboard", state, ...)` — the same frozen
  switchboard that plays every era, thoughts included (a deliberation
  covenant makes the companion visibly think, F1's record live rather
  than replayed).
- **Appear** — every frame is `genome.render_packet_v2(grid, state,
  slip_profile=...)`: mood and animation selected from the lifecycle
  state, bounded by the species' visual grammar (E1's gate).
- **Die** — honestly: an exhausted or starved companion dies with the
  engine's named cause, and tending a dead companion is refused, not
  no-opped. Adoption of a successor is the only way on.

State persists as play state (`keeper/companion.json`, gitignored —
a live pet is not evidence). Deterministic: the switchboard path draws
no randomness; the only nondeterminism in a companion's life is the
player.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from mecha_engine.genome import render_packet_v2  # noqa: E402
from mecha_engine.lifecycle import (  # noqa: E402
    ACTIONS,
    advance_tick,
    choose_action_detailed,
    initial_state,
)

COMPANION_FORMAT = "keeper_companion_v1"
# The switchboard path never draws from the RNG (only the `random`
# policy does); a fixed instance keeps the call signature honest.
_SWITCHBOARD_RNG = random.Random(0)

# The needs a keeper reads at a glance, with the direction that means
# "content" (display metadata only — values are the state's, verbatim).
NEED_DISPLAY = {
    "hunger": {"label": "hunger", "good_when": "low"},
    "energy": {"label": "energy", "good_when": "high"},
    "stress": {"label": "stress", "good_when": "low"},
    "bond": {"label": "bond", "good_when": "high"},
    "grid_stability": {"label": "body stability", "good_when": "high"},
}


def adopt_companion(
    grid: dict,
    slip_profile: dict,
    *,
    source: dict,
    name: str | None = None,
) -> dict:
    """Adopt a creature as THE companion. The engine's own gate judges
    the adoption: `initial_state` raises with the validator's or the
    covenant's verbatim errors when the body or the match is wrong."""
    state = initial_state(grid, slip_profile)
    return {
        "companion_format": COMPANION_FORMAT,
        "name": name or grid.get("grid_id", "companion"),
        "grid": json.loads(json.dumps(grid)),
        "slip_profile": json.loads(json.dumps(slip_profile)),
        "source": dict(source),
        "state": state,
        "log": [],  # the companion's recent moments (bounded)
    }


def _remember(companion: dict, entry: dict) -> None:
    companion["log"] = (companion["log"] + [entry])[-24:]


def companion_snapshot(companion: dict) -> dict:
    """The read model one heartbeat renders: the state's own numbers,
    the packet-v2 frame (mood + animation from the state, vocabulary
    from the covenant), and the recent moments."""
    state = companion["state"]
    packet = render_packet_v2(
        companion["grid"],
        state,
        slip_profile=companion["slip_profile"],
    )
    return {
        "companion_format": companion["companion_format"],
        "name": companion["name"],
        "source": companion["source"],
        "alive": state["alive"],
        "death_cause": state["death_cause"],
        "age_ticks": state["age_ticks"],
        "needs": {
            key: {"value": state[key], **NEED_DISPLAY[key]}
            for key in NEED_DISPLAY
        },
        "mood": packet["mood"],
        "animation": packet["animation"],
        "animation_vocabulary": packet["animation_vocabulary"],
        "packet": packet,
        "actions": list(ACTIONS),
        "log": list(companion["log"]),
    }


def player_act(companion: dict, action: str) -> dict:
    """The player tends the companion — one engine tick, the player's
    choice. Refused (never no-opped) on a dead companion or an unknown
    action; the engine's transition does the rest."""
    state = companion["state"]
    if not state["alive"]:
        raise ValueError(
            f"the companion died of {state['death_cause']} at tick "
            f"{state['age_ticks']} — adopt a successor"
        )
    if action not in ACTIONS:
        raise ValueError(f"unsupported lifecycle action: {action}")
    companion["state"] = advance_tick(state, action)
    _remember(
        companion,
        {
            "tick": companion["state"]["age_ticks"],
            "actor": "keeper",
            "action": action,
            "alive": companion["state"]["alive"],
            "death_cause": companion["state"]["death_cause"],
        },
    )
    return companion["state"]


def autonomous_tick(companion: dict) -> tuple[dict, str, dict | None]:
    """The companion lives on its own for one tick: the frozen
    switchboard chooses (thought included when the covenant grants
    deliberation), then the same engine transition runs."""
    state = companion["state"]
    if not state["alive"]:
        raise ValueError(
            f"the companion died of {state['death_cause']} at tick "
            f"{state['age_ticks']} — adopt a successor"
        )
    action, thought = choose_action_detailed(
        "switchboard", state, _SWITCHBOARD_RNG
    )
    companion["state"] = advance_tick(state, action, deliberation=thought)
    entry = {
        "tick": companion["state"]["age_ticks"],
        "actor": "companion",
        "action": action,
        "alive": companion["state"]["alive"],
        "death_cause": companion["state"]["death_cause"],
    }
    if thought is not None:
        entry["thought"] = thought
    _remember(companion, entry)
    return companion["state"], action, thought


def save_companion(companion: dict, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.with_suffix(".bak.json").write_text(
            path.read_text(encoding="utf-8"), encoding="utf-8"
        )
    path.write_text(
        json.dumps(companion, indent=2) + "\n", encoding="utf-8"
    )


def load_companion(path: str | Path) -> dict | None:
    path = Path(path)
    if not path.exists():
        return None
    companion = json.loads(path.read_text(encoding="utf-8"))
    if companion.get("companion_format") != COMPANION_FORMAT:
        raise ValueError("not a keeper_companion_v1 state")
    return companion
