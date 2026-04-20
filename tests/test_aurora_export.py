import unittest
from types import SimpleNamespace

from aurora_svmat_lab.export import export_beam_rows, export_plan_rows, export_trajectory_rows
from aurora_svmat_lab.metrics import calculate_plan_metrics
from aurora_svmat_lab.models import AuroraBeam, AuroraControlPoint, AuroraPlanMetadata
from aurora_svmat_lab.notes import get_metric_notes


def build_control_point(
    *,
    index: int,
    angle: float,
    axial: float,
    meterset_weight: float,
    x1: tuple[float, ...],
    x2: tuple[float, ...],
) -> AuroraControlPoint:
    return AuroraControlPoint(
        control_point_index=index,
        gantry_angle_deg=angle,
        cumulative_meterset_weight=meterset_weight,
        axial_position_mm=axial,
        mlc_x1_positions_mm=x1,
        mlc_x2_positions_mm=x2,
    )


def build_beam() -> AuroraBeam:
    return AuroraBeam(
        beam_number=1,
        beam_name="Beam A",
        control_points=[
            build_control_point(index=0, angle=0.0, axial=0.0, meterset_weight=0.0, x1=(-5.0,), x2=(5.0,)),
            build_control_point(index=1, angle=120.0, axial=15.0, meterset_weight=0.5, x1=(-4.0,), x2=(6.0,)),
            build_control_point(index=2, angle=240.0, axial=30.0, meterset_weight=1.0, x1=(-3.0,), x2=(7.0,)),
        ],
    )


def build_fake_analysis_result() -> SimpleNamespace:
    beam = build_beam()
    metadata = AuroraPlanMetadata(
        source_path="synthetic/aurora_plan.dcm",
        plan_label="AURORA",
        plan_name="Aurora Research Plan",
        manufacturer="WisdomTech Medical Systems",
        manufacturer_model_name="DeepPlan",
        beam_count=1,
    )
    return SimpleNamespace(
        source_path=metadata.source_path,
        metadata=metadata,
        beams=[beam],
        warnings=["Private axial audit differs by 0.2 mm."],
        supported=False,
        reason="Missing axial trajectory",
        plan_metrics=calculate_plan_metrics([beam]),
    )


class AuroraExportTests(unittest.TestCase):
    def test_export_rows_include_reason_and_core_aurora_metrics(self):
        result = build_fake_analysis_result()

        rows = export_plan_rows([result])

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["reason"], "Missing axial trajectory")
        self.assertIn("travel_per_rotation_mm", rows[0])
        self.assertIn("projection_pitch_mean", rows[0])
        self.assertIn("projection_pitch_cv", rows[0])
        self.assertIn("reversal_symmetry_index", rows[0])
        self.assertIn("beam_pair_balance_index", rows[0])
        self.assertIn("coupled_modulation_index", rows[0])
        self.assertEqual(rows[0]["warning_count"], 1)

    def test_beam_and_trajectory_exports_flatten_synthetic_motion(self):
        result = build_fake_analysis_result()

        beam_rows = export_beam_rows([result])
        trajectory_rows = export_trajectory_rows([result])

        self.assertEqual(len(beam_rows), 1)
        self.assertEqual(beam_rows[0]["beam_number"], 1)
        self.assertIn("leaf_travel_per_mm", beam_rows[0])
        self.assertIn("small_opening_fraction", beam_rows[0])
        self.assertIn("projection_leaf_travel_max", beam_rows[0])
        self.assertIn("head_mu_density_mean_proxy", beam_rows[0])
        self.assertIn("layer_correlation_index", beam_rows[0])
        self.assertIn("projection_leaf_travel_mean_mlcx1", beam_rows[0])
        self.assertIn("projection_leaf_travel_mean_mlcx2", beam_rows[0])
        self.assertEqual(len(trajectory_rows), 3)
        self.assertEqual(trajectory_rows[1]["control_point_index"], 1)
        self.assertIn("delta_gantry_deg", trajectory_rows[1])
        self.assertAlmostEqual(trajectory_rows[1]["projection_pitch"], 15.0 / 120.0)
        self.assertAlmostEqual(trajectory_rows[1]["projection_mu_density_proxy"], 0.5 / 15.0)
        self.assertAlmostEqual(trajectory_rows[1]["projection_leaf_travel"], 2.0 / 15.0)
        self.assertAlmostEqual(trajectory_rows[1]["projection_leaf_travel_mlcx1"], 1.0 / 15.0)
        self.assertAlmostEqual(trajectory_rows[1]["projection_leaf_travel_mlcx2"], 1.0 / 15.0)

    def test_metric_notes_cover_all_first_pass_aurora_metrics(self):
        notes = get_metric_notes()

        expected_v2_metrics = {
            "longitudinal_travel_mm",
            "total_rotation_deg",
            "rotations",
            "travel_per_rotation_mm",
            "projection_pitch_mean",
            "projection_pitch_cv",
            "projection_mu_density_mean_proxy",
            "projection_mu_density_cv_proxy",
            "projection_aperture_change_mean",
            "projection_aperture_change_cv",
            "projection_leaf_travel_mean",
            "projection_leaf_travel_cv",
            "projection_leaf_travel_mean_mlcx1",
            "projection_leaf_travel_cv_mlcx1",
            "projection_leaf_travel_mean_mlcx2",
            "projection_leaf_travel_cv_mlcx2",
            "theta_z_coupling_cv",
            "mu_z_coupling_cv_proxy",
            "mlc_z_coupling_cv",
            "mlcx1_z_coupling_cv",
            "mlcx2_z_coupling_cv",
        }

        self.assertTrue(expected_v2_metrics.issubset(set(notes)))
        self.assertIn("projection", notes["projection_pitch_mean"].lower())
        self.assertIn("coupling", notes["theta_z_coupling_cv"].lower())
        self.assertIn("mlcx1_z_coupling_cv", notes)
        self.assertIn("mlcx2_z_coupling_cv", notes)
        self.assertIn("x1", notes["mlcx1_z_coupling_cv"].lower())
        self.assertIn("x2", notes["mlcx2_z_coupling_cv"].lower())


if __name__ == "__main__":
    unittest.main()
