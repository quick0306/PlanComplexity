# Metric Definitions

This document summarizes the mathematical definitions and physical meanings of all metrics currently implemented in the project.

Definitions are written to match the current code implementation. They are not automatically identical to the original publication notation unless noted.

## VMAT/IMRT

### `mus` - MUs

- Group: Plan prescription
- Symbol/short name: MUs
- Mathematical definition: MUs = sum_beams(MU_beam)
- Physical meaning: Total monitor units delivered by the plan.
- Unit: MU
- Inputs required: Plan MU, prescription, fraction count, beam list
- Status: implemented
- Notes: None

### `pmu` - PMU

- Group: Plan prescription
- Symbol/short name: PMU
- Mathematical definition: PMU = MUs * (2 Gy / fraction dose in Gy)
- Physical meaning: Monitor units normalized to a standard 2 Gy fraction.
- Unit: MU
- Inputs required: Plan MU, prescription, fraction count, beam list
- Status: implemented
- Notes: None

### `muca` - MUCA

- Group: Plan prescription
- Symbol/short name: MUCA
- Mathematical definition: MUCA = MUs / N_control_arcs
- Physical meaning: Average monitor units delivered per control arc.
- Unit: MU/control arc
- Inputs required: Plan MU, prescription, fraction count, beam list
- Status: implemented
- Notes: None

### `fraction_dose_gy` - Prescribed Dose

- Group: Plan prescription
- Symbol/short name: Prescribed Dose
- Mathematical definition: Fraction dose = prescribed dose / number of fractions
- Physical meaning: Dose prescribed per fraction.
- Unit: Gy
- Inputs required: Plan MU, prescription, fraction count, beam list
- Status: implemented
- Notes: None

### `fractions_count` - Fractions

- Group: Plan prescription
- Symbol/short name: Fractions
- Mathematical definition: Fractions = N_fx
- Physical meaning: Number of planned treatment fractions.
- Unit: count
- Inputs required: Plan MU, prescription, fraction count, beam list
- Status: implemented
- Notes: None

### `mucgy` - MUcGy

- Group: Plan prescription
- Symbol/short name: MUcGy
- Mathematical definition: MUcGy = MUs / prescribed dose in cGy
- Physical meaning: Monitor units delivered per centigray of prescribed dose.
- Unit: MU/cGy
- Inputs required: Plan MU, prescription, fraction count, beam list
- Status: implemented
- Notes: None

### `lt` - LT

- Group: Leaf travel
- Symbol/short name: LT
- Mathematical definition: LT = weighted mean over control arcs of total leaf travel between adjacent apertures
- Physical meaning: Average total leaf travel across a control arc.
- Unit: mm
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `lt_mlcx1` - LT MLCX1

- Group: Leaf travel
- Symbol/short name: LT MLCX1
- Mathematical definition: Same formula as LT, but computed using MLCX1 apertures only.
- Physical meaning: Average total leaf travel across a control arc. Reported for MLCX1.
- Unit: mm
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LT.

### `lt_mlcx2` - LT MLCX2

- Group: Leaf travel
- Symbol/short name: LT MLCX2
- Mathematical definition: Same formula as LT, but computed using MLCX2 apertures only.
- Physical meaning: Average total leaf travel across a control arc. Reported for MLCX2.
- Unit: mm
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LT.

### `ltmu` - LTMU

- Group: Leaf travel
- Symbol/short name: LTMU
- Mathematical definition: LTMU = sum(control-arc leaf travel) / MU_beam
- Physical meaning: Leaf travel normalized by delivered monitor units.
- Unit: mm/MU
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `ltmu_mlcx1` - LTMU MLCX1

- Group: Leaf travel
- Symbol/short name: LTMU MLCX1
- Mathematical definition: Same formula as LTMU, but computed using MLCX1 apertures only.
- Physical meaning: Leaf travel normalized by delivered monitor units. Reported for MLCX1.
- Unit: mm/MU
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTMU.

### `ltmu_mlcx2` - LTMU MLCX2

- Group: Leaf travel
- Symbol/short name: LTMU MLCX2
- Mathematical definition: Same formula as LTMU, but computed using MLCX2 apertures only.
- Physical meaning: Leaf travel normalized by delivered monitor units. Reported for MLCX2.
- Unit: mm/MU
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTMU.

### `ltnlmu` - LTNLMU

- Group: Leaf travel
- Symbol/short name: LTNLMU
- Mathematical definition: LTNLMU = sum(leaf travel / active leaves) / MU_beam
- Physical meaning: Leaf travel per involved leaf, normalized by monitor units.
- Unit: mm/(leaf*MU)
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `ltnlmu_mlcx1` - LTNLMU MLCX1

- Group: Leaf travel
- Symbol/short name: LTNLMU MLCX1
- Mathematical definition: Same formula as LTNLMU, but computed using MLCX1 apertures only.
- Physical meaning: Leaf travel per involved leaf, normalized by monitor units. Reported for MLCX1.
- Unit: mm/(leaf*MU)
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTNLMU.

### `ltnlmu_mlcx2` - LTNLMU MLCX2

- Group: Leaf travel
- Symbol/short name: LTNLMU MLCX2
- Mathematical definition: Same formula as LTNLMU, but computed using MLCX2 apertures only.
- Physical meaning: Leaf travel per involved leaf, normalized by monitor units. Reported for MLCX2.
- Unit: mm/(leaf*MU)
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTNLMU.

### `nl` - NL

- Group: Leaf travel
- Symbol/short name: NL
- Mathematical definition: NL = weighted mean over control points of the number of active leaf pairs
- Physical meaning: Average number of leaves actively shaping the aperture.
- Unit: count
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `nl_mlcx1` - NL MLCX1

- Group: Leaf travel
- Symbol/short name: NL MLCX1
- Mathematical definition: Same formula as NL, but computed using MLCX1 apertures only.
- Physical meaning: Average number of leaves actively shaping the aperture. Reported for MLCX1.
- Unit: count
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for NL.

### `nl_mlcx2` - NL MLCX2

- Group: Leaf travel
- Symbol/short name: NL MLCX2
- Mathematical definition: Same formula as NL, but computed using MLCX2 apertures only.
- Physical meaning: Average number of leaves actively shaping the aperture. Reported for MLCX2.
- Unit: count
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for NL.

### `ltnl` - LTNL

- Group: Leaf travel
- Symbol/short name: LTNL
- Mathematical definition: LTNL = weighted mean of (leaf travel / active leaves)
- Physical meaning: Leaf travel normalized by the number of involved leaves.
- Unit: mm/leaf
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `ltnl_mlcx1` - LTNL MLCX1

- Group: Leaf travel
- Symbol/short name: LTNL MLCX1
- Mathematical definition: Same formula as LTNL, but computed using MLCX1 apertures only.
- Physical meaning: Leaf travel normalized by the number of involved leaves. Reported for MLCX1.
- Unit: mm/leaf
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTNL.

### `ltnl_mlcx2` - LTNL MLCX2

- Group: Leaf travel
- Symbol/short name: LTNL MLCX2
- Mathematical definition: Same formula as LTNL, but computed using MLCX2 apertures only.
- Physical meaning: Leaf travel normalized by the number of involved leaves. Reported for MLCX2.
- Unit: mm/leaf
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTNL.

### `al` - AL

- Group: Arc geometry
- Symbol/short name: AL
- Mathematical definition: AL = total gantry travel / N_beams
- Physical meaning: Average arc length delivered per beam.
- Unit: deg
- Inputs required: Beam gantry rotation angle and beam MU
- Status: implemented
- Notes: None

### `lna` - LNA

- Group: Leaf travel
- Symbol/short name: LNA
- Mathematical definition: LNA = weighted mean of (leaf travel / active leaves / gantry-step)
- Physical meaning: Leaf travel per involved leaf and per unit gantry travel.
- Unit: mm/(leaf*deg)
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `lna_mlcx1` - LNA MLCX1

- Group: Leaf travel
- Symbol/short name: LNA MLCX1
- Mathematical definition: Same formula as LNA, but computed using MLCX1 apertures only.
- Physical meaning: Leaf travel per involved leaf and per unit gantry travel. Reported for MLCX1.
- Unit: mm/(leaf*deg)
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LNA.

### `lna_mlcx2` - LNA MLCX2

- Group: Leaf travel
- Symbol/short name: LNA MLCX2
- Mathematical definition: Same formula as LNA, but computed using MLCX2 apertures only.
- Physical meaning: Leaf travel per involved leaf and per unit gantry travel. Reported for MLCX2.
- Unit: mm/(leaf*deg)
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LNA.

### `cal` - CAL

- Group: Arc geometry
- Symbol/short name: CAL
- Mathematical definition: CAL = total gantry travel / N_control_arcs
- Physical meaning: Average control-arc length between successive control points.
- Unit: deg/control arc
- Inputs required: Beam gantry rotation angle and beam MU
- Status: implemented
- Notes: None

### `gt` - GT

- Group: Arc geometry
- Symbol/short name: GT
- Mathematical definition: GT = sum_beams(abs(gantry rotation angle))
- Physical meaning: Total gantry travel delivered by the plan.
- Unit: deg
- Inputs required: Beam gantry rotation angle and beam MU
- Status: implemented
- Notes: None

### `mudeg` - MUdeg

- Group: Arc geometry
- Symbol/short name: MUdeg
- Mathematical definition: MUdeg = MUs / GT
- Physical meaning: Monitor units delivered per degree of gantry rotation.
- Unit: MU/deg
- Inputs required: Beam gantry rotation angle and beam MU
- Status: implemented
- Notes: None

### `ltal` - LTAL

- Group: Leaf travel
- Symbol/short name: LTAL
- Mathematical definition: LTAL = weighted mean of (leaf travel / gantry-step)
- Physical meaning: Leaf travel normalized by unit gantry angle.
- Unit: mm/deg
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `ltal_mlcx1` - LTAL MLCX1

- Group: Leaf travel
- Symbol/short name: LTAL MLCX1
- Mathematical definition: Same formula as LTAL, but computed using MLCX1 apertures only.
- Physical meaning: Leaf travel normalized by unit gantry angle. Reported for MLCX1.
- Unit: mm/deg
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTAL.

### `ltal_mlcx2` - LTAL MLCX2

- Group: Leaf travel
- Symbol/short name: LTAL MLCX2
- Mathematical definition: Same formula as LTAL, but computed using MLCX2 apertures only.
- Physical meaning: Leaf travel normalized by unit gantry angle. Reported for MLCX2.
- Unit: mm/deg
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTAL.

### `narcs` - NArcs

- Group: Plan prescription
- Symbol/short name: NArcs
- Mathematical definition: NArcs = number of treatment beams/arcs
- Physical meaning: Number of treatment arcs or beams contributing to the plan.
- Unit: count
- Inputs required: Plan MU, prescription, fraction count, beam list
- Status: implemented
- Notes: None

### `mdrv` - mDRV

- Group: Delivery dynamics
- Symbol/short name: mDRV
- Mathematical definition: mDRV = mean(delta dose-rate / delta gantry)
- Physical meaning: Mean variation of dose rate during delivery.
- Unit: MU/(min*deg)
- Inputs required: Control-point MLC motion, dose rate, gantry angle, and meterset timing
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `mdrv_mlcx1` - mDRV MLCX1

- Group: Delivery dynamics
- Symbol/short name: mDRV MLCX1
- Mathematical definition: Same formula as mDRV, but computed using MLCX1 apertures only.
- Physical meaning: Mean variation of dose rate during delivery. Reported for MLCX1.
- Unit: MU/(min*deg)
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for mDRV.

### `mdrv_mlcx2` - mDRV MLCX2

- Group: Delivery dynamics
- Symbol/short name: mDRV MLCX2
- Mathematical definition: Same formula as mDRV, but computed using MLCX2 apertures only.
- Physical meaning: Mean variation of dose rate during delivery. Reported for MLCX2.
- Unit: MU/(min*deg)
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for mDRV.

### `mgsv` - mGSV

- Group: Delivery dynamics
- Symbol/short name: mGSV
- Mathematical definition: mGSV = mean(delta gantry-speed / delta gantry)
- Physical meaning: Mean variation of gantry speed during delivery.
- Unit: deg/s/deg
- Inputs required: Control-point MLC motion, dose rate, gantry angle, and meterset timing
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `mgsv_mlcx1` - mGSV MLCX1

- Group: Delivery dynamics
- Symbol/short name: mGSV MLCX1
- Mathematical definition: Same formula as mGSV, but computed using MLCX1 apertures only.
- Physical meaning: Mean variation of gantry speed during delivery. Reported for MLCX1.
- Unit: deg/s/deg
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for mGSV.

### `mgsv_mlcx2` - mGSV MLCX2

- Group: Delivery dynamics
- Symbol/short name: mGSV MLCX2
- Mathematical definition: Same formula as mGSV, but computed using MLCX2 apertures only.
- Physical meaning: Mean variation of gantry speed during delivery. Reported for MLCX2.
- Unit: deg/s/deg
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for mGSV.

### `dr` - DR

- Group: Delivery dynamics
- Symbol/short name: DR
- Mathematical definition: DR = mean(control-point dose rate)
- Physical meaning: Average dose rate used during delivery.
- Unit: MU/min
- Inputs required: Control-point MLC motion, dose rate, gantry angle, and meterset timing
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `dr_mlcx1` - DR MLCX1

- Group: Delivery dynamics
- Symbol/short name: DR MLCX1
- Mathematical definition: Same formula as DR, but computed using MLCX1 apertures only.
- Physical meaning: Average dose rate used during delivery. Reported for MLCX1.
- Unit: MU/min
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for DR.

### `dr_mlcx2` - DR MLCX2

- Group: Delivery dynamics
- Symbol/short name: DR MLCX2
- Mathematical definition: Same formula as DR, but computed using MLCX2 apertures only.
- Physical meaning: Average dose rate used during delivery. Reported for MLCX2.
- Unit: MU/min
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for DR.

### `gs` - GS

- Group: Delivery dynamics
- Symbol/short name: GS
- Mathematical definition: GS = mean(control-point gantry speed)
- Physical meaning: Average gantry speed during arc delivery.
- Unit: deg/s
- Inputs required: Control-point MLC motion, dose rate, gantry angle, and meterset timing
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `gs_mlcx1` - GS MLCX1

- Group: Delivery dynamics
- Symbol/short name: GS MLCX1
- Mathematical definition: Same formula as GS, but computed using MLCX1 apertures only.
- Physical meaning: Average gantry speed during arc delivery. Reported for MLCX1.
- Unit: deg/s
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for GS.

### `gs_mlcx2` - GS MLCX2

- Group: Delivery dynamics
- Symbol/short name: GS MLCX2
- Mathematical definition: Same formula as GS, but computed using MLCX2 apertures only.
- Physical meaning: Average gantry speed during arc delivery. Reported for MLCX2.
- Unit: deg/s
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for GS.

### `ls` - LS

- Group: Delivery dynamics
- Symbol/short name: LS
- Mathematical definition: LS = mean(leaf speed)
- Physical meaning: Average leaf speed during delivery.
- Unit: mm/s
- Inputs required: Control-point MLC motion, dose rate, gantry angle, and meterset timing
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `ls_mlcx1` - LS MLCX1

- Group: Delivery dynamics
- Symbol/short name: LS MLCX1
- Mathematical definition: Same formula as LS, but computed using MLCX1 apertures only.
- Physical meaning: Average leaf speed during delivery. Reported for MLCX1.
- Unit: mm/s
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LS.

### `ls_mlcx2` - LS MLCX2

- Group: Delivery dynamics
- Symbol/short name: LS MLCX2
- Mathematical definition: Same formula as LS, but computed using MLCX2 apertures only.
- Physical meaning: Average leaf speed during delivery. Reported for MLCX2.
- Unit: mm/s
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LS.

### `mcsv` - MCSv

- Group: McNiven-style modulation
- Symbol/short name: MCSv
- Mathematical definition: MCSv = weighted mean[((AAV_i + AAV_{i+1}) / 2) * ((LSV_i + LSV_{i+1}) / 2)]
- Physical meaning: Overall aperture modulation score combining area and leaf sequence variability.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `mcsv_mlcx1` - MCSv MLCX1

- Group: McNiven-style modulation
- Symbol/short name: MCSv MLCX1
- Mathematical definition: Same formula as MCSv, but computed using MLCX1 apertures only.
- Physical meaning: Overall aperture modulation score combining area and leaf sequence variability. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MCSv.

### `mcsv_mlcx2` - MCSv MLCX2

- Group: McNiven-style modulation
- Symbol/short name: MCSv MLCX2
- Mathematical definition: Same formula as MCSv, but computed using MLCX2 apertures only.
- Physical meaning: Overall aperture modulation score combining area and leaf sequence variability. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MCSv.

### `aav` - AAV

- Group: McNiven-style modulation
- Symbol/short name: AAV
- Mathematical definition: AAV = aperture area / arc-level union aperture area, then weighted over the arc
- Physical meaning: Variability of aperture area across control points.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `aav_mlcx1` - AAV MLCX1

- Group: McNiven-style modulation
- Symbol/short name: AAV MLCX1
- Mathematical definition: Same formula as AAV, but computed using MLCX1 apertures only.
- Physical meaning: Variability of aperture area across control points. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for AAV.

### `aav_mlcx2` - AAV MLCX2

- Group: McNiven-style modulation
- Symbol/short name: AAV MLCX2
- Mathematical definition: Same formula as AAV, but computed using MLCX2 apertures only.
- Physical meaning: Variability of aperture area across control points. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for AAV.

### `lsv` - LSV

- Group: McNiven-style modulation
- Symbol/short name: LSV
- Mathematical definition: LSV = bank_LSV(left) * bank_LSV(right), then weighted over the arc
- Physical meaning: Variability of the leaf sequence pattern across the aperture.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `lsv_mlcx1` - LSV MLCX1

- Group: McNiven-style modulation
- Symbol/short name: LSV MLCX1
- Mathematical definition: Same formula as LSV, but computed using MLCX1 apertures only.
- Physical meaning: Variability of the leaf sequence pattern across the aperture. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LSV.

### `lsv_mlcx2` - LSV MLCX2

- Group: McNiven-style modulation
- Symbol/short name: LSV MLCX2
- Mathematical definition: Same formula as LSV, but computed using MLCX2 apertures only.
- Physical meaning: Variability of the leaf sequence pattern across the aperture. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LSV.

### `tg` - TG

- Group: McNiven-style modulation
- Symbol/short name: TG
- Mathematical definition: TG = weighted mean of adjacent-leaf left/right offset magnitudes
- Physical meaning: Average tongue-and-groove offset between neighboring leaves.
- Unit: mm
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `tg_mlcx1` - TG MLCX1

- Group: McNiven-style modulation
- Symbol/short name: TG MLCX1
- Mathematical definition: Same formula as TG, but computed using MLCX1 apertures only.
- Physical meaning: Average tongue-and-groove offset between neighboring leaves. Reported for MLCX1.
- Unit: mm
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for TG.

### `tg_mlcx2` - TG MLCX2

- Group: McNiven-style modulation
- Symbol/short name: TG MLCX2
- Mathematical definition: Same formula as TG, but computed using MLCX2 apertures only.
- Physical meaning: Average tongue-and-groove offset between neighboring leaves. Reported for MLCX2.
- Unit: mm
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for TG.

### `mi_0_2` - MI(0.2)

- Group: MI family
- Symbol/short name: MI(0.2)
- Mathematical definition: MI(k=0.2) = (MIs, MIa, MIt) at threshold factor k = 0.2
- Physical meaning: Modulation index using a 0.2 threshold factor.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: The base key returns a tuple of speed, acceleration, and total MI components before flattening.

### `mi_0_2_mis` - MI(0.2) Speed

- Group: MI components
- Symbol/short name: MI(0.2) Speed
- Mathematical definition: MIs(0.2) = mean_beams[ mean_CP min(v / sigma_v, 0.2) ]
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 0.2.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

### `mi_0_2_mia` - MI(0.2) Acceleration

- Group: MI components
- Symbol/short name: MI(0.2) Acceleration
- Mathematical definition: MIa(0.2) = mean_beams[ mean_CP min(max(v / sigma_v, a / (alpha * sigma_a)), 0.2) ]
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 0.2.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

### `mi_0_2_mit` - MI(0.2) Total

- Group: MI components
- Symbol/short name: MI(0.2) Total
- Mathematical definition: MIt(0.2) = weighted mean over control points of min(max(v / sigma_v, a / (alpha * sigma_a)), 0.2)
- Physical meaning: Total modulation index with threshold factor 0.2.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

### `mi_0_2_mlcx1_mis` - MI(0.2) MLCX1 Speed

- Group: MI components
- Symbol/short name: MI(0.2) MLCX1 Speed
- Mathematical definition: Same speed-component MI formula as MI(0.2), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 0.2 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

### `mi_0_2_mlcx1_mia` - MI(0.2) MLCX1 Acceleration

- Group: MI components
- Symbol/short name: MI(0.2) MLCX1 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(0.2), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 0.2 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

### `mi_0_2_mlcx1_mit` - MI(0.2) MLCX1 Total

- Group: MI components
- Symbol/short name: MI(0.2) MLCX1 Total
- Mathematical definition: Same total-component MI formula as MI(0.2), but restricted to MLCX1 leaf positions.
- Physical meaning: Total modulation index with threshold factor 0.2 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

### `mi_0_2_mlcx2_mis` - MI(0.2) MLCX2 Speed

- Group: MI components
- Symbol/short name: MI(0.2) MLCX2 Speed
- Mathematical definition: Same speed-component MI formula as MI(0.2), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 0.2 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

### `mi_0_2_mlcx2_mia` - MI(0.2) MLCX2 Acceleration

- Group: MI components
- Symbol/short name: MI(0.2) MLCX2 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(0.2), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 0.2 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

### `mi_0_2_mlcx2_mit` - MI(0.2) MLCX2 Total

- Group: MI components
- Symbol/short name: MI(0.2) MLCX2 Total
- Mathematical definition: Same total-component MI formula as MI(0.2), but restricted to MLCX2 leaf positions.
- Physical meaning: Total modulation index with threshold factor 0.2 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

### `mi_0_5` - MI(0.5)

- Group: MI family
- Symbol/short name: MI(0.5)
- Mathematical definition: MI(k=0.5) = (MIs, MIa, MIt) at threshold factor k = 0.5
- Physical meaning: Modulation index using a 0.5 threshold factor.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: The base key returns a tuple of speed, acceleration, and total MI components before flattening.

### `mi_0_5_mis` - MI(0.5) Speed

- Group: MI components
- Symbol/short name: MI(0.5) Speed
- Mathematical definition: MIs(0.5) = mean_beams[ mean_CP min(v / sigma_v, 0.5) ]
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 0.5.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

### `mi_0_5_mia` - MI(0.5) Acceleration

- Group: MI components
- Symbol/short name: MI(0.5) Acceleration
- Mathematical definition: MIa(0.5) = mean_beams[ mean_CP min(max(v / sigma_v, a / (alpha * sigma_a)), 0.5) ]
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 0.5.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

### `mi_0_5_mit` - MI(0.5) Total

- Group: MI components
- Symbol/short name: MI(0.5) Total
- Mathematical definition: MIt(0.5) = weighted mean over control points of min(max(v / sigma_v, a / (alpha * sigma_a)), 0.5)
- Physical meaning: Total modulation index with threshold factor 0.5.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

### `mi_0_5_mlcx1_mis` - MI(0.5) MLCX1 Speed

- Group: MI components
- Symbol/short name: MI(0.5) MLCX1 Speed
- Mathematical definition: Same speed-component MI formula as MI(0.5), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 0.5 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

### `mi_0_5_mlcx1_mia` - MI(0.5) MLCX1 Acceleration

- Group: MI components
- Symbol/short name: MI(0.5) MLCX1 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(0.5), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 0.5 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

### `mi_0_5_mlcx1_mit` - MI(0.5) MLCX1 Total

- Group: MI components
- Symbol/short name: MI(0.5) MLCX1 Total
- Mathematical definition: Same total-component MI formula as MI(0.5), but restricted to MLCX1 leaf positions.
- Physical meaning: Total modulation index with threshold factor 0.5 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

### `mi_0_5_mlcx2_mis` - MI(0.5) MLCX2 Speed

- Group: MI components
- Symbol/short name: MI(0.5) MLCX2 Speed
- Mathematical definition: Same speed-component MI formula as MI(0.5), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 0.5 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

### `mi_0_5_mlcx2_mia` - MI(0.5) MLCX2 Acceleration

- Group: MI components
- Symbol/short name: MI(0.5) MLCX2 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(0.5), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 0.5 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

### `mi_0_5_mlcx2_mit` - MI(0.5) MLCX2 Total

- Group: MI components
- Symbol/short name: MI(0.5) MLCX2 Total
- Mathematical definition: Same total-component MI formula as MI(0.5), but restricted to MLCX2 leaf positions.
- Physical meaning: Total modulation index with threshold factor 0.5 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

### `mi_1_0` - MI(1.0)

- Group: MI family
- Symbol/short name: MI(1.0)
- Mathematical definition: MI(k=1.0) = (MIs, MIa, MIt) at threshold factor k = 1.0
- Physical meaning: Modulation index using a 1.0 threshold factor.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: The base key returns a tuple of speed, acceleration, and total MI components before flattening.

### `mi_1_0_mis` - MI(1.0) Speed

- Group: MI components
- Symbol/short name: MI(1.0) Speed
- Mathematical definition: MIs(1.0) = mean_beams[ mean_CP min(v / sigma_v, 1.0) ]
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 1.0.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

### `mi_1_0_mia` - MI(1.0) Acceleration

- Group: MI components
- Symbol/short name: MI(1.0) Acceleration
- Mathematical definition: MIa(1.0) = mean_beams[ mean_CP min(max(v / sigma_v, a / (alpha * sigma_a)), 1.0) ]
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 1.0.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

### `mi_1_0_mit` - MI(1.0) Total

- Group: MI components
- Symbol/short name: MI(1.0) Total
- Mathematical definition: MIt(1.0) = weighted mean over control points of min(max(v / sigma_v, a / (alpha * sigma_a)), 1.0)
- Physical meaning: Total modulation index with threshold factor 1.0.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

### `mi_1_0_mlcx1_mis` - MI(1.0) MLCX1 Speed

- Group: MI components
- Symbol/short name: MI(1.0) MLCX1 Speed
- Mathematical definition: Same speed-component MI formula as MI(1.0), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 1.0 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

### `mi_1_0_mlcx1_mia` - MI(1.0) MLCX1 Acceleration

- Group: MI components
- Symbol/short name: MI(1.0) MLCX1 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(1.0), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 1.0 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

### `mi_1_0_mlcx1_mit` - MI(1.0) MLCX1 Total

- Group: MI components
- Symbol/short name: MI(1.0) MLCX1 Total
- Mathematical definition: Same total-component MI formula as MI(1.0), but restricted to MLCX1 leaf positions.
- Physical meaning: Total modulation index with threshold factor 1.0 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

### `mi_1_0_mlcx2_mis` - MI(1.0) MLCX2 Speed

- Group: MI components
- Symbol/short name: MI(1.0) MLCX2 Speed
- Mathematical definition: Same speed-component MI formula as MI(1.0), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 1.0 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

### `mi_1_0_mlcx2_mia` - MI(1.0) MLCX2 Acceleration

- Group: MI components
- Symbol/short name: MI(1.0) MLCX2 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(1.0), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 1.0 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

### `mi_1_0_mlcx2_mit` - MI(1.0) MLCX2 Total

- Group: MI components
- Symbol/short name: MI(1.0) MLCX2 Total
- Mathematical definition: Same total-component MI formula as MI(1.0), but restricted to MLCX2 leaf positions.
- Physical meaning: Total modulation index with threshold factor 1.0 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

### `mi_2_0` - MI(2.0)

- Group: MI family
- Symbol/short name: MI(2.0)
- Mathematical definition: MI(k=2.0) = (MIs, MIa, MIt) at threshold factor k = 2.0
- Physical meaning: Modulation index using a 2.0 threshold factor.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: The base key returns a tuple of speed, acceleration, and total MI components before flattening.

### `mi_2_0_mis` - MI(2.0) Speed

- Group: MI components
- Symbol/short name: MI(2.0) Speed
- Mathematical definition: MIs(2.0) = mean_beams[ mean_CP min(v / sigma_v, 2.0) ]
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 2.0.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

### `mi_2_0_mia` - MI(2.0) Acceleration

- Group: MI components
- Symbol/short name: MI(2.0) Acceleration
- Mathematical definition: MIa(2.0) = mean_beams[ mean_CP min(max(v / sigma_v, a / (alpha * sigma_a)), 2.0) ]
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 2.0.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

### `mi_2_0_mit` - MI(2.0) Total

- Group: MI components
- Symbol/short name: MI(2.0) Total
- Mathematical definition: MIt(2.0) = weighted mean over control points of min(max(v / sigma_v, a / (alpha * sigma_a)), 2.0)
- Physical meaning: Total modulation index with threshold factor 2.0.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

### `mi_2_0_mlcx1_mis` - MI(2.0) MLCX1 Speed

- Group: MI components
- Symbol/short name: MI(2.0) MLCX1 Speed
- Mathematical definition: Same speed-component MI formula as MI(2.0), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 2.0 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

### `mi_2_0_mlcx1_mia` - MI(2.0) MLCX1 Acceleration

- Group: MI components
- Symbol/short name: MI(2.0) MLCX1 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(2.0), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 2.0 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

### `mi_2_0_mlcx1_mit` - MI(2.0) MLCX1 Total

- Group: MI components
- Symbol/short name: MI(2.0) MLCX1 Total
- Mathematical definition: Same total-component MI formula as MI(2.0), but restricted to MLCX1 leaf positions.
- Physical meaning: Total modulation index with threshold factor 2.0 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

### `mi_2_0_mlcx2_mis` - MI(2.0) MLCX2 Speed

- Group: MI components
- Symbol/short name: MI(2.0) MLCX2 Speed
- Mathematical definition: Same speed-component MI formula as MI(2.0), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 2.0 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

### `mi_2_0_mlcx2_mia` - MI(2.0) MLCX2 Acceleration

- Group: MI components
- Symbol/short name: MI(2.0) MLCX2 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(2.0), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 2.0 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

### `mi_2_0_mlcx2_mit` - MI(2.0) MLCX2 Total

- Group: MI components
- Symbol/short name: MI(2.0) MLCX2 Total
- Mathematical definition: Same total-component MI formula as MI(2.0), but restricted to MLCX2 leaf positions.
- Physical meaning: Total modulation index with threshold factor 2.0 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

### `dt` - dt

- Group: Delivery dynamics
- Symbol/short name: dt
- Mathematical definition: dt = mean(control-point time increment) * N_control_points
- Physical meaning: Beam-on delivery time.
- Unit: s
- Inputs required: Control-point MLC motion, dose rate, gantry angle, and meterset timing
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `dt_mlcx1` - dt MLCX1

- Group: Delivery dynamics
- Symbol/short name: dt MLCX1
- Mathematical definition: Same formula as dt, but computed using MLCX1 apertures only.
- Physical meaning: Beam-on delivery time. Reported for MLCX1.
- Unit: s
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for dt.

### `dt_mlcx2` - dt MLCX2

- Group: Delivery dynamics
- Symbol/short name: dt MLCX2
- Mathematical definition: Same formula as dt, but computed using MLCX2 apertures only.
- Physical meaning: Beam-on delivery time. Reported for MLCX2.
- Unit: s
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for dt.

### `pi` - PI

- Group: Shape modulation
- Symbol/short name: PI
- Mathematical definition: PI = perimeter^2 / (4 * pi * area), aggregated over apertures
- Physical meaning: Irregularity of the aperture shape relative to its area.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `pi_mlcx1` - PI MLCX1

- Group: Shape modulation
- Symbol/short name: PI MLCX1
- Mathematical definition: Same formula as PI, but computed using MLCX1 apertures only.
- Physical meaning: Irregularity of the aperture shape relative to its area. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for PI.

### `pi_mlcx2` - PI MLCX2

- Group: Shape modulation
- Symbol/short name: PI MLCX2
- Mathematical definition: Same formula as PI, but computed using MLCX2 apertures only.
- Physical meaning: Irregularity of the aperture shape relative to its area. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for PI.

### `pm` - PM

- Group: Shape modulation
- Symbol/short name: PM
- Mathematical definition: PM = mean over adjacent control points of normalized aperture-area change
- Physical meaning: Variation in aperture area between successive control points.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `pm_mlcx1` - PM MLCX1

- Group: Shape modulation
- Symbol/short name: PM MLCX1
- Mathematical definition: Same formula as PM, but computed using MLCX1 apertures only.
- Physical meaning: Variation in aperture area between successive control points. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for PM.

### `pm_mlcx2` - PM MLCX2

- Group: Shape modulation
- Symbol/short name: PM MLCX2
- Mathematical definition: Same formula as PM, but computed using MLCX2 apertures only.
- Physical meaning: Variation in aperture area between successive control points. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for PM.

### `md` - MD

- Group: Shape modulation
- Symbol/short name: MD
- Mathematical definition: MD = union-area / weighted mean aperture area
- Physical meaning: Degree of modulation present in the delivered field shapes.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `md_mlcx1` - MD MLCX1

- Group: Shape modulation
- Symbol/short name: MD MLCX1
- Mathematical definition: Same formula as MD, but computed using MLCX1 apertures only.
- Physical meaning: Degree of modulation present in the delivered field shapes. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MD.

### `md_mlcx2` - MD MLCX2

- Group: Shape modulation
- Symbol/short name: MD MLCX2
- Mathematical definition: Same formula as MD, but computed using MLCX2 apertures only.
- Physical meaning: Degree of modulation present in the delivered field shapes. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MD.

### `pa` - PA

- Group: Aperture geometry
- Symbol/short name: PA
- Mathematical definition: PA = weighted mean(aperture area)
- Physical meaning: Average beam's-eye-view aperture area.
- Unit: mm^2
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `pa_mlcx1` - PA MLCX1

- Group: Aperture geometry
- Symbol/short name: PA MLCX1
- Mathematical definition: Same formula as PA, but computed using MLCX1 apertures only.
- Physical meaning: Average beam's-eye-view aperture area. Reported for MLCX1.
- Unit: mm^2
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for PA.

### `pa_mlcx2` - PA MLCX2

- Group: Aperture geometry
- Symbol/short name: PA MLCX2
- Mathematical definition: Same formula as PA, but computed using MLCX2 apertures only.
- Physical meaning: Average beam's-eye-view aperture area. Reported for MLCX2.
- Unit: mm^2
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for PA.

### `efs` - EFS

- Group: Aperture geometry
- Symbol/short name: EFS
- Mathematical definition: EFS = weighted mean(4 * area / perimeter)
- Physical meaning: Equivalent square field size of the aperture.
- Unit: mm
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `efs_mlcx1` - EFS MLCX1

- Group: Aperture geometry
- Symbol/short name: EFS MLCX1
- Mathematical definition: Same formula as EFS, but computed using MLCX1 apertures only.
- Physical meaning: Equivalent square field size of the aperture. Reported for MLCX1.
- Unit: mm
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for EFS.

### `efs_mlcx2` - EFS MLCX2

- Group: Aperture geometry
- Symbol/short name: EFS MLCX2
- Mathematical definition: Same formula as EFS, but computed using MLCX2 apertures only.
- Physical meaning: Equivalent square field size of the aperture. Reported for MLCX2.
- Unit: mm
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for EFS.

### `psmall` - psmall

- Group: Aperture geometry
- Symbol/short name: psmall
- Mathematical definition: psmall = weighted fraction(EFS < 30 mm)
- Physical meaning: Fraction of apertures classified as small fields.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `psmall_mlcx1` - psmall MLCX1

- Group: Aperture geometry
- Symbol/short name: psmall MLCX1
- Mathematical definition: Same formula as psmall, but computed using MLCX1 apertures only.
- Physical meaning: Fraction of apertures classified as small fields. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for psmall.

### `psmall_mlcx2` - psmall MLCX2

- Group: Aperture geometry
- Symbol/short name: psmall MLCX2
- Mathematical definition: Same formula as psmall, but computed using MLCX2 apertures only.
- Physical meaning: Fraction of apertures classified as small fields. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for psmall.

### `sas_5mm` - SAS5mm

- Group: Aperture geometry
- Symbol/short name: SAS5mm
- Mathematical definition: SAS5mm = active leaf gaps below 5 mm / all active leaf gaps
- Physical meaning: Fraction of leaf gaps smaller than 5 mm.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `sas_5mm_mlcx1` - SAS5mm MLCX1

- Group: Aperture geometry
- Symbol/short name: SAS5mm MLCX1
- Mathematical definition: Same formula as SAS5mm, but computed using MLCX1 apertures only.
- Physical meaning: Fraction of leaf gaps smaller than 5 mm. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for SAS5mm.

### `sas_5mm_mlcx2` - SAS5mm MLCX2

- Group: Aperture geometry
- Symbol/short name: SAS5mm MLCX2
- Mathematical definition: Same formula as SAS5mm, but computed using MLCX2 apertures only.
- Physical meaning: Fraction of leaf gaps smaller than 5 mm. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for SAS5mm.

### `sas_10mm` - SAS10mm

- Group: Aperture geometry
- Symbol/short name: SAS10mm
- Mathematical definition: SAS10mm = active leaf gaps below 10 mm / all active leaf gaps
- Physical meaning: Fraction of leaf gaps smaller than 10 mm.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `sas_10mm_mlcx1` - SAS10mm MLCX1

- Group: Aperture geometry
- Symbol/short name: SAS10mm MLCX1
- Mathematical definition: Same formula as SAS10mm, but computed using MLCX1 apertures only.
- Physical meaning: Fraction of leaf gaps smaller than 10 mm. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for SAS10mm.

### `sas_10mm_mlcx2` - SAS10mm MLCX2

- Group: Aperture geometry
- Symbol/short name: SAS10mm MLCX2
- Mathematical definition: Same formula as SAS10mm, but computed using MLCX2 apertures only.
- Physical meaning: Fraction of leaf gaps smaller than 10 mm. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for SAS10mm.

### `sas_20mm` - SAS20mm

- Group: Aperture geometry
- Symbol/short name: SAS20mm
- Mathematical definition: SAS20mm = active leaf gaps below 20 mm / all active leaf gaps
- Physical meaning: Fraction of leaf gaps smaller than 20 mm.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `sas_20mm_mlcx1` - SAS20mm MLCX1

- Group: Aperture geometry
- Symbol/short name: SAS20mm MLCX1
- Mathematical definition: Same formula as SAS20mm, but computed using MLCX1 apertures only.
- Physical meaning: Fraction of leaf gaps smaller than 20 mm. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for SAS20mm.

### `sas_20mm_mlcx2` - SAS20mm MLCX2

- Group: Aperture geometry
- Symbol/short name: SAS20mm MLCX2
- Mathematical definition: Same formula as SAS20mm, but computed using MLCX2 apertures only.
- Physical meaning: Fraction of leaf gaps smaller than 20 mm. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for SAS20mm.

### `em` - EM

- Group: Aperture geometry
- Symbol/short name: EM
- Mathematical definition: EM = aperture edge metric calculated from BEV perimeter relative to area
- Physical meaning: Relative amount of aperture edge compared with open field area.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `em_mlcx1` - EM MLCX1

- Group: Aperture geometry
- Symbol/short name: EM MLCX1
- Mathematical definition: Same formula as EM, but computed using MLCX1 apertures only.
- Physical meaning: Relative amount of aperture edge compared with open field area. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for EM.

### `em_mlcx2` - EM MLCX2

- Group: Aperture geometry
- Symbol/short name: EM MLCX2
- Mathematical definition: Same formula as EM, but computed using MLCX2 apertures only.
- Physical meaning: Relative amount of aperture edge compared with open field area. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for EM.

### `bjar` - BJAR

- Group: Aperture geometry
- Symbol/short name: BJAR
- Mathematical definition: BJAR = aperture area / jaw-defined area
- Physical meaning: Ratio between aperture area and jaw-defined area.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: None

### `mad` - MAD

- Group: Aperture geometry
- Symbol/short name: MAD
- Mathematical definition: MAD = mean distance of open leaf ends from the beam central axis
- Physical meaning: Average distance of the aperture opening from the beam central axis.
- Unit: mm
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `mad_mlcx1` - MAD MLCX1

- Group: Aperture geometry
- Symbol/short name: MAD MLCX1
- Mathematical definition: Same formula as MAD, but computed using MLCX1 apertures only.
- Physical meaning: Average distance of the aperture opening from the beam central axis. Reported for MLCX1.
- Unit: mm
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MAD.

### `mad_mlcx2` - MAD MLCX2

- Group: Aperture geometry
- Symbol/short name: MAD MLCX2
- Mathematical definition: Same formula as MAD, but computed using MLCX2 apertures only.
- Physical meaning: Average distance of the aperture opening from the beam central axis. Reported for MLCX2.
- Unit: mm
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MAD.

### `alg` - ALG

- Group: Aperture geometry
- Symbol/short name: ALG
- Mathematical definition: ALG = mean(opposing leaf gap over active leaf pairs)
- Physical meaning: Average gap between opposing leaf pairs.
- Unit: mm
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `alg_mlcx1` - ALG MLCX1

- Group: Aperture geometry
- Symbol/short name: ALG MLCX1
- Mathematical definition: Same formula as ALG, but computed using MLCX1 apertures only.
- Physical meaning: Average gap between opposing leaf pairs. Reported for MLCX1.
- Unit: mm
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for ALG.

### `alg_mlcx2` - ALG MLCX2

- Group: Aperture geometry
- Symbol/short name: ALG MLCX2
- Mathematical definition: Same formula as ALG, but computed using MLCX2 apertures only.
- Physical meaning: Average gap between opposing leaf pairs. Reported for MLCX2.
- Unit: mm
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for ALG.

### `alg_sd` - ALG SD

- Group: Aperture geometry
- Symbol/short name: ALG SD
- Mathematical definition: ALG SD = std(opposing leaf gap over active leaf pairs)
- Physical meaning: Standard deviation of the opposing leaf gap.
- Unit: mm
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `alg_sd_mlcx1` - ALG SD MLCX1

- Group: Aperture geometry
- Symbol/short name: ALG SD MLCX1
- Mathematical definition: Same formula as ALG SD, but computed using MLCX1 apertures only.
- Physical meaning: Standard deviation of the opposing leaf gap. Reported for MLCX1.
- Unit: mm
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for ALG SD.

### `alg_sd_mlcx2` - ALG SD MLCX2

- Group: Aperture geometry
- Symbol/short name: ALG SD MLCX2
- Mathematical definition: Same formula as ALG SD, but computed using MLCX2 apertures only.
- Physical meaning: Standard deviation of the opposing leaf gap. Reported for MLCX2.
- Unit: mm
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for ALG SD.

### `perimeter` - P

- Group: Aperture geometry
- Symbol/short name: P
- Mathematical definition: P = mean aperture perimeter in beam's-eye view
- Physical meaning: Average perimeter of the beam's-eye-view aperture.
- Unit: mm
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `perimeter_mlcx1` - P MLCX1

- Group: Aperture geometry
- Symbol/short name: P MLCX1
- Mathematical definition: Same formula as P, but computed using MLCX1 apertures only.
- Physical meaning: Average perimeter of the beam's-eye-view aperture. Reported for MLCX1.
- Unit: mm
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for P.

### `perimeter_mlcx2` - P MLCX2

- Group: Aperture geometry
- Symbol/short name: P MLCX2
- Mathematical definition: Same formula as P, but computed using MLCX2 apertures only.
- Physical meaning: Average perimeter of the beam's-eye-view aperture. Reported for MLCX2.
- Unit: mm
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for P.

### `asr` - ASR

- Group: Aperture geometry
- Symbol/short name: ASR
- Mathematical definition: ASR = mean number of disconnected open aperture sub-regions
- Physical meaning: Average number of disconnected open sub-regions in the aperture.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `asr_mlcx1` - ASR MLCX1

- Group: Aperture geometry
- Symbol/short name: ASR MLCX1
- Mathematical definition: Same formula as ASR, but computed using MLCX1 apertures only.
- Physical meaning: Average number of disconnected open sub-regions in the aperture. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for ASR.

### `asr_mlcx2` - ASR MLCX2

- Group: Aperture geometry
- Symbol/short name: ASR MLCX2
- Mathematical definition: Same formula as ASR, but computed using MLCX2 apertures only.
- Physical meaning: Average number of disconnected open sub-regions in the aperture. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for ASR.

### `axjd` - AXJD

- Group: Aperture geometry
- Symbol/short name: AXJD
- Mathematical definition: AXJD = mean distance between aperture extent and X jaws
- Physical meaning: Distance between aperture extent and X jaws.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: None

### `ayjd` - AYJD

- Group: Aperture geometry
- Symbol/short name: AYJD
- Mathematical definition: AYJD = mean distance between aperture extent and Y jaws
- Physical meaning: Distance between aperture extent and Y jaws.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: None

### `cam` - CAM

- Group: Aperture geometry
- Symbol/short name: CAM
- Mathematical definition: CAM = converted-aperture complexity metric from transformed field geometry
- Physical meaning: Aperture complexity score based on converted field geometry.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `cam_mlcx1` - CAM MLCX1

- Group: Aperture geometry
- Symbol/short name: CAM MLCX1
- Mathematical definition: Same formula as CAM, but computed using MLCX1 apertures only.
- Physical meaning: Aperture complexity score based on converted field geometry. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for CAM.

### `cam_mlcx2` - CAM MLCX2

- Group: Aperture geometry
- Symbol/short name: CAM MLCX2
- Mathematical definition: Same formula as CAM, but computed using MLCX2 apertures only.
- Physical meaning: Aperture complexity score based on converted field geometry. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for CAM.

### `eam` - EAM

- Group: Aperture geometry
- Symbol/short name: EAM
- Mathematical definition: EAM = combined edge-and-area aperture complexity metric
- Physical meaning: Combined edge-and-area measure of aperture complexity.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

### `eam_mlcx1` - EAM MLCX1

- Group: Aperture geometry
- Symbol/short name: EAM MLCX1
- Mathematical definition: Same formula as EAM, but computed using MLCX1 apertures only.
- Physical meaning: Combined edge-and-area measure of aperture complexity. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for EAM.

### `eam_mlcx2` - EAM MLCX2

- Group: Aperture geometry
- Symbol/short name: EAM MLCX2
- Mathematical definition: Same formula as EAM, but computed using MLCX2 apertures only.
- Physical meaning: Combined edge-and-area measure of aperture complexity. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for EAM.

### `mlc_speed_acc` - MLC Speed and Acceleration Proportions (Park 2015)

- Group: Delivery dynamics
- Symbol/short name: MLC Speed/Acceleration Profile
- Mathematical definition: For each leaf, compute the proportion of valid intervals falling into each Park 2015 speed/acceleration bin; then average over leaves and beams.
- Physical meaning: Leaf-wise mean proportions for Park et al. VMAT delivery bins. Speed bins: 0-4, 4-8, 8-12, 12-16, 16-20 mm/s. Acceleration bins: 0-40, 40-80, 80-120, 120-160, 160-200 mm/s^2.
- Unit: dimensionless
- Inputs required: Control-point MLC motion, dose rate, gantry angle, and meterset timing
- Status: implemented
- Notes: The base key returns binned speed/acceleration proportions and summary statistics before flattening.

### `speed_0_4` - Park Speed 0-4 mm/s

- Group: Motion bins
- Symbol/short name: Park Speed 0-4 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 0-4 mm/s) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with speed in 0-4 mm/s.
- Unit: proportion
- Inputs required: Per-leaf MLC speed over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 speed-bin proportion, averaged over leaves.

### `speed_4_8` - Park Speed 4-8 mm/s

- Group: Motion bins
- Symbol/short name: Park Speed 4-8 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 4-8 mm/s) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with speed in 4-8 mm/s.
- Unit: proportion
- Inputs required: Per-leaf MLC speed over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 speed-bin proportion, averaged over leaves.

### `speed_8_12` - Park Speed 8-12 mm/s

- Group: Motion bins
- Symbol/short name: Park Speed 8-12 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 8-12 mm/s) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with speed in 8-12 mm/s.
- Unit: proportion
- Inputs required: Per-leaf MLC speed over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 speed-bin proportion, averaged over leaves.

### `speed_12_16` - Park Speed 12-16 mm/s

- Group: Motion bins
- Symbol/short name: Park Speed 12-16 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 12-16 mm/s) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with speed in 12-16 mm/s.
- Unit: proportion
- Inputs required: Per-leaf MLC speed over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 speed-bin proportion, averaged over leaves.

### `speed_16_20` - Park Speed 16-20 mm/s

- Group: Motion bins
- Symbol/short name: Park Speed 16-20 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 16-20 mm/s) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with speed in 16-20 mm/s.
- Unit: proportion
- Inputs required: Per-leaf MLC speed over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 speed-bin proportion, averaged over leaves.

### `acc_0_40` - Park Acceleration 0-40 mm/s^2

- Group: Motion bins
- Symbol/short name: Park Acceleration 0-40 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 0-40 mm/s^2) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with acceleration in 0-40 mm/s^2.
- Unit: proportion
- Inputs required: Per-leaf MLC acceleration over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 acceleration-bin proportion, averaged over leaves.

### `acc_40_80` - Park Acceleration 40-80 mm/s^2

- Group: Motion bins
- Symbol/short name: Park Acceleration 40-80 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 40-80 mm/s^2) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with acceleration in 40-80 mm/s^2.
- Unit: proportion
- Inputs required: Per-leaf MLC acceleration over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 acceleration-bin proportion, averaged over leaves.

### `acc_80_120` - Park Acceleration 80-120 mm/s^2

- Group: Motion bins
- Symbol/short name: Park Acceleration 80-120 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 80-120 mm/s^2) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with acceleration in 80-120 mm/s^2.
- Unit: proportion
- Inputs required: Per-leaf MLC acceleration over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 acceleration-bin proportion, averaged over leaves.

### `acc_120_160` - Park Acceleration 120-160 mm/s^2

- Group: Motion bins
- Symbol/short name: Park Acceleration 120-160 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 120-160 mm/s^2) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with acceleration in 120-160 mm/s^2.
- Unit: proportion
- Inputs required: Per-leaf MLC acceleration over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 acceleration-bin proportion, averaged over leaves.

### `acc_160_200` - Park Acceleration 160-200 mm/s^2

- Group: Motion bins
- Symbol/short name: Park Acceleration 160-200 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 160-200 mm/s^2) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with acceleration in 160-200 mm/s^2.
- Unit: proportion
- Inputs required: Per-leaf MLC acceleration over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 acceleration-bin proportion, averaged over leaves.

### `speed_average` - Mean Leaf Speed (mm/s)

- Group: Motion bins
- Symbol/short name: Mean Leaf Speed (mm/s)
- Mathematical definition: mean_leaf(mean_interval(speed))
- Physical meaning: Leaf-wise mean proportions for Park et al. VMAT delivery bins. Speed bins: 0-4, 4-8, 8-12, 12-16, 16-20 mm/s. Acceleration bins: 0-40, 40-80, 80-120, 120-160, 160-200 mm/s^2.
- Unit: mm/s
- Inputs required: Per-leaf motion time series
- Status: implemented_flattened
- Notes: Park 2015 summary statistic flattened for export.

### `acc_average` - Mean Leaf Acceleration (mm/s^2)

- Group: Motion bins
- Symbol/short name: Mean Leaf Acceleration (mm/s^2)
- Mathematical definition: mean_leaf(mean_interval(acceleration))
- Physical meaning: Leaf-wise mean proportions for Park et al. VMAT delivery bins. Speed bins: 0-4, 4-8, 8-12, 12-16, 16-20 mm/s. Acceleration bins: 0-40, 40-80, 80-120, 120-160, 160-200 mm/s^2.
- Unit: mm/s^2
- Inputs required: Per-leaf motion time series
- Status: implemented_flattened
- Notes: Park 2015 summary statistic flattened for export.

### `speed_std` - Mean Leaf Speed SD (mm/s)

- Group: Motion bins
- Symbol/short name: Mean Leaf Speed SD (mm/s)
- Mathematical definition: mean_leaf(std_interval(speed))
- Physical meaning: Leaf-wise mean proportions for Park et al. VMAT delivery bins. Speed bins: 0-4, 4-8, 8-12, 12-16, 16-20 mm/s. Acceleration bins: 0-40, 40-80, 80-120, 120-160, 160-200 mm/s^2.
- Unit: mm/s
- Inputs required: Per-leaf motion time series
- Status: implemented_flattened
- Notes: Park 2015 summary statistic flattened for export.

### `acc_std` - Mean Leaf Acceleration SD (mm/s^2)

- Group: Motion bins
- Symbol/short name: Mean Leaf Acceleration SD (mm/s^2)
- Mathematical definition: mean_leaf(std_interval(acceleration))
- Physical meaning: Leaf-wise mean proportions for Park et al. VMAT delivery bins. Speed bins: 0-4, 4-8, 8-12, 12-16, 16-20 mm/s. Acceleration bins: 0-40, 40-80, 80-120, 120-160, 160-200 mm/s^2.
- Unit: mm/s^2
- Inputs required: Per-leaf motion time series
- Status: implemented_flattened
- Notes: Park 2015 summary statistic flattened for export.

### `mlcx1_speed_0_4` - MLCX1 Park Speed 0-4 mm/s

- Group: Motion bins
- Symbol/short name: MLCX1 Park Speed 0-4 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 0-4 mm/s) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

### `mlcx1_speed_4_8` - MLCX1 Park Speed 4-8 mm/s

- Group: Motion bins
- Symbol/short name: MLCX1 Park Speed 4-8 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 4-8 mm/s) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

### `mlcx1_speed_8_12` - MLCX1 Park Speed 8-12 mm/s

- Group: Motion bins
- Symbol/short name: MLCX1 Park Speed 8-12 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 8-12 mm/s) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

### `mlcx1_speed_12_16` - MLCX1 Park Speed 12-16 mm/s

- Group: Motion bins
- Symbol/short name: MLCX1 Park Speed 12-16 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 12-16 mm/s) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

### `mlcx1_speed_16_20` - MLCX1 Park Speed 16-20 mm/s

- Group: Motion bins
- Symbol/short name: MLCX1 Park Speed 16-20 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 16-20 mm/s) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

### `mlcx1_acc_0_40` - MLCX1 Park Acceleration 0-40 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX1 Park Acceleration 0-40 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 0-40 mm/s^2) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

### `mlcx1_acc_40_80` - MLCX1 Park Acceleration 40-80 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX1 Park Acceleration 40-80 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 40-80 mm/s^2) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

### `mlcx1_acc_80_120` - MLCX1 Park Acceleration 80-120 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX1 Park Acceleration 80-120 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 80-120 mm/s^2) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

### `mlcx1_acc_120_160` - MLCX1 Park Acceleration 120-160 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX1 Park Acceleration 120-160 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 120-160 mm/s^2) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

### `mlcx1_acc_160_200` - MLCX1 Park Acceleration 160-200 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX1 Park Acceleration 160-200 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 160-200 mm/s^2) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

### `mlcx1_speed_average` - MLCX1 Mean Leaf Speed (mm/s)

- Group: Motion bins
- Symbol/short name: MLCX1 Mean Leaf Speed (mm/s)
- Mathematical definition: mean_leaf(mean_interval(speed)), restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: mm/s
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

### `mlcx1_acc_average` - MLCX1 Mean Leaf Acceleration (mm/s^2)

- Group: Motion bins
- Symbol/short name: MLCX1 Mean Leaf Acceleration (mm/s^2)
- Mathematical definition: mean_leaf(mean_interval(acceleration)), restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: mm/s^2
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

### `mlcx1_speed_std` - MLCX1 Mean Leaf Speed SD (mm/s)

- Group: Motion bins
- Symbol/short name: MLCX1 Mean Leaf Speed SD (mm/s)
- Mathematical definition: mean_leaf(std_interval(speed)), restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: mm/s
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

### `mlcx1_acc_std` - MLCX1 Mean Leaf Acceleration SD (mm/s^2)

- Group: Motion bins
- Symbol/short name: MLCX1 Mean Leaf Acceleration SD (mm/s^2)
- Mathematical definition: mean_leaf(std_interval(acceleration)), restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: mm/s^2
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

### `mlcx2_speed_0_4` - MLCX2 Park Speed 0-4 mm/s

- Group: Motion bins
- Symbol/short name: MLCX2 Park Speed 0-4 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 0-4 mm/s) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

### `mlcx2_speed_4_8` - MLCX2 Park Speed 4-8 mm/s

- Group: Motion bins
- Symbol/short name: MLCX2 Park Speed 4-8 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 4-8 mm/s) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

### `mlcx2_speed_8_12` - MLCX2 Park Speed 8-12 mm/s

- Group: Motion bins
- Symbol/short name: MLCX2 Park Speed 8-12 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 8-12 mm/s) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

### `mlcx2_speed_12_16` - MLCX2 Park Speed 12-16 mm/s

- Group: Motion bins
- Symbol/short name: MLCX2 Park Speed 12-16 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 12-16 mm/s) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

### `mlcx2_speed_16_20` - MLCX2 Park Speed 16-20 mm/s

- Group: Motion bins
- Symbol/short name: MLCX2 Park Speed 16-20 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 16-20 mm/s) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

### `mlcx2_acc_0_40` - MLCX2 Park Acceleration 0-40 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX2 Park Acceleration 0-40 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 0-40 mm/s^2) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

### `mlcx2_acc_40_80` - MLCX2 Park Acceleration 40-80 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX2 Park Acceleration 40-80 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 40-80 mm/s^2) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

### `mlcx2_acc_80_120` - MLCX2 Park Acceleration 80-120 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX2 Park Acceleration 80-120 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 80-120 mm/s^2) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

### `mlcx2_acc_120_160` - MLCX2 Park Acceleration 120-160 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX2 Park Acceleration 120-160 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 120-160 mm/s^2) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

### `mlcx2_acc_160_200` - MLCX2 Park Acceleration 160-200 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX2 Park Acceleration 160-200 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 160-200 mm/s^2) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

### `mlcx2_speed_average` - MLCX2 Mean Leaf Speed (mm/s)

- Group: Motion bins
- Symbol/short name: MLCX2 Mean Leaf Speed (mm/s)
- Mathematical definition: mean_leaf(mean_interval(speed)), restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: mm/s
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

### `mlcx2_acc_average` - MLCX2 Mean Leaf Acceleration (mm/s^2)

- Group: Motion bins
- Symbol/short name: MLCX2 Mean Leaf Acceleration (mm/s^2)
- Mathematical definition: mean_leaf(mean_interval(acceleration)), restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: mm/s^2
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

### `mlcx2_speed_std` - MLCX2 Mean Leaf Speed SD (mm/s)

- Group: Motion bins
- Symbol/short name: MLCX2 Mean Leaf Speed SD (mm/s)
- Mathematical definition: mean_leaf(std_interval(speed)), restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: mm/s
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

### `mlcx2_acc_std` - MLCX2 Mean Leaf Acceleration SD (mm/s^2)

- Group: Motion bins
- Symbol/short name: MLCX2 Mean Leaf Acceleration SD (mm/s^2)
- Mathematical definition: mean_leaf(std_interval(acceleration)), restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: mm/s^2
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

### `sport` - SPORT Modulation Index (Li and Xing 2013)

- Group: SPORT
- Symbol/short name: SPORT
- Mathematical definition: SPORT = weighted aggregate of station-wise MI(s) over the plan
- Physical meaning: Station-wise SPORT modulation index MI(s) from Li and Xing, reported here as the framework's beam/plan aggregate summary.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: None

## TOMO

### `mf` - MF

- Group: Delivery
- Symbol/short name: MF
- Mathematical definition: MF = mean(non-zero LOT) / max(LOT)
- Physical meaning: Ratio describing how strongly the sinogram is modulated overall.
- Unit: dimensionless
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `nproj_rot` - N proj,rot

- Group: Delivery
- Symbol/short name: N proj,rot
- Mathematical definition: N proj,rot = configured projections per rotation
- Physical meaning: Number of projections delivered in one full gantry rotation.
- Unit: count
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `nproj` - N proj

- Group: Delivery
- Symbol/short name: N proj
- Mathematical definition: N proj = number of sinogram projections
- Physical meaning: Total number of projections in the plan.
- Unit: count
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `nrot` - N rot

- Group: Delivery
- Symbol/short name: N rot
- Mathematical definition: N rot = N proj / N proj,rot
- Physical meaning: Total number of gantry rotations in the plan.
- Unit: count
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `projection_time_s` - PT

- Group: Delivery
- Symbol/short name: PT
- Mathematical definition: PT = projection time
- Physical meaning: Duration of each projection.
- Unit: s
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `gantry_period_s` - GP

- Group: Delivery
- Symbol/short name: GP
- Mathematical definition: GP = PT * N proj,rot
- Physical meaning: Time required for one full gantry rotation.
- Unit: s
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `treatment_time_s` - TT

- Group: Delivery
- Symbol/short name: TT
- Mathematical definition: TT = PT * N proj
- Physical meaning: Total beam-on treatment time.
- Unit: s
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `field_width_mm` - FW

- Group: Delivery
- Symbol/short name: FW
- Mathematical definition: FW = nominal tomotherapy field width
- Physical meaning: Nominal field width used for the plan.
- Unit: mm
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `pitch` - Pitch

- Group: Delivery
- Symbol/short name: Pitch
- Mathematical definition: Pitch = couch advance per rotation / field width
- Physical meaning: Ratio between couch travel per rotation and field width.
- Unit: dimensionless
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `couch_translation_mm` - CT

- Group: Delivery
- Symbol/short name: CT
- Mathematical definition: CT = total couch travel
- Physical meaning: Total couch translation during treatment.
- Unit: mm
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `couch_speed_mm_s` - CS

- Group: Delivery
- Symbol/short name: CS
- Mathematical definition: CS = CT / TT
- Physical meaning: Average couch translation speed.
- Unit: s
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `target_length_mm` - TL

- Group: Delivery
- Symbol/short name: TL
- Mathematical definition: TL = couch translation - field width
- Physical meaning: Estimated target length covered by the plan.
- Unit: mm
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `ttdf_s_cgy` - TTDF

- Group: Delivery
- Symbol/short name: TTDF
- Mathematical definition: TTDF = TT / dose per fraction in cGy
- Physical meaning: Treatment time normalized by dose per fraction.
- Unit: s/cGy
- Inputs required: Sinogram metadata: projection time, projections per rotation, field width, pitch, couch travel, dose
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `mlot` - mLOT

- Group: Leaf open time
- Symbol/short name: mLOT
- Mathematical definition: mLOT = mean(LOT)
- Physical meaning: Mean leaf open time across all open leaves.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `sdlot` - sdLOT

- Group: Leaf open time
- Symbol/short name: sdLOT
- Mathematical definition: sdLOT = std(LOT)
- Physical meaning: Standard deviation of leaf open time.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `mdlot` - mdLOT

- Group: Leaf open time
- Symbol/short name: mdLOT
- Mathematical definition: mdLOT = median(LOT)
- Physical meaning: Median leaf open time.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `molot` - moLOT

- Group: Leaf open time
- Symbol/short name: moLOT
- Mathematical definition: moLOT = mode(LOT)
- Physical meaning: Most frequent leaf open time.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `maxlot` - maxLOT

- Group: Leaf open time
- Symbol/short name: maxLOT
- Mathematical definition: maxLOT = max(LOT)
- Physical meaning: Maximum leaf open time.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `minlot` - minLOT

- Group: Leaf open time
- Symbol/short name: minLOT
- Mathematical definition: minLOT = min(non-zero LOT)
- Physical meaning: Minimum non-zero leaf open time.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `klot` - kLOT

- Group: Leaf open time
- Symbol/short name: kLOT
- Mathematical definition: kLOT = kurtosis(LOT)
- Physical meaning: Kurtosis of the leaf open time distribution.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `slot` - sLOT

- Group: Leaf open time
- Symbol/short name: sLOT
- Mathematical definition: sLOT = skewness(LOT)
- Physical meaning: Skewness of the leaf open time distribution.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `clns_10ms` - CLNS10

- Group: Leaf open time
- Symbol/short name: CLNS10
- Mathematical definition: CLNS10 = count(LOT < 10 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times shorter than 10 ms.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `clns_20ms` - CLNS20

- Group: Leaf open time
- Symbol/short name: CLNS20
- Mathematical definition: CLNS20 = count(LOT < 20 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times shorter than 20 ms.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `clns_30ms` - CLNS30

- Group: Leaf open time
- Symbol/short name: CLNS30
- Mathematical definition: CLNS30 = count(LOT < 30 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times shorter than 30 ms.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `clns_50ms` - CLNS50

- Group: Leaf open time
- Symbol/short name: CLNS50
- Mathematical definition: CLNS50 = count(LOT < 50 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times shorter than 50 ms.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `clns_pt_10ms` - CLNSpt10

- Group: Leaf open time
- Symbol/short name: CLNSpt10
- Mathematical definition: CLNSpt_10 = count(LOT < pt_10 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times within 10 ms of the projection time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `clns_pt_20ms` - CLNSpt20

- Group: Leaf open time
- Symbol/short name: CLNSpt20
- Mathematical definition: CLNSpt_20 = count(LOT < pt_20 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times within 20 ms of the projection time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `clns_pt_30ms` - CLNSpt30

- Group: Leaf open time
- Symbol/short name: CLNSpt30
- Mathematical definition: CLNSpt_30 = count(LOT < pt_30 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times within 30 ms of the projection time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `clns_pt_50ms` - CLNSpt50

- Group: Leaf open time
- Symbol/short name: CLNSpt50
- Mathematical definition: CLNSpt_50 = count(LOT < pt_50 ms) / count(non-zero LOT)
- Physical meaning: Fraction of leaf open times within 50 ms of the projection time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `mflot` - mFLOT

- Group: Leaf open time
- Symbol/short name: mFLOT
- Mathematical definition: mFLOT = mean(FLOT)
- Physical meaning: Mean fractional leaf open time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `sdflot` - sdFLOT

- Group: Leaf open time
- Symbol/short name: sdFLOT
- Mathematical definition: sdFLOT = std(FLOT)
- Physical meaning: Standard deviation of fractional leaf open time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `mdflot` - mdFLOT

- Group: Leaf open time
- Symbol/short name: mdFLOT
- Mathematical definition: mdFLOT = median(FLOT)
- Physical meaning: Median fractional leaf open time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `moflot` - moFLOT

- Group: Leaf open time
- Symbol/short name: moFLOT
- Mathematical definition: moFLOT = mode(FLOT)
- Physical meaning: Most frequent fractional leaf open time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `maxflot` - maxFLOT

- Group: Leaf open time
- Symbol/short name: maxFLOT
- Mathematical definition: maxFLOT = max(FLOT)
- Physical meaning: Maximum fractional leaf open time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `minflot` - minFLOT

- Group: Leaf open time
- Symbol/short name: minFLOT
- Mathematical definition: minFLOT = min(non-zero FLOT)
- Physical meaning: Minimum non-zero fractional leaf open time.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `cfns_0_1` - CFNS0.1

- Group: Leaf open time
- Symbol/short name: CFNS0.1
- Mathematical definition: CFNS0.1 = count(FLOT < 0.1) / count(non-zero FLOT)
- Physical meaning: Fraction of fractional leaf open times below 0.1.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `cfns_0_25` - CFNS0.25

- Group: Leaf open time
- Symbol/short name: CFNS0.25
- Mathematical definition: CFNS0.25 = count(FLOT < 0.25) / count(non-zero FLOT)
- Physical meaning: Fraction of fractional leaf open times below 0.25.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `cfns_0_5` - CFNS0.5

- Group: Leaf open time
- Symbol/short name: CFNS0.5
- Mathematical definition: CFNS0.5 = count(FLOT < 0.5) / count(non-zero FLOT)
- Physical meaning: Fraction of fractional leaf open times below 0.5.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `cfns_0_75` - CFNS0.75

- Group: Leaf open time
- Symbol/short name: CFNS0.75
- Mathematical definition: CFNS0.75 = count(FLOT < 0.75) / count(non-zero FLOT)
- Physical meaning: Fraction of fractional leaf open times below 0.75.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `ta` - TA

- Group: Sinogram geometry
- Symbol/short name: TA
- Mathematical definition: TA = mean projection treatment width across the sinogram
- Physical meaning: Average width of the treated sinogram area per projection.
- Unit: mm
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `ncc` - nCC

- Group: Sinogram geometry
- Symbol/short name: nCC
- Mathematical definition: nCC = mean number of connected open components per projection
- Physical meaning: Average number of disconnected open components per projection.
- Unit: count
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `lengthcc` - lengthCC

- Group: Sinogram geometry
- Symbol/short name: lengthCC
- Mathematical definition: lengthCC = mean connected-component length in the sinogram
- Physical meaning: Average length of connected open sinogram components.
- Unit: mm
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `fdisc` - fDISC

- Group: Sinogram geometry
- Symbol/short name: fDISC
- Mathematical definition: fDISC = fraction(projections with more than one connected component)
- Physical meaning: Fraction of projections with discontinuous open regions.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `cls` - CLS

- Group: Sinogram geometry
- Symbol/short name: CLS
- Mathematical definition: CLS = mean[(N_leaves - open leaves) / N_leaves] over projections
- Physical meaning: Fraction of leaves that remain closed across the full sinogram width.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `clsin` - CLSin

- Group: Sinogram geometry
- Symbol/short name: CLSin
- Mathematical definition: CLSin = mean(closed leaves inside the treatment area)
- Physical meaning: Closed leaf score within the treatment area.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `clsinarea` - CLSinarea

- Group: Sinogram geometry
- Symbol/short name: CLSinarea
- Mathematical definition: CLSinarea = mean(closed leaves inside the treatment area / treatment area)
- Physical meaning: Closed leaf score within the treatment area, normalized by area.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `clsindisc` - CLSindisc

- Group: Sinogram geometry
- Symbol/short name: CLSindisc
- Mathematical definition: CLSindisc = CLSin restricted to discontinuous projections
- Physical meaning: Closed leaf score within discontinuous treatment projections.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `clsinareadisc` - CLSinareadisc

- Group: Sinogram geometry
- Symbol/short name: CLSinareadisc
- Mathematical definition: CLSinareadisc = area-normalized CLSin restricted to discontinuous projections
- Physical meaning: Area-normalized closed leaf score for discontinuous projections.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `centroid` - Centroid

- Group: Sinogram geometry
- Symbol/short name: Centroid
- Mathematical definition: Centroid = mean lateral centroid of open leaves over projections
- Physical meaning: Average lateral position of the open sinogram barycenter.
- Unit: mm
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `l0ns` - L0NS

- Group: Sinogram geometry
- Symbol/short name: L0NS
- Mathematical definition: L0NS = mean fraction of open leaves with 0 open nearest neighbors
- Physical meaning: Fraction of open leaves with no open nearest neighbors.
- Unit: count
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `l1ns` - L1NS

- Group: Sinogram geometry
- Symbol/short name: L1NS
- Mathematical definition: L1NS = mean fraction of open leaves with 1 open nearest neighbor
- Physical meaning: Fraction of open leaves with one open nearest neighbor.
- Unit: count
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `l2ns` - L2NS

- Group: Sinogram geometry
- Symbol/short name: L2NS
- Mathematical definition: L2NS = mean fraction of open leaves with 2 open nearest neighbors
- Physical meaning: Fraction of open leaves with two open nearest neighbors.
- Unit: count
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `lotv` - LOTV

- Group: Leaf open time
- Symbol/short name: LOTV
- Mathematical definition: LOTV = mean over leaves of [ sum(max(LOT) - abs(delta LOT)) / ((N_proj - 1) * max(LOT)) ]
- Physical meaning: Variability of leaf open time across consecutive projections.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `elotv_1` - ELOTV-1

- Group: Leaf open time
- Symbol/short name: ELOTV-1
- Mathematical definition: ELOTV-1 = mean normalized abs(LOT_i - LOT_{i+1}) over leaves
- Physical meaning: Extended leaf open time variability using a one-projection offset.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `elotv_5` - ELOTV-5

- Group: Leaf open time
- Symbol/short name: ELOTV-5
- Mathematical definition: ELOTV-5 = mean normalized abs(LOT_i - LOT_{i+5}) over leaves
- Physical meaning: Extended leaf open time variability using a five-projection offset.
- Unit: ms
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `pstv` - PSTV

- Group: Sinogram modulation
- Symbol/short name: PSTV
- Mathematical definition: PSTV = EPSTV with delta projection = 1 and delta leaf = 1
- Physical meaning: Plan sinogram time variability across neighboring projections and leaves.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `epstv_1_1` - EPSTV-1,1

- Group: Sinogram modulation
- Symbol/short name: EPSTV-1,1
- Mathematical definition: EPSTV-1,1 = mean of abs(delta projection) + abs(delta leaf) sinogram differences for offsets (1,1)
- Physical meaning: Extended plan sinogram time variability using one-step projection and leaf offsets.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `epstv_1_0` - EPSTV-1,0

- Group: Sinogram modulation
- Symbol/short name: EPSTV-1,0
- Mathematical definition: EPSTV-1,0 = mean sinogram difference for projection offset 1 and leaf offset 0
- Physical meaning: Extended plan sinogram time variability using only a projection offset.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `epstv_0_1` - EPSTV-0,1

- Group: Sinogram modulation
- Symbol/short name: EPSTV-0,1
- Mathematical definition: EPSTV-0,1 = mean sinogram difference for projection offset 0 and leaf offset 1
- Physical meaning: Extended plan sinogram time variability using only a leaf offset.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `mi` - MI

- Group: Sinogram modulation
- Symbol/short name: MI
- Mathematical definition: MI = trapezoidal integral over threshold factor f of the mean fraction of directional sinogram differences exceeding f * sd(FLOT)
- Physical meaning: Overall modulation index of the tomotherapy sinogram.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `noc` - nOC

- Group: Sinogram modulation
- Symbol/short name: nOC
- Mathematical definition: nOC = mean per leaf of [2 * merged open intervals / N_proj]
- Physical meaning: Average number of leaf openings and closures per leaf.
- Unit: count
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `msa` - mSA

- Group: Sinogram modulation
- Symbol/short name: mSA
- Mathematical definition: mSA = sum(position * mean leaf opening) / sum(mean leaf opening)
- Physical meaning: Mean left-right asymmetry of the sinogram.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `msi` - mSI

- Group: Sinogram modulation
- Symbol/short name: mSI
- Mathematical definition: mSI = mean leaf-open intensity over leaves
- Physical meaning: Mean sinogram intensity.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `mdsi` - mdSI

- Group: Sinogram modulation
- Symbol/short name: mdSI
- Mathematical definition: mdSI = median leaf-open intensity over leaves
- Physical meaning: Median sinogram intensity.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

### `sdsi` - sdSI

- Group: Sinogram modulation
- Symbol/short name: sdSI
- Mathematical definition: sdSI = std leaf-open intensity over leaves
- Physical meaning: Standard deviation of sinogram intensity.
- Unit: dimensionless
- Inputs required: Sinogram matrix, non-zero leaf open times, and per-leaf open/closed topology
- Status: implemented
- Notes: Mathematical definition summarizes the current sinogram-based implementation.

## CyberKnife MLC

### `mcs` - MCS (CyberKnife MLC)

- Group: MLC-based subset
- Symbol/short name: MCS
- Mathematical definition: MCS = sum_segments[(MU_segment / MU_plan) * AAV_segment * LSV_segment]
- Physical meaning: Overall modulation complexity of the delivered CyberKnife MLC apertures.
- Unit: dimensionless
- Inputs required: CyberKnife MLC segment apertures, segment MU, and interval grouping from beam-path XML
- Status: implemented
- Notes: Implements the paper-limited six-metric MLC subset only.

### `em` - EM

- Group: MLC-based subset
- Symbol/short name: EM
- Mathematical definition: EM = sum_segments[(MU_segment / MU_plan) * aperture edge metric]
- Physical meaning: Relative amount of aperture edge compared with open field area.
- Unit: dimensionless
- Inputs required: CyberKnife MLC segment apertures, segment MU, and interval grouping from beam-path XML
- Status: implemented
- Notes: Implements the paper-limited six-metric MLC subset only.

### `pi` - PI

- Group: MLC-based subset
- Symbol/short name: PI
- Mathematical definition: PI = sum_segments[(MU_segment / MU_plan) * aperture irregularity]
- Physical meaning: Irregularity of the CyberKnife MLC aperture shape.
- Unit: dimensionless
- Inputs required: CyberKnife MLC segment apertures, segment MU, and interval grouping from beam-path XML
- Status: implemented
- Notes: Implements the paper-limited six-metric MLC subset only.

### `pm` - PM

- Group: MLC-based subset
- Symbol/short name: PM
- Mathematical definition: PM = sum_intervals[(MU_interval / MU_plan) * (1 - weighted beam area / (MU_interval * union area_interval))]
- Physical meaning: Variation in aperture opening between successive segments.
- Unit: dimensionless
- Inputs required: CyberKnife MLC segment apertures, segment MU, and interval grouping from beam-path XML
- Status: implemented
- Notes: Implements the paper-limited six-metric MLC subset only.

### `lg` - LG (Mean Leaf Gap)

- Group: MLC-based subset
- Symbol/short name: LG
- Mathematical definition: LG = sum_segments[(MU_segment / MU_plan) * mean opposing leaf gap_segment]
- Physical meaning: Average gap between opposing CyberKnife MLC leaves.
- Unit: mm
- Inputs required: CyberKnife MLC segment apertures, segment MU, and interval grouping from beam-path XML
- Status: implemented
- Notes: Implements the paper-limited six-metric MLC subset only.

### `sas10` - SAS10 (CyberKnife)

- Group: MLC-based subset
- Symbol/short name: SAS10
- Mathematical definition: SAS10 = count(open leaf gaps < 10 mm) / count(all open leaf gaps)
- Physical meaning: Fraction of CyberKnife MLC gaps smaller than 10 mm.
- Unit: dimensionless
- Inputs required: CyberKnife MLC segment apertures, segment MU, and interval grouping from beam-path XML
- Status: implemented
- Notes: Implements the paper-limited six-metric MLC subset only.

## Aurora SVMAT Lab

### `longitudinal_travel_mm` - longitudinal_travel_mm

- Group: V2 paper-style physics
- Symbol/short name: longitudinal_travel_mm
- Mathematical definition: sum_i abs(delta z_i)
- Physical meaning: Total absolute longitudinal travel reconstructed from adjacent control-point isocenter z positions.
- Unit: mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `total_rotation_deg` - total_rotation_deg

- Group: V2 paper-style physics
- Symbol/short name: total_rotation_deg
- Mathematical definition: sum_i abs(delta theta_i)
- Physical meaning: Total absolute gantry rotation reconstructed from the observed angle sequence rather than declared direction tags.
- Unit: deg
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `rotations` - rotations

- Group: V2 paper-style physics
- Symbol/short name: rotations
- Mathematical definition: total rotation / 360
- Physical meaning: Total gantry rotation expressed in full 360-degree turns.
- Unit: turns
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `travel_per_rotation_mm` - travel_per_rotation_mm

- Group: V2 paper-style physics
- Symbol/short name: travel_per_rotation_mm
- Mathematical definition: longitudinal travel / rotations
- Physical meaning: Average longitudinal travel per gantry rotation, derived from total travel and total rotation.
- Unit: mm/rotation
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_pitch_mean` - projection_pitch_mean

- Group: V2 paper-style physics
- Symbol/short name: projection_pitch_mean
- Mathematical definition: mean_i(abs(delta z_i) / abs(delta theta_i))
- Physical meaning: Mean projection pitch, defined as the mean of |delta z| / |delta theta| over valid adjacent control-point intervals.
- Unit: mm/deg
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_pitch_cv` - projection_pitch_cv

- Group: V2 paper-style physics
- Symbol/short name: projection_pitch_cv
- Mathematical definition: std(projection pitch_i) / mean(projection pitch_i)
- Physical meaning: Coefficient of variation of projection pitch. Lower values mean steadier theta-z coupling.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_mu_density_mean_proxy` - projection_mu_density_mean_proxy

- Group: V2 paper-style physics
- Symbol/short name: projection_mu_density_mean_proxy
- Mathematical definition: mean_i(abs(delta w_i) / abs(delta z_i))
- Physical meaning: Mean projection MU-density proxy, using cumulative meterset-weight change per millimeter of longitudinal travel.
- Unit: weight/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_mu_density_cv_proxy` - projection_mu_density_cv_proxy

- Group: V2 paper-style physics
- Symbol/short name: projection_mu_density_cv_proxy
- Mathematical definition: std(abs(delta w_i) / abs(delta z_i)) / mean(abs(delta w_i) / abs(delta z_i))
- Physical meaning: Coefficient of variation of the projection MU-density proxy across adjacent control-point intervals.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_aperture_change_mean` - projection_aperture_change_mean

- Group: V2 paper-style physics
- Symbol/short name: projection_aperture_change_mean
- Mathematical definition: mean_i(abs(delta A_i) / abs(delta z_i))
- Physical meaning: Mean projection aperture-change rate, defined as absolute aperture-width change per millimeter of longitudinal travel.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_aperture_change_cv` - projection_aperture_change_cv

- Group: V2 paper-style physics
- Symbol/short name: projection_aperture_change_cv
- Mathematical definition: std(abs(delta A_i) / abs(delta z_i)) / mean(abs(delta A_i) / abs(delta z_i))
- Physical meaning: Coefficient of variation of the projection aperture-change rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_leaf_travel_mean` - projection_leaf_travel_mean

- Group: V2 paper-style physics
- Symbol/short name: projection_leaf_travel_mean
- Mathematical definition: mean_i(delta L_i / abs(delta z_i)), with delta L_i summed across both MLC layers
- Physical meaning: Mean projection leaf-travel rate, defined as summed leaf travel per millimeter of longitudinal travel.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_leaf_travel_cv` - projection_leaf_travel_cv

- Group: V2 paper-style physics
- Symbol/short name: projection_leaf_travel_cv
- Mathematical definition: std(delta L_i / abs(delta z_i)) / mean(delta L_i / abs(delta z_i))
- Physical meaning: Coefficient of variation of the projection leaf-travel rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_leaf_travel_mean_mlcx1` - projection_leaf_travel_mean_mlcx1

- Group: V2 paper-style physics
- Symbol/short name: projection_leaf_travel_mean_mlcx1
- Mathematical definition: mean_i(delta L_i_MLCX1 / abs(delta z_i))
- Physical meaning: Mean projection leaf-travel rate for the MLCX1 layer only, normalized by longitudinal travel.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_leaf_travel_cv_mlcx1` - projection_leaf_travel_cv_mlcx1

- Group: V2 paper-style physics
- Symbol/short name: projection_leaf_travel_cv_mlcx1
- Mathematical definition: std(delta L_i_MLCX1 / abs(delta z_i)) / mean(delta L_i_MLCX1 / abs(delta z_i))
- Physical meaning: Coefficient of variation of the MLCX1 projection leaf-travel rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_leaf_travel_mean_mlcx2` - projection_leaf_travel_mean_mlcx2

- Group: V2 paper-style physics
- Symbol/short name: projection_leaf_travel_mean_mlcx2
- Mathematical definition: mean_i(delta L_i_MLCX2 / abs(delta z_i))
- Physical meaning: Mean projection leaf-travel rate for the MLCX2 layer only, normalized by longitudinal travel.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_leaf_travel_cv_mlcx2` - projection_leaf_travel_cv_mlcx2

- Group: V2 paper-style physics
- Symbol/short name: projection_leaf_travel_cv_mlcx2
- Mathematical definition: std(delta L_i_MLCX2 / abs(delta z_i)) / mean(delta L_i_MLCX2 / abs(delta z_i))
- Physical meaning: Coefficient of variation of the MLCX2 projection leaf-travel rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `theta_z_coupling_cv` - theta_z_coupling_cv

- Group: V2 paper-style physics
- Symbol/short name: theta_z_coupling_cv
- Mathematical definition: projection_pitch_cv
- Physical meaning: Theta-z coupling variability, reported here as the same projection-pitch coefficient of variation.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `mu_z_coupling_cv_proxy` - mu_z_coupling_cv_proxy

- Group: V2 paper-style physics
- Symbol/short name: mu_z_coupling_cv_proxy
- Mathematical definition: projection_mu_density_cv_proxy
- Physical meaning: MU-z coupling variability proxy, reported as the coefficient of variation of meterset-weight density over longitudinal travel.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `mlc_z_coupling_cv` - mlc_z_coupling_cv

- Group: V2 paper-style physics
- Symbol/short name: mlc_z_coupling_cv
- Mathematical definition: projection_leaf_travel_cv
- Physical meaning: MLC-z coupling variability, reported here as the coefficient of variation of the projection leaf-travel rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `mlcx1_z_coupling_cv` - mlcx1_z_coupling_cv

- Group: V2 paper-style physics
- Symbol/short name: mlcx1_z_coupling_cv
- Mathematical definition: projection_leaf_travel_cv_mlcx1
- Physical meaning: MLCX1-z coupling variability, reported as the coefficient of variation of the MLCX1 projection leaf-travel rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `mlcx2_z_coupling_cv` - mlcx2_z_coupling_cv

- Group: V2 paper-style physics
- Symbol/short name: mlcx2_z_coupling_cv
- Mathematical definition: projection_leaf_travel_cv_mlcx2
- Physical meaning: MLCX2-z coupling variability, reported as the coefficient of variation of the MLCX2 projection leaf-travel rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `reversal_symmetry_index` - reversal_symmetry_index

- Group: V3 bidirectional symmetry
- Symbol/short name: reversal_symmetry_index
- Mathematical definition: mean over selected burden families of [1 - abs(forward_mean - backward_mean) / (abs(forward_mean) + abs(backward_mean))]
- Physical meaning: Symmetry score comparing forward and backward beam groups across matched modulation summaries. Higher values mean more balanced bidirectional modulation.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `forward_backward_metric_difference` - forward_backward_metric_difference

- Group: V3 bidirectional symmetry
- Symbol/short name: forward_backward_metric_difference
- Mathematical definition: abs(mean_forward(coupled_modulation_index) - mean_backward(coupled_modulation_index))
- Physical meaning: Absolute difference in average modulation burden between forward-moving and backward-moving beam groups.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `beam_pair_balance_index` - beam_pair_balance_index

- Group: V3 bidirectional symmetry
- Symbol/short name: beam_pair_balance_index
- Mathematical definition: 1 - abs(sum_forward(coupled_modulation_index) - sum_backward(coupled_modulation_index)) / (sum_forward + sum_backward)
- Physical meaning: Balance score comparing the total modulation burden assigned to forward and backward beam groups.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `small_opening_fraction` - small_opening_fraction

- Group: V3 small-opening burden
- Symbol/short name: small_opening_fraction
- Mathematical definition: weighted count(gap < 10 mm and gap > 0) / weighted count(gap > 0)
- Physical meaning: Weighted fraction of effective openings smaller than 10 mm.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `near_closed_fraction` - near_closed_fraction

- Group: V3 small-opening burden
- Symbol/short name: near_closed_fraction
- Mathematical definition: weighted count(gap < 2 mm and gap > 0) / weighted count(gap > 0)
- Physical meaning: Weighted fraction of effective openings smaller than 2 mm.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `effective_small_gap_burden` - effective_small_gap_burden

- Group: V3 small-opening burden
- Symbol/short name: effective_small_gap_burden
- Mathematical definition: weighted mean of max(0, 1 - gap / 10 mm) over open effective gaps
- Physical meaning: Weighted severity score for narrow effective openings, with smaller openings contributing more burden.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_pitch_p95` - projection_pitch_p95

- Group: V3 local interval peaks
- Symbol/short name: projection_pitch_p95
- Mathematical definition: nearest-rank 95th percentile of projection_pitch_i
- Physical meaning: 95th percentile of projection pitch, using the nearest-rank interval summary.
- Unit: mm/deg
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_pitch_max` - projection_pitch_max

- Group: V3 local interval peaks
- Symbol/short name: projection_pitch_max
- Mathematical definition: max(projection_pitch_i)
- Physical meaning: Maximum projection pitch observed across adjacent control-point intervals.
- Unit: mm/deg
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_pitch_top3_mean` - projection_pitch_top3_mean

- Group: V3 local interval peaks
- Symbol/short name: projection_pitch_top3_mean
- Mathematical definition: mean of the three largest projection_pitch_i values
- Physical meaning: Mean of the three largest projection-pitch intervals, or all intervals if fewer than three exist.
- Unit: mm/deg
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_mu_density_p95_proxy` - projection_mu_density_p95_proxy

- Group: V3 local interval peaks
- Symbol/short name: projection_mu_density_p95_proxy
- Mathematical definition: nearest-rank 95th percentile of projection_mu_density_proxy_i
- Physical meaning: 95th percentile of the projection MU-density proxy, using cumulative meterset-weight change per millimeter.
- Unit: weight/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_mu_density_max_proxy` - projection_mu_density_max_proxy

- Group: V3 local interval peaks
- Symbol/short name: projection_mu_density_max_proxy
- Mathematical definition: max(projection_mu_density_proxy_i)
- Physical meaning: Maximum projection MU-density proxy observed across adjacent control-point intervals.
- Unit: weight/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_mu_density_top3_mean_proxy` - projection_mu_density_top3_mean_proxy

- Group: V3 local interval peaks
- Symbol/short name: projection_mu_density_top3_mean_proxy
- Mathematical definition: mean of the three largest projection_mu_density_proxy_i values
- Physical meaning: Mean of the three largest projection MU-density proxy values.
- Unit: weight/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_aperture_change_p95` - projection_aperture_change_p95

- Group: V3 local interval peaks
- Symbol/short name: projection_aperture_change_p95
- Mathematical definition: nearest-rank 95th percentile of projection_aperture_change_i
- Physical meaning: 95th percentile of the projection aperture-change rate.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_aperture_change_max` - projection_aperture_change_max

- Group: V3 local interval peaks
- Symbol/short name: projection_aperture_change_max
- Mathematical definition: max(projection_aperture_change_i)
- Physical meaning: Maximum projection aperture-change rate observed across adjacent control-point intervals.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_aperture_change_top3_mean` - projection_aperture_change_top3_mean

- Group: V3 local interval peaks
- Symbol/short name: projection_aperture_change_top3_mean
- Mathematical definition: mean of the three largest projection_aperture_change_i values
- Physical meaning: Mean of the three largest projection aperture-change rates.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_leaf_travel_p95` - projection_leaf_travel_p95

- Group: V3 local interval peaks
- Symbol/short name: projection_leaf_travel_p95
- Mathematical definition: nearest-rank 95th percentile of projection_leaf_travel_i
- Physical meaning: 95th percentile of the projection leaf-travel rate across both layers.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_leaf_travel_max` - projection_leaf_travel_max

- Group: V3 local interval peaks
- Symbol/short name: projection_leaf_travel_max
- Mathematical definition: max(projection_leaf_travel_i)
- Physical meaning: Maximum projection leaf-travel rate across both layers.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `projection_leaf_travel_top3_mean` - projection_leaf_travel_top3_mean

- Group: V3 local interval peaks
- Symbol/short name: projection_leaf_travel_top3_mean
- Mathematical definition: mean of the three largest projection_leaf_travel_i values
- Physical meaning: Mean of the three largest projection leaf-travel rates across both layers.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `head_mu_density_mean_proxy` - head_mu_density_mean_proxy

- Group: V3 axial regions
- Symbol/short name: head_mu_density_mean_proxy
- Mathematical definition: mean(projection_mu_density_proxy_i) over head-third intervals
- Physical meaning: Mean projection MU-density proxy inside the head longitudinal third of the covered z-range.
- Unit: weight/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `head_mu_density_cv_proxy` - head_mu_density_cv_proxy

- Group: V3 axial regions
- Symbol/short name: head_mu_density_cv_proxy
- Mathematical definition: CV(projection_mu_density_proxy_i) over head-third intervals
- Physical meaning: Coefficient of variation of the projection MU-density proxy inside the head longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `head_aperture_change_mean` - head_aperture_change_mean

- Group: V3 axial regions
- Symbol/short name: head_aperture_change_mean
- Mathematical definition: mean(projection_aperture_change_i) over head-third intervals
- Physical meaning: Mean projection aperture-change rate inside the head longitudinal third of the covered z-range.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `head_aperture_change_cv` - head_aperture_change_cv

- Group: V3 axial regions
- Symbol/short name: head_aperture_change_cv
- Mathematical definition: CV(projection_aperture_change_i) over head-third intervals
- Physical meaning: Coefficient of variation of the projection aperture-change rate inside the head longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `head_leaf_travel_mean` - head_leaf_travel_mean

- Group: V3 axial regions
- Symbol/short name: head_leaf_travel_mean
- Mathematical definition: mean(projection_leaf_travel_i) over head-third intervals
- Physical meaning: Mean projection leaf-travel rate inside the head longitudinal third of the covered z-range.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `head_leaf_travel_cv` - head_leaf_travel_cv

- Group: V3 axial regions
- Symbol/short name: head_leaf_travel_cv
- Mathematical definition: CV(projection_leaf_travel_i) over head-third intervals
- Physical meaning: Coefficient of variation of the projection leaf-travel rate inside the head longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `mid_mu_density_mean_proxy` - mid_mu_density_mean_proxy

- Group: V3 axial regions
- Symbol/short name: mid_mu_density_mean_proxy
- Mathematical definition: mean(projection_mu_density_proxy_i) over mid-third intervals
- Physical meaning: Mean projection MU-density proxy inside the mid longitudinal third of the covered z-range.
- Unit: weight/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `mid_mu_density_cv_proxy` - mid_mu_density_cv_proxy

- Group: V3 axial regions
- Symbol/short name: mid_mu_density_cv_proxy
- Mathematical definition: CV(projection_mu_density_proxy_i) over mid-third intervals
- Physical meaning: Coefficient of variation of the projection MU-density proxy inside the mid longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `mid_aperture_change_mean` - mid_aperture_change_mean

- Group: V3 axial regions
- Symbol/short name: mid_aperture_change_mean
- Mathematical definition: mean(projection_aperture_change_i) over mid-third intervals
- Physical meaning: Mean projection aperture-change rate inside the mid longitudinal third of the covered z-range.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `mid_aperture_change_cv` - mid_aperture_change_cv

- Group: V3 axial regions
- Symbol/short name: mid_aperture_change_cv
- Mathematical definition: CV(projection_aperture_change_i) over mid-third intervals
- Physical meaning: Coefficient of variation of the projection aperture-change rate inside the mid longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `mid_leaf_travel_mean` - mid_leaf_travel_mean

- Group: V3 axial regions
- Symbol/short name: mid_leaf_travel_mean
- Mathematical definition: mean(projection_leaf_travel_i) over mid-third intervals
- Physical meaning: Mean projection leaf-travel rate inside the mid longitudinal third of the covered z-range.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `mid_leaf_travel_cv` - mid_leaf_travel_cv

- Group: V3 axial regions
- Symbol/short name: mid_leaf_travel_cv
- Mathematical definition: CV(projection_leaf_travel_i) over mid-third intervals
- Physical meaning: Coefficient of variation of the projection leaf-travel rate inside the mid longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `tail_mu_density_mean_proxy` - tail_mu_density_mean_proxy

- Group: V3 axial regions
- Symbol/short name: tail_mu_density_mean_proxy
- Mathematical definition: mean(projection_mu_density_proxy_i) over tail-third intervals
- Physical meaning: Mean projection MU-density proxy inside the tail longitudinal third of the covered z-range.
- Unit: weight/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `tail_mu_density_cv_proxy` - tail_mu_density_cv_proxy

- Group: V3 axial regions
- Symbol/short name: tail_mu_density_cv_proxy
- Mathematical definition: CV(projection_mu_density_proxy_i) over tail-third intervals
- Physical meaning: Coefficient of variation of the projection MU-density proxy inside the tail longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `tail_aperture_change_mean` - tail_aperture_change_mean

- Group: V3 axial regions
- Symbol/short name: tail_aperture_change_mean
- Mathematical definition: mean(projection_aperture_change_i) over tail-third intervals
- Physical meaning: Mean projection aperture-change rate inside the tail longitudinal third of the covered z-range.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `tail_aperture_change_cv` - tail_aperture_change_cv

- Group: V3 axial regions
- Symbol/short name: tail_aperture_change_cv
- Mathematical definition: CV(projection_aperture_change_i) over tail-third intervals
- Physical meaning: Coefficient of variation of the projection aperture-change rate inside the tail longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `tail_leaf_travel_mean` - tail_leaf_travel_mean

- Group: V3 axial regions
- Symbol/short name: tail_leaf_travel_mean
- Mathematical definition: mean(projection_leaf_travel_i) over tail-third intervals
- Physical meaning: Mean projection leaf-travel rate inside the tail longitudinal third of the covered z-range.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `tail_leaf_travel_cv` - tail_leaf_travel_cv

- Group: V3 axial regions
- Symbol/short name: tail_leaf_travel_cv
- Mathematical definition: CV(projection_leaf_travel_i) over tail-third intervals
- Physical meaning: Coefficient of variation of the projection leaf-travel rate inside the tail longitudinal third.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `layer_imbalance_index` - layer_imbalance_index

- Group: V3 dual-layer coordination
- Symbol/short name: layer_imbalance_index
- Mathematical definition: abs(mean(leaf_travel_i_MLCX1) - mean(leaf_travel_i_MLCX2)) / (abs(mean_MLCX1) + abs(mean_MLCX2))
- Physical meaning: Normalized difference between the mean MLCX1 and MLCX2 leaf-travel rates.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `layer_correlation_index` - layer_correlation_index

- Group: V3 dual-layer coordination
- Symbol/short name: layer_correlation_index
- Mathematical definition: correlation(projection_leaf_travel_i_MLCX1, projection_leaf_travel_i_MLCX2)
- Physical meaning: Correlation between the interval-by-interval MLCX1 and MLCX2 leaf-travel rates.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `x1_x2_aperture_disparity` - x1_x2_aperture_disparity

- Group: V3 dual-layer coordination
- Symbol/short name: x1_x2_aperture_disparity
- Mathematical definition: mean over control points of abs(sum|MLCX1| - sum|MLCX2|) / (sum|MLCX1| + sum|MLCX2|)
- Physical meaning: Surrogate side-opening disparity, computed from the relative difference in MLCX1 and MLCX2 position magnitudes.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `x1_x2_leaf_travel_ratio` - x1_x2_leaf_travel_ratio

- Group: V3 dual-layer coordination
- Symbol/short name: x1_x2_leaf_travel_ratio
- Mathematical definition: mean(projection_leaf_travel_i_MLCX1) / mean(projection_leaf_travel_i_MLCX2)
- Physical meaning: Ratio of mean MLCX1 leaf-travel rate to mean MLCX2 leaf-travel rate.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Standalone Aurora SVMAT Lab metric.

### `axial_travel_mm` - axial_travel_mm

- Group: Legacy engineering
- Symbol/short name: axial_travel_mm
- Mathematical definition: sum_i abs(delta z_i)
- Physical meaning: Legacy engineering metric for total absolute axial travel reconstructed from adjacent control-point isocenter z positions.
- Unit: mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

### `gantry_rotation_deg` - gantry_rotation_deg

- Group: Legacy engineering
- Symbol/short name: gantry_rotation_deg
- Mathematical definition: sum_i abs(delta theta_i)
- Physical meaning: Legacy engineering metric for total absolute gantry rotation reconstructed from the observed angle sequence.
- Unit: deg
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

### `mm_per_deg` - mm_per_deg

- Group: Legacy engineering
- Symbol/short name: mm_per_deg
- Mathematical definition: axial travel / total rotation
- Physical meaning: Legacy engineering metric for total axial travel divided by total gantry rotation.
- Unit: mm/deg
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

### `mm_per_rotation` - mm_per_rotation

- Group: Legacy engineering
- Symbol/short name: mm_per_rotation
- Mathematical definition: axial travel / (total rotation / 360)
- Physical meaning: Legacy engineering metric for total axial travel per full 360-degree gantry rotation.
- Unit: mm/rotation
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

### `pitch_consistency` - pitch_consistency

- Group: Legacy engineering
- Symbol/short name: pitch_consistency
- Mathematical definition: std(abs(delta z_i) / abs(delta theta_i)) / mean(abs(delta z_i) / abs(delta theta_i))
- Physical meaning: Legacy engineering pitch variability metric, equivalent to the coefficient of variation of interval pitch.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

### `mu_per_mm` - mu_per_mm

- Group: Legacy engineering
- Symbol/short name: mu_per_mm
- Mathematical definition: MU_total / axial travel
- Physical meaning: Legacy engineering MU density per millimeter of axial travel. Uses explicit total MU when available, otherwise cumulative meterset-weight span as a transparent proxy.
- Unit: MU/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

### `aperture_change_per_mm` - aperture_change_per_mm

- Group: Legacy engineering
- Symbol/short name: aperture_change_per_mm
- Mathematical definition: sum_i abs(delta A_i) / sum_i abs(delta z_i)
- Physical meaning: Legacy engineering metric for total absolute aperture-width change normalized by total axial travel.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

### `leaf_travel_per_mm` - leaf_travel_per_mm

- Group: Legacy engineering
- Symbol/short name: leaf_travel_per_mm
- Mathematical definition: sum_i delta L_i / sum_i abs(delta z_i)
- Physical meaning: Legacy engineering metric for total absolute leaf travel normalized by total axial travel.
- Unit: mm/mm
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.

### `coupled_modulation_index` - coupled_modulation_index

- Group: Legacy engineering
- Symbol/short name: coupled_modulation_index
- Mathematical definition: mean of normalized aperture-change/mm, leaf-travel/mm, MU-density variability, and pitch variability
- Physical meaning: Legacy engineering aggregate of normalized aperture change, leaf travel, MU-density variability, and pitch variability.
- Unit: dimensionless
- Inputs required: Aurora RTPLAN control points: gantry angle, isocenter z, cumulative meterset weight, MLCX1 and MLCX2
- Status: implemented
- Notes: Retained for comparison against the v2 paper-style metrics.
