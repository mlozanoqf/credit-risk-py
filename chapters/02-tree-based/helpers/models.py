"""Python CART and XGBoost fits with explicit, documented settings."""
import numpy as np
import pandas as pd
import xgboost as xgb
from scipy.special import expit,logit
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import roc_auc_score,log_loss
from shared.scoring import design


def fit_tree_models(train,test):
    xtrain,xtest = design(train,intercept=False),design(test,intercept=False)
    ytrain,ytest = train.loan_st.to_numpy(int),test.loan_st.to_numpy(int)
    # rpart's relative misclassification cp has no direct sklearn alpha equivalent.
    # Use depth/sample restrictions and disclose the absence of cp pruning.
    tree = DecisionTreeClassifier(criterion='gini',max_depth=4,min_samples_split=100,
                                  min_samples_leaf=33,ccp_alpha=0,random_state=567)
    tree.fit(xtrain,ytrain)
    dtrain = xgb.DMatrix(xtrain,label=ytrain,nthread=1)
    dtest = xgb.DMatrix(xtest,label=ytest,nthread=1)
    params = dict(objective='binary:logistic',eval_metric=['logloss','auc'],
                  max_depth=3,eta=.05,subsample=.8,colsample_bytree=.8,
                  min_child_weight=20,reg_lambda=1,base_score=float(ytrain.mean()),
                  seed=1049419804,nthread=1,tree_method='hist')
    history = {}
    booster = xgb.train(params,dtrain,num_boost_round=160,
                        evals=[(dtrain,'train'),(dtest,'test')],
                        evals_result=history,verbose_eval=False)
    return tree,booster,dtrain,dtest,xtrain,xtest,params,history


def leaf_rules(tree,feature_names):
    rows = []
    t = tree.tree_
    def visit(node,path):
        left,right = t.children_left[node],t.children_right[node]
        if left==right:
            weights = t.value[node][0]
            rows.append({'Leaf':int(node),'Rule':' and '.join(path),
                         'Training loans':int(t.n_node_samples[node]),
                         'Training PD':float(weights[1]/weights.sum())})
            return
        f,cut = feature_names[t.feature[node]],t.threshold[node]
        visit(left,path+[f'{f} <= {cut:.4f}'])
        visit(right,path+[f'{f} > {cut:.4f}'])
    visit(0,[])
    return pd.DataFrame(rows)


def checkpoint_paths(booster,dtest,y,base_pd):
    rounds = [0,1,2,3,4,5,20,60,100,160]
    scores = np.column_stack([np.repeat(logit(base_pd),len(y))]+[
        booster.predict(dtest,output_margin=True,iteration_range=(0,r)) for r in rounds[1:]])
    probabilities = expit(scores)
    loss = lambda p: -(y*np.log(np.clip(p,1e-8,1-1e-8))+
                           (1-y)*np.log1p(-np.clip(p,1e-8,1-1e-8)))
    gain = loss(np.repeat(base_pd,len(y)))-loss(probabilities[:,-1])
    # Match R's illustrative selection using its checkpoint grid.
    grid = [rounds.index(r) for r in [0,5,20,60,100,160]]
    move = np.abs(np.diff(scores[:,grid],axis=1)).sum(axis=1)
    chosen = []
    for mask in [(y==1)&(probabilities[:,-1]>base_pd),(y==0)&(probabilities[:,-1]<base_pd)]:
        candidates = np.flatnonzero(mask)
        if not len(candidates): raise ValueError('No applicant satisfies the illustrative case rule.')
        chosen.append(int(candidates[np.argmax((gain+.05*move)[candidates])]))
    return rounds,scores,probabilities,chosen


def contributions(booster,dtest):
    shap = booster.predict(dtest,pred_contribs=True)
    margin = booster.predict(dtest,output_margin=True)
    np.testing.assert_allclose(shap.sum(axis=1),margin,atol=5e-6,rtol=2e-6)
    return shap


def partial_dependence(booster,test):
    rows = []
    for variable in ['int','income','age']:
        grid = np.linspace(*np.quantile(test[variable],[.05,.95],method='linear'),40)
        for value in grid:
            modified = test.copy()
            modified[variable] = value
            matrix = xgb.DMatrix(design(modified,intercept=False),nthread=1)
            rows.append({'variable':variable,'value':value,
                         'average_predicted_pd':float(booster.predict(matrix).mean())})
    return pd.DataFrame(rows)
