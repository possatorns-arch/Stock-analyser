"""
SET Stock Analyser — Value Investor Edition  (Streamlit)
Run:  streamlit run app.py
Deploy: Streamlit Cloud / Render / Railway (free tier)
"""
import warnings; warnings.filterwarnings('ignore')
import streamlit as st
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
    page_title="SET Analyser · VI Edition",
    page_icon="🏦", layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
  body, .stApp { background:#060e1c; color:#ddd; }
  section[data-testid="stSidebar"] { background:#0a1428; }
  .block-container { padding:1rem 1.5rem; }
  .stTabs [data-baseweb="tab"] { color:#aaa; font-size:13px; }
  .stTabs [aria-selected="true"] { color:#00d4ff; border-bottom:2px solid #00d4ff; }
  div[data-testid="stDataFrameResizable"] { border:1px solid #1e3a5f; border-radius:6px; }
  .stButton>button { background:#0e2040; color:#00d4ff; border:1px solid #1e3a5f;
                     border-radius:6px; transition:all 0.2s; }
  .stButton>button:hover { background:#1e3a5f; }
  h1,h2,h3 { color:#00d4ff; }
  .vi-card { background:#060e1c; border:1px solid #1e3a5f; border-radius:10px;
             padding:16px; margin:8px 0; }
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
    ax.set_facecolor('#0d0d0d')
    ax.tick_params(colors='#aaaaaa', labelsize=8)
    ax.grid(axis='y', color='#2a2a2a', linewidth=0.5, linestyle='--')
    ax.grid(axis='x', color='#1a1a1a', linewidth=0.3)
    for sp in ax.spines.values(): sp.set_edgecolor('#2a2a2a')

# ─── Data fetch (cached 6h) ─────────────────────────────────────────────────────
@st.cache_data(ttl=21600, show_spinner=False)
def fetch_all(ticker):
    tk = yf.Ticker(ticker)
    end = pd.Timestamp.now()
    data = dict(ticker=ticker, info={}, price=pd.DataFrame(),
                income=pd.DataFrame(), balance=pd.DataFrame(),
                cashflow=pd.DataFrame(), divs=pd.Series(dtype=float))
    try: data['info']     = tk.info or {}
    except: pass
    try: data['price']    = tk.history(interval='1d', start=end-pd.DateOffset(years=10), end=end)
    except: pass
    try: data['income']   = tk.income_stmt
    except: pass
    try: data['balance']  = tk.balance_sheet
    except: pass
    try: data['cashflow'] = tk.cashflow
    except: pass
    try: data['divs']     = tk.dividends
    except: pass
    return data

# ─── 1. Price chart ──────────────────────────────────────────────────────────────
EMA_W = [25,75,200]; EMA_C = ['deeppink','limegreen','grey']; EMA_L = ['EMA 25','EMA 75','EMA 200']

def make_price_chart(ticker, start):
    d = fetch_all(ticker); df = ts_filter(d['price'], start)
    fig = plt.figure(figsize=(14, 5.5), facecolor='#0d0d0d')
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
                  xy=(0.01,0.96), xycoords='axes fraction', fontsize=8.5,
                  color='#ff4d6d', va='top', fontfamily='monospace')
    ax_p.annotate(f"▲ from MIN  +{(ep-close.min())/close.min()*100:.1f}%",
                  xy=(0.50,0.96), xycoords='axes fraction', fontsize=8.5,
                  color='#4ecca3', va='top', ha='center', fontfamily='monospace')
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
        return f"<p style='color:#555;font-style:italic'>No data for {title}</p>"
    cols = sorted(df.columns)[-max_years:]
    sub  = df[cols].copy(); col_lbs = [str(c)[:4] for c in cols]
    scale, ulabel = _auto_scale(sub)
    hdr = "".join(f"<th style='padding:6px 12px;color:#00d4ff;text-align:right;"
                  f"background:#0e1628;border-bottom:2px solid #1e3a5f;font-size:11px'>{y}</th>"
                  for y in col_lbs)
    rows = ""
    for i, (rn, rd) in enumerate(sub.iterrows()):
        bg = "#0b1120" if i%2==0 else "#0d1526"
        cells = ""
        for col in cols:
            try:
                v = float(rd[col])
                txt = "—" if pd.isna(v) else f"{v/scale:,.2f}"
                clr = "#555" if pd.isna(v) else ("#ff6b6b" if v<0 else "#c8f0d8")
            except: txt,clr = "—","#555"
            cells += (f"<td style='padding:4px 12px;text-align:right;color:{clr};"
                      f"font-size:11px;font-family:monospace;border-bottom:1px solid #13213a'>{txt}</td>")
        rows += (f"<tr style='background:{bg}'>"
                 f"<td style='padding:4px 8px;color:#ccc;font-size:11px;"
                 f"border-bottom:1px solid #13213a;white-space:nowrap'>{str(rn)[:55]}</td>{cells}</tr>")
    return (f"<div style='margin:12px 0'>"
            f"<div style='color:#00d4ff;font-size:13px;font-weight:bold;margin-bottom:4px'>{title}"
            f" <span style='color:#555;font-size:10px;font-weight:normal'>({ulabel})</span></div>"
            f"<div style='overflow-x:auto'><table style='border-collapse:collapse;width:100%'>"
            f"<thead><tr><th style='padding:6px 8px;color:#aaa;text-align:left;background:#0e1628;"
            f"border-bottom:2px solid #1e3a5f;font-size:11px'>Line Item</th>{hdr}</tr></thead>"
            f"<tbody>{rows}</tbody></table></div></div>")

# ─── 3. Fundamental chart ───────────────────────────────────────────────────────
def make_fundamental_chart(ticker):
    DARK='#0d0d0d'; ACC='#00d4ff'; POS='#26c6da'; NEG='#ef5350'; WARN='#f0c040'; GRN='#4ecca3'
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
        st.caption("5-section analysis · cycle-adjusted · Beneish fraud model · Buffett / Graham standards")
    with col2:
        st.markdown(f"<div style='text-align:right'>"
                    f"<span style='font-size:22px;font-weight:bold;color:{vc}'>{overall:.0f}%</span>"
                    f"<br><span style='color:{vc};font-size:13px'>{verdict}</span>"
                    f"<br><span style='color:#555;font-size:10px'>{tp}/{tn} criteria passed</span></div>",
                    unsafe_allow_html=True)

    # Section progress bars
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

    # Cycle flags
    if cycle_flags:
        items="  ·  ".join(f"📉 {f['label']}: recent {f['recent']:.1f}% vs 5Y median {f['hist']:.1f}% ({f['pct']:+.1f}pp)"
                            for f in cycle_flags)
        st.info(f"🔄 **Cycle Detector** — {items}")

    # Red flags
    for title,msg in red_flags:
        if title.startswith('💎'): st.success(f"**{title}** — {msg}")
        elif '🚨' in title:       st.error  (f"**{title}** — {msg}")
        else:                      st.warning(f"**{title}** — {msg}")

    # Section tables
    for sid,(stitle,crit) in sections.items():
        p,n,pct=sec_scores[sid]; bc='#4ecca3' if pct>=70 else ('#f0c040' if pct>=50 else '#ef5350')
        rows=""
        for lbl,tgt,val,ok,expl in crit:
            ic='✅' if ok else '❌'; rb='#0b1a10' if ok else '#1a0b0b'; vc2='#4ecca3' if ok else '#ef5350'
            rows+=(f"<tr style='background:{rb}'>"
                   f"<td style='padding:5px 8px;color:#ddd;font-size:11px'>{ic} {lbl}</td>"
                   f"<td style='padding:5px 8px;color:#666;font-size:10px'>{expl}</td>"
                   f"<td style='padding:5px 8px;color:#888;font-size:10px;text-align:center'>{tgt}</td>"
                   f"<td style='padding:5px 8px;color:{vc2};font-size:11px;font-weight:bold;"
                   f"text-align:right;font-family:monospace;white-space:nowrap'>{val}</td></tr>")
        st.markdown(
            f"<div style='margin-bottom:12px'>"
            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:4px'>"
            f"<span style='color:{SC.get(sid,'#aaa')};font-size:13px;font-weight:bold'>{stitle}</span>"
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
            unsafe_allow_html=True
        )
    st.caption("Thresholds: Buffett / Graham / Beneish (1999). Quality metrics use 5Y medians. Not financial advice.")

# ─── 5. News — improved sources + body snippets + temporal decay ────────────────
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
    # MAI
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
    "EA"   :["\u0e1e\u0e25\u0e31\u0e07\u0e07\u0e32\u0e19\u0e1a\u0e23\u0e34\u0e2a\u0e38\u0e17\u0e18\u0e34\u0e4c","\u0e2d\u0e21\u0e23 \u0e17\u0e2d\u0e07\u0e18\u0e34\u0e23\u0e32\u0e0a","EA \u0e2a\u0e2d\u0e1a\u0e2a\u0e27\u0e19"],
    "PTT"  :["\u0e1b\u0e15\u0e17."],
    "PTTEP":["\u0e1b\u0e15\u0e17\u0e2a\u0e2a."],
    "AOT"  :["\u0e17\u0e2d\u0e17.","\u0e17\u0e48\u0e32\u0e2d\u0e32\u0e01\u0e32\u0e28\u0e22\u0e32\u0e19\u0e44\u0e17\u0e22"],
    "KBANK":["\u0e01\u0e2a\u0e34\u0e01\u0e23\u0e44\u0e17\u0e22"],
    "SCB"  :["\u0e44\u0e17\u0e22\u0e1e\u0e32\u0e13\u0e34\u0e0a\u0e22\u0e4c"],
    "BBL"  :["\u0e01\u0e23\u0e38\u0e07\u0e40\u0e17\u0e1e\u0e41\u0e1a\u0e07\u0e01\u0e4c\u0e04\u0e4c"],
    "KTB"  :["\u0e01\u0e23\u0e38\u0e07\u0e44\u0e17\u0e22"],
    "GULF" :["\u0e01\u0e31\u0e25\u0e1f\u0e4c"],
    "TOP"  :["\u0e44\u0e17\u0e22\u0e2d\u0e2d\u0e22\u0e25\u0e4c"],
    "CPALL":["\u0e0b\u0e35\u0e1e\u0e35 \u0e2d\u0e2d\u0e25\u0e25\u0e4c","\u0e40\u0e0b\u0e40\u0e27\u0e48\u0e19"],
    "TRUE" :["\u0e17\u0e23\u0e39 \u0e04\u0e2d\u0e23\u0e4c\u0e1b\u0e2d\u0e40\u0e23\u0e0a\u0e31\u0e48\u0e19","\u0e17\u0e23\u0e39\u0e21\u0e39\u0e1f"],
    "ADVANC":["\u0e40\u0e2d\u0e44\u0e2d\u0e40\u0e2d\u0e2a","AIS"],
    "BTS"  :["\u0e1a\u0e35\u0e17\u0e35\u0e40\u0e2d\u0e2a","\u0e23\u0e16\u0e44\u0e1f\u0e1f\u0e49\u0e32\u0e1a\u0e35\u0e17\u0e35\u0e40\u0e2d\u0e2a"],
    "SAWAD":["\u0e28\u0e23\u0e35\u0e2a\u0e27\u0e31\u0e2a\u0e14\u0e34\u0e4c"],
    "TIDLOR":["\u0e40\u0e07\u0e34\u0e19\u0e15\u0e34\u0e14\u0e25\u0e49\u0e2d"],
    "MTC"  :["\u0e40\u0e21\u0e37\u0e2d\u0e07\u0e44\u0e17\u0e22\u0e41\u0e04\u0e1b\u0e1b\u0e34\u0e15\u0e2d\u0e25"],
    "BDMS" :["\u0e1a\u0e32\u0e07\u0e01\u0e2d\u0e01 \u0e14\u0e38\u0e2a\u0e34\u0e15"],
    "CPF"  :["\u0e40\u0e08\u0e23\u0e34\u0e0d\u0e42\u0e20\u0e04\u0e20\u0e31\u0e13\u0e11\u0e4c"],
    "SCC"  :["\u0e1b\u0e39\u0e19\u0e0b\u0e35\u0e40\u0e21\u0e19\u0e15\u0e4c"],
    "BANPU":["\u0e1a\u0e49\u0e32\u0e19\u0e1b\u0e39"],
    "IVL"  :["Indorama"],
}

RISK_KW=[
    (4,"Fraud/Corruption",["fraud","embezzl","corrupt","bribery","ponzi","money launder",
                           "misappropriat","fictitious","kickback","fake invoice",
                           "\u0e09\u0e49\u0e2d\u0e42\u0e01\u0e07","\u0e17\u0e38\u0e08\u0e23\u0e34\u0e15","\u0e42\u0e01\u0e07\u0e40\u0e07\u0e34\u0e19","\u0e22\u0e31\u0e01\u0e22\u0e2d\u0e01","\u0e1b\u0e25\u0e2d\u0e21"]),
    (4,"Criminal Charges", ["arrested","indicted","criminal charge","prosecut","warrant","jail","prison","charged with",
                           "\u0e08\u0e31\u0e1a\u0e01\u0e38\u0e21","\u0e04\u0e14\u0e35\u0e2d\u0e32\u0e0d\u0e32","\u0e2d\u0e2d\u0e01\u0e2b\u0e21\u0e32\u0e22\u0e08\u0e31\u0e1a","\u0e16\u0e39\u0e01\u0e08\u0e31\u0e1a"]),
    (4,"Regulatory Action",["sec charges","suspended trading","trading halted","delisted","revoked license",
                           "\u0e2b\u0e22\u0e38\u0e14\u0e0b\u0e37\u0e49\u0e2d\u0e02\u0e32\u0e22","\u0e16\u0e2d\u0e14\u0e17\u0e30\u0e40\u0e1a\u0e35\u0e22\u0e19"]),
    (3,"Investigation",    ["investigat","probe","raided","subpoena","sec inquiry","dsi","special case",
                           "\u0e2a\u0e2d\u0e1a\u0e2a\u0e27\u0e19","\u0e15\u0e23\u0e27\u0e08\u0e2a\u0e2d\u0e1a","\u0e1a\u0e38\u0e01\u0e04\u0e49\u0e19","\u0e14\u0e2a\u0e2e."]),
    (3,"Legal Action",     ["lawsuit","sued","litigation","court order","injunction","class action","filed complaint",
                           "\u0e1f\u0e49\u0e2d\u0e07\u0e23\u0e49\u0e2d\u0e07","\u0e23\u0e49\u0e2d\u0e07\u0e17\u0e38\u0e01\u0e02\u0e4c","\u0e28\u0e32\u0e25"]),
    (3,"Mgmt Misconduct",  ["ceo resign","fired","dismissed","misconduct","insider trading","executive arrested","management arrested",
                           "\u0e1c\u0e39\u0e49\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e25\u0e32\u0e2d\u0e2d\u0e01","\u0e1c\u0e39\u0e49\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e16\u0e39\u0e01\u0e08\u0e31\u0e1a"]),
    (2,"Accounting/Audit", ["restat","qualified opinion","going concern","material weakness","auditor resign","delayed filing","falsif",
                           "\u0e07\u0e1a\u0e01\u0e32\u0e23\u0e40\u0e07\u0e34\u0e19\u0e41\u0e01\u0e49\u0e44\u0e02"]),
    (2,"Regulatory Warning",["warning","penalt","violation","non-complian","fine imposed","sanction",
                            "\u0e1b\u0e23\u0e31\u0e1a","\u0e42\u0e17\u0e29","\u0e40\u0e15\u0e37\u0e2d\u0e19"]),
    (2,"Related Party",    ["related party","self-dealing","tunneling","undisclosed transaction",
                           "\u0e23\u0e32\u0e22\u0e01\u0e32\u0e23\u0e01\u0e31\u0e1a\u0e1a\u0e38\u0e04\u0e04\u0e25\u0e17\u0e35\u0e48\u0e40\u0e01\u0e35\u0e48\u0e22\u0e27\u0e02\u0e49\u0e2d\u0e07"]),
    (1,"Controversy",      ["scandal","controversy","boycott","\u0e41\u0e09","\u0e01\u0e23\u0e30\u0e41\u0e2a"]),
]
POS_KW=["award","record profit","upgraded","buy rating","dividend increase",
        "\u0e01\u0e33\u0e44\u0e23\u0e2a\u0e39\u0e07\u0e2a\u0e38\u0e14"]

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
        st.info(f"No news found for {base}. Try broadening by searching Bangkok Post directly.")
        return
    now=_dt.now()
    max_sev=0; flagged=0; positives=0
    for art in articles:
        t=art.get("title",""); snip=art.get("snippet","")
        sev,cat,is_pos=_classify(t+" "+snip)
        if sev>=3: flagged+=1
        if is_pos: positives+=1
        if sev>max_sev: max_sev=sev
    if max_sev>=4 or flagged>=3:   ov="🚨 High Risk";  ov_c="#ef5350"
    elif max_sev>=3 or flagged>=1: ov="⚠️ Caution";    ov_c="#f0c040"
    else:                           ov="✅ Clean";       ov_c="#4ecca3"
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:16px;margin-bottom:12px'>"
        f"<span style='color:#00d4ff;font-size:16px;font-weight:bold'>📰 {base} News</span>"
        f"<span style='color:{ov_c};font-size:14px;font-weight:bold'>{ov}</span>"
        f"<span style='color:#555;font-size:11px'>{len(articles)} articles · "
        f"{flagged} flagged · {positives} positive</span></div>",
        unsafe_allow_html=True
    )
    SEV_C={4:"#ff1744",3:"#ef5350",2:"#f0c040",1:"#aaaaaa",0:"#444444"}
    SEV_L={4:"CRITICAL",3:"HIGH",2:"MEDIUM",1:"LOW",0:""}
    for art in articles:
        title=art.get("title",""); link=art.get("link","")
        src=art.get("source",""); date_s=art.get("date",""); snip=art.get("snippet","")
        sev,cat,is_pos=_classify(title+" "+snip)
        # Temporal decay
        age_days=999
        try: age_days=(now-_dt.strptime(date_s,"%Y-%m-%d")).days
        except: pass
        opacity=1.0 if age_days<=90 else (0.65 if age_days<=365 else 0.35)
        if is_pos: bdr="#4ecca3"; lbl="✅ POSITIVE"
        elif sev>0: bdr=SEV_C[sev]; lbl=f"{'🚨' if sev>=4 else '🔴' if sev>=3 else '🟡'} {SEV_L[sev]}: {cat}"
        else: bdr="#1e3a5f"; lbl=""
        age_note="" if age_days<=365 else f" · <span style='color:#f0c040'>⏰ {age_days//365}y ago</span>"
        snip_html=f"<br><span style='color:#888;font-size:10px'>{snip[:180]}…</span>" if snip and sev>0 else ""
        st.markdown(
            f"<div style='border-left:3px solid {bdr};padding:6px 12px;margin-bottom:5px;"
            f"background:#0a1020;border-radius:0 4px 4px 0;opacity:{opacity}'>"
            f"<div style='display:flex;justify-content:space-between;align-items:flex-start'>"
            f"<a href='{link}' target='_blank' style='color:#ddd;text-decoration:none;font-size:12px;flex:1'>{title}</a>"
            f"<span style='color:#555;font-size:10px;white-space:nowrap;margin-left:8px'>{src}</span></div>"
            f"<div style='color:#555;font-size:10px;margin-top:2px'>{date_s}{age_note}"
            f"{' · <span style=\"color:'+bdr+';font-weight:bold\">'+lbl+'</span>' if lbl else ''}"
            f"</div>{snip_html}</div>",
            unsafe_allow_html=True
        )

# ─── 6. Screener ────────────────────────────────────────────────────────────────
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
        dy=(info.get('dividendYield') or 0)*100
        base=ticker_yf.replace('.BK','')
        return {"Ticker":base,"VI Score":round(overall,1),"Verdict":verdict,
                "Rev CAGR%":cagr,"ROE%":roe,"D/E":de,
                "P/E":round(float(pe),1) if pe else None,
                "Div%":round(dy,1) if dy else None,
                "M-Score":round(m,2) if m else None,
                "FCF+":fcf_ok,
                "A%":round(sec_sc.get('A',(0,0,0))[2]),"B%":round(sec_sc.get('B',(0,0,0))[2]),
                "C%":round(sec_sc.get('C',(0,0,0))[2]),"D%":round(sec_sc.get('D',(0,0,0))[2]),
                "E%":round(sec_sc.get('E',(0,0,0))[2])}
    except Exception as e:
        return {"Ticker":ticker_yf.replace('.BK',''),"VI Score":0,"Verdict":f"Error",
                "Rev CAGR%":None,"ROE%":None,"D/E":None,"P/E":None,"Div%":None,
                "M-Score":None,"FCF+":False,"A%":0,"B%":0,"C%":0,"D%":0,"E%":0}

def show_screener_tab():
    st.markdown("### 🔍 Stock Screener")
    st.caption("Batch-runs the full VI scorecard across your selected universe. Shows ranked results.")
    c1,c2,c3=st.columns([2,2,1])
    with c1:
        universe=st.selectbox("Universe",["SET100","MAI","SET100 + MAI"],key="scr_uni")
    with c2:
        sectors=["All Sectors"]+sorted(SECTOR_MAP.keys())
        sector_f=st.selectbox("Filter by Sector",sectors,key="scr_sec")
    with c3:
        min_score=st.number_input("Min VI Score%",0,100,0,5,key="scr_min")

    run=st.button("▶ Run Screener",type="primary",use_container_width=True)
    if not run and "screener_results" not in st.session_state:
        st.info("Select universe and click **Run Screener** to batch-analyse all tickers.")
        return
    if run:
        if universe=="SET100":      pool=SET100
        elif universe=="MAI":        pool=MAI_TICKERS
        else:                        pool=SET100+MAI_TICKERS
        if sector_f!="All Sectors":
            sector_set=set(SECTOR_MAP.get(sector_f,[]))
            pool=[t for t in pool if t in sector_set]
        if not pool: st.warning("No tickers match filter."); return
        results=[]
        bar=st.progress(0,text=f"Analysing {pool[0]}…")
        for i,t in enumerate(pool):
            bar.progress((i+1)/len(pool),text=f"Analysing {t} ({i+1}/{len(pool)})…")
            results.append(compute_quick_score(to_yf(t)))
        bar.empty()
        st.session_state["screener_results"]=results
        st.session_state["screener_label"]=f"{universe} · {sector_f} · min {min_score}%"

    if "screener_results" not in st.session_state: return
    results=st.session_state["screener_results"]
    df=pd.DataFrame(results)
    df=df[df["VI Score"]>=min_score].sort_values("VI Score",ascending=False).reset_index(drop=True)
    st.caption(f"**{len(df)} results** — {st.session_state.get('screener_label','')}")

    # Color verdict
    def color_verdict(v):
        if "✅" in v: return "color:#4ecca3;font-weight:bold"
        if "🚨" in v: return "color:#ef5350;font-weight:bold"
        if "⚠️" in v: return "color:#f0c040"
        return "color:#aaa"

    st.dataframe(
        df,
        column_config={
            "Ticker":     st.column_config.TextColumn("Ticker",width=70),
            "VI Score":   st.column_config.ProgressColumn("VI Score",min_value=0,max_value=100,format="%.0f%%",width=110),
            "Verdict":    st.column_config.TextColumn("Verdict",width=160),
            "Rev CAGR%":  st.column_config.NumberColumn("Rev CAGR%",format="%.1f%%"),
            "ROE%":       st.column_config.NumberColumn("ROE%",format="%.1f%%"),
            "D/E":        st.column_config.NumberColumn("D/E",format="%.2f×"),
            "P/E":        st.column_config.NumberColumn("P/E",format="%.1f×"),
            "Div%":       st.column_config.NumberColumn("Div%",format="%.1f%%"),
            "M-Score":    st.column_config.NumberColumn("Beneish M",format="%.2f"),
            "FCF+":       st.column_config.CheckboxColumn("FCF+"),
            "A%":         st.column_config.ProgressColumn("Quality",min_value=0,max_value=100,format="%.0f%%",width=80),
            "B%":         st.column_config.ProgressColumn("Health",min_value=0,max_value=100,format="%.0f%%",width=80),
            "C%":         st.column_config.ProgressColumn("Integrity",min_value=0,max_value=100,format="%.0f%%",width=80),
            "D%":         st.column_config.ProgressColumn("Fraud",min_value=0,max_value=100,format="%.0f%%",width=80),
            "E%":         st.column_config.ProgressColumn("Value",min_value=0,max_value=100,format="%.0f%%",width=80),
        },
        use_container_width=True, height=500, hide_index=True
    )
    # Drill-down
    st.markdown("---")
    drill=st.selectbox("🔎 Drill into ticker for full analysis",
                       [""]+df["Ticker"].tolist(), key="scr_drill")
    if drill:
        dtabs=st.tabs(["📈 Price","📋 Financials","📊 Trends","⚖️ VI Score","📰 News"])
        with dtabs[0]:
            with st.spinner(f"Loading {drill}…"):
                fig=make_price_chart(to_yf(drill),"2021-01-01")
                st.pyplot(fig); plt.close(fig)
        with dtabs[1]:
            d=fetch_all(to_yf(drill))
            st.markdown(_df_to_html(d['income'],"Income Statement"),unsafe_allow_html=True)
            st.markdown(_df_to_html(d['balance'],"Balance Sheet"),unsafe_allow_html=True)
            st.markdown(_df_to_html(d['cashflow'],"Cash Flow"),unsafe_allow_html=True)
        with dtabs[2]:
            with st.spinner("Plotting…"):
                fig=make_fundamental_chart(to_yf(drill))
                st.pyplot(fig); plt.close(fig)
        with dtabs[3]:
            with st.spinner("Computing…"):
                render_vi_scorecard_st(compute_vi_scorecard(to_yf(drill)))
        with dtabs[4]:
            with st.spinner("Fetching news…"):
                render_news_st(to_yf(drill), fetch_all_news(to_yf(drill)))

# ─── Main app ───────────────────────────────────────────────────────────────────
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("<h2 style='color:#00d4ff;margin:0 0 4px'>🏦 SET Analyser</h2>",unsafe_allow_html=True)
        st.caption("Value Investor Edition · H1 2025")
        st.markdown("---")
        st.markdown("**📅 Date Range**")
        start_year=st.selectbox("Start Year",[str(y) for y in range(2015,2026)],index=6,key="sy")
        start_month=st.selectbox("Start Month",[f"{m:02d}" for m in range(1,13)],index=0,key="sm")
        start=f"{start_year}-{start_month}-01"
        st.markdown("---")

        st.markdown("<span style='color:#00d4ff;font-weight:bold'>SET100</span>",unsafe_allow_html=True)
        all_set=st.checkbox("Select All SET100",key="all_set")
        set_search=st.text_input("Filter SET100","",placeholder="e.g. KBANK",key="ss")
        set_filtered=[t for t in SET100 if set_search.upper() in t]
        set_selected=[t for t in set_filtered if st.checkbox(t,value=all_set,key=f"s_{t}")]

        st.markdown("---")
        st.markdown("<span style='color:#4ecca3;font-weight:bold'>MAI</span>",unsafe_allow_html=True)
        all_mai=st.checkbox("Select All MAI",key="all_mai")
        mai_search=st.text_input("Filter MAI","",placeholder="e.g. BBGI",key="ms")
        mai_filtered=[t for t in MAI_TICKERS if mai_search.upper() in t]
        mai_selected=[t for t in mai_filtered if st.checkbox(t,value=all_mai,key=f"m_{t}")]

        st.markdown("---")
        st.markdown("<span style='color:#f0c040;font-weight:bold'>DR / ETF</span>",unsafe_allow_html=True)
        all_dr=st.checkbox("Select All DR",key="all_dr")
        dr_selected=[t for t in DR_TICKERS if st.checkbox(t,value=all_dr,key=f"d_{t}")]

        selected_base=set_selected+mai_selected+dr_selected
        selected=[to_yf(t) for t in selected_base]
        if selected:
            st.markdown(f"<div style='background:#0e2040;border-radius:6px;padding:8px;margin-top:8px'>"
                        f"<span style='color:#4ecca3;font-weight:bold'>{len(selected)} selected</span><br>"
                        f"<span style='color:#aaa;font-size:11px'>{', '.join(selected_base[:8])}"
                        f"{'…' if len(selected_base)>8 else ''}</span></div>",unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🗑 Clear Cache",help="Force refresh all data"):
            st.cache_data.clear(); st.rerun()

    # Tabs
    tab_names=["🔍 Screener","📈 Price Charts","📋 Financials","📊 Fundamentals","⚖️ VI Scorecard","📰 News Scan"]
    tabs=st.tabs(tab_names)

    with tabs[0]:
        show_screener_tab()

    with tabs[1]:
        if not selected: st.info("Select tickers in the sidebar."); 
        else:
            for ticker in selected:
                with st.spinner(f"Loading {ticker}…"):
                    fig=make_price_chart(ticker,start)
                    st.pyplot(fig); plt.close(fig)

    with tabs[2]:
        if not selected: st.info("Select tickers in the sidebar.")
        else:
            for ticker in selected:
                d=fetch_all(ticker); base=ticker.replace('.BK','')
                st.markdown(f"<h4 style='color:#00d4ff'>📋 {base} — Financial Statements</h4>",unsafe_allow_html=True)
                st.markdown(_df_to_html(d['income'],"Income Statement (Annual)"),unsafe_allow_html=True)
                st.markdown(_df_to_html(d['balance'],"Balance Sheet (Annual)"),unsafe_allow_html=True)
                st.markdown(_df_to_html(d['cashflow'],"Cash Flow (Annual)"),unsafe_allow_html=True)
                st.markdown("<hr style='border-color:#1e3a5f'>",unsafe_allow_html=True)

    with tabs[3]:
        if not selected: st.info("Select tickers in the sidebar.")
        else:
            for ticker in selected:
                with st.spinner(f"Plotting {ticker}…"):
                    fig=make_fundamental_chart(ticker)
                    st.pyplot(fig); plt.close(fig)

    with tabs[4]:
        if not selected: st.info("Select tickers in the sidebar.")
        else:
            for ticker in selected:
                with st.spinner(f"Scoring {ticker}…"):
                    render_vi_scorecard_st(compute_vi_scorecard(ticker))
                    st.markdown("<div style='height:3px;background:linear-gradient(to right,#0e2040,#00d4ff,#0e2040);margin:16px 0;border-radius:2px'></div>",unsafe_allow_html=True)

    with tabs[5]:
        if not selected: st.info("Select tickers in the sidebar.")
        else:
            for ticker in selected:
                with st.spinner(f"Scanning news for {ticker}…"):
                    render_news_st(ticker, fetch_all_news(ticker))
                    st.markdown("<div style='height:2px;background:#1e3a5f;margin:12px 0'></div>",unsafe_allow_html=True)

main()
