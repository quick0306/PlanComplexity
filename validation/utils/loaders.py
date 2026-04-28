from __future__ import annotations

import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path
import re
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from metric_registry import SUPPORTED_VALIDATION_DOMAINS
import yaml

from validation_models import (
    ExpectedRangeRecord,
    MetricGroupRecord,
    MetricSpecRecord,
    ReferenceCaseProvenanceRecord,
    ReferenceCaseRecord,
    ToleranceOverrideRecord,
    ValidationProfileRecord,
)


class _MetricGroupDefinition:
    def __init__(self, *, group_key: str, platform: str, label: str, description: str) -> None:
        self.group_key = group_key
        self.platform = platform
        self.label = label
        self.description = description


_VALIDATION_LEVELS = {
    "Formula-exact",
    "Reference-case exact",
    "Derived-equivalent",
    "Association-only",
}
_COMPARISON_CLASSES = {
    "exact-equivalent",
    "derived-equivalent",
    "association-only",
    "not-comparable",
}
_EXPECTED_RANGE_KINDS = {
    "nonnegative",
    "unit_interval",
    "signed_unit_interval",
    "unbounded",
}
_CASE_CLASSES = {"canonical", "edge"}
_FORMAT_CHECKER = FormatChecker()
_RFC3339_DATE_TIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
_SPECS_DIR = Path(__file__).resolve().parents[1] / "specs"
_SCHEMAS_DIR = Path(__file__).resolve().parents[1] / "schemas"
_REFERENCE_CASES_DIR = Path(__file__).resolve().parents[1] / "reference_cases"


@_FORMAT_CHECKER.checks("date-time")
def _is_date_time(value: object) -> bool:
    if not isinstance(value, str):
        return True
    if not _RFC3339_DATE_TIME.match(value):
        return False
    candidate = value.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(candidate)
    except ValueError:
        return False
    return True


def load_metric_specs() -> list[MetricSpecRecord]:
    payload = _load_payload("metric_specs.yaml")
    _validate_schema(payload, "metric_spec.schema.json")
    entries = _require_sequence(payload, "metric_specs", "metric_specs.yaml")
    group_definitions = _load_metric_group_definitions()
    records: list[MetricSpecRecord] = []
    for index, entry in enumerate(entries):
        context = f"metric_specs.yaml metric_specs[{index}]"
        row = _require_mapping(entry, context)
        platform = _require_string(row, "platform", context)
        mode = _require_string(row, "mode", context)
        if mode != platform:
            raise ValueError(
                f"{context} has mode mismatch: platform '{platform}' vs mode '{mode}'."
            )
        group_key = _require_string(row, "group_key", context)
        metric_key = _require_metric_key(row, context)
        label = _require_string(row, "label", context)
        unit = _require_string(row, "unit", context)
        aggregation_scope = _require_string(row, "aggregation_scope", context)
        normalization_basis = _require_string(row, "normalization_basis", context)
        validation_level = _require_choice(row, "validation_level", context, _VALIDATION_LEVELS)
        comparison_class = _require_choice(row, "comparison_class", context, _COMPARISON_CLASSES)
        clinical_readiness = _require_string(row, "clinical_readiness", context)
        assumptions = _require_string_tuple(row, "assumptions", context)
        exclusions = _require_string_tuple(row, "exclusions", context)

        if group_key not in group_definitions:
            raise ValueError(
                f"{context} references unknown metric group '{group_key}'."
            )
        group_definition = group_definitions[group_key]
        if group_definition.platform != platform:
            raise ValueError(
                f"{context} has platform mismatch for group '{group_key}': "
                f"metric platform '{platform}' vs group platform '{group_definition.platform}'."
            )

        records.append(
            MetricSpecRecord(
                platform=platform,
                mode=mode,
                group_key=group_key,
                metric_key=metric_key,
                label=label,
                unit=unit,
                aggregation_scope=aggregation_scope,
                normalization_basis=normalization_basis,
                validation_level=validation_level,
                comparison_class=comparison_class,
                default_tolerance_abs=_require_float_or_none(row, "default_tolerance_abs", context),
                default_tolerance_rel=_require_float_or_none(row, "default_tolerance_rel", context),
                expected_range=_require_expected_range(row, "expected_range", context),
                clinical_readiness=clinical_readiness,
                known_noncomparability=_require_string_tuple(row, "known_noncomparability", context),
                comparable_to=_require_string_tuple(row, "comparable_to", context),
                assumptions=assumptions,
                exclusions=exclusions,
            )
        )

    _require_unique(
        [(record.platform, record.metric_key) for record in records],
        "metric spec key",
    )
    return records


def load_metric_groups() -> list[MetricGroupRecord]:
    group_definitions = _load_metric_group_definitions()
    metric_inventory: dict[str, list[str]] = {}
    for record in load_metric_specs():
        metric_inventory.setdefault(record.group_key, []).append(record.metric_key)

    records: list[MetricGroupRecord] = []
    for definition in group_definitions.values():
        metric_keys = tuple(sorted(metric_inventory.get(definition.group_key, [])))
        if not metric_keys:
            raise ValueError(
                f"Metric group '{definition.group_key}' has no metric specs."
            )
        records.append(
            MetricGroupRecord(
                group_key=definition.group_key,
                platform=definition.platform,
                label=definition.label,
                description=definition.description,
                metric_keys=metric_keys,
            )
        )
    return records


def load_validation_profiles() -> list[ValidationProfileRecord]:
    payload = _load_payload("validation_profiles.yaml")
    entries = _require_sequence(payload, "validation_profiles", "validation_profiles.yaml")
    group_keys = {group.group_key for group in load_metric_groups()}
    records: list[ValidationProfileRecord] = []
    for index, entry in enumerate(entries):
        context = f"validation_profiles.yaml validation_profiles[{index}]"
        row = _require_mapping(entry, context)
        records.append(
            ValidationProfileRecord(
                profile_key=_require_string(row, "profile_key", context),
                description=_require_string(row, "description", context, allow_empty=True),
                exact_abs_default=_require_float(row, "exact_abs_default", context),
                exact_rel_default=_require_float(row, "exact_rel_default", context),
                require_reference_exact_green=_require_bool(row, "require_reference_exact_green", context),
                include_association_only_in_core_gate=_require_bool(
                    row,
                    "include_association_only_in_core_gate",
                    context,
                ),
                group_keys=_require_string_tuple(row, "group_keys", context),
            )
        )

    _require_unique([record.profile_key for record in records], "validation profile")
    for record in records:
        unknown = sorted(set(record.group_keys) - group_keys)
        if unknown:
            raise ValueError(
                f"Validation profile '{record.profile_key}' references unknown groups: {', '.join(unknown)}"
            )
    return records


def load_reference_manifest() -> list[ReferenceCaseRecord]:
    payload = _load_yaml_payload(_REFERENCE_CASES_DIR / "manifest.yaml", "manifest.yaml")
    _validate_schema(payload, "reference_case.schema.json")
    entries = _require_sequence(payload, "cases", "manifest.yaml")
    records: list[ReferenceCaseRecord] = []
    for index, entry in enumerate(entries):
        context = f"manifest.yaml cases[{index}]"
        row = _require_mapping(entry, context)
        case_id = _require_string(row, "case_id", context)
        expected_metrics_source = _require_string(row, "expected_metrics_source", context)
        if expected_metrics_source != "checked_in_json":
            raise ValueError(
                f"{context} field 'expected_metrics_source' must be 'checked_in_json'."
            )

        domain = _require_choice(
            row,
            "domain",
            context,
            set(SUPPORTED_VALIDATION_DOMAINS),
        )
        expected_mode = _require_string(row, "expected_mode", context)
        if expected_mode != domain:
            raise ValueError(
                f"{context} has expected_mode mismatch: domain '{domain}' vs expected_mode '{expected_mode}'."
            )

        expected_metrics_path = _REFERENCE_CASES_DIR / "cases" / case_id / "expected_metrics.json"
        records.append(
            ReferenceCaseRecord(
                case_id=case_id,
                source_path=_require_string(row, "source_path", context),
                domain=domain,
                device_or_tps=_require_string(row, "device_or_tps", context),
                expected_mode=expected_mode,
                case_class=_require_choice(row, "case_class", context, _CASE_CLASSES),
                expected_metrics_source=expected_metrics_source,
                expected_metrics_path=expected_metrics_path,
                expected_metrics=_load_expected_metrics(expected_metrics_path, context),
                tolerance_overrides=_require_tolerance_overrides(row, "tolerance_overrides", context),
                checksum=_require_string(row, "checksum", context),
                provenance=_require_provenance(row, "provenance", context),
                notes=_require_string(row, "notes", context, allow_empty=True),
            )
        )

    _require_unique([record.case_id for record in records], "reference case")
    return records


def _load_metric_group_definitions() -> dict[str, _MetricGroupDefinition]:
    payload = _load_payload("metric_groups.yaml")
    entries = _require_sequence(payload, "metric_groups", "metric_groups.yaml")
    definitions: list[_MetricGroupDefinition] = []
    for index, entry in enumerate(entries):
        context = f"metric_groups.yaml metric_groups[{index}]"
        row = _require_mapping(entry, context)
        definitions.append(
            _MetricGroupDefinition(
                group_key=_require_string(row, "group_key", context),
                platform=_require_string(row, "platform", context),
                label=_require_string(row, "label", context),
                description=_require_string(row, "description", context, allow_empty=True),
            )
        )

    _require_unique([definition.group_key for definition in definitions], "metric group")
    return {definition.group_key: definition for definition in definitions}


def _load_payload(file_name: str) -> dict[str, Any]:
    return _load_yaml_payload(_SPECS_DIR / file_name, file_name)


def _load_yaml_payload(path: Path, label: str) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must contain a top-level mapping.")
    return payload


def _validate_schema(payload: dict[str, Any], schema_name: str) -> None:
    validator = Draft202012Validator(_load_schema(schema_name), format_checker=_FORMAT_CHECKER)
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.absolute_path))
    if not errors:
        return
    first_error = errors[0]
    location = ".".join(str(item) for item in first_error.absolute_path) or "<root>"
    raise ValueError(
        f"Schema validation failed for {schema_name} at {location}: {first_error.message}"
    )


@lru_cache(maxsize=None)
def _load_schema(schema_name: str) -> dict[str, Any]:
    path = _SCHEMAS_DIR / schema_name
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Failed to load schema {schema_name}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"Failed to load schema {schema_name}: top-level JSON value must be an object.")
    return payload


def _require_sequence(payload: dict[str, Any], key: str, file_name: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{file_name} must define '{key}' as a list.")
    return value


def _require_mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be a mapping.")
    return value


def _require_string(
    row: dict[str, Any],
    key: str,
    context: str,
    *,
    allow_empty: bool = False,
) -> str:
    value = row.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{context} is missing required string field '{key}'.")
    if not allow_empty and not value.strip():
        raise ValueError(f"{context} field '{key}' cannot be empty.")
    return value


def _require_choice(
    row: dict[str, Any],
    key: str,
    context: str,
    allowed: set[str],
) -> str:
    value = _require_string(row, key, context)
    if value not in allowed:
        raise ValueError(
            f"{context} field '{key}' must be one of: {', '.join(sorted(allowed))}."
        )
    return value


def _require_float(row: dict[str, Any], key: str, context: str) -> float:
    value = row.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{context} is missing required numeric field '{key}'.")
    return float(value)


def _require_float_or_none(row: dict[str, Any], key: str, context: str) -> float | None:
    value = row.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{context} field '{key}' must be numeric or null.")
    return float(value)


def _require_bool(row: dict[str, Any], key: str, context: str) -> bool:
    value = row.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"{context} is missing required boolean field '{key}'.")
    return value


def _optional_bool(row: dict[str, Any], key: str, context: str) -> bool | None:
    value = row.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError(f"{context} field '{key}' must be a boolean.")
    return value


def _optional_string(
    row: dict[str, Any],
    key: str,
    context: str,
    *,
    allow_empty: bool = False,
) -> str | None:
    value = row.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{context} field '{key}' must be a string.")
    if not allow_empty and not value.strip():
        raise ValueError(f"{context} field '{key}' cannot be empty.")
    return value


def _require_string_tuple(row: dict[str, Any], key: str, context: str) -> tuple[str, ...]:
    value = row.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{context} field '{key}' must be a list of strings.")
    items: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise ValueError(
                f"{context} field '{key}' item {index} must be a string."
            )
        items.append(item)
    return tuple(items)


def _require_metric_key(row: dict[str, Any], context: str) -> str:
    metric_key = row.get("metric_key")
    key_alias = row.get("key")
    if metric_key is None:
        raise ValueError(f"{context} is missing required string field 'metric_key'.")
    if metric_key is not None and not isinstance(metric_key, str):
        raise ValueError(f"{context} field 'metric_key' must be a string.")
    if key_alias is not None and not isinstance(key_alias, str):
        raise ValueError(f"{context} field 'key' must be a string.")
    if metric_key and key_alias and metric_key != key_alias:
        raise ValueError(f"{context} field 'metric_key' does not match alias field 'key'.")
    value = metric_key
    if value is None or not value.strip():
        raise ValueError(f"{context} field 'metric_key' cannot be empty.")
    return value


def _require_expected_range(
    row: dict[str, Any],
    key: str,
    context: str,
) -> ExpectedRangeRecord:
    value = row.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{context} field '{key}' must be a mapping.")
    minimum = _optional_float(value, "minimum", f"{context} field '{key}'")
    maximum = _optional_float(value, "maximum", f"{context} field '{key}'")
    if minimum is not None and maximum is not None and minimum > maximum:
        raise ValueError(
            f"{context} field '{key}' has minimum greater than maximum."
        )
    kind = _require_expected_range_kind(value, "kind", f"{context} field '{key}'")
    _validate_expected_range_bounds(
        kind,
        minimum,
        maximum,
        f"{context} field '{key}'",
    )
    return ExpectedRangeRecord(
        kind=kind,
        minimum=minimum,
        maximum=maximum,
    )


def _optional_float(row: dict[str, Any], key: str, context: str) -> float | None:
    value = row.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{context} field '{key}' must be numeric or null.")
    return float(value)


def _require_expected_range_kind(
    row: dict[str, Any],
    key: str,
    context: str,
) -> str:
    value = _require_string(row, key, context)
    if value not in _EXPECTED_RANGE_KINDS:
        raise ValueError(
            f"{context} field '{key}' must be one of: {', '.join(sorted(_EXPECTED_RANGE_KINDS))}."
        )
    return value


def _validate_expected_range_bounds(
    kind: str,
    minimum: float | None,
    maximum: float | None,
    context: str,
) -> None:
    if kind == "unit_interval":
        if minimum != 0.0 or maximum != 1.0:
            raise ValueError(
                f"{context} kind 'unit_interval' requires bounds [0.0, 1.0]."
            )
        return
    if kind == "signed_unit_interval":
        if minimum != -1.0 or maximum != 1.0:
            raise ValueError(
                f"{context} kind 'signed_unit_interval' requires bounds [-1.0, 1.0]."
            )
        return
    if kind == "nonnegative":
        if minimum != 0.0:
            raise ValueError(
                f"{context} kind 'nonnegative' requires a minimum of 0.0."
            )
        if maximum is not None and maximum < 0.0:
            raise ValueError(
                f"{context} kind 'nonnegative' cannot use a negative maximum."
            )


def _require_unique(values: list[object], label: str) -> None:
    seen: set[object] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen:
            duplicates.append(str(value))
            continue
        seen.add(value)
    if duplicates:
        raise ValueError(f"Duplicate {label} entries: {', '.join(duplicates)}")


def _require_tolerance_overrides(
    row: dict[str, Any],
    key: str,
    context: str,
) -> dict[str, ToleranceOverrideRecord]:
    value = row.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{context} field '{key}' must be a mapping.")

    overrides: dict[str, ToleranceOverrideRecord] = {}
    for metric_key, item in value.items():
        if not isinstance(metric_key, str) or not metric_key.strip():
            raise ValueError(f"{context} field '{key}' contains an invalid metric key.")
        item_context = f"{context} field '{key}'[{metric_key}]"
        item_row = _require_mapping(item, item_context)
        overrides[metric_key] = ToleranceOverrideRecord(
            absolute=_optional_float(item_row, "abs", item_context),
            relative=_optional_float(item_row, "rel", item_context),
            skip=_optional_bool(item_row, "skip", item_context) or False,
            reason=_optional_string(item_row, "reason", item_context, allow_empty=True) or "",
        )
    return overrides


def _require_provenance(
    row: dict[str, Any],
    key: str,
    context: str,
) -> ReferenceCaseProvenanceRecord:
    value = row.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{context} field '{key}' must be a mapping.")
    item_context = f"{context} field '{key}'"
    return ReferenceCaseProvenanceRecord(
        source_kind=_require_string(value, "source_kind", item_context),
        version=_optional_string(value, "version", item_context, allow_empty=True) or "",
        notes=_optional_string(value, "notes", item_context, allow_empty=True) or "",
    )


def _load_expected_metrics(path: Path, context: str) -> dict[str, float | int | str | None]:
    if not path.exists():
        raise ValueError(f"{context} is missing expected metrics artifact '{path}'.")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{context} failed to load expected metrics '{path}': {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{context} expected metrics '{path}' must contain a top-level object.")

    metrics: dict[str, float | int | str | None] = {}
    for metric_key, value in payload.items():
        if not isinstance(metric_key, str) or not metric_key.strip():
            raise ValueError(f"{context} expected metrics '{path}' contains an invalid metric key.")
        if isinstance(value, bool) or not isinstance(value, (int, float, str)) and value is not None:
            raise ValueError(
                f"{context} expected metrics '{path}' value for '{metric_key}' must be numeric, string, or null."
            )
        metrics[metric_key] = value
    return metrics
