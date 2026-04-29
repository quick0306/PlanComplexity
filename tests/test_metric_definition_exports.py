import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class MetricDefinitionExportTests(unittest.TestCase):
    def test_catalog_contains_all_supported_platforms_and_key_metrics(self):
        from metric_definition_catalog import build_metric_definition_catalog

        records = build_metric_definition_catalog()

        platforms = {record.platform for record in records}
        metric_keys = {record.metric_key for record in records}

        self.assertTrue({"VMAT_IMRT", "TOMO", "CYBERKNIFE_MLC", "AURORA"}.issubset(platforms))
        self.assertIn("mcsv", metric_keys)
        self.assertIn("mi", metric_keys)
        self.assertIn("sas10", metric_keys)
        self.assertIn("projection_pitch_mean", metric_keys)
        self.assertIn("reversal_symmetry_index", metric_keys)
        self.assertIn("small_opening_fraction", metric_keys)
        self.assertIn("projection_leaf_travel_max", metric_keys)
        self.assertIn("head_mu_density_mean_proxy", metric_keys)
        self.assertIn("layer_correlation_index", metric_keys)

        representative = next(record for record in records if record.metric_key == "projection_pitch_mean")
        self.assertTrue(representative.mathematical_definition)
        self.assertTrue(representative.physical_meaning)
        v3_representative = next(record for record in records if record.metric_key == "reversal_symmetry_index")
        self.assertEqual(v3_representative.group, "V3 bidirectional symmetry")
        self.assertTrue(v3_representative.mathematical_definition)
        self.assertTrue(v3_representative.physical_meaning)

    def test_export_script_writes_csv_and_markdown(self):
        from metric_definition_catalog import export_metric_definitions

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            csv_path = temp_path / "metric_definitions_all.csv"
            md_path = temp_path / "metric_definitions_all.md"

            export_metric_definitions(csv_path=csv_path, markdown_path=md_path)

            self.assertTrue(csv_path.exists())
            self.assertTrue(md_path.exists())

            with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))

            self.assertGreater(len(rows), 20)
            self.assertIn("platform", rows[0])
            self.assertIn("mathematical_definition", rows[0])
            self.assertIn("physical_meaning", rows[0])
            self.assertTrue(any(row["metric_key"] == "projection_pitch_mean" for row in rows))
            self.assertTrue(any(row["metric_key"] == "mcsv" for row in rows))

            markdown_text = md_path.read_text(encoding="utf-8")
            self.assertIn("# Metric Definitions", markdown_text)
            self.assertIn("## VMAT/IMRT", markdown_text)
            self.assertIn("## TOMO", markdown_text)
            self.assertIn("## CyberKnife MLC", markdown_text)
            self.assertIn("## Aurora SVMAT Lab", markdown_text)
            self.assertIn("projection_pitch_mean", markdown_text)
            self.assertIn("reversal_symmetry_index", markdown_text)
            self.assertIn("small_opening_fraction", markdown_text)
            self.assertIn("layer_correlation_index", markdown_text)

            appendix_paths = {
                "VMAT/IMRT": temp_path / "metric_definitions_vmat_imrt.md",
                "TOMO": temp_path / "metric_definitions_tomo.md",
                "CyberKnife MLC": temp_path / "metric_definitions_cyberknife_mlc.md",
                "Aurora SVMAT Lab": temp_path / "metric_definitions_aurora.md",
            }
            for section_name, appendix_path in appendix_paths.items():
                self.assertTrue(appendix_path.exists(), f"missing appendix for {section_name}")
                appendix_text = appendix_path.read_text(encoding="utf-8")
                self.assertIn(f"# {section_name} Metric Definitions", appendix_text)
            aurora_appendix = (temp_path / "metric_definitions_aurora.md").read_text(encoding="utf-8")
            self.assertIn("V3 bidirectional symmetry", aurora_appendix)
            self.assertIn("small_opening_fraction", aurora_appendix)
            self.assertIn("head_mu_density_mean_proxy", aurora_appendix)

    def test_export_script_runs_from_tools_directory_entrypoint(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            csv_path = temp_path / "metric_definitions_all.csv"
            md_path = temp_path / "metric_definitions_all.md"

            completed = subprocess.run(
                [
                    sys.executable,
                    "tools/export_metric_definitions.py",
                    "--csv-path",
                    str(csv_path),
                    "--markdown-path",
                    str(md_path),
                ],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(csv_path.exists())
            self.assertTrue(md_path.exists())
            self.assertTrue((temp_path / "metric_definitions_vmat_imrt.md").exists())
            self.assertTrue((temp_path / "metric_definitions_tomo.md").exists())
            self.assertTrue((temp_path / "metric_definitions_cyberknife_mlc.md").exists())
            self.assertTrue((temp_path / "metric_definitions_aurora.md").exists())


if __name__ == "__main__":
    unittest.main()
