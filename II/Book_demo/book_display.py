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
    st.subheader("📚추천 결과📚")
    st.write('<small>추천 점수는 각 도서의 리뷰 수, 평점, 베스트셀러 순위를 다른 도서들과 비교한 상대적 순위를 기반으로 계산되었습니다.</small>', unsafe_allow_html=True)

    # 열 이름 변경
    df.rename(
        columns={
            "title": "책 제목",
            "rating_score": "평점",
            "review_count_score": "리뷰수",
            "best_seller_rank_score": "베스트셀러 순위",
            "recommend_score": "총점"  
        },
        inplace=True
    )

    df_trimmed = df.drop(columns=df.columns[1:4])  # 불필요한 열 제거
    df_trimmed.index = df_trimmed.index + 1  # 인덱스를 1부터 시작
    df_trimmed.index.name = "순위"  # 인덱스 열 이름 설정
    st.dataframe(df_trimmed)

    # 추천 리스트를 DataFrame으로 변환
    recommendations_df = pd.DataFrame(recommendations)

    # 열 이름 변경
    recommendations_df.rename(
        columns={
            "title": "책 제목",
            "recommend_score": "추천 점수"  # 가상의 열 이름 예시
        },
        inplace=True
    )

    recommendations_df.index = recommendations_df.index + 1  # 인덱스를 1부터 시작
    recommendations_df.index.name = "순위"  # 인덱스 열 이름 설정
    st.table(recommendations_df)

    # 추천 점수가 가장 높은 책 선택
    best_book = recommendations_df.iloc[0]

    # 결과 출력
    st.success(f"✅ 분석 결과: **{best_book['책 제목']}**(을)를 구매하는 것을 추천합니다.")