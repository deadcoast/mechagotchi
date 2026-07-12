"""The Mechagotchi window — the playable companion loop (F2, MVP 0.1).

A fixed-timestep pygame-ce loop over one `CompanionSession`: the LCD
panel (the composed engine frame) above the HUD strip (engine-truth
bars and ui_hints icons), with a text footer for mood/age/lineage —
every displayed number a state field, a packet field, or a lineage
record (DR 0021 first law). Pygame touches ONLY this layer.

Controls: F feed · P play · S sleep (queued for the next lifecycle
tick — the keeper answers the tick, mashing keys does not accelerate
time) · ENTER adopt the successor when the companion dies · ESC or
close to quit (the lineage file is saved on death and on quit).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from mecha_engine.genome import clip_frame_count

from mecha_game.clips import TRANSITIONS, ClipDriver
from mecha_game.hud import HUD_HEIGHT, render_hud
from mecha_game.packets import default_fixture_paths
from mecha_game.rasterize import (
    Buffer,
    apply_scanline,
    compose_frame,
    scale_buffer,
    stack_buffers,
)
from mecha_game.session import CompanionSession, load_session_inputs

WINDOW_TITLE = "Mechagotchi"
DEFAULT_CELL_PX = 24
DEFAULT_FPS = 8  # the LCD heartbeat (render frames)
DEFAULT_TICK_FRAMES = 12  # lifecycle tick every N frames (1.5 s at 8 fps)
FOOTER_PX = 72  # the casing's text area (chrome, not LCD)
LINEAGE_FILENAME = "lineage.json"


def default_keeper_dir(start: Path | None = None) -> Path:
    """The save home: `keeper/` at the repo root in a dev checkout
    (gitignored — a live pet is not evidence), else the user's own
    `~/.mechagotchi`."""
    origin = (start or Path(__file__)).resolve()
    for base in (origin, *origin.parents):
        if (base / "data" / "seed_grids_16x16").is_dir():
            return base / "keeper"
    return Path.home() / ".mechagotchi"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mechagotchi",
        description=(
            "Mechagotchi — raise a living grid creature; every pixel "
            "and number is the engine's own truth (MVP 0.1)"
        ),
    )
    parser.add_argument(
        "--seed",
        type=Path,
        default=None,
        help="founder grid genome JSON (default: the 16x16 corpus beetle)",
    )
    parser.add_argument(
        "--slip",
        type=Path,
        default=None,
        help="SLIP covenant JSON (default: the LCD seed profile)",
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=DEFAULT_CELL_PX,
        help=f"window pixels per LCD cell (default {DEFAULT_CELL_PX})",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=DEFAULT_FPS,
        help=f"render frames per second (default {DEFAULT_FPS}; 0 = uncapped)",
    )
    parser.add_argument(
        "--tick-frames",
        type=int,
        default=DEFAULT_TICK_FRAMES,
        help=(
            "render frames per lifecycle tick "
            f"(default {DEFAULT_TICK_FRAMES})"
        ),
    )
    parser.add_argument(
        "--ticks",
        type=int,
        default=None,
        help="quit after N lifecycle ticks (verification runs)",
    )
    parser.add_argument(
        "--auto-succeed",
        action="store_true",
        help="adopt the successor automatically on death (headless runs)",
    )
    parser.add_argument(
        "--keeper-dir",
        type=Path,
        default=None,
        help="save directory (default: repo keeper/ or ~/.mechagotchi)",
    )
    return parser


def _frame_bytes(pixels: Buffer) -> bytes:
    return b"".join(bytes(rgb) for row in pixels for rgb in row)


def _footer_lines(snapshot: dict, queued: str | None) -> list[str]:
    if not snapshot["alive"]:
        return [
            f"{snapshot['name']} died: {snapshot['death_cause']}"
            f" (age {snapshot['age_ticks']})",
            "ENTER: adopt successor    ESC: quit",
        ]
    needs = snapshot["needs"]
    line = (
        f"mood {snapshot['mood']}   age {snapshot['age_ticks']}   "
        f"gen {snapshot['generation_count']}"
    )
    if snapshot["begging"]:
        line += "   BEGGING"
    controls = "F feed  P play  S sleep"
    if queued:
        controls += f"   queued: {queued}"
    detail = (
        f"stress {needs['stress']['value']:.2f}   "
        f"bond {needs['bond']['value']:.2f}"
        if "stress" in needs and "bond" in needs
        else ""
    )
    return [line, controls, detail]


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    import pygame  # the window layer's dependency, paid only here

    seed, slip = args.seed, args.slip
    if seed is None or slip is None:
        default_seed, default_slip = default_fixture_paths()
        seed = seed or default_seed
        slip = slip or default_slip
    grid, slip_profile, model = load_session_inputs(seed, slip)
    session = CompanionSession(grid, slip_profile, model=model)
    keeper_dir = args.keeper_dir or default_keeper_dir()
    lineage_path = keeper_dir / LINEAGE_FILENAME

    width, height = session.grid["grid_size"]
    panel_px = height * args.scale
    hud_px = HUD_HEIGHT * args.scale
    window_size = (width * args.scale, panel_px + hud_px + FOOTER_PX)

    key_actions = {
        pygame.K_f: "feed",
        pygame.K_p: "play",
        pygame.K_s: "sleep",
    }

    pygame.init()
    try:
        window = pygame.display.set_mode(window_size)
        pygame.display.set_caption(f"{WINDOW_TITLE} — {session.name}")
        font = pygame.font.Font(None, 22)
        clock = pygame.time.Clock()
        # Live clip driving through the C2 graph (F3): the driver walks
        # frame by frame toward the state's desired clip.
        clip_vocabulary = {clip for edge in TRANSITIONS for clip in edge}
        driver = ClipDriver(
            {clip: clip_frame_count(clip) for clip in clip_vocabulary}
        )
        ghost = None
        frame = 0
        queued: str | None = None
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in key_actions and session.alive:
                        queued = key_actions[event.key]
                    elif (
                        event.key == pygame.K_RETURN
                        and not session.alive
                    ):
                        session.save_lineage(lineage_path)
                        session.succeed()
                        ghost = None
                        driver = ClipDriver(driver.frame_counts)

            if session.alive and frame % args.tick_frames == 0:
                session.advance(player_action=queued)
                queued = None
                if not session.alive:
                    session.save_lineage(lineage_path)
                    if args.auto_succeed:
                        session.succeed()
                        ghost = None
                        driver = ClipDriver(driver.frame_counts)
                    elif args.ticks is not None:
                        # A bounded, unattended run ends at death.
                        running = False
                if session.session_tick == args.ticks:
                    running = False

            clip, frame_index = driver.step(session.desired_clip())
            packet = session.packet_for(clip, frame_index)
            composed = compose_frame(
                packet, previous_ghost=ghost, cell_px=args.scale
            )
            ghost = composed.ghost
            snapshot = session.snapshot()
            hud = render_hud(
                session.state,
                snapshot["ui_hints"],
                width=width,
                palette=packet["palette"],
                frame=frame,
            )
            hud_scaled = apply_scanline(
                scale_buffer(hud, args.scale),
                period=2,
                opacity=0.12,
            )
            lcd = stack_buffers(composed.pixels, hud_scaled)
            surface = pygame.image.frombytes(
                _frame_bytes(lcd),
                (width * args.scale, panel_px + hud_px),
                "RGB",
            )
            window.fill((16, 18, 16))
            window.blit(surface, (0, 0))
            for index, line in enumerate(
                _footer_lines(snapshot, queued)
            ):
                if line:
                    window.blit(
                        font.render(line, True, (200, 230, 200)),
                        (8, panel_px + hud_px + 6 + index * 22),
                    )
            pygame.display.flip()
            frame += 1
            clock.tick(args.fps)
        session.save_lineage(lineage_path)
        return 0
    finally:
        pygame.quit()
