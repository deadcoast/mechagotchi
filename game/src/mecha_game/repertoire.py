"""The repertoire browser — species memory made visible (F13, MVP 0.3).

Phase E proved the repertoire (the MAP-Elites archive at documented
scale; E5's recurrent families are the species-memory substrate); the
era bench fills it every era. This browser SURFACES it: page through
the archive's elites in its own deterministic niche order, each one
drawn from its real render packet under the campaign's covenant, each
caption built from the elite RECORD verbatim — the descriptor's named
axes, the fitness and its components, the lineage generation. The
browser never re-derives a statistic (DR 0021's first law).

The original in-memory source remains supported. T2 closes the named F13/F17
restart remainder with the same complete elite records read from the ledger.
Historical bodies use their recorded covenant; adoption uses the current one.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from mecha_engine.genome import render_packet_v2
from mecha_engine.storage import load_era_elites
from mecha_game.era_review import EraReview


class RepertoireBrowser:
    """Scrub the bloodline's archive, era by era, niche by niche."""

    def __init__(self, keeper_campaign, *, eras=None, error=None) -> None:
        self.campaign = keeper_campaign
        self.eras = eras if eras is not None else keeper_campaign.eras
        if not self.eras and not error:
            raise ValueError("no era to browse yet - run one (E)")
        self.error = error
        self.allow_planning = error is None
        self.era_index = max(0, len(self.eras) - 1)
        self.index = 0

    @classmethod
    def unavailable(cls, message, *, allow_planning=False):
        browser = cls(None, eras=[], error=message)
        browser.allow_planning = allow_planning
        return browser

    @classmethod
    def load(cls, keeper_dir, *, campaign_id=None, era_index=None):
        keeper = Path(keeper_dir)
        history = EraReview.load(keeper, campaign_id=campaign_id).history
        if not history['eras']:
            return cls.unavailable("No recorded eras. E runs the first era.", allow_planning=True)
        conn = sqlite3.connect((keeper / 'campaign.sqlite3').resolve().as_uri() + '?mode=ro', uri=True)
        try:
            for era in history['eras']:
                era['elites'] = load_era_elites(conn, history['campaign_id'], era['era_index'])
                expected = (era['report'].get('summary') or {}).get('archive', {}).get('filled_niches')
                if expected is not None and expected != len(era['elites']):
                    raise ValueError("The saved archive does not match its recorded niche count.")
            browser = cls(None, eras=history['eras'])
            # Validate displayable saved records before navigation can encounter
            # a broken older blob. These are render reads, never lifecycle ticks.
            for position in range(len(browser.eras)):
                browser.era_index = position
                for index in range(browser.count):
                    browser.index = index
                    browser.caption()
                    browser.axes_line()
                    browser.components_line()
                    browser.packet()
        except (sqlite3.Error, KeyError, TypeError, AttributeError, ValueError) as error:
            raise ValueError("Stored archive records cannot be displayed.") from error
        finally:
            conn.close()
        browser.era_index = len(browser.eras) - 1
        if era_index is not None:
            positions = [i for i, era in enumerate(browser.eras) if era['era_index'] == era_index]
            if not positions:
                raise ValueError(f"No saved archive for era {era_index}.")
            browser.era_index = positions[0]
        browser.index = 0
        return browser

    @property
    def selected_era(self):
        return self.eras[self.era_index] if self.eras else None

    # -- position ---------------------------------------------------------

    @property
    def elites(self) -> list[dict]:
        return self.selected_era["elites"] if self.selected_era is not None else []

    @property
    def count(self) -> int:
        return len(self.elites)

    def current(self) -> dict | None:
        return self.elites[self.index] if self.elites else None

    def step(self) -> int:
        self.index = max(0, min(self.count - 1, self.index + 1))
        return self.index

    def back(self) -> int:
        self.index = max(0, self.index - 1)
        return self.index

    def next_era(self) -> int:
        if self.era_index < len(self.eras) - 1:
            self.era_index += 1
            self.index = 0
        return self.era_index

    def previous_era(self) -> int:
        if self.era_index > 0:
            self.era_index -= 1
            self.index = 0
        return self.era_index

    # -- display (record fields verbatim) -----------------------------------

    def packet(self) -> dict | None:
        """The elite's body as a real render packet under the
        campaign's covenant (idle display; the vocabulary gate stays
        the engine's)."""
        if self.current() is None:
            return None
        profile = self.selected_era.get('slip_profile')
        if profile is None:
            profile = self.campaign.campaign['slip_profile']
        return render_packet_v2(
            self.current()["grid"],
            None,
            slip_profile=profile,
        )

    def caption(self) -> str:
        if self.error:
            return self.error if self.allow_planning else "unavailable: " + self.error
        elite = self.current()
        era = self.selected_era
        if elite is None:
            return f"era {era['era_index']} [{era['weather']['forecast']}]  0 elites recorded"
        generation = (
            elite["grid"].get("lineage", {}).get("generation", 0)
        )
        return (
            f"era {era['era_index']} [{era['weather']['forecast']}]  "
            f"{self.index + 1}/{self.count}  {elite['grid_id']}  "
            f"fitness {elite['fitness']:.3f}  gen {generation}"
        )

    def axes_line(self) -> str:
        """The descriptor's NAMED axes, values verbatim."""
        if self.current() is None:
            return ""
        descriptor = self.current()["descriptor"]
        return "  ".join(
            f"{name} {value}"
            for name, value in zip(
                descriptor["names"], descriptor["values"]
            )
        )

    def components_line(self) -> str:
        """The fitness components, record fields verbatim."""
        if self.current() is None:
            return ""
        components = self.current().get("fitness_components") or {}
        return "  ".join(
            f"{name} {value:.3f}"
            for name, value in sorted(components.items())
        )
