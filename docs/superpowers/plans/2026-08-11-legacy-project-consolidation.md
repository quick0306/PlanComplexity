# Legacy Plan Complexity Project Consolidation Implementation Plan

> **COMPLETED PLAN — HISTORICAL ARCHIVE ONLY (2026-08-12):** This consolidation was completed on 2026-08-12. This document is now historical archival material only and is non-executable.
> This notice overrides every `REQUIRED SUB-SKILL` line, checkbox, imperative, command, path, and acceptance step below.
> None of those items may be executed or treated as current guidance.
> `D:\MedicalPhysicsResearch` is a historical source path and may no longer exist.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve all useful, unique material from the legacy Plan Complexity Metrics snapshot in the current repository without importing obsolete code, monorepo policy, or patient-data tracking behavior.

**Architecture:** Treat the current repository as the only code authority and the legacy directory as a read-only documentation source. Import research knowledge into `docs/research/`, adapt the two UCoMX planning documents to repository-relative execution paths, and prove through explicit inventories and Git checks that no program or source data changed.

**Tech Stack:** Markdown, Git, PowerShell, Python/pytest for regression verification.

---

## Source and Safety Context

- Current repository: `C:\Users\hujin\Desktop\Programming\PlanComplexity`
- Read-only legacy source: `D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics`
- Design specification: `docs/superpowers/specs/2026-08-11-legacy-project-consolidation-design.md`
- The current working tree already contains unrelated modified and untracked files. Never use broad `git add .`, `git add -A`, checkout, reset, clean, or bulk-copy commands.
- Do not edit, rename, or delete anything beneath `D:\MedicalPhysicsResearch`.
- Do not modify current Python, test, validation, workflow, data, run-report, `.gitignore`, or repository-hygiene files.
- Use `apply_patch` for every created or edited repository file.

## Target File Map

### Create

- `docs/research/README.md`: index, document status, and navigation.
- `docs/research/codebase_comparison_2026-08-11.md`: methods, inventory, differences, exclusions, and consolidation decision.
- `docs/research/project_design_summary.md`: imported design summary.
- `docs/research/research_question.md`: imported research questions.
- `docs/research/analysis_plan.md`: imported analysis plan.
- `docs/research/novelty_and_gap.md`: imported novelty/gap assessment.
- `docs/research/reviewer_risk_register.md`: imported reviewer risks.
- `docs/research/target_journal_logic.md`: imported journal-selection logic.
- `docs/research/research_guardrails.md`: scientific boundaries converted from legacy agent instructions.
- `docs/research/data_and_migration_provenance.md`: combined data index and migration record.
- `docs/research/shared_code_extraction.md`: imported deferred extraction boundary.
- `docs/superpowers/specs/2026-07-09-ucomx-comparator-validation-design.md`: imported future-work design with a current-context banner.
- `docs/superpowers/plans/2026-07-09-ucomx-comparator-validation.md`: imported future-work plan with portable paths.

### Must Not Modify

- `.gitignore`
- `tests/test_repository_hygiene.py`
- All `*.py` files outside any already-existing user change
- `.github/`, `data/`, `run_reports/`, `validation/`, and `tests/`
- Any file beneath the legacy source directory

## Task 1: Establish the Safety Baseline and Comparison Record

**Files:**
- Create: `docs/research/README.md`
- Create: `docs/research/codebase_comparison_2026-08-11.md`

- [ ] **Step 1: Capture the pre-implementation Git state**

Run:

```powershell
git status --short --branch
git diff --name-only
git ls-files --others --exclude-standard
git -C D:\MedicalPhysicsResearch status --short -- 02_Projects/Plan_Complexity_Metrics
$baseCommit = git log --format=%H --grep='^docs: plan legacy project consolidation$' -1
if (-not $baseCommit) { throw 'Cannot identify consolidation base commit' }
$baseCommit
```

Expected: the current repository shows the user's existing dirty files; the legacy project subtree has no uncommitted changes; `$baseCommit` prints the implementation-plan commit hash. Keep the output and hash in the task transcript for the final before/after comparison. Do not write them to the repository.

- [ ] **Step 2: Verify that the target documentation files do not already exist**

Run:

```powershell
Test-Path docs\research\README.md
Test-Path docs\research\codebase_comparison_2026-08-11.md
```

Expected: both commands return `False`. If either returns `True`, inspect and reconcile it before continuing rather than overwriting it.

- [ ] **Step 3: Create the comparison report**

Create `docs/research/codebase_comparison_2026-08-11.md` with these exact top-level sections:

```markdown
# Plan Complexity Codebase Comparison (2026-08-11)

## Compared Locations
## Method
## Findings
## Legacy-only File Disposition
## Shared-file Differences
## Excluded Monorepo Policies
## Consolidation Decision
## Historical Provenance
```

The report must record:

- the current repository is the source and the legacy directory is its 2026-05-22 snapshot;
- 438 common in-scope files and 19 legacy-only files were found after excluding `.git`, virtual environments, IDE state, caches, builds, distributions, outputs, and bytecode;
- no Python implementation is unique to the legacy snapshot;
- most common text-file differences reduce to line endings/final newlines;
- the remaining meaningful common-file differences are migration-specific `.gitignore`, repository-hygiene behavior, XML/reference-text whitespace, and newer current-repository work;
- all 19 legacy-only paths and the exact disposition table from the approved design;
- the legacy `.gitignore` and `tests/test_repository_hygiene.py` are rejected because they permit tracked validation CSV evidence in the monorepo, while the current repository keeps generated CSV and `data/` material local;
- `D:\MedicalPhysicsResearch` is historical provenance only and must not be used by executable instructions.

- [ ] **Step 4: Create the research index**

Create `docs/research/README.md` with:

- a statement that the directory consolidates research knowledge formerly held in the legacy snapshot;
- a table linking every file planned under `docs/research/`;
- status labels distinguishing imported evidence boundaries, future work, and historical provenance;
- a note that the current codebase, tests, privacy rules, and validation fixtures remain authoritative;
- a link to `../superpowers/specs/2026-07-09-ucomx-comparator-validation-design.md` and `../superpowers/plans/2026-07-09-ucomx-comparator-validation.md`, labeled as unimplemented future work.

- [ ] **Step 5: Check Markdown formatting**

Run:

```powershell
git diff --check -- docs/research/README.md docs/research/codebase_comparison_2026-08-11.md
```

Expected: exit code 0 with no whitespace errors.

- [ ] **Step 6: Commit only the comparison and index**

Run:

```powershell
git add -- docs/research/README.md docs/research/codebase_comparison_2026-08-11.md
git diff --cached --name-only
git commit -m "docs: record legacy codebase comparison"
```

Expected: the staged list contains exactly the two files named above, and the commit succeeds.

## Task 2: Import the Research Design and Scientific Guardrails

**Files:**
- Create: `docs/research/project_design_summary.md`
- Create: `docs/research/research_question.md`
- Create: `docs/research/analysis_plan.md`
- Create: `docs/research/novelty_and_gap.md`
- Create: `docs/research/reviewer_risk_register.md`
- Create: `docs/research/target_journal_logic.md`
- Create: `docs/research/research_guardrails.md`
- Modify: `docs/research/README.md`

- [ ] **Step 1: Read all source documents before transforming them**

Read these files in full:

```text
D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics\00_Project_Design\project_design_summary.md
D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics\00_Project_Design\research_question.md
D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics\00_Project_Design\analysis_plan.md
D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics\00_Project_Design\novelty_and_gap.md
D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics\00_Project_Design\reviewer_risk_register.md
D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics\00_Project_Design\target_journal_logic.md
D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics\AGENTS.md
```

Expected: all seven source files exist. Stop and report the missing path if any file cannot be read.

- [ ] **Step 2: Verify every research-design target is absent before creation**

Run:

```powershell
$targets = @(
  'docs/research/project_design_summary.md',
  'docs/research/research_question.md',
  'docs/research/analysis_plan.md',
  'docs/research/novelty_and_gap.md',
  'docs/research/reviewer_risk_register.md',
  'docs/research/target_journal_logic.md',
  'docs/research/research_guardrails.md'
)
$existing = $targets | Where-Object { Test-Path -LiteralPath $_ }
if ($existing) { throw "Targets already exist; inspect and reconcile before continuing: $($existing -join ', ')" }
```

Expected: exit code 0 with no exception. If any target exists, inspect it and revise the plan or reconcile it explicitly; never overwrite it automatically.

- [ ] **Step 3: Create the six research-design documents**

Create the six same-named target documents using the full substantive content of their source documents. Apply only these transformations:

1. Add this block immediately beneath each title:

   ```markdown
   > Imported on 2026-08-11 from the legacy unified-workspace snapshot.
   > This document records research framing and evidence boundaries; it is not completed clinical evidence.
   ```

2. Replace descriptions that call the current repository a copied or migrated source with descriptions that call it the authoritative repository.
3. Replace operational references to `C:\Users\hujin\Desktop\Programming\PlanComplexity` with “this repository.”
4. Repair any relative Markdown link so it resolves from the new `docs/research/` location.
5. Preserve all research questions, scope exclusions, required inputs, system-specific limitations, reviewer risks, candidate journals, and traceability statements.

- [ ] **Step 4: Convert the legacy agent instructions into ordinary research documentation**

Create `docs/research/research_guardrails.md` with these sections:

```markdown
# Plan Complexity Research Guardrails

> Imported on 2026-08-11 from legacy project instructions and retained as scientific documentation.

## Scientific Focus
## Data Traceability
## System-specific Boundaries
## Shared-code Boundary
## UCoMX Evidence Boundary
```

Transfer the substantive rules from legacy `AGENTS.md`. Do not preserve agent-command language. In particular, state that complexity thresholds cannot be transferred across TOMO, Aurora, VMAT, IMRT, CyberKnife, Halcyon, or Ethos without system-specific justification.

- [ ] **Step 5: Confirm the imported documents do not create a discarded-tree dependency**

Run:

```powershell
rg -n -F 'D:\MedicalPhysicsResearch' docs\research\project_design_summary.md docs\research\research_question.md docs\research\analysis_plan.md docs\research\novelty_and_gap.md docs\research\reviewer_risk_register.md docs\research\target_journal_logic.md docs\research\research_guardrails.md
```

Expected: no matches and exit code 1 from `rg`.

- [ ] **Step 6: Verify the research index links the seven new files**

Run a PowerShell loop over the seven target filenames and assert both the file and its link entry exist:

```powershell
$names = @(
  'project_design_summary.md',
  'research_question.md',
  'analysis_plan.md',
  'novelty_and_gap.md',
  'reviewer_risk_register.md',
  'target_journal_logic.md',
  'research_guardrails.md'
)
$index = Get-Content -Raw docs\research\README.md
$names | ForEach-Object {
  if (-not (Test-Path (Join-Path docs\research $_))) { throw "Missing file: $_" }
  if (-not $index.Contains($_)) { throw "Missing index link: $_" }
}
```

Expected: exit code 0 with no exception.

- [ ] **Step 7: Commit only the research-design documents and index update**

Run:

```powershell
git add -- docs/research/project_design_summary.md docs/research/research_question.md docs/research/analysis_plan.md docs/research/novelty_and_gap.md docs/research/reviewer_risk_register.md docs/research/target_journal_logic.md docs/research/research_guardrails.md docs/research/README.md
git diff --cached --name-only
git diff --cached --check
git commit -m "docs: consolidate plan complexity research design"
```

Expected: exactly the eight listed documentation files are staged and committed.

## Task 3: Consolidate Migration, Data, and Shared-code Provenance

**Files:**
- Create: `docs/research/data_and_migration_provenance.md`
- Create: `docs/research/shared_code_extraction.md`
- Modify: `docs/research/README.md`

- [ ] **Step 1: Read the three provenance sources in full**

Read:

```text
D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics\DATA_INDEX.md
D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics\MIGRATION_NOTES.md
D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics\02_Code\extraction_note.md
```

Expected: all three files exist and describe the May 2026 snapshot, copied data/evidence, exclusions, and deferred shared-code extraction.

- [ ] **Step 2: Verify both provenance targets are absent before creation**

Run:

```powershell
$targets = @(
  'docs/research/data_and_migration_provenance.md',
  'docs/research/shared_code_extraction.md'
)
$existing = $targets | Where-Object { Test-Path -LiteralPath $_ }
if ($existing) { throw "Targets already exist; inspect and reconcile before continuing: $($existing -join ', ')" }
```

Expected: exit code 0 with no exception. If a target exists, inspect and reconcile it explicitly rather than overwriting it.

- [ ] **Step 3: Create the combined provenance document**

Create `docs/research/data_and_migration_provenance.md` with these sections:

```markdown
# Data and Migration Provenance

## Historical Snapshot
## Copied Scope
## Data and Evidence Inventory at Migration Time
## Technical Exclusions
## Current Authority
## Decommissioning Note
```

Requirements:

- identify both original paths as historical locations and state that the current repository is authoritative;
- preserve the historical counts: `data/` 238 files and 220.54 MB, `run_reports/` 21 files and 1.33 MB, `output/` 12 files and 0.72 MB;
- preserve which locations were and were not copied in May 2026;
- preserve the technical exclusions from the migration note;
- state that the legacy tree was a snapshot, added no later Python implementation, and can be discarded after this consolidation is reviewed;
- state that historical path strings are provenance, not runtime dependencies.

- [ ] **Step 4: Create the shared-code extraction document**

Create `docs/research/shared_code_extraction.md` from the full substantive content of `02_Code/extraction_note.md`. Add an import banner, repair any relative Markdown links for the new location, and preserve the rule that project-specific analysis dependencies must be separated before moving stable code into a shared package.

- [ ] **Step 5: Add both documents to the research index**

Update `docs/research/README.md` with relative links to both new files and label them “historical provenance” and “deferred architecture work,” respectively.

- [ ] **Step 6: Verify that historical path references are contained**

Run:

```powershell
rg -l -F 'D:\MedicalPhysicsResearch' docs\research
```

Expected: matches are limited to:

```text
docs/research/codebase_comparison_2026-08-11.md
docs/research/data_and_migration_provenance.md
```

- [ ] **Step 7: Commit the provenance documents and index update**

Run:

```powershell
git add -- docs/research/data_and_migration_provenance.md docs/research/shared_code_extraction.md docs/research/README.md
git diff --cached --name-only
git diff --cached --check
git commit -m "docs: preserve plan complexity provenance"
```

Expected: exactly the three listed files are staged and committed.

## Task 4: Import and Adapt the UCoMX Future-work Documents

**Files:**
- Create: `docs/superpowers/specs/2026-07-09-ucomx-comparator-validation-design.md`
- Create: `docs/superpowers/plans/2026-07-09-ucomx-comparator-validation.md`
- Modify: `docs/research/README.md`

- [ ] **Step 1: Confirm source and target state**

Run:

```powershell
Test-Path D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics\docs\superpowers\specs\2026-07-09-ucomx-comparator-validation-design.md
Test-Path D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics\docs\superpowers\plans\2026-07-09-ucomx-comparator-validation.md
Test-Path docs\superpowers\specs\2026-07-09-ucomx-comparator-validation-design.md
Test-Path docs\superpowers\plans\2026-07-09-ucomx-comparator-validation.md
```

Expected: the two source checks return `True` and the two target checks return `False`.

- [ ] **Step 2: Import the UCoMX design with a status banner**

Create the target design from the full legacy design content. Immediately below its title add:

```markdown
> Imported on 2026-08-11 from the legacy unified-workspace snapshot.
> Status: approved historical design for unimplemented future work.
```

Retain the separate input reference to `C:\Users\hujin\Desktop\Programming\ucomx`; it is outside the directory being decommissioned.
Repair any relative Markdown links so they resolve from the target design's location.

- [ ] **Step 3: Import the UCoMX implementation plan and perform exact path adaptations**

Create the target plan from the full legacy plan content, add the same imported/unimplemented banner, and apply all of these replacements:

| Legacy instruction | Current-repository instruction |
|---|---|
| Run from `D:\MedicalPhysicsResearch\02_Projects\Plan_Complexity_Metrics` | Run from the repository root. |
| `D:\MedicalPhysicsResearch\.venv\Scripts\python.exe` | `.venv\Scripts\python.exe` |
| `D:\MedicalPhysicsResearch\.codex_tmp\ucomx_comparator` | `%TEMP%\PlanComplexity\ucomx_comparator` |
| `D:/MedicalPhysicsResearch/02_Projects/Plan_Complexity_Metrics/data/...` | repository-relative `data/...` |
| `02_Projects/Plan_Complexity_Metrics/validation/...` | `validation/...` |
| `04_Manuscript/ucomx_comparator_validation_technical_report.md` | `docs/research/ucomx_comparator_validation_technical_report.md` |

Do not change metric definitions, schemas, tolerances, task order, test expectations, claim boundaries, PHI guardrails, or open-source release policy.
Repair any relative Markdown links so they resolve from the target plan's location.

- [ ] **Step 4: Verify no UCoMX executable instruction depends on the discarded tree**

Run:

```powershell
rg -n -F 'D:\MedicalPhysicsResearch' docs\superpowers\specs\2026-07-09-ucomx-comparator-validation-design.md docs\superpowers\plans\2026-07-09-ucomx-comparator-validation.md
rg -n -F 'D:/MedicalPhysicsResearch' docs\superpowers\specs\2026-07-09-ucomx-comparator-validation-design.md docs\superpowers\plans\2026-07-09-ucomx-comparator-validation.md
rg -n -F '02_Projects/Plan_Complexity_Metrics' docs\superpowers\plans\2026-07-09-ucomx-comparator-validation.md
rg -n -F '04_Manuscript/' docs\superpowers\plans\2026-07-09-ucomx-comparator-validation.md
```

Expected: all four commands return no matches with `rg` exit code 1.

- [ ] **Step 5: Verify required portable paths appear**

Run:

```powershell
rg -n -F '.venv\Scripts\python.exe' docs\superpowers\plans\2026-07-09-ucomx-comparator-validation.md
rg -n -F '%TEMP%\PlanComplexity\ucomx_comparator' docs\superpowers\plans\2026-07-09-ucomx-comparator-validation.md
rg -n -F 'docs/research/ucomx_comparator_validation_technical_report.md' docs\superpowers\plans\2026-07-09-ucomx-comparator-validation.md
```

Expected: each command finds at least one match.

- [ ] **Step 6: Check the index and Markdown changes**

Run:

```powershell
$index = Get-Content -Raw docs\research\README.md
if (-not $index.Contains('../superpowers/specs/2026-07-09-ucomx-comparator-validation-design.md')) { throw 'Missing UCoMX design link' }
if (-not $index.Contains('../superpowers/plans/2026-07-09-ucomx-comparator-validation.md')) { throw 'Missing UCoMX plan link' }
git diff --check -- docs/superpowers/specs/2026-07-09-ucomx-comparator-validation-design.md docs/superpowers/plans/2026-07-09-ucomx-comparator-validation.md docs/research/README.md
```

Expected: exit code 0 and no exception.

- [ ] **Step 7: Commit only the two UCoMX documents and index update**

Run:

```powershell
git add -- docs/superpowers/specs/2026-07-09-ucomx-comparator-validation-design.md docs/superpowers/plans/2026-07-09-ucomx-comparator-validation.md docs/research/README.md
git diff --cached --name-only
git diff --cached --check
git commit -m "docs: preserve UCoMX comparator validation plan"
```

Expected: exactly the three listed files are staged and committed.

## Task 5: Verify Completeness, Isolation, and Regression Safety

**Files:**
- Verify: `docs/research/*.md`
- Verify: `docs/superpowers/specs/2026-07-09-ucomx-comparator-validation-design.md`
- Verify: `docs/superpowers/plans/2026-07-09-ucomx-comparator-validation.md`
- Verify: repository source and tests remain untouched by consolidation commits

- [ ] **Step 1: Verify every target document exists**

Run:

```powershell
$targets = @(
  'docs/research/README.md',
  'docs/research/codebase_comparison_2026-08-11.md',
  'docs/research/project_design_summary.md',
  'docs/research/research_question.md',
  'docs/research/analysis_plan.md',
  'docs/research/novelty_and_gap.md',
  'docs/research/reviewer_risk_register.md',
  'docs/research/target_journal_logic.md',
  'docs/research/research_guardrails.md',
  'docs/research/data_and_migration_provenance.md',
  'docs/research/shared_code_extraction.md',
  'docs/superpowers/specs/2026-07-09-ucomx-comparator-validation-design.md',
  'docs/superpowers/plans/2026-07-09-ucomx-comparator-validation.md'
)
$missing = $targets | Where-Object { -not (Test-Path -LiteralPath $_) }
if ($missing) { throw "Missing targets: $($missing -join ', ')" }
```

Expected: exit code 0 and no exception.

- [ ] **Step 2: Verify the 19-source disposition is complete**

Use the approved design's `Complete Legacy-only File Map` as the checklist. Confirm the comparison report contains all 19 legacy source paths and that each substantive source has its target representation. Confirm the seven placeholder README files were not copied.

Run:

```powershell
Get-ChildItem docs\research -Recurse -File | Select-Object -ExpandProperty FullName
Test-Path 00_Project_Design
Test-Path 01_Data
Test-Path 02_Code
Test-Path 03_Results
Test-Path 04_Manuscript
Test-Path 05_References
Test-Path 99_Archive
```

Expected: the research files are present and every placeholder directory check returns `False`.

- [ ] **Step 3: Verify discarded-tree references are provenance-only**

Run:

```powershell
rg -l -F 'D:\MedicalPhysicsResearch' docs\research docs\superpowers\specs\2026-07-09-ucomx-comparator-validation-design.md docs\superpowers\plans\2026-07-09-ucomx-comparator-validation.md
```

Expected: only the comparison and provenance files match.

- [ ] **Step 4: Verify all imported Markdown links resolve**

Run a PowerShell check over relative Markdown links in every imported document:

```powershell
$markdownFiles = @(
  Get-ChildItem docs\research -Recurse -Filter '*.md' -File
  Get-Item docs\superpowers\specs\2026-07-09-ucomx-comparator-validation-design.md
  Get-Item docs\superpowers\plans\2026-07-09-ucomx-comparator-validation.md
)
foreach ($file in $markdownFiles) {
  $base = Split-Path $file.FullName
  $text = Get-Content -Raw $file.FullName
  $matches = [regex]::Matches($text, '\[[^\]]+\]\(([^)]+)\)')
  foreach ($match in $matches) {
    $link = $match.Groups[1].Value.Trim()
    if ($link -match '^(https?://|mailto:|#)') { continue }
    $pathPart = ($link -split '#', 2)[0]
    if (-not $pathPart) { continue }
    $target = Join-Path $base ([Uri]::UnescapeDataString($pathPart))
    if (-not (Test-Path -LiteralPath $target)) {
      throw "Broken link in $($file.FullName): $link"
    }
  }
}
```

Expected: exit code 0 and no broken-link exception.

- [ ] **Step 5: Verify consolidation commits contain documentation only**

Resolve the committed plan as the fixed pre-implementation base and inspect through `HEAD`:

```powershell
git log --oneline -8
$baseCommit = git log --format=%H --grep='^docs: plan legacy project consolidation$' -1
if (-not $baseCommit) { throw 'Cannot identify consolidation base commit' }
git diff --name-only "$baseCommit..HEAD"
```

Expected: only files beneath `docs/research/` and the two named UCoMX documents beneath `docs/superpowers/` appear. The already-committed design and plan documents may also appear if the chosen base predates them.

- [ ] **Step 6: Verify protected policy files were not changed by consolidation**

Run:

```powershell
$baseCommit = git log --format=%H --grep='^docs: plan legacy project consolidation$' -1
git diff "$baseCommit..HEAD" -- .gitignore tests/test_repository_hygiene.py
```

Expected: no output.

- [ ] **Step 7: Run repository formatting and test verification**

Run:

```powershell
$baseCommit = git log --format=%H --grep='^docs: plan legacy project consolidation$' -1
git diff --check "$baseCommit..HEAD"
.venv\Scripts\python.exe -m pytest -q
```

Expected: `git diff --check` exits 0. The test suite passes. If it fails, compare the failure with the pre-existing dirty working tree and report it accurately; do not change program code under this documentation-only consolidation plan.

- [ ] **Step 8: Confirm the legacy source remained untouched**

Run:

```powershell
git -C D:\MedicalPhysicsResearch status --short -- 02_Projects/Plan_Complexity_Metrics
```

Expected: the output matches the Task 1 baseline and contains no changes caused by this work.

- [ ] **Step 9: Report completion without deleting the legacy tree**

Report:

- the comparison conclusion;
- the created documents and their location;
- the UCoMX plan's future-work status;
- verification and test results;
- commit hashes created by the consolidation;
- confirmation that the legacy tree was not modified or deleted.

The user remains responsible for discarding `D:\MedicalPhysicsResearch` after reviewing the consolidated repository.
