import unittest
import os
from pathlib import Path

from pydicom.dataset import Dataset
from pydicom.sequence import Sequence

from aurora_svmat_lab.parser import (
    _to_float_tuple,
    is_aurora_rtplan,
    parse_aurora_rtplan,
    reconstruct_observed_angle_deltas,
    wrap_angle_delta,
)


REAL_SAMPLE_ENV = "AURORA_SAMPLE_RTPLAN"
REAL_SAMPLE_PATH = Path(os.environ[REAL_SAMPLE_ENV]) if os.environ.get(REAL_SAMPLE_ENV) else None


def build_fake_aurora_rtplan(
    *,
    include_mlcx2: bool = True,
    control_point_count: int = 3,
    dynamic_motion: bool = True,
    manufacturer: str = "WisdomTech Medical Systems",
    manufacturer_model_name: str = "DeepPlan",
    treatment_delivery_type: str = "TREATMENT",
) -> Dataset:
    dataset = Dataset()
    dataset.SOPClassUID = "1.2.840.10008.5.1.4.1.1.481.5"
    dataset.Modality = "RTPLAN"
    dataset.RTPlanLabel = "AURORA"
    dataset.RTPlanName = "Aurora Research Plan"
    dataset.Manufacturer = manufacturer
    dataset.ManufacturerModelName = manufacturer_model_name
    dataset.PatientID = "AURORA-001"
    dataset.StudyInstanceUID = "1.2.3"
    dataset.SeriesInstanceUID = "1.2.3.4"
    dataset.SOPInstanceUID = "1.2.3.4.5"
    dataset.BeamSequence = Sequence(
        [
            build_fake_beam(
                include_mlcx2=include_mlcx2,
                control_point_count=control_point_count,
                dynamic_motion=dynamic_motion,
                treatment_delivery_type=treatment_delivery_type,
            )
        ]
    )
    return dataset


def build_fake_beam(
    *,
    include_mlcx2: bool,
    control_point_count: int,
    dynamic_motion: bool,
    treatment_delivery_type: str,
) -> Dataset:
    beam = Dataset()
    beam.BeamNumber = 1
    beam.BeamName = "Beam A"
    beam.BeamType = "DYNAMIC"
    beam.TreatmentDeliveryType = treatment_delivery_type
    beam.TreatmentMachineName = "Aurora Linac"
    beam.ControlPointSequence = Sequence(
        [
            build_fake_control_point(
                index=0,
                angle=0.0,
                axial=-60.25,
                meterset_weight=0.0,
                jaw_x=(-10.0, 10.0),
                jaw_y=(-20.0, 20.0),
                mlcx1=[-15.0 + value for value in range(60)],
                mlcx2=[-14.5 + value for value in range(58)],
                private_1004=-165.0,
                private_1005=(-6.775, -218.05, -135.25),
                direction="CW",
                include_mlcx2=include_mlcx2,
            ),
            build_fake_control_point(
                index=1,
                angle=356.0 if dynamic_motion else 0.0,
                axial=-60.620368958 if dynamic_motion else -60.25,
                meterset_weight=0.5 if dynamic_motion else 0.0,
                jaw_x=(-10.5, 10.5),
                jaw_y=(-19.5, 19.5),
                mlcx1=[-14.0 + value for value in range(60)],
                mlcx2=[-13.5 + value for value in range(58)],
                private_1004=-164.629631042,
                private_1005=None,
                direction="CW",
                include_mlcx2=include_mlcx2,
            ),
            build_fake_control_point(
                index=2,
                angle=352.0 if dynamic_motion else 0.0,
                axial=-60.990737916 if dynamic_motion else -60.25,
                meterset_weight=1.0 if dynamic_motion else 0.0,
                jaw_x=(-11.0, 11.0),
                jaw_y=(-19.0, 19.0),
                mlcx1=[-13.0 + value for value in range(60)],
                mlcx2=[-12.5 + value for value in range(58)],
                private_1004=-164.259262084,
                private_1005=None,
                direction="CW",
                include_mlcx2=include_mlcx2,
            ),
        ][:control_point_count]
    )
    return beam


def build_fake_control_point(
    *,
    index: int,
    angle: float,
    axial: float,
    meterset_weight: float,
    jaw_x: tuple[float, float],
    jaw_y: tuple[float, float],
    mlcx1: list[float],
    mlcx2: list[float],
    private_1004: float,
    private_1005: tuple[float, float, float] | None,
    direction: str,
    include_mlcx2: bool,
) -> Dataset:
    control_point = Dataset()
    control_point.ControlPointIndex = index
    control_point.GantryAngle = angle
    control_point.GantryRotationDirection = direction
    control_point.DoseRateSet = 600.0 + index * 10.0
    control_point.CumulativeMetersetWeight = meterset_weight
    control_point.IsocenterPosition = [-6.775, -218.05, axial]
    control_point.BeamLimitingDevicePositionSequence = Sequence(
        [
            build_device_position("ASYMX", jaw_x),
            build_device_position("ASYMY", jaw_y),
            build_device_position("MLCX1", mlcx1),
        ]
        + ([build_device_position("MLCX2", mlcx2)] if include_mlcx2 else [])
    )
    control_point.add_new((0x4001, 0x1004), "DS", str(private_1004))
    if private_1005 is not None:
        control_point.add_new((0x4001, 0x1005), "DS", [str(value) for value in private_1005])
    return control_point


def build_device_position(device_type: str, values: tuple[float, float] | list[float]) -> Dataset:
    item = Dataset()
    item.RTBeamLimitingDeviceType = device_type
    item.LeafJawPositions = [str(value) for value in values]
    return item


class AuroraParserTests(unittest.TestCase):
    def test_detects_aurora_dual_layer_dynamic_plan(self):
        dataset = build_fake_aurora_rtplan()

        self.assertTrue(is_aurora_rtplan(dataset))

        parsed = parse_aurora_rtplan(dataset)

        self.assertEqual(parsed.metadata.manufacturer, "WisdomTech Medical Systems")
        self.assertEqual(parsed.metadata.manufacturer_model_name, "DeepPlan")
        self.assertEqual(parsed.metadata.beam_count, 1)
        self.assertEqual(len(parsed.beams), 1)

    def test_rejects_manufacturer_hint_without_dual_layer_dynamic_beam(self):
        dataset = build_fake_aurora_rtplan(include_mlcx2=False)

        self.assertFalse(is_aurora_rtplan(dataset))
        with self.assertRaisesRegex(ValueError, "Aurora"):
            parse_aurora_rtplan(dataset)

    def test_rejects_dynamic_label_without_actual_dynamic_control_point_evidence(self):
        dataset = build_fake_aurora_rtplan(dynamic_motion=False)

        self.assertFalse(is_aurora_rtplan(dataset))
        with self.assertRaisesRegex(ValueError, "Aurora"):
            parse_aurora_rtplan(dataset)

    def test_rejects_incompatible_manufacturer_and_model_hints_even_with_matching_geometry(self):
        dataset = build_fake_aurora_rtplan(
            manufacturer="Other Vendor",
            manufacturer_model_name="OtherPlan",
        )

        self.assertFalse(is_aurora_rtplan(dataset))
        with self.assertRaisesRegex(ValueError, "Aurora"):
            parse_aurora_rtplan(dataset)

    def test_rejects_setup_only_beams(self):
        dataset = build_fake_aurora_rtplan(treatment_delivery_type="SETUP")

        self.assertFalse(is_aurora_rtplan(dataset))
        with self.assertRaisesRegex(ValueError, "Aurora"):
            parse_aurora_rtplan(dataset)

    def test_parses_control_point_fields_and_observed_angle_deltas(self):
        dataset = build_fake_aurora_rtplan()

        parsed = parse_aurora_rtplan(dataset)
        beam = parsed.beams[0]
        first_cp = beam.control_points[0]
        second_cp = beam.control_points[1]

        self.assertEqual(first_cp.gantry_angle_deg, 0.0)
        self.assertEqual(second_cp.gantry_angle_deg, 356.0)
        self.assertEqual(first_cp.dose_rate_mu_per_min, 600.0)
        self.assertEqual(second_cp.cumulative_meterset_weight, 0.5)
        self.assertEqual(first_cp.isocenter_position_mm, (-6.775, -218.05, -60.25))
        self.assertAlmostEqual(second_cp.axial_position_mm, -60.620368958)
        self.assertEqual(first_cp.jaw_x, (-10.0, 10.0))
        self.assertEqual(first_cp.jaw_y, (-20.0, 20.0))
        self.assertEqual(len(first_cp.mlc_x1_positions_mm), 60)
        self.assertEqual(len(first_cp.mlc_x2_positions_mm), 58)
        self.assertEqual(first_cp.private_wistech_4001_1004["value"], -165.0)
        self.assertEqual(first_cp.private_wistech_4001_1005["values"], (-6.775, -218.05, -135.25))
        self.assertEqual(second_cp.private_wistech_4001_1005["values"], (-6.775, -218.05, -135.25))
        self.assertEqual(reconstruct_observed_angle_deltas(beam), [-4.0, -4.0])

    def test_wrap_angle_delta_uses_actual_angle_sequence(self):
        self.assertEqual(wrap_angle_delta(356.0, 352.0), -4.0)
        self.assertEqual(wrap_angle_delta(358.0, 2.0), 4.0)
        self.assertEqual(wrap_angle_delta(2.0, 358.0), -4.0)

    def test_malformed_numeric_strings_do_not_crash_tuple_conversion(self):
        self.assertEqual(_to_float_tuple("bad\\data"), ())
        self.assertEqual(_to_float_tuple(["1.0", "bad"]), ())

    @unittest.skipUnless(REAL_SAMPLE_PATH and REAL_SAMPLE_PATH.exists(), f"Set {REAL_SAMPLE_ENV} to a valid Aurora RTPLAN path")
    def test_real_sample_matches_known_aurora_shape(self):
        parsed = parse_aurora_rtplan(REAL_SAMPLE_PATH)

        self.assertEqual(parsed.metadata.manufacturer, "WisdomTech Medical Systems")
        self.assertEqual(parsed.metadata.manufacturer_model_name, "DeepPlan")
        self.assertEqual(parsed.metadata.beam_count, 2)
        self.assertEqual([len(beam.control_points) for beam in parsed.beams], [406, 406])
        self.assertEqual(len(parsed.beams[0].control_points[0].mlc_x1_positions_mm), 60)
        self.assertEqual(len(parsed.beams[0].control_points[0].mlc_x2_positions_mm), 58)
        self.assertNotEqual(parsed.beams[0].control_points[0].axial_position_mm, parsed.beams[0].control_points[-1].axial_position_mm)


if __name__ == "__main__":
    unittest.main()
