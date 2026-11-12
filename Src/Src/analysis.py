import duckdb
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DB = "data/processed/fleetsense.duckdb"
os.makedirs("data/processed/charts", exist_ok=True)
os.makedirs("Docs", exist_ok=True)

con = duckdb.connect(DB)

 1. Seasonality by hour, weekday, month
hourly = con.execute("""
SELECT EXTRACT(hour FROM tpep_pickup_datetime) as hour, COUNT(*) as trips
FROM fact_trips GROUP BY 1 ORDER BY 1
""").df()

weekday = con.execute("""
SELECT EXTRACT(dow FROM tpep_pickup_datetime) as weekday, COUNT(*) as trips
FROM fact_trips GROUP BY 1 ORDER BY 1
""").df()

monthly = con.execute("""
SELECT date_trunc('month', tpep_pickup_datetime)::DATE as month, COUNT(*) as trips
FROM fact_trips GROUP BY 1 ORDER BY 1
""").df()

 2. Top and bottom zones
top_zones = con.execute("""
SELECT PULocationID as zone_id, COUNT(*) as trips
FROM fact_trips GROUP BY 1 ORDER BY trips DESC LIMIT 10
""").df()

bottom_zones = con.execute("""
SELECT PULocationID as zone_id, COUNT(*) as trips
FROM fact_trips GROUP BY 1 ORDER BY trips ASC LIMIT 10
""").df()

 3. Charts
plt.figure()
plt.bar(hourly['hour'], hourly['trips'])
plt.title('Seasonality by Hour')
plt.xlabel('Hour'); plt.ylabel('Trips')
plt.savefig('data/processed/charts/seasonality_hour.png')
plt.close()

plt.figure()
plt.bar(weekday['weekday'], weekday['trips'])
plt.title('Seasonality by Weekday')
plt.xlabel('Weekday 0=Sun'); plt.ylabel('Trips')
plt.savefig('data/processed/charts/seasonality_weekday.png')
plt.close()

plt.figure()
plt.plot(monthly['month'].astype(str), monthly['trips'], marker='o')
plt.title('Seasonality by Month')
plt.xticks(rotation=45); plt.tight_layout()
plt.savefig('data/processed/charts/seasonality_month.png')
plt.close()

plt.figure()
plt.bar(top_zones['zone_id'].astype(str), top_zones['trips'])
plt.title('Top 10 Zones')
plt.xticks(rotation=45); plt.tight_layout()
plt.savefig('data/processed/charts/top_zones.png')
plt.close()

 4. Anomaly detection - flag hours > 3 std dev
stats = con.execute("""
SELECT AVG(cnt) as mean, STDDEV(cnt) as std FROM
(SELECT COUNT(*) as cnt FROM fact_trips GROUP BY date_trunc('hour', tpep_pickup_datetime))
""").fetchall()
mean = stats[0][0] or 0
std = stats[0][1] or 1
threshold = mean + 3*std

anomalies = con.execute(f"""
SELECT date_trunc('hour', tpep_pickup_datetime) as hour, COUNT(*) as trips
FROM fact_trips
GROUP BY 1
HAVING COUNT(*) > {threshold}
ORDER BY trips DESC
""").df()

anomalies.to_csv('data/processed/anomalies.csv', index=False)
hourly.to_csv('data/processed/seasonality_hour.csv', index=False)

print(f"Top zones: {top_zones.head(3).values}")
print(f"Bottom zones: {bottom_zones.head(3).values}")
print(f"Anomalies found: {len(anomalies)} hours > mean+3std ({threshold:.1f})")
print("Charts saved to data/processed/charts/")