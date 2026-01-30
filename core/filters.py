def get_main_components(df):
    return sorted(df["Main_Component"].unique())

def get_subcomponents(df, main_component):
    return sorted(
        df[df["Main_Component"] == main_component]["Sub_Component"].unique()
    )

def filter_data(df, main_component, subcomponents):
    filtered = df[df["Main_Component"] == main_component]
    if subcomponents:
        filtered = filtered[filtered["Sub_Component"].isin(subcomponents)]
    return filtered
