import streamlit as st
import pandas as pd
import re

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Maintenance Decision Console",
    layout="wide",
    page_icon="🛠️"
)

st.title("Maintenance Decision Console")
st.caption("Module → Sub Module → Components → Summary")

# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------
uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=["xlsx"])
if not uploaded_file:
    st.info("Upload an Excel file to start.")
    st.stop()

df = pd.read_excel(uploaded_file)

# -------------------------------------------------
# NORMALIZE TEXT (CRITICAL)
# -------------------------------------------------
def normalize(x):
    if pd.isna(x):
        return None
    x = str(x)
    x = re.sub(r"\s+", " ", x)
    return x.strip()

for col in ["Module", "Sub Module", "Components"]:
    df[col] = df[col].apply(normalize)

# -------------------------------------------------
# MODULE FILTER (MULTI)
# -------------------------------------------------
st.subheader("Module")

all_modules = sorted(df["Module"].dropna().unique())

selected_modules = st.multiselect(
    "Select module(s)",
    options=all_modules
)

if not selected_modules:
    st.stop()

df_m = df[df["Module"].isin(selected_modules)]

# -------------------------------------------------
# SUB MODULE FILTER (MULTI)
# -------------------------------------------------
st.subheader("Sub Module")

all_submodules = sorted(df_m["Sub Module"].dropna().unique())

selected_submodules = st.multiselect(
    "Select sub module(s)",
    options=all_submodules
)

if not selected_submodules:
    st.stop()

df_sm = df_m[df_m["Sub Module"].isin(selected_submodules)]

# -------------------------------------------------
# COMPONENT FILTER (MULTI)
# -------------------------------------------------
st.subheader("Components")

all_components = sorted(df_sm["Components"].dropna().unique())

selected_components = st.multiselect(
    "Select component(s)",
    options=all_components
)

if not selected_components:
    st.stop()

df_final = df_sm[df_sm["Components"].isin(selected_components)].copy()

# -------------------------------------------------
# CLEAN OUTPUT TABLE
# -------------------------------------------------
df_final.reset_index(drop=True, inplace=True)
df_final.insert(0, "No", range(1, len(df_final) + 1))

st.divider()
st.subheader("Filtered Maintenance Data")

st.dataframe(df_final, use_container_width=True)
