import streamlit as st
import sys
import os
# 프로젝트 루트 디렉토리를 PYTHONPATH에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Book_demo.book_rating import get_book_ratings_and_reviews
from Book_demo.book_data import fetch_book_data
from Book_demo.book_summary import get_book_summaries_and_recommendations

def display_sorted_books():
    """
    Streamlit 탭에서 리뷰 수, 평점을 기준으로 정렬된 책 데이터를 표시하는 함수
    """
        # 현재 입력된 book_data
    book_data = st.session_state["title"]

    # 데이터 정제: NoneType 또는 "N/A" 값을 기본값으로 대체
    for book in book_data:
        book["review_count"] = int(book["review_count"]) if book["review_count"] and book["review_count"] != "N/A" else 0
        book["rating"] = float(book["rating"]) if book["rating"] and book["rating"] != "N/A" else 0.0

    # 이전에 저장된 데이터와 현재 데이터를 비교하여 상태 초기화
    if "previous_data" not in st.session_state or st.session_state["previous_data"] != book_data:
        # 새로운 데이터가 들어왔을 경우 상태 초기화
        st.session_state["sorted_by_reviews"] = sorted(
            book_data, key=lambda x: x["review_count"], reverse=True
        )
        st.session_state["sorted_by_rating"] = sorted(
            book_data, key=lambda x: x["rating"], reverse=True
        )
        # 현재 데이터를 "previous_data"로 저장
        st.session_state["previous_data"] = book_data

    # Streamlit 탭 생성
    tab1, tab2 = st.tabs(["리뷰순", "평점순"])

    # 각 탭에 데이터를 표시
    for tab, sorted_books, title, highlight_field, highlight_label in zip(
        [tab1, tab2], 
        [st.session_state["sorted_by_reviews"], st.session_state["sorted_by_rating"]],
        ["리뷰 순위", "평점 순위"], 
        ["review_count", "rating"], 
        ["리뷰 수", "평점"]
    ):
        with tab:
            st.subheader(title)
            for idx, book in enumerate(sorted_books, start=1):
                st.markdown(f"### {idx}. {book['title']}")
                highlighted_value = ""
                if highlight_field == "review_count":
                    highlighted_value = f"{book['review_count']}회"
                elif highlight_field == "rating":
                    highlighted_value = f"{book['rating']}점"
                st.markdown(f"<h4 style='font-weight:bold; font-size:1.2em;'>- {highlight_label}: {highlighted_value}</h4>", unsafe_allow_html=True)

                other_details = {
                    "review_count": f"- 리뷰 수: {book['review_count']}회",
                    "rating": f"- 평점: {book['rating']}점"
                }
                for key, value in other_details.items():
                    if key != highlight_field:
                        st.markdown(value)

                with st.spinner("줄거리와 추천 독자 정보를 가져오는 중..."):
                    summary_data = get_book_summaries_and_recommendations([{"title": book["title"]}])
                    if summary_data:
                        summary = summary_data[0].get("book_summary", "요약 정보 없음")
                        recommended_for = summary_data[0].get("recommended_for", "추천 정보 없음")
                        st.markdown(f"**줄거리 요약:** {summary}")
                        st.markdown(f"**추천 독자:** {recommended_for}")
                    else:
                        st.warning("줄거리 정보를 가져올 수 없습니다.")
                st.markdown("---")

# Streamlit 앱 실행
if __name__ == "__main__":
    st.title("도서 정렬 및 추천")
    
    # 책 데이터 입력
    if "book_data" not in st.session_state:
        st.session_state["book_data"] = fetch_book_data([
            {"title": "해리포터와 마법사의 돌"},
            {"title": "반지의 제왕"},
            {"title": "어린 왕자"}
        ])
    
    display_sorted_books()
