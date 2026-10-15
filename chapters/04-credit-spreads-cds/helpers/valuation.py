"""Discrete bond/CDS valuation and dated issuer-curve relative value."""
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy.optimize import brentq, least_squares


def survival_schedule(h):
    h = np.atleast_1d(np.asarray(h,dtype=float))
    if len(h)==0 or np.any((h<0)|(h>1)):
        raise ValueError('Conditional PDs must be in [0,1].')
    start = np.r_[1,np.cumprod(1-h)[:-1]]
    marginal = start*h
    end = start-marginal
    return pd.DataFrame(dict(period=np.arange(1,len(h)+1),h=h,survival_start=start,
                             marginal_pd=marginal,survival_end=end,cumulative_pd=1-end))


def coupon_components(face,coupon_rate,r,recovery,h):
    s = survival_schedule(h)
    discount = (1+r)**(-s.period.to_numpy(dtype=float))
    return np.array([np.sum(discount*face*coupon_rate*s.survival_end),
                     np.sum(discount*face*recovery*s.marginal_pd),
                     face*discount[-1]*s.survival_end.iloc[-1]])


def price_coupon(face,coupon_rate,r,recovery,h):
    return coupon_components(face,coupon_rate,r,recovery,h).sum()


def price_from_yield(face,coupon_rate,y,maturity):
    return np.sum(face*coupon_rate/(1+y)**np.arange(1,maturity+1))+face/(1+y)**maturity


def coupon_ytm(price,face,coupon_rate,maturity):
    return brentq(lambda y:price_from_yield(face,coupon_rate,y,maturity)-price,-.95,1,xtol=1e-13)


def cds_components(r,recovery,h,notional=1):
    s = survival_schedule(h)
    discount = (1+r)**(-s.period.to_numpy(dtype=float))
    protection = notional*(1-recovery)*np.sum(discount*s.marginal_pd)
    annuity = notional*np.sum(discount*s.survival_end)
    return dict(protection_leg=protection,premium_annuity=annuity,fair_spread=protection/annuity)


def hull_schedule(hazard,r,recovery,maturity):
    year = np.arange(1,maturity+1)
    survival = np.exp(-hazard*year)
    default = np.exp(-hazard*(year-1))-survival
    premium_discount = np.exp(-r*year)
    default_discount = np.exp(-r*(year-.5))
    return pd.DataFrame(dict(year=year,default_time=year-.5,survival_probability=survival,
        default_probability=default,premium_discount=premium_discount,default_discount=default_discount,
        premium_annuity_piece=survival*premium_discount,protection_piece=default*(1-recovery)*default_discount,
        accrual_annuity_piece=.5*default*default_discount))


def hull_components(hazard,r=.05,recovery=.4,maturity=5,notional=1):
    s = hull_schedule(hazard,r,recovery,maturity)
    regular,protection,accrual = notional*s[['premium_annuity_piece','protection_piece','accrual_annuity_piece']].sum().to_numpy()
    return dict(premium_annuity=regular,protection_leg=protection,accrual_annuity=accrual,
        risky_annuity_with_accrual=regular+accrual,fair_spread=protection/(regular+accrual))


def days360(a,b):
    a,b = pd.Timestamp(a),pd.Timestamp(b)
    return 360*(b.year-a.year)+30*(b.month-a.month)+min(b.day,30)-min(a.day,30)


def spot(t,curve):
    t = np.asarray(t,dtype=float)
    def a(z):
        return np.divide(-np.expm1(-z),z,out=np.ones_like(z),where=np.abs(z)>=1e-10)
    u,v = t/curve['TAU1'],t/curve['TAU2']
    return (curve['BETA0']+curve['BETA1']*a(u)+curve['BETA2']*(a(u)-np.exp(-u))+curve['BETA3']*(a(v)-np.exp(-v)))/100


def discount(t,curve,settlement,shift=0):
    t = np.asarray(t)
    elapsed = (pd.Timestamp(settlement)-pd.Timestamp(curve['Date'])).days/365
    return np.exp(-spot(t+elapsed,curve)*(t+elapsed)+spot(elapsed,curve)*elapsed-shift*t)


@dataclass
class Bond:
    isin: str
    issuer: str
    dates: pd.DatetimeIndex
    maturity: pd.Timestamp
    settlement: pd.Timestamp
    time: np.ndarray
    coupon: float
    cash: np.ndarray
    price: float
    accrued: float
    exponent: np.ndarray
    exposure: np.ndarray
    ytm: float = 0
    dv01: float = 0


def yield_price(b,y):
    return np.sum(b.cash/(1+y/2)**b.exponent)-b.accrued


def ytm(b,price):
    return brentq(lambda y:yield_price(b,y)-price,-.02,.5,xtol=1e-13)


def make_bonds(inputs,settlement='2026-09-29'):
    settlement = pd.Timestamp(settlement)
    result = []
    for row in inputs.itertuples():
        maturity = pd.Timestamp(row.maturity)
        dates = pd.DatetimeIndex(sorted(maturity-pd.DateOffset(months=6*k) for k in range(30)))
        previous = dates[dates<=settlement].max()
        dates = dates[dates>settlement]
        time = np.asarray((dates-settlement).days)/365
        coupon = row.coupon_percent/2
        cash = np.repeat(coupon,len(time)); cash[-1] += 100
        b = Bond(row.isin,row.issuer,dates,maturity,settlement,time,coupon,cash,row.clean_price,
            row.coupon_percent*days360(previous,settlement)/360,
            days360(settlement,dates[0])/180+np.arange(len(time)),
            np.clip(time[:,None]-np.arange(8),0,1))
        assert 0 < time.max() < 8
        b.ytm = ytm(b,b.price)
        b.dv01 = (yield_price(b,b.ytm-.0001)-yield_price(b,b.ytm+.0001))/2
        result.append(b)
    return result


def survival(b,endpoints,shape='gradual',knot=4):
    if shape=='gradual':
        return np.exp(b.exposure@np.log1p(-np.linspace(*endpoints,8)))
    return (1-endpoints[0])**np.minimum(b.time,knot)*(1-endpoints[1])**np.maximum(b.time-knot,0)


def bond_components(b,endpoints,curve,recovery=.4,shift=0,timing='end',shape='gradual',knot=4):
    s = survival(b,endpoints,shape,knot)
    q = np.r_[1,s[:-1]]-s
    df = discount(b.time,curve,b.settlement,shift)
    recovery_time = b.time if timing=='end' else (b.time+np.r_[0,b.time[:-1]])/2
    rdf = discount(recovery_time,curve,b.settlement,shift)
    principal = np.zeros(len(s)); principal[-1] = 100*df[-1]*s[-1]
    return pd.DataFrame(dict(time=b.time,survival=s,default=q,discount=df,coupon_pv=df*b.coupon*s,
        recovery_pv=100*recovery*rdf*q,principal_pv=principal))


def bond_price(b,endpoints,curve,**kwargs):
    components = bond_components(b,endpoints,curve,**kwargs)
    return components[['coupon_pv','recovery_pv','principal_pv']].to_numpy().sum()-b.accrued


def fit_curve(bonds,train,curve,recovery=.4,shift=0,weight='dv01',timing='end',shape='gradual',knot=4):
    prepared = []
    for j in train:
        b = bonds[j]
        rt = b.time if timing=='end' else (b.time+np.r_[0,b.time[:-1]])/2
        prepared.append((b,discount(b.time,curve,b.settlement,shift),discount(rt,curve,b.settlement,shift)))
    def residual(h):
        errors = []
        for b,df,rdf in prepared:
            s = survival(b,h,shape,knot)
            q = np.r_[1,s[:-1]]-s
            p = np.sum(df*b.coupon*s)+100*recovery*np.sum(rdf*q)+100*df[-1]*s[-1]-b.accrued
            errors.append((p-b.price)/(b.dv01 if weight=='dv01' else 1))
        return np.asarray(errors)
    fits = [least_squares(residual,x,bounds=([1e-6]*2,[.5]*2),ftol=1e-12,xtol=1e-12,gtol=1e-10,max_nfev=1500)
            for x in [[.01,.02],[.025,.005],[.04,.05]]]
    good = [f for f in fits if f.success]
    if not good: raise RuntimeError('No converged issuer-curve fit.')
    best = min(good,key=lambda f:np.sum(f.fun**2))
    return dict(h=best.x,objective=float(np.sum(best.fun**2)),boundary=bool(np.any((best.x<1e-5)|(best.x>.5-1e-5))))


def evaluate(i,bonds,curve,omit=(),**kwargs):
    train = [j for j,b in enumerate(bonds) if b.issuer==bonds[i].issuer and j!=i and j not in omit]
    assert len(train)>=3 and i not in train
    fit = fit_curve(bonds,train,curve,**kwargs)
    pricing = {k:v for k,v in kwargs.items() if k!='weight'}
    p = bond_price(bonds[i],fit['h'],curve,**pricing)
    y = ytm(bonds[i],p)
    return dict(**fit,train=train,model_price=p,model_yield=y,residual_bp=1e4*(bonds[i].ytm-y))


def call_price(b,date,redemption,y):
    date = pd.Timestamp(date)
    dates = list(b.dates[b.dates<=date]); cash = [b.coupon]*len(dates)
    if dates and dates[-1]==date:
        cash[-1] += redemption
    else:
        schedule = [b.maturity-pd.DateOffset(months=6*k) for k in range(30)]
        last = max(d for d in schedule if d<date)
        dates.append(date); cash.append(redemption+2*b.coupon*days360(last,date)/360)
    exponents = np.array([days360(b.settlement,d)/180 for d in dates])
    return np.sum(np.array(cash)/(1+y/2)**exponents)-b.accrued


def call_yield(b,date,redemption=100):
    return brentq(lambda y:call_price(b,date,redemption,y)-b.price,-.02,3,xtol=1e-13)
