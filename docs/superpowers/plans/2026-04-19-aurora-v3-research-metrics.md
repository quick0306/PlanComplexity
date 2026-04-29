# Aurora V3 Research Metrics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add immediately supportable Aurora v3 research metrics for reversal symmetry, small-opening burden, local interval peaks, axial regions, and dual-layer coordination.

**Architecture:** Extend the standalone Aurora metrics layer with additional interval-statistics helpers, then expose the new metrics through the existing notes and export pipeline. Keep the parsing layer unchanged and derive everything from already parsed control-point data.

**Tech Stack:** Python 3.14, unittest, existing Aurora SVMAT Lab package

---

### Task 1: Add failing tests for Aurora v3 metrics

**Files:**
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_aurora_metrics.py`
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\tests\test_aurora_export.py`

- [ ] **Step 1: Write failing metric tests**
- [ ] **Step 2: Run targeted Aurora tests and verify failure**
- [ ] **Step 3: Write failing export assertions for new metric names**
- [ ] **Step 4: Re-run targeted tests and verify failure remains focused**

### Task 2: Implement Aurora v3 metric calculations

**Files:**
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\metrics.py`

- [ ] **Step 1: Add grouped v3 metric ordering constants**
- [ ] **Step 2: Add reusable helpers for interval summaries, regional partitioning, and weighted small-gap calculations**
- [ ] **Step 3: Implement beam-level small-opening, local-peak, regional, and dual-layer metrics**
- [ ] **Step 4: Implement plan-level reversal and bidirectional symmetry metrics**
- [ ] **Step 5: Integrate v3 metrics into `calculate_beam_metrics()` and `calculate_plan_metrics()`**

### Task 3: Wire notes and exports

**Files:**
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\notes.py`
- Modify: `C:\Users\hujin\Desktop\Programming\PlanComplexity\aurora_svmat_lab\export.py`

- [ ] **Step 1: Add Aurora v3 metric notes**
- [ ] **Step 2: Extend export ordering to include v3 metrics**
- [ ] **Step 3: Keep projection and trajectory exports compatible with prior columns**

### Task 4: Verify and stabilize

**Files:**
- Modify only if verification reveals issues in the files above

- [ ] **Step 1: Run targeted Aurora metric tests**
- [ ] **Step 2: Run Aurora export tests**
- [ ] **Step 3: Run compile checks for modified modules**
- [ ] **Step 4: Summarize which of the requested metric families are now implemented**
