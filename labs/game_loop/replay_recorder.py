"""Replay recorder — a creature's life as recorded engine truth (R5).

DR 0017 R5 / DR 0021's Review step: "per-tick render packets from
live_cycle/episodes into a replay artifact; the preview gains a scrubber
(engine truth, recorded). The player's window."

The recorder runs `mecha_engine.runtime.live_cycle(record_frames=True)`
(the DR 0023 engine seam) and lays the life out as a scrubber timeline:

- **birth** — the creature's render packet before anything happens;
- **wound** (per cycle) — the damage event's `removed_cells` VERBATIM
  (the repair observability contract: destroyed positions, never
  tokens); the scrubber overlays them on the current body;
- **repair** (per cycle) — the repaired body's render packet, or — when
  a repair comes back invalid (the measured aligned-but-invalid
  boundary) — the validator's errors verbatim instead of a packet,
  never a crash and never a fake body;
- **episode_tick** (per tick) — the episode's own per-tick history
  entry (action, need balance, recoveries, alive/death-cause, full
  state snapshot, R1 deliberation fields when the covenant carries
  them); the scrubber animates these over the cycle's repaired body.

Every frame is a report field, an artifact, or a grid the engine
produced — nothing is synthesized for display (DR 0021's first law).
An unaligned cycle ends the recording exactly where the engine ends the
life; the cut IS the replay. Deterministic end to end; inputs are never
mutated; the artifact is JSON-serializable and carries the parameters
(seed included) that reproduce it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from mecha_engine.genome import (  # noqa: E402
    render_packet_from_grid,
    validate_grid,
)
from mecha_engine.repair import train_repair_model  # noqa: E402
from mecha_engine.runtime import live_cycle  # noqa: E402

ARTIFACT_ID = "game_loop_replay_recorder_stage0"
REPORT_DATE = "2026-07-07"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "game_loop"
SEED_GRID_PATH = ROOT / "data" / "seed_grids" / "mg_seed_001.json"
SLIP_PROFILE_PATH = ROOT / "data" / "slips" / "valid" / "slip_lcd_seed.json"
REPLAY_FORMAT = "mechagotchi_replay_v1"


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
) -> dict:
    """Record one creature's live_cycle as a replay artifact."""
    lived = live_cycle(
        grid,
        slip_profile,
        repair_model,
        damage_cycles=damage_cycles,
        ticks=ticks,
        dropout_rate=dropout_rate,
        rng_seed=rng_seed,
        record_frames=True,
    )

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
                "position_restoration": cycle_entry["position_restoration"],
                "token_restoration": cycle_entry["token_restoration"],
                "guard_substitutions": cycle_entry["guard_substitutions"],
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
        "engine_surface": "mecha_engine.runtime.live_cycle(record_frames=True)",
        "creature": {
            "grid_id": grid["grid_id"],
            "profile_id": slip_profile.get("profile_id"),
        },
        "parameters": {
            "damage_cycles": damage_cycles,
            "ticks": ticks,
            "dropout_rate": dropout_rate,
            "rng_seed": rng_seed,
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


def build_recorder_report(replay: dict) -> dict:
    """The lab's stage-0 report over one recorded life."""
    phases: dict[str, int] = {}
    for frame in replay["frames"]:
        phases[frame["phase"]] = phases.get(frame["phase"], 0) + 1
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0_complete",
        "date": REPORT_DATE,
        "purpose": (
            "R5 (DR 0017 / DR 0021 Review step): record a creature's "
            "live_cycle as a replay artifact of per-tick engine truth — "
            "birth/wound/repair packets plus every episode tick — for "
            "the workshop preview's scrubber."
        ),
        "source_artifacts": [
            "research/decision_records/0023-replay-recording.md",
            "packages/mecha_engine/src/mecha_engine/runtime/live.py",
            "data/seed_grids/mg_seed_001.json",
            "data/slips/valid/slip_lcd_seed.json",
        ],
        "metrics": {
            "replay_id": replay["replay_id"],
            "frame_count": replay["frame_count"],
            "tick_frame_count": replay["tick_frame_count"],
            "frames_by_phase": phases,
            "all_cycles_valid": replay["live"]["all_cycles_valid"],
            "all_cycles_aligned": replay["live"]["all_cycles_aligned"],
            "removed_cells_total": sum(
                cycle["removed_cell_count"]
                for cycle in replay["live"]["cycles"]
            ),
        },
        "closed_states": [
            "record_frames_default_off_byte_identical",
            "every_frame_is_engine_truth_verbatim",
            "invalid_repairs_carry_validator_errors_never_fake_bodies",
            "replay_reproducible_from_recorded_parameters",
        ],
        "blocked_states": [
            # The 100k-tick replay dataset is R6's deliverable; this lab
            # records single lives.
            "replay_100k_ticks_dataset_pending_r6",
        ],
        "decision": {
            "status": "replay_recorder_composed",
            "adoption": "lab_only_game_loop_evidence",
            "reason": (
                "A creature's whole life scrubs as recorded engine "
                "truth: the wound frames are the damage events' own "
                "observability records, the bodies are validator-passed "
                "render packets, and every episode tick is the "
                "lifecycle's own history entry. Nothing is synthesized "
                "for display."
            ),
        },
        "next_research_step": (
            "The preview scrubber consumes this artifact live "
            "(/api/preview/replay); R6's replay_100k_ticks dataset "
            "batches this recorder over the corpus."
        ),
    }


def write_replay_artifacts(
    output_dir: str | Path, report: dict, replay: dict
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "replay_recorder_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "replay_sample.json").write_text(
        json.dumps(replay, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Record one creature's life as a replay artifact (R5)."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--rng-seed", type=int, default=20260707)
    parser.add_argument("--cycles", type=int, default=3)
    parser.add_argument("--ticks", type=int, default=48)
    args = parser.parse_args()

    grid = json.loads(SEED_GRID_PATH.read_text(encoding="utf-8"))
    slip_profile = json.loads(SLIP_PROFILE_PATH.read_text(encoding="utf-8"))
    seed_grids = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(
            (ROOT / "data" / "seed_grids").glob("mg_seed_*.json")
        )
    ]
    repair_model = train_repair_model(
        seed_grids[:40], epochs=40, rng_seed=args.rng_seed
    )
    replay = build_replay(
        grid,
        slip_profile,
        repair_model,
        damage_cycles=args.cycles,
        ticks=args.ticks,
        rng_seed=args.rng_seed,
    )
    report = build_recorder_report(replay)
    write_replay_artifacts(args.output_dir, report, replay)
    print(
        json.dumps(
            {
                "artifact_id": report["artifact_id"],
                "decision": report["decision"]["status"],
                "frame_count": replay["frame_count"],
                "tick_frame_count": replay["tick_frame_count"],
                "output_dir": str(args.output_dir),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
