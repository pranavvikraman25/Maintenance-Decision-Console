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
# NORMALIZE TEXT (MANDATORY)
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
# MODULE (MULTISELECT – NO DEFAULT)
# --------------------------------------------------
st.subheader("Module")

all_modules = sorted(df["Module"].dropna().unique())

selected_modules = st.multiselect(
    "Select module(s)",
    options=all_modules,
    default=[]
)

# Stop here if nothing selected
if not selected_modules:
    st.stop()

# --------------------------------------------------
# SUB MODULE (MULTISELECT – DEPENDS ON MODULE)
# --------------------------------------------------
st.subheader("Sub Module")

submodule_df = df[df["Module"].isin(selected_modules)]

all_submodules = sorted(
    submodule_df["Sub Module"].dropna().unique()
)

selected_submodules = st.multiselect(
    "Select sub module(s)",
    options=all_submodules,
    default=[]
)

# Stop here if nothing selected
if not selected_submodules:
    st.stop()

# --------------------------------------------------
# COMPONENTS (MULTISELECT – DEPENDS ON SUB MODULE)
# --------------------------------------------------
st.subheader("Components")

component_df = submodule_df[
    submodule_df["Sub Module"].isin(selected_submodules)
]

all_components = sorted(
    component_df["Components"].dropna().unique()
)

selected_components = st.multiselect(
    "Select component(s)",
    options=all_components,
    default=[]
)

# Stop here if nothing selected
if not selected_components:
    st.stop()

# --------------------------------------------------
# FINAL FILTER (NO MAGIC)
# --------------------------------------------------
final_df = component_df[
    component_df["Components"].isin(selected_components)
].copy()

# Reset numbering
final_df.reset_index(drop=True, inplace=True)
final_df.insert(0, "No", range(1, len(final_df) + 1))

# --------------------------------------------------
# OUTPUT
# --------------------------------------------------
st.divider()
st.subheader("Filtered Maintenance Data")

st.dataframe(
    final_df,
    use_container_width=True,
    height=550
)
