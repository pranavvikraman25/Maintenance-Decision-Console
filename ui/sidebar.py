import streamlit as st


def sidebar_upload():
    st.sidebar.header("Data Input")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Excel file",
        type=["xlsx"]
    )
    return uploaded_file
