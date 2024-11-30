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
    for title, book_info in book_ratings.items():
        # 데이터 추출
        title = book_info.get('title', 'N/A')
        
        # review_count 처리
        raw_review_count = book_info.get('review_count', None)
        if raw_review_count is None or not isinstance(raw_review_count, (int, float, str)):
            review_count = 0
        else:
            try:
                review_count = int(raw_review_count)  # 숫자로 변환
            except ValueError:
                review_count = 0  # 변환 실패 시 기본값

        # rating 처리
        raw_rating = book_info.get('rating', 'N/A')
        rating = raw_rating if isinstance(raw_rating, (int, float)) else 'N/A'

        # best_seller 처리
        best_seller = book_info.get('best_seller', 'N/A')

        # 결과 리스트에 추가
        online_data.append({
            "title": title,
            "review_count": review_count,
            "rating": rating,
            "best_seller": best_seller
        })
        print(online_data)  # 디버깅용 출력

    return online_data