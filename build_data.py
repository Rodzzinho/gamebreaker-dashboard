"""Builds data/bets.csv for the dashboard from pinnacle_clv_drift.csv.
Only SETTLED picks (a Pinnacle closing price exists) are exported, so no live pre-kick-off pick is ever shown.
'logged_at' = the commit time when the pick first appeared in git, i.e. a timestamp that was set before the match."""
import pandas as pd, re, subprocess, sys, json, os, datetime
SRC = r'C:\Users\RODNE\pinnacle_clv_drift.csv'
REPO = r'C:\Users\RODNE'
d = pd.read_csv(SRC)

def num(x):
    if pd.isna(x): return None
    s = re.sub(r'[%+\s]', '', str(x))
    try: return float(s)
    except ValueError: return None

d['clv_pct'] = d['pin_clv'].map(num)
d = d.dropna(subset=['clv_pct']).copy()

def first_seen(match):
    try:
        out = subprocess.run(['git', '-C', REPO, 'log', '--reverse', '--format=%aI', '-S', match, '--', 'pinnacle_clv_drift.csv'],
                             capture_output=True, text=True, timeout=60).stdout.strip().splitlines()
        return out[0] if out else ''
    except Exception:
        return ''

CACHE_PATH = 'data/firstseen.json'
cache = json.load(open(CACHE_PATH, encoding='utf-8')) if os.path.exists(CACHE_PATH) else {}
logged = []
for i, m in enumerate(d['match']):
    if not cache.get(m):
        cache[m] = first_seen(m)
    logged.append(cache[m])
    if i % 50 == 0:
        print(i, '/', len(d), file=sys.stderr, flush=True)
json.dump(cache, open(CACHE_PATH, 'w', encoding='utf-8'))
d['logged_at'] = logged
out = d.rename(columns={'entry': 'entry_odds', 'pin_close': 'pinnacle_close', 'gb_fair': 'gb_fair_odds'})[
    ['logged_at', 'match', 'league', 'pick', 'entry_odds', 'pinnacle_close', 'clv_pct', 'gb_fair_odds', 'result']]
out.to_csv('data/bets.csv', index=False)
print('rows', len(out), 'with logged_at', int((out['logged_at'] != '').sum()))

json.dump({'refreshed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'rows': len(out)}, open('data/meta.json', 'w'))
