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

import dataclasses
import json
import hashlib
import os
import tempfile
import math
import random
from pathlib import Path

from mecha_engine.generation import (
    GenerationModel,
    generate_candidate,
    train_generation_model,
)
from mecha_engine.genome import clip_frame_count, render_packet_v2
from mecha_engine.learning import decide, fleet_signals, observe_fleet
from mecha_engine.lifecycle import (
    ACTIONS,
    advance_tick,
    choose_action_detailed,
    initial_state,
)

from .happiness import happiness_readout
from .health import health_readout

LINEAGE_FORMAT = "keeper_lineage_v1"
SESSION_FORMAT = "keeper_session_v1"
# The D6 ablation verdicts, applied without sentiment: exactly the five
# KEPT threads run in the game; dropped threads stay out of default
# profiles (data/micro_threads/ablation_gates_stage0.json).
KEPT_THREADS = (
    "hunger_forecast",
    "energy_forecast",
    "interaction_timing",
    "animation_bandit",
    "hidden_mood_hmm",
)
# Bounded history: advance_tick deepcopies the state each tick (the
# D5-measured hotspot); decisions never read the trimmed tail, PINNED
# by test_history_trim_does_not_change_decisions.
HISTORY_WINDOW = 32
LOG_LIMIT = 100
DEFAULT_SUCCESSION_SEED = 20260712

# The needs a keeper reads at a glance (W1's display metadata —
# values are the state's, verbatim). `cleanliness` appears only when a
# session opts into the engine's mechanic (P3, DR 0059): the needs loop
# below shows a key only when the state carries it, so a default
# session's read model is byte-identical to the pre-seam client.
NEED_DISPLAY = {
    "hunger": {"label": "hunger", "good_when": "low"},
    "energy": {"label": "energy", "good_when": "high"},
    "stress": {"label": "stress", "good_when": "low"},
    "bond": {"label": "bond", "good_when": "high"},
    "grid_stability": {"label": "body stability", "good_when": "high"},
    "cleanliness": {"label": "cleanliness", "good_when": "high"},
}
CLEAN_ACTION = "clean"
LEARNING_POLICIES = ("incumbent", "qtable")


def _validate_learning_policy(policy: object) -> str:
    if not isinstance(policy, str) or policy not in LEARNING_POLICIES:
        raise ValueError("learning policy must be incumbent or qtable")
    return policy


def _validate_saved_qtable(state: dict, policy: str, fleet: bool) -> None:
    """Reject inconsistent or malformed experimental state before resuming."""
    if not isinstance(state, dict):
        raise ValueError("invalid saved learning state")
    switches = state.get("learning_switches") or {}
    states = state.get("thread_states") or {}
    if not isinstance(switches, dict) or not isinstance(states, dict):
        raise ValueError("invalid saved Q-table learning state")
    expected = policy == "qtable" and fleet
    if any((switches.get(key) is True) != expected
           for key in ("qtable_policy", "qtable_consumer")):
        raise ValueError("saved learning policy conflicts with its Q-table switches")
    thread = states.get("qtable_policy")
    if thread is None:
        return
    if not expected or not isinstance(thread, dict):
        raise ValueError("invalid saved Q-table state")
    table = thread.get("q", {})
    buckets = {f"{h}{e}" for h in range(3) for e in range(3)}
    keys = {f"{bucket}|{action}" for bucket in buckets for action in ACTIONS}
    if not isinstance(table, dict) or not set(table).issubset(keys):
        raise ValueError("invalid saved Q-table entries")
    pending = thread.get("pending_bucket")
    if pending is not None and (not isinstance(pending, str) or pending not in buckets):
        raise ValueError("invalid saved Q-table pending bucket")
    for record in table.values():
        if not isinstance(record, dict):
            raise ValueError("invalid saved Q-table reward")
        count, value = record.get("n"), record.get("mean")
        if (type(count) is not int or count < 1 or type(value) not in (int, float)
                or not math.isfinite(value) or not 0 <= value <= 1):
            raise ValueError("invalid saved Q-table reward")


def _write_bytes_atomic(path: Path, data: bytes) -> None:
    """Replace one save only after its complete bytes have reached a sibling file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _document_bytes(document: dict) -> bytes:
    # Match the established platform text-file convention, while preserving
    # existing backup/archive bytes verbatim instead of decoding them.
    return (json.dumps(document, indent=2) + "\n").replace("\n", os.linesep).encode("utf-8")


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
        fleet: bool = True,
        origin: str = "founder",
        mechanics: tuple | list | None = None,
        learning_policy: str = "incumbent",
    ) -> None:
        # The engine's own gate judges the adoption (refuses with the
        # validator's/covenant's verbatim errors). `mechanics` (P3,
        # DR 0059 / DR 0063) overrides covenant mechanics. None inherits;
        # an explicit empty sequence disables. Ordinary off-mode is unchanged.
        self.learning_policy = _validate_learning_policy(learning_policy)
        self.mechanics = None if mechanics is None else tuple(mechanics)
        self.state = initial_state(grid, slip_profile, mechanics=self.mechanics)
        self.fleet = fleet
        if fleet:
            # The kept fleet opts in (the load-bearing D1 rule: an
            # explicit True per name; covenant-carried switches stay).
            self.state["learning_switches"] = {
                **(self.state.get("learning_switches") or {}),
                **{name: True for name in KEPT_THREADS},
                **({"qtable_policy": True, "qtable_consumer": True}
                   if self.learning_policy == "qtable" else {}),
            }
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
        # ``origin`` (F14, additive): how this life began — founder /
        # hatched / era_elite / succession — a Keeper fact the engine
        # does not own, recorded alongside the engine's lineage block.
        self.lineage: list[dict] = [
            self._lineage_record(self.grid, origin=origin)
        ]

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
            **({"learning_policy": self.learning_policy, "learning_active": self.fleet}
               if self.learning_policy == "qtable" else {}),
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
            # O2 (DR 0054): the adopted CHOSEN definition of `health`,
            # carried with the axis that binds it — a bare minimum
            # throws away the one thing that makes it legible, and the
            # keeper's `play` verb LOWERS it (play costs energy), so the
            # readout has to be able to say why.
            "health": health_readout(self.state),
            # P2 (DR 0058): the adopted CHOSEN definition of
            # `happiness` — the engine's own recent-interaction window.
            # Play RAISES it while it lowers `health`; both are engine
            # truth and the two bars answer different questions.
            "happiness": happiness_readout(self.state),
            "begging": self.begging,
            "ui_hints": probe["ui_hints"],
            "generation_count": len(self.lineage),
            # The keeper's verbs: the engine vocabulary, plus `clean`
            # exactly when the session runs the mechanic (P3, DR 0059).
            "actions": list(ACTIONS)
            + ([CLEAN_ACTION] if CLEAN_ACTION in self._extra_actions() else []),
            "log": list(self.log[-24:]),
            # The kept threads' signals, verbatim (D1 shape) — the
            # fleet's game-side read model (empty with the fleet off).
            "threads": {
                signal["name"]: {
                    "output": signal["output"],
                    "confidence": signal["confidence"],
                    "explanation": signal["explanation"],
                    "effects": signal["effects"],
                }
                for signal in (
                    fleet_signals(self.state) if self.fleet else []
                )
            },
        }

    def desired_clip(self) -> str:
        """The clip the companion's state asks for: the engine's own
        T16 selection via a probe packet (never a client threshold),
        beg overriding while the companion begs. The clip DRIVER walks
        the transition graph toward this target (F3).

        The bandit consumer (D3: clip preference is PACKET-side,
        honestly effect-free): when the engine selects plain idle and
        the kept bandit has a confident learned recommendation, the
        recommendation is displayed instead — the thread's own output,
        never a client heuristic."""
        if self.begging:
            return "beg"
        selected = self._selected_animation()
        if self.fleet and selected == "idle":
            bandit = self._thread_signal("animation_bandit")
            if bandit is not None and bandit["confidence"] > 0:
                recommended = bandit["output"].get("recommended_clip")
                if isinstance(recommended, str):
                    return recommended
        return selected

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

    def advance(
        self,
        player_action: str | None = None,
        displayed_clip: str | None = None,
    ) -> dict:
        """One lifecycle tick under the documented interaction model.

        The keeper's action (if any) overrides the autonomous choice;
        otherwise the switchboard decides — and a "feed" decision begs
        instead of executing (only the keeper feeds). Refused, never
        no-opped, on a dead companion or an unknown action.

        With the fleet on, the D6 wiring runs first each tick (the
        lab's exact order): ``last_animation`` is what the display
        actually showed (``displayed_clip`` from the window's clip
        driver; the engine's own selection when absent — the bandit's
        reward attribution input), then ``observe_fleet`` refreshes
        ``thread_states``, then the switchboard decides with the kept
        threads' signals riding its additive seam.
        """
        if not self.alive:
            raise ValueError(
                f"the companion died of {self.death_cause} at tick "
                f"{self.state['age_ticks']} — adopt a successor"
            )
        if player_action is not None and player_action not in (
            tuple(ACTIONS) + self._extra_actions()
        ):
            raise ValueError(
                f"unsupported lifecycle action: {player_action}"
            )
        if self.fleet:
            self.state["last_animation"] = (
                displayed_clip
                if displayed_clip is not None
                else self._selected_animation()
            )
            self.state["thread_states"] = observe_fleet(self.state)
        decision, thought = choose_action_detailed(
            "switchboard", self.state, self._rng,
            **({"decision_function": decide}
               if self.fleet and self.learning_policy == "qtable" else {}),
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
        # The Keeper's opted-in mechanics carry across successions —
        # they are covenant-level choices, not per-life ones.
        self.state = initial_state(
            child, self.slip_profile, mechanics=self.mechanics
        )
        if self.fleet:
            # The Keeper's fleet stays opted in across successions;
            # thread MEMORY starts fresh — it belonged to the parent
            # (the D1 threads are per-companion learners).
            self.state["learning_switches"] = {
                **(self.state.get("learning_switches") or {}),
                **{name: True for name in KEPT_THREADS},
                **({"qtable_policy": True, "qtable_consumer": True}
                   if self.learning_policy == "qtable" else {}),
            }
        self.grid = child
        self.begging = False
        self.lineage.append(
            self._lineage_record(child, origin="succession")
        )
        return child["grid_id"]

    # -- lineage ---------------------------------------------------------

    def _lineage_record(self, grid: dict, *, origin: str) -> dict:
        return {
            "grid_id": grid["grid_id"],
            "parent_grid_id": grid.get("parent_grid_id"),
            # The engine's own lineage block, verbatim.
            "lineage": json.loads(json.dumps(grid.get("lineage"))),
            "born_session_tick": self.session_tick,
            "origin": origin,
            **({"learning_policy": self.learning_policy}
               if self.learning_policy == "qtable" else {}),
        }

    def lineage_document(self) -> dict:
        return {
            "lineage_format": LINEAGE_FORMAT,
            "keeper_name": self.name,
            "records": list(self.lineage),
        }

    def save_lineage(self, path: str | Path) -> Path:
        path = Path(path)
        data = _document_bytes(self.lineage_document())
        if path.exists():
            _write_bytes_atomic(path.with_suffix(".bak.json"), path.read_bytes())
        _write_bytes_atomic(path, data)
        return path

    def sync_lineage_export(self, path: str | Path) -> bool:
        """Repair the derived export from this validated companion, preserving old bytes."""
        path = Path(path)
        if path.exists() and path.read_bytes() == _document_bytes(self.lineage_document()):
            return False
        self.save_lineage(path)
        return True

    def save_checkpoint(self, path: str | Path) -> str | None:
        """Commit the complete pet first; an export failure cannot discard progress.

        The companion already embeds its lineage. A stale standalone export is
        repaired on resume, including after explicit S1 backup recovery.
        """
        path = Path(path)
        self.save(path, only_if_changed=True)
        try:
            self.sync_lineage_export(path.with_name("lineage.json"))
        except OSError as error:
            reason = error.strerror or str(error)
            return f"Companion saved. Lineage export unavailable: {reason}. It will retry on resume."
        return None

    # -- save / resume (F5 — quit and come back) ---------------------------

    def save(self, path: str | Path, *, only_if_changed: bool = False) -> Path:
        """Persist the LIVE session (state, log, lineage, and the
        succession model verbatim) with the W1 backup-before-overwrite
        pattern. A live pet is play state, never evidence."""
        self.model.validate_for(self.grid["grid_size"])
        _validate_learning_policy(self.learning_policy)
        _validate_saved_qtable(self.state, self.learning_policy, self.fleet)
        payload = {
            "session_format": SESSION_FORMAT,
            "name": self.name,
            "grid": self.grid,
            "slip_profile": self.slip_profile,
            "state": self.state,
            "session_tick": self.session_tick,
            "begging": self.begging,
            "fleet": self.fleet,
            "succession_seed": self.succession_seed,
            "log": self.log,
            "lineage": self.lineage,
            "generation_model": dataclasses.asdict(self.model),
        }
        if self.learning_policy != "incumbent":
            payload["learning_policy"] = self.learning_policy
        # Rung-conditional (the engine's own convention): only sessions
        # that opted into mechanics carry the key, so a default save is
        # byte-identical to the pre-seam format.
        # An explicit empty override needs persistence only when it disables
        # a covenant-carried opt-in. Ordinary off-mode saves retain their shape.
        profile_enabled = self.slip_profile.get("mechanics", {}).get("cleanliness") is True
        if self.mechanics or (self.mechanics is not None and profile_enabled):
            payload["mechanics"] = list(self.mechanics)
        path = Path(path)
        data = _document_bytes(payload)
        if only_if_changed and path.is_file() and path.read_bytes() == data:
            return path
        if path.exists():
            _write_bytes_atomic(path.with_suffix(".bak.json"), path.read_bytes())
        _write_bytes_atomic(path, data)
        return path

    @classmethod
    def recover_backup(cls, path: str | Path, *, learning_policy: str | None = None):
        """Explicitly restore a validated backup, retaining the previous primary."""
        path = Path(path)
        backup = path.with_suffix(".bak.json")
        if not backup.is_file():
            raise ValueError("no companion backup is available to recover")
        restored_bytes = backup.read_bytes()
        session = cls._from_payload(json.loads(restored_bytes.decode("utf-8")), learning_policy=learning_policy)
        archive = None
        if path.exists():
            previous = path.read_bytes()
            digest = hashlib.sha256(previous).hexdigest()[:16]
            archive = path.with_name(f"{path.stem}.before-recovery-{digest}{path.suffix}")
            try:
                with archive.open("xb") as stream:
                    stream.write(previous)
                    stream.flush()
                    os.fsync(stream.fileno())
            except FileExistsError:
                if archive.read_bytes() != previous:
                    raise ValueError("recovery archive already exists with different contents")
        _write_bytes_atomic(path, restored_bytes)
        return session, archive

    @classmethod
    def load(cls, path: str | Path, *, learning_policy: str | None = None) -> "CompanionSession":
        """Resume a saved session exactly where it stopped. The fixed
        RNG instance is recreated fresh — the switchboard path never
        draws from it, so a resumed life continues byte-identically
        (pinned by test against a never-saved twin)."""
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls._from_payload(payload, learning_policy=learning_policy)

    @classmethod
    def _from_payload(cls, payload, *, learning_policy: str | None = None):
        """Validate one exact read snapshot; never reread different backup bytes."""
        if not isinstance(payload, dict):
            raise ValueError("invalid companion save: expected an object")
        if payload.get("session_format") != SESSION_FORMAT:
            raise ValueError(
                "not a keeper session save: "
                f"{payload.get('session_format')!r}"
            )
        required = {"state": dict, "grid": dict, "slip_profile": dict, "generation_model": dict,
                    "name": str, "succession_seed": int, "session_tick": int, "fleet": bool,
                    "begging": bool, "log": list, "lineage": list}
        for name, expected in required.items():
            if type(payload.get(name)) is not expected:
                raise ValueError(f"invalid companion save field: {name}")
        if "mechanics" in payload and (not isinstance(payload["mechanics"], list) or
                any(not isinstance(name, str) for name in payload["mechanics"])):
            raise ValueError("invalid companion save mechanics")
        try:
            mechanics = tuple(payload["mechanics"]) if "mechanics" in payload else None
            # Validate the body/covenant through the existing engine gate;
            # never replace or reset the saved lifecycle/learning state.
            initial_state(payload["grid"], payload["slip_profile"], mechanics=mechanics)
            model = GenerationModel(**payload["generation_model"])
            model.validate_for(payload["grid"]["grid_size"])
        except (KeyError, TypeError, AttributeError) as error:
            raise ValueError("invalid companion save body, covenant or generation model") from error
        state = payload["state"]
        if (type(state.get("alive")) is not bool or type(state.get("age_ticks")) is not int or
                state["age_ticks"] < 0 or payload["session_tick"] < state["age_ticks"] or
                not isinstance(state.get("history"), list) or
                any(not isinstance(row, dict) for row in state["history"])):
            raise ValueError("invalid saved lifecycle state")
        for name in ("hunger", "energy", "stress", "bond", "grid_stability"):
            value = state.get(name)
            if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"invalid saved lifecycle need: {name}")
        saved_policy = _validate_learning_policy(payload.get("learning_policy", "incumbent"))
        if learning_policy is not None and _validate_learning_policy(learning_policy) != saved_policy:
            raise ValueError("learning policy conflicts with the saved companion; use --new or a separate --keeper-dir")
        _validate_saved_qtable(payload["state"], saved_policy, payload["fleet"])
        session = cls.__new__(cls)
        session.learning_policy = saved_policy
        session.state = payload["state"]
        session.grid = payload["grid"]
        session.slip_profile = payload["slip_profile"]
        session.model = model
        session.name = payload["name"]
        session.succession_seed = payload["succession_seed"]
        session.fleet = payload["fleet"]
        session.mechanics = mechanics
        session._rng = random.Random(0)
        session.session_tick = payload["session_tick"]
        session.begging = payload["begging"]
        session.log = payload["log"]
        session.lineage = payload["lineage"]
        try:
            session.snapshot()
            if session.fleet:
                observe_fleet(session.state)  # pure validation; discard the proposed update
        except (KeyError, TypeError, AttributeError, ValueError) as error:
            raise ValueError("invalid saved companion display or learning state") from error
        return session

    # -- internals -------------------------------------------------------

    def _probe_packet(self) -> dict:
        """The engine's own selection (animation + mood + ui_hints)
        for the current state — the no-clip packet."""
        return render_packet_v2(
            self.grid, self.state, slip_profile=self.slip_profile
        )

    def _selected_animation(self) -> str:
        return self._probe_packet()["animation"]

    def _thread_signal(self, name: str) -> dict | None:
        for signal in fleet_signals(self.state):
            if signal["name"] == name:
                return signal
        return None

    def _extra_actions(self) -> tuple:
        """The keeper verbs the opted-in mechanics add (P3, DR 0059)."""
        return (CLEAN_ACTION,) if "cleanliness" in self.state else ()
