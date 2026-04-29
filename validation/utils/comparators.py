from __future__ import annotations

from validation.utils.statistics import summarize_agreement
from validation_models import ComparatorMappingRecord


def summarize_comparator_mapping(
    mapping: ComparatorMappingRecord,
    reference_metric_rows: list[dict[str, object]],
) -> dict[str, object]:
    if mapping.relationship in {"not-comparable", "association-only"}:
        return _skipped_result(
            mapping,
            "Not eligible for numeric agreement statistics in this comparison layer.",
        )

    observed_by_case = {
        str(row["case_id"]): row.get("observed")
        for row in reference_metric_rows
        if row.get("metric_key") == mapping.internal_metric
    }
    expected_values: list[float] = []
    observed_values: list[float] = []
    for sample in mapping.samples:
        observed = observed_by_case.get(sample.case_id)
        if _is_numeric(sample.comparator_value) and _is_numeric(observed):
            expected_values.append(float(sample.comparator_value))
            observed_values.append(float(observed))

    if not expected_values:
        return _skipped_result(mapping, "No numeric paired samples were available.")

    statistics = summarize_agreement(expected_values, observed_values)
    return {
        "platform": mapping.platform,
        "internal_metric": mapping.internal_metric,
        "comparator": mapping.comparator,
        "comparator_metric": mapping.comparator_metric,
        "relationship": mapping.relationship,
        "status": "compared",
        "sample_count": statistics["n"],
        "mae": statistics["mae"],
        "bias": statistics["bias"],
        "rmse": statistics["rmse"],
        "notes": mapping.notes,
    }


def _skipped_result(mapping: ComparatorMappingRecord, reason: str) -> dict[str, object]:
    return {
        "platform": mapping.platform,
        "internal_metric": mapping.internal_metric,
        "comparator": mapping.comparator,
        "comparator_metric": mapping.comparator_metric,
        "relationship": mapping.relationship,
        "status": "skipped",
        "sample_count": 0,
        "mae": None,
        "bias": None,
        "rmse": None,
        "notes": reason if not mapping.notes else f"{reason} {mapping.notes}",
    }


def _is_numeric(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float))
