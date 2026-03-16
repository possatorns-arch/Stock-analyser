"""
SET Stock Analyser — Value Investor Edition  (Streamlit)
Run:  streamlit run app.py
Deploy: Streamlit Cloud / Render / Railway (free tier)
"""
import warnings; warnings.filterwarnings('ignore')
import streamlit as st
import streamlit.components.v1 as _components
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import yfinance as yf
import pandas as pd
import numpy as np
import urllib.request as _ureq, urllib.parse as _uparse
import xml.etree.ElementTree as _ET
import html as _html_lib
import re as _re
from datetime import datetime as _dt, timezone as _tz, timedelta as _td

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SET Analyser · VI",
    page_icon="🏦", layout="wide",
    initial_sidebar_state="expanded"
)

# ── Connectivity smoke test — shows error immediately instead of blank screen ──
@st.cache_data(ttl=3600, show_spinner=False)
def _check_yfinance():
    try:
        tk = yf.Ticker("PTT.BK")
        px = tk.history(period="5d", timeout=15)
        if px is not None and not px.empty:
            return True, f"OK — PTT.BK: {px['Close'].iloc[-1]:.2f}"
        return False, "Empty data returned — market may be closed or feed blocked"
    except Exception as e:
        return False, str(e)[:120]

st.markdown("""
<style>
/* ══════════════════════════════════════════════════════════════════════════
   DESIGN TOKENS
   ══════════════════════════════════════════════════════════════════════════ */
:root {
  --bg:        #0b1120;
  --bg2:       #111a2e;
  --bg3:       #172038;
  --border:    #1e3358;
  --border2:   #2a4570;
  --txt:       #dce9ff;
  --txt2:      #8ba8cc;
  --txt3:      #4a6480;
  --accent:    #00c8f8;
  --green:     #22d68a;
  --yellow:    #f5c842;
  --red:       #ff5566;
  --orange:    #ff8c42;
  --purple:    #b47eff;
  --radius:    8px;
  --shadow:    0 4px 24px rgba(0,0,0,0.4);
}

/* ══════════════════════════════════════════════════════════════════════════
   BASE
   ══════════════════════════════════════════════════════════════════════════ */
html, body, .stApp {
  background: var(--bg) !important;
  color: var(--txt) !important;
  font-family: 'Sora', system-ui, sans-serif !important;
}
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1440px !important; }

/* ══════════════════════════════════════════════════════════════════════════
   HIDE STREAMLIT CHROME — toolbar, header, footer, deploy button
   ══════════════════════════════════════════════════════════════════════════ */
/* Hide Streamlit toolbar/footer — safe selectors only */
#MainMenu                              { visibility: hidden !important; }
footer                                 { visibility: hidden !important; }
[data-testid="stToolbar"]             { visibility: hidden !important; }
[data-testid="stDecoration"]          { display: none !important; }
[data-testid="stStatusWidget"]        { visibility: hidden !important; }
/* Shrink (don't hide) the header so it takes no space */
header[data-testid="stHeader"]        { height: 0 !important; min-height: 0 !important;
                                         overflow: hidden !important; padding: 0 !important; }
/* Remove the blank space left behind */
.block-container { padding-top: 1rem !important; }

/* ══════════════════════════════════════════════════════════════════════════
   SCROLLBARS — visible and styled
   ══════════════════════════════════════════════════════════════════════════ */
* { scrollbar-width: thin; scrollbar-color: var(--border2) var(--bg2); }
::-webkit-scrollbar        { width: 7px; height: 7px; background: var(--bg2); }
::-webkit-scrollbar-thumb  { background: var(--border2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }

/* ══════════════════════════════════════════════════════════════════════════
   SIDEBAR
   ══════════════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
  padding-top: 0 !important;
}
section[data-testid="stSidebar"] > div { padding-top: 1rem; }
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span { color: var(--txt2) !important; }

/* ══════════════════════════════════════════════════════════════════════════
   TYPOGRAPHY
   ══════════════════════════════════════════════════════════════════════════ */
h1,h2,h3 { color: var(--accent) !important; font-weight: 800 !important;
            letter-spacing: -0.3px; }
p, li { color: var(--txt); line-height: 1.65; }

/* caption / small text */
.stCaption, small, .caption-text {
  color: var(--txt2) !important; font-size: 12px !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   DIVIDER
   ══════════════════════════════════════════════════════════════════════════ */
hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 18px 0 !important; }

/* ══════════════════════════════════════════════════════════════════════════
   TABS  — bright, readable active state
   ══════════════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px !important;
  border-bottom: 2px solid var(--border) !important;
  background: transparent !important;
  padding-bottom: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  color: var(--txt2) !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  padding: 10px 18px !important;
  border-radius: 8px 8px 0 0 !important;
  background: transparent !important;
  border: 1px solid transparent !important;
  border-bottom: none !important;
  transition: all 0.15s !important;
}
.stTabs [data-baseweb="tab"]:hover {
  color: var(--txt) !important;
  background: var(--bg3) !important;
}
.stTabs [aria-selected="true"] {
  color: var(--accent) !important;
  background: var(--bg3) !important;
  border-color: var(--border) !important;
  border-bottom: 2px solid var(--accent) !important;
  margin-bottom: -2px !important;
}
/* tab content area */
.stTabs [data-baseweb="tab-panel"] { padding: 20px 0 0 !important; }

/* ══════════════════════════════════════════════════════════════════════════
   BUTTONS  — high contrast, obvious hover/active
   ══════════════════════════════════════════════════════════════════════════ */
.stButton > button {
  background: var(--bg3) !important;
  color: var(--txt) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--radius) !important;
  font-family: 'Sora', sans-serif !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  padding: 8px 16px !important;
  transition: all 0.15s ease !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
}
.stButton > button:hover {
  background: var(--bg2) !important;
  border-color: var(--accent) !important;
  color: var(--accent) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(0,200,248,0.15) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
/* Primary button */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
  background: linear-gradient(135deg, #0e3060 0%, #0d2550 100%) !important;
  border-color: var(--accent) !important;
  color: var(--accent) !important;
  font-weight: 700 !important;
  letter-spacing: 0.3px !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
  background: linear-gradient(135deg, #1a4580 0%, #153570 100%) !important;
  box-shadow: 0 4px 20px rgba(0,200,248,0.25) !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   INPUTS — clear borders, readable text
   ══════════════════════════════════════════════════════════════════════════ */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stTextInput > div > div {
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
  color: var(--txt) !important;
  border-radius: var(--radius) !important;
}
.stSelectbox > div > div:focus-within,
.stMultiSelect > div > div:focus-within,
.stTextInput > div > div:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(0,200,248,0.15) !important;
}
.stNumberInput > div > div {
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
  color: var(--txt) !important;
  border-radius: var(--radius) !important;
}
/* Dropdown option text */
[data-baseweb="select"] [role="option"] {
  background: var(--bg2) !important;
  color: var(--txt) !important;
}
[data-baseweb="select"] [role="option"]:hover,
[data-baseweb="select"] [aria-selected="true"] {
  background: var(--bg3) !important;
  color: var(--accent) !important;
}
/* Multiselect tag chips — previously near-invisible */
span[data-baseweb="tag"] {
  background: rgba(0,200,248,0.15) !important;
  border: 1px solid rgba(0,200,248,0.35) !important;
  color: var(--accent) !important;
  border-radius: 4px !important;
  font-size: 12px !important;
}
/* Multiselect listbox */
[data-baseweb="popover"] ul {
  background: var(--bg2) !important;
  border: 1px solid var(--border2) !important;
}
[data-baseweb="popover"] li {
  color: var(--txt) !important;
}
[data-baseweb="popover"] li:hover {
  background: var(--bg3) !important;
}
/* Remove icon on chips */
span[data-baseweb="tag"] span { color: var(--txt2) !important; }

/* ══════════════════════════════════════════════════════════════════════════
   SELECTBOX arrow + text contrast
   ══════════════════════════════════════════════════════════════════════════ */
[data-baseweb="select"] svg { color: var(--txt2) !important; }
[data-baseweb="select"] > div { color: var(--txt) !important; }

</style>""", unsafe_allow_html=True)
st.markdown("""
<style>/* ══════════════════════════════════════════════════════════════════════════
   PROGRESS BAR  (screener loading)
   ══════════════════════════════════════════════════════════════════════════ */
.stProgress > div > div { background: var(--bg3) !important; border-radius: 4px; }
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--accent), var(--green)) !important;
  border-radius: 4px !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   ALERTS / INFO / WARNING / SUCCESS / ERROR
   ══════════════════════════════════════════════════════════════════════════ */
[data-testid="stAlert"] {
  border-radius: var(--radius) !important;
  border-width: 1px !important;
}
[data-testid="stAlert"][data-baseweb="notification"][kind="info"] {
  background: rgba(0,200,248,0.08) !important;
  border-color: rgba(0,200,248,0.3) !important;
  color: var(--txt) !important;
}
[data-testid="stAlert"][kind="success"] {
  background: rgba(34,214,138,0.08) !important;
  border-color: rgba(34,214,138,0.3) !important;
  color: var(--txt) !important;
}
[data-testid="stAlert"][kind="warning"] {
  background: rgba(245,200,66,0.08) !important;
  border-color: rgba(245,200,66,0.3) !important;
  color: var(--txt) !important;
}
[data-testid="stAlert"][kind="error"] {
  background: rgba(255,85,102,0.08) !important;
  border-color: rgba(255,85,102,0.3) !important;
  color: var(--txt) !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   METRICS
   ══════════════════════════════════════════════════════════════════════════ */
div[data-testid="metric-container"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  padding: 14px !important;
}
div[data-testid="metric-container"] label { color: var(--txt2) !important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
  color: var(--txt) !important; font-weight: 700 !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   SPINNER / STATUS
   ══════════════════════════════════════════════════════════════════════════ */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ══════════════════════════════════════════════════════════════════════════
   CUSTOM CLASSES used in sidebar HTML
   ══════════════════════════════════════════════════════════════════════════ */
.sidebar-label {
  color: var(--txt2) !important;
  font-size: 11px !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 1px !important;
  margin-bottom: 8px !important;
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
}
.sidebar-divider {
  border: none; border-top: 1px solid var(--border);
  margin: 14px -12px !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   NUMBER INPUT — stepper arrows visible
   ══════════════════════════════════════════════════════════════════════════ */
.stNumberInput button {
  background: var(--bg3) !important;
  border-color: var(--border2) !important;
  color: var(--txt) !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   COLUMN GAPS — less cramped
   ══════════════════════════════════════════════════════════════════════════ */
[data-testid="stHorizontalBlock"] { gap: 12px !important; }
</style>""", unsafe_allow_html=True)

# ─── Universe ──────────────────────────────────────────────────────────────────
SET100 = [
    "AAV","ADVANC","AEONTS","AMATA","AOT","AP","AWC",
    "BA","BAM","BANPU","BBL","BCH","BCP","BCPG","BDMS","BEM","BGRIM","BH","BJC","BLA","BTG","BTS",
    "CBG","CCET","CENTEL","CHG","CK","CKP","COCOCO","COM7","CPALL","CPF","CPN","CRC",
    "DELTA","DOHOME","EA","EGCO","ERW",
    "GLOBAL","GPSC","GULF","GUNKUL","HANA","HMPRO",
    "ICHI","IRPC","ITC","IVL","JAS","JMART","JMT",
    "KBANK","KCE","KKP","KTB","KTC","LH",
    "M","MEGA","MINT","MOSHI","MTC","OR","OSP",
    "PLANB","PR9","PRM","PTT","PTTEP","PTTGC","QH","RATCH","RCL","ROJNA",
    "SAPPE","SAWAD","SCB","SCC","SCGP","SIRI","SISB","SJWD","SKY","SNNP",
    "SPALI","SPRC","STA","STGT","TASCO","TCAP","TIDLOR","TISCO","TLI","TOP",
    "TRUE","TTB","TU","VGI","WHA",
]
MAI_TICKERS = [
    "ADVICE","ASK","A5","BBGI","BEC","CHEWA","DITTO","EPG",
    "FORTH","GCAP","KAMART","MASTER","MFEC","MBK","MONO","MORE",
    "NETBAY","NEO","PLANET","PM","RBF","RS","SCGD","SGC","SKR",
    "SMPC","SPA","SSP","THRE","TPCH","VIH",
]
DR_TICKERS = [
    "E1VFVN3001","FUEVFVND01","EQHVN30U1","FUEVN100",
    "STAR5001","CNTECH01","BABA80","TENCENT80","XIAOMI80","BYDCOM80",
    "NDX01","AAPL80X","TSLA80X",
]

SECTOR_MAP = {
    "Banking":      ["BBL","KBANK","KTB","SCB","BAY","KKP","TISCO","TTB","TCAP"],
    "Finance":      ["KTC","MTC","JMT","BLA","AEONTS","BAM","SAWAD","TIDLOR","ASK","THRE"],
    "Energy":       ["PTT","PTTEP","PTTGC","TOP","BANPU","BCP","BCPG","BGRIM","EA",
                     "EGCO","GULF","GPSC","GUNKUL","CKP","RATCH","IRPC","SPRC","OR","BBGI","EPG","SSP","TPCH"],
    "Tech/Telecom": ["ADVANC","TRUE","JAS","CCET","SKY","SISB","ADVICE","DITTO","FORTH","MFEC","NETBAY","NEO"],
    "Property":     ["LH","CPN","SIRI","SPALI","WHA","AWC","AP","QH","AMATA","ROJNA",
                     "A5","CHEWA","MORE","SCGD"],
    "Healthcare":   ["BDMS","BH","CHG","BCH","PR9","SPA","VIH"],
    "Commerce":     ["CPALL","BJC","OSP","CBG","HMPRO","COM7","CRC","DOHOME","GLOBAL","MEGA","MOSHI",
                     "KAMART","MBK","MASTER"],
    "Food":         ["CPF","TU","STA","BTG","ITC","ICHI","SAPPE","SNNP","COCOCO","PM","RBF"],
    "Industrial":   ["SCC","SCGP","IVL","DELTA","HANA","KCE","TASCO","SMPC"],
    "Transport":    ["AOT","BTS","BEM","AAV","BA","RCL","PRM","SJWD"],
    "Media/Leisure":["PLANB","VGI","MINT","CENTEL","ERW","M","JMART","RS","BEC","MONO"],
}

def to_yf(sym): return sym + ".BK"

# ─── Core helpers ───────────────────────────────────────────────────────────────
def ema(p, n=30):    return p.ewm(span=n).mean()
def strip_tz(idx):   return idx.tz_localize(None) if idx.tz else idx
def ts_filter(df, s):
    if df.empty: return df
    ts = pd.Timestamp(s)
    if df.index.tz: ts = ts.tz_localize(df.index.tz)
    return df[df.index >= ts]

def calc_rsi(p, n=14):
    d = p.diff(); g = d.clip(lower=0); l = -d.clip(upper=0)
    ag = g.ewm(com=n-1, min_periods=n).mean()
    al = l.ewm(com=n-1, min_periods=n).mean()
    return 100 - (100/(1 + ag/al))

def safe_row(df, *keys):
    if df is None or df.empty: return pd.Series(dtype=float)
    for k in keys:
        if k in df.index: return df.loc[k].sort_index()
    return pd.Series(dtype=float)

def trailing_div_yield(divs, price_df):
    try:
        d = divs.copy(); d.index = strip_tz(d.index)
        trail = d[d.index >= pd.Timestamp.now() - pd.DateOffset(years=1)].sum()
        cp = price_df['Close'].iloc[-1] if not price_df.empty else 0
        return trail / cp * 100 if cp > 0 and trail > 0 else None
    except: return None

def style_ax(ax):
    ax.set_facecolor('#0b1120')
    ax.tick_params(colors='#8ba8cc', labelsize=9)
    ax.grid(axis='y', color='#1e3358', linewidth=0.6, linestyle='--', alpha=0.7)
    ax.grid(axis='x', color='#172038', linewidth=0.3, alpha=0.5)
    for sp in ax.spines.values(): sp.set_edgecolor('#1e3358')

# ─── Data fetch (cached 6h) ─────────────────────────────────────────────────────
@st.cache_data(ttl=21600, show_spinner=False)
def fetch_all(ticker):
    """Fetch all yfinance data with retry logic for Streamlit Cloud."""
    import time
    data = dict(ticker=ticker, info={}, price=pd.DataFrame(),
                income=pd.DataFrame(), balance=pd.DataFrame(),
                cashflow=pd.DataFrame(), divs=pd.Series(dtype=float))
    for attempt in range(3):
        try:
            tk = yf.Ticker(ticker)
            end = pd.Timestamp.now()
            # info first — if this times out, skip rather than crash
            try:
                info = tk.info or {}
                data['info'] = info if isinstance(info, dict) else {}
            except Exception: data['info'] = {}
            try:
                px = tk.history(interval='1d',
                                start=end - pd.DateOffset(years=10), end=end,
                                timeout=30)
                if not px.empty: data['price'] = px
            except Exception: pass
            try:
                inc = tk.income_stmt
                if inc is not None and not (hasattr(inc,'empty') and inc.empty):
                    data['income'] = inc
            except Exception: pass
            try:
                bal = tk.balance_sheet
                if bal is not None and not (hasattr(bal,'empty') and bal.empty):
                    data['balance'] = bal
            except Exception: pass
            try:
                cf = tk.cashflow
                if cf is not None and not (hasattr(cf,'empty') and cf.empty):
                    data['cashflow'] = cf
            except Exception: pass
            try:
                dv = tk.dividends
                if dv is not None and len(dv) > 0:
                    data['divs'] = dv
            except Exception: pass
            break  # success — exit retry loop
        except Exception:
            if attempt < 2:
                time.sleep(2 ** attempt)  # 1s, 2s backoff
            continue
    return data

# ─── 1. Price chart ──────────────────────────────────────────────────────────────
EMA_W = [25,75,200]; EMA_C = ['deeppink','limegreen','grey']; EMA_L = ['EMA 25','EMA 75','EMA 200']

def make_price_chart(ticker, start):
    d = fetch_all(ticker); df = ts_filter(d['price'], start)
    fig = plt.figure(figsize=(14, 5.5), facecolor='#0b1120')
    if df.empty:
        plt.text(0.5, 0.5, f"No price data — {ticker}", ha='center', va='center',
                 color='white', transform=fig.transFigure, fontsize=14)
        return fig
    gs = gridspec.GridSpec(3, 1, figure=fig, hspace=0,
                           height_ratios=[3.0, 0.9, 0.7])
    ax_p = fig.add_subplot(gs[0]); ax_r = fig.add_subplot(gs[1]); ax_v = fig.add_subplot(gs[2])
    close = df['Close']; dates = close.index; n_days = len(df)
    dy = trailing_div_yield(d['divs'], d['price'])

    ax_p.plot(dates, close, lw=1.8, color='white', zorder=3)
    for w,c,l in zip(EMA_W, EMA_C, EMA_L):
        ax_p.plot(dates, ema(close,w), lw=1.1, color=c, alpha=0.85, label=l, zorder=2)
    e25 = ema(close, 25)
    ax_p.fill_between(dates, close, e25, where=(close>=e25), alpha=0.08, color='limegreen')
    ax_p.fill_between(dates, close, e25, where=(close< e25), alpha=0.08, color='deeppink')
    style_ax(ax_p); ax_p.set_ylabel('THB', fontsize=9, color='#aaa')
    ax_p.set_xlim(dates[0], dates[-1])
    ax_p.set_title(ticker, fontsize=13, fontweight='bold', color='white', loc='left', pad=6)
    ep = close.iloc[-1]
    ax_p.annotate(f"▼ from MAX  {(ep-close.max())/close.max()*100:.1f}%",
                  xy=(0.01,0.96), xycoords='axes fraction', fontsize=9.5,
                  color='#ff5566', va='top', fontfamily='monospace', fontweight='bold')
    ax_p.annotate(f"▲ from MIN  +{(ep-close.min())/close.min()*100:.1f}%",
                  xy=(0.50,0.96), xycoords='axes fraction', fontsize=9.5,
                  color='#22d68a', va='top', ha='center', fontfamily='monospace', fontweight='bold')
    if dy:
        ax_p.annotate(f"Div: {dy:.2f}%", xy=(0.99,0.96), xycoords='axes fraction',
                      fontsize=8.5, color='#f0c040', va='top', ha='right',
                      fontfamily='monospace',
                      bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1a1a',
                                edgecolor='#333', alpha=0.8))
    ax_p.legend(fontsize=7.5, loc='lower right', facecolor='#1a1a1a',
                edgecolor='#333', labelcolor='white', framealpha=0.8)
    plt.setp(ax_p.get_xticklabels(), visible=False)

    rsi_v = calc_rsi(close); cr = rsi_v.iloc[-1]
    rc = '#ef5350' if cr>=70 else ('#26c6da' if cr<=30 else '#b0bec5')
    ax_r.plot(dates, rsi_v, lw=1.2, color=rc, zorder=3)
    ax_r.axhline(70, color='#ef5350', lw=0.7, ls='--', alpha=0.6)
    ax_r.axhline(30, color='#26c6da', lw=0.7, ls='--', alpha=0.6)
    ax_r.axhline(50, color='#444',    lw=0.5, ls=':',  alpha=0.5)
    ax_r.fill_between(dates, rsi_v, 70, where=(rsi_v>=70), alpha=0.12, color='#ef5350')
    ax_r.fill_between(dates, rsi_v, 30, where=(rsi_v<=30), alpha=0.12, color='#26c6da')
    style_ax(ax_r); ax_r.set_xlim(dates[0], dates[-1]); ax_r.set_ylim(0,100)
    ax_r.set_yticks([30,50,70]); ax_r.set_ylabel('RSI', fontsize=8, color='#aaa')
    ax_r.annotate(f"RSI {cr:.1f}", xy=(0.01,0.85), xycoords='axes fraction',
                  fontsize=7.5, color=rc, va='top', fontfamily='monospace')
    plt.setp(ax_r.get_xticklabels(), visible=False)

    vc = np.where(df['Close']>=df['Open'], '#3d9970', '#e74c3c')
    ax_v.bar(dates, df['Volume'], color=vc, alpha=0.7, width=1.2)
    style_ax(ax_v); ax_v.set_ylabel('Vol', fontsize=7, color='#555')
    ax_v.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x,_: f"{x/1e6:.0f}M" if x>=1e6 else f"{x/1e3:.0f}K"))
    ax_v.set_xlim(dates[0], dates[-1])
    if n_days <= 365:
        ax_v.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
        ax_v.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    else:
        ax_v.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax_v.xaxis.set_major_locator(mdates.YearLocator())
    ax_v.tick_params(axis='x', colors='#aaa', labelsize=9)

    plt.tight_layout()
    return fig

# ─── 2. Financial tables ────────────────────────────────────────────────────────
def _auto_scale(df):
    try:
        med = df.abs().median().median()
        if med >= 1e9: return 1e9, "Billions (B THB)"
        if med >= 1e6: return 1e6, "Millions (M THB)"
    except: pass
    return 1.0, "THB"

def _df_to_html(df, title, max_years=10):
    if df is None or df.empty:
        return f"<p style='color:#4a6480;font-style:italic;padding:8px'>No data for {title}</p>"
    cols = sorted(df.columns)[-max_years:]
    sub  = df[cols].copy(); col_lbs = [str(c)[:4] for c in cols]
    scale, ulabel = _auto_scale(sub)
    TH = ("padding:8px 14px;color:#00c8f8;text-align:right;background:#131e38;"
          "border-bottom:2px solid #2a4570;font-size:11px;font-weight:700;"
          "letter-spacing:0.5px;white-space:nowrap")
    hdr = "".join(f"<th style='{TH}'>{y}</th>" for y in col_lbs)
    rows = ""
    for i, (rn, rd) in enumerate(sub.iterrows()):
        bg = "#0e1830" if i%2==0 else "#111e38"
        cells = ""
        for col in cols:
            try:
                v = float(rd[col])
                txt = "—" if pd.isna(v) else f"{v/scale:,.2f}"
                clr = "#4a6480" if pd.isna(v) else ("#ff7a85" if v<0 else "#5ef0aa")
            except: txt,clr = "—","#4a6480"
            cells += (f"<td style='padding:6px 14px;text-align:right;color:{clr};"
                      f"font-size:12px;font-family:JetBrains Mono,monospace;"
                      f"border-bottom:1px solid #1e3358'>{txt}</td>")
        rows += (f"<tr style='background:{bg}'>"
                 f"<td style='padding:6px 10px;color:#c8dcf8;font-size:12px;"
                 f"border-bottom:1px solid #1e3358;white-space:nowrap;max-width:260px;"
                 f"overflow:hidden;text-overflow:ellipsis'>{str(rn)[:55]}</td>{cells}</tr>")
    return (f"<div style='margin:16px 0;border:1px solid #1e3358;border-radius:10px;overflow:hidden'>"
            f"<div style='background:#0e1830;padding:10px 14px;border-bottom:1px solid #1e3358;"
            f"display:flex;align-items:baseline;gap:10px'>"
            f"<span style='color:#00c8f8;font-size:14px;font-weight:700'>{title}</span>"
            f"<span style='color:#4a6480;font-size:11px'>({ulabel})</span></div>"
            f"<div style='overflow-x:auto'><table style='border-collapse:collapse;width:100%;min-width:600px'>"
            f"<thead><tr>"
            f"<th style='padding:8px 10px;color:#8ba8cc;text-align:left;background:#131e38;"
            f"border-bottom:2px solid #2a4570;font-size:11px;font-weight:700'>Line Item</th>{hdr}"
            f"</tr></thead><tbody>{rows}</tbody></table></div></div>")

# ─── 3. Fundamental chart ───────────────────────────────────────────────────────
def make_fundamental_chart(ticker):
    DARK='#0b1120'; ACC='#00d4ff'; POS='#26c6da'; NEG='#ef5350'; WARN='#f0c040'; GRN='#4ecca3'
    d=fetch_all(ticker); inc=d['income']; bal=d['balance']; cf=d['cashflow']; divs=d['divs']; pr=d['price']
    revenue      = safe_row(inc,'Total Revenue')
    gross_profit = safe_row(inc,'Gross Profit')
    net_income   = safe_row(inc,'Net Income')
    ebitda       = safe_row(inc,'EBITDA','Normalized EBITDA')
    cogs         = safe_row(inc,'Cost Of Revenue','Reconciled Cost Of Revenue')
    total_equity = safe_row(bal,'Stockholders Equity','Total Equity Gross Minority Interest')
    total_assets = safe_row(bal,'Total Assets')
    total_debt   = safe_row(bal,'Total Debt','Long Term Debt')
    curr_assets  = safe_row(bal,'Current Assets'); curr_liab = safe_row(bal,'Current Liabilities')
    op_cf        = safe_row(cf, 'Operating Cash Flow','Cash Flow From Continuing Operating Activities')
    capex        = safe_row(cf, 'Capital Expenditure')
    free_cf      = (op_cf+capex) if not op_cf.empty and not capex.empty else pd.Series(dtype=float)
    def der(a,b):
        if a.empty or b.empty: return pd.Series(dtype=float)
        return (a/b*100).replace([np.inf,-np.inf],np.nan)
    gross_margin  = der(gross_profit, revenue); net_margin = der(net_income, revenue)
    roe = der(net_income, total_equity); roa = der(net_income, total_assets)
    de  = (total_debt/total_equity).replace([np.inf,-np.inf],np.nan) \
          if not total_debt.empty and not total_equity.empty else pd.Series(dtype=float)
    cr  = (curr_assets/curr_liab).replace([np.inf,-np.inf],np.nan) \
          if not curr_assets.empty and not curr_liab.empty else pd.Series(dtype=float)
    dy_ts = pd.Series(dtype=float)
    if not divs.empty and not pr.empty:
        try:
            dv=divs.copy(); dv.index=strip_tz(dv.index)
            pc=pr['Close'].copy(); pc.index=strip_tz(pc.index)
            dy_dict={}
            for yr in sorted(set(dv.index.year)):
                ann=dv[dv.index.year==yr].sum()
                px=pc[pc.index<=pd.Timestamp(f"{yr}-12-31")]
                if not px.empty and px.iloc[-1]>0: dy_dict[pd.Timestamp(f"{yr}-12-31")]=ann/px.iloc[-1]*100
            dy_ts=pd.Series(dy_dict)
        except: pass

    fig,axes=plt.subplots(4,3,figsize=(14,15),facecolor=DARK,gridspec_kw={'hspace':0.55,'wspace':0.35})
    fig.suptitle(f"  {ticker}  —  Fundamental Trend Analysis",fontsize=14,fontweight='bold',
                 color='white',backgroundcolor='#0e2040',y=1.01,x=0.5,ha='center')

    def bar(ax,s,title,unit='B THB',thr=None,pc=POS,nc=NEG,tc='#f0c040',sc=1e9):
        ax.set_facecolor(DARK)
        for sp in ax.spines.values(): sp.set_edgecolor('#2a2a2a')
        ax.tick_params(colors='#aaa',labelsize=8)
        ax.grid(axis='y',color='#1e1e1e',linewidth=0.5,linestyle='--',zorder=0)
        if s is None or s.empty:
            ax.text(0.5,0.5,'No data',ha='center',va='center',color='#444',
                    transform=ax.transAxes,fontsize=10); ax.set_title(title,color=ACC,fontsize=10,pad=6); return
        xs=[str(x)[:4] for x in s.index]
        ys=(s.values/sc).astype(float) if sc!=1 else s.values.astype(float)
        bc=[pc if v>=0 else nc for v in ys]
        bars=ax.bar(xs,ys,color=bc,alpha=0.85,zorder=3,edgecolor='#0d0d0d',linewidth=0.4)
        for b,v in zip(bars,ys):
            if np.isnan(v): continue
            ax.text(b.get_x()+b.get_width()/2,v+abs(max(ys,default=0))*0.02,
                    f"{v:.1f}",ha='center',va='bottom',fontsize=7,color='#aaa',fontfamily='monospace')
        if thr is not None:
            ax.axhline(thr,color=tc,lw=1.2,ls='--',alpha=0.7,zorder=4)
            ax.text(0.01,thr,f" {thr}{unit}",transform=ax.get_yaxis_transform(),fontsize=7,color=tc,va='bottom')
        ax.set_title(title,color=ACC,fontsize=10,pad=6); ax.set_ylabel(unit,fontsize=8,color='#666')
        ax.tick_params(axis='x',rotation=45,labelsize=8); ax.set_xlim(-0.6,len(xs)-0.4)

    bar(axes[0,0],revenue/1e9,"Revenue",unit='B THB',pc=POS)
    if not revenue.empty and not cogs.empty:
        xs=[str(x)[:4] for x in revenue.index]; axes[0,1].set_facecolor(DARK)
        for sp in axes[0,1].spines.values(): sp.set_edgecolor('#2a2a2a')
        axes[0,1].tick_params(colors='#aaa',labelsize=8)
        axes[0,1].grid(axis='y',color='#1e1e1e',lw=0.5,ls='--',zorder=0)
        rv=revenue.values/1e9; cg=abs(cogs.values)/1e9
        gp=gross_profit.values/1e9 if not gross_profit.empty else rv-cg
        xp=np.arange(len(xs))
        axes[0,1].bar(xp,rv,label='Revenue',color='#1e4a6e',alpha=0.9,zorder=2)
        axes[0,1].bar(xp,cg,label='Cost',color=NEG,alpha=0.8,zorder=3)
        axes[0,1].bar(xp,gp,label='Gross Profit',color=GRN,alpha=0.8,zorder=4,bottom=cg)
        axes[0,1].set_xticks(xp); axes[0,1].set_xticklabels(xs,rotation=45,fontsize=8)
        axes[0,1].legend(fontsize=7,labelcolor='white',facecolor='#1a1a2e',edgecolor='#333',loc='upper left')
        axes[0,1].set_title("Revenue vs Cost vs Gross Profit",color=ACC,fontsize=10,pad=6)
        axes[0,1].set_ylabel("B THB",fontsize=8,color='#666')
    else: bar(axes[0,1],gross_profit/1e9,"Gross Profit",unit='B THB',pc=GRN)
    bar(axes[0,2],net_income/1e9,"Net Income",unit='B THB',pc=WARN)
    bar(axes[1,0],gross_margin,"Gross Margin",unit='%',thr=20,pc=GRN,sc=1)
    bar(axes[1,1],net_margin,  "Net Margin",  unit='%',thr=10,pc=GRN,sc=1)
    bar(axes[1,2],ebitda/1e9,  "EBITDA",unit='B THB',pc='#ab47bc')
    bar(axes[2,0],roe,"ROE",unit='%',thr=15,pc=POS,sc=1)
    bar(axes[2,1],roa,"ROA",unit='%',thr=8, pc=POS,sc=1)
    bar(axes[2,2],de, "D/E Ratio",unit='×',thr=1.0,pc='#ef9a9a',nc=NEG,tc=WARN,sc=1)
    bar(axes[3,0],free_cf/1e9,"Free Cash Flow",unit='B THB',thr=0,pc=GRN,tc='#888')
    bar(axes[3,1],cr,"Current Ratio",unit='×',thr=1.5,pc=GRN,tc=WARN,sc=1)
    bar(axes[3,2],dy_ts,"Dividend Yield",unit='%',thr=1.0,pc=WARN,tc='#888',sc=1)
    plt.tight_layout(rect=[0,0,1,0.99])
    return fig

# ─── 4. VI Scorecard ────────────────────────────────────────────────────────────
def _s(s,n=-1):
    try: s2=s.sort_index().dropna(); return float(s2.iloc[n]) if len(s2)>=abs(n) else None
    except: return None
def _med(s,y=5):
    try: return float(s.sort_index().dropna().iloc[-y:].median())
    except: return None
def _all_pos(s):
    try: s2=s.sort_index().dropna(); return bool((s2>0).all()) and len(s2)>0
    except: return False

def compute_beneish(inc,bal,cf):
    try:
        revenue=safe_row(inc,'Total Revenue').sort_index().dropna()
        gross_profit=safe_row(inc,'Gross Profit').sort_index().dropna()
        net_income=safe_row(inc,'Net Income').sort_index().dropna()
        receivables=safe_row(bal,'Receivables','Net Receivables','Accounts Receivable').sort_index().dropna()
        total_assets=safe_row(bal,'Total Assets').sort_index().dropna()
        curr_assets=safe_row(bal,'Current Assets').sort_index().dropna()
        ppe=safe_row(bal,'Net PPE','Net Property Plant Equipment','Property Plant Equipment').sort_index().dropna()
        total_debt=safe_row(bal,'Total Debt','Long Term Debt').sort_index().dropna()
        curr_liab=safe_row(bal,'Current Liabilities').sort_index().dropna()
        op_cf=safe_row(cf,'Operating Cash Flow','Cash Flow From Continuing Operating Activities').sort_index().dropna()
        common=revenue.index.intersection(total_assets.index)
        if len(common)<2: return None,'Insufficient data','#555'
        t,t1=common[-1],common[-2]
        def g(s,i): return float(s[i]) if i in s.index else None
        rv=g(revenue,t); rv1=g(revenue,t1); gp=g(gross_profit,t); gp1=g(gross_profit,t1)
        rc=g(receivables,t); rc1=g(receivables,t1); ta=g(total_assets,t); ta1=g(total_assets,t1)
        ca=g(curr_assets,t); ca1=g(curr_assets,t1); pp=g(ppe,t); pp1=g(ppe,t1)
        ni=g(net_income,t); oc=g(op_cf,t); td=g(total_debt,t); td1=g(total_debt,t1)
        cl=g(curr_liab,t); cl1=g(curr_liab,t1)
        comp={}
        if all(v and v!=0 for v in [rc,rv,rc1,rv1]): comp['DSRI']=(rc/rv)/(rc1/rv1)
        if all(v and v!=0 for v in [gp,rv,gp1,rv1]): comp['GMI']=(gp1/rv1)/(gp/rv)
        if all(v and v!=0 for v in [ca,pp,ta,ca1,pp1,ta1]):
            comp['AQI']=(1-(ca+pp)/ta)/(1-(ca1+pp1)/ta1)
        if rv and rv1 and rv1!=0: comp['SGI']=rv/rv1
        if all(v is not None for v in [td,cl,ta,td1,cl1,ta1]) and ta!=0 and ta1!=0:
            comp['LVGI']=((td+cl)/ta)/((td1+cl1)/ta1)
        if ni is not None and oc is not None and ta and ta!=0: comp['TATA']=(ni-oc)/ta
        if len(comp)<3: return None,'Insufficient data','#555'
        coef={'DSRI':0.920,'GMI':0.528,'AQI':0.404,'SGI':0.892,'LVGI':-0.327,'TATA':4.679}
        m=-4.84+sum(coef.get(k,0)*v for k,v in comp.items())
        if m>-1.78:   return m,'🚨 HIGH','#ef5350'
        elif m>-2.22: return m,'⚠️ GREY','#f0c040'
        else:         return m,'✅ CLEAN','#4ecca3'
    except: return None,'N/A','#555'

def detect_cycle(s,label):
    try:
        s2=s.sort_index().dropna()
        if len(s2)<3: return None
        hm=float(s2.iloc[-5:].median()); ra=float(s2.iloc[-2:].mean())
        if hm==0: return None
        pct=(ra-hm)/abs(hm)*100
        if pct<-25: return {'label':label,'pct':pct,'hist':hm,'recent':ra}
    except: pass
    return None

def compute_vi_scorecard(ticker):
    d=fetch_all(ticker); inc=d['income']; bal=d['balance']; cf=d['cashflow']
    info=d['info']; divs=d['divs']; price_df=d['price']
    revenue=safe_row(inc,'Total Revenue'); gross_profit=safe_row(inc,'Gross Profit')
    net_income=safe_row(inc,'Net Income')
    total_equity=safe_row(bal,'Stockholders Equity','Total Equity Gross Minority Interest')
    total_assets=safe_row(bal,'Total Assets'); total_debt=safe_row(bal,'Total Debt','Long Term Debt')
    curr_assets=safe_row(bal,'Current Assets'); curr_liab=safe_row(bal,'Current Liabilities')
    op_cf=safe_row(cf,'Operating Cash Flow','Cash Flow From Continuing Operating Activities')
    capex=safe_row(cf,'Capital Expenditure')
    interest_exp=safe_row(inc,'Interest Expense'); ebit=safe_row(inc,'Operating Income','EBIT')
    receivables=safe_row(bal,'Receivables','Net Receivables','Accounts Receivable')
    free_cf=(op_cf+capex) if not op_cf.empty and not capex.empty else pd.Series(dtype=float)
    def der(a,b):
        if a.empty or b.empty: return pd.Series(dtype=float)
        return (a/b*100).replace([np.inf,-np.inf],np.nan)
    roe_s=der(net_income,total_equity); nm_s=der(net_income,revenue); gm_s=der(gross_profit,revenue)
    result={'ticker':ticker,'sections':{},'cycle_flags':[],'red_flags':[]}

    # A. Business Quality
    sec_a=[]
    try:
        rev=revenue.sort_index().dropna(); n=min(5,len(rev)-1)
        cagr=((rev.iloc[-1]/rev.iloc[-1-n])**(1/n)-1)*100 if len(rev)>=2 else None
        sec_a.append(('Revenue CAGR (5Y)','>7%',f"{cagr:.1f}%" if cagr else 'N/A',
                      cagr is not None and cagr>=7,'Durable growth compounders grow faster than GDP'))
    except: sec_a.append(('Revenue CAGR (5Y)','>7%','N/A',False,''))
    gm_med=_med(gm_s)
    sec_a.append(('Gross Margin (5Y median)','>40%',f"{gm_med:.1f}%" if gm_med else 'N/A',
                  gm_med is not None and gm_med>=40,'>40% signals durable pricing power / moat'))
    nm_med=_med(nm_s)
    sec_a.append(('Net Margin (5Y median)','>10%',f"{nm_med:.1f}%" if nm_med else 'N/A',
                  nm_med is not None and nm_med>=10,'Efficient businesses with real pricing power'))
    roe_med=_med(roe_s)
    sec_a.append(('ROE (5Y median)','>15%',f"{roe_med:.1f}%" if roe_med else 'N/A',
                  roe_med is not None and roe_med>=15,"Buffett's classic ROE floor"))
    earn_ok=_all_pos(net_income)
    sec_a.append(('Earnings Consistency','All years +','✓ No loss years' if earn_ok else '✗ Has loss years',
                  earn_ok,'Loss years signal structural weakness'))
    result['sections']['A']=('🏆 Business Quality',sec_a)

    # B. Financial Health
    sec_b=[]
    de=_s(total_debt/total_equity) if not total_debt.empty and not total_equity.empty else None
    sec_b.append(('D/E Ratio','<0.5×',f"{de:.2f}×" if de is not None else 'N/A',
                  de is not None and de<0.5,'Fortress balance sheet'))
    crat=_s(curr_assets/curr_liab) if not curr_assets.empty and not curr_liab.empty else None
    sec_b.append(('Current Ratio','>1.5×',f"{crat:.2f}×" if crat is not None else 'N/A',
                  crat is not None and crat>=1.5,'Comfortable short-term liquidity'))
    try:
        ic=float(ebit.iloc[-1]/abs(interest_exp.iloc[-1])) if not ebit.empty and not interest_exp.empty else None
        sec_b.append(('Interest Coverage','>5×',f"{ic:.1f}×" if ic else 'N/A',
                      ic is not None and ic>=5,'>5× means earnings easily service debt'))
    except: sec_b.append(('Interest Coverage','>5×','N/A',False,''))
    fcf_ok=_all_pos(free_cf); fcf_v=_s(free_cf)
    sec_b.append(('FCF (all years)','Always +',
                  f"✓ Latest: {fcf_v/1e9:.2f}B" if fcf_ok and fcf_v else '✗ Has negative FCF years',
                  fcf_ok,'Owner earnings — the only truly real profit (Buffett)'))
    result['sections']['B']=('💪 Financial Health',sec_b)

    # C. Earnings Integrity
    sec_c=[]
    try:
        fa,na=free_cf.align(net_income,join='inner')
        fa=fa.sort_index().dropna(); na=na.sort_index().dropna()
        rs=(fa/na).replace([np.inf,-np.inf],np.nan).dropna()
        cc=float(rs.iloc[-3:].median()) if len(rs)>=1 else None
        ok=cc is not None and cc>=0.8
        if cc is not None and cc<0.5:
            result['red_flags'].append(('🚨 Cash Conversion Crisis',
                f"FCF/NI = {cc:.2f} — only {cc*100:.0f}% of profit is backed by cash."))
        sec_c.append(('Cash Conversion (FCF/NI)','>0.8',f"{cc:.2f}" if cc else 'N/A',
                      ok,'Profit not converting to cash = accounting red flag'))
    except: sec_c.append(('Cash Conversion (FCF/NI)','>0.8','N/A',False,''))
    try:
        oc_s=op_cf.sort_index(); ni_s2=net_income.sort_index(); ta_s=total_assets.sort_index()
        idx=oc_s.index.intersection(ni_s2.index).intersection(ta_s.index)
        if len(idx)>=1:
            acc=((ni_s2[idx]-oc_s[idx])/ta_s[idx]*100); al=float(acc.iloc[-1])
            ok=abs(al)<=5
            if abs(al)>10:
                result['red_flags'].append(('🚨 High Accruals',
                    f"Accruals = {al:.1f}% of assets. High accruals predict underperformance (Sloan 1996)."))
            sec_c.append(('Accruals Ratio','|acc|<5% assets',f"{al:.1f}%",ok,'High accruals = earnings driven by estimates not cash'))
        else: raise ValueError
    except: sec_c.append(('Accruals Ratio','|acc|<5% assets','N/A',False,''))
    try:
        rv=revenue.sort_index().dropna(); rc=receivables.sort_index().dropna()
        i2=rv.index.intersection(rc.index)
        if len(i2)>=2:
            rg=(rv[i2].iloc[-1]/rv[i2].iloc[-2]-1)*100; rcg=(rc[i2].iloc[-1]/rc[i2].iloc[-2]-1)*100
            dv=rcg-rg; ok=dv<=15
            if dv>30:
                result['red_flags'].append(('🚨 Revenue Recognition Risk',
                    f"Receivables +{rcg:.1f}% vs revenue +{rg:.1f}% (gap: +{dv:.1f}pp)."))
            sec_c.append(('Receivables vs Revenue','Gap<15pp',
                          f"Rec:{rcg:+.1f}%  Rev:{rg:+.1f}%  Gap:{dv:+.1f}pp",ok,
                          'Receivables outgrowing revenue = channel stuffing risk'))
        else: raise ValueError
    except: sec_c.append(('Receivables vs Revenue','Gap<15pp','N/A',False,''))
    try:
        gs=gm_s.sort_index().dropna(); std=float(gs.std()); ok=std<=8
        if std>15:
            result['red_flags'].append(('⚠️ Volatile Gross Margin',
                f"GM std dev = {std:.1f}pp. Wild swings suggest accounting adjustments."))
        sec_c.append(('Gross Margin Stability','Std<8pp',f"{std:.1f}pp",ok,'Stable margins = durable moat'))
    except: sec_c.append(('Gross Margin Stability','Std<8pp','N/A',False,''))
    result['sections']['C']=('🔬 Earnings Integrity',sec_c)

    # D. Beneish M-Score
    m,ml,mc=compute_beneish(inc,bal,cf); m_ok=m is not None and m<=-2.22
    if m is not None and m>-1.78:
        result['red_flags'].append(('🚨 Beneish M-Score Alert',
            f"M={m:.3f} (threshold −1.78). Statistical model flags earnings manipulation."))
    elif m is not None and m>-2.22:
        result['red_flags'].append(('⚠️ Beneish Grey Zone',f"M={m:.3f}. Ambiguous — investigate further."))
    result['sections']['D']=('🕵️ Fraud Risk (Beneish)',
        [('Beneish M-Score','<−2.22',f"{m:.3f} {ml}" if m else ml,m_ok,
          'Statistical fraud model — M>−1.78 = high manipulation risk')])

    # E. Valuation
    sec_e=[]
    try:
        cp=price_df['Close'].iloc[-1] if not price_df.empty else None
        sh=info.get('sharesOutstanding') or info.get('impliedSharesOutstanding')
        ni_s2=net_income.sort_index().dropna()
        if cp and sh and len(ni_s2)>=1:
            mni=float(ni_s2.iloc[-5:].median()); meps=mni/float(sh)
            npe=cp/meps if meps>0 else None; ok=npe is not None and 0<npe<20
            sec_e.append(('Normalized P/E (5Y)','<20×',f"{npe:.1f}×" if npe else 'N/A',ok,
                          'Median earnings removes cyclical distortion'))
        else: raise ValueError
    except: sec_e.append(('Normalized P/E (5Y)','<20×','N/A',False,''))
    try:
        pb=float(info.get('priceToBook'))
        sec_e.append(('Price/Book','<3×',f"{pb:.2f}×",0<pb<3,'Graham margin of safety'))
    except: sec_e.append(('Price/Book','<3×','N/A',False,''))
    dy=trailing_div_yield(divs,price_df)
    sec_e.append(('Dividend Yield','>1%',f"{dy:.2f}%" if dy else 'N/A',(dy or 0)>=1.0,'Cash returned confirms real profit'))
    try:
        per=float(info.get('trailingPE') or info.get('forwardPE'))
        rev2=revenue.sort_index().dropna(); n=min(5,len(rev2)-1)
        cagr2=((rev2.iloc[-1]/rev2.iloc[-1-n])**(1/n)-1) if len(rev2)>=2 else None
        if cagr2 and cagr2>0 and per:
            peg=per/(cagr2*100); ok=peg<1.5
            if peg<1.0:
                result['red_flags'].insert(0,('💎 PEG Opportunity',
                    f"PEG={peg:.2f} — Peter Lynch's 'growth at reasonable price' sweet spot."))
            sec_e.append(('PEG Ratio (P/E÷growth)','<1.5',f"{peg:.2f}",ok,
                          'Lynch: PEG<1 = paying less than growth rate'))
        else: raise ValueError
    except: sec_e.append(('PEG Ratio','<1.5','N/A',False,''))
    result['sections']['E']=('💰 Valuation',sec_e)

    # F. Cash Reality Check
    sec_f=[]
    try:
        ni_s2=net_income.sort_index().dropna(); op_s=op_cf.sort_index().dropna()
        rv2=revenue.sort_index().dropna()
        common=ni_s2.index.intersection(op_s.index).intersection(rv2.index); yrs=list(common)[-5:]
        phantom=[str(y)[:4] for y in yrs
                 if float(ni_s2[y])>float(rv2[y])*0.005 and float(op_s[y])<0]
        ok=len(phantom)<3
        if not ok:
            result['red_flags'].append(('🚨 Phantom Profit Pattern',
                f"NI>0 but OCF<0 in {len(phantom)}/5 years ({', '.join(phantom)}). Profit not arriving as cash."))
        sec_f.append(('Phantom Profit Check','NI>0 and OCF<0 <3yr',
                      f"⚠️ {len(phantom)}/5 years" if not ok else f"✓ {len(phantom)}/5 years",ok,
                      'OCF is pre-capex — real profits always generate positive OCF'))
    except: sec_f.append(('Phantom Profit','<3yr','N/A',True,''))
    # F2 — NI vs OCF raw display
    try:
        lines=[]
        common2=net_income.index.intersection(op_cf.index).intersection(free_cf.index if not free_cf.empty else net_income.index)
        for yr in list(sorted(common2))[-6:]:
            ni_v=net_income[yr]/1e9 if yr in net_income.index else float('nan')
            oc_v=op_cf[yr]/1e9    if yr in op_cf.index    else float('nan')
            fc_v=free_cf[yr]/1e9  if yr in free_cf.index and not free_cf.empty else float('nan')
            lines.append(f"{str(yr)[:4]}: NI={ni_v:.1f}B OCF={oc_v:.1f}B FCF={fc_v:.1f}B")
        sec_f.append(('Raw NI/OCF/FCF','visual check','  |  '.join(lines) if lines else 'N/A',True,
                      'OCF should roughly track NI — divergence is the first fraud signal'))
    except: sec_f.append(('Raw NI/OCF/FCF','visual','N/A',True,''))
    result['sections']['F']=('🏴‍☠️ Cash Reality Check',sec_f)

    for s2,lbl in [(roe_s,'ROE'),(nm_s,'Net Margin'),(gm_s,'Gross Margin')]:
        f=detect_cycle(s2,lbl)
        if f: result['cycle_flags'].append(f)
    return result

def render_vi_scorecard_st(res):
    ticker=res['ticker']; sections=res['sections']
    red_flags=res['red_flags']; cycle_flags=res['cycle_flags']
    sec_scores={}
    for sid,(title,crit) in sections.items():
        n=len(crit); p=sum(1 for *_,ok,_ in crit if ok)
        sec_scores[sid]=(p,n,p/n*100 if n else 0)
    q=['A','B','C','D','E']
    tp=sum(sec_scores.get(s,(0,0,0))[0] for s in q); tn=sum(sec_scores.get(s,(0,0,0))[1] for s in q)
    overall=tp/tn*100 if tn else 0
    fd=sections.get('D',(None,[]))[1]; b_ok=fd[0][3] if fd else True
    gd=sections.get('F',(None,[]))[1]; ph_ok=gd[0][3] if gd else True
    has_wide=any('Phantom' in t or 'Widening' in t for t,_ in red_flags)
    if not b_ok and not ph_ok: verdict='🚨 SERIOUS RED FLAGS'; vc='#ff5566'
    elif not ph_ok:            verdict='🚨 PHANTOM PROFIT';    vc='#ff5566'
    elif not b_ok:             verdict='⚠️ Beneish Risk';       vc='#f5c842'
    elif has_wide:             verdict='⚠️ Cash Gap — Monitor'; vc='#f5c842'
    elif overall>=72:          verdict='✅ Strong Buy Candidate';vc='#22d68a'
    elif overall>=55:          verdict='⚠️ Research Further';   vc='#f5c842'
    else:                      verdict='❌ Avoid';               vc='#ff5566'

    SC={'A':'#00c8f8','B':'#22d68a','C':'#f5c842','D':'#ff5566','E':'#b47eff','F':'#ff8c42'}

    col1,col2=st.columns([3,1])
    with col1:
        st.markdown(
            f"<h3 style='color:#00c8f8;margin:0 0 4px;letter-spacing:-0.3px'>"
            f"🔍 {ticker} — Value Investor Scorecard</h3>"
            f"<p style='color:#5a7898;font-size:12px;margin:0'>"
            f"5-section · cycle-adjusted · Beneish · Buffett/Graham</p>",
            unsafe_allow_html=True)
    with col2:
        st.markdown(
            f"<div style='text-align:right;background:#111a2e;border:1px solid #1e3358;"
            f"border-radius:10px;padding:12px 16px'>"
            f"<div style='font-size:30px;font-weight:800;color:{vc};line-height:1'>{overall:.0f}%</div>"
            f"<div style='color:{vc};font-size:12px;font-weight:600;margin:6px 0 4px'>{verdict}</div>"
            f"<div style='color:#4a6480;font-size:10px'>{tp}/{tn} criteria passed</div></div>",
            unsafe_allow_html=True)

    # Section progress cards
    cols=st.columns(5)
    for i,(sid,lbl) in enumerate([('A','Quality'),('B','Health'),('C','Integrity'),('D','Fraud'),('E','Value')]):
        if sid in sec_scores:
            p,n,pct=sec_scores[sid]
            bc='#22d68a' if pct>=70 else ('#f5c842' if pct>=50 else '#ff5566')
            with cols[i]:
                st.markdown(
                    f"<div style='text-align:center;background:#111a2e;border:1px solid #1e3358;"
                    f"border-radius:10px;padding:12px 8px'>"
                    f"<div style='color:{SC[sid]};font-size:10px;font-weight:700;text-transform:uppercase;"
                    f"letter-spacing:0.8px;margin-bottom:6px'>{lbl}</div>"
                    f"<div style='color:#dce9ff;font-size:24px;font-weight:800;line-height:1'>{pct:.0f}%</div>"
                    f"<div style='color:#4a6480;font-size:10px;margin:4px 0 8px'>{p}/{n} passed</div>"
                    f"<div style='background:#172038;border-radius:4px;height:8px;overflow:hidden'>"
                    f"<div style='width:{pct:.0f}%;height:8px;background:{bc};border-radius:4px'>"
                    f"</div></div></div>",
                    unsafe_allow_html=True)
    st.markdown("---")

    # Cycle flags
    if cycle_flags:
        items="  ·  ".join(f"📉 {f['label']}: recent {f['recent']:.1f}% vs 5Y {f['hist']:.1f}% ({f['pct']:+.1f}pp)"
                            for f in cycle_flags)
        st.info(f"🔄 **Cycle Detector** — {items}")

    # Red flags
    for title,msg in red_flags:
        if title.startswith('💎'): st.success(f"**{title}** — {msg}")
        elif '🚨' in title:       st.error  (f"**{title}** — {msg}")
        else:                      st.warning(f"**{title}** — {msg}")

    # Section tables
    for sid,(stitle,crit) in sections.items():
        p,n,pct=sec_scores[sid]
        _bc='#22d68a' if pct>=70 else ('#f5c842' if pct>=50 else '#ff5566')
        _sc_col=SC.get(sid,'#8ba8cc')
        rows=""
        for lbl,tgt,val,ok,expl in crit:
            ic='✅' if ok else '❌'
            rb='rgba(34,214,138,0.07)' if ok else 'rgba(255,85,102,0.07)'
            vc2='#22d68a' if ok else '#ff5566'
            rows+=(f"<tr style='background:{rb};border-bottom:1px solid #1e3358'>"
                   f"<td style='padding:7px 10px;color:#dce9ff;font-size:12px;white-space:nowrap'>{ic} {lbl}</td>"
                   f"<td style='padding:7px 10px;color:#6a88aa;font-size:11px;line-height:1.4'>{expl}</td>"
                   f"<td style='padding:7px 10px;color:#8ba8cc;font-size:11px;text-align:center;"
                   f"white-space:nowrap'>{tgt}</td>"
                   f"<td style='padding:7px 10px;color:{vc2};font-size:12px;font-weight:700;"
                   f"text-align:right;font-family:JetBrains Mono,monospace;white-space:nowrap'>{val}</td></tr>")
        st.markdown(
            f"<div style='margin-bottom:16px;border:1px solid #1e3358;border-radius:10px;overflow:hidden'>"
            f"<div style='background:#0e1830;padding:10px 14px;border-bottom:1px solid #1e3358;"
            f"display:flex;align-items:center;gap:10px'>"
            f"<span style='color:{_sc_col};font-size:14px;font-weight:700'>{stitle}</span>"
            f"<span style='color:#4a6480;font-size:11px;background:#172038;border-radius:12px;"
            f"padding:2px 8px'>{p}/{n}</span>"
            f"<div style='flex:1;background:#172038;border-radius:3px;height:6px'>"
            f"<div style='width:{pct:.0f}%;height:6px;background:{_bc};border-radius:3px'></div></div>"
            f"<span style='color:{_bc};font-size:12px;font-weight:700'>{pct:.0f}%</span></div>"
            f"<table style='width:100%;border-collapse:collapse'>"
            f"<thead><tr style='background:#111a2e'>"
            f"<th style='padding:6px 10px;color:#5a7898;font-size:10px;text-align:left;"
            f"text-transform:uppercase;letter-spacing:0.7px;font-weight:700'>Criterion</th>"
            f"<th style='padding:6px 10px;color:#5a7898;font-size:10px;text-align:left;"
            f"text-transform:uppercase;letter-spacing:0.7px;font-weight:700'>Why it matters</th>"
            f"<th style='padding:6px 10px;color:#5a7898;font-size:10px;text-align:center;"
            f"text-transform:uppercase;letter-spacing:0.7px;font-weight:700'>Target</th>"
            f"<th style='padding:6px 10px;color:#5a7898;font-size:10px;text-align:right;"
            f"text-transform:uppercase;letter-spacing:0.7px;font-weight:700'>Value</th>"
            f"</tr></thead><tbody>{rows}</tbody></table></div>",
            unsafe_allow_html=True
        )
    st.caption("Thresholds: Buffett / Graham / Beneish (1999). Quality metrics use 5Y medians. Not financial advice.")


def _classify(text):
    t=text.lower(); bs,bc=0,None
    for sev,cat,kws in RISK_KW:
        if any(kw in t for kw in kws) and sev>bs: bs,bc=sev,cat
    return bs,bc,any(kw in t for kw in POS_KW)

def _company_name(base): return TICKER_NAMES.get(base, f"{base} Thailand")

def _is_relevant(title, base, trusted=False):
    if trusted: return True
    t=title.lower(); name=_company_name(base).lower()
    skip={"thai","group","holdings","public","company","thailand","limited","stock",
          "property","power","energy","bank","hotel","hospital","retail","media",
          "advertising","hardware","beverage","insurance","refinery","telecom",
          "cement","chemical","poultry","rubber","seafood","food"}
    words=[w for w in name.split() if len(w)>3 and w not in skip]
    if any(w in t for w in words): return True
    thai_terms=TICKER_THAI.get(base,[])
    if any(th.lower() in t for th in thai_terms): return True
    if _re.search(r'(?<![a-z])'+_re.escape(base.lower())+r'(?![a-z])',t,_re.I): return True
    return False

def _google_rss(query, n=8):
    out=[]
    try:
        url="https://news.google.com/rss/search?q="+_uparse.quote(query)+"&hl=en&gl=TH&ceid=TH:en"
        req=_ureq.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with _ureq.urlopen(req,timeout=10) as r: root=_ET.fromstring(r.read())
        for item in root.findall(".//item")[:n]:
            title=_html_lib.unescape(item.findtext("title",""))
            link=item.findtext("link","")
            pub=item.findtext("pubDate","")
            desc=_html_lib.unescape(item.findtext("description",""))
            src=item.find("{https://news.google.com/rss}source")
            try: date=_dt.strptime(pub[:25],"%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%d")
            except: date=pub[:10]
            out.append({"title":title,"link":link,"source":src.text if src else "Google News",
                        "date":date,"snippet":_re.sub(r'<[^>]+>',' ',desc)[:300]})
    except: pass
    return out

def _bkk_post_rss(base, n=12):
    """Bangkok Post business feed — includes description snippet."""
    out=[]
    try:
        url="https://www.bangkokpost.com/rss/data/business.xml"
        req=_ureq.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with _ureq.urlopen(req,timeout=8) as r: root=_ET.fromstring(r.read())
        name=_company_name(base).lower()
        skip={"thai","group","holdings","public","company","thailand","limited","stock",
              "property","power","energy","bank","hotel"}
        words=[w for w in name.split() if len(w)>3 and w not in skip]
        thai_terms=[t.lower() for t in TICKER_THAI.get(base,[])]
        for item in root.findall(".//item"):
            title=_html_lib.unescape(item.findtext("title",""))
            desc=_html_lib.unescape(item.findtext("description",""))
            combined=(title+" "+desc).lower()
            if (any(w in combined for w in words) or
                any(th in combined for th in thai_terms) or
                base.lower() in combined):
                link=item.findtext("link","")
                pub=item.findtext("pubDate","")
                try: date=_dt.strptime(pub[:25],"%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%d")
                except: date=pub[:10]
                out.append({"title":title,"link":link,"source":"Bangkok Post",
                            "date":date,"snippet":_re.sub(r'<[^>]+>',' ',desc)[:300]})
                if len(out)>=n: break
    except: pass
    return out

def _yf_news(ticker, n=12):
    out=[]
    try:
        for art in (yf.Ticker(ticker).news or [])[:n]:
            ct=art.get("content",{})
            title=ct.get("title",art.get("title",""))
            link=(ct.get("canonicalUrl") or {}).get("url","") or (ct.get("clickThroughUrl") or {}).get("url","")
            pub=art.get("providerPublishTime",0)
            date=_dt.fromtimestamp(pub,tz=_tz.utc).strftime("%Y-%m-%d") if pub else ""
            if title: out.append({"title":title,"link":link,"source":"Yahoo Finance",
                                  "date":date,"snippet":""})
    except: pass
    return out

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_all_news(ticker):
    base=ticker.replace(".BK","")
    name=_company_name(base)
    thai_terms=TICKER_THAI.get(base,[])
    raw=[dict(i,trusted=True) for i in _yf_news(ticker)]
    # English Google queries
    for q in [f'"{name}"', f'"{name}" fraud investigation scandal',
              f'"{name}" SEC DSI audit lawsuit OR criminal']:
        raw+=[dict(i,trusted=True) for i in _google_rss(q,n=8)]
    # Thai Google queries (critical for Thai fraud coverage)
    if thai_terms:
        primary=thai_terms[0]
        for q in [f'"{primary}"',
                  f'"{primary}" \u0e17\u0e38\u0e08\u0e23\u0e34\u0e15 \u0e2a\u0e2d\u0e1a\u0e2a\u0e27\u0e19',
                  f'"{primary}" \u0e01.\u0e25.\u0e15. \u0e14\u0e2a\u0e2e.']:
            raw+=[dict(i,trusted=True) for i in _google_rss(q,n=6)]
    # Bangkok Post — rich snippets, company-filtered
    raw+=[dict(i,trusted=True) for i in _bkk_post_rss(base,n=10)]
    # Broad Thai stock query (lower trust)
    raw+=[dict(i,trusted=False) for i in _google_rss(f'{base} \u0e2a\u0e15\u0e4a\u0e2d\u0e01 \u0e2a\u0e2d\u0e1a\u0e2a\u0e27\u0e19',n=4)]

    # Deduplicate + relevance filter
    seen=set(); out=[]
    for item in raw:
        title=item.get("title",""); trusted=item.get("trusted",False)
        k=title[:48].lower().strip()
        if not k or k in seen: continue
        if not _is_relevant(title,base,trusted=trusted): continue
        # For untrusted items, also check snippet
        snippet=item.get("snippet","")
        if not trusted and snippet and not _is_relevant(snippet,base,trusted=False):
            continue
        seen.add(k)
        out.append({kk:vv for kk,vv in item.items() if kk!="trusted"})
    out.sort(key=lambda x: x.get("date",""),reverse=True)
    return out

def render_news_st(ticker, articles):
    base=ticker.replace(".BK","")
    if not articles:
        st.info(f"No news found for {base}. Try searching Bangkok Post directly.")
        return
    now=_dt.now()
    max_sev=0; flagged=0; positives=0
    for art in articles:
        t=art.get("title",""); snip=art.get("snippet","")
        sev,cat,is_pos=_classify(t+" "+snip)
        if sev>=3: flagged+=1
        if is_pos: positives+=1
        if sev>max_sev: max_sev=sev
    if max_sev>=4 or flagged>=3:   ov="🚨 High Risk";  ov_c="#ff5566"
    elif max_sev>=3 or flagged>=1: ov="⚠️ Caution";    ov_c="#f5c842"
    else:                           ov="✅ Clean";       ov_c="#22d68a"
    _nh = (
        "<div style='background:#111a2e;border:1px solid #1e3358;border-radius:10px;"
        "padding:14px 18px;margin-bottom:16px;display:flex;align-items:center;gap:16px;flex-wrap:wrap'>"
        "<span style='color:#00c8f8;font-size:17px;font-weight:700'>"
        f"📰 {base} News</span>"
        "<div style='width:1px;height:22px;background:#2a4570'></div>"
        f"<span style='color:{ov_c};font-size:13px;font-weight:700'>{ov}</span>"
        f"<span style='color:#4a6480;font-size:11px;margin-left:auto'>"
        f"{len(articles)} articles · "
        f"<b style='color:#dce9ff'>{flagged}</b> flagged · "
        f"<b style='color:#22d68a'>{positives}</b> positive</span></div>"
    )
    st.markdown(_nh, unsafe_allow_html=True)
    SEV_C={4:"#ff1744",3:"#ff5566",2:"#f5c842",1:"#8ba8cc",0:"#2a4570"}
    SEV_L={4:"CRITICAL",3:"HIGH",2:"MEDIUM",1:"LOW",0:""}
    for art in articles:
        title=art.get("title",""); link=art.get("link","")
        src2=art.get("source",""); date_s=art.get("date",""); snip=art.get("snippet","")
        sev,cat,is_pos=_classify(title+" "+snip)
        age_days=999
        try: age_days=(now-_dt.strptime(date_s,"%Y-%m-%d")).days
        except: pass
        opacity=1.0 if age_days<=90 else (0.65 if age_days<=365 else 0.35)
        if is_pos: bdr="#22d68a"; lbl="✅ POSITIVE"
        elif sev>0: bdr=SEV_C[sev]; lbl=f"{'🚨' if sev>=4 else '🔴' if sev>=3 else '🟡'} {SEV_L[sev]}: {cat}"
        else: bdr="#1e3358"; lbl=""
        age_note="" if age_days<=365 else f" · <span style='color:#f5c842'>⏰ {age_days//365}y ago</span>"
        snip_html=(f"<div style='color:#5a7898;font-size:11px;margin-top:6px;line-height:1.5;"
                   f"border-top:1px solid #172038;padding-top:6px'>{snip[:200]}…</div>") if snip and sev>0 else ""
        _flag = (f"<span style='color:{bdr};font-weight:700;padding:1px 7px;"
                 f"border-radius:4px;background:{bdr}22'>{lbl}</span>") if lbl else ""
        _card = (
            f"<div style='border-left:3px solid {bdr};padding:10px 14px;margin-bottom:6px;"
            f"background:#0e1830;border-radius:0 8px 8px 0;opacity:{opacity}'>"
            f"<div style='display:flex;justify-content:space-between;align-items:flex-start;gap:10px'>"
            f"<a href='{link}' target='_blank' style='color:#c8dcf8;text-decoration:none;"
            f"font-size:13px;flex:1;line-height:1.55;font-weight:500'>{title}</a>"
            f"<span style='color:#4a6480;font-size:10px;white-space:nowrap;background:#172038;"
            f"padding:2px 8px;border-radius:4px;flex-shrink:0'>{src2}</span></div>"
            f"<div style='color:#4a6480;font-size:10px;margin-top:6px;display:flex;gap:8px;flex-wrap:wrap;align-items:center'>"
            f"<span>📅 {date_s}</span>{age_note}{_flag}</div>"
            f"{snip_html}</div>"
        )
        st.markdown(_card, unsafe_allow_html=True)


def compute_quick_score(ticker_yf):
    try:
        res=compute_vi_scorecard(ticker_yf)
        secs=res['sections']
        sec_sc={}
        for sid,(t,crit) in secs.items():
            n=len(crit); p=sum(1 for *_,ok,_ in crit if ok)
            sec_sc[sid]=(p,n,p/n*100 if n else 0)
        q=['A','B','C','D','E']
        tp=sum(sec_sc.get(s,(0,0,0))[0] for s in q); tn=sum(sec_sc.get(s,(0,0,0))[1] for s in q)
        overall=tp/tn*100 if tn else 0
        b_ok=sec_sc.get('D',(0,0,0))[2]>=50
        gd=secs.get('F',(None,[]))[1]; ph_ok=gd[0][3] if gd else True
        if not b_ok and not ph_ok: verdict='🚨 Serious Flags'
        elif not ph_ok:            verdict='🚨 Phantom Profit'
        elif not b_ok:             verdict='⚠️ Beneish Risk'
        elif overall>=72:          verdict='✅ Strong Buy'
        elif overall>=55:          verdict='⚠️ Research More'
        else:                      verdict='❌ Avoid'
        d=fetch_all(ticker_yf); info=d['info']
        revenue=safe_row(d['income'],'Total Revenue')
        net_income=safe_row(d['income'],'Net Income')
        total_equity=safe_row(d['balance'],'Stockholders Equity','Total Equity Gross Minority Interest')
        total_debt=safe_row(d['balance'],'Total Debt','Long Term Debt')
        op_cf=safe_row(d['cashflow'],'Operating Cash Flow','Cash Flow From Continuing Operating Activities')
        capex=safe_row(d['cashflow'],'Capital Expenditure')
        cagr=None
        try:
            rv=revenue.sort_index().dropna(); n=min(5,len(rv)-1)
            if len(rv)>=2: cagr=round(((rv.iloc[-1]/rv.iloc[-1-n])**(1/n)-1)*100,1)
        except: pass
        roe=None
        try:
            if not net_income.empty and not total_equity.empty:
                roe=round(float((net_income/total_equity*100).sort_index().dropna().iloc[-5:].median()),1)
        except: pass
        de=None
        try:
            if not total_debt.empty and not total_equity.empty:
                de=round(float((total_debt/total_equity).sort_index().dropna().iloc[-1]),2)
        except: pass
        fcf_ok=False
        try:
            if not op_cf.empty and not capex.empty:
                fcf_ok=bool(((op_cf+capex)>0).all())
        except: pass
        m,ml,_=compute_beneish(d['income'],d['balance'],d['cashflow'])
        pe=info.get('trailingPE') or info.get('forwardPE')
        # Use trailing_div_yield — avoids the yfinance Thai-stock unit bug
        # (info['dividendYield'] for .BK stocks returns e.g. 2.79 meaning 2.79%,
        #  NOT 0.0279 as it does for US stocks — multiplying by 100 gives 279%)
        dy = trailing_div_yield(d['divs'], d['price'])
        base=ticker_yf.replace('.BK','')
        name=TICKER_NAMES.get(base, "")
        return {"Ticker":base,"Company":name,"VI Score":round(overall,1),"Verdict":verdict,
                "Rev CAGR%":cagr,"ROE%":roe,"D/E":de,
                "P/E":round(float(pe),1) if pe else None,
                "Div%":round(dy,1) if dy else None,
                "M-Score":round(m,2) if m else None,
                "FCF+":fcf_ok,
                "A%":round(sec_sc.get('A',(0,0,0))[2]),"B%":round(sec_sc.get('B',(0,0,0))[2]),
                "C%":round(sec_sc.get('C',(0,0,0))[2]),"D%":round(sec_sc.get('D',(0,0,0))[2]),
                "E%":round(sec_sc.get('E',(0,0,0))[2])}
    except Exception as e:
        base = ticker_yf.replace('.BK','')
        return {"Ticker":base,"Company":TICKER_NAMES.get(base,""),
                "VI Score":0,"Verdict":"Error",
                "Rev CAGR%":None,"ROE%":None,"D/E":None,"P/E":None,"Div%":None,
                "M-Score":None,"FCF+":False,"A%":0,"B%":0,"C%":0,"D%":0,"E%":0,
                "_err":str(e)}

def _sc(p):
    return "#22d68a" if p>=72 else ("#f5c842" if p>=55 else "#ff5566")

def _build_screener_page(rows):
    """Return a full standalone HTML page — safe to pass to components.html()."""
    def cell(v, fmt, good, bad):
        if v is None: return "<span style='color:#334'>—</span>"
        ok = good(v); fail = bad(v)
        c = "#4ecca3" if ok else ("#ef5350" if fail else "#f0c040")
        return f"<span style='color:{c}'>{fmt.format(v)}</span>"

    def badge(verdict):
        if "Strong"   in verdict: bg,tc,ic="#0a2016","#22d68a","✅"
        elif "Serious" in verdict or "Phantom" in verdict: bg,tc,ic="#220808","#ff5566","🚨"
        elif "Beneish" in verdict: bg,tc,ic="#1e1600","#f5c842","⚠️"
        elif "Research" in verdict: bg,tc,ic="#141200","#f5c842","⚠️"
        elif "Avoid"   in verdict: bg,tc,ic="#180808","#ff5566","❌"
        else: bg,tc,ic="#111","#8ba8cc",""
        label = verdict.replace("✅ ","").replace("🚨 ","").replace("⚠️ ","").replace("❌ ","")
        return (f"<span style='background:{bg};color:{tc};padding:2px 10px;"
                f"border-radius:10px;font-size:11px;font-weight:600;white-space:nowrap'>"
                f"{ic} {label}</span>")

    def mini_bars(r):
        out = ""
        for lbl, key in [("Q","A%"),("H","B%"),("I","C%"),("F","D%"),("V","E%")]:
            pct = r.get(key) or 0
            c = _sc(pct)
            out += (f"<div style='display:inline-block;text-align:center;margin-right:3px'>"
                    f"<div style='font-size:8px;color:#446;margin-bottom:1px'>{lbl}</div>"
                    f"<div style='position:relative;width:22px;height:32px;"
                    f"background:#0c1628;border-radius:3px;overflow:hidden'>"
                    f"<div style='position:absolute;bottom:0;left:0;right:0;"
                    f"height:{pct:.0f}%;background:{c};opacity:0.8'></div>"
                    f"<span style='position:absolute;top:50%;left:50%;"
                    f"transform:translate(-50%,-50%);font-size:8px;color:#ccc;"
                    f"font-weight:700;z-index:1'>{pct:.0f}</span></div></div>")
        return out

    def beneish(m):
        if m is None: return "<span style='color:#334'>—</span>"
        if m > -1.78: c,l = "#ff5566","HIGH"
        elif m > -2.22: c,l = "#f5c842","GREY"
        else: c,l = "#22d68a","LOW"
        return f"<span style='color:{c};font-size:11px'>{m:.2f} <b>{l}</b></span>"

    # Summary stats
    strong   = sum(1 for r in rows if "Strong"  in r.get("Verdict",""))
    research = sum(1 for r in rows if "Research" in r.get("Verdict",""))
    risk     = sum(1 for r in rows if "Beneish" in r.get("Verdict","") or "Phantom" in r.get("Verdict",""))
    avoid    = sum(1 for r in rows if "Avoid"   in r.get("Verdict",""))
    serious  = sum(1 for r in rows if "Serious" in r.get("Verdict",""))
    avg_sc   = sum(r.get("VI Score",0) or 0 for r in rows) / len(rows) if rows else 0

    def stat(v, lbl, c):
        return (f"<div style='background:#111a2e;border:1px solid #2a4570;border-radius:10px;"
                f"padding:12px 16px;text-align:center;flex:1;min-width:100px;"
                f"box-shadow:0 2px 12px rgba(0,0,0,0.3)'>"
                f"<div style='font-size:24px;font-weight:800;color:{c};line-height:1.1'>{v}</div>"
                f"<div style='font-size:10px;color:#6a88aa;margin-top:5px;font-weight:600;"
                f"text-transform:uppercase;letter-spacing:0.6px'>{lbl}</div></div>")

    summary = (
        f"<div style='display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap;padding:4px 2px'>"
        + stat(f"{avg_sc:.0f}%","Avg Score","#00c8f8")
        + stat(strong,  "Strong Buy",    "#22d68a")
        + stat(research,"Research",      "#f5c842")
        + stat(risk,    "Fraud Risk",    "#ff8c42")
        + stat(avoid,   "Avoid",         "#ff5566")
        + stat(serious, "Serious 🚨",    "#ff2244")
        + "</div>"
    )

    # Table rows
    trs = ""
    for i, r in enumerate(rows):
        score   = r.get("VI Score", 0) or 0
        sc      = _sc(score)
        bg      = "#0e1830" if i % 2 == 0 else "#111e38"
        ticker  = r.get("Ticker","")
        company = (r.get("Company","") or "")[:34]
        TD = "padding:11px 10px;border-bottom:1px solid #1e3358;vertical-align:middle"
        trs += f"""
        <tr style='background:{bg};border-bottom:1px solid #1e3358'>
          <td style='{TD};color:#4a6480;font-size:11px;text-align:center;width:36px'>{i+1}</td>
          <td style='{TD};min-width:130px'>
            <div style='font-size:15px;font-weight:700;color:#e8f2ff;letter-spacing:-0.3px'>{ticker}</div>
            <div style='font-size:10px;color:#5a7898;margin-top:2px;max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap'>{company}</div>
          </td>
          <td style='{TD}'>{badge(r.get("Verdict","—"))}</td>
          <td style='{TD};text-align:center'>
            <div style='display:inline-flex;align-items:center;justify-content:center;
                        width:44px;height:44px;border-radius:50%;border:2.5px solid {sc};
                        font-size:14px;font-weight:800;color:{sc};background:rgba(0,0,0,0.3)'>{score:.0f}</div>
          </td>
          <td style='{TD}'>{mini_bars(r)}</td>
          <td style='{TD};font-family:"JetBrains Mono",monospace;font-size:12px;text-align:right'>{cell(r.get("Rev CAGR%"),"{:.1f}%",lambda v:v>=7,lambda v:v<0)}</td>
          <td style='{TD};font-family:"JetBrains Mono",monospace;font-size:12px;text-align:right'>{cell(r.get("ROE%"),"{:.1f}%",lambda v:v>=15,lambda v:v<8)}</td>
          <td style='{TD};font-family:"JetBrains Mono",monospace;font-size:12px;text-align:right'>{cell(r.get("D/E"),"{:.2f}×",lambda v:v<0.5,lambda v:v>1.5)}</td>
          <td style='{TD};font-family:"JetBrains Mono",monospace;font-size:12px;text-align:right'>{cell(r.get("P/E"),"{:.1f}×",lambda v:0<v<20,lambda v:v>35 or v<=0)}</td>
          <td style='{TD};font-family:"JetBrains Mono",monospace;font-size:12px;text-align:right'>{cell(r.get("Div%"),"{:.1f}%",lambda v:v>=2,lambda v:v<0.5)}</td>
          <td style='{TD}'>{beneish(r.get("M-Score"))}</td>
          <td style='{TD};text-align:center;font-size:15px'>
            {"<span style='color:#22d68a;font-weight:700'>✔</span>" if r.get("FCF+") else "<span style='color:#2a4060'>✘</span>"}
          </td>
        </tr>"""

    th = ("background:#0e1830;color:#8ba8cc;font-size:10px;font-weight:700;"
          "padding:10px 10px;text-transform:uppercase;letter-spacing:0.8px;"
          "text-align:left;border-bottom:2px solid #2a4570;white-space:nowrap;"
          "position:sticky;top:0;z-index:10")
    header = (
        f"<tr>"
        f"<th style='{th};width:36px;text-align:center'>#</th>"
        f"<th style='{th}'>Stock</th>"
        f"<th style='{th}'>Verdict</th>"
        f"<th style='{th};text-align:center'>Score</th>"
        f"<th style='{th}'>Q · H · I · F · V</th>"
        f"<th style='{th};text-align:right'>Rev CAGR</th>"
        f"<th style='{th};text-align:right'>ROE</th>"
        f"<th style='{th};text-align:right'>D/E</th>"
        f"<th style='{th};text-align:right'>P/E</th>"
        f"<th style='{th};text-align:right'>Div%</th>"
        f"<th style='{th}'>Beneish M</th>"
        f"<th style='{th};text-align:center'>FCF+</th>"
        f"</tr>"
    )

    row_h   = 58
    head_h  = 80
    total_h = head_h + len(rows) * row_h + 20
    height  = min(total_h, 820)

    return f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<link rel='preconnect' href='https://fonts.googleapis.com'>
<link href='https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@500;700&display=swap' rel='stylesheet'>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:#0b1120; font-family:'Sora',system-ui,sans-serif;
          color:#dce9ff; padding:0; }}
  .wrap {{ padding:6px 4px 16px; }}
  table {{ width:100%; border-collapse:collapse; min-width:900px; }}
  tbody tr {{ transition: background 0.1s; cursor:pointer; }}
  tbody tr:hover {{ background:#1a2e50 !important; }}
  ::-webkit-scrollbar {{ height:6px; width:6px; background:#111a2e; }}
  ::-webkit-scrollbar-thumb {{ background:#2a4570; border-radius:4px; }}
  ::-webkit-scrollbar-thumb:hover {{ background:#00c8f8; }}
  ::-webkit-scrollbar-corner {{ background:#111a2e; }}
</style>
</head><body>
<div class='wrap'>
  {summary}
  <div style='overflow-x:auto'>
    <table>
      <thead>{header}</thead>
      <tbody>{trs}</tbody>
    </table>
  </div>
</div>
</body></html>""", height

def show_screener_tab():
    st.markdown(
        "<div style='margin-bottom:16px'>"
        "<h3 style='color:#00c8f8;margin:0 0 8px;letter-spacing:-0.3px'>🔍 Screener</h3>"
        "<p style='color:#5a7898;font-size:13px;margin:0;line-height:1.7'>"
        "Batch VI-scorecard · "
        "<span style='color:#22d68a;font-weight:600'>●</span> ≥72% Strong Buy &nbsp;"
        "<span style='color:#f5c842;font-weight:600'>●</span> ≥55% Research &nbsp;"
        "<span style='color:#ff5566;font-weight:600'>●</span> Below &nbsp;·&nbsp; "
        "Q=Quality H=Health I=Integrity F=Fraud V=Valuation</p></div>",
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
    with c1: universe = st.selectbox("Universe", ["SET100","MAI","SET100 + MAI"], key="scr_uni")
    with c2:
        sector_f = st.selectbox("Sector", ["All Sectors"]+sorted(SECTOR_MAP.keys()), key="scr_sec")
    with c3: min_score = st.number_input("Min Score%", 0, 100, 0, 5, key="scr_min")
    with c4: sort_by  = st.selectbox("Sort by", ["VI Score","ROE%","Rev CAGR%","Div%","P/E"], key="scr_sort")

    run = st.button("▶  Run Screener", type="primary", use_container_width=True)

    if not run and "screener_results" not in st.session_state:
        st.markdown(
            "<div style='background:#111a2e;border:2px dashed #2a4570;border-radius:12px;"
            "padding:48px;text-align:center;margin-top:20px'>"
            "<div style='font-size:44px'>🔍</div>"
            "<div style='color:#00c8f8;font-size:18px;margin:14px 0 8px;font-weight:700'>Ready to screen</div>"
            "<div style='color:#5a7898;font-size:13px;line-height:1.7'>"
            "Pick a universe, then click <b style='color:#dce9ff'>▶ Run Screener</b></div>"
            "<div style='color:#3a5878;font-size:11px;margin-top:12px;padding:8px 16px;"
            "background:#0e1830;border-radius:6px;display:inline-block'>"
            "⏱ SET100 ≈ 3–5 min first run · results cached 6 hours</div></div>",
            unsafe_allow_html=True
        )
        return

    if run:
        if universe == "SET100":    pool = SET100
        elif universe == "MAI":      pool = MAI_TICKERS
        else:                        pool = SET100 + MAI_TICKERS
        if sector_f != "All Sectors":
            pool = [t for t in pool if t in set(SECTOR_MAP.get(sector_f, []))]
        if not pool: st.warning("No tickers match this filter."); return

        bar = st.progress(0)
        results = []
        errors  = []
        for i, t in enumerate(pool):
            bar.progress((i+1)/len(pool), text=f"Analysing **{t}** · {i+1}/{len(pool)}")
            r = compute_quick_score(to_yf(t))
            results.append(r)
            if r.get("Verdict") == "Error":
                errors.append(t)
        bar.empty()
        ok = len(results) - len(errors)
        st.success(f"✅ Done — {ok}/{len(results)} stocks analysed" +
                   (f"  ·  ⚠️ {len(errors)} failed ({', '.join(errors[:5])}{'…' if len(errors)>5 else ''})" if errors else ""))
        st.session_state["screener_results"] = results
        st.session_state["screener_meta"] = f"{universe} · {sector_f}"

    if "screener_results" not in st.session_state: return
    all_r = st.session_state["screener_results"]

    # ── Filter ──────────────────────────────────────────────────────────
    filtered = [r for r in all_r if (r.get("VI Score") or 0) >= min_score]
    asc = (sort_by == "P/E")
    filtered.sort(key=lambda r: (r.get(sort_by) or 0), reverse=not asc)

    meta = st.session_state.get("screener_meta","")
    st.markdown(
        f"<div style='background:#111a2e;border:1px solid #1e3358;border-radius:8px;"
        f"padding:8px 14px;margin:8px 0;font-size:12px;color:#8ba8cc'>"
        f"<b style='color:#dce9ff'>{len(filtered)}</b> stocks · {meta} · "
        f"min <b style='color:#dce9ff'>{min_score}%</b> · "
        f"sorted by <b style='color:#00c8f8'>{sort_by}</b></div>",
        unsafe_allow_html=True
    )

    # ── Quick filters row ────────────────────────────────────────────────
    fa, fb, fc, fd, fe = st.columns(5)
    active = st.session_state.get("scr_filter","all")
    with fa:
        if st.button("✅ Strong Buy", use_container_width=True, key="f_sb"):
            st.session_state["scr_filter"] = "sb" if active!="sb" else "all"
    with fb:
        if st.button("🚨 Red Flags",  use_container_width=True, key="f_rf"):
            st.session_state["scr_filter"] = "rf" if active!="rf" else "all"
    with fc:
        if st.button("✔ FCF+ only",  use_container_width=True, key="f_fcf"):
            st.session_state["scr_filter"] = "fcf" if active!="fcf" else "all"
    with fd:
        if st.button("💰 Div ≥ 2%",  use_container_width=True, key="f_div"):
            st.session_state["scr_filter"] = "div" if active!="div" else "all"
    with fe:
        if st.button("📈 ROE ≥ 15%", use_container_width=True, key="f_roe"):
            st.session_state["scr_filter"] = "roe" if active!="roe" else "all"

    flt = st.session_state.get("scr_filter","all")
    if flt == "sb":  filtered = [r for r in filtered if "Strong"  in r.get("Verdict","")]
    elif flt == "rf": filtered = [r for r in filtered if "🚨"     in r.get("Verdict","")]
    elif flt == "fcf":filtered = [r for r in filtered if r.get("FCF+")]
    elif flt == "div":filtered = [r for r in filtered if (r.get("Div%") or 0)>=2]
    elif flt == "roe":filtered = [r for r in filtered if (r.get("ROE%") or 0)>=15]

    # ── Table (components.html — no sanitizer) ───────────────────────────
    if filtered:
        html_page, h = _build_screener_page(filtered)
        _components.html(html_page, height=h, scrolling=True)
    else:
        st.info("No stocks match this filter.")

    # ── Drill-down ───────────────────────────────────────────────────────
    st.markdown(
        "<div style='margin:20px 0 10px;border-top:1px solid #1e3358;padding-top:16px'>"
        "<div style='color:#8ba8cc;font-size:11px;font-weight:700;"
        "text-transform:uppercase;letter-spacing:1px'>🔎 Deep Dive</div></div>",
        unsafe_allow_html=True
    )
    tickers_shown = ["— pick a stock —"] + [r["Ticker"] for r in filtered]
    drill = st.selectbox("", tickers_shown, key="scr_drill", label_visibility="collapsed")

    if drill and drill != "— pick a stock —":
        name = TICKER_NAMES.get(drill, "")
        st.markdown(
            f"<div style='background:linear-gradient(135deg,#0e2248,#0a1830);"
            f"border:1px solid #2a4570;border-radius:10px;"
            f"padding:14px 20px;margin-bottom:16px;display:flex;align-items:center;gap:14px'>"
            f"<span style='font-size:22px;font-weight:800;color:#00c8f8'>{drill}</span>"
            f"<div style='width:1px;height:24px;background:#2a4570'></div>"
            f"<span style='color:#8ba8cc;font-size:13px'>{name}</span></div>",
            unsafe_allow_html=True
        )
        dt = st.tabs(["📈 Price","📋 Financials","📊 Fundamentals","⚖️ VI Scorecard","📰 News"])
        with dt[0]:
            with st.spinner("Loading…"): fig=make_price_chart(to_yf(drill),"2020-01-01"); st.pyplot(fig); plt.close(fig)
        with dt[1]:
            d=fetch_all(to_yf(drill))
            for title,df in [("Income Statement",d['income']),("Balance Sheet",d['balance']),("Cash Flow",d['cashflow'])]:
                st.markdown(_df_to_html(df,title), unsafe_allow_html=True)
        with dt[2]:
            with st.spinner("Plotting…"): fig=make_fundamental_chart(to_yf(drill)); st.pyplot(fig); plt.close(fig)
        with dt[3]:
            with st.spinner("Scoring…"): render_vi_scorecard_st(compute_vi_scorecard(to_yf(drill)))
        with dt[4]:
            with st.spinner("Fetching news…"): render_news_st(to_yf(drill), fetch_all_news(to_yf(drill)))

# ─── Main app ───────────────────────────────────────────────────────────────────
def main():
    # ── Sidebar ──────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            "<div style='background:#0e1a38;border:1px solid #2a4570;"
            "border-radius:10px;padding:14px 16px;margin-bottom:12px'>"
            "<div style='color:#00c8f8;font-size:20px;font-weight:800'>🏦 SET Analyser</div>"
            "<div style='color:#5a7898;font-size:11px;margin-top:4px'>Value Investor Edition · H1 2025</div>"
            "</div>",
            unsafe_allow_html=True
        )

        # ── Date range ───────────────────────────────────────────────────────────
        st.markdown("<div class='sidebar-label'><span style='color:#00c8f8'>📅</span> Chart Start Date</div>", unsafe_allow_html=True)
        c1, c2 = st.columns([3, 2])
        with c1: start_year  = st.selectbox("Year",  [str(y) for y in range(2015,2026)], index=6, key="sy", label_visibility="collapsed")
        with c2: start_month = st.selectbox("Month", [f"{m:02d}" for m in range(1,13)], index=0, key="sm", label_visibility="collapsed")
        start = f"{start_year}-{start_month}-01"

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── SET100 multiselect ───────────────────────────────────────────────────
        st.markdown(
            "<div class='sidebar-label'><span style='color:#00c8f8;font-size:14px'>●</span> SET100</div>",
            unsafe_allow_html=True
        )
        # Sector shortcut
        sector_pick = st.selectbox("Quick sector", ["All"]+sorted(SECTOR_MAP.keys()),
                                   key="sb_sec", label_visibility="collapsed")
        if sector_pick != "All":
            default_set = [t for t in SET100 if t in set(SECTOR_MAP.get(sector_pick,[]))]
        else:
            default_set = []
        set_sel = st.multiselect(
            "SET100 tickers", SET100,
            default=default_set,
            placeholder="Type or scroll to pick…",
            key="set_ms", label_visibility="collapsed"
        )

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── MAI multiselect ──────────────────────────────────────────────────────
        st.markdown(
            "<div class='sidebar-label'><span style='color:#22d68a;font-size:14px'>●</span> MAI</div>",
            unsafe_allow_html=True
        )
        mai_sel = st.multiselect(
            "MAI tickers", MAI_TICKERS,
            placeholder="Type or scroll to pick…",
            key="mai_ms", label_visibility="collapsed"
        )

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── DR multiselect ───────────────────────────────────────────────────────
        st.markdown(
            "<div class='sidebar-label'><span style='color:#f5c842;font-size:14px'>●</span> DR / ETF</div>",
            unsafe_allow_html=True
        )
        dr_sel = st.multiselect(
            "DR tickers", DR_TICKERS,
            placeholder="Pick DR / ETF…",
            key="dr_ms", label_visibility="collapsed"
        )

        selected_base = set_sel + mai_sel + dr_sel
        selected      = [to_yf(t) for t in selected_base]

        # ── Selection summary pill ───────────────────────────────────────────────
        if selected_base:
            names_preview = ", ".join(selected_base[:6]) + ("…" if len(selected_base) > 6 else "")
            st.markdown(
                f"<div style='background:rgba(0,200,248,0.08);border:1px solid rgba(0,200,248,0.3);"
                f"border-radius:8px;padding:10px 14px;margin-top:8px'>"
                f"<div style='color:#22d68a;font-weight:700;font-size:15px'>{len(selected_base)} selected</div>"
                f"<div style='color:#8ba8cc;font-size:11px;margin-top:3px'>{names_preview}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

        st.markdown("<hr>", unsafe_allow_html=True)
        _ds_ok, _ds_msg = _check_yfinance()
        if _ds_ok:
            st.markdown("<div style='background:rgba(34,214,138,0.1);border:1px solid #22d68a;"
                        "border-radius:6px;padding:6px 10px;font-size:11px;color:#22d68a;"
                        "margin-bottom:8px'>🟢 Data feed OK</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div style='background:rgba(255,85,102,0.1);border:1px solid #ff5566;"
                f"border-radius:6px;padding:6px 10px;font-size:11px;color:#ff5566;"
                f"margin-bottom:8px'>🔴 Data issue: {_ds_msg[:60]}</div>",
                unsafe_allow_html=True)
        if st.button("🗑 Clear cache", use_container_width=True, help="Force-refresh all data"):
            st.cache_data.clear(); st.rerun()

    # ── Main tabs ────────────────────────────────────────────────────────────────
    TABS = ["🔍 Screener", "📈 Price", "📋 Financials", "📊 Fundamentals", "⚖️ VI Score", "📰 News"]
    tabs = st.tabs(TABS)

    def _need_selection():
        st.markdown(
            "<div style='background:#111a2e;border:2px dashed #2a4570;border-radius:12px;"
            "padding:48px;text-align:center;margin-top:24px'>"
            "<div style='font-size:44px'>🏦</div>"
            "<div style='color:#00c8f8;font-size:18px;margin:14px 0 8px;font-weight:700'>"
            "Select stocks in the sidebar</div>"
            "<div style='color:#5a7898;font-size:13px;line-height:1.7'>"
            "Use the <b style='color:#8ba8cc'>SET100</b>, "
            "<b style='color:#8ba8cc'>MAI</b>, or "
            "<b style='color:#8ba8cc'>DR/ETF</b> selectors on the left.</div>"
            "</div>",
            unsafe_allow_html=True
        )

    with tabs[0]: show_screener_tab()

    with tabs[1]:
        if not selected: _need_selection()
        else:
            for ticker in selected:
                with st.spinner(f"Loading {ticker}…"):
                    fig = make_price_chart(ticker, start)
                    st.pyplot(fig); plt.close(fig)

    with tabs[2]:
        if not selected: _need_selection()
        else:
            for ticker in selected:
                base = ticker.replace('.BK','')
                name = TICKER_NAMES.get(base, "")
                st.markdown(
                    f"<div style='background:#0e1830;border:1px solid #1e3358;border-radius:8px;"
                    f"padding:10px 16px;margin:12px 0 8px;display:flex;align-items:center;gap:12px'>"
                    f"<span style='color:#00c8f8;font-size:18px;font-weight:800'>{base}</span>"
                    f"<div style='width:1px;height:20px;background:#1e3358'></div>"
                    f"<span style='color:#8ba8cc;font-size:13px'>{name}</span></div>",
                    unsafe_allow_html=True
                )
                d = fetch_all(ticker)
                for title, df in [("Income Statement", d['income']),
                                   ("Balance Sheet",    d['balance']),
                                   ("Cash Flow",        d['cashflow'])]:
                    st.markdown(_df_to_html(df, title), unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)

    with tabs[3]:
        if not selected: _need_selection()
        else:
            for ticker in selected:
                with st.spinner(f"Plotting {ticker}…"):
                    fig = make_fundamental_chart(ticker)
                    st.pyplot(fig); plt.close(fig)

    with tabs[4]:
        if not selected: _need_selection()
        else:
            for ticker in selected:
                with st.spinner(f"Scoring {ticker}…"):
                    render_vi_scorecard_st(compute_vi_scorecard(ticker))
                st.markdown("<hr>", unsafe_allow_html=True)

    with tabs[5]:
        if not selected: _need_selection()
        else:
            for ticker in selected:
                with st.spinner(f"Scanning news for {ticker}…"):
                    render_news_st(ticker, fetch_all_news(ticker))
                st.markdown("<hr>", unsafe_allow_html=True)

if __name__ == "__main__" or True:
    try:
        main()
    except Exception as _e:
        import traceback
        st.error(f"❌ App error: {_e}")
        st.code(traceback.format_exc())
