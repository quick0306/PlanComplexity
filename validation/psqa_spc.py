from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Iterable

from jsonschema import Draft202012Validator


_SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "psqa_outcome.schema.json"


def load_psqa_records(path: Path | str) -> list[dict[str, object]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        records = [dict(row) for row in csv.DictReader(handle)]
    validate_psqa_records(records)
    return records


def validate_psqa_records(records: Iterable[dict[str, object]]) -> None:
    validator = Draft202012Validator(_load_schema())
    for index, record in enumerate(records):
        errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
        if errors:
            first_error = errors[0]
            location = ".".join(str(item) for item in first_error.path) or "<record>"
            raise ValueError(f"Invalid PSQA record {index} at {location}: {first_error.message}")


def harmonize_metric_values(
    records: Iterable[dict[str, object]],
    *,
    metric_key: str,
    group_by: str | Iterable[str] = ("site_id", "machine_id", "platform"),
) -> list[dict[str, object]]:
    rows = [
        dict(record)
        for record in records
        if str(record.get("metric_key", "")) == metric_key
    ]
    grouped_values: dict[str, list[float]] = {}
    for row in rows:
        group = _stratification_key(row, group_by)
        grouped_values.setdefault(group, []).append(float(row["metric_value"]))

    baselines = {
        group: _mean_sigma(values)
        for group, values in grouped_values.items()
    }
    harmonized = []
    for row in rows:
        group = _stratification_key(row, group_by)
        center, sigma = baselines[group]
        value = float(row["metric_value"])
        z_score = 0.0 if sigma == 0.0 else (value - center) / sigma
        harmonized.append(
            {
                **row,
                "harmonized_metric_key": metric_key,
                "harmonization_group": group,
                "baseline_center": center,
                "baseline_sigma": sigma,
                "z_score": z_score,
            }
        )
    return harmonized


def calculate_spc_limits(values: Iterable[float], *, sigma_width: float = 3.0) -> dict[str, float]:
    numeric_values = [float(value) for value in values]
    center, sigma = _mean_sigma(numeric_values)
    return {
        "center": center,
        "sigma": sigma,
        "lcl": center - sigma_width * sigma,
        "ucl": center + sigma_width * sigma,
        "sigma_width": sigma_width,
    }


def classify_spc_points(values: Iterable[float], limits: dict[str, float]) -> list[dict[str, object]]:
    rows = []
    for index, value in enumerate(float(item) for item in values):
        outside_limits = value < float(limits["lcl"]) or value > float(limits["ucl"])
        rows.append(
            {
                "index": index,
                "value": value,
                "status": "out_of_control" if outside_limits else "in_control",
                "rule": "outside_3_sigma" if outside_limits else "",
            }
        )
    return rows


def summarize_psqa(records: Iterable[dict[str, object]], *, gamma_key: str = "gamma_3_3") -> dict[str, object]:
    values = [
        float(record[gamma_key])
        for record in records
        if record.get(gamma_key) not in (None, "")
    ]
    if not values:
        return {"sample_count": 0, "mean_gamma": None, "min_gamma": None, "pass_rate_95": None}
    return {
        "sample_count": len(values),
        "mean_gamma": sum(values) / len(values),
        "min_gamma": min(values),
        "pass_rate_95": sum(1 for value in values if value >= 95.0) / len(values),
    }


def _stratification_key(row: dict[str, object], group_by: str | Iterable[str]) -> str:
    if isinstance(group_by, str):
        return str(row.get(group_by, ""))
    parts = [
        f"{field}={row.get(field)}"
        for field in group_by
        if row.get(field) not in (None, "")
    ]
    return "|".join(parts) if parts else "all"


def _load_schema() -> dict[str, object]:
    import json

    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def _mean_sigma(values: list[float]) -> tuple[float, float]:
    if not values:
        raise ValueError("At least one value is required.")
    center = sum(values) / len(values)
    if len(values) == 1:
        return center, 0.0
    variance = sum((value - center) ** 2 for value in values) / (len(values) - 1)
    return center, math.sqrt(variance)


__all__ = [
    "calculate_spc_limits",
    "classify_spc_points",
    "harmonize_metric_values",
    "load_psqa_records",
    "summarize_psqa",
    "validate_psqa_records",
]
