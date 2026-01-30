import pandas as pd

COL_MAIN_COMPONENT = 1  # main component column index

def load_excel(file):
    df = pd.read_excel(file)

    # Fix merged cells in main component column
    df.iloc[:, COL_MAIN_COMPONENT] = (
        df.iloc[:, COL_MAIN_COMPONENT].ffill()
    )

    return df
