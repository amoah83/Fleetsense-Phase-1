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
---
## 22 Nov - CR-2: FleetSense Dashboard

**Decision:** Build FleetSense Streamlit dashboard with Overview, Map, Insights tabs. Format all revenue as USD ($). Keep CR-1 revenue definitions unchanged.

**Context:** Mentor needs to see trips, revenue, average fare per zone with map view for Top 10 pickup zones. Previous display showed raw numbers like 2181762.54, hard to read.

**Options Considered:**
1. Format in Python as string - rejected, breaks chart sorting
2. Format only for display copy, keep numeric for charts - APPROVED
3. Use Plotly map - rejected, use simple lat/lon table + Streamlit map for speed

**Impact:** 2 days effort. Low-Medium risk. No breaking change, additive display only.

**Status:** Approved for Implementation in Week 3 Task 3. Linked to Docs/cr2_impact.md