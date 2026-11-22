import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(
    page_title="FleetSense NYC",
    page_icon="🚕",
    layout="wide"
)

st.title("🚕 FleetSense")
st.caption("NYC Yellow Taxi - Jan 2024 - USD ($)")

URL = "https://d37ci6vzurychx.cloudfront.net/"
URL += "trip-data/yellow_tripdata_2024-01.parquet"

@st.cache_data
def L():
    con = duckdb.connect(":memory:")
    U = "FROM read_parquet('"
    U += URL
    U += "')"
    k = con.execute(
        "SELECT COUNT(*), "
        "SUM(fare_amount), "
        "AVG(fare_amount), "
        "COUNT(DISTINCT PULocationID) " + U
    ).fetchone()
    z = con.execute(
        "SELECT PULocationID as Z, "
        "COUNT(*) as T, "
        "SUM(fare_amount) as R "
        + U +
        " GROUP BY Z "
        "ORDER BY T DESC LIMIT 10"
    ).df()
    d = con.execute(
        "SELECT DATE(tpep_pickup_datetime) as day, "
        "COUNT(*) as T "
        + U +
        " WHERE tpep_pickup_datetime "
        "BETWEEN '2024-01-01' "
        "AND '2024-01-31 23:59:59' "
        "GROUP BY day ORDER BY day"
    ).df()
    h = con.execute(
        "SELECT HOUR(tpep_pickup_datetime) as hr, "
        "COUNT(*) as T, "
        "AVG(fare_amount) as A "
        + U +
        " GROUP BY hr ORDER BY hr"
    ).df()
    p = con.execute(
        "SELECT CASE payment_type "
        "WHEN 1 THEN 'Card' "
        "WHEN 2 THEN 'Cash' "
        "ELSE 'Other' END as P, "
        "COUNT(*) as T, "
        "AVG(tip_amount) as Tip "
        + U +
        " GROUP BY P ORDER BY T DESC"
    ).df()
    con.close()
    return k, z, d, h, p
 @st.cache_data
def M():
    con = duckdb.connect(":memory:")
    U = "FROM read_parquet('"
    U += URL
    U += "')"
    s = con.execute(
        "SELECT CASE "
        "WHEN trip_distance BETWEEN 0 AND 0.99 "
        "THEN '0-1 mi' "
        "WHEN trip_distance BETWEEN 1 AND 1.99 "
        "THEN '1-2 mi' "
        "WHEN trip_distance BETWEEN 2 AND 4.99 "
        "THEN '2-5 mi' "
        "ELSE '5+ mi' END as D, "
        "COUNT(*) as T, "
        "AVG(total_amount) as A "
        + U +
        " WHERE trip_distance BETWEEN 0 AND 50 "
        "GROUP BY D ORDER BY T DESC"
    ).df()
    w = con.execute(
        "SELECT CASE DAYOFWEEK(tpep_pickup_datetime) "
        "WHEN 0 THEN 'Sunday' "
        "WHEN 1 THEN 'Monday' "
        "WHEN 2 THEN 'Tuesday' "
        "WHEN 3 THEN 'Wednesday' "
        "WHEN 4 THEN 'Thursday' "
        "WHEN 5 THEN 'Friday' "
        "ELSE 'Saturday' END as D, "
        "COUNT(*) as T, "
        "AVG(tip_amount) as Tip "
        + U +
        " GROUP BY D ORDER BY T DESC"
    ).df()
    a = con.execute(
        "SELECT CASE "
        "WHEN PULocationID = 132 THEN 'JFK' "
        "WHEN PULocationID = 138 THEN 'LaGuardia' "
        "WHEN PULocationID = 1 THEN 'Newark' "
        "ELSE 'City' END as A, "
        "COUNT(*) as T, "
        "AVG(total_amount) as Amt "
        + U +
        " WHERE fare_amount BETWEEN 1 AND 300 "
        "GROUP BY A ORDER BY T DESC"
    ).df()
    con.close()
    return s, w, a

f = st.sidebar.selectbox(
    "Data Range",
    ["All", "Last 7 days", "Last 30 days"]
)
st.sidebar.divider()
st.sidebar.write("Tip: Use tabs to explore")

k, z, d, h, p = L()
s, w, a = M()

dd = d.copy()
if f == "Last 7 days":
    dd = dd.tail(7)
if f == "Last 30 days":
    dd = dd.tail(30)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Trips", f"{k[0]:,}")
c2.metric("Total Revenue", f"${k[1]:,.0f}")
c3.metric("Avg Fare", f"${k[2]:,.2f}")
c4.metric("Zones", f"{k[3]:,}")

st.divider()
t1, t2, t3 = st.tabs(
    ["Overview", "Map", "Insights"]
)

with t1:
    st.subheader("Top 10 Pickup Zones")
    zd = z.copy()
    zd["Revenue ($)"] = zd["R"].map(
        lambda x: f"${x:,.0f}"
    )
    zd = zd.drop(columns=["R"])
    st.dataframe(zd, use_container_width=True)
    z2 = z.copy()
    z2["Z"] = z2["Z"].astype(str)
    z2 = z2.sort_values("T")
    st.bar_chart(
        z2.set_index("Z")["T"]
    )
    st.subheader("Daily Trips")
    dd["day"] = pd.to_datetime(dd["day"])
    dd["lb"] = dd["day"].dt.strftime("%b %d")
    st.bar_chart(dd.set_index("lb")["T"])
    st.subheader("Hourly Demand")
    hd = h.copy()
    hd["Avg Fare ($)"] = hd["A"].map(
        lambda x: f"${x:,.2f}"
    )
    hd = hd.drop(columns=["A"])
    h["lb"] = h["hr"].astype(str) + ":00"
    st.bar_chart(h.set_index("lb")["T"])
    st.dataframe(hd, use_container_width=True)

with t2:
    st.subheader("Where The Money Is")
    ids = [230, 161, 162, 48, 170]
    ids += [100, 186, 164, 114, 68]
    nm = ["Times Sq", "Midtown C", "Midtown E"]
    nm += ["Clinton E", "Murray Hill", "Garment"]
    nm += ["Penn", "Midtown N", "Greenwich"]
    nm += ["E Chelsea"]
    la = [40.758, 40.7549, 40.7527, 40.766, 40.747]
    la += [40.752, 40.7505, 40.762, 40.734, 40.744]
    lo = [-73.9855, -73.984, -73.9772, -73.988]
    lo += [-73.978, -73.99, -73.9934, -73.979]
    lo += [-73.999, -73.996]
    lk = pd.DataFrame()
    lk["Z"] = ids
    lk["Zone Name"] = nm
    lk["lat"] = la
    lk["lon"] = lo
    m = pd.merge(z, lk, on="Z", how="left")
    m = m.dropna(subset=["lat"])
    st.map(m)
    st.dataframe(m, use_container_width=True)
    st.caption("Red dots = Top 10 busiest zones")

with t3:
    st.subheader("Payment and Tips")
    pd2 = p.copy()
    pd2["Avg Tip ($)"] = pd2["Tip"].map(
        lambda x: f"${x:,.2f}"
    )
    pd2 = pd2.drop(columns=["Tip"])
    st.dataframe(pd2, use_container_width=True)
    st.bar_chart(p.set_index("P")["T"])
    st.bar_chart(p.set_index("P")["Tip"])
    st.subheader("Distance vs Fare")
    sd = s.copy()
    sd["Avg Total ($)"] = sd["A"].map(
        lambda x: f"${x:,.2f}"
    )
    sd = sd.drop(columns=["A"])
    st.dataframe(sd, use_container_width=True)
    st.bar_chart(s.set_index("D")["T"])
    st.bar_chart(s.set_index("D")["A"])
    st.subheader("Weekday vs Weekend")
    wd = w.copy()
    wd["Avg Tip ($)"] = wd["Tip"].map(
        lambda x: f"${x:,.2f}"
    )
    wd = wd.drop(columns=["Tip"])
    st.dataframe(wd, use_container_width=True)
    st.bar_chart(w.set_index("D")["T"])
    st.bar_chart(w.set_index("D")["Tip"])
    st.subheader("Airport vs City")
    ad = a.copy()
    ad["Avg Total ($)"] = ad["Amt"].map(
        lambda x: f"${x:,.2f}"
    )
    ad = ad.drop(columns=["Amt"])
    st.dataframe(ad, use_container_width=True)
    st.bar_chart(a.set_index("A")["T"])
    st.bar_chart(a.set_index("A")["Amt"])

st.divider()
st.download_button(
    "Download Top Zones CSV",
    z.to_csv(index=False),
    "top_zones.csv",
    "text/csv"
)
st.success("FleetSense Presentable Version Complete")
