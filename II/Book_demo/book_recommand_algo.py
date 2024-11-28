import pandas as pd

def process_book_data(book_data):
    """
    책 데이터를 처리하여 추천 점수와 정규화된 별점을 계산하는 함수.

    Args:
        book_data (list of dict): 책 제목, 리뷰 수, 별점을 포함한 데이터.
            예: [{"title": "책 제목", "review_count": 1000, "rating": 4.5}, ...]

    Returns:
        pd.DataFrame: 추천 점수와 정규화된 별점을 포함한 데이터프레임.
        list of dict: 각 책의 제목, 정규화된 별점, 추천 점수를 포함한 리스트.
    """
    processed_data = []
    recommendations = []  # 추천 정보를 저장할 리스트

    for item in book_data:
        try:
            # rating을 float으로 변환
            rating = float(item["rating"])
            review_count = int(item["review_count"])

            # 최대 별점 추정
            max_rating = 10 if rating > 5 else 5

            # 별점 정규화 (5점 기준)
            normalized_rating = (rating / max_rating) * 5

            # 추천 점수 계산
            recommend_score = review_count * 0.3 + normalized_rating * 0.7

            # 데이터 처리 결과 추가
            processed_data.append({
                "title": item["title"],
                "review_count": review_count,
                "rating": rating,
                "normalized_rating": normalized_rating,
                "recommend_score": recommend_score
            })

            # 추천 정보를 리스트에 추가
            recommendations.append({
                "title": item["title"],
                "normalized_rating": normalized_rating,
                "recommend_score": recommend_score
            })

        except KeyError as e:
            print(f"Missing key in data: {e}")
        except ValueError as e:
            print(f"Invalid value in data: {e}")

    # 데이터를 데이터프레임으로 변환
    df = pd.DataFrame(processed_data)

    # 추천 점수 기준으로 정렬
    df = df.sort_values(by='recommend_score', ascending=False)

    return df, recommendations
