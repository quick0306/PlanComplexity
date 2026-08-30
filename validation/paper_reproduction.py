from __future__ import annotations

from validation.utils.loaders import load_metric_specs


_PAPER_GROUPS = {
    "vmat_imrt_motion_bins": "Park 2015",
    "vmat_imrt_sport": "Li and Xing 2013",
    "vmat_imrt_halcyon_ethos_tamura_2020": "Tamura/Park 2020",
    "vmat_imrt_halcyon_ethos_quintero_2021": "Quintero/Esposito 2021",
    "cyberknife_mlc_mlc_based_subset": "Masi 2021",
    "aurora_v2_paper_style_physics": "Aurora research specification",
}


def build_paper_reproduction_table() -> dict[str, object]:
    rows = []
    for spec in load_metric_specs():
        paper = _PAPER_GROUPS.get(spec.group_key)
        if paper is None:
            continue
        rows.append(
            {
                "paper": paper,
                "platform": spec.platform,
                "metric_key": spec.metric_key,
                "group_key": spec.group_key,
                "validation_level": spec.validation_level,
                "comparison_class": spec.comparison_class,
                "status": _status_for_spec(spec.validation_level, spec.comparison_class),
            }
        )
    return {
        "summary": {
            "paper_metric_rows": len(rows),
            "papers_total": len({row["paper"] for row in rows}),
            "reference_exact_rows": sum(1 for row in rows if row["validation_level"] == "Reference-case exact"),
        },
        "rows": rows,
    }


def _status_for_spec(validation_level: str, comparison_class: str) -> str:
    if validation_level == "Reference-case exact" and comparison_class == "exact-equivalent":
        return "reference-gated"
    if comparison_class == "derived-equivalent":
        return "derived-comparison"
    if comparison_class == "not-comparable":
        return "formula-only"
    return "tracked"


__all__ = ["build_paper_reproduction_table"]
