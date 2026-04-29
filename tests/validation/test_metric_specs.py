import unittest
from collections import Counter, defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory

from metric_definition_catalog import build_metric_group_catalog, metric_catalog_keys
from validation.utils import loaders


_CHECKED_IN_SPECS_DIR = Path(__file__).resolve().parents[2] / "validation" / "specs"
_VALIDATION_LEVELS = {
    "Formula-exact",
    "Reference-case exact",
    "Derived-equivalent",
    "Association-only",
}
_COMPARISON_CLASSES = {
    "exact-equivalent",
    "derived-equivalent",
    "association-only",
    "not-comparable",
}


class MetricSpecInventoryTests(unittest.TestCase):
    def test_checked_in_metric_specs_match_catalog_groups_and_research_profile(self):
        expected_metric_keys = metric_catalog_keys()
        expected_groups = {
            (group.group_key, group.platform, group.group_label)
            for group in build_metric_group_catalog()
        }

        metric_specs = loaders.load_metric_specs()
        metric_spec_map = {
            (record.platform, record.metric_key): record for record in metric_specs
        }
        self.assertEqual(
            expected_metric_keys,
            {(record.platform, record.metric_key) for record in metric_specs},
        )
        for record in metric_specs:
            self.assertEqual(record.platform, record.mode)
            self.assertTrue(record.group_key)
            self.assertTrue(record.label)
            self.assertTrue(record.aggregation_scope)
            self.assertTrue(record.normalization_basis)
            self.assertIn(record.validation_level, _VALIDATION_LEVELS)
            self.assertIn(record.comparison_class, _COMPARISON_CLASSES)
            self.assertTrue(record.expected_range.kind)
            self.assertEqual("research", record.clinical_readiness)
            self.assertIsInstance(record.known_noncomparability, tuple)
            self.assertIsInstance(record.comparable_to, tuple)
            if record.expected_range.kind == "unit_interval":
                self.assertEqual(0.0, record.expected_range.minimum)
                self.assertEqual(1.0, record.expected_range.maximum)
                self.assertIn(record.unit, {"proportion", "dimensionless"})
            if record.unit in {"mm/MU", "mm/(leaf*deg)"}:
                self.assertEqual("nonnegative", record.expected_range.kind)
        self.assertEqual(
            "nonnegative",
            metric_spec_map[("VMAT_IMRT", "fraction_dose_gy")].expected_range.kind,
        )
        self.assertEqual(
            "nonnegative",
            metric_spec_map[("VMAT_IMRT", "fractions_count")].expected_range.kind,
        )

        metric_groups = loaders.load_metric_groups()
        group_map = {group.group_key: group for group in metric_groups}
        self.assertEqual(len(metric_groups), len(group_map))
        self.assertEqual(
            expected_groups,
            {(group.group_key, group.platform, group.label) for group in metric_groups},
        )
        expected_group_metrics = defaultdict(list)
        for record in metric_specs:
            expected_group_metrics[record.group_key].append(record.metric_key)
        for group in metric_groups:
            self.assertEqual(sorted(expected_group_metrics[group.group_key]), list(group.metric_keys))

        validation_profiles = loaders.load_validation_profiles()
        profile_map = {profile.profile_key: profile for profile in validation_profiles}
        self.assertEqual(len(validation_profiles), len(profile_map))

        research_profile = profile_map["research"]
        self.assertAlmostEqual(1.0e-6, research_profile.exact_abs_default)
        self.assertAlmostEqual(1.0e-4, research_profile.exact_rel_default)
        self.assertTrue(research_profile.require_reference_exact_green)
        self.assertFalse(research_profile.include_association_only_in_core_gate)
        self.assertEqual(set(group_map), set(research_profile.group_keys))

    def test_metric_groups_yaml_uses_logical_family_groups(self):
        group_text = (_CHECKED_IN_SPECS_DIR / "metric_groups.yaml").read_text(encoding="utf-8")

        self.assertIn("label", group_text)
        self.assertNotIn("metric_keys", group_text)
        self.assertNotRegex(group_text, r"_all\\b")

        platform_group_counts = Counter(group.platform for group in loaders.load_metric_groups())
        self.assertGreater(platform_group_counts["VMAT_IMRT"], 1)
        self.assertGreater(platform_group_counts["TOMO"], 1)
        self.assertGreater(platform_group_counts["AURORA"], 1)

    def test_loaders_parse_rich_yaml_and_expand_group_metric_keys_from_metric_specs(self):
        with TemporaryDirectory() as temp_dir:
            specs_dir = Path(temp_dir)
            (specs_dir / "metric_specs.yaml").write_text(
                """
                metric_specs:
                  - platform: VMAT_IMRT
                    mode: VMAT_IMRT
                    group_key: vmat_imrt_aperture_geometry
                    key: alpha
                    metric_key: alpha
                    label: Alpha
                    unit: dimensionless
                    aggregation_scope: plan
                    normalization_basis: beam_weighted_mean
                    validation_level: Reference-case exact
                    comparison_class: exact-equivalent
                    default_tolerance_abs: 1.0e-6
                    default_tolerance_rel: 1.0e-4
                    expected_range:
                      kind: unit_interval
                      minimum: 0.0
                      maximum: 1.0
                    clinical_readiness: research
                    known_noncomparability: []
                    comparable_to:
                      - UCoMX:ApertureGeometry:alpha
                    assumptions:
                      - valid plan geometry
                    exclusions: []
                  - platform: VMAT_IMRT
                    mode: VMAT_IMRT
                    group_key: vmat_imrt_aperture_geometry
                    key: beta
                    metric_key: beta
                    label: Beta
                    unit: mm
                    aggregation_scope: plan
                    normalization_basis: implementation_defined
                    validation_level: Derived-equivalent
                    comparison_class: derived-equivalent
                    default_tolerance_abs: null
                    default_tolerance_rel: null
                    expected_range:
                      kind: nonnegative
                      minimum: 0.0
                      maximum: null
                    clinical_readiness: research
                    known_noncomparability:
                      - comparator-specific normalization
                    comparable_to: []
                    assumptions: []
                    exclusions:
                      - comparator-specific normalization
                  - platform: TOMO
                    mode: TOMO
                    group_key: tomo_delivery
                    key: gamma
                    metric_key: gamma
                    label: Gamma
                    unit: s
                    aggregation_scope: plan
                    normalization_basis: implementation_defined
                    validation_level: Reference-case exact
                    comparison_class: exact-equivalent
                    default_tolerance_abs: 1.0e-6
                    default_tolerance_rel: 1.0e-4
                    expected_range:
                      kind: nonnegative
                      minimum: 0.0
                      maximum: null
                    clinical_readiness: research
                    known_noncomparability: []
                    comparable_to:
                      - TCoMX:Delivery:gamma
                    assumptions: []
                    exclusions: []
                """.strip(),
                encoding="utf-8",
            )
            (specs_dir / "metric_groups.yaml").write_text(
                """
                metric_groups:
                  - group_key: vmat_imrt_aperture_geometry
                    platform: VMAT_IMRT
                    label: Aperture geometry
                    description: Example VMAT family.
                  - group_key: tomo_delivery
                    platform: TOMO
                    label: Delivery
                    description: Example Tomo family.
                """.strip(),
                encoding="utf-8",
            )
            (specs_dir / "validation_profiles.yaml").write_text(
                """
                validation_profiles:
                  - profile_key: research
                    description: Example research profile.
                    exact_abs_default: 1.0e-6
                    exact_rel_default: 1.0e-4
                    require_reference_exact_green: true
                    include_association_only_in_core_gate: false
                    group_keys:
                      - vmat_imrt_aperture_geometry
                      - tomo_delivery
                """.strip(),
                encoding="utf-8",
            )

            original_specs_dir = loaders._SPECS_DIR
            loaders._SPECS_DIR = specs_dir
            try:
                metric_specs = {
                    (record.platform, record.metric_key): record
                    for record in loaders.load_metric_specs()
                }
                alpha = metric_specs[("VMAT_IMRT", "alpha")]
                beta = metric_specs[("VMAT_IMRT", "beta")]
                self.assertEqual("Alpha", alpha.label)
                self.assertEqual("VMAT_IMRT", alpha.mode)
                self.assertEqual("unit_interval", alpha.expected_range.kind)
                self.assertEqual(("valid plan geometry",), alpha.assumptions)
                self.assertEqual(("UCoMX:ApertureGeometry:alpha",), alpha.comparable_to)
                self.assertEqual(("comparator-specific normalization",), beta.known_noncomparability)
                self.assertEqual(("comparator-specific normalization",), beta.exclusions)
                self.assertEqual("Derived-equivalent", beta.validation_level)

                metric_groups = {group.group_key: group for group in loaders.load_metric_groups()}
                self.assertEqual(("alpha", "beta"), metric_groups["vmat_imrt_aperture_geometry"].metric_keys)
                self.assertEqual("Aperture geometry", metric_groups["vmat_imrt_aperture_geometry"].label)
                self.assertEqual(("gamma",), metric_groups["tomo_delivery"].metric_keys)

                research_profile = {profile.profile_key: profile for profile in loaders.load_validation_profiles()}["research"]
                self.assertAlmostEqual(1.0e-6, research_profile.exact_abs_default)
                self.assertAlmostEqual(1.0e-4, research_profile.exact_rel_default)
                self.assertTrue(research_profile.require_reference_exact_green)
                self.assertFalse(research_profile.include_association_only_in_core_gate)
                self.assertEqual(
                    ("vmat_imrt_aperture_geometry", "tomo_delivery"),
                    research_profile.group_keys,
                )
            finally:
                loaders._SPECS_DIR = original_specs_dir

    def test_loaders_fail_fast_on_definition_errors_with_context(self):
        with TemporaryDirectory() as temp_dir:
            specs_dir = Path(temp_dir)
            (specs_dir / "metric_specs.yaml").write_text(
                """
                metric_specs:
                  - platform: VMAT_IMRT
                    mode: VMAT_IMRT
                    group_key: vmat_imrt_aperture_geometry
                    key: alpha
                    metric_key: alpha
                    label: Alpha
                    unit: dimensionless
                    aggregation_scope: plan
                    normalization_basis: beam_weighted_mean
                    validation_level: Reference-case exact
                    comparison_class: exact-equivalent
                    default_tolerance_abs: 1.0e-6
                    default_tolerance_rel: 1.0e-4
                    expected_range:
                      kind: unit_interval
                      minimum: 0.0
                      maximum: 1.0
                    clinical_readiness: research
                    known_noncomparability: []
                    comparable_to: []
                    assumptions: []
                    exclusions: []
                  - platform: VMAT_IMRT
                    mode: VMAT_IMRT
                    group_key: vmat_imrt_aperture_geometry
                    key: alpha
                    metric_key: alpha
                    label: Alpha duplicate
                    unit: dimensionless
                    aggregation_scope: plan
                    normalization_basis: beam_weighted_mean
                    validation_level: Reference-case exact
                    comparison_class: exact-equivalent
                    default_tolerance_abs: 1.0e-6
                    default_tolerance_rel: 1.0e-4
                    expected_range:
                      kind: unit_interval
                      minimum: 0.0
                      maximum: 1.0
                    clinical_readiness: research
                    known_noncomparability: []
                    comparable_to: []
                    assumptions: []
                    exclusions: []
                """.strip(),
                encoding="utf-8",
            )
            (specs_dir / "metric_groups.yaml").write_text(
                """
                metric_groups:
                  - group_key: vmat_imrt_aperture_geometry
                    platform: VMAT_IMRT
                    label: Aperture geometry
                    description: Example VMAT family.
                  - group_key: tomo_delivery
                    platform: TOMO
                    label: Delivery
                    description: Example Tomo family.
                """.strip(),
                encoding="utf-8",
            )
            (specs_dir / "validation_profiles.yaml").write_text(
                """
                validation_profiles:
                  - profile_key: research
                    description: Example profile.
                    exact_abs_default: 1.0e-6
                    exact_rel_default: 1.0e-4
                    require_reference_exact_green: true
                    include_association_only_in_core_gate: false
                    group_keys:
                      - missing_group
                  - profile_key: research
                    description: Example profile duplicate.
                    exact_abs_default: 1.0e-6
                    exact_rel_default: 1.0e-4
                    require_reference_exact_green: true
                    include_association_only_in_core_gate: false
                    group_keys:
                      - missing_group
                """.strip(),
                encoding="utf-8",
            )

            original_specs_dir = loaders._SPECS_DIR
            loaders._SPECS_DIR = specs_dir
            try:
                with self.assertRaisesRegex(ValueError, "Duplicate metric spec key entries"):
                    loaders.load_metric_specs()

                (specs_dir / "metric_specs.yaml").write_text(
                    """
                    metric_specs:
                      - platform: VMAT_IMRT
                        mode: VMAT_IMRT
                        group_key: missing_group
                        key: alpha
                        metric_key: alpha
                        label: Alpha
                        unit: dimensionless
                        aggregation_scope: plan
                        normalization_basis: beam_weighted_mean
                        validation_level: Reference-case exact
                        comparison_class: exact-equivalent
                        default_tolerance_abs: 1.0e-6
                        default_tolerance_rel: 1.0e-4
                        expected_range:
                          kind: unit_interval
                          minimum: 0.0
                          maximum: 1.0
                        clinical_readiness: research
                        known_noncomparability: []
                        comparable_to: []
                        assumptions: []
                        exclusions: []
                    """.strip(),
                    encoding="utf-8",
                )
                (specs_dir / "metric_groups.yaml").write_text(
                    """
                    metric_groups:
                      - group_key: vmat_imrt_aperture_geometry
                        platform: VMAT_IMRT
                        label: Aperture geometry
                        description: Example VMAT family.
                      - group_key: vmat_imrt_aperture_geometry
                        platform: VMAT_IMRT
                        label: Aperture geometry duplicate
                        description: Example VMAT family.
                    """.strip(),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "Duplicate metric group entries"):
                    loaders.load_metric_groups()

                (specs_dir / "metric_groups.yaml").write_text(
                    """
                    metric_groups:
                      - group_key: vmat_imrt_aperture_geometry
                        platform: TOMO
                        label: Aperture geometry
                        description: Wrong platform on purpose.
                    """.strip(),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "unknown metric group"):
                    loaders.load_metric_groups()

                (specs_dir / "metric_groups.yaml").write_text(
                    """
                    metric_groups:
                      - group_key: vmat_imrt_aperture_geometry
                        platform: VMAT_IMRT
                        label: Aperture geometry
                        description: Example VMAT family.
                    """.strip(),
                    encoding="utf-8",
                )
                (specs_dir / "metric_specs.yaml").write_text(
                    """
                    metric_specs:
                      - platform: VMAT_IMRT
                        mode: TOMO
                        group_key: vmat_imrt_aperture_geometry
                        key: alpha
                        metric_key: alpha
                        label: Alpha
                        unit: dimensionless
                        aggregation_scope: plan
                        normalization_basis: beam_weighted_mean
                        validation_level: Reference-case exact
                        comparison_class: exact-equivalent
                        default_tolerance_abs: 1.0e-6
                        default_tolerance_rel: 1.0e-4
                        expected_range:
                          kind: unit_interval
                          minimum: 0.0
                          maximum: 1.0
                        clinical_readiness: research
                        known_noncomparability: []
                        comparable_to: []
                        assumptions: []
                        exclusions: []
                    """.strip(),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "mode mismatch"):
                    loaders.load_metric_groups()

                (specs_dir / "metric_specs.yaml").write_text(
                    """
                    metric_specs:
                      - platform: VMAT_IMRT
                        mode: VMAT_IMRT
                        group_key: vmat_imrt_aperture_geometry
                        key: alpha
                        metric_key: alpha
                        label: Alpha
                        unit: dimensionless
                        aggregation_scope: plan
                        normalization_basis: beam_weighted_mean
                        validation_level: Reference-case exact
                        comparison_class: exact-equivalent
                        default_tolerance_abs: 1.0e-6
                        default_tolerance_rel: 1.0e-4
                        expected_range:
                          kind: impossible_kind
                          minimum: 0.0
                          maximum: 1.0
                        clinical_readiness: research
                        known_noncomparability: []
                        comparable_to: []
                        assumptions: []
                        exclusions: []
                    """.strip(),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "not one of"):
                    loaders.load_metric_groups()

                (specs_dir / "metric_groups.yaml").write_text(
                    """
                    metric_groups:
                      - group_key: vmat_imrt_aperture_geometry
                        platform: VMAT_IMRT
                        label: Aperture geometry
                        description: Example VMAT family.
                    """.strip(),
                    encoding="utf-8",
                )
                (specs_dir / "metric_specs.yaml").write_text(
                    """
                    metric_specs:
                      - platform: VMAT_IMRT
                        mode: VMAT_IMRT
                        group_key: vmat_imrt_aperture_geometry
                        key: alpha
                        metric_key: alpha
                        label: Alpha
                        unit: dimensionless
                        aggregation_scope: plan
                        normalization_basis: beam_weighted_mean
                        validation_level: Reference-case exact
                        comparison_class: exact-equivalent
                        default_tolerance_abs: 1.0e-6
                        default_tolerance_rel: 1.0e-4
                        expected_range:
                          kind: unit_interval
                          minimum: -2.0
                          maximum: 5.0
                        clinical_readiness: research
                        known_noncomparability: []
                        comparable_to: []
                        assumptions: []
                        exclusions: []
                    """.strip(),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "requires bounds"):
                    loaders.load_metric_groups()

                (specs_dir / "metric_specs.yaml").write_text(
                    """
                    metric_specs:
                      - platform: VMAT_IMRT
                        mode: VMAT_IMRT
                        group_key: vmat_imrt_aperture_geometry
                        key: alpha
                        metric_key: alpha
                        label: Alpha
                        unit: dimensionless
                        aggregation_scope: plan
                        normalization_basis: beam_weighted_mean
                        validation_level: Reference-case exact
                        comparison_class: exact-equivalent
                        default_tolerance_abs: 1.0e-6
                        default_tolerance_rel: 1.0e-4
                        expected_range:
                          kind: nonnegative
                          minimum: -1.0
                          maximum: null
                        clinical_readiness: research
                        known_noncomparability: []
                        comparable_to: []
                        assumptions: []
                        exclusions: []
                    """.strip(),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "requires a minimum of 0.0"):
                    loaders.load_metric_groups()

                (specs_dir / "metric_groups.yaml").write_text(
                    """
                    metric_groups:
                      - group_key: vmat_imrt_aperture_geometry
                        platform: TOMO
                        label: Aperture geometry
                        description: Wrong platform on purpose.
                    """.strip(),
                    encoding="utf-8",
                )
                (specs_dir / "metric_specs.yaml").write_text(
                    """
                    metric_specs:
                      - platform: VMAT_IMRT
                        mode: VMAT_IMRT
                        group_key: vmat_imrt_aperture_geometry
                        key: alpha
                        metric_key: alpha
                        label: Alpha
                        unit: dimensionless
                        aggregation_scope: plan
                        normalization_basis: beam_weighted_mean
                        validation_level: Reference-case exact
                        comparison_class: exact-equivalent
                        default_tolerance_abs: 1.0e-6
                        default_tolerance_rel: 1.0e-4
                        expected_range:
                          kind: unit_interval
                          minimum: 0.0
                          maximum: 1.0
                        clinical_readiness: research
                        known_noncomparability: []
                        comparable_to: []
                        assumptions: []
                        exclusions: []
                    """.strip(),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "platform mismatch"):
                    loaders.load_metric_groups()

                (specs_dir / "metric_groups.yaml").write_text(
                    """
                    metric_groups:
                      - group_key: vmat_imrt_aperture_geometry
                        platform: VMAT_IMRT
                        label: Aperture geometry
                        description: Example VMAT family.
                    """.strip(),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "Duplicate validation profile entries"):
                    loaders.load_validation_profiles()

                (specs_dir / "validation_profiles.yaml").write_text(
                    """
                    validation_profiles:
                      - profile_key: research
                        description: Example profile.
                        exact_abs_default: true
                        exact_rel_default: 1.0e-4
                        require_reference_exact_green: true
                        include_association_only_in_core_gate: false
                        group_keys:
                          - missing_group
                    """.strip(),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "missing required numeric field 'exact_abs_default'"):
                    loaders.load_validation_profiles()

                (specs_dir / "validation_profiles.yaml").write_text(
                    """
                    validation_profiles:
                      - profile_key: research
                        description: Example profile.
                        exact_abs_default: 1.0e-6
                        exact_rel_default: 1.0e-4
                        require_reference_exact_green: true
                        include_association_only_in_core_gate: false
                        group_keys:
                          - missing_group
                    """.strip(),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, "references unknown groups"):
                    loaders.load_validation_profiles()
            finally:
                loaders._SPECS_DIR = original_specs_dir


if __name__ == "__main__":
    unittest.main()
