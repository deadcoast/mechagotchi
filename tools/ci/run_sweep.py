"""The full verification sweep as ONE runner (G1, DR 0034).

The same sweep locally and in CI, stdlib-only: every lab suite
(discovered), the package suite, the workshop suite, the CLI suite,
the game suite, and JSON validation over every committed data
artifact. Everything runs with THE CURRENT interpreter — in CI the
venv built from the runner's set-up CPython (`UV_PYTHON`, DR 0034),
so the zlib provenance is explicit and the foreign-fixture byte pins
condition themselves honestly. pygame suites run headless via the
SDL dummy driver.

    python -B tools/ci/run_sweep.py [--quick]

``--quick`` skips the ~2-minute workshop suite (a LOCAL convenience;
CI always runs everything).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SUITES: list[tuple[str, Path]] = [
    ("package", ROOT / "packages" / "mecha_engine" / "tests"),
    ("cli", ROOT / "tools" / "mechas_cli" / "tests"),
    ("game", ROOT / "game" / "tests"),
    ("workshop", ROOT / "workshop" / "tests"),
]


def run_suite(name: str, directory: Path) -> tuple[bool, str]:
    env = dict(os.environ)
    env.setdefault("SDL_VIDEODRIVER", "dummy")
    started = time.time()
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            str(directory),
            "-p",
            "test_*.py",
        ],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        env=env,
    )
    elapsed = time.time() - started
    tail = (result.stderr or result.stdout).strip().splitlines()
    verdict = tail[-1] if tail else "(no output)"
    summary = f"{verdict}  [{elapsed:.1f}s]"
    return result.returncode == 0, summary


def validate_artifacts() -> tuple[bool, str]:
    started = time.time()
    checked = 0
    for path in sorted((ROOT / "data").rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            return False, f"{path.relative_to(ROOT).as_posix()}: {error}"
        checked += 1
    elapsed = time.time() - started
    return True, f"{checked} JSON artifacts valid  [{elapsed:.1f}s]"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quick",
        action="store_true",
        help="skip the workshop suite (local convenience only)",
    )
    args = parser.parse_args()

    plan: list[tuple[str, Path]] = []
    for lab in sorted((ROOT / "labs").iterdir()):
        if lab.is_dir() and any(lab.glob("test_*.py")):
            plan.append((f"lab:{lab.name}", lab))
    for name, directory in SUITES:
        if args.quick and name == "workshop":
            print(f"{'workshop':32} SKIPPED (--quick)")
            continue
        plan.append((name, directory))

    failures: list[str] = []
    for name, directory in plan:
        ok, summary = run_suite(name, directory)
        print(f"{name:32} {'OK ' if ok else 'FAIL'} {summary}")
        if not ok:
            failures.append(name)

    ok, summary = validate_artifacts()
    print(f"{'data artifacts':32} {'OK ' if ok else 'FAIL'} {summary}")
    if not ok:
        failures.append("data artifacts")

    if failures:
        print(f"\nSWEEP FAILED: {', '.join(failures)}")
        return 1
    print("\nSWEEP GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
