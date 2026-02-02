import streamlit as st
import pandas as pd
import re

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
Module → Sub Module → Components → Summary
</p>
""", unsafe_allow_html=True)

st.divider()

# =========================================================
# LOAD EXCEL
# =========================================================
uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=["xlsx"])
if not uploaded_file:
    st.stop()

df = pd.read_excel(uploaded_file)

# =========================================================
# 🔧 NORMALIZE TEXT (THIS IS THE FIX)
# =========================================================
def normalize(val):
    if pd.isna(val):
        return val
    val = str(val)
    val = re.sub(r"\s+", " ", val)  # collapse multiple spaces
    return val.strip()

for col in ["Module", "Sub Module", "Components"]:
    df[col] = df[col].apply(normalize)

# =========================================================
# SESSION STATE
# =========================================================
if "module" not in st.session_state:
    st.session_state.module = None
if "submodule" not in st.session_state:
    st.session_state.submodule = None

# =========================================================
# MODULE (BOX CLICK)
# =========================================================
st.subheader("Module")

modules = sorted(df["Module"].dropna().unique())
cols = st.columns(min(5, len(modules)))

clicked = None
for i, m in enumerate(modules):
    if cols[i % len(cols)].button(m):
        clicked = m

if clicked:
    st.session_state.module = clicked
    st.session_state.submodule = None

if not st.session_state.module:
    st.stop()

# =========================================================
# SUB MODULE
# =========================================================
st.subheader("Sub Module")

submodules = sorted(
    df[df["Module"] == st.session_state.module]["Sub Module"]
    .dropna().unique()
)

selected_sub = st.selectbox(
    "Select sub module",
    options=["-- Select --"] + list(submodules)
)

if selected_sub == "-- Select --":
    st.stop()

st.session_state.submodule = selected_sub

# =========================================================
# COMPONENTS (THIS WILL NOW SHOW ALL)
# =========================================================
st.subheader("Components")

components = sorted(
    df[
        (df["Module"] == st.session_state.module) &
        (df["Sub Module"] == st.session_state.submodule)
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
# FILTERED TABLE
# =========================================================
filtered_df = df[
    (df["Module"] == st.session_state.module) &
    (df["Sub Module"] == st.session_state.submodule) &
    (df["Components"].isin(selected_components))
].copy()

filtered_df.reset_index(drop=True, inplace=True)
filtered_df.insert(0, "No", range(1, len(filtered_df) + 1))

st.divider()
st.subheader("Selected Maintenance Tasks (Summary)")
st.dataframe(filtered_df, use_container_width=True)
