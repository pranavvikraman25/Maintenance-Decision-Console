import pandas as pd

REQUIRED_COLUMNS = {
    "S.no",
    "Main_Component",
    "Sub_Component",
    "Preparation_Time",
    "Activity_Time",
    "Total_Time",
    "Manpower"
}

def load_excel(file):
    df = pd.read_excel(file)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    return df
