# TOMO Metric Definitions

This appendix is generated from the shared metric-definition catalog.

## `mf` - MF

- Group: Delivery
- Symbol/short name: MF
- Mathematical definition: MF = mean(non-zero LOT) / max(LOT)
- Physical meaning: Ratio describing how strongly the sinogram is modulated overall.
- Unit: dimensionless
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `nproj_rot` - N proj,rot

- Group: Delivery
- Symbol/short name: N proj,rot
- Mathematical definition: N proj,rot = configured projections per rotation
- Physical meaning: Number of projections delivered in one full gantry rotation.
- Unit: count
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `nproj` - N proj

- Group: Delivery
- Symbol/short name: N proj
- Mathematical definition: N proj = number of sinogram projections
- Physical meaning: Total number of projections in the plan.
- Unit: count
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `nrot` - N rot

- Group: Delivery
- Symbol/short name: N rot
- Mathematical definition: N rot = N proj / N proj,rot
- Physical meaning: Total number of gantry rotations in the plan.
- Unit: count
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `projection_time_s` - PT

- Group: Delivery
- Symbol/short name: PT
- Mathematical definition: PT = projection time
- Physical meaning: Duration of each projection.
- Unit: s
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `gantry_period_s` - GP

- Group: Delivery
- Symbol/short name: GP
- Mathematical definition: GP = PT * N proj,rot
- Physical meaning: Time required for one full gantry rotation.
- Unit: s
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `treatment_time_s` - TT

- Group: Delivery
- Symbol/short name: TT
- Mathematical definition: TT = PT * N proj
- Physical meaning: Total beam-on treatment time.
- Unit: s
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `field_width_mm` - FW

- Group: Delivery
- Symbol/short name: FW
- Mathematical definition: FW = nominal tomotherapy field width
- Physical meaning: Nominal field width used for the plan.
- Unit: mm
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `pitch` - Pitch

- Group: Delivery
- Symbol/short name: Pitch
- Mathematical definition: Pitch = couch advance per rotation / field width
- Physical meaning: Ratio between couch travel per rotation and field width.
- Unit: dimensionless
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `couch_translation_mm` - CT

- Group: Delivery
- Symbol/short name: CT
- Mathematical definition: CT = total couch travel
- Physical meaning: Total couch translation during treatment.
- Unit: mm
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `couch_speed_mm_s` - CS

- Group: Delivery
- Symbol/short name: CS
- Mathematical definition: CS = CT / TT
- Physical meaning: Average couch translation speed.
- Unit: mm/s
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `target_length_mm` - TL

- Group: Delivery
- Symbol/short name: TL
- Mathematical definition: TL = couch translation - field width
- Physical meaning: Estimated target length covered by the plan.
- Unit: mm
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `ttdf_s_cgy` - TTDF

- Group: Delivery
- Symbol/short name: TTDF
- Mathematical definition: TTDF = TT / dose per fraction in cGy
- Physical meaning: Treatment time normalized by dose per fraction.
- Unit: s/cGy
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `mlot` - mLOT

- Group: Leaf open time
- Symbol/short name: mLOT
- Mathematical definition: mLOT = mean(LOT)
- Physical meaning: Mean leaf open time across all open leaves.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `sdlot` - sdLOT

- Group: Leaf open time
- Symbol/short name: sdLOT
- Mathematical definition: sdLOT = std(LOT)
- Physical meaning: Standard deviation of leaf open time.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `mdlot` - mdLOT

- Group: Leaf open time
- Symbol/short name: mdLOT
- Mathematical definition: mdLOT = median(LOT)
- Physical meaning: Median leaf open time.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `molot` - moLOT

- Group: Leaf open time
- Symbol/short name: moLOT
- Mathematical definition: moLOT = mode(LOT)
- Physical meaning: Most frequent leaf open time.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `maxlot` - maxLOT

- Group: Leaf open time
- Symbol/short name: maxLOT
- Mathematical definition: maxLOT = max(LOT)
- Physical meaning: Maximum leaf open time.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `minlot` - minLOT

- Group: Leaf open time
- Symbol/short name: minLOT
- Mathematical definition: minLOT = min(non-zero LOT)
- Physical meaning: Minimum non-zero leaf open time.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `klot` - kLOT

- Group: Leaf open time
- Symbol/short name: kLOT
- Mathematical definition: kLOT = kurtosis(LOT)
- Physical meaning: Kurtosis of the leaf open time distribution.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `slot` - sLOT

- Group: Leaf open time
- Symbol/short name: sLOT
- Mathematical definition: sLOT = skewness(LOT)
- Physical meaning: Skewness of the leaf open time distribution.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `clns_10ms` - CLNS10

- Group: Leaf open time
- Symbol/short name: CLNS10
- Mathematical definition: CLNS10 = count(0 < LOT < 10 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times shorter than 10 ms.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `clns_20ms` - CLNS20

- Group: Leaf open time
- Symbol/short name: CLNS20
- Mathematical definition: CLNS20 = count(0 < LOT < 20 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times shorter than 20 ms.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `clns_30ms` - CLNS30

- Group: Leaf open time
- Symbol/short name: CLNS30
- Mathematical definition: CLNS30 = count(0 < LOT < 30 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times shorter than 30 ms.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `clns_50ms` - CLNS50

- Group: Leaf open time
- Symbol/short name: CLNS50
- Mathematical definition: CLNS50 = count(0 < LOT < 50 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times shorter than 50 ms.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `clns_pt_10ms` - CLNSpt10

- Group: Leaf open time
- Symbol/short name: CLNSpt10
- Mathematical definition: CLNSpt10 = count(LOT > projection time - 10 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times within 10 ms of the projection time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `clns_pt_20ms` - CLNSpt20

- Group: Leaf open time
- Symbol/short name: CLNSpt20
- Mathematical definition: CLNSpt20 = count(LOT > projection time - 20 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times within 20 ms of the projection time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `clns_pt_30ms` - CLNSpt30

- Group: Leaf open time
- Symbol/short name: CLNSpt30
- Mathematical definition: CLNSpt30 = count(LOT > projection time - 30 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times within 30 ms of the projection time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `clns_pt_50ms` - CLNSpt50

- Group: Leaf open time
- Symbol/short name: CLNSpt50
- Mathematical definition: CLNSpt50 = count(LOT > projection time - 50 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times within 50 ms of the projection time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `mflot` - mFLOT

- Group: Leaf open time
- Symbol/short name: mFLOT
- Mathematical definition: mFLOT = mean(FLOT)
- Physical meaning: Mean fractional leaf open time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `sdflot` - sdFLOT

- Group: Leaf open time
- Symbol/short name: sdFLOT
- Mathematical definition: sdFLOT = std(FLOT)
- Physical meaning: Standard deviation of fractional leaf open time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `mdflot` - mdFLOT

- Group: Leaf open time
- Symbol/short name: mdFLOT
- Mathematical definition: mdFLOT = median(FLOT)
- Physical meaning: Median fractional leaf open time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `moflot` - moFLOT

- Group: Leaf open time
- Symbol/short name: moFLOT
- Mathematical definition: moFLOT = mode(FLOT)
- Physical meaning: Most frequent fractional leaf open time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `maxflot` - maxFLOT

- Group: Leaf open time
- Symbol/short name: maxFLOT
- Mathematical definition: maxFLOT = max(FLOT)
- Physical meaning: Maximum fractional leaf open time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `minflot` - minFLOT

- Group: Leaf open time
- Symbol/short name: minFLOT
- Mathematical definition: minFLOT = min(non-zero FLOT)
- Physical meaning: Minimum non-zero fractional leaf open time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `cfns_0_1` - CFNS0.1

- Group: Leaf open time
- Symbol/short name: CFNS0.1
- Mathematical definition: CFNS0.1 = count(FLOT < 0.1) / count(non-zero FLOT)
- Physical meaning: Fraction of fractional leaf open times below 0.1.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `cfns_0_25` - CFNS0.25

- Group: Leaf open time
- Symbol/short name: CFNS0.25
- Mathematical definition: CFNS0.25 = count(FLOT < 0.25) / count(non-zero FLOT)
- Physical meaning: Fraction of fractional leaf open times below 0.25.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `cfns_0_5` - CFNS0.5

- Group: Leaf open time
- Symbol/short name: CFNS0.5
- Mathematical definition: CFNS0.5 = count(FLOT < 0.5) / count(non-zero FLOT)
- Physical meaning: Fraction of fractional leaf open times below 0.5.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `cfns_0_75` - CFNS0.75

- Group: Leaf open time
- Symbol/short name: CFNS0.75
- Mathematical definition: CFNS0.75 = count(FLOT < 0.75) / count(non-zero FLOT)
- Physical meaning: Fraction of fractional leaf open times below 0.75.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `ta` - TA

- Group: Sinogram geometry
- Symbol/short name: TA
- Mathematical definition: TA = mean projection treatment width across the sinogram
- Physical meaning: Average width of the treated sinogram area per projection.
- Unit: leaf slots
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `ncc` - nCC

- Group: Sinogram geometry
- Symbol/short name: nCC
- Mathematical definition: nCC = mean number of connected open components per projection
- Physical meaning: Average number of disconnected open components per projection.
- Unit: count
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `lengthcc` - lengthCC

- Group: Sinogram geometry
- Symbol/short name: lengthCC
- Mathematical definition: lengthCC = mean connected-component length in the sinogram
- Physical meaning: Average length of connected open sinogram components.
- Unit: leaf slots
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `fdisc` - fDISC

- Group: Sinogram geometry
- Symbol/short name: fDISC
- Mathematical definition: fDISC = fraction(projections with more than one connected component)
- Physical meaning: Fraction of projections with discontinuous open regions.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `cls` - CLS

- Group: Sinogram geometry
- Symbol/short name: CLS
- Mathematical definition: CLS = mean[(N_leaves - open leaves) / N_leaves] over projections
- Physical meaning: Fraction of leaves that remain closed across the full sinogram width.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `clsin` - CLSin

- Group: Sinogram geometry
- Symbol/short name: CLSin
- Mathematical definition: CLSin = mean_nonempty_rows(closed leaves inside treatment span / total number of leaf columns)
- Physical meaning: Closed leaf score within the treatment area.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `clsinarea` - CLSinarea

- Group: Sinogram geometry
- Symbol/short name: CLSinarea
- Mathematical definition: CLSinarea = mean(closed leaves inside the treatment area / treatment area)
- Physical meaning: Closed leaf score within the treatment area, normalized by area.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `clsindisc` - CLSindisc

- Group: Sinogram geometry
- Symbol/short name: CLSindisc
- Mathematical definition: CLSindisc = CLSin restricted to discontinuous projections
- Physical meaning: Closed leaf score within discontinuous treatment projections.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `clsinareadisc` - CLSinareadisc

- Group: Sinogram geometry
- Symbol/short name: CLSinareadisc
- Mathematical definition: CLSinareadisc = area-normalized CLSin restricted to discontinuous projections
- Physical meaning: Area-normalized closed leaf score for discontinuous projections.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `centroid` - Centroid

- Group: Sinogram geometry
- Symbol/short name: Centroid
- Mathematical definition: Centroid = mean lateral centroid of open leaves over projections
- Physical meaning: Average lateral position of the open sinogram barycenter.
- Unit: leaf-index displacement
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `l0ns` - L0NS

- Group: Sinogram geometry
- Symbol/short name: L0NS
- Mathematical definition: L0NS = mean fraction of open leaves with 0 open nearest neighbors
- Physical meaning: Fraction of open leaves with no open nearest neighbors.
- Unit: proportion
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `l1ns` - L1NS

- Group: Sinogram geometry
- Symbol/short name: L1NS
- Mathematical definition: L1NS = mean fraction of open leaves with 1 open nearest neighbor
- Physical meaning: Fraction of open leaves with one open nearest neighbor.
- Unit: proportion
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `l2ns` - L2NS

- Group: Sinogram geometry
- Symbol/short name: L2NS
- Mathematical definition: L2NS = mean fraction of open leaves with 2 open nearest neighbors
- Physical meaning: Fraction of open leaves with two open nearest neighbors.
- Unit: proportion
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `lotv` - LOTV

- Group: Leaf open time
- Symbol/short name: LOTV
- Mathematical definition: LOTV = mean over leaves of [ sum(max(LOT) - abs(delta LOT)) / ((N_proj - 1) * max(LOT)) ]
- Physical meaning: Variability of leaf open time across consecutive projections.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `elotv_1` - ELOTV-1

- Group: Leaf open time
- Symbol/short name: ELOTV-1
- Mathematical definition: ELOTV-1 = mean normalized abs(LOT_i - LOT_{i+1}) over leaves
- Physical meaning: Extended leaf open time variability using a one-projection offset.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `elotv_5` - ELOTV-5

- Group: Leaf open time
- Symbol/short name: ELOTV-5
- Mathematical definition: ELOTV-5 = mean normalized abs(LOT_i - LOT_{i+5}) over leaves
- Physical meaning: Extended leaf open time variability using a five-projection offset.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `pstv` - PSTV

- Group: Sinogram modulation
- Symbol/short name: PSTV
- Mathematical definition: PSTV = EPSTV with delta projection = 1 and delta leaf = 1
- Physical meaning: Plan sinogram time variability across neighboring projections and leaves.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `epstv_1_1` - EPSTV-1,1

- Group: Sinogram modulation
- Symbol/short name: EPSTV-1,1
- Mathematical definition: EPSTV-1,1 = mean of abs(delta projection) + abs(delta leaf) sinogram differences for offsets (1,1)
- Physical meaning: Extended plan sinogram time variability using one-step projection and leaf offsets.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `epstv_1_0` - EPSTV-1,0

- Group: Sinogram modulation
- Symbol/short name: EPSTV-1,0
- Mathematical definition: EPSTV-1,0 = mean sinogram difference for projection offset 1 and leaf offset 0
- Physical meaning: Extended plan sinogram time variability using only a projection offset.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `epstv_0_1` - EPSTV-0,1

- Group: Sinogram modulation
- Symbol/short name: EPSTV-0,1
- Mathematical definition: EPSTV-0,1 = mean sinogram difference for projection offset 0 and leaf offset 1
- Physical meaning: Extended plan sinogram time variability using only a leaf offset.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `mi` - MI

- Group: Sinogram modulation
- Symbol/short name: MI
- Mathematical definition: MI = trapezoidal integral over threshold factor f of the mean fraction of directional sinogram differences exceeding f * sd(FLOT)
- Physical meaning: Overall modulation index of the tomotherapy sinogram.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `noc` - nOC

- Group: Sinogram modulation
- Symbol/short name: nOC
- Mathematical definition: nOC = mean per leaf of [2 * merged open intervals / N_proj]
- Physical meaning: Average number of leaf openings and closures per leaf.
- Unit: count
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `msa` - mSA

- Group: Sinogram modulation
- Symbol/short name: mSA
- Mathematical definition: mSA = sum(position * mean leaf opening) / sum(mean leaf opening)
- Physical meaning: Mean left-right asymmetry of the sinogram.
- Unit: leaf-index displacement
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `msi` - mSI

- Group: Sinogram modulation
- Symbol/short name: mSI
- Mathematical definition: mSI = mean leaf-open intensity over leaves
- Physical meaning: Mean sinogram intensity.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `mdsi` - mdSI

- Group: Sinogram modulation
- Symbol/short name: mdSI
- Mathematical definition: mdSI = median leaf-open intensity over leaves
- Physical meaning: Median sinogram intensity.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## `sdsi` - sdSI

- Group: Sinogram modulation
- Symbol/short name: sdSI
- Mathematical definition: sdSI = std leaf-open intensity over leaves
- Physical meaning: Standard deviation of sinogram intensity.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.
