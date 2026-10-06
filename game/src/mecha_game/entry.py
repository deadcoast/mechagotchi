"""Native entry choices over existing read-only save/recovery authority."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from mecha_game.session import load_session_inputs
from mecha_game.startup import inspect_home, resume_session, restore_session, resolve_new_learning_policy


@dataclass(frozen=True)
class EntrySelection:
    session: object
    home: Path
    notice: str | None = None
    from_menu: bool = False


def _facts(inspection, entered_play=False):
    return {'primary_status': inspection.primary.status, 'backup_status': inspection.backup.status,
            'available_actions': list(inspection.actions), 'entered_play': entered_play}


def choose_entry(args, *, default_home, default_paths, new_session, receipt):
    """Return (selection, exit code); inspecting or cancelling never writes saves."""
    inspection = inspect_home(args.keeper_dir or default_home())
    home = inspection.home
    receipt.update(keeper_dir=str(home), startup=_facts(inspection))
    interactive = (args.startup or (args.keeper_dir is None and args.ticks is None
                   and args.eras is None and not args.new and not args.recover_backup
                   and not args.creator and args.view == 'care'))
    error = None
    care_options = {}
    if getattr(args, 'care_selection', None) is not None:
        care_options['care_selection_policy'] = args.care_selection
    if getattr(args, 'care_evaluator', None) is not None:
        care_options['care_evaluator'] = args.care_evaluator

    if getattr(args, 'body_response', None) is not None:
        care_options['body_response'] = args.body_response

    def effective_new_body(selected):
        requested = getattr(args, 'body_response', None)
        if requested is not None: return requested
        prior = selected.primary if selected.primary.status == 'valid' else selected.backup
        return getattr(prior, 'body_response', None) or 'legacy'

    built_in_inputs = args.seed is None and args.slip is None

    def effective_new_policy(selected):
        resolved = resolve_new_learning_policy(selected, requested_policy=args.learning_policy,
                                              built_in_inputs=built_in_inputs)
        if resolved is not None:
            return resolved
        prior = selected.primary if selected.primary.status == 'valid' else selected.backup
        return prior.learning_policy

    def create(selected, requested_policy=None, requested_body=None):
        policy = resolve_new_learning_policy(selected,
            requested_policy=args.learning_policy if requested_policy is None else requested_policy,
            built_in_inputs=built_in_inputs)
        seed, slip = args.seed, args.slip
        if seed is None or slip is None:
            default_seed, default_slip = default_paths()
            seed, slip = seed or default_seed, slip or default_slip
        grid, profile, model = load_session_inputs(seed, slip)
        return new_session(selected.home / 'companion.json', grid, profile, model,
                           policy, inspection=selected, **(care_options if requested_body is None else
                           {**care_options, 'body_response': requested_body}))

    if not interactive:
        try:
            if args.slip is not None and inspection.primary.status != 'missing' and not args.new:
                raise ValueError('--slip selects a new companion; use --new or a separate --keeper-dir to preserve the existing save')
            notice = None
            if args.recover_backup:
                session, archive = restore_session(inspection, learning_policy=args.learning_policy, **care_options)
                notice = 'Recovered prior save.' + (f' Previous primary retained as {archive.name}.' if archive else '')
            elif args.new:
                session = create(inspection)
            elif inspection.primary.status == 'valid':
                session = resume_session(inspection, learning_policy=args.learning_policy, **care_options)
            elif inspection.primary.status == 'missing' and inspection.backup.status == 'missing':
                session = create(inspection)
            else:
                raise ValueError(inspection.reason or inspection.primary.reason or
                                 'Cannot resume companion. Inspect a valid backup or choose a new companion explicitly.')
            receipt.update(startup_outcome='ready', startup=_facts(inspection, True), reason=notice)
            return EntrySelection(session, home, notice), 0
        except (OSError, ValueError) as exc:
            error = str(exc)
            receipt.update(startup_outcome='refused', reason=error)
            # Existing explicit bounded commands retain a clear noninteractive
            # refusal. --startup/--frames exercise the actual windowed state.
            if args.frames is None and (args.ticks is not None or args.eras is not None):
                raise ValueError(error) from exc

    import pygame
    from mecha_game.native_ui import StartupView
    pygame.init()
    try:
        display = pygame.display.Info()
        size = (min(760, max(384, display.current_w)), min(680, max(420, display.current_h)))
        window = pygame.display.set_mode(size, pygame.RESIZABLE)
        receipt.update(display={'driver': pygame.display.get_driver(),
                                'size': list(window.get_size()),
                                'resizable': bool(window.get_flags() & pygame.RESIZABLE)})
        pygame.display.set_caption('Mechagotchi - choose your Keeper')
        font = pygame.font.Font(None, 24)
        clock = pygame.time.Clock()
        view = StartupView(inspection, new_learning_policy=effective_new_policy(inspection), new_body_response=effective_new_body(inspection))
        if error:
            view.show_error(error)
        frames = 0
        while True:
            view.draw(window, font)
            pygame.display.flip()
            if frames == 0:
                receipt.update(startup_rendered_frames=1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    receipt.update(startup_outcome='cancelled', startup=_facts(inspection), reason=error)
                    return None, 0
                if event.type == pygame.VIDEORESIZE:
                    window = pygame.display.set_mode((max(384,event.w), max(420,event.h)), pygame.RESIZABLE)
                    continue
                result = view.handle(event)
                if not result.action:
                    continue
                if result.action == 'quit':
                    receipt.update(startup_outcome='cancelled', startup=_facts(inspection), reason=error)
                    return None, 0
                try:
                    if result.action == 'choose_directory':
                        inspection = inspect_home(result.directory)
                        home = inspection.home
                        view.set_inspection(inspection, new_learning_policy=effective_new_policy(inspection), new_body_response=effective_new_body(inspection))
                        error = None
                        receipt.update(keeper_dir=str(home), startup_outcome='inspection',
                                       reason=None, startup=_facts(inspection))
                        continue
                    if result.action == 'retry':
                        inspection = inspect_home(home)
                        view.set_inspection(inspection, new_learning_policy=effective_new_policy(inspection), new_body_response=effective_new_body(inspection))
                        error = None
                        receipt.update(startup_outcome='inspection', reason=None, startup=_facts(inspection))
                        continue
                    if result.inspection_revision != inspection.revision:
                        raise ValueError('The selected save inspection changed. Inspect it again before continuing.')
                    notice = None
                    if result.action == 'resume':
                        session = resume_session(inspection, learning_policy=args.learning_policy, **care_options)
                    elif result.action == 'confirm_restore':
                        session, archive = restore_session(inspection, learning_policy=args.learning_policy, **care_options)
                        notice = 'Recovered prior save.' + (f' Previous primary retained as {archive.name}.' if archive else '')
                    elif result.action == 'confirm_new':
                        session = create(inspection, requested_policy=result.learning_policy, requested_body=result.body_response)
                        notice = 'New companion selected. Available previous lives and original files are preserved.'
                    else:
                        continue
                    # The player has accepted an action. Catch its first actual
                    # checkpoint refusal before advancing care; never probe-write
                    # during inspection or cancel.
                    session.save_checkpoint(home / 'companion.json')
                    receipt.update(startup_outcome='ready', reason=notice, startup=_facts(inspection, True))
                    return EntrySelection(session, home, notice, True), 0
                except (OSError, ValueError) as exc:
                    error = str(exc)
                    inspection = inspect_home(home)
                    view.set_inspection(inspection, new_learning_policy=effective_new_policy(inspection), new_body_response=effective_new_body(inspection))
                    view.show_error(error)
                    receipt.update(startup_outcome='refused', reason=error, startup=_facts(inspection))
            frames += 1
            if args.frames is not None and frames >= args.frames:
                outcome = 'refused' if error or inspection.primary.status in ('invalid','directory','unreadable') else 'cancelled'
                receipt.update(startup_outcome=outcome, startup=_facts(inspection), reason=error or inspection.reason)
                return None, 2 if outcome == 'refused' else 0
            clock.tick(args.fps)
    finally:
        pygame.quit()
