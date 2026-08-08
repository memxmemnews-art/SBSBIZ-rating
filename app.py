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

# [세 번째 기능을 위한 전용 데이터 파서]
def parse_graph_data(pasted_text):
    lines = pasted_text.strip().split('\n')
    data_list = []
    for line in lines:
        parts = line.split('\t')
        # 빈칸이나 프로그램명 유무와 상관없이 최소 2개(시간, 시청률)의 데이터만 있으면 추출
        if len(parts) >= 2:
            try:
                # 무조건 끝에서 첫 번째는 시청률, 끝에서 두 번째는 시간대로 인식
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
            
            # 그래프 판(도화지) 생성
            fig, ax = plt.subplots(figsize=(10, 4))
            
            # 엑셀과 동일한 스타일의 파란색 선 그래프
            ax.plot(df3['시간'], df3['시청률'], color='#5B9BD5', linewidth=2.5)
            
            # 최고 시청률 데이터 찾기
            max_idx = df3['시청률'].idxmax()
            max_val = df3['시청률'].max()
            
            # 1. 최고점에 엑셀 모양의 빨간색 점선 원 그리기
            ax.scatter(max_idx, max_val, s=600, facecolors='none', edgecolors='red', linewidths=2, linestyles='--')
            
            # 2. 최고점의 시청률 텍스트 표시 (동그라미 왼쪽으로 살짝 띄워서 배치)
            ax.annotate(f'{max_val:.3f}', 
                        xy=(max_idx, max_val), 
                        xytext=(-25, 0), 
                        textcoords='offset points', 
                        ha='right', va='center', 
                        fontsize=14, fontweight='bold')
            
            # 그래프 배경 및 테두리 깔끔하게 다듬기 (엑셀 스타일)
            ax.grid(axis='y', color='#E0E0E0', linestyle='-')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            
            # X축 시간대 글씨가 겹치지 않도록 적절히 건너뛰며 90도로 세워서 표시
            ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=20))
            plt.xticks(rotation=90, fontsize=9)
            plt.yticks(fontsize=9)
            
            fig.tight_layout()
            
            # 완성된 그래프를 웹 화면에 출력
            st.pyplot(fig)
            
        else:
            st.warning("유효한 데이터를 찾지 못했습니다. 데이터를 다시 복사해 주세요.")
    else:
        st.warning("데이터를 먼저 붙여넣어 주세요.")
