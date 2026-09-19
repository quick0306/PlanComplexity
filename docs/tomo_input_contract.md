# TOMO input contract (`tomo-v3`)

The parser reads the selected treatment beam's `ControlPointSequence` from the
existing RT Plan entrypoint. Its output sinogram contains dimensionless leaf
open fractions. Recognizing a standard leaf-duration attribute here does not
claim support for the complete second-generation RT Radiation IOD.

## Units and source identity

| Input | Meaning | Validation and conversion |
| --- | --- | --- |
| `TomotherapeuticLeafOpenDurations` `(3010,0099)` | Seconds of leaf opening during a control-point interval | Divide by a known positive projection duration in seconds; subsecond values are still seconds. |
| `(300D,10A7)` with creator `(300D,0010) = TOMO_HA_01` in its control-point item | Fraction of projection time for each of 64 leaves | Require 64 finite values in `[0,1]`; retain values without rescaling. |
| Beam `(300D,1040)` with the same creator in the beam item | Gantry rotation period in seconds | Divide by inferred projections per rotation. |
| Beam `(300D,1080)` with the same creator | Planned couch speed in mm/s | Multiply by the retained projection count and known projection duration for supported helical motion. |
| Beam `(300D,1060)` with the same creator | Helical couch advance per rotation divided by maximum Y opening | Read the nominal pitch, or derive it only from independently known helical motion and width. |
| Beam `(300D,10A4)` with the same creator | `HELICAL` or `FIXED_ANGLE` geometry | Fixed-angle delivery is explicitly unsupported by this helical reader. |

The standard's unit definition is explicit in [DICOM PS3.3 2026c,
C.36.17](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.36.17.html).
The private profile is specified in Accuray's [1064007 Rev. A, page
82](https://www.accuray.com/wp-content/uploads/10640071.pdf) and [1066787 Rev. A,
page 83](https://www.accuray.com/wp-content/uploads/1066787.pdf). These vendor
definitions were retrieved from indexed official-domain excerpts on
2026-09-19; direct PDF retrieval returned HTTP 404. The local UCoMX manual also
defines its sinogram as fractional leaf open times in `[0,1]`, but that alone
would not establish the meaning of a private DICOM element.

Units are never inferred from magnitude. Unknown or missing private sinogram creators,
mixed standard/private sources, inconsistent leaf counts, negative or nonfinite
values, malformed numeric strings, and fractions outside `[0,1]` cause a
`ValueError`. Values are not clipped to hide invalid durations.

## Empty projections and timing

The Accuray profile permits no sinogram value for an all-closed projection and
for the terminal control point. Empty or absent private rows are represented by
64 zeros, preserving interior closed projections. Exactly one final all-zero
placeholder is removed. A small positive final row is retained; no approximate
zero threshold is used. Standard rows may have an absent final placeholder;
missing interior standard rows are unsupported because this reader does not
implement duration inheritance.

Standard durations require known projection timing to obtain fractions. For
already-fractional private rows, the existing 0.02-second research assumption is
retained only when timing is unavailable, with an explicit warning. The existing
10-mm field-width fallback remains warned, but neither assumption is used to
derive physical motion, pitch, or target length. The former 0.287 pitch default
has been removed. These assumptions limit timing/geometry metrics; parsing does
not validate machine delivery.

## Planned couch motion

For recognized native helical input:

`translation_mm = couch_speed_mm_per_s * retained_projections * projection_time_s`.

Closed interior projections contribute to duration; the terminal placeholder
does not. The [pinned TCoMX Hi-Art reader](https://github.com/SamueleCavinato/TCoMX/blob/ac8f28e4068fac0c883bd409dd8cc464593ea351/libs/01_read-input/TCoMX_read_RTplan.m#L209-L222)
provides an independently inspected implementation of this physical relation.
No upstream source was copied into this implementation.

Older native exports can omit the geometry enum. Only `TOMO_HA_01` input with a
positive private helical pitch, positive private gantry period, and a regular,
nonzero, monotonic gantry-angle sequence is inferred to be helical. Wraparound
is removed before checking rotation. Missing angles inherit their previous
state; unchanged inherited intervals do not establish regular rotation. The
inference is recorded in metadata and a warning. An explicitly unknown enum or
`FIXED_ANGLE` is never overwritten by this inference. Other missing geometry
remains unknown, disabling helical extrapolation and target-length calculation.

An explicit standard `TableTopLongitudinalPosition` trajectory can independently
supply absolute translation and mean speed. Absent control-point attributes
inherit the prior value; an explicitly empty or nonfinite value is unknown.
All retained intervals need known endpoints and a monotonic trajectory.
Unknown or reversing trajectories are unavailable, rather than being treated
as zero travel. Genuine stationary positions and declared zero speed/pitch
remain zero.

Pitch can supply translation from known rotation count and nominal width when
speed is missing. Conversely, known translation and rotations can supply pitch.
The nominal width is the maximum inherited Y jaw opening across control points,
so an initially narrow dynamic jaw does not create a false pitch conflict.
Neither a default width nor rotation timing obtained from a guessed projection
count is used in these derivations.

Independently supplied standard positions, private speed, and private pitch must
agree on translation within relative tolerance `1e-4` plus absolute tolerance
`0.001 mm`, allowing decimal field precision. Conflicts or an explicitly invalid
private motion value make motion, pitch, and target length unavailable with a
warning; they are not silently replaced from another source. Unknown beam
private creators are ignored with a warning while valid standard positions
remain usable. Missing motion or pitch is represented by NaN.

`target_length_mm` retains the defined nominal helical proxy
`translation_mm - field_width_mm` only when both quantities are known and the
result is nonnegative. It is unavailable for unknown geometry, insufficient
travel, or an assumed width. It is not an anatomical target measurement or a
reconstruction of delivered motion.

Metadata records `tomo_plan_geometry`, `tomo_geometry_source`,
`couch_speed_source`, `couch_translation_source`, `pitch_source`,
`field_width_source`, and `target_length_source` so declared, derived, inferred,
and unavailable quantities remain distinguishable.

## Dose per fraction

A single fraction group with a positive integer `NumberOfFractionsPlanned` is
required. A unique positive target prescription is converted as
`dose_cGy_per_fraction = 100 * TargetPrescriptionDose_Gy / fractions`; for
example, 60 Gy over 30 fractions gives 200 cGy per fraction. Multiple differing
prescription levels are ambiguous without selecting a target and return NaN.

When no target prescription is supplied, complete nonnegative `BeamDose`
values in the sole group are summed in Gy per fraction and multiplied by 100;
they are not divided by the fraction count again. Missing or zero total dose,
invalid values, incomplete beam-dose data, and missing/multiple fraction groups
return NaN with a parser warning. Consequently `ttdf_s_cgy` is unavailable
instead of reporting a fabricated zero. Dose quantities and the per-fraction
meaning of `BeamDose` are specified in [DICOM C.8.8.10](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.8.10.html)
and [C.8.8.13](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.8.8.13.html).

## Verification record

Synthetic DICOM tests establish seconds-to-fractions conversion, 64-leaf private
fractions, terminal and interior closed projections, malformed/ambiguous input
rejection, gantry-period conversion, and the 60 Gy / 30 fraction hand case.
Motion cases independently verify millimeters per second, retained interval
counting, standard position inheritance, zeros, missing or invalid fields,
geometry inference, fixed-angle rejection, dynamic-jaw width, and conflicting
sources. End-to-end service cases verify available metrics, unavailable values,
and actionable unsupported results.

A bounded read-only local compatibility check covered 24 RT Plan objects using
`TOMO_HA_01`, Hi-Art software 5.0.2 or 5.1.3. All parsed as 64-leaf fractional
sinograms using the documented private gantry period. Thirteen contained empty
private rows. All had unavailable dose: 23 had zero `BeamDose`, one omitted it,
and none supplied a target prescription. Only aggregate technical results were
recorded; no source objects were modified. This is compatibility evidence, not
an independent validation of every derived metric or a clinical claim.

The native motion check reproduced 223.17343239215685 mm and 98.4505202 mm for
the two reference aliases, using speeds 0.610483 and 0.238533 mm/s. Their nominal
target-length proxies are 198.07343239215686 and 73.3505202 mm. All 24 inputs
omit the explicit geometry enum and therefore retain an inference warning.
