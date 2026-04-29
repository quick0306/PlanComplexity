# CyberKnife MLC Metric Definitions

This appendix is generated from the shared metric-definition catalog.

## `mcs` - MCS (CyberKnife MLC)

- Group: MLC-based subset
- Symbol/short name: MCS
- Mathematical definition: MCS = sum_segments[(MU_segment / MU_plan) * AAV_segment * LSV_segment]
- Physical meaning: Overall modulation complexity of the delivered CyberKnife MLC apertures.
- Unit: dimensionless
- Inputs required: CyberKnife MLC segment apertures, segment MU, and interval grouping from beam-path XML
- Status: implemented
- Notes: Implements the paper-limited six-metric MLC subset only.

## `em` - EM

- Group: MLC-based subset
- Symbol/short name: EM
- Mathematical definition: EM = sum_segments[(MU_segment / MU_plan) * aperture edge metric]
- Physical meaning: Relative amount of aperture edge compared with open field area.
- Unit: dimensionless
- Inputs required: CyberKnife MLC segment apertures, segment MU, and interval grouping from beam-path XML
- Status: implemented
- Notes: Implements the paper-limited six-metric MLC subset only.

## `pi` - PI

- Group: MLC-based subset
- Symbol/short name: PI
- Mathematical definition: PI = sum_segments[(MU_segment / MU_plan) * aperture irregularity]
- Physical meaning: Irregularity of the CyberKnife MLC aperture shape.
- Unit: dimensionless
- Inputs required: CyberKnife MLC segment apertures, segment MU, and interval grouping from beam-path XML
- Status: implemented
- Notes: Implements the paper-limited six-metric MLC subset only.

## `pm` - PM

- Group: MLC-based subset
- Symbol/short name: PM
- Mathematical definition: PM = sum_intervals[(MU_interval / MU_plan) * (1 - weighted beam area / (MU_interval * union area_interval))]
- Physical meaning: Variation in aperture opening between successive segments.
- Unit: dimensionless
- Inputs required: CyberKnife MLC segment apertures, segment MU, and interval grouping from beam-path XML
- Status: implemented
- Notes: Implements the paper-limited six-metric MLC subset only.

## `lg` - LG (Mean Leaf Gap)

- Group: MLC-based subset
- Symbol/short name: LG
- Mathematical definition: LG = sum_segments[(MU_segment / MU_plan) * mean opposing leaf gap_segment]
- Physical meaning: Average gap between opposing CyberKnife MLC leaves.
- Unit: mm
- Inputs required: CyberKnife MLC segment apertures, segment MU, and interval grouping from beam-path XML
- Status: implemented
- Notes: Implements the paper-limited six-metric MLC subset only.

## `sas10` - SAS10 (CyberKnife)

- Group: MLC-based subset
- Symbol/short name: SAS10
- Mathematical definition: SAS10 = count(open leaf gaps < 10 mm) / count(all open leaf gaps)
- Physical meaning: Fraction of CyberKnife MLC gaps smaller than 10 mm.
- Unit: dimensionless
- Inputs required: CyberKnife MLC segment apertures, segment MU, and interval grouping from beam-path XML
- Status: implemented
- Notes: Implements the paper-limited six-metric MLC subset only.
