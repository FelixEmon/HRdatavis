# app.py

import streamlit as st
from styles import get_custom_css
from state_manager import initialize_session_state, reset_all_states
# MODIFIED: Correctly importing from ui_components
from ui_components import render_filter_panel, render_channel_analysis, render_supply_demand_analysis
from data_processing import load_data, preprocess_data, filter_dataframe, generate_supply_demand_data

st.set_page_config(layout="wide", page_title="岗位&渠道数据展示面板")
st.markdown(get_custom_css(), unsafe_allow_html=True)
DEFAULT_EXCEL_FILENAME = "monawu.xlsx"


def render_main_content():
    """Renders the main analysis content if data is available."""
    # MODIFIED: Moved the expander logic into render_filter_panel
    render_filter_panel()
    st.markdown("---")

    applied_selections = {
        'bgs': st.session_state.applied_bgs,
        'job_types': st.session_state.applied_job_types,
        'job_titles': st.session_state.applied_job_titles,
        'grades': st.session_state.applied_grades,
        'start_date': st.session_state.applied_start_date,
        'end_date': st.session_state.applied_end_date
    }
    filtered_data = filter_dataframe(st.session_state.processed_df, applied_selections)

    if filtered_data.empty:
        st.info("根据已应用的筛选条件，没有找到匹配的数据。请调整筛选条件后点击“应用筛选”。")
    else:
        render_channel_analysis(filtered_data)
        render_supply_demand_analysis()


def render_file_uploader():
    """Renders the file uploader and reset button at the bottom of the page."""
    st.markdown("<hr style='margin-top: 50px'>", unsafe_allow_html=True)
    st.subheader("上传与管理数据文件")

    uploader_col, button_col = st.columns([0.8, 0.2])
    with uploader_col:
        uploaded_file = st.file_uploader(
            f"请上传 '{DEFAULT_EXCEL_FILENAME}' 文件 (包含主数据和'bole'工作表)",
            type=["xlsx"],
            key=f"fileuploader_{st.session_state.file_uploader_key}",
            label_visibility="collapsed"
        )

    if uploaded_file and uploaded_file.name != st.session_state.last_uploaded_filename:
        with st.spinner("正在加载和处理数据..."):
            reset_all_states(clear_df=False)
            main_df, bole_df = load_data(uploaded_file)
            st.session_state.processed_df = preprocess_data(main_df, bole_df)
            st.session_state.last_uploaded_filename = uploaded_file.name
            if st.session_state.processed_df is not None:
                all_job_categories = st.session_state.processed_df['职位类'].dropna().unique()
                st.session_state.supply_demand_data = generate_supply_demand_data(all_job_categories)
            st.rerun()

    with button_col:
        if st.session_state.processed_df is not None:
            st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
            st.button("🗑️ 删除数据并重置", on_click=reset_all_states, args=(True,))


def main():
    initialize_session_state()
    st.markdown("<div class='main-title-container'><h2>岗位 & 渠道数据展示面板</h2></div>", unsafe_allow_html=True)

    if st.session_state.processed_df is None:
        st.warning("请在页面底部上传数据文件以开始分析。")
    else:
        render_main_content()

    render_file_uploader()


if __name__ == "__main__":
    main()