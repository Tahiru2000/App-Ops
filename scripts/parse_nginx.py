

import sys, re, csv, statistics
from datetime import datetime
from collections import defaultdict

NGINX_RE = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) HTTP/[^"]+" (?P<status>\d{3}) \S+ "[^"]*" "[^"]*" "(?P<req_time>[\d.]+)" "(?P<upstream_time>[\d.]+)" "[^"]*"'
)

def parse_time(s):
    return datetime.strptime(s, '%d/%b/%Y:%H:%M:%S +0000')

def main(path):
    per_min = defaultdict(list)
    with open(path) as f:
        for line in f:
            m = NGINX_RE.search(line)
            if not m:
                continue
            d = m.groupdict()
            ts = parse_time(d['time']).replace(second=0, microsecond=0)
            status = int(d['status'])
            req_time = float(d['req_time'])
            per_min[ts].append((req_time, status))

    rows = []
    for minute in sorted(per_min.keys()):
        vals = [v for v,s in per_min[minute]]
        if not vals:
            continue
        p50 = statistics.median(vals)
        p95 = statistics.quantiles(vals, n=100)[94] if len(vals) >= 2 else max(vals)
        error_rate = sum(1 for v,s in per_min[minute] if s >= 500) / len(vals)
        rows.append({'minute': minute.isoformat(), 'rps': len(vals), 'p50': round(p50,3), 'p95': round(p95,3), 'error_rate': round(error_rate,4)})

    out = 'metrics_per_minute.csv'
    with open(out,'w',newline='') as csvf:
        writer = csv.DictWriter(csvf, fieldnames=['minute','rps','p50','p95','error_rate'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print('Wrote', out)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python scripts/parse_nginx.py /path/to/access.log')
        sys.exit(1)
    main(sys.argv[1])
