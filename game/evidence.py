"""F1 evidence harness — the client skeleton, measured (cycle 14 F1).

Runs the hello-creature composition pipeline headless (no pygame, pure
compositor only) and records what F1 actually delivers: real engine
packets, deterministic frames (twin-run byte equality over checksums),
the idle clip cycling, and the honest effect ledger (the LCD identity
applied; nothing declared was skipped for a calm creature). Emits
``data/game_client/front_end_skeleton_stage0.json``.

Dev harness, not product code: the path bootstrap lives here (DR 0033
decision 3), and the artifact is repo evidence, so it runs from a
checkout only:

    uv run python -B game/evidence.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _src in (ROOT / "game" / "src", ROOT / "packages" / "mecha_engine" / "src"):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from mecha_game.packets import (  # noqa: E402
    HELLO_SEED,
    HELLO_SLIP,
    hello_packet,
    load_hello_creature,
)
from mecha_game.rasterize import compose_frame  # noqa: E402

ARTIFACT_ID = "front_end_skeleton_stage0"
REPORT_DATE = "2026-07-12"
SESSION_TICKS = 32
CELL_PX = 4  # spec-equivalent scale for cheap evidence frames


def _frame_checksum(pixels) -> str:
    payload = b"".join(bytes(rgb) for row in pixels for rgb in row)
    return hashlib.sha256(payload).hexdigest()


def run_composition_session(
    ticks: int = SESSION_TICKS, cell_px: int = CELL_PX
) -> dict:
    """One headless session: engine packets composed frame by frame."""
    creature = load_hello_creature(ROOT / HELLO_SEED, ROOT / HELLO_SLIP)
    ghost = None
    checksums: list[str] = []
    frame_indices: list[int] = []
    applied: set[str] = set()
    skipped: set[str] = set()
    for tick in range(ticks):
        packet = hello_packet(creature, tick)
        composed = compose_frame(
            packet, previous_ghost=ghost, cell_px=cell_px
        )
        ghost = composed.ghost
        checksums.append(_frame_checksum(composed.pixels))
        frame_indices.append(packet["animation"]["frame_index"])
        applied.update(composed.applied)
        skipped.update(composed.skipped)
    return {
        "ticks": ticks,
        "cell_px": cell_px,
        "clip_frame_count": creature.frame_count,
        "frame_checksums": checksums,
        "frame_indices": frame_indices,
        "effects_applied": sorted(applied),
        "effects_skipped": sorted(skipped),
        "distinct_frames": len(set(checksums)),
    }


def build_front_end_skeleton_report(
    ticks: int = SESSION_TICKS, cell_px: int = CELL_PX
) -> dict:
    first = run_composition_session(ticks, cell_px)
    second = run_composition_session(ticks, cell_px)
    deterministic = first == second
    clip_cycles = first["frame_indices"] == [
        t % first["clip_frame_count"] for t in range(ticks)
    ]
    lcd_identity = first["effects_applied"] == ["lcd_ghosting", "scanline"]
    nothing_skipped = first["effects_skipped"] == []
    status = (
        "complete"
        if deterministic and clip_cycles and lcd_identity and nothing_skipped
        else "refuted"
    )
    return {
        "artifact_id": ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 14 F1 (GAME track, Phase F): prove the launchable "
            "pygame-ce client skeleton renders REAL engine packets end "
            "to end — deterministic composed frames, the idle clip "
            "driven through render_packet_v2, the always-on LCD "
            "identity effects rasterized (lcd_ghosting first "
            "implemented here — the named Phase-C remainder), nothing "
            "declared silently dropped."
        ),
        "source_artifacts": [
            HELLO_SEED.as_posix(),
            HELLO_SLIP.as_posix(),
            "game/src/mecha_game/packets.py",
            "game/src/mecha_game/rasterize.py",
            "research/decision_records/0033-game-front-end-technology.md",
        ],
        "metrics": {
            "session": first,
            "twin_run_byte_equal": deterministic,
            "idle_clip_cycles_documented_frames": clip_cycles,
            "lcd_identity_applied": lcd_identity,
            "declared_effects_skipped": first["effects_skipped"],
            "ghosting_makes_frames_distinct": first["distinct_frames"]
            > first["clip_frame_count"],
        },
        "closed_states": [
            "front_end_technology_decided (pygame-ce desktop client, "
            "DR 0033 — in-process engine import, packets verbatim)",
            "hello_creature_launchable (window loop over real "
            "render_packet_v2 frames; headless twin proven by the "
            "launch tests)",
            "lcd_ghosting_first_rasterized (the Phase-C remainder #2: "
            "temporal per-LCD-pixel persistence at grid resolution)",
            "pure_compositor_spec (pygame-free packet->pixel math, "
            "reusable by any future client)",
        ],
        "blocked_states": [
            "crt_bloom_glitch_rasterization_is_F3 (declared-but-"
            "unimplemented effects are reported, never dropped; a calm "
            "hello creature declares neither)",
            "companion_loop_is_F2 (the hello state is static engine "
            "truth; tending/death/lineage land with MVP 0.1's loop)",
            "installable_release_is_F5 (PyInstaller named in DR 0033, "
            "decided at its own rung)",
        ],
        "decision": (
            "adopt: the pygame-ce skeleton is the game client's "
            "foundation; F2 builds the companion loop on it"
        ),
        "next_research_step": (
            "F2 — the companion loop as a product (MVP 0.1): the W1 "
            "lab's adopt/tend/live/die loop productized in this client"
        ),
    }


def write_front_end_skeleton_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data" / "game_client",
    )
    args = parser.parse_args()
    written = write_front_end_skeleton_artifacts(
        args.output_dir, build_front_end_skeleton_report()
    )
    print(f"wrote {written}")
