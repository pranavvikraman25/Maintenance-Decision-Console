import streamlit as st


def component_selector(main_components):
    st.subheader("Main Components")

    cols = st.columns(len(main_components))
    selected_component = None

    for i, comp in enumerate(main_components):
        if cols[i].button(comp):
            selected_component = comp

    return selected_component
