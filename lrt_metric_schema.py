"""Versioned LRT candidate schema; historical report fields remain readable.

51 exported fields = 3 x 16 geometry metrics + 2 delivery + 1 reference.
PR_System is a reference, excluded from the default 50-feature geometry pool
because PR_Eff reproduces it on the supported report geometry.
"""
SCHEMA_VERSION = 'lrt-three-layer-v1'
BASE_METRICS = {
    'MCSv': 'mcsv', 'LSV': 'lsv', 'AAV': 'aav', 'PA': 'pa',
    'MAD': 'mad', 'ALG': 'alg', 'SLG': 'alg_sd', 'SAS5': 'sas_5mm',
    'SAS10': 'sas_10mm', 'SAS20': 'sas_20mm', 'LT': 'lt',
    'LTmean': 'lt_mean_leaf', 'NL': 'nl_pairs',
}
LAYERS = {'Eff': 'effective', 'D': 'mlcx1', 'P': 'mlcx2'}
GEOMETRY_KEYS = tuple(f'{name}_{layer}' for layer in LAYERS
                      for name in (*BASE_METRICS, 'PI', 'PM', 'PR'))
DELIVERY_KEYS = ('MU', 'MU_per_CP')
REFERENCE_KEYS = ('PR_System',)
EXPORT_KEYS = GEOMETRY_KEYS + DELIVERY_KEYS + REFERENCE_KEYS
CANDIDATE_KEYS = GEOMETRY_KEYS + DELIVERY_KEYS
EXCLUDED_HISTORICAL_KEYS = ('ethos_sas10', 'ethos_one_minus_mcs')
LEGACY_MAP = {f'{name}_{layer}': f'{old}_{suffix}'
              for layer, suffix in LAYERS.items() for name, old in BASE_METRICS.items()}
LEGACY_MAP.update({'PI_Eff': 'pi5', 'PM_Eff': 'pm5',
                   'PI_D': 'pi_mlcx1', 'PI_P': 'pi_mlcx2',
                   'PM_D': 'pm_mlcx1', 'PM_P': 'pm_mlcx2',
                   'PR_System': 'ethos_penumbra_ratio', 'MU': 'mus'})
# Public paper labels are accepted only by explicit callers. Historical model
# keys are never rewritten or filled from a different PR feature.
PUBLIC_ALIASES = {key.replace('_', '-'): key for key in GEOMETRY_KEYS}

FORMULAS = {
    'MCSv': 'sum_i d_i * mean(AAV_i,AAV_i+1) * mean(LSV_i,LSV_i+1) / sum_i d_i',
    'AAV': '<A_i/E>_c; E = sum_slot (max_CP right-min_CP left)_+ * max_CP exposed_height',
    'LSV': '<LSV_i>_c; each bank = 1-sum_adjacent(abs(dx))/((N-1)*range); multiply banks',
    'PA': '<A_i>_c, A_i = sum_j jaw-clipped positive gap * exposed strip height',
    'MAD': '<mean_active_slot abs((left+right)/2)>_c; omit empty CPs',
    'ALG': '<mean_active_slot(right-left)>_c; omit empty CPs',
    'SLG': 'sqrt(<mean_active_slot(gap-ALG_beam)^2>_c); omit empty CPs; beam-MU mean of beam SDs',
    'SAS5': '<count(0<raw_gap<5 mm)/count(raw_gap>0)>_c; omit empty CPs',
    'SAS10': '<count(0<raw_gap<10 mm)/count(raw_gap>0)>_c; omit empty CPs',
    'SAS20': '<count(0<raw_gap<20 mm)/count(raw_gap>0)>_c; omit empty CPs',
    'LT': 'sum_interval d_i * sum_leaf abs(x_i+1-x_i) / sum_interval d_i',
    'LTmean': 'sum_leaf raw trajectory travel / count(moving leaves); unweighted intervals',
    'NL': '<count(raw_gap>0 and Y jaw overlap>0)>_c',
    'PI': '<P_i^2/(4*pi*A_i)>_c; zero area contributes 0',
    'PM': '1-<A_i>_c/U; U=sum_slot max_CP(jaw-clipped slot area); U=0 => 0',
    'PR': '<1-C_i/A_open_i>_c; finite tip 2.8 mm, exposed side 2.3 mm; gap>0.5+1e-8 mm',
    'MU': 'sum_beam MU_beam',
    'MU_per_CP': 'sum_beam MU_beam / sum_beam N_CP (includes both endpoints)',
    'PR_System': 'Unchanged legacy ethos_penumbra_ratio value; report-profile reconstruction, not a newly observed TPS value',
}
UNITS = {'PA': 'mm^2', 'MAD': 'mm', 'ALG': 'mm', 'SLG': 'mm', 'LT': 'mm',
         'LTmean': 'mm/moving leaf (Eff: virtual leaf)', 'NL': 'active pairs (Eff: virtual pairs)',
         'MU': 'MU', 'MU_per_CP': 'MU/CP'}


def metric_base(key):
    return key.rsplit('_', 1)[0] if key in GEOMETRY_KEYS else key


def metric_group(key):
    return ('LRT ' + key.rsplit('_', 1)[1] if key in GEOMETRY_KEYS else
            'LRT System reference' if key in REFERENCE_KEYS else 'LRT Delivery')


def select_candidates(values, *, include_system_reference=False):
    """Fail on missing fields; never substitute System PR with geometry PR."""
    keys = EXPORT_KEYS if include_system_reference else CANDIDATE_KEYS
    missing = set(keys) - set(values)
    if missing:
        raise KeyError(f'Missing {SCHEMA_VERSION} fields: {sorted(missing)}')
    return {key: values[key] for key in keys}
