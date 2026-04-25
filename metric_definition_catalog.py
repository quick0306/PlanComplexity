from __future__ import annotations

import csv
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

from aurora_svmat_lab.metrics import LEGACY_METRIC_ORDER, V2_METRIC_ORDER, V3_METRIC_ORDER
from aurora_svmat_lab.notes import get_metric_notes as get_aurora_metric_notes
from metric_registry import (
    CYBERKNIFE_METRIC_SPECS,
    SPECIAL_FLATTENED_DESCRIPTIONS,
    SPECIAL_FLATTENED_LABELS,
    TOMO_METRIC_SPECS,
    VMAT_DUAL_MLC_KEYS,
    VMAT_METRIC_SPECS,
)


@dataclass(frozen=True)
class MetricDefinitionRecord:
    platform: str
    group: str
    metric_key: str
    display_name: str
    symbol_or_short_name: str
    mathematical_definition: str
    physical_meaning: str
    unit: str
    inputs_required: str
    implementation_status: str
    notes: str = ""


@dataclass(frozen=True)
class MetricGroupCatalogRecord:
    platform: str
    group_label: str
    group_key: str


def build_metric_definition_catalog() -> list[MetricDefinitionRecord]:
    records: list[MetricDefinitionRecord] = []
    records.extend(_build_vmat_metric_records())
    records.extend(_build_tomo_metric_records())
    records.extend(_build_cyberknife_metric_records())
    records.extend(_build_aurora_metric_records())
    return records


def metric_catalog_keys() -> set[tuple[str, str]]:
    return {(record.platform, record.metric_key) for record in build_metric_definition_catalog()}


def build_metric_group_catalog() -> list[MetricGroupCatalogRecord]:
    records: list[MetricGroupCatalogRecord] = []
    seen: set[tuple[str, str]] = set()
    for record in build_metric_definition_catalog():
        group_identity = (record.platform, record.group)
        if group_identity in seen:
            continue
        seen.add(group_identity)
        records.append(
            MetricGroupCatalogRecord(
                platform=record.platform,
                group_label=record.group,
                group_key=metric_group_key(record.platform, record.group),
            )
        )
    return records


def metric_group_key(platform: str, group_label: str) -> str:
    normalized_platform = platform.strip().lower()
    normalized_group = _slugify_group_label(group_label)
    return f"{normalized_platform}_{normalized_group}"


def export_metric_definitions(*, csv_path: str | Path, markdown_path: str | Path) -> list[MetricDefinitionRecord]:
    records = build_metric_definition_catalog()
    _write_csv(records, Path(csv_path))
    _write_markdown(records, Path(markdown_path))
    _write_platform_appendices(records, Path(markdown_path).parent)
    return records


def _build_vmat_metric_records() -> list[MetricDefinitionRecord]:
    records: list[MetricDefinitionRecord] = []
    for spec in VMAT_METRIC_SPECS:
        records.append(
            MetricDefinitionRecord(
                platform="VMAT_IMRT",
                group=_vmat_group(spec.key),
                metric_key=spec.key,
                display_name=spec.gui_label or spec.label,
                symbol_or_short_name=spec.label,
                mathematical_definition=_vmat_formula(spec.key),
                physical_meaning=spec.description or f"{spec.label} as implemented by the current VMAT/IMRT workflow.",
                unit=_vmat_unit(spec.key),
                inputs_required=_vmat_inputs(spec.key),
                implementation_status="implemented",
                notes=_notes_for_metric(spec.key, dual_mlc=spec.key in VMAT_DUAL_MLC_KEYS),
            )
        )
        records.extend(_build_vmat_flattened_records(spec.key, spec.label, spec.description))
    return records


def _build_vmat_flattened_records(metric_key: str, label: str, description: str) -> list[MetricDefinitionRecord]:
    records: list[MetricDefinitionRecord] = []
    if metric_key.startswith("mi_"):
        threshold = label.replace("MI(", "").replace(")", "")
        for component_key, component_label, component_formula in (
            (f"{metric_key}_mis", f"{label} Speed", f"MIs({threshold}) = mean_beams[ mean_CP min(v / sigma_v, {threshold}) ]"),
            (f"{metric_key}_mia", f"{label} Acceleration", f"MIa({threshold}) = mean_beams[ mean_CP min(max(v / sigma_v, a / (alpha * sigma_a)), {threshold}) ]"),
            (f"{metric_key}_mit", f"{label} Total", f"MIt({threshold}) = weighted mean over control points of min(max(v / sigma_v, a / (alpha * sigma_a)), {threshold})"),
        ):
            records.append(
                MetricDefinitionRecord(
                    platform="VMAT_IMRT",
                    group="MI components",
                    metric_key=component_key,
                    display_name=component_label,
                    symbol_or_short_name=component_label,
                    mathematical_definition=component_formula,
                    physical_meaning=SPECIAL_FLATTENED_DESCRIPTIONS.get(component_key, description),
                    unit="dimensionless",
                    inputs_required="MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights",
                    implementation_status="implemented_flattened",
                    notes="Flattened export component of the Park 2014 modulation-index tuple.",
                )
            )
        if metric_key in VMAT_DUAL_MLC_KEYS:
            for mlc_layer in ("mlcx1", "mlcx2"):
                for component_key, component_label in (
                    (f"{metric_key}_{mlc_layer}_mis", "Speed"),
                    (f"{metric_key}_{mlc_layer}_mia", "Acceleration"),
                    (f"{metric_key}_{mlc_layer}_mit", "Total"),
                ):
                    records.append(
                        MetricDefinitionRecord(
                            platform="VMAT_IMRT",
                            group="MI components",
                            metric_key=component_key,
                            display_name=SPECIAL_FLATTENED_LABELS.get(component_key, component_key),
                            symbol_or_short_name=f"{label} {mlc_layer.upper()} {component_label}",
                            mathematical_definition=f"Same {component_label.lower()}-component MI formula as {label}, but restricted to {mlc_layer.upper()} leaf positions.",
                            physical_meaning=SPECIAL_FLATTENED_DESCRIPTIONS.get(component_key, description),
                            unit="dimensionless",
                            inputs_required="Per-layer MLC speed and acceleration traces",
                            implementation_status="implemented_flattened",
                            notes=f"Layer-specific flattened export for {mlc_layer.upper()}.",
                        )
                    )
        return records

    if metric_key == "mlc_speed_acc":
        for bucket_key, bucket_text in (
            ("speed_0_4", "0-4 mm/s"),
            ("speed_4_8", "4-8 mm/s"),
            ("speed_8_12", "8-12 mm/s"),
            ("speed_12_16", "12-16 mm/s"),
            ("speed_16_20", "16-20 mm/s"),
        ):
            records.append(
                MetricDefinitionRecord(
                    platform="VMAT_IMRT",
                    group="Motion bins",
                    metric_key=bucket_key,
                    display_name=SPECIAL_FLATTENED_LABELS[bucket_key],
                    symbol_or_short_name=SPECIAL_FLATTENED_LABELS[bucket_key],
                    mathematical_definition=f"mean_leaf [ proportion(intervals with speed in {bucket_text}) ]",
                    physical_meaning=SPECIAL_FLATTENED_DESCRIPTIONS.get(bucket_key, description),
                    unit="proportion",
                    inputs_required="Per-leaf MLC speed over valid control-point intervals",
                    implementation_status="implemented_flattened",
                    notes="Park 2015 speed-bin proportion, averaged over leaves.",
                )
            )
        for bucket_key, bucket_text in (
            ("acc_0_40", "0-40 mm/s^2"),
            ("acc_40_80", "40-80 mm/s^2"),
            ("acc_80_120", "80-120 mm/s^2"),
            ("acc_120_160", "120-160 mm/s^2"),
            ("acc_160_200", "160-200 mm/s^2"),
        ):
            records.append(
                MetricDefinitionRecord(
                    platform="VMAT_IMRT",
                    group="Motion bins",
                    metric_key=bucket_key,
                    display_name=SPECIAL_FLATTENED_LABELS[bucket_key],
                    symbol_or_short_name=SPECIAL_FLATTENED_LABELS[bucket_key],
                    mathematical_definition=f"mean_leaf [ proportion(intervals with acceleration in {bucket_text}) ]",
                    physical_meaning=SPECIAL_FLATTENED_DESCRIPTIONS.get(bucket_key, description),
                    unit="proportion",
                    inputs_required="Per-leaf MLC acceleration over valid control-point intervals",
                    implementation_status="implemented_flattened",
                    notes="Park 2015 acceleration-bin proportion, averaged over leaves.",
                )
            )
        for summary_key, summary_formula, summary_unit in (
            ("speed_average", "mean_leaf(mean_interval(speed))", "mm/s"),
            ("acc_average", "mean_leaf(mean_interval(acceleration))", "mm/s^2"),
            ("speed_std", "mean_leaf(std_interval(speed))", "mm/s"),
            ("acc_std", "mean_leaf(std_interval(acceleration))", "mm/s^2"),
        ):
            records.append(
                MetricDefinitionRecord(
                    platform="VMAT_IMRT",
                    group="Motion bins",
                    metric_key=summary_key,
                    display_name=SPECIAL_FLATTENED_LABELS[summary_key],
                    symbol_or_short_name=SPECIAL_FLATTENED_LABELS[summary_key],
                    mathematical_definition=summary_formula,
                    physical_meaning=SPECIAL_FLATTENED_DESCRIPTIONS.get(summary_key, description),
                    unit=summary_unit,
                    inputs_required="Per-leaf motion time series",
                    implementation_status="implemented_flattened",
                    notes="Park 2015 summary statistic flattened for export.",
                )
            )
        for layer in ("mlcx1", "mlcx2"):
            layer_label = layer.upper()
            for suffix, formula, unit in (
                ("speed_0_4", "mean_leaf [ proportion(intervals with speed in 0-4 mm/s) ]", "proportion"),
                ("speed_4_8", "mean_leaf [ proportion(intervals with speed in 4-8 mm/s) ]", "proportion"),
                ("speed_8_12", "mean_leaf [ proportion(intervals with speed in 8-12 mm/s) ]", "proportion"),
                ("speed_12_16", "mean_leaf [ proportion(intervals with speed in 12-16 mm/s) ]", "proportion"),
                ("speed_16_20", "mean_leaf [ proportion(intervals with speed in 16-20 mm/s) ]", "proportion"),
                ("acc_0_40", "mean_leaf [ proportion(intervals with acceleration in 0-40 mm/s^2) ]", "proportion"),
                ("acc_40_80", "mean_leaf [ proportion(intervals with acceleration in 40-80 mm/s^2) ]", "proportion"),
                ("acc_80_120", "mean_leaf [ proportion(intervals with acceleration in 80-120 mm/s^2) ]", "proportion"),
                ("acc_120_160", "mean_leaf [ proportion(intervals with acceleration in 120-160 mm/s^2) ]", "proportion"),
                ("acc_160_200", "mean_leaf [ proportion(intervals with acceleration in 160-200 mm/s^2) ]", "proportion"),
                ("speed_average", "mean_leaf(mean_interval(speed))", "mm/s"),
                ("acc_average", "mean_leaf(mean_interval(acceleration))", "mm/s^2"),
                ("speed_std", "mean_leaf(std_interval(speed))", "mm/s"),
                ("acc_std", "mean_leaf(std_interval(acceleration))", "mm/s^2"),
            ):
                metric_name = f"{layer}_{suffix}"
                if metric_name not in SPECIAL_FLATTENED_LABELS:
                    continue
                records.append(
                    MetricDefinitionRecord(
                        platform="VMAT_IMRT",
                        group="Motion bins",
                        metric_key=metric_name,
                        display_name=SPECIAL_FLATTENED_LABELS[metric_name],
                        symbol_or_short_name=SPECIAL_FLATTENED_LABELS[metric_name],
                        mathematical_definition=f"{formula}, restricted to {layer_label} leaf positions.",
                        physical_meaning=SPECIAL_FLATTENED_DESCRIPTIONS.get(metric_name, f"{layer_label}-only Park 2015 derived motion statistic."),
                        unit=unit,
                        inputs_required=f"{layer_label} motion traces only",
                        implementation_status="implemented_flattened",
                        notes=f"Layer-specific Park 2015 flattened export for {layer_label}.",
                    )
                )
        return records

    if metric_key in VMAT_DUAL_MLC_KEYS:
        for layer in ("mlcx1", "mlcx2"):
            key = f"{metric_key}_{layer}"
            records.append(
                MetricDefinitionRecord(
                    platform="VMAT_IMRT",
                    group=_vmat_group(metric_key),
                    metric_key=key,
                    display_name=SPECIAL_FLATTENED_LABELS.get(key, key),
                    symbol_or_short_name=SPECIAL_FLATTENED_LABELS.get(key, key),
                    mathematical_definition=f"Same formula as {label}, but computed using {layer.upper()} apertures only.",
                    physical_meaning=SPECIAL_FLATTENED_DESCRIPTIONS.get(key, description),
                    unit=_vmat_unit(metric_key),
                    inputs_required=f"{layer.upper()} leaf positions, control-point weights, and beam geometry",
                    implementation_status="implemented_flattened",
                    notes=f"Layer-specific flattened export for {label}.",
                )
            )
    return records


def _build_tomo_metric_records() -> list[MetricDefinitionRecord]:
    records: list[MetricDefinitionRecord] = []
    for spec in TOMO_METRIC_SPECS:
        records.append(
            MetricDefinitionRecord(
                platform="TOMO",
                group=_tomo_group(spec.key),
                metric_key=spec.key,
                display_name=spec.gui_label or spec.label,
                symbol_or_short_name=spec.label,
                mathematical_definition=_tomo_formula(spec.key),
                physical_meaning=spec.description,
                unit=_tomo_unit(spec.key),
                inputs_required=_tomo_inputs(spec.key),
                implementation_status="implemented",
                notes="Mathematical definition summarizes the current sinogram-based implementation.",
            )
        )
    return records


def _build_cyberknife_metric_records() -> list[MetricDefinitionRecord]:
    records: list[MetricDefinitionRecord] = []
    for spec in CYBERKNIFE_METRIC_SPECS:
        records.append(
            MetricDefinitionRecord(
                platform="CYBERKNIFE_MLC",
                group="MLC-based subset",
                metric_key=spec.key,
                display_name=spec.gui_label or spec.label,
                symbol_or_short_name=spec.label,
                mathematical_definition=_cyberknife_formula(spec.key),
                physical_meaning=spec.description,
                unit=_cyberknife_unit(spec.key),
                inputs_required="CyberKnife MLC segment apertures, segment MU, and interval grouping from beam-path XML",
                implementation_status="implemented",
                notes="Implements the paper-limited six-metric MLC subset only.",
            )
        )
    return records


def _build_aurora_metric_records() -> list[MetricDefinitionRecord]:
    records: list[MetricDefinitionRecord] = []
    aurora_notes = get_aurora_metric_notes()
    for metric_key in V2_METRIC_ORDER:
        records.append(
            MetricDefinitionRecord(
                platform="AURORA",
                group=_aurora_group(metric_key),
                metric_key=metric_key,
                display_name=metric_key,
                symbol_or_short_name=metric_key,
                mathematical_definition=_aurora_formula(metric_key),
                physical_meaning=aurora_notes.get(metric_key, ""),
                unit=_aurora_unit(metric_key),
                inputs_required="Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2",
                implementation_status="implemented",
                notes="Standalone Aurora SVMAT Lab metric.",
            )
        )
    for metric_key in V3_METRIC_ORDER:
        records.append(
            MetricDefinitionRecord(
                platform="AURORA",
                group=_aurora_group(metric_key),
                metric_key=metric_key,
                display_name=metric_key,
                symbol_or_short_name=metric_key,
                mathematical_definition=_aurora_formula(metric_key),
                physical_meaning=aurora_notes.get(metric_key, ""),
                unit=_aurora_unit(metric_key),
                inputs_required="Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2",
                implementation_status="implemented",
                notes="Standalone Aurora SVMAT Lab metric.",
            )
        )
    for metric_key in LEGACY_METRIC_ORDER:
        records.append(
            MetricDefinitionRecord(
                platform="AURORA",
                group=_aurora_group(metric_key),
                metric_key=metric_key,
                display_name=metric_key,
                symbol_or_short_name=metric_key,
                mathematical_definition=_aurora_formula(metric_key),
                physical_meaning=aurora_notes.get(metric_key, ""),
                unit=_aurora_unit(metric_key),
                inputs_required="Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2",
                implementation_status="implemented",
                notes="Retained for comparison against the v2 paper-style metrics.",
            )
        )
    return records


def _write_csv(records: Sequence[MetricDefinitionRecord], csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(records[0]).keys()))
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def _write_markdown(records: Sequence[MetricDefinitionRecord], markdown_path: Path) -> None:
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Metric Definitions",
        "",
        "This document summarizes the mathematical definitions and physical meanings of all metrics currently implemented in the project.",
        "",
        "Definitions are written to match the current code implementation. They are not automatically identical to the original publication notation unless noted.",
        "",
    ]
    sections = [
        ("VMAT/IMRT", "VMAT_IMRT"),
        ("TOMO", "TOMO"),
        ("CyberKnife MLC", "CYBERKNIFE_MLC"),
        ("Aurora SVMAT Lab", "AURORA"),
    ]
    for section_title, platform in sections:
        lines.extend([f"## {section_title}", ""])
        for record in [item for item in records if item.platform == platform]:
            lines.extend(
                [
                    f"### `{record.metric_key}` - {record.display_name}",
                    "",
                    f"- Group: {record.group}",
                    f"- Symbol/short name: {record.symbol_or_short_name}",
                    f"- Mathematical definition: {record.mathematical_definition}",
                    f"- Physical meaning: {record.physical_meaning}",
                    f"- Unit: {record.unit}",
                    f"- Inputs required: {record.inputs_required}",
                    f"- Status: {record.implementation_status}",
                    f"- Notes: {record.notes or 'None'}",
                    "",
                ]
            )
    markdown_path.write_text("\n".join(lines), encoding="utf-8")


def _write_platform_appendices(records: Sequence[MetricDefinitionRecord], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    appendix_specs = (
        ("VMAT_IMRT", "VMAT/IMRT", "metric_definitions_vmat_imrt.md"),
        ("TOMO", "TOMO", "metric_definitions_tomo.md"),
        ("CYBERKNIFE_MLC", "CyberKnife MLC", "metric_definitions_cyberknife_mlc.md"),
        ("AURORA", "Aurora SVMAT Lab", "metric_definitions_aurora.md"),
    )
    for platform, title, filename in appendix_specs:
        platform_records = [record for record in records if record.platform == platform]
        lines = [
            f"# {title} Metric Definitions",
            "",
            "This appendix is generated from the shared metric-definition catalog.",
            "",
        ]
        for record in platform_records:
            lines.extend(
                [
                    f"## `{record.metric_key}` - {record.display_name}",
                    "",
                    f"- Group: {record.group}",
                    f"- Symbol/short name: {record.symbol_or_short_name}",
                    f"- Mathematical definition: {record.mathematical_definition}",
                    f"- Physical meaning: {record.physical_meaning}",
                    f"- Unit: {record.unit}",
                    f"- Inputs required: {record.inputs_required}",
                    f"- Status: {record.implementation_status}",
                    f"- Notes: {record.notes or 'None'}",
                    "",
                ]
            )
        (output_dir / filename).write_text("\n".join(lines), encoding="utf-8")


def _vmat_group(metric_key: str) -> str:
    if metric_key in {"mus", "pmu", "muca", "fraction_dose_gy", "fractions_count", "mucgy", "narcs"}:
        return "Plan prescription"
    if metric_key in {"al", "cal", "gt", "mudeg"}:
        return "Arc geometry"
    if metric_key in {"lt", "ltmu", "ltnlmu", "nl", "ltnl", "lna", "ltal"}:
        return "Leaf travel"
    if metric_key in {"mdrv", "mgsv", "dr", "gs", "ls", "dt", "mlc_speed_acc"}:
        return "Delivery dynamics"
    if metric_key in {"mcsv", "aav", "lsv", "tg"}:
        return "McNiven-style modulation"
    if metric_key.startswith("mi_"):
        return "MI family"
    if metric_key in {"pi", "pm", "md"}:
        return "Shape modulation"
    if metric_key in {"pa", "ja", "efs", "psmall", "sas_5mm", "sas_10mm", "sas_20mm", "em", "bjar", "mad", "alg", "alg_sd", "perimeter", "asr", "axjd", "ayjd", "cam", "eam"}:
        return "Aperture geometry"
    if metric_key == "sport":
        return "SPORT"
    return "VMAT/IMRT"


def _vmat_formula(metric_key: str) -> str:
    formulas = {
        "mus": "MUs = sum_beams(MU_beam)",
        "pmu": "PMU = MUs * (2 Gy / fraction dose in Gy)",
        "muca": "MUCA = MUs / N_control_arcs",
        "fraction_dose_gy": "Fraction dose = prescribed dose / number of fractions",
        "fractions_count": "Fractions = N_fx",
        "mucgy": "MUcGy = MUs / prescribed dose in cGy",
        "lt": "LT = weighted mean over control arcs of total leaf travel between adjacent apertures",
        "ltmu": "LTMU = sum(control-arc leaf travel) / MU_beam",
        "ltnlmu": "LTNLMU = sum(leaf travel / active leaves) / MU_beam",
        "nl": "NL = weighted mean over control points of the number of active leaf pairs",
        "ltnl": "LTNL = weighted mean of (leaf travel / active leaves)",
        "al": "AL = total gantry travel / N_beams",
        "lna": "LNA = weighted mean of (leaf travel / active leaves / gantry-step)",
        "cal": "CAL = total gantry travel / N_control_arcs",
        "gt": "GT = sum_beams(abs(gantry rotation angle))",
        "mudeg": "MUdeg = MUs / GT",
        "ltal": "LTAL = weighted mean of (leaf travel / gantry-step)",
        "narcs": "NArcs = number of treatment beams/arcs",
        "mdrv": "mDRV = mean(delta dose-rate / delta gantry)",
        "mgsv": "mGSV = mean(delta gantry-speed / delta gantry)",
        "dr": "DR = mean(control-point dose rate)",
        "gs": "GS = mean(control-point gantry speed)",
        "ls": "LS = mean(leaf speed)",
        "mcsv": "MCSv = weighted mean[((AAV_i + AAV_{i+1}) / 2) * ((LSV_i + LSV_{i+1}) / 2)]",
        "aav": "AAV = aperture area / arc-level union aperture area, then weighted over the arc",
        "lsv": "LSV = bank_LSV(left) * bank_LSV(right), then weighted over the arc",
        "tg": "TG = weighted mean of adjacent-leaf left/right offset magnitudes",
        "mi_0_2": "MI(k=0.2) = (MIs, MIa, MIt) at threshold factor k = 0.2",
        "mi_0_5": "MI(k=0.5) = (MIs, MIa, MIt) at threshold factor k = 0.5",
        "mi_1_0": "MI(k=1.0) = (MIs, MIa, MIt) at threshold factor k = 1.0",
        "mi_2_0": "MI(k=2.0) = (MIs, MIa, MIt) at threshold factor k = 2.0",
        "dt": "dt = mean(control-point time increment) * N_control_points",
        "pi": "PI = perimeter^2 / (4 * pi * area), aggregated over apertures",
        "pm": "PM = mean over adjacent control points of normalized aperture-area change",
        "md": "MD = union-area / weighted mean aperture area",
        "pa": "PA = weighted mean(aperture area)",
        "efs": "EFS = weighted mean(4 * area / perimeter)",
        "psmall": "psmall = weighted fraction(EFS < 30 mm)",
        "sas_5mm": "SAS5mm = active leaf gaps below 5 mm / all active leaf gaps",
        "sas_10mm": "SAS10mm = active leaf gaps below 10 mm / all active leaf gaps",
        "sas_20mm": "SAS20mm = active leaf gaps below 20 mm / all active leaf gaps",
        "em": "EM = aperture edge metric calculated from BEV perimeter relative to area",
        "bjar": "BJAR = aperture area / jaw-defined area",
        "mad": "MAD = mean distance of open leaf ends from the beam central axis",
        "alg": "ALG = mean(opposing leaf gap over active leaf pairs)",
        "alg_sd": "ALG SD = std(opposing leaf gap over active leaf pairs)",
        "perimeter": "P = mean aperture perimeter in beam's-eye view",
        "asr": "ASR = mean number of disconnected open aperture sub-regions",
        "axjd": "AXJD = mean distance between aperture extent and X jaws",
        "ayjd": "AYJD = mean distance between aperture extent and Y jaws",
        "cam": "CAM = converted-aperture complexity metric from transformed field geometry",
        "eam": "EAM = combined edge-and-area aperture complexity metric",
        "sport": "SPORT = weighted aggregate of station-wise MI(s) over the plan",
        "mlc_speed_acc": "For each leaf, compute the proportion of valid intervals falling into each Park 2015 speed/acceleration bin; then average over leaves and beams.",
    }
    return formulas.get(metric_key, f"{metric_key} follows the current implementation-specific aggregation in the VMAT/IMRT workflow.")


def _vmat_unit(metric_key: str) -> str:
    units = {
        "mus": "MU",
        "pmu": "MU",
        "muca": "MU/control arc",
        "fraction_dose_gy": "Gy",
        "fractions_count": "count",
        "mucgy": "MU/cGy",
        "lt": "mm",
        "ltmu": "mm/MU",
        "ltnlmu": "mm/(leaf*MU)",
        "nl": "count",
        "ltnl": "mm/leaf",
        "al": "deg",
        "lna": "mm/(leaf*deg)",
        "cal": "deg/control arc",
        "gt": "deg",
        "mudeg": "MU/deg",
        "ltal": "mm/deg",
        "narcs": "count",
        "mdrv": "MU/(min*deg)",
        "mgsv": "deg/s/deg",
        "dr": "MU/min",
        "gs": "deg/s",
        "ls": "mm/s",
        "dt": "s",
        "pa": "mm^2",
        "ja": "mm^2",
        "efs": "mm",
        "tg": "mm",
        "mad": "mm",
        "alg": "mm",
        "alg_sd": "mm",
        "perimeter": "mm",
    }
    return units.get(metric_key, "dimensionless")


def _vmat_inputs(metric_key: str) -> str:
    if metric_key in {"mus", "pmu", "muca", "fraction_dose_gy", "fractions_count", "mucgy", "narcs"}:
        return "Plan MU, prescription, fraction count, beam list"
    if metric_key in {"al", "cal", "gt", "mudeg"}:
        return "Beam gantry rotation angle and beam MU"
    if metric_key in {"mdrv", "mgsv", "dr", "gs", "ls", "dt", "mlc_speed_acc"}:
        return "Control-point MLC motion, dose rate, gantry angle, and meterset timing"
    return "MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights"


def _tomo_group(metric_key: str) -> str:
    if metric_key in {"mf", "nproj_rot", "nproj", "nrot", "projection_time_s", "gantry_period_s", "treatment_time_s", "field_width_mm", "pitch", "couch_translation_mm", "couch_speed_mm_s", "target_length_mm", "ttdf_s_cgy"}:
        return "Delivery"
    if "lot" in metric_key or "flot" in metric_key or metric_key.startswith("clns") or metric_key.startswith("cfns"):
        return "Leaf open time"
    if metric_key in {"ta", "ncc", "lengthcc", "fdisc", "cls", "clsin", "clsinarea", "clsindisc", "clsinareadisc", "centroid", "l0ns", "l1ns", "l2ns"}:
        return "Sinogram geometry"
    return "Sinogram modulation"


def _tomo_formula(metric_key: str) -> str:
    formulas = {
        "mf": "MF = mean(non-zero LOT) / max(LOT)",
        "nproj_rot": "N proj,rot = configured projections per rotation",
        "nproj": "N proj = number of sinogram projections",
        "nrot": "N rot = N proj / N proj,rot",
        "projection_time_s": "PT = projection time",
        "gantry_period_s": "GP = PT * N proj,rot",
        "treatment_time_s": "TT = PT * N proj",
        "field_width_mm": "FW = nominal tomotherapy field width",
        "pitch": "Pitch = couch advance per rotation / field width",
        "couch_translation_mm": "CT = total couch travel",
        "couch_speed_mm_s": "CS = CT / TT",
        "target_length_mm": "TL = couch translation - field width",
        "ttdf_s_cgy": "TTDF = TT / dose per fraction in cGy",
        "mlot": "mLOT = mean(LOT)",
        "sdlot": "sdLOT = std(LOT)",
        "mdlot": "mdLOT = median(LOT)",
        "molot": "moLOT = mode(LOT)",
        "maxlot": "maxLOT = max(LOT)",
        "minlot": "minLOT = min(non-zero LOT)",
        "klot": "kLOT = kurtosis(LOT)",
        "slot": "sLOT = skewness(LOT)",
        "mflot": "mFLOT = mean(FLOT)",
        "sdflot": "sdFLOT = std(FLOT)",
        "mdflot": "mdFLOT = median(FLOT)",
        "moflot": "moFLOT = mode(FLOT)",
        "maxflot": "maxFLOT = max(FLOT)",
        "minflot": "minFLOT = min(non-zero FLOT)",
        "ta": "TA = mean projection treatment width across the sinogram",
        "ncc": "nCC = mean number of connected open components per projection",
        "lengthcc": "lengthCC = mean connected-component length in the sinogram",
        "fdisc": "fDISC = fraction(projections with more than one connected component)",
        "cls": "CLS = mean[(N_leaves - open leaves) / N_leaves] over projections",
        "clsin": "CLSin = mean(closed leaves inside the treatment area)",
        "clsinarea": "CLSinarea = mean(closed leaves inside the treatment area / treatment area)",
        "clsindisc": "CLSindisc = CLSin restricted to discontinuous projections",
        "clsinareadisc": "CLSinareadisc = area-normalized CLSin restricted to discontinuous projections",
        "centroid": "Centroid = mean lateral centroid of open leaves over projections",
        "l0ns": "L0NS = mean fraction of open leaves with 0 open nearest neighbors",
        "l1ns": "L1NS = mean fraction of open leaves with 1 open nearest neighbor",
        "l2ns": "L2NS = mean fraction of open leaves with 2 open nearest neighbors",
        "lotv": "LOTV = mean over leaves of [ sum(max(LOT) - abs(delta LOT)) / ((N_proj - 1) * max(LOT)) ]",
        "elotv_1": "ELOTV-1 = mean normalized abs(LOT_i - LOT_{i+1}) over leaves",
        "elotv_5": "ELOTV-5 = mean normalized abs(LOT_i - LOT_{i+5}) over leaves",
        "pstv": "PSTV = EPSTV with delta projection = 1 and delta leaf = 1",
        "epstv_1_1": "EPSTV-1,1 = mean of abs(delta projection) + abs(delta leaf) sinogram differences for offsets (1,1)",
        "epstv_1_0": "EPSTV-1,0 = mean sinogram difference for projection offset 1 and leaf offset 0",
        "epstv_0_1": "EPSTV-0,1 = mean sinogram difference for projection offset 0 and leaf offset 1",
        "mi": "MI = trapezoidal integral over threshold factor f of the mean fraction of directional sinogram differences exceeding f * sd(FLOT)",
        "noc": "nOC = mean per leaf of [2 * merged open intervals / N_proj]",
        "msa": "mSA = sum(position * mean leaf opening) / sum(mean leaf opening)",
        "msi": "mSI = mean leaf-open intensity over leaves",
        "mdsi": "mdSI = median leaf-open intensity over leaves",
        "sdsi": "sdSI = std leaf-open intensity over leaves",
    }
    if metric_key.startswith("clns_"):
        threshold = metric_key.replace("clns_", "").replace("ms", "")
        return f"CLNS{threshold} = count(LOT < {threshold} ms) / count(non-zero LOT)"
    if metric_key.startswith("clns_pt_"):
        threshold = metric_key.replace("clns_pt_", "").replace("ms", "")
        return f"CLNSpt{threshold} = count(LOT > projection time - {threshold} ms) / count(non-zero LOT)"
    if metric_key.startswith("cfns_"):
        threshold = metric_key.replace("cfns_", "").replace("_", ".")
        return f"CFNS{threshold} = count(FLOT < {threshold}) / count(non-zero FLOT)"
    return formulas.get(metric_key, f"{metric_key} follows the current tomotherapy sinogram implementation.")


def _tomo_unit(metric_key: str) -> str:
    if metric_key in {"nproj_rot", "nproj", "nrot", "ncc", "l0ns", "l1ns", "l2ns", "noc"}:
        return "count"
    if metric_key.endswith("_s") or metric_key in {"projection_time_s", "gantry_period_s", "treatment_time_s", "ttdf_s_cgy"}:
        return "s" if metric_key != "ttdf_s_cgy" else "s/cGy"
    if metric_key.endswith("_mm") or metric_key in {"field_width_mm", "couch_translation_mm", "target_length_mm", "lengthcc", "ta", "centroid"}:
        return "mm"
    if metric_key == "couch_speed_mm_s":
        return "mm/s"
    if "lot" in metric_key and not "flot" in metric_key:
        return "ms"
    return "dimensionless"


def _tomo_inputs(metric_key: str) -> str:
    if _tomo_group(metric_key) == "Delivery":
        return "Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose"
    return "Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology"


def _cyberknife_formula(metric_key: str) -> str:
    formulas = {
        "mcs": "MCS = sum_segments[(MU_segment / MU_plan) * AAV_segment * LSV_segment]",
        "em": "EM = sum_segments[(MU_segment / MU_plan) * aperture edge metric]",
        "pi": "PI = sum_segments[(MU_segment / MU_plan) * aperture irregularity]",
        "pm": "PM = sum_intervals[(MU_interval / MU_plan) * (1 - weighted beam area / (MU_interval * union area_interval))]",
        "lg": "LG = sum_segments[(MU_segment / MU_plan) * mean opposing leaf gap_segment]",
        "sas10": "SAS10 = count(open leaf gaps < 10 mm) / count(all open leaf gaps)",
    }
    return formulas[metric_key]


def _cyberknife_unit(metric_key: str) -> str:
    return "mm" if metric_key == "lg" else "dimensionless"


def _aurora_group(metric_key: str) -> str:
    if metric_key in V2_METRIC_ORDER:
        return "V2 paper-style physics"
    if metric_key in LEGACY_METRIC_ORDER:
        return "Legacy engineering"
    if metric_key in {"reversal_symmetry_index", "forward_backward_metric_difference", "beam_pair_balance_index"}:
        return "V3 bidirectional symmetry"
    if metric_key in {"small_opening_fraction", "near_closed_fraction", "effective_small_gap_burden"}:
        return "V3 small-opening burden"
    if metric_key.startswith("projection_pitch_") or metric_key.startswith("projection_mu_density_") or metric_key.startswith("projection_aperture_change_") or metric_key.startswith("projection_leaf_travel_"):
        if metric_key.endswith("_p95") or metric_key.endswith("_max") or metric_key.endswith("_top3_mean") or metric_key.endswith("_p95_proxy") or metric_key.endswith("_max_proxy") or metric_key.endswith("_top3_mean_proxy"):
            return "V3 local interval peaks"
    if metric_key.startswith("head_") or metric_key.startswith("mid_") or metric_key.startswith("tail_"):
        return "V3 axial regions"
    if metric_key in {"layer_imbalance_index", "layer_correlation_index", "x1_x2_aperture_disparity", "x1_x2_leaf_travel_ratio"}:
        return "V3 dual-layer coordination"
    return "Aurora research"


def _aurora_formula(metric_key: str) -> str:
    formulas = {
        "longitudinal_travel_mm": "sum_i abs(delta z_i)",
        "total_rotation_deg": "sum_i abs(delta theta_i)",
        "rotations": "total rotation / 360",
        "travel_per_rotation_mm": "longitudinal travel / rotations",
        "projection_pitch_mean": "mean_i(abs(delta z_i) / abs(delta theta_i))",
        "projection_pitch_cv": "std(projection pitch_i) / mean(projection pitch_i)",
        "projection_mu_density_mean_proxy": "mean_i(abs(delta w_i) / abs(delta z_i))",
        "projection_mu_density_cv_proxy": "std(abs(delta w_i) / abs(delta z_i)) / mean(abs(delta w_i) / abs(delta z_i))",
        "projection_aperture_change_mean": "mean_i(abs(delta A_i) / abs(delta z_i))",
        "projection_aperture_change_cv": "std(abs(delta A_i) / abs(delta z_i)) / mean(abs(delta A_i) / abs(delta z_i))",
        "projection_leaf_travel_mean": "mean_i(delta L_i / abs(delta z_i)), with delta L_i summed across both MLC layers",
        "projection_leaf_travel_cv": "std(delta L_i / abs(delta z_i)) / mean(delta L_i / abs(delta z_i))",
        "projection_leaf_travel_mean_mlcx1": "mean_i(delta L_i_MLCX1 / abs(delta z_i))",
        "projection_leaf_travel_cv_mlcx1": "std(delta L_i_MLCX1 / abs(delta z_i)) / mean(delta L_i_MLCX1 / abs(delta z_i))",
        "projection_leaf_travel_mean_mlcx2": "mean_i(delta L_i_MLCX2 / abs(delta z_i))",
        "projection_leaf_travel_cv_mlcx2": "std(delta L_i_MLCX2 / abs(delta z_i)) / mean(delta L_i_MLCX2 / abs(delta z_i))",
        "theta_z_coupling_cv": "projection_pitch_cv",
        "mu_z_coupling_cv_proxy": "projection_mu_density_cv_proxy",
        "mlc_z_coupling_cv": "projection_leaf_travel_cv",
        "mlcx1_z_coupling_cv": "projection_leaf_travel_cv_mlcx1",
        "mlcx2_z_coupling_cv": "projection_leaf_travel_cv_mlcx2",
        "reversal_symmetry_index": "mean over selected burden families of [1 - abs(forward_mean - backward_mean) / (abs(forward_mean) + abs(backward_mean))]",
        "forward_backward_metric_difference": "abs(mean_forward(coupled_modulation_index) - mean_backward(coupled_modulation_index))",
        "beam_pair_balance_index": "1 - abs(sum_forward(coupled_modulation_index) - sum_backward(coupled_modulation_index)) / (sum_forward + sum_backward)",
        "small_opening_fraction": "weighted count(gap < 10 mm and gap > 0) / weighted count(gap > 0)",
        "near_closed_fraction": "weighted count(gap < 2 mm and gap > 0) / weighted count(gap > 0)",
        "effective_small_gap_burden": "weighted mean of max(0, 1 - gap / 10 mm) over open effective gaps",
        "projection_pitch_p95": "nearest-rank 95th percentile of projection_pitch_i",
        "projection_pitch_max": "max(projection_pitch_i)",
        "projection_pitch_top3_mean": "mean of the three largest projection_pitch_i values",
        "projection_mu_density_p95_proxy": "nearest-rank 95th percentile of projection_mu_density_proxy_i",
        "projection_mu_density_max_proxy": "max(projection_mu_density_proxy_i)",
        "projection_mu_density_top3_mean_proxy": "mean of the three largest projection_mu_density_proxy_i values",
        "projection_aperture_change_p95": "nearest-rank 95th percentile of projection_aperture_change_i",
        "projection_aperture_change_max": "max(projection_aperture_change_i)",
        "projection_aperture_change_top3_mean": "mean of the three largest projection_aperture_change_i values",
        "projection_leaf_travel_p95": "nearest-rank 95th percentile of projection_leaf_travel_i",
        "projection_leaf_travel_max": "max(projection_leaf_travel_i)",
        "projection_leaf_travel_top3_mean": "mean of the three largest projection_leaf_travel_i values",
        "head_mu_density_mean_proxy": "mean(projection_mu_density_proxy_i) over head-third intervals",
        "head_mu_density_cv_proxy": "CV(projection_mu_density_proxy_i) over head-third intervals",
        "head_aperture_change_mean": "mean(projection_aperture_change_i) over head-third intervals",
        "head_aperture_change_cv": "CV(projection_aperture_change_i) over head-third intervals",
        "head_leaf_travel_mean": "mean(projection_leaf_travel_i) over head-third intervals",
        "head_leaf_travel_cv": "CV(projection_leaf_travel_i) over head-third intervals",
        "mid_mu_density_mean_proxy": "mean(projection_mu_density_proxy_i) over mid-third intervals",
        "mid_mu_density_cv_proxy": "CV(projection_mu_density_proxy_i) over mid-third intervals",
        "mid_aperture_change_mean": "mean(projection_aperture_change_i) over mid-third intervals",
        "mid_aperture_change_cv": "CV(projection_aperture_change_i) over mid-third intervals",
        "mid_leaf_travel_mean": "mean(projection_leaf_travel_i) over mid-third intervals",
        "mid_leaf_travel_cv": "CV(projection_leaf_travel_i) over mid-third intervals",
        "tail_mu_density_mean_proxy": "mean(projection_mu_density_proxy_i) over tail-third intervals",
        "tail_mu_density_cv_proxy": "CV(projection_mu_density_proxy_i) over tail-third intervals",
        "tail_aperture_change_mean": "mean(projection_aperture_change_i) over tail-third intervals",
        "tail_aperture_change_cv": "CV(projection_aperture_change_i) over tail-third intervals",
        "tail_leaf_travel_mean": "mean(projection_leaf_travel_i) over tail-third intervals",
        "tail_leaf_travel_cv": "CV(projection_leaf_travel_i) over tail-third intervals",
        "layer_imbalance_index": "abs(mean(leaf_travel_i_MLCX1) - mean(leaf_travel_i_MLCX2)) / (abs(mean_MLCX1) + abs(mean_MLCX2))",
        "layer_correlation_index": "correlation(projection_leaf_travel_i_MLCX1, projection_leaf_travel_i_MLCX2)",
        "x1_x2_aperture_disparity": "mean over control points of abs(sum|MLCX1| - sum|MLCX2|) / (sum|MLCX1| + sum|MLCX2|)",
        "x1_x2_leaf_travel_ratio": "mean(projection_leaf_travel_i_MLCX1) / mean(projection_leaf_travel_i_MLCX2)",
        "axial_travel_mm": "sum_i abs(delta z_i)",
        "gantry_rotation_deg": "sum_i abs(delta theta_i)",
        "mm_per_deg": "axial travel / total rotation",
        "mm_per_rotation": "axial travel / (total rotation / 360)",
        "pitch_consistency": "std(abs(delta z_i) / abs(delta theta_i)) / mean(abs(delta z_i) / abs(delta theta_i))",
        "mu_per_mm": "MU_total / axial travel",
        "aperture_change_per_mm": "sum_i abs(delta A_i) / sum_i abs(delta z_i)",
        "leaf_travel_per_mm": "sum_i delta L_i / sum_i abs(delta z_i)",
        "coupled_modulation_index": "mean of normalized aperture-change/mm, leaf-travel/mm, MU-density variability, and pitch variability",
    }
    return formulas.get(metric_key, f"{metric_key} follows the current Aurora implementation.")


def _aurora_unit(metric_key: str) -> str:
    units = {
        "longitudinal_travel_mm": "mm",
        "total_rotation_deg": "deg",
        "rotations": "turns",
        "travel_per_rotation_mm": "mm/rotation",
        "projection_pitch_mean": "mm/deg",
        "projection_pitch_p95": "mm/deg",
        "projection_pitch_max": "mm/deg",
        "projection_pitch_top3_mean": "mm/deg",
        "projection_mu_density_mean_proxy": "weight/mm",
        "projection_mu_density_p95_proxy": "weight/mm",
        "projection_mu_density_max_proxy": "weight/mm",
        "projection_mu_density_top3_mean_proxy": "weight/mm",
        "projection_aperture_change_mean": "mm/mm",
        "projection_aperture_change_p95": "mm/mm",
        "projection_aperture_change_max": "mm/mm",
        "projection_aperture_change_top3_mean": "mm/mm",
        "projection_leaf_travel_mean": "mm/mm",
        "projection_leaf_travel_p95": "mm/mm",
        "projection_leaf_travel_max": "mm/mm",
        "projection_leaf_travel_top3_mean": "mm/mm",
        "projection_leaf_travel_mean_mlcx1": "mm/mm",
        "projection_leaf_travel_mean_mlcx2": "mm/mm",
        "head_mu_density_mean_proxy": "weight/mm",
        "mid_mu_density_mean_proxy": "weight/mm",
        "tail_mu_density_mean_proxy": "weight/mm",
        "head_aperture_change_mean": "mm/mm",
        "mid_aperture_change_mean": "mm/mm",
        "tail_aperture_change_mean": "mm/mm",
        "head_leaf_travel_mean": "mm/mm",
        "mid_leaf_travel_mean": "mm/mm",
        "tail_leaf_travel_mean": "mm/mm",
        "axial_travel_mm": "mm",
        "gantry_rotation_deg": "deg",
        "mm_per_deg": "mm/deg",
        "mm_per_rotation": "mm/rotation",
        "mu_per_mm": "MU/mm",
        "aperture_change_per_mm": "mm/mm",
        "leaf_travel_per_mm": "mm/mm",
    }
    return units.get(metric_key, "dimensionless")


def _notes_for_metric(metric_key: str, *, dual_mlc: bool) -> str:
    if metric_key.startswith("mi_"):
        return "The base key returns a tuple of speed, acceleration, and total MI components before flattening."
    if metric_key == "mlc_speed_acc":
        return "The base key returns binned speed/acceleration proportions and summary statistics before flattening."
    if dual_mlc:
        return "For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants."
    return ""


def _slugify_group_label(group_label: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", group_label.strip().lower())
    slug = re.sub(r"_+", "_", slug)
    return slug.strip("_")
