"""The Review step — a real recorded life plays back (F10, R5/G3).

The R5 recorder's contract mirrored over engine publics
(`labs/game_loop/replay_recorder.py` — mirrored, never imported):
one `runtime.live_cycle(record_frames=True)` run (DR 0023's engine
seam) becomes a frame sequence — birth, per-cycle wound (the damage
event's own `removed_cells`), repair (with restoration fidelity and
the validator's verdicts), and every episode tick. **The replay never
invents a displayable body**: packets exist only for
validator-passing states, errors ride verbatim otherwise, and the
scrubber invariant is the shared drawer's — the body at frame i is
the latest packet-bearing frame ≤ i.
"""

from __future__ import annotations

import hashlib
import json

from mecha_engine.genome import render_packet_from_grid, validate_grid
from mecha_engine.runtime import live_cycle
from mecha_game.thought_view import thought_lines

REPLAY_FORMAT = "mechagotchi_replay_v1"
RECOMPUTED_IDENTITY_FORMAT = "mechagotchi_recomputed_replay_v2"


def packet_or_errors(grid: dict) -> tuple[dict | None, list[str]]:
    """A render packet for a valid body, or the validator's errors
    verbatim — the replay never invents a displayable body."""
    result = validate_grid(grid)
    if not result.ok:
        return None, list(result.errors)
    return render_packet_from_grid(grid), []


def build_replay(
    grid: dict,
    slip_profile: dict,
    repair_model: dict,
    *,
    damage_cycles: int = 3,
    ticks: int = 48,
    dropout_rate: float = 0.2,
    rng_seed: int = 20260707,
    body_response: str = "legacy",
) -> dict:
    """Run a fresh preview, retaining the historical frame schema.

    Only recomputation gets the versioned identity: original evaluation
    captures continue using replay_from_lived without altered evidence.
    """
    from mecha_game.body_response import validate_body_response
    validate_body_response(body_response)
    identity_inputs = {
        "format": RECOMPUTED_IDENTITY_FORMAT,
        "grid": grid,
        "slip_profile": slip_profile,
        "repair_model": repair_model,
        "body_response": body_response,
        "damage_cycles": damage_cycles,
        "ticks": ticks,
        "dropout_rate": dropout_rate,
        "rng_seed": rng_seed,
    }
    inputs_sha256 = hashlib.sha256(json.dumps(
        identity_inputs, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")).hexdigest()
    lived = live_cycle(
        grid,
        slip_profile,
        repair_model,
        damage_cycles=damage_cycles,
        ticks=ticks,
        dropout_rate=dropout_rate,
        rng_seed=rng_seed,
        record_frames=True,
        **({"body_response": body_response} if body_response != "legacy" else {}),
    )

    replay = replay_from_lived(grid, slip_profile, lived, damage_cycles=damage_cycles,
                               ticks=ticks, dropout_rate=dropout_rate, rng_seed=rng_seed)
    replay["replay_id"] = "preview-v2-" + inputs_sha256
    replay["replay_identity"] = {
        "format": RECOMPUTED_IDENTITY_FORMAT,
        "kind": "recomputed_preview",
        "body_response": body_response,
        "inputs_sha256": inputs_sha256,
    }
    return replay


def replay_from_lived(grid, slip_profile, lived, *, damage_cycles, ticks, dropout_rate, rng_seed):
    """Lay out already captured engine frames; never simulate or consume RNG."""
    frames: list[dict] = []
    birth_packet, birth_errors = packet_or_errors(grid)
    frames.append(
        {
            "frame": 0,
            "phase": "birth",
            "cycle": 0,
            "packet": birth_packet,
            "validation_errors": birth_errors,
        }
    )
    for cycle_entry in lived["cycles"]:
        cycle = cycle_entry["cycle"]
        recorded = cycle_entry["frames"]
        frames.append(
            {
                "frame": len(frames),
                "phase": "wound",
                "cycle": cycle,
                "removed_cells": recorded["removed_cells"],
                "removed_cell_count": cycle_entry["removed_cell_count"],
            }
        )
        repaired_packet, repaired_errors = packet_or_errors(
            recorded["repaired_grid"]
        )
        frames.append(
            {
                "frame": len(frames),
                "phase": "repair",
                "cycle": cycle,
                "packet": repaired_packet,
                "validation_errors": repaired_errors,
                "position_restoration": cycle_entry[
                    "position_restoration"
                ],
                "token_restoration": cycle_entry["token_restoration"],
                "guard_substitutions": cycle_entry[
                    "guard_substitutions"
                ],
                "valid": cycle_entry["valid"],
                "aligned": cycle_entry["aligned"],
            }
        )
        for entry in recorded["episode_history"] or []:
            frames.append(
                {
                    "frame": len(frames),
                    "phase": "episode_tick",
                    "cycle": cycle,
                    "tick": entry["tick"],
                    "entry": entry,
                }
            )

    digest_cycles = [
        {key: value for key, value in cycle.items() if key != "frames"}
        for cycle in lived["cycles"]
    ]
    return {
        "replay_format": REPLAY_FORMAT,
        "replay_id": f"{grid['grid_id']}_seed{rng_seed}",
        "engine_surface": (
            "mecha_engine.runtime.live_cycle(record_frames=True)"
        ),
        "creature": {
            "grid_id": grid["grid_id"],
            "profile_id": slip_profile.get("profile_id"),
        },
        "parameters": {
            "damage_cycles": damage_cycles,
            "ticks": ticks,
            "dropout_rate": dropout_rate,
            "rng_seed": rng_seed,
            **({"body_response": lived["body_response"]} if "body_response" in lived else {}),
        },
        "live": {
            "cycles": digest_cycles,
            "all_cycles_valid": lived["all_cycles_valid"],
            "all_cycles_aligned": lived["all_cycles_aligned"],
            "final_state": lived["final_state"],
        },
        "frames": frames,
        "frame_count": len(frames),
        "tick_frame_count": sum(
            1 for frame in frames if frame["phase"] == "episode_tick"
        ),
    }


WOUND_COLOR = (200, 60, 40)
WOUND_ALPHA = 0.75  # the shared drawer's woundOverlay fill, as math


def overlay_wounds(buffer, removed_cells) -> tuple:
    """The wound overlay at grid resolution — the damage event's own
    removed_cells (engine observability truth) blended over the body,
    the shared drawer's fill as arithmetic."""
    keep = 1 - WOUND_ALPHA
    marked = {(x, y) for x, y in removed_cells}
    return tuple(
        tuple(
            (
                round(r * keep + WOUND_COLOR[0] * WOUND_ALPHA),
                round(g * keep + WOUND_COLOR[1] * WOUND_ALPHA),
                round(b * keep + WOUND_COLOR[2] * WOUND_ALPHA),
            )
            if (x, y) in marked
            else (r, g, b)
            for x, (r, g, b) in enumerate(row)
        )
        for y, row in enumerate(buffer)
    )


class ReplayPlayer:
    """Scrubber-lite over a recorded life: step, back, the body at
    the cursor (the shared drawer's invariant), and an engine-truth
    caption per frame."""

    def __init__(self, replay: dict) -> None:
        self.replay = replay
        self.index = 0

    def step(self) -> int:
        self.index = min(
            self.replay["frame_count"] - 1, self.index + 1
        )
        return self.index

    def back(self) -> int:
        self.index = max(0, self.index - 1)
        return self.index

    def current(self) -> dict:
        return self.replay["frames"][self.index]

    def body_packet_at(self, index: int) -> dict | None:
        """The body at frame i = the latest packet-bearing frame ≤ i
        (`workshop/shared/draw.js` bodyPacketAt, mirrored)."""
        for i in range(index, -1, -1):
            frame = self.replay["frames"][i]
            if frame.get("packet"):
                return frame["packet"]
        return None

    def body_packet(self) -> dict | None:
        return self.body_packet_at(self.index)

    def wound_cells(self) -> list | None:
        """The current frame's wound, when it is one (the damage
        event's own removed_cells — engine observability truth)."""
        frame = self.current()
        if frame["phase"] == "wound":
            return frame["removed_cells"]
        return None

    def caption(self) -> str:
        frame = self.current()
        parts = [
            f"frame {frame['frame']}/{self.replay['frame_count'] - 1}",
            f"{frame['phase']}",
            f"cycle {frame['cycle']}",
        ]
        if frame["phase"] == "wound":
            parts.append(f"{frame['removed_cell_count']} cells lost")
        if frame["phase"] == "repair":
            parts.append(
                f"restoration {frame['position_restoration']:.2f}"
            )
        if frame["phase"] == "episode_tick":
            parts.append(f"tick {frame['tick']}")
        return "  ".join(parts)

    def provenance_lines(self) -> list[str]:
        """Describe stored model provenance without consulting the current life."""
        parameters = self.replay.get("parameters", {})
        model = parameters.get("body_response", "legacy")
        if model not in ("legacy", "workload-v1"):
            return ["Unknown recorded body response; frames retained as recorded."]
        model_line = f"Recorded body response: {model}."
        identity = self.replay.get("replay_identity")
        if (isinstance(identity, dict)
                and identity.get("format") == RECOMPUTED_IDENTITY_FORMAT
                and identity.get("kind") == "recomputed_preview"):
            return [model_line, "Recomputed preview: a new simulation, not original Keeper footage."]
        evaluation = self.replay.get("evaluation")
        if (isinstance(evaluation, dict)
                and evaluation.get("kind") == "mechagotchi_original_evaluation_v1"):
            return [model_line, "Original recorded evaluation; model belongs to the recorded era."]
        return [model_line, "Saved recording; omitted historical model fields mean legacy."]

    def thought_lines(self) -> list[str]:
        """The selected recorded episode's thought, never an earlier frame's."""
        frame = self.current()
        entry = frame.get("entry")
        if (frame.get("phase") != "episode_tick" or not isinstance(entry, dict)
                or type(frame.get("tick")) is not int or type(entry.get("tick")) is not int
                or entry["tick"] != frame["tick"]):
            return []
        return thought_lines(entry.get("deliberation"), tick=frame["tick"],
                             action=entry.get("action"), recorded=True)
