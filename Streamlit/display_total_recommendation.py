import streamlit as st

def display_recommendations(recommendation_df, recommendations):
    """
    추천 결과를 Streamlit에 출력하는 함수.

    Parameters:
        recommendation_df (pd.DataFrame): 추천 점수 계산된 데이터프레임.
        recommendations (list): 유사 상품 추천 리스트.
    """
    # Best Product 출력
    st.subheader("🎉 추천 결과 🎉")
    best_product = recommendation_df.iloc[0]  # 추천 점수가 가장 높은 제품 선택
    st.write(f"**추천 상품:** {best_product['product_name']}")
    st.write(f"**오프라인 가격:** {best_product['local_price']}원")
    st.write(f"**온라인 가격:** {best_product['online_price']}원")
    st.write(f"**리뷰 수:** {best_product['review_count']}개")
    st.write(f"**평점:** {best_product['rating']} / 5.0")
    st.write(f"**추천 점수:** {best_product['recommend_score']:.2f}")
    st.success(f"✅ 분석 결과: **{best_product['product_name']}**(을)를 구매하는 것이 추천됩니다.")

    # 유사 상품 추천 출력
    st.subheader("📊 유사 상품 추천")
    for rec in recommendations:
        st.write(f"**상품명:** {rec['product_name']}")
        st.write("유사 상품:")
        for similar_item, score in rec['recommendations']:
            st.write(f"- {similar_item} (유사도: {score:.2f})")

