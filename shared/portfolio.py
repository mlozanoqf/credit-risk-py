"""Discrete portfolio loss measures and Gaussian/Student copula simulation."""
import numpy as np
from scipy.stats import norm, t


def expected_shortfall(losses, confidence):
    losses = np.asarray(losses, dtype=float)
    if losses.size == 0 or not np.isfinite(losses).all() or not 0 <= confidence < 1:
        raise ValueError('Finite losses and confidence in [0, 1) required.')
    threshold = np.quantile(losses, confidence, method='inverted_cdf')
    return float(threshold + np.maximum(losses-threshold, 0).mean()/(1-confidence))


def risk_summary(losses):
    losses = np.asarray(losses)
    median, v95, v99, v999 = np.quantile(losses, [.5,.95,.99,.999], method='inverted_cdf')
    return dict(expected_loss=float(losses.mean()), median_loss=float(median),
                var_95=float(v95), var_99=float(v99), var_999=float(v999),
                es_99=expected_shortfall(losses,.99), es_999=expected_shortfall(losses,.999),
                economic_capital_999=float(v999-losses.mean()))


def correlation_matrix(n, rho):
    if n < 2 or not -1/(n-1) < rho < 1:
        raise ValueError('Equicorrelation matrix must be positive definite.')
    return (1-rho)*np.eye(n)+rho*np.ones((n,n))


def latent_scores(n_sims, n_firms, rho, seed=130575, df=None):
    rng = np.random.default_rng(seed)
    normal = rng.standard_normal((n_sims,n_firms)) @ np.linalg.cholesky(correlation_matrix(n_firms,rho)).T
    if df is None:
        return normal
    scale = np.sqrt(rng.chisquare(df,n_sims)/df)
    return normal/scale[:,None]


def event_summary(defaults):
    counts = defaults.sum(axis=1)
    return dict(expected_defaults=float(counts.mean()),no_default=float(np.mean(counts==0)),
                at_least_one=float(np.mean(counts>=1)),three_or_more=float(np.mean(counts>=3)),
                five_or_more=float(np.mean(counts>=5)),all_default=float(np.mean(counts==defaults.shape[1])))


def vasicek_rate(pd, rho, confidence):
    return norm.cdf((norm.ppf(pd)+np.sqrt(rho)*norm.ppf(confidence))/np.sqrt(1-rho))


def granular_losses(n_sims=200000, n_names=1000, ead=100e6, pd=.02,
                    recovery=.6, rho=.1, seed=130575, df=None):
    rng = np.random.default_rng(seed)
    factor = rng.standard_normal(n_sims)
    threshold = norm.ppf(pd) if df is None else t.ppf(pd,df)*np.sqrt(rng.chisquare(df,n_sims)/df)
    conditional = norm.cdf((threshold-np.sqrt(rho)*factor)/np.sqrt(1-rho))
    return rng.binomial(n_names,conditional)*(ead/n_names)*(1-recovery)


def climate_losses(baseline, climate, ead, recovery, rho=.25, n_sims=50000, seed=202606):
    rng = np.random.default_rng(seed)
    scores = np.sqrt(rho)*rng.standard_normal(n_sims)[:,None]+np.sqrt(1-rho)*rng.standard_normal((n_sims,len(baseline)))
    base_events = scores < norm.ppf(baseline)
    climate_events = scores < norm.ppf(climate)
    loss_amount = np.asarray(ead)*(1-np.asarray(recovery))
    return scores, base_events, climate_events, base_events@loss_amount, climate_events@loss_amount
