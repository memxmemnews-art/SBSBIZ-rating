import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

st.title("📊 통합 데이터 자동 분석기")

# ==========================================
# [공통 기능] 텍스트 데이터를 표로 변환하는 안전 로직
# ==========================================
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

def parse_graph_data(pasted_text):
    lines = pasted_text.strip().split('\n')
    data_list = []
    for line in lines:
        parts = line.split('\t')
        if len(parts) >= 2:
            try:
                rating = float(parts[-1].strip())
                time_str = parts[-2].strip()
                data_list.append({'시간': time_str, '시청률': rating})
            except ValueError:
                pass
    return pd.DataFrame(data_list)

# ==========================================
# 1️⃣ [첫 번째 기능] 시청률 분석
# ==========================================
st.header("1️⃣ 시청률 분석")
st.write("엑셀 데이터를 드래그하여 복사(Ctrl+C)한 뒤, 아래에 붙여넣기(Ctrl+V) 해주세요.")

pasted_data_1 = st.text_area("시청률 분석용 데이터 붙여넣기", height=150, key="paste1")

if st.button("시청률 분석 실행", key="btn1"):
    if pasted_data_1.strip() != "":
        df1 = parse_pasted_data(pasted_data_1)
        
        if not df1.empty:
            st.subheader("🎯 주요 채널 시청률")
            targets = ['SBS Biz', 'YTN', '연합뉴스TV', '한국경제TV']
            
            for ch in targets:
                res = df1[df1['채널명'] == ch]
                if not res.empty:
                    rank = res.iloc[0]['순위']
                    rating = res.iloc[0]['시청률']
                    st.write(f"**{ch}**: {rank}위 ({rating})")
                else:
                    st.write(f"**{ch}**: 순위권 밖 (데이터 없음)")

            st.subheader("📊 12위 ~ 18위 채널 순위")
            range_df = df1[(df1['순위'] >= 12) & (df1['순위'] <= 18)]
            
            range_lines = []
            for _, row in range_df.iterrows():
                range_lines.append(f"{row['순위']}위 {row['채널명']} ({row['시청률']})")
            st.markdown("  \n".join(range_lines))
        else:
            st.warning("유효한 숫자를 찾지 못했습니다. 데이터를 다시 복사해 주세요.")
    else:
        st.warning("데이터를 먼저 붙여넣어 주세요.")

st.divider()

# ==========================================
# 2️⃣ [두 번째 기능] 전략 시간대
# ==========================================
st.header("2️⃣ 전략 시간대")
st.write("엑셀 데이터를 드래그하여 복사(Ctrl+C)한 뒤, 아래에 붙여넣기(Ctrl+V) 해주세요.")

pasted_data_2 = st.text_area("전략 시간대 분석용 데이터 붙여넣기", height=150, key="paste2")

if st.button("전략 시간대 분석 실행", key="btn2"):
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
st.write("시간대별 시청률 데이터를 드래그하여 복사(Ctrl+C)한 뒤, 아래에 붙여넣기(Ctrl+V) 해주세요.")

pasted_data_3 = st.text_area("그래프 분석용 데이터 붙여넣기", height=150, key="paste3")

if st.button("그래프 그리기", key="btn3"):
    if pasted_data_3.strip() != "":
        df3 = parse_graph_data(pasted_data_3)
        
        if not df3.empty:
            st.subheader("📈 시간대별 시청률 추이")
            
            # [수정 사항 1] 도화지(figsize) 가로 길이를 10에서 12로 늘려 글씨 겹침 방지
            fig, ax = plt.subplots(figsize=(12, 4))
            
            ax.plot(df3['시간'], df3['시청률'], color='#5B9BD5', linewidth=2.5)
            
            # 최고/최저 시청률 데이터 찾기
            max_idx = df3['시청률'].idxmax()
            max_val = df3['시청률'].max()
            min_val = df3['시청률'].min()
            
            # [수정 사항 2] Y축 상단/하단에 20%의 여유 공간(padding)을 주어 동그라미가 잘리지 않게 함
            padding = (max_val - min_val) * 0.2
            if padding == 0: padding = 0.1
            ax.set_ylim(bottom=min_val - padding, top=max_val + padding)
            
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
            
            # [수정 사항 3] 건너뛰는 로직을 삭제하고, 모든 데이터(1분 간격)를 강제로 X축에 표시
            ax.set_xticks(range(len(df3['시간'])))
            ax.set_xticklabels(df3['시간'], rotation=90, fontsize=9)
            
            plt.yticks(fontsize=9)
            
            fig.tight_layout()
            st.pyplot(fig)
            
        else:
            st.warning("유효한 데이터를 찾지 못했습니다. 데이터를 다시 복사해 주세요.")
    else:
        st.warning("데이터를 먼저 붙여넣어 주세요.")
