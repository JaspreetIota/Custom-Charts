import streamlit as st
import pandas as pd
import numpy as np
from streamlit_echarts import st_echarts

st.set_page_config(page_title="Custom ECharts Dashboard", layout="wide")
st.title("Superset-Style ECharts in Streamlit")
st.write("Upload an Excel file and create interactive charts with many ECharts types.")

# --- Upload Excel ---
uploaded = st.file_uploader("Upload Excel File", type=["xlsx", "csv"])

if uploaded:
    # Detect Excel or CSV
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

    st.write("### Data Preview", df)

    # Replace invalid JSON values
    df = df.replace([np.nan, np.inf, -np.inf], None)

    columns = df.columns.tolist()

    if len(columns) < 1:
        st.error("No columns found in your file.")
        st.stop()

    # --- User selects columns ---
    x_axis = st.selectbox("X-axis Column (categories)", options=columns)
    y_axis = st.selectbox(
        "Y-axis Column (numeric or category, optional for count)",
        options=["<count>"] + columns
    )

    # --- Chart type selection ---
    chart_type = st.selectbox(
        "Chart Type",
        [
            "Bar",
            "Stacked Bar",
            "Horizontal Bar",
            "Line",
            "Area",
            "Stacked Area",
            "Pie",
            "Donut",
            "Scatter",
            "Radar",
            "Funnel",
            "Gauge",
            "Treemap",
            "Word Cloud"
        ]
    )

    # --- Prepare data ---
    x_data = df[x_axis].astype(str)

    # Determine y_data
    if y_axis == "<count>":
        # Count occurrences of X-axis categories
        counted = x_data.value_counts().reset_index()
        counted.columns = [x_axis, "count"]
        x_list = counted[x_axis].astype(str).tolist()
        y_list = counted["count"].tolist()
    else:
        # Use numeric values if possible
        if pd.api.types.is_numeric_dtype(df[y_axis]):
            y_list = df[y_axis].replace([np.nan, np.inf, -np.inf], None).tolist()
            x_list = x_data.tolist()
        else:
            # Count occurrences of Y categories
            counted = df[y_axis].astype(str).value_counts().reset_index()
            counted.columns = [y_axis, "count"]
            x_list = counted[y_axis].tolist()
            y_list = counted["count"].tolist()

    # --- Build ECharts options ---
    options = {}

    if chart_type == "Bar":
        options = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "data": x_list},
            "yAxis": {"type": "value"},
            "series": [{"data": y_list, "type": "bar"}]
        }

    elif chart_type == "Stacked Bar":
        options = {
            "tooltip": {"trigger": "axis"},
            "legend": {},
            "xAxis": {"type": "category", "data": x_list},
            "yAxis": {"type": "value"},
            "series": [{"type": "bar", "stack": "total", "data": y_list}]
        }

    elif chart_type == "Horizontal Bar":
        options = {
            "tooltip": {"trigger": "axis"},
            "yAxis": {"type": "category", "data": x_list},
            "xAxis": {"type": "value"},
            "series": [{"data": y_list, "type": "bar"}]
        }

    elif chart_type == "Line":
        options = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "data": x_list},
            "yAxis": {"type": "value"},
            "series": [{"data": y_list, "type": "line"}]
        }

    elif chart_type == "Area":
        options = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "data": x_list},
            "yAxis": {"type": "value"},
            "series": [{"data": y_list, "type": "line", "areaStyle": {}}]
        }

    elif chart_type == "Stacked Area":
        options = {
            "tooltip": {"trigger": "axis"},
            "legend": {},
            "xAxis": {"type": "category", "data": x_list},
            "yAxis": {"type": "value"},
            "series": [{"type": "line", "areaStyle": {}, "stack": "total", "data": y_list}]
        }

    elif chart_type == "Pie":
        options = {
            "tooltip": {"trigger": "item"},
            "series": [{"type": "pie", "radius": "60%", "data": [{"value": v, "name": n} for n, v in zip(x_list, y_list)]}]
        }

    elif chart_type == "Donut":
        options = {
            "tooltip": {"trigger": "item"},
            "series": [{"type": "pie", "radius": ["40%", "70%"], "data": [{"value": v, "name": n} for n, v in zip(x_list, y_list)]}]
        }

    elif chart_type == "Scatter":
        options = {
            "xAxis": {"type": "category", "data": list(range(len(y_list)))},
            "yAxis": {"type": "value"},
            "series": [{"data": [[i, v] for i, v in enumerate(y_list)], "type": "scatter"}]
        }

    elif chart_type == "Radar":
        options = {
            "tooltip": {},
            "radar": {
                "indicator": [{"name": n, "max": max(y_list) if max(y_list) else 1} for n in x_list]
            },
            "series": [{"type": "radar", "data": [{"value": y_list, "name": "Values"}]}]
        }

    elif chart_type == "Funnel":
        options = {
            "tooltip": {"trigger": "item"},
            "series": [{"type": "funnel", "data": [{"value": v, "name": n} for n, v in zip(x_list, y_list)]}]
        }

    elif chart_type == "Gauge":
        options = {
            "series": [{"type": "gauge", "progress": {"show": True}, "data": [{"value": y_list[0] if y_list else 0}]}]
        }

    elif chart_type == "Treemap":
        options = {
            "series": [{"type": "treemap", "data": [{"name": n, "value": v} for n, v in zip(x_list, y_list)]}]
        }

    elif chart_type == "Word Cloud":
        options = {
            "series": [{"type": "wordCloud", "shape": "circle", "data": [{"name": n, "value": v} for n, v in zip(x_list, y_list)]}]
        }

    # --- Render chart ---
    st_echarts(options=options, height="500px")
