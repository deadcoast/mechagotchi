"""Build the supported Windows x64 one-directory Mechagotchi player.

Run with this checkout's .venv Python. The EXE, _internal and artifact manifest
travel together. Each build requires a new output and work directory; no existing
release is overwritten. A standalone Python wheel is a code/developer form,
not this complete player distribution.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import platform
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
GAME_SRC = ROOT / "game/src"
from release_payload import BUNDLED_DATA, DEPENDENCIES, HELPER_MODULES, HELPER_PATHS, source_identity, stage_payload, write_artifact_manifest


def build(dist_dir: Path, work_dir: Path, *, windowed: bool = False) -> Path:
    if sys.platform != "win32" or struct.calcsize("P") != 8 or platform.machine().lower() not in {"amd64", "x86_64"}:
        raise RuntimeError("This player target is Windows x64 one-directory delivery")
    dist_dir, work_dir = Path(dist_dir).resolve(), Path(work_dir).resolve()
    bundle = dist_dir / "Mechagotchi"
    if bundle.exists() or work_dir.exists():
        raise FileExistsError("Choose new dist/work directories; existing release evidence is preserved")
    work_dir.mkdir(parents=True)
    manifest = stage_payload(work_dir / "runtime-payload")
    entry = work_dir / "release_entry.py"
    entry.write_text("import sys\nfrom mecha_game.app import run\n\nif __name__ == '__main__':\n    sys.exit(run())\n", encoding="utf-8")
    import PyInstaller.__main__ as pyinstaller
    pyinstaller.run([
        str(entry), "--name=Mechagotchi", "--onedir", "--clean", "--noupx",
        f"--distpath={dist_dir}", f"--workpath={work_dir / 'build'}", f"--specpath={work_dir}",
        f"--paths={GAME_SRC}", f"--paths={ROOT / 'packages/mecha_engine/src'}",
        *[f"--paths={folder}" for folder in HELPER_PATHS],
        *[f"--hidden-import={name}" for name in HELPER_MODULES],
        *[f"--copy-metadata={name}" for name in DEPENDENCIES if name != "pyinstaller"],
        "--collect-submodules=mecha_engine",
        "--windowed" if windowed else "--console",
        f"--add-data={work_dir / 'runtime-payload'};.",
    ])
    after = source_identity()
    if after["files"] != manifest["source"]["files"] or after["head"] != manifest["source"]["head"]:
        raise RuntimeError("Runtime sources changed during the build; artifact is not verified. Freeze writers and rebuild to a fresh directory")
    write_artifact_manifest(bundle, manifest)
    return bundle


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, default=ROOT / "game/dist")
    parser.add_argument("--work", type=Path, default=ROOT / "game/release_work")
    parser.add_argument("--windowed", action="store_true", help="build the player without a console window")
    args = parser.parse_args()
    print(f"built {build(args.dist, args.work, windowed=args.windowed)}")
