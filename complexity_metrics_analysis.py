import csv
import os
from DicomParse.utilities import retrieve_dcm_filenames
from DicomParse.dicomrt import RTPlan
from ComplexityMetric.EdgeMetric import EdgeMetric
from ComplexityMetric.ApertureAreaRatioJawArea import ApertureAreaRatioJawArea
from ComplexityMetric.ApertureSubRegions import ApertureSubRegions
from ComplexityMetric.ApertureYJaw import ApertureYJaw
from ComplexityMetric.ApertureXJaw import ApertureXJaw
from ComplexityMetric.ConvertedApertureMetric import ConvertedApertureMetric
from ComplexityMetric.EdgeAreaMetric import EdgeAreaMetric
from ComplexityMetric.LeafTravel import LeafTravel
from ComplexityMetric.LeafGap import LeafGap
from ComplexityMetric.LeafArea import LeafArea
from ComplexityMetric.MeanFieldArea import  MeanFieldArea
from ComplexityMetric.MeanAsymmetryDistance import MeanAsymmetryDistance
from ComplexityMetric.ModulationComplexityScore import ModulationComplexityScore
from ComplexityMetric.PlanModulation import PlanModulation
from ComplexityMetric.PlanIrregularity import PlanIrregularity
from ComplexityMetric.ProportionMLCSpeedAcceleration import ProportionMLCSpeedAcceleration
from ComplexityMetric.SmallApertureScore import SmallApertureScore
from ComplexityMetric.StationParameterOptimizedRadiationTherapy import StationParameterOptimizedRadiationTherapy


if __name__ == '__main__':
    pdir = r"D:\RT_Plan\Axesse"
    filepaths = retrieve_dcm_filenames(pdir, recursive=True)

    imrt_path = r".\axesse_complexity_analysis1.csv"
    with open(imrt_path, 'w') as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')

        row = ['ID', 'Name', 'PlanID', 'MachineID', 'Calculation_Model', 'Prescribed_Dose', 'MU', 'EDGE_Metric',
               'Leaf_Area', 'Plan_Irregularity', 'Plan_Modulation', 'Modulation_Complexity_Score', 'Small_Aperture_Score_5mm',
               'Small_Aperture_Score_10mm', 'Small_Aperture_Score_20mm', 'Mean_Field_Area', 'Mean_Asymmetry_Distance',
               'Aperture_Area_Ration_Jaw_Area', 'Aperture_Sub_Regions', 'Aperture_X_Jaw_Distance', 'Aperture_Y_Jaw_Distance',
               'Leaf_Gap_Average', ' Leaf_Gap_Std', 'Leaf_Travel', 'Converted_Aperture_Metric', 'Edge_Area_Metric']

        writer.writerow(row)

        for pfile in filepaths:
            print(pfile)
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
            print("ID: ", patient_id, ", Name: ", patient_name, ", PlanID: ", plan_id, ", MachineID: ", machine_id,
                  ", Calculation_Model: ", calculation_model, ", Prescribed_Dose: ", prescribed_dose, ", MU: ", mu)

            matches = ["DMLC", "IMRT", "VMAT"]
            if any(x in plan_id for x in matches):
                edge_metric_obj = EdgeMetric()
                edge_metric = edge_metric_obj.CalculateForPlan(plan_dict)
                print("Edge Metric (EM): ", edge_metric)

                leaf_area_obj = LeafArea()
                leaf_area = leaf_area_obj.CalculateForPlan(plan_dict)
                print("Mean Leaf Area (MLA): ", leaf_area)

                plan_irregularity_obj = PlanIrregularity()
                plan_irregularity = plan_irregularity_obj.CalculateForPlan(plan_dict)
                print("Plan Irregularity (PI): ", plan_irregularity)

                plan_modulation_obj = PlanModulation()
                plan_modulation = plan_modulation_obj.CalculateForPlan(plan_dict)
                print("Plan Modulation (PM): ", plan_modulation)

                modulation_complexity_score_obj = ModulationComplexityScore()
                modulation_complexity_score = modulation_complexity_score_obj.CalculateForPlan(plan_dict)
                print("Modulation Complexity Score (MCS): ", modulation_complexity_score)

                small_aperture_score_obj = SmallApertureScore()
                small_aperture_score_5mm = small_aperture_score_obj.CalculateForPlan(plan_dict, x=5)
                small_aperture_score_10mm = small_aperture_score_obj.CalculateForPlan(plan_dict, x=10)
                small_aperture_score_20mm = small_aperture_score_obj.CalculateForPlan(plan_dict, x=20)
                print("Small Aperture Score 5 mm: ", small_aperture_score_5mm)
                print("Small Aperture Score 10 mm: ", small_aperture_score_10mm)
                print("Small Aperture Score 20 mm: ", small_aperture_score_20mm)

                mean_field_area_obj = MeanFieldArea()
                mean_field_area = mean_field_area_obj.CalculateForPlan(plan_dict)
                print("Mean Field Area: ", mean_field_area)

                mean_asymmetry_distance_obj = MeanAsymmetryDistance()
                mean_asymmetry_distance = mean_asymmetry_distance_obj.CalculateForPlan(plan_dict)
                print("Mean Asymmetry Distance: ", mean_asymmetry_distance)

                aperture_ratio_jaw_area_obj = ApertureAreaRatioJawArea()
                aperture_ratio_jaw_area = aperture_ratio_jaw_area_obj.CalculateForPlan(plan_dict)
                print("Aperture Area Ratio Jaw Area: ", aperture_ratio_jaw_area)

                aperture_sub_regions_obj = ApertureSubRegions()
                aperture_sub_regions = aperture_sub_regions_obj.CalculateForPlan(plan_dict)
                print("Aperture Sub Regions: ", aperture_sub_regions)

                aperture_x_jaw_obj = ApertureXJaw()
                aperture_x_jaw_distance = aperture_x_jaw_obj.CalculateForPlan(plan_dict)
                print("Aperture X Jaw: ", aperture_x_jaw_distance)
                aperture_y_jaw_obj = ApertureYJaw()
                aperture_y_jaw_distance = aperture_y_jaw_obj.CalculateForPlan(plan_dict)
                print("Aperture Y Jaw: ", aperture_y_jaw_distance)

                leaf_gap_obj = LeafGap()
                leaf_gap_average, leaf_gap_std = leaf_gap_obj.CalculateForPlan(plan_dict)
                print("Leaf Gap Average: ", leaf_gap_average)
                print("Leaf Gap Std: ", leaf_gap_std)

                leaf_travel_obj = LeafTravel()
                leaf_travel = leaf_travel_obj.CalculateForPlan(plan_dict)
                print("Leaf Travel: ", leaf_travel)

                cam_obj = ConvertedApertureMetric()
                cam = cam_obj.CalculateForPlan(plan_dict)
                print("Converted Aperture Metric (CAM): ", cam)

                eam_obj = EdgeAreaMetric()
                eam = eam_obj.CalculateForPlan(plan_dict)
                print("Edge Area Metric (EAM): ", eam)

                info = [patient_id, patient_name, plan_id, machine_id, calculation_model, prescribed_dose, mu,
                        edge_metric, leaf_area, plan_irregularity, plan_modulation, modulation_complexity_score,
                        small_aperture_score_5mm, small_aperture_score_10mm, small_aperture_score_20mm, mean_field_area,
                        mean_asymmetry_distance, aperture_ratio_jaw_area, aperture_sub_regions, aperture_x_jaw_distance,
                        aperture_y_jaw_distance, leaf_gap_average, leaf_gap_std, leaf_travel, cam, eam]

                print(info)
                writer.writerow(info)

            else:
                os.remove(pfile)
