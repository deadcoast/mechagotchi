"""The Mechagotchi window — the playable companion loop (F2, MVP 0.1).

A fixed-timestep pygame-ce loop over one `CompanionSession`: the LCD
panel (the composed engine frame) above the HUD strip (engine-truth
bars and ui_hints icons), with a text footer for mood/age/lineage —
every displayed number a state field, a packet field, or a lineage
record (DR 0021 first law). Pygame touches ONLY this layer.

Controls: F feed · P play · S sleep · G clean (when the covenant opts in;
queued for the next lifecycle
tick — the keeper answers the tick, mashing keys does not accelerate
time) · ENTER adopt the successor when the companion dies · ESC or
close to quit. Ctrl+S checkpoints now; save failures pause care for retry.
Companion checkpoints embed lineage; the standalone export is derived.
"""

from __future__ import annotations

import argparse
import copy
import sqlite3
import json
import sys
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
from mecha_game.inbox import InboxPicker
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
from mecha_game.footer import FooterPager, HELP_LINES
from mecha_game.era_review import EraReview
from mecha_game.niche_history import CampaignStory, NicheHistory
from mecha_game.era_plan import EraPlan, state_digest
from mecha_game.era_work import EraCancelled, EraWork
from mecha_game.recorded_review import fit_recorded_panel, load_saved_replay
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
from mecha_game.session import CompanionSession, LEARNING_POLICIES, load_session_inputs

WINDOW_TITLE = "Mechagotchi"
DEFAULT_CELL_PX = 24
DEFAULT_FPS = 8  # the LCD heartbeat (render frames)
DEFAULT_TICK_FRAMES = 12  # lifecycle tick every N frames (1.5 s at 8 fps)
FOOTER_PX = 184  # eight 22px rows plus margins: needs, covenant and notice
LINEAGE_FILENAME = "lineage.json"
COMPANION_FILENAME = "companion.json"


def default_keeper_dir(start: Path | None = None) -> Path:
    """The save home: `keeper/` at the repo root in a dev checkout
    (gitignored — a live pet is not evidence), else the user's own
    `~/.mechagotchi`. Frozen bundles retain an existing legacy save in
    `_internal/keeper` only when the user home has no existing save."""
    if getattr(sys, "frozen", False):
        home = Path.home() / ".mechagotchi"
        bundle = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent / "_internal"))
        legacy = bundle / "keeper"
        saved_names = (COMPANION_FILENAME, "companion.bak.json", LINEAGE_FILENAME,
                       "lineage.bak.json", "campaign_state.json", "campaign.sqlite3")
        has_home = any((home / name).is_file() for name in saved_names)
        has_legacy = any((legacy / name).is_file() for name in saved_names)
        # Continue older bundled companions in place. Never silently copy,
        # migrate, or overwrite a second save when both homes contain lives.
        return legacy if has_legacy and not has_home else home
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
        help="covenant for a new companion (default: LCD with cleanliness; existing saves resume their own covenant)",
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
    parser.add_argument(
        "--learning-policy", choices=LEARNING_POLICIES, default=None,
        help="new companion policy: incumbent (default) or experimental qtable; resumes preserve their saved policy",
    )
    parser.add_argument("--recover-backup", action="store_true",
                        help="restore the previous companion save; validate it and archive the current save first")
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
        initial_profile: dict | None = None,
    ) -> None:
        self.era_scale = era_scale
        self.cache_dir = cache_dir
        self.state_path = state_path
        self.ledger_path = ledger_path
        self.initial_profile = json.loads(json.dumps(initial_profile)) if initial_profile is not None else None
        self.campaign: KeeperCampaign | None = None
        self.plan = EraPlan(state_path.with_name('era_plan.json') if state_path is not None else None)
        self.weather_index = WEATHER_NAMES.index(self.plan.weather)
        self._loaded_state_digest = state_digest(state_path)
        self._completed_work = None
        self._completed_previous_state = None
        self.message = self.plan.error or ""

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
                # Q3: a new bloodline starts under the companion's covenant.
                # A recorded campaign above remains its own authority.
                if self.initial_profile is not None:
                    inputs = dict(inputs, slip_profile=json.loads(json.dumps(self.initial_profile)))
                self.campaign = KeeperCampaign(
                    inputs,
                    era_config=TINY_ERA_CONFIG if tiny else ERA_CONFIG,
                )
            self._loaded_state_digest = state_digest(self.state_path)
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
            "I choose covenant   K choose pack   X export",
        ]

    def require_preparation(self):
        self.plan.require_ready()
        if self._completed_work is not None:
            raise ValueError('E finishes saving the completed era before another preparation change.')

    def preparation_line(self):
        if self.plan.error: return self.plan.error
        if self.plan.pending is not None or self._completed_work is not None:
            return 'ERA RESULT awaiting save. E retry; no new era runs.'
        return f'NEXT ERA [{self.weather}]: {len(self.plan.releases)} staged'

    def preparation_controls(self):
        if self.plan.error:
            return 'Preparation unavailable; care and recorded history remain available.'
        if self.plan.pending is not None or self._completed_work is not None:
            return 'E retry save   T report   F1 help'
        return '1-5 weather   R stage current pet   W gather   Backspace unstage'

    def choose_weather(self, index):
        self.require_preparation()
        self.plan.select_weather(WEATHER_NAMES[index])
        self.weather_index = index
        self.message = f'Next era weather saved: {self.weather}.'

    def stage_releases(self, grids):
        self.require_preparation()
        added = self.plan.stage(grids)
        self.message = f'Staged {added}; {len(self.plan.releases)} ready for the next era. Your companion stays with you.'

    def check_current_state(self):
        if state_digest(self.state_path) != self._loaded_state_digest:
            raise ValueError('Campaign state changed outside this session; existing state preserved.')

    def unstage(self):
        self.require_preparation()
        self.plan.unstage_all()
        self.message = 'Contributions unstaged. Source creatures and your companion are unchanged.'

    def change_covenant(self, operation):
        self.require_preparation()
        current = self.ensure()
        self.check_current_state()
        candidate = copy.deepcopy(current)
        result = operation(candidate)
        if result['ok']:
            if self.state_path is not None:
                candidate.save(self.ledger_path)
                candidate.save_state(self.state_path)
                self._loaded_state_digest = state_digest(self.state_path)
            self.campaign = candidate
        return result

    def spend(self, key_index: int) -> None:
        spends = {0:spend_next_palette,1:spend_deliberation_to_budget,
                  2:spend_population_to_cap,3:spend_generations_to_cap}
        result = self.change_covenant(spends[key_index])
        self.message = 'Covenant saved.' if result['ok'] else '; '.join(result['violations'])

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
        self, ledger_path: Path, released_grids: list[dict] | None = None, *, work=None
    ) -> dict:
        self.plan.require_ready(allow_pending=True)
        if self.plan.pending is not None:
            if work is not None: work.begin_commit()
            era = self.plan.finish(ledger_path,self.state_path)
            # A recovered persisted era is history, not a new current-run era.
            self.campaign = None
            self._loaded_state_digest = state_digest(self.state_path)
            self._completed_work = None
            self.message = f"Era {era['era_index']} saved. No additional era ran."
            return era
        if self._completed_work is None:
            if work is not None: work.phase("Loading models")
            current = self.ensure()
            self.check_current_state()
            campaign = copy.deepcopy(current)
            if campaign.status != 'active': campaign = campaign.successor()
            previous_state = state_digest(self.state_path)
            era = campaign.advance_era(self.weather,released_grids=(
                released_grids if released_grids is not None else self.plan.releases) or None,
                record_original=True,
                **({"progress_callback": work.progress} if work is not None else {}))
            if work is not None: work.begin_commit()
            self._completed_work = campaign
            self._completed_previous_state = previous_state
        if work is not None: work.begin_commit()
        campaign = self._completed_work
        era = campaign.eras[-1]
        self.plan.begin(campaign,era,self._completed_previous_state)
        self.plan.finish(ledger_path,self.state_path)
        self.campaign = campaign
        self._loaded_state_digest = state_digest(self.state_path)
        self._completed_work = None
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
            ("Policy: experimental Q-table" if snapshot.get("learning_policy") == "qtable"
             else "Policy: incumbent"),
        ]
    needs = snapshot["needs"]
    # O2 (DR 0054): health is the CHOSEN `danger_margin` definition, and
    # it is shown WITH the axis binding it. The keeper's `play` verb
    # lowers the number (play costs energy), so a bare figure would read
    # as a bug; "health 0.62 (tired)" reads as a sentence instead. The
    # word is the state the axis is in, never a friendlier name for it.
    health = snapshot.get("health")
    health_text = (
        f"health {health['value']:.2f} ({health['binding_word']})   "
        if health
        else ""
    )
    line = (
        f"{health_text}mood {snapshot['mood']}   age {snapshot['age_ticks']}   "
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
    lines = [line, controls, detail, felt]
    if snapshot.get("learning_policy", "incumbent") == "incumbent":
        lines.append("Policy: incumbent")
    if "cleanliness" in needs and "clean" in snapshot.get("actions", []):
        lines.append(f"cleanliness {needs['cleanliness']['value']:.2f}   G clean")
    if snapshot.get("learning_policy") == "qtable":
        policy_line = "Experimental Q-table"
        signal = threads.get("qtable_policy")
        if not snapshot.get("learning_active"):
            policy_line += ": inactive (fleet off)"
        elif not signal or signal["output"].get("cold_start", True):
            policy_line += ": learning from care"
        else:
            policy_line += f": recommends {signal['output']['best_action']} (confidence {signal['confidence']:.2f})"
        lines.append(policy_line)
        last = (snapshot.get("log") or [{}])[-1]
        consumer = (last.get("thought") or {}).get("qtable_consumer")
        if consumer:
            lines.append(f"Last followed {consumer['recommended']}; additive suggested {consumer['base_action']}. Only you feed.")
    return lines


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.recover_backup and (args.new or args.slip is not None or args.seed is not None):
        parser.error("--recover-backup cannot be combined with --new, --slip or --seed")
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
    if args.slip is not None and companion_path.is_file() and not args.new:
        parser.error("--slip selects a new companion; use --new or a separate --keeper-dir to preserve the existing save")
    recovery_notice = None
    if companion_path.exists() and not companion_path.is_file():
        parser.error("companion save path is not a file; choose a separate --keeper-dir")
    if (not companion_path.exists() and companion_path.with_suffix(".bak.json").is_file()
            and not args.new and not args.recover_backup):
        parser.error("primary companion save is missing but a backup exists; use --recover-backup to restore it, or --new for a new life")
    # Quit and come back; backup recovery is an explicit choice, never fallback.
    if args.recover_backup:
        try:
            session, archive = CompanionSession.recover_backup(companion_path, learning_policy=args.learning_policy)
        except (ValueError, OSError) as error:
            parser.error(f"Cannot recover companion backup: {error}")
        recovery_notice = "Recovered prior save." + (f" Previous primary retained as {archive.name}." if archive else "")
    elif companion_path.is_file() and not args.new:
        try:
            session = CompanionSession.load(companion_path, learning_policy=args.learning_policy)
        except (ValueError, OSError) as error:
            parser.error(f"Cannot resume companion: {error}. Save unchanged; --recover-backup explicitly restores a valid prior save.")
    else:
        grid, slip_profile, model = load_session_inputs(seed, slip)
        session = CompanionSession(grid, slip_profile, model=model,
                                   learning_policy=args.learning_policy or "incumbent")

    bench = _EraBench(
        args.era_scale,
        cache_dir=keeper_dir / "model_cache",
        state_path=keeper_dir / "campaign_state.json",
        ledger_path=campaign_ledger,
        initial_profile=session.slip_profile,
    )

    if recovery_notice:
        bench.message = recovery_notice
        print(recovery_notice)

    if args.recover_backup or (companion_path.is_file() and not args.new):
        try:
            session.sync_lineage_export(lineage_path)
        except OSError as error:
            reason = error.strerror or str(error)
            warning = f"Companion loaded. Lineage export unavailable: {reason}."
            bench.message = (bench.message + " " + warning).strip()
            print(f"{warning}\n{error}", file=sys.stderr)

    width, height = session.grid["grid_size"]
    panel_px = height * args.scale
    hud_px = HUD_HEIGHT * args.scale
    window_size = (max(384, width * args.scale), panel_px + hud_px + FOOTER_PX)

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
        help_mode = False
        inbox: InboxPicker | None = None
        footer_pager = FooterPager()
        footer_context = None
        hatch_count = 0
        review: ReplayPlayer | None = None
        review_playing = False
        review_context: EraReview | None = None
        review_return: EraReview | None = None
        review_archive_return: RepertoireBrowser | None = None
        recording_status_cache = None
        browser: RepertoireBrowser | None = None
        story: LineageBrowser | None = None
        era_review: EraReview | None = None
        campaign_story: CampaignStory | None = None
        archive_return: EraReview | None = None
        running = True
        save_failed = False
        quit_after_retry = False

        def checkpoint(*, announce=False):
            nonlocal save_failed, queued, help_mode
            try:
                warning = session.save_checkpoint(companion_path)
            except (OSError, ValueError) as error:
                save_failed = True
                queued = None
                help_mode = False
                reason = getattr(error, "strerror", None) or str(error)
                bench.message = ("Save failed. Care paused. Ctrl+S retry; "
                                 "Ctrl+Q quit without saving. " + reason)
                print(f"{bench.message}\n{error}", file=sys.stderr)
                return False
            had_failure = save_failed
            save_failed = False
            if warning:
                bench.message = warning
                print(warning, file=sys.stderr)
            elif announce or had_failure:
                bench.message = f"Saved companion at age {session.state['age_ticks']}."
            return True

        def open_era_review(era_index=None, selected_campaign_id=None):
            nonlocal campaign_story
            nonlocal recording_status_cache
            recording_status_cache = None
            nonlocal era_review, review, browser, story, covenant_mode, queued, archive_return, review_context, review_return
            campaign_id = bench.campaign.campaign["campaign_id"] if bench.campaign else None
            try:
                campaign_story = CampaignStory.load(keeper_dir, campaign_id=campaign_id)
                era_review = (campaign_story.select(selected_campaign_id) if selected_campaign_id is not None
                              else campaign_story.current)
                if era_index is not None:
                    for index, era in enumerate(era_review.history['eras']):
                        if era['era_index'] == era_index:
                            era_review.index = index
                            break
            except (OSError, ValueError) as error:
                campaign_story = None
                era_review = EraReview(error=str(error))
            review = browser = story = archive_return = review_context = review_return = None
            covenant_mode = False
            queued = None
            footer_pager.reset()

        def open_archive():
            nonlocal recording_status_cache
            recording_status_cache = None
            nonlocal browser, era_review, archive_return, review, story, covenant_mode, queued
            entry = era_review
            campaign_id = bench.campaign.campaign["campaign_id"] if bench.campaign else None
            if entry is not None:
                campaign_id = entry.history.get('campaign_id', campaign_id)
            era_index = entry.current['era_index'] if entry is not None and entry.current is not None else None
            try:
                browser = RepertoireBrowser.load(keeper_dir, campaign_id=campaign_id, era_index=era_index)
            except (OSError, ValueError) as error:
                browser = RepertoireBrowser.unavailable(str(error))
            archive_return = entry
            era_review = review = story = None
            covenant_mode = False
            queued = None
            footer_pager.reset()

        def close_archive():
            nonlocal browser, era_review, archive_return, queued
            if isinstance(browser, NicheHistory):
                browser = browser.origin
                queued = None
                footer_pager.reset()
                return
            browser = None
            era_review = archive_return
            archive_return = None
            queued = None
            footer_pager.reset()

        def recording_status(campaign_id, selected, elite=None):
            nonlocal recording_status_cache
            if selected is None or campaign_id is None:
                return 'Not recorded: no selected era.'
            key = (campaign_id, selected['era_index'], elite.get('niche_key') if elite else None)
            if recording_status_cache is not None and recording_status_cache[0] == key:
                return recording_status_cache[1]
            try:
                saved = load_saved_replay(keeper_dir, campaign_id, selected['era_index'],
                    expected_seed=selected['rng_seed'], selected_elite=elite)
                label = ('Original best-elite evaluation recorded.' if saved and 'evaluation' in saved else
                         'Legacy post-era recording; not original footage.' if saved else
                         'Not recorded: no saved replay for this era.')
            except (OSError, ValueError) as error:
                label = f'Replay unavailable: {error}'
            recording_status_cache = (key, label)
            return label

        def open_review():
            nonlocal review, review_playing, review_context, review_return, era_review, story, covenant_mode, queued
            nonlocal browser, review_archive_return
            entry, archive_entry = era_review, browser
            context = entry
            try:
                if context is None:
                    campaign_id = (archive_entry.campaign_id if archive_entry is not None else
                        bench.campaign.campaign['campaign_id'] if bench.campaign else None)
                    context = EraReview.load(keeper_dir, campaign_id=campaign_id)
                if context.error:
                    raise ValueError(context.error)
                if archive_entry is not None:
                    selected_era = archive_entry.selected_era
                    if selected_era is None or archive_entry.current() is None:
                        raise ValueError('No selected elite; original evaluation not recorded.')
                    context.index = next(i for i, era in enumerate(context.history['eras'])
                                         if era['era_index'] == selected_era['era_index'])
                selected = context.current
                if selected is None:
                    raise ValueError('No era has been recorded yet. E runs the first era.')
                campaign_id = context.history['campaign_id']
                replay = load_saved_replay(keeper_dir, campaign_id, selected['era_index'],
                    expected_seed=selected['rng_seed'],
                    selected_elite=archive_entry.current() if archive_entry is not None else None)
                if replay is None:
                    raise ValueError('Original evaluation not recorded for this historical era; its report remains available.')
                review = ReplayPlayer(replay)
                review_playing = True
                review_context, review_return = context, entry
                review_archive_return = archive_entry
                era_review = browser = None
            except (OSError, ValueError) as error:
                if archive_entry is not None:
                    archive_entry.replay_notice = f'Replay unavailable: {error}'
                else:
                    era_review = context or EraReview(error=str(error))
                    era_review.notice = f'Replay unavailable: {error}'
            story = None
            covenant_mode = False
            queued = None
            footer_pager.reset()

        def close_review():
            nonlocal review, review_context, review_return, era_review, queued, browser, review_archive_return
            review = None
            era_review = review_return
            browser = review_archive_return
            review_context = review_return = review_archive_return = None
            queued = None
            footer_pager.reset()

        def prepare(operation):
            notice = None
            try:
                operation()
            except (OSError,ValueError,sqlite3.Error) as error:
                bench.message = f'Preparation not changed: {error}'
                notice = bench.message
            if era_review is not None:
                era_review.notice = notice
            footer_pager.reset()

        def import_selected():
            if inbox.selected is None or inbox.error or inbox.completed:
                return
            try:
                if inbox.kind == 'covenant':
                    result = bench.change_covenant(lambda campaign: import_covenant(
                        campaign, inbox.selected, expected_digest=inbox.digest))
                    inbox.result_lines = ([f"Covenant imported ({result['aligned_seeds']} seeds).",
                        'Future eras use it; your current pet is unchanged.'] if result['ok'] else
                        ['Covenant not changed.', *result['violations']])
                else:
                    result = import_pack(keeper_dir, inbox.selected, expected_digest=inbox.digest)
                    if result['ok']:
                        slips, creatures = result['slips'], result['creatures']
                        inbox.result_lines = [
                            f"Pack processed: {sum(e['ok'] for e in slips)}/{len(slips)} covenants; "
                            f"{sum(e['ok'] for e in creatures)}/{len(creatures)} creatures ready.",
                            'I choose a staged covenant; K/Escape back.']
                        for kind, entries in (('covenant', slips), ('creature', creatures)):
                            for entry in entries:
                                identity = entry.get('profile_id', entry.get('grid_id'))
                                outcome = ('already staged' if entry.get('already_staged') else 'staged') if entry['ok'] else 'refused'
                                inbox.result_lines.append(f'{kind} {identity}: {outcome}')
                                inbox.result_lines.extend(entry['violations'])
                    else:
                        inbox.result_lines = ['Pack not imported.', *result['violations']]
                inbox.completed = result['ok'] and (inbox.kind == 'covenant' or
                    all(entry['ok'] for field in ('slips', 'creatures') for entry in result[field]))
            except (OSError, ValueError, sqlite3.Error) as error:
                inbox.result_lines = [f'Import not completed: {error}', 'Fix the problem; Enter retries.']
            footer_pager.reset()

        era_ran_frame = False

        def wait_for_era(work, initial_events):
            """Keep SDL on its main thread while an explicit era owns the bench."""
            nonlocal running
            still = window.copy()
            if frame == 0:
                # E can arrive before the ordinary loop has painted once. Draw
                # the actual held state without stepping care or the clip clock.
                packet = session.packet_for(session.desired_clip(), 0)
                held = compose_frame(packet, previous_ghost=None, cell_px=args.scale)
                snapshot = session.snapshot()
                hud = render_hud(session.state, snapshot["ui_hints"], width=width,
                                 palette=packet["palette"], frame=frame)
                lcd = stack_buffers(held.pixels, apply_scanline(
                    scale_buffer(hud, args.scale), period=2, opacity=0.12))
                surface = pygame.image.frombytes(_frame_bytes(lcd),
                    (width * args.scale, panel_px + hud_px), "RGB")
                still.fill((16, 18, 16))
                still.blit(surface, ((window_size[0] - width * args.scale) // 2, 0))
            pager = FooterPager()
            busy_help = False
            close_requested = False
            waiting_clock = pygame.time.Clock()
            pending_events = iter(initial_events)
            def next_work_event():
                return next(pending_events, None) or pygame.event.poll()
            work.start()
            try:
                while True:
                    # Preserve controls already retrieved beside E, then drain SDL.
                    event = next_work_event()
                    while event.type != pygame.NOEVENT:
                        if event.type == pygame.QUIT:
                            close_requested = True
                            work.cancel()
                        elif event.type == pygame.MOUSEWHEEL:
                            pager.move(-event.y)
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_F1:
                                busy_help = not busy_help
                                pager.reset()
                            elif event.key == pygame.K_ESCAPE:
                                if busy_help:
                                    busy_help = False
                                    pager.reset()
                                else:
                                    work.cancel()
                            elif event.key == pygame.K_PAGEUP:
                                pager.move(-1)
                            elif event.key == pygame.K_PAGEDOWN:
                                pager.move(1)
                            # All care/preparation/save/repeated-E input is consumed here.
                        event = next_work_event()
                    status = work.snapshot()
                    lines = ['ERA RUNNING - care paused', status['phase']]
                    if status['budget'] is not None:
                        lines.append(f"Evaluations {status['completed']}/{status['budget']} completed")
                    if status['cancelling']:
                        lines.append('Cancel requested; finishing the current step.')
                    elif status['committing']:
                        lines.append('Saving result; please wait.')
                    else:
                        lines.append('Escape cancel   F1 help')
                    if close_requested:
                        lines.append('Closing after work stops; companion will be saved.')
                    if busy_help:
                        lines = ['ERA RUNNING - help; care paused',
                                 'F1/Escape close help; Escape outside help cancels',
                                 'Close cancels computation, waits, then quits',
                                 'Cancellation waits for model load/current candidate',
                                 'Completed-result saving cannot be cancelled',
                                 'Other commands are ignored, never queued',
                                 'Counts are completed candidates, not time estimates']
                    window.blit(still, (0, 0))
                    window.fill((16, 18, 16), (0, panel_px + hud_px, window_size[0], FOOTER_PX))
                    rows = (FOOTER_PX - 12 - font.get_height()) // 22 + 1
                    page = pager.layout(lines, lambda text: font.size(text)[0], window_size[0] - 16, rows)
                    for index, line in enumerate(page.lines):
                        if line:
                            window.blit(font.render(line, True, (200, 230, 200)),
                                        (8, panel_px + hud_px + 6 + index * 22))
                    pygame.display.flip()
                    if status['done']:
                        break
                    waiting_clock.tick(30)
            finally:
                # A render/event exception cannot leave computation alive after the app.
                work.cancel()
                work.join()
                if close_requested:
                    running = False
            return work.result()

        def run_prepared_era(initial_events=()):
            nonlocal era_ran_frame
            era_ran_frame = True
            try:
                if args.eras is not None:
                    bench.run_era(campaign_ledger)
                else:
                    wait_for_era(EraWork(lambda work: bench.run_era(campaign_ledger, work=work)), initial_events)
            except EraCancelled as error:
                bench.message = str(error)
                if era_review is not None:
                    era_review.notice = bench.message
                return False
            except (OSError,ValueError,sqlite3.Error) as error:
                bench.message = f'Era not completed: {error}. E retries; saved progress is retained.'
                if era_review is not None:
                    era_review.notice = bench.message
                return False
            if args.ticks is None and running:
                open_era_review()
            return True

        # Headless verification: run the requested eras up front.
        if args.eras is not None:
            for _ in range(args.eras):
                if not run_prepared_era():
                    print(bench.message,file=sys.stderr)
                    return 2
        while running:
            era_ran_frame = False
            help_was_open = help_mode
            inbox_was_open = inbox is not None
            event_batch = pygame.event.get()
            for event_index, event in enumerate(event_batch):
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEWHEEL:
                    footer_pager.move(-event.y)
                elif event.type == pygame.KEYDOWN:
                    control = bool(getattr(event, "mod", 0) & pygame.KMOD_CTRL)
                    if control and event.key == pygame.K_s:
                        if checkpoint(announce=True) and quit_after_retry:
                            return 0
                    elif control and event.key == pygame.K_q and save_failed:
                        print("Quit without saving current progress; the previous save is retained.", file=sys.stderr)
                        return 1
                    elif save_failed and event.key not in (pygame.K_F1, pygame.K_ESCAPE, pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                        continue
                    elif event.key == pygame.K_F1:
                        help_mode = not help_mode
                    elif help_mode:
                        if event.key == pygame.K_ESCAPE:
                            help_mode = False
                        elif event.key == pygame.K_PAGEUP:
                            footer_pager.move(-1)
                        elif event.key == pygame.K_PAGEDOWN:
                            footer_pager.move(1)
                    elif inbox is not None:
                        if event.key == pygame.K_ESCAPE or event.key == (pygame.K_i if inbox.kind == 'covenant' else pygame.K_k):
                            inbox = None
                            queued = None
                        elif event.key in (pygame.K_i, pygame.K_k):
                            inbox = InboxPicker(keeper_dir, 'covenant' if event.key == pygame.K_i else 'pack')
                        elif event.key in (pygame.K_COMMA, pygame.K_LEFT, pygame.K_UP):
                            inbox.move(-1)
                        elif event.key in (pygame.K_PERIOD, pygame.K_RIGHT, pygame.K_DOWN):
                            inbox.move(1)
                        elif event.key == pygame.K_HOME:
                            inbox.select(0)
                        elif event.key == pygame.K_END:
                            inbox.select(len(inbox.files)-1)
                        elif event.key == pygame.K_F5:
                            inbox.refresh()
                            footer_pager.reset()
                        elif event.key == pygame.K_RETURN and not getattr(event, 'repeat', False):
                            import_selected()
                        elif event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                            footer_pager.move(-1 if event.key == pygame.K_PAGEUP else 1)
                    elif inbox_was_open:
                        continue  # A closing key cannot leak care/preparation from its batch.
                    elif event.key == pygame.K_v:
                        if review is not None:
                            close_review()
                        else:
                            open_review()
                    elif event.key == pygame.K_b and review is None:
                        if browser is None:
                            open_archive()
                        else:
                            close_archive()
                    elif event.key == pygame.K_t:
                        if review is not None:
                            selected = review_context.current
                            open_era_review(selected["era_index"], review_context.history["campaign_id"])
                        elif browser is not None:
                            selected = browser.selected_era
                            open_era_review(selected['era_index'] if selected else None, browser.campaign_id)
                        elif era_review is None:
                            open_era_review()
                        else:
                            era_review = None
                    elif review is not None and event.key == pygame.K_ESCAPE:
                        close_review()
                    elif review is not None and event.key not in (
                        pygame.K_SPACE, pygame.K_PERIOD, pygame.K_COMMA, pygame.K_PAGEUP, pygame.K_PAGEDOWN,
                    ):
                        continue
                    elif browser is not None and event.key == pygame.K_n:
                        if isinstance(browser, NicheHistory):
                            close_archive()
                        else:
                            try:
                                root_id = bench.campaign.campaign['campaign_id'] if bench.campaign else None
                                browser = NicheHistory.load(keeper_dir, browser, campaign_id=root_id)
                            except (OSError, ValueError) as error:
                                browser.replay_notice = f'Niche history unavailable: {error}'
                            queued = None
                            footer_pager.reset()
                    elif browser is not None and event.key == pygame.K_ESCAPE:
                        close_archive()
                    elif browser is not None and not browser.allow_planning and event.key in (pygame.K_c, pygame.K_e):
                        continue
                    elif browser is not None and event.key not in (
                        pygame.K_PERIOD, pygame.K_COMMA, pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET,
                        pygame.K_a, pygame.K_c, pygame.K_e, pygame.K_PAGEUP, pygame.K_PAGEDOWN,
                    ):
                        continue
                    elif era_review is not None and campaign_story is not None and getattr(event, 'mod', 0) & pygame.KMOD_CTRL and event.key in (pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET):
                        era_review = campaign_story.move(-1 if event.key == pygame.K_LEFTBRACKET else 1)
                        queued = None
                        footer_pager.reset()
                    elif era_review is not None and event.key in (pygame.K_LEFTBRACKET, pygame.K_COMMA):
                        era_review.move(-1)
                    elif era_review is not None and event.key in (pygame.K_RIGHTBRACKET, pygame.K_PERIOD):
                        era_review.move(1)
                    elif era_review is not None and event.key == pygame.K_ESCAPE:
                        era_review = None
                    elif era_review is not None and event.key == pygame.K_c:
                        if not era_review.error:
                            era_review = None
                            covenant_mode = True
                    elif era_review is not None and event.key == pygame.K_e:
                        if not era_review.error:
                            run_prepared_era(event_batch[event_index + 1:])
                            break  # The waiting loop consumed the rest of this batch.
                    elif era_review is not None and event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                        footer_pager.move(-1 if event.key == pygame.K_PAGEUP else 1)
                    elif era_review is not None and (era_review.error or event.key not in (
                        pygame.K_PAGEUP, pygame.K_PAGEDOWN, pygame.K_r, pygame.K_w, pygame.K_BACKSPACE,
                        pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                    )):
                        continue
                    elif story is not None and event.key == pygame.K_ESCAPE:
                        story = None
                        queued = None
                    elif story is not None and event.key not in (
                        pygame.K_l, pygame.K_PERIOD, pygame.K_COMMA, pygame.K_PAGEUP, pygame.K_PAGEDOWN,
                    ):
                        continue
                    elif event.key == pygame.K_PAGEUP:
                        footer_pager.move(-1)
                    elif event.key == pygame.K_PAGEDOWN:
                        footer_pager.move(1)
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_g and session.alive and "cleanliness" in session.state:
                        queued = "clean"
                    elif event.key in key_actions and session.alive:
                        queued = key_actions[event.key]
                    elif (
                        event.key == pygame.K_RETURN
                        and not session.alive
                    ):
                        if not checkpoint():
                            continue
                        session.succeed()
                        ghost = None
                        driver = ClipDriver(driver.frame_counts)
                        checkpoint()
                    elif event.key == pygame.K_e:
                        run_prepared_era(event_batch[event_index + 1:])
                        break  # The waiting loop consumed the rest of this batch.
                    elif event.key == pygame.K_h:
                        # Hatch a founder under the ACTIVE covenant
                        # and adopt it; its origin is the engine's own
                        # generation trace (F8).
                        if not checkpoint():
                            continue
                        hatch_count += 1
                        hatched = bench.hatch(20260713 + hatch_count)
                        session = CompanionSession(
                            hatched["grid"],
                            bench.active_covenant(),
                            model=train_generation_model(
                                [hatched["grid"]]
                            ),
                            name=hatched["grid"]["grid_id"],
                            origin="hatched",
                            learning_policy=session.learning_policy,
                        )
                        ghost = None
                        driver = ClipDriver(driver.frame_counts)
                        bench.message = "hatched: " + origin_summary(
                            hatched["explanation"]
                        )
                        checkpoint()
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
                        queued = None
                    elif story is not None and event.key == pygame.K_PERIOD:
                        story.step()
                    elif story is not None and event.key == pygame.K_COMMA:
                        story.back()
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
                        inbox = InboxPicker(keeper_dir, 'pack')
                        queued = None
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
                        inbox = InboxPicker(keeper_dir, 'covenant')
                        queued = None
                    elif event.key == pygame.K_BACKSPACE:
                        prepare(bench.unstage)
                    elif event.key == pygame.K_w:
                        prepare(lambda: bench.stage_releases(gather_releases(keeper_dir)))
                    elif event.key == pygame.K_r:
                        prepare(lambda: bench.stage_releases([session.grid]))
                    elif event.key == pygame.K_c:
                        if browser is not None:
                            browser = archive_return = None
                            queued = None
                        covenant_mode = not covenant_mode
                    elif covenant_mode and event.key in (
                        pygame.K_1,
                        pygame.K_2,
                        pygame.K_3,
                        pygame.K_4,
                    ):
                        prepare(lambda: bench.spend(event.key - pygame.K_1))
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
                        prepare(lambda: bench.choose_weather((event.key - pygame.K_1) % len(WEATHER_NAMES)))
                    elif event.key == pygame.K_a and (bench.campaign or browser is not None):
                        # Browsing is a read. Only explicit adoption loads the
                        # current covenant and applies the existing engine gate.
                        selected = browser.current() if browser is not None else None
                        elite = (json.loads(json.dumps(selected['grid'])) if selected is not None else
                                 bench.campaign.best_elite_grid() if browser is None else None)
                        if elite is None:
                            bench.message = "No elite to adopt in this era."
                            continue
                        campaign = bench.ensure()
                        try:
                            adopted = CompanionSession(
                                elite, campaign.campaign['slip_profile'], model=session.model,
                                name=elite['grid_id'], origin='era_elite', learning_policy=session.learning_policy,
                            )
                        except ValueError as error:
                            bench.message = "Adoption refused: " + str(error)
                            continue
                        if not checkpoint():
                            continue
                        session = adopted
                        browser = archive_return = None
                        ghost = None
                        driver = ClipDriver(driver.frame_counts)
                        pygame.display.set_caption(f"{WINDOW_TITLE} - {session.name}")
                        bench.message = f"Adopted {elite['grid_id']}."
                        checkpoint()

            if (
                running
                and not era_ran_frame
                and not save_failed
                and not help_mode
                and inbox is None
                and not inbox_was_open
                and era_review is None
                and review is None
                and browser is None
                and story is None
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
                    if checkpoint() and args.auto_succeed:
                        session.succeed()
                        ghost = None
                        driver = ClipDriver(driver.frame_counts)
                        checkpoint()
                    elif args.ticks is not None:
                        # A bounded, unattended run ends at death.
                        running = False
                if ticks_run == args.ticks:
                    running = False

            if browser is not None:
                # The repertoire window: the elite's real packet under
                # the campaign's covenant, statically composed.
                packet = browser.packet()
                if packet is None:
                    archive_pixels = tuple(tuple((16, 18, 16) for _ in range(width * args.scale))
                                           for _ in range(panel_px))
                else:
                    archive_pixels = compose_frame(packet, previous_ghost=None, cell_px=args.scale).pixels
                blank_hud = tuple(
                    tuple(
                        (16, 18, 16) for _ in range(width * args.scale)
                    )
                    for _ in range(HUD_HEIGHT * args.scale)
                )
                lcd = stack_buffers(archive_pixels, blank_hud)
                snapshot = session.snapshot()
            elif review is not None:
                # The Review window: recorded body states, raw and
                # honestly effect-free (v1 packets declare none); the
                # wound frames wear the damage event's own cells.
                if review_playing and not help_mode and not help_was_open and frame % 2 == 0:
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
                panel = fit_recorded_panel(raster, width, height, args.scale)
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
            window.blit(surface, ((window_size[0] - width * args.scale) // 2, 0))
            footer = _footer_lines(snapshot, queued)
            if help_mode:
                footer = inbox.help_lines() if inbox is not None else list(HELP_LINES)
            elif inbox is not None:
                footer = inbox.lines()
            elif era_review is not None:
                footer = era_review.lines()
                if campaign_story is not None:
                    footer[1:1] = campaign_story.lines()[:1]
                    footer.extend(campaign_story.lines()[1:])
                    footer = [line.replace('Your companion is paused. [ ] eras   T close',
                        'Care paused. [ ] eras; Ctrl+[ ] campaigns; T close') for line in footer]
                    if campaign_story.index != len(campaign_story.views) - 1:
                        footer.append('C/E preparation uses the active campaign, not this historical selection.')
                if era_review.current is not None and not era_review.error:
                    footer.append(recording_status(era_review.history["campaign_id"], era_review.current))
                if not era_review.error:
                    actions = next((i for i,line in enumerate(footer) if line.startswith('B archive')),len(footer))
                    if bench.plan.pending is not None or bench._completed_work is not None:
                        if actions < len(footer): footer[actions] = 'B archive   V replay   E retry save'
                        footer.insert(1,bench.preparation_line())
                        footer.append(bench.preparation_controls())
                    else:
                        footer[actions:actions] = [bench.preparation_line()]
                        footer.append(bench.preparation_controls())
            elif story is not None:
                footer = [
                    "LINEAGE  " + story.caption(),
                    *story.detail_lines(),
                    ". older→newer  , newer→older  L close",
                    "Care paused. T recorded campaign story",
                ]
            elif browser is not None:
                footer = [("NICHE HISTORY  " if isinstance(browser, NicheHistory) else "REPERTOIRE  ") + browser.caption()]
                footer.append("N back to archive; , . occurrences" if isinstance(browser, NicheHistory) else "N niche history   campaign " + str(browser.campaign_id))
                if isinstance(browser, NicheHistory) and browser.warnings:
                    footer.append(f'{len(browser.warnings)} history notices; PgDn for missing/incompatible records.')
                if browser.current() is None:
                    footer.extend(["Care paused. No creature selected.",
                                   "[ ] other eras" if browser.selected_era is not None else "",
                                   "T era report   B/Escape back"])
                else:
                    footer.extend([
                        "Care paused. , . occurrences   [ ] occurrences" if isinstance(browser, NicheHistory) else "Care paused. , . creatures   [ ] eras",
                        "A adopt with current covenant   V recording",
                        browser.replay_notice or recording_status(browser.campaign_id, browser.selected_era, browser.current()),
                        "T selected report   B/Escape back",
                        browser.axes_line(), browser.components_line(),
                    ])
                if isinstance(browser, NicheHistory):
                    footer.extend(browser.history_lines())
            elif review is not None:
                footer = [
                    f"REVIEW ERA {review_context.current['era_index']}  {review.replay['creature']['grid_id']}",
                    review.caption(),
                    "Care paused. SPACE play/pause  . step  , back",
                    "V/Escape back   T selected report   F1 controls",
                    review.replay.get("honest_label", "Saved recording; its original provenance label was not stored."),
                ]
            elif covenant_mode:
                footer = [*bench.budget_lines(), bench.preparation_line(), *footer]
            else:
                footer.extend([bench.preparation_line(),
                    "F1 controls  Ctrl+S save  T report  E era  C covenant",
                    bench.preparation_controls()])
            if bench.message and not help_mode and (inbox is None or save_failed) and ((era_review is None and review is None) or save_failed):
                footer.insert(0, bench.message)
            context = ('help' if help_mode else 'inbox' if inbox is not None else 'era_report' if era_review is not None else 'lineage' if story is not None else
                       'repertoire' if browser is not None else 'review' if review is not None else
                       'covenant' if covenant_mode else 'play', bench.message, (inbox.kind, inbox.index, inbox.digest, inbox.error, tuple(inbox.result_lines)) if inbox is not None else era_review.index if era_review is not None else
                       (browser.campaign_id, browser.era_index, browser.index, isinstance(browser, NicheHistory)) if browser is not None else None)
            if context != footer_context:
                footer_pager.reset()
                footer_context = context
            rows = (FOOTER_PX - 12 - font.get_height()) // 22 + 1
            page = footer_pager.layout(footer, lambda text: font.size(text)[0], window_size[0] - 16, rows)
            for index, line in enumerate(page.lines):
                if line:
                    window.blit(
                        font.render(line, True, (200, 230, 200)),
                        (8, panel_px + hud_px + 6 + index * 22),
                    )
            pygame.display.flip()
            frame += 1
            clock.tick(args.fps)
            if save_failed and args.ticks is not None:
                return 1
            if not running:
                if checkpoint():
                    return 0
                if args.ticks is not None:
                    return 1
                quit_after_retry = True
                running = True
        return 0
    finally:
        pygame.quit()
