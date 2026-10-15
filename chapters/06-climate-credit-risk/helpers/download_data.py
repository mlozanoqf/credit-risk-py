"""Optional refresh of NGFS source observations into a NEW directory.

This is a translation of the documented R API request, not part of rendering.
Endpoint availability is external. The frozen files remain the default inputs.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen
from urllib.error import URLError
import pandas as pd
from climate import portfolio_inputs, METRICS

DATABASE = 'IXSE_NGFS_PHASE_5_SHORT_TERM'
AUTH = 'https://api.manager.ece.iiasa.ac.at/legacy/anonym/'+DATABASE+'?algorithm=HS256'
BASE = 'https://db1.ene.iiasa.ac.at/ngfs-phase-5-short-term-api/rest/v2.1'


def guest_token():
    last_error = None
    for attempt in range(5):
        try:
            with urlopen(AUTH,timeout=30) as response:
                text = response.read().decode('utf-8').strip()
            token = json.loads(text) if text.startswith('"') else text
            if isinstance(token,str) and token: return token
        except (URLError,ValueError) as exc:
            last_error = exc
        time.sleep(1)
    raise RuntimeError('NGFS guest token unavailable; frozen data can still be used.') from last_error


def query(runs,regions,variables,years):
    body = {'filters':dict(runs=runs,regions=regions,variables=variables,years=years,units=[],timeslices=['Year'])}
    request = Request(BASE+'/runs/bulk/ts',data=json.dumps(body).encode(),
        headers={'Authorization':'Bearer '+guest_token(),'Content-Type':'application/json'},method='POST')
    with urlopen(request,timeout=120) as response:
        payload = json.loads(response.read())
    if not isinstance(payload,list) or not payload: raise ValueError('Unexpected or empty API response.')
    frame = pd.json_normalize(payload)
    if not {'scenario','region','variable','year','value'}.issubset(frame):
        raise ValueError('API schema changed; inspect the response before replacing any data.')
    return frame


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',type=Path,required=True)
    dest = parser.parse_args().destination.resolve()
    if dest.exists(): parser.error('Use a new destination; frozen data are never overwritten.')
    sectors = portfolio_inputs().ngfs_sector
    global_data = query([74,75,76],['World'],[m+'|'+s for s in sectors for m in METRICS],list(range(2022,2031)))
    daps_data = query(list(range(68,74)),['Africa','Asia','Euro Area','North America','Oceania','South America'],
        ['pd_adjustment|'+s for s in ['Agriculture','Coal','Power Supply']],list(range(2024,2031)))
    dest.mkdir(parents=True)
    manifest = []
    for name,data in [('global',global_data),('daps',daps_data)]:
        file = dest/f'ngfs_climacred_{name}_raw.csv'
        data.to_csv(file,index=False)
        manifest.append(dict(file=str(file),rows=len(data),database=DATABASE,endpoint=BASE+'/runs/bulk/ts',
            downloaded_at_utc=datetime.now(timezone.utc).isoformat()))
    pd.DataFrame(manifest).to_csv(dest/'ngfs_climacred_download_manifest.csv',index=False)


if __name__=='__main__':
    main()
