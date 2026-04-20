from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ucomx_service import analyze_directory, export_results_to_csv
from ucomx_models import AnalysisMode


warnings.filterwarnings("ignore")


def main() -> None:
    data_dir = Path("data")
    output_dir = Path("run_reports")
    output_dir.mkdir(exist_ok=True)

    results = analyze_directory(str(data_dir), requested_mode=AnalysisMode.AUTO, recursive=True)
    csv_path = output_dir / "real_rtplan_metrics_all.csv"
    export_results_to_csv(results, str(csv_path))

    summary: dict[str, dict[str, int]] = {}
    for result in results:
        tps = Path(result.source_path).parent.name
        bucket = summary.setdefault(tps, {"total": 0, "ready": 0, "unsupported": 0})
        bucket["total"] += 1
        if result.supported:
            bucket["ready"] += 1
        else:
            bucket["unsupported"] += 1

    payload = {
        "total_files": len(results),
        "csv_path": str(csv_path),
        "summary_by_tps": summary,
    }
    (output_dir / "real_rtplan_metrics_all_summary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
