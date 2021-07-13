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
                if dicom.__version__ >= "0.9.5":
                    self.ds = dicom.read_file(filename, defer_size=100, force=True)
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

    def get_plan(self) -> Dict[str, str]:
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
            if ("ReferencedBeamSequence" in fg) and ("NumberofFractionsPlanned" in fg):
                beams = fg.ReferencedBeamSequence
                fx = fg.NumberofFractionsPlanned
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
        self.plan["Plan_MU"] = total_mu

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

        return self.plan

    def get_beams(self, fx: int = 0) -> Dict[IS, Dict[str, str]]:
        """Return the referenced beams from the specified fraction."""

        beams = {}
        if "BeamSequence" in self.ds:
            bdict = self.ds.BeamSequence
        else:
            return beams
        # Obtain the beam information
        for bi in bdict:
            if bi.TreatmentDeliveryType != 'SETUP':
                beam = dict()
                beam["Manufacturer"] = bi.Manufacturer if "Manufacturer" in bi else ""
                beam["InstitutionName"] = bi.InstitutionName if "InstitutionName" in bi else ""
                beam["TreatmentMachineName"] = bi.TreatmentMachineName if "TreatmentMachineName" in bi else ""
                beam["BeamName"] = bi.BeamName if "BeamName" in bi else ""
                beam["SourcetoSurfaceDistance"] = bi.SourcetoSurfaceDistance if "SourcetoSurfaceDistance" in bi else ""
                beam["BeamDescription"] = bi.BeamDescription if "BeamDescription" in bi else ""
                beam["BeamType"] = bi.BeamType if "BeamType" in bi else ""
                beam["RadiationType"] = bi.RadiationType if "RadiationType" in bi else ""
                beam["ManufacturerModelName"] = bi.ManufacturerModelName if "ManufacturerModelName" in bi else ""
                beam["PrimaryDosimeterUnit"] = bi.PrimaryDosimeterUnit if "PrimaryDosimeterUnit" in bi else ""
                beam["NumberofWedges"] = bi.NumberofWedges if "NumberofWedges" in bi else ""
                beam["NumberofCompensators"] = bi.NumberofCompensators if "NumberofCompensators" in bi else ""
                beam["NumberofBoli"] = bi.NumberofBoli if "NumberofBoli" in bi else ""
                beam["NumberofBlocks"] = bi.NumberofBlocks if "NumberofBlocks" in bi else ""
                ftemp = bi.FinalCumulativeMetersetWeight if "FinalCumulativeMetersetWeight" in bi else ""
                beam["FinalCumulativeMetersetWeight"] = ftemp
                beam["NumberofControlPoints"] = bi.NumberofControlPoints if "NumberofControlPoints" in bi else ""
                beam["TreatmentDeliveryType"] = bi.TreatmentDeliveryType if "TreatmentDeliveryType" in bi else ""

                # adding mlc info from BeamLimitingDeviceSequence
                beam_limits = bi.BeamLimitingDeviceSequence if "BeamLimitingDeviceSequence" in bi else ""
                beam["BeamLimitingDeviceSequence"] = beam_limits

                # Check control points if exists
                if "ControlPointSequence" in bi:
                    beam["ControlPointSequence"] = bi.ControlPointSequence
                    # control point 0
                    cp0 = bi.ControlPointSequence[0]
                    # final control point
                    final_cp = bi.ControlPointSequence[-1]

                    beam["NominalBeamEnergy"] = cp0.NominalBeamEnergy if "NominalBeamEnergy" in cp0 else ""
                    beam["DoseRateSet"] = cp0.DoseRateSet if "DoseRateSet" in cp0 else ""
                    beam["IsocenterPosition"] = cp0.IsocenterPosition if "IsocenterPosition" in cp0 else ""
                    beam["GantryAngle"] = cp0.GantryAngle if "GantryAngle" in cp0 else ""

                    # check VMAT delivery, but please attention Monaco TPS one beam multiple Arc,
                    # gantry direction will change, in this situation cp GantryRotationDirection equal "NONE"
                    if "GantryRotationDirection" in cp0:
                        if cp0.GantryRotationDirection != "NONE":
                            # VMAT Delivery
                            beam["GantryRotationDirection"] = cp0.GantryRotationDirection \
                                if "GantryRotationDirection" in cp0 else ""

                            # last control point angle
                            if final_cp.GantryRotationDirection == "NONE":
                                final_angle = bi.ControlPointSequence[-1].GantryAngle \
                                    if "GantryAngle" in cp0 else ""
                                beam["GantryFinalAngle"] = final_angle

                    btmp = cp0.BeamLimitingDeviceAngle if "BeamLimitingDeviceAngle" in cp0 else ""
                    beam["BeamLimitingDeviceAngle"] = btmp
                    beam["TableTopEccentricAngle"] = cp0.TableTopEccentricAngle if "TableTopEccentricAngle" in cp0 else ""

                    # check beam limits
                    if "BeamLimitingDevicePositionSequence" in cp0:
                        for bl in cp0.BeamLimitingDevicePositionSequence:
                            beam[bl.RTBeamLimitingDeviceType] = bl.LeafJawPositions

                # add each beam to beams dict
                beams[bi.BeamNumber] = beam

        # Obtain the referenced beam info from the fraction info
        if "FractionGroupSequence" in self.ds:
            fg = self.ds.FractionGroupSequence[fx]
            if "ReferencedBeamSequence" in fg:
                rb = fg.ReferencedBeamSequence
                nfx = fg.NumberOfFractionsPlanned
                for bi in rb:
                    if "BeamDose" in bi:
                        # dose in cGy
                        beams[bi.ReferencedBeamNumber]["dose"] = bi.BeamDose * nfx * 100
                    if 'BeamMeterset' in bi:
                        beams[bi.ReferencedBeamNumber]["MU"] = float(bi.BeamMeterset)
        return beams

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
