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

from mecha_game.campaign import (
    ERA_CONFIG,
    TINY_ERA_CONFIG,
    WEATHER_NAMES,
    KeeperCampaign,
    default_campaign_paths,
    load_campaign_inputs,
)
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
FOOTER_PX = 140  # the casing's text area (chrome, not LCD)
LINEAGE_FILENAME = "lineage.json"
COMPANION_FILENAME = "companion.json"


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
    parser.add_argument(
        "--eras",
        type=int,
        default=None,
        help="run N eras headless then quit (verification runs)",
    )
    parser.add_argument(
        "--era-scale",
        choices=["session", "tiny"],
        default="session",
        help="era configuration (tiny is for verification runs)",
    )
    parser.add_argument(
        "--new",
        action="store_true",
        help="start a fresh companion (default: resume the save file)",
    )
    return parser


def _frame_bytes(pixels: Buffer) -> bytes:
    return b"".join(bytes(rgb) for row in pixels for rgb in row)


class _EraBench:
    """The Keeper's evolution bench, lazily trained on first use
    (model training costs seconds — never paid by pure companion play)."""

    def __init__(self, era_scale: str) -> None:
        self.era_scale = era_scale
        self.campaign: KeeperCampaign | None = None
        self.weather_index = 0
        self.message = ""

    @property
    def weather(self) -> str:
        return WEATHER_NAMES[self.weather_index]

    def ensure(self) -> KeeperCampaign:
        if self.campaign is None:
            paths = default_campaign_paths()
            tiny = self.era_scale == "tiny"
            inputs = load_campaign_inputs(
                paths["seed_dir"],
                paths["slip_path"],
                paths["adopted_model_path"],
                repair_epochs=6 if tiny else 40,
                seed_limit=12 if tiny else None,
            )
            self.campaign = KeeperCampaign(
                inputs,
                era_config=TINY_ERA_CONFIG if tiny else ERA_CONFIG,
            )
        return self.campaign

    def run_era(self, ledger_path: Path) -> dict:
        campaign = self.ensure()
        if campaign.status != "active":
            campaign = self.campaign = campaign.successor()
            self.message = "bloodline extinct — successor founded; "
        era = campaign.advance_era(self.weather)
        campaign.save(ledger_path)
        memory = campaign.species_memory()
        last = memory["last_era"]
        self.message = (
            f"era {last['era_index']} [{last['weather']}]: "
            f"niches {last['filled_niches']}  qd {last['qd_score']:.1f}  "
            f"elites {last['elite_count']}  "
            f"unlocks {len(memory['unlocks'])}"
            + ("  EXTINCT" if last["went_extinct"] else "")
            + "   A: adopt best elite"
        )
        return era


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
    # The kept fleet's read model, verbatim thread outputs (F3b):
    # the HMM's felt mood with entropy-honest confidence, and the
    # hunger forecast — "begs soon" exactly when the thread's own
    # anticipatory feed effect fires (never a client threshold).
    threads = snapshot.get("threads") or {}
    felt = ""
    hmm = threads.get("hidden_mood_hmm")
    if hmm and hmm["output"].get("map_mood"):
        felt = (
            f"felt {hmm['output']['map_mood']} "
            f"({hmm['confidence']:.2f})"
        )
    forecast = threads.get("hunger_forecast")
    if forecast and forecast["output"].get("predicted_hunger") is not None:
        felt += (
            f"   hunger→{forecast['output']['predicted_hunger']:.2f}"
        )
        if forecast["effects"].get("feed"):
            felt += "   begs soon"
    return [line, controls, detail, felt]


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    import pygame  # the window layer's dependency, paid only here

    seed, slip = args.seed, args.slip
    if seed is None or slip is None:
        default_seed, default_slip = default_fixture_paths()
        seed = seed or default_seed
        slip = slip or default_slip
    keeper_dir = args.keeper_dir or default_keeper_dir()
    lineage_path = keeper_dir / LINEAGE_FILENAME
    companion_path = keeper_dir / COMPANION_FILENAME
    bench = _EraBench(args.era_scale)
    campaign_ledger = keeper_dir / "campaign.sqlite3"
    # Quit and come back (F5): the save file resumes unless --new.
    if companion_path.is_file() and not args.new:
        session = CompanionSession.load(companion_path)
    else:
        grid, slip_profile, model = load_session_inputs(seed, slip)
        session = CompanionSession(grid, slip_profile, model=model)

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
        ticks_run = 0  # THIS run's ticks (a resumed session's
        # session_tick continues across launches)
        queued: str | None = None
        displayed_clip: str | None = None
        running = True
        # Headless verification: run the requested eras up front.
        if args.eras is not None:
            for _ in range(args.eras):
                bench.run_era(campaign_ledger)
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
                    elif event.key == pygame.K_e:
                        bench.run_era(campaign_ledger)
                    elif event.key in (
                        pygame.K_1,
                        pygame.K_2,
                        pygame.K_3,
                    ):
                        bench.weather_index = (
                            event.key - pygame.K_1
                        ) % len(WEATHER_NAMES)
                    elif event.key == pygame.K_a and bench.campaign:
                        elite = bench.campaign.best_elite_grid()
                        if elite is not None:
                            # The era's best elite becomes the Keeper's
                            # companion — through the same engine gate.
                            session.save_lineage(lineage_path)
                            session = CompanionSession(
                                elite,
                                session.slip_profile,
                                model=session.model,
                                name=elite["grid_id"],
                            )
                            ghost = None
                            driver = ClipDriver(driver.frame_counts)
                            bench.message += "   adopted!"

            if session.alive and frame % args.tick_frames == 0:
                # The bandit's reward attribution sees what the window
                # actually showed last (the driver's emitted clip).
                session.advance(
                    player_action=queued, displayed_clip=displayed_clip
                )
                ticks_run += 1
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
                if ticks_run == args.ticks:
                    running = False

            clip, frame_index = driver.step(session.desired_clip())
            displayed_clip = clip
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
            footer = _footer_lines(snapshot, queued)
            footer.append(
                f"E: run era [{bench.weather}]  1/2/3: weather"
            )
            if bench.message:
                footer.append(bench.message)
            for index, line in enumerate(footer):
                if line:
                    window.blit(
                        font.render(line, True, (200, 230, 200)),
                        (8, panel_px + hud_px + 6 + index * 22),
                    )
            pygame.display.flip()
            frame += 1
            clock.tick(args.fps)
        session.save_lineage(lineage_path)
        session.save(companion_path)
        return 0
    finally:
        pygame.quit()
