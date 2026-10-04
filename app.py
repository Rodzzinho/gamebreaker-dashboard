import html
import math
import urllib.parse

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="GameBreaker closing line record", page_icon="📈", layout="wide")

# Same palette as the GameBreaker app so the two read as one product.
BG, SURFACE, SURFACE2, BORDER = "#09090b", "#18181b", "#1f1f23", "#27272a"
TEXT, DIM, FAINT = "#fafafa", "#a1a1aa", "#6b6f7a"
GREEN, GREEN_BG, RED = "#10b981", "#0d2a20", "#ef4444"
COPY_TRADE_URL = "https://gamebreaker-app.vercel.app/copy-trade"


@st.cache_data(ttl=300)
def load() -> pd.DataFrame:
    d = pd.read_csv("data/bets.csv")
    d["logged_at"] = pd.to_datetime(d["logged_at"], utc=True, errors="coerce")
    d = d.sort_values("logged_at").reset_index(drop=True)
    d["n"] = d.index + 1
    d["running_avg"] = d["clv_pct"].expanding().mean()
    return d


df = load()
N = len(df)
try:
    import json as _json
    _meta = _json.load(open('data/meta.json', encoding='utf-8'))
    UPDATED = pd.to_datetime(_meta['refreshed_utc']).strftime('%d %b %Y, %H:%M UTC')
except Exception:
    UPDATED = ''
mean = df["clv_pct"].mean()
sd = df["clv_pct"].std()
half = 1.96 * sd / math.sqrt(N)
POS = round((df["clv_pct"] > 0).mean() * 100)

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
html, body, [class*="css"], .stApp {{ font-family: 'Space Grotesk', sans-serif; }}
.stApp {{ background: {BG}; }}
.block-container {{ max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem; position: relative; z-index: 1; }}
header[data-testid="stHeader"] {{ background: transparent; }}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {{ visibility: hidden; }}

@property --pick {{ syntax: '<integer>'; initial-value: 0; inherits: false; }}
@property --pos  {{ syntax: '<integer>'; initial-value: 0; inherits: false; }}
@keyframes countpick {{ to {{ --pick: {N}; }} }}
@keyframes countpos  {{ to {{ --pos: {POS}; }} }}
@keyframes rise {{ from {{ opacity:0; transform: translateY(14px); }} to {{ opacity:1; transform:none; }} }}
@keyframes drawline {{ to {{ stroke-dashoffset: 0; }} }}
@keyframes fadein {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
@keyframes floaty {{ 0%,100% {{ transform: translate(0,0) scale(1); }} 50% {{ transform: translate(40px,-30px) scale(1.12); }} }}
@keyframes glow {{ 0%,100% {{ text-shadow: 0 0 0 rgba(16,185,129,0); }} 50% {{ text-shadow: 0 0 28px rgba(16,185,129,.55); }} }}
@keyframes marquee {{ to {{ transform: translateX(-50%); }} }}

.stApp::before, .stApp::after {{ content:""; position:fixed; z-index:0; border-radius:50%; filter: blur(90px); pointer-events:none; }}
.stApp::before {{ width:520px; height:520px; left:-120px; top:60px; background: rgba(16,185,129,.16); animation: floaty 16s ease-in-out infinite; }}
.stApp::after  {{ width:460px; height:460px; right:-100px; top:360px; background: rgba(6,182,212,.10); animation: floaty 22s ease-in-out infinite reverse; }}

.mono {{ font-family:'IBM Plex Mono',monospace; font-variant-numeric: tabular-nums; }}
.hero {{ padding: 6px 0 4px; animation: rise .8s ease both; }}
.eyebrow {{ font-family:'IBM Plex Mono',monospace; font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:{GREEN}; }}
.h1 {{ font-size: clamp(34px, 6vw, 62px); font-weight: 700; letter-spacing: -2px; line-height: 1.02; margin: 10px 0 14px; color:{TEXT}; }}
.h1 em {{ font-style: normal; background: linear-gradient(90deg,{GREEN},#67e8c0); -webkit-background-clip:text; background-clip:text; color:transparent; }}
.lede {{ color:{DIM}; font-size: 17px; line-height:1.55; max-width: 740px; margin-bottom: 18px; }}
.lede b {{ color:{TEXT}; font-weight:600; }}

.ticker {{ overflow:hidden; border:1px solid {BORDER}; border-radius:12px; background:{SURFACE}; margin: 8px 0 22px; white-space:nowrap; animation: rise .9s ease .15s both; }}
.ticker .track {{ display:inline-block; padding: 11px 0; animation: marquee 80s linear infinite; }}
.ticker:hover .track {{ animation-play-state: paused; }}
.tk {{ display:inline-block; margin: 0 22px; font-size:13px; color:{DIM}; }}
.tk b {{ font-family:'IBM Plex Mono',monospace; font-weight:600; margin-left:8px; }}
.up {{ color:{GREEN}; }} .dn {{ color:{RED}; }}

.cards {{ display:grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 8px; }}
@media (max-width: 800px) {{ .cards {{ grid-template-columns: repeat(2, 1fr); }} }}
.card {{ background:{SURFACE}; border:1px solid {BORDER}; border-radius:16px; padding:18px 18px 16px; animation: rise .9s ease both; }}
.card:nth-child(2) {{ animation-delay:.08s; }} .card:nth-child(3) {{ animation-delay:.16s; }} .card:nth-child(4) {{ animation-delay:.24s; }}
.card.hero-card {{ background: linear-gradient(160deg, {GREEN_BG}, {SURFACE} 70%); border-color:#14573f; }}
.k {{ font-size:11px; text-transform:uppercase; letter-spacing:.08em; color:{FAINT}; margin-bottom:8px; }}
.v {{ font-family:'IBM Plex Mono',monospace; font-size:32px; font-weight:600; letter-spacing:-1px; line-height:1; color:{TEXT}; font-variant-numeric: tabular-nums; }}
.v.pos {{ color:{GREEN}; animation: glow 3.2s ease-in-out infinite; }}
.count-pick::after {{ counter-reset: cp var(--pick); content: counter(cp); animation: countpick 1.8s cubic-bezier(.2,.8,.2,1) .3s forwards; }}
.count-pos::after  {{ counter-reset: cq var(--pos);  content: counter(cq) "%"; animation: countpos 1.8s cubic-bezier(.2,.8,.2,1) .5s forwards; }}
.n {{ color:{FAINT}; font-size:12px; margin-top:8px; }}
.note {{ color:{FAINT}; font-size:12.5px; line-height:1.5; margin: 6px 0 22px; }}

.chartwrap {{ background:{SURFACE}; border:1px solid {BORDER}; border-radius:18px; padding:18px 20px 12px; margin: 14px 0 24px; animation: rise .9s ease .25s both; }}
.chartwrap .ttl {{ font-size:20px; font-weight:700; letter-spacing:-.4px; color:{TEXT}; }}
.chartwrap .sub {{ color:{DIM}; font-size:13.5px; margin: 4px 0 8px; }}
.chartwrap .cap {{ display:flex; justify-content:space-between; color:{FAINT}; font-size:12px; margin-top:2px; font-family:'IBM Plex Mono',monospace; }}
.draw {{ fill:none; stroke:{GREEN}; stroke-width:3; stroke-linecap:round; stroke-linejoin:round; stroke-dasharray: 3000; stroke-dashoffset: 3000; animation: drawline 3.4s cubic-bezier(.4,0,.2,1) .5s forwards; }}
.areafill {{ opacity:0; animation: fadein 1.4s ease 2.6s forwards; }}
.dot {{ opacity:0; animation: fadein .6s ease 3.7s forwards; }}

.proof {{ background:{SURFACE}; border:1px solid {BORDER}; border-left:3px solid {GREEN}; border-radius:14px; padding:16px 18px; margin: 4px 0 24px; animation: rise .9s ease .3s both; }}
.proof .lbl {{ font-size:11px; text-transform:uppercase; letter-spacing:.08em; color:{GREEN}; margin-bottom:8px; }}
.flow {{ display:flex; align-items:center; gap:14px; flex-wrap:wrap; }}
.flow .px {{ font-family:'IBM Plex Mono',monospace; font-size:26px; font-weight:600; }}
.flow .arrow {{ color:{FAINT}; font-size:20px; }}
.flow .badge {{ margin-left:auto; background:{GREEN_BG}; color:{GREEN}; font-family:'IBM Plex Mono',monospace; font-weight:600; padding:6px 12px; border-radius:10px; font-size:18px; }}
.flow .lab {{ font-size:10px; text-transform:uppercase; letter-spacing:.08em; color:{FAINT}; display:block; margin-bottom:2px; }}
.proof .meta {{ color:{DIM}; font-size:13px; margin-top:10px; }}

.steps3 {{ display:grid; grid-template-columns: repeat(3,1fr); gap:14px; margin: 6px 0 26px; }}
@media (max-width: 800px) {{ .steps3 {{ grid-template-columns: 1fr; }} }}
.step {{ background:{SURFACE}; border:1px solid {BORDER}; border-radius:16px; padding:16px 18px; animation: rise .9s ease both; }}
.step:nth-child(2) {{ animation-delay:.12s; }} .step:nth-child(3) {{ animation-delay:.24s; }}
.step .no {{ font-family:'IBM Plex Mono',monospace; color:{GREEN}; font-size:12px; margin-bottom:8px; }}
.step .tt {{ font-weight:600; font-size:15px; margin-bottom:4px; color:{TEXT}; }}
.step .dd {{ color:{DIM}; font-size:13px; line-height:1.5; }}

.cta {{ display:flex; align-items:center; justify-content:space-between; gap:18px; flex-wrap:wrap; background: linear-gradient(120deg,{GREEN_BG},{SURFACE} 65%); border:1px solid #14573f; border-radius:18px; padding:22px 24px; margin: 8px 0 26px; animation: rise .9s ease .4s both; }}
.cta .t {{ font-size:22px; font-weight:700; letter-spacing:-.5px; color:{TEXT}; }}
.cta .s {{ color:{DIM}; font-size:14px; margin-top:4px; max-width:560px; line-height:1.5; }}
.btn {{ display:inline-block; background:{GREEN}; color:#04130d !important; font-weight:700; padding:12px 20px; border-radius:12px; text-decoration:none !important; font-size:15px; transition: transform .15s ease, box-shadow .15s ease; }}
.btn:hover {{ transform: translateY(-2px); box-shadow: 0 8px 28px rgba(16,185,129,.35); }}
.btn.ghost {{ background:transparent; color:{TEXT} !important; border:1px solid {BORDER}; margin-left:10px; }}

.quote {{ border-left:3px solid {GREEN}; padding:6px 0 6px 18px; margin: 6px 0 24px; color:{TEXT}; font-size:19px; line-height:1.5; letter-spacing:-.2px; max-width:820px; }}
.quote span {{ display:block; color:{DIM}; font-size:15px; margin-top:6px; letter-spacing:0; }}
.section {{ font-size:18px; font-weight:700; letter-spacing:-.3px; margin: 10px 0 2px; color:{TEXT}; }}
.legal {{ color:{FAINT}; font-size:12px; margin-top: 26px; line-height:1.6; border-top:1px solid {BORDER}; padding-top:14px; }}
div[data-testid="stDataFrame"] {{ border:1px solid {BORDER}; border-radius:14px; overflow:hidden; }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation-duration: .01ms !important; animation-delay: 0s !important; }} .draw {{ stroke-dashoffset: 0 !important; }} .areafill, .dot {{ opacity:1 !important; }} }}
</style>
""",
    unsafe_allow_html=True,
)

# ---- hero ----------------------------------------------------------------------------------
st.markdown(
    f"""
<div class="hero">
  <div class="eyebrow">GameBreaker &middot; closing line record{(" &middot; updated " + UPDATED) if UPDATED else ""}</div>
  <div class="h1">The market moves.<br><em>We were already there.</em></div>
  <div class="lede">Every price below was locked <b>before kick-off</b> and checked against where the market finally closed.
  No screenshots. Just <b>{N} settled picks</b>, each committed to GitHub with a timestamp.</div>
</div>
""",
    unsafe_allow_html=True,
)

tab_live, tab_bt, tab_n, tab_gh = st.tabs(["Live record", "Backtest", "How many bets?", "Proof on GitHub"])
tab_live.__enter__()

# ---- ticker of the most recent verified prints (losers included) ---------------------------
recent = df.sort_values("logged_at", ascending=False).head(26)
items = []
for _, r in recent.iterrows():
    cls = "up" if r["clv_pct"] > 0 else "dn"
    items.append(
        f'<span class="tk">{html.escape(str(r["match"]))} '
        f'<span class="mono">{r["entry_odds"]:.2f} &rarr; {r["pinnacle_close"]:.2f}</span>'
        f'<b class="{cls}">{r["clv_pct"]:+.1f}%</b></span>'
    )
track = "".join(items) * 2
st.markdown(f'<div class="ticker"><div class="track">{track}</div></div>', unsafe_allow_html=True)

# ---- headline cards -------------------------------------------------------------------------
st.markdown(
    f"""
<div class="cards">
  <div class="card hero-card"><div class="k">Average CLV vs Pinnacle close</div><div class="v pos">{mean:+.2f}%</div><div class="n">median {df['clv_pct'].median():+.2f}%</div></div>
  <div class="card"><div class="k">Settled picks</div><div class="v count-pick"></div><div class="n">{df['league'].nunique()} competitions</div></div>
  <div class="card"><div class="k">Positive CLV</div><div class="v count-pos"></div><div class="n">{int((df['clv_pct'] > 0).sum())} of {N} picks</div></div>
  <div class="card"><div class="k">95% range for the average</div><div class="v" style="font-size:24px;padding-top:6px">{mean - half:+.1f}% to {mean + half:+.1f}%</div><div class="n">rough estimate</div></div>
</div>
<div class="note">CLV is not profit: a pick can have positive CLV and still lose. The range assumes picks are independent.</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="quote">You will never eliminate uncertainty from betting, so the real skill is learning to make good '
    'decisions knowing there will always be things you simply cannot predict or control.'
    '<span>Football just gives us a scoreboard at the end.</span></div>',
    unsafe_allow_html=True,
)

# ---- the self-drawing line ------------------------------------------------------------------
W, H, PAD = 1000, 230, 14
start = 10
pts = df[df["n"] >= start][["n", "running_avg"]]
ymin = min(0.0, pts["running_avg"].min()) - 0.3
ymax = pts["running_avg"].max() + 0.3


def sx(n_):
    return (n_ - start) / (N - start) * (W - 2 * PAD) + PAD


def sy(v):
    return H - PAD - (v - ymin) / (ymax - ymin) * (H - 2 * PAD)


step = max(1, len(pts) // 160)
sel = pts.iloc[::step]
if sel.iloc[-1]["n"] != N:
    sel = pd.concat([sel, pts.iloc[[-1]]])
line_pts = " ".join(f"{sx(a):.1f},{sy(b):.1f}" for a, b in zip(sel["n"], sel["running_avg"]))
area_pts = f"{sx(sel.iloc[0]['n']):.1f},{H - PAD} {line_pts} {sx(sel.iloc[-1]['n']):.1f},{H - PAD}"
zero_y = sy(0)
lx, ly = sx(N), sy(mean)
st.markdown(
    f"""
<div class="chartwrap">
  <div class="ttl">{N} picks. One line. Watch it settle.</div>
  <div class="sub">Average CLV after each new pick. Early on it swings. With more picks it steadies, which is why a small sample proves little and a large one starts to.</div>
  <svg viewBox="0 0 {W} {H}" width="100%" preserveAspectRatio="none" style="display:block;height:230px">
    <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GREEN}" stop-opacity=".30"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></linearGradient></defs>
    <line x1="{PAD}" x2="{W - PAD}" y1="{zero_y:.1f}" y2="{zero_y:.1f}" stroke="{FAINT}" stroke-dasharray="5 6" stroke-width="1.2"/>
    <polygon class="areafill" points="{area_pts}" fill="url(#g)"/>
    <polyline class="draw" points="{line_pts}"/>
    <circle class="dot" cx="{lx:.1f}" cy="{ly:.1f}" r="6" fill="{GREEN}"/>
  </svg>
  <div class="cap"><span>pick {start}</span><span>zero line dashed</span><span>pick {N}: {mean:+.2f}%</span></div>
</div>
""",
    unsafe_allow_html=True,
)

# ---- proof example --------------------------------------------------------------------------
ex = df[df["match"].str.contains("Aston Villa v Nottingham Forest", na=False)]
if len(ex):
    r = ex.iloc[0]
    st.markdown(
        f"""
<div class="proof"><div class="lbl">Proof, timestamped a week early</div>
<div class="flow">
  <div><span class="lab">Price taken</span><span class="px">{r['entry_odds']:.2f}</span></div>
  <div class="arrow">&rarr;</div>
  <div><span class="lab">Pinnacle close</span><span class="px" style="color:{DIM}">{r['pinnacle_close']:.2f}</span></div>
  <div class="badge">{r['clv_pct']:+.2f}% CLV</div>
</div>
<div class="meta">{html.escape(str(r['match']))} &middot; pick: {html.escape(str(r['pick']))} &middot; logged {r['logged_at']:%d %b %Y, %H:%M} UTC</div></div>
""",
        unsafe_allow_html=True,
    )

# ---- how it works ---------------------------------------------------------------------------
st.markdown(
    """
<div class="steps3">
  <div class="step"><div class="no">01</div><div class="tt">Lock the price</div><div class="dd">Each pick is logged before kick-off, and the commit time is the timestamp.</div></div>
  <div class="step"><div class="no">02</div><div class="tt">Let the market move</div><div class="dd">Pinnacle's closing price is recorded as the benchmark for that pick.</div></div>
  <div class="step"><div class="no">03</div><div class="tt">Publish the result</div><div class="dd">CLV goes up whether the pick won or lost. The record is the product.</div></div>
</div>
""",
    unsafe_allow_html=True,
)

# ---- call to action -------------------------------------------------------------------------
share_text = f"A football pricing record with {N} timestamped picks and +{mean:.2f}% average CLV against Pinnacle's close. Worth a look: {COPY_TRADE_URL}"
share_url = "https://wa.me/?text=" + urllib.parse.quote(share_text)
st.markdown(
    f"""
<div class="cta">
  <div><div class="t">Want the price before the market closes?</div>
  <div class="s">Copy Trade shows the price I took and the fair price my model says, before kick-off. You place your own bets. Nothing is copied automatically.</div></div>
  <div><a class="btn" href="{COPY_TRADE_URL}" target="_blank" rel="noopener noreferrer">See Copy Trade</a>
  <a class="btn ghost" href="{share_url}" target="_blank" rel="noopener noreferrer">Send to a friend</a></div>
</div>
""",
    unsafe_allow_html=True,
)


# ---- charts ---------------------------------------------------------------------------------
def style_chart(ch, h: int = 290):
    return (
        ch.properties(height=h, background="transparent")
        .configure_view(strokeWidth=0)
        .configure_axis(
            labelColor=DIM, titleColor=FAINT, gridColor=BORDER, domainColor=BORDER, tickColor=BORDER,
            labelFont="IBM Plex Mono", titleFont="Space Grotesk", labelFontSize=11, titleFontSize=11,
        )
    )


c_left, c_right = st.columns(2)
with c_left:
    st.markdown('<div class="section">Average CLV by competition</div>', unsafe_allow_html=True)
    by = df.groupby("league")["clv_pct"].agg(["mean", "count"]).reset_index().sort_values("mean", ascending=False)
    bars = alt.Chart(by).mark_bar(color=GREEN, cornerRadiusEnd=5).encode(
        y=alt.Y("league:N", sort="-x", title=None),
        x=alt.X("mean:Q", title="Average CLV (%)"),
        tooltip=[alt.Tooltip("league:N"), alt.Tooltip("mean:Q", format="+.2f", title="Avg CLV %"), alt.Tooltip("count:Q", title="Picks")],
    )
    labels = alt.Chart(by).mark_text(align="left", dx=6, color=DIM, font="IBM Plex Mono", fontSize=11).encode(
        y=alt.Y("league:N", sort="-x"), x="mean:Q", text=alt.Text("count:Q", format="d")
    )
    st.altair_chart(style_chart(bars + labels, 260), width="stretch")
    st.markdown('<div class="note">The number at the end of each bar is the picks behind it. Smaller samples swing more.</div>', unsafe_allow_html=True)

with c_right:
    st.markdown('<div class="section">Spread of CLV across picks</div>', unsafe_allow_html=True)
    hist = (
        alt.Chart(df)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X("clv_pct:Q", bin=alt.Bin(step=5), title="CLV (%) per pick"),
            y=alt.Y("count():Q", title="Picks"),
            color=alt.condition(alt.datum.clv_pct >= 0, alt.value(GREEN), alt.value(RED)),
            tooltip=[alt.Tooltip("count():Q", title="Picks")],
        )
    )
    st.altair_chart(style_chart(hist, 260), width="stretch")
    st.markdown('<div class="note">Most picks cluster near zero with a long tail either side. That spread is why one result tells you little.</div>', unsafe_allow_html=True)

# ---- best and worst prints (losers shown on purpose) ----------------------------------------
def print_card(r, good):
    cls = "up" if good else "dn"
    return (
        f'<div class="card"><div class="k">{html.escape(str(r["match"]))}</div>'
        f'<div class="v {cls}" style="font-size:26px">{r["clv_pct"]:+.1f}%</div>'
        f'<div class="n">{r["entry_odds"]:.2f} &rarr; {r["pinnacle_close"]:.2f} &middot; {html.escape(str(r["pick"]))}</div></div>'
    )


best = df.nlargest(3, "clv_pct")
worst = df.nsmallest(3, "clv_pct")
st.markdown('<div class="section">Best three and worst three prints</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="cards" style="grid-template-columns: repeat(3, 1fr)">'
    + "".join(print_card(r, True) for _, r in best.iterrows())
    + "".join(print_card(r, False) for _, r in worst.iterrows())
    + '</div><div class="note">The worst prints are shown next to the best on purpose.</div>',
    unsafe_allow_html=True,
)

# ---- bet history ----------------------------------------------------------------------------
st.markdown('<div class="section" style="margin-top:12px">Every pick, with its timestamp</div>', unsafe_allow_html=True)
f1, f2, f3 = st.columns([2, 2, 1])
leagues = f1.multiselect("Competition", sorted(df["league"].unique()), default=[])
q = f2.text_input("Search a match or team")
pos_only = f3.checkbox("Positive CLV only", value=False)

view = df.copy()
if leagues:
    view = view[view["league"].isin(leagues)]
if q:
    view = view[view["match"].str.contains(q, case=False, na=False) | view["pick"].str.contains(q, case=False, na=False)]
if pos_only:
    view = view[view["clv_pct"] > 0]
view = view.sort_values("logged_at", ascending=False)

cols = ["logged_at", "match", "league", "pick", "entry_odds", "pinnacle_close", "clv_pct", "gb_fair_odds", "result"]
shown = view[cols].reset_index(drop=True)


def clv_colour(v):
    if pd.isna(v):
        return ""
    return f"color: {GREEN}; font-weight: 600" if v > 0 else f"color: {RED}; font-weight: 600"


st.dataframe(
    shown.style.map(clv_colour, subset=["clv_pct"]),
    width="stretch",
    hide_index=True,
    height=540,
    column_config={
        "logged_at": st.column_config.DatetimeColumn("Logged (UTC)", format="DD MMM YYYY, HH:mm"),
        "match": "Match",
        "league": "Competition",
        "pick": "Pick",
        "entry_odds": st.column_config.NumberColumn("Price taken", format="%.2f"),
        "pinnacle_close": st.column_config.NumberColumn("Pinnacle close", format="%.2f"),
        "clv_pct": st.column_config.NumberColumn("CLV %", format="%+.2f%%"),
        "gb_fair_odds": st.column_config.NumberColumn("Model fair", format="%.2f"),
        "result": "Result",
    },
)
st.markdown(f'<div class="note">Showing {len(view)} of {N} settled picks. Losers are included on purpose.</div>', unsafe_allow_html=True)
st.download_button(
    "Download this view as CSV",
    view.drop(columns=["n", "running_avg"]).to_csv(index=False),
    "gamebreaker_bet_history.csv",
    "text/csv",
)

tab_live.__exit__(None, None, None)

# ---- backtest tab ---------------------------------------------------------------------------
with tab_bt:
    import json as _bj
    bs_ = _bj.load(open("data/backtest_summary.json", encoding="utf-8"))
    bn, bmean = bs_["n"], bs_["mean"]
    st.markdown(
        f"""
<div class="cards" style="grid-template-columns: repeat(3, 1fr)">
  <div class="card hero-card"><div class="k">Backtest average CLV vs Pinnacle</div><div class="v pos">{bmean:+.2f}%</div><div class="n">replayed on past seasons</div></div>
  <div class="card"><div class="k">Games replayed</div><div class="v">{bn:,}</div><div class="n">{bs_['seasons']} seasons, {bs_['leagues']} leagues</div></div>
  <div class="card"><div class="k">Seasons</div><div class="v" style="font-size:22px;padding-top:6px">{bs_['first']} to {bs_['last']}</div><div class="n">Premier League, La Liga, Ligue 1</div></div>
</div>
<div class="note">A backtest replays the model on past seasons. It is a sanity check, not the timestamped record. The live record is the one that counts, and it sits on the first tab.</div>
<div class="proof"><div class="lbl">Full game-by-game file</div>
<div class="meta" style="margin-top:0">Available on request. Email <a href="mailto:hello@rsrodai.org" style="color:{GREEN}">hello@rsrodai.org</a> and ask for the backtest CSV.</div></div>
""",
        unsafe_allow_html=True,
    )

# ---- sample size tab ------------------------------------------------------------------------
with tab_n:
    st.markdown('<div class="section">How many bets until skill shows?</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="note">Closing line value is noisy per bet (spread {sd:.1f}% in the live record) but the average settles. '
        "Pick an assumed true average CLV and see how many bets it takes before the record can show it.</div>",
        unsafe_allow_html=True,
    )
    default_edge = min(max(round(mean * 4) / 4, 0.25), 5.0)
    edge = st.slider("Assumed true average CLV (%)", 0.25, 5.0, float(default_edge), 0.25)
    n95 = math.ceil((1.645 * sd / edge) ** 2)
    more = "already past it" if N >= n95 else f"{n95 - N:,} more picks"
    st.markdown(
        f"""
<div class="cards" style="grid-template-columns: repeat(3, 1fr)">
  <div class="card hero-card"><div class="k">Bets for about 95% confidence</div><div class="v pos">{n95:,}</div><div class="n">at {edge:.2f}% true CLV, spread {sd:.1f}%</div></div>
  <div class="card"><div class="k">Live record so far</div><div class="v">{N}</div><div class="n">settled picks</div></div>
  <div class="card"><div class="k">Share of the way there</div><div class="v">{min(N / n95, 1) * 100:.0f}%</div><div class="n">{more}</div></div>
</div>
""",
        unsafe_allow_html=True,
    )
    ns = list(range(5, max(n95 * 2, 120) + 1, max(1, n95 // 40)))
    curve = pd.DataFrame({"bets": ns, "chance": [0.5 * (1 + math.erf(edge * math.sqrt(k) / sd / math.sqrt(2))) * 100 for k in ns]})
    line = alt.Chart(curve).mark_line(color=GREEN, strokeWidth=3).encode(
        x=alt.X("bets:Q", title="Number of bets"),
        y=alt.Y("chance:Q", title="Chance the record shows a positive average (%)", scale=alt.Scale(domain=[50, 100])),
        tooltip=[alt.Tooltip("bets:Q"), alt.Tooltip("chance:Q", format=".0f")],
    )
    rule = alt.Chart(pd.DataFrame({"x": [N]})).mark_rule(color=FAINT, strokeDash=[5, 5]).encode(x="x:Q")
    st.altair_chart(style_chart(line + rule, 300), width="stretch")
    st.markdown(
        '<div class="note">The dashed line marks the live record. Assumes bets are independent and the spread stays the same. '
        "Compare that with win rate: a true 3% edge at odds of 3.0 needs about 6,100 bets to show in results.</div>",
        unsafe_allow_html=True,
    )

# ---- github proof tab -----------------------------------------------------------------------
with tab_gh:
    GH = "https://github.com/Rodzzinho/gamebreaker-clv-proof"
    st.markdown(
        f"""
<div class="section">Check it yourself</div>
<div class="lede" style="margin-top:6px">Every pick is a line in a public file on GitHub. GitHub stamps each commit with the time it was made, and that stamp cannot be backdated. Compare the commit time with the kick-off time and you can see the price was locked first.</div>
<div class="steps3">
  <div class="step"><div class="no">01</div><div class="tt">Open the repo</div><div class="dd">The file <span class="mono">pinnacle_clv_drift.csv</span> holds every pick, price taken, closing price and CLV.</div></div>
  <div class="step"><div class="no">02</div><div class="tt">Open the history</div><div class="dd">Click History on the file. Each pick shows the date and time it was added.</div></div>
  <div class="step"><div class="no">03</div><div class="tt">Compare with kick-off</div><div class="dd">If the commit is before kick-off, the price was locked before the market closed.</div></div>
</div>
<div class="cta">
  <div><div class="t">The public record</div><div class="s">Entry prices are timestamped when each pick is logged. Model fair prices are added to the file as they are filled in, so the commit history shows when each one went in.</div></div>
  <div><a class="btn" href="{GH}" target="_blank" rel="noopener noreferrer">Open on GitHub</a></div>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="legal">Education only, not financial advice. 18+ only. Gambling can be harmful. BeGambleAware.org. '
    "Past CLV does not guarantee future results.</div>",
    unsafe_allow_html=True,
)
