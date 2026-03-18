"""
SET Stock Analyser — Value Investor Edition  (Streamlit)
Run:  streamlit run app.py
"""
import warnings; warnings.filterwarnings('ignore')
import streamlit as st
import streamlit.components.v1 as _components
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
try:
    import plotly.graph_objects as go
    import plotly.subplots as _psp
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
import yfinance as yf
import pandas as pd
import numpy as np
import urllib.request as _ureq, urllib.parse as _uparse
import xml.etree.ElementTree as _ET
import html as _html_lib
import re as _re
from datetime import datetime as _dt, timezone as _tz, timedelta as _td

st.set_page_config(page_title="SET Analyser · VI", page_icon="🏦", layout="wide",
                   initial_sidebar_state="expanded")
st.markdown("""
<style>
:root{
  --bg:#0b1120; --bg2:#111a2e; --bg3:#172038;
  --border:#1e3358; --border2:#2a4570;
  --txt:#dce9ff; --txt2:#8ba8cc; --txt3:#4a6480;
  --accent:#00c8f8; --green:#22d68a; --yellow:#f5c842;
  --red:#ff5566; --radius:8px;
}
html,body,.stApp{background:var(--bg)!important;color:var(--txt)!important;font-family:system-ui,sans-serif!important;}
.block-container{padding:1.2rem 2rem 2rem!important;max-width:1440px!important;}
#MainMenu,footer,[data-testid="stStatusWidget"]{visibility:hidden!important;}
[data-testid="stDecoration"]{display:none!important;}
*{scrollbar-width:thin;scrollbar-color:var(--border2) var(--bg2);}
::-webkit-scrollbar{width:7px;height:7px;background:var(--bg2);}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:4px;}
::-webkit-scrollbar-thumb:hover{background:var(--accent);}
section[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border)!important;}
section[data-testid="stSidebar"] label,section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span{color:var(--txt2)!important;}
header[data-testid="stHeader"]{background:transparent!important;border-bottom:none!important;}
[data-testid="stSidebarCollapsedControl"]{
  position:fixed!important;left:0!important;top:50%!important;
  transform:translateY(-50%)!important;z-index:99999!important;
  display:flex!important;visibility:visible!important;opacity:1!important;
  background:var(--bg2)!important;border:1px solid var(--border2)!important;
  border-left:none!important;border-radius:0 var(--radius) var(--radius) 0!important;
  padding:10px 6px!important;box-shadow:3px 0 12px rgba(0,0,0,0.5)!important;cursor:pointer!important;}
[data-testid="stSidebarCollapsedControl"]:hover{background:var(--bg3)!important;border-color:var(--accent)!important;}
[data-testid="stSidebarCollapsedControl"] svg,[data-testid="stSidebarCollapsedControl"] button svg{fill:var(--accent)!important;stroke:var(--accent)!important;}
[data-testid="collapsedControl"]{
  position:fixed!important;left:0!important;top:50%!important;
  transform:translateY(-50%)!important;z-index:99999!important;
  display:flex!important;visibility:visible!important;opacity:1!important;
  background:var(--bg2)!important;border:1px solid var(--border2)!important;
  border-left:none!important;border-radius:0 var(--radius) var(--radius) 0!important;
  padding:10px 6px!important;box-shadow:3px 0 12px rgba(0,0,0,0.5)!important;cursor:pointer!important;}
[data-testid="collapsedControl"]:hover{background:var(--bg3)!important;border-color:var(--accent)!important;}
[data-testid="collapsedControl"] svg{fill:var(--accent)!important;}
h1,h2,h3{color:var(--accent)!important;font-weight:800!important;}
hr{border:none!important;border-top:1px solid var(--border)!important;margin:14px 0!important;}
.stTabs [data-baseweb="tab-list"]{gap:4px!important;border-bottom:2px solid var(--border)!important;background:transparent!important;}
.stTabs [data-baseweb="tab"]{color:var(--txt2)!important;font-size:13px!important;font-weight:600!important;padding:10px 18px!important;background:transparent!important;}
.stTabs [data-baseweb="tab"] p,.stTabs [data-baseweb="tab"] span,.stTabs [data-baseweb="tab"] div{color:var(--txt2)!important;font-size:13px!important;font-weight:600!important;}
.stTabs [data-baseweb="tab"]:hover,.stTabs [data-baseweb="tab"]:hover p,.stTabs [data-baseweb="tab"]:hover span{color:var(--txt)!important;background:var(--bg3)!important;}
.stTabs [aria-selected="true"],.stTabs [aria-selected="true"] p,.stTabs [aria-selected="true"] span,.stTabs [aria-selected="true"] div{color:var(--accent)!important;background:var(--bg3)!important;border-bottom:2px solid var(--accent)!important;margin-bottom:-2px!important;}
.stButton>button{background:var(--bg3)!important;color:var(--txt)!important;border:1px solid var(--border2)!important;border-radius:var(--radius)!important;font-size:13px!important;font-weight:600!important;}
.stButton>button:hover{border-color:var(--accent)!important;color:var(--accent)!important;}
.stButton>button[kind="primary"],.stButton>button[data-testid="baseButton-primary"]{background:#0e2850!important;border-color:var(--accent)!important;color:var(--accent)!important;font-weight:700!important;}
.stSelectbox>div>div,.stMultiSelect>div>div,.stTextInput>div>div,.stNumberInput>div>div{background:var(--bg2)!important;border:1px solid var(--border2)!important;color:var(--txt)!important;border-radius:var(--radius)!important;}
span[data-baseweb="tag"]{background:rgba(0,200,248,0.15)!important;border:1px solid rgba(0,200,248,0.35)!important;color:var(--accent)!important;border-radius:4px!important;}
[data-baseweb="popover"] ul{background:var(--bg2)!important;border:1px solid var(--border2)!important;}
[data-baseweb="popover"] li{color:var(--txt)!important;}
[data-baseweb="popover"] li:hover{background:var(--bg3)!important;}
.stProgress>div>div>div{background:linear-gradient(90deg,var(--accent),var(--green))!important;}
div[data-testid="metric-container"]{background:var(--bg2)!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important;}
.sidebar-label{color:var(--txt2)!important;font-size:11px!important;font-weight:700!important;text-transform:uppercase!important;letter-spacing:1px!important;margin-bottom:6px!important;}
/* Sector icon buttons — force single line */
section[data-testid="stSidebar"] div[data-testid="stButton"] button{
  padding:4px 2px!important;border-radius:6px!important;
  min-height:32px!important;height:32px!important;}
section[data-testid="stSidebar"] div[data-testid="stButton"] button p,
section[data-testid="stSidebar"] div[data-testid="stButton"] button div{
  white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;
  font-size:11px!important;line-height:1!important;font-weight:600!important;
  margin:0!important;padding:0!important;}
/* Plotly chart background */
.js-plotly-plot .plotly .bg{fill:#0b1120!important;}
.modebar{background:rgba(11,17,32,0.8)!important;}
.modebar-btn svg{fill:#8ba8cc!important;}
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
    "Property":     ["LH","CPN","SIRI","SPALI","WHA","AWC","AP","QH","AMATA","ROJNA","A5","CHEWA","MORE","SCGD"],
    "Healthcare":   ["BDMS","BH","CHG","BCH","PR9","SPA","VIH"],
    "Commerce":     ["CPALL","BJC","OSP","CBG","HMPRO","COM7","CRC","DOHOME","GLOBAL","MEGA","MOSHI","KAMART","MBK","MASTER"],
    "Food":         ["CPF","TU","STA","BTG","ITC","ICHI","SAPPE","SNNP","COCOCO","PM","RBF"],
    "Industrial":   ["SCC","SCGP","IVL","DELTA","HANA","KCE","TASCO","SMPC"],
    "Transport":    ["AOT","BTS","BEM","AAV","BA","RCL","PRM","SJWD"],
    "Media/Leisure":["PLANB","VGI","MINT","CENTEL","ERW","M","JMART","RS","BEC","MONO"],
}

# Sector icon buttons for sidebar (emoji + label)
SECTOR_ICONS = {
    "All":          ("🌐","All"),
    "Banking":      ("🏦","Bank"),
    "Finance":      ("💳","Fin"),
    "Energy":       ("⛽","Energy"),
    "Tech/Telecom": ("📡","Tech"),
    "Property":     ("🏗","Prop"),
    "Healthcare":   ("💊","Health"),
    "Commerce":     ("🛒","Shop"),
    "Food":         ("🍗","Food"),
    "Industrial":   ("🔧","Indus"),
    "Transport":    ("✈️","Trans"),
    "Media/Leisure":("🎬","Media"),
}

# MAI sector mapping
MAI_SECTOR_MAP = {
    "Tech":     ["ADVICE","DITTO","FORTH","MFEC","NETBAY","NEO","PLANET","SKR"],
    "Finance":  ["ASK","GCAP","SGC","THRE"],
    "Property": ["A5","CHEWA","MORE","SCGD"],
    "Energy":   ["BBGI","EPG","SSP","TPCH"],
    "Healthcare":["SPA","VIH"],
    "Commerce": ["KAMART","MASTER","MBK"],
    "Food":     ["PM","RBF"],
    "Media":    ["BEC","MONO","RS"],
    "Other":    ["SMPC"],
}

def to_yf(sym): return sym + ".BK"

# ─── Sector-aware scoring profiles ─────────────────────────────────────────────
# Each sector has different structural characteristics that require adjusted thresholds.
# Applying industrial metrics to banks or property companies gives wrong conclusions.

SECTOR_PROFILES = {
    # ── Banks ─────────────────────────────────────────────────────────────────
    # High D/E is STRUCTURAL (deposits = liabilities; loans = assets).
    # A bank with D/E < 1 would be dangerously under-leveraged.
    # Key risks: NPL ratio, capital adequacy (CAR), net interest margin (NIM),
    # loan growth, and cost-to-income ratio — most not available via yfinance.
    'bank': {
        'label': '🏦 Bank', 'color': '#4fc3f7',
        'note': ('Banking model: deposits are liabilities → D/E 8–15× is NORMAL & regulated. '
                 'Thresholds adjusted. Key risks not in yfinance: NPL ratio, CAR, NIM — '
                 'always cross-check BOT regulatory filings.'),
        'rev_cagr_min': 5,
        'gross_margin_min': None,   # Replace with net interest income / revenue
        'net_margin_min': 15,       # Banks earn fat margins on revenue
        'roe_min': 12,              # Capital-intensive; 10%+ is good for Thai banks
        'de_max': None,             # SKIP — structural, not a risk signal
        'cr_min': None,             # SKIP — deposit-funded; ALM manages liquidity
        'ic_min': 2,                # Banks earn interest; coverage concept differs
        'div_yield_min': 3.0,       # Thai banks historically pay 3–6%
        'fcf_mode': 'ocf_positive', # OCF = core cash; capex minimal for banks
        'phantom_mode': 'ni_trend', # Loan book expansion causes OCF swing; NI trend better signal
    },
    # ── Consumer Finance / Leasing / Microfinance ─────────────────────────────
    # Leverage is the PRODUCT: they borrow cheap, lend expensive.
    # D/E 3–8× is perfectly healthy. Key risks: NPL, collection rate, cost of funds.
    'finance': {
        'label': '💳 Finance/Leasing', 'color': '#ce93d8',
        'note': ('Finance model: borrowing to lend IS the business. D/E 3–8× is normal. '
                 'Key risks not in yfinance: NPL%, collection rate, cost-of-funds spread. '
                 'Check company quarterly filings for portfolio quality.'),
        'rev_cagr_min': 7,
        'gross_margin_min': None,   # Interest spread, not a traditional gross margin
        'net_margin_min': 15,       # Good finance cos run 15–30% net margin
        'roe_min': 15,
        'de_max': 6.0,
        'cr_min': None,             # Funded by bonds/banks, not payables
        'ic_min': 2,
        'div_yield_min': 3.0,
        'fcf_mode': 'ocf_positive',
        'phantom_mode': 'ni_trend',
    },
    # ── Property Developers ───────────────────────────────────────────────────
    # Project-based: revenue and FCF are lumpy by design (3–5 year build cycles).
    # Moderate leverage (1–2×) is normal. Backlog/presales are key, but not in yfinance.
    'property': {
        'label': '🏗 Property/REIT', 'color': '#ffb74d',
        'note': ('Property model: revenue is project-lumpy (3–5yr cycles). '
                 'D/E 1–1.5× is standard. FCF evaluated as 3Y average. '
                 'Key metrics not in yfinance: presales backlog, sell-through rate.'),
        'rev_cagr_min': 5,
        'gross_margin_min': 25,     # Thai residential developers: 25–40%
        'net_margin_min': 8,
        'roe_min': 15,
        'de_max': 1.5,
        'cr_min': 1.2,              # Funded partly by homebuyer deposits
        'ic_min': 3,
        'div_yield_min': 5.0,
        'fcf_mode': 'avg_3y',       # 3Y average; single years can be heavily negative
        'phantom_mode': 'standard',
    },
    # ── Energy / Infrastructure / Utilities ───────────────────────────────────
    # Long-lived assets financed with project debt (20–30yr bonds normal).
    # D/E 2–3× is healthy for power plants. FCF dips sharply during construction.
    # Dividend yield is the primary investor return driver.
    'energy': {
        'label': '⚡ Energy/Infra', 'color': '#aed581',
        'note': ('Energy/infra model: project-finance debt (2–2.5× D/E) is normal for '
                 'power plants and pipelines. FCF is evaluated as 3Y average (construction '
                 'phases create negative FCF). Dividend yield is the primary return driver.'),
        'rev_cagr_min': 5,
        'gross_margin_min': 20,     # Commodity/refining margins can be thin
        'net_margin_min': 5,
        'roe_min': 10,
        'de_max': 2.5,
        'cr_min': 1.0,
        'ic_min': 3,
        'div_yield_min': 4.0,       # Energy/utility co.s should distribute cash
        'fcf_mode': 'avg_3y',
        'phantom_mode': 'standard',
    },
    # ── General (Industrial / Tech / Healthcare / Food / Consumer) ────────────
    'general': {
        'label': '🏭 Industrial/General', 'color': '#80cbc4',
        'note': 'Standard Buffett/Graham thresholds for non-financial, non-utility businesses.',
        'rev_cagr_min': 7,
        'gross_margin_min': 40,
        'net_margin_min': 10,
        'roe_min': 15,
        'de_max': 0.5,
        'cr_min': 1.5,
        'ic_min': 5,
        'div_yield_min': 2.5,
        'fcf_mode': 'all_positive',
        'phantom_mode': 'standard',
    },
}

# Map each ticker to its sector group
_TICKER_TO_GROUP = {}
for _g, _tickers in [
    ('bank',     ['BBL','KBANK','KTB','SCB','BAY','KKP','TISCO','TTB','TCAP']),
    ('finance',  ['KTC','MTC','TIDLOR','SAWAD','AEONTS','BAM','JMT','ASK','THRE','BLA']),
    ('property', ['LH','CPN','SIRI','SPALI','WHA','AWC','AP','QH','AMATA','ROJNA',
                  'A5','CHEWA','MORE','SCGD']),
    ('energy',   ['PTT','PTTEP','PTTGC','TOP','BANPU','BCP','BCPG','BGRIM','EA',
                  'EGCO','GULF','GPSC','GUNKUL','CKP','RATCH','IRPC','SPRC','OR',
                  'BBGI','EPG','SSP','TPCH']),
]:
    for _t in _tickers:
        _TICKER_TO_GROUP[_t] = _g

def get_sector_profile(base_ticker):
    """Return (group_key, profile_dict) for a ticker."""
    g = _TICKER_TO_GROUP.get(base_ticker, 'general')
    return g, SECTOR_PROFILES[g]

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
    ag = g.ewm(com=n-1, min_periods=n).mean(); al = l.ewm(com=n-1, min_periods=n).mean()
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
    ax.set_facecolor('#0d0d0d'); ax.tick_params(colors='#aaaaaa', labelsize=8)
    ax.grid(axis='y', color='#2a2a2a', linewidth=0.5, linestyle='--')
    ax.grid(axis='x', color='#1a1a1a', linewidth=0.3)
    for sp in ax.spines.values(): sp.set_edgecolor('#2a2a2a')

# ─── Data fetch (cached 6h) ─────────────────────────────────────────────────────
@st.cache_data(ttl=21600, show_spinner=False)
def fetch_all(ticker):
    import time
    data = dict(ticker=ticker, info={}, price=pd.DataFrame(), income=pd.DataFrame(),
                balance=pd.DataFrame(), cashflow=pd.DataFrame(), divs=pd.Series(dtype=float))
    for attempt in range(3):
        try:
            tk = yf.Ticker(ticker); end = pd.Timestamp.now()
            try:
                info = tk.info or {}; data['info'] = info if isinstance(info, dict) else {}
            except Exception: pass
            try:
                px = tk.history(interval='1d', start=end - pd.DateOffset(years=10), end=end, timeout=30)
                if px is not None and not px.empty: data['price'] = px
            except Exception: pass
            try:
                inc = tk.income_stmt
                if inc is not None and not (hasattr(inc,'empty') and inc.empty): data['income'] = inc
            except Exception: pass
            try:
                bal = tk.balance_sheet
                if bal is not None and not (hasattr(bal,'empty') and bal.empty): data['balance'] = bal
            except Exception: pass
            try:
                cf = tk.cashflow
                if cf is not None and not (hasattr(cf,'empty') and cf.empty): data['cashflow'] = cf
            except Exception: pass
            try:
                dv = tk.dividends
                if dv is not None and len(dv) > 0: data['divs'] = dv
            except Exception: pass
            break
        except Exception:
            if attempt < 2: time.sleep(2 ** attempt)
    return data


# ─── 1. Price chart ──────────────────────────────────────────────────────────────
EMA_W=[25,75,200]; EMA_C=['deeppink','limegreen','grey']; EMA_L=['EMA 25','EMA 75','EMA 200']

def make_tv_chart(ticker):
    """
    TradingView Lightweight Charts — full interactive chart.
    Daily / Weekly / Monthly intervals.
    Panes: Price+EMAs | RSI | Volume | P/BV
    Period buttons, crosshair sync, zoom/pan, log scale.
    """
    import json

    d = fetch_all(ticker)
    raw = d['price'].copy()
    if raw.empty:
        return f"<div style='color:#ef5350;padding:24px'>No price data for {ticker}</div>", 200

    raw.index = strip_tz(raw.index)
    raw = raw.sort_index()

    # ── Compute EMAs and RSI on full daily history ──────────────────────────────
    close_d = raw['Close']
    ema25_d  = close_d.ewm(span=25,  adjust=False).mean()
    ema75_d  = close_d.ewm(span=75,  adjust=False).mean()
    ema200_d = close_d.ewm(span=200, adjust=False).mean()
    rsi_d    = calc_rsi(close_d)

    # ── Resample to Weekly and Monthly ─────────────────────────────────────────
    def resample_ohlcv(df, rule):
        r = df.resample(rule).agg(
            Open=('Open','first'), High=('High','max'),
            Low=('Low','min'),   Close=('Close','last'), Volume=('Volume','sum')
        ).dropna()
        # recompute EMA/RSI on resampled close
        c = r['Close']
        r['ema25']  = c.ewm(span=25,  adjust=False).mean()
        r['ema75']  = c.ewm(span=75,  adjust=False).mean()
        r['ema200'] = c.ewm(span=200, adjust=False).mean()
        r['rsi']    = calc_rsi(c)
        return r

    raw_with_ema = raw.copy()
    raw_with_ema['ema25']  = ema25_d
    raw_with_ema['ema75']  = ema75_d
    raw_with_ema['ema200'] = ema200_d
    raw_with_ema['rsi']    = rsi_d
    week_df  = resample_ohlcv(raw, 'W-FRI')
    month_df = resample_ohlcv(raw, 'ME')

    # ── P/BV historical series ─────────────────────────────────────────────────
    pbv_series = pd.Series(dtype=float)
    try:
        bal   = d['balance']
        info  = d['info']
        equity = safe_row(bal, 'Stockholders Equity', 'Total Equity Gross Minority Interest')
        shares = info.get('sharesOutstanding') or info.get('impliedSharesOutstanding')
        if not equity.empty and shares and shares > 0:
            # equity index is annual; interpolate to daily
            equity_daily = equity.reindex(
                equity.index.union(close_d.index)
            ).sort_index().interpolate(method='time').reindex(close_d.index)
            bvps = equity_daily / float(shares)
            pbv_series = (close_d / bvps).replace([np.inf, -np.inf], np.nan).dropna()
    except Exception:
        pass

    # ── Serialisers ────────────────────────────────────────────────────────────
    def candles(df):
        return [{"time": int(t.timestamp()),
                 "open":  round(float(r['Open']),  3),
                 "high":  round(float(r['High']),  3),
                 "low":   round(float(r['Low']),   3),
                 "close": round(float(r['Close']), 3)}
                for t, r in df.iterrows()
                if not any(pd.isna(r[c]) for c in ['Open','High','Low','Close'])]

    def series(s):
        return [{"time": int(t.timestamp()), "value": round(float(v), 4)}
                for t, v in s.items() if not pd.isna(v)]

    def vols(df):
        return [{"time": int(t.timestamp()),
                 "value": float(r['Volume']),
                 "color": "#22d68a55" if r['Close'] >= r['Open'] else "#ff556655"}
                for t, r in df.iterrows() if not pd.isna(r['Volume'])]

    # daily
    d_candle = json.dumps(candles(raw))
    d_line   = json.dumps(series(close_d))
    d_e25    = json.dumps(series(ema25_d))
    d_e75    = json.dumps(series(ema75_d))
    d_e200   = json.dumps(series(ema200_d))
    d_rsi    = json.dumps(series(rsi_d))
    d_vol    = json.dumps(vols(raw))
    # weekly
    w_candle = json.dumps(candles(week_df))
    w_line   = json.dumps(series(week_df['Close']))
    w_e25    = json.dumps(series(week_df['ema25']))
    w_e75    = json.dumps(series(week_df['ema75']))
    w_e200   = json.dumps(series(week_df['ema200']))
    w_rsi    = json.dumps(series(week_df['rsi']))
    w_vol    = json.dumps(vols(week_df))
    # monthly
    m_candle = json.dumps(candles(month_df))
    m_line   = json.dumps(series(month_df['Close']))
    m_e25    = json.dumps(series(month_df['ema25']))
    m_e75    = json.dumps(series(month_df['ema75']))
    m_e200   = json.dumps(series(month_df['ema200']))
    m_rsi    = json.dumps(series(month_df['rsi']))
    m_vol    = json.dumps(vols(month_df))
    # P/BV
    pbv_data = json.dumps(series(pbv_series))

    # ── Header stats (full history) ────────────────────────────────────────────
    ep   = float(close_d.iloc[-1])
    fmax = (ep - float(close_d.max())) / float(close_d.max()) * 100
    fmin = (ep - float(close_d.min())) / float(close_d.min()) * 100
    dy   = trailing_div_yield(d['divs'], d['price'])
    dy_txt = f" · Div {dy:.2f}%" if dy else ""
    base  = ticker.replace('.BK', '')
    has_pbv = len(pbv_series) > 0
    pbv_h   = 110 if has_pbv else 0
    title   = f"{base} · {ep:.2f} THB · ▼ from MAX {fmax:.1f}% · ▲ from MIN +{fmin:.1f}%{dy_txt}"

    PH, RH, VH, BH = 400, 130, 100, pbv_h
    total_h = PH + RH + VH + BH + 82  # 82 = header+legend+toolbar

    html = f"""<!DOCTYPE html><html>
<head>
<meta charset="utf-8">
<script src="https://unpkg.com/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:#0b1120; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; overflow:hidden; user-select:none; }}
#hdr {{ padding:7px 14px 3px; color:#dce9ff; font-size:12.5px; font-weight:600;
        white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
#stats {{ padding:0 14px 4px; font-size:11px; color:#4a6480; }}
#ohlc  {{ display:inline; }}
#pct   {{ display:inline; margin-left:10px; }}
.pane  {{ width:100%; }}
#p-rsi {{ border-top:1px solid #1a2a40; }}
#p-vol {{ border-top:1px solid #1a2a40; }}
#p-pbv {{ border-top:1px solid #1a2a40; }}
.toolbar {{ display:flex; gap:3px; padding:5px 10px; background:#080e1c;
            border-top:1px solid #0e1a2e; flex-wrap:nowrap; align-items:center; }}
.pb {{ background:#111a2e; border:1px solid #1e3358; color:#5a7090;
       padding:3px 9px; border-radius:4px; cursor:pointer;
       font-size:11px; font-weight:600; white-space:nowrap; }}
.pb:hover {{ background:#0d1e38; border-color:#00c8f8; color:#c8e8ff; }}
.pb.active {{ background:#0a1e38; border-color:#00c8f8; color:#00c8f8; }}
.sep {{ width:1px; height:16px; background:#1e3358; margin:0 3px; }}
.spacer {{ flex:1; }}
</style>
</head>
<body>
<div id="hdr">{title}</div>
<div id="stats"><span id="ohlc"></span><span id="pct"></span></div>
<div id="p-price" class="pane"></div>
<div id="p-rsi"   class="pane"></div>
<div id="p-vol"   class="pane"></div>
{'<div id="p-pbv" class="pane"></div>' if has_pbv else ''}
<div class="toolbar">
  <!-- Period -->
  <button class="pb" onclick="setRange(90)">3M</button>
  <button class="pb" onclick="setRange(180)">6M</button>
  <button class="pb active" id="pb1y" onclick="setRange(365)">1Y</button>
  <button class="pb" onclick="setRange(730)">2Y</button>
  <button class="pb" onclick="setRange(1825)">5Y</button>
  <button class="pb" onclick="setRange(99999)">Max</button>
  <div class="sep"></div>
  <!-- Interval -->
  <button class="pb active" id="ibD" onclick="setInterval('D')">D</button>
  <button class="pb" id="ibW" onclick="setInterval('W')">W</button>
  <button class="pb" id="ibM" onclick="setInterval('M')">M</button>
  <div class="sep"></div>
  <!-- Type + tools -->
  <button class="pb" id="btn_type" onclick="toggleType()">Line</button>
  <button class="pb" id="btn_log"  onclick="toggleLog()">Log</button>
  <button class="pb" onclick="resetZoom()">⟳</button>
</div>

<script>
const C = {{ bg:'#0b1120',grid:'#0f1c2e',up:'#22d68a',dn:'#ff5566',
             e25:'#ff69b4',e75:'#00e676',e200:'#666',
             rsi:'#a0b8d0',rsiOB:'#ef5350',rsiOS:'#26c6da',
             pbv:'#f5c842',txt:'#8ba8cc',cross:'#2a4060' }};

// ── All interval data ──────────────────────────────────────────────────────────
const DATA = {{
  D: {{ candle:{d_candle}, line:{d_line}, e25:{d_e25}, e75:{d_e75}, e200:{d_e200}, rsi:{d_rsi}, vol:{d_vol} }},
  W: {{ candle:{w_candle}, line:{w_line}, e25:{w_e25}, e75:{w_e75}, e200:{w_e200}, rsi:{w_rsi}, vol:{w_vol} }},
  M: {{ candle:{m_candle}, line:{m_line}, e25:{m_e25}, e75:{m_e75}, e200:{m_e200}, rsi:{m_rsi}, vol:{m_vol} }},
}};
const pbvData = {pbv_data};

let curInterval = 'D';
let showCandle = true;
let logMode = false;
let curRange = 365;  // days

// ── Chart heights ──────────────────────────────────────────────────────────────
const W  = Math.max(window.innerWidth, 400);
const PH = {PH}, RH = {RH}, VH = {VH}, BH = {BH};

document.getElementById('p-price').style.height = PH+'px';
document.getElementById('p-rsi').style.height   = RH+'px';
document.getElementById('p-vol').style.height   = VH+'px';
{'document.getElementById("p-pbv").style.height = BH+"px";' if has_pbv else '// no pbv'}

const mkOpts = (h) => ({{
  width:W, height:h,
  layout:{{ background:{{color:C.bg}}, textColor:C.txt, fontSize:11 }},
  grid:{{ vertLines:{{color:C.grid}}, horzLines:{{color:C.grid}} }},
  crosshair:{{ mode:LightweightCharts.CrosshairMode.Normal,
               vertLine:{{color:C.cross,labelBackgroundColor:'#1e3358'}},
               horzLine:{{color:C.cross,labelBackgroundColor:'#1e3358'}} }},
  timeScale:{{ borderColor:C.grid, timeVisible:true, secondsVisible:false }},
  rightPriceScale:{{ borderColor:C.grid }},
  handleScroll:true, handleScale:true,
}});

const cP = LightweightCharts.createChart(document.getElementById('p-price'), mkOpts(PH));
const cR = LightweightCharts.createChart(document.getElementById('p-rsi'),   mkOpts(RH));
const cV = LightweightCharts.createChart(document.getElementById('p-vol'),   mkOpts(VH));
{'const cB = LightweightCharts.createChart(document.getElementById("p-pbv"), mkOpts(BH));' if has_pbv else 'const cB = null;'}

// ── Series ────────────────────────────────────────────────────────────────────
const sCand = cP.addCandlestickSeries({{
  upColor:C.up,downColor:C.dn,borderUpColor:C.up,borderDownColor:C.dn,wickUpColor:C.up,wickDownColor:C.dn
}});
const sLine = cP.addLineSeries({{ color:C.up, lineWidth:2, visible:false, priceLineVisible:false }});
const sE25  = cP.addLineSeries({{ color:C.e25,  lineWidth:1, priceLineVisible:false, lastValueVisible:false, title:'EMA25'  }});
const sE75  = cP.addLineSeries({{ color:C.e75,  lineWidth:1, priceLineVisible:false, lastValueVisible:false, title:'EMA75'  }});
const sE200 = cP.addLineSeries({{ color:C.e200, lineWidth:1, priceLineVisible:false, lastValueVisible:false, title:'EMA200' }});
const sRsi  = cR.addLineSeries({{ color:C.rsi, lineWidth:1.5, priceLineVisible:false }});
[{{p:70,c:C.rsiOB,s:1}},{{p:50,c:'#222',s:2}},{{p:30,c:C.rsiOS,s:1}}].forEach(l=>
  sRsi.createPriceLine({{price:l.p,color:l.c,lineStyle:l.s,lineWidth:1,axisLabelVisible:true}}));
cR.applyOptions({{rightPriceScale:{{scaleMargins:{{top:0.1,bottom:0.1}},mode:0}}}});
const sVol  = cV.addHistogramSeries({{ priceFormat:{{type:'volume'}} }});
cV.applyOptions({{rightPriceScale:{{scaleMargins:{{top:0.1,bottom:0}}}}}});
let sPbv = null;
if (cB) {{
  sPbv = cB.addLineSeries({{ color:C.pbv, lineWidth:1.5, priceLineVisible:false, title:'P/BV' }});
  sPbv.setData(pbvData);
  cB.applyOptions({{rightPriceScale:{{scaleMargins:{{top:0.1,bottom:0.1}}}}}});
  // P/BV reference lines at 1×, 2×, 3×
  [1,2,3].forEach(v => sPbv.createPriceLine({{price:v,color:'#2a4060',lineStyle:2,lineWidth:1,axisLabelVisible:true}}));
}}

// ── Load interval data ─────────────────────────────────────────────────────────
function loadData(interval) {{
  const d = DATA[interval];
  if (showCandle) {{ sCand.setData(d.candle); sLine.setData(d.line); }}
  else            {{ sCand.setData(d.candle); sLine.setData(d.line); }}
  sCand.setData(d.candle);
  sLine.setData(d.line);
  sE25.setData(d.e25); sE75.setData(d.e75); sE200.setData(d.e200);
  sRsi.setData(d.rsi);
  sVol.setData(d.vol);
  curInterval = interval;
}}
loadData('D');

// ── Crosshair sync with proper grid alignment ─────────────────────────────────────
const allCharts = [cP, cR, cV, ...(cB?[cB]:[])];
const seriesMap = new Map([[cR,sRsi],[cV,sVol]]);
if (cB) seriesMap.set(cB, sPbv);

// Store last synced time to prevent infinite loops
let lastSyncTime = null;

cP.subscribeCrosshairMove(p => {
  const ts = p.time;
  
  // Only sync if time actually changed
  if (ts !== lastSyncTime) {
    lastSyncTime = ts;
    
    // Sync crosshair to all other charts with proper series alignment
    [cR, cV, ...(cB?[cB]:[])].forEach(c => {
      if (ts) {
        const targetSeries = seriesMap.get(c);
        c.setCrosshairPosition(p.point.x, ts, targetSeries);
      } else {
        c.clearCrosshairPosition();
      }
    });
  }
  
  // OHLC legend
  if (p.seriesData?.has(sCand)) {
    const d = p.seriesData.get(sCand);
    if (d) {
      const col = d.close >= d.open ? C.up : C.dn;
      document.getElementById('ohlc').innerHTML =
        `O:<b style="color:${col}">${d.open?.toFixed(2)}</b> ` +
        `H:<b style="color:${C.up}">${d.high?.toFixed(2)}</b> ` +
        `L:<b style="color:${C.dn}">${d.low?.toFixed(2)}</b> ` +
        `C:<b style="color:${col}">${d.close?.toFixed(2)}</b>`;
    }
  }
  
  // % from MAX/MIN in visible range
  if (ts) {
    const vr = cP.timeScale().getVisibleRange();
    if (vr) {
      const vis = DATA[curInterval].candle.filter(x => x.time >= vr.from && x.time <= vr.to);
      if (vis.length > 0) {
        const hi = Math.max(...vis.map(x=>x.high));
        const lo = Math.min(...vis.map(x=>x.low));
        const last = vis[vis.length-1].close;
        const pm = ((last-hi)/hi*100).toFixed(1);
        const pl = ((last-lo)/lo*100).toFixed(1);
        document.getElementById('pct').innerHTML =
          ` <span style="color:#ef5350">▼MAX ${pm}%</span>` +
          ` <span style="color:#22d68a">▲MIN +${pl}%</span>`;
      }
    }
  }
});

// ── Time range sync via logical range with debouncing ──────────────────────────────
let _syncLock = false;
let _syncTimeout = null;

function makeSyncHandler(src) {
  return () => {
    if (_syncLock) return;
    
    // Debounce sync to prevent excessive updates
    clearTimeout(_syncTimeout);
    _syncTimeout = setTimeout(() => {
      _syncLock = true;
      try {
        const lr = src.timeScale().getVisibleLogicalRange();
        if (lr) {
          allCharts.filter(c => c !== src).forEach(c => {
            c.timeScale().setVisibleLogicalRange(lr);
          });
        }
      } finally {
        _syncLock = false;
      }
    }, 10); // 10ms debounce
  };
}

allCharts.forEach(c => {
  c.timeScale().subscribeVisibleLogicalRangeChange(makeSyncHandler(c));
});

// Force grid line alignment on initial load
setTimeout(() => {
  allCharts.forEach(c => c.applyOptions({}));
}, 100);

// ── Period buttons ─────────────────────────────────────────────────────────────
function setRange(days) {{
  document.querySelectorAll('.pb[onclick*="setRange"]').forEach(b=>b.classList.remove('active'));
  event.target.classList.add('active');
  curRange = days;
  applyRange(days);
}}

function applyRange(days) {{
  const src = DATA[curInterval].candle;
  if (!src.length) return;
  if (days >= 99999) {{ allCharts.forEach(c=>c.timeScale().fitContent()); return; }}
  const last = src[src.length-1].time;
  const from = last - days*86400;
  // Use cP as source; sync handler will propagate to others
  _syncLock = false;
  cP.timeScale().setVisibleRange({{from, to: last + 86400}});
}}

// ── Interval buttons ──────────────────────────────────────────────────────────
function setInterval(iv) {{
  ['ibD','ibW','ibM'].forEach(id => document.getElementById(id).classList.remove('active'));
  document.getElementById('ib'+iv).classList.add('active');
  loadData(iv);
  // Re-apply the current period range after switching interval
  setTimeout(() => setRangeSilent(curRange), 50);
}}

function setRangeSilent(days) {{
  applyRange(days);
}}

// ── Toggle type / log ─────────────────────────────────────────────────────────
function toggleType() {{
  showCandle = !showCandle;
  sCand.applyOptions({{visible: showCandle}});
  sLine.applyOptions({{visible: !showCandle}});
  document.getElementById('btn_type').textContent = showCandle ? 'Line' : 'Candle';
}}

function toggleLog() {{
  logMode = !logMode;
  cP.applyOptions({{rightPriceScale:{{mode: logMode?1:0}}}});
  document.getElementById('btn_log').classList.toggle('active', logMode);
}}

function resetZoom() {{ allCharts.forEach(c=>c.timeScale().fitContent()); }}

// ── Resize ────────────────────────────────────────────────────────────────────
window.addEventListener('resize', () => {{
  const nw = Math.max(window.innerWidth, 400);
  allCharts.forEach(c => c.applyOptions({{width:nw}}));
}});

// ── Init: show 1Y ────────────────────────────────────────────────────────────
setTimeout(() => setRangeSilent(365), 200);
</script></body></html>"""

    return html, total_h


# ─── 1b. Matplotlib fallback (used when plotly not installed) ──────────────────
def make_price_chart(ticker, start):
    d=fetch_all(ticker); df=ts_filter(d['price'],start)
    fig=plt.figure(figsize=(14,5.5),facecolor='#0d0d0d')
    if df.empty:
        plt.text(0.5,0.5,f"No price data — {ticker}",ha='center',va='center',color='white',transform=fig.transFigure,fontsize=14)
        return fig
    gs=gridspec.GridSpec(3,1,figure=fig,hspace=0,height_ratios=[3.0,0.9,0.7])
    ax_p=fig.add_subplot(gs[0]); ax_r=fig.add_subplot(gs[1]); ax_v=fig.add_subplot(gs[2])
    close=df['Close']; dates=close.index; n_days=len(df)
    dy=trailing_div_yield(d['divs'],d['price'])
    ax_p.plot(dates,close,lw=1.8,color='white',zorder=3)
    ema_colors=['#ff69b4','#00e676','#aaaaaa']
    for w,c,l in zip(EMA_W,ema_colors,EMA_L): ax_p.plot(dates,close.ewm(span=w).mean(),lw=1.1,color=c,alpha=0.85,label=l,zorder=2)
    style_ax(ax_p); ax_p.set_ylabel('THB',fontsize=9,color='#aaa'); ax_p.set_xlim(dates[0],dates[-1])
    ax_p.set_title(ticker,fontsize=13,fontweight='bold',color='white',loc='left',pad=6)
    ep=close.iloc[-1]
    ax_p.annotate(f"▼ from MAX  {(ep-close.max())/close.max()*100:.1f}%",xy=(0.01,0.96),xycoords='axes fraction',fontsize=8.5,color='#ff4d6d',va='top',fontfamily='monospace')
    ax_p.annotate(f"▲ from MIN  +{(ep-close.min())/close.min()*100:.1f}%",xy=(0.50,0.96),xycoords='axes fraction',fontsize=8.5,color='#4ecca3',va='top',ha='center',fontfamily='monospace')
    ax_p.legend(fontsize=7.5,loc='lower right',facecolor='#1a1a1a',edgecolor='#333',labelcolor='white',framealpha=0.8)
    plt.setp(ax_p.get_xticklabels(),visible=False)
    rsi_v=calc_rsi(close); cr=rsi_v.iloc[-1]; rc='#ef5350' if cr>=70 else ('#26c6da' if cr<=30 else '#b0bec5')
    ax_r.plot(dates,rsi_v,lw=1.2,color=rc,zorder=3)
    ax_r.axhline(70,color='#ef5350',lw=0.7,ls='--',alpha=0.6); ax_r.axhline(30,color='#26c6da',lw=0.7,ls='--',alpha=0.6)
    style_ax(ax_r); ax_r.set_xlim(dates[0],dates[-1]); ax_r.set_ylim(0,100); ax_r.set_yticks([30,50,70]); ax_r.set_ylabel('RSI',fontsize=8,color='#aaa')
    plt.setp(ax_r.get_xticklabels(),visible=False)
    vc=np.where(df['Close']>=df['Open'],'#3d9970','#e74c3c')
    ax_v.bar(dates,df['Volume'],color=vc,alpha=0.7,width=1.2); style_ax(ax_v); ax_v.set_ylabel('Vol',fontsize=7,color='#555')
    ax_v.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"{x/1e6:.0f}M" if x>=1e6 else f"{x/1e3:.0f}K"))
    ax_v.set_xlim(dates[0],dates[-1])
    if n_days<=365: ax_v.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y")); ax_v.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    else: ax_v.xaxis.set_major_formatter(mdates.DateFormatter("%Y")); ax_v.xaxis.set_major_locator(mdates.YearLocator())
    ax_v.tick_params(axis='x',colors='#aaa',labelsize=9)
    plt.tight_layout(); return fig


# ─── 2. Financial tables ────────────────────────────────────────────────────────
def _auto_scale(df):
    try:
        med=df.abs().median().median()
        if med>=1e9: return 1e9,"Billions (B THB)"
        if med>=1e6: return 1e6,"Millions (M THB)"
    except: pass
    return 1.0,"THB"

# Row importance tiers: 'star' = most critical, 'key' = important, '' = standard
_ROW_TIERS = {
    # Income statement key rows
    'Total Revenue':         'star',
    'Gross Profit':          'star',
    'Operating Income':      'star',
    'Net Income':            'star',
    'EBITDA':                'star',
    'Gross Profit Ratio':    'key',
    'Operating Margin':      'key',
    'Net Income Ratio':      'key',
    'Cost Of Revenue':       'key',
    'Total Expenses':        'star',
    'Interest Expense':      'key',
    'Tax Provision':         '',
    'Diluted EPS':           'key',
    # Balance sheet key rows
    'Total Assets':          'star',
    'Total Liabilities Net Minority Interest': 'star',
    'Stockholders Equity':   'star',
    'Total Equity Gross Minority Interest': 'star',
    'Total Debt':            'key',
    'Net Debt':              'key',
    'Cash And Cash Equivalents': 'key',
    'Current Assets':        'key',
    'Current Liabilities':   'key',
    'Working Capital':       'key',
    'Total Capitalization':  '',
    # Cash flow key rows
    'Operating Cash Flow':   'star',
    'Cash Flow From Continuing Operating Activities': 'star',
    'Capital Expenditure':   'key',
    'Free Cash Flow':        'star',
    'Investing Cash Flow':   'key',
    'Financing Cash Flow':   'key',
    'Dividends Paid':        'key',
    'Repurchase Of Capital Stock': '',
    'Changes In Cash':       '',
}

# Row groups for visual separation within tables
_ROW_GROUPS = {
    'income': {
        '📈 Revenue & Profitability': ['Total Revenue','Gross Profit','Operating Income','Net Income','EBITDA','Diluted EPS'],
        '📊 Margins & Ratios':        ['Gross Profit Ratio','Operating Margin','Net Income Ratio'],
        '💸 Costs & Expenses':        ['Cost Of Revenue','Total Expenses','Selling General And Administration','Research And Development','Interest Expense','Tax Provision'],
    },
    'balance': {
        '🏦 Asset Base':              ['Total Assets','Cash And Cash Equivalents','Net Receivables','Inventory','Current Assets','Net PPE'],
        '⚖️ Liabilities & Equity':   ['Current Liabilities','Total Debt','Long Term Debt','Total Liabilities Net Minority Interest','Stockholders Equity','Total Equity Gross Minority Interest'],
        '📐 Working Capital':         ['Working Capital','Net Debt','Total Capitalization'],
    },
    'cashflow': {
        '💰 Operating Cash':          ['Operating Cash Flow','Cash Flow From Continuing Operating Activities'],
        '🏗 Investing':               ['Capital Expenditure','Investing Cash Flow','Free Cash Flow'],
        '🏦 Financing':               ['Financing Cash Flow','Dividends Paid','Repurchase Of Capital Stock','Issuance Of Debt','Repayment Of Debt'],
        '📊 Net Change':              ['Changes In Cash'],
    },
}

def _detect_table_type(title):
    t=title.lower()
    if 'income' in t or 'profit' in t: return 'income'
    if 'balance' in t or 'sheet' in t: return 'balance'
    if 'cash' in t or 'flow' in t:     return 'cashflow'
    return ''

def _df_to_html(df,title,max_years=10):
    if df is None or df.empty: return f"<p style='color:#555;font-style:italic'>No data for {title}</p>"
    cols=sorted(df.columns)[-max_years:]; sub=df[cols].copy(); col_lbs=[str(c)[:4] for c in cols]
    scale,ulabel=_auto_scale(sub)
    table_type=_detect_table_type(title)
    groups=_ROW_GROUPS.get(table_type,{})

    # Build ordered row list: grouped rows first, then remainder
    ordered_rows=[]
    used=set()
    if groups:
        for grp_label,grp_keys in groups.items():
            grp_rows=[(rn,rd) for rn,rd in sub.iterrows() if str(rn) in grp_keys]
            if grp_rows: ordered_rows.append(('group',grp_label,grp_rows)); [used.add(str(rn)) for rn,_ in grp_rows]
        remainder=[(rn,rd) for rn,rd in sub.iterrows() if str(rn) not in used]
        if remainder: ordered_rows.append(('group','📋 Other',remainder))
    else:
        ordered_rows.append(('group','',list(sub.iterrows())))

    hdr="".join(f"<th style='padding:8px 14px;color:#00c8f8;text-align:right;background:#0b1628;border-bottom:2px solid #1e3a5f;font-size:12px;font-weight:700;letter-spacing:0.3px'>{y}</th>" for y in col_lbs)

    rows=""
    for grp_type,grp_label,grp_data in ordered_rows:
        if grp_label:
            rows+=(f"<tr><td colspan='{len(cols)+1}' style='padding:10px 8px 4px;color:#00c8f8;font-size:11px;"
                   f"font-weight:700;text-transform:uppercase;letter-spacing:0.8px;"
                   f"background:#080f1e;border-top:1px solid #1e3358;border-bottom:1px solid #1e3358'>"
                   f"{grp_label}</td></tr>")
        for rn,rd in grp_data:
            rn_str=str(rn)
            tier=_ROW_TIERS.get(rn_str,'')
            if tier=='star':
                row_bg="#0d1e38"; row_border="2px solid #1e4a6e"; label_color="#e8f4ff"; label_weight="700"; label_size="13px"
            elif tier=='key':
                row_bg="#0a1628"; row_border="1px solid #152235"; label_color="#b0c8e8"; label_weight="600"; label_size="12px"
            else:
                row_bg="#080e1c"; row_border="1px solid #0e1a28"; label_color="#5a7090"; label_weight="400"; label_size="11px"
            cells=""
            for col in cols:
                try:
                    v=float(rd[col]); txt="—" if pd.isna(v) else f"{v/scale:,.2f}"
                    if pd.isna(v): clr="#334"
                    elif tier=='star': clr="#ff7a85" if v<0 else "#5ef0aa"
                    elif tier=='key':  clr="#e05070" if v<0 else "#3acc80"
                    else:              clr="#4a6480" if v<0 else "#2a6048"
                    cell_size="13px" if tier=='star' else ("12px" if tier=='key' else "11px")
                    cell_weight="700" if tier=='star' else ("600" if tier=='key' else "400")
                except: txt,clr,cell_size,cell_weight="—","#334","11px","400"
                cells+=(f"<td style='padding:6px 14px;text-align:right;color:{clr};font-size:{cell_size};"
                        f"font-family:monospace;font-weight:{cell_weight};border-bottom:{row_border}'>{txt}</td>")
            rows+=(f"<tr style='background:{row_bg}'>"
                   f"<td style='padding:6px 10px;color:{label_color};font-size:{label_size};font-weight:{label_weight};"
                   f"border-bottom:{row_border};white-space:nowrap;max-width:280px'>{rn_str[:60]}</td>{cells}</tr>")

    return (f"<div style='margin:16px 0'>"
            f"<div style='color:#00c8f8;font-size:15px;font-weight:700;margin-bottom:8px;letter-spacing:-0.3px'>{title}"
            f" <span style='color:#2a4060;font-size:11px;font-weight:400'>({ulabel})</span></div>"
            f"<div style='overflow-x:auto;border-radius:8px;border:1px solid #1e3358'>"
            f"<table style='border-collapse:collapse;width:100%'>"
            f"<thead><tr style='background:#080f1e'><th style='padding:8px 10px;color:#4a6480;text-align:left;border-bottom:2px solid #1e3a5f;font-size:12px;font-weight:700'>Line Item</th>{hdr}</tr></thead>"
            f"<tbody>{rows}</tbody></table></div></div>")


# ─── 3. Fundamental chart ───────────────────────────────────────────────────────
def make_fundamental_chart(ticker):
    DARK='#0d0d0d'; ACC='#00d4ff'; POS='#26c6da'; NEG='#ef5350'; WARN='#f0c040'; GRN='#4ecca3'
    d=fetch_all(ticker); inc=d['income']; bal=d['balance']; cf=d['cashflow']; divs=d['divs']; pr=d['price']
    revenue=safe_row(inc,'Total Revenue'); gross_profit=safe_row(inc,'Gross Profit')
    net_income=safe_row(inc,'Net Income'); ebitda=safe_row(inc,'EBITDA','Normalized EBITDA')
    cogs=safe_row(inc,'Cost Of Revenue','Reconciled Cost Of Revenue')
    total_equity=safe_row(bal,'Stockholders Equity','Total Equity Gross Minority Interest')
    total_assets=safe_row(bal,'Total Assets'); total_debt=safe_row(bal,'Total Debt','Long Term Debt')
    curr_assets=safe_row(bal,'Current Assets'); curr_liab=safe_row(bal,'Current Liabilities')
    op_cf=safe_row(cf,'Operating Cash Flow','Cash Flow From Continuing Operating Activities')
    capex=safe_row(cf,'Capital Expenditure')
    free_cf=(op_cf+capex) if not op_cf.empty and not capex.empty else pd.Series(dtype=float)
    def der(a,b):
        if a.empty or b.empty: return pd.Series(dtype=float)
        return (a/b*100).replace([np.inf,-np.inf],np.nan)
    gross_margin=der(gross_profit,revenue); net_margin=der(net_income,revenue)
    roe=der(net_income,total_equity); roa=der(net_income,total_assets)
    de=(total_debt/total_equity).replace([np.inf,-np.inf],np.nan) if not total_debt.empty and not total_equity.empty else pd.Series(dtype=float)
    cr=(curr_assets/curr_liab).replace([np.inf,-np.inf],np.nan) if not curr_assets.empty and not curr_liab.empty else pd.Series(dtype=float)
    dy_ts=pd.Series(dtype=float)
    if not divs.empty and not pr.empty:
        try:
            dv=divs.copy(); dv.index=strip_tz(dv.index); pc=pr['Close'].copy(); pc.index=strip_tz(pc.index)
            dy_dict={}
            for yr in sorted(set(dv.index.year)):
                ann=dv[dv.index.year==yr].sum(); px=pc[pc.index<=pd.Timestamp(f"{yr}-12-31")]
                if not px.empty and px.iloc[-1]>0: dy_dict[pd.Timestamp(f"{yr}-12-31")]=ann/px.iloc[-1]*100
            dy_ts=pd.Series(dy_dict)
        except: pass
    fig,axes=plt.subplots(4,3,figsize=(14,15),facecolor=DARK,gridspec_kw={'hspace':0.55,'wspace':0.35})
    fig.suptitle(f"  {ticker}  —  Fundamental Trend Analysis",fontsize=14,fontweight='bold',color='white',backgroundcolor='#0e2040',y=1.01,x=0.5,ha='center')
    def bar(ax,s,title,unit='B THB',thr=None,pc=POS,nc=NEG,tc='#f0c040',sc=1e9):
        ax.set_facecolor(DARK)
        for sp in ax.spines.values(): sp.set_edgecolor('#2a2a2a')
        ax.tick_params(colors='#aaa',labelsize=8); ax.grid(axis='y',color='#1e1e1e',linewidth=0.5,linestyle='--',zorder=0)
        if s is None or s.empty:
            ax.text(0.5,0.5,'No data',ha='center',va='center',color='#444',transform=ax.transAxes,fontsize=10)
            ax.set_title(title,color=ACC,fontsize=10,pad=6); return
        xs=[str(x)[:4] for x in s.index]; ys=(s.values/sc).astype(float) if sc!=1 else s.values.astype(float)
        bc=[pc if v>=0 else nc for v in ys]
        bars=ax.bar(xs,ys,color=bc,alpha=0.85,zorder=3,edgecolor='#0d0d0d',linewidth=0.4)
        for b,v in zip(bars,ys):
            if np.isnan(v): continue
            ax.text(b.get_x()+b.get_width()/2,v+abs(max(ys,default=0))*0.02,f"{v:.1f}",ha='center',va='bottom',fontsize=7,color='#aaa',fontfamily='monospace')
        if thr is not None:
            ax.axhline(thr,color=tc,lw=1.2,ls='--',alpha=0.7,zorder=4)
            ax.text(0.01,thr,f" {thr}{unit}",transform=ax.get_yaxis_transform(),fontsize=7,color=tc,va='bottom')
        ax.set_title(title,color=ACC,fontsize=10,pad=6); ax.set_ylabel(unit,fontsize=8,color='#666')
        ax.tick_params(axis='x',rotation=45,labelsize=8); ax.set_xlim(-0.6,len(xs)-0.4)
    bar(axes[0,0],revenue/1e9,"Revenue",unit='B THB',pc=POS)
    if not revenue.empty and not cogs.empty:
        xs=[str(x)[:4] for x in revenue.index]; axes[0,1].set_facecolor(DARK)
        for sp in axes[0,1].spines.values(): sp.set_edgecolor('#2a2a2a')
        axes[0,1].tick_params(colors='#aaa',labelsize=8); axes[0,1].grid(axis='y',color='#1e1e1e',lw=0.5,ls='--',zorder=0)
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
    bar(axes[1,1],net_margin,"Net Margin",unit='%',thr=10,pc=GRN,sc=1)
    bar(axes[1,2],ebitda/1e9,"EBITDA",unit='B THB',pc='#ab47bc')
    bar(axes[2,0],roe,"ROE",unit='%',thr=15,pc=POS,sc=1)
    bar(axes[2,1],roa,"ROA",unit='%',thr=8,pc=POS,sc=1)
    bar(axes[2,2],de,"D/E Ratio",unit='×',thr=1.0,pc='#ef9a9a',nc=NEG,tc=WARN,sc=1)
    bar(axes[3,0],free_cf/1e9,"Free Cash Flow",unit='B THB',thr=0,pc=GRN,tc='#888')
    bar(axes[3,1],cr,"Current Ratio",unit='×',thr=1.5,pc=GRN,tc=WARN,sc=1)
    bar(axes[3,2],dy_ts,"Dividend Yield",unit='%',thr=1.0,pc=WARN,tc='#888',sc=1)
    plt.tight_layout(rect=[0,0,1,0.99]); return fig


# ─── 4. VI Scorecard ─────────────────────────────────────────────────────────────
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
        if all(v and v!=0 for v in [ca,pp,ta,ca1,pp1,ta1]): comp['AQI']=(1-(ca+pp)/ta)/(1-(ca1+pp1)/ta1)
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
    base=ticker.replace('.BK','')
    sg, prof=get_sector_profile(base)
    thr=prof

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
    result={'ticker':ticker,'sections':{},'cycle_flags':[],'red_flags':[],
            'sector_group':sg,'sector_profile':prof}

    # ── A. Business Quality ── (all thresholds sector-adjusted)
    sec_a=[]
    cagr_min=thr['rev_cagr_min']
    try:
        rev=revenue.sort_index().dropna(); n=min(5,len(rev)-1)
        cagr=((rev.iloc[-1]/rev.iloc[-1-n])**(1/n)-1)*100 if len(rev)>=2 else None
        sec_a.append((f'Revenue CAGR (5Y)',f'>{cagr_min}%',
                      f"{cagr:.1f}%" if cagr else 'N/A',
                      cagr is not None and cagr>=cagr_min,
                      'Revenue growing consistently = the business has real demand and pricing power'))
    except: sec_a.append((f'Revenue CAGR (5Y)',f'>{cagr_min}%','N/A',False,''))

    gm_min=thr['gross_margin_min']
    if gm_min is None:
        # Banks/finance: gross margin is meaningless (no COGS vs revenue split)
        sec_a.append(('Gross Margin','N/A — use NIM','—',True,
                      'Banks: use Net Interest Margin (NIM) from filings — gross margin concept does not apply'))
    else:
        gm_med=_med(gm_s)
        sec_a.append((f'Gross Margin (5Y median)',f'>{gm_min}%',
                      f"{gm_med:.1f}%" if gm_med else 'N/A',
                      gm_med is not None and gm_med>=gm_min,
                      f'>{gm_min}% gross margin = strong pricing power and low commodity dependency'))

    nm_min=thr['net_margin_min']
    nm_med=_med(nm_s)
    sec_a.append((f'Net Margin (5Y median)',f'>{nm_min}%',
                  f"{nm_med:.1f}%" if nm_med else 'N/A',
                  nm_med is not None and nm_med>=nm_min,
                  ''
                  ))

    roe_min=thr['roe_min']
    roe_med=_med(roe_s)
    sec_a.append((f'ROE (5Y median)',f'>{roe_min}%',
                  f"{roe_med:.1f}%" if roe_med else 'N/A',
                  roe_med is not None and roe_med>=roe_min,
                  ''
                  ))

    earn_ok=_all_pos(net_income)
    sec_a.append(('Earnings Consistency','All years +',
                  '✓ No loss years' if earn_ok else '✗ Has loss years',
                  earn_ok,'Loss years signal structural or cyclical weakness — avoid for VI'))
    result['sections']['A']=('🏆 Business Quality',sec_a)

    # ── B. Financial Health ── (sector-aware D/E, Current Ratio, FCF mode)
    sec_b=[]
    de_max=thr['de_max']
    if de_max is None:
        # Banks: explain structural leverage — DO NOT penalise
        try:
            de_actual=_s(total_debt/total_equity) if not total_debt.empty and not total_equity.empty else None
            de_str=f"{de_actual:.1f}×" if de_actual else "N/A"
        except: de_str="N/A"
        sec_b.append(('D/E Ratio','Structural (not scored)',
                      f"{de_str} — normal for banks",True,
                      'Banks: deposits are liabilities by design — D/E reflects regulatory capital structure, not over-leverage'))
    else:
        de=_s(total_debt/total_equity) if not total_debt.empty and not total_equity.empty else None
        sec_b.append((f'D/E Ratio',f'<{de_max}×',
                      f"{de:.2f}×" if de is not None else 'N/A',
                      de is not None and de<de_max,
                      'Lower debt relative to equity = less financial risk and more resilience in downturns'))

    cr_min=thr['cr_min']
    if cr_min is None:
        sec_b.append(('Current Ratio','N/A — deposit-funded','—',True,
                      'Banks: liquidity risk managed via asset-liability matching — current ratio does not apply'))
    else:
        crat=_s(curr_assets/curr_liab) if not curr_assets.empty and not curr_liab.empty else None
        sec_b.append((f'Current Ratio',f'>{cr_min}×',
                      f"{crat:.2f}×" if crat is not None else 'N/A',
                      crat is not None and crat>=cr_min,
                      'Current ratio >1: cover current debts — company can pay short-term bills'))

    ic_min=thr['ic_min']
    try:
        ic=float(ebit.iloc[-1]/abs(interest_exp.iloc[-1])) if not ebit.empty and not interest_exp.empty else None
        sec_b.append((f'Interest Coverage',f'>{ic_min}×',
                      f"{ic:.1f}×" if ic else 'N/A',
                      ic is not None and ic>=ic_min,
                      'Interest coverage shows if operating profit can comfortably service debt — below 2× is danger zone'))
    except: sec_b.append((f'Interest Coverage',f'>{ic_min}×','N/A',False,''))

    # FCF mode: all_positive / ocf_positive / avg_3y
    fcf_mode=thr['fcf_mode']
    if fcf_mode=='ocf_positive':
        ocf_ok=_all_pos(op_cf); ocf_v=_s(op_cf)
        sec_b.append(('Operating CF (all years)','Always +',
                      f"✓ Latest: {ocf_v/1e9:.2f}B" if ocf_ok and ocf_v else '✗ Has negative OCF years',
                      ocf_ok,
                      'For financial firms OCF = core lending cash; negative FCF is normal when growing loan book'))
    elif fcf_mode=='avg_3y':
        try:
            fcf_s=free_cf.sort_index().dropna()
            avg_fcf=float(fcf_s.iloc[-3:].mean()) if len(fcf_s)>=1 else None
            ok=avg_fcf is not None and avg_fcf>0
            lbl_val=f"{'✓' if ok else '✗'} 3Y avg: {avg_fcf/1e9:.2f}B" if avg_fcf is not None else 'N/A'
            if avg_fcf is not None and avg_fcf<0:
                result['red_flags'].append(('⚠️ Negative Average FCF',
                    f"3Y average FCF = {avg_fcf/1e9:.2f}B. Sustained negative FCF = cash burn, not investment cycle."))
            sec_b.append(('FCF (3Y average)','Avg > 0',lbl_val,ok,
                          'Single-year FCF can be negative during construction — 3Y average smooths project cycles'))
        except: sec_b.append(('FCF (3Y average)','Avg > 0','N/A',False,''))
    else:
        fcf_ok=_all_pos(free_cf); fcf_v=_s(free_cf)
        sec_b.append(('FCF (all years)','Always +',
                      f"✓ Latest: {fcf_v/1e9:.2f}B" if fcf_ok and fcf_v else '✗ Has negative FCF years',
                      fcf_ok,"Owner earnings — the only truly real profit (Buffett)"))
    result['sections']['B']=('💪 Financial Health',sec_b)

    # ── C. Earnings Integrity ── (standard, but phantom check mode is sector-adjusted)
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
            acc=((ni_s2[idx]-oc_s[idx])/ta_s[idx]*100); al=float(acc.iloc[-1]); ok=abs(al)<=5
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

    # ── D. Beneish M-Score ── (universal — fraud is fraud in any sector)
    m,ml,mc=compute_beneish(inc,bal,cf); m_ok=m is not None and m<=-2.22
    if m is not None and m>-1.78:
        result['red_flags'].append(('🚨 Beneish M-Score Alert',
            f"M={m:.3f} (threshold −1.78). Statistical model flags earnings manipulation."))
    elif m is not None and m>-2.22:
        result['red_flags'].append(('⚠️ Beneish Grey Zone',f"M={m:.3f}. Ambiguous — investigate further."))
    result['sections']['D']=('🕵️ Fraud Risk (Beneish)',
        [('Beneish M-Score','<−2.22',f"{m:.3f} {ml}" if m else ml,m_ok,
          'Statistical fraud model — universal; M>−1.78 = high manipulation risk')])

    # ── E. Valuation ── (dividend yield threshold is sector-adjusted)
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
        # P/B is especially important for banks (book value = capital base)
        pb_note = ('For banks, P/B is the PRIMARY valuation anchor — book value = net loans + assets'
                   if sg=='bank' else 'Graham margin of safety')
        pb_ok = (0<pb<1.5) if sg=='bank' else (0<pb<3)
        pb_tgt = '<1.5×' if sg=='bank' else '<3×'
        sec_e.append(('Price/Book',pb_tgt,f"{pb:.2f}×",pb_ok,pb_note))
    except: sec_e.append(('Price/Book','<3×','N/A',False,''))
    dy_min=thr['div_yield_min']
    dy=trailing_div_yield(divs,price_df)
    sec_e.append((f'Dividend Yield',f'>{dy_min}%',
                  f"{dy:.2f}%" if dy else 'N/A',
                  (dy or 0)>=dy_min,
                  'Dividends confirm real cash profits — companies paying >2% consistently are usually healthy'))
    try:
        per=float(info.get('trailingPE') or info.get('forwardPE'))
        rev2=revenue.sort_index().dropna(); n=min(5,len(rev2)-1)
        cagr2=((rev2.iloc[-1]/rev2.iloc[-1-n])**(1/n)-1) if len(rev2)>=2 else None
        if cagr2 and cagr2>0 and per:
            peg=per/(cagr2*100); ok=peg<1.5
            if peg<1.0:
                result['red_flags'].insert(0,('💎 PEG Opportunity',
                    f"PEG={peg:.2f} — Peter Lynch's 'growth at reasonable price' sweet spot."))
            sec_e.append(('PEG Ratio (P/E÷growth)','<1.5',f"{peg:.2f}",ok,'Lynch: PEG<1 = paying less than growth rate'))
        else: raise ValueError
    except: sec_e.append(('PEG Ratio','<1.5','N/A',False,''))
    result['sections']['E']=('💰 Valuation',sec_e)

    # ── F. Cash Reality Check ── (phantom mode is sector-adjusted)
    sec_f=[]
    phantom_mode=thr['phantom_mode']

    if phantom_mode=='ni_trend':
        # Banks/finance: OCF fluctuates with loan book size — use NI trend instead
        try:
            ni_sorted=net_income.sort_index().dropna()
            if len(ni_sorted)>=3:
                ni_trend=float(ni_sorted.iloc[-1])>float(ni_sorted.iloc[-3])
                ni_latest=float(ni_sorted.iloc[-1])/1e9
                ni_3y_ago=float(ni_sorted.iloc[-3])/1e9
                sec_f.append(('Net Income Trend (3Y)','Growing',
                              f"{'✓' if ni_trend else '✗'} {ni_3y_ago:.1f}B → {ni_latest:.1f}B",
                              ni_trend,
                              'For financial firms OCF swings with loan volumes — consistent NI growth is the quality signal'))
                if not ni_trend:
                    result['red_flags'].append(('⚠️ Declining Net Income',
                        f"NI fell from {ni_3y_ago:.1f}B to {ni_latest:.1f}B over 3 years. Investigate loan quality and provisioning."))
            else: raise ValueError
        except: sec_f.append(('NI Trend (3Y)','Growing','N/A',True,''))
        # Also show raw NI trend
        try:
            lines=[]
            ni_s=net_income.sort_index().dropna()
            for yr in list(ni_s.index)[-5:]:
                lines.append(f"{str(yr)[:4]}: NI={ni_s[yr]/1e9:.1f}B")
            sec_f.append(('Raw NI (5Y)','visual','  |  '.join(lines) if lines else 'N/A',True,
                          'Consistent NI growth = healthy loan book and provisioning'))
        except: sec_f.append(('Raw NI (5Y)','visual','N/A',True,''))
    else:
        # Standard phantom profit check
        try:
            ni_s2=net_income.sort_index().dropna(); op_s=op_cf.sort_index().dropna()
            rv2=revenue.sort_index().dropna()
            common=ni_s2.index.intersection(op_s.index).intersection(rv2.index); yrs=list(common)[-5:]
            phantom=[str(y)[:4] for y in yrs if float(ni_s2[y])>float(rv2[y])*0.005 and float(op_s[y])<0]
            ok=len(phantom)<3
            if not ok:
                result['red_flags'].append(('🚨 Phantom Profit Pattern',
                    f"NI>0 but OCF<0 in {len(phantom)}/5 years ({', '.join(phantom)}). Profit not arriving as cash."))
            sec_f.append(('Phantom Profit Check','NI>0 and OCF<0 <3yr',
                          f"⚠️ {len(phantom)}/5 years" if not ok else f"✓ {len(phantom)}/5 years",ok,
                          'OCF is pre-capex — real profits always generate positive OCF'))
        except: sec_f.append(('Phantom Profit','<3yr','N/A',True,''))
        try:
            lines=[]
            common2=net_income.index.intersection(op_cf.index).intersection(free_cf.index if not free_cf.empty else net_income.index)
            for yr in list(sorted(common2))[-6:]:
                ni_v=net_income[yr]/1e9 if yr in net_income.index else float('nan')
                oc_v=op_cf[yr]/1e9 if yr in op_cf.index else float('nan')
                fc_v=free_cf[yr]/1e9 if yr in free_cf.index and not free_cf.empty else float('nan')
                lines.append(f"{str(yr)[:4]}: NI={ni_v:.1f}B OCF={oc_v:.1f}B FCF={fc_v:.1f}B")
            sec_f.append(('Raw NI/OCF/FCF','visual check','  |  '.join(lines) if lines else 'N/A',True,
                          'OCF should roughly track NI — divergence is the first fraud signal'))
        except: sec_f.append(('Raw NI/OCF/FCF','visual','N/A',True,''))
    result['sections']['F']=('🏴\u200d☠️ Cash Reality Check',sec_f)

    for s2,lbl in [(roe_s,'ROE'),(nm_s,'Net Margin'),(gm_s,'Gross Margin')]:
        f=detect_cycle(s2,lbl)
        if f: result['cycle_flags'].append(f)
    return result


def render_vi_scorecard_st(res):
    ticker=res['ticker']; sections=res['sections']
    red_flags=res['red_flags']; cycle_flags=res['cycle_flags']
    sg=res.get('sector_group','general'); prof=res.get('sector_profile',SECTOR_PROFILES['general'])
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
    if not b_ok and not ph_ok: verdict='🚨 SERIOUS RED FLAGS'; vc='#ef5350'
    elif not ph_ok:            verdict='🚨 PHANTOM PROFIT';    vc='#ef5350'
    elif not b_ok:             verdict='⚠️ Beneish Risk';       vc='#f0c040'
    elif has_wide:             verdict='⚠️ Cash Gap — Monitor'; vc='#f0c040'
    elif overall>=72:          verdict='✅ Strong Buy Candidate';vc='#4ecca3'
    elif overall>=55:          verdict='⚠️ Research Further';   vc='#f0c040'
    else:                      verdict='❌ Avoid';               vc='#ef5350'

    SC={'A':'#00d4ff','B':'#4ecca3','C':'#f0c040','D':'#ef5350','E':'#ab47bc','F':'#ff7043'}
    col1,col2=st.columns([3,1])
    with col1:
        st.markdown(f"<h3 style='color:#00d4ff;margin:0'>🔍 {ticker} — Value Investor Scorecard</h3>",unsafe_allow_html=True)
        # Sector badge
        sc=prof.get('color','#80cbc4')
        st.markdown(
            f"<div style='display:inline-flex;align-items:center;gap:8px;margin:4px 0 6px'>"
            f"<span style='background:rgba(0,0,0,0.3);border:1px solid {sc};border-radius:12px;"
            f"padding:2px 10px;color:{sc};font-size:11px;font-weight:700'>{prof['label']}</span>"
            f"<span style='color:#3a5070;font-size:10px'>{prof['note']}</span></div>",
            unsafe_allow_html=True)
        st.caption("5-section analysis · sector-adjusted · Beneish fraud model · Buffett / Graham standards")
    with col2:
        st.markdown(f"<div style='text-align:right'>"
                    f"<span style='font-size:22px;font-weight:bold;color:{vc}'>{overall:.0f}%</span>"
                    f"<br><span style='color:{vc};font-size:13px'>{verdict}</span>"
                    f"<br><span style='color:#555;font-size:10px'>{tp}/{tn} criteria passed</span></div>",
                    unsafe_allow_html=True)

    cols=st.columns(5)
    for i,(sid,lbl) in enumerate([('A','Quality'),('B','Health'),('C','Integrity'),('D','Fraud'),('E','Value')]):
        if sid in sec_scores:
            p,n,pct=sec_scores[sid]; bc='#4ecca3' if pct>=70 else ('#f0c040' if pct>=50 else '#ef5350')
            with cols[i]:
                st.markdown(f"<div style='text-align:center'>"
                            f"<span style='color:{SC[sid]};font-size:11px;font-weight:bold'>{lbl}</span>"
                            f"<br><span style='color:#aaa;font-size:13px'>{pct:.0f}%</span>"
                            f"<br><div style='background:#0e1628;border-radius:3px;height:6px'>"
                            f"<div style='width:{pct:.0f}%;height:6px;background:{bc};border-radius:3px'></div>"
                            f"</div></div>",unsafe_allow_html=True)
    st.markdown("---")
    if cycle_flags:
        items="  ·  ".join(f"📉 {f['label']}: recent {f['recent']:.1f}% vs 5Y median {f['hist']:.1f}% ({f['pct']:+.1f}pp)" for f in cycle_flags)
        st.info(f"🔄 **Cycle Detector** — {items}")
    for title,msg in red_flags:
        if title.startswith('💎'): st.success(f"**{title}** — {msg}")
        elif '🚨' in title:       st.error  (f"**{title}** — {msg}")
        else:                      st.warning(f"**{title}** — {msg}")
    for sid,(stitle,crit) in sections.items():
        p,n,pct=sec_scores[sid]; bc='#4ecca3' if pct>=70 else ('#f0c040' if pct>=50 else '#ef5350')
        rows=""
        for lbl,tgt,val,ok,expl in crit:
            ic='✅' if ok else '❌'; rb='#0b1a10' if ok else '#1a0b0b'; vc2='#4ecca3' if ok else '#ef5350'
            rows+=(f"<tr style='background:{rb}'>"
                   f"<td style='padding:5px 8px;color:#ddd;font-size:11px'>{ic} {lbl}</td>"
                   f"<td style='padding:5px 8px;color:#666;font-size:10px'>{expl}</td>"
                   f"<td style='padding:5px 8px;color:#888;font-size:10px;text-align:center'>{tgt}</td>"
                   f"<td style='padding:5px 8px;color:{vc2};font-size:11px;font-weight:bold;text-align:right;font-family:monospace;white-space:nowrap'>{val}</td></tr>")
        sc_color=SC.get(sid,'#aaa')
        st.markdown(
            f"<div style='margin-bottom:12px'>"
            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:4px'>"
            f"<span style='color:{sc_color};font-size:13px;font-weight:bold'>{stitle}</span>"
            f"<span style='color:#555;font-size:11px'>{p}/{n}</span>"
            f"<div style='flex:1;background:#0e1628;border-radius:3px;height:5px'>"
            f"<div style='width:{pct:.0f}%;height:5px;background:{bc};border-radius:3px'></div></div></div>"
            f"<table style='width:100%;border-collapse:collapse'>"
            f"<thead><tr style='background:#0a1020'>"
            f"<th style='padding:4px 8px;color:#555;font-size:10px;text-align:left'>Criterion</th>"
            f"<th style='padding:4px 8px;color:#555;font-size:10px;text-align:left'>Why it matters</th>"
            f"<th style='padding:4px 8px;color:#555;font-size:10px;text-align:center'>Target</th>"
            f"<th style='padding:4px 8px;color:#555;font-size:10px;text-align:right'>Value</th>"
            f"</tr></thead><tbody>{rows}</tbody></table></div>",
            unsafe_allow_html=True)
    st.caption(f"Sector: {prof['label']} · Thresholds adjusted per sector model · Beneish (1999) · Not financial advice.")


# ─── 5. News ────────────────────────────────────────────────────────────────────
TICKER_NAMES={
    "AAV":"Asia Aviation","ADVANC":"Advanced Info Service AIS","AEONTS":"Aeon Thana Sinsap",
    "AMATA":"Amata Corporation industrial estate","AOT":"Airports of Thailand",
    "AP":"AP Thailand property","AWC":"Asset World Corp hotel",
    "BA":"Bangkok Airways","BAM":"Bangkok Commercial Asset Management",
    "BANPU":"Banpu coal energy","BBL":"Bangkok Bank","BCH":"Bangkok Chain Hospital",
    "BCP":"Bangchak Corporation","BCPG":"BCPG renewable energy",
    "BDMS":"Bangkok Dusit Medical","BEM":"Bangkok Expressway Metro",
    "BGRIM":"B.Grimm Power","BH":"Bumrungrad Hospital","BJC":"Berli Jucker",
    "BLA":"Bangkok Life Assurance","BTG":"Betagro food","BTS":"BTS Group Holdings skytrain",
    "CBG":"Carabao Group energy drink","CCET":"Cal-Comp Electronics Thailand",
    "CENTEL":"Central Plaza Hotel","CHG":"Chularat Hospital","CK":"CH Karnchang construction",
    "CKP":"CK Power","COCOCO":"Thai Coconut","COM7":"COM7 IT retail",
    "CPALL":"CP All 7-Eleven","CPF":"Charoen Pokphand Foods","CPN":"Central Pattana mall",
    "CRC":"Central Retail","DELTA":"Delta Electronics Thailand","DOHOME":"Do Home hardware",
    "EA":"Energy Absolute","EGCO":"Electricity Generating EGCO","ERW":"Erawan Group hotel",
    "GLOBAL":"Siam Global House","GPSC":"Global Power Synergy","GULF":"Gulf Development energy",
    "GUNKUL":"Gunkul Engineering solar","HANA":"Hana Microelectronics","HMPRO":"HomePro hardware",
    "ICHI":"Ichitan Group tea","IRPC":"IRPC petrochemicals","ITC":"i-Tail Corporation pet food",
    "IVL":"Indorama Ventures","JAS":"Jasmine International telecom",
    "JMART":"Jaymart Group electronics","JMT":"JMT Network Services",
    "KBANK":"Kasikorn Bank","KCE":"KCE Electronics","KKP":"Kiatnakin Phatra bank",
    "KTB":"Krungthai Bank","KTC":"Krungthai Card","LH":"Land and Houses property",
    "M":"MK Restaurant Group","MEGA":"Mega Lifesciences","MINT":"Minor International hotel",
    "MOSHI":"Moshi Moshi retail","MTC":"Muangthai Capital loan","OR":"PTT Oil Retail OR",
    "OSP":"Osotspa beverage","PLANB":"Plan B Media advertising","PR9":"Praram 9 Hospital",
    "PRM":"Prima Marine","PTT":"PTT Public Company oil","PTTEP":"PTT Exploration Production",
    "PTTGC":"PTT Global Chemical","QH":"Quality Houses property","RATCH":"Ratch Group power",
    "RCL":"Regional Container Lines","ROJNA":"Rojana Industrial Park",
    "SAPPE":"Sappe beverage","SAWAD":"Srisawad Corporation","SCB":"SCB X Siam Commercial Bank",
    "SCC":"Siam Cement SCG","SCGP":"SCG Packaging","SIRI":"Sansiri property",
    "SISB":"SISB international school","SJWD":"SCGJWD Logistics","SKY":"Sky ICT",
    "SNNP":"Srinanaporn snack","SPALI":"Supalai property","SPRC":"Star Petroleum Refining",
    "STA":"Sri Trang Agro rubber","STGT":"Sri Trang Gloves","TASCO":"Tipco Asphalt",
    "TCAP":"Thanachart Capital","TIDLOR":"Ngern Tid Lor","TISCO":"Tisco Financial Group",
    "TLI":"Thai Life Insurance","TOP":"Thai Oil refinery","TRUE":"True Corporation telecom",
    "TTB":"TMBThanachart Bank","TU":"Thai Union Group seafood","VGI":"VGI advertising","WHA":"WHA Corporation",
    "ADVICE":"Advice IT Infinite","ASK":"Asia Sermkij Leasing","A5":"Asset Five Group",
    "BBGI":"BBGI biofuel","BEC":"BEC World channel 3","CHEWA":"Chewathai property",
    "DITTO":"Ditto Thailand printing","EPG":"Eastern Polymer Group","FORTH":"Forth Corporation",
    "GCAP":"Global Capital","KAMART":"KA Mart convenience store","MASTER":"Master Style fashion",
    "MFEC":"MFEC technology","MBK":"MBK Center shopping","MONO":"Mono Next media",
    "MORE":"More Return Capital","NETBAY":"Netbay","NEO":"NEO Corporate advisory",
    "PLANET":"Planet Communication","PM":"Premier Marketing","RBF":"R&B Food Supply",
    "RS":"RS Group media commerce","SCGD":"SCG Decor","SGC":"SG Capital",
    "SKR":"Sakari Resources coal","SMPC":"Sahamitr Pressure Container","SPA":"Siam Wellness spa",
    "SSP":"Sermsang Power","THRE":"Thai Reinsurance","TPCH":"TPC Consolidated power","VIH":"Srivichaivejvivat hospital",
}
TICKER_THAI={
    "EA":["\u0e1e\u0e25\u0e31\u0e07\u0e07\u0e32\u0e19\u0e1a\u0e23\u0e34\u0e2a\u0e38\u0e17\u0e18\u0e34\u0e4c","\u0e2d\u0e21\u0e23 \u0e17\u0e2d\u0e07\u0e18\u0e34\u0e23\u0e32\u0e0a"],
    "PTT":["\u0e1b\u0e15\u0e17."],"PTTEP":["\u0e1b\u0e15\u0e17\u0e2a\u0e2a."],
    "AOT":["\u0e17\u0e2d\u0e17.","\u0e17\u0e48\u0e32\u0e2d\u0e32\u0e01\u0e32\u0e28\u0e22\u0e32\u0e19\u0e44\u0e17\u0e22"],
    "KBANK":["\u0e01\u0e2a\u0e34\u0e01\u0e23\u0e44\u0e17\u0e22"],"SCB":["\u0e44\u0e17\u0e22\u0e1e\u0e32\u0e13\u0e34\u0e0a\u0e22\u0e4c"],
    "BBL":["\u0e01\u0e23\u0e38\u0e07\u0e40\u0e17\u0e1e\u0e41\u0e1a\u0e07\u0e01\u0e4c\u0e04\u0e4c"],"KTB":["\u0e01\u0e23\u0e38\u0e07\u0e44\u0e17\u0e22"],
    "GULF":["\u0e01\u0e31\u0e25\u0e1f\u0e4c"],"TOP":["\u0e44\u0e17\u0e22\u0e2d\u0e2d\u0e22\u0e25\u0e4c"],
    "CPALL":["\u0e0b\u0e35\u0e1e\u0e35 \u0e2d\u0e2d\u0e25\u0e25\u0e4c","\u0e40\u0e0b\u0e40\u0e27\u0e48\u0e19"],
    "TRUE":["\u0e17\u0e23\u0e39 \u0e04\u0e2d\u0e23\u0e4c\u0e1b\u0e2d\u0e40\u0e23\u0e0a\u0e31\u0e48\u0e19"],
    "ADVANC":["\u0e40\u0e2d\u0e44\u0e2d\u0e40\u0e2d\u0e2a","AIS"],"BTS":["\u0e1a\u0e35\u0e17\u0e35\u0e40\u0e2d\u0e2a"],
    "SAWAD":["\u0e28\u0e23\u0e35\u0e2a\u0e27\u0e31\u0e2a\u0e14\u0e34\u0e4c"],"TIDLOR":["\u0e40\u0e07\u0e34\u0e19\u0e15\u0e34\u0e14\u0e25\u0e49\u0e2d"],
    "MTC":["\u0e40\u0e21\u0e37\u0e2d\u0e07\u0e44\u0e17\u0e22\u0e41\u0e04\u0e1b\u0e1b\u0e34\u0e15\u0e2d\u0e25"],"BDMS":["\u0e1a\u0e32\u0e07\u0e01\u0e2d\u0e01 \u0e14\u0e38\u0e2a\u0e34\u0e15"],
    "CPF":["\u0e40\u0e08\u0e23\u0e34\u0e0d\u0e42\u0e20\u0e04\u0e20\u0e31\u0e13\u0e11\u0e4c"],"SCC":["\u0e1b\u0e39\u0e19\u0e0b\u0e35\u0e40\u0e21\u0e19\u0e15\u0e4c"],
    "BANPU":["\u0e1a\u0e49\u0e32\u0e19\u0e1b\u0e39"],"IVL":["Indorama"],
}
RISK_KW=[
    (4,"Fraud/Corruption",["fraud","embezzl","corrupt","bribery","ponzi","money launder","misappropriate","fictitious","kickback","fake invoice","\u0e09\u0e49\u0e2d\u0e42\u0e01\u0e07","\u0e17\u0e38\u0e08\u0e23\u0e34\u0e15","\u0e42\u0e01\u0e07\u0e40\u0e07\u0e34\u0e19","\u0e22\u0e31\u0e01\u0e22\u0e2d\u0e01","\u0e1b\u0e25\u0e2d\u0e21"]),
    (4,"Criminal Charges",["arrested","indicted","criminal charge","prosecut","warrant","jail","prison","charged with","\u0e08\u0e31\u0e1a\u0e01\u0e38\u0e21","\u0e04\u0e14\u0e35\u0e2d\u0e32\u0e0d\u0e32","\u0e2d\u0e2d\u0e01\u0e2b\u0e21\u0e32\u0e22\u0e08\u0e31\u0e1a","\u0e16\u0e39\u0e01\u0e08\u0e31\u0e1a"]),
    (4,"Regulatory Action",["sec charges","suspended trading","trading halted","delisted","revoked license","\u0e2b\u0e22\u0e38\u0e14\u0e0b\u0e37\u0e49\u0e2d\u0e02\u0e32\u0e22","\u0e16\u0e2d\u0e14\u0e17\u0e30\u0e40\u0e1a\u0e35\u0e22\u0e19"]),
    (3,"Investigation",["investigat","probe","raided","subpoena","sec inquiry","dsi","special case","\u0e2a\u0e2d\u0e1a\u0e2a\u0e27\u0e19","\u0e15\u0e23\u0e27\u0e08\u0e2a\u0e2d\u0e1a","\u0e1a\u0e38\u0e01\u0e04\u0e49\u0e19","\u0e14\u0e2a\u0e2e."]),
    (3,"Legal Action",["lawsuit","sued","litigation","court order","injunction","class action","filed complaint","\u0e1f\u0e49\u0e2d\u0e07\u0e23\u0e49\u0e2d\u0e07","\u0e23\u0e49\u0e2d\u0e07\u0e17\u0e38\u0e01\u0e02\u0e4c","\u0e28\u0e32\u0e25"]),
    (3,"Mgmt Misconduct",["ceo resign","fired","dismissed","misconduct","insider trading","executive arrested","management arrested","\u0e1c\u0e39\u0e49\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e25\u0e32\u0e2d\u0e2d\u0e01","\u0e1c\u0e39\u0e49\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e16\u0e39\u0e01\u0e08\u0e31\u0e1a"]),
    (2,"Accounting/Audit",["restat","qualified opinion","going concern","material weakness","auditor resign","delayed filing","falsif","\u0e07\u0e1a\u0e01\u0e32\u0e23\u0e40\u0e07\u0e34\u0e19\u0e41\u0e01\u0e49\u0e44\u0e02"]),
    (2,"Regulatory Warning",["warning","penalty","violation","non-complian","fine imposed","sanction","\u0e1b\u0e23\u0e31\u0e1a","\u0e42\u0e17\u0e29","\u0e40\u0e15\u0e37\u0e2d\u0e19"]),
    (2,"Related Party",["related party","self-dealing","tunneling","undisclosed transaction","\u0e23\u0e32\u0e22\u0e01\u0e32\u0e23\u0e01\u0e31\u0e1a\u0e1a\u0e38\u0e04\u0e04\u0e25\u0e17\u0e35\u0e48\u0e40\u0e01\u0e35\u0e48\u0e22\u0e27\u0e02\u0e49\u0e2d\u0e07"]),
    (1,"Controversy",["scandal","controversy","boycott","\u0e41\u0e09","\u0e01\u0e23\u0e30\u0e41\u0e2a"]),
]
POS_KW=["award","record profit","upgraded","buy rating","dividend increase","\u0e01\u0e33\u0e44\u0e23\u0e2a\u0e39\u0e07\u0e2a\u0e38\u0e14"]

def _classify(text):
    t=text.lower(); bs,bc=0,None
    for sev,cat,kws in RISK_KW:
        if any(kw in t for kw in kws) and sev>bs: bs,bc=sev,cat
    return bs,bc,any(kw in t for kw in POS_KW)

def _company_name(base): return TICKER_NAMES.get(base,f"{base} Thailand")

def _is_relevant(title,base,trusted=False):
    if trusted: return True
    t=title.lower(); name=_company_name(base).lower()
    skip={"thai","group","holdings","public","company","thailand","limited","stock","property","power","energy","bank","hotel","hospital","retail","media","advertising","hardware","beverage","insurance","refinery","telecom","cement","chemical","poultry","rubber","seafood","food"}
    words=[w for w in name.split() if len(w)>3 and w not in skip]
    if any(w in t for w in words): return True
    thai_terms=TICKER_THAI.get(base,[])
    if any(th.lower() in t for th in thai_terms): return True
    if _re.search(r'(?<![a-z])'+_re.escape(base.lower())+r'(?![a-z])',t,_re.I): return True
    return False

def _google_rss(query,n=8):
    out=[]
    try:
        url="https://news.google.com/rss/search?q="+_uparse.quote(query)+"&hl=en&gl=TH&ceid=TH:en"
        req=_ureq.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with _ureq.urlopen(req,timeout=10) as r: root=_ET.fromstring(r.read())
        for item in root.findall(".//item")[:n]:
            title=_html_lib.unescape(item.findtext("title","")); link=item.findtext("link","")
            pub=item.findtext("pubDate",""); desc=_html_lib.unescape(item.findtext("description",""))
            src=item.find("{https://news.google.com/rss}source")
            try: date=_dt.strptime(pub[:25],"%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%d")
            except: date=pub[:10]
            out.append({"title":title,"link":link,"source":src.text if src else "Google News","date":date,"snippet":_re.sub(r'<[^>]+',' ',desc)[:300]})
    except: pass
    return out

def _bkk_post_rss(base,n=12):
    out=[]
    try:
        url="https://www.bangkokpost.com/rss/data/business.xml"
        req=_ureq.Request(url,headers={"User-Agent":"Mozilla/5.0"})
        with _ureq.urlopen(req,timeout=8) as r: root=_ET.fromstring(r.read())
        name=_company_name(base).lower()
        skip={"thai","group","holdings","public","company","thailand","limited","stock","property","power","energy","bank","hotel"}
        words=[w for w in name.split() if len(w)>3 and w not in skip]
        thai_terms=[t.lower() for t in TICKER_THAI.get(base,[])]
        for item in root.findall(".//item"):
            title=_html_lib.unescape(item.findtext("title","")); desc=_html_lib.unescape(item.findtext("description",""))
            combined=(title+" "+desc).lower()
            if (any(w in combined for w in words) or any(th in combined for th in thai_terms) or base.lower() in combined):
                link=item.findtext("link",""); pub=item.findtext("pubDate","")
                try: date=_dt.strptime(pub[:25],"%a, %d %b %Y %H:%M:%S").strftime("%Y-%m-%d")
                except: date=pub[:10]
                out.append({"title":title,"link":link,"source":"Bangkok Post","date":date,"snippet":_re.sub(r'<[^>]+',' ',desc)[:300]})
                if len(out)>=n: break
    except: pass
    return out

def _yf_news(ticker,n=12):
    out=[]
    try:
        for art in (yf.Ticker(ticker).news or [])[:n]:
            ct=art.get("content",{}); title=ct.get("title",art.get("title",""))
            link=(ct.get("canonicalUrl") or {}).get("url","") or (ct.get("clickThroughUrl") or {}).get("url","")
            pub=art.get("providerPublishTime",0)
            date=_dt.fromtimestamp(pub,tz=_tz.utc).strftime("%Y-%m-%d") if pub else ""
            if title: out.append({"title":title,"link":link,"source":"Yahoo Finance","date":date,"snippet":""})
    except: pass
    return out

@st.cache_data(ttl=1800,show_spinner=False)
def fetch_all_news(ticker):
    base=ticker.replace(".BK",""); name=_company_name(base); thai_terms=TICKER_THAI.get(base,[])
    raw=[dict(i,trusted=True) for i in _yf_news(ticker)]
    for q in [f'"{name}"',f'"{name}" fraud investigation scandal',f'"{name}" SEC DSI audit lawsuit OR criminal']:
        raw+=[dict(i,trusted=True) for i in _google_rss(q,n=8)]
    if thai_terms:
        primary=thai_terms[0]
        for q in [f'"{primary}"',f'"{primary}" \u0e17\u0e38\u0e08\u0e23\u0e34\u0e15 \u0e2a\u0e2d\u0e1a\u0e2a\u0e27\u0e19',f'"{primary}" \u0e01.\u0e25.\u0e15. \u0e14\u0e2a\u0e2e.']:
            raw+=[dict(i,trusted=True) for i in _google_rss(q,n=6)]
    raw+=[dict(i,trusted=True) for i in _bkk_post_rss(base,n=10)]
    raw+=[dict(i,trusted=False) for i in _google_rss(f'{base} \u0e2a\u0e15\u0e4a\u0e2d\u0e01 \u0e2a\u0e2d\u0e1a\u0e2a\u0e27\u0e19',n=4)]
    seen=set(); out=[]
    for item in raw:
        title=item.get("title",""); trusted=item.get("trusted",False); k=title[:48].lower().strip()
        if not k or k in seen: continue
        if not _is_relevant(title,base,trusted=trusted): continue
        snippet=item.get("snippet","")
        if not trusted and snippet and not _is_relevant(snippet,base,trusted=False): continue
        seen.add(k); out.append({kk:vv for kk,vv in item.items() if kk!="trusted"})
    out.sort(key=lambda x: x.get("date",""),reverse=True)
    return out

def render_news_st(ticker,articles):
    base=ticker.replace(".BK","")
    if not articles: st.info(f"No news found for {base}."); return
    now=_dt.now(); max_sev=0; flagged=0; positives=0
    for art in articles:
        t=art.get("title",""); snip=art.get("snippet",""); sev,cat,is_pos=_classify(t+" "+snip)
        if sev>=3: flagged+=1
        if is_pos: positives+=1
        if sev>max_sev: max_sev=sev
    if max_sev>=4 or flagged>=3:   ov="🚨 High Risk"; ov_c="#ef5350"
    elif max_sev>=3 or flagged>=1: ov="⚠️ Caution"; ov_c="#f0c040"
    else:                           ov="✅ Clean"; ov_c="#4ecca3"
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:16px;margin-bottom:12px'>"
        f"<span style='color:#00d4ff;font-size:16px;font-weight:bold'>📰 {base} News</span>"
        f"<span style='color:{ov_c};font-size:14px;font-weight:bold'>{ov}</span>"
        f"<span style='color:#555;font-size:11px'>{len(articles)} articles · {flagged} flagged · {positives} positive</span></div>",
        unsafe_allow_html=True)
    SEV_C={4:"#ff1744",3:"#ef5350",2:"#f0c040",1:"#aaaaaa",0:"#444444"}
    SEV_L={4:"CRITICAL",3:"HIGH",2:"MEDIUM",1:"LOW",0:""}
    for art in articles:
        title=art.get("title",""); link=art.get("link",""); src=art.get("source","")
        date_s=art.get("date",""); snip=art.get("snippet",""); sev,cat,is_pos=_classify(title+" "+snip)
        age_days=999
        try: age_days=(now-_dt.strptime(date_s,"%Y-%m-%d")).days
        except: pass
        opacity=1.0 if age_days<=90 else (0.65 if age_days<=365 else 0.35)
        if is_pos: bdr="#4ecca3"; lbl="✅ POSITIVE"
        elif sev>0: bdr=SEV_C[sev]; lbl=f"{'🚨' if sev>=4 else '🔴' if sev>=3 else '🟡'} {SEV_L[sev]}: {cat}"
        else: bdr="#1e3a5f"; lbl=""
        age_note="" if age_days<=365 else f" · <span style='color:#f0c040'>⏰ {age_days//365}y ago</span>"
        snip_html=f"<br><span style='color:#888;font-size:10px'>{snip[:180]}…</span>" if snip and sev>0 else ""
        lbl_html=f" · <span style='color:{bdr};font-weight:bold'>{lbl}</span>" if lbl else ""
        st.markdown(
            f"<div style='border-left:3px solid {bdr};padding:6px 12px;margin-bottom:5px;background:#0a1020;border-radius:0 4px 4px 0;opacity:{opacity}'>"
            f"<div style='display:flex;justify-content:space-between;align-items:flex-start'>"
            f"<a href='{link}' target='_blank' style='color:#ddd;text-decoration:none;font-size:12px;flex:1'>{title}</a>"
            f"<span style='color:#555;font-size:10px;white-space:nowrap;margin-left:8px'>{src}</span></div>"
            f"<div style='color:#555;font-size:10px;margin-top:2px'>{date_s}{age_note}{lbl_html}</div>"
            f"{snip_html}</div>",unsafe_allow_html=True)


# ─── 6. Screener ────────────────────────────────────────────────────────────────
def compute_quick_score(ticker_yf):
    try:
        res=compute_vi_scorecard(ticker_yf); secs=res['sections']; sec_sc={}
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
        revenue=safe_row(d['income'],'Total Revenue'); net_income=safe_row(d['income'],'Net Income')
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
            if not op_cf.empty and not capex.empty: fcf_ok=bool(((op_cf+capex)>0).all())
        except: pass
        m,ml,_=compute_beneish(d['income'],d['balance'],d['cashflow'])
        pe=info.get('trailingPE') or info.get('forwardPE')
        dy=trailing_div_yield(d['divs'],d['price'])
        base=ticker_yf.replace('.BK',''); name=TICKER_NAMES.get(base,"")
        sg,prof=get_sector_profile(base)
        return {"Ticker":base,"Company":name,"VI Score":round(overall,1),"Verdict":verdict,
                "Sector":prof['label'],
                "Rev CAGR%":cagr,"ROE%":roe,"D/E":de,
                "P/E":round(float(pe),1) if pe else None,
                "Div%":round(dy,1) if dy else None,
                "M-Score":round(m,2) if m else None,"FCF+":fcf_ok,
                "A%":round(sec_sc.get('A',(0,0,0))[2]),"B%":round(sec_sc.get('B',(0,0,0))[2]),
                "C%":round(sec_sc.get('C',(0,0,0))[2]),"D%":round(sec_sc.get('D',(0,0,0))[2]),
                "E%":round(sec_sc.get('E',(0,0,0))[2])}
    except Exception as e:
        return {"Ticker":ticker_yf.replace('.BK',''),"Company":"","VI Score":0,"Verdict":"Error","Sector":"",
                "Rev CAGR%":None,"ROE%":None,"D/E":None,"P/E":None,"Div%":None,
                "M-Score":None,"FCF+":False,"A%":0,"B%":0,"C%":0,"D%":0,"E%":0}

def _sc(p): return "#4ecca3" if p>=72 else ("#f0c040" if p>=55 else "#ef5350")

def _build_screener_page(rows):
    def cell(v,fmt,good,bad):
        if v is None: return "<span style='color:#334'>—</span>"
        ok=good(v); fail=bad(v); c="#4ecca3" if ok else ("#ef5350" if fail else "#f0c040")
        return f"<span style='color:{c}'>{fmt.format(v)}</span>"
    def badge(verdict):
        if "Strong" in verdict:   bg,tc,ic="#0a2016","#4ecca3","✅"
        elif "Serious" in verdict or "Phantom" in verdict: bg,tc,ic="#220808","#ef5350","🚨"
        elif "Beneish" in verdict: bg,tc,ic="#1e1600","#f0c040","⚠️"
        elif "Research" in verdict: bg,tc,ic="#141200","#d4b800","⚠️"
        elif "Avoid" in verdict:   bg,tc,ic="#180808","#e05050","❌"
        else: bg,tc,ic="#111","#888",""
        label=verdict.replace("✅ ","").replace("🚨 ","").replace("⚠️ ","").replace("❌ ","")
        return (f"<span style='background:{bg};color:{tc};padding:2px 10px;border-radius:10px;font-size:11px;font-weight:600;white-space:nowrap'>{ic} {label}</span>")
    def mini_bars(r):
        out=""
        for lbl,key in [("Q","A%"),("H","B%"),("I","C%"),("F","D%"),("V","E%")]:
            pct=r.get(key) or 0; c=_sc(pct)
            out+=(f"<div style='display:inline-block;text-align:center;margin-right:3px'>"
                  f"<div style='font-size:8px;color:#446;margin-bottom:1px'>{lbl}</div>"
                  f"<div style='position:relative;width:22px;height:32px;background:#0c1628;border-radius:3px;overflow:hidden'>"
                  f"<div style='position:absolute;bottom:0;left:0;right:0;height:{pct:.0f}%;background:{c};opacity:0.8'></div>"
                  f"<span style='position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:8px;color:#ccc;font-weight:700;z-index:1'>{pct:.0f}</span></div></div>")
        return out
    def beneish(m):
        if m is None: return "<span style='color:#334'>—</span>"
        if m>-1.78: c,l="#ef5350","HIGH"
        elif m>-2.22: c,l="#f0c040","GREY"
        else: c,l="#4ecca3","LOW"
        return f"<span style='color:{c};font-size:11px'>{m:.2f} <b>{l}</b></span>"
    strong=sum(1 for r in rows if "Strong" in r.get("Verdict",""))
    research=sum(1 for r in rows if "Research" in r.get("Verdict",""))
    risk=sum(1 for r in rows if "Beneish" in r.get("Verdict","") or "Phantom" in r.get("Verdict",""))
    avoid=sum(1 for r in rows if "Avoid" in r.get("Verdict",""))
    serious=sum(1 for r in rows if "Serious" in r.get("Verdict",""))
    avg_sc=sum(r.get("VI Score",0) or 0 for r in rows)/len(rows) if rows else 0
    def stat(v,lbl,c):
        return (f"<div style='background:#0a1220;border:1px solid #0e1e35;border-radius:8px;padding:10px 14px;text-align:center;flex:1;min-width:90px'>"
                f"<div style='font-size:22px;font-weight:800;color:{c}'>{v}</div>"
                f"<div style='font-size:10px;color:#446;margin-top:2px'>{lbl}</div></div>")
    summary=(f"<div style='display:flex;gap:8px;margin-bottom:18px;flex-wrap:wrap'>"
             +stat(f"{avg_sc:.0f}%","Avg Score","#00d4ff")+stat(strong,"✅ Strong Buy","#4ecca3")
             +stat(research,"⚠️ Research More","#d4b800")+stat(risk,"⚠️ Fraud Risk","#f08020")
             +stat(avoid,"❌ Avoid","#e05050")+stat(serious,"🚨 Serious","#ff2244")+"</div>")
    trs=""
    for i,r in enumerate(rows):
        score=r.get("VI Score",0) or 0; sc=_sc(score)
        bg="#07101f" if i%2==0 else "#080e1c"
        ticker=r.get("Ticker",""); company=(r.get("Company","") or "")[:28]
        sector_lbl=(r.get("Sector","") or "").replace("🏦 ","").replace("💳 ","").replace("🏗 ","").replace("⚡ ","").replace("🏭 ","")[:12]
        trs+=f"""
        <tr style='background:{bg};border-bottom:1px solid #0b1628'>
          <td style='padding:10px 8px;color:#334;font-size:11px;text-align:center;width:30px'>{i+1}</td>
          <td style='padding:10px 8px;min-width:130px'>
            <div style='font-size:15px;font-weight:700;color:#e8f0ff'>{ticker}</div>
            <div style='font-size:10px;color:#3a5070;margin-top:1px'>{company}</div>
            <div style='font-size:9px;color:#2a4060;margin-top:1px'>{sector_lbl}</div>
          </td>
          <td style='padding:10px 8px'>{badge(r.get("Verdict","—"))}</td>
          <td style='padding:10px 8px;text-align:center'>
            <div style='display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:50%;border:2.5px solid {sc};font-size:13px;font-weight:800;color:{sc}'>{score:.0f}</div>
          </td>
          <td style='padding:10px 8px'>{mini_bars(r)}</td>
          <td style='padding:10px 8px;font-family:monospace;font-size:12px'>{cell(r.get("Rev CAGR%"),"{:.1f}%",lambda v:v>=7,lambda v:v<0)}</td>
          <td style='padding:10px 8px;font-family:monospace;font-size:12px'>{cell(r.get("ROE%"),"{:.1f}%",lambda v:v>=15,lambda v:v<8)}</td>
          <td style='padding:10px 8px;font-family:monospace;font-size:12px'>{cell(r.get("D/E"),"{:.2f}×",lambda v:v<0.5,lambda v:v>1.5)}</td>
          <td style='padding:10px 8px;font-family:monospace;font-size:12px'>{cell(r.get("P/E"),"{:.1f}×",lambda v:0<v<20,lambda v:v>35 or v<=0)}</td>
          <td style='padding:10px 8px;font-family:monospace;font-size:12px'>{cell(r.get("Div%"),"{:.1f}%",lambda v:v>=2,lambda v:v<0.5)}</td>
          <td style='padding:10px 8px'>{beneish(r.get("M-Score"))}</td>
          <td style='padding:10px 8px;text-align:center;font-size:12px'>
            {"<span style='color:#4ecca3'>✔</span>" if r.get("FCF+") else "<span style='color:#445'>✘</span>"}
          </td>
        </tr>"""
    th=("background:#060d1a;color:#3a5878;font-size:10px;font-weight:600;padding:8px 8px;text-transform:uppercase;letter-spacing:0.5px;text-align:left;border-bottom:1px solid #0e1e35;white-space:nowrap")
    header=(f"<tr><th style='{th}'>#</th><th style='{th}'>Stock</th><th style='{th}'>Verdict</th>"
            f"<th style='{th};text-align:center'>Score</th><th style='{th}'>Q H I F V</th>"
            f"<th style='{th}'>Rev CAGR</th><th style='{th}'>ROE</th><th style='{th}'>D/E</th>"
            f"<th style='{th}'>P/E</th><th style='{th}'>Div%</th><th style='{th}'>Beneish M</th>"
            f"<th style='{th};text-align:center'>FCF+</th></tr>")
    row_h=62; head_h=80; total_h=head_h+len(rows)*row_h+20; height=min(total_h,820)
    return f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
<style>
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{background:#07101f;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#d0d8e8;padding:0;}}
  .wrap{{padding:4px 2px 12px;}} table{{width:100%;border-collapse:collapse;}}
  tbody tr:hover{{background:#0d1a2e!important;}}
  ::-webkit-scrollbar{{height:5px;background:#07101f;}}
  ::-webkit-scrollbar-thumb{{background:#1e3a5f;border-radius:3px;}}
</style></head><body><div class='wrap'>
  {summary}<div style='overflow-x:auto'><table><thead>{header}</thead><tbody>{trs}</tbody></table></div>
</div></body></html>""", height

def show_screener_tab():
    st.markdown("<h3 style='color:#00d4ff;margin-bottom:2px'>🔍 Screener</h3>"
                "<p style='color:#3a5070;font-size:13px;margin:0 0 16px'>Batch VI-scorecard across SET100 / MAI. "
                "Thresholds auto-adjust per sector. Green ≥72% · yellow ≥55% · red below.</p>",unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns([2,2,1,1])
    with c1: universe=st.selectbox("Universe",["SET100","MAI","SET100 + MAI"],key="scr_uni")
    with c2: sector_f=st.selectbox("Sector",["All Sectors"]+sorted(SECTOR_MAP.keys()),key="scr_sec")
    with c3: min_score=st.number_input("Min Score%",0,100,0,5,key="scr_min")
    with c4: sort_by=st.selectbox("Sort by",["VI Score","ROE%","Rev CAGR%","Div%","P/E"],key="scr_sort")
    run=st.button("▶  Run Screener",type="primary",use_container_width=True)
    if not run and "screener_results" not in st.session_state:
        st.markdown("<div style='background:#080e1c;border:1px dashed #1a2e48;border-radius:10px;padding:40px;text-align:center;margin-top:20px'>"
                    "<div style='font-size:40px'>🔍</div>"
                    "<div style='color:#00d4ff;font-size:17px;margin:10px 0 6px;font-weight:600'>Ready to screen</div>"
                    "<div style='color:#3a5070;font-size:13px'>Pick a universe and hit <b style='color:#8ab'>Run Screener</b></div>"
                    "<div style='color:#253545;font-size:11px;margin-top:8px'>SET100 = ~3–5 min · results cached 6h · thresholds auto-adjusted per sector</div>"
                    "</div>",unsafe_allow_html=True)
        return
    if run:
        if universe=="SET100":       pool=SET100
        elif universe=="MAI":        pool=MAI_TICKERS
        else:                        pool=SET100+MAI_TICKERS
        if sector_f!="All Sectors":  pool=[t for t in pool if t in set(SECTOR_MAP.get(sector_f,[]))]
        if not pool: st.warning("No tickers match this filter."); return
        bar=st.progress(0); results=[]; errors=[]
        for i,t in enumerate(pool):
            bar.progress((i+1)/len(pool),text=f"Analysing **{t}** · {i+1}/{len(pool)}")
            r=compute_quick_score(to_yf(t)); results.append(r)
            if r.get("Verdict")=="Error": errors.append(t)
        bar.empty(); ok_n=len(results)-len(errors)
        msg=f"Done — {ok_n}/{len(results)} stocks analysed"
        if errors: msg+=f"  ·  {len(errors)} no data: {', '.join(errors[:5])}"
        st.success(f"✅ {msg}")
        st.session_state["screener_results"]=results; st.session_state["screener_meta"]=f"{universe} · {sector_f}"
    if "screener_results" not in st.session_state: return
    all_r=st.session_state["screener_results"]
    filtered=[r for r in all_r if (r.get("VI Score") or 0)>=min_score]
    asc=(sort_by=="P/E"); filtered.sort(key=lambda r:(r.get(sort_by) or 0),reverse=not asc)
    meta=st.session_state.get("screener_meta","")
    st.caption(f"**{len(filtered)}** stocks · {meta} · min {min_score}% · sorted by {sort_by}  · Q=Quality  H=Health  I=Integrity  F=Fraud  V=Valuation")
    fa,fb,fc,fd,fe=st.columns(5); active=st.session_state.get("scr_filter","all")
    with fa:
        if st.button("✅ Strong Buy",use_container_width=True,key="f_sb"): st.session_state["scr_filter"]="sb" if active!="sb" else "all"
    with fb:
        if st.button("🚨 Red Flags",use_container_width=True,key="f_rf"): st.session_state["scr_filter"]="rf" if active!="rf" else "all"
    with fc:
        if st.button("✔ FCF+ only",use_container_width=True,key="f_fcf"): st.session_state["scr_filter"]="fcf" if active!="fcf" else "all"
    with fd:
        if st.button("💰 Div ≥ 2%",use_container_width=True,key="f_div"): st.session_state["scr_filter"]="div" if active!="div" else "all"
    with fe:
        if st.button("📈 ROE ≥ 15%",use_container_width=True,key="f_roe"): st.session_state["scr_filter"]="roe" if active!="roe" else "all"
    flt=st.session_state.get("scr_filter","all")
    if flt=="sb":   filtered=[r for r in filtered if "Strong" in r.get("Verdict","")]
    elif flt=="rf": filtered=[r for r in filtered if "🚨" in r.get("Verdict","")]
    elif flt=="fcf":filtered=[r for r in filtered if r.get("FCF+")]
    elif flt=="div":filtered=[r for r in filtered if (r.get("Div%") or 0)>=2]
    elif flt=="roe":filtered=[r for r in filtered if (r.get("ROE%") or 0)>=15]
    if filtered:
        html_page,h=_build_screener_page(filtered); _components.html(html_page,height=h,scrolling=True)
    else: st.info("No stocks match this filter.")
    st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
    st.markdown("<div style='color:#6688aa;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px'>🔎 Deep Dive</div>",unsafe_allow_html=True)
    tickers_shown=["— pick a stock —"]+[r["Ticker"] for r in filtered]
    drill=st.selectbox("",tickers_shown,key="scr_drill",label_visibility="collapsed")
    if drill and drill!="— pick a stock —":
        name=TICKER_NAMES.get(drill,""); sg,prof=get_sector_profile(drill); sc=prof.get('color','#80cbc4')
        st.markdown(
            f"<div style='background:#080e1c;border:1px solid #1a2e48;border-radius:8px;padding:10px 18px;margin-bottom:12px;display:flex;align-items:center;gap:12px'>"
            f"<span style='font-size:20px;font-weight:800;color:#00d4ff'>{drill}</span>"
            f"<span style='color:#3a5070;font-size:13px'>{name}</span>"
            f"<span style='background:rgba(0,0,0,0.3);border:1px solid {sc};border-radius:10px;padding:2px 8px;color:{sc};font-size:10px;font-weight:700'>{prof['label']}</span></div>",
            unsafe_allow_html=True)
        dt=st.tabs(["📈 Price","📋 Financials","📊 Fundamentals","⚖️ VI Scorecard","📰 News"])
        with dt[0]:
            with st.spinner("Loading…"):
                    html_c,h_c=make_tv_chart(to_yf(drill)); _components.html(html_c,height=h_c,scrolling=False)
        with dt[1]:
            d=fetch_all(to_yf(drill))
            for title,df in [("Income Statement",d['income']),("Balance Sheet",d['balance']),("Cash Flow",d['cashflow'])]:
                st.markdown(_df_to_html(df,title),unsafe_allow_html=True)
        with dt[2]:
            with st.spinner("Plotting…"): fig=make_fundamental_chart(to_yf(drill)); st.pyplot(fig); plt.close(fig)
        with dt[3]:
            with st.spinner("Scoring…"): render_vi_scorecard_st(compute_vi_scorecard(to_yf(drill)))
        with dt[4]:
            with st.spinner("Fetching news…"): render_news_st(to_yf(drill),fetch_all_news(to_yf(drill)))

# ─── Main ────────────────────────────────────────────────────────────────────────
def main():
    # ── Init session state ──────────────────────────────────────────────────────
    if 'sb_sec' not in st.session_state: st.session_state['sb_sec'] = 'All'
    if 'mai_sec' not in st.session_state: st.session_state['mai_sec'] = 'All'

    with st.sidebar:
        st.markdown("<div style='padding:4px 0 12px'>"
                    "<div style='color:#00c8f8;font-size:20px;font-weight:800;letter-spacing:-0.5px'>🏦 STOCK Analyser</div>"
                    "<div style='color:#2a4060;font-size:11px;margin-top:3px'>Value Investor Edition</div></div>",unsafe_allow_html=True)

        # ── Date range ──────────────────────────────────────────────────────────
        st.markdown("<div class='sidebar-label'>📅 Chart Start Date</div>",unsafe_allow_html=True)
        c1,c2=st.columns([3,2])
        with c1: start_year=st.selectbox("Year",[str(y) for y in range(2015,2026)],index=6,key="sy",label_visibility="collapsed")
        with c2: start_month=st.selectbox("Month",[f"{m:02d}" for m in range(1,13)],index=0,key="sm",label_visibility="collapsed")
        start=f"{start_year}-{start_month}-01"
        st.markdown("<hr>",unsafe_allow_html=True)

        # ── SET100 section ──────────────────────────────────────────────────────
        st.markdown("<div class='sidebar-label'><span style='color:#00c8f8'>●</span> SET100</div>",unsafe_allow_html=True)

        # Sector icon grid — 3 per row, compact
        sector_keys=['All']+sorted(SECTOR_MAP.keys())
        active_sec=st.session_state.get('sb_sec','All')
        for row_start in range(0,len(sector_keys),3):
            row_keys=sector_keys[row_start:row_start+3]
            btn_cols=st.columns(3)
            for ci,sk in enumerate(row_keys):
                ico,lbl=SECTOR_ICONS.get(sk,(sk[0],sk[:5]))
                is_active=(sk==active_sec)
                with btn_cols[ci]:
                    if is_active:
                        st.markdown(f"<div style='border:1px solid #00c8f8;border-radius:6px;background:#0a1e38;padding:1px 0;margin-bottom:2px'></div>",unsafe_allow_html=True)
                    if st.button(f"{ico} {lbl}",key=f"sec_btn_{sk}",help=sk,use_container_width=True):
                        st.session_state['sb_sec']=sk if sk!=active_sec else 'All'
                        if 'set_ms' in st.session_state: del st.session_state['set_ms']
                        st.rerun()

        # Only show tickers from selected sector
        active_sec=st.session_state.get('sb_sec','All')
        if active_sec=='All':
            available_set100=SET100
            ms_placeholder="Type or pick any SET100 stock…"
        else:
            available_set100=[t for t in SECTOR_MAP.get(active_sec,[]) if t in SET100]
            ms_placeholder=f"Pick from {active_sec} ({len(available_set100)} stocks)…"

        set_sel=st.multiselect("SET100 tickers",available_set100,
                               placeholder=ms_placeholder,key="set_ms",label_visibility="collapsed")
        st.markdown("<hr>",unsafe_allow_html=True)

        # ── MAI section ─────────────────────────────────────────────────────────
        st.markdown("<div class='sidebar-label'><span style='color:#4ecca3'>●</span> MAI</div>",unsafe_allow_html=True)

        # MAI sector filter
        mai_sec_keys=['All']+sorted(MAI_SECTOR_MAP.keys())
        active_mai=st.session_state.get('mai_sec','All')
        for mrow_start in range(0,len(mai_sec_keys),3):
            mrow_keys=mai_sec_keys[mrow_start:mrow_start+3]
            mai_cols=st.columns(3)
            for ci,sk in enumerate(mrow_keys):
                ico,lbl=SECTOR_ICONS.get(sk,(sk[0],sk[:5]))
                is_active=(sk==active_mai)
                with mai_cols[ci]:
                    if is_active:
                        st.markdown(f"<div style='border:1px solid #4ecca3;border-radius:6px;background:#0a1e2e;padding:1px 0;margin-bottom:2px'></div>",unsafe_allow_html=True)
                    if st.button(f"{ico} {lbl}",key=f"mai_btn_{sk}",help=sk,use_container_width=True):
                        st.session_state['mai_sec']=sk if sk!=active_mai else 'All'
                        if 'mai_ms' in st.session_state: del st.session_state['mai_ms']
                        st.rerun()

        active_mai=st.session_state.get('mai_sec','All')
        if active_mai=='All':
            available_mai=MAI_TICKERS
            mai_placeholder="Type or pick any MAI stock…"
        else:
            available_mai=[t for t in MAI_SECTOR_MAP.get(active_mai,[]) if t in MAI_TICKERS]
            mai_placeholder=f"Pick from {active_mai} MAI ({len(available_mai)})…"

        mai_sel=st.multiselect("MAI tickers",available_mai,
                               placeholder=mai_placeholder,key="mai_ms",label_visibility="collapsed")
        st.markdown("<hr>",unsafe_allow_html=True)

        # ── DR / ETF section ─────────────────────────────────────────────────────
        st.markdown("<div class='sidebar-label'><span style='color:#f0c040'>●</span> DR / ETF</div>",unsafe_allow_html=True)
        dr_sel=st.multiselect("DR tickers",DR_TICKERS,placeholder="Pick DR / ETF…",key="dr_ms",label_visibility="collapsed")

        selected_base=set_sel+mai_sel+dr_sel; selected=[to_yf(t) for t in selected_base]

        # ── Selection summary pill ───────────────────────────────────────────────
        if selected_base:
            names_preview=", ".join(selected_base[:6])+("…" if len(selected_base)>6 else "")
            st.markdown(f"<div style='background:#080f1e;border:1px solid #1a2e48;border-radius:6px;"
                        f"padding:8px 12px;margin-top:4px'>"
                        f"<span style='color:#4ecca3;font-weight:700'>{len(selected_base)} selected</span>"
                        f"<span style='color:#2a4060;font-size:11px'> · {names_preview}</span></div>",unsafe_allow_html=True)

        st.markdown("<hr>",unsafe_allow_html=True)
        # Two buttons: Clear Selection + Refresh Data
        bc1,bc2=st.columns(2)
        with bc1:
            if st.button("🗑 Clear Selection",use_container_width=True,help="Reset all stock picks"):
                for k in ['set_ms','mai_ms','dr_ms','sb_sec','mai_sec']:
                    if k in st.session_state: del st.session_state[k]
                st.rerun()
        with bc2:
            if st.button("🔄 Refresh",use_container_width=True,help="Force-reload from Yahoo Finance"):
                st.cache_data.clear(); st.rerun()

    TABS=["🔍 Screener","📈 Price","📋 Financials","📊 Fundamentals","⚖️ VI Score","📰 News"]
    tabs=st.tabs(TABS)
    def _need_selection():
        st.markdown("<div style='background:#080e1c;border:1px dashed #1a2e48;border-radius:10px;padding:100px;text-align:center;margin-top:20px'>"
                    "<div style='font-size:36px'>←</div><div style='color:#00c8f8;font-size:16px;margin:10px 0 6px;font-weight:600'>Pick a stock in the sidebar</div>"
                    "<div style='color:#2a4060;font-size:13px'>Use the sector icons → stock list on the left</div></div>",unsafe_allow_html=True)

    with tabs[0]: show_screener_tab()

    # ── Price tab ──────────────────────────────────────────────────────────────
    with tabs[1]:
        if not selected: _need_selection()
        else:
            for ticker in selected:
                with st.spinner(f"Loading {ticker}…"):
                    html_chart, chart_h = make_tv_chart(ticker)
                    _components.html(html_chart, height=chart_h, scrolling=False)

    # ── Financials tab ─────────────────────────────────────────────────────────
    with tabs[2]:
        if not selected: _need_selection()
        else:
            for ticker in selected:
                base=ticker.replace('.BK',''); name=TICKER_NAMES.get(base,"")
                sg,prof=get_sector_profile(base); sc=prof.get('color','#80cbc4')
                st.markdown(f"<div style='display:flex;align-items:center;gap:12px;margin:12px 0 8px'>"
                            f"<span style='color:#00c8f8;font-size:18px;font-weight:700'>{base}</span>"
                            f"<span style='color:#3a5070;font-size:14px'>{name}</span>"
                            f"<span style='background:rgba(0,0,0,0.3);border:1px solid {sc};border-radius:10px;"
                            f"padding:2px 9px;color:{sc};font-size:11px;font-weight:700'>{prof['label']}</span></div>",
                            unsafe_allow_html=True)
                d=fetch_all(ticker)
                # Sector note inline (no st.info which renders as [...])
                if sg in ('bank','finance'):
                    st.markdown(
                        f"<div style='background:#0a1628;border-left:3px solid {sc};"
                        f"border-radius:0 6px 6px 0;padding:8px 14px;margin-bottom:12px;"
                        f"color:#7a9ab8;font-size:12px'>"
                        f"<span style='color:{sc};font-weight:700'>ℹ {prof["label"]} note: </span>"
                        f"{prof['note']}</div>",
                        unsafe_allow_html=True)
                for title,df in [("📈 Income Statement",d['income']),
                                  ("⚖️ Balance Sheet",d['balance']),
                                  ("💵 Cash Flow Statement",d['cashflow'])]:
                    st.markdown(_df_to_html(df,title),unsafe_allow_html=True)
                st.markdown("<hr>",unsafe_allow_html=True)

    with tabs[3]:
        if not selected: _need_selection()
        else:
            for ticker in selected:
                with st.spinner(f"Plotting {ticker}…"): fig=make_fundamental_chart(ticker); st.pyplot(fig,use_container_width=True); plt.close(fig)

    with tabs[4]:
        if not selected: _need_selection()
        else:
            for ticker in selected:
                with st.spinner(f"Scoring {ticker}…"): render_vi_scorecard_st(compute_vi_scorecard(ticker))
                st.markdown("<hr>",unsafe_allow_html=True)

    with tabs[5]:
        if not selected: _need_selection()
        else:
            for ticker in selected:
                with st.spinner(f"Scanning news for {ticker}…"): render_news_st(ticker,fetch_all_news(ticker))
                st.markdown("<hr>",unsafe_allow_html=True)

try:
    main()
except Exception as _e:
    import traceback as _tb
    st.error(f'App error: {_e}')
    st.code(_tb.format_exc())
