from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Iterable

from jsonschema import Draft202012Validator


_SCHEMA_PATH = Path(__file__).resolve().parent / "schemas" / "clinical_endpoint.schema.json"


def load_endpoint_records(path: Path | str) -> list[dict[str, object]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        records = [dict(row) for row in csv.DictReader(handle)]
    validate_endpoint_records(records)
    return records


def validate_endpoint_records(records: Iterable[dict[str, object]]) -> None:
    validator = Draft202012Validator(_load_schema())
    for index, record in enumerate(records):
        errors = sorted(validator.iter_errors(record), key=lambda error: list(error.path))
        if errors:
            first_error = errors[0]
            location = ".".join(str(item) for item in first_error.path) or "<record>"
            raise ValueError(f"Invalid clinical endpoint record {index} at {location}: {first_error.message}")


def associate_binary_endpoint(
    records: Iterable[dict[str, object]],
    *,
    metric_key: str,
    endpoint_key: str,
) -> dict[str, object]:
    paired = [
        (float(record[metric_key]), int(float(record[endpoint_key])))
        for record in records
        if record.get(metric_key) not in (None, "") and record.get(endpoint_key) not in (None, "")
    ]
    if not paired:
        raise ValueError("At least one metric/endpoint pair is required.")

    event_values = [metric for metric, endpoint in paired if endpoint == 1]
    non_event_values = [metric for metric, endpoint in paired if endpoint == 0]
    all_metrics = [metric for metric, _endpoint in paired]
    all_endpoints = [endpoint for _metric, endpoint in paired]
    return {
        "metric_key": metric_key,
        "endpoint_key": endpoint_key,
        "sample_count": len(paired),
        "event_count": len(event_values),
        "non_event_count": len(non_event_values),
        "event_mean": _mean_or_none(event_values),
        "non_event_mean": _mean_or_none(non_event_values),
        "mean_difference": _mean_difference(event_values, non_event_values),
        "point_biserial_r": _pearson(all_metrics, all_endpoints),
    }


def _mean_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _mean_difference(event_values: list[float], non_event_values: list[float]) -> float | None:
    event_mean = _mean_or_none(event_values)
    non_event_mean = _mean_or_none(non_event_values)
    if event_mean is None or non_event_mean is None:
        return None
    return event_mean - non_event_mean


def _pearson(xs: list[float], ys: list[int]) -> float | None:
    if len(xs) < 2:
        return None
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_denom = math.sqrt(sum((x - x_mean) ** 2 for x in xs))
    y_denom = math.sqrt(sum((y - y_mean) ** 2 for y in ys))
    if x_denom == 0.0 or y_denom == 0.0:
        return None
    return numerator / (x_denom * y_denom)


def _load_schema() -> dict[str, object]:
    import json

    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


__all__ = ["associate_binary_endpoint", "load_endpoint_records", "validate_endpoint_records"]
