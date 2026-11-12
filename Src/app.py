import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Fleetsense", layout="wide")
st.title("Fleetsense - NYC Taxi Demo")

# Sidebar Filters - REQUIRED
st.sidebar.header("Filters")
data_filter = st.sidebar.selectbox(
    "Data Range",
    ["Last 7 days", "Last 30 days", "All"]
)
min_trips = st.sidebar.slider(
    "Min Trips", 0, 500, 10
)

st.sidebar.success(f"Active: {data_filter}")

# Sample Data
df = pd.DataFrame({
    "Zone": ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"],
    "Trips": [150, 120, 90, 60, 30],
    "Revenue": [1500, 1100, 800, 500, 250]
})

# Filter
df_f = df[df["Trips"] >= min_trips]

col1, col2, col3 = st.columns(3)
col1.metric("Total Trips", int(df_f["Trips"].sum()))
col2.metric("Total Revenue", f"${int(df_f['Revenue'].sum())}")
col3.metric("Zones", len(df_f))

st.dataframe(df_f, use_container_width=True)

fig = px.bar(
    df_f,
    x="Zone",
    y=["Trips", "Revenue"],
    barmode="group",
    title=f"NYC Taxi - {data_filter}"
)
st.plotly_chart(fig, use_container_width=True)

st.info("Fleetsense Phase 1 - Live on Streamlit Cloud")