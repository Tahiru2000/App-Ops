import sys, re, csv

DUR_RE = re.compile(r'duration:\s+(?P<dur>[\d.]+)\s+ms\s+statement:\s+(?P<stmt>.+)$')

def main(path, thresh=1000):
    hits = []
    with open(path) as f:
        for line in f:
            m = DUR_RE.search(line.strip())
            if not m:
                continue
            dur = float(m.group('dur'))
            stmt = m.group('stmt').strip()
            hits.append((dur, stmt))
    hits_sorted = sorted(hits, reverse=True)
    out = 'postgres_slow.csv'
    with open(out,'w',newline='') as csvf:
        writer = csv.writer(csvf)
        writer.writerow(['duration_ms','statement'])
        for d, s in hits_sorted:
            if d >= thresh:
                writer.writerow([d, s])
    print(f'Wrote {out} ({sum(1 for d,s in hits_sorted if d>=thresh)} slow entries >= {thresh} ms)')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python scripts/check_postgres_slow.py /path/to/postgres.log [threshold_ms]')
        sys.exit(1)
    thresh = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    main(sys.argv[1], thresh)
