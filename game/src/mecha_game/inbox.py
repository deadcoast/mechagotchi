"""Paused file-bridge selection; rendering and engine application stay with their owners."""
from __future__ import annotations

from pathlib import Path
from mecha_game.covenant_io import read_import_file


class InboxPicker:
    """Read-only, deterministic selection for the Keeper's two import inboxes."""

    def __init__(self, keeper_dir: str | Path, kind: str) -> None:
        if kind not in ('covenant', 'pack'):
            raise ValueError('Unknown import inbox.')
        self.kind = kind
        self.directory = Path(keeper_dir) / ('covenants' if kind == 'covenant' else 'packs')
        self.files: list[Path] = []
        self.index = 0
        self.preview: dict = {}
        self.digest: str | None = None
        self.error: str | None = None
        self.result_lines: list[str] = []
        self.completed = False
        self.refresh()

    @property
    def selected(self) -> Path | None:
        return self.files[self.index] if self.files else None

    def refresh(self) -> None:
        selected = self.selected
        try:
            self.files = sorted((p for p in self.directory.iterdir()
                if p.is_file() and p.suffix.lower() == '.json' and not p.name.lower().endswith('.bak.json')),
                key=lambda p: (p.name.casefold(), p.name)) if self.directory.exists() else []
        except OSError as error:
            self.files = []
            self._reset()
            self.error = f'Inbox unreadable: {error}. F5 retries.'
            return
        self.index = self.files.index(selected) if selected in self.files else min(self.index, max(0, len(self.files)-1))
        self._read_preview()

    def select(self, index: int) -> None:
        index = max(0, min(len(self.files)-1, index))
        if index != self.index:
            self.index = index
            self._read_preview()

    def move(self, delta: int) -> None:
        self.select(self.index + delta)

    def _reset(self) -> None:
        self.preview = {}
        self.digest = None
        self.error = None
        self.result_lines = []
        self.completed = False

    def _read_preview(self) -> None:
        self._reset()
        if self.selected is not None:
            try:
                self.preview, self.digest = read_import_file(self.selected)
            except (OSError, ValueError, UnicodeError) as error:
                self.error = f'File unreadable: {error}. Fix it, then F5 refresh.'

    def help_lines(self) -> list[str]:
        shortcut = 'I' if self.kind == 'covenant' else 'K'
        return [f'HELP - {self.kind} inbox; care paused',
                ', . / arrows select; Home/End first/last',
                'F5 refreshes files and their preview',
                'Enter imports the displayed selection once',
                f'{shortcut}/Escape returns without importing',
                'F1/Escape closes help; selection stays',
                'PgUp/PgDn or wheel pages full details',
                'Care and era keys are ignored in this inbox.',
                'An imported covenant governs future eras, hatches and adoptions; your pet keeps its covenant.',
                'Pack items stage separately. I chooses staged covenants; W gathers creatures after closing.',
                'Refused items and existing-file conflicts stay visible. Fix the file or write problem, then retry.',
                f'Folder: {self.directory}']

    def lines(self) -> list[str]:
        label = self.kind.upper()
        shortcut = 'I' if self.kind == 'covenant' else 'K'
        action = ('import complete' if self.completed else 'import unavailable' if self.error else
                  'no file selected' if self.selected is None else 'Enter imports')
        lines = [f'{label} INBOX - care paused',
                 f', . / arrows select; {action}',
                 f'{shortcut}/Escape back; F5 refresh; F1 help']
        if self.error:
            lines.append('File unreadable; fix it, then F5 refresh.' if self.selected else 'Inbox unreadable; F5 retries.')
        if self.result_lines:
            lines.extend(self.result_lines)
        if self.selected is None:
            lines.append(self.error or 'No JSON files. Add a file here, then F5 refresh.')
        else:
            lines.append(f'{self.index + 1}/{len(self.files)}  {self.selected.name}')
            if self.error:
                lines.append(self.error)
            elif self.kind == 'covenant':
                lines.append(f"Covenant: {self.preview.get('profile_id', 'not recorded')}")
                lines.append('Applies to future eras/hatches/adoptions; your pet keeps its covenant.')
                lines.append('Engine validation and seed compatibility are checked on import.')
            else:
                lines.append(f"Pack: {self.preview.get('title') or self.preview.get('pack_id', 'not recorded')}")
                for field, label in (('slips', 'covenants'), ('creatures', 'creatures')):
                    items = self.preview.get(field, [])
                    lines.append(f'{len(items)} {label} declared' if isinstance(items, list) else f'Invalid {label} list')
                lines.append('Stages accepted items; I chooses a covenant, W gathers creatures after closing.')
        if self.completed:
            lines.append('Already imported here. Choose another file or return.')
        lines.extend([f'Folder: {self.directory}', 'Home/End first/last; PgUp/PgDn or wheel pages details'])
        return lines
