import streamlit as st
import json
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.data import get_price_data, calc_indicators, generate_signal, IHSG_STOCKS


ALERTS_FILE = "alerts_config.json"

def load_alerts():
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, "r") as f:
            return json.load(f)
    return []

def save_alerts(alerts):
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)


def render():
    st.markdown('<div class="main-header">🔔 ALERTS</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">// pantau kondisi pasar & set threshold otomatis</div>', unsafe_allow_html=True)

    # ── Tambah Alert Baru ─────────────────────────────────────────────────────
    st.markdown('<div class="section-title">// TAMBAH ALERT BARU</div>', unsafe_allow_html=True)

    with st.form("add_alert"):
        fc1, fc2, fc3 = st.columns([2, 2, 1])
        with fc1:
            alert_ticker = st.selectbox(
                "Saham",
                options=list(IHSG_STOCKS.keys()),
                format_func=lambda x: f"{x.replace('.JK','')} — {IHSG_STOCKS[x]}"
            )
        with fc2:
            alert_type = st.selectbox("Jenis Alert", [
                "Harga di atas threshold",
                "Harga di bawah threshold",
                "RSI Overbought (>70)",
                "RSI Oversold (<30)",
                "Sinyal BUY muncul",
                "Sinyal SELL muncul",
                "Volume > 2x rata-rata",
            ])
        with fc3:
            threshold = st.number_input("Threshold Harga", min_value=0.0, value=0.0, step=100.0,
                                        help="Isi harga jika alert berbasis harga")

        note = st.text_input("Catatan (opsional)", placeholder="misal: level support kuat")
        submitted = st.form_submit_button("➕ TAMBAH ALERT")

        if submitted:
            alerts = load_alerts()
            alerts.append({
                "ticker": alert_ticker,
                "nama": IHSG_STOCKS.get(alert_ticker, alert_ticker),
                "type": alert_type,
                "threshold": threshold,
                "note": note,
                "active": True
            })
            save_alerts(alerts)
            st.success(f"✅ Alert untuk {alert_ticker.replace('.JK','')} berhasil ditambahkan!")

    # ── Check Alerts ──────────────────────────────────────────────────────────
    alerts = load_alerts()

    if not alerts:
        st.markdown("""
<div class="alert-box">
    ℹ Belum ada alert yang dibuat. Tambahkan alert di atas untuk mulai memantau saham secara otomatis.
    <br><br>
    <strong>Tips penggunaan alert:</strong><br>
    • Set alert RSI Oversold untuk saham yang kamu incar — masuk ketika pasar panic selling<br>
    • Set alert Harga di bawah threshold pada level support kunci sebagai sinyal entry<br>
    • Set alert Sinyal BUY muncul untuk auto-monitoring tanpa harus buka chart setiap saat
</div>
""", unsafe_allow_html=True)
        return

    st.markdown('<div class="section-title">// ALERT AKTIF — KLIK CEK KONDISI SEKARANG</div>', unsafe_allow_html=True)

    if st.button("🔄 CEK SEMUA ALERT SEKARANG"):
        with st.spinner("Mengecek kondisi semua alert..."):
            triggered = []
            ok_alerts = []

            for alert in alerts:
                if not alert.get("active", True):
                    continue

                ticker = alert["ticker"]
                df = get_price_data(ticker, "3mo")
                if df.empty:
                    continue

                df = calc_indicators(df)
                sig = generate_signal(df)
                latest = df.iloc[-1]
                close = float(latest["Close"])
                rsi   = sig.get("rsi", 50)
                signal = sig.get("signal", "HOLD")
                vol_r  = sig.get("vol_ratio", 1.0)

                atype = alert["type"]
                thr   = float(alert.get("threshold", 0))
                fired = False

                if atype == "Harga di atas threshold" and thr > 0:
                    fired = close > thr
                elif atype == "Harga di bawah threshold" and thr > 0:
                    fired = close < thr
                elif atype == "RSI Overbought (>70)":
                    fired = rsi > 70
                elif atype == "RSI Oversold (<30)":
                    fired = rsi < 30
                elif atype == "Sinyal BUY muncul":
                    fired = signal == "BUY"
                elif atype == "Sinyal SELL muncul":
                    fired = signal == "SELL"
                elif atype == "Volume > 2x rata-rata":
                    fired = vol_r > 2.0

                alert["_close"]  = close
                alert["_rsi"]    = rsi
                alert["_signal"] = signal
                alert["_vol"]    = vol_r
                alert["_fired"]  = fired

                if fired:
                    triggered.append(alert)
                else:
                    ok_alerts.append(alert)

        # Triggered alerts
        if triggered:
            st.markdown(f"""
<div style="background:#ff174411;border:1px solid #ff1744;border-radius:12px;padding:16px 20px;margin-bottom:16px;">
<div style="font-family:'Space Mono',monospace;font-size:14px;font-weight:700;color:#ff1744;margin-bottom:12px;">
🚨 {len(triggered)} ALERT TERPICU
</div>
""", unsafe_allow_html=True)

            for a in triggered:
                close_fmt = f"Rp {a['_close']:,.0f}"
                st.markdown(f"""
<div style="background:#1a0000;border:1px solid #ff174466;border-radius:8px;padding:14px 18px;margin-bottom:8px;">
<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
<div>
<span style="font-family:'Space Mono',monospace;font-size:16px;font-weight:700;color:#ff1744;">
{a['ticker'].replace('.JK','')}
</span>
<span style="font-size:12px;color:#546e7a;margin-left:8px;">{a['nama']}</span>
</div>
<div style="font-size:12px;color:#78909c;">
Harga: {close_fmt} · RSI: {a['_rsi']:.1f} · Vol: {a['_vol']:.1f}x · Sinyal: {a['_signal']}
</div>
</div>
<div style="margin-top:8px;font-size:13px;color:#e8eaf6;">
⚡ <strong>{a['type']}</strong>
{' — ' + a['note'] if a.get('note') else ''}
</div>
</div>
""", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # OK alerts
        if ok_alerts:
            st.markdown('<div class="section-title">// DALAM PANTAUAN (BELUM TERPICU)</div>', unsafe_allow_html=True)
            for a in ok_alerts:
                close_fmt = f"Rp {a['_close']:,.0f}"
                sig_col = "#00e676" if a['_signal']=="BUY" else "#ff1744" if a['_signal']=="SELL" else "#ffd600"
                st.markdown(f"""
<div style="background:#111827;border:1px solid #1e293b;border-radius:8px;padding:12px 16px;margin-bottom:6px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
<div>
<span style="font-family:'Space Mono',monospace;font-weight:700;color:#e8eaf6;">
{a['ticker'].replace('.JK','')}
</span>
<span style="font-size:12px;color:#546e7a;margin-left:8px;">{a['type']}</span>
</div>
<div style="display:flex;gap:16px;align-items:center;font-size:12px;color:#546e7a;">
<span>{close_fmt}</span>
<span>RSI {a['_rsi']:.1f}</span>
<span>Vol {a['_vol']:.1f}x</span>
<span style="color:{sig_col};font-weight:600;">{a['_signal']}</span>
</div>
<span style="font-size:11px;color:#37474f;">⚪ Belum terpicu</span>
</div>
""", unsafe_allow_html=True)

    else:
        # Tampilkan list alert tanpa check
        st.markdown('<div class="section-title">// DAFTAR ALERT</div>', unsafe_allow_html=True)
        for i, a in enumerate(alerts):
            st.markdown(f"""
<div style="background:#111827;border:1px solid #1e293b;border-radius:8px;padding:12px 16px;margin-bottom:6px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
<div>
<span style="font-family:'Space Mono',monospace;font-weight:700;color:#00e5ff;">
{a['ticker'].replace('.JK','')}
</span>
<span style="font-size:13px;color:#e8eaf6;margin-left:12px;">{a['type']}</span>
{f'<div style="font-size:11px;color:#37474f;margin-top:2px;">{a["note"]}</div>' if a.get('note') else ''}
</div>
<div style="font-size:12px;color:#546e7a;">
{f'Threshold: Rp {a["threshold"]:,.0f}' if a.get("threshold",0) > 0 else ''}
</div>
</div>
""", unsafe_allow_html=True)

        if st.button("🗑 Hapus Semua Alert"):
            save_alerts([])
            st.rerun()
