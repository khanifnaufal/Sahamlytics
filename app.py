import streamlit as st

st.set_page_config(
    page_title="Sahamlytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: #0a0e1a;
        color: #e8eaf6;
    }

    .main-header {
        font-family: 'Space Mono', monospace;
        font-size: 28px;
        font-weight: 700;
        color: #00e5ff;
        letter-spacing: -1px;
        margin-bottom: 4px;
    }

    .sub-header {
        font-size: 13px;
        color: #546e7a;
        font-family: 'Space Mono', monospace;
        margin-bottom: 24px;
    }

    .metric-card {
        background: #111827;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }

    .signal-BUY {
        background: linear-gradient(135deg, #003300, #004d00);
        border: 1px solid #00c853;
        color: #00e676;
        padding: 8px 20px;
        border-radius: 8px;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        font-size: 20px;
        text-align: center;
    }

    .signal-SELL {
        background: linear-gradient(135deg, #330000, #4d0000);
        border: 1px solid #d50000;
        color: #ff1744;
        padding: 8px 20px;
        border-radius: 8px;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        font-size: 20px;
        text-align: center;
    }

    .signal-HOLD {
        background: linear-gradient(135deg, #1a1a00, #2d2d00);
        border: 1px solid #ffd600;
        color: #ffea00;
        padding: 8px 20px;
        border-radius: 8px;
        font-family: 'Space Mono', monospace;
        font-weight: 700;
        font-size: 20px;
        text-align: center;
    }

    .stSelectbox > div > div {
        background: #111827;
        border: 1px solid #1e293b;
        color: #e8eaf6;
    }

    div[data-testid="stMetricValue"] {
        font-family: 'Space Mono', monospace;
        font-size: 22px;
    }

    .section-title {
        font-family: 'Space Mono', monospace;
        font-size: 13px;
        color: #546e7a;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 20px 0 12px;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 8px;
    }

    .alert-box {
        background: #1a1a2e;
        border-left: 3px solid #00e5ff;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        font-size: 13px;
        color: #90a4ae;
        margin: 8px 0;
    }

    .stSidebar {
        background: #060b18 !important;
    }

    .stButton > button {
        background: #00e5ff11;
        border: 1px solid #00e5ff44;
        color: #00e5ff;
        font-family: 'Space Mono', monospace;
        font-size: 12px;
        letter-spacing: 1px;
        border-radius: 8px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: #00e5ff22;
        border-color: #00e5ff;
    }

    .score-bar-container {
        background: #1e293b;
        border-radius: 4px;
        height: 6px;
        width: 100%;
        margin-top: 4px;
    }

    .tab-content { padding: 8px 0; }
</style>
""", unsafe_allow_html=True)

from pages import dashboard, screener, fundamental, alerts

st.sidebar.markdown('<div class="main-header">Sahamlytics</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sub-header">// PRO EDITION v1.0</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "NAVIGATE",
    ["📊 Dashboard", "🔍 Screener", "📋 Fundamental", "🔔 Alerts"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="font-size:11px; color:#37474f; font-family:'Space Mono',monospace; line-height:1.8;">
⚠ DISCLAIMER<br>
Aplikasi ini bukan<br>
rekomendasi investasi.<br>
Selalu DYOR.<br><br>
Data: Yahoo Finance<br>
Update: Real-time*
</div>
""", unsafe_allow_html=True)

if page == "📊 Dashboard":
    dashboard.render()
elif page == "🔍 Screener":
    screener.render()
elif page == "📋 Fundamental":
    fundamental.render()
elif page == "🔔 Alerts":
    alerts.render()
