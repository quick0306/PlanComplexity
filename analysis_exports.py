from __future__ import annotations

from metric_registry import VMAT_DUAL_MLC_KEYS, VMAT_METRIC_SPECS


BASE_HEADER = [
    "ID",
    "Name",
    "PlanID",
    "MachineID",
    "Calculation_Model",
    "Prescribed_Dose",
    "MU",
]


def _metric_columns():
    columns = []
    for spec in VMAT_METRIC_SPECS:
        key = spec.key
        label = spec.label
        if key.startswith("mi_"):
            columns.extend([f"{label}_MIs", f"{label}_MIa", f"{label}_MIt"])
        elif key == "mlc_speed_acc":
            columns.extend(
                [
                    "MLC_Speed_0_4",
                    "MLC_Speed_4_8",
                    "MLC_Speed_8_12",
                    "MLC_Speed_12_16",
                    "MLC_Speed_16_20",
                    "MLC_Acc_0_40",
                    "MLC_Acc_40_80",
                    "MLC_Acc_80_120",
                    "MLC_Acc_120_160",
                    "MLC_Acc_160_200",
                    "MLC_Speed_Average",
                    "MLC_Acc_Average",
                    "MLC_Speed_Std",
                    "MLC_Acc_Std",
                ]
            )
        elif key in VMAT_DUAL_MLC_KEYS:
            columns.extend([f"{label}_MLCX1", f"{label}_MLCX2"])
        else:
            columns.append(label)
    return columns


STANDARD_CSV_HEADER = BASE_HEADER + _metric_columns()


def _dual_metric_columns():
    columns = []
    for spec in VMAT_METRIC_SPECS:
        key = spec.key
        label = spec.label
        if key == "mlc_speed_acc":
            columns.extend(
                [
                    "MLCX1_Speed_0_4",
                    "MLCX1_Speed_4_8",
                    "MLCX1_Speed_8_12",
                    "MLCX1_Speed_12_16",
                    "MLCX1_Speed_16_20",
                    "MLCX1_Acc_0_40",
                    "MLCX1_Acc_40_80",
                    "MLCX1_Acc_80_120",
                    "MLCX1_Acc_120_160",
                    "MLCX1_Acc_160_200",
                    "MLCX1_Speed_Average",
                    "MLCX1_Acc_Average",
                    "MLCX1_Speed_Std",
                    "MLCX1_Acc_Std",
                    "MLCX2_Speed_0_4",
                    "MLCX2_Speed_4_8",
                    "MLCX2_Speed_8_12",
                    "MLCX2_Speed_12_16",
                    "MLCX2_Speed_16_20",
                    "MLCX2_Acc_0_40",
                    "MLCX2_Acc_40_80",
                    "MLCX2_Acc_80_120",
                    "MLCX2_Acc_120_160",
                    "MLCX2_Acc_160_200",
                    "MLCX2_Speed_Average",
                    "MLCX2_Acc_Average",
                    "MLCX2_Speed_Std",
                    "MLCX2_Acc_Std",
                ]
            )
        elif key.startswith("mi_"):
            columns.extend(
                [
                    f"{label}_MLCX1_MIs",
                    f"{label}_MLCX1_MIa",
                    f"{label}_MLCX1_MIt",
                    f"{label}_MLCX2_MIs",
                    f"{label}_MLCX2_MIa",
                    f"{label}_MLCX2_MIt",
                ]
            )
        elif key in VMAT_DUAL_MLC_KEYS:
            columns.extend([f"{label}_MLCX1", f"{label}_MLCX2"])
        else:
            columns.append(label)
    return columns


DUAL_MLC_CSV_HEADER = BASE_HEADER + _dual_metric_columns()


def build_standard_row(metadata, metrics):
    row = [
        metadata["patient_id"],
        metadata["patient_name"],
        metadata.get("plan_name", metadata.get("plan_label", "")),
        metadata["machine_id"],
        metadata["calculation_model"],
        metadata["prescribed_dose"],
        metadata["mu"],
    ]
    row.extend(_metric_values(metrics))
    return row


def build_dual_mlc_row(metadata, metrics):
    row = [
        metadata["patient_id"],
        metadata["patient_name"],
        metadata.get("plan_name", metadata.get("plan_label", "")),
        metadata["machine_id"],
        metadata["calculation_model"],
        metadata["prescribed_dose"],
        metadata["mu"],
    ]
    row.extend(_dual_metric_values(metrics))
    return row


def _metric_values(metrics):
    values = []
    for spec in VMAT_METRIC_SPECS:
        key = spec.key
        value = metrics.get(key, "")
        if key.startswith("mi_"):
            mis, mia, mit = value if value else ("", "", "")
            values.extend([mis, mia, mit])
        elif key == "mlc_speed_acc":
            speed, acceleration, summary = value if value else ([""] * 5, [""] * 5, [""] * 4)
            values.extend(
                [
                    speed[0],
                    speed[1],
                    speed[2],
                    speed[3],
                    speed[4],
                    acceleration[0],
                    acceleration[1],
                    acceleration[2],
                    acceleration[3],
                    acceleration[4],
                    summary[0],
                    summary[1],
                    summary[2],
                    summary[3],
                ]
            )
        elif key in VMAT_DUAL_MLC_KEYS:
            if isinstance(value, tuple):
                values.extend([value[0], value[1]])
            else:
                values.extend([value, value])
        else:
            values.append(value)
    return values


def _dual_metric_values(metrics):
    values = []
    for spec in VMAT_METRIC_SPECS:
        key = spec.key
        value = metrics.get(key, "")
        if key == "mlc_speed_acc":
            if value and len(value) == 6:
                speed1, acc1, summary1, speed2, acc2, summary2 = value
                values.extend(
                    [
                        speed1[0], speed1[1], speed1[2], speed1[3], speed1[4],
                        acc1[0], acc1[1], acc1[2], acc1[3], acc1[4],
                        summary1[0], summary1[1], summary1[2], summary1[3],
                        speed2[0], speed2[1], speed2[2], speed2[3], speed2[4],
                        acc2[0], acc2[1], acc2[2], acc2[3], acc2[4],
                        summary2[0], summary2[1], summary2[2], summary2[3],
                    ]
                )
            else:
                values.extend([""] * 28)
        elif key.startswith("mi_"):
            if value and len(value) == 2:
                mis1, mia1, mit1 = value[0]
                mis2, mia2, mit2 = value[1]
                values.extend([mis1, mia1, mit1, mis2, mia2, mit2])
            else:
                values.extend([""] * 6)
        elif key in VMAT_DUAL_MLC_KEYS:
            if isinstance(value, tuple):
                values.extend([value[0], value[1]])
            else:
                values.extend([value, value])
        else:
            values.append(value)
    return values
