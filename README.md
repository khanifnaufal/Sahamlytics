# 📈 IHSG Analyzer Pro

Aplikasi analisa saham IHSG berbasis Python + Streamlit.  
Dibuat sebagai MVP portofolio IT — siap dikembangkan lebih lanjut.

---

## 🚀 Cara Menjalankan

### 1. Clone / Download project ini

```bash
git clone https://github.com/username/ihsg-analyzer.git
cd ihsg-analyzer
```

### 2. Buat virtual environment (disarankan)

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Jalankan aplikasi

```bash
streamlit run app.py
```

Buka browser ke: **http://localhost:8501**

---

## 📁 Struktur Project

```
ihsg-analyzer/
├── app.py                  # Entry point + routing + global CSS
├── requirements.txt
├── README.md
│
├── pages/
│   ├── dashboard.py        # Chart teknikal + sinyal buy/sell
│   ├── screener.py         # Multi-stock scanner
│   ├── fundamental.py      # Analisa laporan keuangan
│   └── alerts.py           # Sistem alert & threshold
│
└── utils/
    └── data.py             # Data fetching, indikator, signal engine
```

---

## 🔧 Fitur MVP

| Fitur | Status |
|-------|--------|
| Chart Candlestick interaktif | ✅ |
| Indikator: RSI, MACD, MA, BB, Stochastic, OBV | ✅ |
| Signal engine (BUY/HOLD/SELL) multi-indikator | ✅ |
| Auto Stop Loss & Take Profit (ATR-based) | ✅ |
| Screener multi-saham dengan filter | ✅ |
| Analisa fundamental (valuasi, profitabilitas, solvabilitas) | ✅ |
| Sistem alert dengan threshold | ✅ |
| 30 saham IHSG populer (LQ45/IDX30) | ✅ |

---

## 🗺 Roadmap Fitur Berikutnya

### v1.1 — Notifikasi & Data
- [ ] Telegram bot alert (via python-telegram-bot)
- [ ] Tambah data dari IDX API langsung
- [ ] Candle pattern recognition otomatis (Hammer, Engulfing, dll)

### v1.2 — AI & Analytics
- [ ] Backtest strategi sinyal historical
- [ ] Analisa sentimen berita (scraping / NewsAPI)
- [ ] Machine learning untuk prediksi trend

### v1.3 — Portfolio
- [ ] Manajemen portfolio & tracking P/L
- [ ] Jurnal trading terintegrasi
- [ ] Export laporan PDF/Excel

### v2.0 — Production
- [ ] Deploy ke Streamlit Cloud / VPS
- [ ] User authentication
- [ ] Database PostgreSQL untuk menyimpan alert & history
- [ ] Mobile-responsive UI

---

## 📡 Sumber Data

- **Harga & Fundamental**: Yahoo Finance (via `yfinance`)
- **Coverage**: Saham dengan suffix `.JK` (Jakarta Stock Exchange)
- **Update**: Real-time saat market buka, delay ~15 menit

---

## ⚠ Disclaimer

Aplikasi ini dibuat untuk tujuan edukasi dan riset pribadi.  
**Bukan rekomendasi investasi.** Selalu lakukan riset mandiri (DYOR) sebelum mengambil keputusan investasi.

---

## 🛠 Tech Stack

- **Python 3.10+**
- **Streamlit** — UI framework
- **yfinance** — Data source
- **Plotly** — Interactive charts
- **Pandas + NumPy** — Data processing

---

*Built by [Nama Kamu] · IHSG Analyzer Pro v1.0*
