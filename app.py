import streamlit as st
from loader import load_excel
from filters import (
    get_main_components,
    get_subcomponents,
    filter_data
)

st.set_page_config(layout="wide")
st.title("Maintenance Time Visualization")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = load_excel(uploaded_file)

    # Header preview (safe place)
    st.caption("Detected columns:")
    st.write(list(df.columns))

    main_components = get_main_components(df)

    st.subheader("Main Components")
    cols = st.columns(len(main_components))

    selected_component = None
    for i, comp in enumerate(main_components):
        if cols[i].button(comp):
            selected_component = comp

    if selected_component:
        sub_components = get_subcomponents(df, selected_component)

        selected_subs = st.multiselect(
            "Select Sub Components",
            options=sub_components,
            default=[sub_components[0]] if sub_components else []
        )

        result_df = filter_data(df, selected_component, selected_subs)

        st.subheader("Selected Data")
        st.dataframe(result_df, use_container_width=True)
