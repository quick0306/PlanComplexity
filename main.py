from ComplexityMetric.LeafTravel import LeafTravel
from DicomParse.dicomrt import RTPlan


if __name__ == '__main__':
    pfile = r"D:\RT_Plan\Axesse\Monaco\1910280C_C5DMLCa-QA1.dcm"
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

    leaf_travel_obj = LeafTravel()
    leaf_travel = leaf_travel_obj.CalculateForPlan(plan_dict)
    print("Leaf Travel: ", leaf_travel)
