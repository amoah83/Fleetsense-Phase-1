 CR-1 Impact Assessment - Issued 22 Nov

 CR-1 Summary
Request: Build revenue with and without tolls and surcharges per zone.

 What Changes
1. transform.py: Keep columns tolls_amount, extra, mta_tax, improvement_surcharge, congestion_surcharge, airport_fee (currently dropped in Phase 1)
2. metrics.py: Add 2 new KPIs:
   - revenue_excluding_tolls = SUM(fare_amount + tip_amount)
   - revenue_including_tolls = SUM(fare_amount + tip + tolls + extra + mta_tax + improvement_surcharge + congestion_surcharge + airport_fee)
3. New table: revenue_per_zone = PULocationID, revenue_with_tolls, revenue_without_tolls
4. Docs/design.md: Update revenue definition

 Effort
- Dev: 1 day (modify transform, metrics, rerun pipeline)
- Testing: 0.5 day (validate tolls not null, sum check)
- Docs: 0.5 day
- Total: 2 days

 Risk
- Low-Medium
- Risk 1: tolls_amount has 95% nulls -> need COALESCE(tolls_amount,0). Mitigation: use COALESCE.
- Risk 2: Double counting if tip included twice. Mitigation: define formula clearly in design.
- Risk 3: Historical data without surcharges (pre-2019) -> revenue gap. Mitigation: note in decision_log.
- Backward compat: No breaking, additive columns only.

 Decision
Approved for implementation in Week 3 Task 3.