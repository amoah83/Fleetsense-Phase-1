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
 CR-1: Revenue with and without tolls and surcharges per zone
con.execute("""
CREATE OR REPLACE TABLE revenue_per_zone AS
SELECT
    PULocationID as zone_id,
    SUM(COALESCE(fare_amount,0)) as revenue_without_tolls,
    SUM(COALESCE(fare_amount,0) + COALESCE(tip_amount,0) + COALESCE(tolls_amount,0) + COALESCE(extra,0) + COALESCE(mta_tax,0) + COALESCE(improvement_surcharge,0) + COALESCE(congestion_surcharge,0) + COALESCE(airport_fee,0)) as revenue_with_tolls
FROM fact_trips
GROUP BY 1
ORDER BY revenue_with_tolls DESC
""")

con.execute("COPY revenue_per_zone TO 'data/processed/revenue_per_zone.csv' (HEADER)")
print("CR-1 DONE: revenue_per_zone.csv created with with/without tolls")
print(con.execute("SELECT * FROM revenue_per_zone LIMIT 5").fetchall())