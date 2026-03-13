import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import random
from datetime import datetime

st.set_page_config(
    page_title="Limi AI - Module Health Dashboard",
    layout="wide",
    page_icon="🏢"
)

# ---- Styling ----
st.markdown("""
<style>
    .metric-card { background: #1e1e2e; border-radius: 10px; padding: 15px; }
    .alert-high { color: #ff4444; font-weight: bold; }
    .alert-medium { color: #ffaa00; font-weight: bold; }
    .alert-low { color: #44ff88; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ---- Mock Data Generator ----
def generate_building_data():
    """Simulate real-time sensor data for 20 modules across 5 floors."""
    floors = ["Floor 1", "Floor 2", "Floor 3", "Floor 4", "Floor 5"]
    modules_per_floor = 4
    
    data = []
    for floor_idx, floor in enumerate(floors):
        for module_idx in range(modules_per_floor):
            module_id = f"LM-{floor_idx+1}{module_idx+1:02d}"
            
            # Simulate realistic sensor data with some failing modules
            base_temp = 40 + floor_idx * 3
            temp = base_temp + random.gauss(0, 8)
            voltage = 220 + random.gauss(0, 15)
            load = random.uniform(20, 95)
            usage_hours = random.uniform(1, 24)
            
            # Calculate failure probability (simplified)
            prob = min(1.0, max(0.0,
                (temp - 40) / 50 +
                abs(voltage - 220) / 100 +
                (load - 50) / 100
            ))
            
            if prob > 0.7:
                status = "CRITICAL"
                color = "red"
            elif prob > 0.4:
                status = "WARNING"
                color = "orange"
            else:
                status = "NORMAL"
                color = "green"
            
            data.append({
                "module_id": module_id,
                "floor": floor,
                "module_num": module_idx + 1,
                "temperature": round(temp, 1),
                "voltage": round(voltage, 1),
                "load_pct": round(load, 1),
                "usage_hours": round(usage_hours, 1),
                "failure_prob": round(prob, 3),
                "status": status,
                "color": color,
                "x": module_idx,
                "y": floor_idx,
                "energy_kwh": round(load * 0.05, 2)
            })
    
    return pd.DataFrame(data)

# ---- Header ----
st.title("🏢 Limi AI — Module Health Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Auto-refreshes every 5 minutes")

# ---- Summary Metrics ----
df = generate_building_data()

col1, col2, col3, col4, col5 = st.columns(5)
total = len(df)
critical = len(df[df["status"] == "CRITICAL"])
warning = len(df[df["status"] == "WARNING"])
normal = len(df[df["status"] == "NORMAL"])
avg_temp = df["temperature"].mean()

col1.metric("Total Modules", total)
col2.metric("🔴 Critical", critical, delta=f"{critical/total*100:.0f}%")
col3.metric("🟡 Warning", warning, delta=f"{warning/total*100:.0f}%")
col4.metric("🟢 Normal", normal)
col5.metric("Avg Temperature", f"{avg_temp:.1f}°C")

st.divider()

# ---- Two-column layout ----
left, right = st.columns([2, 1])

with left:
    st.subheader("🗺️ Building Heat Map — Module Health")
    
    # Create heatmap of failure probability
    pivot = df.pivot(index="floor", columns="module_num", values="failure_prob")
    
    fig_heat = px.imshow(
        pivot,
        color_continuous_scale=["#00ff88", "#ffaa00", "#ff4444"],
        zmin=0, zmax=1,
        labels={"color": "Failure Risk"},
        title="Module Failure Risk by Location",
        text_auto=".2f"
    )
    fig_heat.update_layout(
        height=400,
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font_color="white"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

with right:
    st.subheader("⚡ Energy Usage by Floor")
    
    floor_energy = df.groupby("floor")["energy_kwh"].sum().reset_index()
    fig_bar = px.bar(
        floor_energy,
        x="energy_kwh",
        y="floor",
        orientation="h",
        color="energy_kwh",
        color_continuous_scale=["green", "yellow", "red"],
        title="Total Energy Consumption (kWh)"
    )
    fig_bar.update_layout(
        height=400,
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font_color="white"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ---- Alerts Table ----
st.subheader("🚨 Active Alerts")

alerts = df[df["status"].isin(["CRITICAL", "WARNING"])].sort_values(
    "failure_prob", ascending=False
)[["module_id", "floor", "temperature", "voltage", "load_pct", "failure_prob", "status"]]

if len(alerts) > 0:
    st.dataframe(
        alerts.style.apply(
            lambda row: ["background-color: #3d0000" if row["status"] == "CRITICAL" 
                        else "background-color: #3d2d00"] * len(row),
            axis=1
        ),
        use_container_width=True,
        height=250
    )
else:
    st.success("✅ All modules operating normally!")

# ---- Real-time Chart ----
st.subheader("📈 Temperature Trend (Simulated Live Feed)")

if "history" not in st.session_state:
    st.session_state.history = []

new_avg = df["temperature"].mean() + random.gauss(0, 1)
st.session_state.history.append({
    "time": datetime.now().strftime("%H:%M:%S"),
    "avg_temp": round(new_avg, 2),
    "critical_count": critical
})

if len(st.session_state.history) > 20:
    st.session_state.history.pop(0)

hist_df = pd.DataFrame(st.session_state.history)
if len(hist_df) > 1:
    fig_line = px.line(
        hist_df, x="time", y="avg_temp",
        title="Average Module Temperature Over Time",
        markers=True
    )
    fig_line.add_hline(y=65, line_dash="dash", line_color="red", annotation_text="CRITICAL THRESHOLD")
    fig_line.update_layout(
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font_color="white", height=300
    )
    st.plotly_chart(fig_line, use_container_width=True)

# ---- Module Detail Table ----
with st.expander("📋 View All Module Details"):
    st.dataframe(df.drop(columns=["color", "x", "y"]), use_container_width=True)

# ---- Auto-refresh ----
st.divider()
auto_refresh = st.checkbox("Enable Auto-Refresh (5 min)", value=False)
if auto_refresh:
    time.sleep(300)
    st.rerun()
