import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader


class AuroraFormulaPdfTests(unittest.TestCase):
    def test_export_function_writes_pdf_with_v2_v3_main_body_and_legacy_appendix(self):
        from aurora_svmat_lab.formula_pdf import export_aurora_formula_pdf

        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "aurora_metric_formulas.pdf"

            export_aurora_formula_pdf(pdf_path)

            self.assertTrue(pdf_path.exists())
            self.assertGreater(pdf_path.stat().st_size, 0)

            reader = PdfReader(str(pdf_path))
            extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages)

            self.assertIn("Aurora SVMAT Metric Formula Reference", extracted_text)
            self.assertIn("Section 1. V2 Metrics", extracted_text)
            self.assertIn("projection_pitch_mean", extracted_text)
            self.assertIn("Section 2. V3 Research Metrics", extracted_text)
            self.assertIn("reversal_symmetry_index", extracted_text)
            self.assertIn("small_opening_fraction", extracted_text)
            self.assertIn("layer_correlation_index", extracted_text)
            self.assertIn("Appendix A. Legacy Engineering Metrics", extracted_text)
            self.assertIn("coupled_modulation_index", extracted_text)

    def test_cli_entrypoint_writes_requested_pdf_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "aurora_metric_formulas.pdf"

            completed = subprocess.run(
                [
                    sys.executable,
                    "tools/export_aurora_formula_pdf.py",
                    "--output-path",
                    str(pdf_path),
                ],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(pdf_path.exists())
            self.assertGreater(pdf_path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
