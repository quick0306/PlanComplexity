# Documentation synchronization audit - 2026-10-08

Implementation baseline: `cdc566b` (open-only Aurora update). This change synchronizes documentation and adds a reproducible application-summary PDF exporter; it does not change metric calculation behavior.

## All-platform LaTeX follow-up

Documentation baseline: `1c0d497`. Expanded the update beyond Aurora into five substantive editable Markdown/LaTeX guides: [IMRT/VMAT](vmat_imrt_guide.md), [Halcyon/Ethos](halcyon_ethos_guide.md), [TOMO](tomo_guide.md), [CyberKnife MLC](cyberknife_guide.md), [Aurora V2/V3/legacy/V4](aurora_guide.md). These explain inputs, sampling, weights, geometry, thresholds and missing values against current source and formula contracts. The [complete equation index](metric_math_index.md) maps all 434 registered records, including variants and containers; it does not claim 434 independent scalar formulas or external validation.

The root README, document index, general user guide, current TOMO/Ethos and migration pages link the relevant guides. All five generated definition tables now link every record to the matching equation family. Two new tests enforce family/anchor existence and one-to-one index/appendix coverage. Calculations and existing executable behavior are unchanged. Earlier verification results below describe the preceding documentation revision; fresh results for this follow-up are recorded after verification.

Follow-up verification: full suite 399 passed, 1 skipped, 99 subtests passed (58.07 s). All 60 Markdown files contain 1,619 checked relative link targets with zero broken paths. Final KaTeX strict parsing validated 122 inline/display LaTeX expressions in the five new guides, including the explicit CyberKnife segment-MU normalization. Definition/index export tests were rerun after the final refinement: 7 passed. This validates syntax and navigation, not independent clinical or external numerical equivalence. The generated equation index is also compared byte-for-byte to fresh output by the new coverage test.

## Findings and corrections

- Replaced the candidate Aurora aperture draft with the implemented seven snake_case keys, physical geometry, MU/open-only aggregation, warnings and missing-value semantics.
- Added a Chinese user guide and centralized document index; aligned GUI labels, supported modes, CLI flag boundaries, CSV schemas and build instructions with source.
- Updated the application-summary PDF, which previously omitted Aurora and packaging, and regenerated all metric definitions/contracts and the formula PDF.
- Distinguished current float paths from default rounded VMAT/CyberKnife paths; distinguished the GUI/service column dictionary from standalone Aurora exports.
- Clarified that legacy Aurora reference fixtures cover frozen scalar subsets, rather than validating all seven V4 values; historical evidence remains unchanged.
- Marked historical comparisons, imported research and old plans/specs as historical or deferred. Original commands and observations retain their original dates.

## File-by-file scope

| Document | Disposition |
| --- | --- |
| [README.md](../README.md) | Current guidance or versioned migration; reviewed and synchronized |
| [docs/README.md](README.md) | Current guidance or versioned migration; reviewed and synchronized |
| [docs/aurora_aperture_metrics.md](aurora_aperture_metrics.md) | Current guidance or versioned migration; reviewed and synchronized |
| [docs/aurora_rtplans_comparison.md](aurora_rtplans_comparison.md) | Historical observations; explicit current/history boundary |
| [docs/aurora_v4_migration.md](aurora_v4_migration.md) | Current guidance or versioned migration; reviewed and synchronized |
| [docs/clinical_implementation_sop.md](clinical_implementation_sop.md) | Current guidance or versioned migration; reviewed and synchronized |
| [docs/deepplan_aurora_compatibility.md](deepplan_aurora_compatibility.md) | Current guidance or versioned migration; reviewed and synchronized |
| [docs/deployment_rollback.md](deployment_rollback.md) | Current guidance or versioned migration; reviewed and synchronized |
| [docs/documentation_sync_20261008.md](documentation_sync_20261008.md) | Current guidance or versioned migration; reviewed and synchronized |
| [docs/ethos_report_profile.md](ethos_report_profile.md) | Current guidance or versioned migration; reviewed and synchronized |
| [docs/external_benchmarks.md](external_benchmarks.md) | Historical observations; explicit current/history boundary |
| [docs/geometry_v3_metrics.md](geometry_v3_metrics.md) | Current guidance or versioned migration; reviewed and synchronized |
| [docs/hybrid_v2_metrics.md](hybrid_v2_metrics.md) | Current guidance or versioned migration; reviewed and synchronized |
| [docs/metric_definitions_all.md](metric_definitions_all.md) | Generated from current definition sources; regenerated and checked |
| [docs/metric_definitions_aurora.md](metric_definitions_aurora.md) | Generated from current definition sources; regenerated and checked |
| [docs/metric_definitions_cyberknife_mlc.md](metric_definitions_cyberknife_mlc.md) | Generated from current definition sources; regenerated and checked |
| [docs/metric_definitions_tomo.md](metric_definitions_tomo.md) | Generated from current definition sources; regenerated and checked |
| [docs/metric_definitions_vmat_imrt.md](metric_definitions_vmat_imrt.md) | Generated from current definition sources; regenerated and checked |
| [docs/metric_formula_contracts.md](metric_formula_contracts.md) | Generated from current definition sources; regenerated and checked |
| [docs/metric_surface_audit_20261008.md](metric_surface_audit_20261008.md) | Current guidance or versioned migration; reviewed and synchronized |
| [docs/precision_motion_validation.md](precision_motion_validation.md) | Current guidance or versioned migration; reviewed and synchronized |
| [docs/reference_pack_v1.md](reference_pack_v1.md) | Current guidance or versioned migration; reviewed and synchronized |
| [docs/repository_cleanup.md](repository_cleanup.md) | Historical observations; explicit current/history boundary |
| [docs/research/README.md](research/README.md) | Research/provenance/deferred work; current-guide pointers added |
| [docs/research/analysis_plan.md](research/analysis_plan.md) | Research/provenance/deferred work; current-guide pointers added |
| [docs/research/codebase_comparison_2026-08-11.md](research/codebase_comparison_2026-08-11.md) | Research/provenance/deferred work; current-guide pointers added |
| [docs/research/data_and_migration_provenance.md](research/data_and_migration_provenance.md) | Research/provenance/deferred work; current-guide pointers added |
| [docs/research/github_accuracy_review_2026-09-19.md](research/github_accuracy_review_2026-09-19.md) | Research/provenance/deferred work; current-guide pointers added |
| [docs/research/novelty_and_gap.md](research/novelty_and_gap.md) | Research/provenance/deferred work; current-guide pointers added |
| [docs/research/project_design_summary.md](research/project_design_summary.md) | Research/provenance/deferred work; current-guide pointers added |
| [docs/research/research_guardrails.md](research/research_guardrails.md) | Research/provenance/deferred work; current-guide pointers added |
| [docs/research/research_question.md](research/research_question.md) | Research/provenance/deferred work; current-guide pointers added |
| [docs/research/reviewer_risk_register.md](research/reviewer_risk_register.md) | Research/provenance/deferred work; current-guide pointers added |
| [docs/research/shared_code_extraction.md](research/shared_code_extraction.md) | Research/provenance/deferred work; current-guide pointers added |
| [docs/research/target_journal_logic.md](research/target_journal_logic.md) | Research/provenance/deferred work; current-guide pointers added |
| [docs/superpowers/plans/2026-04-18-aurora-svmat-lab.md](superpowers/plans/2026-04-18-aurora-svmat-lab.md) | Historical design/plan; current-version boundary added |
| [docs/superpowers/plans/2026-04-19-aurora-v3-research-metrics.md](superpowers/plans/2026-04-19-aurora-v3-research-metrics.md) | Historical design/plan; current-version boundary added |
| [docs/superpowers/plans/2026-04-19-metric-definition-exports.md](superpowers/plans/2026-04-19-metric-definition-exports.md) | Historical design/plan; current-version boundary added |
| [docs/superpowers/plans/2026-04-20-unified-complexity-core-research-validation.md](superpowers/plans/2026-04-20-unified-complexity-core-research-validation.md) | Historical design/plan; current-version boundary added |
| [docs/superpowers/plans/2026-07-09-ucomx-comparator-validation.md](superpowers/plans/2026-07-09-ucomx-comparator-validation.md) | Historical design/plan; current-version boundary added |
| [docs/superpowers/plans/2026-08-11-legacy-project-consolidation.md](superpowers/plans/2026-08-11-legacy-project-consolidation.md) | Historical design/plan; current-version boundary added |
| [docs/superpowers/plans/2026-08-30-hybrid-complexity-metrics.md](superpowers/plans/2026-08-30-hybrid-complexity-metrics.md) | Historical design/plan; current-version boundary added |
| [docs/superpowers/plans/2026-09-19-geometry-units-validation.md](superpowers/plans/2026-09-19-geometry-units-validation.md) | Historical design/plan; current-version boundary added |
| [docs/superpowers/plans/2026-09-19-tomo-contracts-external-precision.md](superpowers/plans/2026-09-19-tomo-contracts-external-precision.md) | Historical design/plan; current-version boundary added |
| [docs/superpowers/plans/2026-10-08-documentation-sync.md](superpowers/plans/2026-10-08-documentation-sync.md) | This synchronization plan |
| [docs/superpowers/specs/2026-04-18-aurora-svmat-lab-design.md](superpowers/specs/2026-04-18-aurora-svmat-lab-design.md) | Historical design/plan; current-version boundary added |
| [docs/superpowers/specs/2026-04-19-aurora-v3-research-metrics-design.md](superpowers/specs/2026-04-19-aurora-v3-research-metrics-design.md) | Historical design/plan; current-version boundary added |
| [docs/superpowers/specs/2026-04-20-unified-complexity-core-research-validation-design.md](superpowers/specs/2026-04-20-unified-complexity-core-research-validation-design.md) | Historical design/plan; current-version boundary added |
| [docs/superpowers/specs/2026-07-09-ucomx-comparator-validation-design.md](superpowers/specs/2026-07-09-ucomx-comparator-validation-design.md) | Historical design/plan; current-version boundary added |
| [docs/superpowers/specs/2026-08-11-legacy-project-consolidation-design.md](superpowers/specs/2026-08-11-legacy-project-consolidation-design.md) | Historical design/plan; current-version boundary added |
| [docs/superpowers/specs/2026-08-30-hybrid-complexity-metrics-design.md](superpowers/specs/2026-08-30-hybrid-complexity-metrics-design.md) | Historical design/plan; current-version boundary added |
| [docs/tomo_input_contract.md](tomo_input_contract.md) | Current guidance or versioned migration; reviewed and synchronized |
| [docs/user_guide.md](user_guide.md) | Current guidance or versioned migration; reviewed and synchronized |
| [output/pdf/aurora_metric_formulas.pdf](../output/pdf/aurora_metric_formulas.pdf) | Regenerated from current sources; text and layout checked |
| [output/pdf/plancomplexity_app_summary.pdf](../output/pdf/plancomplexity_app_summary.pdf) | Regenerated from current sources; text and layout checked |
| [reference_text/Medical Physics - 2024 - Cavinato - Technical note  A software tool to extract complexity metrics from radiotherapy.txt](../reference_text/Medical Physics - 2024 - Cavinato - Technical note  A software tool to extract complexity metrics from radiotherapy.txt) | External source; preserved byte-for-byte, not current app instructions |
| [reference_text/UCoMX_User_Manual_v1.0.clean.txt](../reference_text/UCoMX_User_Manual_v1.0.clean.txt) | External source; preserved byte-for-byte, not current app instructions |
| [reference_text/UCoMX_User_Manual_v1.0.txt](../reference_text/UCoMX_User_Manual_v1.0.txt) | External source; preserved byte-for-byte, not current app instructions |
| [reference_text/mp17365-sup-0001-tables1.txt](../reference_text/mp17365-sup-0001-tables1.txt) | External source; preserved byte-for-byte, not current app instructions |
| [reference_text/mp17365-sup-0002-tables2.txt](../reference_text/mp17365-sup-0002-tables2.txt) | External source; preserved byte-for-byte, not current app instructions |
| [requirements.txt](../requirements.txt) | Dependency source reviewed; unchanged by documentation synchronization |
| [run_reports/validation/validation_summary.md](../run_reports/validation/validation_summary.md) | Historical evidence snapshot; preserved byte-for-byte |

## Verification

Generated files are compared against fresh catalog/contract output. CLI examples are checked against parser help. Local Markdown link targets are checked after removing code fences; historical absolute-workstation links are outside the current relative-link check. Both PDF documents are rendered for visual inspection. No claim is made that archived external URLs are currently reachable or that historical plans have all been executed.

### Results

- Full suite: 397 passed, 1 skipped, 99 subtests passed (`python -m pytest tests -q`, 44.92 s).
- 53 Markdown documents: 254 relative link targets checked, zero broken targets. External/absolute links were not network-verified.
- Four user-facing analysis CLIs and the new summary exporter: parser help matches documented options.
- Catalog/contract export tests compare freshly generated definition content with checked-in documents; all passed.
- Both PDFs regenerate successfully. Summary is one page; the updated summary and Aurora V4 pages were rendered and visually inspected. Other Aurora sections retain their existing formulas/layout.
- Git diff confirms no edits to original `reference_text/`, frozen `validation/reference_cases/` or `run_reports/` evidence.
- No metric-engine, GUI or parsing behavior changes in this documentation update.
