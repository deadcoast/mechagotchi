"""Dev launcher — run the Mechagotchi client from a repo checkout.

Usage (pygame-ce provisioned via ``uv sync --group game``):

    uv run python -B game/run_game.py [--ticks N] [--scale PX] [--fps N]

The path bootstrap lives HERE, never inside ``game/src`` (DR 0033
decision 3 — the engine package's boundary discipline, applied to the
game). The installed form (`mechagotchi` entry point) resolves real
dependencies instead.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _src in (ROOT / "game" / "src", ROOT / "packages" / "mecha_engine" / "src"):
    if str(_src) not in sys.path:
        sys.path.insert(0, str(_src))

from mecha_game.app import run  # noqa: E402

if __name__ == "__main__":
    sys.exit(run())
