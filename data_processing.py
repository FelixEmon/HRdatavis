# data_processing.py

import pandas as pd
import numpy as np


def generate_supply_demand_data(job_categories):
    # This function is unchanged.
    if job_categories.size == 0:
        return {}
    data_dict = {}
    trends = ['上升', '略微上升', '大致持平', '下降', '略微下降', '剧烈波动']
    x = np.arange(24)
    for category in job_categories:
        chosen_trend = np.random.choice(trends)
        if chosen_trend == '上升':
            base, noise_std = np.linspace(0.5, 2.5, 24), 0.3
        elif chosen_trend == '略微上升':
            base, noise_std = np.linspace(1.0, 2.0, 24), 0.15
        elif chosen_trend == '大致持平':
            start_point = np.random.uniform(1.0, 2.0)
            base, noise_std = np.linspace(start_point, start_point + np.random.uniform(-0.2, 0.2), 24), 0.2
        elif chosen_trend == '下降':
            base, noise_std = np.linspace(2.5, 0.5, 24), 0.3
        elif chosen_trend == '略微下降':
            base, noise_std = np.linspace(2.0, 1.0, 24), 0.15
        else:  # '剧烈波动'
            start_point = np.random.uniform(0.5, 2.5)
            base, noise_std = np.linspace(start_point, start_point + np.random.uniform(-0.5, 0.5), 24), 0.6
        noise = np.random.normal(0, noise_std, 24)
        raw_data = base + noise
        clipped_data = np.clip(raw_data, 0.0, 3.0)
        final_data = np.round(clipped_data, 1)
        data_dict[category] = final_data.tolist()
    return data_dict


def safe_split_付费渠道(series):
    # This function is unchanged.
    res = series.astype(str).str.split('-', n=3, expand=True)
    res.columns = [f'pc_{i}' for i in range(res.shape[1])]
    for i in range(4):
        col_name = f'pc_{i}'
        if col_name not in res.columns:
            res[col_name] = np.nan
    return res[['pc_0', 'pc_1', 'pc_2', 'pc_3']]


def load_data(uploaded_file):
    # This function is unchanged.
    if uploaded_file is not None:
        try:
            xls = pd.ExcelFile(uploaded_file)
            main_df = pd.read_excel(xls, sheet_name=0)
            bole_df = pd.read_excel(xls, sheet_name='bole') if 'bole' in xls.sheet_names else pd.DataFrame()
            return main_df, bole_df
        except Exception as e:
            return None, None
    return None, None


def preprocess_data(main_df, bole_df):
    # This function is unchanged from the last correct version.
    if main_df is None or main_df.empty: return None
    processed_df = main_df.copy()
    if '入职日期' in processed_df.columns:
        processed_df['入职日期'] = pd.to_datetime(processed_df['入职日期'], errors='coerce')
    else:
        processed_df['入职日期'] = pd.NaT
    if 'BG' not in processed_df.columns: processed_df['BG'] = processed_df['组织全路径'].astype(str).apply(
        lambda x: x.split('/')[0] if pd.notnull(x) and '/' in x else x)
    processed_df = processed_df[processed_df['BG'] != 'Overseas Functional System']
    pc_cols = safe_split_付费渠道(processed_df['付费渠道'])
    processed_df = pd.concat([processed_df, pc_cols], axis=1)
    processed_df.rename(
        columns={'pc_0': '付费渠道_a', 'pc_1': '付费渠道_b', 'pc_2': '付费渠道_c', 'pc_3': '付费渠道_d'}, inplace=True)
    for col in ['简历来源', '职位类', '专业职位', '最后渠道1', '最后渠道2', '职级&管理职级']:
        if col in processed_df.columns:
            processed_df[col] = processed_df[col].astype(str).fillna('')
    if not bole_df.empty and '伯乐名称' in bole_df.columns and '伯乐所在BG' in bole_df.columns:
        bole_bg_map = bole_df[['伯乐名称', '伯乐所在BG']].drop_duplicates(subset=['伯乐名称'])
        processed_df = pd.merge(processed_df, bole_bg_map, left_on='付费渠道_d', right_on='伯乐名称', how='left')
        processed_df.drop(columns=['伯乐名称'], inplace=True, errors='ignore')
    else:
        processed_df['伯乐所在BG'] = np.nan
    return processed_df


# --- MODIFIED: Added back the missing function ---
def get_global_filter_options(df, ui_selections):
    options = {}
    if df is None or df.empty:
        return {'bgs': [], 'job_types': [], 'job_titles': [], 'grades': []}
    for target_filter in ['bgs', 'job_types', 'job_titles', 'grades']:
        temp_df = df.copy()
        for other_filter, selection in ui_selections.items():
            if target_filter != other_filter and selection:
                if other_filter == 'bgs':
                    temp_df = temp_df[temp_df['BG'].isin(selection)]
                elif other_filter == 'job_types':
                    temp_df = temp_df[temp_df['职位类'].isin(selection)]
                elif other_filter == 'job_titles':
                    temp_df = temp_df[temp_df['专业职位'].isin(selection)]
                elif other_filter == 'grades':
                    temp_df = temp_df[temp_df['职级&管理职级'].isin(selection)]
        if target_filter == 'bgs':
            raw_options = temp_df['BG'].dropna().unique()
            options[target_filter] = sorted([opt for opt in raw_options if opt and opt != 'nan'])
        elif target_filter == 'job_types':
            raw_options = temp_df['职位类'].dropna().unique()
            options[target_filter] = sorted([opt for opt in raw_options if opt and opt != 'nan'])
        elif target_filter == 'job_titles':
            raw_options = temp_df['专业职位'].dropna().unique()
            options[target_filter] = sorted([opt for opt in raw_options if opt and opt != 'nan'])
        elif target_filter == 'grades':
            grade_options = [opt for opt in temp_df['职级&管理职级'].dropna().unique() if opt and opt != 'nan']
            numeric_grades = sorted([g for g in grade_options if g.isdigit()], key=int)
            alpha_grades = sorted([g for g in grade_options if not g.isdigit()])
            options[target_filter] = numeric_grades + alpha_grades
    return options


# --- MODIFIED: Added back the missing function ---
def filter_dataframe(df_processed, applied_selections):
    if df_processed is None: return pd.DataFrame()
    filtered_df = df_processed.copy()
    if applied_selections['bgs']: filtered_df = filtered_df[filtered_df['BG'].isin(applied_selections['bgs'])]
    if applied_selections['job_types']: filtered_df = filtered_df[
        filtered_df['职位类'].isin(applied_selections['job_types'])]
    if applied_selections['job_titles']: filtered_df = filtered_df[
        filtered_df['专业职位'].isin(applied_selections['job_titles'])]
    if applied_selections['grades']: filtered_df = filtered_df[
        filtered_df['职级&管理职级'].isin(applied_selections['grades'])]
    filtered_df.dropna(subset=['入职日期'], inplace=True)
    if not filtered_df.empty:
        try:
            if applied_selections['start_date']: filtered_df = filtered_df[
                filtered_df['入职日期'] >= pd.to_datetime(applied_selections['start_date'])]
            if applied_selections['end_date']: filtered_df = filtered_df[
                filtered_df['入职日期'] <= pd.to_datetime(applied_selections['end_date'])]
        except (ValueError, TypeError):
            pass
    return filtered_df


def calculate_channel_metrics(df_filtered):
    """MODIFIED: Fixed TypeError by correctly using Series methods instead of dict.pop()."""
    if df_filtered is None or df_filtered.empty: return {}
    results = {}

    # --- Channel 1: Media ---
    website_df = df_filtered[df_filtered['最后渠道1'] == '媒体'].copy()
    media_df = df_filtered[df_filtered['简历来源'].str.contains("媒体", na=False)].copy()
    media_df['normalized_source'] = media_df['简历来源'].str.replace('/', '', regex=False).str.strip()

    total_media_hires = len(pd.concat([website_df, media_df]).drop_duplicates())

    website_breakdown_counts = website_df['最后渠道2'].value_counts()
    media_breakdown_counts = media_df['normalized_source'].value_counts()

    # --- MODIFIED: Correctly get and remove '脉脉' from Pandas Series ---
    maimai_from_website = 0
    if '脉脉' in website_breakdown_counts.index:
        maimai_from_website = website_breakdown_counts['脉脉']
        website_breakdown_counts = website_breakdown_counts.drop('脉脉')

    maimai_from_media = 0
    if '媒体-脉脉' in media_breakdown_counts.index:
        maimai_from_media = media_breakdown_counts['媒体-脉脉']
        media_breakdown_counts = media_breakdown_counts.drop('媒体-脉脉')

    total_maimai = maimai_from_website + maimai_from_media

    final_media_counts = {}
    if total_maimai > 0:
        final_media_counts['媒体-脉脉'] = total_maimai

    for cat, count in website_breakdown_counts.items():
        final_media_counts[f"官网-{cat}"] = count
    for cat, count in media_breakdown_counts.items():
        final_media_counts[cat] = count

    media_details = []
    if total_media_hires > 0:
        media_details = [f"- {cat}: {(count / total_media_hires) * 100:.1f}%" for cat, count in
                         final_media_counts.items()]
    if not media_details:
        media_details = ["无媒体渠道细分"]

    media_pie_data = {'labels': list(final_media_counts.keys()), 'values': list(final_media_counts.values())}

    # --- The rest of the function remains unchanged ---
    # (Bole, Headhunter, Talent Pool, and Final Assembly logic is the same as the last correct version)

    # Bole (Unchanged)
    bole_only_df = df_filtered[df_filtered['付费渠道_b'] == '伯乐'].copy()
    bole_only_df['is_same_bg'] = bole_only_df.apply(
        lambda row: row['伯乐所在BG'] == row['BG'] if pd.notna(row['伯乐所在BG']) and pd.notna(row['BG']) else False,
        axis=1)
    本bg_hires = int(bole_only_df['is_same_bg'].sum())
    其他bg_hires = len(bole_only_df) - 本bg_hires
    qlima_df = df_filtered[df_filtered['付费渠道_b'] == '千里马自主投递'].copy()
    qlima_hires = len(qlima_df)
    total_bole_hires = 本bg_hires + 其他bg_hires + qlima_hires
    bole_pie_data = {'labels': ['本BG', '其他BG', '千里马自主投递'], 'values': [本bg_hires, 其他bg_hires, qlima_hires]}
    if total_bole_hires > 0:
        bole_details = [f"- 本BG: {(本bg_hires / total_bole_hires) * 100:.1f}%",
                        f"- 其他BG: {(其他bg_hires / total_bole_hires) * 100:.1f}%",
                        f"- 千里马自主投递: {(qlima_hires / total_bole_hires) * 100:.1f}%"]
    else:
        bole_details = ["无伯乐渠道入职"]

    # Headhunter (Unchanged)
    lietou_df = df_filtered[df_filtered['付费渠道_b'] == '猎头'].copy()
    total_lietou_hires = len(lietou_df)
    lietou_details, lietou_pie_labels, lietou_pie_values = [], [], []
    if total_lietou_hires > 0:
        source_counts = lietou_df['付费渠道_c'].value_counts()
        top_5 = source_counts.head(5)
        for source, count in top_5.items():
            source_perc = (count / total_lietou_hires) * 100
            lietou_details.append(f"- {source}: {source_perc:.1f}%")
            lietou_pie_labels.append(source)
            lietou_pie_values.append(count)
        other_count = total_lietou_hires - top_5.sum()
        if other_count > 0:
            other_perc = (other_count / total_lietou_hires) * 100
            lietou_details.append(f"- 其他: {other_perc:.1f}%")
            lietou_pie_labels.append("其他")
            lietou_pie_values.append(other_count)
    else:
        lietou_details.append("无猎头渠道入职")
    lietou_pie_data = {'labels': lietou_pie_labels, 'values': lietou_pie_values}

    # Talent Pool (Unchanged)
    tp_keywords = ['内部人才盘活', '公司并购/投资公司或子公司转入', '外包/外聘转正']
    on_keywords = ['个人自有人脉', '公司外朋友推荐/候选人推荐']
    tp_df = df_filtered[df_filtered['简历来源'].isin(tp_keywords)].copy()
    on_df = df_filtered[df_filtered['简历来源'].isin(on_keywords)].copy()
    tp_hires = len(tp_df)
    on_hires = len(on_df)
    total_tp_hires = tp_hires + on_hires
    if total_tp_hires > 0:
        tp_details = [f"- 人才库盘活: {(tp_hires / total_tp_hires) * 100:.1f}%",
                      f"- 自有人脉: {(on_hires / total_tp_hires) * 100:.1f}%"]
    else:
        tp_details = ["无人才库盘活入职"]
    tp_pie_data = {"main": {'labels': ['人才库盘活', '自有人脉'], 'values': [tp_hires, on_hires]}, "details": {
        "人才库盘活": {'labels': tp_df['简历来源'].unique().tolist(),
                       'values': tp_df['简历来源'].value_counts().values.tolist()},
        "自有人脉": {'labels': on_df['简历来源'].unique().tolist(),
                     'values': on_df['简历来源'].value_counts().values.tolist()}}}

    # Final Assembly (Unchanged)
    total_hires = total_media_hires + total_bole_hires + total_lietou_hires + total_tp_hires
    if total_hires == 0: return {}
    results['媒体'] = {"hires": total_media_hires, "percentage": (total_media_hires / total_hires) * 100,
                       "details_text_list": media_details, "pie_data": media_pie_data}
    results['伯乐'] = {"hires": total_bole_hires, "percentage": (total_bole_hires / total_hires) * 100,
                       "details_text_list": bole_details, "pie_data": bole_pie_data}
    results['猎头'] = {"hires": total_lietou_hires, "percentage": (total_lietou_hires / total_hires) * 100,
                       "details_text_list": lietou_details, "pie_data": lietou_pie_data}
    results['人才库盘活'] = {"hires": total_tp_hires, "percentage": (total_tp_hires / total_hires) * 100,
                             "details_text_list": tp_details, "pie_data": tp_pie_data}
    return results