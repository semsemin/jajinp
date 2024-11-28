import streamlit as st

def book_display_recommendations(recommendation_df, recommendations):
    """
    추천 결과를 Streamlit에 출력하는 함수.

    Parameters:
        recommendation_df (pd.DataFrame): 추천 점수 계산된 데이터프레임.
        recommendations (list): 유사 상품 추천 리스트.
    """
    # Best Product 출력
    st.subheader("📚 추천 결과 📚 ")
    best_book = recommendation_df.iloc[0]  # 추천 점수가 가장 높은 제품 선택
    st.write(f"**추천 책:** {best_book['title']}")
    st.write(f"**리뷰 수:** {best_book['review_count']}개")
    st.write(f"**평점:** {best_book['rating']} / 5.0")
    st.write(f"**추천 점수:** {best_book['recommend_score']:.2f}")
    st.success(f"✅ 분석 결과: **{best_book['title']}**(을)를 구매하는 것이 추천됩니다.")


