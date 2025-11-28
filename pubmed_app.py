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

    # Clean bad values globally
    df = df.replace([np.nan, np.inf, -np.inf], None)

    columns = df.columns.tolist()

    # Detect numeric columns
    numeric_columns = df.select_dtypes(include="number").columns.tolist()

    if not numeric_columns:
        st.error("No numeric columns found in your Excel file. Please upload a file with numeric data.")
        st.stop()

    x_axis = st.selectbox("X-axis Column", options=columns)
    y_axis = st.selectbox("Y-axis Column (numeric)", options=numeric_columns)

    # Validate selection
    if x_axis not in df.columns or y_axis not in df.columns:
        st.warning("Please select valid X and Y axis columns.")
        st.stop()

    chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Pie"])

    # Prepare JSON-safe data
    x_data = df[x_axis].astype(str).tolist()
    y_series = df[y_axis].replace([np.nan, np.inf, -np.inf], None).tolist()

    # Bar Chart
    if chart_type == "Bar":
        options = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "data": x_data},
            "yAxis": {"type": "value"},
            "series": [{
                "data": y_series,
                "type": "bar"
            }]
        }

    # Line Chart
    elif chart_type == "Line":
        options = {
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "data": x_data},
            "yAxis": {"type": "value"},
            "series": [{
                "data": y_series,
                "type": "line"
            }]
        }

    # Pie Chart
    elif chart_type == "Pie":
        pie_data = []
        for name, val in zip(x_data, y_series):
            pie_data.append({
                "value": 0 if val is None else val,
                "name": name
            })

        options = {
            "tooltip": {"trigger": "item"},
            "series": [{
                "type": "pie",
                "radius": "60%",
                "data": pie_data
            }]
        }

    st_echarts(options=options, height="500px")
