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
from mecha_game.session import (  # noqa: E402
    CompanionSession,
    load_session_inputs,
)

ARTIFACT_ID = "front_end_skeleton_stage0"
LOOP_ARTIFACT_ID = "companion_loop_stage0"
REPORT_DATE = "2026-07-12"
SESSION_TICKS = 32
CELL_PX = 4  # spec-equivalent scale for cheap evidence frames
LOOP_TICK_BUDGET = 400


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


def _new_session() -> CompanionSession:
    grid, slip_profile, model = load_session_inputs(
        ROOT / HELLO_SEED, ROOT / HELLO_SLIP
    )
    return CompanionSession(grid, slip_profile, model=model)


def _run_arm(attentive: bool, budget: int) -> dict:
    """One life under a policy: neglect (nobody answers the beg) or
    attentive (the keeper feeds whenever the companion begs) —
    D6's keeper-dependent model, measured through the product session."""
    session = _new_session()
    beg_ticks = 0
    keeper_feeds = 0
    for _ in range(budget):
        if not session.alive:
            break
        if attentive and session.begging:
            session.advance(player_action="feed")
            keeper_feeds += 1
        else:
            session.advance()
        if session.begging:
            beg_ticks += 1
    return {
        "attentive": attentive,
        "survived_budget": session.alive,
        "age_ticks": session.state["age_ticks"],
        "death_cause": session.death_cause,
        "beg_ticks": beg_ticks,
        "keeper_feeds": keeper_feeds,
    }


def build_companion_loop_report(
    budget: int = LOOP_TICK_BUDGET,
) -> dict:
    """F2's measured claims: the loop has REAL stakes (neglect kills,
    tending saves — the engine's own dynamics under the documented
    beg-mediated model), succession is the engine's child with lineage
    preserved, and the whole loop is deterministic without a player."""
    neglect_a = _run_arm(attentive=False, budget=budget)
    neglect_b = _run_arm(attentive=False, budget=budget)
    attentive = _run_arm(attentive=True, budget=budget)

    session = _new_session()
    while session.alive:
        session.advance()
    parent_id = session.grid["grid_id"]
    parent_record = dict(session.lineage[-1])
    child_id = session.succeed()
    child_record = dict(session.lineage[-1])
    lineage_document = session.lineage_document()

    deterministic = neglect_a == neglect_b
    neglect_dies = not neglect_a["survived_budget"]
    tending_saves = (
        attentive["survived_budget"]
        or attentive["age_ticks"] > neglect_a["age_ticks"]
    )
    child_linked = (
        child_record["parent_grid_id"] == parent_id
        and child_id != parent_id
    )
    status = (
        "complete"
        if deterministic and neglect_dies and tending_saves and child_linked
        else "refuted"
    )
    return {
        "artifact_id": LOOP_ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 14 F2 (GAME track, Phase F): prove MVP 0.1's "
            "companion loop as a product — the documented beg-mediated "
            "interaction model (the companion cannot feed itself; only "
            "the keeper's feed fills hunger) gives the loop real "
            "stakes measured through the engine's own dynamics; death "
            "-> engine-generated child carrying parent lineage; a "
            "lineage file of verbatim engine blocks; deterministic "
            "without a player."
        ),
        "source_artifacts": [
            HELLO_SEED.as_posix(),
            HELLO_SLIP.as_posix(),
            "game/src/mecha_game/session.py",
            "game/src/mecha_game/hud.py",
            "game/src/mecha_game/app.py",
            "labs/micro_threads/ablation_gates.py",
            "labs/game_loop/companion.py",
        ],
        "metrics": {
            "tick_budget": budget,
            "neglect_arm": neglect_a,
            "attentive_arm": attentive,
            "twin_run_equal": deterministic,
            "neglect_dies_within_budget": neglect_dies,
            "tending_saves": tending_saves,
            "succession": {
                "parent_grid_id": parent_id,
                "child_grid_id": child_id,
                "child_parent_link_holds": child_linked,
                "parent_death_cause": parent_record.get("death_cause"),
                "child_lineage": child_record["lineage"],
            },
            "lineage_document_records": len(lineage_document["records"]),
        },
        "closed_states": [
            "companion_loop_is_a_product (adopt/tend/beg/die/succeed "
            "in the launchable client — W1 semantics + the D6 "
            "keeper-dependent model, engine surfaces only)",
            "loop_has_real_stakes (neglect starves the companion; the "
            "attentive keeper's feeding measurably extends the life — "
            "the engine's own dynamics, no scripted events)",
            "succession_is_the_engines_child (generate_candidate from "
            "the dead parent, lineage blocks recorded verbatim)",
            "needs_visible (hunger/energy bars + ui_hints icons pure "
            "and engine-truth; mood/age in the footer from the packet "
            "and the state)",
        ],
        "blocked_states": [
            "full_render_bridge_consumption_is_F3 (transition-graph "
            "clip driving, bloom/glitch rasterization, the kept "
            "fleet's beg-timing/clip-choice/mood consumers)",
            "keeper_era_loop_is_F4 (eras, saves beyond the lineage "
            "file, the evolution repertoire surfacing)",
            "installable_release_is_F5 (install/launch/play/quit/"
            "resume as a product)",
        ],
        "decision": (
            "adopt: MVP 0.1's documented loop runs as a product on "
            "the F1 skeleton; F3 consumes the render bridge in full"
        ),
        "next_research_step": (
            "F3 — the render bridge consumed in full: live clip "
            "driving through the transition graph, the retro effects "
            "pipeline completed (crt_bloom, glitch), ui_hints and the "
            "D6-kept threads' game-side consumers"
        ),
    }


def write_companion_loop_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{LOOP_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


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
    written = write_companion_loop_artifacts(
        args.output_dir, build_companion_loop_report()
    )
    print(f"wrote {written}")
