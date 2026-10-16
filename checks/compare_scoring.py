"""Compare Python computations against explicitly exported, local R references."""
from pathlib import Path
import argparse
import json
import sys
import numpy as np
import pandas as pd
import xgboost as xgb
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from shared.scoring import load_data,design,metrics,policy,strategy,calibration


def read(path): return json.loads((ROOT/path).read_text(encoding='utf-8-sig'))


FOUNDATIONS_KEYS = tuple('''
total_exposure observed_defaults number_of_loans mean_exposure change_pp
relative_change change_bps segment_pd segment_weight overall_pd year1_pd
year2_conditional_pd survival_two_years cumulative_two_year_pd new_applicant_pd
loss_in_default expected_loss loan_el portfolio_el weighted_pd portfolio_el_check
exposure_weight mean_independent mean_together sd_independent sd_together
cdf_independent cdf_together q95_independent q95_together normal_threshold
normal_check central_probability odds score probability_check future_amount
present_value_check discount_factor payment_pv continuous_rate discount_discrete
discount_exponential bond_face bond_recovery bond_rf bond_price bond_q
bond_expected_payment bond_repriced bond_risk_free_price protection_payment
protection_from_prices protection_from_q standard_errors scenario_el
'''.split())
FOUNDATIONS_SIMULATION_KEYS = ('simulated_mean_loss', 'simulated_joint_pd')
FOUNDATIONS_MC_LIMIT = 4.0


def compare_foundations(python, reference):
    """Return separate deterministic and Monte Carlo diagnostics, or fail.

    R's unlabeled simulation records and Python's arrays both order independent
    loans first, perfectly joint loans second. Random streams need not match.
    """
    expected_keys = set(FOUNDATIONS_KEYS) | set(FOUNDATIONS_SIMULATION_KEYS)
    if set(python) != expected_keys:
        raise AssertionError(f'Foundations Python keys: missing {sorted(expected_keys-set(python))}, '
                             f'unexpected {sorted(set(python)-expected_keys)}')
    missing = set(FOUNDATIONS_KEYS) - set(reference)
    if missing:
        raise AssertionError(f'Foundations R keys missing: {sorted(missing)}')

    def numeric(value, name, shape=None):
        array = np.asarray(value, dtype=float)
        if not np.all(np.isfinite(array)) or (shape is not None and array.shape != shape):
            raise AssertionError(f'{name}: expected finite values with shape {shape}, got {array}')
        return array

    deterministic = []
    for key in FOUNDATIONS_KEYS:
        a = numeric(python[key], f'Foundations Python {key}')
        b = numeric(reference[key], f'Foundations R {key}', a.shape)
        row = {'Comparison': 'Foundations: '+key, 'Values': a.size,
               'Max absolute difference': float(np.max(np.abs(a-b))),
               'Tolerance met': bool(np.allclose(a, b, atol=1e-12, rtol=1e-12))}
        if not row['Tolerance met']:
            raise AssertionError(row)
        deterministic.append(row)

    records = reference.get('simulation_check')
    if not isinstance(records, list) or len(records) != 2 or not all(
            isinstance(row, dict) and all(key in row for key in (
                *FOUNDATIONS_SIMULATION_KEYS, 'exact_mean_loss', 'exact_joint_pd'))
            for row in records):
        raise AssertionError('Foundations R simulation_check: expected two complete records')
    if reference.get('n_scenarios') != 10000:
        raise AssertionError('Foundations simulations require n_scenarios=10000')

    n, loss, p = 10000, 5000, .1
    targets = {'simulated_mean_loss': np.array([2*loss*p, 2*loss*p]),
               'simulated_joint_pd': np.array([p*p, p])}
    # Var(loss sum) is 2*l^2*p*(1-p) for independence, 4*l^2*p*(1-p)
    # for perfectly joint defaults. Joint-frequency estimates are Bernoulli means.
    standard_errors = {
        'simulated_mean_loss': np.sqrt(np.array([2, 4])*loss**2*p*(1-p)/n),
        'simulated_joint_pd': np.sqrt(targets['simulated_joint_pd'] *
                                      (1-targets['simulated_joint_pd'])/n)}
    diagnostics = []
    for key in FOUNDATIONS_SIMULATION_KEYS:
        target, se = targets[key], standard_errors[key]
        exact_key = key.replace('simulated_', 'exact_')
        r_target = numeric([row[exact_key] for row in records], exact_key, (2,))
        if not np.allclose(r_target, target, atol=1e-12, rtol=1e-12):
            raise AssertionError(f'Foundations R {exact_key}: unexpected analytical targets')
        py = numeric(python[key], 'Foundations Python '+key, (2,))
        rr = numeric([row[key] for row in records], 'Foundations R '+key, (2,))
        for source, observed, expected, error in (
                ('Python vs analytical', py, target, se),
                ('R vs analytical', rr, target, se),
                ('Python minus R', py-rr, np.zeros(2), np.sqrt(2)*se)):
            for i, portfolio in enumerate(('independent', 'perfectly joint')):
                z = float((observed[i]-expected[i])/error[i])
                row = {'Comparison': f'Foundations MC: {source}: {portfolio}: {key}',
                       'Scenarios per run': n, 'Observed': float(observed[i]),
                       'Expected': float(expected[i]), 'Standard error': float(error[i]),
                       'Signed standard errors': z, 'SE limit': FOUNDATIONS_MC_LIMIT,
                       'Absolute tolerance': float(FOUNDATIONS_MC_LIMIT*error[i]),
                       'Tolerance met': abs(z) <= FOUNDATIONS_MC_LIMIT}
                if not row['Tolerance met']:
                    raise AssertionError(row)
                diagnostics.append(row)
    return deterministic, diagnostics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scoring-only', action='store_true',
                        help='Compare Chapters 1-2 without the separate Foundations reference.')
    args = parser.parse_args()
    results=[]
    foundations_mc=[]
    def exact(name,a,b,atol=1e-7,rtol=1e-7):
        a,b=np.asarray(a,float),np.asarray(b,float)
        assert a.shape==b.shape,(name,a.shape,b.shape)
        ok=bool(np.allclose(a,b,atol=atol,rtol=rtol,equal_nan=True))
        results.append({'Comparison':name,'Values':a.size,'Max absolute difference':float(np.nanmax(np.abs(a-b))),
                        'Tolerance met':ok})
        assert ok,(name,results[-1])
    if not args.scoring_only:
        r0=read('.local/00-foundations.json')
        p0=read('output/00-foundations/numeric-results.json')
        foundations,foundations_mc=compare_foundations(p0,r0)
        results.extend(foundations)
    r=read('.local/scoring-reference.json')
    r1=read('.local/01-logistic.json')
    r2=read('.local/02-tree-based.json')
    p1=read('output/01-logistic/numeric-results.json')
    p2=read('output/02-tree-based/numeric-results.json')
    configuration=read('.local/r-xgb-config.json')
    assert int(configuration['learner']['generic_param']['seed'])==1049419804
    _,_,_,train,test,_=load_data()
    y=test.loan_st.to_numpy(int)
    for sample,frame in [('train',train),('test',test)]:
        exact(sample+' row IDs',frame.index,r[sample+'_rows'],0,0)
        exact(sample+' encoded matrix',design(frame,intercept=False),r[sample+'_matrix'],1e-13,1e-13)
    for key in ['coefficients','standard_errors','p_values','aic','predictions']:
        for model in ['age','int','multi','full']:
            a,b=np.asarray(p1[key][model]),np.asarray(r[key][model])
            if key in ('standard_errors','p_values') and not np.allclose(a,b,atol=2e-6,rtol=2e-6):
                exact(f'Logistic {model}: {key}, tighter R convergence',a,r['tight_'+key][model],1e-9,1e-9)
                results[-1]['Original R max difference']=float(np.max(np.abs(a-b)))
                results[-1]['Reviewed cause']='Default glm convergence tolerance; stricter R agrees'
                if key=='p_values': assert np.array_equal(a<.05,b<.05)
            else:
                exact(f'Logistic {model}: {key}',a,b,atol=2e-6,rtol=2e-6)
    for name,frame in p1['calibration'].items():
        # Snapshot retains numeric columns only; R sorts full first, then age in its grouped rows.
        # Recompute from reference predictions to retain explicit model labels and ties.
        expected=calibration(r['predictions'][name],y,test.index)
        for col in expected:
            exact(f'Logistic {name}: decile {col}',frame[col],expected[col],atol=1e-7,rtol=1e-7)
    for row in p1['policies']:
        rp=np.asarray(r['predictions'][row['Model']])
        expected=policy(rp,y,row['accept_rate'])
        for col in expected: exact(f"Policy {row['Model']} {row['accept_rate']}: {col}",row[col],expected[col])
    for col in ['accept_rate','cutoff','accepted','accepted_good','accepted_defaults','bad_rate','net_payoff']:
        exact('Chapter 1 payoff: '+col,p1['payoff'][col],pd.DataFrame(r1['net_payoff_results'])[col])
    exact('Chapter 1 expected dollar loss',p1['expected_loss'],r1['el_expected_loss'])
    # Verify that newly recomputed R reference matches the saved book run.
    exact('R XGBoost rerun versus saved output',r['xgb'],r2['pred_xgb'],1e-10,1e-10)
    exact('R tree rerun versus saved output',r['tree'],r2['pred_tree_simple'],1e-12,1e-12)
    exported_model=xgb.Booster()
    exported_model.load_model(ROOT/'.local/r-xgb-reference.ubj')
    direct=exported_model.predict(xgb.DMatrix(design(test,intercept=False),nthread=1))
    exact('Same R-trained XGBoost model predicted in Python',direct,r['xgb'],1e-7,1e-7)
    summary=[]
    for model,py,rp in [('logi_full',p2['logistic_predictions'],r['predictions']['full']),
                        ('single_tree',p2['tree_predictions'],r['tree']),
                        ('xgboost',p2['xgb_predictions'],r['xgb'])]:
        py,rp=np.asarray(py),np.asarray(rp)
        pm,rm=metrics(py,y),metrics(rp,y)
        ps,rs=strategy(py,y),strategy(rp,y)
        pb,rb=ps.loc[ps.net_payoff.idxmax()],rs.loc[rs.net_payoff.idxmax()]
        pp,rpol=policy(py,y,.8),policy(rp,y,.8)
        summary.append(dict(Model=model,AUC_R=rm['auc'],AUC_Python=pm['auc'],AUC_difference=pm['auc']-rm['auc'],
            Brier_R=rm['brier_score'],Brier_Python=pm['brier_score'],
            Bad_rate_80_R=rpol['bad_rate'],Bad_rate_80_Python=pp['bad_rate'],
            Actual_acceptance_80_R=rpol['actual_accept_rate'],Actual_acceptance_80_Python=pp['actual_accept_rate'],
            Best_payoff_R=rb.net_payoff,Best_payoff_Python=pb.net_payoff,
            Best_target_R=rb.accept_rate,Best_target_Python=pb.accept_rate,
            Mean_absolute_PD_difference=float(np.mean(np.abs(py-rp))),Max_PD_difference=float(np.max(np.abs(py-rp))),
            Decisions_changed_80=int(np.sum((py<=pp['cutoff'])!=(rp<=rpol['cutoff'])))))
    frame=pd.DataFrame(summary)
    frame.to_csv(ROOT/'.local/scoring-comparison.csv',index=False)
    pd.DataFrame(results).to_csv(ROOT/'.local/deterministic-comparison.csv',index=False)
    print(f'{len(results)} deterministic groups passed; {sum(x["Values"] for x in results):,} values compared.')
    if foundations_mc:
        mc_frame=pd.DataFrame(foundations_mc)
        mc_frame.to_csv(ROOT/'.local/foundations-monte-carlo-comparison.csv',index=False)
        print(f'{len(foundations_mc)} Foundations Monte Carlo checks passed '
              f'(limit {FOUNDATIONS_MC_LIMIT:g} analytical standard errors).')
        print(mc_frame.to_string(index=False))
    print(frame.to_string(index=False))
    print('Tree leaves: R',r['tree_leaves'],'Python',p2['tree_leaves'])
    print('Random-score AUC: R',r1['auc_rand'],'Python',p1['random_auc'])
    print('XGBoost versions: R',r['xgb_version'])
    for model in ['logi_full','xgboost']:
        py=pd.DataFrame(p2['calibration'][model])
        rr=pd.DataFrame(r['calibration'])
        rr=rr[rr.model==model]
        out=pd.DataFrame({'Decile':py.risk_decile,'Mean_PD_R':rr.average_predicted_pd.to_numpy(),
            'Mean_PD_Python':py.average_predicted_pd,'Observed_rate_R':rr.observed_default_rate.to_numpy(),
            'Observed_rate_Python':py.observed_default_rate,'Brier_R':rr.brier_score.to_numpy(),'Brier_Python':py.brier_score})
        out.to_csv(ROOT/'.local'/f'{model}-decile-comparison.csv',index=False)


if __name__=='__main__': main()
