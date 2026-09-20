# Ethos report profile

Implement three separately named report metrics without changing generic SAS,
MCSv, MCS5 or Edge Metric. The report profile is inferred from one paired RP/PDF
case, and checked on a second supplied sample. Each has nine beams and a
MU-weighted plan comparison at report precision.
It is not a claim to reproduce proprietary source code or every software version.

Implementation plan: analytic failing tests; bounded geometry and MU validation;
production service/registry/catalog integration; original-case comparison;
regression tests and independent review; commit and local merge into main.

Common geometry: standard Halcyon/Ethos MLCX1 28 x 10 mm and MLCX2 29 x 10 mm,
offset 5 mm, physical intersection represented by 56 x 5 mm slots. This version
requires un-clipped slots and tips inside jaws. Unsupported geometry, invalid MU
or an entirely closed beam makes the report metrics unavailable, with a warning.
No incomplete subset of treatment beams is reported as a plan result. Zero-MU
beams do not contribute; missing, negative or nonfinite treatment MU invalidates
the report profile. Raw cumulative weights are checked before normalization can
mask invalid signs: start zero, finite, nondecreasing, positive final weight.

Open means gap > 0.5 mm + 1e-8 mm numerical tolerance. This threshold is inferred,
not explicitly established as a universal manufacturer rule by the supplied guide.

- `ethos_sas10`: sum of counts(0.5 < gap <= 10 mm) over all CPs divided by sum
  of open counts. Every CP counted once, including endpoints; no CP MU weighting.
  The upper boundary also has 1e-8 mm tolerance. The second sample distinguishes
  the inclusive upper boundary: the strict <10 rule misses two beam rows and
  the plan row; <=10 matches both samples at displayed precision.
- `ethos_one_minus_mcs`: 1 minus centered-CP-MU mean(AAV * LSV).
  AAV uses only open area; its denominator is the per-slot bank-extrema envelope
  across CPs where that slot is open. For each bank LSV = 1 - sum of absolute
  differences between physically adjacent open slots / (number of such pairs *
  range of all open bank positions). The two bank scores multiply. Constant
  banks or no adjacent pairs score 1; an empty CP contributes zero MCS.
- `ethos_penumbra_ratio`: centered-CP-MU mean of the aperture fraction covered by
  the union of finite tip (2.8 mm) and exposed side (2.3 mm) strips. Closed CPs
  contribute zero. These distances are typical values in guide pp.121-123.
  Finite side strips must not be replaced by rectangular morphological erosion,
  which adds extra area at concave corners.

All three are dimensionless fractions; multiply SAS10 and PR by 100 to compare
with percentage reports. Plan aggregation uses beam MU. Generic metrics retain
their earlier names, formulas and values. Edge Penalty remains unresolved.

MCS residual investigation distinguished three issues: filtering closed slots
must not invent adjacency across gaps; the closure mask must also apply to CP
area and the envelope; the CP product must precede MU averaging. A rounded match
on these samples does not uniquely identify every implementation detail.

The second RP and PDF have differing plan labels (IM102 versus IM104); all nine
beam MUs agree at the PDF precision. Record it as a supplied cross-check with a
label caveat, rather than asserting that the underlying DICOM objects are identical.
