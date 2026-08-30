import unittest
from pathlib import Path

import numpy as np

from ApertureMetric.aperture_geometry import PyAperture
from DicomParse.dicom_rt import RTPlan
from halcyon_dual_layer_metrics import (
    BeamPaperMetrics,
    HYBRID_REPRESENTATION_KEYS,
    _aggregate_beam_results,
    _layer_contributions,
    calculate_halcyon_dual_layer_metrics_with_warnings,
)
from ucomx_models import AnalysisMode
from ucomx_service import analyze_plan_file, build_metric_reference_rows


class HalcyonDualLayerPaperMetricTests(unittest.TestCase):
    def test_plan_aggregation_excludes_beams_without_valid_geometry_observations(self):
        metrics = _aggregate_beam_results(
            [
                BeamPaperMetrics(
                    values={"mad_effective": None, "nl_pairs_effective": 0.0},
                    mu=3.0,
                ),
                BeamPaperMetrics(
                    values={"mad_effective": 10.0, "nl_pairs_effective": 2.0},
                    mu=1.0,
                ),
            ]
        )

        self.assertEqual(metrics["mad_effective"], 10.0)
        self.assertEqual(metrics["nl_pairs_effective"], 0.5)

    def test_halcyon_result_includes_tamura_and_quintero_metrics(self):
        samples = sorted(Path("data/Halcyon").glob("*.dcm"))
        if not samples:
            self.skipTest("No Halcyon RTPLAN samples are available")

        result = analyze_plan_file(str(samples[0]), requested_mode=AnalysisMode.VMAT_IMRT)
        metrics = result.flattened_metrics

        expected_keys = {
            "mcsv",
            "mcs5",
            "pa5",
            "pi5",
            "pm5",
            "eds",
            "mcsw",
            "paw",
            "piw",
            "pmw",
            "ul",
            "mcsul",
            "np",
            "mucp",
            "proximal_mcs",
            "distal_mcs",
            "proximal_weight_mean",
            "distal_weight_mean",
        }
        self.assertTrue(expected_keys.issubset(metrics), expected_keys - set(metrics))

        self.assertEqual(result.mode, AnalysisMode.VMAT_IMRT)
        self.assertTrue(result.supported)
        self.assertGreater(metrics["mcs5"], 0.0)
        self.assertGreater(metrics["pa5"], 0.0)
        self.assertGreater(metrics["pi5"], 0.0)
        self.assertGreaterEqual(metrics["pm5"], 0.0)
        self.assertLessEqual(metrics["pm5"], 1.0)
        self.assertGreaterEqual(metrics["eds"], 0.0)
        self.assertLessEqual(metrics["eds"], 1.0)
        self.assertGreaterEqual(metrics["ul"], 0.0)
        self.assertLessEqual(metrics["ul"], 1.0)
        self.assertGreaterEqual(metrics["mcsul"], 0.0)
        self.assertLessEqual(metrics["mcsul"], metrics["mcsw"])
        self.assertGreater(metrics["np"], 0.0)
        self.assertAlmostEqual(metrics["proximal_weight_mean"] + metrics["distal_weight_mean"], 1.0, places=6)

    def test_metric_reference_rows_describe_paper_specific_outputs(self):
        samples = sorted(Path("data/Halcyon").glob("*.dcm"))
        if not samples:
            self.skipTest("No Halcyon RTPLAN samples are available")

        result = analyze_plan_file(str(samples[0]), requested_mode=AnalysisMode.VMAT_IMRT)
        reference_text = "\n".join(" | ".join(row) for row in build_metric_reference_rows(result))

        self.assertIn("Tamura", reference_text)
        self.assertIn("effective distal MLC score", reference_text)
        self.assertIn("Quintero", reference_text)
        self.assertIn("uncovered-layer", reference_text)

    def test_halcyon_result_includes_effective_and_stacked_hybrid_families(self):
        samples = sorted(Path("data/Halcyon").glob("*.dcm"))
        if not samples:
            self.skipTest("No Halcyon RTPLAN samples are available")

        result = analyze_plan_file(str(samples[0]), requested_mode=AnalysisMode.VMAT_IMRT)
        metrics = result.flattened_metrics

        expected = {
            "mcsv_effective",
            "aav_effective",
            "lsv_effective",
            "pa_effective",
            "mad_effective",
            "alg_effective",
            "alg_sd_effective",
            "sas_5mm_effective",
            "sas_10mm_effective",
            "sas_20mm_effective",
            "lt_effective",
            "lt_mean_leaf_effective",
            "nl_pairs_effective",
            "nl_leaves_effective",
            "mcsv_stacked",
            "aav_stacked",
            "lsv_stacked",
            "pa_stacked",
            "mad_stacked",
            "alg_stacked",
            "alg_sd_stacked",
            "sas_5mm_stacked",
            "sas_10mm_stacked",
            "sas_20mm_stacked",
            "lt_stacked",
            "lt_mean_leaf_stacked",
            "nl_pairs_stacked",
            "nl_leaves_stacked",
        }
        self.assertTrue(expected.issubset(metrics), expected - set(metrics))
        self.assertEqual(metrics["mcsv_effective"], metrics["mcs5"])
        self.assertEqual(metrics["pa_effective"], metrics["pa5"])
        self.assertAlmostEqual(
            metrics["nl_pairs_stacked"],
            result.metrics["nl_pairs"][0] + result.metrics["nl_pairs"][1],
            places=2,
        )
        self.assertNotEqual(metrics["mcsv_effective"], metrics["mcsv_stacked"])

    def test_uncovered_layer_is_zero_when_dual_layers_are_identical(self):
        # Identical dual layers should not inflate Quintero UL via open-height alone.
        positions = np.array([[-5.0, -4.0], [5.0, 6.0]])
        aperture = PyAperture(
            leaf_positions=positions,
            leaf_widths=np.array([5.0, 5.0]),
            jaw=[-10.0, 10.0, 10.0, -10.0],
            gantry_angle=0.0,
        )

        distal_weight, proximal_weight, distal_ul, proximal_ul = _layer_contributions(
            aperture,
            positions,
            positions,
        )

        self.assertAlmostEqual(0.5, distal_weight)
        self.assertAlmostEqual(0.5, proximal_weight)
        self.assertEqual(0.0, distal_ul)
        self.assertEqual(0.0, proximal_ul)

    def test_layer_mismatch_disables_effective_and_stacked_families(self):
        samples = sorted(Path("data/Halcyon").glob("*.dcm"))
        if not samples:
            self.skipTest("No Halcyon RTPLAN samples are available")

        plan = RTPlan(filename=str(samples[0])).to_plan_dict()
        beam = next(iter(plan["beams"].values()))
        control_point = beam["ControlPointSequence"][0]
        control_point.BeamLimitingDevicePositionSequence = [
            item
            for item in control_point.BeamLimitingDevicePositionSequence
            if str(item.RTBeamLimitingDeviceType).upper() != "MLCX2"
        ]

        metrics, warnings = calculate_halcyon_dual_layer_metrics_with_warnings(plan)

        self.assertTrue(all(metrics[key] is None for key in HYBRID_REPRESENTATION_KEYS))
        self.assertTrue(any(item.startswith("[HALCYON_LAYER_ALIGNMENT]") for item in warnings))

    def test_omitted_unchanged_dual_layer_positions_are_inherited(self):
        samples = sorted(Path("data/Halcyon").glob("*.dcm"))
        if not samples:
            self.skipTest("No Halcyon RTPLAN samples are available")

        plan = RTPlan(filename=str(samples[0])).to_plan_dict()
        beam = next(iter(plan["beams"].values()))
        control_point = beam["ControlPointSequence"][-1]
        control_point.BeamLimitingDevicePositionSequence = [
            item
            for item in control_point.BeamLimitingDevicePositionSequence
            if str(item.RTBeamLimitingDeviceType).upper() not in {"MLCX1", "MLCX2"}
        ]

        metrics, warnings = calculate_halcyon_dual_layer_metrics_with_warnings(plan)

        self.assertTrue(all(metrics[key] is not None for key in HYBRID_REPRESENTATION_KEYS))
        self.assertFalse(any(item.startswith("[HALCYON_LAYER_ALIGNMENT]") for item in warnings))


if __name__ == "__main__":
    unittest.main()
