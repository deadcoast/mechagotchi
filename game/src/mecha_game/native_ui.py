"""Pygame casing controls. No save, session, resource or simulation authority.

The caller owns event batches, mode changes and pause/closing-frame decisions.
Call draw before handling activation; every action/transition disarms until the
next draw, and held activation keys require release before another activation.
"""
from __future__ import annotations

from dataclasses import dataclass
import pygame
from mecha_game.footer import FooterPager, wrap_lines

GROUND = (16, 18, 16)
PANEL = (28, 35, 27)
INK = (200, 230, 200)
MUTED = (139, 164, 135)
LINE = (74, 101, 67)
FOCUS = (230, 197, 112)
DANGER = (226, 157, 126)


@dataclass(frozen=True)
class UiAction:
    id: str
    label: str
    hint: str = ""
    enabled: bool = True
    destructive: bool = False


@dataclass(frozen=True)
class UiResult:
    action: str | None = None
    consumed: bool = False
    focus_active: bool = False
    inspection_revision: str | None = None
    directory: str | None = None
    learning_policy: str | None = None
    body_response: str | None = None


@dataclass(frozen=True)
class NativeLayout:
    scale: int
    lcd_rect: pygame.Rect
    footer_rect: pygame.Rect
    actions_rect: pygame.Rect
    footer_rows: int
    line_height: int
    window_size: tuple[int, int]


def fit_native_layout(window_size, lcd_size, font_height, preferred_scale=None,
                      footer_rows=6, action_rows=3) -> NativeLayout:
    """Fit integer LCD pixels above separately legible text and controls.

    The app clamps the resizable window to at least 384 x 360. Tiny external
    surfaces are refused instead of returning overlapping/clipped geometry.
    lcd_size is the unscaled grid plus its HUD rows; preferred_scale is a cap.
    """
    width, height = map(int, window_size)
    lcd_width, lcd_height = map(int, lcd_size)
    if min(lcd_width, lcd_height, font_height) < 1 or width < 160:
        raise ValueError("Native layout needs positive LCD dimensions and readable width.")
    line_height = max(22, int(font_height) + 4)
    rows = max(2, int(footer_rows))
    action_height = max(1, int(action_rows)) * (int(font_height) + 16) + 56
    # Keep a usable minimum on a short display; both regions page their content.
    action_height = min(action_height, max(int(font_height) + 72, height // 3))
    while rows > 2 and height - (rows * line_height + 8) - action_height - 24 < lcd_height:
        rows -= 1
    footer_height = rows * line_height + 8
    available_height = height - footer_height - action_height - 24
    scale = min((width - 16) // lcd_width, available_height // lcd_height)
    if scale < 1:
        raise ValueError("Window is too short for LCD pixels, text and controls.")
    if preferred_scale is not None:
        scale = min(scale, max(1, int(preferred_scale)))
    lcd_rect = pygame.Rect((width - lcd_width * scale) // 2, 8,
                           lcd_width * scale, lcd_height * scale)
    actions = pygame.Rect(8, height - action_height - 8, width - 16, action_height)
    footer = pygame.Rect(8, actions.top - footer_height - 4, width - 16, footer_height)
    return NativeLayout(scale, lcd_rect, footer, actions, rows, line_height, (width, height))


class ActionStrip:
    """Visible buttons with keyboard focus and mouse-only paging.

    F6 always enters navigation. allow_tab=False leaves a mode's existing Tab
    command alone until this strip has focus. Mouse activation does not acquire
    keyboard focus, so hover/click alone never pauses care indefinitely.
    """
    def __init__(self, actions=(), *, allow_tab=True):
        self.actions = tuple(actions)
        self.allow_tab = allow_tab
        self.focus_active = False
        self.focused_id = None
        self.page = 0
        self.page_count = 1
        self.button_rects = {}
        self.navigation_rects = {}
        self._pages = []
        self._armed = False
        self._held = set()
        self._pressed = None
        self._rect = pygame.Rect(0, 0, 0, 0)

    def set_actions(self, actions):
        actions = tuple(actions)
        if actions == self.actions:
            return
        self.actions = actions
        self._armed = False
        self._pressed = None
        enabled = [a.id for a in actions if a.enabled]
        if self.focused_id not in enabled:
            self.focused_id = enabled[0] if enabled else None
        self.page = 0

    def focus(self, action_id=None):
        enabled = [a.id for a in self.actions if a.enabled]
        if not enabled:
            self.focus_active = False
            self.focused_id = None
            return
        self.focus_active = True
        self.focused_id = (action_id if action_id in enabled else
                           self.focused_id if self.focused_id in enabled else enabled[0])
        self._reveal_focus()

    def blur(self):
        self.focus_active = False
        self._pressed = None

    def _reveal_focus(self):
        if self.focus_active:
            for index, page in enumerate(self._pages):
                if self.focused_id in page:
                    if self.page != index:
                        self._armed = False
                        self._pressed = None
                    self.page = index
                    break

    def _move(self, step):
        ids = [a.id for a in self.actions if a.enabled]
        if ids:
            current = ids.index(self.focused_id) if self.focused_id in ids else -1
            self.focused_id = ids[(current + step) % len(ids)]
            self._reveal_focus()

    def layout(self, rect, font):
        rect = pygame.Rect(rect)
        self._rect = rect
        measure = lambda text: font.size(text)[0]
        gap = 6
        rows = []
        row = []
        x = 0
        row_height = 0
        for action in self.actions:
            width = min(rect.width, max(64, measure(action.label) + 22))
            labels = wrap_lines([action.label], measure, max(1, width - 20))
            height = max(font.get_height() + 16, len(labels) * font.get_height() + 14)
            if row and x + width > rect.width:
                rows.append((row, row_height)); row = []; x = 0; row_height = 0
            row.append((action.id, x, width, height))
            x += width + gap
            row_height = max(row_height, height)
        if row:
            rows.append((row, row_height))
        capacity = max(font.get_height() + 16, rect.height - 54)
        pages = []
        page = {}
        y = 0
        for row, row_height in rows:
            if page and y + row_height > capacity:
                pages.append(page); page = {}; y = 0
            for action_id, x, width, height in row:
                page[action_id] = pygame.Rect(rect.x + x, rect.y + y, width, height)
            y += row_height + gap
        if page or not pages:
            pages.append(page)
        self._pages = pages
        self.page_count = len(pages)
        self.page = max(0, min(self.page_count - 1, self.page))
        self._reveal_focus()
        self.button_rects = pages[self.page]
        self.navigation_rects = {}
        if self.page_count > 1:
            if self.page:
                self.navigation_rects['previous'] = pygame.Rect(rect.x, rect.bottom - 49, 90, 25)
            if self.page + 1 < self.page_count:
                self.navigation_rects['next'] = pygame.Rect(rect.x + 96, rect.bottom - 49, 90, 25)
        return self.button_rects

    def draw(self, surface, font, rect):
        self.layout(rect, font)
        old_clip = surface.get_clip()
        surface.set_clip(self._rect)
        surface.fill(GROUND, self._rect)
        for action in self.actions:
            button = self.button_rects.get(action.id)
            if button is None:
                continue
            focused = self.focus_active and self.focused_id == action.id
            color = (FOCUS if focused else DANGER if action.destructive else LINE)
            pygame.draw.rect(surface, PANEL, button)
            pygame.draw.rect(surface, color if action.enabled else LINE, button, 2 if focused else 1)
            labels = wrap_lines([action.label], lambda text: font.size(text)[0], button.width - 20)
            for index, label in enumerate(labels):
                text = font.render(label, True, INK if action.enabled else MUTED)
                surface.blit(text, (button.x + 10, button.y + 7 + index * font.get_height()))
        for direction, button in self.navigation_rects.items():
            pygame.draw.rect(surface, PANEL, button)
            pygame.draw.rect(surface, LINE, button, 1)
            surface.blit(font.render('More >' if direction == 'next' else '< Back', True, INK),
                         (button.x + 8, button.y + 3))
        if self.page_count > 1:
            surface.blit(font.render(f'{self.page+1}/{self.page_count}', True, MUTED),
                         (self._rect.x + 195, self._rect.bottom - 47))
        focused = next((a for a in self.actions if a.id == self.focused_id), None)
        hint = focused.hint if self.focus_active and focused and focused.hint else (
            'Arrows / Tab select; Enter acts; Esc returns' if self.focus_active else
            'F6: actions  |  click a button')
        # Hints supplement visible labels. Never squeeze or scale the body font.
        fitting = wrap_lines([hint], lambda text: font.size(text)[0], self._rect.width)
        surface.blit(font.render(fitting[0], True, MUTED), (self._rect.x, self._rect.bottom - 20))
        surface.set_clip(old_clip)
        self._armed = True

    def _result(self, action=None, consumed=True):
        return UiResult(action, consumed, self.focus_active)

    def _activate(self, action_id):
        if not self._armed:
            return self._result()
        action = next((a for a in self.actions if a.id == action_id and a.enabled), None)
        if action is None:
            return self._result()
        self._armed = False
        self._pressed = None
        return self._result(action.id)

    def handle(self, event):
        if event.type == pygame.KEYUP:
            self._held.discard(getattr(event, 'key', None))
            return self._result(consumed=False)
        if event.type == pygame.WINDOWFOCUSLOST:
            self._held.clear(); self._pressed = None; self.blur()
            return self._result(consumed=False)
        if event.type == pygame.KEYDOWN:
            code = event.key
            if code in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                already = code in self._held or getattr(event, 'repeat', False)
                self._held.add(code)
                if self.focus_active:
                    return self._result() if already else self._activate(self.focused_id)
            if code == pygame.K_F6:
                self.focus(); return self._result()
            if code == pygame.K_TAB and (self.allow_tab or self.focus_active):
                if not self.focus_active:
                    self.focus()
                else:
                    self._move(-1 if getattr(event, 'mod', 0) & pygame.KMOD_SHIFT else 1)
                return self._result()
            if self.focus_active:
                if code in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT, pygame.K_UP):
                    self._move(-1 if code in (pygame.K_LEFT, pygame.K_UP) else 1)
                elif code == pygame.K_HOME:
                    self.focus(next((a.id for a in self.actions if a.enabled), None))
                elif code == pygame.K_END:
                    ids = [a.id for a in self.actions if a.enabled]
                    self.focus(ids[-1] if ids else None)
                elif code == pygame.K_ESCAPE:
                    self.blur()
                return self._result()
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) and getattr(event, 'button', None) == 1:
            pos = event.pos
            hit = next((name for name, rect in self.button_rects.items() if rect.collidepoint(pos)), None)
            nav = next((name for name, rect in self.navigation_rects.items() if rect.collidepoint(pos)), None)
            selected = ('action', hit) if hit else ('nav', nav) if nav else None
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._pressed = selected if self._armed else None
                return self._result(consumed=selected is not None)
            pressed = self._pressed
            self._pressed = None
            if selected is not None and selected == pressed:
                if selected[0] == 'nav':
                    self.blur()
                    self.page += 1 if selected[1] == 'next' else -1
                    self._armed = False
                    return self._result()
                return self._activate(selected[1])
            return self._result(consumed=selected is not None or pressed is not None)
        return self._result(consumed=False)


_LABELS = {'resume': 'Resume', 'inspect_backup': 'Inspect backup', 'new': 'New companion',
           'choose_directory': 'Choose save directory', 'retry': 'Retry', 'quit': 'Quit'}


class StartupView:
    """Read-only entry/confirmation UI around the startup authority's inspection."""
    def __init__(self, inspection, *, new_learning_policy='incumbent', new_body_response='legacy'):
        self._default_new_learning_policy = self._validated_policy(new_learning_policy)
        from mecha_game.body_response import validate_body_response
        self._default_new_body_response = validate_body_response(new_body_response)
        self._chosen_new_body_response = None
        self._chosen_new_learning_policy = None
        self.inspection = inspection
        self.mode = 'home'
        self.error = None
        self.strip = ActionStrip()
        self.pager = FooterPager()
        self.directory_text = str(inspection.home)
        self._caret = len(self.directory_text)
        self._anchor = self._caret
        self._path_focus = False
        self._path_rect = pygame.Rect(0, 0, 0, 0)
        self._path_offset = 0
        self.lines = []
        self._configure()

    @property
    def focused_id(self):
        return self.strip.focused_id

    @property
    def button_rects(self):
        return self.strip.button_rects

    @property
    def focus_active(self):
        return True  # startup owns the window; no care is running

    @staticmethod
    def _validated_policy(policy):
        if policy not in ('incumbent', 'qtable'):
            raise ValueError('New companion policy must be incumbent or qtable')
        return policy

    @property
    def new_learning_policy(self):
        return self._chosen_new_learning_policy or self._default_new_learning_policy

    @property
    def new_body_response(self):
        return self._chosen_new_body_response or self._default_new_body_response

    def _configure(self):
        if self.mode == 'backup':
            actions = (UiAction('cancel', 'Cancel'), UiAction('confirm_restore', 'Restore this backup',
                       enabled=bool(self.inspection.can_restore), destructive=True))
        elif self.mode == 'new':
            label = 'Q-table' if self.new_learning_policy == 'qtable' else 'incumbent'
            actions = (UiAction('cancel', 'Cancel'),
                       UiAction('new_policy', 'New policy: ' + label, 'Change only the new life'),
                       UiAction('new_body', 'Body: ' + self.new_body_response, 'Choose for the new life; new campaigns follow it'),
                       UiAction('confirm_new', 'Create new companion', destructive=True))
        elif self.mode == 'directory':
            actions = (UiAction('cancel', 'Cancel'), UiAction('apply_directory', 'Inspect directory',
                       enabled=bool(self.directory_text.strip())))
        else:
            actions = tuple(UiAction(a, _LABELS[a]) for a in self.inspection.actions if a in _LABELS)
        self.strip.set_actions(actions)
        self.strip.focus('cancel' if self.mode != 'home' else None)
        self.strip._armed = False
        self.strip._pressed = None

    def set_inspection(self, inspection, *, new_learning_policy=None, new_body_response=None):
        if new_learning_policy is not None:
            self._default_new_learning_policy = self._validated_policy(new_learning_policy)
        if new_body_response is not None:
            from mecha_game.body_response import validate_body_response
            self._default_new_body_response = validate_body_response(new_body_response)
        self._chosen_new_body_response = None
        self._chosen_new_learning_policy = None
        self.inspection = inspection
        self.error = None
        self.mode = 'home'
        self._path_focus = False
        self.pager.reset()
        self._configure()

    def show_error(self, message):
        self.error = str(message)
        self.mode = 'home'
        self._path_focus = False
        self.pager.reset()
        self._configure()

    def _transition(self, mode):
        if mode == 'new':
            self._chosen_new_learning_policy = None
            self._chosen_new_body_response = None
        self.mode = mode
        self.pager.reset()
        self._path_focus = mode == 'directory'
        if self._path_focus:
            self.directory_text = str(self.inspection.home)
            self._caret = len(self.directory_text)
            self._anchor = self._caret
            self._path_offset = 0
        self._configure()
        if self._path_focus:
            self.strip.blur()

    @staticmethod
    def _save_lines(label, save):
        lines = [f'{label}: {save.status}']
        if save.reason:
            lines.append(str(save.reason))
        if save.status == 'valid':
            facts = [('Companion', save.name), ('Keeper', save.keeper_id), ('Life', save.life_id),
                     ('Policy', save.learning_policy), ('Body response', getattr(save, 'body_response', None)), ('Saved tick', save.session_tick),
                     ('Recorded lives', save.life_count)]
            lines.append(' | '.join(f'{name}: {value}' for name, value in facts if value is not None))
            if save.alive is not None:
                lines.append('Saved state: alive' if save.alive else 'Saved state: deceased')
        return lines

    def _content(self):
        selected = self.inspection
        lines = [f'Save directory: {selected.home}']
        if self.error:
            lines += ['ACTION FAILED - files have not been assumed saved.', self.error]
        if selected.reason:
            lines.append(str(selected.reason))
        if self.mode == 'backup':
            lines += ['RESTORE BACKUP - confirm this inspected prior save.',
                      *self._save_lines('Backup', selected.backup),
                      'The existing primary bytes are retained before replacement.',
                      'Only the inspected files may be restored. Changes require a fresh inspection.']
            if not selected.can_restore:
                lines.append('Restore unavailable: the primary cannot be safely replaced. Choose another directory or retry.')
        elif self.mode == 'new':
            lines += ['NEW COMPANION - begin a new life in this directory.',
                      'Existing readable companion bytes are preserved before replacement.',
                      'Available Keeper life history is retained; missing history is not invented.',
                      'The new companion requires the packaged starting resources.',
                      ('New policy: Q-table; learns within this life.'
                       if self.new_learning_policy == 'qtable' else 'New policy: incumbent.'),
                      'Change policy below to choose for this new life. Existing life records keep their policy.',
                      'New lives start without a trained table; only you can feed your companion.',
                      'New body response: ' + self.new_body_response + '.',
                      ('Experimental workload-v1: play energy follows actual functional body capacity.'
                       if self.new_body_response == 'workload-v1' else 'Legacy: all bodies retain the existing play energy cost.'),
                      'Existing campaigns keep their body model. Use a separate Keeper for a different campaign model.']
        elif self.mode == 'directory':
            lines += ['CHOOSE SAVE DIRECTORY',
                      'Enter a path, then Inspect directory. This does not create or save files.',
                      'Ctrl+A selects all; Ctrl+V pastes; arrows/Home/End move; Backspace/Delete edits.',
                      'Tab selects buttons; Escape cancels without changing the selected home.']
        else:
            lines += [*self._save_lines('Primary', selected.primary),
                      *self._save_lines('Backup', selected.backup),
                      *map(str, selected.notices),
                      'Inspection changes no files. Resume uses the selected saved life.',
                      'A later save can still fail; read access does not prove write access.']
        return lines

    def draw(self, surface, font):
        bounds = surface.get_rect()
        surface.fill(GROUND)
        pygame.draw.rect(surface, LINE, bounds.inflate(-16, -16), 1)
        for text, y, color in (('MECHAGOTCHI / KEEPER ENTRY', 20, INK),
                               ('Saved lives stay yours. Choose the next action.', 45, MUTED)):
            heading = font.render(text, True, color)
            available = max(1, bounds.width - 40)
            if heading.get_width() > available:
                heading = pygame.transform.smoothscale(heading, (available,
                    max(1, round(heading.get_height() * available / heading.get_width()))))
            surface.blit(heading, (20, y))
        action_height = min(180, max(116, bounds.height // 3))
        action_rect = pygame.Rect(20, bounds.height - action_height - 18, bounds.width - 40, action_height)
        bottom = action_rect.top - 10
        if self.mode == 'directory':
            self._path_rect = pygame.Rect(20, bottom - 44, bounds.width - 40, 34)
            self._draw_path(surface, font)
            bottom = self._path_rect.top - 12
        self.lines = self._content()
        rows = max(2, (bottom - 78) // (font.get_height() + 4))
        page = self.pager.layout(self.lines, lambda text: font.size(text)[0], bounds.width - 40, rows)
        for index, line in enumerate(page.lines):
            surface.blit(font.render(line, True, INK if index else MUTED),
                         (20, 78 + index * (font.get_height() + 4)))
        self.strip.draw(surface, font, action_rect)

    def _draw_path(self, surface, font):
        rect = self._path_rect
        pygame.draw.rect(surface, PANEL, rect)
        pygame.draw.rect(surface, FOCUS if self._path_focus else LINE, rect, 2)
        inner = rect.inflate(-16, -10)
        caret_px = font.size(self.directory_text[:self._caret])[0]
        if caret_px - self._path_offset > inner.width - 3:
            self._path_offset = caret_px - inner.width + 3
        if caret_px < self._path_offset:
            self._path_offset = caret_px
        old_clip = surface.get_clip(); surface.set_clip(inner)
        low, high = sorted((self._caret, self._anchor))
        if low != high:
            left = font.size(self.directory_text[:low])[0]
            right = font.size(self.directory_text[:high])[0]
            pygame.draw.rect(surface, LINE, (inner.x + left - self._path_offset, inner.y, right-left, inner.height))
        surface.blit(font.render(self.directory_text, True, INK), (inner.x - self._path_offset, inner.y))
        if self._path_focus:
            pygame.draw.line(surface, FOCUS, (inner.x + caret_px-self._path_offset, inner.y),
                             (inner.x + caret_px-self._path_offset, inner.bottom-1))
        surface.set_clip(old_clip)

    def _replace_selection(self, text):
        low, high = sorted((self._caret, self._anchor))
        candidate = self.directory_text[:low] + text + self.directory_text[high:]
        if len(candidate) > 32767:
            self.error = 'Directory path is too long; current text retained.'
            return
        self.directory_text = candidate
        self._caret = low + len(text); self._anchor = self._caret
        actions = (UiAction('cancel', 'Cancel'), UiAction('apply_directory', 'Inspect directory',
                   enabled=bool(self.directory_text.strip())))
        self.strip.set_actions(actions)

    def _path_key(self, event):
        code = event.key
        mod = getattr(event, 'mod', 0)
        if code == pygame.K_a and mod & pygame.KMOD_CTRL:
            self._anchor = 0; self._caret = len(self.directory_text)
        elif code == pygame.K_v and mod & pygame.KMOD_CTRL:
            try:
                text = pygame.scrap.get_text()
                self._replace_selection(''.join(c for c in text if c >= ' ' and c != '\x7f'))
            except pygame.error as error:
                self.error = f'Clipboard unavailable: {error}. Type the directory instead.'
        elif code in (pygame.K_c, pygame.K_x) and mod & pygame.KMOD_CTRL:
            low, high = sorted((self._caret, self._anchor))
            if low != high:
                try:
                    pygame.scrap.put_text(self.directory_text[low:high])
                    if code == pygame.K_x:
                        self._replace_selection('')
                except pygame.error as error:
                    self.error = f'Clipboard unavailable: {error}. Current text retained.'
        elif code in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_HOME, pygame.K_END):
            if code == pygame.K_HOME: self._caret = 0
            elif code == pygame.K_END: self._caret = len(self.directory_text)
            else: self._caret = max(0, min(len(self.directory_text), self._caret + (1 if code == pygame.K_RIGHT else -1)))
            if not mod & pygame.KMOD_SHIFT: self._anchor = self._caret
        elif code in (pygame.K_BACKSPACE, pygame.K_DELETE):
            if self._anchor == self._caret:
                self._anchor = (max(0, self._caret - 1) if code == pygame.K_BACKSPACE else
                                min(len(self.directory_text), self._caret + 1))
            self._replace_selection('')
        return UiResult(consumed=True, focus_active=True)

    def handle(self, event):
        if event.type == pygame.QUIT:
            return UiResult('quit', True, True, self.inspection.revision)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.mode != 'home':
                self._transition('home')
                return UiResult(consumed=True, focus_active=True)
            return UiResult('quit', True, True, self.inspection.revision)
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
            self.pager.move(-1 if event.key == pygame.K_PAGEUP else 1)
            return UiResult(consumed=True, focus_active=True)
        if event.type == pygame.MOUSEWHEEL:
            self.pager.move(-event.y)
            return UiResult(consumed=True, focus_active=True)
        if self.mode == 'directory':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                stops = ['path', *[a.id for a in self.strip.actions if a.enabled]]
                current = 'path' if self._path_focus else self.strip.focused_id
                index = stops.index(current) if current in stops else 0
                target = stops[(index + (-1 if getattr(event, 'mod', 0) & pygame.KMOD_SHIFT else 1)) % len(stops)]
                self._path_focus = target == 'path'
                if self._path_focus:
                    self.strip.blur()
                else:
                    self.strip.focus(target)
                return UiResult(consumed=True, focus_active=True)
            if event.type == pygame.MOUSEBUTTONDOWN and getattr(event, 'button', None) == 1:
                self._path_focus = self._path_rect.collidepoint(event.pos)
                if self._path_focus:
                    self.strip.blur()
                    return UiResult(consumed=True, focus_active=True)
            if event.type == pygame.TEXTINPUT and self._path_focus:
                self._replace_selection(''.join(c for c in event.text if c >= ' ' and c != '\x7f'))
                return UiResult(consumed=True, focus_active=True)
            if event.type == pygame.KEYDOWN and self._path_focus:
                if event.key in (pygame.K_TAB, pygame.K_F6):
                    self._path_focus = False; self.strip.focus('cancel')
                    return UiResult(consumed=True, focus_active=True)
                if event.key not in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return self._path_key(event)
                self._path_focus = False; self.strip.focus('apply_directory')
        result = self.strip.handle(event)
        action = result.action
        if action in ('inspect_backup', 'new', 'choose_directory'):
            self._transition({'inspect_backup': 'backup', 'new': 'new', 'choose_directory': 'directory'}[action])
            action = None
        elif action == 'new_policy':
            self._chosen_new_learning_policy = ('incumbent' if self.new_learning_policy == 'qtable' else 'qtable')
            self._configure()
            self.strip.focus('new_policy')
            action = None
        elif action == 'new_body':
            self._chosen_new_body_response = 'legacy' if self.new_body_response == 'workload-v1' else 'workload-v1'
            self._configure()
            self.strip.focus('new_body')
            action = None
        elif action == 'cancel':
            self._transition('home'); action = None
        elif action == 'apply_directory':
            return UiResult('choose_directory', True, True, self.inspection.revision, self.directory_text)
        return UiResult(action, result.consumed, True, self.inspection.revision if action else None,
                        learning_policy=self._chosen_new_learning_policy if action == 'confirm_new' else None,
                        body_response=self._chosen_new_body_response if action == 'confirm_new' else None)
