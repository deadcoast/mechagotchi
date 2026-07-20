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
import os
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
from mecha_game.campaign import (  # noqa: E402
    ERA_CONFIG,
    TINY_ERA_CONFIG,
    KeeperCampaign,
    load_campaign_inputs,
)
from mecha_game.clips import TRANSITIONS, ClipDriver  # noqa: E402
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


def _new_session(fleet: bool = True) -> CompanionSession:
    grid, slip_profile, model = load_session_inputs(
        ROOT / HELLO_SEED, ROOT / HELLO_SLIP
    )
    return CompanionSession(
        grid, slip_profile, model=model, fleet=fleet
    )


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


BRIDGE_ARTIFACT_ID = "render_bridge_stage0"


def _drive_bridge(cell_px: int = 2) -> dict:
    """One scripted drive of the full bridge over the real creature:
    the driver walks the C2 graph toward a state-shaped target script,
    every step becomes a REAL engine packet, and the compositor
    rasterizes every declared effect. Legality is judged per emitted
    cut against the documented graph."""
    from mecha_engine.genome import clip_frame_count

    creature_grid, slip_profile, _model = load_session_inputs(
        ROOT / HELLO_SEED, ROOT / HELLO_SLIP
    )
    session = CompanionSession(
        creature_grid, slip_profile, model=_model
    )
    vocabulary = {clip for edge in TRANSITIONS for clip in edge}
    driver = ClipDriver(
        {clip: clip_frame_count(clip) for clip in vocabulary}
    )
    # The state script: calm -> hungry (beg + crt_bloom) -> stressed
    # (ill + glitch) -> exhausted (sleep) -> calm. Values drive the
    # engine's OWN selection thresholds; nothing is hand-picked.
    state_script = (
        [{}] * 6
        + [{"hunger": 0.9}] * 10
        + [{"hunger": 0.2, "stress": 0.9}] * 10
        + [{"stress": 0.2, "energy": 0.05}] * 10
        + [{"energy": 0.9}] * 8
    )
    base_state = dict(session.state)
    steps: list[dict] = []
    checksums: list[str] = []
    applied_union: set[str] = set()
    skipped_union: set[str] = set()
    illegal_cuts = 0
    previous = None
    ghost = None
    for overrides in state_script:
        session.state = {**base_state, **overrides}
        session.begging = overrides.get("hunger", 0.0) > 0.7
        clip, frame_index = driver.step(session.desired_clip())
        if previous is not None:
            prev_clip, prev_frame = previous
            intra = clip == prev_clip and frame_index == prev_frame + 1
            boundary_cut = (
                prev_frame == driver.frame_counts[prev_clip] - 1
                and frame_index == 0
                and (prev_clip, clip) in TRANSITIONS
            )
            if not (intra or boundary_cut):
                illegal_cuts += 1
        previous = (clip, frame_index)
        packet = session.packet_for(clip, frame_index)
        composed = compose_frame(
            packet, previous_ghost=ghost, cell_px=cell_px
        )
        ghost = composed.ghost
        checksums.append(_frame_checksum(composed.pixels))
        applied_union.update(composed.applied)
        skipped_union.update(composed.skipped)
        steps.append(
            {
                "clip": clip,
                "frame_index": frame_index,
                "displayed_clip": packet["animation"]["clip"],
                "effects": packet["effects"],
            }
        )
    clips_driven = sorted({step["clip"] for step in steps})
    return {
        "ticks": len(state_script),
        "cell_px": cell_px,
        "steps": steps,
        "frame_checksums": checksums,
        "clips_driven": clips_driven,
        "effects_applied": sorted(applied_union),
        "effects_skipped": sorted(skipped_union),
        "illegal_cuts": illegal_cuts,
    }


def build_render_bridge_report(cell_px: int = 2) -> dict:
    first = _drive_bridge(cell_px)
    second = _drive_bridge(cell_px)
    deterministic = first == second
    graph_legal = first["illegal_cuts"] == 0
    full_contract = first["effects_applied"] == [
        "crt_bloom",
        "glitch",
        "lcd_ghosting",
        "scanline",
    ]
    nothing_skipped = first["effects_skipped"] == []
    all_clips = first["clips_driven"] == [
        "beg",
        "idle",
        "ill",
        "sleep",
    ]
    status = (
        "complete"
        if deterministic
        and graph_legal
        and full_contract
        and nothing_skipped
        and all_clips
        else "refuted"
    )
    return {
        "artifact_id": BRIDGE_ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 14 F3 (GAME track, Phase F): the render bridge "
            "consumed in full on the client side — live clip DRIVING "
            "through the documented C2 hub-and-spoke graph (the named "
            "Phase-C remainder #3: every emitted cut a measured graph "
            "edge at the loop boundary), and the complete documented "
            "effects contract rasterized (scanline + lcd_ghosting + "
            "crt_bloom riding beg + glitch riding ill with amplitude "
            "= the engine's own stress)."
        ),
        "source_artifacts": [
            HELLO_SEED.as_posix(),
            HELLO_SLIP.as_posix(),
            "game/src/mecha_game/clips.py",
            "game/src/mecha_game/rasterize.py",
            "labs/animation_system/transition_graph.py",
            "workshop/shared/draw.js",
        ],
        "metrics": {
            "session": {
                key: first[key]
                for key in (
                    "ticks",
                    "cell_px",
                    "clips_driven",
                    "effects_applied",
                    "effects_skipped",
                    "illegal_cuts",
                )
            },
            "twin_run_byte_equal": deterministic,
            "every_cut_is_a_graph_edge": graph_legal,
            "full_effects_contract_rasterized": full_contract,
            "nothing_declared_skipped": nothing_skipped,
        },
        "closed_states": [
            "live_clip_driving (the C2 graph walked frame by frame — "
            "cuts only at loop boundaries, illegal edges routed "
            "through the idle hub; Phase-C remainder #3 consumed)",
            "retro_effects_pipeline_complete (all four documented "
            "effects rasterized by the pure compositor, the shared "
            "drawer's exact math; glitch amplitude IS engine stress)",
            "ui_hints_consumed (need icons + the attention ping "
            "PINGING on a deterministic phase)",
        ],
        "blocked_states": [
            "per_role_limb_joint_motion (the standing Phase-C "
            "remainder #1, an engine-side increment)",
        ],
        "decision": (
            "adopt: the client consumes the bridge contract in full; "
            "the fleet's game-side consumers landed the same day "
            "(fleet_consumers_stage0 — F3a's 'needs promotion' claim "
            "was CORRECTED: cycle 12 had already ported the fleet "
            "into learning.threads; only the public export and the "
            "consumers were missing)"
        ),
        "next_research_step": (
            "F4 — the Keeper/era loop (DR 0021 as design input)"
        ),
    }


FLEET_ARTIFACT_ID = "fleet_consumers_stage0"


def _run_fleet_session(fleet: bool, ticks: int) -> dict:
    """One attentive scripted life: the keeper answers every beg, so
    the companion survives long enough for the threads to warm."""
    session = _new_session(fleet=fleet)
    actions: list[str] = []
    for _ in range(ticks):
        if not session.alive:
            break
        if session.begging:
            session.advance(player_action="feed")
        else:
            session.advance()
        actions.append(session.log[-1]["action"])
    threads = session.snapshot()["threads"]
    return {
        "fleet": fleet,
        "survived": session.alive,
        "executed_actions": actions,
        "threads": {
            name: {
                "confidence": signal["confidence"],
                "output": signal["output"],
            }
            for name, signal in threads.items()
        },
        "desired_clip_final": session.desired_clip(),
    }


def build_fleet_consumers_report(ticks: int = 80) -> dict:
    """F3b's measured claims: exactly the D6-kept five stream through
    the PUBLIC learning surface into the product session; the
    forecasters and the HMM warm to nonzero confidence on the
    companion's own life; the whole loop stays deterministic; and the
    fleet-on/fleet-off decision divergence is RECORDED (D6 measured
    the welfare increment ~0 — whatever it is here, it is reported,
    not assumed)."""
    on_a = _run_fleet_session(fleet=True, ticks=ticks)
    on_b = _run_fleet_session(fleet=True, ticks=ticks)
    off = _run_fleet_session(fleet=False, ticks=ticks)
    deterministic = on_a == on_b
    kept = [
        "animation_bandit",
        "energy_forecast",
        "hidden_mood_hmm",
        "hunger_forecast",
        "interaction_timing",
    ]
    streamed = sorted(on_a["threads"]) == kept
    hunger_warm = on_a["threads"]["hunger_forecast"]["confidence"] > 0
    hmm_warm = on_a["threads"]["hidden_mood_hmm"]["confidence"] > 0
    pairs = zip(on_a["executed_actions"], off["executed_actions"])
    diverged = sum(1 for a, b in pairs if a != b) + abs(
        len(on_a["executed_actions"]) - len(off["executed_actions"])
    )
    status = (
        "complete"
        if deterministic and streamed and hunger_warm and hmm_warm
        else "refuted"
    )
    return {
        "artifact_id": FLEET_ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 14 F3b (GAME track, Phase F): the D6-kept fleet "
            "cashes out at the game's consumers — the five kept "
            "threads (and ONLY those; dropped threads stay out) "
            "stream through the learning module's public fleet "
            "surface into the product session: the hunger forecast's "
            "own anticipatory effect is the 'begs soon' display, the "
            "bandit's recommendation is the idle-time clip choice "
            "(packet-side per D3), the HMM's felt mood shows with "
            "entropy-honest confidence."
        ),
        "source_artifacts": [
            "packages/mecha_engine/src/mecha_engine/learning/__init__.py",
            "packages/mecha_engine/tests/test_learning_fleet_surface.py",
            "research/package_specs/mecha_engine_learning_interface_spec.md",
            "data/micro_threads/ablation_gates_stage0.json",
            "game/src/mecha_game/session.py",
            "game/src/mecha_game/app.py",
        ],
        "metrics": {
            "ticks": ticks,
            "fleet_on": on_a,
            "fleet_off_executed_actions": off["executed_actions"],
            "twin_run_equal": deterministic,
            "exactly_the_kept_five_stream": streamed,
            "hunger_forecast_warms": hunger_warm,
            "hidden_mood_hmm_warms": hmm_warm,
            "decisions_diverged_vs_frozen": diverged,
        },
        "closed_states": [
            "fleet_public_surface (observe_fleet/fleet_signals/"
            "FLEET_THREAD_NAMES exported — additive, zero behavior "
            "change, spec + contract pin updated together)",
            "kept_five_opted_in (D6 verdicts applied without "
            "sentiment; dropped threads stay out; successors keep "
            "the opt-in with fresh per-companion memory)",
            "consumers_wired (begs-soon = the thread's OWN "
            "anticipatory effect; clip choice = the bandit's "
            "recommendation, packet-side; felt mood = the HMM's MAP "
            "readout with entropy-honest confidence)",
            "correction_recorded (F3a claimed the fleet needed "
            "promotion — cycle 12 had already ported it into "
            "learning.threads; only the export and consumers were "
            "missing)",
        ],
        "blocked_states": [
            "bandit_learning_needs_real_play (the recommendation "
            "emerges from interaction feedback over real sessions; "
            "the scripted harness records whatever warmth the script "
            "earns, nothing is fabricated)",
            "keeper_era_loop_is_F4 (eras, saves, the evolution "
            "repertoire surfacing)",
        ],
        "decision": (
            "adopt: F3 is complete — the render bridge and the kept "
            "fleet's game-side value both consumed"
        ),
        "next_research_step": (
            "F4 — the Keeper/era loop (DR 0021 as design input; "
            "the archive scale-geometry seam promotes here IF this "
            "consumer demands it)"
        ),
    }


REAL_WEATHER_ARTIFACT_ID = "real_weather_stage0"


def build_real_weather_report() -> dict:
    """G4's measured claims at session scale: the G2-ingested REAL
    snapshots drive an era through the UNCHANGED pressure seam; the
    era record's provenance carries the engine's own per-generation
    real snapshot ids and dropout multipliers; twin runs byte-equal;
    the harshness of real early-phase soup is recorded, not tuned."""
    from mecha_game.campaign import load_real_weather_source

    inputs = _campaign_inputs(session_scale=True)

    def run_era() -> dict:
        campaign = KeeperCampaign(
            inputs, campaign_id="real_weather_evidence"
        )
        return campaign.advance_era("real")

    first = run_era()
    second = run_era()
    deterministic = json.dumps(first, sort_keys=True) == json.dumps(
        second, sort_keys=True
    )
    real_ids = {
        record["snapshot_id"]
        for record in load_real_weather_source()
    }
    by_generation = first["report"]["cubff_pressure"]["by_generation"]
    provenance_real = all(
        entry["snapshot_id"] in real_ids for entry in by_generation
    )
    multipliers = [
        entry["dropout_multiplier"] for entry in by_generation
    ]
    status = (
        "complete"
        if deterministic
        and provenance_real
        and by_generation
        and first["derived"]["generations_ran"] > 0
        else "refuted"
    )
    return {
        "artifact_id": REAL_WEATHER_ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 17 G4 (SHARED, Phase G): REAL weather in the game "
            "— the G2-ingested CuBFF snapshot records drive an era "
            "through the engine's cubff_pressure_source seam with "
            "ZERO seam changes (the DR 0021 promise, verified); the "
            "era's weather provenance is the engine's own "
            "per-generation report over real snapshot ids."
        ),
        "source_artifacts": [
            "data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json",
            "game/src/mecha_game/campaign.py",
            "packages/mecha_engine/src/mecha_engine/runtime/_cubff.py",
            "research/decision_records/0018-cubff-live-lineage-pressure.md",
            "research/decision_records/0020-cubff-pressure-runtime-promotion.md",
        ],
        "metrics": {
            "weather": first["weather"],
            "generations_ran": first["derived"]["generations_ran"],
            "went_extinct": first["derived"]["went_extinct"],
            "elites": len(first["elites"]),
            "dropout_multipliers_by_generation": multipliers,
            "max_multiplier": max(multipliers) if multipliers else None,
            "provenance_all_real_ids": provenance_real,
            "twin_run_byte_equal": deterministic,
        },
        "closed_states": [
            "zero_seam_changes (the ingested records pass into evolve "
            "verbatim; the seam's defensive reads supply the honest "
            "defaults for fields checkpoints do not store)",
            "provenance_shows (the era record carries the engine's "
            "own per-generation real snapshot ids; the client's "
            "weather key 4 = REAL)",
            "harshness_is_measured_not_tuned (early-phase soup is "
            "high-entropy — the multipliers are whatever the "
            "engine's own feature math says; recorded verbatim)",
        ],
        "blocked_states": [
            "replication_and_lineage_channels_silent (checkpoints "
            "store neither replication scores nor lineage events — "
            "those pressure channels read their honest defaults; the "
            "Python-callback export path would light them, a named "
            "upstream-integration increment)",
        ],
        "decision": (
            "adopt: the game's weather is upgradeable to real CuBFF "
            "with a keypress; synthetic forecasts remain available"
        ),
        "next_research_step": (
            "G5 — the community distribution decision record"
        ),
    }


def write_real_weather_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{REAL_WEATHER_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


HARSHNESS_ARTIFACT_ID = "real_weather_harshness_stage0"
HARSHNESS_REPORT_DATE = "2026-07-20"
# DR 0018's measured synthetic-storm figure: the chaotic soup drove a
# 1.17x dropout multiplier. The I3 question is whether any REAL
# post-takeover snapshot breaches it — measured, never tuned.
STORM_PRECEDENT_MULTIPLIER = 1.17


def build_real_weather_harshness_report() -> dict:
    """Cycle 19 I3: per-phase harshness through the UNTOUCHED seam.

    Every committed real snapshot (the I1 two-phase corpus, phase
    labels from the runs' own metrics) is measured with the engine's
    own promoted pressure math (`_cubff_generation_pressure` —
    verbatim, zero seam changes); multipliers are grouped by phase and
    the storm-precedent question is answered by the numbers.
    """
    from mecha_engine.runtime.evolve import _cubff_generation_pressure
    from mecha_game.campaign import load_real_weather_source

    per_snapshot = []
    for record in load_real_weather_source():
        pressure, multiplier = _cubff_generation_pressure(record)
        per_snapshot.append(
            {
                "snapshot_id": record["snapshot_id"],
                "epoch": record["epoch"],
                "phase": record.get("phase", "unmeasured"),
                "mutation_pressure": pressure,
                "dropout_multiplier": multiplier,
            }
        )

    by_phase: dict = {}
    for phase in sorted({entry["phase"] for entry in per_snapshot}):
        multipliers = [
            entry["dropout_multiplier"]
            for entry in per_snapshot
            if entry["phase"] == phase
        ]
        by_phase[phase] = {
            "snapshot_count": len(multipliers),
            "min_multiplier": min(multipliers),
            "max_multiplier": max(multipliers),
            "mean_multiplier": round(
                sum(multipliers) / len(multipliers), 6
            ),
        }

    post = by_phase.get("post_takeover", {})
    breaches = (
        post.get("max_multiplier", 0.0) > STORM_PRECEDENT_MULTIPLIER
    )

    # The callback path (the named increment made real): committed
    # compact records with replication_per_prog evaluated — every
    # engine number recomputed live from the committed evidence.
    callback_payload = json.loads(
        (
            ROOT
            / "data"
            / "cubff_real_ingest"
            / "callback_states"
            / "callback_states_compact.json"
        ).read_text(encoding="utf-8")
    )
    callback_states = []
    for record in callback_payload["records"]:
        pressure, multiplier = _cubff_generation_pressure(record)
        scores = record.get("replication_scores", [])
        callback_states.append(
            {
                "snapshot_id": record["snapshot_id"],
                "epoch": record["epoch"],
                "phase": record.get("phase", "unmeasured"),
                "replication_score_count": len(scores),
                "high_replication_count": sum(
                    1 for score in scores if score >= 48
                ),
                "mutation_pressure": pressure,
                "dropout_multiplier": multiplier,
            }
        )
    callback_post = [
        entry["dropout_multiplier"]
        for entry in callback_states
        if entry["phase"] == "post_takeover"
    ]
    callback_breaches = bool(
        callback_post
        and max(callback_post) > STORM_PRECEDENT_MULTIPLIER
    )
    callback_path = {
        "protocol": callback_payload["protocol"],
        "per_state": callback_states,
        "post_takeover_breaches_storm_precedent": callback_breaches,
    }

    return {
        "artifact_id": HARSHNESS_ARTIFACT_ID,
        "status": "complete" if per_snapshot else "refuted",
        "date": HARSHNESS_REPORT_DATE,
        "purpose": (
            "Cycle 19 I3 (SHARED, Phase I): real weather harshness "
            "measured per phase over the I1 two-phase corpus through "
            "the engine's UNTOUCHED cubff_pressure_source seam — the "
            "multiplier direction measured, not tuned; the synthetic "
            "storm's 1.17x precedent is the pre-registered bar."
        ),
        "source_artifacts": [
            "data/cubff_real_ingest/real_snapshot_ingest_stage0_report.json",
            "packages/mecha_engine/src/mecha_engine/runtime/evolve.py",
            "packages/mecha_engine/src/mecha_engine/runtime/_cubff.py",
            "research/experiment_reports/2026-07-20-post-takeover-corpus.md",
            "research/decision_records/0018-cubff-live-lineage-pressure.md",
        ],
        "metrics": {
            "storm_precedent_multiplier": STORM_PRECEDENT_MULTIPLIER,
            "per_snapshot": per_snapshot,
            "by_phase": by_phase,
            "post_takeover_breaches_storm_precedent": breaches,
            "callback_path": callback_path,
        },
        "closed_states": [
            "per_phase_harshness_measured (every committed snapshot "
            "through the engine's own promoted pressure math, zero "
            "seam changes)",
            "storm_precedent_question_answered_by_the_numbers "
            "(checkpoint seam: NOT breached — post-takeover measures "
            "MILDER than early through this path because the "
            "harshness channels are format-silent)",
            "callback_export_path_real (the upstream PERMITS: "
            "pybind11 module built at the audited commit, "
            "eval_selfrep lights replication_per_prog — the "
            "replication channel carries ~98.6% replicators "
            "post-takeover vs 2 programs early; multipliers rise to "
            "~1.02-1.05, HARSHER measured direction, still under "
            "the 1.17x precedent)",
        ],
        "blocked_states": [
            "lineage_churn_channel_still_silent (neither checkpoints "
            "nor the callback state expose a lineage-event stream — "
            "the 0.3*lineage_churn instability channel reads 0 on "
            "every real path; a harsher real weather may exist "
            "behind it, unmeasurable until the upstream exposes "
            "lineage events)",
            "callback_export_is_wsl_only (the .so is a Linux build; "
            "the committed compact records + the recorded protocol "
            "reproduce it)",
        ],
        "decision": (
            "real weather harshness is DIRECTIONAL and measured: "
            "mild through the checkpoint seam (channels silent), "
            "harsher (~1.02-1.05x) through the callback path with "
            "the replication channel lit, and the synthetic storm's "
            "1.17x precedent stands unbeaten by real soup on every "
            "path — nothing tuned to feel dramatic"
        ),
        "next_research_step": (
            "wire a callback-sourced weather forecast into the game "
            "IF a consumer asks (the records are seam-compatible "
            "today); lineage events remain an upstream-integration "
            "question"
        ),
    }


def write_real_weather_harshness_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{HARSHNESS_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


PACKS_ARTIFACT_ID = "community_pack_stage0"
STARTER_PACK_PATH = ROOT / "data" / "packs" / "mechagotchi_starter_pack.json"


def build_community_pack_report() -> dict:
    """F16's measured claims: the STARTER PACK builds from committed
    material (the valid zoo covenants + the committed workshop
    releases + a corpus creature), writes deterministically to
    `data/packs/`, imports with per-item verdicts staging into the
    inboxes, and its staged creatures flow into a real era where the
    engine's admission gates judge them AGAIN (the 8×8 pair verbatim-
    rejected on size, the 16×16 creature admitted)."""
    import tempfile

    from mecha_game.contribute import (
        founders_verdict,
        load_released_grids,
    )
    from mecha_game.packs import build_pack, import_pack, write_pack

    zoo = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(
            (ROOT / "data" / "slips" / "valid").glob("*.json")
        )
    ]
    releases = load_released_grids(
        ROOT / "data" / "workshop" / "released"
    )
    beetle = json.loads(
        (ROOT / HELLO_SEED).read_text(encoding="utf-8")
    )
    pack = build_pack(
        pack_id="mechagotchi_starter",
        title="The Mechagotchi Starter Pack",
        provenance={
            "author": "the mechagotchi repository",
            "source": "data/slips/valid + data/workshop/released "
            "+ data/seed_grids_16x16 (committed material)",
            "license": "Apache-2.0",
            "created_date": REPORT_DATE,
        },
        slips=zoo,
        creatures=releases + [beetle],
    )
    write_pack(pack, STARTER_PACK_PATH)

    inputs = _campaign_inputs(session_scale=True)
    campaign = KeeperCampaign(inputs, campaign_id="pack_evidence")
    campaign.advance_era("calm")
    with tempfile.TemporaryDirectory() as tmp:
        keeper = Path(tmp)
        report = import_pack(keeper, STARTER_PACK_PATH)
        staged_creatures = load_released_grids(keeper / "released")
        era = campaign.advance_era(
            "calm", released_grids=staged_creatures
        )
    verdict = founders_verdict(era)
    rejected_ids = sorted(r["grid_id"] for r in verdict["rejected"])
    all_slips_staged = all(entry["ok"] for entry in report["slips"])
    all_creatures_staged = all(
        entry["ok"] for entry in report["creatures"]
    )
    beetle_admitted = "mg_seed16_001_beetle" in verdict["admitted_ids"]
    size_rejected = rejected_ids == [
        "released_tall_wisp",
        "released_wide_sentinel",
    ]
    status = (
        "complete"
        if all_slips_staged
        and all_creatures_staged
        and beetle_admitted
        and size_rejected
        and not era["derived"]["went_extinct"]
        else "refuted"
    )
    return {
        "artifact_id": PACKS_ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 16 F16 (GAME track, Phase F, MVP 0.3): community "
            "profile packs at the FORMAT rung — mechagotchi_pack_v1 "
            "carries SLIPs + creatures + provenance in one importable "
            "file; the builder refuses invalid content verbatim; "
            "import judges every item again and stages only accepted "
            "ones into the existing inboxes; the era admission gates "
            "judge staged creatures a third time at run time. "
            "Distribution infrastructure stays Phase G."
        ),
        "source_artifacts": [
            "game/src/mecha_game/packs.py",
            "data/packs/mechagotchi_starter_pack.json",
            "data/slips/valid",
            "data/workshop/released",
        ],
        "metrics": {
            "starter_pack": {
                "slips": len(pack["slips"]),
                "creatures": len(pack["creatures"]),
                "provenance": pack["provenance"],
            },
            "import_report": {
                "slips_staged": sum(
                    1 for s in report["slips"] if s["ok"]
                ),
                "creatures_staged": sum(
                    1 for c in report["creatures"] if c["ok"]
                ),
            },
            "era_admission": {
                "admitted_ids": verdict["admitted_ids"],
                "rejected_ids": rejected_ids,
                "first_rejection_error": (
                    verdict["rejected"][0]["errors"][0]
                    if verdict["rejected"]
                    else None
                ),
            },
            "era_survived": not era["derived"]["went_extinct"],
        },
        "closed_states": [
            "the_pack_format_exists (one importable file: SLIPs + "
            "creatures + provenance; the starter pack is committed "
            "material, built deterministically)",
            "three_layers_of_engine_gates (build refuses invalid; "
            "import re-judges and stages per-item; the era admission "
            "gates judge staged creatures at run time — measured: "
            "the 8×8 pair rejected verbatim, the beetle admitted)",
            "packs_ride_the_existing_inboxes (covenants → I imports "
            "them; creatures → W gathers them; K imports a pack in "
            "the client)",
        ],
        "blocked_states": [
            "distribution_is_phase_g (registries, sharing "
            "infrastructure, moderation — the documented late-stage "
            "community scope; this rung is the CARRIER format)",
            "pack_signing_unversioned (provenance is declarative; "
            "integrity/signature schemes belong with Phase G's "
            "distribution decisions)",
        ],
        "decision": (
            "adopt: the community carrier exists; F17 closes the "
            "carried remainders, F18 gates MVP 0.3"
        ),
        "next_research_step": (
            "F17 — carried remainders (replay persistence, "
            "spent-covenant resume, windowed launch-verify)"
        ),
    }


def write_community_pack_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{PACKS_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


COVENANT_IO_ARTIFACT_ID = "covenant_io_stage0"


def build_covenant_io_report() -> dict:
    """F15's measured claims at session scale: the ACTIVE covenant
    (spends included) exports verbatim as a shareable SLIP; imports
    pass the authority AND the corpus-compatibility gate with verbatim
    refusals applying nothing; an accepted import becomes the new
    base; the round trip is identity; an era runs under an imported
    zoo covenant."""
    import tempfile

    from mecha_game.covenant import apply_covenant_change
    from mecha_game.covenant_io import export_covenant, import_covenant

    inputs = _campaign_inputs(session_scale=True)
    campaign = KeeperCampaign(inputs, campaign_id="io_evidence")
    campaign.advance_era("calm")
    spend = apply_covenant_change(
        campaign,
        deliberation_max_ticks=campaign.budget()[
            "deliberation_max_ticks"
        ],
    )
    with tempfile.TemporaryDirectory() as tmp:
        exported_path = export_covenant(
            campaign, Path(tmp) / "covenant.json"
        )
        exported = json.loads(
            exported_path.read_text(encoding="utf-8")
        )
        export_verbatim = (
            exported == campaign.campaign["slip_profile"]
        )
        round_trip = import_covenant(campaign, exported_path)
    gray = import_covenant(
        campaign, ROOT / "data" / "slips" / "valid" / "slip_gray_stable.json"
    )
    era_under_import = campaign.advance_era("calm")
    bad = import_covenant(
        campaign,
        ROOT / "data" / "slips" / "failure_cases" / "slip_bad_version.json",
    )
    impossible = json.loads(
        (ROOT / HELLO_SLIP).read_text(encoding="utf-8")
    )
    impossible["grid"]["body_mass_min"] = 200
    impossible["grid"]["body_mass_max"] = 256
    with tempfile.TemporaryDirectory() as tmp:
        impossible_path = Path(tmp) / "impossible.json"
        impossible_path.write_text(
            json.dumps(impossible), encoding="utf-8"
        )
        incompatible = import_covenant(campaign, impossible_path)
    status = (
        "complete"
        if spend["ok"]
        and export_verbatim
        and round_trip["ok"]
        and gray["ok"]
        and bool(era_under_import["elites"])
        and not bad["ok"]
        and any("authority rejects" in v for v in bad["violations"])
        and not incompatible["ok"]
        and any(
            "no seed grid satisfies" in v
            for v in incompatible["violations"]
        )
        else "refuted"
    )
    return {
        "artifact_id": COVENANT_IO_ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 16 F15 (GAME track, Phase F, MVP 0.3): SLIP "
            "import/export in the product — the active covenant "
            "(spends included) exports VERBATIM as a shareable SLIP "
            "(the zoo's convention, no wrapper); imports pass the "
            "engine's authority and evolve's own corpus-"
            "compatibility rule with verbatim refusals applying "
            "NOTHING; an accepted import is the new species contract "
            "and governs the next era."
        ),
        "source_artifacts": [
            "game/src/mecha_game/covenant_io.py",
            "data/slips/valid/slip_gray_stable.json",
            "data/slips/failure_cases/slip_bad_version.json",
            "research/decision_records/0012-slip-schema-extension-ladder.md",
        ],
        "metrics": {
            "spent_covenant_exported_verbatim": export_verbatim,
            "round_trip_ok": round_trip["ok"],
            "zoo_import_ok": gray["ok"],
            "zoo_import_aligned_seeds": gray.get("aligned_seeds"),
            "era_under_imported_covenant_elites": len(
                era_under_import["elites"]
            ),
            "invalid_refused_verbatim": (
                not bad["ok"] and bad["violations"][:1]
            ),
            "incompatible_refused_named": (
                not incompatible["ok"]
                and incompatible["violations"][:1]
            ),
        },
        "closed_states": [
            "covenants_are_shareable_files (export verbatim — an "
            "authority-validated SLIP needs no wrapper; X/I in the "
            "client via the keeper/covenants inbox, the F9 file-"
            "bridge pattern)",
            "imports_pass_two_engine_gates (the authority verbatim + "
            "evolve's no-seed-satisfies rule via is_grid_aligned; "
            "refusals apply nothing)",
            "an_import_is_a_new_species_contract (base AND active "
            "covenant replaced; the earned budget recomputes; spends "
            "re-apply by choice, never silently)",
        ],
        "blocked_states": [
            "companion_covenant_changes_on_next_adoption (a live "
            "pet's covenant never swaps under it — imports govern "
            "future adoptions/hatches/eras)",
            "pack_bundling_is_F16 (a covenant plus creatures plus "
            "provenance in one importable file)",
        ],
        "decision": (
            "adopt: covenants travel; F16 bundles the community pack "
            "format"
        ),
        "next_research_step": (
            "F16 — community profile packs at the FORMAT rung"
        ),
    }


def write_covenant_io_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{COVENANT_IO_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


LINEAGE_ARTIFACT_ID = "lineage_story_stage0"


def build_lineage_story_report() -> dict:
    """F14's measured claims: a real multi-life story — founder →
    starvation → succession, twice — browsable with every line a
    record field verbatim: origins (founder/succession), the engine's
    death causes, the growing ancestor chain in the grid schema's own
    lineage blocks; the story rides the save file; twin runs equal."""
    import tempfile

    from mecha_game.lineage import LineageBrowser

    def run_story() -> tuple[list[dict], list[str]]:
        session = _new_session()
        captions: list[str] = []
        for _ in range(2):
            while session.alive:
                session.advance()
            session.succeed()
        browser = LineageBrowser(session.lineage)
        browser.index = 0
        for _ in range(browser.count):
            captions.append(browser.caption())
            browser.step()
        with tempfile.TemporaryDirectory() as tmp:
            path = session.save(Path(tmp) / "companion.json")
            resumed = CompanionSession.load(path)
        assert resumed.lineage == session.lineage
        return session.lineage, captions

    first_lineage, first_captions = run_story()
    second_lineage, second_captions = run_story()
    deterministic = (
        first_lineage == second_lineage
        and first_captions == second_captions
    )
    origins = [record["origin"] for record in first_lineage]
    causes = [
        record.get("death_cause")
        for record in first_lineage
        if "death_cause" in record
    ]
    ancestor_depths = [
        len((record.get("lineage") or {}).get("ancestor_ids") or [])
        for record in first_lineage
    ]
    chain_grows = ancestor_depths == sorted(ancestor_depths) and (
        ancestor_depths[-1] > ancestor_depths[0]
    )
    status = (
        "complete"
        if deterministic
        and origins == ["founder", "succession", "succession"]
        and len(causes) == 2
        and all(causes)
        and chain_grows
        else "refuted"
    )
    return {
        "artifact_id": LINEAGE_ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 16 F14 (GAME track, Phase F, MVP 0.3): the "
            "lineage browser — the Keeper's whole story browsable, "
            "every line a record field verbatim: how each life began "
            "(the additive origin fact), how it ended (the engine's "
            "own death cause), and the grid schema's lineage blocks "
            "(generation, the growing ancestor chain, mutation "
            "events). Nothing invented."
        ),
        "source_artifacts": [
            "game/src/mecha_game/lineage.py",
            "game/src/mecha_game/session.py",
            "research/grid_genome/grid_genome.schema.json",
        ],
        "metrics": {
            "lives": len(first_lineage),
            "origins": origins,
            "death_causes": causes,
            "ancestor_chain_depths": ancestor_depths,
            "ancestor_chain_grows": chain_grows,
            "captions": first_captions,
            "save_round_trips_the_story": True,
            "twin_run_equal": deterministic,
        },
        "closed_states": [
            "the_story_is_records (origins + engine death causes + "
            "verbatim lineage blocks; L pages it in the client)",
            "origins_are_additive (founder/hatched/era_elite/"
            "succession ride the lineage records and the save file; "
            "old saves without them stay loadable — pinned)",
            "the_ancestor_chain_is_the_engines (generate_candidate's "
            "own ancestor_ids, growing across successions)",
        ],
        "blocked_states": [
            "cross_campaign_story_awaits_resume (the session's "
            "lineage browses today; weaving the ledger's era chain "
            "into one timeline is the F17 resume rung's material)",
            "no_body_thumbnails_for_past_lives (lineage records are "
            "id+metadata by design — a live pet is not evidence, and "
            "dead bodies are not stored; the repertoire browses the "
            "archive's stored bodies instead)",
        ],
        "decision": (
            "adopt: the lineage browser ships; F15 imports/exports "
            "the covenant"
        ),
        "next_research_step": (
            "F15 — SLIP import/export through the engine's authority"
        ),
    }


def write_lineage_story_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{LINEAGE_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


REPERTOIRE_ARTIFACT_ID = "repertoire_stage0"


def build_repertoire_report() -> dict:
    """F13's measured claims at session scale: the whole era archive
    browsable — EVERY elite renders a real packet under the covenant,
    every caption/axes/components line is record fields verbatim,
    paging and era switching deterministic."""
    from mecha_game.repertoire import RepertoireBrowser

    inputs = _campaign_inputs(session_scale=True)
    campaign = KeeperCampaign(
        inputs, campaign_id="repertoire_evidence"
    )
    campaign.advance_era("calm")
    campaign.advance_era("stable_soup")

    def browse_run() -> dict:
        browser = RepertoireBrowser(campaign)
        rendered = 0
        packet_ids_match = True
        samples = []
        for position in range(browser.count):
            packet = browser.packet()
            rendered += 1
            if packet["grid_id"] != browser.current()["grid_id"]:
                packet_ids_match = False
            if position < 3:
                samples.append(
                    {
                        "caption": browser.caption(),
                        "axes": browser.axes_line(),
                        "components": browser.components_line(),
                    }
                )
            browser.step()
        browser.previous_era()
        first_era_count = browser.count
        return {
            "latest_era_elites": len(
                campaign.eras[-1]["elites"]
            ),
            "rendered": rendered,
            "packet_ids_match": packet_ids_match,
            "samples": samples,
            "first_era_elites_via_switch": first_era_count,
        }

    first = browse_run()
    second = browse_run()
    deterministic = first == second
    all_rendered = first["rendered"] == first["latest_era_elites"]
    era_switch_true = first["first_era_elites_via_switch"] == len(
        campaign.eras[0]["elites"]
    )
    status = (
        "complete"
        if deterministic
        and all_rendered
        and first["packet_ids_match"]
        and era_switch_true
        else "refuted"
    )
    return {
        "artifact_id": REPERTOIRE_ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 16 F13 (GAME track, Phase F, MVP 0.3): the "
            "repertoire browser — the era archive's elites surfaced "
            "as a browsable product (species memory visible): niche "
            "order, the descriptor's NAMED axes, fitness and its "
            "components, the body drawn from its real packet under "
            "the covenant — record fields verbatim, nothing "
            "re-derived."
        ),
        "source_artifacts": [
            "game/src/mecha_game/repertoire.py",
            "game/src/mecha_game/campaign.py",
            "research/experiment_reports/2026-07-09-phase-e-gate.md",
        ],
        "metrics": {
            "eras": len(campaign.eras),
            "latest_era_elites": first["latest_era_elites"],
            "every_elite_rendered": all_rendered,
            "packet_ids_match_records": first["packet_ids_match"],
            "era_switch_reaches_the_first_era": era_switch_true,
            "twin_run_equal": deterministic,
            "display_samples": first["samples"],
        },
        "closed_states": [
            "species_memory_visible (the archive browsable in the "
            "client: B opens it, ./,/[/] drive it, A adopts the "
            "BROWSED elite — the repertoire is a place the Keeper "
            "shops for their next companion)",
            "captions_are_records (descriptor names+values, fitness "
            "components, lineage generation — verbatim)",
            "every_body_real (each elite drawn from render_packet_v2 "
            "under the campaign covenant)",
        ],
        "blocked_states": [
            "ledger_sourced_browsing_awaits_resume (in-memory eras "
            "browse today; past-campaign browsing across restarts "
            "rides the F17 resume rung — the ledger already stores "
            "the records verbatim)",
            "family_view_awaits_a_consumer_rung (E5's recurrent-"
            "family clustering is lab math; a cross-era family lens "
            "is a named future rung, not smuggled client statistics)",
        ],
        "decision": (
            "adopt: the archive is a product surface; F14 browses "
            "the lineage"
        ),
        "next_research_step": (
            "F14 — the lineage browser (the Keeper's whole story "
            "from the verbatim lineage blocks and the ledger)"
        ),
    }


def write_repertoire_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{REPERTOIRE_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


REVIEW_ARTIFACT_ID = "review_replay_stage0"


def build_review_replay_report() -> dict:
    """F10's measured claims at session scale: the Review replays the
    era's best elite at the era's own seed — a REAL recorded life
    (live_cycle record_frames, DR 0023) with the full phase
    vocabulary, the scrubber invariant holding at every frame, twin
    runs byte-equal, and the honest label riding the artifact."""
    from mecha_game.replay import ReplayPlayer

    inputs = _campaign_inputs(session_scale=True)
    campaign = KeeperCampaign(inputs, campaign_id="review_evidence")
    era = campaign.advance_era("calm")
    replay = campaign.record_review_replay()
    twin = campaign.record_review_replay()
    deterministic = json.dumps(replay, sort_keys=True) == json.dumps(
        twin, sort_keys=True
    )
    phases: dict[str, int] = {}
    for frame in replay["frames"]:
        phases[frame["phase"]] = phases.get(frame["phase"], 0) + 1
    player = ReplayPlayer(replay)
    invariant_holds = all(
        player.body_packet_at(i) is not None
        for i in range(replay["frame_count"])
    )
    best_id = max(
        era["elites"], key=lambda e: (e["fitness"], e["niche_key"])
    )["grid"]["grid_id"]
    status = (
        "complete"
        if deterministic
        and replay["creature"]["grid_id"] == best_id
        and replay["parameters"]["rng_seed"] == era["rng_seed"]
        and replay["tick_frame_count"] > 0
        and invariant_holds
        else "refuted"
    )
    return {
        "artifact_id": REVIEW_ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 15 F10 (GAME track, Phase F, MVP 0.2): the Review "
            "step — the era's best elite lives one RECORDED life "
            "(live_cycle record_frames, DR 0023) replayed in the "
            "client at the era's own seed, scrubber-lite "
            "(play/pause/step) over birth/wound/repair/episode "
            "frames, the wound overlay from the damage event's own "
            "removed_cells, the honest label shown."
        ),
        "source_artifacts": [
            "game/src/mecha_game/replay.py",
            "game/src/mecha_game/campaign.py",
            "labs/game_loop/replay_recorder.py",
            "research/decision_records/0023-replay-recording.md",
        ],
        "metrics": {
            "creature": replay["creature"],
            "parameters": replay["parameters"],
            "honest_label": replay["honest_label"],
            "frame_count": replay["frame_count"],
            "phase_counts": phases,
            "tick_frame_count": replay["tick_frame_count"],
            "all_cycles_valid": replay["live"]["all_cycles_valid"],
            "all_cycles_aligned": replay["live"]["all_cycles_aligned"],
            "twin_run_byte_equal": deterministic,
            "replays_the_best_elite_at_the_era_seed": (
                replay["creature"]["grid_id"] == best_id
                and replay["parameters"]["rng_seed"] == era["rng_seed"]
            ),
            "scrubber_invariant_holds_at_every_frame": invariant_holds,
        },
        "closed_states": [
            "review_is_a_recorded_life (the R5 contract mirrored "
            "over engine publics; the replay never invents a "
            "displayable body — packets only for validator-passing "
            "states, errors verbatim)",
            "scrubber_lite (V opens the review; SPACE/./, drive it; "
            "the body at frame i is the latest packet-bearing frame "
            "<= i — the shared drawer's invariant, pinned per frame)",
            "wounds_are_engine_observability (the overlay marks the "
            "damage event's own removed_cells, the drawer's fill as "
            "arithmetic)",
            "honest_labeling (a real recorded life of a real era "
            "creature, replayed post-era at the era's own seed — "
            "shown in the review footer)",
        ],
        "blocked_states": [
            "in_era_lives_not_frame_recorded (threading "
            "record_frames through evolve is the engine's named "
            "future seam — the lab's honest note, unchanged)",
            "replay_persistence (the ledger's record_replay surface "
            "exists; the client records on demand and does not "
            "persist replays yet — a 0.3 saves rung)",
            "truncated_lives_display_honestly (an unaligned repair "
            "ends the recording early — pinned by test; the review "
            "shows exactly what the engine lived)",
        ],
        "decision": (
            "adopt: DR 0021's Review step is a product surface; F11 "
            "hardens, F12 gates MVP 0.2"
        ),
        "next_research_step": (
            "F11 — product hardening (era model caching, windowed "
            "build, mechas commands)"
        ),
    }


def write_review_replay_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{REVIEW_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


CONTRIBUTE_ARTIFACT_ID = "contribute_bridge_stage0"


def build_contribute_bridge_report() -> dict:
    """F9's measured claims at session scale: the committed workshop
    releases enter an era and the ENGINE judges them — the 8×8 pair
    is rejected VERBATIM on size coherence (recorded, shown), a
    16×16 covenant-aligned release is ADMITTED and LEADS the pool;
    the era survives either way; twin runs byte-equal."""
    from mecha_game.contribute import (
        founders_verdict,
        load_released_grids,
    )

    inputs = _campaign_inputs(session_scale=True)
    workshop_inbox = ROOT / "data" / "workshop" / "released"

    def run_cycle() -> dict:
        campaign = KeeperCampaign(
            inputs, campaign_id="contribute_evidence"
        )
        committed = load_released_grids(workshop_inbox)
        aligned_release = json.loads(
            json.dumps(inputs["seed_grids"][1])
        )
        aligned_release["grid_id"] = "released_workshop_16"
        era = campaign.advance_era(
            "calm", released_grids=committed + [aligned_release]
        )
        verdict = founders_verdict(era)
        return {
            "submitted": era["founders_submitted"],
            "verdict": verdict,
            "era_survived": not era["derived"]["went_extinct"],
            "elites": len(era["elites"]),
        }

    first = run_cycle()
    second = run_cycle()
    deterministic = first == second
    verdict = first["verdict"]
    rejected_ids = [r["grid_id"] for r in verdict["rejected"]]
    size_rejections_verbatim = all(
        any("8x8" in error and "16x16" in error for error in r["errors"])
        for r in verdict["rejected"]
    )
    # H1 raised the committed corpus's truth: the authored 16×16
    # lantern admits alongside the renamed aligned seed; the 8×8
    # pair still rejects verbatim. Submissions lead in file order.
    admitted_leads = (
        "released_workshop_16" in verdict["admitted_ids"]
        and "released_glow_lantern" in verdict["admitted_ids"]
        and first["submitted"][-1] == "released_workshop_16"
        and set(first["submitted"][:3])
        == {
            "released_glow_lantern",
            "released_tall_wisp",
            "released_wide_sentinel",
        }
    )
    status = (
        "complete"
        if deterministic
        and sorted(rejected_ids)
        == ["released_tall_wisp", "released_wide_sentinel"]
        and size_rejections_verbatim
        and admitted_leads
        and first["era_survived"]
        else "refuted"
    )
    return {
        "artifact_id": CONTRIBUTE_ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 15 F9 (GAME track, Phase F, MVP 0.2): the "
            "Contribute step — workshop-released creatures enter the "
            "client's eras through the engine's own gates. A FILE "
            "bridge (the lab's inbox rule: deterministic order, "
            "backups skipped) into the F8 era seam; admission is the "
            "ENGINE's verdict — the committed 8×8 releases rejected "
            "VERBATIM on DR 0029 size coherence, an aligned 16×16 "
            "release admitted and leading the pool — both shown to "
            "the Keeper, never smoothed."
        ),
        "source_artifacts": [
            "game/src/mecha_game/contribute.py",
            "data/workshop/released/released_tall_wisp.json",
            "data/workshop/released/released_wide_sentinel.json",
            "labs/game_loop/session_runner.py",
            "packages/mecha_engine/src/mecha_engine/runtime/evolve.py",
        ],
        "metrics": {
            "cycle": first,
            "twin_run_equal": deterministic,
            "committed_releases_rejected_verbatim": (
                size_rejections_verbatim
            ),
            "aligned_release_admitted_and_leads": admitted_leads,
        },
        "closed_states": [
            "contribute_is_a_file_bridge (the workshop keeps its own "
            "stack; inboxes: data/workshop/released + the player's "
            "keeper/released)",
            "admission_is_the_engines_verdict (DR 0016 founders-lead "
            "+ DR 0029 size coherence + SLIP alignment, recorded in "
            "the era report's founders block and shown in the era "
            "message)",
            "rejections_are_verbatim (the 8×8 committed releases "
            "reject with the engine's own size error — an honest, "
            "documented outcome, not a bridge failure)",
        ],
        "blocked_states": [
            "workshop_authoring_at_16x16 (the committed releases are "
            "8×8-era pieces; a 16×16 authored release will admit the "
            "day the workshop saves one — the bridge needs no change)",
            "release_provenance_display (the inspector's released-"
            "ancestry browsing stays workshop-side; the client shows "
            "the verdict, not the full ancestry — a 0.3 lineage-"
            "browser rung)",
        ],
        "decision": (
            "adopt: DR 0021's Contribute step is a product surface; "
            "F10 brings the Review replays"
        ),
        "next_research_step": (
            "F10 — the Review step: era replays in the client "
            "(scrubber-lite over the R5 recorder)"
        ),
    }


def write_contribute_bridge_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{CONTRIBUTE_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


HATCHERY_ARTIFACT_ID = "hatchery_stage0"


def build_hatchery_report(count: int = 3) -> dict:
    """F8's measured claims at session scale: founders GENERATED under
    the covenant (profile-weighted, validator-gated, adoptable through
    the engine's own gate), every origin legible from the verbatim
    generation trace, twin runs byte-equal, and a released founder
    LEADS the next era's pool through the engine's admission gates."""
    from mecha_engine.lifecycle import initial_state
    from mecha_engine.slip import is_grid_aligned

    from mecha_game.hatchery import hatch_founders, origin_summary

    inputs = _campaign_inputs(session_scale=True)

    def hatch_run() -> list[dict]:
        return hatch_founders(
            inputs["seed_grids"],
            inputs["slip_profile"],
            count=count,
            rng_seed=20260713,
        )

    first = hatch_run()
    second = hatch_run()
    deterministic = json.dumps(first, sort_keys=True) == json.dumps(
        second, sort_keys=True
    )
    ids = [entry["grid"]["grid_id"] for entry in first]
    all_adoptable = all(
        initial_state(entry["grid"], inputs["slip_profile"])["alive"]
        for entry in first
    )
    all_aligned = all(
        is_grid_aligned(entry["grid"], inputs["slip_profile"])
        for entry in first
    )
    origins = [origin_summary(entry["explanation"]) for entry in first]

    campaign = KeeperCampaign(inputs, campaign_id="hatch_evidence")
    campaign.advance_era("calm")
    era = campaign.advance_era(
        "calm", released_grids=[first[0]["grid"]]
    )
    released_leads = era["founders_submitted"][0] == ids[0]

    status = (
        "complete"
        if deterministic
        and len(set(ids)) == count
        and all_adoptable
        and all_aligned
        and released_leads
        and not era["derived"]["went_extinct"]
        else "refuted"
    )
    return {
        "artifact_id": HATCHERY_ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 15 F8 (GAME track, Phase F, MVP 0.2): species "
            "generation in the client — founders GENERATED through "
            "the promoted constrained surfaces under the covenant "
            "(profile-weighted, validator-gated), every creature's "
            "origin LEGIBLE from explain_generation's verbatim trace, "
            "and released founders LEADING the next era's pool "
            "through the engine's own admission gates (the lab's "
            "founders-lead rule). Generation stops being a "
            "fixtures-only path."
        ),
        "source_artifacts": [
            "game/src/mecha_game/hatchery.py",
            "game/src/mecha_game/campaign.py",
            "packages/mecha_engine/src/mecha_engine/generation/__init__.py",
            "research/decision_records/0031-wfc-generation-adoption.md",
        ],
        "metrics": {
            "count": count,
            "hatched_ids": ids,
            "origins": origins,
            "explanations": [entry["explanation"] for entry in first],
            "twin_run_equal": deterministic,
            "all_adoptable_through_the_gate": all_adoptable,
            "all_covenant_aligned": all_aligned,
            "released_founder_leads_the_pool": released_leads,
            "era_with_release_survived": not era["derived"][
                "went_extinct"
            ],
        },
        "closed_states": [
            "generation_is_a_product_path (hatch under the ACTIVE "
            "covenant in the client: H adopts the hatchling, R "
            "releases a genome into the next era)",
            "origins_are_legible (the display line is built only "
            "from the engine's generation trace fields)",
            "released_founders_lead (the lab's E5 seam consumed: "
            "releases ahead of elites, admission judged by evolve)",
        ],
        "blocked_states": [
            "workshop_releases_are_F9 (this rung releases HATCHED "
            "and adopted genomes; the workshop's authored creatures "
            "arrive with the F9 bridge)",
            "wfc_stays_era_side (DR 0031's production generator runs "
            "inside the engine; the hatchery is the constrained "
            "stabilizer because only its candidates carry the "
            "explanation trace — a WFC hatchery path would need an "
            "engine-side trace seam, named not smuggled)",
        ],
        "decision": (
            "adopt: the creator loop's generation rung is a product "
            "surface; F9 bridges the workshop"
        ),
        "next_research_step": (
            "F9 — the Contribute step: workshop-released creatures "
            "enter the client's eras as founders"
        ),
    }


def write_hatchery_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{HATCHERY_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


COVENANT_ARTIFACT_ID = "covenant_spending_stage0"


def build_covenant_spending_report() -> dict:
    """F7's measured claims, at the session scale: real eras EARN the
    facts; an over-budget request is REFUSED verbatim with nothing
    applied; the one-key spends apply inside the budget; the SPENT
    covenant governs the next era; the whole sequence twin-runs equal.
    (The builder's components are pinned by test_covenant/test_campaign;
    this artifact is the measured product cycle.)"""
    from mecha_game.covenant import (
        apply_covenant_change,
        spend_deliberation_to_budget,
        spend_next_palette,
        spend_population_to_cap,
    )

    def run_cycle() -> dict:
        inputs = _campaign_inputs(session_scale=True)
        campaign = KeeperCampaign(
            inputs, campaign_id="covenant_evidence"
        )
        campaign.advance_era("calm")
        earned = [
            (fact["axis"], fact["tier"]) for fact in campaign.unlocks
        ]
        budget_before = campaign.budget()
        covenant_before = json.loads(
            json.dumps(campaign.campaign["slip_profile"])
        )
        over_budget = apply_covenant_change(
            campaign,
            deliberation_max_ticks=budget_before[
                "deliberation_max_ticks"
            ]
            + 1,
        )
        nothing_applied = (
            campaign.campaign["slip_profile"] == covenant_before
        )
        spends = {
            "palette": spend_next_palette(campaign),
            "thinking": spend_deliberation_to_budget(campaign),
            "population": spend_population_to_cap(campaign),
        }
        era_after = campaign.advance_era("stable_soup")
        return {
            "facts_earned_era0": earned,
            "budget_after_era0": {
                key: budget_before[key]
                for key in (
                    "allowed_palettes",
                    "deliberation_max_ticks",
                    "population_cap",
                    "generation_cap",
                    "legibility_blend",
                )
            },
            "over_budget_refused": not over_budget["ok"],
            "refusal_violations": over_budget["violations"],
            "nothing_applied_on_refusal": nothing_applied,
            "spends": {
                name: {
                    "ok": result["ok"],
                    "violations": result.get("violations", []),
                }
                for name, result in spends.items()
            },
            "spent_covenant": {
                "allowed_palettes": campaign.campaign["slip_profile"][
                    "grid"
                ]["allowed_palettes"],
                "deliberation": campaign.campaign["slip_profile"].get(
                    "deliberation"
                ),
                "population": campaign.era_config["population"],
            },
            "era_under_spent_covenant": {
                "elites": len(era_after["elites"]),
                "went_extinct": era_after["derived"]["went_extinct"],
                "population_requested": campaign.era_config[
                    "population"
                ],
            },
        }

    first = run_cycle()
    second = run_cycle()
    deterministic = first == second
    all_spends_ok = all(
        spend["ok"] for spend in first["spends"].values()
    )
    status = (
        "complete"
        if deterministic
        and first["facts_earned_era0"]
        and first["over_budget_refused"]
        and first["nothing_applied_on_refusal"]
        and all_spends_ok
        and first["era_under_spent_covenant"]["elites"] > 0
        else "refuted"
    )
    return {
        "artifact_id": COVENANT_ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 15 F7 (GAME track, Phase F, MVP 0.2): covenant "
            "spending — the earned unlock facts SPEND into the "
            "covenant inside a pure budget (DR 0021's progression "
            "table, the session lab's semantics mirrored); "
            "over-budget requests are refused with named violations "
            "and nothing applied; every accepted covenant passes the "
            "engine's SLIP authority; the SPENT covenant governs the "
            "next era. The progression is FELT."
        ),
        "source_artifacts": [
            "game/src/mecha_game/covenant.py",
            "game/src/mecha_game/campaign.py",
            "labs/game_loop/session_runner.py",
            "research/decision_records/0021-game-loop.md",
        ],
        "metrics": {
            "cycle": first,
            "twin_run_equal": deterministic,
            "all_spends_applied": all_spends_ok,
        },
        "closed_states": [
            "budget_is_pure_and_earned (base covenant + base "
            "parameters + facts; palettes per niche tier, thinking "
            "per bloodline tier on the authority's 2-tick floor, "
            "caps doubling per qd tier, the blend stepping)",
            "refusal_is_total (named violations, nothing applied, "
            "the authority's verdicts verbatim)",
            "spent_covenant_governs (the next era runs under the "
            "spent profile and caps; past eras stay reproducible in "
            "the ledger verbatim)",
            "successor_inherits_unlocks_not_spends (roguelite: the "
            "budget survives, the covenant and caps reset to base)",
            "adopted_elites_live_under_the_active_covenant (a spent "
            "thinking budget makes the companion visibly deliberate)",
        ],
        "blocked_states": [
            "organ_role_budget_deferred (awaiting an allowed_roles "
            "SLIP field — the lab's named deferral, mirrored)",
            "harsher_forecasts_deferred (storm_record tiers await "
            "weather sources beyond the three shipped forecasts)",
        ],
        "decision": (
            "adopt: the Covenant step is a product surface; F8 "
            "surfaces species generation"
        ),
        "next_research_step": (
            "F8 — species generation in the client (the promoted "
            "constrained/WFC surfaces produce adoptable/releasable "
            "founders under the covenant)"
        ),
    }


def write_covenant_spending_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{COVENANT_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


RELEASE_ARTIFACT_ID = "installable_release_stage0"


def build_installable_release_report(
    bundle_dir: str | Path | None = None,
) -> dict | None:
    """F5's verification, run against an EXISTING build (produce one
    with ``uv run python -B game/build_release.py``); returns None —
    never a fabricated artifact — when no build is present.

    The player loop, observed: launch the built executable fresh
    (play N ticks, quit → save written), launch it again (RESUME →
    the same life continues). Machine-specific facts (sizes, paths)
    are recorded as observations, never pinned (the H-01 rule)."""
    import subprocess
    import tempfile

    bundle = Path(bundle_dir or ROOT / "game" / "dist" / "Mechagotchi")
    exe = bundle / (
        "Mechagotchi.exe" if sys.platform == "win32" else "Mechagotchi"
    )
    if not exe.is_file():
        return None
    bundled_corpus = (
        bundle / "_internal" / "data" / "seed_grids_16x16"
    ).is_dir()
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ)
        env["SDL_VIDEODRIVER"] = "dummy"
        base = ["--tick-frames", "1", "--fps", "0", "--scale", "2"]
        first = subprocess.run(
            [str(exe), "--ticks", "4", "--keeper-dir", tmp, *base],
            capture_output=True,
            text=True,
            env=env,
            timeout=300,
        )
        save_path = Path(tmp) / "companion.json"
        fresh_age = (
            json.loads(save_path.read_text(encoding="utf-8"))["state"][
                "age_ticks"
            ]
            if save_path.is_file()
            else None
        )
        second = subprocess.run(
            [str(exe), "--ticks", "3", "--keeper-dir", tmp, *base],
            capture_output=True,
            text=True,
            env=env,
            timeout=300,
        )
        resumed_age = (
            json.loads(save_path.read_text(encoding="utf-8"))["state"][
                "age_ticks"
            ]
            if save_path.is_file()
            else None
        )
    resumed = fresh_age == 4 and resumed_age == 7
    launches = first.returncode == 0 and second.returncode == 0
    status = (
        "complete"
        if launches and resumed and bundled_corpus
        else "refuted"
    )
    return {
        "artifact_id": RELEASE_ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 14 F5 (GAME track, Phase F): MVP 0.1 as a PRODUCT "
            "— a player can install, launch, play, quit, and RESUME "
            "from a save file. PyInstaller one-directory build "
            "(DR 0033 named it; this rung decided it) bundling the "
            "seed corpus, the LCD covenant, and the adopted "
            "readability model; the client resolves bundled data via "
            "the frozen-bundle origins; saves live in the player's "
            "own home outside a checkout."
        ),
        "source_artifacts": [
            "game/build_release.py",
            "game/src/mecha_game/session.py",
            "game/src/mecha_game/app.py",
            "research/decision_records/0033-game-front-end-technology.md",
        ],
        "metrics": {
            "bundle_present": True,
            "bundled_data_corpus": bundled_corpus,
            "fresh_launch_exit": first.returncode,
            "resume_launch_exit": second.returncode,
            "fresh_save_age_ticks": fresh_age,
            "resumed_save_age_ticks": resumed_age,
            "resume_continues_the_same_life": resumed,
        },
        "closed_states": [
            "install_launch_play_quit_resume (the F5 sentence, "
            "observed on the built executable end to end)",
            "session_save_resume (keeper_session_v1: state, log, "
            "lineage, and the succession model verbatim; resumed "
            "twins continue byte-identically, pinned in the suite)",
            "bundled_data_resolution (sys._MEIPASS origins joined "
            "the walk-up rule; the dev checkout path is unchanged)",
        ],
        "blocked_states": [
            "full_ci_reproducibility_is_phase_g (the build is "
            "verified on this machine; CI packaging, signing, and "
            "multi-platform matrices are the documented Phase-G "
            "delivery scope)",
            "machine_specific_observations_not_pinned (bundle size "
            "and timings vary by host; the suite pins behavior, "
            "never the build environment — H-01)",
        ],
        "decision": (
            "adopt: MVP 0.1 is installable; F6 judges the Phase-F "
            "MVP 0.1 gate"
        ),
        "next_research_step": (
            "F6 — the consolidated Phase-F MVP 0.1 gate report; the "
            "0.2/0.3 rungs decompose from the gap analysis"
        ),
    }


def write_installable_release_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{RELEASE_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


CAMPAIGN_ARTIFACT_ID = "keeper_campaign_stage0"


def _campaign_inputs(session_scale: bool) -> dict:
    return load_campaign_inputs(
        ROOT / "data" / "seed_grids_16x16",
        ROOT / HELLO_SLIP,
        ROOT
        / "data"
        / "readability_benchmark"
        / "adopted_readability_model.json",
        repair_epochs=40 if session_scale else 6,
        seed_limit=None if session_scale else 12,
    )


def _run_keeper_campaign(
    inputs: dict, *, era_config: dict, eras: tuple[str, ...]
) -> KeeperCampaign:
    campaign = KeeperCampaign(
        inputs, era_config=era_config, campaign_id="evidence_campaign"
    )
    for weather in eras:
        if campaign.status != "active":
            break
        campaign.advance_era(weather)
    return campaign


def build_keeper_campaign_report(
    *,
    session_scale: bool = True,
    eras: tuple[str, ...] = ("calm", "stable_soup", "storm"),
) -> dict:
    """F4's measured claims: the client's era loop is one promoted
    evolve run per era at the A4 session scale, founders chain from
    elites, unlock facts are earned from report metrics, the ledger
    round-trips losslessly, the best elite adopts through the engine
    gate, and eras are deterministic (twin first eras byte-equal)."""
    import sqlite3
    import tempfile

    from mecha_engine.lifecycle import initial_state
    from mecha_engine.storage import campaign_history, open_ledger

    era_config = ERA_CONFIG if session_scale else TINY_ERA_CONFIG
    inputs = _campaign_inputs(session_scale)
    campaign = _run_keeper_campaign(
        inputs, era_config=era_config, eras=eras
    )
    twin = _run_keeper_campaign(
        inputs, era_config=era_config, eras=eras[:1]
    )
    deterministic = json.dumps(
        campaign.eras[0], sort_keys=True
    ) == json.dumps(twin.eras[0], sort_keys=True)

    chains = all(
        campaign.eras[i]["founders_submitted"]
        == [
            elite["grid"]["grid_id"]
            for elite in campaign.eras[i - 1]["elites"]
        ]
        for i in range(1, len(campaign.eras))
    )
    elite = campaign.best_elite_grid()
    adoptable = False
    if elite is not None:
        adoptable = bool(
            initial_state(elite, inputs["slip_profile"])["alive"]
        )
    with tempfile.TemporaryDirectory() as tmp:
        ledger_path = Path(tmp) / "campaign.sqlite3"
        campaign.save(ledger_path)
        conn = open_ledger(ledger_path)
        try:
            history = campaign_history(conn, "evidence_campaign")
        finally:
            conn.close()
    round_trip = len(history["eras"]) == len(campaign.eras) and (
        history["eras"][0]["report"] == campaign.eras[0]["report"]
    )
    memory = campaign.species_memory()
    status = (
        "complete"
        if deterministic and chains and adoptable and round_trip
        else "refuted"
    )
    return {
        "artifact_id": CAMPAIGN_ARTIFACT_ID,
        "status": status,
        "date": REPORT_DATE,
        "purpose": (
            "Cycle 14 F4 (GAME track, Phase F): the Keeper/era loop "
            "in the client — DR 0021's core loop as a product surface "
            "mirroring the proven session lab over engine publics "
            "only: one era = one promoted evolve run (the A4 session "
            "scale), founders chain from elites, unlock facts earned "
            "from report metrics, the storage ledger persists "
            "losslessly, and the era's best elite ADOPTS as the "
            "companion through the same engine gate — species memory "
            "the player can hold."
        ),
        "source_artifacts": [
            "game/src/mecha_game/campaign.py",
            "game/src/mecha_game/app.py",
            "labs/game_loop/session_runner.py",
            "packages/mecha_engine/src/mecha_engine/runtime/__init__.py",
            "research/decision_records/0021-game-loop.md",
            "data/readability_benchmark/adopted_readability_model.json",
        ],
        "metrics": {
            "era_config": era_config,
            "session_scale": session_scale,
            "weather_schedule": list(eras),
            "eras_run": len(campaign.eras),
            "campaign_status": campaign.status,
            "species_memory": memory,
            "founders_chain_from_elites": chains,
            "first_era_twin_equal": deterministic,
            "best_elite_adoptable": adoptable,
            "ledger_round_trip": round_trip,
            "sqlite_version": sqlite3.sqlite_version,
        },
        "closed_states": [
            "era_loop_is_the_promoted_engine (one evolve run per era; "
            "the learned readability scorer injected from the new "
            "runtime export — the client re-implements nothing)",
            "founder_spine (each era's founders are the previous "
            "era's elites, verbatim grids)",
            "unlocks_are_earned_facts (the lab's A4-calibrated table, "
            "falsifiable by test; facts cite path/value/threshold)",
            "campaign_persists (DR 0022's ledger, blob-authoritative, "
            "idempotent re-save)",
            "species_memory_adoptable (the best elite becomes the "
            "companion through the engine's own adoption gate)",
        ],
        "blocked_states": [
            "replay_review_is_the_R5_scrubber (the lab records era "
            "replays; the client's Review step shows summary metrics "
            "only — the scrubber consumer is a named F-ladder rung)",
            "workshop_release_contribute_step (DR 0021's Contribute "
            "runs lab-side; the client's release flow waits for the "
            "workshop bridge)",
            "scale_geometry_seam_not_demanded (the client's eras run "
            "the A4 toy-scale config; the unpromoted archive "
            "scale-geometry seam stays unpromoted — this consumer "
            "did NOT demand it, recorded per the Phase-E remainder)",
            "real_cubff_weather_awaits_phase_g (synthetic snapshots "
            "mirror the lab; real exports drop into the same seam)",
        ],
        "decision": (
            "adopt: the Keeper loop plays in the client on engine "
            "truth; F5 packages it"
        ),
        "next_research_step": (
            "F5 — the installable release (PyInstaller named in "
            "DR 0033, decided at its own rung)"
        ),
    }


def write_keeper_campaign_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{CAMPAIGN_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


def write_fleet_consumers_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{FLEET_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


def write_render_bridge_artifacts(
    output_dir: str | Path, report: dict
) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{BRIDGE_ARTIFACT_ID}.json"
    path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    return path


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
    written = write_render_bridge_artifacts(
        args.output_dir, build_render_bridge_report()
    )
    print(f"wrote {written}")
    written = write_fleet_consumers_artifacts(
        args.output_dir, build_fleet_consumers_report()
    )
    print(f"wrote {written}")
    written = write_keeper_campaign_artifacts(
        args.output_dir, build_keeper_campaign_report()
    )
    print(f"wrote {written}")
    written = write_covenant_spending_artifacts(
        args.output_dir, build_covenant_spending_report()
    )
    print(f"wrote {written}")
    written = write_hatchery_artifacts(
        args.output_dir, build_hatchery_report()
    )
    print(f"wrote {written}")
    written = write_contribute_bridge_artifacts(
        args.output_dir, build_contribute_bridge_report()
    )
    print(f"wrote {written}")
    written = write_review_replay_artifacts(
        args.output_dir, build_review_replay_report()
    )
    print(f"wrote {written}")
    written = write_repertoire_artifacts(
        args.output_dir, build_repertoire_report()
    )
    print(f"wrote {written}")
    written = write_lineage_story_artifacts(
        args.output_dir, build_lineage_story_report()
    )
    print(f"wrote {written}")
    written = write_covenant_io_artifacts(
        args.output_dir, build_covenant_io_report()
    )
    print(f"wrote {written}")
    written = write_community_pack_artifacts(
        args.output_dir, build_community_pack_report()
    )
    print(f"wrote {written}")
    written = write_real_weather_artifacts(
        args.output_dir, build_real_weather_report()
    )
    print(f"wrote {written}")
    release_report = build_installable_release_report()
    if release_report is None:
        print(
            "no release build found (run game/build_release.py) — "
            "installable_release_stage0 not regenerated"
        )
    else:
        written = write_installable_release_artifacts(
            args.output_dir, release_report
        )
        print(f"wrote {written}")
