# Legacy Plan Complexity Project Consolidation Design

## Goal

Consolidate the useful, unique material from
`D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics` into this
repository so that the `D:\MedicalPhysicsResearch` tree can be discarded
without losing project knowledge. The current repository remains the sole
authoritative codebase.

## Comparison Findings

The legacy directory is a snapshot copied from this repository on 2026-05-22.
The comparison found 438 common in-scope files and 19 legacy-only files. The
legacy-only files contain project-design notes, migration and data provenance,
research guardrails, empty standardized-directory README files, and a UCoMX
validation design and implementation plan.

No Python implementation exists only in the legacy directory. Differences in
the shared program files are newline or formatting effects from the migration,
or newer work in the current repository. The current repository also contains
substantial uncommitted source, test, validation, workflow, and documentation
changes. Those files must not be overwritten by the older snapshot.

Two legacy changes are intentionally not portable:

- The legacy `.gitignore` tracks validation CSV evidence for the unified
  monorepo, whereas the current repository ignores generated CSV files and
  `data/` to reduce the risk of committing patient-identifying material.
- The legacy repository-hygiene test allows tracked CSV files under
  `run_reports/`; the current repository deliberately rejects tracked CSV
  files.

The current privacy-oriented behavior remains unchanged.

## Consolidation Structure

Create `docs/research/` as the home for imported research knowledge:

- `README.md`: index of the consolidated documents and their status.
- `project_design_summary.md`: imported project framing and evidence boundary.
- `research_question.md`: primary and secondary research questions.
- `analysis_plan.md`: planned analyses, required inputs, and traceability.
- `novelty_and_gap.md`: candidate research gap and evidence limitations.
- `reviewer_risk_register.md`: anticipated reviewer concerns.
- `target_journal_logic.md`: article type and journal-selection logic.
- `research_guardrails.md`: the scientific boundaries formerly expressed as
  agent instructions, rewritten as ordinary project documentation.
- `data_and_migration_provenance.md`: a consolidated record derived from
  `DATA_INDEX.md` and `MIGRATION_NOTES.md`.
- `shared_code_extraction.md`: the deferred shared-code extraction boundary.
- `codebase_comparison_2026-08-11.md`: the comparison method, inventory,
  exceptions, and merge decision.

The standardized placeholder directories `01_Data`, `02_Code`, `03_Results`,
`04_Manuscript`, `05_References`, and `99_Archive` are not copied. Their README
files contain no project information beyond the empty monorepo skeleton.

## Complete Legacy-only File Map

Every one of the 19 legacy-only files has the following disposition:

| Legacy source | Disposition in current repository |
|---|---|
| `00_Project_Design/analysis_plan.md` | Import as `docs/research/analysis_plan.md`. |
| `00_Project_Design/novelty_and_gap.md` | Import as `docs/research/novelty_and_gap.md`. |
| `00_Project_Design/project_design_summary.md` | Import as `docs/research/project_design_summary.md`. |
| `00_Project_Design/README.md` | Do not copy; replace its placeholder role with `docs/research/README.md`. |
| `00_Project_Design/research_question.md` | Import as `docs/research/research_question.md`. |
| `00_Project_Design/reviewer_risk_register.md` | Import as `docs/research/reviewer_risk_register.md`. |
| `00_Project_Design/target_journal_logic.md` | Import as `docs/research/target_journal_logic.md`. |
| `01_Data/README.md` | Do not copy; placeholder-only and covered by the provenance document. |
| `02_Code/extraction_note.md` | Import as `docs/research/shared_code_extraction.md`. |
| `02_Code/README.md` | Do not copy; placeholder-only and covered by the research index. |
| `03_Results/README.md` | Do not copy; placeholder-only and covered by the research index. |
| `04_Manuscript/README.md` | Do not copy; placeholder-only and covered by the research index. |
| `05_References/README.md` | Do not copy; placeholder-only and covered by the research index. |
| `99_Archive/README.md` | Do not copy; placeholder-only and covered by the comparison report. |
| `AGENTS.md` | Rewrite as ordinary documentation at `docs/research/research_guardrails.md`. |
| `DATA_INDEX.md` | Merge into `docs/research/data_and_migration_provenance.md`. |
| `MIGRATION_NOTES.md` | Merge into `docs/research/data_and_migration_provenance.md`. |
| `docs/superpowers/plans/2026-07-09-ucomx-comparator-validation.md` | Import at the same relative path and adapt stale execution paths. |
| `docs/superpowers/specs/2026-07-09-ucomx-comparator-validation-design.md` | Import at the same relative path and mark as imported, future work. |

`docs/research/codebase_comparison_2026-08-11.md` is newly authored from the
comparison evidence and is not counted among the 19 legacy-only files.

## UCoMX Documents

Copy the legacy UCoMX validation documents into the existing documentation
layout:

- `docs/superpowers/specs/2026-07-09-ucomx-comparator-validation-design.md`
- `docs/superpowers/plans/2026-07-09-ucomx-comparator-validation.md`

These documents describe future work and must be labeled as imported and not
implemented. Make their execution instructions independent of the discarded
tree:

- Replace the legacy project-root prefix with repository-relative paths.
- Replace the monorepo Python executable with `.venv\Scripts\python.exe`.
- Replace monorepo-prefixed ignore examples with repository-relative paths.
- Replace the planned `04_Manuscript` output with
  `docs/research/ucomx_comparator_validation_technical_report.md`.
- Replace protected temporary paths beneath `D:\MedicalPhysicsResearch` with
  `%TEMP%\PlanComplexity\ucomx_comparator`, which is user-local and outside the
  repository.
- Retain references to `C:\Users\hujin\Desktop\Programming\ucomx` because that
  is a separate input location and is not part of the tree being discarded.

Historical paths may remain in the provenance and comparison documents only
when explicitly labeled as historical. No executable instruction may depend
on `D:\MedicalPhysicsResearch`.

## Content Preservation Rules

The imported research documents may receive only the edits required to:

- identify their origin and import date;
- replace stale repository-location descriptions with the current repository;
- repair links after reorganization; and
- clarify that candidate claims and UCoMX work are not completed evidence.

Scientific claims, scope limitations, metric boundaries, and traceability
statements must otherwise be preserved. The source directory remains read-only
throughout the consolidation.

## Data Flow

The legacy documents are read from the snapshot, classified as substantive or
placeholder-only, and transformed into the target documentation layout. A new
index links the imported documents. The comparison report records why program
files, data files, generated results, `.gitignore`, and repository-hygiene
tests were not imported.

No Python module, validation fixture, patient/plan data, generated report, or
existing current-repository file is copied from the legacy snapshot.

## Safety and Error Handling

- Stop if any expected legacy source document is missing.
- Never overwrite a target file that already exists without first comparing
  and reconciling it.
- Preserve all unrelated dirty working-tree changes.
- Stage and commit only consolidation files; never stage the user's existing
  modifications.
- Do not delete, rename, or modify the legacy directory. The user will discard
  it separately after reviewing the result.

## Verification

Verification must demonstrate all of the following:

1. Every substantive legacy-only document is represented in the current
   repository.
2. Placeholder-only README files are intentionally accounted for in the
   comparison report.
3. No executable instruction outside historical provenance references
   `D:\MedicalPhysicsResearch`.
4. Imported Markdown links resolve within the current repository.
5. No current Python, data, test, workflow, or validation file changed as part
   of the consolidation.
6. The current repository's `.gitignore` and repository-hygiene policy remain
   unchanged.
7. The source directory has not been modified.
8. The existing test suite is run after the documentation merge; any failure
   is reported with a distinction between consolidation-caused and pre-existing
   dirty-worktree failures.

## Acceptance Criteria

The consolidation is complete when the current repository contains the
organized research documents, adapted UCoMX planning documents, and a durable
comparison report; all verification rules pass or any pre-existing failures
are explicitly documented; and the discarded tree is no longer required by
any executable project instruction.
