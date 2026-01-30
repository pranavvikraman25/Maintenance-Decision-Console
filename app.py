import streamlit as st

# -------- Core imports --------
from core.loader import load_excel
from core.filters import (
    get_main_components,
    get_subcomponents,
    filter_data
)

# -------- UI imports --------
from ui.sidebar import sidebar_upload
from ui.components import component_selector
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
            Component → Subcomponent → Time & Manpower Analysis
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
try:
    df = load_excel(uploaded_file)
except Exception as e:
    st.error("Failed to load Excel file.")
    st.exception(e)
    st.stop()

# -------- Column preview --------
with st.expander("📄 View detected Excel columns"):
    st.write(list(df.columns))

# -------- Get main components --------
main_components = get_main_components(df)

if not main_components:
    st.warning("No main components found in the uploaded file.")
    st.stop()

# -------- Session state init --------
if "last_component" not in st.session_state:
    st.session_state.last_component = None

# -------- Main component selector --------
selected_component = component_selector(main_components)

# -------- Reset subcomponents when component changes --------
if selected_component and selected_component != st.session_state.last_component:
    for key in list(st.session_state.keys()):
        if key.startswith("subs_"):
            del st.session_state[key]
    st.session_state.last_component = selected_component

# -------- Subcomponent selection --------
if selected_component:
    st.divider()
    st.subheader(f"Subcomponents for: **{selected_component}**")

    sub_components = get_subcomponents(df, selected_component)

    if not sub_components:
        st.warning("No subcomponents available for this component.")
        st.stop()

    state_key = f"subs_{selected_component}"

    if state_key not in st.session_state:
        st.session_state[state_key] = []

    selected_subs = st.multiselect(
        label="Select one or more subcomponents",
        options=sub_components,
        key=state_key
    )

    if not selected_subs:
        st.info("Select one or more subcomponents to view data.")
        st.stop()

    # -------- Filtered data --------
    result_df = filter_data(df, selected_component, selected_subs)

    st.divider()

    # -------- Result table --------
    show_table(result_df, title="Selected Maintenance Tasks")

    # -------- Summary metrics --------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Tasks", len(result_df))

    with col2:
        st.metric(
            "Total Manpower",
            int(result_df.iloc[:, 6].sum())
        )

    with col3:
        st.metric(
            "Avg Manpower / Task",
            round(result_df.iloc[:, 6].mean(), 2)
        )
else:
    st.info("Select a main component to continue.")
