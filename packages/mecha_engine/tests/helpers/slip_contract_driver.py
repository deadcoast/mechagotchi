"""SLIP contract probe driver executed against the package surface.

Traceability: research/decision_records/0027-slip-module-disposition.md
(the port's gates) and decision records 0012/0013 (the schema ladder the
fields implement). ``tests/test_slip_contract.py`` launches this script
in a subprocess whose PYTHONPATH points at the package ``src`` directory
(the same documented import mechanics as every other contract suite), so
every probe exercises ``mecha_engine.slip`` only — never repository-root
or research lab modules.

Fixtures are the frozen repository corpora: ``data/slips/valid``,
``data/slips/failure_cases``, and the SLIP zoo (``data/slips/zoo``) —
the same corpus DR 0027's gate-1 reconciliation swept. The driver prints
a single JSON report on stdout.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

from mecha_engine.slip import SlipResult, is_grid_aligned, validate_slip


def _load_dir(path: Path) -> list[tuple[str, dict]]:
    return [
        (file.name, json.loads(file.read_text(encoding="utf-8")))
        for file in sorted(path.glob("*.json"))
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()

    valid = _load_dir(repo_root / "data" / "slips" / "valid")
    failures = _load_dir(repo_root / "data" / "slips" / "failure_cases")
    zoo = _load_dir(repo_root / "data" / "slips" / "zoo")
    seed = json.loads(
        (repo_root / "data" / "seed_grids" / "mg_seed_001.json").read_text(
            encoding="utf-8"
        )
    )
    lcd = next(p for n, p in valid if n == "slip_lcd_seed.json")

    # Verdicts over the frozen corpora.
    valid_ok = {name: validate_slip(p).ok for name, p in valid}
    failure_ok = {name: validate_slip(p).ok for name, p in failures}
    zoo_ok = {name: validate_slip(p).ok for name, p in zoo}

    # SlipResult shape.
    result = validate_slip(lcd)
    shape_ok = (
        isinstance(result, SlipResult)
        and isinstance(result.ok, bool)
        and isinstance(result.errors, list)
    )

    # Ladder-field rejections (the v0.2 rungs must be version-gated and
    # bounded — a sample per rung).
    ladder_rejections = {}
    for key, payload in (
        ("v01_carrying_ladder_field", dict(lcd, deliberation={"max_ticks": 4})),
        (
            "deliberation_out_of_bounds",
            dict(
                lcd,
                slip_version="0.2.0",
                deliberation={"max_ticks": 99, "confidence_threshold": 0.7},
            ),
        ),
        (
            "species_class_bad_case",
            dict(lcd, slip_version="0.2.0", species_class="Bad Case"),
        ),
        (
            "empty_animation_vocab",
            dict(
                lcd,
                slip_version="0.2.0",
                visual_grammar={"animation_vocab": []},
            ),
        ),
    ):
        verdict = validate_slip(payload)
        ladder_rejections[key] = {
            "rejected": not verdict.ok,
            "has_errors": bool(verdict.errors),
        }

    # Alignment: the lcd seed aligns with its own profile; a palette the
    # profile forbids is rejected with a named error.
    aligned = is_grid_aligned(seed, lcd)
    misaligned_profile = deepcopy(lcd)
    misaligned_profile["grid"]["allowed_palettes"] = ["amber_terminal"]
    misaligned = is_grid_aligned(seed, misaligned_profile)

    # Determinism + no input mutation.
    seed_pristine = deepcopy(seed)
    lcd_pristine = deepcopy(lcd)
    repeat = validate_slip(lcd)
    repeat_alignment = is_grid_aligned(seed, lcd)

    json.dump(
        {
            "valid_fixture_count": len(valid),
            "valid_all_ok": all(valid_ok.values()),
            "failure_case_count": len(failures),
            "failure_all_rejected": not any(failure_ok.values()),
            "zoo_count": len(zoo),
            "zoo_ok_count": sum(1 for ok in zoo_ok.values() if ok),
            "slip_result_shape_ok": shape_ok,
            "ladder_rejections": ladder_rejections,
            "lcd_seed_aligned": aligned.ok,
            "misaligned_rejected": not misaligned.ok,
            "misaligned_error_names_palette": any(
                "palette" in error for error in misaligned.errors
            ),
            "deterministic_repeat_identical": (
                repeat.ok == result.ok
                and repeat.errors == result.errors
                and repeat_alignment.ok == aligned.ok
                and repeat_alignment.errors == aligned.errors
            ),
            "inputs_mutated": seed != seed_pristine or lcd != lcd_pristine,
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
