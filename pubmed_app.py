import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts
import numpy as np

st.title("Superset-Style ECharts in Streamlit")
st.write("Upload an Excel file and create interactive charts with ECharts.")

uploaded = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded:
    df = pd.read_excel(uploaded)
    st.write("### Data Preview", df)

    # Convert all NaN, NaT, None, inf → None (valid JSON)
    df = df.replace([np.nan, np.inf, -np.inf], None)

    columns = df.columns.tolist()
    x_axis = st.selectbox("X-axis Column", options=columns)
    y_axis = st.selectbox("Y-axis Column (numeric)", options=df.select_dtypes(include="number").columns)

    chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Pie"])

    # Clean y-axis values
    y_data = df[y_axis].replace([np.nan, np.inf, -np.inf], None).tolist()

    # Prepare x data as strings (safe)
    x_data = df[x_axis].astype(str).tolist()

    # BAR
    if chart_type == "Bar":
        options = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "data": x_data},
            "yAxis": {"type": "value"},
            "series": [{
                "data": y_data,
                "type": "bar",
            }]
        }

    # LINE
    elif chart_type == "Line":
        options = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "data": x_data},
            "yAxis": {"type": "value"},
            "series": [{
                "data": y_data,
                "type": "line",
            }]
        }

    # PIE (special care)
    elif chart_type == "Pie":
        pie_data = []
        for name, val in zip(x_data, y_data):
            if val is None:       # prevent NaN in pie charts
                val = 0
            pie_data.append({"value": val, "name": name})

        options = {
            "tooltip": {"trigger": "item"},
            "series": [{
                "type": "pie",
                "radius": "60%",
                "data": pie_data,
            }]
        }

    st_echarts(options=options, height="500px")
