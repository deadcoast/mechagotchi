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
import json
from pathlib import Path

from mecha_engine.generation import train_generation_model
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
from mecha_game.contribute import founders_verdict, gather_releases
from mecha_game.covenant_io import export_covenant, import_covenant
from mecha_game.packs import import_pack
from mecha_game.hatchery import hatch_founders, origin_summary
from mecha_game.lineage import LineageBrowser
from mecha_game.repertoire import RepertoireBrowser
from mecha_game.replay import ReplayPlayer, overlay_wounds
from mecha_game.covenant import (
    spend_deliberation_to_budget,
    spend_generations_to_cap,
    spend_next_palette,
    spend_population_to_cap,
)
from mecha_game.hud import HUD_HEIGHT, render_hud
from mecha_game.packets import default_fixture_paths
from mecha_game.rasterize import (
    Buffer,
    apply_scanline,
    compose_frame,
    rasterize_cells,
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

    def __init__(
        self,
        era_scale: str,
        cache_dir: Path | None = None,
        state_path: Path | None = None,
        ledger_path: Path | None = None,
    ) -> None:
        self.era_scale = era_scale
        self.cache_dir = cache_dir
        self.state_path = state_path
        self.ledger_path = ledger_path
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
                # F11: the slow trainer caches to the keeper dir —
                # byte-equal to fresh training, pinned by test.
                cache_dir=self.cache_dir,
            )
            # F17: resume the campaign exactly where it stopped (the
            # spent covenant included; founders from the ledger).
            if (
                self.state_path is not None
                and self.state_path.is_file()
                and self.ledger_path is not None
                and self.ledger_path.is_file()
            ):
                self.campaign = KeeperCampaign.load_state(
                    inputs, self.state_path, self.ledger_path
                )
                self.message = (
                    f"campaign resumed at era "
                    f"{self.campaign.era_offset}"
                )
            else:
                self.campaign = KeeperCampaign(
                    inputs,
                    era_config=TINY_ERA_CONFIG if tiny else ERA_CONFIG,
                )
        return self.campaign

    def budget_lines(self) -> list[str]:
        """The covenant mode's display — every number the campaign's
        own budget/covenant, verbatim (F7)."""
        campaign = self.ensure()
        budget = campaign.budget()
        profile = campaign.campaign["slip_profile"]
        active_palettes = profile["grid"]["allowed_palettes"]
        thinking = profile.get("deliberation", {}).get("max_ticks", 0)
        return [
            (
                f"COVENANT   palettes {len(active_palettes)}/"
                f"{len(budget['allowed_palettes'])}   thinking "
                f"{thinking}/{budget['deliberation_max_ticks']}   pop "
                f"{campaign.era_config['population']}/"
                f"{budget['population_cap']}   gens "
                f"{campaign.era_config['generations']}/"
                f"{budget['generation_cap']}"
            ),
            "1 palette  2 thinking  3 population  4 generations  C close",
        ]

    def spend(self, key_index: int) -> None:
        campaign = self.ensure()
        spends = {
            0: spend_next_palette,
            1: spend_deliberation_to_budget,
            2: spend_population_to_cap,
            3: spend_generations_to_cap,
        }
        result = spends[key_index](campaign)
        self.message = (
            "covenant updated"
            if result["ok"]
            else "; ".join(result["violations"])
        )

    def active_covenant(self) -> dict:
        return self.ensure().campaign["slip_profile"]

    def hatch(self, rng_seed: int) -> dict:
        """One founder generated under the ACTIVE covenant, its origin
        trace riding along (F8)."""
        campaign = self.ensure()
        return hatch_founders(
            campaign.inputs["seed_grids"],
            self.active_covenant(),
            count=1,
            rng_seed=rng_seed,
        )[0]

    def run_era(
        self, ledger_path: Path, released_grids: list[dict] | None = None
    ) -> dict:
        campaign = self.ensure()
        if campaign.status != "active":
            campaign = self.campaign = campaign.successor()
            self.message = "bloodline extinct — successor founded; "
        era = campaign.advance_era(
            self.weather, released_grids=released_grids
        )
        campaign.save(ledger_path)
        if self.state_path is not None:
            campaign.save_state(self.state_path)
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
        # The engine's own admission verdict, shown never smoothed (F9).
        verdict = founders_verdict(era)
        if verdict is not None:
            self.message += (
                f"   founders: {len(verdict['admitted_ids'])} admitted"
                f", {len(verdict['rejected'])} rejected"
            )
            if verdict["rejected"]:
                first = verdict["rejected"][0]
                self.message += (
                    f" ({first['grid_id']}: {first['errors'][0]})"
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
    campaign_ledger = keeper_dir / "campaign.sqlite3"
    bench = _EraBench(
        args.era_scale,
        cache_dir=keeper_dir / "model_cache",
        state_path=keeper_dir / "campaign_state.json",
        ledger_path=campaign_ledger,
    )
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
        covenant_mode = False
        pending_releases: list[dict] = []
        hatch_count = 0
        review: ReplayPlayer | None = None
        review_playing = False
        browser: RepertoireBrowser | None = None
        story: LineageBrowser | None = None
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
                        bench.run_era(
                            campaign_ledger,
                            released_grids=pending_releases or None,
                        )
                        pending_releases = []
                    elif event.key == pygame.K_h:
                        # Hatch a founder under the ACTIVE covenant
                        # and adopt it; its origin is the engine's own
                        # generation trace (F8).
                        hatch_count += 1
                        hatched = bench.hatch(20260713 + hatch_count)
                        session.save_lineage(lineage_path)
                        session = CompanionSession(
                            hatched["grid"],
                            bench.active_covenant(),
                            model=train_generation_model(
                                [hatched["grid"]]
                            ),
                            name=hatched["grid"]["grid_id"],
                            origin="hatched",
                        )
                        ghost = None
                        driver = ClipDriver(driver.frame_counts)
                        bench.message = "hatched: " + origin_summary(
                            hatched["explanation"]
                        )
                    elif event.key == pygame.K_v:
                        # The Review step (F10): the last era's best
                        # elite lives one RECORDED life — replayed at
                        # the era's own seed; V again returns to the
                        # companion (whose time stands still while
                        # the Keeper reviews).
                        if review is not None:
                            review = None
                        elif bench.campaign and bench.campaign.eras:
                            try:
                                campaign = bench.ensure()
                                era_idx = campaign.eras[-1][
                                    "era_index"
                                ]
                                # F17: a persisted review loads back
                                # (hash-verified); otherwise record it
                                # and persist the pointer.
                                replay = campaign.load_review_replay(
                                    keeper_dir,
                                    campaign_ledger,
                                    era_idx,
                                )
                                if replay is None:
                                    replay = (
                                        campaign.record_review_replay()
                                    )
                                    campaign.save_review_replay(
                                        replay,
                                        keeper_dir,
                                        campaign_ledger,
                                    )
                                review = ReplayPlayer(replay)
                                review_playing = True
                            except ValueError as error:
                                bench.message = str(error)
                        else:
                            bench.message = "no era to review yet (E)"
                    elif review is not None and event.key == pygame.K_SPACE:
                        review_playing = not review_playing
                    elif review is not None and event.key == pygame.K_PERIOD:
                        review_playing = False
                        review.step()
                    elif review is not None and event.key == pygame.K_COMMA:
                        review_playing = False
                        review.back()
                    elif event.key == pygame.K_l:
                        # The lineage browser (F14): the Keeper's
                        # whole story, life by life.
                        story = (
                            None
                            if story is not None
                            else LineageBrowser(session.lineage)
                        )
                    elif story is not None and event.key == pygame.K_PERIOD:
                        story.step()
                    elif story is not None and event.key == pygame.K_COMMA:
                        story.back()
                    elif event.key == pygame.K_b:
                        # The repertoire browser (F13): species memory
                        # made visible, era by era, niche by niche.
                        if browser is not None:
                            browser = None
                        elif bench.campaign and bench.campaign.eras:
                            browser = RepertoireBrowser(bench.campaign)
                        else:
                            bench.message = "no era to browse yet (E)"
                    elif browser is not None and event.key == pygame.K_PERIOD:
                        browser.step()
                    elif browser is not None and event.key == pygame.K_COMMA:
                        browser.back()
                    elif (
                        browser is not None
                        and event.key == pygame.K_LEFTBRACKET
                    ):
                        browser.previous_era()
                    elif (
                        browser is not None
                        and event.key == pygame.K_RIGHTBRACKET
                    ):
                        browser.next_era()
                    elif event.key == pygame.K_k:
                        # Import a community pack (F16): the format's
                        # contents judged item by item and staged into
                        # the inboxes; verdicts shown. (K — P is the
                        # companion's play action.)
                        pack_path = (
                            keeper_dir / "packs" / "pack_import.json"
                        )
                        if not pack_path.is_file():
                            bench.message = (
                                "place a pack at keeper/packs/"
                                "pack_import.json to import"
                            )
                            continue
                        report = import_pack(keeper_dir, pack_path)
                        if not report["ok"]:
                            bench.message = "; ".join(
                                report["violations"]
                            )
                        else:
                            ok_slips = sum(
                                1 for s in report["slips"] if s["ok"]
                            )
                            ok_creatures = sum(
                                1
                                for c in report["creatures"]
                                if c["ok"]
                            )
                            bench.message = (
                                f"pack {report['pack_id']}: "
                                f"{ok_slips}/{len(report['slips'])} "
                                f"covenants and {ok_creatures}/"
                                f"{len(report['creatures'])} creatures "
                                "staged (I imports a covenant; W "
                                "gathers the creatures)"
                            )
                    elif event.key == pygame.K_x:
                        # Export the ACTIVE covenant (spends included)
                        # as a shareable SLIP file (F15).
                        exported = export_covenant(
                            bench.ensure(),
                            keeper_dir
                            / "covenants"
                            / "covenant_export.json",
                        )
                        bench.message = f"covenant exported: {exported.name}"
                    elif event.key == pygame.K_i:
                        # Import a covenant through the engine's gates
                        # (F15): keeper/covenants/covenant_import.json.
                        import_path = (
                            keeper_dir
                            / "covenants"
                            / "covenant_import.json"
                        )
                        if not import_path.is_file():
                            bench.message = (
                                f"place a SLIP at {import_path.name} "
                                "under keeper/covenants/ to import"
                            )
                        else:
                            result = import_covenant(
                                bench.ensure(), import_path
                            )
                            bench.message = (
                                "covenant imported "
                                f"({result['aligned_seeds']} seeds "
                                "satisfy it) — the new species contract"
                                if result["ok"]
                                else "; ".join(result["violations"])
                            )
                    elif event.key == pygame.K_w:
                        # Gather the workshop's and the Keeper's
                        # released creatures for the next era; the
                        # engine's gates judge them there (F9).
                        releases = gather_releases(keeper_dir)
                        pending_releases.extend(releases)
                        bench.message = (
                            f"gathered {len(releases)} released "
                            f"creatures ({len(pending_releases)} "
                            "pending for the next era)"
                        )
                    elif event.key == pygame.K_r:
                        # Release the companion's genome as a founder
                        # for the next era (the engine's own admission
                        # gates judge it there).
                        pending_releases.append(
                            json.loads(json.dumps(session.grid))
                        )
                        bench.message = (
                            f"released {session.grid['grid_id']} to "
                            f"the next era ({len(pending_releases)} "
                            "pending)"
                        )
                    elif event.key == pygame.K_c:
                        covenant_mode = not covenant_mode
                    elif covenant_mode and event.key in (
                        pygame.K_1,
                        pygame.K_2,
                        pygame.K_3,
                        pygame.K_4,
                    ):
                        bench.spend(event.key - pygame.K_1)
                    elif event.key in (
                        pygame.K_1,
                        pygame.K_2,
                        pygame.K_3,
                        pygame.K_4,
                        pygame.K_5,
                    ):
                        # 4 = "real" (G4): the G2-ingested REAL CuBFF
                        # snapshots as this era's weather. 5 =
                        # "callback" (K4, DR 0043): the I3 records
                        # with the replication channel LIT.
                        bench.weather_index = (
                            event.key - pygame.K_1
                        ) % len(WEATHER_NAMES)
                    elif event.key == pygame.K_a and bench.campaign:
                        # A adopts: the browsed elite when the
                        # repertoire is open, else the era's best.
                        elite = (
                            json.loads(
                                json.dumps(browser.current()["grid"])
                            )
                            if browser is not None
                            else bench.campaign.best_elite_grid()
                        )
                        if elite is not None:
                            # The era's best elite becomes the Keeper's
                            # companion — through the same engine gate,
                            # under the campaign's ACTIVE covenant (a
                            # spent deliberation budget makes it THINK).
                            session.save_lineage(lineage_path)
                            session = CompanionSession(
                                elite,
                                bench.campaign.campaign["slip_profile"],
                                model=session.model,
                                name=elite["grid_id"],
                                origin="era_elite",
                            )
                            ghost = None
                            driver = ClipDriver(driver.frame_counts)
                            bench.message += "   adopted!"

            if (
                review is None
                and browser is None
                and session.alive
                and frame % args.tick_frames == 0
            ):
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

            if browser is not None:
                # The repertoire window: the elite's real packet under
                # the campaign's covenant, statically composed.
                composed = compose_frame(
                    browser.packet(),
                    previous_ghost=None,
                    cell_px=args.scale,
                )
                blank_hud = tuple(
                    tuple(
                        (16, 18, 16) for _ in range(width * args.scale)
                    )
                    for _ in range(HUD_HEIGHT * args.scale)
                )
                lcd = stack_buffers(composed.pixels, blank_hud)
                snapshot = session.snapshot()
            elif review is not None:
                # The Review window: recorded body states, raw and
                # honestly effect-free (v1 packets declare none); the
                # wound frames wear the damage event's own cells.
                if review_playing and frame % 2 == 0:
                    review.step()
                body = review.body_packet()
                raster = (
                    rasterize_cells(body)
                    if body is not None
                    else tuple(
                        tuple((0, 0, 0) for _ in range(width))
                        for _ in range(height)
                    )
                )
                wounds = review.wound_cells()
                if wounds:
                    raster = overlay_wounds(raster, wounds)
                panel = scale_buffer(raster, args.scale)
                blank_hud = tuple(
                    tuple((16, 18, 16) for _ in range(width * args.scale))
                    for _ in range(HUD_HEIGHT * args.scale)
                )
                lcd = stack_buffers(panel, blank_hud)
                snapshot = session.snapshot()
            else:
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
            if story is not None:
                footer = [
                    "LINEAGE  " + story.caption(),
                    *story.detail_lines(),
                    ". older→newer  , newer→older  L close",
                ]
            elif browser is not None:
                footer = [
                    "REPERTOIRE  " + browser.caption(),
                    browser.axes_line(),
                    browser.components_line(),
                    ". next  , prev  [ ] era  A adopt this one  B close",
                ]
            elif review is not None:
                footer = [
                    f"REVIEW  {review.replay['creature']['grid_id']}",
                    review.caption(),
                    "SPACE play/pause  . step  , back  V close",
                    review.replay.get("honest_label", ""),
                ]
            elif covenant_mode:
                footer.extend(bench.budget_lines())
            else:
                footer.append(
                    f"E: run era [{bench.weather}]  1-5: weather "
                    "(4=REAL 5=CALLBACK)  C: covenant  H: hatch  "
                    "R: release  W: workshop  V: review  B: "
                    "repertoire  L: lineage  X/I: covenant io  K: pack"
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
