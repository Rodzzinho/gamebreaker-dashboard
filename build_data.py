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

def _git_first(args):
    try:
        out = subprocess.run(['git', '-C', REPO, 'log', '--reverse', '--format=%aI'] + args + ['--', 'pinnacle_clv_drift.csv'],
                             capture_output=True, text=True, timeout=120, creationflags=0x08000000).stdout.strip().splitlines()
        return out[0] if out else ''
    except Exception:
        return ''

def first_seen(match, pick):
    """Commit time when this exact match+pick row first appeared (keyed on pick too, so two picks on one match do not share a date)."""
    return _git_first(['-S', f'{match},{pick},']) or _git_first(['-S', match])

def clv_seen(match, pick, clv_text):
    """Commit time when this row first carried its CLV, i.e. when the close was recorded."""
    c = re.escape(str(clv_text).strip())
    return _git_first(['-G', f'^{re.escape(match)},{re.escape(pick)},.*{c}'])

CACHE_PATH = 'data/firstseen.json'
cache = json.load(open(CACHE_PATH, encoding='utf-8')) if os.path.exists(CACHE_PATH) else {}
logged, settled = [], []
for i, (m, p, c) in enumerate(zip(d['match'], d['pick'], d['pin_clv'])):
    k1, k2 = f'{m}|{p}', f'clv|{m}|{p}|{c}'
    if not cache.get(k1):
        cache[k1] = first_seen(m, p)
    if not cache.get(k2):
        cache[k2] = clv_seen(m, p, c)
    logged.append(cache[k1]); settled.append(cache[k2] or cache[k1])
    if i % 25 == 0:
        print(i, '/', len(d), file=sys.stderr, flush=True)
        json.dump(cache, open(CACHE_PATH, 'w', encoding='utf-8'))
json.dump(cache, open(CACHE_PATH, 'w', encoding='utf-8'))
d['clv_logged_at'] = settled
d['logged_at'] = logged
out = d.rename(columns={'entry': 'entry_odds', 'pin_close': 'pinnacle_close', 'gb_fair': 'gb_fair_odds'})[
    ['logged_at', 'clv_logged_at', 'match', 'league', 'pick', 'entry_odds', 'pinnacle_close', 'clv_pct', 'gb_fair_odds', 'result']]
out.to_csv('data/bets.csv', index=False)
print('rows', len(out), 'with logged_at', int((out['logged_at'] != '').sum()))

json.dump({'refreshed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'rows': len(out)}, open('data/meta.json', 'w'))
