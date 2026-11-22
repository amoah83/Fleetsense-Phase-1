import streamlit as st, duckdb, pandas as pd
st.set_page_config(page_title="FleetSense", page_icon="🚕", layout="wide")
st.title("FleetSense")
U="FROM read_parquet('https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet')"
@st.cache_data
def L():
 con=duckdb.connect(":memory:")
 k=con.execute("SELECT COUNT(*),SUM(fare_amount),AVG(fare_amount),COUNT(DISTINCT PULocationID) "+U).fetchone()
 z=con.execute("SELECT PULocationID as Z,COUNT(*) as T,SUM(fare_amount) as R "+U+" GROUP BY Z ORDER BY T DESC LIMIT 10").df()
 d=con.execute("SELECT DATE(tpep_pickup_datetime) as day,COUNT(*) as T "+U+" WHERE tpep_pickup_datetime BETWEEN '2024-01-01' AND '2024-01-31 23:59:59' GROUP BY day ORDER BY day").df()
 h=con.execute("SELECT HOUR(tpep_pickup_datetime) as hr,COUNT(*) as T,AVG(fare_amount) as A "+U+" GROUP BY hr ORDER BY hr").df()
 p=con.execute("SELECT CASE payment_type WHEN 1 THEN 'Card' WHEN 2 THEN 'Cash' ELSE 'Other' END as P,COUNT(*) as T,AVG(tip_amount) as Tip "+U+" GROUP BY P ORDER BY T DESC").df()
 s=con.execute("SELECT CASE WHEN trip_distance BETWEEN 0 AND 0.99 THEN '0-1' WHEN trip_distance BETWEEN 1 AND 1.99 THEN '1-2' WHEN trip_distance BETWEEN 2 AND 4.99 THEN '2-5' ELSE '5+' END as D,COUNT(*) as T,AVG(total_amount) as A "+U+" WHERE trip_distance BETWEEN 0 AND 50 GROUP BY D ORDER BY T DESC").df()
 w=con.execute("SELECT CASE DAYOFWEEK(tpep_pickup_datetime) WHEN 0 THEN 'Sun' WHEN 1 THEN 'Mon' WHEN 2 THEN 'Tue' WHEN 3 THEN 'Wed' WHEN 4 THEN 'Thu' WHEN 5 THEN 'Fri' ELSE 'Sat' END as D,COUNT(*) as T,AVG(tip_amount) as Tip "+U+" GROUP BY D ORDER BY T DESC").df()
 a=con.execute("SELECT CASE WHEN PULocationID=132 THEN 'JFK' WHEN PULocationID=138 THEN 'LGA' WHEN PULocationID=1 THEN 'Newark' ELSE 'City' END as A,COUNT(*) as T,AVG(total_amount) as Amt,AVG(trip_distance) as Dist "+U+" WHERE fare_amount BETWEEN 1 AND 300 GROUP BY A ORDER BY T DESC").df()
 con.close()
 return k,z,d,h,p,s,w,a
f=st.sidebar.selectbox("Range",["All","Last 7 days","Last 30 days"])
k,z,d,h,p,s,w,a=L()
dd=d.copy()
if f=="Last 7 days": dd=dd.tail(7)
if f=="Last 30 days": dd=dd.tail(30)
c1,c2=st.columns(2)
c1.metric("Trips",str(k[0]));c2.metric("Revenue",str(int(k[1])))
c3,c4=st.columns(2)
c3.metric("Avg Fare",str(round(k[2],2)));c4.metric("Zones",str(k[3]))
st.subheader("Top 10 Zones");st.dataframe(z,use_container_width=True)
z2=z.copy();z2["Z"]=z2["Z"].astype(str);z2=z2.sort_values("T")
st.bar_chart(z2.set_index("Z")["T"])
st.subheader("Phase 6 - Real Map")
ids=[230,161,162,48,170,100,186,164,114,68]
nm=["Times Sq","Midtown C","Midtown E","Clinton E","Murray Hill","Garment","Penn","Midtown N","Greenwich","E Chelsea"]
la=[40.758,40.7549,40.7527,40.766,40.747,40.752,40.7505,40.762,40.734,40.744]
lo=[-73.9855,-73.984,-73.9772,-73.988,-73.978,-73.99,-73.9934,-73.979,-73.999,-73.996]
lk=pd.DataFrame();lk["Z"]=ids;lk["Name"]=nm;lk["lat"]=la;lk["lon"]=lo
m=pd.merge(z,lk,on="Z",how="left").dropna(subset=["lat"])
st.map(m)
st.dataframe(m,use_container_width=True)
st.subheader("Daily");dd["day"]=pd.to_datetime(dd["day"]);dd["lb"]=dd["day"].dt.strftime("%b %d")
st.bar_chart(dd.set_index("lb")["T"])
st.subheader("Hourly");h["lb"]=h["hr"].astype(str)+":00";st.bar_chart(h.set_index("lb")["T"]);st.dataframe(h,use_container_width=True)
st.subheader("Payment");st.dataframe(p,use_container_width=True);st.bar_chart(p.set_index("P")["T"]);st.bar_chart(p.set_index("P")["Tip"])
st.subheader("Distance");st.dataframe(s,use_container_width=True);st.bar_chart(s.set_index("D")["T"]);st.bar_chart(s.set_index("D")["A"])
st.subheader("Weekday");st.dataframe(w,use_container_width=True);st.bar_chart(w.set_index("D")["T"]);st.bar_chart(w.set_index("D")["Tip"])
st.subheader("Airport");st.dataframe(a,use_container_width=True);st.bar_chart(a.set_index("A")["T"]);st.bar_chart(a.set_index("A")["Amt"])
st.download_button("Download Zones CSV",z.to_csv(index=False),"zones.csv","text/csv")
st.success("FleetSense Phase 6 Complete - Real Map")
