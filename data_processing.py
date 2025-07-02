import pandas as pd
import numpy as np


# --- Helper Functions ---
def safe_split_付费渠道(series):
    """Safely splits the '付费渠道' column into 4 parts, handling NaNs and fewer parts."""
    res = series.astype(str).str.split('-', n=3, expand=True)
    res.columns = [f'pc_{i}' for i in range(res.shape[1])]
    for i in range(4):
        col_name = f'pc_{i}'
        if col_name not in res.columns:
            res[col_name] = np.nan
    return res[['pc_0', 'pc_1', 'pc_2', 'pc_3']]


# --- Main Data Functions ---
def load_data(uploaded_file):
    """Loads data from the uploaded Excel file."""
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            return df
        except Exception as e:
            return None
    return None


def preprocess_data(df):
    """Preprocesses the raw DataFrame."""
    if df is None: return None
    processed_df = df.copy()

    # Convert '入职日期' to datetime, coercing errors to NaT (Not a Time)
    if '入职日期' in processed_df.columns:
        processed_df['入职日期'] = pd.to_datetime(processed_df['入职日期'], errors='coerce')
    else:
        # If column doesn't exist, create it with NaT to avoid errors downstream
        processed_df['入职日期'] = pd.NaT

    processed_df['员工BG'] = processed_df['组织全路径'].astype(str).apply(
        lambda x: x.split('/')[0] if pd.notnull(x) and '/' in x else x)
    pc_cols = safe_split_付费渠道(processed_df['付费渠道'])
    processed_df = pd.concat([processed_df, pc_cols], axis=1)
    processed_df.rename(
        columns={'pc_0': '付费渠道_a', 'pc_1': '付费渠道_b', 'pc_2': '付费渠道_c', 'pc_3': '付费渠道_d'}, inplace=True)
    processed_df['伯乐所在BG'] = processed_df['伯乐所在BG'].astype(str)
    processed_df['职位类'] = processed_df['职位类'].astype(str)
    processed_df['专业职位'] = processed_df['专业职位'].astype(str)
    processed_df['专业职级-数字'] = pd.to_numeric(processed_df['专业职级-数字'], errors='coerce')
    return processed_df


def get_filter_options(df_processed):
    """Gets unique values for all filter dropdowns from the processed DataFrame."""
    if df_processed is None:
        return {'job_types': [], 'job_titles': [], 'years': [], 'months': [], 'days': []}

    # Standard filters
    job_types = sorted(df_processed['职位类'].dropna().unique().tolist())
    job_titles = sorted(df_processed['专业职位'].dropna().unique().tolist())

    # Date filters
    valid_dates_df = df_processed.dropna(subset=['入职日期'])
    if not valid_dates_df.empty:
        years = sorted(valid_dates_df['入职日期'].dt.year.unique(), reverse=True)
        months = sorted(valid_dates_df['入职日期'].dt.month.unique())
        days = sorted(valid_dates_df['入职日期'].dt.day.unique())
    else:
        years, months, days = [], [], []

    return {
        'job_types': job_types,
        'job_titles': job_titles,
        'years': [str(y) for y in years],
        'months': [f"{m:02d}" for m in months],  # Pad with zero for consistency
        'days': [f"{d:02d}" for d in days]
    }


def filter_dataframe(df_processed, selected_bgs, selected_job_types, selected_job_titles, grade_range,
                     start_date_parts, end_date_parts):
    """Filters the processed DataFrame based on all user selections."""
    if df_processed is None: return pd.DataFrame()

    filtered_df = df_processed.copy()

    # --- Standard Filters ---
    if selected_bgs: filtered_df = filtered_df[filtered_df['员工BG'].isin(selected_bgs)]
    if selected_job_types: filtered_df = filtered_df[filtered_df['职位类'].isin(selected_job_types)]
    if selected_job_titles: filtered_df = filtered_df[filtered_df['专业职位'].isin(selected_job_titles)]
    if grade_range:
        min_grade, max_grade = grade_range
        filtered_df = filtered_df[filtered_df['专业职级-数字'].notna() & (filtered_df['专业职级-数字'] >= min_grade) & (
                    filtered_df['专业职级-数字'] <= max_grade)]

    # --- Date Filter ---
    # Drop rows with invalid dates before attempting to filter
    filtered_df.dropna(subset=['入职日期'], inplace=True)
    if filtered_df.empty:
        return filtered_df

    s_year, s_month, s_day = start_date_parts
    e_year, e_month, e_day = end_date_parts

    # Construct start and end date boundaries, handling '任意'
    min_date = filtered_df['入职日期'].min()
    max_date = filtered_df['入职日期'].max()

    start_y = s_year if s_year != '任意' else str(min_date.year)
    start_m = s_month if s_month != '任意' else '01'
    start_d = s_day if s_day != '任意' else '01'

    end_y = e_year if e_year != '任意' else str(max_date.year)
    end_m = e_month if e_month != '任意' else '12'
    end_d = e_day if e_day != '任意' else '31'

    try:
        # Create robust start and end dates
        start_bound = pd.to_datetime(f'{start_y}-{start_m}-{start_d}', errors='coerce')
        end_bound = pd.to_datetime(f'{end_y}-{end_m}-{end_d}', errors='coerce')

        # If user provides an invalid date (e.g. Feb 30), coerce will make it NaT.
        # Default to the absolute min/max of the data in that case.
        if pd.isna(start_bound): start_bound = min_date
        if pd.isna(end_bound): end_bound = max_date

        # Apply the filter only if there are valid dates to compare against
        if not (s_year == '任意' and s_month == '任意' and s_day == '任意' and \
                e_year == '任意' and e_month == '任意' and e_day == '任意'):
            filtered_df = filtered_df[filtered_df['入职日期'].between(start_bound, end_bound, inclusive='both')]

    except Exception:
        # Failsafe in case of unexpected date string format issues
        pass

    return filtered_df


def calculate_channel_metrics(df_filtered, mode='relative'):
    """Calculates all channel contribution metrics and breakdowns. (Unchanged from your version)"""
    if df_filtered is None or df_filtered.empty: return {}
    results = {}
    media_df = df_filtered[df_filtered['付费渠道_b'] == '媒体']
    bole_df = df_filtered[df_filtered['付费渠道_b'] == '伯乐']
    lietou_df = df_filtered[df_filtered['付费渠道_b'] == '猎头']
    talentpool_df = df_filtered[(df_filtered['付费渠道_b'] == '内部团队') & (
                (df_filtered['简历来源'] == '内部人才盘活') | (df_filtered['简历来源'].isnull()) | (
                    df_filtered['简历来源'] == ''))]
    st_df = df_filtered[(df_filtered['付费渠道_b'] == '交付团队') & (df_filtered['付费渠道_c'] == '人才寻访组')]
    liepin_delivery_df = df_filtered[
        (df_filtered['付费渠道_b'] == '交付团队') & (df_filtered['付费渠道_c'] == '高招猎聘')]
    hires_counts = {'媒体': len(media_df), '伯乐': len(bole_df), '猎头': len(lietou_df),
                    '人才库盘活': len(talentpool_df), 'ST': len(st_df), '猎聘': len(liepin_delivery_df)}
    total_hires_for_percentage = len(df_filtered) if mode == 'absolute' else sum(hires_counts.values())
    if total_hires_for_percentage == 0:
        for channel_name_key in ['媒体', '伯乐', '猎头', '人才库盘活', 'ST', '猎聘']:
            results[channel_name_key] = {"hires": 0, "percentage": 0,
                                         "details_text_list": [f"无{channel_name_key}渠道入职"],
                                         "pie_data": {"labels": [], "values": []}}
        results['ST_Liepin_Combined_Pie'] = {"pie_data": {"labels": [], "values": []}}
        return results
    media_hires = hires_counts['媒体']
    media_percentage = (media_hires / total_hires_for_percentage) * 100 if total_hires_for_percentage > 0 else 0
    media_breakdown_text, media_pie_labels, media_pie_values = [], [], []
    if not media_df.empty and media_hires > 0:
        source_counts = media_df['付费渠道_d'].value_counts()
        if not source_counts.empty:
            for source_name, count in source_counts.items():
                display_name = str(source_name) if pd.notna(source_name) and source_name != '' else "未指定D类"
                cat_percent = (count / media_hires) * 100
                media_breakdown_text.append(f"{display_name}: {cat_percent:.0f}% ")
                if count > 0: media_pie_labels.append(display_name); media_pie_values.append(count)
        else:
            media_breakdown_text.append("无付费渠道D类细分数据")
    else:
        media_breakdown_text.append("无媒体渠道入职")
    results['媒体'] = {"hires": media_hires, "percentage": media_percentage, "details_text_list": media_breakdown_text,
                       "pie_data": {"labels": media_pie_labels, "values": media_pie_values}}
    bole_hires = hires_counts['伯乐']
    bole_percentage = (bole_hires / total_hires_for_percentage) * 100 if total_hires_for_percentage > 0 else 0
    bole_breakdown_text, bole_pie_labels, bole_pie_values = [], [], []
    if not bole_df.empty and bole_hires > 0:
        bole_df_for_breakdown = bole_df[
            ~bole_df['伯乐所在BG'].isin(['nan', '#N/A', '子公司组织']) & bole_df['伯乐所在BG'].notna()].copy()
        if not bole_df_for_breakdown.empty:
            bole_df_for_breakdown['is_本BG'] = (bole_df_for_breakdown['伯乐所在BG'] == bole_df_for_breakdown['员工BG'])
            本BG_count, 其他BG_count = bole_df_for_breakdown['is_本BG'].sum(), len(bole_df_for_breakdown) - \
                                                                               bole_df_for_breakdown['is_本BG'].sum()
            total_valid = len(bole_df_for_breakdown)
            本BG_perc = (本BG_count / total_valid) * 100 if total_valid > 0 else 0
            其他BG_perc = (其他BG_count / total_valid) * 100 if total_valid > 0 else 0
            bole_breakdown_text.append(f"本BG: {本BG_perc:.0f}% ");
            bole_breakdown_text.append(f"其他BG: {其他BG_perc:.0f}% ")
            if 本BG_count > 0: bole_pie_labels.append("本BG"); bole_pie_values.append(本BG_count)
            if 其他BG_count > 0: bole_pie_labels.append("其他BG"); bole_pie_values.append(其他BG_count)
        else:
            bole_breakdown_text.append("无有效伯乐BG数据进行细分")
    else:
        bole_breakdown_text.append("无伯乐渠道入职")
    results['伯乐'] = {"hires": bole_hires, "percentage": bole_percentage, "details_text_list": bole_breakdown_text,
                       "pie_data": {"labels": bole_pie_labels, "values": bole_pie_values}}
    lietou_hires = hires_counts['猎头']
    lietou_percentage = (lietou_hires / total_hires_for_percentage) * 100 if total_hires_for_percentage > 0 else 0
    lietou_breakdown_text, lietou_pie_labels, lietou_pie_values = [], [], []
    if not lietou_df.empty and lietou_hires > 0:
        source_counts = lietou_df['付费渠道_c'].value_counts()
        if not source_counts.empty:
            top_n, current_sum = 3, 0
            for i, (source, count) in enumerate(source_counts.head(top_n).items()):
                display_source = str(source) if pd.notna(source) and source != '' else "未指定C类"
                source_perc = (count / lietou_hires) * 100
                lietou_breakdown_text.append(f"TOP {i + 1} ({display_source}): {source_perc:.0f}% ")
                lietou_pie_labels.append(f"{display_source} (TOP{i + 1})");
                lietou_pie_values.append(count)
                current_sum += count
            other_count = lietou_hires - current_sum
            if other_count > 0:
                other_perc = (other_count / lietou_hires) * 100
                lietou_breakdown_text.append(f"其他猎头: {other_perc:.0f}% ")
                lietou_pie_labels.append("其他猎头");
                lietou_pie_values.append(other_count)
            if not lietou_pie_labels and not lietou_breakdown_text: lietou_breakdown_text.append("无付费渠道细分数据")
        else:
            lietou_breakdown_text.append("无付费渠道细分数据")
    else:
        lietou_breakdown_text.append("无猎头渠道入职")
    results['猎头'] = {"hires": lietou_hires, "percentage": lietou_percentage,
                       "details_text_list": lietou_breakdown_text,
                       "pie_data": {"labels": lietou_pie_labels, "values": lietou_pie_values}}
    talentpool_hires = hires_counts['人才库盘活']
    talentpool_percentage = (
                                        talentpool_hires / total_hires_for_percentage) * 100 if total_hires_for_percentage > 0 else 0
    talentpool_breakdown_text, talentpool_pie_labels, talentpool_pie_values = [], [], []
    if not talentpool_df.empty and talentpool_hires > 0:
        source_counts = talentpool_df['付费渠道_c'].value_counts()
        if not source_counts.empty:
            for source_name, count in source_counts.items():
                display_name = str(source_name) if pd.notna(source_name) and source_name != '' else "未指定C类"
                cat_percent = (count / talentpool_hires) * 100
                talentpool_breakdown_text.append(f"{display_name}: {cat_percent:.0f}%")
                if count > 0: talentpool_pie_labels.append(display_name); talentpool_pie_values.append(count)
        else:
            talentpool_breakdown_text.append("无付费渠道C类细分数据")
    else:
        talentpool_breakdown_text.append("无人才库盘活入职")
    results['人才库盘活'] = {"hires": talentpool_hires, "percentage": talentpool_percentage,
                             "details_text_list": talentpool_breakdown_text,
                             "pie_data": {"labels": talentpool_pie_labels, "values": talentpool_pie_values}}
    st_hires = hires_counts['ST']
    st_percentage = (st_hires / total_hires_for_percentage) * 100 if total_hires_for_percentage > 0 else 0
    results['ST'] = {"hires": st_hires, "percentage": st_percentage, "details_text_list": ["交付团队-ST"],
                     "pie_data": {}}
    liepin_delivery_hires = hires_counts['猎聘']
    liepin_delivery_percentage = (
                                             liepin_delivery_hires / total_hires_for_percentage) * 100 if total_hires_for_percentage > 0 else 0
    results['猎聘'] = {"hires": liepin_delivery_hires, "percentage": liepin_delivery_percentage,
                       "details_text_list": ["交付团队-猎聘"], "pie_data": {}}
    st_lp_pie_labels, st_lp_pie_values = [], []
    if st_hires > 0: st_lp_pie_labels.append("ST (人才寻访组)"); st_lp_pie_values.append(st_hires)
    if liepin_delivery_hires > 0: st_lp_pie_labels.append("猎聘 (高招猎聘)"); st_lp_pie_values.append(
        liepin_delivery_hires)
    results['ST_Liepin_Combined_Pie'] = {"pie_data": {"labels": st_lp_pie_labels, "values": st_lp_pie_values}}
    return results