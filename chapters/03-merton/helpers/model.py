"""Merton equations, bounded calibration and risk-neutral GBM simulation."""
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from scipy.optimize import minimize
from scipy.special import ndtr


@dataclass(frozen=True)
class Inputs:
    equity: float = 3.0
    equity_vol: float = 0.8
    rate: float = 0.05
    maturity: float = 1.0
    debt: float = 10.0

    def __post_init__(self):
        if not all(np.isfinite([self.equity, self.equity_vol, self.rate,
                                self.maturity, self.debt])):
            raise ValueError('Inputs must be finite.')
        if min(self.equity, self.equity_vol, self.maturity, self.debt) <= 0:
            raise ValueError('Equity, volatility, maturity and debt must be positive.')


def d_values(asset, vol, inputs):
    scale = vol * np.sqrt(inputs.maturity)
    d1 = (np.log(asset / inputs.debt) +
          (inputs.rate + vol**2 / 2) * inputs.maturity) / scale
    return d1, d1 - scale


def residuals(asset, vol, inputs):
    d1, d2 = d_values(asset, vol, inputs)
    equity_error = (asset * ndtr(d1) - inputs.debt * np.exp(
        -inputs.rate * inputs.maturity) * ndtr(d2) - inputs.equity)
    vol_error = asset * vol * ndtr(d1) - inputs.equity_vol * inputs.equity
    return np.array([equity_error, vol_error])


def objective(asset, vol, inputs):
    return np.sum(residuals(asset, vol, inputs)**2, axis=0)


def residual_jacobian(asset, vol, inputs):
    d1, d2 = d_values(asset, vol, inputs)
    pdf = np.exp(-d1**2 / 2) / np.sqrt(2 * np.pi)
    sqrt_t = np.sqrt(inputs.maturity)
    return np.array([[ndtr(d1), asset * pdf * sqrt_t],
                     [vol * ndtr(d1) + pdf / sqrt_t,
                      asset * (ndtr(d1) - pdf * d2)]])


@lru_cache(maxsize=None)
def calibrate(inputs=Inputs()):
    start_asset = inputs.equity + inputs.debt * np.exp(-inputs.rate * inputs.maturity)
    start_vol = inputs.equity_vol * inputs.equity / start_asset
    # The R example scales parameters by (10, 0.2); use the same coordinates.
    scale = np.array([10.0, 0.2])

    def function(y):
        asset, vol = y * scale
        errors = residuals(asset, vol, inputs)
        gradient = 2 * residual_jacobian(asset, vol, inputs).T @ errors
        return float(errors @ errors), gradient * scale

    result = minimize(function, np.array([start_asset, start_vol]) / scale,
                      jac=True, method='L-BFGS-B',
                      bounds=[(1e-6 / scale[0], None), (1e-6 / scale[1], None)],
                      options={'ftol': 1e-15, 'gtol': 1e-10,
                               'maxiter': 2000, 'maxls': 50})
    asset, vol = result.x * scale
    errors = residuals(asset, vol, inputs)
    if np.max(np.abs(errors)) > 2e-6:
        raise RuntimeError(f'Calibration residual too large: {inputs}, {errors}, {result.message}')
    d1, d2 = d_values(asset, vol, inputs)
    return {'V0': float(asset), 'sv': float(vol), 'd1': float(d1), 'd2': float(d2),
            'pd': float(ndtr(-d2)), 'objective': float(errors @ errors),
            'max_residual': float(np.max(np.abs(errors))),
            'optimizer_success': bool(result.success), 'message': str(result.message)}


def paths(inputs, fit, count, seed=3, steps=365):
    rng = np.random.Generator(np.random.PCG64(seed))
    dt = inputs.maturity / steps
    # Draw complete paths by row, so the first ten also occur in the 100-path run.
    shocks = rng.standard_normal((count, steps))
    increments = (inputs.rate - fit['sv']**2 / 2) * dt + fit['sv'] * np.sqrt(dt) * shocks
    logs = np.column_stack([np.zeros(count), np.cumsum(increments, axis=1)])
    return fit['V0'] * np.exp(logs.T)


def terminal_assets(inputs, fit, count, rng):
    return fit['V0'] * np.exp((inputs.rate - fit['sv']**2 / 2) * inputs.maturity +
                             fit['sv'] * np.sqrt(inputs.maturity) * rng.standard_normal(count))
