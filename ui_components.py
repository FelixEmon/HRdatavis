# ui_components.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from data_processing import get_global_filter_options, calculate_channel_metrics
from plotting import create_pie_chart


# --- MODIFIED: Created a specific callback for clearing dates ---
def clear_date_selection():
    """Callback function to reset date selection in session state."""
    st.session_state.ui_start_date = None
    st.session_state.ui_end_date = None
    # No need for st.rerun() here, on_click handles it automatically.


def render_filter_panel():
    """Renders the entire filter panel UI and handles its state."""
    with st.expander("数据筛选条件", expanded=True):
        st.markdown(
            """<style>div[data-testid="stExpander"] div[role="button"] p {font-size: 1.2em;font-weight: bold;}</style>""",
            unsafe_allow_html=True)

        ui_selections = {'bgs': st.session_state.ui_bgs, 'job_types': st.session_state.ui_job_types,
                         'job_titles': st.session_state.ui_job_titles, 'grades': st.session_state.ui_grades}
        options = get_global_filter_options(st.session_state.processed_df, ui_selections)

        date_col1, date_col2, clear_col = st.columns([5, 5, 2])
        with date_col1:
            st.date_input("开始日期", key='ui_start_date')
        with date_col2:
            st.date_input("结束日期", key='ui_end_date')
        with clear_col:
            st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
            # --- MODIFIED: Using on_click callback to reset dates ---
            st.button("清除日期选择", on_click=clear_date_selection)

        st.markdown("---")

        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        for key, opt in [('bgs', options['bgs']), ('job_types', options['job_types']),
                         ('job_titles', options['job_titles']), ('grades', options['grades'])]:
            current_selection = st.session_state.get(f'ui_{key}', [])
            validated_selection = [s for s in current_selection if s in opt]
            st.session_state[f'ui_{key}'] = validated_selection

        with f_col1:
            st.multiselect("BG", options['bgs'], key='ui_bgs')
        with f_col2:
            st.multiselect("职位类", options['job_types'], key='ui_job_types')
        with f_col3:
            st.multiselect("职位名称", options['job_titles'], key='ui_job_titles')
        with f_col4:
            st.multiselect("职级&管理职级", options['grades'], key='ui_grades')

        if st.button("应用筛选", type="primary"):
            for key in ['bgs', 'job_types', 'job_titles', 'grades', 'start_date', 'end_date']:
                st.session_state[f'applied_{key}'] = st.session_state[f'ui_{key}']


def render_channel_analysis(filtered_data):
    """Renders channel analysis with drill-down pie charts."""
    st.markdown("<h3 class='channel-main-title'>相对渠道入职贡献率</h3>", unsafe_allow_html=True)
    channel_metrics = calculate_channel_metrics(filtered_data)

    if not channel_metrics:
        st.warning("根据新规则，无法计算出任何渠道贡献率。")
        return

    channel_order = ['媒体', '伯乐', '猎头', '人才库盘活']
    cols = st.columns(len(channel_order))

    for i, channel_name in enumerate(channel_order):
        metric = channel_metrics.get(channel_name, {"hires": 0, "percentage": 0, "details_text_list": ["无数据"]})
        with cols[i]:
            st.markdown(
                f"<div class='channel-header-box'><h5>{channel_name}</h5><p>{metric['percentage']:.1f}%</p></div>",
                unsafe_allow_html=True)
            style_class = "channel-detail-box-white" if i % 2 == 0 else "channel-detail-box-gray"
            detail_html = "<ul>" + "".join(f"<li>{item}</li>" for item in metric['details_text_list']) + "</ul>"
            st.markdown(f"<div class='channel-detail-box {style_class}'>{detail_html}</div>", unsafe_allow_html=True)

    st.markdown("<h3 class='channel-main-title' style='font-size: 22px; margin-top:15px;'>渠道细分饼图</h3>",
                unsafe_allow_html=True)
    pie_cols = st.columns(len(channel_order))

    with pie_cols[0]:
        metric = channel_metrics.get('媒体')
        if metric and metric['pie_data'].get('values'):
            title = "媒体渠道细分"
            st.markdown(f"<div class='pie-chart-title'>{title}</div>", unsafe_allow_html=True)
            fig = create_pie_chart(metric['pie_data']['labels'], metric['pie_data']['values'], title)
            if fig: st.plotly_chart(fig, use_container_width=True)

    with pie_cols[1]:
        metric = channel_metrics.get('伯乐')
        if metric and metric['pie_data'].get('values'):
            title = "伯乐渠道细分"
            st.markdown(f"<div class='pie-chart-title'>{title}</div>", unsafe_allow_html=True)
            fig = create_pie_chart(metric['pie_data']['labels'], metric['pie_data']['values'], title)
            if fig: st.plotly_chart(fig, use_container_width=True)

    with pie_cols[2]:
        metric = channel_metrics.get('猎头')
        if metric and metric['pie_data'].get('values'):
            title = "猎头渠道细分"
            st.markdown(f"<div class='pie-chart-title'>{title}</div>", unsafe_allow_html=True)
            fig = create_pie_chart(metric['pie_data']['labels'], metric['pie_data']['values'], title)
            if fig: st.plotly_chart(fig, use_container_width=True)

    with pie_cols[3]:
        metric = channel_metrics.get('人才库盘活')
        if metric and metric['pie_data']['main']['values']:
            options = ['总览'] + metric['pie_data']['main']['labels']
            selection = st.radio("人才库盘活下钻", options, key='talent_pool_drilldown_selection', horizontal=True,
                                 label_visibility="collapsed")
            chart_data = metric['pie_data']['details'].get(selection, metric['pie_data']['main'])
            title = f"人才库盘活细分 ({selection})"
            st.markdown(f"<div class='pie-chart-title'>{title}</div>", unsafe_allow_html=True)
            fig = create_pie_chart(chart_data['labels'], chart_data['values'], title)
            if fig: st.plotly_chart(fig, use_container_width=True)


def render_supply_demand_analysis():
    # This function is unchanged.
    st.markdown("---")
    st.markdown("<h3 class='channel-main-title' style='font-size: 22px; margin-top:15px;'>职位供需分析</h3>",
                unsafe_allow_html=True)
    if st.session_state.applied_job_types:
        for job_category in st.session_state.applied_job_types:
            st.subheader(f"职位类别: {job_category}")
            category_data = st.session_state.supply_demand_data.get(job_category)
            if category_data is None:
                st.warning(f"无法找到 '{job_category}' 的供需数据。")
                continue
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="7月供需比 (2025/07)", value=f"{category_data[-1]:.1f}")
            with col2:
                st.metric(label="近两年平均供需比", value=f"{np.mean(category_data):.2f}")
            show_trendline = st.checkbox("显示趋势线", key=f"trend_{job_category}")
            x_dates = pd.to_datetime(pd.date_range(start="2023-08", end="2025-08", freq='M')).strftime('%Y-%m')
            y_values = category_data
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(x=x_dates, y=y_values, mode='lines+markers', name='月度供需比', line=dict(color='blue')))
            x_numeric = np.arange(len(x_dates))
            coeffs = np.polyfit(x_numeric, y_values, 1)
            trend_line = np.polyval(coeffs, x_numeric)
            fig.add_trace(
                go.Scatter(x=x_dates, y=trend_line, mode='lines', name='趋势线', line=dict(color='red', dash='dash'),
                           opacity=1 if show_trendline else 0))
            fig.update_layout(xaxis_title="月份", yaxis_title="供需比",
                              legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("---")
    else:
        st.info("请在上方筛选器中选择一个或多个“职位类”并点击“应用筛选”，以查看职位供需分析。")