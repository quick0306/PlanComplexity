from __future__ import annotations

import json
import sys
from pathlib import Path

import pydicom


def describe_value(value):
    if value is None:
        return {"type": "NoneType", "repr": "None"}
    if isinstance(value, bytes):
        preview = value[:80].decode("ascii", errors="ignore")
        return {"type": "bytes", "len": len(value), "preview": preview}
    try:
        length = len(value)
    except TypeError:
        length = None
    preview = None
    if length:
        try:
            preview = list(value[:8])
        except Exception:
            preview = repr(value)[:120]
    return {"type": type(value).__name__, "len": length, "preview": preview}


def main(path: str) -> None:
    ds = pydicom.dcmread(path, force=True)
    beam = next(beam for beam in ds.BeamSequence if getattr(beam, "TreatmentDeliveryType", "").upper() != "SETUP")
    cps = list(getattr(beam, "ControlPointSequence", []))

    report = {
        "path": path,
        "machine": getattr(beam, "TreatmentMachineName", ""),
        "beam_types": [getattr(item, "RTBeamLimitingDeviceType", "") for item in getattr(beam, "BeamLimitingDeviceSequence", [])],
        "cp_count": len(cps),
        "private_tag_populated_counts": {},
        "first_control_points": [],
    }

    interesting_tags = [
        "TomotherapeuticLeafOpenDurations",
        "LeafJawPositions",
        "TableTopLongitudinalPosition",
        "GantryAngle",
        "SourceRollAngle",
    ]
    private_tags = [(0x300D, 0x10A7)]

    for index, cp in enumerate(cps[:5]):
        entry = {"index": index, "keywords": {}, "private": {}}
        for keyword in interesting_tags:
            if hasattr(cp, keyword):
                entry["keywords"][keyword] = describe_value(getattr(cp, keyword))
        for tag in private_tags:
            if tag in cp:
                element = cp[tag]
                entry["private"][str(tag)] = {
                    "vr": element.VR,
                    "value": describe_value(element.value),
                }
        report["first_control_points"].append(entry)

    tag_counts = {}
    for cp in cps:
        for element in cp:
            if element.tag.is_private:
                key = str((element.tag.group, element.tag.elem))
                bucket = tag_counts.setdefault(key, {"present": 0, "non_null": 0, "vr": element.VR})
                bucket["present"] += 1
                if element.value is not None:
                    bucket["non_null"] += 1
    report["private_tag_populated_counts"] = tag_counts

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
