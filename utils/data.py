import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import requests

# Setup session for yfinance to be more robust and avoid rate limits
_session = requests.Session()
_session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})


# ── Daftar saham IHSG populer ─────────────────────────────────────────────────
IHSG_STOCKS = {
    # Perbankan
    "BBCA.JK": "Bank Central Asia",
    "BBRI.JK": "Bank Rakyat Indonesia",
    "BMRI.JK": "Bank Mandiri",
    "BBNI.JK": "Bank Negara Indonesia",
    "BRIS.JK": "Bank Syariah Indonesia",
    # Konsumer
    "UNVR.JK": "Unilever Indonesia",
    "ICBP.JK": "Indofood CBP",
    "INDF.JK": "Indofood Sukses Makmur",
    "MYOR.JK": "Mayora Indah",
    # Energi & Tambang
    "ADRO.JK": "Adaro Energy",
    "PTBA.JK": "Bukit Asam",
    "INCO.JK": "Vale Indonesia",
    "ANTM.JK": "Aneka Tambang",
    "MDKA.JK": "Merdeka Copper Gold",
    # Telekomunikasi
    "TLKM.JK": "Telkom Indonesia",
    "EXCL.JK": "XL Axiata",
    "ISAT.JK": "Indosat Ooredoo",
    # Properti
    "BSDE.JK": "Bumi Serpong Damai",
    "SMRA.JK": "Summarecon Agung",
    # CPO & Agrikultur
    "AALI.JK": "Astra Agro Lestari",
    "LSIP.JK": "PP London Sumatra",
    # Otomotif & Industri
    "ASII.JK": "Astra International",
    "SRIL.JK": "Sri Rejeki Isman",
    # Infrastruktur
    "JSMR.JK": "Jasa Marga",
    "WIKA.JK": "Wijaya Karya",
    "WSKT.JK": "Waskita Karya",
    # Healthcare
    "KLBF.JK": "Kalbe Farma",
    "SIDO.JK": "Industri Jamu SIDO MUNCUL",
    # Retail
    "MAPI.JK": "Mitra Adiperkasa",
    "ACES.JK": "Ace Hardware Indonesia",
}

SECTORS = {
    "Semua Sektor": list(IHSG_STOCKS.keys()),
    "Perbankan": ["BBCA.JK","BBRI.JK","BMRI.JK","BBNI.JK","BRIS.JK"],
    "Energi & Tambang": ["ADRO.JK","PTBA.JK","INCO.JK","ANTM.JK","MDKA.JK"],
    "Konsumer": ["UNVR.JK","ICBP.JK","INDF.JK","MYOR.JK"],
    "Telekomunikasi": ["TLKM.JK","EXCL.JK","ISAT.JK"],
    "Infrastruktur": ["JSMR.JK","WIKA.JK","WSKT.JK"],
    "Healthcare": ["KLBF.JK","SIDO.JK"],
}


# ── Fetch price data ──────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_price_data(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """Ambil data harga dari Yahoo Finance."""
    try:
        df = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False, session=_session)
        if df.empty:
            return pd.DataFrame()
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df = df[["Open","High","Low","Close","Volume"]].dropna()
        return df
    except Exception as e:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def get_stock_info(ticker: str) -> dict:
    """Ambil info fundamental dari Yahoo Finance."""
    try:
        t = yf.Ticker(ticker, session=_session)
        info = t.info
        if not info or len(info) < 5:
            return dict(t.fast_info)
        return info
    except:
        return {}


def get_logo_url(website: str) -> str:
    """Extract domain from website and return Google Favicon URL."""
    if not website or not isinstance(website, str):
        return ""
    from urllib.parse import urlparse
    try:
        # Standardize URL
        if "://" not in website:
            website = "http://" + website
        parsed = urlparse(website)
        domain = parsed.netloc or parsed.path
        if "/" in domain:
            domain = domain.split("/")[0]
        domain = domain.replace("www.", "")
        if domain:
            # Google's favicon service is more reliable and widely available
            return f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
    except:
        pass
    return ""


# ── Indikator Teknikal ────────────────────────────────────────────────────────
def calc_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Hitung semua indikator teknikal."""
    if df.empty or len(df) < 26:
        return df

    close = df["Close"]
    high  = df["High"]
    low   = df["Low"]
    vol   = df["Volume"]

    # Moving Averages
    df["MA20"]  = close.rolling(20).mean()
    df["MA50"]  = close.rolling(50).mean()
    df["MA200"] = close.rolling(200).mean()
    df["EMA9"]  = close.ewm(span=9, adjust=False).mean()
    df["EMA20"] = close.ewm(span=20, adjust=False).mean()

    # Bollinger Bands (20, 2σ)
    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    df["BB_upper"] = bb_mid + 2 * bb_std
    df["BB_lower"] = bb_mid - 2 * bb_std
    df["BB_mid"]   = bb_mid

    # RSI (14)
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD (12, 26, 9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["MACD"]        = ema12 - ema26
    df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_hist"]   = df["MACD"] - df["MACD_signal"]

    # Stochastic (14, 3, 3)
    low14  = low.rolling(14).min()
    high14 = high.rolling(14).max()
    k = 100 * (close - low14) / (high14 - low14 + 1e-10)
    df["Stoch_K"] = k.rolling(3).mean()
    df["Stoch_D"] = df["Stoch_K"].rolling(3).mean()

    # OBV
    direction = np.where(close > close.shift(1), 1, np.where(close < close.shift(1), -1, 0))
    df["OBV"] = (vol * direction).cumsum()

    # ATR (14) — untuk stop loss calculation
    tr = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low  - close.shift()).abs()
    ], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(14).mean()

    # Volume MA
    df["Vol_MA20"] = vol.rolling(20).mean()

    # Fibonacci levels (dari 52-week high/low atau max tersedia)
    fib_period = min(252, len(df))
    h52 = high.rolling(fib_period, min_periods=1).max()
    l52 = low.rolling(fib_period, min_periods=1).min()
    diff = h52 - l52
    df["Fib_236"] = h52 - 0.236 * diff
    df["Fib_382"] = h52 - 0.382 * diff
    df["Fib_618"] = h52 - 0.618 * diff

    # VWAP & ORB (Intraday only)
    # Tentukan apakah data intraday (interval < 1d)
    is_intraday = (df.index[1] - df.index[0]).total_seconds() < 86400 if len(df) > 1 else False
    if is_intraday:
        df['date_only'] = df.index.date
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        pv = tp * df['Volume']
        df['VWAP'] = pv.groupby(df['date_only']).cumsum() / df['Volume'].groupby(df['date_only']).cumsum()
        
        # ORB 30m (asumsi 1 interval = 5m atau 15m)
        # Jika 5m, maka 6 bar. Jika 15m, maka 2 bar.
        interval_min = (df.index[1] - df.index[0]).total_seconds() / 60
        bars_30m = int(30 / interval_min) if interval_min > 0 else 1
        
        df['ORB_High'] = df.groupby('date_only')['High'].transform(lambda x: x.iloc[:bars_30m].max())
        df['ORB_Low']  = df.groupby('date_only')['Low'].transform(lambda x: x.iloc[:bars_30m].min())
    else:
        df['VWAP'] = df['Close'] # Fallback
        df['ORB_High'] = df['High']
        df['ORB_Low'] = df['Low']

    # Camarilla Pivots (Based on previous session)
    ph = df['High'].shift(1)
    pl = df['Low'].shift(1)
    pc = df['Close'].shift(1)
    diff_h_l = ph - pl
    df['H4'] = pc + diff_h_l * 1.1 / 2
    df['H3'] = pc + diff_h_l * 1.1 / 4
    df['L3'] = pc - diff_h_l * 1.1 / 4
    df['L4'] = pc - diff_h_l * 1.1 / 2

    return df


# ── Signal Engine ─────────────────────────────────────────────────────────────
def generate_signal(df: pd.DataFrame) -> dict:
    """
    Generate sinyal BUY / SELL / HOLD berdasarkan multi-indikator.
    Returns dict dengan signal, score, dan detail reasoning.
    """
    if df.empty or len(df) < 50:
        return {"signal": "N/A", "score": 0, "details": [], "sl": None, "tp": None}

    latest = df.iloc[-1]
    prev   = df.iloc[-2]
    close  = float(latest["Close"])

    signals   = []  # list of (name, bullish: bool, weight: int, detail: str)

    # ── RSI ──────────────────────────────────────────────────────────────────
    rsi = float(latest["RSI"]) if "RSI" in latest and not pd.isna(latest["RSI"]) else None
    if rsi is None:
        signals.append(("RSI", None, 0, "Data RSI tidak cukup"))
    elif rsi < 30:
        signals.append(("RSI", True, 3, f"RSI {rsi:.1f} — Oversold (potensi reversal ↑)"))
    elif rsi > 70:
        signals.append(("RSI", False, 3, f"RSI {rsi:.1f} — Overbought (potensi koreksi ↓)"))
    elif 40 <= rsi <= 60:
        signals.append(("RSI", True, 1, f"RSI {rsi:.1f} — Zona netral sehat"))
    else:
        signals.append(("RSI", rsi < 50, 1, f"RSI {rsi:.1f}"))

    # ── MACD ─────────────────────────────────────────────────────────────────
    if "MACD" not in latest or pd.isna(latest["MACD"]):
        signals.append(("MACD", None, 0, "Data MACD tidak cukup"))
    else:
        macd     = float(latest["MACD"])
        macd_sig = float(latest["MACD_signal"])
        macd_prev= float(prev["MACD"])
        sig_prev = float(prev["MACD_signal"])

        if macd > macd_sig and macd_prev <= sig_prev:
            signals.append(("MACD", True, 3, "MACD Golden Cross — sinyal BUY kuat ✓"))
        elif macd < macd_sig and macd_prev >= sig_prev:
            signals.append(("MACD", False, 3, "MACD Death Cross — sinyal SELL kuat ✗"))
        elif macd > macd_sig:
            signals.append(("MACD", True, 2, "MACD di atas signal line (bullish)"))
        else:
            signals.append(("MACD", False, 2, "MACD di bawah signal line (bearish)"))

    # ── Moving Average Trend ──────────────────────────────────────────────────
    ma20  = float(latest["MA20"])  if not pd.isna(latest["MA20"])  else None
    ma50  = float(latest["MA50"])  if not pd.isna(latest["MA50"])  else None
    ma200 = float(latest["MA200"]) if not pd.isna(latest["MA200"]) else None

    if ma20 and close > ma20:
        signals.append(("MA20", True, 2, f"Harga di atas MA20 ({ma20:,.0f}) — uptrend jangka pendek"))
    elif ma20:
        signals.append(("MA20", False, 2, f"Harga di bawah MA20 ({ma20:,.0f}) — downtrend jangka pendek"))

    if ma50 and ma200:
        if ma50 > ma200:
            signals.append(("MA Golden", True, 3, f"MA50 ({ma50:,.0f}) > MA200 ({ma200:,.0f}) — Golden Cross aktif"))
        else:
            signals.append(("MA Death", False, 3, f"MA50 < MA200 — Death Cross, trend bearish jangka panjang"))

    # ── Volume konfirmasi ─────────────────────────────────────────────────────
    vol     = float(latest["Volume"])
    vol_avg = float(latest["Vol_MA20"]) if not pd.isna(latest["Vol_MA20"]) else vol
    vol_ratio = vol / vol_avg if vol_avg > 0 else 1.0

    if vol_ratio > 1.5:
        close_change = close - float(prev["Close"])
        if close_change > 0:
            signals.append(("Volume", True, 2, f"Volume {vol_ratio:.1f}x rata-rata + harga naik — konfirmasi kuat"))
        else:
            signals.append(("Volume", False, 2, f"Volume {vol_ratio:.1f}x rata-rata + harga turun — distribusi"))
    else:
        signals.append(("Volume", None, 0, f"Volume normal ({vol_ratio:.1f}x rata-rata)"))

    # ── Bollinger Bands ───────────────────────────────────────────────────────
    bb_up  = float(latest["BB_upper"])
    bb_low = float(latest["BB_lower"])
    bb_mid = float(latest["BB_mid"])

    if close < bb_low:
        signals.append(("Bollinger", True, 2, f"Harga menyentuh BB Lower ({bb_low:,.0f}) — potensi reversal"))
    elif close > bb_up:
        signals.append(("Bollinger", False, 2, f"Harga menyentuh BB Upper ({bb_up:,.0f}) — overbought area"))
    else:
        bb_pos = (close - bb_low) / (bb_up - bb_low) * 100 if (bb_up - bb_low) > 0 else 50
        signals.append(("Bollinger", bb_pos < 50, 1, f"Posisi di BB: {bb_pos:.0f}% dari bawah"))

    # ── Stochastic ────────────────────────────────────────────────────────────
    stoch_k = float(latest["Stoch_K"]) if not pd.isna(latest["Stoch_K"]) else 50
    stoch_d = float(latest["Stoch_D"]) if not pd.isna(latest["Stoch_D"]) else 50

    if stoch_k < 20 and stoch_k > stoch_d:
        signals.append(("Stochastic", True, 2, f"Stoch K={stoch_k:.1f} — oversold + bullish crossover"))
    elif stoch_k > 80 and stoch_k < stoch_d:
        signals.append(("Stochastic", False, 2, f"Stoch K={stoch_k:.1f} — overbought + bearish crossover"))
    else:
        signals.append(("Stochastic", stoch_k > stoch_d, 1, f"Stoch K={stoch_k:.1f}, D={stoch_d:.1f}"))

    # ── Hitung final score ────────────────────────────────────────────────────
    bull_score = sum(w for _, b, w, _ in signals if b is True)
    bear_score = sum(w for _, b, w, _ in signals if b is False)
    total_w    = sum(w for _, b, w, _ in signals if b is not None)

    net_score = (bull_score - bear_score) / max(total_w, 1) * 100  # -100 to +100

    if net_score >= 30:
        signal = "BUY"
    elif net_score <= -30:
        signal = "SELL"
    else:
        signal = "HOLD"

    # ── Stop Loss & Take Profit (ATR-based) ───────────────────────────────────
    atr = float(latest["ATR"]) if not pd.isna(latest["ATR"]) else close * 0.02
    sl  = round(close - 2.0 * atr, 0)
    tp  = round(close + 3.0 * atr, 0)  # R:R = 1:1.5 minimum

    return {
        "signal":    signal,
        "score":     net_score,
        "bull_pts":  bull_score,
        "bear_pts":  bear_score,
        "details":   signals,
        "sl":        sl,
        "tp":        tp,
        "rsi":       rsi,
        "macd":      macd,
        "macd_sig":  macd_sig,
        "stoch_k":   stoch_k,
        "vol_ratio": vol_ratio,
        "close":     close,
        "atr":       atr,
    }


# ── Quick scan untuk Screener ─────────────────────────────────────────────────
@st.cache_data(ttl=600)
def quick_scan(tickers: list, period: str = "3mo", interval: str = "1d") -> pd.DataFrame:
    """Scan beberapa saham dan return DataFrame ringkasan."""
    rows = []
    for ticker in tickers:
        df = get_price_data(ticker, period=period, interval=interval)
        if df.empty:
            continue
        df = calc_indicators(df)
        sig = generate_signal(df)
        info = get_stock_info(ticker)

        latest = df.iloc[-1]
        prev   = df.iloc[-2]
        chg    = ((float(latest["Close"]) - float(prev["Close"])) / float(prev["Close"])) * 100

        rows.append({
            "Ticker":   ticker.replace(".JK",""),
            "Nama":     IHSG_STOCKS.get(ticker, ticker),
            "Harga":    float(latest["Close"]),
            "Chg%":     chg,
            "Logo_URL": get_logo_url(info.get("website", "")),
            "Vol/Avg":  sig.get("vol_ratio", 1.0),
            "RSI":      sig.get("rsi", 0),
            "MACD":     sig.get("macd", 0),
            "Score":    sig.get("score", 0),
            "Sinyal":   sig.get("signal", "N/A"),
            "PER":      info.get("trailingPE", None),
            "PBV":      info.get("priceToBook", None),
        })

    return pd.DataFrame(rows)
