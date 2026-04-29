from __future__ import annotations

import json
import sys
import traceback
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ucomx_service import AnalysisMode, analyze_plan_file


warnings.filterwarnings("ignore")


def sample_per_tps(base: Path) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for folder in sorted((p for p in base.iterdir() if p.is_dir()), key=lambda p: p.name):
        files = sorted(folder.glob("*.dcm"))
        if not files:
            results.append({"tps": folder.name, "status": "no_dcm"})
            continue

        sample = files[0]
        try:
            report = analyze_plan_file(str(sample), requested_mode=AnalysisMode.AUTO)
            results.append(
                {
                    "tps": folder.name,
                    "status": "ok",
                    "file": sample.name,
                    "mode": report.mode.value,
                    "metric_count": len(report.metrics),
                }
            )
        except Exception as exc:  # pragma: no cover - diagnostic helper
            results.append(
                {
                    "tps": folder.name,
                    "status": "error",
                    "file": sample.name,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                }
            )

    return results


def focused(paths: list[str]) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for path in paths:
        try:
            report = analyze_plan_file(path, requested_mode=AnalysisMode.AUTO)
            results.append(
                {
                    "path": path,
                    "status": "ok",
                    "mode": report.mode.value,
                    "metric_count": len(report.metrics),
                }
            )
        except Exception as exc:  # pragma: no cover - diagnostic helper
            results.append(
                {
                    "path": path,
                    "status": "error",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                }
            )
    return results


def all_files(base: Path, requested: set[str] | None = None) -> dict[str, object]:
    details: list[dict[str, object]] = []
    per_tps: dict[str, dict[str, object]] = {}

    for folder in sorted((p for p in base.iterdir() if p.is_dir()), key=lambda p: p.name):
        if requested is not None and folder.name.lower() not in requested:
            continue
        stats = {"total": 0, "ok": 0, "error": 0, "modes": {}}
        for path in sorted(folder.glob("*.dcm")):
            stats["total"] += 1
            try:
                report = analyze_plan_file(str(path), requested_mode=AnalysisMode.AUTO)
                stats["ok"] += 1
                stats["modes"][report.mode.value] = stats["modes"].get(report.mode.value, 0) + 1
                details.append(
                    {
                        "tps": folder.name,
                        "file": path.name,
                        "status": "ok",
                        "mode": report.mode.value,
                        "metric_count": len(report.metrics),
                        "warning_count": len(report.warnings),
                    }
                )
            except Exception as exc:  # pragma: no cover - diagnostic helper
                stats["error"] += 1
                details.append(
                    {
                        "tps": folder.name,
                        "file": path.name,
                        "status": "error",
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "traceback": traceback.format_exc(),
                    }
                )
        per_tps[folder.name] = stats

    return {"summary": per_tps, "details": details}


if __name__ == "__main__":
    base = Path("data")
    if len(sys.argv) > 1:
        requested = {arg.lower() for arg in sys.argv[1:]}
        payload = {"all_files": all_files(base, requested=requested)}
    else:
        payload = {
            "samples": sample_per_tps(base),
            "focused": focused(
                [
                    r"data\PRECISION\ANON_PRECISION_RP01_Prostata.dcm",
                    r"data\RAYSTATION\ANON_RAYSTATION_RP01_Prostata.dcm",
                    r"data\Tomo\RP.1.2.826.0.1.3680043.2.200.1006842071.58789.987.79527.2425.dcm",
                ]
            ),
            "all_files": all_files(base),
        }
    report_dir = Path("run_reports")
    report_dir.mkdir(exist_ok=True)
    filename = "real_rtplan_validation.json" if len(sys.argv) == 1 else f"real_rtplan_validation_{'_'.join(sys.argv[1:])}.json"
    (report_dir / filename).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
