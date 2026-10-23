"""Aurora aperture fields backed by the shared V5 physical geometry contract.

Historical module and function names remain import compatible. CA is P/A;
the Aurora gap-sequence MCS adaptation and its exact complement are retained.
"""
from .physical_aperture import (
    _finite, _bounds, _jaw, _aperture, _area_perimeter,
    summarize_apertures, geometry_scope,
)

V4_METRIC_ORDER = ("mean_ba", "mean_bi", "mean_ca", "mean_sas5", "mean_sas10",
                   "mean_mcs_aurora", "mcs_complexity_aurora")


@geometry_scope
def calculate_v4_metrics_with_warnings(beams):
    """Compatibility entrypoint for the seven versioned physical aperture means."""
    values, warnings = summarize_apertures(list(beams))
    return {key: values[key] for key in V4_METRIC_ORDER}, warnings
