import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(page_title="FleetSense Phase 1", layout="wide")
st.title("🚕 LogicVeda FleetSense - NYC Taxi Dashboard")
st.markdown("Phase 1: NYC Yellow Taxi 2023 Pipeline")

DB_PATH = "data/fleetsense.duckdb"

@st.cache_data
def load_data():
    try:
        con = duckdb.connect(DB_PATH)
        df = con.execute("SELECT * FROM yellow_taxi LIMIT 10000").fetchdf()
        con.close()
        return df
    except:
        return None

df = load_data()

if df is None:
    st.warning("No data yet. Run ingestion pipeline first.")
    st.code("python Src/ingestion.py", language="bash")
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Trips", f"{len(df):,}")
    col2.metric("Avg Distance", f"{df['trip_distance'].mean():.2f} miles")
    col3.metric("Avg Fare", f"${df['fare_amount'].mean():.2f}")
    
    st.subheader("Trip Distance Distribution")
    st.bar_chart(df['trip_distance'].clip(0, 30))
    
    st.subheader("Sample Data")
    st.dataframe(df.head(100))

st.sidebar.markdown("**Author:** amoah83\n**Stack:** DuckDB + Polars + Pandera + Streamlit")
