import streamlit as st
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Label_demo.naver_review import fetch_and_display_review_summary


def highlight_column(df, column_name):
    """
    특정 열(column_name)을 강조하는 스타일링 함수
    """
    highlight_color = "background-color: #e6f3fc;"  # 강조할 배경색
    styles = pd.DataFrame("", index=df.index, columns=df.columns)  # 기본 스타일은 빈 문자열
    if column_name in df.columns:
        styles[column_name] = highlight_color  # 지정된 열에만 스타일 적용
    return styles


def display_tab(tab, product_df, sort_by, ascending, highlight_col):
    """
    탭별 데이터 정렬 및 출력 함수
    """
    with tab:
        # 정렬
        sorted_df = product_df.sort_values(by=sort_by, ascending=ascending).reset_index(drop=True)
        
        # 순위 설정
        sorted_df.index = sorted_df.index + 1
        sorted_df.index.name = "순위"

        # Streamlit에 출력
        st.dataframe(
            sorted_df.style.apply(highlight_column, column_name=highlight_col, axis=None),
            use_container_width=True,
        )


def display_sorted_products():
    """
    Streamlit에서 리뷰 수, 최저가, 평점을 기준으로 정렬된 데이터를 표시하며,
    선택된 열을 강조하는 함수
    """
    # 현재 입력된 product_data
    product_data = st.session_state.get("product_data", [])
    if not product_data:
        st.error("상품 데이터가 없습니다. 데이터를 먼저 로드하세요.")
        return

    # 데이터 정제
    for product in product_data:
        product["review_count"] = int(product.get("review_count", 0))  # 기본값 0
        product["online_price"] = (
            int(product["online_price"]) if product.get("online_price") not in [None, "N/A"] else float("inf")
        )
        try:
            product["rating"] = float(product.get("rating", 0.0))  # 기본값 0.0
        except (ValueError, TypeError):
            product["rating"] = 0.0
        product["review_summary"] = fetch_and_display_review_summary(product["product_name"])

    # DataFrame 생성 및 열 이름 변경
    product_df = pd.DataFrame(product_data)
    product_df.rename(
        columns={
            "product_name": "상품명",
            "review_count": "리뷰수",
            "rating": "평점",
            "online_price": "온라인 최저가",
            "review_summary": "한줄평"
        },
        inplace=True
    )

    # Streamlit 탭 생성
    st.markdown("<h5>리뷰 수 / 평점 / 최저가 </h5>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["리뷰수", "평점", "최저가"])

    # 탭별 데이터 정렬 및 출력
    display_tab(tab1, product_df, sort_by="리뷰수", ascending=False, highlight_col="리뷰수")
    display_tab(tab2, product_df, sort_by="평점", ascending=False, highlight_col="평점")
    display_tab(tab3, product_df, sort_by="온라인 최저가", ascending=True, highlight_col="온라인 최저가")
