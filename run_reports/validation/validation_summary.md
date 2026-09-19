# Unified Complexity Validation Summary

Research validation profile: research

Generated at: 2026-09-19T14:33:23Z

Report ID: validation-research-20260919T143323UTC

Scope: This artifact is research/publication-ready evidence support and is not clinical deployment ready.

## Reference Suite

- Reference cases: 8
- Metric rows: 564
- Exact-equivalent metric rows: 280
- Exact failures: 0
- Analysis failures: 0
- Formula provenance failures: 0
- Reference exact green: True

## Case Formula Provenance And Analysis State

| Case | Domain | Required version | Baseline version | Observed version | Formula status | Analysis status | Reference exact green |
| --- | --- | --- | --- | --- | --- | --- | --- |

| vmat_truebeam_canonical | VMAT_IMRT | geometry-v4 | geometry-v4 | geometry-v4 | pass | pass | True |

| vmat_halcyon_edge | VMAT_IMRT | geometry-v4 | geometry-v4 | geometry-v4 | pass | pass | True |

| tomo_canonical | TOMO | tomo-v3 | tomo-v3 | tomo-v3 | pass | pass | True |

| tomo_default_inference_edge | TOMO | tomo-v3 | tomo-v3 | tomo-v3 | pass | pass | True |

| cyberknife_multiplan_canonical | CYBERKNIFE_MLC | geometry-v4 | geometry-v4 | geometry-v4 | pass | pass | True |

| cyberknife_precision_missing_xml_edge | CYBERKNIFE_MLC | geometry-v4 | geometry-v4 | geometry-v4 | pass | pass | True |

| aurora_canonical | AURORA |  |  |  | legacy-unversioned | pass | True |

| aurora_research_edge | AURORA |  |  |  | legacy-unversioned | pass | True |


## Domains

| Domain | Cases |
| --- | ---: |

| AURORA | 2 |

| CYBERKNIFE_MLC | 2 |

| TOMO | 2 |

| VMAT_IMRT | 2 |


## Cross-Tool And Literature Comparisons

| Platform | Metric | Comparator | Relationship | Status | N | MAE | Bias | RMSE | Notes |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |

| VMAT_IMRT | lt | UCoMX / LT | exact-equivalent | skipped | 0 |  |  |  | Unverified legacy sample: external artifact, input identity and formula provenance are absent. Same leaf-travel metric name and unit in the current UCoMX-oriented VMAT inventory. |

| VMAT_IMRT | lt_mlcx1 | UCoMX / LT_MLCX1 | derived-equivalent | skipped | 0 |  |  |  | Unverified legacy sample: external artifact, input identity and formula provenance are absent. Bank-specific derivative of the VMAT leaf-travel family; agreement is summarized but not exact-gated. |

| AURORA | projection_pitch_mean | AuroraPaper / projection_pitch_mean | not-comparable | skipped | 0 |  |  |  | Not eligible for numeric agreement statistics in this comparison layer. Aurora research metric is tracked in the mapping table but excluded from exact external-equivalence claims. |



## Traceable External Captures

- Historical captures: 1
- Captured external values: 10
- Values paired with input-hash-bound, full-precision internal observations: 6
- Pairs with independently established formula equivalence: 0
- Authenticated external executions: 0

See `external_benchmarks.json` for source/config hashes, workbook cells, formula status, and unrounded differences. Historical captures retain their provenance limits and do not enter an exactness or clinical gate. Legacy demonstration values above remain excluded.


## Interpretation Notes

- Exact-equivalent rows contribute to the reference-case exactness gate.
- Formula provenance and expected analysis state also contribute to the gate, including cases with no metric rows.
- Baseline agreement is regression evidence; an unversioned legacy baseline does not establish formula provenance.
- Derived-equivalent rows report agreement statistics and should not be reduced to simple pass/fail claims.
- Association-only and not-comparable evidence remains visible rather than being silently dropped.
- Aurora is included in the same artifact pipeline while preserving declared non-comparability where external equivalence is not established.
