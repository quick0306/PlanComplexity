import unittest
from types import SimpleNamespace
from unittest.mock import patch

import analysis_helpers
import main
from aurora_svmat_lab.models import AuroraAnalysisResult, AuroraPlanMetadata
from analysis_exports import build_dual_mlc_row, build_standard_row
from ucomx_models import AnalysisMode, PlanAnalysisResult
import ucomx_service
from ucomx_service import analyze_filepaths, build_export_record, build_metric_reference_rows, build_metric_rows, detect_mode
from tests.test_aurora_parser import build_fake_aurora_rtplan


class FakeMetric:
    def __init__(self, result):
        self.result = result

    def calculate_for_plan(self, plan_dict, **kwargs):
        return self.result


class FakeSmallApertureScore:
    def calculate_for_plan(self, plan_dict, x):
        return f"sas-{x}"


class FakeModulationIndexScore:
    def calculate_for_plan(self, plan_dict, k):
        return (f"mis-{k}", f"mia-{k}", f"mit-{k}")


def fake_supplemental_metrics(_plan_dict):
    return {
        "mus": 325.4,
        "pmu": 325.4,
        "muca": 10.0,
        "fractions_count": 25,
        "fraction_dose_gy": 2.0,
        "mucgy": 1.63,
        "lt": "lt-table",
        "ltmu": 0.31,
        "ltnlmu": 0.12,
        "nl": 30.0,
        "ltnl": 5.0,
        "al": 180.0,
        "lna": 0.02,
        "cal": 2.0,
        "gt": 360.0,
        "mudeg": 0.9,
        "ltal": 1.5,
        "narcs": 2,
        "mdrv": 0.1,
        "mgsv": 0.2,
        "dr": 300.0,
        "gs": 4.0,
        "ls": 8.0,
        "aav": 0.8,
        "lsv": 0.7,
        "tg": 1.1,
        "dt": 90.0,
        "md": 1.25,
        "pa": 100.0,
        "ja": 144.0,
        "efs": 20.0,
        "psmall": 0.3,
        "perimeter": 40.0,
    }


class AnalysisHelpersTests(unittest.TestCase):
    def test_get_plan_metadata_collects_expected_fields(self):
        plan_info = SimpleNamespace(ds=SimpleNamespace(BeamSequence=[SimpleNamespace(TreatmentMachineName="TB-1")]))
        plan_dict = {
            "patient_id": "P001",
            "patient_name": "Alice",
            "plan_name": "Plan A",
            "label": "PLAN_A",
            "calculation_model": "AAA",
            "rxdose": 6000,
            "Plan_MU": 325.4,
            "beam_type": "DYNAMIC",
            "beam_number": 2,
            "rotation_direction": "CW",
        }

        metadata = analysis_helpers.get_plan_metadata(plan_info, plan_dict)

        self.assertEqual(metadata["machine_id"], "TB-1")
        self.assertEqual(metadata["plan_label"], "PLAN_A")
        self.assertEqual(metadata["rotation_direction"], "CW")
        self.assertEqual(metadata["beam_number"], 2)

    @patch.object(analysis_helpers, "EdgeMetric", return_value=FakeMetric("edge"))
    @patch.object(analysis_helpers, "PlanIrregularity", return_value=FakeMetric("pi"))
    @patch.object(analysis_helpers, "PlanModulation", return_value=FakeMetric("pm"))
    @patch.object(analysis_helpers, "ModulationComplexityScore", return_value=FakeMetric("mcs"))
    @patch.object(analysis_helpers, "SmallApertureScore", return_value=FakeSmallApertureScore())
    @patch.object(analysis_helpers, "MeanFieldArea", return_value=FakeMetric("mfa"))
    @patch.object(analysis_helpers, "MeanAsymmetryDistance", return_value=FakeMetric("mad"))
    @patch.object(analysis_helpers, "ApertureAreaRatioJawArea", return_value=FakeMetric("aarja"))
    @patch.object(analysis_helpers, "ApertureSubRegions", return_value=FakeMetric("asr"))
    @patch.object(analysis_helpers, "ApertureXJaw", return_value=FakeMetric("axj"))
    @patch.object(analysis_helpers, "ApertureYJaw", return_value=FakeMetric("ayj"))
    @patch.object(analysis_helpers, "LeafGap", return_value=FakeMetric((4.0, 0.8)))
    @patch.object(analysis_helpers, "ConvertedApertureMetric", return_value=FakeMetric("cam"))
    @patch.object(analysis_helpers, "EdgeAreaMetric", return_value=FakeMetric("eam"))
    @patch.object(analysis_helpers, "StationParameterOptimizedRadiationTherapy", return_value=FakeMetric("sport"))
    @patch.object(analysis_helpers, "ProportionMLCSpeedAcceleration", return_value=FakeMetric(([1, 2, 3, 4, 5], [7, 8, 9, 10, 11], [11, 12, 13, 14])))
    @patch.object(analysis_helpers, "ModulationIndexScore", return_value=FakeModulationIndexScore())
    @patch.object(analysis_helpers, "calculate_vcomx_supplemental_metrics", side_effect=fake_supplemental_metrics)
    def test_calculate_core_metrics_returns_stable_structure(self, *_mocks):
        metrics = analysis_helpers.calculate_core_metrics({"beams": {}})

        self.assertEqual(metrics["em"], "edge")
        self.assertEqual(metrics["sas_5mm"], "sas-5")
        self.assertEqual(metrics["sas_10mm"], "sas-10")
        self.assertEqual(metrics["sas_20mm"], "sas-20")
        self.assertEqual(metrics["alg"], 4.0)
        self.assertEqual(metrics["alg_sd"], 0.8)
        self.assertEqual(metrics["mlc_speed_acc"][2], [11, 12, 13, 14])
        self.assertEqual(metrics["mi_2_0"], ("mis-2.0", "mia-2.0", "mit-2.0"))
        self.assertEqual(metrics["mus"], 325.4)
        self.assertEqual(metrics["aav"], 0.8)
        self.assertEqual(metrics["perimeter"], 40.0)

    @patch.object(analysis_helpers, "EdgeMetric", return_value=FakeMetric("edge"))
    @patch.object(analysis_helpers, "PlanIrregularity", return_value=FakeMetric("pi"))
    @patch.object(analysis_helpers, "PlanModulation", return_value=FakeMetric("pm"))
    @patch.object(analysis_helpers, "ModulationComplexityScore", return_value=FakeMetric("mcs"))
    @patch.object(analysis_helpers, "SmallApertureScore", return_value=FakeSmallApertureScore())
    @patch.object(analysis_helpers, "LeafGap", return_value=FakeMetric((4.0, 0.8)))
    def test_calculate_cyberknife_metrics_returns_six_paper_metrics(self, *_mocks):
        metrics = analysis_helpers.calculate_cyberknife_mlc_metrics({"beams": {}})

        self.assertEqual(
            metrics,
            {
                "mcs": "mcs",
                "em": "edge",
                "pi": "pi",
                "pm": "pm",
                "lg": 4.0,
                "sas10": "sas-10",
            },
        )

    def test_build_standard_row_keeps_export_order(self):
        metadata = {
            "patient_id": "P001",
            "patient_name": "Alice",
            "plan_name": "Plan A",
            "machine_id": "TB-1",
            "calculation_model": "AAA",
            "prescribed_dose": 6000,
            "mu": 325.4,
        }
        metrics = {
            "mus": 325.4,
            "pmu": 325.4,
            "muca": 12.0,
            "fraction_dose_gy": 2.0,
            "fractions_count": 25,
            "mucgy": 1.5,
            "lt": "lt",
            "ltmu": 0.2,
            "ltnlmu": 0.1,
            "nl": 40.0,
            "ltnl": 5.0,
            "al": 180.0,
            "lna": 0.03,
            "cal": 3.2,
            "gt": 360.0,
            "mudeg": 0.9,
            "ltal": 1.8,
            "narcs": 2,
            "mdrv": 0.1,
            "mgsv": 0.2,
            "dr": 300.0,
            "gs": 4.0,
            "ls": 8.0,
            "mcsv": "mcs",
            "aav": 0.7,
            "lsv": 0.8,
            "tg": 1.2,
            "mi_2_0": ("mis20", "mia20", "mit20"),
            "mi_1_0": ("mis10", "mia10", "mit10"),
            "mi_0_5": ("mis05", "mia05", "mit05"),
            "mi_0_2": ("mis02", "mia02", "mit02"),
            "dt": 90.0,
            "pi": "pi",
            "pm": "pm",
            "md": 1.1,
            "pa": "mfa",
            "efs": 25.0,
            "psmall": 0.4,
            "sas_5mm": "sas-5",
            "sas_10mm": "sas-10",
            "sas_20mm": "sas-20",
            "em": "edge",
            "bjar": "aarja",
            "mad": "mad",
            "alg": 4.0,
            "alg_sd": 0.8,
            "perimeter": 42.0,
            "asr": "asr",
            "axjd": "axj",
            "ayjd": "ayj",
            "cam": "cam",
            "eam": "eam",
            "mlc_speed_acc": ([1, 2, 3, 4, 5], [7, 8, 9, 10, 11], [11, 12, 13, 14]),
            "sport": "sport",
        }

        row = build_standard_row(metadata, metrics)

        self.assertEqual(row[:7], ["P001", "Alice", "Plan A", "TB-1", "AAA", 6000, 325.4])
        self.assertEqual(row[-1], "sport")
        self.assertGreater(len(row), 53)

    def test_build_dual_mlc_row_keeps_dual_machine_fields(self):
        metadata = {
            "patient_id": "P001",
            "patient_name": "Alice",
            "plan_label": "PLAN_A",
            "machine_id": "HALCYON",
            "calculation_model": "AXB",
            "prescribed_dose": 5000,
            "mu": 210.0,
        }
        metrics = {
            "mus": 210.0,
            "pmu": 84.0,
            "muca": 4.0,
            "fraction_dose_gy": 2.0,
            "fractions_count": 25,
            "mucgy": 2.1,
            "lt": (1, 2),
            "ltmu": (3, 4),
            "ltnlmu": (5, 6),
            "nl": (7, 8),
            "ltnl": (9, 10),
            "al": 180.0,
            "lna": (11, 12),
            "cal": 3.0,
            "gt": 360.0,
            "mudeg": 1.0,
            "ltal": (13, 14),
            "narcs": 2,
            "mdrv": (15, 16),
            "mgsv": (17, 18),
            "dr": (19, 20),
            "gs": (21, 22),
            "ls": (23, 24),
            "mcsv": (25, 26),
            "aav": (27, 28),
            "lsv": (29, 30),
            "tg": (31, 32),
            "mi_2_0": ((33, 34, 35), (36, 37, 38)),
            "mi_1_0": ((39, 40, 41), (42, 43, 44)),
            "mi_0_5": ((45, 46, 47), (48, 49, 50)),
            "mi_0_2": ((51, 52, 53), (54, 55, 56)),
            "dt": (57, 58),
            "pi": (59, 60),
            "pm": (61, 62),
            "md": (63, 64),
            "pa": (65, 66),
            "efs": (67, 68),
            "psmall": (69, 70),
            "sas_5mm": (71, 72),
            "sas_10mm": (73, 74),
            "sas_20mm": (75, 76),
            "em": (77, 78),
            "bjar": 79,
            "mad": (80, 81),
            "alg": (82, 83),
            "alg_sd": (84, 85),
            "perimeter": (86, 87),
            "asr": (88, 89),
            "axjd": 90,
            "ayjd": 91,
            "cam": (92, 93),
            "eam": (94, 95),
            "mlc_speed_acc": ([1, 2, 3, 4, 5], [7, 8, 9, 10, 11], [11, 12, 13, 14]),
            "sport": "sport",
        }

        row = build_dual_mlc_row(metadata, metrics)

        self.assertEqual(row[:7], ["P001", "Alice", "PLAN_A", "HALCYON", "AXB", 5000, 210.0])
        self.assertGreater(len(row), 37)

    def test_metric_rows_use_paper_labels_for_park_and_sport(self):
        result = PlanAnalysisResult(
            source_path="plan.dcm",
            mode=AnalysisMode.VMAT_IMRT,
            metadata={},
            metrics={},
            flattened_metrics={"speed_0_4": 0.2, "sport": 1.5},
            supported=True,
            warnings=[],
        )

        metric_rows = build_metric_rows(result)
        reference_rows = build_metric_reference_rows(result)

        self.assertEqual(metric_rows[0][0], "Park Speed 0-4 mm/s")
        self.assertEqual(metric_rows[1][0], "SPORT Modulation Index (Li and Xing 2013)")
        self.assertIn("Leaf-wise mean proportion", reference_rows[0][1])
        self.assertIn("beam/plan aggregate summary", reference_rows[1][1])

    def test_metric_rows_use_cyberknife_labels(self):
        result = PlanAnalysisResult(
            source_path="plan.dcm",
            mode=AnalysisMode.CYBERKNIFE_MLC,
            metadata={},
            metrics={},
            flattened_metrics={"mcs": 0.7, "lg": 5.5, "sas10": 0.2},
            supported=True,
            warnings=[],
        )

        metric_rows = build_metric_rows(result)
        self.assertEqual(metric_rows[0][0], "MCS (CyberKnife MLC)")
        self.assertEqual(metric_rows[1][0], "LG (Mean Leaf Gap)")
        self.assertEqual(metric_rows[2][0], "SAS10 (CyberKnife)")

    def test_metric_reference_rows_include_vmat_and_mi_notes(self):
        result = PlanAnalysisResult(
            source_path="plan.dcm",
            mode=AnalysisMode.VMAT_IMRT,
            metadata={},
            metrics={},
            flattened_metrics={"em": 0.4, "alg": 5.0, "mi_0_5_mit": 0.3},
            supported=True,
            warnings=[],
        )

        reference_rows = build_metric_reference_rows(result)
        notes_by_label = {label: note for label, note in reference_rows}

        self.assertIn("EM", notes_by_label)
        self.assertIn("aperture edge", notes_by_label["EM"])
        self.assertIn("ALG", notes_by_label)
        self.assertIn("opposing leaf pairs", notes_by_label["ALG"])
        self.assertIn("MI(0.5) Total", notes_by_label)
        self.assertIn("threshold factor 0.5", notes_by_label["MI(0.5) Total"])

    def test_metric_reference_rows_include_tomo_notes(self):
        result = PlanAnalysisResult(
            source_path="plan.dcm",
            mode=AnalysisMode.TOMO,
            metadata={},
            metrics={},
            flattened_metrics={"mlot": 75.0, "ta": 2.5, "epstv_1_1": 0.1},
            supported=True,
            warnings=[],
        )

        reference_rows = build_metric_reference_rows(result)
        notes_by_label = {label: note for label, note in reference_rows}

        self.assertIn("mLOT", notes_by_label)
        self.assertIn("leaf open time", notes_by_label["mLOT"])
        self.assertIn("TA", notes_by_label)
        self.assertIn("treated sinogram area", notes_by_label["TA"])
        self.assertIn("EPSTV-1,1", notes_by_label)
        self.assertIn("one-step projection and leaf offsets", notes_by_label["EPSTV-1,1"])

    def test_metric_reference_rows_include_aurora_notes(self):
        result = PlanAnalysisResult(
            source_path="aurora.dcm",
            mode=AnalysisMode.AURORA,
            metadata={},
            metrics={},
            flattened_metrics={
                "projection_pitch_mean": 0.12,
                "theta_z_coupling_cv": 0.05,
            },
            supported=True,
            warnings=[],
        )

        metric_rows = build_metric_rows(result)
        reference_rows = build_metric_reference_rows(result)
        notes_by_label = {label: note for label, note in reference_rows}

        self.assertEqual(metric_rows[0][0], "Projection Pitch Mean")
        self.assertEqual(metric_rows[1][0], "Theta Z Coupling CV")
        self.assertIn("projection pitch", notes_by_label["Projection Pitch Mean"].lower())
        self.assertIn("theta-z coupling", notes_by_label["Theta Z Coupling CV"].lower())

    def test_reason_label_and_export_record_for_missing_external_xml(self):
        result = PlanAnalysisResult(
            source_path="data/CyberKnife/plan.dcm",
            mode=AnalysisMode.CYBERKNIFE_MLC,
            metadata={},
            metrics={},
            flattened_metrics={},
            supported=False,
            warnings=["CyberKnife MLC plan references external beam-path XML files that are not present: beam_path1.xml"],
        )

        record = build_export_record(result)

        self.assertEqual(result.reason_label, "Missing external XML")
        self.assertEqual(record["status"], "UNSUPPORTED")
        self.assertEqual(record["reason"], "Missing external XML")

    def test_reason_label_for_mode_override(self):
        result = PlanAnalysisResult(
            source_path="plan.dcm",
            mode=AnalysisMode.VMAT_IMRT,
            metadata={},
            metrics={},
            flattened_metrics={},
            supported=True,
            warnings=["Requested mode VMAT_IMRT overrides detected mode TOMO."],
        )

        self.assertEqual(result.reason_label, "Mode override")

    @patch.object(ucomx_service, "_analyze_plan_file_safe")
    def test_analyze_filepaths_yields_results_incrementally(self, analyze_safe_mock):
        analyze_safe_mock.side_effect = [
            PlanAnalysisResult("a.dcm", AnalysisMode.VMAT_IMRT, {}, {}, {}, True, []),
            PlanAnalysisResult("b.dcm", AnalysisMode.TOMO, {}, {}, {}, True, []),
        ]

        results = list(analyze_filepaths(["a.dcm", "b.dcm"], requested_mode=AnalysisMode.AUTO))

        self.assertEqual([result.source_path for result in results], ["a.dcm", "b.dcm"])
        self.assertEqual(analyze_safe_mock.call_count, 2)

    def test_detect_mode_identifies_cyberknife_mlc(self):
        mode = detect_mode(
            {
                "manufacturer": "Accuray Inc",
                "machine_id": "C0493",
                "calculation_model": "CyberKnife",
                "plan_name": "Bone_MLC",
            }
        )
        self.assertEqual(mode, AnalysisMode.CYBERKNIFE_MLC)

    def test_detect_mode_identifies_aurora_from_metadata(self):
        mode = detect_mode(
            {
                "manufacturer": "WisdomTech Medical Systems",
                "calculation_model": "DeepPlan",
                "plan_name": "Aurora Research Plan",
                "plan_label": "AURORA",
            }
        )
        self.assertEqual(mode, AnalysisMode.AURORA)

    @patch.object(ucomx_service, "pydicom")
    def test_detect_mode_from_file_identifies_aurora_rtplan(self, pydicom_mock):
        pydicom_mock.dcmread.return_value = build_fake_aurora_rtplan()

        self.assertEqual(ucomx_service.detect_mode_from_file("aurora.dcm"), AnalysisMode.AURORA)

    @patch.object(ucomx_service, "analyze_aurora_plan_file")
    @patch.object(ucomx_service, "detect_mode_from_file", return_value=AnalysisMode.AURORA)
    def test_analyze_plan_file_auto_routes_aurora_into_unified_result(
        self,
        _detect_mode_mock,
        analyze_aurora_plan_file_mock,
    ):
        analyze_aurora_plan_file_mock.return_value = AuroraAnalysisResult(
            source_path="aurora.dcm",
            metadata=AuroraPlanMetadata(
                source_path="aurora.dcm",
                plan_label="AURORA",
                plan_name="Aurora Research Plan",
                manufacturer="WisdomTech Medical Systems",
                manufacturer_model_name="DeepPlan",
                treatment_machine_name="Aurora Linac",
                patient_id="AURORA-001",
                beam_count=2,
            ),
            plan_metrics={
                "projection_pitch_mean": 0.12,
                "theta_z_coupling_cv": 0.05,
            },
            warnings=["research-only metric set"],
            supported=True,
            reason="",
        )

        result = ucomx_service.analyze_plan_file("aurora.dcm", requested_mode=AnalysisMode.AUTO)

        self.assertEqual(result.mode, AnalysisMode.AURORA)
        self.assertTrue(result.supported)
        self.assertEqual(result.metadata["calculation_model"], "DeepPlan")
        self.assertEqual(result.metadata["machine_id"], "Aurora Linac")
        self.assertEqual(result.metrics["projection_pitch_mean"], 0.12)
        self.assertEqual(result.flattened_metrics["theta_z_coupling_cv"], 0.05)
        self.assertIn("research-only metric set", result.warnings)
        analyze_aurora_plan_file_mock.assert_called_once_with("aurora.dcm")

    @patch.object(main, "log_metric_summary")
    @patch.object(main, "log_plan_summary")
    @patch.object(main, "configure_logging")
    @patch.object(main, "analyze_plan_file")
    @patch("sys.argv", ["main.py", "--input-file", "sample.dcm"])
    def test_main_cli_uses_ucomx_service(
        self,
        analyze_plan_file_mock,
        configure_logging_mock,
        log_plan_summary_mock,
        log_metric_summary_mock,
    ):
        logger = SimpleNamespace(exception=lambda *args, **kwargs: None)
        configure_logging_mock.return_value = logger
        analyze_plan_file_mock.return_value = PlanAnalysisResult(
            source_path="sample.dcm",
            mode=AnalysisMode.VMAT_IMRT,
            metadata={
                "patient_id": "P001",
                "patient_name": "Alice",
                "plan_name": "Plan A",
                "machine_id": "TB-1",
                "calculation_model": "AAA",
                "prescribed_dose": 6000,
                "mu": 300.0,
                "beam_type": "DYNAMIC",
                "beam_number": 2,
                "rotation_direction": "CW",
            },
            metrics={"em": 0.5},
            flattened_metrics={"em": 0.5},
            supported=True,
            warnings=[],
        )

        main.main()

        analyze_plan_file_mock.assert_called_once_with("sample.dcm")
        log_plan_summary_mock.assert_called_once()
        log_metric_summary_mock.assert_called_once_with(logger, {"em": 0.5})


if __name__ == "__main__":
    unittest.main()
