"""Validate complete scenario coverage before aggregating portfolio losses."""
import numpy as np
import pandas as pd

UNITS = {
    'baseline_pd': 'value/level in percentage points',
    'pd_adjustment': 'abs. change in value with respect to BAU in percentage points',
    'corporate_bond_spread_adjustment': 'abs. change in value with respect to BAU in percentage points',
    'corporate_bond_price_rel_adjustment': 'relative change with respect to BAU in percents',
    'wacc_adjustment': 'abs. change in value with respect to BAU in percentage points',
}


def validate_climate_inputs(raw, portfolio, scenarios, years, metrics):
    required = ['model', 'region', 'scenario', 'year', 'variable', 'unit', 'value']
    if not set(required).issubset(raw.columns):
        raise ValueError('Missing raw climate fields.')
    fields = ['ngfs_sector', 'portfolio_sector', 'ead', 'recovery']
    if not set(fields).issubset(portfolio.columns):
        raise ValueError('Incomplete portfolio columns.')
    if (portfolio.empty or portfolio[fields].isna().any().any()
            or portfolio.ngfs_sector.duplicated().any()
            or portfolio.portfolio_sector.duplicated().any()
            or (portfolio[['ngfs_sector', 'portfolio_sector']] == '').any().any()
            or not np.isfinite(portfolio[['ead', 'recovery']]).all().all()
            or (portfolio.ead < 0).any() or portfolio.ead.sum() <= 0
            or not portfolio.recovery.between(0, 1).all()):
        raise ValueError('Review portfolio identifiers, exposures and recoveries.')
    variables = [f'{metric}|{sector}' for sector in portfolio.ngfs_sector for metric in metrics]
    selected = raw[raw.scenario.isin(scenarios) & raw.year.isin(years)
                   & raw.variable.isin(variables)].copy()
    if (selected[required].isna().any().any()
            or not (selected.model == 'CLIMACRED').all()
            or not (selected.region == 'World').all()
            or not np.isfinite(selected.value).all()):
        raise ValueError('Review model, region and finite raw values.')
    keys = ['scenario', 'year', 'variable']
    if selected.duplicated(keys).any():
        raise ValueError('Duplicate climate observations.')
    expected = pd.MultiIndex.from_product([scenarios, years, variables], names=keys)
    present = pd.MultiIndex.from_frame(selected[keys])
    if len(expected.difference(present)):
        raise ValueError('Missing sector/scenario/year/metric observations; reconcile mapping.')
    expected_units = selected.variable.str.split('|', n=1).str[0].map(UNITS)
    if expected_units.isna().any() or not selected.unit.eq(expected_units).all():
        raise ValueError('Source units changed; review conversion before proceeding.')


def validate_climate_portfolio(data, portfolio, scenarios, years):
    keys = ['scenario', 'year', 'ngfs_sector']
    expected = pd.MultiIndex.from_product([scenarios, years, portfolio.ngfs_sector], names=keys)
    if data[keys].isna().any().any() or data.duplicated(keys).any() or len(data) != len(expected):
        raise ValueError('Transformed portfolio grid incomplete or duplicated.')
    aligned = data.set_index(keys).reindex(expected)
    fields = ['baseline_pd', 'pd_adjustment', 'climate_pd', 'recovery', 'ead']
    if (not np.isfinite(aligned[fields]).all().all()
            or not aligned.baseline_pd.between(0, 1).all()
            or not aligned.climate_pd.between(0, 1).all()
            or (aligned.baseline_pd + aligned.pd_adjustment < 0).any()):
        raise ValueError('Invalid PD or loss inputs; review source and units.')
    original = portfolio.set_index('ngfs_sector')
    sectors = aligned.index.get_level_values('ngfs_sector')
    for field in ('ead', 'recovery'):
        if not np.array_equal(aligned[field].to_numpy(), original.loc[sectors, field].to_numpy()):
            raise ValueError('Exposure or recovery changed during the join.')
    totals = aligned.groupby(level=['scenario', 'year']).ead.sum().reset_index()
    if not np.allclose(totals.ead, portfolio.ead.sum(), rtol=1e-8, atol=0):
        raise ValueError('Represented exposure differs from specified portfolio.')
    return totals
