import streamlit as st


def show_table(df, title="Selected Data"):
    st.subheader(title)
    st.dataframe(df, use_container_width=True)
