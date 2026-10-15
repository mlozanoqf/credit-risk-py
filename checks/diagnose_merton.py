"""Independently solve each R/Python discrepancy outside the initial tolerance."""
from dataclasses import asdict, replace
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from scipy.special import ndtr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'chapters/03-merton/helpers'))
from model import Inputs, calibrate, residuals, d_values


def parameters(key,index):
    q = Inputs()
    grids = {'pd.E':('equity',np.linspace(1,20,50)), 'pd.rf':('rate',np.linspace(0,0.2,50)),
             'pd.D':('debt',np.linspace(1,20,50)), 'pd.T':('maturity',np.linspace(0.5,20,50)),
             'pd.se':('equity_vol',np.linspace(0.01,3,50))}
    if key in grids:
        field,grid=grids[key]
        return replace(q,**{field:float(grid[index[0]])})
    if key.startswith('E') and key[1:].isdigit():
        return replace(q,equity=float(key[1:]),debt=(index[0]+1)/10)
    if key.startswith('T') and key[1:].isdigit():
        return replace(q,maturity=int(key[1:])/2,debt=(index[0]+1)/10)
    if key=='pd_surface_50':
        return replace(q,equity=float(np.linspace(1,10,50)[index[1]]),
                       equity_vol=float(np.linspace(0.01,1.5,50)[index[0]]))
    if key=='pd_surface_40':
        return replace(q,equity=float(np.linspace(2,4,40)[index[1]]),
                       equity_vol=float(np.linspace(0.2,1.5,40)[index[0]]))
    raise ValueError(f'No discrepancy policy for {key}')


def main():
    reference=json.loads((ROOT/'.local/merton-r-reference.json').read_text())
    computed=json.loads((ROOT/'output/03-merton/numeric-results.json').read_text())
    cases=[]
    for key,r in reference.items():
        a,b=np.asarray(r),np.asarray(computed[key])
        absolute=2e-5 if key in ('V0','FG.V0','FG.sv') else 1e-5
        for index_array in np.argwhere(np.abs(a-b)>absolute+1e-5*np.abs(a)):
            index=tuple(int(i) for i in index_array)
            q=parameters(key,index)
            f=calibrate(q)
            start=[q.equity+q.debt*np.exp(-q.rate*q.maturity),q.equity_vol/2]
            independent=least_squares(lambda x:residuals(*x,q),start,bounds=(1e-8,np.inf),
                                      xtol=1e-13,ftol=1e-13,gtol=1e-13,max_nfev=4000)
            independent_pd=float(ndtr(-d_values(*independent.x,q)[1]))
            assert np.max(np.abs(independent.fun))<2e-6
            assert abs(independent_pd-b[index])<1e-7
            assert abs(a[index]-b[index])<5e-5 # Economic review ceiling: 0.5 PD basis points.
            cases.append(dict(Object=key,Index=json.dumps(index),**asdict(q),
                              R_PD=float(a[index]),Python_PD=float(b[index]),
                              independent_PD=independent_pd,Python_residual=f['max_residual'],
                              independent_residual=float(np.max(np.abs(independent.fun))),
                              difference_bps=float((b[index]-a[index])*10000)))
    frame=pd.DataFrame(cases)
    frame.to_csv(ROOT/'.local/merton-discrepancy-cases.csv',index=False)
    print(frame.to_string(index=False))
    print(f'{len(frame)} discrepant points independently verified. R equation diagnostics remain required.')


if __name__=='__main__':
    main()
