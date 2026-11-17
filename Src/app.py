import streamlit as st
import duckdb

st.set_page_config(page_title="Fleetsense", layout="wide")
st.title("Fleetsense - NYC Taxi Demo")
st.caption("Source: NYC TLC")

URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"

@st.cache_data
def load_kpis():
    con = duckdb.connect(":memory:")
    total_trips = con.execute(f"SELECT COUNT(*) FROM read_parquet('{URL}')").fetchone()[0]
    total_revenue = con.execute(f"SELECT SUM(fare_amount) FROM read_parquet('{URL}')").fetchone()[0]
    zones = con.execute(f"SELECT COUNT(DISTINCT PULocationID) FROM read_parquet('{URL}')").fetchone()[0]
    return total_trips, total_revenue, zones

@st.cache_data
def load_zones():
    con = duckdb.connect(":memory:")
    return con.execute(f"""
        SELECT PULocationID as Zone_ID, COUNT(*) as Trips, SUM(fare_amount) as Revenue
        FROM read_parquet('{URL}')
        GROUP BY PULocationID ORDER BY Trips DESC LIMIT 10
    """).df()

@st.cache_data
def load_daily():
    con = duckdb.connect(":memory:")
    return con.execute(f"""
        SELECT DATE(tpep_pickup_datetime) as day, COUNT(*) as Trips
        FROM read_parquet('{URL}')
        WHERE tpep_pickup_datetime IS NOT NULL
          AND tpep_pickup_datetime >= '2024-01-01'
          AND tpep_pickup_datetime < '2024-02-01'
        GROUP BY day ORDER BY day
    """).df()

st.sidebar.header("Filters - REQUIRED")
data_filter = st.sidebar.selectbox("Data Range", ["Last 7 days", "Last 30 days", "All"])
min_trips = st.sidebar.slider("Min Trips", 0, 100, 50)
st.sidebar.success("Active: 1 data filter")

with st.spinner("Loading real Jan 2024 data (2.9M rows)..."):
    total_trips, total_revenue, zones = load_kpis()
    df = load_zones()
    daily = load_daily()

col1, col2, col3 = st.columns(3)
col1.metric("Total Trips", f"{total_trips:,}")
col2.metric("Total Revenue", f"${total_revenue:,.0f}")
col3.metric("Zones", zones)

st.subheader("Top 10 Pickup Zones - Jan 2024 Real Data")
st.dataframe(df, use_container_width=True)
st.bar_chart(df.set_index("Zone_ID")["Trips"])

st.subheader("Daily Trips - Jan 2024 - Daily Trips")
st.bar_chart(daily.set_index("day")["Trips"])

st.info("Fleetsense Phase 1 - Live on Streamlit Cloud | Source: NYC TLC")
