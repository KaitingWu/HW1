"""
dashboard.py — Streamlit AIoT Dashboard
=========================================
Reads sensor data from aiotdb.db (sensors table) and displays:
  - KPI cards (total records, avg temp, avg humidity, latest reading)
  - Data table (last 20 records)
  - Temperature line chart
  - Humidity line chart

Auto-refreshes every 5 seconds.
Run:  streamlit run dashboard.py
"""

import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AIoT Sensor Dashboard",
    page_icon="🌡️",
    layout="wide"
)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aiotdb.db")

# ─── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=5)   # cache invalidates every 5 seconds
def load_data(limit=100):
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        f"SELECT * FROM sensors ORDER BY id DESC LIMIT {limit}",
        conn
    )
    conn.close()
    if not df.empty:
        df = df.iloc[::-1].reset_index(drop=True)   # oldest → newest
    return df

# ─── UI ───────────────────────────────────────────────────────────────────────
st.title("🌡️ AIoT Sensor Dashboard")
st.caption(f"Data source: `{DB_PATH}` · Auto-refresh every 5s")

df = load_data()

if df.empty:
    st.warning("No data yet. Make sure app.py and esp32_sim.py are running.")
    st.info("Run in separate terminals:\n```\npython app.py\npython esp32_sim.py\n```")
    st.stop()

# ─── KPI Cards ────────────────────────────────────────────────────────────────
latest = df.iloc[-1]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📦 Total Records",
        value=f"{len(df)}"
    )
with col2:
    st.metric(
        label="🌡️ Avg Temperature",
        value=f"{df['temperature'].mean():.1f} °C",
        delta=f"{latest['temperature']:.1f} °C (latest)"
    )
with col3:
    st.metric(
        label="💧 Avg Humidity",
        value=f"{df['humidity'].mean():.1f} %",
        delta=f"{latest['humidity']:.1f} % (latest)"
    )
with col4:
    st.metric(
        label="🕐 Last Updated",
        value=latest["recorded_at"]
    )

st.divider()

# ─── Charts ───────────────────────────────────────────────────────────────────
chart_df = df[["recorded_at", "temperature", "humidity"]].copy()
chart_df = chart_df.set_index("recorded_at")

col_temp, col_hum = st.columns(2)

with col_temp:
    st.subheader("🌡️ Temperature (°C)")
    st.line_chart(chart_df["temperature"], color="#FF6B6B")

with col_hum:
    st.subheader("💧 Humidity (%RH)")
    st.line_chart(chart_df["humidity"], color="#4ECDC4")

st.divider()

# ─── Data Table ───────────────────────────────────────────────────────────────
st.subheader("📋 Recent Records (last 20)")
display_df = df.tail(20).iloc[::-1].reset_index(drop=True)
display_df.index += 1
st.dataframe(
    display_df[["recorded_at", "device_id", "temperature", "humidity", "wifi_rssi", "ip_address"]],
    use_container_width=True,
    column_config={
        "recorded_at":  "Timestamp",
        "device_id":    "Device",
        "temperature":  st.column_config.NumberColumn("Temp (°C)", format="%.1f"),
        "humidity":     st.column_config.NumberColumn("Humidity (%)", format="%.1f"),
        "wifi_rssi":    st.column_config.NumberColumn("RSSI (dBm)"),
        "ip_address":   "IP Address"
    }
)

# ─── Auto Refresh ─────────────────────────────────────────────────────────────
import time
time.sleep(5)
st.rerun()
