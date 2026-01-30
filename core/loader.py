import pandas as pd

COL_MAIN_COMPONENT = 1  # merged cells column

def load_excel(file):
    xls = pd.ExcelFile(file)

    # -------- Sheet 1: main data --------
    main_df = pd.read_excel(xls, sheet_name=0)

    # Fix merged cells (CRITICAL)
    main_df.iloc[:, COL_MAIN_COMPONENT] = (
        main_df.iloc[:, COL_MAIN_COMPONENT].ffill()
    )

    # -------- Sheet 2: split data --------
    split_df = None
    if "Split_Data" in xls.sheet_names:
        split_df = pd.read_excel(xls, sheet_name="Split_Data")

    return main_df, split_df
