import streamlit as st
import pandas as pd
from styles import get_custom_css
from data_processing import (
    load_data, preprocess_data, get_filter_options,
    filter_dataframe, calculate_channel_metrics
)
from plotting import create_pie_chart

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="岗位&渠道数据展示面板")
st.markdown(get_custom_css(), unsafe_allow_html=True)

# --- Hardcoded BG options ---
BG_OPTIONS = [
    "CDG企业发展事业群", "IEG互动娱乐事业群", "CSIG云与智慧产业事业群",
    "TEG技术工程事业群", "WXG微信事业群", "PCG平台与内容事业群",
    "S3职能系统－HR与管理线", "S1职能系统－职能线", "S2职能系统－财经线"
]
DEFAULT_EXCEL_FILENAME = "monawu.xlsx"


# --- Main Application ---
def main():
    # --- Top Title & Data Type Selector ---
    st.markdown("<div class='main-title-container'><h2>岗位 & 渠道数据展示面板</h2></div>", unsafe_allow_html=True)
    _, col_data_type = st.columns([0.7, 0.3])
    with col_data_type:
        data_source_type = st.selectbox("数据类型", ("内部数据", "外部数据"), label_visibility="collapsed")
    if data_source_type == "外部数据":
        st.info("外部数据模块正在建设中，敬请期待。")
        st.stop()

    # --- Initialize session state ---
    if 'raw_df' not in st.session_state: st.session_state.raw_df = None
    if 'processed_df' not in st.session_state: st.session_state.processed_df = None
    if 'file_uploader_key' not in st.session_state: st.session_state.file_uploader_key = 0
    if 'last_uploaded_filename' not in st.session_state: st.session_state.last_uploaded_filename = ""

    # --- Filters Expander ---
    with st.expander("数据筛选条件", expanded=True):
        st.markdown(
            """<style>div[data-testid="stExpander"] div[role="button"] p { font-size: 1.2em; font-weight: bold; }</style>""",
            unsafe_allow_html=True)

        # Get all filter options from data
        filter_opts = get_filter_options(st.session_state.processed_df)
        job_types_options = filter_opts.get('job_types', [])
        job_titles_options = filter_opts.get('job_titles', [])
        years_options = ['任意'] + filter_opts.get('years', [])
        months_options = ['任意'] + filter_opts.get('months', [])
        days_options = ['任意'] + filter_opts.get('days', [])

        # --- Row 1: BG, Job, Grade Filters ---
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        with filter_col1:
            st.markdown("<span class='filter-section-title'>BG</span>", unsafe_allow_html=True)
            selected_bgs = st.multiselect("BG", BG_OPTIONS, [], label_visibility="collapsed")
        with filter_col2:
            st.markdown("<span class='filter-section-title'>职位类</span>", unsafe_allow_html=True)
            selected_job_types = st.multiselect("职位类", job_types_options, [], label_visibility="collapsed")
        with filter_col3:
            st.markdown("<span class='filter-section-title'>职位名称</span>", unsafe_allow_html=True)
            selected_job_titles = st.multiselect("职位名称", job_titles_options, [], label_visibility="collapsed")
        with filter_col4:
            st.markdown("<span class='filter-section-title'>职级区间</span>", unsafe_allow_html=True)
            selected_grade_range = st.slider("职级区间", 5, 16, (5, 16), label_visibility="collapsed")

        st.markdown("---", )  # Visual separator inside expander

        # --- Row 2: Date Range Filter ---
        date_filter_col1, date_filter_col2 = st.columns(2)
        with date_filter_col1:
            st.markdown("##### 开始日期")
            sc1, sc2, sc3 = st.columns(3)
            selected_start_year = sc1.selectbox("年", options=years_options, key="start_year")
            selected_start_month = sc2.selectbox("月", options=months_options, key="start_month")
            selected_start_day = sc3.selectbox("日", options=days_options, key="start_day")

        with date_filter_col2:
            st.markdown("##### 结束日期")
            ec1, ec2, ec3 = st.columns(3)
            selected_end_year = ec1.selectbox("年 ", options=years_options,
                                              key="end_year")  # space in label to make key unique
            selected_end_month = ec2.selectbox("月 ", options=months_options, key="end_month")
            selected_end_day = ec3.selectbox("日 ", options=days_options, key="end_day")

    st.markdown("---")

    # --- Data Display Area ---
    data_display_area = st.container()

    if st.session_state.processed_df is None:
        with data_display_area:
            st.warning("请在页面底部上传数据文件以开始分析。")
    else:
        # Apply all filters
        start_date_parts = (selected_start_year, selected_start_month, selected_start_day)
        end_date_parts = (selected_end_year, selected_end_month, selected_end_day)
        filtered_data = filter_dataframe(st.session_state.processed_df, selected_bgs, selected_job_types,
                                         selected_job_titles, selected_grade_range, start_date_parts, end_date_parts)

        with data_display_area:
            if filtered_data.empty:
                st.info("根据当前筛选条件，没有找到匹配的数据。")
            else:
                # --- Calculation Mode Selector ---
                _, center_col, _ = st.columns([1, 1.5, 1])
                with center_col:
                    st.markdown(
                        "<h3 class='channel-main-title' style='text-align:center; margin-bottom:5px;'>渠道入职贡献率</h3>",
                        unsafe_allow_html=True)
                    mode_selection = st.selectbox("选择计算方式", ("相对渠道入职贡献率", "绝对渠道入职贡献率"),
                                                  label_visibility="collapsed")

                calculation_mode = 'absolute' if mode_selection == "绝对渠道入职贡献率" else 'relative'
                channel_metrics = calculate_channel_metrics(filtered_data, mode=calculation_mode)

                if not channel_metrics:
                    st.warning("无法计算渠道贡献率，可能是因为筛选后总入职人数为0。")
                else:
                    # --- Display Results ---
                    channel_order = ['媒体', '伯乐', '猎头', '人才库盘活', 'ST', '猎聘']
                    cols = st.columns(6)
                    detail_box_styles = ["channel-detail-box-white", "channel-detail-box-gray"]
                    pie_charts_to_display = []

                    for i, channel_name in enumerate(channel_order):
                        metric = channel_metrics.get(channel_name)
                        with cols[i]:
                            if not metric:
                                st.markdown(f"<div class='channel-header-box'><h5>{channel_name}</h5><p>0.0%</p></div>",
                                            unsafe_allow_html=True)
                                st.markdown(
                                    f"<div class='channel-detail-box {detail_box_styles[i % 2]}'><ul><li>无数据</li></ul></div>",
                                    unsafe_allow_html=True)
                                continue

                            st.markdown(
                                f"<div class='channel-header-box'><h5>{channel_name}</h5><p>{metric['percentage']:.1f}%</p></div>",
                                unsafe_allow_html=True)
                            detail_html = "<ul>" + "".join(
                                f"<li>{item}</li>" for item in metric['details_text_list']) + "</ul>" if metric.get(
                                'details_text_list') else "<ul><li>无细分数据</li></ul>"
                            st.markdown(
                                f"<div class='channel-detail-box {detail_box_styles[i % 2]}'>{detail_html}</div>",
                                unsafe_allow_html=True)

                            if channel_name in ['媒体', '伯乐', '猎头', '人才库盘活'] and metric['pie_data'].get(
                                    'labels'):
                                pie_charts_to_display.append(
                                    {"title": f"{channel_name}渠道细分", "data": metric['pie_data']})

                    st_liepin_pie_data = channel_metrics.get('ST_Liepin_Combined_Pie', {}).get('pie_data', {})
                    if st_liepin_pie_data.get("labels"):
                        pie_charts_to_display.append({"title": "ST & 交付团队-猎聘占比", "data": st_liepin_pie_data})

                    if pie_charts_to_display:
                        st.markdown(
                            "<h3 class='channel-main-title' style='font-size: 22px; margin-top:15px;'>渠道细分饼图</h3>",
                            unsafe_allow_html=True)
                        pie_cols = st.columns(5)
                        chart_map = {"媒体渠道细分": 0, "伯乐渠道细分": 1, "猎头渠道细分": 2, "人才库盘活渠道细分": 3,
                                     "ST & 交付团队-猎聘占比": 4}

                        for chart_info in pie_charts_to_display:
                            target_col_idx = chart_map.get(chart_info['title'])
                            if target_col_idx is not None:
                                with pie_cols[target_col_idx]:
                                    st.markdown(f"<div class='pie-chart-title'>{chart_info['title']}</div>",
                                                unsafe_allow_html=True)
                                    fig = create_pie_chart(chart_info['data']['labels'], chart_info['data']['values'],
                                                           chart_info['title'])
                                    if fig:
                                        st.markdown("<div class='pie-chart-container'><div style='width:100%'>",
                                                    unsafe_allow_html=True)
                                        st.plotly_chart(fig, use_container_width=True)
                                        st.markdown("</div></div>", unsafe_allow_html=True)
                                    else:
                                        st.markdown("<div class='pie-chart-container'><p>无数据可供展示</p></div>",
                                                    unsafe_allow_html=True)

    # --- File Uploader and Reset Button ---
    st.markdown("---")
    st.subheader("上传与管理数据文件")
    uploader_col, button_col = st.columns([0.8, 0.2])
    with uploader_col:
        uploaded_file_new = st.file_uploader(f"请上传 '{DEFAULT_EXCEL_FILENAME}' 文件", type=["xlsx"],
                                             key=f"fileuploader_{st.session_state.file_uploader_key}",
                                             label_visibility="collapsed")
    with button_col:
        if st.session_state.raw_df is not None:
            st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)  # Alignment
            if st.button("🗑️ 删除数据并重置"):
                st.session_state.raw_df, st.session_state.processed_df, st.session_state.last_uploaded_filename = None, None, ""
                st.session_state.file_uploader_key += 1
                st.rerun()

    if uploaded_file_new and uploaded_file_new.name != st.session_state.last_uploaded_filename:
        with st.spinner("正在加载和处理数据..."):
            raw_df_temp = load_data(uploaded_file_new)
            if raw_df_temp is not None:
                st.session_state.raw_df, st.session_state.processed_df, st.session_state.last_uploaded_filename = raw_df_temp, preprocess_data(
                    raw_df_temp), uploaded_file_new.name
                st.rerun()
            else:
                st.error(f"无法加载文件 '{uploaded_file_new.name}'. 请检查文件格式。")
                st.session_state.raw_df, st.session_state.processed_df, st.session_state.last_uploaded_filename = None, None, ""


if __name__ == "__main__":
    main()