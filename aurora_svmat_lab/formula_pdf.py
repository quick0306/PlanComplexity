from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from metric_definition_catalog import build_metric_definition_catalog

from .metrics import LEGACY_METRIC_ORDER, V2_METRIC_ORDER, V3_METRIC_ORDER
from .notes import get_metric_notes


@dataclass(frozen=True)
class FormulaEntry:
    metric_key: str
    title: str
    formula_lines: tuple[str, ...]
    physical_meaning: str


def export_aurora_formula_pdf(output_path: str | Path) -> Path:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    document = SimpleDocTemplate(
        str(destination),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Aurora SVMAT Metric Formula Reference",
        author="Codex for Jinyan Hu",
    )
    styles = _build_styles()
    story: list[object] = []

    story.extend(_build_cover(styles))
    story.extend(_build_notation_section(styles))
    story.extend(_build_metric_section("Section 1. V2 Metrics", _build_v2_entries(), styles))
    story.append(PageBreak())
    story.extend(
        _build_metric_section(
            "Section 2. V3 Research Metrics",
            _build_v3_entries(),
            styles,
            intro=(
                "These research-facing v3 metrics are the immediately implementable Aurora extensions derived directly "
                "from currently parsed RTPLAN control-point data."
            ),
        )
    )
    story.append(PageBreak())
    story.extend(
        _build_metric_section(
            "Appendix A. Legacy Engineering Metrics",
            _build_legacy_entries(),
            styles,
            intro=(
                "These legacy metrics are retained for engineering comparison with the first-pass Aurora prototype. "
                "They are not the preferred paper-style reporting set."
            ),
        )
    )

    document.build(story, onFirstPage=_draw_page_number, onLaterPages=_draw_page_number)
    return destination


def _build_cover(styles: dict[str, ParagraphStyle]) -> list[object]:
    return [
        Spacer(1, 18 * mm),
        Paragraph("Aurora SVMAT Metric Formula Reference", styles["title"]),
        Spacer(1, 4 * mm),
        Paragraph("Main body: v2 and v3 research metrics. Appendix: legacy engineering metrics.", styles["subtitle"]),
        Spacer(1, 8 * mm),
        Paragraph(
            "This document records the explicit mathematical definitions currently implemented in Aurora SVMAT Lab. "
            "The notation is aligned to the control-point sequence view c_i = {theta_i, w_i, M_i, z_i}.",
            styles["body"],
        ),
        Spacer(1, 6 * mm),
        Paragraph(
            "RESEARCH USE ONLY. This document reflects the current code implementation and should be interpreted as a "
            "research reference rather than a clinical specification.",
            styles["callout"],
        ),
        Spacer(1, 10 * mm),
    ]


def _build_notation_section(styles: dict[str, ParagraphStyle]) -> list[object]:
    items = [
        "i indexes adjacent control-point intervals from control point i to i+1.",
        "theta_i is the gantry angle in degrees at control point i.",
        "z_i is the longitudinal or axial position in millimeters at control point i.",
        "w_i is the cumulative meterset weight at control point i.",
        "A_i is the scalar aperture width surrogate at control point i, defined as the summed positive opening across both MLC layers.",
        "L_i is the total leaf-position vector at control point i across both layers.",
        "delta theta_i = wrapped(theta_(i+1) - theta_i), constrained to [-180, 180] degrees.",
        "delta z_i = z_(i+1) - z_i.",
        "delta w_i = w_(i+1) - w_i.",
        "delta A_i = |A_(i+1) - A_i|.",
        "delta L_i = summed absolute leaf travel between adjacent control points across both layers.",
        "CV(x) = std_pop(x) / mean(x), evaluated only on valid non-empty interval sets.",
    ]
    story: list[object] = [
        Paragraph("Notation", styles["section"]),
        Spacer(1, 2 * mm),
    ]
    for item in items:
        story.append(Paragraph(item, styles["bullet"]))
    story.append(Spacer(1, 6 * mm))
    return story


def _build_metric_section(
    heading: str,
    entries: list[FormulaEntry],
    styles: dict[str, ParagraphStyle],
    *,
    intro: str | None = None,
) -> list[object]:
    story: list[object] = [Paragraph(heading, styles["section"]), Spacer(1, 2 * mm)]
    if intro:
        story.extend([Paragraph(intro, styles["body"]), Spacer(1, 4 * mm)])
    for entry in entries:
        story.append(Paragraph(entry.metric_key, styles["metric_key"]))
        story.append(Paragraph(entry.title, styles["metric_title"]))
        for formula_line in entry.formula_lines:
            story.append(Paragraph(formula_line, styles["formula"]))
        story.append(Paragraph(f"Meaning: {entry.physical_meaning}", styles["body"]))
        story.append(Spacer(1, 4 * mm))
    return story


def _build_v2_entries() -> list[FormulaEntry]:
    notes = get_metric_notes(V2_METRIC_ORDER)
    return [
        FormulaEntry(
            metric_key="longitudinal_travel_mm",
            title="Total absolute longitudinal travel",
            formula_lines=("longitudinal_travel_mm = sum_i |delta z_i|",),
            physical_meaning=notes["longitudinal_travel_mm"],
        ),
        FormulaEntry(
            metric_key="total_rotation_deg",
            title="Total absolute gantry rotation",
            formula_lines=("total_rotation_deg = sum_i |delta theta_i|",),
            physical_meaning=notes["total_rotation_deg"],
        ),
        FormulaEntry(
            metric_key="rotations",
            title="Total gantry rotations",
            formula_lines=("rotations = total_rotation_deg / 360",),
            physical_meaning=notes["rotations"],
        ),
        FormulaEntry(
            metric_key="travel_per_rotation_mm",
            title="Longitudinal travel per full gantry rotation",
            formula_lines=("travel_per_rotation_mm = longitudinal_travel_mm / rotations",),
            physical_meaning=notes["travel_per_rotation_mm"],
        ),
        FormulaEntry(
            metric_key="projection_pitch_mean",
            title="Mean projection pitch",
            formula_lines=(
                "projection_pitch_i = |delta z_i| / |delta theta_i|",
                "projection_pitch_mean = mean_i(projection_pitch_i)",
            ),
            physical_meaning=notes["projection_pitch_mean"],
        ),
        FormulaEntry(
            metric_key="projection_pitch_cv",
            title="Projection pitch variability",
            formula_lines=(
                "projection_pitch_i = |delta z_i| / |delta theta_i|",
                "projection_pitch_cv = CV(projection_pitch_i)",
            ),
            physical_meaning=notes["projection_pitch_cv"],
        ),
        FormulaEntry(
            metric_key="projection_mu_density_mean_proxy",
            title="Mean projection meterset-weight density proxy",
            formula_lines=(
                "projection_mu_density_proxy_i = delta w_i / |delta z_i|",
                "projection_mu_density_mean_proxy = mean_i(projection_mu_density_proxy_i)",
            ),
            physical_meaning=notes["projection_mu_density_mean_proxy"],
        ),
        FormulaEntry(
            metric_key="projection_mu_density_cv_proxy",
            title="Variability of the projection meterset-weight density proxy",
            formula_lines=(
                "projection_mu_density_proxy_i = delta w_i / |delta z_i|",
                "projection_mu_density_cv_proxy = CV(projection_mu_density_proxy_i)",
            ),
            physical_meaning=notes["projection_mu_density_cv_proxy"],
        ),
        FormulaEntry(
            metric_key="projection_aperture_change_mean",
            title="Mean aperture-change rate along the longitudinal axis",
            formula_lines=(
                "delta A_i = |A_(i+1) - A_i|",
                "projection_aperture_change_i = delta A_i / |delta z_i|",
                "projection_aperture_change_mean = mean_i(projection_aperture_change_i)",
            ),
            physical_meaning=notes["projection_aperture_change_mean"],
        ),
        FormulaEntry(
            metric_key="projection_aperture_change_cv",
            title="Variability of the aperture-change rate",
            formula_lines=(
                "delta A_i = |A_(i+1) - A_i|",
                "projection_aperture_change_i = delta A_i / |delta z_i|",
                "projection_aperture_change_cv = CV(projection_aperture_change_i)",
            ),
            physical_meaning=notes["projection_aperture_change_cv"],
        ),
        FormulaEntry(
            metric_key="projection_leaf_travel_mean",
            title="Mean leaf-travel rate across both MLC layers",
            formula_lines=(
                "delta L_i = sum_leaves |leaf_(i+1) - leaf_i| across MLCX1 and MLCX2",
                "projection_leaf_travel_i = delta L_i / |delta z_i|",
                "projection_leaf_travel_mean = mean_i(projection_leaf_travel_i)",
            ),
            physical_meaning=notes["projection_leaf_travel_mean"],
        ),
        FormulaEntry(
            metric_key="projection_leaf_travel_cv",
            title="Variability of the total leaf-travel rate",
            formula_lines=(
                "delta L_i = sum_leaves |leaf_(i+1) - leaf_i| across MLCX1 and MLCX2",
                "projection_leaf_travel_i = delta L_i / |delta z_i|",
                "projection_leaf_travel_cv = CV(projection_leaf_travel_i)",
            ),
            physical_meaning=notes["projection_leaf_travel_cv"],
        ),
        FormulaEntry(
            metric_key="projection_leaf_travel_mean_mlcx1",
            title="Mean leaf-travel rate for MLCX1",
            formula_lines=(
                "delta L_i^(MLCX1) = sum_x1 |x1_(i+1) - x1_i|",
                "projection_leaf_travel_mlcx1_i = delta L_i^(MLCX1) / |delta z_i|",
                "projection_leaf_travel_mean_mlcx1 = mean_i(projection_leaf_travel_mlcx1_i)",
            ),
            physical_meaning=notes["projection_leaf_travel_mean_mlcx1"],
        ),
        FormulaEntry(
            metric_key="projection_leaf_travel_cv_mlcx1",
            title="Variability of the MLCX1 leaf-travel rate",
            formula_lines=(
                "delta L_i^(MLCX1) = sum_x1 |x1_(i+1) - x1_i|",
                "projection_leaf_travel_mlcx1_i = delta L_i^(MLCX1) / |delta z_i|",
                "projection_leaf_travel_cv_mlcx1 = CV(projection_leaf_travel_mlcx1_i)",
            ),
            physical_meaning=notes["projection_leaf_travel_cv_mlcx1"],
        ),
        FormulaEntry(
            metric_key="projection_leaf_travel_mean_mlcx2",
            title="Mean leaf-travel rate for MLCX2",
            formula_lines=(
                "delta L_i^(MLCX2) = sum_x2 |x2_(i+1) - x2_i|",
                "projection_leaf_travel_mlcx2_i = delta L_i^(MLCX2) / |delta z_i|",
                "projection_leaf_travel_mean_mlcx2 = mean_i(projection_leaf_travel_mlcx2_i)",
            ),
            physical_meaning=notes["projection_leaf_travel_mean_mlcx2"],
        ),
        FormulaEntry(
            metric_key="projection_leaf_travel_cv_mlcx2",
            title="Variability of the MLCX2 leaf-travel rate",
            formula_lines=(
                "delta L_i^(MLCX2) = sum_x2 |x2_(i+1) - x2_i|",
                "projection_leaf_travel_mlcx2_i = delta L_i^(MLCX2) / |delta z_i|",
                "projection_leaf_travel_cv_mlcx2 = CV(projection_leaf_travel_mlcx2_i)",
            ),
            physical_meaning=notes["projection_leaf_travel_cv_mlcx2"],
        ),
        FormulaEntry(
            metric_key="theta_z_coupling_cv",
            title="Theta-z coupling variability",
            formula_lines=("theta_z_coupling_cv = projection_pitch_cv",),
            physical_meaning=notes["theta_z_coupling_cv"],
        ),
        FormulaEntry(
            metric_key="mu_z_coupling_cv_proxy",
            title="Meterset-weight-density to z coupling variability proxy",
            formula_lines=("mu_z_coupling_cv_proxy = projection_mu_density_cv_proxy",),
            physical_meaning=notes["mu_z_coupling_cv_proxy"],
        ),
        FormulaEntry(
            metric_key="mlc_z_coupling_cv",
            title="MLC-z coupling variability across both layers",
            formula_lines=("mlc_z_coupling_cv = projection_leaf_travel_cv",),
            physical_meaning=notes["mlc_z_coupling_cv"],
        ),
        FormulaEntry(
            metric_key="mlcx1_z_coupling_cv",
            title="MLCX1-z coupling variability",
            formula_lines=("mlcx1_z_coupling_cv = projection_leaf_travel_cv_mlcx1",),
            physical_meaning=notes["mlcx1_z_coupling_cv"],
        ),
        FormulaEntry(
            metric_key="mlcx2_z_coupling_cv",
            title="MLCX2-z coupling variability",
            formula_lines=("mlcx2_z_coupling_cv = projection_leaf_travel_cv_mlcx2",),
            physical_meaning=notes["mlcx2_z_coupling_cv"],
        ),
    ]


def _build_v3_entries() -> list[FormulaEntry]:
    aurora_records = _aurora_record_map()
    title_overrides = {
        "reversal_symmetry_index": "Bidirectional modulation symmetry",
        "forward_backward_metric_difference": "Forward-versus-backward modulation difference",
        "beam_pair_balance_index": "Beam-pair modulation balance",
        "small_opening_fraction": "Fraction of narrow effective openings",
        "near_closed_fraction": "Fraction of near-closed effective openings",
        "effective_small_gap_burden": "Weighted burden of narrow effective gaps",
        "projection_pitch_p95": "95th percentile of projection pitch",
        "projection_pitch_max": "Maximum projection pitch",
        "projection_pitch_top3_mean": "Mean of the top three projection-pitch intervals",
        "projection_mu_density_p95_proxy": "95th percentile of the projection meterset-weight density proxy",
        "projection_mu_density_max_proxy": "Maximum projection meterset-weight density proxy",
        "projection_mu_density_top3_mean_proxy": "Mean of the top three projection meterset-weight density proxy values",
        "projection_aperture_change_p95": "95th percentile of the aperture-change rate",
        "projection_aperture_change_max": "Maximum aperture-change rate",
        "projection_aperture_change_top3_mean": "Mean of the top three aperture-change rates",
        "projection_leaf_travel_p95": "95th percentile of the leaf-travel rate",
        "projection_leaf_travel_max": "Maximum leaf-travel rate",
        "projection_leaf_travel_top3_mean": "Mean of the top three leaf-travel rates",
        "head_mu_density_mean_proxy": "Head-third mean MU-density proxy",
        "head_mu_density_cv_proxy": "Head-third MU-density proxy variability",
        "head_aperture_change_mean": "Head-third mean aperture-change rate",
        "head_aperture_change_cv": "Head-third aperture-change variability",
        "head_leaf_travel_mean": "Head-third mean leaf-travel rate",
        "head_leaf_travel_cv": "Head-third leaf-travel variability",
        "mid_mu_density_mean_proxy": "Mid-third mean MU-density proxy",
        "mid_mu_density_cv_proxy": "Mid-third MU-density proxy variability",
        "mid_aperture_change_mean": "Mid-third mean aperture-change rate",
        "mid_aperture_change_cv": "Mid-third aperture-change variability",
        "mid_leaf_travel_mean": "Mid-third mean leaf-travel rate",
        "mid_leaf_travel_cv": "Mid-third leaf-travel variability",
        "tail_mu_density_mean_proxy": "Tail-third mean MU-density proxy",
        "tail_mu_density_cv_proxy": "Tail-third MU-density proxy variability",
        "tail_aperture_change_mean": "Tail-third mean aperture-change rate",
        "tail_aperture_change_cv": "Tail-third aperture-change variability",
        "tail_leaf_travel_mean": "Tail-third mean leaf-travel rate",
        "tail_leaf_travel_cv": "Tail-third leaf-travel variability",
        "layer_imbalance_index": "Dual-layer travel imbalance",
        "layer_correlation_index": "Dual-layer travel correlation",
        "x1_x2_aperture_disparity": "Dual-layer aperture disparity surrogate",
        "x1_x2_leaf_travel_ratio": "Dual-layer leaf-travel ratio",
    }
    entries: list[FormulaEntry] = []
    for metric_key in V3_METRIC_ORDER:
        record = aurora_records[metric_key]
        entries.append(
            FormulaEntry(
                metric_key=metric_key,
                title=title_overrides.get(metric_key, metric_key),
                formula_lines=(record["mathematical_definition"],),
                physical_meaning=record["physical_meaning"],
            )
        )
    return entries


def _build_legacy_entries() -> list[FormulaEntry]:
    notes = get_metric_notes(LEGACY_METRIC_ORDER)
    return [
        FormulaEntry(
            metric_key="axial_travel_mm",
            title="Legacy total axial travel",
            formula_lines=("axial_travel_mm = sum_i |delta z_i|",),
            physical_meaning=notes["axial_travel_mm"],
        ),
        FormulaEntry(
            metric_key="gantry_rotation_deg",
            title="Legacy total gantry rotation",
            formula_lines=("gantry_rotation_deg = sum_i |delta theta_i|",),
            physical_meaning=notes["gantry_rotation_deg"],
        ),
        FormulaEntry(
            metric_key="mm_per_deg",
            title="Legacy axial travel per gantry degree",
            formula_lines=("mm_per_deg = axial_travel_mm / gantry_rotation_deg",),
            physical_meaning=notes["mm_per_deg"],
        ),
        FormulaEntry(
            metric_key="mm_per_rotation",
            title="Legacy axial travel per full rotation",
            formula_lines=("mm_per_rotation = axial_travel_mm / (gantry_rotation_deg / 360)",),
            physical_meaning=notes["mm_per_rotation"],
        ),
        FormulaEntry(
            metric_key="pitch_consistency",
            title="Legacy pitch consistency metric",
            formula_lines=(
                "interval_pitch_i = |delta z_i| / |delta theta_i|",
                "pitch_consistency = CV(interval_pitch_i)",
            ),
            physical_meaning=notes["pitch_consistency"],
        ),
        FormulaEntry(
            metric_key="mu_per_mm",
            title="Legacy MU density along the axial axis",
            formula_lines=("mu_per_mm = total_mu_or_weight_proxy / axial_travel_mm",),
            physical_meaning=notes["mu_per_mm"],
        ),
        FormulaEntry(
            metric_key="aperture_change_per_mm",
            title="Legacy aperture-change density",
            formula_lines=(
                "aperture_change_per_mm = sum_i delta A_i / sum_i |delta z_i|",
            ),
            physical_meaning=notes["aperture_change_per_mm"],
        ),
        FormulaEntry(
            metric_key="leaf_travel_per_mm",
            title="Legacy leaf-travel density",
            formula_lines=(
                "leaf_travel_per_mm = sum_i delta L_i / sum_i |delta z_i|",
            ),
            physical_meaning=notes["leaf_travel_per_mm"],
        ),
        FormulaEntry(
            metric_key="coupled_modulation_index",
            title="Legacy engineering aggregate",
            formula_lines=(
                "n(x) = x / (1 + x)",
                "coupled_modulation_index = mean( n(aperture_change_per_mm), n(leaf_travel_per_mm), n(mu_density_variability), n(pitch_consistency) )",
            ),
            physical_meaning=notes["coupled_modulation_index"],
        ),
    ]


def _aurora_record_map() -> dict[str, dict[str, str]]:
    records = build_metric_definition_catalog()
    return {
        record.metric_key: {
            "mathematical_definition": record.mathematical_definition,
            "physical_meaning": record.physical_meaning,
        }
        for record in records
        if record.platform == "AURORA"
    }


def _build_styles() -> dict[str, ParagraphStyle]:
    base_styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "AuroraTitle",
            parent=base_styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#15324b"),
        ),
        "subtitle": ParagraphStyle(
            "AuroraSubtitle",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#455a64"),
        ),
        "section": ParagraphStyle(
            "AuroraSection",
            parent=base_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1f4e79"),
            spaceAfter=4,
        ),
        "metric_key": ParagraphStyle(
            "AuroraMetricKey",
            parent=base_styles["Heading4"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=colors.HexColor("#7a2e0b"),
            spaceAfter=2,
        ),
        "metric_title": ParagraphStyle(
            "AuroraMetricTitle",
            parent=base_styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=colors.black,
            spaceAfter=2,
        ),
        "formula": ParagraphStyle(
            "AuroraFormula",
            parent=base_styles["Code"],
            fontName="Courier",
            fontSize=8.7,
            leading=11,
            leftIndent=10,
            textColor=colors.HexColor("#173f35"),
            spaceAfter=1,
        ),
        "body": ParagraphStyle(
            "AuroraBody",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.black,
        ),
        "bullet": ParagraphStyle(
            "AuroraBullet",
            parent=base_styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            leftIndent=10,
            bulletIndent=0,
        ),
        "callout": ParagraphStyle(
            "AuroraCallout",
            parent=base_styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#8a1c1c"),
            backColor=colors.HexColor("#fdf1f1"),
            borderWidth=0.5,
            borderPadding=6,
            borderColor=colors.HexColor("#d9b7b7"),
            borderRadius=3,
        ),
    }


def _draw_page_number(canvas, document) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#607d8b"))
    canvas.drawRightString(195 * mm, 10 * mm, f"Page {document.page}")
    canvas.restoreState()
