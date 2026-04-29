import unittest

import aurora_svmat
import aurora_svmat_cli
import aurora_svmat_lab
from aurora_svmat_lab import models
from tests.test_aurora_parser import build_fake_aurora_rtplan


class AuroraServiceScaffoldingTests(unittest.TestCase):
    def test_aurora_package_exports_full_surface(self):
        self.assertEqual(
            aurora_svmat_lab.__all__,
            ["models", "parser", "metrics", "service", "export", "formula_pdf", "notes", "gui", "cli"],
        )
        self.assertIs(models, aurora_svmat_lab.models)

    def test_service_analyzes_supported_dataset(self):
        from aurora_svmat_lab.service import analyze_dataset

        result = analyze_dataset(build_fake_aurora_rtplan())

        self.assertTrue(result.supported)
        self.assertEqual(result.reason, "")
        self.assertIn("axial_travel_mm", result.plan_metrics)
        self.assertGreater(result.plan_metrics["gantry_rotation_deg"], 0.0)

    def test_service_returns_unsupported_when_axial_track_is_missing(self):
        from aurora_svmat_lab.service import analyze_dataset

        dataset = build_fake_aurora_rtplan()
        for control_point in dataset.BeamSequence[0].ControlPointSequence:
            if hasattr(control_point, "IsocenterPosition"):
                del control_point.IsocenterPosition
            if (0x4001, 0x1004) in control_point:
                del control_point[(0x4001, 0x1004)]
            if (0x4001, 0x1005) in control_point:
                del control_point[(0x4001, 0x1005)]

        result = analyze_dataset(dataset)

        self.assertFalse(result.supported)
        self.assertEqual(result.reason, "Missing axial trajectory")

    def test_cli_builds_argument_parser(self):
        from aurora_svmat_lab.cli import build_arg_parser

        parser = build_arg_parser()

        self.assertEqual(parser.prog, "aurora_svmat_cli")

    def test_aurora_entrypoints_call_real_main_functions(self):
        self.assertIsNone(aurora_svmat.main())
        self.assertIsNone(aurora_svmat_cli.main())
