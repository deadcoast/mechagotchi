"""The Mechagotchi window — F1's launchable hello-creature client.

A fixed-timestep pygame-ce loop presenting composed engine frames
(DR 0033). Pygame touches ONLY this layer: the packet source and the
compositor are pure, so everything the window shows is reproducible
headless byte for byte. Close the window or press ESC to quit;
``--ticks`` bounds the run for verification and evidence harnesses.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from mecha_game.packets import (
    default_fixture_paths,
    hello_packet,
    load_hello_creature,
)
from mecha_game.rasterize import Buffer, compose_frame

WINDOW_TITLE = "Mechagotchi"
DEFAULT_CELL_PX = 24
DEFAULT_FPS = 8  # the LCD heartbeat


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mechagotchi",
        description=(
            "Mechagotchi — a living grid creature, rendered from the "
            "engine's own packets (hello-creature skeleton, MVP 0.1 F1)"
        ),
    )
    parser.add_argument(
        "--seed",
        type=Path,
        default=None,
        help="grid genome JSON (default: the 16x16 corpus beetle)",
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
        help=f"ticks per second (default {DEFAULT_FPS})",
    )
    parser.add_argument(
        "--ticks",
        type=int,
        default=None,
        help="quit after N ticks (verification runs; default: play on)",
    )
    return parser


def _frame_bytes(pixels: Buffer) -> bytes:
    return b"".join(bytes(rgb) for row in pixels for rgb in row)


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    import pygame  # the window layer's dependency, paid only here

    seed, slip = args.seed, args.slip
    if seed is None or slip is None:
        default_seed, default_slip = default_fixture_paths()
        seed = seed or default_seed
        slip = slip or default_slip
    creature = load_hello_creature(seed, slip)
    width, height = creature.grid["grid_size"]

    pygame.init()
    try:
        window = pygame.display.set_mode(
            (width * args.scale, height * args.scale)
        )
        pygame.display.set_caption(
            f"{WINDOW_TITLE} — {creature.grid['grid_id']}"
        )
        clock = pygame.time.Clock()
        ghost = None
        tick = 0
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    running = False
            packet = hello_packet(creature, tick)
            composed = compose_frame(
                packet, previous_ghost=ghost, cell_px=args.scale
            )
            ghost = composed.ghost
            frame = pygame.image.frombytes(
                _frame_bytes(composed.pixels),
                (width * args.scale, height * args.scale),
                "RGB",
            )
            window.blit(frame, (0, 0))
            pygame.display.flip()
            tick += 1
            if args.ticks is not None and tick >= args.ticks:
                running = False
            clock.tick(args.fps)
        return 0
    finally:
        pygame.quit()
