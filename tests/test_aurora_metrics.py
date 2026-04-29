import math
import unittest
from pathlib import Path
from types import SimpleNamespace

from aurora_svmat_lab.models import AuroraBeam, AuroraControlPoint
from aurora_svmat_lab.metrics import calculate_beam_metrics, calculate_plan_metrics


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
        gantry_angle_deg=angle % 360.0,
        cumulative_meterset_weight=meterset_weight,
        axial_position_mm=axial,
        mlc_x1_positions_mm=x1,
        mlc_x2_positions_mm=x2,
    )


def build_multi_rotation_beam() -> AuroraBeam:
    control_points = []
    for index in range(11):
        control_points.append(
            build_control_point(
                index=index,
                angle=162.0 * index,
                axial=15.0 * index,
                meterset_weight=index / 10.0,
                x1=(-5.0, -5.0),
                x2=(5.0, 5.0),
            )
        )
    return AuroraBeam(beam_number=1, beam_name="Rotation Beam", control_points=control_points)


def build_modulated_beam() -> AuroraBeam:
    return AuroraBeam(
        beam_number=2,
        beam_name="Modulated Beam",
        control_points=[
            build_control_point(
                index=0,
                angle=0.0,
                axial=0.0,
                meterset_weight=0.0,
                x1=(-5.0, -5.0),
                x2=(5.0, 5.0),
            ),
            build_control_point(
                index=1,
                angle=90.0,
                axial=10.0,
                meterset_weight=0.5,
                x1=(-4.0, -6.0),
                x2=(6.0, 4.0),
            ),
            build_control_point(
                index=2,
                angle=180.0,
                axial=20.0,
                meterset_weight=1.0,
                x1=(-3.0, -7.0),
                x2=(7.0, 3.0),
            ),
        ],
    )


def build_zero_travel_beam() -> SimpleNamespace:
    control_points = [
        build_control_point(
            index=0,
            angle=0.0,
            axial=5.0,
            meterset_weight=0.0,
            x1=(-5.0,),
            x2=(5.0,),
        ),
        build_control_point(
            index=1,
            angle=30.0,
            axial=5.0,
            meterset_weight=1.0,
            x1=(-4.5,),
            x2=(5.5,),
        ),
    ]
    return SimpleNamespace(
        beam_number=3,
        beam_name="Zero Travel",
        control_points=control_points,
        total_mu=200.0,
    )


def build_variable_pitch_beam() -> AuroraBeam:
    return AuroraBeam(
        beam_number=5,
        beam_name="Variable Pitch Beam",
        control_points=[
            build_control_point(
                index=0,
                angle=0.0,
                axial=0.0,
                meterset_weight=0.0,
                x1=(-5.0,),
                x2=(5.0,),
            ),
            build_control_point(
                index=1,
                angle=10.0,
                axial=10.0,
                meterset_weight=0.25,
                x1=(-5.0,),
                x2=(5.0,),
            ),
            build_control_point(
                index=2,
                angle=20.0,
                axial=40.0,
                meterset_weight=1.0,
                x1=(-5.0,),
                x2=(5.0,),
            ),
        ],
    )


def build_small_opening_beam() -> AuroraBeam:
    return AuroraBeam(
        beam_number=7,
        beam_name="Small Opening Beam",
        control_points=[
            build_control_point(
                index=0,
                angle=0.0,
                axial=0.0,
                meterset_weight=0.0,
                x1=(0.0, 0.0),
                x2=(10.0, 10.0),
            ),
            build_control_point(
                index=1,
                angle=90.0,
                axial=10.0,
                meterset_weight=0.2,
                x1=(0.0, 0.0),
                x2=(1.0, 9.0),
            ),
            build_control_point(
                index=2,
                angle=180.0,
                axial=20.0,
                meterset_weight=0.7,
                x1=(0.0, 0.0),
                x2=(4.0, 12.0),
            ),
            build_control_point(
                index=3,
                angle=270.0,
                axial=30.0,
                meterset_weight=1.0,
                x1=(0.0, 0.0),
                x2=(20.0, 6.0),
            ),
        ],
    )


def build_dual_layer_synergy_beam() -> AuroraBeam:
    return AuroraBeam(
        beam_number=8,
        beam_name="Dual Layer Synergy Beam",
        control_points=[
            build_control_point(
                index=0,
                angle=0.0,
                axial=0.0,
                meterset_weight=0.0,
                x1=(1.0,),
                x2=(2.0,),
            ),
            build_control_point(
                index=1,
                angle=90.0,
                axial=10.0,
                meterset_weight=0.2,
                x1=(2.0,),
                x2=(4.0,),
            ),
            build_control_point(
                index=2,
                angle=180.0,
                axial=20.0,
                meterset_weight=0.6,
                x1=(4.0,),
                x2=(8.0,),
            ),
            build_control_point(
                index=3,
                angle=270.0,
                axial=30.0,
                meterset_weight=1.0,
                x1=(7.0,),
                x2=(14.0,),
            ),
        ],
    )


def build_reversed_beam(source_beam: AuroraBeam, *, beam_number: int, beam_name: str) -> AuroraBeam:
    control_points = list(reversed(source_beam.control_points))
    rebuilt = [
        build_control_point(
            index=index,
            angle=control_point.gantry_angle_deg,
            axial=control_point.axial_position_mm,
            meterset_weight=control_point.cumulative_meterset_weight,
            x1=tuple(control_point.mlc_x1_positions_mm),
            x2=tuple(control_point.mlc_x2_positions_mm),
        )
        for index, control_point in enumerate(control_points)
    ]
    return AuroraBeam(beam_number=beam_number, beam_name=beam_name, control_points=rebuilt)


class AuroraMetricTests(unittest.TestCase):
    def test_v2_projection_physics_metrics_exist_for_beam(self):
        metrics = calculate_beam_metrics(build_modulated_beam())

        self.assertAlmostEqual(metrics["longitudinal_travel_mm"], 20.0)
        self.assertAlmostEqual(metrics["total_rotation_deg"], 180.0)
        self.assertAlmostEqual(metrics["rotations"], 0.5)
        self.assertAlmostEqual(metrics["travel_per_rotation_mm"], 40.0)
        self.assertAlmostEqual(metrics["projection_pitch_mean"], 20.0 / 180.0)
        self.assertAlmostEqual(metrics["projection_pitch_cv"], 0.0)
        self.assertAlmostEqual(metrics["projection_mu_density_mean_proxy"], 0.05)
        self.assertAlmostEqual(metrics["projection_mu_density_cv_proxy"], 0.0)
        self.assertAlmostEqual(metrics["projection_aperture_change_mean"], 0.0)
        self.assertAlmostEqual(metrics["projection_aperture_change_cv"], 0.0)
        self.assertAlmostEqual(metrics["projection_leaf_travel_mean"], 0.4)
        self.assertAlmostEqual(metrics["projection_leaf_travel_cv"], 0.0)
        self.assertIn("projection_leaf_travel_mean_mlcx1", metrics)
        self.assertIn("projection_leaf_travel_cv_mlcx1", metrics)
        self.assertIn("projection_leaf_travel_mean_mlcx2", metrics)
        self.assertIn("projection_leaf_travel_cv_mlcx2", metrics)
        self.assertAlmostEqual(metrics["projection_leaf_travel_mean_mlcx1"], 0.2)
        self.assertAlmostEqual(metrics["projection_leaf_travel_cv_mlcx1"], 0.0)
        self.assertAlmostEqual(metrics["projection_leaf_travel_mean_mlcx2"], 0.2)
        self.assertAlmostEqual(metrics["projection_leaf_travel_cv_mlcx2"], 0.0)
        self.assertAlmostEqual(metrics["theta_z_coupling_cv"], 0.0)
        self.assertAlmostEqual(metrics["mu_z_coupling_cv_proxy"], 0.0)
        self.assertAlmostEqual(metrics["mlc_z_coupling_cv"], 0.0)
        self.assertAlmostEqual(metrics["mlcx1_z_coupling_cv"], 0.0)
        self.assertAlmostEqual(metrics["mlcx2_z_coupling_cv"], 0.0)

    def test_mm_per_rotation_uses_total_axial_travel_and_total_rotation(self):
        metrics = calculate_beam_metrics(build_multi_rotation_beam())

        self.assertAlmostEqual(metrics["axial_travel_mm"], 150.0)
        self.assertAlmostEqual(metrics["gantry_rotation_deg"], 1620.0)
        self.assertAlmostEqual(metrics["mm_per_rotation"], 150.0 / (1620.0 / 360.0))
        self.assertAlmostEqual(metrics["pitch_consistency"], 0.0)

    def test_mu_per_mm_handles_zero_travel_safely(self):
        metrics = calculate_beam_metrics(build_zero_travel_beam())

        self.assertIsNone(metrics["mu_per_mm"])
        self.assertIsNone(metrics["aperture_change_per_mm"])
        self.assertIsNone(metrics["leaf_travel_per_mm"])

    def test_modulation_metrics_are_explicit_and_interpretable(self):
        metrics = calculate_beam_metrics(build_modulated_beam())

        self.assertAlmostEqual(metrics["axial_travel_mm"], 20.0)
        self.assertAlmostEqual(metrics["gantry_rotation_deg"], 180.0)
        self.assertAlmostEqual(metrics["mm_per_deg"], 20.0 / 180.0)
        self.assertAlmostEqual(metrics["mm_per_rotation"], 40.0)
        self.assertAlmostEqual(metrics["pitch_consistency"], 0.0)
        self.assertAlmostEqual(metrics["mu_per_mm"], 0.05)
        self.assertAlmostEqual(metrics["aperture_change_per_mm"], 0.0)
        self.assertAlmostEqual(metrics["leaf_travel_per_mm"], 0.4)
        self.assertAlmostEqual(metrics["coupled_modulation_index"], 1.0 / 14.0)

    def test_v21_split_dual_layer_coupling_metrics_separate_mlcx1_and_mlcx2(self):
        beam = AuroraBeam(
            beam_number=6,
            beam_name="Split Dual Layer Beam",
            control_points=[
                build_control_point(
                    index=0,
                    angle=0.0,
                    axial=0.0,
                    meterset_weight=0.0,
                    x1=(-5.0, -5.0),
                    x2=(5.0, 5.0),
                ),
                build_control_point(
                    index=1,
                    angle=90.0,
                    axial=10.0,
                    meterset_weight=0.5,
                    x1=(-5.0, -5.0),
                    x2=(4.0, 5.0),
                ),
                build_control_point(
                    index=2,
                    angle=180.0,
                    axial=20.0,
                    meterset_weight=1.0,
                    x1=(-3.0, -5.0),
                    x2=(4.0, 4.0),
                ),
            ],
        )

        metrics = calculate_beam_metrics(beam)

        self.assertIn("mlcx1_z_coupling_cv", metrics)
        self.assertIn("mlcx2_z_coupling_cv", metrics)
        self.assertAlmostEqual(metrics["projection_leaf_travel_mean_mlcx1"], 0.1)
        self.assertAlmostEqual(metrics["projection_leaf_travel_mean_mlcx2"], 0.1)
        self.assertAlmostEqual(metrics["mlcx1_z_coupling_cv"], 1.0)
        self.assertAlmostEqual(metrics["mlcx2_z_coupling_cv"], 0.0)
        self.assertAlmostEqual(metrics["mlc_z_coupling_cv"], 0.5)

    def test_plan_metrics_recompute_nonlinear_terms_over_all_intervals(self):
        beam_a = build_multi_rotation_beam()
        beam_b = build_variable_pitch_beam()

        metrics = calculate_plan_metrics([beam_a, beam_b])
        interval_pitches = ([15.0 / 162.0] * 10) + [1.0, 3.0]
        mean_pitch = sum(interval_pitches) / len(interval_pitches)
        pitch_variance = sum((value - mean_pitch) ** 2 for value in interval_pitches) / len(interval_pitches)
        expected_pitch = math.sqrt(pitch_variance) / mean_pitch
        interval_mu_density = ([0.1 / 15.0] * 10) + [0.25 / 10.0, 0.75 / 30.0]
        mean_mu_density = sum(interval_mu_density) / len(interval_mu_density)
        mu_density_variance = sum(
            (value - mean_mu_density) ** 2 for value in interval_mu_density
        ) / len(interval_mu_density)
        expected_mu_density_variability = math.sqrt(mu_density_variance) / mean_mu_density
        expected_cmi = (
            (expected_mu_density_variability / (1.0 + expected_mu_density_variability))
            + (expected_pitch / (1.0 + expected_pitch))
        ) / 4.0

        self.assertAlmostEqual(metrics["axial_travel_mm"], 190.0)
        self.assertAlmostEqual(metrics["gantry_rotation_deg"], 1640.0)
        self.assertAlmostEqual(metrics["mm_per_deg"], 190.0 / 1640.0)
        self.assertAlmostEqual(metrics["mm_per_rotation"], 190.0 / (1640.0 / 360.0))
        self.assertAlmostEqual(metrics["mu_per_mm"], 2.0 / 190.0)
        self.assertAlmostEqual(metrics["pitch_consistency"], expected_pitch)
        self.assertAlmostEqual(metrics["coupled_modulation_index"], expected_cmi)
        self.assertAlmostEqual(metrics["projection_pitch_cv"], expected_pitch)
        self.assertAlmostEqual(metrics["theta_z_coupling_cv"], expected_pitch)
        self.assertAlmostEqual(metrics["projection_mu_density_cv_proxy"], expected_mu_density_variability)
        self.assertAlmostEqual(metrics["mu_z_coupling_cv_proxy"], expected_mu_density_variability)
        self.assertAlmostEqual(metrics["projection_leaf_travel_cv"], 0.0)
        self.assertAlmostEqual(metrics["mlc_z_coupling_cv"], 0.0)
        self.assertIn("projection_leaf_travel_cv_mlcx1", metrics)
        self.assertIn("projection_leaf_travel_cv_mlcx2", metrics)
        self.assertIn("mlcx1_z_coupling_cv", metrics)
        self.assertIn("mlcx2_z_coupling_cv", metrics)
        self.assertAlmostEqual(metrics["projection_leaf_travel_cv_mlcx1"], 0.0)
        self.assertAlmostEqual(metrics["projection_leaf_travel_cv_mlcx2"], 0.0)
        self.assertAlmostEqual(metrics["mlcx1_z_coupling_cv"], 0.0)
        self.assertAlmostEqual(metrics["mlcx2_z_coupling_cv"], 0.0)

    def test_v3_small_opening_peak_and_regional_metrics_are_reported(self):
        metrics = calculate_beam_metrics(build_small_opening_beam())

        self.assertAlmostEqual(metrics["small_opening_fraction"], 0.6)
        self.assertAlmostEqual(metrics["near_closed_fraction"], 0.1)
        self.assertAlmostEqual(metrics["effective_small_gap_burden"], 0.31)

        self.assertAlmostEqual(metrics["projection_pitch_max"], 1.0 / 9.0)
        self.assertAlmostEqual(metrics["projection_pitch_top3_mean"], 1.0 / 9.0)
        self.assertAlmostEqual(metrics["projection_mu_density_max_proxy"], 0.05)
        self.assertAlmostEqual(metrics["projection_mu_density_top3_mean_proxy"], (0.02 + 0.05 + 0.03) / 3.0)
        self.assertAlmostEqual(metrics["projection_aperture_change_max"], 1.0)
        self.assertAlmostEqual(metrics["projection_aperture_change_top3_mean"], (1.0 + 0.6 + 1.0) / 3.0)
        self.assertAlmostEqual(metrics["projection_leaf_travel_max"], 2.2)
        self.assertAlmostEqual(metrics["projection_leaf_travel_top3_mean"], (1.0 + 0.6 + 2.2) / 3.0)

        self.assertAlmostEqual(metrics["head_mu_density_mean_proxy"], 0.02)
        self.assertAlmostEqual(metrics["mid_mu_density_mean_proxy"], 0.05)
        self.assertAlmostEqual(metrics["tail_mu_density_mean_proxy"], 0.03)
        self.assertAlmostEqual(metrics["head_mu_density_cv_proxy"], 0.0)
        self.assertAlmostEqual(metrics["mid_mu_density_cv_proxy"], 0.0)
        self.assertAlmostEqual(metrics["tail_mu_density_cv_proxy"], 0.0)

        self.assertAlmostEqual(metrics["head_aperture_change_mean"], 1.0)
        self.assertAlmostEqual(metrics["mid_aperture_change_mean"], 0.6)
        self.assertAlmostEqual(metrics["tail_aperture_change_mean"], 1.0)
        self.assertAlmostEqual(metrics["head_leaf_travel_mean"], 1.0)
        self.assertAlmostEqual(metrics["mid_leaf_travel_mean"], 0.6)
        self.assertAlmostEqual(metrics["tail_leaf_travel_mean"], 2.2)

    def test_v3_dual_layer_synergy_metrics_are_interpretable(self):
        metrics = calculate_beam_metrics(build_dual_layer_synergy_beam())

        self.assertAlmostEqual(metrics["layer_imbalance_index"], 1.0 / 3.0)
        self.assertAlmostEqual(metrics["layer_correlation_index"], 1.0)
        self.assertAlmostEqual(metrics["x1_x2_aperture_disparity"], 1.0 / 3.0)
        self.assertAlmostEqual(metrics["x1_x2_leaf_travel_ratio"], 0.5)

    def test_v3_reversal_metrics_detect_balanced_bidirectional_pair(self):
        forward_beam = build_small_opening_beam()
        backward_beam = build_reversed_beam(forward_beam, beam_number=9, beam_name="Backward Beam")

        metrics = calculate_plan_metrics([forward_beam, backward_beam])

        self.assertAlmostEqual(metrics["reversal_symmetry_index"], 1.0)
        self.assertAlmostEqual(metrics["forward_backward_metric_difference"], 0.0)
        self.assertAlmostEqual(metrics["beam_pair_balance_index"], 1.0)

    def test_metrics_and_export_modules_do_not_import_parser_layer(self):
        metrics_source = Path("aurora_svmat_lab/metrics.py").read_text(encoding="utf-8")
        export_source = Path("aurora_svmat_lab/export.py").read_text(encoding="utf-8")

        self.assertNotIn("from .parser import", metrics_source)
        self.assertNotIn("from .parser import", export_source)


if __name__ == "__main__":
    unittest.main()
