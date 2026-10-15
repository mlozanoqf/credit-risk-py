"""Shared cleaning, design matrix and credit-policy calculations for Chapters 1-2."""
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd
import rdata
import statsmodels.api as sm
from sklearn.metrics import roc_auc_score, confusion_matrix, log_loss

NAMES = ['loan_st','l_amnt','int','grade','emp_len','home','income','age','sex','region']
DATA_MD5 = '1fbea5f14ec0c0174a946e010540b02f'


def load_data():
    path = Path('data/credit-scoring/credit_scoring.rds')
    if not path.is_file():
        raise FileNotFoundError('Restricted credit-scoring data are required. See data/credit-scoring/README.md.')
    if hashlib.md5(path.read_bytes()).hexdigest() != DATA_MD5:
        raise ValueError('This frozen split requires the reference dataset; checksum mismatch.')
    raw = rdata.read_rds(path)
    original_names = list(raw.columns)
    raw.columns = NAMES
    raw.index = np.arange(1,len(raw)+1)
    for col in ['loan_st','l_amnt','int','emp_len','income','age']:
        raw[col] = raw[col].astype(float)
    income_ok = raw.loc[raw.income<=1_000_000].copy()
    clean = income_ok.loc[income_ok.emp_len<=income_ok.age-16].copy()
    manifest = Path('data/credit-scoring/reference-split.csv')
    if not manifest.is_file():
        raise FileNotFoundError('The reference-split.csv supplied with authorized data is required.')
    split = pd.read_csv(manifest)
    ids = split.file_row.to_numpy()
    if len(ids)!=len(clean) or len(np.unique(ids))!=len(ids) or set(ids)!=set(clean.index):
        raise ValueError('Split membership does not match the cleaned data.')
    train = clean.loc[split.loc[split['split']=='train','file_row']].copy()
    test = clean.loc[split.loc[split['split']=='test','file_row']].copy()
    assert len(train)==20000 and len(test)==10000
    return raw, income_ok, clean, train, test, original_names


def design(frame, kind='full', intercept=True):
    """Explicit R treatment contrasts, preserving factor levels and column order."""
    parts = {}
    if intercept: parts['(Intercept)'] = np.ones(len(frame))
    if kind in ('age','multi','full'): parts['age'] = frame.age.to_numpy(float)
    if kind in ('int','multi','full'): parts['int'] = frame['int'].to_numpy(float)
    if kind in ('multi','full'):
        for level in frame.grade.cat.categories[1:]:
            parts['grade'+str(level)] = (frame.grade==level).to_numpy(float)
        parts['log(l_amnt)'] = np.log(frame.l_amnt.to_numpy(float))
        parts['log(income)'] = np.log(frame.income.to_numpy(float))
    if kind=='full':
        parts['emp_len'] = frame.emp_len.to_numpy(float)
        for col in ['home','sex','region']:
            for level in frame[col].cat.categories[1:]:
                parts[col+str(level)] = (frame[col]==level).to_numpy(float)
    return pd.DataFrame(parts,index=frame.index)


def fit_logistic(train,test):
    models, predictions = {},{}
    for name in ['age','int','multi','full']:
        x = design(train,name)
        models[name] = sm.GLM(train.loan_st.to_numpy(float),x,
                              family=sm.families.Binomial()).fit(tol=1e-10,maxiter=100)
        predictions[name] = np.asarray(models[name].predict(design(test,name)))
    return models,predictions


def policy(probability,actual,target,cost=5):
    p,y = np.asarray(probability),np.asarray(actual)
    cutoff = float(np.quantile(p,target,method='linear')) if target>0 else -np.inf
    accepted = p<=cutoff
    good,bad = int(np.sum(y[accepted]==0)),int(np.sum(y[accepted]==1))
    return dict(accept_rate=float(target),actual_accept_rate=float(accepted.mean()),
                cutoff=cutoff,accepted=int(accepted.sum()),accepted_good=good,
                accepted_defaults=bad,bad_rate=bad/accepted.sum() if accepted.any() else np.nan,
                net_payoff=good-cost*bad)


def strategy(p,y,grid=None,cost=5):
    if grid is None: grid = np.arange(50,100,5)/100
    return pd.DataFrame([policy(p,y,q,cost) for q in grid])


def calibration(p,y,file_rows):
    frame = pd.DataFrame({'predicted_pd':p,'actual':y,'file_row':file_rows})
    frame = frame.sort_values(['predicted_pd','file_row'],kind='stable')
    # dplyr::ntile uses equal-sized buckets even when predicted scores tie.
    frame['decile'] = np.repeat(np.arange(1,11),[len(x) for x in np.array_split(frame,10)])
    rows = []
    for decile,group in frame.groupby('decile'):
        rows.append(dict(risk_decile=int(decile),applications=len(group),
                         average_predicted_pd=group.predicted_pd.mean(),
                         observed_default_rate=group.actual.mean(),
                         brier_score=np.mean((group.predicted_pd-group.actual)**2)))
    return pd.DataFrame(rows)


def metrics(p,y):
    p,y = np.asarray(p),np.asarray(y)
    brier = np.mean((p-y)**2)
    baseline = np.mean((y.mean()-y)**2)
    return dict(auc=roc_auc_score(y,p),brier_score=brier,brier_skill=1-brier/baseline,
                min_pd=p.min(),max_pd=p.max(),log_loss=log_loss(y,p))


def classification(p,y,cutoff):
    tn,fp,fn,tp = confusion_matrix(y,np.asarray(p)>cutoff,labels=[0,1]).ravel()
    return dict(TN=int(tn),FP=int(fp),FN=int(fn),TP=int(tp),
                sensitivity=tp/(tp+fn),specificity=tn/(tn+fp),accuracy=(tn+tp)/len(y))


def cases(test,p,cutoff,positions):
    positions = np.asarray(positions)
    observed = test.loan_st.to_numpy(int)[positions]
    predicted = (np.asarray(p)[positions]>cutoff).astype(int)
    meanings = np.array([['Good loan accepted','Good applicant rejected'],
                         ['Defaulting borrower accepted','Default avoided']])
    return pd.DataFrame({'File row':test.index.to_numpy()[positions],
                         'Predicted PD':np.asarray(p)[positions],
                         'Predicted class':predicted,
                         'Decision':np.where(predicted,'Reject','Accept'),
                         'Observed outcome':np.where(observed,'Default','No default'),
                         'Credit consequence':meanings[observed,predicted]})


def display_frame(frame):
    labels = {'accept_rate':'Target acceptance','actual_accept_rate':'Actual acceptance',
              'cutoff':'PD cutoff','accepted':'Accepted applications','accepted_good':'Accepted good loans',
              'accepted_defaults':'Accepted defaults','bad_rate':'Bad rate','net_payoff':'Net payoff ($)',
              'risk_decile':'Predicted-risk decile','applications':'Applications',
              'average_predicted_pd':'Mean predicted PD','observed_default_rate':'Observed default rate',
              'brier_score':'Brier score','brier_skill':'Brier skill','auc':'AUC','model':'Model'}
    return frame.rename(columns=labels).round(6)
