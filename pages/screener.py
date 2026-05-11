import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.data import quick_scan, SECTORS, IHSG_STOCKS


def render():
    st.markdown('<div class="main-header">🔍 SCREENER</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">// filter saham IHSG sesuai kriteriamu</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        saham_input = st.text_input("Kode Saham (pisahkan dengan koma, contoh: BBCA, GOTO, ASII)", value="BBCA, BMRI, BBNI, BBRI, TLKM, ASII")
    with c2:
        trading_style = st.selectbox("Gaya Trading", 
                                     ["Scalping (5m)", "Day-Trade (15m)", "Swing (1d)", 
                                      "Beli Pagi - Jual Sore ", "Beli Sore - Jual Pagi"], 
                                     index=1)

    sc1, sc2, sc3 = st.columns([1, 1, 1])
    with sc1:
        min_rsi = st.slider("RSI Min", 0, 100, 30)
        max_rsi = st.slider("RSI Max", 0, 100, 70)
    with sc2:
        signal_filter = st.multiselect("Filter Sinyal", ["BUY","HOLD","SELL"], default=["BUY","HOLD","SELL"])
    with sc3:
        min_vol = st.number_input("Min Vol/Avg", 0.0, 10.0, 0.5, 0.1)

    if st.button("🔍 SCAN SEKARANG", type="primary"):
        tickers_list = [t.strip().upper() for t in saham_input.split(",") if t.strip()]
        if not tickers_list:
            st.error("Masukkan minimal satu kode saham.")
            return
            
        tickers_jk = [t if t.endswith('.JK') else t + '.JK' for t in tickers_list]

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

        with st.spinner(f"Scanning {len(tickers_jk)} saham..."):
            df_scan = quick_scan(tickers_jk, period=period, interval=interval)

        if df_scan.empty:
            st.warning("Tidak ada data. Cek koneksi internet.")
            return

        # Apply filters
        df_filtered = df_scan[
            (df_scan["RSI"] >= min_rsi) &
            (df_scan["RSI"] <= max_rsi) &
            (df_scan["Sinyal"].isin(signal_filter)) &
            (df_scan["Vol/Avg"] >= min_vol)
        ].sort_values("Score", ascending=False)

        st.markdown(f"<div class='section-title'>// HASIL: {len(df_filtered)} SAHAM DITEMUKAN</div>", unsafe_allow_html=True)

        for _, row in df_filtered.iterrows():
            signal = row["Sinyal"]
            sig_color = "#00e676" if signal=="BUY" else "#ff1744" if signal=="SELL" else "#ffd600"
            chg = row["Chg%"]
            chg_color = "#00e676" if chg >= 0 else "#ff1744"
            score = row["Score"]
            logo_url = row.get("Logo_URL", "")

            per_str = f"{row['PER']:.1f}x" if pd.notna(row.get("PER")) else "N/A"
            pbv_str = f"{row['PBV']:.2f}x" if pd.notna(row.get("PBV")) else "N/A"
            
            logo_html = f'<img src="{logo_url}" width="32" style="border-radius:4px; margin-right:12px; vertical-align:middle;">' if logo_url else ''

            st.markdown(f"""
<div style="background:#111827;border:1px solid #1e293b;border-left:3px solid {sig_color};border-radius:12px;padding:16px 20px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
<div style="display:flex;align-items:center;min-width:180px;">
{logo_html}
<div>
<div style="font-family:'Space Mono',monospace;font-size:16px;font-weight:700;color:#e8eaf6;">
{row['Ticker']}
</div>
<div style="font-size:12px;color:#546e7a;">{row['Nama']}</div>
</div>
</div>
<div style="text-align:center;">
<div style="font-size:11px;color:#546e7a;">Harga</div>
<div style="font-family:'Space Mono',monospace;font-weight:700;color:#e8eaf6;">
Rp {row['Harga']:,.0f}
</div>
<div style="font-size:12px;color:{chg_color};">{chg:+.2f}%</div>
</div>
<div style="text-align:center;">
<div style="font-size:11px;color:#546e7a;">RSI</div>
<div style="font-family:'Space Mono',monospace;font-weight:700;color:#e8eaf6;">{row['RSI']:.1f}</div>
</div>
<div style="text-align:center;">
<div style="font-size:11px;color:#546e7a;">Vol/Avg</div>
<div style="font-family:'Space Mono',monospace;font-weight:700;color:#e8eaf6;">{row['Vol/Avg']:.2f}x</div>
</div>
<div style="text-align:center;">
<div style="font-size:11px;color:#546e7a;">PER / PBV</div>
<div style="font-family:'Space Mono',monospace;font-weight:700;color:#e8eaf6;">{per_str} / {pbv_str}</div>
</div>
<div style="text-align:center;">
<div style="font-size:11px;color:#546e7a;">Score</div>
<div style="font-family:'Space Mono',monospace;font-weight:700;color:{'#00e676' if score>0 else '#ff1744'};">{score:+.0f}</div>
</div>
<div style="background:{sig_color}22;border:1px solid {sig_color}66;border-radius:8px;padding:6px 16px;font-family:'Space Mono',monospace;font-weight:700;color:{sig_color};font-size:14px;">
{signal}
</div>
</div>
""", unsafe_allow_html=True)


        # Export CSV
        st.markdown("---")
        csv = df_filtered.to_csv(index=False).encode()
        st.download_button("⬇ Download Hasil CSV", csv, "scan_ihsg.csv", "text/csv")
    else:
        st.markdown("""
<div class="alert-box">
    ℹ Pilih sektor dan kriteria di atas, lalu tekan SCAN untuk memulai screening saham secara otomatis.
    Proses scanning membutuhkan waktu 30-60 detik tergantung jumlah saham yang dipilih.
</div>
""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">// KRITERIA SCREENING YANG DIREKOMENDASIKAN</div>', unsafe_allow_html=True)
        tips = [
            ("🎯 Entry Agresif", "RSI 25-40, Vol/Avg > 1.5x, Sinyal: BUY — mencari bottom reversal"),
            ("📈 Trend Following", "RSI 45-60, Vol/Avg > 1.2x, Sinyal: BUY — ikuti momentum"),
            ("🛡 Konservatif", "RSI 40-55, Vol/Avg > 1.0x, Sinyal: BUY/HOLD — posisi aman"),
            ("⚠ Screening Sell", "RSI > 70, Vol/Avg > 2x, Sinyal: SELL — cari posisi exit"),
        ]
        for title, desc in tips:
            st.markdown(f"""
<div style="background:#111827;border:1px solid #1e293b;border-radius:8px;
            padding:12px 16px;margin-bottom:8px;">
    <div style="font-size:14px;font-weight:500;color:#e8eaf6;margin-bottom:4px;">{title}</div>
    <div style="font-size:12px;color:#546e7a;">{desc}</div>
</div>
""", unsafe_allow_html=True)
