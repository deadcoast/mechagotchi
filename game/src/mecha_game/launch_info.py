"""Explicit, owned launch diagnostics; never part of a Keeper save."""
from __future__ import annotations
import json
import os
from pathlib import Path
import tempfile


class LaunchInfo:
    def __init__(self, path=None):
        self.path = Path(path).resolve() if path is not None else None
        self.document = {'format': 'mechagotchi_launch_v1', 'process_id': os.getpid(),
                         'startup_outcome': 'inspection', 'view': 'startup', 'stopped': False}
        self._bytes = None
        if self.path is not None:
            raw = self._encode()
            with self.path.open('xb') as stream:
                stream.write(raw)
            self._bytes = raw

    def _encode(self):
        return (json.dumps(self.document, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')

    def update(self, **values):
        self.document.update(values)
        if self.path is None:
            return
        if self.path.read_bytes() != self._bytes:
            raise ValueError('Launch receipt changed externally; it was preserved.')
        raw = self._encode()
        handle, name = tempfile.mkstemp(prefix='.mecha-launch-', suffix='.tmp', dir=self.path.parent)
        temporary = Path(name)
        try:
            with os.fdopen(handle, 'wb') as stream:
                stream.write(raw); stream.flush(); os.fsync(stream.fileno())
            if self.path.read_bytes() != self._bytes:
                raise ValueError('Launch receipt changed externally; it was preserved.')
            os.replace(temporary, self.path)
            self._bytes = raw
        finally:
            temporary.unlink(missing_ok=True)

    def finish(self, exit_code):
        self.update(stopped=True, exit_code=exit_code)
