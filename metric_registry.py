from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Tuple

from aurora_svmat_lab.notes import get_metric_notes


SUPPORTED_VALIDATION_DOMAINS = (
    "VMAT_IMRT",
    "TOMO",
    "CYBERKNIFE_MLC",
    "AURORA",
)


@dataclass(frozen=True)
class MetricSpec:
    key: str
    label: str
    doi: str = ""
    dual_mlc: bool = False
    aliases: Tuple[str, ...] = field(default_factory=tuple)
    gui_label: str = ""
    description: str = ""


VMAT_METRIC_SPECS = (
    MetricSpec("mus", "MUs", "10.1118/1.4861821", description="Total monitor units delivered by the plan."),
    MetricSpec("pmu", "PMU", "10.1118/1.4861821", description="Monitor units normalized to a standard 2 Gy fraction."),
    MetricSpec("muca", "MUCA", description="Average monitor units delivered per control arc."),
    MetricSpec("fraction_dose_gy", "Prescribed Dose", description="Dose prescribed per fraction."),
    MetricSpec("fractions_count", "Fractions", description="Number of planned treatment fractions."),
    MetricSpec("mucgy", "MUcGy", "10.1118/1.4861821", description="Monitor units delivered per centigray of prescribed dose."),
    MetricSpec("lt", "LT", "10.1118/1.4810969", dual_mlc=True, aliases=("leaf_travel",), description="Average total leaf travel across a control arc."),
    MetricSpec("ltmu", "LTMU", dual_mlc=True, description="Leaf travel normalized by delivered monitor units."),
    MetricSpec("ltnlmu", "LTNLMU", dual_mlc=True, description="Leaf travel per involved leaf, normalized by monitor units."),
    MetricSpec("nl", "NL", dual_mlc=True, description="Average number of leaves actively shaping the aperture."),
    MetricSpec("ltnl", "LTNL", dual_mlc=True, description="Leaf travel normalized by the number of involved leaves."),
    MetricSpec("al", "AL", description="Average arc length delivered per beam."),
    MetricSpec("lna", "LNA", dual_mlc=True, description="Leaf travel per involved leaf and per unit gantry travel."),
    MetricSpec("cal", "CAL", description="Average control-arc length between successive control points."),
    MetricSpec("gt", "GT", description="Total gantry travel delivered by the plan."),
    MetricSpec("mudeg", "MUdeg", "10.4236/ijmpcero.2014.32013", description="Monitor units delivered per degree of gantry rotation."),
    MetricSpec("ltal", "LTAL", dual_mlc=True, description="Leaf travel normalized by unit gantry angle."),
    MetricSpec("narcs", "NArcs", description="Number of treatment arcs or beams contributing to the plan."),
    MetricSpec("mdrv", "mDRV", "10.1186/1748-717X-2-42", dual_mlc=True, description="Mean variation of dose rate during delivery."),
    MetricSpec("mgsv", "mGSV", "10.1186/1748-717X-2-42", dual_mlc=True, description="Mean variation of gantry speed during delivery."),
    MetricSpec("dr", "DR", dual_mlc=True, description="Average dose rate used during delivery."),
    MetricSpec("gs", "GS", dual_mlc=True, description="Average gantry speed during arc delivery."),
    MetricSpec("ls", "LS", dual_mlc=True, description="Average leaf speed during delivery."),
    MetricSpec("mcsv", "MCSv", "10.1118/1.4810969", dual_mlc=True, aliases=("modulation_complexity_score",), description="Overall aperture modulation score combining area and leaf sequence variability. For Halcyon/Ethos dual-layer plans this is also reported on the synthesized effective aperture used by Quintero et al. 2021."),
    MetricSpec("aav", "AAV", "10.1118/1.3276775", dual_mlc=True, description="Variability of aperture area across control points."),
    MetricSpec("lsv", "LSV", "10.1118/1.3276775", dual_mlc=True, description="Variability of the leaf sequence pattern across the aperture."),
    MetricSpec("tg", "TG", "10.1120/jacmp.v16i4.5321", dual_mlc=True, description="Average tongue-and-groove offset between neighboring leaves."),
    MetricSpec("mi_0_2", "MI(0.2)", dual_mlc=True, description="Modulation index using a 0.2 threshold factor."),
    MetricSpec("mi_0_5", "MI(0.5)", dual_mlc=True, description="Modulation index using a 0.5 threshold factor."),
    MetricSpec("mi_1_0", "MI(1.0)", dual_mlc=True, description="Modulation index using a 1.0 threshold factor."),
    MetricSpec("mi_2_0", "MI(2.0)", dual_mlc=True, description="Modulation index using a 2.0 threshold factor."),
    MetricSpec("dt", "dt", dual_mlc=True, description="Beam-on delivery time."),
    MetricSpec("pi", "PI", "10.1118/1.4861821", dual_mlc=True, aliases=("plan_irregularity",), description="Irregularity of the aperture shape relative to its area."),
    MetricSpec("pm", "PM", "10.1118/1.4861821", dual_mlc=True, aliases=("plan_modulation",), description="Variation in aperture area between successive control points."),
    MetricSpec("mcs5", "MCS5", "10.1007/s13246-020-00891-2", gui_label="MCS5 (Tamura 2020 effective 5 mm MLC)", description="Tamura et al. effective 5 mm dual-layer MLC modulation complexity score computed from the synthesized Halcyon/Ethos aperture."),
    MetricSpec("pa5", "PA5", "10.1007/s13246-020-00891-2", gui_label="PA5 (Tamura 2020 effective 5 mm MLC)", description="Tamura et al. plan averaged beam area for the synthesized effective 5 mm Halcyon/Ethos aperture."),
    MetricSpec("pi5", "PI5", "10.1007/s13246-020-00891-2", gui_label="PI5 (Tamura 2020 effective 5 mm MLC)", description="Tamura et al. plan averaged beam irregularity for the synthesized effective 5 mm Halcyon/Ethos aperture."),
    MetricSpec("pm5", "PM5", "10.1007/s13246-020-00891-2", gui_label="PM5 (Tamura 2020 effective 5 mm MLC)", description="Tamura et al. plan averaged beam modulation for the synthesized effective 5 mm Halcyon/Ethos aperture."),
    MetricSpec("eds", "EDS", "10.1007/s13246-020-00891-2", gui_label="EDS (Tamura 2020 effective distal MLC score)", description="Tamura et al. effective distal MLC score: MU-weighted fraction of the effective field shape attributed to the distal MLC layer."),
    MetricSpec("mcsw", "MCSw", "10.1007/s13246-020-00891-2", gui_label="MCSw (Tamura 2020 weighted dual-layer MCS)", description="Tamura et al. weighted MCS combining proximal and distal MLC layer contributions to the effective field shape."),
    MetricSpec("paw", "PAw", "10.1007/s13246-020-00891-2", gui_label="PAw (Tamura 2020 weighted dual-layer PA)", description="Tamura et al. weighted plan averaged beam area combining proximal and distal MLC layer field-shape contributions."),
    MetricSpec("piw", "PIw", "10.1007/s13246-020-00891-2", gui_label="PIw (Tamura 2020 weighted dual-layer PI)", description="Tamura et al. weighted plan averaged beam irregularity combining proximal and distal MLC layer field-shape contributions."),
    MetricSpec("pmw", "PMw", "10.1007/s13246-020-00891-2", gui_label="PMw (Tamura 2020 weighted dual-layer PM)", description="Tamura et al. weighted plan averaged beam modulation combining proximal and distal MLC layer field-shape contributions."),
    MetricSpec("proximal_mcs", "pMCS", "10.1007/s13246-020-00891-2", description="Tamura et al. proximal-layer MCS for Halcyon/Ethos MLCX2."),
    MetricSpec("distal_mcs", "dMCS", "10.1007/s13246-020-00891-2", description="Tamura et al. distal-layer MCS for Halcyon/Ethos MLCX1."),
    MetricSpec("proximal_pa", "pPA", "10.1007/s13246-020-00891-2", description="Tamura et al. proximal-layer PA for Halcyon/Ethos MLCX2."),
    MetricSpec("distal_pa", "dPA", "10.1007/s13246-020-00891-2", description="Tamura et al. distal-layer PA for Halcyon/Ethos MLCX1."),
    MetricSpec("proximal_pi", "pPI", "10.1007/s13246-020-00891-2", description="Tamura et al. proximal-layer PI for Halcyon/Ethos MLCX2."),
    MetricSpec("distal_pi", "dPI", "10.1007/s13246-020-00891-2", description="Tamura et al. distal-layer PI for Halcyon/Ethos MLCX1."),
    MetricSpec("proximal_pm", "pPM", "10.1007/s13246-020-00891-2", description="Tamura et al. proximal-layer PM for Halcyon/Ethos MLCX2."),
    MetricSpec("distal_pm", "dPM", "10.1007/s13246-020-00891-2", description="Tamura et al. distal-layer PM for Halcyon/Ethos MLCX1."),
    MetricSpec("proximal_mcsw", "pMCSw", "10.1007/s13246-020-00891-2", description="Proximal contribution term of Tamura et al. weighted MCS."),
    MetricSpec("distal_mcsw", "dMCSw", "10.1007/s13246-020-00891-2", description="Distal contribution term of Tamura et al. weighted MCS."),
    MetricSpec("proximal_paw", "pPAw", "10.1007/s13246-020-00891-2", description="Proximal contribution term of Tamura et al. weighted PA."),
    MetricSpec("distal_paw", "dPAw", "10.1007/s13246-020-00891-2", description="Distal contribution term of Tamura et al. weighted PA."),
    MetricSpec("proximal_piw", "pPIw", "10.1007/s13246-020-00891-2", description="Proximal contribution term of Tamura et al. weighted PI."),
    MetricSpec("distal_piw", "dPIw", "10.1007/s13246-020-00891-2", description="Distal contribution term of Tamura et al. weighted PI."),
    MetricSpec("proximal_pmw", "pPMw", "10.1007/s13246-020-00891-2", description="Proximal contribution term of Tamura et al. weighted PM."),
    MetricSpec("distal_pmw", "dPMw", "10.1007/s13246-020-00891-2", description="Distal contribution term of Tamura et al. weighted PM."),
    MetricSpec("ul", "UL", "10.1259/bjr.20201011", gui_label="UL (Quintero 2021 uncovered-layer score)", description="Quintero et al. uncovered-layer score: MU-weighted fraction of effective leaf-edge spots exposed by incomplete complementary-layer coverage."),
    MetricSpec("proximal_ul", "pUL", "10.1259/bjr.20201011", description="Proximal-layer component of the Quintero et al. uncovered-layer score."),
    MetricSpec("distal_ul", "dUL", "10.1259/bjr.20201011", description="Distal-layer component of the Quintero et al. uncovered-layer score."),
    MetricSpec("mcsul", "MCSUL", "10.1259/bjr.20201011", gui_label="MCSUL (Quintero 2021 uncovered-layer weighted MCS)", description="Quintero et al. MCSw adapted by uncovered-layer contribution for Halcyon-v2 dual-layer MLC complexity."),
    MetricSpec("proximal_mcsul", "pMCSUL", "10.1259/bjr.20201011", description="Proximal component of Quintero et al. MCSUL."),
    MetricSpec("distal_mcsul", "dMCSUL", "10.1259/bjr.20201011", description="Distal component of Quintero et al. MCSUL."),
    MetricSpec("np", "NP", "10.1259/bjr.20201011", gui_label="NP (Quintero 2021 number of peaks score)", description="Quintero et al. number of peaks score: average number of scipy.signal.find_peaks trajectory peaks across moving leaves."),
    MetricSpec("mucp", "MUcp", "10.1259/bjr.20201011", gui_label="MUcp (Quintero 2021 mean MU increment %)", description="Quintero et al. averaged monitor-unit increment between adjacent control points, reported as a percentage of beam MU."),
    MetricSpec("proximal_weight_mean", "Mean wp", "10.1007/s13246-020-00891-2", description="MU-weighted mean proximal MLC field-shape contribution used by the Tamura weighting method."),
    MetricSpec("distal_weight_mean", "Mean wd", "10.1007/s13246-020-00891-2", description="MU-weighted mean distal MLC field-shape contribution used by the Tamura weighting method and equivalent to the EDS attribution basis."),
    MetricSpec("md", "MD", "10.1016/j.radonc.2018.06.023", dual_mlc=True, description="Degree of modulation present in the delivered field shapes."),
    MetricSpec("pa", "PA", "10.1118/1.4810969", dual_mlc=True, aliases=("mean_field_area", "leaf_area"), description="Average beam's-eye-view aperture area."),
    MetricSpec("efs", "EFS", "10.1088/1361-6560/aae338", dual_mlc=True, description="Equivalent square field size of the aperture."),
    MetricSpec("psmall", "psmall", dual_mlc=True, description="Fraction of apertures classified as small fields."),
    MetricSpec("sas_5mm", "SAS5mm", "10.1088/0031-9155/60/6/2587", dual_mlc=True, aliases=("small_aperture_score_5mm",), description="Fraction of leaf gaps smaller than 5 mm."),
    MetricSpec("sas_10mm", "SAS10mm", "10.1088/0031-9155/60/6/2587", dual_mlc=True, aliases=("small_aperture_score_10mm",), description="Fraction of leaf gaps smaller than 10 mm."),
    MetricSpec("sas_20mm", "SAS20mm", "10.1088/0031-9155/60/6/2587", dual_mlc=True, aliases=("small_aperture_score_20mm",), description="Fraction of leaf gaps smaller than 20 mm."),
    MetricSpec("em", "EM", "10.1118/1.4762566", dual_mlc=True, aliases=("edge_metric",), description="Relative amount of aperture edge compared with open field area."),
    MetricSpec("bjar", "BJAR", dual_mlc=False, aliases=("aperture_area_ratio_jaw_area",), description="Ratio between aperture area and jaw-defined area."),
    MetricSpec("mad", "MAD", "10.1088/0031-9155/60/6/2587", dual_mlc=True, aliases=("mean_asymmetry_distance",), description="Average distance of the aperture opening from the beam central axis."),
    MetricSpec("alg", "ALG", dual_mlc=True, description="Average gap between opposing leaf pairs."),
    MetricSpec("alg_sd", "ALG SD", dual_mlc=True, description="Standard deviation of the opposing leaf gap."),
    MetricSpec("perimeter", "P", dual_mlc=True, description="Average perimeter of the beam's-eye-view aperture."),
    MetricSpec("asr", "ASR", dual_mlc=True, aliases=("aperture_sub_regions",), description="Average number of disconnected open sub-regions in the aperture."),
    MetricSpec("axjd", "AXJD", aliases=("aperture_x_jaw_distance",), description="Distance between aperture extent and X jaws."),
    MetricSpec("ayjd", "AYJD", aliases=("aperture_y_jaw_distance",), description="Distance between aperture extent and Y jaws."),
    MetricSpec("cam", "CAM", dual_mlc=True, aliases=("converted_aperture_metric",), description="Aperture complexity score based on converted field geometry."),
    MetricSpec("eam", "EAM", dual_mlc=True, aliases=("edge_area_metric",), description="Combined edge-and-area measure of aperture complexity."),
    MetricSpec(
        "mlc_speed_acc",
        "MLC Speed/Acceleration Profile",
        "10.1259/bjr.20140698",
        gui_label="MLC Speed and Acceleration Proportions (Park 2015)",
        description=(
            "Leaf-wise mean proportions for Park et al. VMAT delivery bins. "
            "Speed bins: 0-4, 4-8, 8-12, 12-16, 16-20 mm/s. "
            "Acceleration bins: 0-40, 40-80, 80-120, 120-160, 160-200 mm/s^2."
        ),
    ),
    MetricSpec(
        "sport",
        "SPORT",
        "10.1118/1.4802748",
        gui_label="SPORT Modulation Index (Li and Xing 2013)",
        description=(
            "Station-wise SPORT modulation index MI(s) from Li and Xing, "
            "reported here as the framework's beam/plan aggregate summary."
        ),
    ),
)

VMAT_METRIC_SPECS += (
    MetricSpec(
        "lt_mean_leaf",
        "LT Mean Leaf",
        "10.1118/1.4810969",
        dual_mlc=True,
        description="Raw trajectory travel averaged over moving physical leaves.",
    ),
    MetricSpec(
        "nl_pairs",
        "NL Pairs",
        dual_mlc=True,
        description="MU-weighted number of active leaf pairs; the legacy NL key is an alias value.",
    ),
    MetricSpec(
        "nl_leaves",
        "NL Leaves",
        dual_mlc=True,
        description="MU-weighted number of active physical leaves, exactly twice NL Pairs.",
    ),
)

_HYBRID_REPRESENTATION_LABELS = {
    "mcsv": "MCSv",
    "aav": "AAV",
    "lsv": "LSV",
    "pa": "PA",
    "mad": "MAD",
    "alg": "ALG",
    "alg_sd": "ALG SD",
    "sas_5mm": "SAS5mm",
    "sas_10mm": "SAS10mm",
    "sas_20mm": "SAS20mm",
    "lt": "LT",
    "lt_mean_leaf": "LT Mean Leaf",
    "nl_pairs": "NL Pairs",
    "nl_leaves": "NL Leaves",
}
VMAT_METRIC_SPECS += tuple(
    MetricSpec(
        f"{key}_{representation}",
        f"{label} {representation.title()}",
        description=(
            f"{label} computed on the physical effective dual-layer aperture."
            if representation == "effective"
            else f"{label} computed on the non-physical stacked dual-layer diagnostic geometry."
        ),
    )
    for representation in ("effective", "stacked")
    for key, label in _HYBRID_REPRESENTATION_LABELS.items()
)

CYBERKNIFE_METRIC_SPECS = (
    MetricSpec("mcs", "MCS", "10.1002/mp.14667", gui_label="MCS (CyberKnife MLC)", description="Overall modulation complexity of the delivered CyberKnife MLC apertures."),
    MetricSpec("em", "EM", "10.1118/1.4762566", description="Relative amount of aperture edge compared with open field area."),
    MetricSpec("pi", "PI", "10.1118/1.4861821", description="Irregularity of the CyberKnife MLC aperture shape."),
    MetricSpec("pm", "PM", "10.1118/1.4861821", description="Variation in aperture opening between successive segments."),
    MetricSpec("lg", "LG", "10.1002/mp.14667", gui_label="LG (Mean Leaf Gap)", description="Average gap between opposing CyberKnife MLC leaves."),
    MetricSpec("sas10", "SAS10", "10.1002/mp.14667", gui_label="SAS10 (CyberKnife)", description="Fraction of CyberKnife MLC gaps smaller than 10 mm."),
)

TOMO_METRIC_SPECS = (
    MetricSpec("mf", "MF", description="Ratio describing how strongly the sinogram is modulated overall."),
    MetricSpec("nproj_rot", "N proj,rot", description="Number of projections delivered in one full gantry rotation."),
    MetricSpec("nproj", "N proj", description="Total number of projections in the plan."),
    MetricSpec("nrot", "N rot", description="Total number of gantry rotations in the plan."),
    MetricSpec("projection_time_s", "PT", description="Duration of each projection."),
    MetricSpec("gantry_period_s", "GP", description="Time required for one full gantry rotation."),
    MetricSpec("treatment_time_s", "TT", description="Total beam-on treatment time."),
    MetricSpec("field_width_mm", "FW", description="Nominal field width used for the plan."),
    MetricSpec("pitch", "Pitch", description="Ratio between couch travel per rotation and field width."),
    MetricSpec("couch_translation_mm", "CT", description="Total couch translation during treatment."),
    MetricSpec("couch_speed_mm_s", "CS", description="Average couch translation speed."),
    MetricSpec("target_length_mm", "TL", description="Estimated target length covered by the plan."),
    MetricSpec("ttdf_s_cgy", "TTDF", description="Treatment time normalized by dose per fraction."),
    MetricSpec("mlot", "mLOT", description="Mean leaf open time across all open leaves."),
    MetricSpec("sdlot", "sdLOT", description="Standard deviation of leaf open time."),
    MetricSpec("mdlot", "mdLOT", description="Median leaf open time."),
    MetricSpec("molot", "moLOT", description="Most frequent leaf open time."),
    MetricSpec("maxlot", "maxLOT", description="Maximum leaf open time."),
    MetricSpec("minlot", "minLOT", description="Minimum non-zero leaf open time."),
    MetricSpec("klot", "kLOT", description="Kurtosis of the leaf open time distribution."),
    MetricSpec("slot", "sLOT", description="Skewness of the leaf open time distribution."),
    MetricSpec("clns_10ms", "CLNS10", description="Fraction of leaf open times shorter than 10 ms."),
    MetricSpec("clns_20ms", "CLNS20", description="Fraction of leaf open times shorter than 20 ms."),
    MetricSpec("clns_30ms", "CLNS30", description="Fraction of leaf open times shorter than 30 ms."),
    MetricSpec("clns_50ms", "CLNS50", description="Fraction of leaf open times shorter than 50 ms."),
    MetricSpec("clns_pt_10ms", "CLNSpt10", description="Fraction of leaf open times within 10 ms of the projection time."),
    MetricSpec("clns_pt_20ms", "CLNSpt20", description="Fraction of leaf open times within 20 ms of the projection time."),
    MetricSpec("clns_pt_30ms", "CLNSpt30", description="Fraction of leaf open times within 30 ms of the projection time."),
    MetricSpec("clns_pt_50ms", "CLNSpt50", description="Fraction of leaf open times within 50 ms of the projection time."),
    MetricSpec("mflot", "mFLOT", description="Mean fractional leaf open time."),
    MetricSpec("sdflot", "sdFLOT", description="Standard deviation of fractional leaf open time."),
    MetricSpec("mdflot", "mdFLOT", description="Median fractional leaf open time."),
    MetricSpec("moflot", "moFLOT", description="Most frequent fractional leaf open time."),
    MetricSpec("maxflot", "maxFLOT", description="Maximum fractional leaf open time."),
    MetricSpec("minflot", "minFLOT", description="Minimum non-zero fractional leaf open time."),
    MetricSpec("cfns_0_1", "CFNS0.1", description="Fraction of fractional leaf open times below 0.1."),
    MetricSpec("cfns_0_25", "CFNS0.25", description="Fraction of fractional leaf open times below 0.25."),
    MetricSpec("cfns_0_5", "CFNS0.5", description="Fraction of fractional leaf open times below 0.5."),
    MetricSpec("cfns_0_75", "CFNS0.75", description="Fraction of fractional leaf open times below 0.75."),
    MetricSpec("ta", "TA", description="Average width of the treated sinogram area per projection."),
    MetricSpec("ncc", "nCC", description="Average number of disconnected open components per projection."),
    MetricSpec("lengthcc", "lengthCC", description="Average length of connected open sinogram components."),
    MetricSpec("fdisc", "fDISC", description="Fraction of projections with discontinuous open regions."),
    MetricSpec("cls", "CLS", description="Fraction of leaves that remain closed across the full sinogram width."),
    MetricSpec("clsin", "CLSin", description="Closed leaf score within the treatment area."),
    MetricSpec("clsinarea", "CLSinarea", description="Closed leaf score within the treatment area, normalized by area."),
    MetricSpec("clsindisc", "CLSindisc", description="Closed leaf score within discontinuous treatment projections."),
    MetricSpec("clsinareadisc", "CLSinareadisc", description="Area-normalized closed leaf score for discontinuous projections."),
    MetricSpec("centroid", "Centroid", description="Average lateral position of the open sinogram barycenter."),
    MetricSpec("l0ns", "L0NS", description="Fraction of open leaves with no open nearest neighbors."),
    MetricSpec("l1ns", "L1NS", description="Fraction of open leaves with one open nearest neighbor."),
    MetricSpec("l2ns", "L2NS", description="Fraction of open leaves with two open nearest neighbors."),
    MetricSpec("lotv", "LOTV", description="Variability of leaf open time across consecutive projections."),
    MetricSpec("elotv_1", "ELOTV-1", description="Extended leaf open time variability using a one-projection offset."),
    MetricSpec("elotv_5", "ELOTV-5", description="Extended leaf open time variability using a five-projection offset."),
    MetricSpec("pstv", "PSTV", description="Plan sinogram time variability across neighboring projections and leaves."),
    MetricSpec("epstv_1_1", "EPSTV-1,1", description="Extended plan sinogram time variability using one-step projection and leaf offsets."),
    MetricSpec("epstv_1_0", "EPSTV-1,0", description="Extended plan sinogram time variability using only a projection offset."),
    MetricSpec("epstv_0_1", "EPSTV-0,1", description="Extended plan sinogram time variability using only a leaf offset."),
    MetricSpec("mi", "MI", description="Overall modulation index of the tomotherapy sinogram."),
    MetricSpec("noc", "nOC", description="Average number of leaf openings and closures per leaf."),
    MetricSpec("msa", "mSA", description="Mean left-right asymmetry of the sinogram."),
    MetricSpec("msi", "mSI", description="Mean sinogram intensity."),
    MetricSpec("mdsi", "mdSI", description="Median sinogram intensity."),
    MetricSpec("sdsi", "sdSI", description="Standard deviation of sinogram intensity."),
)


def _humanize_aurora_metric_key(metric_key: str) -> str:
    replacements = {
        "cv": "CV",
        "mu": "MU",
        "mm": "mm",
        "mlc": "MLC",
        "mlcx1": "MLCX1",
        "mlcx2": "MLCX2",
        "x1": "X1",
        "x2": "X2",
        "z": "Z",
        "p95": "P95",
        "top3": "Top3",
    }
    return " ".join(
        replacements.get(word, word.capitalize())
        for word in metric_key.replace("-", "_").split("_")
        if word
    )


VMAT_METRIC_BY_KEY: Dict[str, MetricSpec] = {spec.key: spec for spec in VMAT_METRIC_SPECS}
CYBERKNIFE_METRIC_BY_KEY: Dict[str, MetricSpec] = {spec.key: spec for spec in CYBERKNIFE_METRIC_SPECS}
TOMO_METRIC_BY_KEY: Dict[str, MetricSpec] = {spec.key: spec for spec in TOMO_METRIC_SPECS}
AURORA_METRIC_DESCRIPTIONS: Dict[str, str] = get_metric_notes()
AURORA_METRIC_LABELS: Dict[str, str] = {
    key: _humanize_aurora_metric_key(key)
    for key in AURORA_METRIC_DESCRIPTIONS
}
AURORA_METRIC_GUI_LABELS: Dict[str, str] = dict(AURORA_METRIC_LABELS)
VMAT_METRIC_LABELS: Dict[str, str] = {spec.key: spec.label for spec in VMAT_METRIC_SPECS}
CYBERKNIFE_METRIC_LABELS: Dict[str, str] = {spec.key: spec.label for spec in CYBERKNIFE_METRIC_SPECS}
TOMO_METRIC_LABELS: Dict[str, str] = {spec.key: spec.label for spec in TOMO_METRIC_SPECS}
VMAT_METRIC_GUI_LABELS: Dict[str, str] = {
    spec.key: (spec.gui_label or spec.label) for spec in VMAT_METRIC_SPECS
}
CYBERKNIFE_METRIC_GUI_LABELS: Dict[str, str] = {
    spec.key: (spec.gui_label or spec.label) for spec in CYBERKNIFE_METRIC_SPECS
}
TOMO_METRIC_GUI_LABELS: Dict[str, str] = {
    spec.key: (spec.gui_label or spec.label) for spec in TOMO_METRIC_SPECS
}
VMAT_METRIC_DESCRIPTIONS: Dict[str, str] = {spec.key: spec.description for spec in VMAT_METRIC_SPECS if spec.description}
CYBERKNIFE_METRIC_DESCRIPTIONS: Dict[str, str] = {spec.key: spec.description for spec in CYBERKNIFE_METRIC_SPECS if spec.description}
TOMO_METRIC_DESCRIPTIONS: Dict[str, str] = {spec.key: spec.description for spec in TOMO_METRIC_SPECS if spec.description}
VMAT_DUAL_MLC_KEYS = {spec.key for spec in VMAT_METRIC_SPECS if spec.dual_mlc}
VMAT_ALIAS_TO_KEY: Dict[str, str] = {}
for spec in VMAT_METRIC_SPECS:
    for alias in spec.aliases:
        VMAT_ALIAS_TO_KEY[alias] = spec.key


SPECIAL_FLATTENED_LABELS: Dict[str, str] = {
    "speed_0_4": "Park Speed 0-4 mm/s",
    "speed_4_8": "Park Speed 4-8 mm/s",
    "speed_8_12": "Park Speed 8-12 mm/s",
    "speed_12_16": "Park Speed 12-16 mm/s",
    "speed_16_20": "Park Speed 16-20 mm/s",
    "acc_0_40": "Park Acceleration 0-40 mm/s^2",
    "acc_40_80": "Park Acceleration 40-80 mm/s^2",
    "acc_80_120": "Park Acceleration 80-120 mm/s^2",
    "acc_120_160": "Park Acceleration 120-160 mm/s^2",
    "acc_160_200": "Park Acceleration 160-200 mm/s^2",
    "speed_average": "Mean Leaf Speed (mm/s)",
    "acc_average": "Mean Leaf Acceleration (mm/s^2)",
    "speed_std": "Mean Leaf Speed SD (mm/s)",
    "acc_std": "Mean Leaf Acceleration SD (mm/s^2)",
    "mlcx1_speed_0_4": "MLCX1 Park Speed 0-4 mm/s",
    "mlcx1_speed_4_8": "MLCX1 Park Speed 4-8 mm/s",
    "mlcx1_speed_8_12": "MLCX1 Park Speed 8-12 mm/s",
    "mlcx1_speed_12_16": "MLCX1 Park Speed 12-16 mm/s",
    "mlcx1_speed_16_20": "MLCX1 Park Speed 16-20 mm/s",
    "mlcx1_acc_0_40": "MLCX1 Park Acceleration 0-40 mm/s^2",
    "mlcx1_acc_40_80": "MLCX1 Park Acceleration 40-80 mm/s^2",
    "mlcx1_acc_80_120": "MLCX1 Park Acceleration 80-120 mm/s^2",
    "mlcx1_acc_120_160": "MLCX1 Park Acceleration 120-160 mm/s^2",
    "mlcx1_acc_160_200": "MLCX1 Park Acceleration 160-200 mm/s^2",
    "mlcx1_speed_average": "MLCX1 Mean Leaf Speed (mm/s)",
    "mlcx1_acc_average": "MLCX1 Mean Leaf Acceleration (mm/s^2)",
    "mlcx1_speed_std": "MLCX1 Mean Leaf Speed SD (mm/s)",
    "mlcx1_acc_std": "MLCX1 Mean Leaf Acceleration SD (mm/s^2)",
    "mlcx2_speed_0_4": "MLCX2 Park Speed 0-4 mm/s",
    "mlcx2_speed_4_8": "MLCX2 Park Speed 4-8 mm/s",
    "mlcx2_speed_8_12": "MLCX2 Park Speed 8-12 mm/s",
    "mlcx2_speed_12_16": "MLCX2 Park Speed 12-16 mm/s",
    "mlcx2_speed_16_20": "MLCX2 Park Speed 16-20 mm/s",
    "mlcx2_acc_0_40": "MLCX2 Park Acceleration 0-40 mm/s^2",
    "mlcx2_acc_40_80": "MLCX2 Park Acceleration 40-80 mm/s^2",
    "mlcx2_acc_80_120": "MLCX2 Park Acceleration 80-120 mm/s^2",
    "mlcx2_acc_120_160": "MLCX2 Park Acceleration 120-160 mm/s^2",
    "mlcx2_acc_160_200": "MLCX2 Park Acceleration 160-200 mm/s^2",
    "mlcx2_speed_average": "MLCX2 Mean Leaf Speed (mm/s)",
    "mlcx2_acc_average": "MLCX2 Mean Leaf Acceleration (mm/s^2)",
    "mlcx2_speed_std": "MLCX2 Mean Leaf Speed SD (mm/s)",
    "mlcx2_acc_std": "MLCX2 Mean Leaf Acceleration SD (mm/s^2)",
}


SPECIAL_FLATTENED_DESCRIPTIONS: Dict[str, str] = {
    "sport": VMAT_METRIC_DESCRIPTIONS["sport"],
    "speed_0_4": "Leaf-wise mean proportion of valid control-point intervals with speed in 0-4 mm/s.",
    "speed_4_8": "Leaf-wise mean proportion of valid control-point intervals with speed in 4-8 mm/s.",
    "speed_8_12": "Leaf-wise mean proportion of valid control-point intervals with speed in 8-12 mm/s.",
    "speed_12_16": "Leaf-wise mean proportion of valid control-point intervals with speed in 12-16 mm/s.",
    "speed_16_20": "Leaf-wise mean proportion of valid control-point intervals with speed in 16-20 mm/s.",
    "acc_0_40": "Leaf-wise mean proportion of valid control-point intervals with acceleration in 0-40 mm/s^2.",
    "acc_40_80": "Leaf-wise mean proportion of valid control-point intervals with acceleration in 40-80 mm/s^2.",
    "acc_80_120": "Leaf-wise mean proportion of valid control-point intervals with acceleration in 80-120 mm/s^2.",
    "acc_120_160": "Leaf-wise mean proportion of valid control-point intervals with acceleration in 120-160 mm/s^2.",
    "acc_160_200": "Leaf-wise mean proportion of valid control-point intervals with acceleration in 160-200 mm/s^2.",
}

for metric_key, label in (("mi_0_2", "0.2"), ("mi_0_5", "0.5"), ("mi_1_0", "1.0"), ("mi_2_0", "2.0")):
    SPECIAL_FLATTENED_DESCRIPTIONS[f"{metric_key}_mis"] = f"Leaf speed contribution to the modulation index with threshold factor {label}."
    SPECIAL_FLATTENED_DESCRIPTIONS[f"{metric_key}_mia"] = f"Leaf acceleration contribution to the modulation index with threshold factor {label}."
    SPECIAL_FLATTENED_DESCRIPTIONS[f"{metric_key}_mit"] = f"Total modulation index with threshold factor {label}."
    SPECIAL_FLATTENED_DESCRIPTIONS[f"{metric_key}_mlcx1_mis"] = f"Leaf speed contribution to the modulation index with threshold factor {label} for MLCX1."
    SPECIAL_FLATTENED_DESCRIPTIONS[f"{metric_key}_mlcx1_mia"] = f"Leaf acceleration contribution to the modulation index with threshold factor {label} for MLCX1."
    SPECIAL_FLATTENED_DESCRIPTIONS[f"{metric_key}_mlcx1_mit"] = f"Total modulation index with threshold factor {label} for MLCX1."
    SPECIAL_FLATTENED_DESCRIPTIONS[f"{metric_key}_mlcx2_mis"] = f"Leaf speed contribution to the modulation index with threshold factor {label} for MLCX2."
    SPECIAL_FLATTENED_DESCRIPTIONS[f"{metric_key}_mlcx2_mia"] = f"Leaf acceleration contribution to the modulation index with threshold factor {label} for MLCX2."
    SPECIAL_FLATTENED_DESCRIPTIONS[f"{metric_key}_mlcx2_mit"] = f"Total modulation index with threshold factor {label} for MLCX2."

for key, description in list(VMAT_METRIC_DESCRIPTIONS.items()):
    if key in VMAT_DUAL_MLC_KEYS:
        SPECIAL_FLATTENED_DESCRIPTIONS[f"{key}_mlcx1"] = f"{description} Reported for MLCX1."
        SPECIAL_FLATTENED_DESCRIPTIONS[f"{key}_mlcx2"] = f"{description} Reported for MLCX2."

for key, label in (("mi_0_2", "0.2"), ("mi_0_5", "0.5"), ("mi_1_0", "1.0"), ("mi_2_0", "2.0")):
    SPECIAL_FLATTENED_LABELS[f"{key}_mis"] = f"MI({label}) Speed"
    SPECIAL_FLATTENED_LABELS[f"{key}_mia"] = f"MI({label}) Acceleration"
    SPECIAL_FLATTENED_LABELS[f"{key}_mit"] = f"MI({label}) Total"
    SPECIAL_FLATTENED_LABELS[f"{key}_mlcx1_mis"] = f"MI({label}) MLCX1 Speed"
    SPECIAL_FLATTENED_LABELS[f"{key}_mlcx1_mia"] = f"MI({label}) MLCX1 Acceleration"
    SPECIAL_FLATTENED_LABELS[f"{key}_mlcx1_mit"] = f"MI({label}) MLCX1 Total"
    SPECIAL_FLATTENED_LABELS[f"{key}_mlcx2_mis"] = f"MI({label}) MLCX2 Speed"
    SPECIAL_FLATTENED_LABELS[f"{key}_mlcx2_mia"] = f"MI({label}) MLCX2 Acceleration"
    SPECIAL_FLATTENED_LABELS[f"{key}_mlcx2_mit"] = f"MI({label}) MLCX2 Total"

for key, label in list(VMAT_METRIC_LABELS.items()):
    if key in VMAT_DUAL_MLC_KEYS:
        SPECIAL_FLATTENED_LABELS[f"{key}_mlcx1"] = f"{label} MLCX1"
        SPECIAL_FLATTENED_LABELS[f"{key}_mlcx2"] = f"{label} MLCX2"


def canonical_metric_key(key: str) -> str:
    return VMAT_ALIAS_TO_KEY.get(key, key)


def metric_labels_with_aliases() -> Dict[str, str]:
    labels = dict(VMAT_METRIC_LABELS)
    labels.update(CYBERKNIFE_METRIC_LABELS)
    labels.update(TOMO_METRIC_LABELS)
    labels.update(AURORA_METRIC_LABELS)
    for alias, key in VMAT_ALIAS_TO_KEY.items():
        labels[alias] = VMAT_METRIC_LABELS[key]
    return labels


def metric_gui_labels_with_aliases() -> Dict[str, str]:
    labels = dict(VMAT_METRIC_GUI_LABELS)
    labels.update(CYBERKNIFE_METRIC_GUI_LABELS)
    labels.update(TOMO_METRIC_GUI_LABELS)
    labels.update(AURORA_METRIC_GUI_LABELS)
    labels.update(SPECIAL_FLATTENED_LABELS)
    for alias, key in VMAT_ALIAS_TO_KEY.items():
        labels[alias] = VMAT_METRIC_GUI_LABELS[key]
    return labels


def metric_descriptions_with_aliases() -> Dict[str, str]:
    descriptions = dict(VMAT_METRIC_DESCRIPTIONS)
    descriptions.update(CYBERKNIFE_METRIC_DESCRIPTIONS)
    descriptions.update(TOMO_METRIC_DESCRIPTIONS)
    descriptions.update(AURORA_METRIC_DESCRIPTIONS)
    descriptions.update(SPECIAL_FLATTENED_DESCRIPTIONS)
    for alias, key in VMAT_ALIAS_TO_KEY.items():
        if key in VMAT_METRIC_DESCRIPTIONS:
            descriptions[alias] = VMAT_METRIC_DESCRIPTIONS[key]
    return descriptions


def ordered_metric_keys() -> Iterable[str]:
    for spec in VMAT_METRIC_SPECS:
        yield spec.key
