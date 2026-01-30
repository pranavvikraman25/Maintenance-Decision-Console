import pandas as pd

# column index mapping (0-based)
COL_MAIN_COMPONENT = 1
COL_SUB_COMPONENT  = 2
COL_PREP_TIME      = 3
COL_ACTIVITY_TIME  = 4
COL_TOTAL_TIME     = 5
COL_MANPOWER       = 6


def time_to_minutes(val):
    """
    Safely convert Excel time / string / timedelta to minutes
    """
    if pd.isna(val):
        return 0.0

    try:
        return pd.to_timedelta(val).total_seconds() / 60
    except Exception:
        return 0.0


def add_time_columns(df):
    """
    Adds calculated minute columns without touching original data
    """
    df = df.copy()

    df["prep_minutes"] = df.iloc[:, COL_PREP_TIME].apply(time_to_minutes)
    df["activity_minutes"] = df.iloc[:, COL_ACTIVITY_TIME].apply(time_to_minutes)
    df["total_minutes"] = df.iloc[:, COL_TOTAL_TIME].apply(time_to_minutes)

    return df


def aggregate_by_subcomponent(df):
    """
    Used later for confirmation / reporting
    """
    df = add_time_columns(df)

    grouped = (
        df.groupby(df.iloc[:, COL_SUB_COMPONENT])
        .agg(
            total_prep_minutes=("prep_minutes", "sum"),
            total_activity_minutes=("activity_minutes", "sum"),
            total_minutes=("total_minutes", "sum"),
            avg_manpower=(df.columns[COL_MANPOWER], "mean"),
            task_count=(df.columns[COL_SUB_COMPONENT], "count")
        )
        .reset_index()
    )

    return grouped
