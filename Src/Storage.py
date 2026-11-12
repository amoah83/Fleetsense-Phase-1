import duckdb
import polars as pl
import os

DB_PATH = "data/fleetsense.duckdb"
os.makedirs("data", exist_ok=True)

def save_to_duckdb(df: pl.DataFrame, table: str = "yellow_taxi"):
    con = duckdb.connect(DB_PATH)
    con.execute(f"CREATE TABLE IF NOT EXISTS {table} AS SELECT * FROM df LIMIT 0")
    con.execute(f"INSERT INTO {table} SELECT * FROM df")
    con.close()
    print(f"Saved {df.shape[0]} rows to {table}")

def get_stats():
    con = duckdb.connect(DB_PATH)
    try:
        result = con.execute("SELECT COUNT(*) as total_trips, AVG(trip_distance) as avg_dist FROM yellow_taxi").fetchall()
        print(result)
        return result
    except:
        print("No data yet")
        return None
    finally:
        con.close()
