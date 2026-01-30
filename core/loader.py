import pandas as pd

def load_excel(file):
    df = pd.read_excel(file)

    if df.shape[1] < 7:
        raise ValueError("Excel must have at least 7 columns")

    return df
