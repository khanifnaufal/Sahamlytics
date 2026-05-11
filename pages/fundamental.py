import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_stock_info, IHSG_STOCKS, get_logo_url


def gauge_chart(value, title, min_val, max_val, thresholds, colors):
    """Mini gauge chart untuk rasio keuangan."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 12, "color": "#90a4ae", "family": "Space Mono"}},
        number={"font": {"size": 18, "color": "#e8eaf6", "family": "Space Mono"}},
        gauge={
            "axis": {"range": [min_val, max_val], "tickcolor": "#546e7a", "tickfont": {"size": 9}},
            "bar": {"color": "#00e5ff", "thickness": 0.25},
            "bgcolor": "#111827",
            "borderwidth": 0,
            "steps": [
                {"range": [thresholds[0], thresholds[1]], "color": colors[0]},
                {"range": [thresholds[1], thresholds[2]], "color": colors[1]},
                {"range": [thresholds[2], max_val], "color": colors[2]},
            ],
        }
    ))
    fig.update_layout(
        height=160, margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="#0a0e1a", font_color="#90a4ae"
    )
    return fig


def render():
    st.markdown('<div class="main-header">📋 FUNDAMENTAL</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">// analisa kesehatan keuangan emiten</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        ticker = st.selectbox(
            "Pilih Saham",
            options=list(IHSG_STOCKS.keys()),
            format_func=lambda x: f"{x.replace('.JK','')} — {IHSG_STOCKS[x]}",
        )

    with st.spinner("Mengambil data fundamental..."):
        info = get_stock_info(ticker)

    if not info:
        st.error("Gagal mengambil data fundamental.")
        return

    # ── Header Perusahaan ─────────────────────────────────────────────────────
    name     = info.get("longName", ticker)
    sector   = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    market_cap = info.get("marketCap", 0)
    currency = info.get("currency", "IDR")
    website  = info.get("website", "")

    logo_url = get_logo_url(website)
    logo_html = f'<img src="{logo_url}" width="50" style="border-radius:8px; margin-right:16px;">' if logo_url else ''

    mc_str = f"Rp {market_cap/1e12:.2f}T" if market_cap > 1e12 else f"Rp {market_cap/1e9:.1f}M" if market_cap else "N/A"

    st.markdown(f"""
<div style="background:#111827;border:1px solid #1e293b;border-radius:12px;
            padding:20px 24px;margin-bottom:20px;display:flex;align-items:center;">
    {logo_html}
    <div>
        <div style="font-family:'Space Mono',monospace;font-size:22px;font-weight:700;color:#00e5ff;">
            {ticker.replace('.JK','')}
        </div>
        <div style="font-size:16px;color:#e8eaf6;margin:4px 0;">{name}</div>
        <div style="font-size:13px;color:#546e7a;">{sector} · {industry}</div>
    </div>
</div>
<div style="background:#111827;border:1px solid #1e293b;border-radius:12px;
            padding:16px 24px;margin-bottom:20px;">
    <div style="display:flex;gap:24px;flex-wrap:wrap;">
        <div>
            <div style="font-size:11px;color:#546e7a;">Market Cap</div>
            <div style="font-size:16px;font-weight:600;color:#e8eaf6;font-family:'Space Mono',monospace;">{mc_str}</div>
        </div>
        <div>
            <div style="font-size:11px;color:#546e7a;">Mata Uang</div>
            <div style="font-size:16px;font-weight:600;color:#e8eaf6;font-family:'Space Mono',monospace;">{currency}</div>
        </div>
        {'<div><a href="' + website + '" target="_blank" style="font-size:12px;color:#00e5ff;">' + website + '</a></div>' if website else ''}
    </div>
</div>
""", unsafe_allow_html=True)

    # ── Rasio Valuasi ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">// VALUASI</div>', unsafe_allow_html=True)

    per    = info.get("trailingPE")
    fpe    = info.get("forwardPE")
    pbv    = info.get("priceToBook")
    ps     = info.get("priceToSalesTrailing12Months")
    ev_eb  = info.get("enterpriseToEbitda")
    dy     = info.get("dividendYield", 0) or 0

    v1, v2, v3, v4, v5, v6 = st.columns(6)
    def fmt(val, suffix="x", digits=1): return f"{val:.{digits}f}{suffix}" if val else "N/A"

    with v1: st.metric("PER (Trailing)", fmt(per))
    with v2: st.metric("PER (Forward)", fmt(fpe))
    with v3: st.metric("PBV", fmt(pbv, "x", 2))
    with v4: st.metric("P/S Ratio", fmt(ps))
    with v5: st.metric("EV/EBITDA", fmt(ev_eb))
    with v6: st.metric("Dividend Yield", f"{dy*100:.2f}%" if dy else "N/A")

    # PER gauge
    if per:
        g1, g2, g3 = st.columns(3)
        with g1:
            fig_per = gauge_chart(
                min(per, 40), "PER", 0, 40,
                [0, 10, 20, 40],
                ["rgba(0,0,0,0)", "rgba(0, 200, 83, 0.2)", "rgba(255, 23, 68, 0.2)"]
            )
            st.plotly_chart(fig_per, use_container_width=True, config={"displayModeBar":False})
            st.markdown('<div style="text-align:center;font-size:11px;color:#546e7a;">< 10 = murah · 10-20 = wajar · >20 = mahal</div>', unsafe_allow_html=True)
        with g2:
            if pbv:
                fig_pbv = gauge_chart(
                    min(pbv, 5), "PBV", 0, 5,
                    [0, 1, 2, 5],
                    ["rgba(0,0,0,0)", "rgba(0, 200, 83, 0.2)", "rgba(255, 23, 68, 0.2)"]
                )
                st.plotly_chart(fig_pbv, use_container_width=True, config={"displayModeBar":False})
                st.markdown('<div style="text-align:center;font-size:11px;color:#546e7a;">< 1 = undervalue · 1-2 = wajar · >2 = mahal</div>', unsafe_allow_html=True)

    # ── Profitabilitas ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">// PROFITABILITAS</div>', unsafe_allow_html=True)

    roe    = info.get("returnOnEquity", 0) or 0
    roa    = info.get("returnOnAssets", 0) or 0
    npm    = info.get("profitMargins", 0) or 0
    gpm    = info.get("grossMargins", 0) or 0
    opm    = info.get("operatingMargins", 0) or 0
    rev    = info.get("totalRevenue", 0) or 0
    earn   = info.get("netIncomeToCommon", 0) or 0
    eg     = info.get("earningsGrowth", 0) or 0
    rg     = info.get("revenueGrowth", 0) or 0

    p1, p2, p3, p4, p5 = st.columns(5)
    with p1: st.metric("ROE", f"{roe*100:.1f}%", "✓ Bagus" if roe > 0.15 else "⚠ Rendah" if roe > 0 else "❌ Rugi")
    with p2: st.metric("ROA", f"{roa*100:.1f}%")
    with p3: st.metric("Net Profit Margin", f"{npm*100:.1f}%")
    with p4: st.metric("Earnings Growth", f"{eg*100:.1f}%" if eg else "N/A", "YoY")
    with p5: st.metric("Revenue Growth", f"{rg*100:.1f}%" if rg else "N/A", "YoY")

    rev_str  = f"Rp {rev/1e12:.2f}T" if rev > 1e12 else f"Rp {rev/1e9:.1f}M" if rev else "N/A"
    earn_str = f"Rp {earn/1e12:.2f}T" if earn and abs(earn) > 1e12 else f"Rp {earn/1e9:.1f}M" if earn else "N/A"

    st.markdown(f"""
<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:8px;">
    <div style="flex:1;min-width:200px;background:#111827;border:1px solid #1e293b;border-radius:8px;padding:14px;">
        <div style="font-size:11px;color:#546e7a;">Total Revenue (TTM)</div>
        <div style="font-size:20px;font-weight:700;color:#e8eaf6;font-family:'Space Mono',monospace;">{rev_str}</div>
    </div>
    <div style="flex:1;min-width:200px;background:#111827;border:1px solid #1e293b;border-radius:8px;padding:14px;">
        <div style="font-size:11px;color:#546e7a;">Net Income (TTM)</div>
        <div style="font-size:20px;font-weight:700;font-family:'Space Mono',monospace;
                    color:{'#00e676' if (earn or 0)>0 else '#ff1744'};">{earn_str}</div>
    </div>
    <div style="flex:1;min-width:200px;background:#111827;border:1px solid #1e293b;border-radius:8px;padding:14px;">
        <div style="font-size:11px;color:#546e7a;">Gross Margin</div>
        <div style="font-size:20px;font-weight:700;color:#e8eaf6;font-family:'Space Mono',monospace;">{gpm*100:.1f}%</div>
    </div>
    <div style="flex:1;min-width:200px;background:#111827;border:1px solid #1e293b;border-radius:8px;padding:14px;">
        <div style="font-size:11px;color:#546e7a;">Operating Margin</div>
        <div style="font-size:20px;font-weight:700;color:#e8eaf6;font-family:'Space Mono',monospace;">{opm*100:.1f}%</div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── Solvabilitas ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">// SOLVABILITAS & LIKUIDITAS</div>', unsafe_allow_html=True)

    de      = info.get("debtToEquity", 0) or 0
    cr      = info.get("currentRatio", 0) or 0
    qr      = info.get("quickRatio", 0) or 0
    fcf     = info.get("freeCashflow", 0) or 0
    op_cf   = info.get("operatingCashflow", 0) or 0
    total_d = info.get("totalDebt", 0) or 0
    total_c = info.get("totalCash", 0) or 0

    s1, s2, s3, s4 = st.columns(4)
    with s1: st.metric("DER", f"{de/100:.2f}x" if de else "N/A", "✓ Aman" if de < 150 else "⚠ Tinggi")
    with s2: st.metric("Current Ratio", f"{cr:.2f}x" if cr else "N/A", "✓ Likuid" if cr > 1.5 else "⚠ Ketat")
    with s3: st.metric("Quick Ratio", f"{qr:.2f}x" if qr else "N/A")
    with s4:
        fcf_str = f"Rp {fcf/1e12:.2f}T" if fcf and abs(fcf) > 1e12 else f"Rp {fcf/1e9:.1f}M" if fcf else "N/A"
        st.metric("Free Cash Flow", fcf_str, "✓ Positif" if (fcf or 0) > 0 else "⚠ Negatif")

    # ── Penilaian akhir ───────────────────────────────────────────────────────
    st.markdown('<div class="section-title">// SCORECARD FUNDAMENTAL</div>', unsafe_allow_html=True)

    score_items = [
        ("ROE > 15%",     (roe or 0) > 0.15,     "Profitabilitas tinggi"),
        ("DER < 1.5x",    (de or 999)/100 < 1.5,  "Utang terkendali"),
        ("Current Ratio > 1.5x", (cr or 0) > 1.5, "Likuiditas sehat"),
        ("Net Margin > 10%",  (npm or 0) > 0.10,  "Margin laba wajar"),
        ("FCF Positif",   (fcf or 0) > 0,          "Arus kas positif"),
        ("PBV < 3x",      (pbv or 99) < 3,         "Valuasi tidak terlalu mahal"),
        ("Earnings Growth +", (eg or 0) > 0,        "Laba sedang tumbuh"),
    ]

    passed = sum(1 for _, ok, _ in score_items if ok)
    total  = len(score_items)

    overall = "🟢 FUNDAMENTAL KUAT" if passed >= 5 else "🟡 FUNDAMENTAL CUKUP" if passed >= 3 else "🔴 FUNDAMENTAL LEMAH"

    st.markdown(f"""
<div style="background:#111827;border:1px solid #1e293b;border-radius:12px;padding:20px 24px;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
        <div style="font-size:16px;font-weight:500;color:#e8eaf6;">{overall}</div>
        <div style="font-family:'Space Mono',monospace;font-size:24px;font-weight:700;color:#00e5ff;">{passed}/{total}</div>
    </div>
    {''.join(f'<div style="display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid #1e293b;"><span style="font-size:16px;">{"✅" if ok else "❌"}</span><div style="flex:1;font-size:13px;color:#{"e8eaf6" if ok else "546e7a"};">{label}</div><div style="font-size:12px;color:#37474f;">{desc}</div></div>' for label, ok, desc in score_items)}
</div>
""", unsafe_allow_html=True)


    # Business summary
    summary = info.get("longBusinessSummary", "")
    if summary:
        st.markdown('<div class="section-title">// TENTANG PERUSAHAAN</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div style="background:#111827;border:1px solid #1e293b;border-radius:8px;padding:16px 20px;
            font-size:13px;color:#78909c;line-height:1.8;">
    {summary[:600]}{'...' if len(summary) > 600 else ''}
</div>
""", unsafe_allow_html=True)
