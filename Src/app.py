import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fleetsense", layout="wide")
st.title("Fleetsense - NYC Taxi Demo")

# Sidebar Filters - REQUIRED
st.sidebar.header("Filters")

data_filter = st.sidebar.selectbox("Data Range", ["Last 7 days", "Last 30 days", "All"])
zone_filter = st.sidebar.slider("Min Trips", 0, 500, 10)

st.success(f"Filters loaded: {data_filter} | Min trips: {zone_filter}")
# Sample data to prove app works
df = pd.DataFrame({
    "Zone": ["Manhattan", "Brooklyn", "Queens", "Bronx"],
    "Trips": [150, 120, 90, 60],
    "Revenue": [1500, 1100, 800, 500]
})

st.dataframe(df, use_container_width=True)
st.bar_chart(df.set_index("Zone"))

st.info("App deployed via Streamlit - Fleetsense Phase 1 v1.0.0")