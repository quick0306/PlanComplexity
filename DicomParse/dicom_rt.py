from typing import Dict

import numpy as np
import pydicom as dicom
from pydicom.valuerep import IS


class RTPlan:
    """Class that parses and returns formatted DICOM RT Plan data."""

    def __init__(self, filename: str) -> None:

        if filename:
            self.plan = dict()
            try:
                # Only pydicom 0.9.5 and above supports the force read argument
                if hasattr(dicom, "dcmread"):
                    self.ds = dicom.dcmread(filename, defer_size=100, force=True)
                else:
                    self.ds = dicom.read_file(filename, defer_size=100)
            except (EOFError, IOError):
                # Raise the error for the calling method to handle
                raise
            else:
                # Sometimes DICOM files may not have headers, but they should always
                # have a SOPClassUID to declare what type of file it is. If the
                # file doesn't have a SOPClassUID, then it probably isn't DICOM.
                if "SOPClassUID" not in self.ds:
                    raise AttributeError
        else:
            raise AttributeError

    def to_plan_dict(self) -> Dict[str, str]:
        """Returns the plan information."""
        self.plan["label"] = self.ds.RTPlanLabel

        # get plan id
        if "RTPlanName" in self.ds:
            self.plan["plan_name"] = self.ds.RTPlanName
        else:
            self.plan["plan_name"] = self.plan["label"]

        # get patient name
        if "PatientName" in self.ds:
            self.plan["patient_name"] = self.ds.PatientName
        else:
            self.plan["patient_name"] = ""

        # get patient id
        if "PatientID" in self.ds:
            self.plan["patient_id"] = self.ds.PatientID
        else:
            self.plan["patient_id"] = ""

        # get calculation model name
        if "ManufacturerModelName" in self.ds:
            self.plan["calculation_model"] = self.ds.ManufacturerModelName
        else:
            self.plan["calculation_model"] = ""

        self.plan["rxdose"] = 0.0
        if "DoseReferenceSequence" in self.ds:
            for item in self.ds.DoseReferenceSequence:
                if item.DoseReferenceStructureType == "SITE":
                    self.plan["name"] = "N/A"
                    if "DoseReferenceDescription" in item:
                        self.plan["name"] = item.DoseReferenceDescription
                    if "TargetPrescriptionDose" in item:
                        rxdose = item.TargetPrescriptionDose * 100
                        if rxdose > self.plan["rxdose"]:
                            self.plan["rxdose"] = rxdose
                elif item.DoseReferenceStructureType == "VOLUME":
                    if "TargetPrescriptionDose" in item:
                        self.plan["rxdose"] = item.TargetPrescriptionDose * 100
        if ("FractionGroupSequence" in self.ds) and (self.plan["rxdose"] == 0):
            fg = self.ds.FractionGroupSequence[0]
            if ("ReferencedBeamSequence" in fg) and ("NumberOfFractionsPlanned" in fg):
                beams = fg.ReferencedBeamSequence
                fx = fg.NumberOfFractionsPlanned
                for beam in beams:
                    if "BeamDose" in beam:
                        self.plan["rxdose"] += beam.BeamDose * fx * 100

        if "FractionGroupSequence" in self.ds:
            fg = self.ds.FractionGroupSequence[0]
            if "ReferencedBeamSequence" in fg:
                self.plan["fractions"] = fg.NumberOfFractionsPlanned
        self.plan["rxdose"] = int(self.plan["rxdose"])

        # referenced beams
        ref_beams = self.get_beams()
        self.plan["beams"] = ref_beams

        # Total number of MU
        total_mu = np.sum([ref_beams[b]["MU"] for b in ref_beams if "MU" in ref_beams[b]])
        self.plan["Plan_MU"] = round(total_mu, 2)

        tmp = self.get_study_info()
        self.plan["description"] = tmp["description"]

        # get treatment machine name
        for item in ref_beams:
            if "TreatmentMachineName" in ref_beams[item]:
                self.plan["machine_id"] = ref_beams[item]["TreatmentMachineName"]
            else:
                self.plan["machine_id"] = ""

        # get beam type
        for item in ref_beams:
            if "BeamType" in ref_beams[item]:
                self.plan["beam_type"] = ref_beams[item]["BeamType"]
            else:
                self.plan["beam_type"] = ""

        rotation_directions = []
        for item in ref_beams:
            direction = ref_beams[item].get("GantryRotationDirection", "")
            if direction and direction != "NONE" and direction not in rotation_directions:
                rotation_directions.append(direction)

        if len(rotation_directions) == 1:
            self.plan["rotation_direction"] = rotation_directions[0]
        elif len(rotation_directions) > 1:
            self.plan["rotation_direction"] = "MIXED"
        else:
            self.plan["rotation_direction"] = ""

        self.plan["beam_number"] = len(ref_beams)

        return self.plan

    def get_beams(self, fx: int = 0) -> Dict[IS, Dict[str, str]]:
        """Return the referenced beams from the specified fraction."""

        beams = {}
        if "BeamSequence" in self.ds:
            beam_sequence = self.ds.BeamSequence
        else:
            return beams
        # Obtain the beam information
        for beam_item in beam_sequence:
            if beam_item.TreatmentDeliveryType != 'SETUP':
                beam = dict()
                # Use the official pydicom keywords here. The older mixed-case spellings
                # trigger warnings and a slower keyword lookup path in recent pydicom.
                beam["Manufacturer"] = self._keyword_value(beam_item, "Manufacturer")
                beam["InstitutionName"] = self._keyword_value(beam_item, "InstitutionName")
                beam["TreatmentMachineName"] = self._keyword_value(beam_item, "TreatmentMachineName")
                beam["BeamName"] = self._keyword_value(beam_item, "BeamName")
                beam["SourceToSurfaceDistance"] = self._keyword_value(beam_item, "SourceToSurfaceDistance")
                beam["SourcetoSurfaceDistance"] = beam["SourceToSurfaceDistance"]
                beam["BeamDescription"] = self._keyword_value(beam_item, "BeamDescription")
                beam["BeamType"] = self._keyword_value(beam_item, "BeamType")
                beam["RadiationType"] = self._keyword_value(beam_item, "RadiationType")
                beam["ManufacturerModelName"] = self._keyword_value(beam_item, "ManufacturerModelName")
                beam["PrimaryDosimeterUnit"] = self._keyword_value(beam_item, "PrimaryDosimeterUnit")
                beam["NumberOfWedges"] = self._keyword_value(beam_item, "NumberOfWedges")
                beam["NumberOfCompensators"] = self._keyword_value(beam_item, "NumberOfCompensators")
                beam["NumberOfBoli"] = self._keyword_value(beam_item, "NumberOfBoli")
                beam["NumberOfBlocks"] = self._keyword_value(beam_item, "NumberOfBlocks")
                beam["NumberofWedges"] = beam["NumberOfWedges"]
                beam["NumberofCompensators"] = beam["NumberOfCompensators"]
                beam["NumberofBoli"] = beam["NumberOfBoli"]
                beam["NumberofBlocks"] = beam["NumberOfBlocks"]
                beam["FinalCumulativeMetersetWeight"] = self._keyword_value(beam_item, "FinalCumulativeMetersetWeight")
                beam["NumberOfControlPoints"] = self._keyword_value(beam_item, "NumberOfControlPoints")
                beam["NumberofControlPoints"] = beam["NumberOfControlPoints"]
                beam["TreatmentDeliveryType"] = self._keyword_value(beam_item, "TreatmentDeliveryType")

                # adding mlc info from BeamLimitingDeviceSequence
                beam_limits = beam_item.BeamLimitingDeviceSequence if "BeamLimitingDeviceSequence" in beam_item else ""
                beam["BeamLimitingDeviceSequence"] = beam_limits
                for beam_limit in beam_limits:
                    # MLCX1鍏?8瀵瑰彾鐗囷紝杩滅锛屽彾鐗囦綅缃甗-140,-130,-120,...,120,130,140]
                    if beam_limit.RTBeamLimitingDeviceType == "MLCX1":
                        beam["NumberOfMLCX1"] = beam_limit.NumberOfLeafJawPairs
                        beam["LeafPositionBoundariesOfMLCX1"] = beam_limit.LeafPositionBoundaries
                    # MLCX2鍏?9瀵瑰彾鐗囷紝杩戠锛屽彾鐗囦綅缃甗-145,135,-125,...,125,135,145]
                    if beam_limit.RTBeamLimitingDeviceType == "MLCX2":
                        beam["NumberOfMLCX2"] = beam_limit.NumberOfLeafJawPairs
                        beam["LeafPositionBoundariesOfMLCX2"] = beam_limit.LeafPositionBoundaries

                # Check control points if exists
                if "ControlPointSequence" in beam_item:
                    beam["ControlPointSequence"] = beam_item.ControlPointSequence
                    # control point 0
                    first_control_point = beam_item.ControlPointSequence[0]
                    # final control point
                    final_control_point = beam_item.ControlPointSequence[-1]

                    beam["NominalBeamEnergy"] = first_control_point.NominalBeamEnergy if "NominalBeamEnergy" in first_control_point else ""
                    beam["DoseRateSet"] = first_control_point.DoseRateSet if "DoseRateSet" in first_control_point else ""
                    beam["IsocenterPosition"] = first_control_point.IsocenterPosition if "IsocenterPosition" in first_control_point else ""
                    beam["GantryAngle"] = first_control_point.GantryAngle if "GantryAngle" in first_control_point else ""

                    # check VMAT delivery, but please attention Monaco TPS one beam multiple Arc,
                    # gantry direction will change, in this situation cp GantryRotationDirection equal "NONE"
                    beam["GantryRotationDirection"] = ""
                    beam["GantryRotationAngle"] = 0.0
                    if "GantryRotationDirection" in first_control_point:
                        if first_control_point.GantryRotationDirection != "NONE":
                            # VMAT Delivery
                            beam["GantryRotationDirection"] = first_control_point.GantryRotationDirection \
                                if "GantryRotationDirection" in first_control_point else ""

                            # last control point angle
                            beam["GantryFinalAngle"] = final_control_point.GantryAngle if "GantryAngle" in final_control_point else beam["GantryAngle"]
                            if "GantryRotationDirection" in final_control_point and final_control_point.GantryRotationDirection == "NONE":
                                beam["GantryFinalAngle"] = beam_item.ControlPointSequence[-1].GantryAngle \
                                    if "GantryAngle" in first_control_point else ""

                            if beam["GantryRotationDirection"] == "CW":
                                rotation_angle = ((beam["GantryFinalAngle"] - beam["GantryAngle"]) + 360) % 360
                                beam["GantryRotationAngle"] = rotation_angle
                            elif beam["GantryRotationDirection"] == "CC":
                                rotation_angle = (360 - (beam["GantryFinalAngle"] - beam["GantryAngle"])) % 360
                                beam["GantryRotationAngle"] = rotation_angle
                    elif len(beam_item.ControlPointSequence) > 1:
                        first_angle = float(first_control_point.GantryAngle) if "GantryAngle" in first_control_point else 0.0
                        last_angle = float(final_control_point.GantryAngle) if "GantryAngle" in final_control_point else first_angle
                        beam["GantryRotationAngle"] = abs((last_angle - first_angle + 360) % 360)

                    beam["BeamLimitingDeviceAngle"] = first_control_point.BeamLimitingDeviceAngle \
                        if "BeamLimitingDeviceAngle" in first_control_point else ""
                    beam["TableTopEccentricAngle"] = first_control_point.TableTopEccentricAngle \
                        if "TableTopEccentricAngle" in first_control_point else ""

                    # check beam limits
                    if "BeamLimitingDevicePositionSequence" in first_control_point:
                        for beam_limit in first_control_point.BeamLimitingDevicePositionSequence:
                            beam[beam_limit.RTBeamLimitingDeviceType] = beam_limit.LeafJawPositions

                # add each beam to beams dict
                beams[beam_item.BeamNumber] = beam

        # Obtain the referenced beam info from the fraction info
        if "FractionGroupSequence" in self.ds:
            fg = self.ds.FractionGroupSequence[fx]
            if "ReferencedBeamSequence" in fg:
                referenced_beams = fg.ReferencedBeamSequence
                number_of_fractions = fg.NumberOfFractionsPlanned
                for referenced_beam in referenced_beams:
                    if "BeamDose" in referenced_beam:
                        # dose in cGy
                        beams[referenced_beam.ReferencedBeamNumber]["dose"] = referenced_beam.BeamDose * number_of_fractions * 100
                    if 'BeamMeterset' in referenced_beam:
                        beams[referenced_beam.ReferencedBeamNumber]["MU"] = float(referenced_beam.BeamMeterset)
        return beams

    @staticmethod
    def _keyword_value(dataset, keyword: str, default=""):
        return getattr(dataset, keyword, default)

    def get_study_info(self) -> Dict[str, str]:
        """Return the study information of the current file."""

        study = {}
        if 'StudyDescription' in self.ds:
            desc = self.ds.StudyDescription
        else:
            desc = 'No description'
        study['description'] = desc
        # Don't assume that every dataset includes a study UID
        study['id'] = self.ds.SeriesInstanceUID
        if 'StudyInstanceUID' in self.ds:
            study['id'] = self.ds.StudyInstanceUID

        return study


