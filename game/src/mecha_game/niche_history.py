"""Read-only navigation over recorded campaign links and exact niche labels.

No geometry projection, founder inference, simulation or storage writes.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from mecha_engine.storage import load_era_elites
from mecha_game.era_review import EraReview
from mecha_game.repertoire import RepertoireBrowser

RECORDED_AXES = ('body_mass', 'sensor_count', 'symmetry', 'readability',
                 'lifecycle_survival', 'mutation_stability', 'behavior_neediness')


class CampaignStory:
    def __init__(self, views):
        self.views = views
        self.index = len(views) - 1

    @classmethod
    def load(cls, keeper_dir, *, campaign_id=None):
        view = EraReview.load(keeper_dir, campaign_id=campaign_id)
        views, seen = [view], {view.history.get('campaign_id')}
        previous = view.history.get('predecessor_campaign_id')
        while previous is not None:
            if not isinstance(previous, str) or not previous or previous in seen:
                views.append(EraReview({'eras': [], 'unlocks': []},
                    error=f'Invalid or cyclic campaign link (cycle): {previous}. No ancestry inferred.'))
                break
            seen.add(previous)
            try:
                view = EraReview.load(keeper_dir, campaign_id=previous)
            except (OSError, ValueError) as error:
                views.append(EraReview({'campaign_id': previous, 'eras': [], 'unlocks': []},
                    error=f'Campaign {previous} unavailable: {error}'))
                break
            views.append(view)
            previous = view.history.get('predecessor_campaign_id')
        return cls(list(reversed(views)))

    @property
    def current(self):
        return self.views[self.index]

    def move(self, delta):
        self.index = max(0, min(len(self.views) - 1, self.index + delta))
        return self.current

    def select(self, campaign_id):
        for index, view in enumerate(self.views):
            if view.history.get('campaign_id') == campaign_id:
                self.index = index
                return view
        raise ValueError(f'Campaign {campaign_id} is not in the saved campaign chain.')

    def lines(self):
        record = self.current.history
        previous = record.get('predecessor_campaign_id', 'not recorded')
        previous = 'none' if previous is None else previous or 'invalid empty link'
        return [f"CAMPAIGN {record.get('campaign_id', 'not recorded')}  {self.index + 1}/{len(self.views)}",
                'Ctrl+[ / Ctrl+] recorded campaigns; [ ] eras',
                f'Recorded predecessor: {previous}']


def recorded_niche(elite):
    descriptor = elite.get('descriptor') if isinstance(elite, dict) else None
    if not isinstance(descriptor, dict):
        raise ValueError('A compatible recorded seven-axis niche is required.')
    values = descriptor.get('values')
    names = descriptor.get('names')
    if (not isinstance(names, list) or tuple(names) != RECORDED_AXES or
        not isinstance(values, list) or len(values) != len(RECORDED_AXES) or
        any(type(value) is not int or not 0 <= value < 5 for value in values)):
        raise ValueError('A compatible recorded seven-axis niche is required.')
    key = ','.join(map(str, values))
    if descriptor.get('key') != key or elite.get('niche_key') != key:
        raise ValueError('The recorded seven-axis niche key is inconsistent.')
    return tuple(values)


class NicheHistory(RepertoireBrowser):
    """One exact recorded niche, preserving each campaign/era occurrence."""
    def __init__(self, eras, origin, warnings):
        super().__init__(None, eras=eras)
        self.origin = origin
        self.warnings = warnings
        self.niche = recorded_niche(origin.current())
        self.era_index = next(i for i, era in enumerate(eras)
            if era['campaign_id'] == origin.campaign_id and
               era['era_index'] == origin.selected_era['era_index'])

    @classmethod
    def load(cls, keeper_dir, origin, *, campaign_id=None):
        if origin.current() is None:
            raise ValueError('No selected creature has a recorded niche.')
        wanted = recorded_niche(origin.current())
        story = CampaignStory.load(keeper_dir, campaign_id=campaign_id)
        entries, warnings = [], []
        conn = sqlite3.connect((Path(keeper_dir)/'campaign.sqlite3').resolve().as_uri()+'?mode=ro', uri=True)
        try:
            for view in story.views:
                campaign = view.history.get('campaign_id', 'unknown')
                if view.error:
                    warnings.append(view.error)
                    continue
                if not view.history['eras']:
                    warnings.append(f'{campaign}: no eras recorded.')
                for era in view.history['eras']:
                    label = f"{campaign} era {era['era_index']}"
                    try:
                        elites = load_era_elites(conn, campaign, era['era_index'])
                    except (sqlite3.Error, ValueError, KeyError, TypeError) as error:
                        warnings.append(f'{label}: archive unavailable ({error}).')
                        continue
                    expected = ((era['report'].get('summary') or {}).get('archive') or {}).get('filled_niches')
                    if expected is not None and expected != len(elites):
                        warnings.append(f'{label}: missing/incomplete archive; {len(elites)} of {expected} records.')
                    if not elites and expected in (None, 0):
                        warnings.append(f'{label}: no elite records.')
                    incompatible = 0
                    for elite in elites:
                        try:
                            niche = recorded_niche(elite)
                        except (ValueError, TypeError, AttributeError):
                            incompatible += 1
                            continue
                        if niche != wanted:
                            continue
                        try:
                            candidate = RepertoireBrowser(None, eras=[dict(era, elites=[elite])])
                            candidate.caption()
                            candidate.components_line()
                            candidate.packet()
                        except (ValueError, KeyError, TypeError, AttributeError) as error:
                            warnings.append(f'{label}: matching body unavailable ({error}).')
                            continue
                        entries.append(dict(era, campaign_id=campaign, elites=[elite]))
                    if incompatible:
                        warnings.append(f'{label}: {incompatible} incompatible niche records excluded.')
        finally:
            conn.close()
        if not any(era['campaign_id'] == origin.campaign_id and
                   era['era_index'] == origin.selected_era['era_index'] for era in entries):
            raise ValueError('Selected occurrence is unavailable in saved history. ' + ' '.join(warnings))
        return cls(entries, origin, warnings)

    @property
    def campaign_id(self):
        return self.selected_era.get('campaign_id') if self.selected_era else self._campaign_id

    @campaign_id.setter
    def campaign_id(self, value):
        self._campaign_id = value

    def step(self):
        self.replay_notice = None
        return super().next_era()

    def back(self):
        self.replay_notice = None
        return super().previous_era()

    def caption(self):
        return f"{self.era_index + 1}/{len(self.eras)} occurrences; {self.campaign_id}; " + super().caption()

    def history_lines(self):
        return [f"Same saved niche: {','.join(map(str, self.niche))}",
                'Matches recorded bin labels; historical calibration is not recorded.',
                f'{len(self.warnings)} history notices; only recorded campaign links searched.', *self.warnings]
