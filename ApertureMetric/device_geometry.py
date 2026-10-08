"""Select layer handling from DICOM device definitions, not TPS identity."""


def is_dual_layer_beam(beam):
    devices = {str(d.RTBeamLimitingDeviceType).upper()
               for d in beam.get("BeamLimitingDeviceSequence", [])}
    if devices:
        return {"MLCX1", "MLCX2"} <= devices
    # Preserve legacy callers which provide cached apertures without definitions.
    name = str(beam.get("TreatmentMachineName", "")).lower()
    return any(token in name for token in ("halcyon", "ethos"))


def is_dual_layer_plan(plan):
    beams = [b for b in plan.get("beams", {}).values()
             if b.get("TreatmentDeliveryType", "TREATMENT") == "TREATMENT"]
    if beams:
        layers = {is_dual_layer_beam(b) for b in beams}
        if len(layers) > 1:
            raise ValueError("Mixed single- and dual-layer treatment beams cannot be aggregated.")
        return layers.pop()
    return any(token in str(plan.get("machine_id", "")).lower()
               for token in ("halcyon", "ethos"))
