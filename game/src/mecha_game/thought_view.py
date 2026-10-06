"""X7 presentation of recorded decisions, never fabricated internal reasoning.

The live view is transient and only armed by an actual native care tick. Saved
logs remain history; launch, help and quit do not replay them as current thought.
"""
from __future__ import annotations


def thought_lines(thought, *, tick, action, begging=False, recorded=False):
    """Format only fields actually recorded by the engine's decision path."""
    if (not isinstance(thought, dict) or type(tick) is not int or tick < 1
            or action not in ('feed', 'play', 'sleep', 'idle', 'mutate', 'clean')):
        return []
    count, limit = thought.get('tick_count'), thought.get('max_ticks')
    lines = []
    if type(count) is int and type(limit) is int and 1 <= count <= limit:
        outcome = f'asked for food; executed {action}' if begging else f'chose {action}'
        prefix = 'Recorded thought' if recorded else 'Thought'
        lines.append(f'{prefix} t{tick}: {count}/{limit} internal steps; {outcome}.')
    consumer = thought.get('qtable_consumer')
    if isinstance(consumer, dict):
        recommended, base = consumer.get('recommended'), consumer.get('base_action')
        actions = ('feed', 'play', 'sleep', 'idle', 'mutate')
        if recommended in actions and base in actions:
            prefix = 'Recorded policy choice' if recorded else 'Policy choice'
            lines.append(f'{prefix} t{tick}: followed {recommended}; additive suggested {base}.'
                         + ('' if recorded else ' Only you feed.'))
    return lines


def current_thought(snapshot):
    """Return the latest current-life event only when its clocks are exact.

    Legacy events lack a life_id. Their exact age/session clocks must still be
    later than the current life's recorded birth; no old record is rewritten.
    Malformed log records are unavailable, never an exception in the renderer.
    """
    if not isinstance(snapshot, dict) or snapshot.get('alive') is not True:
        return None
    age, tick = snapshot.get('age_ticks'), snapshot.get('session_tick')
    life_id, born = snapshot.get('life_id'), snapshot.get('born_session_tick')
    if (type(age) is not int or age < 1 or type(tick) is not int
            or type(born) is not int or not 0 <= born < tick
            or not isinstance(life_id, str) or not life_id):
        return None
    log = snapshot.get('log')
    if not isinstance(log, list) or not log or not isinstance(log[-1], dict):
        return None
    entry = log[-1]
    if (entry.get('actor') != 'companion' or entry.get('alive') is not True
            or entry.get('death_cause') is not None or type(entry.get('begging')) is not bool
            or type(entry.get('tick')) is not int
            or type(entry.get('session_tick')) is not int
            or entry['tick'] != age or entry['session_tick'] != tick
            or ('life_id' in entry and entry['life_id'] != life_id)):
        return None
    if not thought_lines(entry.get('thought'), tick=age, action=entry.get('action'),
                         begging=entry.get('begging') is True):
        return None
    return entry


class LiveThoughtView:
    """A tick-bound transient readout; no timers, fake progress or save state."""

    def __init__(self):
        self._key = None

    def clear(self):
        self._key = None

    @staticmethod
    def _identity(snapshot):
        return snapshot.get('life_id'), snapshot.get('age_ticks'), snapshot.get('session_tick')

    def observe(self, snapshot):
        self._key = self._identity(snapshot) if current_thought(snapshot) is not None else None

    def lines(self, snapshot):
        entry = current_thought(snapshot)
        if entry is None or self._key != self._identity(snapshot):
            self.clear()
            return []
        return thought_lines(entry['thought'], tick=entry['tick'], action=entry['action'],
                             begging=entry.get('begging') is True)
