# VMAT/IMRT Metric Definitions

This appendix is generated from the shared metric-definition catalog.

## `mus` - MUs

- Group: Plan prescription
- Symbol/short name: MUs
- Mathematical definition: MUs = sum_beams(MU_beam)
- Physical meaning: Total monitor units delivered by the plan.
- Unit: MU
- Inputs required: Plan MU, prescription, fraction count, beam list
- Status: implemented
- Notes: None

## `pmu` - PMU

- Group: Plan prescription
- Symbol/short name: PMU
- Mathematical definition: PMU = MUs * (2 Gy / fraction dose in Gy)
- Physical meaning: Monitor units normalized to a standard 2 Gy fraction.
- Unit: MU
- Inputs required: Plan MU, prescription, fraction count, beam list
- Status: implemented
- Notes: None

## `muca` - MUCA

- Group: Plan prescription
- Symbol/short name: MUCA
- Mathematical definition: MUCA = MUs / N_control_arcs
- Physical meaning: Average monitor units delivered per control arc.
- Unit: MU/control arc
- Inputs required: Plan MU, prescription, fraction count, beam list
- Status: implemented
- Notes: None

## `fraction_dose_gy` - Prescribed Dose

- Group: Plan prescription
- Symbol/short name: Prescribed Dose
- Mathematical definition: Fraction dose = prescribed dose / number of fractions
- Physical meaning: Dose prescribed per fraction.
- Unit: Gy
- Inputs required: Plan MU, prescription, fraction count, beam list
- Status: implemented
- Notes: None

## `fractions_count` - Fractions

- Group: Plan prescription
- Symbol/short name: Fractions
- Mathematical definition: Fractions = N_fx
- Physical meaning: Number of planned treatment fractions.
- Unit: count
- Inputs required: Plan MU, prescription, fraction count, beam list
- Status: implemented
- Notes: None

## `mucgy` - MUcGy

- Group: Plan prescription
- Symbol/short name: MUcGy
- Mathematical definition: MUcGy = MUs / prescribed dose in cGy
- Physical meaning: Monitor units delivered per centigray of prescribed dose.
- Unit: MU/cGy
- Inputs required: Plan MU, prescription, fraction count, beam list
- Status: implemented
- Notes: None

## `lt` - LT

- Group: Leaf travel
- Symbol/short name: LT
- Mathematical definition: LT = weighted mean over control arcs of total leaf travel between adjacent apertures
- Physical meaning: Average total leaf travel across a control arc.
- Unit: mm
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `lt_mlcx1` - LT MLCX1

- Group: Leaf travel
- Symbol/short name: LT MLCX1
- Mathematical definition: Same formula as LT, but computed using MLCX1 apertures only.
- Physical meaning: Average total leaf travel across a control arc. Reported for MLCX1.
- Unit: mm
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LT.

## `lt_mlcx2` - LT MLCX2

- Group: Leaf travel
- Symbol/short name: LT MLCX2
- Mathematical definition: Same formula as LT, but computed using MLCX2 apertures only.
- Physical meaning: Average total leaf travel across a control arc. Reported for MLCX2.
- Unit: mm
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LT.

## `ltmu` - LTMU

- Group: Leaf travel
- Symbol/short name: LTMU
- Mathematical definition: LTMU = sum(control-arc leaf travel) / MU_beam
- Physical meaning: Leaf travel normalized by delivered monitor units.
- Unit: mm/MU
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `ltmu_mlcx1` - LTMU MLCX1

- Group: Leaf travel
- Symbol/short name: LTMU MLCX1
- Mathematical definition: Same formula as LTMU, but computed using MLCX1 apertures only.
- Physical meaning: Leaf travel normalized by delivered monitor units. Reported for MLCX1.
- Unit: mm/MU
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTMU.

## `ltmu_mlcx2` - LTMU MLCX2

- Group: Leaf travel
- Symbol/short name: LTMU MLCX2
- Mathematical definition: Same formula as LTMU, but computed using MLCX2 apertures only.
- Physical meaning: Leaf travel normalized by delivered monitor units. Reported for MLCX2.
- Unit: mm/MU
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTMU.

## `ltnlmu` - LTNLMU

- Group: Leaf travel
- Symbol/short name: LTNLMU
- Mathematical definition: LTNLMU = sum(leaf travel / active leaves) / MU_beam
- Physical meaning: Leaf travel per involved leaf, normalized by monitor units.
- Unit: mm/(leaf*MU)
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `ltnlmu_mlcx1` - LTNLMU MLCX1

- Group: Leaf travel
- Symbol/short name: LTNLMU MLCX1
- Mathematical definition: Same formula as LTNLMU, but computed using MLCX1 apertures only.
- Physical meaning: Leaf travel per involved leaf, normalized by monitor units. Reported for MLCX1.
- Unit: mm/(leaf*MU)
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTNLMU.

## `ltnlmu_mlcx2` - LTNLMU MLCX2

- Group: Leaf travel
- Symbol/short name: LTNLMU MLCX2
- Mathematical definition: Same formula as LTNLMU, but computed using MLCX2 apertures only.
- Physical meaning: Leaf travel per involved leaf, normalized by monitor units. Reported for MLCX2.
- Unit: mm/(leaf*MU)
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTNLMU.

## `nl` - NL

- Group: Leaf travel
- Symbol/short name: NL
- Mathematical definition: NL = weighted mean over control points of the number of active leaf pairs
- Physical meaning: Average number of leaves actively shaping the aperture.
- Unit: count
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `nl_mlcx1` - NL MLCX1

- Group: Leaf travel
- Symbol/short name: NL MLCX1
- Mathematical definition: Same formula as NL, but computed using MLCX1 apertures only.
- Physical meaning: Average number of leaves actively shaping the aperture. Reported for MLCX1.
- Unit: count
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for NL.

## `nl_mlcx2` - NL MLCX2

- Group: Leaf travel
- Symbol/short name: NL MLCX2
- Mathematical definition: Same formula as NL, but computed using MLCX2 apertures only.
- Physical meaning: Average number of leaves actively shaping the aperture. Reported for MLCX2.
- Unit: count
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for NL.

## `ltnl` - LTNL

- Group: Leaf travel
- Symbol/short name: LTNL
- Mathematical definition: LTNL = weighted mean of (leaf travel / active leaves)
- Physical meaning: Leaf travel normalized by the number of involved leaves.
- Unit: mm/leaf
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `ltnl_mlcx1` - LTNL MLCX1

- Group: Leaf travel
- Symbol/short name: LTNL MLCX1
- Mathematical definition: Same formula as LTNL, but computed using MLCX1 apertures only.
- Physical meaning: Leaf travel normalized by the number of involved leaves. Reported for MLCX1.
- Unit: mm/leaf
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTNL.

## `ltnl_mlcx2` - LTNL MLCX2

- Group: Leaf travel
- Symbol/short name: LTNL MLCX2
- Mathematical definition: Same formula as LTNL, but computed using MLCX2 apertures only.
- Physical meaning: Leaf travel normalized by the number of involved leaves. Reported for MLCX2.
- Unit: mm/leaf
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTNL.

## `al` - AL

- Group: Arc geometry
- Symbol/short name: AL
- Mathematical definition: AL = total gantry travel / N_beams
- Physical meaning: Average arc length delivered per beam.
- Unit: deg
- Inputs required: Beam gantry rotation angle and beam MU
- Status: implemented
- Notes: None

## `lna` - LNA

- Group: Leaf travel
- Symbol/short name: LNA
- Mathematical definition: LNA = weighted mean of (leaf travel / active leaves / gantry-step)
- Physical meaning: Leaf travel per involved leaf and per unit gantry travel.
- Unit: mm/(leaf*deg)
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `lna_mlcx1` - LNA MLCX1

- Group: Leaf travel
- Symbol/short name: LNA MLCX1
- Mathematical definition: Same formula as LNA, but computed using MLCX1 apertures only.
- Physical meaning: Leaf travel per involved leaf and per unit gantry travel. Reported for MLCX1.
- Unit: mm/(leaf*deg)
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LNA.

## `lna_mlcx2` - LNA MLCX2

- Group: Leaf travel
- Symbol/short name: LNA MLCX2
- Mathematical definition: Same formula as LNA, but computed using MLCX2 apertures only.
- Physical meaning: Leaf travel per involved leaf and per unit gantry travel. Reported for MLCX2.
- Unit: mm/(leaf*deg)
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LNA.

## `cal` - CAL

- Group: Arc geometry
- Symbol/short name: CAL
- Mathematical definition: CAL = total gantry travel / N_control_arcs
- Physical meaning: Average control-arc length between successive control points.
- Unit: deg/control arc
- Inputs required: Beam gantry rotation angle and beam MU
- Status: implemented
- Notes: None

## `gt` - GT

- Group: Arc geometry
- Symbol/short name: GT
- Mathematical definition: GT = sum_beams(abs(gantry rotation angle))
- Physical meaning: Total gantry travel delivered by the plan.
- Unit: deg
- Inputs required: Beam gantry rotation angle and beam MU
- Status: implemented
- Notes: None

## `mudeg` - MUdeg

- Group: Arc geometry
- Symbol/short name: MUdeg
- Mathematical definition: MUdeg = MUs / GT
- Physical meaning: Monitor units delivered per degree of gantry rotation.
- Unit: MU/deg
- Inputs required: Beam gantry rotation angle and beam MU
- Status: implemented
- Notes: None

## `ltal` - LTAL

- Group: Leaf travel
- Symbol/short name: LTAL
- Mathematical definition: LTAL = weighted mean of (leaf travel / gantry-step)
- Physical meaning: Leaf travel normalized by unit gantry angle.
- Unit: mm/deg
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `ltal_mlcx1` - LTAL MLCX1

- Group: Leaf travel
- Symbol/short name: LTAL MLCX1
- Mathematical definition: Same formula as LTAL, but computed using MLCX1 apertures only.
- Physical meaning: Leaf travel normalized by unit gantry angle. Reported for MLCX1.
- Unit: mm/deg
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTAL.

## `ltal_mlcx2` - LTAL MLCX2

- Group: Leaf travel
- Symbol/short name: LTAL MLCX2
- Mathematical definition: Same formula as LTAL, but computed using MLCX2 apertures only.
- Physical meaning: Leaf travel normalized by unit gantry angle. Reported for MLCX2.
- Unit: mm/deg
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LTAL.

## `narcs` - NArcs

- Group: Plan prescription
- Symbol/short name: NArcs
- Mathematical definition: NArcs = number of treatment beams/arcs
- Physical meaning: Number of treatment arcs or beams contributing to the plan.
- Unit: count
- Inputs required: Plan MU, prescription, fraction count, beam list
- Status: implemented
- Notes: None

## `mdrv` - mDRV

- Group: Delivery dynamics
- Symbol/short name: mDRV
- Mathematical definition: mDRV = mean(delta dose-rate / delta gantry)
- Physical meaning: Mean variation of dose rate during delivery.
- Unit: MU/(min*deg)
- Inputs required: Control-point MLC motion, dose rate, gantry angle, and meterset timing
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `mdrv_mlcx1` - mDRV MLCX1

- Group: Delivery dynamics
- Symbol/short name: mDRV MLCX1
- Mathematical definition: Same formula as mDRV, but computed using MLCX1 apertures only.
- Physical meaning: Mean variation of dose rate during delivery. Reported for MLCX1.
- Unit: MU/(min*deg)
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for mDRV.

## `mdrv_mlcx2` - mDRV MLCX2

- Group: Delivery dynamics
- Symbol/short name: mDRV MLCX2
- Mathematical definition: Same formula as mDRV, but computed using MLCX2 apertures only.
- Physical meaning: Mean variation of dose rate during delivery. Reported for MLCX2.
- Unit: MU/(min*deg)
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for mDRV.

## `mgsv` - mGSV

- Group: Delivery dynamics
- Symbol/short name: mGSV
- Mathematical definition: mGSV = mean(delta gantry-speed / delta gantry)
- Physical meaning: Mean variation of gantry speed during delivery.
- Unit: deg/s/deg
- Inputs required: Control-point MLC motion, dose rate, gantry angle, and meterset timing
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `mgsv_mlcx1` - mGSV MLCX1

- Group: Delivery dynamics
- Symbol/short name: mGSV MLCX1
- Mathematical definition: Same formula as mGSV, but computed using MLCX1 apertures only.
- Physical meaning: Mean variation of gantry speed during delivery. Reported for MLCX1.
- Unit: deg/s/deg
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for mGSV.

## `mgsv_mlcx2` - mGSV MLCX2

- Group: Delivery dynamics
- Symbol/short name: mGSV MLCX2
- Mathematical definition: Same formula as mGSV, but computed using MLCX2 apertures only.
- Physical meaning: Mean variation of gantry speed during delivery. Reported for MLCX2.
- Unit: deg/s/deg
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for mGSV.

## `dr` - DR

- Group: Delivery dynamics
- Symbol/short name: DR
- Mathematical definition: DR = mean(control-point dose rate)
- Physical meaning: Average dose rate used during delivery.
- Unit: MU/min
- Inputs required: Control-point MLC motion, dose rate, gantry angle, and meterset timing
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `dr_mlcx1` - DR MLCX1

- Group: Delivery dynamics
- Symbol/short name: DR MLCX1
- Mathematical definition: Same formula as DR, but computed using MLCX1 apertures only.
- Physical meaning: Average dose rate used during delivery. Reported for MLCX1.
- Unit: MU/min
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for DR.

## `dr_mlcx2` - DR MLCX2

- Group: Delivery dynamics
- Symbol/short name: DR MLCX2
- Mathematical definition: Same formula as DR, but computed using MLCX2 apertures only.
- Physical meaning: Average dose rate used during delivery. Reported for MLCX2.
- Unit: MU/min
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for DR.

## `gs` - GS

- Group: Delivery dynamics
- Symbol/short name: GS
- Mathematical definition: GS = mean(control-point gantry speed)
- Physical meaning: Average gantry speed during arc delivery.
- Unit: deg/s
- Inputs required: Control-point MLC motion, dose rate, gantry angle, and meterset timing
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `gs_mlcx1` - GS MLCX1

- Group: Delivery dynamics
- Symbol/short name: GS MLCX1
- Mathematical definition: Same formula as GS, but computed using MLCX1 apertures only.
- Physical meaning: Average gantry speed during arc delivery. Reported for MLCX1.
- Unit: deg/s
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for GS.

## `gs_mlcx2` - GS MLCX2

- Group: Delivery dynamics
- Symbol/short name: GS MLCX2
- Mathematical definition: Same formula as GS, but computed using MLCX2 apertures only.
- Physical meaning: Average gantry speed during arc delivery. Reported for MLCX2.
- Unit: deg/s
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for GS.

## `ls` - LS

- Group: Delivery dynamics
- Symbol/short name: LS
- Mathematical definition: LS = mean(leaf speed)
- Physical meaning: Average leaf speed during delivery.
- Unit: mm/s
- Inputs required: Control-point MLC motion, dose rate, gantry angle, and meterset timing
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `ls_mlcx1` - LS MLCX1

- Group: Delivery dynamics
- Symbol/short name: LS MLCX1
- Mathematical definition: Same formula as LS, but computed using MLCX1 apertures only.
- Physical meaning: Average leaf speed during delivery. Reported for MLCX1.
- Unit: mm/s
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LS.

## `ls_mlcx2` - LS MLCX2

- Group: Delivery dynamics
- Symbol/short name: LS MLCX2
- Mathematical definition: Same formula as LS, but computed using MLCX2 apertures only.
- Physical meaning: Average leaf speed during delivery. Reported for MLCX2.
- Unit: mm/s
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LS.

## `mcsv` - MCSv

- Group: McNiven-style modulation
- Symbol/short name: MCSv
- Mathematical definition: MCSv = weighted mean[((AAV_i + AAV_{i+1}) / 2) * ((LSV_i + LSV_{i+1}) / 2)]
- Physical meaning: Overall aperture modulation score combining area and leaf sequence variability.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `mcsv_mlcx1` - MCSv MLCX1

- Group: McNiven-style modulation
- Symbol/short name: MCSv MLCX1
- Mathematical definition: Same formula as MCSv, but computed using MLCX1 apertures only.
- Physical meaning: Overall aperture modulation score combining area and leaf sequence variability. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MCSv.

## `mcsv_mlcx2` - MCSv MLCX2

- Group: McNiven-style modulation
- Symbol/short name: MCSv MLCX2
- Mathematical definition: Same formula as MCSv, but computed using MLCX2 apertures only.
- Physical meaning: Overall aperture modulation score combining area and leaf sequence variability. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MCSv.

## `aav` - AAV

- Group: McNiven-style modulation
- Symbol/short name: AAV
- Mathematical definition: AAV = aperture area / arc-level union aperture area, then weighted over the arc
- Physical meaning: Variability of aperture area across control points.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `aav_mlcx1` - AAV MLCX1

- Group: McNiven-style modulation
- Symbol/short name: AAV MLCX1
- Mathematical definition: Same formula as AAV, but computed using MLCX1 apertures only.
- Physical meaning: Variability of aperture area across control points. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for AAV.

## `aav_mlcx2` - AAV MLCX2

- Group: McNiven-style modulation
- Symbol/short name: AAV MLCX2
- Mathematical definition: Same formula as AAV, but computed using MLCX2 apertures only.
- Physical meaning: Variability of aperture area across control points. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for AAV.

## `lsv` - LSV

- Group: McNiven-style modulation
- Symbol/short name: LSV
- Mathematical definition: LSV = bank_LSV(left) * bank_LSV(right), then weighted over the arc
- Physical meaning: Variability of the leaf sequence pattern across the aperture.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `lsv_mlcx1` - LSV MLCX1

- Group: McNiven-style modulation
- Symbol/short name: LSV MLCX1
- Mathematical definition: Same formula as LSV, but computed using MLCX1 apertures only.
- Physical meaning: Variability of the leaf sequence pattern across the aperture. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LSV.

## `lsv_mlcx2` - LSV MLCX2

- Group: McNiven-style modulation
- Symbol/short name: LSV MLCX2
- Mathematical definition: Same formula as LSV, but computed using MLCX2 apertures only.
- Physical meaning: Variability of the leaf sequence pattern across the aperture. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for LSV.

## `tg` - TG

- Group: McNiven-style modulation
- Symbol/short name: TG
- Mathematical definition: TG = weighted mean of adjacent-leaf left/right offset magnitudes
- Physical meaning: Average tongue-and-groove offset between neighboring leaves.
- Unit: mm
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `tg_mlcx1` - TG MLCX1

- Group: McNiven-style modulation
- Symbol/short name: TG MLCX1
- Mathematical definition: Same formula as TG, but computed using MLCX1 apertures only.
- Physical meaning: Average tongue-and-groove offset between neighboring leaves. Reported for MLCX1.
- Unit: mm
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for TG.

## `tg_mlcx2` - TG MLCX2

- Group: McNiven-style modulation
- Symbol/short name: TG MLCX2
- Mathematical definition: Same formula as TG, but computed using MLCX2 apertures only.
- Physical meaning: Average tongue-and-groove offset between neighboring leaves. Reported for MLCX2.
- Unit: mm
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for TG.

## `mi_0_2` - MI(0.2)

- Group: MI family
- Symbol/short name: MI(0.2)
- Mathematical definition: MI(k=0.2) = (MIs, MIa, MIt) at threshold factor k = 0.2
- Physical meaning: Modulation index using a 0.2 threshold factor.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: The base key returns a tuple of speed, acceleration, and total MI components before flattening.

## `mi_0_2_mis` - MI(0.2) Speed

- Group: MI components
- Symbol/short name: MI(0.2) Speed
- Mathematical definition: MIs(0.2) = mean_beams[ mean_CP min(v / sigma_v, 0.2) ]
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 0.2.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

## `mi_0_2_mia` - MI(0.2) Acceleration

- Group: MI components
- Symbol/short name: MI(0.2) Acceleration
- Mathematical definition: MIa(0.2) = mean_beams[ mean_CP min(max(v / sigma_v, a / (alpha * sigma_a)), 0.2) ]
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 0.2.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

## `mi_0_2_mit` - MI(0.2) Total

- Group: MI components
- Symbol/short name: MI(0.2) Total
- Mathematical definition: MIt(0.2) = weighted mean over control points of min(max(v / sigma_v, a / (alpha * sigma_a)), 0.2)
- Physical meaning: Total modulation index with threshold factor 0.2.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

## `mi_0_2_mlcx1_mis` - MI(0.2) MLCX1 Speed

- Group: MI components
- Symbol/short name: MI(0.2) MLCX1 Speed
- Mathematical definition: Same speed-component MI formula as MI(0.2), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 0.2 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

## `mi_0_2_mlcx1_mia` - MI(0.2) MLCX1 Acceleration

- Group: MI components
- Symbol/short name: MI(0.2) MLCX1 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(0.2), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 0.2 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

## `mi_0_2_mlcx1_mit` - MI(0.2) MLCX1 Total

- Group: MI components
- Symbol/short name: MI(0.2) MLCX1 Total
- Mathematical definition: Same total-component MI formula as MI(0.2), but restricted to MLCX1 leaf positions.
- Physical meaning: Total modulation index with threshold factor 0.2 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

## `mi_0_2_mlcx2_mis` - MI(0.2) MLCX2 Speed

- Group: MI components
- Symbol/short name: MI(0.2) MLCX2 Speed
- Mathematical definition: Same speed-component MI formula as MI(0.2), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 0.2 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

## `mi_0_2_mlcx2_mia` - MI(0.2) MLCX2 Acceleration

- Group: MI components
- Symbol/short name: MI(0.2) MLCX2 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(0.2), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 0.2 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

## `mi_0_2_mlcx2_mit` - MI(0.2) MLCX2 Total

- Group: MI components
- Symbol/short name: MI(0.2) MLCX2 Total
- Mathematical definition: Same total-component MI formula as MI(0.2), but restricted to MLCX2 leaf positions.
- Physical meaning: Total modulation index with threshold factor 0.2 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

## `mi_0_5` - MI(0.5)

- Group: MI family
- Symbol/short name: MI(0.5)
- Mathematical definition: MI(k=0.5) = (MIs, MIa, MIt) at threshold factor k = 0.5
- Physical meaning: Modulation index using a 0.5 threshold factor.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: The base key returns a tuple of speed, acceleration, and total MI components before flattening.

## `mi_0_5_mis` - MI(0.5) Speed

- Group: MI components
- Symbol/short name: MI(0.5) Speed
- Mathematical definition: MIs(0.5) = mean_beams[ mean_CP min(v / sigma_v, 0.5) ]
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 0.5.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

## `mi_0_5_mia` - MI(0.5) Acceleration

- Group: MI components
- Symbol/short name: MI(0.5) Acceleration
- Mathematical definition: MIa(0.5) = mean_beams[ mean_CP min(max(v / sigma_v, a / (alpha * sigma_a)), 0.5) ]
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 0.5.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

## `mi_0_5_mit` - MI(0.5) Total

- Group: MI components
- Symbol/short name: MI(0.5) Total
- Mathematical definition: MIt(0.5) = weighted mean over control points of min(max(v / sigma_v, a / (alpha * sigma_a)), 0.5)
- Physical meaning: Total modulation index with threshold factor 0.5.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

## `mi_0_5_mlcx1_mis` - MI(0.5) MLCX1 Speed

- Group: MI components
- Symbol/short name: MI(0.5) MLCX1 Speed
- Mathematical definition: Same speed-component MI formula as MI(0.5), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 0.5 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

## `mi_0_5_mlcx1_mia` - MI(0.5) MLCX1 Acceleration

- Group: MI components
- Symbol/short name: MI(0.5) MLCX1 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(0.5), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 0.5 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

## `mi_0_5_mlcx1_mit` - MI(0.5) MLCX1 Total

- Group: MI components
- Symbol/short name: MI(0.5) MLCX1 Total
- Mathematical definition: Same total-component MI formula as MI(0.5), but restricted to MLCX1 leaf positions.
- Physical meaning: Total modulation index with threshold factor 0.5 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

## `mi_0_5_mlcx2_mis` - MI(0.5) MLCX2 Speed

- Group: MI components
- Symbol/short name: MI(0.5) MLCX2 Speed
- Mathematical definition: Same speed-component MI formula as MI(0.5), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 0.5 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

## `mi_0_5_mlcx2_mia` - MI(0.5) MLCX2 Acceleration

- Group: MI components
- Symbol/short name: MI(0.5) MLCX2 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(0.5), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 0.5 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

## `mi_0_5_mlcx2_mit` - MI(0.5) MLCX2 Total

- Group: MI components
- Symbol/short name: MI(0.5) MLCX2 Total
- Mathematical definition: Same total-component MI formula as MI(0.5), but restricted to MLCX2 leaf positions.
- Physical meaning: Total modulation index with threshold factor 0.5 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

## `mi_1_0` - MI(1.0)

- Group: MI family
- Symbol/short name: MI(1.0)
- Mathematical definition: MI(k=1.0) = (MIs, MIa, MIt) at threshold factor k = 1.0
- Physical meaning: Modulation index using a 1.0 threshold factor.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: The base key returns a tuple of speed, acceleration, and total MI components before flattening.

## `mi_1_0_mis` - MI(1.0) Speed

- Group: MI components
- Symbol/short name: MI(1.0) Speed
- Mathematical definition: MIs(1.0) = mean_beams[ mean_CP min(v / sigma_v, 1.0) ]
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 1.0.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

## `mi_1_0_mia` - MI(1.0) Acceleration

- Group: MI components
- Symbol/short name: MI(1.0) Acceleration
- Mathematical definition: MIa(1.0) = mean_beams[ mean_CP min(max(v / sigma_v, a / (alpha * sigma_a)), 1.0) ]
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 1.0.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

## `mi_1_0_mit` - MI(1.0) Total

- Group: MI components
- Symbol/short name: MI(1.0) Total
- Mathematical definition: MIt(1.0) = weighted mean over control points of min(max(v / sigma_v, a / (alpha * sigma_a)), 1.0)
- Physical meaning: Total modulation index with threshold factor 1.0.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

## `mi_1_0_mlcx1_mis` - MI(1.0) MLCX1 Speed

- Group: MI components
- Symbol/short name: MI(1.0) MLCX1 Speed
- Mathematical definition: Same speed-component MI formula as MI(1.0), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 1.0 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

## `mi_1_0_mlcx1_mia` - MI(1.0) MLCX1 Acceleration

- Group: MI components
- Symbol/short name: MI(1.0) MLCX1 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(1.0), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 1.0 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

## `mi_1_0_mlcx1_mit` - MI(1.0) MLCX1 Total

- Group: MI components
- Symbol/short name: MI(1.0) MLCX1 Total
- Mathematical definition: Same total-component MI formula as MI(1.0), but restricted to MLCX1 leaf positions.
- Physical meaning: Total modulation index with threshold factor 1.0 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

## `mi_1_0_mlcx2_mis` - MI(1.0) MLCX2 Speed

- Group: MI components
- Symbol/short name: MI(1.0) MLCX2 Speed
- Mathematical definition: Same speed-component MI formula as MI(1.0), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 1.0 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

## `mi_1_0_mlcx2_mia` - MI(1.0) MLCX2 Acceleration

- Group: MI components
- Symbol/short name: MI(1.0) MLCX2 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(1.0), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 1.0 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

## `mi_1_0_mlcx2_mit` - MI(1.0) MLCX2 Total

- Group: MI components
- Symbol/short name: MI(1.0) MLCX2 Total
- Mathematical definition: Same total-component MI formula as MI(1.0), but restricted to MLCX2 leaf positions.
- Physical meaning: Total modulation index with threshold factor 1.0 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

## `mi_2_0` - MI(2.0)

- Group: MI family
- Symbol/short name: MI(2.0)
- Mathematical definition: MI(k=2.0) = (MIs, MIa, MIt) at threshold factor k = 2.0
- Physical meaning: Modulation index using a 2.0 threshold factor.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: The base key returns a tuple of speed, acceleration, and total MI components before flattening.

## `mi_2_0_mis` - MI(2.0) Speed

- Group: MI components
- Symbol/short name: MI(2.0) Speed
- Mathematical definition: MIs(2.0) = mean_beams[ mean_CP min(v / sigma_v, 2.0) ]
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 2.0.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

## `mi_2_0_mia` - MI(2.0) Acceleration

- Group: MI components
- Symbol/short name: MI(2.0) Acceleration
- Mathematical definition: MIa(2.0) = mean_beams[ mean_CP min(max(v / sigma_v, a / (alpha * sigma_a)), 2.0) ]
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 2.0.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

## `mi_2_0_mit` - MI(2.0) Total

- Group: MI components
- Symbol/short name: MI(2.0) Total
- Mathematical definition: MIt(2.0) = weighted mean over control points of min(max(v / sigma_v, a / (alpha * sigma_a)), 2.0)
- Physical meaning: Total modulation index with threshold factor 2.0.
- Unit: dimensionless
- Inputs required: MLC speed, MLC acceleration, speed/acceleration spread, gantry and dose-rate weights
- Status: implemented_flattened
- Notes: Flattened export component of the Park 2014 modulation-index tuple.

## `mi_2_0_mlcx1_mis` - MI(2.0) MLCX1 Speed

- Group: MI components
- Symbol/short name: MI(2.0) MLCX1 Speed
- Mathematical definition: Same speed-component MI formula as MI(2.0), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 2.0 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

## `mi_2_0_mlcx1_mia` - MI(2.0) MLCX1 Acceleration

- Group: MI components
- Symbol/short name: MI(2.0) MLCX1 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(2.0), but restricted to MLCX1 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 2.0 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

## `mi_2_0_mlcx1_mit` - MI(2.0) MLCX1 Total

- Group: MI components
- Symbol/short name: MI(2.0) MLCX1 Total
- Mathematical definition: Same total-component MI formula as MI(2.0), but restricted to MLCX1 leaf positions.
- Physical meaning: Total modulation index with threshold factor 2.0 for MLCX1.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX1.

## `mi_2_0_mlcx2_mis` - MI(2.0) MLCX2 Speed

- Group: MI components
- Symbol/short name: MI(2.0) MLCX2 Speed
- Mathematical definition: Same speed-component MI formula as MI(2.0), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf speed contribution to the modulation index with threshold factor 2.0 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

## `mi_2_0_mlcx2_mia` - MI(2.0) MLCX2 Acceleration

- Group: MI components
- Symbol/short name: MI(2.0) MLCX2 Acceleration
- Mathematical definition: Same acceleration-component MI formula as MI(2.0), but restricted to MLCX2 leaf positions.
- Physical meaning: Leaf acceleration contribution to the modulation index with threshold factor 2.0 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

## `mi_2_0_mlcx2_mit` - MI(2.0) MLCX2 Total

- Group: MI components
- Symbol/short name: MI(2.0) MLCX2 Total
- Mathematical definition: Same total-component MI formula as MI(2.0), but restricted to MLCX2 leaf positions.
- Physical meaning: Total modulation index with threshold factor 2.0 for MLCX2.
- Unit: dimensionless
- Inputs required: Per-layer MLC speed and acceleration traces
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MLCX2.

## `dt` - dt

- Group: Delivery dynamics
- Symbol/short name: dt
- Mathematical definition: dt = mean(control-point time increment) * N_control_points
- Physical meaning: Beam-on delivery time.
- Unit: s
- Inputs required: Control-point MLC motion, dose rate, gantry angle, and meterset timing
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `dt_mlcx1` - dt MLCX1

- Group: Delivery dynamics
- Symbol/short name: dt MLCX1
- Mathematical definition: Same formula as dt, but computed using MLCX1 apertures only.
- Physical meaning: Beam-on delivery time. Reported for MLCX1.
- Unit: s
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for dt.

## `dt_mlcx2` - dt MLCX2

- Group: Delivery dynamics
- Symbol/short name: dt MLCX2
- Mathematical definition: Same formula as dt, but computed using MLCX2 apertures only.
- Physical meaning: Beam-on delivery time. Reported for MLCX2.
- Unit: s
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for dt.

## `pi` - PI

- Group: Shape modulation
- Symbol/short name: PI
- Mathematical definition: PI = perimeter^2 / (4 * pi * area), aggregated over apertures
- Physical meaning: Irregularity of the aperture shape relative to its area.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `pi_mlcx1` - PI MLCX1

- Group: Shape modulation
- Symbol/short name: PI MLCX1
- Mathematical definition: Same formula as PI, but computed using MLCX1 apertures only.
- Physical meaning: Irregularity of the aperture shape relative to its area. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for PI.

## `pi_mlcx2` - PI MLCX2

- Group: Shape modulation
- Symbol/short name: PI MLCX2
- Mathematical definition: Same formula as PI, but computed using MLCX2 apertures only.
- Physical meaning: Irregularity of the aperture shape relative to its area. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for PI.

## `pm` - PM

- Group: Shape modulation
- Symbol/short name: PM
- Mathematical definition: PM = mean over adjacent control points of normalized aperture-area change
- Physical meaning: Variation in aperture area between successive control points.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `pm_mlcx1` - PM MLCX1

- Group: Shape modulation
- Symbol/short name: PM MLCX1
- Mathematical definition: Same formula as PM, but computed using MLCX1 apertures only.
- Physical meaning: Variation in aperture area between successive control points. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for PM.

## `pm_mlcx2` - PM MLCX2

- Group: Shape modulation
- Symbol/short name: PM MLCX2
- Mathematical definition: Same formula as PM, but computed using MLCX2 apertures only.
- Physical meaning: Variation in aperture area between successive control points. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for PM.

## `md` - MD

- Group: Shape modulation
- Symbol/short name: MD
- Mathematical definition: MD = union-area / weighted mean aperture area
- Physical meaning: Degree of modulation present in the delivered field shapes.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `md_mlcx1` - MD MLCX1

- Group: Shape modulation
- Symbol/short name: MD MLCX1
- Mathematical definition: Same formula as MD, but computed using MLCX1 apertures only.
- Physical meaning: Degree of modulation present in the delivered field shapes. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MD.

## `md_mlcx2` - MD MLCX2

- Group: Shape modulation
- Symbol/short name: MD MLCX2
- Mathematical definition: Same formula as MD, but computed using MLCX2 apertures only.
- Physical meaning: Degree of modulation present in the delivered field shapes. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MD.

## `pa` - PA

- Group: Aperture geometry
- Symbol/short name: PA
- Mathematical definition: PA = weighted mean(aperture area)
- Physical meaning: Average beam's-eye-view aperture area.
- Unit: mm^2
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `pa_mlcx1` - PA MLCX1

- Group: Aperture geometry
- Symbol/short name: PA MLCX1
- Mathematical definition: Same formula as PA, but computed using MLCX1 apertures only.
- Physical meaning: Average beam's-eye-view aperture area. Reported for MLCX1.
- Unit: mm^2
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for PA.

## `pa_mlcx2` - PA MLCX2

- Group: Aperture geometry
- Symbol/short name: PA MLCX2
- Mathematical definition: Same formula as PA, but computed using MLCX2 apertures only.
- Physical meaning: Average beam's-eye-view aperture area. Reported for MLCX2.
- Unit: mm^2
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for PA.

## `efs` - EFS

- Group: Aperture geometry
- Symbol/short name: EFS
- Mathematical definition: EFS = weighted mean(4 * area / perimeter)
- Physical meaning: Equivalent square field size of the aperture.
- Unit: mm
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `efs_mlcx1` - EFS MLCX1

- Group: Aperture geometry
- Symbol/short name: EFS MLCX1
- Mathematical definition: Same formula as EFS, but computed using MLCX1 apertures only.
- Physical meaning: Equivalent square field size of the aperture. Reported for MLCX1.
- Unit: mm
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for EFS.

## `efs_mlcx2` - EFS MLCX2

- Group: Aperture geometry
- Symbol/short name: EFS MLCX2
- Mathematical definition: Same formula as EFS, but computed using MLCX2 apertures only.
- Physical meaning: Equivalent square field size of the aperture. Reported for MLCX2.
- Unit: mm
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for EFS.

## `psmall` - psmall

- Group: Aperture geometry
- Symbol/short name: psmall
- Mathematical definition: psmall = weighted fraction(EFS < 30 mm)
- Physical meaning: Fraction of apertures classified as small fields.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `psmall_mlcx1` - psmall MLCX1

- Group: Aperture geometry
- Symbol/short name: psmall MLCX1
- Mathematical definition: Same formula as psmall, but computed using MLCX1 apertures only.
- Physical meaning: Fraction of apertures classified as small fields. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for psmall.

## `psmall_mlcx2` - psmall MLCX2

- Group: Aperture geometry
- Symbol/short name: psmall MLCX2
- Mathematical definition: Same formula as psmall, but computed using MLCX2 apertures only.
- Physical meaning: Fraction of apertures classified as small fields. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for psmall.

## `sas_5mm` - SAS5mm

- Group: Aperture geometry
- Symbol/short name: SAS5mm
- Mathematical definition: SAS5mm = active leaf gaps below 5 mm / all active leaf gaps
- Physical meaning: Fraction of leaf gaps smaller than 5 mm.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `sas_5mm_mlcx1` - SAS5mm MLCX1

- Group: Aperture geometry
- Symbol/short name: SAS5mm MLCX1
- Mathematical definition: Same formula as SAS5mm, but computed using MLCX1 apertures only.
- Physical meaning: Fraction of leaf gaps smaller than 5 mm. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for SAS5mm.

## `sas_5mm_mlcx2` - SAS5mm MLCX2

- Group: Aperture geometry
- Symbol/short name: SAS5mm MLCX2
- Mathematical definition: Same formula as SAS5mm, but computed using MLCX2 apertures only.
- Physical meaning: Fraction of leaf gaps smaller than 5 mm. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for SAS5mm.

## `sas_10mm` - SAS10mm

- Group: Aperture geometry
- Symbol/short name: SAS10mm
- Mathematical definition: SAS10mm = active leaf gaps below 10 mm / all active leaf gaps
- Physical meaning: Fraction of leaf gaps smaller than 10 mm.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `sas_10mm_mlcx1` - SAS10mm MLCX1

- Group: Aperture geometry
- Symbol/short name: SAS10mm MLCX1
- Mathematical definition: Same formula as SAS10mm, but computed using MLCX1 apertures only.
- Physical meaning: Fraction of leaf gaps smaller than 10 mm. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for SAS10mm.

## `sas_10mm_mlcx2` - SAS10mm MLCX2

- Group: Aperture geometry
- Symbol/short name: SAS10mm MLCX2
- Mathematical definition: Same formula as SAS10mm, but computed using MLCX2 apertures only.
- Physical meaning: Fraction of leaf gaps smaller than 10 mm. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for SAS10mm.

## `sas_20mm` - SAS20mm

- Group: Aperture geometry
- Symbol/short name: SAS20mm
- Mathematical definition: SAS20mm = active leaf gaps below 20 mm / all active leaf gaps
- Physical meaning: Fraction of leaf gaps smaller than 20 mm.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `sas_20mm_mlcx1` - SAS20mm MLCX1

- Group: Aperture geometry
- Symbol/short name: SAS20mm MLCX1
- Mathematical definition: Same formula as SAS20mm, but computed using MLCX1 apertures only.
- Physical meaning: Fraction of leaf gaps smaller than 20 mm. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for SAS20mm.

## `sas_20mm_mlcx2` - SAS20mm MLCX2

- Group: Aperture geometry
- Symbol/short name: SAS20mm MLCX2
- Mathematical definition: Same formula as SAS20mm, but computed using MLCX2 apertures only.
- Physical meaning: Fraction of leaf gaps smaller than 20 mm. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for SAS20mm.

## `em` - EM

- Group: Aperture geometry
- Symbol/short name: EM
- Mathematical definition: EM = aperture edge metric calculated from BEV perimeter relative to area
- Physical meaning: Relative amount of aperture edge compared with open field area.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `em_mlcx1` - EM MLCX1

- Group: Aperture geometry
- Symbol/short name: EM MLCX1
- Mathematical definition: Same formula as EM, but computed using MLCX1 apertures only.
- Physical meaning: Relative amount of aperture edge compared with open field area. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for EM.

## `em_mlcx2` - EM MLCX2

- Group: Aperture geometry
- Symbol/short name: EM MLCX2
- Mathematical definition: Same formula as EM, but computed using MLCX2 apertures only.
- Physical meaning: Relative amount of aperture edge compared with open field area. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for EM.

## `bjar` - BJAR

- Group: Aperture geometry
- Symbol/short name: BJAR
- Mathematical definition: BJAR = aperture area / jaw-defined area
- Physical meaning: Ratio between aperture area and jaw-defined area.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: None

## `mad` - MAD

- Group: Aperture geometry
- Symbol/short name: MAD
- Mathematical definition: MAD = mean distance of open leaf ends from the beam central axis
- Physical meaning: Average distance of the aperture opening from the beam central axis.
- Unit: mm
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `mad_mlcx1` - MAD MLCX1

- Group: Aperture geometry
- Symbol/short name: MAD MLCX1
- Mathematical definition: Same formula as MAD, but computed using MLCX1 apertures only.
- Physical meaning: Average distance of the aperture opening from the beam central axis. Reported for MLCX1.
- Unit: mm
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MAD.

## `mad_mlcx2` - MAD MLCX2

- Group: Aperture geometry
- Symbol/short name: MAD MLCX2
- Mathematical definition: Same formula as MAD, but computed using MLCX2 apertures only.
- Physical meaning: Average distance of the aperture opening from the beam central axis. Reported for MLCX2.
- Unit: mm
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for MAD.

## `alg` - ALG

- Group: Aperture geometry
- Symbol/short name: ALG
- Mathematical definition: ALG = mean(opposing leaf gap over active leaf pairs)
- Physical meaning: Average gap between opposing leaf pairs.
- Unit: mm
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `alg_mlcx1` - ALG MLCX1

- Group: Aperture geometry
- Symbol/short name: ALG MLCX1
- Mathematical definition: Same formula as ALG, but computed using MLCX1 apertures only.
- Physical meaning: Average gap between opposing leaf pairs. Reported for MLCX1.
- Unit: mm
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for ALG.

## `alg_mlcx2` - ALG MLCX2

- Group: Aperture geometry
- Symbol/short name: ALG MLCX2
- Mathematical definition: Same formula as ALG, but computed using MLCX2 apertures only.
- Physical meaning: Average gap between opposing leaf pairs. Reported for MLCX2.
- Unit: mm
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for ALG.

## `alg_sd` - ALG SD

- Group: Aperture geometry
- Symbol/short name: ALG SD
- Mathematical definition: ALG SD = std(opposing leaf gap over active leaf pairs)
- Physical meaning: Standard deviation of the opposing leaf gap.
- Unit: mm
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `alg_sd_mlcx1` - ALG SD MLCX1

- Group: Aperture geometry
- Symbol/short name: ALG SD MLCX1
- Mathematical definition: Same formula as ALG SD, but computed using MLCX1 apertures only.
- Physical meaning: Standard deviation of the opposing leaf gap. Reported for MLCX1.
- Unit: mm
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for ALG SD.

## `alg_sd_mlcx2` - ALG SD MLCX2

- Group: Aperture geometry
- Symbol/short name: ALG SD MLCX2
- Mathematical definition: Same formula as ALG SD, but computed using MLCX2 apertures only.
- Physical meaning: Standard deviation of the opposing leaf gap. Reported for MLCX2.
- Unit: mm
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for ALG SD.

## `perimeter` - P

- Group: Aperture geometry
- Symbol/short name: P
- Mathematical definition: P = mean aperture perimeter in beam's-eye view
- Physical meaning: Average perimeter of the beam's-eye-view aperture.
- Unit: mm
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `perimeter_mlcx1` - P MLCX1

- Group: Aperture geometry
- Symbol/short name: P MLCX1
- Mathematical definition: Same formula as P, but computed using MLCX1 apertures only.
- Physical meaning: Average perimeter of the beam's-eye-view aperture. Reported for MLCX1.
- Unit: mm
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for P.

## `perimeter_mlcx2` - P MLCX2

- Group: Aperture geometry
- Symbol/short name: P MLCX2
- Mathematical definition: Same formula as P, but computed using MLCX2 apertures only.
- Physical meaning: Average perimeter of the beam's-eye-view aperture. Reported for MLCX2.
- Unit: mm
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for P.

## `asr` - ASR

- Group: Aperture geometry
- Symbol/short name: ASR
- Mathematical definition: ASR = mean number of disconnected open aperture sub-regions
- Physical meaning: Average number of disconnected open sub-regions in the aperture.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `asr_mlcx1` - ASR MLCX1

- Group: Aperture geometry
- Symbol/short name: ASR MLCX1
- Mathematical definition: Same formula as ASR, but computed using MLCX1 apertures only.
- Physical meaning: Average number of disconnected open sub-regions in the aperture. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for ASR.

## `asr_mlcx2` - ASR MLCX2

- Group: Aperture geometry
- Symbol/short name: ASR MLCX2
- Mathematical definition: Same formula as ASR, but computed using MLCX2 apertures only.
- Physical meaning: Average number of disconnected open sub-regions in the aperture. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for ASR.

## `axjd` - AXJD

- Group: Aperture geometry
- Symbol/short name: AXJD
- Mathematical definition: AXJD = mean distance between aperture extent and X jaws
- Physical meaning: Distance between aperture extent and X jaws.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: None

## `ayjd` - AYJD

- Group: Aperture geometry
- Symbol/short name: AYJD
- Mathematical definition: AYJD = mean distance between aperture extent and Y jaws
- Physical meaning: Distance between aperture extent and Y jaws.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: None

## `cam` - CAM

- Group: Aperture geometry
- Symbol/short name: CAM
- Mathematical definition: CAM = converted-aperture complexity metric from transformed field geometry
- Physical meaning: Aperture complexity score based on converted field geometry.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `cam_mlcx1` - CAM MLCX1

- Group: Aperture geometry
- Symbol/short name: CAM MLCX1
- Mathematical definition: Same formula as CAM, but computed using MLCX1 apertures only.
- Physical meaning: Aperture complexity score based on converted field geometry. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for CAM.

## `cam_mlcx2` - CAM MLCX2

- Group: Aperture geometry
- Symbol/short name: CAM MLCX2
- Mathematical definition: Same formula as CAM, but computed using MLCX2 apertures only.
- Physical meaning: Aperture complexity score based on converted field geometry. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for CAM.

## `eam` - EAM

- Group: Aperture geometry
- Symbol/short name: EAM
- Mathematical definition: EAM = combined edge-and-area aperture complexity metric
- Physical meaning: Combined edge-and-area measure of aperture complexity.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: For Halcyon/Ethos-style plans, the workflow also exports per-layer MLCX1 and MLCX2 variants.

## `eam_mlcx1` - EAM MLCX1

- Group: Aperture geometry
- Symbol/short name: EAM MLCX1
- Mathematical definition: Same formula as EAM, but computed using MLCX1 apertures only.
- Physical meaning: Combined edge-and-area measure of aperture complexity. Reported for MLCX1.
- Unit: dimensionless
- Inputs required: MLCX1 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for EAM.

## `eam_mlcx2` - EAM MLCX2

- Group: Aperture geometry
- Symbol/short name: EAM MLCX2
- Mathematical definition: Same formula as EAM, but computed using MLCX2 apertures only.
- Physical meaning: Combined edge-and-area measure of aperture complexity. Reported for MLCX2.
- Unit: dimensionless
- Inputs required: MLCX2 leaf positions, control-point weights, and beam geometry
- Status: implemented_flattened
- Notes: Layer-specific flattened export for EAM.

## `mlc_speed_acc` - MLC Speed and Acceleration Proportions (Park 2015)

- Group: Delivery dynamics
- Symbol/short name: MLC Speed/Acceleration Profile
- Mathematical definition: For each leaf, compute the proportion of valid intervals falling into each Park 2015 speed/acceleration bin; then average over leaves and beams.
- Physical meaning: Leaf-wise mean proportions for Park et al. VMAT delivery bins. Speed bins: 0-4, 4-8, 8-12, 12-16, 16-20 mm/s. Acceleration bins: 0-40, 40-80, 80-120, 120-160, 160-200 mm/s^2.
- Unit: dimensionless
- Inputs required: Control-point MLC motion, dose rate, gantry angle, and meterset timing
- Status: implemented
- Notes: The base key returns binned speed/acceleration proportions and summary statistics before flattening.

## `speed_0_4` - Park Speed 0-4 mm/s

- Group: Motion bins
- Symbol/short name: Park Speed 0-4 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 0-4 mm/s) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with speed in 0-4 mm/s.
- Unit: proportion
- Inputs required: Per-leaf MLC speed over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 speed-bin proportion, averaged over leaves.

## `speed_4_8` - Park Speed 4-8 mm/s

- Group: Motion bins
- Symbol/short name: Park Speed 4-8 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 4-8 mm/s) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with speed in 4-8 mm/s.
- Unit: proportion
- Inputs required: Per-leaf MLC speed over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 speed-bin proportion, averaged over leaves.

## `speed_8_12` - Park Speed 8-12 mm/s

- Group: Motion bins
- Symbol/short name: Park Speed 8-12 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 8-12 mm/s) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with speed in 8-12 mm/s.
- Unit: proportion
- Inputs required: Per-leaf MLC speed over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 speed-bin proportion, averaged over leaves.

## `speed_12_16` - Park Speed 12-16 mm/s

- Group: Motion bins
- Symbol/short name: Park Speed 12-16 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 12-16 mm/s) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with speed in 12-16 mm/s.
- Unit: proportion
- Inputs required: Per-leaf MLC speed over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 speed-bin proportion, averaged over leaves.

## `speed_16_20` - Park Speed 16-20 mm/s

- Group: Motion bins
- Symbol/short name: Park Speed 16-20 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 16-20 mm/s) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with speed in 16-20 mm/s.
- Unit: proportion
- Inputs required: Per-leaf MLC speed over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 speed-bin proportion, averaged over leaves.

## `acc_0_40` - Park Acceleration 0-40 mm/s^2

- Group: Motion bins
- Symbol/short name: Park Acceleration 0-40 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 0-40 mm/s^2) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with acceleration in 0-40 mm/s^2.
- Unit: proportion
- Inputs required: Per-leaf MLC acceleration over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 acceleration-bin proportion, averaged over leaves.

## `acc_40_80` - Park Acceleration 40-80 mm/s^2

- Group: Motion bins
- Symbol/short name: Park Acceleration 40-80 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 40-80 mm/s^2) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with acceleration in 40-80 mm/s^2.
- Unit: proportion
- Inputs required: Per-leaf MLC acceleration over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 acceleration-bin proportion, averaged over leaves.

## `acc_80_120` - Park Acceleration 80-120 mm/s^2

- Group: Motion bins
- Symbol/short name: Park Acceleration 80-120 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 80-120 mm/s^2) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with acceleration in 80-120 mm/s^2.
- Unit: proportion
- Inputs required: Per-leaf MLC acceleration over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 acceleration-bin proportion, averaged over leaves.

## `acc_120_160` - Park Acceleration 120-160 mm/s^2

- Group: Motion bins
- Symbol/short name: Park Acceleration 120-160 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 120-160 mm/s^2) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with acceleration in 120-160 mm/s^2.
- Unit: proportion
- Inputs required: Per-leaf MLC acceleration over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 acceleration-bin proportion, averaged over leaves.

## `acc_160_200` - Park Acceleration 160-200 mm/s^2

- Group: Motion bins
- Symbol/short name: Park Acceleration 160-200 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 160-200 mm/s^2) ]
- Physical meaning: Leaf-wise mean proportion of valid control-point intervals with acceleration in 160-200 mm/s^2.
- Unit: proportion
- Inputs required: Per-leaf MLC acceleration over valid control-point intervals
- Status: implemented_flattened
- Notes: Park 2015 acceleration-bin proportion, averaged over leaves.

## `speed_average` - Mean Leaf Speed (mm/s)

- Group: Motion bins
- Symbol/short name: Mean Leaf Speed (mm/s)
- Mathematical definition: mean_leaf(mean_interval(speed))
- Physical meaning: Leaf-wise mean proportions for Park et al. VMAT delivery bins. Speed bins: 0-4, 4-8, 8-12, 12-16, 16-20 mm/s. Acceleration bins: 0-40, 40-80, 80-120, 120-160, 160-200 mm/s^2.
- Unit: mm/s
- Inputs required: Per-leaf motion time series
- Status: implemented_flattened
- Notes: Park 2015 summary statistic flattened for export.

## `acc_average` - Mean Leaf Acceleration (mm/s^2)

- Group: Motion bins
- Symbol/short name: Mean Leaf Acceleration (mm/s^2)
- Mathematical definition: mean_leaf(mean_interval(acceleration))
- Physical meaning: Leaf-wise mean proportions for Park et al. VMAT delivery bins. Speed bins: 0-4, 4-8, 8-12, 12-16, 16-20 mm/s. Acceleration bins: 0-40, 40-80, 80-120, 120-160, 160-200 mm/s^2.
- Unit: mm/s^2
- Inputs required: Per-leaf motion time series
- Status: implemented_flattened
- Notes: Park 2015 summary statistic flattened for export.

## `speed_std` - Mean Leaf Speed SD (mm/s)

- Group: Motion bins
- Symbol/short name: Mean Leaf Speed SD (mm/s)
- Mathematical definition: mean_leaf(std_interval(speed))
- Physical meaning: Leaf-wise mean proportions for Park et al. VMAT delivery bins. Speed bins: 0-4, 4-8, 8-12, 12-16, 16-20 mm/s. Acceleration bins: 0-40, 40-80, 80-120, 120-160, 160-200 mm/s^2.
- Unit: mm/s
- Inputs required: Per-leaf motion time series
- Status: implemented_flattened
- Notes: Park 2015 summary statistic flattened for export.

## `acc_std` - Mean Leaf Acceleration SD (mm/s^2)

- Group: Motion bins
- Symbol/short name: Mean Leaf Acceleration SD (mm/s^2)
- Mathematical definition: mean_leaf(std_interval(acceleration))
- Physical meaning: Leaf-wise mean proportions for Park et al. VMAT delivery bins. Speed bins: 0-4, 4-8, 8-12, 12-16, 16-20 mm/s. Acceleration bins: 0-40, 40-80, 80-120, 120-160, 160-200 mm/s^2.
- Unit: mm/s^2
- Inputs required: Per-leaf motion time series
- Status: implemented_flattened
- Notes: Park 2015 summary statistic flattened for export.

## `mlcx1_speed_0_4` - MLCX1 Park Speed 0-4 mm/s

- Group: Motion bins
- Symbol/short name: MLCX1 Park Speed 0-4 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 0-4 mm/s) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

## `mlcx1_speed_4_8` - MLCX1 Park Speed 4-8 mm/s

- Group: Motion bins
- Symbol/short name: MLCX1 Park Speed 4-8 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 4-8 mm/s) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

## `mlcx1_speed_8_12` - MLCX1 Park Speed 8-12 mm/s

- Group: Motion bins
- Symbol/short name: MLCX1 Park Speed 8-12 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 8-12 mm/s) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

## `mlcx1_speed_12_16` - MLCX1 Park Speed 12-16 mm/s

- Group: Motion bins
- Symbol/short name: MLCX1 Park Speed 12-16 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 12-16 mm/s) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

## `mlcx1_speed_16_20` - MLCX1 Park Speed 16-20 mm/s

- Group: Motion bins
- Symbol/short name: MLCX1 Park Speed 16-20 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 16-20 mm/s) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

## `mlcx1_acc_0_40` - MLCX1 Park Acceleration 0-40 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX1 Park Acceleration 0-40 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 0-40 mm/s^2) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

## `mlcx1_acc_40_80` - MLCX1 Park Acceleration 40-80 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX1 Park Acceleration 40-80 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 40-80 mm/s^2) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

## `mlcx1_acc_80_120` - MLCX1 Park Acceleration 80-120 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX1 Park Acceleration 80-120 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 80-120 mm/s^2) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

## `mlcx1_acc_120_160` - MLCX1 Park Acceleration 120-160 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX1 Park Acceleration 120-160 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 120-160 mm/s^2) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

## `mlcx1_acc_160_200` - MLCX1 Park Acceleration 160-200 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX1 Park Acceleration 160-200 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 160-200 mm/s^2) ], restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

## `mlcx1_speed_average` - MLCX1 Mean Leaf Speed (mm/s)

- Group: Motion bins
- Symbol/short name: MLCX1 Mean Leaf Speed (mm/s)
- Mathematical definition: mean_leaf(mean_interval(speed)), restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: mm/s
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

## `mlcx1_acc_average` - MLCX1 Mean Leaf Acceleration (mm/s^2)

- Group: Motion bins
- Symbol/short name: MLCX1 Mean Leaf Acceleration (mm/s^2)
- Mathematical definition: mean_leaf(mean_interval(acceleration)), restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: mm/s^2
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

## `mlcx1_speed_std` - MLCX1 Mean Leaf Speed SD (mm/s)

- Group: Motion bins
- Symbol/short name: MLCX1 Mean Leaf Speed SD (mm/s)
- Mathematical definition: mean_leaf(std_interval(speed)), restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: mm/s
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

## `mlcx1_acc_std` - MLCX1 Mean Leaf Acceleration SD (mm/s^2)

- Group: Motion bins
- Symbol/short name: MLCX1 Mean Leaf Acceleration SD (mm/s^2)
- Mathematical definition: mean_leaf(std_interval(acceleration)), restricted to MLCX1 leaf positions.
- Physical meaning: MLCX1-only Park 2015 derived motion statistic.
- Unit: mm/s^2
- Inputs required: MLCX1 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX1.

## `mlcx2_speed_0_4` - MLCX2 Park Speed 0-4 mm/s

- Group: Motion bins
- Symbol/short name: MLCX2 Park Speed 0-4 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 0-4 mm/s) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

## `mlcx2_speed_4_8` - MLCX2 Park Speed 4-8 mm/s

- Group: Motion bins
- Symbol/short name: MLCX2 Park Speed 4-8 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 4-8 mm/s) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

## `mlcx2_speed_8_12` - MLCX2 Park Speed 8-12 mm/s

- Group: Motion bins
- Symbol/short name: MLCX2 Park Speed 8-12 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 8-12 mm/s) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

## `mlcx2_speed_12_16` - MLCX2 Park Speed 12-16 mm/s

- Group: Motion bins
- Symbol/short name: MLCX2 Park Speed 12-16 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 12-16 mm/s) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

## `mlcx2_speed_16_20` - MLCX2 Park Speed 16-20 mm/s

- Group: Motion bins
- Symbol/short name: MLCX2 Park Speed 16-20 mm/s
- Mathematical definition: mean_leaf [ proportion(intervals with speed in 16-20 mm/s) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

## `mlcx2_acc_0_40` - MLCX2 Park Acceleration 0-40 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX2 Park Acceleration 0-40 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 0-40 mm/s^2) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

## `mlcx2_acc_40_80` - MLCX2 Park Acceleration 40-80 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX2 Park Acceleration 40-80 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 40-80 mm/s^2) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

## `mlcx2_acc_80_120` - MLCX2 Park Acceleration 80-120 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX2 Park Acceleration 80-120 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 80-120 mm/s^2) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

## `mlcx2_acc_120_160` - MLCX2 Park Acceleration 120-160 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX2 Park Acceleration 120-160 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 120-160 mm/s^2) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

## `mlcx2_acc_160_200` - MLCX2 Park Acceleration 160-200 mm/s^2

- Group: Motion bins
- Symbol/short name: MLCX2 Park Acceleration 160-200 mm/s^2
- Mathematical definition: mean_leaf [ proportion(intervals with acceleration in 160-200 mm/s^2) ], restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: proportion
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

## `mlcx2_speed_average` - MLCX2 Mean Leaf Speed (mm/s)

- Group: Motion bins
- Symbol/short name: MLCX2 Mean Leaf Speed (mm/s)
- Mathematical definition: mean_leaf(mean_interval(speed)), restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: mm/s
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

## `mlcx2_acc_average` - MLCX2 Mean Leaf Acceleration (mm/s^2)

- Group: Motion bins
- Symbol/short name: MLCX2 Mean Leaf Acceleration (mm/s^2)
- Mathematical definition: mean_leaf(mean_interval(acceleration)), restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: mm/s^2
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

## `mlcx2_speed_std` - MLCX2 Mean Leaf Speed SD (mm/s)

- Group: Motion bins
- Symbol/short name: MLCX2 Mean Leaf Speed SD (mm/s)
- Mathematical definition: mean_leaf(std_interval(speed)), restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: mm/s
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

## `mlcx2_acc_std` - MLCX2 Mean Leaf Acceleration SD (mm/s^2)

- Group: Motion bins
- Symbol/short name: MLCX2 Mean Leaf Acceleration SD (mm/s^2)
- Mathematical definition: mean_leaf(std_interval(acceleration)), restricted to MLCX2 leaf positions.
- Physical meaning: MLCX2-only Park 2015 derived motion statistic.
- Unit: mm/s^2
- Inputs required: MLCX2 motion traces only
- Status: implemented_flattened
- Notes: Layer-specific Park 2015 flattened export for MLCX2.

## `sport` - SPORT Modulation Index (Li and Xing 2013)

- Group: SPORT
- Symbol/short name: SPORT
- Mathematical definition: SPORT = weighted aggregate of station-wise MI(s) over the plan
- Physical meaning: Station-wise SPORT modulation index MI(s) from Li and Xing, reported here as the framework's beam/plan aggregate summary.
- Unit: dimensionless
- Inputs required: MLC leaf positions, jaw positions, gantry angle, and control-point meterset weights
- Status: implemented
- Notes: None
