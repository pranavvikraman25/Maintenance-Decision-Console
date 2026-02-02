import streamlit as st
import pandas as pd


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


uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=["xlsx"])
if not uploaded_file:
    st.stop()

df = pd.read_excel(uploaded_file)


def find_col(keyword):
    for col in df.columns:
        if keyword in col.lower().replace(" ", ""):
            return col
    return None

COL_MODULE = find_col("module")
COL_SUBMODULE = find_col("sub")
COL_COMPONENT = find_col("component")
COL_PREP = find_col("preparation")
COL_ACTIVITY = find_col("activity")
COL_TOTAL = find_col("total")
COL_MAN = find_col("man")
COL_PRACTICAL = find_col("practical")

required = {
    "Module": COL_MODULE,
    "Sub Module": COL_SUBMODULE,
    "Components": COL_COMPONENT,
    "Preparation": COL_PREP,
    "Activity": COL_ACTIVITY,
    "Total time": COL_TOTAL,
    "Man power": COL_MAN,
    "Practical/Theoretical": COL_PRACTICAL,
}

missing = [k for k, v in required.items() if v is None]
if missing:
    st.error(f"Could not detect columns for: {missing}")
    st.stop()


if "module" not in st.session_state:
    st.session_state.module = None
if "submodule" not in st.session_state:
    st.session_state.submodule = None


st.subheader("Module")

modules = sorted(df[COL_MODULE].dropna().unique())
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


st.subheader("Sub Module")

submodules = sorted(
    df[df[COL_MODULE] == st.session_state.module][COL_SUBMODULE]
    .dropna().unique()
)

selected_sub = st.selectbox(
    "Select sub module",
    options=["-- Select --"] + submodules
)

if selected_sub == "-- Select --":
    st.stop()

st.session_state.submodule = selected_sub


st.subheader("Components")

components = sorted(
    df[
        (df[COL_MODULE] == st.session_state.module) &
        (df[COL_SUBMODULE] == st.session_state.submodule)
    ][COL_COMPONENT]
    .dropna().unique()
)

selected_components = st.multiselect(
    "Select components",
    options=components
)

if not selected_components:
    st.stop()


filtered_df = df[
    (df[COL_MODULE] == st.session_state.module) &
    (df[COL_SUBMODULE] == st.session_state.submodule) &
    (df[COL_COMPONENT].isin(selected_components))
].copy()

filtered_df.reset_index(drop=True, inplace=True)
filtered_df.insert(0, "No", range(1, len(filtered_df) + 1))

st.divider()
st.subheader("Selected Maintenance Tasks (Summary)")
st.dataframe(filtered_df, use_container_width=True)
