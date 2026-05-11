import streamlit as st
print("DEBUG: DASHBOARD.PY LOADING...")
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys, os
try:
    from google import genai
except ImportError:
    genai = None
import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_price_data, calc_indicators, generate_signal, get_stock_info, IHSG_STOCKS, get_logo_url


def render():
    st.markdown('<div class="main-header">📊 DASHBOARD</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">// analisa teknikal real-time</div>', unsafe_allow_html=True)

    # ── Controls ──────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    with col1:
        raw_ticker = st.text_input("Kode Saham (contoh: BBCA, GOTO)", value="BBCA").upper().strip()
        ticker_display = raw_ticker if raw_ticker.endswith(".JK") else raw_ticker + ".JK"
    with col2:
        trading_style = st.selectbox("Gaya Trading", 
                                     ["Scalping (5m)", "Day-Trade (15m)", "Swing (1d)", 
                                      "Beli Pagi - Jual Sore", "Beli Sore - Jual Pagi"], 
                                     index=1)
    with col3:
        chart_type = st.selectbox("Tipe Chart", ["Candlestick","Line"])

    if "Scalping" in trading_style:
        period = "5d"
        interval = "5m"
    elif "Day-Trade" in trading_style or "Beli Pagi" in trading_style:
        period = "1mo"
        interval = "15m"
    elif "Beli Sore" in trading_style:
        period = "1mo"
        interval = "30m"
    else:
        period = "6mo"
        interval = "1d"

    # ── Fetch & Kalkulasi ─────────────────────────────────────────────────────
    with st.spinner(f"Mengambil data {ticker_display}..."):
        df = get_price_data(ticker_display, period=period, interval=interval)
        if df.empty:
            st.error(f"❌ Gagal mengambil data untuk {ticker_display}. Pastikan kode saham benar atau coba lagi nanti.")
            return
        df = calc_indicators(df)
        sig = generate_signal(df)
        info = get_stock_info(ticker_display)

    logo_url = get_logo_url(info.get("website", ""))
    logo_html = f'<img src="{logo_url}" width="40" style="border-radius:4px; margin-right:12px; vertical-align:middle;">' if logo_url else ''
    
    name = info.get("longName", ticker_display)
    st.markdown(f"""
    <div style="background:#111827;border:1px solid #1e293b;border-radius:8px;
                padding:12px 20px;margin-bottom:16px;display:flex;align-items:center;">
        {logo_html}
        <div>
            <span style="font-family:'Space Mono',monospace;font-size:20px;font-weight:700;color:#00e5ff;">{ticker_display.replace('.JK','')}</span>
            <span style="font-size:14px;color:#90a4ae;margin-left:8px;">{name}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if len(df) < 2:
        st.warning("⚠️ Data historis tidak cukup untuk analisa teknikal.")
        return

    latest = df.iloc[-1]
    prev   = df.iloc[-2]
    close  = float(latest["Close"])
    chg    = close - float(prev["Close"])
    chg_pct = (chg / float(prev["Close"])) * 100 if float(prev["Close"]) != 0 else 0

    # ── Metrics row ───────────────────────────────────────────────────────────
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Harga Terakhir", f"Rp {close:,.0f}", f"{chg_pct:+.2f}%")
    with m2:
        if "RSI" in latest and not pd.isna(latest["RSI"]):
            rsi_val = float(latest["RSI"])
            st.metric("RSI (14)", f"{rsi_val:.1f}",
                      "Oversold" if rsi_val < 30 else "Overbought" if rsi_val > 70 else "Normal")
        else:
            st.metric("RSI (14)", "N/A", "Data kurang")
    with m3:
        vol_ratio = sig.get("vol_ratio", 1.0)
        st.metric("Volume / MA20", f"{vol_ratio:.2f}x", "Tinggi" if vol_ratio > 1.5 else "Normal")
    with m4:
        if "ATR" in latest and not pd.isna(latest["ATR"]):
            atr = float(latest["ATR"])
            st.metric("ATR (14)", f"Rp {atr:,.0f}", "Volatilitas harian")
        else:
            st.metric("ATR (14)", "N/A", "Data kurang")
    with m5:
        score = sig.get("score", 0)
        st.metric("Signal Score", f"{score:+.0f}", sig.get("signal", "N/A"))

    st.markdown("---")

    # ── Signal Box ────────────────────────────────────────────────────────────
    signal = sig.get("signal", "HOLD")
    sc1, sc2, sc3 = st.columns([1, 1, 1])
    with sc1:
        st.markdown(f'<div class="signal-{signal}">⬤ {signal}</div>', unsafe_allow_html=True)
    with sc2:
        sl = sig.get("sl")
        tp = sig.get("tp")
        if sl:
            st.markdown(f"""
            <div style="background:#111827;border:1px solid #1e293b;border-radius:8px;padding:10px 16px;text-align:center;">
                <div style="font-size:11px;color:#546e7a;font-family:'Space Mono',monospace;">STOP LOSS</div>
                <div style="font-size:20px;font-weight:700;color:#ff1744;font-family:'Space Mono',monospace;">Rp {sl:,.0f}</div>
                <div style="font-size:11px;color:#37474f;">({((sl-close)/close*100):+.1f}%)</div>
            </div>""", unsafe_allow_html=True)
    with sc3:
        if tp:
            st.markdown(f"""
            <div style="background:#111827;border:1px solid #1e293b;border-radius:8px;padding:10px 16px;text-align:center;">
                <div style="font-size:11px;color:#546e7a;font-family:'Space Mono',monospace;">TAKE PROFIT</div>
                <div style="font-size:20px;font-weight:700;color:#00e676;font-family:'Space Mono',monospace;">Rp {tp:,.0f}</div>
                <div style="font-size:11px;color:#37474f;">({((tp-close)/close*100):+.1f}%)</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">// CHART TEKNIKAL</div>', unsafe_allow_html=True)

    # ── Chart ─────────────────────────────────────────────────────────────────
    show_ma   = st.checkbox("Moving Average", value=True)
    show_bb   = st.checkbox("Bollinger Bands", value=True)
    show_vol  = st.checkbox("Volume", value=True)
    show_macd = st.checkbox("MACD", value=True)
    show_rsi  = st.checkbox("RSI", value=True)

    # Tentukan subplot rows
    rows = 1
    row_heights = [0.5]
    if show_vol:  rows += 1; row_heights.append(0.15)
    if show_macd: rows += 1; row_heights.append(0.15)
    if show_rsi:  rows += 1; row_heights.append(0.15)

    specs = [[{"secondary_y": False}]] * rows
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, row_heights=row_heights, specs=specs)

    curr_row = 1

    # Candlestick / Line
    if chart_type == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
            name="OHLC",
            increasing_line_color="#00e676", decreasing_line_color="#ff1744",
            increasing_fillcolor="#00e676", decreasing_fillcolor="#ff1744"
        ), row=curr_row, col=1)
    else:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Close"], name="Close",
            line=dict(color="#00e5ff", width=1.5)
        ), row=curr_row, col=1)

    # Moving Averages
    if show_ma:
        for col_name, color, label in [
            ("MA20","#ffeb3b","MA20"), ("MA50","#ff9800","MA50"), ("MA200","#e91e63","MA200")
        ]:
            if col_name in df.columns:
                fig.add_trace(go.Scatter(
                    x=df.index, y=df[col_name], name=label,
                    line=dict(color=color, width=1, dash="dot"), opacity=0.8
                ), row=curr_row, col=1)

    # Bollinger Bands
    if show_bb and "BB_upper" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_upper"], name="BB Upper",
            line=dict(color="#7c4dff", width=1, dash="dash"), opacity=0.5
        ), row=curr_row, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_lower"], name="BB Lower",
            line=dict(color="#7c4dff", width=1, dash="dash"),
            fill="tonexty", fillcolor="rgba(124,77,255,0.05)", opacity=0.5
        ), row=curr_row, col=1)

    # Signal markers
    fig.add_trace(go.Scatter(
        x=[df.index[-1]], y=[close],
        mode="markers+text",
        marker=dict(
            color="#00e676" if signal=="BUY" else "#ff1744" if signal=="SELL" else "#ffd600",
            size=12, symbol="diamond"
        ),
        text=[signal], textposition="top center",
        textfont=dict(color="#ffffff", size=11),
        name="Signal"
    ), row=curr_row, col=1)

    # Stop Loss & Take Profit lines
    if sl:
        fig.add_hline(y=sl, line_color="#ff1744", line_dash="dash", line_width=1,
                      annotation_text=f"SL: {sl:,.0f}", annotation_position="right",
                      row=curr_row, col=1)
    if tp:
        fig.add_hline(y=tp, line_color="#00e676", line_dash="dash", line_width=1,
                      annotation_text=f"TP: {tp:,.0f}", annotation_position="right",
                      row=curr_row, col=1)

    # Volume
    if show_vol:
        curr_row += 1
        colors = ["#00e676" if float(df["Close"].iloc[i]) >= float(df["Open"].iloc[i]) else "#ff1744"
                  for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=df.index, y=df["Volume"], name="Volume",
            marker_color=colors, opacity=0.7
        ), row=curr_row, col=1)
        if "Vol_MA20" in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, y=df["Vol_MA20"], name="Vol MA20",
                line=dict(color="#ffeb3b", width=1)
            ), row=curr_row, col=1)

    # MACD
    if show_macd and "MACD" in df.columns:
        curr_row += 1
        hist_colors = ["#00e676" if v >= 0 else "#ff1744" for v in df["MACD_hist"].fillna(0)]
        fig.add_trace(go.Bar(
            x=df.index, y=df["MACD_hist"], name="MACD Hist",
            marker_color=hist_colors, opacity=0.6
        ), row=curr_row, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["MACD"], name="MACD",
            line=dict(color="#00e5ff", width=1.2)
        ), row=curr_row, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["MACD_signal"], name="Signal",
            line=dict(color="#ff9800", width=1.2)
        ), row=curr_row, col=1)
        fig.add_hline(y=0, line_color="#37474f", line_width=1, row=curr_row, col=1)

    # RSI
    if show_rsi and "RSI" in df.columns:
        curr_row += 1
        fig.add_trace(go.Scatter(
            x=df.index, y=df["RSI"], name="RSI",
            line=dict(color="#e040fb", width=1.5)
        ), row=curr_row, col=1)
        fig.add_hline(y=70, line_color="#ff1744", line_dash="dash", line_width=1, row=curr_row, col=1)
        fig.add_hline(y=30, line_color="#00e676", line_dash="dash", line_width=1, row=curr_row, col=1)
        fig.add_hline(y=50, line_color="#37474f", line_width=0.5, row=curr_row, col=1)

    fig.update_layout(
        height=680,
        paper_bgcolor="#0a0e1a",
        plot_bgcolor="#0d1117",
        font=dict(color="#90a4ae", family="Space Mono", size=11),
        xaxis_rangeslider_visible=False,
        legend=dict(bgcolor="#111827", bordercolor="#1e293b", borderwidth=1, font=dict(size=10)),
        margin=dict(l=10, r=60, t=20, b=10),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#111827", bordercolor="#1e293b", font=dict(color="#e8eaf6")),
    )
    fig.update_xaxes(gridcolor="#1e293b", zeroline=False, showspikes=True, spikecolor="#546e7a")
    fig.update_yaxes(gridcolor="#1e293b", zeroline=False)

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Signal Details ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">// DETAIL SINYAL</div>', unsafe_allow_html=True)

    details = sig.get("details", [])
    for name, bullish, weight, desc in details:
        if weight == 0:
            icon = "⚪"
            color = "#546e7a"
        elif bullish:
            icon = "🟢"
            color = "#00e676"
        else:
            icon = "🔴"
            color = "#ff1744"

        strength = "●" * weight + "○" * (3 - weight)
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;padding:8px 12px;
            background:#111827;border-radius:8px;margin-bottom:6px;
            border-left:3px solid {color}">
    <span style="font-size:16px">{icon}</span>
    <div style="flex:1">
        <span style="font-size:13px;color:#e8eaf6;">{desc}</span>
    </div>
    <span style="font-size:12px;color:#546e7a;font-family:'Space Mono',monospace;">{strength}</span>
</div>
""", unsafe_allow_html=True)

    # Skor akhir
    bull = sig.get("bull_pts", 0)
    bear = sig.get("bear_pts", 0)
    score = sig.get("score", 0)
    st.markdown(f"""
<div style="margin-top:16px;padding:16px 20px;background:#111827;
            border:1px solid #1e293b;border-radius:12px;
            display:flex;justify-content:space-between;align-items:center;">
    <div style="text-align:center;">
        <div style="font-size:11px;color:#546e7a;font-family:'Space Mono',monospace;">BULL POINTS</div>
        <div style="font-size:24px;font-weight:700;color:#00e676;font-family:'Space Mono',monospace;">+{bull}</div>
    </div>
    <div style="text-align:center;">
        <div style="font-size:11px;color:#546e7a;font-family:'Space Mono',monospace;">BEAR POINTS</div>
        <div style="font-size:24px;font-weight:700;color:#ff1744;font-family:'Space Mono',monospace;">-{bear}</div>
    </div>
    <div style="text-align:center;">
        <div style="font-size:11px;color:#546e7a;font-family:'Space Mono',monospace;">NET SCORE</div>
        <div style="font-size:28px;font-weight:700;font-family:'Space Mono',monospace;
                    color:{'#00e676' if score>0 else '#ff1744' if score<0 else '#ffd600'}">
            {score:+.0f}
        </div>
    </div>
    <div style="text-align:center;">
        <div style="font-size:11px;color:#546e7a;font-family:'Space Mono',monospace;">KEPUTUSAN</div>
        <div style="font-size:24px;font-weight:700;font-family:'Space Mono',monospace;
                    color:{'#00e676' if signal=='BUY' else '#ff1744' if signal=='SELL' else '#ffd600'}">
            {signal}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── AI Analyst (Gemini) ───────────────────────────────────────────────────
    st.markdown('<div class="section-title">// 🤖 AI ANALYST (EXPERIMENTAL)</div>', unsafe_allow_html=True)
    with st.expander("Minta Pendapat AI tentang Saham ini"):
        if not genai:
            st.error("Library google-genai belum terinstall.")
        else:
            api_key = st.text_input("Google Gemini API Key", type="password", help="Dapatkan dari Google AI Studio")
            if st.button("Analisa dengan AI", type="primary"):
                if not api_key:
                    st.warning("Silakan masukkan API Key terlebih dahulu.")
                else:
                    try:
                        client = genai.Client(api_key=api_key)
                        model_id = 'gemini-flash-latest'
                        now_wib = datetime.datetime.now().strftime('%H:%M WIB')
                        
                        prompt = f"""
                        # PERAN: Antigravity - Senior Trader IHSG
                        Gaya: 1. Day Trading (Pagi-Sore) | 2. Overnight (Sore-Pagi)
                        
                        KONTEKS:
                        - Saham: {ticker_display} | Harga: {close} | Waktu: {now_wib}
                        - VWAP: {float(latest.get('VWAP', 0)):.2f} | EMA9/20: {float(latest.get('EMA9', 0)):.2f}/{float(latest.get('EMA20', 0)):.2f}
                        - RSI: {float(latest.get('RSI', 0)):.1f} | Stochastic: {float(latest.get('Stoch_K', 0)):.1f}/{float(latest.get('Stoch_D', 0)):.1f}
                        - Camarilla: H4={float(latest.get('H4', 0)):.0f}, H3={float(latest.get('H3', 0)):.0f}, L3={float(latest.get('L3', 0)):.0f}
                        - ORB 30m: {float(latest.get('ORB_High', 0)):.0f} - {float(latest.get('ORB_Low', 0)):.0f}
                        
                        Berikan respon singkat, actionable, dengan level Entry, SL, Target (bullet points).
                        Tandai sinyal: ✅ (kuat) / ⚠️ (lemah).
                        """
                        
                        with st.spinner("Antigravity sedang menganalisa (mungkin butuh beberapa saat jika antrian penuh)..."):
                            import time
                            max_retries = 3
                            for i in range(max_retries):
                                try:
                                    response = client.models.generate_content(
                                        model=model_id,
                                        contents=prompt
                                    )
                                    st.info(response.text)
                                    break
                                except Exception as e:
                                    if "429" in str(e) and i < max_retries - 1:
                                        time.sleep(5)
                                        continue
                                    else:
                                        raise e
                    except Exception as e:
                        if "429" in str(e):
                            st.error("⚠️ Quota API Habis atau Terlalu Cepat. Silakan tunggu 1 menit atau gunakan API Key lain.")
                        else:
                            st.error(f"Gagal memanggil AI: {e}")
