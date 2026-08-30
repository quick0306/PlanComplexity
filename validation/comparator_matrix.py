from __future__ import annotations

from collections import Counter, defaultdict

from validation.utils.loaders import load_comparator_mappings, load_metric_specs


def build_comparator_matrix() -> dict[str, object]:
    specs = load_metric_specs()
    mappings = load_comparator_mappings()
    mappings_by_key = {
        (mapping.platform, mapping.internal_metric): mapping
        for mapping in mappings
    }

    metric_rows = []
    for spec in specs:
        mapping = mappings_by_key.get((spec.platform, spec.metric_key))
        metric_rows.append(
            {
                "platform": spec.platform,
                "metric_key": spec.metric_key,
                "group_key": spec.group_key,
                "validation_level": spec.validation_level,
                "comparison_class": spec.comparison_class,
                "coverage_status": "mapped" if mapping else "unmapped",
                "comparator": mapping.comparator if mapping else "",
                "comparator_metric": mapping.comparator_metric if mapping else "",
                "relationship": mapping.relationship if mapping else "",
                "sample_count": len(mapping.samples) if mapping else 0,
            }
        )

    platform_rows = []
    rows_by_platform: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in metric_rows:
        rows_by_platform[str(row["platform"])].append(row)

    for platform, rows in sorted(rows_by_platform.items()):
        status_counts = Counter(str(row["coverage_status"]) for row in rows)
        relationship_counts = Counter(str(row["relationship"]) for row in rows if row["relationship"])
        platform_rows.append(
            {
                "platform": platform,
                "metric_count": len(rows),
                "mapped_metrics": status_counts["mapped"],
                "unmapped_metrics": status_counts["unmapped"],
                "exact_equivalent_mappings": relationship_counts["exact-equivalent"],
                "derived_equivalent_mappings": relationship_counts["derived-equivalent"],
                "association_only_mappings": relationship_counts["association-only"],
                "not_comparable_mappings": relationship_counts["not-comparable"],
                "sample_count": sum(int(row["sample_count"]) for row in rows),
            }
        )

    return {
        "summary": {
            "metrics_total": len(metric_rows),
            "mapped_metrics": sum(1 for row in metric_rows if row["coverage_status"] == "mapped"),
            "platforms_total": len(platform_rows),
        },
        "platforms": platform_rows,
        "metrics": metric_rows,
    }


__all__ = ["build_comparator_matrix"]
