import pydicom as dicom

from DicomParse.utilities import retrieve_dcm_filenames
from DicomParse.dicomrt import RTPlan


if __name__ == '__main__':
    pdir = r"D:\RT_Plan\Trilogy"
    filepaths = retrieve_dcm_filenames(pdir, recursive=True)

    for pfile in filepaths:
        ds = dicom.read_file(pfile, defer_size=100, force=True)

        plan_info = RTPlan(filename=pfile)
        plan_dict = plan_info.get_plan()

        # calculation plan complexity metric
        patient_id = plan_dict["patient_id"]
        patient_name = plan_dict["patient_name"]
        plan_id = plan_dict["plan_name"]
        machine_id = plan_info.ds.BeamSequence[0].TreatmentMachineName
        calculation_model = plan_dict["calculation_model"]
        prescribed_dose = plan_dict["rxdose"]
        mu = plan_dict["Plan_MU"]
        beam_type = plan_dict["beam_type"]
        print("ID: ", patient_id, ", Name: ", patient_name, ", PlanID: ", plan_id, ", MachineID: ", machine_id,
              ", Calculation_Model: ", calculation_model, ", Prescribed_Dose: ", prescribed_dose, ", MU: ", mu,
              ", Beam_Type: ", beam_type)



