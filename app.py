import streamlit as st
import pandas as pd
import base64
import json

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Maintenance Decision Console",
    layout="wide"
)

# --------------------------------------------------
# BACKGROUND IMAGE
# --------------------------------------------------
def set_background(image_path, opacity=0.12):
    try:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

        st.markdown(
            f"""
            <style>
            .stApp {{
                background:
                    linear-gradient(
                        rgba(255,255,255,{opacity}),
                        rgba(255,255,255,{opacity})
                    ),
                    url("data:image/jpg;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except:
        pass


set_background("assets/kone_bg.jpg")

# --------------------------------------------------
# LOGO
# --------------------------------------------------
try:
    logo_base64 = base64.b64encode(
        open("assets/kone_logo.png", "rb").read()
    ).decode()

    st.markdown(
        f"""
        <div style="position:fixed; top:20px; left:20px; z-index:100;">
            <img src="data:image/png;base64,{logo_base64}" width="120">
        </div>
        """,
        unsafe_allow_html=True
    )
except:
    pass

# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.title("Maintenance Decision Console")
st.caption("Module → Sub Module → Components → Summary")

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload Excel file",
    type=["xlsx"]
)

if not uploaded_file:
    st.info("Please upload the Excel file to continue.")
    st.stop()

# --------------------------------------------------
# LOAD EXCEL
# --------------------------------------------------
df = pd.read_excel(uploaded_file)

# --------------------------------------------------
# NORMALIZE COLUMN NAMES (IMPORTANT FIX)
# --------------------------------------------------
df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)

COLUMN_ALIASES = {
    "Activity": "Activity (h:mm:ss)",
    "Activity time": "Activity (h:mm:ss)",
    "Activity Time": "Activity (h:mm:ss)",
    "Activity time (h:mm:ss)": "Activity (h:mm:ss)",

    "Total time": "Total time (h:mm:ss)",
    "Total Time": "Total time (h:mm:ss)",
    "Total Time (h:mm:ss)": "Total time (h:mm:ss)",
}

df.rename(columns=COLUMN_ALIASES, inplace=True)

# --------------------------------------------------
# REQUIRED COLUMNS CHECK
# --------------------------------------------------
REQUIRED_COLUMNS = [
    "Module",
    "Sub Module",
    "Components",
    "Preparation/Finalization (h:mm:ss)",
    "Activity (h:mm:ss)",
    "Total time (h:mm:ss)",
    "No of man power",
    "Practical(Site)/ Theoretical"
]

missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

# --------------------------------------------------
# FILTERS (ALL MULTISELECT, DEFAULT EMPTY)
# --------------------------------------------------
st.subheader("Module")
selected_modules = st.multiselect(
    "Select module(s)",
    options=sorted(df["Module"].dropna().unique()),
    default=[]
)

if not selected_modules:
    st.stop()

df_mod = df[df["Module"].isin(selected_modules)]

st.subheader("Sub Module")
selected_submodules = st.multiselect(
    "Select sub module(s)",
    options=sorted(df_mod["Sub Module"].dropna().unique()),
    default=[]
)

if not selected_submodules:
    st.stop()

df_sub = df_mod[df_mod["Sub Module"].isin(selected_submodules)]

st.subheader("Components")
selected_components = st.multiselect(
    "Select component(s)",
    options=sorted(df_sub["Components"].dropna().unique()),
    default=[]
)

if not selected_components:
    st.stop()

# --------------------------------------------------
# FINAL FILTERED DATA
# --------------------------------------------------
filtered_df = df_sub[df_sub["Components"].isin(selected_components)].copy()

filtered_df.insert(0, "No", range(1, len(filtered_df) + 1))

# --------------------------------------------------
# SUMMARY TABLE
# --------------------------------------------------
st.subheader("Filtered Maintenance Data")
st.dataframe(filtered_df, use_container_width=True)

# --------------------------------------------------
# PROCEDURE / SPLIT DATA (JSON – OPTIONAL)
# --------------------------------------------------
if "Procedure_JSON" in filtered_df.columns:
    st.subheader("Detailed Procedure / Split Time")

    for comp in selected_components:
        rows = filtered_df[filtered_df["Components"] == comp]

        for _, row in rows.iterrows():
            raw = row.get("Procedure_JSON")

            if pd.isna(raw):
                continue

            try:
                steps = json.loads(raw)
                steps_df = pd.DataFrame(steps)

                st.markdown(f"### 🔧 {comp}")
                st.dataframe(steps_df, use_container_width=True)

            except:
                st.warning(f"Invalid procedure data for {comp}")

# --------------------------------------------------
# DEBUG VIEW (OPTIONAL)
# --------------------------------------------------
with st.expander("View detected Excel columns"):
    st.write(list(df.columns))
