from __future__ import annotations

import sys
from collections import defaultdict

import pydicom


def printable(value, limit: int = 160) -> str:
    text = repr(value)
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: inspect_rtplan_private_tags.py <rtplan.dcm>")
        return 2

    path = sys.argv[1]
    ds = pydicom.dcmread(path, force=True, stop_before_pixels=True)

    print("File:", path)
    print("RTPlanLabel:", getattr(ds, "RTPlanLabel", ""))
    print("RTPlanName:", getattr(ds, "RTPlanName", ""))
    print("Manufacturer:", getattr(ds, "Manufacturer", ""))
    print("ManufacturerModelName:", getattr(ds, "ManufacturerModelName", ""))
    print("SoftwareVersions:", getattr(ds, "SoftwareVersions", ""))

    print("\n=== Top-level private creators ===")
    private_creators = set()
    for element in ds.iterall():
        tag = element.tag
        if tag.is_private and tag.element < 0x0100 and element.VR in {"LO", "SH", "CS", "UT", "ST"}:
            private_creators.add((str(tag), printable(element.value)))
    for tag_text, value in sorted(private_creators)[:80]:
        print(tag_text, value)

    print("\n=== Top-level private data elements ===")
    top_private = []
    for element in ds.iterall():
        tag = element.tag
        if tag.is_private and tag.element >= 0x1000:
            top_private.append(
                (
                    str(tag),
                    element.VR,
                    printable(element.value),
                )
            )
    for tag_text, vr, value in top_private[:200]:
        print(tag_text, vr, value)

    print("\n=== Beam summary ===")
    for beam_index, beam in enumerate(getattr(ds, "BeamSequence", []), start=1):
        print(f"\n--- Beam {beam_index} ---")
        print("BeamName:", getattr(beam, "BeamName", ""))
        print("BeamDescription:", getattr(beam, "BeamDescription", ""))
        print("TreatmentMachineName:", getattr(beam, "TreatmentMachineName", ""))
        print("BeamType:", getattr(beam, "BeamType", ""))
        print("TreatmentDeliveryType:", getattr(beam, "TreatmentDeliveryType", ""))
        print("RadiationType:", getattr(beam, "RadiationType", ""))
        print("ControlPointCount:", len(getattr(beam, "ControlPointSequence", [])))

        print("BeamLimitingDeviceSequence:")
        for device in getattr(beam, "BeamLimitingDeviceSequence", []):
            boundaries = getattr(device, "LeafPositionBoundaries", None)
            boundary_count = len(boundaries) if boundaries is not None else 0
            print(
                " ",
                getattr(device, "RTBeamLimitingDeviceType", ""),
                "pairs=",
                getattr(device, "NumberOfLeafJawPairs", ""),
                "boundaries=",
                boundary_count,
            )

        beam_private = []
        for element in beam.iterall():
            tag = element.tag
            if tag.is_private:
                beam_private.append((str(tag), element.VR, printable(element.value)))
        if beam_private:
            print("Private elements in beam:")
            for tag_text, vr, value in beam_private[:80]:
                print(" ", tag_text, vr, value)

        control_points = getattr(beam, "ControlPointSequence", [])
        if control_points:
            interesting = [
                "GantryAngle",
                "GantryRotationDirection",
                "BeamLimitingDeviceAngle",
                "PatientSupportAngle",
                "TableTopEccentricAngle",
                "TableTopVerticalPosition",
                "TableTopLongitudinalPosition",
                "TableTopLateralPosition",
                "CumulativeMetersetWeight",
                "DoseRateSet",
                "IsocenterPosition",
            ]
            print("CP0 standard fields:")
            cp0 = control_points[0]
            for field in interesting:
                if hasattr(cp0, field):
                    print(" ", field, printable(getattr(cp0, field)))

            sample_indices = [0, len(control_points) // 2, len(control_points) - 1]
            print("Selected control point trajectory samples:")
            for idx in sample_indices:
                cp = control_points[idx]
                private_map = {
                    str(element.tag): printable(element.value)
                    for element in cp
                    if element.tag.is_private
                }
                summary = {
                    "idx": idx,
                    "gantry": printable(getattr(cp, "GantryAngle", "")),
                    "cmw": printable(getattr(cp, "CumulativeMetersetWeight", "")),
                    "iso": printable(getattr(cp, "IsocenterPosition", "")),
                    "tt_long": printable(getattr(cp, "TableTopLongitudinalPosition", "")),
                    "priv_4001_1004": private_map.get("(4001,1004)", ""),
                    "priv_4001_1005": private_map.get("(4001,1005)", ""),
                }
                print(" ", summary)

            cp_private_counts = defaultdict(int)
            cp_private_examples = {}
            for cp in control_points:
                for element in cp.iterall():
                    if element.tag.is_private:
                        key = (str(element.tag), element.VR)
                        cp_private_counts[key] += 1
                        cp_private_examples.setdefault(key, printable(element.value))

            if cp_private_counts:
                print("Control point private elements:")
                for (tag_text, vr), count in sorted(cp_private_counts.items())[:120]:
                    print(" ", tag_text, vr, "count=", count, "example=", cp_private_examples[(tag_text, vr)])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
