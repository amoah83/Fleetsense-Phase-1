import duckdb

URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"

def test_jan2024_loads():
    con = duckdb.connect(":memory:")
    count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{URL}')").fetchone()[0]
    print(f"Jan 2024 rows: {count}")
    assert count > 2000000

def test_jan2024_has_expected_columns():
    con = duckdb.connect(":memory:")
    cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{URL}') LIMIT 1").fetchall()]
    for c in ["tpep_pickup_datetime", "tpep_dropoff_datetime", "fare_amount", "trip_distance", "PULocationID", "DOLocationID"]:
        assert c in cols

def test_jan2024_data_quality_sample():
    con = duckdb.connect(":memory:")
    bad = con.execute(
        f"""SELECT COUNT(*) FROM read_parquet('{URL}')
        WHERE tpep_dropoff_datetime <= tpep_pickup_datetime
        OR fare_amount < 0 OR trip_distance < 0"""
    ).fetchone()[0]
    total = con.execute(f"SELECT COUNT(*) FROM read_parquet('{URL}')").fetchone()[0]
    print(f"Bad rows: {bad} / {total}")
    assert bad < total * 0.05
