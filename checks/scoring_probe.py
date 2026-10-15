"""Maintainer preflight. R outputs are read only for comparison, never for fitting."""
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from shared.scoring import load_data,fit_logistic,design,metrics,policy,strategy
spec=importlib.util.spec_from_file_location('trees',ROOT/'chapters/02-tree-based/helpers/models.py')
trees=importlib.util.module_from_spec(spec); spec.loader.exec_module(trees)
_,_,_,tr,te,_=load_data()
reference=json.loads((ROOT/'.local/scoring-reference.json').read_text())
models,pred=fit_logistic(tr,te)
for kind in ['train','test']:
    matrix=design(tr if kind=='train' else te,intercept=False)
    assert list(matrix.columns)==reference['columns']
    np.testing.assert_allclose(matrix,reference[kind+'_matrix'],atol=1e-13,rtol=1e-13)
for k,m in models.items():
    print(k,'coefficient max difference',np.max(np.abs(m.params-np.asarray(reference['coefficients'][k]))),
          'PD max difference',np.max(np.abs(pred[k]-reference['predictions'][k])))
tree,booster,dt,ds,xt,xs,params,history=trees.fit_tree_models(tr,te)
pred.update(single_tree=tree.predict_proba(xs)[:,1],xgboost=booster.predict(ds))
rows=[]
for key,rkey in [('full','logi_full'),('single_tree','single_tree'),('xgboost','xgboost')]:
    r=next(r for r in reference['model_metrics'] if r['model']==rkey)
    py=metrics(pred[key],te.loan_st)
    p80=policy(pred[key],te.loan_st,.8)
    best=strategy(pred[key],te.loan_st).sort_values('net_payoff',ascending=False).iloc[0]
    rows.append(dict(model=key,auc_R=r['auc'],auc_Python=py['auc'],brier_R=r['brier_score'],
                     brier_Python=py['brier_score'],bad_rate_80=p80['bad_rate'],
                     best_payoff=best.net_payoff,best_target=best.accept_rate))
frame=pd.DataFrame(rows)
print(frame.to_string(index=False))
print('Python leaves',tree.get_n_leaves(),'R leaves',reference['tree_leaves'])
frame.to_csv(ROOT/'.local/scoring-preflight.csv',index=False)
