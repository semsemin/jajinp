import streamlit as st
import pandas as pd

def display_recommendations(df, recommendations, similar):
    
    st.subheader("🛍️추천 결과🛍️")
    st.write('<small>추천 점수는 각 상품의 리뷰 수, 평점, 가격 차이를 다른 상품들과 비교한 상대적 순위를 기반으로 계산되었습니다.</small>', unsafe_allow_html=True)
    

    # 열 이름 변경
    df.rename(
        columns={
            "rating_score": "평점",
            "review_count_score": "리뷰수",
            "price_difference_score":"오프라인과 온라인 가격 차이",
            "recommend_score": "총점",
            "product_name": "상품명"
        },
        inplace=True
    )

    # 불필요한 열 제거
    columns_to_drop = list(df.columns[1:7]) + [df.columns[-1]]
    df_trimmed = df.drop(columns=columns_to_drop)
    df_trimmed.index = df_trimmed.index + 1  # 인덱스를 1부터 시작
    df_trimmed.index.name = "순위"  # 인덱스 열 이름 설정
    st.dataframe(df_trimmed)

    # 추천 리스트 열 이름 변경
    recommendations_df = pd.DataFrame(recommendations)
    recommendations_df.rename(
        columns={
            "product_name": "상품명",
            "recommend_score": "추천 점수"  # 가상의 열 이름 예시
        },
        inplace=True
    )
    recommendations_df.index = recommendations_df.index + 1  # 인덱스를 1부터 시작
    recommendations_df.index.name = "순위"  # 인덱스 이름 설정
    st.table(recommendations_df)

    # 추천 점수가 가장 높은 제품 선택
    best_product = recommendations_df.iloc[0]
    st.success(f"✅ 분석 결과: **{best_product['상품명']}**(을)를 구매하는 것을 추천합니다.")

    # 유사 상품 추천 출력
    st.subheader("🌟 유사 상품 추천")
    st.write('<small>유사도는 상품명과 추천 점수의 유사성을 기준으로 산출되었습니다.</small>', unsafe_allow_html=True)
    for rec in similar:
        st.write(f"**상품명:** {rec['product_name']}")
        st.write("유사 상품:")
        for similar_item, score in rec['recommendations']:
            st.write(f"- {similar_item} (유사도: {score:.2f})")