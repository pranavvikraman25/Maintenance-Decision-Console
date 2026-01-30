import streamlit as st

# -------- Core imports --------
from core.loader import load_excel
from core.filters import (
    get_main_components,
    get_subcomponents,
    filter_data
)

# -------- Fixed split data --------
from core.split_data import SPLIT_DATA

# -------- UI imports --------
from ui.sidebar import sidebar_upload
from ui.tables import show_table


# -------- Page configuration --------
st.set_page_config(
    page_title="Maintenance Decision Console",
    page_icon="🛠️",
    layout="wide"
)

# -------- Header --------
st.markdown(
    """
    <div style="padding:10px 0;">
        <h1 style="margin-bottom:0;">Maintenance Decision Console</h1>
        <p style="color:gray; margin-top:4px;">
            Component → Subcomponent → Summary & Procedure View
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# -------- Sidebar upload --------
uploaded_file = sidebar_upload()

if not uploaded_file:
    st.info("⬅️ Upload an Excel file from the sidebar to begin analysis.")
    st.stop()

# -------- Load Excel --------
main_df = load_excel(uploaded_file)

# -------- Column preview --------
with st.expander("📄 View detected Excel columns"):
    st.write(list(main_df.columns))

# -------- Get main components --------
main_components = get_main_components(main_df)

if not main_components:
    st.warning("No main components found.")
    st.stop()

# -------- Session state init --------
if "selected_component" not in st.session_state:
    st.session_state.selected_component = None

if "selected_subs" not in st.session_state:
    st.session_state.selected_subs = []

# -------- Main Components UI --------
st.subheader("Main Components")
cols = st.columns(len(main_components))

for i, comp in enumerate(main_components):
    if cols[i].button(comp):
        # store selection permanently
        st.session_state.selected_component = comp
        # reset subcomponents when main changes
        st.session_state.selected_subs = []

selected_component = st.session_state.selected_component

if not selected_component:
    st.info("Select a main component to continue.")
    st.stop()

# -------- Subcomponents --------
st.divider()
st.subheader(f"Subcomponents for: **{selected_component}**")

sub_components = get_subcomponents(main_df, selected_component)

if not sub_components:
    st.warning("No subcomponents available.")
    st.stop()

selected_subs = st.multiselect(
    "Select one or more subcomponents",
    options=sub_components,
    key="selected_subs"
)

if not selected_subs:
    st.info("Select one or more subcomponents to view data.")
    st.stop()

# -------- Summary table --------
result_df = filter_data(main_df, selected_component, selected_subs)

st.divider()
show_table(result_df, title="Selected Maintenance Tasks (Summary)")

# -------- Detailed split table (ONLY when one subcomponent) --------
if len(selected_subs) == 1:
    sub = selected_subs[0]

    if sub in SPLIT_DATA:
        st.divider()
        st.subheader(f"Detailed Time Split for: **{sub}**")

        st.dataframe(
            SPLIT_DATA[sub],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No detailed procedure data available for this subcomponent.")
