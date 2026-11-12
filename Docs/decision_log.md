 Decision Log - Week 3

 Seasonality Analysis
- Hour: Peak 18-19h evening rush, low 4-5am. Matches NYC commute.
- Weekday: Friday highest, Sunday lowest.
- Month: Q4 months highest (Oct-Dec) due to holidays.

 Top / Bottom Zones
- Top 3 zones: high demand Manhattan Midtown, JFK, LaGuardia - consistent with business/airport.
- Bottom zones: low population outer boroughs, possible data gaps.
- Decision: Keep all zones, no filter. Low zones still needed for coverage KPI.

 Charts
- Saved: seasonality_hour.png, seasonality_weekday.png, seasonality_month.png, top_zones.png in data/processed/charts/

 Anomalies
- Method: mean + 3*stddev per hourly count.
- Found: spikes on New Year's Eve, Thanksgiving, heavy rain days.
- Handling: Flagged in anomalies.csv, not removed. Reason: real demand, not error. Log in validation run_log as info, keep in fact_trips but exclude from avg calculations if needed.
- Action: Monitor, no quarantine. Add note to design doc for future capping.

 Date
- Analyzed: Nov 2026