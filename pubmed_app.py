import streamlit as st
import pandas as pd
import numpy as np
from streamlit_echarts import st_echarts

st.title("Superset-Style ECharts in Streamlit")
st.write("Upload an Excel file and create interactive charts with ECharts.")

uploaded = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded:
    df = pd.read_excel(uploaded)
    st.write("### Data Preview", df)

    # Clean NaN / inf values
    df = df.replace([np.nan, np.inf, -np.inf], None)

    columns = df.columns.tolist()

    x_axis = st.selectbox("X-axis Column", options=columns)
    y_axis = st.selectbox("Y-axis Column (optional, numeric or category)", options=["<count>"] + columns)

    chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Pie"])

    # ---------------------------
    # 1️⃣ X-axis always categories
    # ---------------------------
    x_data = df[x_axis].astype(str)

    # ---------------------------
    # 2️⃣ Determine numeric Y data
    # ---------------------------
    if y_axis == "<count>":
        # Count occurrences of each X category
        counted = x_data.value_counts().reset_index()
        counted.columns = [x_axis, "count"]
        x_list = counted[x_axis].astype(str).tolist()
        y_list = counted["count"].tolist()

    else:
        # If selected Y-axis exists
        if pd.api.types.is_numeric_dtype(df[y_axis]):
            # Use numeric values
            y_list = df[y_axis].replace([np.nan, np.inf, -np.inf], None).tolist()
            x_list = x_data.tolist()
        else:
            # Auto-count Y category values
            counted = df[y_axis].astype(str).value_counts().reset_index()
            counted.columns = [y_axis, "count"]
            x_list = counted[y_axis].tolist()
            y_list = counted["count"].tolist()

    # -----------------------
    # 3️⃣ Build ECharts options
    # -----------------------

    if chart_type == "Bar":
        options = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "data": x_list},
            "yAxis": {"type": "value"},
            "series": [{
                "data": y_list,
                "type": "bar",
                "smooth": True
            }]
        }

    elif chart_type == "Line":
        options = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "data": x_list},
            "yAxis": {"type": "value"},
            "series": [{
                "data": y_list,
                "type": "line",
                "smooth": True
            }]
        }

    elif chart_type == "Pie":
        pie_data = [{"value": v, "name": n} for n, v in zip(x_list, y_list)]

        options = {
            "tooltip": {"trigger": "item"},
            "series": [{
                "type": "pie",
                "radius": "60%",
                "data": pie_data
            }]
        }

    st_echarts(options=options, height="500px")
