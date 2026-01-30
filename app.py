import streamlit as st

# -------- Core imports (correct package paths) --------
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


# -------- Page config --------
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

# -------- Sidebar --------
uploaded_file = sidebar_upload()

# -------- Main logic --------
if not uploaded_file:
    st.info("⬅️ Upload an Excel file from the sidebar to begin analysis.")
    st.stop()

# -------- Load data --------
try:
    df = load_excel(uploaded_file)
except Exception as e:
    st.error("Failed to load Excel file.")
    st.exception(e)
    st.stop()

# -------- Column preview (trust builder) --------
with st.expander("📄 View detected Excel columns"):
    st.write(list(df.columns))

# -------- Component selection --------
main_components = get_main_components(df)

if not main_components:
    st.warning("No components found in the uploaded file.")
    st.stop()

selected_component = component_selector(main_components)

# -------- Subcomponent selection --------
if selected_component:
    st.divider()

    st.subheader(f"Subcomponents for: **{selected_component}**")

    sub_components = get_subcomponents(df, selected_component)

    if not sub_components:
        st.warning("No subcomponents available for this component.")
        st.stop()

    selected_subs = st.multiselect(
        label="Select one or more subcomponents",
        options=sub_components,
        default=[sub_components[0]]
    )

    if not selected_subs:
        st.info("Select at least one subcomponent to view data.")
        st.stop()

    # -------- Filtered data --------
    result_df = filter_data(df, selected_component, selected_subs)

    st.divider()

    # -------- Result table --------
    show_table(result_df, title="Selected Maintenance Tasks")

    # -------- Summary metrics (visual polish) --------
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
