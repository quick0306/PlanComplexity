# Aurora RTPLAN File Comparison

This table combines DICOM structural parameters with representative Aurora V4 results from `jia.csv`.

| File | Plan Name | Machine | Beams | Beam Organization | Beam Direction Pattern | Control Points | Rotations | Axial Travel (mm) | Travel/Rotation (mm) | Dual-Layer MLC Channels | mean_BA | mean_MCS_Aurora |
| --- | --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 1RTPLAN_001.dcm | A10FSVMATaX20 | R0_Clinical Rese | 2 | bidirectional pair | B1:backward, B2:forward | 812 | 9.0 | 1662.0 | 184.67 | MLCX1=60, MLCX2=58 | 609.5 | 0.0559 |
| 1RTPLAN_002.dcm | A10SVMATaX20 | R0_Clinical Rese | 2 | bidirectional pair | B1:backward, B2:forward | 812 | 9.0 | 1530.0 | 170.00 | MLCX1=60, MLCX2=58 | 467.1 | 0.0526 |
| 1RTPLAN_003.dcm | A10FSVMATaX20 | R0_Clinical Rese | 2 | bidirectional pair | B1:backward, B2:forward | 812 | 9.0 | 1896.0 | 210.67 | MLCX1=60, MLCX2=58 | 627.0 | 0.0596 |
| 1RTPLAN_004.dcm | A10SVMATaX20 | R0_Clinical Rese | 2 | bidirectional pair | B1:backward, B2:forward | 812 | 9.0 | 1860.0 | 206.67 | MLCX1=60, MLCX2=58 | 523.7 | 0.0534 |
| 1RTPLAN_005.dcm | A10FSVMATaX20 | R0_Clinical Rese | 2 | bidirectional pair | B1:backward, B2:forward | 812 | 9.0 | 2000.0 | 222.22 | MLCX1=60, MLCX2=58 | 637.9 | 0.0555 |
| RTPLAN_001.dcm | A10FSVMATax2.5-20260402 | R05-26010001HMLC | 2 | bidirectional pair | B1:backward, B2:forward | 812 | 9.0 | 270.0 | 30.00 | MLCX1=76, MLCX2=74 | 83.8 | 0.0510 |
| RTPLAN_002.dcm | A10FSVMATax2.5-20260402 | R05-26010001HMLC | 2 | bidirectional pair | B1:backward, B2:forward | 812 | 9.0 | 276.0 | 30.67 | MLCX1=76, MLCX2=74 | 86.8 | 0.0534 |
| RTPLAN_003.dcm | A10FVMATax2.5-20260319 | R0_Clinical Rese | 2 | bidirectional pair | B1:backward, B2:forward | 812 | 9.0 | 300.0 | 33.33 | MLCX1=60, MLCX2=58 | 62.2 | 0.0582 |
| RTPLAN_004.dcm | A10FSVMATax2.5-1 | R0_Clinical Rese | 2 | bidirectional pair | B1:backward, B2:forward | 812 | 9.0 | 297.0 | 33.00 | MLCX1=60, MLCX2=58 | 68.5 | 0.0553 |
| RTPLAN_005.dcm | A10FSVMATax2.5-20260324 | R0_Clinical Rese | 2 | bidirectional pair | B1:backward, B2:forward | 812 | 9.0 | 300.0 | 33.33 | MLCX1=60, MLCX2=58 | 69.2 | 0.0567 |
| RTPLAN_006.dcm | A10FSVMATaX2.5-20260321 | R0_Clinical Rese | 2 | bidirectional pair | B1:backward, B2:forward | 812 | 9.0 | 264.0 | 29.33 | MLCX1=60, MLCX2=58 | 77.9 | 0.0628 |
| RTPLAN_007.dcm | A10FVMATax2.5-20260414 | R0_Clinical Rese | 1 | single-beam | B1:backward | 856 | 9.5 | 149.2 | 15.71 | MLCX1=60, MLCX2=58 | 56.8 | 0.0482 |
| RTPLAN_008.dcm | A10FSVMATax2.5-20260321 | R0_Clinical Rese | 2 | bidirectional pair | B1:backward, B2:forward | 812 | 9.0 | 298.5 | 33.17 | MLCX1=60, MLCX2=58 | 68.6 | 0.0552 |
| RTPLAN_009.dcm | A10FSVMATax2.5-20260324 | R0_Clinical Rese | 2 | bidirectional pair | B1:backward, B2:forward | 812 | 9.0 | 282.0 | 31.33 | MLCX1=60, MLCX2=58 | 66.6 | 0.0561 |
| RTPLAN_010.dcm | A10FSVMATax2.5-20260324 | R0_Clinical Rese | 2 | bidirectional pair | B1:backward, B2:forward | 812 | 9.0 | 300.0 | 33.33 | MLCX1=60, MLCX2=58 | 65.6 | 0.0527 |
| RTPLAN_57661.dcm | A10FSVMATax2.5-20260321 | R0_Clinical Rese | 2 | bidirectional pair | B1:backward, B2:forward | 812 | 9.0 | 300.0 | 33.33 | MLCX1=60, MLCX2=58 | 63.8 | 0.0502 |

## Quick Reading

- `1RTPLAN_001` to `1RTPLAN_005` form a long-travel family with very large travel-per-rotation values (about 170 to 222 mm/rotation).
- `RTPLAN_003` to `RTPLAN_010` plus `RTPLAN_57661` form a short-travel family centered near 29 to 33 mm/rotation.
- `RTPLAN_001` and `RTPLAN_002` stand out as a different hardware/channel configuration (`MLCX1=76`, `MLCX2=74`).
- `RTPLAN_007` is the main outlier because it is a single-beam, 9.5-rotation plan rather than a two-beam forward/backward pair.