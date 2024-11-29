import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Label_demo.product_data import fetch_online_product_data
from Label_demo.naver_review import fetch_and_display_review_summary


# Streamlit 탭에서 데이터 표시
def display_sorted_products():
    # 샘플 데이터
    product_data = st.session_state["product_data"]

    # 데이터 정제: None 값과 타입 처리
    for product in product_data:
        # 리뷰 수와 가격 기본값 설정
        product["review_count"] = product.get("review_count", 0) or 0
        product["online_price"] = product.get("online_price", float("inf")) or float("inf")    

        # 평점 타입 변환 및 기본값 설정
        rating = product.get("rating", 0.0)
        if isinstance(rating, str):  # 문자열인 경우 float으로 변환 시도
            try:
                rating = float(rating)
            except ValueError:
                rating = 0.0
        product["rating"] = rating  # 변환된 값을 다시 할당

        # 리뷰 요약 기본값 설정
        product["review_summary"] = product.get("review_summary", "요약 없음")
        # 리뷰 한줄평 추가
    for product in product_data:
        product["review_summary"] = fetch_and_display_review_summary(product["product_name"])

    # 데이터 정렬
    sorted_by_reviews = sorted(product_data, key=lambda x: x["review_count"], reverse=True)
    sorted_by_price = sorted(product_data, key=lambda x: x["online_price"])
    sorted_by_rating = sorted(product_data, key=lambda x: x["rating"], reverse=True)

    # Streamlit 탭 생성
    tab1, tab2, tab3 = st.tabs(["리뷰순", "최저가순", "평점순"])

    # 탭 별로 테이블 표시
    for tab, sorted_products, columns, highlight_field in zip(
        [tab1, tab2, tab3],
        [sorted_by_reviews, sorted_by_price, sorted_by_rating],
        [
            ["순위", "제품명", "리뷰수", "한줄평"],
            ["순위", "제품명", "최저가", "한줄평"],
            ["순위", "제품명", "평점", "한줄평"],
        ],
        ["리뷰수", "최저가", "평점"],
    ):
        with tab:
            # 데이터프레임 생성
            table_data = [
                {
                    "순위": idx + 1,
                    "제품명": product["product_name"],
                    "리뷰수": product["review_count"] if "리뷰수" in columns else None,
                    "최저가": product["online_price"] if "최저가" in columns else None,
                    "평점": product["rating"] if "평점" in columns else None,
                    "한줄평": product["review_summary"],
                }
                for idx, product in enumerate(sorted_products)
            ]

            df = pd.DataFrame(table_data)

            # 선택된 기준만 표시
            df = df[[col for col in columns if col in df.columns]]

            # 열 강조를 위한 스타일링 함수
            def highlight_column(data, column):
                styles = pd.DataFrame("", index=data.index, columns=data.columns)
                styles[column] = "background-color: #4A90E2; color: white;"  # 파란색 배경, 흰색 글씨
                return styles

            # 스타일 적용
            styled_df = df.style.apply(lambda x: highlight_column(df, highlight_field), axis=None)

            # Streamlit에 HTML로 렌더링
            st.markdown(styled_df.to_html(index=False), unsafe_allow_html=True)
