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
# 1️⃣ [첫 번째 기능] 시청률 분석 (엑셀 양식 완벽 재현)
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
            
    # 25년 실적 데이터 고정
    table_data['25년 실적\n(12/31 기준)'] = [
        "23위 (0.122)", 
        "2위 (0.795)",  
        "4위 (0.691)",  
        "50위 (0.056)"  
    ]
    
    st.markdown("##### 1. 채널 순위 및 시청률 (종편 및 케이블 채널 210개)")
    
    # [핵심 로직] 엑셀 디자인을 웹에 100% 이식하는 HTML/CSS 커스텀 생성기
    html_str = """
    <style>
    .report-table {
        border-collapse: collapse;
        text-align: center;
        font-family: 'Malgun Gothic', '맑은 고딕', sans-serif;
        font-size: 13.5px;
        color: #000;
        margin-top: 5px;
    }
    .report-table th {
        background-color: #dce6f2; /* 파스텔 블루 */
        border: 1px solid #000;
        padding: 6px 15px;
        font-weight: normal;
        white-space: nowrap; /* 글씨 줄바꿈 방지 */
    }
    .report-table td {
        border-top: 1px dotted #000;
        border-bottom: 1px dotted #000;
        border-left: 1px dotted #000;
        border-right: 1px dotted #000;
        padding: 6px 15px;
        white-space: nowrap;
    }
    /* 블록 외곽선은 굵은 실선으로 처리 */
    .report-table th:first-child, .report-table td:first-child {
        border-left: 1px solid #000;
    }
    .report-table tr:last-child td {
        border-bottom: 1px solid #000;
    }
    /* '26년 누적'과 '25년 실적' 사이의 여백 기둥 */
    .spacer {
        border: none !important;
        background-color: #fff !important;
        width: 15px !important;
        padding: 0 !important;
    }
    /* 25년 실적 박스 외곽선 */
    .right-box th, .right-box td {
        border-left: 1px solid #000 !important;
        border-right: 1px solid #000 !important;
    }
    /* 누적 데이터 우측 마감선 */
    .left-box-end {
        border-right: 1px solid #000 !important;
    }
    </style>
    <table class="report-table">
    <thead><tr>
    """
    
    cols = list(table_data.keys())
    target_col = '25년 실적\n(12/31 기준)'
    
    for c in cols:
        if c == target_col:
            html_str += f"<th class='spacer'></th><th class='right-box'>{c.replace(chr(10), '<br>')}</th>"
        else:
            cls = "left-box-end" if c == cols[cols.index(target_col)-1] else ""
            html_str += f"<th class='{cls}'>{c}</th>"
    html_str += "</tr></thead><tbody>"
    
    for i in range(len(table_data['채널'])):
        html_str += "<tr>"
        for c in cols:
            val = table_data[c][i]
            if c == target_col:
                html_str += f"<td class='spacer'></td><td class='right-box'>{val}</td>"
            else:
                cls = "left-box-end" if c == cols[cols.index(target_col)-1] else ""
                html_str += f"<td class='{cls}'>{val}</td>"
        html_str += "</tr>"
        
    html_str += "</tbody></table>"
    
    # 여백 최적화를 위해 컬럼 비율 조정
    out_col1, out_col2 = st.columns([6.7, 3.3]) 
    
    with out_col1:
        st.markdown(html_str, unsafe_allow_html=True)
        
    with out_col2:
        if not df_acc.empty:
            range_df = df_acc[(df_acc['순위'] >= 12) & (df_acc['순위'] <= 18)]
            if not range_df.empty:
                # 우측 텍스트도 표와 폰트 크기가 일치하도록 HTML로 커스텀
                right_html = f"""
                <div style="font-family: 'Malgun Gothic', '맑은 고딕', sans-serif; font-size: 13.5px; color: #000; padding-top: 10px;">
                    <span style="font-weight: bold;">[근접 순위 채널 (26년 누적)]</span><br><br>
                """
                for _, row in range_df.iterrows():
                    right_html += f"{row['순위']}위 {row['채널명']} ({row['시청률']:.3f})<br>"
                right_html += "</div>"
                st.markdown(right_html, unsafe_allow_html=True)
            else:
                st.write("해당 순위 데이터가 없습니다.")
        else:
            st.write("⚠️ 26년 누적 데이터를 입력해 주세요.")

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
# 3️⃣ [세 번째 기능] 시청률 추이 그래프 (엑셀 업로드 방식)
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
                    
                    fig, ax = plt.subplots(figsize=(10, 4))
                    
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
            st.error(f"파일을 분석할 수 없습니다. (상세 오류: {e})")
    else:
        st.warning("엑셀 파일을 먼저 업로드해 주세요.")
