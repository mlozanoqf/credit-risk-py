"""Maintainer comparison of Python Chapters 4-6 against frozen/recomputed R."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import rdata
from scipy.integrate import quad
from scipy.stats import norm, binom

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from shared.portfolio import expected_shortfall


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--r-root',type=Path,default=ROOT.parent/'credit-risk-r')
    refroot = parser.parse_args().r_root
    checks = []
    def same(name,a,b,atol=1e-8,rtol=1e-9):
        a,b = np.asarray(a,dtype=float),np.asarray(b,dtype=float)
        assert a.size==b.size,(name,a.shape,b.shape)
        a,b = a.ravel(),b.ravel()
        delta = np.abs(a-b)
        ok = bool(np.allclose(a,b,atol=atol,rtol=rtol))
        checks.append(dict(check=name,n=a.size,max_difference=float(delta.max()),pass_check=ok))
    def probability(name,a,b,n):
        a,b = np.asarray(a),np.asarray(b)
        se = np.sqrt((a*(1-a)+b*(1-b))/n)
        limit = 5*se+2/n
        checks.append(dict(check=name,n=a.size,max_difference=float(np.abs(a-b).max()),
            pass_check=bool(np.all(np.abs(a-b)<=limit))))
    def snapshot(id):
        return json.loads((ROOT/'output'/id/'numeric-results.json').read_text())
    p4,p5,p6 = [snapshot(id) for id in ['04-credit-spreads-cds','05-copulas','06-climate-credit-risk']]
    r4,r5,r6 = [rdata.read_rds(refroot/'output'/id/'numeric-results.rds') for id in ['04-credit-spreads-cds','05-copulas','06-climate-credit-risk']]
    details4 = json.loads((ROOT/'.local/04-credit-spreads-cds-reference.json').read_text())
    details6 = json.loads((ROOT/'.local/06-climate-credit-risk-reference.json').read_text())
    for folder in ['credit-spreads','climate']:
        for file in (ROOT/'data'/folder).glob('*.csv'):
            assert hashlib.sha256(file.read_bytes()).digest()==hashlib.sha256((refroot/'data'/folder/file.name).read_bytes()).digest(),file
    for name in ['pd_merton','market_value_debt','merton_implied_spread','zero_risk_free_price','zero_risky_price',
        'zero_risky_yield','zero_spread','coupon_risk_free_price','coupon_risky_price','coupon_risky_yield','coupon_spread',
        'merton_cds_spread','merton_cds_reference_recovery','merton_cds_reference_spread','cds_exact_spread',
        'hull_mtm_seller','hull_implied_hazard','brazil_yield','brazil_spread','brazil_h','brazil_pd_maturity',
        'brazil_repriced','brazil_no_default_price','brazil_price_at_reported_yield','brazil_time','brazil_coupons',
        'brazil_promised','brazil_h_values','rv_call_yields']:
        same('4/'+name,p4[name],r4[name],atol=1e-7)
    for name in ['example_sched','hull_schedule','cds_timing_results']:
        p = pd.DataFrame(p4[name]); r = r4[name]
        same('4/'+name,p[r.columns],r)
    same('4/hull components',list(p4['hull_components'].values()),[details4['hull_components'][k] for k in p4['hull_components']])
    cs = pd.DataFrame(p4['coupon_sensitivity']).rename(columns={'yield_value':'yield'})
    same('4/coupon sensitivity',cs[r4['coupon_sensitivity'].columns],r4['coupon_sensitivity'],atol=1e-7)
    same('4/CDS sensitivity',p4['hull_cds_sensitivity'],r4['hull_cds_sensitivity'])
    for name in ['all_bond_yields','all_accrued','all_dv01']:
        same('4/'+name,p4[name],details4[name])
    same('4/issuer endpoints',p4['rv_fitted_h'],details4['h'],atol=1e-6)
    pycomp = pd.DataFrame(p4['rv_comparison'])
    rcomp = pd.DataFrame(details4['comparison'])
    for col in ['mark','model_price','market_yield','model_yield','residual_bp','price_gap']:
        same('4/relative value '+col,pycomp[col],rcomp[col],atol=.002 if col=='residual_bp' else 2e-5)
    for name in ['rv_all_residuals','rv_rmse','rv_advantage','rv_purchase_limit','rv_deduction']:
        same('4/'+name,p4[name],r4[name],atol=.002 if name in ['rv_all_residuals','rv_rmse','rv_advantage'] else 2e-5)
    same('4/sensitivity extrema',p4['rv_sensitivity_ranges'],r4['rv_sensitivity_summary'],atol=.002)
    pyrv = pd.DataFrame(p4['rv_sensitivity_all'])
    for issuer,records in zip(['CCO','Verizon'],details4['sensitivity']):
        r = pd.DataFrame(records)
        p = pyrv[pyrv.issuer==issuer].merge(r,on=['recovery','shift','weight','timing'],suffixes=('_py','_r'),validate='one_to_one')
        same('4/all sensitivity fits '+issuer,p.residual_py,p.residual_r,atol=.002)
    same('4/zero curve',p4['rv_curve_zero'],r4['rv_curve_plot']['zero'])
    same('4/Brazil fixed PD prices',p4['brazil_fixed_prices'],r4['brazil_sensitivity']['price_at_fixed_h'])
    for key in ['pd_cum','default_threshold','pd_incremental','threshold_check','loss_expected_theoretical',
                'credit_var_rate','credit_var_loss','credit_expected_loss']:
        same('5/'+key,p5[key],r5[key])
    probability('5/one-firm PD',p5['one_firm_sim_pd'],np.asarray(r5['one_firm_sim_pd'])[0],100000)
    two = pd.DataFrame(p5['two_firm'])
    probability('5/two-firm events',two.iloc[:,1:5],r5['two_firm_numeric'].iloc[:,1:5],100000)
    for rho,pjoint in zip(two.rho,two['P(A and B)']):
        z = norm.ppf(.15)
        exact = quad(lambda x:norm.pdf(x)*norm.cdf((z-rho*x)/np.sqrt(1-rho*rho)),-10,z,epsabs=1e-12)[0]
        assert abs(pjoint-exact)<5*np.sqrt(exact*(1-exact)/100000)+2/100000
    for key in ['count_probability_matrix','tcopula_count_matrix']:
        probability('5/'+key,p5[key],np.asarray(r5[key]),100000)
    # Independently integrate the Gaussian count distribution, including rho=0.
    for j,rho in enumerate([0,.2,.5]):
        exact = np.array([binom.pmf(k,10,.15) if rho==0 else quad(
            lambda f:binom.pmf(k,10,norm.cdf((norm.ppf(.15)-np.sqrt(rho)*f)/np.sqrt(1-rho)))*norm.pdf(f),
            -10,10,epsabs=1e-10)[0] for k in range(11)])
        estimate = np.asarray(p5['count_probability_matrix'])[:,j]
        assert np.all(np.abs(estimate-exact)<=5*np.sqrt(exact*(1-exact)/100000)+2/100000)
    p6cl = pd.DataFrame(p6['climate_credit']).sort_values(['scenario','portfolio_sector','year'])
    r6cl = pd.DataFrame(details6['climate_credit']).sort_values(['scenario','portfolio_sector','year'])
    numeric = ['year','ead','recovery','baseline_pd','pd_adjustment','climate_pd','corporate_bond_spread_adjustment',
               'corporate_bond_price_rel_adjustment','wacc_adjustment','lgd']
    assert p6cl[['scenario','portfolio_sector','year']].to_numpy().tolist()==r6cl[['scenario','portfolio_sector','year']].to_numpy().tolist()
    same('6/clean climate data',p6cl[numeric],r6cl[numeric])
    for name,keys,cols in [
        ('horizon_loss',['scenario','portfolio_sector'],['pv_el_baseline','pv_el_climate','incremental_pv_el']),
        ('portfolio_horizon_loss',['scenario_label'],['pv_el_baseline','pv_el_climate','incremental_pv_el','increase']),
        ('spread_bridge',['scenario','portfolio_sector'],['default_loss_change_bps','ngfs_spread_bps','spread_gap_bps'])]:
        p = pd.DataFrame(p6[name]).sort_values(keys)
        r = pd.DataFrame(details6[name]).rename(columns={'baseline_pv_el':'pv_el_baseline','climate_pv_el':'pv_el_climate'}).sort_values(keys)
        same('6/'+name,p[cols],r[cols],atol=1e-7)
    daps = pd.DataFrame(p6['daps_summary']).melt(id_vars='region_label',var_name='ngfs_sector',value_name='max_pd_adjustment')
    r = pd.DataFrame(details6['daps_summary'])
    keys = ['region_label','ngfs_sector']
    same('6/physical-risk regional maxima',daps.sort_values(keys).max_pd_adjustment,r.sort_values(keys).max_pd_adjustment)
    coal = pd.DataFrame(p6['coal_steps'])
    for col,key in [('Survival at start','coal_survival'),('Marginal PD','coal_marginal'),('PV expected loss','coal_pv')]:
        same('6/coal '+key,coal[col],details6[key],atol=1e-7)
    # Compare simulation means, ES and quantiles with sampling-aware diagnostics.
    simulations = []
    def mean_es_quantiles(name,p,r,alpha):
        p,r = np.asarray(p).ravel(),np.asarray(r).ravel()
        for metric in ['Mean','ES']:
            if metric=='Mean':
                pv,rv = p.mean(),r.mean()
                pse,rse = p.std(ddof=1)/np.sqrt(len(p)),r.std(ddof=1)/np.sqrt(len(r))
            else:
                pv,rv = expected_shortfall(p,alpha),expected_shortfall(r,alpha)
                pex = np.maximum(p-np.quantile(p,alpha,method='inverted_cdf'),0)
                rex = np.maximum(r-np.quantile(r,alpha,method='inverted_cdf'),0)
                pse,rse = pex.std(ddof=1)/((1-alpha)*np.sqrt(len(p))),rex.std(ddof=1)/((1-alpha)*np.sqrt(len(r)))
            se = np.hypot(pse,rse)
            z = abs(pv-rv)/se if se else 0
            simulations.append(dict(case=name,metric=metric,R=rv,Python=pv,difference=pv-rv,combined_se=se,z=z,pass_check=z<=5))
        def interval(x):
            delta = 4.5*np.sqrt(alpha*(1-alpha)/len(x))
            return np.quantile(x,[max(0,alpha-delta),min(1,alpha+delta)],method='inverted_cdf')
        pi,ri = interval(p),interval(r)
        overlap = max(pi[0],ri[0])<=min(pi[1],ri[1])
        simulations.append(dict(case=name,metric=f'VaR {alpha}',R=np.quantile(r,alpha,method='inverted_cdf'),
            Python=np.quantile(p,alpha,method='inverted_cdf'),difference=np.quantile(p,alpha,method='inverted_cdf')-np.quantile(r,alpha,method='inverted_cdf'),
            combined_se=None,z=None,pass_check=overlap))
    sim5 = np.load(ROOT/'output/05-copulas/simulation-losses.npz')
    for pkey,rkey in [('vasicek','vasicek_loss'),('gaussian','credit_gaussian_sim_loss'),('t10','credit_t10_sim_loss'),
                      ('t4','credit_t4_sim_loss'),('equal','loss_equal'),('concentrated','loss_concentrated')]:
        mean_es_quantiles('5/'+pkey,sim5[pkey],r5[rkey],.999)
    sim6 = np.load(ROOT/'output/06-climate-credit-risk/simulation-losses.npz')
    rloss = np.asarray(r6['simulated_losses']['loss'])
    for i,key in enumerate(['baseline','climate']):
        mean_es_quantiles('6/'+key,sim6[key],rloss[i*50000:(i+1)*50000],.95)
        estimate = sim6[key].mean(); se = sim6[key].std(ddof=1)/np.sqrt(50000)
        assert abs(estimate-p6['analytic_one_year_el'][i])<5*se
    for j,label in enumerate(['Gaussian ES','t(4) ES','ES difference']):
        p = np.asarray(p5['credit_tail_repeats'])[:,j]
        r = np.asarray(r5['credit_tail_repeats'])[:,j]
        combined = np.hypot(p.std(ddof=1)/np.sqrt(len(p)),r.std(ddof=1)/np.sqrt(len(r)))
        z = abs(p.mean()-r.mean())/combined
        simulations.append(dict(case='5/repeats',metric=label,R=r.mean(),Python=p.mean(),difference=p.mean()-r.mean(),combined_se=combined,z=z,pass_check=z<=5))
    check_frame = pd.DataFrame(checks)
    sim_frame = pd.DataFrame(simulations)
    check_frame.to_csv(ROOT/'.local/portfolio-deterministic-checks.csv',index=False)
    sim_frame.to_csv(ROOT/'.local/portfolio-simulation-checks.csv',index=False)
    print(check_frame.to_string(index=False))
    print(sim_frame.to_string(index=False))
    assert check_frame.pass_check.all(),check_frame[~check_frame.pass_check]
    assert sim_frame.pass_check.all(),sim_frame[~sim_frame.pass_check]
    assert p4['rv_advantage']>0 and min(np.asarray(p4['rv_sensitivity_ranges'])[:,0])>0
    assert p5['tail_precision_mean'][2]>0
    print(f'PASS: {len(checks)} deterministic/distribution checks; {len(simulations)} sampling diagnostics.')


if __name__=='__main__':
    main()
