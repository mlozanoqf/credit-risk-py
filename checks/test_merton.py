"""Financial and numerical tests independent of the rendered chapter."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest

import numpy as np
from scipy.optimize import least_squares
from scipy.special import ndtr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'chapters/03-merton/helpers'))
from model import Inputs, calibrate, residuals, residual_jacobian, paths, terminal_assets


class MertonTests(unittest.TestCase):
    def test_baseline_equations(self):
        q = Inputs()
        f = calibrate(q)
        np.testing.assert_allclose(residuals(f['V0'],f['sv'],q), 0, atol=2e-6)
        self.assertGreater(f['V0'], q.equity)
        self.assertTrue(0 < f['pd'] < 1)
        self.assertAlmostEqual(ndtr(f['d2']) + f['pd'], 1)

    def test_jacobian(self):
        q = Inputs()
        x = np.array([12.4,0.25])
        h = np.array([1e-5,1e-6])
        columns = []
        for i in range(2):
            step = np.zeros(2)
            step[i] = h[i]
            columns.append((residuals(*(x+step),q)-residuals(*(x-step),q))/(2*h[i]))
        np.testing.assert_allclose(residual_jacobian(*x,q),np.column_stack(columns),rtol=1e-7,atol=1e-8)

    def test_independent_solver(self):
        # An independent least-squares solve validates rather than supplies results.
        candidates = [Inputs(), Inputs(equity=1), Inputs(equity=20),
                      Inputs(equity_vol=0.01), Inputs(equity_vol=3),
                      Inputs(maturity=20), Inputs(debt=0.1), Inputs(rate=0.2)]
        for q in candidates:
            with self.subTest(inputs=q):
                f = calibrate(q)
                start = [q.equity+q.debt*np.exp(-q.rate*q.maturity),q.equity_vol/2]
                other = least_squares(lambda x: residuals(*x,q), start, bounds=(1e-8,np.inf),
                                      xtol=1e-13,ftol=1e-13,gtol=1e-13,max_nfev=4000)
                np.testing.assert_allclose([f['V0'],f['sv']],other.x,rtol=2e-5,atol=2e-6)

    def test_value_decomposition(self):
        q = Inputs()
        f = calibrate(q)
        debt = f['V0']*ndtr(-f['d1']) + q.debt*np.exp(-q.rate*q.maturity)*ndtr(f['d2'])
        self.assertAlmostEqual(debt+q.equity,f['V0'],places=5)

    def test_rng_and_paths(self):
        q, f = Inputs(), calibrate()
        p = paths(q,f,100)
        np.testing.assert_array_equal(p[:,:10],paths(q,f,10))
        np.testing.assert_allclose(p[0],f['V0'])
        self.assertTrue(np.all(p>0))
        self.assertGreater(np.sum(np.any(p<q.debt,axis=0) & (p[-1]>=q.debt)),0)

    def test_terminal_sampling(self):
        q, f = Inputs(), calibrate()
        terminal = terminal_assets(q,f,100000,np.random.Generator(np.random.PCG64(13)))
        pd_hat = np.mean(terminal<q.debt)
        se = np.sqrt(f['pd']*(1-f['pd'])/len(terminal))
        self.assertLess(abs(pd_hat-f['pd']),5*se)
        self.assertLess(abs(terminal.mean()-f['V0']*np.exp(q.rate*q.maturity)),
                        5*terminal.std(ddof=1)/np.sqrt(len(terminal)))

    def test_invalid_inputs(self):
        for field in ['equity','equity_vol','debt','maturity']:
            with self.assertRaises(ValueError):
                replace(Inputs(),**{field:0})


if __name__ == '__main__':
    unittest.main(verbosity=2)
