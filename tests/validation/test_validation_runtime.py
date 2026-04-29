import sys
import types
import unittest
from unittest.mock import patch

import numpy as np
from aurora_svmat_lab.models import AuroraAnalysisResult, AuroraPlanMetadata
from ucomx_models import AnalysisMode, PlanAnalysisResult


class ValidationRuntimeTests(unittest.TestCase):
    def test_runtime_normalization_routes_core_domains_and_filters_unknown_metrics(self):
        from validation_runtime import ValidationCaseResult, analyze_validation_case

        fake_result = PlanAnalysisResult(
            source_path="demo_tomo.dcm",
            mode=AnalysisMode.TOMO,
            metadata={"plan_name": "Demo Tomo"},
            metrics={"mf": 0.42},
            flattened_metrics={"mf": 0.42, "unknown_metric": 9.9},
            supported=True,
            warnings=[],
        )

        fake_service = types.ModuleType("ucomx_service")
        fake_service.analyze_plan_file = unittest.mock.Mock(return_value=fake_result)

        with patch.dict(sys.modules, {"ucomx_service": fake_service}):
            record = analyze_validation_case(source_path="demo_tomo.dcm", domain="TOMO")

        fake_service.analyze_plan_file.assert_called_once_with(
            "demo_tomo.dcm",
            requested_mode=AnalysisMode.TOMO,
        )
        self.assertIsInstance(record, ValidationCaseResult)
        self.assertEqual("TOMO", record.domain)
        self.assertEqual("TOMO", record.mode)
        self.assertTrue(record.supported)
        self.assertEqual({"mf": 0.42}, record.metrics)
        self.assertNotIn("unknown_metric", record.metrics)

    def test_runtime_normalization_returns_canonical_aurora_record(self):
        from validation_runtime import ValidationCaseResult, analyze_validation_case

        fake_result = AuroraAnalysisResult(
            source_path="aurora_demo.dcm",
            metadata=AuroraPlanMetadata(plan_name="Aurora Demo"),
            plan_metrics={"projection_pitch_mean": 1.25, "unknown_metric": 7.7},
            warnings=["synthetic warning"],
            supported=True,
            reason="",
        )

        fake_service = types.ModuleType("aurora_svmat_lab.service")
        fake_service.analyze_plan_file = unittest.mock.Mock(return_value=fake_result)

        with patch.dict(sys.modules, {"aurora_svmat_lab.service": fake_service}):
            record = analyze_validation_case(source_path="aurora_demo.dcm", domain="AURORA")

        fake_service.analyze_plan_file.assert_called_once_with("aurora_demo.dcm")
        self.assertIsInstance(record, ValidationCaseResult)
        self.assertEqual("AURORA", record.domain)
        self.assertEqual("AURORA", record.mode)
        self.assertTrue(record.supported)
        self.assertEqual({"projection_pitch_mean": 1.25}, record.metrics)
        self.assertEqual(("synthetic warning",), record.warnings)

    def test_runtime_normalization_drops_non_scalar_core_metric_values(self):
        from validation_runtime import analyze_validation_case

        fake_result = PlanAnalysisResult(
            source_path="demo_vmat.dcm",
            mode=AnalysisMode.VMAT_IMRT,
            metadata={"plan_name": "Demo VMAT"},
            metrics={"mi_0_2": np.array([5.93, 7.8, 7.85])},
            flattened_metrics={
                "mi_0_2": np.array([5.93, 7.8, 7.85]),
                "pm": np.float64(0.44),
            },
            supported=True,
            warnings=[],
        )

        fake_service = types.ModuleType("ucomx_service")
        fake_service.analyze_plan_file = unittest.mock.Mock(return_value=fake_result)

        with patch.dict(sys.modules, {"ucomx_service": fake_service}):
            record = analyze_validation_case(source_path="demo_vmat.dcm", domain="VMAT_IMRT")

        self.assertEqual({"pm": 0.44}, record.metrics)
        self.assertNotIn("mi_0_2", record.metrics)


if __name__ == "__main__":
    unittest.main()
