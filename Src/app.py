import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(
    page_title="FleetSense NYC",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
  .block-container { padding-top: 0.8rem; padding-bottom: 0.8rem; padding-left: 0.8rem; padding-right: 0.8rem; }
  h1 { font-size: 1.6rem !important; line-height: 1.2 !important; }
  h3 { font-size: 1.1rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("FleetSense")
st.markdown("### 🚕 NYC Taxi - Jan 2024")
st.caption("Source: NYC TLC • 2.9M real trips")

URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"

@st.cache_data
def load_data():
    con = duckdb.connect(":memory:")
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
    hourly_df = con.execute(f"""
        SELECT HOUR(tpep_pickup_datetime) as hour, COUNT(*) as Trips, AVG(fare_amount) as Avg_Fare
        FROM read_parquet('{URL}')
        WHERE tpep_pickup_datetime IS NOT NULL
        GROUP BY hour ORDER BY hour
    """).df()
    pay_df = con.execute(f"""
        SELECT CASE payment_type WHEN 1 THEN 'Credit Card' WHEN 2 THEN 'Cash' WHEN 3 THEN 'No Charge' WHEN 4 THEN 'Dispute' ELSE 'Other' END as Payment,
               COUNT(*) as Trips,
               AVG(CASE WHEN fare_amount > 0 THEN tip_amount / fare_amount ELSE 0 END) * 100 as Tip_Pct,
               AVG(tip_amount) as Avg_Tip
        FROM read_parquet('{URL}')
        GROUP BY Payment ORDER BY Trips DESC
    """).df()
    dist_df = con.execute(f"""
        SELECT CASE WHEN trip_distance < 1 THEN '0-1 mi' WHEN trip_distance < 2 THEN '1-2 mi' WHEN trip_distance < 3 THEN '2-3 mi' WHEN trip_distance < 5 THEN '3-5 mi' WHEN trip_distance < 10 THEN '5-10 mi' ELSE '10+ mi' END as Distance,
               COUNT(*) as Trips,
               AVG(fare_amount) as Avg_Fare,
               AVG(tip_amount) as Avg_Tip,
               AVG(total_amount) as Avg_Total
        FROM read_parquet('{URL}')
        WHERE trip_distance >= 0 AND trip_distance < 50 AND fare_amount > 0 AND fare_amount < 200
        GROUP BY Distance ORDER BY Trips DESC
    """).df()
    weekday_df = con.execute(f"""
        SELECT CASE DAYOFWEEK(tpep_pickup_datetime) WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday' WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday' WHEN 6 THEN 'Saturday' END as Day,
               COUNT(*) as Trips,
               AVG(fare_amount) as Avg_Fare,
               AVG(tip_amount) as Avg_Tip
        FROM read_parquet('{URL}')
        WHERE tpep_pickup_datetime IS NOT NULL
        GROUP BY Day ORDER BY Trips DESC
    """).df()
    con.close()
    return kpis, zones_df, daily_df, hourly_df, pay_df, dist_df, weekday_df

st.sidebar.header("Filters")
data_filter = st.sidebar.selectbox("Data Range", ["All", "Last 7 days", "Last 30 days"])
min_trips = st.sidebar.slider("Min Trips (Top Zones)", 0, 100, 0)
st.sidebar.success(f"Active: {data_filter} • Min {min_trips}")

with st.spinner("Loading real Jan 2024 data (2.9M rows)..."):
    (total_trips, total_revenue, avg_fare, zones), df, daily, hourly, pay, dist, weekday = load_data()

daily_filtered = daily.copy()
if data_filter == "Last 7 days":
    daily_filtered = daily_filtered.tail(7)
elif data_filter == "Last 30 days":
    daily_filtered = daily_filtered.tail(30)

df_filtered = df[df["Trips"] >= min_trips]

st.markdown(f"""
<div style="display:flex; flex-wrap:wrap; gap:8px;">
  <div style="flex:1 1 45%; background:#f0f2f6; padding:12px; border-radius:10px;">
    <div style="font-size:12px; color:#666;">Total Trips</div>
    <div style="font-size:20px; font-weight:700;">{total_trips:,}</div>
  </div>
  <div style="flex:1 1 45%; background:#f0f2f6; padding:12px; border-radius:10px;">
    <div style="font-size:12px; color:#666;">Total Revenue</div>
    <div style="font-size:20px; font-weight:700;">${total_revenue:,.0f}</div>
  </div>
  <div style="flex:1 1 45%; background:#f0f2f6; padding:12px; border-radius:10px;">
    <div style="font-size:12px; color:#666;">Avg Fare</div>
    <div style="font-size:20px; font-weight:700;">${avg_fare:.2f}</div>
  </div>
  <div style="flex:1 1 45%; background:#f0f2f6; padding:12px; border-radius:10px;">
    <div style="font-size:12px; color:#666;">Zones</div>
    <div style="font-size:20px; font-weight:700;">{zones}</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.subheader("Top 10 Pickup Zones")
st.dataframe(
    df_filtered,
    use_container_width=True,
    hide_index=True,
    column_config={"Revenue": st.column_config.NumberColumn(format="$%.0f")}
)

zones_plot = df_filtered.copy()
zones_plot["Zone_ID"] = zones_plot["Zone_ID"].astype(str)
zones_plot = zones_plot.sort_values("Trips")
st.bar_chart(zones_plot.set_index("Zone_ID")["Trips"], height=340)

st.subheader(f"Daily Trips - {data_filter}")
daily_filtered["day"] = pd.to_datetime(daily_filtered["day"])
daily_filtered["label"] = daily_filtered["day"].dt.strftime("%b %d")
st.bar_chart(daily_filtered.set_index("label")["Trips"], height=320)

st.subheader("Phase 2 - Hourly Demand")
st.caption("When do New York
