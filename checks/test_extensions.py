from pathlib import Path
import sys
import importlib.util
import re
import numpy as np
import pandas as pd
from scipy.stats import norm
sys.path.insert(0, str(Path.cwd()))
from shared.scoring import load_data, design
from shared.portfolio import latent_scores
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
helper = load('chapters/02-tree-based/helpers/new_applicants.py', 'new_applicants')
_, _, _, train, test, _ = load_data()
encode = helper.make_xgb_encoder(train, design(train, intercept=False).columns)
one = test.drop(columns='loan_st').iloc[[0]].copy()
for field in ('grade', 'home', 'sex', 'region'):
    one[field] = one[field].astype(str)
np.testing.assert_array_equal(encode(one).to_numpy(), design(test, intercept=False).iloc[[0]].to_numpy())
np.testing.assert_array_equal(encode(test.iloc[:100]).to_numpy(), design(test, intercept=False).iloc[:100].to_numpy())
def bad(function):
    try: function()
    except (ValueError, KeyError): return
    raise AssertionError('Invalid input was accepted')
for field, value in [('grade', 'Z'), ('region', 'UNKNOWN'), ('home', None), ('income', 0), ('age', np.inf)]:
    case = one.copy(); case[field] = value
    bad(lambda: encode(case))
bad(lambda: encode(one.drop(columns='home')))
print('Python incoming-applicant encoding PASS')
source = Path('chapters/05-copulas/chapter.qmd').read_text(encoding='utf-8')
body = next(x for x in re.findall(r'```\{python\}\s*\n(.*?)\n```', source, re.S) if x.startswith('borrowers = pd.DataFrame'))
exec(body)
assert hetero_el == 1_820_000
assert abs(hetero_el-hetero_mean) < 5*hetero_mcse
se = np.sqrt(borrowers['pd']*(1-borrowers['pd'])/len(hetero_defaults))
assert ((hetero_defaults.mean()-borrowers['pd']).abs() < 5*se).all()
cols = ['C', 'A', 'B']
np.testing.assert_array_equal(hetero_defaults[cols].to_numpy() @ loss_if_default.loc[cols].to_numpy(), hetero_losses)
print('Python heterogeneous mean, marginals and borrower alignment PASS')
sys.path.insert(0, str(Path('chapters/06-climate-credit-risk/helpers').resolve()))
from climate import prepare_global, portfolio_inputs, SCENARIOS, METRICS
from validation import validate_climate_inputs, validate_climate_portfolio
raw = pd.read_csv('data/climate/ngfs_climacred_global_raw.csv')
portfolio = portfolio_inputs()
def validate(data=raw, p=portfolio):
    validate_climate_inputs(data, p, list(SCENARIOS), range(2022, 2031), METRICS)
validate()
for data in (raw.iloc[1:], pd.concat([raw,raw.iloc[[0]]]), raw[raw.year!=2029], raw[raw.scenario!='HWTP']):
    bad(lambda: validate(data))
case = portfolio.copy(); case.loc[0, 'ngfs_sector'] = 'Missing sector'
bad(lambda: validate(p=case))
case = raw.copy(); case.loc[0, 'unit'] = 'fraction'; bad(lambda: validate(case))
case = raw.copy(); case.loc[0, 'value'] = np.inf; bad(lambda: validate(case))
data = prepare_global(raw, portfolio)
totals = validate_climate_portfolio(data, portfolio, list(SCENARIOS), range(2022, 2031))
assert len(totals)==27 and (totals.ead==1e8).all()
for field, value in [('climate_pd', -.1), ('baseline_pd', 1.01), ('ead', 1)]:
    case = data.copy(); case.loc[0,field] = value
    bad(lambda: validate_climate_portfolio(case, portfolio, list(SCENARIOS), range(2022, 2031)))
print('Python climate coverage, units, duplicates and PD checks PASS')
