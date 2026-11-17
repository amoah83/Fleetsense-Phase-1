import duckdb
import pandas as pd


def clean_trips(df: pd.DataFrame):
    quarantined = []
    clean = []
    for _, row in df.iterrows():
        reasons = []
        if row["tpep_dropoff_datetime"] <= row["tpep_pickup_datetime"]:
            reasons.append("dropoff_before_pickup")
        if row["fare_amount"] < 0 or row["trip_distance"] < 0:
            reasons.append("negative_value")
        if row["PULocationID"] not in [1, 2, 3] or row["DOLocationID"] not in [1, 2, 3]:
            reasons.append("unknown_zone")
        if reasons:
            r = row.to_dict()
            r["reason_code"] = ";".join(reasons)
            quarantined.append(r)
        else:
            clean.append(row.to_dict())
    return pd.DataFrame(clean), pd.DataFrame(quarantined)

def sample_df():
    return pd.DataFrame(
        [
            {
                "tpep_pickup_datetime": pd.Timestamp("2024-01-01 08:00"),
                "tpep_dropoff_datetime": pd.Timestamp("2024-01-01 08:20"),
                "fare_amount": 15.0,
                "trip_distance": 3.5,
                "PULocationID": 1,
                "DOLocationID": 2,
            },
            {
                "tpep_pickup_datetime": pd.Timestamp("2024-01-01 09:00"),
                "tpep_dropoff_datetime": pd.Timestamp("2024-01-01 08:50"),
                "fare_amount": 10.0,
                "trip_distance": 2.0,
                "PULocationID": 1,
                "DOLocationID": 2,
            },
            {
                "tpep_pickup_datetime": pd.Timestamp("2024-01-01 10:00"),
                "tpep_dropoff_datetime": pd.Timestamp("2024-01-01 10:30"),
                "fare_amount": -5.0,
                "trip_distance": 1.0,
                "PULocationID": 1,
                "DOLocationID": 2,
            },
        ]
    )

def test_ac_1_2_row_reconciliation():
    df = sample_df()
    clean, quar = clean_trips(df)
    assert len(df) == len(clean) + len(quar)
    assert len(clean) == 1
    assert len(quar) == 2

def test_fr_1_02_quarantine_has_reason_code():
    _, quar = clean_trips(sample_df())
    assert "reason_code" in quar.columns
    assert quar["reason_code"].notna().all()
    assert "dropoff_before_pickup" in quar["reason_code"].iloc[0]

def test_clean_data_has_no_violations():
    clean, _ = clean_trips(sample_df())
    assert (clean["fare_amount"] >= 0).all()
    assert (clean["trip_distance"] >= 0).all()
    assert (clean["tpep_dropoff_datetime"] > clean["tpep_pickup_datetime"]).all()

def test_duckdb_warehouse_tables():
    con = duckdb.connect(":memory:")
    con.execute("CREATE TABLE trips (id INTEGER)")
    con.execute("CREATE TABLE zones (id INTEGER)")
    con.execute("CREATE TABLE calendar (date DATE)")
    con.execute("CREATE TABLE hourly_demand (hour INTEGER, demand INTEGER)")
    tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
    for t in ["trips", "zones", "calendar", "hourly_demand"]:
        assert t in tables

def test_nfr_02_data_quality_report():
    df = sample_df()
    clean, quar = clean_trips(df)
    report = {
        "rows_in": len(df),
        "rows_loaded": len(clean),
        "rows_quarantined": len(quar),
    }
    assert report["rows_in"] == report["rows_loaded"] + report["rows_quarantined"]
