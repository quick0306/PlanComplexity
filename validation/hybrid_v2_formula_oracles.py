"""Hand-calculated reference values for the VMAT/IMRT hybrid-v2 formulas."""

HYBRID_V2_ORACLES = {
    "mad_opening_center_mm": 2.0,
    "weighted_gap_mean_mm": 8.25,
    "weighted_gap_variance_mm2": 9.4375,
    "weighted_sas_5mm": 0.875,
    "mean_leaf_travel_mm": 5.0,
    "nl_pairs": 1.5,
    "nl_leaves": 3.0,
}


def get_hybrid_v2_formula_oracles():
    return dict(HYBRID_V2_ORACLES)
