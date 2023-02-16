from ComplexityMetric.LeafTravel import LeafTravel
from DicomParse.dicomrt import RTPlan
from ComplexityMetric.LeafArea import LeafArea
from ComplexityMetric.ModulationComplexityScore import ModulationComplexityScore
from ComplexityMetric.LeafGap import LeafGap

if __name__ == '__main__':
    pfile = r"C:\Users\Administrator\Desktop\PlanComplexity\data\RP.719072.ST-SRS.dcm"

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
    beam_number = plan_dict["beam_number"]

    print("ID: ", patient_id, ", Name: ", patient_name, ", PlanID: ", plan_id, ", MachineID: ", machine_id,
          ", Calculation_Model: ", calculation_model, ", Prescribed_Dose: ", prescribed_dose, ", MU: ", mu,
          ", Beam_Type: ", beam_type, ", Beam_Number: ", beam_number)

    leaf_area_obj = LeafArea()
    leaf_area = leaf_area_obj.CalculateForPlan(plan_dict)
    print("Mean Leaf Area (MLA): ", leaf_area)

    modulation_complexity_score_obj = ModulationComplexityScore()
    modulation_complexity_score = modulation_complexity_score_obj.CalculateForPlan(plan_dict)
    print("Modulation Complexity Score (MCS): ", modulation_complexity_score)

    leaf_gap_obj = LeafGap()
    leaf_gap_average, leaf_gap_std = leaf_gap_obj.CalculateForPlan(plan_dict)
    print("Leaf Gap Average: ", leaf_gap_average)
    print("Leaf Gap Std: ", leaf_gap_std)
