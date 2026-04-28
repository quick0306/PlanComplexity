import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from validation_models import (
    ReferenceCaseProvenanceRecord,
    ReferenceCaseRecord,
    ValidationCaseResult,
)


class FreezeReferenceOutputsTests(unittest.TestCase):
    def test_freeze_case_rejects_checksum_mismatch_before_overwrite(self):
        from tools.freeze_reference_outputs import freeze_case

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = root / "data" / "demo_case.dcm"
            source_path.parent.mkdir(parents=True)
            source_path.write_bytes(b"demo")
            output_path = root / "expected_metrics.json"

            case = ReferenceCaseRecord(
                case_id="demo",
                source_path="data/demo_case.dcm",
                domain="AURORA",
                device_or_tps="Aurora",
                expected_mode="AURORA",
                case_class="canonical",
                expected_metrics_source="checked_in_json",
                expected_metrics_path=output_path,
                expected_metrics={},
                tolerance_overrides={},
                checksum="deadbeef",
                provenance=ReferenceCaseProvenanceRecord(
                    source_kind="synthetic",
                    version="test",
                    notes="",
                ),
                notes="",
            )

            with patch("tools.freeze_reference_outputs.analyze_validation_case") as analyze_validation_case:
                with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
                    freeze_case(case, source_root=root)
            analyze_validation_case.assert_not_called()

    def test_freeze_case_requires_explicit_source_root_when_source_file_is_missing(self):
        from tools.freeze_reference_outputs import freeze_case

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output_path = root / "expected_metrics.json"
            case = ReferenceCaseRecord(
                case_id="demo",
                source_path="data/demo_case.dcm",
                domain="AURORA",
                device_or_tps="Aurora",
                expected_mode="AURORA",
                case_class="canonical",
                expected_metrics_source="checked_in_json",
                expected_metrics_path=output_path,
                expected_metrics={},
                tolerance_overrides={},
                checksum="deadbeef",
                provenance=ReferenceCaseProvenanceRecord(
                    source_kind="synthetic",
                    version="test",
                    notes="",
                ),
                notes="",
            )

            with self.assertRaisesRegex(FileNotFoundError, "Could not resolve"):
                freeze_case(case, source_root=root)

    def test_freeze_case_writes_metrics_when_source_root_and_checksum_match(self):
        from tools.freeze_reference_outputs import freeze_case

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_path = root / "data" / "demo_case.dcm"
            source_path.parent.mkdir(parents=True)
            source_path.write_bytes(b"demo")
            output_path = root / "expected_metrics.json"
            checksum = hashlib.sha256(source_path.read_bytes()).hexdigest()

            case = ReferenceCaseRecord(
                case_id="demo",
                source_path="data/demo_case.dcm",
                domain="AURORA",
                device_or_tps="Aurora",
                expected_mode="AURORA",
                case_class="canonical",
                expected_metrics_source="checked_in_json",
                expected_metrics_path=output_path,
                expected_metrics={},
                tolerance_overrides={},
                checksum=checksum,
                provenance=ReferenceCaseProvenanceRecord(
                    source_kind="synthetic",
                    version="test",
                    notes="",
                ),
                notes="",
            )
            fake_result = ValidationCaseResult(
                source_path=str(source_path),
                domain="AURORA",
                mode="AURORA",
                supported=True,
                reason="",
                metadata={},
                metrics={"projection_pitch_mean": 1.25},
                warnings=(),
            )

            with patch("tools.freeze_reference_outputs.analyze_validation_case", return_value=fake_result):
                freeze_case(case, source_root=root)

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual({"projection_pitch_mean": 1.25}, payload)


if __name__ == "__main__":
    unittest.main()
