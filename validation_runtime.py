from __future__ import annotations

from dataclasses import asdict

from aurora_svmat_lab.models import AuroraAnalysisResult
from metric_definition_catalog import metric_catalog_keys_for_platform
from ucomx_models import AnalysisMode, PlanAnalysisResult
from validation_models import ValidationCaseResult


def analyze_validation_case(source_path: str, domain: str) -> ValidationCaseResult:
    normalized_domain = domain.strip().upper()
    if normalized_domain == "AURORA":
        from aurora_svmat_lab.service import analyze_plan_file as analyze_aurora_plan_file

        result = analyze_aurora_plan_file(source_path)
        return _normalize_aurora_result(result)

    requested_mode = _analysis_mode_for_domain(normalized_domain)

    from ucomx_service import analyze_plan_file

    result = analyze_plan_file(source_path, requested_mode=requested_mode)
    return _normalize_core_result(result, domain=normalized_domain)


def _analysis_mode_for_domain(domain: str) -> AnalysisMode:
    try:
        return {
            "VMAT_IMRT": AnalysisMode.VMAT_IMRT,
            "TOMO": AnalysisMode.TOMO,
            "CYBERKNIFE_MLC": AnalysisMode.CYBERKNIFE_MLC,
        }[domain]
    except KeyError as exc:
        raise ValueError(f"Unsupported validation domain '{domain}'.") from exc


def _normalize_core_result(result: PlanAnalysisResult, *, domain: str) -> ValidationCaseResult:
    allowed_metric_keys = metric_catalog_keys_for_platform(domain)
    metrics = {
        key: value
        for key, value in result.flattened_metrics.items()
        if key in allowed_metric_keys
    }
    return ValidationCaseResult(
        source_path=result.source_path,
        domain=domain,
        mode=result.mode.value,
        supported=result.supported,
        reason=result.reason_label,
        metadata=dict(result.metadata),
        metrics=metrics,
        warnings=tuple(result.warnings),
    )


def _normalize_aurora_result(result: AuroraAnalysisResult) -> ValidationCaseResult:
    allowed_metric_keys = metric_catalog_keys_for_platform("AURORA")
    listed_metrics = {
        metric.metric_name: metric.value
        for metric in result.metrics
        if metric.metric_name in allowed_metric_keys
    }
    listed_metrics.update(
        {
            key: value
            for key, value in result.plan_metrics.items()
            if key in allowed_metric_keys
        }
    )
    return ValidationCaseResult(
        source_path=result.source_path,
        domain="AURORA",
        mode="AURORA",
        supported=result.supported,
        reason=result.reason,
        metadata=asdict(result.metadata),
        metrics=listed_metrics,
        warnings=tuple(result.warnings),
    )


__all__ = [
    "ValidationCaseResult",
    "analyze_validation_case",
]

