import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(page_title="FleetSense NYC", page_icon="🚕", layout="wide", initial_sidebar_state="collapsed")

st.title("FleetSense")
st.markdown("### NYC Taxi - Jan 2024")
st.caption("Source: NYC TLC - 2.9M trips")

URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"

@st.cache_data
def load_data():
    con = duckdb.connect(":memory:")
    kpis = con.execute("SELECT COUNT(*) as trips, SUM(fare_amount) as revenue, AVG(fare_amount) as avg_fare, COUNT(DISTINCT PULocationID) as zones FROM read_parquet('" + URL + "')").fetchone()
    zones_df = con.execute("SELECT PULocationID as Zone_ID, COUNT(*) as Trips, SUM(fare_amount) as Revenue FROM read_parquet('" + URL + "') GROUP BY PULocationID ORDER BY Trips DESC LIMIT 10").df()
    daily_df = con.execute("SELECT DATE(tpep_pickup_datetime) as day, COUNT(*) as Trips FROM read_parquet('" + URL + "') WHERE tpep_pickup_datetime IS NOT NULL AND tpep_pickup_datetime >= '2024-01-01' AND tpep_pickup_datetime < '2024-02-01' GROUP BY day ORDER BY day").df()
    hourly_df = con.execute("SELECT HOUR(tpep_pickup_datetime) as hour, COUNT(*) as Trips, AVG(fare_amount) as Avg_Fare FROM read_parquet('" + URL + "') WHERE tpep_pickup_datetime IS NOT NULL GROUP BY hour ORDER BY hour").df()
    pay_df = con.execute("SELECT CASE payment_type WHEN 1 THEN 'Credit Card' WHEN 2 THEN 'Cash' WHEN 3 THEN 'No Charge' WHEN 4 THEN 'Dispute' ELSE 'Other' END as Payment, COUNT(*) as Trips, AVG(CASE WHEN fare_amount > 0 THEN tip_amount / fare_amount ELSE 0 END) * 100 as Tip_Pct, AVG(tip_amount) as Avg_Tip FROM read_parquet('" + URL + "') GROUP BY Payment ORDER BY Trips DESC").df()
    dist_df = con.execute("SELECT CASE WHEN trip_distance < 1 THEN '0-1 mi' WHEN trip_distance < 2 THEN '1-2 mi' WHEN trip_distance < 3 THEN '2-3 mi' WHEN trip_distance < 5 THEN '3-5 mi' WHEN trip_distance < 10 THEN '5-10 mi' ELSE '10+ mi' END as Distance, COUNT(*) as Trips, AVG(fare_amount) as Avg_Fare, AVG(tip_amount) as Avg_Tip, AVG(total_amount) as Avg_Total FROM read_parquet('" + URL + "') WHERE trip_distance >= 0 AND trip_distance < 50 AND fare_amount > 0 AND fare_amount < 200 GROUP BY Distance ORDER BY Trips DESC").df()
    weekday_df = con.execute("SELECT CASE DAYOFWEEK(tpep_pickup_datetime) WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday' WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday' WHEN 6 THEN 'Saturday' END as Day, COUNT(*) as Trips, AVG(fare_amount) as Avg_Fare, AVG(tip_amount) as Avg_Tip FROM read_parquet('" + URL + "') WHERE tpep_pickup_datetime IS NOT NULL GROUP BY Day ORDER BY Trips DESC").df()
    airport_df = con.execute("SELECT CASE WHEN PULocationID = 132 THEN 'JFK Airport' WHEN PULocationID = 138 THEN 'LaGuardia Airport' WHEN PULocationID = 1 THEN 'Newark Airport' ELSE 'City' END as Area, COUNT(*) as Trips, AVG(fare_amount) as Avg_Fare, AVG(tip_amount) as Avg_Tip, AVG(total_amount) as Avg_Total, AVG(trip_distance) as Avg_Distance FROM read_parquet('" + URL + "') WHERE fare_amount > 0 AND fare_amount < 300 GROUP BY Area ORDER BY Trips DESC").df()
    con.close()
    return kpis, zones_df, daily_df, hourly_df, pay_df, dist_df, weekday_df, airport_df

st.sidebar.header("Filters")
data_filter = st.sidebar.selectbox("Data Range", ["All", "Last 7 days", "Last 30 days"])
min_trips = st.sidebar.slider("Min Trips (Top Zones)", 0, 100, 0)
st.sidebar.success("Filters active")

with st.spinner("Loading real Jan 2024 data..."):
    (total_trips, total_revenue, avg_fare, zones), df, daily, hourly, pay, dist, weekday, airport = load_data()

daily_filtered = daily.copy()
if data_filter == "Last 7 days":
    daily_filtered = daily_filtered.tail(7)
elif data_filter == "Last 30 days":
    daily_filtered = daily_filtered.tail(30)
df_filtered = df[df["Trips"] >= min_trips]

c1, c2 = st.columns(2)
c1.metric("Total Trips", f"{total_trips:,}")
c2.metric("Total Revenue", f"${total_revenue:,.0f}")
c3, c4 = st.columns(2)
c3.metric("Avg Fare", f"${avg_fare:.2f}")
c4.metric("Zones", f"{zones}")

st.subheader("Top 10 Pickup Zones")
st.dataframe(df_filtered, use_container_width=True, hide_index=True, column_config={"Revenue": st.column_config.NumberColumn(format="$%.0f")})
zones_plot = df_filtered.copy()
zones_plot["Zone_ID"] = zones_plot["Zone_ID"].astype(str)
zones_plot = zones_plot.sort_values("Trips")
st.bar_chart(zones_plot.set_index("Zone_ID")["Trips"], height=340)

st.subheader("Daily Trips")
daily_filtered["day"] = pd.to_datetime(daily_filtered["day"])
daily_filtered["label"] = daily_filtered["day"].dt.strftime("%b %d")
st.bar_chart(daily_filtered.set_index("label")["Trips"], height=320)

st.subheader("Phase 2 - Hourly Demand")
st.caption("Peak is evening rush")
hourly["hour_label"] = hourly["hour"].astype(str) + ":00"
st.bar_chart(hourly.set_index("hour_label")["Trips"], height=320)
st.dataframe(hourly, use_container_width=True, hide_index=True, column_config={"Avg_Fare": st.column_config.NumberColumn(format="$%.2f")})

st.subheader("Phase 2 - Payment Type and Tips")
st.caption("Card riders tip more")
st.dataframe(pay, use_container_width=True, hide_index=True, column_config={"Tip_Pct": st.column_config.NumberColumn(format="%.1f%%"), "Avg_Tip": st.column_config.NumberColumn(format="$%.2f")})
st.bar_chart(pay.set_index("Payment")["Trips"], height=280)
st.bar_chart(pay.set_index("Payment")["Tip_Pct"], height=280)

st.subheader("Phase 3 - Trip Distance vs Fare")
st.caption("Short trips are most common")
st.dataframe(dist,
