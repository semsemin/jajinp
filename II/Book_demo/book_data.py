import json
from Book_demo.book_rating import get_book_ratings_and_reviews
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)



def fetch_book_data(book_titles):
    """
    책 제목 리스트를 받아 온라인 데이터를 생성합니다.

    Args:
        book_titles (list): 책 제목 리스트. 예: [{"title": "책 제목"}]

    Returns:
        list: JSON 형태의 온라인 데이터. 각 책의 제목, 리뷰 수, 별점을 포함.
    """
    # 책의 별점과 리뷰 수 가져오기
    book_ratings = get_book_ratings_and_reviews(book_titles)

    # 결과 데이터 생성
    online_data = []
    for book in book_ratings:
        # 문자열인 경우 JSON 포맷팅 제거 후 파싱
        if isinstance(book, str):
            try:
                # ```json과 \n 제거
                book = book.replace("```json", "").replace("```", "").strip()
                book = json.loads(book)
            except json.JSONDecodeError:
                book = {"title": "N/A", "review_count": "N/A", "rating": "N/A"}

        # 데이터 추출
        title = book.get('title', 'N/A')
        review_count = book.get('review_count', 'N/A')
        rating = book.get('rating', 'N/A')

        # 결과 리스트에 추가
        online_data.append({
            "title": title,
            "review_count": review_count,
            "rating": rating
        })

    return online_data
