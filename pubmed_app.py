import streamlit as st
import pandas as pd
import plotly.express as px
import os

EXCEL_PATH = "uat_issues.xlsx"
CLIENT_COLUMNS = ["Portfolio Demo","Diabetes","TMW","MDR","EDL","STF","IPRG Demo"]

# ------------------------ LOAD EXCEL ------------------------
@st.cache_data(ttl=5)
def load_excel():
    if not os.path.exists(EXCEL_PATH):
        st.error(f"Excel file {EXCEL_PATH} not found.")
        return pd.DataFrame(), pd.DataFrame()

    xls = pd.ExcelFile(EXCEL_PATH)
    sheet_names = [s.lower() for s in xls.sheet_names]

    df_main = pd.read_excel(EXCEL_PATH, sheet_name=xls.sheet_names[sheet_names.index("uat_issues")]) \
        if "uat_issues" in sheet_names else pd.DataFrame()

    df_arch = pd.read_excel(EXCEL_PATH, sheet_name=xls.sheet_names[sheet_names.index("architecture_issues")]) \
        if "architecture_issues" in sheet_names else pd.DataFrame()

    df_main.columns = df_main.columns.str.strip()
    df_arch.columns = df_arch.columns.str.strip()

    return df_main, df_arch

# ------------------------ CONFIG ------------------------
st.set_page_config(page_title="UAT & Architecture Bug Tracker", layout="wide")
st.title("🧪 Bug Tracker Dashboard with Charts & Row Media Viewer")

# Load data
df_main, df_arch = load_excel()

# ------------------------ SIDEBAR ------------------------
page = st.sidebar.radio("Select Page", ["📊 Dashboard", "📋 UAT Issues (Editable)", "🏗️ Architecture Issues (Editable)"])

# ------------------------ DASHBOARD ------------------------
if page == "📊 Dashboard":
    dashboard_type = st.radio("Choose Dashboard", ["UAT Issues", "Architecture Issues"])

    if dashboard_type == "UAT Issues":
        st.header("📊 UAT Issues Dashboard")

        # Filters
        type_options = df_main["Type"].unique() if "Type" in df_main.columns else []
        selected_types = st.multiselect("Filter by Type", type_options, default=type_options)

        client_options = [c for c in CLIENT_COLUMNS if c in df_main.columns]
        selected_clients = st.multiselect("Filter by Resolved Clients", client_options, default=client_options)

        df_filtered = df_main.copy()
        if selected_types:
            df_filtered = df_filtered[df_filtered["Type"].isin(selected_types)]
        if selected_clients:
            df_filtered = df_filtered[df_filtered[selected_clients].eq("Yes").all(axis=1)]

        st.subheader("✅ Predefined Charts")
        # Issues by Type
        if "Type" in df_filtered.columns:
            fig_type = px.bar(df_filtered['Type'].value_counts().reset_index(), x='index', y='Type',
                              labels={'index': 'Type', 'Type':'Count'}, title='Issues by Type')
            st.plotly_chart(fig_type, use_container_width=True)

        # Issues resolved per client (stacked)
        if selected_clients:
            client_counts = df_filtered[selected_clients].apply(lambda x: x=='Yes').sum()
            fig_client = px.bar(client_counts.reset_index(), x='index', y=selected_clients,
                                labels={'index':'Client','value':'Resolved Count'},
                                title="Issues Resolved per Client")
            st.plotly_chart(fig_client, use_container_width=True)

        # Open vs Dev Status
        if "Dev Status" in df_filtered.columns:
            dev_counts = df_filtered["Dev Status"].value_counts()
            fig_dev = px.pie(names=dev_counts.index, values=dev_counts.values, title="Dev Status Distribution")
            st.plotly_chart(fig_dev, use_container_width=True)

        st.subheader("📊 Custom Charts")
        chart_x = st.selectbox("X-axis", df_filtered.columns, index=1)
        chart_y = st.selectbox("Y-axis", df_filtered.columns, index=2)
        chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Scatter", "Pie"])

        if chart_type=="Bar":
            fig_custom = px.bar(df_filtered, x=chart_x, y=chart_y)
        elif chart_type=="Line":
            fig_custom = px.line(df_filtered, x=chart_x, y=chart_y)
        elif chart_type=="Scatter":
            fig_custom = px.scatter(df_filtered, x=chart_x, y=chart_y)
        elif chart_type=="Pie":
            fig_custom = px.pie(df_filtered, names=chart_x, values=chart_y)
        st.plotly_chart(fig_custom, use_container_width=True)

        # Column filter and table
        st.subheader("📋 Filter Table")
        columns_to_show = st.multiselect("Select columns to display", df_filtered.columns.tolist(), default=df_filtered.columns.tolist())
        st.dataframe(df_filtered[columns_to_show], use_container_width=True)

        # Media Viewer
        st.subheader("🎬 Media Viewer")
        for idx, row in df_filtered.iterrows():
            with st.expander(f"Row {row.get('Sno.', '')}: {row.get('Issue', '')}"):
                if "image" in row and pd.notna(row["image"]):
                    for img in str(row["image"]).split("|"):
                        st.image(img.strip(), caption="Screenshot", use_column_width=True)
                if "video" in row and pd.notna(row["video"]):
                    for vid in str(row["video"]).split("|"):
                        st.video(vid.strip())

    else:  # Architecture dashboard
        st.header("🏗️ Architecture Issues Dashboard")

        type_options = df_arch["Type"].unique() if "Type" in df_arch.columns else []
        selected_types = st.multiselect("Filter by Type", type_options, default=type_options)
        status_options = df_arch["Status"].unique() if "Status" in df_arch.columns else []
        selected_status = st.multiselect("Filter by Status", status_options, default=status_options)

        df_filtered = df_arch.copy()
        if selected_types:
            df_filtered = df_filtered[df_filtered["Type"].isin(selected_types)]
        if selected_status:
            df_filtered = df_filtered[df_filtered["Status"].isin(selected_status)]

        st.subheader("✅ Predefined Charts")
        # Issues by Type
        if "Type" in df_filtered.columns:
            fig_type = px.bar(df_filtered['Type'].value_counts().reset_index(), x='index', y='Type',
                              labels={'index': 'Type', 'Type':'Count'}, title='Issues by Type')
            st.plotly_chart(fig_type, use_container_width=True)

        # Open vs Status
        if "Status" in df_filtered.columns:
            status_counts = df_filtered['Status'].value_counts()
            fig_status = px.pie(names=status_counts.index, values=status_counts.values, title="Status Distribution")
            st.plotly_chart(fig_status, use_container_width=True)

        # Custom charts
        st.subheader("📊 Custom Charts")
        chart_x = st.selectbox("X-axis", df_filtered.columns, index=1)
        chart_y = st.selectbox("Y-axis", df_filtered.columns, index=2)
        chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Scatter", "Pie"], key="arch_chart_type")

        if chart_type=="Bar":
            fig_custom = px.bar(df_filtered, x=chart_x, y=chart_y)
        elif chart_type=="Line":
            fig_custom = px.line(df_filtered, x=chart_x, y=chart_y)
        elif chart_type=="Scatter":
            fig_custom = px.scatter(df_filtered, x=chart_x, y=chart_y)
        elif chart_type=="Pie":
            fig_custom = px.pie(df_filtered, names=chart_x, values=chart_y)
        st.plotly_chart(fig_custom, use_container_width=True)

        # Column filter and table
        st.subheader("📋 Filter Table")
        columns_to_show = st.multiselect("Select columns to display", df_filtered.columns.tolist(), default=df_filtered.columns.tolist())
        st.dataframe(df_filtered[columns_to_show], use_container_width=True)

        # Media viewer
        st.subheader("🎬 Media Viewer")
        for idx, row in df_filtered.iterrows():
            with st.expander(f"Row {row.get('Sno.', '')}: {row.get('Issue', '')}"):
                if "image" in row and pd.notna(row["image"]):
                    for img in str(row["image"]).split("|"):
                        st.image(img.strip(), caption="Screenshot", use_column_width=True)
                if "video" in row and pd.notna(row["video"]):
                    for vid in str(row["video"]).split("|"):
                        st.video(vid.strip())
