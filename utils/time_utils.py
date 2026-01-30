import pandas as pd

def to_minutes(time_val):
    if pd.isna(time_val):
        return 0
    if isinstance(time_val, pd.Timedelta):
        return time_val.total_seconds() / 60
    return pd.to_timedelta(time_val).total_seconds() / 60
