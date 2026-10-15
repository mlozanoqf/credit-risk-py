"""Financial invariants and data checks for Chapters 4-6; no R runtime needed."""
from pathlib import Path
import sys
import unittest
import numpy as np
import pandas as pd
from scipy.stats import norm,t

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'chapters/04-credit-spreads-cds/helpers'))
sys.path.insert(0,str(ROOT/'chapters/06-climate-credit-risk/helpers'))
from valuation import (survival_schedule,price_coupon,price_from_yield,coupon_ytm,cds_components,
    hull_components,make_bonds,yield_price,bond_price,fit_curve,discount,days360)
from climate import portfolio_inputs,prepare_global,prepare_daps,horizon_losses,loss_steps
from shared.portfolio import (expected_shortfall,correlation_matrix,latent_scores,vasicek_rate,
    granular_losses,climate_losses)


class BondTests(unittest.TestCase):
    def test_survival_accounting(self):
        s = survival_schedule([.02,.03,.07,.1])
        np.testing.assert_allclose(s.marginal_pd.cumsum()+s.survival_end,1)
        self.assertAlmostEqual(s.marginal_pd.sum(),1-np.prod(1-s.h))
    def test_default_free_and_price_yield(self):
        p = price_coupon(100,.05,.04,.4,[0]*5)
        self.assertAlmostEqual(p,price_from_yield(100,.05,.04,5))
        self.assertAlmostEqual(coupon_ytm(p,100,.05,5),.04)
    def test_default_and_recovery_monotonicity(self):
        self.assertGreater(price_coupon(100,.05,.04,.4,[.02]*5),price_coupon(100,.05,.04,.4,[.04]*5))
        self.assertGreater(price_coupon(100,.05,.04,.6,[.02]*5),price_coupon(100,.05,.04,.4,[.02]*5))
    def test_cds_balance(self):
        c = cds_components(.05,.4,[.12],100)
        self.assertAlmostEqual(c['fair_spread'],.6*.12/.88)
        self.assertAlmostEqual(c['premium_annuity']*c['fair_spread'],c['protection_leg'])
        h = hull_components(.02)
        self.assertAlmostEqual(h['fair_spread']*h['risky_annuity_with_accrual'],h['protection_leg'])
    def test_calendar_and_curve(self):
        inputs = pd.read_csv(ROOT/'data/credit-spreads/corporate-bond-snapshot.csv')
        curve = pd.read_csv(ROOT/'data/credit-spreads/corporate-treasury-curve.csv').iloc[0].to_dict()
        bonds = make_bonds(inputs)
        self.assertEqual(days360('2026-08-01','2026-09-29'),58)
        self.assertAlmostEqual(float(discount(0,curve,bonds[0].settlement)),1)
        for b in bonds:
            self.assertAlmostEqual(yield_price(b,b.ytm),b.price,places=8)
            self.assertGreater(b.dv01,0)
            self.assertTrue(np.all(np.diff(b.time)>0))
    def test_synthetic_curve_recovery(self):
        inputs = pd.read_csv(ROOT/'data/credit-spreads/corporate-bond-snapshot.csv')
        curve = pd.read_csv(ROOT/'data/credit-spreads/corporate-treasury-curve.csv').iloc[0].to_dict()
        bonds = make_bonds(inputs.iloc[:5])
        true = np.array([.02,.065])
        for b in bonds: b.price = bond_price(b,true,curve)
        fit = fit_curve(bonds,list(range(5)),curve)
        np.testing.assert_allclose(fit['h'],true,atol=1e-8)
        self.assertLess(fit['objective'],1e-10)


class CopulaTests(unittest.TestCase):
    def test_es_boundary_mass(self):
        losses = np.array([0,0,0,10,10,20],dtype=float)
        self.assertAlmostEqual(expected_shortfall(losses,.75),(20+10*.5)/1.5)
        self.assertAlmostEqual(expected_shortfall(losses,0),losses.mean())
        self.assertEqual(expected_shortfall([5,5,5],.99),5)
        with self.assertRaises(ValueError): expected_shortfall(losses,1)
    def test_es_fractional_sorted_tail(self):
        x = np.array([2,0,20,10,5,10,30,0,8,8,0])
        for alpha in [.5,.9,.95,.999]:
            mass = len(x)*(1-alpha)
            ordered = np.sort(x)[::-1]
            n = int(np.floor(mass))
            direct = (ordered[:n].sum()+(mass-n)*ordered[n])/mass
            self.assertAlmostEqual(expected_shortfall(x,alpha),direct)
    def test_marginals_and_covariance(self):
        scores = latent_scores(100000,3,.2)
        np.testing.assert_allclose(np.cov(scores.T),correlation_matrix(3,.2),atol=.015)
        np.testing.assert_allclose((scores<=norm.ppf(.15)).mean(axis=0),.15,atol=.006)
        student = latent_scores(100000,3,.2,df=4)
        np.testing.assert_allclose((student<=t.ppf(.15,4)).mean(axis=0),.15,atol=.006)
    def test_shared_scale(self):
        g = latent_scores(1000,5,.2)
        s = latent_scores(1000,5,.2,df=4)
        ratio = g/s
        np.testing.assert_allclose(ratio, np.repeat(ratio[:,:1],5,axis=1))
    def test_vasicek_and_granular(self):
        np.testing.assert_allclose(vasicek_rate(.02,0,[.95,.99]),.02)
        loss = granular_losses(n_sims=100000)
        self.assertLess(abs(loss.mean()-.02*100e6*.4),5*loss.std(ddof=1)/np.sqrt(len(loss)))
        np.testing.assert_allclose(loss/40000,np.round(loss/40000))
    def test_repeatable_seeds(self):
        np.testing.assert_array_equal(granular_losses(n_sims=1000,df=4),granular_losses(n_sims=1000,df=4))


class ClimateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.portfolio = portfolio_inputs()
        cls.raw = pd.read_csv(ROOT/'data/climate/ngfs_climacred_global_raw.csv')
        cls.data = prepare_global(cls.raw,cls.portfolio)
    def test_unique_complete_and_units(self):
        self.assertEqual(len(self.data),270)
        self.assertFalse(self.data.duplicated(['scenario','portfolio_sector','year']).any())
        coal = self.data.query("scenario=='HWTP' and year==2030 and portfolio_sector=='Coal'").iloc[0]
        raw = self.raw.query("scenario=='HWTP' and year==2030 and variable=='pd_adjustment|Coal'").iloc[0]
        self.assertAlmostEqual(coal.pd_adjustment,raw.value/100)
        self.assertAlmostEqual(coal.climate_pd,min(1,coal.baseline_pd+coal.pd_adjustment))
    def test_loss_aggregation(self):
        h = horizon_losses(self.data)
        self.assertEqual(len(h),30)
        np.testing.assert_allclose(h.incremental_pv_el,h.pv_el_climate-h.pv_el_baseline)
        s = loss_steps([.1,.2],100,.4,0)
        self.assertAlmostEqual(s['PV expected loss'].sum(),100*.6*(.1+.9*.2))
    def test_physical_geography(self):
        d = prepare_daps(pd.read_csv(ROOT/'data/climate/ngfs_climacred_daps_raw.csv'))
        self.assertEqual(len(d),126)
        self.assertTrue((d.region==d.region_label).all())
    def test_common_shock_coupling(self):
        scores,base,climate,lb,lc = climate_losses([.1,.2],[.2,.3],[100,200],[.4,.5],n_sims=10000)
        self.assertFalse((base&~climate).any())
        self.assertTrue((lc>=lb).all())
        np.testing.assert_allclose(lb,base@np.array([60,100]))
        np.testing.assert_allclose(lc,climate@np.array([60,100]))


if __name__=='__main__':
    unittest.main()
