"""Auditable implementation contracts, not a claim of external validation.

Formula text has one owner: metric_definition_catalog. This module adds the
sampling and boundary conditions needed to interpret that text. The expanded
records are generated at runtime so new registry keys cannot silently inherit
an unspecified contract. Run this module to regenerate the human-readable table.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import re

from formula_versions import formula_version_for_mode
from ethos_report_metrics import ETHOS_REPORT_KEYS, ETHOS_REPORT_VERSION


CP_WEIGHTS = "Centered CP MU: w0=du0/2, wlast=du_last/2, wi=(du_prev+du_next)/2; u=BeamMU*CMW/lastCMW."
CP_MEAN = "Normalize centered CP MU within each beam, then beam-MU mean. " + CP_WEIGHTS
INTERVAL_MEAN = "Normalize du=u[i+1]-u[i] within each beam, then beam-MU mean. " + CP_WEIGHTS
FULL_MASK = "Positive jaw-clipped gap and positive Y-jaw overlap; per-device absolute IEC leaf boundaries reflected to internal Y; area uses exposed slot height."
RAW_MASK = "Positive raw right-left gap and positive Y-jaw overlap; X jaws do not clip the gap; each active pair has equal weight within its CP."
ENVELOPE = "E=sum_slot max(0,max_CP raw_right-min_CP raw_left)*max_CP exposed_height, over CPs where that slot is not outside jaws; this max-slot bank envelope is not a geometric union."
SLOT_MAX = "U=sum_slot max_CP(jaw-clipped slot area); maxima occur independently per slot; U is neither the bank envelope E nor a geometric union."
LSV_RANGE = "Each bank uses R=max(x)-min(x), not max adjacent difference; 1-sum(abs(diff(x)))/((n-1)*R); two bank scores multiply. Active indices are compressed before differences."
UNIFORM_FALLBACK = "No eligible observations => 0; missing/misaligned/nonfinite/negative or zero-total MU weights => uniform weights with a warning; nonfinite result => 0."
CORE_MISSING = "Zero total aggregation weight => 0; NaN observations contribute zero but retain their original weight in the denominator; absent required geometry may fail parsing."
TIMING = "Adjacent CPs; dt=max(abs(du)/(DoseRateSet/60),shortest_abs_dtheta/machine_max_speed) over available finite timing candidates; dose-rate setting comes from the beam; unavailable candidates yield NaN."
PRECISION = "Validation requests full_precision=True: retain floating-point calculation values and fractional prescription cGy. Compatibility default may truncate prescription cGy and round VMAT/CyberKnife to 2 digits, motion profiles to 4 and Halcyon paper values to 6; display rounding is not a formula tolerance."


@dataclass(frozen=True)
class MetricFormulaContract:
    platform: str
    metric_key: str
    formula: str
    sampling: str
    active_mask: str
    normalization: str
    unit: str
    aggregation: str
    missing_value: str
    representation: str
    formula_version: str
    source_anchors: tuple[str, ...]
    evidence_status: str = "implementation_contract"
    precision: str = PRECISION


def _vmat_base(key: str) -> tuple[str, str]:
    for suffix in ("_effective", "_stacked", "_mlcx1", "_mlcx2"):
        if key.endswith(suffix):
            return key[:-len(suffix)], suffix[1:]
    if key.startswith(("mlcx1_", "mlcx2_")):
        return key[6:], key[:5]
    if "_mlcx1_" in key or "_mlcx2_" in key:
        match = re.search(r"_(mlcx[12])_", key)
        return key.replace(match.group(0), "_"), match.group(1)
    return key, "native"


def _representation(layer: str) -> str:
    return {
        "native": "Native single-device apertures; dual-device base values are layer tuples before flattening; base MCSv is replaced by effective MCS5 when Halcyon paper metrics are available.",
        "mlcx1": "Native MLCX1 (distal for Halcyon), using its own DICOM boundaries and leaf count.",
        "mlcx2": "Native MLCX2 (proximal for Halcyon), using its own DICOM boundaries and leaf count.",
        "effective": "Halcyon aligned 5 mm slots, left=max(layer left), right=min(layer right); physical intersection; synthesized virtual leaves.",
        "stacked": "Native MLCX1 slots followed by native MLCX2 slots; nonphysical diagnostic sequence; LSV includes the artificial layer seam.",
    }[layer]


def _vmat(record) -> dict:
    key, layer = _vmat_base(record.metric_key)
    if key.startswith("ethos_"):
        normalizers = {
            'ethos_sas10': 'Pooled open-slot count over all CPs, each endpoint counted once; no CP MU weighting.',
            'ethos_one_minus_mcs': 'Open-slot bank-extrema envelope for AAV; each LSV bank uses all-open range, only physically adjacent open differences and their count. Constant bank/no adjacency=>1.',
            'ethos_penumbra_ratio': 'Open aperture area at each CP; union of finite tip 2.8 mm and exposed side 2.3 mm strips, with overlaps counted once.',
        }
        return dict(
            sampling="Every CP, including endpoints, once for pooled SAS counts; CP products for MCS and CP ratios for PR.",
            active_mask="Effective gap > 0.5 mm + 1e-8 mm; closure mask also used for area and envelope; physical adjacency is preserved.",
            normalization=normalizers[key],
            aggregation="Beam-MU mean; SAS has no CP weights; MCS and PR use " + CP_WEIGHTS,
            missing_value="Unsupported layout, clipped/nonfinite geometry, invalid cumulative MU, entirely closed beam or incomplete beam coverage => None plus warning; no subset aggregation. Empty CP contributes zero MCS and PR.",
            representation="Varian Ethos/Halcyon dual-layer MLC (legacy formula ID ethos-report-v1): physical 56 x 5 mm intersection, native 28/29 x 10 mm staggered layers; no jaw clipping. Two-sample display agreement with a second-sample plan-label caveat, not universal vendor validation.",
            source_anchors=("ethos_report_metrics.py:calculate_ethos_beam_metrics", "ethos_report_metrics.py:supported_beam_layout"),
            evidence_status="analytic_cases_checked",
        )
    result = dict(sampling="Each CP aperture.", active_mask=FULL_MASK,
                  normalization="No scale normalization; use the ratio, count, or physical quantity in the formula.",
                  aggregation=CP_MEAN, missing_value=CORE_MISSING,
                  representation=_representation(layer),
                  source_anchors=("vcomx_vmat_metrics.py:_summarize_aperture_series", "ApertureMetric/meterset_creator.py:MetersetsFromMetersetWeightsCreator"))
    prescription = {"mus", "pmu", "muca", "fraction_dose_gy", "fractions_count", "mucgy", "narcs", "al", "cal", "gt", "mudeg"}
    if key in prescription:
        result.update(sampling="Treatment beams with positive MU; plan prescription and stored beam GantryRotationAngle.",
                      active_mask="No leaf mask.", aggregation="Plan totals and ratios; N_control_arcs=sum_beams max(Ncp-1,0), not number of beams.",
                      normalization=record.mathematical_definition,
                      missing_value="Missing prescription/fractions => 0; zero denominator => 0; if fraction count is absent, rxdose is treated as fraction dose; no eligible beams => key omitted.")
    elif key in {"alg", "alg_sd", "mad", "sas_5mm", "sas_10mm", "sas_20mm", "nl", "nl_pairs", "nl_leaves"}:
        result.update(active_mask=RAW_MASK, missing_value=UNIFORM_FALLBACK,
                      source_anchors=("ComplexityMetric/aperture_series_metrics.py:active_leaf_pairs", "ComplexityMetric/aperture_series_metrics.py:weighted_gap_moments"))
        result["normalization"] = "Equal active-pair mean at each nonempty CP, then CP MU renormalized over nonempty CPs; no leaf-width weighting."
        if key in {"nl", "nl_pairs", "nl_leaves"}:
            result["normalization"] = "Count active pairs at every CP, including empty CPs as zero; physical-leaf count=2*pair count."
        if key == "alg_sd":
            result["normalization"] = "Population second moment: sqrt(sum_CP normalized_w*mean_pairs((gap-global_mean)^2)); equal mass per CP according to its MU, not pooled leaf counts."
            result["aggregation"] = "Native plan SD pools beam means/variances using beam MU. Effective/stacked SD is a beam-MU mean of beam SDs; these are distinct variants."
    elif key in {"mcsv", "aav", "lsv"}:
        result.update(sampling="Adjacent CP endpoints: AAV and LSV are each arithmetically averaged over endpoints; MCS multiplies these two means, not endpoint products or midpoint geometry.",
                      normalization=ENVELOPE + " " + LSV_RANGE, aggregation=INTERVAL_MEAN,
                      active_mask=FULL_MASK + " LSV uses raw bank positions of active clipped gaps; envelope uses raw extrema from jaw-overlapping slots.",
                      missing_value="Zero envelope => AAV 0; no active slots => LSV 0; constant/single-slot bank => LSV 1; fewer than two CPs => no interval score. Supplemental AAV/LSV use uniform MU fallback; core MCS uses " + CORE_MISSING,
                      source_anchors=("ComplexityMetric/aperture_shape_metrics.py:maximum_aperture_area", "ComplexityMetric/aperture_shape_metrics.py:leaf_sequence_variability", "ComplexityMetric/modulation_complexity_score.py:calculate_per_aperture"),
                      evidence_status="analytic_cases_checked")
    elif key in {"lt", "ltmu", "ltnlmu", "ltnl", "lna", "ltal", "lt_mean_leaf"}:
        result.update(sampling="Adjacent CP raw leaf-coordinate differences; shortest absolute gantry angle modulo 360.",
                      active_mask="LT includes a slot unless it is outside full jaws at both endpoints. LT Mean Leaf instead tests Y-jaw overlap only; no gap clipping of trajectories.",
                      normalization="D_i=sum_pairs(abs(delta_left)+abs(delta_right)); n_i=mean endpoint active PAIR counts (despite legacy 'leaf' labels). LT=mean_du(D); LTMU=sum(D)/beamMU; LTNL=mean_du(D/n); LTNLMU=sum(D/n)/beamMU; LTAL=mean_du(D/dtheta); LNA=mean_du(D/(n*dtheta)).",
                      aggregation=INTERVAL_MEAN, missing_value=UNIFORM_FALLBACK,
                      source_anchors=("vcomx_vmat_metrics.py:_leaf_travel", "ComplexityMetric/aperture_series_metrics.py:mean_leaf_travel"))
        if key == "lt_mean_leaf":
            result.update(normalization="Sum raw absolute trajectory increments for each physical leaf; average only leaves with positive total travel; no MU interval weighting.", aggregation="Beam-MU mean of beam moving-leaf means; no moving leaf => 0.")
    elif key in {"mdrv", "mgsv", "dr", "gs", "ls", "dt"}:
        result.update(sampling=TIMING, active_mask="All raw leaf coordinates for LS; no jaw or open-gap mask.",
                      normalization="DR=abs(du)/dt in MU/s; GS=shortest_abs_dtheta/dt; mDRV=finite mean(abs(deltaDR)/dtheta), mGSV=finite mean(abs(deltaGS)/dtheta); zero denominator contributes 0. LS averages nonzero finite speeds per leaf then leaves; dt=finite mean(dt)*Ncp, not sum of Ncp-1 intervals.",
                      aggregation="Within-beam finite arithmetic means (LS: mean over leaves); then beam-MU mean.",
                      missing_value="Missing cumulative MU or timing exception => all six outputs 0; nonfinite values filtered, empty finite set => 0. RTPLAN timing is an estimate, not a measured delivery trace.",
                      source_anchors=("vcomx_vmat_metrics.py:_timing_metrics", "ApertureMetric/mlc_attributes.py:MLCAttributes"))
    elif key.startswith("mi_"):
        result.update(sampling=TIMING + " Speed and absolute acceleration are pandas-differenced raw-coordinate traces.", active_mask="All raw leaves; no jaws; zero motion remains in the MI denominator.",
                      normalization="Per-leaf sample SD sigma_v,sigma_a (ddof=1); alpha_acc=1/mean(dt). MIs denominator=max(Ncp-1,1), MIa/MIt=max(Ncp-2,1), with SUM over leaves. Positive/zero scale=>infinity, zero/zero and NaN=>0. WGA=2/(1+exp(-gantry_acc/2)), WMU=2/(1+exp(-delta_DR/2)).",
                      aggregation="Beam-MU mean of each component. Base key is the ordered container (MIs,MIa,MIt); scalar suffixes export its components.",
                      missing_value="Missing motion becomes zero via nan_to_num in ratio construction; base container is not an additional scalar measurement.",
                      source_anchors=("ComplexityMetric/modulation_index_score.py:ModulationIndexTotal", "ApertureMetric/mlc_attributes.py:MLCAttributes"))
    elif key == "mlc_speed_acc" or key.startswith(("speed_", "acc_")):
        result.update(sampling=TIMING, active_mask="All raw leaves; finite values only. Proportion denominator includes finite speeds above 20 or accelerations above 200 even though no bin contains them.",
                      normalization="Per-leaf bins are [lo,hi), except final [16,20] mm/s and [160,200] mm/s^2 include upper edge. Summary means/SDs exclude zero motion; SD uses ddof=1. Base container holds ten bins plus four summaries.",
                      aggregation="Unweighted mean across usable leaves; plan uses max(Ncp-1,1), not MU, as beam weights.",
                      missing_value="No valid timing/motion => NaN, serialized as unavailable rather than a physical zero.",
                      source_anchors=("ComplexityMetric/proportion_mlc_speed_acceleration.py:ProportionMLCSpeedAcceleration", "ApertureMetric/mlc_attributes.py:MLCAttributes"))
    elif key in {"pa", "ja", "perimeter", "efs", "psmall", "pi", "pm", "md", "em", "bjar", "asr", "axjd", "ayjd", "cam", "eam", "tg", "sport"}:
        extra = {
            "pa": "A=sum_slot max(clipped_right-clipped_left,0)*Y-exposed height.",
            "ja": "J=max(X2-X1,0)*max(Y2-Y1,0); no MLC clipping.",
            "perimeter": "P=horizontal interval symmetric differences at slot boundaries plus 2*sum_positive_slots exposed height; zero-height jaw => 0.",
            "efs": "EFS=4*A/P; zero P=>0.", "psmall": "CP-MU proportion of EFS<30 mm, strictly; closed aperture has EFS=0 and is counted.",
            "pi": "P^2/(4*pi*A), with full union boundary P; zero A=>0.",
            "pm": SLOT_MAX + " Beam score=1-CP-MUmean(A)/U; no generic clipping in the native legacy class.",
            "md": SLOT_MAX + " Beam score=U/CP-MUmean(A); zero denominator=>0.",
            "em": "Horizontal boundary/A, with C1=0,C2=1; full P/(2*A) is a different named variant; zero A=>0.",
            "bjar": "A/(abs(X2-X1)*abs(Y2-Y1)); denominator is jaw rectangle, not maximum arc area.",
            "asr": "Count connected slot runs with clipped gap>0.5 mm; next row starts a component when raw intervals are disjoint or only touch.",
            "axjd": "abs(X2-X1), not clearance between aperture and jaw.", "ayjd": "abs(Y2-Y1), not clearance between aperture and jaw.",
            "cam": "1-mean_j(1-exp(-gap_j/10 mm))*(1-exp(-sqrt(A)/10 mm)); include all jaw-overlapping slots, even closed.",
            "eam": "10 mm*H/(A+5 mm*H), where H=sum exposed slot heights even for closed slots (legacy one-bank side-height helper).",
            "tg": "Concatenate abs adjacent raw-left and raw-right differences after removing outside-jaw slots; mean over these 2*(n-1) differences; closed gaps retained.",
            "sport": "At station s sum over t=s+-1..10 within beam, all raw leaves: abs(x_s-x_t)*abs(u_s-u_t)/shortest_angle(s,t); skip zero angle.",
        }
        result["normalization"] = extra[key]
        if key in {"pa", "ja", "perimeter", "efs", "psmall", "md", "tg"}:
            result["missing_value"] = UNIFORM_FALLBACK
        if key in {"bjar", "eam", "cam", "pm"}:
            result["missing_value"] += " Degenerate jaw/area denominator or empty CAM set is not uniformly guarded in the legacy class: may raise or yield NaN; this contract does not promise zero."
        if key in {"cam", "eam", "tg"}:
            result["active_mask"] = "Slots not outside full jaws, including zero-gap slots; geometry quantities and normalization above specify the additional masks."
        if key == "sport":
            result.update(active_mask="Every physical leaf position, including closed/outside-jaw leaves.", sampling="Each station and up to ten neighbors on each side within its beam.", missing_value="Missing or zero-total weights => nanmean; mismatched lengths truncated; empty observations => NaN.")
        result["source_anchors"] += ("ApertureMetric/aperture_geometry.py:PyAperture",)
        if key == "em":
            result["source_anchors"] += ("ComplexityMetric/edge_metric.py:EdgeMetric",)
        if key in {"em", "pi", "perimeter", "pa", "pm"}:
            result["evidence_status"] = "analytic_cases_checked"
    elif key in {"mcs5", "pa5", "pi5", "pm5", "eds", "mcsw", "paw", "piw", "pmw", "ul", "mcsul", "np", "mucp", "proximal_weight_mean", "distal_weight_mean"} or key.startswith(("proximal_", "distal_")):
        result.update(_halcyon(key))
    else:
        raise KeyError(f"No explicit VMAT contract family for {record.metric_key}")
    if layer in {"effective", "stacked"}:
        result["source_anchors"] += ("halcyon_dual_layer_metrics.py:_hybrid_representation_values",)
        result["missing_value"] += " Effective/stacked results require aligned dual-layer CPs and valid cumulative MU; unavailable beam is omitted."
        if key in {"mad", "alg", "alg_sd", "sas_5mm", "sas_10mm", "sas_20mm"}:
            result["missing_value"] = "Beam with no active pairs=>None and excluded from plan weights; all excluded=>plan0. Invalid CP weights may fall back to uniform with warning. Any detected cross-layer alignment failure marks all hybrid outputs None."
        if key == "lt":
            result["active_mask"] = "Raw bank increments for slots overlapping Y jaws at either endpoint; X jaws do not affect trajectory inclusion."
    return result


def _halcyon(key: str) -> dict:
    edges = "At each effective positive jaw-clipped gap assign its left/right limiting raw edge to the tighter layer; ties share 1/2 (math.isclose, abs_tol=1e-6 plus Python default relative tolerance). w_layer=limiting-edge score/(2*Nactive); u_layer excludes tied edges from this numerator."
    normalization = edges
    if "mcs" in key:
        normalization += " " + ENVELOPE + " " + LSV_RANGE + " Let t_layer=mean_endpoint(A/E)*mean_endpoint(LSV). Layer MCSw=sum_norm_du t_layer*mean_endpoint(w_layer); MCSUL additionally multiplies mean_endpoint(u_layer). Unweighted MCS uses t_layer alone."
    elif "pm" in key:
        normalization += " " + SLOT_MAX + " Layer PMw=sum_norm_CP_MU (1-A_layer/U_layer)*w_layer; PM5/native PM omit w. Combined PMw clipped to [0,1]; components floored at zero."
    elif "pa" in key or "pi" in key:
        normalization += " Per-CP PA=A; PI=P^2/(4*pi*A) with full P and zero-area score 0. Weighted layer contribution multiplies w_layer before CP-MU aggregation."
    elif key == "np":
        normalization = "Count scipy.signal.find_peaks on each raw leaf trajectory with range>1e-6 mm; arithmetic mean over moving leaves. If scipy unavailable, strict immediate-neighbor local maxima fallback (plateaus can differ)."
    elif key == "mucp":
        normalization = "100*mean(du)/beamMU; no leaf dependence."
    return dict(sampling="Adjacent endpoint means for all MCS terms; individual CPs for PA/PI/PM, edge contributions and uncovered fractions; complete trajectories for NP.",
                active_mask=FULL_MASK + " Weight/uncovered scores count two edges per active effective slot equally, not weighted by leaf width.",
                normalization=normalization, aggregation="Normalize interval MU for MCS; centered CP MU for CP terms; beam-MU mean. Proximal/distal weighted component sums give the total, without renormalizing each layer's contribution.",
                missing_value="Requires aligned MLCX1/MLCX2, >=2 CPs and valid cumulative MU; missing beam omitted. No effective openings: w1=w2=0.5,u1=u2=0. No moving leaves=>NP0; zero normalization weights=>all-zero weights; zero A/E/U guarded as 0.",
                representation="MLCX2 proximal, MLCX1 distal; native boundaries for layer metrics; synthesized 5 mm physical intersection for *5; weighted scores combine native metrics using effective edge counts.",
                source_anchors=("halcyon_dual_layer_metrics.py:_calculate_beam_paper_metrics", "halcyon_dual_layer_metrics.py:_layer_contributions", "halcyon_dual_layer_metrics.py:_weighted_mcs"),
                evidence_status="research_variant_pending_review")


def _tomo(record) -> dict:
    key = record.metric_key
    result = dict(sampling="All retained sinogram projections and leaf columns; parser terminal-row policy is recorded in input metadata.",
                  active_mask="S>0 is open; S is fractional opening in [0,1], LOT_ms=S*projection_time_s*1000.",
                  normalization="No leaf-width multiplication: sinogram geometry uses column indices, not millimetres.",
                  aggregation="Plan-level sinogram calculation; no VMAT CP-MU or beam-MU weighting.",
                  missing_value="Empty eligible observation set => 0 unless a specific denominator rule below states otherwise.",
                  representation="Fractional sinogram; physical planned motion comes from the parser's recorded source/fallback, not a delivery log.",
                  source_anchors=("tomo_metrics.py:calculate_tomo_metrics", "tomo_parser.py:parse_tomo_rtplan"),
                  precision="Floating-point metrics are unrounded; mode deliberately groups values rounded to six decimal places.")
    delivery = {"mf", "nproj_rot", "nproj", "nrot", "projection_time_s", "gantry_period_s", "treatment_time_s", "field_width_mm", "pitch", "couch_translation_mm", "couch_speed_mm_s", "target_length_mm", "ttdf_s_cgy"}
    if key in delivery:
        result["normalization"] = record.mathematical_definition + "; projection count includes exactly the rows retained by the parser."
        result["active_mask"] = "MF uses only S>0; other delivery quantities use plan metadata and all retained rows."
        result["missing_value"] = "Undefined safe ratios => 0. Unavailable planned couch motion/pitch/target length may remain NaN and serialize as unavailable; target length must be finite and nonnegative. Parser may explicitly assume 20 ms projection time or 10 mm field width; metadata distinguishes these assumptions from observations."
        if key == "mf":
            result["normalization"] += " This mean/max ratio is the reciprocal of the commonly named max/mean modulation factor; same name does not establish equivalence."
        if key == "couch_speed_mm_s":
            result["normalization"] = "Explicit planned couch speed when parsed; otherwise planned translation/TT; unavailable value stays NaN."
    elif key in {"mlot", "sdlot", "mdlot", "molot", "maxlot", "minlot", "klot", "slot", "mflot", "sdflot", "mdflot", "moflot", "maxflot", "minflot"} or key.startswith(("clns_", "cfns_")):
        result.update(sampling="Flatten S in row-major order; select strictly positive cells.",
                      normalization="LOT statistics use milliseconds; FLOT uses fractions. SD is sample SD (ddof=1). Mode rounds to 6 decimals and uses first encountered value on ties. Kurtosis is scipy Fisher excess, bias=False; skewness bias=False. Thresholds are strict (< for short LOT/FLOT, > for near-projection-time LOT).",
                      aggregation="One observation per positive cell; no projection balancing or MU weighting.",
                      missing_value="Empty set => 0; SD with <=1 sample =>0; nonfinite kurtosis/skewness =>0.", source_anchors=("tomo_metrics.py:_lot_statistics", "tomo_metrics.py:_flot_statistics"))
    elif key in {"ta", "ncc", "lengthcc", "fdisc", "cls", "clsin", "clsinarea", "clsindisc", "clsinareadisc", "centroid", "l0ns", "l1ns", "l2ns"}:
        normalizers = {
            "ta": "Per row span=last_open_index-first_open_index+1, or0; mean over all rows.",
            "ncc": "Count contiguous runs of S>0 per row; mean over all rows.",
            "lengthcc": "Mean length over all contiguous open runs pooled across rows; each run weighted equally.",
            "fdisc": "Count rows with >1 run / total row count.",
            "cls": "Mean_rows((Nleaves-count_open)/Nleaves), including fully closed rows.",
            "clsin": "Mean_nonempty_rows((span-count_open)/Nleaves).",
            "clsinarea": "Mean_nonempty_rows((span-count_open)/span).",
            "clsindisc": "Mean_rows_with_multiple_runs((span-count_open)/Nleaves).",
            "clsinareadisc": "Mean_rows_with_multiple_runs((span-count_open)/span).",
            "centroid": "Mean_nonempty_rows(mean_open_indices(j-(Nleaves-1)/2)); binary openings, not FLOT weights.",
            "l0ns": "Mean_nonempty_rows(count open cells having 0 open immediate left/right neighbors / count_open); outside array closed.",
            "l1ns": "Mean_nonempty_rows(count open cells having 1 open immediate left/right neighbor / count_open); outside array closed.",
            "l2ns": "Mean_nonempty_rows(count open cells having 2 open immediate left/right neighbors / count_open); outside array closed.",
        }
        result.update(normalization=normalizers[key], source_anchors=("tomo_metrics.py:_geometry_metrics",))
    else:
        normalizers = {
            "lotv": "Mean_columns(sum_i(max_column S-abs(S[i+1]-S[i]))/((Nproj-1)*max_column S)); identically closed column contributes1.",
            "elotv_1": "Mean_columns(sum_i abs(S[i+1]-S[i])/((Nproj-1)*max_column S)); closed column0, Nproj<=1=>0.",
            "elotv_5": "Mean_columns(sum_i abs(S[i+5]-S[i])/((Nproj-5)*max_column S)); closed column0, Nproj<=5=>0.",
            "pstv": "EPSTV(1,1): mean over i<Nproj-1,j<Nleaves-1 of abs(S[i+1,j]-S[i,j])+abs(S[i,j+1]-S[i,j]).",
            "epstv_1_1": "Mean over i<Nproj-1,j<Nleaves-1 of abs(S[i+1,j]-S[i,j])+abs(S[i,j+1]-S[i,j]).",
            "epstv_1_0": "Mean over i<Nproj-1,all j of abs(S[i+1,j]-S[i,j]).",
            "epstv_0_1": "Mean over all i,j<Nleaves-1 of abs(S[i,j+1]-S[i,j]).",
            "mi": "Sample SD of positive S; four absolute difference arrays (row,column,two diagonals). For f=linspace(0,2,201), mean of four directional fractions(diff>f*SD); trapezoidal integral over f. Empty direction contributes0.",
            "noc": "For each column merge touching positive intervals [i+0.5-S/2,i+0.5+S/2], then2*merged_count/Nproj; mean over ALL columns.",
            "msa": "Intensity-weighted centered index: sum_j((j-(Nleaves-1)/2)*mean_rows(S[:,j]))/sum_j mean_rows(S[:,j]).",
            "msi": "Mean over all columns of mean_rows S[:,j].", "mdsi": "Median over all columns of mean_rows S[:,j].",
            "sdsi": "Sample SD (ddof=1) over all columns of mean_rows S[:,j].",
        }
        result.update(normalization=normalizers[key], active_mask="All S cells, including zeros; MI scale only uses positive cells; NOC constructs intervals only for positive cells.",
                      missing_value="Empty arrays/zero denominator=>0, except LOTV with one projection and nonzero column has an unguarded zero denominator and can yield NaN. MI zero SD=>0; closed-column LOTV=1.",
                      source_anchors=("tomo_metrics.py:_modulation_metrics",))
    return result


def _cyberknife(record) -> dict:
    key = record.metric_key
    normalization = {
        "mcs": "Per segment (A/E)*LSV; E computed across all beams sharing XML interval_key. " + ENVELOPE + " " + LSV_RANGE,
        "pm": "For each beam 1-sum_segment(mu*A)/(beamMU*E_interval); then beamMU/planMU weighted sum. " + ENVELOPE,
        "em": "Per segment horizontal leaf-side boundary/A (C1=0,C2=1); zero A=>0; not fullP/(2*A).",
        "pi": "Per segment fullP^2/(4*pi*A); zero A=>0.",
        "lg": "Equal-pair mean of jaw-clipped positive opposing gaps within each segment; no width weighting.",
        "sas10": "Pooled count of jaw-clipped positive gaps<10 mm / pooled count of positive gaps across every segment; no MU weighting or per-segment balancing.",
    }[key]
    fallback = {
        "mcs": "With standard RTPLAN MLC geometry and no XML segment model, helper fallback is VMAT MCS: mean_du(mean_endpoint(A/E_beam)*mean_endpoint(LSV)), then beam-MU mean.",
        "pm": "Standard-MLC fallback instead uses native VMAT PM:1-CP-MUmean(A)/sum_slot max_CP(slot area), then beam-MU mean; its denominator differs from the XML path.",
        "em": "Standard-MLC fallback uses the same per-aperture horizontal/A ratio with centered CP-MU and beam-MU means.",
        "pi": "Standard-MLC fallback uses the same per-aperture fullP^2/(4*pi*A) with centered CP-MU and beam-MU means.",
        "lg": "Standard-MLC fallback uses VMAT ALG: raw positive gaps selected by Y-jaw overlap, equal-pair mean per nonempty CP, then centered CP-MU and beam-MU means.",
        "sas10": "Standard-MLC fallback uses VMAT SAS10: fraction of raw Y-jaw-active positive gaps<10 at each nonempty CP, then centered CP-MU and beam-MU means; not the pooled XML-segment ratio.",
    }[key]
    normalization += " " + fallback
    return dict(sampling="Delivered MLC segment apertures; XML interval_key groups the envelope; no endpoint interpolation.", active_mask=FULL_MASK,
                normalization=normalization, aggregation="Segment-MU/planMU sum for MCS,EM,PI,LG; beam-MU/planMU sum for PM; unweighted pooled-pair ratio for SAS10.",
                missing_value="PlanMU<=0 => all six0; no open gaps=>LG/SAS0; E<=0=>AAV0 and beam PM skipped; incomplete XML association limits the represented subset.",
                representation="XML-associated CyberKnife MLC segments are the primary path; standard RTPLAN MLC geometry uses the explicitly described VMAT helper fallback. These paths must not be assumed numerically equivalent.",
                source_anchors=("cyberknife_metrics.py:calculate_cyberknife_metrics", "cyberknife_metrics.py:_build_union_area", "analysis_helpers.py:calculate_cyberknife_mlc_metrics"))


def _aurora(record) -> dict:
    key = record.metric_key
    result = dict(sampling="Adjacent CPs within each beam only; shortest signed gantry unwrap then absolute dtheta; axial dz=abs(delta z). Plan intervals are pooled, never joined across beams.",
                  active_mask="No jaw/leaf-width clipping; W=sum_zip max(x2-x1,0) is an opening-WIDTH proxy, not area or a verified physical dual-layer intersection; leaf travel sums raw coordinate changes over the paired available entries.",
                  normalization="Pitch_i=dz/dtheta for dtheta>0; density_i=abs(deltaCMW)/dz, aperture_change_i=abs(deltaW)/dz, travel_i=sum(abs(delta leaf))/dz for dz>0. CV=population_SD/abs(mean); each retained interval equal weight.",
                  aggregation="Pool valid within-beam interval observations; ordinary mean, population CV, maximum, nearest-rank ceil(0.95*N), or mean of largest min(3,N), as named in the formula.",
                  missing_value="Empty valid samples or undefined ratio=>None; one-value or all-zero CV=>0; no artificial zero is substituted for unavailable motion.",
                  representation="Aurora research proxies; MLCX1/MLCX2 channels are not silently mapped to Halcyon effective geometry.",
                  source_anchors=("aurora_svmat_lab/metrics.py:calculate_plan_metrics", "aurora_svmat_lab/metrics.py:_iter_interval_motion"),
                  evidence_status="research_variant_pending_review", precision="Unrounded Python floating-point values; None remains unavailable.")
    if key.startswith(("head_", "mid_", "tail_")):
        result["sampling"] += " Assign interval midpoint z to thirds of the global midpoint span: normalized<1/3 head,<2/3 mid,otherwise tail; zero span=>mid."
    elif key in {"small_opening_fraction", "near_closed_fraction", "effective_small_gap_burden"}:
        result.update(sampling="Next endpoint of each within-beam CP interval, zipped MLCX1/MLCX2 entries.", active_mask="gap=max(x2-x1,0)>0; no jaws; these are research proxy openings.",
                      normalization="Weight each eligible pair by abs(deltaCMW); zero increment falls back to1. Fraction uses strict gap<10 or<2 mm; severity=max(0,1-gap/10 mm).",
                      aggregation="Pool pair samples and weights across all within-beam intervals.", missing_value="No positive-gap samples with positive weight=>0.")
    elif key in {"reversal_symmetry_index", "forward_backward_metric_difference", "beam_pair_balance_index"}:
        result.update(sampling="Group beams by sign(z_last-z_first); abs(net motion)<=1e-9 excluded.",
                      normalization="Symmetry averages four family comparisons (mean MU-density proxy, aperture change, leaf travel, pitch):1-abs(f-b)/(abs(f)+abs(b)), both zero=>1. Difference compares mean coupled index; balance compares sums of coupled index.",
                      aggregation="Equal beam means within direction; equal available-family means for symmetry; no MU weights.", missing_value="Either direction absent=>None; missing family excluded; no usable family=>None; zero total coupled load=>balance None.")
    elif key in {"layer_imbalance_index", "layer_correlation_index", "x1_x2_aperture_disparity", "x1_x2_leaf_travel_ratio"}:
        result["normalization"] += " Imbalance=abs(mean1-mean2)/(abs(mean1)+abs(mean2)); ratio=mean1/mean2. Correlation uses population Pearson; single/constant sequences return1 if pairwise equal within abs_tol1e-12, else0. Aperture disparity compares sum(abs(position)) of each channel at each CP, skips zero total."
    elif key == "coupled_modulation_index":
        result["normalization"] = "For available (aperture_change_per_mm,leaf_travel_per_mm,MU-density CV,pitch CV), apply x/(1+x), then equal-component mean; unavailable components excluded."
    elif key in {"longitudinal_travel_mm", "axial_travel_mm", "total_rotation_deg", "gantry_rotation_deg", "rotations", "travel_per_rotation_mm", "mm_per_deg", "mm_per_rotation", "mu_per_mm", "aperture_change_per_mm", "leaf_travel_per_mm"}:
        result["aggregation"] = "Sum within-beam distances first; form plan ratio of sums, not mean of interval ratios. Aperture/leaf change ratios retain only dz>0 intervals."
        result["normalization"] += " Explicit beam MU is used for MU/mm; absent MU falls back to cumulative-weight span, so proxy values must not be compared as absolute MU/mm."
    return result


def build_metric_formula_contracts() -> list[MetricFormulaContract]:
    from metric_definition_catalog import build_metric_definition_catalog
    builders = {"VMAT_IMRT": _vmat, "TOMO": _tomo, "CYBERKNIFE_MLC": _cyberknife, "AURORA": _aurora}
    contracts = []
    for record in build_metric_definition_catalog():
        fields = builders[record.platform](record)
        contracts.append(MetricFormulaContract(
            platform=record.platform, metric_key=record.metric_key,
            formula=record.mathematical_definition, unit=record.unit,
            formula_version=(ETHOS_REPORT_VERSION if record.metric_key in ETHOS_REPORT_KEYS else
                             formula_version_for_mode(record.platform) or "aurora-unversioned-research-v2-v3-legacy"),
            **fields,
        ))
    return contracts


def export_metric_formula_contracts(path: str | Path) -> None:
    """Optional machine-readable export; generated from the canonical catalog."""
    Path(path).write_text(json.dumps([asdict(c) for c in build_metric_formula_contracts()], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_contract_document(path: str | Path) -> None:
    contracts = build_metric_formula_contracts()
    lines = ["# Metric formula contracts", "", "Generated by `python -m metric_formula_contracts`; edit the catalog and contract builders, then regenerate. This inventory documents current implementation semantics. It does not certify agreement with all source papers or external software.", "",
             "`implementation_contract` means source traced; `analytic_cases_checked` means the named formula family has discriminating synthetic examples, not every machine/layer combination; `research_variant_pending_review` means literature/physical interpretation still needs independent review. No row claims external validation.", "",
             "Counts include container keys (four MI triplets and the motion-profile container), scalar components, native layers and research variants; they are not counts of independently validated scalar metrics. Formula versions come from `formula_versions.py`. Aurora remains explicitly unversioned research code.", "",
             "Precision: validation requests full precision; legacy default output rounding remains for compatibility. Floating-point error tolerances are separate from display precision. See each row for missing values and fallback rules.", "",
             "Compatibility in geometry-v4: BJAR, AXJD, AYJD, JA and SPORT dual-layer tuples flatten as `_mlcx1`/`_mlcx2`, replacing incidental `_1`/`_2` names. JA now has a catalog entry. NumPy MI triplets must flatten to `_mis`, `_mia`, `_mit` scalar components, including native-layer names; an array is a container, not a scalar metric.", "",
             "Discriminating examples: disjoint 2x1 slots at [0,2] and [4,6] have geometric union4, AAV bank envelope6 and PM max-slot area2. Bank [0,1,2] yields range-normalized LSV0.5 versus max-adjacent-difference variant0. A20x5 rectangle gives EM0.4/mm versus fullP/(2A)=0.25/mm. Endpoint MCS multiplies the two endpoint means; it differs from both mean endpoint products and midpoint geometry. These cases are executable in `tests/test_metric_formula_contracts.py`.", ""]
    for platform in ("VMAT_IMRT", "TOMO", "CYBERKNIFE_MLC", "AURORA"):
        selected = [c for c in contracts if c.platform == platform]
        lines += [f"## {platform} ({len(selected)} records)", "", "| Key | Formula / normalization | Sampling / mask / representation | Units / aggregation / missing | Version / evidence / source |", "|---|---|---|---|---|"]
        for c in selected:
            cells = [c.metric_key, c.formula + "<br>" + c.normalization, c.sampling + "<br>" + c.active_mask + "<br>" + c.representation, c.unit + "<br>" + c.aggregation + "<br>" + c.missing_value, c.formula_version + "<br>" + c.evidence_status + "<br>" + "; ".join(c.source_anchors)]
            lines.append("| " + " | ".join(s.replace("|", "&#124;").replace("\n", " ") for s in cells) + " |")
        lines.append("")
    Path(path).write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    write_contract_document(Path(__file__).parent / "docs" / "metric_formula_contracts.md")
