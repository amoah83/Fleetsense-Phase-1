CR-2 Impact Assessment - Issued 22 Nov

CR-2 Summary Request: Build FleetSense Streamlit dashboard for trips, revenue, average fare per zone with map view.

What Changes

1. app.py: New Streamlit app with 3 tabs - Overview, Map, Insights
   - Overview: Top 10 pickup zones, Daily Trips, Hourly Demand
   - Map: Lat/lon for Top 10 zones, Revenue ($) table
   - Insights: Payment and Tips, Distance vs Fare, Weekday vs Weekend, Airport vs City

2. metrics.py: Keep KPIs from CR-1
   - revenue_excluding_tolls = SUM(fare_amount + tip_amount)
   - revenue_including_tolls = SUM(fare_amount + tip + tolls + extra + mta_tax + improvement_surcharge + congestion_surcharge + airport_fee)

3. Display: Format all money as USD ($)
   - Total Revenue: $53.8M, Avg Fare: $18.40
   - Tables: Revenue ($) as $2,181,762 instead of 2181762.54

4. Docs/design.md: Update revenue definition to include tolls logic from CR-1

Effort

- Dev: 1 day (build Streamlit app, DuckDB query, map)
- Testing: 0.5 day (validate totals match pipeline, check $ formatting)
- Docs: 0.5 day
- Total: 2 days

Risk

- Low-Medium
- Risk 1: Map lat/lon mismatch for zones -> need hardcoded lat/lon for Top 10 zones. Mitigation: use verified Times Sq / Midtown coordinates.
- Risk 2: Large Parquet (2.9M rows) slow load. Mitigation: use DuckDB + @st.cache_data.
- Risk 3: Revenue formatting breaks sorting if formatted as string. Mitigation: format only for display copy, keep numeric for charts.
- Backward compat: No breaking, additive display only.

Decision Approved for Implementation in Week 3 Task 3.