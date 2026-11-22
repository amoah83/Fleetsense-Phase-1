import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(
    page_title="FleetSense NYC",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Mobile fix ---
st.markdown("""
<style>
  .block-container { padding-top: 0.8rem; padding-bottom: 0.8rem; padding-left: 0.8rem; padding-right: 0.8rem; }
  h1 { font-size: 1.5rem !important; line-height: 1.2 !important; white-space: normal !important; }
  h3 { font-size: 1.1rem !important; }
  [data-testid="stMetricValue"] { font-size: 1.25rem !important; }
  [data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("🚕 FleetSense - NYC Taxi")
st.caption("Source: NYC TLC • Jan 2024 • 2.9M real trips")

URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"

@st.cache_data
def load_data():
    con = duckdb.connect(":memory:")
    # One query instead of 3 - much faster on Streamlit Cloud
    kpis = con.execute(f"""
        SELECT COUNT(*) as trips,
               SUM(fare_amount) as revenue,
               AVG(fare_amount) as avg_fare,
               COUNT(DISTINCT PULocationID) as zones
        FROM read_parquet('{URL}')
    """).fetchone()
    zones_df = con.execute(f"""
        SELECT PULocationID as Zone_ID, COUNT(*) as Trips, SUM(fare_amount) as Revenue
        FROM read_parquet('{URL}')
        GROUP BY PULocationID ORDER BY Trips DESC LIMIT 10
    """).df()
    daily_df = con.execute(f"""
        SELECT DATE(tpep_pickup_datetime) as day, COUNT(*) as Trips
        FROM read_parquet('{URL}')
        WHERE tpep_pickup_datetime IS NOT NULL
          AND tpep_pickup_datetime >= '2024-01-01'
          AND tpep_pickup_datetime < '2024-02-01'
        GROUP BY day ORDER BY day
    """).df()
    con.close()
    return kpis, zones_df, daily_df

# --- Sidebar - now actually works ---
st.sidebar.header("Filters")
data_filter = st.sidebar.selectbox("Data Range", ["All", "Last 7 days", "Last 30 days"])
min_trips = st.sidebar.slider("Min Trips (Top Zones)", 0, 100, 0)
st.sidebar.success(f"Active: {data_filter} • Min {min_trips}")

with st.spinner("Loading real Jan 2024 data (2.9M rows)..."):
    (total_trips, total_revenue, avg_fare, zones), df, daily = load_data()

# Apply filters
daily_filtered = daily.copy()
if data_filter == "Last 7 days":
    daily_filtered = daily_filtered.tail(7)
elif data_filter == "Last 30 days":
    daily_filtered = daily_filtered.tail(30)

df_filtered = df[df["Trips"] >= min_trips]

# --- KPIs - 2x2 on mobile, 4 in a row on desktop ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Trips", f"{total_trips:,}")
c2.metric("Total Revenue", f"${total_revenue:,.0f}")
c3.metric("Avg Fare", f"${avg_fare:.2f}")
c4.metric("Zones", zones)

# --- Top Zones ---
st.subheader("Top 10 Pickup Zones")
st.dataframe(
    df_filtered,
    use_container_width=True,
    hide_index=True,
    column_config={"Revenue": st.column_config.NumberColumn(format="$%.0f")}
)
# Horizontal bar = reads better on mobile
st.bar_chart(df_filtered.set_index("Zone_ID")["Trips"], horizontal=True, height=320)

# --- Daily Trips ---
st.subheader(f"Daily Trips - {data_filter}")
daily_filtered["day"] = pd.to_datetime(daily_filtered["day"])
# Short date labels so they don't overlap
daily_filtered["label"] = daily_filtered["day"].dt.strftime("%b %d")
st.bar_chart(daily_filtered.set_index("label")["Trips"], height=320)

st.info("FleetSense Phase 1 • Live on Streamlit Cloud | Source: NYC TLC")
