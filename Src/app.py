import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(page_title="Fleetsense Dashboard", layout="wide")
st.title("Fleetsense - NYC Taxi Demand")

DB = "data/processed/fleetsense.duckdb"
con = duckdb.connect(DB)

 Sidebar Filters - REQUIRED
st.sidebar.header("Filters")
date_filter = st.sidebar.date_input("Date Range")
zone_filter = st.sidebar.multiselect("Zone ID", options=[1,2,3,4,5,10,13,42,43,48,68,74,100,132,138,161,162,170,186,230,236,237,239,262], default=[])

 Build filter SQL
where_clause = "WHERE 1=1"
if zone_filter:
    where_clause += f" AND PULocationID IN ({','.join(map(str,zone_filter))})"

 1. Zone Ranked Table - REQUIRED
st.subheader("Zone Ranked Table")
ranked = con.execute(f"""
SELECT PULocationID as zone_id, COUNT(*) as trips, SUM(fare_amount) as revenue
FROM fact_trips {where_clause}
GROUP BY 1 ORDER BY trips DESC LIMIT 20
""").df()
st.dataframe(ranked, use_container_width=True)

 2. Hourly Demand Profiles - REQUIRED
st.subheader("Hourly Demand Profile")
hourly = con.execute(f"""
SELECT EXTRACT(hour FROM tpep_pickup_datetime) as hour, COUNT(*) as trips
FROM fact_trips {where_clause}
GROUP BY 1 ORDER BY 1
""").df()
st.line_chart(hourly, x='hour', y='trips')

 3. CR-1 Revenue View Live - REQUIRED
st.subheader("CR-1 Revenue View (With vs Without Tolls)")
try:
    rev = con.execute("""
    SELECT zone_id, revenue_without_tolls, revenue_with_tolls 
    FROM revenue_per_zone ORDER BY revenue_with_tolls DESC LIMIT 20
    """).df()
    st.dataframe(rev)
    st.bar_chart(rev, x='zone_id', y=['revenue_without_tolls','revenue_with_tolls'])
except:
    st.warning("Run metrics.py to generate revenue_per_zone")
     fallback
    rev_fallback = con.execute(f"""
    SELECT PULocationID as zone_id,
    SUM(fare_amount) as revenue_without_tolls,
    SUM(fare_amount + COALESCE(tolls_amount,0)) as revenue_with_tolls
    FROM fact_trips {where_clause} GROUP BY 1 ORDER BY 2 DESC LIMIT 20
    """).df()
    st.dataframe(rev_fallback)

 KPI
st.subheader("KPIs")
kpis = con.execute(f"SELECT COUNT(*) as trips, SUM(fare_amount) as revenue, AVG(fare_amount) as avg_fare FROM fact_trips {where_clause}").df()
st.metric("Trips", f"{kpis['trips'][0]:,}")
st.metric("Revenue", f"${kpis['revenue'][0]:,.2f}")
st.metric("Avg Fare", f"${kpis['avg_fare'][0]:.2f}")

st.caption("Deployed via Streamlit Cloud - Fleetsense Phase 1 v1.0.0")