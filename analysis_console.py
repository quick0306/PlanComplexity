from metric_registry import metric_gui_labels_with_aliases, metric_labels_with_aliases


METRIC_LABELS = metric_labels_with_aliases()
METRIC_GUI_LABELS = metric_gui_labels_with_aliases()


def log_plan_summary(logger, metadata):
    logger.info(
        "ID: %s, Name: %s, PlanID: %s, MachineID: %s, Calculation_Model: %s, Prescribed_Dose: %s, MU: %s, Beam_Type: %s, Beam_Number: %s, Rotation_Direction: %s",
        metadata["patient_id"],
        metadata["patient_name"],
        metadata["plan_name"],
        metadata["machine_id"],
        metadata["calculation_model"],
        metadata["prescribed_dose"],
        metadata["mu"],
        metadata["beam_type"],
        metadata["beam_number"],
        metadata["rotation_direction"] or "N/A",
    )


def log_batch_plan_summary(logger, metadata):
    logger.info(
        "ID: %s, Name: %s, PlanID: %s, MachineID: %s, Calculation_Model: %s, Prescribed_Dose: %s, MU: %s, Beam_Type: %s, Rotation_Direction: %s",
        metadata["patient_id"],
        metadata["patient_name"],
        metadata["plan_name"],
        metadata["machine_id"],
        metadata["calculation_model"],
        metadata["prescribed_dose"],
        metadata["mu"],
        metadata["beam_type"],
        metadata["rotation_direction"] or "N/A",
    )


def log_metric_summary(logger, metrics):
    for key, value in metrics.items():
        label = METRIC_GUI_LABELS.get(key, METRIC_LABELS.get(key, key))
        logger.info("%s: %s", label, value)
