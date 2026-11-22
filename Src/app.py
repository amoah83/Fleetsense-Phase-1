import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(
    page_title="FleetSense NYC",
    page_icon="🚕",
    layout="wide"
)

st.title("FleetSense")
st.caption("NYC Taxi - Jan 2024")

URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"

@st.cache_data
def load_data():
    con = duckdb.connect(":memory:")
    q1 = "SELECT COUNT(*) as trips, "
    q1 += "SUM(fare_amount) as revenue, "
    q1 += "AVG(fare_amount) as avg_fare, "
    q1 += "COUNT(DISTINCT PULocationID) as zones "
    q1 += "FROM read_parquet('" + URL + "')"
    kpis = con.execute(q1).fetchone()
    q2 = "SELECT PULocationID as Zone_ID, "
    q2 += "COUNT(*) as Trips, "
    q2 += "SUM(fare_amount) as Revenue "
    q2 += "FROM read_parquet('" + URL + "') "
    q2 += "GROUP BY PULocationID "
    q2 += "ORDER BY Trips DESC LIMIT 10"
    zones_df = con.execute(q2).df()
    q3 = "SELECT DATE(tpep_pickup_datetime) as day, "
    q3 += "COUNT(*) as Trips "
    q3 += "FROM read_parquet('" + URL + "') "
    q3 += "WHERE tpep_pickup_datetime >= '2024-01-01' "
    q3 += "AND tpep_pickup_datetime < '2024-02-01' "
    q3 += "GROUP BY day ORDER BY day"
    daily_df = con.execute(q3).df()
    q4 = "SELECT HOUR(tpep_pickup_datetime) as hour, "
    q4 += "COUNT(*) as Trips, "
    q4 += "AVG(fare_amount) as Avg_Fare "
    q4 += "FROM read_parquet('" + URL + "') "
    q4 += "GROUP BY hour ORDER BY hour"
    hourly_df = con.execute(q4).df()
    q5 = "SELECT CASE payment_type "
    q5 += "WHEN 1 THEN 'Credit Card' "
    q5 += "WHEN 2 THEN 'Cash' "
    q5 += "ELSE 'Other' END as Payment, "
    q5 += "COUNT(*) as Trips, "
    q5 += "AVG(tip_amount) as Avg_Tip "
    q5 += "FROM read_parquet('" + URL + "') "
    q5 += "GROUP BY Payment ORDER BY Trips DESC"
    pay_df = con.execute(q5).df()
    q6 = "SELECT CASE "
    q6 += "WHEN trip_distance < 1 THEN '0-1 mi' "
    q6 += "WHEN trip_distance < 2 THEN '1-2 mi' "
    q6 += "WHEN trip_distance < 5 THEN '2-5 mi' "
    q6 += "ELSE '5+ mi' END as Distance, "
    q6 += "COUNT(*) as Trips, "
    q6 += "AVG(total_amount) as Avg_Total "
    q6 += "FROM read_parquet('" + URL + "') "
    q6 += "WHERE trip_distance >= 0 "
    q6 += "AND trip_distance < 50 "
    q6 += "GROUP BY Distance "
    q6 += "ORDER BY Trips DESC"
    dist_df = con.execute(q6).df()
    q7 = "SELECT CASE DAYOFWEEK(tpep_pickup_datetime) "
    q7 += "WHEN 0 THEN 'Sunday' "
    q7 += "WHEN 1 THEN 'Monday' "
    q7 += "WHEN 2 THEN 'Tuesday' "
    q7 += "WHEN 3 THEN 'Wednesday' "
    q7 += "WHEN 4 THEN 'Thursday' "
    q7 += "WHEN 5 THEN 'Friday' "
    q7 += "ELSE 'Saturday' END as Day, "
    q7 += "COUNT(*) as Trips, "
    q7 += "AVG(tip_amount) as Avg_Tip "
    q7 += "FROM read_parquet('" + URL + "') "
    q7 += "GROUP BY Day ORDER BY Trips DESC"
    weekday_df = con.execute(q7).df()
    q8 = "SELECT CASE "
    q8 += "WHEN PULocationID = 132 THEN 'JFK' "
    q8 += "WHEN PULocationID = 138 THEN 'LaGuardia' "
    q8 += "WHEN PULocationID = 1 THEN 'Newark' "
    q8 += "ELSE 'City' END as Area, "
    q8 += "COUNT(*) as Trips, "
    q8 += "AVG(total_amount) as Avg_Total, "
    q8 += "AVG(trip_distance) as Avg_Distance "
    q8 += "FROM read_parquet('" + URL + "') "
    q8 += "WHERE fare_amount > 0 "
    q8 += "AND fare_amount < 300 "
    q8 += "GROUP BY Area ORDER BY Trips DESC"
    airport_df = con.execute(q8).df()
    con.close()
    result = (kpis, zones_df, daily_df, hourly_df)
    result += (pay_df, dist_df, weekday_df, airport_df)
    return result

st.sidebar.header("Filters")
data_filter = st.sidebar
