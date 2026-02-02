import streamlit as st
import pandas as pd
import json
import base64

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Maintenance Decision Console",
    layout="wide"
)

# --------------------------------------------------
# BACKGROUND + LOGO (optional, safe)
# --------------------------------------------------
def set_background(image_path: str, opacity: float = 0.08):
    try:
        with open(image_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background:
                    linear-gradient(
                        rgba(255,255,255,{1-opacity}),
                        rgba(255,255,255,{1-opacity})
                    ),
                    url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    except FileNotFoundError:
        pass


set_background("assets/background.png")

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
    st.info("Upload the Excel file to begin.")
    st.stop()

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
df = pd.read_excel(uploaded_file)

# Normalize column names (DO NOT RENAME USER DATA)
df.columns = [c.strip() for c in df.columns]

# REQUIRED COLUMNS (STRICT)
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
# FILTER UI
# --------------------------------------------------
st.subheader("Module")
selected_modules = st.multiselect(
    "Select module(s)",
    options=sorted(df["Module"].dropna().unique()),
    default=[]
)

if not selected_modules:
    st.info("Select at least one Module.")
    st.stop()

sub_df = df[df["Module"].isin(selected_modules)]

st.subheader("Sub Module")
selected_submodules = st.multiselect(
    "Select sub module(s)",
    options=sorted(sub_df["Sub Module"].dropna().unique()),
    default=[]
)

if not selected_submodules:
    st.info("Select at least one Sub Module.")
    st.stop()

comp_df = sub_df[sub_df["Sub Module"].isin(selected_submodules)]

st.subheader("Components")
selected_components = st.multiselect(
    "Select component(s)",
    options=sorted(comp_df["Components"].dropna().unique()),
    default=[]
)

if not selected_components:
    st.info("Select at least one Component.")
    st.stop()

# --------------------------------------------------
# FINAL FILTER
# --------------------------------------------------
filtered_df = comp_df[comp_df["Components"].isin(selected_components)].copy()

# Reset serial number
filtered_df.insert(0, "No", range(1, len(filtered_df) + 1))

# --------------------------------------------------
# SUMMARY TABLE
# --------------------------------------------------
st.subheader("Filtered Maintenance Data")
st.dataframe(
    filtered_df,
    use_container_width=True
)

# --------------------------------------------------
# PROCEDURE / SPLIT DATA (OPTION B – JSON)
# --------------------------------------------------
# Expected format:
# Procedure_JSON column (optional)
# Each cell contains JSON list of steps

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
                proc_df = pd.DataFrame(steps)

                st.markdown(f"### 🔧 {comp}")
                st.dataframe(proc_df, use_container_width=True)

            except Exception:
                st.warning(f"Invalid JSON for component: {comp}")

# --------------------------------------------------
# DEBUG (optional)
# --------------------------------------------------
with st.expander("View detected columns"):
    st.write(list(df.columns))
