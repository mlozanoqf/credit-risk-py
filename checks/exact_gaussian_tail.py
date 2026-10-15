"""Independent quadrature check of Gaussian 99.9% ES; no simulated inputs."""
from pathlib import Path
import json
import numpy as np
from scipy.integrate import quad
from scipy.stats import norm,binom


def main():
    root = Path(__file__).resolve().parents[1]
    pd,rho,n,alpha,unit = .02,.1,1000,.999,40000
    def conditional(f):
        return norm.cdf((norm.ppf(pd)-np.sqrt(rho)*f)/np.sqrt(1-rho))
    def integrate(fn):
        return quad(lambda f:fn(conditional(f))*norm.pdf(f),-12,12,epsabs=1e-11,epsrel=1e-10,limit=200)[0]
    lo,hi = 0,n
    while lo<hi:
        k = (lo+hi)//2
        cdf = integrate(lambda p:binom.cdf(k,n,p))
        if cdf>=alpha: hi=k
        else: lo=k+1
    k = lo
    excess = integrate(lambda p:n*p*binom.sf(k-1,n-1,p)-k*binom.sf(k,n,p))
    es = unit*(k+excess/(1-alpha))
    vasicek_es = quad(lambda f:conditional(f)*norm.pdf(f),-12,norm.ppf(1-alpha),epsabs=1e-13)[0]*40e6/(1-alpha)
    result = dict(gaussian_finite_var_999=k*unit,gaussian_finite_es_999=es,
                  gaussian_asymptotic_es_999=vasicek_es)
    (root/'.local/exact-gaussian-tail.json').write_text(json.dumps(result,indent=2))
    print(result)


if __name__=='__main__': main()
