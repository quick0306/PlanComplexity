# Aurora Aperture Metrics Draft

This note defines a VMAT-like aperture-complexity subset for Aurora SVMAT research. The goal is not to replace the existing Aurora coupling metrics, but to add a geometry-focused metric family that describes how complex the effective field shape is at each evaluation unit.

## Scope

This draft covers five candidate Aurora aperture metrics:

- `mean_BA`
- `mean_BI`
- `mean_CA`
- `mean_SAS5` and `mean_SAS10`
- `mean_MCS_Aurora`

These metrics are intended as research descriptors of aperture shape complexity. They should be reported alongside the existing Aurora delivery-coupling metrics such as `projection_pitch_*`, `projection_mu_density_*`, and `mlc_z_coupling_*`.

## Notation

Let:

- `l = 1, 2, ..., L` index the leaf pairs
- `i = 1, 2, ..., N` index the Aurora evaluation units
- `alpha_i >= 0` be the weight assigned to evaluation unit `i`
- `x1(i,l)` and `x2(i,l)` be the two side positions used to form the effective opening for leaf pair `l`
- `g(i,l) = max(0, x2(i,l) - x1(i,l))` be the effective opening width for leaf pair `l`
- `h(l)` be the physical width of leaf pair `l`

Define the effective aperture for evaluation unit `i` as:

```text
Omega_i = union over open leaf pairs l of [b_(l-1), b_l] x [x1(i,l), x2(i,l)]
```

with:

```text
A_i = Area(Omega_i)
P_i = Perimeter(Omega_i)
```

For any per-unit quantity `Q_i`, define the weighted plan mean as:

```text
mean(Q) = sum_i alpha_i * Q_i / sum_i alpha_i
```

Recommended default weighting:

```text
alpha_i = delta w_i
```

where `delta w_i` is the cumulative meterset-weight increment over the corresponding Aurora interval. If absolute interval MU becomes available later, `delta MU_i` can replace `delta w_i`.

## Recommended Evaluation Unit

For Aurora, the preferred evaluation unit is the adjacent control-point interval, not the raw control point. This keeps the aperture metrics aligned with the current Aurora v2 and v3 interval-based metrics and with the natural weighting by `delta w_i`.

The effective aperture associated with interval `i` can be chosen as:

- the end-control-point aperture
- the midpoint surrogate between the two adjacent control points

For consistency with the current Aurora implementation style, the end-control-point aperture is the simplest first choice.

## Metric 1: Mean Beam Area

Per-unit beam area:

```text
BA_i = A_i
```

Weighted plan mean:

```text
mean_BA = sum_i alpha_i * BA_i / sum_i alpha_i
```

Physical meaning:

- measures the average effective field size
- smaller values generally indicate tighter modulation

## Metric 2: Mean Beam Irregularity

Following the Du 2014 plan-irregularity form:

```text
BI_i = P_i^2 / (4 * pi * A_i)
```

Weighted plan mean:

```text
mean_BI = sum_i alpha_i * BI_i / sum_i alpha_i
```

Physical meaning:

- equals its minimum for compact, regular shapes
- increases for elongated, jagged, or fragmented apertures

## Metric 3: Mean Circumference-to-Area Ratio

Per-unit ratio:

```text
CA_i = P_i / A_i
```

Weighted plan mean:

```text
mean_CA = sum_i alpha_i * CA_i / sum_i alpha_i
```

Physical meaning:

- describes how much boundary is needed per unit area
- is sensitive to narrow slots and fragmented openings

## Metric 4: Mean Small Aperture Score

For a gap threshold `t`, define the per-unit small-aperture score:

```text
SAS_t(i) =
    sum_l I(0 < g(i,l) < t) / sum_l I(g(i,l) > 0)
```

Weighted plan mean:

```text
mean_SAS_t = sum_i alpha_i * SAS_t(i) / sum_i alpha_i
```

Recommended reported thresholds:

```text
mean_SAS5
mean_SAS10
```

Physical meaning:

- quantifies how much of the effective field is carried by narrow openings
- is expected to be more directly connected to delivery difficulty than area alone

## Metric 5: Aurora-Adapted Modulation Complexity Score

This should be treated as an Aurora-adapted metric rather than a direct reuse of the original VMAT MCS definition.

First define the maximum effective opening for each leaf pair:

```text
g_max(l) = max_i g(i,l)
```

Define the area-variability term:

```text
AAV_i = sum_l g(i,l) / sum_l g_max(l)
```

Define a gap-sequence variability term using the effective gap profile:

```text
L_i = { l | g(i,l) > 0 }
n_i = |L_i|
```

If `n_i <= 1`, set:

```text
LSV_i = 1
```

Otherwise:

```text
g_i,max = max_l g(i,l)

LSV_i =
    1 - [ sum_(l=1 to n_i-1) |g(i,l+1) - g(i,l)| ] / [ (n_i - 1) * g_i,max ]
```

Then define the per-unit Aurora-adapted modulation complexity score:

```text
MCS_i = AAV_i * LSV_i
```

Weighted plan mean:

```text
mean_MCS_Aurora = sum_i alpha_i * MCS_i / sum_i alpha_i
```

Interpretation:

- higher `mean_MCS_Aurora` means smoother, less modulated aperture behavior
- lower `mean_MCS_Aurora` means more irregular and more strongly modulated aperture behavior

If a monotonic complexity-up score is preferred, define:

```text
MCS_complexity_Aurora = 1 - mean_MCS_Aurora
```

## Recommended Reporting Set

For a first Aurora aperture-complexity subset, report:

```text
mean_BA
mean_BI
mean_CA
mean_SAS5
mean_SAS10
mean_MCS_Aurora
```

If stronger emphasis on the effective-aperture interpretation is desired, the same quantities can be named:

```text
mean_BA_eff
mean_BI_eff
mean_CA_eff
mean_SAS5_eff
mean_SAS10_eff
mean_MCS_Aurora_eff
```

## Important Methodological Notes

### 1. These metrics depend on the effective-aperture definition

The main methodological decision is not the final formula, but how Aurora's dual-layer geometry is collapsed into an effective aperture `Omega_i`. The formulas above are only meaningful once that definition is fixed.

### 2. These metrics are geometry descriptors, not full delivery descriptors

They describe the complexity of the aperture shape, but not the full Aurora delivery problem. They should therefore be interpreted together with:

- `projection_pitch_*`
- `projection_mu_density_*`
- `projection_aperture_change_*`
- `projection_leaf_travel_*`
- `theta_z_coupling_*`
- `mlc_z_coupling_*`
- `reversal_*`
- regional and dual-layer coordination metrics

### 3. MCS should be labeled as adapted

The proposed `mean_MCS_Aurora` is structurally inspired by VMAT-style MCS, but its gap definition and weighting are Aurora-specific. It should therefore be labeled as an Aurora-adapted metric in research outputs.
