"""F5 — build the installable Mechagotchi release (DR 0033/PyInstaller).

One-directory build: the executable plus the bundled data corpus the
client's walk-up resolution finds through ``sys._MEIPASS`` (the seed
corpus, the LCD covenant, the adopted readability model). Saves go to
the player's own ``~/.mechagotchi`` (the keeper-dir default outside a
repo checkout). Dev harness, repo checkout only:

    uv run python -B game/build_release.py [--dist DIR]

Verify the build the way a player would:

    dist/Mechagotchi/Mechagotchi.exe            # play
    dist/Mechagotchi/Mechagotchi.exe --ticks 3  # bounded check
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAME_SRC = ROOT / "game" / "src"

BUNDLED_DATA = [
    ("data/seed_grids_16x16", "data/seed_grids_16x16"),
    ("data/slips/valid/slip_lcd_seed.json", "data/slips/valid"),
    (
        "data/readability_benchmark/adopted_readability_model.json",
        "data/readability_benchmark",
    ),
]


def build(
    dist_dir: Path, work_dir: Path, *, windowed: bool = False
) -> Path:
    import PyInstaller.__main__ as pyinstaller

    entry = work_dir / "release_entry.py"
    work_dir.mkdir(parents=True, exist_ok=True)
    entry.write_text(
        "import sys\n"
        "from mecha_game.app import run\n\n"
        'if __name__ == "__main__":\n'
        "    sys.exit(run())\n",
        encoding="utf-8",
    )
    separator = ";" if sys.platform == "win32" else ":"
    add_data = [
        f"--add-data={ROOT / source}{separator}{destination}"
        for source, destination in BUNDLED_DATA
    ]
    pyinstaller.run(
        [
            str(entry),
            "--name=Mechagotchi",
            "--onedir",
            "--noconfirm",
            "--clean",
            f"--distpath={dist_dir}",
            f"--workpath={work_dir / 'build'}",
            f"--specpath={work_dir}",
            f"--paths={GAME_SRC}",
            f"--paths={ROOT / 'packages' / 'mecha_engine' / 'src'}",
            # Console stays the default (diagnostics visible — the F5
            # report's note); --windowed is the player-facing build.
            "--windowed" if windowed else "--console",
            *add_data,
        ]
    )
    return dist_dir / "Mechagotchi"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dist", type=Path, default=ROOT / "game" / "dist"
    )
    parser.add_argument(
        "--work", type=Path, default=ROOT / "game" / "release_work"
    )
    parser.add_argument(
        "--windowed",
        action="store_true",
        help="build without a console window (the player-facing form)",
    )
    args = parser.parse_args()
    bundle = build(args.dist, args.work, windowed=args.windowed)
    print(f"built {bundle}")
