# app.py
import streamlit as st
import pandas as pd
import numpy as np
import json
from streamlit_echarts import st_echarts
from streamlit_elements import elements, dashboard

st.set_page_config(layout="wide")
st.title("Draggable & Resizable Dashboard — ECharts + Streamlit Elements")

# Upload file
uploaded = st.file_uploader("Upload Excel or CSV", type=["xlsx", "csv"])
if not uploaded:
    st.info("Upload a file to get started")
    st.stop()

if uploaded.name.endswith(".csv"):
    df = pd.read_csv(uploaded)
else:
    df = pd.read_excel(uploaded)

# Clean invalid values
df = df.replace([np.nan, np.inf, -np.inf], None)

columns = df.columns.tolist()
if not columns:
    st.error("No columns found in file.")
    st.stop()

# Session state: dashboard layout & chart configs
if "dashboard_layout" not in st.session_state:
    st.session_state.dashboard_layout = []
if "charts" not in st.session_state:
    st.session_state.charts = {}

# Sidebar: Add new chart
with st.sidebar.expander("➕ Add new chart"):
    x_col = st.selectbox("X-axis (category)", options=columns, key="new_x")
    y_col = st.selectbox("Y-axis (numeric / category / count)", options=["<count>"] + columns, key="new_y")
    chart_type = st.selectbox(
        "Chart type",
        ["Bar", "Line", "Pie"],
        key="new_type"
    )
    default_w = st.number_input("Initial grid width (cols out of 12)", min_value=2, max_value=12, value=6, step=1, key="new_w")
    default_h = st.number_input("Initial height (rows)", min_value=2, max_value=10, value=4, step=1, key="new_h")
    if st.button("Add Chart"):
        uid = f"chart_{len(st.session_state.charts)+1}"
        st.session_state.charts[uid] = {
            "x": x_col,
            "y": y_col,
            "type": chart_type
        }
        # Add to layout
        st.session_state.dashboard_layout.append({
            "i": uid,
            "x": 0, "y": 0,
            "w": default_w, "h": default_h,
        })

# Save / load dashboards
with st.sidebar.expander("💾 Save / Load Dashboards"):
    dash_name = st.text_input("Dashboard name")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Dashboard") and dash_name:
            data = {
                "layout": st.session_state.dashboard_layout,
                "charts": st.session_state.charts
            }
            with open(f"{dash_name}.json", "w") as f:
                json.dump(data, f)
            st.success(f"Saved as {dash_name}.json")
    with col2:
        if st.button("Load Dashboard") and dash_name:
            try:
                with open(f"{dash_name}.json") as f:
                    data = json.load(f)
                st.session_state.dashboard_layout = data.get("layout", [])
                st.session_state.charts = data.get("charts", {})
                st.experimental_rerun()
            except FileNotFoundError:
                st.error("Dashboard file not found")

# Render dashboard
with elements("dashboard"):
    # Use the layout from session_state
    with dashboard.Grid(st.session_state.dashboard_layout, draggableHandle=".react-resizable-handle"):
        for uid, cfg in st.session_state.charts.items():
            i = uid
            # Each chart lives in its own grid cell
            with st.container():  # container placeholder
                # Build chart options
                x_col = cfg["x"]
                y_col = cfg["y"]
                typ   = cfg["type"]

                x_data = df[x_col].astype(str)

                # Determine y_data
                if y_col == "<count>":
                    counted = x_data.value_counts().reset_index()
                    counted.columns = [x_col, "count"]
                    x_list = counted[x_col].astype(str).tolist()
                    y_list = counted["count"].tolist()
                else:
                    if pd.api.types.is_numeric_dtype(df[y_col]):
                        y_list = df[y_col].replace([np.nan, np.inf, -np.inf], None).tolist()
                        x_list = x_data.tolist()
                    else:
                        counted = df[y_col].astype(str).value_counts().reset_index()
                        counted.columns = [y_col, "count"]
                        x_list = counted[y_col].tolist()
                        y_list = counted["count"].tolist()

                # Build ECharts option
                if typ == "Bar":
                    opt = {
                        "tooltip": {"trigger": "axis"},
                        "xAxis": {"type": "category", "data": x_list},
                        "yAxis": {"type": "value"},
                        "series": [{"data": y_list, "type": "bar"}]
                    }
                elif typ == "Line":
                    opt = {
                        "tooltip": {"trigger": "axis"},
                        "xAxis": {"type": "category", "data": x_list},
                        "yAxis": {"type": "value"},
                        "series": [{"data": y_list, "type": "line"}]
                    }
                elif typ == "Pie":
                    opt = {
                        "tooltip": {"trigger": "item"},
                        "series": [{"type": "pie", "radius": "50%", "data": [{"value": v, "name": n} for n, v in zip(x_list, y_list)]}]
                    }
                else:
                    opt = {}

                st_echarts(options=opt, height="100%")
