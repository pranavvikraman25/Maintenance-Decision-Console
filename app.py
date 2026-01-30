import streamlit as st

from loader import load_excel
from filters import (
    get_main_components,
    get_subcomponents,
    filter_data
)

from ui.sidebar import sidebar_upload
from ui.components import component_selector
from ui.tables import show_table


st.set_page_config(layout="wide")
st.title("Maintenance Time Visualization")

uploaded_file = sidebar_upload()

if uploaded_file:
    df = load_excel(uploaded_file)

    st.caption("Detected columns:")
    st.write(list(df.columns))

    main_components = get_main_components(df)
    selected_component = component_selector(main_components)

    if selected_component:
        sub_components = get_subcomponents(df, selected_component)

        selected_subs = st.multiselect(
            "Select Sub Components",
            options=sub_components,
            default=[sub_components[0]] if sub_components else []
        )

        result_df = filter_data(df, selected_component, selected_subs)
        show_table(result_df)
