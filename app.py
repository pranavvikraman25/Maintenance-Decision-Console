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
# 🔥 FIX MERGED CELLS (THIS IS THE KEY)
# --------------------------------------------------
df["Module"] = df["Module"].ffill()
df["Sub Module"] = df["Sub Module"].ffill()

# --------------------------------------------------
# NORMALIZE TEXT
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
# MODULE FILTER
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

df_module = df[df["Module"].isin(selected_modules)]

# --------------------------------------------------
# SUB MODULE FILTER (NOW WORKS)
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
# COMPONENT FILTER
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
# FINAL TABLE (SINGLE SERIAL NUMBER)
# --------------------------------------------------
df_final.reset_index(drop=True, inplace=True)
df_final.insert(0, "No", range(1, len(df_final) + 1))

st.divider()
st.subheader("Filtered Maintenance Data")

st.dataframe(
    df_final,
    use_container_width=True,
    hide_index=True
)


import json

st.divider()
st.subheader("Procedure / Split Details")

if "Procedure_JSON" in filtered_data.columns:

    for comp in selected_components:

        row = filtered_data[filtered_data["Components"] == comp]

        if row.empty:
            continue

        proc_json = row.iloc[0]["Procedure_JSON"]

        if pd.isna(proc_json) or str(proc_json).strip() == "":
            continue

        try:
            steps = json.loads(proc_json)

            if not isinstance(steps, list) or len(steps) == 0:
                continue

            proc_df = pd.DataFrame(steps)
            proc_df.insert(0, "Step No", range(1, len(proc_df) + 1))

            st.markdown(f"### 🔹 {comp}")
            st.dataframe(proc_df, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Invalid Procedure_JSON for component: {comp}")
