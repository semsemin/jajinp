import streamlit as st
import pandas as pd
import sys
import os

# 프로젝트 루트 디렉토리를 PYTHONPATH에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Book_demo.book_rating import get_book_ratings_and_reviews
from Book_demo.book_data import fetch_book_data
from Book_demo.book_summary import get_book_summaries_and_recommendations

def highlight_column(df, column_name):
    """
    특정 열(column_name)을 강조하는 스타일링 함수
    """
    pastel_green = "background-color: #d5f5e3;"  # 강조할 배경색
    styles = pd.DataFrame("", index=df.index, columns=df.columns)
    styles[column_name] = pastel_green  # 특정 열에만 스타일 적용
    return styles


def display_tab(tab, book_df, sort_by, ascending, highlight_col):
    """
    탭별 데이터 정렬 및 출력 함수
    """
    with tab:
        sorted_df = book_df.sort_values(by=sort_by, ascending=ascending).reset_index(drop=True)
        sorted_df.index = sorted_df.index + 1  # 순위 설정
        sorted_df.index.name = "순위"  # 인덱스 열 이름 설정
        st.dataframe(
            sorted_df.style.apply(highlight_column, column_name=highlight_col, axis=None),
            use_container_width=True,
        )


def display_sorted_books():
    """
    Streamlit에서 리뷰 수, 평점, 베스트셀러 순위를 기준으로 정렬된 표와,
    줄거리 및 추천 정보를 표시하는 표를 구현
    """
    # 현재 입력된 book_data
    book_data = st.session_state.get("title", [])
    if not book_data:
        st.error("책 데이터가 없습니다. 먼저 데이터를 로드하세요.")
        return

    # 데이터 정제
    for book in book_data:
        # 리뷰 수 정제
        try:
            book["review_count"] = int(book.get("review_count", 0))  # 기본값 0
        except ValueError:
            book["review_count"] = 0

        # 평점 정제
        try:
            book["rating"] = float(book.get("rating", 0.0))  # 기본값 0.0
        except ValueError:
            book["rating"] = 0.0

        # 베스트셀러 순위 정제
        best_seller = book.get("best_seller", None)
        if best_seller is None or best_seller == "N/A":
            book["best_seller"] = 99999  # 매우 낮은 우선순위를 의미하는 큰 값
        else:
            try:
                book["best_seller"] = int(best_seller)
            except ValueError:
                book["best_seller"] = 99999  # 정수 변환 실패 시 기본값

    # DataFrame 생성
    book_df = pd.DataFrame(book_data)

    # 열 이름 변경
    book_df.rename(
        columns={
            "review_count": "리뷰 수",
            "rating": "평점",
            "best_seller": "베스트셀러 순위",
            "title": "책 제목"  # 'title' 컬럼이 있을 경우
        },
        inplace=True
    )

    # 평점 데이터를 숫자로 변환 및 포맷팅
    book_df["평점"] = pd.to_numeric(book_df["평점"], errors="coerce").fillna(0.0)
    book_df["평점"] = book_df["평점"].map("{:.1f}".format)

    # 첫 번째 표: 리뷰 수, 평점, 베스트셀러 순위를 기준으로 정렬 및 강조
    st.markdown("<h5>리뷰 수 / 평점 / 베스트셀러 순위</h5>", unsafe_allow_html=True)

    # Streamlit 탭 생성
    tab1, tab2, tab3 = st.tabs(["리뷰 수", "평점", "베스트셀러 순위"])

    # 탭별 데이터 정렬 및 출력
    display_tab(tab1, book_df, sort_by="리뷰 수", ascending=False, highlight_col="리뷰 수")
    display_tab(tab2, book_df, sort_by="평점", ascending=False, highlight_col="평점")
    display_tab(tab3, book_df, sort_by="베스트셀러 순위", ascending=True, highlight_col="베스트셀러 순위")


def get_detailed_info(book_data):
    """
    책의 줄거리와 추천 독자 정보를 가져오는 함수
    """
    st.subheader("🌟 줄거리와 추천 독자")
    
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
    return pd.DataFrame(detailed_info_data)