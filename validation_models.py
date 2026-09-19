from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExpectedRangeRecord:
    kind: str
    minimum: float | None
    maximum: float | None


@dataclass(frozen=True)
class MetricSpecRecord:
    platform: str
    mode: str
    group_key: str
    metric_key: str
    label: str
    unit: str
    aggregation_scope: str
    normalization_basis: str
    validation_level: str
    comparison_class: str
    default_tolerance_abs: float | None
    default_tolerance_rel: float | None
    expected_range: ExpectedRangeRecord
    clinical_readiness: str
    known_noncomparability: tuple[str, ...]
    comparable_to: tuple[str, ...]
    assumptions: tuple[str, ...]
    exclusions: tuple[str, ...]


@dataclass(frozen=True)
class MetricGroupRecord:
    group_key: str
    platform: str
    label: str
    description: str
    metric_keys: tuple[str, ...]


@dataclass(frozen=True)
class ValidationProfileRecord:
    profile_key: str
    description: str
    exact_abs_default: float
    exact_rel_default: float
    require_reference_exact_green: bool
    include_association_only_in_core_gate: bool
    group_keys: tuple[str, ...]


@dataclass(frozen=True)
class ComparatorSampleRecord:
    case_id: str
    comparator_value: float | int | str | None
    notes: str


@dataclass(frozen=True)
class ComparatorMappingRecord:
    platform: str
    internal_metric: str
    comparator: str
    comparator_metric: str
    relationship: str
    samples: tuple[ComparatorSampleRecord, ...]
    notes: str


@dataclass(frozen=True)
class ToleranceOverrideRecord:
    absolute: float | None
    relative: float | None
    skip: bool
    reason: str


@dataclass(frozen=True)
class ReferenceCaseProvenanceRecord:
    source_kind: str
    version: str
    notes: str


@dataclass(frozen=True)
class ExpectedMetricsProvenanceRecord:
    schema_version: int
    formula_version: str
    case_id: str
    domain: str
    mode: str
    source_checksum: str
    expected_metrics_checksum: str
    generated_at: str


@dataclass(frozen=True)
class ReferenceCaseRecord:
    case_id: str
    source_path: str
    domain: str
    device_or_tps: str
    expected_mode: str
    case_class: str
    expected_metrics_source: str
    expected_metrics_path: Path
    expected_metrics: dict[str, float | int | str | None]
    tolerance_overrides: dict[str, ToleranceOverrideRecord]
    checksum: str
    provenance: ReferenceCaseProvenanceRecord
    notes: str
    expected_formula_version: str | None = None
    expected_metrics_provenance: ExpectedMetricsProvenanceRecord | None = None
    expected_supported: bool = True


@dataclass(frozen=True)
class ValidationCaseResult:
    source_path: str
    domain: str
    mode: str
    supported: bool
    reason: str
    metadata: dict[str, Any]
    metrics: dict[str, float | int | str | None]
    warnings: tuple[str, ...]


__all__ = [
    "ComparatorMappingRecord",
    "ComparatorSampleRecord",
    "ExpectedRangeRecord",
    "ExpectedMetricsProvenanceRecord",
    "MetricGroupRecord",
    "MetricSpecRecord",
    "ReferenceCaseProvenanceRecord",
    "ReferenceCaseRecord",
    "ToleranceOverrideRecord",
    "ValidationCaseResult",
    "ValidationProfileRecord",
]
