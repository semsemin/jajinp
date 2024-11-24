import pandas as pd

# 예시 데이터
local_data = [
    {"title": "해리포터와 마법사의 돌"},
    {"title": "반지의 제왕"},
    {"title": "어린 왕자"}
]

online_data = [
    {"title": "해리포터와 마법사의 돌", "review_count": 12500, "rating": 4.8},
    {"title": "반지의 제왕", "review_count": 24000, "rating": 9.5},
    {"title": "어린 왕자", "review_count": 15000, "rating": 4.7}
]

# 최대 별점 추정 함수
def estimate_max_rating(rating):
    if rating > 5:  # 별점이 5를 초과하면 10점 만점으로 간주
        return 10
    else:  # 그렇지 않으면 5점 만점으로 간주
        return 5

# 현장과 온라인 정보 결합
merged_data = []
for local_item in local_data:
    for online_item in online_data:
        if local_item["title"] == online_item["title"]:
            max_rating = estimate_max_rating(online_item["rating"])  # 최대 별점 추정
            normalized_rating = (online_item["rating"] / max_rating) * 5  # 별점 정규화
            merged_data.append({
                "title": local_item["title"],
                "review_count": online_item["review_count"],
                "rating": online_item["rating"],
                "normalized_rating": normalized_rating,  # 정규화된 별점 추가
                "recommend_score": 0  # Placeholder for recommendation score
            })

# 데이터를 데이터프레임으로 변환
df = pd.DataFrame(merged_data)

# 점수 계산: 정규화된 별점과 리뷰 수 기반
df['recommend_score'] = (
    df['review_count'] * 0.3 + 
    df['normalized_rating'] *0.7 
)

# 추천 점수에 따라 정렬
df = df.sort_values(by='recommend_score', ascending=False)

# 출력
print("\n추천 점수 기준으로 정렬된 상품:")
print(df[['title', 'recommend_score', 'review_count', 'rating', 'normalized_rating']])

