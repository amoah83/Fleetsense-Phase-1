import duckdb
import os

DB = "data/processed/fleetsense.duckdb"
os.makedirs("data/processed", exist_ok=True)

con = duckdb.connect(DB)

 One module computes all 5 metrics
con.execute("""
CREATE OR REPLACE TABLE kpi_per_zone_month AS
SELECT
    CAST(date_trunc('month', tpep_pickup_datetime) AS DATE) as month,
    PULocationID as zone_id,
    COUNT(*) as trips,
    SUM(fare_amount) as revenue,
    AVG(fare_amount) as avg_fare,
    AVG(DATE_DIFF('minute', tpep_pickup_datetime, tpep_dropoff_datetime)) as avg_duration_min,
    COUNT(*) * 1.0 / NULLIF(COUNT(DISTINCT date_trunc('hour', tpep_pickup_datetime)),0) as utilisation_proxy_trips_per_hour
FROM fact_trips
GROUP BY 1,2
ORDER BY 1,2
""")

con.execute("COPY kpi_per_zone_month TO 'data/processed/kpis.csv' (HEADER)")

print("Metrics computed:")
print(con.execute("SELECT * FROM kpi_per_zone_month LIMIT 5").fetchall())
print("Saved to data/processed/kpis.csv")

 Definitions also for doc verification
definitions = {
 "trips": "COUNT(*)",
 "revenue": "SUM(fare_amount)",
 "avg_fare": "AVG(fare_amount)",
 "avg_duration_min": "AVG(DATE_DIFF(minute, pickup, dropoff))",
 "utilisation_proxy": "trips per active hour per zone"
}
print(definitions)