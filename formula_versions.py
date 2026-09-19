"""Calculation contracts recorded with exported metrics and reference baselines."""

GEOMETRY_FORMULA_VERSION = "geometry-v4"
TOMO_FORMULA_VERSION = "tomo-v3"


def formula_version_for_mode(mode: str) -> str:
    if mode in {"VMAT_IMRT", "CYBERKNIFE_MLC"}:
        return GEOMETRY_FORMULA_VERSION
    if mode == "TOMO":
        return TOMO_FORMULA_VERSION
    return ""
