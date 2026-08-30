import csv
import os
import re
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Iterable, List, Sequence

import pydicom

from analysis_helpers import (
    calculate_core_metrics,
    calculate_core_metrics_with_warnings,
    calculate_cyberknife_mlc_metrics,
    get_plan_metadata,
)
from aurora_svmat_lab.parser import is_aurora_rtplan
from aurora_svmat_lab.service import analyze_plan_file as analyze_aurora_plan_file
from cyberknife_parser import build_cyberknife_plan_dict, parse_cyberknife_beams, resolve_referenced_xml_paths
from DicomParse.dicom_rt import RTPlan
from DicomParse.utilities import retrieve_dcm_filenames
from metric_registry import (
    VMAT_DUAL_MLC_KEYS,
    metric_descriptions_with_aliases,
    metric_gui_labels_with_aliases,
    metric_labels_with_aliases,
)
from tomo_metrics import calculate_tomo_metrics
from tomo_parser import parse_tomo_rtplan
from ucomx_models import AnalysisMode, PlanAnalysisResult


SPEED_BUCKET_LABELS = ("0_4", "4_8", "8_12", "12_16", "16_20")
ACC_BUCKET_LABELS = ("0_40", "40_80", "80_120", "120_160", "160_200")
MI_COMPONENT_LABELS = ("mis", "mia", "mit")
DUAL_MLC_METRICS = set(VMAT_DUAL_MLC_KEYS)
METRIC_LABELS = metric_labels_with_aliases()
METRIC_GUI_LABELS = metric_gui_labels_with_aliases()
METRIC_DESCRIPTIONS = metric_descriptions_with_aliases()


class UnsupportedModeError(RuntimeError):
    pass


def _first_treatment_beam(beam_sequence: Sequence[Any]) -> Any | None:
    for beam in beam_sequence:
        if str(getattr(beam, "TreatmentDeliveryType", "")).upper() != "SETUP":
            return beam
    return None


def detect_mode(metadata: Dict[str, Any]) -> AnalysisMode:
    machine_id = str(metadata.get("machine_id", "")).lower()
    model = str(metadata.get("calculation_model", "")).lower()
    manufacturer_model = str(metadata.get("manufacturer_model_name", "")).lower()
    plan_name = str(metadata.get("plan_name", "")).lower()
    plan_label = str(metadata.get("plan_label", "")).lower()
    manufacturer = str(metadata.get("manufacturer", "")).lower()

    if (
        any(token in manufacturer for token in ("wisdomtech", "neurt"))
        or any(token in model for token in ("deepplan", "aurora"))
        or any(token in manufacturer_model for token in ("deepplan", "aurora"))
        or "aurora" in plan_name
        or "aurora" in plan_label
    ):
        return AnalysisMode.AURORA
    if any(token in machine_id for token in ("tomo", "tomotherapy", "radixact")):
        return AnalysisMode.TOMO
    if any(token in model for token in ("tomo", "tomotherapy", "radixact")):
        return AnalysisMode.TOMO
    if "tomo" in plan_name:
        return AnalysisMode.TOMO
    if (
        ("accuray" in manufacturer or "cyberknife" in machine_id or "cyberknife" in model)
        and ("mlc" in plan_name or "mlc" in plan_label)
    ):
        return AnalysisMode.CYBERKNIFE_MLC
    return AnalysisMode.VMAT_IMRT


def detect_mode_from_file(source_path: str) -> AnalysisMode:
    ds = pydicom.dcmread(source_path, force=True, stop_before_pixels=True)
    if is_aurora_rtplan(ds):
        return AnalysisMode.AURORA
    manufacturer = str(getattr(ds, "Manufacturer", "")).lower()
    model = str(getattr(ds, "ManufacturerModelName", "")).lower()
    plan_name = str(getattr(ds, "RTPlanName", "")).lower()
    plan_label = str(getattr(ds, "RTPlanLabel", "")).lower()
    beam_sequence = getattr(ds, "BeamSequence", [])
    treatment_beam = _first_treatment_beam(beam_sequence)
    if treatment_beam is None:
        return AnalysisMode.VMAT_IMRT

    machine_id = str(getattr(treatment_beam, "TreatmentMachineName", "")).lower()
    if any(token in machine_id for token in ("tomo", "tomotherapy", "radixact")):
        return AnalysisMode.TOMO

    beam_types = {str(getattr(item, "RTBeamLimitingDeviceType", "")).upper() for item in getattr(treatment_beam, "BeamLimitingDeviceSequence", [])}
    has_mlc = any(name.startswith("MLCX") for name in beam_types)
    if (
        ("accuray" in manufacturer or "cyberknife" in machine_id or "cyberknife" in model)
        and (has_mlc or "mlc" in plan_name or "mlc" in plan_label or "mlc" in os.path.basename(source_path).lower())
    ):
        return AnalysisMode.CYBERKNIFE_MLC
    return AnalysisMode.VMAT_IMRT


def _has_standard_mlc_geometry(plan_dict: Dict[str, Any]) -> bool:
    for beam in plan_dict.get("beams", {}).values():
        for key in beam.keys():
            if str(key).upper().startswith("MLCX"):
                return True
    return False


def _has_any_mlc_geometry(plan_dict: Dict[str, Any]) -> bool:
    return _has_standard_mlc_geometry(plan_dict)


def _unsupported_result(
    *,
    source_path: str,
    mode: AnalysisMode,
    metadata: Dict[str, Any],
    warning: str,
) -> PlanAnalysisResult:
    return PlanAnalysisResult(
        source_path=source_path,
        mode=mode,
        metadata=metadata,
        metrics={},
        flattened_metrics={},
        supported=False,
        warnings=[warning],
    )


def analyze_plan_file(source_path: str, requested_mode: AnalysisMode = AnalysisMode.AUTO) -> PlanAnalysisResult:
    detected_mode_from_file = detect_mode_from_file(source_path)
    if requested_mode == AnalysisMode.AUTO and detected_mode_from_file in (
        AnalysisMode.TOMO,
        AnalysisMode.CYBERKNIFE_MLC,
        AnalysisMode.AURORA,
    ):
        requested_mode = detected_mode_from_file

    if requested_mode == AnalysisMode.AURORA:
        return _adapt_aurora_result(
            source_path=source_path,
            result=analyze_aurora_plan_file(source_path),
        )

    if requested_mode == AnalysisMode.TOMO:
        tomo_plan, warnings = parse_tomo_rtplan(source_path)
        metrics = calculate_tomo_metrics(tomo_plan)
        flattened_metrics = flatten_metrics(metrics)
        return PlanAnalysisResult(
            source_path=source_path,
            mode=AnalysisMode.TOMO,
            metadata=tomo_plan.metadata,
            metrics=metrics,
            flattened_metrics=flattened_metrics,
            supported=True,
            warnings=warnings,
        )

    plan_info = RTPlan(filename=source_path)
    plan_dict = plan_info.to_plan_dict()
    metadata = get_plan_metadata(plan_info, plan_dict)
    detected_mode = detect_mode(metadata)
    active_mode = detected_mode if requested_mode == AnalysisMode.AUTO else requested_mode
    if active_mode == AnalysisMode.VMAT_IMRT:
        metadata["metric_formula_version"] = "hybrid-v2"
    cyberknife_beams = None

    if active_mode == AnalysisMode.TOMO:
        tomo_plan, warnings = parse_tomo_rtplan(source_path)
        metrics = calculate_tomo_metrics(tomo_plan)
        flattened_metrics = flatten_metrics(metrics)
        return PlanAnalysisResult(
            source_path=source_path,
            mode=active_mode,
            metadata=tomo_plan.metadata,
            metrics=metrics,
            flattened_metrics=flattened_metrics,
            supported=True,
            warnings=warnings,
        )

    if active_mode == AnalysisMode.CYBERKNIFE_MLC and not _has_standard_mlc_geometry(plan_dict):
        plan_dir = os.path.dirname(source_path)
        resolved_xml_paths, missing_xml = resolve_referenced_xml_paths(plan_dict, plan_dir)
        if missing_xml:
            return _unsupported_result(
                source_path=source_path,
                mode=active_mode,
                metadata=metadata,
                warning=(
                    "CyberKnife MLC plan references external beam-path XML files that are not present: "
                    + ", ".join(sorted(set(missing_xml)))
                ),
            )
        cyberknife_beams = None
        try:
            cyberknife_beams = parse_cyberknife_beams(
                resolved_xml_paths,
                machine_name=str(metadata.get("machine_id", "")) or "CyberKnife MLC",
            )
            plan_dict = build_cyberknife_plan_dict(
                plan_dict,
                resolved_xml_paths,
                machine_name=str(metadata.get("machine_id", "")) or "CyberKnife MLC",
            )
        except ValueError as exc:
            return _unsupported_result(
                source_path=source_path,
                mode=active_mode,
                metadata=metadata,
                warning=str(exc),
            )

    if active_mode == AnalysisMode.VMAT_IMRT and not _has_any_mlc_geometry(plan_dict):
        return _unsupported_result(
            source_path=source_path,
            mode=active_mode,
            metadata=metadata,
            warning="RT Plan does not contain usable MLC leaf geometry, so aperture-based complexity metrics cannot be computed.",
        )

    metric_warnings = []
    try:
        if active_mode == AnalysisMode.CYBERKNIFE_MLC:
            metrics = calculate_cyberknife_mlc_metrics(
                plan_dict, cyberknife_beams=cyberknife_beams
            )
        else:
            metrics, metric_warnings = calculate_core_metrics_with_warnings(plan_dict)
    except IndexError as exc:
        return _unsupported_result(
            source_path=source_path,
            mode=active_mode,
            metadata=metadata,
            warning=f"Aperture geometry is empty or incomplete for this plan: {exc}",
        )
    flattened_metrics = flatten_metrics(metrics)
    warnings = list(metric_warnings)
    if detected_mode != active_mode:
        warnings.append(f"Requested mode {active_mode.value} overrides detected mode {detected_mode.value}.")

    return PlanAnalysisResult(
        source_path=source_path,
        mode=active_mode,
        metadata=metadata,
        metrics=metrics,
        flattened_metrics=flattened_metrics,
        supported=True,
        warnings=warnings,
    )


def _adapt_aurora_result(*, source_path: str, result: Any) -> PlanAnalysisResult:
    aurora_metadata = result.metadata
    metrics = dict(getattr(result, "plan_metrics", {}) or {})
    warnings = list(getattr(result, "warnings", []) or [])
    reason = str(getattr(result, "reason", "") or "")
    supported = bool(getattr(result, "supported", False))
    if not supported and reason and reason not in warnings:
        warnings.insert(0, reason)

    metadata = {
        "patient_id": getattr(aurora_metadata, "patient_id", ""),
        "patient_name": "",
        "plan_name": getattr(aurora_metadata, "plan_name", ""),
        "plan_label": getattr(aurora_metadata, "plan_label", ""),
        "manufacturer": getattr(aurora_metadata, "manufacturer", ""),
        "manufacturer_model_name": getattr(aurora_metadata, "manufacturer_model_name", ""),
        "machine_id": getattr(aurora_metadata, "treatment_machine_name", ""),
        "calculation_model": getattr(aurora_metadata, "manufacturer_model_name", ""),
        "prescribed_dose": "",
        "mu": "",
        "beam_type": "AURORA_SVMAT",
        "beam_number": getattr(aurora_metadata, "beam_count", 0),
        "rotation_direction": "",
        "study_instance_uid": getattr(aurora_metadata, "study_instance_uid", ""),
        "series_instance_uid": getattr(aurora_metadata, "series_instance_uid", ""),
        "sop_instance_uid": getattr(aurora_metadata, "sop_instance_uid", ""),
    }
    return PlanAnalysisResult(
        source_path=source_path,
        mode=AnalysisMode.AURORA,
        metadata=metadata,
        metrics=metrics,
        flattened_metrics=flatten_metrics(metrics),
        supported=supported,
        warnings=warnings,
    )


def analyze_directory(directory: str, requested_mode: AnalysisMode = AnalysisMode.AUTO, recursive: bool = True) -> List[PlanAnalysisResult]:
    filepaths = retrieve_dcm_filenames(directory, recursive=recursive)
    return list(analyze_filepaths(filepaths, requested_mode=requested_mode))


def analyze_filepaths(filepaths: Sequence[str], requested_mode: AnalysisMode = AnalysisMode.AUTO) -> Iterable[PlanAnalysisResult]:
    filepaths = list(filepaths)
    if len(filepaths) <= 1:
        for source_path in filepaths:
            yield _analyze_plan_file_safe(source_path, requested_mode)
        return

    max_workers = min(4, max(1, os.cpu_count() or 1))
    # Batch mode benefits from light parallelism because each file is independent and
    # spends meaningful time in pydicom/numpy code outside the Python interpreter loop.
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        yield from executor.map(lambda path: _analyze_plan_file_safe(path, requested_mode), filepaths)


def flatten_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    flattened: "OrderedDict[str, Any]" = OrderedDict()

    for key, value in metrics.items():
        if key.startswith("mi_") and _is_sequence(value, expected_len=3):
            for label, item in zip(MI_COMPONENT_LABELS, value):
                flattened[f"{key}_{label}"] = item
            continue

        if key.startswith("mi_") and _is_sequence(value, expected_len=2) and all(
            _is_sequence(item, expected_len=3) for item in value
        ):
            for mlc_label, triple in zip(("mlcx1", "mlcx2"), value):
                for component_label, item in zip(MI_COMPONENT_LABELS, triple):
                    flattened[f"{key}_{mlc_label}_{component_label}"] = item
            continue

        if key == "mlc_speed_acc" and _is_sequence(value, expected_len=3):
            speed, acceleration, summary = value
            for label, item in zip(SPEED_BUCKET_LABELS, speed):
                flattened[f"speed_{label}"] = item
            for label, item in zip(ACC_BUCKET_LABELS, acceleration):
                flattened[f"acc_{label}"] = item
            if len(summary) >= 4:
                flattened["speed_average"] = summary[0]
                flattened["acc_average"] = summary[1]
                flattened["speed_std"] = summary[2]
                flattened["acc_std"] = summary[3]
            continue

        if key == "mlc_speed_acc" and _is_sequence(value, expected_len=6):
            speed_1, acc_1, summary_1, speed_2, acc_2, summary_2 = value
            for label, item in zip(SPEED_BUCKET_LABELS, speed_1):
                flattened[f"mlcx1_speed_{label}"] = item
            for label, item in zip(ACC_BUCKET_LABELS, acc_1):
                flattened[f"mlcx1_acc_{label}"] = item
            if len(summary_1) >= 4:
                flattened["mlcx1_speed_average"] = summary_1[0]
                flattened["mlcx1_acc_average"] = summary_1[1]
                flattened["mlcx1_speed_std"] = summary_1[2]
                flattened["mlcx1_acc_std"] = summary_1[3]

            for label, item in zip(SPEED_BUCKET_LABELS, speed_2):
                flattened[f"mlcx2_speed_{label}"] = item
            for label, item in zip(ACC_BUCKET_LABELS, acc_2):
                flattened[f"mlcx2_acc_{label}"] = item
            if len(summary_2) >= 4:
                flattened["mlcx2_speed_average"] = summary_2[0]
                flattened["mlcx2_acc_average"] = summary_2[1]
                flattened["mlcx2_speed_std"] = summary_2[2]
                flattened["mlcx2_acc_std"] = summary_2[3]
            continue

        if key in DUAL_MLC_METRICS and _is_sequence(value, expected_len=2):
            flattened[f"{key}_mlcx1"] = value[0]
            flattened[f"{key}_mlcx2"] = value[1]
            continue

        if isinstance(value, (list, tuple)):
            for index, item in enumerate(value, start=1):
                flattened[f"{key}_{index}"] = item
            continue

        flattened[key] = value

    return flattened


def export_results_to_csv(results: Sequence[PlanAnalysisResult], output_csv: str) -> None:
    exportable_results = list(results)
    if not exportable_results:
        raise ValueError("No analysis results available for export.")

    headers = list(build_export_record(exportable_results[0]).keys())
    for result in exportable_results[1:]:
        for key in build_export_record(result).keys():
            if key not in headers:
                headers.append(key)

    with open(output_csv, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for result in exportable_results:
            writer.writerow(build_export_record(result))

    export_metric_reference_csv(exportable_results, output_csv)


def build_export_record(result: PlanAnalysisResult) -> Dict[str, Any]:
    record: "OrderedDict[str, Any]" = OrderedDict()
    record["source_path"] = result.source_path
    record["file_name"] = os.path.basename(result.source_path)
    record["tps_folder"] = os.path.basename(os.path.dirname(result.source_path))
    record["status"] = result.status
    record["reason"] = result.reason_label
    record["mode"] = result.mode.value
    record["patient_id"] = result.metadata.get("patient_id", "")
    record["patient_name"] = result.metadata.get("patient_name", "")
    record["plan_name"] = result.metadata.get("plan_name", "")
    record["plan_label"] = result.metadata.get("plan_label", "")
    record["machine_id"] = result.metadata.get("machine_id", "")
    record["beam_type"] = result.metadata.get("beam_type", "")
    record["rotation_direction"] = result.metadata.get("rotation_direction", "")
    record["prescribed_dose"] = result.metadata.get("prescribed_dose", "")
    record["mu"] = result.metadata.get("mu", "")
    record["metric_formula_version"] = result.metadata.get("metric_formula_version", "")
    record["warnings"] = " | ".join(result.warnings)
    for key, value in result.flattened_metrics.items():
        record[key] = value
    return record


def export_metric_reference_csv(results: Sequence[PlanAnalysisResult], output_csv: str) -> str:
    reference_csv = os.path.splitext(output_csv)[0] + "_columns.csv"
    seen = OrderedDict()
    for result in results:
        for key in result.flattened_metrics.keys():
            seen[key] = {
                "column_name": key,
                "display_name": METRIC_GUI_LABELS.get(key, METRIC_LABELS.get(key, _humanize_key(key))),
                "description": METRIC_DESCRIPTIONS.get(key, ""),
            }

    with open(reference_csv, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["column_name", "display_name", "description"])
        writer.writeheader()
        for row in seen.values():
            writer.writerow(row)
    return reference_csv


def build_metric_rows(result: PlanAnalysisResult) -> List[List[str]]:
    rows: List[List[str]] = []
    for key, value in result.flattened_metrics.items():
        rows.append([METRIC_GUI_LABELS.get(key, METRIC_LABELS.get(key, _humanize_key(key))), _stringify(value)])
    return rows


def build_metric_reference_rows(result: PlanAnalysisResult) -> List[List[str]]:
    rows: List[List[str]] = []
    for key in result.flattened_metrics.keys():
        if key in METRIC_DESCRIPTIONS:
            rows.append(
                [
                    METRIC_GUI_LABELS.get(key, METRIC_LABELS.get(key, _humanize_key(key))),
                    METRIC_DESCRIPTIONS[key],
                ]
            )
    return rows


def build_metadata_rows(result: PlanAnalysisResult) -> List[List[str]]:
    preferred_order = [
        "analysis_status",
        "analysis_reason",
        "patient_id",
        "patient_name",
        "plan_name",
        "plan_label",
        "machine_id",
        "calculation_model",
        "prescribed_dose",
        "mu",
        "beam_type",
        "beam_number",
        "rotation_direction",
        "metric_formula_version",
    ]
    rows = []
    metadata_view = dict(result.metadata)
    metadata_view["analysis_status"] = result.status
    metadata_view["analysis_reason"] = result.reason_label
    for key in preferred_order:
        if key in metadata_view:
            rows.append([_humanize_key(key), _stringify(metadata_view[key])])

    seen_keys = {item[0].lower().replace(" ", "_") for item in rows}
    for key, value in metadata_view.items():
        if key not in seen_keys and key not in preferred_order:
            rows.append([_humanize_key(key), _stringify(value)])
    return rows


def summarize_results(results: Iterable[PlanAnalysisResult]) -> Dict[str, int]:
    total = 0
    supported = 0
    unsupported = 0
    for result in results:
        total += 1
        if result.supported:
            supported += 1
        else:
            unsupported += 1
    return {"total": total, "supported": supported, "unsupported": unsupported}


def _humanize_key(value: str) -> str:
    return value.replace("_", " ").strip().title()


def _stringify(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    if isinstance(value, (list, tuple)):
        return ", ".join(_stringify(item) for item in value)
    return str(value)


def _is_sequence(value: Any, expected_len: int) -> bool:
    return isinstance(value, (list, tuple)) and len(value) == expected_len


def _analyze_plan_file_safe(source_path: str, requested_mode: AnalysisMode) -> PlanAnalysisResult:
    try:
        return analyze_plan_file(source_path, requested_mode=requested_mode)
    except Exception as exc:
        fallback_mode = requested_mode if requested_mode != AnalysisMode.AUTO else AnalysisMode.VMAT_IMRT
        metadata = {"plan_name": "", "patient_id": "", "patient_name": "", "machine_id": ""}
        if fallback_mode == AnalysisMode.VMAT_IMRT:
            metadata["metric_formula_version"] = "hybrid-v2"
        return PlanAnalysisResult(
            source_path=source_path,
            mode=fallback_mode,
            metadata=metadata,
            metrics={},
            flattened_metrics={},
            supported=False,
            warnings=[f"Failed to parse/analyze file: {exc}"],
        )


