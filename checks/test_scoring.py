"""Financial and computational invariants; reference input data are required."""
import importlib.util
from pathlib import Path
import sys
import unittest
import numpy as np
import xgboost as xgb
from scipy.special import expit,logit
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from shared.scoring import load_data,fit_logistic,design,policy,calibration,classification


class PolicyTests(unittest.TestCase):
    def test_quantile_ties(self):
        p=np.array([.1,.1,.1,.9]); y=np.array([0,0,1,1])
        r=policy(p,y,.5)
        self.assertEqual(r['actual_accept_rate'],.75)
        self.assertEqual(r['accepted_defaults'],1)
        self.assertEqual(r['net_payoff'],-3)
        self.assertEqual(policy(p,y,0)['accepted'],0)
        self.assertEqual(policy(p,y,1)['accepted'],4)

    def test_decile_ties(self):
        p=np.repeat(.1,20); y=np.tile([0,1],10)
        t=calibration(p,y,np.arange(20)[::-1])
        self.assertEqual(t.applications.sum(),20)
        self.assertTrue((t.applications==2).all())
        self.assertAlmostEqual(t.brier_score.mean(),np.mean((p-y)**2))

    def test_confusion_direction(self):
        r=classification([.1,.8,.1,.8],[0,0,1,1],.5)
        self.assertEqual([r[k] for k in ['TN','FP','FN','TP']],[1,1,1,1])
        self.assertEqual(r['sensitivity'],.5)
        self.assertEqual(r['specificity'],.5)


@unittest.skipUnless((ROOT/'data/credit-scoring/credit_scoring.rds').exists(),
                     'Reference credit data not present')
class ScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw,cls.income,cls.clean,cls.train,cls.test,_=load_data()
        cls.models,cls.pred=fit_logistic(cls.train,cls.test)
        spec=importlib.util.spec_from_file_location('trees',ROOT/'chapters/02-tree-based/helpers/models.py')
        cls.helpers=importlib.util.module_from_spec(spec); spec.loader.exec_module(cls.helpers)
        cls.tree,cls.booster,cls.dt,cls.ds,cls.xt,cls.xs,cls.params,cls.history=cls.helpers.fit_tree_models(cls.train,cls.test)

    def test_cleaning_and_split(self):
        self.assertEqual([len(self.raw),len(self.clean),len(self.train),len(self.test)],[30024,30000,20000,10000])
        self.assertFalse(set(self.train.index)&set(self.test.index))
        self.assertTrue((self.clean.emp_len<=self.clean.age-16).all())
        self.assertTrue((self.clean.income<=1e6).all())

    def test_logistic_link(self):
        for name,m in self.models.items():
            np.testing.assert_allclose(expit(design(self.test,name)@m.params),self.pred[name],atol=1e-14)
            self.assertTrue(m.converged)
            self.assertTrue(np.all((self.pred[name]>0)&(self.pred[name]<1)))

    def test_tree_leaf_probabilities(self):
        training_leaf=self.tree.apply(self.xt)
        testing_leaf=self.tree.apply(self.xs)
        y=self.train.loan_st.to_numpy()
        predicted=self.tree.predict_proba(self.xs)[:,1]
        for leaf in np.unique(testing_leaf):
            np.testing.assert_allclose(predicted[testing_leaf==leaf],y[training_leaf==leaf].mean(),atol=1e-14)

    def test_prefix_and_leaf_arithmetic(self):
        short=xgb.train(self.params,self.dt,num_boost_round=5,verbose_eval=False)
        np.testing.assert_array_equal(short.predict(self.ds),self.booster.predict(self.ds,iteration_range=(0,5)))
        leaf=self.booster.predict(self.ds,pred_leaf=True).astype(int)
        dump=self.booster.trees_to_dataframe()
        total=np.repeat(logit(self.params['base_score']),len(self.test))
        for r in range(5):
            t=dump[(dump.Tree==r)&(dump.Feature=='Leaf')].set_index('Node').Gain
            total+=t.loc[leaf[:,r]].to_numpy()
            np.testing.assert_allclose(total,self.booster.predict(self.ds,output_margin=True,iteration_range=(0,r+1)),
                                       atol=5e-7,rtol=2e-6)

    def test_contribution_reconstruction(self):
        c=self.helpers.contributions(self.booster,self.ds)
        np.testing.assert_allclose(expit(c.sum(axis=1)),self.booster.predict(self.ds),atol=1e-6)

    def test_policy_and_decile_accounting(self):
        y=self.test.loan_st.to_numpy()
        for p in [self.pred['full'],self.booster.predict(self.ds)]:
            accepted=[]
            for target in np.arange(50,100,5)/100:
                r=policy(p,y,target)
                self.assertEqual(r['accepted'],r['accepted_good']+r['accepted_defaults'])
                self.assertEqual(r['net_payoff'],r['accepted_good']-5*r['accepted_defaults'])
                accepted.append(r['accepted'])
            self.assertEqual(accepted,sorted(accepted))
            t=calibration(p,y,self.test.index)
            self.assertAlmostEqual(np.average(t.brier_score,weights=t.applications),np.mean((p-y)**2),places=13)


if __name__=='__main__': unittest.main()
