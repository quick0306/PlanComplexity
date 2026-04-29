import unittest

from validation.utils.loaders import load_metric_specs, load_reference_manifest


# These paper metrics must be in expected_metrics so exact validation catches formula drift.
HALCYON_PAPER_KEYS = {
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
}


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

    def test_halcyon_paper_metrics_are_reference_gated(self):
        specs = {
            (spec.platform, spec.metric_key): spec
            for spec in load_metric_specs()
        }
        halcyon_case = next(
            case
            for case in load_reference_manifest()
            if case.case_id == "vmat_halcyon_edge"
        )

        missing_expected = HALCYON_PAPER_KEYS - set(halcyon_case.expected_metrics)
        self.assertEqual(set(), missing_expected)
        for metric_key in HALCYON_PAPER_KEYS:
            with self.subTest(metric_key=metric_key):
                spec = specs[("VMAT_IMRT", metric_key)]
                self.assertEqual("Reference-case exact", spec.validation_level)
                self.assertEqual("exact-equivalent", spec.comparison_class)


if __name__ == "__main__":
    unittest.main()
