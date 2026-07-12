"""Mechagotchi — the playable game client (GAME build, DR 0033).

The second of the two builds (`docs/gap-analysis.md` §0): a desktop
client a player launches and plays, showcasing the Mechagotchi
Computational Life Engine. The first law (DR 0021): every number,
event, and image shown is engine truth — this package imports
`mecha_engine` and never invents a displayed value.

Boundary law (DR 0033 decision 3): `mecha_game` imports `mecha_engine`
and never `labs`; no ``sys.path`` text lives anywhere in this tree —
the dev launcher (`game/run_game.py`) and the tests own the path
bootstrap for repo checkouts.
"""

__all__ = ["__version__"]

__version__ = "0.1.0.dev0"
