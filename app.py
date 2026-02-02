import streamlit as st
import pandas as pd
import re

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Maintenance Decision Console",
    layout="wide",
    page_icon="🛠️"
)

st.title("Maintenance Decision Console")
st.caption("Module → Sub Module → Components → Summary")
st.divider()

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
uploaded_file = st.sidebar.file_uploader(
    "Upload Excel file",
    type=["xlsx"]
)

if not uploaded_file:
    st.info("Upload an Excel file to begin.")
    st.stop()

df = pd.read_excel(uploaded_file)

# --------------------------------------------------
# NORMALIZE TEXT (CRITICAL)
# --------------------------------------------------
def normalize(val):
    if pd.isna(val):
        return None
    val = str(val)
    val = re.sub(r"\s+", " ", val)
    return val.strip()

for col in ["Module", "Sub Module", "Components"]:
    df[col] = df[col].apply(normalize)

# --------------------------------------------------
# MODULE FILTER (MULTISELECT)
# --------------------------------------------------
st.subheader("Module")

modules = sorted(df["Module"].dropna().unique())

selected_modules = st.multiselect(
    "Select module(s)",
    options=modules,
    default=[]
)

if not selected_modules:
    st.stop()

# IMPORTANT: do NOT over-filter here
df_module = df[df["Module"].isin(selected_modules)]

# --------------------------------------------------
# SUB MODULE FILTER (MULTISELECT, UNION)
# --------------------------------------------------
st.subheader("Sub Module")

submodules = sorted(
    df_module["Sub Module"].dropna().unique()
)

selected_submodules = st.multiselect(
    "Select sub module(s)",
    options=submodules,
    default=[]
)

if not selected_submodules:
    st.stop()

df_submodule = df_module[
    df_module["Sub Module"].isin(selected_submodules)
]

# --------------------------------------------------
# COMPONENT FILTER (MULTISELECT, UNION)
# --------------------------------------------------
st.subheader("Components")

components = sorted(
    df_submodule["Components"].dropna().unique()
)

selected_components = st.multiselect(
    "Select component(s)",
    options=components,
    default=[]
)

if not selected_components:
    st.stop()

df_final = df_submodule[
    df_submodule["Components"].isin(selected_components)
].copy()

# --------------------------------------------------
# FINAL TABLE (FIXED SERIAL NUMBER)
# --------------------------------------------------
df_final = df_final.reset_index(drop=True)
df_final.insert(0, "No", range(1, len(df_final) + 1))

st.divider()
st.subheader("Filtered Maintenance Data")

st.dataframe(
    df_final,
    use_container_width=True,
    hide_index=True   # 🔥 THIS REMOVES EXTRA NUMBER COLUMN
)
