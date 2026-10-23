#!/usr/bin/env python3
"""Independent, read-only checks for the provided BTS January 2019 export.
Usage: python TS018_201901_INDEPENDENT_EVIDENCE_CHECK_20261020.py path/to/BTS.zip
Never edits input or production files. Does NOT verify user project raw CSV parity.
"""
import csv
import hashlib
import io
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

EXPECTED_SHA = '342de99f65561fb856b524c704f2ad3851f8015f52251668ece346dff1350ae6'
KEYS_CLAIMED_IN_REPORT = [
 ('2019-01-01','DL','1142','ATL','LGA'),
 ('2019-01-12','AA','2401','DFW','ORD'),
 ('2019-01-20','WN','582','DEN','PHX'),
]

def audit(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(1024*1024),b''):
            digest.update(part)
    sha = digest.hexdigest()
    if sha != EXPECTED_SHA:
        raise SystemExit(f'UNEXPECTED ZIP SHA256 {sha}; expected {EXPECTED_SHA}')
    witnessed = {}
    rows = 0
    null_arr = 0
    null_arr_active = 0
    flags = Counter()
    dates = set()
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            raise SystemExit('CRC FAILURE')
        with z.open('T_ONTIME_REPORTING.csv') as f:
            for r in csv.DictReader(io.TextIOWrapper(f,encoding='utf-8')):
                rows += 1
                month,day,year = map(int,r['FL_DATE'].split()[0].split('/'))
                key = (f'{year:04}-{month:02}-{day:02}',r['OP_CARRIER'],str(int(float(r['OP_CARRIER_FL_NUM']))),r['ORIGIN'],r['DEST'])
                dates.add(key[0])
                if key in KEYS_CLAIMED_IN_REPORT:
                    witnessed[key] = {m:r[m] for m in ('ARR_DELAY','DEP_DELAY','TAXI_OUT','TAXI_IN','AIR_TIME','ACTUAL_ELAPSED_TIME','CRS_ELAPSED_TIME')}
                canceled = r['CANCELLED'].strip() in ('1','1.0','1.00')
                diverted = r['DIVERTED'].strip() in ('1','1.0','1.00')
                flags[('cancelled' if canceled else 'active'),('diverted' if diverted else 'not_diverted')] += 1
                if not r['ARR_DELAY'].strip():
                    null_arr += 1
                    if not canceled and not diverted:
                        null_arr_active += 1
    return {
     'zip_sha256':sha,'bts_rows':rows,'date_count':len(dates),'date_min':min(dates),'date_max':max(dates),
     'claimed_examples_present':{'|'.join(k):k in witnessed for k in KEYS_CLAIMED_IN_REPORT},
     'arr_delay_null_total':null_arr,'arr_delay_null_not_cancelled_nor_diverted':null_arr_active,
     'status_breakdown':{':'.join(k):v for k,v in flags.items()},
     'note':'Can check factual BTS examples and null status only; project RAW CSV was not supplied here.'
    }

if __name__ == '__main__':
    if len(sys.argv)!=2:
        raise SystemExit('Usage: python independent_check.py path/to/T_ONTIME_REPORTING_20261019_112232.zip')
    print(json.dumps(audit(Path(sys.argv[1])),indent=2,ensure_ascii=False))
