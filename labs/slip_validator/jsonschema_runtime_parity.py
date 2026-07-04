"""Runtime JSON Schema validation parity gate.

Decision record 0005 declared `jsonschema` in the pyproject lab dependency
group. This lab is the executable evidence that unblocks lab-level runtime
JSON Schema validation: it runs `Draft202012Validator` over the full Stage 0
SLIP corpus and proves parity with the dependency-free structural validator,
recording the one known semantic gap (body-mass ordering is a semantic check
the authored JSON Schema cannot express, so the layered semantic checks stay
on top of schema validation).
"""

import argparse
import importlib.metadata
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from slip_validator import validate_profile

ROOT = Path(__file__).resolve().parents[2]

AUTHORED_SCHEMA_PATH = ROOT / "research/slip/slip.schema.json"
REPORT_PATH = ROOT / "data/slips/slip_jsonschema_runtime_parity_stage0.json"
ARTIFACT_ID = "slip_jsonschema_runtime_parity_stage0"
STATUS = "research_slip_jsonschema_runtime_parity_no_package_code"

# Failure cases that the dependency-free validator rejects through a
# *semantic* check the authored JSON Schema cannot express. jsonschema alone
# is expected to accept these; the layered semantic checks reject them.
KNOWN_SEMANTIC_GAP_STEMS = {"slip_body_mass_bounds_reversed"}


def build_parity_report(
    valid_paths: list[Path],
    failure_paths: list[Path],
    example_paths: list[Path],
) -> dict:
    schema = json.loads(AUTHORED_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    results = []
    disagreements = []
    semantic_gap_cases = []
    for group, paths in [
        ("valid", valid_paths),
        ("failure", failure_paths),
        ("example", example_paths),
    ]:
        for path in paths:
            payload = json.loads(path.read_text(encoding="utf-8"))
            jsonschema_errors = sorted(
                validator.iter_errors(payload), key=lambda error: list(error.absolute_path)
            )
            jsonschema_ok = not jsonschema_errors
            structural = validate_profile(payload, source_path=path)
            layered_ok = jsonschema_ok and structural["ok"]
            source = path.relative_to(ROOT).as_posix()
            result = {
                "source_path": source,
                "group": group,
                "jsonschema_ok": jsonschema_ok,
                "structural_ok": structural["ok"],
                "layered_ok": layered_ok,
                "jsonschema_error_paths": [
                    "/".join(str(part) for part in error.absolute_path) or "$"
                    for error in jsonschema_errors
                ],
                "structural_error_families": structural["error_families"],
            }
            results.append(result)
            if jsonschema_ok != structural["ok"]:
                if path.stem in KNOWN_SEMANTIC_GAP_STEMS:
                    semantic_gap_cases.append(source)
                else:
                    disagreements.append(result)

    return {
        "artifact_id": ARTIFACT_ID,
        "status": STATUS,
        "date": "2026-07-04",
        "purpose": (
            "Prove Draft 2020-12 runtime validation of SLIP profiles agrees "
            "with the dependency-free Stage 0 validator over the full corpus, "
            "as the evidence for unblocking lab-level runtime JSON Schema "
            "validation (decision record 0005)."
        ),
        "authored_schema_path": AUTHORED_SCHEMA_PATH.relative_to(ROOT).as_posix(),
        "jsonschema_version": importlib.metadata.version("jsonschema"),
        "schema_check": "Draft202012Validator.check_schema passed",
        "corpus_counts": {
            "valid": len(valid_paths),
            "failure": len(failure_paths),
            "example": len(example_paths),
        },
        "parity": {
            "agreements": sum(
                1 for result in results if result["jsonschema_ok"] == result["structural_ok"]
            ),
            "total": len(results),
            "unexplained_disagreements": disagreements,
            "known_semantic_gap_cases": sorted(semantic_gap_cases),
            "semantic_gap_policy": (
                "Schema validation is the first layer only; the structural "
                "validator's semantic checks (body-mass ordering) remain "
                "layered on top. layered_ok is the decision surface."
            ),
        },
        "layered_outcomes": {
            "valid_accepted": sum(
                1 for result in results if result["group"] == "valid" and result["layered_ok"]
            ),
            "examples_accepted": sum(
                1 for result in results if result["group"] == "example" and result["layered_ok"]
            ),
            "failures_rejected": sum(
                1
                for result in results
                if result["group"] == "failure" and not result["layered_ok"]
            ),
        },
        "results": results,
        "closed_states": [
            "lab_runtime_jsonschema_validation",
            "jsonschema_structural_validator_parity",
        ],
        "blocked_states": [
            "package_runtime_jsonschema_validation",
            "package_import_surface",
        ],
        "decision": "adopt_layered_runtime_schema_validation_for_labs",
        "sources": [
            "research/decision_records/0005-declare-lab-dependency-manifest.md",
            "pyproject.toml",
        ],
    }


def write_parity_report(
    valid_paths: list[Path],
    failure_paths: list[Path],
    example_paths: list[Path],
) -> dict:
    report = build_parity_report(valid_paths, failure_paths, example_paths)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--valid-dir", type=Path, default=ROOT / "data/slips/valid")
    parser.add_argument("--failure-dir", type=Path, default=ROOT / "data/slips/failure_cases")
    parser.add_argument(
        "--examples-dir", type=Path, default=ROOT / "research/slip/slip_examples"
    )
    args = parser.parse_args()

    report = write_parity_report(
        sorted(args.valid_dir.glob("*.json")),
        sorted(args.failure_dir.glob("*.json")),
        sorted(args.examples_dir.glob("*.json")),
    )
    print(json.dumps({key: report[key] for key in ["parity", "layered_outcomes"]}, indent=2))


if __name__ == "__main__":
    main()
