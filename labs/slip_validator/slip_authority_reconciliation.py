"""SLIP authority reconciliation (F2, DR 0027 gate 1) — the evidence.

Before the four private ``_slip`` mirrors collapsed into
``mecha_engine.slip``, gate 1 demanded proof they were behaviorally
identical. The pre-collapse five-way sweep (lab authority + the four
mirrors) measured ZERO divergences — recorded below as the historical
gate-1 measurement. This lab keeps the reconciliation ALIVE for the
surviving pair: it sweeps the Stage 0 lab authority against the
promoted ``mecha_engine.slip`` over the whole frozen profile corpus
(valid + failure_cases + the SLIP zoo), systematic corruptions of every
profile, and grid alignment across the seed corpus, and writes the
stage-0 artifact the promotion gate judges.

Deterministic; stdlib + the package surface + the lab authority.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRID_GENOME = ROOT / "labs" / "grid_genome"
PACKAGE_SRC = ROOT / "packages" / "mecha_engine" / "src"
for path in [GRID_GENOME, PACKAGE_SRC]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import slip as lab_slip  # noqa: E402
from corpus_builder import build_seed_grids  # noqa: E402

from mecha_engine import slip as package_slip  # noqa: E402

ARTIFACT_ID = "slip_authority_reconciliation_stage0"
REPORT_DATE = "2026-07-07"
DEFAULT_OUTPUT_DIR = ROOT / "data" / "slips"

# The pre-collapse five-way measurement (lab + generation/lifecycle/
# repair/runtime mirrors), run 2026-07-07 before the mirrors were
# deleted: zero divergences in both sweeps.
GATE_1_HISTORY = {
    "implementations": [
        "labs/grid_genome/slip.py",
        "mecha_engine.generation._slip",
        "mecha_engine.lifecycle._slip",
        "mecha_engine.repair._slip",
        "mecha_engine.runtime._slip",
    ],
    "validate_cases": "118 profiles x 5 cases (as-is + 4 corruptions)",
    "alignment_cases": "104 valid profiles x 20 seeds",
    "validate_divergences": 0,
    "alignment_divergences": 0,
}


def _profiles() -> list[tuple[str, dict]]:
    paths = []
    for sub in ("valid", "failure_cases", "zoo"):
        paths.extend(sorted((ROOT / "data" / "slips" / sub).glob("*.json")))
    return [
        (path.name, json.loads(path.read_text(encoding="utf-8")))
        for path in paths
    ]


def _corruptions(profile: dict):
    yield dict(profile, slip_version="9.9.9")
    stripped = json.loads(json.dumps(profile))
    stripped.pop("grid", None)
    yield stripped
    bad_species = json.loads(json.dumps(profile))
    bad_species["species_class"] = "Bad Case"
    yield bad_species
    bad_delib = json.loads(json.dumps(profile))
    bad_delib.setdefault("deliberation", {})["max_ticks"] = 99
    yield bad_delib


def run_reconciliation() -> dict:
    profiles = _profiles()
    seeds = build_seed_grids()
    validate_cases = 0
    validate_divergences = 0
    for _, profile in profiles:
        for case in [profile, *list(_corruptions(profile))]:
            validate_cases += 1
            lab = lab_slip.validate_slip(case)
            pkg = package_slip.validate_slip(case)
            if (lab.ok, lab.errors) != (pkg.ok, pkg.errors):
                validate_divergences += 1
    valid_profiles = [
        p for _, p in profiles if lab_slip.validate_slip(p).ok
    ]
    alignment_cases = 0
    alignment_divergences = 0
    for profile in valid_profiles:
        for seed in seeds[:20]:
            alignment_cases += 1
            lab = lab_slip.is_grid_aligned(seed, profile)
            pkg = package_slip.is_grid_aligned(seed, profile)
            if (lab.ok, lab.errors) != (pkg.ok, pkg.errors):
                alignment_divergences += 1
    return {
        "profile_count": len(profiles),
        "valid_profile_count": len(valid_profiles),
        "validate_cases": validate_cases,
        "validate_divergences": validate_divergences,
        "alignment_cases": alignment_cases,
        "alignment_divergences": alignment_divergences,
        "authorities_identical": validate_divergences == 0
        and alignment_divergences == 0,
    }


def build_reconciliation_report(sweep: dict) -> dict:
    return {
        "artifact_id": ARTIFACT_ID,
        "status": "stage0_complete",
        "date": REPORT_DATE,
        "purpose": (
            "F2 (DR 0027 gate 1, kept alive): the Stage 0 lab SLIP "
            "authority and the promoted mecha_engine.slip must agree "
            "exactly — verdicts and error strings — over the frozen "
            "profile corpus, systematic corruptions, and seed alignment."
        ),
        "source_artifacts": [
            "research/decision_records/0027-slip-module-disposition.md",
            "labs/grid_genome/slip.py",
            "data/slips/",
        ],
        "gate_1_pre_collapse_measurement": GATE_1_HISTORY,
        "metrics": sweep,
        "closed_states": [
            "gate_1_five_way_reconciliation_measured_zero_divergences",
            "lab_vs_package_pair_sweep_permanent",
        ],
        "blocked_states": [],
        "decision": {
            "status": "slip_authorities_identical"
            if sweep["authorities_identical"]
            else "slip_authorities_diverged",
            "adoption": "package_slip_authority_evidence",
            "reason": (
                f"{sweep['validate_cases']} validate cases and "
                f"{sweep['alignment_cases']} alignment cases with "
                f"{sweep['validate_divergences']}/"
                f"{sweep['alignment_divergences']} divergences — the "
                "promoted module IS the authority's behavior."
            ),
        },
        "next_research_step": (
            "None — the parity pin (test_package_slip_parity.py) runs "
            "this sweep in every suite; rerun this lab after any "
            "authority change to refresh the artifact."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sweep the SLIP authorities for divergence (F2)."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    report = build_reconciliation_report(run_reconciliation())
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "slip_authority_reconciliation_stage0.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "artifact_id": report["artifact_id"],
                "decision": report["decision"]["status"],
                **report["metrics"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
