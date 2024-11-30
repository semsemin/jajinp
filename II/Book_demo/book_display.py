import streamlit as st
import pandas as pd



import streamlit as st
import pandas as pd

# Streamlit UI에 DataFrame과 추천 리스트를 출력하는 함수
def book_display_recommendations(df, recommendations):
    """
    Streamlit에서 DataFrame과 추천 리스트를 표로 출력하는 함수.

    Args:
        df (pd.DataFrame): 추천 점수와 관련 정보를 포함한 데이터프레임.
        recommendations (list of dict): 추천 점수와 상품명을 포함한 리스트.
    """
    # DataFrame 출력 (앞의 3개 열 제거)
    st.subheader("📚추천 결과📚")
    df_trimmed = df.drop(columns=df.columns[1:4])
    st.dataframe(df_trimmed)

    # 추천 리스트를 DataFrame으로 변환
    recommendations_df = pd.DataFrame(recommendations)

    st.table(recommendations_df)
    best_book = recommendations_df.iloc[0]  # 추천 점수가 가장 높은 제품 선택

    st.success(f"✅ 분석 결과: **{best_book['title']}**(을)를 구매하는 것을 추천합니다.")


