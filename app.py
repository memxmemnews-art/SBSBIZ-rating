import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import math

st.title("📊 통합 데이터 자동 분석기")

# ==========================================
# [공통 기능] 데이터 파서 및 입력칸 초기화 로직
# ==========================================
def clear_texts(keys):
    for key in keys:
        if key in st.session_state:
            if "upload" in key:
                del st.session_state[key]
            else:
                st.session_state[key] = ""

def parse_pasted_data(pasted_text):
    lines = pasted_text.strip().split('\n')
    data_list = []
    for line in lines:
        parts = line.split('\t')
        if len(parts) >= 3:
            try:
                rank = int(parts[0].strip())
                channel = parts[1].strip()
                rating = float(parts[2].strip())
                data_list.append({'순위': rank, '채널명': channel, '시청률': rating})
            except ValueError:
                pass
    return pd.DataFrame(data_list)

# ==========================================
# 1️⃣ [첫 번째 기능] 시청률 분석
# ==========================================
st.header("1️⃣ 채널 순위 및 시청률")
st.write("각 일자별 데이터와 누적 데이터를 넣으면 통합 표를 생성합니다. (날짜를 입력하지 않은 칸은 표에서 제외됩니다.)")

col1, col2, col3 = st.columns(3)
with col1:
    date_1 = st.text_input("일자 1 (예: 8/7 (금))", key="date1")
    paste_1 = st.text_area("일자 1 데이터 붙여넣기", height=120, key="paste_day1")
with col2:
    date_2 = st.text_input("일자 2 (예: 8/8 (토))", key="date2")
    paste_2 = st.text_area("일자 2 데이터 붙여넣기", height=120, key="paste_day2")
with col3:
    date_3 = st.text_input("일자 3 (예: 8/9 (일))", key="date3")
    paste_3 = st.text_area("일자 3 데이터 붙여넣기", height=120, key="paste_day3")

paste_acc = st.text_area("26년 누적 데이터 붙여넣기", height=120, key="paste_acc")

btn_col1, btn_col2, _ = st.columns([2, 2, 6])
with btn_col1:
    run1 = st.button("시청률 표 생성", key="btn1", use_container_width=True)
with btn_col2:
    keys_to_clear = ["date1", "paste_day1", "date2", "paste_day2", "date3", "paste_day3", "paste_acc"]
    st.button("데이터 지우기 🗑️", key="clear1", on_click=clear_texts, args=(keys_to_clear,), use_container_width=True)

if run1:
    targets = ['SBS Biz', 'YTN', '연합뉴스TV', '한국경제TV']
    table_data = {'채널': targets}
    
    def get_channel_stat(df, ch):
        res = df[df['채널명'] == ch]
        if not res.empty:
            return f"{res.iloc[0]['순위']}위 ({res.iloc[0]['시청률']:.3f})"
        return "-"
        
    dfs = {}
    if date_1.strip() and paste_1.strip():
        df_tmp = parse_pasted_data(paste_1)
        if not df_tmp.empty: dfs[date_1.strip()] = df_tmp
        
    if date_2.strip() and paste_2.strip():
        df_tmp = parse_pasted_data(paste_2)
        if not df_tmp.empty: dfs[date_2.strip()] = df_tmp
        
    if date_3.strip() and paste_3.strip():
        df_tmp = parse_pasted_data(paste_3)
        if not df_tmp.empty: dfs[date_3.strip()] = df_tmp
        
    for date_label, df_tmp in dfs.items():
        table_data[date_label] = [get_channel_stat(df_tmp, ch) for ch in targets]
        
    df_acc = pd.DataFrame()
    if paste_acc.strip():
        df_acc = parse_pasted_data(paste_acc)
        if not df_acc.empty:
            table_data['26년 누적'] = [get_channel_stat(df_acc, ch) for ch in targets]
            
    table_data['26년 목표'] = ["21위 (0.133)", "", "", ""]
    table_data['25년 실적\n(12/31 기준)'] = [
        "23위 (0.122)", 
        "2위 (0.795)",  
        "4위 (0.691)",  
        "50위 (0.056)"  
    ]
    
    st.markdown("##### 1. 채널 순위 및 시청률 (종편 및 케이블 채널 210개)")
    st.info("💡 **팁:** 표 전체를 마우스로 드래그하여 복사(Ctrl+C)한 뒤, 엑셀이나 메일에 붙여넣기(Ctrl+V) 하시면 테두리와 색상 양식이 그대로 복사됩니다!")

    raw_css = """
    <style>
    .report-table {
        border-collapse: collapse;
        text-align: center;
        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
        font-size: 13.5px;
        color: #000;
        margin-top: 5px;
        background-color: #fff;
        flex-shrink: 0;
    }
    .report-table th {
        background-color: #dce6f2;
        border: 1px solid #000;
        padding: 6px 15px;
        font-weight: normal;
        white-space: nowrap;
    }
    .report-table td {
        border: 1px dotted #000;
        padding: 6px 15px;
        white-space: nowrap;
    }
    .report-table th:first-child,
    .report-table td:first-child {
        border-left: 1px solid #000;
    }
    .report-table tr:last-child td {
        border-bottom: 1px solid #000;
    }
    .empty-goal {
        background-color: #d9d9d9 !important;
        border-left: 1px solid #000 !important;
        border-right: 1px solid #000 !important;
        border-top: 1px dotted #000 !important;
        border-bottom: 1px dotted #000 !important;
    }
    .goal-bottom {
        background-color: #d9d9d9 !important;
        border-left: 1px solid #000 !important;
        border-right: 1px solid #000 !important;
        border-bottom: 1px solid #000 !important;
    }
    .goal-header {
        border: 1px solid red !important;
        background-color: #dce6f2 !important;
        font-weight: bold !important;
    }
    .goal-value {
        border: 1px solid red !important;
        background-color: #fff !important;
        font-weight: bold !important;
        color: #000 !important;
    }
    .spacer {
        border: none !important;
        background-color: transparent !important;
        width: 10px !important;
        min-width: 10px !important;
        padding: 0 !important;
    }
    .right-box {
        border-left: 1px solid #000 !important;
        border-right: 1px solid #000 !important;
    }
    .report-layout {
        display: inline-flex;
        flex-direction: row;
        align-items: flex-start;
        gap: 20px;
        width: max-content;
        min-width: 100%;
    }
    .report-table-wrap {
        flex: 0 0 auto;
    }
    .right-ranking {
        flex: 0 0 auto;
        min-width: 250px;
        width: 250px;
        overflow: visible;
        white-space: nowrap;
    }
    </style>
    """
    html_str = "\n".join(line.strip() for line in raw_css.split("\n"))
    html_str += "<table class='report-table'><thead><tr>"
    
    cols = list(table_data.keys())
    target_col = '25년 실적\n(12/31 기준)'
    goal_col = '26년 목표'
    
    for c in cols:
        if c == target_col:
            html_str += f"<th class='spacer'></th><th class='right-box'>{c.replace(chr(10), '<br>')}</th>"
        elif c == goal_col:
            html_str += f"<th class='goal-header'>{c}</th>"
        else:
            html_str += f"<th>{c}</th>"
    html_str += "</tr></thead><tbody>"
    
    for i, target_ch in enumerate(targets):
        html_str += "<tr>"
        for c in cols:
            val = table_data[c][i]
            
            if c == goal_col:
                if target_ch == 'SBS Biz':
                    html_str += f"<td class='goal-value'>{val}</td>"
                elif i == len(targets) - 1:
                    html_str += "<td class='goal-bottom'></td>"
                else:
                    html_str += "<td class='empty-goal'></td>"
            elif c == target_col:
                html_str += f"<td class='spacer'></td><td class='right-box'>{val}</td>"
            else:
                html_str += f"<td>{val}</td>"
        html_str += "</tr>"
        
    html_str += "</tbody></table>"
    
    right_raw = ""
    if not df_acc.empty:
        range_df = df_acc[(df_acc['순위'] >= 12) & (df_acc['순위'] <= 18)]
        if not range_df.empty:
            right_raw += """
            <div class="right-ranking"
                 style="font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
                        font-size: 13.5px;
                        color: #000;
                        padding-top: 5px;
                        white-space: nowrap;">
            """
            right_raw += "<span style=\"font-weight: bold;\">[근접 순위 채널 (26년 누적)]</span><br><br>"
            for _, row in range_df.iterrows():
                right_raw += f"{row['순위']}위 {row['채널명']} ({row['시청률']:.3f})<br>"
            right_raw += "</div>"
        else:
            right_raw = """
            <div class="right-ranking"
                 style="font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
                        font-size: 13.5px;
                        color: #000;
                        padding-top: 5px;
                        white-space: nowrap;">
                <span style="font-weight: bold;">[근접 순위 채널 (26년 누적)]</span><br><br>
                해당 순위 데이터가 없습니다.
            </div>
            """
    else:
        right_raw = """
        <div class="right-ranking"
             style="font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
                    font-size: 13.5px;
                    color: #000;
                    padding-top: 5px;
                    white-space: nowrap;">
            <span style="font-weight: bold;">[근접 순위 채널 (26년 누적)]</span><br><br>
            ⚠️ 26년 누적 데이터를 입력해 주세요.
        </div>
        """

    layout_raw = f"""
    <div style="
        width: 100%;
        overflow-x: auto;
        overflow-y: hidden;
        padding: 10px 0px;
        background-color: #fff;
    ">
        <div class="report-layout">
            <div class="report-table-wrap">
                {html_str}
            </div>
            {right_raw}
        </div>
    </div>
    """
    final_layout = "\n".join(line.strip() for line in layout_raw.split("\n"))
    
    st.markdown(final_layout, unsafe_allow_html=True)

st.divider()

# ==========================================
# 2️⃣ [두 번째 기능] 전략 시간대
# ==========================================
st.header("2️⃣ 전략 시간대")
st.write("엑셀 데이터를 드래그하여 복사(Ctrl+C)한 뒤, 아래에 붙여넣기(Ctrl+V) 해주세요.")

pasted_data_2 = st.text_area("전략 시간대 분석용 데이터 붙여넣기", height=150, key="paste2")

col1, col2, col3 = st.columns([2, 2, 6])
with col1:
    run2 = st.button("전략 시간대 분석 실행", key="btn2", use_container_width=True)
with col2:
    st.button("데이터 지우기 🗑️", key="clear2", on_click=clear_texts, args=(["paste2"],), use_container_width=True)

if run2:
    if pasted_data_2.strip() != "":
        df2 = parse_pasted_data(pasted_data_2)
        
        if not df2.empty:
            sbs_biz_row = df2[df2['채널명'] == 'SBS Biz']
            if not sbs_biz_row.empty:
                sbs_biz_rating = sbs_biz_row.iloc[0]['시청률']
                
                st.subheader(f"🧮 타 채널 대비 SBS Biz 비율 (SBS Biz: {sbs_biz_rating})")
                
                compare_targets = ['YTN', '연합뉴스TV', 'MBN', '채널A', 'TV CHOSUN']
                
                ratio_lines = []
                for ch in compare_targets:
                    target_row = df2[df2['채널명'] == ch]
                    if not target_row.empty:
                        target_rating = target_row.iloc[0]['시청률']
                        
                        if target_rating > 0:
                            ratio = (sbs_biz_rating / target_rating) * 100
                            ratio_lines.append(f"**{ch}**: {ratio:.0f}% (시청률: {target_rating})")
                        else:
                            ratio_lines.append(f"**{ch}**: 계산 불가 (시청률 0)")
                    else:
                        ratio_lines.append(f"**{ch}**: 순위권 밖 (데이터 없음)")
                
                st.markdown("  \n".join(ratio_lines))
                
            else:
                st.error("데이터에서 'SBS Biz'를 찾을 수 없어 나누기를 할 수 없습니다.")

            st.subheader("🏆 시청률 1위 ~ 10위")
            top10 = df2.sort_values(by='시청률', ascending=False).head(10)
            
            rank_lines = []
            for _, row in top10.iterrows():
                rank_lines.append(f"{row['순위']}위 {row['채널명']} ({row['시청률']})")
            
            st.markdown("  \n".join(rank_lines))

        else:
            st.warning("유효한 숫자를 찾지 못했습니다. 데이터를 다시 복사해 주세요.")
    else:
        st.warning("데이터를 먼저 붙여넣어 주세요.")

st.divider()

# ==========================================
# 3️⃣ [세 번째 기능] 시청률 추이 그래프
# ==========================================
st.header("3️⃣ 시청률 추이 그래프")
st.write("시청률 엑셀 파일을 업로드해 주세요. (시간대 그룹별로 그래프가 각각 생성됩니다)")

upload_3 = st.file_uploader("그래프 분석용 엑셀 업로드", type=["xlsx", "xls"], key="upload3")

col1, col2, col3 = st.columns([2, 2, 6])
with col1:
    run3 = st.button("그래프 그리기", key="btn3", use_container_width=True)
with col2:
    st.button("데이터 지우기 🗑️", key="clear3", on_click=clear_texts, args=(["upload3"],), use_container_width=True)

if run3:
    if upload_3 is not None:
        try:
            df3 = pd.read_excel(upload_3, header=3)
            df3.columns = ['시간대 그룹', '시간', '시청률']
            
            df3['시간대 그룹'] = df3['시간대 그룹'].ffill()
            
            df3 = df3.dropna(subset=['시간', '시청률'])
            df3['시청률'] = pd.to_numeric(df3['시청률'], errors='coerce')
            df3 = df3.dropna(subset=['시청률'])
            
            if not df3.empty:
                groups = df3['시간대 그룹'].unique()
                
                for grp in groups:
                    st.subheader(f"📈 {grp} 시청률 추이")
                    
                    df_grp = df3[df3['시간대 그룹'] == grp].copy().reset_index(drop=True)
                    
                    fig, ax = plt.subplots(figsize=(8, 3.15))
                    
                    ax.plot(df_grp['시간'], df_grp['시청률'], color='#5B9BD5', linewidth=2.5)
                    
                    max_idx = df_grp['시청률'].idxmax()
                    max_val = df_grp['시청률'].max()
                    min_val = df_grp['시청률'].min()
                    
                    padding = (max_val - min_val) * 0.2
                    if padding == 0: padding = 0.1
                    
                    ax.set_ylim(bottom=max(0, min_val - padding), top=max_val + padding)
                    
                    ax.scatter(max_idx, max_val, s=600, facecolors='none', edgecolors='red', linewidths=2, linestyles='--')
                    
                    ax.annotate(f'{max_val:.3f}', 
                                xy=(max_idx, max_val), 
                                xytext=(-25, 0), 
                                textcoords='offset points', 
                                ha='right', va='center', 
                                fontsize=14, fontweight='bold')
                    
                    ax.grid(axis='y', color='#E0E0E0', linestyle='-')
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['left'].set_visible(False)
                    
                    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.05))
                    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.3f'))
                    
                    num_labels = 40
                    step = max(1, math.ceil(len(df_grp['시간']) / num_labels))
                    
                    ax.set_xticks(range(0, len(df_grp['시간']), step))
                    ax.set_xticklabels(df_grp['시간'].iloc[::step], rotation=90, fontsize=9)
                    
                    plt.yticks(fontsize=9)
                    
                    fig.tight_layout()
                    st.pyplot(fig)
                    
            else:
                st.warning("유효한 데이터를 찾지 못했습니다. 파일 양식을 확인해 주세요.")
                
        except Exception as e:
            st.error(f"파일을 분석할 수 분석할 수 없습니다. (상세 오류: {e})")
    else:
        st.warning("엑셀 파일을 먼저 업로드해 주세요.")

st.divider()

# ==========================================
# 4️⃣ [네 번째 기능] 경제채널 경쟁사 비교 (요약표 기능 포함)
# ==========================================
st.header("4️⃣ 경제채널 비교")
st.write("엑셀 데이터를 드래그하여 복사(Ctrl+C)한 뒤, 평일, 휴일, 전체, 누적 항목에 각각 붙여넣어 주세요. (파일 업로드가 아닌 텍스트 붙여넣기 방식입니다.)")

col4_1, col4_2, col4_3, col4_4 = st.columns(4)
with col4_1:
    paste_wd = st.text_area("평일(월-금) 데이터 붙여넣기", height=120, key="paste_wd")
with col4_2:
    paste_we = st.text_area("휴일(토,일) 데이터 붙여넣기", height=120, key="paste_we")
with col4_3:
    paste_all = st.text_area("전체(월-일) 데이터 붙여넣기", height=120, key="paste_all")
with col4_4:
    paste_acc4 = st.text_area("26년 누적 데이터 붙여넣기", height=120, key="paste_acc4")

st.markdown("##### 📝 요약 표(SBS Biz) 추가 데이터 수동 입력")
st.write("기간 및 직접 입력해야 할 수치를 입력해 주세요.")

sub1, sub2, sub3 = st.columns(3)
with sub1:
    st.markdown("**[전주]**")
    date_prev = st.text_input("기간 입력", value="9/7~9/13", key="date_prev")
    st.info("※ 순위/시청률은 위 데이터에서 자동 반영됩니다.")
with sub2:
    st.markdown("**[26년 누적]**")
    date_acc = st.text_input("기간 입력 ", value="1/1~9/13", key="date_acc")
    man_acc_wd = st.text_input("평일 (예: 15위 (0.209))", key="man_acc_wd")
    man_acc_we = st.text_input("휴일 (예: 30위 (0.119))", key="man_acc_we")
with sub3:
    st.markdown("**[전년 동기 누적]**")
    date_yoy = st.text_input("기간 입력  ", value="25/1/1~9/13", key="date_yoy")
    man_yoy_all = st.text_input("전체 (예: 23위 (0.123))", key="man_yoy_all")
    man_yoy_wd = st.text_input("평일 (예: 23위 (0.129))", key="man_yoy_wd")
    man_yoy_we = st.text_input("휴일 (예: 23위 (0.110))", key="man_yoy_we")

btn_col4_1, btn_col4_2, _ = st.columns([2, 2, 6])
with btn_col4_1:
    run4 = st.button("경쟁사 비교 표 생성", key="btn4", use_container_width=True)
with btn_col4_2:
    keys_to_clear4 = [
        "paste_wd", "paste_we", "paste_all", "paste_acc4",
        "date_prev", "date_acc", "date_yoy",
        "man_acc_wd", "man_acc_we",
        "man_yoy_all", "man_yoy_wd", "man_yoy_we"
    ]
    st.button("데이터 지우기 🗑️", key="clear4", on_click=clear_texts, args=(keys_to_clear4,), use_container_width=True)

if run4:
    target_channels_4 = [
        'SBS Biz', '한국경제TV', 'MTN 머니투데이', '매일경제TV', 
        '토마토TV', '서울경제TV', '연합뉴스경제TV', '이데일리TV'
    ]
    
    channel_numbers = {
        'SBS Biz': ['26, 25, 27번', '25번'],
        '한국경제TV': ['151, 180, 162번', '151번'],
        'MTN 머니투데이': ['152, 181, 163번', '152번'],
        '매일경제TV': ['153, 182, 164번', '153번'],
        '토마토TV': ['150, 185, 165번', '154번'],
        '서울경제TV': ['156, 184, 167번', '156번'],
        '연합뉴스경제TV': ['157, 187, 171번', '157번'],
        '이데일리TV': ['155, 183, 166번', '155번']
    }
    
    df_wd = parse_pasted_data(paste_wd) if paste_wd.strip() else pd.DataFrame()
    df_we = parse_pasted_data(paste_we) if paste_we.strip() else pd.DataFrame()
    df_all = parse_pasted_data(paste_all) if paste_all.strip() else pd.DataFrame()
    df_acc4 = parse_pasted_data(paste_acc4) if paste_acc4.strip() else pd.DataFrame()
    
    # [핵심] 원본 데이터에 "MTN" 글자가 포함되어 있으면 알아서 "MTN 머니투데이"로 연결해주는 스마트 검색 추가
    def get_target_row(df, ch):
        if df.empty:
            return pd.DataFrame()
        if ch == 'MTN 머니투데이':
            return df[df['채널명'].astype(str).str.contains('MTN|머니투데이', case=False, na=False)]
        else:
            return df[df['채널명'].astype(str) == ch]

    def get_rank_rating_formatted(df, ch):
        res = get_target_row(df, ch)
        if not res.empty:
            return f"{res.iloc[0]['순위']}위", f"{res.iloc[0]['시청률']:.3f}"
        return "-", "-"
        
    def get_combined_stat(df, ch):
        res = get_target_row(df, ch)
        if not res.empty:
            return f"{res.iloc[0]['순위']}위 ({res.iloc[0]['시청률']:.3f})"
        return "-"
    
    st.info("💡 **팁:** 표 전체를 마우스로 드래그하여 복사(Ctrl+C)한 뒤, 엑셀이나 메일에 붙여넣기(Ctrl+V) 하시면 테두리와 색상 양식이 그대로 복사됩니다!")

    val_prev_all = get_combined_stat(df_all, 'SBS Biz')
    val_prev_wd = get_combined_stat(df_wd, 'SBS Biz')
    val_prev_we = get_combined_stat(df_we, 'SBS Biz')
    val_acc_all = get_combined_stat(df_acc4, 'SBS Biz')

    html_4 = ""

    css_4 = """
    <style>
    .summary-table {
        border-collapse: collapse;
        text-align: center;
        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
        font-size: 13.5px;
        color: #000;
        margin-bottom: 30px;
        background-color: #fff;
        border: 1.5px solid #000;
    }
    .summary-table th, .summary-table td {
        border: 1px solid #000;
        padding: 8px 25px;
        white-space: nowrap;
    }
    .summary-table th {
        background-color: #f2f2f2;
        font-weight: normal;
    }
    .summary-table .col-header {
        background-color: #f2f2f2;
    }

    .comp-table {
        border-collapse: collapse;
        text-align: center;
        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
        font-size: 13.5px;
        color: #000;
        background-color: #fff;
        width: max-content;
        border: 1px solid #000;
    }
    .comp-table th {
        background-color: #dce6f2;
        border: 1px dotted #000;
        padding: 6px 12px;
        font-weight: normal;
        white-space: nowrap;
    }
    .comp-table td {
        border: 1px dotted #000;
        padding: 6px 12px;
        white-space: nowrap;
    }
    .comp-table thead tr:first-child th { border-top: 1px solid #000 !important; }
    .comp-table tbody tr:last-child td { border-bottom: 1px solid #000 !important; }
    .comp-table th:first-child, .comp-table td:first-child { border-left: 1px solid #000 !important; }
    .comp-table th:last-child, .comp-table td:last-child { border-right: 1px solid #000 !important; }
    .comp-table thead tr:last-child th { border-bottom: 1px solid #000 !important; }
    
    .comp-table .col-group-end { border-right: 1.5px solid #000 !important; }
    .comp-table .sbs-row td { background-color: #fff2cc !important; }
    </style>
    """
    
    html_4 += css_4
    
    html_4 += f"""
    <div style="width: 100%; overflow-x: auto; padding: 10px 0px; background-color: #fff;">
        <table class="summary-table">
            <thead>
                <tr>
                    <th>구분</th>
                    <th>전주<br>({date_prev})</th>
                    <th>26년 누적<br>({date_acc})</th>
                    <th>전년 동기 누적<br>({date_yoy})</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="col-header">전체</td>
                    <td>{val_prev_all}</td>
                    <td>{val_acc_all}</td>
                    <td>{man_yoy_all if man_yoy_all else '-'}</td>
                </tr>
                <tr>
                    <td class="col-header">평일</td>
                    <td>{val_prev_wd}</td>
                    <td>{man_acc_wd if man_acc_wd else '-'}</td>
                    <td>{man_yoy_wd if man_yoy_wd else '-'}</td>
                </tr>
                <tr>
                    <td class="col-header">휴일</td>
                    <td>{val_prev_we}</td>
                    <td>{man_acc_we if man_acc_we else '-'}</td>
                    <td>{man_yoy_we if man_yoy_we else '-'}</td>
                </tr>
            </tbody>
        </table>
    """
    
    html_4 += """
        <table class="comp-table">
        <thead>
            <tr>
                <th rowspan="2">구분</th>
                <th colspan="2">평일 (월-금)</th>
                <th colspan="2">휴일 (토,일)</th>
                <th colspan="2" class="col-group-end">전체 (월-일)</th>
                <th colspan="2" class="col-group-end">26년 누적</th>
                <th colspan="2">채널번호</th>
            </tr>
            <tr>
                <th>순위</th><th>시청률</th>
                <th>순위</th><th>시청률</th>
                <th>순위</th><th class="col-group-end">시청률</th>
                <th>순위</th><th class="col-group-end">시청률</th>
                <th>IPTV (SK, KT, LG)</th><th>스카이라이프</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for ch in target_channels_4:
        rk_wd, rt_wd = get_rank_rating_formatted(df_wd, ch)
        rk_we, rt_we = get_rank_rating_formatted(df_we, ch)
        rk_all, rt_all = get_rank_rating_formatted(df_all, ch)
        rk_acc, rt_acc = get_rank_rating_formatted(df_acc4, ch)
        ip_tv, sky = channel_numbers[ch]
        
        row_cls = "sbs-row" if ch == 'SBS Biz' else ""
        ch_weight = "bold" if ch == 'SBS Biz' else "normal"
        
        html_4 += f"""
            <tr class="{row_cls}">
                <td style="font-weight: {ch_weight};">{ch}</td>
                <td>{rk_wd}</td><td>{rt_wd}</td>
                <td>{rk_we}</td><td>{rt_we}</td>
                <td>{rk_all}</td><td class="col-group-end">{rt_all}</td>
                <td>{rk_acc}</td><td class="col-group-end">{rt_acc}</td>
                <td>{ip_tv}</td><td>{sky}</td>
            </tr>
        """
        
    html_4 += "</tbody></table></div>"
    
    final_html_4 = "\n".join(line.strip() for line in html_4.split("\n"))
    
    st.markdown(final_html_4, unsafe_allow_html=True)
