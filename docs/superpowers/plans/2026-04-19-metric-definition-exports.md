# Metric Definition Exports Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Export all currently implemented metric mathematical definitions and physical meanings into one CSV table and one Markdown reference document.

**Architecture:** Introduce a unified metric-definition catalog that gathers implemented metrics from the main registry and Aurora standalone prototype, then generate both CSV and Markdown from that shared source. Keep the generated artifacts in stable paths so users can re-run the export without touching GUI logic.

**Tech Stack:** Python 3.14, standard library (`csv`, `pathlib`), existing metric registry and Aurora notes modules, `unittest`.

---

### Task 1: Define the export surface

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_metric_definition_exports.py`

- [ ] **Step 1: Write failing tests for the catalog shape**
- [ ] **Step 2: Run the new test file and confirm it fails for missing export/catalog code**
- [ ] **Step 3: Extend the tests to assert CSV and Markdown generation paths and key fields**
- [ ] **Step 4: Re-run the targeted test file and keep it red for the intended reasons**

### Task 2: Build the unified metric-definition catalog

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\metric_definition_catalog.py`
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\metric_registry.py`
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\notes.py`

- [ ] **Step 1: Implement a normalized record model for exported metric definitions**
- [ ] **Step 2: Populate VMAT/IMRT, TOMO, and CyberKnife records from the existing registry**
- [ ] **Step 3: Populate Aurora v2 and legacy records from the Aurora standalone implementation**
- [ ] **Step 4: Ensure each record includes platform, group, display name, mathematical definition, physical meaning, and implementation notes**

### Task 3: Add export generation

**Files:**
- Create: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tools\export_metric_definitions.py`

- [ ] **Step 1: Implement CSV export to `C:\Users\hujin\Desktop\Programming\PlanComplexity\output\metric_definitions_all.csv`**
- [ ] **Step 2: Implement Markdown export to `C:\Users\hujin\Desktop\Programming\PlanComplexity\docs\metric_definitions_all.md`**
- [ ] **Step 3: Keep both outputs driven by the same in-memory catalog**

### Task 4: Verify and generate artifacts

**Files:**
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\README.md`

- [ ] **Step 1: Run the targeted export tests and confirm they pass**
- [ ] **Step 2: Run the exporter script to generate both artifacts**
- [ ] **Step 3: Inspect the generated CSV and Markdown outputs for representative metrics across all four platforms**
- [ ] **Step 4: Update README if a short pointer to the exported definition references adds value**
