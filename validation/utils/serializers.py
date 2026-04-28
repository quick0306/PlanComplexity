from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable


def write_json_artifact(path: Path | str, payload: dict[str, Any]) -> Path:
    artifact_path = Path(path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return artifact_path


def write_csv_artifact(
    path: Path | str,
    rows: Iterable[dict[str, Any]],
    *,
    fieldnames: list[str],
) -> Path:
    artifact_path = Path(path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    row_list = list(rows)
    with artifact_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in row_list:
            writer.writerow(row)
    return artifact_path
