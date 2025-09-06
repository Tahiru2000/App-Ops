

import sys, json, csv
from datetime import datetime
from collections import defaultdict

def minute(ts):
    return ts.replace(second=0, microsecond=0)

def parse_ts(s):
    return datetime.fromisoformat(s.replace('Z','+00:00')).astimezone().replace(tzinfo=None)

def main(path):
    per_min = defaultdict(list)
    with open(path) as f:
        for line in f:
            try:
                j = json.loads(line)
            except Exception:
                continue
            if 'ts' not in j: 
                continue
            ts = parse_ts(j['ts'])
            m = minute(ts)
            per_min[m].append((j.get('duration_ms',0), j.get('db_time_ms',0), j.get('status',0)))

    rows = []
    for m in sorted(per_min.keys()):
        entries = per_min[m]
        n = len(entries)
        avg_dur = sum(e[0] for e in entries) / n
        avg_db = sum(e[1] for e in entries) / n
        err_rate = sum(1 for e in entries if e[2] >= 500) / n
        rows.append({'minute': m.isoformat(), 'count': n, 'avg_duration_ms': round(avg_dur,1), 'avg_db_time_ms': round(avg_db,1), 'error_rate': round(err_rate,4)})

    out = 'app_metrics_per_minute.csv'
    with open(out,'w',newline='') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=['minute','count','avg_duration_ms','avg_db_time_ms','error_rate'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print('Wrote', out)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python scripts/parse_app_logs.py /path/to/app.log')
        sys.exit(1)
    main(sys.argv[1])
