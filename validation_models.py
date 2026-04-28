from __future__ import annotations

from dataclasses import dataclass


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


__all__ = [
    "ExpectedRangeRecord",
    "MetricGroupRecord",
    "MetricSpecRecord",
    "ValidationProfileRecord",
]
