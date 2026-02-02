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
# SAFE BACKGROUND (SUBTLE, BLURRED, DARK)
# --------------------------------------------------
def safe_background(image_path):
    try:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

        st.markdown(
            f"""
            <style>
            .stApp {{
                background:
                    linear-gradient(
                        rgba(0,0,0,0.55),
                        rgba(0,0,0,0.55)
                    ),
                    url("data:image/jpg;base64,{encoded}");
                background-size: cover;
                background-position: center;
            }}

            /* Content card */
            .block-container {{
                background-color: rgba(255,255,255,0.96);
                padding: 2rem 2.5rem;
                border-radius: 12px;
            }}

            h1, h2, h3, label {{
                color: #1a1a1a !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except:
        pass


safe_background("assets/kone_bg.jpg")

# --------------------------------------------------
# HEADER WITH LOGO (PROFESSIONAL)
# --------------------------------------------------
col1, col2 = st.columns([1, 6])

with col1:
    st.image("assets/kone_logo.png", width=110)

with col2:
    st.markdown("## Maintenance Decision Console")
    st.caption("Module → Sub Module → Components → Summary")

st.divider()

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "Upload Excel file",
    type=["xlsx"]
)

if not uploaded_file:
    st.info("Upload the Excel file to begin.")
    st.stop()

# --------------------------------------------------
# LOAD & NORMALIZE EXCEL
# --------------------------------------------------
df = pd.read_excel(uploaded_file)

df.columns = (
    df.columns.astype(str)
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)

COLUMN_ALIASES = {
    "Activity": "Activity (h:mm:ss)",
    "Activity time": "Activity (h:mm:ss)",
    "Total time": "Total time (h:mm:ss)",
    "Total Time": "Total time (h:mm:ss)",
}

df.rename(columns=COLUMN_ALIASES, inplace=True)

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
# FILTERS (CLEAN & STABLE)
# --------------------------------------------------
st.subheader("Module")
modules = st.multiselect(
    "Select module(s)",
    sorted(df["Module"].dropna().unique())
)

if not modules:
    st.stop()

df_m = df[df["Module"].isin(modules)]

st.subheader("Sub Module")
sub_modules = st.multiselect(
    "Select sub module(s)",
    sorted(df_m["Sub Module"].dropna().unique())
)

if not sub_modules:
    st.stop()

df_s = df_m[df_m["Sub Module"].isin(sub_modules)]

st.subheader("Components")
components = st.multiselect(
    "Select component(s)",
    sorted(df_s["Components"].dropna().unique())
)

if not components:
    st.stop()

# --------------------------------------------------
# FILTERED DATA
# --------------------------------------------------
filtered_df = df_s[df_s["Components"].isin(components)].copy()
filtered_df.insert(0, "No", range(1, len(filtered_df) + 1))

st.subheader("Filtered Maintenance Data")
st.dataframe(filtered_df, use_container_width=True)

# --------------------------------------------------
# OPTIONAL PROCEDURE JSON
# --------------------------------------------------
if "Procedure_JSON" in filtered_df.columns:
    st.subheader("Detailed Procedure / Split Time")

    for comp in components:
        rows = filtered_df[filtered_df["Components"] == comp]

        for _, row in rows.iterrows():
            raw = row.get("Procedure_JSON")
            if pd.isna(raw):
                continue

            try:
                steps = json.loads(raw)
                st.markdown(f"### {comp}")
                st.dataframe(pd.DataFrame(steps), use_container_width=True)
            except:
                st.warning(f"Invalid procedure data for {comp}")
