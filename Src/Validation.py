import pandera as pa
import pandas as pd

schema = pa.DataFrameSchema({
    "VendorID": pa.Column(int, pa.Check.in_range(1, 2), nullable=True),
    "tpep_pickup_datetime": pa.Column(pd.DatetimeTZDtype("ns", "UTC"), nullable=True),
    "tpep_dropoff_datetime": pa.Column(pd.DatetimeTZDtype("ns", "UTC"), nullable=True),
    "passenger_count": pa.Column(float, pa.Check.in_range(0, 9), nullable=True),
    "trip_distance": pa.Column(float, pa.Check.ge(0), nullable=True),
    "fare_amount": pa.Column(float, pa.Check.ge(0), nullable=True),
    "total_amount": pa.Column(float, pa.Check.ge(0), nullable=True),
})

def validate(df: pd.DataFrame):
    try:
        schema.validate(df, lazy=True)
        print("Validation passed")
        return True
    except pa.errors.SchemaErrors as e:
        print(f"Validation failed: {e}")
        return False
