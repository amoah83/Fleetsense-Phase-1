import streamlit as st
import duckdb
import pandas as pd
st.set_page_config(page_title="FleetSense NYC", page_icon="🚕", layout="wide")
st.title("FleetSense")
st.caption("NYC Taxi - Jan 2024")
URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
@st.cache_data
def load_data():
    con = duckdb.connect(":memory:")
    U = "FROM read_parquet('" + URL + "')"
    kpis = con.execute("SELECT COUNT(*) as t, SUM(fare_amount) as r, AVG(fare_amount) as a, COUNT(DISTINCT PULocationID) as z " + U).fetchone()
    zdf = con.execute("SELECT PULocationID as Zone_ID, COUNT(*) as Trips, SUM(fare_amount) as Revenue " + U + " GROUP BY PULocationID ORDER BY Trips DESC LIMIT 10").df()
    ddf = con.execute("SELECT DATE(tpep_pickup_datetime) as day, COUNT(*) as Trips " + U + " WHERE tpep_pickup_datetime BETWEEN '2024-01-01' AND '2024-01-31 23:59:59' GROUP BY day ORDER BY day").df()
    hdf = con.execute("SELECT HOUR(tpep_pickup_datetime) as hour, COUNT(*) as Trips, AVG(fare_amount) as Avg_Fare " + U + " GROUP BY hour ORDER BY hour").df()
    pdf = con.execute("SELECT CASE payment_type WHEN 1 THEN 'Credit Card' WHEN 2 THEN 'Cash' ELSE 'Other' END as Payment, COUNT(*) as Trips, AVG(tip_amount) as Avg_Tip " + U + " GROUP BY Payment ORDER BY Trips DESC").df()
    d2 = con.execute("SELECT CASE WHEN trip_distance BETWEEN 0 AND 0.99 THEN '0-1 mi' WHEN trip_distance BETWEEN 1 AND 1.99 THEN '1-2 mi' WHEN trip_distance BETWEEN 2 AND 4.99 THEN '2-5 mi' ELSE '5+ mi' END as Distance, COUNT(*) as Trips, AVG(total_amount) as Avg_Total " + U + " WHERE trip_distance BETWEEN 0 AND 50 GROUP BY Distance ORDER BY Trips DESC").df()
    wdf = con.execute("SELECT CASE DAYOFWEEK(tpep_pickup_datetime) WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday' WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday' ELSE 'Saturday' END as Day, COUNT(*) as Trips, AVG(tip_amount) as Avg_Tip " + U + " GROUP BY Day ORDER BY Trips DESC").df()
    adf = con.execute("SELECT CASE WHEN PULocationID = 132 THEN 'JFK' WHEN PULocationID = 138 THEN 'LaGuardia' WHEN PULocationID = 1 THEN 'Newark' ELSE 'City' END as Area, COUNT(*) as Trips, AVG(total_amount) as Avg_Total, AVG(trip_distance) as Avg_Distance " + U + " WHERE fare_amount BETWEEN 1 AND 300 GROUP BY Area ORDER BY Trips DESC").df()
    con.close()
    return (kpis, zdf, ddf, hdf, pdf, d2, wdf, adf)
    f = st.sidebar.selectbox("Data Range", ["All", "Last 7 days", "Last 30 days"])
out = load_data()
k, df, daily, hourly, pay, dist, weekday, airport = out
d2 = daily.copy()
if f == "Last 7 days":
    d2 = d2.tail(7)
if f == "Last 30 days":
    d2 = d2.tail(30)
c1, c2 = st.columns(2)
c1.metric("Total Trips", str(k[0]))
c2.metric("Total Revenue", str(int(k[1])))
c3, c4 = st.columns(2)
c3.metric("Avg Fare", str(round(k[2], 2)))
c4.metric("Zones", str(k[3]))
st.subheader("Top 10 Pickup Zones")
st.dataframe(df, use_container_width=True)
zp = df.copy()
zp["Zone_ID"] = zp["Zone_ID"].astype(str)
zp = zp.sort_values("Trips")
st.bar_chart(zp.set_index("Zone_ID")["Trips"], height=340)
st.subheader("Phase 5 - Map Data")
ids = [230, 161, 162, 48, 170, 100, 186, 164, 114, 68]
names = ["Times Sq", "Midtown Center", "Midtown East", "Clinton East", "Murray Hill", "Garment District", "Penn Station", "Midtown North", "Greenwich Village", "East Chelsea"]
lats = [40.7580, 40.7549, 40.7527, 40.7660, 40.7470, 40.7520, 40.7505, 40.7620, 40.7340, 40.7440]
lons = [-73.9855, -73.9840, -73.9772, -73.9880, -73.9780, -73.9900, -73.9934, -73.9790, -73.9990, -73.9960]
lk = pd.DataFrame()
lk["Zone_ID"] = ids
lk["Zone_Name"] = names
lk["lat"] = lats
lk["lon"] = lons
mdf = pd.merge(df, lk, on="Zone_ID", how="left")
mdf = mdf.dropna(subset=["lat"])
st.dataframe(mdf, use_container_width=True)
st.subheader("Daily Trips")
d2["day"] = pd.to_datetime(d2["day"])
d2["label"] = d2["day"].dt.strftime("%b %d")
st.bar_chart(d2.set_index("label")["Trips"], height=320)
st.subheader("Phase 2 - Hourly Demand")
hourly["hour_label"] = hourly["hour"].astype(str) + ":00"
st.bar_chart(hourly.set_index("hour_label")["Trips"], height=320)
st.dataframe(hourly, use_container_width=True)
st.subheader("Phase 2 - Payment and Tips")
st.dataframe(pay, use_container_width=True)
st.bar_chart(pay.set_index("Payment")["Trips"], height=280)
st.bar_chart(pay.set_index("Payment")["Avg_Tip"], height=280)
st.subheader("Phase 3 - Distance vs Fare")
st.dataframe(dist, use_container_width=True)
st.bar_chart(dist.set_index("Distance")["Trips"], height=280)
st.bar_chart(dist.set_index("Distance")["Avg_Total"], height=280)
st.subheader("Phase 3 - Weekday vs Weekend")
st.dataframe(weekday, use_container_width=True)
st.bar_chart(weekday.set_index("Day")["Trips"], height=280)
st.bar_chart(weekday.set_index("Day")["Avg_Tip"], height=280)
st.subheader("Phase 4 - Airport vs City")
st.dataframe(airport, use_container_width=True)
st.bar_chart(airport.set_index("Area")["Trips"], height=280)
st.bar_chart(airport.set_index("Area")["Avg_Total"], height=280)
st.subheader("Download Data")
st.download_button("Download Top Zones CSV", df.to_csv(index=False), "top_zones.csv", "text/csv")
st.download_button("Download Daily CSV", daily.to_csv(index=False), "daily.csv", "text/csv")
st.download_button("Download Airport CSV", airport.to_csv(index=False), "airport.csv", "text/csv")
st.success("FleetSense Phase 5 Complete")
