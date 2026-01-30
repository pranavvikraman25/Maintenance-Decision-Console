import streamlit as st
import pandas as pd

# =========================================================
# 🔐 LOGIN GATE
# =========================================================
def login_gate():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return

    st.set_page_config(page_title="Login required", layout="centered")

    # --- KONE LOGO (local or URL) ---
    # Option 1: local file -> put logo in /assets/kone_logo.png
    # Option 2: URL -> replace src
    st.markdown(
        """
        <div style="text-align:center;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6a/KONE_Logo.svg"
                 width="180"/>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h3 style='text-align:center;'>Login required</h3>", unsafe_allow_html=True)

    username = st.text_input("Username / Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "kone" and password == "kone":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()


login_gate()

# =========================================================
# IMPORTS (AFTER LOGIN)
# =========================================================
from core.loader import load_excel
from core.split_data import SPLIT_DATA

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Maintenance Decision Console",
    page_icon="🛠️",
    layout="wide"
)

st.markdown(
    """
    <h1>Maintenance Decision Console</h1>
    <p style="color:gray;">
    Module → Sub-module → Components → Summary & Procedure
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# =========================================================
# SIDEBAR – FILE UPLOAD
# =========================================================
uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=["xlsx"])

if not uploaded_file:
    st.info("⬅️ Upload an Excel file to begin.")
    st.stop()

# =========================================================
# LOAD EXCEL
# =========================================================
df = load_excel(uploaded_file)

# =========================================================
# COLUMN INDEX DEFINITIONS (ONLY CHANGE HERE IF NEEDED)
# =========================================================
COL_MODULE = 1
COL_SUBMODULE = 2
COL_COMPONENT = 3

# =========================================================
# SESSION STATE INIT
# =========================================================
for key in ["module", "submodule", "components"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "components" else []

# =========================================================
# MODULE SELECTION
# =========================================================
st.subheader("Module")

modules = sorted(df.iloc[:, COL_MODULE].dropna().unique())

selected_module = st.selectbox(
    "Select module",
    options=["-- Select --"] + modules
)

if selected_module == "-- Select --":
    st.stop()

if selected_module != st.session_state.module:
    st.session_state.module = selected_module
    st.session_state.submodule = None
    st.session_state.components = []

# =========================================================
# SUB-MODULE SELECTION
# =========================================================
st.subheader("Sub-module")

submodules = sorted(
    df[df.iloc[:, COL_MODULE] == selected_module]
    .iloc[:, COL_SUBMODULE]
    .dropna()
    .unique()
)

selected_submodule = st.selectbox(
    "Select sub-module",
    options=["-- Select --"] + submodules
)

if selected_submodule == "-- Select --":
    st.stop()

if selected_submodule != st.session_state.submodule:
    st.session_state.submodule = selected_submodule
    st.session_state.components = []

# =========================================================
# COMPONENT SELECTION
# =========================================================
st.subheader("Components")

components = sorted(
    df[
        (df.iloc[:, COL_MODULE] == selected_module) &
        (df.iloc[:, COL_SUBMODULE] == selected_submodule)
    ]
    .iloc[:, COL_COMPONENT]
    .dropna()
    .unique()
)

selected_components = st.multiselect(
    "Select components",
    options=components,
    key="components"
)

if not selected_components:
    st.stop()

# =========================================================
# FILTERED TABLE (REMOVE S.no, RESET NUMBERING)
# =========================================================
filtered_df = df[
    (df.iloc[:, COL_MODULE] == selected_module) &
    (df.iloc[:, COL_SUBMODULE] == selected_submodule) &
    (df.iloc[:, COL_COMPONENT].isin(selected_components))
].copy()

# Drop original S.no
filtered_df = filtered_df.drop(columns=filtered_df.columns[0])

# Reset numbering from 1
filtered_df.insert(0, "No", range(1, len(filtered_df) + 1))

st.divider()
st.subheader("Selected Maintenance Tasks (Summary)")

st.dataframe(filtered_df, use_container_width=True)

# =========================================================
# PROCEDURE / SPLIT TABLES (OPTIONAL, PER COMPONENT)
# =========================================================
st.divider()
st.subheader("Detailed Time Split")

found = False
for comp in selected_components:
    if comp in SPLIT_DATA:
        found = True
        st.markdown(f"### 🔧 {comp}")
        st.dataframe(
            SPLIT_DATA[comp],
            use_container_width=True,
            hide_index=True
        )

if not found:
    st.info("No procedure data available for selected components.")
