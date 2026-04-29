from __future__ import annotations

from validation_models import MetricSpecRecord, ReferenceCaseRecord, ValidationProfileRecord


def compare_exact(
    expected: float | int | str | None,
    observed: float | int | str | None,
    abs_tol: float,
    rel_tol: float,
) -> dict[str, float | int | str | bool | None]:
    if _is_numeric(expected) and _is_numeric(observed):
        expected_value = float(expected)
        observed_value = float(observed)
        abs_diff = abs(observed_value - expected_value)
        if expected_value == 0.0:
            rel_diff = 0.0 if abs_diff == 0.0 else None
            rel_pass = abs_diff == 0.0
        else:
            rel_diff = abs_diff / abs(expected_value)
            rel_pass = rel_diff <= rel_tol
        return {
            "pass": abs_diff <= abs_tol or rel_pass,
            "expected": expected_value,
            "observed": observed_value,
            "abs_diff": abs_diff,
            "rel_diff": rel_diff,
        }

    return {
        "pass": expected == observed,
        "expected": expected,
        "observed": observed,
        "abs_diff": None,
        "rel_diff": None,
    }


def resolve_metric_tolerances(
    case: ReferenceCaseRecord,
    metric_spec: MetricSpecRecord,
    profile: ValidationProfileRecord,
) -> dict[str, float | bool | str]:
    override = case.tolerance_overrides.get(metric_spec.metric_key)
    abs_tol = profile.exact_abs_default
    rel_tol = profile.exact_rel_default
    if metric_spec.default_tolerance_abs is not None:
        abs_tol = metric_spec.default_tolerance_abs
    if metric_spec.default_tolerance_rel is not None:
        rel_tol = metric_spec.default_tolerance_rel
    if override is not None and override.absolute is not None:
        abs_tol = override.absolute
    if override is not None and override.relative is not None:
        rel_tol = override.relative
    return {
        "abs_tol": abs_tol,
        "rel_tol": rel_tol,
        "skip": override.skip if override is not None else False,
        "reason": override.reason if override is not None else "",
    }


def _is_numeric(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float))
