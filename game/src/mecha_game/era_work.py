"""An explicit era's foreground-owned work; no pygame or detached worker."""
from __future__ import annotations
import threading


class EraCancelled(Exception):
    """Uncommitted computation was cancelled; saved inputs remain authoritative."""


class EraWork:
    """One joined worker, observational counters and an atomic commit boundary."""

    def __init__(self, operation):
        self._operation = operation
        self._lock = threading.Lock()
        self.cancel_requested = threading.Event()
        self.done = threading.Event()
        self._phase = 'Preparing era'
        self._completed = 0
        self._budget = None
        self._committing = False
        self._value = None
        self._error = None
        self.thread = threading.Thread(target=self._run, name='mechagotchi-era', daemon=False)

    def start(self):
        self.thread.start()

    def _run(self):
        try:
            self._value = self._operation(self)
        except BaseException as error:
            self._error = error
        finally:
            self.done.set()

    def _check_cancel(self):
        if self.cancel_requested.is_set() and not self._committing:
            raise EraCancelled('Era request cancelled; saved progress and preparation retained.')

    def phase(self, name):
        with self._lock:
            self._check_cancel()
            self._phase = name

    def progress(self, completed, budget):
        with self._lock:
            self._check_cancel()
            self._phase = 'Evaluating candidates'
            self._completed = completed
            self._budget = budget

    def begin_commit(self):
        # A cancellation accepted before this boundary cannot begin persistence.
        # Afterwards the real result owns T4's journal/recovery path.
        with self._lock:
            self._check_cancel()
            self._committing = True
            self._phase = 'Saving completed era'

    def cancel(self):
        with self._lock:
            if self._committing or self.done.is_set():
                return False
            self.cancel_requested.set()
            return True

    def snapshot(self):
        with self._lock:
            return dict(phase=self._phase, completed=self._completed, budget=self._budget,
                        committing=self._committing, cancelling=self.cancel_requested.is_set(),
                        done=self.done.is_set())

    def join(self):
        self.thread.join()

    def result(self):
        self.join()
        if self._error is not None:
            raise self._error
        return self._value
