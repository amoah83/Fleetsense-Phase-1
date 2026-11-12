 Fleetsense Design - Metrics

 Metric Definitions

1. Trips: COUNT(*) per grouping. Base unit of demand.
   - SQL: `COUNT(*) as trips`

2. Revenue: SUM(fare_amount + tip_amount + tolls_amount + extra + mta_tax + improvement_surcharge + congestion_surcharge + airport_fee)
   - For Phase 1 we use `fare_amount` as proxy if others null. Final revenue = `SUM(fare_amount)` + tolls/surcharges when available.
   - SQL: `SUM(fare_amount) as revenue`

3. Average Fare: revenue / trips
   - SQL: `AVG(fare_amount) as avg_fare`

4. Duration: tpep_dropoff_datetime - tpep_pickup_datetime in minutes
   - SQL: `AVG(EXTRACT(EPOCH FROM (tpep_dropoff_datetime - tpep_pickup_datetime))/60) as avg_duration_min`

5. Utilisation Proxy: trips per active hour per zone = demand density. Higher trips/hour = higher utilisation.
   - SQL: `COUNT(*) * 1.0 / COUNT(DISTINCT date_trunc('hour', tpep_pickup_datetime)) as trips_per_hour`
   - Proxy because we don't have vehicle supply data, only demand.

All metrics computed in `Src/metrics.py` in one module.

 Source Tables
- fact_trips, dim_zones, dim_calendar, hourly_demand_per_zone (from transform.py)

 Output
- data/processed/kpis.csv per zone/month