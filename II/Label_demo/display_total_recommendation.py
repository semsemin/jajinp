import streamlit as st
import pandas as pd


def display_recommendations(df, recommendations, similar):
    st.subheader("🛍️추천 결과🛍️")

    columns_to_drop = list(df.columns[1:7]) + [df.columns[-1]]
    df_trimmed = df.drop(columns=columns_to_drop)
    st.dataframe(df_trimmed)

    # 추천 리스트 출력
    recommendations_df = pd.DataFrame(recommendations)
    st.table(recommendations_df)
    best_product = recommendations_df.iloc[0]  # 추천 점수가 가장 높은 제품 선택
    st.success(f"✅ 분석 결과: **{best_product['product_name']}**(을)를 구매하는 것을 추천합니다.")

    # 유사 상품 추천 출력
    st.subheader("🌟 유사 상품 추천")
    for rec in similar:
        st.write(f"**상품명:** {rec['product_name']}")
        st.write("유사 상품:")
        for similar_item, score in rec['recommendations']:
            st.write(f"- {similar_item} (유사도: {score:.2f})")

