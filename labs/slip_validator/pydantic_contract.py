import importlib
import importlib.util
import json
from enum import Enum
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator


AUTHORED_SCHEMA_PATH = Path("research/slip/slip.schema.json")
GENERATED_SCHEMA_PATH = Path("research/slip/slip_pydantic_model.schema.json")
REPORT_PATH = Path("data/slips/slip_pydantic_contract_stage0.json")
CONTRACT_STATUS = "research_slip_pydantic_contract_no_package_code"

UnitInterval = Annotated[float, Field(ge=0, le=1)]
PositiveInt = Annotated[int, Field(ge=1)]
ProfileId = Annotated[str, Field(min_length=1, pattern=r"^[a-z0-9_]+$")]
NonEmptyString = Annotated[str, Field(min_length=1)]


class PaletteId(str, Enum):
    lcd_green = "lcd_green"
    gameboy_gray = "gameboy_gray"
    amber_terminal = "amber_terminal"
    crt_blue = "crt_blue"
    pocket_plum = "pocket_plum"


class OrganRole(str, Enum):
    sensor = "sensor"
    expression = "expression"
    body_core = "body_core"


class GridContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed_palettes: Annotated[
        list[PaletteId],
        Field(min_length=1, json_schema_extra={"uniqueItems": True}),
    ]
    body_mass_min: PositiveInt
    body_mass_max: PositiveInt
    required_organ_roles: Annotated[
        list[OrganRole],
        Field(min_length=1, json_schema_extra={"uniqueItems": True}),
    ]

    @field_validator("body_mass_min", "body_mass_max", mode="before")
    @classmethod
    def reject_bool_for_body_mass(cls, value: object) -> object:
        if isinstance(value, bool):
            raise ValueError("body mass bounds must be integers, not bool")
        if not isinstance(value, int):
            raise ValueError("body mass bounds must be integers")
        return value

    @field_validator("allowed_palettes", "required_organ_roles")
    @classmethod
    def require_unique_items(cls, value: list[Enum]) -> list[Enum]:
        normalized = [item.value for item in value]
        if len(normalized) != len(set(normalized)):
            raise ValueError("array items must be unique")
        return value

    @model_validator(mode="after")
    def body_mass_bounds_are_ordered(self) -> "GridContract":
        if self.body_mass_max < self.body_mass_min:
            raise ValueError(
                "grid.body_mass_max must be greater than or equal to grid.body_mass_min"
            )
        return self


class MutationContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cell_mutation_rate_max: UnitInterval
    organ_shift_rate_max: UnitInterval
    palette_shift_rate_max: UnitInterval
    symmetry_break_rate_max: UnitInterval

    @field_validator(
        "cell_mutation_rate_max",
        "organ_shift_rate_max",
        "palette_shift_rate_max",
        "symmetry_break_rate_max",
        mode="before",
    )
    @classmethod
    def reject_bool_for_mutation_weights(cls, value: object) -> object:
        return _reject_numeric_bool(value)


class BehaviorContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    curiosity: UnitInterval
    neediness: UnitInterval
    sleepiness: UnitInterval

    @field_validator("curiosity", "neediness", "sleepiness", mode="before")
    @classmethod
    def reject_bool_for_behavior_weights(cls, value: object) -> object:
        return _reject_numeric_bool(value)


class SurvivalWeightsContract(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stability: UnitInterval
    novelty: UnitInterval
    bond: UnitInterval

    @field_validator("stability", "novelty", "bond", mode="before")
    @classmethod
    def reject_bool_for_survival_weights(cls, value: object) -> object:
        return _reject_numeric_bool(value)


class SLIPProfile(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        title="Mechagotchi SLIP Pydantic Contract",
    )

    slip_version: Literal["0.1.0"]
    profile_id: ProfileId
    name: NonEmptyString
    grid: GridContract
    mutation: MutationContract
    behavior: BehaviorContract
    survival_weights: SurvivalWeightsContract


def build_pydantic_contract_report(
    valid_paths: list[Path],
    failure_paths: list[Path],
    example_paths: list[Path],
    ad_hoc_payloads: list[tuple[str, dict]] | None = None,
) -> dict:
    ad_hoc_payloads = ad_hoc_payloads or []
    generated_schema = _generated_schema()
    valid_results = [_validate_path(path) for path in valid_paths]
    failure_results = [_validate_path(path) for path in failure_paths]
    example_results = [_validate_path(path) for path in example_paths]
    ad_hoc_results = [
        _validate_payload(source_name, payload) for source_name, payload in ad_hoc_payloads
    ]
    unexpected_valid_rejections = [
        result["source_path"] for result in valid_results if not result["ok"]
    ]
    unexpected_example_rejections = [
        result["source_path"] for result in example_results if not result["ok"]
    ]
    unexpected_failure_acceptances = [
        result["source_path"] for result in failure_results if result["ok"]
    ]
    observed_families = sorted(
        {
            family
            for result in valid_results + failure_results + example_results
            for family in result["error_families"]
        }
        | {
            family
            for result in ad_hoc_results
            for family in result["error_families"]
        }
    )
    return {
        "artifact_id": "slip_pydantic_contract_stage0",
        "status": CONTRACT_STATUS,
        "authored_schema_path": str(AUTHORED_SCHEMA_PATH).replace("\\", "/"),
        "generated_schema_path": str(GENERATED_SCHEMA_PATH).replace("\\", "/"),
        "pydantic_available": _module_available("pydantic"),
        "pydantic_version": _module_version("pydantic"),
        "jsonschema_available": _module_available("jsonschema"),
        "jsonschema_version": _module_version("jsonschema"),
        "dependency_policy": (
            "Pydantic is available in this environment, but no repository "
            "dependency manifest exists; package gates must declare it before "
            "requiring it."
        ),
        "contract_methods": [
            "BaseModel.model_validate",
            "BaseModel.model_validate_json",
            "BaseModel.model_json_schema",
            "ConfigDict(extra='forbid')",
            "Field bounds and patterns",
        ],
        "valid_profile_count": len(valid_paths),
        "failure_case_count": len(failure_paths),
        "example_profile_count": len(example_paths),
        "accepted_valid_profiles": sum(1 for result in valid_results if result["ok"]),
        "rejected_failure_cases": sum(1 for result in failure_results if not result["ok"]),
        "accepted_example_profiles": sum(1 for result in example_results if result["ok"]),
        "unexpected_valid_rejections": unexpected_valid_rejections,
        "unexpected_example_rejections": unexpected_example_rejections,
        "unexpected_failure_acceptances": unexpected_failure_acceptances,
        "observed_error_families": observed_families,
        "generated_schema_summary": _schema_summary(generated_schema),
        "valid_results": valid_results,
        "failure_results": failure_results,
        "example_results": example_results,
        "ad_hoc_results": ad_hoc_results,
        "related_migration_dependency_report": (
            "data/slips/slip_schema_migration_dependency_gate_stage0.json"
        ),
        "blocked_states": [
            "python_jsonschema_runtime_validation",
            "declared_dependency_manifest",
            "package_import_surface",
            "behavior_preview",
            "mutation_preview_ui",
        ],
    }


def write_pydantic_contract_artifacts(
    valid_paths: list[Path],
    failure_paths: list[Path],
    example_paths: list[Path],
) -> dict:
    generated_schema = _generated_schema()
    GENERATED_SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    GENERATED_SCHEMA_PATH.write_text(
        json.dumps(generated_schema, indent=2) + "\n",
        encoding="utf-8",
    )
    report = build_pydantic_contract_report(valid_paths, failure_paths, example_paths)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def _reject_numeric_bool(value: object) -> object:
    if isinstance(value, bool):
        raise ValueError("numeric weights must be numbers, not bool")
    if not isinstance(value, int | float):
        raise ValueError("numeric weights must be numbers")
    return value


def _validate_path(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return _validate_payload(str(path).replace("\\", "/"), payload)


def _validate_payload(source_name: str, payload: dict) -> dict:
    try:
        model = SLIPProfile.model_validate(payload)
        return {
            "source_path": source_name,
            "ok": True,
            "profile_id": model.profile_id,
            "errors": [],
            "error_families": [],
        }
    except ValidationError as error:
        errors = [_normalize_error(item) for item in error.errors()]
        return {
            "source_path": source_name,
            "ok": False,
            "errors": errors,
            "error_families": sorted({item["family"] for item in errors}),
        }


def _normalize_error(error: dict) -> dict:
    message = str(error.get("msg", ""))
    location = ".".join(str(part) for part in error.get("loc", ())) or "$"
    error_type = str(error.get("type", ""))
    family = _error_family(error_type, message)
    return {
        "family": family,
        "path": location,
        "type": error_type,
        "message": message,
    }


def _error_family(error_type: str, message: str) -> str:
    if "numeric weights must be numbers, not bool" in message:
        return "semantic_numeric_bool"
    if "numeric weights must be numbers" in message:
        return "schema_type"
    if "body mass bounds must be integers" in message:
        return "schema_type"
    if "grid.body_mass_max must be greater" in message:
        return "semantic_body_mass_bounds"
    if error_type == "missing":
        return "schema_required"
    if error_type in {"extra_forbidden"}:
        return "schema_additional_properties"
    if error_type in {"literal_error", "enum"}:
        return "schema_enum"
    if error_type in {"greater_than_equal", "less_than_equal"}:
        return "schema_range"
    if error_type in {"too_short", "list_too_short"}:
        return "schema_min_items"
    if error_type in {
        "string_type",
        "int_type",
        "float_type",
        "list_type",
        "model_type",
        "dict_type",
    }:
        return "schema_type"
    if "Input should be" in message and "valid" in message:
        return "schema_type"
    if "array items must be unique" in message:
        return "schema_unique_items"
    return "semantic_validation"


def _generated_schema() -> dict:
    schema = SLIPProfile.model_json_schema(mode="validation")
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = "https://mechagotchi.local/schema/slip/pydantic/0.1.0"
    return schema


def _schema_summary(schema: dict) -> dict:
    return {
        "top_level_required": sorted(schema.get("required", [])),
        "top_level_forbid_extra": schema.get("additionalProperties") is False,
        "palette_values": sorted(item.value for item in PaletteId),
        "organ_role_values": sorted(item.value for item in OrganRole),
        "behavior_required": sorted(
            schema["$defs"]["BehaviorContract"].get("required", [])
        ),
        "survival_required": sorted(
            schema["$defs"]["SurvivalWeightsContract"].get("required", [])
        ),
        "mutation_required": sorted(
            schema["$defs"]["MutationContract"].get("required", [])
        ),
    }


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _module_version(name: str) -> str | None:
    if not _module_available(name):
        return None
    module = importlib.import_module(name)
    return str(getattr(module, "__version__", "unknown"))


def main() -> None:
    valid_paths = sorted(Path("data/slips/valid").glob("*.json"))
    failure_paths = sorted(Path("data/slips/failure_cases").glob("*.json"))
    example_paths = sorted(Path("research/slip/slip_examples").glob("*.json"))
    report = write_pydantic_contract_artifacts(
        valid_paths=valid_paths,
        failure_paths=failure_paths,
        example_paths=example_paths,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
