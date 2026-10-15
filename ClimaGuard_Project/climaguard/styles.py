"""Shared visual design system for the ClimaGuard dashboard."""

import streamlit as st

DASHBOARD_CSS = r"""
<style>
.stApp {
    background:
        radial-gradient(circle at 12% 8%, rgba(20,78,108,.28), transparent 28%),
        radial-gradient(circle at 88% 15%, rgba(196,91,20,.16), transparent 25%),
        linear-gradient(135deg, #071018 0%, #0b1720 50%, #101b24 100%);
    color: #f4f7fa;
}

.block-container {
    max-width: 1500px;
    padding: 1rem 1.5rem 2rem 1.5rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #08121a 0%, #0c1b25 100%);
    border-right: 1px solid rgba(255,255,255,.08);
}

.dashboard-head {
    background: linear-gradient(110deg, rgba(19,51,69,.94), rgba(9,19,27,.97));
    border: 1px solid rgba(255,255,255,.12);
    border-radius: 8px;
    padding: 16px 24px 13px 24px;
    margin-bottom: 10px;
    box-shadow: 0 8px 28px rgba(0,0,0,.25);
}

.dashboard-title {
    font-size: 31px;
    line-height: 1.05;
    font-weight: 850;
    letter-spacing: .7px;
    margin: 0;
}

.dashboard-title span {
    color: #ff8a24;
}

.dashboard-subtitle {
    margin-top: 8px;
    color: #b7c6ce;
    font-size: 13px;
}

.kpi {
    background: linear-gradient(145deg, rgba(29,43,53,.96), rgba(13,24,32,.96));
    border: 1px solid rgba(255,255,255,.13);
    border-radius: 7px;
    padding: 13px 15px;
    min-height: 82px;
    box-shadow: 0 6px 18px rgba(0,0,0,.20);
}

.kpi-label {
    color: #b6c5cc;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 5px;
}

.kpi-value {
    color: #f4f7f8;
    font-size: 25px;
    font-weight: 800;
    line-height: 1.1;
}

.kpi-small {
    color: #ff9b43;
    font-size: 10px;
    margin-top: 4px;
}

.panel {
    background: linear-gradient(145deg, rgba(24,39,49,.94), rgba(12,22,29,.96));
    border: 1px solid rgba(255,255,255,.11);
    border-radius: 8px;
    padding: 10px 13px 6px 13px;
    box-shadow: 0 7px 20px rgba(0,0,0,.18);
}

.panel-title {
    color: #e9eef1;
    font-size: 13px;
    font-weight: 750;
    margin: 0 0 5px 0;
}

.panel-title .accent {
    color: #ff8a24;
}

.alert-strip {
    border-left: 4px solid #ff8a24;
    background: rgba(255,138,36,.09);
    border-radius: 5px;
    padding: 9px 13px;
    margin: 7px 0 10px 0;
    color: #e9edf0;
    font-size: 12px;
}

.sidebar-brand {
    color: #ff8a24;
    font-size: 22px;
    font-weight: 850;
    letter-spacing: .8px;
}

.sidebar-caption {
    color: #94aab5;
    font-size: 11px;
}

[data-testid="stMetric"] {
    background: transparent;
    border: 0;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.stButton > button {
    border-radius: 6px;
}
</style>
"""

def inject_styles() -> None:
    """Apply the dashboard theme and component styling."""
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
