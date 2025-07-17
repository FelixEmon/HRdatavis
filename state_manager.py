# state_manager.py

import streamlit as st


def initialize_session_state():
    """Initializes all necessary keys in session_state if they don't exist."""
    state_keys = {
        'processed_df': None,
        'supply_demand_data': None,
        'last_uploaded_filename': None,
        'file_uploader_key': 0,
        'ui_bgs': [], 'applied_bgs': [],
        'ui_job_types': [], 'applied_job_types': [],
        'ui_job_titles': [], 'applied_job_titles': [],
        'ui_grades': [], 'applied_grades': [],
        'ui_start_date': None, 'applied_start_date': None,
        'ui_end_date': None, 'applied_end_date': None,
        # --- MODIFIED: Add states for drill-down ---
        'media_drilldown_selection': '总览',
        'talent_pool_drilldown_selection': '总览',
    }
    for key, default_value in state_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def reset_all_states(clear_df=True):
    """Resets all session states to their initial values. Designed to be a callback."""
    if clear_df:
        st.session_state.processed_df = None
        st.session_state.last_uploaded_filename = None
        st.session_state.file_uploader_key += 1

    st.session_state.supply_demand_data = None
    filter_keys = ['bgs', 'job_types', 'job_titles', 'grades']
    for key in filter_keys:
        st.session_state[f'ui_{key}'] = []
        st.session_state[f'applied_{key}'] = []
    st.session_state.ui_start_date = None
    st.session_state.ui_end_date = None
    st.session_state.applied_start_date = None
    st.session_state.applied_end_date = None
    # --- MODIFIED: Reset drill-down states ---
    st.session_state.media_drilldown_selection = '总览'
    st.session_state.talent_pool_drilldown_selection = '总览'