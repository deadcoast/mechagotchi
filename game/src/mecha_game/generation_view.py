"""Paused consumer of recorded generation truth and engine animation packets.

This is a constrained hatch/origin reader, not a WFC collapse visualization.
No lifecycle steps, generation decisions or save writes occur here.
"""
from copy import deepcopy
import json

from mecha_engine.generation import explain_generation
from mecha_engine.genome import clip_frame_count, render_packet_v2
from mecha_game.clips import TRANSITIONS


class GenerationView:
    def __init__(self, grid=None, profile=None, *, adoptable=False, error=None):
        self.grid = deepcopy(grid)
        self.profile = deepcopy(profile)
        self.adoptable = adoptable
        self.error = error
        self.notice = None
        self.playing = False
        self.frame_index = 0
        self.clip_index = 0
        self.explanation = None
        self.clips = ['idle']
        self._trace_lines = []
        if grid is not None:
            packet = render_packet_v2(self.grid, None, slip_profile=self.profile)
            supported = {clip for edge in TRANSITIONS for clip in edge}
            allowed = [c for c in packet['animation_vocabulary'] if c in supported]
            self.clips = (['idle'] if 'idle' in allowed else []) + sorted(c for c in allowed if c != 'idle')
            self.clips = self.clips or ['idle']  # engine's documented fallback
            try:
                self.explanation = explain_generation(self.grid)
            except ValueError as failure:
                self.error = f'Generation trace unavailable: {failure}'
            else:
                self._trace_lines = [f'{field}: {json.dumps(value, ensure_ascii=True, sort_keys=True)}'
                                     for field, value in self.explanation.items()]

    def packet(self):
        if self.grid is None:
            return None
        return render_packet_v2(self.grid, None, slip_profile=self.profile,
                               clip=self.clips[self.clip_index], frame_index=self.frame_index)

    def step(self, delta):
        self.frame_index = (self.frame_index + delta) % clip_frame_count(self.clips[self.clip_index])

    def move_clip(self, delta):
        self.clip_index = (self.clip_index + delta) % len(self.clips)
        self.frame_index = 0

    def lines(self):
        lines = ['HATCH PREVIEW - care paused' if self.adoptable else 'ORIGIN TRACE - care paused',
                 'Enter adopt replaces current companion' if self.adoptable else 'Saved birth genome; read-only',
                 'N next; Tab WFC trace; H/Escape back; F1 help' if self.adoptable else 'O/Escape back; F1 help']
        if self.notice:
            lines.insert(1, self.notice)
        if self.error:
            lines.append(self.error)
        if self.grid is not None:
            lines.extend([f"Creature: {self.grid['grid_id']}", f"Covenant: {self.profile['profile_id']}"])
            animation = self.packet()['animation']
            lines.extend([f"Animation {animation['clip']} {animation['frame_index'] + 1}/{animation['frame_count']} - {'playing' if self.playing else 'paused'}",
                          'Space play/pause; , . step; [ ] clips',
                          'Animation preview only; no life simulation.'])
        if self.explanation is not None:
            trace = self.explanation
            recorded = lambda key: trace[key] if trace[key] is not None else 'not recorded'
            lines.extend([f"Recorded parent: {recorded('parent_grid_id')}",
                          f"Proposals accepted: {recorded('accepted_proposals')} / {recorded('proposal_attempts')} attempted",
                          f"Seed: {recorded('rng_seed')}; generation: {recorded('lineage_generation')}",
                          'Recorded generation explanation (all fields):',
                          'Constrained hatch trace; not a WFC collapse trace.', *self._trace_lines])
        return lines

    def help_lines(self):
        return ['HATCH / ORIGIN HELP - care and animation paused',
                'H opens a generated founder under the active covenant.',
                'Enter in hatch preview replaces your companion with that founder.',
                'H/Escape closes without adopting; N explicitly generates another.',
                'O in care opens the saved companion birth genome and its recorded origin.',
                'Origin is read-only; absent traces are reported as unavailable.',
                'Space play/pause; comma/period step; brackets change engine clips.',
                'These are animation frames, not lifespan or health predictions.',
                'PgUp/PgDn or wheel reads every recorded explanation field.',
                'Null means the field was not recorded; values are not inferred.',
                'Constrained hatching and the era-side WFC generator are distinct.',
                'Tab opens a separate fresh WFC capture; your constrained candidate stays.',
                'F1/Escape returns to the same candidate and animation position.']
