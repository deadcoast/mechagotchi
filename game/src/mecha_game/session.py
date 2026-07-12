"""The companion loop as a product — MVP 0.1's heart (F2).

Every beat is the engine's own machinery, mirroring the proven W1 lab
(`labs/game_loop/companion.py`) without importing it (boundary law,
DR 0033): adoption is `lifecycle.initial_state`, tending is
`advance_tick` over the action vocabulary, autonomy is
`choose_action_detailed("switchboard", ...)` — thoughts included when
the covenant grants deliberation.

The interaction model is the DOCUMENTED game model (D5's honest zero
forced it, D6 operationalized it, DR 0021 names it): **the companion
cannot feed itself.** An autonomous "feed" decision is a BEG DISPLAY
executed as ``idle`` — the tick's deliberation record still rides the
history entry, because the thought was real even though the game
mediated the act — and only the keeper's feed fills hunger.

Succession is the engine's child: `generation.generate_candidate`
from the dead parent under the same covenant, lineage preserved by
the engine (parent id, generation number, ancestor ids, mutation
events) — the client records those blocks verbatim and invents
nothing. Deterministic: the switchboard path draws no randomness and
the succession seed chain is fixed, so the only nondeterminism in a
companion's life is the player.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

from mecha_engine.generation import (
    GenerationModel,
    generate_candidate,
    train_generation_model,
)
from mecha_engine.genome import clip_frame_count, render_packet_v2
from mecha_engine.lifecycle import (
    ACTIONS,
    advance_tick,
    choose_action_detailed,
    initial_state,
)

LINEAGE_FORMAT = "keeper_lineage_v1"
# Bounded history: advance_tick deepcopies the state each tick (the
# D5-measured hotspot); decisions never read the trimmed tail, PINNED
# by test_history_trim_does_not_change_decisions.
HISTORY_WINDOW = 32
LOG_LIMIT = 100
DEFAULT_SUCCESSION_SEED = 20260712

# The needs a keeper reads at a glance (W1's display metadata —
# values are the state's, verbatim).
NEED_DISPLAY = {
    "hunger": {"label": "hunger", "good_when": "low"},
    "energy": {"label": "energy", "good_when": "high"},
    "stress": {"label": "stress", "good_when": "low"},
    "bond": {"label": "bond", "good_when": "high"},
    "grid_stability": {"label": "body stability", "good_when": "high"},
}


def load_session_inputs(
    seed_path: str | Path, slip_path: str | Path
) -> tuple[dict, dict, GenerationModel]:
    """Load a founder grid + covenant and train the succession model
    on the founder — children carry parent traits (MVP 0.1; the fuller
    generation ladder is MVP 0.2)."""
    grid = json.loads(Path(seed_path).read_text(encoding="utf-8"))
    slip_profile = json.loads(Path(slip_path).read_text(encoding="utf-8"))
    model = train_generation_model([grid])
    return grid, slip_profile, model


class CompanionSession:
    """One Keeper's companion: a living creature, its log, its lineage."""

    def __init__(
        self,
        grid: dict,
        slip_profile: dict,
        *,
        model: GenerationModel,
        name: str | None = None,
        succession_seed: int = DEFAULT_SUCCESSION_SEED,
    ) -> None:
        # The engine's own gate judges the adoption (refuses with the
        # validator's/covenant's verbatim errors).
        self.state = initial_state(grid, slip_profile)
        self.grid = json.loads(json.dumps(grid))
        self.slip_profile = json.loads(json.dumps(slip_profile))
        self.model = model
        self.name = name or grid.get("grid_id", "companion")
        self.succession_seed = succession_seed
        # The switchboard path never draws from the RNG (only the
        # `random` policy does); a fixed instance keeps calls honest.
        self._rng = random.Random(0)
        self.session_tick = 0
        self.begging = False
        self.log: list[dict] = []
        self.lineage: list[dict] = [self._lineage_record(self.grid)]

    # -- read model ------------------------------------------------------

    @property
    def alive(self) -> bool:
        return bool(self.state.get("alive", False))

    @property
    def death_cause(self) -> str | None:
        return self.state.get("death_cause")

    def snapshot(self) -> dict:
        """The numbers a frame shows — the state's own, verbatim."""
        probe = self._probe_packet()
        return {
            "name": self.name,
            "alive": self.alive,
            "death_cause": self.death_cause,
            "age_ticks": self.state["age_ticks"],
            "session_tick": self.session_tick,
            "needs": {
                key: {"value": self.state[key], **NEED_DISPLAY[key]}
                for key in NEED_DISPLAY
                if key in self.state
            },
            "mood": probe["mood"],
            "begging": self.begging,
            "ui_hints": probe["ui_hints"],
            "generation_count": len(self.lineage),
            "actions": list(ACTIONS),
            "log": list(self.log[-24:]),
        }

    def desired_clip(self) -> str:
        """The clip the companion's state asks for: the engine's own
        T16 selection via a probe packet (never a client threshold),
        beg overriding while the companion begs. The clip DRIVER walks
        the transition graph toward this target (F3)."""
        return "beg" if self.begging else self._selected_animation()

    def packet_for(self, clip: str, frame_index: int) -> dict:
        """One display frame at an explicit driver position.
        Vocabulary gating stays the engine's."""
        return render_packet_v2(
            self.grid,
            self.state,
            slip_profile=self.slip_profile,
            clip=clip,
            frame_index=frame_index % clip_frame_count(clip),
        )

    def packet(self, frame_tick: int) -> dict:
        """One display frame with naive frame cycling (evidence and
        headless harness use; the window drives the graph instead)."""
        return self.packet_for(self.desired_clip(), frame_tick)

    # -- the loop --------------------------------------------------------

    def advance(self, player_action: str | None = None) -> dict:
        """One lifecycle tick under the documented interaction model.

        The keeper's action (if any) overrides the autonomous choice;
        otherwise the switchboard decides — and a "feed" decision begs
        instead of executing (only the keeper feeds). Refused, never
        no-opped, on a dead companion or an unknown action.
        """
        if not self.alive:
            raise ValueError(
                f"the companion died of {self.death_cause} at tick "
                f"{self.state['age_ticks']} — adopt a successor"
            )
        if player_action is not None and player_action not in ACTIONS:
            raise ValueError(
                f"unsupported lifecycle action: {player_action}"
            )
        decision, thought = choose_action_detailed(
            "switchboard", self.state, self._rng
        )
        begging = decision == "feed"
        if player_action is not None:
            actor, executed, deliberation = "keeper", player_action, None
        else:
            actor = "companion"
            executed = "idle" if begging else decision
            deliberation = thought
        self.state = advance_tick(self.state, executed, deliberation)
        self.state["history"] = self.state["history"][-HISTORY_WINDOW:]
        self.session_tick += 1
        self.begging = begging and self.alive
        entry = {
            "tick": self.state["age_ticks"],
            "session_tick": self.session_tick,
            "actor": actor,
            "action": executed,
            "begging": begging,
            "alive": self.alive,
            "death_cause": self.death_cause,
        }
        if deliberation is not None:
            entry["thought"] = deliberation
        self.log = (self.log + [entry])[-LOG_LIMIT:]
        if not self.alive:
            record = self.lineage[-1]
            record["died_age_ticks"] = self.state["age_ticks"]
            record["died_session_tick"] = self.session_tick
            record["death_cause"] = self.death_cause
        return self.state

    def succeed(self) -> str:
        """Death's only door: the engine generates the child from the
        dead parent under the same covenant, lineage preserved by the
        engine; the session adopts it through the same gate."""
        if self.alive:
            raise ValueError(
                "the companion is alive — succession is death's door"
            )
        child = generate_candidate(
            self.grid,
            self.model,
            slip_profile=self.slip_profile,
            rng_seed=self.succession_seed + len(self.lineage),
        )
        self.state = initial_state(child, self.slip_profile)
        self.grid = child
        self.begging = False
        self.lineage.append(self._lineage_record(child))
        return child["grid_id"]

    # -- lineage ---------------------------------------------------------

    def _lineage_record(self, grid: dict) -> dict:
        return {
            "grid_id": grid["grid_id"],
            "parent_grid_id": grid.get("parent_grid_id"),
            # The engine's own lineage block, verbatim.
            "lineage": json.loads(json.dumps(grid.get("lineage"))),
            "born_session_tick": self.session_tick,
        }

    def lineage_document(self) -> dict:
        return {
            "lineage_format": LINEAGE_FORMAT,
            "keeper_name": self.name,
            "records": list(self.lineage),
        }

    def save_lineage(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            path.with_suffix(".bak.json").write_text(
                path.read_text(encoding="utf-8"), encoding="utf-8"
            )
        path.write_text(
            json.dumps(self.lineage_document(), indent=2) + "\n",
            encoding="utf-8",
        )
        return path

    # -- internals -------------------------------------------------------

    def _probe_packet(self) -> dict:
        """The engine's own selection (animation + mood + ui_hints)
        for the current state — the no-clip packet."""
        return render_packet_v2(
            self.grid, self.state, slip_profile=self.slip_profile
        )

    def _selected_animation(self) -> str:
        return self._probe_packet()["animation"]
