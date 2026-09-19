from __future__ import annotations

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

    # Legacy mappings contain values and names only: they have neither an input
    # identity nor an external artifact/version hash. Numerical agreement with
    # these demonstration values is not external validation. The provenance-
    # checked external_benchmarks pipeline owns actual captured comparisons.
    return _skipped_result(
        mapping,
        "Unverified legacy sample: external artifact, input identity and formula provenance are absent.",
    )


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
