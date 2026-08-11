# Plan Complexity Codebase Comparison (2026-08-11)

## Compared Locations

- **Current repository:** `C:\Users\hujin\Desktop\Programming\PlanComplexity`, the authoritative source for code, tests, policies, fixtures, and ongoing work.
- **Legacy snapshot:** `D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics`, a 2026-05-22 snapshot of the current repository retained only as historical provenance.

## Method

The comparison matched relative paths in the current repository and the legacy snapshot while excluding repository metadata (`.git`), virtual environments, IDE state, caches, build and distribution artifacts, generated outputs, and bytecode. It then separated common paths from legacy-only paths and reviewed common text files both with and without line-ending and final-newline differences.

After those exclusions, the comparison found 438 common in-scope files and 19 legacy-only files.

## Findings

- No Python implementation is unique to the legacy snapshot.
- Most differences among common text files reduce to line endings or final newlines.
- The remaining meaningful common-file differences are migration-specific `.gitignore` and repository-hygiene behavior, XML/reference-text whitespace, and newer work in the current repository.
- The current repository is therefore the source of truth. Consolidation requires preserving research context and provenance, not copying legacy implementation or replacing current behavior.

## Legacy-only File Disposition

| # | Legacy-only path | Disposition |
|---:|---|---|
| 1 | `00_Project_Design/analysis_plan.md` | Import as `docs/research/analysis_plan.md`. |
| 2 | `00_Project_Design/novelty_and_gap.md` | Import as `docs/research/novelty_and_gap.md`. |
| 3 | `00_Project_Design/project_design_summary.md` | Import as `docs/research/project_design_summary.md`. |
| 4 | `00_Project_Design/README.md` | Omit placeholder; replace with `docs/research/README.md`. |
| 5 | `00_Project_Design/research_question.md` | Import as `docs/research/research_question.md`. |
| 6 | `00_Project_Design/reviewer_risk_register.md` | Import as `docs/research/reviewer_risk_register.md`. |
| 7 | `00_Project_Design/target_journal_logic.md` | Import as `docs/research/target_journal_logic.md`. |
| 8 | `01_Data/README.md` | Omit placeholder; cover its context in provenance documentation. |
| 9 | `02_Code/extraction_note.md` | Import as `docs/research/shared_code_extraction.md`. |
| 10 | `02_Code/README.md` | Omit placeholder. |
| 11 | `03_Results/README.md` | Omit placeholder. |
| 12 | `04_Manuscript/README.md` | Omit placeholder. |
| 13 | `05_References/README.md` | Omit placeholder. |
| 14 | `99_Archive/README.md` | Omit placeholder. |
| 15 | `AGENTS.md` | Convert to ordinary documentation at `docs/research/research_guardrails.md`. |
| 16 | `DATA_INDEX.md` | Merge into `docs/research/data_and_migration_provenance.md`. |
| 17 | `MIGRATION_NOTES.md` | Merge into `docs/research/data_and_migration_provenance.md`. |
| 18 | `docs/superpowers/plans/2026-07-09-ucomx-comparator-validation.md` | Preserve at the same relative path with the original body unchanged and an overriding non-executable archival warning; the 2026-08-12 user override supersedes the earlier path-adaptation disposition. |
| 19 | `docs/superpowers/specs/2026-07-09-ucomx-comparator-validation-design.md` | Preserve at the same relative path as unimplemented future work. |

## Shared-file Differences

Most common text-file differences are formatting-only changes in line endings or final newlines. The meaningful remainder falls into four categories: migration-specific `.gitignore` behavior, corresponding repository-hygiene behavior, whitespace differences in XML and reference text, and newer current-repository work added after the snapshot. None establishes a missing legacy Python implementation or justifies replacing a current source file.

## Excluded Monorepo Policies

The legacy `.gitignore` and `tests/test_repository_hygiene.py` behavior are explicitly rejected. They permit tracked validation CSV evidence in the monorepo, whereas the authoritative current repository keeps generated CSV evidence and `data/` material local. Importing those legacy policy differences would weaken the current repository's privacy and hygiene boundary.

## Consolidation Decision

Preserve the 12 substantive legacy-only research, provenance, guardrail, and future-work documents through the destinations listed above; omit the seven placeholder README files. Do not import Python implementation or alter current code, tests, privacy rules, validation fixtures, `.gitignore`, or repository-hygiene behavior. The current repository remains authoritative.

## Historical Provenance

`D:\MedicalPhysicsResearch` records where the 2026-05-22 snapshot was held. That path is historical provenance only: documentation may identify it to preserve traceability, but executable instructions, tests, scripts, workflows, and runtime configuration must never depend on it.
