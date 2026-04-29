import unittest

from validation.utils.loaders import load_reference_manifest


class ReferenceManifestTests(unittest.TestCase):
    def test_manifest_contains_canonical_and_edge_cases_for_each_domain(self):
        manifest = load_reference_manifest()

        self.assertGreaterEqual(len(manifest), 8)
        domain_case_types = {(case.domain, case.case_class) for case in manifest}
        self.assertIn(("VMAT_IMRT", "canonical"), domain_case_types)
        self.assertIn(("VMAT_IMRT", "edge"), domain_case_types)
        self.assertIn(("TOMO", "canonical"), domain_case_types)
        self.assertIn(("TOMO", "edge"), domain_case_types)
        self.assertIn(("CYBERKNIFE_MLC", "canonical"), domain_case_types)
        self.assertIn(("CYBERKNIFE_MLC", "edge"), domain_case_types)
        self.assertIn(("AURORA", "canonical"), domain_case_types)
        self.assertIn(("AURORA", "edge"), domain_case_types)

    def test_manifest_cases_point_at_checked_in_expected_metric_artifacts(self):
        manifest = load_reference_manifest()

        for case in manifest:
            with self.subTest(case_id=case.case_id):
                self.assertEqual("checked_in_json", case.expected_metrics_source)
                self.assertEqual("expected_metrics.json", case.expected_metrics_path.name)
                self.assertTrue(case.expected_metrics_path.exists())


if __name__ == "__main__":
    unittest.main()
