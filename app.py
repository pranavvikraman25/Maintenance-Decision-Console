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

    st.markdown(
        """
        <div style="text-align:center;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6a/KONE_Logo.svg"
                 width="180"/>
            <h3>Login required</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

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
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Maintenance Decision Console",
    page_icon="🛠️",
    layout="wide"
)

st.markdown("""
<h1>Maintenance Decision Console</h1>
<p style="color:gray;">
Module → Sub Module → Components → Summary & Procedure
</p>
""", unsafe_allow_html=True)

st.divider()

# =========================================================
# LOAD DATA
# =========================================================
uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=["xlsx"])

if not uploaded_file:
    st.info("⬅️ Upload an Excel file to begin.")
    st.stop()

df = pd.read_excel(uploaded_file)

# =========================================================
# REQUIRED COLUMN NAMES (STRICT CHECK)
# =========================================================
REQUIRED_COLUMNS = [
    "Module",
    "Sub Module",
    "Components",
    "Preparation/Finalization (h:mm:ss)",
    "Activity (h:mm:ss)",
    "Total time (h:mm:ss)",
    "No of man power",
    "Practical(Site)/Theoretical"
]

missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]

if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

# =========================================================
# SESSION STATE
# =========================================================
if "selected_module" not in st.session_state:
    st.session_state.selected_module = None

if "selected_submodule" not in st.session_state:
    st.session_state.selected_submodule = None

# =========================================================
# MODULE SELECTION (BOX STYLE)
# =========================================================
st.subheader("Module")

modules = sorted(df["Module"].dropna().unique())
cols = st.columns(min(5, len(modules)))

clicked = None
for i, module in enumerate(modules):
    if cols[i % len(cols)].button(module):
        clicked = module

if clicked:
    st.session_state.selected_module = clicked
    st.session_state.selected_submodule = None

if not st.session_state.selected_module:
    st.info("Select a module to continue.")
    st.stop()

# =========================================================
# SUB MODULE
# =========================================================
st.subheader("Sub Module")

submodules = sorted(
    df[df["Module"] == st.session_state.selected_module]["Sub Module"]
    .dropna()
    .unique()
)

selected_submodule = st.selectbox(
    "Select sub module",
    options=["-- Select --"] + submodules
)

if selected_submodule == "-- Select --":
    st.stop()

st.session_state.selected_submodule = selected_submodule

# =========================================================
# COMPONENTS
# =========================================================
st.subheader("Components")

components = sorted(
    df[
        (df["Module"] == st.session_state.selected_module) &
        (df["Sub Module"] == st.session_state.selected_submodule)
    ]["Components"]
    .dropna()
    .unique()
)

selected_components = st.multiselect(
    "Select components",
    options=components
)

if not selected_components:
    st.stop()

# =========================================================
# FILTER DATA (REMOVE S.NO, RESET INDEX)
# =========================================================
filtered_df = df[
    (df["Module"] == st.session_state.selected_module) &
    (df["Sub Module"] == st.session_state.selected_submodule) &
    (df["Components"].isin(selected_components))
].copy()

filtered_df.reset_index(drop=True, inplace=True)
filtered_df.insert(0, "No", range(1, len(filtered_df) + 1))

st.divider()
st.subheader("Selected Maintenance Tasks (Summary)")

st.dataframe(filtered_df, use_container_width=True)
