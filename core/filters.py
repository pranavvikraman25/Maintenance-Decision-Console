# core/filters.py

# column index mapping (0-based)
COL_MAIN_COMPONENT = 1
COL_SUB_COMPONENT = 2


def get_main_components(df):
    return sorted(
        df.iloc[:, COL_MAIN_COMPONENT]
        .dropna()
        .unique()
    )


def get_subcomponents(df, main_component):
    return sorted(
        df[df.iloc[:, COL_MAIN_COMPONENT] == main_component]
        .iloc[:, COL_SUB_COMPONENT]
        .dropna()
        .unique()
    )


def filter_data(df, main_component, subcomponents):
    filtered = df[df.iloc[:, COL_MAIN_COMPONENT] == main_component]

    if subcomponents:
        filtered = filtered[
            filtered.iloc[:, COL_SUB_COMPONENT].isin(subcomponents)
        ]

    return filtered
