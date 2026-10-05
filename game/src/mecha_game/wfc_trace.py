"""Read-only WFC observations, diagnostic wave playback and joined capture."""
from copy import deepcopy
import json
import threading

from mecha_engine.generation import train_wfc_model, generate_wfc_grid
from mecha_engine.genome import render_packet_v2, clip_frame_count
from mecha_game.clips import TRANSITIONS


def capture_wfc(seeds, grid_id, rng_seed, events):
    return generate_wfc_grid(train_wfc_model(seeds), grid_id=grid_id, rng_seed=rng_seed, trace=events)


class WfcWork:
    """Cancellation discards a request; the engine call completes unchanged."""
    def __init__(self, operation):
        self.operation = operation
        self.events = []
        self.grid = None
        self.error = None
        self.cancelled = False
        self.done = threading.Event()
        self.thread = threading.Thread(target=self._run, name='mechagotchi-wfc', daemon=False)

    def _run(self):
        try:
            self.grid = self.operation(self.events)
        except BaseException as error:
            self.error = error
        finally:
            self.done.set()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.cancelled = True

    def join(self):
        self.thread.join()


class WfcTraceView:
    def __init__(self, grid, events, *, error=None):
        self.grid = deepcopy(grid)
        self.events = deepcopy(events)
        self.error = (str(error) or type(error).__name__) if error is not None else None
        self.index = next((i for i, event in enumerate(self.events) if event['event'] == 'wave_started'), 0)
        self.playing = False
        self.final = False
        self.frame_index = self.clip_index = 0
        self.clips = ['idle'] + sorted({clip for edge in TRANSITIONS for clip in edge} - {'idle'})
        self.attempts = [i for i, event in enumerate(self.events) if event['event'] == 'attempt_started']

    @property
    def event(self):
        return self.events[self.index] if self.events else None

    def step(self, delta):
        if self.final:
            self.frame_index = (self.frame_index + delta) % clip_frame_count(self.clips[self.clip_index])
        else:
            self.index = max(0, min(len(self.events) - 1, self.index + delta))
            if self.index == len(self.events) - 1:
                self.playing = False

    def move_attempt(self, delta):
        self.playing = False
        if self.final:
            self.clip_index = (self.clip_index + delta) % len(self.clips)
            self.frame_index = 0
        elif self.attempts:
            options = [i for i in self.attempts if i < self.index] if delta < 0 else [i for i in self.attempts if i > self.index]
            if options:
                self.index = options[-1] if delta < 0 else options[0]

    def toggle_final(self):
        if self.grid is not None:
            self.final = not self.final
            self.playing = False

    def packet(self):
        if self.grid is None:
            return None
        return render_packet_v2(self.grid, None, clip=self.clips[self.clip_index], frame_index=self.frame_index)

    def wave(self):
        if not self.events:
            return {}
        starts = [i for i in range(self.index + 1) if self.events[i]['event'] in ('attempt_started', 'wave_started')]
        if not starts or self.events[starts[-1]]['event'] != 'wave_started':
            return {}
        start = starts[-1]
        wave = deepcopy(self.events[start]['cells'])
        for event in self.events[start + 1:self.index + 1]:
            if event['event'] == 'cell_collapsed':
                wave[','.join(map(str, event['position']))] = {event['token']: 1}
            elif event['event'] == 'propagated':
                wave[','.join(map(str, event['target']))] = deepcopy(event['remaining'])
            elif event['event'] in ('collapsed', 'finished'):
                wave = {f'{x},{y}': {token: 1} for y, row in enumerate(event['matrix']) for x, token in enumerate(row)}
            # A contradiction reports an empty proposed filter; it was NOT
            # assigned to the engine's wave. Preserve that distinction here.
        return wave

    def pixels(self, scale):
        wave = self.wave()
        size_event = next((e for e in self.events[:self.index + 1] if e['event'] == 'wave_started'), None)
        width, height = (size_event['width'], size_event['height']) if size_event else (16, 16)
        position = (self.event or {}).get('position', (self.event or {}).get('target'))
        focus = ','.join(map(str, position)) if position is not None else None
        colors = {}
        for key, choices in wave.items():
            colors[key] = ((80, 88, 80) if len(choices) > 1 else
                           (16, 18, 16) if next(iter(choices), '.') == '.' else (140, 205, 140))
        return tuple(tuple((232, 240, 224) if f'{x // scale},{y // scale}' == focus and
                           (x % scale in (0, scale - 1) or y % scale in (0, scale - 1)) else
                           colors.get(f'{x // scale},{y // scale}', (16, 18, 16))
                           for x in range(width * scale)) for y in range(height * scale))

    def lines(self):
        event = self.event
        attempt = next((e['attempt'] for e in reversed(self.events[:self.index + 1]) if e['event'] == 'attempt_started'), None)
        cursor = f"{self.index + 1 if event else 0}/{len(self.events)}"
        lines = ['WFC FINAL BODY - care paused' if self.final else 'WFC TRACE - care paused',
                 'Fresh capture; session-only; read-only',
                 f'Trace paused at event {cursor}' if self.final else f"Event {cursor}: {event['event'] if event else 'unavailable'}",
                 'Space play/pause; , . steps; [ ] attempts' if not self.final else 'Space animation; , . frames; [ ] clips',
                 'Home/End first/last; V final body / wave',
                 'Tab/Escape back; N new WFC; F1 help',
                 'Engine animation; no life simulation.' if self.final else 'Gray choices; green fixed tokens; white target.',
                 'Seed corpus WFC; covenant not enforced; no adoption.']
        if self.error:
            lines.insert(3, 'Capture result: ' + self.error)
        if self.final:
            animation = self.packet()['animation']
            lines.extend([f"Actual final grid: {self.grid['grid_id']}",
                          f"Animation {animation['clip']} {animation['frame_index'] + 1}/{animation['frame_count']}",
                          'Animation only; no lifecycle simulation.'])
        else:
            lines.extend(['Wave choices, not a creature. Gray unresolved; green fixed tokens;',
                          'dark fixed empty / not initialized; white observed target.',
                          f"Attempt: {attempt if attempt is not None else 'not started'}",
                          'Contradiction: empty proposed filter, not applied to the wave.'])
        if event:
            if self.final:
                lines.append('Retained trace event; separate from final-body animation:')
            lines.extend(f'{key}: {json.dumps(value, ensure_ascii=True, sort_keys=True)}' for key, value in event.items())
        return lines

    def help_lines(self):
        return ['WFC HELP - care and playback paused',
                'This is a fresh observation of the separate WFC generator.',
                'Constrained generation remains the evolution default (DR0042).',
                'Space plays/pauses actual events; comma/period steps them.',
                'Brackets jump to attempt starts; Home/End selects endpoints.',
                'PgUp/PgDn or wheel pauses playback and reads every event field.',
                'V shows the real final body when generation succeeded.',
                'In final body: Space animation, comma/period frames, brackets clips.',
                'Tab/Escape returns to the unchanged constrained hatch preview.',
                'N captures another WFC run. Failed attempts remain inspectable.',
                'Captured traces are session-only; restarting creates a fresh run.',
                'This inspector never adopts a creature or writes preparation/saves.',
                'The corpus is the generator input; the active covenant is not a WFC constraint.',
                'F1/Escape returns to the same event.']
