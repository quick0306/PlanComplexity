import unittest
from unittest.mock import patch

from DicomParse.dicom_rt import RTPlan


class MockDataset(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError as exc:
            raise AttributeError(item) from exc


def make_plan_dataset(**overrides):
    data = {
        "RTPlanLabel": "LBL1",
        "RTPlanName": "Plan One",
        "PatientName": "Alice",
        "PatientID": "P001",
        "ManufacturerModelName": "AAA",
        "StudyDescription": "Study",
        "SeriesInstanceUID": "SERIES-1",
    }
    data.update(overrides)
    return MockDataset(data)


class RTPlanGetPlanTests(unittest.TestCase):
    def build_rtplan(self, dataset):
        rtplan = object.__new__(RTPlan)
        rtplan.plan = {}
        rtplan.ds = dataset
        return rtplan

    def test_get_plan_sets_rotation_direction_when_all_beams_match(self):
        rtplan = self.build_rtplan(make_plan_dataset())
        beams = {
            1: {"MU": 100.0, "TreatmentMachineName": "TB", "BeamType": "DYNAMIC", "GantryRotationDirection": "CW"},
            2: {"MU": 50.0, "TreatmentMachineName": "TB", "BeamType": "DYNAMIC", "GantryRotationDirection": "CW"},
        }

        with patch.object(RTPlan, "get_beams", return_value=beams), patch.object(
            RTPlan, "get_study_info", return_value={"description": "Study"}
        ):
            plan = rtplan.to_plan_dict()

        self.assertEqual(plan["rotation_direction"], "CW")
        self.assertEqual(plan["Plan_MU"], 150.0)
        self.assertEqual(plan["beam_number"], 2)
        self.assertEqual(plan["machine_id"], "TB")

    def test_get_plan_marks_mixed_rotation_direction(self):
        rtplan = self.build_rtplan(make_plan_dataset())
        beams = {
            1: {"MU": 80.0, "TreatmentMachineName": "TB", "BeamType": "DYNAMIC", "GantryRotationDirection": "CW"},
            2: {"MU": 70.0, "TreatmentMachineName": "TB", "BeamType": "DYNAMIC", "GantryRotationDirection": "CC"},
        }

        with patch.object(RTPlan, "get_beams", return_value=beams), patch.object(
            RTPlan, "get_study_info", return_value={"description": "Study"}
        ):
            plan = rtplan.to_plan_dict()

        self.assertEqual(plan["rotation_direction"], "MIXED")

    def test_get_plan_falls_back_when_rotation_direction_missing(self):
        dataset = make_plan_dataset()
        del dataset["RTPlanName"]
        rtplan = self.build_rtplan(dataset)
        beams = {
            1: {"MU": 90.0, "TreatmentMachineName": "TB", "BeamType": "STATIC"},
        }

        with patch.object(RTPlan, "get_beams", return_value=beams), patch.object(
            RTPlan, "get_study_info", return_value={"description": "Study"}
        ):
            plan = rtplan.to_plan_dict()

        self.assertEqual(plan["plan_name"], "LBL1")
        self.assertEqual(plan["rotation_direction"], "")
        self.assertEqual(plan["beam_type"], "STATIC")


if __name__ == "__main__":
    unittest.main()


