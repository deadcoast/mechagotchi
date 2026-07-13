"""The repertoire browser — species memory made visible (F13, MVP 0.3).

Phase E proved the repertoire (the MAP-Elites archive at documented
scale; E5's recurrent families are the species-memory substrate); the
era bench fills it every era. This browser SURFACES it: page through
the archive's elites in its own deterministic niche order, each one
drawn from its real render packet under the campaign's covenant, each
caption built from the elite RECORD verbatim — the descriptor's named
axes, the fitness and its components, the lineage generation. The
browser never re-derives a statistic (DR 0021's first law).

The in-memory campaign's eras are the source; the ledger persists the
same records verbatim (DR 0022), and ledger-sourced browsing across
restarts lands with the campaign-resume rung (F17) — named, not
smuggled.
"""

from __future__ import annotations

from mecha_engine.genome import render_packet_v2


class RepertoireBrowser:
    """Scrub the bloodline's archive, era by era, niche by niche."""

    def __init__(self, keeper_campaign) -> None:
        if not keeper_campaign.eras:
            raise ValueError("no era to browse yet — run one (E)")
        self.campaign = keeper_campaign
        self.era_index = len(keeper_campaign.eras) - 1
        self.index = 0

    # -- position ---------------------------------------------------------

    @property
    def elites(self) -> list[dict]:
        return self.campaign.eras[self.era_index]["elites"]

    @property
    def count(self) -> int:
        return len(self.elites)

    def current(self) -> dict:
        return self.elites[self.index]

    def step(self) -> int:
        self.index = min(self.count - 1, self.index + 1)
        return self.index

    def back(self) -> int:
        self.index = max(0, self.index - 1)
        return self.index

    def next_era(self) -> int:
        if self.era_index < len(self.campaign.eras) - 1:
            self.era_index += 1
            self.index = 0
        return self.era_index

    def previous_era(self) -> int:
        if self.era_index > 0:
            self.era_index -= 1
            self.index = 0
        return self.era_index

    # -- display (record fields verbatim) -----------------------------------

    def packet(self) -> dict:
        """The elite's body as a real render packet under the
        campaign's covenant (idle display; the vocabulary gate stays
        the engine's)."""
        return render_packet_v2(
            self.current()["grid"],
            None,
            slip_profile=self.campaign.campaign["slip_profile"],
        )

    def caption(self) -> str:
        elite = self.current()
        era = self.campaign.eras[self.era_index]
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
        descriptor = self.current()["descriptor"]
        return "  ".join(
            f"{name} {value}"
            for name, value in zip(
                descriptor["names"], descriptor["values"]
            )
        )

    def components_line(self) -> str:
        """The fitness components, record fields verbatim."""
        components = self.current().get("fitness_components") or {}
        return "  ".join(
            f"{name} {value:.3f}"
            for name, value in sorted(components.items())
        )
