# Unified Complexity Validation Summary

Research validation profile: research

Generated at: 2026-04-28T15:52:13Z

Report ID: validation-research-20260428T155213UTC

Scope: This artifact is research/publication-ready evidence support and is not clinical deployment ready.

## Reference Suite

- Reference cases: 8
- Metric rows: 446
- Exact-equivalent metric rows: 196
- Exact failures: 0
- Reference exact green: True

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

| VMAT_IMRT | lt | UCoMX / LT | exact-equivalent | compared | 1 | 0 | 0 | 0 | Same leaf-travel metric name and unit in the current UCoMX-oriented VMAT inventory. |

| VMAT_IMRT | lt_mlcx1 | UCoMX / LT_MLCX1 | derived-equivalent | compared | 1 | 0.06 | -0.06 | 0.06 | Bank-specific derivative of the VMAT leaf-travel family; agreement is summarized but not exact-gated. |

| AURORA | projection_pitch_mean | AuroraPaper / projection_pitch_mean | not-comparable | skipped | 0 |  |  |  | Not eligible for numeric agreement statistics in this comparison layer. Aurora research metric is tracked in the mapping table but excluded from exact external-equivalence claims. |


## Interpretation Notes

- Exact-equivalent rows contribute to the reference-case exactness gate.
- Derived-equivalent rows report agreement statistics and should not be reduced to simple pass/fail claims.
- Association-only and not-comparable evidence remains visible rather than being silently dropped.
- Aurora is included in the same artifact pipeline while preserving declared non-comparability where external equivalence is not established.
