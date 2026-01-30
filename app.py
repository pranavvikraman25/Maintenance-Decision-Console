import streamlit as st

# =========================================================
# 🔐 LOGIN GATE (MUST BE AT VERY TOP)
# =========================================================
def login_gate():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return

    st.set_page_config(page_title="Secure Login", layout="centered")
    st.title("🔒 Secure Access")

    username = st.text_input("Username / Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "kone" and password == "kone":
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Invalid credentials. Access denied.")

    st.stop()


login_gate()

# =========================================================
# IMPORTS (AFTER LOGIN)
# =========================================================
from core.loader import load_excel
from core.filters import (
    get_main_components,
    get_subcomponents,
    filter_data
)
from core.split_data import SPLIT_DATA
from ui.sidebar import sidebar_upload
from ui.tables import show_table


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Maintenance Decision Console",
    page_icon="🛠️",
    layout="wide"
)

# =========================================================
# STYLE: CLEAN COMPONENT BOX GRID
# =========================================================
st.markdown("""
<style>
.component-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 16px;
    margin-top: 10px;
}

.component-box {
    border: 1px solid #d0d0d0;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    font-weight: 600;
    background-color: white;
    cursor: pointer;
}

.component-box:hover {
    background-color: #f3f6fb;
    border-color: #4f8bf9;
}

.component-box.selected {
    background-color: #e8f0fe;
    border: 2px solid #4f8bf9;
    color: #1a3e8a;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<h1 style="margin-bottom:0;">Maintenance Decision Console</h1>
<p style="color:gray; margin-top:4px;">
Component → Subcomponent → Summary & Procedure View
</p>
""", unsafe_allow_html=True)

st.divider()

# =========================================================
# SIDEBAR: FILE UPLOAD
# =========================================================
uploaded_file = sidebar_upload()

if not uploaded_file:
    st.info("⬅️ Upload an Excel file from the sidebar to begin.")
    st.stop()

# =========================================================
# LOAD EXCEL
# =========================================================
main_df = load_excel(uploaded_file)

with st.expander("📄 View detected Excel columns"):
    st.write(list(main_df.columns))

# =========================================================
# SESSION STATE INIT
# =========================================================
if "selected_component" not in st.session_state:
    st.session_state.selected_component = None

if "selected_subs" not in st.session_state:
    st.session_state.selected_subs = []

# =========================================================
# MAIN COMPONENTS (CLEAN GRID)
# =========================================================
st.subheader("Main Components")

main_components = get_main_components(main_df)

clicked_component = None

st.markdown('<div class="component-grid">', unsafe_allow_html=True)

for comp in main_components:
    is_selected = comp == st.session_state.selected_component
    box_class = "component-box selected" if is_selected else "component-box"

    if st.button(comp, key=f"comp_{comp}"):
        clicked_component = comp

    st.markdown(
        f'<div class="{box_class}">{comp}</div>',
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

if clicked_component:
    st.session_state.selected_component = clicked_component
    st.session_state.selected_subs = []

selected_component = st.session_state.selected_component

if not selected_component:
    st.info("Select a main component to continue.")
    st.stop()

# =========================================================
# SUBCOMPONENTS
# =========================================================
st.divider()
st.subheader(f"Subcomponents for: **{selected_component}**")

sub_components = get_subcomponents(main_df, selected_component)

selected_subs = st.multiselect(
    "Select one or more subcomponents",
    options=sub_components,
    key="selected_subs"
)

if not selected_subs:
    st.info("Select one or more subcomponents to view data.")
    st.stop()

# =========================================================
# SUMMARY TABLE
# =========================================================
result_df = filter_data(main_df, selected_component, selected_subs)

st.divider()
show_table(result_df, title="Selected Maintenance Tasks (Summary)")

# =========================================================
# DETAILED SPLIT TABLES (FOR EACH SUBCOMPONENT)
# =========================================================
st.divider()
st.subheader("Detailed Time Split (Procedure Data)")

found = False

for sub in selected_subs:
    if sub in SPLIT_DATA:
        found = True
        st.markdown(f"### 🔧 {sub}")
        st.dataframe(
            SPLIT_DATA[sub],
            use_container_width=True,
            hide_index=True
        )

if not found:
    st.info("No detailed procedure data available for the selected subcomponents.")
