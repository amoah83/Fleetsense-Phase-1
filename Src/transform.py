import duckdb
import os

os.makedirs("data/processed", exist_ok=True)
con = duckdb.connect("data/processed/fleetsense.duckdb")

 Load raw parquet (all 12 months)
con.execute("""
CREATE OR REPLACE TABLE raw_trips AS 
SELECT * FROM read_parquet('data/raw/yellow_2023_*.parquet')
""")

 dim_zones from lookup
con.execute("""
CREATE OR REPLACE TABLE dim_zones AS
SELECT * FROM read_csv('data/raw/taxi_zone_lookup.csv')
""")

 dim_calendar - documented SQL
con.execute("""
CREATE OR REPLACE TABLE dim_calendar AS
SELECT DISTINCT
    CAST(tpep_pickup_datetime AS DATE) as date,
    YEAR(tpep_pickup_datetime) as year,
    MONTH(tpep_pickup_datetime) as month,
    DAY(tpep_pickup_datetime) as day,
    DAYOFWEEK(tpep_pickup_datetime) as day_of_week
FROM raw_trips
""")


 fact_trips - documented SQL
con.execute("""
CREATE OR REPLACE TABLE fact_trips AS
SELECT
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    PULocationID,
    DOLocationID,
    trip_distance,
    fare_amount,
    passenger_count
FROM raw_trips
WHERE trip_distance > 0 AND trip_distance < 100 AND fare_amount > 0
""")

 hourly demand per zone - documented SQL
con.execute("""
CREATE OR REPLACE TABLE hourly_demand_per_zone AS
SELECT
    date_trunc('hour', tpep_pickup_datetime) as hour,
    PULocationID as zone_id,
    COUNT(*) as demand_count
FROM fact_trips
GROUP BY 1,2
ORDER BY 1,2
""")

print("Built: dim_zones, dim_calendar, fact_trips, hourly_demand_per_zone")
print(con.execute("SHOW TABLES").fetchall())