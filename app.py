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
/* ══════════════════════════════════════════════════════
   DESIGN SYSTEM — One accent, two greys, semantic colors
   ══════════════════════════════════════════════════════ */
:root {
  /* Backgrounds — dark slate (not pure black, easier on eyes) */
  --bg:    #0d1117;
  --bg2:   #161b22;
  --bg3:   #1f2937;
  --bg4:   #252d3a;

  /* Borders */
  --line:  #21262d;
  --line2: #30363d;

  /* Text — three weights */
  --t1: #e6edf3;   /* primary */
  --t2: #8b949e;   /* secondary */
  --t3: #484f58;   /* muted */

  /* Single UI accent */
  --acc: #2f81f7;

  /* Semantic data colors — ONLY for data, never UI chrome */
  --pos: #3fb950;
  --neg: #f85149;
  --wrn: #d29922;

  --r: 6px;  /* border-radius */
}

/* ══════════════════════════════════════════════════════
   BASE
   ══════════════════════════════════════════════════════ */
html, body, .stApp {
  background: var(--bg) !important;
  color: var(--t1) !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif !important;
  font-size: 14px !important;
  line-height: 1.5 !important;
}
.block-container {
  padding: 12px 28px 40px !important;
  max-width: 1360px !important;
}
#MainMenu, footer, [data-testid="stStatusWidget"], [data-testid="stDecoration"] {
  display: none !important;
}

/* Scrollbars */
* { scrollbar-width: thin; scrollbar-color: var(--line2) transparent; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--line2); border-radius: 3px; }

/* ══════════════════════════════════════════════════════
   SIDEBAR
   ══════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--line) !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
  color: var(--t2) !important;
  font-size: 13px !important;
}
header[data-testid="stHeader"] {
  background: transparent !important;
  border-bottom: none !important;
}

/* Sidebar collapse toggle */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
  position: fixed !important; left: 0 !important; top: 50% !important;
  transform: translateY(-50%) !important; z-index: 99999 !important;
  display: flex !important; visibility: visible !important; opacity: 1 !important;
  background: var(--bg2) !important; border: 1px solid var(--line2) !important;
  border-left: none !important; border-radius: 0 4px 4px 0 !important;
  padding: 8px 5px !important; cursor: pointer !important;
}
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg { fill: var(--t2) !important; }

/* Sidebar captions used as section labels */
section[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] p {
  font-size: 10px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 1px !important;
  color: var(--t3) !important;
  margin: 8px 0 4px !important;
}
.sidebar-label {
  color: var(--t3) !important;
  font-size: 10px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 1px !important;
  margin: 8px 0 4px !important;
  display: block !important;
}

/* Sidebar sector grid buttons */
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] { gap:3px!important; margin-bottom:2px!important; }
section[data-testid="stSidebar"] div[data-testid="stButton"] { margin:0!important; padding:0!important; }
section[data-testid="stSidebar"] div[data-testid="stButton"] button {
  width:100%!important; height:28px!important; min-height:28px!important;
  padding:0 3px!important; border-radius:4px!important;
  font-size:11.5px!important; font-weight:500!important;
  background:transparent!important; border:1px solid var(--line)!important; color:var(--t2)!important;
  transition:all 0.1s!important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
  background:var(--bg3)!important; border-color:var(--line2)!important; color:var(--t1)!important;
}
/* Active = primary type — accent fill */
section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {
  background:rgba(47,129,247,0.15)!important; border-color:var(--acc)!important; color:var(--acc)!important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] button p,
section[data-testid="stSidebar"] div[data-testid="stButton"] button div {
  white-space:nowrap!important; overflow:hidden!important; text-overflow:ellipsis!important;
  font-size:11.5px!important; line-height:1.2!important; font-weight:500!important;
  margin:0!important; padding:0!important;
}

/* ══════════════════════════════════════════════════════
   TAB BAR — sticky inside its scroll container
   ══════════════════════════════════════════════════════ */

/* Sidebar must scroll freely */
section[data-testid="stSidebar"] > div {
  overflow-y: auto !important;
  overflow-x: hidden !important;
}

/* Tab bar — sticky inside the main content area */
.stTabs [data-baseweb="tab-list"] {
  position: sticky !important;
  top: 0 !important;
  z-index: 999 !important;
  background: var(--bg) !important;
  border-bottom: 1px solid var(--line) !important;
  box-shadow: 0 2px 6px rgba(0,0,0,0.5) !important;
  gap: 0 !important;
  padding: 0 !important;
  margin-left: -28px !important;
  margin-right: -28px !important;
  padding-left: 28px !important;
  padding-right: 28px !important;
}

/* Large click targets */
.stTabs [data-baseweb="tab"] {
  color: var(--t2) !important;
  font-size: 14px !important; font-weight: 500 !important;
  padding: 14px 28px !important;  /* big click zone */
  background: transparent !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
  margin: 0 !important;
  cursor: pointer !important;
  transition: color 0.1s !important;
  user-select: none !important;
  min-width: 80px !important;
  text-align: center !important;
}
.stTabs [data-baseweb="tab"] p,
.stTabs [data-baseweb="tab"] span,
.stTabs [data-baseweb="tab"] div { color: inherit !important; font-size: 14px !important; }
.stTabs [data-baseweb="tab"]:hover { color: var(--t1) !important; background: transparent !important; }
.stTabs [aria-selected="true"],
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span,
.stTabs [aria-selected="true"] div {
  color: var(--t1) !important;
  font-weight: 600 !important;
  background: transparent !important;
  border-bottom: 2px solid var(--acc) !important;
}

/* ══════════════════════════════════════════════════════
   BUTTONS — main content
   ══════════════════════════════════════════════════════ */
.stButton > button {
  background: var(--bg3) !important;
  color: var(--t2) !important;
  border: 1px solid var(--line2) !important;
  border-radius: var(--r) !important;
  font-size: 13px !important; font-weight: 500 !important;
  padding: 7px 16px !important;
  transition: all 0.1s ease !important;
}
.stButton > button:hover {
  background: var(--bg4) !important;
  border-color: var(--t3) !important;
  color: var(--t1) !important;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
  background: var(--acc) !important;
  border-color: var(--acc) !important;
  color: #fff !important; font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover { filter: brightness(1.1) !important; }

/* ══════════════════════════════════════════════════════
   INPUTS
   ══════════════════════════════════════════════════════ */
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stTextInput > div > div,
.stNumberInput > div > div {
  background: var(--bg2) !important;
  border: 1px solid var(--line2) !important;
  color: var(--t1) !important;
  border-radius: var(--r) !important;
  font-size: 13px !important;
}
span[data-baseweb="tag"] {
  background: rgba(47,129,247,0.12) !important;
  border: 1px solid rgba(47,129,247,0.3) !important;
  color: var(--acc) !important; border-radius: 4px !important;
}
[data-baseweb="popover"] ul {
  background: var(--bg2) !important;
  border: 1px solid var(--line2) !important;
}
[data-baseweb="popover"] li {
  color: var(--t1) !important; font-size: 13px !important;
}
[data-baseweb="popover"] li:hover { background: var(--bg3) !important; }

/* ══════════════════════════════════════════════════════
   MISC
   ══════════════════════════════════════════════════════ */
h1, h2, h3 {
  color: var(--t1) !important;
  font-weight: 600 !important;
  letter-spacing: -0.3px !important;
}
hr {
  border: none !important;
  border-top: 1px solid var(--line) !important;
  margin: 10px 0 !important;
}
.stProgress > div > div > div { background: var(--acc) !important; }
div[data-testid="metric-container"] {
  background: var(--bg2) !important;
  border: 1px solid var(--line) !important;
  border-radius: var(--r) !important;
}
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
    # Vietnam ETFs (SET-listed DRs)
    "E1VFVN3001","FUEVFVND01","FUEVN100",
    # China/HK DRs
    "BABA80","TENCENT80","XIAOMI80","BYDCOM80",
    # US-linked DRs / ETFs
    "NDX01","AAPL80X","TSLA80X","STAR5001",
]
SECTOR_MAP = {
    "Banking":      ["BBL","KBANK","KTB","SCB","KKP","TISCO","TTB","TCAP"],
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
    # MAI-specific sectors
    "Media":    ("","Media"),
    "Other":    ("","Other"),
    "Tech":     ("","Tech"),
    "Finance":  ("","Finance"),
    "Property": ("","Property"),
    "Energy":   ("","Energy"),
    "Healthcare":("","Health"),
    "Commerce": ("","Commerce"),
    "Food":     ("","Food"),
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

    # ══════════════════════════════════════════════════════════════════════
    # BANKS — Thai commercial & specialized banks
    # Business model: take deposits (liabilities), lend at spread (assets).
    # D/E 8-15× is NORMAL and regulatory requirement, not a risk.
    # Revenue = net interest income + fee income. Gross margin concept N/A.
    # Key value driver: ROE, NIM, NPL, loan growth. Most not in yfinance.
    # Valuation: P/B is primary anchor. P/E meaningful only vs peers.
    # ══════════════════════════════════════════════════════════════════════
    'bank': {
        'label': 'Bank', 'color': '#4fc3f7',
        'note': 'D/E 8–15× is normal (deposits = liabilities). ROE >10% is solid for Thai banks. Cross-check NPL, CAR, NIM in BOT filings.',
        'rev_cagr_min':    5,     # Net interest income growth target
        'gross_margin_min': None, # N/A — no COGS vs revenue split for banks
        'net_margin_min':  15,    # Banks should earn 15-25% net margin on revenue
        'roe_min':         10,    # Thai banks: 8-14% ROE is normal
        'de_max':          None,  # SKIP — structural leverage, not a credit risk
        'cr_min':          None,  # SKIP — ALM framework, not working capital
        'ic_min':          None,  # SKIP — banks earn interest, IC not applicable
        'div_yield_min':   2.5,   # Thai major banks: 3-6% typical
        'pe_max':          12,    # Banks trade 6-12× — above 14× is expensive
        'pb_max':          1.5,   # Book value = loan book; >1.5× needs strong ROE
        'fcf_mode':        'ocf_positive',
        'phantom_mode':    'ni_trend',
    },

    # ══════════════════════════════════════════════════════════════════════
    # CONSUMER FINANCE / LEASING / MICROFINANCE
    # Model: borrow wholesale (bonds/bank lines), lend retail at higher rate.
    # D/E 3-8× is their natural leverage (lending IS the product).
    # Revenue = interest income. High ROE expected from leverage.
    # Key risk: NPL ratio (not in yfinance), cost of funds, credit cycle.
    # ══════════════════════════════════════════════════════════════════════
    'finance': {
        'label': 'Finance/Leasing', 'color': '#ce93d8',
        'note': 'Borrowing to lend at spread — D/E 3-8× is healthy. High ROE from leverage. Watch NPL and cost-of-funds in filings.',
        'rev_cagr_min':    8,     # Loan book should grow faster than GDP
        'gross_margin_min': None, # N/A — interest spread, not a COGS business
        'net_margin_min':  18,    # Finance cos run 15-35% net margin
        'roe_min':         15,    # Leverage amplifies returns; 15%+ expected
        'de_max':          8.0,   # >8× starts becoming risky
        'cr_min':          None,  # Funded by bonds, not short-term payables
        'ic_min':          2.0,   # Should cover interest at minimum 2×
        'div_yield_min':   2.0,
        'pe_max':          18,    # Finance cos: 8-18× P/E range
        'pb_max':          3.0,   # Book value matters; >3× needs premium growth
        'fcf_mode':        'ocf_positive',
        'phantom_mode':    'ni_trend',
    },

    # ══════════════════════════════════════════════════════════════════════
    # PROPERTY DEVELOPERS (residential, industrial estate, commercial)
    # Revenue is lumpy — projects take 2-4 years from sale to delivery.
    # Working capital is huge (land bank, construction WIP).
    # D/E 1-1.5× standard; REITs have different structure.
    # Gross margin 25-45% depending on project mix and location.
    # Key VI metric: backlog/presales (not in yfinance — check filings).
    # ══════════════════════════════════════════════════════════════════════
    'property': {
        'label': 'Property', 'color': '#ffb74d',
        'note': 'Project-lumpy revenue (2-4yr cycles). Gross margin 25-40%. FCF negative during land build-up is normal. Check presales backlog.',
        'rev_cagr_min':    4,     # Residential growth tracks economy; 4-6% decent
        'gross_margin_min': 25,   # Good Thai developer: 28-40%; <25% margin erosion
        'net_margin_min':  7,     # After interest on project debt: 7-15%
        'roe_min':         10,    # Capital-heavy: 10-18% is healthy
        'de_max':          1.5,   # >1.5× starts pressuring coverage
        'cr_min':          1.5,   # Need buffer for construction draws
        'ic_min':          3.0,   # Interest coverage: project debt is cheap but large
        'div_yield_min':   2.5,   # Property cos should distribute when projects complete
        'pe_max':          15,    # Thai property trades 8-15×; above is rich
        'pb_max':          2.0,   # Landbank at cost; 1.5-2× is fair
        'fcf_mode':        'avg_3y',
        'phantom_mode':    'standard',
    },

    # ══════════════════════════════════════════════════════════════════════
    # UPSTREAM ENERGY (oil/gas E&P, coal mining)
    # PTT, PTTEP, BANPU — commodity price takers, not margin controllers.
    # Revenue and margins swing violently with commodity cycles.
    # D/E 0.5-1.5× normal; capex is huge for resource development.
    # FCF highly cyclical — evaluate on normalized 3-5Y basis.
    # Dividend varies with oil price; reserve replacement rate is key.
    # ══════════════════════════════════════════════════════════════════════
    'energy_upstream': {
        'label': 'Energy (E&P/Mining)', 'color': '#ef9a9a',
        'note': 'Commodity price taker — margins and FCF are cyclical. Gross margin 20-50% depends on oil/coal prices. Evaluate on 5Y normalized basis.',
        'rev_cagr_min':    3,     # Commodity growth slow; 3% real is fine
        'gross_margin_min': 20,   # In trough: 15-25%; at peak: 40-55%
        'net_margin_min':  5,     # Cyclical: accept low margins in trough
        'roe_min':         8,     # Cyclical: 8% trough ROE, 20%+ at peak
        'de_max':          1.5,   # E&P debt manageable at <1.5×
        'cr_min':          1.0,   # Minimum liquidity buffer
        'ic_min':          3.0,   # Should cover interest 3× at trough pricing
        'div_yield_min':   3.0,   # Commodity cos pay special dividends at peak
        'pe_max':          15,    # Normalized P/E 8-15× (peak P/E misleadingly low)
        'pb_max':          2.5,   # Asset-heavy; 1-2.5× is normal range
        'fcf_mode':        'avg_3y',
        'phantom_mode':    'standard',
    },

    # ══════════════════════════════════════════════════════════════════════
    # DOWNSTREAM / REFINING / PETROCHEMICALS
    # PTTGC, TOP, IRPC, SPRC, IVL — thin crack-spread businesses.
    # Gross margin 5-15% is NORMAL for refining — not a moat problem.
    # High revenue, low margin. Cyclical with refining spreads.
    # Capital intensive. D/E 0.5-2× depending on refinery age/size.
    # ══════════════════════════════════════════════════════════════════════
    'energy_refining': {
        'label': 'Refining/Petrochem', 'color': '#a5d6a7',
        'note': 'Crack-spread business — gross margin 5-15% is NORMAL (not a weakness). Revenue is huge, margins thin. Evaluate on through-cycle D/E and OCF.',
        'rev_cagr_min':    3,
        'gross_margin_min': 5,    # Refining crack spread: 5-15% is healthy
        'net_margin_min':  2,     # Net after D&A, interest: 2-8%
        'roe_min':         6,     # Through-cycle: 6-12%
        'de_max':          2.0,   # Refineries are asset-heavy
        'cr_min':          1.0,
        'ic_min':          2.5,
        'div_yield_min':   2.0,
        'pe_max':          12,    # Refining trades cheap on low margin
        'pb_max':          2.0,
        'fcf_mode':        'avg_3y',
        'phantom_mode':    'standard',
    },

    # ══════════════════════════════════════════════════════════════════════
    # POWER GENERATION / UTILITIES / RENEWABLES
    # BGRIM, EA, EGCO, GULF, GPSC, GUNKUL, CKP, RATCH, BCPG, BBGI, SSP
    # Contracted revenue (PPA), very stable. Capital is project-finance debt.
    # D/E 2-4× is STANDARD for power plant SPVs (30-year bonds vs 25-year assets).
    # High gross margin (60-80%) but huge D&A eats into net margin.
    # Dividend yield is primary return; treat like bond-equity hybrid.
    # ══════════════════════════════════════════════════════════════════════
    'power': {
        'label': 'Power/Utilities', 'color': '#aed581',
        'note': 'PPA-contracted revenue = bond-like stability. D/E 2-4× is normal (project finance). High gross margin but D&A is large. Value via dividend yield + EV/EBITDA.',
        'rev_cagr_min':    5,     # COD (commercial operation date) drives growth
        'gross_margin_min': 30,   # Power gross margin: 30-70% depending on fuel
        'net_margin_min':  8,     # After heavy D&A and project interest: 8-20%
        'roe_min':         8,     # Leverage amplifies; but contracted = lower risk
        'de_max':          4.0,   # Project finance: 3-4× is normal
        'cr_min':          1.0,   # Cash flow timing by PPA schedule
        'ic_min':          2.5,   # Must cover project debt interest
        'div_yield_min':   3.5,   # Utilities should yield 3-6%
        'pe_max':          20,    # Regulated returns: trade at premium P/E
        'pb_max':          3.0,   # Asset base valued at replacement cost
        'fcf_mode':        'avg_3y',
        'phantom_mode':    'standard',
    },

    # ══════════════════════════════════════════════════════════════════════
    # HEALTHCARE (hospitals, pharma, medical devices)
    # BDMS, BH, BCH, CHG, BCH, PR9 — recession-resistant, pricing power.
    # High gross margin (50-70%). Premium P/E justified by stability.
    # Low D/E (hospitals fund capex from operations).
    # ROE may appear modest due to conservative asset valuation.
    # ══════════════════════════════════════════════════════════════════════
    'healthcare': {
        'label': 'Healthcare', 'color': '#f48fb1',
        'note': 'Recession-resistant, high gross margin (50-70%). Premium P/E justified. Watch bed utilization rate and ARPU trends in filings.',
        'rev_cagr_min':    8,     # Medical tourism + aging population driver
        'gross_margin_min': 35,   # Hospital gross margin after direct costs: 35-60%
        'net_margin_min':  10,    # After SGA, D&A: 10-20%
        'roe_min':         12,    # Good hospitals: 12-25% ROE
        'de_max':          0.8,   # Conservative; hospitals avoid heavy leverage
        'cr_min':          1.5,
        'ic_min':          5.0,   # Should have headroom; healthcare is defensive
        'div_yield_min':   1.5,   # Healthcare reinvests; yield can be lower
        'pe_max':          30,    # Premium sector: 20-35× is normal
        'pb_max':          4.0,   # Intangibles (reputation, licenses) not on balance sheet
        'fcf_mode':        'all_positive',
        'phantom_mode':    'standard',
    },

    # ══════════════════════════════════════════════════════════════════════
    # FOOD & BEVERAGE (producers, processors, distributors)
    # CPF, TU, BTG, SAPPE, CBG, ICHI, OSP — commodity input costs vary.
    # Gross margin 20-50% depending on value-added vs commodity processing.
    # CPF (integrated poultry/aqua): 10-20% gross margin normal.
    # Premium brands (SAPPE, CBG): 40-60% gross margin.
    # ══════════════════════════════════════════════════════════════════════
    'food': {
        'label': 'Food & Beverage', 'color': '#ffcc80',
        'note': 'Wide range: commodity processors (10-20% gross margin) vs branded (40-60%). Separate integrated producers like CPF from premium brands.',
        'rev_cagr_min':    5,
        'gross_margin_min': 12,   # Commodity food: 10-20%; branded: 35-55%
        'net_margin_min':  4,     # Commodity: 3-7%; branded: 10-18%
        'roe_min':         10,
        'de_max':          1.0,
        'cr_min':          1.3,
        'ic_min':          4.0,
        'div_yield_min':   1.5,
        'pe_max':          20,
        'pb_max':          3.0,
        'fcf_mode':        'all_positive',
        'phantom_mode':    'standard',
    },

    # ══════════════════════════════════════════════════════════════════════
    # COMMERCE / RETAIL (convenience stores, home improvement, fashion)
    # CPALL, HMPRO, COM7, CRC, DOHOME, GLOBAL — thin margins, high volume.
    # CPALL (7-Eleven): gross margin ~25% but massive footprint.
    # Home improvement/electronics: 20-30% gross margin typical.
    # D/E can be moderate (lease liabilities inflate reported D/E).
    # ══════════════════════════════════════════════════════════════════════
    'commerce': {
        'label': 'Commerce/Retail', 'color': '#80cbc4',
        'note': 'Thin margins, high volume. Gross margin 15-30% for retail (not a red flag). IFRS16 lease liabilities inflate D/E — use EV/EBITDA. Check SSS growth.',
        'rev_cagr_min':    6,
        'gross_margin_min': 15,   # Convenience/retail: 15-30%
        'net_margin_min':  3,     # After rents, staff: 3-8%
        'roe_min':         12,    # Retail leverage amplifies ROE; 12%+ acceptable
        'de_max':          2.5,   # IFRS16 inflates; adjust for lease liabilities
        'cr_min':          1.0,   # Retail typically runs tight working capital
        'ic_min':          3.0,
        'div_yield_min':   1.5,
        'pe_max':          25,    # Defensive retail can trade at premium
        'pb_max':          4.0,   # Brand + store network not fully on balance sheet
        'fcf_mode':        'all_positive',
        'phantom_mode':    'standard',
    },

    # ══════════════════════════════════════════════════════════════════════
    # TECHNOLOGY / TELECOM / MEDIA
    # ADVANC, TRUE, DELTA, KCE, HANA — range from asset-light (telecom services)
    # to capital-heavy (semiconductor/electronics manufacturing).
    # ADVANC/TRUE: 30-50% gross margin; high D/E from spectrum investment.
    # DELTA/HANA: electronics manufacturing, 15-25% gross margin.
    # ══════════════════════════════════════════════════════════════════════
    'tech': {
        'label': 'Tech/Telecom', 'color': '#82b1ff',
        'note': 'Wide range: telecom (30-50% GM, high D/E for spectrum) vs electronics mfg (15-25% GM). High growth tech can trade at premium P/E.',
        'rev_cagr_min':    8,
        'gross_margin_min': 15,   # Electronics mfg: 15-25%; software/telecom: 35-60%
        'net_margin_min':  6,     # Telecom after D&A: 6-18%; software: 15-30%
        'roe_min':         12,
        'de_max':          2.0,   # Telecom spectrum/tower debt accepted
        'cr_min':          1.2,
        'ic_min':          3.5,
        'div_yield_min':   1.0,   # Growth tech reinvests; low yield acceptable
        'pe_max':          30,    # Growth premium: 15-40× depending on growth rate
        'pb_max':          5.0,   # Intangibles (software, spectrum) understated
        'fcf_mode':        'all_positive',
        'phantom_mode':    'standard',
    },

    # ══════════════════════════════════════════════════════════════════════
    # INDUSTRIAL / MATERIALS / TRANSPORT / LOGISTICS
    # SCC, SCGP, IVL, BTS, BEM, AOT, RCL — capital-intensive cyclicals.
    # SCC cement: 25-35% gross margin. IVL PET resin: 8-15%.
    # Transport (BTS, BEM): regulated, high gross margin but D/E elevated.
    # AOT: near-monopoly airport; exceptional margin and pricing power.
    # ══════════════════════════════════════════════════════════════════════
    'industrial': {
        'label': 'Industrial/Transport', 'color': '#b0bec5',
        'note': 'Wide range: cement (25-35% GM), packaging (20-30%), PET resin (8-15%), transport (40-60% GM). D/E varies by asset intensity.',
        'rev_cagr_min':    5,
        'gross_margin_min': 10,   # Materials: 8-35% depending on product
        'net_margin_min':  4,     # After heavy D&A: 4-15%
        'roe_min':         8,
        'de_max':          1.5,
        'cr_min':          1.2,
        'ic_min':          4.0,
        'div_yield_min':   2.0,
        'pe_max':          18,
        'pb_max':          2.5,
        'fcf_mode':        'avg_3y',
        'phantom_mode':    'standard',
    },

    # ══════════════════════════════════════════════════════════════════════
    # GENERAL FALLBACK — consumer staples, services, conglomerates
    # For tickers not mapped to a specific sector above.
    # ══════════════════════════════════════════════════════════════════════
    'general': {
        'label': 'General', 'color': '#90caf9',
        'note': 'General thresholds. If this stock has special sector characteristics, consider thresholds indicative only.',
        'rev_cagr_min':    6,
        'gross_margin_min': 20,
        'net_margin_min':  6,
        'roe_min':         12,
        'de_max':          1.0,
        'cr_min':          1.3,
        'ic_min':          4.0,
        'div_yield_min':   1.5,
        'pe_max':          20,
        'pb_max':          3.0,
        'fcf_mode':        'all_positive',
        'phantom_mode':    'standard',
    },
}

# ── Ticker → sector group mapping ──────────────────────────────────────────────
_TICKER_TO_GROUP = {}
for _g, _tickers in [
    ('bank',     ['BBL','KBANK','KTB','SCB','BAY','KKP','TISCO','TTB','TCAP']),
    ('finance',  ['KTC','MTC','TIDLOR','SAWAD','AEONTS','BAM','JMT','ASK','THRE','BLA','TLI']),
    ('property', ['LH','CPN','SIRI','SPALI','WHA','AWC','AP','QH','AMATA','ROJNA',
                  'A5','CHEWA','MORE','SCGD','ROJNA']),
    ('energy_upstream',  ['PTT','PTTEP','BANPU','SKR']),
    ('energy_refining',  ['PTTGC','TOP','IRPC','SPRC','BCP','OR','IVL','TASCO']),
    ('power',    ['BGRIM','EA','EGCO','GULF','GPSC','GUNKUL','CKP','RATCH','BCPG',
                  'BBGI','EPG','SSP','TPCH']),
    ('healthcare',['BDMS','BH','BCH','CHG','PR9','SPA','VIH','MEGA']),
    ('food',     ['CPF','TU','BTG','CBG','ICHI','SAPPE','SNNP','COCOCO','OSP','ITC',
                  'PM','RBF','STA','STGT']),
    ('commerce', ['CPALL','HMPRO','COM7','CRC','DOHOME','GLOBAL','BJC','MBK',
                  'MASTER','KAMART','MOSHI']),
    ('tech',     ['ADVANC','TRUE','JAS','DELTA','KCE','HANA','CCET','SKY','SISB',
                  'ADVICE','DITTO','FORTH','MFEC','NETBAY','NEO']),
    ('industrial',['SCC','SCGP','BTS','BEM','AOT','RCL','PRM','SJWD','AAV','BA',
                   'TISCO','IVL','AMATA','WHA','SMPC']),
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
# ── Price cache: short TTL so chart stays current (5 min) ────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_price(ticker):
    """Fetch latest OHLCV — short cache so price is near real-time."""
    import time
    for attempt in range(3):
        try:
            tk = yf.Ticker(ticker)
            # Request end = tomorrow so today's bar is always included
            end = pd.Timestamp.now(tz='UTC') + pd.Timedelta(days=1)
            start = end - pd.DateOffset(years=10)
            px = tk.history(
                interval='1d', start=start, end=end,
                auto_adjust=True, actions=True,
                timeout=20, raise_errors=False
            )
            if px is not None and not px.empty:
                px.index = strip_tz(px.index)
                return px
            # Fallback: use period parameter
            px2 = tk.history(period='10y', interval='1d',
                             auto_adjust=True, timeout=20)
            if px2 is not None and not px2.empty:
                px2.index = strip_tz(px2.index)
                return px2
        except Exception:
            if attempt < 2: time.sleep(1.5 ** attempt)
    return pd.DataFrame()

# ── Fundamentals cache: long TTL (financials update quarterly) ────────────────
@st.cache_data(ttl=21600, show_spinner=False)
def fetch_fundamentals(ticker):
    """Fetch financials, info, dividends — cached 6h (quarterly data)."""
    import time
    data = dict(ticker=ticker, info={}, income=pd.DataFrame(),
                balance=pd.DataFrame(), cashflow=pd.DataFrame(),
                divs=pd.Series(dtype=float))
    for attempt in range(3):
        try:
            tk = yf.Ticker(ticker)
            try:
                info = tk.info or {}
                data['info'] = info if isinstance(info, dict) else {}
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
            break
        except Exception:
            if attempt < 2: time.sleep(2 ** attempt)
    return data

def fetch_all(ticker):
    """Combine short-TTL price with long-TTL fundamentals."""
    price = fetch_price(ticker)
    fund  = fetch_fundamentals(ticker)
    return dict(ticker=ticker, price=price, **fund)


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
    # P/BV — resample to W and M to match interval
    def resample_pbv(pbv_s, rule):
        if pbv_s.empty: return pbv_s
        try: return pbv_s.resample(rule).last().dropna()
        except: return pbv_s
    pbv_w = resample_pbv(pbv_series, 'W-FRI')
    pbv_m = resample_pbv(pbv_series, 'ME')
    d_pbv = json.dumps(series(pbv_series))
    w_pbv = json.dumps(series(pbv_w))
    m_pbv = json.dumps(series(pbv_m))

    # ── Header stats (full history) ────────────────────────────────────────────
    ep   = float(close_d.iloc[-1])
    fmax = (ep - float(close_d.max())) / float(close_d.max()) * 100
    fmin = (ep - float(close_d.min())) / float(close_d.min()) * 100
    dy   = trailing_div_yield(d['divs'], d['price'])
    dy_txt = f" · Div {dy:.2f}%" if dy else ""
    base  = ticker.replace('.BK', '') if ticker.endswith('.BK') else ticker
    has_pbv = len(pbv_series) > 0
    pbv_h   = 110 if has_pbv else 0
    title   = f"{base} · {ep:.2f} THB · ▼ from MAX {fmax:.1f}% · ▲ from MIN +{fmin:.1f}%{dy_txt}"

    PH, RH, VH, BH = 400, 130, 100, pbv_h
    total_h = PH + RH + VH + BH + 82  # 82 = header+legend+toolbar
    # Use JS to resize chart to full viewport on load

    html = f"""<!DOCTYPE html><html>
<head>
<meta charset="utf-8">
<script src="https://unpkg.com/lightweight-charts@4.1.3/dist/lightweight-charts.standalone.production.js"></script>
<style>
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ background:#0b1120; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; overflow:hidden; user-select:none; }}
#hdr  {{ padding:7px 14px 3px; color:#dce9ff; font-size:12.5px; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
#stats {{ padding:0 14px 4px; font-size:11px; color:#4a6480; min-height:18px; }}
#ohlc  {{ display:inline; }}
#pct   {{ display:inline; margin-left:10px; }}
#chart {{ width:100%; }}
.toolbar {{ display:flex; gap:3px; padding:5px 10px; background:#080e1c;
            border-top:1px solid #0e1a2e; flex-wrap:nowrap; align-items:center; }}
.pb {{ background:#111a2e; border:1px solid #1e3358; color:#5a7090;
       padding:3px 9px; border-radius:4px; cursor:pointer;
       font-size:11px; font-weight:600; white-space:nowrap; }}
.pb:hover {{ background:#0d1e38; border-color:#00c8f8; color:#c8e8ff; }}
.pb.active {{ background:#0a1e38; border-color:#00c8f8; color:#00c8f8; }}
.sep {{ width:1px; height:16px; background:#1e3358; margin:0 3px; }}
</style>
</head>
<body>
<div id="hdr">{title}</div>
<div id="stats"><span id="ohlc"></span><span id="pct"></span></div>
<div id="chart"></div>
<div class="toolbar">
  <button class="pb" onclick="setRange(90)">3M</button>
  <button class="pb" onclick="setRange(180)">6M</button>
  <button class="pb active" onclick="setRange(365)">1Y</button>
  <button class="pb" onclick="setRange(730)">2Y</button>
  <button class="pb" onclick="setRange(1825)">5Y</button>
  <button class="pb" onclick="setRange(99999)">Max</button>
  <div class="sep"></div>
  <button class="pb active" id="ibD" onclick="setIv('D')">D</button>
  <button class="pb" id="ibW" onclick="setIv('W')">W</button>
  <button class="pb" id="ibM" onclick="setIv('M')">M</button>
  <div class="sep"></div>
  <button class="pb" id="btn_type" onclick="toggleType()">Line</button>
  <button class="pb" id="btn_log"  onclick="toggleLog()">Log</button>
  <button class="pb" onclick="chart.timeScale().fitContent()">⟳</button>
</div>

<script>
const C = {{ bg:'#0b1120', grid:'#0f1c2e', up:'#22d68a', dn:'#ff5566',
             e25:'#ff69b4', e75:'#00e676', e200:'#666',
             rsi:'#a0b8d0', rsiOB:'#ef5350', rsiOS:'#26c6da',
             pbv:'#f5c842', txt:'#8ba8cc', cross:'#2a4060' }};

const DATA = {{
  D: {{ candle:{d_candle}, line:{d_line}, e25:{d_e25}, e75:{d_e75}, e200:{d_e200}, rsi:{d_rsi}, vol:{d_vol}, pbv:{d_pbv} }},
  W: {{ candle:{w_candle}, line:{w_line}, e25:{w_e25}, e75:{w_e75}, e200:{w_e200}, rsi:{w_rsi}, vol:{w_vol}, pbv:{w_pbv} }},
  M: {{ candle:{m_candle}, line:{m_line}, e25:{m_e25}, e75:{m_e75}, e200:{m_e200}, rsi:{m_rsi}, vol:{m_vol}, pbv:{m_pbv} }},
}};

let curIv = 'D', showCandle = true, logMode = false, curRange = 365;

// ── Total chart height covers all panes ────────────────────────────────────────
const W = Math.max(window.innerWidth, 400);
// Use full viewport height minus toolbar+header (~82px)
const AVAIL_H = Math.max(window.innerHeight - 82, {PH} + {RH} + {VH} + {BH});
const TOTAL_H = AVAIL_H;
document.getElementById('chart').style.height = TOTAL_H + 'px';

// ── Single chart with pane separation using price scales ──────────────────────
const chart = LightweightCharts.createChart(document.getElementById('chart'), {{
  width: W, height: TOTAL_H,
  layout: {{ background: {{color: C.bg}}, textColor: C.txt, fontSize: 11 }},
  grid: {{ vertLines: {{color: C.grid}}, horzLines: {{color: C.grid}} }},
  crosshair: {{
    mode: LightweightCharts.CrosshairMode.Normal,
    vertLine: {{ color: C.cross, labelBackgroundColor: '#1e3358' }},
    horzLine: {{ color: C.cross, labelBackgroundColor: '#1e3358' }},
  }},
  timeScale: {{ borderColor: C.grid, timeVisible: true, secondsVisible: false,
                rightOffset: 8, fixRightEdge: true }},
  rightPriceScale: {{ visible: true, borderColor: C.grid }},
  handleScroll: true, handleScale: true,
  kineticScroll: {{ mouse: true, touch: true }},
}});

// ── Price pane (main, default right scale) ────────────────────────────────────
const sCand = chart.addCandlestickSeries({{
  upColor: C.up, downColor: C.dn,
  borderUpColor: C.up, borderDownColor: C.dn,
  wickUpColor: C.up, wickDownColor: C.dn,
  priceScaleId: 'price',
}});
const sLine = chart.addLineSeries({{
  color: C.up, lineWidth: 2, visible: false, priceLineVisible: false,
  priceScaleId: 'price',
}});
const sE25 = chart.addLineSeries({{ color: C.e25, lineWidth: 1, priceLineVisible: false, lastValueVisible: true, title: 'EMA25', priceScaleId: 'price' }});
const sE75 = chart.addLineSeries({{ color: C.e75, lineWidth: 1, priceLineVisible: false, lastValueVisible: true, title: 'EMA75', priceScaleId: 'price' }});
const sE200= chart.addLineSeries({{ color: C.e200,lineWidth: 1, priceLineVisible: false, lastValueVisible: true, title: 'EMA200',priceScaleId: 'price' }});

// ── RSI pane (separate scale, positioned below price) ─────────────────────────
const sRsi = chart.addLineSeries({{
  color: C.rsi, lineWidth: 1.5, priceLineVisible: false, lastValueVisible: true,
  priceScaleId: 'rsi',
}});
[{{p:70,c:C.rsiOB,s:1}},{{p:50,c:'#222',s:2}},{{p:30,c:C.rsiOS,s:1}}].forEach(l =>
  sRsi.createPriceLine({{price:l.p, color:l.c, lineStyle:l.s, lineWidth:1, axisLabelVisible:true}}));

// ── Volume pane ────────────────────────────────────────────────────────────────
const sVol = chart.addHistogramSeries({{
  priceFormat: {{type: 'volume'}},
  priceScaleId: 'vol',
}});

// ── P/BV pane ─────────────────────────────────────────────────────────────────
let sPbv = null;
{'sPbv = chart.addLineSeries({ color: C.pbv, lineWidth: 1.5, priceLineVisible: false, lastValueVisible: true, title: "P/BV", priceScaleId: "pbv" }); [1,2,3].forEach(v => sPbv.createPriceLine({price:v, color:"#2a4060", lineStyle:2, lineWidth:1, axisLabelVisible:true}));' if has_pbv else '// no pbv data'}

// ── Configure price scale heights as fractions of total ───────────────────────
// Pane layout: price=top 55%, rsi=next 18%, vol=next 15%, pbv=bottom 12%
chart.priceScale('price').applyOptions({{
  scaleMargins: {{ top: 0.01, bottom: {'0.45' if has_pbv else '0.37'} }},
  borderColor: C.grid,
}});
chart.priceScale('rsi').applyOptions({{
  scaleMargins: {{ top: {'0.57' if has_pbv else '0.57'}, bottom: {'0.29' if has_pbv else '0.21'} }},
  borderColor: '#1a2a40',
}});
chart.priceScale('vol').applyOptions({{
  scaleMargins: {{ top: {'0.73' if has_pbv else '0.73'}, bottom: {'0.12' if has_pbv else '0.0'} }},
  borderColor: '#1a2a40',
}});
{'chart.priceScale("pbv").applyOptions({ scaleMargins: { top: 0.88, bottom: 0.0 }, borderColor: "#1a2a40" });' if has_pbv else ''}

// ── Separator lines between panes ─────────────────────────────────────────────
// Draw visual separators at pane boundaries using fake zero-width series
function addSeparator(psId, pos) {{
  const s = chart.addLineSeries({{ priceScaleId: psId, visible: false, priceLineVisible: false, lastValueVisible: false }});
  chart.priceScale(psId).applyOptions({{ borderVisible: true, borderColor: '#1a2a40' }});
}}

// ── Load data ─────────────────────────────────────────────────────────────────
function loadData(iv) {{
  const d = DATA[iv];
  sCand.setData(d.candle);
  sLine.setData(d.line);
  sE25.setData(d.e25); sE75.setData(d.e75); sE200.setData(d.e200);
  sRsi.setData(d.rsi);
  sVol.setData(d.vol);
  if (sPbv && d.pbv && d.pbv.length) sPbv.setData(d.pbv);
  curIv = iv;
}}
loadData('D');

// ── Crosshair OHLC legend ─────────────────────────────────────────────────────
chart.subscribeCrosshairMove(p => {{
  if (p.seriesData?.has(sCand)) {{
    const d = p.seriesData.get(sCand);
    if (d) {{
      const col = d.close >= d.open ? C.up : C.dn;
      document.getElementById('ohlc').innerHTML =
        `O:<b style="color:${{col}}">${{d.open?.toFixed(2)}}</b> ` +
        `H:<b style="color:${{C.up}}">${{d.high?.toFixed(2)}}</b> ` +
        `L:<b style="color:${{C.dn}}">${{d.low?.toFixed(2)}}</b> ` +
        `C:<b style="color:${{col}}">${{d.close?.toFixed(2)}}</b>`;
    }}
  }}
  // % from MAX/MIN in visible range
  const ts = p.time;
  if (ts) {{
    const vr = chart.timeScale().getVisibleRange();
    if (vr) {{
      const vis = DATA[curIv].candle.filter(x => x.time >= vr.from && x.time <= vr.to);
      if (vis.length) {{
        const hi = Math.max(...vis.map(x=>x.high));
        const lo = Math.min(...vis.map(x=>x.low));
        const last = vis[vis.length-1].close;
        document.getElementById('pct').innerHTML =
          ` <span style="color:#ef5350">▼MAX ${{((last-hi)/hi*100).toFixed(1)}}%</span>` +
          ` <span style="color:#22d68a">▲MIN +${{((last-lo)/lo*100).toFixed(1)}}%</span>`;
      }}
    }}
  }}
}});

// ── Controls ──────────────────────────────────────────────────────────────────
function setRange(days) {{
  document.querySelectorAll('.pb[onclick*="setRange"]').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  curRange = days;
  const src = DATA[curIv].candle;
  if (!src.length) return;
  if (days >= 99999) {{ chart.timeScale().fitContent(); return; }}
  const last = src[src.length-1].time;
  chart.timeScale().setVisibleRange({{ from: last - days*86400, to: last + 86400*3 }});
}}

function setIv(iv) {{
  ['ibD','ibW','ibM'].forEach(id => document.getElementById(id).classList.remove('active'));
  document.getElementById('ib'+iv).classList.add('active');
  loadData(iv);
  setTimeout(() => setRange_silent(curRange), 50);
}}

function setRange_silent(days) {{
  const src = DATA[curIv].candle;
  if (!src.length) return;
  if (days >= 99999) {{ chart.timeScale().fitContent(); return; }}
  const last = src[src.length-1].time;
  chart.timeScale().setVisibleRange({{ from: last - days*86400, to: last + 86400*3 }});
}}

function toggleType() {{
  showCandle = !showCandle;
  sCand.applyOptions({{visible: showCandle}});
  sLine.applyOptions({{visible: !showCandle}});
  document.getElementById('btn_type').textContent = showCandle ? 'Line' : 'Candle';
}}

function toggleLog() {{
  logMode = !logMode;
  chart.priceScale('price').applyOptions({{mode: logMode ? 1 : 0}});
  document.getElementById('btn_log').classList.toggle('active', logMode);
}}

// ── Resize ────────────────────────────────────────────────────────────────────
window.addEventListener('resize', () => chart.applyOptions({{width: Math.max(window.innerWidth,400)}}));

// ── Init: fit then zoom 1Y ────────────────────────────────────────────────────
(function init() {{
  const src = DATA['D'].candle;
  if (!src || !src.length) {{ setTimeout(init, 100); return; }}
  chart.timeScale().fitContent();
  setTimeout(() => {{
    const last = src[src.length-1].time;
    chart.timeScale().setVisibleRange({{ from: last - 365*86400, to: last + 86400*3 }});
  }}, 80);
}})();
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
    'EBITDA':                'key',
    'Gross Profit Ratio':    'key',
    'Operating Margin':      'key',
    'Net Income Ratio':      'key',
    'Cost Of Revenue':       'key',
    'Total Expenses':        'key',
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
        'Revenue & Profitability': ['Total Revenue','Gross Profit','Operating Income','Net Income','EBITDA','Diluted EPS'],
        'Margins & Ratios':        ['Gross Profit Ratio','Operating Margin','Net Income Ratio'],
        'Costs & Expenses':        ['Cost Of Revenue','Total Expenses','Selling General And Administration','Research And Development','Interest Expense','Tax Provision'],
    },
    'balance': {
        'Asset Base':              ['Total Assets','Cash And Cash Equivalents','Net Receivables','Inventory','Current Assets','Net PPE'],
        'Liabilities & Equity':   ['Current Liabilities','Total Debt','Long Term Debt','Total Liabilities Net Minority Interest','Stockholders Equity','Total Equity Gross Minority Interest'],
        'Working Capital':         ['Working Capital','Net Debt','Total Capitalization'],
    },
    'cashflow': {
        'Operating Cash':          ['Operating Cash Flow','Cash Flow From Continuing Operating Activities'],
        'Investing':               ['Capital Expenditure','Investing Cash Flow','Free Cash Flow'],
        'Financing':               ['Financing Cash Flow','Dividends Paid','Repurchase Of Capital Stock','Issuance Of Debt','Repayment Of Debt'],
        'Net Change':              ['Changes In Cash'],
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
        if remainder: ordered_rows.append(('group','Other',remainder))
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
    base=ticker.replace('.BK','') if ticker.endswith('.BK') else ticker
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
                  'Net margin shows how much of every revenue baht becomes profit after all costs'))

    roe_min=thr['roe_min']
    roe_med=_med(roe_s)
    sec_a.append((f'ROE (5Y median)',f'>{roe_min}%',
                  f"{roe_med:.1f}%" if roe_med else 'N/A',
                  roe_med is not None and roe_med>=roe_min,
                  'ROE measures how efficiently the company generates profit from shareholders capital'))

    earn_ok=_all_pos(net_income)
    sec_a.append(('Earnings Consistency','All years +',
                  '✓ No loss years' if earn_ok else '✗ Has loss years',
                  earn_ok,'Loss years signal structural or cyclical weakness — avoid for VI'))
    result['sections']['A']=('Business Quality',sec_a)

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
                      'Current ratio >1 means current assets cover current debts — company can pay short-term bills'))

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
    result['sections']['B']=('Financial Health',sec_b)

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
    result['sections']['C']=('Earnings Integrity',sec_c)

    # ── D. Fraud / Integrity — multi-signal scoring ────────────────────────────
    # Beneish M-Score
    m,ml,mc=compute_beneish(inc,bal,cf); m_ok=m is not None and m<=-2.22
    if m is not None and m>-1.78:
        result['red_flags'].append(('🚨 Governance Alert',
            f"Beneish M={m:.3f} — above −1.78. Elevated accounting manipulation risk."))
    elif m is not None and m>-2.22:
        result['red_flags'].append(('⚠️ Governance Watch',f"Beneish M={m:.3f}. Ambiguous signal — verify with latest filings."))

    sec_d=[]
    # D1. Beneish — show as probability-like scale, not binary
    if m is not None:
        # Rough probability mapping: M=-3 → ~5%, M=-2.22 → ~20%, M=-1.78 → ~50%, M>-1 → ~80%+
        risk_pct = min(95, max(3, int((m + 4.84) / 3.06 * 100)))
        beneish_label = f"M={m:.2f} → ~{risk_pct}% manipulation probability"
        sec_d.append(('Beneish M-Score','M < −2.22',beneish_label, m_ok,
            'Probabilistic score across 8 ratios: DSRI, GMI, AQI, SGI, LVGI, TATA. '
            'NOT a certainty — flags elevated accounting risk, not confirmed fraud.'))
    else:
        sec_d.append(('Beneish M-Score','M < −2.22','N/A (insufficient data)',False,
            'Needs 2+ years of financials. Check DSRI, GMI, AQI, SGI, LVGI, TATA manually.'))

    # D2. Receivables surge (channel stuffing / revenue inflation signal)
    try:
        rv=revenue.sort_index().dropna(); rc=receivables.sort_index().dropna()
        i2=rv.index.intersection(rc.index)
        if len(i2)>=2:
            rv_g=(rv[i2].iloc[-1]/rv[i2].iloc[-2]-1)*100
            rc_g=(rc[i2].iloc[-1]/rc[i2].iloc[-2]-1)*100
            gap=rc_g-rv_g; ok_d2=gap<=20
            risk_level='🟢 Clean' if gap<=20 else ('🟡 Caution' if gap<=40 else '🔴 High')
            if gap>40:
                result['red_flags'].append(('🚨 Receivables Surge',
                    f"Receivables grew {rc_g:+.0f}% vs revenue {rv_g:+.0f}% (+{gap:.0f}pp gap). Classic revenue-stuffing pattern."))
            sec_d.append(('Receivables vs Revenue Growth',f'Gap < 20pp',
                          f"{risk_level} (gap: {gap:+.0f}pp)",ok_d2,
                          'Large receivables growth vs revenue = booking sales not yet collected = potential inflation'))
        else: raise ValueError
    except: sec_d.append(('Receivables vs Revenue Growth','Gap < 20pp','N/A',True,''))

    # D3. Asset quality — unexplained asset growth vs revenue growth
    try:
        ta=safe_row(bal,'Total Assets').sort_index().dropna()
        if len(ta)>=2 and len(revenue.sort_index().dropna())>=2:
            rv2=revenue.sort_index().dropna()
            asset_g=(ta.iloc[-1]/ta.iloc[-2]-1)*100
            rev_g2=(rv2.iloc[-1]/rv2.iloc[-2]-1)*100
            bloat=asset_g-rev_g2; ok_d3=bloat<=25
            risk_level2='🟢 Clean' if bloat<=25 else ('🟡 Watch' if bloat<=50 else '🔴 Bloated')
            if bloat>50:
                result['red_flags'].append(('⚠️ Asset Bloat',
                    f"Assets grew {asset_g:+.0f}% vs revenue {rev_g2:+.0f}%. Unexplained asset accumulation."))
            sec_d.append(('Asset vs Revenue Growth','Gap < 25pp',
                          f"{risk_level2} (gap: {bloat:+.0f}pp)",ok_d3,
                          'Assets growing much faster than revenue = potential fictitious asset creation or acquisition masking weak growth'))
        else: raise ValueError
    except: sec_d.append(('Asset vs Revenue Growth','Gap < 25pp','N/A',True,''))

    # D4. Auditor/opinion check (via notes — placeholder, yfinance has no audit data)
    # We proxy this with leverage trend as a red flag
    try:
        td2=safe_row(bal,'Total Debt','Long Term Debt').sort_index().dropna()
        te2=safe_row(bal,'Stockholders Equity','Total Equity Gross Minority Interest').sort_index().dropna()
        if len(td2)>=3 and len(te2)>=3:
            de_now=float(td2.iloc[-1]/te2.iloc[-1]) if float(te2.iloc[-1])!=0 else None
            de_3y=float(td2.iloc[-3]/te2.iloc[-3]) if float(te2.iloc[-3])!=0 else None
            if de_now and de_3y:
                de_chg=de_now-de_3y; ok_d4=de_chg<=0.5
                risk_label='🟢 Stable' if de_chg<=0.5 else ('🟡 Rising' if de_chg<=1.5 else '🔴 Surging')
                if de_chg>1.5:
                    result['red_flags'].append(('⚠️ Debt Surge',
                        f"D/E ratio jumped +{de_chg:.2f}× in 3 years — investigate financing purpose."))
                sec_d.append(('Leverage Trend (3Y)','+D/E < 0.5×',
                              f"{risk_label} ({de_3y:.2f}× → {de_now:.2f}×)",ok_d4,
                              'Rapidly rising leverage can mask earnings weakness or fund fictitious growth'))
            else: raise ValueError
        else: raise ValueError
    except: sec_d.append(('Leverage Trend (3Y)','+D/E < 0.5×','N/A',True,''))

    # D5. Cash vs profit consistency (Sloan accruals already in C — here: OCF/NI ratio trend)
    try:
        ni_s3=net_income.sort_index().dropna(); oc_s3=op_cf.sort_index().dropna()
        idx3=ni_s3.index.intersection(oc_s3.index)
        if len(idx3)>=3:
            ratios=[(float(oc_s3[y])/float(ni_s3[y])) for y in idx3[-3:] if float(ni_s3[y])>0]
            if ratios:
                avg_ratio=sum(ratios)/len(ratios); ok_d5=avg_ratio>=0.6
                risk_l3='🟢 Solid' if avg_ratio>=0.8 else ('🟡 Weak' if avg_ratio>=0.4 else '🔴 Suspicious')
                if avg_ratio<0.4:
                    result['red_flags'].append(('🚨 Chronic Low Cash Conversion',
                        f"OCF/NI avg {avg_ratio:.2f} over 3Y — only {avg_ratio*100:.0f}% of reported profit backed by cash."))
                sec_d.append(('OCF/NI Ratio (3Y avg)','>0.6',
                              f"{risk_l3} ({avg_ratio:.2f})",ok_d5,
                              'Consistently low OCF vs NI = profit not materialising as cash — a strong fraud indicator'))
            else: raise ValueError
        else: raise ValueError
    except: sec_d.append(('OCF/NI Ratio (3Y avg)','>0.6','N/A',True,''))

    # Aggregate fraud risk score across all D signals
    d_pass=sum(1 for *_,ok,_ in sec_d if ok); d_total=len(sec_d)
    d_score=d_pass/d_total*100 if d_total else 0
    d_ok = d_score >= 60  # need at least 60% of fraud checks to pass

    result['sections']['D']=('Governance',sec_d)

    # ── E. Valuation ── (all thresholds sector-specific)
    sec_e=[]
    pe_max  = thr.get('pe_max',  20)
    pb_max  = thr.get('pb_max',  3.0)
    dy_min  = thr['div_yield_min']

    # Use the freshest price available: info.currentPrice > price_df latest close
    cp = (info.get('currentPrice') or info.get('regularMarketPrice') or
          (float(price_df['Close'].iloc[-1]) if not price_df.empty else None))

    # E1. Normalized P/E (5Y median EPS removes cyclical peaks/troughs)
    try:
        sh = info.get('sharesOutstanding') or info.get('impliedSharesOutstanding')
        ni_s2 = net_income.sort_index().dropna()
        if cp and sh and len(ni_s2) >= 1:
            mni  = float(ni_s2.iloc[-5:].median())
            meps = mni / float(sh)
            npe  = cp / meps if meps > 0 else None
            ok   = npe is not None and 0 < npe < pe_max
            sec_e.append((f'Normalized P/E (5Y median)', f'<{pe_max}×',
                           f"{npe:.1f}×" if npe else 'N/A', ok,
                           f'5Y median EPS removes cyclical distortion — sector ceiling {pe_max}×'))
        else: raise ValueError
    except: sec_e.append(('Normalized P/E (5Y)','N/A','N/A',False,''))

    # E2. Price/Book — sector-adjusted ceiling
    try:
        pb = float(info.get('priceToBook'))
        pb_ok = 0 < pb < pb_max
        if sg == 'bank':
            pb_note = f'For banks, P/B is the PRIMARY anchor (book = net loan assets). Target <{pb_max}×'
        elif sg in ('tech','healthcare'):
            pb_note = f'Intangibles understated on balance sheet — P/B <{pb_max}× acceptable for quality growth'
        else:
            pb_note = f'Graham margin of safety — ceiling {pb_max}× for {thr["label"]}'
        sec_e.append((f'Price/Book', f'<{pb_max}×', f"{pb:.2f}×", pb_ok, pb_note))
    except: sec_e.append(('Price/Book','N/A','N/A',False,''))

    # E3. Dividend yield
    dy = trailing_div_yield(divs, price_df)
    dy_ok = (dy or 0) >= dy_min
    sec_e.append(('Dividend Yield', f'>{dy_min}%',
                   f"{dy:.2f}%" if dy else 'N/A', dy_ok,
                   'Consistent dividend = real cash profits being returned to owners'))

    # E4. PEG ratio — growth at reasonable price
    try:
        per = float(info.get('trailingPE') or info.get('forwardPE'))
        rev2 = revenue.sort_index().dropna(); n = min(5, len(rev2)-1)
        cagr2 = ((rev2.iloc[-1]/rev2.iloc[-1-n])**(1/n)-1) if len(rev2) >= 2 else None
        if cagr2 and cagr2 > 0 and per:
            peg = per / (cagr2 * 100); ok = peg < 1.5
            if peg < 1.0:
                result['red_flags'].insert(0,('PEG Opportunity',
                    f"PEG={peg:.2f} — paying less than the earnings growth rate (Lynch sweet spot)"))
            sec_e.append(('PEG (P/E ÷ rev. growth)', '<1.5', f"{peg:.2f}", ok,
                           'PEG<1 = price below growth rate; >2 = expensive relative to growth'))
        else: raise ValueError
    except: sec_e.append(('PEG Ratio','<1.5','N/A',False,''))

    # E5. EV/EBITDA — useful for capital-intensive sectors where P/E misleads
    try:
        ev = info.get('enterpriseValue')
        ebitda_v = safe_row(inc,'EBITDA','Normalized EBITDA').sort_index().dropna()
        if ev and not ebitda_v.empty:
            ev_ebitda = float(ev) / float(ebitda_v.iloc[-1])
            # Sector-appropriate ceiling
            ev_ceil = 15 if sg in ('bank','finance') else (20 if sg in ('power','healthcare') else 12)
            ok_ev = 0 < ev_ebitda < ev_ceil
            sec_e.append((f'EV/EBITDA', f'<{ev_ceil}×', f"{ev_ebitda:.1f}×", ok_ev,
                           'Enterprise valuation — adjusts for leverage differences between companies'))
        else: raise ValueError
    except: sec_e.append(('EV/EBITDA','N/A','N/A',False,''))

    result['sections']['E']=('Valuation',sec_e)

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
    fd=sections.get('D',(None,[]))[1]
    # b_ok = majority of fraud signals pass (not just Beneish alone)
    if fd: b_ok=sum(1 for *_,ok,_ in fd if ok)/len(fd)>=0.6
    else:  b_ok=True
    gd=sections.get('F',(None,[]))[1]; ph_ok=gd[0][3] if gd else True
    has_wide=any('Phantom' in t or 'Widening' in t for t,_ in red_flags)
    if not b_ok and not ph_ok: verdict='🚨 SERIOUS RED FLAGS'; vc='#ef5350'
    elif not ph_ok:            verdict='🚨 PHANTOM PROFIT';    vc='#ef5350'
    elif not b_ok:             verdict='⚠️ Governance Risk';       vc='#f0c040'
    elif has_wide:             verdict='⚠️ Cash Gap — Monitor'; vc='#f0c040'
    elif overall>=72:          verdict='✅ Strong Buy Candidate';vc='#4ecca3'
    elif overall>=55:          verdict='⚠️ Research Further';   vc='#f0c040'
    else:                      verdict='❌ Avoid';               vc='#ef5350'

    SC={'A':'#2f81f7','B':'#3fb950','C':'#d29922','D':'#8b949e','E':'#a371f7','F':'#f0883e'}
    # Header bar
    base_disp = ticker.replace('.BK','') if ticker.endswith('.BK') else ticker
    sc=prof.get('color','#8b949e')
    vc_bg = 'rgba(63,185,80,0.1)' if vc=='#3fb950' else ('rgba(248,81,73,0.1)' if vc=='#f85149' else 'rgba(210,153,34,0.1)')
    st.markdown(f"""
<div style='display:flex;align-items:flex-start;justify-content:space-between;
            padding:16px 20px;background:#161b22;border:1px solid #21262d;
            border-radius:8px;margin-bottom:16px'>
  <div>
    <div style='font-size:18px;font-weight:700;color:#e6edf3;letter-spacing:-0.3px'>
      {base_disp}
      <span style='font-size:13px;font-weight:400;color:#8b949e;margin-left:8px'>VI Scorecard</span>
    </div>
    <div style='margin-top:6px;display:flex;align-items:center;gap:8px;flex-wrap:wrap'>
      <span style='border:1px solid {sc};border-radius:4px;padding:2px 8px;
                   color:{sc};font-size:11px;font-weight:600'>{prof["label"]}</span>
      <span style='color:#484f58;font-size:11px'>{prof["note"][:80]}{"…" if len(prof["note"])>80 else ""}</span>
    </div>
  </div>
  <div style='text-align:right;flex-shrink:0;margin-left:20px'>
    <div style='font-size:32px;font-weight:700;color:{vc};letter-spacing:-1px'>{overall:.0f}<span style='font-size:16px'>%</span></div>
    <div style='font-size:12px;font-weight:600;color:{vc};margin-top:2px;
                background:{vc_bg};padding:2px 8px;border-radius:4px'>{verdict}</div>
    <div style='font-size:11px;color:#484f58;margin-top:4px'>{tp}/{tn} passed</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Radar / Polygon chart ──────────────────────────────────────────────────
    axes_order = [('A','Quality'),('B','Health'),('C','Integrity'),('D','Governance'),('E','Value')]
    radar_vals = [sec_scores.get(sid,(0,0,0))[2] for sid,_ in axes_order]
    radar_labels = [lbl for _,lbl in axes_order]
    radar_colors = [SC.get(sid,'#aaa') for sid,_ in axes_order]
    n_axes = len(axes_order)

    import math
    # SVG polygon radar
    cx, cy, r_max = 150, 150, 110
    def pt(i, val):
        ang = math.pi/2 + 2*math.pi*i/n_axes
        rv = val/100 * r_max
        return cx - rv*math.cos(ang), cy - rv*math.sin(ang)

    # Background rings
    rings_svg = ""
    for ring_pct in [25, 50, 75, 100]:
        ring_pts = " ".join(f"{cx - ring_pct/100*r_max*math.cos(math.pi/2+2*math.pi*i/n_axes):.1f},{cy - ring_pct/100*r_max*math.sin(math.pi/2+2*math.pi*i/n_axes):.1f}" for i in range(n_axes))
        rings_svg += f"<polygon points='{ring_pts}' fill='none' stroke='#1e3358' stroke-width='1'/>"
        # Ring labels at right axis
        lx = cx - ring_pct/100*r_max*math.cos(math.pi/2) + 4
        ly = cy - ring_pct/100*r_max*math.sin(math.pi/2)
        rings_svg += f"<text x='{lx:.1f}' y='{ly:.1f}' fill='#2a4060' font-size='8' dominant-baseline='middle'>{ring_pct}%</text>"

    # Axis lines + labels
    axes_svg = ""
    for i, (sid, lbl) in enumerate(axes_order):
        ax, ay = pt(i, 100)
        axes_svg += f"<line x1='{cx}' y1='{cy}' x2='{ax:.1f}' y2='{ay:.1f}' stroke='#1e3358' stroke-width='1'/>"
        # Label position (push outward)
        lx2 = cx + (ax - cx)*1.22
        ly2 = cy + (ay - cy)*1.22
        col = radar_colors[i]
        pct_v = radar_vals[i]
        axes_svg += (f"<text x='{lx2:.1f}' y='{ly2-7:.1f}' fill='{col}' font-size='10' font-weight='700' text-anchor='middle'>{lbl}</text>"
                     f"<text x='{lx2:.1f}' y='{ly2+6:.1f}' fill='{col}' font-size='10' text-anchor='middle'>{pct_v:.0f}%</text>")

    # Filled polygon
    poly_pts = " ".join(f"{pt(i, v)[0]:.1f},{pt(i, v)[1]:.1f}" for i, v in enumerate(radar_vals))
    # Color based on overall score
    poly_fill = '#4ecca3' if overall>=72 else ('#f0c040' if overall>=55 else '#ef5350')
    poly_svg = (f"<polygon points='{poly_pts}' fill='{poly_fill}' fill-opacity='0.18' stroke='{poly_fill}' stroke-width='2' stroke-linejoin='round'/>"
                + "".join(f"<circle cx='{pt(i,v)[0]:.1f}' cy='{pt(i,v)[1]:.1f}' r='4' fill='{radar_colors[i]}' stroke='#0b1120' stroke-width='1.5'/>" for i,v in enumerate(radar_vals)))

    svg_html = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 300' width='300' height='300' style='display:block'>"
                f"<rect width='300' height='300' fill='#0b1120'/>"
                f"{rings_svg}{axes_svg}{poly_svg}"
                f"</svg>")

    left_col, right_col = st.columns([1, 2])
    with left_col:
        st.markdown(svg_html, unsafe_allow_html=True)
    with right_col:
        st.markdown("<div style='padding:8px 0'>",unsafe_allow_html=True)
        for sid, lbl in axes_order:
            p,n,pct = sec_scores.get(sid,(0,0,0))
            bc = '#3fb950' if pct>=70 else ('#d29922' if pct>=50 else '#f85149')
            st.markdown(
                f"<div style='margin-bottom:14px'>"
                f"<div style='display:flex;justify-content:space-between;align-items:baseline;margin-bottom:5px'>"
                f"<span style='color:#8b949e;font-size:13px;font-weight:500'>{lbl}</span>"
                f"<span style='color:{bc};font-size:14px;font-weight:700;font-variant-numeric:tabular-nums'>{pct:.0f}%</span>"
                f"</div>"
                f"<div style='background:#21262d;border-radius:3px;height:5px'>"
                f"<div style='width:{pct:.0f}%;height:5px;background:{bc};border-radius:3px'></div>"
                f"</div></div>",
                unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("<hr style='margin:12px 0'>",unsafe_allow_html=True)
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
            rows+=(f"<tr style='background:{rb};border-bottom:1px solid #21262d'>"
                   f"<td style='padding:7px 12px;color:#e6edf3;font-size:13px;white-space:nowrap'>"
                   f"<span style='color:{vc2};margin-right:6px;font-size:11px'>{ic}</span>{lbl}</td>"
                   f"<td style='padding:7px 12px;color:#484f58;font-size:12px'>{expl}</td>"
                   f"<td style='padding:7px 12px;color:#484f58;font-size:12px;text-align:center;white-space:nowrap'>{tgt}</td>"
                   f"<td style='padding:7px 12px;color:{vc2};font-size:13px;font-weight:600;text-align:right;font-family:ui-monospace,monospace;white-space:nowrap'>{val}</td></tr>")
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
    st.caption(f"Sector: {prof['label']} · Thresholds adjusted per sector model · Governance score = % of 5 integrity checks passing · Beneish (1999) · Not financial advice.")


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
    (4,"Fraud/Corruption",["fraud","embezzl","corrupt","bribery","ponzi","money launder","misappropriat","fictitious","kickback","fake invoice","\u0e09\u0e49\u0e2d\u0e42\u0e01\u0e07","\u0e17\u0e38\u0e08\u0e23\u0e34\u0e15","\u0e42\u0e01\u0e07\u0e40\u0e07\u0e34\u0e19","\u0e22\u0e31\u0e01\u0e22\u0e2d\u0e01","\u0e1b\u0e25\u0e2d\u0e21"]),
    (4,"Criminal Charges",["arrested","indicted","criminal charge","prosecut","warrant","jail","prison","charged with","\u0e08\u0e31\u0e1a\u0e01\u0e38\u0e21","\u0e04\u0e14\u0e35\u0e2d\u0e32\u0e0d\u0e32","\u0e2d\u0e2d\u0e01\u0e2b\u0e21\u0e32\u0e22\u0e08\u0e31\u0e1a","\u0e16\u0e39\u0e01\u0e08\u0e31\u0e1a"]),
    (4,"Regulatory Action",["sec charges","suspended trading","trading halted","delisted","revoked license","\u0e2b\u0e22\u0e38\u0e14\u0e0b\u0e37\u0e49\u0e2d\u0e02\u0e32\u0e22","\u0e16\u0e2d\u0e14\u0e17\u0e30\u0e40\u0e1a\u0e35\u0e22\u0e19"]),
    (3,"Investigation",["investigat","probe","raided","subpoena","sec inquiry","dsi","special case","\u0e2a\u0e2d\u0e1a\u0e2a\u0e27\u0e19","\u0e15\u0e23\u0e27\u0e08\u0e2a\u0e2d\u0e1a","\u0e1a\u0e38\u0e01\u0e04\u0e49\u0e19","\u0e14\u0e2a\u0e2e."]),
    (3,"Legal Action",["lawsuit","sued","litigation","court order","injunction","class action","filed complaint","\u0e1f\u0e49\u0e2d\u0e07\u0e23\u0e49\u0e2d\u0e07","\u0e23\u0e49\u0e2d\u0e07\u0e17\u0e38\u0e01\u0e02\u0e4c","\u0e28\u0e32\u0e25"]),
    (3,"Mgmt Misconduct",["ceo resign","fired","dismissed","misconduct","insider trading","executive arrested","management arrested","\u0e1c\u0e39\u0e49\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e25\u0e32\u0e2d\u0e2d\u0e01","\u0e1c\u0e39\u0e49\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e16\u0e39\u0e01\u0e08\u0e31\u0e1a"]),
    (2,"Accounting/Audit",["restat","qualified opinion","going concern","material weakness","auditor resign","delayed filing","falsif","\u0e07\u0e1a\u0e01\u0e32\u0e23\u0e40\u0e07\u0e34\u0e19\u0e41\u0e01\u0e49\u0e44\u0e02"]),
    (2,"Regulatory Warning",["warning","penalt","violation","non-complian","fine imposed","sanction","\u0e1b\u0e23\u0e31\u0e1a","\u0e42\u0e17\u0e29","\u0e40\u0e15\u0e37\u0e2d\u0e19"]),
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
        elif not b_ok:             verdict='⚠️ Governance Risk'
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
        base=ticker_yf.replace('.BK','') if ticker_yf.endswith('.BK') else ticker_yf; name=TICKER_NAMES.get(base,base)
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
        elif "Governance" in r.get("Verdict","") or "Beneish" in verdict: bg,tc,ic="#1e1600","#f0c040","⚠️"
        elif "Research" in verdict: bg,tc,ic="#141200","#d4b800","⚠️"
        elif "Avoid" in verdict:   bg,tc,ic="#180808","#e05050","❌"
        else: bg,tc,ic="#111","#888",""
        label=verdict.replace("✅ ","").replace("🚨 ","").replace("⚠️ ","").replace("❌ ","")
        return (f"<span style='background:{bg};color:{tc};padding:2px 10px;border-radius:10px;font-size:11px;font-weight:600;white-space:nowrap'>{ic} {label}</span>")
    def mini_bars(r):
        out=""
        for lbl,key in [("Q","A%"),("H","B%"),("I","C%"),("G","D%"),("V","E%")]:
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
    risk=sum(1 for r in rows if "Governance" in r.get("Verdict","") or "Beneish" in r.get("Verdict","") or "Phantom" in r.get("Verdict",""))
    avoid=sum(1 for r in rows if "Avoid" in r.get("Verdict",""))
    serious=sum(1 for r in rows if "Serious" in r.get("Verdict",""))
    avg_sc=sum(r.get("VI Score",0) or 0 for r in rows)/len(rows) if rows else 0
    def stat(v,lbl,c):
        return (f"<div style='background:#0a1220;border:1px solid #0e1e35;border-radius:8px;padding:10px 14px;text-align:center;flex:1;min-width:90px'>"
                f"<div style='font-size:22px;font-weight:800;color:{c}'>{v}</div>"
                f"<div style='font-size:10px;color:#446;margin-top:2px'>{lbl}</div></div>")
    summary=(f"<div style='display:flex;gap:8px;margin-bottom:18px;flex-wrap:wrap'>"
             +stat(f"{avg_sc:.0f}%","Avg Score","#00d4ff")+stat(strong,"Strong Buy","#4ecca3")
             +stat(research,"⚠️ Research More","#d4b800")+stat(risk,"⚠️ Fraud Risk","#f08020")
             +stat(avoid,"Avoid","#e05050")+stat(serious,"Serious","#ff2244")+"</div>")
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
    st.markdown("""<div style='margin-bottom:16px'>
<div style='font-size:18px;font-weight:600;color:#e6edf3;margin-bottom:4px'>Screener</div>
<div style='font-size:13px;color:#484f58'>Batch analysis across SET100 / MAI. Thresholds sector-adjusted. ≥72% strong · ≥55% research · below avoid.</div>
</div>""",unsafe_allow_html=True)
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
        import time as _time
        results=[]; errors=[]; t0=_time.time()
        prog_bar=st.progress(0)
        prog_text=st.empty()
        for i,t in enumerate(pool):
            elapsed=_time.time()-t0
            done_pct=(i+1)/len(pool)
            eta=elapsed/done_pct*(1-done_pct) if done_pct>0 else 0
            eta_str=f"{eta:.0f}s remaining" if eta>2 else "almost done…"
            prog_bar.progress(done_pct)
            prog_text.markdown(
                f"<div style='display:flex;align-items:center;gap:10px;padding:6px 0'>"
                f"<span style='color:#e6edf3;font-weight:600;font-size:13px'>{t}</span>"
                f"<span style='color:#484f58;font-size:12px'>{i+1} / {len(pool)}</span>"
                f"<span style='color:#484f58;font-size:12px'>·</span>"
                f"<span style='color:#8b949e;font-size:12px'>{eta_str}</span>"
                f"</div>", unsafe_allow_html=True)
            r=compute_quick_score(to_yf(t)); results.append(r)
            if r.get("Verdict")=="Error": errors.append(t)
        prog_bar.empty(); prog_text.empty()
        ok_n=len(results)-len(errors)
        total_t=_time.time()-t0
        msg=f"{ok_n}/{len(results)} stocks analysed in {total_t:.0f}s"
        if errors: msg+=f" · {len(errors)} failed: {', '.join(errors[:4])}"
        st.success(msg)
        st.session_state["screener_results"]=results; st.session_state["screener_meta"]=f"{universe} · {sector_f}"
    if "screener_results" not in st.session_state: return
    all_r=st.session_state["screener_results"]
    filtered=[r for r in all_r if (r.get("VI Score") or 0)>=min_score]
    asc=(sort_by=="P/E"); filtered.sort(key=lambda r:(r.get(sort_by) or 0),reverse=not asc)
    meta=st.session_state.get("screener_meta","")
    st.caption(f"**{len(filtered)}** stocks · {meta} · min {min_score}% · sorted by {sort_by}  · Q=Quality  H=Health  I=Integrity  G=Governance  V=Valuation")
    fa,fb,fc,fd,fe=st.columns(5); active=st.session_state.get("scr_filter","all")
    with fa:
        if st.button("Strong Buy",use_container_width=True,key="f_sb"): st.session_state["scr_filter"]="sb" if active!="sb" else "all"
    with fb:
        if st.button("Red Flags",use_container_width=True,key="f_rf"): st.session_state["scr_filter"]="rf" if active!="rf" else "all"
    with fc:
        if st.button("FCF+ only",use_container_width=True,key="f_fcf"): st.session_state["scr_filter"]="fcf" if active!="fcf" else "all"
    with fd:
        if st.button("Div ≥ 2%",use_container_width=True,key="f_div"): st.session_state["scr_filter"]="div" if active!="div" else "all"
    with fe:
        if st.button("ROE ≥ 15%",use_container_width=True,key="f_roe"): st.session_state["scr_filter"]="roe" if active!="roe" else "all"
    flt=st.session_state.get("scr_filter","all")
    if flt=="sb":   filtered=[r for r in filtered if "Strong" in r.get("Verdict","")]
    elif flt=="rf": filtered=[r for r in filtered if "🚨" in r.get("Verdict","") or "Governance" in r.get("Verdict","")]
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
        dt=st.tabs(["Price","Financials","Fundamentals","VI Scorecard","News"])
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
        st.markdown("<div style='padding:12px 2px 10px;border-bottom:1px solid #21262d;margin-bottom:10px'><div style='font-size:14px;font-weight:600;color:#e6edf3'>SET Analyser</div><div style='font-size:11px;color:#484f58;margin-top:1px'>Value Investor Edition</div></div>",unsafe_allow_html=True)

        # ── SET100 section ──────────────────────────────────────────────────────
        st.markdown("<div class='sidebar-label'>SET 100</div>",unsafe_allow_html=True)
        sector_keys=['All']+sorted(SECTOR_MAP.keys())
        active_sec=st.session_state.get('sb_sec','All')
        for row_start in range(0,len(sector_keys),3):
            row_keys=sector_keys[row_start:row_start+3]
            btn_cols=st.columns([1,1,1],gap="small")
            for ci,sk in enumerate(row_keys):
                ico,lbl=SECTOR_ICONS.get(sk,("",sk[:6]))
                is_active=(sk==active_sec)
                with btn_cols[ci]:
                    label_str=f"{ico} {lbl}" if ico else lbl
                    btn_type="primary" if is_active else "secondary"
                    if st.button(label_str,key=f"sec_btn_{sk}",use_container_width=True,type=btn_type):
                        st.session_state['sb_sec']=sk if sk!=active_sec else 'All'
                        if 'set_ms' in st.session_state: del st.session_state['set_ms']
                        st.rerun()

        active_sec=st.session_state.get('sb_sec','All')
        available_set100=SET100 if active_sec=='All' else [t for t in SECTOR_MAP.get(active_sec,[]) if t in SET100]
        ph100="All SET100…" if active_sec=='All' else f"{active_sec} ({len(available_set100)})"
        set_sel=st.multiselect("SET100",available_set100,placeholder=ph100,key="set_ms",label_visibility="collapsed")
        st.markdown("<hr>",unsafe_allow_html=True)

        # ── MAI section ─────────────────────────────────────────────────────────
        st.markdown("<div class='sidebar-label'>MAI</div>",unsafe_allow_html=True)
        mai_sec_keys=['All']+sorted(MAI_SECTOR_MAP.keys())
        active_mai=st.session_state.get('mai_sec','All')
        for mrow_start in range(0,len(mai_sec_keys),3):
            mrow_keys=mai_sec_keys[mrow_start:mrow_start+3]
            mai_cols=st.columns([1,1,1],gap="small")
            for ci,sk in enumerate(mrow_keys):
                ico,lbl=SECTOR_ICONS.get(sk,("",sk[:6]))
                is_active=(sk==active_mai)
                with mai_cols[ci]:
                    label_str=f"{ico} {lbl}" if ico else lbl
                    btn_type="primary" if is_active else "secondary"
                    if st.button(label_str,key=f"mai_btn_{sk}",use_container_width=True,type=btn_type):
                        st.session_state['mai_sec']=sk if sk!=active_mai else 'All'
                        if 'mai_ms' in st.session_state: del st.session_state['mai_ms']
                        st.rerun()

        active_mai=st.session_state.get('mai_sec','All')
        available_mai=MAI_TICKERS if active_mai=='All' else [t for t in MAI_SECTOR_MAP.get(active_mai,[]) if t in MAI_TICKERS]
        ph_mai="All MAI…" if active_mai=='All' else f"{active_mai} ({len(available_mai)})"
        mai_sel=st.multiselect("MAI",available_mai,placeholder=ph_mai,key="mai_ms",label_visibility="collapsed")
        st.markdown("<hr>",unsafe_allow_html=True)

        # ── DR / ETF ────────────────────────────────────────────────────────────
        st.markdown("<div class='sidebar-label'>DR / ETF</div>",unsafe_allow_html=True)
        dr_sel=st.multiselect("DR",DR_TICKERS,placeholder="DR / ETF…",key="dr_ms",label_visibility="collapsed")
        st.markdown("<hr>",unsafe_allow_html=True)

        # ── Global / Custom ─────────────────────────────────────────────────────
        st.markdown("<div class='sidebar-label'>Global / Custom</div>",unsafe_allow_html=True)
        st.markdown("<div style='font-size:11px;color:#484f58;margin-bottom:5px'>Any Yahoo Finance ticker</div>",unsafe_allow_html=True)
        custom_raw=st.text_input("Custom",placeholder="AAPL, TSLA, 9984.T…",key="custom_tickers",label_visibility="collapsed")
        custom_sel=[t.strip().upper() for t in custom_raw.replace(","," ").split() if t.strip()]
        GLOBAL_SHORTCUTS = {
            "US Tech":     ["AAPL","MSFT","GOOGL","AMZN","NVDA","META","TSLA","AMD","INTC","CRM","ORCL","NFLX","ADBE","QCOM"],
            "US Finance":  ["JPM","BAC","GS","MS","V","MA","BRK-B","AXP","C","WFC","BLK"],
            "US Health":   ["JNJ","UNH","PFE","ABBV","LLY","MRK","ABT","TMO","MDT"],
            "US Others":   ["BRK-B","XOM","CVX","WMT","KO","PEP","MCD","DIS","BA","CAT","HON","GE"],
            "Indices":     ["^GSPC","^DJI","^IXIC","^RUT","^FTSE","^N225","^HSI","^STI","^SET.BK","^KS11","^AXJO"],
            "Japan":       ["7203.T","9984.T","6758.T","8306.T","6861.T","7267.T","4661.T","9432.T","8058.T","6902.T"],
            "Korea":       ["005930.KS","000660.KS","035420.KS","051910.KS","035720.KS","068270.KS","005380.KS"],
            "China/HK":    ["0700.HK","9988.HK","3690.HK","1299.HK","0005.HK","BABA","JD","PDD","BIDU","NIO","XPEV"],
            "Singapore":   ["D05.SI","O39.SI","U11.SI","Z74.SI","F34.SI","C09.SI","G13.SI","BN4.SI"],
            "Europe":      ["ASML","SAP","NVO","AZN","LVMH.PA","MC.PA","NESN.SW","NOVO-B.CO"],
            "Crypto":      ["BTC-USD","ETH-USD","BNB-USD","SOL-USD","ADA-USD","XRP-USD","DOGE-USD"],
            "ETF/Bond":    ["SPY","QQQ","VTI","IWM","EEM","GLD","SLV","TLT","HYG","VNQ","XLE","XLK"],
            "Commodities": ["GC=F","SI=F","CL=F","NG=F","HG=F","ZC=F","ZS=F","KC=F"],
        }
        gl_grp=st.selectbox("Region",["—"]+list(GLOBAL_SHORTCUTS.keys()),key="gl_grp",label_visibility="collapsed")
        gl_sel=st.multiselect("Picks",GLOBAL_SHORTCUTS.get(gl_grp,[]),placeholder=f"Pick {gl_grp}…",key=f"gl_ms_{gl_grp}",label_visibility="collapsed") if gl_grp and gl_grp!="—" else []

        selected_base=set_sel+mai_sel+dr_sel
        selected_global=custom_sel+gl_sel
        selected=[to_yf(t) for t in selected_base]+selected_global
        all_selected_base=selected_base+selected_global

        st.markdown("<hr>",unsafe_allow_html=True)
        if all_selected_base:
            preview=", ".join(all_selected_base[:5])+("…" if len(all_selected_base)>5 else "")
            st.markdown(f"<div style='font-size:12px;color:#8b949e;margin-bottom:8px'><span style='color:#3fb950;font-weight:600'>{len(all_selected_base)}</span> selected · {preview}</div>",unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("Clear all",use_container_width=True):
                # Clear ALL stock selection state — multiselects, sector filters, custom input
                keys_to_clear = [k for k in st.session_state.keys() if any(
                    k.startswith(p) for p in [
                        'set_ms','mai_ms','dr_ms',           # multiselect selections
                        'sb_sec','mai_sec',                   # sector filter state
                        'custom_tickers','gl_grp',            # custom input
                        'scr_filter','screener_results','screener_meta',  # screener
                    ]) or k.startswith('gl_ms_')              # regional picks
                ]
                for k in keys_to_clear:
                    del st.session_state[k]
                st.rerun()
        with c2:
            if st.button("Refresh prices",use_container_width=True,
                          help="Force reload latest prices (prices auto-refresh every 5 min)"):
                # Only clear price cache — keep fundamentals cache (slow to reload)
                fetch_price.clear()
                st.rerun()

    TABS=["Screener","Price","Financials","Fundamentals","VI Score","News"]
    tabs=st.tabs(TABS)

    def _need_selection():
        st.markdown("<div style='background:#080e1c;border:1px dashed #1a2e48;border-radius:10px;padding:36px;text-align:center;margin-top:20px'>"
                    "<div style='font-size:36px'>←</div><div style='color:#00c8f8;font-size:16px;margin:10px 0 6px;font-weight:600'>Pick a stock in the sidebar</div>"
                    "<div style='color:#2a4060;font-size:13px'>Use the sector icons → stock list on the left</div></div>",unsafe_allow_html=True)

    with tabs[0]: show_screener_tab()

    # ── Price tab ──────────────────────────────────────────────────────────────
    with tabs[1]:
        if not selected: _need_selection()
        else:
            # Show only first ticker in price tab to avoid vertical scroll
            ticker = selected[0]
            if len(selected) > 1:
                st.caption(f"Showing {ticker.replace('.BK','')} · {len(selected)-1} more in sidebar — price tab shows one at a time")
            with st.spinner(f"Loading {ticker}…"):
                html_chart, chart_h = make_tv_chart(ticker)
                # height=0 lets the iframe expand to its content height via AVAIL_H JS
                _components.html(html_chart, height=chart_h, scrolling=False)

    # ── Financials tab ─────────────────────────────────────────────────────────
    with tabs[2]:
        if not selected: _need_selection()
        else:
            for ticker in selected:
                base=ticker.replace('.BK','') if ticker.endswith('.BK') else ticker; name=TICKER_NAMES.get(base,base)
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
