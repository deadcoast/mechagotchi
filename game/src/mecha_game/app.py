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
import hashlib
from datetime import datetime, timezone
import sqlite3
import json
import sys
from pathlib import Path

from mecha_engine.generation import train_generation_model
from mecha_engine.genome import clip_frame_count
from mecha_engine.runtime.care import CARE_POLICIES, CARE_EVALUATORS

from mecha_game.campaign import (
    ERA_CONFIG,
    TINY_ERA_CONFIG,
    WEATHER_NAMES,
    KeeperCampaign,
    default_campaign_paths,
    load_campaign_inputs,
    prepare_campaign_models,
)
from mecha_game.clips import TRANSITIONS, ClipDriver
from mecha_game.contribute import (founders_verdict, gather_releases,
                                   gather_release_inputs, companion_release_source)
from mecha_game.creator_bridge import CreatorBridge
from mecha_game.covenant_io import export_covenant, import_covenant
from mecha_game.packs import import_pack
from mecha_game.inbox import InboxPicker
from mecha_game.hatchery import hatch_founders
from mecha_game.generation_view import GenerationView
from mecha_game import wfc_trace
from mecha_game.lineage import LineageBrowser
from mecha_game.repertoire import RepertoireBrowser
from mecha_game.replay import ReplayPlayer, overlay_wounds
from mecha_game.covenant import (
    spend_deliberation_to_budget,
    spend_generations_to_cap,
    spend_next_palette,
    spend_population_to_cap,
    spend_next_organ_role,
    starter_role_covenant,
)
from mecha_game.footer import FooterPager, HELP_LINES
from mecha_game.thought_view import LiveThoughtView
from mecha_game.era_review import EraReview
from mecha_game.niche_history import CampaignStory, NicheHistory
from mecha_game.era_plan import EraPlan, state_digest
from mecha_game.preparation_commit import PreparationCommit
from mecha_game.preparation_readout import (
    role_progress_lines, next_era_line, covenant_change_summary, preparation_notice,
)
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
    from mecha_game.runtime_resources import source_checkout_root
    source = source_checkout_root(start)
    return source / "keeper" if source is not None else Path.home() / ".mechagotchi"


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
        help="new-life policy: built-in fresh Keeper defaults to qtable; custom inputs default to incumbent; existing Keepers preserve their saved policy",
    )
    parser.add_argument('--body-response', choices=('legacy', 'workload-v1'), default=None,
                        help='new-life body response: legacy default or opt-in workload-v1 play energy cost; saved choices remain')
    parser.add_argument('--care-selection', choices=('off', *CARE_POLICIES), default=None,
                        help='new-life care selection: off (default) or experimental observed care; saved choices are preserved')
    parser.add_argument('--care-evaluator', choices=CARE_EVALUATORS, default=None,
                        help='experimental selection probe (default: archive_morphology_probe_v1); not live personality')
    parser.add_argument("--recover-backup", action="store_true",
                        help="restore the previous companion save; validate it and archive the current save first")
    parser.add_argument('--startup', action='store_true', help='open the native save/restore/new companion chooser')
    parser.add_argument('--frames', type=int, default=None, help='quit after N rendered frames, including paused views')
    parser.add_argument('--creator', action='store_true', help='open the creator for this selected Keeper; care pauses')
    parser.add_argument('--no-browser', action='store_true', help='with --creator, retain the local URL without opening a browser')
    parser.add_argument('--launch-info', '--creator-info', type=Path, default=None,
                        help='write an owned diagnostic receipt to a new file outside your save data')
    parser.add_argument('--prepare-weather', choices=WEATHER_NAMES, default=None,
                        help='select and save ordinary era preparation before an optional --eras run')
    parser.add_argument('--population-policy', choices=('legacy_archive','generation_survivors_v1'), default=None,
                        help='explicit new campaign only: historical archive continuity or experimental living generations')
    parser.add_argument('--campaign-seed', type=int, default=None, help='explicit seed for a new campaign; saved campaigns refuse changes')
    parser.add_argument('--starter-roles', action='store_true', help='explicit new campaign with the optional four-role starter covenant')
    parser.add_argument('--prepare-survival-regime', choices=('sheltered','stress_probe'), default=None,
                        help='save the next era survival environment; experimental stress is separate from era scale')
    parser.add_argument('--prepare-density-pressure', choices=('off','on'), default=None,
                        help='save earned density pressure for recorded weather; storm-record tier 1 required')
    parser.add_argument('--create-successor', action='store_true', help='explicitly create the ended campaign successor before an optional era')
    parser.add_argument('--finish-preparation', action='store_true',
                        help='explicitly finish a captured covenant/successor save; never runs an era')
    parser.add_argument('--view', choices=('care','preparation','review','archive'), default='care',
                        help='open an existing native view after loading the selected companion')
    parser.add_argument('--example', choices=('care-to-era',), default=None,
                        help='run the isolated executable example with --output NEW_DIRECTORY')
    parser.add_argument('--reproduce-era', type=int, default=None, help='explicitly reproduce one saved era from immutable recorded inputs')
    parser.add_argument('--campaign-id', default=None, help='recorded campaign identity for --reproduce-era')
    parser.add_argument('--output', type=Path, default=None, help='new output directory for --example or --reproduce-era')
    return parser


def _frame_bytes(pixels: Buffer) -> bytes:
    return b"".join(bytes(rgb) for row in pixels for rgb in row)


class _EraBench:
    """The Keeper's preparation bench; evolution models load only for an era.
    Covenant actions and companion play never pay that training cost."""

    def __init__(
        self,
        era_scale: str,
        cache_dir: Path | None = None,
        state_path: Path | None = None,
        ledger_path: Path | None = None,
        initial_profile: dict | None = None,
        keeper_session: CompanionSession | None = None,
    ) -> None:
        self.era_scale = era_scale
        self.cache_dir = cache_dir
        self.state_path = state_path
        self.ledger_path = ledger_path
        self.initial_profile = json.loads(json.dumps(initial_profile)) if initial_profile is not None else None
        self.campaign: KeeperCampaign | None = None
        self.keeper_session = keeper_session
        self.recovery_offer = None
        self.plan = EraPlan(state_path.with_name('era_plan.json') if state_path is not None else None)
        self.weather_index = WEATHER_NAMES.index(self.plan.weather)
        self._loaded_state_digest = state_digest(state_path)
        self._loaded_ledger_digest = state_digest(ledger_path)
        self._completed_work = None
        self._completed_previous_state = None
        self._pending_preparation_digest = None
        self.preparation_commit = (PreparationCommit(state_path, ledger_path)
                                   if state_path is not None and ledger_path is not None else None)
        self.message = preparation_notice(self.preparation_commit) or self.plan.error or ""

    @property
    def weather(self) -> str:
        return WEATHER_NAMES[self.weather_index]

    def _check_binding(self, campaign):
        """A read verifies a known association without inventing a new one."""
        self._check_campaign_identity(campaign.state_payload())

    def _check_campaign_identity(self, state):
        from mecha_game.compatibility import require_campaign_compatibility
        require_campaign_compatibility(state, keeper_session=self.keeper_session, state_path=self.state_path)

    def bind_current_campaign(self):
        if self.keeper_session is None or self.campaign is None:
            return False
        self._check_binding(self.campaign)
        return self.keeper_session.bind_campaign(
            self.campaign.campaign['campaign_id'],
            predecessor_campaign_id=self.campaign.campaign.get('predecessor_campaign_id'))

    def _remember_files(self):
        self._loaded_state_digest = state_digest(self.state_path)
        self._loaded_ledger_digest = state_digest(self.ledger_path)

    def ensure(self, *, models: bool = False) -> KeeperCampaign:
        if self.campaign is None:
            from mecha_game.campaign_recovery import has_campaign_evidence
            established = (self.state_path is not None and self.ledger_path is not None
                           and has_campaign_evidence(self.state_path, self.ledger_path))
            if established and (not self.state_path.is_file() or not self.ledger_path.is_file()):
                raise ValueError('Campaign state and ledger must both be present. U inspects recovery; nothing was replaced.')
            paths = default_campaign_paths()
            tiny = self.era_scale == 'tiny'
            inputs = load_campaign_inputs(
                paths['seed_dir'], paths['slip_path'], paths['adopted_model_path'],
                repair_epochs=6 if tiny else 40, seed_limit=12 if tiny else None,
                cache_dir=self.cache_dir, with_models=False)
            if established:
                candidate = KeeperCampaign.load_state(inputs, self.state_path, self.ledger_path)
            else:
                if self.initial_profile is not None:
                    inputs = dict(inputs, slip_profile=copy.deepcopy(self.initial_profile))
                identity = ({'campaign_id': self.keeper_session.keeper_id,
                             'created_date': datetime.now(timezone.utc).date().isoformat()}
                            if self.keeper_session is not None else {})
                candidate = KeeperCampaign(inputs, era_config=TINY_ERA_CONFIG if tiny else ERA_CONFIG,
                                           body_response=getattr(self.keeper_session, 'body_response', 'legacy'), **identity)
            self._check_binding(candidate)
            self.campaign = candidate
            if established:
                self.message = f'campaign resumed at era {candidate.era_offset}'
            self._remember_files()
        else:
            self._check_binding(self.campaign)
        if models:
            self.check_current_state()
            self.campaign.inputs = prepare_campaign_models(self.campaign.inputs,
                repair_epochs=6 if self.era_scale == 'tiny' else 40, cache_dir=self.cache_dir)
        return self.campaign

    def new_campaign_available(self):
        from mecha_game.campaign_recovery import has_campaign_evidence
        if self.state_path is not None and self.ledger_path is not None and has_campaign_evidence(self.state_path, self.ledger_path):
            return False
        return self.campaign is None or (not self.campaign.eras and self.campaign.era_offset == 0
            and self.campaign.campaign.get('predecessor_campaign_id') is None)

    def choose_new_campaign(self, population_policy, *, starter_roles=False, base_seed=None):
        self.require_preparation()
        if not self.new_campaign_available():
            raise ValueError('A recorded campaign keeps its population policy. Choose a separate new Keeper for a new mode.')
        if population_policy not in ('legacy_archive', 'generation_survivors_v1') or type(starter_roles) is not bool:
            raise ValueError('Invalid new campaign choice.')
        if base_seed is not None and (type(base_seed) is not int or base_seed < 0):
            raise ValueError('Campaign seed must be a nonnegative integer.')
        current = self.ensure()
        self.check_current_state()
        profile = starter_role_covenant(current.base_profile) if starter_roles else copy.deepcopy(current.base_profile)
        identity = current.campaign
        candidate = KeeperCampaign(dict(current.inputs, slip_profile=profile), era_config=current.era_config,
            campaign_id=identity['campaign_id'], keeper_label=identity['keeper_label'], created_date=identity['created_date'],
            base_seed=identity['base_seed'] if base_seed is None else base_seed, population_policy=population_policy,
            body_response=current.body_response)
        if starter_roles:
            from mecha_game.execution import source_record
            raw = (json.dumps(profile, indent=2) + '\n').encode('utf-8')
            candidate.base_covenant_source = source_record(raw, role='base_covenant',
                source_kind='designed_covenant', label='Optional starter roles v1')
        else:
            candidate.base_covenant_source = copy.deepcopy(current.base_covenant_source)
        if self.state_path is not None and self.ledger_path is not None:
            from mecha_game.campaign_recovery import initialize_campaign_checkpoint
            initialize_campaign_checkpoint(candidate, self.state_path, self.ledger_path)
        self.campaign = candidate
        self._remember_files()
        self.message = ('New experimental living-generation campaign saved.' if population_policy == 'generation_survivors_v1'
                        else 'New archive-continuity campaign saved.')
        if starter_roles: self.message += ' Four-role starter selected; earned roles require an explicit spend.'

    def choose_survival_regime(self, regime):
        self.require_preparation()
        self.plan.select_survival_regime(regime)
        self.message = 'Next survival environment saved: ' + ('experimental stress probe.' if regime == 'stress_probe' else 'sheltered.')

    def choose_density_pressure(self, enabled):
        self.require_preparation()
        if type(enabled) is not bool:
            raise ValueError('Density pressure must be on or off.')
        if enabled:
            from mecha_game.campaign import build_weather_source
            campaign = self.ensure()
            self.check_current_state()
            if not campaign.budget()['cubff_density_pressure_allowed']:
                raise ValueError('Density pressure requires earned storm-record tier 1.')
            if not build_weather_source(self.weather):
                raise ValueError('Density pressure requires a recorded weather source; calm has none.')
        self.plan.select_density_pressure(enabled)
        self.message = 'Next weather density pressure saved: ' + ('on.' if enabled else 'off.')

    def create_successor(self):
        self.require_preparation()
        current = self.ensure()
        self.check_current_state()
        if current.status != 'extinct':
            raise ValueError('Only an extinct campaign can create a successor.')
        candidate = current.successor()
        self._save_preparation(candidate, current, kind='successor',
            summary='Create successor with inherited unlocks and its base covenant.')
        self.message = 'Successor created with inherited unlocks and its base covenant. Choose preparation, then run its first era.'

    def inspect_recovery(self, *, slot="current"):
        from mecha_game.campaign_recovery import inspect_campaign_backup
        if self.state_path is None or self.ledger_path is None:
            raise ValueError('No campaign save home is selected.')
        offer = inspect_campaign_backup(self.state_path, self.ledger_path, slot=slot)
        # Inspection may show an incompatible historical model; restore still
        # requires the current compatibility boundary before any mutation.
        current = getattr(self.keeper_session, 'campaign_id', None)
        if current is not None and current not in (offer['state']['campaign_id'], offer['state'].get('predecessor_campaign_id')):
            raise ValueError('Campaign belongs to a different recorded Keeper history; files preserved.')
        if self.preparation_commit is not None:
            self.preparation_commit.refresh()
        self.recovery_offer = dict(offer, target_state_digest=state_digest(self.state_path),
                                   target_ledger_digest=state_digest(self.ledger_path),
                                   preparation_digest=((self.preparation_commit.journal_digest
                                       if self.preparation_commit is not None else None) or offer.get('preparation_digest')))
        return self.recovery_offer

    def restore_recovery(self):
        from mecha_game.campaign_recovery import recover_campaign_backup
        offer = self.recovery_offer
        if offer is None:
            raise ValueError('Inspect the recovery checkpoint before restoring it.')
        if (offer['target_state_digest'] != state_digest(self.state_path)
                or offer['target_ledger_digest'] != state_digest(self.ledger_path)):
            self.recovery_offer = None
            raise ValueError('Campaign files changed after inspection. U inspects them again; files preserved.')
        self._check_campaign_identity(offer['state'])
        recover_campaign_backup(self.state_path, self.ledger_path,
            expected_manifest_digest=offer['manifest_digest'],
            expected_campaign_id=offer['state']['campaign_id'], slot=offer['slot'],
            expected_preparation_digest=offer.get('preparation_digest'))
        if self.preparation_commit is not None:
            self.preparation_commit.refresh()
        self.campaign = None
        self.recovery_offer = None
        self._remember_files()
        self.ensure()
        self.message = 'Campaign checkpoint restored; previous primary bytes retained.'
        if self.plan.pending is not None:
            self.message += ' E finishes the already recorded pending result once.'

    def recovery_lines(self):
        if self.recovery_offer is None:
            return ['U inspect latest checkpoint; Y inspect prior. C close, F1 help.']
        state = self.recovery_offer['state']
        label = 'latest' if self.recovery_offer['slot'] == 'current' else 'prior'
        return [f'RECOVERY ({label}): U restore / C cancel',
                'Care paused. Current primary bytes will be retained.',
                f"Campaign {state['campaign_id']}: {state['era_count']} recorded eras",
                ('Captured preparation is archived after this verified restore; no choice is replayed.'
                 if self.recovery_offer.get('preparation_digest') else 'Pending completed eras stay recorded.'),
                'Y inspects the prior checkpoint.']

    def budget_lines(self) -> list[str]:
        """The covenant mode's display — every number the campaign's
        own budget/covenant, verbatim (F7)."""
        if self.recovery_offer is not None:
            return self.recovery_lines()
        notice = preparation_notice(self.preparation_commit)
        if notice:
            return [notice, 'C close; care and recorded history remain available.', *self.recovery_lines()]
        try:
            campaign = self.ensure()
            budget = campaign.budget()
        except (OSError, ValueError, sqlite3.Error) as error:
            return ['Covenant unavailable', *self.recovery_lines(), str(error),
                    'Saved campaign unchanged; care remains available.']
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
            "1 palette  2 thinking  3 population  4 generations  5 organ role",
            *role_progress_lines(campaign),
            ('Living generations (experimental): only qualified survivors continue.' if campaign.population_policy == 'generation_survivors_v1'
             else 'Population: historical archive continuity'),
            '6 density '+('on' if self.plan.cubff_density_pressure else 'off')+'; 7 survival '+self.plan.survival_regime,
            ('Density choice earned: select recorded weather.' if budget['cubff_density_pressure_allowed']
             else 'Density pressure needs storm-record tier 1.'),
            ('8 start living generations; 9 start with role limits (experimental)' if self.new_campaign_available()
             else 'N create successor' if campaign.status == 'extinct' else 'Saved population policy stays fixed; archives remain history.'),
            "C close",
            "Care continues here; F1 pauses. Close C for weather keys.",
            "I choose covenant   K choose pack   X export",
            "H hatch preview   O saved origin   U/Y recovery   F1 controls",
            *([] if self.recovery_offer is None else self.recovery_lines()),
        ]

    def require_preparation(self):
        from mecha_game.compatibility import require_keeper_writable
        if self.state_path is not None:
            require_keeper_writable(self.state_path.parent)
        if self.campaign is not None:
            self._check_binding(self.campaign)
        if self.preparation_commit is not None:
            self.preparation_commit.require_ready()
        self.plan.require_ready()
        if self._completed_work is not None:
            raise ValueError('E finishes saving the completed era before another preparation change.')

    def preparation_line(self):
        notice = preparation_notice(self.preparation_commit)
        if notice: return notice
        if self.plan.error: return self.plan.error
        if self.plan.pending is not None or self._completed_work is not None:
            return 'ERA RESULT awaiting save. E retry; no new era runs.'
        policy = self.campaign.population_policy if self.campaign is not None else 'legacy_archive'
        body_response = self.campaign.body_response if self.campaign is not None else getattr(self.keeper_session, 'body_response', 'legacy')
        if self.campaign is None and self.state_path is not None:
            try:
                if self.state_path.exists():
                    saved = json.loads(self.state_path.read_text(encoding='utf-8'))
                    KeeperCampaign.validate_state_payload(saved)
                    policy = saved.get('population_policy', 'legacy_archive')
                    body_response = saved.get('body_response', 'legacy')
                elif self.ledger_path is not None:
                    from mecha_game.campaign_recovery import has_campaign_evidence
                    if has_campaign_evidence(self.state_path, self.ledger_path):
                        policy = None
            except (OSError, ValueError, TypeError, KeyError):
                policy = None
        return next_era_line(self.weather, len(self.plan.releases), population_policy=policy,
                            survival_regime=self.plan.survival_regime, density=self.plan.cubff_density_pressure, body_response=body_response)

    def preparation_controls(self):
        if preparation_notice(self.preparation_commit):
            return ('C/U inspect recovery; care and recorded history remain available.' if self.preparation_commit.error
                    else 'C then E finish captured preparation; U inspect recovery; no new era runs.')
        if self.plan.error:
            return 'Preparation unavailable; care and recorded history remain available.'
        if self.plan.pending is not None or self._completed_work is not None:
            return 'E retry save   T report   F1 help'
        return '1-5 weather   R stage current pet   W gather   Backspace unstage'

    def choose_weather(self, index):
        self.require_preparation()
        if self.plan.cubff_density_pressure and WEATHER_NAMES[index] == 'calm':
            raise ValueError('Turn density pressure off before choosing calm weather.')
        self.plan.select_weather(WEATHER_NAMES[index])
        self.weather_index = index
        self.message = f'Next era weather saved: {self.weather}.'

    def stage_releases(self, grids, sources=None):
        self.require_preparation()
        added = self.plan.stage(grids, sources=sources)
        self.message = f'Staged {added}; {len(self.plan.releases)} ready for the next era. Your companion stays with you.'
        if any(isinstance(source, dict) and source.get('care_context') is not None
               for source in self.plan.release_sources):
            self.message += ' Care snapshot frozen; unstage/restage to update.'

    def check_current_state(self):
        if state_digest(self.state_path) != self._loaded_state_digest:
            raise ValueError('Campaign state changed outside this session; existing state preserved.')
        if state_digest(self.ledger_path) != self._loaded_ledger_digest:
            raise ValueError('Campaign ledger changed outside this session; existing ledger preserved.')
        if self.state_path is not None and self.state_path.is_file():
            from mecha_game.campaign_recovery import validate_ledger_state
            validate_ledger_state(json.loads(self.state_path.read_text(encoding='utf-8')), self.ledger_path)

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
            summary = covenant_change_summary(current.state_payload(), candidate.state_payload())
            self._save_preparation(candidate, current, kind='covenant', summary=summary)
            self.message = summary
        return result

    def _save_preparation(self, candidate, current, *, kind, summary):
        self._pending_preparation_digest = None
        if self.preparation_commit is not None:
            self.preparation_commit.begin(candidate, kind=kind, summary=summary,
                expected_state_digest=self._loaded_state_digest,
                expected_ledger_digest=self._loaded_ledger_digest,
                source_campaign_id=current.campaign['campaign_id'])
            self._pending_preparation_digest = self.preparation_commit.journal_digest
            self.preparation_commit.finish(expected_journal_digest=self._pending_preparation_digest,
                expected_campaign_id=current.campaign['campaign_id'])
            self._pending_preparation_digest = None
        self.campaign = candidate
        self._remember_files()

    def finish_preparation(self, *, expected_journal_digest=None):
        self.plan.require_ready()
        if self._completed_work is not None:
            raise ValueError('Finish saving the completed era before another preparation change.')
        if self.preparation_commit is None:
            self.message = 'No saved preparation awaits finishing.'
            return False
        self.preparation_commit.refresh()
        if expected_journal_digest is not None and self.preparation_commit.journal_digest != expected_journal_digest:
            raise ValueError('Captured preparation changed since this import attempt; existing files preserved.')
        if self.preparation_commit.pending is not None:
            self._check_campaign_identity(self.preparation_commit.pending['state'])
        summary = (self.preparation_commit.pending or {}).get('summary', 'Preparation saved.')
        expected = self.keeper_session.campaign_id if self.keeper_session is not None else None
        state = self.preparation_commit.finish(expected_journal_digest=(expected_journal_digest or
            self.preparation_commit.journal_digest), expected_campaign_id=expected)
        if state is None:
            self.message = 'No saved preparation awaits finishing.'
            return False
        self._pending_preparation_digest = None
        self.campaign = None
        self._remember_files()
        self.ensure()
        self.message = summary + ' Captured preparation finished; no era ran.'
        return True

    def preparation_failed(self, error):
        if self.preparation_commit is not None:
            self.preparation_commit.refresh()
        notice = preparation_notice(self.preparation_commit)
        if notice:
            self.message = f'{notice} {error}'
        else:
            self.message = f'Preparation action not completed: {error}. Inspect saved choices before retrying.'
        return self.message

    def spend(self, key_index: int) -> None:
        spends = {0:spend_next_palette,1:spend_deliberation_to_budget,
                  2:spend_population_to_cap,3:spend_generations_to_cap,4:spend_next_organ_role}
        result = self.change_covenant(spends[key_index])
        if not result['ok']:
            self.message = '; '.join(result['violations'])

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
        self, ledger_path: Path, released_grids: list[dict] | None = None, *, released_sources=None, work=None
    ) -> dict:
        if self.preparation_commit is not None:
            self.preparation_commit.require_ready()
        self.plan.require_ready(allow_pending=True)
        if self.plan.pending is not None:
            self._check_campaign_identity(self.plan.pending['state'])
            if work is not None: work.begin_commit()
            era = self.plan.finish(ledger_path,self.state_path)
            # A recovered persisted era is history, not a new current-run era.
            self.campaign = None
            self._remember_files()
            self._completed_work = None
            self.message = f"Era {era['era_index']} saved. No additional era ran."
            return era
        if self._completed_work is None:
            current = self.ensure()
            if current.status != 'active' and current.population_policy == 'generation_survivors_v1':
                raise ValueError('This population is extinct. Create its successor explicitly before running another era.')
            if work is not None: work.phase("Loading models")
            current = self.ensure(models=True)
            self.check_current_state()
            campaign = copy.deepcopy(current)
            if campaign.status != 'active': campaign = campaign.successor()
            previous_state = state_digest(self.state_path)
            era = campaign.advance_era(self.weather,released_grids=(
                released_grids if released_grids is not None else self.plan.releases) or None,
                released_sources=(released_sources if released_grids is not None else self.plan.release_sources) or None,
                record_original=True,
                **(dict(survival_regime=self.plan.survival_regime,
                        cubff_density_pressure=self.plan.cubff_density_pressure)
                   if self.plan.survival_regime != 'sheltered' or self.plan.cubff_density_pressure else {}),
                care_selection_policy=getattr(self.keeper_session, 'care_selection_policy', 'off'),
                care_evaluator=getattr(self.keeper_session, 'care_evaluator', 'archive_morphology_probe_v1'),
                **({"progress_callback": work.progress} if work is not None else {}))
            if work is not None: work.begin_commit()
            self._completed_work = campaign
            self._completed_previous_state = previous_state
        if work is not None: work.begin_commit()
        campaign = self._completed_work
        self._check_binding(campaign)
        era = campaign.eras[-1]
        self.plan.begin(campaign,era,self._completed_previous_state)
        self.plan.finish(ledger_path,self.state_path)
        self.campaign = campaign
        self._remember_files()
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


def _care_selection_lines(snapshot: dict) -> list[str]:
    from mecha_game.body_response import body_lines
    details = body_lines(snapshot)
    if snapshot.get('care_selection_policy', 'off') == 'off':
        return ['Care selection: off', *details]
    evaluator = ('pristine control' if snapshot.get('care_evaluator') == 'pristine'
                 else 'morphology stress probe')
    return ['Care selection: experimental; benefit unqualified',
            'Selection evaluator: ' + evaluator + '; not live personality', *details]


def _footer_lines(snapshot: dict, queued: str | None, *, thought_lines=()) -> list[str]:
    if not snapshot["alive"]:
        return [
            f"{snapshot['name']} died: {snapshot['death_cause']}"
            f" (age {snapshot['age_ticks']})",
            "ENTER: adopt successor    ESC: quit",
            ("Policy: Q-table; learns within this life" if snapshot.get("learning_policy") == "qtable"
             else "Policy: incumbent"),
            *_care_selection_lines(snapshot),
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
        f"life {snapshot['generation_count']}"
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
    lines = [line, *thought_lines, controls, detail, felt]
    if snapshot.get("learning_policy", "incumbent") == "incumbent":
        lines.append("Policy: incumbent")
    if "cleanliness" in needs and "clean" in snapshot.get("actions", []):
        lines.append(f"cleanliness {needs['cleanliness']['value']:.2f}   G clean")
    if snapshot.get("learning_policy") == "qtable":
        policy_line = "Q-table (within this life)"
        signal = threads.get("qtable_policy")
        if not snapshot.get("learning_active"):
            policy_line += ": inactive (fleet off)"
        elif not signal or signal["output"].get("cold_start", True):
            policy_line += ": learning from care"
        else:
            policy_line += f": recommends {signal['output']['best_action']} (confidence {signal['confidence']:.2f})"
        lines.append(policy_line)
    lines.extend(_care_selection_lines(snapshot))
    return lines


def _explicit_new_session(companion_path, grid, slip_profile, model, learning_policy, *, inspection=None,
                          care_selection_policy=None, care_evaluator=None, body_response=None):
    # Keep the established application import seam; startup owns captured-byte
    # inspection and explicit new-life preservation for both entry forms.
    from mecha_game.startup import explicit_new_session
    return explicit_new_session(companion_path, grid, slip_profile, model,
                                learning_policy, inspection=inspection,
                                care_selection_policy=care_selection_policy, care_evaluator=care_evaluator, body_response=body_response)


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    arguments = list(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(arguments)
    if args.recover_backup and (args.new or args.slip is not None or args.seed is not None):
        parser.error('--recover-backup cannot be combined with --new, --slip or --seed')
    if args.no_browser and not args.creator:
        parser.error('--no-browser requires --creator')
    if args.scale < 1 or args.tick_frames < 1 or args.fps < 0 or (args.frames is not None and args.frames < 1):
        parser.error('scale, tick-frames and frames must be positive; fps cannot be negative')
    if args.finish_preparation and (args.eras is not None or args.create_successor or args.new
            or args.recover_backup or args.creator or args.example or args.reproduce_era is not None
            or args.seed is not None or args.slip is not None or args.learning_policy is not None
            or args.care_selection is not None or args.care_evaluator is not None or args.body_response is not None
            or args.population_policy is not None or args.campaign_seed is not None or args.starter_roles
            or args.prepare_weather is not None or args.prepare_survival_regime is not None
            or args.prepare_density_pressure is not None):
        parser.error('--finish-preparation finishes only its captured choice; run new actions separately')
    if args.reproduce_era is not None:
        if args.keeper_dir is None or args.campaign_id is None or args.output is None:
            parser.error('--reproduce-era requires --keeper-dir DIR --campaign-id ID --output NEW_DIRECTORY')
        if (args.example or args.new or args.recover_backup or args.creator or args.eras is not None or args.prepare_weather is not None
                or args.population_policy is not None or args.campaign_seed is not None or args.starter_roles
                or args.prepare_survival_regime is not None or args.prepare_density_pressure is not None or args.create_successor or args.finish_preparation):
            parser.error('--reproduce-era cannot be combined with example, companion, creator or era-writing actions')
        from mecha_game.execution_readout import reproduce_to_directory, comparison_notice
        try:
            result = reproduce_to_directory(args.keeper_dir, args.campaign_id, args.reproduce_era, args.output)
            print(comparison_notice(result))
            return {'matched': 0, 'mismatch': 1, 'unavailable': 2}[result['status']]
        except (OSError, ValueError) as error:
            print(f'Reproduction refused: {error}', file=sys.stderr)
            return 2
    if args.campaign_id is not None:
        parser.error('--campaign-id requires --reproduce-era')
    if args.example:
        if args.output is None:
            parser.error('--example requires --output NEW_DIRECTORY')
        from mecha_game.examples import run_example
        command = ([sys.executable] if getattr(sys, 'frozen', False) else
                   [sys.executable, '-B', str(Path(__file__).resolve().parents[2] / 'run_game.py')])
        example_scale = args.era_scale if any(a == '--era-scale' or a.startswith('--era-scale=') for a in arguments) else 'tiny'
        try:
            result = run_example(command, args.output, weather=args.prepare_weather or 'calm', era_scale=example_scale)
            return 0 if result['ok'] else 1
        except (OSError, ValueError) as error:
            print(f'Example refused: {error}', file=sys.stderr)
            return 2
    if args.output is not None:
        parser.error('--output requires --example or --reproduce-era')
    from mecha_game.launch_info import LaunchInfo
    try:
        receipt = LaunchInfo(args.launch_info)
    except (OSError, ValueError) as error:
        print(f'Launch receipt unavailable; existing files preserved: {error}', file=sys.stderr)
        return 2
    exit_code = 1
    try:
        exit_code = _run_selected(args, parser, receipt)
        return exit_code
    except SystemExit as error:
        exit_code = error.code if isinstance(error.code, int) else 2
        raise
    finally:
        try:
            receipt.finish(exit_code)
        except (OSError, ValueError) as error:
            print(f'Launch receipt could not be finalized; external data preserved: {error}', file=sys.stderr)


def _run_selected(args, parser, receipt):
    import pygame
    from mecha_game.entry import choose_entry
    from mecha_game.runtime_resources import inspect_runtime
    if receipt.path is not None:
        receipt.update(runtime=inspect_runtime())
    try:
        selected, code = choose_entry(args, default_home=default_keeper_dir,
                                      default_paths=default_fixture_paths,
                                      new_session=_explicit_new_session, receipt=receipt)
    except (OSError, ValueError) as error:
        receipt.update(startup_outcome='refused', reason=str(error))
        parser.error(f'Cannot resume companion: {error}. Existing files are preserved.')
    if selected is None:
        return code
    session, keeper_dir, recovery_notice = selected.session, selected.home, selected.notice
    lineage_path = keeper_dir / LINEAGE_FILENAME
    companion_path = keeper_dir / COMPANION_FILENAME
    campaign_ledger = keeper_dir / 'campaign.sqlite3'
    receipt.update(keeper_dir=str(keeper_dir), keeper_id=session.keeper_id,
                   campaign_id=session.campaign_id, learning_policy=session.learning_policy,
                   care_selection_policy=session.care_selection_policy, care_evaluator=session.care_evaluator,
                   **({'body_response': session.body_response, 'body_workload': session.state['body_workload']} if session.body_response != 'legacy' else {}))

    bench = _EraBench(
        args.era_scale,
        cache_dir=keeper_dir / "model_cache",
        state_path=keeper_dir / "campaign_state.json",
        ledger_path=campaign_ledger,
        initial_profile=session.slip_profile,
        keeper_session=session,
    )

    if recovery_notice:
        bench.message = recovery_notice
        print(recovery_notice)

    if args.recover_backup or (companion_path.is_file() and not args.new):
        try:
            session.sync_lineage_export(lineage_path)
        except ValueError as error:
            parser.error(f'Cannot resume companion: {error}')
        except OSError as error:
            reason = error.strerror or str(error)
            warning = f"Companion loaded. Lineage export unavailable: {reason}."
            bench.message = (bench.message + " " + warning).strip()
            print(f"{warning}\n{error}", file=sys.stderr)

    width, height = session.grid["grid_size"]

    key_actions = {
        pygame.K_f: "feed",
        pygame.K_p: "play",
        pygame.K_s: "sleep",
    }

    creator = CreatorBridge(keeper_dir)
    pygame.init()
    try:
        from mecha_game.native_ui import ActionStrip, UiAction, fit_native_layout
        display = pygame.display.Info()
        display_bounds = (max(384, display.current_w), max(360, display.current_h))
        window_size = (min(display_bounds[0], max(640, width * args.scale + 16)),
                       min(display_bounds[1], max(480, (height + HUD_HEIGHT) * args.scale + FOOTER_PX + 174)))
        window = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        pygame.display.set_caption(f"{WINDOW_TITLE} — {session.name}")
        font = pygame.font.Font(None, 22)
        layout = fit_native_layout(window_size, (width, height + HUD_HEIGHT), font.get_height(),
                                   preferred_scale=args.scale)
        cell_px = layout.scale
        panel_px, hud_px = height * cell_px, HUD_HEIGHT * cell_px
        action_strip = ActionStrip(allow_tab=False)
        action_keys = {}
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
        creator_mode = False
        creator_url = None
        recovery_inspected_frame = None
        help_mode = False
        help_bookmark = None
        live_thought = LiveThoughtView()
        reading_closed = False
        inboxes: dict[str, InboxPicker] = {}
        inbox: InboxPicker | None = None
        inbox_pending_import = None
        generation: GenerationView | None = None
        wfc: wfc_trace.WfcTraceView | None = None
        wfc_count = 0
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

        def resize_native(size):
            nonlocal window, window_size, layout, cell_px, panel_px, hud_px, ghost
            window_size = (min(display_bounds[0], max(384, int(size[0]))),
                           min(display_bounds[1], max(360, int(size[1]))))
            window = pygame.display.set_mode(window_size, pygame.RESIZABLE)
            new_layout = fit_native_layout(window_size, (width, height + HUD_HEIGHT), font.get_height())
            if new_layout.scale != cell_px:
                ghost = None  # A different raster size cannot reuse pixel ghost buffers.
            layout = new_layout
            cell_px = layout.scale
            panel_px, hud_px = height * cell_px, HUD_HEIGHT * cell_px
            action_strip._armed = False
            action_strip._pressed = None

        def resize_event(event):
            if event.type == pygame.VIDEORESIZE:
                resize_native((event.w, event.h))
                return True
            if event.type == pygame.WINDOWSIZECHANGED:
                size = window.get_size()
                if size != window_size:
                    resize_native(size)
                    return True
            return False

        def paint_footer(lines, pager):
            page = pager.layout(lines, lambda text: font.size(text)[0], layout.footer_rect.width,
                                layout.footer_rows)
            for index, line in enumerate(page.lines):
                if line:
                    window.blit(font.render(line, True, (200, 230, 200)),
                                (layout.footer_rect.x, layout.footer_rect.y + 4 + index * layout.line_height))
            return page

        def native_actions():
            # These are existing commands, not new care/campaign implementations.
            nonlocal action_keys
            action_keys = {}
            actions = []
            def add(identity, label, code, *, mod=0, enabled=True, hint='', destructive=False):
                actions.append(UiAction(identity, label, hint, enabled, destructive))
                action_keys[identity] = (code, mod)
            def pages():
                add('previous_page', 'Text <', pygame.K_PAGEUP)
                add('next_page', 'Text >', pygame.K_PAGEDOWN)
            def common():
                add('help', 'Help [F1]', pygame.K_F1)
                add('save', 'Save', pygame.K_s, mod=pygame.KMOD_CTRL)
                add('quit', 'Save and quit', None)
            preparation_waiting = bool(preparation_notice(bench.preparation_commit))
            ready = not preparation_waiting and not bench.plan.error and bench.plan.pending is None and bench._completed_work is None
            if save_failed:
                add('save', 'Retry save', pygame.K_s, mod=pygame.KMOD_CTRL)
                add('quit_without_save', 'Quit without saving', pygame.K_q, mod=pygame.KMOD_CTRL, destructive=True)
                add('help', 'Help [F1]', pygame.K_F1); pages()
            elif help_mode:
                add('back', 'Back', pygame.K_ESCAPE); pages()
            elif creator_mode:
                add('back', 'Back to care', pygame.K_j)
                add('reopen_creator', 'Open browser', pygame.K_RETURN); pages(); common()
            elif bench.recovery_offer is not None:
                add('back', 'Cancel recovery', pygame.K_c)
                add('restore_campaign', 'Restore inspected', pygame.K_u, destructive=True)
                add('prior_checkpoint', 'Inspect prior', pygame.K_y); pages(); common()
            elif wfc is not None:
                add('back', 'Back to hatch', pygame.K_TAB)
                add('playback', 'Pause' if wfc.playing else 'Play', pygame.K_SPACE)
                add('previous_frame', 'Frame <', pygame.K_COMMA)
                add('next_frame', 'Frame >', pygame.K_PERIOD)
                add('previous_attempt', 'Attempt <', pygame.K_LEFTBRACKET)
                add('next_attempt', 'Attempt >', pygame.K_RIGHTBRACKET)
                add('final', 'Trace / final', pygame.K_v)
                add('retry_trace', 'New trace', pygame.K_n); pages(); common()
            elif generation is not None:
                add('back', 'Back', pygame.K_ESCAPE)
                if generation.adoptable:
                    add('adopt_hatch', 'Adopt founder', pygame.K_RETURN,
                        enabled=generation.grid is not None and not generation.error, destructive=True)
                    add('next_hatch', 'Next founder', pygame.K_n)
                    add('trace', 'WFC trace [Tab]', pygame.K_TAB)
                add('playback', 'Pause' if generation.playing else 'Play', pygame.K_SPACE)
                add('previous_frame', 'Frame <', pygame.K_COMMA)
                add('next_frame', 'Frame >', pygame.K_PERIOD)
                add('previous_clip', 'Clip <', pygame.K_LEFTBRACKET)
                add('next_clip', 'Clip >', pygame.K_RIGHTBRACKET); pages(); common()
            elif inbox is not None:
                add('back', 'Back', pygame.K_ESCAPE)
                add('previous_file', 'File <', pygame.K_COMMA, enabled=bool(inbox.files))
                add('next_file', 'File >', pygame.K_PERIOD, enabled=bool(inbox.files))
                retry_import = (inbox_pending_import is not None and inbox.kind == 'covenant' and
                    (str(inbox.selected), inbox.digest) == inbox_pending_import['selection'])
                add('import_selected', 'Finish captured import' if retry_import else 'Import selected', pygame.K_RETURN,
                    enabled=inbox.selected is not None and not inbox.error and not inbox.completed)
                add('refresh', 'Refresh', pygame.K_F5)
                add('other_inbox', 'Covenant inbox' if inbox.kind == 'pack' else 'Pack inbox',
                    pygame.K_i if inbox.kind == 'pack' else pygame.K_k); pages(); common()
            elif review is not None:
                add('back', 'Back', pygame.K_v)
                add('playback', 'Pause' if review_playing else 'Play', pygame.K_SPACE)
                add('previous_frame', 'Frame <', pygame.K_COMMA)
                add('next_frame', 'Frame >', pygame.K_PERIOD)
                add('report', 'Selected report', pygame.K_t); pages(); common()
            elif browser is not None:
                add('back', 'Back', pygame.K_b)
                add('previous_creature', 'Creature <', pygame.K_COMMA, enabled=browser.current() is not None)
                add('next_creature', 'Creature >', pygame.K_PERIOD, enabled=browser.current() is not None)
                add('previous_era', 'Era <', pygame.K_LEFTBRACKET)
                add('next_era', 'Era >', pygame.K_RIGHTBRACKET)
                add('adopt', 'Adopt selected', pygame.K_a, enabled=browser.current() is not None, destructive=True)
                add('report', 'Selected report', pygame.K_t)
                add('replay', 'Saved recording', pygame.K_v, enabled=browser.current() is not None)
                if not isinstance(browser, NicheHistory):
                    add('reproduce', 'Reproduce [D]', pygame.K_d, enabled=browser.selected_era is not None and not browser.error)
                add('niche_history', 'Back to archive' if isinstance(browser, NicheHistory) else 'Niche history', pygame.K_n)
                add('preparation', 'Covenant [C]', pygame.K_c, enabled=browser.allow_planning)
                add('run_era', 'Next era [E]', pygame.K_e, enabled=browser.allow_planning); pages(); common()
            elif era_review is not None:
                add('back', 'Back to care', pygame.K_t)
                add('previous_era', 'Era <', pygame.K_LEFTBRACKET)
                add('next_era', 'Era >', pygame.K_RIGHTBRACKET)
                add('previous_campaign', 'Campaign <', pygame.K_LEFTBRACKET, mod=pygame.KMOD_CTRL)
                add('next_campaign', 'Campaign >', pygame.K_RIGHTBRACKET, mod=pygame.KMOD_CTRL)
                add('archive', 'Archive [B]', pygame.K_b)
                add('replay', 'Saved recording', pygame.K_v, enabled=era_review.current is not None and not era_review.error)
                add('reproduce', 'Reproduce [D]', pygame.K_d, enabled=era_review.current is not None and not era_review.error)
                add('preparation', 'Covenant [C]', pygame.K_c, enabled=not era_review.error)
                add('run_era', 'Next era [E]', pygame.K_e, enabled=not era_review.error); pages(); common()
            elif story is not None:
                add('back', 'Back to care', pygame.K_l)
                add('previous_life', 'Life <', pygame.K_COMMA)
                add('next_life', 'Life >', pygame.K_PERIOD)
                add('report', 'Campaign story', pygame.K_t); pages(); common()
            else:
                if covenant_mode:
                    add('back', 'Back to care [C]', pygame.K_c)
                    if preparation_waiting:
                        add('finish_preparation', 'Finish saved preparation [E]', pygame.K_e,
                            enabled=not bench.preparation_commit.error)
                    for identity, label, code in (('palette','Add palette',pygame.K_1),
                        ('thinking','Spend thinking',pygame.K_2),('population','Spend population',pygame.K_3),
                        ('generations','Spend generations',pygame.K_4)):
                        add(identity,label,code,enabled=ready)
                    add('organ_role','Spend organ role [5]',pygame.K_5,enabled=ready)
                    add('density_pressure','Density: '+('on' if bench.plan.cubff_density_pressure else 'off')+' [6]',pygame.K_6,enabled=ready)
                    add('survival_regime','Survival: '+('stress probe' if bench.plan.survival_regime == 'stress_probe' else 'sheltered')+' [7]',pygame.K_7,enabled=ready)
                    if bench.new_campaign_available():
                        add('living_campaign','Start living generations [8]',pygame.K_8,enabled=ready)
                        add('role_campaign','Start with role limits [9]',pygame.K_9,enabled=ready)
                    elif bench.campaign is not None and bench.campaign.status == 'extinct':
                        add('campaign_successor','Create successor [N]',pygame.K_n,enabled=ready)
                    add('inspect_checkpoint','Inspect checkpoint',pygame.K_u)
                    add('prior_checkpoint','Inspect prior',pygame.K_y)
                    add('export_covenant','Export covenant',pygame.K_x)
                else:
                    for identity, label, code in (('feed','Feed [F]',pygame.K_f),('play','Play [P]',pygame.K_p),
                                                  ('sleep','Sleep [S]',pygame.K_s)):
                        add(identity,label,code,enabled=session.alive)
                    add('clean','Clean [G]',pygame.K_g,enabled=session.alive and 'cleanliness' in session.state)
                    if not session.alive:
                        add('successor','Adopt successor',pygame.K_RETURN,destructive=True)
                    add('preparation','Covenant [C]',pygame.K_c)
                add('run_era','Retry era save [E]' if bench.plan.pending is not None or bench._completed_work is not None else 'Run era [E]',pygame.K_e,enabled=not bench.plan.error and not preparation_waiting)
                add('report','Reports [T]',pygame.K_t)
                add('archive','Archive [B]',pygame.K_b)
                add('creator','Creator [J]',pygame.K_j)
                add('hatch','Hatch [H]',pygame.K_h,enabled=ready)
                add('origin','Saved origin [O]',pygame.K_o)
                add('lineage','Keeper lives [L]',pygame.K_l)
                add('stage_pet','Stage companion',pygame.K_r,enabled=ready)
                add('gather','Gather releases',pygame.K_w,enabled=ready)
                add('unstage','Unstage creatures',pygame.K_BACKSPACE,enabled=ready and bool(bench.plan.releases))
                if not covenant_mode:
                    for index,name in enumerate(WEATHER_NAMES):
                        add('weather_'+name,'Weather: '+name.replace('_',' '),pygame.K_1+index,enabled=ready)
                add('covenant_inbox','Covenant inbox',pygame.K_i)
                add('pack_inbox','Pack inbox',pygame.K_k); pages(); common()
            return actions

        def action_event(identity):
            code, mod = action_keys[identity]
            if code is None:
                return pygame.event.Event(pygame.QUIT)
            return pygame.event.Event(pygame.KEYDOWN, key=code, mod=mod, repeat=False)

        def finish_reading():
            # The closing key belongs to the reader, including the rest of its
            # retrieved batch. Resume care on the next frame, never this one.
            nonlocal reading_closed, queued
            reading_closed = True
            queued = None
            live_thought.clear()

        def toggle_help():
            nonlocal help_mode, help_bookmark, footer_pager, footer_context
            live_thought.clear()
            if help_mode:
                help_mode = False
                footer_pager, footer_context = help_bookmark
                help_bookmark = None
                finish_reading()
            else:
                help_bookmark = (footer_pager, footer_context)
                footer_pager, footer_context = FooterPager(), None
                help_mode = True

        def selected_inbox(kind):
            nonlocal inbox_pending_import
            inbox_pending_import = None
            if kind not in inboxes:
                inboxes[kind] = InboxPicker(keeper_dir, kind)
            else:
                inboxes[kind].refresh()
            return inboxes[kind]

        def open_creator():
            nonlocal creator_mode, creator_url, queued
            if not checkpoint():
                return
            notice = None
            try:
                bench.require_preparation()
                campaign = bench.ensure()
                bench.check_current_state()
                if not bench.state_path.exists():
                    from mecha_game.campaign_recovery import initialize_campaign_checkpoint
                    initialize_campaign_checkpoint(campaign, bench.state_path, bench.ledger_path)
                    bench._remember_files()
                if bench.bind_current_campaign() and not checkpoint():
                    return
            except (OSError, ValueError, sqlite3.Error) as error:
                # Context inspection remains useful, but the server's own
                # validators refuse writes to an unavailable campaign.
                notice = f"Keeper context unavailable: {error}. Return to C/U for recorded checkpoint recovery."
            try:
                creator_url = creator.open(open_browser=False) if args.no_browser else creator.open()
            except (OSError, ValueError, ImportError) as error:
                bench.message = f"Creator could not open: {error}"
                return
            creator_mode = True
            queued = None
            footer_pager.reset()
            bench.message = notice or "Creator opened for this Keeper."

        def help_lines():
            if creator_mode:
                return ["CREATOR HELP - care paused",
                        "Edit, preview, release and compose packs in your browser.",
                        "J or Escape returns to care; the server closes when this game exits.",
                        "This Keeper's releases are staged; W gathers them and E runs an era.",
                        "Native care/eras stay here. Browser-lab histories stay separate.",
                        "F1/Escape closes help; PgUp/PgDn reads this view."]
            if wfc is not None:
                return wfc.help_lines()
            if generation is not None:
                return generation.help_lines()
            if inbox is not None:
                return inbox.help_lines()
            common = ['F1/Escape returns to the same reading page',
                      'PgUp/PgDn or wheel pages this help; Ctrl+S saves']
            if era_review is not None:
                return ['REPORT HELP - care paused', *common,
                        '[ ] or , . select era; Ctrl+[ ] recorded campaigns',
                        'B selected archive; V original recording when saved',
                        'D explicitly reproduces recorded inputs and compares results.',
                        'Comparison pauses care; Escape cancels; originals stay unchanged.',
                        'T/Escape closes reports; C active covenant; E next era',
                        '1-5 weather; R stage pet; W gather; Backspace unstage',
                        'Preparation applies to the active campaign.',
                        'Unavailable reports permit reading and navigation only.',
                        'Campaign links do not infer ancestry.']
            if browser is not None:
                return [('NICHE HISTORY HELP' if isinstance(browser, NicheHistory) else 'ARCHIVE HELP') + ' - care paused',
                        *common, ', . select occurrences' if isinstance(browser, NicheHistory) else ', . select creatures; [ ] select era',
                        '[ ] also selects occurrences' if isinstance(browser, NicheHistory) else 'N exact seven-axis niche history',
                        'A adopts selected creature with the current covenant',
                        'V saved original recording; T selected report',
                        'D explicitly compares saved inputs in the archive view.',
                        'N/B/Escape back to archive' if isinstance(browser, NicheHistory) else 'B/Escape back',
                        'Missing recordings are not reconstructed.',
                        'Matching niche labels do not infer ancestry.']
            if review is not None:
                return ['REPLAY HELP - care and playback paused', *common,
                        'Space play/pause; . next frame; , previous frame',
                        'V/Escape back; T selected report',
                        'This is the saved recording with its original provenance.']
            if story is not None:
                return ['LINEAGE HELP - care paused', *common,
                        '. newer life; , older life; L/Escape back',
                        'T recorded campaign story',
                        'PgUp/PgDn reads all stored ancestors and mutation fields.',
                        'These are recorded facts; missing ancestry is not inferred.']
            if covenant_mode:
                return ['COVENANT HELP - care paused while help is open', *common,
                        '1 palette; 2 thinking; 3 population; 4 generations; 5 organ role',
                        'Spends use earned unlocks and save immediately.',
                        'U inspects latest checkpoint; Y inspects prior. U again restores.',
                        'Recovery inspection pauses care; C cancels without changes.',
                        'Recovery retains current bytes; C cancels inspection.',
                        '6 earned density; 7 sheltered/stress preparation.',
                        '8 new living campaign; 9 also selects four-role starter.',
                        'N explicitly creates an extinct campaign successor.',
                        'Pending preparation: E finishes its saved choice; no era runs.',
                        'U/Y inspect paired recovery before an explicit restore.',
                        'C closes; then 1-5 selects weather.',
                        'Care continues in covenant mode; F1 pauses it.',
                        'I covenant inbox; K pack inbox; X export active covenant',
                        'H constrained hatch preview; O saved origin',
                        'F feed; P play; S sleep; G clean when enabled',
                        'Escape outside help quits and saves.']
            return list(HELP_LINES)

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
            # The completed era has a saved report. Its transient notice must
            # not bury navigation in a newly opened archive.
            bench.message = None
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
            finish_reading()
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
            finish_reading()
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
                if bench.state_path.is_file() and bench.bind_current_campaign():
                    checkpoint()
            except (OSError,ValueError,sqlite3.Error) as error:
                notice = bench.preparation_failed(error)
            if era_review is not None:
                era_review.notice = notice
            footer_pager.reset()

        def import_selected():
            nonlocal inbox_pending_import
            if inbox.selected is None or inbox.error or inbox.completed:
                return
            attempted_result = None
            try:
                if inbox.kind == 'covenant':
                    if inbox_pending_import is not None:
                        if frame <= inbox_pending_import['frame']:
                            return  # A duplicate Enter cannot retry the same failing write batch.
                        if (str(inbox.selected), inbox.digest) != inbox_pending_import['selection']:
                            raise ValueError('A different selection or preview cannot finish the captured import. Escape then C/E inspects its saved choice.')
                        bench.finish_preparation(expected_journal_digest=inbox_pending_import['journal_digest'])
                        result = copy.deepcopy(inbox_pending_import['result'])
                        inbox_pending_import = None
                    else:
                        def apply_import(campaign):
                            nonlocal attempted_result
                            attempted_result = import_covenant(campaign, inbox.selected, expected_digest=inbox.digest)
                            return attempted_result
                        result = bench.change_covenant(apply_import)
                    if result['ok'] and bench.bind_current_campaign():
                        checkpoint()
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
                if inbox.kind == 'covenant':
                    notice = bench.preparation_failed(error)
                    if (attempted_result is not None and attempted_result['ok'] and
                            bench._pending_preparation_digest is not None and
                            bench.preparation_commit.journal_digest == bench._pending_preparation_digest):
                        inbox_pending_import = dict(selection=(str(inbox.selected), inbox.digest),
                            journal_digest=bench._pending_preparation_digest,
                            result=copy.deepcopy(attempted_result), frame=frame)
                    retry_this_import = (inbox_pending_import is not None and
                        (str(inbox.selected), inbox.digest) == inbox_pending_import['selection'] and
                        bench.preparation_commit.journal_digest == inbox_pending_import['journal_digest'] and
                        not bench.preparation_commit.error)
                    if retry_this_import:
                        inbox_pending_import['frame'] = frame
                    inbox.result_lines = ['Import not completed.',
                        ('Enter finishes this captured import; no new import or era runs.' if retry_this_import else
                         'Escape returns; C opens saved preparation and recovery controls.'), notice]
                else:
                    inbox.result_lines = [f'Import not completed: {error}', 'Fix the problem; Enter retries.']
            footer_pager.reset()

        def open_hatch():
            nonlocal generation, hatch_count, queued
            queued = None
            try:
                bench.require_preparation()
                bench.ensure()
                bench.check_current_state()
                hatch_count += 1
                hatched = bench.hatch(20260713 + hatch_count)
                generation = GenerationView(hatched['grid'], bench.active_covenant(), adoptable=True)
            except (OSError, ValueError, sqlite3.Error) as error:
                generation = GenerationView(adoptable=True, error=f'Hatch unavailable: {error}. N retries.')
            footer_pager.reset()

        def open_wfc(initial_events=()):
            nonlocal wfc, wfc_count, running, queued
            queued = None
            wfc_count += 1
            work = wfc_trace.WfcWork(lambda events: wfc_trace.capture_wfc(
                bench.ensure().inputs['seed_grids'], f'mg_wfc_preview_{wfc_count:03}', 20261005 + wfc_count, events))
            busy_help = False
            busy_strip = ActionStrip([UiAction('cancel_work', 'Cancel capture'), UiAction('help_work', 'Help [F1]')], allow_tab=False)
            pending = list(initial_events)
            work.start()
            try:
                while True:
                    event = pygame.event.poll()
                    while event.type != pygame.NOEVENT:
                        pending.append(event)
                        event = pygame.event.poll()
                    for event in pending:
                        busy_strip.set_actions([UiAction('cancel_work', 'Cancel capture', enabled=not work.cancelled),
                                                UiAction('help_work', 'Back' if busy_help else 'Help [F1]')])
                        if resize_event(event):
                            busy_strip._armed = False
                            continue
                        if event.type in (pygame.KEYUP, pygame.WINDOWFOCUSLOST):
                            action_strip.handle(event)
                        result = busy_strip.handle(event)
                        if result.action:
                            event = pygame.event.Event(pygame.KEYDOWN,
                                key=pygame.K_ESCAPE if result.action == 'cancel_work' else pygame.K_F1, mod=0)
                            busy_strip.blur()
                        elif result.consumed:
                            continue
                        if event.type == pygame.QUIT:
                            running = False
                            work.cancel()
                        elif event.type == pygame.KEYDOWN:
                            if event.key in (pygame.K_ESCAPE, pygame.K_TAB):
                                work.cancel()
                            elif event.key == pygame.K_F1:
                                busy_help = not busy_help
                    pending = []
                    window.fill((16, 18, 16))
                    lines = ['WFC CAPTURE - care paused', f'{len(work.events)} engine events captured',
                             'Finishing current call before closing.' if work.cancelled else 'Escape cancels this view; close quits.',
                             'Closing waits for the worker; saves stay unchanged.',
                             'F1: read-only observations; no RNG or generator decisions changed.' if busy_help else 'F1 capture help']
                    paint_footer(lines, FooterPager())
                    busy_strip.set_actions([UiAction('cancel_work', 'Cancel capture', enabled=not work.cancelled),
                                            UiAction('help_work', 'Back' if busy_help else 'Help [F1]')])
                    busy_strip.draw(window, font, layout.actions_rect)
                    pygame.display.flip()
                    if work.done.is_set():
                        break
                    clock.tick(60)
            finally:
                work.join()
            if not work.cancelled and running:
                wfc = wfc_trace.WfcTraceView(work.grid, work.events, error=work.error)
            footer_pager.reset()

        def adopt_hatch():
            nonlocal generation, session, ghost, driver, queued, covenant_mode
            if not generation.adoptable or generation.grid is None or generation.error:
                return
            try:
                bench.require_preparation()
                bench.check_current_state()
                if bench.active_covenant() != generation.profile:
                    raise ValueError('Covenant changed since preview; N generates a new candidate.')
                candidate = session.adopt(generation.grid, generation.profile,
                    model=train_generation_model([generation.grid]), name=generation.grid['grid_id'],
                    origin='hatched', source={'campaign_id': bench.ensure().campaign['campaign_id']})
                candidate.bind_campaign(bench.ensure().campaign['campaign_id'],
                    predecessor_campaign_id=bench.ensure().campaign.get('predecessor_campaign_id'))
            except (OSError, ValueError, sqlite3.Error) as error:
                generation.notice = f'Adoption refused: {error}'
                footer_pager.reset()
                return
            if not checkpoint():
                return
            session = candidate
            bench.keeper_session = session
            generation = None
            queued = ghost = None
            covenant_mode = False
            driver = ClipDriver(driver.frame_counts)
            pygame.display.set_caption(f"{WINDOW_TITLE} - {session.name}")
            bench.message = f'Adopted hatched founder {session.name}. O reads its saved origin.'
            checkpoint()

        era_ran_frame = False

        def wait_for_era(work, initial_events, *, reproducing=False):
            """Keep SDL on its main thread while an explicit era owns the bench."""
            nonlocal running
            held_surface = window.subsurface(layout.lcd_rect).copy()
            if frame == 0:
                # E can arrive before the ordinary loop has painted once. Draw
                # the actual held state without stepping care or the clip clock.
                packet = session.packet_for(session.desired_clip(), 0)
                held = compose_frame(packet, previous_ghost=None, cell_px=cell_px)
                snapshot = session.snapshot()
                hud = render_hud(session.state, snapshot["ui_hints"], width=width,
                                 palette=packet["palette"], frame=frame)
                lcd = stack_buffers(held.pixels, apply_scanline(
                    scale_buffer(hud, cell_px), period=2, opacity=0.12))
                held_surface = pygame.image.frombytes(_frame_bytes(lcd),
                    (width * cell_px, panel_px + hud_px), "RGB")
            pager = FooterPager()
            cancel_label = 'Cancel reproduction' if reproducing else 'Cancel era'
            heading = 'REPRODUCING ERA' if reproducing else 'ERA RUNNING'
            busy_strip = ActionStrip([UiAction('cancel_work', cancel_label), UiAction('help_work', 'Help [F1]'),
                                      UiAction('previous_page', 'Text <'), UiAction('next_page', 'Text >')], allow_tab=False)
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
                        current_status = work.snapshot()
                        busy_strip.set_actions([UiAction('cancel_work', 'Back from help' if busy_help else cancel_label,
                                                enabled=busy_help or (not current_status['cancelling'] and not current_status['committing'])),
                                                UiAction('help_work', 'Back' if busy_help else 'Help [F1]'),
                                                UiAction('previous_page', 'Text <'), UiAction('next_page', 'Text >')])
                        if resize_event(event):
                            busy_strip._armed = False
                            event = next_work_event()
                            continue
                        if event.type in (pygame.KEYUP, pygame.WINDOWFOCUSLOST):
                            action_strip.handle(event)
                        result = busy_strip.handle(event)
                        if result.action:
                            event = pygame.event.Event(pygame.KEYDOWN, key={
                                'cancel_work': pygame.K_ESCAPE, 'help_work': pygame.K_F1,
                                'previous_page': pygame.K_PAGEUP, 'next_page': pygame.K_PAGEDOWN}[result.action], mod=0)
                            busy_strip.blur()
                        elif result.consumed:
                            event = next_work_event()
                            continue
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
                    lines = [heading + ' - care paused', status['phase']]
                    if status['budget'] is not None:
                        lines.append(f"Evaluations {status['completed']}/{status['budget']} completed")
                    if status['cancelling']:
                        lines.append('Cancel requested; finishing the current step.')
                    elif status['committing']:
                        lines.append('Saving result; please wait.')
                    else:
                        lines.append('Escape cancel   F1 help')
                    if close_requested:
                        lines.append('Closing after comparison stops; original results are unchanged.' if reproducing else
                                     'Closing after work stops; companion will be saved.')
                    if busy_help:
                        lines = [heading + ' - help; care paused',
                                 'F1/Escape close help; Escape outside help cancels',
                                 'Close cancels computation, waits, then quits',
                                 'Cancellation waits for the current candidate' if reproducing else 'Cancellation waits for model load/current candidate',
                                 'Comparison never saves or replaces original results' if reproducing else 'Completed-result saving cannot be cancelled',
                                 'Other commands are ignored, never queued',
                                 'Counts are completed candidates, not time estimates']
                    window.fill((16, 18, 16))
                    held = (held_surface if held_surface.get_size() == layout.lcd_rect.size else
                            pygame.transform.scale(held_surface, layout.lcd_rect.size))
                    window.blit(held, layout.lcd_rect)
                    paint_footer(lines, pager)
                    busy_strip.set_actions([UiAction('cancel_work', 'Back from help' if busy_help else cancel_label,
                                            enabled=busy_help or (not status['cancelling'] and not status['committing'])),
                                            UiAction('help_work', 'Back' if busy_help else 'Help [F1]'),
                                            UiAction('previous_page', 'Text <'), UiAction('next_page', 'Text >')])
                    busy_strip.draw(window, font, layout.actions_rect)
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

        def reproduce_selected_era(initial_events=()):
            nonlocal era_ran_frame, queued
            from mecha_game.execution_readout import reproduce_saved_era, comparison_notice
            target = era_review if era_review is not None else browser
            era = era_review.current if era_review is not None else browser.selected_era
            if era is None or target.error:
                return
            campaign_id = era_review.history['campaign_id'] if era_review is not None else browser.campaign_id
            era_index = era['era_index']
            era_ran_frame = True
            queued = None
            def operation(work):
                work.phase('Reading immutable recorded inputs')
                return reproduce_saved_era(keeper_dir, campaign_id, era_index, progress_callback=work.progress)
            try:
                result = wait_for_era(EraWork(operation), initial_events, reproducing=True)
                notice = comparison_notice(result)
            except EraCancelled:
                notice = 'Reproduction cancelled; original results, footage and preparation are unchanged.'
            except (OSError, ValueError, sqlite3.Error) as error:
                notice = f'Reproduction unavailable: {error}. Original results and footage are unchanged.'
            if era_review is not None:
                era_review.notice = notice
            else:
                browser.replay_notice = notice
            footer_pager.reset()

        def run_prepared_era(initial_events=()):
            nonlocal era_ran_frame
            era_ran_frame = True
            try:
                if args.eras is not None:
                    bench.run_era(campaign_ledger)
                else:
                    wait_for_era(EraWork(lambda work: bench.run_era(campaign_ledger, work=work)), initial_events)
                bench.ensure()
                if bench.bind_current_campaign() and not checkpoint():
                    return False
            except EraCancelled as error:
                bench.message = str(error)
                if era_review is not None:
                    era_review.notice = bench.message
                return False
            except (OSError,ValueError,sqlite3.Error) as error:
                if preparation_notice(bench.preparation_commit):
                    bench.preparation_failed(error)
                else:
                    bench.message = f'Era not completed: {error}. E retries; saved progress is retained.'
                if era_review is not None:
                    era_review.notice = bench.message
                return False
            if args.ticks is None and running:
                open_era_review()
            return True

        def record_launch():
            if receipt.path is None:
                return
            actual_view = ('creator' if creator_mode else 'review' if era_review is not None else
                           'archive' if browser is not None else 'preparation' if covenant_mode else 'care')
            values = dict(view=actual_view, runtime=inspect_runtime(), keeper_id=session.keeper_id,
                          campaign_id=session.campaign_id, learning_policy=session.learning_policy,
                          display=dict(driver=pygame.display.get_driver(), size=list(window.get_size()),
                                       resizable=bool(window.get_flags() & pygame.RESIZABLE)))
            if era_review is not None:
                current = era_review.current
                values['review'] = dict(campaign_id=era_review.history.get('campaign_id'),
                    era_count=len(era_review.history['eras']), current_era_index=current.get('era_index') if current else None,
                    weather=current.get('weather') if current else None, lines=era_review.lines())
                if era_review.error:
                    values.update(startup_outcome='refused', reason=era_review.error)
            if browser is not None:
                values['archive'] = dict(campaign_id=browser.campaign_id, era_index=browser.era_index,
                                        entry_count=len(browser.elites), error=browser.error)
                if browser.error:
                    values.update(startup_outcome='refused', reason=browser.error)
            if creator_mode:
                from urllib.request import urlopen
                values['creator_url'] = creator_url
                try:
                    with urlopen(creator_url + 'api/context', timeout=5) as response:
                        values['context'] = json.load(response)
                except (OSError, ValueError) as error:
                    values['context'] = {'available': False, 'reason': str(error)}
            receipt.update(**values)

        try:
            if args.finish_preparation:
                bench.finish_preparation()
                if bench.bind_current_campaign() and not checkpoint(): return 2
            if args.population_policy is not None or args.campaign_seed is not None or args.starter_roles:
                bench.choose_new_campaign(args.population_policy or 'legacy_archive',
                    starter_roles=args.starter_roles, base_seed=args.campaign_seed)
                if bench.bind_current_campaign() and not checkpoint(): return 2
            if args.create_successor:
                bench.create_successor()
                if bench.bind_current_campaign() and not checkpoint(): return 2
            if args.prepare_survival_regime is not None:
                bench.choose_survival_regime(args.prepare_survival_regime)
            if args.prepare_density_pressure == 'off':
                bench.choose_density_pressure(False)
        except (OSError, ValueError, sqlite3.Error) as error:
            receipt.update(startup_outcome='refused', reason=str(error))
            print(f'Preparation refused: {error}', file=sys.stderr)
            return 2

        if args.prepare_weather is not None:
            try:
                bench.choose_weather(WEATHER_NAMES.index(args.prepare_weather))
            except (OSError, ValueError, sqlite3.Error) as error:
                receipt.update(startup_outcome='refused', reason=str(error))
                print(f'Preparation refused: {error}', file=sys.stderr)
                return 2

        if args.prepare_density_pressure == 'on':
            try:
                bench.choose_density_pressure(True)
            except (OSError, ValueError, sqlite3.Error) as error:
                receipt.update(startup_outcome='refused', reason=str(error))
                print(f'Preparation refused: {error}', file=sys.stderr)
                return 2

        # Headless verification: run the requested eras up front.
        if args.eras is not None:
            for _ in range(args.eras):
                if not run_prepared_era():
                    print(bench.message,file=sys.stderr)
                    return 2
        if args.creator:
            open_creator()
            if not creator_mode:
                receipt.update(startup_outcome='refused', reason=bench.message)
                return 2
        elif args.view == 'review':
            open_era_review()
        elif args.view == 'archive':
            open_archive()
        elif args.view == 'preparation':
            covenant_mode = True
        record_launch()
        held_preparation_keys = set()
        while running:
            reading_closed = False
            era_ran_frame = False
            help_was_open = help_mode
            inbox_was_open = inbox is not None
            generation_was_open = generation is not None
            wfc_was_open = wfc is not None
            generation_touched = generation_was_open
            action_strip.set_actions(native_actions())
            navigation_paused = action_strip.focus_active
            navigation_acted = False
            event_batch = pygame.event.get()
            for event_index, event in enumerate(event_batch):
                from_native_action = False
                if event.type == pygame.KEYUP:
                    held_preparation_keys.discard(getattr(event, 'key', None))
                elif event.type == pygame.WINDOWFOCUSLOST:
                    held_preparation_keys.clear()
                # A raw shortcut may have changed modes earlier in this batch.
                # Reconcile/disarm old drawn controls before any later pointer
                # activation can reinterpret their key in the new mode.
                action_strip.set_actions(native_actions())
                if resize_event(event):
                    navigation_paused = True
                    continue
                if event.type != pygame.QUIT:
                    result = action_strip.handle(event)
                    navigation_paused = navigation_paused or result.consumed or result.focus_active
                    if navigation_acted:
                        continue
                    if result.action:
                        event = action_event(result.action)
                        from_native_action = True
                        action_strip.blur()
                        navigation_acted = True
                    elif result.consumed or (navigation_paused and event.type == pygame.KEYDOWN):
                        continue
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEWHEEL:
                    if wfc is not None:
                        wfc.playing = False
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
                    elif reading_closed:
                        continue
                    elif event.key == pygame.K_F1:
                        toggle_help()
                    elif help_mode:
                        if event.key == pygame.K_ESCAPE:
                            toggle_help()
                        elif event.key == pygame.K_PAGEUP:
                            footer_pager.move(-1)
                        elif event.key == pygame.K_PAGEDOWN:
                            footer_pager.move(1)
                    elif creator_mode:
                        if getattr(event, 'repeat', False) and event.key in (pygame.K_j, pygame.K_ESCAPE, pygame.K_RETURN):
                            continue
                        if event.key in (pygame.K_j, pygame.K_ESCAPE):
                            creator_mode = False
                            finish_reading()
                        elif event.key == pygame.K_RETURN:
                            open_creator()
                        elif event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                            footer_pager.move(-1 if event.key == pygame.K_PAGEUP else 1)
                    elif bench.recovery_offer is not None and event.key not in (
                        pygame.K_u, pygame.K_y, pygame.K_c, pygame.K_ESCAPE,
                        pygame.K_PAGEUP, pygame.K_PAGEDOWN,
                    ):
                        continue
                    elif wfc is not None:
                        if event.key in (pygame.K_ESCAPE, pygame.K_TAB):
                            wfc = None
                            finish_reading()
                        elif event.key == pygame.K_n and not getattr(event, 'repeat', False):
                            open_wfc(event_batch[event_index + 1:])
                            break
                        elif event.key == pygame.K_SPACE:
                            wfc.playing = not wfc.playing
                        elif event.key in (pygame.K_COMMA, pygame.K_PERIOD):
                            wfc.playing = False
                            wfc.step(-1 if event.key == pygame.K_COMMA else 1)
                        elif event.key in (pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET):
                            wfc.move_attempt(-1 if event.key == pygame.K_LEFTBRACKET else 1)
                        elif event.key in (pygame.K_HOME, pygame.K_END):
                            wfc.playing = False
                            wfc.index = 0 if event.key == pygame.K_HOME else max(0, len(wfc.events) - 1)
                        elif event.key == pygame.K_v:
                            wfc.toggle_final()
                        elif event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                            wfc.playing = False
                            footer_pager.move(-1 if event.key == pygame.K_PAGEUP else 1)
                    elif wfc_was_open:
                        continue
                    elif generation is not None:
                        if event.key == pygame.K_ESCAPE or event.key == (pygame.K_h if generation.adoptable else pygame.K_o):
                            generation = None
                            finish_reading()
                        elif event.key == pygame.K_TAB and generation.adoptable:
                            open_wfc(event_batch[event_index + 1:])
                            break
                        elif event.key == pygame.K_RETURN and not getattr(event, 'repeat', False):
                            adopt_hatch()
                        elif event.key == pygame.K_n and generation.adoptable and not getattr(event, 'repeat', False):
                            open_hatch()
                        elif event.key == pygame.K_SPACE:
                            generation.playing = not generation.playing
                        elif event.key in (pygame.K_COMMA, pygame.K_PERIOD):
                            generation.playing = False
                            generation.step(-1 if event.key == pygame.K_COMMA else 1)
                        elif event.key in (pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET):
                            generation.move_clip(-1 if event.key == pygame.K_LEFTBRACKET else 1)
                        elif event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
                            footer_pager.move(-1 if event.key == pygame.K_PAGEUP else 1)
                    elif generation_touched:
                        continue  # No care/adoption leaks out of a closed preview batch.
                    elif inbox is not None:
                        if event.key == pygame.K_ESCAPE or event.key == (pygame.K_i if inbox.kind == 'covenant' else pygame.K_k):
                            inbox = None
                            finish_reading()
                        elif event.key in (pygame.K_i, pygame.K_k):
                            inbox = selected_inbox('covenant' if event.key == pygame.K_i else 'pack')
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
                            finish_reading()
                    elif review is not None and event.key == pygame.K_ESCAPE:
                        close_review()
                    elif review is not None and event.key not in (
                        pygame.K_SPACE, pygame.K_PERIOD, pygame.K_COMMA, pygame.K_PAGEUP, pygame.K_PAGEDOWN,
                    ):
                        continue
                    elif event.key == pygame.K_d and not getattr(event, 'repeat', False) and (
                        era_review is not None or (browser is not None and not isinstance(browser, NicheHistory))):
                        reproduce_selected_era(event_batch[event_index + 1:])
                        break
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
                        finish_reading()
                    elif era_review is not None and event.key == pygame.K_c:
                        if not era_review.error:
                            era_review = None
                            covenant_mode = True
                            finish_reading()
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
                        finish_reading()
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
                    elif event.key == pygame.K_j and not getattr(event, 'repeat', False):
                        open_creator()
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
                        if (getattr(event, 'repeat', False) or
                                (not from_native_action and event.key in held_preparation_keys)):
                            continue
                        if covenant_mode:
                            if not from_native_action:
                                held_preparation_keys.add(event.key)
                            prepare(bench.finish_preparation)
                        else:
                            run_prepared_era(event_batch[event_index + 1:])
                            break  # The waiting loop consumed the rest of this batch.
                    elif event.key == pygame.K_h:
                        generation_touched = True
                        open_hatch()
                    elif event.key == pygame.K_o:
                        generation_touched = True
                        generation = GenerationView(session.grid, session.slip_profile)
                        queued = None
                        footer_pager.reset()
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
                        if story is not None:
                            finish_reading()
                        story = (
                            None
                            if story is not None
                            else LineageBrowser(session.lineage, chronicle=session.chronicle)
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
                        inbox = selected_inbox('pack')
                        queued = None
                    elif event.key == pygame.K_x:
                        # Export the ACTIVE covenant (spends included)
                        # as a shareable SLIP file (F15).
                        try:
                            exported = export_covenant(bench.ensure(),
                                keeper_dir / "covenants" / "covenant_export.json")
                            bench.message = f"covenant exported: {exported.name}"
                        except (OSError, ValueError, sqlite3.Error) as error:
                            bench.message = f"Export not completed: {error}"
                        footer_pager.reset()
                    elif event.key == pygame.K_i:
                        inbox = selected_inbox('covenant')
                        queued = None
                    elif event.key == pygame.K_BACKSPACE:
                        prepare(bench.unstage)
                    elif event.key == pygame.K_w:
                        prepare(lambda: bench.stage_releases(*gather_release_inputs(keeper_dir, include_shared=False)))
                    elif event.key == pygame.K_r:
                        prepare(lambda: bench.stage_releases([session.grid], [companion_release_source(session)]))
                    elif event.key == pygame.K_c:
                        if browser is not None:
                            browser = archive_return = None
                            finish_reading()
                        covenant_mode = not covenant_mode
                        if bench.recovery_offer is not None:
                            finish_reading()
                        bench.recovery_offer = None
                        recovery_inspected_frame = None
                    elif covenant_mode and event.key in (pygame.K_u, pygame.K_y) and not getattr(event, 'repeat', False):
                        try:
                            if bench.recovery_offer is None or event.key == pygame.K_y:
                                bench.inspect_recovery(slot='previous' if event.key == pygame.K_y else 'current')
                                recovery_inspected_frame = frame
                                bench.message = 'Inspect the recovery checkpoint below; nothing has changed.'
                            elif recovery_inspected_frame is not None and frame > recovery_inspected_frame:
                                bench.restore_recovery()
                                finish_reading()
                                recovery_inspected_frame = None
                                if bench.bind_current_campaign():
                                    checkpoint()
                        except (OSError, ValueError, sqlite3.Error) as error:
                            bench.recovery_offer = None
                            recovery_inspected_frame = None
                            bench.message = f'Recovery not completed: {error}'
                            finish_reading()
                        queued = None
                        footer_pager.reset()
                    elif covenant_mode and event.key in (pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_n) and not getattr(event, 'repeat', False):
                        if event.key == pygame.K_6:
                            prepare(lambda: bench.choose_density_pressure(not bench.plan.cubff_density_pressure))
                        elif event.key == pygame.K_7:
                            prepare(lambda: bench.choose_survival_regime('sheltered' if bench.plan.survival_regime == 'stress_probe' else 'stress_probe'))
                        elif event.key in (pygame.K_8, pygame.K_9):
                            prepare(lambda: bench.choose_new_campaign('generation_survivors_v1', starter_roles=event.key == pygame.K_9))
                        else:
                            prepare(bench.create_successor)
                    elif covenant_mode and event.key in (
                        pygame.K_1,
                        pygame.K_2,
                        pygame.K_3,
                        pygame.K_4,
                        pygame.K_5,
                    ):
                        if (getattr(event, 'repeat', False) or
                                (not from_native_action and event.key in held_preparation_keys)):
                            continue
                        if not from_native_action:
                            held_preparation_keys.add(event.key)
                        prepare(lambda: bench.spend(event.key - pygame.K_1))
                    elif not covenant_mode and event.key in (
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
                        try:
                            campaign = bench.ensure()
                            bench.check_current_state()
                            source = {'campaign_id': (browser.campaign_id if browser is not None
                                                      else campaign.campaign['campaign_id'])}
                            if browser is not None and browser.selected_era is not None:
                                source['era_index'] = browser.selected_era['era_index']
                            elif browser is None and campaign.eras:
                                source['era_index'] = campaign.eras[-1]['era_index']
                            adopted = session.adopt(
                                elite, campaign.campaign['slip_profile'], model=session.model,
                                name=elite['grid_id'], origin='era_elite', source=source)
                            adopted.bind_campaign(campaign.campaign['campaign_id'],
                                predecessor_campaign_id=campaign.campaign.get('predecessor_campaign_id'))
                        except (OSError, ValueError, sqlite3.Error) as error:
                            bench.message = "Adoption refused: " + str(error)
                            continue
                        if not checkpoint():
                            continue
                        session = adopted
                        bench.keeper_session = session
                        browser = archive_return = None
                        ghost = None
                        driver = ClipDriver(driver.frame_counts)
                        pygame.display.set_caption(f"{WINDOW_TITLE} - {session.name}")
                        bench.message = f"Adopted {elite['grid_id']}."
                        checkpoint()

            if (
                running
                and not era_ran_frame
                and not reading_closed
                and not navigation_paused
                and not action_strip.focus_active
                and not save_failed
                and bench.recovery_offer is None
                and not help_mode
                and not creator_mode
                and inbox is None
                and generation is None
                and not generation_touched
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
                live_thought.observe(session.snapshot())
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

            if wfc is not None:
                if wfc.playing and not help_mode and not help_was_open and not navigation_paused and wfc_was_open and frame % 2 == 0:
                    wfc.step(1)
                if wfc.final:
                    pixels = compose_frame(wfc.packet(), previous_ghost=None, cell_px=cell_px).pixels
                else:
                    pixels = wfc.pixels(cell_px)
                panel = fit_recorded_panel(pixels, width, height, cell_px)
                blank_hud = tuple(tuple((16, 18, 16) for _ in range(width * cell_px)) for _ in range(hud_px))
                lcd = stack_buffers(panel, blank_hud)
                snapshot = session.snapshot()
            elif generation is not None:
                if generation.playing and not help_mode and not help_was_open and not navigation_paused and generation_was_open and frame % 2 == 0:
                    generation.step(1)
                packet = generation.packet()
                pixels = (compose_frame(packet, previous_ghost=None, cell_px=cell_px).pixels
                          if packet is not None else tuple(tuple((16, 18, 16) for _ in range(width)) for _ in range(height)))
                panel = fit_recorded_panel(pixels, width, height, cell_px)
                blank_hud = tuple(tuple((16, 18, 16) for _ in range(width * cell_px)) for _ in range(hud_px))
                lcd = stack_buffers(panel, blank_hud)
                snapshot = session.snapshot()
            elif browser is not None:
                # The repertoire window: the elite's real packet under
                # the campaign's covenant, statically composed.
                packet = browser.packet()
                if packet is None:
                    archive_pixels = tuple(tuple((16, 18, 16) for _ in range(width * cell_px))
                                           for _ in range(panel_px))
                else:
                    archive_pixels = compose_frame(packet, previous_ghost=None, cell_px=cell_px).pixels
                blank_hud = tuple(
                    tuple(
                        (16, 18, 16) for _ in range(width * cell_px)
                    )
                    for _ in range(HUD_HEIGHT * cell_px)
                )
                lcd = stack_buffers(archive_pixels, blank_hud)
                snapshot = session.snapshot()
            elif review is not None:
                # The Review window: recorded body states, raw and
                # honestly effect-free (v1 packets declare none); the
                # wound frames wear the damage event's own cells.
                if review_playing and not help_mode and not help_was_open and not navigation_paused and frame % 2 == 0:
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
                panel = fit_recorded_panel(raster, width, height, cell_px)
                blank_hud = tuple(
                    tuple((16, 18, 16) for _ in range(width * cell_px))
                    for _ in range(HUD_HEIGHT * cell_px)
                )
                lcd = stack_buffers(panel, blank_hud)
                snapshot = session.snapshot()
            else:
                clip, frame_index = driver.step(session.desired_clip())
                displayed_clip = clip
                packet = session.packet_for(clip, frame_index)
                composed = compose_frame(
                    packet, previous_ghost=ghost, cell_px=cell_px
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
                    scale_buffer(hud, cell_px),
                    period=2,
                    opacity=0.12,
                )
                lcd = stack_buffers(composed.pixels, hud_scaled)
            surface = pygame.image.frombytes(
                _frame_bytes(lcd),
                (width * cell_px, panel_px + hud_px),
                "RGB",
            )
            window.fill((16, 18, 16))
            window.blit(surface, layout.lcd_rect)
            if not running or save_failed:
                live_thought.clear()
            footer = _footer_lines(snapshot, queued, thought_lines=live_thought.lines(snapshot))
            if help_mode:
                footer = help_lines()
            elif creator_mode:
                footer = ["CREATOR - this Keeper; care paused",
                          str(keeper_dir.resolve()), creator_url or "No browser URL",
                          "J/Escape back to care; Enter reopens browser; F1 help",
                          "Create or remix, preview, release, and exchange named packs.",
                          "W gathers this Keeper's released creatures after returning.",
                          "E runs the prepared era; T shows actual admission and results.",
                          "Workshop closes when this game exits. Unsaved drafts stay here."]
            elif wfc is not None:
                footer = wfc.lines()
            elif generation is not None:
                footer = generation.lines()
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
                    ". newer  , older  L/Escape back   F1 help",
                    "Care paused. T recorded campaign story",
                    *story.detail_lines(),
                ]
            elif browser is not None:
                footer = [("NICHE HISTORY  " if isinstance(browser, NicheHistory) else "REPERTOIRE  ") + browser.caption()]
                footer.append("N/B/Escape back; F1 help; , . occurrences" if isinstance(browser, NicheHistory) else "N niche history   B/Escape back   F1 help")
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
                        "T selected report   campaign " + str(browser.campaign_id),
                        browser.axes_line(), browser.components_line(),
                    ])
                if isinstance(browser, NicheHistory):
                    footer.extend(browser.history_lines())
                else:
                    footer.extend(browser.execution_lines())
            elif review is not None:
                footer = [
                    f"REVIEW ERA {review_context.current['era_index']}  {review.replay['creature']['grid_id']}",
                    review.caption(),
                    *review.thought_lines(),
                    "Care paused. SPACE play/pause  . step  , back",
                    "V/Escape back   T selected report   F1 controls",
                    review.replay.get("honest_label", "Saved recording; its original provenance label was not stored."),
                ]
            elif covenant_mode:
                footer = [*bench.budget_lines(), bench.preparation_line(), *footer]
            else:
                footer.extend([bench.preparation_line(),
                    "J creator   H hatch preview   O origin   F1 controls",
                    "Ctrl+S save  T report  E era  C covenant",
                    bench.preparation_controls()])
            if bench.message and not help_mode and (inbox is None or save_failed) and (generation is None or save_failed) and ((era_review is None and review is None) or save_failed):
                footer.insert(0, bench.message)
            context = ('help' if help_mode else 'creator' if creator_mode else 'wfc' if wfc is not None else 'generation' if generation is not None else 'inbox' if inbox is not None else 'era_report' if era_review is not None else 'lineage' if story is not None else
                       'repertoire' if browser is not None else 'review' if review is not None else
                       'covenant' if covenant_mode else 'play', bench.message, (id(wfc), wfc.final, None if wfc.final else wfc.index) if wfc is not None else (id(generation), generation.notice) if generation is not None else (inbox.kind, inbox.index, inbox.digest, inbox.error, tuple(inbox.result_lines)) if inbox is not None else era_review.index if era_review is not None else
                       (browser.campaign_id, browser.era_index, browser.index, isinstance(browser, NicheHistory)) if browser is not None else story.index if story is not None else None)
            if context != footer_context:
                footer_pager.reset()
                footer_context = context
            if navigation_paused or action_strip.focus_active:
                footer.insert(0, 'NAVIGATION - care paused; Escape returns to the current view.')
            drawn_footer = paint_footer(footer, footer_pager)
            action_strip.set_actions(native_actions())
            action_strip.draw(window, font, layout.actions_rect)
            pygame.display.flip()
            if receipt.path is not None:
                # Bounded, explicit diagnostic evidence of text actually drawn;
                # it is outside save data and never claims OS input observation.
                observation = dict(life_id=snapshot.get('life_id'), age_ticks=snapshot['age_ticks'],
                    session_tick=snapshot['session_tick'], view=context[0],
                    size=list(window.get_size()), footer_lines=list(drawn_footer.lines))
                observed = list(receipt.document.get('native_readout', []))
                if not observed or observed[-1] != observation:
                    omitted = receipt.document.get('native_readout_omitted', 0)
                    observed.append(observation)
                    if len(observed) > 32:
                        observed = observed[-32:]
                        omitted += 1
                    receipt.update(native_readout=observed, native_readout_omitted=omitted)
            frame += 1
            if args.frames is not None and frame >= args.frames:
                running = False
            clock.tick(args.fps)
            if save_failed and (args.ticks is not None or args.frames is not None):
                return 1
            if not running:
                if checkpoint():
                    return 0
                if args.ticks is not None or args.frames is not None:
                    return 1
                quit_after_retry = True
                running = True
        return 0
    finally:
        try:
            creator.close()
        finally:
            pygame.quit()
