import streamlit as st
import pandas as pd
import sys
import os

# 프로젝트 루트 디렉토리를 PYTHONPATH에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Book_demo.book_rating import get_book_ratings_and_reviews
from Book_demo.book_data import fetch_book_data
from Book_demo.book_summary import get_book_summaries_and_recommendations


def display_sorted_books():
    """
    Streamlit에서 리뷰 수, 평점, 베스트셀러 순위를 기준으로 정렬된 표와,
    줄거리 및 추천 정보를 표시하는 표를 구현
    """

    # 현재 입력된 book_data
    book_data = st.session_state["title"]

    # 데이터 정제: NoneType 또는 "N/A" 값을 기본값으로 대체
    for book in book_data:
        book["review_count"] = int(book["review_count"]) if book["review_count"] and book["review_count"] != "N/A" else 0
        book["rating"] = float(book["rating"]) if book["rating"] and book["rating"] != "N/A" else 0.0
        book["bestseller_rank"] = 0  # 베스트셀러 순위는 현재 없으므로 0으로 설정

    # DataFrame 생성
    book_df = pd.DataFrame(book_data)

    # 첫 번째 표: 리뷰 수, 평점, 베스트셀러 순위를 기준으로 정렬 및 강조
    st.subheader("기본 정보")

    tab1, tab2, tab3 = st.tabs(["리뷰 수", "평점", "베스트셀러 순위"])

    def highlight_column(df, column_name):
        """
        특정 열(column_name)을 강조하는 스타일링 함수
        """
        pastel_green = "background-color: #d5f5e3;"  # 강조할 배경색
        styles = pd.DataFrame("", index=df.index, columns=df.columns)
        styles[column_name] = pastel_green  # 특정 열에만 스타일 적용
        return styles

    # 각 탭의 내용
    with tab1:
        st.subheader("리뷰 수")
        sorted_df = book_df.sort_values(by="review_count", ascending=False).reset_index(drop=True)
        st.dataframe(
            sorted_df.style.apply(highlight_column, column_name="review_count", axis=None),
            use_container_width=True,
        )

    with tab2:
        st.subheader("평점")
        sorted_df = book_df.sort_values(by="rating", ascending=False).reset_index(drop=True)
        st.dataframe(
            sorted_df.style.apply(highlight_column, column_name="rating", axis=None),
            use_container_width=True,
        )

    with tab3:
        st.subheader("베스트셀러 순위")
        sorted_df = book_df.sort_values(by="bestseller_rank", ascending=True).reset_index(drop=True)
        st.dataframe(
            sorted_df.style.apply(highlight_column, column_name="bestseller_rank", axis=None),
            use_container_width=True,
        )

    # 두 번째 표: 줄거리와 추천 정보 표시
    st.subheader("줄거리와 추천")

    detailed_info_data = []
    for book in book_data:
        with st.spinner(f"'{book['title']}'의 줄거리와 추천 독자 정보를 가져오는 중..."):
            summary_data = get_book_summaries_and_recommendations([{"title": book["title"]}])
            if summary_data:
                summary = summary_data[0].get("book_summary", "요약 정보 없음")
                recommended_for = summary_data[0].get("recommended_for", "추천 정보 없음")
            else:
                summary = "요약 정보를 가져올 수 없습니다."
                recommended_for = "추천 정보를 가져올 수 없습니다."

            detailed_info_data.append({
                "책 제목": book["title"],
                "줄거리 요약": summary,
                "추천 독자": recommended_for
            })

    detailed_info_df = pd.DataFrame(detailed_info_data)
    st.table(detailed_info_df)
