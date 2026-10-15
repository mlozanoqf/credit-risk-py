"""Prepare the frozen CLIMACRED source and calculate survival-weighted losses."""
from pathlib import Path
import numpy as np
import pandas as pd

SCENARIOS = {'DIRE':'Diverging Realities','HWTP':'Highway to Paris','SWUC':'Sudden Wake-up Call'}
METRICS = ['baseline_pd','pd_adjustment','corporate_bond_spread_adjustment',
           'corporate_bond_price_rel_adjustment','wacc_adjustment']


def portfolio_inputs():
    return pd.DataFrame(dict(
        portfolio_sector=['Coal','Oil','Gas','Power','Land transport','Air transport','Construction','Agriculture','Chemicals','Technology hardware'],
        ngfs_sector=['Coal','Oil','Gas','Power Supply','Land transport','Air transport','Construction','Agriculture','Chemical Products','Computer, electronic and optical products'],
        ead=np.array([10,12,10,12,10,8,10,8,10,10])*1e6,
        recovery=[.35,.4,.42,.45,.4,.35,.45,.35,.42,.5]))


def prepare_global(raw, portfolio):
    raw = raw.copy()
    raw[['metric','ngfs_sector']] = raw.variable.str.split('|',n=1,expand=True)
    selected = raw.merge(portfolio,on='ngfs_sector',validate='many_to_one')
    selected = selected[selected.scenario.isin(SCENARIOS)].copy()
    ids = ['scenario','year','portfolio_sector','ngfs_sector','ead','recovery']
    if selected.duplicated(ids+['metric']).any():
        raise ValueError('Duplicate scenario/year/sector/metric observations.')
    result = selected.pivot(index=ids,columns='metric',values='value').reset_index()
    if result[METRICS].isna().any().any():
        raise ValueError('Incomplete climate metrics.')
    result[METRICS] = result[METRICS]/100
    result['scenario_label'] = result.scenario.map(SCENARIOS)
    result['climate_pd'] = np.minimum(result.baseline_pd+result.pd_adjustment,1)
    result['lgd'] = 1-result.recovery
    if not result[['baseline_pd','climate_pd']].ge(0).all().all():
        raise ValueError('Negative PD requires explicit source review.')
    return result


def prepare_daps(raw):
    lookup = dict(zip(['DAPS_AFR_R','DAPS_ASIA','DAPS_EUR','DAPS_NAM','DAPS_OCE','DAPS_SAM'],
                      ['Africa','Asia','Euro Area','North America','Oceania','South America']))
    data = raw.copy()
    data[['metric','ngfs_sector']] = data.variable.str.split('|',n=1,expand=True)
    data['region_label'] = data.scenario.map(lookup)
    data = data[data.region==data.region_label].copy()
    data['pd_adjustment'] = data.value/100
    return data


def loss_steps(pd_path, ead, recovery, rate=.04):
    h = np.clip(np.asarray(pd_path),0,1)
    start = np.r_[1,np.cumprod(1-h)[:-1]]
    marginal = start*h
    discount = (1+rate)**(-np.arange(1,len(h)+1,dtype=float))
    return pd.DataFrame({'Conditional PD':h,'Survival at start':start,'Marginal PD':marginal,
                         'Discount factor':discount,'PV expected loss':ead*(1-recovery)*marginal*discount})


def horizon_losses(data):
    rows = []
    for (scenario,sector), group in data[data.year.between(2026,2030)].groupby(['scenario','portfolio_sector']):
        group = group.sort_values('year')
        assert group.year.tolist()==list(range(2026,2031))
        ead,recovery = group.iloc[0][['ead','recovery']]
        baseline = loss_steps(group.baseline_pd,ead,recovery)['PV expected loss'].sum()
        climate = loss_steps(group.climate_pd,ead,recovery)['PV expected loss'].sum()
        rows.append(dict(scenario=scenario,scenario_label=SCENARIOS[scenario],portfolio_sector=sector,
                         pv_el_baseline=baseline,pv_el_climate=climate,incremental_pv_el=climate-baseline))
    return pd.DataFrame(rows)
