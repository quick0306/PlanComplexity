from __future__ import annotations

import subprocess
from pathlib import Path

from validation.utils.loaders import load_metric_specs, load_reference_manifest


def run_clinical_readiness_gate(repo_root: Path | str | None = None) -> dict[str, object]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[1]
    checks = [
        _check_metric_specs_load(),
        _check_reference_manifest_load(),
        _check_ci_workflow_exists(root),
        _check_no_tracked_csv(root),
        _check_csv_history_clean(root),
        _check_clinical_sop_exists(root),
        _check_deployment_rollback_docs(root),
        _check_audit_log_schema_exists(root),
        _check_research_only_claims(),
    ]
    blocking = [check for check in checks if check["status"] == "fail" and check["blocking"]]
    return {
        "summary": {
            "checks_total": len(checks),
            "blocking_failures": len(blocking),
            "clinical_ready": False,
            "open_source_ready": len(blocking) == 0,
        },
        "checks": checks,
    }


def _check_metric_specs_load() -> dict[str, object]:
    specs = load_metric_specs()
    return _check(
        "metric_specs_load",
        "pass" if specs else "fail",
        f"Loaded {len(specs)} metric specs.",
        blocking=True,
    )


def _check_reference_manifest_load() -> dict[str, object]:
    cases = load_reference_manifest()
    return _check(
        "reference_manifest_load",
        "pass" if cases else "fail",
        f"Loaded {len(cases)} reference cases.",
        blocking=True,
    )


def _check_ci_workflow_exists(root: Path) -> dict[str, object]:
    workflow = root / ".github" / "workflows" / "validation.yml"
    return _check(
        "ci_validation_workflow",
        "pass" if workflow.exists() else "fail",
        "Validation workflow exists." if workflow.exists() else "Missing validation workflow.",
        blocking=True,
    )


def _check_no_tracked_csv(root: Path) -> dict[str, object]:
    result = _git(root, ["ls-files", "*.csv"])
    tracked = [line for line in result.stdout.splitlines() if line.strip()]
    return _check(
        "no_tracked_csv_reports",
        "pass" if not tracked else "fail",
        "No tracked CSV files." if not tracked else f"Tracked CSV files remain: {', '.join(tracked[:5])}",
        blocking=True,
    )


def _check_csv_history_clean(root: Path) -> dict[str, object]:
    result = _git(root, ["log", "--oneline", "--all", "--", "*.csv"])
    historical = [line for line in result.stdout.splitlines() if line.strip()]
    return _check(
        "csv_history_phi_review",
        "pass" if not historical else "fail",
        "No CSV history found."
        if not historical
        else "CSV history exists; rewrite history or publish from a clean repository before open-source release.",
        blocking=True,
    )


def _check_research_only_claims() -> dict[str, object]:
    readiness_values = {spec.clinical_readiness for spec in load_metric_specs()}
    return _check(
        "research_only_clinical_claims",
        "pass" if readiness_values == {"research"} else "fail",
        f"Clinical readiness values: {', '.join(sorted(readiness_values))}.",
        blocking=False,
    )


def _check_clinical_sop_exists(root: Path) -> dict[str, object]:
    candidates = [
        root / "docs" / "clinical_implementation_sop.md",
        root / "docs" / "CLINICAL_IMPLEMENTATION_SOP.md",
    ]
    exists = any(path.exists() for path in candidates)
    return _check(
        "clinical_sop_documented",
        "pass" if exists else "fail",
        "Clinical implementation SOP exists."
        if exists
        else "Clinical implementation SOP is not documented; keep clinical_ready false.",
        blocking=False,
    )


def _check_deployment_rollback_docs(root: Path) -> dict[str, object]:
    candidates = [
        root / "docs" / "deployment_rollback.md",
        root / "docs" / "DEPLOYMENT_ROLLBACK.md",
    ]
    exists = any(path.exists() for path in candidates)
    return _check(
        "deployment_rollback_documented",
        "pass" if exists else "fail",
        "Deployment and rollback procedure exists."
        if exists
        else "Deployment and rollback procedure is not documented.",
        blocking=False,
    )


def _check_audit_log_schema_exists(root: Path) -> dict[str, object]:
    schema = root / "validation" / "schemas" / "audit_log.schema.json"
    return _check(
        "audit_log_schema_documented",
        "pass" if schema.exists() else "fail",
        "Audit log schema exists." if schema.exists() else "Audit log schema is not documented.",
        blocking=False,
    )


def _check(check_id: str, status: str, message: str, *, blocking: bool) -> dict[str, object]:
    return {
        "check_id": check_id,
        "status": status,
        "blocking": blocking,
        "message": message,
    }


def _git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


__all__ = ["run_clinical_readiness_gate"]
