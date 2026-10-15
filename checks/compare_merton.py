"""Compare the completed Python run with an explicitly supplied local R export."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference', type=Path)
    parser.add_argument('--optimizer-diagnostics', type=Path)
    args = parser.parse_args()
    reference = json.loads(args.reference.read_text(encoding='utf-8-sig'))
    computed = json.loads((ROOT/'output/03-merton/numeric-results.json').read_text())
    diagnostics = {}
    if args.optimizer_diagnostics:
        for d in pd.read_csv(args.optimizer_diagnostics).to_dict('records'):
            diagnostics[(d['Object'],tuple(json.loads(d['Index'])))] = d
    rows = []
    for key, expected in reference.items():
        a,b = np.asarray(expected,dtype=float),np.asarray(computed[key],dtype=float)
        if a.shape != b.shape:
            raise AssertionError((key,a.shape,b.shape))
        absolute = 2e-5 if key in ('V0','FG.V0','FG.sv') else 1e-5
        relative = 1e-5
        delta = np.abs(a-b)
        ok = np.all(delta <= absolute+relative*np.abs(a))
        verified = bool(ok)
        reviewed = 0
        if not ok:
            verified = True
            for index_array in np.argwhere(delta > absolute+relative*np.abs(a)):
                index = tuple(int(i) for i in index_array)
                d = diagnostics.get((key,index))
                accepted = bool(d is not None and delta[index] < 5e-5
                    and abs(d['R_PD']-a[index]) < 1e-12
                    and abs(d['R_rerun_PD']-a[index]) < 1e-10
                    and abs(d['Python_PD']-b[index]) < 1e-12
                    and abs(d['independent_PD']-b[index]) < 1e-7
                    and d['Python_residual'] < 2e-6 and d['independent_residual'] < 2e-6
                    and d['R_max_residual'] > d['Python_residual'])
                verified = verified and accepted
                reviewed += int(accepted)
        rows.append({'Object':key,'Values':a.size,'Maximum absolute difference':float(delta.max()),
                     'Absolute tolerance':absolute,'Relative tolerance':relative,
                     'Within default tolerance':bool(ok),'Reviewed optimizer differences':reviewed,
                     'Verified':verified})
    result = pd.DataFrame(rows)
    result.to_csv(ROOT/'output/03-merton/r-comparison.csv',index=False)
    print(result.to_string(index=False))
    print(f"Compared {len(result)} groups / {result['Values'].sum()} values.")
    if not result['Verified'].all():
        raise AssertionError('Differences require diagnosis; see r-comparison.csv.')


if __name__ == '__main__':
    main()
